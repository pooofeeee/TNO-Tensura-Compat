"""Focused, read-only R2k10a validation and optional pinned-JAR reproduction."""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import subprocess

from catalog_common import OUT, ROOT, read_json
from collect_cataclysm_scylla_admission import (
    EVIDENCE_FILE, FRAGMENTS, METHODS, S, PHASE, SLEEP, WAKE, PARRY, SWING, PKG, REGISTRY,
    SPEC_FILE, collect, specification,
)

START = 'e2a8682bc0f9a08dc2039b117d2193bd9c896cf7'
CHECKPOINT = 'R2k10a-cataclysm-scylla-admission-complete'
NOTE = OUT / 'cataclysm-r2k10a-scylla-admission.json'
REVIEW = OUT / 'mod-reviews/cataclysm.json'
LEDGER = OUT / 'mod-completion-ledger.json'
BOSS_BASE = 'entity/InternalAnimationMonster/IABossMonsters/IABoss_monster'
KINDS = {'VANILLA_DIRECT', 'VANILLA_EQUIVALENT', 'VANILLA_LIKE_EXTENDED',
         'VANILLA_COMPOSITE', 'CUSTOM_DAMAGE', 'CUSTOM_STATUS', 'CUSTOM_CONTROL',
         'CUSTOM_RESOURCE', 'BINARY_MECHANIC'}
KEYS = {
    'activation_encounter',
    'activation_sleep_prerequisites',
    'combat_persistence',
    'encounter_setup',
    'environment_admission',
    'incoming_admission',
    'incoming_damage_notification',
    'nature_regen_binding',
    'parry_admission',
    'parry_state_prerequisites',
    'phase_state_prerequisites',
    'raw_combat_state',
    'shared_defense_bindings',
}
ORDER = ['UNLESS_INVULNERABILITY_BYPASS_FACE_SERVER_PARRY_COUNT_OR_RNG_REJECT', 'UNLESS_INVULNERABILITY_BYPASS_FACE_SERVER_STATE19_TICKS2_TO10_REJECT', 'UNLESS_INVULNERABILITY_BYPASS_PHASE_STATE21_OR22_REJECT', 'UNLESS_INVULNERABILITY_BYPASS_SLEEP_STATE23_OR24_REJECT', 'ARM_DESTROY_BLOCKS20_IF_NONPOSITIVE', 'SHARED_HURT_SAME_SOURCE_AND_AMOUNT', 'TRUE_HURT_FACING_COUNT_LT18_INCREMENT_PROJECTILE2_ELSE1', 'RETURN_SHARED_HURT_RESULT']


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
    assert {e['id'] for e in new} == {'cataclysm:scylla_' + k for k in KEYS}
    pids, eids = {p['id'] for p in paths}, {e['id'] for e in effects}
    for e in new:
        assert e['mod_key'] == 'cataclysm' and e['primary_classification'] in KINDS
        assert e['inspection_status'] == 'STATIC_REVIEWED' and not e['unresolved_ambiguities']
        assert e['actual_behavior'] and e['source_actor'] and e['primary_test_source']
        assert e['components'] and e['implementation'] and e['delivery_paths']
        assert not {'stage_scaling_needed','stage_policy','stage_multiplier','runtime_hook'} & e.keys()
        assert set(e['delivery_paths']) <= pids
        observations = []
        for c in e['components']:
            assert c['primitive'] and c['formula'] and c['native_boundary']
            assert set(c['numerical_parameters']) == set(c['parameter_units'])
            for p, v in c['numerical_parameters'].items():
                assert isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)
                observations.append(dict(primitive=c['primitive'], parameter=p, native_value=v,
                    native_formula=c['formula'], units=c['parameter_units'][p], boundary=c['native_boundary']))
        assert observations == e['numeric_observations']
        candidates = e['scalable_parameter_candidates']
        assert candidates == sorted(candidates, key=lambda c: (c['primitive'], c['parameters']))
        for c in candidates:
            assert len(c['parameters']) == 1
            p = c['parameters'][0]
            owners = [x for x in e['components'] if x['primitive'] == c['primitive']
                      and p in x['numerical_parameters']]
            assert len(owners) == 1
            owner = owners[0]
            assert c['native_value'] == owner['numerical_parameters'][p]
            assert c['native_formula'] == owner['formula']
            assert c['units'] == owner['parameter_units'][p]
            assert c['native_boundary'] == owner['native_boundary']
        if e['id'] != 'cataclysm:scylla_nature_regen_binding':
            assert not candidates, 'Native admission/setup constants are not outgoing scalar candidates'
    new_paths = [p for p in paths if p['id'].startswith('cataclysm:scylla-admission:')]
    assert len(new_paths) == 13
    for p in new_paths:
        assert p['mod_key'] == 'cataclysm' and p['status'] == 'VERIFIED'
        assert p['primary_source'] and p['native_path'] and p['setup'] and p['implementation']
        assert p['labels'] and p['runtime_status'] == 'NOT_RUN'
        assert p['effect_ids'] and set(p['effect_ids']) <= eids
        for e in new:
            assert (p['id'] in e['delivery_paths']) == (e['id'] in p['effect_ids'])
    expected_packages = [dict(id=e['id'], primary_classification=e['primary_classification'],
        delivery_paths=e['delivery_paths'], numerical_candidates=[{k: c[k] for k in
            ['primitive', 'parameters', 'native_value', 'units', 'native_boundary']}
            for c in e['scalable_parameter_candidates']], binary_gates=e['binary_parameters']) for e in new]
    assert note['mechanic_packages'] == expected_packages
    summary = dict(new_mechanics=len(new), delivery_paths=len(new_paths),
        classifications=dict(sorted(Counter(e['primary_classification'] for e in new).items())),
        candidate_numeric_parameters=sum(len(c['parameters']) for e in new for c in e['scalable_parameter_candidates']),
        shared_binding_records=1, unresolved_subsection_ambiguities=0)
    assert summary == note['summary']
    assert summary['classifications'] == {'BINARY_MECHANIC': 12, 'VANILLA_DIRECT': 1}
    assert summary['candidate_numeric_parameters'] == 1
    assert review['status'] == ledger['status'] == note['status'] == 'PARTIAL'
    assert all(review[k] is False for k in ['semantic_discovery_complete',
        'special_damage_discovery_complete', 'source_mapping_complete', 'delivery_mapping_complete'])
    cat = next(t for t in ledger['targets'] if t['mod_key'] == 'cataclysm')
    assert cat['state'] == 'PARTIAL' and cat['semantic_effect_count'] == len(effects)
    assert review['checkpoint'] == ledger['checkpoint'] == note['checkpoint'] == CHECKPOINT
    assert review['exact_next_task'] == note['exact_next_task'] == cat['exact_next_task']
    assert note['exact_next_task'].startswith('R2k10b: Scylla offense/payload family.')
    assert note['remaining_scylla_work'] and not note['remaining_subsection_native_ambiguities']
    assert note['whole_mod_complete'] is False and note['runtime_tests'] == 0
    assert all(note[k] is False for k in ['stage_eligibility_decided', 'phase6_reopened',
        'production_changed', 'stage_changed', 'boss_testing_started', 'l2_testing_started',
        'compatibility_fixes_started', 'phase7_started'])
    validate_contracts({e['id'].removeprefix('cataclysm:scylla_'): e for e in new}, note)
    return summary


