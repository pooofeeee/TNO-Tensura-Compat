"""Focused R2k14a admission/state/encounter and pinned-JAR validation."""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import struct
import subprocess

from catalog_common import OUT, ROOT, read_json
from collect_cataclysm_kobolediator_admission import (
    D, EVIDENCE_FILE, FRAGMENTS, K, METHODS, PKG, PYRAMID, REGISTRY,
    SPEC_FILE, collect, specification,
)

START = '264afa3d24f57a9f3e653f2b2091b5f08c81d037'
CHECKPOINT = 'R2k14a-cataclysm-kobolediator-admission-complete'
NOTE = OUT / 'cataclysm-r2k14a-kobolediator-admission.json'
REVIEW = OUT / 'mod-reviews/cataclysm.json'
LEDGER = OUT / 'mod-completion-ledger.json'
I = 'entity/InternalAnimationMonster/Internal_Animation_Monster'
A = 'entity/etc/Animation_Monsters'
KEYS = {'incoming_admission','poison_dart_admission','projectile_block_admission',
        'projectile_block_response','sleep_admission','native_invulnerability',
        'shared_defense_applicability','environment_admission','effect_admission',
        'awakened_state','awakening_prerequisites','combat_persistence','encounter_setup',
        'pyramid_spawn_prerequisites','death_state_transition'}
KINDS = {'VANILLA_DIRECT','VANILLA_EQUIVALENT','VANILLA_LIKE_EXTENDED','VANILLA_COMPOSITE',
         'CUSTOM_DAMAGE','CUSTOM_STATUS','CUSTOM_CONTROL','CUSTOM_RESOURCE','BINARY_MECHANIC'}
ORDER = ['DIRECT_POISON_DART_REJECTION','CONCRETE_PROJECTILE_BLOCK_ADMISSION',
         'BLOCKED_DIRECT_ARROW_RESPONSE_AND_IDLE_STATE9_FALSE_RETURN',
         'SLEEP_REJECTION_UNLESS_BYPASSES_INVULNERABILITY','UNCHANGED_SOURCE_AND_AMOUNT_TO_NATIVE_HURT',
         'NATIVE_VIRTUAL_INVULNERABILITY_CLIENT_DEAD_FIRE_RESISTANCE',
         'NATIVE_DAMAGE_CONTAINER_EVENTS_SHIELD_FREEZING_HELMET',
         'NATIVE_COOLDOWN_ACTUALLY_HURT_SOURCE_CREDIT_IMPACT_TOTEM_DEATH_CALLBACKS',
         'NATIVE_RETURN_NO_CONCRETE_POST_HURT_WRITE']
DEFENSE_NAMES = {'DamageCap','DpsCap','RangeLimit','NatureRegen','HealCooldown'}
NATIVE_REF = 'reference-evidence/bossesrise-knight-defense-244.json'
f32 = lambda x: struct.unpack('f',struct.pack('f',x))[0]


def at_start(path):
    return subprocess.check_output(['git','show',START+':'+Path(path).relative_to(ROOT).as_posix()],cwd=ROOT)


def selected(review):
    return [e for e in review['effects'] if e['review_checkpoint']==CHECKPOINT]


