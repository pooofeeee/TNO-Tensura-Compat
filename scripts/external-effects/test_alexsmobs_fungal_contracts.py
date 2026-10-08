"""Pinned fungal payload ordering, ineffective writes and native lifecycle gates."""
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
class FungalContracts(unittest.TestCase):
    def test_exact_render_and_numeric_identity(self):
        b=read_json(OUT/'alexsmobs-r2o8-fungal.json');self.assertEqual(render(read_json(OUT/'native-specifications/alexsmobs-fungal-contracts.json')),b)
        r=read_json(OUT/'mod-reviews/alexsmobs.json');ids={e['id'] for e in b['effects']}
        r['effects']=[e for e in r['effects'] if e['id'] not in ids];r['paths']=[p for p in r['paths'] if not set(p['effect_ids'])&ids]
        validate_batch(b,r,read_json(OUT/'alexsmobs-combat-census.json'));self.assertEqual(audit(dict(effects=b['effects']))['unresolved_numeric_labels'],0)
    def test_bunfungus_victim_motion_precedes_ignored_hurt(self):
        b=method('entity/EntityBunfungus','tick')['instructions'];h=calls(b,'.hurt(')
        self.assertEqual(len(h),2);self.assertLess(calls(b,'.launch(')[0]['offset'],h[0]['offset']);self.assertLess(calls(b,'.knockback(')[0]['offset'],h[1]['offset'])
        for i in h:self.assertEqual(b[b.index(i)+1]['opcode'],'0x57')
    def test_bunfungus_food_consumption_precedes_two_effects_and_heal(self):
        b=method('entity/EntityBunfungus','tick')['instructions'];s=calls(b,'.shrink(')[0];e=calls(b,'.addEffect(')
        self.assertEqual(len(e),2);self.assertLess(s['offset'],e[0]['offset']);self.assertLess(e[1]['offset'],calls(b,'.heal(')[-1]['offset'])
    def test_mungus_explode_has_no_damage_or_world_explosion(self):
        for name in ('explode','lambda$explode$0'):
            b=method('entity/EntityMungus',name)['instructions'];self.assertFalse(calls(b,'.hurt('));self.assertFalse(calls(b,'Level.explode('))
        self.assertTrue(calls(method('entity/EntityMungus','lambda$explode$0')['instructions'],'.setBlockAndUpdate('))
    def test_mungus_biome_setter_never_loads_container_parameter(self):
        b=method('entity/EntityMungus','setChunkBiomes')['instructions'];self.assertFalse(any(i.get('local_index')==2 for i in b));self.assertEqual(b[-1]['opcode'],'0xb1')
        self.assertFalse(calls(b,'.setBiomes('));self.assertTrue(calls(method('entity/EntityMungus','transformBiome')['instructions'],'.recreate('))
    def test_mungus_death_latch_is_before_operation(self):
        b=method('entity/EntityMungus','tickDeath')['instructions'];self.assertLess(calls(b,'.hasExplodedZ')[-1]['offset'],calls(b,'.explode(')[0]['offset'])
    def test_mungus_disabled_clock_has_only_negative_increment(self):
        b=method('entity/EntityMungus','baseTick')['instructions'];write=[i for i in b if i['opcode']=='0xb5' and '.mosquitoAttackCooldownI' in str(i['operand'])]
        self.assertEqual(len(write),2);self.assertEqual(next(i for i in b if i['offset']==132)['opcode'],'0x9c');self.assertEqual(next(i for i in b if i['offset']==132)['branch_target'],145)
    def test_flutter_capture_mutates_copy_without_component_installation(self):
        b=method('entity/EntityFlutter','getFishBucket')['instructions'];self.assertTrue(calls(b,'.copyTag('));self.assertTrue(calls(b,'CompoundTag.put('))
        component_sets=calls(b,'ItemStack.set(');self.assertEqual(len(component_sets),1);self.assertEqual(b[b.index(component_sets[0])-3]['operand'],'net/minecraft/core/component/DataComponents.CUSTOM_NAMELnet/minecraft/core/component/DataComponentType;')
        c=next(c for c in read_json(OUT/'vanilla-evidence/alexsmobs-aquatic-native-dispatch.json')['classes'] if c['class_name'].endswith('/CustomData'));self.assertTrue(calls(c['methods'][0]['instructions'],'CompoundTag.copy('))
    def test_pollen_homing_keeps_target_and_original_projectile_kernel(self):
        b=method('entity/EntityPollenBall','doBehavior')['instructions'];self.assertEqual(len(calls(b,'Mob.getTarget(')),2);self.assertTrue(calls(b,'.shoot('));self.assertFalse(calls(b,'.hurt('));self.assertFalse(calls(b,'.addEffect('));self.assertFalse(calls(b,'.isAlive('))
        self.assertEqual(method('entity/EntityPollenBall','getDamage')['instructions'][0]['operand'],3.0)
if __name__=='__main__':unittest.main()
