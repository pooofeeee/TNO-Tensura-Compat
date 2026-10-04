"""Focused regressions for bounded R2k13a Ignited Berserker static research."""
import copy
import unittest

from catalog_common import read_json
from collect_cataclysm_ignited_berserker_admission import B, EVIDENCE_FILE, PKG, REGISTRY
from validate_cataclysm_ignited_berserker_admission import (
    LEDGER, NOTE, REVIEW, selected, validate, validate_contracts,
    validate_native_boundaries, validate_preservation, validate_records,
)


class IgnitedBerserkerAdmissionTests(unittest.TestCase):
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
        return next(e for e in selected(self.review) if e['id']=='cataclysm:ignited_berserker_'+key)

    def check(self):
        return validate_records(self.review, self.note, self.ledger)

    def reject_facts(self, changes):
        for key, field, value in changes:
            with self.subTest(mechanic=key, field=field):
                rows = copy.deepcopy({e['id'].removeprefix('cataclysm:ignited_berserker_'):e
                                      for e in selected(self.review)})
                rows[key][field] = value
                with self.assertRaises(AssertionError):
                    validate_contracts(rows, self.note)

    def test_checkpoint_evidence_formatting_and_protected_families(self):
        result = validate()
        self.assertEqual(result['status'], 'PASS')
        self.assertEqual(result['new_mechanics'], 9)
        self.assertEqual(result['candidate_numeric_parameters'], 0)
        self.assertEqual(result['new_method_witnesses'], 15)
        self.assertEqual(result['protected_shared_status_prior_families_revenant'], 'BYTE_IDENTICAL')

    def test_unique_ids_classifications_and_source_delivery(self):
        selected(self.review)[1]['id'] = selected(self.review)[0]['id']
        with self.assertRaises(AssertionError):
            self.check()
        for field, value in [('primary_classification', 'INVENTED'), ('source_actor', None),
                             ('delivery_paths', None), ('hurt_return_dependency', None)]:
            with self.subTest(field=field):
                self.review = copy.deepcopy(self.original_review)
                self.row('incoming_admission')[field] = value
                with self.assertRaises(AssertionError):
                    self.check()

    def test_state_defense_setup_and_roll_numbers_not_automatic_candidates(self):
        for key in ['combat_state_prerequisites', 'shared_defense_applicability',
                    'encounter_setup', 'spawn_prerequisites', 'death_state_reset']:
            with self.subTest(mechanic=key):
                self.review = copy.deepcopy(self.original_review)
                self.row(key)['scalable_parameter_candidates'] = [dict(primitive='INVENTED', parameter='value')]
                with self.assertRaises(AssertionError):
                    self.check()

    def test_native_admission_order_and_actor_identity(self):
        self.note['admission_order'][1], self.note['admission_order'][2] = (
            self.note['admission_order'][2], self.note['admission_order'][1])
        self.row('incoming_admission')['admission_order'] = copy.deepcopy(self.note['admission_order'])
        with self.assertRaises(AssertionError):
            self.check()
        self.note = copy.deepcopy(self.original_note)
        self.review = copy.deepcopy(self.original_review)
        self.reject_facts([
            ('incoming_admission', 'incoming_amount_rewritten', True),
            ('incoming_admission', 'concrete_direct_entity_read', True),
            ('incoming_admission', 'concrete_causing_entity_read', True),
            ('incoming_admission', 'concrete_post_hurt_callback', True),
            ('native_invulnerability', 'unconditional_bypass_claimed', True),
        ])

    def test_absent_boss_bindings_cannot_be_replaced_with_boss_defaults(self):
        for name, binding in self.note['concrete_bindings'].items():
            self.assertFalse(binding['applicable'], name)
            self.assertIsNone(binding['native_value'], name)
        self.note['concrete_bindings']['NatureRegen']['native_value'] = 0.0
        with self.assertRaises(AssertionError):
            self.check()
        self.note = copy.deepcopy(self.original_note)
        self.reject_facts([
            ('incoming_admission', 'shared_boss_hurt_reached', True),
            ('shared_defense_applicability', 'boss_defaults_substituted', True),
            ('shared_defense_applicability', 'boss_effect_whitelist_applies', True),
            ('shared_defense_applicability', 'boss_home_return_applies', True),
            ('shared_defense_applicability', 'positive_regen_delivery', True),
        ])

    def test_environment_admission_not_blanket_damage_or_motion_immunity(self):
        self.reject_facts([
            ('environment_admission', 'air_returns_native_max', True),
            ('environment_admission', 'blanket_drowning_immunity_claimed', True),
            ('environment_admission', 'all_forced_motion_immunity_claimed', True),
            ('environment_admission', 'can_ride', True),
            ('native_invulnerability', 'unconditional_fall_immunity_claimed', True),
        ])

    def test_raw_state_and_parent_only_persistence(self):
        self.reject_facts([
            ('combat_state_prerequisites', 'raw_state_is_stage', True),
            ('combat_state_prerequisites', 'state_setter_clamps', True),
            ('combat_state_prerequisites', 'state_setter_heals', True),
            ('combat_state_prerequisites', 'concrete_incoming_state_gate', True),
            ('combat_persistence', 'saved_attack_state', True),
            ('combat_persistence', 'saved_local_attack_cooldowns', True),
            ('combat_persistence', 'inherited_boss_home_nbt', True),
            ('combat_persistence', 'inherited_ia_boss_life', True),
        ])

    def test_instance_world_flag_and_placement_are_distinct(self):
        self.reject_facts([
            ('spawn_prerequisites', 'spawner_bypasses_world_flag', True),
            ('spawn_prerequisites', 'roll_argument_one_has_random_exclusion', True),
            ('spawn_prerequisites', 'non_spawner_roll_consumes_rng', False),
            ('spawn_prerequisites', 'requires_spawn_dimension_nether', True),
            ('spawn_prerequisites', 'world_lookup_has_overworld_fallback', False),
            ('spawn_prerequisites', 'constructor_runs_instance_spawn_rules', True),
            ('spawn_prerequisites', 'universal_spawn_gate_claimed', True),
            ('spawn_prerequisites', 'placement_is_any_light', False),
        ])

    def test_factory_attributes_not_borrowed_config_or_healing(self):
        self.reject_facts([
            ('encounter_setup', 'constructor_calls_config_attribute_helper', True),
            ('encounter_setup', 'installed_combat_config_present', True),
            ('encounter_setup', 'constructor_is_heal_delivery', True),
            ('encounter_setup', 'constructor_sets_home', True),
            ('encounter_setup', 'explicit_armor_toughness_added', True),
        ])

    def test_void_death_return_resets_state_even_on_native_cancellation(self):
        self.reject_facts([
            ('death_state_reset', 'reset_after_super_die', False),
            ('death_state_reset', 'reset_requires_death_success', True),
            ('death_state_reset', 'reset_requires_hurt_success', True),
            ('death_state_reset', 'source_object_preserved', False),
        ])

    def test_new_native_spawn_and_death_boundaries_reject_changed_evidence(self):
        for name, method, offset, field, value in [
            (B, 'checkSpawnRules', 13, 'operand', 'net/minecraft/server/level/ServerLevelAccessor'),
            (B, 'checkSpawnRules', 35, 'branch_target', 52),
            (B, 'die', 6, 'operand', 1),
            (REGISTRY, 'rollSpawn', 7, 'operand', 0),
            (REGISTRY, 'lambda$static$23', 12, 'operand', 2.0),
        ]:
            with self.subTest(method=method, offset=offset):
                evidence = read_json(EVIDENCE_FILE)
                w = next(w for w in evidence['witnesses'] if w['entry']==PKG+name+'.class')
                m = next(m for m in w['methods'] if m['name']==method)
                next(i for i in m['instructions'] if i['offset']==offset)[field] = value
                with self.assertRaises(AssertionError):
                    validate_native_boundaries(evidence)

    def test_prior_catalog_cannot_be_reopened(self):
        old = next(e for e in self.review['effects'] if e['review_checkpoint']!=self.note['checkpoint'])
        old['actual_behavior'] = 'reopened completed research'
        with self.assertRaises(AssertionError):
            validate_preservation(self.review, self.note, self.ledger)

    def test_no_policy_nonfinite_or_premature_completion(self):
        self.row('incoming_admission')['stage_multiplier'] = 2
        with self.assertRaises(AssertionError):
            self.check()
        self.review = copy.deepcopy(self.original_review)
        self.row('encounter_setup')['components'][0]['numerical_parameters']['max_health'] = float('inf')
        with self.assertRaises(AssertionError):
            self.check()
        self.review = copy.deepcopy(self.original_review)
        next(t for t in self.ledger['targets'] if t['mod_key']=='cataclysm')['state'] = 'COMPLETE'
        with self.assertRaises(AssertionError):
            self.check()
        self.reject_facts([('combat_state_prerequisites', 'offensive_execution_reviewed', True),
                           ('death_state_reset', 'full_offense_death_family_reviewed', True)])


if __name__=='__main__':
    unittest.main()
