"""End-to-end contract consumption through the CLI, without native reinspection."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from examples.sugar_rush_workflow import (CLI, MECHANIC, MOD_VERSION, MOD_HASH, DEPENDENCY_HASH,
    DEPENDENCY_VERSION, SugarRush, WorkflowError, call_cli, load_contract)


class SugarRushWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.get, cls.get_bytes = call_cli('get', MECHANIC, '--mod', 'alexscaves', '--section', 'semantics',
            '--section', 'numbers', '--section', 'evidence', '--expect-version', MOD_VERSION, '--expect-sha256', MOD_HASH)
        cls.dependencies, cls.dependency_bytes = call_cli('dependencies', 'alexscaves',
            '--expect-version', MOD_VERSION, '--expect-sha256', MOD_HASH)
        cls.verify, cls.verify_bytes = call_cli('verify', 'citadel', '--expect-version', DEPENDENCY_VERSION,
                                             '--expect-sha256', DEPENDENCY_HASH)
        cls.contract = SugarRush.from_responses(cls.get, cls.dependencies, cls.verify)

    def test_cli_provides_semantics_numeric_method_evidence_and_dependency_contract(self):
        row = self.get['data']['mechanics'][0]
        self.assertIn('LOCAL_ENTITY alone leaves server tick-length50', row['actual_behavior'])
        self.assertEqual(self.contract.duration_multiplier, 2.0)
        self.assertEqual(self.contract.radius, 10.0)
        sites = self.contract.provenance['numeric_sites']
        down = next(s for s in sites if s['parameters'] == ['downward_y_factor'])
        self.assertEqual(down['consumer']['offset'], 86)
        self.assertEqual(down['consumer']['methods'], ['applyEffectTick'])
        self.assertEqual(len(down['methods'][0]['code_sha256']), 64)
        regular = next(s for s in sites if s['parameters'] == ['potion_regular_duration'])
        long = next(s for s in sites if s['parameters'] == ['potion_long_duration'])
        self.assertEqual(regular['methods'][0]['name'], 'lambda$static$18')
        self.assertEqual(long['methods'][0]['name'], 'lambda$static$19')
        self.assertNotEqual(regular['methods'][0]['code_sha256'], long['methods'][0]['code_sha256'])
        self.assertTrue(self.contract.provenance['dependency_evidence'])
        self.assertEqual(self.contract.provenance['source_checks']['mod']['local_artifact'], 'NOT_CHECKED')
        inputs = self.contract.provenance['inputs']
        self.assertIn('alexscaves-citadel-dependency-obligations.json', inputs)
        self.assertNotIn('alexscaves-combat-census.json', inputs)
        self.assertNotIn('effect-catalog.json', inputs)

    def test_amplifier_changes_attribute_amount_and_not_callback_motion(self):
        self.assertEqual(self.contract.attribute_amount(0), 0.25)
        self.assertEqual(self.contract.attribute_amount(1), 0.5)
        self.assertEqual(self.contract.motion((1, 2, 3))['velocity'], (1, 1.7, 3))
        self.assertEqual(self.contract.motion((1, -2, 3))['velocity'], (1, -0.9, 3))

    def test_slow_falling_only_requests_on_descending_server_arm_when_absent(self):
        descending = self.contract.motion((1, -2, 3))
        self.assertEqual(descending['slow_falling_request'], dict(duration=10, amplifier=0, flags=[False] * 3))
        for args, velocity in [({}, (1, 2, 3)), ({}, (1, 0, 3)),
                               ({'on_server': False}, (1, -2, 3)),
                               ({'remaining_duration': 0}, (1, -2, 3)),
                               ({'slow_falling_present': True}, (1, -2, 3))]:
            with self.subTest(args=args, velocity=velocity):
                result = self.contract.motion(velocity, **args)
                self.assertIsNone(result['slow_falling_request'])
                if args.get('on_server') is False or args.get('remaining_duration') == 0:
                    self.assertEqual(result['velocity'], velocity)

    def test_citadel_local_multiplier_applies_twice_to_client_and_preserves_server_query(self):
        inside = self.contract.controller_query(9)
        self.assertEqual(inside['max_duration'], 3600)
        self.assertEqual(inside['client_expiry_master_tick'], 1800)
        self.assertEqual(inside['client_tick_ms'], 200)
        self.assertEqual(inside['server_tick_ms'], 50)
        self.assertEqual(inside['server_speed_return'], 0.1)
        self.assertAlmostEqual(inside['client_speed_return'], 0.3, places=6)
        self.assertAlmostEqual(inside['client_flying_return'], 0.15, places=6)
        self.assertNotEqual(inside['client_flying_return'], 0.02 * 0.5)

    def test_radius_is_strict_and_modifier_expires_at_client_master_tick_boundary(self):
        for distance in [10, 11]:
            with self.subTest(distance=distance):
                result = self.contract.controller_query(distance)
                self.assertFalse(result['local_query_applies'])
                self.assertEqual(result['client_tick_ms'], 50)
                self.assertEqual(result['client_speed_return'], 0.1)
                self.assertEqual(result['client_flying_return'], 0.02)
        self.assertTrue(self.contract.controller_query(0, master_ticks=1799)['local_query_applies'])
        self.assertFalse(self.contract.controller_query(0, master_ticks=1800)['local_query_applies'])
        long = self.contract.controller_query(0, duration=self.contract.long_duration)
        self.assertEqual(long['max_duration'], 7200)
        self.assertEqual(long['client_expiry_master_tick'], 3600)

    def test_modifier_owner_validity_is_separate_from_recipient_speed_gate(self):
        for args in [dict(owner_has_sugar_rush=False), dict(entity_valid=False), dict(local_modifier_present=False)]:
            with self.subTest(args=args):
                result = self.contract.controller_query(0, **args)
                self.assertEqual(result['client_tick_ms'], 50)
        for args in [dict(recipient_has_sugar_rush=False), dict(config=False)]:
            with self.subTest(args=args):
                result = self.contract.controller_query(0, **args)
                self.assertEqual(result['client_tick_ms'], 200)
                self.assertEqual(result['client_speed_return'], 0.1)
                self.assertEqual(result['client_flying_return'], 0.02)

    def test_consumer_uses_retrieved_values_instead_of_hidden_duplicate_constants(self):
        get = copy.deepcopy(self.get)
        components = {c['primitive']: c for c in get['data']['mechanics'][0]['components']}
        # Synthetic adapter wiring probe, not another verified native contract.
        components['FORCED_MOVEMENT']['numerical_parameters']['downward_y_factor'] = 0.6
        changed = SugarRush.from_responses(get, self.dependencies, self.verify)
        self.assertEqual(changed.motion((1, -2, 3))['velocity'], (1, -1.2, 3))

    def test_cli_rejects_incorrect_mod_and_dependency_versions_and_hashes_before_evaluation(self):
        for overrides in [dict(mod_version='2.0.11'), dict(mod_hash='f' * 64),
                          dict(dependency_version='2.7.7'), dict(dependency_hash='f' * 64)]:
            with self.subTest(overrides=overrides):
                with self.assertRaises(WorkflowError) as raised:
                    load_contract(**overrides)
                self.assertEqual(raised.exception.code, 3)

    def test_cli_rejects_local_mod_or_dependency_artifacts_with_incorrect_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            fake = Path(directory) / 'same-version-different-bytes.jar'
            fake.write_bytes(b'not the pinned artifact')
            for args in [dict(mod_jar=fake), dict(dependency_jar=fake)]:
                with self.subTest(args=args):
                    with self.assertRaises(WorkflowError) as raised:
                        load_contract(**args)
                    self.assertEqual(raised.exception.code, 3)

    def test_consumer_rejects_stale_response_identity_and_unresolved_dependency(self):
        for which, mutate in [
            (0, lambda d: d['data']['source_check']['catalog_pin'].update(sha256='f' * 64)),
            (1, lambda d: d['data']['artifact'].update(exact_installed_version='2.7.7')),
            (1, lambda d: d['data'].update(obligation_status='PARTIAL')),
            (2, lambda d: d['data']['source_check']['catalog_pin'].update(sha256='f' * 64)),
            (0, lambda d: d.update(schema='future-schema'))]:
            with self.subTest(which=which):
                responses = copy.deepcopy([self.get, self.dependencies, self.verify])
                mutate(responses[which])
                with self.assertRaises(WorkflowError):
                    SugarRush.from_responses(*responses)

    def test_consumer_rejects_catalog_drift_between_cli_calls(self):
        dependencies = copy.deepcopy(self.dependencies)
        inventory = next(item for item in dependencies['inputs'] if item['file'] == 'jar-inventory.json')
        inventory['sha256'] = 'f' * 64
        with self.assertRaisesRegex(WorkflowError, 'changed between CLI calls'):
            SugarRush.from_responses(self.get, dependencies, self.verify)

    def test_dependency_evidence_gap_is_recorded_rather_than_silently_claimed_verified(self):
        # V1 exposes the completed obligation and locators, but does not resolve
        # its Citadel witnesses to method hashes in this response.
        files = {item['file'] for item in self.dependencies['inputs']}
        self.assertNotIn('native-evidence/citadel-alexscaves-dependencies.json', files)
        self.assertTrue(any(e['evidence_file'] == 'native-evidence/citadel-alexscaves-dependencies.json'
                            for e in self.contract.provenance['dependency_evidence']))

    def test_concrete_demo_runs_from_an_unrelated_directory(self):
        script = CLI.parent / 'examples/sugar_rush_workflow.py'
        with tempfile.TemporaryDirectory() as directory:
            process = subprocess.run([sys.executable, '-B', str(script)], cwd=directory,
                                     capture_output=True, text=True, check=True)
        result = json.loads(process.stdout)
        self.assertEqual(result['status'], 'OK')
        self.assertEqual(result['demonstration']['inside_radius']['client_tick_ms'], 200)
        self.assertEqual(result['cli_output_bytes'], dict(get=self.get_bytes, dependencies=self.dependency_bytes,
                                                       verify=self.verify_bytes))
        self.assertEqual(process.stderr, '')


if __name__ == '__main__':
    unittest.main()
