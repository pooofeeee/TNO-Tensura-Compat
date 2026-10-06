"""Assert native event reachability and scalar facts independently of prose."""
import unittest
from catalog_common import OUT,read_json
from collect_combat_census import decode_sites
from promote_combat_batch import validate_batch


class GlobalHooksTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.census=read_json(OUT/'arphex-combat-census.json')
        cls.native=read_json(OUT/'native-evidence/arphex-global-hooks.json')
        cls.batch=read_json(OUT/'arphex-r2m2c-small-global-deliveries.json')

    def witness(self,name):
        return next(w for w in self.native['witnesses'] if w['entry']==f'net/arphex/procedures/{name}.class')

    def test_small_batch_native_consumers_and_unique_identities(self):
        review=read_json(OUT/'mod-reviews/arphex.json');ids={r['id'] for r in self.batch['effects']}
        review['effects']=[r for r in review['effects'] if r['id'] not in ids]
        review['paths']=[p for p in review['paths'] if not set(p['effect_ids'])&ids]
        self.assertEqual(validate_batch(self.batch,review,self.census)['semantic_records'],
                         len(review['effects'])+len(self.batch['effects']))
        self.assertEqual(len(ids),9)

    def test_method_annotation_without_class_or_caller_is_not_live_registration(self):
        w=self.witness('EntitySpawnReasonProcedure')
        self.assertFalse(any(a['descriptor'].endswith('/EventBusSubscriber;') for a in w['annotations']))
        self.assertTrue(any(a['descriptor'].endswith('/SubscribeEvent;') for m in w['methods'] for a in m['annotations']))
        target='net/arphex/procedures/EntitySpawnReasonProcedure.'
        external=[(m,s) for m in self.census['methods'] if not m['entry'].startswith(w['entry'][:-6])
                  for s in decode_sites(self.census,m,'calls') if target in s['operand']]
        self.assertEqual(external,[])
        self.assertFalse(any(target in str(b['arguments']) and b['entry']!=w['entry']
                             for b in self.census['registration_bootstraps']))
        registrations=[(m['entry'],m['method'],s['offset']) for m in self.census['methods']
                       for s in decode_sites(self.census,m,'calls')
                       if '/IEventBus.register(Ljava/lang/Object;)V' in s['operand']]
        self.assertEqual(registrations,[('net/arphex/ArphexMod.class','<init>',8)])
        root=next(w for w in read_json(OUT/'native-evidence/arphex-status-core.json')['witnesses'] if w['entry']=='net/arphex/ArphexMod.class')
        ctor=next(m for m in root['methods'] if m['name']=='<init>')
        before=next(i for i in ctor['instructions'] if i['offset']==7)
        self.assertEqual(before['opcode'],'0x2a') # register(this), not a procedure class
        tick=next(m for m in self.census['methods'] if m['entry']==root['entry'] and m['method']=='tick')
        self.assertFalse(tick['access']&0x8) # instance handler matches register(this)

    def test_mob_disable_list_preserves_literal_native_defaults(self):
        config=next(w for w in self.native['witnesses'] if w['entry'].endswith('/ConfigurationSettingsConfiguration.class'))
        body=config['methods'][0]['instructions']
        at=next(n for n,i in enumerate(body) if 'List.of(Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;)' in str(i['operand']))
        defaults=[i['operand'] for i in body[at-3:at]]
        self.assertEqual(defaults,['mob_id','mob_id','mob_id (add as many as needed, e.g. spider_snatcher)'])
        row=next(r for r in self.batch['effects'] if r['id']=='arphex:global_entity_join_admission')
        self.assertEqual(row['binary_parameters']['disable_specific_mobs_default'],defaults)

    def test_global_resistance_is_under_living_gate_not_species_gate(self):
        body=next(m['instructions'] for m in self.witness('BloodWormOnInitialEntitySpawnProcedure')['methods']
                  if m['name']=='execute' and any(i['offset']==533 for i in m['instructions']))
        at=next(n for n,i in enumerate(body) if i['offset']==533)
        self.assertEqual([i['operand'] for i in body[at-4:at]],[40,0,0,0])
        types=[i['operand'] for i in body[:at] if i['opcode']=='0xc1']
        self.assertEqual(types[-1],'net/minecraft/world/entity/LivingEntity')
        self.assertIn('DAMAGE_RESISTANCE',body[at-5]['operand'])

    def test_motion_cleanup_uses_component_sum_not_magnitude(self):
        body=next(m['instructions'] for m in self.witness('EntityJoinsWorldProcedure')['methods']
                  if m['name']=='execute' and any('Math.abs(D)' in str(i['operand']) for i in m['instructions']))
        at=next(n for n,i in enumerate(body) if 'Math.abs(D)' in str(i['operand']))
        self.assertEqual(sum(i['opcode']=='0x63' for i in body[max(0,at-20):at]),2)
        self.assertEqual(body[at+1]['operand'],0.001)
        self.assertEqual(abs(1+(-1)+0),0)
        self.assertNotEqual((1**2+(-1)**2+0**2)**0.5,0)

    def test_zero_sleep_hurt_and_native_map_coordinate_typo_are_preserved(self):
        w=self.witness('PlayerSleepsProcedure')
        body=next(m['instructions'] for m in w['methods'] if m['name']=='lambda$execute$0')
        at=next(n for n,i in enumerate(body) if '.hurt(' in str(i['operand']))
        self.assertEqual(body[at-1]['operand'],0.0)
        self.assertEqual(body[at+1]['opcode'],'0x57')
        main=next(m['instructions'] for m in w['methods'] if m['name']=='execute' and any('tormentor_healthD' in str(i['operand']) for i in m['instructions']))
        self.assertEqual(sum('tormentor_yD' in str(i['operand']) for i in main),4)
        self.assertEqual(sum('tormentor_zD' in str(i['operand']) for i in main),0)

    def test_visual_scale_name_does_not_exclude_physical_dimensions(self):
        reader=next(m for m in self.census['methods'] if m['entry']=='net/arphex/entity/ScorpioidBloodlusterEntity.class' and m['method']=='getDefaultDimensions')
        self.assertTrue(any('ScorpioidBloodlusterEntityVisualScaleProcedure.execute(' in s['operand'] for s in decode_sites(self.census,reader,'calls')))
        excluded={r['entry'] for r in self.batch['exclusions']}
        self.assertNotIn('net/arphex/procedures/ScorpioidBloodlusterEntityVisualScaleProcedure.class',excluded)

    def body(self,procedure,name='execute'):
        return max((m['instructions'] for m in self.witness(procedure)['methods'] if m['name']==name),key=len)

    def test_shared_batch_validates_consumers_without_duplicate_records(self):
        batch=read_json(OUT/'arphex-r2m2k-small-shared-global-roots.json')
        review=read_json(OUT/'mod-reviews/arphex.json');ids={r['id'] for r in batch['effects']}
        review['effects']=[r for r in review['effects'] if r['id'] not in ids]
        review['paths']=[p for p in review['paths'] if not set(p['effect_ids'])&ids]
        result=validate_batch(batch,review,self.census)
        self.assertEqual(result['semantic_records'],len(review['effects'])+3)
        self.assertEqual(sum(len(c['parameters']) for r in batch['effects'] for c in r['scalable_parameter_candidates']),9)

    def test_climb_delivery_uses_captured_position_and_current_yaw_without_rechecks(self):
        main=self.body('ClimbingProcedure');by_offset={i['offset']:i for i in main}
        self.assertEqual([by_offset[n]['operand'] for n in (542,725,754)],[13,13,10])
        capture=next(i for i in main if i['offset']==507)
        self.assertIn('LevelAccessor;DDDLnet/minecraft/world/entity/Entity;',capture['operand'])
        status=self.body('ClimbingProcedure','lambda$execute$0')
        at=next(n for n,i in enumerate(status) if i['offset']==360)
        self.assertEqual([i['operand'] for i in status[at-4:at]],[50,1,0,0])
        self.assertIn('SLOW_FALLING',status[at-5]['operand'])
        self.assertTrue(any(i['operand']=='climbradius' for i in status))
        self.assertFalse(any(any(s in str(i['operand']) for s in ('isVehicle','isInWater','isAlive','getTarget','arphexclimber')) for i in status))
        for name in ('lambda$execute$1','lambda$execute$2'):
            motion=self.body('ClimbingProcedure',name)
            self.assertEqual(sum('getYRot()' in str(i['operand']) for i in motion),2)
            self.assertEqual([i['operand'] for i in motion if isinstance(i['operand'],float) and i['operand'] in (.0299,.15)],[.0299,.15,.0299])
            self.assertFalse(any('branch_target' in i for i in motion))
            self.assertEqual(motion[-2]['offset'],49)
            self.assertIn('.setDeltaMovement(',motion[-2]['operand'])

    def test_world_countdown_reset_is_exact_floor_gate_without_spawn(self):
        body=self.body('WorldTickProcedure');at=next(n for n,i in enumerate(body) if i['offset']==984)
        self.assertEqual([body[n]['operand'] for n in (at-2,at,at+1)],[6.0,'java/lang/Math.floor(D)D',1.0])
        self.assertEqual(body[at-1]['opcode'],'0x6f')
        self.assertEqual(body[at+3]['branch_target'],1094)
        hp=next(n for n,i in enumerate(body) if i['offset']==1083)
        self.assertEqual(body[hp-1]['operand'],1024.0)
        self.assertIn('tormentor_healthD',body[hp]['operand'])
        self.assertFalse(any(any(s in str(i['operand']) for s in ('EntityType.spawn','addFreshEntity','queueServerWork','.hurt(','.addEffect(')) for i in body))
        row=next(r for r in read_json(OUT/'arphex-r2m2k-small-shared-global-roots.json')['effects'] if r['id']=='arphex:shared_native_world_state_tick')
        self.assertEqual(row['scalable_parameter_candidates'],[])

    def test_overlay_is_native_darkness_and_chat_replies_are_message_commands(self):
        main=self.body('GameModeDetectorProcedure');at=next(n for n,i in enumerate(main) if i['offset']==1950)
        self.assertEqual([i['operand'] for i in main[at-4:at]],[3,0,0,0])
        self.assertIn('DARKNESS',main[at-5]['operand'])
        gate=next(i for i in main if i['offset']==1908);self.assertEqual(gate['branch_target'],1969)
        self.assertEqual(next(i for i in main if i['offset']==1957)['operand'],8)
        clear=self.body('GameModeDetectorProcedure','lambda$execute$14')
        self.assertFalse(any('branch_target' in i for i in clear))
        self.assertEqual(next(i for i in clear if i['offset']==12)['operand'],0)
        self.assertIn('show_tormentor_overlayZ',next(i for i in clear if i['offset']==13)['operand'])
        chat=self.witness('PlayerChatTormentorProcedure')
        recipes={b['index']:b['arguments'][0] for b in self.census['registration_bootstraps']
                 if b['entry']==chat['entry'] and 'StringConcatFactory' in b['handle']}
        for method in chat['methods']:
            if not method['name'].startswith('lambda$execute$'):continue
            ins=method['instructions'];command=next(n for n,i in enumerate(ins) if '.performPrefixedCommand(' in str(i['operand']))
            argument=ins[command-1]['operand']
            if ins[command-1]['opcode']=='0xba':
                argument=recipes[int(argument.split(':')[0].split('#')[1])]
            self.assertTrue(argument.startswith('/tellraw @a '),method['name'])
            self.assertFalse(any(any(s in str(i['operand']) for s in ('.hurt(','.heal(','.addEffect(','.setDeltaMovement(')) for i in ins))
        self.assertTrue(any('show_tormentor_overlayZ' in str(i['operand']) and i['opcode']=='0xb5' for i in self.body('PlayerChatTormentorProcedure')))

    def test_spider_moth_scale_external_consumer_is_renderer_only_and_reproduces(self):
        getter='net/arphex/procedures/SpiderMothDwellerEntityVisualScaleProcedure'
        callers={m['entry'] for m in self.census['methods'] for s in decode_sites(self.census,m,'calls') if getter+'.execute(' in s['operand'] and m['entry']!=getter+'.class'}
        self.assertEqual(callers,{'net/arphex/client/renderer/SpiderMothRenderer.class'})
        native=read_json(OUT/'native-evidence/arphex-shared-reader-contexts.json')
        body=native['witnesses'][0]['methods'][0]['instructions']
        self.assertEqual([i['operand'].split('.')[1] for i in body if i['opcode']=='0xb5'],['scaleHeightF','scaleWidthF'])
        from native_evidence import collect
        from pathlib import Path
        jar=Path('/workspace/.cache/large-mod-campaign/ArPhEx-5.0.2-neoforge-1.21.1.jar')
        if jar.exists():self.assertEqual(collect(read_json(OUT/'native-specifications/arphex-shared-reader-contexts.json'),{'arphex':jar}),native)

    def target_tick_batch(self):
        batch=read_json(OUT/'arphex-r2m2l-target-and-entity-tick-roots.json')
        review=read_json(OUT/'mod-reviews/arphex.json');ids={r['id'] for r in batch['effects']}
        review['effects']=[r for r in review['effects'] if r['id'] not in ids]
        review['paths']=[p for p in review['paths'] if not set(p['effect_ids'])&ids]
        return batch,review

    def test_target_tick_candidates_and_literal_commands_fail_closed_when_detached(self):
        from copy import deepcopy
        batch,review=self.target_tick_batch()
        result=validate_batch(batch,review,self.census)
        self.assertEqual(result['semantic_records'],len(review['effects'])+20)
        ids={r['id'] for r in review['effects']+batch['effects']}
        self.assertTrue(all(s in ids for r in batch['effects'] for s in r.get('canonical_contract_reuse',[])))
        wrong=deepcopy(batch)
        c=next(c for r in wrong['effects'] for c in r['scalable_parameter_candidates'] if 'native_command_binding' in c)
        c['native_command_binding']['command']='effect give @a minecraft:wither 20 20'
        with self.assertRaises(AssertionError):validate_batch(wrong,review,self.census)
        wrong=deepcopy(batch)
        wrong['record_refinements'][0]['candidate_additions'][0]['native_holder_symbol']='net/minecraft/world/effect/MobEffects.DAMAGE_BOOSTLnet/minecraft/core/Holder;'
        with self.assertRaises(AssertionError):validate_batch(wrong,review,self.census)

    def test_target_event_reads_original_target_and_larvae_decrements_wrong_entity(self):
        wrapper=self.body('DwellerTargetProcedure','onEntitySetsAttackTarget')
        self.assertIn('getOriginalAboutToBeSetTarget()',next(i for i in wrapper if i['offset']==30)['operand'])
        self.assertIn('getEntity()',next(i for i in wrapper if i['offset']==34)['operand'])
        body=self.body('DwellerTargetProcedure');by={i['offset']:i for i in body}
        self.assertEqual(by[5005]['opcode'],'0x57') # hurt return discarded before source reset
        self.assertEqual(by[5006]['local_index'],9)
        self.assertEqual(by[5014]['operand'],10.0)
        self.assertEqual(by[5023]['local_index'],8) # destination is original target
        self.assertEqual(by[5031]['local_index'],9) # decrement reads actor
        self.assertEqual(by[5043]['opcode'],'0x67')
        self.assertIn('.putDouble(',by[5044]['operand'])

    def test_moth_target_side_state_and_commands_have_independent_recipient_selection(self):
        body=self.body('DwellerTargetProcedure')
        for key in ('flyvers','chasemode','growattack'):
            sites=[n for n,i in enumerate(body) if i['operand']==key]
            self.assertTrue(sites)
            if key=='growattack':sites=sites[:1] # later source growattack is a distinct branch
            for n in sites:
                self.assertEqual(body[n-2].get('local_index'),8)
        from promote_combat_batch import literal_command_binding
        method=max((m for m in self.witness('DwellerTargetProcedure')['methods'] if m['name']=='execute'),key=lambda m:len(m['instructions']))
        self.assertEqual(literal_command_binding(method,1519)['command'],'effect give @p[distance=..3] minecraft:nausea 4 3')
        clear=literal_command_binding(method,693)['command']
        self.assertIn('limit=1,distance=..7',clear);self.assertNotIn('sort=nearest',clear)

    def test_configured_weakness_uses_other_config_and_resistance_profiles_differ(self):
        body=self.body('EntitiesTickProcedure')
        self.assertTrue(any('OVERALL_DIFFICULTY_LOWER' in str(i['operand']) for i in body if 500<=i['offset']<545))
        self.assertTrue(any('OVERALL_DIFFICULTYL' in str(i['operand']) for i in body if 545<=i['offset']<577))
        self.assertFalse(any('OVERALL_DIFFICULTY_LOWER' in str(i['operand']) for i in body if 545<=i['offset']<577))
        rounded=[i for i in body if 627<=i['offset']<661]
        truncated=[i for i in body if 4123<=i['offset']<4156]
        self.assertTrue(any('Math.round(D)' in str(i['operand']) for i in rounded))
        self.assertFalse(any('Math.round(' in str(i['operand']) for i in truncated))
        self.assertTrue(any(i['opcode']=='0x8e' for i in truncated)) # d2i

    def test_void_spear_damage_has_integer_armor_and_no_native_owner(self):
        body=self.body('EntitiesTickProcedure','lambda$execute$25');at=next(n for n,i in enumerate(body) if i['offset']==1371)
        before=body[at-45:at]
        self.assertIn('0x6c',[i['opcode'] for i in before])
        self.assertTrue(any('DamageTypes.FELL_OUT_OF_WORLD' in str(i['operand']) for i in before))
        self.assertTrue(any('DamageSource.<init>(Lnet/minecraft/core/Holder;)V' in str(i['operand']) for i in before))
        self.assertEqual(body[at+1]['opcode'],'0x57')
        self.assertTrue(any('.discard()' in str(i['operand']) for i in body[at+2:]))
        self.assertFalse(any('getOwner' in str(i['operand']) or 'setOwner' in str(i['operand']) for i in body))

    def test_burn_uses_larger_integer_branch_and_not_clamped_percent_damage(self):
        body=self.body('EntitiesTickProcedure');by={i['offset']:i for i in body}
        self.assertEqual(by[3835]['operand'],400)
        self.assertEqual([by[n]['opcode'] for n in (3865,3866)],['0x6c','0x6c'])
        start=next(n for n,i in enumerate(body) if i['offset']==3835)
        first=next(n for n,i in enumerate(body) if i['offset']==3957)
        comparisons=[i for i in body[start:first] if i['opcode'] in ('0x95','0x96')]
        self.assertTrue(comparisons)
        gate=next(i for i in body if i['offset']==comparisons[0]['offset']+1)
        self.assertEqual(gate['opcode'],'0x9e') # <= jumps past armor-branch hurt to max-health request
        self.assertGreater(gate['branch_target'],3957)
        self.assertLess(gate['branch_target'],4016)
        self.assertEqual(by[4028]['operand'],10.0)
        self.assertEqual(by[3751]['operand'],1.0)

    def test_follow_local_flag_unused_and_only_reachable_status_sites_counted(self):
        body=self.body('EntitiesTickProcedure')
        stores=[i for i in body if i['opcode']=='0x36' and i.get('local_index')==16]
        loads=[i for i in body if i['opcode']=='0x15' and i.get('local_index')==16]
        self.assertTrue(stores);self.assertEqual(loads,[])
        batch,_=self.target_tick_batch();row=next(r for r in batch['effects'] if r['id']=='arphex:forced_owner_tick_follow')
        sites={c['native_consumer']['offset'] for c in row['scalable_parameter_candidates']}
        sites.update(s['offset'] for c in row['scalable_parameter_candidates'] for s in c.get('additional_consumer_sites',[]))
        self.assertTrue({5456,5695}<=sites);self.assertFalse({5378,5617}&sites)
        flag_writes=[i['offset'] for i in body if i['operand']=='donespawn']
        self.assertTrue(flag_writes)
        first_spawn=next(i['offset'] for i in body if 'EntityType.spawn(' in str(i['operand']))
        self.assertLess(flag_writes[0],first_spawn)

    def test_instant_marker_command_passes_duration_in_ticks_and_direct_instance_retains_window(self):
        doc=read_json(OUT/'vanilla-evidence/arphex-instant-marker-command.json')
        instant=next(c for c in doc['classes'] if c['class_name'].endswith('/InstantenousMobEffect'))
        self.assertEqual(next(m for m in instant['methods'] if m['name']=='isInstantenous')['code_hex'],'04ac')
        give=next(c for c in doc['classes'] if c['class_name'].endswith('/EffectCommands'))['methods'][0]
        code=bytes.fromhex(give['code_hex'])
        self.assertEqual(23+int.from_bytes(code[24:26],'big',signed=True),35)
        self.assertEqual(32+int.from_bytes(code[33:35],'big',signed=True),80)
        self.assertFalse(any(i['opcode']=='0x68' for i in give['instructions'] if 26<=i['offset']<=32))
        self.assertEqual(next(i for i in give['instructions'] if i['offset']==53)['operand'],20)
        base=read_json(OUT/'vanilla-evidence/twilight-ominous-progression.json')
        apply=next(m for c in base['classes'] for m in c['methods'] if c['class_name'].endswith('/MobEffect') and m['name']=='applyEffectTick')
        self.assertEqual(apply['code_hex'],'04ac')
        direct=read_json(OUT/'reference-evidence/cataclysm-shared-244.json')
        method=next(m for w in direct['witnesses'] for m in w.get('methods',[]) if w['entry'].endswith('/LivingEntity.class') and m['name']=='addEffect' and 'Entity;)Z' in m['descriptor'])
        self.assertTrue(any('Map.put(' in str(i['operand']) for i in method['instructions']))
        self.assertFalse(any('isInstantenous' in str(i['operand']) for i in method['instructions']))
        from pathlib import Path
        from vanilla_reference import prepare_raw
        cache=Path('/workspace/.cache/large-mod-campaign/vanilla')
        if (cache/'client.jar').exists():self.assertEqual(prepare_raw(read_json(OUT/'vanilla-specifications/arphex-instant-marker-command.json'),cache/'client.jar',cache/'client_mappings.txt',cache/'version.json'),doc)

    def test_target_tendril_owner_two_launches_and_double_clock_decrement(self):
        body=self.body('DwellerTargetProcedure');by={i['offset']:i for i in body}
        self.assertIn('$4.getArrow(',by[5958]['operand']);self.assertIn('$5.getArrow(',by[6082]['operand'])
        self.assertEqual([by[n]['operand'] for n in (5956,5957,6080,6081)],[2,3,2,3])
        self.assertEqual([by[n]['operand'] for n in (6173,6238)],[1.0,1.0])
        for p in ('DwellerTargetProcedure$4','DwellerTargetProcedure$5'):
            native=self.body(p,'getArrow');n=next(n for n,i in enumerate(native) if '.setOwner(' in str(i['operand']))
            self.assertEqual(native[n-1]['opcode'],'0x2c') # shooter local2
            self.assertEqual(next(i for i in native if i['offset']==45)['operand'],100.0)

    def test_death_batch_merges_scarab_and_validates_exact_consumers(self):
        batch=read_json(OUT/'arphex-r2m2m-sourceful-death-and-shared-completion.json')
        review=read_json(OUT/'mod-reviews/arphex.json');ids={r['id'] for r in batch['effects']}
        review['effects']=[r for r in review['effects'] if r['id'] not in ids]
        review['paths']=[p for p in review['paths'] if not set(p['effect_ids'])&ids]
        result=validate_batch(batch,review,self.census)
        self.assertEqual(result['semantic_records'],len(review['effects'])+9)
        self.assertEqual([r['id'] for r in batch['record_refinements']],['arphex:scarab_native_family'])
        self.assertNotIn('arphex:scarab_native_family',ids)

    def test_death_requires_causing_actor_and_scarab_cancel_does_not_return(self):
        wrapper=self.body('EntityDiesProcedure','onEntityDeath')
        self.assertTrue(any('DamageSource.getEntity()' in str(i['operand']) for i in wrapper))
        self.assertFalse(any('getDirectEntity' in str(i['operand']) for i in wrapper))
        body=self.body('EntityDiesProcedure');by={i['offset']:i for i in body}
        self.assertEqual([by[n].get('local_index') for n in (0,5)],[8,9])
        self.assertEqual([by[n]['branch_target'] for n in (2,7)],[10,11])
        self.assertEqual(by[10]['opcode'],'0xb1')
        self.assertEqual([by[n]['operand'].split('.')[-1].split('(')[0] for n in (3632,3655,3674,3692)],
                         ['setCanceled','setHealth','setCanceled','discard'])
        self.assertFalse(any(i['opcode']=='0xb1' for i in body if 3632<=i['offset']<3695))
        self.assertTrue(any('TORMENTOREntity' in str(i['operand']) for i in body if i['offset']>3692))

    def test_nearest_core_short_circuits_shared_helper_and_wasp_is_not_bound_to_spawn(self):
        core=self.body('EntityDiesProcedure','lambda$execute$21');by={i['offset']:i for i in core}
        self.assertIn('CORE_OF_ETERNAL_SUFFERING',by[163]['operand'])
        self.assertEqual(by[169]['branch_target'],239)
        self.assertIn('TORMENTOREntityDiesProcedure.execute(',by[236]['operand'])
        self.assertEqual(by[239]['opcode'],'0xb1')
        wasp=self.body('EntityDiesProcedure','lambda$execute$18')
        self.assertEqual(sum('getEntitiesOfClass(' in str(i['operand']) for i in wasp),2)
        self.assertTrue(any('DATA_size' in str(i['operand']) for i in wasp))
        self.assertFalse(any('setOwner' in str(i['operand']) for i in wasp))
        main=self.body('EntityDiesProcedure');by={i['offset']:i for i in main}
        self.assertIn('LevelAccessor;DDD)',by[4629]['operand']) # queue captures world/XYZ, not spawned entity

    def test_conduit_requests_native_heal_on_causer_and_capture_statuses_stay_separate(self):
        body=self.body('EntityDiesProcedure');by={i['offset']:i for i in body}
        self.assertEqual([by[n]['operand'] for n in (6099,6100,6101,6102)],[1,0,0,0])
        from promote_combat_batch import effect_receiver_binding,effect_holder_binding
        method=max((m for m in self.witness('EntityDiesProcedure')['methods'] if m['name']=='execute'),key=lambda m:len(m['instructions']))
        self.assertEqual(effect_receiver_binding(method,6103)['origin_local_index'],9)
        self.assertIn('MobEffects.HEAL',effect_holder_binding(method,6103)[0])
        holders=[effect_holder_binding(method,n)[0].split('MobEffects.')[1].split('Lnet/')[0]
                 for n in (5266,5314,5361,5409,5457)]
        self.assertEqual(holders,['BLINDNESS','DARKNESS','CONFUSION','WEAKNESS','DIG_SLOWDOWN'])
        self.assertFalse(any('.hurt(' in str(i['operand']) for i in body))

    def test_shared_completion_intrinsic_callers_native_guard_and_evidence_reproduce(self):
        native=read_json(OUT/'native-evidence/arphex-death-reader-contexts.json')
        helper=next(w for w in native['witnesses'] if w['entry'].endswith('/TORMENTOREntityDiesProcedure.class'))
        method=next(m for m in helper['methods'] if m['name']=='execute')
        self.assertEqual(method['descriptor'],'(Lnet/minecraft/world/level/LevelAccessor;DDD)V')
        by={i['offset']:i for i in method['instructions']}
        self.assertEqual([by[n]['branch_target'] for n in (11,23)],[2081,2081])
        self.assertEqual(by[30]['operand'],2000.0)
        self.assertEqual(by[2051]['operand'],1)
        self.assertIn('setVisualOnly',by[2052]['operand'])
        for w in native['witnesses']:
            if '/entity/' not in w['entry']:continue
            body=w['methods'][0]['instructions']
            self.assertIn('Monster.die(',body[2]['operand'])
            self.assertIn('TORMENTOREntityDiesProcedure.execute(',body[-2]['operand'])
            self.assertFalse(any('branch_target' in i for i in body))
        from pathlib import Path
        from native_evidence import collect
        jar=Path('/workspace/.cache/large-mod-campaign/ArPhEx-5.0.2-neoforge-1.21.1.jar')
        if jar.exists():self.assertEqual(collect(read_json(OUT/'native-specifications/arphex-death-reader-contexts.json'),{'arphex':jar}),native)

    def test_interaction_batch_exact_consumers_and_follow_producer_merge(self):
        batch=read_json(OUT/'arphex-r2m2n-native-interactions-and-seismic-hazard.json')
        review=read_json(OUT/'mod-reviews/arphex.json');ids={r['id'] for r in batch['effects']}
        review['effects']=[r for r in review['effects'] if r['id'] not in ids]
        review['paths']=[p for p in review['paths'] if not set(p['effect_ids'])&ids]
        self.assertEqual(validate_batch(batch,review,self.census)['semantic_records'],len(review['effects'])+12)
        self.assertEqual([r['id'] for r in batch['record_refinements']],['arphex:forced_owner_tick_follow'])

    def test_interaction_event_roles_and_native_stop_use_order(self):
        left=self.body('HitBlockProcedure','onLeftClickBlock')
        self.assertTrue(any('getFace()' in str(i['operand']) for i in left))
        self.assertFalse(any('getHand()' in str(i['operand']) for i in left))
        right=self.body('RightClickEntityProcedure','onRightClickEntity')
        self.assertTrue(any('isClientSide()' in str(i['operand']) for i in right))
        self.assertLess(next(i['offset'] for i in right if 'getTarget()' in str(i['operand'])),
                        next(i['offset'] for i in right if 'getX()' in str(i['operand'])))
        body=self.body('RightClickEntityProcedure')
        self.assertLess(next(i['offset'] for i in body if 'stopUsingItem()' in str(i['operand'])),
                        next(i['offset'] for i in body if 'isUsingItem()' in str(i['operand'])))
        self.assertFalse(any('setCanceled' in str(i['operand']) for i in body))

    def test_block_impulse_is_absolute_and_chaos_clear_has_two_independent_literals(self):
        body=self.body('HitBlockProcedure');by={i['offset']:i for i in body}
        segment=[i for i in body if 2557<=i['offset']<=3180]
        self.assertEqual(sum('setDeltaMovement(' in str(i['operand']) for i in segment),4)
        self.assertEqual(sum(i['operand']==.3 for i in segment),4)
        self.assertFalse(any(any(s in str(i['operand']) for s in ('knockback(','getOwner','hurt(','normalize(')) for i in segment))
        from promote_combat_batch import literal_command_binding
        method=max((m for m in self.witness('HitBlockProcedure')['methods'] if m['name']=='execute'),key=lambda m:len(m['instructions']))
        self.assertEqual(literal_command_binding(method,3298)['command'],'effect clear @e[distance=..40] arphex:chaos_controlled')
        self.assertEqual(literal_command_binding(method,3371)['command'],'effect clear @e[distance=..40] arphex:chaos_target')
        self.assertEqual(by[2554]['operand'],5.0)

    def interaction_witness(self,name):
        return next(w for w in read_json(OUT/'native-evidence/arphex-interaction-readers.json')['witnesses']
                    if w['entry'].endswith('/'+name+'.class'))

    def test_blockwave_authored_spawns_and_nested_timing_are_not_idealized_ring(self):
        wave=self.interaction_witness('BlockwaveProcedure')
        methods=[m for m in wave['methods'] if m['name']=='execute' or m['name'].startswith('lambda')]
        counts=[sum('EntityType.spawn(' in str(i['operand']) for i in m['instructions']) for m in methods]
        self.assertEqual(counts,[1,4,8,12,16,24,36,44,48,52])
        self.assertEqual(sum(counts),245)
        intervals=[]
        for m in methods:
            b=m['instructions']
            for n,i in enumerate(b):
                if '.queueServerWork(' in str(i['operand']):intervals.append(b[n-6]['operand'])
            self.assertFalse(any(any(s in str(i['operand']) for s in ('setOwner','hurt(','destroyBlock(','setBlock(')) for i in b))
        self.assertEqual(intervals,[4,4,3,3,3,3,2,2,2])
        # Two independently emitted requests for the literal (-3,0,-2)
        # prove this stage is not an idealized unique-point perimeter.
        ring=next(m['instructions'] for m in methods if m['name']=='lambda$execute$4')
        points=[]
        for n,i in enumerate(ring):
            if 'BlockPos.containing(DDD)' not in str(i['operand']):continue
            window=ring[n-7:n]
            if [x['opcode'] for x in window]==['0x27','0x14','0x67','0x29','0x18','0x14','0x67']:
                if window[1]['operand']==3.0 and window[5]['operand']==2.0:
                    points.append(i['offset'])
        self.assertEqual(len(points),2)
        # Full native method remains the source; canonical metadata must retain
        # its explicit repeated offsets rather than deduplicating its requests.
        batch=read_json(OUT/'arphex-r2m2n-native-interactions-and-seismic-hazard.json')
        row=next(r for r in batch['effects'] if r['id']=='arphex:seismic_blockwave_native_delivery')
        stage=next(s for c in row['components'] if c['primitive']=='NATIVE_HAZARD_STENCIL'
                   for s in c['numerical_parameters']['native_stages'] if s['method']=='lambda$execute$4')
        self.assertIn({'offset':[-3.0,0.0,-2.0],'requests':2},stage['repeated_offsets'])

    def test_blocktest_damage_integer_division_independent_motion_and_zero_melee(self):
        hazard=self.interaction_witness('BlockTestOnEntityTickUpdateProcedure')
        body=next(m['instructions'] for m in hazard['methods'] if m['name']=='lambda$execute$11')
        damage=next(n for n,i in enumerate(body) if i['offset']==479)
        self.assertIn('0x6c',[i['opcode'] for i in body[damage-25:damage]])
        self.assertEqual(body[damage+1]['opcode'],'0x57')
        self.assertTrue(any('DamageSource.<init>(Lnet/minecraft/core/Holder;)V' in str(i['operand']) for i in body[:damage]))
        self.assertEqual(sum('.setDeltaMovement(' in str(i['operand']) for i in body),5)
        self.assertFalse(any('setOwner' in str(i['operand']) or 'destroyBlock(' in str(i['operand']) for i in body))
        from promote_combat_batch import literal_attribute_binding
        method=next(m for m in self.interaction_witness('BlockTestEntity')['methods'] if m['name']=='createAttributes')
        bindings=[literal_attribute_binding(method,i['offset']) for i in method['instructions']
                  if 'AttributeSupplier$Builder.add(' in str(i['operand'])]
        attack=next(b for b in bindings if '/Attributes.ATTACK_DAMAGE' in b['attribute_symbol'])
        self.assertEqual(attack['native_value'],0.0)

    def test_interaction_reader_evidence_reproduces_exact_selected_classes(self):
        from pathlib import Path
        from native_evidence import collect
        jar=Path('/workspace/.cache/large-mod-campaign/ArPhEx-5.0.2-neoforge-1.21.1.jar')
        if jar.exists():self.assertEqual(collect(read_json(OUT/'native-specifications/arphex-interaction-readers.json'),{'arphex':jar}),
                                       read_json(OUT/'native-evidence/arphex-interaction-readers.json'))

    def test_block_use_batch_exact_consumers_and_explosion_primitive_fail_closed(self):
        from copy import deepcopy
        batch=read_json(OUT/'arphex-r2m2o-block-use-altar-and-repellant.json')
        review=read_json(OUT/'mod-reviews/arphex.json');ids={r['id'] for r in batch['effects']}
        review['effects']=[r for r in review['effects'] if r['id'] not in ids]
        review['paths']=[p for p in review['paths'] if not set(p['effect_ids'])&ids]
        self.assertEqual(validate_batch(batch,review,self.census)['semantic_records'],len(review['effects'])+7)
        bad=deepcopy(batch)
        row=next(r for r in bad['effects'] if r['id']=='arphex:altar_native_explosion_delivery')
        row['scalable_parameter_candidates'][0]['primitive']='FORCED_MOVEMENT'
        with self.assertRaises(AssertionError):validate_batch(bad,review,self.census)

    def test_block_use_hand_admission_and_summon_cooldown_reads_current_mainitem(self):
        wrapper=self.body('RightClickBlockProcedure','onRightClickBlock')
        by={i['offset']:i for i in wrapper}
        self.assertIn('getHand()',by[1]['operand'])
        self.assertIn('getUsedItemHand()',by[8]['operand'])
        self.assertEqual(by[11]['branch_target'],15)
        self.assertEqual(by[14]['opcode'],'0xb1')
        delivery=self.body('RightClickBlockProcedure','lambda$execute$33')
        by={i['offset']:i for i in delivery}
        self.assertIn('getMainHandItem()',by[611]['operand'])
        self.assertIn('getItem()',by[620]['operand'])
        self.assertEqual(by[623]['operand'],200)
        self.assertIn('addCooldown(',by[626]['operand'])
        self.assertFalse(any('MOTH_SUMMONER' in str(i['operand']) for i in delivery))

    def test_altar_failed_pattern_moth_blast_and_native_anonymous_none_explosion(self):
        moth=self.body('SummonAltarProcedure','lambda$execute$10')
        scorpion=self.body('SummonAltarProcedure','lambda$execute$21')
        self.assertEqual({i['branch_target'] for i in moth if i['offset'] in (19,43,72)},{875})
        self.assertEqual({i['branch_target'] for i in scorpion if i['offset'] in (60,84,113)},{889})
        for body in (moth,scorpion):
            by={i['offset']:i for i in body}
            self.assertEqual(by[875]['operand'],1)
            self.assertIn('queueServerWork(',by[886]['operand'])
            self.assertEqual(by[889]['opcode'],'0xb1')
        for name in ('lambda$execute$9','lambda$execute$20','lambda$execute$29','lambda$execute$41','lambda$execute$50'):
            blast=self.body('SummonAltarProcedure',name);by={i['offset']:i for i in blast}
            self.assertEqual(by[23]['opcode'],'0x1') # null actor
            self.assertEqual(by[28]['operand'],6.0)
            self.assertIn('ExplosionInteraction.NONE',by[31]['operand'])
            self.assertIn('Level.explode(',by[34]['operand'])
            self.assertEqual(by[37]['opcode'],'0x57') # ignores native result
        wrong=self.body('SummonAltarProcedure','lambda$execute$29')
        self.assertTrue(any('SpiderMothDwellerEntity' in str(i['operand']) for i in wrong))
        self.assertFalse(any('DraconicVoidlasher' in str(i['operand']) for i in wrong))

    def test_repellant_rechecks_marker_and_command_has_no_source_actor(self):
        witness=self.interaction_witness('RepellantTickProcedure')
        main=next(m for m in witness['methods'] if m['name']=='execute')
        by={i['offset']:i for i in main['instructions']}
        self.assertEqual(by[32]['operand'],20)
        self.assertIn('queueServerWork(',by[41]['operand'])
        self.assertEqual([by[n]['operand'] for n in (217,219,220,221)],[20,1,0,0])
        self.assertEqual(by[286]['opcode'],'0x1')
        from promote_combat_batch import literal_command_binding
        self.assertEqual(literal_command_binding(main,295)['command'],
                         'effect give @e[type=!player,distance=..30] arphex:repulsion 1 1 false')
        delayed=next(m['instructions'] for m in witness['methods'] if m['name']=='lambda$execute$0')
        by={i['offset']:i for i in delayed}
        self.assertIn('hasEffect(',by[16]['operand'])
        self.assertEqual([by[n]['branch_target'] for n in (19,29)],[36,36])
        self.assertIn('discard()',by[33]['operand'])
        entity=self.interaction_witness('RepellantEntity')
        self.assertFalse(any(m['name']=='doHurtTarget' for m in entity['methods']))
        goals=[m for m in entity['methods'] if m['name']=='registerGoals']
        self.assertFalse(any('addGoal(' in str(i['operand']) for m in goals for i in m['instructions']))


if __name__=='__main__':unittest.main()
