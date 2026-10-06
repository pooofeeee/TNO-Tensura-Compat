import copy
import unittest

from catalog_common import OUT, read_json, sha256
from validate_arrow_factory_kernels import validate
from promote_combat_batch import validate_batch
from update_arrow_producer_queue import update


class ArrowFactoryKernelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = read_json(OUT/'arphex-projectile-producer-kernel-registry.json')
        cls.census = read_json(OUT/cls.registry['finite_census_file'])

    def test_exact_native_methods_and_direct_callers(self):
        result = validate(self.registry, self.census)
        self.assertEqual(result['factories'], 137)
        self.assertEqual(result['native_methods'], 548)

    def test_owner_free_factory_cannot_be_given_a_source(self):
        changed = copy.deepcopy(self.registry)
        row = next(r for r in changed['rows'] if r['owner_set_offset'] is None)
        self.assertIn('PartispinEntitySwingsItemProcedure', row['factory']['entry'])
        row['owner_set_offset'] = 27
        with self.assertRaises(AssertionError):
            validate(changed, self.census)

    def test_native_method_hash_mutation_is_rejected(self):
        changed = copy.deepcopy(self.registry)
        changed['rows'][0]['knockback']['code_sha256'] = '0'*64
        with self.assertRaises(AssertionError):
            validate(changed, self.census)

    def test_kernel_proof_cannot_close_the_mod(self):
        changed = copy.deepcopy(self.registry)
        changed['whole_mod_complete'] = True
        with self.assertRaises(AssertionError):
            validate(changed, self.census)

    def test_native_knockback_and_piercing_body_semantics(self):
        row = self.registry['rows'][0]
        evidence = read_json(OUT/row['knockback']['evidence_file'])
        witness = next(w for w in evidence['witnesses'] if w['id'] == row['knockback']['witness_id'])
        body = next(m['instructions'] for m in witness['methods'] if m['name'] == 'doKnockback')
        self.assertEqual(body[2]['branch_target'], 77)  # nonpositive captured knockback returns
        self.assertTrue(any(i['operand'] == .6 for i in body))
        self.assertTrue(any(i['operand'] == .1 for i in body))
        self.assertTrue(any('KNOCKBACK_RESISTANCE' in str(i['operand']) for i in body))
        self.assertFalse(any('.doKnockback(' in str(i['operand']) for i in body))
        piercing = next(m['instructions'] for m in witness['methods'] if m['name'] == 'getPierceLevel')
        self.assertEqual([i['opcode'] for i in piercing], ['0x2a', '0xb4', '0xac'])
        self.assertTrue(piercing[1]['operand'].endswith('.val$piercingB'))


class SmallWeaponProducerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch = read_json(OUT/'arphex-r2m4a-small-swing-and-hook-producers.json')
        cls.census = read_json(OUT/'arphex-combat-census.json')
        cls.native = read_json(OUT/'native-evidence/arphex-weapon-projectile-producers.json')
        cls.setup = read_json(OUT/'native-evidence/arphex-small-weapon-setup.json')

    def method(self, name, method, setup=False):
        packet = self.setup if setup else self.native
        witness = next(w for w in packet['witnesses'] if w['entry'].endswith('/'+name+'.class'))
        return next(m for m in witness['methods'] if m['name'] == method)

    def prior_review(self):
        review = copy.deepcopy(read_json(OUT/'mod-reviews/arphex.json'))
        ids = {r['id'] for r in self.batch['effects']}
        review['effects'] = [r for r in review['effects'] if r['id'] not in ids]
        review['paths'] = [p for p in review['paths'] if not set(p['effect_ids']) & ids]
        return review

    def test_six_source_contracts_with_independent_native_sinks(self):
        result = validate_batch(self.batch, self.prior_review(), self.census)
        self.assertEqual(result['semantic_records'], len(self.prior_review()['effects'])+6)
        self.assertEqual(sum(len(c['parameters']) for r in self.batch['effects']
                             for c in r['scalable_parameter_candidates']), 30)

    def test_wrong_factory_value_and_role_are_rejected(self):
        for kind in ('value', 'role'):
            changed = copy.deepcopy(self.batch)
            c = next(c for r in changed['effects'] for c in r['scalable_parameter_candidates']
                     if 'native_arrow_factory_binding' in c)
            if kind == 'value':
                c['native_arrow_factory_binding']['literal_arguments']['base_damage']['value'] = 999
            else:
                c['native_arrow_factory_binding']['parameter_role'] = 'piercing'
            with self.assertRaises(AssertionError):
                validate_batch(changed, self.prior_review(), self.census)

    def test_sling_clock_trigger_polarity_and_increment(self):
        body = self.method('SlingWebRightclickedProcedure', 'execute', True)['instructions']
        by = {i['offset']: i for i in body}
        self.assertEqual([(by[n]['opcode'], by[n]['branch_target']) for n in (18,34,50)],
                         [('0x9e',53), ('0x99',53), ('0x9a',164)])
        self.assertEqual([by[n]['operand'] for n in (14,30,46,179)], [2.0,5.0,9.0,1.0])
        self.assertEqual(by[180]['opcode'], '0x63')
        self.assertIn('.putDouble(', by[181]['operand'])
        for r in self.batch['effects']:
            if 'hook_delivery' in r['id']:
                self.assertIn('slingtime<=2 OR ==5 OR ==9', r['actual_behavior'])

    def test_selected_holding_precedes_cleanup_and_has_no_cooldown_check(self):
        for item, helper in [('SilkSlingerItem','SlingWebItemInHandTickProcedure'),
                             ('TarantulaTetherItem','TarantulaTetherHoldingTickProcedure')]:
            body = self.method(item, 'inventoryTick')['instructions']
            by = {i['offset']: i for i in body}
            self.assertEqual(by[13]['branch_target'], 34)
            self.assertIn(helper+'.execute(', by[31]['operand'])
            self.assertIn('TarantulaTetherItemInInventoryTickProcedure.execute(', by[35]['operand'])
            holding = self.method(helper, 'execute')['instructions']
            self.assertFalse(any('.isOnCooldown(' in str(i['operand']) for i in holding))
            self.assertEqual(self.method(item,'getUseDuration',True)['instructions'][0]['operand'],30)

    def test_delayed_checks_are_sampled_in_the_lambda(self):
        for helper, delay_offset in [('AscendantStaffEntitySwingsItemProcedure',50),
                                     ('VisionarySpearEntitySwingsItemProcedure',13)]:
            body = self.method(helper,'execute')['instructions']
            self.assertIn('.queueServerWork(', next(i['operand'] for i in body if i['offset']==delay_offset))
            self.assertFalse(any('.isOnCooldown(' in str(i['operand']) for i in body))
            delayed = self.method(helper,'lambda$execute$0')['instructions']
            self.assertTrue(any('.isOnCooldown(' in str(i['operand']) for i in delayed))

    def test_zero_hook_knockback_is_not_a_positive_scalar(self):
        for r in self.batch['effects']:
            if 'hook_delivery' in r['id']:
                self.assertFalse(any(c['primitive']=='PROJECTILE_KNOCKBACK'
                                     for c in r['scalable_parameter_candidates']))
        silk = next(r for r in self.batch['effects'] if r['id']=='arphex:silk_slinger_native_hook_delivery')
        self.assertFalse(any(c['primitive']=='PROJECTILE_BASE_DAMAGE' for c in silk['scalable_parameter_candidates']))

    def test_queue_regenerates_without_closing_captured_roots(self):
        filename = OUT/'arphex-projectile-producer-review-queue.json'
        before = sha256(filename)
        update('arphex')
        self.assertEqual(sha256(filename), before)
        queue = read_json(filename)
        self.assertFalse(queue['whole_mod_complete'])
        pending = next(r for r in queue['owners'] if r['entry'].endswith('/BlackWidowBowOnPlayerStoppedUsingProcedure.class'))
        self.assertEqual(pending['disposition'], 'PENDING_OWNING_SOURCE_SEMANTICS')


if __name__ == '__main__':
    unittest.main()
