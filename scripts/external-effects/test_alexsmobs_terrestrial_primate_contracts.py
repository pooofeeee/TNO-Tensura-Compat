"""Primate native self heal, veto and attribute transition boundaries."""
import unittest

from assemble_authored_contracts import render
from audit_numeric_labels import audit
from catalog_common import OUT, read_json
from promote_combat_batch import validate_batch
from test_alexsmobs_terrestrial_predator_contracts import method, calls


class TerrestrialPrimates(unittest.TestCase):
    def test_exact_render_and_numeric_bindings(self):
        b = read_json(OUT/'alexsmobs-r2o5d-terrestrial-primates.json')
        self.assertEqual(render(read_json(OUT/'native-specifications/alexsmobs-terrestrial-primate-contracts.json')), b)
        r = read_json(OUT/'mod-reviews/alexsmobs.json')
        ids = {row['id'] for row in b['effects']}
        r['effects'] = [row for row in r['effects'] if row['id'] not in ids]
        r['paths'] = [row for row in r['paths'] if not set(row['effect_ids']) & ids]
        validate_batch(b, r, read_json(OUT/'alexsmobs-combat-census.json'))
        self.assertEqual(audit(dict(effects=b['effects']))['unresolved_numeric_labels'], 0)

    def test_gelada_revenge_veto_is_overwritten_and_not_decremented(self):
        b = method('entity/EntityGeladaMonkey', 'hurt')['instructions']
        writes = [i for i in b if i['opcode'] == '0xb5' and '.revengeCooldownI' in str(i['operand'])]
        self.assertEqual(len(writes), 2)
        tick = method('entity/EntityGeladaMonkey', 'tick')['instructions']
        self.assertFalse(any('.revengeCooldownI' in str(i['operand']) for i in tick))
        self.assertEqual([i['operand'] for i in b if i['offset'] in (47, 53)], [10, 30])

    def test_gelada_spar_retains_zero_hurt_after_knockback(self):
        b = method('entity/EntityGeladaMonkey', 'tick')['instructions']
        hit = calls(b, '.hurt(')[0]
        self.assertLess(calls(b, '.knockback(')[0]['offset'], hit['offset'])
        self.assertEqual(b[b.index(hit)+1]['opcode'], '0x57')
        self.assertEqual(next(i['operand'] for i in b if i['offset'] == 390), 0.0)

    def test_groom_heals_groomer_field_not_recipient(self):
        b = method('entity/ai/GeladaAIGroom', 'tick')['instructions']
        hit = calls(b, '.heal(')[0]
        previous = b[b.index(hit)-3:b.index(hit)]
        self.assertTrue(any('.monkeyL' in str(i['operand']) for i in previous))
        self.assertFalse(any('.beingGroomedL' in str(i['operand']) for i in previous))
        self.assertEqual(b[b.index(hit)-1]['operand'], 1.0)

    def test_gorilla_knockback_before_ignored_frame_damage(self):
        b = method('entity/EntityGorilla', 'tick')['instructions']
        hit = calls(b, '.hurt(')[0]
        self.assertLess(calls(b, '.knockback(')[0]['offset'], hit['offset'])
        self.assertEqual(b[b.index(hit)+1]['opcode'], '0x57')

    def test_gorilla_switched_back_attack_differs_from_initial_base(self):
        base = method('entity/EntityGorilla', 'bakeAttributes')['instructions']
        tick = method('entity/EntityGorilla', 'tick')['instructions']
        self.assertEqual(next(i['operand'] for i in base if i['offset'] == 31), 7.0)
        self.assertEqual(next(i['operand'] for i in tick if i['offset'] == 1243), 8.0)
        self.assertEqual(len(calls(tick, '.setBaseValue(')), 4)

    def test_gorilla_gaze_charge_has_no_recipient_damage_or_status(self):
        b = method('entity/ai/GorillaAIChargeLooker', 'tick')['instructions']
        for sym in ('.hurt(', '.addEffect(', '.setTarget('):
            self.assertFalse(calls(b, sym))
        self.assertTrue(calls(b, '.moveTo('))

    def test_gorilla_leaf_change_retains_grief_gate(self):
        b = method('entity/ai/GorillaAIForageLeaves', 'breakLeaves')['instructions']
        self.assertLess(calls(b, 'EventHooks.canEntityGrief(')[0]['offset'], calls(b, '.destroyBlock(')[0]['offset'])
        self.assertEqual(len(calls(b, '.addFreshEntity(')), 2)
        self.assertFalse(calls(b, '.heal('))


if __name__ == '__main__':
    unittest.main()
