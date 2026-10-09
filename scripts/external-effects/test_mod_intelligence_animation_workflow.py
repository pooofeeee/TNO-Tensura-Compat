"""Coding validation through CLI JSON, without opening canonical research files."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from examples.animation_clock_preview import (AnimationClock, Frame, load_clock, call_cli,
                                               WorkflowError, MECHANIC, OBLIGATION)


class AnimationWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.responses = []
        def capture(*args):
            result = call_cli(*args)
            cls.responses.append(result[0])
            return result
        with patch('examples.animation_clock_preview.call_cli', side_effect=capture):
            cls.clock, cls.measurements = load_clock()

    def test_cli_search_and_exact_selection_supply_only_the_used_contract_sections(self):
        self.assertTrue(any(r['id'] == MECHANIC for r in self.responses[0]['data']['results']))
        row = self.responses[1]['data']['mechanics'][0]
        self.assertNotIn('components', row)
        self.assertNotIn('dependencies', self.responses[1]['data'])
        obligation, = self.responses[2]['data']['obligations']
        self.assertEqual(obligation['id'], OBLIGATION)
        self.assertEqual(self.clock.increment, obligation['contract']['numerical_contract']['clock_increment'])
        self.assertEqual(self.clock.increment, 1)
        self.assertEqual(self.clock.provenance['handler']['source_pin_check'], 'INVENTORY_MATCH')
        self.assertIn('native-evidence/citadel-alexscaves-dependencies.json', self.clock.provenance['inputs'])
        self.assertEqual(len(self.measurements), 3)
        self.assertTrue(all(m['response_bytes'] > 0 for m in self.measurements))

    def test_cancelled_start_skips_send_and_still_advances(self):
        normal, sent = self.clock.advance(Frame(0), 3)
        cancelled, skipped = self.clock.advance(Frame(0), 3, start_cancelled=True)
        self.assertEqual(normal, cancelled)
        self.assertEqual(cancelled, Frame(1))
        self.assertIn('SEND_ANIMATION', [a['action'] for a in sent])
        self.assertNotIn('SEND_ANIMATION', [a['action'] for a in skipped])
        self.assertEqual(skipped[-1], dict(action='POST_TICK', tick=1))

    def test_client_advances_without_server_send_and_start_only_occurs_at_zero(self):
        client, actions = self.clock.advance(Frame(0), 3, server=False)
        self.assertEqual(client, Frame(1))
        self.assertEqual([a['action'] for a in actions], ['POST_START', 'POST_TICK'])
        _, actions = self.clock.advance(Frame(1), 3)
        self.assertEqual([a['action'] for a in actions], ['POST_TICK'])

    def test_terminal_tick_is_posted_before_equality_reset(self):
        state, actions = self.clock.advance(Frame(2), 3)
        self.assertEqual(state, Frame(0, False))
        self.assertEqual(actions, [dict(action='POST_TICK', tick=3), dict(action='RESET_TO_NO_ANIMATION')])
        next_state, actions = self.clock.advance(state, 3)
        self.assertEqual(next_state, state)
        self.assertEqual(actions, [])

    def test_above_duration_does_not_clamp_or_reset(self):
        state, actions = self.clock.advance(Frame(4), 3)
        self.assertEqual(state, Frame(4))
        self.assertEqual(actions, [])

    def test_zero_and_negative_duration_preserve_unclamped_input_semantics(self):
        zero, actions = self.clock.advance(Frame(0), 0, start_cancelled=True)
        self.assertEqual(zero, Frame(0, False))
        self.assertNotIn('POST_TICK', [a['action'] for a in actions])
        negative, actions = self.clock.advance(Frame(0), -1, start_cancelled=True)
        self.assertEqual(negative, Frame(0))
        self.assertEqual([a['action'] for a in actions], ['POST_START'])

    def test_increment_is_consumed_from_response_and_not_duplicated_in_adapter(self):
        responses = copy.deepcopy(self.responses)
        # Synthetic wiring probe, not a different verified native contract.
        responses[2]['data']['obligations'][0]['contract']['numerical_contract']['clock_increment'] = 2
        clock = AnimationClock.from_responses(*responses)
        self.assertEqual(clock.advance(Frame(1), 5)[0], Frame(3))

    def test_stale_mod_and_dependency_pins_fail_before_simulation(self):
        for overrides in [dict(mod_version='2.0.11'), dict(mod_hash='f' * 64),
                          dict(dependency_version='2.7.7'), dict(dependency_hash='f' * 64)]:
            with self.subTest(overrides=overrides), self.assertRaises(WorkflowError) as raised:
                load_clock(**overrides)
            self.assertEqual(raised.exception.code, 3)

    def test_missing_handler_hash_identity_or_unresolved_obligation_is_rejected(self):
        for defect in ('identity', 'hash', 'unresolved', 'end_rule'):
            responses = copy.deepcopy(self.responses)
            obligation = responses[2]['data']['obligations'][0]
            handler = next(w for w in obligation['witnesses'] if w['class_name'] and w['class_name'].endswith('/AnimationHandler'))
            if defect == 'identity':
                handler['class_name'] = None
            elif defect == 'hash':
                next(m for m in handler['methods'] if m['name'] == 'updateAnimations')['code_sha256'] = None
            elif defect == 'end_rule':
                obligation['contract']['numerical_contract']['end_condition'] = 'tick >= duration'
            else:
                obligation['status'] = 'BLOCKED'
            with self.subTest(defect=defect), self.assertRaises(WorkflowError):
                AnimationClock.from_responses(*responses)

    def test_input_fingerprints_detect_drift_between_cli_calls(self):
        responses = copy.deepcopy(self.responses)
        next(i for i in responses[2]['inputs'] if i['file'] == 'jar-inventory.json')['sha256'] = 'f' * 64
        with self.assertRaisesRegex(WorkflowError, 'Catalog changed between CLI calls'):
            AnimationClock.from_responses(*responses)

    def test_executable_preview_runs_from_an_unrelated_directory(self):
        script = Path(__file__).parent / 'examples/animation_clock_preview.py'
        with tempfile.TemporaryDirectory() as directory:
            process = subprocess.run([sys.executable, '-B', str(script), '--duration', '3', '--updates', '4',
                '--start-cancelled'], cwd=directory, capture_output=True, text=True, check=True)
        result = json.loads(process.stdout)
        self.assertEqual(result['duration_input'], 3)
        self.assertEqual([step['after']['tick'] for step in result['trace']], [1, 2, 0, 0])
        self.assertEqual([step['after']['active'] for step in result['trace']], [True, True, False, False])
        self.assertEqual(process.stderr, '')


if __name__ == '__main__':
    unittest.main()
