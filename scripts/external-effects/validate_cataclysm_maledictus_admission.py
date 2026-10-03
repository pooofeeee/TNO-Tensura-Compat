"""Focused, read-only R2k8a validation and optional pinned-JAR reproduction."""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import subprocess

from catalog_common import OUT, ROOT, read_json
from collect_cataclysm_maledictus_admission import (
    BLOCK, EVIDENCE_FILE, FRAGMENTS, M, PKG, REGISTRY, SPEC_FILE, TOMB,
    collect, specification,
)

START = '46d26d4960462006c66f272ef2ed9b4ccb03f8e7'
CHECKPOINT = 'R2k8a-cataclysm-maledictus-admission-complete'
NOTE = OUT / 'cataclysm-r2k8a-maledictus-admission.json'
REVIEW = OUT / 'mod-reviews/cataclysm.json'
LEDGER = OUT / 'mod-completion-ledger.json'
KINDS = {'VANILLA_DIRECT', 'VANILLA_EQUIVALENT', 'VANILLA_LIKE_EXTENDED',
         'VANILLA_COMPOSITE', 'CUSTOM_DAMAGE', 'CUSTOM_STATUS', 'CUSTOM_CONTROL',
         'CUSTOM_RESOURCE', 'BINARY_MECHANIC'}
KEYS = {'incoming_admission', 'shared_defense_bindings', 'nature_regen_binding',
        'environment_admission', 'phase_state_prerequisites', 'combat_persistence',
        'encounter_setup', 'tombstone_encounter'}
ORDER = ['STATE31_32_33_UNLESS_INVULNERABILITY_BYPASS',
         'ARM_DESTROY_BLOCKS20_IF_TIMER_NONPOSITIVE',
         'SHARED_HURT_SAME_SOURCE_AND_AMOUNT', 'RETURN_SHARED_HURT_RESULT']
SPAWN_ORDER = ['CREATE_BEFORE_SERVER_CHECK', 'SERVER_LEVEL_AND_NON_NULL', 'SET_POS',
               'SET_BLOCK_FACING', 'SET_HOME', 'FINALIZE_SPAWNER_RESETS_DIRECTION_SOUTH',
               'CLEAR_ENCOUNTER_VOLUME', 'ADD_FRESH_ENTITY', 'ON_SUCCESS_DESTROY_TOMBSTONE']


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
    assert {e['id'] for e in new} == {'cataclysm:maledictus_' + k for k in KEYS}
    pids, eids = {p['id'] for p in paths}, {e['id'] for e in effects}
    for e in new:
        assert e['mod_key'] == 'cataclysm' and e['primary_classification'] in KINDS
        assert e['inspection_status'] == 'STATIC_REVIEWED' and not e['unresolved_ambiguities']
        assert e['actual_behavior'] and e['source_actor'] and e['primary_test_source']
        assert e['components'] and e['implementation'] and e['delivery_paths']
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
        if e['id'] != 'cataclysm:maledictus_nature_regen_binding':
            assert not candidates, 'Native admission/setup observations are not outgoing scalar candidates'
    new_paths = [p for p in paths if p['id'].startswith('cataclysm:maledictus-admission:')]
    assert len(new_paths) == 8
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
    assert summary == note['summary'] and summary['candidate_numeric_parameters'] == 1
    assert review['status'] == ledger['status'] == note['status'] == 'PARTIAL'
    assert all(review[k] is False for k in ['semantic_discovery_complete',
        'special_damage_discovery_complete', 'source_mapping_complete', 'delivery_mapping_complete'])
    cat = next(t for t in ledger['targets'] if t['mod_key'] == 'cataclysm')
    assert cat['state'] == 'PARTIAL' and cat['semantic_effect_count'] == len(effects)
    assert review['checkpoint'] == ledger['checkpoint'] == note['checkpoint'] == CHECKPOINT
    assert review['exact_next_task'] == note['exact_next_task'] == cat['exact_next_task']
    assert note['exact_next_task'].startswith('R2k8b: Maledictus offense/payload family.')
    assert note['remaining_maledictus_work'] and not note['remaining_subsection_native_ambiguities']
    assert note['whole_mod_complete'] is False and note['runtime_tests'] == 0
    assert all(note[k] is False for k in ['stage_eligibility_decided', 'phase6_reopened',
        'production_changed', 'stage_changed', 'boss_testing_started', 'l2_testing_started',
        'compatibility_fixes_started', 'phase7_started'])
    validate_contracts({e['id'].removeprefix('cataclysm:maledictus_'): e for e in new}, note)
    return summary


