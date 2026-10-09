"""Bounded V2.0 relationships and lossless context/budget regressions."""
import contextlib
import copy
import hashlib
import io
import json
from pathlib import Path
import unittest

import test_mod_intelligence as fixtures
from mod_intelligence import Catalog, CatalogError, main, V2_SCHEMA


RELATIONSHIPS = {'CONFIRMED_DEPENDENCY', 'EVIDENCE_BACKED_RELATIONSHIP', 'POSSIBLE_IMPACT', 'UNKNOWN'}


class ImpactTests(unittest.TestCase):
    def setUp(self):
        self.f = fixtures.RetrievalTests(methodName='runTest')
        self.f.setUp()
        self.addCleanup(self.f.doCleanups)
        document = json.loads((self.f.root/'dependencies.json').read_text())
        document['schema'] = 'tno.external_effects.external_dependency_obligations.v1'
        self.f.write('dependencies.json', document)
        self.repo = self.f.root / 'repo'
        self.repo.mkdir()

    def impact(self, **kwargs):
        return Catalog(self.f.root).impact('demo:bite', 'demo', repo_root=self.repo, **kwargs)

    def context(self, **kwargs):
        return Catalog(self.f.root).context('demo:bite', 'demo', repo_root=self.repo, **kwargs)

    def peer(self, identity, proof):
        row = copy.deepcopy(self.f.row)
        row.update(id=identity, implementation=[proof], scalable_parameter_candidates=[])
        self.f.review['effects'].append(row)
        self.f.write('mod-reviews/demo.json', self.f.review)

    def mapping(self):
        file = self.repo / 'fixture.py'
        file.write_text('class FixtureTests:\n    pass\n')
        link = dict(file='fixture.py', symbol='FixtureTests', scope='STATIC_CODING_FIXTURE',
                    sha256=hashlib.sha256(file.read_bytes()).hexdigest())
        entry = dict(id='demo:bite', mod_key='demo', jar_sha256=self.f.digest,
                     review_sha256=hashlib.sha256((self.f.root/'mod-reviews/demo.json').read_bytes()).hexdigest(),
                     catalog_inputs=[dict(file='dependencies.json', sha256=hashlib.sha256(
                         (self.f.root/'dependencies.json').read_bytes()).hexdigest())],
                     tests=[link], sources=[dict(link)])
        document = dict(schema='tno.mod_intelligence.repository_links.v1', mechanics=[entry])
        path = self.repo / 'links.json'
        path.write_text(json.dumps(document))
        return path, document

    def test_explicit_method_and_dependency_links_are_classified(self):
        self.f.dependency_fixture()
        self.peer('demo:peer', dict(self.f.proof))
        result = self.impact()
        self.assertEqual(result['dependencies'][0]['relationship'], 'CONFIRMED_DEPENDENCY')
        self.assertEqual(result['dependencies'][0]['artifact']['sha256'], 'a' * 64)
        self.assertTrue(all(m['relationship'] == 'EVIDENCE_BACKED_RELATIONSHIP'
                            for m in result['confirmed_contract']['methods']))
        peer, = result['possible_impact']['mechanics']
        self.assertEqual(peer['id'], 'demo:peer')
        self.assertEqual(peer['relationship'], 'POSSIBLE_IMPACT')
        self.assertEqual(peer['reasons'][0]['descriptor'], '()V')
        self.assertIn('condition', peer['reasons'][0])
        self.assertTrue(all(w['relationship'] == 'UNKNOWN' for w in result['unknown']))

    def test_names_values_and_different_descriptors_do_not_create_relationships(self):
        self.peer('demo:bite_name_only', dict(self.f.proof, entry='Other.class'))
        self.peer('demo:bite_other_packet', dict(self.f.proof, evidence_file='absent.json'))
        self.peer('demo:bite_other_overload', dict(self.f.proof, descriptor='(I)V'))
        result = self.impact()
        self.assertEqual(result['possible_impact']['total'], 0)
        self.assertEqual(result['possible_impact']['mechanics'], [])

    def test_bounded_pagination_is_stable_and_does_not_hide_required_contracts(self):
        for identity in ('demo:z', 'demo:a', 'demo:m'):
            self.peer(identity, dict(self.f.proof))
        first = self.impact(limit=1)
        second = self.impact(limit=1, offset=1)
        self.assertEqual(first['possible_impact']['total'], 3)
        self.assertTrue(first['possible_impact']['has_more'])
        self.assertEqual(first['possible_impact']['mechanics'][0]['id'], 'demo:a')
        self.assertEqual(second['possible_impact']['mechanics'][0]['id'], 'demo:m')
        self.assertEqual(first['known_boundaries'], second['known_boundaries'])
        self.assertEqual(first['confirmed_contract'], second['confirmed_contract'])

    def test_matching_peer_witness_is_validated_not_promoted_from_metadata(self):
        self.peer('demo:peer', dict(self.f.proof, witness_id='WRONG'))
        code, result = self.f.invoke('impact', 'demo:bite')
        self.assertEqual(code, 2)
        self.assertEqual(result['status'], 'ERROR')
        self.assertNotIn('data', result)

    def test_unqualified_relationship_requires_unique_matching_witness_id(self):
        proof = dict(self.f.proof)
        file = proof.pop('evidence_file')
        self.peer('demo:peer', proof)
        self.f.review['effects'][-1]['reference_evidence'] = [file]
        self.f.write('mod-reviews/demo.json', self.f.review)
        self.assertEqual(self.impact()['possible_impact']['mechanics'][0]['id'], 'demo:peer')
        proof['witness_id'] = 'WRONG'
        self.f.write('mod-reviews/demo.json', self.f.review)
        self.assertEqual(self.f.invoke('impact', 'demo:bite')[0], 2)

    def test_missing_selected_evidence_fails_json_protocol(self):
        (self.f.root/'native-evidence/demo.json').unlink()
        for command in ('impact', 'context'):
            with self.subTest(command=command):
                code, result = self.f.invoke(command, 'demo:bite')
                self.assertEqual(code, 2)
                self.assertEqual(result['status'], 'ERROR')
                self.assertNotIn('data', result)

    def test_missing_dependency_evidence_is_not_downgraded_to_unknown(self):
        self.f.dependency_fixture()
        (self.f.root/'native-evidence/support.json').unlink()
        self.assertEqual(self.f.invoke('impact', 'demo:bite')[0], 2)

    def test_malformed_recorded_entry_hash_is_rejected(self):
        self.f.packet['witnesses'][0]['entry_sha256'] = 'not-a-sha256'
        self.f.write('native-evidence/demo.json', self.f.packet)
        for command in ('impact', 'context'):
            with self.subTest(command=command):
                code, result = self.f.invoke(command, 'demo:bite')
                self.assertEqual(code, 2)
                self.assertEqual(result['status'], 'ERROR')
                self.assertNotIn('data', result)

    def test_missing_hashes_stay_null_with_visible_warnings(self):
        _, packet = self.f.dependency_fixture()
        method = packet['witnesses'][0]['methods'][0]
        method.pop('code_sha256')
        method.pop('code_hex')
        method['raw_descriptor'] = method.pop('descriptor')
        packet['witnesses'][0].pop('entry_sha256')
        self.f.write('native-evidence/support.json', packet)
        impact = self.impact()
        dependency, = impact['dependencies']
        self.assertEqual(dependency['validation_state'], 'WITNESSES_RESOLVED_WITH_MISSING_HASHES')
        self.assertIsNone(dependency['missing_method_hashes'][0]['code_sha256'])
        self.assertEqual(dependency['missing_method_hashes'][0]['descriptor'], '()V')
        context = self.context()
        self.assertIsNone(next(e for e in context['evidence'] if e['entry'] == 'Support.class')['class_hash'])
        self.assertIn('METHOD_HASHES', {w['area'] for w in context['warnings']})
        self.assertEqual(context['dependencies'][0]['missing_method_hashes'], dependency['missing_method_hashes'])

    def test_module_dependency_references_do_not_imply_mechanic_dependency(self):
        result = self.impact()
        self.assertEqual(result['dependencies'], [])
        self.assertEqual(result['related_references']['module_obligations'][0]['relationship'], 'UNKNOWN')
        self.assertIn('DEPENDENCY_MAPPING', {w['area'] for w in result['unknown']})
        self.assertEqual(self.f.invoke('impact', 'demo:bite', '--expect-dependency-version', '2.3')[0], 4)

    def test_pinned_fixture_mapping_has_provenance_without_execution_claim(self):
        file, _ = self.mapping()
        result = self.impact(links_file=file)
        test, = result['tests']['references']
        self.assertEqual(test['relationship'], 'EVIDENCE_BACKED_RELATIONSHIP')
        self.assertEqual(test['execution'], 'NOT_RUN')
        self.assertEqual(test['scope'], 'STATIC_CODING_FIXTURE')
        self.assertIn('fixture.py', {i['file'] for i in result['repository_inputs']})
        self.assertTrue(result['source_locations'][-1]['editable'])

    def test_stale_mapping_pins_or_file_bytes_are_rejected(self):
        for corruption in ('jar', 'review', 'test_file', 'dependency_contract'):
            file, document = self.mapping()
            if corruption == 'test_file':
                (self.repo/'fixture.py').write_text('class FixtureTests:\n    changed = True\n')
            elif corruption == 'dependency_contract':
                dependency = json.loads((self.f.root/'dependencies.json').read_text())
                dependency['obligations'][0]['actual_contract'] = 'Changed contract'
                self.f.write('dependencies.json', dependency)
            else:
                document['mechanics'][0][corruption + '_sha256'] = 'f' * 64
                file.write_text(json.dumps(document))
            with self.subTest(corruption=corruption), self.assertRaises(CatalogError) as caught:
                self.impact(links_file=file)
            self.assertEqual(caught.exception.code, 3)

    def test_missing_mapping_symbol_or_escaped_path_is_rejected(self):
        for change in (dict(symbol='Missing'), dict(file='../outside.py')):
            file, document = self.mapping()
            document['mechanics'][0]['tests'][0].update(change)
            file.write_text(json.dumps(document))
            with self.subTest(change=change), self.assertRaises(CatalogError):
                self.impact(links_file=file)

    def test_exact_literal_id_is_a_reference_not_verified_test_coverage(self):
        directory = self.repo/'scripts/external-effects'
        directory.mkdir(parents=True)
        (directory/'test_reference.py').write_text("ID = 'demo:bite'\n")
        (directory/'test_name_only.py').write_text("ID = 'Native Bite'\n")
        references = self.impact()['tests']['references']
        self.assertEqual([r['file'] for r in references], ['scripts/external-effects/test_reference.py'])
        self.assertEqual(references[0]['relationship'], 'UNKNOWN')
        self.assertEqual(references[0]['coverage'], 'UNVERIFIED_ID_REFERENCE')

    def test_context_preserves_gates_units_and_original_binding_evidence(self):
        self.f.row['components'][0]['native_flags'] = dict(server_only=True, admission='accepted hurt')
        self.f.write('mod-reviews/demo.json', self.f.review)
        result = self.context()
        self.assertEqual(result['numbers_and_formulas'][0]['components'][0], self.f.row['components'][0])
        consumer, = result['consumers']
        self.assertEqual(consumer['native_consumer']['offset'], 4)
        self.assertEqual(consumer['native_consumer']['operand'], 4.0)
        method_id, = consumer['native_consumer']['method_ids']
        method = next(m for m in result['methods'] if m['id'] == method_id)
        evidence = next(e for e in result['evidence'] if e['id'] == method['evidence_link'])
        source = next(p for p in result['evidence_sources'] if p['id'] == evidence['source_id'])
        self.assertEqual(evidence['entry'], 'Demo.class')
        self.assertEqual(source['file'], 'native-evidence/demo.json')
        self.assertEqual(source['jar_sha256'], self.f.digest)
        self.assertTrue(result['warnings'])

    def test_context_budget_counts_exact_utf8_wire_bytes_and_never_truncates(self):
        self.f.row['actual_behavior'] += ' λ' * 40
        self.f.write('mod-reviews/demo.json', self.f.review)
        def invoke(budget, pretty=False):
            output = io.StringIO()
            argv = ['--catalog', str(self.f.root)] + (['--pretty'] if pretty else [])
            with contextlib.redirect_stdout(output):
                code = main([*argv, 'context', 'demo:bite', '--budget-bytes', str(budget)])
            return code, output.getvalue(), json.loads(output.getvalue())
        for pretty in (False, True):
            code, raw, original = invoke(1000000, pretty)
            self.assertEqual(code, 0)
            required = len(raw.encode('utf-8'))
            self.assertEqual(invoke(required, pretty)[2], original)
            code, _, failure = invoke(required-1, pretty)
            self.assertEqual(code, 2)
            self.assertEqual(failure['schema'], V2_SCHEMA)
            self.assertEqual(failure['budget']['required_bytes'], required)
            self.assertNotIn('data', failure)
        self.assertEqual(self.f.invoke('context', 'demo:bite', '--budget-bytes', '0')[0], 2)

    def test_source_constraints_and_legacy_schema_remain_active(self):
        for command in ('impact', 'context'):
            self.assertEqual(self.f.invoke(command, 'demo:bite', '--expect-version', '9.9')[0], 3)
            self.assertEqual(self.f.invoke(command, 'demo:bite', '--expect-sha256', 'f'*64)[0], 3)
            self.assertEqual(self.f.invoke(command, 'demo:bite')[1]['schema'], V2_SCHEMA)
        self.assertEqual(self.f.invoke('get', 'demo:bite')[1]['schema'], 'tno.mod_intelligence.v1')


class ExistingImpactExamples(unittest.TestCase):
    def test_completed_sugar_rush_and_corrodent_packages(self):
        examples = {'alexscaves:sugar_rush': ('SugarRushWorkflowTests', 'sugar_rush_tick_controller'),
                    'alexscaves:corrodent_bite_native_dig_light_fear': ('AnimationWorkflowTests', 'actor_animation_clock')}
        for identity, (test_symbol, obligation_suffix) in examples.items():
            with self.subTest(mechanic=identity):
                catalog = Catalog()
                result = catalog.context(identity, 'alexscaves')
                self.assertTrue(any(d['id'].endswith(obligation_suffix) for d in result['dependencies']))
                self.assertTrue(any(t.get('symbol') == test_symbol for t in result['tests']['references']))
                original = Catalog().get(identity, 'alexscaves', ['numbers'])['mechanics'][0]
                self.assertEqual(result['numbers_and_formulas'][0]['components'], original['components'])
                self.assertTrue(all(e['relationship'] in RELATIONSHIPS for e in result['evidence']))
                self.assertNotIn('code_hex', json.dumps(result))


if __name__ == '__main__':
    unittest.main()
