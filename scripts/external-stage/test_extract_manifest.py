import collections
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import extract_manifest as extractor


class ManifestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = extractor.OUTPUT.read_bytes()
        cls.manifest = json.loads(cls.payload)
        cls.commit, cls.reviews = extractor.read_reviews(extractor.REPO_ROOT, cls.manifest["source_commit"])
        cls.records = cls.manifest["mechanics"]
        cls.by_identity = {(record["mod_key"], record["mechanic_id"]): record for record in cls.records}

    def test_all_nine_completed_reviews_are_fully_represented(self):
        names = {
            "royalvariations", "cultofazazel", "variantsandventures", "friendsandfoes",
            "twilightforest", "iceandfire", "eternalstarlight", "block_factorys_bosses",
            "bosses_of_mass_destruction",
        }
        expected_paths = {f"docs/benchmarks/external-effects-catalog/mod-reviews/{name}.json" for name in names}
        self.assertEqual(expected_paths, set(self.manifest["source_reviews"]))
        self.assertEqual(9, len(self.reviews))
        self.assertEqual(names, {record["mod_key"] for record in self.records})
        source_counts = collections.Counter()
        for _, review in self.reviews:
            self.assertEqual("COMPLETE", review["status"])
            source_counts.update(effect["mod_key"] for effect in review["effects"])
        self.assertEqual(source_counts, collections.Counter(record["mod_key"] for record in self.records))

    def test_cataclysm_is_absent(self):
        self.assertFalse(any("cataclysm" in path for path in self.manifest["source_reviews"]))
        self.assertFalse(any(record["mod_key"] == "cataclysm" for record in self.records))

    def test_required_keys_exact_source_ids_uniqueness_and_stable_sorting(self):
        required = {"mod_key", "mechanic_id", "primary_classification", "stage_review_bucket"}
        for record in self.records:
            self.assertTrue(required <= record.keys())
        identities = [(record["mod_key"], record["mechanic_id"]) for record in self.records]
        source_identities = [(effect["mod_key"], effect["id"]) for _, review in self.reviews for effect in review["effects"]]
        self.assertEqual(sorted(source_identities), identities)
        self.assertEqual(len(identities), len(set(identities)))

    def test_every_bucket_obeys_only_the_fixed_classification_mapping(self):
        expected = {
            "VANILLA_DIRECT": "VANILLA_REUSE_CANDIDATE",
            "VANILLA_EQUIVALENT": "VANILLA_REUSE_CANDIDATE",
            "VANILLA_COMPOSITE": "PRIMITIVE_COMPOSITION_CANDIDATE",
            "VANILLA_LIKE_EXTENDED": "PRIMITIVE_COMPOSITION_CANDIDATE",
            "BINARY_MECHANIC": "NON_SCALAR_OR_SPECIAL_REVIEW",
        }
        for record in self.records:
            classification = record["primary_classification"]
            bucket = "CUSTOM_POLICY_REVIEW" if classification.startswith("CUSTOM_") else expected.get(classification, "UNCLASSIFIED_REVIEW")
            self.assertEqual(bucket, record["stage_review_bucket"])
        for classification in (None, "", "UNKNOWN", "custom_damage", {"name": "CUSTOM_DAMAGE"}):
            self.assertEqual("UNCLASSIFIED_REVIEW", extractor.stage_review_bucket(classification))
        self.assertEqual("CUSTOM_POLICY_REVIEW", extractor.stage_review_bucket("CUSTOM_FUTURE"))

    def test_dazed_retains_classification_both_attributes_and_exact_candidates(self):
        dazed = self.by_identity[("royalvariations", "royalvariations:dazed")]
        review = next(review for _, review in self.reviews if review["mod_key"] == "royalvariations")
        source = next(effect for effect in review["effects"] if effect["id"] == "royalvariations:dazed")
        self.assertEqual("VANILLA_COMPOSITE", dazed["primary_classification"])
        self.assertEqual({"ATTRIBUTE_MOVEMENT_SPEED", "ATTRIBUTE_ATTACK_DAMAGE"}, {component["primitive"] for component in dazed["components"]})
        self.assertEqual({"MOVEMENT_SPEED", "ATTACK_DAMAGE"}, {component["attribute"] for component in dazed["components"]})
        self.assertEqual(source["scalable_parameter_candidates"], dazed["scalable_parameter_candidates"])
        for component in dazed["components"]:
            self.assertEqual("ADD_MULTIPLIED_TOTAL", component["operation"])
            self.assertEqual(-0.6, component["coefficient"])

    def test_optional_source_fields_and_candidate_aliases_are_preserved_without_invention(self):
        copied = ("display_name", "closest_vanilla_equivalent", "delivery_paths", "primary_test_source", "alternate_sources", "inspection_status", "unresolved_ambiguities")
        for _, review in self.reviews:
            for source in review["effects"]:
                record = self.by_identity[(source["mod_key"], source["id"])]
                self.assertEqual(source["primary_classification"], record["primary_classification"])
                for field in copied:
                    if field in source:
                        self.assertEqual(source[field], record[field])
                    else:
                        self.assertNotIn(field, record)
                candidates = next((field for field in ("scalable_parameter_candidates", "scalable_parameters") if field in source), None)
                if candidates:
                    self.assertEqual(source[candidates], record["scalable_parameter_candidates"])
                else:
                    self.assertNotIn("scalable_parameter_candidates", record)

    def test_manifest_contains_only_the_compact_allowlisted_fields(self):
        allowed = {
            "mod_key", "mechanic_id", "display_name", "primary_classification", "stage_review_bucket",
            "closest_vanilla_equivalent", "vanilla_differences", "components", "scalable_parameter_candidates",
            "delivery_paths", "primary_test_source", "alternate_sources", "inspection_status", "unresolved_ambiguities",
        }
        for record in self.records:
            self.assertTrue(record.keys() <= allowed)
            for component in record.get("components", []):
                self.assertTrue(component.keys() <= {"primitive", "attribute", "operation", "formula", "coefficient"})

    def test_all_prose_excerpts_are_bounded_source_prefixes_and_component_facts_are_exact(self):
        def assert_excerpt(source, compact):
            normalized = " ".join(source.split())
            self.assertLessEqual(len(compact), 240)
            if len(normalized) <= 240:
                self.assertEqual(normalized, compact)
            else:
                self.assertTrue(compact.endswith("…"))
                self.assertTrue(normalized.startswith(compact[:-1]))

        def difference_notes(value):
            if isinstance(value, str):
                return [value]
            if isinstance(value, dict):
                return [component["native_relation"] for component in value["component_contracts"]]
            return [note for item in value for note in difference_notes(item)]

        for _, review in self.reviews:
            for source in review["effects"]:
                record = self.by_identity[(source["mod_key"], source["id"])]
                differences = difference_notes(source["vanilla_differences"])
                self.assertEqual(len(differences), len(record["vanilla_differences"]))
                for original, compact in zip(differences, record["vanilla_differences"]):
                    assert_excerpt(original, compact)
                self.assertEqual(len(source["components"]), len(record["components"]))
                for original, compact in zip(source["components"], record["components"]):
                    for field in ("primitive", "attribute", "operation"):
                        if field in original:
                            self.assertEqual(original[field], compact[field])
                        else:
                            self.assertNotIn(field, compact)
                    numeric = original.get("numerical_parameters", {})
                    formula = numeric.get("formula", original.get("formula"))
                    if formula is not None:
                        assert_excerpt(formula, compact["formula"])
                    coefficient = original.get("coefficient", numeric.get("coefficient"))
                    if coefficient is not None:
                        self.assertEqual(coefficient, compact["coefficient"])
                    else:
                        self.assertNotIn("coefficient", compact)

    def test_cli_reruns_are_byte_identical_and_leave_the_branch_unchanged(self):
        before = subprocess.check_output(["git", "symbolic-ref", "HEAD"], cwd=extractor.REPO_ROOT)
        with tempfile.TemporaryDirectory() as directory:
            for name in ("first.json", "second.json"):
                output = Path(directory) / name
                subprocess.run([sys.executable, str(Path(extractor.__file__)), "--output", str(output)], cwd=extractor.REPO_ROOT, capture_output=True, check=True)
                self.assertEqual(self.payload, output.read_bytes())
        self.assertEqual(before, subprocess.check_output(["git", "symbolic-ref", "HEAD"], cwd=extractor.REPO_ROOT))


