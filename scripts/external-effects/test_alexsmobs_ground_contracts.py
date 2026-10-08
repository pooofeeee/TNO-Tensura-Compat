"""Independent pinned consumer/order/admission regressions for terrestrial batch."""
import unittest
from catalog_common import OUT,read_json
from assemble_authored_contracts import render
from promote_combat_batch import validate_batch
from audit_numeric_labels import audit
P='com/github/alexthe666/alexsmobs/'
F='native-evidence/alexsmobs-ground-herds.json';D='native-evidence/alexsmobs-foundation.json'
def method(cls,name,file=F):
 w=next(w for w in read_json(OUT/file)['witnesses'] if w['entry']==P+cls+'.class');return next(m for m in w['methods'] if m['name']==name)
def calls(ins,part):return [i for i in ins if i['opcode'] in ('0xb6','0xb7','0xb8','0xb9') and part in str(i['operand'])]
class GroundContracts(unittest.TestCase):
 def test_renderer_exact_consumers_numeric_audit(self):
  b=read_json(OUT/'alexsmobs-r2o5a-ground-herds.json');self.assertEqual(render(read_json(OUT/'native-specifications/alexsmobs-ground-contracts.json')),b)
  r=read_json(OUT/'mod-reviews/alexsmobs.json');ids={x['id'] for x in b['effects']};r['effects']=[x for x in r['effects'] if x['id'] not in ids];r['paths']=[x for x in r['paths'] if not set(x['effect_ids'])&ids]
  validate_batch(b,r,read_json(OUT/'alexsmobs-combat-census.json'));self.assertEqual(audit(dict(effects=b['effects']))['unresolved_numeric_labels'],0)
 def test_delayed_attack_admission_returns_without_damage(self):
  for c in ['EntityRoadrunner','EntityEmu','EntityMoose','EntityBison']:
   i=method('entity/'+c,'doHurtTarget')['instructions'];self.assertFalse(calls(i,'.hurt('));self.assertTrue(any(x['opcode']=='0xac' for x in i))
  i=method('entity/EntityRoadrunner','aiStep')['instructions'];h=calls(i,'.hurt(')[0];self.assertEqual(i[i.index(h)+1]['opcode'],'0x57');self.assertEqual(next(x['operand'] for x in i if x['offset']==299),2.0)
 def test_gazelle_has_no_damage_attack_and_herd_requires_accepted_hurt(self):
  i=method('entity/EntityGazelle','hurt')['instructions'];h=calls(i,'Animal.hurt(')[0];self.assertEqual(i[i.index(h)+3]['opcode'],'0x99');self.assertTrue(calls(i,'.getEntitiesOfClass('))
  i=method('entity/EntityGazelle','tick')['instructions'];self.assertFalse(calls(i,'.hurt('));self.assertTrue(calls(i,'.setBaseValue('))
 def test_emu_and_moose_knockback_precedes_ignored_damage(self):
  for c in ['EntityEmu','EntityMoose']:
   i=method('entity/'+c,'tick')['instructions'];h=calls(i,'.hurt(')[0];self.assertLess(calls(i,'.knockback(')[0]['offset'],h['offset']);self.assertEqual(i[i.index(h)+1]['opcode'],'0x57')
 def test_emu_old_reach_method_not_current_goal_hook(self):
  d=read_json(OUT/'vanilla-evidence/alexsmobs-predator-native-dispatch.json');c=next(c for c in d['classes'] if 'MeleeAttackGoal' in str(c));names={m['name'] for m in c['declared_methods']};self.assertNotIn('getAttackReachSqr',names)
  self.assertFalse(any('getAttackReachSqr' in str(i['operand']) for m in c['methods'] for i in m['instructions']))
 def test_emu_projectile_cancel_native_hook_and_selfmotion(self):
  i=method('event/ServerEvents','onProjectileHit',D)['instructions'];self.assertEqual(len(calls(i,'.setCanceled(')),2);self.assertTrue(calls(i,'.move('));self.assertTrue(calls(i,'.setDeltaMovement('));self.assertFalse(calls(i,'.hurt('))
  d=read_json(OUT/'reference-evidence/alexsmobs-emu-projectile-impact.json');w=next(w for w in d['witnesses'] if w['entry'].endswith('/EventHooks.class'));i=w['methods'][0]['instructions'];self.assertTrue(calls(i,'.post('));self.assertTrue(calls(i,'.isCanceled('))
  p=next(w for w in d['witnesses'] if w['entry'].endswith('AbstractArrow.java.patch'));text=p['text_sections'][0]['text'];self.assertLess(text.index('onProjectileImpact'),text.index('hitTargetOrDeflectSelf'));self.assertIn('break;',text)
 def test_bison_launch_uses_attacker_delta_and_precedes_hurt(self):
  i=method('entity/EntityBison','launch')['instructions'];self.assertTrue(calls(i,'EntityBison.getDeltaMovement('));self.assertTrue(calls(i,'Entity.setDeltaMovement('));self.assertFalse(calls(i,'.knockback('));self.assertTrue(calls(i,'.getAttributeValue('))
  i=method('entity/EntityBison','tick')['instructions'];h=calls(i,'.hurt(')[0];self.assertLess(calls(i,'.launch(')[0]['offset'],h['offset']);self.assertEqual(i[i.index(h)+1]['opcode'],'0x57')
 def test_sparring_native_event_cancel_and_absolute_y(self):
  for c,n in [('EntityMoose','applyKnockbackFromMoose'),('EntityBison','applyKnockbackFromBuffalo')]:
   i=method('entity/'+c,n)['instructions'];self.assertTrue(calls(i,'.onLivingKnockBack('));self.assertTrue(calls(i,'.isCanceled('));self.assertTrue(calls(i,'.getStrength('));self.assertFalse(calls(i,'.hurt('));self.assertTrue(any(x['operand']==.30000001192092896 for x in i))
 def test_private_bison_helper_no_native_call_or_bootstrap(self):
  d=read_json(OUT/'alexsmobs-combat-census.json');name=P+'entity/EntityBison.knockbackTarget';syms={n for n,x in enumerate(d['symbols']) if x.startswith(name)};self.assertFalse(any(s[2] in syms for m in d['methods'] for s in m['calls']));self.assertFalse(any(name in str(x) for x in d['registration_bootstraps']))
 def test_jerboa_exact_holder_duration_default_amp_and_hurt_removal(self):
  i=method('entity/EntityJerboa','mobInteract')['instructions'];ctor=next(x for x in i if x['offset']==352);self.assertEqual(ctor['operand'],'net/minecraft/world/effect/MobEffectInstance.<init>(Lnet/minecraft/core/Holder;I)V');self.assertEqual(next(x['operand'] for x in i if x['offset']==349),12000)
  self.assertFalse(calls([x for x in i if x['offset']>=331],'.shrink('));self.assertTrue(calls(i,'.heal('));self.assertIn('FLEET_FOOTED',str(next(x['operand'] for x in i if x['offset']==343)))
  i=method('entity/EntityJerboa','hurt')['instructions'];h=calls(i,'Animal.hurt(')[0];self.assertLess(h['offset'],calls(i,'.removeEffect(')[0]['offset'])
if __name__=='__main__':unittest.main()
