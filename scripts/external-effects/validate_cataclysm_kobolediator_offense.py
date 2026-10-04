"""Focused R2k14b records, native boundaries, protected facts and reproduction."""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import subprocess

from catalog_common import OUT, ROOT, read_json
from collect_cataclysm_kobolediator_offense import (
    K, PKG, METHODS, FRAGMENTS, EVIDENCE_FILE, SPEC_FILE, collect, specification,
)
from validate_cataclysm_kobolediator_admission import f32

START='5c3caf0ebfa83a86ebfbdbd2830a41dba9e7e526'
CHECKPOINT='R2k14b-cataclysm-kobolediator-offense-complete'
NOTE=OUT/'cataclysm-r2k14b-kobolediator-offense.json'
REVIEW=OUT/'mod-reviews/cataclysm.json'
LEDGER=OUT/'mod-completion-ledger.json'
PRIOR=OUT/'cataclysm-r2k14a-kobolediator-admission.json'
KEYS={'attack_selection','sequence_state','pursuit_goal','area_geometry','area_damage','shield_disable',
      'stomp_sampling','stomp_damage','stomp_pull','stomp_debris','charge_motion','charge_damage','charge_push',
      'charge_terrain','charge_debris','alliance','payload_lifecycle_closure','defeat_lifecycle'}
KINDS={'VANILLA_DIRECT','VANILLA_EQUIVALENT','VANILLA_LIKE_EXTENDED','VANILLA_COMPOSITE',
       'CUSTOM_DAMAGE','CUSTOM_STATUS','CUSTOM_CONTROL','CUSTOM_RESOURCE','BINARY_MECHANIC'}
NO_CANDIDATES=KEYS-{'area_damage','shield_disable','stomp_damage','stomp_pull','charge_motion','charge_damage','charge_push'}


def at_start(path):
    return subprocess.check_output(['git','show',START+':'+Path(path).relative_to(ROOT).as_posix()],cwd=ROOT)


def selected(review):
    return [e for e in review['effects'] if e['review_checkpoint']==CHECKPOINT]


