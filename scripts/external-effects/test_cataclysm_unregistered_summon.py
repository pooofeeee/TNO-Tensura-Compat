"""Focused registry/source protection for the R2k31 compiled summon surface."""
import copy
import os
from pathlib import Path
import unittest

from catalog_common import OUT, read_json
from collect_cataclysm_family import collect


class UnregisteredSummonTests(unittest.TestCase):
    def test_no_registered_source_or_candidate_is_invented(self):
        note = read_json(OUT / 'cataclysm-r2k31-ignited_sword-family.json')
        review = read_json(OUT / 'mod-reviews/cataclysm.json')
        rows = [r for r in review['effects'] if r['id'] in note['mechanic_ids']]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['registry_ids'], [])
        self.assertEqual(rows[0]['scalable_parameter_candidates'], [])
        self.assertEqual(rows[0]['native_source_status'], 'UNREGISTERED_CODE_SURFACE')
        self.assertTrue(rows[0]['primary_test_source'].startswith('UNREGISTERED_NATIVE_CLASS:'))
        self.assertEqual(note['facts']['live_summon_producer_proven'], False)

    def test_absence_check_rejects_a_present_registry_term(self):
        note = read_json(OUT / 'cataclysm-r2k31-ignited_sword-family.json')
        spec = copy.deepcopy(read_json(OUT / note['specification_file']))
        selected = next(w for w in spec['evidence_specifications']
                        if w['entry'].endswith('/init/ModEntities.class'))
        selected['absent_constant_pool_terms'] = ['com/github/L_Ender/cataclysm/init/ModEntities']
        with self.assertRaises(AssertionError):
            collect(spec, Path(os.environ['CATACLYSM_PINNED_JAR']))


if __name__ == '__main__':
    unittest.main()
