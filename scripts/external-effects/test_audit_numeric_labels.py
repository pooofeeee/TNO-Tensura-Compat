import copy
import unittest
from audit_numeric_labels import audit


def fixture():
    return dict(effects=[dict(id='x',components=[dict(primitive='P',numerical_parameters={'seconds':2}),
        dict(primitive='S',numerical_parameters={'ticks':40},numeric_label_bindings={'ticks':dict(
            original_primitive='S',original_summary_value=40,binding='DERIVED_SUMMARY_FROM_NATIVE_LITERAL',
            target_primitive='P',target_parameter='seconds',multiplier=20)})],
        scalable_parameter_candidates=[dict(primitive='P',parameters=['seconds'],native_parameter_identity=dict(
            entry='X.class',method='m',descriptor='()V',offset=1))])])


class NumericLabelTests(unittest.TestCase):
    def test_conversion_and_unique_native_identity(self):
        self.assertEqual(audit(fixture())['summary_label_dispositions'],1)
    def test_unbound_and_dangling_labels_are_rejected(self):
        for key,value in [('target_parameter','missing'),('multiplier',10)]:
            r=fixture();r['effects'][0]['components'][1]['numeric_label_bindings']['ticks'][key]=value
            with self.assertRaises(AssertionError):audit(r)
        r=fixture();r['effects'][0]['components'][1].pop('numeric_label_bindings')
        with self.assertRaises(AssertionError):audit(r)
    def test_duplicate_native_identity_across_records_is_rejected(self):
        r=fixture();other=copy.deepcopy(r['effects'][0]);other['id']='y';r['effects'].append(other)
        with self.assertRaises(AssertionError):audit(r)
    def test_shadowed_summary_cannot_hide_missing_identity(self):
        r=fixture();r['effects'][0]['components'].append(copy.deepcopy(r['effects'][0]['components'][1]))
        with self.assertRaises(AssertionError):audit(r)
