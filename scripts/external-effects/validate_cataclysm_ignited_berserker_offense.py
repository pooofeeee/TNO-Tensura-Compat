"""Focused R2k13b records, native boundaries, protected facts and reproduction."""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import subprocess

from catalog_common import OUT, ROOT, read_json
from collect_cataclysm_ignited_berserker_offense import (
    B, S, PKG, METHODS, FRAGMENTS, DESCRIPTORS, EVIDENCE_FILE, SPEC_FILE, collect, specification,
)
from validate_cataclysm_ignited_berserker_admission import f32

START='3a48c597937d12402834ad2fec9aa9b24c8f5911'
CHECKPOINT='R2k13b-cataclysm-ignited-berserker-offense-complete'
NOTE=OUT/'cataclysm-r2k13b-ignited-berserker-offense.json'
REVIEW=OUT/'mod-reviews/cataclysm.json'
LEDGER=OUT/'mod-completion-ledger.json'
PRIOR=OUT/'cataclysm-r2k13a-ignited-berserker-admission.json'
KEYS={'attack_selection','sequence_state','pursuit_goal','falling_motion','body_repulsion',
      'area_geometry','area_damage','area_brand','area_heal','shield_disable','combo_self_lunge',
      'spin_aura_damage','spin_push','sword_helper_damage','sword_helper_brand','sword_helper_heal',
      'alliance','payload_terrain_closure','defeat_lifecycle'}
KINDS={'VANILLA_DIRECT','VANILLA_EQUIVALENT','VANILLA_LIKE_EXTENDED','VANILLA_COMPOSITE',
       'CUSTOM_DAMAGE','CUSTOM_STATUS','CUSTOM_CONTROL','CUSTOM_RESOURCE','BINARY_MECHANIC'}
NO_CANDIDATES={'attack_selection','sequence_state','pursuit_goal','sword_helper_damage',
               'sword_helper_brand','sword_helper_heal','alliance','payload_terrain_closure','defeat_lifecycle'}


def at_start(path):
    return subprocess.check_output(['git','show',START+':'+Path(path).relative_to(ROOT).as_posix()],cwd=ROOT)


def selected(review):
    return [e for e in review['effects'] if e['review_checkpoint']==CHECKPOINT]


def validate_records(review,note,ledger):
    effects,paths=review['effects'],review['paths']
    assert len(effects)==len({e['id'] for e in effects}) and len(paths)==len({p['id'] for p in paths})
    assert effects==sorted(effects,key=lambda e:e['id']) and paths==sorted(paths,key=lambda p:p['id'])
    new=selected(review)
    assert {e['id'] for e in new}=={'cataclysm:ignited_berserker_'+k for k in KEYS}
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
        if e['id'].removeprefix('cataclysm:ignited_berserker_') in NO_CANDIDATES:
            assert not candidates,'State/gates/uncalled helpers are not active scalar candidates'
        assert not e['spawned_entity_ids']
    new_paths=[p for p in paths if p['id'].startswith('cataclysm:ignited-berserker-offense:')]
    assert len(new_paths)==19
    for p in new_paths:
        assert p['mod_key']=='cataclysm' and p['status']=='VERIFIED' and p['runtime_status']=='NOT_RUN'
        assert p['primary_source'] and p['native_path'] and p['setup'] and p['implementation'] and p['labels']
        assert p['effect_ids'] and set(p['effect_ids'])<=eids
        for e in new:assert (p['id'] in e['delivery_paths'])==(e['id'] in p['effect_ids'])
    assert note['mechanic_packages']==[dict(id=e['id'],primary_classification=e['primary_classification'],delivery_paths=e['delivery_paths'],
        numerical_candidates=e['scalable_parameter_candidates'],binary_gates=e['binary_parameters']) for e in new]
    assert note['facts']=={e['id'].removeprefix('cataclysm:ignited_berserker_'):e['actual_behavior'] for e in new}
    summary=dict(new_mechanics=len(new),delivery_paths=len(new_paths),classifications=dict(sorted(Counter(e['primary_classification'] for e in new).items())),
        candidate_numeric_parameters=sum(len(c['parameters']) for e in new for c in e['scalable_parameter_candidates']),
        new_owned_payload_classes=0,unresolved_subsection_ambiguities=0)
    assert summary==note['summary']
    assert summary['classifications']=={'BINARY_MECHANIC':6,'CUSTOM_CONTROL':4,'CUSTOM_DAMAGE':1,'CUSTOM_RESOURCE':2,'VANILLA_LIKE_EXTENDED':6}
    assert summary['candidate_numeric_parameters']==15
    assert review['status']==ledger['status']==note['status']=='PARTIAL'
    assert all(review[k] is False for k in ['semantic_discovery_complete','special_damage_discovery_complete','source_mapping_complete','delivery_mapping_complete'])
    cat=next(t for t in ledger['targets'] if t['mod_key']=='cataclysm')
    assert cat['state']=='PARTIAL' and cat['semantic_effect_count']==len(effects)
    assert review['checkpoint']==ledger['checkpoint']==note['checkpoint']==CHECKPOINT
    assert review['exact_next_task']==note['exact_next_task']==cat['exact_next_task']
    assert note['exact_next_task'].startswith('R2k14a: Kobolediator incoming admission and combat-state/encounter prerequisites.')
    assert note['ignited_berserker_fully_closed'] and not note['remaining_ignited_berserker_work']
    assert not note['remaining_subsection_native_ambiguities'] and note['remaining_cataclysm_research']
    assert note['runtime_tests']==0
    assert all(note[k] is False for k in ['whole_mod_complete','stage_eligibility_decided','phase6_reopened','production_changed',
        'stage_changed','boss_testing_started','l2_testing_started','compatibility_fixes_started','phase7_started'])
    validate_contracts({e['id'].removeprefix('cataclysm:ignited_berserker_'):e for e in new},note)
    return summary


