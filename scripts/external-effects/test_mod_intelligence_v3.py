"""Change-specific obligations, evidence boundaries, and request/CLI failures."""
import copy
import contextlib
import hashlib
import io
import json
import unittest

import mod_intelligence as mi
import test_mod_intelligence_v2 as fixtures


SECTIONS = ('mechanics', 'source_locations', 'preserved_constraints', 'dependencies',
            'required_tests', 'patterns', 'risks_and_questions')
LABELS = {'VERIFIED', 'REQUIRES_REVIEW', 'UNKNOWN'}


class ChangePlanTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.ImpactTests(methodName='runTest')
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.f = self.fixture.f
        self.f.dependency_fixture()
        self.f.row['scalable_parameter_candidates'][0]['native_literal_numeric_site_binding'] = {
            'native_value': 4.0, 'value_offset': 4, 'kind': 'EXPLICITLY_REVIEWED_LITERAL_SITE'}
        self.f.write('mod-reviews/demo.json', self.f.review)
        self.links, self.document = self.fixture.mapping()
        self.request = dict(target='demo:bite', change_type='modify numeric parameter',
                            requested_behavior='Increase admitted damage',
                            parameter=dict(primitive='DAMAGE', name='damage'), proposed_value=5.0)
        self.request_file = self.f.root/'request.json'

    def plan(self, request=None, **options):
        return mi.Catalog(self.f.root).plan('demo:bite', request or self.request, 'demo',
            repo_root=self.fixture.repo, links_file=self.links, **options)

    def invoke(self, request=None, *arguments):
        self.request_file.write_text(json.dumps(self.request if request is None else request))
        return self.f.invoke('plan', '--request', str(self.request_file), *arguments)

    def test_plan_connects_literal_to_preservation_edit_and_validation(self):
        result = self.plan()
        self.assertEqual(result['readiness'], 'REVIEW_REQUIRED')
        site, edit = result['source_locations']
        self.assertEqual((site['method'], site['descriptor'], site['literal']['offset']), ('tick', '()V', 4))
        self.assertEqual(site['literal']['current_value'], 4.0)
        self.assertEqual(site['classification'], 'VERIFIED')
        self.assertFalse(site['editable'])
        self.assertEqual(edit['classification'], 'REQUIRES_REVIEW')
        self.assertEqual(edit['proposed_value'], 5.0)
        ids = {i['id'] for s in SECTIONS for i in result[s]}
        chain, = result['reasoning_chain']
        for name in ('existing_behavior', 'preserved_constraints', 'implementation_locations', 'validation_requirements'):
            self.assertTrue(chain[name])
            self.assertTrue(set(chain[name]) <= ids)
        for s in SECTIONS:
            self.assertTrue(all(i['classification'] in LABELS for i in result[s]))
        obligations = [i for i in result['required_tests'] if i['kind'] == 'VALIDATION_OBLIGATION']
        self.assertTrue(all(i['classification'] == 'REQUIRES_REVIEW' for i in obligations))
        self.assertEqual(result['request']['classification'], 'REQUIRES_REVIEW')

    def test_full_root_constraints_and_dependency_contract_are_retained(self):
        context = self.fixture.context(links_file=self.links)
        result = self.plan()
        components = [i['record'] for i in result['preserved_constraints'] if i['kind'] == 'RECORDED_COMPONENT']
        self.assertEqual(components, context['numbers_and_formulas'][0]['components'])
        contract = next(i for i in result['preserved_constraints'] if i['kind'] == 'RECORDED_CONTRACT')['record']
        self.assertEqual(contract['contract'], context['verified_behavior'][0]['contract'])
        self.assertEqual(result['dependencies'][0]['record'],
                         {k: v for k, v in context['dependencies'][0].items() if k != 'relationship'})
        self.assertEqual(result['dependencies'][0]['scope'], 'WHOLE_MECHANIC')
        self.assertIn('DEPENDENCY_EFFECT', {i['kind'] for i in result['risks_and_questions']})
        references = [i for i in result['required_tests'] if i['kind'] == 'EXISTING_TEST_REFERENCE']
        self.assertEqual(references[0]['record']['execution'], 'NOT_RUN')

    def test_no_parameter_or_ambiguous_prose_does_not_infer_an_edit(self):
        request = dict(target='demo:bite', change_type='modify numeric parameter', requested_behavior='Make it stronger')
        result = self.plan(request)
        self.assertEqual(result['readiness'], 'SELECTION_REQUIRED')
        self.assertFalse(result['source_locations'])
        self.assertIsNone(result['selected_parameter'])
        self.assertIn('PARAMETER_SELECTION', {i['kind'] for i in result['risks_and_questions']})

    def test_unsupported_changes_have_no_claimed_edit_or_peer_impact(self):
        self.fixture.peer('demo:shared', dict(self.f.proof))
        self.links, self.document = self.fixture.mapping()
        result = self.plan(dict(self.request, change_type='change ownership'))
        self.assertEqual(result['readiness'], 'UNSUPPORTED_CHANGE')
        self.assertFalse(result['source_locations'])
        self.assertFalse(result['reasoning_chain'][0]['implementation_locations'])
        self.assertNotIn('CONDITIONAL_SHARED_METHOD', {i['kind'] for i in result['risks_and_questions']})

    def test_exact_shared_method_is_conditional_and_name_or_overload_is_not_impact(self):
        self.fixture.peer('demo:shared', dict(self.f.proof))
        self.fixture.peer('demo:name_only', dict(self.f.proof, entry='Other.class'))
        self.fixture.peer('demo:overload', dict(self.f.proof, descriptor='(I)V'))
        self.fixture.peer('demo:other_packet', dict(self.f.proof, evidence_file='absent.json'))
        self.links, self.document = self.fixture.mapping()
        result = self.plan()
        peers = [i for i in result['risks_and_questions'] if i['kind'] == 'CONDITIONAL_SHARED_METHOD']
        self.assertEqual([i['mechanic_id'] for i in peers], ['demo:shared'])
        self.assertEqual(peers[0]['classification'], 'REQUIRES_REVIEW')

    def test_unqualified_consumer_uses_the_verified_resolver(self):
        self.f.row['reference_evidence'] = ['native-evidence/demo.json']
        self.f.row['scalable_parameter_candidates'][0]['native_consumer'].pop('evidence_file')
        self.f.write('mod-reviews/demo.json', self.f.review)
        self.links, self.document = self.fixture.mapping()
        site = self.plan()['source_locations'][0]
        self.assertEqual(site['file'], 'native-evidence/demo.json')
        self.f.row['scalable_parameter_candidates'][0]['native_consumer']['witness_id'] = 'WRONG'
        self.f.write('mod-reviews/demo.json', self.f.review)
        code, result = self.invoke()
        self.assertEqual(code, 2)
        self.assertEqual(result['status'], 'ERROR')

    def test_missing_binding_or_hash_does_not_become_an_edit_target(self):
        original = copy.deepcopy(self.f.row['scalable_parameter_candidates'][0])
        self.f.row['scalable_parameter_candidates'][0].pop('native_literal_numeric_site_binding')
        self.f.write('mod-reviews/demo.json', self.f.review)
        self.links, self.document = self.fixture.mapping()
        self.assertEqual(self.plan()['readiness'], 'LITERAL_SITE_UNKNOWN')
        self.f.row['scalable_parameter_candidates'][0] = original
        self.f.write('mod-reviews/demo.json', self.f.review)
        self.f.packet['witnesses'][0].pop('entry_sha256')
        self.f.write('native-evidence/demo.json', self.f.packet)
        self.links, self.document = self.fixture.mapping()
        result = self.plan()
        self.assertEqual(result['readiness'], 'LITERAL_SITE_UNKNOWN')
        self.assertFalse(result['source_locations'])

    def test_numeric_corruption_and_invocation_as_literal_are_errors(self):
        self.f.row['components'][0]['numerical_parameters']['damage'] = 5.0
        self.f.write('mod-reviews/demo.json', self.f.review)
        with self.assertRaises(mi.CatalogError) as raised:
            self.plan()
        self.assertEqual(raised.exception.code, 2)
        self.f.row['components'][0]['numerical_parameters']['damage'] = 4.0
        self.f.write('mod-reviews/demo.json', self.f.review)
        self.f.packet['witnesses'][0]['methods'][0]['instructions'][0]['opcode'] = '0xb6'
        self.f.write('native-evidence/demo.json', self.f.packet)
        with self.assertRaises(mi.CatalogError) as raised:
            self.plan()
        self.assertEqual(raised.exception.code, 2)

    def test_coupled_parameters_require_review(self):
        self.f.row['components'][0]['numerical_parameters']['other_damage'] = 4.0
        self.f.row['scalable_parameter_candidates'][0]['parameters'].append('other_damage')
        self.f.write('mod-reviews/demo.json', self.f.review)
        self.links, self.document = self.fixture.mapping()
        result = self.plan()
        coupled = next(i for i in result['risks_and_questions'] if i['kind'] == 'COUPLED_PARAMETER_BINDING')
        self.assertEqual(coupled['classification'], 'REQUIRES_REVIEW')
        self.assertEqual(coupled['parameters'], ['damage', 'other_damage'])
        self.assertEqual(result['readiness'], 'REVIEW_REQUIRED')

    def test_malformed_or_escaping_validation_records_are_rejected(self):
        for reports in [None, ['bad'], [dict(file='../outside.md', sha256='a'*64, scope='STATIC_CODING_FIXTURE')],
                        [dict(file='record.md', sha256='', scope='STATIC_CODING_FIXTURE')]]:
            self.document['mechanics'][0]['validation_records'] = reports
            self.links.write_text(json.dumps(self.document))
            with self.subTest(reports=reports), self.assertRaises(mi.CatalogError) as raised:
                self.plan()
            self.assertEqual(raised.exception.code, 2)

    def test_stale_validation_reports_fail_and_history_is_not_new_execution(self):
        file = self.fixture.repo/'validation.md'
        file.write_text('Historical static fixture validation\n')
        self.document['mechanics'][0]['validation_records'] = [dict(file='validation.md',
            sha256=hashlib.sha256(file.read_bytes()).hexdigest(), scope='STATIC_CODING_FIXTURE')]
        self.links.write_text(json.dumps(self.document))
        report = next(i for i in self.plan()['patterns'] if i['kind'] == 'VALIDATION_RECORD')
        self.assertEqual(report['record']['execution'], 'NOT_RERUN')
        file.write_text('Changed\n')
        with self.assertRaises(mi.CatalogError) as raised:
            self.plan()
        self.assertEqual(raised.exception.code, 3)

    def test_malformed_requests_and_nonfinite_values_return_json_errors(self):
        cases = [[], dict(self.request, typo=True), dict(self.request, proposed_value=True),
                 dict(self.request, proposed_value=float('nan')), dict(self.request, constraints=[None]),
                 dict(self.request, parameter=dict(primitive='DAMAGE', name='damage', component_index=True))]
        for request in cases:
            with self.subTest(request=request):
                code, result = self.invoke(request)
                self.assertEqual(code, 2)
                self.assertEqual(result['schema'], mi.PLAN_SCHEMA)
                self.assertEqual(result['status'], 'ERROR')
                self.assertNotIn('data', result)

    def test_selectors_targets_and_source_constraints_fail_safely(self):
        for arguments, expected in [(('--mechanic', 'demo:other'), 2), (('--expect-version', '9.9'), 3),
                                    (('--expect-dependency-version', '9.9'), 3)]:
            code, result = self.invoke(None, *arguments)
            self.assertEqual(code, expected)
            self.assertEqual(result['status'], 'ERROR')
        code, result = self.invoke(dict(self.request, parameter=dict(primitive='DAMAGE', name='missing')))
        self.assertEqual(code, 4)
        code, result = self.invoke(dict(self.request, change_type='modify movement multiplier'))
        self.assertEqual(code, 2)

    def test_plan_budget_counts_utf8_and_never_drops_constraints(self):
        request = dict(self.request, requested_behavior='Increase damage λ')
        for pretty in (False, True):
            def invoke(budget):
                self.request_file.write_text(json.dumps(request))
                stream = io.StringIO()
                with contextlib.redirect_stdout(stream):
                    code = mi.main(['--catalog', str(self.f.root)] + (['--pretty'] if pretty else []) +
                        ['plan', '--request', str(self.request_file), '--budget-bytes', str(budget)])
                return code, stream.getvalue(), json.loads(stream.getvalue())
            code, raw, result = invoke(1000000)
            self.assertEqual(code, 0)
            required = len(raw.encode('utf-8'))
            self.assertEqual(invoke(required)[2], result)
            code, _, failure = invoke(required-1)
            self.assertEqual(code, 2)
            self.assertEqual(failure['schema'], mi.PLAN_SCHEMA)
            self.assertEqual(failure['budget']['required_bytes'], required)
            self.assertNotIn('data', failure)


