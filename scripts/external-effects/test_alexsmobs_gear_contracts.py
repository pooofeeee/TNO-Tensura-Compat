"""Independent original movement, ownership, ordering and timer regressions."""
import unittest
from catalog_common import OUT,read_json
from assemble_authored_contracts import render
from promote_combat_batch import validate_batch
from audit_numeric_labels import audit

P='com/github/alexthe666/alexsmobs/'


def method(entry,name):
    w=next(w for w in read_json(OUT/'native-evidence/alexsmobs-gear-helpers.json')['witnesses'] if w['entry']==P+entry+'.class')
    return next(m for m in w['methods'] if m['name']==name)


class AlexMobsGearTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec=read_json(OUT/'native-specifications/alexsmobs-gear-contracts.json')
        cls.batch=read_json(OUT/'alexsmobs-r2o2c-gear-event-controls.json')

    def test_renderer_native_inputs_and_original_primitives(self):
        self.assertEqual(render(self.spec),self.batch)
        prior=read_json(OUT/'mod-reviews/alexsmobs.json')
        prior['effects']=[r for r in prior['effects'] if r['id'] not in {r['id'] for r in self.batch['effects']}]
        prior['paths']=[r for r in prior['paths'] if r['id'] not in {r['id'] for r in self.batch['paths']}]
        validate_batch(self.batch,prior,read_json(OUT/'alexsmobs-combat-census.json'))
        self.assertEqual(audit(dict(effects=self.batch['effects']))['native_candidate_identities'],41)

    def test_roll_damage_is_independent_of_hurt_acceptance_and_two_way_team_gate(self):
        m=method('entity/util/RockyChestplateUtil','tickRockyRolling');ins=m['instructions']
        n=next(n for n,i in enumerate(ins) if '.hurt(' in str(i['operand']))
        self.assertEqual(ins[n+1]['opcode'],'0x57')
        self.assertEqual(sum('isAlliedTo' in str(i['operand']) for i in ins),2)
        self.assertTrue(any('DamageSources.mobAttack' in str(i['operand']) for i in ins))
        self.assertFalse(any('.knockback(' in str(i['operand']) for i in ins))
        self.assertTrue(any('setForcedPose' in str(i['operand']) for i in ins))
        self.assertEqual(next(i['operand'] for i in ins if i['offset']==81),30)

    def test_roll_counter_one_and_sprinting_keep_native_lifecycle(self):
        m=method('entity/util/RockyChestplateUtil','tickRockyRolling')
        ins=m['instructions'];n=next(n for n,i in enumerate(ins) if i['offset']>395 and '.isSprinting()' in str(i['operand']))
        self.assertTrue(any(i['opcode']=='0xa3' for i in ins[max(0,n-7):n]))
        r=next(r for r in self.batch['effects'] if r['id']=='alexsmobs:rocky_chestplate_roll')
        self.assertIn('counter1 persists while sprinting',r['actual_behavior'])

    def test_lasso_sync_checks_key_presence_and_player_y_is_zero(self):
        ins=method('entity/util/VineLassoUtil','tickLasso')['instructions']
        self.assertTrue(any('CompoundTag.contains(Ljava/lang/String;)Z' in str(i['operand']) for i in ins))
        self.assertTrue(any(i['opcode']=='0xc1' and i['operand']=='net/minecraft/world/entity/player/Player' for i in ins))
        self.assertEqual(next(i['operand'] for i in ins if i['offset']==189),0.0)
        self.assertFalse(any('.hurt(' in str(i['operand']) for i in ins))

    def test_flying_boost_writes_original_tag_and_preserves_binary_flight_gate(self):
        ins=method('entity/util/FlyingFishBootsUtil','tickFlyingFishBoots')['instructions']
        self.assertTrue(any('Abilities.flying' in str(i['operand']) for i in ins))
        self.assertTrue(any('Pose.FALL_FLYING' in str(i['operand']) for i in ins))
        self.assertEqual(next(i['operand'] for i in ins if i['offset']==76),35)
        self.assertFalse(any('.hurt(' in str(i['operand']) for i in ins))
        self.assertTrue(any('MessageSyncEntityData.<init>' in str(i['operand']) for i in method('entity/util/FlyingFishBootsUtil','setBoostTicks')['instructions']))

    def test_water_breathing_is_exact_native_holder_and_duration(self):
        r=next(r for r in self.batch['effects'] if r['id']=='alexsmobs:spiked_turtle_shell')
        c=next(c for c in r['scalable_parameter_candidates'] if c['primitive']=='MOB_EFFECT_WATER_BREATHING')
        self.assertIn('MobEffects.WATER_BREATHING',c['native_holder_symbol'])
        self.assertEqual(c['native_literal_effect_arguments']['duration'],310)
        self.assertEqual(c['native_literal_effect_arguments']['amplifier'],0)
        self.assertEqual(c['native_literal_effect_arguments']['explicit_flags'],[0,0,1])


if __name__=='__main__':unittest.main()
