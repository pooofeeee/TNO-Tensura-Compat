"""Independent native branch/source checks for shared shadow and clone contracts."""
import copy
import unittest

from catalog_common import OUT, read_json
from promote_combat_batch import validate_batch


def native_short_branch(method, offset):
    """Decode the existing pinned bytes when an old packet lacks branch metadata."""
    raw = bytes.fromhex(method['code_hex'])
    return offset + int.from_bytes(raw[offset+1:offset+3], 'big', signed=True)


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
        path_ids = {x['id'] for x in self.batch['paths']}
        r['effects'] = [x for x in r['effects'] if x['id'] not in ids]
        r['paths'] = [x for x in r['paths'] if x['id'] not in path_ids and not set(x['effect_ids']) & ids]
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


class WebSpiderNativeTests(NativeContractHarness, unittest.TestCase):
    """Independent exact callback, recipient, RNG and native lifecycle checks."""

    @classmethod
    def setUpClass(cls):
        cls.batch = read_json(OUT / 'arphex-r2m5e-web-spider-native-family.json')
        cls.native = read_json(OUT / 'native-evidence/arphex-spider-web-family.json')
        cls.census = read_json(OUT / 'arphex-combat-census.json')

    def test_shared_registration_and_exact_partial_pet_scope(self):
        validate_batch(self.batch, self.prior(), self.census)
        self.assertEqual(len(self.batch['effects']), 4)
        self.assertEqual(len(self.batch['closed_actor_callback_entries']), 5)
        self.assertEqual(sum(len(c['parameters']) for r in self.batch['effects']
                             for c in r['scalable_parameter_candidates']), 75)
        for a in ('SpiderBroodEntity', 'SpiderSnatcherEntity', 'SpiderFlatEntity', 'SpiderJumpEntity'):
            self.assertTrue(any('SpiderBroodOnEntityTickUpdateProcedure.execute(' in str(i['operand'])
                                for i in self.body(a, 'baseTick')))
        for a in ('SpiderFlatEntity', 'SpiderJumpEntity'):
            w = next(w for w in self.native['witnesses'] if w['entry'].endswith('/'+a+'.class'))
            self.assertEqual([m['name'] for m in w['methods']], ['baseTick'])
        self.assertFalse(self.batch['whole_mod_complete'])

    def test_small_web_both_loops_capture_current_recipient(self):
        b = self.body('SmallWebTickProcedure')
        self.assertEqual([i['offset'] for i in b if '.queueServerWork(' in str(i['operand'])], [555, 736])
        for offset in (481, 662):
            i = next(i for i in b if i['offset'] == offset)
            self.assertEqual((i['opcode'], i['local_index']), ('0x3a', 17))
        for offset in (555, 736):
            j = next(j for j,i in enumerate(b) if i['offset'] == offset)
            self.assertEqual((b[j-2]['opcode'], b[j-2]['local_index']), ('0x19', 17))
        for m in ('lambda$execute$2', 'lambda$execute$5'):
            bb = self.body('SmallWebTickProcedure', m)
            self.assertTrue(any('.makeStuckInBlock(' in str(i['operand']) for i in bb))
            self.assertEqual([i['operand'] for i in bb if i['opcode'] in ('0x12','0x13','0x14')], [.25,.05,.25])
            self.assertFalse(any('.isAlive(' in str(i['operand']) for i in bb))

    def test_giant_web_reversed_rng_bounds_use_existing_vanilla_contract(self):
        b = self.body('GiantWebOnEntityTickUpdateProcedure')
        for offset, values in ((1111,[-10,-28]),(1152,[-10,-28]),(1127,[10,28]),(1168,[10,28])):
            j = next(j for j,i in enumerate(b) if i['offset']==offset)
            self.assertIn('Mth.nextInt(', b[j]['operand'])
            self.assertEqual([i['operand'] for i in b[j-2:j]], values)
        p = read_json(OUT / 'vanilla-evidence/twilight-multiplayer.json')
        w = next(w for w in p['classes'] if w.get('raw_entry')=='ayo.class')
        mm = next(m for m in w['methods'] if m['name']=='nextInt')
        bb = mm['instructions']
        by = {i['offset']:i for i in bb}
        self.assertEqual((by[2]['opcode'],native_short_branch(mm,2)),('0xa1',7))
        self.assertEqual([by[o]['opcode'] for o in (5,6)], ['0x1b','0xac'])
        r = self.row('giant_web_native_contact_hatching_and_snatcher_delivery')
        keys = {k for c in r['scalable_parameter_candidates'] for k in c['parameters']}
        self.assertFalse({'unused_random_y','native_negative_unused_max'} & keys)

    def test_giant_web_removal_precedes_late_silk_check_and_is_cancellable(self):
        b = self.body('GiantWebOnEntityTickUpdateProcedure')
        remove = next(i['offset'] for i in b if '.removeAllEffects(' in str(i['operand']))
        silk = [i['offset'] for i in b if 'ArphexModMobEffects.SPIDER_SILK_TOUCH' in str(i['operand'])]
        self.assertEqual(remove,1472)
        self.assertTrue(any(o>remove for o in silk))
        p = read_json(OUT / 'reference-evidence/cult-loader-244.json')
        w = next(w for w in p['witnesses'] if w['entry']=='net/minecraft/world/entity/LivingEntity.class')
        mm = next(m for m in w['methods'] if m['name']=='removeAllEffects')
        bb = mm['instructions']
        j = next(j for j,i in enumerate(bb) if 'EventHooks.onEffectRemoved(' in str(i['operand']))
        self.assertEqual(bb[j+1]['opcode'],'0x99')
        self.assertEqual(native_short_branch(mm,54),60)  # false hook permits removal
        self.assertEqual(native_short_branch(mm,57),71)  # true hook skips native removal
        self.assertTrue(any('.discard(' in str(i['operand']) and i['offset']<remove for i in b))

    def test_native_brood_and_giant_death_spawn_attempts(self):
        for name, method, count in (('SpiderBroodEntityDiesProcedure','execute',5),
                                    ('SpiderBroodEntityDiesProcedure','lambda$execute$0',5),
                                    ('GiantWebEntityDiesProcedure','execute',7)):
            b = self.body(name,method)
            self.assertEqual(sum('EntityType.spawn(' in str(i['operand']) for i in b), count)
            self.assertFalse(any('.setOwner(' in str(i['operand']) for i in b))
        for actor, helper in (('SpiderBroodEntity','SpiderBroodEntityDiesProcedure'),
                              ('GiantWebEntity','GiantWebEntityDiesProcedure')):
            b = self.body(actor,'die')
            parent = next(j for j,i in enumerate(b) if i['opcode']=='0xb7' and '.die(' in str(i['operand']))
            payload = next(j for j,i in enumerate(b) if helper+'.execute(' in str(i['operand']))
            self.assertLess(parent,payload)

    def test_incoming_helpers_precede_filters_and_ignore_hurt_return(self):
        for actor,helper in (('SpiderBroodEntity','SpiderBroodEntityIsHurtProcedure'),
                            ('SpiderSnatcherEntity','SpiderWidowEntityIsHurtProcedure'),
                            ('SpiderFunnelEntity','SpiderFunnelEntityIsHurtProcedure')):
            b = self.body(actor,'hurt')
            payload = next(j for j,i in enumerate(b) if helper+'.execute(' in str(i['operand']))
            filter_site = next(j for j,i in enumerate(b) if 'DamageSource.getDirectEntity()' in str(i['operand']))
            parent = next(j for j,i in enumerate(b) if i['opcode']=='0xb7' and '.hurt(' in str(i['operand']))
            self.assertLess(payload,filter_site)
            self.assertLess(payload,parent)
        b = self.body('SpiderWidowEntityIsHurtProcedure','lambda$execute$2')
        cmd = next(i['operand'] for i in b if isinstance(i['operand'],str) and i['operand'].startswith('effect give'))
        self.assertEqual(cmd,'effect give @e[type=!arphex:spider_snatcher,distance=..5] arphex:webbed 4 0')
        self.assertFalse(any('.isAlive(' in str(i['operand']) for i in b))

    def test_live_pet_sit_status_and_curse_order_are_distinct(self):
        b = self.body('SpiderBroodOnEntityTickUpdateProcedure')
        by = {i['offset']:i for i in b}
        for offset in (2237,3504):
            self.assertIn('LivingEntity.addEffect(',by[offset]['operand'])
        self.assertIn('SynchedEntityData.set(',by[950]['operand'])
        self.assertLess(950,995)
        self.assertLess(995,1043)
        for name,mode in (('SpiderBroodOnEntityTickUpdateProcedure$1','SURVIVAL'),
                          ('SpiderBroodOnEntityTickUpdateProcedure$2','ADVENTURE')):
            self.assertTrue(any('GameType.'+mode in str(i['operand']) for i in self.body(name,'checkGamemode')))
        r = self.row('shared_brood_snatcher_flat_jump_native_spider_callbacks')
        self.assertFalse(any(c['primitive']=='MOB_EFFECT_FATIGUE_SHOW' for c in r['scalable_parameter_candidates']))

    def test_funnel_wander_marker_and_three_native_velocity_writes(self):
        b = self.body('ProwlMoveProcedure')
        self.assertTrue(any(i['operand']==20 for i in b))
        self.assertTrue(any('MobEffectInstance.getAmplifier(' in str(i['operand']) for i in b))
        b = self.body('SpiderFunnelEntity$3','canUse')
        self.assertTrue(any('RandomStrollGoal.canUse(' in str(i['operand']) for i in b))
        self.assertTrue(any('ProwlMoveProcedure.execute(' in str(i['operand']) for i in b))
        for m in ('execute','lambda$execute$1','lambda$execute$0'):
            b = self.body('SpiderFunnelEntityIsHurtProcedure',m)
            self.assertEqual(sum('.setDeltaMovement(' in str(i['operand']) for i in b),1)
            self.assertFalse(any('.isAlive(' in str(i['operand']) for i in b))
        r = self.row('funnel_spider_native_web_motion_and_pre_admission_reaction')
        self.assertFalse(any('amplifier' in k for c in r['scalable_parameter_candidates']
                             if c['primitive']=='MOB_EFFECT_SLOWNESS' for k in c['parameters']))


