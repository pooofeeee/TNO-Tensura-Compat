"""Authored Darkness/Rage contracts, reusing the locked status foundation."""
from catalog_common import OUT, BASELINE, read_json, write_json
from assemble_alexscaves_status_foundation import (PREFIX,PACKET,proof,method,candidate,
    component,row,vector)
from promote_combat_batch import (literal_numeric_input_binding,
    literal_last_numeric_argument_binding,literal_effect_arguments,
    effect_holder_binding)

BATCH='alexscaves-r2m8b-darkness-rage-and-vision-context.json'
NEW='native-evidence/alexscaves-status-lifecycle.json'
CHECKPOINT='R2m8b-alexscaves-darkness-rage-and-vision-context-closed'
NEXT=('R2m8c — AlexCaves Magnetizing shared movement/attachment contract and Sugar Rush '
      'lifecycle/time-control dependency: reuse locked status cores and finite field/call indexes; '
      'resolve the directly consumed Citadel tick-controller pin where necessary, then native status doses and actor-specific producers.')


def new_proof(short,names,partial=False):
    entry=PREFIX+short+'.class'
    return dict(evidence_file=NEW,witness_id='alexscaves:status-lifecycle:'+entry,entry=entry,methods=names,
                **({'partial_contract':True} if partial else {}))


def new_method(short,name):
    w=next(w for w in read_json(OUT/NEW)['witnesses'] if w['entry']==PREFIX+short+'.class')
    return next(m for m in w['methods'] if m['name']==name)


def new_candidate(short,name,offset,primitive,parameters,units,**binding):
    m=new_method(short,name);i=next(i for i in m['instructions'] if i['offset']==offset)
    p=new_proof(short,[name]);p.update(descriptor=m['descriptor'],offset=offset,operand=i['operand'],opcode=i['opcode'])
    return dict(primitive=primitive,parameters=parameters,units=units,observation_only=True,
        native_consumer=p,native_parameter_identity=dict(entry=p['entry'],method=name,descriptor=m['descriptor'],offset=offset),**binding)


