"""Independent native setup/indirect-delivery checks for the last finite scope."""
import copy
import unittest
from catalog_common import OUT, read_json
from assemble_authored_contracts import render
from promote_combat_batch import validate_batch


def body(cls,name):
    spec=read_json(OUT/'native-findings/alexscaves-remaining-utility-context.json')
    ss=[p for r in spec['contracts']+spec['exclusions'] for p in r['implementation']]
    ss += [p for r in spec['record_refinements'] for p in r['implementation_additions']]
    p=next(p for p in ss if p['entry'].endswith('/'+cls+'.class') and name in p['methods'])
    w=next(w for w in read_json(OUT/p['evidence_file'])['witnesses'] if w['entry']==p['entry'])
    return next(m['instructions'] for m in w['methods'] if m['name']==name)


class UtilityContextTests(unittest.TestCase):
    def test_render_native_proofs_and_no_duplicate_new_payload(self):
        b=read_json(OUT/'alexscaves-r2m9-independent-native-closure.json')
        self.assertEqual(b,render(read_json(OUT/'native-findings/alexscaves-remaining-utility-context.json')))
        r=copy.deepcopy(read_json(OUT/'mod-reviews/alexscaves.json'));ids={e['id'] for e in b['effects']}
        r['effects']=[e for e in r['effects'] if e['id'] not in ids]
        r['paths']=[p for p in r['paths'] if not ids.intersection(p['effect_ids'])]
        self.assertEqual(validate_batch(b,r,read_json(OUT/'alexscaves-combat-census.json'))['status'],'PASS')

    def test_native_reputation_clamp_and_boss_activity_are_separate(self):
        b=body('ACWorldData','setDeepOneReputation')
        at=next(n for n,i in enumerate(b) if 'Mth.clamp(' in str(i['operand']))
        self.assertEqual([i['operand'] for i in b[at-2:at]],[-100,100])
        s=str(body('ACWorldData','isPrimordialBossActive'))
        for marker in ('LuxtructosaurusEntity','.isAlive(','.isLoadedInWorld('):self.assertIn(marker,s)
        for marker in ('.hurt(','.spawn(','.heal('):self.assertNotIn(marker,s)

    def test_dispenser_preserves_success_gated_original_extra_content(self):
        b=body('FluidContainerDispenseItemBehavior','execute');s=str(b)
        empty=next(i['offset'] for i in b if '.emptyContents(' in str(i['operand']))
        extra=next(i['offset'] for i in b if '.checkExtraContent(' in str(i['operand']))
        self.assertLess(empty,extra)
        self.assertTrue(any(i['opcode']=='0x99' for i in b if empty<i['offset']<extra))
        self.assertIn('Items.BUCKET',s);self.assertNotIn('.setOwner(',s)

    def test_exact_template_payloads_have_no_entities_and_keep_native_block_data(self):
        d=read_json(OUT/'native-evidence/alexscaves-utility-template-payloads.json')
        ps=[w['structure_payload'] for w in d['witnesses'] if 'structure_payload' in w]
        self.assertEqual(len(ps),57)
        self.assertTrue(all(not p['entities'] for p in ps))
        self.assertEqual([w['entry'] for w in d['witnesses'] if w.get('entry_absent')],
                         ['data/alexscaves/structure/magnetic_ruins_4.nbt'])
        be=[b['nbt'] for p in ps for b in p['block_payloads']]
        self.assertTrue(any(b.get('ExtenderIngots')==19 for b in be))
        self.assertTrue(any(b.get('id')=='alexscaves:abyssal_altar' and 'PlayerUUID' in b for b in be))

    def test_hazmat_tick_is_particle_delivery_and_furnace_result_is_native_acquisition(self):
        s=str(body('HazmatArmorItem','onArmorTick'))
        self.assertIn('HAZMAT_BREATHE',s)
        for marker in ('.hurt(','.addEffect(','.heal('):self.assertNotIn(marker,s)
        s=str(body('NuclearFurnaceResultSlot','checkTakeAchievements'))
        for marker in ('.onCraftedBy(','.awardUsedRecipesAndPopExperience(','.firePlayerSmeltedEvent('):self.assertIn(marker,s)
        self.assertNotIn('.hurt(',s)


if __name__=='__main__':unittest.main()
