"""Focused retrieval and corruption regressions; never extract or rescan mods."""
import contextlib
import copy
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from catalog_common import sha256
from mod_intelligence import Catalog, CatalogError, main


class RetrievalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.jar_bytes = b'exact source artifact bytes'
        self.digest = hashlib.sha256(self.jar_bytes).hexdigest()
        self.proof = dict(evidence_file='native-evidence/demo.json', witness_id='demo-witness',
                          entry='Demo.class', methods=['tick'])
        self.consumer = dict(self.proof, descriptor='()V', offset=4, opcode='0x12', operand=4.0)
        self.row = dict(id='demo:bite', mod_key='demo', display_name='Native Bite',
            primary_classification='CUSTOM_DAMAGE', inspection_status='VERIFIED',
            actual_behavior='Native bite requests 4 damage; rejected hurt returns skip the heal.',
            hurt_return_dependency='heal requires accepted hurt', registry_ids=['demo:biter'],
            components=[dict(primitive='DAMAGE', numerical_parameters={'damage': 4.0},
                             parameter_units={'damage': 'HP'}, parameter_formulas={'damage': 'native constant'})],
            scalable_parameter_candidates=[dict(primitive='DAMAGE', parameters=['damage'], native_value=4.0,
                                                native_consumer=self.consumer, observation_only=True)],
            implementation=[self.proof], fact_references=[dict(file='facts.json', key='admission')],
            unresolved_ambiguities=[], delivery_paths=['demo:bite:melee'])
        self.review = dict(schema='review.v1', baseline='baseline', mod_key='demo', status='COMPLETE',
            effects=[self.row], paths=[dict(id='demo:bite:melee', labels=['MELEE'], effect_ids=['demo:bite'])],
            semantic_aliases=[dict(original_id='demo:old_bite', canonical_ids=['demo:bite'],
                                   reason='One native payload', native_evidence=[self.proof])],
            checkpoint='closed', external_dependency_complete=True,
            external_dependency_obligations_file='dependencies.json')
        artifact = dict(key='demo', filename='demo-9.9.jar', sha256=self.digest,
            metadata=[dict(entry='META-INF/neoforge.mods.toml', parsed=dict(
                mods=[dict(modId='demo', version='1.2', displayName='Demo')],
                dependencies={'demo': [dict(modId='support', type='required', versionRange='[2.0,)')]}))])
        targets = [dict(mod_key='demo', state='COMPLETE', detail='Pinned complete review', semantic_effect_count=1),
                   dict(mod_key='pending', state='UNSTARTED', detail='Not researched', semantic_effect_count=None),
                   dict(mod_key='reference', state='COMPLETE', detail='Reference-only', semantic_effect_count=None)]
        self.write('mod-completion-ledger.json', dict(baseline='baseline', checkpoint='closed', targets=targets))
        self.write('jar-inventory.json', dict(baseline='baseline', targets=[artifact,
            dict(artifact, key='pending'), dict(artifact, key='reference')],
            dependency_artifacts=[dict(key='support', filename='support-2.3.jar', version='2.3', sha256='a' * 64)]))
        self.write('mod-reviews/demo.json', self.review)
        self.packet = dict(baseline='baseline', witnesses=[dict(id='demo-witness', mod_key='demo',
            jar_sha256=self.digest, entry='Demo.class', entry_sha256='b' * 64,
            methods=[dict(name='tick', descriptor='()V', code_hex='00',
                code_sha256=hashlib.sha256(b'\0').hexdigest(),
                instructions=[dict(offset=4, opcode='0x12', operand=4.0)])])])
        self.write('native-evidence/demo.json', self.packet)
        self.write('facts.json', dict(facts={'admission': 'Native hurt acceptance required'}))
        self.write('dependencies.json', dict(mod_key='demo', native_jar_sha256=self.digest, status='COMPLETE',
            artifact=dict(mod_id='support', filename='support-2.3.jar', declared_minimum='2.0',
                          exact_installed_version='2.3', sha256='a' * 64, status='AVAILABLE_VERIFIED'),
            obligations=[dict(id='demo:support', status='RESOLVED_PINNED',
                              actual_contract='Native support contract', evidence_files=['native-evidence/demo.json'])]))

    def write(self, file, data):
        path = self.root / file
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data), encoding='utf-8')

    def invoke(self, *args):
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            code = main(['--catalog', str(self.root), *args])
        return code, json.loads(stream.getvalue())

    def test_retrieves_values_semantics_facts_deliveries_and_exact_evidence(self):
        code, response = self.invoke('get', 'demo:bite', '--expect-version', '1.2')
        self.assertEqual(code, 0)
        row = response['data']['mechanics'][0]
        self.assertIn('rejected hurt', row['actual_behavior'])
        self.assertEqual(row['contract']['hurt_return_dependency'], 'heal requires accepted hurt')
        self.assertEqual(row['components'][0]['numerical_parameters']['damage'], 4.0)
        self.assertEqual(row['components'][0]['parameter_units']['damage'], 'HP')
        self.assertEqual(row['facts'][0]['value'], 'Native hurt acceptance required')
        self.assertEqual(row['delivery_paths'][0]['labels'], ['MELEE'])
        site = next(e for e in row['evidence'] if 'site' in e)
        self.assertEqual(site['site']['offset'], 4)
        self.assertEqual(site['methods'][0]['descriptor'], '()V')
        self.assertEqual(site['source_pin_check'], 'INVENTORY_MATCH')
        self.assertEqual(site['file_sha256'], sha256(self.root / site['file']))
        self.assertEqual(response['data']['source_check']['local_artifact'], 'NOT_CHECKED')
        self.assertEqual(response['data']['dependencies']['obligations'], [{'id': 'demo:support', 'status': 'RESOLVED_PINNED'}])
        inputs = {v['file']: v['sha256'] for v in response['inputs']}
        self.assertEqual(inputs['mod-reviews/demo.json'], sha256(self.root / 'mod-reviews/demo.json'))

    def test_section_selection_checks_evidence_without_emitting_it(self):
        code, response = self.invoke('get', 'demo:bite', '--section', 'numbers')
        self.assertEqual(code, 0)
        row = response['data']['mechanics'][0]
        self.assertIn('components', row)
        self.assertNotIn('actual_behavior', row)
        self.assertNotIn('evidence', row)
        self.assertNotIn('dependencies', response['data'])
        self.assertIn('native-evidence/demo.json', [i['file'] for i in response['inputs']])

    def test_search_is_bounded_deterministic_and_uses_and_terms(self):
        second = copy.deepcopy(self.row)
        second['id'] = 'demo:another_bite'
        self.review['effects'].append(second)
        self.write('mod-reviews/demo.json', self.review)
        c = Catalog(self.root)
        first = c.search('BITE damage', limit=1)
        next_page = c.search('bite damage', limit=1, offset=1)
        self.assertEqual(first['total'], 2)
        self.assertTrue(first['has_more'])
        self.assertEqual(first['results'][0]['id'], 'demo:another_bite')
        self.assertEqual(next_page['results'][0]['id'], 'demo:bite')
        self.assertFalse(next_page['has_more'])
        self.assertEqual(c.search('bite missing')['total'], 0)
        self.assertEqual(c.search('bite', primitive='OTHER')['total'], 0)
        self.assertEqual(c.search('bite', classification='CUSTOM_DAMAGE')['total'], 2)
        self.assertEqual(set(c.index.files), {'mod-completion-ledger.json', 'jar-inventory.json', 'mod-reviews/demo.json'})

    def test_resolves_canonical_alias_without_inventing_another_mechanic(self):
        code, response = self.invoke('get', 'demo:old_bite')
        self.assertEqual(code, 0)
        self.assertEqual(response['data']['alias']['canonical_ids'], ['demo:bite'])
        self.assertEqual(response['data']['mechanics'][0]['id'], 'demo:bite')

    def test_lists_unstarted_and_reference_only_scopes_without_serving_them(self):
        code, response = self.invoke('mods')
        self.assertEqual(code, 0)
        statuses = {m['mod_key']: m['semantic_catalog_available'] for m in response['data']['mods']}
        self.assertEqual(statuses, {'demo': True, 'pending': False, 'reference': False})
        for key in ['pending', 'reference', 'unknown']:
            code, response = self.invoke('search', 'bite', '--mod', key)
            self.assertEqual(code, 4)
            self.assertEqual(response['status'], 'ERROR')

    def test_local_artifact_check_hashes_bytes_without_parsing_or_filename_inference(self):
        artifact = self.root / 'renamed.jar'
        artifact.write_bytes(self.jar_bytes)
        code, response = self.invoke('verify', 'demo', '--jar', str(artifact), '--expect-sha256', self.digest.upper())
        self.assertEqual(code, 0)
        self.assertEqual(response['data']['source_check']['local_artifact']['status'], 'MATCH')
        artifact.write_bytes(b'another version')
        self.assertEqual(self.invoke('verify', 'demo', '--jar', str(artifact))[0], 3)

    def test_rejects_filename_version_and_stale_expected_digest(self):
        self.assertEqual(self.invoke('get', 'demo:bite', '--expect-version', '9.9')[0], 3)
        self.assertEqual(self.invoke('get', 'demo:bite', '--expect-sha256', 'f' * 64)[0], 3)
        self.assertEqual(self.invoke('verify', 'demo', '--expect-sha256', 'bad')[0], 2)

    def test_rejects_stale_selected_witness_jar_hash(self):
        self.packet['witnesses'][0]['jar_sha256'] = 'f' * 64
        self.write('native-evidence/demo.json', self.packet)
        self.assertEqual(self.invoke('get', 'demo:bite')[0], 3)

    def test_rejects_missing_method_or_wrong_numeric_descriptor_offset_and_operand(self):
        for change in [dict(methods=['missing']), dict(descriptor='(I)V'), dict(offset=5), dict(operand=5.0)]:
            with self.subTest(change=change):
                row = copy.deepcopy(self.row)
                row['scalable_parameter_candidates'][0]['native_consumer'].update(change)
                self.write('mod-reviews/demo.json', dict(self.review, effects=[row]))
                self.assertEqual(self.invoke('get', 'demo:bite')[0], 2)

    def test_rejects_changed_code_bytes_and_detached_numeric_value(self):
        self.packet['witnesses'][0]['methods'][0]['code_hex'] = '01'
        self.write('native-evidence/demo.json', self.packet)
        self.assertEqual(self.invoke('get', 'demo:bite')[0], 2)
        self.packet['witnesses'][0]['methods'][0]['code_hex'] = '00'
        self.write('native-evidence/demo.json', self.packet)
        self.row['components'][0]['numerical_parameters']['damage'] = 7.0
        self.write('mod-reviews/demo.json', self.review)
        self.assertEqual(self.invoke('get', 'demo:bite')[0], 2)

    def test_rejects_missing_fact_broken_delivery_and_unresolved_row(self):
        for change in [dict(fact_references=[dict(file='facts.json', key='unknown')]),
                       dict(delivery_paths=['absent']), dict(unresolved_ambiguities=['unknown admission'])]:
            with self.subTest(change=change):
                row = dict(self.row, **change)
                self.write('mod-reviews/demo.json', dict(self.review, effects=[row]))
                self.assertNotEqual(self.invoke('get', 'demo:bite')[0], 0)

    def test_rejects_catalog_path_escape_and_symlink_escape(self):
        outside = self.root.parent / (self.root.name + '-outside.json')
        outside.write_text(json.dumps(self.packet))
        self.addCleanup(outside.unlink)
        link = self.root / 'escape.json'
        link.symlink_to(outside)
        for file in ['../' + outside.name, 'escape.json']:
            with self.subTest(file=file):
                row = dict(self.row, implementation=[dict(self.proof, evidence_file=file)])
                self.write('mod-reviews/demo.json', dict(self.review, effects=[row]))
                self.assertEqual(self.invoke('get', 'demo:bite')[0], 2)

    def test_dependencies_keep_declared_ranges_and_exact_installed_pins_separate(self):
        code, response = self.invoke('dependencies', 'demo')
        self.assertEqual(code, 0)
        dependencies = response['data']
        self.assertEqual(dependencies['declared'][0]['versionRange'], '[2.0,)')
        self.assertEqual(dependencies['artifact']['exact_installed_version'], '2.3')
        self.assertEqual(dependencies['obligations'][0]['actual_contract'], 'Native support contract')
        corrupted = json.loads((self.root / 'dependencies.json').read_text())
        corrupted['artifact']['sha256'] = 'f' * 64
        self.write('dependencies.json', corrupted)
        self.assertEqual(self.invoke('dependencies', 'demo')[0], 3)

    def test_verifies_inventoried_dependency_version_without_a_semantic_catalog(self):
        code, response = self.invoke('verify', 'support', '--expect-version', '2.3')
        self.assertEqual(code, 0)
        self.assertEqual(response['data']['source_check']['catalog_pin']['recorded_version'], '2.3')
        self.assertEqual(self.invoke('verify', 'support', '--expect-version', '2.0')[0], 3)

    def test_no_recorded_obligations_is_not_claimed_dependency_completion(self):
        self.review.pop('external_dependency_obligations_file')
        self.write('mod-reviews/demo.json', self.review)
        result = Catalog(self.root).dependencies('demo')
        self.assertEqual(result['obligation_status'], 'NOT_RECORDED')
        self.assertIsNone(result['obligations'])

    def test_usage_errors_are_json_and_do_not_emit_partial_success(self):
        for args in [('search', 'bite', '--limit', '0'), ('search', 'bite', '--offset', '-1'),
                     ('search', 'bite', '--expect-version', '1.2'), ('get', 'unknown'), ('unknown',)]:
            with self.subTest(args=args):
                code, response = self.invoke(*args)
                self.assertNotEqual(code, 0)
                self.assertEqual(response['status'], 'ERROR')
                self.assertNotIn('data', response)

    def test_catalog_reads_are_repeatable_and_leave_all_inputs_unchanged(self):
        before = {p.relative_to(self.root): sha256(p) for p in self.root.rglob('*.json')}
        first = self.invoke('get', 'demo:bite')
        second = self.invoke('get', 'demo:bite')
        self.assertEqual(first, second)
        self.assertEqual(before, {p.relative_to(self.root): sha256(p) for p in self.root.rglob('*.json')})


