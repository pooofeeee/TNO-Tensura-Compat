"""Native null producers, empty setters and repeated delivery boundaries."""
import unittest

from assemble_authored_contracts import render
from audit_numeric_labels import audit
from catalog_common import OUT, read_json
from collect_combat_census import decode_sites
from promote_combat_batch import validate_batch
from test_alexsmobs_terrestrial_predator_contracts import method, calls, P


class TerrestrialHerds(unittest.TestCase):
    def test_render_and_independent_numeric_bindings(self):
        b = read_json(OUT/'alexsmobs-r2o5d-terrestrial-herds.json')
        self.assertEqual(render(read_json(OUT/'native-specifications/alexsmobs-terrestrial-herd-contracts.json')), b)
        r = read_json(OUT/'mod-reviews/alexsmobs.json')
        ids = {row['id'] for row in b['effects']}
        r['effects'] = [row for row in r['effects'] if row['id'] not in ids]
        r['paths'] = [row for row in r['paths'] if not set(row['effect_ids']) & ids]
        validate_batch(b, r, read_json(OUT/'alexsmobs-combat-census.json'))
        self.assertEqual(audit(dict(effects=b['effects']))['unresolved_numeric_labels'], 0)

    def test_rhino_damage_result_does_not_gate_potion(self):
        b = method('entity/EntityRhinoceros', 'attackWithPotion')['instructions']
        hit = calls(b, '.hurt(')[0]
        self.assertEqual(b[b.index(hit)+1]['opcode'], '0x57')
        effect = calls(b, '.addEffect(')[0]
        self.assertLess(hit['offset'], effect['offset'])
        self.assertEqual(b[b.index(effect)+1]['opcode'], '0x99')
        self.assertLess(effect['offset'], calls(b, '.setInflictedCount(')[0]['offset'])

    def test_rhino_null_potion_argument_and_exact_native_callers(self):
        b = method('entity/EntityRhinoceros', 'mobInteract')['instructions']
        at = b.index(calls(b, '.applyPotion(')[0])
        self.assertEqual(b[at-1]['local_index'], b[at-3]['local_index'])
        self.assertEqual(b[at-4]['opcode'], '0x1')
        c = read_json(OUT/'alexsmobs-combat-census.json')
        symbol = P+'entity/EntityRhinoceros.applyPotion(Lnet/minecraft/world/item/alchemy/Potion;)Z'
        callers = [(m['entry'], m['method'], i['offset']) for m in c['methods']
                   for i in decode_sites(c, m, 'calls') if i['operand'] == symbol]
        self.assertEqual(callers, [(P+'entity/EntityRhinoceros.class', 'mobInteract', 57)])

    def test_rhino_vertical_launch_bypasses_resistance_scaled_horizontal_strength(self):
        b = method('entity/EntityRhinoceros', 'launch')['instructions']
        self.assertTrue(calls(b, '.getAttributeValue('))
        self.assertTrue(calls(b, '.setDeltaMovement('))
        self.assertTrue(calls(b, '.setOnGround('))
        self.assertFalse(calls(b, '.knockback('))
        # Native final vertical argument loads hugeScale, not strength.
        i = next(n for n, ins in enumerate(b) if ins['offset'] == 122)
        self.assertEqual(b[i-1]['local_index'], 5)
        self.assertEqual(b[i]['operand'], 0.30000001192092896)

    def test_rhino_has_four_separate_native_potion_attack_sites(self):
        b = method('entity/EntityRhinoceros', 'tick')['instructions']
        self.assertEqual(len(calls(b, '.attackWithPotion(')), 4)
        self.assertEqual(len(calls(b, '.launch(')), 4)
        self.assertEqual([i['operand'] for i in b if i['offset'] in (381, 389, 548, 557, 566, 575)], [5, 8, 9, 11, 19, 21])

    def test_tusklin_shoe_setter_is_empty(self):
        b = method('entity/EntityTusklin', 'setShoeStack')['instructions']
        self.assertEqual(b, [dict(offset=0, opcode='0xb1', operand=None)])
        self.assertTrue(calls(method('entity/EntityTusklin', 'mobInteract')['instructions'], '.setShoeStack('))
        self.assertTrue(calls(method('entity/EntityTusklin', 'readAdditionalSaveData')['instructions'], '.setShoeStack('))

    def test_tusklin_native_tick_has_no_passivity_countdown(self):
        b = method('entity/EntityTusklin', 'tick')['instructions']
        self.assertFalse(calls(b, '.setPassiveTicks('))
        self.assertFalse(calls(b, '.getPassiveTicks('))
        b = method('entity/EntityTusklin', 'mobInteract')['instructions']
        self.assertTrue(calls(b, '.setPassiveTicks('))
        self.assertEqual(next(i['operand'] for i in b if i['offset'] == 158), 1200)

    def test_tusklin_contact_damage_is_ignored_before_raw_push(self):
        b = method('entity/EntityTusklin', 'tick')['instructions']
        hit = calls(b, '.hurt(')[0]
        self.assertEqual(b[b.index(hit)+1]['opcode'], '0x57')
        self.assertLess(hit['offset'], calls(b, '.push(')[0]['offset'])
        self.assertEqual(len(calls(b, '.hurt(')), 4)

    def test_tusklin_conversion_keeps_native_duplicate_spawn_and_discard_order(self):
        b = method('entity/EntityTusklin', 'tick')['instructions']
        order = [calls(b, sym)[0]['offset'] for sym in ('.convertTo(', '.addEffect(', '.dropEquipment(', '.addFreshEntity(', '.remove(')]
        self.assertEqual(order, sorted(order))
        save = method('entity/EntityTusklin', 'addAdditionalSaveData')['instructions']
        self.assertFalse(any('.conversionTime' in str(i['operand']) for i in save))

    def test_anteater_melee_distance_is_linear(self):
        b = method('entity/EntityAnteater$AIMelee', 'tick')['instructions']
        self.assertTrue(calls(b, '.distanceTo('))
        self.assertFalse(calls(b, '.distanceToSqr('))

    def test_anteater_tongue_removes_without_hurt(self):
        b = method('entity/EntityAnteater', 'tick')['instructions']
        self.assertTrue(calls(b, '.remove('))
        self.assertFalse(calls(b, '.hurt('))
        self.assertEqual(len(calls(b, '.doHurtTarget(')), 2)
        self.assertTrue(any('RemovalReason.KILLED' in str(i['operand']) for i in b))


if __name__ == '__main__':
    unittest.main()