def validate_records(review,note,ledger):
    effects,paths=review['effects'],review['paths']
    assert len(effects)==len({e['id'] for e in effects}) and len(paths)==len({p['id'] for p in paths})
    assert effects==sorted(effects,key=lambda e:e['id']) and paths==sorted(paths,key=lambda p:p['id'])
    new=selected(review)
    assert {e['id'] for e in new}=={'cataclysm:kobolediator_'+k for k in KEYS}
    pids,eids={p['id'] for p in paths},{e['id'] for e in effects}
    for e in new:
        assert e['mod_key']=='cataclysm' and e['primary_classification'] in KINDS
        assert e['inspection_status']=='STATIC_REVIEWED' and not e['unresolved_ambiguities']
        for k in ['actual_behavior','source_actor','primary_test_source','components','implementation',
                  'delivery_paths','closest_vanilla_equivalent','hurt_return_dependency','binary_parameters']:
            # Binary closure records do not invent a scalar component.
            assert e[k] or (k=='components' and e['primary_classification']=='BINARY_MECHANIC'),(e['id'],k)
        assert not {'stage_scaling_needed','stage_policy','stage_multiplier','stage_eligibility',
                    'stage_cap','stage_floor','runtime_hook'} & e.keys()
        assert set(e['delivery_paths'])<=pids
        observations=[]
        for c in e['components']:
            assert c['primitive'] and c['formula'] and c['native_boundary'] and c['vanilla_relation']
            assert set(c['numerical_parameters'])==set(c['parameter_units'])
            for p,v in c['numerical_parameters'].items():
                assert isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v)
                observations.append(dict(primitive=c['primitive'],parameter=p,native_value=v,native_formula=c['formula'],
                    units=c['parameter_units'][p],boundary=c['native_boundary']))
            assert set(c.get('parameter_formulas',{}))==set(c.get('formula_parameter_units',{}))
            for p,v in c.get('parameter_formulas',{}).items():
                assert p not in c['numerical_parameters'] and v
                observations.append(dict(primitive=c['primitive'],parameter=p,native_value=None,native_formula=v,
                    units=c['formula_parameter_units'][p],boundary=c['native_boundary']))
        assert observations==e['numeric_observations']
        candidates=e['scalable_parameter_candidates'];seen=set()
        assert candidates==sorted(candidates,key=lambda c:(c['primitive'],c['parameters']))
        for c in candidates:
            assert len(c['parameters'])==1
            p=c['parameters'][0];key=(c['primitive'],p)
            assert key not in seen;seen.add(key)
            owners=[o for o in observations if (o['primitive'],o['parameter'])==key]
            assert len(owners)==1,'Candidate lost native primitive ownership'
            o=owners[0]
            assert c['native_value']==o['native_value'] and c['native_formula']==o['native_formula']
            assert c['units']==o['units'] and c['native_boundary']==o['boundary']
        if e['id'].removeprefix('cataclysm:kobolediator_') in NO_CANDIDATES:
            assert not candidates,'State/gates/uncalled helpers are not active scalar candidates'
        assert e['spawned_entity_ids']==(['cataclysm:cm_falling_block'] if e['id'].removeprefix('cataclysm:kobolediator_') in ['stomp_debris','charge_debris'] else [])
    new_paths=[p for p in paths if p['id'].startswith('cataclysm:kobolediator-offense:')]
    assert len(new_paths)==18
    for p in new_paths:
        assert p['mod_key']=='cataclysm' and p['status']=='VERIFIED' and p['runtime_status']=='NOT_RUN'
        assert p['primary_source'] and p['native_path'] and p['setup'] and p['implementation'] and p['labels']
        assert p['effect_ids'] and set(p['effect_ids'])<=eids
        for e in new:assert (p['id'] in e['delivery_paths'])==(e['id'] in p['effect_ids'])
    assert note['mechanic_packages']==[dict(id=e['id'],primary_classification=e['primary_classification'],delivery_paths=e['delivery_paths'],
        numerical_candidates=e['scalable_parameter_candidates'],binary_gates=e['binary_parameters']) for e in new]
    assert note['facts']=={e['id'].removeprefix('cataclysm:kobolediator_'):e['actual_behavior'] for e in new}
    summary=dict(new_mechanics=len(new),delivery_paths=len(new_paths),classifications=dict(sorted(Counter(e['primary_classification'] for e in new).items())),
        candidate_numeric_parameters=sum(len(c['parameters']) for e in new for c in e['scalable_parameter_candidates']),
        new_owned_payload_classes=0,reused_owned_payload_classes=1,unresolved_subsection_ambiguities=0)
    assert summary==note['summary']
    assert summary['classifications']=={'BINARY_MECHANIC':9,'CUSTOM_CONTROL':3,'VANILLA_LIKE_EXTENDED':6}
    assert summary['candidate_numeric_parameters']==10
    assert review['status']==ledger['status']==note['status']=='PARTIAL'
    assert all(review[k] is False for k in ['semantic_discovery_complete','special_damage_discovery_complete','source_mapping_complete','delivery_mapping_complete'])
    cat=next(t for t in ledger['targets'] if t['mod_key']=='cataclysm')
    assert cat['state']=='PARTIAL' and cat['semantic_effect_count']==len(effects)
    assert review['checkpoint']==ledger['checkpoint']==note['checkpoint']==CHECKPOINT
    assert review['exact_next_task']==note['exact_next_task']==cat['exact_next_task']
    assert note['exact_next_task'].startswith('R2k15a: Wadjet incoming admission and combat-state/encounter prerequisites.')
    assert note['kobolediator_fully_closed'] and not note['remaining_kobolediator_work']
    assert not note['remaining_subsection_native_ambiguities'] and note['remaining_cataclysm_research']
    assert note['runtime_tests']==0
    assert all(note[k] is False for k in ['whole_mod_complete','stage_eligibility_decided','phase6_reopened','production_changed',
        'stage_changed','boss_testing_started','l2_testing_started','compatibility_fixes_started','phase7_started'])
    validate_contracts({e['id'].removeprefix('cataclysm:kobolediator_'):e for e in new},note)
    return summary