def validate_records(review, note, ledger):
    effects,paths = review['effects'],review['paths']
    assert len(effects)==len({e['id'] for e in effects})
    assert len(paths)==len({p['id'] for p in paths})
    assert effects==sorted(effects,key=lambda e:e['id']) and paths==sorted(paths,key=lambda p:p['id'])
    new = selected(review)
    assert {e['id'] for e in new}=={'cataclysm:kobolediator_'+k for k in KEYS}
    pids,eids = {p['id'] for p in paths},{e['id'] for e in effects}
    for e in new:
        assert e['mod_key']=='cataclysm' and e['primary_classification'] in KINDS
        assert e['inspection_status']=='STATIC_REVIEWED' and not e['unresolved_ambiguities']
        for k in ['actual_behavior','source_actor','primary_test_source','components','implementation',
                  'delivery_paths','closest_vanilla_equivalent','hurt_return_dependency','binary_parameters']:
            assert e[k],(e['id'],k)
        assert not {'stage_scaling_needed','stage_policy','stage_multiplier','stage_eligibility',
                    'stage_cap','stage_floor','runtime_hook'} & e.keys()
        assert set(e['delivery_paths'])<=pids
        observations=[]
        for c in e['components']:
            assert c['primitive'] and c['formula'] and c['native_boundary'] and c['vanilla_relation']
            assert set(c['numerical_parameters'])==set(c['parameter_units'])
            for p,v in c['numerical_parameters'].items():
                assert isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v)
                observations.append(dict(primitive=c['primitive'],parameter=p,native_value=v,
                    native_formula=c['formula'],units=c['parameter_units'][p],boundary=c['native_boundary']))
            assert set(c.get('parameter_formulas',{}))==set(c.get('formula_parameter_units',{}))
            for p,v in c.get('parameter_formulas',{}).items():
                assert isinstance(v,str) and v
                observations.append(dict(primitive=c['primitive'],parameter=p,native_value=None,
                    native_formula=v,units=c['formula_parameter_units'][p],boundary=c['native_boundary']))
        assert observations==e['numeric_observations']
        assert e['scalable_parameter_candidates']==[], 'Admission/state/setup observations are not automatic Stage candidates'
    new_paths=[p for p in paths if p['id'].startswith('cataclysm:kobolediator-admission:')]
    assert len(new_paths)==15
    for p in new_paths:
        assert p['mod_key']=='cataclysm' and p['status']=='VERIFIED' and p['runtime_status']=='NOT_RUN'
        assert p['primary_source'] and p['native_path'] and p['setup'] and p['implementation'] and p['labels']
        assert p['effect_ids'] and set(p['effect_ids'])<=eids
        for e in new:
            assert (p['id'] in e['delivery_paths'])==(e['id'] in p['effect_ids'])
    assert note['mechanic_packages']==[dict(id=e['id'],primary_classification=e['primary_classification'],
        delivery_paths=e['delivery_paths'],numerical_candidates=e['scalable_parameter_candidates'],binary_gates=e['binary_parameters']) for e in new]
    assert note['facts']=={e['id'].removeprefix('cataclysm:kobolediator_'):e['actual_behavior'] for e in new}
    summary=dict(new_mechanics=len(new),delivery_paths=len(new_paths),
        classifications=dict(sorted(Counter(e['primary_classification'] for e in new).items())),
        candidate_numeric_parameters=0,boss_shared_bindings_applicable=False,unresolved_subsection_ambiguities=0)
    assert summary==note['summary'] and summary['classifications']=={'BINARY_MECHANIC':14,'CUSTOM_CONTROL':1}
    assert next(e for e in new if e['id'].endswith('_projectile_block_response'))['primary_classification']=='CUSTOM_CONTROL'
    assert review['status']==ledger['status']==note['status']=='PARTIAL'
    assert all(review[k] is False for k in ['semantic_discovery_complete','special_damage_discovery_complete',
                                           'source_mapping_complete','delivery_mapping_complete'])
    cat=next(t for t in ledger['targets'] if t['mod_key']=='cataclysm')
    assert cat['state']=='PARTIAL' and cat['semantic_effect_count']==len(effects)
    assert review['checkpoint']==ledger['checkpoint']==note['checkpoint']==CHECKPOINT
    assert review['exact_next_task']==note['exact_next_task']==cat['exact_next_task']
    assert note['exact_next_task'].startswith('R2k14b: Kobolediator offense/payload family.')
    assert note['remaining_kobolediator_work']==['R2k14b Kobolediator offense/payload family']
    assert not note['remaining_subsection_native_ambiguities'] and note['remaining_cataclysm_research']
    assert note['runtime_tests']==0
    assert all(note[k] is False for k in ['whole_mod_complete','stage_eligibility_decided','phase6_reopened',
        'production_changed','stage_changed','boss_testing_started','l2_testing_started','compatibility_fixes_started','phase7_started'])
    validate_contracts({e['id'].removeprefix('cataclysm:kobolediator_'):e for e in new},note)
    return summary


