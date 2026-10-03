"""Focused R2k6b archive regressions; no runtime or Stage policy tests."""
import copy
import json
import unittest

from catalog_common import read_json
from collect_cataclysm_harbinger_offense import EVIDENCE_FILE, SPEC_FILE
from validate_cataclysm_harbinger_offense import (
    LEDGER, NOTE, REVIEW, selected, validate, validate_contracts,
    validate_native_returns, validate_preservation, validate_records,
)


class HarbingerOffenseTests(unittest.TestCase):
    def setUp(self):
        self.review, self.note, self.ledger = [read_json(p) for p in [REVIEW, NOTE, LEDGER]]

    def check(self):
        return validate_records(self.review, self.note, self.ledger)

    def row(self, key):
        return next(e for e in selected(self.review) if e['id'] == 'cataclysm:harbinger_' + key)

    def reject_contract_changes(self, changes):
        for key, field, value in changes:
            with self.subTest(mechanic=key, field=field):
                rows = copy.deepcopy({e['id']: e for e in selected(self.review)})
                rows['cataclysm:harbinger_' + key][field] = value
                with self.assertRaises(AssertionError):
                    validate_contracts(rows)

    def test_scoped_archive_and_protected_checkpoints(self):
        result = validate()
        self.assertEqual(result['status'], 'PASS')
        self.assertEqual(result['new_mechanics'], 27)
        self.assertEqual(result['delivery_paths'], 27)
        self.assertEqual(result['candidate_numeric_parameters'], 88)
        self.assertEqual(result['new_method_witnesses'], 191)
        self.assertEqual(result['protected_harbinger_admission_shared_status_guardian_monstrosity_ignis'],
                         'BYTE_IDENTICAL')

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
        candidate = next(c for c in self.row('charge_contact')['scalable_parameter_candidates']
                         if c['primitive'] == 'FORCED_MOVEMENT')
        candidate['primitive'] = 'NATIVE_DAMAGE_REQUEST'
        with self.assertRaises(AssertionError):
            self.check()

    def test_nonfinite_native_value_rejected(self):
        self.row('charge_contact')['components'][0]['numerical_parameters']['hp_damage'] = float('inf')
        with self.assertRaises(AssertionError):
            self.check()

    def test_native_candidate_formula_cannot_change(self):
        self.row('charge_contact')['scalable_parameter_candidates'][0]['native_formula'] = 'Flattened damage'
        with self.assertRaises(AssertionError):
            self.check()

    def test_native_payload_links_are_not_invented(self):
        self.note['payload_entities'][0]['source_mechanic_ids'] = ['cataclysm:harbinger_alliance']
        with self.assertRaises((AssertionError, KeyError)):
            self.check()

    def test_selection_head_indices_and_native_target_state(self):
        self.reject_contract_changes([
            ('attack_selection', 'selection_order', ['CHARGE', 'DEATHLASER', 'LAUNCH', 'MISSILE']),
            ('attack_selection', 'rolls_short_circuit', False),
            ('head_targeting', 'side_head_dispatch_indices', [1, 2]),
            ('head_targeting', 'idle_head_counter_read_for_shot', True),
            ('head_targeting', 'stale_id_has_instanceof_guard', True),
        ])

    def test_custom_motion_and_native_charge_gates(self):
        self.reject_contract_changes([
            ('flight_control', 'movement_is_native_knockback', True),
            ('flight_control', 'pursuit_reads_is_act', True),
            ('flight_control', 'pursuit_reads_no_ai', True),
            ('charge_chain', 'movement_is_native_knockback', True),
            ('charge_chain', 'stop_requires_cooldown', True),
            ('charge_contact', 'push_requires_hurt_true', False),
            ('charge_contact', 'push_requires_on_ground', False),
            ('charge_contact', 'terrain_result_gates_damage', True),
        ])

    def test_launch_and_volley_native_snapshot_boundaries(self):
        self.reject_contract_changes([
            ('launch_chain', 'power_read_at_each_launch', False),
            ('missile_volley', 'shots_per_goal', 12),
            ('ranged_dispatch', 'caller_gate_rechecked', True),
        ])

    def test_hurt_return_status_and_distinct_kill_heal_calls(self):
        self.reject_contract_changes([
            ('missile_contact', 'kill_heal_call_count', 1),
            ('homing_contact', 'kill_heal_call_count', 1),
            ('howitzer_contact', 'kill_heal_call_count', 2),
            ('howitzer_contact', 'other_difficulty_duration', 0),
            ('missile_contact', 'status_requires_hurt_true', False),
            ('homing_contact', 'status_requires_victim_alive', True),
            ('howitzer_burst', 'explosion_requires_hurt_true', True),
            ('howitzer_burst', 'smoke_requires_hurt_true', True),
        ])

    def test_homing_speed_and_independent_terminal_branches(self):
        self.reject_contract_changes([
            ('homing_motion', 'steering_speed_reassigned_to_inertia', False),
            ('homing_motion', 'terminal_branches_mutually_exclusive', True),
            ('homing_motion', 'continues_after_discard', False),
            ('homing_motion', 'target_equals_owner', True),
        ])

    def test_explosion_radius_remains_separate_from_direct_damage(self):
        for key in ['missile_contact', 'homing_contact', 'homing_motion']:
            with self.subTest(mechanic=key):
                rows = copy.deepcopy({e['id']: e for e in selected(self.review)})
                r = rows['cataclysm:harbinger_' + key]
                r['components'] = [c for c in r['components'] if c['primitive'] != 'NATIVE_EXPLOSION']
                with self.assertRaises(StopIteration):
                    validate_contracts(rows)

    def test_smoke_native_owner_omission_unused_fields_and_hit_admission(self):
        self.reject_contract_changes([
            ('smoke_lifecycle', 'owner_uuid_saved', True),
            ('smoke_lifecycle', 'radius_on_use_consumed', True),
            ('smoke_lifecycle', 'duration_on_use_consumed', True),
            ('smoke_payload', 'has_radial_distance_check', True),
            ('smoke_payload', 'has_victim_reuse_cache', True),
            ('smoke_payload', 'has_bilateral_allied_check', False),
            ('smoke_payload', 'status_has_explicit_source', True),
        ])

    def test_laser_burn_rollback_and_entity_non_discard(self):
        self.reject_contract_changes([
            ('laser_contact', 'burn_restored_on_hurt_false', False),
            ('laser_contact', 'enchantment_requires_alive_after_hurt', True),
            ('laser_contact', 'entity_hit_discards', True),
            ('laser_motion', 'has_water_inertia_override', True),
        ])

    def test_death_laser_percent_ray_fade_and_empty_persistence(self):
        self.reject_contract_changes([
            ('death_laser_payload', 'hp_percent_factor', 1.0),
            ('death_laser_payload', 'dispatch_requires_on', True),
            ('death_laser_payload', 'dispatch_checks_caster_alive', True),
            ('death_laser_lifecycle', 'native_nbt_empty', False),
            ('death_laser_lifecycle', 'discard_returns_early', True),
            ('death_laser_lifecycle', 'ray_entity_clip_uses_full_endpoint', False),
            ('death_laser_lifecycle', 'default_possible_dispatch_ticks', 60),
        ])

    def test_native_terrain_actors_hooks_and_emp_gate(self):
        self.reject_contract_changes([
            ('death_laser_terrain', 'emp_reset_has_grief_gate', True),
            ('death_laser_terrain', 'grief_actor', 'CASTER'),
            ('death_laser_terrain', 'glass_has_destroy_event_hook', True),
            ('terrain_control', 'debris_adds_damage', True),
            ('terrain_control', 'reads_ignore_mobgriefing', True),
            ('terrain_control', 'idle_has_destroy_event_hook', True),
            ('terrain_control', 'reactive_timer_decrements_during_stun', True),
        ])

    def test_native_alliance_and_death_respawner(self):
        self.reject_contract_changes([
            ('missile_contact', 'direct_has_ally_check', True),
            ('alliance', 'scoped_selector_tag', 'HARBINGER_NONE_TARGETS'),
            ('alliance', 'none_targets_tag_read', True),
            ('defeat_lifecycle', 'death_explosion_time', 124),
            ('defeat_lifecycle', 'respawner_item', 'cataclysm:netherite_effigy'),
            ('defeat_lifecycle', 'has_first_defeat_ledger', True),
        ])

    def test_native_witness_guards_detect_lost_hurt_callbacks(self):
        evidence = read_json(EVIDENCE_FILE)
        witness = next(w for w in evidence['witnesses'] if w['entry'].endswith('/Wither_Missile_Entity.class'))
        method = next(m for m in witness['methods'] if m['name'] == 'onHitEntity')
        offset = next(i['offset'] for i in method['instructions'] if '.heal(' in str(i.get('operand')))
        method['instructions'] = [i for i in method['instructions'] if i['offset'] != offset]
        with self.assertRaises(AssertionError):
            validate_native_returns(evidence)

    def test_locked_admission_and_prior_boss_records_unchanged(self):
        for key in ['harbinger_incoming_admission', 'guardian_attack_selection',
                    'monstrosity_incoming_admission', 'ignis_shield_admission']:
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
                self.assertEqual(path.read_bytes(),
                    (json.dumps(read_json(path), ensure_ascii=False, indent=2) + '\n').encode('utf-8'))


if __name__ == '__main__':
    unittest.main()
