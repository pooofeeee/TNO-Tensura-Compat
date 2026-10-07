"""Pinned dispatch and consumer facts, independent of authored classifications."""
import copy
import unittest
from assemble_authored_contracts import render
from catalog_common import OUT,read_json
from promote_combat_batch import validate_batch

def witness(name,scope='item-consumers'):
    return next(w for w in read_json(OUT/f'native-evidence/alexscaves-{scope}.json')['witnesses'] if w['entry'].endswith('/'+name+'.class'))
def body(name,method,scope='item-consumers'):
    return next(m['instructions'] for m in witness(name,scope)['methods'] if m['name']==method)

class EquippedFoodTests(unittest.TestCase):
    def test_deterministic_render_and_pinned_bindings(self):
        b=read_json(OUT/'alexscaves-r2m8q-equipped-food-consumers.json')
        self.assertEqual(b,render(read_json(OUT/'native-findings/alexscaves-equipped-food-consumers.json')))
        review=copy.deepcopy(read_json(OUT/'mod-reviews/alexscaves.json'));ids={r['id'] for r in b['effects']}
        review['effects']=[r for r in review['effects'] if r['id'] not in ids]
        review['paths']=[r for r in review['paths'] if not ids.intersection(r['effect_ids'])]
        self.assertEqual(validate_batch(b,review,read_json(OUT/'alexscaves-combat-census.json'))['status'],'PASS')
    def test_current_loader_hook_signatures_exclude_legacy_methods(self):
        w=read_json(OUT/'reference-evidence/alexscaves-equipment-api.json')['witnesses'][0]
        members={(m['name'],m['descriptor']) for m in w['declared_methods']}
        self.assertIn(('getDefaultAttributeModifiers','(Lnet/minecraft/world/item/ItemStack;)Lnet/minecraft/world/item/component/ItemAttributeModifiers;'),members)
        self.assertFalse(any(n in ('getAttributeModifiers','onArmorTick') for n,d in members))
        self.assertIn(('getEquipmentSlot','(Lnet/minecraft/world/item/ItemStack;)Lnet/minecraft/world/entity/EquipmentSlot;'),members)
        c=read_json(OUT/'alexscaves-combat-census.json')
        calls=[c['symbols'][s[2]] for m in c['methods'] for s in m['calls']]
        self.assertFalse(any('GingerbreadArmorItem.getOrCreateDurabilityAttributes(' in s for s in calls))
        self.assertFalse(any(s.startswith('com/github/alexmodguy/alexscaves/') and '.getAttributeModifiers(' in s for s in calls))
    def test_repaired_records_preserve_real_requests_remove_dead_attributes(self):
        review=read_json(OUT/'mod-reviews/alexscaves.json');repair=read_json(OUT/'alexscaves-equipment-integrity-repair.json')
        for r in review['effects']:
            if r['id'] not in repair['affected_record_ids']:continue
            self.assertTrue(r['inactive_native_declarations'])
            self.assertFalse(any(c['primitive'] in ('ATTACK_SPEED','ATTACK_DAMAGE_ATTRIBUTE') or 'melee_add' in c['numerical_parameters'] for c in r['components']))
        self.assertIn('.hurt(',str(body('OrtholanceItem','releaseUsing')))
    def test_food_supplier_status_and_probability_are_separate_bindings(self):
        r=next(r for r in read_json(OUT/'alexscaves-r2m8q-equipped-food-consumers.json')['effects'] if r['id'].endswith(':native_food_definition_status_packages'))
        native=witness('ACFoods');suppliers={m['name'] for m in native['methods'] if m['name'].startswith('lambda$')}
        table=[p for f in r['food_definition_context'] for p in f['status_packages']]
        self.assertEqual({p['supplier'] for p in table},suppliers)
        self.assertEqual(len(table),46)
        self.assertEqual(len(r['scalable_parameter_candidates']),92)
        self.assertEqual(next(p['duration'] for p in table if 'BAD_OMEN' in p['holder']),48000)
        self.assertTrue(all(c['native_consumer']['operand'].find('MobEffectInstance.<init>')>=0 for c in r['scalable_parameter_candidates'] if c['primitive'].startswith('MOB_EFFECT_')))
    def test_food_overrides_do_not_gain_invented_removal_or_parent_eating(self):
        self.assertNotIn('finishUsingItem(',str(body('JellyBeanItem','finishUsingItem')))
        b=str(body('RadiationRemovingFoodItem','finishUsingItem'))
        self.assertIn('.setHealth(',b);self.assertNotIn('.removeEffect(',b)
        self.assertIn('.forceAddEffect(',str(body('DarkenedAppleItem','finishUsingItem')))
    def test_resistor_hurt_return_does_not_gate_knockback(self):
        b=body('ResistorShieldItem','onUseTick');n=next(n for n,i in enumerate(b) if '.hurt(' in str(i['operand']))
        self.assertEqual(b[n+1]['opcode'],'0x57');self.assertIn('.knockback(',str(b))
    def test_radioactive_destroyed_cloud_has_no_owner(self):
        b=str(body('RadioactiveOnDestroyedBlockItem','onDestroyed'))
        self.assertIn('AreaEffectCloud',b);self.assertIn('.explode(',b);self.assertNotIn('.setOwner(',b)
    def test_primordial_food_gain_is_a_modifier_argument(self):
        b=body('PlayerMixin','ac_eat','equipped-context')
        self.assertIn('FoodData.eat(IF)V',str(b));self.assertTrue(any(i['operand']==0.125 for i in b))

if __name__=='__main__':unittest.main()
