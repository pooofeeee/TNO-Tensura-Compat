"""Focused R2k4b regressions for primitive/source/return and archive protection."""
import copy
import json
import unittest

from catalog_common import read_json
from collect_cataclysm_monstrosity_offense import EVIDENCE_FILE, SPEC_FILE
from validate_cataclysm_monstrosity_offense import (
    LEDGER, NOTE, REVIEW, selected, validate, validate_preservation, validate_records,
)


class MonstrosityOffenseTests(unittest.TestCase):
    def setUp(self):
        self.review, self.note, self.ledger = [read_json(p) for p in [REVIEW, NOTE, LEDGER]]

    def check(self):
        return validate_records(self.review, self.note, self.ledger)

    def row(self, key):
        return next(e for e in selected(self.review) if e['id'] == 'cataclysm:monstrosity_' + key)

    def test_scoped_evidence_and_locked_artifacts(self):
        result = validate()
        self.assertEqual(result['status'], 'PASS')
        self.assertEqual(result['protected_admission_guardian_shared_status'], 'BYTE_IDENTICAL')
        self.assertEqual(result['new_mechanics'], 16)
        self.assertEqual(result['candidate_numeric_parameters'], 157)

    def test_duplicate_mechanic_rejected(self):
        selected(self.review)[1]['id'] = selected(self.review)[0]['id']
        with self.assertRaises(AssertionError):
            self.check()

    def test_invalid_classification_rejected(self):
        selected(self.review)[0]['primary_classification'] = 'INVENTED'
        with self.assertRaises(AssertionError):
            self.check()

    def test_missing_source_or_delivery_rejected(self):
        for field in ['primary_test_source', 'source_actor', 'delivery_paths']:
            with self.subTest(field=field):
                original = copy.deepcopy(self.review)
                selected(self.review)[0][field] = None
                with self.assertRaises(AssertionError):
                    self.check()
                self.review = original

    def test_payload_must_link_to_its_actual_producer(self):
        self.note['payload_entities'][0]['source_mechanic_ids'] = ['cataclysm:monstrosity_alliance']
        with self.assertRaises((AssertionError, KeyError)):
            self.check()

    def test_candidate_cannot_be_flattened_into_damage(self):
        candidate = next(c for c in self.row('shoulder_check')['scalable_parameter_candidates']
                         if c['primitive'] == 'FORCED_MOVEMENT')
        candidate['primitive'] = 'NATIVE_DAMAGE_REQUEST'
        with self.assertRaises(AssertionError):
            self.check()

    def test_nonfinite_native_parameter_rejected(self):
        self.row('lava_absorption')['components'][0]['numerical_parameters']['amount_coefficient'] = float('inf')
        with self.assertRaises(AssertionError):
            self.check()

    def test_return_dependencies_cannot_silently_change(self):
        for key, field, value in [
            ('flare_impact', 'child_spawn_requires_hurt', True),
            ('flare_impact', 'burn_requires_alive_after_hurt', False),
            ('flame_jet_payload', 'burn_requires_alive_after_hurt', True),
            ('lava_absorption', 'heal_requires_lava_removal', True),
            ('terrain_control', 'terrain_result_gates_victim_damage', True),
        ]:
            with self.subTest(mechanic=key, field=field):
                original = copy.deepcopy(self.review)
                self.row(key)[field] = value
                with self.assertRaises(AssertionError):
                    self.check()
                self.review = original

    def test_explosion_direct_sources_remain_distinct(self):
        self.row('lava_bomb_impact')['block_hit_source_argument'] = 'owner'
        with self.assertRaises(AssertionError):
            self.check()

    def test_debris_cannot_gain_an_invented_damage_payload(self):
        self.row('stomp_wave')['debris_adds_damage'] = True
        with self.assertRaises(AssertionError):
            self.check()

    def test_protected_admission_and_guardian_rows_unchanged(self):
        for key in ['monstrosity_incoming_admission', 'guardian_attack_selection']:
            with self.subTest(mechanic=key):
                original = copy.deepcopy(self.review)
                old = next(e for e in self.review['effects'] if e['id'] == 'cataclysm:' + key)
                old['actual_behavior'] = 'Silently changed protected fact'
                with self.assertRaises(AssertionError):
                    validate_preservation(self.review, self.note, self.ledger)
                self.review = original

    def test_whole_mod_cannot_be_marked_complete(self):
        self.review['status'] = 'COMPLETE'
        with self.assertRaises(AssertionError):
            self.check()

    def test_deterministic_json_formatting(self):
        for path in [REVIEW, NOTE, LEDGER, EVIDENCE_FILE, SPEC_FILE]:
            with self.subTest(file=path.name):
                encoded = (json.dumps(read_json(path), ensure_ascii=False, indent=2) + '\n').encode('utf-8')
                self.assertEqual(path.read_bytes(), encoded)


if __name__ == '__main__':
    unittest.main()
