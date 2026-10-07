"""Shared body/pickup refinements must preserve actual consumers and identity."""
import copy
import unittest
from catalog_common import OUT, read_json
from assemble_authored_contracts import render
from promote_combat_batch import validate_batch


def witness(name, scope):
    return next(w for w in read_json(OUT/f'native-evidence/alexscaves-{scope}.json')['witnesses']
                if w['entry'].endswith('/'+name+'.class'))


def body(name, method, scope='dinosaur-actors'):
    return next(m for m in witness(name,scope)['methods'] if m['name']==method)['instructions']


class SharedBodyTests(unittest.TestCase):
    def test_regeneration_and_refinements_reuse_existing_ids(self):
        b=read_json(OUT/'alexscaves-r2m8k-support-and-presentation.json')
        self.assertEqual(render(read_json(OUT/'native-findings/alexscaves-dinosaur-support-contracts.json')),b)
        r=copy.deepcopy(read_json(OUT/'mod-reviews/alexscaves.json'));ids={e['id'] for e in b['effects']}
        r['effects']=[e for e in r['effects'] if e['id'] not in ids]
        r['paths']=[e for e in r['paths'] if not set(e['effect_ids'])&ids]
        self.assertEqual(validate_batch(b,r,read_json(OUT/'alexscaves-combat-census.json'))['semantic_records'],len(r['effects'])+3)
        self.assertEqual(len(b['record_refinements']),5)
        self.assertFalse(ids&{e['id'] for e in b['record_refinements']})

    def test_debris_disables_parent_carry_and_placement(self):
        for name in ('FallingTreeBlockEntity','CrushedBlockEntity'):
            for method in ('movesEntities','canBePlaced'):
                self.assertEqual([i['opcode'] for i in body(name,method,'dinosaur-support')],['0x3','0xac'])
        b=body('AbstractMovingBlockEntity','tick','moving-block')
        self.assertIn('.movesEntities()Z',str(b));self.assertIn('.canBePlaced()Z',str(b))
        self.assertIn('MoverType.SELF',str(b));self.assertIn('loadWithComponents',str(b))
        self.assertNotIn('.hurt(',str(b));self.assertNotIn('.addEffect(',str(b))

    def test_parent_carry_preserves_native_gravity_and_shared_vehicle(self):
        b=body('AbstractMovingBlockEntity','moveEntitiesOnTop','moving-block')
        self.assertIn('NO_SPECTATORS',str(b));self.assertIn('MovingMetalBlockEntity',str(b))
        self.assertIn('Attributes.GRAVITY',str(b));self.assertIn('MoverType.SHULKER',str(b))
        self.assertNotIn('.hurt(',str(b))
        self.assertIn('isPassengerOfSameVehicle',str(body('AbstractMovingBlockEntity','lambda$moveEntitiesOnTop$0','moving-block')))

    def test_drop_target_predicate_formal_is_unused_not_invented(self):
        w=witness('MobTargetItemGoal','dinosaur-support')
        m=next(m for m in w['methods'] if m['name']=='<init>' and 'Lcom/google/common/base/Predicate;' in m['descriptor'])
        self.assertFalse(any(i.get('local_index')==5 and i['opcode'] in ('0x19','0x2a','0x2b','0x2c','0x2d') for i in m['instructions']))
        tick=body('MobTargetItemGoal','tick','dinosaur-support')
        self.assertIn('getMaxDistToItem()D',str(tick));self.assertIn('distanceToSqr',str(tick))
        self.assertIn('onGetItem',str(tick))

    def test_tame_feed_is_original_owner_gate_and_original_heal(self):
        b=body('VallumraptorEntity','onFeedMixture')
        self.assertIn('SERENE_SALAD',str(b));self.assertIn('getRelaxedFor',str(b));self.assertIn('isTame',str(b))
        self.assertIn('tame(Lnet/minecraft/world/entity/player/Player;)',str(b))
        self.assertIn('setOrderedToSit',str(b));self.assertIn(5.0,[i['operand'] for i in b])
        self.assertNotIn('isClientSide',str(b))


if __name__=='__main__':
    unittest.main()
