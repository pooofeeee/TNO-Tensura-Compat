"""Native invocation roots/event annotations must override any exclusion label."""
import copy
import unittest
from catalog_common import OUT,read_json
from native_uncalled import native_references,validate
from reconcile_native_census import reconcile


class UncalledProcedureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.census=read_json(OUT/'arphex-combat-census.json')
        cls.document=read_json(OUT/'arphex-native-uncalled-overloads-registry.json')
        cls.evidence=read_json(OUT/cls.document['evidence_file'])

    def test_exact_selected_static_overloads_have_no_native_invocation_root(self):
        self.assertEqual(len(validate(self.document,self.census,self.evidence)),31)
        self.assertTrue(any(r['class_annotations'] for r in self.document['rows']))
        self.assertEqual(self.document['summary']['class_wide_exclusions'],0)
        self.assertEqual(self.document['summary']['new_numeric_parameters'],0)

    def test_a_new_direct_native_caller_invalidates_old_absence_receipt(self):
        c=copy.deepcopy(self.census);r=self.document['rows'][0]
        symbol=r['entry'][:-6]+'.'+r['method']+r['descriptor']
        c['symbols'].append(symbol)
        c['methods'][0]['calls'].append([0,184,len(c['symbols'])-1])
        with self.assertRaisesRegex(AssertionError,'Native invocation root'):
            validate(self.document,c,self.evidence)

    def test_native_bootstrap_target_is_an_invocation_root(self):
        c=copy.deepcopy(self.census);r=self.document['rows'][0]
        symbol=r['entry'][:-6]+'.'+r['method']+r['descriptor']
        c['registration_bootstraps'].append(dict(entry='example/Registered.class',index=0,handle='external/factory',arguments=[symbol]))
        with self.assertRaisesRegex(AssertionError,'Native invocation root'):
            validate(self.document,c,self.evidence)

    def test_subscribed_method_cannot_be_dispositioned_even_without_direct_call(self):
        e=copy.deepcopy(self.evidence);e['witnesses'][0]['methods'][0]['annotations']=[dict(descriptor='Lnet/neoforged/bus/api/SubscribeEvent;',values={})]
        with self.assertRaisesRegex(AssertionError,'Annotated native handler'):
            validate(self.document,self.census,e)

    def test_instance_engine_callback_cannot_borrow_static_absence_proof(self):
        c=copy.deepcopy(self.census);d=copy.deepcopy(self.document);r=d['rows'][0]
        method=next(m for m in c['methods'] if (m['entry'],m['method'],m['descriptor'])==(r['entry'],r['method'],r['descriptor']))
        method['access']&=~8;r['access']=method['access']
        with self.assertRaisesRegex(AssertionError,'explicit static procedure'):
            validate(d,c,self.evidence)

    def test_other_subscriber_methods_and_overloads_remain_independent(self):
        review=read_json(OUT/'mod-reviews/arphex.json')
        batch='arphex-r2m6z-native-model-and-inactive-contexts.json'
        if batch not in review['reviewed_batches']:review['reviewed_batches'].append(batch)
        index,pending=reconcile(review,self.census)
        chosen={(r['entry'],r['method'],r['descriptor']) for r in self.document['rows']}
        self.assertTrue(chosen<={(r['entry'],r['method'],r['descriptor']) for r in index['methods']})
        self.assertTrue(any(r['entry']=='net/arphex/procedures/RenderTest9SkyProcedure.class' and r['method']=='skySetup' for r in pending))
        self.assertTrue(all(r['method']=='execute' for r in self.document['rows']))

    def test_batch_cannot_omit_duplicate_or_extend_the_selected_absence_proof(self):
        from native_uncalled import validate_batch
        batch=read_json(OUT/'arphex-r2m6z-native-model-and-inactive-contexts.json')
        read=lambda name: read_json(OUT/name)
        validate_batch(batch,self.census,read)
        for mutation in ('omit','duplicate','extend'):
            b=copy.deepcopy(batch)
            if mutation=='omit':b['exclusions'].pop()
            elif mutation=='duplicate':b['exclusions'].append(b['exclusions'][0])
            else:b['exclusions'][0]['implementation'][0]['methods'].append('unprovedEventHandler')
            with self.assertRaises(AssertionError):validate_batch(b,self.census,read)


if __name__=='__main__':unittest.main()
