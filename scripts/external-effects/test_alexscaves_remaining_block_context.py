"""Independent native callback facts for the finite remaining block scope."""
import copy
import unittest
from catalog_common import OUT, read_json
from assemble_authored_contracts import render
from promote_combat_batch import validate_batch


def body(cls, name):
    w=next(w for w in read_json(OUT/'native-evidence/alexscaves-remaining-block-context.json')['witnesses']
           if w['entry'].endswith('/'+cls+'.class'))
    return next(m['instructions'] for m in w['methods'] if m['name']==name)


class RemainingBlockTests(unittest.TestCase):
    def test_exact_render_and_native_contracts(self):
        b=read_json(OUT/'alexscaves-r2m8w-remaining-native-block-context.json')
        self.assertEqual(b,render(read_json(OUT/'native-findings/alexscaves-remaining-native-block-context.json')))
        r=copy.deepcopy(read_json(OUT/'mod-reviews/alexscaves.json'))
        ids={e['id'] for e in b['effects']}
        r['effects']=[e for e in r['effects'] if e['id'] not in ids]
        r['paths']=[e for e in r['paths'] if not ids.intersection(e['effect_ids'])]
        self.assertEqual(validate_batch(b,r,read_json(OUT/'alexscaves-combat-census.json'))['status'],'PASS')

    def test_final_monolith_roll_has_no_second_filter(self):
        b=body('AmberMonolithBlockEntity','getDepopulatedEntitySpawnData')
        gates=[i for i in b if '.isEntitySpawnBlocked(' in str(i['operand'])]
        choices=[i for i in b if '.getEntitySpawnSettingsForBiome(' in str(i['operand'])]
        self.assertEqual(len(gates),1); self.assertEqual(len(choices),1)
        self.assertLess(gates[0]['offset'],choices[0]['offset'])
        # Loop exit returns the latest local, without another admission call.
        self.assertEqual([i['opcode'] for i in b[-2:]],['0x19','0xb0'])
        self.assertFalse(any('isEntitySpawnBlocked' in str(i['operand'])
                             for i in b if i['offset']>choices[0]['offset']))

    def test_monolith_native_spawn_modes_and_ownerless_request(self):
        b=str(body('AmberMonolithBlockEntity','spawnMobs'))
        for s in ('MobSpawnType.SPAWNER','MobSpawnType.CHUNK_GENERATION',
                  '.finalizeSpawn(','.addFreshEntityWithPassengers('):self.assertIn(s,b)
        for s in ('.setOwner(','.hurt(','.addEffect(','.explode('):self.assertNotIn(s,b)
        d=str(body('AmberMonolithBlockEntity','getDisplayEntity'))
        self.assertIn('EntityType.create(',d);self.assertNotIn('.addFreshEntity',d)

    def test_quarry_lightning_is_a_particle_not_an_actor(self):
        b=str(body('QuarryBlockEntity','spawnLightningBetween'))
        self.assertIn('QUARRY_BORDER_LIGHTING',b);self.assertIn('.addParticle(',b)
        for s in ('LightningBolt','.addFreshEntity','.thunderHit(','.hurt('):self.assertNotIn(s,b)
        t=str(body('QuarryBlockEntity','tick'))
        self.assertIn('.setQuarryPos(',t);self.assertIn('.setInactive(',t)

    def test_radrock_native_hazard_producer_order_and_gate(self):
        b=body('AcidicRadrockBlock','playerDestroy');s=str(b)
        self.assertIn('SILK_TOUCH',s);self.assertIn('ACBlockRegistry.ACID',s)
        parent=next(i['offset'] for i in b if 'Block.playerDestroy(' in str(i['operand']))
        write=next(i['offset'] for i in b if '.setBlockAndUpdate(' in str(i['operand']))
        self.assertLess(parent,write);self.assertNotIn('.hurt(',s)

    def test_ordinary_flytrap_and_unsupported_scaffold_have_no_attack(self):
        for cls in ('FlytrapBlock','PottedFlytrapBlock'):
            b=str(body(cls,'randomTick'));self.assertIn('.scheduleTick(',b)
            self.assertNotIn('.hurt(',b);self.assertNotIn('.addEffect(',b)
        b=str(body('MetalScaffoldingBlock','tick'))
        self.assertIn('FallingBlockEntity.fall(',b);self.assertNotIn('.setHurtsEntities(',b)


if __name__=='__main__':unittest.main()
