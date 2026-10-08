"""Verify shore payload ordering, dispatch, admission and persistence defects."""
import unittest
from assemble_authored_contracts import render
from audit_numeric_labels import audit
from catalog_common import OUT,read_json
from promote_combat_batch import validate_batch
P='com/github/alexthe666/alexsmobs/'
PACKETS=[read_json(OUT/'native-evidence'/f'alexsmobs-{n}.json') for n in ('shore-terrestrial','shore-payloads','shore-thrown-items')]
def method(cls,name):
    return next(m for d in PACKETS for w in d['witnesses'] if w['entry']==P+cls+'.class' for m in w['methods'] if m['name']==name)
def calls(b,s):return [i for i in b if s in str(i['operand'])]
class ShoreContracts(unittest.TestCase):
    def test_render_and_exact_numeric_validation(self):
        b=read_json(OUT/'alexsmobs-r2o6-shore-terrestrial.json')
        self.assertEqual(render(read_json(OUT/'native-specifications/alexsmobs-shore-terrestrial-contracts.json')),b)
        r=read_json(OUT/'mod-reviews/alexsmobs.json');ids={e['id'] for e in b['effects']}
        r['effects']=[e for e in r['effects'] if e['id'] not in ids];r['paths']=[p for p in r['paths'] if not set(p['effect_ids'])&ids]
        validate_batch(b,r,read_json(OUT/'alexsmobs-combat-census.json'))
        self.assertEqual(audit(dict(effects=b['effects']))['unresolved_numeric_labels'],0)
    def test_frost_tackle_jump_uses_inherited_jump(self):
        b=method('entity/EntityFroststalker','frostJump')['instructions']
        self.assertTrue(calls(b,'.jumpFromGround('));self.assertFalse(calls(b,'.customJumpFromGround('))
    def test_frost_animated_knockback_precedes_ignored_hurt(self):
        b=method('entity/EntityFroststalker','tick')['instructions'];h=calls(b,'.hurt(')[0]
        self.assertLess(calls(b,'.knockback(')[0]['offset'],h['offset']);self.assertEqual(b[b.index(h)+1]['opcode'],'0x57')
    def test_ice_shard_entity_hit_retains_projectile(self):
        b=method('entity/EntityIceShard','onEntityHit')['instructions']
        self.assertTrue(calls(b,'.hurt('));self.assertFalse(calls(b,'.discard('))
        self.assertTrue(calls(b,'EntityFroststalker'))
    def test_rocky_thorns_precedes_parent_hurt(self):
        b=method('entity/EntityRockyRoller','hurt')['instructions'];h=calls(b,'.hurt(')
        self.assertEqual(len(h),2);self.assertLess(calls(b,'.thorns(')[0]['offset'],h[0]['offset']);self.assertEqual(h[-1]['opcode'],'0xb7')
    def test_rocky_stalactite_check_is_string_equals(self):
        b=method('entity/EntityRockyRoller','isInvulnerableTo')['instructions']
        self.assertTrue(any(i['operand']=='fallingStalactite' for i in b));self.assertTrue(calls(b,'.equals('))
    def test_skunk_cloud_has_no_owner_assignment(self):
        b=method('entity/EntitySkunk','spawnLingeringCloud')['instructions']
        self.assertTrue(calls(b,'.addEffect('));self.assertTrue(calls(b,'.addFreshEntity('));self.assertFalse(calls(b,'.setOwner('))
    def test_skunk_spray_copies_active_instances(self):
        b=method('entity/EntitySkunk$SprayGoal','tick')['instructions']
        self.assertTrue(calls(b,'.getActiveEffects('));self.assertTrue(calls(b,'MobEffectInstance.<init>(Lnet/minecraft/world/effect/MobEffectInstance;)'))
        self.assertFalse(calls(b,'canEntityGrief('))
    def test_tossed_save_omits_parent_owner_transport(self):
        for n in ('addAdditionalSaveData','readAdditionalSaveData'):
            b=method('entity/EntityTossedItem',n)['instructions'];self.assertFalse(any(i['opcode']=='0xb7' for i in b))
    def test_capuchin_ranged_attack_time_has_no_decrement(self):
        b=method('entity/ai/CapuchinAIRangedAttack','tick')['instructions']
        sites=calls(b,'.attackTimeI');self.assertEqual(len(sites),1);self.assertEqual(sites[0]['opcode'],'0xb5')
    def test_sugar_owner_status_is_before_detach(self):
        b=method('entity/EntitySugarGlider','rideTick')['instructions']
        self.assertLess(calls(b,'.addEffect(')[0]['offset'],calls(b,'.removeVehicle(')[0]['offset'])
    def test_mud_status_follows_unconditional_base_discard(self):
        b=method('entity/EntityMudBall','onEntityHit')['instructions'];self.assertLess(calls(b,'.onEntityHit(')[0]['offset'],calls(b,'.addEffect(')[0]['offset'])
        x=method('entity/EntityMobProjectile','onEntityHit')['instructions'];self.assertTrue(calls(x,'.remove('));h=calls(x,'.hurt(')[0];self.assertEqual(x[x.index(h)+1]['opcode'],'0x3e')
    def test_mud_bucket_modified_copy_not_installed(self):
        b=method('entity/EntityMudskipper','saveToBucketTag')['instructions']
        self.assertTrue(calls(b,'.copyTag('));self.assertTrue(calls(b,'CompoundTag.put('))
        self.assertEqual(len(calls(b,'ItemStack.set(')),1)
        self.assertTrue(calls(b,'DataComponents.CUSTOM_NAME'));self.assertFalse(any('CUSTOM_DATA' in str(i['operand']) for i in b if i['opcode']=='0xb6' and '.set(' in str(i['operand'])))
if __name__=='__main__':unittest.main()
