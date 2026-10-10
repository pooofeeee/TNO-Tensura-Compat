"""Pinned coding targets and completeness across three completed dependency patterns."""
import copy
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import mod_intelligence as mi
import test_mod_intelligence_v2 as fixtures


class MappedTargetTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.ImpactTests(methodName='runTest')
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.fixture.f.dependency_fixture()
        self.links, self.document = self.fixture.mapping()

    def retrieve(self, **options):
        return mi.Catalog(self.fixture.f.root).impact(coding_target='fixture.py#FixtureTests',
            repo_root=self.fixture.repo, links_file=self.links, **options)

    def test_exact_pinned_target_preserves_id_contract_and_provenance(self):
        result = self.retrieve()
        direct = self.fixture.impact(links_file=self.links)
        target = result.pop('coding_target')
        self.assertEqual(result, direct)
        self.assertEqual(target['scope'], 'STATIC_CODING_FIXTURE')
        self.assertEqual(target['relationship'], 'EVIDENCE_BACKED_RELATIONSHIP')
        self.assertEqual(target['sha256'], hashlib.sha256((self.fixture.repo/'fixture.py').read_bytes()).hexdigest())
        self.assertEqual(target['execution'], 'NOT_RUN')

    def test_format_paths_names_and_wrong_mod_do_not_guess_a_target(self):
        cases = [('FixtureTests', None, 2), ('fixture.py#', None, 2),
                 ('fixture.py#FixtureTests#extra', None, 2), ('../fixture.py#FixtureTests', None, 2),
                 ('fixture.py#Missing', None, 4), ('other.py#FixtureTests', None, 4),
                 ('fixture.py#FixtureTests', 'pending', 4)]
        for target, mod, code in cases:
            with self.subTest(target=target, mod=mod), self.assertRaises(mi.CatalogError) as raised:
                mi.Catalog(self.fixture.f.root).impact(coding_target=target, mod=mod,
                    repo_root=self.fixture.repo, links_file=self.links)
            self.assertEqual(raised.exception.code, code)

    def test_stale_file_and_mapping_pins_fail_before_success(self):
        path = self.fixture.repo/'fixture.py'
        original = path.read_bytes()
        path.write_bytes(original + b'# changed\n')
        with self.assertRaises(mi.CatalogError) as raised:
            self.retrieve()
        self.assertEqual(raised.exception.code, 3)
        path.write_bytes(original)
        self.document['mechanics'][0]['review_sha256'] = 'f'*64
        self.links.write_text(json.dumps(self.document))
        with self.assertRaises(mi.CatalogError) as raised:
            self.retrieve()
        self.assertEqual(raised.exception.code, 3)

    def test_mapping_drift_between_resolution_and_validation_is_rejected(self):
        original = mi.repository_links
        def change_then_validate(*args, **kwargs):
            self.links.write_text(json.dumps(dict(self.document, changed_after_resolution=True)))
            return original(*args, **kwargs)
        with patch.object(mi, 'repository_links', side_effect=change_then_validate), \
                self.assertRaises(mi.CatalogError) as raised:
            self.retrieve()
        self.assertEqual(raised.exception.code, 3)

    def test_multi_mechanic_target_requires_explicit_selection(self):
        self.fixture.peer('demo:other', dict(self.fixture.f.proof))
        self.fixture.f.review['paths'][0]['effect_ids'].append('demo:other')
        self.fixture.f.write('mod-reviews/demo.json', self.fixture.f.review)
        self.links, self.document = self.fixture.mapping()
        second = copy.deepcopy(self.document['mechanics'][0])
        second['id'] = 'demo:other'
        self.document['mechanics'].append(second)
        self.links.write_text(json.dumps(self.document))
        with self.assertRaisesRegex(mi.CatalogError, 'ambiguous') as raised:
            self.retrieve()
        self.assertEqual(raised.exception.code, 4)
        self.assertEqual(self.fixture.impact(links_file=self.links)['canonical_ids'], ['demo:bite'])

    def test_cli_requires_one_input_and_returns_json_errors(self):
        for arguments in [('impact',), ('impact', 'demo:bite', '--target', 'fixture.py#FixtureTests')]:
            code, result = self.fixture.f.invoke(*arguments)
            self.assertEqual(code, 2)
            self.assertEqual(result['status'], 'ERROR')
            self.assertNotIn('data', result)


