"""Focused regressions for bounded R2k14a Kobolediator static research."""
import copy
import unittest

from catalog_common import read_json
from collect_cataclysm_kobolediator_admission import D, EVIDENCE_FILE, K, PKG, PYRAMID, REGISTRY
from validate_cataclysm_kobolediator_admission import (
    LEDGER, NOTE, REVIEW, selected, validate, validate_contracts,
    validate_native_boundaries, validate_preservation, validate_records,
)


class KobolediatorAdmissionTests(unittest.TestCase):
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
        return next(e for e in selected(self.review) if e['id']=='cataclysm:kobolediator_'+key)

    def check(self):
        return validate_records(self.review, self.note, self.ledger)

    def reject_facts(self, changes):
        for key, field, value in changes:
            with self.subTest(mechanic=key, field=field):
                rows = copy.deepcopy({e['id'].removeprefix('cataclysm:kobolediator_'):e
                                      for e in selected(self.review)})
                rows[key][field] = value
                with self.assertRaises(AssertionError):
                    validate_contracts(rows, self.note)

    def test_checkpoint_evidence_formatting_and_protected_families(self):
        result = validate()
        self.assertEqual(result['status'], 'PASS')
        self.assertEqual(result['new_mechanics'], 15)
        self.assertEqual(result['candidate_numeric_parameters'], 0)
        self.assertEqual(result['new_method_witnesses'], 31)
        self.assertEqual(result['protected_shared_status_prior_families_berserker'], 'BYTE_IDENTICAL')

    def test_unique_ids_classifications_and_source_delivery(self):
        selected(self.review)[1]['id'] = selected(self.review)[0]['id']
        with self.assertRaises(AssertionError):self.check()
        for field, value in [('primary_classification', 'INVENTED'), ('source_actor', None),
                             ('delivery_paths', None), ('hurt_return_dependency', None)]:
            with self.subTest(field=field):
                self.review = copy.deepcopy(self.original_review)
                self.row('incoming_admission')[field] = value
                with self.assertRaises(AssertionError):self.check()

    def test_native_observations_not_automatic_stage_candidates(self):
        for e in selected(self.review):
            with self.subTest(mechanic=e['id']):
                rows=copy.deepcopy(self.original_review)
                next(r for r in rows['effects'] if r['id']==e['id'])['scalable_parameter_candidates']=[
                    dict(primitive=e['components'][0]['primitive'],parameter='invented')]
                with self.assertRaises(AssertionError):validate_records(rows,self.note,self.ledger)

    def test_admission_order_and_direct_actor_identity(self):
        self.note['admission_order'][1], self.note['admission_order'][3] = (
            self.note['admission_order'][3], self.note['admission_order'][1])
        self.row('incoming_admission')['admission_order'] = copy.deepcopy(self.note['admission_order'])
        with self.assertRaises(AssertionError):self.check()
        self.note = copy.deepcopy(self.original_note)
        self.review = copy.deepcopy(self.original_review)
        self.reject_facts([
            ('incoming_admission', 'uses_direct_entity', False),
            ('incoming_admission', 'uses_causing_entity_in_prefilters', True),
            ('incoming_admission', 'incoming_amount_rewritten', True),
            ('incoming_admission', 'bypass_skips_earlier_prefilters', True),
            ('incoming_admission', 'concrete_post_hurt_write', True),
            ('poison_dart_admission', 'bypass_overrides_dart_rejection', True),
            ('poison_dart_admission', 'excludes_all_poison_sources', True),
        ])

    def test_block_geometry_gates_not_vanilla_held_shield(self):
        self.reject_facts([
            ('projectile_block_admission', 'uses_native_source_position', False),
            ('projectile_block_admission', 'uses_causing_range', True),
            ('projectile_block_admission', 'renormalizes_after_zero_y', True),
            ('projectile_block_admission', 'reads_arrow_piercing', True),
            ('projectile_block_admission', 'checks_bypasses_shield', True),
            ('projectile_block_admission', 'bypass_overrides_block', True),
            ('projectile_block_admission', 'requires_native_using_item', True),
            ('projectile_block_admission', 'block_tests_awaken', True),
        ])

    def test_arrow_response_keeps_velocity_direction_owner_and_occurrence(self):
        self.reject_facts([
            ('projectile_block_response', 'response_requires_hurt_success', True),
            ('projectile_block_response', 'velocity_rotated_to_new_yaw', True),
            ('projectile_block_response', 'owner_reassigned', True),
            ('projectile_block_response', 'native_deflect_called', True),
            ('projectile_block_response', 'duplicate_projectile_created', True),
            ('projectile_block_response', 'local_server_guard', True),
            ('projectile_block_response', 'block_state_restarts_on_repeat', True),
        ])

    def test_sleep_raw_state_distinct_from_awaken_flag(self):
        self.reject_facts([
            ('sleep_admission', 'sleep_means_raw_state1', True),
            ('sleep_admission', 'set_sleep_changes_awaken', True),
            ('sleep_admission', 'set_sleep_heals', True),
            ('sleep_admission', 'damage_wakes_entity', True),
            ('sleep_admission', 'sleep_bypass_is_unconditional', True),
        ])

    def test_awaken_heal_before_flag_and_native_load_side_effect(self):
        self.reject_facts([
            ('awakened_state', 'heal_before_flag_write', False),
            ('awakened_state', 'heal_only_on_false_to_true_transition', True),
            ('awakened_state', 'flag_write_requires_heal_success', True),
            ('awakened_state', 'setter_sets_raw_state', True),
            ('combat_persistence', 'load_uses_awaken_setter', False),
            ('combat_persistence', 'load_true_requests_heal', False),
            ('combat_persistence', 'load_replays_sleep_state', True),
            ('combat_persistence', 'saved_raw_attack_state', True),
            ('combat_persistence', 'saved_attack_cooldowns', True),
            ('combat_persistence', 'inherited_boss_home_nbt', True),
        ])

    def test_dormant_goal_squared_distance_vertical_motion_and_stop_order(self):
        self.reject_facts([
            ('awakening_prerequisites', 'squared_distance_not_linear_range', False),
            ('awakening_prerequisites', 'preserves_vertical_velocity', False),
            ('awakening_prerequisites', 'stop_checks_target', True),
            ('awakening_prerequisites', 'stop_requires_hurt', True),
            ('awakening_prerequisites', 'stop_heal_before_raw_state', False),
            ('awakening_prerequisites', 'awakening_start_restarts_matching_state', True),
            ('awakening_prerequisites', 'requires_necklace_or_altar', True),
        ])

    def test_absent_boss_bindings_and_native_environment_status(self):
        for name, binding in self.note['concrete_bindings'].items():
            self.assertFalse(binding['applicable'], name)
            self.assertIsNone(binding['native_value'], name)
        self.note['concrete_bindings']['NatureRegen']['native_value'] = 0.0
        with self.assertRaises(AssertionError):self.check()
        self.note = copy.deepcopy(self.original_note)
        self.reject_facts([
            ('shared_defense_applicability', 'boss_defaults_substituted', True),
            ('shared_defense_applicability', 'boss_effect_whitelist_applies', True),
            ('shared_defense_applicability', 'boss_home_return_applies', True),
            ('environment_admission', 'air_returns_native_max', True),
            ('environment_admission', 'blanket_drowning_immunity_claimed', True),
            ('environment_admission', 'all_forced_motion_immunity_claimed', True),
            ('environment_admission', 'inherited_collision_admission', False),
            ('environment_admission', 'factory_fire_immune_call', True),
            ('effect_admission', 'existing_status_contract_reopened', True),
            ('effect_admission', 'all_other_effects_admitted_claimed', True),
            ('native_invulnerability', 'unconditional_fire_immunity_claimed', True),
        ])

    def test_config_setup_not_awaken_heal_and_pyramid_spawn_not_borrowed_gates(self):
        self.reject_facts([
            ('encounter_setup', 'constructor_calls_config_attribute_helper', False),
            ('encounter_setup', 'constructor_calls_heal', True),
            ('encounter_setup', 'constructor_sets_home', True),
            ('encounter_setup', 'constructor_sets_awaken', True),
            ('encounter_setup', 'explicit_armor_toughness_added', True),
            ('pyramid_spawn_prerequisites', 'marker_checks_bounding_box', True),
            ('pyramid_spawn_prerequisites', 'marker_requires_necklace', True),
            ('pyramid_spawn_prerequisites', 'marker_requires_ignis_flag', True),
            ('pyramid_spawn_prerequisites', 'marker_sets_awaken', True),
            ('pyramid_spawn_prerequisites', 'finalize_sets_sleep_before_parent', False),
            ('pyramid_spawn_prerequisites', 'finalize_result_used', True),
            ('pyramid_spawn_prerequisites', 'null_create_clears_marker', True),
            ('pyramid_spawn_prerequisites', 'universal_spawn_gate_claimed', True),
        ])

    def test_void_death_return_changes_raw_state_without_success_gate(self):
        self.reject_facts([
            ('death_state_transition', 'state_write_after_super', False),
            ('death_state_transition', 'state_write_requires_death_success', True),
            ('death_state_transition', 'state_write_requires_hurt_success', True),
            ('death_state_transition', 'source_object_preserved', False),
        ])

    def test_native_boundaries_reject_changed_order_amount_geometry_and_state(self):
        for name, method, offset, field, value in [
            (K, 'hurt', 19, 'branch_target', 119),
            (K, 'hurt', 51, 'operand', -1.5),
            (K, 'hurt', 84, 'operand', 0),
            (K, 'hurt', 121, 'opcode', '0x23'),
            (K, 'canBlockDamageSource', 97, 'opcode', '0x9d'),
            (K, 'isSleep', 11, 'operand', 1),
            (K, 'setAwaken', 1, 'branch_target', 26),
            (K, 'readAdditionalSaveData', 7, 'operand', 'AttackState'),
            (D, 'canUse', 37, 'operand', 16.0),
            (D, 'stop', 12, 'operand', 0),
            (K, 'die', 6, 'operand', 0),
            (REGISTRY, 'lambda$static$81', 14, 'operand', 2.0),
            (PYRAMID, 'handleDataMarker', 483, 'branch_target', 538),
        ]:
            with self.subTest(method=method, offset=offset):
                evidence = read_json(EVIDENCE_FILE)
                w = next(w for w in evidence['witnesses'] if w['entry']==PKG+name+'.class')
                m = next(m for m in w['methods'] if m['name']==method)
                next(i for i in m['instructions'] if i['offset']==offset)[field] = value
                with self.assertRaises(AssertionError):validate_native_boundaries(evidence)

    def test_prior_catalog_cannot_be_reopened(self):
        old = next(e for e in self.review['effects'] if e['review_checkpoint']!=self.note['checkpoint'])
        old['actual_behavior'] = 'reopened completed research'
        with self.assertRaises(AssertionError):validate_preservation(self.review, self.note, self.ledger)

    def test_no_policy_nonfinite_or_premature_completion(self):
        self.row('incoming_admission')['stage_multiplier'] = 2
        with self.assertRaises(AssertionError):self.check()
        self.review = copy.deepcopy(self.original_review)
        self.row('encounter_setup')['components'][0]['numerical_parameters']['max_health'] = float('inf')
        with self.assertRaises(AssertionError):self.check()
        self.review = copy.deepcopy(self.original_review)
        next(t for t in self.ledger['targets'] if t['mod_key']=='cataclysm')['state'] = 'COMPLETE'
        with self.assertRaises(AssertionError):self.check()
        self.reject_facts([('awakened_state', 'offensive_execution_reviewed', True),
                           ('death_state_transition', 'full_offense_death_family_reviewed', True)])


if __name__=='__main__':
    unittest.main()
