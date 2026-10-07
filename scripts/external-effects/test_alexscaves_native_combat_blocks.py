"""Bounded block contracts tested against independently captured pinned bodies."""
import copy
import unittest
from assemble_authored_contracts import render
from catalog_common import OUT,read_json
from promote_combat_batch import validate_batch

def body(cls,name):
    w=next(w for w in read_json(OUT/'native-evidence/alexscaves-combat-blocks.json')['witnesses'] if w['entry'].endswith('/'+cls+'.class'))
    return next(m['instructions'] for m in w['methods'] if m['name']==name)

class BlockTests(unittest.TestCase):
    def test_render_and_independent_consumers(self):
        b=read_json(OUT/'alexscaves-r2m8r-native-combat-blocks.json')
        self.assertEqual(b,render(read_json(OUT/'native-findings/alexscaves-native-combat-blocks.json')))
        r=copy.deepcopy(read_json(OUT/'mod-reviews/alexscaves.json'));ids={e['id'] for e in b['effects']}
        r['effects']=[e for e in r['effects'] if e['id'] not in ids];r['paths']=[e for e in r['paths'] if not ids.intersection(e['effect_ids'])]
        self.assertEqual(validate_batch(b,r,read_json(OUT/'alexscaves-combat-census.json'))['status'],'PASS')
    def test_magma_burn_is_independent_of_hurt_acceptance(self):
        for cls,name in [('PrimalMagmaBlock','stepOn'),('PrimalMagmaBlock','entityInside'),('VolcanicCoreBlock','stepOn')]:
            b=body(cls,name);n=next(n for n,i in enumerate(b) if '.hurt(' in str(i['operand']))
            self.assertEqual(b[n+1]['opcode'],'0x57');self.assertIn('.igniteForSeconds(',str(b))
    def test_acid_armor_wear_precedes_damage(self):
        b=body('AcidBlock','entityInside')
        self.assertLess(next(n for n,i in enumerate(b) if '.hurtAndBreak(' in str(i['operand'])),next(n for n,i in enumerate(b) if '.hurt(' in str(i['operand'])))
        self.assertIn('.getWornAmount(',str(b))
    def test_tesla_manual_callback_and_fire_clear_are_preserved(self):
        b=body('TeslaBulbBlockEntity','tick');calls=[str(i['operand']) for i in b]
        self.assertEqual(sum('.thunderHit(' in s for s in calls),2)
        self.assertEqual(sum('.setRemainingFireTicks(' in s for s in calls),2)
        self.assertTrue(any('.setVisualOnly(' in s for s in calls))
        # Shared pinned loader behavior consumes the configured bolt damage.
        w=next(w for w in read_json(OUT/'reference-evidence/friends-loader-244.json')['witnesses'] if w['entry']=='net/minecraft/world/entity/Entity.class')
        m=next(m for m in w['methods'] if m['name']=='thunderHit')
        self.assertIn('LightningBolt.getDamage()F',str(m['instructions']))
    def test_furnace_resets_waste_before_cloud_amplifier_query(self):
        b=body('NuclearFurnaceBlockEntity','destroyWhileCritical')
        self.assertLess(next(n for n,i in enumerate(b) if i['opcode']=='0xb5' and '.currentWasteI' in str(i['operand'])),next(n for n,i in enumerate(b) if '.getCriticality(' in str(i['operand'])))
        self.assertNotIn('.setOwner(',str(b))
    def test_terrain_payloads_do_not_invent_source_owners(self):
        b=body('VolcanicCoreBlockEntity','spawnTephra');self.assertNotIn('.setOwner(',str(b));self.assertIn('.setArcingTowards(',str(b))
        b=body('PurpleSodaBlock','neighborChanged');self.assertIn('FrostmintExplosion.<init>',str(b));self.assertIn('.finalizeExplosion(',str(b))
    def test_global_spawn_equipment_admission_is_checked_once(self):
        w=next(w for w in read_json(OUT/'native-evidence/alexscaves-forlorn-context.json')['witnesses'] if w['entry'].endswith('/CommonEvents.class'))
        b=next(m['instructions'] for m in w['methods'] if m['name']=='onEntityJoinWorld')
        equips=[n for n,i in enumerate(b) if '.setItemSlot(' in str(i['operand'])]
        empty=[n for n,i in enumerate(b) if '.isEmpty(' in str(i['operand'])]
        self.assertEqual(len(empty),4);self.assertEqual(len(equips),4);self.assertLess(max(empty),min(equips))

if __name__=='__main__':unittest.main()