def validate_contracts(rows, note):
    def values(key, primitive):
        return next(c['numerical_parameters'] for c in rows[key]['components'] if c['primitive'] == primitive)

    expected = {
        'incoming_admission': dict(source_object_preserved=True, incoming_amount_rewritten=False,
            timer_armed_before_shared_hurt=True, timer_requires_hurt_success=False,
            bypass_skips_all_concrete_rejections=True, bypass_skips_postwrite=False,
            concrete_invulnerability_override=False, concrete_effect_override=False, concrete_retry_override=False),
        'parry_admission': dict(facing_uses_source_position=True, facing_uses_causing_range=False,
            forced_parry_checks_cooldown=False, rng_parry_checks_cooldown=True, parry_is_shield_item=False),
        'parry_state_prerequisites': dict(postwrite_local_server_guard=False, postwrite_requires_parry_window=False,
            postwrite_can_overshoot18=True, reset_cooldown_clamps_counter=False, goal_tick_fragment_offense_reviewed=False),
        'shared_defense_bindings': dict(damage_cap_is_bucket_capacity=True, dps_is_bucket_capacity=False,
            range_narrows_float_before_double=False, configured_dps_limit_time_used=False,
            concrete_heal_cooldown_override=False),
        'incoming_damage_notification': dict(notification_hurt_return_consumed=False,
            notification_has_local_server_guard=False, notification_adds_outgoing_payload=False),
        'environment_admission': dict(registered_fire_immune=True, air_returns_argument=True,
            air_returns_native_max=False, fluid_push=False, blanket_drowning_immunity_claimed=False,
            concrete_invulnerability_override=False),
        'phase_state_prerequisites': dict(phase_latched_at_goal_start=True, phase_latched_at_ai_step=False,
            phase_goal_local_server_guard=False, phase_goal_requires_target=False, phase_goal_requires_alive=False,
            phase_goal_local_no_ai_gate=False, raw_phase_clamped=False, healing_clears_phase=False),
        'activation_sleep_prerequisites': dict(act_false_equals_sleep=False, true_act_setter_wakes_directly=False,
            false_act_setter_forces23=True, fresh_constructor_forces23=False, wake_has_added_damage=False),
        'raw_combat_state': dict(raw_integer_setters_clamp=False, raw_setters_heal=False,
            flight_gravity_has_local_server_guard=False),
        'combat_persistence': dict(act_missing_forces23=True, saved_parry_count=False,
            saved_parry_cooldown=False, saved_attack_state=False, saved_flying=False,
            saved_eye=False, saved_chain_anchor=False, saved_anchor_id=False,
            saved_terrain_timer=False, generic_persistence_added=False),
        'encounter_setup': dict(attributes_apply_to='cataclysm:scylla', constructor_sets_home=False,
            constructor_calls_set_act=False, constructor_sets_phase=False, configured_health_is_heal_delivery=False,
            explicit_armor_toughness_added=False, finalize_sets_home=False, finalize_counts_players=False,
            spawn_activation_reasons=['COMMAND','SPAWN_EGG','IS_SPAWNER','DISPENSER']),
        'activation_encounter': dict(interaction_local_server_guard=False, requires_specific_item=False,
            consumes_item=False, activation_sets_home=True, activation_heals_to_max=True,
            activation_counts_players=True, activation_directly_sets_attack_state=False,
            full_heal_is_stage_candidate=False),
    }
    for key, fields in expected.items():
        for name, value in fields.items():
            assert rows[key][name] == value, (key, name)
    assert note['admission_order']['concrete'] == rows['incoming_admission']['admission_order'] == ORDER
    assert values('incoming_admission','TERRAIN_RESPONSE_ARMING') == dict(arming_ticks=20)
    assert values('parry_admission','PARRY_ADMISSION') == dict(count_threshold=18, sentinel=25,
        random_denominator=100.0, chance_coefficient=5, states12_after_tick=35,
        state3_after_tick=51, state4_after_tick=50, state19_first_tick=2, state19_last_tick=10)
    assert values('parry_state_prerequisites','NATIVE_PARRY_STATE') == dict(projectile_increment=2,
        other_increment=1, accepting_count_limit=18, sentinel=25, parry_goal_max_tick=15,
        reset_count=0, reset_cooldown=100)
    assert values('incoming_damage_notification','NATIVE_DAMAGE_NOTIFICATION') == dict(
        invulnerable_time=20,hurt_duration=10,callback_requested_damage=0.0)
    config = read_json(OUT/'cataclysm-installed-common-config.json')['values']['mobs']['scylla']
    bindings = note['concrete_bindings']
    assert bindings == rows['shared_defense_bindings']['concrete_bindings']
    for key, field, value in [
        ('DamageCap','damageCap',config['cap_config']['damage_cap']),
        ('DpsCap','dpsCap',config['cap_config']['dps_cap']),
        ('RangeLimit','rangeCap',config['cap_config']['range_cap']),
        ('NatureRegen','natureHeal',config['nature_heal_config']['nature_heal']),
        ('configuredDpsLimitTime','dpsLimitTime',config['cap_config']['dps_limit_time'])]:
        assert bindings[key]['config_field'] == 'Scylla.' + field
        assert bindings[key]['installed_value'] == value
        assert bindings[key]['shared_boundary']
    assert bindings['HealCooldown']['inherited'] is True and bindings['HealCooldown']['native_value'] == 200
    assert bindings['RangeLimit']['native_cast'] == 'double(config), no float narrowing'
    assert values('shared_defense_bindings','DAMAGE_CAP') == dict(per_hit_cap=21.0)
    assert values('shared_defense_bindings','DPS_BUCKET') == dict(capacity=21.0,dps_cap=13.0,drain_divisor=20)
    assert values('shared_defense_bindings','RANGE_ADMISSION') == dict(range_limit=12.0)
    assert values('shared_defense_bindings','REGEN_ADMISSION_TIMER') == dict(heal_cooldown=200)
    regen = rows['nature_regen_binding']
    assert regen['record_kind'] == 'SHARED_BINDING' and regen['binding_of'] == 'cataclysm:shared_heal'
    assert any(p['id'] == regen['binding_of'] for p in read_json(OUT/regen['binding_contract_file'])['mechanic_packages'])
    assert regen['adds_second_heal'] is False and values('nature_regen_binding','NATIVE_HEAL') == dict(amount=25.0)
    import struct
    f32 = lambda x: struct.unpack('f', struct.pack('f', x))[0]
    assert values('phase_state_prerequisites','PHASE_STATE') == dict(phase1=1,phase2=2,
        phase1_attack_state=21,phase2_attack_state=22,phase1_health_ratio=f32(.6666667),
        phase2_health_ratio=f32(.33333334),phase1_max_tick=55,phase2_max_tick=68)
    assert values('activation_sleep_prerequisites','ACTIVATION_STATE') == dict(sleep_state=23,wake_state=24,idle_state=0,wake_max_tick=40)
    assert rows['raw_combat_state']['default_state'] == dict(eye=False,chain_anchor=False,
        flying=False,act=False,phase=0,parry_count=0,anchor_uuid=None,anchor_id=-1)
    assert rows['combat_persistence']['saved_concrete_keys'] == ['AnchorUUID','Phase','Act']
    assert rows['combat_persistence']['missing_key_defaults'] == dict(Phase=0,Act=False)
    assert values('encounter_setup','NATIVE_ATTRIBUTE_SETUP') == dict(base_health=390.0,
        base_attack_damage=18.0,armor=12.0,knockback_resistance=1.0,health_multiplier=1.0,attack_multiplier=1.0)
    assert rows['encounter_setup']['registered_dimensions'] == dict(width=f32(1.4),height=3.0)
    assert rows['activation_encounter']['activation_order'] == ['IF_ACT_FALSE',
        'SET_HOME_CURRENT_GLOBAL_POS','SET_ACT_TRUE','NATIVE_HEAL_MAX_HEALTH','NATIVE_PLAYER_COUNTER',
        'RETURN_SUCCESS_ELSE_PARENT_INTERACTION']


