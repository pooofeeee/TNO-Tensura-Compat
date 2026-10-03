"""Focused R2k6a static regressions; no runtime or offense review."""
import copy
import json
import unittest

from catalog_common import read_json
from collect_cataclysm_harbinger_admission import EVIDENCE_FILE, SPEC_FILE
from validate_cataclysm_harbinger_admission import (
    LEDGER, NOTE, REVIEW, selected, validate, validate_native_distinctions,
    validate_preservation, validate_records,
)


class HarbingerAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.review, self.note, self.ledger = [read_json(p) for p in [REVIEW, NOTE, LEDGER]]

    def check(self):
        return validate_records(self.review, self.note, self.ledger)

    def row(self, key):
        return next(e for e in selected(self.review) if e['id'] == 'cataclysm:harbinger_' + key)

    def test_scoped_evidence_and_protected_contracts(self):
        result = validate()
        self.assertEqual(result['status'], 'PASS')
        self.assertEqual(result['protected_shared_status_guardian_monstrosity_ignis'], 'BYTE_IDENTICAL')
        self.assertEqual(result['new_mechanics'], 8)
        self.assertEqual(result['new_method_witnesses'], 34)
        self.assertEqual(result['candidate_numeric_parameters'], 3)

    def test_duplicate_mechanic_rejected(self):
        selected(self.review)[1]['id'] = selected(self.review)[0]['id']
        with self.assertRaises(AssertionError):
            self.check()

    def test_invalid_classification_rejected(self):
        selected(self.review)[0]['primary_classification'] = 'INVENTED'
        with self.assertRaises(AssertionError):
            self.check()

    def test_missing_source_or_delivery_rejected(self):
        for field in ['primary_test_source', 'source_actor', 'delivery_paths']:
            with self.subTest(field=field):
                original = copy.deepcopy(self.review)
                selected(self.review)[0][field] = None
                with self.assertRaises(AssertionError):
                    self.check()
                self.review = original

    def test_admission_order_cannot_silently_change(self):
        order = self.note['admission_order']['concrete']
        order[0], order[1] = order[1], order[0]
        with self.assertRaises(AssertionError):
            self.check()

    def test_bypass_tag_does_not_skip_class_and_arrow_gates(self):
        self.row('incoming_admission')['invulnerability_bypass_skips_all_prefilters'] = True
        with self.assertRaises(AssertionError):
            self.check()

    def test_direct_and_causing_actors_cannot_be_swapped(self):
        self.row('incoming_admission')['source_actor_distinctions']['powered_arrow'] = 'getEntity()'
        with self.assertRaises(AssertionError):
            self.check()

    def test_emp_and_timer_prewrites_do_not_require_hurt_success(self):
        for field in ['prewrites_require_hurt_true', 'emp_requires_hurt_true']:
            with self.subTest(field=field):
                original = copy.deepcopy(self.review)
                self.row('incoming_admission')[field] = True
                with self.assertRaises(AssertionError):
                    self.check()
                self.review = original

    def test_power_cannot_become_persisted_or_latched_phase(self):
        for field in ['power_saved', 'power_setter_present', 'derived_not_latched']:
            with self.subTest(field=field):
                original = copy.deepcopy(self.review)
                row = self.row('power_prerequisites')
                row[field] = not row[field]
                with self.assertRaises(AssertionError):
                    self.check()
                self.review = original

    def test_activation_setter_does_not_clear_progress_or_change_hp_home(self):
        for field in ['setter_writes_progress', 'setter_writes_health', 'setter_writes_home']:
            with self.subTest(field=field):
                original = copy.deepcopy(self.review)
                self.row('activation_state')[field] = True
                with self.assertRaises(AssertionError):
                    self.check()
                self.review = original

    def test_mode_cannot_be_equated_with_hp_power(self):
        self.row('mode_state')['mode_cycle_requires_powered'] = True
        with self.assertRaises(AssertionError):
            self.check()

    def test_concrete_bindings_cannot_use_shared_defaults(self):
        for key in ['DamageCap', 'DpsCap', 'RangeLimit', 'NatureRegen']:
            with self.subTest(binding=key):
                original = copy.deepcopy(self.note)
                self.note['concrete_bindings'][key]['installed_value'] = 1000
                with self.assertRaises(AssertionError):
                    self.check()
                self.note = original

    def test_defense_value_cannot_be_promoted_as_candidate(self):
        row = self.row('shared_defense_bindings')
        c = next(c for c in row['components'] if c['primitive'] == 'DAMAGE_CAP')
        row['scalable_parameter_candidates'] = [dict(primitive=c['primitive'], parameters=['per_hit_cap'],
            native_value=22.0, native_formula=c['formula'], units=c['parameter_units']['per_hit_cap'],
            native_boundary=c['native_boundary'])]
        with self.assertRaises(AssertionError):
            self.check()

    def test_healing_calls_keep_independent_primitive_parameter_boundaries(self):
        self.row('native_state_healing')['scalable_parameter_candidates'][0]['primitive'] = 'DAMAGE_CAP'
        with self.assertRaises(AssertionError):
            self.check()

    def test_nonfinite_numeric_observation_rejected(self):
        self.row('power_prerequisites')['components'][0]['numerical_parameters']['health_divisor'] = float('nan')
        with self.assertRaises(AssertionError):
            self.check()

    def test_missing_activation_key_does_not_use_constructor_default(self):
        self.row('encounter_state')['persistence']['missing_is_act_loads'] = True
        with self.assertRaises(AssertionError):
            self.check()

    def test_star_consumption_is_not_conditioned_on_healing(self):
        self.row('encounter_state')['encounter']['consumption_requires_heal_success'] = True
        with self.assertRaises(AssertionError):
            self.check()

    def test_template_state_and_native_source_proofs(self):
        evidence = read_json(EVIDENCE_FILE)
        validate_native_distinctions(evidence)
        template = next(w for w in evidence['witnesses'] if w['entry'].endswith('the_harbinger.nbt'))
        template['entities'][0]['Is_Act'] = 1
        with self.assertRaises(AssertionError):
            validate_native_distinctions(evidence)

    def test_locked_guardian_monstrosity_and_ignis_preserved(self):
        for key in ['guardian_attack_selection', 'monstrosity_incoming_admission', 'ignis_incoming_admission',
                    'ignis_fireball_contact']:
            with self.subTest(mechanic=key):
                original = copy.deepcopy(self.review)
                old = next(e for e in self.review['effects'] if e['id'] == 'cataclysm:' + key)
                old['actual_behavior'] = 'Silently altered protected fact'
                with self.assertRaises(AssertionError):
                    validate_preservation(self.review, self.note, self.ledger)
                self.review = original

    def test_whole_mod_cannot_be_marked_complete(self):
        self.review['status'] = 'COMPLETE'
        with self.assertRaises(AssertionError):
            self.check()

    def test_deterministic_json_format(self):
        for p in [NOTE, SPEC_FILE, EVIDENCE_FILE, REVIEW, LEDGER]:
            with self.subTest(file=p.name):
                self.assertEqual(p.read_bytes(), (json.dumps(read_json(p), indent=2,
                    ensure_ascii=False) + '\n').encode('utf-8'))


if __name__ == '__main__':
    unittest.main()