def validate_contracts(rows, note):
    flags={
        'incoming_admission':dict(uses_direct_entity=True,uses_causing_entity_in_prefilters=False,
            incoming_amount_rewritten=False,bypass_skips_earlier_prefilters=False,shared_boss_hurt_reached=False,concrete_post_hurt_write=False),
        'poison_dart_admission':dict(bypass_overrides_dart_rejection=False,excludes_all_poison_sources=False,projectile_payload_reviewed=False),
        'projectile_block_admission':dict(uses_native_source_position=True,uses_causing_range=False,
            renormalizes_after_zero_y=False,reads_arrow_piercing=False,checks_bypasses_shield=False,
            bypass_overrides_block=False,requires_native_using_item=False,block_tests_awaken=False),
        'projectile_block_response':dict(response_requires_hurt_success=False,velocity_rotated_to_new_yaw=False,
            owner_reassigned=False,native_deflect_called=False,duplicate_projectile_created=False,
            local_server_guard=False,block_state_restarts_on_repeat=False),
        'sleep_admission':dict(sleep_means_raw_state1=False,set_sleep_changes_awaken=False,
            set_sleep_heals=False,damage_wakes_entity=False,sleep_bypass_is_unconditional=False),
        'native_invulnerability':dict(concrete_invulnerability_override=False,unconditional_bypass_claimed=False,
            unconditional_fire_immunity_claimed=False,unconditional_fall_immunity_claimed=False),
        'shared_defense_applicability':dict(damage_cap_applicable=False,dps_cap_applicable=False,range_limit_applicable=False,
            nature_regen_applicable=False,heal_cooldown_applicable=False,boss_defaults_substituted=False,
            boss_effect_whitelist_applies=False,boss_home_return_applies=False),
        'environment_admission':dict(air_returns_argument=True,air_returns_native_max=False,can_ride=False,
            factory_fire_immune_call=False,concrete_collision_override=False,inherited_collision_admission=True,
            blanket_drowning_immunity_claimed=False,all_forced_motion_immunity_claimed=False),
        'effect_admission':dict(existing_status_contract_reopened=False,all_other_effects_admitted_claimed=False),
        'awakened_state':dict(awaken_default=False,heal_before_flag_write=True,heal_only_on_false_to_true_transition=False,
            flag_write_requires_heal_success=False,setter_sets_raw_state=False,setter_sets_home=False,
            raw_state_is_stage=False,offensive_execution_reviewed=False),
        'awakening_prerequisites':dict(squared_distance_not_linear_range=True,preserves_vertical_velocity=True,
            stop_checks_target=False,stop_requires_hurt=False,stop_heal_before_raw_state=True,
            awakening_start_restarts_matching_state=False,requires_necklace_or_altar=False),
        'combat_persistence':dict(load_uses_awaken_setter=True,load_true_requests_heal=True,load_replays_sleep_state=False,
            saved_raw_attack_state=False,saved_attack_cooldowns=False,inherited_boss_home_nbt=False,generic_persistence_added=False),
        'encounter_setup':dict(constructor_calls_config_attribute_helper=True,constructor_calls_heal=False,
            constructor_sets_home=False,constructor_sets_awaken=False,explicit_armor_toughness_added=False,config_is_progression=False),
        'pyramid_spawn_prerequisites':dict(marker_checks_bounding_box=False,marker_sets_home=False,marker_sets_awaken=False,
            marker_requires_ignis_flag=False,marker_requires_necklace=False,finalize_sets_sleep_before_parent=True,
            finalize_result_used=False,concrete_spawn_rules_override=False,concrete_spawn_placement_registered=False,
            null_create_clears_marker=False,distance_despawn=False,peaceful_despawn=False,universal_spawn_gate_claimed=False),
        'death_state_transition':dict(state_write_after_super=True,state_write_requires_death_success=False,
            state_write_requires_hurt_success=False,source_object_preserved=True,full_offense_death_family_reviewed=False),
    }
    for key,fields in flags.items():
        for f,v in fields.items():assert rows[key][f]==v,(key,f)
    assert rows['incoming_admission']['admission_order']==note['admission_order']==ORDER
    assert rows['effect_admission']['exclusions']==['cataclysm:stun','cataclysm:abyssal_curse']
    assert rows['combat_persistence']['local_nbt_keys']==['Awaken']
    assert rows['pyramid_spawn_prerequisites']['native_marker']=='kobolediator'
    assert note['hierarchy']==[PKG+K,PKG+I,PKG+A,'net/minecraft/world/entity/monster/Monster']
    assert set(note['concrete_bindings'])==DEFENSE_NAMES
    for binding in note['concrete_bindings'].values():
        assert binding['applicable'] is False and binding['inherited'] is False and binding['native_value'] is None and binding['reason']
    assert note['installed_config']==dict(health_multiplier=1.0,attack_multiplier=1.0,constructor_applies_config_attribute_helper=True)
    def params(key,prim):return next(c['numerical_parameters'] for c in rows[key]['components'] if c['primitive']==prim)
    assert params('encounter_setup','NATIVE_ATTRIBUTE_SETUP')==dict(follow_range=30.0,movement_speed=f32(.28),
        attack_damage=14.0,max_health=180.0,armor=10.0,step_height=1.25,knockback_resistance=1.0,
        installed_health_multiplier=1.0,installed_attack_multiplier=1.0)
    assert params('encounter_setup','ENTITY_TYPE_SETUP')==dict(width=f32(2.4),height=f32(4.4))
    assert params('environment_admission','NATIVE_ENVIRONMENT_ADMISSION')==dict(rail_path_malus=0.0,water_path_malus=-1.0)
    assert params('projectile_block_response','PROJECTILE_MOTION')==dict(velocity_factor=1.5)
    assert params('projectile_block_response','PROJECTILE_FACING')==dict(yaw_base=170.0,yaw_span=80.0)
    assert params('projectile_block_response','RAW_ATTACK_STATE')==dict(block_state=9,recovery_max_ticks=18)
    assert params('awakening_prerequisites','AWAKEN_ADMISSION')==dict(target_distance_squared_limit=255.0,dormant_goal_priority=0)
    assert params('awakening_prerequisites','FORCED_MOVEMENT')==dict(horizontal_velocity=0.0)
    assert params('awakening_prerequisites','RAW_ATTACK_STATE')==dict(awakening_state=2,awakening_final_ticks=70,awakening_look_ticks=0)
    heal=next(c for c in rows['awakened_state']['components'] if c['primitive']=='HEAL_REQUEST')
    assert heal['parameter_formulas']==dict(requested_heal='current getMaxHealth()') and not heal['numerical_parameters']
    assert params('death_state_transition','RAW_ATTACK_STATE')==dict(death_state=8)
    assert params('death_state_transition','NATIVE_DEATH_DURATION')==dict(duration=60)