def validate_contracts(rows,note):
    flags={
        'attack_selection':dict(rng_before_cooldown=True,selection_has_hp_gate=False,selection_has_los_gate=False,selection_probabilities_are_stage_candidates=False,native_rng_tests=[12,16,16,12]),
        'sequence_state':dict(sword_cooldown=40,spin_cooldown=80,spin_sets_movement_flags=False,state_start_restarts_matching_state=False,cooldown_written_on_stop=True,attack_state_is_stage=False),
        'pursuit_goal':dict(pursuit_calls_hurt=False,ordinary_melee_goal_registered=False,spin_claimed_stationary=False),
        'falling_motion':dict(uses_mob_effect=False,preserves_horizontal_velocity=True,local_server_guard=False),
        'body_repulsion':dict(local_caller_proven=True,absolute_velocity_write=True,local_team_guard=False,preserves_vertical_velocity=True,uses_native_knockback=False),
        'area_geometry':dict(query_before_server_guard=True,wrap_branches_repeat_horizontal_range=False,caller_requires_current_target=False),
        'area_damage':dict(hurt_return_used=True,local_server_guard=True,excludes_all_berserkers=True,post_hurt_velocity=False,ignites_targets=False,invulnerability_reset=False,damage_type='minecraft:mob_attack'),
        'area_brand':dict(hurt_return_used=True,effect_return_used=False,source_effect_overload=False,brand_is_burn_or_dot=False),
        'area_heal':dict(heal_requires_hurt=True,heal_requires_effect_acceptance=False,heal_uses_actual_hp_loss=False),
        'shield_disable':dict(requires_hurt_success=False,blocked_rechecked_after_hurt=True,uses_actual_use_item=True,disabled_calls_are_zero=True),
        'combo_self_lunge':dict(state5_lunge_ticks=[11,18,23,28],state6_lunge_ticks=[15,123,26,33],uses_native_knockback=False,absolute_velocity_write=False,local_server_guard=False,uses_body_yaw=False),
        'spin_aura_damage':dict(hurt_return_used=True,local_server_guard=True,uses_global_tick_count=True,current_target_required=False,applies_brand=False,heals_self=False,damage_type='minecraft:mob_attack'),
        'spin_push':dict(control_depends_on_hurt=True,uses_native_knockback=False,absolute_velocity_write=False,reads_knockback_resistance=False),
        'sword_helper_damage':dict(local_caller_proven=False,local_server_guard=False,explicit_same_type_exclusion=False,damage_type='cataclysm:sword_dance',bundled_damage_tags=['minecraft:bypasses_cooldown']),
        'sword_helper_brand':dict(local_caller_proven=False,effect_return_used=False),
        'sword_helper_heal':dict(local_caller_proven=False,heal_requires_effect_acceptance=False),
        'alliance':dict(native_team_tag='cataclysm:team_ignis',tag_requires_both_teams_null=True,body_repulsion_checks_alliance=False),
        'payload_terrain_closure':dict(owned_payload_classes=0,concrete_explosion=False,concrete_terrain_mutation=False,concrete_grab_or_mount=False,global_callbacks_absent_claimed=False),
        'defeat_lifecycle':dict(concrete_respawner_link=False,concrete_death_payload=False,global_callbacks_absent_claimed=False),
    }
    for key,fields in flags.items():
        for f,v in fields.items():assert rows[key][f]==v,(key,f)
    def params(key,prim):return next(c['numerical_parameters'] for c in rows[key]['components'] if c['primitive']==prim)
    assert params('falling_motion','FORCED_MOVEMENT')==dict(vertical_factor=.6)
    assert params('body_repulsion','FORCED_MOVEMENT')==dict(horizontal_coefficient=-.1)
    assert params('combo_self_lunge','FORCED_MOVEMENT')==dict(horizontal_increment=.45,vertical_increment=0.0)
    assert params('spin_push','FORCED_MOVEMENT')==dict(horizontal_factor=.5,vertical_increment=.1,native_denominator_floor=.001)
    assert params('spin_aura_damage','ATTACK_CADENCE')==dict(interval=4)
    assert params('spin_aura_damage','ATTACK_VOLUME')==dict(inflate=1.0)
    assert params('area_brand','BLAZING_BRAND')==dict(duration=100,native_stack_increment=1,native_min_amplifier=0,native_max_amplifier=1)
    assert params('sword_helper_brand','BLAZING_BRAND')==dict(duration=120,native_max_amplifier=1)
    assert params('area_heal','HEAL_REQUEST')==dict(heal_per_level=2.0)
    assert params('sword_helper_heal','HEAL_REQUEST')==dict(heal_per_level=3)
    assert params('shield_disable','ITEM_COOLDOWN')==dict(duration=60)
    assert rows['sequence_state']['goal_bindings']==note['goal_bindings']
    assert [(b['required_state'],b['active_state'],b['end_state'],b['max_ticks'],b['look_ticks']) for b in note['goal_bindings']]==[
        (0,1,0,50,15),(0,5,0,50,50),(0,6,0,55,55),(0,2,3,30,25),(3,3,4,90,0),(4,4,0,40,0)]
    assert all(b['priority']==1 for b in note['goal_bindings']) and note['goal_bindings'][4]['set_movement_flags'] is False
    assert params('attack_selection','GOAL_ADMISSION')==dict(rng_scale=100.0,state1_threshold=12.0,state5_threshold=16.0,state6_threshold=16.0,
        spin_windup_threshold=12.0,state1_range=f32(3.6),combo_range=4.5,spin_windup_range=8.0)
    assert params('sequence_state','RAW_ATTACK_STATE')==dict(state1_max_ticks=50,state5_max_ticks=50,state6_max_ticks=55,
        windup_max_ticks=30,spin_max_ticks=90,recovery_max_ticks=40,state1_look_ticks=15,state5_look_ticks=50,state6_look_ticks=55,
        windup_look_ticks=25,spin_look_ticks=0,recovery_look_ticks=0,sword_cooldown=40,spin_cooldown=80)
    calls=[]
    for state,events in [(1,[(17,4.35,45,1.25,60),(35,3.6,200,1.25,0)]),
                         (5,[(13,4.5,50,1,0),(20,3.5,60,1,0),(25,4.5,60,1,0),(30,3.25,60,1,0)]),
                         (6,[(17,4.5,40,1,0),(25,3.25,55,1,0),(28,5,60,1,0),(35,3.5,40,1,0)])]:
        for tick,width,arc,damage,shield in events:
            calls.append(dict(attack_state=state,attack_tick=tick,range_width_multiplier=f32(width),height_width_multiplier=f32(width),
                arc_degrees=f32(arc),damage_multiplier=f32(damage),shield_disable_ticks=shield))
    assert rows['area_geometry']['area_call_parameters']==note['area_call_parameters']==calls
    for k in ['area_damage','spin_aura_damage']:
        assert rows[k]['scalable_parameter_candidates'][0 if k=='area_damage' else -1]['primitive']=='NATIVE_DAMAGE_REQUEST'
    assert [c['parameters'] for c in rows['area_brand']['scalable_parameter_candidates']]==[['duration']]
    assert [c['parameters'] for c in rows['area_heal']['scalable_parameter_candidates']]==[['requested_heal']]


