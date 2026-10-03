"""Bounded R2k5b archive regressions; no runtime or Stage policy tests."""
import copy
import json
import unittest

from catalog_common import OUT, read_json
from collect_cataclysm_ignis_offense import EVIDENCE_FILE, I, PKG, SPEC_FILE
from validate_cataclysm_ignis_offense import (
    LEDGER, NOTE, REVIEW, selected, validate, validate_preservation, validate_records,
)


class IgnisOffenseTests(unittest.TestCase):
    def setUp(self):
        self.review, self.note, self.ledger = [read_json(p) for p in [REVIEW, NOTE, LEDGER]]

    def check(self):
        return validate_records(self.review, self.note, self.ledger)

    def row(self, key):
        return next(e for e in selected(self.review) if e['id'] == 'cataclysm:ignis_' + key)

    def test_scoped_archive_and_protected_checkpoints(self):
        result = validate()
        self.assertEqual(result['status'], 'PASS')
        self.assertEqual(result['new_mechanics'], 22)
        self.assertEqual(result['candidate_numeric_parameters'], 344)
        self.assertEqual(result['new_method_witnesses'], 162)
        self.assertEqual(result['protected_ignis_admission_shared_status_guardian_monstrosity'], 'BYTE_IDENTICAL')

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

    def test_native_primitive_cannot_be_flattened(self):
        c = next(c for c in self.row('body_check')['scalable_parameter_candidates'] if c['primitive'] == 'STUN')
        c['primitive'] = 'NATIVE_DAMAGE_REQUEST'
        with self.assertRaises(AssertionError):
            self.check()

    def test_nonfinite_native_value_rejected(self):
        self.row('poke_capture')['components'][0]['numerical_parameters']['hp_fraction'] = float('inf')
        with self.assertRaises(AssertionError):
            self.check()

    def test_native_payload_links_are_not_invented(self):
        self.note['payload_entities'][0]['source_mechanic_ids'] = ['cataclysm:ignis_alliance']
        with self.assertRaises((AssertionError, KeyError)):
            self.check()

    def test_critical_return_dependencies_cannot_change(self):
        for key, field, value in [
            ('poke_capture', 'animation_requires_mount_success', True),
            ('held_victim', 'release_returns_early', True),
            ('area_melee', 'heal_requires_effect_add_success', True),
            ('fireball_contact', 'explosion_requires_hurt_true', True),
            ('abyss_fireball_contact', 'brand_requires_explosion_hurt_true', True),
            ('native_explosion', 'damage_return_controls_motion', True),
            ('native_explosion', 'calculator_should_damage_controls_motion', True),
            ('shield_break_burst', 'status_requires_hurt_true', True),
        ]:
            with self.subTest(mechanic=key, field=field):
                original = copy.deepcopy(self.review)
                self.row(key)[field] = value
                with self.assertRaises(AssertionError):
                    self.check()
                self.review = original

    def test_reflection_keeps_causing_actor_and_bounce_state(self):
        self.row('abyss_fireball_motion')['reflection_reads'] = 'DIRECT_ENTITY'
        with self.assertRaises(AssertionError):
            self.check()

    def test_terminal_flame_explosion_does_not_invent_owner_resolution(self):
        self.row('flame_strike_payload')['terminal_calls_getOwner'] = True
        with self.assertRaises(AssertionError):
            self.check()

    def test_keep_does_not_erase_native_fire_placement(self):
        self.row('native_explosion')['keep_prevents_fire'] = True
        with self.assertRaises(AssertionError):
            self.check()

    def test_native_ally_distinctions_are_preserved(self):
        self.row('area_melee')['has_ally_check'] = True
        with self.assertRaises(AssertionError):
            self.check()

    def test_debris_cannot_acquire_a_damage_payload(self):
        self.row('ground_wave')['debris_adds_damage'] = True
        with self.assertRaises(AssertionError):
            self.check()

    def test_profiles_cover_exact_archived_native_call_sites(self):
        data = read_json(OUT / 'native-evidence/cataclysm-stun.json')
        w = next(w for w in data['witnesses'] if w['entry'] == PKG + I + '.class')
        ins = next(m['instructions'] for m in w['methods'] if m['name'] == 'aiStep')
        for key, method in [('area_melee', '.AreaAttack('), ('ground_wave', '.ShieldSmashDamage(')]:
            native_calls = [i for i in ins if method in str(i.get('operand', ''))]
            self.assertEqual(len(self.row(key)['attack_profiles']), len(native_calls))
        profile = next(p for p in self.row('area_melee')['attack_profiles'] if p['animation'] == 'SWING_ATTACK')
        self.assertEqual(profile['tick'], 24)
        self.assertEqual(profile['arguments']['damage_multiplier'], 1.0)
        self.assertEqual(profile['arguments']['hp_fraction'], 0.05)
        phase = self.row('phase_wave')['damage_ticks']
        self.assertEqual(phase['PHASE_2'], [30, 32, 34, 36, 38])
        self.assertEqual(phase['PHASE_3'], [60, 62, 64, 66])

    def test_locked_admission_guardian_monstrosity_facts_unchanged(self):
        for key in ['ignis_shield_admission', 'guardian_attack_selection', 'monstrosity_incoming_admission']:
            with self.subTest(mechanic=key):
                original = copy.deepcopy(self.review)
                e = next(e for e in self.review['effects'] if e['id'] == 'cataclysm:' + key)
                e['actual_behavior'] = 'Silently changed protected facts'
                with self.assertRaises(AssertionError):
                    validate_preservation(self.review, self.note, self.ledger)
                self.review = original

    def test_whole_mod_cannot_be_marked_complete(self):
        self.ledger['status'] = 'COMPLETE'
        with self.assertRaises(AssertionError):
            self.check()

    def test_deterministic_json_format(self):
        for path in [REVIEW, NOTE, LEDGER, EVIDENCE_FILE, SPEC_FILE]:
            with self.subTest(file=path.name):
                self.assertEqual(path.read_bytes(), (json.dumps(read_json(path), ensure_ascii=False, indent=2) + '\n').encode('utf-8'))


if __name__ == '__main__':
    unittest.main()
