"""Shared harness, independent native facts for bounded small-actor families."""
import unittest
from catalog_common import OUT, read_json
from promote_combat_batch import validate_batch
from test_shadow_clone_contracts import NativeContractHarness


class SmallInsectNativeTests(NativeContractHarness, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch=read_json(OUT/'arphex-r2m5g-small-insect-native-callbacks.json')
        cls.native=read_json(OUT/'native-evidence/arphex-small-insect-callback-family.json')
        cls.census=read_json(OUT/'arphex-combat-census.json')

    def test_native_bindings_and_single_shared_collision_registration(self):
        validate_batch(self.batch,self.prior(),self.census)
        self.assertEqual((len(self.batch['effects']),len(self.batch['closed_actor_callback_entries'])),(5,4))
        self.assertEqual(sum(len(c['parameters']) for r in self.batch['effects']
                             for c in r['scalable_parameter_candidates']),21)
        rows=[r for r in self.batch['effects'] if any(c['native_consumer']['entry'].endswith('/MaggotPlayerCollidesWithThisEntityProcedure.class')
                                                  for c in r['scalable_parameter_candidates'])]
        self.assertEqual(len(rows),1)
        self.assertFalse(self.batch['whole_mod_complete'])

    def test_collision_command_ignores_original_colliding_player(self):
        for actor in ('MaggotLarvaeEntity','FlyFestererEntity'):
            b=self.body(actor,'playerTouch')
            self.assertTrue(any('Monster.playerTouch(' in str(i['operand']) for i in b))
            j=next(j for j,i in enumerate(b) if 'MaggotPlayerCollidesWithThisEntityProcedure.execute(' in str(i['operand']))
            self.assertIn('(Lnet/minecraft/world/level/LevelAccessor;DDD)V',b[j]['operand'])
            for coord in ('getX()', 'getY()', 'getZ()'):
                self.assertTrue(any(coord in str(i['operand']) for i in b[:j]))
        b=self.body('MaggotPlayerCollidesWithThisEntityProcedure')
        cmd=next(i['operand'] for i in b if isinstance(i['operand'],str) and i['operand'].startswith('effect give'))
        self.assertEqual(cmd,'effect give @p poison 1 1')
        self.assertTrue(any('CommandSource.NULL' in str(i['operand']) for i in b))
        self.assertFalse(any('.hurt(' in str(i['operand']) for i in b))

    def test_step_height_is_direct_attribute_write(self):
        b=self.body('BeetleTickMiteOnEntityTickProcedure')
        self.assertTrue(any('Attributes.STEP_HEIGHT' in str(i['operand']) for i in b))
        j=next(j for j,i in enumerate(b) if i['offset']==33)
        self.assertEqual(b[j]['operand'],'net/minecraft/world/entity/ai/attributes/AttributeInstance.setBaseValue(D)V')
        self.assertEqual(b[j-1]['operand'],2.)
        self.assertTrue(any('LivingEntity.getAttribute(' in str(i['operand']) for i in b[:j]))
        self.assertFalse(any('.setDeltaMovement(' in str(i['operand']) for i in b))

    def test_fly_yboost_reads_other_clock_and_late_water_write(self):
        b=self.body('FlyFestererTickProcedure')
        j=next(j for j,i in enumerate(b) if i['offset']==624)
        segment=b[j-8:j]
        self.assertIn('yboost',[i['operand'] for i in segment])  # write key
        read=next(k for k,i in enumerate(segment) if 'CompoundTag.getDouble(' in str(i['operand']))
        self.assertEqual(segment[read-1]['operand'],'flyboost')  # value read key
        self.assertIn(1.,[i['operand'] for i in segment])
        self.assertEqual([i['offset'] for i in b if '.setDeltaMovement(' in str(i['operand'])],[318,549,578,676])
        r=self.row('fly_festerer_native_coupled_motion_and_incoming_state')
        keys={k for c in r['scalable_parameter_candidates'] for k in c['parameters']}
        self.assertFalse(any('yboost' in k for k in keys))
        goal=self.body('FlyFestererEntity','registerGoals')
        self.assertFalse(any('MeleeAttackGoal' in str(i['operand']) for i in goal))
        self.assertFalse(any(c['primitive']=='NATIVE_CONDITIONAL_MELEE' for c in r['scalable_parameter_candidates']))

    def test_shiny_gate_applies_only_to_player_avoidance(self):
        b=self.body('RoachRiverspawnEntity$1','canUse')
        self.assertTrue(any('AvoidEntityGoal.canUse(' in str(i['operand']) for i in b))
        self.assertTrue(any('RoachShinyProcedure.execute(' in str(i['operand']) for i in b))
        b=self.body('RoachRiverspawnEntity$2','canPerformAttack')
        self.assertFalse(any('RoachShinyProcedure.execute(' in str(i['operand']) for i in b))
        self.assertTrue(any('.hasLineOfSight(' in str(i['operand']) for i in b))
        b=self.body('RoachShinyProcedure')
        self.assertTrue(any('RoachRiverspawnEntity.DATA_shiny' in str(i['operand']) for i in b))

    def test_maggot_native_discard_precedes_unowned_fly_spawn(self):
        b=self.body('MaggotOnEntityTickUpdateProcedure')
        discard=next(i['offset'] for i in b if '.discard(' in str(i['operand']))
        self.assertLess(discard,135)
        self.assertTrue(any('ArphexModEntities.FLY_FESTERER' in str(i['operand']) for i in b))
        self.assertEqual(sum('EntityType.spawn(' in str(i['operand']) for i in b),1)
        self.assertFalse(any('.setOwner(' in str(i['operand']) for i in b))
        j=next(j for j,i in enumerate(b) if i['offset']==67)
        self.assertEqual([i['operand'] for i in b[j-2:j]],[1,5000])
        goal=self.body('MaggotLarvaeEntity$1','canPerformAttack')
        self.assertTrue(any('.hasLineOfSight(' in str(i['operand']) for i in goal))
        self.assertFalse(any('MaggotPlayerCollidesWithThisEntityProcedure' in str(i['operand']) for i in goal))
