"""Native selector liveness, stored source, control ordering and owner state."""
import unittest
from catalog_common import OUT,read_json
from assemble_authored_contracts import render
from promote_combat_batch import validate_batch
from audit_numeric_labels import audit
P='com/github/alexthe666/alexsmobs/';F='native-evidence/alexsmobs-aquatic-interactions.json'
def method(cls,name):
 w=next(w for w in read_json(OUT/F)['witnesses'] if w['entry']==P+cls+'.class');return next(m for m in w['methods'] if m['name']==name)
def calls(ins,part):return [i for i in ins if i['opcode'] in ('0xb6','0xb7','0xb8','0xb9') and part in str(i['operand'])]
class AquaticInteractionContracts(unittest.TestCase):
 def test_renderer_and_all_pinned_candidates(self):
  b=read_json(OUT/'alexsmobs-r2o4c-aquatic-interactions.json');self.assertEqual(render(read_json(OUT/'native-specifications/alexsmobs-aquatic-interaction-contracts.json')),b)
  r=read_json(OUT/'mod-reviews/alexsmobs.json');ids={x['id'] for x in b['effects']};r['effects']=[x for x in r['effects'] if x['id'] not in ids];r['paths']=[x for x in r['paths'] if not set(x['effect_ids'])&ids]
  validate_batch(b,r,read_json(OUT/'alexsmobs-combat-census.json'));self.assertEqual(audit(dict(effects=b['effects']))['native_candidate_identities'],31)
 def test_catfish_player_damage_is_unreachable_in_native_selector(self):
  food=method('entity/EntityCatfish','isFood')['instructions'];types=[i['operand'] for i in food if i['opcode']=='0xc1'];self.assertEqual(set(types),{'net/minecraft/world/entity/Mob','com/github/alexthe666/alexsmobs/entity/EntityCatfish','net/minecraft/world/entity/item/ItemEntity'})
  v=read_json(OUT/'vanilla-evidence/alexsmobs-aquatic-owner-lifecycle.json');player=next(w for w in v['classes'] if w['class_name'].endswith('/Player'));self.assertEqual(player['superclass'],'net/minecraft/world/entity/LivingEntity')
  index=read_json(OUT/'alexsmobs-native-field-use-index.json');symbol=P+'entity/EntityCatfish$TargetFoodGoal.foodLnet/minecraft/world/entity/Entity;';s=index['symbols'].index(symbol)
  writes=[m['method'] for m in index['methods'] for i in m['field_sites'] if i[2]==s and i[1]==181];self.assertEqual(writes,['canUse'])
  b=read_json(OUT/'alexsmobs-r2o4c-aquatic-interactions.json');self.assertFalse(any(c['native_value']==12000 for r in b['effects'] for c in r['scalable_parameter_candidates']))
 def test_catfish_save_discard_and_restore_are_not_hurt(self):
  ins=method('entity/EntityCatfish','swallowEntity')['instructions'];self.assertTrue(calls(ins,'Mob.addAdditionalSaveData'));self.assertFalse(calls(ins,'.hurt('));self.assertFalse(calls(ins,'.discard('))
  goal=method('entity/EntityCatfish$TargetFoodGoal','tick')['instructions'];self.assertLess(calls(goal,'.swallowEntity(')[0]['offset'],calls(goal,'.discard(')[0]['offset'])
  ins=method('entity/EntityCatfish','spit')['instructions'];self.assertLess(calls(ins,'.setHealth(')[0]['offset'],calls(ins,'.addFreshEntity(')[0]['offset']);self.assertGreater(calls(ins,'.setHasSwallowedEntity(')[0]['offset'],calls(ins,'.addFreshEntity(')[0]['offset'])
  at=ins.index(calls(ins,'.addFreshEntity(')[0]);self.assertEqual(ins[at+1]['opcode'],'0x99')
 def test_catfish_death_spit_has_current_native_dispatch(self):
  v=read_json(OUT/'vanilla-evidence/alexsmobs-aquatic-owner-lifecycle.json');w=next(w for w in v['classes'] if w['class_name'].endswith('/LivingEntity'));m=next(m for m in w['methods'] if m['name']=='dropAllDeathLoot');self.assertTrue(calls(m['instructions'],'LivingEntity.dropEquipment()V'))
  self.assertTrue(calls(method('entity/EntityCatfish','dropEquipment')['instructions'],'.spit('))
 def test_terrapin_source_is_stored_launcher_not_projectile(self):
  ins=method('entity/EntityTerrapin','tick')['instructions'];self.assertTrue(any('lastLauncher' in str(i['operand']) and i['opcode']=='0xb4' for i in ins));self.assertTrue(calls(ins,'.mobAttack('));self.assertFalse(calls(ins,'.mobProjectile('));self.assertEqual(next(i['operand'] for i in ins if i['offset']==301),4.0)
  save=method('entity/EntityTerrapin','addAdditionalSaveData')['instructions'];self.assertFalse(any('lastLauncher' in str(i['operand']) for i in save))
  push=method('entity/EntityTerrapin','push')['instructions'];self.assertTrue(calls(push,'.setDeltaMovement('));self.assertFalse(calls(push,'.hurt('))
 def test_mantis_movement_burn_before_damage_and_current_target_reader(self):
  ins=method('entity/EntityMantisShrimp','aiStep')['instructions'];h=calls(ins,'.hurt(')[0]['offset'];self.assertLess(calls(ins,'.knockback(')[0]['offset'],h);self.assertLess(calls(ins,'.igniteForSeconds(')[0]['offset'],h);self.assertLess(calls(ins,'.setDeltaMovement(')[0]['offset'],h)
  at=next(n for n,i in enumerate(ins) if 'Attributes.KNOCKBACK_RESISTANCE' in str(i['operand']));self.assertEqual(ins[at-1]['opcode'],'0x2a')
  x=method('entity/EntityMantisShrimp','doHurtTarget')['instructions'];self.assertTrue(calls(x,'.punch('));self.assertFalse(any(i.get('local_index')==1 for i in x));self.assertFalse(calls(x,'.hurt('))
 def test_mantis_sit_does_not_write_parent_ordered_flag(self):
  ins=method('entity/EntityMantisShrimp','setOrderedToSit')['instructions'];self.assertTrue(calls(ins,'SynchedEntityData.set('));self.assertFalse(any(i['opcode']=='0xb5' or 'TamableAnimal.setOrderedToSit' in str(i['operand']) for i in ins))
  v=read_json(OUT/'vanilla-evidence/alexsmobs-aquatic-owner-lifecycle.json');goal=next(w for w in v['classes'] if w['class_name'].endswith('/SitWhenOrderedToGoal'));self.assertTrue(calls(next(m for m in goal['methods'] if m['name']=='canUse')['instructions'],'.isOrderedToSit('))
  own=next(w for w in v['classes'] if w['class_name'].endswith('/OwnableEntity'));self.assertTrue(calls(own['methods'][0]['instructions'],'.getPlayerByUUID('))
 def test_mantis_cooking_punch_does_not_require_absent_combat_target(self):
  d=read_json(OUT/'native-evidence/alexsmobs-aquatic-pet-helpers.json');w=next(w for w in d['witnesses'] if w['entry'].endswith('/MantisShrimpAIFryRice.class'));self.assertTrue(calls(next(m for m in w['methods'] if m['name']=='tick')['instructions'],'.punch('))
  self.assertFalse(calls(next(m for m in w['methods'] if m['name']=='canUse')['instructions'],'.getTarget('))
if __name__=='__main__':unittest.main()
