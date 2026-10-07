"""Routing preserves independent reconciliation; raw hashes cannot prove closure."""
import copy
import unittest
from unittest.mock import patch
from catalog_common import OUT,read_json
from queue_native_census import build
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


if __name__=='__main__':unittest.main()
