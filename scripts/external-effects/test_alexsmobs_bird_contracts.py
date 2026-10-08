"""Native bird attribution, control gates, resource ordering and persistence."""
import unittest
from assemble_authored_contracts import render
from audit_numeric_labels import audit
from catalog_common import OUT,read_json
from promote_combat_batch import validate_batch
P='com/github/alexthe666/alexsmobs/'
RAW=read_json(OUT/'native-evidence/alexsmobs-remaining-actors.json')
def method(cls,name):
    return next(m for w in RAW['witnesses'] if w['entry']==P+cls+'.class' for m in w['methods'] if m['name']==name)
def calls(b,s):return [i for i in b if s in str(i['operand'])]
class BirdContracts(unittest.TestCase):
    def test_exact_render_numeric_validation(self):
        b=read_json(OUT/'alexsmobs-r2o7-birds.json');self.assertEqual(render(read_json(OUT/'native-specifications/alexsmobs-bird-contracts.json')),b)
        r=read_json(OUT/'mod-reviews/alexsmobs.json');ids={e['id'] for e in b['effects']}
        r['effects']=[e for e in r['effects'] if e['id'] not in ids];r['paths']=[p for p in r['paths'] if not set(p['effect_ids'])&ids]
        validate_batch(b,r,read_json(OUT/'alexsmobs-combat-census.json'));self.assertEqual(audit(dict(effects=b['effects']))['unresolved_numeric_labels'],0)
    def test_blue_jay_and_crow_damage_has_generic_source(self):
        for cls in ('BlueJayAIMelee','CrowAIMelee'):
            b=method('entity/ai/'+cls,'tick')['instructions'];self.assertTrue(calls(b,'.generic('));self.assertFalse(calls(b,'.mobAttack('))
            for h in calls(b,'.hurt('):self.assertEqual(b[b.index(h)+1]['opcode'],'0x57')
    def test_blue_highlight_is_enemy_predicate_and_no_owner_filter(self):
        b=method('entity/EntityBlueJay','lambda$static$0')['instructions'];self.assertTrue(calls(b,'net/minecraft/world/entity/monster/Enemy'))
        b=method('entity/EntityBlueJay','highlightMonsters')['instructions'];self.assertTrue(calls(b,'.addEffect('));self.assertFalse(calls(b,'.isAlliedTo('));self.assertFalse(calls(b,'.hasLineOfSight('))
    def test_crow_perch_clock_resets_before_later_command_gate(self):
        b=method('entity/EntityCrow','tick')['instructions'];self.assertEqual(next(i['operand'] for i in b if i['offset']==656),50)
        self.assertEqual(next(i['operand'] for i in b if i['offset']==703),3)
        writes=[i for i in b if i['opcode']=='0xb5' and '.checkPerchCooldownI' in str(i['operand'])]
        self.assertTrue(any(656<i['offset']<703 for i in writes))
    def test_crow_crop_mutation_has_grief_rule(self):
        b=method('entity/ai/CrowAICircleCrops','destroyCrop')['instructions'];self.assertTrue(calls(b,'RULE_MOBGRIEFING'))
        self.assertTrue(calls(b,'.setBlockAndUpdate('));self.assertTrue(calls(b,'.destroyBlock('));self.assertFalse(calls(b,'.heal('))
    def test_seagull_food_random_bound_excludes_last(self):
        b=method('entity/ai/SeagullAIStealFromPlayers','getFoodItemFrom')['instructions'];h=calls(b,'.nextInt(')[0]
        self.assertEqual(b[b.index(h)-1]['opcode'],'0x64');self.assertEqual(b[b.index(h)-2]['operand'],1)
    def test_seagull_map_flag_is_never_assigned_true(self):
        b=method('entity/EntitySeagull','setDataFromTreasureMap')['instructions'];stores=[i for i in b if i['opcode'] in ('0x36','0x3d') and i.get('local_index')==2]
        self.assertEqual(len(stores),1);self.assertEqual(b[b.index(stores[0])-1]['operand'],0)
        self.assertFalse(calls(b,'.setTreasurePos('))
    def test_shoebill_knockback_precedes_ignored_hurt(self):
        b=method('entity/EntityShoebill','tick')['instructions'];h=calls(b,'.hurt(')[0];self.assertLess(calls(b,'.knockback(')[0]['offset'],h['offset']);self.assertEqual(b[b.index(h)+1]['opcode'],'0x57')
    def test_eagle_small_prey_mount_precedes_large_damage_branch(self):
        b=method('entity/EntityBaldEagle$AITackle','tick')['instructions'];self.assertLess(calls(b,'.startRiding(')[0]['offset'],calls(b,'.hurt(')[0]['offset'])
    def test_eagle_direct_damage_formula_retains_ceil_and_cooldown(self):
        b=method('entity/EntityBaldEagle','directFromPlayer')['instructions'];self.assertTrue(calls(b,'Math.ceil('));self.assertTrue(calls(b,'Mth.clamp('));h=calls(b,'.hurt(')[0];self.assertEqual(b[b.index(h)+1]['opcode'],'0x57')
        self.assertEqual(next(i['operand'] for i in b if i['offset']==665),22)
    def test_eagle_forcing_body_never_unforces(self):
        b=method('entity/EntityBaldEagle','loadChunkOnServer')['instructions'];h=calls(b,'.setChunkForced(')[0];self.assertEqual(b[b.index(h)-1]['operand'],1)
    def test_eagle_taming_branch_has_no_existing_owner_gate(self):
        b=method('entity/EntityBaldEagle','mobInteract')['instructions'];h=calls(b,'.tame(')[0];self.assertFalse(calls(b[:b.index(h)],'.isOwnedBy('));self.assertFalse(calls(b[:b.index(h)],'.isTame('))
if __name__=='__main__':unittest.main()