def validate_contracts(rows, note):
    def values(key, primitive):
        return next(c['numerical_parameters'] for c in rows[key]['components'] if c['primitive'] == primitive)

    assert note['admission_order']['concrete'] == rows['incoming_admission']['admission_order'] == ORDER
    incoming = rows['incoming_admission']
    assert incoming['timer_armed_before_shared_hurt'] is True
    assert all(incoming[k] is False for k in ['concrete_is_invulnerable_override',
        'concrete_effect_admission_override', 'incoming_amount_rewritten', 'local_direct_or_causing_filter',
        'hurt_reads_weapon_flying_rage', 'timer_requires_hurt_success', 'post_hurt_state_write'])
    assert values('incoming_admission', 'NATIVE_DAMAGE_ADMISSION') == dict(
        protected_state31=31, protected_state32=32, protected_state33=33)
    assert values('incoming_admission', 'TERRAIN_RESPONSE_ARMING') == dict(arming_ticks=20)
    cfg = read_json(OUT / 'cataclysm-installed-common-config.json')['values']['mobs']['maledictus']
    bindings = {'DamageCap': ('damageCap', cfg['cap_config']['damage_cap']),
        'DpsCap': ('dpsCap', cfg['cap_config']['dps_cap']),
        'RangeLimit': ('rangeCap', cfg['cap_config']['range_cap']),
        'NatureRegen': ('natureHeal', cfg['nature_heal_config']['nature_heal']),
        'DpsMulti': ('dpsLimitTime', cfg['cap_config']['dps_limit_time'])}
    for name, (field, value) in bindings.items():
        assert note['concrete_bindings'][name]['config_field'] == 'Maledictus.' + field
        assert note['concrete_bindings'][name]['installed_value'] == value
        assert note['concrete_bindings'][name]['shared_boundary']
    assert note['concrete_bindings']['RangeLimit']['native_cast'] == 'double(config), no float narrowing'
    assert note['concrete_bindings']['HealCooldown']['native_value'] == 200
    defense = rows['shared_defense_bindings']
    assert defense['damage_cap_is_bucket_capacity'] is True and defense['dps_is_bucket_capacity'] is False
    assert defense['range_narrows_float_before_double'] is False
    assert defense['dps_multi_read_by_shared_hurt_or_tick'] is False
    assert defense['installed_config_values'] == dict(damage_cap=20.0, dps_cap=13.0,
        range_limit=14.0, heal_cooldown=200, dps_limit_time=20)
    assert values('shared_defense_bindings', 'DAMAGE_CAP') == dict(per_hit_cap=20.0)
    assert values('shared_defense_bindings', 'DPS_BUCKET') == dict(capacity=20.0, dps_cap=13.0, drain_divisor=20)
    assert values('shared_defense_bindings', 'RANGE_ADMISSION') == dict(range_limit=14.0)
    assert values('shared_defense_bindings', 'REGEN_ADMISSION_TIMER') == dict(heal_cooldown=200)
    regen = rows['nature_regen_binding']
    assert regen['record_kind'] == 'SHARED_BINDING' and regen['binding_of'] == 'cataclysm:shared_heal'
    assert values('nature_regen_binding', 'NATIVE_HEAL') == dict(amount=25.0)
    environment = rows['environment_admission']
    assert environment['registered_fire_immune'] is True and environment['registered_immune_blocks'] == []
    assert environment['air_supply_returns_input'] is True
    assert all(environment[k] is False for k in ['fall_callback_calls_parent', 'fluid_affected',
        'fluid_push', 'blanket_drowning_damage_immunity_claimed'])
    phase = rows['phase_state_prerequisites']
    assert phase['default_state'] == dict(weapon=0, flying=False, rage=0, tombstone_direction='NORTH')
    assert phase['rage_decay_server_only'] is True
    assert all(phase[k] is False for k in ['raw_integer_setters_clamp', 'state_setters_change_attack_state',
        'state_setters_heal', 'health_predicates_saved', 'separate_saved_phase_or_shield_latch',
        'rage_decay_no_ai_gate', 'rage_decay_target_gate', 'flight_no_gravity_local_server_guard'])
    assert values('phase_state_prerequisites', 'PHASE_STATE') == dict(half_health_ratio=0.5, quarter_health_ratio=0.25)
    assert values('phase_state_prerequisites', 'RAGE_STATE_DECAY') == dict(decay_step=1, decay_ticks=200)
    persistence = rows['combat_persistence']
    assert persistence['saved_concrete_keys'] == ['RageMeter', 'Tombstone_Direction']
    assert persistence['missing_key_defaults'] == dict(RageMeter=0, Tombstone_Direction_byte=0)
    assert all(persistence[k] is False for k in ['saved_weapon', 'saved_flying', 'saved_attack_state',
        'saved_rage_ticks', 'saved_destroy_blocks_tick', 'generic_persistence_added'])
    setup = rows['encounter_setup']
    assert setup['attributes_apply_to'] == 'cataclysm:maledictus'
    assert setup['registered_dimensions'] == dict(width=1.5, height=3.0)
    assert setup['finalize_direction'] == 'SOUTH'
    assert all(setup[k] is False for k in ['explicit_armor_toughness_added',
        'configured_health_is_heal_delivery', 'finalize_sets_home', 'concrete_item_activation_override'])
    assert values('encounter_setup', 'NATIVE_ATTRIBUTE_SETUP') == dict(base_health=420.0,
        base_attack_damage=13.0, armor=10.0, knockback_resistance=1.0, health_multiplier=1.0, attack_multiplier=1.0)
    tomb = rows['tombstone_encounter']
    assert tomb['spawn_order'] == SPAWN_ORDER and tomb['spawn_type'] == 'SPAWNER'
    assert tomb['spawn_sets_home'] is True and tomb['cleanup_requires_add_success'] is True
    assert tomb['default_block_state'] == dict(facing='NORTH', lit=False, powered=False)
    assert all(tomb[k] is False for k in ['activation_requires_item', 'activation_consumes_item',
        'activation_local_server_guard', 'ticker_has_side_gate', 'block_facing_survives_finalize',
        'spawn_sets_attack_state', 'spawn_sets_persistence_required', 'clearance_requires_mobgriefing',
        'retry_counter_reset_on_failed_add', 'cooldown_int_round_trip', 'countdown_saved'])
    assert tomb['cooldown_saved_with'] == 'putInt' and tomb['cooldown_load_tag_type'] == 11
    assert values('tombstone_encounter', 'ENCOUNTER_GATE') == dict(cooldown_minutes=1,
        cooldown_tick_factor=1200, summon_after_tick=63, spawn_y_offset=2, inherited_home_cooldown=400)
    assert read_json(OUT / 'cataclysm-installed-common-config.json')['values']['blocks'][
        'cursed_tombstone']['cursed_tombstone_cooldown'] == 1


