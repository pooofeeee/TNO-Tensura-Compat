"""Focused R2k7b archive regressions; no runtime, balance or Stage tests."""
import copy
import json
import unittest

from catalog_common import read_json
from collect_cataclysm_remnant_offense import EVIDENCE_FILE, SPEC_FILE
from validate_cataclysm_remnant_offense import (
    CHECKPOINT, LEDGER, NOTE, REVIEW, selected, validate, validate_contracts,
    validate_native_boundaries, validate_preservation, validate_records,
)


class RemnantOffenseTests(unittest.TestCase):
    def setUp(self):
        self.review, self.note, self.ledger = [read_json(p) for p in [REVIEW, NOTE, LEDGER]]

    def check(self):
        return validate_records(self.review, self.note, self.ledger)

    def row(self, key):
        return next(e for e in selected(self.review) if e['id'] == 'cataclysm:remnant_' + key)

    def reject_contract_changes(self, changes):
        for key, field, value in changes:
            with self.subTest(mechanic=key, field=field):
                rows = copy.deepcopy({e['id']: e for e in selected(self.review)})
                rows['cataclysm:remnant_' + key][field] = value
                with self.assertRaises(AssertionError):
                    validate_contracts(rows)

    def test_scoped_archive_and_locked_contracts(self):
        result = validate()
        self.assertEqual(result['status'], 'PASS')
        self.assertEqual(result['new_mechanics'], 25)
        self.assertEqual(result['delivery_paths'], 25)
        self.assertEqual(result['candidate_numeric_parameters'], 78)
        self.assertEqual(result['new_method_witnesses'], 127)
        self.assertEqual(result['protected_remnant_admission_shared_status_prior_bosses'], 'BYTE_IDENTICAL')

    def test_duplicate_mechanic_rejected(self):
        selected(self.review)[1]['id'] = selected(self.review)[0]['id']
        with self.assertRaises(AssertionError):
            self.check()

    def test_invalid_classification_rejected(self):
        selected(self.review)[0]['primary_classification'] = 'INVENTED'
        with self.assertRaises(AssertionError):
            self.check()

    def test_missing_source_delivery_or_return_contract_rejected(self):
        for field in ['source_actor', 'primary_test_source', 'delivery_paths', 'hurt_return_dependency']:
            with self.subTest(field=field):
                original = copy.deepcopy(self.review)
                selected(self.review)[0][field] = None
                with self.assertRaises(AssertionError):
                    self.check()
                self.review = original

    def test_numeric_candidate_keeps_native_primitive(self):
        candidate = next(c for c in self.row('charge_contact')['scalable_parameter_candidates']
                         if c['primitive'] == 'FORCED_MOVEMENT')
        candidate['primitive'] = 'NATIVE_DAMAGE_REQUEST'
        with self.assertRaises(AssertionError):
            self.check()

    def test_numeric_candidate_formula_and_value_are_native(self):
        for field, value in [('native_formula', 'Flattened damage'), ('native_value', 1000)]:
            with self.subTest(field=field):
                original = copy.deepcopy(self.review)
                self.row('charge_contact')['scalable_parameter_candidates'][0][field] = value
                with self.assertRaises(AssertionError):
                    self.check()
                self.review = original

    def test_nonfinite_native_parameter_rejected(self):
        self.row('charge_contact')['components'][0]['numerical_parameters']['hp_coefficient'] = float('inf')
        with self.assertRaises(AssertionError):
            self.check()

    def test_payload_owner_delivery_links_are_required(self):
        self.note['payload_entities'][0]['source_mechanic_ids'] = ['cataclysm:remnant_alliance']
        with self.assertRaises((AssertionError, KeyError)):
            self.check()

    def test_native_selection_mode_and_short_circuit_rolls(self):
        self.reject_contract_changes([
            ('attack_selection', 'selection_is_goal_scheduled', False),
            ('attack_selection', 'monolith_roll_calls', 1),
            ('attack_selection', 'monolith_has_outer_maximum_range', True),
            ('attack_mode', 'hunting_cooldown_reset', True),
            ('attack_mode', 'continuation_checks_attack_state', True),
        ])

    def test_rage_hit_latch_crash_and_charge_velocity_remain_distinct(self):
        self.reject_contract_changes([
            ('rage_crash', 'charge_start_clears_hit', True),
            ('rage_crash', 'charge_contact_sets_hit', True),
            ('rage_crash', 'monolith_stop_increments_rage', True),
            ('rage_crash', 'crash_reset_on_run_stop', False),
            ('charge_chain', 'movement_is_native_knockback', True),
            ('charge_chain', 'run_motion_requires_target', True),
            ('charge_chain', 'run_tick_calls_parent', True),
        ])

    def test_hurt_returns_shield_independence_and_hp_formulas(self):
        self.reject_contract_changes([
            ('charge_contact', 'push_requires_hurt_true', False),
            ('charge_contact', 'push_requires_on_ground', False),
            ('charge_contact', 'terrain_result_gates_damage', True),
            ('bite', 'shield_requires_hurt_true', True),
            ('tail_slam', 'quake_spawn_requires_area_hurt_true', True),
            ('tail_swing', 'status_requires_hurt_true', False),
            ('tail_swing', 'push_requires_on_ground', True),
            ('stomp_contact', 'hp_addition_capped', True),
            ('stomp_contact', 'pull_requires_hurt_true', False),
        ])

    def test_stomp_native_schedule_and_unused_argument(self):
        self.reject_contract_changes([
            ('stomp_chain', 'powered_goal_max_ticks', 68),
            ('stomp_chain', 'declared_powered_last_payload_tick', 66),
            ('stomp_chain', 'unused_airborne_argument', 0.15),
        ])
        rows = {e['id']: e for e in selected(self.review)}
        self.row('stomp_chain')['wave_profiles']['9'][1]['side_offset'] *= -1
        with self.assertRaises(AssertionError):
            validate_contracts(rows)

    def test_stomp_debris_is_not_an_extra_damage_or_terrain_payload(self):
        self.reject_contract_changes([
            ('stomp_debris', 'debris_adds_damage', True),
            ('stomp_debris', 'stomp_removes_terrain', True),
            ('stomp_debris', 'stomp_places_terrain', True),
            ('monolith_chain', 'has_terrain_destruction', True),
            ('terrain_control', 'destroy_result_gates_debris', True),
        ])

    def test_storm_orbit_lifespan_and_status_gates(self):
        self.reject_contract_changes([
            ('roar_chain', 'spawn_requires_hurt_true', True),
            ('sandstorm_payload', 'has_bilateral_allied_check', False),
            ('sandstorm_payload', 'status_requires_hurt_true', False),
            ('sandstorm_payload', 'local_damage_server_guard', True),
            ('sandstorm_payload', 'has_radial_distance_check', True),
            ('sandstorm_motion', 'orbit_is_collision_radius', True),
            ('sandstorm_lifecycle', 'offset_saved', True),
            ('sandstorm_lifecycle', 'discard_returns_early', True),
        ])

    def test_quake_native_owner_parent_motion_and_expiry(self):
        self.reject_contract_changes([
            ('earthquake_contact', 'caster_absence_damage_fallback', True),
            ('earthquake_contact', 'contact_gated_by_projectile_impact_hook', True),
            ('earthquake_contact', 'has_bilateral_allied_check', True),
            ('earthquake_motion', 'concrete_move_precedes_parent', False),
            ('earthquake_motion', 'owner_death_still_ticks_parent', False),
            ('earthquake_motion', 'damage_saved', True),
            ('earthquake_motion', 'expiry_discard_returns_early', True),
        ])

    def test_monolith_native_delays_placement_and_distinct_caster(self):
        self.reject_contract_changes([
            ('monolith_chain', 'attempted_entity_count', 128),
            ('monolith_chain', 'requires_found_ceiling', True),
            ('monolith_chain', 'sets_native_projectile_owner', True),
            ('monolith_chain', 'local_spawn_server_guard', True),
        ])

    def test_stele_ray_hurt_status_motion_and_native_nbt(self):
        self.reject_contract_changes([
            ('stele_contact', 'status_requires_hurt_true', False),
            ('stele_contact', 'enchantment_requires_alive_after_hurt', True),
            ('stele_contact', 'impact_discard_requires_hurt_true', True),
            ('stele_contact', 'damage_requires_activation', True),
            ('stele_lifecycle', 'ray_precedes_activation', False),
            ('stele_lifecycle', 'final_position_uses_pre_update_velocity', False),
            ('stele_lifecycle', 'activation_saved', True),
            ('stele_lifecycle', 'nbt_calls_parent', True),
        ])

    def test_native_team_terrain_and_death_callbacks(self):
        self.reject_contract_changes([
            ('terrain_control', 'grief_actor', 'PAYLOAD'),
            ('terrain_control', 'has_destroy_event_hook', False),
            ('alliance', 'scoped_selector_tag', 'TEAM_ANCIENT_REMNANT'),
            ('defeat_lifecycle', 'death_state_write_checks_parent_admission', True),
            ('defeat_lifecycle', 'has_death_damage_payload', True),
            ('defeat_lifecycle', 'respawner_item', 'cataclysm:mech_eye'),
        ])

    def test_native_boundary_validator_detects_lost_parent_tick(self):
        evidence = read_json(EVIDENCE_FILE)
        w = next(w for w in evidence['witnesses'] if w['entry'].endswith('/EarthQuake_Entity.class'))
        m = next(m for m in w['methods'] if m['name'] == 'tick')
        m['instructions'] = [i for i in m['instructions'] if 'ThrowableProjectile.tick(' not in str(i['operand'])]
        with self.assertRaises((AssertionError, IndexError)):
            validate_native_boundaries(evidence)

    def test_protected_r2k7a_and_prior_family_records_unchanged(self):
        for checkpoint in ['R2k7a-cataclysm-remnant-admission-complete',
                           'R2k6b-cataclysm-harbinger-offense-complete',
                           'R2k5b-cataclysm-ignis-offense-complete']:
            with self.subTest(checkpoint=checkpoint):
                original = copy.deepcopy(self.review)
                e = next(e for e in self.review['effects'] if e['review_checkpoint'] == checkpoint)
                e['actual_behavior'] = 'Silently changed protected facts'
                with self.assertRaises(AssertionError):
                    validate_preservation(self.review, self.note, self.ledger)
                self.review = original

    def test_whole_mod_cannot_be_marked_complete(self):
        self.ledger['status'] = 'COMPLETE'
        with self.assertRaises(AssertionError):
            self.check()

    def test_no_stage_policy_or_runtime_claim(self):
        self.note['stage_eligibility_decided'] = True
        with self.assertRaises(AssertionError):
            self.check()

    def test_deterministic_json_format(self):
        for path in [REVIEW, NOTE, LEDGER, EVIDENCE_FILE, SPEC_FILE]:
            with self.subTest(file=path.name):
                self.assertEqual(path.read_bytes(),
                    (json.dumps(read_json(path), ensure_ascii=False, indent=2) + '\n').encode('utf-8'))


if __name__ == '__main__':
    unittest.main()
