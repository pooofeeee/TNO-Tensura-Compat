"""Independent native ordering protects Forlorn damage and control contracts."""
import copy
import unittest
from assemble_authored_contracts import render
from catalog_common import OUT,read_json
from promote_combat_batch import validate_batch


def body(name,method,scope='forlorn-actors'):
 w=next(w for w in read_json(OUT/f'native-evidence/alexscaves-{scope}.json')['witnesses'] if w['entry'].endswith('/'+name+'.class'))
 return next(m for m in w['methods'] if m['name']==method)['instructions']


class ForlornContractsTests(unittest.TestCase):
 def test_regeneration_and_native_candidates(self):
  b=read_json(OUT/'alexscaves-r2m8o-forlorn-contracts.json')
  self.assertEqual(render(read_json(OUT/'native-findings/alexscaves-forlorn-contracts.json')),b)
  r=copy.deepcopy(read_json(OUT/'mod-reviews/alexscaves.json'));ids={e['id'] for e in b['effects']}
  r['effects']=[e for e in r['effects'] if e['id'] not in ids];r['paths']=[p for p in r['paths'] if not ids&set(p['effect_ids'])]
  self.assertEqual(validate_batch(b,r,read_json(OUT/'alexscaves-combat-census.json'))['semantic_records'],len(r['effects'])+8)

 def test_vehicle_damage_and_knockback_are_hurt_independent(self):
  for n in ('CorrodentAttackGoal','UnderzealotMeleeGoal'):
   b=body(n,'checkAndDealDamage');ks=[k for k,i in enumerate(b) if '.hurt(' in str(i['operand'])]
   self.assertEqual(len(ks),2);self.assertEqual([b[k+1]['opcode'] for k in ks],['0x57','0x57'])
   self.assertIn('.getVehicle(',str(b))

 def test_forsaken_blast_reads_primary_target_not_each_recipient(self):
  b=body('ForsakenAttackGoal','tick')
  ks=[k for k,i in enumerate(b) if '.getSonicDamageAgainst(' in str(i['operand'])]
  self.assertEqual(len(ks),2)
  for k in ks:self.assertEqual(b[k-1]['local_index'],1)
  self.assertIn('FORSAKEN_IGNORES',str(b))
  for k in [k for k,i in enumerate(b) if '.hurt(' in str(i['operand'])]:self.assertEqual(b[k+1]['opcode'],'0x57')

 def test_sonic_boom_admission_charges_before_native_parent_hurt(self):
  b=body('ForsakenEntity','hurt')
  c=next(k for k,i in enumerate(b) if '.setSonicCharge(' in str(i['operand']))
  self.assertEqual([(i['opcode'],i['operand']) for i in b[c+1:c+3]],[('0x3',0),('0xac',None)])
  self.assertIn('AbstractGolem',str(b));self.assertIn('Monster.hurt',str(b))

 def test_watcher_pre_damage_zero_preserves_bypass_and_causing_actor(self):
  b=body('CommonEvents','livingHurt','forlorn-context')
  for token in ('isPossessedByWatcher','BYPASSES_INVULNERABILITY','getEntity','WatcherEntity','setNewDamage'):self.assertIn(token,str(b))
  self.assertNotIn('.setCanceled(',str(b))
  self.assertNotIn('getDirectEntity',str(b))

 def test_watcher_camera_boolean_does_not_gate_server_attempt(self):
  self.assertNotIn('watcherPossession',str(body('WatcherEntity','attemptPossession')))
  self.assertIn('watcherPossessionCooldown',str(body('WatcherEntity','canPossessTargetEntity')))
  self.assertIn('watcherPossession',str(body('WatcherEntity','handleEntityEvent')))

 def test_ritual_cloud_event_is_not_an_area_damage_entity(self):
  b=body('UnderzealotEntity','handleEntityEvent')
  self.assertIn('VOID_BEING_CLOUD',str(b));self.assertIn('addParticle',str(b))
  self.assertNotIn('.addFreshEntity(',str(b));self.assertNotIn('.hurt(',str(b))
  b=body('VesperEntity','tick');self.assertIn('.convertTo(',str(b));self.assertIn('FORSAKEN',str(b))

 def test_light_breaking_has_no_added_grief_gate(self):
  b=body('UnderzealotBreakLightGoal','tick')
  self.assertIn('destroyBlock',str(b));self.assertNotIn('canEntityGrief',str(b))

 def test_unused_centering_add_does_not_write_velocity(self):
  b=body('UnderzealotEntity','tick')
  for k,i in enumerate(b):
   if 'Vec3.add(DDD)' in str(i['operand']):self.assertEqual(b[k+1]['opcode'],'0x57')

if __name__=='__main__':unittest.main()
