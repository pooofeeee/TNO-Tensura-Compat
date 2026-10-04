"""Focused R2k12b records, native boundaries, protected facts and reproduction."""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import struct
import subprocess

from catalog_common import OUT, ROOT, read_json
from collect_cataclysm_ignited_revenant_offense import (
    ASH, BONE, EVIDENCE_FILE, FRAGMENTS, METHODS, PKG, R, REGISTRY, SPEC_FILE,
    collect, specification,
)

START = '3dc72e96b19b26a5b18a61c46179b196d07f5dd4'
CHECKPOINT = 'R2k12b-cataclysm-ignited-revenant-offense-complete'
NOTE = OUT / 'cataclysm-r2k12b-ignited-revenant-offense.json'
REVIEW = OUT / 'mod-reviews/cataclysm.json'
LEDGER = OUT / 'mod-completion-ledger.json'
KEYS = {'attack_selection','sequence_state','pursuit_goal','ash_delivery','ash_damage',
        'ash_blindness','ash_lifecycle','bone_delivery','bone_self_lift','bone_damage',
        'bone_lifecycle','shield_aura_damage','shield_aura_push','body_repulsion',
        'alliance','terrain_response','defeat_lifecycle'}
KINDS = {'VANILLA_DIRECT','VANILLA_EQUIVALENT','VANILLA_LIKE_EXTENDED','VANILLA_COMPOSITE',
         'CUSTOM_DAMAGE','CUSTOM_STATUS','CUSTOM_CONTROL','CUSTOM_RESOURCE','BINARY_MECHANIC'}
NO_CANDIDATES = {'attack_selection','sequence_state','pursuit_goal','ash_lifecycle',
                 'bone_lifecycle','body_repulsion','alliance','terrain_response','defeat_lifecycle'}
f32 = lambda x: struct.unpack('f',struct.pack('f',x))[0]


def at_start(path):
    return subprocess.check_output(['git','show',START+':'+Path(path).relative_to(ROOT).as_posix()],cwd=ROOT)


def selected(review):
    return [e for e in review['effects'] if e['review_checkpoint']==CHECKPOINT]


