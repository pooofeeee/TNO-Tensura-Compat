"""Shared native weapon harness with independent pinned consumer assertions."""
import copy
import unittest

from catalog_common import OUT, read_json
from promote_combat_batch import (damage_source_binding, literal_item_attribute_binding,
                                 validate_batch)
from test_shadow_clone_contracts import NativeContractHarness


class NativeAbyssItemContracts(NativeContractHarness, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch = read_json(OUT / 'arphex-r2m6b-residual-abyss-item-contracts.json')
        cls.native = read_json(OUT / 'native-evidence/arphex-residual-abyss-items.json')
        cls.census = read_json(OUT / 'arphex-combat-census.json')

    def test_bounded_contracts_and_parameters_validate(self):
        validate_batch(self.batch, self.prior(), self.census)
        self.assertEqual(len(self.batch['effects']), 7)
        self.assertEqual(len(self.batch['closed_item_callback_entries']), 8)
        self.assertEqual(sum(len(c['parameters']) for r in self.batch['effects']
                             for c in r['scalable_parameter_candidates']), 56)
        self.assertEqual((len(self.native['witnesses']), sum(len(w['methods'])
                         for w in self.native['witnesses'])), (36, 176))
        self.assertFalse(self.batch['whole_mod_complete'])

    def test_native_mainhand_modifiers_have_exact_values_operation_and_slots(self):
        expected = {'AbyssAscendantItem': 27., 'AscendedTormentItem': 59.,
                    'AbyssalBladeItem': 14., 'AbyssalDaggerItem': 7.,
                    'AbyssAtomiserItem': 15.}
        for name, value in expected.items():
            m = dict(instructions=self.body(name, '<init>'))
            offset = next(i['offset'] for i in m['instructions']
                          if 'AttributeModifier.<init>(' in str(i['operand']))
            binding = literal_item_attribute_binding(m, offset)
            self.assertEqual(binding['native_value'], value)
            self.assertIn('Attributes.ATTACK_DAMAGE', binding['attribute_symbol'])
            self.assertIn('ADD_VALUE', binding['operation_symbol'])
            self.assertIn('MAINHAND', binding['slot_symbol'])
        self.assertFalse(any('AttributeModifier' in str(i['operand'])
                             for i in self.body('InfiniteTormentItem', '<init>')))

    def test_digger_arguments_and_tier_bonus_are_distinct_native_facts(self):
        for name, damage, speed in [('AbyssalAxeItem', 18., -3.700000047683716),
                                    ('AbyssalPickaxeItem', 9., -3.)]:
            m = dict(instructions=self.body(name, '<init>'))
            binding = literal_item_attribute_binding(m, 18)
            self.assertEqual((binding['attack_bonus'], binding['attack_speed']), (damage, speed))
            self.assertEqual(self.body(name + '$1', 'getAttackDamageBonus')[0]['operand'], 0.)

    def test_false_attribute_value_or_role_is_rejected(self):
        batch = copy.deepcopy(self.batch)
        row = next(r for r in batch['effects'] if r['id'].endswith(':abyss_weapon_native_attribute_profiles'))
        row['components'][0]['numerical_parameters']['abyssascendant_attack_bonus'] = 28.
        with self.assertRaisesRegex(AssertionError, 'component differs from pinned item attribute'):
            validate_batch(batch, self.prior(), self.census)
        batch = copy.deepcopy(self.batch)
        row = next(r for r in batch['effects'] if r['id'].endswith(':abyss_weapon_native_attribute_profiles'))
        c = next(c for c in row['scalable_parameter_candidates']
                 if c['native_item_attribute_binding']['kind'] == 'DIGGER_ATTRIBUTE_ARGUMENTS')
        c['native_item_attribute_parameter_roles'] = {p: 'attack_bonus' for p in c['parameters']}
        with self.assertRaises(AssertionError):
            validate_batch(batch, self.prior(), self.census)

    def test_computed_item_modifier_is_not_accepted_as_literal(self):
        m = dict(instructions=copy.deepcopy(self.body('AbyssAscendantItem', '<init>')))
        next(i for i in m['instructions'] if i['offset'] == 34)['opcode'] = '0x63'
        with self.assertRaises(AssertionError):
            literal_item_attribute_binding(m, 40)

    def test_axe_post_hit_helper_gets_victim_not_attacker(self):
        b = self.body('AbyssalAxeItem', 'hurtEnemy')
        by = {i['offset']: i for i in b}
        self.assertIn('AxeItem.hurtEnemy(', by[4]['operand'])
        self.assertEqual((by[25]['opcode'], by[26]['opcode']), ('0x2c', '0x2b'))
        self.assertIn('AbyssalAxeRightClickProcedure.execute(', by[27]['operand'])
        self.assertFalse(any(i['opcode'].startswith('0x9') for i in b))

    def test_atomiser_post_hit_durability_uses_victim_and_returns_literal_true(self):
        b = self.body('AbyssAtomiserItem', 'hurtEnemy')
        self.assertEqual([i['opcode'] for i in b[:4]], ['0x2b', '0x5', '0x2c', '0x2c'])
        self.assertFalse(any(i['opcode'] == '0xb7' for i in b))
        self.assertEqual(b[-2]['operand'], 1)
        self.assertIn('AbyssalPickaxeLivingEntityIsHitWithToolProcedure', b[-3]['operand'])

    def test_shared_activation_helpers_have_identical_resolved_bodies(self):
        self.assertEqual(self.body('AbyssalAxeRightClickProcedure'),
                         self.body('AbyssalPickaxeRightclickedProcedure'))
        self.assertEqual(len(self.row('abyss_tools_native_activation_cooldown_and_night_vision')
                             ['scalable_parameter_candidates']), 2)

    def test_mining_fatigue_has_independent_vanilla_attack_speed_evidence(self):
        packet = read_json(OUT / 'vanilla-evidence/royal-final.json')
        cls = next(c for c in packet['classes'] if c['raw_entry'] == 'bsb.class')
        body = next(m['instructions'] for m in cls['methods'] if m['name'] == '<clinit>')
        by = {i['offset']: i for i in body}
        self.assertIn('ATTACK_SPEED', by[125]['operand'])
        self.assertEqual(by[133]['operand'], -.10000000149011612)
        self.assertIn('ADD_MULTIPLIED_TOTAL', by[136]['operand'])
        self.assertIn('DIG_SLOWDOWN', by[145]['operand'])
        self.assertTrue(any('MINING_FATIGUE' in c['primitive']
                            for r in self.batch['effects'] for c in r['scalable_parameter_candidates']))

    def test_infinite_selected_stop_precedes_self_exclusion_and_particle_limit(self):
        b = self.body('InfiniteTormentItemInHandTickProcedure')
        by = {i['offset']: i for i in b}
        self.assertIn('.setDeltaMovement(', by[382]['operand'])
        first_hurt = next(j for j, i in enumerate(b) if '.hurt(' in str(i['operand']))
        stop = next(j for j, i in enumerate(b) if '.setDeltaMovement(' in str(i['operand']))
        self.assertLess(stop, first_hurt)
        self.assertEqual(by[438]['opcode'], '0xb6')
        self.assertEqual(by[488]['opcode'], '0xb6')
        self.assertFalse(any('.getUseItem(' in str(i['operand']) for i in b))
        self.assertFalse(any('.isAlliedTo(' in str(i['operand']) for i in b))
        self.assertTrue(self.row('infinite_torment_native_selected_defense_and_area_requests')
                        ['binary_parameters']['particle_budget_not_target_limit'])

    def test_item_execution_source_profiles_and_factor_differ_from_incoming_contract(self):
        b = self.body('InfiniteTormentLivingEntityIsHitWithItemProcedure')
        m = dict(instructions=b)
        bindings = [damage_source_binding(m, o) for o in (239, 291, 341, 391)]
        self.assertIn('MAGIC', bindings[0][0]); self.assertIn('GENERIC', bindings[1][0])
        self.assertTrue(all('Holder;Lnet/minecraft/world/entity/Entity;' in x[3]
                            for x in bindings[:2]))
        self.assertTrue(all('<init>(Lnet/minecraft/core/Holder;)V' in x[3]
                            for x in bindings[2:]))
        self.assertFalse(any('.removeAllEffects(' in str(i['operand']) or i['operand'] == 'force_death'
                             for i in b))
        for offset in (239, 291, 341, 391):
            at = next(j for j, i in enumerate(b) if i['offset'] == offset)
            self.assertEqual(b[at-2]['operand'], 10.)
        item = self.body('InfiniteTormentItem', 'hurtEnemy')
        self.assertEqual([i['opcode'] for i in item if i['offset'] in (25, 26)], ['0x2c', '0x2d'])

    def test_retry_chain_exact_bootstrap_edges_nine_quartets_and_ten_health_resets(self):
        entry = 'net/arphex/procedures/InfiniteTormentLivingEntityIsHitWithItemProcedure.class'
        w = next(w for w in self.native['witnesses'] if w['entry'] == entry)
        methods = {m['name']: m for m in w['methods']}
        bootstraps = {r['index']: r for r in self.census['registration_bootstraps'] if r['entry'] == entry}
        edges = {}
        for name, m in methods.items():
            edges[name] = []
            for i in m['instructions']:
                if i['opcode'] != '0xba': continue
                index = int(i['operand'].split('#')[1].split(':')[0])
                edges[name] += [a.split('.lambda$')[1].split('(')[0]
                                for a in bootstraps[index]['arguments'] if '.lambda$' in a]
        current = 'execute'; retry_names = []
        while True:
            next_retry = [name for name in edges[current]
                          if name.startswith('execute$') and int(name.split('$')[1]) >= 10
                          and int(name.split('$')[1]) <= 18]
            if not next_retry: break
            self.assertEqual(len(next_retry), 1)
            current = 'lambda$' + next_retry[0]; retry_names.append(current)
        self.assertEqual(retry_names, ['lambda$execute$' + str(n) for n in range(18, 9, -1)])
        for name in retry_names:
            self.assertEqual(sum('.hurt(' in str(i['operand']) for i in methods[name]['instructions']), 4)
        self.assertEqual(sum('.setHealth(' in str(i['operand']) for name, m in methods.items()
                             if name.startswith('lambda$') for i in m['instructions']), 10)
        self.assertFalse(any('.queueServerWork(' in str(i['operand']) and i['offset'] == 209
                             for i in methods[retry_names[-1]]['instructions']))

    def test_uncalled_axe_hit_helper_is_not_promoted_as_active_wither(self):
        symbol = 'net/arphex/procedures/AbyssalAxeLivingEntityIsHitWithToolProcedure.execute('
        self.assertFalse(any(symbol in self.census['symbols'][s]
                             for m in self.census['methods'] for _, _, s in m['calls']))
        self.assertFalse(any(symbol in str(a) for r in self.census['registration_bootstraps']
                             for a in r['arguments']))
        self.assertFalse(any(c['native_parameter_identity']['entry'].endswith(
                             '/AbyssalAxeLivingEntityIsHitWithToolProcedure.class')
                             for r in self.batch['effects'] for c in r['scalable_parameter_candidates']))


if __name__ == '__main__':
    unittest.main()
