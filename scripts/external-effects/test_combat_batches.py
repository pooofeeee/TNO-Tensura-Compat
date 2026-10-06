"""Independent native assertions and mutation tests for generic batch promotion."""
import copy
import unittest
from catalog_common import OUT,read_json
from promote_combat_batch import validate_batch


class BatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch=read_json(OUT/'arphex-r2m2a-active-status-cores.json')
        cls.review=read_json(OUT/'mod-reviews/arphex.json')
        # The same validation supports a published batch without re-appending it.
        ids={r['id'] for r in cls.batch['effects']}
        cls.review['effects']=[r for r in cls.review['effects'] if r['id'] not in ids]
        cls.review['paths']=[p for p in cls.review['paths'] if not set(p['effect_ids'])&ids]
        cls.census=read_json(OUT/'arphex-combat-census.json')
        cls.evidence=read_json(OUT/'native-evidence/arphex-status-core.json')

    def test_reviewed_batch_references_real_native_consumers(self):
        self.assertEqual(validate_batch(self.batch,self.review,self.census)['semantic_records'],20)

    def test_reject_duplicate_native_parameter_identity(self):
        batch=copy.deepcopy(self.batch)
        candidate=next(r for r in batch['effects'] if r['scalable_parameter_candidates'])['scalable_parameter_candidates'][0]
        row=next(r for r in batch['effects'] if candidate in r['scalable_parameter_candidates'])
        row['scalable_parameter_candidates'].append(copy.deepcopy(candidate))
        with self.assertRaises(AssertionError):validate_batch(batch,self.review,self.census)

    def test_reject_invented_or_reader_only_scalar_boundary(self):
        for bad in ('wrong_offset','reader'):
            batch=copy.deepcopy(self.batch);row=next(r for r in batch['effects'] if r['scalable_parameter_candidates']);c=row['scalable_parameter_candidates'][0];consumer=c['native_consumer']
            if bad=='wrong_offset':consumer['offset']=-1
            else:
                witness=next(w for w in self.evidence['witnesses'] if w['entry']==consumer['entry'])
                method=next(m for m in witness['methods'] if m['name']==consumer['methods'][0] and m['descriptor']==consumer['descriptor'])
                reader=next(i for i in method['instructions'] if '.isClientSide' in str(i['operand']) or '.get' in str(i['operand']))
                consumer.update(offset=reader['offset'],operand=reader['operand'],opcode=reader['opcode'])
            with self.subTest(bad=bad),self.assertRaises((AssertionError,StopIteration)):
                validate_batch(batch,self.review,self.census)

    def test_native_attribute_command_requires_numeric_value_after_id(self):
        # Exact Vanilla registration, not a transcription of the mod's intent.
        native=read_json(OUT/'vanilla-evidence/arphex-attribute-command.json')['classes'][0]['methods'][0]['instructions']
        words=[i['operand'] for i in native if i['opcode'] in ('0x12','0x13')]
        at=words.index('modifier');self.assertEqual(words[at:at+7],['modifier','add','id','value','add_value','add_multiplied_base','add_multiplied_total'])
        self.assertTrue(any(i['offset']==177 and 'DoubleArgumentType.doubleArg' in str(i['operand']) for i in native))
        zoom=next(w for w in self.evidence['witnesses'] if w['entry'].endswith('/ZoomEffectStartedappliedProcedure.class'))
        command=next(i['operand'] for m in zoom['methods'] for i in m['instructions'] if str(i['operand']).startswith('attribute @s '))
        tokens=command.split();self.assertEqual(tokens[6],'zoom')
        with self.assertRaises(ValueError):float(tokens[6])

    def test_spiral_unguarded_integer_division_is_not_rewritten_as_float(self):
        w=next(w for w in self.evidence['witnesses'] if w['entry'].endswith('/TormentSpiralOnEffectActiveTickProcedure.class'))
        body=next(m['instructions'] for m in w['methods'] if m['name']=='execute')
        first=next(n for n,i in enumerate(body) if i['operand']==70)
        before_hurt=next(n for n,i in enumerate(body[first:],first) if '.hurt(' in str(i['operand']))
        self.assertEqual(sum(i['opcode']=='0x6c' for i in body[first:before_hurt]),2)
        record=next(r for r in self.batch['effects'] if r['id']=='arphex:torment_spiral')
        self.assertTrue(record['binary_parameters']['unguarded_zero_denominator_exception_preserved'])

    def test_statuses_after_constriction_hurt_are_not_success_gated(self):
        w=next(w for w in self.evidence['witnesses'] if w['entry'].endswith('/ConstrictedOnEffectActiveTickProcedure.class'))
        body=next(m['instructions'] for m in w['methods'] if m['name']=='execute')
        at=next(n for n,i in enumerate(body) if '.hurt(' in str(i['operand']))
        self.assertEqual(body[at-1]['operand'],3.0)
        self.assertEqual(body[at+1]['opcode'],'0x57')
        self.assertTrue(any('MobEffects.HUNGER' in str(i['operand']) for i in body[at+1:]))


if __name__=='__main__':unittest.main()