def validate_records(review, note, ledger):
    effects, paths = review['effects'], review['paths']
    assert len(effects)==len({e['id'] for e in effects})
    assert len(paths)==len({p['id'] for p in paths})
    assert effects==sorted(effects,key=lambda e:e['id'])
    assert paths==sorted(paths,key=lambda p:p['id'])
    new = selected(review)
    assert {e['id'] for e in new}=={'cataclysm:ignited_revenant_'+k for k in KEYS}
    pids,eids = {p['id'] for p in paths},{e['id'] for e in effects}
    for e in new:
        assert e['mod_key']=='cataclysm' and e['primary_classification'] in KINDS
        assert e['inspection_status']=='STATIC_REVIEWED' and not e['unresolved_ambiguities']
        for k in ['actual_behavior','source_actor','primary_test_source','components','implementation',
                  'delivery_paths','closest_vanilla_equivalent','hurt_return_dependency','binary_parameters']:
            assert e[k], (e['id'],k)
        assert not {'stage_scaling_needed','stage_policy','stage_multiplier','stage_eligibility',
                    'stage_cap','stage_floor','runtime_hook'} & e.keys()
        assert set(e['delivery_paths'])<=pids
        observations = []
        for c in e['components']:
            assert c['primitive'] and c['formula'] and c['native_boundary'] and c['vanilla_relation']
            assert set(c['numerical_parameters'])==set(c['parameter_units'])
            for p,v in c['numerical_parameters'].items():
                assert isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v)
                observations.append(dict(primitive=c['primitive'],parameter=p,native_value=v,
                    native_formula=c['formula'],units=c['parameter_units'][p],boundary=c['native_boundary']))
            assert set(c.get('parameter_formulas',{}))==set(c.get('formula_parameter_units',{}))
            for p,formula in c.get('parameter_formulas',{}).items():
                assert p not in c['numerical_parameters'] and formula
                observations.append(dict(primitive=c['primitive'],parameter=p,native_value=None,
                    native_formula=formula,units=c['formula_parameter_units'][p],boundary=c['native_boundary']))
        assert observations==e['numeric_observations']
        candidates=e['scalable_parameter_candidates']
        assert candidates==sorted(candidates,key=lambda c:(c['primitive'],c['parameters']))
        seen=set()
        for cand in candidates:
            assert len(cand['parameters'])==1
            p=cand['parameters'][0]
            assert (cand['primitive'],p) not in seen
            seen.add((cand['primitive'],p))
            owners=[o for o in observations if o['primitive']==cand['primitive'] and o['parameter']==p]
            assert len(owners)==1,'Candidate lost its native primitive'
            o=owners[0]
            assert cand['native_value']==o['native_value'] and cand['native_formula']==o['native_formula']
            assert cand['units']==o['units'] and cand['native_boundary']==o['boundary']
        if e['id'].removeprefix('cataclysm:ignited_revenant_') in NO_CANDIDATES:
            assert not candidates,'Native state/gates/lifecycle or uncalled helpers are not automatic candidates'
    new_paths=[p for p in paths if p['id'].startswith('cataclysm:ignited-revenant-offense:')]
    assert len(new_paths)==17
    for p in new_paths:
        assert p['mod_key']=='cataclysm' and p['status']=='VERIFIED' and p['runtime_status']=='NOT_RUN'
        assert p['primary_source'] and p['native_path'] and p['setup'] and p['implementation'] and p['labels']
        assert p['effect_ids'] and set(p['effect_ids'])<=eids
        for e in new:
            assert (p['id'] in e['delivery_paths'])==(e['id'] in p['effect_ids'])
    assert note['mechanic_packages']==[dict(id=e['id'],primary_classification=e['primary_classification'],
        delivery_paths=e['delivery_paths'],numerical_candidates=e['scalable_parameter_candidates'],binary_gates=e['binary_parameters']) for e in new]
    assert note['facts']=={e['id'].removeprefix('cataclysm:ignited_revenant_'):e['actual_behavior'] for e in new}
    summary=dict(new_mechanics=len(new),delivery_paths=len(new_paths),
        classifications=dict(sorted(Counter(e['primary_classification'] for e in new).items())),
        candidate_numeric_parameters=sum(len(c['parameters']) for e in new for c in e['scalable_parameter_candidates']),
        new_owned_payload_classes=2,unresolved_subsection_ambiguities=0)
    assert summary==note['summary']
    assert summary['classifications']=={'BINARY_MECHANIC':7,'CUSTOM_CONTROL':3,'VANILLA_LIKE_EXTENDED':7}
    assert summary['candidate_numeric_parameters']==23
    assert review['status']==ledger['status']==note['status']=='PARTIAL'
    assert all(review[k] is False for k in ['semantic_discovery_complete','special_damage_discovery_complete',
                                           'source_mapping_complete','delivery_mapping_complete'])
    cat=next(t for t in ledger['targets'] if t['mod_key']=='cataclysm')
    assert cat['state']=='PARTIAL' and cat['semantic_effect_count']==len(effects)
    assert review['checkpoint']==ledger['checkpoint']==note['checkpoint']==CHECKPOINT
    assert review['exact_next_task']==note['exact_next_task']==cat['exact_next_task']
    assert note['exact_next_task'].startswith('R2k13a: Ignited Berserker incoming admission and combat-state/encounter prerequisites.')
    assert note['ignited_revenant_fully_closed'] and not note['remaining_ignited_revenant_work']
    assert not note['remaining_subsection_native_ambiguities'] and note['remaining_cataclysm_research']
    assert note['runtime_tests']==0
    assert all(note[k] is False for k in ['whole_mod_complete','stage_eligibility_decided','phase6_reopened',
        'production_changed','stage_changed','boss_testing_started','l2_testing_started','compatibility_fixes_started','phase7_started'])
    validate_contracts({e['id'].removeprefix('cataclysm:ignited_revenant_'):e for e in new})
    return summary


