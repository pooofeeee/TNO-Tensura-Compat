"""Check native sources and ordering independently of authored forager prose."""
import unittest

from assemble_authored_contracts import render
from audit_numeric_labels import audit
from catalog_common import OUT, read_json
from promote_combat_batch import validate_batch

P = 'com/github/alexthe666/alexsmobs/'
F = 'native-evidence/alexsmobs-small-foragers.json'


def method(cls, name, file=F):
    witness = next(w for w in read_json(OUT/file)['witnesses']
                   if w['entry'] == P+cls+'.class')
    return next(m for m in witness['methods'] if m['name'] == name)


def calls(body, part):
    return [i for i in body if i['opcode'] in ('0xb6', '0xb7', '0xb8', '0xb9')
            and part in str(i['operand'])]


class ForagerContracts(unittest.TestCase):
    def test_exact_render_and_independent_numeric_bindings(self):
        batch = read_json(OUT/'alexsmobs-r2o5c-small-foragers.json')
        self.assertEqual(render(read_json(OUT/'native-specifications/alexsmobs-forager-contracts.json')), batch)
        review = read_json(OUT/'mod-reviews/alexsmobs.json')
        ids = {r['id'] for r in batch['effects']}
        review['effects'] = [r for r in review['effects'] if r['id'] not in ids]
        review['paths'] = [r for r in review['paths'] if not set(r['effect_ids']) & ids]
        validate_batch(batch, review, read_json(OUT/'alexsmobs-combat-census.json'))
        self.assertEqual(audit(dict(effects=batch['effects']))['unresolved_numeric_labels'], 0)

    def test_fly_generic_damage_has_no_actor_and_ignores_return(self):
        body = method('entity/EntityFly$AnnoyZombieGoal', 'tick')['instructions']
        damage = calls(body, '.hurt(')[0]
        self.assertTrue(calls(body, 'DamageSources.generic()'))
        self.assertFalse(calls(body, '.mobAttack('))
        self.assertEqual(body[body.index(damage)-1]['operand'], 1.0)
        self.assertEqual(body[body.index(damage)+1]['opcode'], '0x57')
        self.assertLess(calls(body, '.getHealth(')[0]['offset'], damage['offset'])
        self.assertEqual(next(i['operand'] for i in body if i['offset'] == 152), 3.0)

    def test_fly_conversion_keeps_accumulated_nonpersistent_clock(self):
        body = method('entity/EntityFly', 'tick')['instructions']
        writes = [i for i in body if i['opcode'] == '0xb5' and '.conversionTimeI' in str(i['operand'])]
        self.assertEqual(len(writes), 1)
        self.assertLess(calls(body, '.addFreshEntity(')[0]['offset'], calls(body, '.onSpawnFromFly(')[0]['offset'])
        self.assertLess(calls(body, '.onSpawnFromFly(')[0]['offset'], calls(body, '.remove(')[0]['offset'])
        self.assertFalse(any('.conversionTimeI' in str(i['operand']) for i in
                             method('entity/EntityFly', 'addAdditionalSaveData')['instructions']))

    def test_cockroach_headless_does_not_heal_or_veto_parent_hurt(self):
        body = method('entity/EntityCockroach', 'hurt')['instructions']
        self.assertLess(calls(body, 'Animal.hurt(')[0]['offset'], calls(body, '.setHeadless(')[0]['offset'])
        self.assertFalse(calls(body, '.heal('))
        self.assertFalse(calls(body, '.setHealth('))
        body = method('entity/EntityCockroach', 'travel')['instructions']
        self.assertTrue(calls(body, '.stop()'))
        self.assertTrue(any('Vec3.ZERO' in str(i['operand']) for i in body))

    def test_maned_wolf_clears_both_native_aggro_fields_after_sitting_veto(self):
        body = method('entity/EntityManedWolf', 'attractAnimals')['instructions']
        sitting = calls(body, '.isInSittingPose(')[0]['offset']
        for symbol in ('.setTarget(', '.setLastHurtByMob('):
            hit = calls(body, symbol)[0]
            self.assertGreater(hit['offset'], sitting)
            self.assertEqual(body[body.index(hit)-1]['opcode'], '0x1')
        self.assertFalse(calls(body, '.addEffect('))
        self.assertFalse(calls(body, '.hurt('))
        tick = method('entity/EntityManedWolf', 'tick')['instructions']
        self.assertLess(calls(tick, '.setShakingTime(')[0]['offset'], calls(tick, '.attractAnimals(')[0]['offset'])

    def test_platypus_poison_requires_accepted_hurt_and_direct_living_actor(self):
        body = method('entity/EntityPlatypus', 'hurt')['instructions']
        self.assertEqual(body[4]['opcode'], '0x3e')
        self.assertEqual(body[6]['opcode'], '0x99')
        self.assertTrue(calls(body, '.getDirectEntity('))
        self.assertFalse(calls(body, 'DamageSource.getEntity('))
        ctor = calls(body, 'MobEffectInstance.<init>(')[0]
        self.assertTrue(ctor['operand'].endswith('(Lnet/minecraft/core/Holder;I)V'))
        self.assertEqual(body[body.index(ctor)-1]['operand'], 100)

    def test_platypus_bucket_copy_is_not_assigned_back(self):
        body = method('entity/EntityPlatypus', 'saveToBucketTag')['instructions']
        copy = calls(body, 'CustomData.copyTag(')[0]
        self.assertTrue(calls(body, 'CompoundTag.put('))
        self.assertFalse(calls(body, 'Bucketable.saveDefaultDataToBucketTag('))
        self.assertFalse(calls([i for i in body if i['offset'] > copy['offset']], 'ItemStack.set('))

    def test_rain_frog_dance_registration_is_clientbound_only(self):
        body = method('network/AMNetworking', 'register', 'native-evidence/alexsmobs-foundation.json')['instructions']
        at = next(n for n, i in enumerate(body) if 'MessageStartDancing.ID' in str(i['operand']))
        self.assertIn('PayloadRegistrar.playToClient(', body[at+3]['operand'])
        body = method('entity/EntityRainFrog', 'setRecordPlayingNearby')['instructions']
        self.assertTrue(calls(body, '.sendMSGToServer('))
        census = read_json(OUT/'alexsmobs-combat-census.json')
        from collect_combat_census import decode_sites
        writers = {(m['entry'], m['method']) for m in census['methods']
                   if any('EntityRainFrog.setDanceTime(I)V' in str(i['operand'])
                          for i in decode_sites(census, m, 'calls'))}
        self.assertEqual(writers, {(P+'entity/EntityRainFrog.class', 'tick'),
                                  (P+'entity/EntityRainFrog.class', 'setDancing')})

    def test_rain_frog_random_one_cannot_select_thunder_case(self):
        body = method('entity/EntityRainFrog', 'changeWeather')['instructions']
        rng = calls(body, 'RandomSource.nextInt(')
        self.assertEqual(len(rng), 2)
        self.assertEqual(body[body.index(rng[1])-1]['operand'], 1)
        row = next(r for r in read_json(OUT/'alexsmobs-r2o5c-small-foragers.json')['effects']
                   if r['id'] == 'alexsmobs:rain_frog_native_environment_gate')
        self.assertEqual(row['native_activation_status'], 'NO_PINNED_REGISTERED_SERVER_POSITIVE_DANCE_WRITER')
        self.assertEqual(row['scalable_parameter_candidates'], [])

    def test_potoo_removal_is_after_ignored_hurt_not_hurt_success(self):
        body = method('entity/EntityPotoo$AIMelee', 'tick')['instructions']
        hurt = calls(body, '.hurt(')[0]
        self.assertEqual(body[body.index(hurt)+1]['opcode'], '0x57')
        self.assertLess(hurt['offset'], calls(body, '.getBbWidth(')[0]['offset'])
        self.assertLess(hurt['offset'], calls(body, '.remove(')[0]['offset'])
        self.assertTrue(any('RemovalReason.KILLED' in str(i['operand']) for i in body))
        self.assertEqual(method('entity/EntityPotoo', 'onLaunch')['instructions'],
                         [dict(offset=0, opcode='0xb1', operand=None)])

    def test_toucan_healing_is_delayed_native_held_food_not_golden_effect(self):
        body = method('entity/EntityToucan', 'onGetItem')['instructions']
        self.assertFalse(calls(body, '.heal('))
        body = method('entity/EntityToucan', 'tick')['instructions']
        heal = calls(body, '.heal(')[0]
        self.assertEqual(body[body.index(heal)-1]['operand'], 4.0)
        self.assertLess(calls(body, '.canTargetItem(')[0]['offset'], heal['offset'])
        self.assertFalse(calls(body, '.addEffect('))

    def test_slug_slime_is_item_drop_without_damage_or_trail_block(self):
        body = method('entity/EntityBananaSlug', 'tick')['instructions']
        self.assertTrue(calls(body, '.spawnAtLocation('))
        for symbol in ('.setBlock(', '.hurt(', '.addEffect('):
            self.assertFalse(calls(body, symbol))


if __name__ == '__main__':
    unittest.main()
