"""Current item dispatch, inactive legacy factories and lossy native storage."""
import unittest
from assemble_authored_contracts import render
from catalog_common import OUT,read_json
from promote_combat_batch import validate_batch
P='com/github/alexthe666/alexsmobs/'
D=read_json(OUT/'native-evidence/alexsmobs-remaining-items.json')
def body(cls,name):return next(m['instructions'] for w in D['witnesses'] if w['entry']==P+'item/'+cls+'.class' for m in w['methods'] if m['name']==name)
def calls(b,s):return [i for i in b if s in str(i['operand'])]
class ItemEquipment(unittest.TestCase):
 def test_render_validate(self):
  b=read_json(OUT/'alexsmobs-r2oe-items.json');self.assertEqual(b,render(read_json(OUT/'native-specifications/alexsmobs-item-equipment-contracts.json')))
  r=read_json(OUT/'mod-reviews/alexsmobs.json');ids={e['id'] for e in b['effects']};r['effects']=[e for e in r['effects'] if e['id'] not in ids];r['paths']=[p for p in r['paths'] if not set(p['effect_ids'])&ids];validate_batch(b,r,read_json(OUT/'alexsmobs-combat-census.json'))
 def test_ghost_storage_never_installs_copy(self):
  for n in ['putItemInGhostInventoryOrDrop','inventoryTick']:
   b=body('ItemGhostlyPickaxe',n);self.assertTrue(calls(b,'CustomData.copyTag('));self.assertTrue(calls(b,'SimpleContainer.<init>'));self.assertFalse(calls(b,'ItemStack.set('));self.assertFalse(calls(b,'CustomData.set('));self.assertFalse(calls(b,'SimpleContainer.fromTag('))
 def test_board_copies_entire_input_not_single(self):
  b=body('ItemStraddleboard','use');self.assertTrue(calls(b,'ItemStack.copy('));self.assertFalse(calls(b,'.copyWithCount('));self.assertTrue(calls(b,'.setItemStack('));self.assertFalse(calls(b,'.setOwnerUUID('))
 def test_legacy_dispenser_factories_are_not_active(self):
  v=read_json(OUT/'vanilla-evidence/alexsmobs-item-current-api.json');c=next(c for c in v['classes'] if c['class_name'].endswith('/DefaultDispenseItemBehavior'));self.assertFalse([m for m in c['declared_methods'] if m['name']=='getProjectile']);b=c['methods'][0]['instructions'];self.assertTrue(calls(b,'.split('));self.assertTrue(calls(b,'.spawnItem('));self.assertFalse(calls(b,'.getProjectile('))
  census=read_json(OUT/'alexsmobs-combat-census.json');syms={census['symbols'][s[2]] for m in census['methods'] for s in m['calls']};self.assertFalse([s for s in syms if 'AMItemRegistry$' in s and '.getProjectile(' in s])
 def test_current_duration_rejects_old_rainbow_signature(self):
  v=read_json(OUT/'vanilla-evidence/alexsmobs-item-current-api.json');c=next(c for c in v['classes'] if c['class_name'].endswith('/Item'));ms=[m for m in c['declared_methods'] if m['name']=='getUseDuration'];self.assertEqual(len(ms),1);self.assertEqual(ms[0]['obfuscated_descriptor'].count(';'),2)
 def test_locator_detached_data_and_mainhand_cost(self):
  b=body('ItemEcholocator','use');self.assertTrue(calls(b,'CustomData.copyTag('));self.assertFalse(calls(b,'ItemStack.set('));self.assertTrue(calls(b,'EquipmentSlot.MAINHAND'));self.assertTrue(calls(b,'.addCooldown('))
 def test_loader_damage_hook_and_fuel_descriptor(self):
  d=read_json(OUT/'reference-evidence/alexsmobs-item-current-loader.json');texts={w['entry']:w.get('text','') for w in d['witnesses']};self.assertIn('getItem().getMaxDamage(this)',texts['patches/net/minecraft/world/item/ItemStack.java.patch']);self.assertIn('getBurnTime(ItemStack itemStack, @Nullable RecipeType<?> recipeType)',texts['net/neoforged/neoforge/common/extensions/IItemExtension.java'])
 def test_whole_item_entity_consumed_for_worm(self):
  b=body('ItemMysteriousWorm','onEntityItemUpdate');self.assertTrue(calls(b,'.kill('));self.assertFalse(calls(b,'.shrink('));self.assertFalse(calls(b,'.split('));self.assertTrue(calls(b,'.setBaseMaxHealth('))
if __name__=='__main__':unittest.main()
