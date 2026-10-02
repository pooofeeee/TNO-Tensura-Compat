import hashlib
import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
PACKET = REPO_ROOT / "docs/external-stage/mapping-review-packets.json"
DECISIONS = REPO_ROOT / "docs/external-stage/mapping-decisions-batch5.json"
PREVIOUS_BATCH_HASHES = {
    "mapping-decisions-batch1.json": "3935cba935ffdd1de2c0bd8d72ababca3f8a13fed1841edc6ad29209aa967d53",
    "mapping-decisions-batch2.json": "2b19346ab5c8f01d3706da668ad9d64011b686074440a8329cb3a95cdc3398d2",
    "mapping-decisions-batch3.json": "b49d653027b58068f9a6b54b3279d41922b0d791324edf96222a6fec563e9e63",
    "mapping-decisions-batch4.json": "8246222906a647f04186d5791a0343606c6b0888fd2d6bb29da78b7a9612c819",
}
MECHANIC_IDS = {f"cultofazazel:{name}" for name in ("azazel_shield", "believer_healing", "believer_sickness", "golem_healing_pull", "mask_rescue_repair", "welcomer_buff")}
DISPOSITIONS = {"MAP_EXISTING_COMPONENT", "MECHANIC_LEVEL_PARAMETER", "NON_SCALAR_OR_NATIVE_GATE", "NEEDS_COLD_EVIDENCE"}
SHAPES = {"VANILLA_REUSE", "PRIMITIVE_COMPOSITION", "CUSTOM_SPECIAL", "NON_SCALAR"}


class MappingDecisionBatch5Tests(unittest.TestCase):
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

    def test_resource_healing_control_and_lifecycle_distinctions(self):
        for mechanic in self.mechanics:
            self.assertEqual([component["primitive"] for component in self.packets[mechanic["mechanic_id"]]["components"]], mechanic["packet_component_primitives"])

        def decision(name, candidate):
            return next(item for item in self.by_id[f"cultofazazel:{name}"]["decisions"] if item["candidate_name"] == candidate)

        self.assertEqual(["DAMAGE_REJECTION", "HIT_COUNTER"], self.by_id["cultofazazel:azazel_shield"]["packet_component_primitives"])
        for candidate in ("min_hits", "max_hits"):
            self.assertEqual("HIT_COUNTER", decision("azazel_shield", candidate)["target_primitive"])
        for candidate in ("initial_box", "retained_distance"):
            self.assertEqual("MECHANIC_LEVEL_PARAMETER", decision("believer_healing", candidate)["disposition"])
        self.assertEqual(["AI_MOVEMENT_SUPPRESSION", "CURE"], self.by_id["cultofazazel:believer_sickness"]["packet_component_primitives"])
        for candidate in ("doctor_attempt_interval", "doctor_box", "doctor_reset"):
            self.assertEqual("MECHANIC_LEVEL_PARAMETER", decision("believer_sickness", candidate)["disposition"])
            self.assertEqual("MEDIUM", decision("believer_sickness", candidate)["confidence"])
        self.assertEqual(["FORCED_MOVEMENT", "ITEM_CONSUMPTION", "LIFE_DRAIN"], self.by_id["cultofazazel:golem_healing_pull"]["packet_component_primitives"])
        for candidate, primitive in (("pull", "FORCED_MOVEMENT"), ("item_heal", "ITEM_CONSUMPTION"), ("player_heal", "LIFE_DRAIN")):
            self.assertEqual(primitive, decision("golem_healing_pull", candidate)["target_primitive"])
        self.assertEqual("NEEDS_COLD_EVIDENCE", decision("golem_healing_pull", "heal")["disposition"])
        self.assertNotIn("target_primitive", decision("golem_healing_pull", "heal"))
        self.assertEqual("NON_SCALAR_OR_NATIVE_GATE", decision("golem_healing_pull", "phase_threshold")["disposition"])
        self.assertEqual("NON_SCALAR", decision("golem_healing_pull", "phase_threshold")["integration_shape"])
        self.assertEqual(["DEATH_CANCELLATION", "CHARGE_STATE", "VANILLA_EFFECT_BUNDLE", "EFFECT_REMOVAL"], self.by_id["cultofazazel:mask_rescue_repair"]["packet_component_primitives"])
        self.assertEqual("CHARGE_STATE", decision("mask_rescue_repair", "charges")["target_primitive"])
        for candidate in ("absorption_ticks", "fire_resistance_ticks", "regen_ticks"):
            self.assertEqual("VANILLA_EFFECT_BUNDLE", decision("mask_rescue_repair", candidate)["target_primitive"])
        self.assertEqual("DAMAGE_AND_RANGE_SWITCH", decision("welcomer_buff", "poll")["target_primitive"])
        self.assertEqual("CUSTOM_SPECIAL", decision("welcomer_buff", "poll")["integration_shape"])

    def test_deterministic_format_and_order(self):
        self.assertEqual(json.dumps(self.batch, ensure_ascii=False, sort_keys=True, indent=2) + "\n", self.payload)
        identities = [(mechanic["mod_key"], mechanic["mechanic_id"]) for mechanic in self.mechanics]
        self.assertEqual(sorted(identities), identities)
        self.assertEqual(sorted(MECHANIC_IDS), self.batch["reviewed_mechanic_ids"])
        for mechanic in self.mechanics:
            names = [decision["candidate_name"] for decision in mechanic["decisions"]]
            self.assertEqual(sorted(names), names)

    def test_batches1_through4_are_byte_unchanged(self):
        for filename, expected in PREVIOUS_BATCH_HASHES.items():
            path = REPO_ROOT / "docs/external-stage" / filename
            self.assertEqual(expected, hashlib.sha256(path.read_bytes()).hexdigest())


if __name__ == "__main__":
    unittest.main()
