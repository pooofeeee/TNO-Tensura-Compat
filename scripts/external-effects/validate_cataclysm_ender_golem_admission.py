"""Focused R2k11a Ender Golem records, locked contracts and pinned-JAR checks."""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import struct
import subprocess

from catalog_common import OUT, ROOT, read_json
from collect_cataclysm_ender_golem_admission import (
    EVIDENCE_FILE, FRAGMENTS, G, METHODS, PIECE, PKG, REGISTRY, SPEC_FILE,
    collect, specification,
)

START = 'f66f109ffbd0297e0a61d50358325f72c903fe04'
CHECKPOINT = 'R2k11a-cataclysm-ender-golem-admission-complete'
NOTE = OUT / 'cataclysm-r2k11a-ender-golem-admission.json'
REVIEW = OUT / 'mod-reviews/cataclysm.json'
LEDGER = OUT / 'mod-completion-ledger.json'
BOSS_BASE = 'entity/AnimationMonster/BossMonsters/LLibrary_Boss_Monster'
KEYS = {'incoming_admission', 'shared_defense_bindings', 'environment_admission',
        'awake_state_prerequisites', 'dormant_healing', 'combat_persistence',
        'encounter_setup', 'citadel_spawn_prerequisites'}
KINDS = {'VANILLA_DIRECT', 'VANILLA_EQUIVALENT', 'VANILLA_LIKE_EXTENDED',
         'VANILLA_COMPOSITE', 'CUSTOM_DAMAGE', 'CUSTOM_STATUS', 'CUSTOM_CONTROL',
         'CUSTOM_RESOURCE', 'BINARY_MECHANIC'}
ORDER = ['STATE_RUNE_OR_DORMANT_AND_BYPASS_TAG_OR_NOT_EXACT_MAGIC_HALF',
         'CALCULATE_CAUSING_RANGE_RESULT_UNUSED', 'READ_DIRECT_ENTITY',
         'DIRECT_ABSTRACT_GOLEM_HALF', 'SHARED_HURT_SAME_SOURCE_TRANSFORMED_AMOUNT',
         'RETURN_SHARED_RESULT_WITHOUT_POSTWRITES']