def validate_preservation(review, note, ledger):
    assert note['starting_sha']==START
    old=json.loads(at_start(REVIEW))
    assert len(old['effects'])==375 and len(old['paths'])==381
    assert [e for e in review['effects'] if e['review_checkpoint']!=CHECKPOINT]==old['effects']
    assert [p for p in review['paths'] if not p['id'].startswith('cataclysm:kobolediator-admission:')]==old['paths']
    mutable={'effects','paths','checkpoint','scope','notes_file','exact_next_task','protected_checkpoints'}
    assert {k:v for k,v in review.items() if k not in mutable}=={k:v for k,v in old.items() if k not in mutable}
    assert review['protected_checkpoints']==old['protected_checkpoints']+[dict(checkpoint=old['checkpoint'],notes_file=old['notes_file'])]
    prior=OUT/'cataclysm-r2k13b-ignited-berserker-offense.json'
    required={ref['file'] for ref in read_json(prior)['reference_files']}|{prior.relative_to(OUT).as_posix()}
    assert required<={ref['file'] for ref in note['reference_files']}
    for ref in note['reference_files']:
        path=OUT/ref['file']
        assert hashlib.sha256(path.read_bytes()).hexdigest()==ref['sha256'],ref['file']
        if ref['usage']=='LOCKED_REUSED':assert path.read_bytes()==at_start(path),ref['file']
        else:assert ref['usage']=='NEW_SCOPED' and path in [EVIDENCE_FILE,SPEC_FILE]
    lock=note['protected_r2k13b']
    assert lock['file']==prior.relative_to(OUT).as_posix() and note['previous_checkpoint']==old['checkpoint']
    assert hashlib.sha256(prior.read_bytes()).hexdigest()==lock['sha256']
    previous=json.loads(at_start(LEDGER))
    assert [t for t in ledger['targets'] if t['mod_key']!='cataclysm']==[t for t in previous['targets'] if t['mod_key']!='cataclysm']
    assert {k:v for k,v in ledger.items() if k not in ['targets','checkpoint']}=={k:v for k,v in previous.items() if k not in ['targets','checkpoint']}


