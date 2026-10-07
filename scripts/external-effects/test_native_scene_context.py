"""Actual native glow arguments, optional reflection/fallbacks and pose writes."""
import copy
import unittest
from catalog_common import OUT,read_json
from reconcile_native_census import reconcile
from promote_combat_batch import validate_batch


class NativeSceneContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.b=read_json(OUT/'arphex-r2m7k-native-scene-context.json')
        cls.e=read_json(OUT/'native-evidence/arphex-native-scene-context.json')
        cls.c=read_json(OUT/'arphex-combat-census.json')
        cls.w={w['entry']:w for w in cls.e['witnesses']}

    def method(self,entry,name):
        return next(m for m in self.w[entry]['methods'] if m['name']==name)

    def test_scoped_roots_and_bridges_preserve_the_existing_catalog(self):
        self.assertEqual(len(self.w),72)
        self.assertEqual(sum(len(w['methods']) for w in self.w.values()),161)
        self.assertEqual(len(self.b['native_glow_layers']),49)
        self.assertEqual(len(self.b['native_optional_pose_context']),8)
        self.assertEqual(len(self.b['native_render_admission_context']),15)
        self.assertEqual(self.b['effects'],[]);self.assertEqual(self.b['paths'],[])
        d=read_json(OUT/self.b['native_forwarding_registry_file'])
        self.assertEqual(d['summary'],dict(methods=88,counts_by_kind={'EXACT_COMPILER_BRIDGE':88}))
        r=read_json(OUT/'mod-reviews/arphex.json')
        r['reviewed_batches']=[f for f in r['reviewed_batches'] if f!='arphex-r2m7k-native-scene-context.json']
        self.assertEqual(validate_batch(self.b,r,self.c)['semantic_records'],len(r['effects']))

    def test_glow_layer_uses_original_actor_and_native_draw_parameters(self):
        declared={(m['entry'],m['method']) for m in self.c['methods']}
        for layer in self.b['native_glow_layers']:
            entry=layer['entry'];b=self.method(entry,'render')['instructions']
            self.assertFalse(any(i['opcode'] in ('0xb3','0xb5') for i in b))
            at=next(n for n,i in enumerate(b) if '.getDefaultBakedModel(' in str(i['operand']))
            self.assertEqual(b[at-1].get('local_index'),2)
            call=next(n for n,i in enumerate(b) if '.reRender(' in str(i['operand']))
            self.assertEqual([i.get('local_index') for i in b[at+1:at+6]],[1,5,2,10,5])
            self.assertEqual([i.get('local_index') for i in b[call-4:call-2]],[7,8])
            self.assertEqual(b[call-2]['operand'],'net/minecraft/client/renderer/texture/OverlayTexture.NO_OVERLAYI')
            self.assertEqual(b[call-1]['operand'],-1)
            self.assertTrue(any(i['operand']=='net/minecraft/client/renderer/RenderType.eyes(Lnet/minecraft/resources/ResourceLocation;)Lnet/minecraft/client/renderer/RenderType;' for i in b))
            self.assertNotIn((entry,'getRenderer'),declared)
            self.assertNotIn((entry,'getDefaultBakedModel'),declared)

    def test_texture_is_static_or_exact_existing_string_query_not_a_payload(self):
        kinds=[]
        for layer in self.b['native_glow_layers']:
            source=layer['texture_source'];kinds.append(source['kind'])
            if source['kind']=='NATIVE_STATIC_TEXTURE':
                b=self.method(layer['entry'],'<clinit>')['instructions']
                self.assertEqual([i['opcode'] for i in b],['0x12','0xb8','0xb3','0xb1'])
                self.assertEqual(b[0]['operand'],source['value'])
                self.assertEqual(b[2]['operand'],layer['entry'][:-6]+'.LAYERLnet/minecraft/resources/ResourceLocation;')
            else:
                m=self.method(layer['entry'],'getLayer');b=m['instructions']
                self.assertFalse(any(i['opcode'] in ('0xb3','0xb5') for i in b))
                self.assertEqual([i['operand'] for i in b if i['opcode'] in ('0x12','0x13')],['glowTexture',source['empty_or_null_fallback']])
                self.assertTrue(any(i['opcode']=='0xc6' for i in b))
                self.assertTrue(any('.isEmpty()Z' in str(i['operand']) for i in b))
                boots=[x for x in self.c['registration_bootstraps'] if x['entry']==layer['entry']]
                self.assertEqual(len(boots),1)
                self.assertIn('StringConcatFactory.makeConcatWithConstants',str(boots[0]['handle']))
                self.assertEqual(boots[0]['arguments'][0],source['recipe'])
        self.assertEqual(kinds.count('NATIVE_STATIC_TEXTURE'),44)
        self.assertEqual(kinds.count('NATIVE_PERSISTENT_STRING_TEXTURE_QUERY'),5)

    def test_optional_native_lookup_and_actual_zero_argument_getter_are_distinct(self):
        for pose in self.b['native_optional_pose_context']:
            entry=pose['entry'];init=self.method(entry,'<clinit>')
            strings=[i['operand'] for i in init['instructions'] if i['opcode'] in ('0x12','0x13')]
            self.assertTrue(all(s in strings for s in pose['class_lookups']+pose['native_method_lookups']))
            b=self.method(entry,'getOrientationObject')['instructions']
            self.assertEqual([i['operand'] for i in b if i['opcode']=='0xb2'],[entry[:-6]+'.getOrientationMethodLjava/lang/reflect/Method;']*2)
            at=next(n for n,i in enumerate(b) if '.invoke(' in str(i['operand']))
            self.assertEqual([i['opcode'] for i in b[at-3:at]],['0x2b','0x3','0xbd'])
            self.assertEqual(b[at-1]['operand'],'java/lang/Object')
            self.assertFalse(any('.getRenderOrientationMethod' in u['operand'] and u['opcode'] in ('0xb2','0xb4') for u in pose['renderer_only_field_context']))

    def test_pose_writes_preserve_entity_rotation_and_original_fallback(self):
        for pose in self.b['native_optional_pose_context']:
            entry=pose['entry'];m=self.method(entry,'tryNyfsRotation');b=m['instructions']
            self.assertEqual({i['operand'] for i in b if i['opcode'] in ('0xb3','0xb5')},{entry[:-6]+'.debugYawF'})
            self.assertEqual({h['catch_type'] for h in m['exception_handlers']},{'java/lang/Exception'})
            self.assertEqual(len({h['handler'] for h in m['exception_handlers']}),1)
            for mutator in ('.setYRot(','.setXRot(','.setDeltaMovement(','.hurt(','.addEffect(','.putDouble('):
                self.assertFalse(any(mutator in str(i['operand']) for i in b))
            self.assertEqual(sum('.mulPose(' in str(i['operand']) for i in b),1)
            self.assertEqual(sum('PoseStack.translate(' in str(i['operand']) for i in b),2)
            self.assertEqual([i['opcode'] for i in b[-2:]],['0x3','0xac'])
            self.assertEqual({h['catch_type'] for h in self.method(entry,'<clinit>')['exception_handlers']},
                             {'java/lang/NoSuchMethodException','java/lang/ClassNotFoundException'})
            self.assertEqual([i['opcode'] for i in self.method(entry,'applyRotations')['instructions']],['0xb1'])

    def test_renderer_scale_and_gate_values_are_not_entity_or_stage_writes(self):
        for pose in self.b['native_optional_pose_context']:
            entry=pose['entry'];b=self.method(entry,'preRender')['instructions']
            self.assertEqual({i['operand'] for i in b if i['opcode'] in ('0xb3','0xb5')},
                             {entry[:-6]+'.scaleHeightF',entry[:-6]+'.scaleWidthF'})
            self.assertEqual([i.get('local_index') for i in b[-13:-2]],list(range(11)))
            self.assertTrue(b[-2]['operand'].startswith('software/bernie/geckolib/renderer/GeoEntityRenderer.preRender('))
            b=self.method(entry,'isOnCeiling')['instructions']
            self.assertEqual([i['operand'] for i in b if i['opcode']=='0x14'],[-0.9200000166893005])
            self.assertFalse(any(i['opcode'] in ('0xb3','0xb5') for i in b))
        for p in self.b['native_render_admission_context']:
            self.assertEqual([i['opcode'] for i in self.method(p['entry'],'shouldRender')['instructions']],['0x4','0xac'])

    def test_missing_native_root_or_changed_method_hash_cannot_close_a_bridge(self):
        r=read_json(OUT/'mod-reviews/arphex.json')
        r['reviewed_batches']=[f for f in r['reviewed_batches'] if f!='arphex-r2m7k-native-scene-context.json']
        b=copy.deepcopy(self.b);b['exclusions']=[]
        with self.assertRaisesRegex(AssertionError,'target lacks prior'):validate_batch(b,r,self.c)
        r['reviewed_batches'].append('arphex-r2m7k-native-scene-context.json')
        e=copy.deepcopy(self.e);e['witnesses'][0]['methods'][0]['code_sha256']='0'*64
        def read(path):
            return e if str(path.relative_to(OUT))=='native-evidence/arphex-native-scene-context.json' else read_json(path)
        with self.assertRaisesRegex(AssertionError,'hash mismatch'):reconcile(r,self.c,read=read)


if __name__=='__main__':unittest.main()
