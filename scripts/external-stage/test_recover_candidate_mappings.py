from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import recover_candidate_mappings as recovery


def unrecovered_matrix(matrix):
    """Replay the preserved legacy names, without reading any additional review or manifest."""
    result = deepcopy(matrix)
    for mechanic in result["mechanics"]:
        for candidate in mechanic["scalable_parameter_candidates"]:
            if candidate["candidate_form"] in ("LEGACY_UNSCOPED", "RECOVERED_EXACT"):
                candidate["candidate_form"] = "LEGACY_UNSCOPED"
                candidate["needs_mapping_review"] = True
                for field in ("reason", "matching_primitives", "primitive", "parameters", "recovery"):
                    candidate.pop(field, None)
    return result


class RecoveryMatrixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = recovery.INPUT.read_bytes()
        cls.matrix = json.loads(cls.payload)
        cls.original = unrecovered_matrix(cls.matrix)
        cls.ref = cls.matrix["mapping_recovery_source"]["source_commit"]
        cls.sources, cls.provenance = recovery.read_legacy_reviews(cls.original, cls.ref)
        cls.by_id = {mechanic["mechanic_id"]: mechanic for mechanic in cls.matrix["mechanics"]}

    def candidates(self, mechanic_id):
        return {candidate["candidate_name"]: candidate for candidate in self.by_id[mechanic_id]["scalable_parameter_candidates"]}

    def test_summary_conserves_all_candidates_and_records_exact_outcomes(self):
        summary = self.matrix["summary"]
        self.assertEqual(105, len(self.matrix["mechanics"]))
        self.assertEqual(103, summary["original_structured_candidate_count"])
        self.assertEqual(156, summary["recovered_exact_candidate_count"])
        self.assertEqual(84, summary["unresolved_no_match_candidate_count"])
        self.assertEqual(2, summary["unresolved_ambiguous_candidate_count"])
        self.assertEqual(33, summary["mechanics_needing_mapping_review_count"])
        self.assertEqual(86, summary["legacy_unscoped_candidate_count"])
        candidates = [candidate for mechanic in self.matrix["mechanics"] for candidate in mechanic["scalable_parameter_candidates"]]
        self.assertEqual(345, len(candidates))
        self.assertEqual(Counter(STRUCTURED=103, RECOVERED_EXACT=156, LEGACY_UNSCOPED=86), Counter(candidate["candidate_form"] for candidate in candidates))
        self.assertEqual(33, sum(any(candidate["needs_mapping_review"] for candidate in mechanic["scalable_parameter_candidates"]) for mechanic in self.matrix["mechanics"]))

    def test_azazel_launch_damage_and_vertical_recover_but_duration_does_not(self):
        candidates = self.candidates("cultofazazel:azazel_launch")
        for name, primitive in (("damage", "NATIVE_DAMAGE_REQUEST"), ("vertical", "FORCED_MOVEMENT")):
            candidate = candidates[name]
            self.assertEqual("RECOVERED_EXACT", candidate["candidate_form"])
            self.assertEqual(primitive, candidate["primitive"])
            self.assertEqual([name], candidate["parameters"])
            self.assertFalse(candidate["needs_mapping_review"])
            self.assertEqual("EXACT_COMPONENT_NUMERICAL_PARAMETER_KEY_MATCH", candidate["recovery"]["method"])
        self.assertEqual("LEGACY_UNSCOPED", candidates["duration"]["candidate_form"])
        self.assertEqual("NO_EXACT_COMPONENT_MATCH", candidates["duration"]["reason"])
        self.assertTrue(candidates["duration"]["needs_mapping_review"])

    def test_honey_factor_stays_ambiguous_and_semantic_names_stay_unmatched(self):
        candidates = self.candidates("cultofazazel:honey_properties")
        self.assertEqual("LEGACY_UNSCOPED", candidates["factor"]["candidate_form"])
        self.assertEqual("AMBIGUOUS_COMPONENT_MATCH", candidates["factor"]["reason"])
        self.assertEqual(["BLOCK_JUMP_FACTOR", "BLOCK_SPEED_FACTOR"], candidates["factor"]["matching_primitives"])
        for candidate in candidates.values():
            self.assertTrue(candidate["needs_mapping_review"])
            self.assertNotIn("primitive", candidate)
            self.assertNotIn("parameters", candidate)
        for name in ("jump_factor", "speed_factor"):
            self.assertEqual("NO_EXACT_COMPONENT_MATCH", candidates[name]["reason"])

    def test_dazed_structured_objects_are_unchanged(self):
        candidates = self.by_id["royalvariations:dazed"]["scalable_parameter_candidates"]
        expected = [{"primitive": primitive, "parameters": ["coefficient"],
                     "meaning": "Observation only; no scaling formula or eligibility change proposed.",
                     "candidate_form": "STRUCTURED", "needs_mapping_review": False}
                    for primitive in ("ATTRIBUTE_ATTACK_DAMAGE", "ATTRIBUTE_MOVEMENT_SPEED")]
        self.assertEqual(expected, candidates)

    def test_every_recovered_parameter_is_a_unique_exact_component_key(self):
        count = 0
        for mechanic in self.matrix["mechanics"]:
            for candidate in mechanic["scalable_parameter_candidates"]:
                if candidate["candidate_form"] != "RECOVERED_EXACT":
                    continue
                count += 1
                path, source = self.sources[(mechanic["mod_key"], mechanic["mechanic_id"])]
                name = candidate["candidate_name"]
                matching = []
                for index, component in enumerate(source["components"]):
                    containers = [component.get(field) or {} for field in ("numerical_parameters", "component_numerical_parameters")]
                    containers.append((source.get("component_numerical_parameters") or {}).get(f'{index}:{component["primitive"]}', {}))
                    if any(name in parameters for parameters in containers):
                        matching.append((index, component["primitive"]))
                self.assertEqual([(candidate["recovery"]["component_index"], candidate["primitive"])], matching)
                self.assertEqual([name], candidate["parameters"])
                self.assertEqual(path, candidate["recovery"]["source_review"])
                self.assertTrue(candidate["recovery"]["key_sources"])
        self.assertEqual(156, count)

    def test_replay_preserves_original_structured_entries_and_mechanic_context(self):
        original = deepcopy(self.original)
        replay = recovery.recover_matrix(original, self.sources, self.provenance)
        self.assertEqual(self.original, original)
        self.assertEqual(self.payload, recovery.matrix_extractor.serialize_matrix(replay))
        for before, after in zip(original["mechanics"], replay["mechanics"]):
            self.assertEqual({key: value for key, value in before.items() if key != "scalable_parameter_candidates"}, {key: value for key, value in after.items() if key != "scalable_parameter_candidates"})
            self.assertEqual([candidate for candidate in before["scalable_parameter_candidates"] if candidate["candidate_form"] == "STRUCTURED"], [candidate for candidate in after["scalable_parameter_candidates"] if candidate["candidate_form"] == "STRUCTURED"])

    def test_git_reads_are_only_the_three_allowlisted_completed_reviews(self):
        with patch.object(recovery.subprocess, "check_output", wraps=subprocess.check_output) as reads:
            recovery.read_legacy_reviews(self.original, self.ref)
        commands = [call.args[0] for call in reads.call_args_list]
        self.assertEqual([["git", "show", f"{self.ref}:{recovery.REVIEW_PATHS[mod]}"] for mod in sorted(recovery.REVIEW_PATHS)], commands)
        self.assertEqual(set(recovery.REVIEW_PATHS.values()), set(self.provenance["review_files"]))

    def test_cli_regeneration_is_byte_identical_and_does_not_change_input_or_branch(self):
        branch = subprocess.check_output(["git", "symbolic-ref", "HEAD"], cwd=recovery.matrix_extractor.REPO_ROOT)
        with tempfile.TemporaryDirectory() as directory:
            for name in ("first.json", "second.json"):
                output = Path(directory) / name
                subprocess.run([sys.executable, str(Path(recovery.__file__)), "--ref", self.ref, "--output", str(output)], cwd=recovery.matrix_extractor.REPO_ROOT, capture_output=True, check=True)
                self.assertEqual(self.payload, output.read_bytes())
        self.assertEqual(self.payload, recovery.INPUT.read_bytes())
        self.assertEqual(branch, subprocess.check_output(["git", "symbolic-ref", "HEAD"], cwd=recovery.matrix_extractor.REPO_ROOT))


