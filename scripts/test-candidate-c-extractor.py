"""Negative checks ensure the strict extractor rejects corrupted stored evidence."""
import copy
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('extractor', Path(__file__).with_name('extract-phase6-candidate-c-sustained.py'))
extractor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(extractor)

class ExtractorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = extractor.load(Path(__file__).resolve().parents[1] /
            'docs/benchmarks/phase6-candidate-c-sustained-viability/v1-harness-smoke-final.jsonl')

    def rejects(self, mutate):
        records = copy.deepcopy(self.records)
        mutate(records)
        with self.assertRaises(ValueError):
            extractor.validate(records, smoke=True)

    def test_missing_trajectory_tick(self):
        self.rejects(lambda rs: rs.remove(next(r for r in rs if r['kind'] == 'trajectory')))

    def test_physical_factor_replaced_by_wound_factor(self):
        def mutate(rs):
            row = next(r for r in rs if r['kind'] == 'row' and r['hit_index'] == 9)
            row['severance_wall_trace']['Adaptive_native_factor'] = 1.0
        self.rejects(mutate)

    def test_healing_through_ceiling(self):
        def mutate(rs):
            cycle = next(r for r in rs if r['kind'] == 'regenerate_cycle' and r['state'] == 'C')
            cycle['actual_healing'] = 1.0
        self.rejects(mutate)

    def test_wrong_native_request(self):
        def mutate(rs):
            cycle = next(r for r in rs if r['kind'] == 'regenerate_cycle')
            cycle['requested_healing'] = 399.0
        self.rejects(mutate)

if __name__ == '__main__':
    unittest.main()
