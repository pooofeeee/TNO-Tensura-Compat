"""Native-effect/consumer/target mutations, not callback-name assertions."""
import copy
import unittest
from collections import Counter
from catalog_common import OUT,read_json,byte_hash
from native_forwarding import forwarding_shape,validate
from native_animation_shapes import validate_context
from reconcile_native_census import reconcile
from promote_combat_batch import validate_batch


class NativeAnimationShapeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document=read_json(OUT/'arphex-native-animation-callbacks-registry.json')
        cls.census=read_json(OUT/'arphex-combat-census.json')
        cls.fields=read_json(OUT/'arphex-native-field-use-index.json')
        cls.review=read_json(OUT/'mod-reviews/arphex.json')
        cls.batch=read_json(OUT/'arphex-r2m7f-native-animation-callbacks.json')

    def example(self,kind):
        r=next(r for r in self.document['rows'] if r['kind']==kind)
        return r,copy.deepcopy(self.document['instruction_templates'][r['instruction_template']])

    def shape(self,r,body,bootstraps=None):
        return forwarding_shape(r['entry'],r['method'],r['descriptor'],r['access'],body,
                                bootstraps=r.get('bootstraps',{}) if bootstraps is None else bootstraps,superclass=r['superclass'])

    def test_only_context_methods_close_and_existing_semantics_are_unchanged(self):
        self.assertEqual(self.batch['effects'],[]);self.assertEqual(self.batch['paths'],[])
        before=copy.deepcopy(self.review)
        before['reviewed_batches']=[f for f in before['reviewed_batches'] if f!='arphex-r2m7f-native-animation-callbacks.json']
        prior,_=reconcile(before,self.census)
        rows=validate(self.document,self.census,{(m['entry'],m['method'],m['descriptor']) for m in prior['methods']},self.fields)
        self.assertEqual(Counter(r['kind'] for r in rows),{'EXACT_GECKO_MOVEMENT_CLIP_SELECTION':122,
            'EXACT_GECKO_ATTACK_ANIMATION_CONTEXT':57,'EXACT_GECKO_CONTROLLER_REGISTRATION':123,
            'EXACT_NATIVE_SYNCED_ANIMATION_STRING_TRANSPORT':116,'EXACT_GECKO_ITEM_IDLE_CLIP_CONTEXT':1})
        self.assertEqual(validate_batch(self.batch,before,self.census)['semantic_records'],len(before['effects']))
        self.assertTrue(all(r['method']!='procedurePredicate' for r in rows))

    def test_movement_cannot_hide_authored_payload_or_actor_write(self):
        r,b=self.example('EXACT_GECKO_MOVEMENT_CLIP_SELECTION')
        self.assertIsNotNone(self.shape(r,b))
        for opcode,operand in [('0xb6',r['entry'][:-6]+'.hurt()Z'),('0xb5',r['entry'][:-6]+'.healthF'),
                               ('0xb8','example/Commands.run()V'),('0xbb','example/Projectile')]:
            bad=copy.deepcopy(b);bad.insert(0,dict(offset=0,opcode=opcode,operand=operand))
            self.assertIsNone(self.shape(r,bad))

    def test_unreviewed_query_override_and_arbitrary_bootstrap_fail(self):
        r=next(r for r in self.document['rows'] if r.get('inherited_queries'))
        bad=copy.deepcopy(self.census);query=r['inherited_queries'][0];name,desc=query.split('(',1)
        bad['methods'].append(dict(entry='example/Actor.class',method=name,descriptor='('+desc))
        with self.assertRaisesRegex(AssertionError,'query override'):validate_context(r,r['entry'],bad,self.fields)
        r=next(r for r in self.document['rows'] if r['kind']=='EXACT_GECKO_MOVEMENT_CLIP_SELECTION' and r.get('bootstraps'))
        b=copy.deepcopy(self.document['instruction_templates'][r['instruction_template']]);boots=copy.deepcopy(r['bootstraps'])
        next(iter(boots.values()))['handle']['value']='example/Payload.bootstrap()V'
        self.assertIsNone(self.shape(r,b,boots))

    def test_attack_fields_are_own_private_context_not_parent_or_gameplay(self):
        r,b=self.example('EXACT_GECKO_ATTACK_ANIMATION_CONTEXT');self.assertIsNotNone(self.shape(r,b))
        bad=copy.deepcopy(b);next(i for i in bad if i['opcode']=='0xb5')['operand']='net/minecraft/world/entity/LivingEntity.swingingZ'
        self.assertIsNone(self.shape(r,bad))
        bad=copy.deepcopy(b);next(i for i in bad if i['opcode']=='0xb5')['operand']=r['entry'][:-6]+'.attackClockJ'
        self.assertIsNone(self.shape(r,bad))
        fields=copy.deepcopy(self.fields);symbol=fields['symbols'].index(r['animation_only_fields'][0])
        fields['methods'].append(dict(entry=r['entry'],method='actualDamageTick',descriptor='()V',field_sites=[[0,180,symbol]]))
        with self.assertRaisesRegex(AssertionError,'Gameplay field consumer'):validate_context(r,r['entry'],self.census,fields)
        census=copy.deepcopy(self.census)
        c=next(c for c in census['classes'] if c['entry']==r['entry']);c['fields']=[f for f in c['fields'] if f['name'] not in ('swinging','lastSwing')]
        with self.assertRaisesRegex(AssertionError,'declared on actor'):validate_context(r,r['entry'],census,self.fields)

    def test_registrar_cannot_close_from_capture_or_wrong_handler_type(self):
        r,b=self.example('EXACT_GECKO_CONTROLLER_REGISTRATION')
        boots=copy.deepcopy(r['bootstraps']);next(iter(boots.values()))['arguments'][1]['reference_kind']=6
        self.assertIsNone(self.shape(r,b,boots))
        d=copy.deepcopy(self.document);d['rows']=[copy.deepcopy(r)]
        d['instruction_templates']={r['instruction_template']:d['instruction_templates'][r['instruction_template']]}
        d['summary']=dict(methods=1,counts_by_kind={r['kind']:1})
        with self.assertRaisesRegex(AssertionError,'target lacks prior'):validate(d,self.census,set(),self.fields)

    def test_synced_transport_cannot_write_another_actor_or_hide_update_callback(self):
        r,b=self.example('EXACT_NATIVE_SYNCED_ANIMATION_STRING_TRANSPORT')
        bad=copy.deepcopy(b);bad[2]['operand']='example/Other.ANIMATIONLnet/minecraft/network/syncher/EntityDataAccessor;'
        self.assertIsNone(self.shape(r,bad))
        census=copy.deepcopy(self.census);census['methods'].append(dict(method='onSyncedDataUpdated',descriptor='()V'))
        with self.assertRaisesRegex(AssertionError,'synced-data callback'):validate_context(r,r['entry'],census,self.fields)

    def test_pinned_field_index_cannot_change_silently(self):
        bad=copy.deepcopy(self.fields);bad['methods'].pop()
        with self.assertRaisesRegex(AssertionError,'field-consumer evidence'):validate(self.document,self.census,set(),bad)


if __name__=='__main__':unittest.main()
