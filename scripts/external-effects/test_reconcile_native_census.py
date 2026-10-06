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
        self.assertTrue(any(m['disposition'] == 'SYNTHETIC_BRIDGE_CONTEXT' for m in pending))


if __name__ == '__main__':
    unittest.main()