def validate_preservation(review,note,ledger):
    assert note['starting_sha']==START
    old=json.loads(at_start(REVIEW));previous=json.loads(at_start(LEDGER))
    assert len(old['effects'])==356 and len(old['paths'])==362
    assert [e for e in review['effects'] if e['review_checkpoint']!=CHECKPOINT]==old['effects']
    assert [p for p in review['paths'] if not p['id'].startswith('cataclysm:ignited-berserker-offense:')]==old['paths']
    mutable={'effects','paths','checkpoint','scope','notes_file','exact_next_task','protected_checkpoints'}
    assert {k:v for k,v in review.items() if k not in mutable}=={k:v for k,v in old.items() if k not in mutable}
    assert review['protected_checkpoints']==old['protected_checkpoints']+[dict(checkpoint=old['checkpoint'],notes_file=old['notes_file'])]
    required={r['file'] for r in read_json(PRIOR)['reference_files']}|{PRIOR.relative_to(OUT).as_posix()}
    assert required<={r['file'] for r in note['reference_files']}
    for ref in note['reference_files']:
        path=OUT/ref['file'];assert hashlib.sha256(path.read_bytes()).hexdigest()==ref['sha256'],ref['file']
        if ref['usage']=='LOCKED_REUSED':assert path.read_bytes()==at_start(path),ref['file']
        else:assert ref['usage']=='NEW_SCOPED' and path in [EVIDENCE_FILE,SPEC_FILE]
    assert note['protected_r2k13a']==dict(file=PRIOR.relative_to(OUT).as_posix(),sha256=hashlib.sha256(PRIOR.read_bytes()).hexdigest())
    assert note['previous_checkpoint']==old['checkpoint']
    assert [t for t in ledger['targets'] if t['mod_key']!='cataclysm']==[t for t in previous['targets'] if t['mod_key']!='cataclysm']
    assert {k:v for k,v in ledger.items() if k not in ['targets','checkpoint']}=={k:v for k,v in previous.items() if k not in ['targets','checkpoint']}


