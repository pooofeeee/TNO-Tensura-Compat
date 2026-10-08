"""Exact native upgrade alias, effect ordering, lifecycle and source distinctions."""
import unittest
from catalog_common import OUT, read_json
from assemble_authored_contracts import render
from promote_combat_batch import validate_batch
from audit_numeric_labels import audit
P='com/github/alexthe666/alexsmobs/';F='native-evidence/alexsmobs-mimic-octopus.json'
def method(cls,name,file=F):
 w=next(w for w in read_json(OUT/file)['witnesses'] if w['entry']==P+cls+'.class')
 return next(m for m in w['methods'] if m['name']==name)
def calls(ins,part):return [i for i in ins if i['opcode'] in ('0xb6','0xb7','0xb8','0xb9') and part in str(i['operand'])]
class MimicContracts(unittest.TestCase):
 def test_authored_renderer_and_exact_pinned_consumers(self):
  b=read_json(OUT/'alexsmobs-r2o4d-mimic-octopus.json');self.assertEqual(b,render(read_json(OUT/'native-specifications/alexsmobs-mimic-contracts.json')))
  r=read_json(OUT/'mod-reviews/alexsmobs.json');ids={x['id'] for x in b['effects']};r['effects']=[x for x in r['effects'] if x['id'] not in ids];r['paths']=[x for x in r['paths'] if not set(x['effect_ids'])&ids]
  validate_batch(b,r,read_json(OUT/'alexsmobs-combat-census.json'));a=audit(dict(effects=b['effects']));self.assertEqual(a['unresolved_numeric_labels'],0)
 def test_upgrade_accessor_is_bucket_not_unused_upgrade(self):
  for n in ['isUpgraded','setUpgraded','fromBucket','setFromBucket']:
   i=method('entity/EntityMimicOctopus',n)['instructions'];s=[x['operand'] for x in i if x['opcode']=='0xb2'];self.assertEqual(s,[P+'entity/EntityMimicOctopus.FROM_BUCKETLnet/minecraft/network/syncher/EntityDataAccessor;'])
  i=method('entity/EntityMimicOctopus','readAdditionalSaveData')['instructions'];self.assertLess(calls(i,'.setUpgraded(')[0]['offset'],calls(i,'.setFromBucket(')[0]['offset'])
 def test_puffer_poison_independent_and_asymmetric_geometry(self):
  i=method('entity/EntityMimicOctopus$AIAttack','tick')['instructions'];h=calls(i,'.hurt(')[0];n=i.index(h);self.assertEqual(i[n+1]['opcode'],'0x57');self.assertGreater(calls(i,'.addEffect(')[0]['offset'],h['offset'])
  self.assertEqual(next(x['operand'] for x in i if x['offset']==597),400);self.assertEqual(next(x['operand'] for x in i if x['offset']==600),2)
  self.assertEqual(len(calls(i,'AABB.expandTowards(')),2);self.assertFalse(calls(i,'AABB.inflate('))
 def test_victim_control_is_mob_navigation_and_aggro_not_fear_effect(self):
  i=method('entity/EntityMimicOctopus$AIAttack','tick')['instructions'];control=[x for x in i if x['offset']<220];self.assertTrue(calls(control,'Mob.setTarget('));self.assertTrue(calls(control,'MoveControl.setWantedPosition('));self.assertFalse(calls(control,'.hurt('));self.assertFalse(calls(control,'.addEffect('))
 def test_beam_native_actor_and_current_server_target(self):
  i=method('entity/EntityMimicOctopus','getGuardianLaser')['instructions'];self.assertTrue(calls(i,'.getTarget('));self.assertTrue(calls(i,'.getEntity('))
  i=method('entity/EntityMimicOctopus','hasGuardianLaser')['instructions'];self.assertTrue(calls(i,'.isUpgraded('));self.assertFalse(calls(i,'.getMimicState('))
  i=method('entity/EntityMimicOctopus','tick')['instructions'];self.assertTrue(calls(i,'.mobAttack('));self.assertFalse(calls(i,'.indirectMagic('));self.assertEqual(next(x['operand'] for x in i if x['offset']==1165),5.0)
 def test_explosion_and_client_callback_are_real_native_calls(self):
  i=method('entity/EntityMimicOctopus','creeperExplode')['instructions'];self.assertTrue(calls(i,'Level.explode('));self.assertTrue(any('ExplosionInteraction.NONE' in str(x['operand']) for x in i));self.assertFalse(calls(i,'.discard('))
  self.assertTrue(calls(method('entity/EntityMimicOctopus','handleEntityEvent')['instructions'],'.creeperExplode('))
  v=read_json(OUT/'vanilla-evidence/alexsmobs-mimic-native-dispatch.json');cl=next(w for w in v['classes'] if w['class_name'].endswith('ClientLevel'));self.assertFalse(any(x['name']=='explode' for x in cl['declared_methods']))
  level=next(w for w in v['classes'] if w['class_name'].endswith('/Level'));self.assertTrue(any(calls(m['instructions'],'Explosion.explode()V') for m in level['methods']))
  p=read_json(OUT/'reference-evidence/alexsmobs-mimic-native-loader.json');self.assertIn('onExplosionStart',p['witnesses'][0]['text_sections'][0]['text'])
 def test_default_continuation_rechecks_and_stop_overwrites_cooldown(self):
  v=read_json(OUT/'vanilla-evidence/alexsmobs-mimic-native-dispatch.json');g=next(w for w in v['classes'] if w['class_name'].endswith('/Goal'));self.assertTrue(calls(g['methods'][0]['instructions'],'.canUse()Z'))
  w=next(w for w in read_json(OUT/F)['witnesses'] if w['entry'].endswith('$AIAttack.class'));self.assertNotIn('canContinueToUse',{m['name'] for m in w['methods']})
  i=method('entity/EntityMimicOctopus$AIAttack','stop')['instructions'];self.assertEqual(next(x['operand'] for x in i if x['offset']==43),30)
 def test_owner_pre_zero_after_soulsteal_and_before_thorns(self):
  i=method('event/ServerEvents','onLivingDamageEvent','native-evidence/alexsmobs-foundation.json')['instructions'];o=calls(i,'MimicOctopus.isOwnedBy(')[0]['offset'];self.assertLess(calls(i,'.heal(')[0]['offset'],o);at=next(n for n,x in enumerate(i) if x['offset']==155);self.assertIn('Pre.setNewDamage',i[at]['operand']);self.assertEqual(i[at-1]['operand'],0.0);self.assertEqual(i[at+1]['opcode'],'0xb1');self.assertLess(o,calls(i,'.thorns(')[0]['offset'])
 def test_sit_and_old_air_are_not_invented_current_parent_hooks(self):
  i=method('entity/EntityMimicOctopus','setOrderedToSit')['instructions'];self.assertTrue(calls(i,'SynchedEntityData.set('));self.assertFalse(calls(i,'TamableAnimal.setOrderedToSit'))
  d=read_json(OUT/'alexsmobs-combat-census.json');s=P+'entity/EntityMimicOctopus.updateAir(I)V';ids={n for n,x in enumerate(d['symbols']) if x==s};self.assertFalse(any(c[2] in ids for m in d['methods'] for c in m['calls']))
if __name__=='__main__':unittest.main()