MAX_FLOAT = struct.unpack('f', bytes.fromhex('ffff7f7f'))[0]


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
    assert {e['id'] for e in new} == {'cataclysm:ender_golem_' + k for k in KEYS}
    pids, eids = {p['id'] for p in paths}, {e['id'] for e in effects}
    for e in new:
        assert e['mod_key'] == 'cataclysm' and e['primary_classification'] in KINDS
        assert e['inspection_status'] == 'STATIC_REVIEWED' and not e['unresolved_ambiguities']
        assert e['actual_behavior'] and e['source_actor'] and e['primary_test_source']
        assert e['components'] and e['implementation'] and e['delivery_paths']
        assert e['closest_vanilla_equivalent'] and e['hurt_return_dependency']
        assert not {'stage_scaling_needed', 'stage_policy', 'stage_multiplier', 'stage_eligibility',
                    'stage_cap', 'stage_floor', 'runtime_hook'} & e.keys()
        assert set(e['delivery_paths']) <= pids
        observations = []
        for c in e['components']:
            assert c['primitive'] and c['formula'] and c['native_boundary'] and c['vanilla_relation']
            assert set(c['numerical_parameters']) == set(c['parameter_units'])
            for p, v in c['numerical_parameters'].items():
                assert isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)
                observations.append(dict(primitive=c['primitive'], parameter=p, native_value=v,
                    native_formula=c['formula'], units=c['parameter_units'][p], boundary=c['native_boundary']))
        assert observations == e['numeric_observations']
        candidates = e['scalable_parameter_candidates']
        assert candidates == sorted(candidates, key=lambda c: (c['primitive'], c['parameters']))
        seen = set()
        for c in candidates:
            assert len(c['parameters']) == 1
            p = c['parameters'][0]
            assert (c['primitive'], p) not in seen
            seen.add((c['primitive'], p))
            owners = [x for x in e['components'] if x['primitive'] == c['primitive']
                      and p in x['numerical_parameters']]
            assert len(owners) == 1, 'Candidate lost its native primitive'
            owner = owners[0]
            assert c['native_value'] == owner['numerical_parameters'][p]
            assert c['native_formula'] == owner['formula']
            assert c['units'] == owner['parameter_units'][p]
            assert c['native_boundary'] == owner['native_boundary']
        if e['id'] != 'cataclysm:ender_golem_dormant_healing':
            assert not candidates, 'Native admission/setup constants are not automatic scalar candidates'
    new_paths = [p for p in paths if p['id'].startswith('cataclysm:ender-golem-admission:')]
    assert len(new_paths) == 8
    for p in new_paths:
        assert p['mod_key'] == 'cataclysm' and p['status'] == 'VERIFIED'
        assert p['primary_source'] and p['native_path'] and p['setup'] and p['implementation']
        assert p['labels'] and p['runtime_status'] == 'NOT_RUN'
        assert p['effect_ids'] and set(p['effect_ids']) <= eids
        for e in new:
            assert (p['id'] in e['delivery_paths']) == (e['id'] in p['effect_ids'])
    assert note['mechanic_packages'] == [dict(id=e['id'], primary_classification=e['primary_classification'],
        delivery_paths=e['delivery_paths'], numerical_candidates=[{k: c[k] for k in
            ['primitive', 'parameters', 'native_value', 'units', 'native_boundary']}
            for c in e['scalable_parameter_candidates']], binary_gates=e['binary_parameters']) for e in new]
    summary = dict(new_mechanics=len(new), delivery_paths=len(new_paths),
        classifications=dict(sorted(Counter(e['primary_classification'] for e in new).items())),
        candidate_numeric_parameters=sum(len(c['parameters']) for e in new for c in e['scalable_parameter_candidates']),
        shared_binding_records=1, unresolved_subsection_ambiguities=0)
    assert summary == note['summary']
    assert summary['classifications'] == {'BINARY_MECHANIC': 7, 'VANILLA_DIRECT': 1}
    assert summary['candidate_numeric_parameters'] == 1
    assert review['status'] == ledger['status'] == note['status'] == 'PARTIAL'
    assert all(review[k] is False for k in ['semantic_discovery_complete',
        'special_damage_discovery_complete', 'source_mapping_complete', 'delivery_mapping_complete'])
    cat = next(t for t in ledger['targets'] if t['mod_key'] == 'cataclysm')
    assert cat['state'] == 'PARTIAL' and cat['semantic_effect_count'] == len(effects)
    assert review['checkpoint'] == ledger['checkpoint'] == note['checkpoint'] == CHECKPOINT
    assert review['exact_next_task'] == note['exact_next_task'] == cat['exact_next_task']
    assert note['exact_next_task'].startswith('R2k11b: Ender Golem offense/payload family.')
    assert note['remaining_ender_golem_work'] == ['R2k11b Ender Golem offense/payload family']
    assert not note['remaining_subsection_native_ambiguities'] and note['remaining_cataclysm_research']
    assert note['whole_mod_complete'] is False and note['runtime_tests'] == 0
    assert all(note[k] is False for k in ['stage_eligibility_decided', 'phase6_reopened',
        'production_changed', 'stage_changed', 'boss_testing_started', 'l2_testing_started',
        'compatibility_fixes_started', 'phase7_started'])
    validate_contracts({e['id'].removeprefix('cataclysm:ender_golem_'): e for e in new}, note)
    return summary


