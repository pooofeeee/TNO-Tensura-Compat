"""Focused R2k12a records, protected contracts and pinned-JAR checks."""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import struct
import subprocess
import sys

from catalog_common import OUT, ROOT, read_json
from collect_cataclysm_ignited_revenant_admission import (
    EVIDENCE_FILE, FRAGMENTS, METHODS, PIECE, PKG, R, REGISTRY, SPEC_FILE,
    collect, specification,
)

START = 'd029e450a9a70d9cd9904298591f7f17c075bc81'
CHECKPOINT = 'R2k12a-cataclysm-ignited-revenant-admission-complete'
NOTE = OUT / 'cataclysm-r2k12a-ignited-revenant-admission.json'
REVIEW = OUT / 'mod-reviews/cataclysm.json'
LEDGER = OUT / 'mod-completion-ledger.json'
KEYS = {'incoming_admission', 'shield_break_admission', 'shield_block_admission',
        'shared_defense_bindings', 'environment_admission', 'falling_motion',
        'combat_state_prerequisites', 'combat_persistence', 'encounter_setup', 'arena_spawn_prerequisites'}
KINDS = {'VANILLA_DIRECT', 'VANILLA_EQUIVALENT', 'VANILLA_LIKE_EXTENDED',
         'VANILLA_COMPOSITE', 'CUSTOM_DAMAGE', 'CUSTOM_STATUS', 'CUSTOM_CONTROL',
         'CUSTOM_RESOURCE', 'BINARY_MECHANIC'}
ORDER = ['READ_DIRECT_ENTITY', 'SERVER_ANGER_DIRECT_LIVING_AXE_THRESHOLD_SHIELD_BREAK_FALSE',
         'POSITIVE_AMOUNT_AND_POSITIONAL_SHIELD_BLOCK_FALSE',
         'SHARED_HURT_SAME_SOURCE_SAME_AMOUNT', 'RETURN_SHARED_RESULT_WITHOUT_POSTWRITES']
MAX_FLOAT = struct.unpack('f', bytes.fromhex('ffff7f7f'))[0]
MAX_DOUBLE = sys.float_info.max
SHIELD_REF = 'reference-evidence/twilight-minoshroom-knight-244.json'


def at_start(path):
    return subprocess.check_output(['git', 'show', START + ':' +
        Path(path).relative_to(ROOT).as_posix()], cwd=ROOT)


def selected(review):
    return [e for e in review['effects'] if e['review_checkpoint'] == CHECKPOINT]


