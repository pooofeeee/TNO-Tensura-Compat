"""Focused R2k13a admission/state/encounter and pinned-JAR validation."""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import struct
import subprocess

from catalog_common import OUT, ROOT, read_json
from collect_cataclysm_ignited_berserker_admission import (
    B, EVIDENCE_FILE, FRAGMENTS, METHODS, PKG, REGISTRY, SPEC_FILE, collect, specification,
)

START = '54cd83f5cdb945cdae799baf221de59d53ab9cc3'
CHECKPOINT = 'R2k13a-cataclysm-ignited-berserker-admission-complete'
NOTE = OUT / 'cataclysm-r2k13a-ignited-berserker-admission.json'
REVIEW = OUT / 'mod-reviews/cataclysm.json'
LEDGER = OUT / 'mod-completion-ledger.json'
I = 'entity/InternalAnimationMonster/Internal_Animation_Monster'
A = 'entity/etc/Animation_Monsters'
KEYS = {'incoming_admission','native_invulnerability','shared_defense_applicability',
        'environment_admission','combat_state_prerequisites','combat_persistence',
        'encounter_setup','spawn_prerequisites','death_state_reset'}
KINDS = {'VANILLA_DIRECT','VANILLA_EQUIVALENT','VANILLA_LIKE_EXTENDED','VANILLA_COMPOSITE',
         'CUSTOM_DAMAGE','CUSTOM_STATUS','CUSTOM_CONTROL','CUSTOM_RESOURCE','BINARY_MECHANIC'}
ORDER = ['NO_CONCRETE_OR_CATACLYSM_PARENT_HURT_WRAPPER','NATIVE_VIRTUAL_INVULNERABILITY',
         'NATIVE_CLIENT_DEAD_FIRE_RESISTANCE_REJECTIONS','NATIVE_DAMAGE_CONTAINER_AND_INCOMING_EVENT',
         'NATIVE_SHIELD_FREEZING_HELMET_PROCESSING','NATIVE_COOLDOWN_AND_ACTUALLY_HURT_DEFENSES',
         'NATIVE_SOURCE_CREDIT_IMPACT_TOTEM_DEATH_AND_CALLBACKS','NATIVE_RETURN_NO_CONCRETE_POST_HURT_WRITE']
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
    assert {e['id'] for e in new}=={'cataclysm:ignited_berserker_'+k for k in KEYS}
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
        assert observations==e['numeric_observations']
        assert e['scalable_parameter_candidates']==[], 'Defense/state/encounter constants are not automatic Stage candidates'
    new_paths=[p for p in paths if p['id'].startswith('cataclysm:ignited-berserker-admission:')]
    assert len(new_paths)==9
    for p in new_paths:
        assert p['mod_key']=='cataclysm' and p['status']=='VERIFIED' and p['runtime_status']=='NOT_RUN'
        assert p['primary_source'] and p['native_path'] and p['setup'] and p['implementation'] and p['labels']
        assert p['effect_ids'] and set(p['effect_ids'])<=eids
        for e in new:
            assert (p['id'] in e['delivery_paths'])==(e['id'] in p['effect_ids'])
    assert note['mechanic_packages']==[dict(id=e['id'],primary_classification=e['primary_classification'],
        delivery_paths=e['delivery_paths'],numerical_candidates=e['scalable_parameter_candidates'],binary_gates=e['binary_parameters']) for e in new]
    assert note['facts']=={e['id'].removeprefix('cataclysm:ignited_berserker_'):e['actual_behavior'] for e in new}
    summary=dict(new_mechanics=len(new),delivery_paths=len(new_paths),
        classifications=dict(sorted(Counter(e['primary_classification'] for e in new).items())),
        candidate_numeric_parameters=0,boss_shared_bindings_applicable=False,unresolved_subsection_ambiguities=0)
    assert summary==note['summary'] and summary['classifications']=={'BINARY_MECHANIC':9}
    assert review['status']==ledger['status']==note['status']=='PARTIAL'
    assert all(review[k] is False for k in ['semantic_discovery_complete','special_damage_discovery_complete',
                                           'source_mapping_complete','delivery_mapping_complete'])
    cat=next(t for t in ledger['targets'] if t['mod_key']=='cataclysm')
    assert cat['state']=='PARTIAL' and cat['semantic_effect_count']==len(effects)
    assert review['checkpoint']==ledger['checkpoint']==note['checkpoint']==CHECKPOINT
    assert review['exact_next_task']==note['exact_next_task']==cat['exact_next_task']
    assert note['exact_next_task'].startswith('R2k13b: Ignited Berserker offense/payload family.')
    assert note['remaining_ignited_berserker_work']==['R2k13b Ignited Berserker offense/payload family']
    assert not note['remaining_subsection_native_ambiguities'] and note['remaining_cataclysm_research']
    assert note['runtime_tests']==0
    assert all(note[k] is False for k in ['whole_mod_complete','stage_eligibility_decided','phase6_reopened',
        'production_changed','stage_changed','boss_testing_started','l2_testing_started','compatibility_fixes_started','phase7_started'])
    validate_contracts({e['id'].removeprefix('cataclysm:ignited_berserker_'):e for e in new},note)
    return summary


