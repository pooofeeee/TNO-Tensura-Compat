"""Focused exact-proof indexing tests; absence of a hit never proves exclusion."""
import copy
import unittest
from pathlib import Path

from catalog_common import OUT, read_json
from reconcile_native_census import reconcile


class ExactContractIndexTests(unittest.TestCase):
    def fixture(self):
        entry = 'test/Actor.class'
        method = dict(entry=entry, method='tick', descriptor='()V',
                      code_sha256='tick-hash', disposition='CALL_GRAPH_CONTEXT')
        census = dict(mod_key='test', jar_sha256='jar',
                      classes=[dict(entry=entry, entry_sha256='class')],
                      methods=[method, dict(method, method='getState',
                                            code_sha256='getter', disposition='FIELD_ACCESS_CONTEXT'),
                               dict(method, method='bridge', code_sha256='bridge',
                                    disposition='SYNTHETIC_BRIDGE_CONTEXT')])
        packet = dict(witnesses=[dict(id='actor', entry=entry,
                                     entry_sha256='class', jar_sha256='jar',
                                     methods=[dict(name='tick', descriptor='()V', code_sha256='tick-hash'),
                                              dict(name='getState', descriptor='()V', code_sha256='getter')])])
        row = dict(id='test:actor', implementation=[dict(evidence_file='native-evidence/actor.json',
                   entry=entry, witness_id='actor', methods=['tick'])])
        return dict(effects=[row]), census, {'native-evidence/actor.json': packet}

    def run_fixture(self, review, census, files):
        return reconcile(review, census, read=lambda p: files[p.as_posix()], root=Path('.'))

    def test_capture_only_does_not_close_extra_method(self):
        review, census, files = self.fixture()
        index, pending = self.run_fixture(review, census, files)
        self.assertEqual(index['summary']['exact_contract_methods'], 1)
        self.assertEqual({m['method'] for m in pending}, {'getState', 'bridge'})
        self.assertFalse(index['whole_mod_complete'])

    def test_context_without_hit_is_still_pending(self):
        review, census, files = self.fixture()
        review['effects'] = []
        _, pending = self.run_fixture(review, census, files)
        self.assertEqual(len(pending), 3)

    def test_partial_contract_does_not_close_the_whole_native_method(self):
        review, census, files = self.fixture()
        review['effects'][0]['implementation'][0]['partial_contract'] = True
        index, pending = self.run_fixture(review, census, files)
        self.assertEqual(index['summary']['exact_contract_methods'], 0)
        self.assertEqual({m['method'] for m in pending}, {'tick', 'getState', 'bridge'})

    def test_partial_contract_still_requires_the_original_method_hash(self):
        review, census, files = self.fixture()
        review['effects'][0]['implementation'][0]['partial_contract'] = True
        files['native-evidence/actor.json']['witnesses'][0]['methods'][0]['code_sha256'] = 'wrong'
        with self.assertRaises(AssertionError):
            self.run_fixture(review, census, files)

    def test_census_method_hash_is_independent_of_canonical_claim(self):
        review, census, files = self.fixture()
        files['native-evidence/actor.json']['witnesses'][0]['methods'][0]['code_sha256'] = 'wrong'
        with self.assertRaisesRegex(AssertionError, 'Method hash mismatch'):
            self.run_fixture(review, census, files)

    def test_wrong_class_or_jar_hash_is_rejected(self):
        for field in ('entry_sha256', 'jar_sha256'):
            review, census, files = self.fixture()
            files['native-evidence/actor.json']['witnesses'][0][field] = 'wrong'
            with self.assertRaises(AssertionError):
                self.run_fixture(review, census, files)

    def test_missing_cited_method_is_rejected(self):
        review, census, files = self.fixture()
        review['effects'][0]['implementation'][0]['methods'] = ['missing']
        with self.assertRaisesRegex(AssertionError, 'Cited method missing'):
            self.run_fixture(review, census, files)

    def test_same_method_can_have_multiple_contract_consumers(self):
        review, census, files = self.fixture()
        row = copy.deepcopy(review['effects'][0]); row['id'] = 'test:other'
        review['effects'].append(row)
        index, _ = self.run_fixture(review, census, files)
        self.assertEqual(index['methods'][0]['record_ids'], ['test:actor', 'test:other'])
        self.assertEqual(len(index['methods'][0]['proofs']), 1)

    def test_unsupported_shared_registry_cannot_silently_close_methods(self):
        review, census, files = self.fixture()
        review['effects'][0]['shared_kernel_registry_file'] = 'unknown.json'
        files['unknown.json'] = dict(schema='unsupported')
        with self.assertRaisesRegex(AssertionError, 'Unsupported shared registry'):
            self.run_fixture(review, census, files)

    def exclusion_fixture(self):
        review, census, files = self.fixture()
        review['reviewed_batches'] = ['batch.json']
        files['batch.json'] = dict(schema='tno.external_effects.reviewed_combat_batch.v1',
            mod_key='test', exclusions=[dict(entry='test/Actor.class',
            reason='Exact readonly getter previously reviewed.', disposition='READONLY_CONTEXT',
            implementation=[dict(evidence_file='native-evidence/actor.json',
                entry='test/Actor.class', witness_id='actor', methods=['getState'])])])
        return review, census, files

    def test_reviewed_exclusion_uses_independent_hash_without_creating_semantic_record(self):
        review, census, files = self.exclusion_fixture()
        index, pending = self.run_fixture(review, census, files)
        self.assertEqual(index['summary']['exact_contract_methods'], 1)
        self.assertEqual(index['summary']['explicit_exclusion_methods'], 1)
        self.assertEqual(index['summary']['exact_dispositioned_methods'], 2)
        getter = next(m for m in index['methods'] if m['method'] == 'getState')
        self.assertEqual(getter['record_ids'], [])
        self.assertEqual(getter['proofs'][0]['kind'], 'REVIEWED_EXCLUSION')
        self.assertEqual(getter['proofs'][0]['reviewed_batch'], 'batch.json')
        self.assertEqual([m['method'] for m in pending], ['bridge'])
        self.assertEqual(len(review['effects']), 1)

    def test_legacy_prose_or_names_without_exact_proof_remain_pending(self):
        for exclusions in (['getState is utility'], {'utility': ['getState']},
                           [dict(entry='test/Actor.class', reason='Utility')]):
            review, census, files = self.exclusion_fixture()
            files['batch.json']['exclusions'] = exclusions
            _, pending = self.run_fixture(review, census, files)
            self.assertEqual({m['method'] for m in pending}, {'getState', 'bridge'})

    def test_wrong_exclusion_method_hash_is_rejected(self):
        review, census, files = self.exclusion_fixture()
        files['native-evidence/actor.json']['witnesses'][0]['methods'][1]['code_sha256'] = 'wrong'
        with self.assertRaisesRegex(AssertionError, 'Method hash mismatch'):
            self.run_fixture(review, census, files)

    def test_grouped_exclusion_has_explicit_entry_scope_and_independent_hash(self):
        review,census,files=self.exclusion_fixture()
        e=files['batch.json']['exclusions'][0]
        e['entries']=[e.pop('entry')]
        index,pending=self.run_fixture(review,census,files)
        self.assertEqual(index['summary']['explicit_exclusion_methods'],1)
        e['implementation'][0]['entry']='test/Outside.class'
        with self.assertRaisesRegex(AssertionError,'outside its declared entries'):
            self.run_fixture(review,census,files)

    def test_scoped_methods_without_declared_entry_set_still_do_not_close(self):
        review,census,files=self.exclusion_fixture()
        files['batch.json']['exclusions'][0].pop('entry')
        _,pending=self.run_fixture(review,census,files)
        self.assertEqual({m['method'] for m in pending},{'getState','bridge'})

    def test_missing_method_or_entry_cannot_close_excluded_context(self):
        for field, value in [('entry', 'test/Missing.class'), ('methods', ['missing'])]:
            review, census, files = self.exclusion_fixture()
            exclusion = files['batch.json']['exclusions'][0]
            if field == 'entry': exclusion[field] = value
            else: exclusion['implementation'][0][field] = value
            with self.subTest(field=field), self.assertRaises(AssertionError):
                self.run_fixture(review, census, files)

    def test_other_mod_batch_cannot_supply_exclusions(self):
        review, census, files = self.exclusion_fixture()
        files['batch.json']['mod_key'] = 'other'
        with self.assertRaises(AssertionError):
            self.run_fixture(review, census, files)

    def test_overlap_preserves_both_proofs_and_counts_one_method(self):
        review, census, files = self.exclusion_fixture()
        files['batch.json']['exclusions'][0]['implementation'][0]['methods'] = ['tick']
        index, pending = self.run_fixture(review, census, files)
        self.assertEqual(len(index['methods']), 1)
        self.assertEqual(index['summary']['explicit_exclusion_methods'], 0)
        self.assertEqual({p['kind'] for p in index['methods'][0]['proofs']},
                         {'CANONICAL_CONTRACT', 'REVIEWED_EXCLUSION'})
        self.assertEqual(len(pending), 2)

    def test_arphex_existing_proofs_match_original_finite_census(self):
        review = read_json(OUT / 'mod-reviews/arphex.json')
        census = read_json(OUT / 'arphex-combat-census.json')
        index, pending = reconcile(review, census)
        self.assertEqual(index['summary']['total_census_methods'], 19159)
        self.assertEqual(len(index['methods']) + len(pending), len(census['methods']))
        self.assertTrue(any(p['kind'] == 'SHARED_NATIVE_METHOD'
                            for row in index['methods'] for p in row['proofs']))
        self.assertTrue(any(p['kind'] == 'SHARED_NATIVE_KERNEL'
                            for row in index['methods'] for p in row['proofs']))
        # Progress may legitimately close every bridge. Verify coverage against
        # the independent original index rather than requiring unfinished work.
        key = lambda m: (m['entry'], m['method'], m['descriptor'])
        original = {key(m): m for m in census['methods']}
        covered = {key(m): m for m in index['methods']}
        remaining = {key(m): m for m in pending}
        self.assertEqual(len(covered), len(index['methods']))
        self.assertEqual(len(remaining), len(pending))
        self.assertFalse(set(covered) & set(remaining))
        self.assertEqual(set(covered) | set(remaining), set(original))
        self.assertTrue(all(m['code_sha256'] == original[k]['code_sha256']
                            for k, m in covered.items()))
        self.assertTrue(all(m == original[k] for k, m in remaining.items()))


if __name__ == '__main__':
    unittest.main()