def validate_records(review, note, ledger):
    effects, paths = review['effects'], review['paths']
    assert len(effects) == len({e['id'] for e in effects})
    assert len(paths) == len({p['id'] for p in paths})
    assert effects == sorted(effects, key=lambda e: e['id'])
    assert paths == sorted(paths, key=lambda p: p['id'])
    new = selected(review)
    assert {e['id'] for e in new} == {'cataclysm:ignited_revenant_' + k for k in KEYS}
    pids, eids = {p['id'] for p in paths}, {e['id'] for e in effects}
    for e in new:
        assert e['mod_key'] == 'cataclysm' and e['primary_classification'] in KINDS
        assert e['inspection_status'] == 'STATIC_REVIEWED' and not e['unresolved_ambiguities']
        for k in ['actual_behavior','source_actor','primary_test_source','components',
                  'implementation','delivery_paths','closest_vanilla_equivalent','hurt_return_dependency']:
            assert e[k], (e['id'], k)
        assert not {'stage_scaling_needed','stage_policy','stage_multiplier','stage_eligibility',
                    'stage_cap','stage_floor','runtime_hook'} & e.keys()
        assert set(e['delivery_paths']) <= pids
        observations = []
        for c in e['components']:
            assert c['primitive'] and c['formula'] and c['native_boundary'] and c['vanilla_relation']
            assert set(c['numerical_parameters']) == set(c['parameter_units'])
            for p, v in c['numerical_parameters'].items():
                assert isinstance(v, (int,float)) and not isinstance(v,bool) and math.isfinite(v)
                observations.append(dict(primitive=c['primitive'],parameter=p,native_value=v,
                    native_formula=c['formula'],units=c['parameter_units'][p],boundary=c['native_boundary']))
        assert observations == e['numeric_observations']
        candidates = e['scalable_parameter_candidates']
        assert candidates == sorted(candidates, key=lambda c: (c['primitive'],c['parameters']))
        seen = set()
        for c in candidates:
            assert len(c['parameters']) == 1
            p = c['parameters'][0]
            assert (c['primitive'],p) not in seen
            seen.add((c['primitive'],p))
            owners = [x for x in e['components'] if x['primitive']==c['primitive'] and p in x['numerical_parameters']]
            assert len(owners) == 1, 'Candidate lost its native primitive'
            owner = owners[0]
            assert c['native_value'] == owner['numerical_parameters'][p]
            assert c['native_formula'] == owner['formula']
            assert c['units'] == owner['parameter_units'][p]
            assert c['native_boundary'] == owner['native_boundary']
        if e['id'] != 'cataclysm:ignited_revenant_falling_motion':
            assert not candidates, 'Native defense/state/encounter constants are not automatic scalar candidates'
    new_paths = [p for p in paths if p['id'].startswith('cataclysm:ignited-revenant-admission:')]
    assert len(new_paths) == 10
    for p in new_paths:
        assert p['mod_key']=='cataclysm' and p['status']=='VERIFIED'
        assert p['primary_source'] and p['native_path'] and p['setup'] and p['implementation']
        assert p['labels'] and p['runtime_status']=='NOT_RUN'
        assert p['effect_ids'] and set(p['effect_ids']) <= eids
        for e in new:
            assert (p['id'] in e['delivery_paths']) == (e['id'] in p['effect_ids'])
    assert note['mechanic_packages'] == [dict(id=e['id'],primary_classification=e['primary_classification'],
        delivery_paths=e['delivery_paths'],numerical_candidates=e['scalable_parameter_candidates'],
        binary_gates=e['binary_parameters']) for e in new]
    summary = dict(new_mechanics=len(new),delivery_paths=len(new_paths),
        classifications=dict(sorted(Counter(e['primary_classification'] for e in new).items())),
        candidate_numeric_parameters=sum(len(c['parameters']) for e in new for c in e['scalable_parameter_candidates']),
        shared_binding_records=1,unresolved_subsection_ambiguities=0)
    assert summary == note['summary']
    assert summary['classifications'] == {'BINARY_MECHANIC':9,'CUSTOM_CONTROL':1}
    assert summary['candidate_numeric_parameters'] == 1
    assert review['status']==ledger['status']==note['status']=='PARTIAL'
    assert all(review[k] is False for k in ['semantic_discovery_complete','special_damage_discovery_complete',
                                           'source_mapping_complete','delivery_mapping_complete'])
    cat = next(t for t in ledger['targets'] if t['mod_key']=='cataclysm')
    assert cat['state']=='PARTIAL' and cat['semantic_effect_count']==len(effects)
    assert review['checkpoint']==ledger['checkpoint']==note['checkpoint']==CHECKPOINT
    assert review['exact_next_task']==note['exact_next_task']==cat['exact_next_task']
    assert note['exact_next_task'].startswith('R2k12b: Ignited Revenant offense/payload family.')
    assert note['remaining_ignited_revenant_work']==['R2k12b Ignited Revenant offense/payload family']
    assert not note['remaining_subsection_native_ambiguities'] and note['remaining_cataclysm_research']
    assert note['runtime_tests']==0
    assert all(note[k] is False for k in ['whole_mod_complete','stage_eligibility_decided','phase6_reopened',
        'production_changed','stage_changed','boss_testing_started','l2_testing_started','compatibility_fixes_started','phase7_started'])
    validate_contracts({e['id'].removeprefix('cataclysm:ignited_revenant_'):e for e in new},note)
    return summary