def validate_contracts(rows, note):
    flags={
        'incoming_admission':dict(concrete_hurt_override=False,concrete_invulnerability_override=False,
            incoming_amount_rewritten=False,concrete_direct_entity_read=False,concrete_causing_entity_read=False,
            concrete_source_position_read=False,concrete_post_hurt_callback=False,shared_boss_hurt_reached=False,all_damage_admitted_claimed=False),
        'native_invulnerability':dict(phase_invulnerability_override=False,shield_invulnerability_override=False,
            unconditional_bypass_claimed=False,unconditional_fall_immunity_claimed=False,native_invulnerability_hook_preserved=True),
        'shared_defense_applicability':dict(damage_cap_applicable=False,dps_cap_applicable=False,range_limit_applicable=False,
            nature_regen_applicable=False,heal_cooldown_applicable=False,boss_effect_whitelist_applies=False,
            boss_home_return_applies=False,boss_defaults_substituted=False,positive_regen_delivery=False,all_effects_admitted_claimed=False),
        'environment_admission':dict(registered_fire_immune=True,air_returns_argument=True,air_returns_native_max=False,
            incoming_entity_push=False,can_ride=False,blanket_drowning_immunity_claimed=False,
            all_forced_motion_immunity_claimed=False,concrete_fluid_override=False),
        'combat_state_prerequisites':dict(concrete_local_synced_state=False,raw_state_is_stage=False,
            state_setter_clamps=False,state_setter_heals=False,concrete_incoming_state_gate=False,
            offensive_execution_reviewed=False,concrete_altar_activation_gate=False),
        'combat_persistence':dict(saved_attack_state=False,saved_attack_ticks=False,saved_local_attack_cooldowns=False,
            saved_local_animation_states=False,inherited_boss_home_nbt=False,inherited_ia_boss_life=False,generic_persistence_added=False),
        'encounter_setup':dict(constructor_calls_config_attribute_helper=False,installed_combat_config_present=False,
            constructor_is_heal_delivery=False,constructor_sets_home=False,constructor_sets_combat_state=False,
            concrete_finalize_spawn_override=False,concrete_interaction_override=False,
            explicit_armor_toughness_added=False,exhaustive_spawn_discovery_claimed=False),
        'spawn_prerequisites':dict(spawner_bypasses_world_flag=False,roll_argument_one_has_random_exclusion=False,
            non_spawner_roll_consumes_rng=True,requires_actual_server_level=True,requires_spawn_dimension_nether=False,
            world_lookup_has_overworld_fallback=True,calls_super_spawn_rules=False,constructor_runs_instance_spawn_rules=False,
            spawn_writes_world_flag=False,spawned_home_seed=False,universal_spawn_gate_claimed=False,placement_is_any_light=True),
        'death_state_reset':dict(reset_after_super_die=True,reset_requires_death_success=False,
            reset_requires_hurt_success=False,source_object_preserved=True,concrete_respawner_created=False,
            full_offense_death_family_reviewed=False),
    }
    for key,fields in flags.items():
        for f,v in fields.items():assert rows[key][f]==v,(key,f)
    assert rows['incoming_admission']['admission_order']==note['admission_order']==ORDER
    assert note['hierarchy']==[PKG+B,PKG+I,PKG+A,'net/minecraft/world/entity/monster/Monster']
    assert set(note['concrete_bindings'])==DEFENSE_NAMES
    for binding in note['concrete_bindings'].values():
        assert binding['applicable'] is False and binding['inherited'] is False and binding['native_value'] is None and binding['reason']
    assert note['installed_config']==dict(combat_config_present=False,constructor_applies_config_multiplier=False)
    def params(key,prim):return next(c['numerical_parameters'] for c in rows[key]['components'] if c['primitive']==prim)
    assert params('encounter_setup','NATIVE_ATTRIBUTE_SETUP')==dict(follow_range=20.0,movement_speed=f32(.32),
        attack_damage=7.5,max_health=65.0,armor=8.0,step_height=1.25,knockback_resistance=1.0)
    assert params('encounter_setup','ENTITY_TYPE_SETUP')==dict(width=1.0,height=f32(2.4))
    assert params('environment_admission','NATIVE_ENVIRONMENT_ADMISSION')==dict(rail_path_malus=0.0,water_path_malus=-1.0)
    assert params('combat_state_prerequisites','RAW_ATTACK_STATE')==dict(default_state=0,setter_attack_ticks_reset=0)
    assert params('combat_state_prerequisites','ATTACK_COOLDOWN_STATE')==dict(initial_sword_dance_cooldown=0,initial_spin_cooldown=0)
    assert params('spawn_prerequisites','INSTANCE_SPAWN_ADMISSION')==dict(roll_argument=1)
    assert params('death_state_reset','RAW_ATTACK_STATE_RESET')==dict(reset_state=0)
    assert params('death_state_reset','NATIVE_DEATH_DURATION')==dict(duration=20)


