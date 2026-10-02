import hashlib
import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
PACKET = REPO_ROOT / "docs/external-stage/mapping-review-packets.json"
DECISIONS = REPO_ROOT / "docs/external-stage/mapping-decisions-batch2.json"
BATCH1 = REPO_ROOT / "docs/external-stage/mapping-decisions-batch1.json"
BATCH1_SHA256 = "3935cba935ffdd1de2c0bd8d72ababca3f8a13fed1841edc6ad29209aa967d53"
MECHANIC_IDS = {f"cultofazazel:{name}" for name in ("bad_omen", "darkness", "poison", "slowness", "unluck", "wither")}
DISPOSITIONS = {"MAP_EXISTING_COMPONENT", "MECHANIC_LEVEL_PARAMETER", "NON_SCALAR_OR_NATIVE_GATE", "NEEDS_COLD_EVIDENCE"}
SHAPES = {"VANILLA_REUSE", "PRIMITIVE_COMPOSITION", "CUSTOM_SPECIAL", "NON_SCALAR"}


class MappingDecisionBatch2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        packet = json.loads(PACKET.read_bytes())
        cls.packets = {mechanic["mechanic_id"]: mechanic for mechanic in packet["mechanics"] if mechanic["mechanic_id"] in MECHANIC_IDS}
        cls.source = {field: packet[field] for field in ("source_ref", "source_commit")}
        cls.payload = DECISIONS.read_text()
        cls.batch = json.loads(cls.payload)
        cls.mechanics = cls.batch["mechanics"]
        cls.by_id = {mechanic["mechanic_id"]: mechanic for mechanic in cls.mechanics}

    def test_exact_six_mechanics_seventeen_candidates_and_no_other_mechanics(self):
        self.assertEqual(6, len(self.mechanics))
        self.assertEqual(MECHANIC_IDS, set(self.by_id))
        self.assertEqual(MECHANIC_IDS, set(self.batch["reviewed_mechanic_ids"]))
        self.assertEqual(6, len(self.batch["reviewed_mechanic_ids"]))
        self.assertEqual(17, sum(len(mechanic["decisions"]) for mechanic in self.mechanics))
        self.assertEqual({"cultofazazel"}, {mechanic["mod_key"] for mechanic in self.mechanics})
        for mechanic in self.mechanics:
            packet = self.packets[mechanic["mechanic_id"]]
            self.assertEqual(packet["mod_key"], mechanic["mod_key"])
            self.assertEqual(packet["primary_classification"], mechanic["primary_classification"])
            names = [decision["candidate_name"] for decision in mechanic["decisions"]]
            self.assertEqual(len(names), len(set(names)))
            self.assertCountEqual([candidate["candidate_name"] for candidate in packet["unresolved_candidates"]], names)

    def test_allowed_values_existing_targets_and_concise_reasons(self):
        for mechanic in self.mechanics:
            primitives = {component["primitive"] for component in self.packets[mechanic["mechanic_id"]]["components"]}
            for decision in mechanic["decisions"]:
                self.assertIn(decision["disposition"], DISPOSITIONS)
                self.assertIn(decision["integration_shape"], SHAPES)
                self.assertIn(decision["confidence"], {"HIGH", "MEDIUM", "LOW"})
                self.assertEqual(decision["candidate_name"], decision["candidate_parameter"])
                self.assertTrue(decision["reason"])
                self.assertLessEqual(len(decision["reason"]), 240)
                if decision["disposition"] == "MAP_EXISTING_COMPONENT":
                    self.assertIn(decision["target_primitive"], primitives)
                else:
                    self.assertNotIn("target_primitive", decision)

    def test_packet_provenance_and_resolvable_evidence_pointers(self):
        self.assertEqual("docs/external-stage/mapping-review-packets.json", self.batch["source_packet"])
        self.assertEqual(self.source, {field: self.batch[field] for field in self.source})
        allowed_roots = {"actual_behavior", "closest_vanilla_equivalent", "vanilla_differences", "components", "numerical_parameters", "binary_parameters", "primary_classification"}
        for mechanic in self.mechanics:
            for decision in mechanic["decisions"]:
                self.assertTrue(decision["packet_evidence"])
                for path in decision["packet_evidence"]:
                    self.assertTrue(path.startswith("/"))
                    parts = path.split("/")[1:]
                    self.assertIn(parts[0], allowed_roots)
                    value = self.packets[mechanic["mechanic_id"]]
                    for part in parts:
                        key = part.replace("~1", "/").replace("~0", "~")
                        value = value[int(key)] if isinstance(value, list) else value[key]
                    self.assertIsNotNone(value)

    def test_effect_primitives_stay_independent_and_bad_omen_search_stays_separate(self):
        for mechanic in self.mechanics:
            self.assertEqual([component["primitive"] for component in self.packets[mechanic["mechanic_id"]]["components"]], mechanic["packet_component_primitives"])
        bad_omen = self.by_id["cultofazazel:bad_omen"]["decisions"][0]
        self.assertEqual("boss_box", bad_omen["candidate_name"])
        self.assertEqual("AGGRO_TRIGGER", bad_omen["target_primitive"])
        self.assertEqual("CUSTOM_SPECIAL", bad_omen["integration_shape"])
        for name in ("darkness", "poison", "slowness", "unluck", "wither"):
            for decision in self.by_id[f"cultofazazel:{name}"]["decisions"]:
                if decision["disposition"] == "MAP_EXISTING_COMPONENT":
                    self.assertEqual(f"MOB_EFFECT_{name.upper()}", decision["target_primitive"])

    def test_deterministic_format_and_order(self):
        self.assertEqual(json.dumps(self.batch, ensure_ascii=False, sort_keys=True, indent=2) + "\n", self.payload)
        identities = [(mechanic["mod_key"], mechanic["mechanic_id"]) for mechanic in self.mechanics]
        self.assertEqual(sorted(identities), identities)
        self.assertEqual(sorted(MECHANIC_IDS), self.batch["reviewed_mechanic_ids"])
        for mechanic in self.mechanics:
            names = [decision["candidate_name"] for decision in mechanic["decisions"]]
            self.assertEqual(sorted(names), names)

    def test_batch1_is_byte_unchanged(self):
        self.assertEqual(BATCH1_SHA256, hashlib.sha256(BATCH1.read_bytes()).hexdigest())


if __name__ == "__main__":
    unittest.main()