def validate_native_boundaries(evidence):
    def witness(n):return next(w for w in evidence['witnesses'] if w['entry']==PKG+n+'.class')
    def body(n,m):return next(x['instructions'] for x in witness(n)['methods'] if x['name']==m)
    def at(ins,off):return next(i for i in ins if i['offset']==off)
    def calls(ins,name):return [i['offset'] for i in ins if name in str(i['operand'])]
    hurt=body(K,'hurt')
    assert calls(hurt,'.getDirectEntity(')==[1] and not calls(hurt,'.getEntity(')
    assert 'Poison_Dart_Entity' in at(hurt,6)['operand'] and at(hurt,9)['branch_target']==14
    assert at(hurt,12)['operand']==0 and at(hurt,13)['opcode']=='0xac'
    assert calls(hurt,'.canBlockDamageSource(')==[16] and at(hurt,19)['branch_target']==100
    assert at(hurt,23)['operand']=='net/minecraft/world/entity/projectile/AbstractArrow' and at(hurt,26)['branch_target']==76
    assert at(hurt,29)['operand']==170.0 and calls(hurt,'.nextFloat(')==[35] and at(hurt,40)['operand']==80.0
    assert at(hurt,42)['opcode']=='0x6a' and at(hurt,43)['opcode']=='0x62'
    assert calls(hurt,'.getDeltaMovement(')==[48] and at(hurt,51)['operand']==1.5
    assert calls(hurt,'.scale(')==[54] and calls(hurt,'.setDeltaMovement(')==[57]
    assert calls(hurt,'.getYRot(')==[62] and calls(hurt,'.setYRot(')==[68]
    assert at(hurt,67)['opcode']=='0x62' and '.hurtMarkedZ' in at(hurt,73)['operand']
    assert calls(hurt,'.getAttackState(')==[77] and at(hurt,80)['branch_target']==98
    assert at(hurt,84)['operand']==9 and calls(hurt,'.setAttackState(')==[86]
    assert at(hurt,98)['operand']==0 and at(hurt,99)['opcode']=='0xac'
    assert calls(hurt,'.isSleep(')==[101] and at(hurt,104)['branch_target']==119
    assert 'BYPASSES_INVULNERABILITY' in at(hurt,108)['operand'] and at(hurt,114)['branch_target']==119
    assert at(hurt,117)['operand']==0 and at(hurt,118)['opcode']=='0xac'
    assert [at(hurt,v)['opcode'] for v in [119,120,121,122,125]]==['0x2a','0x2b','0x24','0xb7','0xac']
    assert I+'.hurt(' in at(hurt,122)['operand']
    assert not any(calls(hurt,v) for v in ['.setOwner(','.deflect(','.yRot(','.addFreshEntity(','.heal(','.setAwaken(','DamageSource.<init>'])
    block=body(K,'canBlockDamageSource')
    assert calls(block,'.isNoAi(')==[3] and 'IS_PROJECTILE' in at(block,10)['operand']
    assert [at(block,v)['branch_target'] for v in [6,16,20,36,45]]==[106]*5
    assert at(block,27)['branch_target']==39 and at(block,34)['operand']==9
    assert calls(block,'.getSourcePosition(')==[40] and calls(block,'.getViewVector(')==[50]
    assert calls(block,'.vectorTo(')==[60] and calls(block,'.normalize(')==[63]
    assert at(block,77)['operand']==0.0 and calls(block,'.dot(')==[92]
    assert at(block,95)['operand']==0.0 and at(block,97)['opcode']=='0x9c' and at(block,97)['branch_target']==104
    assert not any(calls(block,v) for v in ['BYPASSES_','.getPierceLevel(','.isUsingItem(','.getAwaken(','.getEntity('])
    asleep=body(K,'isSleep')
    assert calls(asleep,'.getAwaken(')==[1] and at(asleep,4)['branch_target']==15
    assert at(asleep,11)['operand']==2 and at(asleep,12)['branch_target']==19
    sleep=body(K,'setSleep')
    assert at(sleep,5)['operand']==1 and at(sleep,9)['operand']==0 and calls(sleep,'.setAttackState(')==[10]
    assert not calls(sleep,'.setAwaken(') and not calls(sleep,'.heal(')
    seen=body(K,'canBeSeenAsEnemy')
    assert calls(seen,'.isSleep(')==[1] and I+'.canBeSeenAsEnemy(' in at(seen,8)['operand']
    define=body(K,'defineSynchedData')
    assert I+'.defineSynchedData(' in at(define,2)['operand'] and '.AWAKENL' in at(define,6)['operand'] and at(define,9)['operand']==0
    awaken=body(K,'setAwaken')
    assert at(awaken,1)['branch_target']==12 and calls(awaken,'.getMaxHealth(')==[6] and calls(awaken,'.heal(')==[9]
    assert calls(awaken,'SynchedEntityData.set(')==[23]
    assert [i['offset'] for i in awaken if 'branch_target' in i]==[1]
    assert not any(calls(awaken,v) for v in ['.getAwaken(','.setHealth(','.setAttackState(','.setHomePos('])
    use=body(D,'canUse')
    assert calls(use,'.getAwaken(')==[12] and at(use,15)['branch_target']==62
    assert calls(use,'.distanceToSqr(')==[34] and at(use,37)['operand']==255.0
    assert at(use,41)['opcode']=='0x9c' and at(use,41)['branch_target']==58
    assert calls(use,'.hasLineOfSight(')==[52] and at(use,55)['branch_target']==62
    tick=body(D,'tick')
    assert at(tick,4)['operand']==at(tick,15)['operand']==0.0 and at(tick,12)['operand']=='net/minecraft/world/phys/Vec3.yD'
    assert calls(tick,'.setDeltaMovement(')==[16]
    stop=body(D,'stop')
    assert at(stop,4)['operand']==1 and calls(stop,'.setAwaken(')==[5]
    assert at(stop,12)['operand']==2 and calls(stop,'.setAttackState(')==[13]
    assert not any('branch_target' in i for i in stop)
    assert body(D,'isInterruptable')[0]['operand']==0 and body(D,'requiresUpdateEveryTick')[0]['operand']==1
    assert [i['operand'].split('.')[-1] for i in body(D,'<init>') if 'Goal$Flag.' in str(i['operand'])]==[
        'MOVELnet/minecraft/world/entity/ai/goal/Goal$Flag;','JUMPLnet/minecraft/world/entity/ai/goal/Goal$Flag;',
        'LOOKLnet/minecraft/world/entity/ai/goal/Goal$Flag;']
    goals=body(K,'registerGoals')
    assert at(goals,276)['operand']==0 and calls(goals,D+'.<init>')==[282]
    assert [at(goals,v)['operand'] for v in [298,299,300,301,303]]==[2,2,0,70,0]
    assert [at(goals,v)['operand'] for v in [320,322,324,325,327,328]]==[9,9,0,18,0,0]
    for method,offset in [('addAdditionalSaveData',6),('readAdditionalSaveData',7)]:
        ins=body(K,method)
        assert I+'.'+method in at(ins,2)['operand'] and at(ins,offset)['operand']=='Awaken'
    assert calls(body(K,'addAdditionalSaveData'),'.putBoolean(')==[13]
    load=body(K,'readAdditionalSaveData')
    assert calls(load,'.getBoolean(')==[10] and calls(load,'.setAwaken(')==[13] and not calls(load,'.setSleep(')
    assert [i['opcode'] for i in body(K,'decreaseAirSupply')]==['0x1b','0xac']
    assert [i['opcode'] for i in body(A,'canBePushedByEntity')]==['0x4','0xac']
    for method in ['canRide','removeWhenFarAway','shouldDespawnInPeaceful']:
        assert [i['opcode'] for i in body(K,method)]==['0x3','0xac']
    die=body(K,'die')
    assert I+'.die(' in at(die,2)['operand'] and at(die,6)['operand']==8 and calls(die,'.setAttackState(')==[8]
    assert not any('branch_target' in i for i in die) and body(K,'deathtimer')[0]['operand']==60
    ctor=body(K,'<init>')
    assert at(ctor,117)['operand']==at(ctor,122)['operand']==0
    assert at(ctor,136)['operand']==0.0 and at(ctor,144)['operand']==-1.0
    assert 'Kobolediator.healthMultiplierD' in at(ctor,151)['operand'] and 'Kobolediator.attackMultiplierD' in at(ctor,154)['operand']
    assert calls(ctor,'.setConfigattribute(')==[157] and not calls(ctor,'.heal(')
    attrs=body(K,'kobolediator')
    assert [at(attrs,v)['operand'] for v in [6,15,24,33,42,51,60]]==[30.0,f32(.28),14.0,180.0,10.0,1.25,1.0]
    assert len(calls(attrs,'.add('))==7 and not calls(attrs,'ARMOR_TOUGHNESS')
    factory=body(REGISTRY,'lambda$static$81')
    assert at(factory,11)['operand']==f32(2.4) and at(factory,14)['operand']==f32(4.4)
    assert at(factory,25)['operand']=='cataclysm:kobolediator' and not calls(factory,'.fireImmune(')
    assert not any('.fireImmune(' in v for v in witness(REGISTRY)['factory_invocations'])
    reg=body(REGISTRY,'<clinit>')
    assert at(reg,1392)['operand']=='kobolediator' and '.KOBOLEDIATORL' in at(reg,1403)['operand']
    bs={b['index']:b for b in witness(REGISTRY)['registration_bootstraps']}
    assert set(bs)=={32,195} and any(PKG+K+'.<init>' in a for a in bs[32]['arguments'])
    assert any('ModEntities.lambda$static$81' in a for a in bs[195]['arguments'])
    assert witness(REGISTRY)['kobolediator_spawn_placement_bindings']==[]
    spawn=body(K,'finalizeSpawn')
    assert at(spawn,1)['operand']==1 and calls(spawn,'.setSleep(')==[2]
    assert [at(spawn,v)['opcode'] for v in [5,6,7,8,9,11,14]]==['0x2a','0x2b','0x2c','0x2d','0x19','0xb7','0xb0']
    assert I+'.finalizeSpawn(' in at(spawn,11)['operand']
    marker=body(PYRAMID,'handleDataMarker')
    assert at(marker,134)['operand']=='kobolediator' and at(marker,142)['operand']==4
    assert '.KOBOLEDIATORL' in at(marker,458)['operand'] and calls(marker,'.create(')==[473]
    assert at(marker,483)['branch_target']==553
    assert calls(marker,'.setPersistenceRequired(')==[488] and calls(marker,'.moveTo(')==[496]
    assert at(marker,501)['operand']==1 and calls(marker,'.setSleep(')==[502]
    assert 'MobSpawnType.STRUCTURE' in at(marker,519)['operand'] and at(marker,522)['opcode']=='0x1'
    assert calls(marker,'.finalizeSpawn(')==[526] and at(marker,529)['opcode']=='0x57'
    assert calls(marker,'.addFreshEntityWithPassengers(')==[533]
    assert 'Blocks.AIR' in at(marker,540)['operand'] and at(marker,546)['operand']==2 and calls(marker,'.setBlock(')==[547]
    assert not any(calls(marker,v) for v in ['.setAwaken(','.setHomePos(','.setTarget(','.isIgnisDefeatedOnce(','.isInside('])


