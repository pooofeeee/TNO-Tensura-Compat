"""Independent pinned source-order, receiver and original native consumer checks."""
import unittest
from catalog_common import OUT,read_json
from assemble_authored_contracts import render
from promote_combat_batch import validate_batch
from audit_numeric_labels import audit
P='com/github/alexthe666/alexsmobs/'
F='native-evidence/alexsmobs-aquatic-predators.json'
def method(cls,name,file=F):
 w=next(w for w in read_json(OUT/file)['witnesses'] if w['entry']==P+cls+'.class')
 return next(m for m in w['methods'] if m['name']==name)
def calls(ins,part):return [i for i in ins if i['opcode'] in ('0xb6','0xb7','0xb8','0xb9') and part in str(i['operand'])]
class PredatorContracts(unittest.TestCase):
 def test_render_and_native_bindings(self):
  b=read_json(OUT/'alexsmobs-r2o4b-aquatic-predators.json');self.assertEqual(render(read_json(OUT/'native-specifications/alexsmobs-predator-contracts.json')),b)
  r=read_json(OUT/'mod-reviews/alexsmobs.json');ids={v['id'] for v in b['effects']};r['effects']=[v for v in r['effects'] if v['id'] not in ids];r['paths']=[v for v in r['paths'] if not set(v['effect_ids'])&ids]
  validate_batch(b,r,read_json(OUT/'alexsmobs-combat-census.json'));self.assertEqual(audit(dict(effects=b['effects']))['native_candidate_identities'],45)
 def test_frilled_status_is_gated_by_native_hurt_success(self):
  ins=method('entity/EntityFrilledShark','tick')['instructions'];at=ins.index(calls(ins,'.hurt(')[0]);branch=ins[at+1]
  self.assertEqual(branch['opcode'],'0x99');status=calls(ins,'MobEffectInstance.<init>')[0]['offset'];self.assertGreater(status,ins[at]['offset']);self.assertGreater(branch['branch_target'],calls(ins,'.addEffect(')[0]['offset'])
  self.assertTrue(calls(ins,'AttributeInstance.getBaseValue'));self.assertFalse(calls(ins,'.getAttributeValue('))
  ins=method('entity/EntityFrilledShark$AIMelee','tick')['instructions'];self.assertTrue(calls(ins,'Squid.setMovementVector'));self.assertFalse(calls(ins,'.hurt('));self.assertFalse(calls(ins,'.knockback('))
 def test_orca_tail_control_runs_after_discarded_damage_result(self):
  ins=method('entity/EntityOrca','tick')['instructions'];hits=calls(ins,'LivingEntity.hurt(');self.assertEqual(len(hits),2)
  knock=calls(ins,'.knockback(')[0]['offset'];self.assertGreater(knock,hits[-1]['offset']);self.assertTrue(any(i['opcode']=='0xb2' and 'Attributes.KNOCKBACK_RESISTANCE' in str(i['operand']) for i in ins if i['offset']>knock))
  at=next(n for n,i in enumerate(ins) if 'Attributes.KNOCKBACK_RESISTANCE' in str(i['operand']));self.assertEqual(ins[at-1]['opcode'],'0x2a')
  self.assertEqual(sum(i['opcode']=='0x8e' for i in ins),2) # native D2I amount truncations
  jump=method('entity/EntityOrca','onJumpHit')['instructions'];self.assertFalse(any(i['opcode']=='0xc' and i['operand']==2 for i in jump));self.assertFalse(calls(jump,'.knockback('))
 def test_orca_might_two_argument_constructor_has_native_zero_amplifier(self):
  doc=read_json(OUT/'vanilla-evidence/alexsmobs-predator-native-dispatch.json');w=next(w for w in doc['classes'] if w['class_name'].endswith('/MobEffectInstance'))
  m=next(m for m in w['methods'] if m['obfuscated_descriptor'].endswith(';I)V'));self.assertEqual(m['instructions'][-3]['operand'],0);self.assertTrue(str(m['instructions'][-2]['operand']).endswith(';II)V'))
  ins=method('entity/EntityOrca$SwimWithPlayerGoal','tick')['instructions'];self.assertTrue(calls(ins,'Player.addEffect('));self.assertFalse(calls(ins,'.hurt('));self.assertEqual(next(i['operand'] for i in ins if i['offset']==124),1000)
 def test_skelewag_knockback_precedes_stab_and_slash_is_distinct(self):
  ins=method('entity/EntitySkelewag','tick')['instructions'];hits=calls(ins,'.hurt(');self.assertEqual(len(hits),2);self.assertLess(calls(ins,'.knockback(')[0]['offset'],hits[0]['offset'])
  self.assertTrue(calls(ins,'.isPassengerOfSameVehicle('));self.assertEqual(len(calls(ins,'.isAlliedTo(')),1);self.assertEqual(next(i['operand'] for i in ins if i['offset']==490),.5)
  for hit in hits:self.assertEqual(ins[ins.index(hit)+1]['opcode'],'0x57')
 def test_hammerhead_goal_uses_original_parent_attack_without_status(self):
  ins=method('entity/EntityHammerheadShark$CirclePreyGoal','tick')['instructions'];self.assertTrue(calls(ins,'.doHurtTarget('));self.assertFalse(calls(ins,'.addEffect('));self.assertFalse(calls(ins,'.knockback('))
  a=method('entity/EntityHammerheadShark$CirclePreyGoal','start')['instructions'];b=method('entity/EntityHammerheadShark$CirclePreyGoal','stop')['instructions'];self.assertEqual([(i['offset'],i['opcode'],i['operand'] if type(i['operand']) in (int,float) else None) for i in a],[(i['offset'],i['opcode'],i['operand'] if type(i['operand']) in (int,float) else None) for i in b])
  for x,y in [('access$000','access$300'),('access$100','access$400'),('access$200','access$500')]:self.assertEqual(method('entity/EntityHammerheadShark',x)['instructions'],method('entity/EntityHammerheadShark',y)['instructions'])
 def test_old_breathing_and_block_trace_helpers_have_no_native_callers(self):
  c=read_json(OUT/'alexsmobs-combat-census.json');needle=P+'entity/EntityHammerheadShark.isTargetBlocked(Lnet/minecraft/world/phys/Vec3;)Z'
  self.assertFalse(any(needle in str(m['calls']) or '.canBreatheUnderwaterAM()Z' in str(m['calls']) for m in c['methods']))
  self.assertFalse(any(needle in str(r) or '.canBreatheUnderwaterAM()Z' in str(r) for r in c['registration_bootstraps']))
 def test_orca_terrain_has_tag_and_server_but_no_mob_griefing_check(self):
  ins=method('entity/EntityOrca','breakBlock')['instructions'];self.assertTrue(any('AMTagRegistry.ORCA_BREAKABLES' in str(i['operand']) for i in ins));self.assertTrue(calls(ins,'.destroyBlock('));self.assertTrue(calls(ins,'.setBlockAndUpdate('));self.assertFalse(any('MOBGRIEFING' in str(i['operand']) or 'canEntityGrief' in str(i['operand']) for i in ins))
if __name__=='__main__':unittest.main()
