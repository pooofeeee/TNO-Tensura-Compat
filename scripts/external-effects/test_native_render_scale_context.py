"""Exact native scale/query sources, render argument flow and discarded returns."""
import copy
import unittest
from catalog_common import OUT,read_json
from collect_combat_census import decode_sites
from reconcile_native_census import reconcile
from promote_combat_batch import validate_batch


class NativeRenderScaleContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.b=read_json(OUT/'arphex-r2m7j-native-render-scale-context.json')
        cls.e=read_json(OUT/'native-evidence/arphex-native-render-scale-context.json')
        cls.c=read_json(OUT/'arphex-combat-census.json')

    def test_minimum_missing_methods_are_explicit_and_no_semantics_are_added(self):
        self.assertEqual(len(self.e['witnesses']),57)
        self.assertEqual(sum(len(w['methods']) for w in self.e['witnesses']),57)
        self.assertEqual(sum('/procedures/' in w['entry'] for w in self.e['witnesses']),19)
        self.assertEqual(len(self.b['exclusions']),58)
        self.assertEqual(self.b['effects'],[]);self.assertEqual(self.b['paths'],[])
        self.assertEqual(len(read_json(OUT/self.b['native_forwarding_registry_file'])['rows']),76)
        r=read_json(OUT/'mod-reviews/arphex.json');r['reviewed_batches']=[f for f in r['reviewed_batches'] if f!='arphex-r2m7j-native-render-scale-context.json']
        self.assertEqual(validate_batch(self.b,r,self.c)['semantic_records'],len(r['effects']))

    def test_helpers_have_only_actual_read_math_or_original_native_lifecycle_calls(self):
        allowed={'net/minecraft/network/syncher/SynchedEntityData.get(Lnet/minecraft/network/syncher/EntityDataAccessor;)Ljava/lang/Object;',
            'java/lang/Integer.intValue()I','java/lang/String.equals(Ljava/lang/Object;)Z','java/lang/Math.max(DD)D',
            'net/minecraft/world/entity/Entity.getDisplayName()Lnet/minecraft/network/chat/Component;',
            'net/minecraft/network/chat/Component.getString()Ljava/lang/String;',
            'net/minecraft/util/RandomSource.create()Lnet/minecraft/util/RandomSource;',
            'net/minecraft/util/Mth.nextDouble(Lnet/minecraft/util/RandomSource;DD)D',
            'net/arphex/network/ArphexModVariables$MapVariables.get(Lnet/minecraft/world/level/LevelAccessor;)Lnet/arphex/network/ArphexModVariables$MapVariables;'}
        # An unrelated screen/menu declaration cannot override an Entity query.
        declared={m['method']+m['descriptor'] for m in self.c['methods']
                  if m['entry'].startswith('net/arphex/entity/')}
        self.assertFalse('getEntityData()Lnet/minecraft/network/syncher/SynchedEntityData;' in declared)
        self.assertFalse('getDisplayName()Lnet/minecraft/network/chat/Component;' in declared)
        for w in self.e['witnesses']:
            if '/procedures/' not in w['entry']:continue
            m=w['methods'][0];self.assertTrue(m['descriptor'].endswith(')D'))
            self.assertFalse(any(i['opcode'] in ('0xb3','0xb5') for i in m['instructions']))
            for i in m['instructions']:
                if i['opcode'] not in ('0xb6','0xb7','0xb8','0xb9'):continue
                operand=str(i['operand'])
                native_actor=operand.startswith('net/arphex/entity/') and operand.endswith(('.getEntityData()Lnet/minecraft/network/syncher/SynchedEntityData;','.getTexture()Ljava/lang/String;'))
                self.assertTrue(operand in allowed or native_actor,operand)
        # Map lookup/storage and ephemeral RNG remain native; absence of direct
        # helper writes does not assert these library calls never allocate data.
        self.assertTrue(any('storage lifecycle' in r['reason'] for r in self.b['exclusions']))

    def test_computed_render_writes_only_render_fields_and_forwards_exact_arguments(self):
        for w in self.e['witnesses']:
            if '/client/renderer/' not in w['entry']:continue
            b=w['methods'][0]['instructions'];owner=w['entry'][:-6]
            self.assertEqual({i['operand'] for i in b if i['opcode']=='0xb5'},{owner+'.scaleHeightF',owner+'.scaleWidthF'})
            self.assertEqual([i.get('local_index') for i in b[-13:-2]],list(range(11)))
            self.assertTrue(b[-2]['operand'].startswith('software/bernie/geckolib/renderer/GeoEntityRenderer.preRender('))
            self.assertEqual(b[-1]['opcode'],'0xb1')
            calls=[(n,i) for n,i in enumerate(b) if i['opcode']=='0xb8'];self.assertEqual(len(calls),1)
            at,call=calls[0];self.assertTrue(str(call['operand']).endswith(')D'))
            self.assertEqual(b[at+1]['opcode'],'0x90');self.assertEqual(b[at+2].get('local_index'),18)
            if '(Lnet/minecraft/world/entity/Entity;)D' in call['operand']:self.assertEqual(b[at-1].get('local_index'),2)
            elif '(Lnet/minecraft/world/level/LevelAccessor;)D' in call['operand']:self.assertEqual(b[at-1].get('local_index'),11)
            else:self.assertTrue(call['operand'].endswith('.execute()D'))
            self.assertFalse(any('.tryNyfsRotation(' in str(i['operand']) for i in b))

    def test_every_existing_helper_caller_and_handle_is_retained_exactly(self):
        self.assertEqual(len(self.b['native_render_query_call_context']),27)
        for q in self.b['native_render_query_call_context']:
            symbol=q['entry'][:-6]+'.'+q['method']+q['descriptor'];calls=[];handles=[]
            for m in self.c['methods']:
                for i in decode_sites(self.c,m,'calls'):
                    if i['operand']==symbol:calls.append(dict(entry=m['entry'],method=m['method'],descriptor=m['descriptor'],offset=i['offset']))
            for bootstrap in self.c['registration_bootstraps']:
                if symbol in str(bootstrap):handles.append(dict(entry=bootstrap['entry'],index=bootstrap['index']))
            self.assertEqual(calls,q['native_callers']);self.assertEqual(handles,q['native_handle_references'])

    def test_original_event_query_return_is_discarded_not_physical_resize(self):
        x=next(r for r in self.b['exclusions'] if r['disposition']=='EXACT_NATIVE_DISCARDED_EVENT_QUERY_RETURN');p=x['implementation'][0]
        w=next(w for w in read_json(OUT/p['evidence_file'])['witnesses'] if w['id']==p['witness_id'])
        m=next(m for m in w['methods'] if m['name']=='onEntityTick');b=m['instructions']
        self.assertEqual([i['opcode'] for i in b],['0x2a','0x2a','0xb6','0xb8','0x58','0xb1'])
        self.assertTrue(b[2]['operand'].endswith('EntityTickEvent$Pre.getEntity()Lnet/minecraft/world/entity/Entity;'))
        self.assertTrue(b[3]['operand'].endswith('execute(Lnet/neoforged/bus/api/Event;Lnet/minecraft/world/entity/Entity;)D'))

    def test_method_identity_change_cannot_close_the_query_or_renderer(self):
        r=read_json(OUT/'mod-reviews/arphex.json')
        if 'arphex-r2m7j-native-render-scale-context.json' not in r['reviewed_batches']:r['reviewed_batches'].append('arphex-r2m7j-native-render-scale-context.json')
        native=copy.deepcopy(self.e);native['witnesses'][0]['methods'][0]['code_sha256']='0'*64
        def read(path):
            return native if str(path.relative_to(OUT))=='native-evidence/arphex-native-render-scale-context.json' else read_json(path)
        with self.assertRaisesRegex(AssertionError,'hash mismatch'):reconcile(r,self.c,read=read)

    def test_bridges_cannot_supply_their_own_missing_target_proof(self):
        r=read_json(OUT/'mod-reviews/arphex.json')
        r['reviewed_batches']=[f for f in r['reviewed_batches'] if f!='arphex-r2m7j-native-render-scale-context.json']
        b=copy.deepcopy(self.b)
        target=read_json(OUT/b['native_forwarding_registry_file'])['rows'][0]['target']['entry']
        b['exclusions']=[x for x in b['exclusions'] if x['entry']!=target]
        with self.assertRaisesRegex(AssertionError,'target lacks prior'):
            validate_batch(b,r,self.c)


if __name__=='__main__':unittest.main()