def validate_native_boundaries(evidence,note):
    def body(n,m):return next(meth['instructions'] for w in evidence['witnesses'] if w['entry']==PKG+n+'.class' for meth in w['methods'] if meth['name']==m)
    def at(ins,off):return next(i for i in ins if i['offset']==off)
    def calls(ins,term):return [i['offset'] for i in ins if i['opcode'] in ['0xb6','0xb7','0xb8','0xb9'] and term in str(i['operand'])]
    tick=body(B,'tick');ai=body(B,'aiStep');reg=body(B,'registerGoals')
    assert calls(tick,'.repelEntities(')==[133] and at(tick,120)['operand']==.75
    assert at(tick,29)['operand']==.6 and calls(tick,'.multiply(')==[33]
    assert calls(tick,'.setDeltaMovement(')==[36]
    assert at(tick,86)['branch_target']==99 and at(tick,103)['branch_target']==116
    for off,val in [(156,4),(182,1.0),(304,.001),(319,.5),(323,.1),(331,.5),
                    (388,.45),(392,0.0),(395,.45),(600,123),(626,.45),(630,0.0),(633,.45)]:
        assert at(ai,off)['operand']==val,(off,val)
    assert 'tickCount' in at(ai,153)['operand']
    assert calls(ai,'.hurt(')==[259] and at(ai,266)['branch_target']==338
    assert calls(ai,'LivingEntity.push(')==[335] and calls(ai,B+'.push(')==[399,637]
    assert calls(ai,'.AreaSwordAttack(')==[] and calls(ai,'.AreaAttack(')==[96,141,442,487,530,575,680,725,770,815]
    for off,c in zip(calls(ai,'.AreaAttack('),note['area_call_parameters']):
        idx=ai.index(at(ai,off));args=ai[idx-10:idx]
        assert [i['opcode'] for i in args]==['0x2a','0x23',args[2]['opcode'],'0x6a','0x23',args[5]['opcode'],'0x6a',args[7]['opcode'],args[8]['opcode'],args[9]['opcode']]
        assert [args[i]['operand'] for i in [2,5,7,8,9]]==[c[k] for k in ['range_width_multiplier','height_width_multiplier','arc_degrees','damage_multiplier','shield_disable_ticks']]
    assert at(reg,235)['operand']==0 and calls(reg,S+'.<init>(')==[236]
    state_ctor=body(S,'<init>')
    assert at(state_ctor,9)['local_index']==7 and at(state_ctor,11)['branch_target']==30
    assert calls(state_ctor,'.setFlags(')==[27] and not calls(body(S,'tick'),'.setDeltaMovement(')
    for n,chance in [(1,12),(2,16),(3,16),(4,12)]:
        ins=body(B+'$'+str(n),'canUse')
        assert calls(ins,'.canUse(')==[1] and calls(ins,'.nextFloat(')==[14]
        constants=[i['operand'] for i in ins if i['opcode'] in ['0x12','0x13']]
        assert constants==[100.0,float(chance)]
        if n in [2,3,4]:
            assert max(i['offset'] for i in ins if i['opcode']=='0xb4' and 'cooldown' in str(i['operand']))>14
    for n,value,field in [(2,40,'sword_dance_cooldown'),(3,40,'sword_dance_cooldown'),(5,80,'spin_cooldown')]:
        ins=body(B+'$'+str(n),'stop')
        assert calls(ins,'.stop(')==[1]
        assert value in [i['operand'] for i in ins if i['opcode'] in ['0x10','0x11']]
        assert any(i['opcode']=='0xb5' and field in str(i['operand']) for i in ins)
    assert evidence['area_sword_caller_check']==dict(scope=[PKG+B+'.class']+[PKG+B+'$'+str(i)+'.class' for i in range(1,6)],exact_target=PKG+B+'.AreaSwordAttack(FFFFF)V',callers=[])