def validate_preservation(review, note, ledger):
    assert note['starting_sha'] == START
    old = json.loads(at_start(REVIEW))
    assert [e for e in review['effects'] if e['review_checkpoint'] != CHECKPOINT] == old['effects']
    assert [p for p in review['paths'] if not p['id'].startswith('cataclysm:scylla-admission:')] == old['paths']
    mutable = {'effects', 'paths', 'checkpoint', 'scope', 'notes_file', 'exact_next_task', 'protected_checkpoints'}
    assert {k: v for k, v in review.items() if k not in mutable} == {k: v for k, v in old.items() if k not in mutable}
    assert review['protected_checkpoints'] == old['protected_checkpoints'] + [
        dict(checkpoint=old['checkpoint'], notes_file=old['notes_file'])]
    assert note['previous_checkpoint'] == old['checkpoint']
    previous_note = json.loads(at_start(OUT / old['notes_file']))
    assert {r['file'] for r in note['reference_files'] if r['usage'] == 'LOCKED_REUSED'} >= {
        old['notes_file'], *(r['file'] for r in previous_note['reference_files'])}
    assert note['protected_r2k9b'] == dict(file=old['notes_file'],
        sha256=hashlib.sha256(at_start(OUT / old['notes_file'])).hexdigest())
    for reference in note['reference_files']:
        path = OUT / reference['file']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == reference['sha256'], reference['file']
        if reference['usage'] == 'LOCKED_REUSED':
            assert path.read_bytes() == at_start(path), reference['file']
    previous = json.loads(at_start(LEDGER))
    assert [t for t in ledger['targets'] if t['mod_key'] != 'cataclysm'] == [
        t for t in previous['targets'] if t['mod_key'] != 'cataclysm']
    assert {k: v for k, v in ledger.items() if k not in ['targets', 'checkpoint']} == {
        k: v for k, v in previous.items() if k not in ['targets', 'checkpoint']}