def validate_contracts(rows,note):
    flags={
        'attack_selection':dict(rng_before_cooldown=True,selection_has_hp_gate=False,
            concrete_selection_has_los_gate=False,selection_probabilities_are_stage_candidates=False),
        'sequence_state':dict(cooldown_written_on_stop=True,cooldown_decrements_both_sides=True,
            local_noai_decrement_guard=False,state_start_restarts_matching_state=False,
            charge_end_range_goal_required_state=6,state7_tick5_guaranteed_on_recovery=False,attack_state_is_stage=False),
        'pursuit_goal':dict(pursuit_calls_hurt=False,ordinary_melee_goal_registered=False,charge_tick_calls_super=False),
        'area_geometry':dict(query_before_server_guard=True,wrap_branches_repeat_horizontal_range=False,caller_requires_current_target=False),
        'area_damage':dict(damage_type='minecraft:mob_attack',hurt_return_used=False,excludes_all_kobolediators=True,
            post_hurt_motion=False,applies_status=False,heals_self=False,invulnerability_reset=False),
        'shield_disable':dict(requires_hurt_success=False,blocked_rechecked_after_hurt=True,
            uses_actual_use_item=True,stomp_positive_shield_duration=False),
        'stomp_sampling':dict(duplicate_distance5_preserved=True,hitset_added=False,air_fallback_cancels_damage=False,
            render_scan_repositions_damage_sample=False,server_guard_at_stomp=True),
        'stomp_damage':dict(damage_type='minecraft:mob_attack',hurt_return_used=True,helper_has_local_server_guard=False,
            debris_is_damage_source=False,damage_requires_debris_add_success=False,damage_requires_found_support=False,hitset_added=False),
        'stomp_pull':dict(control_depends_on_hurt=True,uses_native_knockback=False,absolute_velocity_write=False,
            reads_knockback_resistance=False,factor_clamped=False),
        'stomp_debris':dict(debris_calls_hurt=False,debris_places_blocks=False,debris_has_damage_owner=False,debris_add_return_gates_damage=False),
        'charge_motion':dict(preserves_vertical_velocity=True,uses_body_yaw=False,uses_target_vector=False,
            local_server_guard=False,uses_native_knockback=False,charge_tick_calls_super=False),
        'charge_damage':dict(damage_type='minecraft:mob_attack',uses_global_tick_count=True,hurt_return_used=True,
            damage_requires_terrain_success=False,damage_requires_grounded_victim=False,current_target_required=False,applies_status=False,heals_self=False),
        'charge_push':dict(control_depends_on_hurt=True,requires_grounded_victim=True,
            uses_native_knockback=False,absolute_velocity_write=False,reads_knockback_resistance=False),
        'charge_terrain':dict(installed_ignore_mob_griefing=False,ignore_setting_or_native_grief=True,
            uses_per_block_destroy_event=True,break_has_local_server_guard=False,destruction_requires_hurt=False,
            destroy_result_gates_debris=False,destroy_result_gates_contact_damage=False,terrain_calls_hurt=False),
        'charge_debris':dict(debris_calls_hurt=False,debris_places_blocks=False,debris_has_damage_owner=False,
            spawn_requires_destroy_success=False,vertical_motion_multiplies_displacement=True),
        'alliance':dict(native_team_tag='cataclysm:team_ancient_remnant',tag_requires_both_teams_null=True,explicit_same_type_exclusion=True),
        'payload_lifecycle_closure':dict(new_owned_payload_classes=0,reused_owned_payload_classes=1,concrete_explosion=False,
            concrete_status_or_heal_payload=False,concrete_grab_or_mount=False,concrete_custom_damage_type=False,global_callbacks_absent_claimed=False),
        'defeat_lifecycle':dict(concrete_respawner_link=False,concrete_death_payload=False,global_callbacks_absent_claimed=False),
    }
    for key,fields in flags.items():
        for f,v in fields.items():assert rows[key][f]==v,(key,f)
    def params(key,prim):return next(c['numerical_parameters'] for c in rows[key]['components'] if c['primitive']==prim)
    assert params('sequence_state','ATTACK_COOLDOWN_STATE')==dict(earthquake_cooldown=80,charge_cooldown=160,decrement=1)
    assert params('attack_selection','GOAL_ADMISSION')==dict(rng_scale=100.0,earthquake_threshold=16.0,charge_threshold=9.0,
        earthquake_range=12.0,combo_range=8.0,charge_start_range=15.0,charge_end_range=5.0)
    assert params('shield_disable','ITEM_COOLDOWN')==dict(duration=120)
    assert params('stomp_pull','FORCED_MOVEMENT')==dict(horizontal_magnitude=-4.0,ground_vertical_increment=.15,distance_divisor=12.0)
    assert params('charge_motion','FORCED_MOVEMENT')==dict(forward_contribution=.7,previous_horizontal_factor=.5)
    assert params('charge_push','FORCED_MOVEMENT')==dict(horizontal_factor=1.5,vertical_increment=.5,native_denominator_floor=.001)
    assert params('charge_damage','ATTACK_CADENCE')==dict(interval=4)
    assert params('charge_damage','ATTACK_VOLUME')==dict(inflate=.5)
    assert params('stomp_debris','DEBRIS_DELIVERY')==dict(life=10,vertical_base=.2,vertical_gaussian_factor=.04)
    assert params('charge_debris','DEBRIS_DELIVERY')==dict(life=20,horizontal_random_base=-1.2,horizontal_divisor=3.0,vertical_base=.2,vertical_gaussian_factor=.15)
    assert rows['sequence_state']['goal_bindings']==note['goal_bindings']
    assert [(b['priority'],b['required_state'],b['active_state'],b['end_state'],b['max_ticks'],b['look_ticks'],b['range']) for b in note['goal_bindings']]==[
        (2,0,3,0,50,15,12.0),(2,0,4,0,100,64,8.0),(2,0,5,6,40,30,15.0),
        (1,6,6,7,30,0,None),(2,6,7,0,40,40,5.0),(1,7,7,0,40,40,None)]
    expected_area=[dict(attack_state=s,attack_tick=t,range=f32(r),height=f32(6),arc_degrees=f32(a),damage_multiplier=f32(d),shield_disable_ticks=b)
        for s,t,r,a,d,b in [(3,20,10,60,1,120),(4,18,9,270,1,0),(4,36,9,270,1,0),(4,65,10,45,1.25,120),(7,5,9,200,1.25,120)]]
    assert rows['area_geometry']['area_call_parameters']==note['area_call_parameters']==expected_area
    expected_stomp=[dict(attack_state=3,attack_tick=t,distance=d,spread_arc=f32(.25),height=5,max_y=f32(1.05),
        forward_offset=f32(2),side_offset=f32(-.2),shield_disable_ticks=0,damage_multiplier=f32(1))
        for t,distances in [(19,[2,3]),(21,[4,5]),(23,[5,6]),(25,[7,8]),(27,[9,10])] for d in distances]
    assert rows['stomp_sampling']['stomp_call_parameters']==note['stomp_call_parameters']==expected_stomp
    candidate_sets={
        'area_damage':{('NATIVE_DAMAGE_REQUEST','requested_damage')},
        'shield_disable':{('ITEM_COOLDOWN','duration')},
        'stomp_damage':{('NATIVE_DAMAGE_REQUEST','requested_damage')},
        'stomp_pull':{('FORCED_MOVEMENT','horizontal_magnitude'),('FORCED_MOVEMENT','ground_vertical_increment')},
        'charge_motion':{('FORCED_MOVEMENT','forward_contribution'),('FORCED_MOVEMENT','previous_horizontal_factor')},
        'charge_damage':{('NATIVE_DAMAGE_REQUEST','requested_damage')},
        'charge_push':{('FORCED_MOVEMENT','horizontal_factor'),('FORCED_MOVEMENT','vertical_increment')},
    }
    for key in KEYS:
        assert {(c['primitive'],c['parameters'][0]) for c in rows[key]['scalable_parameter_candidates']}==candidate_sets.get(key,set())
    for key in ['area_damage','stomp_damage','charge_damage']:
        assert rows[key]['scalable_parameter_candidates'][0]['native_value'] is None
    assert rows['charge_damage']['scalable_parameter_candidates'][0]['native_formula']=='float(configured ATTACK_DAMAGE) * .4F'


