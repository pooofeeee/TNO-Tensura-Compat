"""Focused regressions for the bounded R2k10b Scylla static research."""
import copy
import unittest

from catalog_common import read_json
from collect_cataclysm_scylla_offense import EVIDENCE_FILE, LIGHTNING_SPEAR, PKG, SPEC_FILE, specification
from validate_cataclysm_scylla_offense import (
    LEDGER, NOTE, REVIEW, selected, validate, validate_contracts,
    validate_native_boundaries, validate_preservation, validate_records,
)


class ScyllaOffenseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original_review = read_json(REVIEW)
        cls.original_note = read_json(NOTE)
        cls.original_ledger = read_json(LEDGER)

    def setUp(self):
        self.review = copy.deepcopy(self.original_review)
        self.note = copy.deepcopy(self.original_note)
        self.ledger = copy.deepcopy(self.original_ledger)

    def row(self, key):
        return next(e for e in selected(self.review) if e['id'] == 'cataclysm:scylla_' + key)

    def check(self):
        return validate_records(self.review, self.note, self.ledger)

    def reject_facts(self, changes):
        for key, field, value in changes:
            with self.subTest(mechanic=key, field=field):
                rows = copy.deepcopy({e['id']: e for e in selected(self.review)})
                rows['cataclysm:scylla_' + key][field] = value
                with self.assertRaises(AssertionError):
                    validate_contracts(rows)

    def test_complete_bounded_archive_and_protected_contracts(self):
        result = validate()
        self.assertEqual(result['status'], 'PASS')
        self.assertEqual(result['new_mechanics'], 45)
        self.assertEqual(result['delivery_paths'], 45)
        self.assertEqual(result['candidate_numeric_parameters'], 120)
        self.assertEqual(result['new_method_witnesses'], 279)
        self.assertEqual(result['protected_scylla_admission_shared_status_prior_bosses'], 'BYTE_IDENTICAL')
        self.assertEqual(read_json(SPEC_FILE), specification())

    def test_duplicate_ids_rejected(self):
        selected(self.review)[1]['id'] = selected(self.review)[0]['id']
        with self.assertRaises(AssertionError):
            self.check()

    def test_invalid_classification_rejected(self):
        self.row('alliance')['primary_classification'] = 'INVENTED'
        with self.assertRaises(AssertionError):
            self.check()

    def test_source_delivery_and_hurt_return_required(self):
        for field in ['source_actor', 'delivery_paths', 'hurt_return_dependency', 'primary_test_source']:
            with self.subTest(field=field):
                self.review = copy.deepcopy(self.original_review)
                self.row('area_contact')[field] = None
                with self.assertRaises(AssertionError):
                    self.check()

    def test_candidate_keeps_native_primitive(self):
        candidate = next(c for c in self.row('area_contact')['scalable_parameter_candidates']
            if c['primitive'] == 'FORCED_MOVEMENT')
        candidate['primitive'] = 'NATIVE_DAMAGE_REQUEST'
        with self.assertRaises(AssertionError):
            self.check()

    def test_candidate_preserves_value_formula_units_and_boundary(self):
        for field, value in [('native_value', 999), ('native_formula', 'flattened'),
                             ('units', 'unknown'), ('native_boundary', 'invented hook')]:
            with self.subTest(field=field):
                self.review = copy.deepcopy(self.original_review)
                self.row('area_contact')['scalable_parameter_candidates'][0][field] = value
                with self.assertRaises(AssertionError):
                    self.check()

    def test_nonfinite_observation_and_stage_policy_rejected(self):
        self.row('area_contact')['components'][0]['numerical_parameters']['coefficient'] = float('nan')
        with self.assertRaises(AssertionError):
            self.check()
        self.review = copy.deepcopy(self.original_review)
        self.row('area_contact')['stage_policy'] = 'MULTIPLY'
        with self.assertRaises(AssertionError):
            self.check()

    def test_phase_and_selection_gates_are_not_candidate_scalars(self):
        self.row('sequence_state')['scalable_parameter_candidates'] = copy.deepcopy(
            self.row('area_contact')['scalable_parameter_candidates'])
        with self.assertRaises(AssertionError):
            self.check()
        self.reject_facts([
            ('attack_selection', 'selection_gates_are_stage_scalars', True),
            ('attack_selection', 'whip_spear_registered_max', 25.0),
            ('attack_selection', 'backstep_state_or_bypasses_selection', False),
            ('sequence_state', 'cooldowns_have_local_side_ai_guard', True),
        ])

    def test_damage_shield_and_movement_gates_remain_distinct(self):
        self.reject_facts([
            ('area_contact', 'shield_disable_requires_hurt_true', True),
            ('area_contact', 'movement_requires_hurt_true', False),
            ('area_contact', 'wrapped_angle_branches_have_local_range_check', True),
            ('spin_contact', 'sample_deduplication', True),
            ('spin_contact', 'zero_airborne_removes_native_rng', True),
            ('wave_contact', 'movement_requires_hurt_true', True),
            ('wave_contact', 'wetness_requires_hurt_true', False),
        ])

    def test_control_is_not_flattened_into_native_knockback(self):
        self.reject_facts([
            ('area_contact', 'movement_is_native_knockback', True),
            ('storm_push', 'storm_push_has_local_ally_filter', True),
            ('flight_movement', 'fall_movement_overwrites_velocity', False),
            ('water_movement', 'motion_is_native_knockback', True),
            ('anchor_contact', 'movement_is_native_knockback', True),
        ])

    def test_custom_damage_sources_and_hp_formula_distinctions(self):
        self.reject_facts([
            ('storm_contact', 'hp_contribution_has_min_cap', True),
            ('lightning_body_contact', 'hp_contribution_has_min_cap', False),
            ('lightning_body_contact', 'uses_native_explosion', True),
            ('anchor_contact', 'damage_causing_actor_is_controller', False),
            ('cloud_barrage_delivery', 'lightning_damage_config_field', 'SpearDamage'),
            ('alliance', 'alliance_inherited_globally_by_payloads', True),
        ])

    def test_projectile_motion_impact_and_payload_distinctions(self):
        self.reject_facts([
            ('elemental_spear_motion', 'impact_event_preserved', False),
            ('elemental_spear_motion', 'initial_speed_is_acceleration', True),
            ('water_spear_contact', 'entity_hit_auto_discards', True),
            ('water_spear_bounce', 'reflection_preserves_full_incoming_speed', True),
            ('spark_block_payload', 'spark_has_custom_entity_hit_damage', True),
            ('lightning_spear_block_payload', 'creates_two_distinct_payloads', False),
            ('serpent_delivery', 'serpent_is_projectile_subclass', True),
        ])

    def test_spark_motion_and_persistence_have_separate_records(self):
        self.assertEqual(self.row('spark_lifecycle')['primary_classification'], 'BINARY_MECHANIC')
        self.assertFalse(self.row('spark_lifecycle')['scalable_parameter_candidates'])
        self.assertEqual(self.row('spark_motion')['scalable_parameter_candidates'][0]['parameters'], ['gravity'])
        self.assertEqual(self.row('spark_motion')['scalable_parameter_candidates'][0]['native_value'], .07)

    def test_custom_area_does_not_inherit_vanilla_cloud_rules(self):
        self.reject_facts([
            ('lightning_area_contact', 'uses_native_area_effect_cloud', True),
            ('lightning_area_contact', 'has_vanilla_victim_cache', True),
            ('lightning_area_contact', 'has_circular_distance_filter', True),
            ('lightning_area_contact', 'radius_on_use_consumed', True),
            ('lightning_area_contact', 'duration_on_use_consumed', True),
        ])

    def test_native_saved_state_mismatches_are_not_repaired(self):
        self.reject_facts([
            ('lightning_spear_lifecycle', 'hp_damage_save_reads', 'getHpDamage'),
            ('spark_lifecycle', 'area_damage_load_key', 'AreaDamage'),
            ('lightning_area_lifecycle', 'saved_owner_uuid', True),
            ('lightning_area_lifecycle', 'saved_damage', True),
            ('wave_lifecycle', 'contact_uses_owner_resolver', True),
            ('wave_lifecycle', 'saved_damage', True),
            ('serpent_lifecycle', 'saved_right', True),
            ('elemental_spear_lifecycle', 'saved_private_lifetick', True),
        ])

    def test_grab_carrier_latch_and_ride_result_gates(self):
        self.reject_facts([
            ('anchor_grab_control', 'boss_is_victim_carrier', True),
            ('anchor_grab_control', 'ride_requires_hurt_true', False),
            ('anchor_grab_control', 'grab_latch_requires_hurt_true', True),
            ('anchor_grab_control', 'ride_result_controls_packet', True),
            ('anchor_lifecycle', 'hook_adds_normal_owner_alive_guard', True),
            ('anchor_return_motion', 'returns_after_controller_collision_discard', True),
        ])

    def test_environment_and_death_callbacks_remain_native(self):
        self.reject_facts([
            ('terrain_response', 'ignore_mobgriefing_config_read', True),
            ('terrain_response', 'creates_damaging_debris', True),
            ('weather_transition', 'weather_is_damage', True),
            ('weather_transition', 'weather_is_stage_scalar', True),
            ('defeat_lifecycle', 'adds_duplicate_death_payload', True),
            ('storm_delivery', 'landing_ring_divisor_is_integer', True),
        ])

    def test_owned_payload_source_links_required(self):
        self.note['payload_entities'][0]['source_mechanic_ids'] = ['cataclysm:scylla_alliance']
        with self.assertRaises(AssertionError):
            self.check()

    def test_protected_admission_and_old_catalog_cannot_change(self):
        old = next(e for e in self.review['effects'] if e not in selected(self.review))
        old['actual_behavior'] = 'silently reopened'
        with self.assertRaises(AssertionError):
            validate_preservation(self.review, self.note, self.ledger)

    def test_cataclysm_cannot_be_marked_complete(self):
        cat = next(t for t in self.ledger['targets'] if t['mod_key'] == 'cataclysm')
        cat['state'] = 'COMPLETE'
        with self.assertRaises(AssertionError):
            self.check()

    def test_native_witness_preserves_wrong_radius_getter(self):
        evidence = read_json(EVIDENCE_FILE)
        witness = next(w for w in evidence['witnesses'] if w['entry'] == PKG + LIGHTNING_SPEAR + '.class')
        method = next(m for m in witness['methods'] if m['name'] == 'addAdditionalSaveData')
        instruction = next(i for i in method['instructions'] if i['offset'] == 32)
        instruction['operand'] = instruction['operand'].replace('getAreaRadius', 'getHpDamage')
        with self.assertRaises(AssertionError):
            validate_native_boundaries(evidence)


if __name__ == '__main__':
    unittest.main()