def validate_preservation(review, note, ledger):
    assert note['starting_sha']==START
    old=json.loads(at_start(REVIEW))
    assert len(old['effects'])==347 and len(old['paths'])==353
    assert [e for e in review['effects'] if e['review_checkpoint']!=CHECKPOINT]==old['effects']
    assert [p for p in review['paths'] if not p['id'].startswith('cataclysm:ignited-berserker-admission:')]==old['paths']
    mutable={'effects','paths','checkpoint','scope','notes_file','exact_next_task','protected_checkpoints'}
    assert {k:v for k,v in review.items() if k not in mutable}=={k:v for k,v in old.items() if k not in mutable}
    assert review['protected_checkpoints']==old['protected_checkpoints']+[dict(checkpoint=old['checkpoint'],notes_file=old['notes_file'])]
    prior=OUT/'cataclysm-r2k12b-ignited-revenant-offense.json'
    required={ref['file'] for ref in read_json(prior)['reference_files']}|{prior.relative_to(OUT).as_posix()}
    assert required<={ref['file'] for ref in note['reference_files']}
    for ref in note['reference_files']:
        path=OUT/ref['file']
        assert hashlib.sha256(path.read_bytes()).hexdigest()==ref['sha256'],ref['file']
        if ref['usage']=='LOCKED_REUSED':assert path.read_bytes()==at_start(path),ref['file']
        else:assert ref['usage']=='NEW_SCOPED' and path in [EVIDENCE_FILE,SPEC_FILE]
    lock=note['protected_r2k12b']
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
    for method in ['addAdditionalSaveData','readAdditionalSaveData','defineSynchedData']:
        ins=body(B,method)
        assert [i['opcode'] for i in ins]==['0x2a','0x2b','0xb7','0xb1']
        assert I+'.'+method in at(ins,2)['operand']
    assert [i['opcode'] for i in body(B,'decreaseAirSupply')]==['0x1b','0xac']
    for method in ['canRide','canBePushedByEntity']:
        assert [i['opcode'] for i in body(B,method)]==['0x3','0xac']
    die=body(B,'die')
    assert [i['opcode'] for i in die]==['0x2a','0x2b','0xb7','0x2a','0x3','0xb6','0xb1']
    assert I+'.die(' in at(die,2)['operand'] and at(die,6)['operand']==0
    assert calls(die,'.setAttackState(')==[7] and not any('branch_target' in i for i in die)
    assert body(B,'deathtimer')[0]['operand']==20
    ctor=body(B,'<init>')
    assert at(ctor,84)['operand']==at(ctor,89)['operand']==0
    assert at(ctor,103)['operand']==0.0 and at(ctor,111)['operand']==-1.0
    invocations=witness(B)['constructor_nonvisual_invocations']
    assert invocations==[PKG+I+'.<init>(Lnet/minecraft/world/entity/EntityType;Lnet/minecraft/world/level/Level;)V',
        *[PKG+B+'.setPathfindingMalus(Lnet/minecraft/world/level/pathfinder/PathType;F)V']*2]
    spawn=body(B,'checkSpawnRules')
    assert at(spawn,0)['operand']==1 and calls(spawn,'.rollSpawn(')==[6]
    assert at(spawn,13)['operand']=='net/minecraft/server/level/ServerLevel'
    assert at(spawn,9)['branch_target']==at(spawn,16)['branch_target']==52
    assert calls(spawn,'Level.NETHER')==[25] and calls(spawn,'CMWorldData.get(')==[28]
    assert calls(spawn,'.isIgnisDefeatedOnce(')==[40] and at(spawn,35)['branch_target']==50
    assert not calls(spawn,'.dimension(') and not calls(spawn,'.checkSpawnRules(') and not calls(spawn,'.setIgnisDefeatedOnce(')
    roll=body(REGISTRY,'rollSpawn')
    assert calls(roll,'.isSpawner(')==[1] and at(roll,4)['branch_target']==9
    assert at(roll,7)['operand']==1 and at(roll,8)['opcode']=='0xac'
    assert calls(roll,'.nextInt(')==[15] and at(roll,20)['branch_target']==27
    factory=body(REGISTRY,'lambda$static$23')
    assert calls(factory,'.fireImmune(')==[18]
    assert at(factory,11)['operand']==1.0 and at(factory,12)['operand']==f32(2.4)
    assert at(factory,21)['operand']=='cataclysm:ignited_berserker'
    reg=body(REGISTRY,'<clinit>')
    assert at(reg,406)['operand']=='ignited_berserker' and '.IGNITED_BERSERKERL' in at(reg,417)['operand']
    placement=body(REGISTRY,'registerSpawnPlacements')
    assert '.IGNITED_BERSERKERL' in at(placement,244)['operand']
    assert 'ON_GROUND' in at(placement,253)['operand'] and 'MOTION_BLOCKING_NO_LEAVES' in at(placement,256)['operand']
    assert '$Operation.REPLACE' in at(placement,264)['operand'] and calls(placement,'.register(')==[267]
    bootstraps={b['index']:b for b in witness(REGISTRY)['registration_bootstraps']}
    assert set(bootstraps)=={10,90,137}
    assert any(PKG+B+'.<init>' in a for a in bootstraps[90]['arguments'])
    assert any('ModEntities.lambda$static$23' in a for a in bootstraps[137]['arguments'])
    assert any('Monster.checkAnyLightMonsterSpawnRules' in a for a in bootstraps[10]['arguments'])
    attributes=body(B,'ignited_berserker')
    assert len(calls(attributes,'.add('))==7
    assert not calls(attributes,'ARMOR_TOUGHNESS') and not calls(attributes,'.setConfigattribute(')