def validate_contracts(rows):
    flags={
        'attack_selection':dict(selection_local_server_guard=False,broken_ash_tests_cooldown=False,
            broken_ash_writes_cooldown=False,storm_has_shield_gate=False,selection_has_hp_gate=False),
        'sequence_state':dict(decrement_before_selection=True,selected_cooldown_end_of_tick=200,
            bone_goal_sets_anger=False,attack_state_is_stage=False),
        'pursuit_goal':dict(pursuit_calls_native_hurt=False),
        'ash_delivery':dict(delivery_local_server_guard=False,spawn_requires_target=False,
            constructs_each_goal_tick=True,adds_only_tick27=True,is_moving_projectile=False),
        'ash_damage':dict(hurt_return_used=True,damage_local_server_guard=False,alliance_receiver='payload',
            uses_caster_alliance=False,close_bypasses_query=False,local_los_gate=False,invulnerability_reset=False,ignites_targets=False),
        'ash_blindness':dict(hurt_return_used=True,effect_return_used=False,uses_source_effect_overload=False),
        'ash_lifecycle':dict(saves_native_owner=True,saves_native_damage=True,saves_native_age=False,
            tick_resolves_caster_uuid=False,dead_caster_discard_returns=False,follows_caster_position=False,
            follows_caster_pitch=False,follows_caster_yaw=True,anonymous_damage_fallback=False),
        'bone_delivery':dict(volleys_independently_randomized=True,volley_requires_target=False,
            delivery_local_server_guard=False,volley_shield_gate=False,gravity_disabled=False,initial_y_direction_zero=True),
        'bone_self_lift':dict(control_depends_on_hurt=False,control_recipient='self',uses_native_knockback=False,
            preserves_horizontal_velocity=True,control_local_server_guard=False),
        'bone_damage':dict(hurt_return_used=False,uses_owner_alliance=True,anonymous_magic_fallback=True,
            ignites_targets=False,post_hurt_status=False,invulnerability_reset=False),
        'bone_lifecycle':dict(saves_native_damage=True,parent_owns_owner_persistence=True,
            discard_depends_on_hurt=False,impact_discard_server_only=True,concrete_lifetime_timer=False,damage_on_discard=False),
        'shield_aura_damage':dict(hurt_return_used=True,aura_requires_target=False,aura_checks_no_ai=False,
            aura_local_server_guard=False,local_los_gate=False,excludes_all_revenants=True),
        'shield_aura_push':dict(control_depends_on_hurt=True,uses_native_knockback=False,
            reads_knockback_resistance=False,absolute_velocity_write=False),
        'body_repulsion':dict(local_offense_caller_proven=False,control_depends_on_hurt=False,
            local_team_guard=False,preserves_vertical_velocity=True),
        'alliance':dict(native_team_tag='cataclysm:team_ignis',tag_requires_both_teams_null=True,
            ash_inherits_caster_tag=False,bone_checks_shooter_alliance=True),
        'terrain_response':dict(concrete_terrain_mutation=False,concrete_explosion=False,
            spawns_damaging_debris=False,global_terrain_callbacks_absent_claimed=False),
        'defeat_lifecycle':dict(concrete_respawner_link=False,concrete_death_payload=False,global_death_callbacks_absent_claimed=False),
    }
    for key,fields in flags.items():
        for f,v in fields.items():assert rows[key][f]==v,(key,f)
    def params(key,prim):return next(c['numerical_parameters'] for c in rows[key]['components'] if c['primitive']==prim)
    assert params('ash_blindness','BLINDNESS')==dict(duration=60,amplifier=0)
    assert params('ash_damage','NATIVE_DAMAGE_REQUEST')==dict(installed_damage=4.0)
    assert params('bone_damage','NATIVE_DAMAGE_REQUEST')==dict(installed_damage=5.0)
    assert params('bone_self_lift','FORCED_MOVEMENT')==dict(target_y_velocity=f32(.3),approach_factor=f32(.3))
    assert params('bone_delivery','PROJECTILE_MOTION')==dict(ring1_speed=.5,ring2_speed=f32(.6),ring3_speed=f32(.4),inaccuracy=1.0,initial_y_direction=0.0)
    assert params('shield_aura_push','FORCED_MOVEMENT')==dict(horizontal_factor=1.5,vertical_increment=.2,native_denominator_minimum=.001)
    assert params('shield_aura_damage','ATTACK_CADENCE')==dict(base_interval=6,segment_interval_step=2,shield_limit=4)
    for key in ['ash_damage','bone_damage','shield_aura_damage']:
        cand=next(c for c in rows[key]['scalable_parameter_candidates'] if c['primitive']=='NATIVE_DAMAGE_REQUEST')
        assert cand['parameters']==['requested_damage'] and cand['native_value'] is None
        assert not any('coefficient' in p for c in rows[key]['components'] for p in c['numerical_parameters'])


