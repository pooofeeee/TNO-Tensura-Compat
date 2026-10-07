"""Native-side assertions for magnetic movement, packet admission and carriers."""
import copy
import unittest

from catalog_common import OUT,read_json
from assemble_authored_contracts import render
from promote_combat_batch import validate_batch

P='com/github/alexmodguy/alexscaves/'


def native(short,name,packet='magnet-contract'):
    d=read_json(OUT/f'native-evidence/alexscaves-{packet}.json')
    w=next(w for w in d['witnesses'] if w['entry']==P+short+'.class')
    return next(m for m in w['methods'] if m['name']==name)['instructions']


class MagneticContractsTests(unittest.TestCase):
    def test_authored_batch_regenerates_and_validates(self):
        spec=read_json(OUT/'native-findings/alexscaves-magnet-contracts.json')
        b=read_json(OUT/'alexscaves-r2m8e-magnetic-contracts.json')
        self.assertEqual(render(spec),b)
        before=copy.deepcopy(read_json(OUT/'mod-reviews/alexscaves.json'))
        ids={r['id'] for r in b['effects']};before['effects']=[r for r in before['effects'] if r['id'] not in ids]
        before['paths']=[r for r in before['paths'] if not set(r['effect_ids'])&ids]
        s=validate_batch(b,before,read_json(OUT/'alexscaves-combat-census.json'))
        self.assertGreaterEqual(s['semantic_records'],12)

    def test_field_is_native_accumulation_not_effect_amplifier(self):
        body=native('server/entity/util/MagnetUtil','tickMagnetism')
        at={i['offset']:i for i in body}
        self.assertEqual([at[n]['operand'] for n in (434,442,1000)], [.5,.04,.07999999821186066])
        self.assertTrue(all('Vec3.scale' in at[n]['operand'] for n in (437,445,1003)))
        self.assertNotIn('getAmplifier',str(body))
        self.assertFalse(any('.hurt(' in str(i['operand']) for i in body))
        pull=native('server/entity/util/MagnetUtil','isPulledByMagnets')
        self.assertIn('MAGNETIC_ITEMS',str(pull));self.assertIn('MAGNETIC_BLOCKS',str(pull))

    def test_native_direction_change_vector_and_state_are_distinct(self):
        body=native('server/entity/util/MagnetUtil','tickMagnetism');at={i['offset']:i for i in body}
        self.assertEqual([at[n]['operand'] for n in (955,956,959)], [0.,.4000000059604645,0.])
        jump=native('mixin/EntityMixin','postMagnetJump')
        self.assertEqual(jump[1]['operand'],20)
        controls=native('server/entity/util/MagnetUtil','processMovementControls')
        self.assertIn('Attributes.MOVEMENT_SPEED',str(controls));self.assertIn(.98,[i['operand'] for i in controls])

    def test_packet_does_not_claim_owner_identity_or_cosmetic_only(self):
        body=native('server/message/UpdateEffectVisualityEntityMessage','lambda$handle$0')
        calls=[str(i['operand']) for i in body]
        self.assertTrue(any('.addEffect(' in c for c in calls));self.assertTrue(any('.removeEffect(' in c for c in calls))
        self.assertIn(32.,[i['operand'] for i in body])
        for effect in ('IRRADIATED','BUBBLED','MAGNETIZING','STUNNED'):
            self.assertTrue(any('ACEffectRegistry.'+effect in c for c in calls))
        jumping=native('server/message/PlayerJumpFromMagnetMessage','lambda$handleServer$0')
        self.assertIn('MagnetUtil.isPulledByMagnets',str(jumping));self.assertIn('LivingEntity.setJumping',str(jumping))
        self.assertNotIn('Player.getId',str(jumping))

    def test_powered_block_strength_and_falling_path_are_separate(self):
        body=native('server/block/blockentity/MagnetBlockEntity','pushEntity')
        self.assertIn(.20000000298023224,[i['operand'] for i in body])
        self.assertIn(.03999999910593033,[i['operand'] for i in body])
        self.assertIn('setPlacementCooldown',str(body));self.assertIn('setFallBlockingTime',str(body))
        range_body=native('server/block/blockentity/MagnetBlockEntity','getEffectiveRange')
        self.assertIn(64,[i['operand'] for i in range_body]);self.assertIn('Mth.clamp',str(range_body))

    def test_carrier_damage_is_not_invented_and_native_retry_survives(self):
        body=native('server/entity/item/AbstractMovingBlockEntity','tick','magnet-payload')
        self.assertFalse(any('.hurt(' in str(i['operand']) for i in body))
        self.assertIn(.98,[i['operand'] for i in body]);self.assertIn(10,[i['operand'] for i in body])
        self.assertIn('loadWithComponents',str(body));self.assertIn('RemovalReason.KILLED',str(body))
        carry=native('server/entity/item/AbstractMovingBlockEntity','moveEntitiesOnTop','magnet-payload')
        self.assertIn('Attributes.GRAVITY',str(carry));self.assertIn('MoverType.SHULKER',str(carry))

    def test_wrong_native_candidate_offset_is_rejected(self):
        b=copy.deepcopy(read_json(OUT/'alexscaves-r2m8e-magnetic-contracts.json'))
        row=next(r for r in b['effects'] if r['id']=='alexscaves:magnetic_field')
        row['scalable_parameter_candidates'][0]['native_consumer']['offset']=-1
        before=copy.deepcopy(read_json(OUT/'mod-reviews/alexscaves.json'))
        ids={r['id'] for r in b['effects']};before['effects']=[r for r in before['effects'] if r['id'] not in ids]
        before['paths']=[r for r in before['paths'] if not set(r['effect_ids'])&ids]
        with self.assertRaises((AssertionError,StopIteration)):
            validate_batch(b,before,read_json(OUT/'alexscaves-combat-census.json'))


if __name__=='__main__':unittest.main()
