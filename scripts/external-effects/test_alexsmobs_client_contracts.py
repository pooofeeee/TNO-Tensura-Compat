"""Bounded client context and original network authority, including real display writes."""
import unittest,collections
from catalog_common import OUT,read_json
from assemble_authored_contracts import render
from promote_combat_batch import validate_batch
F='native-evidence/alexsmobs-remaining-client.json';D=read_json(OUT/F)
def body(cls,name):return next(m['instructions'] for w in D['witnesses'] if w['entry'].endswith('/'+cls+'.class') for m in w['methods'] if m['name']==name)
def calls(b,s):return [i for i in b if s in str(i['operand'])]
class ClientContracts(unittest.TestCase):
 def test_render_validate(self):
  s=read_json(OUT/'native-specifications/alexsmobs-client-contracts.json');b=read_json(OUT/'alexsmobs-r2oh-client.json');self.assertEqual(b,render(s));self.assertEqual(validate_batch(b,read_json(OUT/'mod-reviews/alexsmobs.json'),read_json(OUT/'alexsmobs-combat-census.json'))['status'],'PASS')
 def test_full_inventory_has_exact_sites_no_filtering(self):
  r=read_json(OUT/'alexsmobs-r2oh-client-context-inventory.json');c=collections.defaultdict(list);f=collections.defaultdict(list)
  for w in D['witnesses']:
   for m in w['methods']:
    for i in m['instructions']:
     row=dict(entry=w['entry'],method=m['name'],descriptor=m['descriptor'],offset=i['offset'],opcode=i['opcode'])
     if int(i['opcode'],16) in (182,183,184,185):c[i['operand']].append(row)
     if int(i['opcode'],16) in (179,181):f[i['operand']].append(row)
  self.assertEqual(r['calls'],dict(c));self.assertEqual(r['field_writes'],dict(f));self.assertEqual(sum(map(len,c.values())),9269)
 def test_preview_entities_are_created_without_world_add_or_actor_tick(self):
  b=body('AMItemstackRenderer','renderByItem');self.assertTrue(calls(b,'EntityType.create('));self.assertTrue(calls(b,'.renderedEntites'));self.assertFalse(calls(b,'.addFreshEntity('));self.assertFalse(calls(b,'.tick('));self.assertTrue(calls(b,'.setMaracas('))
 def test_preview_components_on_new_stacks(self):
  b=body('AMItemstackRenderer','renderByItem');self.assertEqual(len(calls(b,'ItemStack.set(')),2);self.assertGreater(len(calls(b,'ItemStack.<init>')),2)
 def test_preview_draw_resets_rotation_but_not_actor_tick(self):
  b=body('AMItemstackRenderer','drawEntityOnScreen');self.assertTrue(calls(b,'.setOnGround('));self.assertTrue(calls(b,'.tickCount'));self.assertTrue(calls(b,'.setXRot('));self.assertFalse(calls(b,'Entity.tick('))
 def test_eagle_client_producer_retains_local_call_and_message(self):
  b=body('ClientEvents','onRenderWorldLastEvent');self.assertTrue(calls(b,'.directFromPlayer('));self.assertTrue(calls(b,'MessageUpdateEagleControls.<init>'));self.assertTrue(calls(b,'.hitResult'));self.assertTrue(calls(b,'.setCameraEntity('));self.assertFalse(calls(b,'.hurt('))
 def test_model_counters_have_only_saved_index_display_uses(self):
  f=read_json(OUT/'alexsmobs-native-field-use-index.json')
  for marker,model in [('EntityRockyRoller.clientRoll','ModelRockyRoller'),('EntityTerrapin.clientSpin','ModelTerrapin'),('TileEntityEndPirateAnchorWinch.clientRoll','ModelEndPirateAnchorWinch')]:
   ms=[m for m in f['methods'] if any(marker in f['symbols'][x[2]] for x in m['field_sites'])];self.assertTrue(ms);self.assertTrue(all(model in m['entry'] or m['method']=='<init>' for m in ms))
 def test_pre_post_status_yaw_negation_is_paired(self):
  for name in ['onPreRenderEntity','onPostRenderEntity']:
   b=body('ClientEvents',name);fields=[i for i in b if int(i['opcode'],16)==181 and 'LivingEntity.y' in str(i['operand'])];self.assertEqual(len(fields),4);self.assertFalse(calls(b,'.setDeltaMovement('))
if __name__=='__main__':unittest.main()
