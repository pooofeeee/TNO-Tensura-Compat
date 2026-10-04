"""Focused regressions for bounded R2k13b Ignited Berserker static research."""
import copy
import unittest

from catalog_common import read_json
from collect_cataclysm_ignited_berserker_offense import B, S, PKG, EVIDENCE_FILE
from validate_cataclysm_ignited_berserker_offense import (
    LEDGER, NOTE, REVIEW, selected, validate, validate_contracts,
    validate_native_boundaries, validate_preservation, validate_records,
)


class IgnitedBerserkerOffenseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original_review=read_json(REVIEW)
        cls.original_note=read_json(NOTE)
        cls.original_ledger=read_json(LEDGER)

    def setUp(self):
        self.review=copy.deepcopy(self.original_review)
        self.note=copy.deepcopy(self.original_note)
        self.ledger=copy.deepcopy(self.original_ledger)

    def row(self,key):
        return next(e for e in selected(self.review) if e['id']=='cataclysm:ignited_berserker_'+key)

    def check(self):
        return validate_records(self.review,self.note,self.ledger)

    def reject_facts(self,changes):
        for key,field,value in changes:
            with self.subTest(mechanic=key,field=field):
                rows=copy.deepcopy({e['id'].removeprefix('cataclysm:ignited_berserker_'):e for e in selected(self.review)})
                rows[key][field]=value
                with self.assertRaises(AssertionError):validate_contracts(rows,self.note)

    def test_checkpoint_evidence_formatting_and_protected_families(self):
        result=validate()
        self.assertEqual(result['status'],'PASS')
        self.assertEqual(result['new_mechanics'],19)
        self.assertEqual(result['candidate_numeric_parameters'],15)
        self.assertEqual(result['new_method_witnesses'],18)
        self.assertEqual(result['protected_shared_status_prior_families_r2k13a'],'BYTE_IDENTICAL')

    def test_unique_ids_classifications_and_source_delivery(self):
        selected(self.review)[1]['id']=selected(self.review)[0]['id']
        with self.assertRaises(AssertionError):self.check()
        for field,value in [('primary_classification','INVENTED'),('source_actor',None),
                            ('delivery_paths',None),('hurt_return_dependency',None)]:
            with self.subTest(field=field):
                self.review=copy.deepcopy(self.original_review)
                self.row('area_damage')[field]=value
                with self.assertRaises(AssertionError):self.check()

    def test_candidates_preserve_native_primitive_formula_value_units_boundary(self):
        for field,value in [('primitive','BLAZING_BRAND'),('native_value',2.0),('native_formula','Stage formula'),
                            ('units','seconds'),('native_boundary','invented hook')]:
            with self.subTest(field=field):
                self.review=copy.deepcopy(self.original_review)
                self.row('area_damage')['scalable_parameter_candidates'][0][field]=value
                with self.assertRaises(AssertionError):self.check()

    def test_state_gates_and_uncalled_sword_helper_not_active_candidates(self):
        for key in ['attack_selection','sequence_state','pursuit_goal','sword_helper_damage',
                    'sword_helper_brand','sword_helper_heal','defeat_lifecycle']:
            with self.subTest(mechanic=key):
                self.review=copy.deepcopy(self.original_review)
                self.row(key)['scalable_parameter_candidates']=copy.deepcopy(self.row('area_damage')['scalable_parameter_candidates'])
                with self.assertRaises(AssertionError):self.check()

    def test_raw_state_rng_cooldowns_and_nonexclusive_spin(self):
        self.reject_facts([
            ('attack_selection','rng_before_cooldown',False),
            ('attack_selection','selection_has_hp_gate',True),
            ('attack_selection','selection_has_los_gate',True),
            ('sequence_state','sword_cooldown',80),
            ('sequence_state','spin_sets_movement_flags',True),
            ('sequence_state','state_start_restarts_matching_state',True),
            ('sequence_state','cooldown_written_on_stop',False),
            ('sequence_state','attack_state_is_stage',True),
            ('pursuit_goal','ordinary_melee_goal_registered',True),
            ('pursuit_goal','spin_claimed_stationary',True),
        ])

    def test_ten_native_area_call_tuples_preserve_float_arguments(self):
        self.assertEqual(len(self.note['area_call_parameters']),10)
        self.assertEqual([c['shield_disable_ticks'] for c in self.note['area_call_parameters']],[60]+[0]*9)
        self.note['area_call_parameters'][0]['range_width_multiplier']=4.35
        self.row('area_geometry')['area_call_parameters']=copy.deepcopy(self.note['area_call_parameters'])
        with self.assertRaises(AssertionError):self.check()
        self.note=copy.deepcopy(self.original_note)
        self.review=copy.deepcopy(self.original_review)
        self.reject_facts([('area_geometry','query_before_server_guard',False),
                           ('area_geometry','wrap_branches_repeat_horizontal_range',True)])

    def test_literal_123_and_self_motion_not_victim_knockback(self):
        self.reject_facts([
            ('combo_self_lunge','state6_lunge_ticks',[15,23,26,33]),
            ('combo_self_lunge','uses_native_knockback',True),
            ('combo_self_lunge','absolute_velocity_write',True),
            ('combo_self_lunge','uses_body_yaw',True),
            ('falling_motion','uses_mob_effect',True),
            ('falling_motion','preserves_horizontal_velocity',False),
        ])

    def test_damage_sources_not_collapsed_into_one_damage_type(self):
        self.reject_facts([
            ('area_damage','damage_type','cataclysm:sword_dance'),
            ('spin_aura_damage','damage_type','cataclysm:sword_dance'),
            ('sword_helper_damage','damage_type','minecraft:mob_attack'),
            ('sword_helper_damage','local_caller_proven',True),
            ('sword_helper_damage','explicit_same_type_exclusion',True),
        ])

    def test_brand_and_heal_remain_distinct_and_effect_return_does_not_gate_heal(self):
        self.reject_facts([
            ('area_brand','hurt_return_used',False),
            ('area_brand','effect_return_used',True),
            ('area_brand','brand_is_burn_or_dot',True),
            ('area_heal','heal_requires_hurt',False),
            ('area_heal','heal_requires_effect_acceptance',True),
            ('area_heal','heal_uses_actual_hp_loss',True),
            ('sword_helper_heal','heal_requires_effect_acceptance',True),
        ])
        self.row('area_brand')['components'][0]['numerical_parameters']['duration']=120
        with self.assertRaises(AssertionError):self.check()

    def test_shield_disable_after_hurt_is_not_hurt_success_gated(self):
        self.reject_facts([
            ('shield_disable','requires_hurt_success',True),
            ('shield_disable','blocked_rechecked_after_hurt',False),
            ('shield_disable','uses_actual_use_item',False),
        ])

    def test_spin_global_cadence_and_success_push_not_brand_or_heal(self):
        self.reject_facts([
            ('spin_aura_damage','uses_global_tick_count',False),
            ('spin_aura_damage','current_target_required',True),
            ('spin_aura_damage','applies_brand',True),
            ('spin_aura_damage','heals_self',True),
            ('spin_push','control_depends_on_hurt',False),
            ('spin_push','absolute_velocity_write',True),
            ('spin_push','reads_knockback_resistance',True),
        ])

    def test_absolute_body_repulsion_and_per_boundary_alliance(self):
        self.reject_facts([
            ('body_repulsion','local_caller_proven',False),
            ('body_repulsion','absolute_velocity_write',False),
            ('body_repulsion','local_team_guard',True),
            ('alliance','tag_requires_both_teams_null',False),
            ('alliance','body_repulsion_checks_alliance',True),
        ])

    def test_bounded_closure_no_invented_payload_terrain_or_respawner(self):
        self.reject_facts([
            ('payload_terrain_closure','owned_payload_classes',1),
            ('payload_terrain_closure','concrete_terrain_mutation',True),
            ('payload_terrain_closure','concrete_grab_or_mount',True),
            ('defeat_lifecycle','concrete_respawner_link',True),
            ('defeat_lifecycle','global_callbacks_absent_claimed',True),
        ])

    def test_new_native_boundary_mutations_rejected(self):
        for n,method,offset,field,value in [(B,'aiStep',600,'operand',23),
            (B,'aiStep',266,'branch_target',271),(B,'aiStep',153,'operand','attackTicks'),
            (S,'<init>',11,'branch_target',14),(B,'tick',29,'operand',.3)]:
            with self.subTest(method=method,offset=offset):
                ev=read_json(EVIDENCE_FILE)
                m=next(m for w in ev['witnesses'] if w['entry']==PKG+n+'.class' for m in w['methods'] if m['name']==method)
                next(i for i in m['instructions'] if i['offset']==offset)[field]=value
                with self.assertRaises(AssertionError):validate_native_boundaries(ev,self.note)

    def test_completed_admission_and_prior_catalog_cannot_be_reopened(self):
        e=next(e for e in self.review['effects'] if e['id']=='cataclysm:ignited_berserker_incoming_admission')
        e['actual_behavior']='changed locked admission'
        with self.assertRaises(AssertionError):validate_preservation(self.review,self.note,self.ledger)

    def test_no_policy_nonfinite_or_premature_whole_mod_completion(self):
        self.row('area_damage')['stage_multiplier']=2
        with self.assertRaises(AssertionError):self.check()
        self.review=copy.deepcopy(self.original_review)
        self.row('spin_push')['components'][0]['numerical_parameters']['horizontal_factor']=float('inf')
        with self.assertRaises(AssertionError):self.check()
        self.review=copy.deepcopy(self.original_review)
        next(t for t in self.ledger['targets'] if t['mod_key']=='cataclysm')['state']='COMPLETE'
        with self.assertRaises(AssertionError):self.check()


if __name__=='__main__':
    unittest.main()
