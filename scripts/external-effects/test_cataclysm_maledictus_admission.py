"""Focused R2k8a archive regressions; no runtime, offense or Stage tests."""
import copy
import json
import unittest

from catalog_common import read_json
from collect_cataclysm_maledictus_admission import EVIDENCE_FILE, M, PKG, SPEC_FILE, TOMB
from validate_cataclysm_maledictus_admission import (
    LEDGER, NOTE, REVIEW, selected, validate, validate_contracts,
    validate_native_distinctions, validate_preservation, validate_records,
)


class MaledictusAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.review, self.note, self.ledger = [read_json(p) for p in [REVIEW, NOTE, LEDGER]]

    def row(self, key):
        return next(e for e in selected(self.review) if e['id'] == 'cataclysm:maledictus_' + key)

    def check(self):
        return validate_records(self.review, self.note, self.ledger)

    def reject_contract_changes(self, changes):
        for key, field, value in changes:
            with self.subTest(mechanic=key, field=field):
                rows = copy.deepcopy({e['id'].removeprefix('cataclysm:maledictus_'): e
                                      for e in selected(self.review)})
                rows[key][field] = value
                with self.assertRaises(AssertionError):
                    validate_contracts(rows, self.note)

    def test_scoped_archive_and_locked_contracts(self):
        result = validate()
        self.assertEqual(result['status'], 'PASS')
        self.assertEqual(result['new_mechanics'], 8)
        self.assertEqual(result['delivery_paths'], 8)
        self.assertEqual(result['candidate_numeric_parameters'], 1)
        self.assertEqual(result['new_method_witnesses'], 37)
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

    def test_heal_candidate_preserves_primitive_formula_and_amount(self):
        for field, value in [('primitive', 'DAMAGE_CAP'), ('native_value', 20.0),
                             ('native_formula', 'Combined regen and rage')]:
            with self.subTest(field=field):
                original = copy.deepcopy(self.review)
                self.row('nature_regen_binding')['scalable_parameter_candidates'][0][field] = value
                with self.assertRaises(AssertionError):
                    self.check()
                self.review = original

    def test_only_original_shared_heal_amount_is_a_candidate(self):
        candidates = [(e['id'], c['primitive'], c['parameters'], c['native_value'])
                      for e in selected(self.review) for c in e['scalable_parameter_candidates']]
        self.assertEqual(candidates, [
            ('cataclysm:maledictus_nature_regen_binding', 'NATIVE_HEAL', ['amount'], 25.0)])

    def test_nonfinite_observation_rejected(self):
        self.row('encounter_setup')['components'][0]['numerical_parameters']['armor'] = float('inf')
        with self.assertRaises(AssertionError):
            self.check()

    def test_state_gate_precedes_unconditional_pre_hurt_arming(self):
        order = self.row('incoming_admission')['admission_order']
        self.reject_contract_changes([
            ('incoming_admission', 'admission_order', [order[1], order[0], *order[2:]]),
            ('incoming_admission', 'timer_armed_before_shared_hurt', False),
            ('incoming_admission', 'timer_requires_hurt_success', True),
            ('incoming_admission', 'post_hurt_state_write', True),
            ('incoming_admission', 'incoming_amount_rewritten', True),
            ('incoming_admission', 'concrete_is_invulnerable_override', True),
            ('incoming_admission', 'local_direct_or_causing_filter', True),
            ('incoming_admission', 'hurt_reads_weapon_flying_rage', True),
        ])

    def test_cap_bucket_range_and_unused_dps_multi_remain_distinct(self):
        self.reject_contract_changes([
            ('shared_defense_bindings', 'damage_cap_is_bucket_capacity', False),
            ('shared_defense_bindings', 'dps_is_bucket_capacity', True),
            ('shared_defense_bindings', 'range_narrows_float_before_double', True),
            ('shared_defense_bindings', 'dps_multi_read_by_shared_hurt_or_tick', True),
        ])

    def test_environment_callbacks_do_not_invent_global_damage_immunity(self):
        self.reject_contract_changes([
            ('environment_admission', 'registered_fire_immune', False),
            ('environment_admission', 'fall_callback_calls_parent', True),
            ('environment_admission', 'air_supply_returns_input', False),
            ('environment_admission', 'fluid_push', True),
            ('environment_admission', 'blanket_drowning_damage_immunity_claimed', True),
        ])
        self.assertEqual({c['primitive'] for c in self.row('environment_admission')['components']},
            {'NATIVE_FIRE_ADMISSION', 'NATIVE_FALL_ADMISSION', 'AIR_SUPPLY_GATE', 'FLUID_RESPONSE_GATE'})

    def test_live_health_and_raw_state_do_not_invent_saved_phase_or_shield(self):
        self.reject_contract_changes([
            ('phase_state_prerequisites', field, True) for field in [
                'raw_integer_setters_clamp', 'state_setters_change_attack_state',
                'state_setters_heal', 'health_predicates_saved', 'separate_saved_phase_or_shield_latch']])

    def test_rage_decay_and_flight_keep_native_gates(self):
        self.reject_contract_changes([
            ('phase_state_prerequisites', 'rage_decay_server_only', False),
            ('phase_state_prerequisites', 'rage_decay_no_ai_gate', True),
            ('phase_state_prerequisites', 'rage_decay_target_gate', True),
            ('phase_state_prerequisites', 'flight_no_gravity_local_server_guard', True),
        ])

    def test_concrete_nbt_keeps_transient_state_unsaved(self):
        self.reject_contract_changes([
            ('combat_persistence', field, True) for field in [
                'saved_weapon', 'saved_flying', 'saved_attack_state', 'saved_rage_ticks',
                'saved_destroy_blocks_tick', 'generic_persistence_added']])

    def test_native_attribute_owner_and_configuration_are_not_heal_payloads(self):
        self.reject_contract_changes([
            ('encounter_setup', 'attributes_apply_to', 'cataclysm:ancient_remnant'),
            ('encounter_setup', 'configured_health_is_heal_delivery', True),
            ('encounter_setup', 'explicit_armor_toughness_added', True),
            ('encounter_setup', 'registered_dimensions', dict(width=4.35, height=5.0)),
        ])

    def test_spawn_home_and_finalization_overwrite_order(self):
        order = self.row('tombstone_encounter')['spawn_order']
        self.reject_contract_changes([
            ('tombstone_encounter', 'spawn_order', [*order[:4], order[5], order[4], *order[6:]]),
            ('tombstone_encounter', 'block_facing_survives_finalize', True),
            ('tombstone_encounter', 'spawn_sets_home', False),
            ('encounter_setup', 'finalize_sets_home', True),
            ('encounter_setup', 'finalize_direction', 'NORTH'),
        ])

    def test_tombstone_activation_retry_and_cleanup_gates_are_native(self):
        self.reject_contract_changes([
            ('tombstone_encounter', field, True) for field in [
                'activation_requires_item', 'activation_consumes_item', 'activation_local_server_guard',
                'ticker_has_side_gate', 'clearance_requires_mobgriefing',
                'retry_counter_reset_on_failed_add', 'spawn_sets_persistence_required', 'spawn_sets_attack_state']]
            + [('tombstone_encounter', 'cleanup_requires_add_success', False)])

    def test_literal_cooldown_load_mismatch_is_not_silently_repaired(self):
        self.reject_contract_changes([
            ('tombstone_encounter', 'cooldown_load_tag_type', 3),
            ('tombstone_encounter', 'cooldown_int_round_trip', True),
            ('tombstone_encounter', 'countdown_saved', True),
        ])

    def test_native_witness_guards_detect_changed_arming_and_nbt_literal(self):
        for entry, method, offset, value in [(M, 'hurt', 47, 19),
                                             (TOMB, 'loadAdditional', 10, 3)]:
            with self.subTest(entry=entry, method=method):
                evidence = read_json(EVIDENCE_FILE)
                w = next(w for w in evidence['witnesses'] if w['entry'] == PKG + entry + '.class')
                m = next(m for m in w['methods'] if m['name'] == method)
                next(i for i in m['instructions'] if i['offset'] == offset)['operand'] = value
                with self.assertRaises(AssertionError):
                    validate_native_distinctions(evidence)

    def test_no_offense_payload_or_parent_body_is_recaptured(self):
        spec = read_json(SPEC_FILE)
        self.assertEqual(len(spec['evidence_specifications']), 4)
        for row in spec['evidence_specifications']:
            self.assertNotIn('/entity/projectile/', row['entry'])
            self.assertNotIn('/entity/effect/', row['entry'])
            self.assertFalse({'aiStep', 'registerGoals', 'DMG', 'AreaAttack', 'Grab', 'Rushattack',
                              'ShieldSmashDamage', 'blockbreak', 'AfterDefeatBoss'} & set(row['methods']))

    def test_previous_guardian_through_remnant_records_are_locked(self):
        for key in ['guardian_attack_selection', 'monstrosity_incoming_admission', 'ignis_shield_admission',
                    'harbinger_incoming_admission', 'remnant_incoming_admission', 'remnant_attack_selection']:
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