def validate_evidence(review, note, jar_path=None):
    assert read_json(SPEC_FILE) == specification()
    evidence = read_json(EVIDENCE_FILE)
    assert len(evidence['witnesses']) == 7
    assert {w['entry'] for w in evidence['witnesses']} == {PKG+n+'.class' for n in METHODS}
    if jar_path is not None:
        assert evidence == collect(jar_path), 'Pinned-JAR witnesses did not reproduce'
    census = {c['entry']:c for c in read_json(OUT/'cataclysm-source-census.json')['classes']}
    sources = {r['file']:read_json(OUT/r['file']) for r in note['reference_files']
        if r['file'].startswith('native-evidence/')}
    new_methods = {(w['entry'],m['name'],m['descriptor']):m
        for w in evidence['witnesses'] for m in w.get('methods',[])}
    assert len(new_methods) == 57
    for f, data in sources.items():
        if f == EVIDENCE_FILE.relative_to(OUT).as_posix():
            continue
        for witness in data['witnesses']:
            for old in witness.get('methods',[]):
                new = new_methods.get((witness['entry'],old['name'],old['descriptor']))
                if new is not None:
                    assert 'instruction_offset_ranges' in new, 'Previously captured full method duplicated'
                    assert new['code_sha256'] == old['code_sha256']
                    assert not {i['offset'] for i in new['instructions']} & {
                        i['offset'] for i in old['instructions']}, 'Previously captured fragment duplicated'
    for w in evidence['witnesses']:
        assert w['jar_sha256'] == note['tooling']['jar_sha256']
        assert w['entry_sha256'] == census[w['entry']]['entry_sha256']
        assert w['superclass'] == census[w['entry']]['superclass']
        for m in w.get('methods',[]):
            if 'instruction_offset_ranges' in m:
                assert m['instruction_offset_ranges'] == FRAGMENTS[w['entry'][len(PKG):-6]][m['name']]
    for e in selected(review):
        for pointer in e['implementation']:
            w = next(w for w in sources[pointer['evidence_file']]['witnesses'] if w['id']==pointer['witness_id'])
            assert pointer['entry']==w['entry']
            assert set(pointer['methods']) <= {m['name'] for m in w.get('methods',[])}
    entry = PKG+S+'.class'
    w = next(w for w in evidence['witnesses'] if w['entry']==entry)
    assert not {'isInvulnerableTo','canBeAffected','HealCooldown','DpsMulti','Retry'} & set(w['declared_method_names'])
    assert not {'aiStep','AreaAttack','SpinDamage','Whip','Stormknockback','floatScylla',
        'LightningAttack','SummonWave','blockbreak','AfterDefeatBoss','die','deathtimer'} & {m['name'] for m in w['methods']}
    assert note['hierarchy'] == [PKG+n for n in [S,BOSS_BASE,
        'entity/InternalAnimationMonster/Internal_Animation_Monster','entity/etc/Animation_Monsters']] + ['net/minecraft/world/entity/monster/Monster']
    for child, parent in zip(note['hierarchy'],note['hierarchy'][1:]):
        assert census[child+'.class']['superclass'] == parent
    assert note['tooling']['new_native_witnesses']==7 and note['tooling']['new_method_witnesses']==57
    assert not note['tooling']['recursive_jar_scan'] and not note['tooling']['reused_evidence_regenerated']
    validate_native_boundaries(evidence)
    return len(new_methods)


