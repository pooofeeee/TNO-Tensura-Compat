"""Pinned multipart damage, fallback, split and current dispatch regressions."""
import unittest
from assemble_authored_contracts import render
from audit_numeric_labels import audit
from catalog_common import OUT,read_json
from promote_combat_batch import validate_batch
P='com/github/alexthe666/alexsmobs/'
RAW=read_json(OUT/'native-evidence/alexsmobs-remaining-actors.json')
def method(cls,name,desc=None):return next(m for w in RAW['witnesses'] if w['entry']==P+cls+'.class' for m in w['methods'] if m['name']==name and (not desc or m['descriptor']==desc))
def calls(b,s):return [i for i in b if s in str(i['operand'])]
class MultipartContracts(unittest.TestCase):
    def test_render_numeric_validation(self):
        b=read_json(OUT/'alexsmobs-r2ob-multipart.json');self.assertEqual(render(read_json(OUT/'native-specifications/alexsmobs-multipart-contracts.json')),b)
        r=read_json(OUT/'mod-reviews/alexsmobs.json');ids={e['id'] for e in b['effects']};r['effects']=[e for e in r['effects'] if e['id'] not in ids];r['paths']=[p for p in r['paths'] if not set(p['effect_ids'])&ids]
        validate_batch(b,r,read_json(OUT/'alexsmobs-combat-census.json'));self.assertEqual(audit(dict(effects=b['effects']))['unresolved_numeric_labels'],0)
    def test_centipede_poison_requires_parent_success(self):
        b=method('entity/EntityCentipedeHead','doHurtTarget')['instructions'];h=calls(b,'.doHurtTarget(')[0];self.assertEqual(h['opcode'],'0xb7');self.assertEqual(b[b.index(h)+1]['branch_target'],104);self.assertLess(calls(b,'.addEffect(')[0]['offset'],104)
    def test_centipede_forwards_without_own_damage_or_invulnerability(self):
        b=method('entity/EntityCentipedeBody','hurt')['instructions'];self.assertTrue(calls(b,'.hurt('));self.assertFalse([i for i in calls(b,'.hurt(') if i['opcode']=='0xb7']);self.assertFalse(calls(b,'.isInvulnerableTo('));self.assertTrue(calls(b,'.damageMultiplierF'))
    def test_tail_factory_instantiates_body_for_tail_type(self):
        b=method('entity/EntityCentipedeHead','createBody')['instructions'];self.assertEqual([i['operand'] for i in b if i['opcode']=='0xbb'],[P+'entity/EntityCentipedeBody']*2);self.assertTrue(calls(b,'CENTIPEDE_TAIL'))
    def test_worm_part_hurts_self_not_parent(self):
        b=method('entity/EntityVoidWormPart','hurt')['instructions'];h=calls(b,'.hurt(');self.assertEqual(len(h),1);self.assertEqual(h[0]['opcode'],'0xb7');self.assertFalse(calls(b,'.damageMultiplierF'))
    def test_worm_split_no_parent_die_and_base_health_used(self):
        b=method('entity/EntityVoidWormPart','die')['instructions'];self.assertFalse(calls(b,'.die('));self.assertTrue(calls(b,'.getBaseMaxHealth('));self.assertTrue(calls(b,'.setParent('));self.assertTrue(calls(b,'.setSplitFromUuid('));self.assertFalse(calls(b,'.getHealth('))
    def test_reset_scales_native_loop_is_unreachable(self):
        b=method('entity/EntityVoidWorm','resetWormScales')['instructions'];by={i['offset']:i for i in b};self.assertEqual(by[16]['opcode'],'0xc7');self.assertEqual(by[16]['branch_target'],192);self.assertEqual(by[19]['local_index'],0);self.assertEqual(by[20]['local_index'],2);self.assertEqual(by[51]['operand'],P+'entity/EntityVoidWormPart')
    def test_shot_additive_launch_but_homing_overwrites(self):
        b=method('entity/EntityVoidWormShot','shoot')['instructions'];self.assertTrue(calls(b,'.getDeltaMovement('));self.assertTrue(calls(b,'Vec3.add('));self.assertTrue(calls(b,'.setDeltaMovement('))
        b=method('entity/EntityVoidWormShot','tick')['instructions'];self.assertTrue(calls(b,'.getTarget('));self.assertTrue(calls(b,'.setDeltaMovement('))
    def test_shield_disable_is_hurt_acceptance_gated(self):
        b=method('entity/EntityVoidWormShot','onEntityHit')['instructions'];h=calls(b,'.wormAttack(')[0];self.assertEqual(b[b.index(h)+1]['local_index'],3);self.assertEqual(b[b.index(h)+2]['local_index'],3);self.assertEqual(b[b.index(h)+3]['opcode'],'0x99');self.assertGreater(b[b.index(h)+3]['branch_target'],calls(b,'.disableShield(')[0]['offset']);self.assertTrue(calls(b,'RemovalReason.DISCARDED'))
    def test_worm_death_owns_capture_without_parent_death_tick(self):
        b=method('entity/EntityVoidWorm','tickDeath')['instructions'];self.assertFalse(calls(b,'.tickDeath('));self.assertEqual(len(calls(b,'.captureDrops(')),2);self.assertTrue(calls(b,'.onLivingDrops('));self.assertTrue(calls(b,'.dropExperience('))
    def test_murmur_body_rejection_falls_back_full_head_hurt(self):
        b=method('entity/EntityMurmurHead','hurt')['instructions'];h=calls(b,'.hurt(');self.assertEqual([i['opcode'] for i in h],['0xb6','0xb7']);self.assertEqual(b[b.index(h[0])+1]['opcode'],'0x99');self.assertLess(h[0]['offset'],h[1]['offset']);self.assertEqual(next(i for i in b if i['offset']==21)['operand'],.5)
    def test_murmur_attack_cooldown_precedes_ignored_hurt(self):
        b=method('entity/EntityMurmurHead$AttackGoal','tick')['instructions'];h=calls(b,'.hurt(')[0];self.assertEqual(b[b.index(h)+1]['opcode'],'0x57');self.assertLess(calls(b,'.biteCooldownI')[0]['offset'],h['offset'])
    def test_legacy_zero_arg_xp_is_not_current_dispatch(self):
        c=read_json(OUT/'alexsmobs-combat-census.json');self.assertFalse([s for s in c['symbols'] if '.getExperienceReward()I' in s]);v=read_json(OUT/'vanilla-evidence/alexsmobs-multipart-xp-dispatch.json')
        for cls in v['classes']:self.assertFalse([m for m in cls['declared_methods'] if m['name']=='getExperienceReward' and m['obfuscated_descriptor']=='()I'])
        b=next(m for c in v['classes'] for m in c['methods'] if m['name']=='getExperienceReward')['instructions'];self.assertTrue(calls(b,'.getBaseExperienceReward()I'))
if __name__=='__main__':unittest.main()