def validate_preservation(review, note, ledger):
    assert note['starting_sha'] == START
    old = json.loads(at_start(REVIEW))
    assert [e for e in review['effects'] if e['review_checkpoint'] != CHECKPOINT] == old['effects']
    assert [p for p in review['paths'] if not p['id'].startswith('cataclysm:maledictus-admission:')] == old['paths']
    mutable = {'effects', 'paths', 'checkpoint', 'scope', 'notes_file', 'exact_next_task', 'protected_checkpoints'}
    assert {k: v for k, v in review.items() if k not in mutable} == {k: v for k, v in old.items() if k not in mutable}
    assert review['protected_checkpoints'] == old['protected_checkpoints'] + [
        dict(checkpoint=old['checkpoint'], notes_file=old['notes_file'])]
    assert note['previous_checkpoint'] == old['checkpoint']
    assert {r['file'] for r in note['reference_files']} >= {
        old['notes_file'], 'cataclysm-r2k7a-remnant-admission.json',
        'native-evidence/cataclysm-remnant-admission.json'}
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


def validate_native_distinctions(evidence):
    def body(name, method):
        w = next(w for w in evidence['witnesses'] if w['entry'] == PKG + name + '.class')
        return next(m['instructions'] for m in w['methods'] if m['name'] == method)

    def calls(ins, text):
        return [i['offset'] for i in ins if text in str(i['operand'])]

    def item(ins, offset):
        return next(i for i in ins if i['offset'] == offset)

    hurt = body(M, 'hurt')
    assert [item(hurt, p)['operand'] for p in [4, 13, 22, 47]] == [31, 32, 33, 20]
    assert calls(hurt, 'BYPASSES_INVULNERABILITY') == [28]
    assert item(hurt, 43)['opcode'] == '0x9d'
    assert calls(hurt, '.destroyBlocksTickI') == [40, 49]
    assert calls(hurt, 'IABoss_monster.hurt(') == [55] and item(hurt, 58)['opcode'] == '0xac'
    assert all(not calls(hurt, x) for x in ['.getEntity(', '.getDirectEntity(', '.getWeapon(',
        '.isFlying(', '.getRageMeter(', '.setAttackState(', '.heal('])
    for method, field in [('DamageCap', 'damageCap'), ('DpsCap', 'dpsCap'), ('NatureRegen', 'natureHeal')]:
        ins = body(M, method)
        assert calls(ins, 'CMCommonConfig$Maledictus.' + field + 'D') == [0]
        assert item(ins, 3)['opcode'] == '0x90'
    assert item(body(M, 'RangeLimit'), 3)['opcode'] == '0xaf'
    assert calls(body(M, 'RangeLimit'), 'Maledictus.rangeCapD') == [0]
    assert calls(body(M, 'DpsMulti'), 'Maledictus.dpsLimitTimeI') == [0]
    for method in ['causeFallDamage', 'isAffectedByFluids', 'isPushedByFluid']:
        assert [i['opcode'] for i in body(M, method)] == ['0x3', '0xac']
    assert [i['opcode'] for i in body(M, 'decreaseAirSupply')] == ['0x1b', '0xac']
    defaults = body(M, 'defineSynchedData')
    assert calls(defaults, 'Direction.NORTH') == [9]
    assert [item(defaults, p)['operand'] for p in [20, 32, 44]] == [0, 0, 0]
    for method in ['setWeapon', 'setFlying', 'setRageMeter', 'setTombstoneDirection']:
        ins = body(M, method)
        assert len(calls(ins, 'SynchedEntityData.set(')) == 1
        assert all(not calls(ins, text) for text in ['clamp', '.setAttackState(', '.heal('])
    assert item(body(M, 'isHalfHealth'), 11)['operand'] == 0.5
    assert item(body(M, 'isQuarterHealth'), 11)['operand'] == 0.25
    tick = body(M, 'tick')
    assert calls(tick, 'IABoss_monster.tick(') == [1]
    assert calls(tick, 'Level.isClientSide(') == [83]
    assert calls(tick, '.setRageMeter(') == [159] and item(tick, 163)['operand'] == 200
    assert calls(tick, '.setNoGravity(') == [368, 376]
    assert all(not calls(tick, text) for text in ['.isNoAi(', '.getTarget(', '.DMG(', '.blockbreak(', '.getPassengers('])
    save, load = body(M, 'addAdditionalSaveData'), body(M, 'readAdditionalSaveData')
    assert calls(save, 'CompoundTag.putInt(') == [13] and calls(save, 'CompoundTag.putByte(') == [28]
    assert calls(load, '.setTombstoneDirection(') == [16] and calls(load, '.setRageMeter(') == [27]
    assert not calls(load, 'CompoundTag.contains(')
    finalize = body(M, 'finalizeSpawn')
    assert calls(finalize, 'Direction.SOUTH') == [1] and calls(finalize, '.setTombstoneDirection(') == [4]
    assert calls(finalize, 'IABoss_monster.finalizeSpawn(') == [13] and not calls(finalize, '.setHomePos(')
    constructor = body(M, '<init>')
    assert calls(constructor, '.setConfigattribute(') == [495]
    registry = body(REGISTRY, 'lambda$static$87')
    assert calls(registry, '.fireImmune(') == [20] and not calls(registry, '.immuneTo(')
    assert [item(registry, p)['operand'] for p in [11, 14]] == [1.5, 3.0]
    use = body(BLOCK, 'useItemOn')
    assert calls(use, '.POWEREDL') == [1] and calls(use, '.LITL') == [17, 33]
    assert all(not calls(use, text) for text in ['ItemStack.', '.shrink(', 'isClientSide'])
    common = body(TOMB, 'commonTick')
    assert item(common, 33)['operand'] == 1200 and item(common, 470)['operand'] == 63
    assert calls(common, 'EntityType.create(') == [485] and item(common, 494)['operand'] == 'net/minecraft/server/level/ServerLevel'
    assert calls(common, '.setTombstoneDirection(') == [568] and calls(common, '.setHomePos(') == [582]
    assert calls(common, 'MobSpawnType.SPAWNER') == [595] and calls(common, '.finalizeSpawn(') == [599]
    assert calls(common, 'ALTAR_DESTROY_IMMUNE') == [717]
    assert calls(common, '.destroyBlock(') == [730, 764] and calls(common, '.addFreshEntity(') == [755]
    assert item(common, 758)['opcode'] == '0x99'
    assert all(not calls(common, text) for text in ['.setAttackState(', '.setPersistenceRequired(',
        'GameRules.', 'ScreenShake', '.addParticle('])
    tomb_load, tomb_save = body(TOMB, 'loadAdditional'), body(TOMB, 'saveAdditional')
    assert item(tomb_load, 10)['operand'] == 11
    assert calls(tomb_load, 'CompoundTag.contains(') == [12] and calls(tomb_load, 'CompoundTag.getInt(') == [23]
    assert calls(tomb_save, 'CompoundTag.putInt(') == [14]