def validate_contracts(rows, note):
    def params(key, primitive):
        return next(c['numerical_parameters'] for c in rows[key]['components'] if c['primitive'] == primitive)

    facts = {
        'incoming_admission': dict(source_object_preserved=True, incoming_amount_rewritten=True,
            concrete_invulnerability_override=False, concrete_effect_override=False, concrete_retry_override=False,
            calculate_range_local_unused=True, magic_exemption_is_exact_type=True,
            bypass_skips_state_reduction=False, bypass_skips_direct_golem_reduction=False,
            awakens_on_hurt_return=False, concrete_post_hurt_callback=False),
        'shared_defense_bindings': dict(concrete_damage_cap_override=False, concrete_dps_cap_override=False,
            concrete_nature_regen_override=False, concrete_heal_cooldown_override=False,
            range_narrows_float_before_double=False, installed_cap_config_consumed=False,
            installed_dps_time_config_consumed=False, installed_nature_heal_config_consumed=False,
            damage_cap_is_bucket_capacity=True, dps_is_bucket_capacity=False),
        'environment_admission': dict(registered_fire_immune=True, concrete_invulnerability_override=False,
            air_returns_argument=True, air_returns_native_max=False, incoming_entity_push=False,
            blanket_drowning_immunity_claimed=False, concrete_fluid_override=False),
        'awake_state_prerequisites': dict(setter_resets_progress=False, setter_heals=False,
            initial_awake=False, target_wake_requires_alive=False, target_state_local_no_ai_guard=False,
            progress_update_local_server_guard=False, targetless_timeout_strict_greater=True,
            raw_state_is_tno_stage=False, offensive_dispatch_reviewed=False),
        'dormant_healing': dict(heal_has_local_server_guard=False, heal_has_local_no_ai_guard=False,
            heal_has_target_null_guard=False, heal_has_local_alive_guard=False, heal_reads_self_regen=False,
            heal_reads_nature_heal_config=False, heal_runs_before_target_wake=True, adds_shared_regen_delivery=False),
        'combat_persistence': dict(saved_awake=True, missing_awake_value=False, saved_targetless_ticks=False,
            saved_deactivation_progress=False, saved_rune_cooldown=False, concrete_animation_saved=False,
            inherited_ia_life=False, generic_persistence_added=False),
        'encounter_setup': dict(constructor_sets_home=False, constructor_sets_awake=False,
            constructor_health_is_heal_delivery=False, concrete_finalize_spawn_override=False,
            concrete_interaction_override=False, concrete_player_counter=False,
            explicit_armor_toughness_added=False, exhaustive_spawn_discovery_claimed=False),
        'citadel_spawn_prerequisites': dict(marker_is_exact_match=True, checks_bounding_box=True,
            checks_spawnable_bounds=True, marker_calls_finalize_spawn=False, marker_sets_home=False,
            marker_sets_awake=False, marker_has_creation_null_guard=False, spawn_return_consumed=False,
            unrelated_markers_reviewed=False),
    }
    for key, fields in facts.items():
        for field, value in fields.items():
            assert rows[key][field] == value, (key, field)
    assert rows['incoming_admission']['admission_order'] == note['admission_order']['concrete'] == ORDER
    multipliers = [c for c in rows['incoming_admission']['components'] if c['primitive'] == 'INCOMING_DAMAGE_MULTIPLIER']
    assert [c['numerical_parameters'] for c in multipliers] == [dict(state_multiplier=.5), dict(direct_golem_multiplier=.5)]
    assert multipliers[0]['native_boundary'] != multipliers[1]['native_boundary']
    assert params('shared_defense_bindings', 'DAMAGE_CAP') == dict(per_hit_cap=MAX_FLOAT)
    assert params('shared_defense_bindings', 'DPS_BUCKET') == dict(capacity=MAX_FLOAT, dps_cap=MAX_FLOAT, drain_divisor=20)
    assert params('shared_defense_bindings', 'RANGE_ADMISSION') == dict(range_limit=8.0)
    assert params('shared_defense_bindings', 'NATIVE_REGEN_BINDING') == dict(amount=0.0)
    assert params('shared_defense_bindings', 'REGEN_ADMISSION_TIMER') == dict(heal_cooldown=200)
    assert params('dormant_healing', 'NATIVE_HEAL') == dict(amount=2.0, cadence=20)
    assert params('awake_state_prerequisites', 'AWAKEN_STATE') == dict(targetless_threshold=400)
    assert params('awake_state_prerequisites', 'DEACTIVATION_STATE') == dict(ready_progress=0.0, dormant_progress=30.0, step=1.0)
    f32 = lambda x: struct.unpack('f', struct.pack('f', x))[0]
    assert params('encounter_setup', 'NATIVE_ATTRIBUTE_SETUP') == dict(follow_range=20.0,
        movement_speed=f32(.28), attack_damage=10.0, max_health=150.0, armor=12.0,
        step_height=1.5, knockback_resistance=1.0, health_multiplier=1.0, attack_multiplier=1.0)
    bindings = note['concrete_bindings']
    for name, native_value, config_name, installed_value in [
        ('DamageCap', MAX_FLOAT, 'damageCap', 999999.0), ('DpsCap', MAX_FLOAT, 'dpsCap', 999999.0),
        ('NatureRegen', 0.0, 'natureHeal', 25.0)]:
        b = bindings[name]
        assert b['inherited'] is True and b['native_value'] == native_value
        assert b['installed_but_unused'] == dict(ignored_config_field='EnderGolem.' + config_name,
            installed_value=installed_value, consumed_by_binding=False)
        assert b['candidate_observation_added'] is False
    assert bindings['RangeLimit']['installed_value'] == 8.0 and bindings['RangeLimit']['inherited'] is False
    assert bindings['RangeLimit']['native_cast'] == 'double(config), no float narrowing'
    assert bindings['configuredDpsLimitTime']['consumed_by_binding'] is False
    assert bindings['dormantHeal']['amount'] == 2.0 and not bindings['dormantHeal']['uses_shared_nature_regen']


