"""Independent native actor/payload/return/liveness regressions for aquatic scope."""
import unittest
from catalog_common import OUT,read_json
from assemble_authored_contracts import render
from promote_combat_batch import validate_batch
from audit_numeric_labels import audit
P='com/github/alexthe666/alexsmobs/';F='native-evidence/alexsmobs-aquatic-large.json';G='native-evidence/alexsmobs-aquatic-owned.json'
def method(cls,name,file=F):
 w=next(w for w in read_json(OUT/file)['witnesses'] if w['entry']==P+cls+'.class');return next(m for m in w['methods'] if m['name']==name)
def calls(ins,part):return [i for i in ins if i['opcode'] in ('0xb6','0xb7','0xb8','0xb9') and part in str(i['operand'])]
class LargeAquaticContracts(unittest.TestCase):
 def test_authored_renderer_exact_consumers_and_numeric_labels(self):
  b=read_json(OUT/'alexsmobs-r2o4e-large-aquatic.json');self.assertEqual(render(read_json(OUT/'native-specifications/alexsmobs-large-aquatic-contracts.json')),b)
  r=read_json(OUT/'mod-reviews/alexsmobs.json');ids={x['id'] for x in b['effects']};r['effects']=[x for x in r['effects'] if x['id'] not in ids];r['paths']=[x for x in r['paths'] if not set(x['effect_ids'])&ids]
  validate_batch(b,r,read_json(OUT/'alexsmobs-combat-census.json'));self.assertEqual(audit(dict(effects=b['effects']))['unresolved_numeric_labels'],0)
 def test_squid_parent_hurt_runs_before_ink_conditions_and_false_return(self):
  i=method('entity/EntityGiantSquid','hurt')['instructions'];h=calls(i,'WaterAnimal.hurt(')[0];self.assertLess(h['offset'],calls(i,'.getLastHurtByMob(')[0]['offset']);self.assertLess(h['offset'],calls(i,'.nextBoolean(')[0]['offset']);self.assertEqual(i[-2]['operand'],0);self.assertEqual(i[-1]['opcode'],'0xac')
  i=method('entity/EntityGiantSquid','spawnInk')['instructions'];self.assertFalse(calls(i,'.addEffect('));self.assertTrue(calls(i,'.sendParticles('))
 def test_squid_absolute_hold_motion_is_independent_hurt(self):
  i=method('entity/EntityGiantSquid','tick')['instructions'];h=calls(i,'.hurt(')[0];self.assertEqual(i[i.index(h)+1]['opcode'],'0x57');self.assertTrue(calls(i,'Entity.setDeltaMovement('));self.assertFalse(calls(i,'.knockback('))
  i=method('entity/EntityGiantSquid','tickCaptured')['instructions'];h=calls(i,'.hurt(')[0];self.assertEqual(i[i.index(h)+1]['opcode'],'0x57');self.assertLess(h['offset'],calls(i,'.nextFloat(')[0]['offset'])
 def test_whale_squid_capture_return_not_damage_and_boat_discard_not_hurt_gated(self):
  i=method('entity/EntityCachalotWhale','aiStep')['instructions'];capture=calls(i,'.tickCaptured(')[0];self.assertEqual(i[i.index(capture)+1]['opcode'],'0x99')
  boat=calls(i,'Boat.hurt(')[0];self.assertEqual(i[i.index(boat)+1]['opcode'],'0x57');self.assertGreater(calls(i,'Boat.remove(')[0]['offset'],boat['offset']);self.assertEqual(next(x['operand'] for x in i if x['offset']==3118),1000.0)
  self.assertTrue(calls(i,'LivingEntity.setPos('));self.assertTrue(calls(i,'LivingEntity.setYRot('))
 def test_echo_is_charge_admission_without_damage(self):
  for n in ['tick','onEntityHit','onImpact','onHitBlock']:
   i=method('entity/EntityCachalotEcho',n,G)['instructions'];self.assertFalse(calls(i,'.hurt('));self.assertFalse(calls(i,'.addEffect('))
  i=method('entity/EntityCachalotEcho','onEntityHit',G)['instructions'];self.assertTrue(calls(i,'.recieveEcho('));self.assertTrue(calls(i,'.addFreshEntity('));self.assertTrue(calls(i,'.remove('))
  i=method('entity/EntityCachalotWhale','setTarget')['instructions'];self.assertTrue(any(x['opcode']=='0xb5' and '.receivedEchoZ' in str(x['operand']) for x in i))
 def test_straddler_unused_attack_clock_not_promoted(self):
  d=read_json(OUT/'alexsmobs-native-field-use-index.json');syms={n for n,x in enumerate(d['symbols']) if x==P+'entity/ai/StraddlerAIShoot.attackTimeI'};self.assertTrue(syms);self.assertFalse(any(s[1]==180 and s[2] in syms for m in d['methods'] for s in m['field_sites']))
  b=read_json(OUT/'alexsmobs-r2o4e-large-aquatic.json');r=next(r for r in b['effects'] if r['id']=='alexsmobs:straddler_stradpole_delivery');self.assertFalse(any('attack_cooldown' in x['parameters'] for x in r['scalable_parameter_candidates']))
 def test_stradpole_parent_damage_then_knockback_and_own_shield_target(self):
  i=method('entity/EntityStradpole','onEntityHit')['instructions'];self.assertTrue(calls(i,'.mobProjectile('));h=calls(i,'.hurt(')[0];self.assertEqual(i[i.index(h)+1]['opcode'],'0x57');self.assertLess(h['offset'],calls(i,'.knockback(')[0]['offset'])
  self.assertTrue(calls(i,'EntityStradpole.getTarget('));shield=calls(i,'.damageShieldFor(')[0];self.assertLess(calls(i,'EntityStradpole.getTarget(')[0]['offset'],shield['offset']);self.assertEqual(next(x['operand'] for x in i if x['offset']==62),3.0)
 def test_laviathan_bite_progress_live_damage_gate_and_shrink_independent(self):
  i=method('entity/EntityLaviathan','tick')['instructions'];h=calls(i,'.hurt(')[0];self.assertEqual(i[i.index(h)+1]['opcode'],'0x57');self.assertLess(h['offset'],calls(i,'.setShrink(')[0]['offset']);self.assertEqual(next(x['operand'] for x in i if x['offset']==1661),1000.0)
  self.assertTrue(any(x['opcode']=='0xb4' and '.biteProgressF' in str(x['operand']) and x['offset']<h['offset'] for x in i));self.assertTrue(calls(i,'.setLuringLaviathan('))
 def test_private_part_sizes_are_not_runtime_dimension_inputs(self):
  d=read_json(OUT/'alexsmobs-native-field-use-index.json');r=read_json(OUT/G)
  for cls in ['EntityGiantSquidPart','EntityCachalotPart','EntityLaviathanPart']:
   w=next(w for w in r['witnesses'] if w['entry'].endswith('/'+cls+'.class'));self.assertNotIn('getDimensions',{m['name'] for m in w['methods']});ids={n for n,x in enumerate(d['symbols']) if '/'+cls+'.sizeL' in x};self.assertTrue(ids);self.assertFalse(any(s[1]==180 and s[2] in ids for m in d['methods'] for s in m['field_sites']))
  ref=read_json(OUT/'reference-evidence/alexsmobs-multipart-parent.json')['witnesses'][0];self.assertNotIn('getDimensions',{m['name'] for m in ref['declared_methods']});self.assertTrue(calls(ref['methods'][0]['instructions'],'Entity.getType('))
  v=read_json(OUT/'vanilla-evidence/alexsmobs-multipart-dimensions.json');i=next(m for m in v['classes'][0]['methods'] if m['name']=='getDimensions')['instructions'];self.assertTrue(calls(i,'EntityType.getDimensions('))
 def test_native_griefing_and_shared_herd_revenge_not_damage(self):
  for c in ['EntityCachalotWhale','EntityLaviathan']:
   i=method('entity/'+c,'breakBlock')['instructions'];self.assertTrue(calls(i,'EventHooks.canEntityGrief('));self.assertTrue(calls(i,'.destroyBlock('));self.assertFalse(calls(i,'.hurt('))
  i=method('entity/ai/AnimalAIHerdPanic','canUse')['instructions'];self.assertTrue(calls(i,'.setLastHurtByMob('));self.assertFalse(calls(i,'.hurt('));self.assertFalse(calls(i,'.addEffect('))
if __name__=='__main__':unittest.main()
