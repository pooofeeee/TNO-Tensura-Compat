"""Native pet combat dispatch, state order and resource boundaries."""
import unittest
from assemble_authored_contracts import render
from audit_numeric_labels import audit
from catalog_common import OUT, read_json
from promote_combat_batch import validate_batch
from test_alexsmobs_terrestrial_predator_contracts import method, calls

class TerrestrialPets(unittest.TestCase):
    def test_exact_render_and_numeric_bindings(self):
        b=read_json(OUT/'alexsmobs-r2o5d-terrestrial-pets.json')
        self.assertEqual(render(read_json(OUT/'native-specifications/alexsmobs-terrestrial-pet-contracts.json')),b)
        r=read_json(OUT/'mod-reviews/alexsmobs.json'); ids={e['id'] for e in b['effects']}
        r['effects']=[e for e in r['effects'] if e['id'] not in ids]
        r['paths']=[p for p in r['paths'] if not set(p['effect_ids'])&ids]
        validate_batch(b,r,read_json(OUT/'alexsmobs-combat-census.json'))
        self.assertEqual(audit(dict(effects=b['effects']))['unresolved_numeric_labels'],0)

    def test_elephant_two_counter_increments_and_reset(self):
        b=method('entity/EntityElephant','tick')['instructions']
        writes=[i for i in b if i['opcode']=='0xb5' and '.chargingTicksI' in str(i['operand'])]
        self.assertEqual(len(writes),3)
        self.assertEqual([b[b.index(i)-1]['opcode'] for i in writes],['0x60','0x60','0x3'])

    def test_elephant_charge_contact_ignores_hurt_result(self):
        b=method('entity/EntityElephant','tick')['instructions']; hit=calls(b,'.hurt(')[-1]
        self.assertEqual(b[b.index(hit)+1]['opcode'],'0x57')
        self.assertTrue(calls(b[b.index(hit)+1:],'.launch('))
        self.assertFalse(calls(b[b.index(hit)-20:],'.isClientSide'))

    def test_elephant_tusked_else_restores_normal_damage(self):
        b=method('entity/EntityElephant','setTusked')['instructions']
        self.assertEqual([i['operand'] for i in b if i['offset'] in (20,33,40,56,69)],[110.,15.,150.,85.,10.])
        self.assertEqual(len(calls(b,'.setHealth(')),1)

    def test_kangaroo_old_overload_and_native_direct_call(self):
        x=method('entity/ai/KangarooAIMelee','checkAndPerformAttack')
        self.assertTrue(x['descriptor'].endswith(';D)V'))
        b=method('entity/ai/KangarooAIMelee','tick')['instructions']
        self.assertEqual(len(calls(b,'.checkAndPerformAttack(')),1)
        vanilla=read_json(OUT/'vanilla-evidence/alexsmobs-predator-native-dispatch.json')
        c=next(c for c in vanilla['classes'] if c['class_name'].endswith('/MeleeAttackGoal'))
        self.assertEqual(c['methods'][0]['obfuscated_descriptor'].count(';'),1)
        self.assertNotIn('D)',c['methods'][0]['obfuscated_descriptor'])

    def test_kangaroo_air_control_is_independent_of_hurt(self):
        b=method('entity/ai/KangarooAIMelee','tick')['instructions']
        self.assertEqual(len(calls(b,'.setAirSupply(')),1)
        self.assertFalse(calls(b,'.hurt('))
        self.assertEqual(next(i['operand'] for i in b if i['offset']==74),30)

    def test_kangaroo_scorers_compare_attribute_value_to_holder(self):
        for name in ('getDamageForItem','getProtectionForItem'):
            b=method('entity/EntityKangaroo',name)['instructions']
            hit=calls(b,'Holder.value(')[0]; tail=b[b.index(hit)+1:b.index(hit)+3]
            self.assertEqual(tail[0]['opcode'],'0xb2')
            self.assertIn('Lnet/minecraft/core/Holder;',tail[0]['operand'])
            self.assertEqual(tail[1]['opcode'],'0xa6')

    def test_kangaroo_durability_uses_mainhand_for_armor(self):
        b=method('entity/EntityKangaroo','damageItem')['instructions']
        self.assertTrue(any('.MAINHANDL' in str(i['operand']) for i in b))
        self.assertTrue(calls(b,'.hurtAndBreak(')); self.assertTrue(calls(b,'.shrink('))

    def test_raccoon_fallback_eat_does_not_tame(self):
        b=method('entity/EntityRaccoon','tick')['instructions']
        self.assertTrue(calls(b,'.onEatItem(')); self.assertFalse(calls(b,'.postWashItem('))
        w=method('entity/ai/RaccoonAIWash','tick')['instructions']
        self.assertTrue(calls(w,'.onEatItem(')); self.assertTrue(calls(w,'.postWashItem('))

    def test_raccoon_theft_zero_generic_hurt_does_not_require_acceptance(self):
        b=method('entity/EntityRaccoon$AIStealFromVillagers','tick')['instructions']
        h=calls(b,'.hurt(')[0]; n=b.index(h)
        self.assertEqual(b[n-1]['operand'],0.0)
        self.assertTrue(calls(b[:n],'.generic('))
        self.assertEqual(b[n+1]['opcode'],'0x57')

if __name__=='__main__': unittest.main()
