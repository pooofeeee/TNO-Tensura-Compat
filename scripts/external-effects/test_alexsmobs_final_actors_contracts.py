"""Pinned remaining actor failure, timing, resource and ownership boundaries."""
import unittest
from assemble_authored_contracts import render
from audit_numeric_labels import audit
from catalog_common import OUT,read_json
from promote_combat_batch import validate_batch
P='com/github/alexthe666/alexsmobs/'
RAW=read_json(OUT/'native-evidence/alexsmobs-remaining-actors.json')
def method(cls,name,desc=None):return next(m for w in RAW['witnesses'] if w['entry']==P+cls+'.class' for m in w['methods'] if m['name']==name and (not desc or m['descriptor']==desc))
def calls(b,s):return [i for i in b if s in str(i['operand'])]
class FinalActorContracts(unittest.TestCase):
    def test_render_and_numeric_validation(self):
        b=read_json(OUT/'alexsmobs-r2oc-final-actors.json');self.assertEqual(render(read_json(OUT/'native-specifications/alexsmobs-final-actors-contracts.json')),b)
        r=read_json(OUT/'mod-reviews/alexsmobs.json');ids={e['id'] for e in b['effects']};r['effects']=[e for e in r['effects'] if e['id'] not in ids];r['paths']=[p for p in r['paths'] if not set(p['effect_ids'])&ids]
        validate_batch(b,r,read_json(OUT/'alexsmobs-combat-census.json'));self.assertEqual(audit(dict(effects=b['effects']))['unresolved_numeric_labels'],0)
    def test_mimicube_setter_does_not_install_copied_equipment(self):
        b=method('entity/EntityMimicube','setSlot')['instructions'];self.assertFalse(calls(b,'.setItemSlot('));self.assertFalse(calls(b,'.setSlot('));self.assertFalse([i for i in b if i['opcode']=='0xb5' and '/Mob.' in str(i['operand'])]);self.assertTrue(calls(b,'.setCombatTask('))
    def test_mimicube_copy_side_effect_precedes_hurt_acceptance(self):
        b=method('entity/EntityMimicube','hurt')['instructions'];self.assertLess(max(i['offset'] for i in calls(b,'.setSlot(')),calls(b,'.hurt(')[0]['offset'])
    def test_mimicube_null_arrow_has_no_default_fallback(self):
        b=method('entity/EntityMimicube','fireArrow')['instructions'];self.assertEqual([i['opcode'] for i in b],['0x1','0xb0'])
        b=method('entity/EntityMimicube','performRangedAttack')['instructions'];self.assertTrue(calls(b,'.fireArrow('));self.assertTrue(calls(b,'.getY('));self.assertFalse([i for i in b if i['opcode'] in ['0xc6','0xc7']])
    def test_mimicube_main_food_clock_not_reset_after_heal(self):
        b=method('entity/EntityMimicube','tick')['instructions'];h=calls(b,'.heal(');self.assertEqual(len(h),2)
        writes=[i for i in calls(b,'.eatingTicksI') if i['opcode']=='0xb5'];self.assertTrue(any(h[0]['offset']<i['offset']<h[1]['offset'] for i in writes));self.assertEqual(len([i for i in writes if i['offset']>h[1]['offset']]),1)
        # The sole later reset is in the branch-failure else, beyond its goto.
        after=b[b.index(h[1])+1:];self.assertEqual(after[0]['opcode'],'0xa7');self.assertGreater(after[0]['branch_target'],[i for i in writes if i['offset']>h[1]['offset']][0]['offset'])
    def test_toad_damage_is_ignored_and_mosquito_substitution_exact(self):
        b=method('entity/EntityWarpedToad','tick')['instructions'];h=calls(b,'.hurt(')[0];self.assertEqual(b[b.index(h)+1]['opcode'],'0x57');self.assertEqual(next(i['operand'] for i in b if i['offset']==675),3.4028234663852886e+38);self.assertTrue(calls(b,'.getEyeHeight('));self.assertTrue(calls(b,'.setDeltaMovement('))
    def test_toad_damage_admission_precedes_parent(self):
        b=method('entity/EntityWarpedToad','hurt')['instructions'];self.assertLess(calls(b,'.setOrderedToSit(')[0]['offset'],calls(b,'.hurt(')[0]['offset']);self.assertTrue(calls(b,'AbstractArrow'))
    def test_farseer_uses_max_health_and_native_custom_source(self):
        b=method('entity/EntityFarseer$AttackGoal','tick')['instructions'];self.assertTrue(calls(b,'.getMaxHealth('));self.assertFalse(calls(b,'.getHealth('));self.assertTrue(calls(b,'.causeFarseerDamage('));self.assertTrue(calls(b,'.isAlive('));self.assertTrue(calls(b,'MessageSendVisualFlagFromServer.<init>'))
    def test_skreecher_failed_summon_consumes_attempt_before_requirements(self):
        b=method('entity/EntitySkreecher','tick')['instructions'];w=[i for i in calls(b,'.hasAttemptedWardenSpawningZ') if i['opcode']=='0xb5'][0];self.assertLess(w['offset'],calls(b,'.getBiome(')[0]['offset']);self.assertLess(w['offset'],calls(b,'.getNearbyWardens(')[0]['offset']);self.assertFalse(calls(b,'.hurt('));self.assertFalse(calls(b,'.addEffect('))
    def test_skreecher_hurt_detaches_even_before_rejection(self):
        b=method('entity/EntitySkreecher','hurt')['instructions'];self.assertLess(calls(b,'.setClinging(')[0]['offset'],calls(b,'.hurt(')[0]['offset']);self.assertLess(calls(b,'.setClapping(')[0]['offset'],calls(b,'.hurt(')[0]['offset'])
    def test_underminer_pretend_mining_has_no_terrain_mutation(self):
        b=method('entity/EntityUnderminer$MineGoal','tick')['instructions'];self.assertTrue(calls(b,'.setMiningProgress('));self.assertFalse(calls(b,'.destroyBlock('));self.assertFalse(calls(b,'.setBlock('));self.assertFalse(calls(b,'.hurt('))
    def test_board_codec_result_discarded_and_prefix_is_copied(self):
        b=method('entity/EntityStraddleboard','addAdditionalSaveData')['instructions'];h=calls(b,'ItemStack.save(')[0];self.assertEqual(b[b.index(h)+1]['opcode'],'0x57')
        v=read_json(OUT/'vanilla-evidence/alexsmobs-board-stack-prefix.json');b=next(m for c in v['classes'] if c['class_name'].endswith('$NbtRecordBuilder') for m in c['methods'] if m['name']=='build' and 'CompoundTag' in str(m['instructions']))['instructions'];self.assertTrue(calls(b,'.shallowCopy('));b=next(m for c in v['classes'] for m in c['methods'] if m['name']=='shallowCopy')['instructions'];self.assertTrue(calls(b,'HashMap.<init>(Ljava/util/Map;)V'))
    def test_board_extinguish_timer_never_armed(self):
        bodies=[m['instructions'] for w in RAW['witnesses'] if w['entry']==P+'entity/EntityStraddleboard.class' for m in w['methods']]
        writes=[(b,n) for b in bodies for n,i in enumerate(b) if i['opcode']=='0xb5' and '.extinguishTimerI' in str(i['operand'])];self.assertEqual(len(writes),2);self.assertEqual([b[n-1]['opcode'] for b,n in writes],['0x3','0x64'])
    def test_board_moves_before_current_rider_forward_install(self):
        b=method('entity/EntityStraddleboard','tick')['instructions'];self.assertLess(calls(b,'.tickMovement(')[0]['offset'],calls(b,'.boardForwardsF')[0]['offset']);self.assertTrue(calls(b,'.clearFire('));self.assertTrue(calls(b,'MobEffects.FIRE_RESISTANCE'))
if __name__=='__main__':unittest.main()
