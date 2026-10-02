from collections import Counter
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import extract_candidate_matrix as extractor


class CandidateMatrixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(extractor.INPUT.read_bytes())
        cls.payload = extractor.OUTPUT.read_bytes()
        cls.matrix = json.loads(cls.payload)
        cls.records = cls.matrix["mechanics"]
        cls.by_identity = {(record["mod_key"], record["mechanic_id"]): record for record in cls.records}

    def test_exactly_105_candidate_mechanics_and_no_others_are_present(self):
        expected = {(record["mod_key"], record["mechanic_id"]) for record in self.manifest["mechanics"] if record.get("scalable_parameter_candidates")}
        self.assertEqual(105, len(self.records))
        self.assertEqual(expected, set(self.by_identity))
        self.assertEqual(len(self.records), len(self.by_identity))
        for record in self.records:
            self.assertTrue(record["scalable_parameter_candidates"])

    def test_mechanic_fields_and_candidate_mappings_are_preserved(self):
        for source in self.manifest["mechanics"]:
            if not source.get("scalable_parameter_candidates"):
                continue
            record = self.by_identity[(source["mod_key"], source["mechanic_id"])]
            for field in ("mod_key", "mechanic_id", "primary_classification", "stage_review_bucket", "closest_vanilla_equivalent"):
                self.assertEqual(source[field], record[field])
            structured = []
            legacy = []
            for candidate in record["scalable_parameter_candidates"]:
                if candidate["candidate_form"] == "STRUCTURED":
                    self.assertFalse(candidate["needs_mapping_review"])
                    self.assertNotIn("candidate_name", candidate)
                    original = {key: value for key, value in candidate.items() if key not in {"candidate_form", "needs_mapping_review"}}
                    structured.append(original)
                else:
                    legacy.append(candidate["candidate_name"])
            expected_structured = [dict(candidate, parameters=sorted(candidate["parameters"])) for candidate in source["scalable_parameter_candidates"] if isinstance(candidate, dict)]
            self.assertCountEqual(expected_structured, structured)
            self.assertCountEqual([candidate for candidate in source["scalable_parameter_candidates"] if isinstance(candidate, str)], legacy)

    def test_dazed_has_explicit_movement_and_attack_coefficient_mappings(self):
        dazed = self.by_identity[("royalvariations", "royalvariations:dazed")]
        candidates = dazed["scalable_parameter_candidates"]
        self.assertEqual({("ATTRIBUTE_MOVEMENT_SPEED", "coefficient"), ("ATTRIBUTE_ATTACK_DAMAGE", "coefficient")}, {(candidate["primitive"], parameter) for candidate in candidates for parameter in candidate["parameters"]})
        for candidate in candidates:
            self.assertEqual("STRUCTURED", candidate["candidate_form"])
            self.assertFalse(candidate["needs_mapping_review"])
        self.assertEqual({"ATTRIBUTE_MOVEMENT_SPEED", "ATTRIBUTE_ATTACK_DAMAGE"}, {component["primitive"] for component in dazed["components"]})

    def test_legacy_names_never_receive_an_inferred_primitive_or_parameter(self):
        for source in self.manifest["mechanics"]:
            if not source.get("scalable_parameter_candidates"):
                continue
            record = self.by_identity[(source["mod_key"], source["mechanic_id"])]
            primitives = sorted({component["primitive"] for component in source["components"]})
            for candidate in record["scalable_parameter_candidates"]:
                if candidate["candidate_form"] == "LEGACY_UNSCOPED":
                    self.assertEqual({"candidate_name", "candidate_form", "needs_mapping_review", "available_component_primitives"}, set(candidate))
                    self.assertTrue(candidate["needs_mapping_review"])
                    self.assertEqual(primitives, candidate["available_component_primitives"])
                    self.assertNotIn("primitive", candidate)
                    self.assertNotIn("parameters", candidate)

    def test_components_are_exact_manifest_components_selected_only_by_explicit_scope(self):
        for source in self.manifest["mechanics"]:
            candidates = source.get("scalable_parameter_candidates")
            if not candidates:
                continue
            record = self.by_identity[(source["mod_key"], source["mechanic_id"])]
            if any(isinstance(candidate, str) for candidate in candidates):
                self.assertCountEqual(source["components"], record["components"])
            else:
                primitives = {candidate["primitive"] for candidate in candidates}
                self.assertCountEqual([component for component in source["components"] if component["primitive"] in primitives], record["components"])

    def test_summary_counts_and_unique_pairs_match_the_manifest(self):
        selected = [record for record in self.manifest["mechanics"] if record.get("scalable_parameter_candidates")]
        structured = [candidate for record in selected for candidate in record["scalable_parameter_candidates"] if isinstance(candidate, dict)]
        legacy = [candidate for record in selected for candidate in record["scalable_parameter_candidates"] if isinstance(candidate, str)]
        pairs = sorted({(candidate["primitive"], parameter) for candidate in structured for parameter in candidate["parameters"]})
        summary = self.matrix["summary"]
        self.assertEqual(669, summary["total_mechanics"])
        self.assertEqual(105, summary["mechanics_with_stage_candidates"])
        self.assertEqual(103, summary["structured_candidate_count"])
        self.assertEqual(len(structured), summary["structured_candidate_count"])
        self.assertEqual(245, summary["structured_parameter_count"])
        self.assertEqual(sum(len(candidate["parameters"]) for candidate in structured), summary["structured_parameter_count"])
        self.assertEqual(242, summary["legacy_unscoped_candidate_count"])
        self.assertEqual(len(legacy), summary["legacy_unscoped_candidate_count"])
        self.assertEqual(225, summary["unique_structured_pair_count"])
        self.assertEqual([{"primitive": primitive, "parameter": parameter} for primitive, parameter in pairs], summary["unique_structured_pairs"])
        self.assertEqual(dict(Counter(record["mod_key"] for record in selected)), summary["counts_by_mod"])
        self.assertEqual(dict(Counter(record["stage_review_bucket"] for record in selected)), summary["counts_by_stage_review_bucket"])

    def test_records_components_and_candidates_are_stably_sorted(self):
        identities = [(record["mod_key"], record["mechanic_id"]) for record in self.records]
        self.assertEqual(sorted(identities), identities)
        for record in self.records:
            primitives = [component["primitive"] for component in record["components"]]
            self.assertEqual(sorted(primitives), primitives)
            structured = [candidate for candidate in record["scalable_parameter_candidates"] if candidate["candidate_form"] == "STRUCTURED"]
            keys = [(candidate["primitive"], candidate["parameters"]) for candidate in structured]
            self.assertEqual(sorted(keys), keys)
            for candidate in structured:
                self.assertEqual(sorted(candidate["parameters"]), candidate["parameters"])
            names = [candidate["candidate_name"] for candidate in record["scalable_parameter_candidates"] if candidate["candidate_form"] == "LEGACY_UNSCOPED"]
            self.assertEqual(sorted(names), names)

    def test_cli_reruns_are_byte_identical_and_do_not_change_input(self):
        original = extractor.INPUT.read_bytes()
        with tempfile.TemporaryDirectory() as directory:
            for name in ("first.json", "second.json"):
                output = Path(directory) / name
                subprocess.run([sys.executable, str(Path(extractor.__file__)), "--output", str(output)], cwd=extractor.REPO_ROOT, capture_output=True, check=True)
                self.assertEqual(self.payload, output.read_bytes())
        self.assertEqual(original, extractor.INPUT.read_bytes())