def validate_evidence(review, note, jar_path=None):
    assert read_json(SPEC_FILE) == specification()
    evidence = read_json(EVIDENCE_FILE)
    assert len(evidence['witnesses']) == note['tooling']['new_native_witnesses'] == 4
    assert [w['entry'] for w in evidence['witnesses']] == [s['entry'] for s in specification()['evidence_specifications']]
    if jar_path is not None:
        assert evidence == collect(jar_path), 'Pinned-JAR witnesses did not reproduce'
    census = {c['entry']: c['entry_sha256'] for c in read_json(OUT / 'cataclysm-source-census.json')['classes']}
    inventory = next(t for t in read_json(OUT / 'jar-inventory.json')['targets'] if t['key'] == 'cataclysm')
    sources = {r['file']: read_json(OUT / r['file']) for r in note['reference_files']
               if r['file'].startswith('native-evidence/')}
    methods = [(w['entry'], m['name'], m['descriptor']) for w in evidence['witnesses'] for m in w['methods']]
    assert len(methods) == len(set(methods)) == note['tooling']['new_method_witnesses'] == 37
    for w in evidence['witnesses']:
        assert w['jar_sha256'] == inventory['sha256'] and w['entry_sha256'] == census[w['entry']]
        for m in w['methods']:
            if 'instruction_offset_ranges' in m:
                assert m['instruction_offset_ranges'] == FRAGMENTS[w['entry'][len(PKG):-6]][m['name']]
    concrete = next(w for w in evidence['witnesses'] if w['entry'] == PKG + M + '.class')
    assert concrete['superclass'] == PKG + 'entity/InternalAnimationMonster/IABossMonsters/IABoss_monster'
    assert not {'isInvulnerableTo', 'canBeAffected', 'mobInteract'} & set(concrete['declared_method_names'])
    parents = sources['native-evidence/cataclysm-remnant-admission.json']['witnesses']
    for name in ['entity/InternalAnimationMonster/IABossMonsters/IABoss_monster',
                 'entity/InternalAnimationMonster/Internal_Animation_Monster', 'entity/etc/Animation_Monsters']:
        w = next(w for w in parents if w['entry'] == PKG + name + '.class')
        assert 'isInvulnerableTo' not in w['declared_method_names'] and not w['methods']
    for e in selected(review):
        for p in e['implementation']:
            w = next(w for w in sources[p['evidence_file']]['witnesses'] if w['id'] == p['witness_id'])
            assert p['entry'] == w['entry'] and set(p['methods']) <= {m['name'] for m in w['methods']}
    registration = next(w for w in evidence['witnesses'] if w['entry'] == PKG + REGISTRY + '.class')
    assert [b['index'] for b in registration['registration_bootstraps']] == [26, 201]
    assert any(PKG + M + '.<init>' in str(b['arguments']) for b in registration['registration_bootstraps'])
    ticker = next(w for w in evidence['witnesses'] if w['entry'] == PKG + BLOCK + '.class')
    assert any(PKG + TOMB + '.commonTick' in str(b['arguments']) for b in ticker['registration_bootstraps'])
    attributes = next(w for w in sources['native-evidence/cataclysm-guardian-admission.json']['witnesses']
                      if w['entry'] == PKG + REGISTRY + '.class')
    ins = next(m['instructions'] for m in attributes['methods'] if m['name'] == 'initializeAttributes')
    assert any(i['offset'] == 514 and 'ModEntities.MALEDICTUS' in str(i['operand']) for i in ins)
    assert any(i['offset'] == 523 and PKG + M + '.maledictus(' in str(i['operand']) for i in ins)
    shared = next(w for w in sources['native-evidence/cataclysm-shared.json']['witnesses']
                  if w['entry'].endswith('/IABoss_monster.class'))
    assert not any('DpsMulti' in str(i['operand']) for m in shared['methods'] if m['name'] in ['hurt', 'tick']
                   for i in m['instructions'])
    validate_native_distinctions(evidence)
    return len(methods)


def validate(jar_path=None):
    review, note, ledger = [read_json(p) for p in [REVIEW, NOTE, LEDGER]]
    summary = validate_records(review, note, ledger)
    validate_preservation(review, note, ledger)
    methods = validate_evidence(review, note, jar_path)
    return dict(status='PASS', **summary, new_method_witnesses=methods,
        protected_shared_status_and_prior_bosses='BYTE_IDENTICAL', prior_records_and_paths='UNCHANGED',
        pinned_jar='REPRODUCED' if jar_path is not None else 'ARCHIVED_WITNESSES_VALIDATED')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jar', type=Path, help='Optional exact pinned Cataclysm 3.27 JAR')
    print(json.dumps(validate(parser.parse_args().jar), indent=2))
