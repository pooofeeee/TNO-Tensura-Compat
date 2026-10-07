"""Independent native item inputs, callback receivers and registry reachability."""
import copy
import unittest

from catalog_common import OUT, read_json
from promote_combat_batch import (literal_item_attribute_binding,
    literal_item_wear_binding, literal_numeric_return_binding, refined_review,
    validate_batch)
from reconcile_native_census import reconcile
from test_shadow_clone_contracts import NativeContractHarness


class NativeItemContextTests(NativeContractHarness, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch = read_json(OUT / 'arphex-r2m7p-native-item-context.json')
        cls.native = read_json(OUT / 'native-evidence/arphex-native-item-context.json')
        cls.census = read_json(OUT / 'arphex-combat-census.json')

    def method(self, name, method):
        return next(m for w in self.native['witnesses']
                    if w['entry'].endswith('/' + name + '.class')
                    for m in w['methods'] if m['name'] == method)

    def test_bounded_scope_and_independent_census_hashes(self):
        self.assertEqual((len(self.native['witnesses']), sum(len(w['methods'])
                         for w in self.native['witnesses'])), (205, 331))
        self.assertEqual(len(self.batch['effects']), 2)
        self.assertEqual(len(self.batch['record_refinements']), 2)
        validate_batch(self.batch, self.prior(), self.census)
        count = lambda rows: sum(len(c['parameters']) for r in rows
                                 for c in r['scalable_parameter_candidates'])
        self.assertEqual(count(self.batch['effects']), 23)
        self.assertEqual(sum(len(c['parameters']) for r in self.batch['record_refinements']
                             for c in r['candidate_additions']), 1)
        indexed = {(m['entry'], m['method'], m['descriptor']): m
                   for m in self.census['methods']}
        for w in self.native['witnesses']:
            for m in w['methods']:
                self.assertEqual(indexed[(w['entry'], m['name'], m['descriptor'])]
                                 ['code_sha256'], m['code_sha256'])

    def test_constructor_reachability_is_exact_registry_bootstrap_and_call(self):
        rows = self.batch['native_registered_item_context']
        self.assertEqual(len(rows), 11)
        self.assertEqual(len({r['entry'] for r in rows}), 11)
        for r in rows:
            self.assertIn(r['bootstrap'], self.census['registration_bootstraps'])
            self.assertIn(r['entry'][:-6] + '.<init>()V', r['bootstrap']['arguments'])
            p = r['registry_initializer']
            w = next(w for w in read_json(OUT / p['evidence_file'])['witnesses']
                     if w['id'] == p['witness_id'])
            m = next(m for m in w['methods'] if m['name'] == '<clinit>')
            body = m['instructions']; slice_ = r['registry_instructions']
            start = next(n for n, i in enumerate(body) if i['offset'] == slice_[0]['offset'])
            self.assertEqual(slice_, body[start:start + 5])
            self.assertEqual([slice_[n]['opcode'] for n in (0, 2, 3, 4)],
                             ['0xb2', '0xba', '0xb6', '0xb3'])
            self.assertIn(slice_[1]['opcode'], ('0x12', '0x13'))
            self.assertIsInstance(slice_[1]['operand'], str)
            self.assertTrue(slice_[2]['operand'].startswith('bootstrap#' +
                            str(r['bootstrap']['index']) + ':'))
            self.assertIn('DeferredRegister$Items.register(', slice_[3]['operand'])

    def test_mainhand_inputs_preserve_signed_value_operation_and_native_roles(self):
        expected = {'AbyssalAnnihilatorItem': 5., 'BlackWidowBowItem': 4.,
            'ChronoCannonItem': 17., 'DaggerOfDissolutionItem': 3.,
            'FormicFireblasterItem': 4., 'GenesisRifleItem': 19.,
            'HypnoticHellblasterItem': 5., 'JudgementBlasterItem': 5.,
            'TormentedWrathItem': 24., 'VengefulVoidseekerItem': 5.}
        for name, damage in expected.items():
            m = self.method(name, '<init>')
            hits = [i for i in m['instructions'] if 'AttributeModifier.<init>('
                    in str(i['operand'])]
            self.assertEqual(len(hits), 2)
            bindings = [literal_item_attribute_binding(m, i['offset']) for i in hits]
            for b, attribute, value in zip(bindings, ['ATTACK_DAMAGE', 'ATTACK_SPEED'],
                                           [damage, -2.4]):
                self.assertIn('Attributes.' + attribute, b['attribute_symbol'])
                self.assertEqual(b['native_value'], value)
                self.assertIn('.ADD_VALUE', b['operation_symbol'])
                self.assertIn('.MAINHAND', b['slot_symbol'])
        m = self.method('MantisMacheteItem', '<init>')
        hit = next(i for i in m['instructions'] if 'SwordItem.createAttributes('
                   in str(i['operand']))
        b = literal_item_attribute_binding(m, hit['offset'])
        self.assertEqual((b['attack_bonus'], b['attack_speed']), (9., -3.200000047683716))
        for name in ('MantisMacheteItem$1', 'AbyssAtomiserItem$1'):
            body = self.body(name, 'getAttackDamageBonus')
            self.assertEqual([(i['opcode'], i['operand']) for i in body],
                             [('0xb', 0.), ('0xae', None)])

    def test_wrong_attribute_values_or_parameter_roles_are_rejected(self):
        b = copy.deepcopy(self.batch)
        row = next(r for r in b['effects'] if r['primary_classification'] == 'VANILLA_DIRECT')
        key = next(iter(row['components'][0]['numerical_parameters']))
        row['components'][0]['numerical_parameters'][key] += 1
        with self.assertRaisesRegex(AssertionError, 'component differs from pinned item attribute'):
            validate_batch(b, self.prior(), self.census)
        b = copy.deepcopy(self.batch)
        row = next(r for r in b['effects'] if r['primary_classification'] == 'VANILLA_DIRECT')
        c = next(c for c in row['scalable_parameter_candidates']
                 if c['native_consumer']['entry'].endswith('/MantisMacheteItem.class'))
        c['native_item_attribute_parameter_roles'] = {p: 'attack_bonus' for p in c['parameters']}
        with self.assertRaises(AssertionError): validate_batch(b, self.prior(), self.census)

    def test_dagger_wear_uses_victim_twice_and_never_supplied_attacker(self):
        m = self.method('DaggerOfDissolutionItem', 'hurtEnemy'); body = m['instructions']
        self.assertEqual([i.get('local_index') for i in body[:4]], [1, None, 2, 2])
        b = literal_item_wear_binding(m, 10)
        self.assertEqual((b['native_value'], b['stack_local_index'],
                          b['entity_local_index'], b['hand_entity_local_index']), (1, 1, 2, 2))
        self.assertFalse(any(i.get('local_index') == 3 or i['opcode'] == '0xb7' for i in body))
        self.assertEqual([(i['opcode'], i['operand']) for i in body[-2:]],
                         [('0x4', 1), ('0xac', None)])
        bad = copy.deepcopy(m); bad['instructions'][3]['local_index'] = 3
        with self.assertRaises(AssertionError): literal_item_wear_binding(bad, 10)
        batch = copy.deepcopy(self.batch)
        row = next(r for r in batch['effects'] if r['id'].endswith(':dagger_native_hurt_enemy_durability'))
        row['components'][0]['numerical_parameters']['cost'] = 2
        with self.assertRaisesRegex(AssertionError, 'component differs from native item wear'):
            validate_batch(batch, self.prior(), self.census)

    def test_numeric_return_is_complete_typed_body_and_excludes_binary_gate(self):
        m = self.method('VengefulVoidseekerItem', 'getUseDuration')
        self.assertEqual(literal_numeric_return_binding(m, 2),
                         dict(native_value=60, value_offset=0, return_descriptor='I'))
        bad = copy.deepcopy(m); bad['descriptor'] = '()Z'
        with self.assertRaises(AssertionError): literal_numeric_return_binding(bad, 2)
        bad = copy.deepcopy(m); bad['instructions'].insert(1, dict(offset=1, opcode='0x60', operand=None))
        with self.assertRaises(AssertionError): literal_numeric_return_binding(bad, 2)
        bad = copy.deepcopy(m); bad['descriptor'] = '()J'
        with self.assertRaises(AssertionError): literal_numeric_return_binding(bad, 2)

    def test_voidseeker_returns_original_parent_result_after_unconditional_start(self):
        body = self.body('VengefulVoidseekerItem', 'use')
        self.assertEqual([i['local_index'] for i in body[:4]], [0, 1, 2, 3])
        self.assertIn('Item.use(', body[4]['operand'])
        self.assertEqual(body[5]['local_index'], 4)
        self.assertEqual([i['local_index'] for i in body[6:8]], [2, 3])
        self.assertIn('Player.startUsingItem(', body[8]['operand'])
        self.assertEqual(body[9]['local_index'], 4)
        self.assertEqual(body[10]['opcode'], '0xb0')
        self.assertEqual(len(body), 11)
        release = self.body('VengefulVoidseekerItem', 'releaseUsing')
        self.assertEqual(len(release), 2)
        self.assertIn('RequiredForAnimProcedure.execute()V', release[0]['operand'])

    def test_flame_release_and_drop_keep_native_callback_inputs(self):
        for name in ('FormicFireblasterItem', 'HypnoticHellblasterItem', 'JudgementBlasterItem'):
            for callback, local, opcodes in [('releaseUsing', 3, ['0x2d', '0xb8', '0xb1']),
                    ('onDroppedByPlayer', 2, ['0x2c', '0xb8', '0x4', '0xac'])]:
                body = self.body(name, callback)
                self.assertEqual([i['opcode'] for i in body], opcodes)
                self.assertEqual(body[0]['local_index'], local)
                self.assertIn('FormicFireblasterOnPlayerStoppedUsingProcedure.execute(', body[1]['operand'])

    def test_glint_queries_preserve_repeated_native_reads_and_no_authored_writers(self):
        for name, queries, symbol in [('AbyssalBladeHasItemGlowingEffectProcedure', 3, 'ABYSSAL_DETECTOR'),
                                     ('GlowUseProcedure', 2, 'FORCE_POWER')]:
            body = self.body(name)
            self.assertEqual(sum('.getEntitiesOfClass(' in str(i['operand']) for i in body), queries)
            self.assertEqual(sum(i['operand'] == 20. for i in body), queries * 3)
            self.assertTrue(any('ArphexModMobEffects.' + symbol in str(i['operand']) for i in body))
            self.assertFalse(any(i['opcode'] in ('0xb3', '0xb5') or any(s in str(i['operand'])
                for s in ('.hurt(', '.addEffect(', '.setDeltaMovement(', '.putBoolean(')) for i in body))
        self.assertTrue(any(i['operand'] == 'tormentor_target'
                            for i in self.body('AbyssalBladeHasItemGlowingEffectProcedure')))
        body = self.body('ProwlerGraspProcedure')
        self.assertTrue(any(i['operand'] == 'graspmode' for i in body))
        self.assertTrue(any('CustomData.copyTag()' in str(i['operand']) for i in body))

    def test_changed_native_item_hash_cannot_close_census(self):
        r = refined_review(self.prior(), self.batch)
        r['effects'] += self.batch['effects']; r['paths'] += self.batch['paths']
        r['reviewed_batches'] = list(set(r['reviewed_batches'] + ['arphex-r2m7p-native-item-context.json']))
        e = copy.deepcopy(self.native); e['witnesses'][0]['methods'][0]['code_sha256'] = '0' * 64
        def read(path):
            return e if path.name == 'arphex-native-item-context.json' else read_json(path)
        with self.assertRaisesRegex(AssertionError, 'hash mismatch'): reconcile(r, self.census, read=read)


if __name__ == '__main__': unittest.main()