class CompletedChangeExamples(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.results = {}
        directory = mi.ROOT/'scripts/external-effects/examples/change_requests'
        for file in sorted(directory.glob('*.json')):
            request = json.loads(file.read_text())
            catalog = mi.Catalog()
            cls.results[file.stem] = catalog.plan(request['target'], request)

    def test_simple_heal_and_vector_dependency_example(self):
        simple = self.results['cockroach_heal']
        self.assertEqual(simple['source_locations'][0]['literal']['current_value'], 5.0)
        self.assertEqual(simple['source_locations'][0]['method'], 'onGetItem')
        movement = self.results['sugar_rush_movement']
        self.assertEqual(movement['source_locations'][0]['literal']['offset'], 51)
        self.assertEqual(movement['source_locations'][0]['literal']['current_value'], 0.85)
        self.assertEqual(movement['dependencies'][0]['record']['id'], 'alexscaves:citadel:sugar_rush_tick_controller')
        shared = [i['parameters'] for i in movement['risks_and_questions'] if i['kind'] == 'SHARED_CONSUMER_METHOD']
        self.assertIn(['downward_y_factor'], shared)
        self.assertIn(['duration', 'amplifier'], shared)
        self.assertTrue(any('vector axes' in i.get('scenario', '') for i in movement['required_tests']))

    def test_uncertain_armor_value_is_not_a_verified_edit_or_complete_impact(self):
        result = self.results['knightly_fortitude_uncertain']
        self.assertEqual(result['readiness'], 'LITERAL_SITE_UNKNOWN')
        self.assertEqual(result['selected_parameter']['current_value'], 7)
        self.assertFalse(result['source_locations'])
        questions = {i['kind']: i for i in result['risks_and_questions']}
        for kind in ('NUMERIC_LITERAL_SITE', 'DEPENDENCY_MAPPING', 'PRODUCTION_SOURCE_MAPPING', 'PLAN_COMPLETENESS'):
            self.assertEqual(questions[kind]['classification'], 'UNKNOWN')

    def test_minimal_user_example_requires_explicit_selection(self):
        request = dict(target='alexscaves:sugar_rush', change_type='modify movement multiplier',
                       requested_behavior='increase boost strength')
        result = mi.Catalog().plan(request['target'], request)
        self.assertEqual(result['readiness'], 'SELECTION_REQUIRED')
        self.assertFalse(result['source_locations'])

    def test_legacy_draft_request_can_be_normalized_without_interpreting_prose(self):
        request = dict(schema='tno.mod_intelligence.change_intent.v1', target_mechanic='alexscaves:sugar_rush',
            requested_modification='Increase speed', desired_behavior='Use proposed speed multiplier', constraints=[],
            affected_parameter=dict(primitive='PLAYER_SPEED_QUERY', name='speed_multiplier'), proposed_value=4.0)
        result = mi.Catalog().plan('alexscaves:sugar_rush', request)
        self.assertEqual(result['source_locations'][0]['method'], 'ac_getSpeed')
        self.assertEqual(result['request']['classification'], 'REQUIRES_REVIEW')


if __name__ == '__main__':
    unittest.main()