def validate_evidence(review, note, jar_path=None):
    assert read_json(SPEC_FILE)==specification()
    evidence=read_json(EVIDENCE_FILE)
    assert len(evidence['witnesses'])==5
    assert {w['entry'] for w in evidence['witnesses']}=={PKG+n+'.class' for n in METHODS}
    if jar_path is not None:
        reproduced=collect(jar_path)
        assert evidence==reproduced,'New witnesses failed pinned-JAR reproduction'
        assert EVIDENCE_FILE.read_bytes()==(json.dumps(reproduced,ensure_ascii=False,indent=2)+'\n').encode()
    census={c['entry']:c for c in read_json(OUT/'cataclysm-source-census.json')['classes']}
    new_methods={(w['entry'],m['name'],m['descriptor']):m for w in evidence['witnesses'] for m in w['methods']}
    assert len(new_methods)==31
    sources={ref['file']:read_json(OUT/ref['file']) for ref in note['reference_files'] if ref['file'].startswith('native-evidence/')}
    for file,data in sources.items():
        if file==EVIDENCE_FILE.relative_to(OUT).as_posix():continue
        for w in data['witnesses']:
            for old in w.get('methods',[]):
                new=new_methods.get((w['entry'],old['name'],old['descriptor']))
                if new is not None:
                    assert 'instruction_offset_ranges' in new,'Old method recaptured'
                    assert new['code_sha256']==old['code_sha256']
                    assert not {i['offset'] for i in new['instructions']} & {i['offset'] for i in old['instructions']},'Old fragment recaptured'
    for w in evidence['witnesses']:
        assert w['jar_sha256']==note['tooling']['jar_sha256']
        assert w['entry_sha256']==census[w['entry']]['entry_sha256'] and w['superclass']==census[w['entry']]['superclass']
        n=w['entry'][len(PKG):-6]
        assert {m['name'] for m in w['methods']}==set(METHODS[n])|set(FRAGMENTS.get(n,{}))
        for m in w['methods']:
            if 'instruction_offset_ranges' in m:assert m['instruction_offset_ranges']==FRAGMENTS[n][m['name']]
            assert not any('playSound' in str(i['operand']) or 'addParticle' in str(i['operand']) for i in m['instructions'])
    for e in selected(review):
        for p in e['implementation']:
            w=next(w for w in sources[p['evidence_file']]['witnesses'] if w['id']==p['witness_id'])
            assert p['entry']==w['entry'] and set(p['methods'])<={m['name'] for m in w.get('methods',[])}
        for p in e.get('reference_evidence',[]):
            assert p['evidence_file']==NATIVE_REF
            w=next(w for w in read_json(OUT/p['evidence_file'])['witnesses'] if w['entry']==p['entry'])
            assert set(p['methods'])<={m['name'] for m in w['methods']}
    root=next(w for w in evidence['witnesses'] if w['entry']==PKG+K+'.class')
    parents=read_json(OUT/'native-evidence/cataclysm-remnant-admission.json')['witnesses']
    chain=[root['class_name']]
    absent=DEFENSE_NAMES|{'isInvulnerableTo','ReturnToHome','setHomePos','getHomePos','mobInteract','PlayerCounter',
        'isPushedByFluid','checkSpawnRules','causeFallDamage'}
    for name in [K,I,A]:
        w=root if name==K else next(w for w in parents if w['entry']==PKG+name+'.class')
        chain.append(w['superclass'])
        assert not absent & set(w['declared_method_names'])
        assert ('canBePushedByEntity' in w['declared_method_names'])==(name==A)
        if name!=K:assert not {'hurt','addAdditionalSaveData','readAdditionalSaveData','canBeAffected','finalizeSpawn'} & set(w['declared_method_names'])
    assert chain==note['hierarchy']
    assert not {'tick','aiStep','AreaAttack','StompDamage','spawnBlocks','ChargeBlockBreaking','isAlliedTo',
        'canBeAffected','getAnimationState','onSyncedDataUpdated','stopAllAnimationStates'} & {m['name'] for m in root['methods']}
    assert note['tooling']['new_native_witnesses']==5 and note['tooling']['new_method_witnesses']==31
    assert note['tooling']['new_resource_witnesses']==0
    assert not note['tooling']['reused_evidence_regenerated'] and not note['tooling']['recursive_jar_scan']
    config=read_json(OUT/'cataclysm-installed-common-config.json')['values']['mobs']['kobolediator']['combat_config']
    assert config['health_multiplier']==config['attack_multiplier']==1.0
    validate_native_boundaries(evidence)
    return len(new_methods)


def validate(jar_path=None):
    review,note,ledger=[read_json(p) for p in [REVIEW,NOTE,LEDGER]]
    summary=validate_records(review,note,ledger)
    validate_preservation(review,note,ledger)
    methods=validate_evidence(review,note,jar_path)
    for path in [REVIEW,NOTE,LEDGER,SPEC_FILE,EVIDENCE_FILE]:
        assert path.read_text(encoding='utf-8')==json.dumps(read_json(path),ensure_ascii=False,indent=2)+'\n'
    return dict(status='PASS',**summary,new_method_witnesses=methods,
        protected_shared_status_prior_families_berserker='BYTE_IDENTICAL',
        pinned_jar_reproduction='PASS' if jar_path else 'NOT_REQUESTED')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jar',type=Path,help='Reproduce only new witnesses against the exact pinned JAR')
    print(json.dumps(validate(parser.parse_args().jar),indent=2))
