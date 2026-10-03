"""Small static regressions for Ignis admission and checkpoint preservation."""
import copy
import json
import unittest

from catalog_common import read_json
from collect_cataclysm_ignis_admission import EVIDENCE_FILE, SPEC_FILE
from validate_cataclysm_ignis_admission import (
    LEDGER, NOTE, REVIEW, selected, validate, validate_preservation, validate_records,
)


class IgnisAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.review, self.note, self.ledger = [read_json(p) for p in [REVIEW, NOTE, LEDGER]]

    def check(self):
        return validate_records(self.review, self.note, self.ledger)

    def row(self, key):
        return next(e for e in selected(self.review) if e['id'] == 'cataclysm:ignis_' + key)

    def test_scoped_evidence_and_protected_contracts(self):
        result = validate()
        self.assertEqual(result['status'], 'PASS')
        self.assertEqual(result['protected_shared_status_guardian_monstrosity'], 'BYTE_IDENTICAL')
        self.assertEqual(result['new_mechanics'], 8)
        self.assertEqual(result['candidate_numeric_parameters'], 1)

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

    def test_invulnerability_bypass_is_not_universal(self):
        self.row('incoming_admission')['invulnerability_bypass_skips_all_prefilters'] = True
        with self.assertRaises(AssertionError):
            self.check()

    def test_prewrites_do_not_require_native_hurt_success(self):
        for key, field in [('counter_admission', 'requires_hurt_success'),
                           ('shield_state', 'durability_increment_requires_hurt_true'),
                           ('incoming_admission', 'terrain_timer_requires_hurt_true')]:
            with self.subTest(mechanic=key):
                original = copy.deepcopy(self.review)
                self.row(key)[field] = True
                with self.assertRaises(AssertionError):
                    self.check()
                self.review = original

    def test_shield_cannot_become_vanilla_item_durability(self):
        self.row('shield_admission')['native_shield_damage_noop'] = False
        with self.assertRaises(AssertionError):
            self.check()

    def test_unlisted_shield_windows_retain_native_state(self):
        self.row('shield_state')['shield_windows']['OTHER_ANIMATION'] = False
        with self.assertRaises(AssertionError):
            self.check()

    def test_phase_precedence_and_setter_are_preserved(self):
        self.row('phase_prerequisites')['selection_order'] = ['PHASE_2', 'SHIELD_BREAK', 'PHASE_3']
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
        row = self.row('incoming_admission')
        c = next(c for c in row['components'] if c['primitive'] == 'INCOMING_DAMAGE_MULTIPLIER')
        row['scalable_parameter_candidates'] = [dict(primitive=c['primitive'], parameters=['phase_multiplier'],
            native_value=0.5, native_formula=c['formula'], units='dimensionless incoming request multiplier',
            native_boundary=c['native_boundary'])]
        with self.assertRaises(AssertionError):
            self.check()

    def test_heal_binding_keeps_its_native_primitive(self):
        self.row('nature_regen_binding')['scalable_parameter_candidates'][0]['primitive'] = 'DAMAGE_CAP'
        with self.assertRaises(AssertionError):
            self.check()

    def test_persistence_load_order_is_not_normalized(self):
        self.row('encounter_state')['persistence']['load_order'].reverse()
        with self.assertRaises(AssertionError):
            self.check()

    def test_failed_spawn_does_not_consume_altar_item(self):
        self.row('encounter_state')['encounter']['item_consumption_requires_add_success'] = False
        with self.assertRaises(AssertionError):
            self.check()

    def test_locked_guardian_and_monstrosity_records_preserved(self):
        for key in ['guardian_attack_selection', 'monstrosity_incoming_admission', 'monstrosity_smash']:
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

    def test_deterministic_json_formatting(self):
        for path in [REVIEW, NOTE, LEDGER, EVIDENCE_FILE, SPEC_FILE]:
            with self.subTest(file=path.name):
                encoded = (json.dumps(read_json(path), ensure_ascii=False, indent=2) + '\n').encode('utf-8')
                self.assertEqual(path.read_bytes(), encoded)


if __name__ == '__main__':
    unittest.main()
