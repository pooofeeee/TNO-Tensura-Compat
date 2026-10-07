"""Literal argument provenance independent of authored mechanic meaning."""
import copy
import unittest
from promote_combat_batch import literal_constructor_argument_binding
from catalog_common import OUT,read_json


def ins(offset,opcode,operand=None):
    return dict(offset=offset,opcode=opcode,operand=operand)


class ConstructorArgumentTests(unittest.TestCase):
    def fixture(self):
        return dict(instructions=[ins(0,'0xbb','x/Payload'),ins(3,'0x59'),ins(4,'0x2a'),
            ins(5,'0xb6','x/Actor.level()Lx/World;'),ins(8,'0x12',5.0),ins(10,'0x2a'),
            ins(11,'0xb6','x/Actor.isWet()Z'),ins(14,'0xb2','x/Mode.KEEPLx/Mode;'),
            ins(17,'0xb7','x/Payload.<init>(Lx/World;FZLx/Mode;)V')])

    def test_unknown_other_arguments_do_not_become_claimed_values(self):
        result=literal_constructor_argument_binding(self.fixture(),17,1)
        self.assertEqual((result['argument_descriptor'],result['native_value'],result['value_offset']),('F',5.0,8))
        self.assertEqual(result['allocation_offset'],0)
        for argument in (0,2,3):
            with self.assertRaises(AssertionError):literal_constructor_argument_binding(self.fixture(),17,argument)

    def test_local_expression_branch_and_changed_type_fail_closed(self):
        for replacement in [ins(8,'0x23'),ins(8,'0xb8','x/Config.radius()F'),ins(8,'0x12',5)]:
            method=self.fixture();method['instructions'][4]=replacement
            with self.assertRaises(AssertionError):literal_constructor_argument_binding(method,17,1)
        for extra in [ins(9,'0x99'),ins(9,'0x6a'),ins(9,'0x38')]:
            method=self.fixture();method['instructions'].insert(5,extra)
            with self.assertRaises(AssertionError):literal_constructor_argument_binding(method,17,1)

    def test_literal_from_another_allocation_cannot_bind_this_constructor(self):
        method=self.fixture();method['instructions'][0]['operand']='x/Other'
        with self.assertRaises((AssertionError,ValueError)):
            literal_constructor_argument_binding(method,17,1)
        with self.assertRaises(AssertionError):literal_constructor_argument_binding(self.fixture(),17,5)

    def test_wide_literal_is_typed_long_and_single_argument(self):
        method=dict(instructions=[ins(0,'0xbb','x/Payload'),ins(3,'0x59'),ins(4,'0x14',7),
                                 ins(7,'0xb7','x/Payload.<init>(J)V')])
        self.assertEqual(literal_constructor_argument_binding(method,7,0)['argument_descriptor'],'J')

    def test_original_pinned_mine_radius_is_a_constructor_input_not_an_effect_name(self):
        packet=read_json(OUT/'native-evidence/alexscaves-ferrous-actors.json')
        witness=next(w for w in packet['witnesses'] if w['entry'].endswith('/MineGuardianEntity.class'))
        method=next(m for m in witness['methods'] if m['name']=='tick')
        binding=literal_constructor_argument_binding(method,232,5)
        self.assertEqual(binding['native_value'],5.0)
        self.assertEqual(binding['argument_descriptor'],'F')
        self.assertEqual(binding['allocation_offset'],200)


if __name__=='__main__':unittest.main()
