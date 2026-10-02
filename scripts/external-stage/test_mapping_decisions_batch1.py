import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
PACKET = REPO_ROOT / "docs/external-stage/mapping-review-packets.json"
DECISIONS = REPO_ROOT / "docs/external-stage/mapping-decisions-batch1.json"
MECHANIC_IDS = {
    "twilightforest:frosted_package", "twilightforest:ice_bomb_package",
    "variantsandventures:frozen_ticks_set", "variantsandventures:poison_payload",
    "variantsandventures:underwater_arrow_inertia", "variantsandventures:zombie_powder_snow_conversion",
}
DISPOSITIONS = {"MAP_EXISTING_COMPONENT", "MECHANIC_LEVEL_PARAMETER", "NON_SCALAR_OR_NATIVE_GATE", "NEEDS_COLD_EVIDENCE"}
SHAPES = {"VANILLA_REUSE", "PRIMITIVE_COMPOSITION", "CUSTOM_SPECIAL", "NON_SCALAR"}


class MappingDecisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        packet = json.loads(PACKET.read_bytes())
        cls.packets = {mechanic["mechanic_id"]: mechanic for mechanic in packet["mechanics"] if mechanic["mechanic_id"] in MECHANIC_IDS}
        cls.source = {field: packet[field] for field in ("source_ref", "source_commit")}
        cls.payload = DECISIONS.read_text()
        cls.batch = json.loads(cls.payload)
        cls.mechanics = cls.batch["mechanics"]
        cls.by_id = {mechanic["mechanic_id"]: mechanic for mechanic in cls.mechanics}

    def test_exact_six_mechanics_sixteen_candidates_and_no_cult_of_azazel(self):
        self.assertEqual(6, len(self.mechanics))
        self.assertEqual(MECHANIC_IDS, set(self.by_id))
        self.assertEqual(MECHANIC_IDS, set(self.batch["reviewed_mechanic_ids"]))
        self.assertEqual(6, len(self.batch["reviewed_mechanic_ids"]))
        self.assertEqual(16, sum(len(mechanic["decisions"]) for mechanic in self.mechanics))
        self.assertEqual({"twilightforest", "variantsandventures"}, {mechanic["mod_key"] for mechanic in self.mechanics})
        for mechanic in self.mechanics:
            packet = self.packets[mechanic["mechanic_id"]]
            self.assertEqual(packet["mod_key"], mechanic["mod_key"])
            self.assertEqual(packet["primary_classification"], mechanic["primary_classification"])
            names = [decision["candidate_name"] for decision in mechanic["decisions"]]
            self.assertEqual(len(names), len(set(names)))
            self.assertCountEqual([candidate["candidate_name"] for candidate in packet["unresolved_candidates"]], names)

    def test_dispositions_shapes_confidence_and_existing_primitive_targets(self):
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

    def test_packet_provenance_and_evidence_paths(self):
        self.assertEqual("docs/external-stage/mapping-review-packets.json", self.batch["source_packet"])
        self.assertEqual(self.source, {field: self.batch[field] for field in self.source})
        allowed_roots = {"actual_behavior", "closest_vanilla_equivalent", "vanilla_differences", "components", "numerical_parameters", "binary_parameters", "primary_classification"}
        for mechanic in self.mechanics:
            packet = self.packets[mechanic["mechanic_id"]]
            for decision in mechanic["decisions"]:
                self.assertTrue(decision["packet_evidence"])
                for path in decision["packet_evidence"]:
                    parts = path.split("/")[1:]
                    self.assertIn(parts[0], allowed_roots)
                    value = packet
                    for part in parts:
                        key = part.replace("~1", "/").replace("~0", "~")
                        value = value[int(key)] if isinstance(value, list) else value[key]
                    self.assertIsNotNone(value)

    def test_native_component_distinctions_and_expected_candidate_owners(self):
        for mechanic in self.mechanics:
            self.assertEqual([component["primitive"] for component in self.packets[mechanic["mechanic_id"]]["components"]], mechanic["packet_component_primitives"])
        def decision(mechanic_id, name):
            return next(item for item in self.by_id[mechanic_id]["decisions"] if item["candidate_name"] == name)
        frozen = "variantsandventures:frozen_ticks_set"
        self.assertEqual("FREEZE", decision(frozen, "assigned frozen ticks")["target_primitive"])
        self.assertEqual("DIRECT_DAMAGE", decision(frozen, "snowball requested damage")["target_primitive"])
        self.assertEqual("PROJECTILE_MOTION", decision("variantsandventures:underwater_arrow_inertia", "water velocity retention coefficient")["target_primitive"])
        frosted = "twilightforest:frosted_package"
        self.assertEqual("MOVEMENT_ATTRIBUTE", decision(frosted, "movement coefficient")["target_primitive"])
        self.assertEqual("NATIVE_FREEZE_DAMAGE", decision(frosted, "freeze damage increment")["target_primitive"])
        for name in ("amplifier", "duration"):
            self.assertEqual("MECHANIC_LEVEL_PARAMETER", decision(frosted, name)["disposition"])
        bomb = "twilightforest:ice_bomb_package"
        self.assertEqual("CUSTOM_DAMAGE_REQUEST", decision(bomb, "damage request")["target_primitive"])
        self.assertEqual("FROSTED", decision(bomb, "status duration")["target_primitive"])
        for name in ("zone bounds", "zone interval", "zone lifetime"):
            self.assertEqual("REPEATED_ZONE", decision(bomb, name)["target_primitive"])
        self.assertTrue({"YETI_REPLACEMENT", "TERRAIN_FREEZE"} <= set(self.by_id[bomb]["packet_component_primitives"]))

    def test_deterministic_format_and_record_order(self):
        canonical = json.dumps(self.batch, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
        self.assertEqual(canonical, self.payload)
        identities = [(mechanic["mod_key"], mechanic["mechanic_id"]) for mechanic in self.mechanics]
        self.assertEqual(sorted(identities), identities)
        self.assertEqual(sorted(MECHANIC_IDS), self.batch["reviewed_mechanic_ids"])
        for mechanic in self.mechanics:
            names = [decision["candidate_name"] for decision in mechanic["decisions"]]
            self.assertEqual(sorted(names), names)


if __name__ == "__main__":
    unittest.main()
