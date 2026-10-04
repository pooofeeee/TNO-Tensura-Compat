"""Bounded regressions for the R2k12b static research checkpoint."""
import copy
import unittest

from catalog_common import read_json
from collect_cataclysm_ignited_revenant_offense import ASH, BONE, EVIDENCE_FILE, PKG, R
from validate_cataclysm_ignited_revenant_offense import (
    LEDGER, NOTE, REVIEW, selected, validate, validate_contracts,
    validate_native_boundaries, validate_preservation, validate_records,
)


class IgnitedRevenantOffenseTests(unittest.TestCase):
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
        return next(e for e in selected(self.review) if e['id']=='cataclysm:ignited_revenant_'+key)

    def check(self):
        return validate_records(self.review,self.note,self.ledger)

    def reject_facts(self,changes):
        for key,field,value in changes:
            with self.subTest(mechanic=key,field=field):
                rows=copy.deepcopy({e['id'].removeprefix('cataclysm:ignited_revenant_'):e for e in selected(self.review)})
                rows[key][field]=value
                with self.assertRaises(AssertionError):validate_contracts(rows)

    def test_checkpoint_scoped_evidence_and_protected_families(self):
        result=validate()
        self.assertEqual(result['status'],'PASS')
        self.assertEqual(result['new_mechanics'],17)
        self.assertEqual(result['candidate_numeric_parameters'],23)
        self.assertEqual(result['new_method_witnesses'],50)
        self.assertEqual(result['protected_shared_status_prior_families_r2k12a'],'BYTE_IDENTICAL')

    def test_unique_ids_and_existing_classifications(self):
        selected(self.review)[1]['id']=selected(self.review)[0]['id']
        with self.assertRaises(AssertionError):self.check()
        self.review=copy.deepcopy(self.original_review)
        self.row('ash_damage')['primary_classification']='INVENTED'
        with self.assertRaises(AssertionError):self.check()

    def test_source_delivery_and_return_contract_required(self):
        for f in ['source_actor','delivery_paths','hurt_return_dependency','primary_test_source']:
            with self.subTest(field=f):
                self.review=copy.deepcopy(self.original_review)
                self.row('bone_damage')[f]=None
                with self.assertRaises(AssertionError):self.check()

    def test_candidate_primitive_value_formula_units_and_boundary(self):
        for f,v in [('primitive','KNOCKBACK'),('native_value',9.0),('native_formula','invented'),
                    ('units','unknown'),('native_boundary','invented hook')]:
            with self.subTest(field=f):
                self.review=copy.deepcopy(self.original_review)
                self.row('shield_aura_push')['scalable_parameter_candidates'][0][f]=v
                with self.assertRaises(AssertionError):self.check()

    def test_damage_requests_not_invented_as_fixed_coefficients(self):
        for key in ['ash_damage','bone_damage','shield_aura_damage']:
            with self.subTest(mechanic=key):
                self.review=copy.deepcopy(self.original_review)
                cand=next(c for c in self.row(key)['scalable_parameter_candidates'] if c['primitive']=='NATIVE_DAMAGE_REQUEST')
                self.assertIsNone(cand['native_value'])
                cand['native_value']=1.0
                with self.assertRaises(AssertionError):self.check()

    def test_native_state_timers_gates_unused_helpers_not_automatic_candidates(self):
        for key in ['attack_selection','sequence_state','pursuit_goal','body_repulsion','ash_lifecycle','bone_lifecycle','alliance','terrain_response','defeat_lifecycle']:
            with self.subTest(mechanic=key):
                self.review=copy.deepcopy(self.original_review)
                self.row(key)['scalable_parameter_candidates']=copy.deepcopy(self.row('bone_damage')['scalable_parameter_candidates'])
                with self.assertRaises(AssertionError):self.check()

    def test_ordered_selection_and_broken_shield_cooldown_exception(self):
        self.reject_facts([
            ('attack_selection','broken_ash_tests_cooldown',True),
            ('attack_selection','broken_ash_writes_cooldown',True),
            ('attack_selection','storm_has_shield_gate',True),
            ('attack_selection','selection_local_server_guard',True),
            ('sequence_state','decrement_before_selection',False),
            ('sequence_state','selected_cooldown_end_of_tick',199),
            ('sequence_state','bone_goal_sets_anger',True),
            ('pursuit_goal','pursuit_calls_native_hurt',True),
        ])

    def test_ash_delivery_alliance_and_blindness_distinct(self):
        self.reject_facts([
            ('ash_delivery','spawn_requires_target',True),
            ('ash_delivery','delivery_local_server_guard',True),
            ('ash_delivery','is_moving_projectile',True),
            ('ash_damage','alliance_receiver','caster'),
            ('ash_damage','close_bypasses_query',True),
            ('ash_damage','damage_local_server_guard',True),
            ('ash_blindness','hurt_return_used',False),
            ('ash_blindness','uses_source_effect_overload',True),
        ])

    def test_ash_owner_reload_and_dead_caster_continuation(self):
        self.reject_facts([
            ('ash_lifecycle','tick_resolves_caster_uuid',True),
            ('ash_lifecycle','dead_caster_discard_returns',True),
            ('ash_lifecycle','follows_caster_position',True),
            ('ash_lifecycle','follows_caster_pitch',True),
            ('ash_lifecycle','saves_native_age',True),
            ('ash_lifecycle','anonymous_damage_fallback',True),
        ])

    def test_bone_volley_motion_damage_and_lifecycle_separated(self):
        self.reject_facts([
            ('bone_delivery','volleys_independently_randomized',False),
            ('bone_delivery','volley_requires_target',True),
            ('bone_delivery','gravity_disabled',True),
            ('bone_self_lift','control_recipient','victim'),
            ('bone_self_lift','control_depends_on_hurt',True),
            ('bone_self_lift','uses_native_knockback',True),
            ('bone_damage','hurt_return_used',True),
            ('bone_damage','ignites_targets',True),
            ('bone_damage','uses_owner_alliance',False),
            ('bone_lifecycle','discard_depends_on_hurt',True),
            ('bone_lifecycle','concrete_lifetime_timer',True),
        ])

    def test_aura_push_hurt_gate_and_native_predicates(self):
        self.reject_facts([
            ('shield_aura_damage','aura_requires_target',True),
            ('shield_aura_damage','aura_checks_no_ai',True),
            ('shield_aura_push','control_depends_on_hurt',False),
            ('shield_aura_push','uses_native_knockback',True),
            ('shield_aura_push','reads_knockback_resistance',True),
            ('shield_aura_push','absolute_velocity_write',True),
            ('alliance','ash_inherits_caster_tag',True),
        ])

    def test_bounded_terrain_death_and_no_unused_repulsion_attack(self):
        self.reject_facts([
            ('terrain_response','concrete_terrain_mutation',True),
            ('terrain_response','concrete_explosion',True),
            ('terrain_response','global_terrain_callbacks_absent_claimed',True),
            ('defeat_lifecycle','concrete_respawner_link',True),
            ('defeat_lifecycle','global_death_callbacks_absent_claimed',True),
            ('body_repulsion','local_offense_caller_proven',True),
        ])

    def mutate_native(self,n,m,off,field,value):
        evidence=read_json(EVIDENCE_FILE)
        w=next(w for w in evidence['witnesses'] if w['entry']==PKG+n+'.class')
        method=next(x for x in w['methods'] if x['name']==m)
        next(i for i in method['instructions'] if i['offset']==off)[field]=value
        with self.assertRaises(AssertionError):validate_native_boundaries(evidence)

    def test_native_hurt_return_gates_and_discard_cannot_be_rewritten(self):
        self.mutate_native(R,'tick',488,'opcode','0x9a')
        self.mutate_native(ASH,'hitEntities',511,'branch_target',514)
        self.mutate_native(BONE,'onHitEntity',55,'opcode','0x99')
        self.mutate_native(BONE,'onHit',12,'branch_target',15)

    def test_native_alliance_receiver_and_height_control_cannot_be_repaired(self):
        self.mutate_native(ASH,'hitEntities',471,'opcode','0x2b')
        self.mutate_native(R+'$BoneStormGoal','tick',520,'operand',.3)

    def test_protected_r2k12a_record_cannot_be_reopened(self):
        e=next(e for e in self.review['effects'] if e['id']=='cataclysm:ignited_revenant_shield_break_admission')
        e['actual_behavior']='reopened completed axe/shield research'
        with self.assertRaises(AssertionError):validate_preservation(self.review,self.note,self.ledger)

    def test_no_policy_nonfinite_or_premature_completion(self):
        self.row('bone_damage')['stage_multiplier']=2
        with self.assertRaises(AssertionError):self.check()
        self.review=copy.deepcopy(self.original_review)
        self.row('shield_aura_push')['components'][0]['numerical_parameters']['vertical_increment']=float('inf')
        with self.assertRaises(AssertionError):self.check()
        self.review=copy.deepcopy(self.original_review)
        next(t for t in self.ledger['targets'] if t['mod_key']=='cataclysm')['state']='COMPLETE'
        with self.assertRaises(AssertionError):self.check()


if __name__=='__main__':
    unittest.main()
