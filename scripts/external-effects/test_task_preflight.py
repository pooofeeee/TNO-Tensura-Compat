"""Preflight routing and integrity checks against existing planner fixtures."""
import contextlib
import copy
import hashlib
import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import mod_intelligence as mi
import task_preflight as tp
import test_mod_intelligence_v4 as fixtures


class PreflightTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.AdaptiveScopeTests(methodName='runTest')
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.repo, self.catalog = self.fixture.repo, self.fixture.f.root
        scripts = self.repo / 'scripts/external-effects'
        scripts.mkdir(parents=True)
        (scripts/'mod_intelligence_scope_profiles.json').write_bytes(self.fixture.profile_file.read_bytes())
        (scripts/'mod_intelligence_links.json').write_bytes(self.fixture.fixture.links.read_bytes())
        (self.repo/'edit.py').write_text('value = 4\n')
        (self.repo/'request.json').write_text(json.dumps(self.fixture.fixture.request))
        self.manifest = dict(schema=tp.MANIFEST_SCHEMA, task_type='local_behavior',
            scope=dict(kind='literal_only', description='Replace the selected literal only.'),
            change_request=self.pin('request.json'), approved_edit_targets=[self.pin('edit.py')],
            required_tests=[dict(self.pin('fixture.py'), command=['python3', '-m', 'unittest', 'fixture'])],
            sources=dict(native=dict(mod='demo', version='1.2', sha256=self.fixture.f.digest),
                         dependency=dict(mod='support', version='2.3', sha256='a'*64)),
            unresolved_questions=[])
        self.path = self.repo/'task.json'

    def pin(self, file):
        return dict(file=file, sha256=hashlib.sha256((self.repo/file).read_bytes()).hexdigest())

    def invoke(self, manifest=None, *args):
        self.path.write_text(json.dumps(self.manifest if manifest is None else manifest))
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            code = tp.main(['--manifest', str(self.path), '--root', str(self.repo),
                            '--catalog', str(self.catalog), *args])
        return code, json.loads(stream.getvalue())

    def test_literal_route_retains_exact_v4_plan_and_pins(self):
        code, result = self.invoke()
        self.assertEqual((code, result['route']), (0, 'SUPPORTED_LITERAL_EDIT'))
        expected = mi.Catalog(self.catalog).adaptive_plan('demo:bite', self.fixture.fixture.request,
            'demo', repo_root=self.repo, dependency_version='2.3', dependency_digest='a'*64)
        self.assertEqual(result['evidence_plan']['data'], expected)
        self.assertIn('native-evidence/demo.json',
                      {entry['file'] for entry in result['evidence_plan']['inputs']})
        self.assertEqual(result['checks']['tests'], 'NOT_RUN')
        self.assertEqual(result['checks']['sources']['native']['local_artifact'], 'NOT_CHECKED')

    def test_broader_route_skips_adaptive_and_retains_exact_full_v3(self):
        self.manifest['scope']['kind'] = 'broader_implementation'
        with patch.object(mi.Catalog, 'adaptive_plan', side_effect=RuntimeError('Unnecessary V4 call')):
            code, result = self.invoke()
        self.assertEqual((code, result['route']), (0, 'BROADER_IMPLEMENTATION'))
        expected = mi.Catalog(self.catalog).plan('demo:bite', self.fixture.fixture.request,
            'demo', repo_root=self.repo, dependency_version='2.3', dependency_digest='a'*64)
        self.assertEqual(result['evidence_plan']['data'], expected)

    def test_questions_missing_profile_and_selection_require_evidence(self):
        m = copy.deepcopy(self.manifest)
        m['unresolved_questions'] = ['Which client behavior must change?']
        code, result = self.invoke(m)
        self.assertEqual((code, result['route']), (4, 'REQUIRES_ADDITIONAL_EVIDENCE'))
        self.assertEqual(result['task']['unresolved_questions'], m['unresolved_questions'])
        (self.repo/'scripts/external-effects/mod_intelligence_scope_profiles.json').unlink()
        self.assertEqual(self.invoke()[1]['route'], 'REQUIRES_ADDITIONAL_EVIDENCE')
        request = dict(self.fixture.fixture.request)
        request.pop('parameter')
        request.pop('proposed_value')
        (self.repo/'request.json').write_text(json.dumps(request))
        self.manifest['change_request'] = self.pin('request.json')
        code, result = self.invoke()
        self.assertEqual(code, 4)
        self.assertIn('SELECTION_REQUIRED', ' '.join(result['task']['unresolved_questions']))

    def test_dependency_pin_is_required_when_plan_has_obligations(self):
        del self.manifest['sources']['dependency']
        code, result = self.invoke()
        self.assertEqual(code, 4)
        self.assertIn('dependency identity', ' '.join(result['task']['unresolved_questions']))

    def test_missing_empty_and_stale_source_pins_fail_safely(self):
        for source in ('native', 'dependency'):
            for field, value, code in [('sha256', '', 2), ('sha256', '0'*64, 3), ('version', 'wrong', 3)]:
                with self.subTest(source=source, field=field, value=value):
                    m = copy.deepcopy(self.manifest)
                    m['sources'][source][field] = value
                    actual, result = self.invoke(m)
                    self.assertEqual((actual, result['status']), (code, 'ERROR'))
        del self.manifest['sources']['native']['sha256']
        self.assertEqual(self.invoke()[0], 2)

    def test_missing_stale_traversal_and_symlink_files_are_rejected(self):
        outside = self.catalog/'outside.py'
        outside.write_text('outside')
        (self.repo/'escape.py').symlink_to(outside)
        for file, code in [('missing.py', 2), ('../outside.py', 2), ('escape.py', 2), ('edit.py', 3)]:
            with self.subTest(file=file):
                m = copy.deepcopy(self.manifest)
                m['approved_edit_targets'] = [dict(file=file, sha256='0'*64)]
                actual, result = self.invoke(m)
                self.assertEqual((actual, result['status']), (code, 'ERROR'))
        (self.repo/'request.json').write_text('{}')
        self.assertEqual(self.invoke()[0], 3)

    def test_tests_mandatory_and_cannot_be_edit_targets(self):
        for tests in ([], [None], [self.pin('fixture.py')]):
            with self.subTest(tests=tests):
                m = copy.deepcopy(self.manifest)
                m['required_tests'] = tests
                self.assertEqual(self.invoke(m)[0], 2)
        self.manifest['approved_edit_targets'] = [self.pin('fixture.py')]
        self.assertEqual(self.invoke()[0], 2)

    def test_json_protocol_for_malformed_nonfinite_and_duplicate_input(self):
        for raw in ('[]', '{', '{"n":NaN}', '{"n":1e999}', '{"a":1,"a":2}'):
            with self.subTest(raw=raw):
                self.path.write_text(raw)
                stream = io.StringIO()
                with contextlib.redirect_stdout(stream):
                    code = tp.main(['--manifest', str(self.path)])
                self.assertEqual((code, json.loads(stream.getvalue())['status']), (2, 'ERROR'))
        for field in self.manifest:
            m = copy.deepcopy(self.manifest)
            m[field] = None
            self.assertEqual(self.invoke(m)[0], 2, field)

    def test_budget_failure_never_emits_partial_plan(self):
        code, result = self.invoke(self.manifest, '--budget-bytes', '1')
        self.assertEqual((code, result['status']), (2, 'ERROR'))
        self.assertGreater(result['budget']['required_bytes'], 1)
        self.assertNotIn('evidence_plan', result)

    def test_upstream_witness_corruption_still_fails(self):
        self.fixture.f.packet['witnesses'][0]['methods'][0]['code_hex'] = '01'
        self.fixture.f.write('native-evidence/demo.json', self.fixture.f.packet)
        code, result = self.invoke()
        self.assertNotEqual(code, 0)
        self.assertEqual(result['status'], 'ERROR')

    def test_declared_test_command_is_not_executed(self):
        marker = self.repo/'executed'
        self.manifest['required_tests'][0]['command'] = [
            'python3', '-c', f'open({str(marker)!r}, "w").write("bad")']
        code, result = self.invoke()
        self.assertEqual(code, 0)
        self.assertFalse(marker.exists())
        self.assertEqual(result['checks']['tests'], 'NOT_RUN')


class ExampleTests(unittest.TestCase):
    def test_checked_in_examples_cover_all_routes_with_real_catalog(self):
        examples = mi.ROOT/'scripts/external-effects/examples/task_manifests'
        for name, route, code in [('sugar_rush_literal', 'SUPPORTED_LITERAL_EDIT', 0),
                                  ('sugar_rush_request', 'BROADER_IMPLEMENTATION', 0),
                                  ('sugar_rush_questions', 'REQUIRES_ADDITIONAL_EVIDENCE', 4)]:
            with self.subTest(name=name):
                stream = io.StringIO()
                with contextlib.redirect_stdout(stream):
                    actual = tp.main(['--manifest', str(examples/f'{name}.json')])
                result = json.loads(stream.getvalue())
                self.assertEqual((actual, result.get('route')), (code, route), result)
                self.assertEqual(result['checks']['sources']['dependency']['expected_sha256']['status'], 'MATCH')


if __name__ == '__main__':
    unittest.main()
