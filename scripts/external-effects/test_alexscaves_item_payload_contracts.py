"""Item payload invariants are checked against independent pinned method bodies."""
import copy
import unittest

from assemble_authored_contracts import render
from catalog_common import OUT, read_json
from promote_combat_batch import validate_batch


def body(name, method, scope='item-payloads'):
    witness = next(w for w in read_json(OUT / f'native-evidence/alexscaves-{scope}.json')['witnesses']
                   if w['entry'].endswith('/' + name + '.class'))
    return next(m['instructions'] for m in witness['methods'] if m['name'] == method)


class ItemPayloadContractsTests(unittest.TestCase):
    def test_deterministic_render_and_pinned_consumers(self):
        batch = read_json(OUT / 'alexscaves-r2m8p-item-payload-contracts.json')
        self.assertEqual(batch, render(read_json(OUT / 'native-findings/alexscaves-item-payload-contracts.json')))
        review = copy.deepcopy(read_json(OUT / 'mod-reviews/alexscaves.json'))
        ids = {r['id'] for r in batch['effects']}
        review['effects'] = [r for r in review['effects'] if r['id'] not in ids]
        review['paths'] = [p for p in review['paths'] if not ids.intersection(p['effect_ids'])]
        result = validate_batch(batch, review, read_json(OUT / 'alexscaves-combat-census.json'))
        self.assertEqual(result['semantic_records'], len(review['effects']) + 18)

    def test_zero_request_does_not_gate_ice_cream_effect_removal(self):
        for name in ('GuanoEntity', 'ThrownIceCreamScoopEntity'):
            b = body(name, 'onHitEntity')
            n = next(n for n, i in enumerate(b) if '.hurt(' in str(i['operand']))
            self.assertEqual(b[n - 1]['operand'], 0.0)
            self.assertEqual(b[n + 1]['opcode'], '0x57')
        self.assertIn('.removeAllEffects(', str(body('ThrownIceCreamScoopEntity', 'onHitEntity')))

    def test_desolate_item_has_no_player_id_consumer(self):
        b = body('DesolateDaggerItem', 'hurtEnemy', 'item-consumers')
        self.assertIn('.setTargetId(', str(b))
        self.assertNotIn('.setPlayerId(', str(b))
        census = read_json(OUT / 'alexscaves-combat-census.json')
        self.assertFalse(any('DesolateDaggerEntity.setPlayerId(' in census['symbols'][site[2]]
                             for m in census['methods'] for site in m['calls']))
        for method in ('readAdditionalSaveData', 'addAdditionalSaveData'):
            self.assertEqual(body('DesolateDaggerEntity', method),
                             [{'offset': 0, 'opcode': '0xb1', 'operand': None}])

    def test_depth_charge_tick_does_not_dispatch_entity_hits(self):
        b = body('DepthChargeEntity', 'tick')
        self.assertIn('.baseTick(', str(b))
        self.assertNotIn('ThrowableItemProjectile.tick(', str(b))
        self.assertNotIn('ProjectileUtil.', str(b))
        self.assertNotIn('.onHit(', str(b))
        n = next(n for n, i in enumerate(b) if i['opcode'] == '0x10' and i['operand'] == 30)
        self.assertEqual(b[n + 1]['opcode'], '0xa4')

    def test_dark_arrow_requires_accepted_hurt_to_fade(self):
        b = body('DarkArrowEntity', 'onHitEntity')
        n = next(n for n, i in enumerate(b) if '.hurt(' in str(i['operand']))
        self.assertEqual(b[n + 1]['opcode'], '0x99')
        self.assertEqual(sum('.isAlliedTo(' in str(i['operand']) for i in b), 2)
        self.assertNotIn('AbstractArrow.onHitEntity(', str(b))

    def test_extinction_burn_precedes_hurt_and_spirit_depends_on_return(self):
        b = body('ExtinctionSpearEntity', 'onHitEntity')
        burn = next(n for n, i in enumerate(b) if '.igniteForSeconds(' in str(i['operand']))
        hurt = next(n for n, i in enumerate(b) if '.hurt(' in str(i['operand']))
        summon = next(n for n, i in enumerate(b) if '.addFreshEntity(' in str(i['operand']))
        self.assertLess(burn, hurt)
        self.assertLess(hurt, summon)
        self.assertEqual(b[hurt + 1]['opcode'], '0x99')

    def test_hook_contact_and_proximity_requests_are_distinct(self):
        self.assertNotIn('.hurt(', str(body('CandyCaneHookEntity', 'onHitEntity')))
        b = body('CandyCaneHookEntity', 'tick')
        n = next(n for n, i in enumerate(b) if '.hurt(' in str(i['operand']))
        self.assertEqual(b[n + 1]['opcode'], '0x57')
        # Native scale(1) branch does not normalize the fling vector.
        self.assertNotIn('.normalize(', str(body('CandyCaneHookEntity', 'fling')))

    def test_custom_explosion_hurt_does_not_gate_control(self):
        for name in ('FrostmintExplosion', 'TotemExplosion'):
            b = body(name, 'explode', 'item-extra')
            n = next(n for n, i in enumerate(b) if '.hurt(' in str(i['operand']))
            self.assertEqual(b[n + 1]['opcode'], '0x57')
            self.assertIn('.setDeltaMovement(', str(b))
            dampener = body(name, 'getExplosionKnockbackAfterDampener', 'item-extra')
            self.assertEqual([i['opcode'] for i in dampener], ['0x27', '0xaf'])
        self.assertIn('.setTicksFrozen(', str(body('FrostmintExplosion', 'explode', 'item-extra')))

    def test_totem_does_not_apply_collected_terrain_destruction(self):
        b = body('TotemExplosion', 'finalizeExplosion', 'item-extra')
        self.assertNotIn('.setBlock(', str(b))
        self.assertNotIn('.destroyBlock(', str(b))
        self.assertNotIn('.getDrops(', str(b))
        b = body('TotemOfPossessionItem', 'onUseTick', 'item-consumers')
        attack = next(n for n, i in enumerate(b) if 'Player.attack(' in str(i['operand']))
        reset = next(n for n, i in enumerate(b) if '.resetAttackStrengthTicker(' in str(i['operand']))
        self.assertLess(attack, reset)

    def test_soda_rocket_explode_is_event_and_discard_only(self):
        b = body('SodaBottleRocketEntity', 'explode')
        calls = [str(i['operand']) for i in b if i['opcode'] in ('0xb6', '0xb7', '0xb8', '0xb9')]
        self.assertTrue(any('.discard(' in c for c in calls))
        self.assertFalse(any('.hurt(' in c or 'Explosion' in c for c in calls))


if __name__ == '__main__':
    unittest.main()