def validate_contracts(rows, note):
    flags = {
        'incoming_admission': dict(source_object_preserved=True,incoming_amount_rewritten=False,
            concrete_invulnerability_override=False,concrete_effect_override=False,concrete_post_hurt_callback=False,
            bypass_skips_concrete_prefilters=False,awakens_on_hurt_return=False,local_causing_entity_read=False),
        'shield_break_admission': dict(uses_direct_attacker=True,uses_causing_owner=False,uses_attribute_base=True,
            item_attribute_fallback_overwritten=True,checks_bypasses_shield=False,checks_bypasses_invulnerability=False,
            shield_break_local_server_guard=True,shield_break_depends_on_hurt=False,fourth_break_spills_damage=False,axe_test_is_item_class=True),
        'shield_block_admission': dict(block_uses_source_position=True,block_uses_causing_range=False,
            direct_piercing_arrow_bypasses=True,horizontal_projection_after_normalize=True,renormalizes_horizontal_vector=False,
            native_using_item_gate=False,block_local_server_guard=False,shield_callback_depends_on_hurt=False,
            callback_uses_direct_living=True,projectile_tag_suppresses_callback_only=True,
            default_shield_damage_callback_noop=True,default_blocked_by_shield_knockback_receiver='defender'),
        'shared_defense_bindings': dict(concrete_damage_cap_override=False,concrete_dps_cap_override=False,
            concrete_range_limit_override=False,concrete_nature_regen_override=False,concrete_heal_cooldown_override=False,
            damage_cap_is_bucket_capacity=True,dps_is_bucket_capacity=False,installed_defense_config_present=False,positive_shared_regen_delivery=False),
        'environment_admission': dict(registered_fire_immune=True,air_returns_argument=True,air_returns_native_max=False,
            incoming_entity_push=False,blanket_drowning_immunity_claimed=False,all_forced_motion_immunity_claimed=False,concrete_fluid_override=False),
        'falling_motion': dict(control_depends_on_hurt=False,uses_mob_effect=False,preserves_horizontal_velocity=True,
            fall_local_server_guard=False,fall_local_no_ai_guard=False,fall_target_gate=False),
        'combat_state_prerequisites': dict(initial_anger=False,initial_shield_counter=0,shield_counter_means_segments_lost=True,
            shield_setter_clamps=False,shield_setter_heals=False,anger_setter_resets_shields=False,raw_state_is_tno_stage=False,
            shield_gate_reads_progress=False,concrete_hp_phase_gate=False,offensive_execution_reviewed=False),
        'combat_persistence': dict(saved_anger=False,saved_shield_counter=False,saved_anger_progress=False,
            saved_attack_cooldowns=False,concrete_animation_saved=False,inherited_ia_life=False,generic_persistence_added=False),
        'encounter_setup': dict(constructor_health_is_heal_delivery=False,constructor_sets_home=False,
            constructor_sets_anger=False,constructor_sets_shield_counter=False,concrete_finalize_spawn_override=False,
            concrete_interaction_override=False,concrete_player_counter=False,explicit_armor_toughness_added=False,exhaustive_spawn_discovery_claimed=False),
        'arena_spawn_prerequisites': dict(marker_is_exact_match=True,marker_checks_bounding_box=False,
            marker_checks_spawnable_bounds=False,marker_has_creation_null_guard=False,marker_calls_finalize_spawn=False,
            marker_sets_home=False,marker_sets_anger=False,marker_sets_shield_counter=False,spawn_return_consumed=False,unrelated_markers_reviewed=False),
    }
    for key, fields in flags.items():
        for f, v in fields.items():
            assert rows[key][f] == v, (key,f)
    def params(key, prim):
        return next(c['numerical_parameters'] for c in rows[key]['components'] if c['primitive']==prim)
    assert rows['incoming_admission']['admission_order']==note['admission_order']['concrete']==ORDER
    assert params('shield_break_admission','SHIELD_BREAK_ADMISSION')==dict(item_damage_offset=1.0,threshold_divisor=2.0,shield_limit=4,segment_step=1)
    assert params('shield_block_admission','SHIELD_ADMISSION')==dict(shield_limit=4,dot_threshold=0.0)
    assert params('shield_block_admission','KNOCKBACK')==dict(strength=.5)
    assert params('shared_defense_bindings','DAMAGE_CAP')==dict(per_hit_cap=MAX_FLOAT)
    assert params('shared_defense_bindings','DPS_BUCKET')==dict(capacity=MAX_FLOAT,dps_cap=MAX_FLOAT,drain_divisor=20)
    assert params('shared_defense_bindings','RANGE_ADMISSION')==dict(range_limit=MAX_DOUBLE)
    assert params('shared_defense_bindings','NATIVE_REGEN_BINDING')==dict(amount=0.0)
    assert params('shared_defense_bindings','REGEN_ADMISSION_TIMER')==dict(heal_cooldown=200)
    assert params('falling_motion','FORCED_MOVEMENT')==dict(vertical_factor=.6)
    assert params('combat_state_prerequisites','SHIELD_STATE')==dict(default_counter=0,shield_limit=4,step=1)
    f32=lambda x:struct.unpack('f',struct.pack('f',x))[0]
    assert params('encounter_setup','NATIVE_ATTRIBUTE_SETUP')==dict(follow_range=20.0,movement_speed=f32(.28),
        attack_damage=6.0,max_health=80.0,armor=12.0,step_height=1.5,knockback_resistance=1.0,health_multiplier=1.0,attack_multiplier=1.0)
    assert params('encounter_setup','ENTITY_TYPE_SETUP')==dict(width=f32(1.6),height=f32(2.8))
    assert params('arena_spawn_prerequisites','ENCOUNTER_SPAWN')==dict(block_update_flag=2,yaw=180.0,pitch=180.0)
    for name,v in [('DamageCap',MAX_FLOAT),('DpsCap',MAX_FLOAT),('RangeLimit',MAX_DOUBLE),('NatureRegen',0.0),('HealCooldown',200)]:
        b=note['concrete_bindings'][name]
        assert b['inherited'] is True and b['native_value']==v and b['candidate_observation_added'] is False
    assert note['installed_config']==dict(health_multiplier=1.0,attack_multiplier=1.0,defense_config_present=False)


