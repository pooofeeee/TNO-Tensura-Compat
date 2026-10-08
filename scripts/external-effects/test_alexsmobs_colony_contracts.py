"""Native colony population, serialization defects and shared goal controls."""
import unittest
from assemble_authored_contracts import render
from audit_numeric_labels import audit
from catalog_common import OUT,read_json
from collect_combat_census import decode_sites
from promote_combat_batch import validate_batch

P='com/github/alexthe666/alexsmobs/'
PACKETS=[read_json(OUT/'native-evidence'/f'alexsmobs-{n}.json') for n in ('terrestrial','colony','colony-goals')]
def method(cls,name,descriptor=None):
    return next(m for d in PACKETS for w in d['witnesses'] if w['entry']==P+cls+'.class' for m in w['methods'] if m['name']==name and (descriptor is None or m['descriptor']==descriptor))
def calls(b,s): return [i for i in b if s in str(i['operand'])]

class ColonyContracts(unittest.TestCase):
    def test_render_validation_numeric_identity(self):
        b=read_json(OUT/'alexsmobs-r2o5d-shared-terrestrial-colony.json')
        self.assertEqual(render(read_json(OUT/'native-specifications/alexsmobs-shared-terrestrial-colony-contracts.json')),b)
        r=read_json(OUT/'mod-reviews/alexsmobs.json');ids={e['id'] for e in b['effects']}
        r['effects']=[e for e in r['effects'] if e['id'] not in ids];r['paths']=[p for p in r['paths'] if not set(p['effect_ids'])&ids]
        validate_batch(b,r,read_json(OUT/'alexsmobs-combat-census.json'))
        self.assertEqual(audit(dict(effects=b['effects']))['unresolved_numeric_labels'],0)

    def test_ant_bite_uses_truncated_current_attribute_value(self):
        b=method('entity/EntityLeafcutterAnt','tick')['instructions']
        h=calls(b,'.getAttributeValue(')[0]; j=b.index(h)
        self.assertEqual([i['opcode'] for i in b[j+1:j+3]],['0x8e','0x86'])
        hurt=calls(b,'.hurt(')[0]
        self.assertEqual(b[b.index(hurt)+1]['opcode'],'0x57')

    def test_queen_reproduction_cooldown_has_no_native_tick_countdown(self):
        b=method('entity/EntityLeafcutterAnt','mobInteract')['instructions']
        self.assertTrue(calls(b,'.haveBabyCooldownI'))
        for name in ('tick','customServerAiStep'):
            self.assertFalse(calls(method('entity/EntityLeafcutterAnt',name)['instructions'],'.haveBabyCooldownI'))

    def test_hive_position_transport_uses_different_nbt_types(self):
        a=method('entity/EntityLeafcutterAnt','addAdditionalSaveData')['instructions']
        b=method('entity/EntityLeafcutterAnt','readAdditionalSaveData')['instructions']
        self.assertTrue(calls(a,'NbtUtils.writeBlockPos('));self.assertTrue(calls(b,'CompoundTag.getLong('))
        self.assertTrue(calls(a,'CompoundTag.put('));self.assertTrue(calls(b,'BlockPos.of('))

    def test_stored_queen_flag_is_read_but_omitted_from_saved_ant_list(self):
        a=method('tileentity/TileEntityLeafcutterAnthill','getAnts')['instructions']
        b=method('tileentity/TileEntityLeafcutterAnthill','loadAdditional')['instructions']
        self.assertFalse(any(i['operand']=='Queen' for i in a))
        self.assertTrue(any(i['operand']=='Queen' for i in b))

    def test_colony_full_is_equality_and_entry_capacity_precedes_two_additions(self):
        b=method('tileentity/TileEntityLeafcutterAnthill','isFullOfAnts')['instructions']
        self.assertTrue(any(i['opcode']=='0xa0' for i in b))
        b=method('tileentity/TileEntityLeafcutterAnthill','tryEnterHive','(Lcom/github/alexthe666/alexsmobs/entity/EntityLeafcutterAnt;ZI)V')['instructions']
        self.assertEqual(len(calls(b,'List.add(')),2)
        self.assertEqual(len(calls(b,'.leafcutterAntColonySizeI')),2)
        self.assertTrue(calls(b,'.remove('))

    def test_release_lists_recipient_before_spawn_result(self):
        b=method('tileentity/TileEntityLeafcutterAnthill','addAntToWorld')['instructions']
        self.assertLess(calls(b,'List.add(')[0]['offset'],calls(b,'.addFreshEntity(')[0]['offset'])
        self.assertEqual(b[-1]['opcode'],'0xac')

    def test_anteater_release_filters_stored_queen(self):
        b=method('tileentity/TileEntityLeafcutterAnthill','lambda$tryReleaseAntAnteater$2')['instructions']
        self.assertTrue(calls(b,'.queenZ'))
        self.assertTrue(calls(b,'.addAntToWorld('))

    def test_fungus_shrink_uses_minimum_not_clamp(self):
        b=method('tileentity/TileEntityLeafcutterAnthill','shrinkFungus')['instructions']
        self.assertEqual(len(calls(b,'Math.min(')),2)
        self.assertFalse(calls(b,'Mth.clamp('))
        self.assertEqual(next(i['operand'] for i in b if i['offset']==116),0)

    def test_legacy_colony_use_is_not_current_block_callback(self):
        x=read_json(OUT/'vanilla-evidence/alexsmobs-colony-block-dispatch.json')
        names={m['name'] for c in x['classes'] for m in c['declared_methods']}
        self.assertNotIn('use',names);self.assertIn('useWithoutItem',names);self.assertIn('useItemOn',names)
        c=read_json(OUT/'alexsmobs-combat-census.json')
        targets={P+'block/'+cls+'.use'+method('block/'+cls,'use')['descriptor'] for cls in ('BlockLeafcutterAnthill','BlockLeafcutterAntChamber')}
        self.assertFalse([i for m in c['methods'] for i in decode_sites(c,m,'calls') if i['operand'] in targets])
        self.assertFalse([a for b in c['registration_bootstraps'] for a in b['arguments'] if any(t in str(a) for t in targets)])

    def test_creative_drop_overwrites_block_entity_data(self):
        b=method('block/BlockLeafcutterAnthill','playerWillDestroy')['instructions']
        self.assertEqual(len(calls(b,'DataComponents.BLOCK_ENTITY_DATA')),2)
        self.assertEqual(len(calls(b,'ItemStack.set(')),2)

    def test_anteater_raid_retains_grief_gate_before_target_assignment(self):
        b=method('entity/ai/AnteaterAIRaidNest','eatHive')['instructions']
        self.assertLess(calls(b,'EventHooks.canEntityGrief(')[0]['offset'],calls(b,'.setTarget(')[0]['offset'])
        self.assertFalse(calls(b,'.hurt('));self.assertFalse(calls(b,'.heal('))

    def test_ant_caravan_gate_and_reader_retain_contradiction(self):
        reader=method('entity/EntityLeafcutterAnt','shouldLeadCaravan')['instructions']
        self.assertTrue(calls(reader,'.hasLeaf('))
        b=method('entity/ai/LeafcutterAntAIFollowCaravan','canUse')['instructions']
        self.assertTrue(calls(b,'.shouldLeadCaravan('));self.assertTrue(calls(b,'.hasLeaf('))
        for symbol in ('.shouldLeadCaravan(','.hasLeaf('):
            hit=calls(b,symbol)[0];self.assertEqual(b[b.index(hit)+1]['opcode'],'0x9a')

if __name__=='__main__': unittest.main()
