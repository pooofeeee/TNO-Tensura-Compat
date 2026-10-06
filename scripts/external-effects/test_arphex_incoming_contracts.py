"""Check incoming/critical claims against independent pinned instruction facts."""
from copy import deepcopy
import unittest

from catalog_common import OUT,read_json
from promote_combat_batch import validate_batch


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


if __name__=='__main__':unittest.main()