def validate_preservation(review,note,ledger):
    assert note['starting_sha']==START
    old=json.loads(at_start(REVIEW));previous=json.loads(at_start(LEDGER))
    assert len(old['effects'])==390 and len(old['paths'])==396
    assert [e for e in review['effects'] if e['review_checkpoint']!=CHECKPOINT]==old['effects']
    assert [p for p in review['paths'] if not p['id'].startswith('cataclysm:kobolediator-offense:')]==old['paths']
    mutable={'effects','paths','checkpoint','scope','notes_file','exact_next_task','protected_checkpoints'}
    assert {k:v for k,v in review.items() if k not in mutable}=={k:v for k,v in old.items() if k not in mutable}
    assert review['protected_checkpoints']==old['protected_checkpoints']+[dict(checkpoint=old['checkpoint'],notes_file=old['notes_file'])]
    required={r['file'] for r in read_json(PRIOR)['reference_files']}|{PRIOR.relative_to(OUT).as_posix()}
    assert required<={r['file'] for r in note['reference_files']}
    for ref in note['reference_files']:
        path=OUT/ref['file'];assert hashlib.sha256(path.read_bytes()).hexdigest()==ref['sha256'],ref['file']
        if ref['usage']=='LOCKED_REUSED':assert path.read_bytes()==at_start(path),ref['file']
        else:assert ref['usage']=='NEW_SCOPED' and path in [EVIDENCE_FILE,SPEC_FILE]
    assert note['protected_r2k14a']==dict(file=PRIOR.relative_to(OUT).as_posix(),sha256=hashlib.sha256(PRIOR.read_bytes()).hexdigest())
    assert note['previous_checkpoint']==old['checkpoint']
    assert [t for t in ledger['targets'] if t['mod_key']!='cataclysm']==[t for t in previous['targets'] if t['mod_key']!='cataclysm']
    assert {k:v for k,v in ledger.items() if k not in ['targets','checkpoint']}=={k:v for k,v in previous.items() if k not in ['targets','checkpoint']}




