"""Routing preserves independent reconciliation; raw hashes cannot prove closure."""
import copy
import unittest
from unittest.mock import patch
from catalog_common import OUT,read_json
from queue_native_census import build, call_frontier
from reconcile_native_census import reconcile,method_key


class NativeQueueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.review=read_json(OUT/'mod-reviews/alexscaves.json')
        cls.census=read_json(OUT/'alexscaves-combat-census.json')

    def test_exact_pending_partition_without_duplicate_or_missing_methods(self):
        q=build(self.review,self.census);index,pending=reconcile(self.review,self.census)
        ordinals=[n for g in q['groups'] for n in g['method_ordinals']]
        self.assertEqual(len(ordinals),len(set(ordinals)))
        self.assertEqual({method_key(self.census['methods'][n]) for n in ordinals},
                         {method_key(m) for m in pending})
        self.assertEqual(q['summary']['remaining_methods'],len(pending))
        self.assertEqual(len(pending)+index['summary']['exact_dispositioned_methods'],self.census['total_methods'])
        self.assertTrue(all(h['coverage_proven'] is False for h in q['raw_code_hash_comparison_hints']))

    def test_captures_and_routing_cannot_close_unreviewed_methods(self):
        before=build(self.review,self.census)
        again=build(copy.deepcopy(self.review),copy.deepcopy(self.census))
        self.assertEqual(before,again)
        self.assertEqual(self.review,read_json(OUT/'mod-reviews/alexscaves.json'))

    def test_passenger_aware_spawn_is_not_hidden_from_routing(self):
        # Exercise the parser independently of whatever queue remains today.
        with patch('queue_native_census.decode_sites', return_value=[dict(
                operand='net/minecraft/server/level/ServerLevel.addFreshEntityWithPassengers(Lnet/minecraft/world/entity/Entity;)V')]):
            q=build(self.review,self.census)
        self.assertEqual(q['summary']['direct_native_call_sites']['.addFreshEntityWithPassengers('],
                         q['summary']['remaining_methods'])


class FrontierTests(unittest.TestCase):
    def fixture(self):
        return dict(mod_key='example',jar_sha256='pin',registration_bootstraps=[],
            classes=[dict(name='x/Child',superclass='x/Base'),dict(name='x/Base',superclass='java/lang/Object')],
            symbols=['x/Child.query()I','x/Child.flagI'],methods=[
                dict(entry='x/Child.class',method='caller',descriptor='()V',calls=[[2,182,0]],hits=[[4,181,1]]),
                dict(entry='x/Base.class',method='query',descriptor='()I',calls=[],hits=[])])

    def test_inherited_declaration_preserves_exact_original_call_site(self):
        d=call_frontier(self.fixture(),[0]);self.assertEqual(d['selected_ordinals'],[0])
        self.assertEqual(d['calls'],[dict(symbol='x/Child.query()I',native_declaration_ordinal=1,
            sites=[dict(caller_ordinal=0,offset=2,opcode='0xb6')])])
        self.assertEqual(d['field_writes'][0]['sites'][0]['offset'],4)
        self.assertNotIn('disposition',d);self.assertNotIn('classification',d)

    def test_external_call_is_not_a_proven_native_target(self):
        c=self.fixture();c['symbols'][0]='external/Unknown.activate()V'
        self.assertIsNone(call_frontier(c,[0])['calls'][0]['native_declaration_ordinal'])

    def test_finite_selection_and_deterministic_grouping(self):
        c=self.fixture();self.assertEqual(call_frontier(c,[1,0,0]),call_frontier(c,[0,1]))
        with self.assertRaises(AssertionError):call_frontier(c,[2])


if __name__=='__main__':unittest.main()
