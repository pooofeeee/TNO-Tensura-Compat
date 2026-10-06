"""Shared harness, independent native facts for bounded small-actor families."""
import copy
import unittest
from catalog_common import OUT, read_json
from promote_combat_batch import validate_batch
from test_shadow_clone_contracts import NativeContractHarness




class NativeCrabHarnessTests(NativeContractHarness, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch=read_json(OUT/'arphex-r2m5z-native-crab-solifuge-harness.json')
        cls.native=read_json(OUT/'native-evidence/arphex-native-crab-solifuge-harness.json')
        cls.census=read_json(OUT/'arphex-combat-census.json')

    def test_three_new_contracts_four_roots_and_old_harness_reuse(self):
        validate_batch(self.batch,self.prior(),self.census)
        self.assertEqual((len(self.batch['effects']),len(self.batch['closed_actor_callback_entries'])),(3,4))
        self.assertEqual(sum(len(c['parameters']) for r in self.batch['effects'] for c in r['scalable_parameter_candidates']),60)
        self.assertEqual((len(self.native['witnesses']),sum(len(w['methods']) for w in self.native['witnesses'])),(33,168))
        self.assertFalse(any(w['entry'].endswith('/WebHarnessEntity.class') for w in self.native['witnesses']))
        self.assertEqual(self.batch['reused_closed_actor_contracts'][0]['canonical_contract'],'arphex:hook_harness_native_anchor_control')

    def test_crab_melee_guard_and_native_damage_independent_of_grab(self):
        for name in ('canUse','canContinueToUse'):
            b=self.body('CrabConstrictorEntity$1',name)
            self.assertTrue(any('ConstrictingUpwardsProcedure.execute(' in str(i['operand']) for i in b))
        b=self.body('CrabConstrictorEntity$1','canPerformAttack')
        self.assertTrue(any(i['operand']==169.0 for i in b))
        self.assertTrue(any('.hasLineOfSight(' in str(i['operand']) for i in b))
        b=self.body('CrabConstrictorOnEntityTickUpdateProcedure')
        self.assertFalse(any('.hurt(' in str(i['operand']) or '.isAlliedTo(' in str(i['operand']) for i in b))

    def test_crab_terrain_counter_is_not_periodic_fifteen_ticks(self):
        b=self.body('CrabConstrictorOnEntityTickUpdateProcedure');by={i['offset']:i for i in b}
        self.assertEqual(by[2686]['operand'],0.0)
        self.assertEqual(by[2687]['opcode'],'0x98') # dcmpg: >=0 takes reset path
        self.assertEqual(by[2688]['opcode'],'0x9b') # negative skips reset15
        self.assertEqual((by[2699]['operand'],by[2702]['operand'].split('.')[-1].split('(')[0]),(15.0,'putDouble'))
        self.assertEqual(by[3032]['opcode'],'0x67')
        row=self.row('crab_constrictor_native_grab_pose_melee_and_terrain')
        self.assertFalse(any(c['primitive']=='TERRAIN_CADENCE' for c in row['scalable_parameter_candidates']))

    def test_crab_raw_wait_is_distinct_from_synched_wait(self):
        from promote_combat_batch import literal_synched_int_binding
        b=self.body('CrabConstrictorOnEntityTickUpdateProcedure');by={i['offset']:i for i in b}
        self.assertEqual((by[4425]['operand'],by[4428]['operand']),('grabwait',150.0))
        w=next(w for w in self.native['witnesses'] if w['entry'].endswith('/CrabConstrictorOnEntityTickUpdateProcedure.class'))
        m=next(m for m in w['methods'] if m['name']=='execute')
        for off,value in [(2616,400),(7112,200)]:
            bound=literal_synched_int_binding(m,off)
            self.assertEqual(bound['native_value'],value)
            self.assertIn('DATA_grabwait',str(bound))
        self.assertFalse(any(c.get('native_tag_double_binding',{}).get('tag')=='grabwait' for c in self.row('crab_constrictor_native_grab_pose_melee_and_terrain')['scalable_parameter_candidates']))

    def test_crab_distance_update_occurs_between_sprint_and_crouch_consumers(self):
        b=self.body('CrabConstrictorOnEntityTickUpdateProcedure');by={i['offset']:i for i in b}
        for off in (4411,6035,7035):self.assertIn('.setDeltaMovement(',by[off]['operand'])
        for off in (4537,4596,4670):self.assertIn('.putDouble(',by[off]['operand'])
        self.assertLess(4411,4537);self.assertLess(4670,6035)
        self.assertEqual((by[4484]['operand'],by[4487]['operand'],by[4528]['operand'],by[4532]['operand']),(3.3,.165,.66,.8))
        self.assertEqual((by[4593]['operand'],by[4660]['operand']),(16.5,100))
        row=self.row('crab_constrictor_native_grab_pose_melee_and_terrain')
        c=next(c for c in row['scalable_parameter_candidates'] if c['parameters']==['rising_factor'])
        self.assertFalse(c.get('additional_consumer_sites'))

    def test_crab_constricted_recipient_differs_from_self_status_receiver(self):
        row=self.row('crab_constrictor_native_grab_pose_melee_and_terrain')
        cs=[c for c in row['scalable_parameter_candidates'] if 'native_receiver_binding' in c]
        self.assertEqual(next(c for c in cs if c['primitive']=='MOB_EFFECT_RECIPIENT_CONSTRICTED')['native_receiver_binding']['origin_local_index'],15)
        self.assertTrue(all(c['native_receiver_binding']['origin_local_index']==7 for c in cs if c['primitive']!='MOB_EFFECT_RECIPIENT_CONSTRICTED'))
        b=self.body('CrabConstrictorOnEntityTickUpdateProcedure')
        self.assertLess(next(i['offset'] for i in b if '.removeEffect(' in str(i['operand'])),304)

    def test_solifuge_only_native_caller_excludes_centipede_branch(self):
        from collect_combat_census import decode_sites
        callers=[(m['entry'],m['method'],s['offset']) for m in self.census['methods'] for s in decode_sites(self.census,m,'calls') if 'SolfTickProcedure.execute(' in str(s['operand'])]
        self.assertEqual(callers,[('net/arphex/entity/SolifugeSkulkerEntity.class','baseTick',21)])
        by={i['offset']:i for i in self.body('SolfTickProcedure')}
        self.assertEqual(by[2960]['operand'],'net/arphex/entity/CentipedeEvictorEntity')
        row=self.row('solifuge_native_melee_shadow_climb_leap_and_terrain')
        sites=[c['native_consumer']['offset'] for c in row['scalable_parameter_candidates']]
        self.assertNotIn(3001,sites);self.assertNotIn(3044,sites)

    def test_solifuge_two_southward_guards_compare_identical_native_arguments(self):
        b=self.body('SolfTickProcedure');fingerprint=lambda a:[(i['opcode'],i['operand'],i.get('local_index')) for i in a]
        for first,second,value in [(1312,1329,5.0),(2304,2321,10.0)]:
            a=next(j for j,i in enumerate(b) if i['offset']==first);z=next(j for j,i in enumerate(b) if i['offset']==second)
            self.assertEqual(fingerprint(b[a-7:a+1]),fingerprint(b[z-7:z+1]))
            self.assertEqual((b[z-3]['operand'],b[z-2]['opcode'],b[z+1]['opcode']),(value,'0x67','0xa2'))
        r=self.row('solifuge_native_melee_shadow_climb_leap_and_terrain')
        sites={c['native_consumer']['offset'] for c in r['scalable_parameter_candidates']}|{a['offset'] for c in r['scalable_parameter_candidates'] for a in c.get('additional_consumer_sites',[])}
        self.assertTrue({1456,2448,1501,2493}.isdisjoint(sites))

    def test_solifuge_navigation_near_far_and_speed_consumers_stay_distinct(self):
        r=self.row('solifuge_native_melee_shadow_climb_leap_and_terrain')
        expected={'near_offset':{712,960,1208},'far_offset':{1704,1952,2200},'speed':{712,960,1208,1704,1952,2200}}
        b=self.body('SolfTickProcedure')
        for parameter,offsets in expected.items():
            c=next(c for c in r['scalable_parameter_candidates'] if c['primitive']=='NATIVE_SHADOW_NAVIGATION' and c['parameters']==[parameter])
            self.assertEqual({c['native_consumer']['offset']}|{x['offset'] for x in c.get('additional_consumer_sites',[])},offsets)
            for off in offsets:
                j=next(j for j,i in enumerate(b) if i['offset']==off)
                self.assertEqual(b[j-1]['operand'],1.0)
                self.assertIn(5.0 if parameter=='near_offset' else 10.0 if parameter=='far_offset' else 1.0,[i['operand'] for i in b[j-9:j]])

    def test_common_status_durations_not_counted_per_branch(self):
        for suffix,primitive,sites in [('solifuge_native_melee_shadow_climb_leap_and_terrain','MOB_EFFECT_INJURED_SELF_SPEED',4),('crab_constrictor_native_grab_pose_melee_and_terrain','MOB_EFFECT_SELF_SPEED',4)]:
            cs=[c for c in self.row(suffix)['scalable_parameter_candidates'] if c['primitive']==primitive and 'duration' in c['parameters']]
            self.assertEqual(len(cs),1);self.assertEqual(len(cs[0].get('additional_consumer_sites',[]))+1,sites)

    def test_hanging_harness_motion_shared_horizontal_does_not_alias_verticals(self):
        r=self.row('hook_hanging_harness_native_anchor_mount_and_motion')
        c=next(c for c in r['scalable_parameter_candidates'] if c['parameters']==['return_horizontal_divisor'])
        self.assertEqual(c['additional_consumer_sites'][0]['offset'],657)
        c=next(c for c in r['scalable_parameter_candidates'] if c['parameters']==['low_return_y'])
        self.assertFalse(c.get('additional_consumer_sites'))
        by={i['offset']:i for i in self.body('WebHarnessDownTickProcedure')}
        self.assertEqual((by[573]['operand'],by[631]['operand']),(.4,.05))
        self.assertLess(78,599)

    def test_hanging_harness_unowned_mount_discard_and_native_lifecycle(self):
        b=self.body('WebHarnessDownSpawnProcedure')
        self.assertTrue(any('.startRiding(' in str(i['operand']) for i in b))
        self.assertFalse(any('.setOwner(' in str(i['operand']) for i in b))
        self.assertLess(next(i['offset'] for i in b if '.discard(' in str(i['operand'])),171)
        b=self.body('WebHarnessDownTickProcedure')
        self.assertLess(max(i['offset'] for i in b if '.discard(' in str(i['operand'])),1345)
        b=self.body('WebHarnessDownTickProcedure','lambda$execute$1')
        self.assertTrue(any('.isVehicle(' in str(i['operand']) for i in b))
        self.assertFalse(any('.isAlive(' in str(i['operand']) or '.getOwner(' in str(i['operand']) for i in b))

    def test_terrain_shared_extent_mutant_is_rejected(self):
        altered=copy.deepcopy(self.batch)
        r=next(r for r in altered['effects'] if r['id'].endswith('solifuge_native_melee_shadow_climb_leap_and_terrain'))
        next(c for c in r['components'] if c['primitive']=='TERRAIN_COMMAND')['numerical_parameters']['half_extent']=3.0
        with self.assertRaises(AssertionError):validate_batch(altered,self.prior(),self.census)


class NativeInitialCarrierTests(NativeContractHarness, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch=read_json(OUT/'arphex-r2m5y-native-initial-tormentor-carriers.json')
        cls.native=read_json(OUT/'native-evidence/arphex-native-initial-tormentor-carriers.json')
        cls.census=read_json(OUT/'arphex-combat-census.json')

    def test_seven_roots_six_contracts_reuse_protected_callbacks(self):
        validate_batch(self.batch,self.prior(),self.census)
        self.assertEqual((len(self.batch['effects']),len(self.batch['closed_actor_callback_entries'])),(6,7))
        self.assertEqual(sum(len(c['parameters']) for r in self.batch['effects'] for c in r['scalable_parameter_candidates']),59)
        self.assertEqual((len(self.native['witnesses']),sum(len(w['methods']) for w in self.native['witnesses'])),(93,528))
        for root in ('TormentorLarvaeEntity','TormentorScorpioidSummonEntity','TormentorVoidlasherSummonEntity'):
            w=next(w for w in self.native['witnesses'] if w['entry'].endswith('/'+root+'.class'))
            self.assertNotIn('baseTick',{m['name'] for m in w['methods']})

    def test_larva_physical_size_uses_integer_division_before_float_round(self):
        b=self.body('TormentorLarvaeBoundingBoxScaleProcedure');by={i['offset']:i for i in b}
        self.assertEqual((by[38]['operand'],by[40]['opcode'],by[41]['opcode']),(10,'0x6c','0x86'))
        self.assertEqual(by[42]['operand'],'java/lang/Math.round(F)I')
        self.assertTrue(any('TormentorLarvaeBoundingBoxScaleProcedure.execute(' in str(i['operand']) for i in self.body('TormentorLarvaeEntity','getDefaultDimensions')))
        b=self.body('TormentorLarvaeOnInitialEntitySpawnProcedure');by={i['offset']:i for i in b}
        self.assertEqual((by[41]['operand'],by[43]['operand']),(10,50))
        self.assertIn('.nextInt(',by[45]['operand']);self.assertIn('SynchedEntityData.set(',by[51]['operand'])

    def test_area_distribution_rejects_wrong_literal_bound(self):
        altered=copy.deepcopy(self.batch)
        row=next(r for r in altered['effects'] if r['id'].endswith('tormentor_larvae_native_root_melee_and_integer_body_size'))
        next(c for c in row['components'] if c['primitive']=='NATIVE_AREA_SIZE')['numerical_parameters']['maximum']=51
        with self.assertRaises(AssertionError):validate_batch(altered,self.prior(),self.census)

    def test_tendril_respite_reads_self_local_seven(self):
        b=self.body('TormentorTendrilOnEntityTickUpdateProcedure');by={i['offset']:i for i in b}
        self.assertEqual((by[1635]['opcode'],by[1635]['local_index']),('0x19',7))
        self.assertIn('.getData(',by[1640]['operand']);self.assertIn('PlayerVariables.tormentor_respiteD',by[1646]['operand'])
        self.assertIn('.setDeltaMovement(',by[1696]['operand'])
        self.assertFalse(any('.hurt(' in str(i['operand']) or '.isAlliedTo(' in str(i['operand']) for i in b))

    def test_tendril_beam_contains_native_status_command_and_separate_contact(self):
        b=self.body('TormentorTendrilOnEntityTickUpdateProcedure')
        self.assertTrue(any(i['operand']=='effect give @e[type=player,distance=..3] arphex:torment 2 0' for i in b))
        self.assertTrue(any(i['operand']==100 and i['opcode']=='0x10' for i in b))
        self.assertTrue(any(i['operand']==.01 for i in b))
        goal=self.body('TormentorTendrilEntity$1','tick')
        self.assertTrue(any('.intersects(' in str(i['operand']) for i in goal))
        self.assertTrue(any('.doHurtTarget(' in str(i['operand']) for i in goal))
        self.assertFalse(any('isTimeToAttack' in str(i['operand']) for i in goal))

    def test_sun_source_is_self_and_status_follows_ignored_hurt(self):
        b=self.body('SummonSunBlastOnEntityTickUpdateProcedure');by={i['offset']:i for i in b}
        self.assertEqual(by[245]['local_index'],7)
        self.assertIn('DamageSource.<init>(Lnet/minecraft/core/Holder;Lnet/minecraft/world/entity/Entity;)V',by[247]['operand'])
        self.assertEqual(by[250]['operand'],40.0)
        for hurt,effect in [(252,299),(328,375)]:
            j=next(j for j,i in enumerate(b) if i['offset']==hurt)
            self.assertEqual(b[j+1]['opcode'],'0x57')
            self.assertIn('.addEffect(',by[effect]['operand'])
        r=self.row('summon_sun_blast_native_generic_field_motion_and_size')
        self.assertEqual(sum(c['primitive']=='NATIVE_DAMAGE_REQUEST' for c in r['scalable_parameter_candidates']),1)

    def test_sun_damage_query_precedes_live_size_growth_and_shrink(self):
        b=self.body('SummonSunBlastOnEntityTickUpdateProcedure');by={i['offset']:i for i in b}
        self.assertIn('.inflate(',by[116]['operand'])
        self.assertEqual((by[933]['operand'],by[934]['opcode']),(1,'0x64'))
        self.assertEqual((by[1022]['operand'],by[1023]['opcode']),(1,'0x60'))
        self.assertIn('SynchedEntityData.set(',by[938]['operand']);self.assertIn('SynchedEntityData.set(',by[1027]['operand'])
        self.assertFalse(any('.setOwner(' in str(i['operand']) or '.isAlliedTo(' in str(i['operand']) for i in b))

    def test_initial_hurt_effect_precedes_direct_player_native_rejection(self):
        b=self.body('TormentorInitialEntity','hurt')
        helper=next(i['offset'] for i in b if 'TormentorInitialEntityIsHurtProcedure.execute(' in str(i['operand']))
        player=next(i['offset'] for i in b if i['opcode']=='0xc1' and i['operand']=='net/minecraft/world/entity/player/Player')
        self.assertLess(helper,player)
        b=self.body('TormentorSpawnConditionProcedure')
        self.assertEqual(sum('DWELLERS_FREQUENCY' in str(i['operand']) for i in b),5)
        self.assertFalse(any(type(i['operand']) is float and i['operand']==4.0 for i in b))
        self.assertEqual(sum(type(i['operand']) is float and i['operand']==3.0 for i in b),2)

    def test_scorpioid_initial_spawn_status_is_self_not_entity_iterator(self):
        from promote_combat_batch import effect_receiver_binding
        w=next(w for w in self.native['witnesses'] if w['entry'].endswith('/ScorpioidInitialOnInitialEntitySpawnProcedure.class'))
        m=next(m for m in w['methods'] if m['name']=='lambda$execute$15')
        self.assertEqual(effect_receiver_binding(m,221)['origin_local_index'],0)
        b=self.body('ScorpioidInitialEntity','hurt');by={i['offset']:i for i in b}
        self.assertIn('DamageSource.getEntity()',by[18]['operand'])
        self.assertIn('ScorpioidInitialEntityIsHurtProcedure.execute(',by[21]['operand'])
        self.assertIn('DamageSource.getDirectEntity()',by[25]['operand'])

    def test_summon_flee_guard_is_goal_gate_and_voidlasher_has_no_melee(self):
        for n in range(1,8):
            for method in ('canUse','canContinueToUse'):
                b=self.body('TormentorScorpioidSummonEntity$'+str(n),method)
                self.assertTrue(any('GoToTormentorProcedure.execute(' in str(i['operand']) for i in b))
        b=self.body('TormentorVoidlasherSummonEntity','registerGoals')
        self.assertFalse(any('MeleeAttackGoal' in str(i['operand']) for i in b))
        self.assertTrue(any('HurtByTargetGoal' in str(i['operand']) for i in b))
        r=self.row('tormentor_scorpioid_voidlasher_native_root_setup_and_goal_gates')
        self.assertEqual(sum(c['primitive']=='NATIVE_CONDITIONAL_MELEE' for c in r['scalable_parameter_candidates']),1)

    def test_shared_command_coefficients_reject_changed_extent_and_wrong_token(self):
        altered=copy.deepcopy(self.batch)
        r=next(r for r in altered['effects'] if r['id'].endswith('scorpioid_initial_native_stalking_replacement_and_terrain'))
        next(c for c in r['components'] if c['primitive']=='TERRAIN_COMMAND')['numerical_parameters']['half_extent']=4.0
        with self.assertRaises(AssertionError):validate_batch(altered,self.prior(),self.census)
        altered=copy.deepcopy(self.batch)
        r=next(r for r in altered['effects'] if r['id'].endswith('scorpioid_initial_native_stalking_replacement_and_terrain'))
        c=next(c for c in r['scalable_parameter_candidates'] if c['primitive']=='NATIVE_TELEPORT_COMMAND' and c['parameters']==['vertical'])
        c['native_shared_command_tokens']['vertical']['indices']=[8]
        with self.assertRaises(AssertionError):validate_batch(altered,self.prior(),self.census)

    def test_current_nearest_blindness_does_not_capture_original_player(self):
        b=self.body('ScorpioidInitialOnEntityTickUpdateProcedure','lambda$execute$14')
        self.assertTrue(any('Player' in str(i['operand']) for i in b))
        self.assertTrue(any(i['operand']==250.0 for i in b))
        self.assertTrue(any('.getEntitiesOfClass(' in str(i['operand']) for i in b))
        self.assertFalse(any('getStringUUID' in str(i['operand']) or '.isAlive(' in str(i['operand']) for i in b))


class NativeBossRootTests(NativeContractHarness, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch=read_json(OUT/'arphex-r2m5x-native-boss-root-carriers.json')
        cls.native=read_json(OUT/'native-evidence/arphex-native-boss-root-carriers.json')
        cls.census=read_json(OUT/'arphex-combat-census.json')

    def test_four_roots_reuse_protected_controller_and_incoming_methods(self):
        validate_batch(self.batch,self.prior(),self.census)
        self.assertEqual((len(self.batch['effects']),len(self.batch['closed_actor_callback_entries'])),(4,4))
        self.assertEqual(sum(len(c['parameters']) for r in self.batch['effects'] for c in r['scalable_parameter_candidates']),17)
        self.assertEqual((len(self.native['witnesses']),sum(len(w['methods']) for w in self.native['witnesses'])),(29,188))
        for w in self.native['witnesses']:
            if w['entry'].endswith('Entity.class'):
                self.assertNotIn('baseTick',{m['name'] for m in w['methods']})
        sc=next(w for w in self.native['witnesses'] if w['entry'].endswith('/ScorpioidBloodlusterEntity.class'))
        self.assertFalse({'hurt','getDefaultDimensions'} & {m['name'] for m in sc['methods']})
        for suffix in ('arachnoid','diabolos'):
            r=self.row(suffix+'_native_root_melee_spawn_and_defeated_status')
            self.assertEqual(r['primary_classification'],'CUSTOM_CONTROL')
            self.assertIn('arphex:moth_curse',r['canonical_contract_reuse'])

    def test_kill_helpers_receive_defeated_local_one_and_not_killer(self):
        for a,n in [('ArachnoidTrisectorEntity','ArachnoidKillsEntityProcedure'),('DiabolosDecimatorEntity','DiabolosKillsEntityProcedure'),('ScorpioidBloodlusterEntity','ScorpioidKillProcedure')]:
            b=self.body(a,'awardKillScore');j=next(j for j,i in enumerate(b) if n+'.execute(' in str(i['operand']))
            self.assertEqual(b[j-1]['opcode'],'0x2b')
        for n in ('ArachnoidKillsEntityProcedure','DiabolosKillsEntityProcedure'):
            b=self.body(n);j=next(j for j,i in enumerate(b) if '.addEffect(' in str(i['operand']))
            self.assertEqual(b[j-3]['operand'],60);self.assertEqual(b[j-2]['operand'],1)
            self.assertTrue(any('MobEffects.REGENERATION' in str(i['operand']) for i in b[:j]))

    def test_spawn_custom_moth_curse_recipient_is_self_for_each_player(self):
        from promote_combat_batch import effect_receiver_binding
        for n,amp in [('ArachnoidTrisectorOnInitialEntitySpawnProcedure',3),('DiabolosSpawnProcedure',4)]:
            w=next(w for w in self.native['witnesses'] if w['entry'].endswith('/'+n+'.class'));m=next(m for m in w['methods'] if m['name']=='execute');b=m['instructions'];j=next(j for j,i in enumerate(b) if i['offset']==157)
            self.assertEqual((b[j-3]['operand'],b[j-2]['operand']),(200,amp))
            binding=effect_receiver_binding(m,b[j-1]['offset'])
            self.assertEqual(binding['origin_local_index'],7)
            self.assertTrue(any('.setVisualOnly(' in str(i['operand']) for i in b))

    def test_diabolos_two_melee_goals_share_one_damage_attribute(self):
        b=self.body('DiabolosDecimatorEntity','registerGoals')
        self.assertTrue(any('DiabolosDecimatorEntity$1.<init>' in str(i['operand']) for i in b))
        self.assertTrue(any('DiabolosDecimatorEntity$2.<init>' in str(i['operand']) for i in b))
        for suffix,limit in [('$1',225.0),('$2',64.0)]:
            b=self.body('DiabolosDecimatorEntity'+suffix,'canPerformAttack')
            self.assertTrue(any(i['operand']==limit for i in b))
            self.assertTrue(any('.hasLineOfSight(' in str(i['operand']) for i in b))
        for name in ('canUse','canContinueToUse'):
            self.assertTrue(any('GiantModeDiabolosProcedure.execute(' in str(i['operand']) for i in self.body('DiabolosDecimatorEntity$1',name)))
        cs=self.row('diabolos_native_root_melee_spawn_and_defeated_status')['scalable_parameter_candidates']
        self.assertEqual(sum(c['primitive']=='NATIVE_CONDITIONAL_MELEE' for c in cs),1)

    def test_scorpioid_abort_delivery_checks_current_immunity_without_spawn_recheck(self):
        for name in ('lambda$execute$5','lambda$execute$9'):
            b=self.body('ScorpioidBloodlusterOnInitialEntitySpawnProcedure',name)
            self.assertTrue(any('DESPAWN_IMMUNITY' in str(i['operand']) for i in b))
            self.assertTrue(any('.discard(' in str(i['operand']) for i in b))
            self.assertFalse(any('.getEntitiesOfClass(' in str(i['operand']) or '.isAlive(' in str(i['operand']) for i in b))
        b=self.body('ScorpioidBloodlusterOnInitialEntitySpawnProcedure')
        self.assertEqual([i['offset'] for i in b if '.queueServerWork(' in str(i['operand'])],[150,372,560])
        self.assertTrue(any(i['operand']=='spawnedawayfromplayer' for i in b))

    def test_wasp_initial_flight_distribution_is_distinct_from_tick_reset(self):
        b=self.body('WaspNemesisOnInitialEntitySpawnProcedure');j=next(j for j,i in enumerate(b) if '.nextInt(' in str(i['operand']))
        self.assertEqual((b[j-2]['operand'],b[j-1]['operand']),(600,1200))
        self.assertTrue(any(i['operand']=='eagletickslow' for i in b))
        self.assertFalse(any('.setPersistenceRequired(' in str(i['operand']) or 'FlyingMoveControl' in str(i['operand']) for i in self.body('WaspNemesisEntity','<init>')))

    def test_native_death_protection_is_item_bound_not_boss_attack(self):
        for n,item in [('TrisectorDiesProcedure','TIME_PRISM'),('DiabolosDiesProcedure','ENTROPY_MATRIX'),('ScorpioidBloodlusterEntityDiesProcedure','FIRE_OPAL')]:
            b=self.body(n,'lambda$execute$2')
            self.assertTrue(any('ArphexModItems.'+item in str(i['operand']) for i in b))
            self.assertTrue(any(i['operand']=='data merge entity @s {Glowing:1b,Invulnerable:1b}' for i in b))
            self.assertFalse(any('.hurt(' in str(i['operand']) or '.setOwner(' in str(i['operand']) for i in b))

    def test_ai_facing_repetitions_do_not_duplicate_native_attacks(self):
        for a in ('ArachnoidTrisectorEntity','DiabolosDecimatorEntity'):
            b=self.body(a,'aiStep')
            self.assertEqual(sum('.updateSwingTime(' in str(i['operand']) for i in b),8)
            self.assertFalse(any('.hurt(' in str(i['operand']) or '.doHurtTarget(' in str(i['operand']) for i in b))
            scale=next(i['operand'] for i in self.body(a,'getDefaultDimensions') if i['opcode']=='0x13')
            self.assertAlmostEqual(scale,1.49,places=6)


class NativeTormentorRootTests(NativeContractHarness, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch=read_json(OUT/'arphex-r2m5w-native-tormentor-root-tiers.json')
        cls.native=read_json(OUT/'native-evidence/arphex-native-tormentor-root-tiers.json')
        cls.census=read_json(OUT/'arphex-combat-census.json')

    def test_six_roots_share_two_contracts_without_controller_recapture(self):
        validate_batch(self.batch,self.prior(),self.census)
        self.assertEqual((len(self.batch['effects']),len(self.batch['closed_actor_callback_entries'])),(2,6))
        self.assertEqual(sum(len(c['parameters']) for r in self.batch['effects'] for c in r['scalable_parameter_candidates']),3)
        self.assertEqual((len(self.native['witnesses']),sum(len(w['methods']) for w in self.native['witnesses'])),(20,225))
        root=next(w for w in self.native['witnesses'] if w['entry'].endswith('/TORMENTOREntity.class'))
        self.assertFalse({'baseTick','die'} & {m['name'] for m in root['methods']})
        self.assertFalse(any('TranscendentalTormentor' in w['entry'] for w in self.native['witnesses']))

    def test_split_precedes_native_rejection_without_direct_player_arrow_gate(self):
        b=self.body('TORMENTOREntity','hurt')
        helper=next(i['offset'] for i in b if 'TORMENTOREntityIsHurtProcedure.execute(' in str(i['operand']))
        first=next(i['offset'] for i in b if 'DamageTypes.IN_FIRE' in str(i['operand']))
        self.assertLess(helper,first)
        types=[i['operand'] for i in b if i['opcode']=='0xc1']
        self.assertFalse(any('Player' in t or 'Arrow' in t for t in types))
        for root in ['TormentorTestEntity']+['TormentorT'+str(t)+'Entity' for t in range(2,6)]:
            types=[i['operand'] for i in self.body(root,'hurt') if i['opcode']=='0xc1']
            self.assertIn('net/minecraft/world/entity/player/Player',types)
            self.assertIn('net/minecraft/world/entity/projectile/AbstractArrow',types)
        b=self.body('TORMENTOREntityIsHurtProcedure')
        self.assertEqual([i['offset'] for i in b if 'EntityType.spawn(' in str(i['operand'])],[110,158])
        self.assertFalse(any('tormentor_hitbox_split' in str(i['operand']) and i['opcode']=='0xb5' for i in b))
        self.assertFalse(any('.setOwner(' in str(i['operand']) for i in b))

    def test_delayed_respawn_only_rechecks_original_presence(self):
        b=self.body('TORMENTOROnInitialEntitySpawnProcedure','lambda$execute$5')
        self.assertTrue(any('List.isEmpty()' in str(i['operand']) for i in b))
        self.assertTrue(any(i['operand']==200.0 for i in b))
        self.assertTrue(any('.spawn(' in str(i['operand']) and i['offset']==78 for i in b))
        self.assertFalse(any('tormentor_seal_limit' in str(i['operand']) or 'isAlive(' in str(i['operand']) or 'AscendSphere' in str(i['operand']) for i in b))

    def test_tier_follow_is_five_same_offset_teleports_not_damage(self):
        b=self.body('TormentorTestOnEntityTickUpdateProcedure')
        offsets=[i['offset'] for i in b if '.teleportTo(' in str(i['operand'])]
        self.assertEqual(offsets,[203,643,1083,1523,1963])
        for offset in offsets:
            at=next(j for j,i in enumerate(b) if i['offset']==offset)
            self.assertTrue(any(i['operand']==.7 for i in b[at-12:at]))
        self.assertFalse(any('.hurt(' in str(i['operand']) for i in b))
        self.assertTrue(any('.removeAllEffects(' in str(i['operand']) and i['offset']==3648 for i in b))
        self.assertTrue(any('.setHealth(' in str(i['operand']) and i['offset']==3689 for i in b))

    def test_closure_notification_sets_health_then_anonymous_segment_request(self):
        b=self.body('TormentorTestOnEntityTickUpdateProcedure','lambda$execute$3');by={i['offset']:i for i in b}
        self.assertEqual((by[52]['operand'],by[82]['operand']),(1.0,100.0))
        self.assertIn('.setHealth(',by[53]['operand']);self.assertIn('.hurt(',by[85]['operand'])
        self.assertIn('DamageSource.<init>(Lnet/minecraft/core/Holder;)V',by[79]['operand'])
        self.assertEqual(by[65]['operand'],'arphex:segment');self.assertEqual(by[88]['opcode'],'0x57')

    def test_death_command_is_test_only_for_all_five_callers(self):
        for root in ['TormentorTestEntity']+['TormentorT'+str(t)+'Entity' for t in range(2,6)]:
            b=self.body(root,'tickDeath');by={i['offset']:i for i in b}
            self.assertEqual(by[14]['operand'],1300)
            self.assertIn('.remove(',by[24]['operand'])
            self.assertIn('TormentorTestDeathTimeIsReachedProcedure.execute(',by[48]['operand'])
        self.assertTrue(any(i['operand']=='arphex despawn @e[type=arphex:tormentor_test]' for i in self.body('TormentorTestDeathTimeIsReachedProcedure')))

    def test_presentation_clock_and_overlay_have_no_authored_offense_consumer(self):
        from collect_combat_census import decode_sites
        roots={'net/arphex/entity/'+r+'.class' for r in ['TormentorTestEntity']+['TormentorT'+str(t)+'Entity' for t in range(2,6)]}
        refs={(m['entry'],m['method'].split('(')[0]) for m in self.census['methods']
              if any('DATA_big_attack' in str(s.get('operand')) for s in decode_sites(self.census,m,'hits'))}
        self.assertTrue(refs)
        self.assertTrue(all((e in roots and name in {'defineSynchedData','addAdditionalSaveData','readAdditionalSaveData','<clinit>'}) or
                            (e.endswith('/TormentorTestOnEntityTickUpdateProcedure.class') and name=='execute') for e,name in refs))
        b=self.body('TORMENTORThisEntityKillsAnotherOneProcedure')
        self.assertTrue(any('show_tormentor_overlayZ' in str(i['operand']) and i['opcode']=='0xb5' for i in b))
        self.assertFalse(any('.hurt(' in str(i['operand']) or '.addEffect(' in str(i['operand']) or '.heal(' in str(i['operand']) for i in b))
        self.assertFalse(any(c['primitive']=='NATIVE_CONDITIONAL_MELEE' for r in self.batch['effects'] for c in r['scalable_parameter_candidates']))


class NativeForcefieldDirectionTests(NativeContractHarness, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch=read_json(OUT/'arphex-r2m5v-native-forcefield-direction-transient-carriers.json')
        cls.native=read_json(OUT/'native-evidence/arphex-native-display-control-carriers.json')
        cls.census=read_json(OUT/'arphex-combat-census.json')

    def test_seven_roots_reuse_known_hazards_without_duplicate_consumers(self):
        validate_batch(self.batch,self.prior(),self.census)
        self.assertEqual((len(self.batch['effects']),len(self.batch['closed_actor_callback_entries'])),(2,7))
        self.assertEqual(sum(len(c['parameters']) for r in self.batch['effects'] for c in r['scalable_parameter_candidates']),13)
        self.assertEqual((len(self.native['witnesses']),sum(len(w['methods']) for w in self.native['witnesses'])),(24,177))
        for root in ('SphereAnimEntity','BlockTestEntity'):
            self.assertFalse(any(w['entry'].endswith('/'+root+'.class') for w in self.native['witnesses']))
        review=read_json(OUT/'mod-reviews/arphex.json')
        for proof in self.batch['reused_closed_actor_contracts']:
            r=next(r for r in review['effects'] if r['id']==proof['canonical_id'])
            self.assertTrue(any(p['entry']==proof['entry'] for p in r['implementation']))

    def test_block_placement_writes_actual_placer_uuid_to_block_data(self):
        b=self.body('AscendedCubeBlockIsPlacedByProcedure');by={i['offset']:i for i in b}
        self.assertIn('.getStringUUID(',by[121]['operand'])
        self.assertIn('.putString(',by[124]['operand'])
        self.assertTrue(any(i['operand']=='ascendedowner' for i in b))
        b=self.body('AscendSphereAnimOnEntityTickUpdateProcedure$1','getValue')
        self.assertTrue(any('.getBlockEntity(' in str(i['operand']) for i in b))
        self.assertTrue(any('.getPersistentData(' in str(i['operand']) for i in b))
        self.assertTrue(any('.getString(' in str(i['operand']) for i in b))

    def test_block_timer_has_native_transfer_and_fifty_tick_delivery(self):
        for m,offset in [('onPlace',14),('tick',31)]:
            b=self.body('AscendedCubeBlock',m);by={i['offset']:i for i in b}
            self.assertEqual(by[offset]['operand'],50)
            self.assertTrue(any('.scheduleTick(' in str(i['operand']) for i in b))
        b=self.body('AscendedCubeOnTickUpdateProcedure')
        setter=next(i['offset'] for i in b if 'SynchedEntityData.set(' in str(i['operand']) and i['offset']>200)
        clear=next(i['offset'] for i in b if '.putDouble(' in str(i['operand']))
        self.assertLess(setter,clear)
        self.assertTrue(any(i['operand']=='expel_enemies' for i in b))

    def test_barrier_state_is_decremented_before_motion_and_payload_disposal(self):
        b=self.body('AscendSphereAnimOnEntityTickUpdateProcedure');by={i['offset']:i for i in b}
        self.assertIn('SynchedEntityData.set(',by[257]['operand'])
        self.assertIn('.setDeltaMovement(',by[977]['operand'])
        self.assertIn('.discard(',by[1381]['operand'])
        self.assertIn('.removeAllEffects(',by[1546]['operand'])
        self.assertTrue(any(i['opcode']=='0x64' and i['offset']<257 for i in b))
        self.assertFalse(any('.hurt(' in str(i['operand']) or '.isAlliedTo(' in str(i['operand']) for i in b))

    def test_native_resistance_and_hand_cooldowns_are_separate_consumers(self):
        b=self.body('AscendSphereAnimOnEntityTickUpdateProcedure');by={i['offset']:i for i in b}
        self.assertIn('.addEffect(',by[1075]['operand'])
        self.assertIn('.addCooldown(',by[1170]['operand'])
        self.assertIn('.addCooldown(',by[1261]['operand'])
        r=self.row('ascended_cube_native_owner_forcefield_repulsion_and_payload_admission')
        cooldown=next(c for c in r['scalable_parameter_candidates'] if c['primitive']=='NONOWNER_ETHEREAL_COOLDOWN')
        self.assertEqual(cooldown['additional_consumer_sites'][0]['offset'],1261)

    def test_transient_roots_do_not_turn_unused_attack_seventy_into_damage(self):
        change=self.batch['record_refinements'][0]
        self.assertEqual(change['id'],'arphex:recluse_display_native_transient_spider_callbacks')
        self.assertFalse(change.get('candidate_additions'))
        for root in ('TormentorFlashAnimEntity','TormentorLowDisplayAnimEntity','TormentorLowDisplayEntity'):
            b=self.body(root,'baseTick')
            self.assertTrue(any('RecluseAnim1OnEntityTickUpdateProcedure.execute(' in str(i['operand']) for i in b))
            b=self.body(root,'registerGoals')
            self.assertFalse(any('MeleeAttackGoal' in str(i['operand']) or 'NearestAttackableTargetGoal' in str(i['operand']) for i in b))
            for m in ('canUse','canContinueToUse'):
                self.assertTrue(any('TormentorLookAroundProcedure.execute(' in str(i['operand']) for i in self.body(root+'$1',m)))
        b=self.body('TormentorLookAroundProcedure')
        self.assertTrue(any('MobEffects.BLINDNESS' in str(i['operand']) for i in b))

    def test_warp_first_qualifier_latches_before_native_uuid_equality(self):
        b=self.body('WarpStaffDirectionOnEntityTickUpdateProcedure');by={i['offset']:i for i in b}
        self.assertIn('.putString(',by[347]['operand'])
        eq=next(j for j,i in enumerate(b) if '.equals(' in str(i['operand']))
        preceding=b[eq-12:eq]
        self.assertTrue(any(i['operand']==1 and i['opcode']=='0x4' for i in preceding))
        self.assertIn('.teleportTo(',by[501]['operand'])
        self.assertFalse(any('.setOwner(' in str(i['operand']) or '.tame(' in str(i['operand']) for i in b))
        self.assertTrue(any(i['operand']=='data merge entity @s {NoAI:1}' for i in b))


class NativeStalkerCarrierTests(NativeContractHarness, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch=read_json(OUT/'arphex-r2m5u-native-stalker-ghost-contracts.json')
        cls.native=read_json(OUT/'native-evidence/arphex-stalker-native-families.json')
        cls.census=read_json(OUT/'arphex-combat-census.json')

    def test_five_roots_four_new_contracts_one_shared_caller(self):
        validate_batch(self.batch,self.prior(),self.census)
        self.assertEqual((len(self.batch['effects']),len(self.batch['closed_actor_callback_entries'])),(4,5))
        self.assertEqual(sum(len(c['parameters']) for r in self.batch['effects'] for c in r['scalable_parameter_candidates']),48)
        self.assertEqual((len(self.native['witnesses']),sum(len(w['methods']) for w in self.native['witnesses'])),(151,721))
        self.assertEqual(self.batch['record_refinements'][0]['id'],
                         'arphex:prowler_reaper_native_hanging_terrain_and_shared_incoming_motion')
        self.assertFalse(self.batch['record_refinements'][0].get('candidate_additions'))

    def test_ghost_nested_target_gate_is_not_a_single_target_read(self):
        b=self.body('TeleportGhostOnEntityTickUpdateProcedure');by={i['offset']:i for i in b}
        self.assertIn('.getTarget(',by[1514]['operand'])
        self.assertEqual(by[1525]['opcode'],'0xc1')
        self.assertEqual(by[1525]['operand'],'net/minecraft/world/entity/Mob')
        self.assertIn('.getTarget(',by[1540]['operand'])
        self.assertEqual(by[1547]['opcode'],'0xc6')
        self.assertTrue(any('sort=nearest' in str(i['operand']) and '^0.12' in str(i['operand']) for i in b))

    def test_ghost_contact_and_incoming_source_are_native_and_distinct(self):
        b=self.body('TeleportGhostEntity$1','tick')
        self.assertTrue(any('.intersects(' in str(i['operand']) for i in b))
        self.assertTrue(any('.doHurtTarget(' in str(i['operand']) for i in b))
        b=self.body('TeleportGhostEntity','hurt')
        causing=next(i['offset'] for i in b if '.getEntity(' in str(i['operand']))
        helper=next(i['offset'] for i in b if 'TeleportGhostEntityIsHurtProcedure.execute(' in str(i['operand']))
        rejection=next(i['offset'] for i in b if 'DamageTypes.IN_FIRE' in str(i['operand']))
        self.assertLess(causing,helper);self.assertLess(helper,rejection)
        self.assertFalse(any(i['opcode']=='0xc1' and 'AbstractArrow' in str(i['operand']) for i in b))

    def test_pure_spawn_native_delays_and_replacement_continue_after_discard(self):
        b=self.body('PureStalkingOnInitialEntitySpawnProcedure');by={i['offset']:i for i in b}
        self.assertEqual([by[o]['operand'] for o in (3219,3309,3327,3345)],[200,180,500,600])
        q=self.body('PureStalkingOnInitialEntitySpawnProcedure','lambda$execute$83')
        discard=next(i['offset'] for i in q if '.discard(' in str(i['operand']))
        spawns=[i['offset'] for i in q if 'EntityType.spawn(' in str(i['operand'])]
        self.assertEqual(len(spawns),2);self.assertTrue(all(o>discard for o in spawns))
        self.assertFalse(any('.isAlive(' in str(i['operand']) for i in q))

    def test_invisible_clock_is_updated_before_teleport_and_navigation_after(self):
        b=self.body('InvisibleStalkerOnEntityTickUpdateProcedure');by={i['offset']:i for i in b}
        self.assertEqual([by[o]['operand'] for o in (213,215)],[20,1600])
        self.assertIn('.putDouble(',by[222]['operand'])
        self.assertIn('.teleportTo(',by[586]['operand'])
        self.assertIn('.putDouble(',by[1725]['operand'])
        w=next(w for w in self.native['witnesses'] if w['entry'].endswith('/InvisibleStalkerOnEntityTickUpdateProcedure.class'))
        removal=[m['instructions'] for m in w['methods'] if m['name'].startswith('lambda$execute$') and any('.discard(' in str(i['operand']) for i in m['instructions'])]
        self.assertEqual(len(removal),1);q=removal[0]
        self.assertTrue(any('.nextInt(' in str(i['operand']) for i in q))
        self.assertFalse(any('.isAlive(' in str(i['operand']) or '.getDouble(' in str(i['operand']) for i in q))

    def test_invisible_incoming_darkness_targets_self_after_discard(self):
        b=self.body('InvisibleStalkerEntityIsHurtProcedure')
        discard=next(i['offset'] for i in b if '.discard(' in str(i['operand']))
        self.assertLess(discard,57)
        self.assertTrue(any(i['offset']==57 and '.addEffect(' in str(i['operand']) for i in b))
        r=self.row('invisible_stalker_native_invisibility_clock_teleport_and_admission')
        c=next(c for c in r['scalable_parameter_candidates'] if c['primitive']=='MOB_EFFECT_INCOMING_SELF_DARKNESS')
        self.assertEqual(c['native_receiver_role'],'SELFafterdiscard')

    def test_sky_motion_has_independent_x_angle_and_ordered_vertical_overwrite(self):
        b=self.body('SkyStalkerOnEntityTickUpdateProcedure');by={i['offset']:i for i in b}
        self.assertEqual([by[o]['operand'] for o in (685,687)],[60,300])
        self.assertIn('.nextInt(',by[690]['operand'])
        for off in (729,1144,1615,2096,2154,2713):
            self.assertIn('.setDeltaMovement(',by[off]['operand'])
        self.assertFalse(any('.hurt(' in str(i['operand']) for i in b))
        r=self.row('sky_stalker_native_silk_flight_moth_delivery_and_lifecycle')
        self.assertFalse(any(c['primitive']=='NATIVE_CONDITIONAL_MELEE' for c in r['scalable_parameter_candidates']))

    def test_giant_calls_locked_helpers_even_though_constructor_disables_ai(self):
        b=self.body('GiantEnemySpiderEntity','<init>')
        j=next(j for j,i in enumerate(b) if '.setNoAi(' in str(i['operand']))
        self.assertEqual(b[j-1]['operand'],1)
        for meth,helper in [('baseTick','ReaperTickProcedure'),('hurt','SpiderProwlerEntityIsHurtProcedure'),
                            ('finalizeSpawn','SpiderWanderOnInitialEntitySpawnProcedure')]:
            self.assertTrue(any(helper+'.execute(' in str(i['operand']) for i in self.body('GiantEnemySpiderEntity',meth)))
        self.assertFalse(any(w['entry'].endswith('/ReaperTickProcedure.class') for w in self.native['witnesses']))


class NativeMothCarrierTests(NativeContractHarness, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch=read_json(OUT/'arphex-r2m5t-native-moth-hitbox-contracts.json')
        cls.native=read_json(OUT/'native-evidence/arphex-moth-native-families.json')
        cls.census=read_json(OUT/'arphex-combat-census.json')

    def test_four_roots_and_unique_consumers_reuse_existing_payloads(self):
        validate_batch(self.batch,self.prior(),self.census)
        self.assertEqual((len(self.batch['effects']),len(self.batch['closed_actor_callback_entries'])),(4,4))
        self.assertEqual(sum(len(c['parameters']) for r in self.batch['effects'] for c in r['scalable_parameter_candidates']),134)
        self.assertEqual((len(self.native['witnesses']),sum(len(w['methods']) for w in self.native['witnesses'])),(56,357))
        self.assertFalse(any(w['entry'].endswith('/DraconicTickProcedure.class') or
                             w['entry'].endswith('/BloodProjectileEntity.class') for w in self.native['witnesses']))
        self.assertFalse(self.batch['whole_mod_complete'])

    def test_native_kill_score_helpers_receive_victim_not_killer(self):
        for actor in ('SpiderMothEntity','SpiderMothDwellerEntity'):
            b=self.body(actor,'awardKillScore')
            j=next(j for j,i in enumerate(b) if 'KillsAnother' in str(i['operand']))
            self.assertEqual(b[j-1]['opcode'],'0x2b')  # parameter local1, not SELF local0
            self.assertTrue(any('Monster.awardKillScore(' in str(i['operand']) for i in b[:j]))
        b=self.body('SpiderMothLarvaeEntity','awardKillScore')
        j=next(j for j,i in enumerate(b) if 'KillsAnother' in str(i['operand']))
        self.assertEqual([i['opcode'] for i in b[j-2:j]],['0x2b','0x2a'])
        b=self.body('SpiderMothLarvaeThisEntityKillsAnotherOneProcedure')
        self.assertTrue(any(i['opcode']=='0xc1' and i['operand']=='net/minecraft/world/entity/player/Player' for i in b))
        j=next(j for j,i in enumerate(b) if '.discard(' in str(i['operand']))
        self.assertEqual(b[j-1]['opcode'],'0x2b')  # sourceentity/killer helper parameter1

    def test_native_melee_and_ranged_delivery_are_distinct(self):
        for name,value in [('SpiderMothEntity$1',5.76),('SpiderMothDwellerEntity$1',16.)]:
            b=self.body(name,'canPerformAttack')
            self.assertEqual([i['operand'] for i in b if i['opcode']=='0x14'],[value])
            self.assertTrue(any('.isTimeToAttack(' in str(i['operand']) for i in b))
        b=self.body('SpiderMothLarvaeEntity','performRangedAttack')
        self.assertTrue(any('BloodProjectileEntity.shoot(Lnet/minecraft/world/entity/LivingEntity;Lnet/minecraft/world/entity/LivingEntity;)' in str(i['operand']) for i in b))
        r=self.row('moth_larva_native_parent_target_contact_and_kill_lifecycle')
        self.assertEqual([c['primitive'] for c in r['scalable_parameter_candidates']],['NATIVE_CONDITIONAL_MELEE'])
        self.assertIn('arphex:blood_arrow_intrinsic_combat',r['canonical_contract_reuse'])

    def test_hurt_callback_uses_fresh_holder_only_sources_before_filters(self):
        b=self.body('SpiderMothEntity','hurt')
        helper=next(i['offset'] for i in b if 'SpiderMothDwellerEntityIsHurtProcedure.execute(' in str(i['operand']))
        exclusion=next(i['offset'] for i in b if '/DamageTypes.IN_FIRE' in str(i['operand']))
        self.assertLess(helper,exclusion)
        b=self.body('SpiderMothDwellerEntityIsHurtProcedure')
        self.assertEqual(sum('.isDirect()Z' in str(i['operand']) for i in b),2)
        self.assertEqual(sum('DamageSource.<init>(Lnet/minecraft/core/Holder;)V' in str(i['operand']) for i in b),2)
        self.assertFalse(any('.hurt(' in str(i['operand']) for i in b))

    def test_raw_and_synched_grow_flags_are_independent_native_stores(self):
        b=self.body('SpiderMothDwellerEntityIsHurtProcedure')
        self.assertTrue(any(i['operand']=='growattack' for i in b))
        q=self.body('SpiderMothDwellerEntityIsHurtProcedure','lambda$execute$13')
        self.assertTrue(any('SpiderMothEntity.DATA_growattack' in str(i['operand']) for i in q))
        self.assertFalse(any(i['operand']=='growattack' for i in q))
        q=self.body('SpiderMothDwellerEntityIsHurtProcedure','lambda$execute$16')
        self.assertTrue(any('SpiderMothEntity.DATA_growattack' in str(i['operand']) for i in q))
        b=self.body('SpiderMothTickProcedure')
        self.assertTrue(any(i['operand']=='growattack' for i in b))
        self.assertTrue(any('SpiderMothEntity.DATA_growattack' in str(i['operand']) for i in b))

    def test_flight_delays_use_cached_native_time_but_delivery_checks_current_effect(self):
        b=self.body('SpiderMothDwellerEntityIsHurtProcedure');by={i['offset']:i for i in b}
        self.assertEqual([by[off]['operand'] for off in (848,851,929,955,981,1007)],[200,600,4.,2.,100.,20.])
        for name in ('lambda$execute$5','lambda$execute$6','lambda$execute$7',
                     'lambda$execute$8','lambda$execute$9','lambda$execute$10','lambda$execute$11'):
            q=self.body('SpiderMothDwellerEntityIsHurtProcedure',name)
            self.assertTrue(any('ArphexModMobEffects.FORCE_POWER' in str(i['operand']) for i in q))
            self.assertTrue(any('.hasEffect(' in str(i['operand']) for i in q))
        r=self.row('moth_native_stare_flight_counterattack_setup_and_control')
        fly=next(c for c in r['components'] if c['primitive']=='FORCE_POWER_FLYTIME')
        self.assertEqual(fly['numerical_parameters'],{'minimum':200,'maximum':600})

    def test_moth_command_selectors_do_not_imply_callback_actor_or_query_recipient(self):
        b=self.body('SpiderMothTickProcedure')
        commands=[i['operand'] for i in b if isinstance(i['operand'],str)]
        self.assertIn('attribute @e[type=arphex:spider_moth,limit=1] minecraft:generic.attack_knockback base set 500',commands)
        self.assertIn('effect give @p darkness 8 1 true',commands)
        self.assertIn('effect give @p[gamemode=survival] darkness 5 0',commands)
        self.assertIn('effect give @p[gamemode=survival,distance=..2] darkness 1 0',commands)
        self.assertIn('execute as @e[type=arphex:spider_moth,limit=1,sort=nearest] run data merge entity @s {Invulnerable:1}',commands)
        self.assertFalse(any('.hurt(' in str(i['operand']) for i in b))

    def test_moth_spawn_has_no_local_spawnedaway_writer(self):
        b=self.body('SpiderMothDwellerOnInitialEntitySpawnProcedure')
        self.assertFalse(any(i['operand']=='spawnedawayfromplayer' for i in b))
        self.assertTrue(any(i['operand']=='minimumlifetime' for i in b))
        b=self.body('SpiderMothTickProcedure')
        self.assertTrue(any(i['operand']=='spawnedawayfromplayer' for i in b))
        self.assertTrue(any('PlayerVariables.mothsurvivalsD' in str(i['operand']) for i in b))
        self.assertTrue(any(i['operand']=='mothsurvivals' for i in b))

    def test_voidlasher_spawn_immunity_delivery_does_not_clear_native_despawning_flag(self):
        b=self.body('VoidlasherSpawnProcedure')
        self.assertEqual(sum(i['operand']=='despawning' for i in b),3)
        w=next(w for w in self.native['witnesses'] if w['entry'].endswith('/VoidlasherSpawnProcedure.class'))
        q=[m for m in w['methods'] if any('.discard(' in str(i['operand']) for i in m['instructions'])]
        self.assertEqual(len(q),3)
        for m in q:
            self.assertTrue(any('ArphexModMobEffects.DESPAWN_IMMUNITY' in str(i['operand']) for i in m['instructions']))
            self.assertFalse(any(i['operand']=='despawning' for i in m['instructions']))
        r=self.row('voidlasher_native_root_spawn_status_and_victim_regen')
        self.assertIn('arphex:draconic_native_teleport_and_lifecycle',r['canonical_contract_reuse'])

    def test_hitbox_copies_vehicle_health_without_creating_authored_health_scalar(self):
        b=self.body('ExpandHitboxProcedure')
        self.assertTrue(any('.getVehicle(' in str(i['operand']) for i in b))
        self.assertTrue(any(i['offset']==74 and '.setHealth(F)V' in str(i['operand']) for i in b))
        self.assertFalse(any('.heal(' in str(i['operand']) or '.hurt(' in str(i['operand']) for i in b))
        self.assertFalse(any('.setOwner(' in str(i['operand']) for i in b))
        r=self.row('moth_hitbox_native_rider_health_mirror_and_admission')
        self.assertEqual({c['primitive'] for c in r['scalable_parameter_candidates']},
                         {'MOB_EFFECT_UNMOUNTED_MOTH_INVISIBILITY','DELAYED_UNMOUNTED_REMOVAL'})
        j=next(j for j,i in enumerate(b) if '.startRiding(' in str(i['operand']))
        self.assertEqual(b[j+1]['opcode'],'0x57')


class NativeMatriarchHallucinationTests(NativeContractHarness, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch=read_json(OUT/'arphex-r2m5s-matriarch-hallucination-native-contracts.json')
        cls.native=read_json(OUT/'native-evidence/arphex-matriarch-hallucination-native-families.json')
        cls.census=read_json(OUT/'arphex-combat-census.json')

    def test_five_roots_four_new_contracts_one_reused_caller(self):
        validate_batch(self.batch,self.prior(),self.census)
        self.assertEqual((len(self.batch['effects']),len(self.batch['closed_actor_callback_entries'])),(4,5))
        self.assertEqual(sum(len(c['parameters']) for r in self.batch['effects'] for c in r['scalable_parameter_candidates']),54)
        self.assertEqual((len(self.native['witnesses']),sum(len(w['methods']) for w in self.native['witnesses'])),(28,190))
        changes=self.batch['record_refinements'];self.assertEqual(len(changes),1)
        self.assertEqual(changes[0]['id'],'arphex:shared_chaser_hallucination_native_callback')
        self.assertFalse(changes[0].get('candidate_additions'))
        self.assertTrue(any('HallucinationScorpioidTickProcedure.execute(' in str(i['operand'])
                            for i in self.body('SpiderChaserHallucination2Entity','baseTick')))

    def test_native_melee_ranges_and_spider_parent_remain_distinct(self):
        for name,value in [('SpiderMatriarchEntity$1',36.),('SpiderMatriarchLarvaeEntity$1',1.),
                           ('SpiderChaserHallucination2Entity$1',12.25),('SpiderChaserHallucination3Entity$1',4.)]:
            b=self.body(name,'canPerformAttack')
            self.assertEqual([i['operand'] for i in b if i['opcode'] in ('0xf','0x14')],[value])
            self.assertTrue(any('.hasLineOfSight(' in str(i['operand']) for i in b))
        b=self.body('SpiderChaserHallucination3Entity','registerGoals')
        parent=next(i['offset'] for i in b if i['operand']=='net/minecraft/world/entity/monster/Spider.registerGoals()V')
        local=next(i['offset'] for i in b if '.addGoal(' in str(i['operand']))
        self.assertLess(parent,local)

    def test_hatch_sideeffects_precede_rejected_incoming_hurt(self):
        b=self.body('SpiderMatriarchEntity','hurt')
        helper=next(i['offset'] for i in b if 'SpiderMatriarchEntityIsHurtProcedure.execute(' in str(i['operand']))
        exclusion=next(i['offset'] for i in b if '/DamageTypes.IN_FIRE' in str(i['operand']))
        self.assertLess(helper,exclusion)
        b=self.body('SpiderMatriarchEntityIsHurtProcedure');by={i['offset']:i for i in b}
        self.assertEqual((by[139]['operand'],by[141]['opcode'],by[141]['branch_target']),(6,'0xa2',224))
        self.assertEqual(by[221]['branch_target'],137)
        self.assertTrue(any(i['offset']==178 and 'EntityType.spawn(' in str(i['operand']) for i in b))
        self.assertFalse(any('.setOwner(' in str(i['operand']) or '.tame(' in str(i['operand']) for i in b))

    def test_hatch_setup_writes_current_neighbor_growth_distribution(self):
        from promote_combat_batch import synched_int_distribution_binding
        b=self.body('SpiderMatriarchEntityIsHurtProcedure','lambda$execute$2')
        binding=synched_int_distribution_binding(dict(instructions=b),148)
        self.assertEqual((binding['native_minimum'],binding['native_maximum']),(300,9000))
        self.assertIn('SpiderMatriarchLarvaeEntity.DATA_grow',binding['accessor_symbol'])
        self.assertTrue(any('net/arphex/entity/SpiderMatriarchLarvaeEntity'==i['operand'] and i['opcode']=='0xc1' for i in b))
        self.assertFalse(any('.isAlive(' in str(i['operand']) or '.getOwner(' in str(i['operand']) for i in b))
        changed=copy.deepcopy(self.batch);r=next(r for r in changed['effects'] if 'matriarch_native_lunge' in r['id'])
        next(c for c in r['components'] if c['primitive']=='NATIVE_CLOCK_DISTRIBUTION')['numerical_parameters']['maximum']=9001
        with self.assertRaises(AssertionError):validate_batch(changed,self.prior(),self.census)

    def test_larval_growth_stops_before_largest_physical_branch(self):
        b=self.body('SpiderMatriarchLarvaeOnEntityTickUpdateProcedure');by={i['offset']:i for i in b}
        self.assertEqual((by[37]['operand'],by[40]['branch_target']),(12000,226))
        self.assertEqual((by[75]['operand'],by[78]['branch_target']),(8000,226))
        self.assertEqual((by[218]['operand'],by[219]['opcode']),(2,'0x60'))
        self.assertEqual(sum('SynchedEntityData.set(' in str(i['operand']) for i in b),1)
        shape=self.body('MatriarchLarvaeHitboxScaleProcedure');by={i['offset']:i for i in shape}
        self.assertEqual((by[38]['operand'],by[78]['operand']),(11990,6000))
        self.assertEqual([by[off]['operand'] for off in (44,84,88)],[1.,.7,.4])
        b=self.body('SpiderMatriarchLarvaeEntity','getDefaultDimensions')
        self.assertTrue(any('MatriarchLarvaeHitboxScaleProcedure.execute(' in str(i['operand']) for i in b))
        self.assertTrue(any('EntityDimensions.scale(F)' in str(i['operand']) for i in b))

    def test_matriarch_explosion_is_anonymous_and_separate_from_melee(self):
        b=self.body('SpiderMatriarchOnEntityTickUpdateProcedure');by={i['offset']:i for i in b}
        self.assertEqual(by[922]['operand'],7.)
        self.assertIn('ExplosionInteraction.MOB',by[924]['operand'])
        self.assertTrue(any(i['opcode']=='0x1' for i in b if 900<=i['offset']<907))
        self.assertFalse(any('.hurt(' in str(i['operand']) for i in b))
        self.assertTrue(any('DATA_store_target_distance' in str(i['operand']) for i in b))
        self.assertEqual([by[off]['operand'] for off in (995,1062,1125)],[.3,.3,.3])

    def test_hallucination3_two_ignored_anonymous_magic_requests(self):
        b=self.body('SpiderChaserHallucination3OnEntityTickUpdateProcedure')
        for off,amount in [(319,5.),(923,6.)]:
            j=next(j for j,i in enumerate(b) if i['offset']==off)
            self.assertEqual((b[j-1]['operand'],b[j+1]['opcode']),(amount,'0x57'))
        self.assertEqual(sum('/DamageTypes.MAGIC' in str(i['operand']) for i in b),2)
        self.assertEqual(sum('DamageSource.<init>(Lnet/minecraft/core/Holder;)V' in str(i['operand']) for i in b),2)
        self.assertFalse(any('.hasLineOfSight(' in str(i['operand']) for i in b))
        r=self.row('hallucination3_native_marked_contact_target_search_and_rewards')
        self.assertFalse(any(c['primitive']=='NATIVE_CONDITIONAL_MELEE' for c in r['scalable_parameter_candidates']))

    def test_enormous_has_no_offense_and_size_is_not_physical(self):
        b=self.body('EnormousSpiderHallucinationEntity','registerGoals')
        self.assertFalse(any('AttackGoal' in str(i['operand']) for i in b))
        b=self.body('EnormousSpiderHallucinationEntity','getDefaultDimensions')
        self.assertTrue(any(i['operand']==3. for i in b))
        self.assertFalse(any('DATA_size' in str(i['operand']) for i in b))
        r=self.row('enormous_hallucination_native_motion_admission_and_lifecycle')
        self.assertFalse(any(c['primitive'] in ('BODY_DIMENSION_SCALE','NATIVE_DAMAGE_REQUEST') for c in r['scalable_parameter_candidates']))

    def test_enormous_repeated_queued_motion_has_no_server_alive_gate(self):
        b=self.body('EnormousSpiderHallucinationOnEntityTickUpdateProcedure','lambda$execute$2')
        self.assertTrue(any(i['operand']==-.8 for i in b))
        self.assertTrue(any('.setDeltaMovement(' in str(i['operand']) for i in b))
        self.assertFalse(any(x in str(i['operand']) for i in b for x in ('.isAlive(','.isClientSide(')))
        b=self.body('EnormousSpiderHallucinationOnEntityTickUpdateProcedure')
        self.assertEqual(sum('.queueServerWork(' in str(i['operand']) for i in b),3)
        self.assertTrue(any('Invulnerable:1b' in str(i['operand']) for i in b))


class NativeSpiderControlTests(NativeContractHarness, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch=read_json(OUT/'arphex-r2m5r-native-spider-control-contracts.json')
        cls.native=read_json(OUT/'native-evidence/arphex-spider-control-native-families.json')
        cls.census=read_json(OUT/'arphex-combat-census.json')

    def test_unique_consumers_and_eight_closed_roots(self):
        validate_batch(self.batch,self.prior(),self.census)
        self.assertEqual((len(self.batch['effects']),len(self.batch['closed_actor_callback_entries'])),(7,8))
        self.assertEqual(sum(len(c['parameters']) for r in self.batch['effects'] for c in r['scalable_parameter_candidates']),159)
        self.assertEqual((len(self.native['witnesses']),sum(len(w['methods']) for w in self.native['witnesses'])),(68,342))

    def test_infestor_attack_and_knockback_match_pinned_attribute_consumers(self):
        b=self.body('SpiderInfestorEntity','createAttributes')
        actual={b[j-2]['operand'].split('.')[-1].split('Lnet/')[0]:b[j-1]['operand'] for j,i in enumerate(b) if 'AttributeSupplier$Builder.add(' in str(i['operand'])}
        self.assertEqual((actual['ATTACK_DAMAGE'],actual['ATTACK_KNOCKBACK']),(15.,1.))
        row=self.row('infestor_native_stealth_reveal_crash_and_incoming_motion')
        values=next(c['numerical_parameters'] for c in row['components'] if c['primitive']=='NATIVE_CONDITIONAL_MELEE')
        self.assertEqual((values['attack'],values['native_knockback']),(15.,1.))
        self.assertIn('oneattack15/KB1',row['actual_behavior'])
        altered=copy.deepcopy(self.batch)
        row=next(r for r in altered['effects'] if 'infestor_native_' in r['id'])
        next(c for c in row['components'] if c['primitive']=='NATIVE_CONDITIONAL_MELEE')['numerical_parameters']['attack']=20.
        with self.assertRaises(AssertionError):validate_batch(altered,self.prior(),self.census)

    def test_native_melee_ranges_preserve_actor_distinctions(self):
        expected={'SpiderAmbusherEntity$3':5.76,'SpiderGoliathEntity$1':5.76,
                  'SpiderInfestorEntity$1':16.0,'SpiderObstructerEntity$1':2.25,
                  'SpiderProwlerEntity$1':5.29,'SpiderReaperEntity$1':16.0,'SpiderSinkerEntity$1':1.0}
        for name,value in expected.items():
            b=self.body(name,'canPerformAttack')
            self.assertEqual([i['operand'] for i in b if i['opcode'] in ('0xe','0xf','0x14')],[value])
            self.assertTrue(any('.hasLineOfSight(' in str(i['operand']) for i in b))
            self.assertTrue(any('.isTimeToAttack(' in str(i['operand']) for i in b))
        r=self.row('prowler_reaper_native_hanging_terrain_and_shared_incoming_motion')
        self.assertIn('Prowler5.29/Reaper16',r['actual_behavior'])
        self.assertIn('strictSq<16',self.row('infestor_native_stealth_reveal_crash_and_incoming_motion')['actual_behavior'])
        self.assertIn('strictSq<1',self.row('sinker_native_aquatic_pose_target_navigation_and_melee')['actual_behavior'])

    def test_goliath_positive_state_skips_decrement(self):
        b=self.body('SpiderGoliathOnEntityTickUpdateProcedure');by={i['offset']:i for i in b}
        self.assertEqual((by[53]['opcode'],by[53]['branch_target']),('0x9d',123))
        self.assertEqual(by[116]['opcode'],'0x64')
        self.assertEqual(by[120]['operand'],'net/minecraft/network/syncher/SynchedEntityData.set(Lnet/minecraft/network/syncher/EntityDataAccessor;Ljava/lang/Object;)V')
        self.assertEqual(by[577]['operand'],5000)
        r=self.row('goliath_native_texture_aura_climbing_and_incoming_motion')
        self.assertFalse(any(c['primitive']=='CONTROL_CADENCE' for c in r['scalable_parameter_candidates']))

    def test_ambusher_target_volumes_and_hurt_reset(self):
        b=self.body('SpiderAmbusherOnEntityTickUpdateProcedure')
        self.assertEqual(sum('.inflate(' in str(i['operand']) for i in b),4)
        self.assertEqual(sum(i['operand']==5.5 for i in b),4)
        r=self.row('ambusher_native_hanging_silk_strength_and_dive')
        self.assertFalse(any(c['primitive']=='NATIVE_DAMAGE_REQUEST' for c in r['scalable_parameter_candidates']))
        b=self.body('SpiderAmbusherEntity','hurt')
        reset=next(i['offset'] for i in b if 'SpiderAmbusherEntityIsHurtProcedure.execute(' in str(i['operand']))
        exclusion=next(i['offset'] for i in b if i['opcode']=='0xc1')
        self.assertLess(reset,exclusion)

    def test_lurker_delivery_checks_phase_but_not_water(self):
        b=self.body('SpiderLurkerOnEntityTickUpdateProcedure','lambda$execute$0')
        self.assertTrue(any(i['operand']=='drowntime' for i in b))
        self.assertTrue(any(i['operand']==10.0 for i in b))
        self.assertFalse(any(x in str(i['operand']) for i in b for x in ('.isInWater(','.isAlive(','.isClientSide(')))
        self.assertEqual(sum('.hurt(' in str(i['operand']) for i in b),1)
        self.assertTrue(any('/DamageTypes.GENERIC' in str(i['operand']) for i in b))

    def test_sinker_exact_native_clocks(self):
        from promote_combat_batch import literal_synched_int_binding
        m=dict(instructions=self.body('SpiderSinkerOnEntityTickUpdateProcedure'))
        for off,value,field in [(71,200,'DATA_float_time'),(488,50,'DATA_float_time'),(772,300,'DATA_limnav')]:
            binding=literal_synched_int_binding(m,off)
            self.assertEqual(binding['native_value'],value);self.assertIn(field,binding['accessor_symbol'])
        b=self.body('SpiderSinkerOnEntityTickUpdateProcedure')
        self.assertTrue(any(i['opcode']=='0xc1' and i['operand']=='net/minecraft/world/entity/animal/Squid' for i in b))

    def test_shared_prowler_reaper_incoming_is_one_parameter_set(self):
        r=self.row('prowler_reaper_native_hanging_terrain_and_shared_incoming_motion')
        self.assertEqual(len(r['native_actor_variants']),2)
        for a in ('SpiderProwlerEntity','SpiderReaperEntity'):
            self.assertTrue(any('SpiderProwlerEntityIsHurtProcedure.execute(' in str(i['operand']) for i in self.body(a,'hurt')))
        b=self.body('SpiderProwlerEntityIsHurtProcedure')
        self.assertTrue(any(i['opcode']=='0xc1' and i['operand']=='net/arphex/entity/SpiderProwlerEntity' for i in b))
        cs=[c for c in r['scalable_parameter_candidates'] if c['primitive']=='SHARED_INCOMING_OBSTACLE_DESCENT']
        self.assertEqual(len(cs),1);self.assertEqual(len(cs[0]['additional_consumer_sites']),2)

    def test_reaper_client_server_status_is_not_active_candidate(self):
        b=self.body('ReaperTickProcedure')
        self.assertTrue(any('LevelAccessor.isClientSide(' in str(i['operand']) and i['offset']<866 for i in b))
        self.assertTrue(any('Level.isClientSide(' in str(i['operand']) and 709<i['offset']<866 for i in b))
        r=self.row('prowler_reaper_native_hanging_terrain_and_shared_incoming_motion')
        self.assertFalse(any(c['native_consumer']['entry'].endswith('/ReaperTickProcedure.class')
                             and c['native_consumer']['offset']==863 for c in r['scalable_parameter_candidates']))

    def test_infestor_native_explosion_and_anonymous_area_are_distinct(self):
        b=self.body('SpiderInfestorOnEntityTickUpdateProcedure');by={i['offset']:i for i in b}
        self.assertEqual(by[2470]['opcode'],'0x1');self.assertEqual(by[2475]['operand'],8.0)
        self.assertIn('ExplosionInteraction.MOB',by[2478]['operand'])
        self.assertIn('.explode(',by[2481]['operand']);self.assertIn('.hurt(',by[2664]['operand'])
        r=self.row('infestor_native_stealth_reveal_crash_and_incoming_motion')
        cs=[c for c in r['scalable_parameter_candidates'] if c['primitive'] in ('NATIVE_EXPLOSION','NATIVE_DAMAGE_REQUEST')]
        self.assertEqual(len(cs),2)
        self.assertTrue(any('/DamageTypes.GENERIC' in c.get('native_damage_type_symbol','')
                            and c['native_damage_source_constructor'].endswith('(Lnet/minecraft/core/Holder;)V') for c in cs))
        self.assertEqual(next(c for c in r['components'] if c['primitive']=='NATIVE_DAMAGE_REQUEST')['numerical_parameters']['crash_area_request'],20.)

    def test_infestor_clock_is_bound_to_real_distribution(self):
        from promote_combat_batch import synched_int_distribution_binding
        m=dict(instructions=self.body('SpiderInfestorOnEntityTickUpdateProcedure'))
        b=synched_int_distribution_binding(m,195)
        self.assertEqual((b['native_minimum'],b['native_maximum']),(600,2400))
        self.assertIn('DATA_ontheprowl',b['accessor_symbol'])
        changed=copy.deepcopy(self.batch);r=next(r for r in changed['effects'] if 'infestor_native_' in r['id'])
        next(c for c in r['components'] if c['primitive']=='NATIVE_CLOCK_DISTRIBUTION')['numerical_parameters']['maximum']=2401
        with self.assertRaises(AssertionError):validate_batch(changed,self.prior(),self.census)

    def test_obstructer_helper_names_do_not_define_their_meaning(self):
        b=self.body('BeingRiddenProcedure')
        self.assertTrue(any('.isVehicle(' in str(i['operand']) for i in b))
        self.assertEqual(b[-1]['opcode'],'0xac')
        b=self.body('AttackTargetReturnProcedure')
        self.assertTrue(any('.getTarget(' in str(i['operand']) for i in b))
        b=self.body('ObstructMoveProcedure')
        self.assertTrue(any(i['operand']==1.55 for i in b))
        self.assertTrue(any('TRAPDOOR_GRASS' in str(i['operand']) for i in b))

    def test_obstructer_build_and_release_native_gates(self):
        b=self.body('SpiderObstructerOnEntityTickUpdateProcedure')
        self.assertFalse(any('RULE_MOBGRIEFING' in str(i['operand']) or 'ARPHEX_GRIEFING' in str(i['operand']) for i in b))
        self.assertEqual(sum('.setBlock(' in str(i['operand']) for i in b),5)
        q=self.body('SpiderObstructerOnEntityTickUpdateProcedure','lambda$execute$11')
        self.assertTrue(any('.stopRiding(' in str(i['operand']) for i in q))
        self.assertFalse(any('isAlive(' in str(i['operand']) for i in q))
        self.assertEqual(sum(i['operand']=='target_in_burrow' for i in q),2)
        self.assertTrue(any(i['opcode']=='0x67' for i in q))
        r=self.row('obstructer_native_burrow_admission_capture_motion_and_release')
        home=next(c for c in r['scalable_parameter_candidates'] if c['primitive']=='IDLE_HOME_TELEPORT')
        self.assertEqual(home['native_consumer']['offset'],2997)
        self.assertEqual([s['offset'] for s in home['additional_consumer_sites']],[4415,5521,7632])


class NativeSummonCarrierTests(NativeContractHarness, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch=read_json(OUT/'arphex-r2m5q-native-summon-carrier-contracts.json')
        cls.native=read_json(OUT/'native-evidence/arphex-summon-carrier-native-families.json')
        cls.census=read_json(OUT/'arphex-combat-census.json')

    def test_exact_native_consumers_and_reused_scarab(self):
        validate_batch(self.batch,self.prior(),self.census)
        self.assertEqual((len(self.batch['effects']),len(self.batch['closed_actor_callback_entries'])),(6,8))
        self.assertEqual(sum(len(c['parameters']) for r in self.batch['effects'] for c in r['scalable_parameter_candidates']),115)
        self.assertEqual((len(self.native['witnesses']),sum(len(w['methods']) for w in self.native['witnesses'])),(63,402))
        self.assertFalse(any('/ScarabSummonEntity' in w['entry'] for w in self.native['witnesses']))
        self.assertEqual(self.batch['reused_closed_actor_contracts'][0]['mechanic_id'],'arphex:scarab_native_family')
        self.assertFalse(any('scarab' in r['id'] for r in self.batch['effects']))

    def test_moontracker_yboost_reads_updated_flyboost(self):
        b=self.body('MothTickProcedure');span=[i for i in b if 1945<=i['offset']<=1966]
        self.assertEqual([i['operand'] for i in span if i['opcode'] in ('0x12','0x13')],['yboost','flyboost'])
        self.assertTrue(any(i['opcode']=='0x67' for i in span))
        self.assertTrue(any(i['offset']==1902 and '.putDouble(' in str(i['operand']) for i in b))

    def test_moontracker_has_real_food_but_no_attack_goal(self):
        b=self.body('MothMoontrackerEntity','registerGoals')
        self.assertFalse(any('AttackGoal' in str(i['operand']) for i in b))
        self.assertTrue(any('BreedGoal' in str(i['operand']) for i in b))
        self.assertTrue(any('Blocks.MOSS_CARPET' in str(i['operand']) for i in self.body('MothMoontrackerEntity','isFood')))
        r=self.row('moontracker_native_silk_light_flight_owner_and_lifecycle')
        self.assertFalse(any(c['primitive']=='NATIVE_CONDITIONAL_MELEE' for c in r['scalable_parameter_candidates']))

    def test_hornet_lifetime_is_zero_or_increment_not_initialised(self):
        b=self.body('HornetProjectileOnInitialEntitySpawnProcedure')
        self.assertEqual([i['operand'] for i in b if i['opcode'] in ('0x12','0x13')],['boostlim_wasp'])
        b=self.body('HornetProjectileOnEntityTickUpdateProcedure')
        zero=[i for i in b if 1055<=i['offset']<=1067]
        self.assertTrue(any(i['opcode']=='0xe' and i['operand']==0.0 for i in zero))
        increment=[i for i in b if 1070<=i['offset']<=1094]
        self.assertTrue(any(i['opcode']=='0x63' for i in increment))
        self.assertTrue(any(i['operand']==400.0 for i in b))

    def test_hornet_uuid_contains_and_living_actor_parent(self):
        b=self.body('HornetProjectileOnEntityTickUpdateProcedure')
        self.assertEqual(sum('java/lang/String.contains(' in str(i['operand']) for i in b),2)
        self.assertFalse(any('.isAlliedTo(' in str(i['operand']) for i in b))
        for a in ('HornetProjectileEntity','NemesisProjectileEntity'):
            w=next(w for w in self.native['witnesses'] if w['entry'].endswith('/'+a+'.class'))
            self.assertEqual(w['superclass'],'net/minecraft/world/entity/TamableAnimal')
            b=self.body(a,'getDefaultDimensions')
            self.assertFalse(any('DATA_scale_switch' in str(i['operand']) for i in b))
            self.assertTrue(any(i['operand']==0.800000011920929 for i in b))

    def test_moth_incoming_summon_precedes_native_exclusions(self):
        b=self.body('SpiderMothSummonEntity','hurt')
        helper=next(i['offset'] for i in b if 'SpiderMothSummonEntityIsHurtProcedure.execute' in str(i['operand']))
        first_type=next(i['offset'] for i in b if 'DamageTypes.' in str(i['operand']))
        self.assertLess(helper,first_type)
        b=self.body('SpiderMothSummonEntityIsHurtProcedure')
        self.assertEqual(sum('EntityType.spawn(' in str(i['operand']) for i in b),1)
        self.assertTrue(any(i['operand']==40 for i in b))

    def test_moth_same_callback_noai_restore_and_stuck_factor(self):
        b=self.body('SpiderMothSummonOnEntityTickUpdateProcedure')
        self.assertEqual([i['operand'] for i in b if isinstance(i['operand'],str) and i['operand'].startswith('data modify entity @s NoAI')],
                         ['data modify entity @s NoAI set value 0b','data modify entity @s NoAI set value 1b','data modify entity @s NoAI set value 0b'])
        self.assertEqual([i['operand'] for i in b if 2449<=i['offset']<=2455],[2.0,3.0,2.0])

    def test_larva_native_parent_and_blood_factory_no_payload_duplicate(self):
        b=self.body('SpiderMothSummonLarvaeEntity','registerGoals')
        self.assertTrue(any('Spider.registerGoals(' in str(i['operand']) for i in b))
        b=self.body('SpiderMothSummonLarvaeEntity','performRangedAttack')
        self.assertEqual(sum('BloodProjectileEntity.shoot(' in str(i['operand']) for i in b),1)
        r=self.row('moth_summon_larva_native_target_copy_contact_and_ranged')
        self.assertIn('arphex:blood_arrow_intrinsic_combat',r['canonical_contract_reuse'])
        self.assertEqual([c['primitive'] for c in r['scalable_parameter_candidates']],['NATIVE_CONDITIONAL_MELEE','DELAYED_LIFECYCLE'])

    def test_tormentor_active_writes_preserve_native_order(self):
        b=self.body('TormentorSummonTickProcedure');vals=[]
        for j,i in enumerate(b):
            if 'PlayerVariables.tormentor_summon_activeD' in str(i['operand']) and i['opcode']=='0xb5':vals.append(b[j-1]['operand'])
        self.assertEqual(vals,[160.0,150.0])
        r=self.row('tormentor_summon_native_owner_levels_status_motion_and_transport')
        self.assertFalse(any('active' in p or p=='attack' for c in r['scalable_parameter_candidates'] for p in c['parameters']))
        self.assertIn('arphex:tormentor_summon_incoming_attack_replacement',r['canonical_contract_reuse'])

    def test_tormentor_owner_homing_preserves_signed_z(self):
        b=self.body('TormentorSummonTickProcedure');sqrt_at=next(j for j,i in enumerate(b) if 'Math.sqrt(' in str(i['operand']))
        span=b[sqrt_at-30:sqrt_at]
        self.assertEqual(sum('Math.pow(' in str(i['operand']) for i in span),1)
        self.assertTrue(any(i['opcode']=='0x6b' for i in span))
        self.assertEqual(span[-1]['opcode'],'0x63')

    def test_custom_segment_source_exact_literal_key_chain(self):
        from promote_combat_batch import damage_source_binding
        b=self.body('SpiderMothSummonOnInitialEntitySpawnProcedure','lambda$execute$0')
        source=damage_source_binding(dict(instructions=b),90)
        self.assertEqual(source,('RESOURCE_LOCATION:arphex:segment',43,86,
             'net/minecraft/world/damagesource/DamageSource.<init>(Lnet/minecraft/core/Holder;Lnet/minecraft/world/entity/Entity;)V'))
        mutated=copy.deepcopy(b);next(i for i in mutated if i['offset']==56)['operand']='unrelated.create()V'
        with self.assertRaises(AssertionError):damage_source_binding(dict(instructions=mutated),90)
        changed=copy.deepcopy(self.batch)
        r=next(r for r in changed['effects'] if 'tormentor_summon_native_owner_' in r['id'])
        c=next(c for c in r['scalable_parameter_candidates'] if c['primitive']=='NATIVE_DAMAGE_REQUEST')
        c['native_damage_type_symbol']='RESOURCE_LOCATION:arphex:unrelated'
        with self.assertRaises(AssertionError):validate_batch(changed,self.prior(),self.census)

    def test_tormentor_moth_stuck_receivers_are_distinct(self):
        b=self.body('TormentorMothSummonOnEntityTickUpdateProcedure')
        by={i['offset']:i for i in b}
        self.assertEqual((by[358]['local_index'],by[393]['local_index']),(7,13))
        self.assertEqual((by[358]['opcode'],by[393]['opcode']),('0x19','0x19'))
        self.assertEqual(sum('.hurt(' in str(i['operand']) for i in b),2)
        self.assertFalse(any('.isAlliedTo(' in str(i['operand']) for i in b))

    def test_tormentor_moth_incoming_uses_causing_source_before_filters(self):
        b=self.body('TormentorMothSummonEntity','hurt')
        causes=next(i['offset'] for i in b if 'DamageSource.getEntity(' in str(i['operand']))
        helper=next(i['offset'] for i in b if 'TormentorVoidlasherSummonEntityIsHurtProcedure.execute' in str(i['operand']))
        direct=next(i['offset'] for i in b if 'DamageSource.getDirectEntity(' in str(i['operand']))
        self.assertLess(causes,helper);self.assertLess(helper,direct)
        self.assertFalse(any('MeleeAttackGoal' in str(i['operand']) for i in self.body('TormentorMothSummonEntity','registerGoals')))


class NativeTamedPetTests(NativeContractHarness, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch=read_json(OUT/'arphex-r2m5p-native-tamed-pet-contracts.json')
        cls.native=read_json(OUT/'native-evidence/arphex-native-tamed-pet-families.json')
        cls.census=read_json(OUT/'arphex-combat-census.json')

    def legacy_body(self,name):
        p=read_json(OUT/'native-evidence/arphex-transfer-readers.json')
        return next(m['instructions'] for w in p['witnesses'] if w['entry'].endswith('/'+name+'.class')
                    for m in w['methods'] if m['name']=='execute')

    def test_native_consumers_and_six_roots(self):
        validate_batch(self.batch,self.prior(),self.census)
        self.assertEqual((len(self.batch['effects']),len(self.batch['closed_actor_callback_entries'])),(5,6))
        self.assertEqual(sum(len(c['parameters']) for r in self.batch['effects']
                             for c in r['scalable_parameter_candidates']),102)
        self.assertEqual((len(self.native['witnesses']),sum(len(w['methods']) for w in self.native['witnesses'])),(71,358))
        self.assertEqual([r['id'] for r in self.batch['record_refinements']],['arphex:arthropleura_segment_damage_transfer'])
        self.assertFalse(any(r.get('candidate_additions') for r in self.batch['record_refinements']))

    def test_food_predicates_and_duplicate_heal_not_invented(self):
        for a in ('TamedTarantulaEntity','CrabLarvaeEntity','SegmentedBodyEntity'):
            b=self.body(a,'isFood')
            self.assertTrue(any(i['operand']=='java/util/List.of()Ljava/util/List;' for i in b))
            self.assertFalse(any('ArphexModItems.' in str(i['operand']) for i in b))
        for a in ('MantisMutilatorEntity','SpiderLungerEntity','ArthropleuraAbominationEntity'):
            self.assertTrue(any('ArphexModItems.' in str(i['operand']) for i in self.body(a,'isFood')))
            b=self.body(a,'mobInteract');by={i['offset']:i for i in b}
            self.assertEqual([i['offset'] for i in b if '.heal(' in str(i['operand'])],[168,217])
            self.assertEqual((by[119]['branch_target'],by[131]['branch_target']),(186,186))
            self.assertEqual(by[116]['operand'],by[188]['operand'])
            self.assertEqual(by[123]['operand'],by[195]['operand'])
        cs=[c for r in self.batch['effects'] for c in r['scalable_parameter_candidates'] if c['primitive']=='NATIVE_FOOD_HEAL']
        self.assertEqual(len(cs),3);self.assertTrue(all(c['native_consumer']['offset']==168 for c in cs))

    def test_mantis_head_fixed_strafe_lunger_tarantula_player_strafe(self):
        for a in ('MantisMutilatorEntity','ArthropleuraAbominationEntity'):
            self.assertFalse(any('.xxaF' in str(i['operand']) for i in self.body(a,'travel')))
        for a in ('TamedTarantulaEntity','SpiderLungerEntity'):
            self.assertTrue(any('.xxaF' in str(i['operand']) for i in self.body(a,'travel')))

    def test_tarantula_rider_status_has_no_owner_gate(self):
        b=self.body('TamedTarantulaTickProcedure')
        self.assertFalse(any(x in str(i['operand']) for i in b for x in ('.isOwnedBy(','.stopRiding(')))
        self.assertTrue(any('getFirstPassenger(' in str(i['operand']) for i in b))
        self.assertEqual(sum('.addEffect(' in str(i['operand']) for i in b),11)
        self.assertFalse(any('DATA_variant' in str(i['operand']) for i in self.body('TamedTarantulaOnInitialEntitySpawnProcedure')))

    def test_mantis_noai_commands_restore_same_callback(self):
        b=self.body('MantisMutilatorOnEntityTickUpdateProcedure')
        c=[i['operand'] for i in b if isinstance(i['operand'],str) and i['operand'].startswith('data modify entity @s NoAI')]
        self.assertEqual(c,['data modify entity @s NoAI set value 0b','data modify entity @s NoAI set value 1b','data modify entity @s NoAI set value 0b'])
        self.assertTrue(any(i['operand']==57.5 for i in b))
        self.assertFalse(any('wrapDegrees(' in str(i['operand']) for i in b))

    def test_native_clock_distribution_bound_to_accessor(self):
        from promote_combat_batch import synched_int_distribution_binding
        m=dict(instructions=self.body('MantisMutilatorOnEntityTickUpdateProcedure'))
        binding=synched_int_distribution_binding(m,3568)
        self.assertEqual((binding['native_minimum'],binding['native_maximum']),(2400,3600))
        self.assertIn('DATA_timeloop',binding['accessor_symbol'])
        with self.assertRaises(AssertionError):synched_int_distribution_binding(m,3562)
        changed=copy.deepcopy(self.batch)
        r=next(r for r in changed['effects'] if 'mantis_native_' in r['id'])
        next(c for c in r['components'] if c['primitive']=='NATIVE_CLOCK_DISTRIBUTION')['numerical_parameters']['minimum']=2401
        with self.assertRaises(AssertionError):validate_batch(changed,self.prior(),self.census)

    def test_crab_growth_overwrite_precedes_inactive_weakness(self):
        from promote_combat_batch import literal_synched_int_binding
        b=self.body('CrabLarvaeOnEntityTickUpdateProcedure')
        binding=literal_synched_int_binding(dict(instructions=b),1921)
        self.assertEqual(binding['native_value'],96002)
        self.assertIn('DATA_crab_growth',binding['accessor_symbol'])
        for o in (2465,2613,2761):self.assertLess(1921,o)
        r=self.row('crab_larva_native_constricted_ray_owner_and_forced_maturity')
        self.assertFalse(any('WEAKNESS' in c['primitive'] for c in r['scalable_parameter_candidates']))
        self.assertTrue(any(i['operand']==1.74 for i in self.body('CrabLarvaeHitboxProcedure')))

    def test_ray_three_native_queries_share_proven_literal(self):
        from promote_combat_batch import literal_vector_scale_binding
        b=self.body('CrabLarvaeOnEntityTickUpdateProcedure');m=dict(instructions=b)
        sites=[i['offset'] for i in b if 'Vec3.scale(' in str(i['operand'])]
        self.assertEqual(len(sites),3)
        self.assertEqual([literal_vector_scale_binding(m,o)['native_value'] for o in sites],[5.5]*3)
        with self.assertRaises(AssertionError):literal_vector_scale_binding(m,1456)
        changed=copy.deepcopy(self.batch)
        r=next(r for r in changed['effects'] if 'crab_larva_native_' in r['id'])
        next(c for c in r['components'] if c['primitive']=='NATIVE_RAY_DELIVERY')['numerical_parameters']['range']=6.
        with self.assertRaises(AssertionError):validate_batch(changed,self.prior(),self.census)

    def test_lunger_clock_updates_and_rejected_hurt_sideeffect(self):
        b=self.body('SpiderLungerEntity','hurt')
        self.assertLess(next(i['offset'] for i in b if 'EntityIsHurtProcedure.execute(' in str(i['operand'])),
                        next(i['offset'] for i in b if '.getDirectEntity(' in str(i['operand'])))
        from promote_combat_batch import literal_synched_int_binding
        m=dict(instructions=self.body('SpiderLungerOnEntityTickUpdateProcedure'))
        self.assertEqual([literal_synched_int_binding(m,o)['native_value'] for o in (458,1060,1521,1741)],[100,1200,1200,0])
        self.assertLess(1060,1741)

    def test_segment_owner_native_local_indices_not_decompiler_variable(self):
        b=self.legacy_body('SegmentedBodyOnEntityTickUpdateProcedure');by={i['offset']:i for i in b}
        self.assertEqual((by[1136]['local_index'],by[1151]['local_index']),(7,28))
        self.assertEqual((by[1192]['local_index'],by[1194]['local_index']),(35,37))
        self.assertEqual((by[2758]['local_index'],by[2773]['local_index']),(7,28))
        self.assertIn('.tame(',by[2818]['operand'])
        r=self.row('arthropleura_native_head_body_generation_owner_and_control')
        self.assertIn('arphex:arthropleura_segment_damage_transfer',r['canonical_contract_reuse'])

    def test_segment_init_uuid_copy_precedes_lineage_comparison(self):
        b=self.body('SegmentedBodyOnInitialEntitySpawnProcedure')
        eq=next(i['offset'] for i in b if '.equals(' in str(i['operand']))
        write=next(i['offset'] for i in b if 'SynchedEntityData.set(' in str(i['operand']) and i['offset']>100)
        self.assertLess(write,eq)
        self.assertTrue(any(i['operand']==2. for i in b))

    def test_protected_transfer_candidates_not_duplicated(self):
        r=self.row('arthropleura_native_head_body_generation_owner_and_control')
        self.assertFalse(any(c['primitive'] in ('NATIVE_DAMAGE_TRANSFER','NATIVE_DAMAGE_NOTIFICATION','NATIVE_IMMUNITY_STATE')
                             for c in r['scalable_parameter_candidates']))
        b=self.legacy_body('SegmentedBodyOnEntityTickUpdateProcedure')
        self.assertTrue(any(i['operand']==15. for i in b))
        self.assertFalse(any(x in str(i['operand']) for i in b for x in ('Math.max(', 'Vec3.normalize(')))


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
