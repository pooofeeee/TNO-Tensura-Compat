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


class NativeRemainingArmorContracts(NativeContractHarness, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch = read_json(OUT / 'arphex-r2m6f-remaining-native-armor-contracts.json')
        cls.native = read_json(OUT / 'native-evidence/arphex-residual-native-armor.json')
        cls.native['witnesses'] += read_json(OUT / 'native-evidence/arphex-native-armor-state-predicates.json')['witnesses']
        cls.census = read_json(OUT / 'arphex-combat-census.json')

    def method(self, name, method='execute'):
        return max((m for w in self.native['witnesses'] if w['entry'].endswith('/'+name+'.class')
                    for m in w['methods'] if m['name'] == method), key=lambda m:len(m['instructions']))

    def test_four_contracts_close_sixteen_remaining_worn_roots(self):
        validate_batch(self.batch, self.prior(), self.census)
        self.assertEqual(len(self.batch['effects']), 4)
        self.assertEqual(len(self.batch['closed_item_callback_entries']), 16)
        self.assertEqual(sum(len(c['parameters']) for r in self.batch['effects']
                             for c in r['scalable_parameter_candidates']), 79)
        self.assertFalse(self.batch['whole_mod_complete'])
        for entry in self.batch['closed_item_callback_entries']:
            b=self.body(entry.split('/')[-1][:-6], 'inventoryTick')
            parent=next(j for j,i in enumerate(b) if i['opcode']=='0xb7' and '.inventoryTick(' in str(i['operand']))
            worn=next(j for j,i in enumerate(b) if 'Iterables.contains(' in str(i['operand']))
            payload=next(j for j,i in enumerate(b) if '/procedures/' in str(i['operand']))
            self.assertLess(parent,worn); self.assertLess(worn,payload)

    def test_literal_status_argument_extractor_binds_exact_native_profiles(self):
        from promote_combat_batch import literal_effect_arguments
        expected=[('EternalBootsTickEventProcedure',372,160,2),
                  ('EternalBootsTickEventProcedure',417,50,3),
                  ('EternalLeggingsTickEventProcedure',74,5,15),
                  ('ImmortalLeggingsTickProcedure',74,5,30),
                  ('ImmortalChestplateTickProcedure',291,200,1),
                  ('SpectralLeggingsTickProcedure',185,100,1)]
        for name,offset,duration,amplifier in expected:
            b=literal_effect_arguments(self.method(name),offset)
            self.assertEqual((b['duration'],b['amplifier']),(duration,amplifier))
        with self.assertRaisesRegex(AssertionError,'computed status arguments'):
            literal_effect_arguments(self.method('ImmortalBootsTickProcedure'),2083)

    def test_wrong_native_status_value_or_auxiliary_profile_is_rejected(self):
        b=copy.deepcopy(self.batch)
        row=next(r for r in b['effects'] if r['id'].endswith(':eternal_and_shared_native_worn_profiles'))
        next(c for c in row['components'] if c['primitive']=='MOB_EFFECT_LONG_LEVITATION')['numerical_parameters']['duration']=161
        with self.assertRaisesRegex(AssertionError,'component differs from native status literals'):
            validate_batch(b,self.prior(),self.census)
        b=copy.deepcopy(self.batch)
        row=next(r for r in b['effects'] if r['id'].endswith(':eternal_and_shared_native_worn_profiles'))
        c=next(c for c in row['scalable_parameter_candidates'] if c['primitive']=='MOB_EFFECT_LONG_LEVITATION')
        c['additional_consumer_sites'][0]['offset']=400
        with self.assertRaisesRegex(AssertionError,'auxiliary status literals differ'):
            validate_batch(b,self.prior(),self.census)

    def test_spacetime_ability_writes_exclude_spectator_but_not_creative(self):
        for j,mode in [(1,'SPECTATOR'),(2,'SPECTATOR'),(3,'SPECTATOR'),(4,'CREATIVE')]:
            b=self.body('SpacetimeBootsTickEventProcedure$'+str(j),'checkGamemode')
            modes={i['operand'].split('GameType.')[1].split('Lnet')[0] for i in b if 'GameType.' in str(i['operand'])}
            self.assertEqual(modes,{mode})
        b=self.body('SpacetimeBootsTickEventProcedure')
        writes=[j for j,i in enumerate(b) if i['opcode']=='0xb5' and any(x in str(i['operand']) for x in ['Abilities.mayfly','Abilities.flying'])]
        self.assertEqual(len(writes),2)
        checks=[i['operand'] for i in b[:writes[-1]] if '.checkGamemode(' in str(i['operand'])]
        self.assertEqual(len(checks),1); self.assertIn('Procedure$1.checkGamemode',checks[0])
        self.assertTrue(any('SPACETIME_BOOTSL' in str(i['operand']) for i in b[:writes[-1]]))

    def test_immortal_boost_and_flight_keep_actual_mode_gates(self):
        for j,mode in [(1,'SPECTATOR'),(2,'CREATIVE'),(3,'SPECTATOR'),(4,'CREATIVE')]:
            b=self.body('ImmortalBootsTickProcedure$'+str(j),'checkGamemode')
            self.assertEqual({i['operand'].split('GameType.')[1].split('Lnet')[0]
                              for i in b if 'GameType.' in str(i['operand'])},{mode})
        b=self.body('ImmortalBootsTickProcedure'); by={i['offset']:i for i in b}
        self.assertEqual(by[768]['operand'],20.)
        self.assertEqual(by[771]['operand'],'net/minecraft/nbt/CompoundTag.putDouble(Ljava/lang/String;D)V')
        self.assertTrue(any(i['operand']=='sneakjump_enable' for i in b if 920<i['offset']<1200))

    def test_immortal_health_restore_checks_and_sets_spacetime_leggings_cooldown(self):
        b=self.body('ImmortalLeggingsTickProcedure')
        fields=[i for i in b if 'SPACETIME_LEGGINGSL' in str(i['operand'])]
        self.assertEqual(len(fields),2)
        restore=next(j for j,i in enumerate(b) if '.setHealth(' in str(i['operand']))
        cooldown=next(j for j,i in enumerate(b) if i['offset']==1563)
        self.assertLess(restore,cooldown)
        self.assertFalse(any('.heal(' in str(i['operand']) for i in b))
        self.assertEqual(b[cooldown-1]['operand'],600)
        self.assertFalse(any('IMMORTAL_LEGGINGSL' in str(i['operand']) for i in b))

    def test_native_history_rotation_and_reset_precede_recovery(self):
        for name,first_reset in [('SpacetimeLeggingsTickEventProcedure',339),('ImmortalLeggingsTickProcedure',1136)]:
            b=self.body(name);before=[i['operand'] for i in b if i['offset']<first_reset]
            self.assertIn('bcst5',before);self.assertIn('bcst4',before);self.assertIn('bcst1',before)
            restore=next(i['offset'] for i in b if '.setHealth(' in str(i['operand']))
            self.assertLess(first_reset,restore)
            self.assertTrue(any(i['operand']=='buffer_cycle_spacetime' for i in b))
        shared=self.row('spacetime_immortal_native_temporal_armor_control')
        c=next(c for c in shared['scalable_parameter_candidates'] if c['primitive']=='NATIVE_HEALTH_HISTORY_CADENCE')
        self.assertEqual(len(c['additional_consumer_sites']),1)

    def test_double_crouch_new_window_decrement_and_active_cd_branch(self):
        for name,reset,dec in [('SpacetimeChestplateTickProcedure',1240,1307),('ImmortalChestplateTickProcedure',2248,2315)]:
            m=self.method(name);b=m['instructions'];by={i['offset']:i for i in b}
            self.assertLess(reset,dec)
            j=next(j for j,i in enumerate(b) if i['offset']==reset)
            self.assertEqual(b[j-1]['operand'],10.)
            j=next(j for j,i in enumerate(b) if i['offset']==dec)
            self.assertEqual(b[j-2]['operand'],1.);self.assertEqual(b[j-1]['opcode'],'0x67')
            # Pinned branch operands prove that current cooldown can skip this
            # input region and both timer writes.
            self.assertTrue(any(i['opcode']=='0xa7' and i['offset']<reset
                                and i['branch_target']>dec for i in b))

    def test_impact_damage_keeps_rounding_cap_distance_and_native_source(self):
        from promote_combat_batch import damage_source_binding
        m=self.method('ImmortalBootsTickProcedure');b=m['instructions'];by={i['offset']:i for i in b}
        self.assertEqual(by[2755]['operand'],2.)
        self.assertEqual(by[2795]['operand'],4.)
        self.assertEqual(by[2802]['operand'],5.)
        self.assertEqual(by[2805]['operand'],'java/lang/Math.max(DD)D')
        self.assertEqual(by[2812]['opcode'],'0x57')
        source=damage_source_binding(m,2809)
        self.assertIn('DamageTypes.GENERIC',source[0]); self.assertIn('Holder;Lnet/minecraft/world/entity/Entity;',source[3])
        self.assertEqual(by[2788]['local_index'],7)
        self.assertTrue(any('Math.round(D)J' in str(i['operand']) for i in b))
        self.assertTrue(any(i['operand']==20. and 2341<i['offset']<2552 for i in b))
        self.assertFalse(any('.setDeltaMovement(' in str(i['operand']) for i in b if 2552<i['offset']<2816))
        self.assertTrue(any('.isOwnedBy(' in str(i['operand']) for i in b if 2552<i['offset']<2809))

    def test_raw_impact_charge_reset_is_after_damage_and_before_mount_status(self):
        b=self.body('ImmortalBootsTickProcedure');by={i['offset']:i for i in b}
        self.assertEqual(by[2910]['operand'],'immortal_impact_charge')
        self.assertEqual(by[2913]['operand'],0.)
        self.assertLess(2809,2914);self.assertLess(2914,2979)
        self.assertEqual(by[2897]['operand'],'bootstrap#5:run(Lnet/minecraft/world/level/LevelAccessor;DDD)Ljava/lang/Runnable;')
        self.assertTrue(any(i['opcode']=='0xa7' and 2083<i['offset']<2390 for i in b))

    def test_helmet_evasion_captures_real_coordinates_not_source_aid_alias(self):
        for name,offsets in [('EternalHelmetTickEventProcedure',(417,443)),('ImmortalHelmetTickProcedure',(418,444))]:
            b=self.body(name);by={i['offset']:i for i in b}
            self.assertIn('.getX()',by[offsets[0]]['operand']);self.assertIn('.getZ()',by[offsets[1]]['operand'])
            lambdas=[m for w in self.native['witnesses'] if w['entry'].endswith('/'+name+'.class')
                     for m in w['methods'] if m['name'].startswith('lambda$execute$')]
            setters=[m['instructions'] for m in lambdas if any('.putDouble(' in str(i['operand']) for i in m['instructions'])]
            self.assertEqual(len(setters),2)
            self.assertEqual({i['operand'] for b in setters for i in b if type(i['operand']) is str and i['operand'].startswith('etdir')},{'etdirx','etdirz'})
            self.assertFalse(any('.teleportTo(' in str(i['operand']) for i in b))
        immortal=self.body('ImmortalHelmetTickProcedure')
        self.assertFalse(any('EquipmentSlot.HEADL' in str(i['operand']) for i in immortal))

    def test_native_spectral_invisibility_and_nightvision_are_inside_burst_cooldown(self):
        from promote_combat_batch import literal_effect_arguments
        b=self.body('SpectralLeggingsTickProcedure');cd=next(j for j,i in enumerate(b) if i['offset']==97)
        self.assertEqual(b[cd-1]['operand'],500)
        for offset,holder in [(185,'INVISIBILITY'),(232,'NIGHT_VISION')]:
            p=literal_effect_arguments(self.method('SpectralLeggingsTickProcedure'),offset)
            self.assertEqual((p['duration'],p['amplifier']),(100,1));self.assertIn(holder,p['holder'])
        self.assertFalse(any('.isOwnedBy(' in str(i['operand']) or '.isAlliedTo(' in str(i['operand']) for i in b))

    def test_shared_profile_candidates_keep_each_actual_consumer_once(self):
        r=self.row('eternal_and_shared_native_worn_profiles')
        c=next(c for c in r['scalable_parameter_candidates'] if c['primitive']=='MOB_EFFECT_AREA_SLOWNESS')
        self.assertEqual({s['entry'].split('/')[-1] for s in c['additional_consumer_sites']},
                         {'ImmortalLeggingsTickProcedure.class','SpectralLeggingsTickProcedure.class'})
        self.assertEqual(len(c['additional_consumer_sites']),2)
        all_candidates=[c for r in self.batch['effects'] for c in r['scalable_parameter_candidates']]
        self.assertFalse(any('sphere_near' in p or 'immortal_near' in p or 'shadertime' in p
                            for c in all_candidates for p in c['parameters']))
        self.assertFalse(any(c['primitive']=='NATIVE_IMPACT_SPHERE_CONFIGURATION' for c in all_candidates))

    def test_impact_rounding_binds_actual_power_conversion_not_display_copies(self):
        from promote_combat_batch import rounded_tag_quotient_binding
        m=self.method('ImmortalBootsTickProcedure')
        actual=rounded_tag_quotient_binding(m,2341)
        self.assertEqual(actual,dict(tag_key='immortal_impact_charge',divisor=10.,
                                    entity_local_index=7,conversion='JAVA_MATH_ROUND_DOUBLE_TO_LONG'))
        c=next(c for c in self.row('immortal_armor_native_boost_impact_and_helmet_control')['scalable_parameter_candidates']
               if c['primitive']=='NATIVE_IMPACT_POWER')
        self.assertEqual(c['native_consumer']['offset'],2341)
        bad=copy.deepcopy(m);next(i for i in bad['instructions'] if i['offset']==2340)['opcode']='0x6b'
        with self.assertRaises(AssertionError):rounded_tag_quotient_binding(bad,2341)
        batch=copy.deepcopy(self.batch)
        r=next(r for r in batch['effects'] if r['id'].endswith(':immortal_armor_native_boost_impact_and_helmet_control'))
        next(c for c in r['components'] if c['primitive']=='NATIVE_IMPACT_POWER')['numerical_parameters']['charge_divisor']=11.
        with self.assertRaises(AssertionError):validate_batch(batch,self.prior(),self.census)
        commands=[i['operand'] for i in self.body('ImmortalLeggingsTickProcedure')
                  if str(i['operand']).startswith('fill ')]
        self.assertEqual(commands,['fill ~-3 ~-3 ~-3 ~3 ~3 ~3 arphex:cobweb_passable replace cobweb'])


class NativeConsumableContracts(NativeContractHarness, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch=read_json(OUT/'arphex-r2m6g-native-consumable-and-shared-gem-contracts.json')
        cls.native=read_json(OUT/'native-evidence/arphex-residual-native-consumables.json')
        cls.census=read_json(OUT/'arphex-combat-census.json')

    def method(self,name,method='execute'):
        return max((m for w in self.native['witnesses'] if w['entry'].endswith('/'+name+'.class')
                    for m in w['methods'] if m['name']==method),key=lambda m:len(m['instructions']))

    def test_bounded_seven_contracts_close_twenty_eight_roots(self):
        validate_batch(self.batch,self.prior(),self.census)
        self.assertEqual((len(self.batch['effects']),len(self.batch['closed_item_callback_entries'])),(7,28))
        self.assertEqual(sum(len(c['parameters']) for r in self.batch['effects'] for c in r['scalable_parameter_candidates']),96)
        self.assertEqual((len(self.native['witnesses']),sum(len(w['methods']) for w in self.native['witnesses'])),(47,120))
        self.assertFalse(self.batch['whole_mod_complete'])

    def test_food_inputs_are_literal_native_components_not_derived_aliases(self):
        from promote_combat_batch import literal_food_component_binding
        r=self.row('native_consumable_food_resource_input_profiles')
        self.assertEqual(len(r['native_food_profiles']),19)
        self.assertEqual(sum(len(c['parameters']) for c in r['scalable_parameter_candidates']),38)
        for name,expected in [('EntropySerumItem',(50,2.,True)),('CelestialBarrierItem',(0,.30000001192092896,True)),
                              ('ElixirOfSplinteredSanityItem',(999,20.,True)),('HemoplasmItem',(10,.4000000059604645,False))]:
            m=self.method(name,'<init>');offset=next(i['offset'] for i in m['instructions'] if 'Item$Properties.food(' in str(i['operand']))
            actual=literal_food_component_binding(m,offset)
            self.assertEqual((actual['nutrition'],actual['saturation_modifier'],actual['always_edible']),expected)
        self.assertFalse(any(p.endswith('_derived_saturation') or p.endswith('_final_health')
                             for c in r['scalable_parameter_candidates'] for p in c['parameters']))

    def test_food_argument_mutations_cannot_pass_generic_validation(self):
        from promote_combat_batch import literal_food_component_binding
        m=copy.deepcopy(self.method('EntropySerumItem','<init>'))
        next(i for i in m['instructions'] if i['offset']==34)['opcode']='0x6a'
        with self.assertRaises(AssertionError):literal_food_component_binding(m,44)
        b=copy.deepcopy(self.batch)
        r=next(r for r in b['effects'] if r['id'].endswith(':native_consumable_food_resource_input_profiles'))
        next(c for c in r['components'] if c['primitive']=='NATIVE_FOOD_RESOURCE_INPUTS')['numerical_parameters']['entropyserum_nutrition']=51
        with self.assertRaisesRegex(AssertionError,'component differs from native food input'):
            validate_batch(b,self.prior(),self.census)

    def test_bloodworm_poison_is_unconditional_release_not_consumption(self):
        b=self.body('BloodwormGrubItem','releaseUsing')
        self.assertEqual(len(b),3)
        self.assertEqual(b[0]['opcode'],'0x2d')
        self.assertIn('MaggotGrubPlayerFinishesUsingItemProcedure.execute(',b[1]['operand'])
        self.assertEqual(b[2]['opcode'],'0xb1')
        w=next(w for w in self.native['witnesses'] if w['entry'].endswith('/BloodwormGrubItem.class'))
        self.assertFalse(any(m['name']=='finishUsingItem' for m in w['methods']))

    def test_gems_forward_unconditionally_and_spacetime_is_not_a_holder_predicate(self):
        roots=['AbyssalCrystalItem','EntropyMatrixItem','FireOpalItem','InfernalShardItem','SpacetimeShardItem',
               'SpectralShardItem','TimePrismItem','UmbralShardItem','VoidGeodeItem']
        for name in roots:
            b=self.body(name,'inventoryTick')
            self.assertFalse(any('branch_target' in i for i in b))
            self.assertTrue(any('PowerGemHeldProcedure.execute(' in str(i['operand']) for i in b))
        b=self.body('PowerGemHeldProcedure');ctors=[i for i in b if 'MobEffectInstance.<init>(' in str(i['operand'])]
        self.assertEqual(len(ctors),8)
        self.assertFalse(any('SPACETIME_SHARDL' in str(i['operand']) for i in b))
        r=self.row('shared_native_power_gem_held_strength');self.assertEqual(len(r['scalable_parameter_candidates']),1)
        self.assertEqual(len(r['scalable_parameter_candidates'][0]['additional_consumer_sites']),7)

    def test_fortified_status_order_and_armor_harm_native_requests(self):
        from promote_combat_batch import literal_effect_arguments
        m=self.method('EntropySerumConsumedProcedure')
        profiles=[literal_effect_arguments(m,i['offset']) for i in m['instructions'] if 'MobEffectInstance.<init>(' in str(i['operand'])]
        self.assertEqual([(p['holder'].split('.')[-1].split('Lnet')[0],p['duration'],p['amplifier']) for p in profiles],
                         [('MOVEMENT_SLOWDOWN',200,0),('HEAL',1,0),('FIRE_RESISTANCE',6000,0),('ABSORPTION',2400,3),
                          ('DAMAGE_RESISTANCE',2400,1),('REGENERATION',2400,1),('HARM',1,0),('HARM',1,1)])
        b=m['instructions'];armor=next(j for j,i in enumerate(b) if '.getArmorValue(' in str(i['operand']))
        regen=next(j for j,i in enumerate(b) if 'MobEffects.REGENERATIONL' in str(i['operand']))
        self.assertLess(regen,armor)
        self.assertFalse(any('.hurt(' in str(i['operand']) for i in b))
        self.assertTrue(any(i['operand']==19 for i in b[armor:]));self.assertTrue(any(i['operand']==11 for i in b[armor:]))

    def test_vanilla_instant_ticking_and_undead_inversion_are_independent_proofs(self):
        p=read_json(OUT/'vanilla-evidence/cult-completion.json');w=next(w for w in p['classes'] if w['raw_entry']=='brt.class')
        b=next(m['instructions'] for m in w['methods'] if m['name']=='applyEffectTick')
        self.assertTrue(any('.isInvertedHealAndHarm()' in str(i['operand']) for i in b))
        self.assertTrue(any('.magic()' in str(i['operand']) for i in b))
        self.assertTrue(any('.heal(' in str(i['operand']) for i in b));self.assertTrue(any('.hurt(' in str(i['operand']) for i in b))
        p=read_json(OUT/'vanilla-evidence/arphex-instant-marker-command.json');w=next(w for w in p['classes'] if w['raw_entry']=='brw.class')
        b=next(m['instructions'] for m in w['methods'] if m['name']=='shouldApplyEffectTickThisTick')
        self.assertEqual([i['opcode'] for i in b[:3]],['0x1b','0x4','0xa1'])

    def test_hemoplasm_regen_poison_remain_mutually_exclusive_native_branches(self):
        from promote_combat_batch import literal_effect_arguments
        m=self.method('HemoplasmPlayerFinishesUsingItemProcedure');b=m['instructions']
        profiles=[literal_effect_arguments(m,i['offset']) for i in b if 'MobEffectInstance.<init>(' in str(i['operand'])]
        self.assertEqual([(p['duration'],p['amplifier']) for p in profiles],[(100,1),(100,1)])
        self.assertIn('REGENERATION',profiles[0]['holder']);self.assertIn('POISON',profiles[1]['holder'])
        self.assertTrue(any('.getMaxHealth()' in str(i['operand']) for i in b))
        self.assertTrue(any(i['opcode']=='0x6e' for i in b))
        self.assertTrue(any(i['opcode']=='0xa7' and i['branch_target']>100 for i in b))

    def test_cake_parent_result_is_discarded_before_helper_and_replacement(self):
        b=self.body('CrawlingCakeItem','finishUsingItem');j=next(j for j,i in enumerate(b) if '.finishUsingItem(' in str(i['operand']))
        self.assertEqual(b[j+1]['opcode'],'0x57')
        helper=next(j for j,i in enumerate(b) if 'CrawlingCakePlayerFinishesUsingItemProcedure.execute(' in str(i['operand']))
        empty=next(j for j,i in enumerate(b) if '.isEmpty()' in str(i['operand']))
        self.assertLess(j,helper);self.assertLess(helper,empty)
        q=self.body('CrawlingCakePlayerFinishesUsingItemProcedure')
        invoked=next(i for i in q if i['opcode']=='0xba' and ':run(' in str(i['operand']))
        self.assertNotIn('ItemStack;',invoked['operand']);self.assertIn('Entity;',invoked['operand'])

    def test_cake_delayed_current_hand_priority_and_native_store_lifecycle(self):
        b=self.body('CrawlingCakePlayerFinishesUsingItemProcedure','lambda$execute$0')
        main=next(j for j,i in enumerate(b) if '.getMainHandItem()' in str(i['operand']))
        off=next(j for j,i in enumerate(b) if '.getOffhandItem()' in str(i['operand']))
        self.assertLess(main,off)
        self.assertEqual(sum('.setDamageValue(' in str(i['operand']) for i in b),2)
        self.assertEqual(sum('.setItemInHand(' in str(i['operand']) for i in b),2)
        self.assertFalse(any('.isAlive()' in str(i['operand']) or '.getDamageValue()' in str(i['operand']) for i in b))
        self.assertEqual(sum(i['operand']==8. for i in b),2)
        held=self.body('CrawlingCakeItemInHandTickProcedure');by={i['offset']:i for i in held}
        self.assertIn('.getDamageValue()',by[36]['operand']);self.assertIn('.putDouble(',by[40]['operand'])
        self.assertTrue(any(i['branch_target']>40 for i in held if i['opcode']=='0x99'))

    def test_unlock_delays_reassert_flags_and_do_not_generate_attack_payloads(self):
        for name,field,reassertions in [('CelestialBarrierPlayerFinishesUsingItemProcedure','shield_power_unlocked',1),
                                       ('SeismicPulsePlayerFinishedProcedure','slam_power_unlocked',3)]:
            w=next(w for w in self.native['witnesses'] if w['entry'].endswith('/'+name+'.class'))
            b=[i for m in w['methods'] for i in m['instructions']]
            self.assertEqual(sum(i['opcode']=='0xb5' and field+'Z' in str(i['operand']) for i in b),reassertions)
            self.assertFalse(any('.hurt(' in str(i['operand']) or 'MobEffectInstance' in str(i['operand']) for i in b))
        r=self.row('native_consumed_inherent_power_unlock_prerequisites');self.assertEqual(r['scalable_parameter_candidates'],[])

    def test_enhanced_senses_presentation_exclusion_is_reused_not_reinvented(self):
        r=self.row('native_custom_status_consumable_doses')
        self.assertIn('particle',r['native_presentation_context_reuse']['reason'])
        self.assertFalse(any('ENHANCED_SENSES' in c['primitive'] for c in r['scalable_parameter_candidates']))
        self.assertTrue(any('ENHANCED_SENSES' in q['holder'] for p in r['ordered_native_status_requests'] for q in p['ordered_status_requests']))


class NativeStaffLauncherContracts(NativeContractHarness, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch=read_json(OUT/'arphex-r2m6h-native-staff-launcher-contracts.json')
        cls.native=read_json(OUT/'native-evidence/arphex-residual-native-staff-launcher.json')
        cls.census=read_json(OUT/'arphex-combat-census.json')

    def test_bounded_callbacks_validate_without_claiming_captured_spatial_scope(self):
        validate_batch(self.batch,self.prior(),self.census)
        self.assertEqual(len(self.batch['effects']),7)
        self.assertEqual(len(self.batch['closed_item_callback_entries']),9)
        self.assertEqual(sum(len(c['parameters']) for r in self.batch['effects']
                             for c in r['scalable_parameter_candidates']),77)
        closed={p['entry'] for r in self.batch['effects'] for p in r['implementation']}
        self.assertIn('net/arphex/item/WarpStaffItem.class',self.batch['captured_but_unreviewed_entries'])
        self.assertNotIn('net/arphex/item/WarpStaffItem.class',closed)
        self.assertFalse(self.batch['whole_mod_complete'])

    def test_native_float_sword_builder_and_zero_tier_are_distinct_from_vanilla_int(self):
        b=literal_item_attribute_binding(dict(instructions=self.body('VortexDevastatorItem','<init>')),18)
        self.assertEqual((b['kind'],b['attack_bonus'],b['attack_speed']),('SWORD_ATTRIBUTE_ARGUMENTS',3.,-3.))
        self.assertEqual(self.body('VortexDevastatorItem$1','getAttackDamageBonus')[0]['operand'],0.)
        p=read_json(OUT/'reference-evidence/native-item-attributes-loader-244.json')
        text=''.join(s['text'] for w in p['witnesses'] for s in w['text_sections'])
        self.assertIn('return createAttributes(p_330371_, (float)p_331976_, p_332104_);',text)
        self.assertIn('Tier p_330371_, float p_331976_, float p_332104_',text)
        self.assertTrue(any('.attributes(' in str(i['operand']) for i in self.body('VortexDevastatorItem','<init>')))

    def test_local_scalar_input_requires_literal_and_real_read_not_unused_scratch(self):
        from promote_combat_batch import literal_numeric_input_binding
        m=dict(instructions=copy.deepcopy(self.body('HornetHailstormItemInHandTickProcedure')))
        b=literal_numeric_input_binding(m,154)
        self.assertEqual((b['native_value'],b['local_index']),(5.,15))
        self.assertTrue(b['read_offsets'])
        next(i for i in m['instructions'] if i['offset']==151)['opcode']='0x63'
        with self.assertRaises(AssertionError):literal_numeric_input_binding(m,154)
        m=dict(instructions=self.body('HornetHailstormItemInHandTickProcedure'))
        # Native distance_scaling_factor is assigned 1 but never read.
        with self.assertRaisesRegex(AssertionError,'unused or overwritten'):
            literal_numeric_input_binding(m,179)

    def test_false_targeting_coefficient_is_rejected_by_native_literal(self):
        b=copy.deepcopy(self.batch)
        r=next(r for r in b['effects'] if r['id'].endswith(':shared_hornet_nemesis_native_lock_release_and_owned_cancel'))
        next(c for c in r['components'] if c['primitive']=='NATIVE_LOCK_SELECTION')['numerical_parameters']['pitch_numerator']=141.
        with self.assertRaisesRegex(AssertionError,'component differs from native numeric input'):
            validate_batch(b,self.prior(),self.census)

    def test_ascent_vehicle_request_and_delayed_profile_not_first_passenger(self):
        from promote_combat_batch import literal_effect_arguments
        m=dict(instructions=self.body('AscendantStaffRightclickedProcedure'))
        self.assertEqual(literal_effect_arguments(m,413)['duration'],90)
        self.assertEqual(literal_effect_arguments(m,460)['duration'],90)
        self.assertTrue(any('.getVehicle(' in str(i['operand']) for i in m['instructions']))
        self.assertFalse(any('.getFirstPassenger(' in str(i['operand']) for i in m['instructions']))
        delayed=dict(instructions=self.body('AscendantStaffRightclickedProcedure','lambda$execute$0'))
        self.assertEqual(literal_effect_arguments(delayed,35)['duration'],87)
        self.assertFalse(any('getCooldowns' in str(i['operand']) or 'getItem(' in str(i['operand']) for i in delayed['instructions']))

    def test_ethereal_inventory_delivery_and_null_source_nearest_player_command(self):
        b=self.body('EtherealStaffItem','inventoryTick');by={i['offset']:i for i in b}
        call=next(i['offset'] for i in b if 'EtherealStaffRightclickedProcedure.execute(' in str(i['operand']))
        selected=next(i for i in b if i.get('branch_target') is not None)
        self.assertLessEqual(selected['branch_target'],call)
        helper=self.body('EtherealStaffRightclickedProcedure')
        self.assertTrue(any(i['operand']=='execute at @p run tp @p ^ ^0.01 ^0.5' for i in helper))
        self.assertTrue(any('CommandSource.NULL' in str(i['operand']) for i in helper))
        self.assertFalse(any('.hurt(' in str(i['operand']) for i in helper))
        self.assertEqual([i['offset'] for i in helper if 'addCooldown(' in str(i['operand'])],[739,854])

    def test_vitality_regen_presence_branch_still_reaches_clock_reset(self):
        b=self.body('StaffOfVitalityToolInHandTickProcedure');by={i['offset']:i for i in b}
        presence=next(n for n,i in enumerate(b) if '.hasEffect(' in str(i['operand']))
        branch=b[presence+1]
        self.assertGreater(branch['branch_target'],87)
        self.assertLess(branch['branch_target'],149)
        self.assertEqual(by[146]['operand'],150.)
        self.assertIn('putDouble',by[149]['operand'])

    def test_swarm_releases_reuse_targets_without_cooldown_or_owner_recheck(self):
        for n,species in [('HornetHailstormOnPlayerStoppedUsingProcedure','HORNET_PROJECTILE'),('VenomTyphoonStoppedUsingProcedure','NEMESIS_PROJECTILE')]:
            b=self.body(n)
            self.assertFalse(any('.isOnCooldown(' in str(i['operand']) or '.getTicksUsingItem(' in str(i['operand']) or '.setOwner(' in str(i['operand']) or '.tame(' in str(i['operand']) for i in b))
            self.assertTrue(any(species in str(i['operand']) for i in b))
            self.assertTrue(any(i['operand']==8 and i['opcode']=='0x10' for i in b))
            self.assertEqual([i['offset'] for i in b if 'EntityType.spawn(' in str(i['operand'])],[188])
        for n in ['HornetHailstormRightclickedProcedure','VenomTyphoonRightClickedProcedure']:
            b=self.body(n)
            self.assertTrue(any('.isOnCooldown(' in str(i['operand']) for i in b))
            self.assertTrue(any('.isOwnedBy(' in str(i['operand']) for i in b))
        self.assertIn('arphex:hornet_nemesis_native_uuid_carrier_and_melee',self.row('shared_hornet_nemesis_native_lock_release_and_owned_cancel')['canonical_contract_reuse'])

    def test_ray_damage_sources_are_carrier_and_low_mode_has_no_floor(self):
        from promote_combat_batch import direct_damage_actor_local
        b=self.body('OblivionRayHeldProcedure');m=dict(instructions=b);by={i['offset']:i for i in b}
        hurt=[i['offset'] for i in b if '.hurt(' in str(i['operand'])]
        self.assertEqual(hurt,[1459,1487,1592,1620,1816,1846])
        self.assertTrue(all(direct_damage_actor_local(m,o)==7 for o in hurt))
        self.assertEqual((by[1451]['operand'],by[1452]['opcode']),(3,'0x6c'))
        self.assertEqual((by[1584]['operand'],by[1587]['opcode']),(10.,'0x67'))
        self.assertEqual((by[1812]['operand'],by[1815]['opcode']),('java/lang/Math.round(D)J','0x89'))
        # Low branch round is immediately converted to float and requested: no max/floor.
        self.assertEqual([i['opcode'] for i in b if 1812<=i['offset']<=1819],['0xb8','0x89','0xb6','0x57'])
        self.assertLess(1633,1859)  # Toggle is written after each of the two recipient arms.
        self.assertIn('putBoolean',by[1633]['operand']);self.assertIn('putBoolean',by[1859]['operand'])

    def test_ray_cooldown_integer_division_and_null_actor_native_explosion(self):
        b=self.body('OblivionRayHeldProcedure');by={i['offset']:i for i in b}
        self.assertEqual((by[333]['operand'],by[334]['opcode']),(2,'0x6c'))
        self.assertTrue(any('Math.round(F)I' in str(i['operand']) and i['offset']<339 for i in b))
        explode=next(n for n,i in enumerate(b) if i['offset']==2278)
        self.assertIn('ExplosionInteraction.BLOCK',b[explode-1]['operand'])
        self.assertTrue(any(i['opcode']=='0x1' for i in b[explode-15:explode]))
        self.assertTrue(any(i['operand']==2. and i['opcode'] in ['0xd','0x12','0x13'] for i in b[explode-15:explode]))
        self.assertEqual(by[2192]['operand'],20.)
        self.assertFalse(any('putBoolean' in str(i['operand']) for i in self.body('OblivionRayRightclickedProcedure')))

    def test_vortex_queue_is_outside_cooldown_arm_and_motion_is_per_stack(self):
        b=self.body('VortexDevastatorRightclickedProcedure')
        check=next(n for n,i in enumerate(b) if '.isOnCooldown(' in str(i['operand']))
        self.assertLessEqual(b[check+1]['branch_target'],300)
        self.assertGreater(b[check+1]['branch_target'],77)
        b=self.body('VortexDevastatorToolInInventoryTickProcedure');by={i['offset']:i for i in b}
        self.assertEqual((by[206]['operand'],by[221]['operand'],by[263]['operand'],by[275]['operand']),(1.5,.2,2.,.3))
        self.assertLess(139,243)
        root=self.body('VortexDevastatorItem','inventoryTick')
        self.assertEqual(next(i['branch_target'] for i in root if i.get('branch_target') is not None),34)
        self.assertTrue(any('VortexDevastatorToolInInventoryTickProcedure.execute(' in str(i['operand']) and i['offset']>34 for i in root))

    def test_vanguard_empty_held_callback_keeps_active_swing_contract(self):
        b=self.body('VortexVanguardItemInHandTickProcedure')
        self.assertFalse(any(i['opcode'] in ('0xb5','0xb6','0xb7','0xb8','0xb9','0xba') for i in b))
        self.assertEqual(b[-1]['opcode'],'0xb1')
        self.assertTrue(any('arphex:vortex_vanguard_owner_free_spin_delivery' in r.get('canonical_contract_reuse',[]) for r in self.batch['effects']))


class NativeAntControlContracts(NativeContractHarness, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch = read_json(OUT / 'arphex-r2m6l-native-ant-control-contracts.json')
        cls.native = read_json(OUT / 'native-evidence/arphex-residual-native-summoner-utility.json')
        cls.support = read_json(OUT / 'native-evidence/arphex-native-ant-control-support.json')
        cls.census = read_json(OUT / 'arphex-combat-census.json')

    def support_body(self, name, method='execute'):
        return next(m['instructions'] for w in self.support['witnesses']
                    if w['entry'].endswith('/' + name + '.class')
                    for m in w['methods'] if m['name'] == method)

    def test_exact_contracts_and_dependent_geometry_not_extra_candidates(self):
        validate_batch(self.batch, self.prior(), self.census)
        self.assertEqual(len(self.batch['effects']), 3)
        self.assertEqual(sum(len(c['parameters']) for r in self.batch['effects']
                             for c in r['scalable_parameter_candidates']), 10)
        self.assertEqual((len(self.support['witnesses']), sum(len(w['methods'])
                         for w in self.support['witnesses'])), (4, 12))
        context = self.row('ant_commander_native_terrain_sequence_and_worker_reposition')['native_terrain_sequence_context']
        self.assertEqual(context['native_phase_values'], list(map(float, range(147, 0, -7))))
        self.assertEqual(len(context['normal_branch_block_writes']), 41)
        self.assertFalse(context['independent_scalar_candidates'])
        self.assertFalse(self.batch['whole_mod_complete'])

    def test_queen_and_worker_admission_are_native_owner_predicates(self):
        b = self.body('AntCommanderRightclickedProcedure')
        self.assertEqual(sum('.isOwnedBy(' in str(i['operand']) for i in b), 2)
        self.assertEqual(sum('.moveTo(DDDD)' in str(i['operand']) for i in b), 1)
        self.assertTrue(any('DATA_Xarea' in str(i['operand']) for i in b))
        self.assertTrue(any('DATA_Yarea' in str(i['operand']) for i in b))
        self.assertTrue(any('DATA_Zarea' in str(i['operand']) for i in b))
        self.assertTrue(any(i['operand'] == 180. for i in b))
        self.assertTrue(any(i['operand'] == 140. for i in b))
        self.assertEqual(next(i for i in b if i['offset'] == 755)['opcode'], '0x67')
        self.assertEqual(next(i for i in b if i['offset'] == 893)['opcode'], '0x8e')  # D->I, not rounding

    def test_inventory_clock_is_unconditional_and_phase_test_follows_decrement(self):
        root = self.body('AntCommanderItem', 'inventoryTick')
        self.assertFalse(any(i['opcode'] in ('0x99', '0x9a') for i in root))
        b = self.body('AntCommanderItemInInventoryTickProcedure')
        first_sub = next(i['offset'] for i in b if i['opcode'] == '0x67')
        phase_read = next(i['offset'] for j, i in enumerate(b[:-3])
                          if '.getDouble(' in str(i['operand']) and j and b[j-1]['operand'] == 'antblocktimer'
                          and b[j+1]['operand'] == 147.)
        self.assertLess(first_sub, phase_read)
        self.assertEqual(sum('.setBlock(' in str(i['operand']) for i in b), 41)
        self.assertEqual(sum('Entity.teleportTo(' in str(i['operand']) for i in b), 40)
        self.assertEqual(sum('.isOwnedBy(' in str(i['operand']) for i in b), 20)
        self.assertFalse(any('.hurt(' in str(i['operand']) or '.addEffect(' in str(i['operand']) for i in b))

    def test_each_fixed_geometry_cell_traces_to_native_auxiliary_tag_additions(self):
        b = self.body('AntCommanderItemInInventoryTickProcedure')
        row = self.row('ant_commander_native_terrain_sequence_and_worker_reposition')
        for cell in row['native_terrain_sequence_context']['normal_branch_block_writes']:
            at = next(j for j, i in enumerate(b) if i['offset'] == cell['block_write_offset'])
            self.assertIn('LevelAccessor.setBlock(', b[at]['operand'])
            for axis, value in zip('xyz', cell['relative_xyz']):
                writes = [j for j in range(8, at) if '.putDouble(' in str(b[j]['operand'])
                          and b[j-7]['operand'] == 'antbuild_aux_' + axis]
                j = writes[-1]
                self.assertEqual(b[j-4]['operand'], 'antbuild' + axis)
                self.assertEqual((b[j-2]['operand'], b[j-1]['opcode']), (value, '0x63'))

    def test_temporary_shield_exact_registry_constructor_and_no_blockentity(self):
        entry = 'net/arphex/block/AntShieldTemporaryBlock.class'
        w = next(w for w in self.support['witnesses'] if w['entry'] == entry)
        self.assertEqual(w['superclass'], 'net/minecraft/world/level/block/Block')
        self.assertFalse(any(m['name'] == 'newBlockEntity' for m in w['methods']))
        boot = next(b for b in self.census['registration_bootstraps']
                    if b['entry'] == 'net/arphex/init/ArphexModBlocks.class' and b['index'] == 10)
        self.assertIn('net/arphex/block/AntShieldTemporaryBlock.<init>()V', boot['arguments'])
        self.assertEqual(self.row('native_temporary_ant_shield_collision_and_conditional_cleanup')
                         ['native_registry_binding']['bootstrap'], boot)

    def test_shared_cleanup_flag_needs_real_blockentity_and_has_no_fixed_timer(self):
        helper = self.support_body('TempTickProcedure')
        self.assertTrue(any(i['operand'] == 12. for i in helper))
        self.assertTrue(any(i['operand'] == 'breaknow' for i in helper))
        self.assertFalse(any('.queueServerWork(' in str(i['operand']) or '.scheduleTick(' in str(i['operand']) for i in helper))
        getter = self.support_body('TempTickProcedure$1', 'getValue')
        self.assertEqual((getter[-2]['operand'], getter[-1]['opcode']), (0, '0xac'))
        self.assertTrue(any(i['opcode'] == '0xc6' and i['branch_target'] == 24 for i in getter))
        self.assertFalse(self.row('native_temporary_ant_shield_collision_and_conditional_cleanup')
                         ['scalable_parameter_candidates'])

    def test_attack_and_projectile_cleanup_use_distinct_native_parent_rules(self):
        attack = self.support_body('AntShieldTemporaryBlock', 'attack')
        projectile = self.support_body('AntShieldTemporaryBlock', 'onProjectileHit')
        self.assertTrue(any('Block.attack(' in str(i['operand']) for i in attack))
        self.assertFalse(any('Block.onProjectileHit(' in str(i['operand']) for i in projectile))
        for body in (attack, projectile):
            self.assertTrue(any('AntShieldTemporaryOnTickUpdateProcedure.execute(' in str(i['operand']) for i in body))
            self.assertFalse(any('.hurt(' in str(i['operand']) or '.getOwner(' in str(i['operand']) for i in body))


class NativeSummonerItemContracts(NativeContractHarness, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch = read_json(OUT / 'arphex-r2m6k-native-summoner-item-contracts.json')
        cls.native = read_json(OUT / 'native-evidence/arphex-residual-native-summoner-utility.json')
        cls.census = read_json(OUT / 'arphex-combat-census.json')

    def test_bounded_native_contracts_extend_existing_jar_identity(self):
        validate_batch(self.batch, self.prior(), self.census)
        self.assertEqual((len(self.batch['effects']), len(self.batch['closed_item_callback_entries'])), (5, 6))
        self.assertEqual(sum(len(c['parameters']) for r in self.batch['effects']
                             for c in r['scalable_parameter_candidates']), 29)
        self.assertEqual([r['id'] for r in self.batch['record_refinements']], ['arphex:owned_spider_jar_native_lifecycle'])
        self.assertFalse(any(r['id'] == 'arphex:owned_spider_jar_native_lifecycle' for r in self.batch['effects']))
        self.assertFalse(self.batch['whole_mod_complete'])

    def test_health_buffer_literals_are_native_field_writes_not_live_heals(self):
        from promote_combat_batch import literal_field_numeric_binding
        for name, value, field in [('TormentorSummonerInventoryProcedure', 1024., 'tmshealthD'),
                                   ('SpiderMothSummonInventoryProcedure', 300., 'smshealthD')]:
            m = dict(instructions=self.body(name))
            binding = literal_field_numeric_binding(m, 61)
            self.assertEqual(binding['native_value'], value)
            self.assertTrue(binding['field'].endswith(field))
            self.assertEqual(binding['write'], 'INSTANCE')
            self.assertFalse(any('.heal(' in str(i['operand']) or '.setHealth(' in str(i['operand'])
                                 or '.isOnCooldown(' in str(i['operand']) for i in m['instructions']))
            self.assertEqual(next(i for i in m['instructions'] if i['offset'] == 117)['opcode'], '0x63')
            bad = copy.deepcopy(m)
            next(i for i in bad['instructions'] if i['offset'] == 58)['opcode'] = '0x63'
            with self.assertRaises(AssertionError):
                literal_field_numeric_binding(bad, 61)
        batch = copy.deepcopy(self.batch)
        row = next(r for r in batch['effects'] if r['id'].endswith(':native_summoner_per_stack_attached_health_regeneration'))
        row['components'][0]['numerical_parameters']['initial_value'] += 1
        with self.assertRaises(AssertionError):
            validate_batch(batch, self.prior(), self.census)

    def test_dismissal_checks_ownership_at_delivery_and_lightning_visual_flag(self):
        for name in ('TormentorPortalRightClixProcedure', 'SpiderMothPortalRightclickedProcedure'):
            early = self.body(name)
            self.assertFalse(any('.isOnCooldown(' in str(i['operand']) for i in early))
            b = self.body(name, 'lambda$execute$2')
            calls = [i['operand'] for i in b if i['opcode'] in ('0xb6', '0xb9')]
            for part in ('.isOnCooldown(', '.isOwnedBy(', '.isAlive(', '.discard(', '.setVisualOnly('):
                self.assertTrue(any(part in c for c in calls))
            j = next(j for j, i in enumerate(b) if '.setVisualOnly(' in str(i['operand']))
            self.assertEqual(b[j-1]['operand'], 1)
            self.assertFalse(any('.hurt(' in c or '.setOwner(' in c for c in calls))

    def test_tormentor_swing_rechecks_native_vehicle_without_owner_assignment(self):
        b = self.body('TormentorSummonerEntitySwingsItemProcedure', 'lambda$execute$0')
        self.assertTrue(any('.isPassenger(' in str(i['operand']) for i in b))
        self.assertTrue(any(i['opcode'] == '0xc1' and i['operand'].endswith('/TormentorSummonEntity') for i in b))
        self.assertTrue(any('PlayerVariables.killedtormentorD' in str(i['operand']) for i in b))
        self.assertTrue(any('SUMMON_SUN_BLAST' in str(i['operand']) for i in b))
        self.assertFalse(any('.setOwner(' in str(i['operand']) or '.isOwnedBy(' in str(i['operand']) for i in b))
        row = self.row('tormentor_summoner_native_vehicle_sun_blast_trigger')
        self.assertIn('arphex:summon_sun_blast_native_generic_field_motion_and_size', row['canonical_contract_reuse'])
        self.assertFalse(any(c['primitive'] == 'NATIVE_DAMAGE_REQUEST' for c in row['scalable_parameter_candidates']))

    def test_moth_later_pulses_preserve_carrier_type_veto_without_mount_recheck(self):
        first = self.body('SpiderMothSummonerEntitySwingsItemProcedure', 'lambda$execute$12')
        at = next(j for j, i in enumerate(first) if i['offset'] == 182)
        self.assertEqual(first[at-1]['opcode'], '0x2a')  # static lambda carrier argument0
        for method in ('lambda$execute$9', 'lambda$execute$6'):
            b = self.body('SpiderMothSummonerEntitySwingsItemProcedure', method)
            at = next(j for j, i in enumerate(b) if i['opcode'] == '0xc1' and i['operand'].endswith('/SpiderMothSummonEntity'))
            self.assertEqual(b[at-1]['local_index'], 7)  # captured carrier, not query recipient
            self.assertFalse(any('.isPassenger(' in str(i['operand']) or '.getVehicle(' in str(i['operand'])
                                 or '.isOnCooldown(' in str(i['operand']) for i in b))
            self.assertTrue(any('.isOwnedBy(' in str(i['operand']) for i in b))
        row = self.row('moth_summoner_native_vehicle_three_wither_pulses')
        self.assertEqual(sum(c['primitive'].startswith('MOB_EFFECT_WITHER_PULSE_') for c in row['components']), 3)
        times = next(c for c in row['components'] if c['primitive'] == 'DELAYED_NATIVE_PULSES')['numerical_parameters']
        self.assertEqual(times['initial_delay'], 4)
        self.assertEqual([v for k, v in times.items() if k != 'initial_delay'], [3]*6)
        self.assertNotIn(13, times.values())
        self.assertNotIn(22, times.values())

    def test_jar_regeneration_is_unconditional_stack_resource_not_a_default_pet_heal(self):
        for name in ('SpiderJarItemInInventoryTickProcedure', 'JumpJarTickProcedure'):
            b = self.body(name)
            self.assertTrue(any(i['operand'] == .05 for i in b))
            self.assertTrue(any(i['opcode'] == '0x63' for i in b))
            self.assertFalse(any('.setHealth(' in str(i['operand']) or '.heal(' in str(i['operand']) for i in b))
        b = self.body('SpiderCrabJarRightclickedProcedure', 'lambda$execute$5')
        self.assertTrue(any(i['operand'] == 'Spider Crab Jar' for i in b))
        self.assertTrue(any('.setHealth(' in str(i['operand']) for i in b))
        self.assertGreater(sum('CrabLarvaeEntity' == str(i['operand']).split('/')[-1] for i in b), 1)
        root = self.body('SpiderCrabJarItem', 'use')
        self.assertTrue(any('SpiderCrabJarRightclickedProcedure.execute(' in str(i['operand']) for i in root))

    def test_bucket_has_eight_exact_unowned_spawns_and_positive_z_point_five(self):
        b = self.body('BucketOfWormGrubRightclickedProcedure')
        self.assertEqual(sum('EntityType.spawn(' in str(i['operand']) for i in b), 8)
        self.assertFalse(any('.tame(' in str(i['operand']) or '.setOwner(' in str(i['operand'])
                             or '.hurt(' in str(i['operand']) for i in b))
        j = next(j for j, i in enumerate(b) if i['offset'] == 475)
        self.assertEqual([i['operand'] for i in b[j-3:j]], [0., 0., .5])
        self.assertIn('NATIVE_ENCOUNTER_SETUP_REUSED', {e['disposition'] for e in self.batch['exclusions']})

    def test_native_crab_nearest_comparators_bind_exact_xyz_squared_distance(self):
        support = read_json(OUT / 'native-evidence/arphex-native-summoner-item-support.json')
        self.assertEqual(len(support['witnesses']), 3)
        for witness in support['witnesses']:
            method = next(m for m in witness['methods'] if m['name'] == 'lambda$compareDistOf$0')
            self.assertEqual(method['descriptor'], '(DDDLnet/minecraft/world/entity/Entity;)D')
            b = method['instructions']
            self.assertEqual(b[-2]['operand'], 'net/minecraft/world/entity/Entity.distanceToSqr(DDD)D')
            self.assertEqual(b[-1]['opcode'], '0xaf')
            self.assertEqual(b[0]['local_index'], 6)


class NativePassiveUtilityContracts(NativeContractHarness, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch = read_json(OUT / 'arphex-r2m6j-native-passive-utility-contracts.json')
        cls.native = read_json(OUT / 'native-evidence/arphex-residual-native-summoner-utility.json')
        cls.census = read_json(OUT / 'arphex-combat-census.json')

    def test_bounded_scope_keeps_captured_control_callbacks_pending(self):
        validate_batch(self.batch, self.prior(), self.census)
        self.assertEqual((len(self.batch['effects']), len(self.batch['closed_item_callback_entries'])), (9, 14))
        self.assertEqual(sum(len(c['parameters']) for r in self.batch['effects']
                             for c in r['scalable_parameter_candidates']), 42)
        self.assertEqual((len(self.native['witnesses']), sum(len(w['methods'])
                         for w in self.native['witnesses'])), (69, 379))
        pending = self.batch['captured_but_unreviewed_entries']
        for name in ('AntCommanderItem', 'TormentorSummonerItem', 'VitalityViewfinderItem',
                     'CrawlingContainerItem', 'ScorchChargeItem'):
            self.assertTrue(any(e.endswith('/' + name + '.class') for e in pending))
        self.assertFalse(self.batch['whole_mod_complete'])

    def test_core_selected_forwarding_and_ordered_native_payload(self):
        root = self.body('CoreOfEternalSufferingItem', 'inventoryTick')
        call = next(j for j, i in enumerate(root) if 'CoreOfEternalSufferingItemInInventoryTickProcedure.execute(' in str(i['operand']))
        self.assertTrue(any(i['opcode'] == '0x99' for i in root[:call]))
        b = self.body('CoreOfEternalSufferingItemInInventoryTickProcedure')
        requests = [(i['offset'], i['operand']) for i in b if '.igniteForSeconds(' in str(i['operand'])
                    or 'MobEffectInstance.<init>(' in str(i['operand'])]
        self.assertEqual([o for o, _ in requests], [147, 190, 237, 284, 331, 378])
        holders = [i['operand'] for i in b if 'MobEffects.' in str(i['operand']) and i['opcode'] == '0xb2']
        self.assertEqual([x.split('.')[-1].split('Lnet/')[0] for x in holders],
                         ['WITHER', 'BLINDNESS', 'NECROSIS', 'INVISIBILITY', 'MOTH_CURSE'])
        for j, i in enumerate(b):
            if '.addEffect(' in str(i['operand']):
                self.assertEqual(b[j+1]['opcode'], '0x57')

    def test_mantle_removal_is_ordered_and_has_no_immunity_or_heal(self):
        b = self.body('MantleOfVitalityItemInInventoryTickProcedure')
        holders = [i['operand'] for i in b if i['opcode'] == '0xb2' and 'MobEffects.' in str(i['operand'])]
        self.assertEqual([x.split('.')[-1].split('Lnet/')[0] for x in holders], ['WITHER', 'POISON', 'NECROSIS'])
        self.assertEqual(sum('.removeEffect(' in str(i['operand']) for i in b), 3)
        self.assertFalse(any('.addEffect(' in str(i['operand']) or '.heal(' in str(i['operand']) for i in b))
        self.assertFalse(self.row('mantle_and_native_satchel_status_removal')['scalable_parameter_candidates'])

    def test_bane_command_arguments_bind_to_native_literal_and_reject_false_values(self):
        from promote_combat_batch import literal_effect_command_arguments
        m = dict(instructions=self.body('BaneOfTheDarknessItemInInventoryTickProcedure'))
        args = literal_effect_command_arguments(m, 116)
        self.assertEqual((args['selector_distance_max'], args['duration_seconds'], args['amplifier']), (30., 1, 1))
        for parameter in ('radius', 'duration_seconds', 'amplifier'):
            batch = copy.deepcopy(self.batch)
            row = next(r for r in batch['effects'] if r['id'].endswith(':bane_and_native_satchel_darkness_removal_and_status_delivery'))
            component = next(c for c in row['components'] if c['primitive'] == 'NATIVE_STATUS_COMMAND')
            component['numerical_parameters'][parameter] += 1
            with self.assertRaisesRegex(AssertionError, 'component differs from native command arguments'):
                validate_batch(batch, self.prior(), self.census)
        bad = copy.deepcopy(m)
        next(i for i in bad['instructions'] if i['offset'] == 114)['opcode'] = '0xba'
        with self.assertRaises(AssertionError):
            literal_effect_command_arguments(bad, 116)

    def test_satchel_consumes_distinct_slots_and_native_boolean_lens_read(self):
        b = self.body('ProwlerPackItemInInventoryTickProcedure')
        self.assertTrue(any(i['operand'] == 90 for i in b))
        self.assertTrue(any(i['operand'] == 91 for i in b))
        self.assertEqual(sum(i['operand'] == 92 for i in b), 2)
        j = next(j for j, i in enumerate(b) if i['operand'] == 'lensmode')
        self.assertIn('CompoundTag.getBoolean(', b[j+1]['operand'])
        self.assertFalse(any('.hurt(' in str(i['operand']) for i in b))
        motion = next(j for j, i in enumerate(b) if '.setDeltaMovement(' in str(i['operand']))
        self.assertTrue(any(i['opcode'] == '0xc1' and i['operand'].endswith('/ItemEntity') for i in b[:motion]))

    def test_spray_has_three_combat_rays_and_hurt_result_does_not_gate_slowness(self):
        b = self.body('BugSprayRightclickedProcedure')
        scales = [b[j-1]['operand'] for j, i in enumerate(b) if '.scale(' in str(i['operand'])]
        self.assertEqual(scales, [2., 2., 2., 3., 3., 3.])
        j = next(j for j, i in enumerate(b) if i['offset'] == 528)
        self.assertEqual(b[j+1]['opcode'], '0x57')
        self.assertTrue(any('DamageSource.<init>(Lnet/minecraft/core/Holder;)V' in str(i['operand']) for i in b))
        row = self.row('bug_spray_native_arthropod_area_damage_and_slowness')
        ranges = next(c for c in row['components'] if c['primitive'] == 'NATIVE_RAY_DELIVERY')
        self.assertEqual(set(ranges['numerical_parameters'].values()), {3.})

    def test_parachute_absolute_y_and_inventory_status_have_separate_gates(self):
        b = self.body('ProwlerParachuteRightclickedProcedure')
        self.assertTrue(any('.isOnCooldown(' in str(i['operand']) for i in b))
        self.assertTrue(any(i['operand'] == .6 for i in b))
        self.assertFalse(any('.onGround(' in str(i['operand']) or '.isPassenger(' in str(i['operand']) for i in b))
        held = self.body('ProwlerParachuteItemInHandTickProcedure')
        self.assertFalse(any('.isOnCooldown(' in str(i['operand']) for i in held))
        self.assertEqual(sum('.addEffect(' in str(i['operand']) for i in held), 2)

    def test_cooldown_override_has_no_creative_gate_and_uses_replacement_not_removal(self):
        b = self.body('CreativeCooldownResetRightclickedProcedure')
        calls = [i for i in b if '.addCooldown(' in str(i['operand'])]
        self.assertEqual(len(calls), 5)
        self.assertFalse(any('.removeCooldown(' in str(i['operand']) or 'GameType' in str(i['operand'])
                             or '.isCreative(' in str(i['operand']) for i in b))
        for j, i in enumerate(b):
            if '.addCooldown(' in str(i['operand']):
                self.assertEqual(b[j-1]['operand'], 1)
        self.assertTrue(any('PlayerVariables.inherent_power_cooldown' in str(i['operand']) for i in b))


class NativeSpatialItemContracts(NativeContractHarness, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch=read_json(OUT/'arphex-r2m6i-native-spatial-item-contracts.json')
        cls.support=read_json(OUT/'native-evidence/arphex-native-spatial-item-support.json')
        cls.native=read_json(OUT/'native-evidence/arphex-residual-native-staff-launcher.json')
        cls.native={'witnesses':cls.native['witnesses']+cls.support['witnesses']}
        cls.census=read_json(OUT/'arphex-combat-census.json')

    def test_bounded_spatial_contracts_preserve_utility_and_pending_real_consumers(self):
        validate_batch(self.batch,self.prior(),self.census)
        self.assertEqual(len(self.batch['effects']),3)
        self.assertEqual(len(self.batch['closed_item_callback_entries']),5)
        self.assertEqual(sum(len(c['parameters']) for r in self.batch['effects'] for c in r['scalable_parameter_candidates']),14)
        self.assertEqual(len(self.batch['exclusions']),3)
        self.assertFalse(self.batch['whole_mod_complete'])
        self.assertTrue(any('button' in x for x in self.batch['pending_shared_contexts']))

    def test_warp_inventory_helper_unconditional_and_final_fall_reset_outside_gate(self):
        root=self.body('WarpStaffItem','inventoryTick')
        self.assertFalse(any(i.get('branch_target') is not None for i in root))
        b=self.body('WarpStaffToolInHandTickProcedure')
        self.assertEqual(b[-1]['opcode'],'0xb1')
        self.assertTrue('fallDistance' in str(b[-2]['operand']))
        self.assertTrue(any(i.get('branch_target')==b[-4]['offset'] or i.get('branch_target')==b[-3]['offset'] for i in b))
        self.assertFalse(any('.getTicksUsingItem(' in str(i['operand']) for i in b))

    def test_warp_three_separate_native_rays_round_float_before_centering(self):
        b=self.body('WarpStaffToolInHandTickProcedure')
        self.assertEqual([i['offset'] for i in b if 'Vec3.scale(' in str(i['operand'])],[590,1007,1420])
        for o in (590,1007,1420):
            at=next(n for n,i in enumerate(b) if i['offset']==o)
            self.assertEqual(b[at-1]['operand'],30.)
        rounds=[n for n,i in enumerate(b) if i['operand']=='java/lang/Math.round(F)I']
        self.assertEqual(len(rounds),3)
        self.assertTrue(all(b[n-1]['opcode']=='0x86' and b[n+1]['opcode']=='0x87' for n in rounds))
        self.assertFalse(any('.hurt(' in str(i['operand']) or '.addEffect(' in str(i['operand']) for i in b))
        self.assertIn('arphex:warp_staff_native_uuid_locked_direction_carrier',self.row('warp_staff_native_direction_teleport_and_support_platform')['canonical_contract_reuse'])

    def test_warp_command_geometry_and_air_tag_are_exact_native_facts(self):
        b=self.body('WarpStaffRightclickedProcedure')
        cmd=next(i['operand'] for i in b if isinstance(i['operand'],str) and i['operand'].startswith('/fill'))
        self.assertEqual(cmd,'/fill ~-1 ~ ~-1 ~1 ~ ~1 arphex:warp_manifold[type=top] replace #arphex:airs')
        self.assertFalse(any('.isOnCooldown(' in str(i['operand']) for i in b))
        tag=next(w for w in self.support['witnesses'] if w['entry']=='data/arphex/tags/block/airs.json')
        self.assertEqual(tag['data'],{'replace':False,'values':['minecraft:air','minecraft:void_air','minecraft:cave_air']})
        reg=self.body('ArphexModBlocks','<clinit>');at=next(n for n,i in enumerate(reg) if i['operand']=='warp_manifold')
        self.assertIn('bootstrap#21:',reg[at+1]['operand'])
        self.assertIn('.register(',reg[at+2]['operand'])
        self.assertIn('.WARP_MANIFOLD',reg[at+3]['operand'])
        handle=next(r for r in self.census['registration_bootstraps'] if r['entry']=='net/arphex/init/ArphexModBlocks.class' and r['index']==21)
        self.assertIn('net/arphex/block/WarpManifoldBlock.<init>()V',handle['arguments'])

    def test_platform_factor_rejects_false_or_computed_literals(self):
        from promote_combat_batch import literal_block_factor_binding
        m=dict(instructions=copy.deepcopy(self.body('WarpManifoldBlock','<init>')))
        self.assertEqual(literal_block_factor_binding(m,29)['native_value'],1.5)
        next(i for i in m['instructions'] if i['offset']==27)['opcode']='0x6a'
        with self.assertRaises(AssertionError):literal_block_factor_binding(m,29)
        b=copy.deepcopy(self.batch);r=next(r for r in b['effects'] if r['id'].endswith(':warp_manifold_native_jump_and_conditional_terrain_lifecycle'))
        r['components'][0]['numerical_parameters']['factor']=2.
        with self.assertRaisesRegex(AssertionError,'component differs from native block factor'):
            validate_batch(b,self.prior(),self.census)

    def test_platform_native_schedule_and_presence_cleanup_not_particle_delay(self):
        on=self.body('WarpManifoldBlock','onPlace');tick=self.body('WarpManifoldBlock','tick')
        self.assertEqual(on[-3]['operand'],10);self.assertEqual(tick[-3]['operand'],10)
        helper=self.body('WarpManifoldOnTickUpdateProcedure');by={i['offset']:i for i in helper}
        self.assertIn('scheduleTick',on[-2]['operand']);self.assertIn('scheduleTick',tick[-2]['operand'])
        self.assertEqual(by[56]['operand'],5)
        delayed=self.body('WarpManifoldOnTickUpdateProcedure','lambda$execute$0')
        self.assertTrue(any('.sendParticles(' in str(i['operand']) for i in delayed))
        self.assertFalse(any('.setBlock(' in str(i['operand']) for i in delayed))
        self.assertEqual(by[111]['branch_target'],135)
        self.assertIn('.setBlock(',by[129]['operand'])
        self.assertFalse(any('WarpManifoldBlock' in str(i['operand']) or '.isOwnedBy(' in str(i['operand']) for i in helper))

    def test_transmitter_is_offhand_building_and_preview_only_not_named_time_payload(self):
        p=self.body('TemporalTransmitterItemInHandTickProcedure')
        forbidden=['.hurt(','.addEffect(','.setDeltaMovement(','.setBlock(','.teleportTo(']
        self.assertFalse(any(any(s in str(i['operand']) for s in forbidden) for i in p))
        self.assertTrue(any('.addParticle(' in str(i['operand']) for i in p))
        b=self.body('TemporalTransmitterRightclickedOnBlockProcedure')
        self.assertEqual(sum('.setBlock(' in str(i['operand']) for i in b),2)
        self.assertTrue(any('.getOffhandItem(' in str(i['operand']) for i in b))
        self.assertTrue(any('ARPHEX_BLOCK_GRIEFING' in str(i['operand']) for i in b))
        self.assertFalse(any('.hurt(' in str(i['operand']) or 'TIME_FREEZE' in str(i['operand']) for i in b))

    def test_waypoint_callbacks_are_storage_menu_not_teleport_but_consumer_stays_pending(self):
        for name in ['WarpWayfinderRightclickedOnBlockProcedure','WarpWayfinderItemInHandTickProcedure','WarpConnectorRightclickedProcedure','WarpConnectorItemInHandTickProcedure','PlaceholderWarpProcedure']:
            for w in self.native['witnesses']:
                if not w['entry'].endswith('/'+name+'.class'):continue
                self.assertFalse(any('.teleportTo(' in str(i['operand']) or '.hurt(' in str(i['operand']) or '.addEffect(' in str(i['operand']) for m in w['methods'] for i in m['instructions']))
        menu=self.body('WarpWayfinderItem$1','createMenu')
        self.assertTrue(any('WayfinderMenu.<init>' in str(i['operand']) for i in menu))
        self.assertTrue(any('button' in p.lower() for p in self.batch['pending_shared_contexts']))
