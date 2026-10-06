"""Independent native/census facts for shared intrinsic projectile contracts."""
import unittest

from catalog_common import OUT,read_json
from collect_combat_census import decode_sites
from promote_combat_batch import validate_batch


class ProjectileContractsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.native=read_json(OUT/'native-evidence/arphex-arrow-shared-and-status.json')
        cls.census=read_json(OUT/'arphex-combat-census.json')
        cls.batch=read_json(OUT/'arphex-r2m3a-four-intrinsic-arrow-contracts.json')

    def method(self,name,method,descriptor=None):
        w=next(w for w in self.native['witnesses'] if w['entry'].split('/')[-1]==name+'.class')
        return next(m for m in w['methods'] if m['name']==method and (descriptor is None or m['descriptor']==descriptor))

    def test_batch_has_four_unique_payload_contracts_and_real_scalar_consumers(self):
        review=read_json(OUT/'mod-reviews/arphex.json');ids={r['id'] for r in self.batch['effects']}
        review['effects']=[r for r in review['effects'] if r['id'] not in ids]
        review['paths']=[p for p in review['paths'] if not set(p['effect_ids'])&ids]
        self.assertEqual(validate_batch(self.batch,review,self.census)['semantic_records'],len(review['effects'])+4)
        self.assertEqual(sum(len(c['parameters']) for r in self.batch['effects'] for c in r['scalable_parameter_candidates']),32)

    def test_child_hit_payloads_follow_void_parent_without_success_branch(self):
        for name in ('BloodProjectileEntity','WidowArrowEntity','WebbedArrowEntity'):
            body=self.method(name,'onHitEntity')['instructions']
            parent=next(n for n,i in enumerate(body) if 'AbstractArrow.onHitEntity(' in str(i['operand']))
            child=next(n for n,i in enumerate(body) if '/procedures/' in str(i['operand']))
            self.assertLess(parent,child)
            self.assertTrue(body[parent]['operand'].endswith(')V'))
            self.assertFalse(any(0x99<=int(i['opcode'],16)<=0xa6 for i in body[parent:child]))
        parent=next(w for w in read_json(OUT/'reference-evidence/bossesrise-knight-offense-244.json')['witnesses']
                    if w['class_name']=='net/minecraft/world/entity/projectile/AbstractArrow')
        body=next(m['instructions'] for m in parent['methods'] if m['name']=='onHitEntity')
        at=next(n for n,i in enumerate(body) if '.hurt(' in str(i['operand']))
        self.assertEqual(body[at+1]['opcode'],'0x99')
        self.assertTrue(any('DamageSources.arrow(' in str(i['operand']) for i in body))

    def test_blood_status_has_owner_regeneration_and_native_flags(self):
        body=self.method('BloodProjectileProjectileHitsLivingEntityProcedure','execute')['instructions']
        values=[]
        for n,i in enumerate(body):
            if 'MobEffectInstance.<init>' in str(i['operand']):values.append([x['operand'] for x in body[n-4:n]])
        self.assertEqual(values,[[80,1,0,1],[10,1,0,1],[60,1,1,0]])
        row=next(r for r in self.batch['effects'] if r['id']=='arphex:blood_arrow_intrinsic_combat')
        regen=next(c for c in row['scalable_parameter_candidates'] if c['primitive']=='MOB_EFFECT_REGENERATION')
        self.assertEqual(regen['native_receiver_binding']['origin_local_index'],1)
        self.assertEqual(regen['native_recipient_role'],'current_arrow_owner')
        hit=self.method('BloodProjectileEntity','onHitEntity')['instructions']
        self.assertTrue(any('.getOwner()' in str(i['operand']) for i in hit))

    def test_webbed_flying_baseline_is_owner_not_iterator(self):
        tick=self.method('WebbedArrowEntity','tick')['instructions']
        at=next(n for n,i in enumerate(tick) if 'WebbedArrowWhileProjectileFlyingTickProcedure.execute(' in str(i['operand']))
        self.assertIn('.getOwner()',tick[at-1]['operand'])
        body=self.method('WebbedArrowWhileProjectileFlyingTickProcedure','execute')['instructions'];by={i['offset']:i for i in body}
        self.assertEqual(by[151]['local_index'],11) # iterator
        self.assertEqual([by[n]['local_index'] for n in (153,168,175,183)],[7,7,7,7]) # passed owner
        self.assertEqual(by[158]['operand'],'momenthealth')
        self.assertEqual(by[173]['operand'],'momenthealth')
        self.assertIn('.putDouble(',by[202]['operand'])
        # Independent finite key index: no hidden victim initializer is assumed.
        entries={m['entry'] for m in self.census['methods'] if any(i['operand']=='momenthealth' for i in decode_sites(self.census,m))}
        self.assertEqual(entries,{'net/arphex/procedures/WebbedArrowWhileProjectileFlyingTickProcedure.class',
                                 'net/arphex/procedures/WebbedArrowProjectileHitsLivingEntityProcedure.class'})

    def test_webbed_profiles_follow_raw_health_gate_and_clear_first(self):
        body=self.method('WebbedArrowProjectileHitsLivingEntityProcedure','execute')['instructions']
        profiles=[]
        for n,i in enumerate(body):
            if 'MobEffectInstance.<init>' in str(i['operand']):profiles.append([x['operand'] for x in body[n-4:n]])
        self.assertEqual(profiles,[[60,0,0,0],[80,1,0,0],[100,2,0,0],[120,3,0,0],[140,4,0,0]])
        self.assertIn('getHealth()',next(i['operand'] for i in body if i['offset']==18))
        self.assertIn('.putDouble(',next(i['operand'] for i in body if i['offset']==47))
        self.assertLess(47,107)

    def test_unused_shoot_helpers_are_excluded_but_blood_ranged_path_is_live(self):
        for name in ('WidowArrowEntity','WebbedArrowEntity'):
            prefix=f'net/arphex/entity/{name}.shoot('
            callers=[m for m in self.census['methods'] if m['entry']!=f'net/arphex/entity/{name}.class'
                     and any(prefix in i['operand'] for i in decode_sites(self.census,m,'calls'))]
            self.assertEqual(callers,[])
            self.assertFalse(any(prefix in str(b['arguments']) for b in self.census['registration_bootstraps']))
        prefix='net/arphex/entity/BloodProjectileEntity.shoot('
        callers={(m['entry'],m['method']) for m in self.census['methods'] if m['entry']!='net/arphex/entity/BloodProjectileEntity.class'
                 and any(prefix in i['operand'] for i in decode_sites(self.census,m,'calls'))}
        self.assertEqual(callers,{(f'net/arphex/entity/{name}.class','performRangedAttack') for name in ('SpiderMothLarvaeEntity','SpiderMothSummonLarvaeEntity')})
        body=self.method('BloodProjectileEntity','shoot','(Lnet/minecraft/world/entity/LivingEntity;Lnet/minecraft/world/entity/LivingEntity;)Lnet/arphex/entity/BloodProjectileEntity;')['instructions']
        by={i['offset']:i for i in body}
        self.assertEqual([by[n]['operand'] for n in (43,75,82,84,95,102)],[1.1,.20000000298023224,3.0,12.0,2.5,3])

    def test_brood_pickup_does_not_create_custom_status(self):
        w=next(w for w in self.native['witnesses'] if w['entry'].endswith('/SpiderBroodEntityProjectile.class'))
        names=set(w['declared_method_names'])
        self.assertFalse(names&{'onHitEntity','onHitBlock','tick','doKnockback','hurt'})
        self.assertFalse(any('/procedures/' in str(i['operand']) for m in w['methods'] for i in m['instructions']))
        body=self.method('SpiderBroodEntity','performRangedAttack')['instructions'];by={i['offset']:i for i in body}
        self.assertEqual([by[n]['operand'] for n in (32,84,91,94)],[1.1,.20000000298023224,1.600000023841858,12.0])

    def test_native_constructor_retains_shooter_owner(self):
        refs=read_json(OUT/'vanilla-evidence/arphex-arrow-owner-construction.json')['classes']
        arrow=next(w for w in refs if w['class_name'].endswith('/AbstractArrow'))
        ctor=next(m for m in arrow['methods'] if 'Lbtn;' in m['obfuscated_descriptor'])
        body=ctor['instructions'];at=next(n for n,i in enumerate(body) if '.setOwner(' in str(i['operand']))
        self.assertEqual([i['opcode'] for i in body[at-2:at]],['0x2a','0x2c'])
        projectile=next(w for w in refs if w['class_name'].endswith('/Projectile'))
        setter=next(m for m in projectile['methods'] if m['name']=='setOwner')['instructions']
        self.assertTrue(any('ownerUUID' in str(i['operand']) for i in setter))
        self.assertTrue(any('cachedOwner' in str(i['operand']) for i in setter))


class ProjectileLifecycleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.native=read_json(OUT/'native-evidence/arphex-projectile-lifecycle-and-control.json')
        cls.vanilla=read_json(OUT/'vanilla-evidence/arphex-selector-scope.json')
        cls.census=read_json(OUT/'arphex-combat-census.json')
        cls.batch=read_json(OUT/'arphex-r2m3b-projectile-lifecycle-and-control.json')

    def method(self,name,method,descriptor=None,vanilla=False):
        if vanilla:
            w=next(w for w in self.vanilla['classes'] if w['class_name'].endswith('/'+name))
        else:
            w=next(w for w in self.native['witnesses'] if w['entry'].endswith('/'+name+'.class'))
        return next(m for m in w['methods'] if m['name']==method and
                    (descriptor is None or m.get('descriptor')==descriptor))

    def test_exact_consumers_and_five_meaningful_contracts(self):
        review=read_json(OUT/'mod-reviews/arphex.json');ids={r['id'] for r in self.batch['effects']}
        review['effects']=[r for r in review['effects'] if r['id'] not in ids]
        review['paths']=[p for p in review['paths'] if not set(p['effect_ids'])&ids]
        self.assertEqual(validate_batch(self.batch,review,self.census)['semantic_records'],len(review['effects'])+5)
        self.assertEqual(sum(len(c['parameters']) for r in self.batch['effects'] for c in r['scalable_parameter_candidates']),15)

    def test_miniature_core_damage_preserves_source_integer_order_and_independent_stuck(self):
        hit=self.method('MiniatureCoreEntity','onHitEntity')['instructions']
        self.assertIn('AbstractArrow.onHitEntity(',hit[2]['operand'])
        self.assertEqual(hit[-3]['operand'],'net/arphex/entity/MiniatureCoreEntity.getOwner()Lnet/minecraft/world/entity/Entity;')
        self.assertEqual(hit[-2]['offset'],30)
        self.assertFalse(any(i.get('branch_target') for i in hit))
        body=self.method('MiniatureCoreProjectileHitsLivingEntityProcedure','execute')['instructions'];by={i['offset']:i for i in body}
        self.assertEqual([by[n]['operand'] for n in (93,119,121,150,177,203,205,261,280,283,286)],
                         [15,4,4,100.0,15,4,4,100.0,.25,.05,.25])
        self.assertEqual(sum(i['opcode']=='0x6c' for i in body),4) # nested INTEGER divisions
        self.assertEqual(by[24]['branch_target'],32) # server discard does not exit helper
        for offset in (209,264):
            at=next(n for n,i in enumerate(body) if i['offset']==offset)
            self.assertEqual(body[at+1]['opcode'],'0x57') # hurt result discarded
        self.assertIn('.makeStuckInBlock(',by[292]['operand'])
        constructors=[i['operand'] for i in body if 'DamageSource.<init>' in str(i['operand'])]
        self.assertEqual(constructors,['net/minecraft/world/damagesource/DamageSource.<init>(Lnet/minecraft/core/Holder;Lnet/minecraft/world/entity/Entity;)V']*2)
        self.assertEqual(by[44]['opcode'],'0xa5') # owner == recipient rejects extra payload

    def test_gravity_and_cleanup_use_projectile_and_repeat_only_native_delivery_checks(self):
        for name,helper,delay in [('InvisibleArrowEntity','InvisibleArrowWhileProjectileFlyingTickProcedure',200),
                                  ('AscendantArrowEntity','AscendantArrowWhileProjectileFlyingTickProcedure',60),
                                  ('MiniatureCoreEntity','MiniatureCoreWhileProjectileFlyingTickProcedure',100),
                                  ('SpinpartitestEntity','SpinpartitestWhileProjectileFlyingTickProcedure',400)]:
            tick=self.method(name,'tick')['instructions']
            at=next(n for n,i in enumerate(tick) if helper+'.execute(' in str(i['operand']))
            self.assertEqual(tick[at-1]['opcode'],'0x2a')
            self.assertFalse(any('.getOwner(' in str(i['operand']) for i in tick))
            body=self.method(helper,'execute')['instructions']
            self.assertTrue(any(i['operand']==delay for i in body))
            self.assertEqual(sum('queueServerWork(' in str(i['operand']) for i in body),1)
            delayed=self.method(helper,'lambda$execute$0')['instructions']
            self.assertEqual([i['operand'] for i in delayed if i['opcode']=='0xb6'],
                ['net/minecraft/world/entity/Entity.level()Lnet/minecraft/world/level/Level;',
                 'net/minecraft/world/level/Level.isClientSide()Z','net/minecraft/world/entity/Entity.discard()V'])

    def test_type_and_distance_selectors_have_independent_native_world_scope(self):
        for helper,literal in [('DisappearInvisibleWhileProjectileFlyingTickProcedure','kill @e[type=arphex:projectile_disappear_invisible]'),
                               ('WebRopeWhileProjectileFlyingTickProcedure','kill @e[type=arphex:projectile_web_rope,distance=..50]')]:
            body=self.method(helper,'execute')['instructions'];by={i['offset']:i for i in body}
            self.assertEqual(by[64]['operand'],literal)
            self.assertEqual(next(i for i in body if i['offset']==57)['opcode'],'0x1') # NULL entity
        type_handler=self.method('EntitySelectorOptions','lambda$bootStrap$44',vanilla=True)['instructions']
        self.assertTrue(any('.limitToType(' in str(i['operand']) for i in type_handler))
        self.assertFalse(any('.setWorldLimited(' in str(i['operand']) for i in type_handler))
        for name in ('<init>','parseSelector'):
            self.assertFalse(any(i['opcode']=='0xb5' and '.worldLimited' in str(i['operand'])
                                for i in self.method('EntitySelectorParser',name,vanilla=True)['instructions']))
        distance=self.method('EntitySelectorOptions','lambda$bootStrap$8',vanilla=True)['instructions']
        self.assertTrue(any('.setWorldLimited(' in str(i['operand']) for i in distance))
        find=self.method('EntitySelector','findEntities',vanilla=True);by={i['offset']:i for i in find['instructions']}
        code=bytes.fromhex(find['code_hex'])
        self.assertEqual(by[235]['opcode'],'0x99')
        self.assertEqual(235+int.from_bytes(code[236:238],'big',signed=True),254)
        self.assertIn('.getLevel()',by[242]['operand'])
        self.assertIn('.getAllLevels()',by[258]['operand'])
        levels=self.method('MinecraftServer','getAllLevels',vanilla=True)['instructions']
        self.assertEqual(levels[1]['operand'],'net/minecraft/server/MinecraftServer.levelsLjava/util/Map;')
        self.assertEqual(levels[2]['operand'],'java/util/Map.values()Ljava/util/Collection;')

    def test_web_rope_real_producers_supply_zero_damage_and_release_on_missing_ammo(self):
        prefix='net/arphex/entity/WebRopeEntity.shoot('
        callers=[m for m in self.census['methods'] if m['entry']!='net/arphex/entity/WebRopeEntity.class'
                 and any(prefix in i['operand'] for i in decode_sites(self.census,m,'calls'))]
        self.assertEqual({(m['entry'],m['method']) for m in callers},
                         {(f'net/arphex/item/{name}.class','onUseTick') for name in ('SilkSlingerItem','TarantulaTetherItem')})
        for name in ('SilkSlingerItem','TarantulaTetherItem'):
            body=self.method(name,'onUseTick')['instructions'];by={i['offset']:i for i in body}
            self.assertEqual(by[44]['branch_target'],125)
            self.assertIn('.releaseUsingItem()',by[126]['operand'])
            self.assertTrue(by[53]['operand'].endswith('RandomSource;)Lnet/arphex/entity/WebRopeEntity;'))
            predicate=self.method(name,'lambda$findAmmo$1')['instructions']
            self.assertEqual(predicate[2]['operand'],'net/arphex/entity/WebRopeEntity.PROJECTILE_ITEMLnet/minecraft/world/item/ItemStack;')
        desc='(Lnet/minecraft/world/level/Level;Lnet/minecraft/world/entity/LivingEntity;Lnet/minecraft/util/RandomSource;)Lnet/arphex/entity/WebRopeEntity;'
        by={i['offset']:i for i in self.method('WebRopeEntity','shoot',desc)['instructions']}
        self.assertEqual([by[n]['operand'] for n in (3,5,6)],[7.0,0.0,0])
        full=desc.replace('RandomSource;)', 'RandomSource;FDI)')
        by={i['offset']:i for i in self.method('WebRopeEntity','shoot',full)['instructions']}
        self.assertEqual([by[n]['operand'] for n in (48,50)],[2.0,0.0])
        self.assertIn('.setBaseDamage(D)',by[70]['operand'])

    def test_spin_native_zero_x_gate_and_particles_are_not_scalar_candidates(self):
        body=self.method('SpinpartitestWhileProjectileFlyingTickProcedure','execute')['instructions']
        by={i['offset']:i for i in body}
        self.assertEqual(by[21]['operand'],'deltalockx')
        self.assertEqual(by[28]['opcode'],'0x9a')
        self.assertEqual(by[28]['branch_target'],82)
        self.assertIn('.setDeltaMovement(',by[117]['operand'])
        commands=[i for i in body if i['opcode']=='0x12' and isinstance(i['operand'],str) and 'run particle' in i['operand']]
        self.assertEqual(len(commands),16)
        row=next(r for r in self.batch['effects'] if r['id']=='arphex:spin_projectile_intrinsic_vector_lock')
        self.assertEqual([c['parameters'] for c in row['scalable_parameter_candidates']],[['discard_delay']])


class ProjectileControlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.native=read_json(OUT/'native-evidence/arphex-remaining-intrinsic-projectiles.json')
        cls.batch=read_json(OUT/'arphex-r2m3c-intrinsic-control-and-harness.json')
        cls.census=read_json(OUT/'arphex-combat-census.json')

    def method(self,name,method):
        w=next(w for w in self.native['witnesses'] if w['entry'].endswith('/'+name+'.class'))
        return next(m for m in w['methods'] if m['name']==method)

    def test_batch_preserves_shared_contract_identity_and_real_consumers(self):
        review=read_json(OUT/'mod-reviews/arphex.json');ids={r['id'] for r in self.batch['effects']}
        review['effects']=[r for r in review['effects'] if r['id'] not in ids]
        review['paths']=[p for p in review['paths'] if not set(p['effect_ids'])&ids]
        self.assertEqual(validate_batch(self.batch,review,self.census)['semantic_records'],len(review['effects'])+7)
        self.assertEqual(len(self.batch['record_refinements']),2)
        self.assertNotIn('arphex:bloodthirsty_tendril_payload',ids)
        self.assertNotIn('arphex:gravity_free_arrow_native_cleanup',ids)

    def test_intrinsic_queue_covers_finite_arrow_classes_without_claiming_producer_closure(self):
        q=read_json(OUT/'arphex-intrinsic-projectile-review-queue.json')
        expected={c['entry'] for c in self.census['classes'] if c['superclass']=='net/minecraft/world/entity/projectile/AbstractArrow'}
        self.assertEqual({r['entry'] for r in q['rows']},expected)
        self.assertEqual(len(q['rows']),len(expected))
        closed=sum(r['disposition']=='CLOSED_INTRINSIC_CALLBACKS' for r in q['rows'])
        self.assertEqual(closed,q['closed_intrinsic_callback_classes'])
        self.assertEqual(len(expected)-closed,q['pending_intrinsic_callback_classes'])
        self.assertFalse(q['whole_mod_complete'])
        self.assertIn('factories',q['scope'])
        ids={r['id'] for r in read_json(OUT/'mod-reviews/arphex.json')['effects']}
        for row in q['rows']:
            self.assertLessEqual(set(row['canonical_contract_ids']+row['already_closed_shared_subcontracts']),ids)

    def test_graviton_mirror_state_write_and_velocity_read_have_different_receivers(self):
        by={i['offset']:i for i in self.method('GravitonTickProcedure','execute')['instructions']}
        self.assertEqual([by[n]['opcode'] for n in (422,447,472)],['0x2c']*3) # projectile
        self.assertEqual([by[n]['opcode'] for n in (502,511,520)],['0x2b']*3) # owner
        self.assertEqual(by[440]['operand'],2.0)
        row=next(r for r in self.batch['effects'] if r['id']=='arphex:graviton_arrow_intrinsic_damage_and_motion')
        self.assertFalse(any('mirror' in p for c in row['scalable_parameter_candidates'] for p in c['parameters']))

    def test_graviton_damage_admission_latch_and_source(self):
        body=self.method('GravitonHitsEntityProcedure','execute')['instructions']
        self.assertTrue(any('.isOwnedBy(' in str(i['operand']) for i in body))
        self.assertTrue(any('.isBlocking(' in str(i['operand']) for i in body))
        self.assertTrue(any('.ABYSS_ASCENDANT' in str(i['operand']) for i in body))
        self.assertTrue(any(i['operand']==108.0 for i in body))
        self.assertTrue(any(i['operand']==17.0 for i in body))
        self.assertTrue(any(i['operand']==7.0 for i in body))
        for k,i in enumerate(body):
            if '.hurt(' in str(i['operand']):self.assertEqual(body[k+1]['opcode'],'0x57')
        self.assertEqual(sum('DamageSource.<init>(Lnet/minecraft/core/Holder;Lnet/minecraft/world/entity/Entity;)V' in str(i['operand']) for i in body),2)

    def test_hook_profiles_are_distinct_and_motion_precedes_status(self):
        expected={'PowerHookHitsEntityProcedure':[[80,1,0,0],[100,2,0,0],[120,3,0,0],[140,3,0,0],[200,4,0,0]],
                  'WebHookProjectileHitsLivingEntityProcedure':[[60,0,0,0],[80,1,0,0],[100,2,0,0],[120,3,0,0],[140,4,0,0]]}
        for name,profiles in expected.items():
            body=self.method(name,'execute')['instructions']
            actual=[[x['operand'] for x in body[k-4:k]] for k,i in enumerate(body) if 'MobEffectInstance.<init>' in str(i['operand'])]
            self.assertEqual(actual,profiles)
            self.assertEqual(next(i['offset'] for i in body if '.setDeltaMovement(' in str(i['operand'])),84)
            self.assertLess(84,next(i['offset'] for i in body if 'MobEffectInstance.<init>' in str(i['operand'])))

    def test_hook_cleanup_literal_targets_power_hook_for_both_intrinsic_wrappers(self):
        for name in ['PowerHookEntity','WebHookEntity']:
            body=self.method(name,'tick')['instructions']
            self.assertTrue(any('WebHookWhileProjectileFlyingTickProcedure.execute' in str(i['operand']) for i in body))
        delayed=self.method('WebHookWhileProjectileFlyingTickProcedure','lambda$execute$0')['instructions']
        self.assertTrue(any(i['operand']=='execute at @p run kill @e[type=arphex:projectile_power_hook,distance=..4]' for i in delayed))

    def test_harness_raw_zero_admission_omits_y_and_runtime_status_is_only_harness_constructor(self):
        w=next(w for w in self.native['witnesses'] if w['entry'].endswith('/WebHarnessOnEntityTickUpdateProcedure.class'))
        lambdas=[m for m in w['methods'] if m['name'].startswith('lambda')]
        matching=[m for m in lambdas if sum(i['operand']=='targetX' for i in m['instructions'])==2 and
                  sum(i['operand']=='targetZ' for i in m['instructions'])==1]
        self.assertEqual(len(matching),1)
        self.assertFalse(any(i['operand']=='targetY' for i in matching[0]['instructions']))
        body=self.method('WebHarnessOnEntityTickUpdateProcedure','execute')['instructions']
        self.assertEqual(sum('MobEffectInstance.<init>' in str(i['operand']) for i in body),1)
        self.assertTrue(any(i['operand']=='effect give @p[distance=..5] slow falling 2 0 true' for i in body))
        row=next(r for r in self.batch['effects'] if r['id']=='arphex:hook_harness_native_anchor_control')
        self.assertEqual([c['parameters'] for c in row['scalable_parameter_candidates'] if c['primitive']=='MOB_EFFECT_SLOW_FALLING'],[['near_anchor_duration']])

    def test_native_effect_command_grammar_rejects_space_as_part_of_effect_id(self):
        evidence=read_json(OUT/'vanilla-evidence/arphex-effect-command-grammar.json')['classes']
        resource=next(w for w in evidence if w['class_name'].endswith('/ResourceLocation'))
        method=next(m for m in resource['methods'] if m['name']=='isAllowedInResourceLocation')
        code=bytes.fromhex(method['code_hex'])
        def allows(character):
            pc=0;stack=[]
            while True:
                op=code[pc]
                if op==0x1a:stack.append(ord(character));pc+=1
                elif 0x03<=op<=0x08:stack.append(op-3);pc+=1
                elif op==0x10:stack.append(int.from_bytes(code[pc+1:pc+2],'big',signed=True));pc+=2
                elif op in (0x9f,0xa0,0xa1,0xa4):
                    right=stack.pop();left=stack.pop()
                    condition={0x9f:left==right,0xa0:left!=right,0xa1:left<right,0xa4:left<=right}[op]
                    pc+=int.from_bytes(code[pc+1:pc+3],'big',signed=True) if condition else 3
                elif op==0xa7:pc+=int.from_bytes(code[pc+1:pc+3],'big',signed=True)
                elif op==0xac:return bool(stack.pop())
                else:self.fail('unexpected native predicate opcode '+hex(op))
        self.assertFalse(allows(' '));self.assertTrue(all(allows(c) for c in 'minecraft:slow_falling'))
        greedy=next(m for m in resource['methods'] if m['name']=='readGreedy')['instructions']
        self.assertTrue(any('.isAllowedInResourceLocation(' in str(i['operand']) for i in greedy))
        effect=next(w for w in evidence if w['class_name'].endswith('/EffectCommands'))
        register=next(m for m in effect['methods'] if m['name']=='register')['instructions']
        self.assertTrue(any(i['operand']=='seconds' for i in register))
        self.assertTrue(any('IntegerArgumentType.integer(II)' in str(i['operand']) for i in register))
        with self.assertRaises(ValueError):int('falling')

    def test_spacetime_sources_and_motion_reflection_order_stay_separate(self):
        hit=self.method('SpacetimeAnchorProjectileHitsLivingEntityProcedure','execute')['instructions']
        ctors=[i['operand'] for i in hit if 'DamageSource.<init>' in str(i['operand'])]
        self.assertEqual(ctors,['net/minecraft/world/damagesource/DamageSource.<init>(Lnet/minecraft/core/Holder;Lnet/minecraft/world/entity/Entity;)V',
                                'net/minecraft/world/damagesource/DamageSource.<init>(Lnet/minecraft/core/Holder;)V',
                                'net/minecraft/world/damagesource/DamageSource.<init>(Lnet/minecraft/core/Holder;Lnet/minecraft/world/entity/Entity;)V'])
        tick=self.method('SpacetimeAnchorWhileProjectileFlyingTickProcedure','execute')['instructions'];by={i['offset']:i for i in tick}
        self.assertIn('.setDeltaMovement(',by[446]['operand'])
        self.assertIn('.putDouble(',by[667]['operand']);self.assertGreater(667,446)
        self.assertEqual([by[n]['operand'] for n in (360,382,404)],[1.05]*3)

    def test_shared_block_explosion_is_null_source_and_single_helper_for_three_arrows(self):
        body=self.method('GenesisShotProjectileHitsBlockProcedure','execute')['instructions'];by={i['offset']:i for i in body}
        self.assertEqual(next(i for i in body if i['offset']==93)['opcode'],'0x1')
        self.assertIn('.explode(',by[114]['operand'])
        for name in ['GenesisShotEntity','ChronoShotEntity','GravitonShotEntity']:
            self.assertTrue(any('GenesisShotProjectileHitsBlockProcedure.execute' in str(i['operand'])
                                for i in self.method(name,'onHitBlock')['instructions']))
        self.assertEqual(sum(r['id']=='arphex:shared_genesis_projectile_block_explosion' for r in self.batch['effects']),1)


if __name__=='__main__':unittest.main()


