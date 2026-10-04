"""Run only the checkpoint selected by CATACLYSM_FAMILY_CHECKPOINT."""
import copy
import os
from pathlib import Path
import unittest
from unittest.mock import patch

from catalog_common import read_json
import validate_cataclysm_family as validator


class FamilyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.note = read_json(Path(os.environ['CATACLYSM_FAMILY_CHECKPOINT']))

    def test_semantic_records_and_native_candidates(self):
        validator.validate_records(self.note)

    def test_exact_native_boundaries(self):
        validator.validate_boundaries(self.note)

    def test_protected_prior_work_and_production(self):
        validator.validate_protection(self.note)

    def test_reject_wrong_candidate_primitive(self):
        review, rows = validator.records(self.note)
        corrupted = copy.deepcopy(rows)
        row = next((r for r in corrupted if r['scalable_parameter_candidates']), corrupted[0])
        if row['scalable_parameter_candidates']:
            row['scalable_parameter_candidates'][0]['primitive'] = 'INVENTED_PRIMITIVE'
        else:
            # Admission-only checkpoints must also reject an invented mapping.
            row['scalable_parameter_candidates'] = [dict(
                primitive='INVENTED_PRIMITIVE', parameters=['invented_parameter'])]
        with patch.object(validator, 'records', return_value=(review, corrupted)):
            with self.assertRaises(AssertionError):
                validator.validate_records(self.note)

    def test_reject_wrong_native_constant(self):
        note = copy.deepcopy(self.note)
        assertion = next(c for c in note['native_boundary_assertions'] if c.get('instructions'))
        assertion['instructions'][0]['operand'] = 'WRONG_NATIVE_VALUE'
        with self.assertRaises(AssertionError):
            validator.validate_boundaries(note)

    def test_json_is_canonical(self):
        import json
        path = Path(os.environ['CATACLYSM_FAMILY_CHECKPOINT'])
        self.assertEqual(path.read_text(), json.dumps(self.note, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    unittest.main()