def validate_preservation(review, note, ledger):
    assert note['starting_sha']==START
    old=json.loads(at_start(REVIEW))
    assert len(old['effects'])==330 and len(old['paths'])==336
    assert [e for e in review['effects'] if e['review_checkpoint']!=CHECKPOINT]==old['effects']
    assert [p for p in review['paths'] if not p['id'].startswith('cataclysm:ignited-revenant-offense:')]==old['paths']
    mutable={'effects','paths','checkpoint','scope','notes_file','exact_next_task','protected_checkpoints'}
    assert {k:v for k,v in review.items() if k not in mutable}=={k:v for k,v in old.items() if k not in mutable}
    assert review['protected_checkpoints']==old['protected_checkpoints']+[dict(checkpoint=old['checkpoint'],notes_file=old['notes_file'])]
    prior=OUT/'cataclysm-r2k12a-ignited-revenant-admission.json'
    required={ref['file'] for ref in read_json(prior)['reference_files']}|{prior.relative_to(OUT).as_posix()}
    assert required<={ref['file'] for ref in note['reference_files']}
    for ref in note['reference_files']:
        path=OUT/ref['file']
        assert hashlib.sha256(path.read_bytes()).hexdigest()==ref['sha256'],ref['file']
        if ref['usage']=='LOCKED_REUSED':assert path.read_bytes()==at_start(path),ref['file']
        else:assert ref['usage']=='NEW_SCOPED' and path in [EVIDENCE_FILE,SPEC_FILE]
    lock=note['protected_r2k12a']
    assert lock['file']==prior.relative_to(OUT).as_posix()
    assert hashlib.sha256(prior.read_bytes()).hexdigest()==lock['sha256']
    assert note['previous_checkpoint']==old['checkpoint']
    previous=json.loads(at_start(LEDGER))
    assert [t for t in ledger['targets'] if t['mod_key']!='cataclysm']==[t for t in previous['targets'] if t['mod_key']!='cataclysm']
    assert {k:v for k,v in ledger.items() if k not in ['targets','checkpoint']}=={k:v for k,v in previous.items() if k not in ['targets','checkpoint']}


