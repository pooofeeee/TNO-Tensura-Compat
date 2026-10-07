"""Native gates, inactive dispatcher methods and strict context proof invariants."""
import copy
import tempfile
import unittest
import zipfile
from pathlib import Path
from assemble_authored_contracts import render
from catalog_common import OUT,read_json,sha256
from promote_combat_batch import validate_batch
from selected_reference import collect

def body(cls,method):
    w=next(w for w in read_json(OUT/'native-evidence/alexscaves-residual-control.json')['witnesses'] if w['entry'].endswith('/'+cls+'.class'))
    return next(m['instructions'] for m in w['methods'] if m['name']==method)

class ResidualTests(unittest.TestCase):
    def test_render_and_source_binding(self):
        b=read_json(OUT/'alexscaves-r2m8s-residual-control-context.json');self.assertEqual(b,render(read_json(OUT/'native-findings/alexscaves-residual-control-context.json')))
        r=copy.deepcopy(read_json(OUT/'mod-reviews/alexscaves.json'));ids={e['id'] for e in b['effects']}
        r['effects']=[e for e in r['effects'] if e['id'] not in ids];r['paths']=[e for e in r['paths'] if not ids.intersection(e['effect_ids'])]
        self.assertEqual(validate_batch(b,r,read_json(OUT/'alexscaves-combat-census.json'))['status'],'PASS')
    def test_submarine_bucket_is_not_living_health_damage(self):
        b=str(body('SubmarineEntity','hurt'));self.assertIn('.damageSustainedD',b);self.assertIn('.isInvulnerableTo(',b);self.assertNotIn('Entity.hurt(',b)
        b=str(body('SubmarineEntity','positionRider'));self.assertIn('.setAirSupply(',b);self.assertIn('.stopRiding(',b)
    def test_submarine_native_save_read_type_discrepancy_preserved(self):
        self.assertIn('putDouble',str(body('SubmarineEntity','addAdditionalSaveData')))
        b=str(body('SubmarineEntity','readAdditionalSaveData'));self.assertIn('DamageSustained',b);self.assertIn('getInt',b)
    def test_dispenser_unused_factories_have_no_hook_or_native_callers(self):
        c=read_json(OUT/'alexscaves-combat-census.json');sy=c['symbols']
        self.assertFalse(any('ACItemRegistry$' in sy[s[2]] and '.getProjectile(' in sy[s[2]] for m in c['methods'] for s in m['calls']))
        w=next(w for w in read_json(OUT/'vanilla-evidence/alexscaves-dispenser-api.json')['classes'] if w['class_name']=='net/minecraft/core/dispenser/DefaultDispenseItemBehavior')
        self.assertNotIn('getProjectile',{m['name'] for m in w['declared_methods']})
        self.assertTrue(any('ItemEntity.<init>' in str(m['instructions']) for m in w['methods']))
        p=read_json(OUT/'native-evidence/alexscaves-item-consumers.json')
        for i in range(1,7):
            w=next(w for w in p['witnesses'] if w['entry'].endswith('/ACItemRegistry$'+str(i)+'.class'))
            self.assertEqual(w['superclass'],'net/minecraft/core/dispenser/DefaultDispenseItemBehavior')
    def test_reference_absence_rejects_an_existing_resource(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'reference.zip'
            with zipfile.ZipFile(p,'w') as z:z.writestr('exists.patch','native')
            s={'id':'test','scope':'exact absence','archives':[{'path':str(p),'sha256':sha256(p),'absent_resources':['missing.patch']}]}
            self.assertTrue(collect(s)['witnesses'][0]['absent'])
            s['archives'][0]['absent_resources']=['exists.patch']
            with self.assertRaises(AssertionError):collect(s)
    def test_hologram_display_is_only_reached_from_render_audio(self):
        c=read_json(OUT/'alexscaves-combat-census.json');sy=c['symbols'];callers=[m for m in c['methods'] if any('HologramProjectorBlockEntity.getDisplayEntity(' in sy[s[2]] for s in m['calls'])]
        self.assertEqual(len(callers),2);self.assertTrue(all('/client/render/' in m['entry'] or '/client/sound/' in m['entry'] for m in callers))
        self.assertNotIn('.addFreshEntity(',str(body('HologramProjectorBlockEntity','tick')))
    def test_submarine_setup_does_not_invent_an_owner(self):
        b=str(body('EnigmaticEngineBlockEntity','attemptAssembly'));self.assertIn('SubmarineEntity',b);self.assertNotIn('.setOwner(',b)
    def test_egg_breed_only_sets_native_egg_state(self):
        b=str(body('AnimalBreedEggsGoal','breed'));self.assertIn('.setHasEgg(',b);self.assertNotIn('DinosaurEgg',b)

if __name__=='__main__':unittest.main()