def validate_evidence(review,note,jar_path=None):
    assert read_json(SPEC_FILE)==specification()
    evidence=read_json(EVIDENCE_FILE)
    if jar_path:
        reproduced=collect(jar_path)
        assert evidence==reproduced,'New witnesses failed pinned-JAR reproduction'
        assert EVIDENCE_FILE.read_bytes()==(json.dumps(reproduced,ensure_ascii=False,indent=2)+'\n').encode()
    assert len(evidence['witnesses'])==7 and {w['entry'] for w in evidence['witnesses']}=={PKG+n+'.class' for n in METHODS}
    census={c['entry']:c for c in read_json(OUT/'cataclysm-source-census.json')['classes']}
    new_methods={(w['entry'],m['name'],m['descriptor']):m for w in evidence['witnesses'] for m in w['methods']}
    assert len(new_methods)==18
    sources={p['evidence_file']:read_json(OUT/p['evidence_file']) for e in selected(review) for p in e['implementation']}
    for file,data in sources.items():
        if file==EVIDENCE_FILE.relative_to(OUT).as_posix():continue
        for w in data['witnesses']:
            for old in w.get('methods',[]):
                new=new_methods.get((w['entry'],old['name'],old['descriptor']))
                if new:
                    assert 'instruction_offset_ranges' in new,'Old method recaptured'
                    assert new['code_sha256']==old['code_sha256']
                    assert not {i['offset'] for i in new['instructions']} & {i['offset'] for i in old['instructions']}
    for w in evidence['witnesses']:
        assert w['jar_sha256']==note['tooling']['jar_sha256'] and w['entry_sha256']==census[w['entry']]['entry_sha256']
        assert w['superclass']==census[w['entry']]['superclass']
        n=w['entry'][len(PKG):-6]
        assert {m['name'] for m in w['methods']}==set(METHODS[n])|set(FRAGMENTS.get(n,{}))
        for m in w['methods']:
            if 'instruction_offset_ranges' in m:assert m['instruction_offset_ranges']==FRAGMENTS[n][m['name']]
            if m['name'] in DESCRIPTORS.get(n,{}):assert m['descriptor'] in DESCRIPTORS[n][m['name']]
            assert not any('ModSounds' in str(i['operand']) or 'AnimationState' in str(i['operand']) or 'addParticle' in str(i['operand']) for i in m['instructions'])
    for e in selected(review):
        for p in e['implementation']:
            w=next(w for w in sources[p['evidence_file']]['witnesses'] if w['id']==p['witness_id'])
            assert p['entry']==w['entry'] and set(p['methods'])<={m['name'] for m in w['methods']}
    assert note['tooling']['new_native_witnesses']==7 and note['tooling']['new_method_witnesses']==18 and note['tooling']['new_resource_witnesses']==0
    assert not note['tooling']['reused_evidence_regenerated'] and not note['tooling']['recursive_jar_scan']
    assert PKG+'entity/InternalAnimationMonster/Kobolediator_Entity.class' in census
    assert not any(e['id'].startswith('cataclysm:kobolediator_') for e in review['effects'])
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
        protected_shared_status_prior_families_r2k13a='BYTE_IDENTICAL',pinned_jar_reproduction='PASS' if jar_path else 'NOT_REQUESTED')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jar',type=Path,help='Reproduce only new witnesses against the exact pinned JAR')
    print(json.dumps(validate(parser.parse_args().jar),indent=2))
