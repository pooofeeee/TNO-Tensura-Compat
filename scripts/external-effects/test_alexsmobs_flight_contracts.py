"""Pinned wind, fire, leash, delayed attack and native resource delivery gates."""
import unittest
from assemble_authored_contracts import render
from audit_numeric_labels import audit
from catalog_common import OUT,read_json
from promote_combat_batch import validate_batch
P='com/github/alexthe666/alexsmobs/'
RAW=read_json(OUT/'native-evidence/alexsmobs-remaining-actors.json')
def method(cls,name,desc=None):return next(m for w in RAW['witnesses'] if w['entry']==P+cls+'.class' for m in w['methods'] if m['name']==name and (not desc or m['descriptor']==desc))
def calls(b,s):return [i for i in b if s in str(i['operand'])]
class FlightContracts(unittest.TestCase):
    def test_exact_render_numeric_validation(self):
        b=read_json(OUT/'alexsmobs-r2oa-remaining-flight.json');self.assertEqual(render(read_json(OUT/'native-specifications/alexsmobs-remaining-flight-contracts.json')),b)
        r=read_json(OUT/'mod-reviews/alexsmobs.json');ids={e['id'] for e in b['effects']};r['effects']=[e for e in r['effects'] if e['id'] not in ids];r['paths']=[p for p in r['paths'] if not set(p['effect_ids'])&ids]
        validate_batch(b,r,read_json(OUT/'alexsmobs-combat-census.json'));self.assertEqual(audit(dict(effects=b['effects']))['unresolved_numeric_labels'],0)
    def test_gust_reload_reads_x_for_three_directions(self):
        b=method('entity/EntityGust','readAdditionalSaveData')['instructions'];self.assertEqual([i['operand'] for i in b if isinstance(i['operand'],str) and i['operand'].startswith('GustDir')],['GustDirX']*3)
    def test_gust_nearby_velocity_has_no_status_damage_or_team_gate(self):
        b=method('entity/EntityGust','tick')['instructions'];self.assertTrue(calls(b,'.setDeltaMovement('));self.assertTrue(calls(b,'.fallDistanceF'));self.assertFalse(calls(b,'.hurt('));self.assertFalse(calls(b,'.addEffect('));self.assertFalse(calls(b,'.isAlliedTo('))
    def test_sunbird_hurt_curse_depends_on_parent_acceptance(self):
        b=method('entity/EntitySunbird','hurt')['instructions'];self.assertEqual(calls(b,'.hurt(')[0]['opcode'],'0xb7');self.assertLess(calls(b,'.removeEffect(')[0]['offset'],calls(b,'.addEffect(')[0]['offset'])
        self.assertTrue(any(i['opcode']=='0x99' and i['branch_target']>calls(b,'.addEffect(')[0]['offset'] for i in b))
    def test_sunbird_scorch_is_fire_request(self):
        b=method('entity/EntitySunbird','tick')['instructions'];self.assertTrue(calls(b,'.igniteForSeconds('));self.assertFalse(calls(b,'.hurt('));self.assertFalse(calls(b,'.explode('))
    def test_spectre_legacy_leash_hook_has_no_native_caller(self):
        c=read_json(OUT/'alexsmobs-combat-census.json');self.assertFalse([i for m in c['methods'] for i in m['calls'] if 'tickLeash' in c['symbols'][i[2]]])
        files=['alexsmobs-aquatic-native-dispatch.json','alexsmobs-leash-dispatch.json'];declarations=[c for f in files for c in read_json(OUT/'vanilla-evidence'/f)['classes']]
        for cls in ('Entity','LivingEntity','Mob','PathfinderMob','AgeableMob','Animal'):
            c=next(c for c in declarations if c['class_name'].endswith('/'+cls));self.assertTrue(c['declared_methods']);self.assertFalse([m for m in c['declared_methods'] if m['name']=='tickLeash'])
    def test_endergrade_flower_break_has_no_grief_rule(self):
        b=method('entity/ai/EndergradeAIBreakFlowers','pollinate')['instructions'];self.assertTrue(calls(b,'.destroyBlock('));self.assertFalse(calls(b,'RULE_MOBGRIEFING'))
    def test_vulture_cooldown_precedes_damage_and_heal_is_acceptance_gated(self):
        b=method('entity/EntitySoulVulture$AITackleMelee','tick')['instructions'];h=calls(b,'.hurt(')[0];n=b.index(h);self.assertEqual(b[n+1]['opcode'],'0x99');self.assertGreater(b[n+1]['branch_target'],calls(b,'.heal(')[0]['offset']);self.assertLess(calls(b,'.tackleCooldownI')[-1]['offset'],h['offset'])
    def test_cosmaw_arms_without_immediate_damage_and_ignores_delayed_hurt(self):
        b=method('entity/EntityCosmaw','doHurtTarget')['instructions'];self.assertFalse(calls(b,'.hurt('));self.assertEqual(b[-2]['operand'],1)
        b=method('entity/EntityCosmaw','tick')['instructions'];h=calls(b,'.hurt(')[0];self.assertEqual(b[b.index(h)+1]['opcode'],'0x57');self.assertLess(calls(b,'.readAdditionalSaveData(')[0]['offset'],h['offset'])
    def test_cosmaw_no_safe_ground_fallback_add_is_discarded(self):
        b=method('entity/EntityCosmaw','tick')['instructions'];a=[i for i in b if 'Vec3.add(' in str(i['operand'])];self.assertEqual(len(a),2)
        for i in a:self.assertEqual(b[b.index(i)+1]['opcode'],'0x57')
    def test_cod_bucket_state_is_written_only_into_copy(self):
        b=method('entity/EntityCosmicCod','saveToBucketTag')['instructions'];self.assertTrue(calls(b,'.copyTag('));self.assertTrue(calls(b,'CompoundTag.put('));self.assertEqual(len(calls(b,'ItemStack.set(')),1);self.assertFalse(calls(b,'CustomData.set('))
    def test_cod_teleport_returns_pre_event_coordinates(self):
        b=method('entity/EntityCosmicCod','teleport','()Lnet/minecraft/world/phys/Vec3;')['instructions'];self.assertTrue(calls(b,'Vec3.<init>'));self.assertFalse(calls(b,'getTargetX'))
        b=method('entity/EntityCosmicCod','teleport','(DDD)Z')['instructions'];self.assertLess(calls(b,'.playSound(')[0]['offset'],calls(b,'.onEnderTeleport(')[0]['offset']);self.assertTrue(calls(b,'.getTargetX('))
    def test_cosmaw_cod_loot_suppression_has_active_vanilla_key(self):
        c=next(c for c in read_json(OUT/'vanilla-evidence/twilight-giants-tools.json')['classes'] if c['class_name']=='net/minecraft/world/entity/Mob');b=next(m for m in c['methods'] if m['name']=='readAdditionalSaveData')['instructions'];self.assertTrue(calls(b,'DeathLootTable'));self.assertTrue(calls(b,'Mob.lootTableLnet/minecraft/resources/ResourceKey;'))
if __name__=='__main__':unittest.main()