def validate_native_boundaries(evidence):
    def witness(n):return next(w for w in evidence['witnesses'] if w['entry']==PKG+n+'.class')
    def body(n,m):return next(x['instructions'] for x in witness(n)['methods'] if x['name']==m)
    def calls(ins,name):return [i['offset'] for i in ins if name in str(i['operand'])]
    def at(ins,off):return next(i for i in ins if i['offset']==off)
    tick=body(R,'tick')
    assert at(tick,110)['branch_target']==123 and at(tick,127)['branch_target']==140
    assert at(tick,217)['operand']==at(tick,284)['operand']==200
    assert calls(tick,'.setAnimation(')==[227,294,355]
    assert calls(tick,'breath_cooldown')==[107,115,120,159,220]
    assert calls(tick,'storm_cooldown')==[124,132,137,234,287]
    assert at(tick,186)['operand']==35 and at(tick,273)['operand']==15 and at(tick,321)['operand']==12
    assert calls(tick,'.hurt(')==[481] and at(tick,488)['opcode']=='0x99' and at(tick,488)['branch_target']==557
    assert at(tick,484)['local_index']==at(tick,486)['local_index']==4
    assert calls(tick,'.push(')==[554] and not calls(tick,'.knockback(') and not calls(tick,'KNOCKBACK_RESISTANCE')
    assert at(tick,410)['operand']==1.25 and at(tick,524)['operand']==.001
    assert at(tick,538)['operand']==at(tick,550)['operand']==1.5 and at(tick,542)['operand']==.2
    assert not calls(tick,'isClientSide') and not calls(tick,'.heal(') and not calls(tick,'.repelEntities(')
    shoot=body(R+'$ShootGoal','tick')
    assert calls(shoot,'.addFreshEntity(')==[262] and at(shoot,265)['opcode']=='0x57'
    assert at(shoot,219)['operand']==27 and at(shoot,221)['branch_target']==266
    assert calls(shoot,'AshenbreathDamage')==[200] and calls(shoot,ASH+'.<init>(')==[208]
    assert not calls(shoot,'isClientSide') and not calls(shoot,'.hurt(')
    bone=body(R+'$BoneStormGoal','tick')
    assert calls(bone,'.nextInt(')==[55,141,225,309]
    assert [at(bone,i)['operand'] for i in [43,128,212,296]]==[5,10,15,20]
    assert calls(bone,'.launchbone1(')==[92,176,260,344]
    assert calls(bone,'.launchbone2(')==[102,186,270,354]
    assert calls(bone,'.launchbone3(')==[112,196,280,364]
    switches = [i for i in bone if i['opcode']=='0xaa']
    assert len(switches)==4
    for s in switches:
        assert set(s['switch_cases'])=={'0','1','2'}
        for case,target in s['switch_cases'].items():
            assert at(bone,target)['opcode']=='0x2a'
            assert '.launchbone'+str(int(case)+1)+'(' in at(bone,target+4)['operand']
    assert at(bone,406)['operand']==100 and at(bone,428)['operand']==.5 and at(bone,431)['operand']==6.891
    assert at(bone,520)['operand']==at(bone,528)['operand']==f32(.3)
    assert calls(bone,'.setDeltaMovement(')==[536] and calls(bone,'.canAttack(')==[485]
    assert not calls(bone,'.hurt(') and not calls(bone,'.setIsAnger(') and not calls(bone,'isClientSide')
    for num,count,speed in [(1,8,.5),(2,6,f32(.6)),(3,10,f32(.4))]:
        ins=body(R,'launchbone'+str(num))
        assert at(ins,14)['operand']==count and calls(ins,'.shoot(') and calls(ins,'.addFreshEntity(')
        assert any(i['operand']==speed for i in ins) and calls(ins,'BlazingBoneDamage')
        assert not calls(ins,'isClientSide') and not calls(ins,'.getTarget(')
    ash=body(ASH,'hitEntities')
    assert calls(ash,'.isAlliedTo(')==[473] and at(ash,471)['opcode']=='0x2a'
    assert calls(ash,'.indirectMagic(')==[497] and calls(ash,'.hurt(')==[504]
    assert at(ash,511)['opcode']=='0x99' and at(ash,511)['branch_target']==539
    assert at(ash,521)['operand']==60 and at(ash,523)['operand']==0
    assert [at(ash,i)['operand'] for i in [524,525,526]]==[0,0,1]
    assert calls(ash,'.addEffect(')==[535] and at(ash,538)['opcode']=='0x57'
    assert '.addEffect(Lnet/minecraft/world/effect/MobEffectInstance;)Z' in at(ash,535)['operand']
    assert at(ash,318)['operand']==2 and at(ash,466)['operand']==3 and at(ash,430)['operand']==2.0
    assert not calls(ash,'.getCaster(') and not calls(ash,'isClientSide') and not calls(ash,'.setSecondsOnFire(')
    age=body(ASH,'tick')
    assert calls(age,'.discard(')==[22,539] and at(age,25)['opcode']=='0x2a'
    assert at(age,515)['branch_target']==529 and at(age,514)['operand']==2
    assert at(age,533)['operand']==25 and at(age,535)['branch_target']==542
    assert calls(age,'.hitEntities(')==[526] and calls(age,'.setYRot(')==[40]
    assert not any(calls(age,n) for n in ['.getCaster(','.setPos(','.setXRot(','.setDeltaMovement('])
    impact=body(BONE,'onHitEntity')
    assert calls(impact,'.getOwner(')==[6] and calls(impact,'.isAlliedTo(')==[29]
    assert at(impact,27)['opcode']=='0x2c' and calls(impact,'.mobProjectile(')==[45] and calls(impact,'.magic(')==[64]
    assert calls(impact,'.hurt(')==[52,71] and at(impact,55)['opcode']==at(impact,74)['opcode']=='0x57'
    assert not any(calls(impact,n) for n in ['.addEffect(','.setSecondsOnFire(','.push(','.heal('])
    hit=body(BONE,'onHit')
    assert at(hit,2)['opcode']=='0xb7' and at(hit,12)['branch_target']==28
    assert calls(hit,'.discard(')==[25] and not calls(hit,'.hurt(')
    assert [i['opcode'] for i in body(BONE,'isNoGravity')]==['0x3','0xac']
    assert not {'tick','onHitBlock','isAlliedTo','canHitEntity'} & set(witness(BONE)['declared_method_names'])
    assert 'isAlliedTo' not in witness(ASH)['declared_method_names']
    assert not calls(body(ASH,'readAdditionalSaveData'),'.getCaster(')
    assert 'Owner' in [i['operand'] for i in body(ASH,'addAdditionalSaveData')]
    registry=body(REGISTRY,'<clinit>')
    assert at(registry,593)['operand']=='blazing_bone' and at(registry,848)['operand']=='ashen_breath'
    assert 'BLAZING_BONE' in at(registry,604)['operand'] and 'ASHEN_BREATH' in at(registry,859)['operand']
    allied=body(R,'isAlliedTo')
    assert calls(allied,'ModTag.TEAM_IGNIS')==[21]
    assert at(allied,34)['opcode']==at(allied,41)['opcode']=='0xc7'
    assert at(allied,34)['branch_target']==at(allied,41)['branch_target']==48
    assert [i['opcode'] for i in body(R,'onDeathAIUpdate')]==['0x2a','0xb7','0xb1']


