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


if __name__=='__main__':unittest.main()