class NormalizationTests(unittest.TestCase):
    def mechanic(self, candidates):
        return {
            "mod_key": "example", "mechanic_id": "example:original", "primary_classification": "CUSTOM_DAMAGE",
            "stage_review_bucket": "CUSTOM_POLICY_REVIEW",
            "components": [{"primitive": "UNRELATED"}, {"primitive": "DAMAGE", "coefficient": 2}],
            "scalable_parameter_candidates": candidates,
        }

    def test_unscoped_names_remain_unscoped_even_when_they_match_a_component_name(self):
        source = self.mechanic(["DAMAGE", "damage", "duration", "box"])
        record = extractor.normalize_mechanic(source)
        self.assertCountEqual(source["components"], record["components"])
        for candidate in record["scalable_parameter_candidates"]:
            self.assertEqual("LEGACY_UNSCOPED", candidate["candidate_form"])
            self.assertTrue(candidate["needs_mapping_review"])
            self.assertEqual(["DAMAGE", "UNRELATED"], candidate["available_component_primitives"])
            self.assertNotIn("primitive", candidate)

    def test_mixed_candidates_keep_exact_structured_mapping_and_all_legacy_context(self):
        source = self.mechanic([{"primitive": "DAMAGE", "parameters": ["z", "a"], "meaning": "Observed only"}, "duration"])
        original = copy.deepcopy(source)
        record = extractor.normalize_mechanic(source)
        self.assertEqual(original, source)
        self.assertCountEqual(source["components"], record["components"])
        self.assertEqual({"primitive": "DAMAGE", "parameters": ["a", "z"], "meaning": "Observed only", "candidate_form": "STRUCTURED", "needs_mapping_review": False}, record["scalable_parameter_candidates"][0])
        scoped = extractor.normalize_mechanic(self.mechanic([{"primitive": "DAMAGE", "parameters": ["coefficient"]}]))
        self.assertEqual([{"primitive": "DAMAGE", "coefficient": 2}], scoped["components"])

    def test_missing_null_and_empty_candidates_are_excluded_without_guessing(self):
        mechanics = []
        for index, value in enumerate((None, [])):
            source = self.mechanic(value)
            source["mechanic_id"] = str(index)
            mechanics.append(source)
        absent = self.mechanic([])
        del absent["scalable_parameter_candidates"]
        mechanics.append(absent)
        matrix = extractor.compile_matrix({"mechanics": mechanics})
        self.assertEqual([], matrix["mechanics"])
        self.assertEqual(3, matrix["summary"]["total_mechanics"])
        self.assertEqual(0, matrix["summary"]["mechanics_with_stage_candidates"])

    def test_duplicate_ids_and_unknown_candidate_shapes_are_rejected(self):
        source = self.mechanic(["damage"])
        with self.assertRaises(ValueError):
            extractor.compile_matrix({"mechanics": [source, copy.deepcopy(source)]})
        for candidate in ({"parameters": ["damage"]}, {"primitive": "DAMAGE", "parameters": "damage"}, 7):
            with self.assertRaises(ValueError):
                extractor.normalize_candidate(candidate, ["DAMAGE"])

    def test_absent_or_null_optional_context_is_preserved_without_inventing_components(self):
        source = self.mechanic(["damage"])
        del source["components"]
        record = extractor.normalize_mechanic(source)
        self.assertNotIn("components", record)
        self.assertNotIn("closest_vanilla_equivalent", record)
        self.assertEqual([], record["scalable_parameter_candidates"][0]["available_component_primitives"])
        source["components"] = None
        source["closest_vanilla_equivalent"] = None
        record = extractor.normalize_mechanic(source)
        self.assertIsNone(record["components"])
        self.assertIsNone(record["closest_vanilla_equivalent"])


if __name__ == "__main__":
    unittest.main()
