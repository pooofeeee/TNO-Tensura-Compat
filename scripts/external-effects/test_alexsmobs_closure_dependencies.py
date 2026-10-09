"""Exact installed resources and Citadel tail that materially affect native boundaries."""
import unittest
from catalog_common import OUT,read_json
from assemble_authored_contracts import render
from promote_combat_batch import validate_batch
F='native-evidence/citadel-alexsmobs-final-dependencies.json';D=read_json(OUT/F)
def body(cls,name):return next(m['instructions'] for w in D['witnesses'] if w['entry'].endswith('/'+cls+'.class') for m in w['methods'] if m['name']==name)
def calls(b,s):return [i for i in b if s in str(i['operand'])]
class ClosureDependencies(unittest.TestCase):
 def test_renderer_and_final_additive_contracts(self):
  b=read_json(OUT/'alexsmobs-r2oi-resource-dependencies.json');self.assertEqual(b,render(read_json(OUT/'native-specifications/alexsmobs-final-dependency-contracts.json')));self.assertEqual(validate_batch(b,read_json(OUT/'mod-reviews/alexsmobs.json'),read_json(OUT/'alexsmobs-combat-census.json'))['status'],'PASS')
 def test_data_requires_mixin_interface_and_actual_save_hook(self):
  b=body('CitadelEntityData','setCitadelTag');self.assertTrue(calls(b,'ICitadelDataEntity'));self.assertTrue(calls(b,'.setCitadelEntityData('));b=body('LivingEntityMixin','citadel_writeAdditional');self.assertTrue(calls(b,'CitadelData'));self.assertTrue(calls(b,'.put('));b=body('LivingEntityMixin','setCitadelEntityData');self.assertTrue(calls(b,'SynchedEntityData.set('))
 def test_noninterface_data_is_detached(self):
  b=body('CitadelEntityData','getCitadelTag');self.assertTrue(calls(b,'CompoundTag.<init>'));self.assertFalse(calls(b,'.setData('))
 def test_properties_server_replaces_tag_without_owner_check(self):
  b=body('PropertiesMessage','lambda$handle$0');self.assertTrue(calls(b,'.getEntity('));self.assertTrue(calls(b,'CitadelTagUpdate'));self.assertTrue(calls(b,'.setCitadelTag('));self.assertFalse(calls(b,'.isOwnedBy('));self.assertFalse(calls(b,'.distanceToSqr('))
 def test_deprecated_biome_entry_fails_before_negation(self):
  b=body('SpawnBiomeData$SpawnBiomeEntry','matches');self.assertTrue(calls(b,'.isDepreciated('));self.assertTrue(calls(b,'.negate'));self.assertTrue(calls(b,'.tags('))
 def test_resource_damage_and_enchantment_profiles_are_explicit(self):
  d={w['entry']:w.get('data') for w in read_json(OUT/'native-evidence/alexsmobs-final-resources.json')['witnesses']};self.assertEqual(d['data/alexsmobs/damage_type/freddy.json']['scaling'],'never');self.assertEqual(d['data/alexsmobs/damage_type/farseer.json']['scaling'],'when_caused_by_living_non_player');self.assertEqual(d['data/alexsmobs/enchantment/straddle_jump.json']['max_level'],3);self.assertTrue(all('effects' not in v for k,v in d.items() if '/enchantment/' in k))
 def test_all_complex_nonadvancement_payloads_reviewed(self):
  a=read_json(OUT/'alexsmobs-final-resource-audit.json');self.assertEqual(a['total_data_json'],646);self.assertEqual(len(a['non_advancement_complex_payloads']),1);self.assertEqual(a['advancement_rewards'],[]);self.assertEqual(a['non_advancement_complex_payloads'][0]['value'],{'minecraft:potion_contents':{'potion':'minecraft:water'}})
 def test_numeric_site_alias_does_not_duplicate_input(self):
  s=read_json(OUT/'native-specifications/alexsmobs-global-contracts.json');r=next(x for x in s['contracts'] if x['id']=='alexsmobs:native_global_interaction_resources');self.assertFalse([c for c in r['candidate_bindings'] if c['parameters']==['flu_clear_probability']]);self.assertEqual(next(c for c in r['components'] if c['primitive']=='NATIVE_CONVERSION_ADMISSION')['numeric_label_bindings']['flu_clear_probability']['target_record'],'alexsmobs:ender_flu')
if __name__=='__main__':unittest.main()