def validate_preservation(review, note, ledger):
    assert note['starting_sha'] == START
    old = json.loads(at_start(REVIEW))
    assert len(old['effects']) == 296 and len(old['paths']) == 302
    assert [e for e in review['effects'] if e['review_checkpoint'] != CHECKPOINT] == old['effects']
    assert [p for p in review['paths'] if not p['id'].startswith('cataclysm:ender-golem-admission:')] == old['paths']
    mutable = {'effects', 'paths', 'checkpoint', 'scope', 'notes_file', 'exact_next_task', 'protected_checkpoints'}
    assert {k: v for k, v in review.items() if k not in mutable} == {k: v for k, v in old.items() if k not in mutable}
    assert review['protected_checkpoints'][:-1] == old['protected_checkpoints']
    assert review['protected_checkpoints'][-1] == dict(checkpoint=old['checkpoint'], notes_file=old['notes_file'])
    for r in note['reference_files']:
        path = OUT / r['file']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == r['sha256'], r['file']
        if r['usage'] == 'LOCKED_REUSED':
            assert path.read_bytes() == at_start(path), r['file']
    lock = note['protected_r2k10b']
    assert lock['file'] == 'cataclysm-r2k10b-scylla-offense.json'
    assert hashlib.sha256((OUT / lock['file']).read_bytes()).hexdigest() == lock['sha256']
    previous = json.loads(at_start(LEDGER))
    assert [t for t in ledger['targets'] if t['mod_key'] != 'cataclysm'] == [
        t for t in previous['targets'] if t['mod_key'] != 'cataclysm']
    assert {k: v for k, v in ledger.items() if k not in ['targets', 'checkpoint']} == {
        k: v for k, v in previous.items() if k not in ['targets', 'checkpoint']}


