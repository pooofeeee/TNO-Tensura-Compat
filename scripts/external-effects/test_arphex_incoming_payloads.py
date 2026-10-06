"""Compare incoming actor/recipient/formula claims with exact pinned instructions."""
import hashlib
import unittest
import zipfile
from copy import deepcopy

from catalog_common import OUT, read_json
from classfile import ClassFile
from promote_combat_batch import validate_batch, effect_receiver_binding


class IncomingPayloadTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch = read_json(OUT/'arphex-r2m2f-incoming-status-weapon-payloads.json')
        cls.witness = next(w for w in read_json(OUT/'native-evidence/arphex-global-hooks.json')['witnesses']
                           if w['entry'].endswith('/DwellerLifestealProcedure.class'))
        cls.method = next(m for m in cls.witness['methods'] if m['name'] == 'execute'
                          and 'Lnet/neoforged/bus/api/Event;' in m['descriptor'])
        cls.body = cls.method['instructions']
        cls.by_offset = {i['offset']: i for i in cls.body}

    def row(self, name):
        return next(r for r in self.batch['effects'] if r['id'] == 'arphex:'+name)

    def test_exact_consumers_and_no_existing_parameter_recount(self):
        review = read_json(OUT/'mod-reviews/arphex.json')
        ids = {r['id'] for r in self.batch['effects']}
        base = deepcopy(review)
        base['effects'] = [r for r in base['effects'] if r['id'] not in ids]
        base['paths'] = [p for p in base['paths'] if not set(p['effect_ids']) & ids]
        validate_batch(self.batch, base, read_json(OUT/'arphex-combat-census.json'))
        def identities(rows):
            return {(c['native_parameter_identity']['entry'], c['native_parameter_identity']['method'],
                     c['native_parameter_identity']['offset'], parameter)
                    for r in rows for c in r['scalable_parameter_candidates'] for parameter in c['parameters']}
        self.assertFalse(identities(base['effects']) & identities(self.batch['effects']))

    def test_pinned_class_and_native_recipient_local_bytes(self):
        from pathlib import Path
        jar = Path('/workspace/.cache/large-mod-campaign/ArPhEx-5.0.2-neoforge-1.21.1.jar')
        if not jar.exists():
            self.skipTest('Pinned archive unavailable; evidence/consumer tests still run')
        with zipfile.ZipFile(jar) as archive:
            data = archive.read(self.witness['entry'])
        self.assertEqual(hashlib.sha256(data).hexdigest(), self.witness['entry_sha256'])
        method = next(m for m in ClassFile(data).methods if m['name'] == 'execute'
                      and 'Lnet/neoforged/bus/api/Event;' in m['descriptor'])
        self.assertEqual(hashlib.sha256(method['code']).hexdigest(), self.method['code_sha256'])
        for offset, origin in [(13657, 9), (14199, 11), (14322, 9), (14369, 11), (15627, 11)]:
            binding = effect_receiver_binding(self.method, offset)
            load = binding['origin_load_offset']
            self.assertEqual(method['code'][load:load+2], bytes([0x19, origin]))

    def test_source_statuses_are_not_silently_assigned_to_victim(self):
        dagger = self.row('abyssal_dagger_incoming_payload')
        mapped = {c['native_consumer']['offset']: c for c in dagger['scalable_parameter_candidates']}
        for offset, role in [(14104, 9), (14152, 9), (14199, 11), (14322, 9), (14369, 11)]:
            self.assertEqual(mapped[offset]['native_receiver_binding']['origin_local_index'], role)
        guard = self.row('incoming_weapon_angular_guard')['scalable_parameter_candidates'][0]
        self.assertEqual(guard['native_receiver_binding']['origin_local_index'], 11)
        for site in guard['additional_consumer_sites']:
            self.assertEqual(effect_receiver_binding(self.method, site['offset'])['origin_local_index'], 11)

    def test_vehicle_passenger_has_its_own_native_getter_and_profile(self):
        self.assertEqual(self.by_offset[15634]['local_index'], 11)
        self.assertEqual(self.by_offset[15636]['operand'],
                         'net/minecraft/world/entity/Entity.getFirstPassenger()Lnet/minecraft/world/entity/Entity;')
        self.assertEqual(self.by_offset[15639]['local_index'], 46)
        row = self.row('moth_summon_vehicle_incoming_heal')
        source, passenger = row['scalable_parameter_candidates']
        self.assertEqual(source['native_receiver_binding']['origin_local_index'], 11)
        self.assertEqual(passenger['native_receiver_binding']['origin_local_index'], 46)
        self.assertEqual(passenger['native_recipient_role'], 'causing_entity_current_first_passenger')
        self.assertEqual(self.by_offset[15624]['operand'], 3)
        self.assertEqual(self.by_offset[15678]['operand'], 1)

    def test_native_rng_bounds_and_seven_distinct_deferred_commands(self):
        for offset, upper in [(8243, 4), (9555, 2), (15469, 5)]:
            at = next(n for n, i in enumerate(self.body) if i['offset'] == offset)
            self.assertEqual([i['operand'] for i in self.body[at-2:at]], [1, upper])
            self.assertEqual(self.body[at+1]['operand'], 2)
            self.assertEqual(self.body[at+2]['opcode'], '0xa0')
        commands = []
        for method in self.witness['methods']:
            for i in method['instructions']:
                if i['operand'] == 'execute at @p run tp @e[type=arphex:scorpion_striker,limit=1,sort=nearest,distance=..6] @p':
                    commands.append(method['name'])
        self.assertEqual(sorted(commands), [f'lambda$execute${n}' for n in range(33, 40)])
        row = self.row('scorpion_striker_incoming_payload')
        delays = [c for c in row['scalable_parameter_candidates'] if c['primitive'] == 'DELAYED_DELIVERY']
        for n, c in enumerate(delays, 1):
            at = next(j for j, i in enumerate(self.body) if i['offset'] == c['native_consumer']['offset'])
            self.assertEqual(self.body[at-6]['operand'], n*3)
            self.assertIn('run(Lnet/minecraft/world/level/LevelAccessor;DDD)', self.body[at-1]['operand'])

    def test_necrosis_preserves_integer_armor_division_and_anonymous_source(self):
        self.assertEqual(self.by_offset[10384]['operand'], 'net/minecraft/world/entity/LivingEntity.getArmorValue()I')
        self.assertEqual([self.by_offset[o]['opcode'] for o in [10391,10392,10393,10394,10395]],
                         ['0x8','0x6c','0x87','0x6f','0x90']) # 5, idiv, i2d, ddiv, d2f
        self.assertEqual(self.by_offset[10362]['operand'], 2.5)
        self.assertEqual(self.by_offset[10359]['operand'], 3)
        candidate = next(c for c in self.row('necrosis')['scalable_parameter_candidates'] if c['primitive'] == 'NATIVE_DAMAGE_REQUEST')
        self.assertIn('DamageTypes.WITHER', candidate['native_damage_type_symbol'])
        self.assertEqual(candidate['native_damage_source_constructor'],
                         'net/minecraft/world/damagesource/DamageSource.<init>(Lnet/minecraft/core/Holder;)V')
        self.assertEqual(len(candidate['additional_consumer_sites']), 7)
        for offset in [10396] + [s['offset'] for s in candidate['additional_consumer_sites']]:
            at = next(n for n, i in enumerate(self.body) if i['offset'] == offset)
            self.assertEqual(self.body[at+1]['opcode'], '0x57') # ignores hurt boolean

    def test_mantis_is_an_extra_request_not_an_event_amount_replacement(self):
        window = [i for i in self.body if 12890 <= i['offset'] <= 12954]
        self.assertEqual(sum(i['opcode'] == '0x72' for i in window), 2) # native float modulo
        self.assertEqual(self.by_offset[12946]['operand'], 1.5)
        self.assertEqual(self.by_offset[12944]['local_index'], 12) # supplied original amount
        self.assertEqual(self.by_offset[12954]['opcode'], '0x57')
        self.assertFalse(any('setAmount(' in str(i['operand']) or 'setCanceled(' in str(i['operand']) for i in window))

    def test_binary_effect_amplifiers_are_preserved_without_inventing_magnitude(self):
        for name, primitive in [('tiny_breacher_incoming_payload','MOB_EFFECT_BLINDNESS'),
                                ('mosquito_incoming_payload','MOB_EFFECT_NAUSEA'),
                                ('incoming_weapon_angular_guard','MOB_EFFECT_GLOWING'),
                                ('abyssal_dagger_incoming_payload','MOB_EFFECT_INVISIBILITY')]:
            row = self.row(name)
            self.assertIn('amplifier', next(c for c in row['components'] if c['primitive'] == primitive)['numerical_parameters'])
            self.assertEqual(next(c for c in row['scalable_parameter_candidates'] if c['primitive'] == primitive)['parameters'], ['duration'])


if __name__ == '__main__':
    unittest.main()
