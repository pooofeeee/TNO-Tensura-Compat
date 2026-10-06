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


class NativeForceChaosCrusherContracts(NativeContractHarness, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch = read_json(OUT / 'arphex-r2m6c-native-force-chaos-crusher-contracts.json')
        cls.native = read_json(OUT / 'native-evidence/arphex-residual-force-chaos-crusher.json')
        cls.census = read_json(OUT / 'arphex-combat-census.json')

    def test_bounded_native_contracts_validate(self):
        validate_batch(self.batch, self.prior(), self.census)
        self.assertEqual(len(self.batch['effects']), 5)
        self.assertEqual(len(self.batch['closed_item_callback_entries']), 3)
        self.assertEqual(sum(len(c['parameters']) for r in self.batch['effects']
                             for c in r['scalable_parameter_candidates']), 58)
        self.assertEqual((len(self.native['witnesses']), sum(len(w['methods'])
                         for w in self.native['witnesses'])), (12, 78))
        self.assertFalse(self.batch['whole_mod_complete'])

    def test_force_source_actor_slot_changes_only_in_unarmored_selected_request(self):
        from promote_combat_batch import direct_damage_actor_local
        m = dict(instructions=self.body('ForceGauntletToolInHandTickProcedure'))
        self.assertEqual([direct_damage_actor_local(m, offset)
                          for offset in (2291, 2331, 2622, 2652)], [7, 7, 7, 17])
        b = m['instructions']
        self.assertEqual(sum('.hurt(' in str(i['operand']) for i in b), 4)
        for offset in (2291, 2622):
            at = next(j for j, i in enumerate(b) if i['offset'] == offset)
            self.assertEqual([i['opcode'] for i in b[at-4:at]], ['0x6c', '0x86', '0xb8', '0x86'])
            self.assertIn('Math.round(F)I', b[at-2]['operand'])

    def test_wrong_primary_or_auxiliary_actor_slot_is_rejected(self):
        for auxiliary in (False, True):
            batch = copy.deepcopy(self.batch)
            row = next(r for r in batch['effects'] if r['id'].endswith(':force_gauntlet_native_selected_lift_damage_and_motion'))
            candidate = next(c for c in row['scalable_parameter_candidates']
                             if c['parameters'] == ['selected_damage_base'])
            target = candidate['additional_consumer_sites'][0] if auxiliary else candidate
            target['native_damage_actor_local_index'] = 7 if auxiliary else 17
            with self.assertRaisesRegex(AssertionError, 'damage actor slot'):
                validate_batch(batch, self.prior(), self.census)

    def test_force_lift_request_precedes_strike_and_is_outside_force_power_block(self):
        b = self.body('ForceGauntletToolInHandTickProcedure')
        by = {i['offset']: i for i in b}
        self.assertIn('FORCE_LIFT', by[1776]['operand'])
        self.assertEqual((by[1779]['operand'], by[1780]['operand']), (3, 1))
        self.assertLess(1783, 2291)
        # The next ForcePower presence read is after the entire strike arm.
        self.assertFalse(any('FORCE_POWER' in str(i['operand']) for i in b
                             if 782 < i['offset'] < 2991))
        self.assertFalse(any('.isAlliedTo(' in str(i['operand']) for i in b))

    def test_swing_excludes_spectator_and_delivery_checks_only_using_flag(self):
        b = self.body('ForceGauntletEntitySwingsItemProcedure$1', 'checkGamemode')
        self.assertEqual(sum('.SPECTATOR' in str(i['operand']) for i in b), 2)
        self.assertFalse(any('.CREATIVE' in str(i['operand']) for i in b))
        b = self.body('ForceGauntletEntitySwingsItemProcedure', 'lambda$execute$0')
        strings = [i['operand'] for i in b if isinstance(i['operand'], str)]
        self.assertIn('usinggauntlet', strings); self.assertIn('firegauntlet', strings)
        self.assertFalse(any('.isAlive(' in value or '.isOnCooldown(' in value or
                             '.getMainHandItem(' in value for value in strings))

    def test_two_gauntlet_roots_forward_shared_callbacks_and_selected_distinct_actions(self):
        for root, selected in [('ForceGauntletItem', 'ForceGauntletToolInHandTickProcedure'),
                               ('ChaosGauntletItem', 'ChaosGauntletHeldProcedure')]:
            b = self.body(root, 'inventoryTick')
            self.assertEqual(sum(selected + '.execute(' in str(i['operand']) for i in b), 1)
            self.assertEqual(sum('ForceGauntletItemInInventoryTickProcedure.execute(' in str(i['operand']) for i in b), 1)
            self.assertTrue(any('ForceGauntletEntitySwingsItemProcedure.execute(' in str(i['operand'])
                                for i in self.body(root, 'onEntitySwing')))
        r = self.row('force_chaos_native_use_swing_and_charge_state')
        power = next(c for c in r['scalable_parameter_candidates'] if c['primitive'] == 'MOB_EFFECT_FORCE_POWER')
        self.assertEqual(len(power['additional_consumer_sites']), 1)

    def test_chaos_status_profiles_preserve_float_subtraction_and_distinct_mark_durations(self):
        b = self.body('ChaosGauntletHeldProcedure'); by = {i['offset']: i for i in b}
        self.assertEqual((by[5034]['operand'], by[9492]['operand'], by[10451]['operand']), (120000, 120000, 300))
        at = next(j for j, i in enumerate(b) if i['offset'] == 6477)
        self.assertEqual([i['opcode'] for i in b[at-5:at-3]], ['0x66', '0x8b'])
        self.assertFalse(any('.hurt(' in str(i['operand']) or '.setDeltaMovement(' in str(i['operand'])
                             or '.setOwner(' in str(i['operand']) for i in b))
        self.assertEqual(sum('CHAOS_CONTROLLED' in str(i['operand']) and i['opcode'] == '0xb2' for i in b), 5)
        self.assertEqual(sum('AABB.ofSize(' in str(i['operand']) for i in b), 21)

    def test_crusher_status_precedes_health_gate_and_cooldown_is_outside_grab_branch(self):
        b = self.body('CrusherClawItemInHandTickProcedure'); by = {i['offset']: i for i in b}
        self.assertIn('CONSTRICTED', by[592]['operand'])
        self.assertEqual((by[595]['operand'], by[596]['operand']), (5, 0))
        hp = next(i['offset'] for i in b if '.getMaxHealth(' in str(i['operand']))
        self.assertLess(600, hp); self.assertLess(hp, 772); self.assertLess(772, 900)
        self.assertEqual(by[898]['operand'], 100)
        self.assertFalse(any('.hurt(' in str(i['operand']) or '.getUseItem(' in str(i['operand']) for i in b))
        candidates = self.row('crusher_claw_native_selected_hold_and_constricted')['scalable_parameter_candidates']
        self.assertFalse(any('crabcool' in parameter for c in candidates for parameter in c['parameters']))

    def test_unused_chaos_pullspeed_is_not_mapped_as_a_consumed_parameter(self):
        b = self.body('ChaosGauntletHeldProcedure')
        self.assertEqual(sum(i['operand'] == 'pullspeed' for i in b), 1)
        row = self.row('chaos_gauntlet_native_selected_mark_and_control')
        self.assertFalse(any('pullspeed' in parameter for c in row['scalable_parameter_candidates'] for parameter in c['parameters']))


class NativeMethodEquivalenceSafety(unittest.TestCase):
    def test_local_operand_capture_retains_implicit_explicit_wide_and_signed_increment(self):
        from native_evidence import annotate_local_operands
        raw = bytes.fromhex('19073a118411ffc419012cc484012cff38')
        body = [{'offset': offset} for offset in (0, 2, 4, 7, 11)]
        annotate_local_operands(body, raw)
        self.assertEqual([i['local_index'] for i in body], [7, 17, 17, 300, 300])
        self.assertEqual((body[2]['increment'], body[4]['increment']), (-1, -200))
        implicit = annotate_local_operands([{'offset': 0}], bytes.fromhex('2d'))
        self.assertEqual(implicit[0]['local_index'], 3)

    def test_query_kernels_reproduce_including_actual_lambda_bootstraps(self):
        from pathlib import Path
        from compare_native_methods import collect
        jar = Path('/workspace/.cache/large-mod-campaign/ArPhEx-5.0.2-neoforge-1.21.1.jar')
        if not jar.is_file(): self.skipTest('Pinned artifact reproduction requires the campaign cache')
        spec = read_json(OUT / 'native-specifications/arphex-held-query-comparator-method-equivalence.json')
        registry = read_json(OUT / 'arphex-held-query-comparator-method-equivalence.json')
        self.assertEqual(collect(spec, jar), registry)
        self.assertEqual(len(registry['rows']), 2 * len(spec['entries']))
        original = {m['entry'] for m in read_json(OUT / 'arphex-combat-census.json')['methods']
                    if m['method'] == 'compareDistOf' and any(m['entry'].split('/')[-1].startswith(prefix)
                    for prefix in ('ForceGauntletToolInHandTickProcedure$', 'ChaosGauntletHeldProcedure$',
                                   'CrusherClawItemInHandTickProcedure$'))}
        self.assertEqual(len(original), 23)
        self.assertTrue(original <= set(spec['entries']))

    def test_same_body_but_wrong_bootstrap_handle_kind_is_rejected(self):
        from pathlib import Path
        from unittest.mock import patch
        import compare_native_methods
        from classfile import ClassFile
        jar = Path('/workspace/.cache/large-mod-campaign/ArPhEx-5.0.2-neoforge-1.21.1.jar')
        if not jar.is_file(): self.skipTest('Pinned artifact reproduction requires the campaign cache')
        spec = read_json(OUT / 'native-specifications/arphex-held-query-comparator-method-equivalence.json')
        def altered_class(raw):
            cls = ClassFile(raw)
            if cls.name == 'net/arphex/procedures/ChaosGauntletHeldProcedure$1':
                at = next(i for i, item in enumerate(cls.cp) if item and item[0] == 15
                          and '.lambda$compareDistOf$0(' in cls.resolve(i))
                tag, (kind, reference) = cls.cp[at]
                cls.cp[at] = (tag, (kind - 1, reference))
            return cls
        with patch.object(compare_native_methods, 'ClassFile', side_effect=altered_class):
            with self.assertRaisesRegex(AssertionError, 'non-equivalent bootstrap'):
                compare_native_methods.collect(spec, jar)


class NativeScytheSpearContracts(NativeContractHarness, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch = read_json(OUT / 'arphex-r2m6d-native-scythe-spear-contracts.json')
        cls.native = read_json(OUT / 'native-evidence/arphex-residual-scythe-spears.json')
        cls.census = read_json(OUT / 'arphex-combat-census.json')

    def test_six_item_roots_four_contracts_validate_without_assuming_mod_closure(self):
        validate_batch(self.batch, self.prior(), self.census)
        self.assertEqual((len(self.batch['closed_item_callback_entries']), len(self.batch['effects'])), (6, 4))
        self.assertEqual(sum(len(c['parameters']) for r in self.batch['effects']
                             for c in r['scalable_parameter_candidates']), 47)
        self.assertEqual((len(self.native['witnesses']), sum(len(w['methods'])
                         for w in self.native['witnesses'])), (15, 76))
        self.assertFalse(self.batch['whole_mod_complete'])

    def test_native_attribute_profiles_and_plain_constructor_contexts(self):
        for name, value in [('SingularityScytheItem', 50.), ('SpearOfParalysisItem', 12.),
                            ('VisionarySpearItem', 29.), ('OversizedStingerItem', 7.)]:
            m = dict(instructions=self.body(name, '<init>'))
            offset = next(i['offset'] for i in m['instructions'] if 'AttributeModifier.<init>(' in str(i['operand']))
            self.assertEqual(literal_item_attribute_binding(m, offset)['native_value'], value)
        for name in ('NecroticFangItem', 'VoidSpearItemItem'):
            self.assertFalse(any('AttributeModifier' in str(i['operand']) for i in self.body(name, '<init>')))
        self.assertEqual(self.body('SingularityScytheOnPlayerStoppedUsingProcedure'),
                         [dict(offset=0, opcode='0xb1', operand=None)])

    def test_scythe_earlier_tormentor_tests_recipient_later_tests_carrier(self):
        b = self.body('SingularityScytheItemInHandTickProcedure')
        gates = [(i['offset'], b[j-1]['local_index']) for j, i in enumerate(b)
                 if i['opcode'] == '0xc1' and i['operand'] == 'net/arphex/entity/TORMENTOREntity']
        self.assertEqual(gates, [(638, 30), (1479, 32), (2229, 1), (2983, 1)])
        from promote_combat_batch import direct_damage_actor_local
        offsets = (666, 695, 1507, 1536, 2257, 2286, 3011, 3040, 3928)
        self.assertEqual([direct_damage_actor_local(dict(instructions=b), o) for o in offsets], [1] * 9)
        self.assertEqual(sum('.hurt(' in str(i['operand']) for i in b), 9)

    def test_computed_ray_arguments_retain_current_state_and_separate_axis_sites(self):
        from promote_combat_batch import subtract_tag_vector_scale_binding
        m = dict(instructions=self.body('SingularityScytheItemInHandTickProcedure'))
        for offset, value in ((134, 10.), (883, 20.), (1638, 30.), (2388, 40.)):
            binding = subtract_tag_vector_scale_binding(m, offset)
            self.assertEqual((binding['native_value'], binding['tag_key'], binding['entity_local_index']),
                             (value, 'sing_scythe_anim', 1))
        row = self.row('singularity_scythe_native_swing_rays_shield_and_owned_source')
        rays = [c for c in row['scalable_parameter_candidates'] if c['primitive'] == 'NATIVE_RAY_DELIVERY']
        self.assertEqual([len(c['additional_consumer_sites']) for c in rays], [2, 2, 2, 2])

    def test_false_ray_coefficient_or_operation_is_rejected(self):
        from promote_combat_batch import subtract_tag_vector_scale_binding
        batch = copy.deepcopy(self.batch)
        row = next(r for r in batch['effects'] if r['id'].endswith(':singularity_scythe_native_swing_rays_shield_and_owned_source'))
        component = next(c for c in row['components'] if c['primitive'] == 'NATIVE_RAY_DELIVERY')
        component['numerical_parameters']['ordinary_base'] = 11.
        with self.assertRaisesRegex(AssertionError, 'pinned ray base'):
            validate_batch(batch, self.prior(), self.census)
        m = dict(instructions=copy.deepcopy(self.body('SingularityScytheItemInHandTickProcedure')))
        next(i for i in m['instructions'] if i['offset'] == 133)['opcode'] = '0x63'
        with self.assertRaises(AssertionError): subtract_tag_vector_scale_binding(m, 134)

    def test_scythe_sphere_queue_captures_world_and_mutable_stack_not_spawned_entity(self):
        b = self.body('SingularityScytheItemInHandTickProcedure')
        by = {i['offset']: i for i in b}
        self.assertEqual(by[4061]['operand'],
                         'bootstrap#14:run(Lnet/minecraft/world/level/LevelAccessor;Lnet/minecraft/world/item/ItemStack;)Ljava/lang/Runnable;')
        delayed = self.body('SingularityScytheItemInHandTickProcedure', 'lambda$execute$17')
        d = {i['offset']: i for i in delayed}
        self.assertIn('SphereAnimEntity.DATA_max_size', d[327]['operand'])
        self.assertEqual(d[330]['operand'], 200)
        self.assertIn('SphereAnimEntity.DATA_color', d[557]['operand'])
        self.assertEqual(d[560]['operand'], 'black')
        self.assertEqual(sum('AABB.ofSize(' in str(i['operand']) for i in delayed), 3)
        self.assertFalse(any('.setOwner(' in str(i['operand']) for i in b + delayed))
        self.assertFalse(any('DATA_black_hole' in str(i['operand']) for i in b + delayed))

    def test_scythe_swing_uuid_reset_and_native_posthit_victim_forwarding(self):
        b = self.body('SingularityScytheLivingEntityIsHitWithItemProcedure')
        self.assertTrue(any('Entity.getStringUUID()' in str(i['operand']) for i in b))
        b = self.body('SingularityScytheItem', 'hurtEnemy')
        at = next(j for j, i in enumerate(b) if 'SingularityScytheLivingEntityIsHitWithItemProcedure.execute(' in str(i['operand']))
        self.assertEqual([i['opcode'] for i in b[at-2:at]], ['0x2c', '0x2b'])
        b = self.body('SingularityScytheEntitySwingsItemProcedure', 'lambda$execute$0')
        self.assertTrue(any(i['operand'] == 'prevent_double_uuid' for i in b))
        self.assertTrue(any(i['operand'] == '' for i in b))

    def test_paralysis_captures_actual_area_recipient_and_repeats_native_anonymous_requests(self):
        from promote_combat_batch import damage_source_binding
        b = self.body('SpearOfParalysisItemInHandTickProcedure')
        m = dict(instructions=b)
        _, allocation, _, ctor = damage_source_binding(m, 514)
        at = next(j for j, i in enumerate(b) if i['offset'] == allocation)
        self.assertEqual(b[at-1]['local_index'], 14)
        self.assertTrue(ctor.endswith('(Lnet/minecraft/core/Holder;)V'))
        by = {i['offset']: i for i in b}
        self.assertEqual(by[535]['local_index'], 14)
        for name in ('lambda$execute$3', 'lambda$execute$2'):
            body = self.body('SpearOfParalysisItemInHandTickProcedure', name)
            self.assertEqual(sum('.hurt(' in str(i['operand']) for i in body), 1)
            self.assertEqual(sum('.setDeltaMovement(' in str(i['operand']) for i in body), 1)
            self.assertFalse(any('.isAlive(' in str(i['operand']) for i in body))
        self.assertFalse(any('MobEffectInstance.<init>' in str(i['operand']) for i in b))

    def test_visionary_root_invokes_held_helper_not_paralysis_root(self):
        b = self.body('VisionarySpearItem', 'inventoryTick')
        self.assertTrue(any('SpearOfParalysisRightclickedProcedure.execute(' in str(i['operand']) for i in b))
        b = self.body('SpearOfParalysisItem', 'inventoryTick')
        self.assertTrue(any('SpearOfParalysisItemInHandTickProcedure.execute(' in str(i['operand']) for i in b))
        self.assertFalse(any('SpearOfParalysisRightclickedProcedure.execute(' in str(i['operand']) for i in b))

    def test_visionary_native_command_seconds_and_fallback_regen_are_distinct(self):
        row = self.row('visionary_spear_native_held_freeze_regeneration_and_overcharge')
        command = next(c for c in row['scalable_parameter_candidates'] if c['primitive'] == 'NATIVE_TIME_FREEZE_COMMAND')
        self.assertEqual(command['native_concat_command_binding']['template'], 'effect give @s arphex:time_freeze 2 \u0001')
        b = self.body('SpearOfParalysisRightclickedProcedure'); by = {i['offset']: i for i in b}
        self.assertFalse(any('.hurt(' in str(i['operand']) for i in b))
        self.assertEqual(by[1188]['operand'], 320)
        self.assertLess(1191, 1260)
        self.assertEqual((by[205]['opcode'], by[205]['branch_target']), ('0x9a', 1194))
        self.assertEqual((by[277]['opcode'], by[277]['branch_target']), ('0x9e', 1194))
        at = next(j for j, i in enumerate(b) if i['offset'] == 1068)
        self.assertEqual([i['operand'] for i in b[at-4:at-2]], [5, 1])
        at = next(j for j, i in enumerate(b) if i['offset'] == 1260)
        self.assertEqual([i['operand'] for i in b[at-4:at-2]], [30, 0])


class NativeArmorMaterialAndSharedCallbacks(NativeContractHarness, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch = read_json(OUT / 'arphex-r2m6e-native-material-shared-armor-contracts.json')
        cls.native = read_json(OUT / 'native-evidence/arphex-residual-native-armor.json')
        cls.census = read_json(OUT / 'arphex-combat-census.json')

    def test_material_setup_and_28_callback_pieces_close_without_claiming_all_capture_reviewed(self):
        validate_batch(self.batch, self.prior(), self.census)
        self.assertEqual((len(self.batch['closed_armor_material_entries']), len(self.batch['closed_item_callback_entries'])), (11, 28))
        self.assertEqual((len(self.batch['effects']), sum(len(c['parameters']) for r in self.batch['effects']
                         for c in r['scalable_parameter_candidates'])), (5, 43))
        self.assertEqual(len(self.batch['pending_captured_armor_callback_entries']), 16)
        self.assertEqual((len(self.native['witnesses']), sum(len(w['methods']) for w in self.native['witnesses'])), (87, 305))
        self.assertFalse(self.batch['whole_mod_complete'])

    def test_literal_armor_profiles_preserve_actual_native_type_values_and_float_precision(self):
        from promote_combat_batch import registered_armor_material_binding
        expected = {'ChitinArmourItem': ([2, 5, 6, 2, 6], 10, 2., 0.),
                    'ChitinArmourTier2Item': ([3, 5, 7, 2, 7], 10, 2., 0.),
                    'ChitinArmourTier3Item': ([3, 6, 8, 3, 8], 12, 3., 0.),
                    'EternalItem': ([6, 11, 15, 7, 15], 100, 6., .8999999761581421),
                    'ImmortalItem': ([10, 16, 20, 10, 20], 100, 6., .8999999761581421),
                    'InfernalItem': ([5, 10, 13, 5, 13], 50, 6., .30000001192092896),
                    'JuggernautItem': ([5, 10, 14, 6, 14], 12, 6., 1.),
                    'SpacetimeItem': ([5, 10, 14, 6, 14], 12, 6., 1.),
                    'SpectralItem': ([5, 10, 13, 5, 13], 50, 6., .30000001192092896),
                    'UmbralItem': ([5, 10, 13, 5, 13], 50, 6., .20000000298023224),
                    'VitalityArmourItem': ([3, 4, 8, 5, 8], 10, 2., 0.)}
        for name, (values, enchant, toughness, knockback) in expected.items():
            w = next(w for w in self.native['witnesses'] if w['entry'].endswith('/' + name + '.class'))
            binding = registered_armor_material_binding(w, self.census)
            self.assertEqual([binding['defense_by_native_type'][key]
                              for key in ('BOOTS', 'LEGGINGS', 'CHESTPLATE', 'HELMET', 'BODY')], values)
            self.assertEqual((binding['enchantment_value'], binding['toughness'], binding['knockback_resistance']),
                             (enchant, toughness, knockback))
        row = self.row('native_registered_armor_material_profiles')
        self.assertEqual(len(row['native_piece_setup']), 44)
        self.assertEqual(row['scalable_parameter_candidates'], [])

    def test_wrong_material_value_or_actual_lambda_target_is_rejected(self):
        from promote_combat_batch import registered_armor_material_binding
        batch = copy.deepcopy(self.batch)
        row = next(r for r in batch['effects'] if r['id'].endswith(':native_registered_armor_material_profiles'))
        row['native_armor_material_profiles'][0]['binding']['defense_by_native_type']['BOOTS'] = 999
        with self.assertRaisesRegex(AssertionError, 'wrong pinned armor material profile'):
            validate_batch(batch, self.prior(), self.census)
        c = copy.deepcopy(self.census)
        entry = 'net/arphex/item/ChitinArmourItem.class'
        bootstrap = next(r for r in c['registration_bootstraps'] if r['entry'] == entry and r['index'] == 0)
        bootstrap['arguments'] = [arg.replace('lambda$registerArmorMaterial$2', 'lambda$registerArmorMaterial$1')
                                  for arg in bootstrap['arguments']]
        w = next(w for w in self.native['witnesses'] if w['entry'] == entry)
        with self.assertRaises(AssertionError): registered_armor_material_binding(w, c)

    def test_exact_native_mod_bus_and_register_event_annotation_are_required(self):
        from promote_combat_batch import registered_armor_material_binding
        w = copy.deepcopy(next(w for w in self.native['witnesses'] if w['entry'].endswith('/ChitinArmourItem.class')))
        w['annotations'][0]['values']['bus']['constant'] = 'GAME'
        with self.assertRaises(AssertionError): registered_armor_material_binding(w, self.census)

    def test_closed_pieces_require_native_player_and_armor_stack_membership(self):
        for entry in self.batch['closed_item_callback_entries']:
            name = entry.split('/')[-1][:-6]
            b = self.body(name, 'inventoryTick')
            self.assertTrue(any(i['opcode'] == '0xc1' and i['operand'] == 'net/minecraft/world/entity/player/Player' for i in b))
            self.assertTrue(any('.getArmorSlots()' in str(i['operand']) for i in b))
            self.assertTrue(any('Iterables.contains(' in str(i['operand']) for i in b))
            forward = next(j for j, i in enumerate(b) if '/procedures/' in str(i['operand']) and '.execute(' in str(i['operand']))
            self.assertTrue(any('.inventoryTick(' in str(i['operand']) for i in b[:forward]))
        row = self.row('native_registered_armor_material_profiles')
        for proof in row['implementation']:
            if any(proof['entry'].split('/')[-1].startswith(prefix + '$')
                   for prefix in ('EternalItem', 'ImmortalItem', 'SpacetimeItem', 'SpectralItem')):
                self.assertEqual(proof['methods'], ['<init>'])

    def test_chitin_all_three_tiers_and_juggernaut_forward_one_callback_per_piece(self):
        for parent in ('ChitinArmourItem', 'ChitinArmourTier2Item', 'ChitinArmourTier3Item', 'JuggernautItem'):
            for piece in ('Boots', 'Chestplate', 'Helmet', 'Leggings'):
                b = self.body(parent + '$' + piece, 'inventoryTick')
                self.assertEqual(sum('ChitinArmour' + piece + 'TickEventProcedure.execute(' in str(i['operand']) for i in b), 1)
        b = self.body('ChitinArmourChestplateTickEventProcedure')
        self.assertTrue(any('TamableAnimal.isOwnedBy(' in str(i['operand']) for i in b))
        self.assertFalse(any('TamableAnimal.isTame(' in str(i['operand']) for i in b))
        row = self.row('shared_chitin_tiers_juggernaut_native_worn_callbacks')
        strength = next(c for c in row['scalable_parameter_candidates'] if c['primitive'] == 'MOB_EFFECT_PET_STRENGTH')
        self.assertEqual(len(strength['additional_consumer_sites']), 1)

    def test_chitin_helmet_scan_has_particles_but_no_glowing_status_or_native_damage(self):
        b = self.body('ChitinArmourHelmetTickEventProcedure')
        self.assertFalse(any('MobEffectInstance.<init>' in str(i['operand']) or '.hurt(' in str(i['operand'])
                             or '.setTarget(' in str(i['operand']) for i in b))
        self.assertTrue(any(str(i['operand']).startswith('particle arphex:glow_sense') for i in b))
        row = self.row('shared_chitin_tiers_juggernaut_native_worn_callbacks')
        self.assertFalse(any('scanpower' in parameter for c in row['scalable_parameter_candidates'] for parameter in c['parameters']))
        terrain = next(c for c in row['scalable_parameter_candidates'] if c['primitive'] == 'NATIVE_TERRAIN_COMMAND')
        self.assertEqual(terrain['native_command_binding']['command'],
                         'fill ~-3 ~-3 ~-3 ~3 ~3 ~3 arphex:cobweb_passable replace cobweb')

    def test_vitality_reset_after_absorption_request_and_same_amp_does_not_refresh(self):
        b = self.body('VitalityArmourChestplateTickEventProcedure'); by = {i['offset']: i for i in b}
        self.assertIn('MobEffectInstance.<init>', by[55]['operand'])
        self.assertEqual(by[68]['operand'], 600.)
        self.assertIn('.putDouble(', by[71]['operand'])
        self.assertLess(55, 71)
        b = self.body('VitalityArmourLeggingsTickEventProcedure'); by = {i['offset']: i for i in b}
        self.assertEqual((by[212]['operand'], by[214]['operand'], by[303]['operand'], by[305]['operand']), (100, 2, 100, 1))
        self.assertEqual(sum('.getAmplifier()' in str(i['operand']) for i in b), 2)
        self.assertTrue(any(i['opcode'] == '0xa2' for i in b))  # Native >= skips refresh.
        removes = [i['operand'] for i in self.body('VitalityArmourHelmetTickEventProcedure') if '/MobEffects.' in str(i['operand'])]
        self.assertTrue('CONFUSION' in removes[0] and 'BLINDNESS' in removes[1])

    def test_infernal_first_passenger_is_not_the_native_vehicle(self):
        b = self.body('InfernalBootsTickEventProcedure')
        self.assertTrue(any('.isPassenger()' in str(i['operand']) for i in b))
        self.assertTrue(any('.getFirstPassenger()' in str(i['operand']) for i in b))
        self.assertFalse(any('.getVehicle()' in str(i['operand']) for i in b))
        c = self.body('InfernalChestplateTickEventProcedure')
        air = next(j for j, i in enumerate(c) if '.setAirSupply(' in str(i['operand']))
        self.assertEqual(c[air-1]['operand'], 300)
        self.assertFalse(any('FIRE_RESISTANCE' in str(i['operand']) for i in b + c))

    def test_umbral_two_ordered_levitations_and_inclusive_void_roll_remain_distinct(self):
        b = self.body('UmbralBootsTickProcedure'); by = {i['offset']: i for i in b}
        self.assertEqual((by[119]['operand'], by[122]['operand'], by[165]['operand'], by[167]['operand']), (160, 2, 50, 3))
        b = self.body('UmbralChestplateTickProcedure'); by = {i['offset']: i for i in b}
        self.assertEqual((by[61]['operand'], by[62]['operand']), (1, 2))
        self.assertIn('Mth.nextInt(', by[63]['operand'])
        self.assertTrue(any('VOID_PROTECTION' in str(i['operand']) for i in b))
        self.assertTrue(any('VOID_COOLDOWN' in str(i['operand']) for i in b))

    def test_unbreakable_raw_custom_tag_is_not_an_actual_native_component_set(self):
        b = self.body('InfernalBootsTickEventProcedure')
        self.assertTrue(any(str(i['operand']).startswith('item modify entity @s armor.feet') for i in b))
        self.assertFalse(any('DataComponents.UNBREAKABLE' in str(i['operand']) for i in b))
        raw = self.body('InfernalBootsTickEventProcedure', 'lambda$execute$0')
        self.assertTrue(any(i['operand'] == 'Unbreakable' for i in raw))
        self.assertTrue(any('CompoundTag.putBoolean(' in str(i['operand']) for i in raw))
