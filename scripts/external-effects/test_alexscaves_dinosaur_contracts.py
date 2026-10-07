"""Source attribution, ordering, distinct primitives and native input regressions."""
import copy
import unittest
from catalog_common import OUT, read_json
from assemble_authored_contracts import render
from promote_combat_batch import validate_batch


def body(name, method, scope='dinosaur-actors'):
    p = read_json(OUT/f'native-evidence/alexscaves-{scope}.json')
    w = next(w for w in p['witnesses'] if w['entry'].endswith('/'+name+'.class'))
    return next(m for m in w['methods'] if m['name'] == method)['instructions']


class DinosaurContractsTests(unittest.TestCase):
    def test_native_batch_regenerates_and_parameters_do_not_duplicate(self):
        b = read_json(OUT/'alexscaves-r2m8j-dinosaur-contracts.json')
        self.assertEqual(render(read_json(OUT/'native-findings/alexscaves-dinosaur-contracts.json')), b)
        r = copy.deepcopy(read_json(OUT/'mod-reviews/alexscaves.json'))
        ids = {e['id'] for e in b['effects']}
        r['effects'] = [e for e in r['effects'] if e['id'] not in ids]
        r['paths'] = [e for e in r['paths'] if not set(e['effect_ids']) & ids]
        self.assertEqual(validate_batch(b, r, read_json(OUT/'alexscaves-combat-census.json'))['semantic_records'], len(r['effects'])+15)
        self.assertEqual(sum(len(c['parameters']) for e in b['effects'] for c in e['scalable_parameter_candidates']),42)

    def test_owner_hurt_uses_causing_entity_before_parent(self):
        b = body('DinosaurEntity','hurt')
        self.assertIn('DamageSource.getEntity()', str(b))
        self.assertNotIn('DamageSource.getDirectEntity()', str(b))
        self.assertEqual(b[-2]['opcode'], '0xb7')
        self.assertIn('TamableAnimal.hurt', b[-2]['operand'])
        self.assertEqual(b[-1]['opcode'],'0xac')
        self.assertIn('TamableAnimal.isOwnedBy',str(body('DinosaurEntity','isAlliedTo')))

    def test_sauropod_shield_precedes_damage_and_posteffects_require_success(self):
        b = body('SauropodBaseEntity','hurtEntitiesAround');at={i['offset']:i for i in b}
        self.assertIn('disableShield',at[173]['operand'])
        self.assertIn('.hurt(',at[181]['operand'])
        self.assertEqual(at[184]['opcode'],'0x99')
        self.assertEqual(at[184]['branch_target'],230)
        self.assertIn('igniteForSeconds',at[199]['operand'])
        self.assertIn('knockback',at[227]['operand'])
        self.assertIn('NO_CREATIVE_OR_SPECTATOR',str(b))
        self.assertIn('isAlliedTo',str(b))

    def test_native_bites_keep_independent_knockback(self):
        for name in ('GrottoceratopsMeleeGoal','RelicheirusMeleeGoal','TremorsaurusMeleeGoal'):
            b=body(name,'checkAndDealDamage','dinosaur-support')
            n=next(n for n,i in enumerate(b) if '.hurt(' in str(i['operand']))
            self.assertEqual(b[n+1]['opcode'],'0x57')
            self.assertTrue(any('.knockback(' in str(i['operand']) for i in b[n+2:]))

    def test_subterranodon_schedules_without_immediate_hurt(self):
        b=body('SubterranodonEntity','doHurtTarget')
        self.assertFalse(any('.hurt(' in str(i['operand']) for i in b))
        self.assertIn(7,[i['operand'] for i in b])
        self.assertEqual([i['opcode'] for i in b[-2:]],['0x4','0xac'])
        self.assertIn('.hurt(',str(body('SubterranodonEntity','tick')))

    def test_breath_begins_at_zero_not_one_and_keeps_terrain_separate(self):
        b=body('LuxtructosaurusEntity','burnWithBreath')
        self.assertEqual([i['operand'] for i in (b[0],b[2])],[0.0,1.0])
        self.assertIn('setBlockAndUpdate',str(b))
        self.assertNotIn('canEntityGrief',str(b))
        self.assertIn('hurtEntitiesAround',str(b))

    def test_relicheirus_transient_time_not_invented_as_nbt(self):
        p=read_json(OUT/'native-evidence/alexscaves-dinosaur-actors.json')
        w=next(w for w in p['witnesses'] if w['entry'].endswith('/RelicheirusEntity.class'))
        self.assertFalse({'readAdditionalSaveData','addAdditionalSaveData'} & {m['name'] for m in w['methods']})

    def test_tephra_custom_damage_formula_and_native_owner_stay_distinct(self):
        b=body('TephraExplosion','explode','dinosaur-extra')
        self.assertIn(9.0,[i['operand'] for i in b])
        self.assertIn('LuxtructosaurusEntity',str(b))
        n=next(n for n,i in enumerate(b) if '.hurt(' in str(i['operand']))
        self.assertEqual(b[n+1]['opcode'],'0x57')
        self.assertIn('setDeltaMovement',str(b[n+2:]))
        p=body('TephraEntity','onHitEntity','dinosaur-support')
        self.assertIn('ownedBy',str(p));self.assertIn('noPhysics',str(p))

    def test_fissure_step_and_inside_admission_are_different(self):
        step=body('FissurePrimalMagmaBlock','stepOn','dinosaur-extra')
        inside=body('FissurePrimalMagmaBlock','entityInside','dinosaur-extra')
        self.assertIn('FIRE_RESISTANCE',str(step));self.assertIn('isSteppingCarefully',str(step))
        self.assertNotIn('FIRE_RESISTANCE',str(inside));self.assertNotIn('isSteppingCarefully',str(inside))
        self.assertIn('LuxtructosaurusEntity',str(inside));self.assertIn('Vec3.multiply',str(inside))

    def test_false_literal_parameter_fails_validation(self):
        b=copy.deepcopy(read_json(OUT/'alexscaves-r2m8j-dinosaur-contracts.json'))
        r=copy.deepcopy(read_json(OUT/'mod-reviews/alexscaves.json')); ids={e['id'] for e in b['effects']}
        r['effects']=[e for e in r['effects'] if e['id'] not in ids]
        r['paths']=[e for e in r['paths'] if not set(e['effect_ids'])&ids]
        c=next(c for e in b['effects'] for c in e['scalable_parameter_candidates'] if 'native_literal_call_argument_binding' in c)
        c['native_literal_call_argument_binding']['native_value']+=1
        with self.assertRaises(AssertionError):validate_batch(b,r,read_json(OUT/'alexscaves-combat-census.json'))


if __name__=='__main__':
    unittest.main()
