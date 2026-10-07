"""Independent native evidence protects Candy source and return distinctions."""
import copy
import unittest
from assemble_authored_contracts import render
from catalog_common import OUT,read_json
from promote_combat_batch import validate_batch


def body(name,method,scope):
 w=next(w for w in read_json(OUT/f'native-evidence/alexscaves-{scope}.json')['witnesses'] if w['entry'].endswith('/'+name+'.class'))
 return next(m for m in w['methods'] if m['name']==method)['instructions']


def after(b,token):
 k=next(k for k,i in enumerate(b) if token in str(i['operand']))
 return b[k+1]


class CandyContractsTests(unittest.TestCase):
 def test_native_bindings_and_regeneration(self):
  b=read_json(OUT/'alexscaves-r2m8m-candy-contracts.json')
  self.assertEqual(render(read_json(OUT/'native-findings/alexscaves-candy-contracts.json')),b)
  r=copy.deepcopy(read_json(OUT/'mod-reviews/alexscaves.json'));ids={e['id'] for e in b['effects']}
  r['effects']=[e for e in r['effects'] if e['id'] not in ids];r['paths']=[p for p in r['paths'] if not ids&set(p['effect_ids'])]
  self.assertEqual(validate_batch(b,r,read_json(OUT/'alexscaves-combat-census.json'))['semantic_records'],len(r['effects'])+16)

 def test_candicorn_charge_ignores_hurt_return(self):
  b=body('CandicornEntity','tick','candy-actors')
  self.assertEqual(after(b,'.hurt(')['opcode'],'0x57')
  self.assertIn('.knockback(',str(b))

 def test_candicorn_two_native_fall_hooks_and_requests(self):
  for m in ('causeFallDamage','causeInternalFallDamage'):
   b=body('CandicornEntity',m,'candy-actors')
   self.assertIn('onLivingFall',str(b));self.assertIn('.hurt(',str(b))
  self.assertIn('causeInternalFallDamage',str(body('CandicornEntity','causeFallDamage','candy-actors')))

 def test_gumball_splits_without_assigning_owner(self):
  b=body('GumballEntity','onHitEntity','candy-support')
  self.assertIn('addFreshEntity',str(b));self.assertNotIn('.setOwner(',str(b))
  self.assertEqual(after(b,'.hurt(')['opcode'],'0x57')
  self.assertIn('isFriendlyFire',str(b))

 def test_cube_puddle_does_not_get_creator_owner(self):
  b=body('CaramelCubeEntity','spawnMeltedCaramel','candy-actors')
  self.assertIn('MeltedCaramelEntity',str(b));self.assertIn('addFreshEntity',str(b))
  self.assertNotIn('.setOwner(',str(b))

 def test_hex_raw_owner_is_not_lazily_hydrated_by_tick(self):
  for m in ('tick','hurtEntities'):
   b=body('SugarStaffHexEntity',m,'candy-payloads')
   self.assertNotIn('.getOwner(',str(b))
  b=body('SugarStaffHexEntity','hurtEntities','candy-payloads')
  self.assertIn('.owner',str(b));self.assertEqual(after(b,'.hurt(')['opcode'],'0x57')

 def test_peppermint_overwrites_launch_radius_and_speed(self):
  b=body('SpinningPeppermintEntity','tick','candy-payloads')
  for token in ('.setSpinRadius(','.setSpinSpeed('):
   k=next(k for k,i in enumerate(b) if token in str(i['operand']))
   self.assertEqual(b[k-1]['operand'],3.0 if 'Radius' in token else 7.0)

 def test_worm_area_return_is_not_hurt_acceptance(self):
  b=body('GumWormEntity','attackAllAroundMouth','candy-actors')
  self.assertEqual(after(b,'.hurt(')['opcode'],'0x99')
  self.assertIn('.knockback(',str(b))
  # Return comes from a separate main-target membership flag/local.
  self.assertEqual(b[-1]['opcode'],'0xac')
  self.assertNotEqual(b[-2]['opcode'],'0xb6')

 def test_segment_forwards_source_but_returns_false(self):
  b=body('GumWormSegmentEntity','hurt','candy-actors')
  self.assertEqual(after(b,'.hurt(')['opcode'],'0x57')
  self.assertEqual([(i['opcode'],i['operand']) for i in b[-2:]], [('0x3',0),('0xac',None)])

if __name__=='__main__':unittest.main()
