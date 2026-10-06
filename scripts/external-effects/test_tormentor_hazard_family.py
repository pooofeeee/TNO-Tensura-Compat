"""Independent native invariants for the seven Tormentor hazard carriers."""
import copy
import unittest

from catalog_common import OUT, read_json
from promote_combat_batch import validate_batch, concat_command_binding


class TormentorHazardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch=read_json(OUT/'arphex-r2m5a-tormentor-native-hazard-carriers.json')
        cls.native=read_json(OUT/'native-evidence/arphex-tormentor-hazard-family.json')
        cls.census=read_json(OUT/'arphex-combat-census.json')

    def method(self, n, name='execute'):
        return next(m for w in self.native['witnesses'] if w['entry'].endswith('/'+n+'.class')
                    for m in w['methods'] if m['name']==name)

    def prior(self):
        review=copy.deepcopy(read_json(OUT/'mod-reviews/arphex.json'))
        ids={r['id'] for r in self.batch['effects']}
        review['effects']=[r for r in review['effects'] if r['id'] not in ids]
        review['paths']=[p for p in review['paths'] if not set(p['effect_ids'])&ids]
        return review

    def test_seven_carriers_and_unique_native_scalar_bindings(self):
        result=validate_batch(self.batch,self.prior(),self.census)
        self.assertEqual(result['semantic_records'],len(self.prior()['effects'])+7)
        self.assertEqual(len(self.batch['closed_actor_callback_entries']),7)
        self.assertEqual(sum(len(c['parameters']) for r in self.batch['effects'] for c in r['scalable_parameter_candidates']),81)
        self.assertFalse(self.batch['whole_mod_complete'])
        self.assertTrue(self.batch['pending_shared_contexts'])

    def test_small_sphere_integer_request_preserves_status_damage_explosion_order(self):
        by={i['offset']:i for i in self.method('SmallTormentSphereOnEntityTickUpdateProcedure')['instructions']}
        for a,b,c in [(803,804,805),(1683,1684,1685)]:
            self.assertEqual([by[o]['opcode'] for o in [a,b,c]],['0x6c','0x6c','0x86'])
        for status,hurt,explosion,stuck in [(600,806,910,938),(1513,1686,1780,1808)]:
            self.assertLess(status,hurt);self.assertLess(hurt,explosion);self.assertLess(explosion,stuck)
        body=self.method('SmallTormentSphereOnEntityTickUpdateProcedure')['instructions']
        for j,i in enumerate(body):
            if '.hurt(' in str(i['operand']):self.assertEqual(body[j+1]['opcode'],'0x57')
        # No new break/return after the in-loop native discard.
        for j,i in enumerate(body):
            if '.discard(' in str(i['operand']) and 900<i['offset']<1830:
                self.assertNotEqual(body[j+1]['opcode'],'0xb1')

    def test_shield_hurt_return_does_not_gate_absolute_motion(self):
        b=self.method('TormentorShieldTickProcedure')['instructions'];by={i['offset']:i for i in b}
        at=next(j for j,i in enumerate(b) if i['offset']==845)
        self.assertEqual(b[at+1]['opcode'],'0x57')
        self.assertFalse(any(i['opcode'].startswith('0x9') for i in b[at+2:] if i['offset']<882))
        self.assertIn('.setDeltaMovement(',by[882]['operand'])
        self.assertIn('DamageTypes.MAGIC',next(c for r in self.batch['effects'] for c in r['scalable_parameter_candidates'] if c.get('native_consumer',{}).get('offset')==845)['native_damage_type_symbol'])

    def test_wave_current_amplifier_increment_and_independent_projectile_branch(self):
        b=self.method('TimeDistortionWaveOnEntityTickUpdateProcedure','lambda$execute$2')['instructions'];by={i['offset']:i for i in b}
        self.assertIn('getAmplifier(',by[198]['operand'])
        self.assertEqual((by[205]['operand'],by[206]['opcode'],by[207]['opcode']),(2,'0x60','0x86'))
        self.assertIn('Math.round(F)',by[208]['operand'])
        self.assertIn('.setDeltaMovement(',by[274]['operand'])
        self.assertFalse(any('.isAlive(' in str(i['operand']) or '.distanceTo' in str(i['operand']) for i in b))
        c=next(c for r in self.batch['effects'] for c in r['scalable_parameter_candidates'] if c.get('native_concat_command_binding',{}).get('template','').startswith('effect give @s arphex:time_freeze'))
        self.assertEqual(c['native_concat_command_binding']['template'],'effect give @s arphex:time_freeze 2 \x01')

    def test_laser_conditional_explosion_has_no_in_family_counter_writer(self):
        b=self.method('TormentLaserTickProcedure')['instructions']
        key=next(j for j,i in enumerate(b) if i['operand']=='looktoggle')
        self.assertIn('.getDouble(',b[key+1]['operand'])
        self.assertEqual(b[key+2]['operand'],20.0)
        self.assertEqual(sum(i['operand']=='looktoggle' for i in b),1)
        self.assertFalse(any('.hurt(' in str(i['operand']) for i in b))
        self.assertTrue(any(i['offset']==1966 and '.explode(' in str(i['operand']) for i in b))

    def test_native_dimensions_are_distinct_from_visual_grow_state(self):
        small=self.method('SmallTormentSphereEntity','getDefaultDimensions')['instructions']
        sphere=self.method('TormentorSphereEntity','getDefaultDimensions')['instructions']
        self.assertEqual((small[-3]['operand'],sphere[-3]['operand']),(2.0,1.0))
        shield=self.method('TormentorShieldEntity','getDefaultDimensions')['instructions']
        self.assertTrue(any('TormentorShieldHitboxScaleProcedure.execute(' in str(i['operand']) for i in shield))
        h=self.method('TormentorShieldHitboxScaleProcedure')['instructions']
        self.assertEqual(sum('DATA_growsize' in str(i['operand']) for i in h),2)
        self.assertEqual(h[-3]['operand'],3.0)

    def test_zero_after_increment_death_gate_is_not_normal_removal(self):
        for n in ['SmallTormentSphereEntity','TormentorShieldEntity','TormentorSphereEntity']:
            by={i['offset']:i for i in self.method(n,'tickDeath')['instructions']}
            self.assertEqual((by[5]['operand'],by[6]['opcode']),(1,'0x60'))
            self.assertEqual(by[14]['opcode'],'0x9a')  # IFNE after increment, not deathTime>=20

    def test_two_element_fireball_motion_has_native_zero_z(self):
        vanilla=read_json(OUT/'vanilla-evidence/arphex-tormentor-fireball-motion.json')['classes'][0]
        b=vanilla['methods'][0]['instructions']
        self.assertEqual(b[-2]['operand'],0.0)
        self.assertTrue(any('List.size()' in str(i['operand']) for i in b))
        n='TormentorSphereOnEntityTickUpdateProcedure'
        m=self.method(n,'lambda$execute$8')
        binding=concat_command_binding(m,111,self.census,'net/arphex/procedures/'+n+'.class')
        self.assertEqual(binding['template'],'summon fireball ~ ~ ~ {Motion:[0d,-10d],ExplosionPower:\x01}')

    def test_global_target_bridge_reuses_existing_native_callback(self):
        small=next(r for r in self.batch['effects'] if r['id']=='arphex:small_torment_sphere_native_carrier')
        cs=[c for c in small['scalable_parameter_candidates'] if c['primitive']=='NATIVE_TARGET_BRIDGE']
        self.assertEqual(len(cs),2)
        self.assertTrue(all(c['native_consumer']['evidence_file']=='native-evidence/arphex-global-hooks.json' for c in cs))
        self.assertEqual(len(cs[1]['additional_consumer_sites']),2)
        self.assertIn('arphex:torment_burn_native_reader',next(r for r in self.batch['effects'] if r['id']=='arphex:tormentor_sphere_native_carrier')['canonical_contract_reuse'])

    def test_foreign_source_and_recipient_bindings_are_rejected(self):
        changed=copy.deepcopy(self.batch)
        c=next(c for r in changed['effects'] for c in r['scalable_parameter_candidates'] if 'native_damage_type_symbol' in c)
        c['native_damage_type_symbol']='net/minecraft/world/damagesource/DamageTypes.GENERICLnet/minecraft/resources/ResourceKey;'
        with self.assertRaises(AssertionError):validate_batch(changed,self.prior(),self.census)
        changed=copy.deepcopy(self.batch)
        c=next(c for r in changed['effects'] for c in r['scalable_parameter_candidates'] if 'native_receiver_binding' in c)
        c['native_receiver_binding']['origin_local_index']=999
        with self.assertRaises(AssertionError):validate_batch(changed,self.prior(),self.census)


if __name__=='__main__':
    unittest.main()
