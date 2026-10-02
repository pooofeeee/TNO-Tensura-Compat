from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import extract_mapping_review_packets as extractor


class PacketTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.matrix = json.loads(extractor.INPUT.read_bytes())
        cls.payload = extractor.OUTPUT.read_bytes()
        cls.packets = json.loads(cls.payload)
        cls.records = cls.packets["mechanics"]
        cls.sources, cls.provenance = extractor.read_sources(cls.matrix, cls.packets["source_commit"])
        cls.by_identity = {(packet["mod_key"], packet["mechanic_id"]): packet for packet in cls.records}

    def test_exactly_33_mechanics_and_86_unresolved_candidates(self):
        self.assertEqual(33, len(self.records))
        self.assertEqual(86, sum(len(packet["unresolved_candidates"]) for packet in self.records))
        self.assertEqual(33, self.packets["summary"]["total_unresolved_mechanics"])
        self.assertEqual(86, self.packets["summary"]["total_unresolved_candidates"])

    def test_only_the_three_permitted_mods_and_unresolved_mechanics_are_present(self):
        self.assertEqual({"cultofazazel", "twilightforest", "variantsandventures"}, {packet["mod_key"] for packet in self.records})
        expected = {(mechanic["mod_key"], mechanic["mechanic_id"]) for mechanic in self.matrix["mechanics"] if any(candidate.get("needs_mapping_review") is True for candidate in mechanic["scalable_parameter_candidates"])}
        self.assertEqual(expected, set(self.by_identity))
        self.assertEqual(len(self.records), len(self.by_identity))

    def test_candidate_names_reasons_and_ambiguities_are_exact_and_resolved_candidates_are_excluded(self):
        for mechanic in self.matrix["mechanics"]:
            identity = (mechanic["mod_key"], mechanic["mechanic_id"])
            unresolved = [candidate for candidate in mechanic["scalable_parameter_candidates"] if candidate.get("needs_mapping_review") is True]
            if not unresolved:
                self.assertNotIn(identity, self.by_identity)
                continue
            expected = [{field: deepcopy(candidate[field]) for field in ("candidate_name", "reason", "matching_primitives") if field in candidate} for candidate in unresolved]
            actual = self.by_identity[identity]["unresolved_candidates"]
            self.assertCountEqual(expected, actual)
            for candidate in actual:
                self.assertNotIn("primitive", candidate)
                self.assertNotIn("parameters", candidate)
        launch = self.by_identity[("cultofazazel", "cultofazazel:azazel_launch")]
        self.assertEqual([{"candidate_name": "duration", "reason": "NO_EXACT_COMPONENT_MATCH"}], launch["unresolved_candidates"])

    def test_packet_and_component_fields_exclude_audit_material(self):
        allowed = {"mod_key", "mechanic_id", "display_name", "primary_classification", "closest_vanilla_equivalent", "actual_behavior", "vanilla_differences", "unresolved_candidates", "components", "numerical_parameters", "binary_parameters", "scalability_note"}
        component_allowed = {"primitive", "formula", "numerical_parameters", "binary_parameters", "vanilla_relation"}
        forbidden = {"implementation", "vanilla_implementation", "comparison_evidence", "evidence", "reference_files", "reference_evidence", "witness_id", "bytecode", "instructions", "class_inventory", "method_inventory", "compatibility_history", "delivery_paths"}
        def assert_no_audit(value):
            if isinstance(value, dict):
                self.assertFalse(forbidden & value.keys())
                for item in value.values():
                    assert_no_audit(item)
            elif isinstance(value, list):
                for item in value:
                    assert_no_audit(item)
        for packet in self.records:
            self.assertTrue(packet.keys() <= allowed)
            for component in packet["components"]:
                self.assertTrue(component.keys() <= component_allowed)
            for candidate in packet["unresolved_candidates"]:
                self.assertTrue(candidate.keys() <= {"candidate_name", "reason", "matching_primitives"})
            assert_no_audit(packet)

    def test_prose_is_bounded_source_prefixes_and_all_non_text_facts_are_exact(self):
        def compare(source, compact):
            if isinstance(source, str):
                normalized = " ".join(source.split())
                self.assertLessEqual(len(compact), 240)
                if len(normalized) <= 240:
                    self.assertEqual(normalized, compact)
                else:
                    self.assertTrue(compact.endswith("…"))
                    self.assertTrue(normalized.startswith(compact[:-1]))
            elif isinstance(source, dict):
                self.assertEqual(source.keys(), compact.keys())
                for key in source:
                    compare(source[key], compact[key])
            elif isinstance(source, list):
                self.assertEqual(len(source), len(compact))
                for before, after in zip(source, compact):
                    compare(before, after)
            else:
                self.assertEqual(source, compact)
        for identity, packet in self.by_identity.items():
            source = self.sources[identity]
            for field in extractor.RECORD_FIELDS:
                if field in source:
                    compare(source[field], packet[field])
                else:
                    self.assertNotIn(field, packet)
            compare(source["components"], packet["components"])

    def test_summary_and_stable_sorting(self):
        summary = self.packets["summary"]
        self.assertEqual({"cultofazazel": 27, "twilightforest": 2, "variantsandventures": 4}, summary["counts_by_mod"])
        reasons = Counter(candidate["reason"] for packet in self.records for candidate in packet["unresolved_candidates"])
        self.assertEqual({"NO_EXACT_COMPONENT_MATCH": 84, "AMBIGUOUS_COMPONENT_MATCH": 2}, reasons)
        self.assertEqual(dict(reasons), summary["counts_by_unresolved_reason"])
        identities = [(packet["mod_key"], packet["mechanic_id"]) for packet in self.records]
        self.assertEqual(sorted(identities), identities)
        for packet in self.records:
            names = [candidate["candidate_name"] for candidate in packet["unresolved_candidates"]]
            self.assertEqual(sorted(names), names)

    def test_packets_are_substantially_smaller_than_reviews_and_selected_full_records(self):
        self.assertEqual(self.provenance["source_review_bytes"], self.packets["source_review_bytes"])
        self.assertEqual(self.provenance["selected_source_record_bytes"], self.packets["selected_source_record_bytes"])
        self.assertLess(len(self.payload), self.packets["source_review_bytes"] / 100)
        self.assertLess(len(self.payload), self.packets["selected_source_record_bytes"] / 4)

    def test_only_three_exact_review_paths_are_read_and_only_selected_ids_projected(self):
        with patch.object(extractor.subprocess, "check_output", wraps=subprocess.check_output) as reads:
            sources, _ = extractor.read_sources(self.matrix, self.packets["source_commit"])
        expected = [["git", "show", f"{self.packets['source_commit']}:{extractor.REVIEW_PATHS[mod]}"] for mod in sorted(extractor.REVIEW_PATHS)]
        self.assertEqual(expected, [call.args[0] for call in reads.call_args_list])
        self.assertEqual(set(self.by_identity), set(sources))

    def test_cli_regeneration_is_byte_identical_and_preserves_matrix_and_branch(self):
        before = extractor.INPUT.read_bytes()
        branch = subprocess.check_output(["git", "symbolic-ref", "HEAD"], cwd=extractor.matrix_extractor.REPO_ROOT)
        with tempfile.TemporaryDirectory() as directory:
            for name in ("first.json", "second.json"):
                output = Path(directory) / name
                subprocess.run([sys.executable, str(Path(extractor.__file__)), "--ref", self.packets["source_commit"], "--output", str(output)], cwd=extractor.matrix_extractor.REPO_ROOT, capture_output=True, check=True)
                self.assertEqual(self.payload, output.read_bytes())
        self.assertEqual(before, extractor.INPUT.read_bytes())
        self.assertEqual(branch, subprocess.check_output(["git", "symbolic-ref", "HEAD"], cwd=extractor.matrix_extractor.REPO_ROOT))


