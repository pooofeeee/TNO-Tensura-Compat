"""Native Sugar Rush contracts; the unpinned Citadel consumer remains explicit."""
from catalog_common import OUT, BASELINE, read_json, write_json
from assemble_alexscaves_status_foundation import (
    PREFIX, PACKET, proof, method, candidate, component, row, vector)
from promote_combat_batch import (
    literal_effect_attribute_binding, literal_numeric_input_binding,
    literal_effect_arguments, effect_holder_binding)

BATCH='alexscaves-r2m8c-sugar-rush-native-contract.json'
NEW='native-evidence/alexscaves-sugar-rush-lifecycle.json'
CHECKPOINT='R2m8c-alexscaves-sugar-rush-native-contract-and-exact-dependency-obligation'
NEXT=('R2m8d — AlexCaves Magnetizing shared movement/attachment contract: reuse the '
      'locked intrinsic status bytes and finite field/call indexes; close MagnetUtil '
      'and directly consumed native mixin/message paths before status doses and actor '
      'families. Sugar Rush Citadel internals remain a separate exact-pin obligation.')
OBLIGATION='alexscaves:sugar_rush:citadel_tick_controller_pin'


def new_proof(short,names,partial=False):
    entry=PREFIX+short+'.class'
    return dict(evidence_file=NEW,witness_id='alexscaves:sugar-rush-lifecycle:'+entry,
                entry=entry,methods=names,**({'partial_contract':True} if partial else {}))


def new_method(short,name):
    w=next(w for w in read_json(OUT/NEW)['witnesses'] if w['entry']==PREFIX+short+'.class')
    return next(m for m in w['methods'] if m['name']==name)


def new_candidate(short,name,offset,primitive,parameters,units,**binding):
    m=new_method(short,name);i=next(i for i in m['instructions'] if i['offset']==offset)
    p=new_proof(short,[name]);p.update(descriptor=m['descriptor'],offset=offset,
                                    operand=i['operand'],opcode=i['opcode'])
    return dict(primitive=primitive,parameters=parameters,units=units,observation_only=True,
                native_consumer=p,native_parameter_identity=dict(entry=p['entry'],method=name,
                descriptor=m['descriptor'],offset=offset),**binding)


