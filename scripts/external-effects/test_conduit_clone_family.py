"""Native source/type/order invariants for Conduit, Clone and SlowLook."""
import copy
import unittest

from catalog_common import OUT, read_json
from promote_combat_batch import validate_batch


class ConduitCloneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch=read_json(OUT/'arphex-r2m5b-conduit-clone-beam-callbacks.json')
        cls.native=read_json(OUT/'native-evidence/arphex-conduit-clone-hazard-family.json')
        cls.census=read_json(OUT/'arphex-combat-census.json')

    def method(self,n,name='execute'):
        return next(m for w in self.native['witnesses'] if w['entry'].endswith('/'+n+'.class')
                    for m in w['methods'] if m['name']==name)

    def prior(self):
        r=copy.deepcopy(read_json(OUT/'mod-reviews/arphex.json'))
        ids={x['id'] for x in self.batch['effects']}
        r['effects']=[x for x in r['effects'] if x['id'] not in ids]
        r['paths']=[p for p in r['paths'] if not set(p['effect_ids'])&ids]
        return r

    def test_three_callback_contracts_with_exact_scalar_bindings(self):
        result=validate_batch(self.batch,self.prior(),self.census)
        self.assertEqual(result['semantic_records'],len(self.prior()['effects'])+3)
        self.assertEqual(sum(len(c['parameters']) for r in self.batch['effects'] for c in r['scalable_parameter_candidates']),17)
        self.assertEqual((len(self.native['witnesses']),sum(len(w['methods']) for w in self.native['witnesses'])),(14,95))
        self.assertFalse(self.batch['whole_mod_complete'])

    def test_conduit_health_write_uses_current_health_plus_one_not_heal(self):
        b=self.method('EntropyConduitOnEntityTickUpdateProcedure')['instructions']
        at=next(j for j,i in enumerate(b) if i['offset']==1074)
        self.assertIn('.setHealth(',b[at]['operand'])
        self.assertEqual((b[at-2]['operand'],b[at-1]['opcode']),(1.0,'0x62'))
        self.assertFalse(any('.heal(' in str(i['operand']) for i in b))

    def test_conduit_death_supplies_causing_attacker_after_parent(self):
        b=self.method('EntropyConduitEntity','die')['instructions']
        self.assertIn('Monster.die(',b[2]['operand'])
        self.assertIn('DamageSource.getEntity()',next(i['operand'] for i in b if i['offset']==22))
        self.assertIn('EntropyConduitEntityDiesProcedure.execute(',next(i['operand'] for i in b if i['offset']==25))
        self.assertFalse(any('.getDirectEntity(' in str(i['operand']) for i in b))
        death=self.method('EntropyConduitEntityDiesProcedure')['instructions']
        self.assertTrue(any('.removeEffect(' in str(i['operand']) and i['offset']<317 for i in death))
        self.assertEqual(death[-2]['opcode'],'0x57')

    def test_always_true_is_collision_predicate_not_invulnerability(self):
        collision=self.method('EntropyConduitEntity','canBeCollidedWith')['instructions']
        self.assertTrue(any('AlwaysTrueProcedure.execute(' in str(i['operand']) for i in collision))
        w=next(w for w in self.native['witnesses'] if w['entry'].endswith('/EntropyConduitEntity.class'))
        self.assertNotIn('isInvulnerableTo',w['declared_method_names'])

    def test_clone_hurt_helper_type_guard_cannot_prime_sibling(self):
        w=next(w for w in self.native['witnesses'] if w['entry'].endswith('/DiabolosDecimatorCloneEntity.class'))
        self.assertEqual(w['superclass'],'net/minecraft/world/entity/monster/Monster')
        b=self.method('DiabolosDecimatorEntityIsHurtProcedure')['instructions']
        self.assertEqual(next(i['operand'] for i in b if i['opcode']=='0xc1'),'net/arphex/entity/DiabolosDecimatorEntity')
        self.assertEqual(next(i['branch_target'] for i in b if i['offset']==9),31)
        self.assertEqual(b[-1]['opcode'],'0xb1')

    def test_native_clone_goal_uses_strict_squared_distance_and_los(self):
        by={i['offset']:i for i in self.method('DiabolosDecimatorCloneEntity$1','canPerformAttack')['instructions']}
        self.assertEqual((by[15]['operand'],by[18]['opcode'],by[19]['opcode']),(81.0,'0x98','0x9c'))
        self.assertIn('.isTimeToAttack(',by[1]['operand'])
        self.assertIn('.hasLineOfSight(',by[30]['operand'])

    def test_wander_helper_requires_existing_target_not_target_absence(self):
        b=self.method('HasAttackTargetReturnProcedure')['instructions'];by={i['offset']:i for i in b}
        self.assertIn('.getTarget(',by[19]['operand'])
        self.assertEqual((by[26]['opcode'],by[26]['branch_target']),('0xc7',33))
        self.assertEqual((by[33]['operand'],by[34]['opcode']),(0,'0x9a'))
        self.assertEqual(by[37]['operand'],1)  # nonnull target returns true after native inversion
        for name in ['canUse','canContinueToUse']:
            body=self.method('DiabolosDecimatorCloneEntity$2',name)['instructions']
            self.assertTrue(any('HasAttackTargetReturnProcedure.execute(' in str(i['operand']) for i in body))

    def test_beam_source_is_original_boss_and_hurt_result_is_discarded(self):
        b=self.method('SlowLookTestOnEntityTickUpdateProcedure')['instructions'];by={i['offset']:i for i in b}
        self.assertEqual(by[2836]['local_index'],37)  # initial_lock, not nearest_clone local39
        self.assertIn('DamageTypes.MAGIC',by[2828]['operand'])
        at=next(j for j,i in enumerate(b) if i['offset']==2877)
        self.assertEqual(b[at+1]['opcode'],'0x57')
        source_stores=[j for j,i in enumerate(b) if i['opcode']=='0x3a' and i.get('local_index')==37]
        self.assertEqual(len(source_stores),2)  # null then native nearest-boss query result
        region=b[source_stores[0]+1:source_stores[1]]
        self.assertTrue(any(i['operand']=='net/arphex/entity/DiabolosDecimatorEntity' for i in region))
        self.assertFalse(any(i['operand']=='net/arphex/entity/DiabolosDecimatorCloneEntity' for i in region))
        self.assertFalse(any('.isAlive(' in str(i['operand']) for i in b))

    def test_native_damage_binding_cannot_be_replaced_with_anonymous_source(self):
        changed=copy.deepcopy(self.batch)
        row=next(r for r in changed['effects'] if r['id']=='arphex:diabolos_slow_look_native_beam')
        c=next(c for c in row['scalable_parameter_candidates'] if 'native_damage_source_constructor' in c)
        c['native_damage_source_constructor']='net/minecraft/world/damagesource/DamageSource.<init>(Lnet/minecraft/core/Holder;)V'
        with self.assertRaises(AssertionError):validate_batch(changed,self.prior(),self.census)


if __name__=='__main__':
    unittest.main()
