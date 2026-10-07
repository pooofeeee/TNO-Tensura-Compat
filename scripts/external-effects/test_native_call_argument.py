"""Literal argument position proof, independent of authored semantic labels."""
import copy
import unittest
from catalog_common import OUT, read_json
from promote_combat_batch import literal_call_argument_binding


def method():
    packet = read_json(OUT/'native-evidence/alexscaves-dinosaur-actors.json')
    w = next(w for w in packet['witnesses'] if w['entry'].endswith('/AtlatitanEntity.class'))
    return copy.deepcopy(next(m for m in w['methods'] if m['name'] == 'tick'))


class NativeCallArgumentTests(unittest.TestCase):
    def test_real_native_radius_and_force_arguments(self):
        m = method()
        self.assertEqual(literal_call_argument_binding(m, 702, 1)['native_value'], 5.0)
        self.assertEqual(literal_call_argument_binding(m, 702, 3)['native_value'], 1.0)
        with self.assertRaises(AssertionError):
            literal_call_argument_binding(m, 702, 2)  # computed ATTACK_DAMAGE * .8

    def test_boolean_gate_cannot_become_numeric(self):
        with self.assertRaises(AssertionError):
            literal_call_argument_binding(method(), 702, 4)

    def test_join_between_literal_and_consumer_loses_proof(self):
        m = method()
        proof = literal_call_argument_binding(m, 702, 1)
        # A native branch to the consumer may bypass the original radius push.
        branch = next(i for i in m['instructions'] if 'branch_target' in i)
        branch['branch_target'] = 702
        with self.assertRaises(AssertionError):
            literal_call_argument_binding(m, 702, 1)
        self.assertLess(proof['value_offset'], 702)

    def test_changed_literal_produces_changed_binding(self):
        m = method()
        p = literal_call_argument_binding(m, 702, 1)
        next(i for i in m['instructions'] if i['offset'] == p['value_offset'])['operand'] = 6.0
        self.assertEqual(literal_call_argument_binding(m, 702, 1)['native_value'], 6.0)

    def test_exception_join_is_not_guessed(self):
        m = method(); m['exception_handlers'] = [{'handler_pc': 702}]
        with self.assertRaises(AssertionError):
            literal_call_argument_binding(m, 702, 1)


if __name__ == '__main__':
    unittest.main()