class CompletedDependencyPatterns(unittest.TestCase):
    EXAMPLES = {
        'alexscaves:sugar_rush': ('alexscaves', {'alexscaves:citadel:sugar_rush_tick_controller'}),
        'alexscaves:corrodent_bite_native_dig_light_fear': ('alexscaves',
            {'alexscaves:citadel:actor_animation_clock', 'alexscaves:citadel:selective_actor_collision'}),
        'royalvariations:knightly_fortitude': ('royalvariations', set()),
    }

    @classmethod
    def setUpClass(cls):
        cls.results = {}
        for identity, (mod, _) in cls.EXAMPLES.items():
            catalog = mi.Catalog()
            baseline = catalog.get(identity, mod)
            impact = catalog.impact(identity, mod, limit=100)
            cls.results[identity] = baseline, impact

    def test_required_methods_numbers_evidence_and_deliveries_match_v1(self):
        def method_key(file, entry, method):
            return file, entry, method['name'], method.get('descriptor',
                method.get('raw_descriptor', method.get('obfuscated_descriptor')))
        for identity, (baseline, impact) in self.results.items():
            with self.subTest(mechanic=identity):
                links = {e['id']: e for e in impact['evidence_links']}
                expected = {method_key(e['file'], e['entry'], m) for row in baseline['mechanics']
                            for e in row['evidence'] for m in e['methods']}
                actual = {method_key(links[m['evidence_link']]['file'], m['entry'], m)
                          for m in impact['confirmed_contract']['methods'] if 'MECHANIC_CONTRACT' in m['roles']}
                self.assertEqual(actual, expected)
                self.assertEqual(impact['canonical_ids'], [r['id'] for r in baseline['mechanics']])
                self.assertEqual([n['components'] for n in impact['confirmed_contract']['numeric_parameters']],
                                 [r['components'] for r in baseline['mechanics']])
                self.assertEqual([p['paths'] for p in impact['confirmed_contract']['delivery_paths']],
                                 [r['delivery_paths'] for r in baseline['mechanics']])
                root_evidence = {(e['file'], e['entry']) for row in baseline['mechanics'] for e in row['evidence']}
                self.assertTrue(root_evidence <= {(e['file'], e['entry']) for e in impact['evidence_links']})

    def test_dependency_patterns_and_missing_mapping_keep_distinct_meanings(self):
        for identity, (_, expected) in self.EXAMPLES.items():
            impact = self.results[identity][1]
            with self.subTest(mechanic=identity):
                self.assertEqual({d['id'] for d in impact['dependencies']}, expected)
                self.assertTrue(all(d['relationship'] == 'CONFIRMED_DEPENDENCY' for d in impact['dependencies']))
                if not expected:
                    self.assertTrue(any(u['area'] == 'DEPENDENCY_MAPPING' for u in impact['unknown']))
                    self.assertTrue(any(u['area'] == 'TEST_MAPPING' for u in impact['unknown']))

    def test_known_neighbors_remain_conditional_and_tests_are_not_execution_claims(self):
        sugar = self.results['alexscaves:sugar_rush'][1]
        peer = next(p for p in sugar['possible_impact']['mechanics'] if p['id'] == 'alexscaves:bubbled')
        self.assertEqual(peer['relationship'], 'POSSIBLE_IMPACT')
        self.assertTrue(any(r['kind'] == 'RECORDED_METHOD_OVERLAP' and r['method'] == '<clinit>'
                            and r['entry'].endswith('/ACEffectRegistry.class') for r in peer['reasons']))
        actor = self.results['alexscaves:corrodent_bite_native_dig_light_fear'][1]
        peer = next(p for p in actor['possible_impact']['mechanics'] if p['id'] == 'alexscaves:caniac_spin_lunge')
        self.assertTrue(any(r['kind'] == 'SHARED_DEPENDENCY_OBLIGATION'
                            and r['id'] == 'alexscaves:citadel:actor_animation_clock' for r in peer['reasons']))
        for _, impact in self.results.values():
            self.assertTrue(all(t['execution'] == 'NOT_RUN' for t in impact['tests']['references']))
            self.assertTrue(all(p['relationship'] == 'POSSIBLE_IMPACT' for p in impact['possible_impact']['mechanics']))

    def test_real_coding_target_and_native_source_checks_use_existing_cli(self):
        import contextlib
        import io
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            code = mi.main(['impact', '--target',
                'scripts/external-effects/examples/sugar_rush_workflow.py#SugarRush', '--limit', '1',
                '--expect-version', '9.9'])
        self.assertEqual(code, 3)
        self.assertEqual(json.loads(stream.getvalue())['status'], 'ERROR')


if __name__ == '__main__':
    unittest.main()
