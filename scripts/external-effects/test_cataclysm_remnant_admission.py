"""Focused R2k7a archive regressions; no runtime or Stage policy tests."""
import copy
import json
import unittest

from catalog_common import read_json
from collect_cataclysm_remnant_admission import EVIDENCE_FILE, SPEC_FILE
from validate_cataclysm_remnant_admission import (
    LEDGER, NOTE, REVIEW, selected, validate, validate_contracts,
    validate_native_distinctions, validate_preservation, validate_records,
)


class RemnantAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.review, self.note, self.ledger = [read_json(p) for p in [REVIEW, NOTE, LEDGER]]

    def row(self, key):
        return next(e for e in selected(self.review) if e['id'] == 'cataclysm:remnant_' + key)

    def check(self):
        return validate_records(self.review, self.note, self.ledger)

    def reject_contract_changes(self, changes):
        for key, field, value in changes:
            with self.subTest(mechanic=key, field=field):
                rows = copy.deepcopy({e['id'].removeprefix('cataclysm:remnant_'): e for e in selected(self.review)})
                rows[key][field] = value
                with self.assertRaises(AssertionError):
                    validate_contracts(rows, self.note)

    def test_scoped_archive_and_locked_contracts(self):
        result = validate()
        self.assertEqual(result['status'], 'PASS')
        self.assertEqual(result['new_mechanics'], 8)
        self.assertEqual(result['delivery_paths'], 8)
        self.assertEqual(result['candidate_numeric_parameters'], 2)
        self.assertEqual(result['new_method_witnesses'], 38)
        self.assertEqual(result['protected_shared_status_guardian_monstrosity_ignis_harbinger'], 'BYTE_IDENTICAL')

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

    def test_heal_candidate_keeps_primitive_value_and_formula(self):
        for field, value in [('primitive', 'DAMAGE_CAP'), ('native_value', 1.0), ('native_formula', 'Combined regeneration')]:
            with self.subTest(field=field):
                original = copy.deepcopy(self.review)
                self.row('nature_regen_binding')['scalable_parameter_candidates'][0][field] = value
                with self.assertRaises(AssertionError):
                    self.check()
                self.review = original

    def test_nonfinite_native_observation_rejected(self):
        self.row('powered_regeneration')['components'][0]['numerical_parameters']['amount'] = float('inf')
        with self.assertRaises(AssertionError):
            self.check()

    def test_only_two_named_native_heal_amounts_are_candidates(self):
        candidates = [(e['id'], c['primitive'], c['parameters'], c['native_value'])
                      for e in selected(self.review) for c in e['scalable_parameter_candidates']]
        self.assertEqual(candidates, [
            ('cataclysm:remnant_nature_regen_binding', 'NATIVE_HEAL', ['amount'], 25.0),
            ('cataclysm:remnant_powered_regeneration', 'NATIVE_HEAL', ['amount'], 1.0),
        ])

    def test_admission_order_and_unconditional_arrow_filter(self):
        order = self.row('incoming_admission')['admission_order']
        self.reject_contract_changes([
            ('incoming_admission', 'admission_order', [order[1], order[0], *order[2:]]),
            ('incoming_admission', 'direct_arrow_bypass_exemption', True),
            ('incoming_admission', 'post_hurt_state_write', True),
            ('incoming_admission', 'incoming_amount_rewritten', True),
            ('incoming_admission', 'concrete_is_invulnerable_override', True),
        ])

    def test_cap_drain_range_and_native_fire_binding_distinctions(self):
        self.reject_contract_changes([
            ('shared_defense_bindings', 'damage_cap_is_bucket_capacity', False),
            ('shared_defense_bindings', 'dps_is_bucket_capacity', True),
            ('shared_defense_bindings', 'range_narrows_float_before_double', False),
            ('shared_defense_bindings', 'dps_limit_time_read_by_bindings', True),
            ('shared_defense_bindings', 'registered_fire_immune', False),
        ])
        primitives = {c['primitive'] for c in self.row('shared_defense_bindings')['components']}
        self.assertEqual(primitives, {'DAMAGE_CAP', 'DPS_BUCKET', 'RANGE_ADMISSION',
                                     'REGEN_ADMISSION_TIMER', 'NATIVE_FIRE_ADMISSION'})

    def test_necklace_setter_does_not_invent_state_or_heal_writes(self):
        self.reject_contract_changes([
            ('activation_state', 'default_necklace', False),
            ('activation_state', 'necklace_setter_changes_attack_state', True),
            ('activation_state', 'necklace_setter_heals', True),
            ('activation_state', 'awakening_goal_has_velocity_write', True),
        ])

    def test_live_hp_and_saved_power_are_distinct(self):
        self.reject_contract_changes([
            ('phase_prerequisites', 'live_power_is_saved', True),
            ('phase_prerequisites', 'stored_power_is_saved', False),
            ('phase_prerequisites', 'power_setter_rewrites_health', True),
            ('phase_prerequisites', 'phase_can_use_requires_target', True),
            ('phase_prerequisites', 'phase_can_use_requires_necklace', True),
            ('phase_prerequisites', 'power_latch_tick', 13),
            ('phase_prerequisites', 'power_latch_local_server_guard', True),
        ])

    def test_powered_heal_keeps_its_separate_native_gates(self):
        self.reject_contract_changes([('powered_regeneration', field, True) for field in [
            'local_server_guard', 'reads_live_hp_predicate', 'reads_self_regen',
            'reads_target', 'reads_no_ai', 'reads_necklace']])

    def test_missing_nbt_defaults_and_unsaved_crash_state(self):
        self.reject_contract_changes([
            ('combat_persistence', 'missing_key_defaults', {'has_necklace': True, 'Rage': 0, 'Power': False}),
            ('combat_persistence', 'crash_saved', True),
            ('combat_persistence', 'attack_state_saved', True),
            ('combat_persistence', 'rage_setter_clamps', True),
            ('combat_persistence', 'generic_persistence_added', True),
        ])

    def test_marker_and_interaction_home_boundaries(self):
        order = self.row('encounter_prerequisites')['interaction_order']
        self.reject_contract_changes([
            ('encounter_prerequisites', 'marker_sets_home', True),
            ('encounter_prerequisites', 'marker_sets_attack_state', True),
            ('encounter_prerequisites', 'marker_necklace', True),
            ('encounter_prerequisites', 'marker_persistence_required', False),
            ('encounter_prerequisites', 'interaction_order', [order[0], order[2], order[1], *order[3:]]),
            ('encounter_prerequisites', 'interaction_heals', True),
            ('encounter_prerequisites', 'interaction_local_server_guard', True),
        ])

    def test_odd_attribute_builder_name_keeps_native_entity_ownership(self):
        self.reject_contract_changes([
            ('encounter_prerequisites', 'attributes_apply_to', 'cataclysm:maledictus'),
            ('encounter_prerequisites', 'configured_health_is_heal_delivery', True),
            ('encounter_prerequisites', 'registered_dimensions', {'width': 2.85, 'height': 5.0}),
        ])

    def test_guard_detects_lost_native_arrow_prefilter(self):
        evidence = read_json(EVIDENCE_FILE)
        witness = next(w for w in evidence['witnesses'] if w['entry'].endswith('/Ancient_Remnant_Entity.class'))
        hurt = next(m for m in witness['methods'] if m['name'] == 'hurt')
        instruction = next(i for i in hurt['instructions'] if i['offset'] == 36)
        instruction['operand'] = 'net/minecraft/world/entity/LivingEntity'
        with self.assertRaises(AssertionError):
            validate_native_distinctions(evidence)

    def test_offense_and_payloads_are_not_captured(self):
        spec = read_json(SPEC_FILE)
        for row in spec['evidence_specifications']:
            self.assertNotIn('/entity/projectile/', row['entry'])
            self.assertNotIn('/entity/effect/', row['entry'])
            self.assertFalse({'AreaAttack', 'TailAreaAttack', 'Charge', 'StompDamage',
                              'EarthQuakeSummon', 'AfterDefeatBoss'} & set(row['methods']))

    def test_all_prior_boss_records_are_locked(self):
        for key in ['guardian_attack_selection', 'monstrosity_incoming_admission', 'ignis_shield_admission',
                    'harbinger_incoming_admission', 'harbinger_missile_contact']:
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