class ProjectionTests(unittest.TestCase):
    def fixture(self):
        identity = ("cultofazazel", "cultofazazel:fixture")
        matrix = {"mechanics": [{"mod_key": identity[0], "mechanic_id": identity[1], "scalable_parameter_candidates": [{"candidate_name": "duration", "reason": "NO_EXACT_COMPONENT_MATCH", "needs_mapping_review": True}, {"candidate_name": "damage", "needs_mapping_review": False}]}]}
        source = {"actual_behavior": "  Observed   behavior  ", "numerical_parameters": {"damage": 0}, "binary_parameters": [False], "components": [{"primitive": "P", "formula": "damage", "numerical_parameters": {"damage": 0}, "implementation": ["cold witness"]}], "implementation": ["cold witness"]}
        return identity, matrix, source

    def test_projection_never_changes_or_resolves_candidates_and_drops_other_fields(self):
        identity, matrix, source = self.fixture()
        original_matrix, original_source = deepcopy(matrix), deepcopy(source)
        packet = extractor.compile_packets(matrix, {identity: source}, {})["mechanics"][0]
        self.assertEqual(original_matrix, matrix)
        self.assertEqual(original_source, source)
        self.assertEqual([{"candidate_name": "duration", "reason": "NO_EXACT_COMPONENT_MATCH"}], packet["unresolved_candidates"])
        self.assertEqual("Observed behavior", packet["actual_behavior"])
        self.assertNotIn("implementation", packet)
        self.assertNotIn("implementation", packet["components"][0])

    def test_absent_and_null_source_fields_are_not_guessed(self):
        identity, matrix, _ = self.fixture()
        packet = extractor.compile_packets(matrix, {identity: {"components": None, "actual_behavior": None}}, {})["mechanics"][0]
        self.assertIsNone(packet["components"])
        self.assertIsNone(packet["actual_behavior"])
        self.assertNotIn("scalability_note", packet)
        self.assertNotIn("numerical_parameters", packet)

    def test_unknown_mod_duplicates_missing_sources_and_missing_reasons_are_rejected(self):
        identity, matrix, source = self.fixture()
        unknown = deepcopy(matrix)
        unknown["mechanics"][0]["mod_key"] = "other"
        duplicate = deepcopy(matrix)
        duplicate["mechanics"].append(deepcopy(duplicate["mechanics"][0]))
        for invalid in (unknown, duplicate):
            with patch.object(extractor.subprocess, "run") as git:
                with self.assertRaises(ValueError):
                    extractor.read_sources(invalid)
                git.assert_not_called()
        with self.assertRaises(ValueError):
            extractor.compile_packets(matrix, {}, {})
        del matrix["mechanics"][0]["scalable_parameter_candidates"][0]["reason"]
        with self.assertRaises(ValueError):
            extractor.compile_packets(matrix, {identity: source}, {})

    def test_partial_reviews_and_missing_or_duplicate_exact_ids_are_rejected(self):
        identity, matrix, _ = self.fixture()
        effect = {"id": identity[1], "mod_key": identity[0], "components": []}
        for review in ({"status": "PARTIAL", "mod_key": identity[0], "effects": [effect]},
                       {"status": "COMPLETE", "mod_key": identity[0], "effects": []},
                       {"status": "COMPLETE", "mod_key": identity[0], "effects": [effect, effect]}):
            with patch.object(extractor.subprocess, "run") as resolve, patch.object(extractor.subprocess, "check_output", return_value=json.dumps(review).encode()):
                resolve.return_value.returncode = 0
                resolve.return_value.stdout = "pinned\n"
                with self.assertRaises(ValueError):
                    extractor.read_sources(matrix)

    def test_source_snapshot_mismatch_is_rejected_before_reading_reviews(self):
        _, matrix, _ = self.fixture()
        matrix["mapping_recovery_source"] = {"source_commit": "old"}
        with patch.object(extractor.subprocess, "run") as resolve, patch.object(extractor.subprocess, "check_output") as reads:
            resolve.return_value.returncode = 0
            resolve.return_value.stdout = "new\n"
            with self.assertRaises(ValueError):
                extractor.read_sources(matrix)
            reads.assert_not_called()


if __name__ == "__main__":
    unittest.main()
