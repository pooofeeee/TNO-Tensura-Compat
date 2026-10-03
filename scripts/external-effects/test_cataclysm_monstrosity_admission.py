"""Small negative regressions for R2k4a data, routing and checkpoint protection."""
import copy
import json
import unittest

from catalog_common import read_json
from collect_cataclysm_monstrosity_admission import EVIDENCE_FILE, SPEC_FILE
from validate_cataclysm_monstrosity_admission import (
    LEDGER, NOTE, REVIEW, selected, validate, validate_preservation, validate_records,
)


class MonstrosityAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.review, self.note, self.ledger = [read_json(p) for p in [REVIEW, NOTE, LEDGER]]

    def check(self):
        return validate_records(self.review, self.note, self.ledger)

    def row(self, key):
        return next(e for e in selected(self.review) if e['id'] == 'cataclysm:' + key)

    def test_archived_evidence_and_protected_checkpoints(self):
        result = validate()
        self.assertEqual(result['status'], 'PASS')
        self.assertEqual(result['protected_guardian'], 'BYTE_IDENTICAL')
        self.assertEqual(result['protected_shared_status'], 'BYTE_IDENTICAL')
        self.assertEqual(result['candidate_numeric_parameters'], 1)

    def test_duplicate_mechanic_rejected(self):
        selected(self.review)[1]['id'] = selected(self.review)[0]['id']
        with self.assertRaises(AssertionError):
            self.check()

    def test_invalid_classification_rejected(self):
        selected(self.review)[0]['primary_classification'] = 'INVENTED'
        with self.assertRaises(AssertionError):
            self.check()

    def test_missing_source_or_delivery_rejected(self):
        for field in ['primary_test_source', 'delivery_paths']:
            with self.subTest(field=field):
                original = copy.deepcopy(self.review)
                selected(self.review)[0][field] = None
                with self.assertRaises(AssertionError):
                    self.check()
                self.review = original

    def test_admission_order_cannot_silently_change(self):
        order = self.note['admission_order']['body']
        order[0], order[1] = order[1], order[0]
        with self.assertRaises(AssertionError):
            self.check()

    def test_head_cannot_be_flattened_into_body_admission(self):
        self.row('monstrosity_head_admission')['routing']['part_skips_body_gate'] = False
        with self.assertRaises(AssertionError):
            self.check()

    def test_concrete_bindings_cannot_use_shared_defaults(self):
        for name, value in [('DamageCap', 1000), ('DpsCap', 0), ('RangeLimit', 1000), ('NatureRegen', 0)]:
            with self.subTest(binding=name):
                original = copy.deepcopy(self.note)
                self.note['concrete_bindings'][name]['installed_value'] = value
                with self.assertRaises(AssertionError):
                    self.check()
                self.note = original

    def test_phase_setter_cannot_claim_health_change(self):
        self.row('monstrosity_berserk_phase')['state_binding']['setter_changes_health_or_attributes'] = True
        with self.assertRaises(AssertionError):
            self.check()

    def test_native_encounter_flags_cannot_disappear(self):
        del self.row('monstrosity_encounter_state')['persistence']['native_template_flags']['is_Awaken']
        with self.assertRaises(AssertionError):
            self.check()

    def test_admission_constant_cannot_become_candidate(self):
        row = self.row('monstrosity_incoming_admission')
        comp = row['components'][1]
        row['scalable_parameter_candidates'] = [dict(primitive=comp['primitive'],
            parameters=['direct_golem_multiplier'], native_value=0.5, native_formula=comp['formula'],
            units=comp['parameter_units']['direct_golem_multiplier'], native_boundary=comp['native_boundary'])]
        with self.assertRaises(AssertionError):
            self.check()

    def test_guardian_fact_change_rejected(self):
        old = next(e for e in self.review['effects'] if e['id'].startswith('cataclysm:guardian_'))
        old['actual_behavior'] = 'Silently changed protected fact'
        with self.assertRaises(AssertionError):
            validate_preservation(self.review, self.note, self.ledger)

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
