"""Nuclear contracts preserve independently captured native ordering and actors."""
import copy
import unittest

from assemble_authored_contracts import render
from catalog_common import OUT, read_json
from promote_combat_batch import validate_batch


def witness(name, scope='nuclear-actors'):
    return next(w for w in read_json(OUT/f'native-evidence/alexscaves-{scope}.json')['witnesses']
                if w['entry'].endswith('/'+name+'.class'))


def body(name, method, scope='nuclear-actors'):
    return next(m for m in witness(name, scope)['methods'] if m['name']==method)['instructions']


class NuclearContractsTests(unittest.TestCase):
    def test_regeneration_and_native_parameters(self):
        b=read_json(OUT/'alexscaves-r2m8l-nuclear-contracts.json')
        self.assertEqual(render(read_json(OUT/'native-findings/alexscaves-nuclear-contracts.json')), b)
        r=copy.deepcopy(read_json(OUT/'mod-reviews/alexscaves.json'))
        ids={e['id'] for e in b['effects']}
        r['effects']=[e for e in r['effects'] if e['id'] not in ids]
        r['paths']=[p for p in r['paths'] if not set(p['effect_ids'])&ids]
        self.assertEqual(validate_batch(b,r,read_json(OUT/'alexscaves-combat-census.json'))['semantic_records'],len(r['effects'])+12)
        self.assertEqual(sum(len(c['parameters']) for e in b['effects'] for c in e['scalable_parameter_candidates']),60)

    def test_spawn_does_not_invent_an_owner(self):
        for name, method in [('BrainiacEntity','tick'),('GammaroachEntity','tick'),('NucleeperEntity','explode')]:
            b=body(name,method)
            self.assertIn('addFreshEntity',str(b))
            self.assertNotIn('.setOwner(',str(b))
        for name in ('ThrownWasteDrumEntity','NuclearExplosionEntity'):
            w=witness(name,'nuclear-support')
            self.assertEqual(w['superclass'],'net/minecraft/world/entity/Entity')
            self.assertFalse({'getOwner','setOwner'} & {m['name'] for m in w['methods']})
            self.assertNotIn('.setOwner(',str(w['methods']))

    def test_tongue_status_precedes_damage_and_knockback_is_independent(self):
        b=body('BrainiacEntity','tick');at={i['offset']:i for i in b}
        self.assertIn('postAttackEffect',at[665]['operand'])
        self.assertIn('.hurt(',at[680]['operand'])
        self.assertEqual(at[683]['opcode'],'0x57')
        self.assertIn('knockback',at[706]['operand'])

    def test_tremorzilla_hurt_return_gates_status_and_velocity(self):
        b=body('TremorzillaEntity','hurtEntitiesAround');at={i['offset']:i for i in b}
        self.assertIn('.hurt(',at[237]['operand'])
        self.assertEqual((at[240]['opcode'],at[240]['branch_target']),('0x99',341))
        self.assertTrue(any('knockbackTarget' in str(i['operand']) for i in b if 243<=i['offset']<337))
        self.assertIn('.addEffect(',at[337]['operand'])
        for o in (42,56):
            n=next(n for n,i in enumerate(b) if i['offset']==o)
            self.assertIn('AABB.set',b[n]['operand'])
            self.assertEqual(b[n+1]['opcode'],'0x57')

    def test_custom_velocity_reads_actor_not_recipient(self):
        b=body('TremorzillaEntity','knockbackTarget')
        for token in ('TremorzillaEntity.getDeltaMovement','TremorzillaEntity.onGround','TremorzillaEntity.getAttributeValue'):
            n=next(n for n,i in enumerate(b) if token in str(i['operand']))
            if 'getAttributeValue' not in token:
                self.assertEqual(b[n-1].get('local_index'),0)
        self.assertNotIn('LivingEntity.knockback',str(b))
        self.assertIn('Entity.setDeltaMovement(DDD)',str(b))

    def test_nuclear_hurt_does_not_gate_velocity_or_status(self):
        b=body('NuclearExplosionEntity','tick','nuclear-support');at={i['offset']:i for i in b}
        self.assertIn('.hurt(',at[618]['operand'])
        self.assertEqual(at[621]['opcode'],'0x57')
        self.assertIn('setDeltaMovement',at[638]['operand'])
        self.assertIn('.addEffect(',at[682]['operand'])
        f=body('NuclearExplosionEntity','calculateDamage','nuclear-support')
        self.assertEqual([i['operand'] for i in f if i['opcode']=='0x13'],[1.5,100.0,100.0,1.5,400.0])

    def test_drums_and_cloud_do_not_gain_a_server_damage_guard(self):
        b=body('ThrownWasteDrumEntity','tick','nuclear-support')
        h=next(n for n,i in enumerate(b) if '.hurt(' in str(i['operand']))
        self.assertNotIn('isClientSide',str(b[:h]))
        c=body('GammaroachEntity','tick')
        s=next(n for n,i in enumerate(c) if '.addFreshEntity(' in str(i['operand']))
        self.assertNotIn('isClientSide',str(c[:s]))

    def test_unused_aquatic_speed_multiplier_is_not_applied(self):
        b=body('DirectAquaticMoveControl','tick','nuclear-extra')
        self.assertNotIn('.speedMulti',str(b))
        self.assertIn('.speedModifier',str(b))
        self.assertIn('.yawLimit',str(b))

    def test_wrong_native_candidate_literal_is_rejected(self):
        b=copy.deepcopy(read_json(OUT/'alexscaves-r2m8l-nuclear-contracts.json'))
        r=copy.deepcopy(read_json(OUT/'mod-reviews/alexscaves.json'));ids={e['id'] for e in b['effects']}
        r['effects']=[e for e in r['effects'] if e['id'] not in ids]
        r['paths']=[p for p in r['paths'] if not set(p['effect_ids'])&ids]
        c=next(c for e in b['effects'] for c in e['scalable_parameter_candidates'] if 'native_literal_call_argument_binding' in c)
        c['native_literal_call_argument_binding']['native_value']+=1
        with self.assertRaises(AssertionError):
            validate_batch(b,r,read_json(OUT/'alexscaves-combat-census.json'))


if __name__=='__main__':
    unittest.main()
