import copy
import tempfile
import unittest
import zipfile
from pathlib import Path

from catalog_common import OUT, read_json, sha256
from validate_arrow_factory_kernels import validate
from promote_combat_batch import validate_batch
from update_arrow_producer_queue import update
from selected_reference import collect as collect_reference


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
        for owner in queue['owners']:
            if owner['disposition'].startswith('PENDING_'):
                self.assertEqual(owner['closure_proofs'], [])
            else:
                self.assertTrue(owner['closure_proofs'])
                self.assertTrue(all(p['kind'] in ('EXPLICIT_REVIEWED_SOURCE_HELPER',
                    'REUSED_LOCKED_EVENT_CONTRIBUTIONS') for p in owner['closure_proofs']))


class ReleaseWeaponProducerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch=read_json(OUT/'arphex-r2m4b-release-and-held-source-contracts.json')
        cls.census=read_json(OUT/'arphex-combat-census.json')
        cls.release=read_json(OUT/'native-evidence/arphex-weapon-projectile-producers.json')
        cls.setup=read_json(OUT/'native-evidence/arphex-release-weapon-setup.json')

    def method(self,name,setup=False):
        packet=self.setup if setup else self.release
        witness=next(w for w in packet['witnesses'] if w['entry'].endswith('/'+name+'.class'))
        return next(m for m in witness['methods'] if m['name']=='execute')

    def prior_review(self):
        review=copy.deepcopy(read_json(OUT/'mod-reviews/arphex.json'))
        ids={r['id'] for r in self.batch['effects']}
        review['effects']=[r for r in review['effects'] if r['id'] not in ids]
        review['paths']=[p for p in review['paths'] if not set(p['effect_ids']) & ids]
        return review

    def test_seven_contracts_and_one_existing_recoil_refinement(self):
        result=validate_batch(self.batch,self.prior_review(),self.census)
        self.assertEqual(result['semantic_records'],len(self.prior_review()['effects'])+7)
        self.assertEqual(sum(len(c['parameters']) for r in self.batch['effects']
            for c in r['scalable_parameter_candidates'])+sum(len(c['parameters'])
            for r in self.batch['record_refinements'] for c in r['candidate_additions']),50)

    def test_only_full_draw_widow_factory_ignites(self):
        registry=read_json(OUT/'arphex-projectile-producer-kernel-registry.json')
        rows=[r for r in registry['rows'] if 'BlackWidowBowOnPlayerStoppedUsingProcedure$' in r['factory']['entry']]
        self.assertEqual([r['self_fire_offsets'] for r in rows],[[47],[],[],[],[]])
        body=self.method('BlackWidowBowOnPlayerStoppedUsingProcedure')['instructions']
        self.assertEqual([i['operand'] for n,i in enumerate(body) if i['offset'] in (158,386,612,839,1037)],
                         [4.0,2.0,1.0,1.0,.5])

    def test_burst_common_argument_has_eight_independent_native_sites(self):
        row=next(r for r in self.batch['effects'] if r['id']=='arphex:visionary_spear_native_release_burst')
        for primitive in ('PROJECTILE_BASE_DAMAGE','PROJECTILE_KNOCKBACK'):
            cs=[c for c in row['scalable_parameter_candidates'] if c['primitive']==primitive]
            self.assertEqual(len(cs),1)
            self.assertEqual(len(cs[0]['additional_arrow_factory_sites']),7)
        changed=copy.deepcopy(self.batch)
        c=next(c for r in changed['effects'] for c in r['scalable_parameter_candidates']
               if c.get('additional_arrow_factory_sites'))
        c['additional_arrow_factory_sites'][-1]['binding']['literal_arguments']['base_damage']['value']=999
        with self.assertRaises(AssertionError):
            validate_batch(changed,self.prior_review(),self.census)

    def test_burst_cooldown_precedes_shift_and_any_factory(self):
        body=self.method('VisionarySpearOnPlayerStoppedUsingProcedure')['instructions']
        self.assertLess(88,next(i['offset'] for i in body if '.isShiftKeyDown(' in str(i['operand'])))
        self.assertLess(88,min(i['offset'] for i in body if '.getArrow(' in str(i['operand'])))
        self.assertEqual(sum('.getArrow(' in str(i['operand']) for i in body),8)

    def test_wrath_integer_quantization_and_actual_config_default(self):
        by={i['offset']:i for i in self.method('TormentAnnihilatorHandTickProcedure',True)['instructions']}
        self.assertEqual(by[218]['operand'],20)
        self.assertEqual([by[n]['opcode'] for n in (220,221)],['0x6c','0x87'])
        self.assertIn('Math.floor',by[222]['operand'])
        witness=next(w for w in read_json(OUT/'native-evidence/arphex-global-hooks.json')['witnesses']
                     if w['entry'].endswith('/ConfigurationSettingsConfiguration.class'))
        body=next(m['instructions'] for m in witness['methods'] if m['name']=='<clinit>')
        by={i['offset']:i for i in body}
        self.assertEqual(by[622]['operand'],100.0)
        self.assertIn('Builder.define(',by[628]['operand'])
        self.assertIn('LIMIT_TORMENTED_WRATH',by[631]['operand'])
        self.assertIn('default is 200',by[613]['operand'])

    def test_held_aim_has_no_five_target_counter_and_keeps_previous_yaw(self):
        body=self.method('ChronoCannonHeldProcedure',True)['instructions'];by={i['offset']:i for i in body}
        stores=[i for i in body if i['opcode']=='0x39' and i.get('local_index')==36]
        self.assertEqual(len(stores),2) # initialization and literal5; no per-recipient decrement
        self.assertEqual(by[1172]['branch_target'],1179)
        self.assertEqual(by[1177]['local_index'],9) # winner update conditional
        self.assertEqual(by[1181]['local_index'],42) # previous yaw update unconditional
        self.assertEqual(by[1199]['branch_target'],1425)
        self.assertEqual(by[1416]['operand'],4.0)

    def test_genesis_stop_does_not_recheck_duration_before_resistance(self):
        body=self.method('GenesisRifleItemInHandTickProcedure',True)['instructions']
        self.assertIn('.stopUsingItem(',next(i['operand'] for i in body if i['offset']==231))
        self.assertFalse(any('getTicksUsingItem' in str(i['operand']) for i in body if 231<i['offset']<272))
        self.assertEqual(next(i['operand'] for i in body if i['offset']==269),10)
        self.assertEqual(next(i['operand'] for i in body if i['offset']==271),1)

    def test_raw_recoil_key_binding_mutation_is_rejected(self):
        changed=copy.deepcopy(self.batch)
        c=changed['record_refinements'][0]['candidate_additions'][0]
        self.assertEqual(c['native_tag_double_binding']['key'],'recoil_genesis')
        c['native_tag_double_binding']['key']='unrelated_state'
        with self.assertRaises(AssertionError):
            validate_batch(changed,self.prior_review(),self.census)


class ContinuousWeaponProducerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch=read_json(OUT/'arphex-r2m4c-continuous-and-delayed-weapon-sources.json')
        cls.census=read_json(OUT/'arphex-combat-census.json')
        cls.native=read_json(OUT/'native-evidence/arphex-weapon-projectile-producers.json')
        cls.setup=read_json(OUT/'native-evidence/arphex-continuous-weapon-setup.json')

    def method(self,name,method='execute',setup=False):
        packet=self.setup if setup else self.native
        witness=next(w for w in packet['witnesses'] if w['entry'].endswith('/'+name+'.class'))
        return next(m for m in witness['methods'] if m['name']==method)

    def prior_review(self):
        review=copy.deepcopy(read_json(OUT/'mod-reviews/arphex.json'))
        ids={r['id'] for r in self.batch['effects']}
        review['effects']=[r for r in review['effects'] if r['id'] not in ids]
        review['paths']=[p for p in review['paths'] if not set(p['effect_ids']) & ids]
        return review

    def test_nine_source_contracts_and_seven_explicit_producer_closures(self):
        result=validate_batch(self.batch,self.prior_review(),self.census)
        self.assertEqual(result['semantic_records'],len(self.prior_review()['effects'])+9)
        self.assertEqual(len(self.batch['producer_closed_entries']),7)
        self.assertFalse(self.batch['whole_mod_complete'])

    def test_cross_lambda_factory_sites_cannot_be_substituted(self):
        changed=copy.deepcopy(self.batch)
        c=next(c for r in changed['effects'] for c in r['scalable_parameter_candidates']
               if any('method' in s and s['method']!='execute'
                      for s in c.get('additional_arrow_factory_sites',[])))
        c['additional_arrow_factory_sites'][0]['method']='execute'
        with self.assertRaises((AssertionError,StopIteration)):
            validate_batch(changed,self.prior_review(),self.census)

    def test_echo_native_swing_precedes_explicit_factory(self):
        body=self.method('AbyssAscendantEntitySwingsItemProcedure','lambda$execute$0')['instructions']
        self.assertIn('LivingEntity.swing(',next(i['operand'] for i in body if i['offset']==17))
        self.assertLess(17,next(i['offset'] for i in body if '.getArrow(' in str(i['operand'])))
        self.assertFalse(any('.isOnCooldown(' in str(i['operand']) for i in body))
        reference=read_json(OUT/'reference-evidence/arphex-native-swing-dispatch-244.json')
        patch=next(w for w in reference['witnesses'] if w['entry'].endswith('/LivingEntity.java.patch'))
        text=''.join(s['text'] for s in patch['text_sections'])
        self.assertIn('this.getItemInHand',text)
        self.assertLess(text.index('stack.onEntitySwing'),text.index('!this.swinging'))
        stack=next(w for w in reference['witnesses'] if w['entry'].endswith('/IItemStackExtension.class'))
        body=next(m['instructions'] for m in stack['methods'] if 'InteractionHand;' in m['descriptor'])
        self.assertTrue(any('getItem()' in str(i['operand']) for i in body))
        self.assertTrue(any('Item.onEntitySwing(' in str(i['operand']) for i in body))
        row=next(r for r in self.batch['effects'] if r['id']=='arphex:abyss_ascendant_native_delayed_swing')
        self.assertTrue(row['binary_parameters']['no_fixed_total_arrow_count'])

    def test_flame_boolean_equality_integer_division_and_independent_status(self):
        for name,eq,n1,n2,cast,hurt,burn,status in [
            ('FireblasterRightClickProcedure',1157,1242,1243,1244,1245,1165,1317),
            ('HypnoticRightClickProcedure',1156,1241,1242,1243,1244,1164,1318)]:
            body=self.method(name)['instructions'];by={i['offset']:i for i in body}
            self.assertEqual(by[eq]['opcode'],'0xa0')  # compare two computed booleans
            self.assertEqual([by[n]['opcode'] for n in (n1,n2,cast)],['0x6c','0x6c','0x86'])
            self.assertLess(burn,hurt)
            self.assertLess(hurt,status)
            after=body[body.index(by[hurt])+1]
            self.assertEqual(after['opcode'],'0x57')  # hurt boolean discarded

    def test_selected_source_precedes_shared_hand_cleanup(self):
        for item,source in [('FormicFireblasterItem','FireblasterRightClickProcedure'),
                            ('HypnoticHellblasterItem','HypnoticRightClickProcedure'),
                            ('JudgementBlasterItem','JudgementHandProcedure')]:
            body=self.method(item,'inventoryTick')['instructions']
            own=next(i['offset'] for i in body if source+'.execute(' in str(i['operand']))
            cleanup=next(i['offset'] for i in body if 'FormicFireblasterItemInInventoryTickProcedure.execute(' in str(i['operand']))
            self.assertLess(own,cleanup)
        for name,value in [('lambda$execute$0',1),('lambda$execute$1',0)]:
            body=self.method('FormicFireblasterItemInInventoryTickProcedure',name,True)['instructions']
            self.assertEqual(body[1]['operand'],'mainhand')
            self.assertEqual(body[2]['operand'],value)
        body=self.method('FormicFireblasterItemInInventoryTickProcedure',setup=True)['instructions']
        self.assertFalse(any('JUDGEMENT_BLASTER' in str(i['operand']) for i in body))

    def test_voidseeker_tracking_is_outside_cd_break_and_has_ten_live_checks(self):
        body=self.method('VoidseekerHandTickProcedure')['instructions'];by={i['offset']:i for i in body}
        self.assertEqual(by[1218]['branch_target'],1390)
        self.assertIn('.isAlive()',by[1392]['operand'])
        self.assertLess(1390,1457)
        for j in range(2,12):
            body=self.method('VoidseekerHandTickProcedure','lambda$execute$'+str(j))['instructions']
            self.assertEqual(sum('.isAlive()' in str(i['operand']) for i in body),1)
            self.assertEqual(sum('.putDouble(' in str(i['operand']) for i in body),3)
            self.assertEqual(sum('.queueServerWork(' in str(i['operand']) for i in body),0 if j==2 else 1)
            self.assertFalse(any('.isOnCooldown(' in str(i['operand']) for i in body))

    def test_anonymous_native_explosion_is_not_zero_damage(self):
        body=self.method('AnnihilatorHandTickProcedure')['instructions'];by={i['offset']:i for i in body}
        self.assertEqual(by[107]['opcode'],'0x1')  # null source entity
        self.assertEqual(by[112]['operand'],1.)
        self.assertIn('ExplosionInteraction.NONE',by[113]['operand'])
        self.assertIn('.explode(',by[116]['operand'])
        self.assertLess(349,537)  # second cooldown admission precedes stopUsing


class SelectedReferenceScopeTests(unittest.TestCase):
    def test_resource_ranges_preserve_full_entry_hash_but_emit_only_scoped_text(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'source.jar'
            with zipfile.ZipFile(path,'w') as jar:
                jar.writestr('scope.patch','unrelated\nneeded\nother\nlast\n')
            spec=dict(id='scope',scope='test bounded patch',archives=[dict(path=str(path),
                sha256=sha256(path),resources=[dict(entry='scope.patch',line_ranges=[[2,2],[4,4]])])])
            result=collect_reference(spec)['witnesses'][0]
            self.assertNotIn('text',result)
            self.assertEqual([s['text'] for s in result['text_sections']],['needed\n','last\n'])
            self.assertEqual(result['entry_sha256'],__import__('hashlib').sha256(
                b'unrelated\nneeded\nother\nlast\n').hexdigest())
            self.assertEqual(collect_reference(spec)['witnesses'][0],result)
            for ranges in ([],[[0,1]],[[3,2]],[[2,5]],[[2,3],[3,4]]):
                spec['archives'][0]['resources'][0]['line_ranges']=ranges
                with self.assertRaises(AssertionError):
                    collect_reference(spec)


if __name__ == '__main__':
    unittest.main()
