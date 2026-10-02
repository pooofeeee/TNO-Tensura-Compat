from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import compile_resolved_candidates as compiler


class ResolvedCandidateRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = compiler.load_inputs()
        cls.original_sources = deepcopy(cls.sources)
        cls.registry = compiler.compile_registry(cls.sources)
        cls.payload = compiler.serialize_registry(cls.registry)
        cls.by_id = {mechanic["mechanic_id"]: mechanic for mechanic in cls.registry["mechanics"]}
        cls.cold = {(r["mechanic_id"], r["candidate_name"]): r for r in cls.sources[compiler.RESOLUTION_PATH]["resolutions"]}

    def reviewed_entry(self, mechanic_id, name):
        return next(entry for entry in self.by_id[mechanic_id]["candidates"] if entry["candidate_name"] == name)

    def test_all_105_mechanics_and_every_source_parameter_are_represented(self):
        matrix = self.sources[compiler.MATRIX_PATH]
        self.assertEqual(105, len(self.registry["mechanics"]))
        self.assertEqual({m["mechanic_id"] for m in matrix["mechanics"]}, set(self.by_id))
        total = 0
        for mechanic in matrix["mechanics"]:
            expected = []
            for candidate in mechanic["scalable_parameter_candidates"]:
                if candidate["candidate_form"] == "LEGACY_UNSCOPED":
                    expected.append((candidate["candidate_name"], candidate["candidate_name"]))
                else:
                    expected.extend((candidate.get("candidate_name", p), p) for p in candidate["parameters"])
            actual = self.by_id[mechanic["mechanic_id"]]["candidates"]
            self.assertEqual(Counter(expected), Counter((entry["candidate_name"], entry["parameter"]) for entry in actual))
            self.assertEqual(len(actual), len({(e.get("primitive"), e["candidate_name"], e["parameter"]) for e in actual}))
            total += len(actual)
        self.assertEqual(487, total)

    def test_structured_and_recovered_mappings_keep_exact_scope_and_provenance(self):
        counts = Counter()
        for mechanic in self.sources[compiler.MATRIX_PATH]["mechanics"]:
            for candidate in mechanic["scalable_parameter_candidates"]:
                form = candidate["candidate_form"]
                if form == "LEGACY_UNSCOPED":
                    continue
                for parameter in candidate["parameters"]:
                    entry = next(e for e in self.by_id[mechanic["mechanic_id"]]["candidates"] if e.get("primitive") == candidate["primitive"] and e["parameter"] == parameter)
                    self.assertEqual("MAP_EXISTING_COMPONENT", entry["disposition"])
                    self.assertEqual(form, entry["provenance"]["kind"])
                    self.assertEqual(compiler.MATRIX_PATH, entry["provenance"]["source"])
                    self.assertTrue(entry["independent_runtime_parameter"])
                    self.assertEqual(candidate.get("confidence"), entry["confidence"])
                    self.assertEqual(candidate.get("integration_shape"), entry["integration_shape"])
                    if "meaning" in candidate:
                        self.assertEqual(candidate["meaning"], entry["meaning"])
                    if "recovery" in candidate:
                        self.assertEqual(candidate["recovery"], entry["provenance"]["recovery"])
                    counts[form] += 1
        self.assertEqual({"STRUCTURED": 245, "RECOVERED_EXACT": 156}, dict(counts))

    def test_all_86_decisions_and_three_cold_overrides_are_incorporated(self):
        count = 0
        for path in compiler.BATCH_PATHS:
            for mechanic in self.sources[path]["mechanics"]:
                for decision in mechanic["decisions"]:
                    pair = (mechanic["mechanic_id"], decision["candidate_name"])
                    resolution = self.cold.get(pair)
                    effective = resolution or decision
                    entry = self.reviewed_entry(*pair)
                    self.assertEqual(effective.get("final_outcome", effective.get("disposition")), entry["disposition"])
                    self.assertEqual(decision["candidate_parameter"], entry["parameter"])
                    self.assertEqual(decision["integration_shape"], entry["integration_shape"])
                    self.assertEqual(effective["confidence"], entry["confidence"])
                    self.assertEqual(effective["reason"], entry["mapping_reason"])
                    if entry["disposition"] == "MAP_EXISTING_COMPONENT":
                        self.assertEqual(effective["target_primitive"], entry["primitive"])
                    else:
                        self.assertNotIn("primitive", entry)
                    self.assertEqual(compiler.RESOLUTION_PATH if resolution else path, entry["provenance"]["source"])
                    if resolution:
                        self.assertEqual(path, entry["provenance"]["semantic_review"])
                        self.assertEqual(resolution["evidence"], entry["provenance"]["evidence"])
                    count += 1
        self.assertEqual(86, count)
        self.assertEqual(3, len(self.cold))

    def test_three_aliases_are_audit_entries_and_keep_real_replacements(self):
        aliases = {(m["mechanic_id"], e["candidate_name"]): e for m in self.registry["mechanics"] for e in m["candidates"] if not e["independent_runtime_parameter"]}
        expected = {("cultofazazel:azazel_wheel", "vertical"), ("cultofazazel:honey_properties", "factor"), ("cultofazazel:golem_healing_pull", "heal")}
        self.assertEqual(expected, set(aliases))
        for pair, alias in aliases.items():
            self.assertEqual("NOT_INDEPENDENT_PARAMETER", alias["disposition"])
            self.assertEqual("COLD_EVIDENCE_RESOLUTION", alias["provenance"]["kind"])
            self.assertEqual(self.cold[pair]["existing_parameters"], alias["superseded_by"])
            for replacement in alias["superseded_by"]:
                real = next(e for e in self.by_id[pair[0]]["candidates"] if e.get("primitive") == replacement["primitive"] and e["parameter"] == replacement["parameter"])
                self.assertTrue(real["independent_runtime_parameter"])

    def test_component_formulas_and_mechanic_context_are_unchanged_without_policy(self):
        forbidden = {"stage_eligibility", "eligible", "scaling_policy", "multiplier", "cap", "floor", "ownership", "runtime_hook"}
        for source in self.sources[compiler.MATRIX_PATH]["mechanics"]:
            record = self.by_id[source["mechanic_id"]]
            for field, value in source.items():
                if field != "scalable_parameter_candidates":
                    self.assertEqual(value, record[field])
            for entry in record["candidates"]:
                self.assertFalse(forbidden & set(entry))
                if entry["disposition"] == "MAP_EXISTING_COMPONENT":
                    self.assertIn(entry["primitive"], {c["primitive"] for c in record["components"]})
        dazed = self.by_id["royalvariations:dazed"]
        self.assertEqual({("ATTRIBUTE_MOVEMENT_SPEED", "coefficient"), ("ATTRIBUTE_ATTACK_DAMAGE", "coefficient")}, {(e["primitive"], e["parameter"]) for e in dazed["candidates"]})

    def test_summary_counts_cover_every_entry(self):
        entries = [e for m in self.registry["mechanics"] for e in m["candidates"]]
        summary = self.registry["summary"]
        expected = {"total_candidate_mechanics": 105, "total_candidate_entries": 487, "independent_runtime_parameter_count": 484, "not_independent_parameter_count": 3, "reviewed_decision_count": 86, "cold_evidence_resolution_count": 3, "unresolved_count": 0}
        for field, value in expected.items():
            self.assertEqual(value, summary[field])
        self.assertEqual(dict(Counter(e["integration_shape"] or "UNSPECIFIED" for e in entries)), summary["counts_by_integration_shape"])
        self.assertEqual(dict(Counter(e["disposition"] for e in entries)), summary["counts_by_disposition"])
        self.assertEqual({"STRUCTURED": 245, "RECOVERED_EXACT": 156, "SEMANTIC_REVIEW": 83, "COLD_EVIDENCE_RESOLUTION": 3}, summary["counts_by_provenance"])
        self.assertFalse(any(e["disposition"] in {"NEEDS_COLD_EVIDENCE", "STILL_UNRESOLVED"} for e in entries))

    def test_deterministic_order_and_byte_identical_cli_regeneration(self):
        identities = [(m["mod_key"], m["mechanic_id"]) for m in self.registry["mechanics"]]
        self.assertEqual(sorted(identities), identities)
        for mechanic in self.registry["mechanics"]:
            keys = [(e.get("primitive", ""), e["parameter"], e["candidate_name"]) for e in mechanic["candidates"]]
            self.assertEqual(sorted(keys), keys)
        self.assertEqual(self.payload, compiler.OUTPUT.read_bytes())
        original = {path: (compiler.REPO_ROOT / path).read_bytes() for path in compiler.INPUT_PATHS}
        with tempfile.TemporaryDirectory() as directory:
            for name in ("first.json", "second.json"):
                output = Path(directory) / name
                subprocess.run([sys.executable, str(Path(compiler.__file__)), "--output", str(output)], cwd=compiler.REPO_ROOT, capture_output=True, check=True)
                self.assertEqual(self.payload, output.read_bytes())
        self.assertEqual(original, {path: (compiler.REPO_ROOT / path).read_bytes() for path in compiler.INPUT_PATHS})

    def test_only_the_seven_production_inputs_are_read_and_never_mutated(self):
        seen = []
        read_bytes = Path.read_bytes

        def record_read(path):
            seen.append(path)
            return read_bytes(path)

        with patch.object(Path, "read_bytes", record_read):
            compiler.load_inputs()
        self.assertCountEqual([compiler.REPO_ROOT / path for path in compiler.INPUT_PATHS], seen)
        self.assertEqual(list(compiler.INPUT_PATHS), self.registry["source_files"])
        self.assertEqual(self.original_sources, self.sources)

    def test_missing_duplicate_contradictory_and_unresolved_inputs_are_rejected(self):
        for case in ("missing_review", "duplicate_review", "missing_cold", "still_unresolved", "bad_previous_batch", "missing_replacement", "duplicate_mechanic"):
            with self.subTest(case=case):
                sources = deepcopy(self.sources)
                decisions = sources[compiler.BATCH_PATHS[0]]["mechanics"][0]["decisions"]
                resolutions = sources[compiler.RESOLUTION_PATH]["resolutions"]
                if case == "missing_review":
                    decisions.pop()
                elif case == "duplicate_review":
                    decisions.append(deepcopy(decisions[0]))
                elif case == "missing_cold":
                    resolutions.pop()
                elif case == "still_unresolved":
                    resolutions[0]["final_outcome"] = "STILL_UNRESOLVED"
                elif case == "bad_previous_batch":
                    resolutions[0]["previous_batch"] = compiler.BATCH_PATHS[0]
                elif case == "missing_replacement":
                    resolutions[0]["existing_parameters"][0]["parameter"] = "not_a_candidate"
                else:
                    sources[compiler.MATRIX_PATH]["mechanics"].append(deepcopy(sources[compiler.MATRIX_PATH]["mechanics"][0]))
                with self.assertRaises(ValueError):
                    compiler.compile_registry(sources)


if __name__ == "__main__":
    unittest.main()
