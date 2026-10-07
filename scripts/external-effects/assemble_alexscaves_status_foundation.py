"""Authored, bounded status contracts; helpers only bind pinned native inputs."""
from catalog_common import OUT, WORK, BASELINE, read_json, write_json, sha256
from promote_combat_batch import (literal_vector_components_binding,
    literal_effect_attribute_binding, literal_integer_dividend_binding,
    literal_numeric_input_binding, literal_last_numeric_argument_binding)

KEY='alexscaves'
PREFIX='com/github/alexmodguy/alexscaves/'
PACKET='native-evidence/alexscaves-status-foundation.json'
BATCH='alexscaves-r2m8a-status-foundation.json'
CHECKPOINT='R2m8a-alexscaves-pinned-foundation-and-three-intrinsic-status-contracts'
NEXT=('R2m8b — AlexCaves remaining registered status/control contracts: reuse the captured '
      'Darkness Incarnate, Rage, Sugar Rush, Magnetizing and Deepsight cores; close their '
      'direct lifecycle/mixin/Citadel state dependencies before status producers and actor families.')


def proof(short, names, partial=False):
    entry=PREFIX+short+'.class'
    return dict(evidence_file=PACKET,witness_id=KEY+':status-foundation:'+entry,
                entry=entry,methods=names,**({'partial_contract':True} if partial else {}))


def resource(entry):
    return dict(evidence_file=PACKET,witness_id=KEY+':status-foundation:'+entry,entry=entry)


def method(short, name):
    w=next(w for w in read_json(OUT/PACKET)['witnesses'] if w['entry']==PREFIX+short+'.class')
    return next(m for m in w['methods'] if m['name']==name)


def candidate(short, name, offset, primitive, parameters, units, **binding):
    m=method(short,name);hit=next(i for i in m['instructions'] if i['offset']==offset)
    p=proof(short,[name]);p.update(descriptor=m['descriptor'],offset=offset,
                                  operand=hit['operand'],opcode=hit['opcode'])
    return dict(primitive=primitive,parameters=parameters,units=units,
        native_parameter_identity=dict(entry=p['entry'],method=name,descriptor=m['descriptor'],offset=offset),
        native_consumer=p,observation_only=True,**binding)


def vector(short,offset,parameters):
    binding=literal_vector_components_binding(method(short,'applyEffectTick'),offset)
    return candidate(short,'applyEffectTick',offset,'FORCED_MOVEMENT',list(parameters),
        'native per-tick vector components; not vanilla knockback',
        native_literal_vector_components_binding=binding,native_vector_parameter_roles=parameters)


def component(primitive, values=None, formulas=None, **context):
    return dict(primitive=primitive,numerical_parameters=values or {},parameter_formulas=formulas or {},**context)


def row(identifier,classification,behavior,components,candidates,implementation,gates,lifecycle,vanilla):
    resources=read_json(WORK/KEY/'resources.json')
    language=resources['assets/alexscaves/lang/en_us.json']['data']
    display=language['effect.'+KEY+'.'+identifier]
    path=KEY+':intrinsic_status:'+identifier
    return dict(id=KEY+':'+identifier,mod_key=KEY,display_name=display,registry_ids=[KEY+':'+identifier],
        primary_classification=classification,inspection_status='VERIFIED_NATIVE_CORE_AND_DIRECT_SHARED_READERS',
        scope='Intrinsic status plus directly necessary shared readers. Native doses/actor-specific admission and delivery producers remain independently queued.',
        actual_behavior=behavior,closest_vanilla_equivalent=vanilla,
        vanilla_similarities='Uses the exact native APIs/components below; original admission, defenses, effect stacking and removal remain native.',
        vanilla_differences=behavior,components=components,scalable_parameter_candidates=candidates,
        binary_parameters=gates,lifecycle=lifecycle,
        source_actor='Original affected LivingEntity. These intrinsic callbacks retain no originating attacker/owner/team identity.',
        native_boundary=[PREFIX+p['entry'].split(PREFIX)[-1]+':'+','.join(p['methods']) for p in implementation],
        hurt_return_dependency='Native hurt results are discarded; no return-conditioned secondary payload is added.' if identifier!='stunned' else 'No damage request; direct-source incoming-damage cancellation is a native binary gate.',
        ownership_note='No progression ownership is inferred from a status holder or recipient. Specific native producers remain separate.',
        delivery_paths=[path],primary_test_source='Registered native status callback and directly bound native readers',alternate_sources=[],
        implementation=implementation,reference_evidence=[PACKET,'vanilla-evidence/alexscaves-status-lifecycle.json',
            'reference-evidence/cataclysm-ghost-fear-244.json','reference-evidence/cataclysm-stun-244.json'],
        unresolved_ambiguities=[])


