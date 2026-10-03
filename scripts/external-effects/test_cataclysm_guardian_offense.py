"""Focused structural and preservation regressions for the static R2k3b batch."""
import copy
import unittest

from catalog_common import read_json
from validate_cataclysm_guardian_offense import (
    LEDGER, NOTE, REVIEW, validate, validate_records,
)


class GuardianOffenseTests(unittest.TestCase):
    def setUp(self):
        self.review = read_json(REVIEW)
        self.note = read_json(NOTE)
        self.ledger = read_json(LEDGER)

    def check(self):
        return validate_records(self.review, self.note, self.ledger)

    def test_archived_evidence_and_protected_checkpoint(self):
        result = validate()
        self.assertEqual(result['status'], 'PASS')
        self.assertEqual(result['protected_r2k3a'], 'BYTE_IDENTICAL')
        self.assertEqual(result['new_mechanics'], 18)

    def test_duplicate_mechanic_rejected(self):
        self.review['effects'][1]['id'] = self.review['effects'][0]['id']
        with self.assertRaises(AssertionError):
            self.check()

    def test_invalid_classification_rejected(self):
        self.review['effects'][0]['primary_classification'] = 'INVENTED'
        with self.assertRaises(AssertionError):
            self.check()

    def test_missing_source_or_delivery_rejected(self):
        for field in ['primary_test_source', 'delivery_paths']:
            with self.subTest(field=field):
                original = copy.deepcopy(self.review)
                self.review['effects'][0][field] = None
                with self.assertRaises(AssertionError):
                    self.check()
                self.review = original

    def test_numeric_candidate_cannot_change_primitive_or_native_value(self):
        for field, value in [('primitive', 'INVENTED'), ('native_value', 999.0)]:
            with self.subTest(field=field):
                original = copy.deepcopy(self.review)
                row = next(e for e in self.review['effects'] if e['scalable_parameter_candidates'])
                row['scalable_parameter_candidates'][0][field] = value
                with self.assertRaises(AssertionError):
                    self.check()
                self.review = original

    def test_binary_gate_cannot_become_numeric_candidate(self):
        row = next(e for e in self.review['effects'] if e['primary_classification'] == 'BINARY_MECHANIC')
        row['scalable_parameter_candidates'] = [{'primitive': 'ALLY_ADMISSION',
            'parameters': ['enable'], 'native_value': 1, 'native_formula': 'invented', 'units': 'boolean'}]
        with self.assertRaises(AssertionError):
            self.check()

    def test_whole_mod_cannot_be_marked_complete(self):
        self.review['status'] = 'COMPLETE'
        with self.assertRaises(AssertionError):
            self.check()

    def test_lost_protected_checkpoint_reference_rejected(self):
        self.review['protected_notes_file'] = 'missing.json'
        with self.assertRaises(AssertionError):
            self.check()


if __name__ == '__main__':
    unittest.main()
