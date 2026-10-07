"""Native query/placement/helper facts, separately from generated counts."""
import copy
import unittest
from catalog_common import OUT,read_json
from native_forwarding import validate
from promote_combat_batch import validate_batch,refined_review
from test_shadow_clone_contracts import NativeContractHarness


class NativeQueryContextTests(NativeContractHarness,unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch=read_json(OUT/'arphex-r2m7c-native-query-context.json')
        cls.native=read_json(OUT/'native-evidence/arphex-native-query-context.json')
        cls.global_native=read_json(OUT/'native-evidence/arphex-global-hooks.json')
        cls.census=read_json(OUT/'arphex-combat-census.json')

    def dweller(self,n):
        w=next(w for w in self.global_native['witnesses'] if w['entry']=='net/arphex/procedures/DwellerLifestealProcedure.class')
        return next(m['instructions'] for m in w['methods'] if m['name']=='lambda$execute$'+str(n))

    def test_no_new_records_or_numeric_aliases(self):
        prior=self.prior();after=refined_review(prior,self.batch)
        summary=validate_batch(self.batch,prior,self.census)
        self.assertEqual((summary['semantic_records'],summary['numeric_candidate_entries']),(462,3903))
        self.assertFalse(self.batch['effects']);self.assertFalse(self.batch['paths'])
        self.assertEqual([r['scalable_parameter_candidates'] for r in prior['effects']],
                         [r['scalable_parameter_candidates'] for r in after['effects']])

    def test_deferred_immunity_literals_and_current_config_are_not_new_magnitudes(self):
        for n,profile in [(7,[7,0]),(8,[7,5]),(13,[20,0]),(14,[10,0]),(15,[15,0]),(16,[40,0]),(18,[10,0])]:
            b=self.dweller(n);at=next(j for j,i in enumerate(b) if 'MobEffectInstance.<init>(' in str(i['operand']))
            self.assertEqual([i['operand'] for i in b[at-4:at-2]],profile)
            self.assertIn('INVINCIBILITY_TEMP',b[at-5]['operand'])
            self.assertEqual(b[at+2]['opcode'],'0x57')
        for n in (29,65):
            self.assertTrue(any('TORMENTOR_HIT_SPEED' in str(i['operand']) for i in self.dweller(n)))
        self.assertTrue(any('.hasEffect(' in str(i['operand']) for i in self.dweller(65)))
        self.assertFalse(any('.hasEffect(' in str(i['operand']) for i in self.dweller(29)))
        b=self.dweller(66);remove=next(i['offset'] for i in b if '.removeEffect(' in str(i['operand']))
        hurt=next(j for j,i in enumerate(b) if '.hurt(' in str(i['operand']))
        self.assertLess(remove,b[hurt]['offset']);self.assertEqual(b[hurt-1]['operand'],50.0)
        self.assertEqual(b[hurt+1]['opcode'],'0x57')
        self.assertTrue(any('DamageSource.<init>(Lnet/minecraft/core/Holder;Lnet/minecraft/world/entity/Entity;)V' in str(i['operand']) for i in b))

    def test_visual_lightning_is_explicitly_visual_and_other_leaves_have_no_payload(self):
        for n in (9,10,11):
            b=self.dweller(n);at=next(j for j,i in enumerate(b) if '.setVisualOnly(' in str(i['operand']))
            self.assertEqual(b[at-1]['operand'],1)
            self.assertLess(b[at]['offset'],next(i['offset'] for i in b if '.addFreshEntity(' in str(i['operand'])))
        for n in (0,1,6,9,10,11,30,40):
            self.assertFalse(any(t in str(i['operand']) for i in self.dweller(n) for t in
                                 ('.hurt(','.setHealth(','.heal(','.addEffect(','.setDeltaMovement(')))
        self.assertEqual(self.dweller(101)[1]['operand'],'playertrackfortp')
        self.assertEqual(self.dweller(102)[1]['operand'],'fiveseconds')
        self.assertEqual(self.dweller(102)[2]['operand'],100.0)
        self.assertEqual(self.dweller(103)[1]['operand'],'trackfortp')

    def test_placement_dispatch_and_clone_bindings_preserve_real_predicates(self):
        b=self.body('ArphexModEntities','init')
        self.assertEqual([i['operand'] for i in b if i['opcode']=='0xb8'],self.batch['native_spawn_dispatch'])
        self.assertEqual(len(self.batch['native_spawn_dispatch']),146)
        self.assertEqual(len(set(self.batch['native_spawn_dispatch'])),146)
        self.assertEqual(b[-1]['opcode'],'0xb1')
        for s in self.batch['native_placement_bindings']:
            name=s['entry'].rsplit('/',1)[-1][:-6];b=self.body(name,'init')
            self.assertTrue(any('SpawnPlacementTypes.ON_GROUND' in str(i['operand']) for i in b))
            self.assertTrue(any('MOTION_BLOCKING_NO_LEAVES' in str(i['operand']) for i in b))
            self.assertTrue(any('Operation.REPLACE' in str(i['operand']) for i in b))
            pred=self.body(name,'lambda$init$0')
            calls=[i['operand'] for i in pred if i['opcode']=='0xb8']
            self.assertEqual(calls,[s['shared_predicate']]);self.assertTrue(s['existing_predicate_records'])
            self.assertEqual(s['predicate_bootstrap']['arguments'][1]['reference_kind'],6)
            self.assertTrue(s['predicate_bootstrap']['arguments'][1]['value'].startswith('SELF.lambda$init$0('))

    def test_exact_query_registry_rejects_changed_native_identity(self):
        r=read_json(OUT/self.batch['native_forwarding_registry_file'])
        self.assertEqual(len(validate(r,self.census,set())),97)
        for field in ('code_sha256','entry_sha256'):
            bad=copy.deepcopy(r);bad['rows'][0][field]='0'*64
            with self.assertRaises(AssertionError):validate(bad,self.census,set())


if __name__=='__main__':unittest.main()