class ProjectionTests(unittest.TestCase):
    def test_absent_and_null_fields_stay_absent_or_null_without_classifying_by_name(self):
        record = extractor.reduce_mechanic({"mod_key": "example", "id": "original-id", "display_name": "CUSTOM_DAMAGE", "components": None})
        self.assertIsNone(record["primary_classification"])
        self.assertEqual("UNCLASSIFIED_REVIEW", record["stage_review_bucket"])
        self.assertIsNone(record["components"])
        self.assertNotIn("scalable_parameter_candidates", record)
        self.assertNotIn("closest_vanilla_equivalent", record)
        self.assertEqual("original-id", record["mechanic_id"])

    def test_explicit_numeric_fields_survive_while_audit_material_is_removed(self):
        component = {"primitive": "EXAMPLE", "formula": "Full prose audit", "numerical_parameters": {"formula": "6 << amplifier", "coefficient": -0.15, "reference_files": ["cold.json"]}, "implementation": [{"witness_id": "cold"}]}
        self.assertEqual({"primitive": "EXAMPLE", "formula": "6 << amplifier", "coefficient": -0.15}, extractor.reduce_component(component))
        self.assertEqual({"primitive": "EXAMPLE"}, extractor.reduce_component({"primitive": "EXAMPLE", "numerical_parameters": {"damage": 10}}))

    def test_difference_schema_variants_keep_only_source_notes_and_native_relations(self):
        structured = {"classification": "CUSTOM_DAMAGE", "component_contracts": [{"primitive": "EXAMPLE", "formula": "Full native audit", "native_relation": "Native damage with custom admission"}]}
        self.assertEqual(["Plain note", "Nested note", "Native damage with custom admission"], extractor.reduce_differences(["Plain note", ["Nested note"], structured]))
        self.assertIsNone(extractor.reduce_differences(None))
        self.assertEqual([None], extractor.reduce_differences([None]))
        with self.assertRaises(ValueError):
            extractor.reduce_differences({"unknown": "No guessed interpretation"})

    def test_distinct_mechanics_sharing_primitives_are_not_deduplicated(self):
        reviews = [(path, {"status": "COMPLETE", "mod_key": str(index), "effects": [{"mod_key": str(index), "id": name, "primary_classification": "VANILLA_DIRECT", "components": [{"primitive": "SAME"}]} for name in ("second", "first")]}) for index, path in enumerate(extractor.REVIEW_FILES)]
        manifest = extractor.compile_manifest(reviews, "fixture")
        self.assertEqual(18, len(manifest["mechanics"]))
        self.assertEqual(["first", "second"], [record["mechanic_id"] for record in manifest["mechanics"][:2]])

    def test_incomplete_missing_and_duplicate_reviews_or_identities_are_rejected(self):
        reviews = [(path, {"status": "COMPLETE", "mod_key": str(index), "effects": [{"mod_key": str(index), "id": "original", "primary_classification": "BINARY_MECHANIC"}]}) for index, path in enumerate(extractor.REVIEW_FILES)]
        incomplete = copy.deepcopy(reviews)
        incomplete[0][1]["status"] = "PARTIAL"
        duplicate = copy.deepcopy(reviews)
        duplicate[0][1]["effects"].append(copy.deepcopy(duplicate[0][1]["effects"][0]))
        for invalid in (reviews[:-1], reviews[:-1] + [reviews[0]], incomplete, duplicate):
            with self.assertRaises(ValueError):
                extractor.compile_manifest(invalid, "fixture")
        with self.assertRaises(ValueError):
            extractor.reduce_mechanic({"mod_key": "example"})


if __name__ == "__main__":
    unittest.main()