def build():
    registry=proof('server/potion/ACEffectRegistry',['<clinit>'],True)
    setup=[proof('AlexsCaves',['<init>'],True),proof('server/CommonProxy',['commonInit'])]
    darkness='server/potion/DarknessIncarnateEffect';rage='server/potion/RageEffect'
    dt=method(darkness,'toggleFlight');rt=method(rage,'applyEffectTick')
    handoff=new_method('mixin/LivingEntityMixin','ac_livingTick')
    holder,allocation,load=effect_holder_binding(handoff,26)
    flight_tail=new_proof('mixin/LivingEntityMixin',['ac_livingTick'],True)
    flight_tail['closed_instruction_ranges']=[[0,32],[127,233]]
    dark=row('darkness_incarnate','CUSTOM_CONTROL',
        'Every positive-duration native effect tick discards the parent tick result, enables flight through toggleFlight(true), adds Y0.1 when onGround, and retains native idle-sound RNG. ServerPlayer flight enables mayfly/flying and hardcodes speed0.05000000074505806*4.0; enabling ability sync occurs only when previous flying differs from the requested true flag. toggleFlight always clears recipient fallDistance, including nonplayers/client. On native removal/expiry toggleFlight(false) restores hardcoded base speed; non-spectators stop flying, non-creative actors lose mayfly and receive a slow-fall flag, while original creative/spectator distinctions and update calls remain. Separately, the LivingEntity.tick TAIL consumes and clears an existing slow-fall flag before requesting hidden native Slow Falling80/0 (all explicit flags false, result discarded); then it detects prior Darkness presence followed by absence and independently restores non-creative/non-spectator ServerPlayer flight state and sets the flag again. These native paths can request the handoff on successive ticks; no dedup or unconditional replacement is added. The post-entity-tick hook requests removal every fifth tick when root-vehicle-position block light, or native sky/time rule, reaches11. Effect-object first/last-duration fields only feed original visual intensity and remain singleton-local.',
        [component('FLIGHT_CONTROL',dict(active_speed_multiplier=4.0,native_base_speed=0.05000000074505806),
            dict(enabled_flying_speed='native_base_speed*active_speed_multiplier'),
            native_restore='hardcoded0.05000000074505806; original abilities flags and sync gates'),
         component('FORCED_MOVEMENT',dict(grounded_y_addend=0.1),operation='original movement.add(0,0.1,0) only onGround'),
         component('FALL_DAMAGE_GATE'),
         component('MOB_EFFECT_SLOW_FALLING',dict(duration=80,amplifier=0),native_flags=[False,False,False]),
         component('ENVIRONMENTAL_STATUS_REMOVAL',dict(check_period=5,brightness_threshold=11,sky_brightness=15,day_low=0.259,day_high=0.74),
            dict(isInLight='rootVehicle.blockPosition block-light; if canSeeSky AND (timeOfDay<0.259 OR timeOfDay>0.74), brightness=15; compare brightness>=11'))],
        [candidate(darkness,'toggleFlight',84,'FLIGHT_CONTROL',['active_speed_multiplier'],'native multiplier of hardcoded flight speed',
             native_literal_numeric_input_binding=literal_numeric_input_binding(dt,84)),
         vector(darkness,30,{'grounded_y_addend':'y'}),
         new_candidate('mixin/LivingEntityMixin','ac_livingTick',26,'MOB_EFFECT_SLOW_FALLING',['duration','amplifier'],'original native effect ticks/amplifier',
             native_holder_symbol=holder,native_holder_allocation_offset=allocation,native_holder_load_offset=load,
             native_literal_effect_arguments=literal_effect_arguments(handoff,26),
             native_recipient_context=dict(kind='MIXIN_TARGET_THIS',target='net/minecraft/world/entity/LivingEntity',receiver_load_offset=12,add_effect_offset=29))],
        [proof(darkness,['<init>','applyEffectTick','onEffectStarted','getActiveTime','shouldApplyEffectTickThisTick','toggleFlight','getIntensity','isInLight','isCreativePlayer']),
         proof('server/potion/ACEffectRegistry',['lambda$static$6']),registry,*setup,
         proof('server/event/CommonEvents',['livingTick','livingRemoveEffect','livingExpireEffect'],True),
         flight_tail,new_proof('mixin/LivingEntityMixin',['setSlowFallingFlag','hasSlowFallingFlag'])],
        dict(tick='remaining duration>0; amplifier unused by physical tick',flight='server side ServerPlayer for abilities; fallDistance reset is outside that gate',
             cleanup='native removal/expiry and separate prior-presence TAIL reader; original creative/spectator distinctions',
             handoff='consume existing per-entity flag first, then detect disappearance; no new alive/effect/source recheck',
             environment='tickCount%5==0 and native root-vehicle light rule; native removal return ignored'),
        'Native effect removal/expiry, direct flight cleanup and delayed per-entity flag handoff remain separate occurrences. No saved progression/owner carrier.',
        'native abilities flight and Slow Falling inside custom flight/light-conditioned status control')
    dark['hurt_return_dependency']='No damage request. Native Slow Falling addEffect and native status removal returns are discarded.'
    dark['reference_evidence'].append(NEW)
    dark['native_non_candidate_context']='Flight restore baseline, fallDistance reset and brightness/admission gates remain native context; their numerical form does not automatically make them Stage parameters.'

    r=row('rage','CUSTOM_CONTROL',
        'Each positive-duration tick, if ATTACK_DAMAGE exists, compute float((1+amplifier)*2.5)*(1-health/maxHealth), remove existing alexscaves:rage_attack_boost if present, then add one same-ID transient ADD_VALUE modifier. No clamp, own native damage request, or parent-template registration is added. Server Mob recipients with no target, tickCount%10==0 and nextInt(2)==0 scan living-alive candidates in boundingBox.inflate(80). The first eligible candidate needs no nearer-choice RNG; a later candidate can replace it only if strictly closer and a fresh nextInt(2)==0. Native self, both-direction alliance and canAttack checks remain after that choice gate. The selected actor becomes both lastHurtByMob and target. The native random-bound particle loop runs afterwards and is retained without being a Stage proc candidate. The only original native removeRageModifier caller is this active tick; the inspected Remove/Expired hooks and empty MobEffect template map provide no own expiry/cure cleanup for this manually inserted transient modifier. Do not silently add one or claim the bonus is permanent across unrelated lifecycle/attribute operations.',
        [component('ATTRIBUTE_MODIFIER',dict(missing_health_amplifier_coefficient=2.5),
            dict(amount='float((1+amplifier)*coefficient)*(1-health/maxHealth); widened to double at modifier construction'),
            attribute='ATTACK_DAMAGE',modifier_id='alexscaves:rage_attack_boost',native_operation='ADD_VALUE',lifecycle='same-ID remove then addTransientModifier each active tick'),
         component('AGGRO_REDIRECTION',dict(search_period=10,search_radius=80.0),
            dict(target='first eligible or RNG-accepted strictly closer candidate; original list order and native gates')),
         component('PROC_CHANCE',dict(scan_rng_bound=2,nearer_choice_rng_bound=2),
            dict(scan='RandomSource.nextInt(scan_rng_bound)==0',replace='only for strictly closer candidate; nextInt(nearer_choice_rng_bound)==0'))],
        [candidate(rage,'applyEffectTick',18,'ATTRIBUTE_MODIFIER',['missing_health_amplifier_coefficient'],'native float attack-modifier coefficient',
             native_literal_numeric_input_binding=literal_numeric_input_binding(rt,18)),
         candidate(rage,'applyEffectTick',99,'AGGRO_REDIRECTION',['search_period'],'native entity-tick modulo',
             native_literal_numeric_input_binding=literal_numeric_input_binding(rt,99)),
         candidate(rage,'applyEffectTick',124,'AGGRO_REDIRECTION',['search_radius'],'native AABB inflation in blocks',
             native_last_numeric_argument_binding=literal_last_numeric_argument_binding(rt,124)),
         candidate(rage,'applyEffectTick',108,'PROC_CHANCE',['scan_rng_bound'],'exclusive native RandomSource.nextInt bound',
             native_last_numeric_argument_binding=literal_last_numeric_argument_binding(rt,108)),
         candidate(rage,'applyEffectTick',205,'PROC_CHANCE',['nearer_choice_rng_bound'],'exclusive native RandomSource.nextInt bound',
             native_last_numeric_argument_binding=literal_last_numeric_argument_binding(rt,205))],
        [proof(rage,['<init>','applyEffectTick','shouldApplyEffectTickThisTick','removeRageModifier','<clinit>']),
         proof('server/potion/ACEffectRegistry',['lambda$static$2']),registry,*setup],
        dict(attribute='recipient has ATTACK_DAMAGE',tick='remaining duration>0',aggro='server Mob, no existing target, modulo and original RNG checks',
             target='not self; not allied in either direction; native canAttack; strict closer replacement comparison'),
        'Original transient-modifier update and source-free target redirection only. No own removal/expiry/cure listener resets this manually inserted ID; broader native entity/attribute lifecycle remains native.',
        'native additive attack attribute plus custom missing-health formula and probabilistic Mob aggro redirection')
    r['hurt_return_dependency']='No damage request or status delivery in this intrinsic callback; subsequent original attack goals remain native.'
    r['shared_contracts']=[proof('server/event/CommonEvents',['livingRemoveEffect','livingExpireEffect'],True)]
    r['reference_evidence'].append('vanilla-evidence/alexscaves-status-attributes.json')
    v=read_json(OUT/'vanilla-evidence/alexscaves-status-attributes.json')['classes'][0]
    r['shared_contracts'].append(dict(evidence_file='vanilla-evidence/alexscaves-status-attributes.json',
        evidence_format='VANILLA_COMPARISON',entry=v['raw_entry'],methods=['<init>','addAttributeModifiers','removeAttributeModifiers']))

    effects=[dark,r]
    paths=[dict(id=x['delivery_paths'][0],mod_key='alexscaves',labels=['OTHER'],effect_ids=[x['id']],
        primary_source='Registered '+x['id']+' and original native lifecycle readers',implementation=x['implementation']) for x in effects]
    deepsight='server/potion/DeepsightEffect'
    exclusions=[dict(entry=PREFIX+darkness+'.class',disposition='LEGACY_UNCALLED_CURE_HELPER',
        reason='Same independently proven legacy getCurativeItems shape as the locked first status batch; not the actual NeoForge fillEffectCures lifecycle.',implementation=[proof(darkness,['getCurativeItems'])]),
        dict(entry=PREFIX+deepsight+'.class',disposition='REGISTERED_CLIENT_VISION_UTILITY',
        reason='Live registered Deepsight has no intrinsic applyEffectTick/attribute/gameplay-writer override. Its duration fields/intensity only feed source-indexed client fog/brightness readers. Preserve this live vision utility; do not label it a dead method or infer a server damage/control/resource payload from the name.',
        actual_behavior='Original singleton duration fields reset on start; query returns0 absent or1 infinite, otherwise min(20,activeTime+partial,remainingDuration+partial)*0.05000000074505806. Native client readers alter fog planes and brightness. Ordinary render/vision utility excluded from combat scalar contributions; originating native potion doses remain separately queued.',
        implementation=[proof(deepsight,['<init>','getActiveTime','shouldApplyEffectTickThisTick','onEffectStarted','getIntensity']),
            proof('server/potion/ACEffectRegistry',['lambda$static$5']),
            new_proof('mixin/client/LightTextureMixin',['ac_getBrightness'],True),new_proof('client/event/ClientEvents',['fogRender'],True)])]
    return dict(schema='tno.external_effects.reviewed_combat_batch.v1',baseline=BASELINE,mod_key='alexscaves',checkpoint=CHECKPOINT,
        closed_scope='Darkness flight/light-removal/slow-fall lifecycle and Rage attribute/aggro/cleanup contracts closed; live Deepsight vision utility explicitly accounted for. Locked first three statuses reused. Larger magnetism and Citadel time-controller domains remain a separate bounded task; mixed callbacks retain their unreviewed branches.',
        effects=effects,paths=paths,record_refinements=[],exclusions=exclusions,
        locked_canonical_contracts_reused=['alexscaves:bubbled','alexscaves:irradiated','alexscaves:stunned'],
        pending_status_contracts=['MagnetizedEffect and shared MagnetUtil/mixin movement/attachment','SugarRushEffect and directly used Player/Citadel lifecycle'],
        pending_shared_methods=['CommonEvents.livingTick non-status branches','CommonEvents.livingRemoveEffect/livingExpireEffect SugarRush branches',
            'LivingEntityMixin.ac_livingTick Frostmint branch','ACEffectRegistry doses/brewing and remaining registrations'],
        native_quirks_preserved=['Rage manual transient modifier lacks an own effect-expiry cleanup path.',
            'Darkness slow-fall flag is consumed before the separate disappearance reader can set it again.',
            'Brightness/native restore baselines and singleton visual timers are not progression ownership.'],
        exact_next_task=NEXT,stage_policy_decided=False,runtime_tests=0)


if __name__=='__main__':
    b=build();write_json(OUT/BATCH,b)
    print(dict(records=len(b['effects']),numeric_candidates=sum(len(c['parameters']) for r in b['effects'] for c in r['scalable_parameter_candidates']),checkpoint=CHECKPOINT))
