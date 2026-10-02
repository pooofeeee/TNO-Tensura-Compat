import hashlib
import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
PACKET = REPO_ROOT / "docs/external-stage/mapping-review-packets.json"
DECISIONS = REPO_ROOT / "docs/external-stage/mapping-decisions-batch4.json"
PREVIOUS_BATCH_HASHES = {
    "mapping-decisions-batch1.json": "3935cba935ffdd1de2c0bd8d72ababca3f8a13fed1841edc6ad29209aa967d53",
    "mapping-decisions-batch2.json": "2b19346ab5c8f01d3706da668ad9d64011b686074440a8329cb3a95cdc3398d2",
    "mapping-decisions-batch3.json": "b49d653027b58068f9a6b54b3279d41922b0d791324edf96222a6fec563e9e63",
}
MECHANIC_IDS = {f"cultofazazel:{name}" for name in ("golem_launch", "guardian_mega_punch", "guardian_rapid_melee", "honey_properties", "laser_hazard", "midas_fire_ring", "native_fangs")}
DISPOSITIONS = {"MAP_EXISTING_COMPONENT", "MECHANIC_LEVEL_PARAMETER", "NON_SCALAR_OR_NATIVE_GATE", "NEEDS_COLD_EVIDENCE"}
SHAPES = {"VANILLA_REUSE", "PRIMITIVE_COMPOSITION", "CUSTOM_SPECIAL", "NON_SCALAR"}


class MappingDecisionBatch4Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        packet = json.loads(PACKET.read_bytes())
        cls.packets = {mechanic["mechanic_id"]: mechanic for mechanic in packet["mechanics"] if mechanic["mechanic_id"] in MECHANIC_IDS}
        cls.source = {field: packet[field] for field in ("source_ref", "source_commit")}
        cls.payload = DECISIONS.read_text()
        cls.batch = json.loads(cls.payload)
        cls.mechanics = cls.batch["mechanics"]
        cls.by_id = {mechanic["mechanic_id"]: mechanic for mechanic in cls.mechanics}

    def test_exact_seven_mechanics_nineteen_candidates_and_no_other_mechanics(self):
        self.assertEqual(7, len(self.mechanics))
        self.assertEqual(MECHANIC_IDS, set(self.by_id))
        self.assertEqual(MECHANIC_IDS, set(self.batch["reviewed_mechanic_ids"]))
        self.assertEqual(7, len(self.batch["reviewed_mechanic_ids"]))
        self.assertEqual(19, sum(len(mechanic["decisions"]) for mechanic in self.mechanics))
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

    def test_damage_motion_burn_and_delivery_distinctions(self):
        for mechanic in self.mechanics:
            self.assertEqual([component["primitive"] for component in self.packets[mechanic["mechanic_id"]]["components"]], mechanic["packet_component_primitives"])

        def decision(name, candidate):
            return next(item for item in self.by_id[f"cultofazazel:{name}"]["decisions"] if item["candidate_name"] == candidate)

        self.assertEqual("EXTRA_LAUNCH", decision("golem_launch", "extra_Y")["target_primitive"])
        self.assertEqual("CUSTOM_SPECIAL", decision("golem_launch", "extra_Y")["integration_shape"])
        for name in ("guardian_mega_punch", "guardian_rapid_melee"):
            self.assertEqual("NATIVE_DAMAGE_REQUEST", decision(name, "damage")["target_primitive"])
        self.assertEqual(["NATIVE_DAMAGE_REQUEST", "FORCED_MOVEMENT"], self.by_id["cultofazazel:guardian_mega_punch"]["packet_component_primitives"])
        self.assertEqual(["COOLDOWN_RESET", "NATIVE_DAMAGE_REQUEST"], self.by_id["cultofazazel:guardian_rapid_melee"]["packet_component_primitives"])
        self.assertEqual("MECHANIC_LEVEL_PARAMETER", decision("guardian_mega_punch", "normal_goal_cooldown_ticks")["disposition"])
        for candidate in ("hits_max", "hits_min", "interval"):
            self.assertEqual("MECHANIC_LEVEL_PARAMETER", decision("guardian_rapid_melee", candidate)["disposition"])
        for candidate, primitive in (("speed_factor", "BLOCK_SPEED_FACTOR"), ("jump_factor", "BLOCK_JUMP_FACTOR")):
            self.assertEqual(primitive, decision("honey_properties", candidate)["target_primitive"])
        self.assertEqual("NEEDS_COLD_EVIDENCE", decision("honey_properties", "factor")["disposition"])
        self.assertNotIn("target_primitive", decision("honey_properties", "factor"))
        self.assertEqual(["NATIVE_DAMAGE_REQUEST", "BURN", "HAZARD_MOTION"], self.by_id["cultofazazel:laser_hazard"]["packet_component_primitives"])
        self.assertEqual("BURN", decision("laser_hazard", "fire_ticks")["target_primitive"])
        for candidate in ("height", "width"):
            self.assertEqual("MECHANIC_LEVEL_PARAMETER", decision("laser_hazard", candidate)["disposition"])
        self.assertEqual(["FIRE_DAMAGE", "BURN"], self.by_id["cultofazazel:midas_fire_ring"]["packet_component_primitives"])
        self.assertEqual("BURN", decision("midas_fire_ring", "ignite_seconds")["target_primitive"])
        for candidate in ("box", "duration", "max_radius"):
            self.assertEqual("MECHANIC_LEVEL_PARAMETER", decision("midas_fire_ring", candidate)["disposition"])
        for candidate in ("bursts", "per_burst"):
            self.assertEqual("MECHANIC_LEVEL_PARAMETER", decision("native_fangs", candidate)["disposition"])
            self.assertEqual("VANILLA_REUSE", decision("native_fangs", candidate)["integration_shape"])

    def test_deterministic_format_and_order(self):
        self.assertEqual(json.dumps(self.batch, ensure_ascii=False, sort_keys=True, indent=2) + "\n", self.payload)
        identities = [(mechanic["mod_key"], mechanic["mechanic_id"]) for mechanic in self.mechanics]
        self.assertEqual(sorted(identities), identities)
        self.assertEqual(sorted(MECHANIC_IDS), self.batch["reviewed_mechanic_ids"])
        for mechanic in self.mechanics:
            names = [decision["candidate_name"] for decision in mechanic["decisions"]]
            self.assertEqual(sorted(names), names)

    def test_batches1_through3_are_byte_unchanged(self):
        for filename, expected in PREVIOUS_BATCH_HASHES.items():
            path = REPO_ROOT / "docs/external-stage" / filename
            self.assertEqual(expected, hashlib.sha256(path.read_bytes()).hexdigest())


if __name__ == "__main__":
    unittest.main()