class NativeSpiderPetTests(NativeContractHarness, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch = read_json(OUT / 'arphex-r2m5f-flat-jump-native-pet-contracts.json')
        cls.native = read_json(OUT / 'native-evidence/arphex-spider-pet-family.json')
        cls.census = read_json(OUT / 'arphex-combat-census.json')

    def test_native_parameter_binding_and_shared_tick_reuse(self):
        validate_batch(self.batch,self.prior(),self.census)
        self.assertEqual(len(self.batch['effects']),1)
        r = self.row('shared_flat_jump_native_pet_specific_contract')
        self.assertEqual(sum(len(c['parameters']) for c in r['scalable_parameter_candidates']),17)
        self.assertIn('arphex:shared_brood_snatcher_flat_jump_native_spider_callbacks',r['canonical_contract_reuse'])
        self.assertFalse(any(c['native_consumer']['entry'].endswith('/SpiderBroodOnEntityTickUpdateProcedure.class')
                             for c in r['scalable_parameter_candidates']))
        self.assertEqual(len(r['native_actor_variants']),2)
        self.assertTrue(all(not c['no_owner_assignment_in_callbacks'] for c in r['native_actor_variants']))

    def test_feeding_source_order_and_dead_duplicate_condition(self):
        for actor in ('SpiderFlatEntity','SpiderJumpEntity'):
            b=self.body(actor,'mobInteract');by={i['offset']:i for i in b}
            self.assertIn('.usePlayerItem(',by[138]['operand'])
            self.assertIn('ItemStack.getFoodProperties(',by[143]['operand'])
            self.assertIn('.heal(',by[168]['operand'])
            self.assertEqual((by[111]['opcode'],by[111]['branch_target']),('0x99',357))
            # Identical pure predicates, with no native mutation along the failed first branch.
            for a,z in ((116,188),(123,195),(127,199)):
                self.assertEqual(by[a]['operand'],by[z]['operand'])
            self.assertEqual((by[119]['branch_target'],by[131]['branch_target']),(186,186))
            self.assertEqual((by[191]['branch_target'],by[203]['branch_target']),(235,235))
            self.assertEqual(by[214]['operand'],4.)
            r=self.row('shared_flat_jump_native_pet_specific_contract')
            self.assertFalse(any(c['native_consumer']['entry'].endswith('/'+actor+'.class')
                                 and c['native_consumer']['methods']==['mobInteract']
                                 and c['native_consumer']['offset']==217
                                 for c in r['scalable_parameter_candidates']))
        for item in ('MaggotGrubItem','RoachNymphItem','LocustLarvaeItem'):
            b=self.body(item,'<init>')
            j=next(j for j,i in enumerate(b) if 'FoodProperties$Builder.nutrition(' in str(i['operand']))
            self.assertEqual(b[j-1]['operand'],2)
            self.assertTrue(any('Item$Properties.food(' in str(i['operand']) for i in b))

    def test_current_owner_damage_after_delay_and_no_snapshot(self):
        b=self.body('SpiderFlatOnInitialEntitySpawnProcedure','lambda$execute$0')
        self.assertTrue(any(i['operand']=='arphex:segment' for i in b))
        self.assertTrue(any('TamableAnimal.isTame()' in str(i['operand']) for i in b))
        self.assertEqual(sum('TamableAnimal.getOwner()' in str(i['operand']) for i in b),2)
        self.assertTrue(any('DamageSource.<init>(Lnet/minecraft/core/Holder;Lnet/minecraft/world/entity/Entity;)V'
                            in str(i['operand']) for i in b))
        by={i['offset']:i for i in b}
        self.assertEqual(by[89]['operand'],1.)
        self.assertEqual(by[93]['opcode'],'0x57')  # hurt return ignored
        self.assertFalse(any('.isAlive(' in str(i['operand']) for i in b))

    def test_owned_goal_checks_current_target_and_raw_sit(self):
        b=self.body('CheckOwnedProcedure')
        self.assertTrue(any('Mob.getTarget()' in str(i['operand']) for i in b))
        self.assertTrue(any('TamableAnimal.isOwnedBy(' in str(i['operand']) for i in b))
        self.assertFalse(any('.getLastHurt' in str(i['operand']) for i in b))
        for actor,sit in (('SpiderFlatEntity','SittingFlatProcedure'),('SpiderJumpEntity','SittingJumpProcedure')):
            for child in ('$1','$2'):
                for m in ('canUse','canContinueToUse'):
                    self.assertTrue(any('CheckOwnedProcedure.execute(' in str(i['operand'])
                                        for i in self.body(actor+child,m)))
            b=self.body(sit)
            self.assertTrue(any(actor+'.DATA_sit' in str(i['operand']) for i in b))
            self.assertFalse(any('.isOrderedToSit(' in str(i['operand']) for i in b))
            b=self.body(actor,'mobInteract')
            self.assertTrue(any('.tame(' in str(i['operand']) for i in b))
            self.assertFalse(any('.DATA_sit' in str(i['operand']) for i in b))

    def test_variant_incoming_reactions_before_native_filters(self):
        for actor in ('SpiderFlatEntity','SpiderJumpEntity'):
            b=self.body(actor,'hurt')
            helper=next(i['offset'] for i in b if 'EntityIsHurtProcedure.execute(' in str(i['operand']))
            firstfilter=next(i['offset'] for i in b if 'DamageSource.' in str(i['operand']))
            self.assertLess(helper,firstfilter)
        flat=self.body('SpiderFlatEntity','hurt');jump=self.body('SpiderJumpEntity','hurt')
        self.assertTrue(any('POISON_DAMAGE' in str(i['operand']) for i in flat))
        self.assertFalse(any('POISON_DAMAGE' in str(i['operand']) for i in jump))
        for m in ('execute','lambda$execute$1','lambda$execute$0'):
            self.assertEqual(sum('.setDeltaMovement(' in str(i['operand'])
                                 for i in self.body('SpiderJumpEntityIsHurtProcedure',m)),1)
