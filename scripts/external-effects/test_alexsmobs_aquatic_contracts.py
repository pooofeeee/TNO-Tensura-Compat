"""Native aquatic consumers, copied data and current dispatcher regressions."""
import unittest
from catalog_common import OUT,read_json
from assemble_authored_contracts import render
from promote_combat_batch import validate_batch
from audit_numeric_labels import audit
P='com/github/alexthe666/alexsmobs/'
F='native-evidence/alexsmobs-aquatic-small.json'
def method(cls,name,file=F):
 w=next(w for w in read_json(OUT/file)['witnesses'] if w['entry']==P+cls+'.class')
 return next(m for m in w['methods'] if m['name']==name)
def calls(ins,part):return [i for i in ins if i['opcode'] in ('0xb6','0xb7','0xb8','0xb9') and part in str(i['operand'])]
class AquaticContracts(unittest.TestCase):
 def test_render_and_exact_native_candidates(self):
  b=read_json(OUT/'alexsmobs-r2o4a-small-aquatic.json');self.assertEqual(render(read_json(OUT/'native-specifications/alexsmobs-aquatic-contracts.json')),b)
  r=read_json(OUT/'mod-reviews/alexsmobs.json');ids={v['id'] for v in b['effects']};r['effects']=[v for v in r['effects'] if v['id'] not in ids];r['paths']=[v for v in r['paths'] if not set(v['effect_ids'])&ids]
  validate_batch(b,r,read_json(OUT/'alexsmobs-combat-census.json'));self.assertEqual(audit(dict(effects=b['effects']))['native_candidate_identities'],19)
 def test_bucket_extras_are_detached_not_written_back(self):
  v=read_json(OUT/'vanilla-evidence/alexsmobs-aquatic-native-dispatch.json');copy=next(w for w in v['classes'] if w['class_name'].endswith('/CustomData'))['methods'][0]
  self.assertTrue(calls(copy['instructions'],'CompoundTag.copy'))
  for cls in ['Blobfish','CombJelly','FlyingFish','Lobster','Triops','DevilsHolePupfish']:
   ins=method('entity/Entity'+cls,'saveToBucketTag')['instructions'];at=calls(ins,'CustomData.copyTag')[0]['offset']
   self.assertTrue(calls([i for i in ins if i['offset']>at],'CompoundTag.put'))
   self.assertFalse(calls([i for i in ins if i['offset']>at],'ItemStack.set('))
   self.assertFalse(calls(ins,'CustomData.update('))
  loader=read_json(OUT/'reference-evidence/alexsmobs-aquatic-native-loader.json');self.assertTrue(all(w.get('absent') for w in loader['witnesses']))
  ins=method('item/ItemModFishBucket','spawnFish','native-evidence/alexsmobs-aquatic-helpers.json')['instructions']
  self.assertTrue(any('DataComponents.BUCKET_ENTITY_DATA' in str(i['operand']) for i in ins));self.assertFalse(any('DataComponents.CUSTOM_DATA' in str(i['operand']) for i in ins))
 def test_lobster_second_hurt_is_independent_and_first_result_native(self):
  ins=method('entity/EntityLobster','doHurtTarget')['instructions'];self.assertLess(calls(ins,'SynchedEntityData.set(')[0]['offset'],calls(ins,'.doHurtTarget(')[0]['offset'])
  ins=method('entity/EntityLobster','tick')['instructions'];hit=calls(ins,'.hurt(')[0];at=ins.index(hit)
  self.assertEqual(ins[at+1]['opcode'],'0x57');self.assertEqual(ins[at-1]['operand'],2.0)
  self.assertGreater(calls(ins,'.doHurtTarget(')[0]['offset'],hit['offset'])
 def test_flying_fish_escape_is_hurt_return_and_causing_entity_gated(self):
  ins=method('entity/EntityFlyingFish','hurt')['instructions'];h=calls(ins,'.hurt(')[0]['offset'];s=calls(ins,'DamageSource.getEntity')[0]['offset'];writes=[i['offset'] for i in ins if i['opcode']=='0xb5' and 'glideIn' in str(i['operand'])]
  self.assertLess(h,s);self.assertTrue(all(o>s for o in writes));self.assertFalse(calls(ins,'DamageSource.getDirectEntity'))
  raw=read_json(OUT/'vanilla-evidence/alexsmobs-aquatic-native-dispatch.json')
  for cls in raw['classes']:
   if cls['class_name'].endswith(('Entity','LivingEntity','Mob','PathfinderMob','WaterAnimal')):
    for m in cls['declared_methods']:
     if m['name']=='causeFallDamage':self.assertNotEqual(m['obfuscated_descriptor'],'(FF)Z')
     self.assertNotEqual(m['name'],'getStandingEyeHeight')
  self.assertEqual(method('entity/EntityFlyingFish','checkFallDamage')['instructions'][-1]['opcode'],'0xb1')
 def test_blobfish_registered_builder_is_not_old_create_attributes(self):
  c=read_json(OUT/'alexsmobs-combat-census.json');symbol=P+'entity/EntityBlobfish.createAttributes()Lnet/minecraft/world/entity/ai/attributes/AttributeSupplier$Builder;'
  self.assertFalse(any(symbol in str(m.get('calls',[]))+str(m.get('bootstrap_method_refs',[])) for m in c['methods']))
  ins=method('entity/AMEntityRegistry','initializeAttributes','native-evidence/alexsmobs-foundation.json')['instructions'];self.assertTrue(calls(ins,'EntityBlobfish.bakeAttributes'))
 def test_dropped_item_heal_precedes_consumption_even_when_heal_branch_fails(self):
  ins=method('entity/ai/CreatureAITargetItems','tick')['instructions'];self.assertLess(calls(ins,'.onGetItem(')[0]['offset'],calls(ins,'ItemStack.shrink(')[0]['offset'])
  tri=method('entity/EntityTriops','onGetItem')['instructions'];self.assertLess(calls(tri,'getFoodProperties(')[0]['offset'],calls(tri,'.heal(')[0]['offset'])
  defaults=method('entity/ITargetsDroppedItems','getMaxDistToItem','native-evidence/alexsmobs-aquatic-helpers.json');self.assertEqual(defaults['instructions'][0]['operand'],2.0)
 def test_ordinary_foraging_and_chase_do_not_deal_damage_or_destroy_moss(self):
  for cls in ['EntityDevilsHolePupfish$EatMossGoal','EntityDevilsHolePupfish$ChaseGoal','EntityTriops$BreedGoal','EntityTriops$LayEggGoal']:
   w=next(w for w in read_json(OUT/F)['witnesses'] if w['entry']==P+'entity/'+cls+'.class')
   for m in w['methods']:
    self.assertFalse(calls(m['instructions'],'.hurt('));self.assertFalse(calls(m['instructions'],'.addEffect('));self.assertFalse(calls(m['instructions'],'.destroyBlock('))
if __name__=='__main__':unittest.main()
