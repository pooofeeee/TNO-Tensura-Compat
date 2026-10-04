"""Bounded regressions for the R2k11b static research checkpoint."""
import copy
import unittest

from catalog_common import read_json
from collect_cataclysm_ender_golem_offense import EVIDENCE_FILE, G, PKG
from validate_cataclysm_ender_golem_offense import (
    LEDGER, NOTE, REVIEW, selected, validate, validate_contracts,
    validate_native_boundaries, validate_preservation, validate_records,
)


class EnderGolemOffenseTests(unittest.TestCase):
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
        return next(e for e in selected(self.review) if e['id']=='cataclysm:ender_golem_'+key)

    def check(self):
        return validate_records(self.review, self.note, self.ledger)

    def reject_facts(self, changes):
        for key, field, value in changes:
            with self.subTest(mechanic=key, field=field):
                rows = copy.deepcopy({e['id'].removeprefix('cataclysm:ender_golem_'): e for e in selected(self.review)})
                rows[key][field] = value
                with self.assertRaises(AssertionError):
                    validate_contracts(rows)

    def test_checkpoint_evidence_formatting_and_protected_families(self):
        result = validate()
        self.assertEqual(result['status'], 'PASS')
        self.assertEqual(result['new_mechanics'], 16)
        self.assertEqual(result['candidate_numeric_parameters'], 27)
        self.assertEqual(result['new_method_witnesses'], 27)
        self.assertEqual(result['protected_shared_status_prior_families_r2k11a'], 'BYTE_IDENTICAL')

    def test_unique_ids_and_existing_classifications(self):
        selected(self.review)[1]['id'] = selected(self.review)[0]['id']
        with self.assertRaises(AssertionError):
            self.check()
        self.review = copy.deepcopy(self.original_review)
        self.row('quake_damage')['primary_classification'] = 'INVENTED'
        with self.assertRaises(AssertionError):
            self.check()

    def test_source_delivery_and_return_contract_required(self):
        for f in ['source_actor','delivery_paths','hurt_return_dependency','primary_test_source']:
            with self.subTest(field=f):
                self.review = copy.deepcopy(self.original_review)
                self.row('rune_damage')[f] = None
                with self.assertRaises(AssertionError):
                    self.check()

    def test_candidate_primitive_value_formula_units_and_boundary(self):
        for f,v in [('primitive','KNOCKBACK'),('native_value',9.0),('native_formula','invented'),
                    ('units','unknown'),('native_boundary','invented hook')]:
            with self.subTest(field=f):
                self.review = copy.deepcopy(self.original_review)
                self.row('rune_damage')['scalable_parameter_candidates'][0][f] = v
                with self.assertRaises(AssertionError):
                    self.check()

    def test_dynamic_damage_not_invented_as_fixed_coefficient(self):
        for key in ['melee_damage','quake_damage']:
            with self.subTest(mechanic=key):
                self.review = copy.deepcopy(self.original_review)
                c = next(c for c in self.row(key)['scalable_parameter_candidates'] if c['parameters']==['requested_damage'])
                self.assertIsNone(c['native_value'])
                c['native_value'] = 1.0
                with self.assertRaises(AssertionError):
                    self.check()

    def test_state_and_binary_controls_are_not_automatic_candidates(self):
        for key in ['attack_selection','sequence_state','rune_lifecycle','terrain_response','dormant_control']:
            with self.subTest(mechanic=key):
                self.review = copy.deepcopy(self.original_review)
                self.row(key)['scalable_parameter_candidates'] = copy.deepcopy(self.row('rune_damage')['scalable_parameter_candidates'])
                with self.assertRaises(AssertionError):
                    self.check()

    def test_movement_and_damage_return_distinctions(self):
        self.reject_facts([
            ('pursuit_goal','pursuit_calls_native_hurt',True),
            ('melee_knockback','control_depends_on_hurt',True),
            ('quake_damage','launch_depends_on_hurt',True),
            ('quake_launch','uses_native_knockback',True),
            ('quake_launch','reads_knockback_resistance',True),
            ('attack_control','preserves_vertical_velocity',False),
            ('terrain_response','terrain_depends_on_hurt',True),
            ('terrain_response','spawns_damaging_debris',True),
            ('body_repulsion','local_team_guard',True),
        ])

    def test_selection_cooldown_and_original_native_rotations(self):
        self.reject_facts([
            ('attack_selection','rune_ground_gate_applies_to_fallback',True),
            ('attack_selection','selection_local_server_guard',True),
            ('sequence_state','selected_cooldown_end_of_tick',250),
            ('rune_delivery','ring_rotation_argument','placement angle'),
            ('rune_delivery','gaussian_rotation_argument','aim angle'),
            ('rune_delivery','guaranteed_spawn_count',True),
            ('rune_delivery','creates_evoker_fangs',True),
        ])

    def test_reused_rune_owner_lifecycle_and_bounded_death_claim(self):
        self.reject_facts([
            ('rune_damage','stored_damage_at_creation',False),
            ('rune_damage','anonymous_magic_fallback',False),
            ('rune_lifecycle','native_damage_saved',False),
            ('rune_lifecycle','native_life_ticks_saved',True),
            ('rune_lifecycle','new_owned_payload_class',True),
            ('defeat_lifecycle','concrete_respawner_link',True),
            ('defeat_lifecycle','global_death_callbacks_absent_claimed',True),
        ])

    def test_native_hurt_return_discard_cannot_be_changed(self):
        evidence = read_json(EVIDENCE_FILE)
        w = next(w for w in evidence['witnesses'] if w['entry']==PKG+G+'.class')
        q = next(m for m in w['methods'] if m['name']=='EarthQuake')
        next(i for i in q['instructions'] if i['offset']==147)['opcode'] = '0x99'
        with self.assertRaises(AssertionError):
            validate_native_boundaries(evidence)

    def test_native_rune_rotation_alias_cannot_be_repaired(self):
        evidence = read_json(EVIDENCE_FILE)
        w = next(w for w in evidence['witnesses'] if w['entry']==PKG+G+'.class')
        m = next(m for m in w['methods'] if m['name']=='VoidRuneAttack')
        next(i for i in m['instructions'] if i['offset']==287)['local_index'] = 6
        with self.assertRaises(AssertionError):
            validate_native_boundaries(evidence)

    def test_protected_catalog_record_cannot_be_reopened(self):
        e = next(e for e in self.review['effects'] if e['review_checkpoint']!=self.note['checkpoint'])
        e['actual_behavior'] = 'reopened completed research'
        with self.assertRaises(AssertionError):
            validate_preservation(self.review,self.note,self.ledger)

    def test_no_policy_nonfinite_or_premature_completion(self):
        self.row('rune_damage')['stage_multiplier'] = 2
        with self.assertRaises(AssertionError):
            self.check()
        self.review = copy.deepcopy(self.original_review)
        self.row('quake_launch')['components'][0]['numerical_parameters']['vertical_increment'] = float('inf')
        with self.assertRaises(AssertionError):
            self.check()
        self.review = copy.deepcopy(self.original_review)
        next(t for t in self.ledger['targets'] if t['mod_key']=='cataclysm')['state'] = 'COMPLETE'
        with self.assertRaises(AssertionError):
            self.check()


if __name__ == '__main__':
    unittest.main()
