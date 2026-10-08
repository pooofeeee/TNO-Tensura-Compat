"""Independent native ordering, dispatch and health-assignment checks."""
import unittest

from assemble_authored_contracts import render
from audit_numeric_labels import audit
from catalog_common import OUT, read_json
from promote_combat_batch import validate_batch

P = 'com/github/alexthe666/alexsmobs/'
F = 'native-evidence/alexsmobs-terrestrial.json'


def method(cls, name, file=F):
    w = next(w for w in read_json(OUT/file)['witnesses']
             if w['entry'] == P+cls+'.class')
    return next(m for m in w['methods'] if m['name'] == name)


def calls(body, symbol):
    return [i for i in body if i['opcode'] in ('0xb6', '0xb7', '0xb8', '0xb9')
            and symbol in str(i['operand'])]


class TerrestrialPredators(unittest.TestCase):
    def test_authored_render_numeric_and_canonical_validation(self):
        b = read_json(OUT/'alexsmobs-r2o5d-terrestrial-predators.json')
        self.assertEqual(render(read_json(OUT/'native-specifications/alexsmobs-terrestrial-predator-contracts.json')), b)
        r = read_json(OUT/'mod-reviews/alexsmobs.json')
        ids = {row['id'] for row in b['effects']}
        r['effects'] = [row for row in r['effects'] if row['id'] not in ids]
        r['paths'] = [row for row in r['paths'] if not set(row['effect_ids']) & ids]
        validate_batch(b, r, read_json(OUT/'alexsmobs-combat-census.json'))
        self.assertEqual(audit(dict(effects=b['effects']))['unresolved_numeric_labels'], 0)

    def test_snow_leopard_has_separate_goal_and_actor_damage_frames(self):
        goal = method('entity/ai/SnowLeopardAIMelee', 'tick')['instructions']
        own = method('entity/EntitySnowLeopard', 'tick')['instructions']
        self.assertEqual(next(i['operand'] for i in goal if i['offset'] == 590), 5)
        self.assertEqual([i['operand'] for i in own if i['offset'] in (663, 728)], [7, 7])
        self.assertEqual(len(calls(goal, '.doHurtTarget(')), 1)
        self.assertEqual(len(calls(own, '.doHurtTarget(')), 2)
        for hit in calls(own, '.doHurtTarget('):
            self.assertEqual(own[own.index(hit)+1]['opcode'], '0x57')
        self.assertLess(calls(own, '.doHurtTarget(')[0]['offset'], calls(own, '.knockback(')[0]['offset'])

    def test_tasmanian_knockback_precedes_ignored_damage(self):
        b = method('entity/EntityTasmanianDevil', 'tick')['instructions']
        damage = calls(b, '.hurt(')[0]
        self.assertLess(calls(b, '.knockback(')[0]['offset'], damage['offset'])
        self.assertEqual(b[b.index(damage)+1]['opcode'], '0x57')
        self.assertFalse(calls(b, '.addEffect('))
        for symbol in ('.setTarget(', '.setLastHurtByMob('):
            self.assertTrue(calls(b, symbol))

    def test_drop_bear_updates_animation_before_server_frame_delivery(self):
        b = method('entity/EntityDropBear', 'tick')['instructions']
        update = calls(b, 'AnimationHandler.updateAnimations(')[0]
        self.assertLess(update['offset'], calls(b, '.knockback(')[0]['offset'])
        for knock, hit in zip(calls(b, '.knockback('), calls(b, '.hurt(')):
            self.assertLess(knock['offset'], hit['offset'])
            self.assertEqual(b[b.index(hit)+1]['opcode'], '0x57')

    def test_drop_bear_landing_launch_follows_ignored_damage(self):
        b = method('entity/EntityDropBear', 'onLand')['instructions']
        hit = calls(b, '.hurt(')[0]
        self.assertEqual(b[b.index(hit)+1]['opcode'], '0x57')
        self.assertLess(hit['offset'], calls(b, '.launch(')[0]['offset'])
        launch = method('entity/EntityDropBear', 'launch')['instructions']
        self.assertTrue(calls(launch, '.push('))
        self.assertFalse(calls(launch, '.knockback('))
        self.assertTrue(calls(launch, 'Math.max('))

    def test_fall_sound_hook_is_before_native_hurt(self):
        d = read_json(OUT/'vanilla-evidence/alexsmobs-terrestrial-fall-dispatch.json')
        c = next(c for c in d['classes'] if c['class_name'].endswith('/LivingEntity'))
        m = next(m for m in c['methods'] if m['name'] == 'causeFallDamage')
        self.assertEqual(m['obfuscated_descriptor'].count(';'), 1)
        b = m['instructions']
        self.assertLess(calls(b, '.playBlockFallSound(')[0]['offset'], calls(b, '.hurt(')[0]['offset'])

    def test_tiger_capture_does_not_depend_on_accepted_hurt(self):
        b = method('entity/EntityTiger$AIMelee', 'tick')['instructions']
        hit = calls(b, '.hurt(')[-1]
        self.assertEqual(b[b.index(hit)+1]['opcode'], '0x57')
        hold = calls(b, '.setHolding(')[-1]
        self.assertLess(hit['offset'], hold['offset'])
        self.assertEqual(b[b.index(hold)-1]['operand'], 1)

    def test_tiger_hold_sets_motion_without_success_gate_or_passenger(self):
        b = method('entity/EntityTiger', 'tick')['instructions']
        hit = calls(b, '.hurt(')[0]
        self.assertLess(calls(b, '.setDeltaMovement(')[0]['offset'], hit['offset'])
        self.assertEqual(b[b.index(hit)+1]['opcode'], '0x57')
        self.assertFalse(calls(b, '.startRiding('))
        save = method('entity/EntityTiger', 'addAdditionalSaveData')['instructions']
        self.assertFalse(any('.holdTime' in str(i['operand']) for i in save))

    def test_grizzly_reduction_uses_causing_entity_before_parent_hurt(self):
        b = method('entity/EntityGrizzlyBear', 'hurt')['instructions']
        self.assertTrue(calls(b, 'DamageSource.getEntity('))
        self.assertFalse(calls(b, 'DamageSource.getDirectEntity('))
        self.assertLess(calls(b, '.setOrderedToSit(')[0]['offset'], calls(b, 'TamableAnimal.hurt(')[0]['offset'])
        self.assertEqual([i['operand'] for i in b if i['offset'] in (46, 48)], [1.0, 3.0])

    def test_grizzly_obsolete_melee_overload_is_not_parent_dispatch(self):
        native = method('entity/EntityGrizzlyBear$MeleeAttackGoal', 'checkAndPerformAttack')
        self.assertTrue(native['descriptor'].endswith(';D)V'))
        d = read_json(OUT/'vanilla-evidence/alexsmobs-predator-native-dispatch.json')
        c = next(c for c in d['classes'] if c['class_name'].endswith('/MeleeAttackGoal'))
        parent = next(m for m in c['methods'] if m['name'] == 'checkAndPerformAttack')
        self.assertTrue(parent['obfuscated_descriptor'].endswith(';)V'))
        self.assertFalse(parent['obfuscated_descriptor'].endswith(';D)V'))

    def test_freddy_hardcore_health_assignment_is_unconditional_after_hurt(self):
        b = method('entity/ai/GrizzlyBearAIAprilFools', 'tick')['instructions']
        hit = calls(b, '.hurt(')[0]
        self.assertEqual(b[b.index(hit)+1]['opcode'], '0x57')
        assign = calls(b, '.setHealth(')[0]
        between = [i['opcode'] for i in b if hit['offset'] < i['offset'] < assign['offset']]
        self.assertFalse(any(op.startswith('0x9') or op in ('0xa7', '0xc6', '0xc7') for op in between))
        self.assertEqual(b[b.index(assign)-1]['operand'], 1.0)

    def test_hive_provocation_preserves_native_grief_gate(self):
        b = method('entity/ai/GrizzlyBearAIBeehive', 'eatHive')['instructions']
        grief = calls(b, 'EventHooks.canEntityGrief(')[0]
        self.assertLess(grief['offset'], calls(b, '.destroyBlock(')[0]['offset'])
        for symbol in ('.setRemainingPersistentAngerTime(', '.setTarget(', '.setStayOutOfHiveCountdown('):
            self.assertTrue(calls(b, symbol))


if __name__ == '__main__':
    unittest.main()
