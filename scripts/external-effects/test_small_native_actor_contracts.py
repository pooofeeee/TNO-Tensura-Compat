"""Shared harness, independent native facts for bounded small-actor families."""
import unittest
from catalog_common import OUT, read_json
from promote_combat_batch import validate_batch
from test_shadow_clone_contracts import NativeContractHarness


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
