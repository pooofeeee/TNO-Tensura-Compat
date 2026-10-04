"""Focused regressions for R2k14b offense/source/control/debris boundaries."""
import copy
import unittest

from catalog_common import read_json
from collect_cataclysm_kobolediator_offense import EVIDENCE_FILE, K, PKG
from validate_cataclysm_kobolediator_offense import (
    LEDGER, NOTE, REVIEW, selected, validate, validate_contracts,
    validate_native_boundaries, validate_preservation, validate_records,
)


class KobolediatorOffenseTests(unittest.TestCase):
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
        return next(e for e in selected(self.review) if e['id']=='cataclysm:kobolediator_'+key)

    def check(self):return validate_records(self.review,self.note,self.ledger)

    def reject_facts(self,changes):
        for key,field,value in changes:
            with self.subTest(mechanic=key,field=field):
                rows=copy.deepcopy({e['id'].removeprefix('cataclysm:kobolediator_'):e for e in selected(self.review)})
                rows[key][field]=value
                with self.assertRaises(AssertionError):validate_contracts(rows,self.note)

    def test_checkpoint_formatting_protected_facts_and_evidence_scope(self):
        result=validate()
        self.assertEqual(result['status'],'PASS')
        self.assertEqual(result['new_mechanics'],18)
        self.assertEqual(result['candidate_numeric_parameters'],10)
        self.assertEqual(result['new_method_witnesses'],19)
        self.assertEqual(result['protected_shared_status_prior_families_r2k14a'],'BYTE_IDENTICAL')

    def test_unique_ids_valid_classifications_and_sources(self):
        selected(self.review)[1]['id']=selected(self.review)[0]['id']
        with self.assertRaises(AssertionError):self.check()
        for field,value in [('primary_classification','INVENTED'),('source_actor',None),('delivery_paths',None),('hurt_return_dependency',None)]:
            with self.subTest(field=field):
                self.review=copy.deepcopy(self.original_review)
                self.row('area_damage')[field]=value
                with self.assertRaises(AssertionError):self.check()

    def test_candidate_primitive_formula_units_and_boundary_are_preserved(self):
        for field,value in [('primitive','FORCED_MOVEMENT'),('native_formula','invented'),('native_value',14),('units','ticks'),('native_boundary','another callback')]:
            with self.subTest(field=field):
                self.review=copy.deepcopy(self.original_review)
                self.row('area_damage')['scalable_parameter_candidates'][0][field]=value
                with self.assertRaises(AssertionError):self.check()

    def test_no_automatic_stage_scalars_from_native_state_terrain_or_debris(self):
        for key in ['attack_selection','sequence_state','charge_terrain','charge_debris','stomp_debris']:
            with self.subTest(mechanic=key):
                self.review=copy.deepcopy(self.original_review)
                e=self.row(key);o=e['numeric_observations'][0]
                e['scalable_parameter_candidates']=[dict(primitive=o['primitive'],parameters=[o['parameter']],native_value=o['native_value'],
                    native_formula=o['native_formula'],units=o['units'],native_boundary=o['boundary'])]
                with self.assertRaises(AssertionError):self.check()

    def test_rng_stop_cooldown_and_matching_state_counter_are_native(self):
        self.reject_facts([
            ('attack_selection','rng_before_cooldown',False),
            ('sequence_state','cooldown_written_on_stop',False),
            ('sequence_state','cooldown_decrements_both_sides',False),
            ('sequence_state','local_noai_decrement_guard',True),
            ('sequence_state','state_start_restarts_matching_state',True),
            ('sequence_state','charge_end_range_goal_required_state',7),
            ('sequence_state','state7_tick5_guaranteed_on_recovery',True),
            ('pursuit_goal','ordinary_melee_goal_registered',True),
        ])

    def test_damage_control_and_shield_hurt_return_dependencies_stay_distinct(self):
        self.reject_facts([
            ('area_damage','hurt_return_used',True),
            ('area_damage','post_hurt_motion',True),
            ('shield_disable','requires_hurt_success',True),
            ('shield_disable','stomp_positive_shield_duration',True),
            ('stomp_pull','control_depends_on_hurt',False),
            ('stomp_pull','absolute_velocity_write',True),
            ('stomp_pull','factor_clamped',True),
            ('charge_push','control_depends_on_hurt',False),
            ('charge_push','requires_grounded_victim',False),
            ('charge_push','uses_native_knockback',True),
        ])

    def test_charge_self_motion_not_target_knockback_or_charge_damage(self):
        self.reject_facts([
            ('charge_motion','preserves_vertical_velocity',False),
            ('charge_motion','uses_body_yaw',True),
            ('charge_motion','uses_target_vector',True),
            ('charge_motion','charge_tick_calls_super',True),
            ('charge_damage','uses_global_tick_count',False),
            ('charge_damage','damage_requires_grounded_victim',True),
            ('charge_damage','current_target_required',True),
        ])

    def test_area_wrap_geometry_and_duplicate_stomp_samples_are_not_repaired(self):
        self.reject_facts([
            ('area_geometry','query_before_server_guard',False),
            ('area_geometry','wrap_branches_repeat_horizontal_range',True),
            ('stomp_sampling','duplicate_distance5_preserved',False),
            ('stomp_sampling','hitset_added',True),
            ('stomp_sampling','air_fallback_cancels_damage',True),
            ('stomp_sampling','render_scan_repositions_damage_sample',True),
        ])
        calls=self.note['stomp_call_parameters']
        self.assertEqual([(c['attack_tick'],c['distance']) for c in calls if c['distance']==5],[(21,5),(23,5)])
        calls[4]['distance']=6
        with self.assertRaises(AssertionError):self.check()

    def test_debris_is_not_a_damage_source_or_native_falling_block_payload(self):
        self.reject_facts([
            ('stomp_damage','debris_is_damage_source',True),
            ('stomp_damage','damage_requires_debris_add_success',True),
            ('stomp_damage','damage_requires_found_support',True),
            ('stomp_debris','debris_calls_hurt',True),
            ('stomp_debris','debris_places_blocks',True),
            ('charge_debris','debris_has_damage_owner',True),
            ('charge_debris','spawn_requires_destroy_success',True),
            ('charge_debris','vertical_motion_multiplies_displacement',False),
        ])

    def test_terrain_gates_and_alliance_remain_native(self):
        self.reject_facts([
            ('charge_terrain','ignore_setting_or_native_grief',False),
            ('charge_terrain','uses_per_block_destroy_event',False),
            ('charge_terrain','destruction_requires_hurt',True),
            ('charge_terrain','destroy_result_gates_debris',True),
            ('charge_terrain','destroy_result_gates_contact_damage',True),
            ('charge_terrain','terrain_calls_hurt',True),
            ('alliance','tag_requires_both_teams_null',False),
            ('alliance','explicit_same_type_exclusion',False),
        ])

    def test_native_witnesses_reject_changed_rng_source_float_order_and_control(self):
        for name,method,offset,field,value in [
            (K+'$1','canUse',22,'operand',9.0),
            (K+'$5','stop',8,'operand',80),
            (K,'aiStep',643,'opcode','0x2b'),
            (K,'aiStep',722,'opcode','0x8d'),
            (K,'aiStep',734,'branch_target',737),
            (K,'aiStep',741,'branch_target',744),
            (K,'AreaAttack',293,'opcode','0x36'),
            (K,'AreaAttack',235,'branch_target',331),
            (K,'spawnBlocks',414,'operand',4.0),
            (K,'spawnBlocks',411,'branch_target',414),
            (K+'$3','tick',89,'operand','net/minecraft/world/phys/Vec3.xD'),
            (K,'ChargeBlockBreaking',143,'branch_target',150),
            (K,'ChargeBlockBreaking',208,'operand',10),
            (K,'isAlliedTo',34,'branch_target',44),
        ]:
            with self.subTest(method=method,offset=offset):
                evidence=read_json(EVIDENCE_FILE)
                w=next(w for w in evidence['witnesses'] if w['entry']==PKG+name+'.class')
                m=next(m for m in w['methods'] if m['name']==method)
                next(i for i in m['instructions'] if i['offset']==offset)[field]=value
                with self.assertRaises(AssertionError):validate_native_boundaries(evidence,self.note)

    def test_locked_admission_and_prior_families_cannot_be_reopened(self):
        old=next(e for e in self.review['effects'] if e['id']=='cataclysm:kobolediator_incoming_admission')
        old['actual_behavior']='changed protected incoming behavior'
        with self.assertRaises(AssertionError):validate_preservation(self.review,self.note,self.ledger)
        self.review=copy.deepcopy(self.original_review)
        old=next(e for e in self.review['effects'] if e['review_checkpoint']!=self.note['checkpoint'])
        old['source_actor']='changed protected source'
        with self.assertRaises(AssertionError):validate_preservation(self.review,self.note,self.ledger)

    def test_no_balance_runtime_or_premature_mod_completion(self):
        self.row('area_damage')['stage_multiplier']=2
        with self.assertRaises(AssertionError):self.check()
        self.review=copy.deepcopy(self.original_review)
        self.row('charge_push')['components'][0]['numerical_parameters']['horizontal_factor']=float('inf')
        with self.assertRaises(AssertionError):self.check()
        self.review=copy.deepcopy(self.original_review)
        next(t for t in self.ledger['targets'] if t['mod_key']=='cataclysm')['state']='COMPLETE'
        with self.assertRaises(AssertionError):self.check()
        self.reject_facts([('payload_lifecycle_closure','global_callbacks_absent_claimed',True),
                           ('defeat_lifecycle','concrete_respawner_link',True)])


if __name__=='__main__':unittest.main()