class ExactKeyTests(unittest.TestCase):
    def legacy(self, name):
        return {"candidate_name": name, "candidate_form": "LEGACY_UNSCOPED", "needs_mapping_review": True, "available_component_primitives": ["NATIVE_DAMAGE_REQUEST"]}

    def test_case_spacing_synonyms_formulas_display_names_and_top_level_numbers_are_ignored(self):
        source = {"display_name": "duration Damage", "numerical_parameters": {"duration": 20},
                  "components": [{"primitive": "NATIVE_DAMAGE_REQUEST", "formula": "duration=20; hurt=damage",
                                  "numerical_parameters": {"damage": 8, "duration_ticks": 20}}]}
        for name in ("Damage", "DAMAGE", " damage", "damage ", "duration", "hurt", "box"):
            candidate = recovery.recover_candidate(self.legacy(name), "fixture.json", source)
            self.assertEqual("LEGACY_UNSCOPED", candidate["candidate_form"])
            self.assertEqual("NO_EXACT_COMPONENT_MATCH", candidate["reason"])
            self.assertNotIn("primitive", candidate)
        self.assertEqual("RECOVERED_EXACT", recovery.recover_candidate(self.legacy("damage"), "fixture.json", source)["candidate_form"])

    def test_duplicate_container_matches_count_one_component_and_values_are_not_interpreted(self):
        source = {"components": [{"primitive": "P", "numerical_parameters": {"zero": 0, "off": False, "null": None},
                                  "component_numerical_parameters": {"zero": 0}}],
                  "component_numerical_parameters": {"0:P": {"zero": 0, "indexed_only": 1}, "9:P": {"unbound": 1}}}
        for name in ("zero", "off", "null", "indexed_only"):
            candidate = recovery.recover_candidate(self.legacy(name), "fixture.json", source)
            self.assertEqual("RECOVERED_EXACT", candidate["candidate_form"])
            self.assertEqual("P", candidate["primitive"])
            self.assertEqual([name], candidate["parameters"])
        self.assertEqual(3, len(recovery.parameter_matches(source, "zero")[0]["key_sources"]))
        self.assertEqual([], recovery.parameter_matches(source, "unbound"))

    def test_two_components_with_the_same_primitive_are_still_ambiguous(self):
        source = {"components": [{"primitive": "P", "numerical_parameters": {"damage": 1}}, {"primitive": "P", "numerical_parameters": {"damage": 2}}]}
        candidate = recovery.recover_candidate(self.legacy("damage"), "fixture.json", source)
        self.assertEqual("AMBIGUOUS_COMPONENT_MATCH", candidate["reason"])
        self.assertEqual(["P", "P"], candidate["matching_primitives"])
        self.assertNotIn("primitive", candidate)

    def test_unknown_legacy_mod_is_rejected_before_any_git_read(self):
        matrix = {"mechanics": [{"mod_key": "other", "mechanic_id": "other:damage", "scalable_parameter_candidates": [self.legacy("damage")]}]}
        with patch.object(recovery.subprocess, "run") as git:
            with self.assertRaises(ValueError):
                recovery.read_legacy_reviews(matrix)
            git.assert_not_called()

    def test_structured_only_matrix_never_opens_any_review(self):
        provenance = {"source_ref": recovery.SOURCE_REF, "source_commit": "pinned", "review_files": [recovery.REVIEW_PATHS["cultofazazel"]]}
        matrix = {"mapping_recovery_source": provenance, "mechanics": [{"mod_key": "royalvariations", "mechanic_id": "royalvariations:dazed", "scalable_parameter_candidates": [{"candidate_form": "STRUCTURED"}]}]}
        with patch.object(recovery.subprocess, "run") as git:
            self.assertEqual(({}, provenance), recovery.read_legacy_reviews(matrix))
            git.assert_not_called()

    def test_partial_reviews_and_nonunique_or_missing_exact_ids_are_rejected(self):
        identity = ("cultofazazel", "cultofazazel:exact")
        matrix = {"mechanics": [{"mod_key": identity[0], "mechanic_id": identity[1], "scalable_parameter_candidates": [self.legacy("damage")]}]}
        effect = {"id": identity[1], "mod_key": identity[0], "components": []}
        for review in ({"status": "PARTIAL", "mod_key": identity[0], "effects": [effect]},
                       {"status": "COMPLETE", "mod_key": identity[0], "effects": []},
                       {"status": "COMPLETE", "mod_key": identity[0], "effects": [effect, effect]}):
            with patch.object(recovery.subprocess, "run") as resolve, patch.object(recovery.subprocess, "check_output", return_value=json.dumps(review).encode()):
                resolve.return_value.returncode = 0
                resolve.return_value.stdout = "pinned\n"
                with self.assertRaises(ValueError):
                    recovery.read_legacy_reviews(matrix)

    def test_mixing_recovery_commits_is_rejected_before_opening_reviews(self):
        matrix = {"mapping_recovery_source": {"source_commit": "old"}, "mechanics": [{"mod_key": "cultofazazel", "mechanic_id": "cultofazazel:exact", "scalable_parameter_candidates": [self.legacy("damage")]}]}
        with patch.object(recovery.subprocess, "run") as resolve, patch.object(recovery.subprocess, "check_output") as reads:
            resolve.return_value.returncode = 0
            resolve.return_value.stdout = "new\n"
            with self.assertRaises(ValueError):
                recovery.read_legacy_reviews(matrix)
            reads.assert_not_called()


if __name__ == "__main__":
    unittest.main()