def validate_preservation(review, note, ledger):
    assert note['starting_sha']==START
    old=json.loads(at_start(REVIEW))
    assert len(old['effects'])==320 and len(old['paths'])==326
    assert [e for e in review['effects'] if e['review_checkpoint']!=CHECKPOINT]==old['effects']
    assert [p for p in review['paths'] if not p['id'].startswith('cataclysm:ignited-revenant-admission:')]==old['paths']
    mutable={'effects','paths','checkpoint','scope','notes_file','exact_next_task','protected_checkpoints'}
    assert {k:v for k,v in review.items() if k not in mutable}=={k:v for k,v in old.items() if k not in mutable}
    assert review['protected_checkpoints']==old['protected_checkpoints']+[dict(checkpoint=old['checkpoint'],notes_file=old['notes_file'])]
    for ref in note['reference_files']:
        path=OUT/ref['file']
        assert hashlib.sha256(path.read_bytes()).hexdigest()==ref['sha256'],ref['file']
        if ref['usage']=='LOCKED_REUSED':
            assert path.read_bytes()==at_start(path),ref['file']
    lock=note['protected_r2k11b']
    assert lock['file']=='cataclysm-r2k11b-ender-golem-offense.json'
    assert hashlib.sha256((OUT/lock['file']).read_bytes()).hexdigest()==lock['sha256']
    previous=json.loads(at_start(LEDGER))
    assert [t for t in ledger['targets'] if t['mod_key']!='cataclysm']==[t for t in previous['targets'] if t['mod_key']!='cataclysm']
    assert {k:v for k,v in ledger.items() if k not in ['targets','checkpoint']}=={k:v for k,v in previous.items() if k not in ['targets','checkpoint']}