def validate_native_boundaries(evidence,note):
    def body(n,m):return next(meth['instructions'] for w in evidence['witnesses'] if w['entry']==PKG+n+'.class' for meth in w['methods'] if meth['name']==m)
    def at(ins,off):return next(i for i in ins if i['offset']==off)
    def calls(ins,term):return [i['offset'] for i in ins if i['opcode'] in ['0xb6','0xb7','0xb8','0xb9'] and term in str(i['operand'])]
    tick=body(K,'tick');ai=body(K,'aiStep');reg=body(K,'registerGoals')
    assert calls(tick,'.tick(')==[1] and at(tick,58)['branch_target']==71 and at(tick,75)['branch_target']==88
    assert at(tick,66)['operand']==at(tick,83)['operand']==1
    assert 'earthquake_cooldownI' in at(tick,68)['operand'] and 'charge_cooldownI' in at(tick,85)['operand']
    assert not calls(tick,'.isNoAi(') and not calls(tick,'.isClientSide(')
    # Every concrete binding is captured; protected dormant/awakening/block bindings are not recaptured.
    for offsets,values in [([125,126,127,128,130,132],[0,3,0,50,15,12.0]),
                          ([150,151,152,153,155,157],[0,4,0,100,64,8.0]),
                          ([176,177,178,180,182,184],[0,5,6,40,30,15.0]),
                          ([203,205,207,209,211],[6,6,7,30,0]),
                          ([229,231,233,234,236,238],[6,7,0,40,40,5.0]),
                          ([257,259,261,262,264],[7,7,0,40,40])]:
        assert [at(reg,o)['operand'] for o in offsets]==values
    assert calls(reg,'InternalMoveGoal.<init>')==[108] and at(reg,100)['operand']==3
    assert at(reg,106)['operand']==0 and at(reg,107)['operand']==1.0
    for index,threshold in [(1,16.0),(2,9.0)]:
        use=body(K+'$'+str(index),'canUse')
        assert calls(use,'InternalAttackGoal.canUse(')==[1] and at(use,4)['branch_target']==42
        assert calls(use,'.nextFloat(')==[14] and at(use,19)['operand']==100.0 and at(use,22)['operand']==threshold
        assert at(use,25)['opcode']=='0x9c' and at(use,25)['branch_target']==42
        assert at(use,35)['opcode']=='0x9d' and at(use,35)['branch_target']==42
    for index,cooldown,field in [(1,80,'earthquake_cooldownI'),(4,160,'charge_cooldownI'),(5,160,'charge_cooldownI')]:
        stop=body(K+'$'+str(index),'stop')
        assert '.stop()V' in at(stop,1)['operand'] and at(stop,8)['operand']==cooldown
        assert field in next(i['operand'] for i in stop if i['opcode']=='0xb5' and field in str(i['operand']))
        assert not any('branch_target' in i for i in stop)
    # Exact scheduled calls, including two native distance5 samples on different ticks.
    assert calls(ai,'.AreaAttack(')==[70,414,472,533,850]
    for offsets,event in zip([[58,61,64,67,68],[403,406,409,412,413],[461,464,467,470,471],
                              [519,522,525,528,531],[836,839,842,845,848]],note['area_call_parameters']):
        assert [at(ai,o)['operand'] for o in offsets]==[event[k] for k in ['range','height','arc_degrees','damage_multiplier','shield_disable_ticks']]
    assert [at(ai,o)['operand'] for o in [52,397,455,513,831]]==[20,18,36,65,5]
    stomp_offsets=[129,147,184,202,239,258,296,315,353,372]
    assert calls(ai,'.StompDamage(')==stomp_offsets
    for call,event in zip(stomp_offsets,note['stomp_call_parameters']):
        pos=next(j for j,i in enumerate(ai) if i['offset']==call)
        assert [i['operand'] for i in ai[pos-8:pos]]==[event[k] for k in ['spread_arc','distance','height','max_y','forward_offset','side_offset','shield_disable_ticks','damage_multiplier']]
    assert at(ai,587)['operand']==6 and at(ai,599)['branch_target']==818
    assert 'ignoreMobGriefingZ' in at(ai,602)['operand'] and at(ai,605)['branch_target']==615
    assert calls(ai,'.canEntityGrief(')==[620] and calls(ai,'.ChargeBlockBreaking(')==[609,627]
    assert at(ai,623)['branch_target']==630 and at(ai,612)['branch_target']==630
    assert 'tickCountI' in at(ai,631)['operand'] and at(ai,634)['operand']==4
    assert calls(ai,'.mobAttack(')==[644] and at(ai,643)['opcode']=='0x2a'
    assert at(ai,659)['operand']==.5 and calls(ai,'.getEntitiesOfClass(')==[665]
    assert at(ai,722)['opcode']=='0x90' and at(ai,723)['operand']==f32(.4) and at(ai,726)['opcode']=='0x6a'
    assert calls(ai,'.hurt(')==[727] and at(ai,734)['branch_target']==815
    assert calls(ai,'.onGround(')==[738] and at(ai,741)['branch_target']==815
    assert at(ai,777)['operand']==.001 and at(ai,785)['operand']==1.5 and at(ai,800)['operand']==.5
    assert calls(ai,'.push(')==[812]
    area=body(K,'AreaAttack')
    assert calls(area,'.getEntityLivingBaseNearby(')==[9] and calls(area,'.mobAttack(')==[19]
    assert at(area,31)['branch_target']==334
    assert [at(area,o)['branch_target'] for o in [203,212,222,235,248]]==[225,225,251,251,331]
    assert at(area,262)['operand']==PKG+K and at(area,265)['branch_target']==331
    assert calls(area,'.hurt(')==[290] and at(area,293)['opcode']=='0x57'
    assert [at(area,o)['opcode'] for o in [285,287,288,289]]==['0x17','0x8d','0x6b','0x90']
    assert calls(area,'.isDamageSourceBlocked(')==[298] and calls(area,'.disableShield(')==[328]
    assert at(area,321)['branch_target']==331
    wave=body(K,'StompDamage')
    assert calls(wave,'Mth.ceil(')==[111] and at(wave,119)['operand']==12.0
    assert at(wave,248)['operand']==30 and at(wave,326)['branch_target']==367
    assert calls(wave,'.spawnBlocks(')==[364]
    spawn=body(K,'spawnBlocks')
    assert calls(spawn,'.mobAttack(')==[5] and calls(spawn,'.isFaceSturdy(')==[54]
    assert calls(spawn,'Mth.floor(')==[132] and at(spawn,137)['branch_target']==25
    assert at(spawn,175)['operand']==10 and calls(spawn,'.nextGaussian(')==[192]
    assert at(spawn,185)['operand']==.2 and at(spawn,197)['operand']==.04
    assert calls(spawn,'.addFreshEntity(')==[212] and at(spawn,215)['opcode']=='0x57'
    assert calls(spawn,'.getEntitiesOfClass(')==[282] and calls(spawn,'.hurt(')==[367]
    assert [at(spawn,o)['opcode'] for o in [362,364,365,366]]==['0x17','0x8d','0x6b','0x90']
    assert calls(spawn,'.isDamageSourceBlocked(')==[376] and calls(spawn,'.disableShield(')==[406]
    assert at(spawn,411)['branch_target']==481 and at(spawn,414)['operand']==-4.0
    assert at(spawn,440)['operand']==.15 and at(spawn,446)['operand']==0.0
    assert calls(spawn,'.add(')==[475] and calls(spawn,'.setDeltaMovement(')==[478]
    assert not calls(spawn,'.destroyBlock(') and not calls(spawn,'.isClientSide(')
    motion=body(K+'$3','tick')
    assert calls(motion,'.onGround(')==[4] and at(motion,7)['branch_target']==99
    assert calls(motion,'.getYRot(')==[22] and at(motion,57)['operand']==.7 and at(motion,64)['operand']==.5
    assert at(motion,89)['operand']=='net/minecraft/world/phys/Vec3.yD' and calls(motion,'.setDeltaMovement(')==[96]
    assert not calls(motion,'.tick(') and not calls(motion,'.getTarget(')
    terrain=body(K,'ChargeBlockBreaking')
    assert [at(terrain,o)['operand'] for o in [6,9,12]]==[.5,.2,.5]
    assert calls(terrain,'.canEntityDestroy(')==[118] and 'REMNANT_IMMUNE' in at(terrain,126)['operand']
    assert calls(terrain,'.onEntityDestroyBlock(')==[140]
    assert [at(terrain,o)['branch_target'] for o in [106,121,132,143]]==[355]*4
    assert at(terrain,150)['operand']==6 and calls(terrain,'.nextInt(')==[152] and calls(terrain,'.hasBlockEntity(')==[162]
    assert at(terrain,208)['operand']==20 and calls(terrain,'.destroyBlock(')==[223,339]
    assert calls(terrain,'.addFreshEntity(')==[324]
    assert at(terrain,258)['operand']==at(terrain,292)['operand']==-1.2
    assert at(terrain,271)['operand']==at(terrain,305)['operand']==3.0
    assert at(terrain,275)['operand']==.2 and at(terrain,287)['operand']==.15
    assert calls(terrain,'.multiply(')==[309] and calls(terrain,'.setDeltaMovement(')==[315]
    # Destroy false can still flow to native debris motion/add, not a success gate.
    assert at(terrain,226)['branch_target']==233 and at(terrain,230)['branch_target']==237
    assert at(terrain,237)['operand']==0 and at(terrain,238)['opcode']=='0x3c'
    assert not calls(terrain,'.hurt(') and not calls(terrain,'.isClientSide(')
    allies=body(K,'isAlliedTo')
    assert 'TEAM_ANCIENT_REMNANT' in at(allies,21)['operand']
    assert calls(allies,'.getTeam(')==[31,38] and at(allies,34)['branch_target']==48 and at(allies,41)['branch_target']==48
    for ins in [ai,area,spawn,terrain,motion]:
        assert not any(calls(ins,v) for v in ['.addEffect(','.heal(','.igniteForSeconds(','.knockback(','.explode(','.setOwner('])