def build():
    sugar='server/potion/SugarRushEffect'
    ctor=method(sugar,'<init>');tick=method(sugar,'applyEffectTick')
    attr=literal_effect_attribute_binding(ctor,42)
    holder,allocation,load=effect_holder_binding(tick,135)
    behavior=(
        'The registered native MOVEMENT_SPEED template uses alexscaves:sugar_rush_speed, '
        'coefficient0.25 and ADD_MULTIPLIED_TOTAL; original template creation multiplies '
        'by amplifier+1. Every positive-duration tick returns true. Client tick requests '
        'only native sound; server tick preserves X/Z and multiplies ascending Y by0.85 '
        'or descending Y by0.45. Only the descending arm, when Slow Falling is absent, '
        'requests native Slow Falling10/0 with ambient/visible/icon allfalse; addEffect '
        'return is discarded. No damage or original effect-owner lookup occurs. '
        'With sugarRushSlowsTime enabled, an Added event for a Player with SugarRush '
        'passes ceil(float(nativeDuration)*2F) and the same2F to enterSlowMotion. '
        'ServerLevel-only helper searches Citadel LocalEntityTickRateModifiers by entity '
        'ID; the first matching modifier has only maxDuration updated, then returns. '
        'Otherwise it submits a new modifier with original player ID/type, third '
        'double argument10D, current dimension, supplied duration and supplied float. '
        'The meanings and execution of external constructor fields are not inferred. '
        'Expiration requests leaveSlowMotion only for Player/SugarRush/configtrue; '
        'explicit Remove has only the original exit sound, no leave call. Dimension '
        'travel requests leave whenever the Player still has SugarRush, without a '
        'config check or destination substitution. Leave searches the full list and '
        'removes only the last matching local modifier. No new type/rate/dimension '
        'filter is added to either search. Player RETURN injections with configtrue, '
        'SugarRush and native proxy-active gate multiply original getSpeed by3F; '
        'getFlyingSpeed returns this.getSpeed()*0.5F rather than multiplying original '
        'flying speed. Native proxy compares server tick-length return with50 or '
        'client tracker return with50F. isTimeModificationValid returnsfalse only '
        'for a LocalEntityTickRateModifier when this Player lacks SugarRush. The '
        'external caller of that interface and controller lifecycle require an exact '
        'Citadel binary pin; no effective tick rate, immunity, expiry cleanup or '
        'duration unit conversion beyond these native call arguments is claimed.')
    components=[
        component('ATTRIBUTE_MODIFIER',dict(movement_speed_coefficient=0.25),
            dict(amount='coefficient*(native amplifier+1)'),
            native_attribute_symbol=attr['attribute_symbol'],native_operation_symbol=attr['operation_symbol'],
            modifier_id=attr['identifier']),
        component('FORCED_MOVEMENT',dict(upward_y_factor=0.85,downward_y_factor=0.45),
            operation='server only: original movement.multiply(1,factor,1); choose by original Y sign'),
        component('MOB_EFFECT_SLOW_FALLING',dict(duration=10,amplifier=0),native_flags=[False,False,False]),
        component('PLAYER_SPEED_QUERY',dict(speed_multiplier=3.0,flying_from_getSpeed_factor=0.5),
            dict(speed='original RETURN value*3F',flying='this.getSpeed()*0.5F'),
            native_gate='configtrue AND SugarRush AND native proxy active predicate'),
        component('TIME_CONTROL_REQUEST',dict(duration_multiplier=2.0),
            dict(supplied_duration='Mth.ceil(float(effectInstance.getDuration())*2F)',
                 supplied_float='same native2F local; external field meaning unresolved'),
            native_protocol_context=dict(third_constructor_double=10.0,owner='player native entity ID/type',
                dimension='original current Level.dimension()',server_active_comparison=50,
                client_active_comparison=50.0),external_dependency_obligation=OBLIGATION)]
    candidates=[
        candidate(sugar,'<init>',42,'ATTRIBUTE_MODIFIER',['movement_speed_coefficient'],
            'native additive-total attribute template coefficient',native_effect_attribute_binding=attr),
        vector(sugar,55,{'upward_y_factor':'y'}),vector(sugar,86,{'downward_y_factor':'y'}),
        candidate(sugar,'applyEffectTick',135,'MOB_EFFECT_SLOW_FALLING',['duration','amplifier'],
            'native effect ticks/amplifier',native_holder_symbol=holder,native_holder_allocation_offset=allocation,
            native_holder_load_offset=load,native_literal_effect_arguments=literal_effect_arguments(tick,135),
            native_recipient_context=dict(kind='SUPPLIED_LIVING_ENTITY',receiver_local_index=1,
                                          receiver_load_offset=122,add_effect_offset=138)),
        new_candidate('mixin/PlayerMixin','ac_getSpeed',54,'PLAYER_SPEED_QUERY',['speed_multiplier'],
            'native multiplier of original getSpeed RETURN',
            native_literal_numeric_input_binding=literal_numeric_input_binding(new_method('mixin/PlayerMixin','ac_getSpeed'),54)),
        new_candidate('mixin/PlayerMixin','ac_getFlyingSpeed',48,'PLAYER_SPEED_QUERY',['flying_from_getSpeed_factor'],
            'native multiplier of this.getSpeed, not original flying speed',
            native_literal_numeric_input_binding=literal_numeric_input_binding(new_method('mixin/PlayerMixin','ac_getFlyingSpeed'),48)),
        candidate('server/event/CommonEvents','livingAddEffect',182,'TIME_CONTROL_REQUEST',['duration_multiplier'],
            'one original float local used for duration multiplication and controller request',
            native_literal_numeric_input_binding=literal_numeric_input_binding(method('server/event/CommonEvents','livingAddEffect'),182),
            native_local_value_context=dict(literal_offset=181,store_offset=182,local_index=3,
                multiply_offset=197,ceil_offset=198,controller_float_load_offset=201,request_offset=202,native_value=2.0))]
    implementation=[
        proof(sugar,['<init>','applyEffectTick','shouldApplyEffectTickThisTick','enterSlowMotion','leaveSlowMotion']),
        proof('server/potion/ACEffectRegistry',['lambda$static$7']),
        proof('server/potion/ACEffectRegistry',['<clinit>'],True),
        proof('server/event/CommonEvents',['livingAddEffect','livingExpireEffect','livingRemoveEffect']),
        proof('AlexsCaves',['<init>'],True),proof('server/CommonProxy',['commonInit']),
        new_proof('mixin/PlayerMixin',['ac_getSpeed','ac_getFlyingSpeed','isTimeModificationValid']),
        new_proof('server/event/CommonEvents',['travelToDimension']),
        new_proof('server/config/ACServerConfig',['<init>'],True),
        new_proof('server/CommonProxy',['isTickRateModificationActive']),
        new_proof('client/ClientProxy',['isTickRateModificationActive'])]
    r=row('sugar_rush','CUSTOM_CONTROL',behavior,components,candidates,implementation,
        dict(tick='remainingDuration>0; motion body ignores amplifier; server/client arms separate',
             slow_fall='server descending Y<0 AND no existing native Slow Falling',
             time_config='sugar_rush_slows_time defaults true; still read at original call sites',
             time_enter='Added event Player AND SugarRush AND configtrue; helper server ServerLevel',
             leave_expiry='Player AND nonnull SugarRush instance AND configtrue',
             leave_travel='Player currently has SugarRush; no config/destination/cancellation-result check',
             external_validity='false iff local modifier AND recipient lacks SugarRush'),
        'Native effect/attribute lifecycle and original controller update/removal requests only. '
        'External Citadel execution/validity consumption remains explicitly unresolved until pinned.',
        'native movement attribute and Slow Falling plus custom directional motion, Player queries and external time-controller requests')
    r['inspection_status']='VERIFIED_NATIVE_ALEXSCAVES_BOUNDARIES_EXTERNAL_CITADEL_CONSUMER_PENDING'
    r['scope']='Complete own Sugar Rush contract and direct native event/query/proxy readers. '
    r['scope']+='Native status doses remain queued; exact Citadel internals are not covered.'
    r['hurt_return_dependency']='No hurt request; original Slow Falling addEffect and List.remove returns are discarded.'
    r['reference_evidence'].append(NEW)
    r['unresolved_ambiguities']=[OBLIGATION]
    r['shared_contracts']=[dict(evidence_file='reference-evidence/cataclysm-stun-244.json',
        evidence_format='SHARED_NATIVE_REFERENCE',entry='net/minecraft/world/effect/MobEffect$AttributeTemplate.class',methods=['create'])]
    dependency=dict(id=OBLIGATION,status='EXACT_INSTALLED_BINARY_PIN_MISSING',
        required_mod='citadel',declared_minimum_version='2.6.0',
        source='jar-inventory.json AlexCaves META-INF/neoforge.mods.toml dependency',
        reason='Inventory records only a minimum version; no exact Citadel JAR/version/hash is present. '
               'An arbitrary release would not prove installed runtime controller behavior.',
        exact_consumers=['com/github/alexthe666/citadel/server/tick/ServerTickRateTracker',
            'com/github/alexthe666/citadel/client/tick/ClientTickRateTracker',
            'com/github/alexthe666/citadel/server/tick/modifier/LocalEntityTickRateModifier',
            'com/github/alexthe666/citadel/server/tick/modifier/TickRateModifier',
            'com/github/alexthe666/citadel/server/entity/IModifiesTime'],
        required_facts=['constructor argument meaning and retained ID/type/dimension',
            'server/client controller execution and lifetime units',
            'actual IModifiesTime caller, admission and cleanup lifecycle'],
        completion_blocked_for_this_scope=True)
    return dict(schema='tno.external_effects.reviewed_combat_batch.v1',baseline=BASELINE,
        mod_key='alexscaves',checkpoint=CHECKPOINT,
        closed_scope='Own Sugar Rush attribute/motion/Slow Falling and direct Player/event/proxy '
            'contracts closed; exact external Citadel dependency retained as a completion obligation. '
            'Magnetizing movement/attachment remains the next bounded domain.',
        effects=[r],paths=[dict(id=r['delivery_paths'][0],mod_key='alexscaves',labels=['OTHER'],
            effect_ids=[r['id']],primary_source='Registered Sugar Rush and original event/query readers',implementation=implementation)],
        record_refinements=[],exclusions=[],dependency_obligations=[dependency],
        locked_canonical_contracts_reused=['alexscaves:bubbled','alexscaves:irradiated','alexscaves:stunned',
            'alexscaves:darkness_incarnate','alexscaves:rage'],
        native_quirks_preserved=['Remove has no leaveSlowMotion call.',
            'Enter updates only first matching ID duration; leave removes only last matching ID.',
            'Flying query uses getSpeed, not its original return value.',
            'One2F local feeds two native protocol arguments without double-counting a separate alias.'],
        exact_next_task=NEXT,stage_policy_decided=False,runtime_tests=0)


if __name__=='__main__':
    b=build();write_json(OUT/BATCH,b)
    print(dict(records=len(b['effects']),numeric_candidates=sum(len(c['parameters']) for r in b['effects']
        for c in r['scalable_parameter_candidates']),checkpoint=CHECKPOINT))
