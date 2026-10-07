"""Typed native particle effects, target coverage and actual client registration."""
import copy
import tempfile
import unittest
from pathlib import Path
from collections import Counter
from catalog_common import OUT,read_json
from native_forwarding import forwarding_shape,validate,write_registry
from native_particle_shapes import validate_context,P,CTOR
from reconcile_native_census import reconcile
from promote_combat_batch import validate_batch


class NativeParticleContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d=read_json(OUT/'arphex-native-particle-context-registry.json')
        cls.c=read_json(OUT/'arphex-combat-census.json')
        cls.batch=read_json(OUT/'arphex-r2m7g-native-particle-context.json')
        cls.e=read_json(OUT/'native-evidence/arphex-native-particle-context.json')

    def example(self,kind):
        r=next(r for r in self.d['rows'] if r['kind']==kind)
        return r,copy.deepcopy(self.d['instruction_templates'][r['instruction_template']])

    def shape(self,r,b,parent=None):
        return forwarding_shape(r['entry'],r['method'],r['descriptor'],r['access'],b,superclass=parent or r.get('superclass'))

    def test_only_typed_client_context_is_closed_and_no_candidate_is_added(self):
        review=read_json(OUT/'mod-reviews/arphex.json')
        review['reviewed_batches']=[f for f in review['reviewed_batches'] if f!='arphex-r2m7g-native-particle-context.json']
        before,_=reconcile(review,self.c)
        rows=validate(self.d,self.c,{(m['entry'],m['method'],m['descriptor']) for m in before['methods']})
        self.assertEqual(len(rows),439)
        counts=Counter(r['kind'] for r in rows)
        self.assertEqual(counts['EXACT_NATIVE_CLIENT_PARTICLE_CONSTRUCTION'],60)
        self.assertEqual(counts['EXACT_NATIVE_CLIENT_PARTICLE_FACTORY'],60)
        self.assertEqual(counts['EXACT_NATIVE_PARTICLE_ROLL_TICK'],13)
        self.assertEqual(self.batch['effects'],[]);self.assertEqual(self.batch['paths'],[])
        self.assertEqual(validate_batch(self.batch,review,self.c)['semantic_records'],len(review['effects']))

    def test_particle_name_cannot_hide_entity_damage_or_actor_motion(self):
        r,b=self.example('EXACT_NATIVE_CLIENT_PARTICLE_CONSTRUCTION')
        self.assertIsNotNone(self.shape(r,b));self.assertIsNone(self.shape(r,b,'example/Monster'))
        for opcode,operand in [('0xb6','net/minecraft/world/entity/Entity.hurt()Z'),
                               ('0xb5','example/Entity.healthF'),('0xb8','example/Combat.execute()V'),
                               ('0xb6','net/minecraft/world/entity/Entity.setDeltaMovement()V')]:
            bad=copy.deepcopy(b);bad.insert(6,dict(offset=10,opcode=opcode,operand=operand))
            self.assertIsNone(self.shape(r,bad))
        c=copy.deepcopy(self.c);c['methods'].append(dict(method='setSize',descriptor='(FF)V'))
        with self.assertRaisesRegex(AssertionError,'setter requires separate'):validate_context(r,r['entry'],c)

    def test_visual_roll_remains_separate_from_damage_and_native_entity_yaw(self):
        r,b=self.example('EXACT_NATIVE_PARTICLE_ROLL_TICK')
        self.assertIsNotNone(self.shape(r,b))
        for field in ('example/Entity.yRotF',r['entry'][:-6]+'.damageF'):
            bad=copy.deepcopy(b);next(i for i in bad if i['opcode']=='0xb5')['operand']=field
            self.assertIsNone(self.shape(r,bad))
        self.assertEqual(b[1]['operand'],P+'TextureSheetParticle.tick()V')

    def test_factories_require_exact_arguments_and_independent_constructor_coverage(self):
        r,b=self.example('EXACT_NATIVE_CLIENT_PARTICLE_FACTORY')
        bad=copy.deepcopy(b);bad[2]['local_index']=0;self.assertIsNone(self.shape(r,bad))
        c=copy.deepcopy(self.c);next(c for c in c['classes'] if c['entry']==r['target']['entry'])['superclass']='example/HazardEntity'
        with self.assertRaises(AssertionError):validate_context(r,r['entry'],c)
        d=copy.deepcopy(self.d);d['rows']=[copy.deepcopy(r)]
        d['instruction_templates']={r['instruction_template']:d['instruction_templates'][r['instruction_template']]}
        d['summary']=dict(methods=1,counts_by_kind={r['kind']:1})
        with self.assertRaisesRegex(AssertionError,'target lacks prior'):validate(d,self.c,set())

    def test_native_client_event_and_every_real_bootstrap_binding(self):
        w=self.e['witnesses'][0];m=w['methods'][0];body=m['instructions']
        annotation=next(a for a in w['annotations'] if a['descriptor'].endswith('/EventBusSubscriber;'))
        self.assertEqual(annotation['values']['bus']['constant'],'MOD')
        self.assertEqual(annotation['values']['value'][0]['constant'],'CLIENT')
        self.assertTrue(any(a['descriptor'].endswith('/SubscribeEvent;') for a in m['annotations']))
        bootstraps={b['index']:b for b in self.c['registration_bootstraps'] if b['entry']==w['entry']}
        registry={(r['entry'],r['method'],r['descriptor']):r for r in self.d['rows']}
        bindings=self.batch['native_particle_registrations'];self.assertEqual(len(bindings),60)
        self.assertEqual({b['event_offset'] for b in bindings},{i['offset'] for i in body if '.registerSpriteSet(' in str(i['operand'])})
        for b in bindings:
            at=next(j for j,i in enumerate(body) if i['offset']==b['event_offset'])
            self.assertEqual([i['opcode'] for i in body[at-5:at+1]],['0x2a','0xb2','0xb6','0xc0','0xba','0xb6'])
            self.assertEqual(body[at-5]['local_index'],0)
            self.assertEqual(body[at-4]['operand'],b['particle_type_holder'])
            native=bootstraps[b['bootstrap_index']];p=b['provider']
            self.assertEqual(native['arguments'][1],p['entry'][:-6]+'.'+p['method']+p['descriptor'])
            self.assertEqual(native['handle'],b['native_bootstrap']['handle']['value'])
            self.assertEqual(b['native_bootstrap']['arguments'][1]['reference_kind'],6)
            self.assertEqual(registry[(p['entry'],p['method'],p['descriptor'])]['kind'],'EXACT_NATIVE_PARTICLE_PROVIDER_FACTORY')

    def test_compact_registry_is_deterministic_and_lossless(self):
        with tempfile.TemporaryDirectory() as d:
            a=Path(d)/'a.json';b=Path(d)/'b.json'
            write_registry(a,self.d,compact=True);write_registry(b,self.d,compact=True)
            self.assertEqual(a.read_bytes(),b.read_bytes())
            self.assertEqual(a.read_bytes(),(OUT/'arphex-native-particle-context-registry.json').read_bytes())
            self.assertEqual(read_json(a),self.d)


if __name__=='__main__':unittest.main()
