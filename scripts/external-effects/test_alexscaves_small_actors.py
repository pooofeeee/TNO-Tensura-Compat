"""Small-actor claims checked against native branches, sinks and declarations."""
import copy
import unittest

from catalog_common import OUT, read_json
from assemble_authored_contracts import render
from collect_combat_census import decode_sites
from promote_combat_batch import validate_batch

P = 'com/github/alexmodguy/alexscaves/'


def method(short, name, scope='small-actors'):
    packet = read_json(OUT / f'native-evidence/alexscaves-{scope}.json')
    witness = next(w for w in packet['witnesses'] if w['entry'] == P + short + '.class')
    return next(m for m in witness['methods'] if m['name'] == name)


def body(actor, name):
    return method('server/entity/living/' + actor + 'Entity', name)['instructions']


class SmallActorsTests(unittest.TestCase):
    def test_authored_batch_regenerates_and_binds_original_inputs(self):
        batch = read_json(OUT / 'alexscaves-r2m8f-small-actors.json')
        self.assertEqual(render(read_json(OUT / 'native-findings/alexscaves-small-actors-contracts.json')), batch)
        review = copy.deepcopy(read_json(OUT / 'mod-reviews/alexscaves.json'))
        ids = {r['id'] for r in batch['effects']}
        review['effects'] = [r for r in review['effects'] if r['id'] not in ids]
        review['paths'] = [r for r in review['paths'] if not set(r['effect_ids']) & ids]
        validate_batch(batch, review, read_json(OUT / 'alexscaves-combat-census.json'))
        self.assertEqual(sum(len(c['parameters']) for r in batch['effects']
                             for c in r['scalable_parameter_candidates']), 5)

    def test_native_dry_out_shape_is_independent_of_species_liquid_gate(self):
        resets = {'Lanternfish': 200, 'Radgill': 500, 'SeaPig': 40, 'SweetishFish': 400}
        for actor, reset in resets.items():
            instructions = body(actor, 'handleAirSupply')
            at = {i['offset']: i for i in instructions}
            self.assertEqual(at[43]['operand'], 2.0)
            self.assertIn('DamageSources.dryOut()', at[40]['operand'])
            self.assertIn('.hurt(', at[44]['operand'])
            self.assertEqual(at[47]['opcode'], '0x57')
            self.assertIn(-20, [i['operand'] for i in instructions])
            self.assertIn(reset, [i['operand'] for i in instructions])
        self.assertIn('isInAcid', str(body('Radgill', 'isInLiquid')))
        self.assertIn('isInSoda', str(body('SweetishFish', 'isInLiquid')))

    def test_trilocaris_has_two_native_attempts_not_one_merged_damage(self):
        immediate = body('Trilocaris', 'doHurtTarget')
        self.assertIn(5, [i['operand'] for i in immediate])
        self.assertIn('SynchedEntityData.set', str(immediate))
        self.assertTrue(any(i['opcode'] == '0xb7' and '.doHurtTarget(' in str(i['operand'])
                            for i in immediate))
        self.assertEqual(immediate[-1]['opcode'], '0xac')
        delayed = body('Trilocaris', 'tick'); at = {i['offset']: i for i in delayed}
        self.assertIn('DamageSources.mobAttack', at[191]['operand'])
        self.assertIn('Attributes.ATTACK_DAMAGE', at[195]['operand'])
        self.assertIn('.hurt(', at[205]['operand'])
        self.assertEqual(at[208]['opcode'], '0x57')

    def test_raycat_heal_precedes_native_irradiation_and_target_removal(self):
        instructions = body('Raycat', 'tick'); at = {i['offset']: i for i in instructions}
        self.assertEqual(at[160]['operand'], 1.0)
        self.assertIn('.heal(', at[161]['operand'])
        self.assertEqual(at[450]['operand'], 10.0)
        self.assertIn('.heal(', at[452]['operand'])
        self.assertEqual(at[463]['operand'], 200)
        self.assertIn('ACEffectRegistry.IRRADIATED', at[460]['operand'])
        self.assertIn('MobEffectInstance.<init>', at[467]['operand'])
        self.assertIn('.addEffect(', at[470]['operand'])
        remove = next(i['offset'] for i in instructions if '.removeEffect(' in str(i['operand']))
        self.assertLess(452, 470); self.assertLess(470, remove); self.assertLess(remove, 559)
        tags = read_json(OUT / 'native-evidence/alexscaves-small-actor-tags.json')
        self.assertIn('alexscaves:raycat', tags['witnesses'][0]['data']['values'])
        self.assertNotIn('setTarget', str(body('Raycat', 'registerGoals')))

    def test_hurt_dependent_flee_is_after_native_result(self):
        instructions = body('Tripodfish', 'hurt')
        parent = next(n for n, i in enumerate(instructions)
                      if i['opcode'] == '0xb7' and '.hurt(' in str(i['operand']))
        self.assertEqual([i['opcode'] for i in instructions[parent + 1:parent + 4]],
                         ['0x3e', '0x1d', '0x99'])
        self.assertEqual(instructions[parent + 1]['local_index'],
                         instructions[parent + 2]['local_index'])
        self.assertTrue(any(i['opcode'] == '0xb5' and '.fleeFor' in str(i['operand'])
                            for i in instructions[parent + 2:]))

    def test_conversion_does_not_synthesize_damage_or_success_callback(self):
        instructions = body('Gloomoth', 'tick')
        calls = [str(i['operand']) for i in instructions]
        sacrifice = next(n for n, op in enumerate(calls) if '.postSacrifice(' in op)
        conversion = next(n for n, op in enumerate(calls) if '.convertTo(' in op)
        self.assertLess(sacrifice, conversion)
        self.assertTrue(any('ACEntityRegistry.WATCHER' in op for op in calls))
        self.assertFalse(any('.hurt(' in op or '.heal(' in op for op in calls))

    def test_lanternfish_legacy_helper_is_not_native_spawn_override(self):
        helper = method('server/entity/living/LanternfishEntity', 'finalizeSpawn')
        self.assertIn('Lnet/minecraft/nbt/CompoundTag;', helper['descriptor'])
        census = read_json(OUT / 'alexscaves-combat-census.json')
        for m in census['methods']:
            self.assertFalse(any('LanternfishEntity.finalizeSpawn(' in i['operand']
                                 for i in decode_sites(census, m, 'calls')))
        self.assertFalse(any('LanternfishEntity.finalizeSpawn' in str(b['arguments'])
                             for b in census['registration_bootstraps']))
        vanilla = read_json(OUT / 'vanilla-evidence/alexscaves-status-lifecycle.json')
        mob = next(c for c in vanilla['classes'] if c['class_name'] == 'net/minecraft/world/entity/Mob')
        native = [m['obfuscated_descriptor'] for m in mob['declared_methods'] if m['name'] == 'finalizeSpawn']
        self.assertEqual(len(native), 1)
        self.assertEqual(native[0], '(Lddl;Lbqp;Lbtr;Lbuh;)Lbuh;')
        loader = read_json(OUT / 'reference-evidence/alexscaves-native-spawn-callback.json')
        text = str(loader['witnesses'][0]['text_sections'])
        self.assertIn('finalizeSpawn(ServerLevelAccessor', text)
        self.assertNotIn('CompoundTag', text)


if __name__ == '__main__':
    unittest.main()
