"""Focused static regressions for the bounded R2k8b Maledictus contracts."""
import copy
import unittest

from catalog_common import read_json
from collect_cataclysm_maledictus_offense import A, EVIDENCE_FILE, H, M, PKG
from validate_cataclysm_maledictus_offense import (
    LEDGER, NOTE, REVIEW, selected, validate, validate_contracts,
    validate_native_boundaries, validate_preservation, validate_records,
)


class MaledictusOffenseTests(unittest.TestCase):
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
        return next(e for e in selected(self.review) if e['id'] == 'cataclysm:maledictus_' + key)

    def check(self):
        return validate_records(self.review, self.note, self.ledger)

    def reject_contract_changes(self, changes):
        for key, field, value in changes:
            with self.subTest(mechanic=key, field=field):
                rows = copy.deepcopy({e['id']: e for e in selected(self.review)})
                rows['cataclysm:maledictus_' + key][field] = value
                with self.assertRaises(AssertionError):
                    validate_contracts(rows)

    def test_archive_and_locked_contracts(self):
        result = validate()
        self.assertEqual(result['status'], 'PASS')
        self.assertEqual(result['new_mechanics'], 36)
        self.assertEqual(result['delivery_paths'], 36)
        self.assertEqual(result['candidate_numeric_parameters'], 136)
        self.assertEqual(result['new_method_witnesses'], 144)
        self.assertEqual(result['protected_maledictus_admission_shared_status_prior_bosses'], 'BYTE_IDENTICAL')

    def test_duplicate_mechanic_rejected(self):
        selected(self.review)[1]['id'] = selected(self.review)[0]['id']
        with self.assertRaises(AssertionError):
            self.check()

    def test_invalid_classification_rejected(self):
        selected(self.review)[0]['primary_classification'] = 'INVENTED'
        with self.assertRaises(AssertionError):
            self.check()

    def test_source_delivery_and_hurt_contract_required(self):
        for field in ['source_actor', 'primary_test_source', 'delivery_paths', 'hurt_return_dependency']:
            with self.subTest(field=field):
                self.review = copy.deepcopy(self.original_review)
                selected(self.review)[0][field] = None
                with self.assertRaises(AssertionError):
                    self.check()

    def test_candidate_keeps_primitive(self):
        candidate = next(c for c in self.row('uppercut_contact')['scalable_parameter_candidates']
                         if c['primitive'] == 'FORCED_MOVEMENT')
        candidate['primitive'] = 'NATIVE_DAMAGE_REQUEST'
        with self.assertRaises(AssertionError):
            self.check()

    def test_candidate_native_formula_value_and_unit_required(self):
        for field, value in [('native_formula', 'flattened damage'), ('native_value', 1000), ('units', 'unknown')]:
            with self.subTest(field=field):
                self.review = copy.deepcopy(self.original_review)
                self.row('uppercut_contact')['scalable_parameter_candidates'][0][field] = value
                with self.assertRaises(AssertionError):
                    self.check()

    def test_nonfinite_native_numeric_rejected(self):
        self.row('uppercut_contact')['components'][0]['numerical_parameters']['hp_coefficient'] = float('nan')
        with self.assertRaises(AssertionError):
            self.check()

    def test_stage_policy_field_rejected(self):
        self.row('uppercut_contact')['stage_multiplier'] = 2
        with self.assertRaises(AssertionError):
            self.check()

    def test_owned_payload_source_links_required(self):
        self.note['payload_entities'][0]['source_mechanic_ids'] = ['cataclysm:maledictus_alliance']
        with self.assertRaises((AssertionError, KeyError)):
            self.check()

    def test_live_rage_and_native_gain_reset_are_separate(self):
        self.reject_contract_changes([
            ('rage_offense', 'direct_rage_is_live', False),
            ('rage_offense', 'raw_setter_clamps_rage', True),
            ('rage_offense', 'gain_guard_is_global_clamp', True),
            ('rage_offense', 'reset_precedes_soul_damage', False),
            ('soul_release', 'reset_precedes_damage', False),
            ('shockwave_sweep', 'base_damage_captured_before_samples', False),
        ])

    def test_carried_damage_snapshot_coefficients_remain_distinct(self):
        for key in ['ground_bow_volley', 'flying_bow_volley', 'halberd_ground_delivery']:
            with self.subTest(mechanic=key):
                rows = copy.deepcopy({e['id']: e for e in selected(self.review)})
                c = next(c for c in rows['cataclysm:maledictus_' + key]['components'] if c['primitive'] == 'DAMAGE_CARRIER')
                c['numerical_parameters']['rage_coefficient'] = .2
                with self.assertRaises(AssertionError):
                    validate_contracts(rows)

    def test_hurt_return_and_independent_shield_callbacks(self):
        self.reject_contract_changes([
            ('area_contact', 'shield_requires_hurt_true', True),
            ('area_contact', 'push_requires_hurt_true', False),
            ('combo_contact', 'combo_requires_hurt_true', False),
            ('combo_chain', 'combo_branch_calls_parent_stop', True),
            ('rush_contact', 'adds_victim_movement', True),
            ('uppercut_contact', 'lift_requires_hurt_true', False),
            ('soul_release', 'hurt_return_consumed', True),
            ('held_soul_slam', 'requires_held_passenger', True),
        ])

    def test_self_movement_is_not_native_knockback(self):
        self.reject_contract_changes([
            ('mace_leap', 'movement_is_native_knockback', True),
            ('rush_chain', 'movement_is_native_knockback', True),
            ('flying_smash_chain', 'movement_is_native_knockback', True),
            ('uppercut_contact', 'movement_is_native_knockback', True),
        ])

    def test_original_goal_continuation_and_flight_profiles(self):
        self.reject_contract_changes([
            ('attack_selection', 'selection_is_goal_scheduled', False),
            ('rush_chain', 'continuation_validates_alternative_state', True),
            ('uppercut_chain', 'goal_tick_calls_parent', True),
            ('flying_smash_chain', 'strike_ticks', {'8': 51, '24': 56}),
            ('flying_smash_contact', 'contact_ticks', {'9': [4], '25': [4]}),
            ('flying_bow_control', 'has_extra_line_of_sight_gate', True),
        ])

    def test_grab_flag_is_not_successful_mount(self):
        self.reject_contract_changes([
            ('grab_contact', 'grab_flag_requires_hurt_true', False),
            ('grab_contact', 'grab_flag_requires_mount_success', True),
            ('grab_control', 'mount_return_checked', True),
            ('grab_control', 'camera_request_requires_mount_success', True),
            ('grab_control', 'grab_transition_requires_passenger', True),
            ('grab_control', 'success_dropspeed_read', True),
        ])

    def test_held_literal_clamp_and_native_release_preserved(self):
        self.reject_contract_changes([
            ('held_victim_control', 'state33_y_equals_boss_y', False),
            ('held_victim_control', 'release_has_local_server_guard', True),
            ('held_victim_control', 'shift_suppression_has_local_server_guard', True),
            ('held_victim_control', 'release_tick', 2),
            ('held_victim_control', 'adds_damage', True),
        ])

    def test_native_halberd_geometry_and_support_are_not_extra_damage(self):
        self.reject_contract_changes([
            ('halberd_ring_chain', 'radius_argument_is_physical_radius', True),
            ('halberd_windmill_chain', 'attempted_entity_count', 60),
            ('halberd_radagon_chain', 'has_single_sample_denominator_fallback', True),
            ('halberd_ground_delivery', 'local_spawn_server_guard', True),
            ('halberd_ground_delivery', 'sets_native_projectile_owner', True),
            ('halberd_ring_chain', 'spawn_requires_hurt_true', True),
            ('shockwave_sweep', 'global_victim_deduplication', True),
            ('shockwave_debris', 'debris_adds_damage', True),
        ])

    def test_halberd_source_cadence_and_partial_nbt_preserved(self):
        self.reject_contract_changes([
            ('halberd_contact', 'has_bilateral_allied_check', False),
            ('halberd_contact', 'caster_absence_magic_fallback', False),
            ('halberd_contact', 'cadence_uses_entity_tick_count', False),
            ('halberd_contact', 'damage_uses_live_caster_rage', True),
            ('halberd_lifecycle', 'damage_saved', True),
            ('halberd_lifecycle', 'default_damage_after_reload', 11),
            ('halberd_lifecycle', 'contact_requires_visual_state', True),
        ])

    def test_arrow_native_payload_return_order_and_lifecycle(self):
        self.reject_contract_changes([
            ('arrow_contact', 'parent_on_hit_entity_called', True),
            ('arrow_contact', 'damage_uses_native_velocity_multiplier', True),
            ('arrow_contact', 'burn_requires_hurt_true', True),
            ('arrow_contact', 'burn_rolled_back_on_false', True),
            ('arrow_contact', 'successful_hit_discards_locally', True),
            ('arrow_contact', 'enderman_true_returns_early', False),
            ('arrow_contact', 'false_slow_discard_requires_pickup_allowed', True),
            ('arrow_lifecycle', 'despawn_is_universal_flight_timer', True),
            ('arrow_lifecycle', 'stop_seeking_saved', True),
        ])

    def test_arrow_motion_retains_original_target_predicate(self):
        self.reject_contract_changes([
            ('arrow_homing', 'native_parent_tick_retained', False),
            ('arrow_homing', 'alive_spectator_predicate_is_conjunction', True),
            ('arrow_homing', 'homing_normalizes_final_speed', True),
            ('arrow_homing', 'failed_target_lookup_retries', True),
        ])

    def test_terrain_and_death_boundaries_remain_native(self):
        self.reject_contract_changes([
            ('terrain_control', 'ground_has_no_ai_gate', False),
            ('terrain_control', 'flying_has_no_ai_gate', True),
            ('terrain_control', 'chandelier_pass_checks_immune_tag', True),
            ('defeat_lifecycle', 'death_state_write_checks_parent_admission', True),
            ('defeat_lifecycle', 'placement_uses_current_level', False),
            ('alliance', 'tag_fallback_requires_both_team_null', False),
        ])

    def test_protected_admission_record_cannot_change(self):
        previous = next(e for e in self.review['effects'] if e['review_checkpoint'] == 'R2k8a-cataclysm-maledictus-admission-complete')
        previous['actual_behavior'] = 'Changed protected admission'
        with self.assertRaises(AssertionError):
            validate_preservation(self.review, self.note, self.ledger)

    def test_cataclysm_cannot_be_marked_complete(self):
        next(t for t in self.ledger['targets'] if t['mod_key'] == 'cataclysm')['state'] = 'COMPLETE'
        with self.assertRaises(AssertionError):
            self.check()

    def test_native_return_and_callback_instruction_mutations_rejected(self):
        for n, name, offset in [(M, 'Grab', 294), (A, 'onHitEntity', 125), (H, 'damage', 52)]:
            with self.subTest(entry=n, method=name):
                evidence = copy.deepcopy(self.original_evidence)
                method = next(m for w in evidence['witnesses'] if w['entry'] == PKG+n+'.class'
                              for m in w['methods'] if m['name'] == name)
                next(i for i in method['instructions'] if i['offset'] == offset)['opcode'] = '0x0'
                with self.assertRaises(AssertionError):
                    validate_native_boundaries(evidence)


if __name__ == '__main__':
    unittest.main()