def validate_evidence(review, note, jar_path=None):
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
    assert len(new_methods)==50
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
            assert p['evidence_file'] in {ref['file'] for ref in note['reference_files']}
            w=next(w for w in read_json(OUT/p['evidence_file'])['witnesses'] if w['entry']==p['entry'])
            assert set(p['methods'])<={m['name'] for m in w['methods']}
    assert note['tooling']['new_native_witnesses']==6 and note['tooling']['new_method_witnesses']==50
    assert note['tooling']['new_owned_payload_classes']==2 and note['tooling']['new_resource_witnesses']==0
    assert not note['tooling']['reused_evidence_regenerated'] and not note['tooling']['recursive_jar_scan']
    next_header=note['next_family_header']
    assert next_header['entry_sha256']==census[next_header['entry']]['entry_sha256']
    assert next_header['superclass']==census[next_header['entry']]['superclass']
    assert next_header['method_bodies_inspected'] is False
    assert not any(e['id'].startswith('cataclysm:ignited_berserker_') for e in review['effects'])
    assert {p['entry'] for p in note['owned_payloads']}=={PKG+ASH+'.class',PKG+BONE+'.class'}
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
        protected_shared_status_prior_families_r2k12a='BYTE_IDENTICAL',
        pinned_jar_reproduction='PASS' if jar_path else 'NOT_REQUESTED')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jar',type=Path,help='Reproduce only new witnesses against the exact pinned JAR')
    print(json.dumps(validate(parser.parse_args().jar),indent=2))
