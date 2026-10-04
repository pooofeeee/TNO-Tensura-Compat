"""Focused static regressions for bounded R2k9b Leviathan offense contracts."""
import copy
import unittest

from catalog_common import read_json
from collect_cataclysm_leviathan_offense import EVIDENCE_FILE, FAMILY, L, PKG
from validate_cataclysm_leviathan_offense import (
    LEDGER, NOTE, REVIEW, selected, validate, validate_contracts,
    validate_evidence, validate_native_boundaries, validate_preservation,
    validate_records,
)


class LeviathanOffenseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original_review = read_json(REVIEW)
        cls.original_note = read_json(NOTE)
        cls.original_ledger = read_json(LEDGER)
        cls.original_evidence = read_json(EVIDENCE_FILE)

    def setUp(self):
        self.review = copy.deepcopy(self.original_review)
        self.note = copy.deepcopy(self.original_note)
        self.ledger = copy.deepcopy(self.original_ledger)

    def row(self, key):
        return next(e for e in selected(self.review) if e['id'] == 'cataclysm:leviathan_' + key)

    def check(self):
        return validate_records(self.review, self.note, self.ledger)

    def reject_changes(self, changes):
        for key, field, value in changes:
            with self.subTest(mechanic=key, field=field):
                rows = copy.deepcopy({e['id']: e for e in selected(self.review)})
                rows['cataclysm:leviathan_' + key][field] = value
                with self.assertRaises(AssertionError):
                    validate_contracts(rows)

    def test_archive_and_locked_contracts(self):
        result = validate()
        self.assertEqual(result['status'], 'PASS')
        self.assertEqual(result['new_mechanics'], 45)
        self.assertEqual(result['delivery_paths'], 45)
        self.assertEqual(result['candidate_numeric_parameters'], 107)
        self.assertEqual(result['new_method_witnesses'], 267)
        self.assertEqual(result['protected_leviathan_admission_shared_status_prior_bosses'], 'BYTE_IDENTICAL')

    def test_duplicate_mechanic_rejected(self):
        selected(self.review)[1]['id'] = selected(self.review)[0]['id']
        with self.assertRaises(AssertionError):
            self.check()

    def test_invalid_classification_rejected(self):
        selected(self.review)[0]['primary_classification'] = 'INVENTED'
        with self.assertRaises(AssertionError):
            self.check()

    def test_source_delivery_and_return_contract_required(self):
        for field in ['source_actor', 'primary_test_source', 'delivery_paths', 'hurt_return_dependency']:
            with self.subTest(field=field):
                self.review = copy.deepcopy(self.original_review)
                selected(self.review)[0][field] = None
                with self.assertRaises(AssertionError):
                    self.check()

    def test_candidate_keeps_primitive(self):
        candidate = next(c for c in self.row('tentacle_contact')['scalable_parameter_candidates']
                         if c['primitive'] == 'FORCED_MOVEMENT')
        candidate['primitive'] = 'NATIVE_DAMAGE_REQUEST'
        with self.assertRaises(AssertionError):
            self.check()

    def test_candidate_native_formula_value_units_and_boundary_required(self):
        for field, value in [('native_formula', 'flattened damage'), ('native_value', 1000),
                             ('units', 'unknown'), ('native_boundary', 'invented hook')]:
            with self.subTest(field=field):
                self.review = copy.deepcopy(self.original_review)
                self.row('tentacle_contact')['scalable_parameter_candidates'][0][field] = value
                with self.assertRaises(AssertionError):
                    self.check()

    def test_nonfinite_numeric_rejected(self):
        self.row('tentacle_contact')['components'][0]['numerical_parameters']['hp_coefficient'] = float('nan')
        with self.assertRaises(AssertionError):
            self.check()

    def test_stage_policy_field_rejected(self):
        self.row('tentacle_contact')['stage_multiplier'] = 2
        with self.assertRaises(AssertionError):
            self.check()

    def test_binary_state_not_promoted_to_candidate(self):
        self.row('sequence_state')['scalable_parameter_candidates'] = copy.deepcopy(
            self.row('tentacle_contact')['scalable_parameter_candidates'])
        with self.assertRaises(AssertionError):
            self.check()

    def test_owned_payload_source_links_required(self):
        self.note['payload_entities'][0]['source_mechanic_ids'] = ['cataclysm:leviathan_alliance']
        with self.assertRaises((AssertionError, KeyError)):
            self.check()

    def test_attack_rng_and_private_charge_helpers_remain_native(self):
        self.reject_changes([
            ('attack_selection', 'independent_random_draws', False),
            ('attack_selection', 'selection_counters_are_stage_scalars', True),
            ('sequence_state', 'unused_charge_helpers_promoted', True),
            ('sequence_state', 'per_tick_mode_decrement_goals', []),
            ('rush_movement', 'rush_requests_contact_damage', True),
        ])

    def test_bite_config_and_hold_formula_remain_distinct(self):
        self.reject_changes([
            ('bite_contact', 'hp_config_field', 'BiteHpDamage'),
            ('hold_contact', 'damage_has_hp_min_cap', True),
        ])

    def test_damage_shield_and_control_return_gates(self):
        self.reject_changes([
            ('bite_contact', 'shield_disable_requires_hurt_true', True),
            ('tentacle_contact', 'movement_requires_hurt_true', False),
            ('tail_contact', 'shield_disable_requires_hurt_true', True),
            ('hold_control', 'ride_result_controls_animation', True),
            ('held_victim_control', 'release_returns_before_positioning', True),
        ])

    def test_water_and_contact_motion_not_standard_knockback(self):
        self.reject_changes([
            ('water_movement', 'water_motion_is_knockback', True),
            ('tail_contact', 'movement_is_native_knockback', True),
            ('tentacle_contact', 'movement_is_native_knockback', True),
            ('tongue_motion', 'movement_is_knockback', True),
        ])

    def test_bone_fracture_and_darkness_not_collapsed(self):
        rows = {e['id']: e for e in selected(self.review)}
        tail = rows['cataclysm:leviathan_tail_contact']
        next(c for c in tail['components'] if c['primitive'] == 'BONE_FRACTURE_DELIVERY')['primitive'] = 'DARKNESS_DELIVERY'
        with self.assertRaises(AssertionError):
            validate_contracts(rows)

    def test_orb_event_and_distinct_fear_explosion_gates(self):
        self.reject_changes([
            ('orb_motion', 'impact_event_preserved', False),
            ('orb_motion', 'homing_has_distance_floor', True),
            ('orb_contact', 'fear_requires_hurt_true', False),
            ('orb_contact', 'explosion_requires_hurt_true', True),
            ('orb_contact', 'local_ally_predicate', True),
            ('orb_terminal_explosion', 'explosion_requires_hurt_true', True),
            ('orb_terminal_explosion', 'applies_fear', True),
            ('orb_lifecycle', 'tracking_load_key', 'tracking'),
        ])

    def test_mine_native_iteration_and_admission_retained(self):
        self.reject_changes([
            ('mine_trigger', 'loop_breaks_after_remove', True),
            ('mine_trigger', 'fear_requires_hurt_true', True),
            ('mine_trigger', 'activation_flag_gates_explosion', True),
            ('mine_delivery', 'mine_requires_ground_support', True),
        ])

    def test_rift_raw_state_source_and_pull_damage_distinctions(self):
        self.reject_changes([
            ('rift_delivery', 'growth_checks_owner', True),
            ('rift_delivery', 'native_rift_stage_is_tno_stage', True),
            ('rift_pull', 'pull_uses_owner_alliance', True),
            ('rift_damage', 'damage_reads_dimensional_rift_config', True),
            ('rift_damage', 'damage_has_local_server_guard', True),
            ('rift_lifecycle', 'ordinal_is_clamped', True),
        ])

    def test_beam_native_percent_unit_factor_and_geometry(self):
        for key, primitive, parameter, value in [
            ('beam_contact', 'NATIVE_DAMAGE_REQUEST', 'hp_unit_factor', 1.0),
            ('beam_geometry', 'AREA_SELECTION', 'range', 64.0)]:
            with self.subTest(mechanic=key, parameter=parameter):
                rows = copy.deepcopy({e['id']: e for e in selected(self.review)})
                component = next(c for c in rows['cataclysm:leviathan_' + key]['components'] if c['primitive'] == primitive)
                component['numerical_parameters'][parameter] = value
                with self.assertRaises(AssertionError):
                    validate_contracts(rows)
        self.reject_changes([('beam_geometry', 'entity_segment_ends_at_block_clip', True),
                             ('beam_contact', 'beam_is_projectile', True)])

    def test_delayed_beam_and_native_nbt_not_repaired(self):
        self.reject_changes([
            ('blast_portal_lifecycle', 'raw_caster_guard_before_resolver', False),
            ('beam_lifecycle', 'portal_damage_saved', True),
            ('beam_lifecycle', 'server_caster_uuid_restore', True),
            ('portal_lifecycle', 'entrance_saved', True),
            ('portal_lifecycle', 'destination_loaded_before_sister', False),
        ])

    def test_teleport_is_control_without_new_team_or_dimension_rule(self):
        self.reject_changes([
            ('stuck_portal_delivery', 'root_stuck_requires_water', True),
            ('portal_teleport', 'changes_dimension', True),
            ('portal_teleport', 'has_local_team_filter', True),
            ('portal_teleport', 'deduplicates_recipients', True),
        ])

    def test_tongue_native_target_return_mount_and_cleanup(self):
        self.reject_changes([
            ('tongue_contact', 'hurt_evaluated_before_server_guard', False),
            ('tongue_contact', 'return_flag_requires_hurt_true', True),
            ('tongue_contact', 'mount_force', True),
            ('tongue_motion', 'target_read_precedes_server_refresh', False),
            ('tongue_lifecycle', 'max_duration_load_calls_set_duration', False),
            ('tongue_lifecycle', 'self_discards_at_duration_limit', True),
        ])

    def test_terrain_hooks_and_non_damage_debris_remain_distinct(self):
        self.reject_changes([
            ('terrain_control', 'melee_response_has_destroy_hook', True),
            ('rift_terrain', 'debris_deals_damage', True),
            ('tongue_lifecycle', 'has_entity_destroy_hook', True),
            ('beam_terrain', 'has_native_explosion', True),
            ('defeat_lifecycle', 'concrete_respawner_spawned', True),
        ])

    def test_protected_record_change_rejected(self):
        old = next(e for e in self.review['effects'] if e['id'] == 'cataclysm:leviathan_incoming_admission')
        old['actual_behavior'] = 'changed'
        with self.assertRaises(AssertionError):
            validate_preservation(self.review, self.note, self.ledger)

    def test_partial_and_next_bounded_family_required(self):
        for field, value in [('whole_mod_complete', True), ('leviathan_family_closed', False),
                             ('exact_next_task', 'Unbounded scan')]:
            with self.subTest(field=field):
                self.note = copy.deepcopy(self.original_note)
                self.note[field] = value
                with self.assertRaises(AssertionError):
                    self.check()

    def test_private_helper_call_proof_required(self):
        self.note['scoped_private_helper_checks'][0]['callers_within_owned_family'] = ['invented caller']
        with self.assertRaises(AssertionError):
            validate_evidence(self.review, self.note)

    def test_native_hurt_and_mount_order_cannot_change(self):
        evidence = copy.deepcopy(self.original_evidence)
        witness = next(w for w in evidence['witnesses'] if w['entry'] == PKG+FAMILY+'The_Leviathan_Tongue_Entity.class')
        method = next(m for m in witness['methods'] if m['name'] == 'hurtEntity')
        next(i for i in method['instructions'] if i['offset'] == 11)['operand'] = 'removed native hurt'
        with self.assertRaises(AssertionError):
            validate_native_boundaries(evidence)


if __name__ == '__main__':
    unittest.main()