def validate_evidence(review, note, jar_path=None):
    assert read_json(SPEC_FILE) == specification()
    evidence = read_json(EVIDENCE_FILE)
    assert len(evidence['witnesses']) == 3
    assert {w['entry'] for w in evidence['witnesses']} == {PKG + n + '.class' for n in METHODS}
    if jar_path is not None:
        reproduced = collect(jar_path)
        assert evidence == reproduced, 'New witnesses failed pinned-JAR reproduction'
        assert EVIDENCE_FILE.read_bytes() == (json.dumps(reproduced, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    census = {c['entry']: c for c in read_json(OUT / 'cataclysm-source-census.json')['classes']}
    new_methods = {(w['entry'], m['name'], m['descriptor']): m
        for w in evidence['witnesses'] for m in w['methods']}
    assert len(new_methods) == 16
    sources = {r['file']: read_json(OUT / r['file']) for r in note['reference_files']
               if r['file'].startswith('native-evidence/')}
    for file, data in sources.items():
        if file == EVIDENCE_FILE.relative_to(OUT).as_posix():
            continue
        for w in data['witnesses']:
            for old in w.get('methods', []):
                new = new_methods.get((w['entry'], old['name'], old['descriptor']))
                if new is not None:
                    assert 'instruction_offset_ranges' in new, 'Old native method recaptured'
                    assert new['code_sha256'] == old['code_sha256']
                    assert not {i['offset'] for i in new['instructions']} & {
                        i['offset'] for i in old['instructions']}, 'Old fragment recaptured'
    for w in evidence['witnesses']:
        assert w['jar_sha256'] == note['tooling']['jar_sha256']
        assert w['entry_sha256'] == census[w['entry']]['entry_sha256']
        assert w['superclass'] == census[w['entry']]['superclass']
        name = w['entry'][len(PKG):-6]
        assert {m['name'] for m in w['methods']} == set(METHODS[name]) | set(FRAGMENTS[name])
        for m in w['methods']:
            if 'instruction_offset_ranges' in m:
                assert m['instruction_offset_ranges'] == FRAGMENTS[name][m['name']]
    for e in selected(review):
        for p in e['implementation']:
            w = next(w for w in sources[p['evidence_file']]['witnesses'] if w['id'] == p['witness_id'])
            assert p['entry'] == w['entry']
            assert set(p['methods']) <= {m['name'] for m in w.get('methods', [])}
    root = next(w for w in evidence['witnesses'] if w['entry'] == PKG + G + '.class')
    assert root['superclass'] == PKG + BOSS_BASE
    absent = {'isInvulnerableTo', 'DamageCap', 'DpsCap', 'NatureRegen', 'HealCooldown',
        'canBeAffected', 'Retry', 'finalizeSpawn', 'mobInteract', 'PlayerCounter',
        'isAffectedByFluids', 'isPushedByFluid', 'canStandOnFluid'}
    assert not absent & set(root['declared_method_names'])
    assert not {'BlockBreaking', 'EarthQuake', 'VoidRuneAttack', 'spawnFangs', 'launch',
                'isAlliedTo', 'onDeathAIUpdate', 'repelEntities', 'getRandomAttack'} & {m['name'] for m in root['methods']}
    assert note['tooling']['new_native_witnesses'] == 3 and note['tooling']['new_method_witnesses'] == 16
    assert not note['tooling']['reused_evidence_regenerated'] and not note['tooling']['recursive_jar_scan']
    validate_native_boundaries(evidence)
    return len(new_methods)


def validate_native_boundaries(evidence):
    """Verify the admission Boolean, actors, native heal/state and exact spawn branch."""
    def witness(entry):
        return next(w for w in evidence['witnesses'] if w['entry'] == PKG + entry + '.class')

    def body(entry, method):
        return next(m['instructions'] for m in witness(entry)['methods'] if m['name'] == method)

    def calls(ins, name):
        return [i['offset'] for i in ins if name in str(i.get('operand', ''))]

    def at(ins, offset):
        return next(i for i in ins if i['offset'] == offset)

    hurt = body(G, 'hurt')
    assert {p: at(hurt, p)['branch_target'] for p in [7, 14, 24, 34, 62]} == {7:17, 14:45, 24:37, 34:45, 62:73}
    assert at(hurt, 24)['opcode'] == at(hurt, 34)['opcode'] == '0x9a'
    assert calls(hurt, 'DamageTypeTags.BYPASSES_INVULNERABILITY') == [18]
    assert calls(hurt, 'DamageTypes.MAGIC') == [28]
    assert calls(hurt, '.calculateRange(') == [47] and calls(hurt, '.getDirectEntity(') == [52]
    assert not calls(hurt, '.getEntity(') and not calls(hurt, '.setIsAwaken(')
    assert calls(hurt, 'world/entity/animal/AbstractGolem') == [59]
    assert [i['offset'] for i in hurt if i['operand'] == .5] == [39, 67]
    assert at(hurt, 43)['opcode'] == at(hurt, 71)['opcode'] == '0x90'
    assert calls(hurt, '.hurt(') == [76] and at(hurt, 79)['opcode'] == '0xac'
    tick = body(G, 'tick')
    assert calls(tick, '.heal(') == [106] and at(tick,105)['operand'] == 2.0
    assert calls(tick, 'isClientSide') == [588]
    assert calls(tick, '.setIsAwaken(') == [622, 653]
    assert at(tick,632)['opcode'] == '0xa4' and at(tick,629)['operand'] == 400
    assert at(tick,605)['branch_target'] == 625 and at(tick,643)['branch_target'] == 656
    assert not calls(tick, '.hurt(') and not calls(tick, 'isNoAi') and not calls(tick, 'self_regen')
    assert not calls(tick, 'EnderGolem.natureHeal') and not calls(tick, '.NatureRegen(')
    assert calls(tick, '.isAlive(') == [119], 'Heal/target wake have no added alive guard'
    assert not calls(body(G,'setIsAwaken'), '.heal(') and not calls(body(G,'setIsAwaken'), 'deactivateProgress')
    save, load = body(G,'addAdditionalSaveData'), body(G,'readAdditionalSaveData')
    assert at(save,6)['operand'] == at(load,7)['operand'] == 'is_Awaken'
    assert calls(load, '.contains(') == [] and calls(load, '.setIsAwaken(') == [12]
    assert not any(s in str(i['operand']) for i in save + load for s in
        ['timeWithoutTarget', 'deactivateProgress', 'void_rune_attack_cooldown', 'LifeRemain'])
    air = body(G,'decreaseAirSupply')
    assert [i['opcode'] for i in air] == ['0x1b','0xac']
    factory = body(REGISTRY,'lambda$static$0')
    assert calls(factory, '.fireImmune(') == [20] and at(factory,23)['operand'] == 'cataclysm:ender_golem'
    assert calls(body(G,'<init>'), 'EnderGolem.healthMultiplier') and calls(body(G,'<init>'), 'EnderGolem.attackMultiplier')
    assert not calls(body(G,'<init>'), '.setHomePos(') and not calls(body(G,'<init>'), '.setIsAwaken(')
    assert calls(body(G,'RangeLimit'), 'EnderGolem.rangeCap') == [0]
    marker = body(PIECE,'handleDataMarker')
    assert calls(marker,'.isInside(') == [3] and calls(marker,'.isInSpawnableBounds(') == [10]
    assert at(marker,184)['operand'] == 'golem' and calls(marker,'java/lang/String.equals') == [187]
    assert calls(marker, '.create(') == [208] and calls(marker, '.moveTo(') == [238]
    assert calls(marker, '.addFreshEntity(') == [244] and at(marker,249)['opcode'] == '0x57'
    assert not calls(marker,'.finalizeSpawn(') and not calls(marker,'.setHomePos(') and not calls(marker,'.setIsAwaken(')
    assert not any(i['opcode'] in {'0xc6','0xc7'} for i in marker)
    registry = witness(REGISTRY)
    assert {b['index'] for b in registry['registration_bootstraps']} == {113,114}
    assert any(PKG + G + '.<init>' in b['arguments'][1] for b in registry['registration_bootstraps'])


def validate(jar_path=None):
    review, note, ledger = [read_json(p) for p in [REVIEW, NOTE, LEDGER]]
    summary = validate_records(review, note, ledger)
    validate_preservation(review, note, ledger)
    methods = validate_evidence(review, note, jar_path)
    for path in [REVIEW, NOTE, LEDGER, SPEC_FILE, EVIDENCE_FILE]:
        assert path.read_text(encoding='utf-8') == json.dumps(read_json(path), ensure_ascii=False, indent=2) + '\n'
    return dict(status='PASS', **summary, new_method_witnesses=methods,
        protected_shared_status_prior_bosses_scylla='BYTE_IDENTICAL',
        pinned_jar_reproduction='PASS' if jar_path else 'NOT_REQUESTED')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jar', type=Path, help='Reproduce only the new witnesses against the exact pinned Cataclysm JAR')
    print(json.dumps(validate(parser.parse_args().jar), indent=2))
