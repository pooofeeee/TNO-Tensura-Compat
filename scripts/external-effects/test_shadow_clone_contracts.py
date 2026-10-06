"""Independent native branch/source checks for shared shadow and clone contracts."""
import copy
import unittest

from catalog_common import OUT, read_json
from promote_combat_batch import validate_batch


class NativeContractHarness:
    def body(self, name, method='execute'):
        return max((m for w in self.native['witnesses']
                    if w['entry'].endswith('/' + name + '.class')
                    for m in w['methods'] if m['name'] == method),
                   key=lambda m: len(m['instructions']))['instructions']

    def row(self, suffix):
        return next(r for r in self.batch['effects'] if r['id'] == 'arphex:' + suffix)

    def prior(self):
        r = copy.deepcopy(read_json(OUT / 'mod-reviews/arphex.json'))
        ids = {x['id'] for x in self.batch['effects']}
        r['effects'] = [x for x in r['effects'] if x['id'] not in ids]
        r['paths'] = [x for x in r['paths'] if not set(x['effect_ids']) & ids]
        return r


class ShadowCloneTests(NativeContractHarness, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch = read_json(OUT / 'arphex-r2m5c-shadow-clone-native-callbacks.json')
        cls.native = read_json(OUT / 'native-evidence/arphex-shadow-clone-family.json')
        cls.census = read_json(OUT / 'arphex-combat-census.json')

    def test_shared_contracts_have_unique_native_parameter_identities(self):
        validate_batch(self.batch, self.prior(), self.census)
        self.assertEqual(len(self.batch['effects']), 6)
        self.assertEqual(len(self.batch['closed_actor_callback_entries']), 9)
        self.assertEqual(sum(len(c['parameters']) for r in self.batch['effects']
                             for c in r['scalable_parameter_candidates']), 85)
        self.assertEqual((len(self.native['witnesses']),
                          sum(len(w['methods']) for w in self.native['witnesses'])), (28, 266))
        self.assertFalse(self.batch['whole_mod_complete'])

    def test_three_variants_call_one_shared_helper(self):
        for actor in ('MothShadowCloneEntity', 'ArachnoidShadowCloneEntity', 'DiabolosShadowCloneEntity'):
            b = self.body(actor, 'baseTick')
            self.assertTrue(any('MothShadowCloneOnEntityTickUpdateProcedure.execute(' in str(i['operand']) for i in b))
        r = self.row('shared_moth_arachnoid_diabolos_shadow_callback')
        self.assertEqual(len(r['native_actor_variants']), 3)

    def test_shared_shadow_attempts_four_larvae_and_moth_only_rush(self):
        b = self.body('MothShadowCloneOnEntityTickUpdateProcedure')
        spawn = [i for i in b if 'EntityType.spawn(' in str(i['operand'])]
        self.assertEqual([i['offset'] for i in spawn], [153, 353, 408, 460, 512, 564])
        # First is no-player Larva; four later attempts are separate native calls.
        fields = [i for i in b if 'ArphexModEntities.' in str(i['operand'])]
        self.assertEqual(sum('SPIDER_LARVAE' in i['operand'] for i in fields), 5)
        self.assertEqual(sum('RUSH_SCARE' in i['operand'] for i in fields), 1)
        self.assertTrue(any(i['opcode'] == '0xc1' and i['operand'] == 'net/arphex/entity/MothShadowCloneEntity'
                            and 304 < i['offset'] < 353 for i in b))

    def test_contact_anonymous_magic_and_rewards_after_discard(self):
        b = self.body('MothShadowCloneOnEntityTickUpdateProcedure')
        at = next(j for j, i in enumerate(b) if i['offset'] == 829)
        self.assertEqual(b[at + 1]['opcode'], '0x57')
        self.assertTrue(any('DamageSource.<init>(Lnet/minecraft/core/Holder;)V' ==
                            str(i['operand']).split('net/minecraft/world/damagesource/')[-1]
                            for i in b[:at]))
        self.assertTrue(any('.discard(' in str(i['operand']) and i['offset'] == 1260 for i in b))
        for offset in (1323, 1381, 1439, 1497, 1546):
            j = next(j for j, i in enumerate(b) if i['offset'] == offset)
            self.assertEqual([i['operand'] for i in b[j-3:j-1]], [1200, 2])
        self.assertFalse(any('.hasLineOfSight(' in str(i['operand']) for i in b))

    def test_shared_size_is_written_and_read_by_native_activation_query(self):
        for n in ('MothShadowCloneOnInitialEntitySpawnProcedure', 'ScorpioidShadowCloneSpawnProcedure',
                  'DraconicShadowSpawnProcedure'):
            b = self.body(n)
            self.assertEqual(sum(i['opcode'] == '0xb5' and 'MapVariables.clonesizeD' in str(i['operand']) for i in b), 2)
        for n in ('MothShadowCloneOnEntityTickUpdateProcedure', 'ScorpioidShadowCloneTickProcedure',
                  'DraconicShadowTickProcedure'):
            b = self.body(n)
            reads = [j for j, i in enumerate(b) if 'MapVariables.clonesizeD' in str(i['operand'])]
            self.assertEqual(len(reads), 3)
            for j in reads:
                self.assertEqual((b[j]['opcode'], b[j+1]['operand'], b[j+2]['opcode']), ('0xb4', 100.0, '0x63'))

    def test_time_clone_delayed_absence_gate_and_effect_order(self):
        b = self.body('ArachnoidTimeCloneOnEntityTickUpdateProcedure', 'lambda$execute$8')
        by = {i['offset']: i for i in b}
        self.assertIn('List.isEmpty()', by[36]['operand'])
        self.assertEqual((by[41]['opcode'], by[41]['branch_target']), ('0x99', 60))
        self.assertIn('.discard(', by[57]['operand'])
        b = self.body('ArachnoidTimeCloneOnEntityTickUpdateProcedure')
        clear = next(i['offset'] for i in b if '.removeAllEffects(' in str(i['operand']))
        restore = next(i['offset'] for i in b if '.setHealth(' in str(i['operand']))
        self.assertLess(clear, 110)
        self.assertEqual(restore, 480)
        self.assertFalse(any('.heal(' in str(i['operand']) for i in b))
        self.assertTrue(any('.discard(' in str(i['operand']) and i['offset'] < restore for i in b))

    def test_hurt_helpers_use_causing_entity_before_native_filters(self):
        for actor in ('ArachnoidTimeCloneEntity', 'DraconicCloneEntity', 'DraconicFlyStalkEntity'):
            b = self.body(actor, 'hurt')
            cause = next(j for j, i in enumerate(b) if 'DamageSource.getEntity()' in str(i['operand']))
            callback = next(j for j, i in enumerate(b) if 'EntityIsHurtProcedure.execute(' in str(i['operand']))
            first_filter = next(j for j, i in enumerate(b) if '/DamageTypes.' in str(i['operand']))
            self.assertLess(cause, callback)
            self.assertLess(callback, first_filter)

    def test_scorpioid_regeneration_has_contradictory_native_side_guards(self):
        b = self.body('ScorpioidCloneTickProcedure')
        by = {i['offset']: i for i in b}
        self.assertIn('LevelAccessor.isClientSide()', by[1304]['operand'])
        self.assertEqual((by[1309]['opcode'], by[1309]['branch_target']), ('0x99', 1709))
        j = next(j for j, i in enumerate(b) if i['offset'] == 1609)
        last_side = max(k for k in range(j) if 'Level.isClientSide()' in str(b[k]['operand']))
        self.assertEqual(b[last_side + 1]['opcode'], '0x9a')
        self.assertGreater(b[last_side + 1]['branch_target'], 1609)
        r = self.row('scorpioid_clone_native_target_motion_and_melee')
        self.assertFalse(any('REGENERATION' in c['primitive'] for c in r['scalable_parameter_candidates']))

    def test_scorpioid_kill_callback_receives_defeated_entity(self):
        b = self.body('ScorpioidCloneEntity', 'awardKillScore')
        self.assertIn('Monster.awardKillScore(', b[4]['operand'])
        j = next(j for j, i in enumerate(b) if 'ScorpioidKillProcedure.execute(' in str(i['operand']))
        self.assertEqual(b[j-1]['opcode'], '0x2b')  # argument1, not this/local0
        goal = self.body('ScorpioidCloneEntity$1', 'canPerformAttack')
        self.assertTrue(any(i['operand'] == 12.25 for i in goal))
        self.assertTrue(any('.hasLineOfSight(' in str(i['operand']) for i in goal))

    def test_draconic_support_uses_independent_random_rays_and_late_motion_override(self):
        b = self.body('DraconicCloneOnEntityTickUpdateProcedure')
        rays = [j for j, i in enumerate(b) if i['offset'] < 2223 and 'Mth.nextInt(' in str(i['operand'])
                and [x['operand'] for x in b[j-2:j]] == [1, 20]]
        self.assertEqual(len(rays), 9)
        gate = next(i for i in b if i['offset'] == 2105)
        self.assertEqual((gate['opcode'], gate['branch_target']), ('0xa6', 2811))
        self.assertIn('.setDeltaMovement(', next(i['operand'] for i in b if i['offset'] == 3219))
        self.assertTrue(any(i['operand'] == .02 and 3200 < i['offset'] < 3219 for i in b))
        for actor in ('DraconicCloneEntity', 'DraconicFlyStalkEntity'):
            self.assertTrue(any('DraconicCloneOnEntityTickUpdateProcedure.execute(' in str(i['operand'])
                                for i in self.body(actor, 'baseTick')))
        self.assertFalse(any('.hurt(' in str(i['operand']) for i in b))

    def test_voidlasher_motion_command_selects_nearest_not_self(self):
        b = self.body('DraconicShadowTickProcedure')
        literal = next(i['operand'] for i in b if isinstance(i['operand'], str)
                       and i['operand'].startswith('execute at @e'))
        self.assertIn('type=arphex:voidlasher_shadow_clone,limit=1,sort=nearest', literal)
        self.assertIn('^ ^0.02 ^10', literal)
        self.assertNotIn('@s', literal)
        self.assertFalse(any('.hurt(' in str(i['operand']) for i in b))


class ShadowSpawnedPayloadTests(NativeContractHarness, unittest.TestCase):
    """Reuse the harness, with only missing native payload invariants as tests."""

    @classmethod
    def setUpClass(cls):
        cls.batch = read_json(OUT / 'arphex-r2m5d-shadow-summoned-native-payloads.json')
        cls.native = read_json(OUT / 'native-evidence/arphex-shadow-payload-family.json')
        cls.census = read_json(OUT / 'arphex-combat-census.json')

    def test_payload_bindings(self):
        validate_batch(self.batch, self.prior(), self.census)
        self.assertEqual(len(self.batch['effects']), 3)
        self.assertEqual(len(self.batch['closed_actor_callback_entries']), 5)
        self.assertEqual(sum(len(c['parameters']) for r in self.batch['effects']
                             for c in r['scalable_parameter_candidates']), 84)
        self.assertEqual((len(self.native['witnesses']),
                          sum(len(w['methods']) for w in self.native['witnesses'])), (25, 189))
        self.assertFalse(self.batch['whole_mod_complete'])

    def test_larvae_death_flag_is_self_not_loop_recipient(self):
        b = self.body('SpiderLarvaeEntityDiesProcedure')
        j = next(j for j, i in enumerate(b) if '.putBoolean(' in str(i['operand']))
        self.assertEqual(b[j-4]['local_index'], 7)  # native execute entity argument
        self.assertEqual(b[j-2]['operand'], 'spidergrab')
        self.assertEqual(b[j-1]['operand'], 0)

    def test_larvae_hurt_side_effect_precedes_native_rejection(self):
        b = self.body('SpiderLarvaeEntity', 'hurt')
        call = next(j for j, i in enumerate(b) if 'SpiderLarvaeEntityIsHurtProcedure.execute(' in str(i['operand']))
        reject = next(j for j, i in enumerate(b) if 'POISON_DAMAGE' in str(i['operand']))
        self.assertLess(call, reject)
        tiny = self.body('SpiderLarvaeTinyEntity', 'hurt')
        self.assertFalse(any('EntityIsHurtProcedure.execute(' in str(i['operand']) for i in tiny))
        h = self.body('SpiderLarvaeEntityIsHurtProcedure')
        self.assertTrue(any(i['operand'] == 3.0 for i in h))
        self.assertTrue(any(i['operand'] == 'spiderwidowmissinglegs' for i in h))
        tick = self.body('SpiderLarvaeOnEntityTickUpdateProcedure')
        self.assertFalse(any(i['operand'] == 'spiderwidowmissinglegs' for i in tick))

    def test_larvae_target_shiny_guard_is_self_and_only_normal_player_goal(self):
        for method in ('canUse', 'canContinueToUse'):
            b = self.body('SpiderLarvaeEntity$1', method)
            self.assertTrue(any('NonShinyProcedure.execute(' in str(i['operand']) for i in b))
        predicate = self.body('NonShinyProcedure')
        self.assertTrue(any('SpiderLarvaeEntity.DATA_shiny' in str(i['operand']) for i in predicate))
        tiny = self.body('SpiderLarvaeTinyEntity', 'registerGoals')
        self.assertFalse(any('NonShinyProcedure' in str(i['operand']) for i in tiny))

    def test_hallucination_contact_clock_is_inside_player_iteration(self):
        b = self.body('HallucinationScorpioidTickProcedure')
        by = {i['offset']: i for i in b}
        self.assertIn('.putDouble(', by[1991]['operand'])
        self.assertIn('.hurt(', by[2015]['operand'])
        self.assertIn('.putDouble(', by[2043]['operand'])
        j = next(j for j, i in enumerate(b) if i['offset'] == 2015)
        self.assertEqual((b[j-1]['operand'], b[j+1]['opcode']), (7.0, '0x57'))
        # Both updates are within the native world.players loop back edge.
        backward = [i for i in b if i.get('branch_target', i['offset']) < i['offset']]
        self.assertTrue(any(i['offset'] > 2043 and i['branch_target'] < 1969 for i in backward))

    def test_rush_blocking_skips_only_poison(self):
        b = self.body('RushScareOnEntityTickUpdateProcedure')
        by = {i['offset']: i for i in b}
        self.assertIn('.isBlocking(', by[498]['operand'])
        self.assertEqual((by[501]['opcode'], by[501]['branch_target']), ('0x9a', 692))
        self.assertIn('.performPrefixedCommand(', by[689]['operand'])
        # Levitation/Darkness/SlowFalling calls follow the poison block's exit.
        for offset in (758, 827, 896):
            self.assertIn('.performPrefixedCommand(', by[offset]['operand'])
        commands = [i['operand'] for i in b if isinstance(i['operand'], str) and i['operand'].startswith('effect give')]
        self.assertIn('effect give @p[distance=..6] poison 10 2 true', commands)
        self.assertIn('effect give @p[distance=..6] levitation 4 0 true', commands)

    def test_rush_delayed_clear_uses_unbounded_current_nearest(self):
        b = self.body('RushScareOnEntityTickUpdateProcedure', 'lambda$execute$5')
        self.assertTrue(any(i['operand'] == 'effect clear @p levitation' for i in b))
        self.assertFalse(any('.isAlive(' in str(i['operand']) for i in b))
        self.assertFalse(any('.getOwner(' in str(i['operand']) for i in b))


if __name__ == '__main__':
    unittest.main()