def validate_native_boundaries(evidence):
    def body(name, method):
        w = next(w for w in evidence['witnesses'] if w['entry']==PKG+name+'.class')
        return next(m['instructions'] for m in w['methods'] if m['name']==method)

    def calls(ins, name):
        return [i['offset'] for i in ins if name in str(i.get('operand',''))]

    def op(ins, offset):
        return next(i['opcode'] for i in ins if i['offset']==offset)

    hurt = body(S,'hurt')
    assert calls(hurt,'DamageTypeTags.BYPASSES_INVULNERABILITY') == [1]
    assert calls(hurt,'.setParryCount(') == [47,109,275]
    assert calls(hurt,'.CanParryState(') == [29]
    assert calls(hurt,'.isSleep(') == [205]
    assert calls(hurt,'.destroyBlocksTickI') == [214,223]
    assert calls(hurt,'IABoss_monster.hurt(') == [229]
    assert calls(hurt,'.canBlockFaceSource(') == [12,239]
    assert calls(hurt,'DamageTypeTags.IS_PROJECTILE') == [260]
    assert calls(hurt,'.parry_cooldownI') == [100]  # no forced-parry or postwrite cooldown test
    assert calls(hurt,'isClientSide') == [22]  # postwrite has no local side test
    assert op(hurt,234)=='0x99'  # shared return must be true for postwrite
    assert not calls(hurt,'.getDirectEntity(') and not calls(hurt,'.getEntity(')
    face = body(S,'canBlockFaceSource')
    assert calls(face,'.getSourcePosition(')==[8] and calls(face,'.isNoAi(')==[1]
    assert calls(face,'.dot(')==[62] and not calls(face,'.calculateRange(')
    notification = body(S,'handleDamageEvent')
    assert calls(notification,'.generic(')==[86] and calls(notification,'.hurt(')==[90]
    assert op(notification,93)=='0x57' and not calls(notification,'isClientSide')
    assert calls(notification,'.lastDamageSourceL')==[96]
    activation = body(S,'mobInteract')
    assert calls(activation,'.setHomePos(')==[22]
    assert calls(activation,'.setAct(')==[27]
    assert calls(activation,'.heal(')==[35]
    assert calls(activation,'.PlayerCounter(')==[43]
    assert not calls(activation,'isClientSide') and not calls(activation,'.getItemInHand(')
    assert not calls(activation,'.setAttackState(')
    act = body(S,'setAct')
    assert calls(act,'.setAttackState(')==[29] and op(act,23)=='0x9a'  # true branch skips state23
    spawn = body(S,'finalizeSpawn')
    assert calls(spawn,'.setAct(')==[30] and calls(spawn,'IABoss_monster.finalizeSpawn(')==[39]
    assert not calls(spawn,'.setHomePos(') and not calls(spawn,'.PlayerCounter(')
    load = body(S,'readAdditionalSaveData')
    assert calls(load,'.setPhase(')==[34] and calls(load,'.setAct(')==[45]
    save = body(S,'addAdditionalSaveData')
    strings = {i['operand'] for i in save if i['opcode'] in ['0x12','0x13'] and isinstance(i['operand'],str)}
    assert strings=={'AnchorUUID','Phase','Act'}
    for method in ['setPhase','setParryCount','setFlying','setEye','setChainAnchor']:
        assert not calls(body(S,method),'Math.') and not calls(body(S,method),'.heal(')
    phase = body(PHASE,'start')
    assert calls(phase,'.setAttackState(')==[19] and calls(phase,'.setPhase(')==[38]
    assert not calls(phase,'isClientSide') and not calls(phase,'.hurt(')
    can_use = body(PHASE,'canUse')
    assert not any(calls(can_use,name) for name in ['.getTarget(','.isAlive(','.isNoAi(','isClientSide'])
    parry_stop = body(PARRY,'stop')
    assert calls(parry_stop,'.setParryCount(')==[43] and calls(parry_stop,'.parry_cooldownI')==[52]
    assert calls(body(SWING,'tick'),'.CanParryState(')==[950]
    assert calls(body(SWING,'tick'),'.stop(')==[969]
    assert calls(body(S,'decreaseAirSupply'),'.getMaxAirSupply(')==[]
    range_method = body(S,'RangeLimit')
    assert not any(i['opcode']=='0x90' for i in range_method)  # no double-to-float narrowing
    assert calls(body(REGISTRY,'lambda$static$96'),'.fireImmune(')
    registry = next(w for w in evidence['witnesses'] if w['entry']==PKG+REGISTRY+'.class')
    ctor = next(b for b in registry['registration_bootstraps'] if b['index']==17)
    assert PKG+S+'.<init>' in ctor['arguments'][1]


def validate(jar_path=None):
    review, note, ledger = [read_json(p) for p in [REVIEW, NOTE, LEDGER]]
    summary = validate_records(review, note, ledger)
    validate_preservation(review, note, ledger)
    methods = validate_evidence(review, note, jar_path)
    for path in [REVIEW, NOTE, LEDGER, SPEC_FILE, EVIDENCE_FILE]:
        assert path.read_text(encoding='utf-8') == json.dumps(read_json(path),ensure_ascii=False,indent=2)+'\n'
    return dict(status='PASS', **summary, new_method_witnesses=methods,
        protected_shared_status_and_prior_bosses='BYTE_IDENTICAL', prior_records_and_paths='UNCHANGED',
        pinned_jar='REPRODUCED' if jar_path is not None else 'ARCHIVED_WITNESSES_VALIDATED')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jar', type=Path, help='Optional exact pinned Cataclysm 3.27 JAR')
    print(json.dumps(validate(parser.parse_args().jar), indent=2))