def build():
    registry=proof('server/potion/ACEffectRegistry',['<clinit>'],True)
    setup=[proof('AlexsCaves',['<init>'],True),proof('server/CommonProxy',['commonInit'])]
    tag=[proof('server/misc/ACTagRegistry',['<clinit>'],True),proof('server/misc/ACTagRegistry',['registerEntityTag'])]
    bubbled='server/potion/BubbledEffect'
    b=method(bubbled,'applyEffectTick')
    effects=[]
    effects.append(row('bubbled','CUSTOM_STATUS',
        'Every native effect tick: canBreatheUnderwater OR AQUATIC-tag actors take the aquatic branch; unless RESISTS_BUBBLED, set air to native maximum and add Y=-0.08 when airborne. Other actors, unless native water-breathing or player abilities.invulnerable, multiply current X/Z by 0.800000011920929, subtract2 air with floor-20, and at air<=-20 reset air0, execute the native eight-bubble RNG/particle loop, then request ownerless native drowning damage2 and discard its return. The resistance tag is checked only in the aquatic branch. Two active mixins suppress increaseAirSupply for any bubbled actor and report isInWater=true only for non-resistant canBreatheUnderwater actors. The post-entity-tick hook requests removal when native isInFluidType() is true.',
        [component('FORCED_MOVEMENT',dict(aquatic_airborne_y_addend=-0.08,x_factor=0.800000011920929,z_factor=0.800000011920929),
            operation='add(0,-0.08,0) in aquatic airborne branch; multiply(xFactor,1,zFactor) in non-aquatic branch'),
         component('AIR_RESOURCE',dict(air_drain=2,air_floor=-20,reset_air=0),
            dict(air='max(originalAir-2,-20); exhaustion branch resets0 before damage'),native_operation='setAirSupply'),
         component('NATIVE_DAMAGE_REQUEST',dict(requested_damage=2.0),damage_source='native damageSources().drown(); no direct/causing entity'),
         component('FLUID_QUERY_AND_AIR_REGEN_GATE')],
        [vector(bubbled,58,{'aquatic_airborne_y_addend':'y'}),vector(bubbled,108,{'x_factor':'x','z_factor':'z'}),
         candidate(bubbled,'applyEffectTick',120,'AIR_RESOURCE',['air_drain'],'air units per native tick',
             native_literal_numeric_input_binding=literal_numeric_input_binding(b,120)),
         candidate(bubbled,'applyEffectTick',283,'NATIVE_DAMAGE_REQUEST',['requested_damage'],'requested native damage before admission',
             native_last_numeric_argument_binding=literal_last_numeric_argument_binding(b,283))],
        [proof(bubbled,['<init>','applyEffectTick','shouldApplyEffectTickThisTick']),
         proof('server/potion/ACEffectRegistry',['lambda$static$4']),registry,*setup,*tag,
         proof('mixin/EntityMixin',['ac_isInWater']),proof('mixin/LivingEntityMixin',['ac_increaseAirSupply']),
         proof('server/event/CommonEvents',['livingTick'],True)],
        dict(aquatic_branch='canBreatheUnderwater OR native AQUATIC tag',resistance='RESISTS_BUBBLED checked only within aquatic branch',
             other_branch_admission='native hasWaterBreathing and player abilities.invulnerable gates',
             air_regeneration='active increaseAirSupply HEAD injection returns its original input',
             removal='has BUBBLED and native isInFluidType true; native removeEffect result ignored'),
        'Core returns true; amplifier is unused. Native duration/stacking/removal applies; no custom cleanup or new carrier.',
        'native air supply and drowning damage inside a custom bubble/control status'))
    effects[-1]['native_resource_evidence']=[resource('data/alexscaves/tags/entity_type/resists_bubbled.json'),resource('alexscaves.mixins.json')]

    irradiated='server/potion/IrradiatedEffect'
    i=method(irradiated,'applyEffectTick');cadence=method(irradiated,'shouldApplyEffectTickThisTick')
    effects.append(row('irradiated','CUSTOM_STATUS',
        'Tick admission is false for amplifier<=0. Otherwise interval=Java int200/amplifier: if interval>1, admit remainingDuration%interval==interval/2; else admit every tick. At each admitted tick count exact worn Hazmat mask/chestplate/leggings/boots; amount=1F-count*0.25F. Players wearing zero pieces receive food exhaustion0.4000000059604645 before the damage branch. Unless recipient is RaycatEntity, draw level.random.nextFloat and, when random<amount+0.10000000149011612, request original amount of ownerless alexscaves:radiation damage; discard hurt return. Four pieces produce zero damage with a0.1 trial, not a new immunity gate. An independently registered heal event cancels healing whenever the recipient has IRRADIATED and lacks RESISTS_RADIATION; that tag is not read by the intrinsic damage tick.',
        [component('CUSTOM_RADIATION_DAMAGE',dict(base_amount=1.0,hazmat_piece_reduction=0.25),
            dict(requested_damage='1F - exactWornHazmatPieces*0.25F'),damage_type='alexscaves:radiation',
            source='DamageSourceRandomMessages(HolderReference,2) delegates to ownerless DamageSource(Holder);2 is death-message variation, not damage'),
         component('FOOD_EXHAUSTION',dict(amount=0.4000000059604645)),
         component('PROC_CHANCE',dict(damage_chance_bias=0.10000000149011612),dict(threshold='requested_damage + bias; compare native random.nextFloat() < threshold; no clamp')),
         component('EFFECT_TICK_CADENCE',dict(cadence_numerator=200),dict(interval='Java integer200/amplifier; see native admission gates')),
         component('HEAL_ADMISSION')],
        [candidate(irradiated,'applyEffectTick',79,'CUSTOM_RADIATION_DAMAGE',['requested_damage'],'native damage request after existing Hazmat reduction'),
         candidate(irradiated,'applyEffectTick',35,'FOOD_EXHAUSTION',['amount'],'native player exhaustion',
             native_last_numeric_argument_binding=literal_last_numeric_argument_binding(i,35)),
         candidate(irradiated,'applyEffectTick',61,'PROC_CHANCE',['damage_chance_bias'],'addend in native random comparison',
             native_literal_numeric_input_binding=literal_numeric_input_binding(i,61)),
         candidate(irradiated,'shouldApplyEffectTickThisTick',10,'EFFECT_TICK_CADENCE',['cadence_numerator'],'native integer cadence numerator in ticks',
             native_literal_integer_dividend_binding=literal_integer_dividend_binding(cadence,10))],
        [proof(irradiated,['<init>','applyEffectTick','shouldApplyEffectTickThisTick']),
         proof('server/potion/ACEffectRegistry',['lambda$static$3']),registry,*setup,*tag,
         proof('server/item/HazmatArmorItem',['getWornAmount']),
         proof('server/misc/ACDamageTypes',['causeRadiationDamage']),proof('server/misc/ACDamageTypes',['<clinit>'],True),
         proof('server/misc/ACDamageTypes$DamageSourceRandomMessages',['<init>']),proof('server/event/CommonEvents',['livingHeal'])],
        dict(amplifier='<=0 skips tick; positive value uses original integer cadence',
             exhaustion='Player AND exact wornHazmatPieceCount==0',damage='recipient not RaycatEntity AND native RNG comparison',
             healing='status present AND recipient type not in native RESISTS_RADIATION tag'),
        'Core returns true, and damage source stores no actor. Native duration/admission/defenses remain unchanged. No extra healing, status or damage callback.',
        'custom damage type, equipment-conditioned damage/exhaustion, and a separate native healing veto'))
    effects[-1]['native_resource_evidence']=[resource('data/alexscaves/damage_type/radiation.json'),resource('data/alexscaves/tags/entity_type/resists_radiation.json')]
    effects[-1]['native_defense_context']={'hazmat_piece_reduction':0.25,'meaning':'Original native defense contribution; recording a numeric value does not automatically promote it to a Stage candidate.'}

    stunned='server/potion/StunnedEffect';binding=literal_effect_attribute_binding(method(stunned,'<init>'),26)
    effects.append(row('stunned','CUSTOM_CONTROL',
        'The registered status adds MOVEMENT_SPEED template coefficient-1, original alexscaves:stunned_slowdown ID, ADD_MULTIPLIED_BASE; native template creation multiplies the coefficient by amplifier+1. Each positive-duration tick dampens only positive Y motion by0.1. Mob recipients are pitched30 degrees (current and old XRot); on server their MOVE/JUMP/LOOK goal-control flags are disabled. Original stun-star RNG/particles remain. The native incoming-damage subscriber cancels only when DamageSource.getDirectEntity() is a LivingEntity with STUNNED; it does not replace direct source with causing/owner. Its preceding resistor-shield/arrow query branch has no writer or payload. No own flag-restoration callback is added; native Mob.tick/updateControlFlags still restores/recomputes flags according to native riding state, and native effect removal removes its attribute template.',
        [component('ATTRIBUTE_MODIFIER',dict(movement_speed_coefficient=-1.0),dict(amount='coefficient*(native amplifier+1)'),
            native_attribute_symbol=binding['attribute_symbol'],native_operation_symbol=binding['operation_symbol'],modifier_id=binding['identifier']),
         component('FORCED_MOVEMENT',dict(upward_y_factor=0.1),operation='multiply(1,0.1,1) only when original Y>0'),
         component('FORCED_FACING',dict(mob_pitch=30.0)),component('AI_CONTROL'),component('DIRECT_SOURCE_ATTACK_ADMISSION')],
        [candidate(stunned,'<init>',26,'ATTRIBUTE_MODIFIER',['movement_speed_coefficient'],'native additive-base attribute template coefficient',native_effect_attribute_binding=binding),
         vector(stunned,22,{'upward_y_factor':'y'}),
         candidate(stunned,'applyEffectTick',116,'FORCED_FACING',['mob_pitch'],'degrees of native Mob pitch',
             native_last_numeric_argument_binding=literal_last_numeric_argument_binding(method(stunned,'applyEffectTick'),116))],
        [proof(stunned,['<init>','applyEffectTick','shouldApplyEffectTickThisTick']),proof('server/potion/ACEffectRegistry',['lambda$static$1']),registry,*setup,
         proof('server/event/CommonEvents',['livingAttack'])],
        dict(tick='remaining duration>0; amplifier does not alter control tick body',vertical_motion='Y>0 only',
             ai='recipient is Mob and server side',attack_veto='original direct source is LivingEntity AND has STUNNED',
             native_control_reset='Vanilla Mob riding/control-flag update; no custom unconditional reset'),
        'Native attribute application/removal and native Mob control-flag recomputation remain authoritative. No speculative persistence/receipt.',
        'native movement attribute plus separate custom vertical/AI/facing control and direct-source attack veto'))
    lifecycle=read_json(OUT/'vanilla-evidence/alexscaves-status-lifecycle.json')
    effects[-1]['shared_contracts']=[dict(evidence_file='vanilla-evidence/alexscaves-status-lifecycle.json',
        evidence_format='VANILLA_COMPARISON',entry=w['raw_entry'],methods=[m['name'] for m in w['methods']]) for w in lifecycle['classes']]
    effects[-1]['shared_contracts'].append(dict(evidence_file='reference-evidence/cataclysm-stun-244.json',
        evidence_format='SHARED_NATIVE_REFERENCE',entry='net/minecraft/world/effect/MobEffect$AttributeTemplate.class',methods=['create']))

    paths=[dict(id=r['delivery_paths'][0],mod_key=KEY,labels=['OTHER'],effect_ids=[r['id']],
        primary_source='Registered '+r['id']+' native tick and original direct shared readers',implementation=r['implementation']) for r in effects]
    census=read_json(OUT/('alexscaves-combat-census.json'))
    fields=read_json(OUT/('alexscaves-native-field-use-index.json'))
    unresolved_producers=[]
    for m in fields['methods']:
        hits=[dict(offset=o,symbol=fields['symbols'][s]) for o,op,s in m['field_sites']
            if op==0xb2 and any('/ACEffectRegistry.'+field+'L' in fields['symbols'][s] for field in ('BUBBLED','IRRADIATED','STUNNED'))]
        if hits:unresolved_producers.append(dict(entry=m['entry'],method=m['method'],descriptor=m['descriptor'],code_sha256=m['code_sha256'],field_sites=hits))
    return dict(schema='tno.external_effects.reviewed_combat_batch.v1',baseline=BASELINE,mod_key=KEY,checkpoint=CHECKPOINT,
        closed_scope='Protected original discovery indexes recovered byte-identically; finite native and additive field-use queues established. Bubbled/Irradiated/Stunned intrinsic contracts and directly necessary shared readers closed. Mixed callbacks remain pending where only one contribution is reviewed.',
        effects=effects,paths=paths,record_refinements=[],
        exclusions=[dict(entry=PREFIX+'server/potion/'+cls+'.class',disposition='LEGACY_UNCALLED_CURE_HELPER',
            reason='getCurativeItems is neither a Vanilla1.21.1 MobEffect declaration nor the NeoForge fillEffectCures lifecycle, and has no original census caller/handle. Its empty list does not prove native cure immunity.',
            implementation=[proof('server/potion/'+cls,['getCurativeItems'])]) for cls in ('BubbledEffect','IrradiatedEffect')],
        source_foundation=dict(jar_sha256=census['jar_sha256'],classes=census['parsed_classes'],methods=census['total_methods'],
            original_index_recovery=census['prior_index_recovery'],census_file='alexscaves-combat-census.json',
            field_index_file='alexscaves-native-field-use-index.json',field_index_summary=fields['summary'],
            note='Field index fills GET/PUT sites absent from keyword over-approximation; neither index grants semantic completion.'),
        status_reference_index=unresolved_producers,
        status_reference_index_scope='Readonly reference aid, including already reviewed readers; it does not mark completed readers pending again or prove every site is a producer.',
        pending_status_contracts=['DarknessIncarnateEffect','RageEffect','SugarRushEffect','MagnetizedEffect','DeepsightEffect'],
        pending_shared_methods=['ACEffectRegistry.<clinit> remaining bindings/doses/brewing','CommonEvents.livingTick remaining branches',
            'CommonEvents.livingAddEffect/livingRemoveEffect/livingExpireEffect','ACDamageTypes.<clinit> remaining keys','ACTagRegistry.<clinit> remaining keys','AlexsCaves.<init> remaining registration context'],
        native_legacy_helper_context='Do not infer immunity from unused getCurativeItems. Reuse pinned NeoForge fillEffectCures and native effect/removal contracts.',
        stage_policy_decided=False,runtime_tests=0,exact_next_task=NEXT)


if __name__=='__main__':
    b=build();write_json(OUT/BATCH,b)
    print(dict(records=len(b['effects']),numeric_candidates=sum(len(c['parameters']) for r in b['effects'] for c in r['scalable_parameter_candidates']),checkpoint=CHECKPOINT))
