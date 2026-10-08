"""Pinned native ordering/source/clock/lifecycle checks for reptile review."""
import unittest
from catalog_common import OUT,read_json
from assemble_authored_contracts import render
from promote_combat_batch import validate_batch
from audit_numeric_labels import audit
P='com/github/alexthe666/alexsmobs/'
F='native-evidence/alexsmobs-reptile-predators.json';G='native-evidence/alexsmobs-reptile-goals.json'
def method(cls,name,file=F):
 w=next(w for w in read_json(OUT/file)['witnesses'] if w['entry']==P+cls+'.class');return next(m for m in w['methods'] if m['name']==name)
def calls(ins,part):return [i for i in ins if i['opcode'] in ('0xb6','0xb7','0xb8','0xb9') and part in str(i['operand'])]
class ReptileContracts(unittest.TestCase):
 def test_renderer_exact_consumers_and_labels(self):
  b=read_json(OUT/'alexsmobs-r2o5b-reptile-predators.json');self.assertEqual(render(read_json(OUT/'native-specifications/alexsmobs-reptile-contracts.json')),b)
  r=read_json(OUT/'mod-reviews/alexsmobs.json');ids={x['id'] for x in b['effects']};r['effects']=[x for x in r['effects'] if x['id'] not in ids];r['paths']=[x for x in r['paths'] if not set(x['effect_ids'])&ids]
  validate_batch(b,r,read_json(OUT/'alexsmobs-combat-census.json'));self.assertEqual(audit(dict(effects=b['effects']))['unresolved_numeric_labels'],0)
 def test_snapping_turtle_damage_uses_progress_equality_not_start_return(self):
  i=method('entity/EntityAlligatorSnappingTurtle','doHurtTarget')['instructions'];self.assertFalse(calls(i,'.hurt('))
  i=method('entity/EntityAlligatorSnappingTurtle','tick')['instructions'];self.assertEqual(next(x['operand'] for x in i if x['offset']==171),4.0);self.assertTrue(any(x['opcode']=='0xb4' and '.attackProgressF' in str(x['operand']) and x['offset']<171 for x in i));h=calls(i,'.hurt(')[0];self.assertEqual(i[i.index(h)+1]['opcode'],'0x57')
 def test_rattlesnake_poison_independent_of_damage_return(self):
  i=method('entity/EntityRattlesnake','tick')['instructions'];h=calls(i,'.hurt(')[0];self.assertEqual(i[i.index(h)+1]['opcode'],'0x57');self.assertLess(h['offset'],calls(i,'.addEffect(')[0]['offset']);self.assertEqual(next(x['operand'] for x in i if x['offset']==416),300)
 def test_komodo_parent_return_required_before_poison(self):
  i=method('entity/EntityKomodoDragon','doHurtTarget')['instructions'];h=calls(i,'TamableAnimal.doHurtTarget(')[0];self.assertEqual(i[i.index(h)+1]['opcode'],'0x99');self.assertLess(h['offset'],calls(i,'.addEffect(')[0]['offset']);self.assertEqual(next(x['operand'] for x in i if x['offset']==64),20)
 def test_caiman_source_switch_and_motion_independent(self):
  i=method('entity/ai/CaimanAIMelee','tick',G)['instructions'];self.assertTrue(calls(i,'.drown('));self.assertTrue(calls(i,'.mobAttack('));h=calls(i,'.hurt(')[0];self.assertEqual(i[i.index(h)+1]['opcode'],'0x57');self.assertLess(h['offset'],calls(i,'.setDeltaMovement(')[0]['offset']);self.assertFalse(calls(i,'.knockback('));self.assertFalse(calls(i,'.startRiding('))
 def test_caiman_and_crocodile_custom_sit_not_parent_flag(self):
  for cls in ['EntityCaiman','EntityCrocodile']:
   i=method('entity/'+cls,'setOrderedToSit')['instructions'];self.assertTrue(calls(i,'SynchedEntityData.set('));self.assertFalse(calls(i,'TamableAnimal.setOrderedToSit('))
 def test_crocodile_capture_before_hurt_and_passenger_separate(self):
  i=method('entity/EntityCrocodile','tick')['instructions'];h=calls(i,'.hurt(')[0];self.assertLess(calls(i,'.startRiding(')[0]['offset'],h['offset']);self.assertEqual(i[i.index(h)+1]['opcode'],'0x57');self.assertEqual(len(calls(i,'.hurt(')),2)
  i=method('entity/EntityCrocodile','positionRider')['instructions'];h=calls(i,'.hurt(')[0];self.assertLess(calls(i,'.setPos(')[0]['offset'],h['offset']);self.assertEqual(next(x['operand'] for x in i if x['offset']==125),40);self.assertEqual(next(x['operand'] for x in i if x['offset']==140),2.0)
 def test_crocodile_old_reach_signature_not_current_hook(self):
  m=method('entity/ai/CrocodileAIMelee','checkAndPerformAttack',G);self.assertEqual(m['descriptor'],'(Lnet/minecraft/world/entity/LivingEntity;D)V')
  d=read_json(OUT/'vanilla-evidence/alexsmobs-predator-native-dispatch.json');c=next(c for c in d['classes'] if 'MeleeAttackGoal' in str(c));dcl=next(x for x in c['declared_methods'] if x['name']=='checkAndPerformAttack');self.assertNotIn(';D)',str(dcl));self.assertFalse(any('checkAndPerformAttack' in str(x['operand']) and ';D)' in str(x['operand']) for m in c['methods'] for x in m['instructions']))
 def test_anaconda_capture_after_ignored_hurt_and_stop_does_not_reset_clock(self):
  i=method('entity/EntityAnaconda$AIMelee','tick')['instructions'];h=calls(i,'.hurt(')[0];self.assertEqual(i[i.index(h)+1]['opcode'],'0x57');self.assertLess(h['offset'],calls(i,'.setStrangling(')[0]['offset'])
  i=method('entity/EntityAnaconda$AIMelee','stop')['instructions'];self.assertTrue(calls(i,'.setStrangling('));self.assertFalse(any('.strangleTimerI' in str(x['operand']) for x in i))
  i=method('entity/EntityAnaconda','tick')['instructions'];self.assertTrue(calls(i,'.getMaxHealth('));self.assertTrue(calls(i,'.setDeltaMovement('));self.assertEqual(next(x['operand'] for x in i if x['offset']==374),.25)
 def test_anaconda_real_heal_consumer_follows_part_chain(self):
  i=method('entity/EntityAnacondaPart','feedAnaconda')['instructions'];self.assertTrue(calls(i,'.getParent('));self.assertTrue(calls(i,'.feed('));i=method('entity/EntityAnaconda','feed')['instructions'];self.assertTrue(calls(i,'.heal('));self.assertEqual(i[1]['operand'],10.0)
 def test_segment_damage_forwarding_is_distinct_from_visual_message(self):
  i=method('entity/EntityAnacondaPart','hurt')['instructions'];self.assertTrue(calls(i,'.hurtHeadId('));self.assertFalse(calls(i,'.sendMSGToAll('));i=method('entity/EntityAnacondaPart','hurtHeadId')['instructions'];self.assertTrue(calls(i,'.getEntity('));self.assertEqual(len(calls(i,'.hurt(')),1)
  i=method('entity/EntityBoneSerpentPart','hurt')['instructions'];self.assertTrue(calls(i,'.getParent('));self.assertEqual(len(calls(i,'.hurt(')),1);self.assertTrue(any(x['opcode']=='0xb4' and '.damageMultiplierF' in str(x['operand']) for x in i));self.assertTrue(calls(i,'.sendMSGToAll('))
 def test_bone_native_melee_output_distinct_from_self_jump(self):
  i=method('entity/ai/BoneSerpentAIMeleeJump','tick',G)['instructions'];self.assertTrue(calls(i,'.doHurtTarget('));self.assertEqual(next(x['operand'] for x in i if x['offset']==139),20)
  i=method('entity/ai/BoneSerpentAIMeleeJump','start',G)['instructions'];self.assertTrue(calls(i,'.setDeltaMovement('));self.assertFalse(calls(i,'.hurt('));self.assertFalse(calls(i,'.addEffect('))
if __name__=='__main__':unittest.main()