class ExistingCatalogTests(unittest.TestCase):
    def test_selected_lookup_in_each_existing_completed_catalog(self):
        for key in Catalog().completed_keys():
            with self.subTest(mod=key):
                catalog = Catalog()
                row = catalog.review(key)['effects'][0]
                result = catalog.get(row['id'], key, ['numbers', 'evidence'])
                self.assertEqual(result['mechanics'][0]['id'], row['id'])
                self.assertTrue(result['mechanics'][0]['evidence'])

    def test_pinned_anaconda_damage_and_citadel_dependency(self):
        catalog = Catalog()
        result = catalog.get('alexsmobs:anaconda_native_bite_strangle', 'alexsmobs')
        row = result['mechanics'][0]
        self.assertEqual(row['components'][0]['numerical_parameters']['bite_damage'], 4.0)
        self.assertEqual(row['components'][0]['numerical_parameters']['maxhealth_coefficient'], 0.25)
        self.assertEqual(row['parameter_candidates'][0]['native_consumer']['offset'], 86)
        self.assertEqual(result['dependencies']['artifact']['exact_installed_version'], '2.7.6')
        self.assertEqual(result['dependencies']['obligation_status'], 'COMPLETE')
        self.assertNotIn('effect-catalog.json', catalog.index.files)
        self.assertNotIn('alexsmobs-combat-census.json', catalog.index.files)

    def test_existing_semantic_alias_and_native_resource_evidence(self):
        catalog = Catalog()
        alias = catalog.get('cataclysm:monstrosity_smash', 'cataclysm')
        self.assertEqual(alias['alias']['canonical_ids'], ['cataclysm:monstrosity_earthquake_payload'])
        catalog = Catalog()
        resource = catalog.get('lm:animated_monster_shared_control', 'legendary_monsters')
        self.assertTrue(any(e['entry'].endswith('.json') for e in resource['mechanics'][0]['evidence']))

    def test_declared_version_is_preserved_independently_of_filename(self):
        catalog = Catalog()
        self.assertEqual(catalog.source_check('royalvariations', version='2.0')['expected_version']['status'], 'MATCH')
        with self.assertRaises(CatalogError):
            catalog.source_check('royalvariations', version='2.0.4')

    def test_cli_runs_from_an_unrelated_directory(self):
        path = Path(__file__).with_name('mod_intelligence.py').resolve()
        with tempfile.TemporaryDirectory() as cwd:
            process = subprocess.run([sys.executable, '-B', str(path), 'search', 'anaconda strangle',
                                      '--mod', 'alexsmobs', '--limit', '1'], cwd=cwd,
                                     capture_output=True, text=True, check=True)
        result = json.loads(process.stdout)
        self.assertEqual(result['schema'], 'tno.mod_intelligence.v1')
        self.assertEqual(len(result['data']['results']), 1)
        self.assertEqual(process.stderr, '')


if __name__ == '__main__':
    unittest.main()
