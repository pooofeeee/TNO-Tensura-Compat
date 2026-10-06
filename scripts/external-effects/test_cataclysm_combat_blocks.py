"""R2k33b only: semantic distinctions, eight-boundary closure and audit protection."""
import copy
import hashlib
import json
import unittest

from catalog_common import OUT, read_json
from collect_cataclysm_coverage_audit import PREFIX, resolve_combat_blocks


class CombatBlockTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_path = OUT / 'cataclysm-r2k33a-coverage-audit.json'
        cls.base = read_json(cls.base_path)
        cls.note = read_json(OUT / 'cataclysm-r2k33b-combat_blocks-family.json')
        cls.review = read_json(OUT / 'mod-reviews/cataclysm.json')
        cls.audit_path = OUT / 'cataclysm-coverage-audit.json'
        cls.audit = read_json(cls.audit_path)
        cls.rows = {r['id'].removeprefix('cataclysm:combat_blocks_'): r
                    for r in cls.review['effects'] if r['id'] in cls.note['mechanic_ids']}
        cls.rows['registry']=next(r['native_context'] for r in cls.review['native_context_records']
                                 if r.get('original_id')=='cataclysm:combat_blocks_registry')
        cls.evidence = read_json(OUT / cls.note['evidence_file'])

    def test_exact_eight_native_boundaries_and_other_rows_unchanged(self):
        expected = {
            ('blockentities/EMP_Block_Entity', 'tick'),
            ('blockentities/ObsidianExplosionTrapBricks_Block_Entity', 'tick'),
            ('blockentities/SandstoneIgniteTrap_Block_Entity', 'tick'),
            ('blockentities/Door_Of_Seal_BlockEntity', 'tick'),
            ('blocks/Altar_Of_Fire_Block', 'entityInside'),
            ('blocks/EndStoneTeleportTrapBricks', 'activate'),
            ('blocks/PurpurVoidRuneTrapBlock', 'activate'),
            ('entity/projectile/Poison_Dart_Entity', 'doPostHurtEffects'),
        }
        actual = {(r['entry'].removeprefix(PREFIX).removesuffix('.class'), r['method'])
                  for r in self.note['coverage_boundary_resolutions']}
        self.assertEqual(actual, expected)
        self.assertEqual(len(self.base['residual_methods']), len(self.audit['residual_methods']))
        changed = 0
        for before, after in zip(self.base['residual_methods'], self.audit['residual_methods']):
            if before.get('queue_domain') == 'R2k33b_BLOCKS_TRAPS_EMP':
                changed += 1
                self.assertEqual(after['disposition'], 'RESOLVED_BY_SEMANTIC_RECORD')
                self.assertTrue(after['mechanic_ids'])
            else:
                # Later integrity reconciliation may close the remaining scope,
                # but it must preserve the exact native method identity/hash.
                for key in ('entry','method','descriptor','code_sha256'):
                    self.assertEqual(before[key],after[key])
        self.assertEqual(changed, 8)
        self.assertNotIn('PENDING_TARGETED_RECONCILIATION',self.audit['summary']['counts_by_disposition'])

    def test_every_census_hit_proven_by_exact_pinned_native_method(self):
        for binding in self.note['coverage_boundary_resolutions']:
            witness = next(w for w in self.evidence['witnesses'] if w['entry'] == binding['entry'])
            method = next(m for m in witness['methods']
                          if (m['name'], m['descriptor']) == (binding['method'], binding['descriptor']))
            self.assertEqual(method['code_sha256'], binding['native_code_sha256'])
            instructions = {(i['offset'], str(i['operand'])) for i in method['instructions']}
            for hit in binding['covered_census_hits']:
                self.assertIn((hit['offset'], str(hit['operand'])), instructions)

    def test_native_ownership_return_and_motion_distinctions(self):
        r = self.rows
        self.assertTrue(r['emp_charge']['overload_written_before_damage'])
        self.assertFalse(r['emp_charge']['power_off_clears_overload'])
        self.assertFalse(r['emp_damage']['adds_status'])
        self.assertIsNone(r['emp_damage']['damage_source_owner'])
        self.assertFalse(r['obsidian_pull']['native_knockback'])
        self.assertEqual(r['obsidian_explosion']['explosion_interaction'], 'NONE')
        self.assertEqual(r['door_explosion']['explosion_interaction'], 'TRIGGER')
        self.assertIsNone(r['door_explosion']['damage_source_owner'])
        self.assertFalse(r['door_activation']['captures_player_damage_owner'])
        self.assertFalse(r['door_activation']['consumes_key'])
        self.assertFalse(r['door_clock']['unlit_resets_clock'])
        self.assertEqual(r['door_clock']['saved_combat_keys'], ['animationTicks'])
        self.assertFalse(r['ignite_burn']['hurt_gates_secondary_payload'])
        self.assertFalse(r['altar_collision']['adds_burn'])
        self.assertFalse(r['teleport_blindness']['teleport_success_gates_status'])
        self.assertEqual(r['teleport_attempt']['teleport_attempts'], 1)
        self.assertFalse(r['rune_slowness']['spawn_success_gates_status'])
        self.assertIsNone(r['rune_delivery']['caster'])
        self.assertTrue(r['rune_damage']['reuses_locked_payload'])
        self.assertFalse(r['dart_cycle']['spawn_success_gates_schedule'])
        self.assertFalse(r['dart_cycle']['guaranteed_fixed_period'])
        self.assertIsNone(r['dart_delivery']['projectile_owner'])
        self.assertEqual(r['dart_delivery']['pickup'], 'DISALLOWED')
        self.assertTrue(r['dart_poison']['hurt_gates_secondary_payload'])
        self.assertEqual(r['dart_poison']['effect_source'], 'owner_or_projectile')
        self.assertFalse(r['dart_lifecycle']['custom_ttl'])

    def test_status_damage_and_delivery_candidates_not_collapsed(self):
        def pairs(key):
            return {(c['primitive'], p) for c in self.rows[key]['scalable_parameter_candidates']
                    for p in c['parameters']}
        self.assertEqual(pairs('teleport_blindness'), {('MOB_EFFECT_BLINDNESS', 'duration')})
        self.assertEqual(pairs('rune_slowness'), {('MOB_EFFECT_MOVEMENT_SLOWDOWN', 'duration'),
                                               ('MOB_EFFECT_MOVEMENT_SLOWDOWN', 'amplifier')})
        self.assertEqual(pairs('dart_poison'), {('MOB_EFFECT_POISON', 'duration'),
                                              ('MOB_EFFECT_POISON', 'amplifier')})
        self.assertEqual(pairs('dart_damage'), {('NATIVE_DAMAGE_REQUEST', 'base_damage')})
        self.assertEqual(pairs('obsidian_pull'), {('FORCED_MOVEMENT', 'strength'),
                                                ('DELIVERY_BOX', 'half_extent')})
        self.assertEqual(pairs('ignite_burn'), {('BURN', 'duration')})
        for row in self.rows.values():
            self.assertFalse(row.get('stage_eligibility_decided', False))
        for key in ('emp_charge', 'obsidian_cycle', 'door_clock', 'step_admission', 'random_rearm'):
            self.assertFalse(self.rows[key]['scalable_parameter_candidates'])

    def test_registry_identity_and_literal_bindings(self):
        bindings = self.rows['registry']['registry_bindings']
        self.assertEqual(len(bindings), 14)
        self.assertEqual(self.rows['registry']['consumed_config_fields'], [])
        dart = next(r for r in bindings if r['field'] == 'POISON_DART')
        self.assertEqual(dart['registry_id'], 'cataclysm:poison_dart')
        tile = next(r for r in bindings if '/ModTileentites.class' in r['class_entry']
                    and r['field'] == 'SANDSTONE_IGNITE_TRAP')
        self.assertEqual(tile['registry_id'], 'cataclysm:sadsotne_ignite_trap')
        self.assertEqual(self.rows['ignite_admission_cycle']['activation_tag'], 'SANDSTONE_TRAP_NOT_DETECTED')
        self.assertEqual(self.rows['step_admission']['activation_tag'], 'TRAP_BLOCK_NOT_DETECTED')

    def test_byte_identical_audit_and_accurate_totals(self):
        self.assertEqual(self.audit['base_audit_sha256'], hashlib.sha256(self.base_path.read_bytes()).hexdigest())
        self.assertEqual(self.audit['summary']['total_canonical_semantic_records'],len(self.review['effects']))
        self.assertEqual(self.audit['summary']['total_canonical_numeric_candidates'],
                         sum(len(c['parameters']) for r in self.review['effects']
                             for c in r.get('scalable_parameter_candidates', [])))
        self.assertEqual(sum(self.audit['summary']['classification_counts'].values()), len(self.review['effects']))
        ledger = read_json(OUT / 'mod-completion-ledger.json')
        cat = next(t for t in ledger['targets'] if t['mod_key'] == 'cataclysm')
        self.assertEqual(cat['state'], 'COMPLETE')
        self.assertEqual(cat['semantic_effect_count'], len(self.review['effects']))
        self.assertEqual(cat['remaining_reconciliation_boundaries'], 0)
        self.assertEqual(cat['numeric_candidate_count'], self.audit['summary']['total_canonical_numeric_candidates'])
        self.assertEqual(cat['remaining_native_ambiguities'],0)
        self.assertEqual(self.review['coverage_audit_file'], cat['coverage_audit_file'])
        self.assertEqual(self.audit['exact_next_task'], cat['exact_next_task'])

    def test_reject_duplicate_missing_or_unrelated_boundary(self):
        for change in ('duplicate', 'missing', 'unrelated', 'wrong_hash', 'lost_hit'):
            note = copy.deepcopy(self.note)
            bindings = note['coverage_boundary_resolutions']
            if change == 'duplicate':
                bindings[1] = copy.deepcopy(bindings[0])
            elif change == 'missing':
                bindings.pop()
            elif change == 'unrelated':
                bindings[0]['entry'] = PREFIX+'unrelated.class'
            elif change == 'wrong_hash':
                bindings[0]['native_code_sha256'] = '0'*64
            else:
                bindings[0]['covered_census_hits'] = []
            with self.subTest(change=change), self.assertRaises(AssertionError):
                resolve_combat_blocks(self.base, self.review, note)


if __name__ == '__main__':
    unittest.main()
