"""Shared harness, independent native facts for bounded small-actor families."""
import unittest
from catalog_common import OUT, read_json
from promote_combat_batch import validate_batch
from test_shadow_clone_contracts import NativeContractHarness


class CentipedeNativeTests(NativeContractHarness, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch=read_json(OUT/'arphex-r2m5o-centipede-native-contracts.json')
        cls.native=read_json(OUT/'native-evidence/arphex-centipede-native-families.json')
        cls.census=read_json(OUT/'arphex-combat-census.json')

    def test_exact_shared_consumers_and_four_roots(self):
        validate_batch(self.batch,self.prior(),self.census)
        self.assertEqual((len(self.batch['effects']),len(self.batch['closed_actor_callback_entries'])),(3,4))
        self.assertEqual(sum(len(c['parameters']) for r in self.batch['effects']
                             for c in r['scalable_parameter_candidates']),59)
        self.assertEqual((len(self.native['witnesses']),sum(len(w['methods']) for w in self.native['witnesses'])),(34,197))
        for a in ('CentipedeEvictorEntity','CentipedeEvictorLarvaeEntity'):
            self.assertEqual(sum('CentipedeEvictorOnEntityTickUpdateProcedure.execute(' in str(i['operand'])
                                 for i in self.body(a,'baseTick')),1)

    def test_evictor_incoming_sideeffects_precede_native_rejection(self):
        b=self.body('CentipedeEvictorEntity','hurt')
        causing=next(i['offset'] for i in b if '.getEntity()' in str(i['operand']))
        helper=next(i['offset'] for i in b if 'EntityIsHurtProcedure.execute(' in str(i['operand']))
        direct=next(i['offset'] for i in b if '.getDirectEntity()' in str(i['operand']))
        self.assertLess(causing,helper);self.assertLess(helper,direct)
        b=self.body('CentipedeEvictorEntityIsHurtProcedure')
        self.assertEqual([i['offset'] for i in b if 'EntityType.spawn(' in str(i['operand'])],[157])
        self.assertFalse(any('.hurt(' in str(i['operand']) or '.setOwner(' in str(i['operand']) for i in b))

    def test_big_missing_regen_gate_contains_stepheight(self):
        b=self.body('CentipedeEvictorOnEntityTickUpdateProcedure');by={i['offset']:i for i in b}
        self.assertIn('.hasEffect(',by[2212]['operand'])
        self.assertEqual((by[2215]['opcode'],by[2215]['branch_target']),('0x9a',2358))
        self.assertTrue(2215<2308<2358)
        self.assertEqual(by[2305]['operand'],2.)
        self.assertEqual([i['offset'] for i in b if '.setBaseValue(' in str(i['operand'])],[2308])

    def test_player_range_is_target_type_not_distance(self):
        b=self.body('PlayerRangeProcedure')
        self.assertTrue(any(i['opcode']=='0xc1' and i['operand']=='net/minecraft/world/entity/player/Player' for i in b))
        self.assertFalse(any('distance' in str(i['operand']) for i in b))
        self.assertTrue(any('PlayerRangeProcedure.execute(' in str(i['operand']) for i in self.body('CentipedeEvictorEntity$1','canUse')))
        self.assertFalse(any('PlayerRangeProcedure.execute(' in str(i['operand']) for i in self.body('CentipedeEvictorEntity$2','canPerformAttack')))

    def test_larva_shiny_guard_keeps_parent_spider_goals(self):
        b=self.body('CentipedeEvictorLarvaeEntity','registerGoals')
        self.assertEqual(b[1]['operand'],'net/minecraft/world/entity/monster/Spider.registerGoals()V')
        for a in ('CentipedeEvictorLarvaeEntity$1','CentipedeEvictorLarvaeEntity$2'):
            self.assertTrue(any('NotShinyProcedure.execute(' in str(i['operand']) for i in self.body(a,'canUse')))
        b=self.body('NotShinyProcedure')
        self.assertTrue(any('DATA_shinier' in str(i['operand']) for i in b))
        b=self.body('CentipedeEvictorLarvaeEntityIsHurtProcedure')
        self.assertTrue(any(i['operand']=='stronger' for i in b))
        self.assertFalse(any('DATA_stronger' in str(i['operand']) for i in b))

    def test_death_summon_delayed_and_lightning_visual_only(self):
        b=self.body('CentipedeEvictorLarvaeEntityDiesProcedure')
        self.assertTrue(any('DATA_stronger' in str(i['operand']) for i in b))
        j=next(j for j,i in enumerate(b) if '.setVisualOnly(' in str(i['operand']))
        self.assertEqual(b[j-1]['operand'],1)
        self.assertFalse(any('EntityType.spawn(' in str(i['operand']) for i in b))
        b=self.body('CentipedeEvictorLarvaeEntityDiesProcedure','lambda$execute$7')
        self.assertTrue(any('ArphexModEntities.CENTIPEDE_EVICTOR' in str(i['operand']) for i in b))
        self.assertFalse(any(x in str(i['operand']) for i in b for x in ('.getArmorValue(','.canOcclude(','.isAlive(','.setOwner(')))

    def test_stalker_duplicate_stepwrites_and_facing_not_duplicate_scalars(self):
        b=self.body('CentipedeStalkerOnEntityTickUpdateProcedure')
        self.assertEqual([i['offset'] for i in b if '.setBaseValue(' in str(i['operand'])],[609,1438])
        cs=self.row('centipede_stalker_native_silk_vertical_control_and_ai_commands')['scalable_parameter_candidates']
        self.assertEqual(sum(c['primitive']=='NATIVE_STEP_HEIGHT' for c in cs),1)
        b=self.body('CentipedeStalkerEntity','aiStep')
        self.assertEqual(sum('.updateSwingTime(' in str(i['operand']) for i in b),8)
        self.assertFalse(any('.doHurtTarget(' in str(i['operand']) for i in b))

    def test_stalker_delayed_noai_can_outlive_admission(self):
        b=self.body('CentipedeStalkerOnEntityTickUpdateProcedure');by={i['offset']:i for i in b}
        self.assertEqual((by[1607]['operand'],by[1619]['branch_target']),(10,1728))
        self.assertEqual(by[1722]['operand'],'data merge entity @s {NoAI:0}')
        b=self.body('CentipedeStalkerOnEntityTickUpdateProcedure','lambda$execute$13')
        self.assertTrue(any(i['operand']=='data merge entity @s {NoAI:1}' for i in b))
        self.assertFalse(any(x in str(i['operand']) for i in b for x in ('.hasEffect(','.isAlive(','.isEmptyBlock(')))

    def test_breacher_contact_and_melee_share_one_attribute(self):
        b=self.body('TinyCentipedeBreacherEntity$1','tick')
        self.assertTrue(any('AABB.intersects(' in str(i['operand']) for i in b))
        j=next(j for j,i in enumerate(b) if '.doHurtTarget(' in str(i['operand']))
        self.assertEqual(b[j+1]['opcode'],'0x57')
        self.assertFalse(any(x in str(i['operand']) for i in b for x in ('isTimeToAttack','hasLineOfSight')))
        b=self.body('TinyCentipedeBreacherEntity$2','canPerformAttack')
        self.assertTrue(any('isTimeToAttack(' in str(i['operand']) for i in b))
        cs=self.row('tiny_centipede_breacher_native_contact_target_and_lifecycle')['scalable_parameter_candidates']
        self.assertEqual(sum(c['primitive']=='NATIVE_CONTACT_AND_CONDITIONAL_MELEE' for c in cs),1)

    def test_breacher_nearest_command_is_not_owner_or_actor_link(self):
        b=self.body('TinyCentipedeBreacherOnEntityTickUpdateProcedure')
        commands=[i['operand'] for i in b if isinstance(i['operand'],str) and i['operand'].startswith('execute as @e')]
        self.assertEqual(len(commands),2)
        self.assertTrue(all('limit=1,sort=nearest' in s for s in commands))
        self.assertTrue(any(i['operand']=='arphex' for i in b))
        self.assertFalse(any(i['operand']=='arphexclimber' or '.setOwner(' in str(i['operand']) for i in b))


class ButterflyBulwarkNativeTests(NativeContractHarness, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch=read_json(OUT/'arphex-r2m5n-butterfly-bulwark-native-contracts.json')
        cls.native=read_json(OUT/'native-evidence/arphex-butterfly-bulwark-native-families.json')
        cls.census=read_json(OUT/'arphex-combat-census.json')

    def test_exact_native_consumers_and_three_roots(self):
        validate_batch(self.batch,self.prior(),self.census)
        self.assertEqual((len(self.batch['effects']),len(self.batch['closed_actor_callback_entries'])),(3,3))
        self.assertEqual(sum(len(c['parameters']) for r in self.batch['effects']
                             for c in r['scalable_parameter_candidates']),32)
        self.assertEqual((len(self.native['witnesses']),sum(len(w['methods']) for w in self.native['witnesses'])),(26,182))
        self.assertFalse(self.batch['whole_mod_complete'])

    def test_butterfly_goals_have_no_attack_producer(self):
        for a in ('ButterflyBewitcherEntity','ButterflyBewitcherGiantEntity'):
            b=self.body(a,'registerGoals')
            self.assertFalse(any(x in str(i['operand']) for i in b
                                 for x in ('MeleeAttackGoal','NearestAttackableTargetGoal')))
            self.assertTrue(any('BreedGoal.<init>' in str(i['operand']) for i in b))
        cs=[c for r in self.batch['effects'] if 'butterfly' in r['id']
            for c in r['scalable_parameter_candidates']]
        self.assertFalse(any(c['primitive']=='NATIVE_CONDITIONAL_MELEE' for c in cs))

    def test_cross_clock_destinations_and_order_are_native(self):
        ordinary={i['offset']:i for i in self.body('ButterflyTickProcedure')}
        giant={i['offset']:i for i in self.body('ButterflyGiantTickProcedure')}
        self.assertEqual((ordinary[1390]['operand'],ordinary[1397]['operand']),('yboost','flyboost'))
        self.assertEqual((giant[998]['operand'],giant[1005]['operand']),('yboost','flyboost'))
        self.assertIn('.putDouble(',ordinary[1404]['operand'])
        self.assertIn('.putDouble(',giant[1012]['operand'])
        self.assertLess(991,1404)  # ordinary boost decrement BEFORE yboost copy
        self.assertLess(1012,1072) # giant boost decrement AFTER yboost copy
        for off in (681,1451):
            self.assertIn('.putDouble(',ordinary[off]['operand'])
        self.assertEqual((ordinary[1417]['operand'],ordinary[1464]['operand']),(1000.,0.))

    def test_nonempty_food_has_one_live_heal_and_unreachable_duplicate(self):
        b=self.body('ButterflyBewitcherGiantEntity','isFood')
        self.assertEqual(sum('Blocks.' in str(i['operand']) for i in b),13)
        b=self.body('ButterflyBewitcherGiantEntity','mobInteract');by={i['offset']:i for i in b}
        self.assertEqual([i['offset'] for i in b if '.heal(' in str(i['operand'])],[168,217])
        self.assertEqual((by[162]['operand'],by[214]['operand']),(1.,4.))
        # Same false food/health predicates lead directly to their identical retest.
        self.assertEqual((by[119]['branch_target'],by[131]['branch_target']),(186,186))
        self.assertEqual(by[116]['operand'],by[188]['operand'])
        self.assertEqual(by[123]['operand'],by[195]['operand'])
        self.assertEqual(by[127]['operand'],by[199]['operand'])
        self.assertFalse(any('.heal(' in str(i['operand']) or '.usePlayerItem(' in str(i['operand'])
                             for i in b if 186<=i['offset']<206))
        cs=self.row('giant_butterfly_native_owner_aura_food_heal_and_riding')['scalable_parameter_candidates']
        self.assertEqual([c['native_consumer']['offset'] for c in cs if c['primitive']=='NATIVE_FOOD_HEAL'],[168])

    def test_regeneration_requires_present_effect_and_native_constructor(self):
        b=self.body('ButterflyGiantTickProcedure');by={i['offset']:i for i in b}
        self.assertIn('.hasEffect(',by[1421]['operand'])
        self.assertEqual((by[1424]['opcode'],by[1424]['branch_target']),('0x99',1472))
        self.assertEqual((by[1462]['operand'],by[1464]['operand']),(60,0))
        self.assertTrue(str(by[1465]['operand']).endswith('(Lnet/minecraft/core/Holder;II)V'))

    def test_giant_rider_vector_precedes_owner_ejection(self):
        b=self.body('ButterflyGiantTickProcedure')
        own=next(i['offset'] for i in b if '.isOwnedBy(' in str(i['operand']))
        eject=next(i['offset'] for i in b if '.stopRiding(' in str(i['operand']))
        self.assertLess(822,own);self.assertLess(own,eject)
        b=self.body('ButterflyBewitcherGiantEntity','mobInteract')
        j=next(j for j,i in enumerate(b) if '.startRiding(' in str(i['operand']))
        self.assertEqual(b[j+1]['opcode'],'0x57')
        self.assertFalse(self.row('giant_butterfly_native_owner_aura_food_heal_and_riding')['native_actor_context']['no_owner_assignment_in_callbacks'])

    def test_bulwark_parent_goals_and_native_melee_not_replaced(self):
        b=self.body('BeetleBulwarkEntity','registerGoals')
        self.assertEqual(b[1]['operand'],'net/minecraft/world/entity/monster/Spider.registerGoals()V')
        self.assertTrue(any('BeetleTickMiteEntity' in str(i['operand']) for i in b))
        b=self.body('BeetleBulwarkEntity$1','canPerformAttack')
        self.assertTrue(any(i['operand']==.49 for i in b))
        self.assertTrue(any('hasLineOfSight(' in str(i['operand']) for i in b))
        cs=self.row('bulwark_native_spider_variant_status_flight_and_jockey_lifecycle')['scalable_parameter_candidates']
        self.assertEqual(sum(c['primitive']=='NATIVE_CONDITIONAL_MELEE' for c in cs),1)

    def test_bulwark_typed_statuses_and_step_override(self):
        b=self.body('RhinoBeetleEntityTickProcedure');by={i['offset']:i for i in b}
        self.assertEqual([i['offset'] for i in b if '.addEffect(' in str(i['operand'])],[153,200,290,337,599,668])
        for off,d,a in [(153,60,0),(200,60,0),(290,60,0),(337,60,1),(599,60,0),(668,60,5)]:
            j=next(j for j,i in enumerate(b) if i['offset']==off)
            ctor=j-1
            nums=[i['operand'] for i in b[ctor-4:ctor]]
            self.assertEqual(nums,[d,a,0,0])
        self.assertEqual(by[1064]['operand'],1.)
        self.assertIn('.setBaseValue(',by[1065]['operand'])

    def test_bulwark_first_passenger_cleanup_latch_not_admission(self):
        b=self.body('RhinoBeetleEntityTickProcedure');by={i['offset']:i for i in b}
        self.assertEqual((by[1078]['opcode'],by[1078]['branch_target']),('0x9a',1141))
        self.assertEqual(by[1102]['operand'],'net/minecraft/world/entity/monster/Skeleton')
        self.assertIn('.discard(',by[1127]['operand'])
        self.assertEqual((by[1135]['operand'],by[1137]['operand']),('despawn_skeleton',1))
        self.assertLess(1127,1138)
        b=self.body('BeetleBulwarkEntity','finalizeSpawn')
        parent=next(i['offset'] for i in b if 'Spider.finalizeSpawn(' in str(i['operand']))
        child=next(i['offset'] for i in b if 'OnInitialEntitySpawnProcedure.execute(' in str(i['operand']))
        self.assertLess(parent,child)


class GroundFlyingNativeTests(NativeContractHarness, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch=read_json(OUT/'arphex-r2m5m-common-ground-and-flying-native-contracts.json')
        cls.native=read_json(OUT/'native-evidence/arphex-common-ground-flying-native-families.json')
        cls.census=read_json(OUT/'arphex-combat-census.json')

    def test_shared_native_consumers_and_ten_roots(self):
        validate_batch(self.batch,self.prior(),self.census)
        self.assertEqual((len(self.batch['effects']),len(self.batch['closed_actor_callback_entries'])),(5,10))
        self.assertEqual(sum(len(c['parameters']) for r in self.batch['effects']
                             for c in r['scalable_parameter_candidates']),75)
        self.assertEqual((len(self.native['witnesses']),sum(len(w['methods']) for w in self.native['witnesses'])),(44,299))
        self.assertFalse(self.batch['whole_mod_complete'])

    def test_shared_ground_callback_and_zero_base_native_melee(self):
        for a in ('ScorpionStrikerEntity','ScorpionLarvaeEntity','LongLegsEntity','LongLegsTinyEntity'):
            self.assertEqual(sum('SunScorpionOnEntityTickUpdateProcedure.execute(' in str(i['operand'])
                                 for i in self.body(a,'baseTick')),1)
        b=self.body('LongLegsTinyEntity','createAttributes')
        j=next(j for j,i in enumerate(b) if 'Attributes.ATTACK_DAMAGE' in str(i['operand']))
        self.assertEqual(b[j+1]['operand'],0.)
        b=self.body('LongLegsTinyEntity$1','canPerformAttack')
        self.assertTrue(any('isTimeToAttack()' in str(i['operand']) for i in b))
        self.assertTrue(any('hasLineOfSight(' in str(i['operand']) for i in b))
        # Existing explicit native target-event contribution is reused, not duplicated.
        self.assertIn('arphex:target_event_small_actor_movement',self.row('shared_scorpion_longlegs_native_climbing_spawn_and_melee')['canonical_contract_reuse'])

    def test_longlegs_silk_has_type_guard_not_scorpion_payload(self):
        b=self.body('SunScorpionOnEntityTickUpdateProcedure')
        self.assertEqual([i['operand'] for i in b if i['opcode']=='0xc1' and
                          str(i['operand']).startswith('net/arphex/entity/')],
                         ['net/arphex/entity/LongLegsTinyEntity','net/arphex/entity/LongLegsEntity','net/arphex/entity/LongLegsTinyEntity'])
        self.assertFalse(any('MobEffects.POISON' in str(i['operand']) or '.hurt(' in str(i['operand']) for i in b))
        self.assertTrue(any('ArphexModMobEffects.SPIDER_SILK_TOUCH' in str(i['operand']) for i in b))

    def test_larva_delayed_strength_separate_from_shade_inheritance(self):
        b=self.body('SunScorpionTinyOnInitialEntitySpawnProcedure','lambda$execute$2')
        presence=next(i for i in b if '.isEmpty()' in str(i['operand']))
        j=b.index(presence)
        self.assertEqual(b[j+1]['opcode'],'0x9a')  # absent goes to independent random arm
        self.assertTrue(any('MobEffects.DAMAGE_BOOST' in str(i['operand']) for i in b))
        ctor=next(j for j,i in enumerate(b) if 'MobEffectInstance.<init>' in str(i['operand']))
        self.assertEqual([i['operand'] for i in b[ctor-4:ctor]],[99999,0,0,0])
        self.assertFalse(any('.isAlive(' in str(i['operand']) or '.setOwner(' in str(i['operand']) for i in b))

    def test_millipede_signed_velocity_not_magnitude_and_radius_not_auto_active(self):
        b=self.body('MillipedeTickProcedure')
        velocity=[i for i in b if i['operand'] in ('net/minecraft/world/phys/Vec3.x()D','net/minecraft/world/phys/Vec3.z()D')]
        self.assertEqual(len(velocity),2)
        self.assertFalse(any('Math.abs(' in str(i['operand']) or 'Vec3.length(' in str(i['operand']) for i in b))
        r=self.row('millipede_native_asymmetric_motion_resistance_and_melee')
        self.assertFalse(any(c['primitive']=='SHARED_CLIMB_STATE' for c in r['scalable_parameter_candidates']))
        self.assertFalse(any(i['operand']=='arphexclimber' for i in b))
        b=self.body('CentipedeStalkerOnInitialEntitySpawnProcedure')
        self.assertTrue(any(i['opcode']=='0xc1' and i['operand']=='net/arphex/entity/CentipedeStalkerEntity' for i in b))
        self.assertFalse(any(i['operand']=='arphexclimber' for i in b))

    def test_hornet_shiny_guard_does_not_follow_texture_only_write(self):
        b=self.body('HornetShinyProcedure')
        self.assertTrue(any('DATA_shiny' in str(i['operand']) for i in b))
        self.assertFalse(any('.getTexture(' in str(i['operand']) for i in b))
        b=self.body('HornetHarbingerOnInitialEntitySpawnProcedure','lambda$execute$2')
        self.assertTrue(any('.setTexture(' in str(i['operand']) for i in b))
        self.assertFalse(any('DATA_shiny' in str(i['operand']) or 'SynchedEntityData.set(' in str(i['operand']) for i in b))
        b=self.body('GiantHornetHarbingerSpawnProcedure')
        self.assertEqual(sum('EntityType.spawn(' in str(i['operand']) for i in b),3)
        self.assertFalse(any('.setOwner(' in str(i['operand']) for i in b))

    def test_longfly_positive_chaos_clock_reads_updated_flyboost(self):
        b=self.body('LongFlyTickProcedure');by={i['offset']:i for i in b}
        self.assertEqual((by[785]['operand'],by[792]['operand']),('chaostime','flyboost'))
        self.assertEqual((by[797]['operand'],by[798]['opcode']),(1.,'0x67'))
        self.assertIn('.putDouble(',by[799]['operand'])
        self.assertLess(739,799)  # prior native flyboost decrement
        self.assertFalse(any('.hurt(' in str(i['operand']) for i in b))

    def test_dragonfly_contact_ignores_return_without_attack_goal_clock(self):
        b=self.body('DragonflyDreadnoughtEntity$1','tick')
        self.assertTrue(any('AABB.intersects(' in str(i['operand']) for i in b))
        j=next(j for j,i in enumerate(b) if '.doHurtTarget(' in str(i['operand']))
        self.assertEqual(b[j+1]['opcode'],'0x57')
        self.assertFalse(any(x in str(i['operand']) for i in b for x in ('isTimeToAttack','hasLineOfSight','resetAttackCooldown')))
        b=self.body('DragonflyDreadnoughtEntity','registerGoals')
        self.assertFalse(any('MeleeAttackGoal' in str(i['operand']) for i in b))
        self.assertIn('arphex:dragonfly_dreadnought_source_feedback',self.row('dragonfly_native_contact_flight_and_source_stance')['canonical_contract_reuse'])

    def test_dragonfly_water_is_delayed_and_continuous_phase_precedes_update(self):
        b=self.body('DragonflyTickProcedure');by={i['offset']:i for i in b}
        self.assertEqual([i['offset'] for i in b if '.queueServerWork(' in str(i['operand'])],[29,1247])
        self.assertIn('.setDeltaMovement(',by[1227]['operand'])
        self.assertIn('.putDouble(',by[1275]['operand'])
        self.assertFalse(any('.setDeltaMovement(' in str(i['operand']) for i in b if 1230<=i['offset']<=1250))
        b=self.body('DragonflyTickProcedure','lambda$execute$1')
        self.assertTrue(any('.getDeltaMovement(' in str(i['operand']) for i in b))
        self.assertFalse(any(x in str(i['operand']) for i in b for x in ('.isInWater(','.isAlive(','.level(')))
        r=self.row('dragonfly_native_contact_flight_and_source_stance')
        self.assertEqual(sum(c['primitive']=='CONTINUOUS_FLIGHT_MOVEMENT' for c in r['scalable_parameter_candidates']),1)


class TermiteColonyNativeTests(NativeContractHarness, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch=read_json(OUT/'arphex-r2m5l-termite-colony-native-contracts.json')
        cls.native=read_json(OUT/'native-evidence/arphex-termite-colony-native-family.json')
        cls.census=read_json(OUT/'arphex-combat-census.json')

    def test_exact_native_consumers_and_six_related_roots(self):
        validate_batch(self.batch,self.prior(),self.census)
        self.assertEqual((len(self.batch['effects']),len(self.batch['closed_actor_callback_entries'])),(6,6))
        self.assertEqual(sum(len(c['parameters']) for r in self.batch['effects']
                             for c in r['scalable_parameter_candidates']),48)
        self.assertEqual((len(self.native['witnesses']),sum(len(w['methods']) for w in self.native['witnesses'])),(42,220))
        self.assertFalse(any(r.get('candidate_additions') for r in self.batch['record_refinements']))
        self.assertFalse(self.batch['whole_mod_complete'])

    def test_shared_healing_only_worker_before_admission(self):
        b=self.body('TermiteTunnelerWorkerEntity','hurt')
        helper=next(i['offset'] for i in b if 'AntArsonistWorkerEntityIsHurtProcedure.execute(' in str(i['operand']))
        self.assertLess(helper,next(i['offset'] for i in b if i['operand']=='net/minecraft/world/damagesource/DamageSource.getDirectEntity()Lnet/minecraft/world/entity/Entity;'))
        for a in ('TermiteTunnelerSoldierEntity','TermiteTunnelerKingEntity','TermiteTunnelerQueenEntity'):
            self.assertFalse(any('IsHurtProcedure.execute(' in str(i['operand']) for i in self.body(a,'hurt')))
        candidates=[c for r in self.batch['effects'] for c in r['scalable_parameter_candidates']]
        self.assertFalse(any(c['primitive']=='MOB_EFFECT_INSTANT_HEALTH' for c in candidates))
        previous=read_json(OUT/'mod-reviews/arphex.json')
        consumers=[c for r in previous['effects'] for c in r['scalable_parameter_candidates']
                   if c['native_consumer']['entry'].endswith('/AntArsonistWorkerEntityIsHurtProcedure.class')]
        self.assertEqual(len(consumers),1)

    def test_worker_entry_physics_precedes_clock_and_other_recipient_write(self):
        b=self.body('TermiteTunnelerWorkerOnEntityTickUpdateProcedure');by={i['offset']:i for i in b}
        self.assertIn('.noPhysicsZ',by[429]['operand'])
        self.assertIn('.setNoGravity(',by[435]['operand'])
        self.assertIn('.putBoolean(',by[559]['operand'])
        self.assertIn('.putBoolean(',by[596]['operand'])
        # Native writes later target-nearest Worker's tag, not the actor parameter.
        j=next(j for j,i in enumerate(b) if i['offset']==1853)
        self.assertTrue(any('Stream.findFirst(' in str(i['operand']) for i in b[j-10:j]))
        self.assertEqual(b[j-2]['operand'],'tunneling')
        self.assertEqual(b[j-1]['operand'],0)
        self.assertFalse(any('.destroyBlock(' in str(i['operand']) or '.setBlock(' in str(i['operand'])
                             for i in b))

    def test_alate_delayed_vectors_have_no_native_recheck(self):
        b=self.body('TermiteTunnelerAlateOnEntityTickUpdateProcedure');by={i['offset']:i for i in b}
        self.assertEqual([i['offset'] for i in b if '.queueServerWork(' in str(i['operand'])],[288,621])
        self.assertEqual((by[280]['operand'],by[613]['operand']),(10,17))
        for m in ('lambda$execute$0','lambda$execute$1'):
            b=self.body('TermiteTunnelerAlateOnEntityTickUpdateProcedure',m)
            self.assertTrue(any('.setDeltaMovement(' in str(i['operand']) for i in b))
            self.assertFalse(any(x in str(i['operand']) for i in b
                                 for x in ('.isAlive(','.level(','.getTarget(','.getBoolean(')))
        b=self.body('TermiteTunnelerAlateOnEntityTickUpdateProcedure','lambda$execute$0')
        self.assertTrue(any('.getYRot()' in str(i['operand']) for i in b))
        self.assertTrue(any('Vec3.y()' in str(i['operand']) for i in b))

    def test_king_native_taming_is_distinct_from_empty_food(self):
        b=self.body('TermiteTunnelerKingEntity','isFood')
        self.assertEqual(b[0]['operand'],'java/util/List.of()Ljava/util/List;')
        self.assertTrue(any('List.contains(' in str(i['operand']) for i in b))
        b=self.body('TermiteTunnelerKingOnEntityTickUpdateProcedure');by={i['offset']:i for i in b}
        self.assertIn('DATA_larvae',by[677]['operand'])
        self.assertIn('.tame(Lnet/minecraft/world/entity/player/Player;)V',by[989]['operand'])
        self.assertFalse(any('.getOwner(' in str(i['operand']) for i in b if 677<i['offset']<989))
        b=self.body('TermiteTunnelerKingEntity$5','canPerformAttack')
        self.assertTrue(any('isTimeToAttack()' in str(i['operand']) for i in b))
        self.assertFalse(any('DATA_larvae' in str(i['operand']) or 'DATA_following' in str(i['operand']) for i in b))

    def test_queen_has_no_local_attack_goal_or_flag_alias(self):
        b=self.body('TermiteTunnelerQueenEntity','<init>')
        j=next(j for j,i in enumerate(b) if '.setNoAi(' in str(i['operand']))
        self.assertEqual(b[j-1]['operand'],1)
        w=next(w for w in self.native['witnesses'] if w['entry'].endswith('/TermiteTunnelerQueenEntity.class'))
        self.assertFalse(any(m['name']=='registerGoals' for m in w['methods']))
        b=self.body('TermiteTunnelerQueenOnEntityTickUpdateProcedure')
        self.assertTrue(any('PlayerVariables.totemfatigueZ' in str(i['operand']) for i in b))
        self.assertFalse(any(i['operand']=='queenslowtotem' for i in b))
        self.assertTrue(any('MobEffects.DIG_SLOWDOWN' in str(i['operand']) for i in b))  # admission read
        constructors=[j for j,i in enumerate(b) if 'MobEffectInstance.<init>' in str(i['operand'])]
        self.assertEqual(len(constructors),1)
        self.assertTrue(any('MobEffects.REGENERATION' in str(i['operand'])
                            for i in b[constructors[0]-8:constructors[0]]))
        r=self.row('termite_queen_native_summon_regeneration_and_flag_delivery')
        self.assertFalse(any(c['primitive']=='NATIVE_CONDITIONAL_MELEE' for c in r['scalable_parameter_candidates']))

    def test_queen_death_nearest_query_not_spawn_reference(self):
        b=self.body('TermiteTunnelerQueenEntity','die')
        self.assertLess(next(i['offset'] for i in b if '.die(' in str(i['operand'])),
                        next(i['offset'] for i in b if 'TermiteTunnelerQueenEntityDiesProcedure.execute(' in str(i['operand'])))
        b=self.body('TermiteTunnelerQueenEntityDiesProcedure','lambda$execute$2')
        self.assertEqual(sum('.getEntitiesOfClass(' in str(i['operand']) for i in b),2)
        self.assertTrue(any('DATA_larvae' in str(i['operand']) for i in b))
        self.assertFalse(any('.setOwner(' in str(i['operand']) or '.isAlive(' in str(i['operand']) for i in b))

    def test_replacement_latch_discard_two_distinct_rolls_and_unowned_children(self):
        b=self.body('RandomTermiteOnEntityTickUpdateProcedure')
        latch=next(i['offset'] for i in b if '.putBoolean(' in str(i['operand']))
        discard=next(i['offset'] for i in b if '.discard(' in str(i['operand']))
        rolls=[i['offset'] for i in b if 'Mth.nextInt(' in str(i['operand'])]
        self.assertEqual(rolls,[51,118])
        self.assertLess(latch,discard);self.assertLess(discard,rolls[0])
        self.assertEqual([i['offset'] for i in b if 'EntityType.spawn(' in str(i['operand'])],[92,215,270])
        self.assertFalse(any('.setOwner(' in str(i['operand']) or '.tame(' in str(i['operand']) for i in b))


class AntColonyNativeTests(NativeContractHarness, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch=read_json(OUT/'arphex-r2m5k-ant-colony-native-contracts.json')
        cls.native=read_json(OUT/'native-evidence/arphex-ant-colony-native-family.json')
        cls.census=read_json(OUT/'arphex-combat-census.json')

    def test_colony_bindings_and_existing_producer_reuse(self):
        validate_batch(self.batch,self.prior(),self.census)
        self.assertEqual((len(self.batch['effects']),len(self.batch['closed_actor_callback_entries'])),(3,3))
        self.assertEqual(sum(len(c['parameters']) for r in self.batch['effects']
                             for c in r['scalable_parameter_candidates']),64)
        self.assertEqual((len(self.native['witnesses']),sum(len(w['methods']) for w in self.native['witnesses'])),(55,278))
        self.assertEqual(len(self.batch['record_refinements']),2)
        self.assertTrue(all(not r.get('candidate_additions') for r in self.batch['record_refinements']))
        self.assertFalse(self.batch['whole_mod_complete'])

    def test_all_empty_food_predicates_disable_generated_feeding(self):
        for a in ('AntArsonistSoldierEntity','AntArsonistWorkerEntity','AntArsonistAlateQueenEntity'):
            b=self.body(a,'isFood')
            self.assertEqual(b[0]['operand'],'java/util/List.of()Ljava/util/List;')
            self.assertTrue(any('List.contains(' in str(i['operand']) for i in b))
            self.assertFalse(any('/Items.' in str(i['operand']) or 'ArphexModItems.' in str(i['operand']) for i in b))
            b=self.body(a,'mobInteract')
            self.assertEqual(sum('.heal(' in str(i['operand']) for i in b),2)  # present but inactive
            candidates=[c for r in self.batch['effects'] for c in r['scalable_parameter_candidates']]
            self.assertFalse(any(c['native_consumer']['entry'].endswith('/'+a+'.class')
                                 and c['native_consumer']['methods']==['mobInteract'] for c in candidates))
        global_review=read_json(OUT/'mod-reviews/arphex.json')
        feed=next(r for r in global_review['effects'] if r['id']=='arphex:interaction_feeding_native_regeneration')
        self.assertTrue(any(p['entry'].endswith('/RightClickEntityProcedure.class') for p in feed['implementation']))

    def test_pre_admission_reaction_is_not_hurt_return_dependent(self):
        for actor,helper in [('AntArsonistSoldierEntity','AntArsonistSoldierEntityIsHurtProcedure'),
                             ('AntArsonistWorkerEntity','AntArsonistWorkerEntityIsHurtProcedure')]:
            b=self.body(actor,'hurt')
            call=next(i['offset'] for i in b if helper+'.execute(' in str(i['operand']))
            self.assertLess(call,next(i['offset'] for i in b if 'DamageTypes.IN_FIRE' in str(i['operand'])))
        b=self.body('AntArsonistSoldierEntityIsHurtProcedure')
        self.assertTrue(any('MobEffects.DAMAGE_RESISTANCE' in str(i['operand']) for i in b))
        self.assertTrue(any('DATA_larvae' in str(i['operand']) for i in b))
        self.assertTrue(any('ArphexModEntities.ANT_ARSONIST_DRONE' in str(i['operand']) for i in b))
        self.assertEqual(sum('EntityType.spawn(' in str(i['operand']) for i in b),1)
        self.assertFalse(any('.setOwner(' in str(i['operand']) for i in b))
        b=self.body('AntArsonistWorkerEntityIsHurtProcedure')
        self.assertTrue(any('.isInWall()' in str(i['operand']) for i in b))
        self.assertTrue(any('MobEffects.HEAL' in str(i['operand']) for i in b))
        self.assertFalse(any('.heal(' in str(i['operand']) for i in b))

    def test_larvae_queue_clears_only_state_without_lifecycle_recheck(self):
        for helper in ('AntArsonistSoldierOnEntityTickUpdateProcedure','AntArsonistWorkerOnEntityTickUpdateProcedure'):
            b=self.body(helper)
            queues=[j for j,i in enumerate(b) if '.queueServerWork(' in str(i['operand'])]
            self.assertEqual(len(queues),1)
            self.assertTrue(any(i['operand']==800 for i in b[queues[0]-5:queues[0]]))
            delayed=[m for w in self.native['witnesses'] if w['entry'].endswith('/'+helper+'.class')
                     for m in w['methods'] if 'lambda$execute$' in m['name']
                     and any('SynchedEntityData.set(' in str(i['operand']) for i in m['instructions'])]
            self.assertEqual(len(delayed),1)
            b=delayed[0]['instructions']
            self.assertTrue(any('DATA_larvae' in str(i['operand']) for i in b))
            self.assertFalse(any('.isAlive(' in str(i['operand']) or '.level(' in str(i['operand']) for i in b))
        for a in ('AntArsonistSoldierEntity$1','AntArsonistWorkerEntity$3'):
            b=self.body(a,'canPerformAttack')
            self.assertTrue(any('isTimeToAttack()' in str(i['operand']) for i in b))
            self.assertFalse(any('DATA_larvae' in str(i['operand']) for i in b))

    def test_actual_taming_differs_from_spawn_larvae_marker(self):
        for helper in ('SoldierSpawnProcedure','AntArsonistWorkerOnInitialEntitySpawnProcedure'):
            b=self.body(helper)
            self.assertTrue(any('DATA_larvae' in str(i['operand']) for i in b))
            self.assertFalse(any('.tame(' in str(i['operand']) for i in b))
        for helper in ('AntArsonistSoldierOnEntityTickUpdateProcedure','AntArsonistWorkerOnEntityTickUpdateProcedure'):
            b=self.body(helper)
            self.assertTrue(any('TamableAnimal.tame(Lnet/minecraft/world/entity/player/Player;)V' in str(i['operand']) for i in b))
            self.assertTrue(any(i['opcode']=='0xc1' and i['operand']=='net/minecraft/world/entity/player/Player' for i in b))
        b=self.body('AntOwnedProcedure')
        self.assertTrue(any('DATA_following' in str(i['operand']) for i in b))
        self.assertTrue(any('Mob.getTarget(' in str(i['operand']) for i in b))

    def test_queen_shape_strict_boundary_differs_from_aura_inclusive(self):
        b=self.body('AntQueenHitboxProcedure');by={i['offset']:i for i in b}
        self.assertEqual((by[40]['operand'],by[42]['opcode']),(36000,'0xa4'))  # <= skips mature
        self.assertEqual([i['operand'] for i in b if i['opcode']=='0x14'],[2.45,1.95,1.46,.96])
        b=self.body('AntArsonistQueenOnEntityTickUpdateProcedure');by={i['offset']:i for i in b}
        self.assertEqual((by[1432]['operand'],by[1435]['opcode']),(36000,'0xa1'))  # < skips mature
        self.assertLess(122,1795)  # old minspawnwait sampled before current tier binding
        holders=[i['operand'].split('.')[-1].split('Lnet/')[0] for i in b if 'ArphexModEntities.ANT_' in str(i['operand'])]
        self.assertEqual(holders,['ANT_ARSONIST','ANT_ARSONIST','ANT_ARSONIST_SOLDIER',
                                  'ANT_ARSONIST','ANT_ARSONIST','ANT_ARSONIST_WORKER'])
        self.assertFalse(any('.setOwner(' in str(i['operand']) or '.tame(' in str(i['operand']) for i in b))
        for r in self.batch['effects']:
            for c in r['scalable_parameter_candidates']:
                component=next(x for x in r['components'] if x['primitive']==c['primitive'])
                self.assertFalse(any(component['numerical_parameters'].get(k)==-1 for k in c['parameters']))

    def test_worker_escape_has_no_invented_griefing_guard(self):
        b=self.body('AntArsonistWorkerOnEntityTickUpdateProcedure')
        self.assertFalse(any('GameRules.RULE_MOBGRIEFING' in str(i['operand'])
                             or 'ConfigurationSettingsConfiguration.ARPHEX_GRIEFING' in str(i['operand']) for i in b))
        self.assertTrue(any('ArphexModBlocks.ANT_SHIELD_TEMPORARY' in str(i['operand']) for i in b))
        self.assertEqual([i['offset'] for i in b if i['operand']=='net/minecraft/world/entity/Entity.teleportTo(DDD)V'],
                         [5574,5791,5990,6189,6388,6544])
        self.assertTrue(any('.isInWall()' in str(i['operand']) and i['offset']>6388 for i in b))
        r=self.row('ant_worker_native_larvae_owner_target_and_pre_admission_heal')
        c=next(c for c in r['scalable_parameter_candidates'] if c['parameters']==['escape_vertical'])
        self.assertEqual(len(c['additional_consumer_sites']),5)


class CommonInsectNativeTests(NativeContractHarness, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch=read_json(OUT/'arphex-r2m5j-common-insect-native-families.json')
        cls.native=read_json(OUT/'native-evidence/arphex-common-insect-native-family.json')
        cls.census=read_json(OUT/'arphex-combat-census.json')

    def test_six_roots_share_one_real_callback_registration(self):
        validate_batch(self.batch,self.prior(),self.census)
        self.assertEqual((len(self.batch['effects']),len(self.batch['closed_actor_callback_entries'])),(3,6))
        self.assertEqual(sum(len(c['parameters']) for r in self.batch['effects']
                             for c in r['scalable_parameter_candidates']),48)
        for name in ('AntArsonistEntity','BloodWormEntity','StickBugEntity','SilverfishSpectreEntity'):
            b=self.body(name,'baseTick')
            self.assertEqual(sum('BloodWormOnEntityTickUpdateProcedure.execute(' in str(i['operand']) for i in b),1)
        self.assertEqual(len(self.row('shared_ant_bloodworm_stick_silverfish_native_callbacks')['native_actor_variants']),4)
        self.assertFalse(self.batch['whole_mod_complete'])

    def test_queen_presence_two_delays_are_not_owner_transport(self):
        b=self.body('BloodWormOnEntityTickUpdateProcedure')
        self.assertEqual([i['offset'] for i in b if '.queueServerWork(' in str(i['operand'])],[29,97])
        self.assertTrue(any(str(i['operand']).endswith('/AntArsonistAlateQueenEntity') for i in b))
        flag=self.body('BloodWormOnEntityTickUpdateProcedure','lambda$execute$0')
        self.assertEqual([i['operand'] for i in flag if i['opcode']=='0x12'],['notfromqueen'])
        self.assertFalse(any('.level(' in str(i['operand']) or '.isAlive(' in str(i['operand']) for i in flag))
        discard=self.body('BloodWormOnEntityTickUpdateProcedure','lambda$execute$2')
        self.assertTrue(any('.discard(' in str(i['operand']) for i in discard))
        self.assertFalse(any('.getEntities' in str(i['operand']) or '.isAlive(' in str(i['operand']) for i in discard))
        self.assertFalse(any('.setOwner(' in str(i['operand']) for i in b))

    def test_resistance_skips_only_status_package_then_step_write(self):
        b=self.body('BloodWormOnEntityTickUpdateProcedure');by={i['offset']:i for i in b}
        self.assertEqual((by[1927]['opcode'],by[1927]['branch_target']),('0x9a',2081))
        for off,holder in ((1970,'INVISIBILITY'),(2017,'WEAKNESS'),(2074,'DAMAGE_RESISTANCE')):
            j=next(j for j,i in enumerate(b) if i['offset']==off)
            self.assertIn('MobEffectInstance.<init>',b[j]['operand'])
            self.assertTrue(any('MobEffects.'+holder in str(i['operand']) for i in b[j-10:j]))
        self.assertIn('AttributeInstance.setBaseValue(D)V',by[2114]['operand'])
        j=next(j for j,i in enumerate(b) if i['offset']==2114)
        self.assertEqual(b[j-1]['operand'],1.)
        self.assertTrue(any('Attributes.STEP_HEIGHT' in str(i['operand']) for i in b[0:j]))

    def test_stick_attribute_does_not_create_offense_and_hurt_helper_is_particles(self):
        b=self.body('StickBugEntity','registerGoals')
        self.assertFalse(any('MeleeAttackGoal' in str(i['operand']) or 'TargetGoal' in str(i['operand']) for i in b))
        self.assertTrue(any('RandomLookAroundGoal' in str(i['operand']) for i in b))
        candidates=self.row('shared_ant_bloodworm_stick_silverfish_native_callbacks')['scalable_parameter_candidates']
        self.assertFalse(any(c['native_consumer']['entry'].endswith('/StickBugEntity.class') for c in candidates))
        b=self.body('BloodWormEntityIsHurtProcedure')
        self.assertTrue(any('.sendParticles(' in str(i['operand']) for i in b))
        self.assertFalse(any(t in str(i['operand']) for i in b
                             for t in ('.hurt(','.setDeltaMovement(','.heal(','.addEffect(')))

    def test_locust_contact_uses_intersection_without_goal_clock_or_los(self):
        b=self.body('LocustLandscourgeEntity$1','tick');by={i['offset']:i for i in b}
        self.assertIn('AABB.intersects(',by[19]['operand'])
        self.assertEqual(by[22]['branch_target'],37)
        self.assertIn('.doHurtTarget(',by[30]['operand'])
        self.assertEqual(by[33]['opcode'],'0x57')  # return deliberately ignored
        self.assertFalse(any('isTimeToAttack' in str(i['operand']) or 'hasLineOfSight' in str(i['operand']) for i in b))
        goals=self.body('LocustLandscourgeEntity','registerGoals')
        self.assertFalse(any('MeleeAttackGoal' in str(i['operand']) for i in goals))
        b=self.body('LocustTickProcedure');by={i['offset']:i for i in b}
        self.assertIn('.setDeltaMovement(',by[1178]['operand'])
        self.assertIn('.setDeltaMovement(',by[1251]['operand'])
        for off in (1178,1251):
            j=next(j for j,i in enumerate(b) if i['offset']==off)
            self.assertEqual(sum(i['operand']==8. for i in b[j-24:j]),2)

    def test_silverfish_kill_delivery_uses_killer_not_victim_and_no_owner(self):
        b=self.body('SilverfishSpectreEntity','awardKillScore')
        j=next(j for j,i in enumerate(b) if 'SilverfishSpectreThisEntityKillsAnotherOneProcedure.execute(' in str(i['operand']))
        self.assertIn('(Lnet/minecraft/world/level/LevelAccessor;DDD)V',b[j]['operand'])
        self.assertTrue(any('Monster.awardKillScore(' in str(i['operand']) for i in b[:j]))
        for coordinate in ('getX()','getY()','getZ()'):
            self.assertTrue(any(coordinate in str(i['operand']) for i in b[:j]))
        b=self.body('SilverfishSpectreThisEntityKillsAnotherOneProcedure')
        self.assertEqual(sum('EntityType.spawn(' in str(i['operand']) for i in b),1)
        self.assertTrue(any('ArphexModEntities.SILVERFISH_SPECTRE' in str(i['operand']) for i in b))
        self.assertFalse(any('.setOwner(' in str(i['operand']) or '.hurt(' in str(i['operand']) for i in b))

    def test_locust_native_hunger_and_independent_griefing_empty_branch(self):
        b=self.body('LocustTickProcedure');by={i['offset']:i for i in b}
        j=next(j for j,i in enumerate(b) if i['offset']==191)
        self.assertEqual([i['operand'] for i in b[j-3:j]],
                         ['net/minecraft/world/effect/MobEffects.HUNGERLnet/minecraft/core/Holder;',60,1])
        self.assertTrue(any('GameRules.RULE_MOBGRIEFING' in str(i['operand']) for i in b))
        self.assertTrue(any('ConfigurationSettingsConfiguration.ARPHEX_GRIEFING' in str(i['operand']) for i in b))
        self.assertEqual((by[1589]['opcode'],by[1589]['branch_target']),('0x9a',1592))
        # Branch destination is the immediately following instruction: empty
        # occlusion body cannot gate the later Grass-to-Dirt conversion.
        j=next(j for j,i in enumerate(b) if i['offset']==1589)
        self.assertEqual(b[j+1]['offset'],1592)
        self.assertEqual([i['offset'] for i in b if 'LevelAccessor.setBlock(' in str(i['operand'])],[1498,1647])


class RecluseNativeTests(NativeContractHarness, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch=read_json(OUT/'arphex-r2m5i-recluse-native-family.json')
        cls.native=read_json(OUT/'native-evidence/arphex-recluse-native-family.json')
        cls.census=read_json(OUT/'arphex-combat-census.json')

    def test_bindings_and_explicit_inheritance_refinements(self):
        validate_batch(self.batch,self.prior(),self.census)
        self.assertEqual(len(self.batch['effects']),2)
        self.assertEqual(len(self.batch['record_refinements']),3)
        self.assertTrue(all(not r.get('candidate_additions') for r in self.batch['record_refinements']))
        self.assertEqual(sum(len(c['parameters']) for r in self.batch['effects']
                             for c in r['scalable_parameter_candidates']),7)
        self.assertFalse(self.batch['whole_mod_complete'])

    def test_concrete_spider_parent_and_independent_parent_goals(self):
        actors={c['entry']:c for c in self.census['classes']}
        for name in ('SpiderRecluseEntity','SpiderRecluseDisplayEntity','SpiderLarvaeEntity',
                     'SpiderLarvaeTinyEntity','SpiderBroodEntity','SpiderFunnelEntity'):
            self.assertEqual(actors['net/arphex/entity/'+name+'.class']['superclass'],
                             'net/minecraft/world/entity/monster/Spider')
        for name in ('SpiderRecluseEntity','SpiderRecluseDisplayEntity'):
            b=self.body(name,'registerGoals')
            self.assertIn('Spider.registerGoals()',b[1]['operand'])
            self.assertEqual(b[1]['opcode'],'0xb7')
        vanilla=read_json(OUT/'vanilla-evidence/twilight-arthropods.json')
        root=next(c for c in vanilla['classes'] if c['raw_entry']=='cko.class')
        b=next(m['instructions'] for m in root['methods'] if m['name']=='registerGoals')
        for symbol in ('Spider$SpiderAttackGoal.<init>','Spider$SpiderTargetGoal.<init>',
                       'EntityType', 'IronGolem', 'Player'):
            if symbol=='EntityType':continue
            self.assertTrue(any(symbol in str(i['operand']) for i in b),symbol)
        target=next(c for c in vanilla['classes'] if c['raw_entry']=='cko$c.class')
        b=next(m['instructions'] for m in target['methods'] if m['name']=='canUse')
        self.assertTrue(any(i['operand']==.5 for i in b))
        self.assertFalse(any('NonShiny' in str(i['operand']) for i in b))

    def test_physical_shape_is_integer_then_double_not_continuous_random(self):
        b=self.body('RecluseHitboxScaleProcedure')
        divs=[j for j,i in enumerate(b) if i['opcode']=='0x6c']
        self.assertEqual(len(divs),4)
        for j in divs:
            self.assertEqual((b[j-1]['operand'],b[j+1]['opcode']),(15,'0x87'))
        self.assertFalse(any(i['opcode']=='0x6f' for i in b))  # no ddiv
        b=self.body('SpiderRecluseEntity','getDefaultDimensions')
        self.assertTrue(any('RecluseHitboxScaleProcedure.execute(' in str(i['operand']) for i in b))
        self.assertTrue(any('EntityDimensions.scale(F)' in str(i['operand']) for i in b))
        from test_shadow_clone_contracts import native_short_branch
        v=read_json(OUT/'vanilla-evidence/arphex-recluse-math.json')['classes'][0]['methods'][0]
        self.assertEqual(native_short_branch(v,3),8)
        by={i['offset']:i for i in v['instructions']}
        self.assertEqual((by[6]['opcode'],by[7]['opcode']),('0x27','0xaf'))
        self.assertIn('RandomSource.nextDouble()',by[9]['operand'])

    def test_first_web_branch_latches_before_only_presence_query(self):
        b=self.body('SpiderRecluseTickProcedure')
        spawn=[i['offset'] for i in b if 'EntityType.spawn(' in str(i['operand'])]
        self.assertEqual(spawn,[979,1190,1405,1620,1831,2042])
        self.assertEqual(sum('AABB.ofSize(' in str(i['operand']) for i in b),1)
        self.assertIn('CompoundTag.putBoolean(',next(i['operand'] for i in b if i['offset']==837))
        self.assertLess(837,863)
        self.assertEqual(sum('ArphexModEntities.CAVE_WEB' in str(i['operand']) for i in b),6)
        self.assertFalse(any('.setOwner(' in str(i['operand']) for i in b))
        reset=next(j for j,i in enumerate(b) if i['offset']==2082)
        self.assertEqual([i['operand'] for i in b[reset-2:reset]],['slow_web_check',5.])

    def test_hang_reader_decrements_before_pose_and_weakness_is_separate(self):
        b=self.body('SpiderRecluseTickProcedure')
        self.assertTrue(any('SpiderRecluseEntity.DATA_hangweb' in str(i['operand']) for i in b))
        write=next(i['offset'] for i in b if 'SynchedEntityData.set(' in str(i['operand']))
        self.assertLess(write,next(i['offset'] for i in b if 'ModList.isLoaded(' in str(i['operand'])))
        self.assertTrue(any('MobEffects.WEAKNESS' in str(i['operand']) for i in b))
        self.assertTrue(any('.setHealth(' in str(i['operand']) and i['offset']==103 for i in b))
        self.assertFalse(any('.heal(' in str(i['operand']) for i in b))
        keys={k for c in self.row('recluse_native_hang_shape_web_and_melee')['scalable_parameter_candidates']
              for k in c['parameters']}
        self.assertFalse(any('health' in k or 'hang' in k for k in keys))

    def test_display_enabled_ai_discard_and_typed_hang_fallback(self):
        b=self.body('SpiderRecluseDisplayEntity','<init>')
        j=next(j for j,i in enumerate(b) if '.setNoAi(' in str(i['operand']))
        self.assertEqual(b[j-1]['operand'],0)
        b=self.body('RecluseAnim1OnEntityTickUpdateProcedure')
        self.assertTrue(any('.isClientSide()' in str(i['operand']) for i in b))
        self.assertEqual(sum('.discard(' in str(i['operand']) for i in b),1)
        b=self.body('LooklimRecluseProcedure')
        self.assertIn('net/arphex/entity/SpiderRecluseEntity',[i['operand'] for i in b if i['opcode']=='0xc1'])
        self.assertNotIn('net/arphex/entity/SpiderRecluseDisplayEntity',[i['operand'] for i in b if i['opcode']=='0xc1'])
        b=self.body('SpiderRecluseDisplayEntity','hurt')
        self.assertFalse(any('SpiderFunnelEntityIsHurtProcedure' in str(i['operand']) for i in b))
        b=self.body('SpiderRecluseEntity','hurt')
        helper=next(i['offset'] for i in b if 'SpiderFunnelEntityIsHurtProcedure' in str(i['operand']))
        self.assertLess(helper,next(i['offset'] for i in b if '.getDirectEntity(' in str(i['operand'])))


class SmallInsectNativeTests(NativeContractHarness, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch=read_json(OUT/'arphex-r2m5g-small-insect-native-callbacks.json')
        cls.native=read_json(OUT/'native-evidence/arphex-small-insect-callback-family.json')
        cls.census=read_json(OUT/'arphex-combat-census.json')

    def test_native_bindings_and_single_shared_collision_registration(self):
        validate_batch(self.batch,self.prior(),self.census)
        self.assertEqual((len(self.batch['effects']),len(self.batch['closed_actor_callback_entries'])),(5,4))
        self.assertEqual(sum(len(c['parameters']) for r in self.batch['effects']
                             for c in r['scalable_parameter_candidates']),21)
        rows=[r for r in self.batch['effects'] if any(c['native_consumer']['entry'].endswith('/MaggotPlayerCollidesWithThisEntityProcedure.class')
                                                  for c in r['scalable_parameter_candidates'])]
        self.assertEqual(len(rows),1)
        self.assertFalse(self.batch['whole_mod_complete'])

    def test_collision_command_ignores_original_colliding_player(self):
        for actor in ('MaggotLarvaeEntity','FlyFestererEntity'):
            b=self.body(actor,'playerTouch')
            self.assertTrue(any('Monster.playerTouch(' in str(i['operand']) for i in b))
            j=next(j for j,i in enumerate(b) if 'MaggotPlayerCollidesWithThisEntityProcedure.execute(' in str(i['operand']))
            self.assertIn('(Lnet/minecraft/world/level/LevelAccessor;DDD)V',b[j]['operand'])
            for coord in ('getX()', 'getY()', 'getZ()'):
                self.assertTrue(any(coord in str(i['operand']) for i in b[:j]))
        b=self.body('MaggotPlayerCollidesWithThisEntityProcedure')
        cmd=next(i['operand'] for i in b if isinstance(i['operand'],str) and i['operand'].startswith('effect give'))
        self.assertEqual(cmd,'effect give @p poison 1 1')
        self.assertTrue(any('CommandSource.NULL' in str(i['operand']) for i in b))
        self.assertFalse(any('.hurt(' in str(i['operand']) for i in b))

    def test_step_height_is_direct_attribute_write(self):
        b=self.body('BeetleTickMiteOnEntityTickProcedure')
        self.assertTrue(any('Attributes.STEP_HEIGHT' in str(i['operand']) for i in b))
        j=next(j for j,i in enumerate(b) if i['offset']==33)
        self.assertEqual(b[j]['operand'],'net/minecraft/world/entity/ai/attributes/AttributeInstance.setBaseValue(D)V')
        self.assertEqual(b[j-1]['operand'],2.)
        self.assertTrue(any('LivingEntity.getAttribute(' in str(i['operand']) for i in b[:j]))
        self.assertFalse(any('.setDeltaMovement(' in str(i['operand']) for i in b))

    def test_fly_yboost_reads_other_clock_and_late_water_write(self):
        b=self.body('FlyFestererTickProcedure')
        j=next(j for j,i in enumerate(b) if i['offset']==624)
        segment=b[j-8:j]
        self.assertIn('yboost',[i['operand'] for i in segment])  # write key
        read=next(k for k,i in enumerate(segment) if 'CompoundTag.getDouble(' in str(i['operand']))
        self.assertEqual(segment[read-1]['operand'],'flyboost')  # value read key
        self.assertIn(1.,[i['operand'] for i in segment])
        self.assertEqual([i['offset'] for i in b if '.setDeltaMovement(' in str(i['operand'])],[318,549,578,676])
        r=self.row('fly_festerer_native_coupled_motion_and_incoming_state')
        keys={k for c in r['scalable_parameter_candidates'] for k in c['parameters']}
        self.assertFalse(any('yboost' in k for k in keys))
        goal=self.body('FlyFestererEntity','registerGoals')
        self.assertFalse(any('MeleeAttackGoal' in str(i['operand']) for i in goal))
        self.assertFalse(any(c['primitive']=='NATIVE_CONDITIONAL_MELEE' for c in r['scalable_parameter_candidates']))

    def test_shiny_gate_applies_only_to_player_avoidance(self):
        b=self.body('RoachRiverspawnEntity$1','canUse')
        self.assertTrue(any('AvoidEntityGoal.canUse(' in str(i['operand']) for i in b))
        self.assertTrue(any('RoachShinyProcedure.execute(' in str(i['operand']) for i in b))
        b=self.body('RoachRiverspawnEntity$2','canPerformAttack')
        self.assertFalse(any('RoachShinyProcedure.execute(' in str(i['operand']) for i in b))
        self.assertTrue(any('.hasLineOfSight(' in str(i['operand']) for i in b))
        b=self.body('RoachShinyProcedure')
        self.assertTrue(any('RoachRiverspawnEntity.DATA_shiny' in str(i['operand']) for i in b))

    def test_maggot_native_discard_precedes_unowned_fly_spawn(self):
        b=self.body('MaggotOnEntityTickUpdateProcedure')
        discard=next(i['offset'] for i in b if '.discard(' in str(i['operand']))
        self.assertLess(discard,135)
        self.assertTrue(any('ArphexModEntities.FLY_FESTERER' in str(i['operand']) for i in b))
        self.assertEqual(sum('EntityType.spawn(' in str(i['operand']) for i in b),1)
        self.assertFalse(any('.setOwner(' in str(i['operand']) for i in b))
        j=next(j for j,i in enumerate(b) if i['offset']==67)
        self.assertEqual([i['operand'] for i in b[j-2:j]],[1,5000])
        goal=self.body('MaggotLarvaeEntity$1','canPerformAttack')
        self.assertTrue(any('.hasLineOfSight(' in str(i['operand']) for i in goal))
        self.assertFalse(any('MaggotPlayerCollidesWithThisEntityProcedure' in str(i['operand']) for i in goal))


class WebPlantNativeTests(NativeContractHarness, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch=read_json(OUT/'arphex-r2m5h-web-plant-native-hazards.json')
        cls.native=read_json(OUT/'native-evidence/arphex-web-plant-hazard-family.json')
        cls.census=read_json(OUT/'arphex-combat-census.json')

    def test_native_bindings_and_explicit_deferred_consumers(self):
        validate_batch(self.batch,self.prior(),self.census)
        self.assertEqual((len(self.batch['effects']),len(self.batch['closed_actor_callback_entries'])),(4,4))
        self.assertEqual(sum(len(c['parameters']) for r in self.batch['effects']
                             for c in r['scalable_parameter_candidates']),14)
        r=self.row('web_funnel_native_ground_conversion')
        self.assertEqual(r['primary_classification'],'BINARY_MECHANIC')
        self.assertEqual(r['scalable_parameter_candidates'],[])
        self.assertTrue(self.row('cave_web_native_sticking_and_recluse_hang_control')['directly_deferred_consumers'])
        self.assertFalse(self.batch['whole_mod_complete'])

    def test_cave_sticking_is_immediate_after_possible_discard(self):
        b=self.body('CaveWebOnEntityTickUpdateProcedure')
        self.assertFalse(any('.queueServerWork(' in str(i['operand']) for i in b))
        self.assertEqual(sum('.makeStuckInBlock(' in str(i['operand']) for i in b),1)
        self.assertTrue(any('.discard(' in str(i['operand']) and i['offset']<1090 for i in b))
        j=next(j for j,i in enumerate(b) if i['offset']==1224)
        self.assertEqual([i['operand'] for i in b[j-9:j] if i['opcode'] in ('0x12','0x13','0x14')],[.25,.05,.25])
        self.assertFalse(any('.hurt(' in str(i['operand']) for i in b))

    def test_recluse_hang_control_is_separate_from_web_self_grid(self):
        b=self.body('CaveWebOnEntityTickUpdateProcedure')
        by={i['offset']:i for i in b}
        self.assertIn('.teleportTo(',by[36]['operand'])
        self.assertIn('.teleportTo(',by[335]['operand'])
        self.assertTrue(any('SpiderRecluseEntity.DATA_size' in str(i['operand']) for i in b))
        self.assertTrue(any('SpiderRecluseEntity.DATA_hangweb' in str(i['operand']) for i in b))
        self.assertTrue(any(i['operand']==30 for i in b))
        self.assertIn('CompoundTag.putDouble(',by[168]['operand'])
        self.assertLess(168,335)  # presence resets age before hanging admission/delivery
        self.assertFalse(any('.setOwner(' in str(i['operand']) for i in b))

    def test_funnel_one_block_conversion_has_no_server_guard(self):
        b=self.body('FunnelWebOnEntityTickUpdateProcedure')
        places=[i for i in b if 'LevelAccessor.setBlock(' in str(i['operand'])]
        self.assertEqual([i['offset'] for i in places],[296])
        j=next(j for j,i in enumerate(b) if i['offset']==296)
        self.assertEqual(b[j-1]['operand'],3)
        self.assertFalse(any(i['opcode']=='0xc1' and i['operand']=='net/minecraft/server/level/ServerLevel' for i in b[:j]))
        self.assertTrue(any('ArphexModBlocks.FUNNEL_WEB' in str(i['operand']) for i in b[:j]))
        actor=self.body('WebFunnelEntity','<init>')
        at=next(j for j,i in enumerate(actor) if '.setNoAi(' in str(i['operand']))
        self.assertEqual(actor[at-1]['operand'],1)

    def test_prototype_latch_precedes_spawn_and_rename_has_no_spawn_reference(self):
        b=self.body('FlytrapOnEntityTickUpdateProcedure')
        self.assertEqual([i['offset'] for i in b if '.queueServerWork(' in str(i['operand'])],[47,69,164])
        latch=next(i['offset'] for i in b if 'CompoundTag.putBoolean(' in str(i['operand']))
        self.assertLess(latch,143)
        w=next(w for w in self.native['witnesses'] if w['entry'].endswith('/FlytrapOnEntityTickUpdateProcedure.class'))
        m=next(m for m in w['methods'] if m['name']=='lambda$execute$4')
        self.assertEqual(m['descriptor'],'(Lnet/minecraft/world/level/LevelAccessor;DDD)V')
        self.assertTrue(any('.setCustomName(' in str(i['operand']) for i in m['instructions']))
        self.assertTrue(any(i['operand']=='Tamed Flytrap' for i in m['instructions']))
        self.assertEqual(sum('AABB.ofSize(' in str(i['operand']) for i in m['instructions']),2)
        self.assertFalse(any('.setOwner(' in str(i['operand']) or '.tame(' in str(i['operand']) for i in b+m['instructions']))

    def test_native_name_goal_and_current_target_clear_are_separate(self):
        b=self.body('NotNamedProcedure')
        self.assertTrue(any(i['operand']=='Venus Flytrap' for i in b))
        j=next(j for j,i in enumerate(b) if 'String.equals(' in str(i['operand']))
        self.assertEqual(b[j+1]['opcode'],'0xac')  # no inversion of authored predicate
        for method in ('canUse','canContinueToUse'):
            self.assertTrue(any('NotNamedProcedure.execute(' in str(i['operand'])
                                for i in self.body('VenusFlytrapEntity$1',method)))
        b=self.body('VenusFlytrapOnEntityTickUpdateProcedure')
        self.assertTrue(any(i['operand']=='Venus Flytrap' for i in b))
        self.assertTrue(any('.setTarget(' in str(i['operand']) for i in b))
        goal=self.body('VenusFlytrapEntity','registerGoals')
        self.assertTrue(any('HurtByTargetGoal.<init>' in str(i['operand']) for i in goal))
        self.assertFalse(any('.setOwner(' in str(i['operand']) or '.tame(' in str(i['operand']) for i in goal))
