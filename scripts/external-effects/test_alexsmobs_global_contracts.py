"""Global delivery authority, actual resource losses and inactive native libraries."""
import unittest
from assemble_authored_contracts import render
from catalog_common import OUT,read_json
from promote_combat_batch import validate_batch
S=read_json(OUT/'native-specifications/alexsmobs-global-contracts.json');B=read_json(OUT/'alexsmobs-r2og-global.json')
files={p.get('evidence_file',S['evidence_file']) for r in S['contracts'] for p in r['implementation']}
D=[w for f in files for w in read_json(OUT/f)['witnesses']]
def body(cls,name):return next(m['instructions'] for w in D if w['entry'].endswith('/'+cls+'.class') for m in w['methods'] if m['name']==name and m['instructions'])
def calls(b,s):return [i for i in b if s in str(i['operand'])]
class GlobalContracts(unittest.TestCase):
 def test_render_validate(self):
  self.assertEqual(B,render(S));r=read_json(OUT/'mod-reviews/alexsmobs.json');ids={e['id'] for e in B['effects']};r['effects']=[e for e in r['effects'] if e['id'] not in ids];r['paths']=[p for p in r['paths'] if not set(p['effect_ids'])&ids];validate_batch(B,r,read_json(OUT/'alexsmobs-combat-census.json'))
 def test_pufferfish_reflection_not_guaranteed_field(self):
  b=body('ServerEvents','setPufferfishState');self.assertTrue(calls(b,'.getDeclaredFields('));self.assertTrue(calls(b,'.PUFF_STATE_INIT_ATTEMPTED'));self.assertTrue(calls(b,'.set('))
 def test_conversion_does_readd_same_instance(self):
  b=body('ServerEvents','onInteractWithEntity');self.assertTrue(calls(b,'.convertTo('));self.assertTrue(calls(b,'.addFreshEntity('));self.assertFalse(calls(b,'Bunfungus.create('))
 def test_lightning_spawn_before_original_discard(self):
  b=body('ServerEvents','onStruckByLightning');self.assertLess(b.index(calls(b,'.addFreshEntityWithPassengers(')[0]),b.index(calls(b,'.discard(')[0]));self.assertTrue(calls(b,'.setBlue('));self.assertTrue(calls(b,'.setCanceled('))
 def test_mimicream_is_full_damage_no_component_install(self):
  b=body('RecipeMimicreamRepair','assemble');self.assertTrue(calls(b,'.getMaxDamage('));self.assertTrue(calls(b,'.setDamageValue('));self.assertFalse(calls(b,'ItemStack.set('));self.assertFalse(calls(b,'.setCustomData('))
 def test_bison_recipe_does_not_install_fur(self):
  b=body('RecipeBisonUpgrade','createBoots');self.assertTrue(calls(b,'.copy('));self.assertFalse(calls(b,'.set('));self.assertFalse(calls(b,'.putBoolean('))
 def test_pupfish_search_has_no_native_caller(self):
  c=read_json(OUT/'alexsmobs-combat-census.json');self.assertFalse([s for m in c['methods'] for s in m.get('calls',[]) if '.tickPupfish(' in c['symbols'][s[2]]]);b=body('AMWorldData','getWaterHeight');self.assertEqual(b[0]['opcode'],'0x1');self.assertTrue(calls(b,'NoiseSettings.minY('))
 def test_biome_client_uses_detached_container(self):
  b=body('MessageMungusBiomeChange','lambda$handleClient$0');self.assertTrue(calls(b,'.recreate('));self.assertTrue(calls(b,'.getAndSetUnchecked('));self.assertFalse(calls(b,'.setBiomes('));self.assertFalse(calls(b,'LevelChunkSection.fillBiomesFromNoise('))
 def test_transmute_uses_context_and_current_menu(self):
  b=body('MessageTransmuteFromMenu','lambda$handleServer$0');self.assertTrue(calls(b,'IPayloadContext.player('));self.assertTrue(calls(b,'.containerMenu'));self.assertFalse(calls(b,'.getEntity('))
 def test_current_harvest_and_client_empty_click(self):
  d=read_json(OUT/'reference-evidence/alexsmobs-global-current-loader.json');texts={w['entry']:w['text'] for w in d['witnesses']};p=next(t for e,t in texts.items() if e.endswith('ServerPlayerGameMode.java.patch'));self.assertIn('blockstate.canHarvestBlock',p);self.assertIn('if (flag1 && flag)',p);p=next(t for e,t in texts.items() if e.endswith('PlayerInteractEvent.java'));self.assertIn('The server is not aware',p)
if __name__=='__main__':unittest.main()
