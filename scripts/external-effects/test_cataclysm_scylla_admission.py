"""Focused static regressions for R2k10a Scylla admission and prerequisites."""
import copy
import unittest

from catalog_common import read_json
from collect_cataclysm_scylla_admission import EVIDENCE_FILE, PKG, S
from validate_cataclysm_scylla_admission import (
    LEDGER, NOTE, REVIEW, selected, validate, validate_contracts,
    validate_native_boundaries, validate_preservation, validate_records,
)


class ScyllaAdmissionTests(unittest.TestCase):
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
        return next(e for e in selected(self.review) if e['id']=='cataclysm:scylla_'+key)

    def check(self):
        return validate_records(self.review,self.note,self.ledger)

    def reject_changes(self, changes):
        for key, field, value in changes:
            with self.subTest(mechanic=key,field=field):
                rows = {e['id'].removeprefix('cataclysm:scylla_'):copy.deepcopy(e) for e in selected(self.review)}
                rows[key][field] = value
                with self.assertRaises(AssertionError):
                    validate_contracts(rows,self.note)

    def test_archive_and_protected_contracts(self):
        result = validate()
        self.assertEqual(result['status'],'PASS')
        self.assertEqual(result['new_mechanics'],13)
        self.assertEqual(result['delivery_paths'],13)
        self.assertEqual(result['candidate_numeric_parameters'],1)
        self.assertEqual(result['new_method_witnesses'],57)
        self.assertEqual(result['protected_shared_status_and_prior_bosses'],'BYTE_IDENTICAL')
        self.assertEqual(result['prior_records_and_paths'],'UNCHANGED')

    def test_duplicate_mechanic_rejected(self):
        selected(self.review)[1]['id'] = selected(self.review)[0]['id']
        with self.assertRaises(AssertionError):
            self.check()

    def test_invalid_classification_rejected(self):
        self.row('incoming_admission')['primary_classification'] = 'INVENTED'
        with self.assertRaises(AssertionError):
            self.check()

    def test_source_and_delivery_required(self):
        for field in ['source_actor','primary_test_source','delivery_paths','implementation']:
            with self.subTest(field=field):
                self.review = copy.deepcopy(self.original_review)
                self.row('incoming_admission')[field] = None
                with self.assertRaises(AssertionError):
                    self.check()

    def test_admission_order_cannot_move_timer_before_native_rejections(self):
        order = self.row('incoming_admission')['admission_order']
        order[0],order[4] = order[4],order[0]
        with self.assertRaises(AssertionError):
            self.check()

    def test_original_source_amount_return_and_bypass_postwrite(self):
        self.reject_changes([
            ('incoming_admission','source_object_preserved',False),
            ('incoming_admission','incoming_amount_rewritten',True),
            ('incoming_admission','timer_requires_hurt_success',True),
            ('incoming_admission','bypass_skips_postwrite',True),
            ('incoming_admission','concrete_invulnerability_override',True),
        ])

    def test_facing_position_and_forced_vs_rng_cooldown_distinctions(self):
        self.reject_changes([
            ('parry_admission','facing_uses_source_position',False),
            ('parry_admission','facing_uses_causing_range',True),
            ('parry_admission','forced_parry_checks_cooldown',True),
            ('parry_admission','rng_parry_checks_cooldown',False),
            ('parry_admission','parry_is_shield_item',True),
        ])

    def test_true_hurt_counter_postwrite_is_not_clamped_or_window_gated(self):
        self.reject_changes([
            ('parry_state_prerequisites','postwrite_local_server_guard',True),
            ('parry_state_prerequisites','postwrite_requires_parry_window',True),
            ('parry_state_prerequisites','postwrite_can_overshoot18',False),
            ('parry_state_prerequisites','reset_cooldown_clamps_counter',True),
        ])

    def test_notification_zero_hurt_not_outgoing_payload(self):
        self.reject_changes([
            ('incoming_damage_notification','notification_hurt_return_consumed',True),
            ('incoming_damage_notification','notification_has_local_server_guard',True),
            ('incoming_damage_notification','notification_adds_outgoing_payload',True),
        ])

    def test_shared_cap_bucket_range_regen_stay_separate(self):
        self.reject_changes([
            ('shared_defense_bindings','dps_is_bucket_capacity',True),
            ('shared_defense_bindings','range_narrows_float_before_double',True),
            ('shared_defense_bindings','configured_dps_limit_time_used',True),
            ('shared_defense_bindings','concrete_heal_cooldown_override',True),
        ])

    def test_only_existing_shared_regen_binding_is_candidate(self):
        regen = self.row('nature_regen_binding')
        self.assertEqual(regen['binding_of'],'cataclysm:shared_heal')
        self.assertFalse(regen['adds_second_heal'])
        self.row('shared_defense_bindings')['scalable_parameter_candidates'] = copy.deepcopy(regen['scalable_parameter_candidates'])
        with self.assertRaises(AssertionError):
            self.check()

    def test_candidate_keeps_native_primitive_value_formula_units_boundary(self):
        for field,value in [('primitive','DAMAGE_CAP'),('native_value',1000),
                            ('native_formula','invented'),('units','unknown'),('native_boundary','invented hook')]:
            with self.subTest(field=field):
                self.review = copy.deepcopy(self.original_review)
                self.row('nature_regen_binding')['scalable_parameter_candidates'][0][field] = value
                with self.assertRaises(AssertionError):
                    self.check()

    def test_nonfinite_values_rejected(self):
        self.row('shared_defense_bindings')['components'][0]['numerical_parameters']['per_hit_cap'] = float('nan')
        with self.assertRaises(AssertionError):
            self.check()

    def test_no_stage_policy_or_hook(self):
        self.row('nature_regen_binding')['stage_multiplier'] = 2
        with self.assertRaises(AssertionError):
            self.check()

    def test_native_fire_air_and_fluid_admission_not_flattened(self):
        self.reject_changes([
            ('environment_admission','registered_fire_immune',False),
            ('environment_admission','air_returns_native_max',True),
            ('environment_admission','fluid_push',True),
            ('environment_admission','blanket_drowning_immunity_claimed',True),
        ])

    def test_phase_latched_at_start_without_added_goal_gates(self):
        self.reject_changes([
            ('phase_state_prerequisites','phase_latched_at_goal_start',False),
            ('phase_state_prerequisites','phase_latched_at_ai_step',True),
            ('phase_state_prerequisites','phase_goal_requires_target',True),
            ('phase_state_prerequisites','phase_goal_requires_alive',True),
            ('phase_state_prerequisites','phase_goal_local_no_ai_gate',True),
            ('phase_state_prerequisites','healing_clears_phase',True),
        ])

    def test_activation_flag_and_sleep_predicate_not_equivalent(self):
        self.reject_changes([
            ('activation_sleep_prerequisites','act_false_equals_sleep',True),
            ('activation_sleep_prerequisites','true_act_setter_wakes_directly',True),
            ('activation_sleep_prerequisites','false_act_setter_forces23',False),
            ('activation_sleep_prerequisites','fresh_constructor_forces23',True),
        ])

    def test_raw_state_and_literal_missing_act_nbt(self):
        self.reject_changes([
            ('raw_combat_state','raw_integer_setters_clamp',True),
            ('raw_combat_state','raw_setters_heal',True),
            ('combat_persistence','act_missing_forces23',False),
            ('combat_persistence','saved_parry_count',True),
            ('combat_persistence','saved_flying',True),
            ('combat_persistence','generic_persistence_added',True),
        ])

    def test_spawn_reason_activation_is_not_home_or_heal_delivery(self):
        self.reject_changes([
            ('encounter_setup','constructor_calls_set_act',True),
            ('encounter_setup','finalize_sets_home',True),
            ('encounter_setup','finalize_counts_players',True),
            ('encounter_setup','configured_health_is_heal_delivery',True),
            ('encounter_setup','spawn_activation_reasons',['STRUCTURE']),
        ])

    def test_activation_home_heal_counter_order_and_native_gates(self):
        self.reject_changes([
            ('activation_encounter','interaction_local_server_guard',True),
            ('activation_encounter','requires_specific_item',True),
            ('activation_encounter','consumes_item',True),
            ('activation_encounter','activation_directly_sets_attack_state',True),
            ('activation_encounter','full_heal_is_stage_candidate',True),
            ('activation_encounter','activation_order',[]),
        ])

    def test_native_postwrite_cannot_ignore_hurt_return(self):
        evidence = copy.deepcopy(self.original_evidence)
        witness = next(w for w in evidence['witnesses'] if w['entry']==PKG+S+'.class')
        hurt = next(m for m in witness['methods'] if m['name']=='hurt')
        next(i for i in hurt['instructions'] if i['offset']==234)['opcode'] = '0x00'
        with self.assertRaises(AssertionError):
            validate_native_boundaries(evidence)

    def test_prior_leviathan_record_cannot_change(self):
        row = next(e for e in self.review['effects'] if e['id']=='cataclysm:leviathan_incoming_admission')
        row['actual_behavior'] = 'changed'
        with self.assertRaises(AssertionError):
            validate_preservation(self.review,self.note,self.ledger)

    def test_partial_and_exact_bounded_next_task_required(self):
        for field,value in [('status','COMPLETE'),('whole_mod_complete',True),
                            ('exact_next_task','R2k11: Unbounded scan')]:
            with self.subTest(field=field):
                self.note = copy.deepcopy(self.original_note)
                self.note[field] = value
                with self.assertRaises(AssertionError):
                    self.check()


if __name__ == '__main__':
    unittest.main()