def validate_evidence(review,note,jar_path=None):
    assert read_json(SPEC_FILE)==specification()
    evidence=read_json(EVIDENCE_FILE)
    assert len(evidence['witnesses'])==6
    assert {w['entry'] for w in evidence['witnesses']}=={PKG+n+'.class' for n in METHODS}
    if jar_path is not None:
        reproduced=collect(jar_path)
        assert evidence==reproduced,'New witnesses failed pinned-JAR reproduction'
        assert EVIDENCE_FILE.read_bytes()==(json.dumps(reproduced,ensure_ascii=False,indent=2)+'\n').encode()
    census={c['entry']:c for c in read_json(OUT/'cataclysm-source-census.json')['classes']}
    new_methods={(w['entry'],m['name'],m['descriptor']):m for w in evidence['witnesses'] for m in w['methods']}
    assert len(new_methods)==19
    sources={r['file']:read_json(OUT/r['file']) for r in note['reference_files'] if r['file'].startswith('native-evidence/')}
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
            assert not any(v in str(i['operand']) for i in m['instructions'] for v in ['playSound','ScreenShake','Makeparticle','Stompsound','animateWhen'])
    for e in selected(review):
        for p in e['implementation']:
            w=next(w for w in sources[p['evidence_file']]['witnesses'] if w['id']==p['witness_id'])
            assert p['entry']==w['entry'] and set(p['methods'])<={m['name'] for m in w.get('methods',[])}
    root=next(w for w in evidence['witnesses'] if w['entry']==PKG+K+'.class')
    assert not {'hurt','canBlockDamageSource','isSleep','setSleep','setAwaken','canBeAffected','die','deathtimer',
        'addAdditionalSaveData','readAdditionalSaveData','finalizeSpawn','getAnimationState','onSyncedDataUpdated'} & {m['name'] for m in root['methods']}
    assert not {'onDeathAIUpdate','AfterDefeatBoss','tickDeath','doHurtTarget'} & set(root['declared_method_names'])
    debris=next(w for w in sources['native-evidence/cataclysm-monstrosity-offense.json']['witnesses'] if w['entry']==PKG+'entity/effect/Cm_Falling_Block_Entity.class')
    assert debris['superclass']=='net/minecraft/world/entity/Entity'
    assert not any('.hurt(' in str(i['operand']) or '.setBlock(' in str(i['operand']) for m in debris['methods'] for i in m['instructions'])
    base=next(w for w in sources['native-evidence/cataclysm-shared.json']['witnesses'] if w['entry']==PKG+'entity/etc/Animation_Monsters.class')
    for name in ['AfterDefeatBoss','onDeathAIUpdate']:
        assert [i['opcode'] for i in next(m['instructions'] for m in base['methods'] if m['name']==name)]==['0xb1']
    assert note['tooling']['new_native_witnesses']==6 and note['tooling']['new_method_witnesses']==19
    assert note['tooling']['new_resource_witnesses']==0
    assert not note['tooling']['recursive_jar_scan'] and not note['tooling']['reused_evidence_regenerated']
    assert read_json(OUT/'cataclysm-installed-common-config.json')['values']['mobs']['kobolediator']['ignore_mobgriefing_config']['ignore_mobgriefing'] is False
    next_entry=PKG+'entity/InternalAnimationMonster/Wadjet_Entity.class'
    assert next_entry in census and census[next_entry]['superclass']==PKG+'entity/InternalAnimationMonster/Internal_Animation_Monster'
    assert not any(e['review_checkpoint'].startswith('R2k15') for e in json.loads(at_start(REVIEW))['effects'])
    validate_native_boundaries(evidence,note)
    return len(new_methods)


def validate(jar_path=None):
    review,note,ledger=[read_json(p) for p in [REVIEW,NOTE,LEDGER]]
    summary=validate_records(review,note,ledger)
    validate_preservation(review,note,ledger)
    methods=validate_evidence(review,note,jar_path)
    for path in [REVIEW,NOTE,LEDGER,SPEC_FILE,EVIDENCE_FILE]:
        assert path.read_text(encoding='utf-8')==json.dumps(read_json(path),ensure_ascii=False,indent=2)+'\n'
    return dict(status='PASS',**summary,new_method_witnesses=methods,
        protected_shared_status_prior_families_r2k14a='BYTE_IDENTICAL',pinned_jar_reproduction='PASS' if jar_path else 'NOT_REQUESTED')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jar',type=Path,help='Reproduce only new witnesses against the exact pinned JAR')
    print(json.dumps(validate(parser.parse_args().jar),indent=2))
