"""Independent event direction, discarded results and native presentation sinks."""
import unittest
from catalog_common import OUT,read_json
from collect_combat_census import decode_sites
from native_uncalled import native_references
from promote_combat_batch import validate_batch
from test_shadow_clone_contracts import NativeContractHarness


class NativeRenderContextTests(NativeContractHarness,unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch=read_json(OUT/'arphex-r2m7d-native-render-context.json')
        cls.native=read_json(OUT/'native-evidence/arphex-native-render-context.json')
        cls.census=read_json(OUT/'arphex-combat-census.json')

    def test_scoped_exclusions_do_not_create_combat_or_scalar_records(self):
        summary=validate_batch(self.batch,self.prior(),self.census)
        self.assertEqual((summary['semantic_records'],summary['numeric_candidate_entries']),(462,3903))
        self.assertFalse(self.batch['effects']);self.assertFalse(self.batch['paths'])
        self.assertEqual(len(self.native['witnesses']),41)
        self.assertEqual(sum(len(w['methods']) for w in self.native['witnesses']),103)
        self.assertEqual({w['entry'] for w in self.native['witnesses']},{e['entry'] for e in self.batch['exclusions']})

    def test_live_entity_tick_callbacks_discard_numeric_query_results(self):
        for name in ('BloodWormEntityVisualScaleProcedure','SpiderMothDwellerBoundingBoxScaleProcedure'):
            b=self.body(name,'onEntityTick');at=next(j for j,i in enumerate(b) if '.execute(' in str(i['operand']))
            self.assertEqual(b[at+1]['opcode'],'0x58');self.assertEqual(b[-1]['opcode'],'0xb1')
            w=next(w for w in self.native['witnesses'] if w['entry'].endswith('/'+name+'.class'))
            m=next(m for m in w['methods'] if m['name']=='onEntityTick')
            self.assertTrue(any('SubscribeEvent;' in a['descriptor'] for a in m['annotations']))
            self.assertFalse(any(i['opcode'] in ('0xb3','0xb5') or '.put' in str(i['operand']) or '.set' in str(i['operand'])
                                 for m in w['methods'] for i in m['instructions']))
        b=self.body('SpiderMothDwellerBoundingBoxScaleProcedure')
        self.assertTrue(any(i['operand']==1.48 for i in b));self.assertEqual(b[-1]['opcode'],'0xaf')

    def test_scale_helpers_keep_all_native_callers_without_inventing_collision(self):
        calls,handles=native_references(self.census)
        for r in self.batch['native_scale_call_context']:
            symbol=r['entry'][:-6]+'.'+r['method']+r['descriptor']
            self.assertEqual(calls.get(symbol,[]),r['native_callers'])
            self.assertEqual(handles.get(symbol,[]),r['native_handle_references'])
        forbidden=('.refreshDimensions(','.setBoundingBox(','.setPos(','.setDeltaMovement(','.setHealth(','.hurt(','.addEffect(')
        for w in self.native['witnesses']:
            if any(w['entry']==r['entry'] for r in self.batch['native_scale_call_context']):
                self.assertFalse(any(t in str(i['operand']) for m in w['methods'] for i in m['instructions'] for t in forbidden))

    def test_client_events_are_explicitly_dist_client_and_have_no_damage_payload(self):
        for name in ('RenderTest4Procedure','RenderTest6Procedure','RenderTest7Procedure','RenderTest8Procedure',
                     'WorldRenderTestProcedure','WorldRenderTest2Procedure','WorldRenderTest3Procedure'):
            w=next(w for w in self.native['witnesses'] if w['entry'].endswith('/'+name+'.class'))
            annotation=next(a for a in w['annotations'] if 'EventBusSubscriber;' in a['descriptor'])
            self.assertEqual(annotation['values']['value'],[{'enum_type':'Lnet/neoforged/api/distmarker/Dist;','constant':'CLIENT'}])
        forbidden=('.hurt(','.heal(','.setHealth(','.addEffect(','.setDeltaMovement(','.teleportTo(','.addFreshEntity(','.spawn(','.sendToServer(')
        self.assertFalse(any(t in str(i['operand']) for w in self.native['witnesses'] for m in w['methods'] for i in m['instructions'] for t in forbidden))

    def test_mutable_render_scratch_fields_have_no_hidden_native_combat_reader(self):
        fields=self.batch['native_client_attachment_field_context']
        expected={'current_ascendant','asc_subchain','asc_x','asc_y','asc_z','overlay_red','overlay_white','overlay_black'}
        self.assertEqual({k.split('PlayerVariables.')[1].split('Ljava')[0].removesuffix('D') for k in fields},expected)
        index=read_json(OUT/self.batch['native_field_index_file'])
        actual={k:[] for k in fields}
        for m in index['methods']:
            for i in decode_sites(index,m,'field_sites'):
                if i['operand'] in actual:
                    actual[i['operand']].append(dict(entry=m['entry'],method=m['method'],descriptor=m['descriptor'],
                        code_sha256=m['code_sha256'],offset=i['offset'],opcode=i['opcode']))
        self.assertEqual({k:sorted(v,key=lambda r:(r['entry'],r['method'],r['descriptor'],r['offset'])) for k,v in actual.items()},fields)
        for key,sites in fields.items():
            if any('PlayerVariables.'+k in key for k in ('current_ascendant','asc_subchain','asc_x','asc_y','asc_z')):
                self.assertTrue(all(s['entry'].endswith(('RenderTest6Procedure.class','ArphexModVariables$PlayerVariables.class',
                                                       'ArphexModVariables$EventBusVariableHandlers.class')) for s in sites))
        writes=[i['operand'] for i in self.body('RenderTest6Procedure') if i['opcode']=='0xb5']
        self.assertEqual(set(writes),set(fields))

    def test_display_models_are_not_inserted_or_ticked_and_inventory_is_copied(self):
        w=next(w for w in self.native['witnesses'] if w['entry'].endswith('/WorldRenderTestProcedure.class'))
        self.assertTrue(any('EntityType.create(' in str(i['operand']) for m in w['methods'] for i in m['instructions']))
        self.assertFalse(any(t in str(i['operand']) for m in w['methods'] for i in m['instructions'] for t in
                             ('.addFreshEntity(','.tick()', '.baseTick()', '.setXRot(', '.setYRot(')))
        for w in self.native['witnesses']:
            for m in w['methods']:
                if m['name']=='getItemStack':
                    b=m['instructions'];at=next(j for j,i in enumerate(b) if '.getStackInSlot(' in str(i['operand']))
                    self.assertIn('ItemStack.copy()',b[at+1]['operand'])
                    self.assertFalse(any('.setStackInSlot(' in str(i['operand']) for i in b))
        prior=read_json(OUT/'native-evidence/arphex-native-state-transport.json')
        w=next(w for w in prior['witnesses'] if w['entry'].endswith('$PlayerVariables.class'))
        b=next(m['instructions'] for m in w['methods'] if m['name']=='syncPlayerVariables')
        server=next(i['offset'] for i in b if i['opcode']=='0xc1' and i['operand']=='net/minecraft/server/level/ServerPlayer')
        send=next(i['offset'] for i in b if '.sendToPlayer(' in str(i['operand']))
        self.assertLess(server,send)

    def test_dimension_effect_factories_are_not_registered_by_empty_event_body(self):
        calls,handles=native_references(self.census)
        self.assertEqual(len(self.batch['native_unreferenced_client_factories']),5)
        w=next(w for w in self.native['witnesses'] if w['entry'].endswith('/RenderTest8Procedure.class'))
        for r in self.batch['native_unreferenced_client_factories']:
            symbol=r['entry'][:-6]+'.'+r['method']+r['descriptor']
            self.assertFalse(calls.get(symbol));self.assertFalse(handles.get(symbol))
            m=next(m for m in w['methods'] if (m['name'],m['descriptor'])==(r['method'],r['descriptor']))
            self.assertFalse(m['annotations']);self.assertEqual(m['code_sha256'],r['code_sha256'])
        self.assertEqual(self.body('RenderTest8Procedure','execute')[-1]['opcode'],'0xb1')
        self.assertFalse(any(i['opcode'] in ('0xb6','0xb7','0xb8','0xb9') for i in self.body('RenderTest8Procedure','execute')))
        live=next(m for m in w['methods'] if m['name']=='setupDimensions')
        self.assertTrue(any('SubscribeEvent;' in a['descriptor'] for a in live['annotations']))


if __name__=='__main__':unittest.main()
