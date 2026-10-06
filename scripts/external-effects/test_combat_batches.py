"""Independent native assertions and mutation tests for generic batch promotion."""
import copy
import unittest
from catalog_common import OUT,read_json
from promote_combat_batch import validate_batch


class RefinementStateTests(unittest.TestCase):
    def fixture(self):
        review = dict(effects=[dict(id='test:portal', actual_behavior='Protected setup. Consumer pending.',
                      binary_parameters=dict(consumer_pending=True), components=[],
                      scalable_parameter_candidates=[], implementation=[], native_boundary=[], delivery_paths=[])])
        batch = dict(checkpoint='consumer-closed', record_refinements=[dict(id='test:portal', reason='Exact consumer closed.',
                     behavior_append='Exact consumer contract referenced.',
                     behavior_replacements=[dict(before='Consumer pending.', after='Consumer closed.')],
                     binary_parameter_updates=dict(consumer_pending=False))])
        return review, batch

    def test_exact_scope_replacement_and_gate_are_idempotent(self):
        from promote_combat_batch import refined_review
        review, batch = self.fixture()
        result = refined_review(review, batch)
        row = result['effects'][0]
        self.assertEqual(row['actual_behavior'], 'Protected setup. Consumer closed. Exact consumer contract referenced.')
        self.assertFalse(row['binary_parameters']['consumer_pending'])
        self.assertEqual(refined_review(result, batch), result)
        self.assertTrue(review['effects'][0]['binary_parameters']['consumer_pending'])

    def test_missing_ambiguous_or_unknown_scope_changes_fail(self):
        from promote_combat_batch import refined_review
        for text in ('Protected setup.', 'Consumer pending. Consumer pending.'):
            review, batch = self.fixture(); review['effects'][0]['actual_behavior'] = text
            with self.assertRaisesRegex(AssertionError, 'behavior replacement'):
                refined_review(review, batch)
        review, batch = self.fixture()
        batch['record_refinements'][0]['binary_parameter_updates']['unknown_gate'] = False
        with self.assertRaisesRegex(AssertionError, 'unknown native gate'):
            refined_review(review, batch)

    def test_stale_published_gate_and_scope_fail(self):
        from promote_combat_batch import refined_review
        review, batch = self.fixture(); result = refined_review(review, batch)
        result['effects'][0]['binary_parameters']['consumer_pending'] = True
        with self.assertRaisesRegex(AssertionError, 'published gate'):
            refined_review(result, batch)
        result = refined_review(review, batch)
        result['effects'][0]['actual_behavior'] += ' Consumer pending.'
        with self.assertRaisesRegex(AssertionError, 'stale published behavior'):
            refined_review(result, batch)


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
        self.assertEqual(validate_batch(self.batch,self.review,self.census)['semantic_records'],
                         len(self.review['effects'])+len(self.batch['effects']))

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

    def test_void_motion_keeps_actual_asymmetric_native_limits(self):
        w=next(w for w in self.evidence['witnesses'] if w['entry'].endswith('/VoidRepulsionOnEffectActiveTickProcedure.class'))
        body=next(m['instructions'] for m in w['methods'] if m['name']=='execute')
        negative=next(n for n,i in enumerate(body) if i['operand']==-0.8)
        self.assertTrue(any(i['operand']=='xvelos' for i in body[max(0,negative-7):negative]))
        self.assertTrue(any(i['operand']==-0.9 for i in body[negative+1:negative+12]))
        positive=next(n for n,i in enumerate(body) if i['operand']==0.8)
        self.assertTrue(any(i['operand']=='zvelos' for i in body[max(0,positive-8):positive]))
        record=next(r for r in self.batch['effects'] if r['id']=='arphex:void_repulsion')
        self.assertTrue(record['binary_parameters']['zero_axes_enter_else'])
        motion=next(c for c in record['components'] if c['primitive']=='FORCED_MOVEMENT')
        self.assertIn('abs(dx)',motion['parameter_formulas']['velocity_x']['else_including_zero_axes'])

    def test_primary_target_batch_has_native_consumers(self):
        batch=read_json(OUT/'arphex-r2m2b-primary-target.json')
        review=read_json(OUT/'mod-reviews/arphex.json');ids={r['id'] for r in batch['effects']}
        review['effects']=[r for r in review['effects'] if r['id'] not in ids]
        review['paths']=[p for p in review['paths'] if not set(p['effect_ids'])&ids]
        self.assertEqual(validate_batch(batch,review,self.census)['semantic_records'],
                         len(review['effects'])+len(batch['effects']))

    def test_enemy_summon_else_is_unreachable_after_guaranteed_roll(self):
        w=next(w for w in self.evidence['witnesses'] if w['entry'].endswith('/TormentorPrimaryTargetOnEffectActiveTickProcedure.class'))
        body=next(m['instructions'] for m in w['methods'] if m['name']=='execute')
        at=next(n for n,i in enumerate(body) if i['offset']==2172)
        self.assertEqual([i['operand'] for i in body[at-2:at]],[1,1])
        self.assertIn('Mth.nextInt(',body[at]['operand'])
        self.assertEqual(body[at+1]['operand'],1)
        self.assertEqual(body[at+2]['opcode'],'0xa0') # if_icmpne: impossible for inclusive 1..1
        self.assertEqual(body[at+2]['branch_target'],2681)

    def test_enhanced_senses_commands_are_display_only(self):
        entry='net/arphex/procedures/EnhancedSensesOnEffectActiveTickProcedure.class'
        w=next(w for w in self.evidence['witnesses'] if w['entry']==entry)
        calls=[str(i['operand']) for m in w['methods'] for i in m['instructions']]
        for mutator in ('.hurt(','.addEffect(','.setTarget(','.setDeltaMovement(','.putDouble('):
            self.assertFalse(any(mutator in call for call in calls))
        recipes=[b['arguments'][0] for b in self.census['registration_bootstraps']
                 if b['entry']==entry and 'StringConcatFactory.' in b['handle']]
        self.assertTrue(recipes)
        self.assertTrue(all(r.startswith('particle arphex:') for r in recipes))

    def test_distinct_parameters_bind_distinct_argument_writes(self):
        rows={r['id']:r for r in self.batch['effects']}
        for rid,parameters,expected in (
            ('arphex:moth_curse',('yaw_delta','pitch_delta'),('Entity.setYRot(','Entity.setXRot(')),
            ('arphex:breathless',('moving_gain','rest_drain'),(1.0,3.0))):
            consumers=[]
            for parameter,want in zip(parameters,expected):
                candidate=next(c for c in rows[rid]['scalable_parameter_candidates'] if parameter in c['parameters'])
                self.assertEqual(candidate['parameters'],[parameter])
                consumer=candidate['native_consumer'];consumers.append(consumer['offset'])
                witness=next(w for w in self.evidence['witnesses'] if w['entry']==consumer['entry'])
                body=next(m['instructions'] for m in witness['methods'] if m['name']==consumer['methods'][0] and m['descriptor']==consumer['descriptor'])
                at=next(n for n,i in enumerate(body) if i['offset']==consumer['offset'])
                if isinstance(want,str):self.assertIn(want,body[at]['operand'])
                else:
                    self.assertEqual(body[at-2]['operand'],want)
                    self.assertEqual(body[at-1]['opcode'],'0x63' if parameter=='moving_gain' else '0x67')
            self.assertEqual(len(set(consumers)),2)

    def test_timer_profiles_do_not_claim_countdown_or_anchor_writes(self):
        row=next(r for r in self.batch['effects'] if r['id']=='arphex:time_freeze')
        c=next(c for c in row['scalable_parameter_candidates'] if c['primitive']=='CONTROL_CADENCE')
        self.assertEqual(c['native_consumer']['offset'],695)
        self.assertEqual([s['offset'] for s in c['additional_consumer_sites']],[713])
        w=next(w for w in self.evidence['witnesses'] if w['entry']==c['native_consumer']['entry'])
        body=next(m['instructions'] for m in w['methods'] if m['name']=='execute')
        for offset,value in ((695,30.0),(713,20.0)):
            at=next(n for n,i in enumerate(body) if i['offset']==offset)
            self.assertEqual(body[at-3]['operand'],value)
            self.assertEqual(body[at-1]['opcode'],'0x67') # reset value minus A

    def test_reject_incorrect_effect_holder_and_duplicate_auxiliary_site(self):
        for defect in ('holder','duplicate_site'):
            batch=copy.deepcopy(self.batch)
            c=next(c for r in batch['effects'] for c in r['scalable_parameter_candidates'] if c['primitive'].startswith('MOB_EFFECT_'))
            if defect=='holder':c['native_holder_symbol']='invented holder'
            else:c.setdefault('additional_consumer_sites',[]).append(copy.deepcopy(c['native_parameter_identity']))
            with self.subTest(defect=defect),self.assertRaises(AssertionError):
                validate_batch(batch,self.review,self.census)


if __name__=='__main__':unittest.main()
