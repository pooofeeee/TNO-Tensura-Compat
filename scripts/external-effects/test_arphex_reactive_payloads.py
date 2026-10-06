"""Check native arrow/order/actor facts separately from curated batch claims."""
import unittest
from copy import deepcopy

from catalog_common import OUT, read_json
from promote_combat_batch import validate_batch


class ReactivePayloadTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch=read_json(OUT/'arphex-r2m2g-reactive-arrow-control.json')
        cls.global_native=read_json(OUT/'native-evidence/arphex-global-hooks.json')
        cls.reactive=read_json(OUT/'native-evidence/arphex-reactive-payloads.json')
        cls.census=read_json(OUT/'arphex-combat-census.json')

    def method(self,name,method='execute',reactive=False):
        doc=self.reactive if reactive else self.global_native
        witness=next(w for w in doc['witnesses'] if w['entry'].endswith('/'+name+'.class'))
        return next(m for m in witness['methods'] if m['name']==method and
                    (name!='DwellerLifestealProcedure' or method!='execute' or 'Lnet/neoforged/bus/api/Event;' in m['descriptor']))

    def base(self):
        review=deepcopy(read_json(OUT/'mod-reviews/arphex.json'))
        ids={r['id'] for r in self.batch['effects']}
        review['effects']=[r for r in review['effects'] if r['id'] not in ids]
        review['paths']=[p for p in review['paths'] if not set(p['effect_ids'])&ids]
        return review

    def test_batch_consumers_and_cross_class_proofs_fail_closed(self):
        validate_batch(self.batch,self.base(),self.census)
        bad=deepcopy(self.batch)
        site=next(c for r in bad['effects'] for c in r['scalable_parameter_candidates']
                  if c['primitive']=='PROJECTILE_DAMAGE')['additional_consumer_sites'][0]
        site['witness_id']='arphex-global-DwellerLifestealProcedure$13'
        with self.assertRaisesRegex(AssertionError,'wrong witness ID'):
            validate_batch(bad,self.base(),self.census)
        del site['witness_id']
        with self.assertRaisesRegex(AssertionError,'cross-class site lacks its own proof'):
            validate_batch(bad,self.base(),self.census)

    def test_parent_hit_returns_before_unconditional_owner_payload(self):
        body=self.method('BloodthirstyTendrilEntity','onHitEntity',True)['instructions']
        self.assertEqual(body[2]['offset'],2)
        self.assertIn('AbstractArrow.onHitEntity(',body[2]['operand'])
        self.assertIn('BloodthirstyTendrilEntity.getOwner()',next(i['operand'] for i in body if i['offset']==26))
        self.assertIn('TendrilHitsProcedure.execute(',next(i['operand'] for i in body if i['offset']==29))
        self.assertFalse(any('branch_target' in i for i in body))
        self.assertFalse(any('.hurt(' in str(i['operand']) for i in body))

    def test_owner_drives_motion_but_distinct_hit_entity_is_recipient(self):
        body=self.method('TendrilHitsProcedure',reactive=True)['instructions'];by={i['offset']:i for i in body}
        self.assertEqual([by[o]['local_index'] for o in [0,5,14,16,21,27,51,72]],[7,8,8,7,7,8,8,8])
        self.assertEqual(by[18]['opcode'],'0xa5') # owner==victim skips custom payload
        self.assertEqual(by[95]['operand'],'net/minecraft/world/entity/Entity.setDeltaMovement(Lnet/minecraft/world/phys/Vec3;)V')
        prefix=[i for i in body if i['offset']<=95]
        self.assertFalse(any('KNOCKBACK_RESISTANCE' in str(i['operand']) or '.hurt(' in str(i['operand']) for i in prefix))
        self.assertIn(.5,[i['operand'] for i in prefix]);self.assertIn(1.5,[i['operand'] for i in prefix])
        self.assertEqual(by[271]['operand'],'effect give @e[type=arphex:scorpioid_bloodluster, distance=..20] regeneration 2 4')
        self.assertNotIn('owner=',by[271]['operand'])

    def test_retaliation_captures_victim_and_sets_three_arrow_profiles(self):
        root=self.method('DwellerLifestealProcedure')['instructions']
        outer=[i for i in root if 16770<=i['offset']<=16793]
        self.assertEqual(outer[-3]['local_index'],9) # incoming victim captured by outer queue
        second=self.method('DwellerLifestealProcedure','lambda$execute$62')['instructions']
        self.assertEqual(second[-5]['operand'],10)
        self.assertEqual(second[-4]['local_index'],7) # same captured victim into inner queue
        body=self.method('DwellerLifestealProcedure','lambda$execute$61')['instructions']
        calls=[i for i in body if '.getArrow(' in str(i['operand'])]
        self.assertEqual(len(calls),3)
        self.assertEqual([i['offset'] for i in body if '.shoot(' in str(i['operand'])],[97,203,309])
        for call in calls:
            at=body.index(call)
            self.assertEqual([i['operand'] for i in body[at-7:at]],
                             ['java/lang/Double.doubleValue()D','java/lang/Math.round(D)J',5,None,None,2,2])
            self.assertEqual(body[at-11]['opcode'],'0x2a') # captured victim passed as shooter
        for n in [13,14,15]:
            arrow=self.method(f'DwellerLifestealProcedure${n}','getArrow')['instructions']
            at=next(j for j,i in enumerate(arrow) if '.setOwner(' in str(i['operand']))
            self.assertEqual(arrow[at-1]['opcode'],'0x2c') # getArrow shooter argument
            self.assertTrue(any(i['operand']==100.0 for i in arrow))

    def test_native_config_comment_is_not_a_runtime_bound(self):
        body=self.method('ConfigurationSettingsConfiguration','<clinit>')['instructions']
        at=next(n for n,i in enumerate(body) if i['opcode']=='0xb3' and 'OVERALL_DIFFICULTY' in str(i['operand']))
        self.assertEqual(body[at-3]['operand'],0.0)
        self.assertIn('ModConfigSpec$Builder.define(',body[at-1]['operand'])
        self.assertNotIn('defineInRange',body[at-1]['operand'])
        self.assertIn('upper limit is 256',body[at-6]['operand'])

    def test_source_thunder_gate_still_writes_victim_clock(self):
        body=self.method('DwellerLifestealProcedure')['instructions']
        for offset in [17168,17195]:
            at=next(n for n,i in enumerate(body) if i['offset']==offset)
            prefix=body[:at]
            target=next(n for n in range(len(prefix)-1,-1,-1) if 'Entity.getPersistentData()' in str(prefix[n]['operand']))
            self.assertEqual(prefix[target-1]['local_index'],9)
        by={i['offset']:i for i in body}
        self.assertEqual(by[16455]['operand'],1)
        self.assertEqual(by[16456]['opcode'],'0x60') # integer amplifier+1
        self.assertEqual(by[17017]['operand'],5)
        self.assertEqual(by[17031]['operand'],20)

    def test_native_lifecycle_discards_on_ground_and_flying_helper_is_particles_only(self):
        body=self.method('BloodthirstyTendrilEntity','tick',True)['instructions']
        self.assertIn('AbstractArrow.tick()',body[1]['operand'])
        self.assertIn('.inGroundZ',next(i['operand'] for i in body if i['offset']==24))
        self.assertIn('.discard()',next(i['operand'] for i in body if i['offset']==31))
        self.assertFalse(any('isClientSide' in str(i['operand']) for i in body))
        flying=self.method('BloodthirstyTendrilWhileProjectileFlyingTickProcedure',reactive=True)['instructions']
        self.assertEqual(len(flying),21)
        self.assertEqual(sum('sendParticles(' in str(i['operand']) for i in flying),1)
        self.assertFalse(any(k in str(i['operand']) for i in flying for k in ['.hurt(','.addEffect(','.setDeltaMovement(','.discard(']))

    def test_teleport_reuses_current_stored_coordinates_and_burn_is_seconds(self):
        body=self.method('DwellerLifestealProcedure','lambda$execute$63')['instructions']
        self.assertEqual(sum('isEmptyBlock(' in str(i['operand']) for i in body),2)
        self.assertEqual([i['offset'] for i in body if '.teleport' in str(i['operand'])],[127,192])
        self.assertFalse(any('getMainHandItem(' in str(i['operand']) or 'hasEffect(' in str(i['operand']) or 'getMaxHealth(' in str(i['operand']) for i in body))
        root=self.method('DwellerLifestealProcedure')['instructions'];by={i['offset']:i for i in root}
        self.assertEqual(by[17334]['local_index'],9)
        self.assertEqual(by[17336]['operand'],5.0)
        self.assertIn('igniteForSeconds(F)',by[17339]['operand'])


if __name__=='__main__':
    unittest.main()
