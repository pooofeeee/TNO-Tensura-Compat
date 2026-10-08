"""Exact literal identities do not prove a parameter's semantic role."""
import unittest
from promote_combat_batch import literal_numeric_site_binding, refined_review


class LiteralSiteTests(unittest.TestCase):
    def test_selected_signed_literal_is_pinned_without_interpreting_branch(self):
        method = dict(instructions=[dict(offset=0, opcode='0x14', operand=-.1),
                                    dict(offset=3, opcode='0x6b', operand=None)])
        self.assertEqual(literal_numeric_site_binding(method, 0),
            dict(native_value=-.1, value_offset=0, kind='EXPLICITLY_REVIEWED_LITERAL_SITE'))

    def test_computed_values_fields_strings_and_boolean_metadata_fail_closed(self):
        for opcode, value in [('0x60', 3), ('0xb2', 3), ('0x12', '3'), ('0x4', True)]:
            with self.subTest(opcode=opcode), self.assertRaises(AssertionError):
                literal_numeric_site_binding(dict(instructions=[
                    dict(offset=5, opcode=opcode, operand=value)]), 5)

    def test_wrong_offset_cannot_bind_a_nearby_literal(self):
        with self.assertRaises(StopIteration):
            literal_numeric_site_binding(dict(instructions=[
                dict(offset=2, opcode='0x10', operand=30)]), 3)

    def test_refinement_without_binary_parameters_is_repeatable(self):
        review = dict(effects=[dict(id='fixture', actual_behavior='original', components=[],
                                  scalable_parameter_candidates=[], implementation=[])])
        batch = dict(checkpoint='fixture', record_refinements=[dict(id='fixture',
            reason='explicit additive evidence', behavior_append='verified context')])
        first = refined_review(review, batch)
        self.assertEqual(first, refined_review(first, batch))


if __name__ == '__main__':
    unittest.main()
