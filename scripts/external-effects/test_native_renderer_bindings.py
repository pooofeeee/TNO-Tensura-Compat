"""Actual constructor/model dependencies and exact draw fields/arguments."""
import copy
import tempfile
import unittest
from pathlib import Path
from collections import Counter
from catalog_common import OUT,read_json
from native_forwarding import forwarding_shape,validate,write_registry
from native_renderer_shapes import bind_context,validate_context,CTX
from reconcile_native_census import reconcile
from promote_combat_batch import validate_batch


class NativeRendererBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d=read_json(OUT/'arphex-native-renderer-bindings-registry.json')
        cls.c=read_json(OUT/'arphex-combat-census.json')
        cls.batch=read_json(OUT/'arphex-r2m7i-native-renderer-bindings.json')

    def example(self,kind):
        r=next(r for r in self.d['rows'] if r['kind']==kind)
        return r,copy.deepcopy(self.d['instruction_templates'][r['instruction_template']])

    def shape(self,r,b):
        return forwarding_shape(r['entry'],r['method'],r['descriptor'],r['access'],b,superclass=r.get('superclass'))

    def test_context_coverage_preserves_semantics_and_leaves_computed_readers_pending(self):
        review=read_json(OUT/'mod-reviews/arphex.json')
        review['reviewed_batches']=[f for f in review['reviewed_batches'] if f!='arphex-r2m7i-native-renderer-bindings.json']
        before,_=reconcile(review,self.c)
        rows=validate(self.d,self.c,{(m['entry'],m['method'],m['descriptor']) for m in before['methods']})
        self.assertEqual(Counter(r['kind'] for r in rows),{'EXACT_GECKO_RENDERER_CONSTRUCTION':127,
            'EXACT_GECKO_RENDER_LAYER_PARENT_CONSTRUCTION':49,'EXACT_GECKO_RENDERER_TEXTURE_TYPE_QUERY':127,
            'EXACT_GECKO_LITERAL_RENDER_SCALE':80,'EXACT_COMPILER_BRIDGE':414})
        self.assertEqual(self.batch['effects'],[]);self.assertEqual(self.batch['paths'],[])
        self.assertEqual(validate_batch(self.batch,review,self.c)['semantic_records'],len(review['effects']))
        for r in rows:
            b=self.d['instruction_templates'][r['instruction_template']]
            self.assertFalse(any('.tryNyfsRotation(' in str(i['operand']) or '.execute(' in str(i['operand']) for i in b))

    def test_constructor_keeps_native_model_and_layers_not_world_entities(self):
        r,b=self.example('EXACT_GECKO_RENDERER_CONSTRUCTION')
        self.assertIsNotNone(self.shape(r,b))
        bad=copy.deepcopy(b);next(i for i in bad if i['opcode']=='0xb5')['operand']='example/Entity.damageF'
        self.assertIsNone(self.shape(r,bad))
        bad=copy.deepcopy(b);bad.insert(6,dict(offset=12,opcode='0xb8',operand='example/World.spawn()V'))
        self.assertIsNone(self.shape(r,bad))
        c=copy.deepcopy(self.c);next(m for m in c['classes'] if m['entry']==r['model_entry'])['superclass']='example/CombatModel'
        with self.assertRaises(AssertionError):validate_context(r,r['entry'],c)

    def test_texture_source_is_the_native_bound_model_not_name_similarity(self):
        for r in self.d['rows']:
            if r['kind']!='EXACT_GECKO_RENDERER_TEXTURE_TYPE_QUERY':continue
            shape=bind_context(self.shape(r,self.d['instruction_templates'][r['instruction_template']]),r['entry'],self.c)
            self.assertEqual(shape['model_binding'],r['model_binding'])
            self.assertEqual(shape['targets'][1]['entry'],r['model_binding']['model_entry'])
            self.assertEqual(shape['targets'][1]['descriptor'],'(L'+r['actor_entry'][:-6]+';)Lnet/minecraft/resources/ResourceLocation;')
        r,b=self.example('EXACT_GECKO_RENDERER_TEXTURE_TYPE_QUERY');c=copy.deepcopy(self.c)
        c['methods'].append(dict(entry=r['entry'],method='getTextureLocation',descriptor='(Lnet/minecraft/world/entity/Entity;)Lnet/minecraft/resources/ResourceLocation;'))
        with self.assertRaisesRegex(AssertionError,'texture dispatch'):validate_context(r,r['entry'],c)
        c=copy.deepcopy(self.c);c['classes'].append(dict(name='example/Child',superclass=r['entry'][:-6],entry='example/Child.class'))
        with self.assertRaisesRegex(AssertionError,'descendant dispatch'):validate_context(r,r['entry'],c)

    def test_captured_constructor_or_model_query_does_not_count_as_target_coverage(self):
        r,b=self.example('EXACT_GECKO_RENDERER_TEXTURE_TYPE_QUERY');d=copy.deepcopy(self.d)
        d['rows']=[copy.deepcopy(r)];d['instruction_templates']={r['instruction_template']:d['instruction_templates'][r['instruction_template']]}
        d['summary']=dict(methods=1,counts_by_kind={r['kind']:1})
        with self.assertRaisesRegex(AssertionError,'target lacks prior'):validate(d,self.c,set())
        ctor=r['targets'][0]
        with self.assertRaisesRegex(AssertionError,'target lacks prior'):validate(d,self.c,{(ctor['entry'],ctor['method'],ctor['descriptor'])})

    def test_draw_scale_does_not_write_actor_dimensions_or_reorder_parent_arguments(self):
        r,b=self.example('EXACT_GECKO_LITERAL_RENDER_SCALE')
        self.assertIsNotNone(self.shape(r,b))
        bad=copy.deepcopy(b);bad[4]['operand']='net/minecraft/world/entity/Entity.scaleHeightF';self.assertIsNone(self.shape(r,bad))
        bad=copy.deepcopy(b);bad[18]['local_index']=9;self.assertIsNone(self.shape(r,bad))
        bad=copy.deepcopy(b);bad[19]['operand']='example/Actor.resize()V';self.assertIsNone(self.shape(r,bad))

    def test_compact_context_registry_is_deterministic(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'context.json';write_registry(p,self.d,compact=True)
            self.assertEqual(read_json(p),self.d)
            self.assertEqual(p.read_bytes(),(OUT/'arphex-native-renderer-bindings-registry.json').read_bytes())


if __name__=='__main__':unittest.main()
