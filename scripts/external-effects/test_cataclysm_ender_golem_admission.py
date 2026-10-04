"""Focused regressions for bounded R2k11a Ender Golem static research."""
import copy
import unittest

from catalog_common import read_json
from collect_cataclysm_ender_golem_admission import EVIDENCE_FILE, G, PKG
from validate_cataclysm_ender_golem_admission import (
    LEDGER, MAX_FLOAT, NOTE, REVIEW, selected, validate, validate_contracts,
    validate_native_boundaries, validate_preservation, validate_records,
)


class EnderGolemAdmissionTests(unittest.TestCase):
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
        return next(e for e in selected(self.review) if e['id'] == 'cataclysm:ender_golem_' + key)

    def check(self):
        return validate_records(self.review, self.note, self.ledger)

    def reject_facts(self, changes):
        for key, field, value in changes:
            with self.subTest(mechanic=key, field=field):
                rows = copy.deepcopy({e['id'].removeprefix('cataclysm:ender_golem_'): e for e in selected(self.review)})
                rows[key][field] = value
                with self.assertRaises(AssertionError):
                    validate_contracts(rows, self.note)

    def test_bounded_archive_and_protected_contracts(self):
        result = validate()
        self.assertEqual(result['status'], 'PASS')
        self.assertEqual(result['new_mechanics'], 8)
        self.assertEqual(result['delivery_paths'], 8)
        self.assertEqual(result['candidate_numeric_parameters'], 1)
        self.assertEqual(result['new_method_witnesses'], 16)
        self.assertEqual(result['protected_shared_status_prior_bosses_scylla'], 'BYTE_IDENTICAL')

    def test_duplicate_mechanic_and_invalid_classification_rejected(self):
        selected(self.review)[1]['id'] = selected(self.review)[0]['id']
        with self.assertRaises(AssertionError):
            self.check()
        self.review = copy.deepcopy(self.original_review)
        self.row('incoming_admission')['primary_classification'] = 'INVENTED'
        with self.assertRaises(AssertionError):
            self.check()

    def test_source_delivery_and_native_return_required(self):
        for field in ['source_actor', 'delivery_paths', 'hurt_return_dependency', 'primary_test_source']:
            with self.subTest(field=field):
                self.review = copy.deepcopy(self.original_review)
                self.row('incoming_admission')[field] = None
                with self.assertRaises(AssertionError):
                    self.check()

    def test_exact_candidate_primitive_value_formula_units_and_boundary(self):
        for field, value in [('primitive', 'INCOMING_DAMAGE_MULTIPLIER'), ('native_value', 25),
                             ('native_formula', 'shared NatureRegen'), ('units', 'unknown'),
                             ('native_boundary', 'invented hook')]:
            with self.subTest(field=field):
                self.review = copy.deepcopy(self.original_review)
                self.row('dormant_healing')['scalable_parameter_candidates'][0][field] = value
                with self.assertRaises(AssertionError):
                    self.check()

    def test_nonfinite_observation_and_stage_policy_rejected(self):
        self.row('dormant_healing')['components'][0]['numerical_parameters']['amount'] = float('inf')
        with self.assertRaises(AssertionError):
            self.check()
        self.review = copy.deepcopy(self.original_review)
        self.row('dormant_healing')['stage_multiplier'] = 2
        with self.assertRaises(AssertionError):
            self.check()

    def test_native_defense_and_state_constants_are_not_promoted(self):
        self.row('shared_defense_bindings')['scalable_parameter_candidates'] = copy.deepcopy(
            self.row('dormant_healing')['scalable_parameter_candidates'])
        with self.assertRaises(AssertionError):
            self.check()
        self.reject_facts([('awake_state_prerequisites', 'raw_state_is_tno_stage', True)])

    def test_incoming_order_and_two_factors_remain_distinct(self):
        self.row('incoming_admission')['admission_order'][0:2] = reversed(
            self.row('incoming_admission')['admission_order'][0:2])
        with self.assertRaises(AssertionError):
            self.check()
        self.review = copy.deepcopy(self.original_review)
        self.row('incoming_admission')['components'][0]['numerical_parameters']['state_multiplier'] = .25
        with self.assertRaises(AssertionError):
            self.check()
        self.reject_facts([
            ('incoming_admission', 'bypass_skips_state_reduction', True),
            ('incoming_admission', 'bypass_skips_direct_golem_reduction', True),
            ('incoming_admission', 'magic_exemption_is_exact_type', False),
            ('incoming_admission', 'calculate_range_local_unused', False),
            ('incoming_admission', 'awakens_on_hurt_return', True),
        ])

    def test_unused_config_cannot_replace_inherited_bindings(self):
        bindings = self.note['concrete_bindings']
        self.assertEqual(bindings['DamageCap']['native_value'], MAX_FLOAT)
        self.assertEqual(bindings['DpsCap']['native_value'], MAX_FLOAT)
        self.assertEqual(bindings['NatureRegen']['native_value'], 0.0)
        bindings['NatureRegen']['native_value'] = 25.0
        with self.assertRaises(AssertionError):
            self.check()
        self.reject_facts([
            ('shared_defense_bindings', 'installed_cap_config_consumed', True),
            ('shared_defense_bindings', 'installed_dps_time_config_consumed', True),
            ('shared_defense_bindings', 'installed_nature_heal_config_consumed', True),
            ('shared_defense_bindings', 'dps_is_bucket_capacity', True),
        ])

    def test_dormant_heal_does_not_acquire_shared_regen_gates(self):
        self.reject_facts([
            ('dormant_healing', 'heal_has_local_server_guard', True),
            ('dormant_healing', 'heal_has_local_no_ai_guard', True),
            ('dormant_healing', 'heal_has_target_null_guard', True),
            ('dormant_healing', 'heal_reads_self_regen', True),
            ('dormant_healing', 'heal_reads_nature_heal_config', True),
            ('dormant_healing', 'heal_runs_before_target_wake', False),
        ])

    def test_native_awake_timeout_setter_and_persistence(self):
        self.reject_facts([
            ('awake_state_prerequisites', 'targetless_timeout_strict_greater', False),
            ('awake_state_prerequisites', 'setter_resets_progress', True),
            ('awake_state_prerequisites', 'target_wake_requires_alive', True),
            ('combat_persistence', 'saved_deactivation_progress', True),
            ('combat_persistence', 'saved_targetless_ticks', True),
            ('combat_persistence', 'inherited_ia_life', True),
            ('combat_persistence', 'generic_persistence_added', True),
        ])

    def test_environment_constructor_and_spawn_contracts(self):
        self.reject_facts([
            ('environment_admission', 'registered_fire_immune', False),
            ('environment_admission', 'air_returns_native_max', True),
            ('environment_admission', 'blanket_drowning_immunity_claimed', True),
            ('encounter_setup', 'constructor_health_is_heal_delivery', True),
            ('encounter_setup', 'constructor_sets_home', True),
            ('citadel_spawn_prerequisites', 'marker_is_exact_match', False),
            ('citadel_spawn_prerequisites', 'marker_calls_finalize_spawn', True),
            ('citadel_spawn_prerequisites', 'marker_sets_home', True),
            ('citadel_spawn_prerequisites', 'spawn_return_consumed', True),
        ])

    def test_native_bypass_branch_cannot_be_reversed(self):
        evidence = read_json(EVIDENCE_FILE)
        root = next(w for w in evidence['witnesses'] if w['entry'] == PKG + G + '.class')
        hurt = next(m for m in root['methods'] if m['name'] == 'hurt')
        next(i for i in hurt['instructions'] if i['offset'] == 24)['branch_target'] = 45
        with self.assertRaises(AssertionError):
            validate_native_boundaries(evidence)

    def test_direct_actor_check_cannot_be_replaced_by_causing_actor(self):
        evidence = read_json(EVIDENCE_FILE)
        root = next(w for w in evidence['witnesses'] if w['entry'] == PKG + G + '.class')
        hurt = next(m for m in root['methods'] if m['name'] == 'hurt')
        i = next(i for i in hurt['instructions'] if i['offset'] == 52)
        i['operand'] = i['operand'].replace('getDirectEntity', 'getEntity')
        with self.assertRaises(AssertionError):
            validate_native_boundaries(evidence)

    def test_prior_catalog_cannot_be_silently_changed(self):
        old = next(e for e in self.review['effects'] if e['review_checkpoint'] != self.note['checkpoint'])
        old['actual_behavior'] = 'reopened protected research'
        with self.assertRaises(AssertionError):
            validate_preservation(self.review, self.note, self.ledger)

    def test_cataclysm_cannot_be_completed_or_offense_claimed(self):
        cat = next(t for t in self.ledger['targets'] if t['mod_key'] == 'cataclysm')
        cat['state'] = 'COMPLETE'
        with self.assertRaises(AssertionError):
            self.check()
        self.reject_facts([('awake_state_prerequisites', 'offensive_dispatch_reviewed', True)])


if __name__ == '__main__':
    unittest.main()
