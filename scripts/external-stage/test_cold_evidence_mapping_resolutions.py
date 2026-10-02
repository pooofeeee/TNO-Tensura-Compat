import hashlib
import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
RESOLUTIONS = REPO_ROOT / "docs/external-stage/cold-evidence-mapping-resolutions.json"
EVIDENCE_ROOT = "docs/benchmarks/external-effects-catalog/native-evidence/"
CASES = {
    ("cultofazazel:azazel_wheel", "vertical"): (3, "cultofazazel-r2c2.json", "coa2-azazel", {"startWheelAttack", "performWheelAttack"}),
    ("cultofazazel:honey_properties", "factor"): (4, "cult-completion.json", "coa3-NetherExp", {"lambda$static$37", "lambda$static$49"}),
    ("cultofazazel:golem_healing_pull", "heal"): (5, "cultofazazel-r2c2.json", "coa2-golem", {"performHealingSuck"}),
}
OUTCOMES = {"MAP_EXISTING_COMPONENT", "MECHANIC_LEVEL_PARAMETER", "NON_SCALAR_OR_NATIVE_GATE", "NOT_INDEPENDENT_PARAMETER", "STILL_UNRESOLVED"}
PREVIOUS_BATCH_HASHES = {
    "mapping-decisions-batch1.json": "3935cba935ffdd1de2c0bd8d72ababca3f8a13fed1841edc6ad29209aa967d53",
    "mapping-decisions-batch2.json": "2b19346ab5c8f01d3706da668ad9d64011b686074440a8329cb3a95cdc3398d2",
    "mapping-decisions-batch3.json": "b49d653027b58068f9a6b54b3279d41922b0d791324edf96222a6fec563e9e63",
    "mapping-decisions-batch4.json": "8246222906a647f04186d5791a0343606c6b0888fd2d6bb29da78b7a9612c819",
    "mapping-decisions-batch5.json": "b78354847e2557a95eeb2526dc926d3f083a6816e9aa440ae16fedcc2321da36",
}


class ColdEvidenceMappingResolutionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = RESOLUTIONS.read_text()
        cls.document = json.loads(cls.payload)
        cls.records = cls.document["resolutions"]
        cls.by_pair = {(record["mechanic_id"], record["candidate_name"]): record for record in cls.records}
        cls.previous = {}
        for pair, (number, _, _, _) in CASES.items():
            path = f"docs/external-stage/mapping-decisions-batch{number}.json"
            batch = json.loads((REPO_ROOT / path).read_bytes())
            mechanic = next(m for m in batch["mechanics"] if m["mechanic_id"] == pair[0])
            decision = next(d for d in mechanic["decisions"] if d["candidate_name"] == pair[1])
            cls.previous[pair] = (path, batch, mechanic, decision)

    def test_exact_three_pairs_and_original_unresolved_decisions(self):
        self.assertEqual(3, len(self.records))
        self.assertEqual(set(CASES), set(self.by_pair))
        for pair, record in self.by_pair.items():
            path, _, _, decision = self.previous[pair]
            self.assertEqual(path, record["previous_batch"])
            self.assertEqual("NEEDS_COLD_EVIDENCE", decision["disposition"])
            self.assertEqual(decision["disposition"], record["previous_disposition"])

    def test_allowed_outcomes_confidence_and_existing_primitive_targets(self):
        for pair, record in self.by_pair.items():
            self.assertIn(record["final_outcome"], OUTCOMES)
            self.assertIn(record["confidence"], {"HIGH", "MEDIUM", "LOW"})
            self.assertTrue(record["reason"])
            self.assertLessEqual(len(record["reason"]), 240)
            if record["final_outcome"] == "MAP_EXISTING_COMPONENT":
                self.assertIn(record["target_primitive"], self.previous[pair][2]["packet_component_primitives"])
            else:
                self.assertNotIn("target_primitive", record)

    def test_non_independent_parameters_explain_distinct_runtime_values(self):
        expected = {
            "cultofazazel:azazel_wheel": {("FORCED_MOVEMENT", "horizontal", "horizontal", 1.2), ("FORCED_MOVEMENT", "recipient_vector_factor", "recipient_vector_factor", 1.5)},
            "cultofazazel:honey_properties": {("BLOCK_SPEED_FACTOR", "speed_factor", "factor", 0.4), ("BLOCK_JUMP_FACTOR", "jump_factor", "factor", 0.5)},
            "cultofazazel:golem_healing_pull": {("ITEM_CONSUMPTION", "item_heal", "heal", 4), ("LIFE_DRAIN", "player_heal", "heal", 6)},
        }
        for pair, record in self.by_pair.items():
            self.assertEqual("NOT_INDEPENDENT_PARAMETER", record["final_outcome"])
            parameters = record["existing_parameters"]
            self.assertEqual(2, len(parameters))
            self.assertEqual(expected[pair[0]], {(p["primitive"], p["parameter"], p.get("component_parameter", p["parameter"]), p["value"]) for p in parameters})
            for parameter in parameters:
                self.assertIn(parameter["primitive"], self.previous[pair][2]["packet_component_primitives"])
                self.assertNotEqual(record["candidate_name"], parameter["parameter"])
                self.assertIn(parameter["parameter"], record["reason"])
        wheel = self.by_pair[("cultofazazel:azazel_wheel", "vertical")]
        self.assertIn("retains current Y", wheel["reason"])
        self.assertIn("not a zero-Y write", wheel["reason"])

    def test_provenance_and_only_exact_allowed_witness_methods(self):
        self.assertEqual("external-effects-catalog-research", self.document["source_ref"])
        self.assertEqual("docs/benchmarks/external-effects-catalog/mod-reviews/cultofazazel.json", self.document["source_review_file"])
        self.assertRegex(self.document["source_commit"], r"^[0-9a-f]{40}$")
        for pair, record in self.by_pair.items():
            _, file_name, witness_id, methods = CASES[pair]
            previous_batch = self.previous[pair][1]
            self.assertEqual(previous_batch["source_ref"], self.document["source_ref"])
            self.assertEqual(previous_batch["source_commit"], self.document["source_commit"])
            self.assertEqual(1, len(record["evidence"]))
            evidence = record["evidence"][0]
            self.assertEqual(EVIDENCE_ROOT + file_name, evidence["file"])
            self.assertEqual(witness_id, evidence["witness_id"])
            self.assertEqual(sorted(methods), evidence["methods"])
            self.assertEqual(methods, set(evidence["method_code_sha256"]))
            for digest in evidence["method_code_sha256"].values():
                self.assertRegex(digest, r"^[0-9a-f]{64}$")
            self.assertTrue(evidence["instruction_offsets"])
            self.assertLessEqual(set(evidence["instruction_offsets"]), methods)
            for offsets in evidence["instruction_offsets"].values():
                self.assertTrue(offsets)
                self.assertEqual(sorted(set(offsets)), offsets)
                self.assertTrue(all(isinstance(offset, int) and offset >= 0 for offset in offsets))

    def test_deterministic_format_and_order(self):
        self.assertEqual(json.dumps(self.document, ensure_ascii=False, sort_keys=True, indent=2) + "\n", self.payload)
        pairs = [(record["mechanic_id"], record["candidate_name"]) for record in self.records]
        self.assertEqual(sorted(pairs), pairs)
        for record in self.records:
            parameters = [(p["primitive"], p["parameter"]) for p in record["existing_parameters"]]
            self.assertEqual(sorted(parameters), parameters)

    def test_batches1_through5_are_byte_unchanged(self):
        for filename, expected in PREVIOUS_BATCH_HASHES.items():
            path = REPO_ROOT / "docs/external-stage" / filename
            self.assertEqual(expected, hashlib.sha256(path.read_bytes()).hexdigest())


if __name__ == "__main__":
    unittest.main()
