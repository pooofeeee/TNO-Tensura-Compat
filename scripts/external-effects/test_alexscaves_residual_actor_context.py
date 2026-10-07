"""Native producer/source invariants; callbacks are not inferred from names."""
import copy
import unittest
from catalog_common import OUT, read_json
from assemble_authored_contracts import render
from promote_combat_batch import validate_batch


def method(cls,name):
    specs=read_json(OUT/'native-findings/alexscaves-residual-actor-caller-context.json')
    selections=[p for row in specs['contracts']+specs['exclusions'] for p in row['implementation']]
    selections += [p for row in specs['record_refinements'] for p in row['implementation_additions']]
    p=next(p for p in selections if p['entry'].endswith('/'+cls+'.class') and name in p['methods'])
    w=next(w for w in read_json(OUT/p['evidence_file'])['witnesses'] if w['entry']==p['entry'])
    return next(m for m in w['methods'] if m['name']==name)


class ResidualActorTests(unittest.TestCase):
    def test_render_native_proofs_and_candidate_identity(self):
        b=read_json(OUT/'alexscaves-r2m8y-residual-actor-caller-context.json')
        self.assertEqual(b,render(read_json(OUT/'native-findings/alexscaves-residual-actor-caller-context.json')))
        r=copy.deepcopy(read_json(OUT/'mod-reviews/alexscaves.json'));ids={e['id'] for e in b['effects']}
        r['effects']=[e for e in r['effects'] if e['id'] not in ids]
        r['paths']=[e for e in r['paths'] if not ids.intersection(e['effect_ids'])]
        self.assertEqual(validate_batch(b,r,read_json(OUT/'alexscaves-combat-census.json'))['status'],'PASS')

    def test_generic_part_hurt_only_sends_request_and_returns_false(self):
        b=method('ACMultipartEntity','hurt')['instructions'];s=str(b)
        self.assertIn('DamageSource.getEntity(',s);self.assertIn('.sendMSGToServer(',s)
        self.assertNotIn('Entity.hurt(',s)
        self.assertEqual([i['opcode'] for i in b[-2:]],['0x3','0xac'])

    def test_chunk_spawn_uses_original_native_spawn_rules_and_passengers(self):
        b=str(method('NaturalSpawnerMixin','ac_spawnMobsForChunkGeneration')['instructions'])
        for s in ('.checkSpawnRules(','.checkSpawnObstruction(','.finalizeSpawn(',
                  'MobSpawnType.CHUNK_GENERATION','.addFreshEntityWithPassengers('):self.assertIn(s,b)
        for s in ('.setOwner(','.hurt(','.addEffect('):self.assertNotIn(s,b)

    def test_bucket_cause_is_not_an_owner(self):
        b=method('ModFishBucketItem','spawnFish')['instructions'];s=str(b)
        at=next(n for n,i in enumerate(b) if 'EntityType.spawn(' in str(i['operand']))
        self.assertEqual(b[at-6]['opcode'],'0x1') # Native NULL followed by its explicit cast.
        self.assertEqual((b[at-5]['opcode'],b[at-5]['operand']),
                         ('0xc0','net/minecraft/world/entity/player/Player'))
        for text in ('MobSpawnType.BUCKET','.loadFromBucketTag(','.setFromBucket('):self.assertIn(text,s)
        self.assertNotIn('.setOwner(',s)

    def test_rider_admission_is_dinosaur_specific(self):
        b=str(method('CommonEvents','playerAttack')['instructions'])
        self.assertIn('DinosaurEntity',b);self.assertIn('.isPassengerOfSameVehicle(',b)
        self.assertIn('.setCanceled(',b);self.assertNotIn('.hurt(',b)

    def test_direct_vanilla_status_holders_and_values_are_distinct(self):
        b=read_json(OUT/'alexscaves-r2m8y-residual-actor-caller-context.json')
        e=next(e for e in b['effects'] if e['id'].endswith(':native_potion_vanilla_status_definitions'))
        self.assertEqual({c['primitive'] for c in e['components']},
                         {'MOB_EFFECT_GLOWING','MOB_EFFECT_DIG_SPEED','MOB_EFFECT_HUNGER'})
        for c in e['scalable_parameter_candidates']:
            self.assertIn(c['primitive'].removeprefix('MOB_EFFECT_'),c['native_holder_symbol'])
            self.assertTrue(c['observation_only'])
        self.assertEqual(len(e['scalable_parameter_candidates']),8)

    def test_goal_uses_existing_attack_boundary_not_duplicate_damage(self):
        b=str(method('DeepOneAttackGoal','tick')['instructions'])
        self.assertIn('.startAttackBehavior(',b);self.assertIn('.alertSubmarineMountOf(',b)
        self.assertNotIn('.hurt(',b)

    def test_corrodent_tail_reuses_generic_hurt_without_a_native_override(self):
        c=read_json(OUT/'alexscaves-combat-census.json')
        tail=next(r for r in c['classes'] if r['entry'].endswith('/CorrodentTailEntity.class'))
        self.assertTrue(tail['superclass'].endswith('/ACMultipartEntity'))
        self.assertFalse(any(m['entry']==tail['entry'] and m['method']=='hurt' for m in c['methods']))
        r=next(e for e in read_json(OUT/'mod-reviews/alexscaves.json')['effects']
               if e['id']=='alexscaves:corrodent_bite_native_dig_light_fear')
        self.assertNotIn('useslockedparenthurt',r['actual_behavior'])


if __name__=='__main__':unittest.main()
