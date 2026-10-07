"""Native setup facts and remaining consumers; names never prove an effect."""
import copy
import unittest
from assemble_authored_contracts import render
from catalog_common import OUT,read_json
from promote_combat_batch import validate_batch

def witness(cls,packet='native-setup'):
 return next(w for w in read_json(OUT/f'native-evidence/alexscaves-{packet}.json')['witnesses'] if w['entry'].endswith('/'+cls+'.class'))
def body(cls,method,packet='native-setup'):
 return next(m['instructions'] for m in witness(cls,packet)['methods'] if m['name']==method)

class SetupTests(unittest.TestCase):
 def test_render_and_exact_consumer_binding(self):
  b=read_json(OUT/'alexscaves-r2m8t-registry-block-setup.json')
  self.assertEqual(b,render(read_json(OUT/'native-findings/alexscaves-registry-block-setup.json')))
  r=copy.deepcopy(read_json(OUT/'mod-reviews/alexscaves.json'));ids={e['id'] for e in b['effects']}
  r['effects']=[e for e in r['effects'] if e['id'] not in ids];r['paths']=[e for e in r['paths'] if not ids.intersection(e['effect_ids'])]
  self.assertEqual(validate_batch(b,r,read_json(OUT/'alexscaves-combat-census.json'))['status'],'PASS')
 def test_enchantments_do_not_define_native_effect_dispatch(self):
  resources=[w for w in read_json(OUT/'native-evidence/alexscaves-native-setup.json')['witnesses'] if '/enchantment/' in w['entry'] and w['entry'].endswith('.json')]
  self.assertEqual(len(resources),53)
  self.assertTrue(all(not w['data'].get('effects') for w in resources))
 def test_attributes_and_spawn_setup_are_native_bindings(self):
  b=body('ACEntityRegistry','initializeAttributes');self.assertEqual(sum('EntityAttributeCreationEvent.put(' in str(i['operand']) for i in b),44)
  self.assertEqual(sum('BoundroidEntity.createAttributes(' in str(i['operand']) for i in b),2)
  b=body('ACEntityRegistry','spawnPlacements');self.assertEqual(sum('RegisterSpawnPlacementsEvent.register(' in str(i['operand']) for i in b),42)
 def test_depth_glass_binds_friction_not_a_synthetic_velocity_write(self):
  b=body('DepthGlassBlock','<init>','remaining-block-setup');self.assertIn('Properties.friction(F)',str(b))
  self.assertNotIn('.setDeltaMovement(',str(b))
 def test_barrel_native_aggro_source_is_the_interacting_player(self):
  for cls in ('GingerbarrelBlock','MetalBarrelBlock'):
   b=body(cls,'useWithoutItem','remaining-block-setup');self.assertIn('PiglinAi.angerNearbyPiglins',str(b));self.assertIn('Level.isClientSideZ',str(b))
   self.assertNotIn('.hurt(',str(b))
 def test_encounter_and_terrain_producers_do_not_invent_owner(self):
  b=body('AbyssalRuinsStructurePiece','spawnSubmarine','remaining-block-setup');self.assertIn('.setDamageLevel(',str(b));self.assertNotIn('.setOwner(',str(b))
  b=body('SubterranodonRoostFeature','fillCliff','remaining-block-setup');self.assertIn('.restrictTo(',str(b));self.assertIn('NEEDS_PLAYER',str(b));self.assertNotIn('.setOwner(',str(b))
 def test_vallum_hide_gate_is_not_a_watcher_refinement(self):
  b=read_json(OUT/'alexscaves-r2m8s-residual-control-context.json')
  refs=[r['id'] for r in b['record_refinements'] if 'livingFindTarget' in str(r['implementation_additions'])]
  self.assertEqual(refs,['alexscaves:vallumraptor_native_pack_attack_hide_and_food'])

if __name__=='__main__':unittest.main()
