"""Native String/bone targets and mutations distinguish models from gameplay."""
import copy
import tempfile
import unittest
from pathlib import Path
from collections import Counter
from catalog_common import OUT,read_json
from native_forwarding import forwarding_shape,validate,write_registry
from native_model_shapes import validate_context,G
from reconcile_native_census import reconcile
from promote_combat_batch import validate_batch


class NativeModelContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d=read_json(OUT/'arphex-native-model-context-registry.json')
        cls.c=read_json(OUT/'arphex-combat-census.json')
        cls.batch=read_json(OUT/'arphex-r2m7h-native-model-context.json')

    def example(self,kind):
        r=next(r for r in self.d['rows'] if r['kind']==kind)
        return r,copy.deepcopy(self.d['instruction_templates'][r['instruction_template']])

    def shape(self,r,b,bootstraps=None,parent=None):
        return forwarding_shape(r['entry'],r['method'],r['descriptor'],r['access'],b,
            bootstraps=r.get('bootstraps',{}) if bootstraps is None else bootstraps,superclass=parent or r.get('superclass'))

    def test_all_remaining_model_methods_have_exact_context_without_new_semantics(self):
        review=read_json(OUT/'mod-reviews/arphex.json')
        review['reviewed_batches']=[f for f in review['reviewed_batches'] if f!='arphex-r2m7h-native-model-context.json']
        before,_=reconcile(review,self.c)
        rows=validate(self.d,self.c,{(m['entry'],m['method'],m['descriptor']) for m in before['methods']})
        self.assertEqual(Counter(r['kind'] for r in rows),{'EXACT_GECKO_MODEL_PARENT_CONSTRUCTION':128,
            'EXACT_GECKO_DYNAMIC_TEXTURE_QUERY':127,'EXACT_GECKO_SYNCED_STRING_ASSET_QUERY':6,
            'EXACT_GECKO_MODEL_BONE_ROTATION':51,'EXACT_COMPILER_BRIDGE':184})
        self.assertEqual(self.batch['effects'],[]);self.assertEqual(self.batch['paths'],[])
        self.assertEqual(validate_batch(self.batch,review,self.c)['semantic_records'],len(review['effects']))

    def test_texture_query_cannot_hide_payload_or_an_uncalled_unreviewed_getter(self):
        r,b=self.example('EXACT_GECKO_DYNAMIC_TEXTURE_QUERY')
        self.assertIsNotNone(self.shape(r,b))
        for index,field,value in [(0,'local_index',0),(1,'operand','example/Actor.damage()Ljava/lang/String;')]:
            bad=copy.deepcopy(b);bad[index][field]=value;self.assertIsNone(self.shape(r,bad))
        boots=copy.deepcopy(r['bootstraps']);next(iter(boots.values()))['handle']['value']='example/Damage.bootstrap()V'
        self.assertIsNone(self.shape(r,b,boots))
        d=copy.deepcopy(self.d);d['rows']=[copy.deepcopy(r)]
        d['instruction_templates']={r['instruction_template']:d['instruction_templates'][r['instruction_template']]}
        d['summary']=dict(methods=1,counts_by_kind={r['kind']:1})
        with self.assertRaisesRegex(AssertionError,'target lacks prior'):validate(d,self.c,set())

    def test_bone_rotation_does_not_become_physical_entity_rotation_or_attack(self):
        r,b=self.example('EXACT_GECKO_MODEL_BONE_ROTATION')
        for value in ('net/minecraft/world/entity/Entity.setYRot(F)V','example/Combat.damage(F)V'):
            bad=copy.deepcopy(b);next(i for i in bad if '.setRotY(' in str(i['operand']))['operand']=value
            self.assertIsNone(self.shape(r,bad))
        bad=copy.deepcopy(b);next(i for i in bad if i.get('local_index')==4)['local_index']=1
        self.assertIsNone(self.shape(r,bad))
        self.assertFalse(any(i['opcode'] in ('0xb3','0xb5') for i in b))

    def test_reskin_selectors_preserve_separate_paths_fallbacks_and_string_source(self):
        rows=[r for r in self.d['rows'] if r['kind']=='EXACT_GECKO_SYNCED_STRING_ASSET_QUERY']
        self.assertEqual(len(rows),6)
        actors={r['actor_entry'] for r in rows};self.assertEqual(len(actors),3)
        for actor in actors:
            pair=[r for r in rows if r['actor_entry']==actor]
            self.assertEqual({r['asset_recipe'] for r in pair},{'animations/\x01.animation.json','geo/\x01.geo.json'})
            self.assertEqual(pair[0]['string_accessor'],pair[1]['string_accessor'])
            self.assertEqual(pair[0]['fallback_asset_name'],pair[1]['fallback_asset_name'])
            self.assertTrue(all(r['asset_namespace']=='arphex' for r in pair))
            for r in pair:
                b=self.d['instruction_templates'][r['instruction_template']]
                self.assertTrue(any(i['opcode']=='0xc6' for i in b));self.assertTrue(any('String.isEmpty' in str(i['operand']) for i in b))
                self.assertFalse(any(i['opcode'] in ('0xb3','0xb5') for i in b))

    def test_authored_model_override_and_constructor_extra_effects_fail(self):
        r,b=self.example('EXACT_GECKO_MODEL_BONE_ROTATION');c=copy.deepcopy(self.c)
        name,desc=r['inherited_query'].split('(',1);c['methods'].append(dict(method=name,descriptor='('+desc))
        with self.assertRaisesRegex(AssertionError,'override needs review'):validate_context(r,r['entry'],c)
        r,b=self.example('EXACT_GECKO_MODEL_PARENT_CONSTRUCTION')
        self.assertIsNotNone(self.shape(r,b));self.assertIsNone(self.shape(r,b,parent='example/Combat'))
        b.insert(1,dict(offset=1,opcode='0xb8',operand='example/Combat.spawn()V'))
        self.assertIsNone(self.shape(r,b))

    def test_deterministic_compact_output_is_lossless(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'model.json';write_registry(p,self.d,compact=True)
            self.assertEqual(read_json(p),self.d)
            self.assertEqual(p.read_bytes(),(OUT/'arphex-native-model-context-registry.json').read_bytes())


if __name__=='__main__':unittest.main()
