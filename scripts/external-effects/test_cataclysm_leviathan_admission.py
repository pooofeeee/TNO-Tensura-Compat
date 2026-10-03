"""Focused R2k9a regressions; no runtime, offense or Stage testing."""
import copy
import json
import unittest

from catalog_common import read_json
from collect_cataclysm_leviathan_admission import ALTAR, EVIDENCE_FILE, L, PKG, SPEC_FILE
from validate_cataclysm_leviathan_admission import (
    LEDGER, NOTE, REVIEW, selected, validate, validate_contracts,
    validate_native_distinctions, validate_preservation, validate_records,
)


class LeviathanAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.review, self.note, self.ledger = [read_json(p) for p in [REVIEW, NOTE, LEDGER]]

    def row(self, key):
        return next(e for e in selected(self.review) if e['id'] == 'cataclysm:leviathan_' + key)

    def check(self):
        return validate_records(self.review, self.note, self.ledger)

    def reject_contract_changes(self, changes):
        for key, field, value in changes:
            with self.subTest(mechanic=key, field=field):
                rows = copy.deepcopy({e['id'].removeprefix('cataclysm:leviathan_'): e
                                      for e in selected(self.review)})
                rows[key][field] = value
                with self.assertRaises(AssertionError):
                    validate_contracts(rows, self.note)

    def test_scoped_archive_and_locked_contracts(self):
        result = validate()
        self.assertEqual(result['status'], 'PASS')
        self.assertEqual(result['new_mechanics'], 10)
        self.assertEqual(result['delivery_paths'], 10)
        self.assertEqual(result['candidate_numeric_parameters'], 1)
        self.assertEqual(result['new_method_witnesses'], 61)
        self.assertEqual(result['protected_shared_status_and_prior_bosses'], 'BYTE_IDENTICAL')

    def test_duplicate_id_rejected(self):
        selected(self.review)[1]['id'] = selected(self.review)[0]['id']
        with self.assertRaises(AssertionError):
            self.check()

    def test_invalid_classification_rejected(self):
        selected(self.review)[0]['primary_classification'] = 'INVENTED'
        with self.assertRaises(AssertionError):
            self.check()

    def test_missing_source_or_delivery_rejected(self):
        for field in ['source_actor', 'primary_test_source', 'delivery_paths']:
            with self.subTest(field=field):
                original = copy.deepcopy(self.review)
                selected(self.review)[0][field] = None
                with self.assertRaises(AssertionError):
                    self.check()
                self.review = original

    def test_candidate_preserves_shared_heal_primitive_and_formula(self):
        for field, value in [('primitive', 'DAMAGE_CAP'), ('native_value', 20.0),
                             ('native_formula', 'Combined phase and regen')]:
            with self.subTest(field=field):
                original = copy.deepcopy(self.review)
                self.row('nature_regen_binding')['scalable_parameter_candidates'][0][field] = value
                with self.assertRaises(AssertionError):
                    self.check()
                self.review = original

    def test_only_shared_heal_amount_is_a_candidate(self):
        candidates = [(e['id'], c['primitive'], c['parameters'], c['native_value'])
                      for e in selected(self.review) for c in e['scalable_parameter_candidates']]
        self.assertEqual(candidates, [
            ('cataclysm:leviathan_nature_regen_binding', 'NATIVE_HEAL', ['amount'], 25.0)])
        self.reject_contract_changes([('nature_regen_binding', 'adds_second_heal', True)])

    def test_nonfinite_observation_rejected(self):
        self.row('encounter_setup')['components'][0]['numerical_parameters']['armor'] = float('inf')
        with self.assertRaises(AssertionError):
            self.check()

    def test_direct_class_exclusion_precedes_tag_exceptions_and_timer(self):
        order = self.row('incoming_admission')['admission_order']
        self.reject_contract_changes([
            ('incoming_admission', 'admission_order', [order[1], order[0], *order[2:]]),
            ('incoming_admission', 'direct_exclusion_bypassable', True),
            ('incoming_admission', 'timer_requires_hurt_success', True),
            ('incoming_admission', 'timer_armed_before_shared_hurt', False),
            ('incoming_admission', 'incoming_amount_rewritten', True),
            ('incoming_admission', 'source_object_preserved', False),
        ])

    def test_eye_fluid_capability_is_not_water_equality_or_local_range_filter(self):
        self.reject_contract_changes([
            ('incoming_admission', 'fluid_gate_uses_eye_fluid', False),
            ('incoming_admission', 'fluid_gate_is_water_type_equality', True),
            ('incoming_admission', 'local_range_read_result_used', True),
            ('incoming_admission', 'feedback_uses_direct_player', False),
            ('incoming_admission', 'phase_gate_uses_animation_not_saved_latch', False),
        ])

    def test_rush_interruption_requires_return_and_is_animation_not_status(self):
        self.reject_contract_changes([
            ('rush_hurt_interruption', 'interruption_requires_hurt_true', False),
            ('rush_hurt_interruption', 'interruption_requires_measured_hp_loss', True),
            ('rush_hurt_interruption', 'interruption_is_mob_effect', True),
            ('rush_hurt_interruption', 'local_interruption_server_guard', True),
            ('rush_hurt_interruption', 'adds_outgoing_damage', True),
        ])

    def test_multipart_is_single_root_admission_and_return_dependent_event(self):
        self.reject_contract_changes([
            ('multipart_admission', field, True) for field in ['part_damage_multiplier_added',
                'part_scale_used_in_hurt', 'part_hurt_calls_super', 'part_hurt_checks_own_invulnerability']]
            + [('multipart_admission', 'game_event_requires_hurt_true', False)])

    def test_cap_bucket_range_and_concrete_regen_cooldown_remain_distinct(self):
        self.reject_contract_changes([
            ('shared_defense_bindings', 'damage_cap_is_bucket_capacity', False),
            ('shared_defense_bindings', 'dps_is_bucket_capacity', True),
            ('shared_defense_bindings', 'range_narrows_float_before_double', True),
            ('shared_defense_bindings', 'dps_multi_read_by_shared_hurt_or_tick', True),
        ])
        changed = copy.deepcopy(self.note)
        changed['concrete_bindings']['HealCooldown']['native_value'] = 200
        with self.assertRaises(AssertionError):
            validate_records(self.review, changed, self.ledger)

    def test_exact_environment_filters_do_not_invent_blanket_immunity(self):
        self.reject_contract_changes([
            ('environment_admission', 'exact_type_filter_precedes_shared_bypass', False),
            ('environment_admission', 'air_supply_returns_native_max', False),
            ('environment_admission', 'bubble_callbacks_call_parent', True),
            ('environment_admission', 'blanket_drowning_damage_immunity_claimed', True),
            ('environment_admission', 'concrete_fall_damage_override', True),
        ])

    def test_receiving_status_contract_is_reused_without_recapture(self):
        self.assertIn('native-evidence/cataclysm-abyssal.json', {
            r['file'] for r in self.note['reference_files'] if r['usage'] == 'LOCKED_REUSED'})
        native = next(w for w in read_json(EVIDENCE_FILE)['witnesses']
                      if w['entry'] == PKG + L + '.class')
        self.assertNotIn('canBeAffected', {m['name'] for m in native['methods']})
        self.assertIn('Reuse locked R2k2d', self.note['facts']['effects'])

    def test_live_health_saved_latch_and_raw_setters_remain_separate(self):
        self.reject_contract_changes([
            ('phase_state_prerequisites', field, True) for field in [
                'live_health_predicate_is_saved_latch', 'raw_integer_setters_clamp',
                'raw_setters_heal', 'raw_setters_change_animation', 'healing_clears_saved_latch',
                'mode_chance_is_attack_mode_enum']])

    def test_phase_prerequisites_keep_original_local_gates(self):
        self.reject_contract_changes([
            ('phase_state_prerequisites', 'phase_start_has_no_ai_gate', False)] + [
            ('phase_state_prerequisites', field, True) for field in [
                'phase_start_local_server_guard', 'phase_start_requires_target',
                'phase_start_requires_fluid', 'latch_write_local_server_guard', 'latch_write_local_no_ai_gate']])

    def test_combat_nbt_does_not_persist_transient_execution_state(self):
        self.reject_contract_changes([
            ('combat_persistence', field, True) for field in [
                'saved_animation', 'saved_attack_mode', 'saved_tongue_uuid', 'saved_tongue_id',
                'saved_portal_target', 'saved_terrain_timer', 'saved_native_attack_timers',
                'generic_persistence_added']])

    def test_construction_is_not_heal_or_phase_delivery(self):
        self.reject_contract_changes([
            ('encounter_setup', 'attributes_apply_to', 'cataclysm:leviathan'),
            ('encounter_setup', 'configured_health_is_heal_delivery', True),
            ('encounter_setup', 'constructor_sets_home', True),
            ('encounter_setup', 'constructor_sets_phase_latch', True),
            ('encounter_setup', 'concrete_finalize_spawn_override', True),
        ])

    def test_altar_clearance_and_create_precede_server_spawn_guard(self):
        order = self.row('altar_encounter')['spawn_order']
        self.reject_contract_changes([
            ('altar_encounter', 'spawn_order', [order[0], order[3], *order[1:3], *order[4:]]),
            ('altar_encounter', 'clearance_has_local_server_guard', True),
            ('altar_encounter', 'clearance_requires_mobgriefing', True),
            ('altar_encounter', 'clearance_precedes_create', False),
            ('altar_encounter', 'spawn_sets_home', False),
            ('altar_encounter', 'spawn_calls_finalize_spawn', True),
            ('altar_encounter', 'spawn_requires_water', True),
        ])

    def test_altar_consumption_retry_and_inventory_persistence_are_native(self):
        self.reject_contract_changes([
            ('altar_encounter', 'cleanup_requires_add_success', False),
            ('altar_encounter', 'inventory_saved', False)] + [
            ('altar_encounter', field, True) for field in ['altar_removed_on_add_success',
                'retry_counter_reset_on_failed_add', 'countdown_saved', 'summoning_flag_saved',
                'ticker_has_side_gate', 'activation_local_server_guard', 'placement_requires_sacrifice']])

    def test_witness_guards_detect_changed_native_literals(self):
        for entry, method, offset, value in [(L, 'hurt', 29, 19),
                (L, 'hurt', 143, 37), (L, 'HealCooldown', 0, 200), (ALTAR, 'tick', 111, 120)]:
            with self.subTest(entry=entry, method=method):
                evidence = read_json(EVIDENCE_FILE)
                w = next(w for w in evidence['witnesses'] if w['entry'] == PKG + entry + '.class')
                m = next(m for m in w['methods'] if m['name'] == method)
                next(i for i in m['instructions'] if i['offset'] == offset)['operand'] = value
                with self.assertRaises(AssertionError):
                    validate_native_distinctions(evidence)

    def test_no_offense_payload_or_shared_parent_body_recaptured(self):
        spec = read_json(SPEC_FILE)
        self.assertEqual(len(spec['evidence_specifications']), 7)
        for row in spec['evidence_specifications']:
            self.assertNotIn('/entity/projectile/', row['entry'])
            self.assertNotIn('/entity/effect/', row['entry'])
            self.assertNotIn('/LLibrary_Boss_Monster.class', row['entry'])
            if row['entry'] == PKG + L + '.class':
                self.assertFalse({'tick', 'aiStep', 'biteattack', 'TailWhips', 'registerGoals',
                    'AfterDefeatBoss', 'BlockBreaking', 'TentacleAttack', 'canBeAffected'} & set(row['methods']))

    def test_all_prior_boss_records_are_locked(self):
        for key in ['guardian_attack_selection', 'monstrosity_incoming_admission',
                'ignis_shield_admission', 'harbinger_incoming_admission', 'remnant_incoming_admission',
                'maledictus_incoming_admission', 'maledictus_attack_selection']:
            with self.subTest(mechanic=key):
                original = copy.deepcopy(self.review)
                e = next(e for e in self.review['effects'] if e['id'] == 'cataclysm:' + key)
                e['actual_behavior'] = 'Silently changed protected facts'
                with self.assertRaises(AssertionError):
                    validate_preservation(self.review, self.note, self.ledger)
                self.review = original

    def test_cataclysm_cannot_be_marked_complete(self):
        self.ledger['status'] = 'COMPLETE'
        with self.assertRaises(AssertionError):
            self.check()

    def test_deterministic_json_format(self):
        for path in [REVIEW, NOTE, LEDGER, EVIDENCE_FILE, SPEC_FILE]:
            with self.subTest(file=path.name):
                self.assertEqual(path.read_bytes(),
                    (json.dumps(read_json(path), ensure_ascii=False, indent=2) + '\n').encode('utf-8'))


if __name__ == '__main__':
    unittest.main()
