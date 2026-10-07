"""Abyssal contracts preserve native damage returns, raw ownership and NBT."""
import copy
import unittest
from assemble_authored_contracts import render
from catalog_common import OUT,read_json
from promote_combat_batch import validate_batch


def native(name,method,scope='abyssal-actors',with_token=None):
 w=next(w for w in read_json(OUT/f'native-evidence/alexscaves-{scope}.json')['witnesses'] if w['entry'].endswith('/'+name+'.class'))
 return next(m for m in w['methods'] if m['name']==method and (with_token is None or with_token in str(m['instructions'])))['instructions']


class AbyssalContractsTests(unittest.TestCase):
 def test_regeneration_and_pinned_candidates(self):
  b=read_json(OUT/'alexscaves-r2m8n-abyssal-contracts.json')
  self.assertEqual(render(read_json(OUT/'native-findings/alexscaves-abyssal-contracts.json')),b)
  r=copy.deepcopy(read_json(OUT/'mod-reviews/alexscaves.json'));ids={e['id'] for e in b['effects']}
  r['effects']=[e for e in r['effects'] if e['id'] not in ids];r['paths']=[p for p in r['paths'] if not ids&set(p['effect_ids'])]
  self.assertEqual(validate_batch(b,r,read_json(OUT/'alexscaves-combat-census.json'))['semantic_records'],len(r['effects'])+8)

 def test_melee_vehicle_requests_are_distinct_and_independent(self):
  for n,m in [('DeepOneBaseEntity','checkAndDealMeleeDamage'),('HullbreakerMeleeGoal','checkAndDealDamage')]:
   b=native(n,m,with_token='.hurt(')
   ks=[k for k,i in enumerate(b) if '.hurt(' in str(i['operand'])]
   self.assertEqual(len(ks),2)
   self.assertEqual([b[k+1]['opcode'] for k in ks],['0x57','0x57'])
   self.assertIn('.getVehicle(',str(b));self.assertIn('.setDeltaMovement(',str(b))

 def test_hullbreaker_part_does_not_forward_native_hurt(self):
  b=native('HullbreakerPartEntity','hurt')
  self.assertNotIn('.hurt(',str(b));self.assertIn('MultipartEntityMessage',str(b))
  self.assertIn('isClientSide',str(b));self.assertEqual(b[-1]['opcode'],'0xac')
  self.assertEqual(b[-2]['operand'],0)

 def test_wave_tick_does_not_hydrate_raw_owner(self):
  for m in ('tick','attackEntities'):
   self.assertNotIn('.getOwner(',str(native('WaveEntity',m,'abyssal-payloads')))
  b=native('WaveEntity','attackEntities','abyssal-payloads')
  k=next(k for k,i in enumerate(b) if '.hurt(' in str(i['operand']))
  self.assertEqual(b[k+1]['opcode'],'0x57');self.assertIn('.owner',str(b))

 def test_ink_cloud_owner_is_not_invented(self):
  b=native('InkBombEntity','onHit','abyssal-payloads')
  self.assertIn('AreaEffectCloud',str(b));self.assertIn('addFreshEntity',str(b))
  self.assertNotIn('.setOwner(',str(b))
  b=native('InkBombEntity','onHitEntity','abyssal-payloads')
  k=next(k for k,i in enumerate(b) if '.hurt(' in str(i['operand']))
  self.assertEqual(b[k+1]['opcode'],'0x57');self.assertIn('BLINDNESS',str(b))

 def test_bolt_status_requires_accepted_hurt(self):
  b=native('WaterBoltEntity','damageMobs','abyssal-payloads')
  k=next(k for k,i in enumerate(b) if '.hurt(' in str(i['operand']))
  self.assertEqual(b[k+1]['opcode'],'0x99');self.assertIn('BUBBLED',str(b))

 def test_bolt_nbt_override_does_not_call_parent(self):
  for m in ('readAdditionalSaveData','addAdditionalSaveData'):
   b=native('WaterBoltEntity',m,'abyssal-payloads')
   self.assertNotIn('Projectile.'+m,str(b));self.assertIn('Bubbling',str(b))

 def test_swapped_item_save_load_keys_differ_natively(self):
  self.assertIn('SwappedItem',str(native('DeepOneBaseEntity','addAdditionalSaveData')))
  self.assertNotIn('SwappedItem',str(native('DeepOneBaseEntity','readAdditionalSaveData')))
  self.assertIn('SwappedWeapon',str(native('DeepOneBaseEntity','readAdditionalSaveData')))

if __name__=='__main__':unittest.main()