def validate_native_boundaries(evidence):
    def witness(n):
        return next(w for w in evidence['witnesses'] if w['entry']==PKG+n+'.class')
    def body(n,m):
        return next(mo['instructions'] for mo in witness(n)['methods'] if mo['name']==m)
    def calls(ins,name):
        return [i['offset'] for i in ins if name in str(i['operand'])]
    def at(ins,off):
        return next(i for i in ins if i['offset']==off)
    hurt=body(R,'hurt')
    assert calls(hurt,'.getDirectEntity(')==[1] and not calls(hurt,'.getEntity(')
    assert calls(hurt,'isClientSide')==[9] and at(hurt,12)['branch_target']==110
    assert at(hurt,23)['operand']=='net/minecraft/world/entity/LivingEntity'
    assert at(hurt,47)['operand']=='net/minecraft/world/item/AxeItem'
    assert at(hurt,61)['operand']==1.0 and at(hurt,71)['operand']==2.0
    assert at(hurt,77)['opcode']=='0x9b' and at(hurt,85)['opcode']=='0xa2'
    assert at(hurt,84)['operand']==4 and calls(hurt,'.setShieldDurability(')==[105]
    assert at(hurt,108)['operand']==0 and at(hurt,109)['opcode']=='0xac'
    assert calls(hurt,'.canBlockDamageSource(')==[118] and calls(hurt,'.hurtCurrentlyUsedShield(')==[126]
    assert calls(hurt,'DamageTypeTags.IS_PROJECTILE')==[130] and at(hurt,136)['branch_target']==154
    assert calls(hurt,'.blockUsingShield(')==[151] and at(hurt,166)['operand']==0
    assert calls(hurt,'.hurt(')==[171] and at(hurt,174)['opcode']=='0xac'
    assert not calls(hurt,'BYPASSES_INVULNERABILITY') and not calls(hurt,'BYPASSES_SHIELD')
    helper=body(R,'getApproximateAttackDamageWithItem')
    assert calls(helper,'.getOrDefault(')==[7] and calls(helper,'.getAttributeModifiers(')==[15]
    assert calls(helper,'.getAttributeBaseValue(')==[24] and not calls(helper,'.getAttributeValue(')
    assert calls(helper,'EquipmentSlot.MAINHAND')==[27] and calls(helper,'.compute(')==[30]
    shield=body(R,'canBlockDamageSource')
    assert calls(shield,'.getDirectEntity(')==[1] and calls(shield,'.getPierceLevel(')==[22]
    assert calls(shield,'BYPASSES_SHIELD')==[31] and not calls(shield,'BYPASSES_INVULNERABILITY')
    assert at(shield,25)['opcode']=='0x9e' and at(shield,55)['operand']==4
    assert calls(shield,'.getSourcePosition(')==[60] and not calls(shield,'.getEntity(')
    assert calls(shield,'.normalize(')==[86] and at(shield,100)['operand']==0.0
    assert calls(shield,'.dot(')==[115] and at(shield,120)['opcode']=='0x9c'
    assert not calls(shield,'.isUsingItem(') and not calls(shield,'isClientSide')
    save,load=body(R,'addAdditionalSaveData'),body(R,'readAdditionalSaveData')
    assert [i['opcode'] for i in save]==[i['opcode'] for i in load]==['0x2a','0x2b','0xb7','0xb1']
    assert not any('put' in str(i['operand']) or '.getBoolean(' in str(i['operand']) for i in save+load)
    for m in ['setIsAnger','setShieldDurability']:
        ins=body(R,m)
        assert len(calls(ins,'SynchedEntityData.set('))==1
        assert not any('branch_target' in i for i in ins)
        assert not calls(ins,'.heal(') and not calls(ins,'.setShieldDurability(')
    define=body(R,'defineSynchedData')
    assert at(define,9)['operand']==at(define,21)['operand']==0
    tick=body(R,'tick')
    assert at(tick,13)['branch_target']==at(tick,25)['branch_target']==44
    assert at(tick,34)['operand']==.6 and calls(tick,'.setDeltaMovement(')==[41]
    assert at(tick,63)['operand']==5.0 and at(tick,75)['operand']==at(tick,101)['operand']==1.0
    assert not calls(tick,'.hurt(') and not calls(tick,'.heal(') and not calls(tick,'isClientSide')
    assert not calls(tick,'.isNoAi(') and not calls(tick,'cooldown') and not calls(tick,'launchbone')
    for goal in [R+'$Ignited_Revenant_Goal',R+'$ShootGoal']:
        for m,value in [('start',1),('stop',0)]:
            ins=body(goal,m)
            assert at(ins,1)['opcode']=='0xb7' and at(ins,8)['operand']==value
            assert calls(ins,'.setIsAnger(')==[9] and not calls(ins,'.hurt(')
    air=body(R,'decreaseAirSupply')
    assert [i['opcode'] for i in air]==['0x1b','0xac']
    factory=body(REGISTRY,'lambda$static$22')
    assert calls(factory,'.fireImmune(')==[20] and at(factory,23)['operand']=='cataclysm:ignited_revenant'
    assert {b['index'] for b in witness(REGISTRY)['registration_bootstraps']}=={91,136}
    assert any(PKG+R+'.<init>' in b['arguments'][1] for b in witness(REGISTRY)['registration_bootstraps'])
    marker=body(PIECE,'handleDataMarker')
    assert at(marker,0)['operand']=='revenant' and calls(marker,'.equals(')==[3]
    assert at(marker,17)['operand']==2 and calls(marker,'.setBlock(')==[18]
    assert calls(marker,'.create(')==[39] and calls(marker,'.moveTo(')==[54] and calls(marker,'.addFreshEntity(')==[60]
    assert at(marker,50)['operand']==at(marker,52)['operand']==180.0 and at(marker,65)['opcode']=='0x57'
    assert not any(i['opcode'] in {'0xc6','0xc7'} for i in marker)
    assert not any(calls(marker,n) for n in ['.isInside(','.isInSpawnableBounds(','.finalizeSpawn(','.setHomePos(','.setIsAnger(','.setShieldDurability('])


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
    assert len(new_methods)==25
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
    for e in selected(review):
        for p in e['implementation']:
            w=next(w for w in sources[p['evidence_file']]['witnesses'] if w['id']==p['witness_id'])
            assert p['entry']==w['entry'] and set(p['methods'])<={m['name'] for m in w.get('methods',[])}
        for p in e.get('reference_evidence',[]):
            assert p['evidence_file']==SHIELD_REF
            w=next(w for w in read_json(OUT/SHIELD_REF)['witnesses'] if w['entry']==p['entry'])
            assert set(p['methods'])<={m['name'] for m in w['methods']}
    root=next(w for w in evidence['witnesses'] if w['entry']==PKG+R+'.class')
    chain=[root['class_name']]
    for name in [R,'entity/AnimationMonster/BossMonsters/LLibrary_Boss_Monster',
                 'entity/AnimationMonster/LLibrary_Monster','entity/etc/Animation_Monsters']:
        chain.append(census[PKG+name+'.class']['superclass'])
    assert note['hierarchy']==chain, 'Exact native inheritance chain must include the animation intermediary'
    absent={'isInvulnerableTo','DamageCap','DpsCap','RangeLimit','NatureRegen','HealCooldown','canBeAffected',
            'finalizeSpawn','mobInteract','PlayerCounter','isAffectedByFluids','isPushedByFluid','canStandOnFluid'}
    assert not absent & set(root['declared_method_names'])
    assert not {'getAnimations','launchbone1','launchbone2','launchbone3','onDeathAIUpdate','repelEntities','isAlliedTo','spawnAtLocation'} & {m['name'] for m in root['methods']}
    assert note['tooling']['new_native_witnesses']==5 and note['tooling']['new_method_witnesses']==25
    assert not note['tooling']['reused_evidence_regenerated'] and not note['tooling']['recursive_jar_scan']
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
        protected_shared_status_prior_families_ender_golem='BYTE_IDENTICAL',
        pinned_jar_reproduction='PASS' if jar_path else 'NOT_REQUESTED')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jar',type=Path,help='Reproduce only new witnesses against the exact pinned JAR')
    print(json.dumps(validate(parser.parse_args().jar),indent=2))