def validate_evidence(review, note, jar_path=None):
    assert read_json(SPEC_FILE)==specification()
    evidence=read_json(EVIDENCE_FILE)
    assert len(evidence['witnesses'])==2
    assert {w['entry'] for w in evidence['witnesses']}=={PKG+n+'.class' for n in METHODS}
    if jar_path is not None:
        reproduced=collect(jar_path)
        assert evidence==reproduced,'New witnesses failed pinned-JAR reproduction'
        assert EVIDENCE_FILE.read_bytes()==(json.dumps(reproduced,ensure_ascii=False,indent=2)+'\n').encode()
    census={c['entry']:c for c in read_json(OUT/'cataclysm-source-census.json')['classes']}
    new_methods={(w['entry'],m['name'],m['descriptor']):m for w in evidence['witnesses'] for m in w['methods']}
    assert len(new_methods)==15
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
    root=next(w for w in evidence['witnesses'] if w['entry']==PKG+B+'.class')
    parents=read_json(OUT/'native-evidence/cataclysm-remnant-admission.json')['witnesses']
    chain=[root['class_name']]
    absent=DEFENSE_NAMES|{'hurt','isInvulnerableTo','canBeAffected','ReturnToHome','setHomePos',
        'getHomePos','finalizeSpawn','mobInteract','PlayerCounter'}
    for name in [B,I,A]:
        w=root if name==B else next(w for w in parents if w['entry']==PKG+name+'.class')
        chain.append(w['superclass'])
        assert not absent & set(w['declared_method_names'])
        if name!=B:assert not {'addAdditionalSaveData','readAdditionalSaveData'} & set(w['declared_method_names'])
    assert chain==note['hierarchy']
    assert not {'tick','aiStep','registerGoals','AreaAttack','AreaSwordAttack','isAlliedTo',
        'getAnimationState','onSyncedDataUpdated','stopAllAnimationStates'} & {m['name'] for m in root['methods']}
    assert note['tooling']['new_native_witnesses']==2 and note['tooling']['new_method_witnesses']==15
    assert note['tooling']['new_resource_witnesses']==0
    assert not note['tooling']['reused_evidence_regenerated'] and not note['tooling']['recursive_jar_scan']
    assert 'ignited_berserker' not in read_json(OUT/'cataclysm-installed-common-config.json')['values']['mobs']
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
        protected_shared_status_prior_families_revenant='BYTE_IDENTICAL',
        pinned_jar_reproduction='PASS' if jar_path else 'NOT_REQUESTED')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jar',type=Path,help='Reproduce only new witnesses against the exact pinned JAR')
    print(json.dumps(validate(parser.parse_args().jar),indent=2))
