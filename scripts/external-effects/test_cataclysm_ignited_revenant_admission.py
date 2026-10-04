"""Focused regressions for bounded R2k12a Ignited Revenant static research."""
import copy
import unittest

from catalog_common import read_json
from collect_cataclysm_ignited_revenant_admission import EVIDENCE_FILE, PKG, R
from validate_cataclysm_ignited_revenant_admission import (
    LEDGER, MAX_DOUBLE, MAX_FLOAT, NOTE, REVIEW, selected, validate,
    validate_contracts, validate_native_boundaries, validate_preservation, validate_records,
)


class IgnitedRevenantAdmissionTests(unittest.TestCase):
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
        return next(e for e in selected(self.review) if e['id']=='cataclysm:ignited_revenant_'+key)

    def check(self):
        return validate_records(self.review,self.note,self.ledger)

    def reject_facts(self, changes):
        for key,field,value in changes:
            with self.subTest(mechanic=key,field=field):
                rows = copy.deepcopy({e['id'].removeprefix('cataclysm:ignited_revenant_'):e for e in selected(self.review)})
                rows[key][field] = value
                with self.assertRaises(AssertionError):
                    validate_contracts(rows,self.note)

    def test_checkpoint_formatting_evidence_and_protected_families(self):
        result = validate()
        self.assertEqual(result['status'],'PASS')
        self.assertEqual(result['new_mechanics'],10)
        self.assertEqual(result['candidate_numeric_parameters'],1)
        self.assertEqual(result['new_method_witnesses'],25)
        self.assertEqual(result['protected_shared_status_prior_families_ender_golem'],'BYTE_IDENTICAL')

    def test_unique_ids_classifications_and_source_delivery(self):
        selected(self.review)[1]['id'] = selected(self.review)[0]['id']
        with self.assertRaises(AssertionError):
            self.check()
        for field,value in [('primary_classification','INVENTED'),('source_actor',None),
                            ('delivery_paths',None),('hurt_return_dependency',None)]:
            with self.subTest(field=field):
                self.review = copy.deepcopy(self.original_review)
                self.row('incoming_admission')[field] = value
                with self.assertRaises(AssertionError):
                    self.check()

    def test_fall_candidate_exact_primitive_value_formula_units_and_boundary(self):
        for field,value in [('primitive','SHIELD_STATE'),('native_value',1.0),('native_formula','Slow Falling effect'),
                            ('units','unknown'),('native_boundary','invented hook')]:
            with self.subTest(field=field):
                self.review = copy.deepcopy(self.original_review)
                self.row('falling_motion')['scalable_parameter_candidates'][0][field] = value
                with self.assertRaises(AssertionError):
                    self.check()

    def test_defensive_and_state_numbers_not_automatic_candidates(self):
        for key in ['shield_break_admission','shield_block_admission','shared_defense_bindings',
                    'combat_state_prerequisites','encounter_setup']:
            with self.subTest(mechanic=key):
                self.review = copy.deepcopy(self.original_review)
                self.row(key)['scalable_parameter_candidates'] = copy.deepcopy(self.row('falling_motion')['scalable_parameter_candidates'])
                with self.assertRaises(AssertionError):
                    self.check()

    def test_concrete_order_and_axe_pre_admission_return(self):
        order = self.row('incoming_admission')['admission_order']
        order[1],order[2] = order[2],order[1]
        with self.assertRaises(AssertionError):
            self.check()
        self.reject_facts([
            ('incoming_admission','bypass_skips_concrete_prefilters',True),
            ('incoming_admission','incoming_amount_rewritten',True),
            ('shield_break_admission','uses_causing_owner',True),
            ('shield_break_admission','uses_attribute_base',False),
            ('shield_break_admission','checks_bypasses_shield',True),
            ('shield_break_admission','shield_break_depends_on_hurt',True),
            ('shield_break_admission','fourth_break_spills_damage',True),
        ])

    def test_shield_direction_arrow_tag_and_callback_distinctions(self):
        self.reject_facts([
            ('shield_block_admission','block_uses_causing_range',True),
            ('shield_block_admission','direct_piercing_arrow_bypasses',False),
            ('shield_block_admission','renormalizes_horizontal_vector',True),
            ('shield_block_admission','native_using_item_gate',True),
            ('shield_block_admission','block_local_server_guard',True),
            ('shield_block_admission','projectile_tag_suppresses_callback_only',False),
            ('shield_block_admission','default_blocked_by_shield_knockback_receiver','attacker'),
        ])

    def test_default_bindings_not_config_guesses(self):
        self.assertEqual(self.note['concrete_bindings']['DamageCap']['native_value'],MAX_FLOAT)
        self.assertEqual(self.note['concrete_bindings']['RangeLimit']['native_value'],MAX_DOUBLE)
        self.note['concrete_bindings']['RangeLimit']['native_value'] = 8.0
        with self.assertRaises(AssertionError):
            self.check()
        self.reject_facts([
            ('shared_defense_bindings','dps_is_bucket_capacity',True),
            ('shared_defense_bindings','concrete_nature_regen_override',True),
            ('shared_defense_bindings','positive_shared_regen_delivery',True),
        ])

    def test_raw_state_and_parent_only_nbt(self):
        self.reject_facts([
            ('combat_state_prerequisites','shield_counter_means_segments_lost',False),
            ('combat_state_prerequisites','shield_setter_clamps',True),
            ('combat_state_prerequisites','shield_setter_heals',True),
            ('combat_state_prerequisites','shield_gate_reads_progress',True),
            ('combat_state_prerequisites','raw_state_is_tno_stage',True),
            ('combat_persistence','saved_anger',True),
            ('combat_persistence','saved_shield_counter',True),
            ('combat_persistence','inherited_ia_life',True),
        ])

    def test_environment_fall_and_literal_encounter_prerequisites(self):
        self.reject_facts([
            ('environment_admission','air_returns_native_max',True),
            ('environment_admission','all_forced_motion_immunity_claimed',True),
            ('falling_motion','uses_mob_effect',True),
            ('falling_motion','fall_target_gate',True),
            ('encounter_setup','constructor_health_is_heal_delivery',True),
            ('arena_spawn_prerequisites','marker_checks_bounding_box',True),
            ('arena_spawn_prerequisites','marker_calls_finalize_spawn',True),
            ('arena_spawn_prerequisites','marker_sets_home',True),
            ('arena_spawn_prerequisites','spawn_return_consumed',True),
        ])

    def test_native_direct_actor_cannot_be_replaced_with_causing_actor(self):
        evidence = read_json(EVIDENCE_FILE)
        root = next(w for w in evidence['witnesses'] if w['entry']==PKG+R+'.class')
        hurt = next(m for m in root['methods'] if m['name']=='hurt')
        i = next(i for i in hurt['instructions'] if i['offset']==1)
        i['operand'] = i['operand'].replace('getDirectEntity','getEntity')
        with self.assertRaises(AssertionError):
            validate_native_boundaries(evidence)

    def test_native_threshold_comparison_cannot_be_reversed(self):
        evidence = read_json(EVIDENCE_FILE)
        root = next(w for w in evidence['witnesses'] if w['entry']==PKG+R+'.class')
        hurt = next(m for m in root['methods'] if m['name']=='hurt')
        next(i for i in hurt['instructions'] if i['offset']==77)['opcode'] = '0x9c'
        with self.assertRaises(AssertionError):
            validate_native_boundaries(evidence)

    def test_prior_catalog_cannot_be_reopened(self):
        old = next(e for e in self.review['effects'] if e['review_checkpoint']!=self.note['checkpoint'])
        old['actual_behavior'] = 'reopened completed research'
        with self.assertRaises(AssertionError):
            validate_preservation(self.review,self.note,self.ledger)

    def test_no_policy_nonfinite_or_offense_completion(self):
        self.row('falling_motion')['stage_multiplier'] = 2
        with self.assertRaises(AssertionError):
            self.check()
        self.review = copy.deepcopy(self.original_review)
        self.row('falling_motion')['components'][0]['numerical_parameters']['vertical_factor'] = float('inf')
        with self.assertRaises(AssertionError):
            self.check()
        self.review = copy.deepcopy(self.original_review)
        next(t for t in self.ledger['targets'] if t['mod_key']=='cataclysm')['state'] = 'COMPLETE'
        with self.assertRaises(AssertionError):
            self.check()
        self.reject_facts([('combat_state_prerequisites','offensive_execution_reviewed',True)])


if __name__=='__main__':
    unittest.main()
