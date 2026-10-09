"""Native ring gates, recipe transfer loss, persistence and dormant registration."""
import unittest
from assemble_authored_contracts import render
from catalog_common import OUT,read_json
from promote_combat_batch import validate_batch
D=read_json(OUT/'native-evidence/alexsmobs-remaining-blocks.json');D['witnesses']+=read_json(OUT/'native-evidence/alexsmobs-block-registry-dependencies.json')['witnesses']
def body(cls,name):return next(m['instructions'] for w in D['witnesses'] if w['entry'].endswith('/'+cls+'.class') for m in w['methods'] if m['name']==name)
def calls(b,s):return [i for i in b if s in str(i['operand'])]
class BlockTile(unittest.TestCase):
 def test_render_validate(self):
  b=read_json(OUT/'alexsmobs-r2of-blocks.json');self.assertEqual(b,render(read_json(OUT/'native-specifications/alexsmobs-block-tile-contracts.json')))
  r=read_json(OUT/'mod-reviews/alexsmobs.json');ids={e['id'] for e in b['effects']};r['effects']=[e for e in r['effects'] if e['id'] not in ids];r['paths']=[p for p in r['paths'] if not set(p['effect_ids'])&ids];validate_batch(b,r,read_json(OUT/'alexsmobs-combat-census.json'))
 def test_scream_magic_then_unconditional_knockback(self):
  b=body('TileEntitySculkBoomer','commonTick');self.assertTrue(calls(b,'.magic('));hit=calls(b,'.hurt(')[0];at=b.index(hit);self.assertEqual(b[at+1]['opcode'],'0x57');self.assertTrue(calls(b[at:],'.knockback('));self.assertTrue(calls(b,'.horizontalDistance('));self.assertFalse(calls(b,'.isAlive('))
 def test_beak_is_server_contact_generic_not_mob_source(self):
  b=body('TileEntityVoidWormBeak','tick');self.assertTrue(calls(b,'.isClientSide'));self.assertTrue(calls(b,'.generic('));self.assertFalse(calls(b,'.mobAttack('));self.assertFalse(calls(b,'.addEffect('))
 def test_hatch_tame_gate_and_terrapin_lookup_after_removal(self):
  b=body('BlockReptileEgg','randomTick');self.assertTrue(calls(b,'.tame('));self.assertTrue(calls(b,'EntitySelector.NO_SPECTATORS'));self.assertFalse(calls(b,'.finalizeSpawn('))
  b=body('BlockTerrapinEgg','randomTick');self.assertLess(b.index(calls(b,'.removeBlock(')[0]),b.index(calls(b,'.getBlockEntity(')[0]));self.assertFalse(calls(b,'.tame('))
 def test_capsid_partial_transfer_retains_source(self):
  b=body('TileEntityCapsid','tick');self.assertTrue(calls(b,'.copy('));self.assertTrue(calls(b,'.grow('));self.assertTrue(calls(b,'.shrink('));self.assertFalse(calls(b,'.canPlaceItemThroughFace('));self.assertFalse(calls(b,'.setChanged('))
 def test_table_load_save_are_inverted_and_spelling_differs(self):
  b=body('TileEntityTransmutationTable','loadAdditional');self.assertTrue(calls(b,'.saveAsNBT('));self.assertFalse(calls(b,'.fromNBT('));bs=[x for x in read_json(OUT/'alexsmobs-combat-census.json')['registration_bootstraps'] if x['entry'].endswith('/TileEntityTransmutationTable.class')];self.assertIn('Possibility',str(bs));self.assertIn('Possiblity',str(bs))
  b=body('TileEntityTransmutationTable','saveAdditional');self.assertTrue(calls(b,'.fromNBT('));self.assertFalse(calls(b,'.saveAsNBT('))
 def test_loader_allows_extra_loot_parameters(self):
  d=read_json(OUT/'reference-evidence/alexsmobs-block-current-loader.json');w=next(w for w in d['witnesses'] if w['entry'].endswith('/LootParams.java.patch'));self.assertIn('false && !set.isEmpty()',w['text'])
 def test_pirate_holders_null_and_restoration_state_null(self):
  b=body('AMTileEntityRegistry','<clinit>');writes=[(n,i) for n,i in enumerate(b) if i['opcode']=='0xb3' and '.END_PIRATE_' in str(i['operand'])];self.assertEqual(len(writes),5);self.assertTrue(all(b[n-1]['opcode']=='0x1' for n,i in writes))
  b=body('TileEntityEndPirateAnchorWinch','tryPlaceAnchor');call=calls(b,'.setBlock(')[0];self.assertTrue(any(i['opcode']=='0x1' for i in b[:b.index(call)]));self.assertFalse(calls(b,'.defaultBlockState('))
if __name__=='__main__':unittest.main()
