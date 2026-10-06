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


class ProjectileAreaFlameTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.native=read_json(OUT/'native-evidence/arphex-remaining-intrinsic-projectiles.json')
        cls.census=read_json(OUT/'arphex-combat-census.json')
        cls.batch=read_json(OUT/'arphex-r2m3d-intrinsic-flame-area-and-spark.json')

    def method(self,name,method='execute'):
        w=next(w for w in self.native['witnesses'] if w['entry'].endswith('/'+name+'.class'))
        return next(m for m in w['methods'] if m['name']==method)

    def test_four_contracts_cover_five_native_callback_paths_with_exact_scalar_consumers(self):
        review=read_json(OUT/'mod-reviews/arphex.json');ids={r['id'] for r in self.batch['effects']}
        review['effects']=[r for r in review['effects'] if r['id'] not in ids]
        review['paths']=[p for p in review['paths'] if not set(p['effect_ids'])&ids]
        self.assertEqual(validate_batch(self.batch,review,self.census)['semantic_records'],len(review['effects'])+4)
        self.assertEqual(len(self.batch['intrinsic_closed_entries']),5)
        self.assertEqual(sum(len(c['parameters']) for r in self.batch['effects'] for c in r['scalable_parameter_candidates']),45)

    def test_abyss_area_is_owner_free_integer_formula_and_delayed_config_recheck(self):
        m=self.method('AbyssExplosiveProjectileHitsBlockProcedure');body=m['instructions']
        self.assertEqual(m['descriptor'],'(Lnet/minecraft/world/level/LevelAccessor;DDD)V')
        self.assertEqual(sum(i['opcode']=='0x6c' for i in body),2) # integer armor denominator/division
        self.assertEqual([i['operand'] for i in body if 'DamageSource.<init>' in str(i['operand'])],
                         ['net/minecraft/world/damagesource/DamageSource.<init>(Lnet/minecraft/core/Holder;)V']*2)
        delayed=self.method('AbyssExplosiveProjectileHitsBlockProcedure','lambda$execute$2')['instructions']
        self.assertTrue(any('.ARPHEX_ITEM_GRIEFING' in str(i['operand']) for i in delayed))
        self.assertTrue(any(i['operand']==6.0 for i in delayed))
        for b in (body,delayed):
            self.assertTrue(any('ExplosionInteraction.TNT' in str(i['operand']) for i in b))
        for name in ('onHitEntity','onHitBlock'):
            self.assertTrue(any('AbyssExplosiveProjectileHitsBlockProcedure.execute' in str(i['operand'])
                                for i in self.method('AbyssExplosiveEntity',name)['instructions']))

    def test_flame_fire_has_two_empty_block_tests_without_invented_griefing_or_damage(self):
        body=self.method('AoEflameProjectileHitsBlockProcedure')['instructions']
        self.assertEqual(sum('.isEmptyBlock(' in str(i['operand']) for i in body),2)
        self.assertEqual(sum('.setBlock(' in str(i['operand']) for i in body),2)
        self.assertEqual(sum('.FIRE' in str(i['operand']) for i in body),2)
        self.assertFalse(any(any(x in str(i['operand']) for x in ['.hurt(','.igniteForSeconds(','.isClientSide(','.ARPHEX_ITEM_GRIEFING']) for i in body))
        for helper,maximum in [('AoEflameWhileProjectileFlyingTickProcedure',8),('AoEFlame2TickProcedure',11)]:
            b=self.method(helper)['instructions'];by={i['offset']:i for i in b}
            self.assertEqual([by[n]['operand'] for n in (6,68,79)],[3,3,maximum])
            self.assertTrue(any(i['operand']=='pastsource' for i in b))
            self.assertTrue(any('.setNoGravity(' in str(i['operand']) for i in b))

    def test_spark_motion_precedes_raw_increment_and_has_no_intrinsic_homing_or_no_gravity(self):
        body=self.method('SparkWhileFlyingProcedure')['instructions'];by={i['offset']:i for i in body}
        self.assertIn('.setDeltaMovement(',by[62]['operand'])
        self.assertIn('.putDouble(',by[84]['operand'])
        self.assertEqual(by[80]['operand'],.2)
        self.assertTrue(any(i['operand']==-.8 for i in body))
        self.assertFalse(any('.getTarget(' in str(i['operand']) or '.setNoGravity(' in str(i['operand']) for i in body))
        hit=self.method('SparkProjectileHitsLivingEntityProcedure')['instructions']
        discard=next(i['offset'] for i in hit if '.discard(' in str(i['operand']))
        hurt=next(i['offset'] for i in hit if '.hurt(' in str(i['operand']))
        self.assertLess(discard,hurt)
        self.assertTrue(any('Math.max(FF)' in str(i['operand']) for i in hit))

    def test_dracon_direct_damage_control_then_roll_is_independent_of_hurt_result(self):
        body=self.method('DraconFireProjectileHitsLivingEntityProcedure')['instructions'];by={i['offset']:i for i in body}
        at=next(n for n,i in enumerate(body) if i['offset']==123)
        self.assertEqual(body[at+1]['opcode'],'0x57')
        self.assertIn('.setDeltaMovement(',by[141]['operand'])
        self.assertIn('.nextInt(',by[149]['operand'])
        self.assertEqual([by[n]['operand'] for n in (116,134,147,148)],[20.0,-5.0,1,3])
        self.assertTrue(any('Math.round(F)I' in str(i['operand']) for i in body))
        profiles=[[x['operand'] for x in body[n-4:n]] for n,i in enumerate(body) if 'MobEffectInstance.<init>' in str(i['operand'])]
        self.assertEqual(profiles,[[60,9,0,0],[180,0,0,0]])
        block=self.method('DraconFireProjectileHitsBlockProcedure')['instructions']
        self.assertTrue(any(i['operand']=='creativespectator' for i in block))
        self.assertTrue(any('MobEffectInstance.<init>(Lnet/minecraft/core/Holder;II)' in str(i['operand']) for i in block))

    def test_dracon_area_latches_before_request_and_reflection_reads_projectile(self):
        body=self.method('DraconFireWhileProjectileFlyingTickProcedure')['instructions']
        first_hurt=next(i['offset'] for i in body if '.hurt(' in str(i['operand']))
        writes=[i['offset'] for i in body if '.putBoolean(' in str(i['operand'])]
        self.assertTrue(any(o<first_hurt for o in writes))
        self.assertTrue(any(i['operand']=='doneit' for i in body))
        self.assertTrue(any(i['operand']==380 for i in body))
        self.assertTrue(any(i['operand']==150 for i in body))
        self.assertTrue(any(i['operand']==300 for i in body))
        for key in ('fixedxvel','fixedyvel','fixedzvel'):
            sites=[(n,i) for n,i in enumerate(body) if i['operand']==key]
            self.assertEqual(len(sites),4) # two native owner-type arms, write and read
            for n,i in sites:
                self.assertEqual(body[n-2].get('local_index'),8) # THIS projectile, not owner(local7)
        self.assertFalse(any(i['operand']=='uuid_compare_source' for i in body))

    def test_static_generated_defaults_have_no_external_census_callers(self):
        for entry in self.batch['intrinsic_closed_entries']:
            prefix=entry[:-6]+'.shoot('
            self.assertFalse(any(prefix in i['operand'] for m in self.census['methods'] if m['entry']!=entry
                                 for i in decode_sites(self.census,m,'calls')))
            self.assertFalse(any(prefix in str(b['arguments']) for b in self.census['registration_bootstraps']))


class ProjectileOwnerAndHazardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.native=read_json(OUT/'native-evidence/arphex-remaining-intrinsic-projectiles.json')
        cls.consumers=read_json(OUT/'native-evidence/arphex-projectile-direct-consumers.json')
        cls.census=read_json(OUT/'arphex-combat-census.json')
        cls.batch=read_json(OUT/'arphex-r2m3e-owner-homing-and-owned-hazards.json')

    def consumer_method(self,name,method='execute'):
        w=next(w for w in self.consumers['witnesses'] if w['entry'].endswith('/'+name+'.class'))
        return next(m for m in w['methods'] if m['name']==method)

    method = ProjectileContractsTests.method
    def test_batch_has_four_unique_payload_contracts_and_real_scalar_consumers(self):
        review=read_json(OUT/'mod-reviews/arphex.json');ids={r['id'] for r in self.batch['effects']}
        review['effects']=[r for r in review['effects'] if r['id'] not in ids]
        review['paths']=[p for p in review['paths'] if not set(p['effect_ids'])&ids]
        self.assertEqual(len(ids),6)
        self.assertEqual(validate_batch(self.batch,review,self.census)['semantic_records'],len(review['effects'])+6)
        self.assertEqual(len(self.batch['intrinsic_closed_entries']),4)

    def test_parent_arrow_attempt_precedes_extra_helper(self):
        for name in ('ChronoShotEntity','GenesisShotEntity','HomingVoidseekerEntity','JudgementBlastEntity'):
            body=self.method(name,'onHitEntity')['instructions']
            parent=next(i['offset'] for i in body if 'AbstractArrow.onHitEntity(' in str(i['operand']))
            helper=next(i['offset'] for i in body if '/procedures/' in str(i['operand']))
            self.assertLess(parent,helper)
            self.assertFalse(any(i['opcode'] in ('0x99','0x9a') for i in body if parent<i['offset']<helper))

    def test_genesis_wither_captures_eligible_area_local_not_player_loop(self):
        body=self.method('GenesisShotWhileProjectileFlyingTickProcedure','execute')['instructions'];by={i['offset']:i for i in body}
        self.assertEqual(by[1743]['opcode'],'0x3a');self.assertEqual(by[1743]['local_index'],26)
        self.assertEqual(by[1740]['operand'],'net/minecraft/world/entity/Entity')
        self.assertIn('Iterator.next(',by[1735]['operand'])
        self.assertEqual(by[1763]['operand'],'net/minecraft/world/entity/player/Player')
        self.assertEqual(by[1766]['branch_target'],1831)
        self.assertEqual(by[1821]['local_index'],26)
        self.assertIn('bootstrap#4:run(Lnet/minecraft/world/entity/Entity;)',by[1823]['operand'])
        delayed=self.method('GenesisShotWhileProjectileFlyingTickProcedure','lambda$execute$4')['instructions']
        self.assertEqual(delayed[0]['opcode'],'0x2a')
        self.assertTrue(any('MobEffects.WITHER' in str(i['operand']) for i in delayed))
        self.assertEqual([i['operand'] for i in delayed if i['offset'] in (30,32,33,34)],[60,1,0,0])

    def test_genesis_first_fraction_precedes_player_and_sqrt_requests(self):
        body=self.method('GenesisShotProjectileHitsLivingEntityProcedure','execute')['instructions'];by={i['offset']:i for i in body}
        self.assertEqual(by[288]['operand'],1000.0);self.assertEqual(by[290]['opcode'],'0x6e')
        players=[i['offset'] for i in body if i['operand']=='net/minecraft/world/entity/player/Player']
        self.assertTrue(players and min(players)>291)
        self.assertEqual(by[449]['operand'],2.5);self.assertEqual(by[453]['opcode'],'0x90')
        self.assertEqual(by[481]['operand'],60.0)
        for off in (81,291,351,454,483):
            at=next(n for n,i in enumerate(body) if i['offset']==off)
            self.assertEqual(body[at+1]['opcode'],'0x57')

    def test_chrono_mirror_reads_owner_fields_after_projectile_writes(self):
        body=self.method('ChronoShotWhileProjectileFlyingTickProcedure','execute')['instructions']
        writes=[n for n,i in enumerate(body) if i['operand']=='limit_homing_x' and i['offset']>500]
        self.assertEqual(len(writes),2)
        self.assertEqual(body[writes[0]-2]['opcode'],'0x2c') # projectile local2
        self.assertEqual(body[writes[1]-2]['opcode'],'0x2b') # OWNER local1
        self.assertFalse(any(c['primitive']=='PROJECTILE_HOMING' and 'reflected_speed' in c['parameters'] for r in self.batch['effects'] for c in r['scalable_parameter_candidates']))

    def test_voidseeker_owner_tracker_and_fallback_are_not_projectile_local(self):
        body=self.method('VoidseekerProjectileTickProcedure','execute')['instructions']
        at=next(n for n,i in enumerate(body) if i['operand']=='distancetravelledvoid' and i['offset']>135)
        self.assertEqual(body[at-2]['local_index'],7)
        delayed=self.method('VoidseekerProjectileTickProcedure','lambda$execute$2')['instructions']
        self.assertTrue(any(i['operand']==-.2 for i in delayed))
        self.assertFalse(any('sneakfire' in str(i['operand']) or 'reverse_mirror_attack' in str(i['operand']) or '.isClientSide(' in str(i['operand']) for i in delayed))

    def test_sphere_has_live_black_command_and_separate_black_hole_payload(self):
        from promote_combat_batch import concat_command_binding
        m=self.consumer_method('SphereAnimOnEntityTickUpdateProcedure');body=m['instructions'];by={i['offset']:i for i in body}
        binding=concat_command_binding(m,954,self.census,'net/arphex/procedures/SphereAnimOnEntityTickUpdateProcedure.class')
        self.assertTrue(binding['template'].startswith('effect give @e[nbt=!{SelectedItem:'))
        self.assertTrue(binding['template'].endswith('] wither 5 5'))
        self.assertEqual(binding['descriptor'],'(I)Ljava/lang/String;')
        self.assertEqual(by[946]['operand'],20);self.assertEqual(by[948]['opcode'],'0x6c')
        self.assertTrue(any('DATA_black_hole' in str(i['operand']) for i in body))
        self.assertTrue(any('DamageTypes.GENERIC' in str(i['operand']) for i in body))
        self.assertIn('.hurt(',by[1503]['operand']);self.assertIn('.setDeltaMovement(',by[1863]['operand'])
        self.assertEqual(by[1582]['operand'],200)
        self.assertTrue(any(i['opcode']=='0x6c' and 1582<i['offset']<1587 for i in body))
        self.assertEqual(by[1761]['operand'],.4)
        self.assertFalse('getDefaultDimensions' in next(w for w in self.consumers['witnesses'] if w['entry'].endswith('/SphereAnimEntity.class'))['declared_method_names'])
        producer=self.consumer_method('DiabolosTickProcedure','lambda$execute$11')['instructions']
        self.assertTrue(any('DATA_black_hole' in str(i['operand']) for i in producer))
        self.assertTrue(any(b['entry'].endswith('/DiabolosTickProcedure.class') and '.lambda$execute$11(' in str(b['arguments']) for b in self.census['registration_bootstraps']))
        self.assertTrue(any(m['entry'].endswith('/DiabolosDecimatorEntity.class') and m['method']=='baseTick' and any('DiabolosTickProcedure.execute(' in i['operand'] for i in decode_sites(self.census,m,'calls')) for m in self.census['methods']))

    def test_scorch_status_hurt_and_burn_are_separate_native_requests(self):
        body=self.consumer_method('ScorchEntityCollidesInTheBlockProcedure')['instructions'];by={i['offset']:i for i in body}
        self.assertLess(457,501);self.assertLess(501,526);self.assertLess(526,533)
        self.assertTrue(any('DamageTypes.IN_FIRE' in str(i['operand']) for i in body))
        at=next(n for n,i in enumerate(body) if i['offset']==526)
        self.assertEqual(body[at+1]['opcode'],'0x57')
        self.assertEqual(body[at-1]['operand'],2.0)
        self.assertEqual(by[531]['operand'],5.0)
        self.assertTrue(any('EntityTypeTags.ARTHROPOD' in str(i['operand']) for i in body))
        self.assertEqual(sum('.JUDGEMENT_BLASTER' in str(i['operand']) for i in body),2)
        self.assertTrue(any('.NECROSIS' in str(i['operand']) for i in body))
        tick=self.consumer_method('ScorchOnTickUpdateProcedure')['instructions']
        self.assertTrue(any('.nextInt(' in str(i['operand']) and i['offset']==15 for i in tick))
        self.assertEqual(sum('.setBlock(' in str(i['operand']) for i in tick),2)
        self.assertFalse(any('.ARPHEX_ITEM_GRIEFING' in str(i['operand']) for i in tick))

    def test_judgement_native_terrain_has_18_distinct_cells_and_no_explosion(self):
        body=self.method('JudgementBlastWhileProjectileFlyingTickProcedure','execute')['instructions']
        self.assertEqual(sum('.setBlock(' in str(i['operand']) for i in body),36) #18cells *2branches
        self.assertEqual(sum('.isEmptyBlock(' in str(i['operand']) for i in body),18)
        self.assertEqual(sum('.SCORCH' in str(i['operand']) for i in body),18)
        self.assertEqual(sum('.FIRE' in str(i['operand']) for i in body),18)
        self.assertEqual(sum(i['operand']==85 for i in body),18)
        self.assertFalse(any('.explode(' in str(i['operand']) or '.ARPHEX_ITEM_GRIEFING' in str(i['operand']) for i in body))
        hit=self.method('JudgementBlastProjectileHitsLivingEntityProcedure','execute')['instructions']
        self.assertFalse(any('.hurt(' in str(i['operand']) or '.addEffect(' in str(i['operand']) for i in hit))

    def test_wrong_concat_recipe_and_nonconcat_argument_fail_closed(self):
        import copy
        from promote_combat_batch import concat_command_binding
        m=self.consumer_method('SphereAnimOnEntityTickUpdateProcedure')
        with self.assertRaises(AssertionError):concat_command_binding(m,134,self.census,'net/arphex/procedures/SphereAnimOnEntityTickUpdateProcedure.class')
        batch=copy.deepcopy(self.batch)
        candidate=next(c for r in batch['effects'] for c in r['scalable_parameter_candidates'] if 'native_concat_command_binding' in c)
        candidate['native_concat_command_binding']['template']='effect give @e wither 999 999'
        review=read_json(OUT/'mod-reviews/arphex.json');ids={r['id'] for r in batch['effects']}
        review['effects']=[r for r in review['effects'] if r['id'] not in ids];review['paths']=[p for p in review['paths'] if not set(p['effect_ids'])&ids]
        with self.assertRaisesRegex(AssertionError,'wrong native concatenated command'):validate_batch(batch,review,self.census)

    def test_brood_type_only_removal_correction_keeps_exact_native_selector(self):
        record=next(r for r in read_json(OUT/'mod-reviews/arphex.json')['effects'] if r['id']=='arphex:spider_brood_incoming_payload')
        self.assertNotIn('in the command dimension',record['actual_behavior'])
        self.assertIn('across native server levels',record['actual_behavior'])
        origin=next(r for r in read_json(OUT/'arphex-r2m2f-incoming-status-weapon-payloads.json')['effects'] if r['id']==record['id'])
        self.assertEqual(origin['actual_behavior'],record['actual_behavior'])
        ev=read_json(OUT/'native-evidence/arphex-global-hooks.json')
        witness=next(w for w in ev['witnesses'] if w['entry'].endswith('/DwellerLifestealProcedure.class'))
        commands=[i['operand'] for m in witness['methods'] for i in m['instructions'] if isinstance(i['operand'],str) and i['operand'].startswith('kill @e[type=arphex:projectile_spider_brood')]
        self.assertTrue(commands);self.assertEqual(set(commands),{'kill @e[type=arphex:projectile_spider_brood]'})


class FinalIntrinsicArrowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.native=read_json(OUT/'native-evidence/arphex-remaining-intrinsic-projectiles.json')
        cls.census=read_json(OUT/'arphex-combat-census.json')
        cls.batch=read_json(OUT/'arphex-r2m3f-final-intrinsic-arrow-transactions.json')
    method=ProjectileContractsTests.method

    def test_final_five_and_shared_helper_have_native_consumers(self):
        review=read_json(OUT/'mod-reviews/arphex.json');ids={r['id'] for r in self.batch['effects']}
        review['effects']=[r for r in review['effects'] if r['id'] not in ids];review['paths']=[p for p in review['paths'] if not set(p['effect_ids'])&ids]
        self.assertEqual(len(ids),6);self.assertEqual(len(self.batch['intrinsic_closed_entries']),5)
        self.assertEqual(validate_batch(self.batch,review,self.census)['semantic_records'],len(review['effects'])+6)

    def test_rifle_hit_context_is_victim_and_block_context_is_owner(self):
        hit=self.method('TormentRifleEntity','onHitEntity')['instructions']
        block=self.method('TormentRifleEntity','onHitBlock')['instructions']
        self.assertTrue(any('EntityHitResult.getEntity(' in str(i['operand']) for i in hit))
        self.assertFalse(any('.getOwner(' in str(i['operand']) for i in hit))
        self.assertTrue(any('.getOwner(' in str(i['operand']) for i in block))
        for body in (hit,block):
            self.assertEqual(sum('TormentRifleHitsBlockProcedure.execute(' in str(i['operand']) for i in body),1)
            self.assertLess(next(i['offset'] for i in body if 'AbstractArrow.onHit' in str(i['operand'])),next(i['offset'] for i in body if '/procedures/' in str(i['operand'])))

    def test_rifle_far_compare_and_request_divisors_are_distinct(self):
        body=self.method('TormentRifleWhileProjectileFlyingTickProcedure','execute')['instructions'];by={i['offset']:i for i in body}
        self.assertTrue(any(i['operand']==20.0 and 800<i['offset']<1050 for i in body))
        self.assertEqual(by[1146]['operand'],40.0)
        self.assertTrue(any(i['opcode']=='0x6c' and 1064<i['offset']<1096 for i in body))
        self.assertEqual(by[1061]['operand'],'net/minecraft/world/damagesource/DamageSource.<init>(Lnet/minecraft/core/Holder;)V')
        self.assertTrue(any('DamageSource.<init>(Lnet/minecraft/core/Holder;Lnet/minecraft/world/entity/Entity;)' in str(i['operand']) and i['offset']<637 for i in body))

    def test_blast_health_write_is_after_attempt_and_before_terminal_hurt(self):
        body=self.method('TormentBlastTickProcedure','execute')['instructions'];by={i['offset']:i for i in body}
        self.assertIn('.hurt(',by[896]['operand']);self.assertIn('.setHealth(',by[1032]['operand'])
        self.assertEqual(by[1055]['operand'],1.0);self.assertIn('.setHealth(',by[1056]['operand'])
        self.assertEqual(by[1081]['operand'],99999.0);self.assertIn('.hurt(',by[1084]['operand'])
        at=next(n for n,i in enumerate(body) if i['offset']==896);self.assertEqual(body[at+1]['opcode'],'0x57')
        self.assertTrue(any('DamageSource.<init>(Lnet/minecraft/core/Holder;Lnet/minecraft/world/entity/Entity;Lnet/minecraft/world/entity/Entity;)' in str(i['operand']) for i in body))

    def test_explosive_direct_map_rounding_and_flight_map_subtraction_differ(self):
        direct=self.method('TormentExplosiveProjectileHitsLivingEntityProcedure','execute')['instructions']
        flying=self.method('TormentedExplosiveFlyingProcedure','execute')['instructions']
        self.assertTrue(any(i['operand']==40.8 for i in direct));self.assertTrue(any(i['operand']==44.5 for i in flying))
        dwrite=next(n for n,i in enumerate(direct) if i['opcode']=='0xb5' and '.tormentor_healthD' in str(i['operand']))
        fwrite=next(n for n,i in enumerate(flying) if i['opcode']=='0xb5' and '.tormentor_healthD' in str(i['operand']))
        self.assertEqual(direct[dwrite-1]['opcode'],'0x8a') # long->double after round(full subtraction)
        self.assertEqual(flying[fwrite-1]['opcode'],'0x67') # dsub after rounded charge
        self.assertFalse(any('damaged_tormentor'==i['operand'] and '.putBoolean(' in str(direct[n+2]['operand']) for n,i in enumerate(direct[:-2])))
        checks=[i['offset'] for i in flying if i['operand']=='damaged_tormentor']
        self.assertEqual(len(checks),2) # one loop-entry read and one inside-loop write
        self.assertLess(checks[0],467);self.assertGreater(checks[1],1001)

    def test_explosive_block_armor_reads_owner_and_terrain_skip_is_cell_count(self):
        body=self.method('TormentExplosiveProjectileHitsBlockProcedure','execute')['instructions'];by={i['offset']:i for i in body}
        armor=next(n for n,i in enumerate(body) if '.getArmorValue(' in str(i['operand']))
        cast=next(n for n in range(armor-1,-1,-1) if body[n]['opcode']=='0xc0' and body[n]['operand']=='net/minecraft/world/entity/LivingEntity')
        self.assertEqual(body[cast-1].get('local_index'),7) # OWNER helper argument, not areaiterator
        self.assertIn('WaitExplodeProcedure.execute(',by[554]['operand'])
        self.assertEqual(by[557]['operand'],20.0);self.assertEqual(by[567]['operand'],1.0)
        self.assertFalse(any('.explode(' in str(i['operand']) for i in body))

    def test_delayed_explosion_has_no_config_or_block_recheck(self):
        e=read_json(OUT/'native-evidence/arphex-delayed-block-explosion.json');w=e['witnesses'][0]
        body=next(m for m in w['methods'] if m['name']=='execute')['instructions']
        self.assertEqual([i['operand'] for i in body if i['offset'] in (3,4)],[1,15])
        delayed=next(m for m in w['methods'] if m['name']=='lambda$execute$0')['instructions']
        self.assertTrue(any(i['operand']==6.0 for i in delayed));self.assertTrue(any('ExplosionInteraction.TNT' in str(i['operand']) for i in delayed))
        self.assertFalse(any('ConfigurationSettings' in str(i['operand']) or '.getBlockState(' in str(i['operand']) for i in delayed))
        self.assertEqual(next(i for i in delayed if i['offset']==23)['opcode'],'0x1')

    def test_vortex_collision_helpers_are_exact_identical_and_overlapping(self):
        hit=self.method('VortexBlastProjectileHitsLivingEntityProcedure','execute')
        block=self.method('VortexBlockProcedure','execute')
        self.assertEqual(hit['code_sha256'],block['code_sha256']);self.assertEqual(hit['instructions'],block['instructions'])
        body=hit['instructions'];profiles=[]
        for n,i in enumerate(body):
            if 'MobEffectInstance.<init>' in str(i['operand']):profiles.append([x['operand'] for x in body[n-2:n]])
        self.assertEqual(profiles,[[120,0],[60,0]])
        self.assertFalse(any('.hurt(' in str(i['operand']) or '.explode(' in str(i['operand']) for i in body))
        row=next(r for r in self.batch['effects'] if r['id']=='arphex:vortex_arrow_intrinsic_native_control')
        cs=[c for c in row['scalable_parameter_candidates'] if c['parameters'][0].startswith('collision_')]
        self.assertEqual(len(cs),4);self.assertTrue(all(len(c['additional_consumer_sites'])==1 for c in cs))

    def test_vortex_last_motion_copies_owner_after_status_and_hurt(self):
        body=self.method('VortexBlastWhileProjectileFlyingTickProcedure','execute')['instructions'];by={i['offset']:i for i in body}
        self.assertIn('MobEffectInstance.<init>',by[665]['operand']);self.assertIn('.hurt(',by[827]['operand'])
        self.assertIn('.makeStuckInBlock(',by[855]['operand']);self.assertIn('.setDeltaMovement(',by[977]['operand'])
        self.assertEqual(by[925]['operand'],.8)
        for off in (940,952,964):
            at=next(n for n,i in enumerate(body) if i['offset']==off)
            self.assertEqual(body[at-1].get('local_index'),7) # OWNER motion, not projectile
        self.assertFalse(any('.setBlock(' in str(i['operand']) or '.explode(' in str(i['operand']) for i in body))

    def test_void_spear_homing_is_in_native_gravity_enabled_branch(self):
        body=self.method('VoidSpearWhileProjectileFlyingTickProcedure','execute')['instructions'];by={i['offset']:i for i in body}
        ng=next(n for n,i in enumerate(body) if '.isNoGravity(' in str(i['operand']))
        self.assertEqual(body[ng+1]['opcode'],'0x99');self.assertEqual(body[ng+1]['branch_target'],273)
        self.assertIn('.teleportTo(',by[309]['operand']);self.assertIn('.setDeltaMovement(',by[723]['operand'])
        self.assertTrue(any('Mob.getTarget(' in str(i['operand']) for i in body))
        self.assertEqual(by[1294]['operand'],150);self.assertEqual(by[1297]['operand'],300)
        hit=self.method('VoidSpearProjectileHitsLivingEntityProcedure','execute')['instructions']
        self.assertTrue(any(i['operand']=='net/arphex/entity/TormentorVoidlasherSummonEntity' for i in hit)) # recipient instance test

    def test_owned_handoff_rejects_changed_callee_hash(self):
        import copy
        b=copy.deepcopy(self.batch);c=next(c for r in b['effects'] for c in r['scalable_parameter_candidates'] if 'native_callee_binding' in c)
        c['native_callee_binding']['code_sha256']='0'*64
        review=read_json(OUT/'mod-reviews/arphex.json');ids={r['id'] for r in b['effects']}
        review['effects']=[r for r in review['effects'] if r['id'] not in ids];review['paths']=[p for p in review['paths'] if not set(p['effect_ids'])&ids]
        with self.assertRaises(AssertionError):validate_batch(b,review,self.census)

    def test_static_generated_defaults_are_uncalled_and_sphere_refinement_bound(self):
        for entry in self.batch['intrinsic_closed_entries']:
            prefix=entry[:-6]+'.shoot('
            self.assertFalse(any(prefix in i['operand'] for m in self.census['methods'] if m['entry']!=entry for i in decode_sites(self.census,m,'calls')))
        change=self.batch['record_refinements'][0];self.assertEqual(len(change['candidate_additions']),1)
        c=change['candidate_additions'][0];self.assertEqual(c['native_consumer']['offset'],248)
        self.assertEqual(c['primitive'],'NATIVE_AREA_SIZE')
        m=self.method('ChronoShotProjectileHitsLivingEntityProcedure','lambda$execute$3')
        body=m['instructions'];at=next(n for n,i in enumerate(body) if i['offset']==248)
        self.assertEqual(body[at-2]['operand'],50)


if __name__=='__main__':unittest.main()



