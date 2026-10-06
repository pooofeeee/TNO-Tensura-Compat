"""Check incoming/critical claims against independent pinned instruction facts."""
from copy import deepcopy
import unittest

from catalog_common import OUT,read_json
from promote_combat_batch import validate_batch,damage_source_binding


class IncomingContractsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch=read_json(OUT/'arphex-r2m2d-incoming-critical.json')
        cls.native=read_json(OUT/'native-evidence/arphex-global-hooks.json')
        cls.census=read_json(OUT/'arphex-combat-census.json')

    def body(self,name):
        witness=next(w for w in self.native['witnesses'] if w['entry'].endswith('/'+name+'.class'))
        return next(m['instructions'] for m in witness['methods']
                    if m['name']=='execute' and 'Lnet/neoforged/bus/api/Event;' in m['descriptor'])

    def window(self,name,offset,before=8):
        body=self.body(name);at=next(n for n,i in enumerate(body) if i['offset']==offset)
        return body[max(0,at-before):at+2]

    def test_reentrant_limit_keeps_original_source_and_ignores_hurt_return(self):
        body=self.body('EntityHurtWithoutSourceProcedure')
        self.assertTrue(any('DamageSource.getEntity()' in str(i['operand']) for i in body))
        self.assertFalse(any('DamageSource.getDirectEntity()' in str(i['operand']) for i in body))
        window=self.window('EntityHurtWithoutSourceProcedure',485)
        self.assertEqual(window[-3]['operand'],20.0)
        self.assertEqual(window[-1]['opcode'],'0x57') # ignored boolean, not a success gate
        self.assertNotIn('DamageSource.<init>',str(window))
        # The bytecode's aload operand is omitted by the decoded witness; verify
        # local 8 source load independently against the pinned class bytes.
        from classfile import ClassFile
        import zipfile
        from pathlib import Path
        jar=Path('/workspace/.cache/large-mod-campaign/ArPhEx-5.0.2-neoforge-1.21.1.jar')
        with zipfile.ZipFile(jar) as z:
            data=z.read('net/arphex/procedures/EntityHurtWithoutSourceProcedure.class')
        import hashlib
        witness=next(w for w in self.native['witnesses'] if w['entry'].endswith('/EntityHurtWithoutSourceProcedure.class'))
        self.assertEqual(hashlib.sha256(data).hexdigest(),witness['entry_sha256'])
        parsed=ClassFile(data)
        method=next(m for m in parsed.methods if m['name']=='execute' and 'Lnet/neoforged/bus/api/Event;' in m['descriptor'])
        self.assertEqual(method['code'][479:483],bytes([0x19,9,0x19,8]))

    def test_segment_request_is_zero_and_holder_only(self):
        window=self.window('EntityHurtWithoutSourceProcedure',1321)
        self.assertEqual(window[-3]['operand'],0.0)
        self.assertIn('DamageSource.<init>(Lnet/minecraft/core/Holder;)V',str(window))
        self.assertEqual(window[-1]['opcode'],'0x57')

    def test_direct_identity_and_holder_only_constructor_are_locked_native_facts(self):
        doc=read_json(OUT/'reference-evidence/bossesrise-sandworm-244.json')
        w=next(w for w in doc['witnesses'] if w['entry'].endswith('/DamageSource.class'))
        body=next(m['instructions'] for m in w['methods'] if m['name']=='isDirect')
        fields=[i['operand'] for i in body if i['opcode']=='0xb4']
        self.assertEqual(fields,['net/minecraft/world/damagesource/DamageSource.causingEntityLnet/minecraft/world/entity/Entity;',
                                 'net/minecraft/world/damagesource/DamageSource.directEntityLnet/minecraft/world/entity/Entity;'])
        self.assertEqual(body[4]['opcode'],'0xa6') # identity comparison
        doc=read_json(OUT/'reference-evidence/twilight-equipment-244.json')
        w=next(w for w in doc['witnesses'] if w['entry'].endswith('/DamageSource.class'))
        ctor=next(m for m in w['methods'] if m['name']=='<init>' and m['descriptor']=='(Lnet/minecraft/core/Holder;)V')
        self.assertEqual(ctor['code_hex'],'2a2b010101b70029b1') # null direct, causing and position

    def test_raw_health_and_current_amount_modifiers_are_distinct(self):
        health=self.window('SpiderShieldProcedure',291)
        self.assertEqual(health[-4]['operand'],25.0)
        self.assertEqual(health[-2]['opcode'],'0xb6')
        for offset,factor in [(1058,.9),(1378,.8),(1862,.6),(2110,2.0)]:
            window=self.window('SpiderShieldProcedure',offset)
            self.assertIn('LivingIncomingDamageEvent.getAmount()F',str(window))
            self.assertIn(factor,[i['operand'] for i in window])
            self.assertIn('LivingIncomingDamageEvent.setAmount(F)V',str(window))
        row=next(r for r in self.batch['effects'] if r['id']=='arphex:sourceful_incoming_shield_response')
        component=next(c for c in row['components'] if c['primitive']=='NATIVE_DAMAGE_MODIFIER')
        self.assertEqual(component['numerical_parameters']['inherent_power_factor'],
                         self.window('SpiderShieldProcedure',2110)[-4]['operand'])

    def test_native_critical_gate_status_holders_and_no_damage_or_clamp(self):
        w=next(w for w in self.native['witnesses'] if w['entry'].endswith('/CriticalHitProcedure.class'))
        root=next(m['instructions'] for m in w['methods'] if m['name']=='onPlayerCriticalHit')
        self.assertIn('CriticalHitEvent.isVanillaCritical()Z',str(root))
        self.assertNotIn('CriticalHitEvent.isCritical()',str(root))
        body=self.body('CriticalHitProcedure')
        self.assertNotIn('.hurt(',str(body));self.assertNotIn('Math.min(',str(body));self.assertNotIn('Math.max(',str(body))
        self.assertEqual([i['operand'] for i in self.window('CriticalHitProcedure',117)[-6:-2]],[8,4,0,0])
        self.assertEqual([i['operand'] for i in self.window('CriticalHitProcedure',164)[-6:-2]],[10,5,0,0])
        movement=[i for i in body if 'Entity.setDeltaMovement(' in str(i['operand'])]
        self.assertEqual(len(movement),9) # direct target + four branches in each radius profile
        self.assertEqual([i['operand'] for i in body if i['offset'] in (477,1265)],[10.0,5.0])

    def test_lifesteal_named_helper_has_no_heal_and_native_item_cooldown(self):
        body=self.body('Lifesteal2Procedure')
        self.assertNotIn('.heal(',str(body));self.assertNotIn('.setHealth(',str(body))
        self.assertEqual(self.window('Lifesteal2Procedure',4540)[-3]['operand'],2)
        w=next(w for w in self.native['witnesses'] if w['entry'].endswith('/Lifesteal2Procedure.class'))
        root=next(m['instructions'] for m in w['methods'] if m['name']=='onEntityAttacked')
        self.assertIn('DamageSource.getDirectEntity()',str(root));self.assertIn('DamageSource.getEntity()',str(root))

    def test_real_consumer_mapping_and_wrong_amount_consumer_rejection(self):
        review=deepcopy(read_json(OUT/'mod-reviews/arphex.json'))
        ids={r['id'] for r in self.batch['effects']};paths={p['id'] for p in self.batch['paths']}
        review['effects']=[r for r in review['effects'] if r['id'] not in ids]
        review['paths']=[p for p in review['paths'] if p['id'] not in paths]
        validate_batch(self.batch,review,self.census)
        bad=deepcopy(self.batch)
        row=next(r for r in bad['effects'] if r['id']=='arphex:sourceful_incoming_shield_response')
        row['scalable_parameter_candidates'][0]['native_consumer']['offset']=1058
        with self.assertRaisesRegex(AssertionError,'identity differs from consumer'):
            validate_batch(bad,review,self.census)


class SharedIncomingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch=read_json(OUT/'arphex-r2m2e-shared-incoming-transfer.json')
        cls.native=read_json(OUT/'native-evidence/arphex-global-hooks.json')
        cls.witness=next(w for w in cls.native['witnesses'] if w['entry'].endswith('/DwellerLifestealProcedure.class'))
        cls.transfer=read_json(OUT/'native-evidence/arphex-transfer-readers.json')

    def method(self,name='execute'):
        return next(m for m in self.witness['methods'] if m['name']==name and
                    (name!='execute' or 'Lnet/neoforged/bus/api/Event;' in m['descriptor']))

    def row(self,name):
        return next(r for r in self.batch['effects'] if r['id']=='arphex:'+name)

    def test_custom_marker_preserves_distinct_actor_presence_admission(self):
        body=self.method()['instructions']
        gate=[i for i in body if 23600<=i['offset']<=23625]
        self.assertIn('INVINCIBILITY_TEMP',str(gate))
        self.assertIn('LivingEntity.hasEffect(',str(gate))
        self.assertEqual(gate[-1]['operand'],'net/neoforged/bus/api/ICancellableEvent.setCanceled(Z)V')
        self.assertFalse(any(i['opcode']=='0x18' for i in gate)) # no amount threshold
        marker=next(r for r in read_json(OUT/'mod-reviews/arphex.json')['effects'] if r['id']=='arphex:invincibility_temp')
        self.assertEqual(marker['primary_classification'],'CUSTOM_STATUS')
        self.assertEqual(marker['scalable_parameter_candidates'],[])
        self.assertTrue(marker['binary_parameters']['null_direct_with_nonnull_causing_not_covered_by_these_two_readers'])

    def test_config_native_default_beats_stale_comment(self):
        w=next(w for w in self.native['witnesses'] if w['entry'].endswith('/ConfigurationSettingsConfiguration.class'))
        body=w['methods'][0]['instructions'];at=next(n for n,i in enumerate(body) if 'TORMENTOR_HIT_SPEED' in str(i['operand']))
        self.assertIn('default 25 ticks',body[at-6]['operand'])
        self.assertEqual(body[at-3]['operand'],20.0)
        c=next(c for c in self.row('tormentor_incoming_map_transaction')['components'] if c['primitive']=='NATIVE_ADMISSION_STATE')
        self.assertEqual(c['numerical_parameters']['damage_speed_default_ticks'],body[at-3]['operand'])

    def test_execution_keeps_two_source_types_and_all_retries(self):
        row=self.row('infinite_torment_native_execution')
        damage=[c for c in row['scalable_parameter_candidates'] if c['primitive']=='NATIVE_DAMAGE_REQUEST']
        self.assertEqual(len(damage),2)
        self.assertIn('DamageTypes.MAGIC',damage[0]['native_damage_type_symbol'])
        self.assertIn('DamageTypes.GENERIC',damage[1]['native_damage_type_symbol'])
        for c in damage:
            consumer=c['native_consumer'];method=self.method(consumer['methods'][0]);body=method['instructions']
            at=next(n for n,i in enumerate(body) if i['offset']==consumer['offset'])
            self.assertEqual(body[at-2]['operand'],100.0)
            self.assertEqual(body[at+1]['opcode'],'0x57')
            self.assertEqual(len(c['additional_consumer_sites']),3)
            for site in c['additional_consumer_sites']:
                binding=damage_source_binding(self.method(site['method']),site['offset'])
                self.assertEqual(binding[0],c['native_damage_type_symbol'])
                self.assertEqual(binding[3],c['native_damage_source_constructor'])
        self.assertEqual(len([c for c in row['scalable_parameter_candidates'] if c['primitive']=='DELAYED_DELIVERY']),4)

    def test_anonymous_summon_formula_and_attributed_followup_stay_distinct(self):
        row=self.row('tormentor_summon_incoming_attack_replacement')
        damage=[c for c in row['scalable_parameter_candidates'] if c['primitive']=='NATIVE_DAMAGE_REQUEST']
        self.assertEqual(damage[0]['native_damage_source_constructor'],
                         'net/minecraft/world/damagesource/DamageSource.<init>(Lnet/minecraft/core/Holder;)V')
        self.assertEqual(damage[1]['native_damage_source_constructor'],
                         'net/minecraft/world/damagesource/DamageSource.<init>(Lnet/minecraft/core/Holder;Lnet/minecraft/world/entity/Entity;)V')
        body=self.method()['instructions'];at=next(n for n,i in enumerate(body) if i['offset']==4233)
        self.assertIn('Math.round(F)I',str(body[at-6:at]))
        self.assertEqual(body[at+1]['opcode'],'0x57')

    def test_transfer_rounding_and_reset_are_native_not_independent_damage(self):
        body=self.method()['instructions']
        self.assertEqual(next(i['operand'] for i in body if i['offset']==35471),'java/lang/Math.round(D)J')
        self.assertEqual(self.row('arthropleura_segment_damage_transfer')['scalable_parameter_candidates'],[])
        w=next(w for w in self.transfer['witnesses'] if w['entry'].endswith('/SegmentedBodyOnEntityTickUpdateProcedure.class'))
        body=next(m['instructions'] for m in w['methods'] if m['name']=='execute')
        for offset,name in [(3708,'segdamagetransfer'),(3720,'segupwardstransfer')]:
            at=next(n for n,i in enumerate(body) if i['offset']==offset)
            self.assertEqual(body[at-2]['operand'],name)
            self.assertEqual(body[at-1]['operand'],0.0)
        at=next(n for n,i in enumerate(body) if i['offset']==1395)
        self.assertIn('DamageTypes.MOB_ATTACK',str(body[at-15:at]))
        self.assertIn('DamageSource.<init>(Lnet/minecraft/core/Holder;)V',str(body[at-15:at]))
        resource=next(w for w in self.transfer['witnesses'] if w['entry']=='data/arphex/damage_type/segment.json')
        self.assertEqual(resource['data'],{'exhaustion':.1,'message_id':'segment','scaling':'never'})

    def test_tame_gate_compares_victim_and_source_despite_wrong_decompiler_name(self):
        # Decoded local-variable operands are not inferred from names. Read only
        # this already-selected class and check its native operand bytes.
        import hashlib,zipfile
        from classfile import ClassFile
        with zipfile.ZipFile('/workspace/.cache/large-mod-campaign/ArPhEx-5.0.2-neoforge-1.21.1.jar') as jar:
            data=jar.read(self.witness['entry'])
        self.assertEqual(hashlib.sha256(data).hexdigest(),self.witness['entry_sha256'])
        parsed=ClassFile(data)
        method=next(m for m in parsed.methods if m['name']=='execute' and 'Lnet/neoforged/bus/api/Event;' in m['descriptor'])
        code=method['code']
        self.assertEqual(code[35807:35809],bytes([0x19,9]))
        self.assertEqual(code[35831:35833],bytes([0x19,11]))
        self.assertEqual(code[35855],0xa6)
        self.assertTrue(self.row('arthropleura_segment_damage_transfer')['binary_parameters']['same_native_owner_required'])

    def test_source_healing_recipients_use_native_causing_local(self):
        body={i['offset']:i for i in self.method()['instructions']}
        # Casts bind causing entity local11 to separate LivingEntity temporaries;
        # later addEffect operates on those same temporaries.
        for before,store,load in [(1690,1695,1708),(7615,7620,7633)]:
            self.assertEqual(body[before]['local_index'],11)
            self.assertEqual(body[store]['local_index'],body[load]['local_index'])

    def test_exact_transfer_callers_and_visual_only_ward_lightning(self):
        for actor,procedure in [('ArthropleuraAbominationEntity','SegmentedHeadOnEntityTickUpdateProcedure'),('SegmentedBodyEntity','SegmentedBodyOnEntityTickUpdateProcedure')]:
            w=next(w for w in self.transfer['witnesses'] if w['entry'].endswith('/'+actor+'.class'))
            body=w['methods'][0]['instructions']
            self.assertTrue(any(i['offset']==21 and procedure+'.execute(' in str(i['operand']) for i in body))
        body=self.method()['instructions']
        calls=[i for i in body if 'LightningBolt.setVisualOnly(Z)' in str(i['operand'])]
        self.assertEqual(len(calls),3)
        for i in calls:
            at=body.index(i);self.assertEqual(body[at-1]['operand'],1)
        self.assertTrue(self.row('spider_moth_incoming_feedback')['binary_parameters']['lightning_is_visual_only'])

    def test_batch_and_source_profile_mutation_rejection(self):
        review=deepcopy(read_json(OUT/'mod-reviews/arphex.json'))
        ids={r['id'] for r in self.batch['effects']};paths={p['id'] for p in self.batch['paths']}
        review['effects']=[r for r in review['effects'] if r['id'] not in ids]
        review['paths']=[p for p in review['paths'] if p['id'] not in paths]
        census=read_json(OUT/'arphex-combat-census.json')
        validate_batch(self.batch,review,census)
        bad=deepcopy(self.batch)
        row=next(r for r in bad['effects'] if r['id']=='arphex:infinite_torment_native_execution')
        # The same hurt API is not enough: replace a MAGIC retry by GENERIC.
        row['scalable_parameter_candidates'][0]['additional_consumer_sites'][0]['offset']=114
        with self.assertRaisesRegex(AssertionError,'auxiliary source identity differs'):
            validate_batch(bad,review,census)

        bad=deepcopy(self.batch)
        row=next(r for r in bad['effects'] if r['id']=='arphex:arthropleura_segment_damage_transfer')
        # An existing class witness must not masquerade as damage-type data.
        row['native_resource_evidence']=[dict(evidence_file='native-evidence/arphex-transfer-readers.json',
            witness_id='arphex-transfer-caller-SegmentedBodyEntity',entry='net/arphex/entity/SegmentedBodyEntity.class')]
        with self.assertRaisesRegex(AssertionError,'not a native JSON resource'):
            validate_batch(bad,review,census)


if __name__=='__main__':unittest.main()
