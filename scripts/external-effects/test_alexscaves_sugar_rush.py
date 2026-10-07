"""Independent native operands, ordering, negative mutations and scope guards."""
import copy
import json
import unittest
import tomllib

from catalog_common import OUT,read_json
from collect_combat_census import decode_sites
from promote_combat_batch import validate_batch,effect_holder_binding,literal_effect_arguments
from reconcile_native_census import reconcile
from assemble_alexscaves_status_foundation import method,PREFIX
from assemble_alexscaves_sugar_rush import BATCH,NEW,new_method,OBLIGATION


def by_offset(m):
    return {i['offset']:i for i in m['instructions']}


class AlexCavesSugarRushTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch=read_json(OUT/BATCH)
        cls.census=read_json(OUT/'alexscaves-combat-census.json')
        cls.before=copy.deepcopy(read_json(OUT/'mod-reviews/alexscaves.json'))
        cls.prior_batches=['alexscaves-r2m8a-status-foundation.json',
                           'alexscaves-r2m8b-darkness-rage-and-vision-context.json']
        old=[read_json(OUT/f) for f in cls.prior_batches]
        ids={r['id'] for b in old for r in b['effects']}
        paths={p['id'] for b in old for p in b['paths']}
        cls.before['effects']=[r for r in cls.before['effects'] if r['id'] in ids]
        cls.before['paths']=[p for p in cls.before['paths'] if p['id'] in paths]
        cls.before['reviewed_batches']=cls.prior_batches

    def test_native_candidates_validate_once_and_old_statuses_remain_exact(self):
        s=validate_batch(self.batch,self.before,self.census)
        self.assertEqual((s['semantic_records'],s['numeric_candidate_entries']),(6,29))
        self.assertEqual(s['classification_counts'],{'CUSTOM_CONTROL':4,'CUSTOM_STATUS':2})
        expected=[r for f in self.prior_batches for r in read_json(OUT/f)['effects']]
        self.assertEqual(sorted(self.before['effects'],key=lambda r:r['id']),sorted(expected,key=lambda r:r['id']))
        self.assertEqual(self.batch['effects'][0]['id'],'alexscaves:sugar_rush')

    def test_attribute_uses_total_operation_and_positive_duration(self):
        ctor=by_offset(method('server/potion/SugarRushEffect','<init>'))
        self.assertEqual(ctor[36]['operand'],0.25)
        self.assertTrue(ctor[39]['operand'].endswith('Operation.ADD_MULTIPLIED_TOTALLnet/minecraft/world/entity/ai/attributes/AttributeModifier$Operation;'))
        self.assertEqual([ctor[o]['operand'] for o in (21,23)],['alexscaves','sugar_rush_speed'])
        cadence=by_offset(method('server/potion/SugarRushEffect','shouldApplyEffectTickThisTick'))
        self.assertEqual(cadence[0]['local_index'],1)
        self.assertEqual((cadence[1]['opcode'],cadence[1]['branch_target']),('0x9e',8))

    def test_motion_sign_branches_preserve_xz_and_do_not_share_one_factor(self):
        body=by_offset(method('server/potion/SugarRushEffect','applyEffectTick'))
        self.assertEqual(body[7]['branch_target'],22)
        self.assertEqual(body[45]['branch_target'],72);self.assertEqual(body[76]['branch_target'],142)
        self.assertEqual([body[o]['operand'] for o in (50,51,54,81,82,85)],[1.0,0.85,1.0,1.0,0.45,1.0])
        self.assertIn('Vec3.multiply',body[55]['operand']);self.assertIn('Vec3.multiply',body[86]['operand'])
        self.assertNotIn('hurt',str([i['operand'] for i in body.values()]))

    def test_slow_fall_is_absent_only_descending_and_recipient_remains_supplied_entity(self):
        m=method('server/potion/SugarRushEffect','applyEffectTick');body=by_offset(m)
        self.assertEqual(body[119]['branch_target'],142)
        self.assertEqual(body[122]['local_index'],1)
        self.assertEqual(body[127]['local_index'],6)
        symbol,allocation,load=effect_holder_binding(m,135)
        self.assertEqual((allocation,load),(123,100));self.assertIn('MobEffects.SLOW_FALLING',symbol)
        self.assertEqual(literal_effect_arguments(m,135),dict(holder=symbol,duration=10,amplifier=0,explicit_flags=[0,0,0]))
        self.assertIn('LivingEntity.addEffect',body[138]['operand']);self.assertEqual(body[141]['opcode'],'0x57')

    def test_holder_local_requires_one_exact_assignment_not_a_nearby_query(self):
        m=copy.deepcopy(method('server/potion/SugarRushEffect','applyEffectTick'))
        next(i for i in m['instructions'] if i['offset']==127)['local_index']=5
        with self.assertRaises(AssertionError):effect_holder_binding(m,135)
        m=copy.deepcopy(method('server/potion/SugarRushEffect','applyEffectTick'))
        m['instructions'].insert(-1,dict(offset=144,opcode='0x3a',operand=None,local_index=6))
        with self.assertRaises(AssertionError):effect_holder_binding(m,135)
        m=copy.deepcopy(method('server/potion/SugarRushEffect','applyEffectTick'))
        next(i for i in m['instructions'] if i['offset']==108)['operand']='net/minecraft/world/effect/MobEffectInstance'
        with self.assertRaises(AssertionError):effect_holder_binding(m,135)

    def test_time_duration_and_float_argument_are_one_original_literal_local(self):
        body=by_offset(method('server/event/CommonEvents','livingAddEffect'))
        self.assertEqual(body[181]['operand'],2.0)
        self.assertEqual([body[o]['local_index'] for o in (182,196,201)],[3,3,3])
        self.assertEqual(body[197]['opcode'],'0x6a');self.assertIn('Mth.ceil(F)I',body[198]['operand'])
        self.assertIn('enterSlowMotion',body[202]['operand'])
        candidates=[c for c in self.batch['effects'][0]['scalable_parameter_candidates'] if c['primitive']=='TIME_CONTROL_REQUEST']
        self.assertEqual(len(candidates),1);self.assertEqual(candidates[0]['parameters'],['duration_multiplier'])
        self.assertEqual(candidates[0]['native_literal_numeric_input_binding']['read_offsets'],[196,201])

    def test_enter_updates_first_matching_entity_id_duration_only(self):
        body=by_offset(method('server/potion/SugarRushEffect','enterSlowMotion'))
        self.assertEqual(body[4]['branch_target'],124);self.assertEqual(body[11]['branch_target'],124)
        self.assertIn('LocalEntityTickRateModifier',body[59]['operand'])
        self.assertEqual(body[81]['branch_target'],92)
        self.assertIn('setMaxDuration',body[88]['operand']);self.assertEqual(body[91]['opcode'],'0xb1')
        self.assertEqual(body[109]['operand'],10.0)
        self.assertEqual(body[116]['local_index'],2);self.assertEqual(body[117]['local_index'],3)
        self.assertTrue(body[118]['operand'].endswith('EntityType;DLnet/minecraft/resources/ResourceKey;IF)V'))
        self.assertFalse(any('getDimension' in str(i['operand']) or 'setTickRate' in str(i['operand']) for i in body.values()))

    def test_leave_removes_last_match_and_expiry_remove_travel_are_separate(self):
        body=by_offset(method('server/potion/SugarRushEffect','leaveSlowMotion'))
        self.assertEqual(body[86]['local_index'],3);self.assertEqual(body[87]['branch_target'],35)
        self.assertIn('List.remove',body[99]['operand']);self.assertEqual(body[104]['opcode'],'0x57')
        remove=method('server/event/CommonEvents','livingRemoveEffect')['instructions']
        self.assertFalse(any('leaveSlowMotion' in str(i['operand']) for i in remove))
        expiry=by_offset(method('server/event/CommonEvents','livingExpireEffect'))
        self.assertIn('sugarRushSlowsTime',expiry[102]['operand']);self.assertIn('leaveSlowMotion',expiry[122]['operand'])
        travel=new_method('server/event/CommonEvents','travelToDimension')
        self.assertTrue(any('leaveSlowMotion' in str(i['operand']) for i in travel['instructions']))
        self.assertFalse(any('sugarRushSlowsTime' in str(i['operand']) or 'isCanceled' in str(i['operand']) or 'getDimension' in str(i['operand']) for i in travel['instructions']))

    def test_player_queries_use_return_speed_but_flying_uses_getspeed(self):
        speed=by_offset(new_method('mixin/PlayerMixin','ac_getSpeed'))
        flying=by_offset(new_method('mixin/PlayerMixin','ac_getFlyingSpeed'))
        self.assertIn('getReturnValue',speed[43]['operand']);self.assertEqual(speed[52]['operand'],3.0)
        self.assertIn('PlayerMixin.getSpeed()F',flying[43]['operand']);self.assertEqual(flying[46]['operand'],0.5)
        self.assertFalse(any('getReturnValue' in str(i['operand']) for i in flying.values()))
        for name in ('ac_getSpeed','ac_getFlyingSpeed'):
            m=new_method('mixin/PlayerMixin',name)
            a=next(a for a in m['annotations'] if a['descriptor'].endswith('/Inject;'))['values']
            self.assertTrue(a['cancellable']);self.assertEqual(a['at'][0]['values']['value'],'RETURN')

    def test_proxy_comparisons_and_validity_do_not_prove_external_execution(self):
        server=by_offset(new_method('server/CommonProxy','isTickRateModificationActive'))
        client=by_offset(new_method('client/ClientProxy','isTickRateModificationActive'))
        self.assertIn('getServerTickLengthMs',server[7]['operand']);self.assertEqual(server[10]['operand'],50)
        self.assertIn('getClientTickRate',client[6]['operand']);self.assertEqual(client[9]['operand'],50.0)
        valid=by_offset(new_method('mixin/PlayerMixin','isTimeModificationValid'))
        self.assertEqual(valid[4]['branch_target'],17);self.assertEqual(valid[14]['branch_target'],21)
        self.assertEqual(valid[17]['operand'],1);self.assertEqual(valid[21]['operand'],0)
        dep=self.batch['dependency_obligations'][0]
        self.assertEqual(dep['id'],OBLIGATION);self.assertEqual(dep['status'],'EXACT_INSTALLED_BINARY_PIN_MISSING')
        self.assertTrue(dep['completion_blocked_for_this_scope'])
        self.assertEqual(self.batch['effects'][0]['unresolved_ambiguities'],[OBLIGATION])
        packet=read_json(OUT/NEW)
        self.assertTrue(all(w['entry'].startswith(PREFIX) for w in packet['witnesses']))
        player=next(w for w in packet['witnesses'] if w['entry'].endswith('/PlayerMixin.class'))
        self.assertEqual(player['interfaces'],['com/github/alexthe666/citadel/server/entity/IModifiesTime'])
        self.assertTrue(set(player['interfaces']) <= set(dep['exact_consumers']))
        found=read_json(OUT/'native-evidence/alexscaves-status-foundation.json')
        meta=next(w for w in found['witnesses'] if w['entry']=='META-INF/neoforge.mods.toml')
        required=tomllib.loads(meta['text'])['dependencies']['alexscaves']
        self.assertEqual(next(d for d in required if d['modId']=='citadel')['versionRange'],'[2.6.0,)')

    def test_config_default_is_exact_partial_constructor_not_whole_config_closure(self):
        ctor=by_offset(new_method('server/config/ACServerConfig','<init>'))
        self.assertEqual(ctor[752]['operand'],'sugar_rush_slows_time');self.assertEqual(ctor[755]['operand'],1)
        self.assertIn('Builder.define(Ljava/lang/String;Z)',ctor[756]['operand'])
        combined=copy.deepcopy(self.before);combined['effects']+=self.batch['effects'];combined['paths']+=self.batch['paths']
        combined['reviewed_batches'].append(BATCH)
        _,pending=reconcile(combined,self.census)
        self.assertTrue(any(m['entry'].endswith('/ACServerConfig.class') and m['method']=='<init>' for m in pending))
        # No unreviewed magnet or Player eating branches are closed by this batch.
        self.assertTrue(any(m['entry'].endswith('/MagnetUtil.class') and m['method']=='tickMagnetism' for m in pending))
        self.assertTrue(any(m['entry'].endswith('/PlayerMixin.class') and m['method']=='ac_eat' for m in pending))

    def test_wrong_constants_and_generic_time_alias_fail_native_validation(self):
        for primitive,parameter,wrong in [('FORCED_MOVEMENT','upward_y_factor',0.45),
                ('PLAYER_SPEED_QUERY','flying_from_getSpeed_factor',3.0),
                ('TIME_CONTROL_REQUEST','duration_multiplier',3.0)]:
            b=copy.deepcopy(self.batch)
            next(c for c in b['effects'][0]['components'] if c['primitive']==primitive)['numerical_parameters'][parameter]=wrong
            with self.assertRaises(AssertionError):validate_batch(b,self.before,self.census)
        b=copy.deepcopy(self.batch);b['effects'][0]['scalable_parameter_candidates'].append(copy.deepcopy(b['effects'][0]['scalable_parameter_candidates'][-1]))
        with self.assertRaises(AssertionError):validate_batch(b,self.before,self.census)

    def test_exact_caller_index_retains_external_request_reachability(self):
        callers=[(m['entry'],m['method']) for m in self.census['methods'] if any(
            'SugarRushEffect.leaveSlowMotion(' in i['operand'] for i in decode_sites(self.census,m,'calls'))]
        self.assertEqual({name for entry,name in callers},{'livingExpireEffect','travelToDimension'})

    def test_regeneration_is_byte_identical(self):
        from assemble_alexscaves_sugar_rush import build
        self.assertEqual((json.dumps(build(),ensure_ascii=False,indent=2)+'\n').encode(),(OUT/BATCH).read_bytes())


if __name__=='__main__':unittest.main()
