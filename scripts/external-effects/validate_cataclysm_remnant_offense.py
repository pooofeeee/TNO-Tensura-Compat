"""Focused read-only R2k7b records, protected contracts and pinned-JAR validation."""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import subprocess

from catalog_common import OUT, ROOT, read_json
from collect_cataclysm_remnant_offense import (
    AM, E, EVIDENCE_FILE, FRAGMENTS, METHODS, PKG, R, REGISTRY, RESOURCES,
    S, SPEC_FILE, T, collect, specification,
)

START = '2e8efcbdbd07ebff9fed488c301a55e38485d3b4'
CHECKPOINT = 'R2k7b-cataclysm-remnant-offense-complete'
NOTE = OUT / 'cataclysm-r2k7b-remnant-offense.json'
REVIEW = OUT / 'mod-reviews/cataclysm.json'
LEDGER = OUT / 'mod-completion-ledger.json'
KINDS = {'VANILLA_DIRECT', 'VANILLA_EQUIVALENT', 'VANILLA_LIKE_EXTENDED',
         'VANILLA_COMPOSITE', 'CUSTOM_DAMAGE', 'CUSTOM_STATUS',
         'CUSTOM_CONTROL', 'CUSTOM_RESOURCE', 'BINARY_MECHANIC'}
KEYS = {'attack_selection', 'attack_mode', 'rage_crash', 'charge_chain',
        'charge_contact', 'bite', 'tail_slam', 'tail_swing', 'stomp_chain',
        'stomp_contact', 'stomp_debris', 'roar_chain', 'sandstorm_payload',
        'sandstorm_motion', 'sandstorm_lifecycle', 'earthquake_volley',
        'earthquake_contact', 'earthquake_motion', 'monolith_chain',
        'stele_contact', 'stele_lifecycle', 'terrain_control', 'alliance',
        'movement_control', 'defeat_lifecycle'}


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
    assert {e['id'] for e in new} == {'cataclysm:remnant_' + k for k in KEYS}
    pids, eids = {p['id'] for p in paths}, {e['id'] for e in effects}
    for e in new:
        assert e['mod_key'] == 'cataclysm' and e['primary_classification'] in KINDS
        assert e['inspection_status'] == 'STATIC_REVIEWED' and not e['unresolved_ambiguities']
        assert e['components'] and e['implementation'] and e['primary_test_source']
        assert e['source_actor'] and e['hurt_return_dependency']
        assert e['delivery_paths'] and set(e['delivery_paths']) <= pids
        assert not {'stage_scaling_needed', 'stage_policy', 'stage_multiplier', 'runtime_hook'} & e.keys()
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
        seen = set()
        for c in candidates:
            assert len(c['parameters']) == 1
            p = c['parameters'][0]
            assert (c['primitive'], p) not in seen
            seen.add((c['primitive'], p))
            owners = [x for x in e['components'] if x['primitive'] == c['primitive']
                      and p in x['numerical_parameters']]
            assert len(owners) == 1, 'Candidate lost its original native primitive'
            owner = owners[0]
            assert c['native_value'] == owner['numerical_parameters'][p]
            assert c['native_formula'] == owner['formula']
            assert c['units'] == owner['parameter_units'][p]
            assert c['native_boundary'] == owner['native_boundary']
        if e['primary_classification'] == 'BINARY_MECHANIC':
            assert not candidates
    new_paths = [p for p in paths if p['id'].startswith('cataclysm:remnant-offense:')]
    assert len(new_paths) == 25
    for p in new_paths:
        assert p['mod_key'] == 'cataclysm' and p['status'] == 'VERIFIED'
        assert p['primary_source'] and p['native_path'] and p['setup'] and p['implementation']
        assert p['labels'] and p['runtime_status'] == 'NOT_RUN'
        assert p['effect_ids'] and set(p['effect_ids']) <= eids
        for e in new:
            assert (p['id'] in e['delivery_paths']) == (e['id'] in p['effect_ids'])
    rows = {e['id']: e for e in new}
    payloads = note['payload_entities']
    assert {p['entry'] for p in payloads} == {PKG + n + '.class' for n in [
        S, E, T, 'entity/effect/Cm_Falling_Block_Entity']}
    assert len(payloads) == 4
    for p in payloads:
        assert p['source_mechanic_ids'] and set(p['source_mechanic_ids']) <= rows.keys()
        assert set(p['payload_mechanic_ids']) <= rows.keys()
        assert p['source_actor'] and p['native_lifecycle']
        for producer in p['source_mechanic_ids']:
            assert p['entity_id'] in rows[producer]['spawned_entity_ids']
        assert bool(p['payload_mechanic_ids']) == (p['role'] != 'NON_DAMAGE_DEBRIS_VERIFIED')
    assert note['offense_paths_closed'] == [p['id'] for p in new_paths]
    assert note['mechanic_packages'] == [dict(id=e['id'],
        primary_classification=e['primary_classification'], delivery_paths=e['delivery_paths'],
        numerical_candidates=[{k: c[k] for k in ['primitive', 'parameters', 'native_value',
            'units', 'native_boundary']} for c in e['scalable_parameter_candidates']],
        binary_gates=e['binary_parameters'], hurt_return_dependency=e['hurt_return_dependency']) for e in new]
    summary = dict(new_mechanics=len(new), delivery_paths=len(new_paths),
        classifications=dict(sorted(Counter(e['primary_classification'] for e in new).items())),
        candidate_numeric_parameters=sum(len(c['parameters']) for e in new for c in e['scalable_parameter_candidates']),
        unresolved_subsection_ambiguities=0, new_owned_payload_classes=3, reused_non_damage_debris_classes=1)
    assert summary == note['summary'] and summary['candidate_numeric_parameters'] == 78
    assert review['status'] == ledger['status'] == note['status'] == 'PARTIAL'
    for field in ['semantic_discovery_complete', 'special_damage_discovery_complete',
                  'source_mapping_complete', 'delivery_mapping_complete']:
        assert review[field] is False
    cat = next(t for t in ledger['targets'] if t['mod_key'] == 'cataclysm')
    assert cat['state'] == 'PARTIAL' and cat['semantic_effect_count'] == len(effects)
    assert review['checkpoint'] == ledger['checkpoint'] == note['checkpoint'] == CHECKPOINT
    assert review['exact_next_task'] == note['exact_next_task'] == cat['exact_next_task']
    assert note['exact_next_task'].startswith('R2k8a: Maledictus incoming admission and phase/encounter prerequisites.')
    assert note['ancient_remnant_family_closed'] is True and not note['remaining_ancient_remnant_work']
    assert not note['remaining_subsection_native_ambiguities'] and note['remaining_cataclysm_research']
    assert note['whole_mod_complete'] is False and note['runtime_tests'] == 0
    assert all(note[k] is False for k in ['stage_eligibility_decided', 'phase6_reopened',
        'production_changed', 'stage_changed', 'boss_testing_started', 'l2_testing_started',
        'compatibility_fixes_started', 'phase7_started'])
    validate_contracts(rows)
    return summary


def validate_contracts(rows):
    def row(k):
        return rows['cataclysm:remnant_' + k]

    def component(k, primitive):
        return next(c for c in row(k)['components'] if c['primitive'] == primitive)

    assert row('attack_selection')['selection_is_goal_scheduled'] is True
    assert row('attack_selection')['monolith_roll_calls'] == 3
    assert row('attack_selection')['monolith_has_outer_maximum_range'] is False
    assert row('attack_selection')['cooldown_resets'] == {'roar': 500, 'monoltih': 200, 'earthquake': 160, 'stomp': 110}
    assert row('attack_mode')['hunting_cooldown_initial'] == 160
    assert row('attack_mode')['hunting_cooldown_reset'] is False
    assert row('attack_mode')['continuation_checks_attack_state'] is False
    assert row('rage_crash')['charge_start_clears_hit'] is False
    assert row('rage_crash')['charge_contact_sets_hit'] is False
    assert row('rage_crash')['monolith_stop_increments_rage'] is False
    assert row('rage_crash')['crash_reset_on_run_stop'] is True
    assert row('charge_chain')['charge_states'] == [10, 11, 12]
    assert row('charge_chain')['movement_is_native_knockback'] is False
    assert row('charge_chain')['run_motion_requires_target'] is False
    assert row('charge_chain')['run_tick_calls_parent'] is False
    for k in ['charge_contact', 'tail_swing']:
        assert row(k)['push_requires_hurt_true'] is True
    assert row('charge_contact')['push_requires_on_ground'] is True
    assert row('charge_contact')['terrain_result_gates_damage'] is False
    assert row('charge_contact')['damage_uses_exact_boss_bbox'] is True
    assert row('charge_contact')['contact_period_ticks'] == 4
    for k in ['bite', 'tail_slam', 'tail_swing', 'stomp_contact']:
        assert row(k)['shield_requires_hurt_true'] is False
    for k in ['bite', 'tail_slam', 'tail_swing']:
        assert row(k)['hp_addition_capped'] is True
    assert row('bite')['attack_tick'] == 31 and row('bite')['stun_duration'] == 0
    assert row('tail_slam')['attack_ticks'] == [26, 55, 85]
    assert row('tail_slam')['quake_spawn_requires_area_hurt_true'] is False
    assert row('tail_swing')['status_requires_hurt_true'] is True
    assert row('tail_swing')['push_requires_on_ground'] is False
    assert row('tail_swing')['status_has_explicit_source'] is False
    assert row('stomp_contact')['hp_addition_capped'] is False
    assert row('stomp_contact')['pull_requires_hurt_true'] is True
    assert row('stomp_contact')['pull_y_requires_on_ground'] is True
    assert component('stomp_contact', 'FORCED_MOVEMENT')['numerical_parameters']['signed_horizontal_coefficient'] == -4.0
    r = row('stomp_chain')
    assert r['normal_goal_max_ticks'] == 50 and r['powered_goal_max_ticks'] == 66
    assert r['declared_powered_last_payload_tick'] == 68
    assert r['unused_airborne_argument'] == 0.10000000149011612
    assert not any('airborne' in c['parameters'] for c in r['scalable_parameter_candidates'])
    assert r['wave_profiles']['8'][-1]['distances'] == [18, 19]
    assert r['wave_profiles']['13'][-1] == dict(tick=68, distances=[19, 20], side_offset=1.399999976158142)
    assert r['wave_profiles']['9'][0]['side_offset'] == -1.399999976158142
    assert r['wave_profiles']['9'][1]['side_offset'] == 1.399999976158142
    assert r['wave_profiles']['14'][10]['side_offset'] == -1.399999976158142
    assert row('stomp_debris')['debris_adds_damage'] is False
    assert row('stomp_debris')['stomp_removes_terrain'] is False
    assert row('stomp_debris')['stomp_places_terrain'] is False
    assert row('roar_chain')['spawn_tick'] == 55 and row('roar_chain')['supplied_lifespan'] == 300
    assert row('roar_chain')['spawn_requires_target'] is False
    assert row('roar_chain')['spawn_requires_hurt_true'] is False
    for k in ['sandstorm_payload', 'earthquake_contact', 'stele_contact']:
        assert row(k)['has_bilateral_allied_check'] == (k == 'sandstorm_payload')
    assert row('sandstorm_payload')['status_requires_hurt_true'] is True
    assert row('sandstorm_payload')['local_damage_server_guard'] is False
    assert row('sandstorm_payload')['contact_period_ticks'] == 3
    assert row('sandstorm_payload')['has_radial_distance_check'] is False
    assert row('sandstorm_motion')['orbit_is_collision_radius'] is False
    assert row('sandstorm_lifecycle')['owner_uuid_saved'] is True
    for k in ['offset_saved', 'state_saved', 'discard_returns_early', 'damage_gated_by_visual_state', 'caster_absence_discards']:
        assert row('sandstorm_lifecycle')[k] is False
    assert row('earthquake_volley')['local_spawn_server_guard'] is False
    assert row('earthquake_volley')['counts_per_volley'] == [22, 29]
    assert row('earthquake_contact')['contact_period_ticks'] == 5
    for k in ['local_damage_server_guard', 'caster_absence_damage_fallback', 'contact_gated_by_projectile_impact_hook']:
        assert row('earthquake_contact')[k] is False
    assert row('earthquake_contact')['push_requires_hurt_true'] is True
    for k in ['native_parent_tick_retained', 'concrete_move_precedes_parent', 'owner_death_still_ticks_parent']:
        assert row('earthquake_motion')[k] is True
    for k in ['expiry_discard_returns_early', 'damage_saved', 'lifetime_saved', 'has_custom_impact_payload', 'has_terrain_destruction']:
        assert row('earthquake_motion')[k] is False
    assert row('earthquake_motion')['owner_storage'] == 'NATIVE_PROJECTILE'
    assert row('monolith_chain')['attempted_entity_count'] == 144
    assert row('monolith_chain')['windmill_count'] == 128 and row('monolith_chain')['line_count'] == 16
    for k in ['requires_found_ceiling', 'sets_native_projectile_owner', 'has_terrain_destruction', 'local_spawn_server_guard']:
        assert row('monolith_chain')[k] is False
    for k in ['status_requires_hurt_true', 'enchantment_requires_hurt_true']:
        assert row('stele_contact')[k] is True
    for k in ['status_has_explicit_source', 'enchantment_requires_alive_after_hurt',
              'impact_discard_requires_hurt_true', 'damage_requires_activation', 'damage_requires_caster_alive']:
        assert row('stele_contact')[k] is False
    for k in ['owner_uuid_saved', 'damage_saved', 'warmup_saved', 'ray_precedes_activation', 'final_position_uses_pre_update_velocity']:
        assert row('stele_lifecycle')[k] is True
    for k in ['activation_saved', 'lifetime_saved', 'caster_death_cleanup', 'sets_native_projectile_owner', 'discard_returns_early', 'nbt_calls_parent']:
        assert row('stele_lifecycle')[k] is False
    assert row('stele_lifecycle')['nominal_active_decrements_before_removal'] == 71
    assert row('terrain_control')['grief_actor'] == 'BOSS'
    assert row('terrain_control')['ignore_mobgriefing_installed'] is True
    assert row('terrain_control')['has_destroy_event_hook'] is True
    for k in ['has_local_no_ai_gate', 'destroy_result_gates_debris', 'terrain_result_gates_damage', 'debris_adds_damage']:
        assert row('terrain_control')[k] is False
    assert row('alliance')['scoped_selector_tag'] == 'ANCIENT_REMNANT_TARGET'
    assert row('alliance')['scoped_team_tag'] == 'TEAM_ANCIENT_REMNANT'
    assert row('movement_control')['adds_victim_damage'] is False
    assert row('defeat_lifecycle')['death_removal_duration'] == 70
    assert row('defeat_lifecycle')['respawner_item'] == 'cataclysm:desert_eye'
    for k in ['death_state_write_checks_parent_admission', 'has_death_damage_payload', 'has_first_defeat_ledger']:
        assert row('defeat_lifecycle')[k] is False


def validate_preservation(review, note, ledger):
    assert note['starting_sha'] == START
    old = json.loads(at_start(REVIEW))
    assert [e for e in review['effects'] if e['review_checkpoint'] != CHECKPOINT] == old['effects']
    assert [p for p in review['paths'] if not p['id'].startswith('cataclysm:remnant-offense:')] == old['paths']
    mutable = {'effects', 'paths', 'checkpoint', 'scope', 'notes_file', 'exact_next_task', 'protected_checkpoints'}
    assert {k: v for k, v in review.items() if k not in mutable} == {k: v for k, v in old.items() if k not in mutable}
    assert review['protected_checkpoints'][:-1] == old['protected_checkpoints']
    assert review['protected_checkpoints'][-1] == dict(checkpoint=old['checkpoint'], notes_file=old['notes_file'])
    for reference in note['reference_files']:
        path = OUT / reference['file']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == reference['sha256'], reference['file']
        if reference['usage'] == 'LOCKED_REUSED':
            assert path.read_bytes() == at_start(path), reference['file']
    locked = note['protected_r2k7a']
    assert locked['file'] == 'cataclysm-r2k7a-remnant-admission.json'
    assert (OUT / locked['file']).read_bytes() == at_start(OUT / locked['file'])
    previous = json.loads(at_start(LEDGER))
    assert [t for t in ledger['targets'] if t['mod_key'] != 'cataclysm'] == [
        t for t in previous['targets'] if t['mod_key'] != 'cataclysm']
    assert {k: v for k, v in ledger.items() if k not in ['targets', 'checkpoint']} == {
        k: v for k, v in previous.items() if k not in ['targets', 'checkpoint']}


def validate_evidence(review, note, jar_path=None):
    assert read_json(SPEC_FILE) == specification()
    evidence = read_json(EVIDENCE_FILE)
    assert len(evidence['witnesses']) == 19
    assert {w['entry'] for w in evidence['witnesses']} == {
        PKG + n + '.class' for n in METHODS} | set(RESOURCES.values())
    if jar_path is not None:
        assert evidence == collect(jar_path), 'Pinned-JAR witnesses did not reproduce'
    census = {c['entry']: c['entry_sha256'] for c in read_json(OUT / 'cataclysm-source-census.json')['classes']}
    sources = {r['file']: read_json(OUT / r['file']) for r in note['reference_files']
               if r['file'].startswith('native-evidence/')}
    new_methods = {(w['entry'], m['name'], m['descriptor']): m
                   for w in evidence['witnesses'] for m in w.get('methods', [])}
    assert len(new_methods) == 127
    for f, data in sources.items():
        if f == EVIDENCE_FILE.relative_to(OUT).as_posix():
            continue
        for w in data['witnesses']:
            for old in w.get('methods', []):
                new = new_methods.get((w['entry'], old['name'], old['descriptor']))
                if new is not None:
                    assert 'instruction_offset_ranges' in new, 'Previously captured method duplicated'
                    assert new['code_sha256'] == old['code_sha256']
                    assert not {i['offset'] for i in new['instructions']} & {
                        i['offset'] for i in old['instructions']}, 'Previously captured fragment duplicated'
    for w in evidence['witnesses']:
        assert w['jar_sha256'] == note['tooling']['jar_sha256']
        if w['entry'].endswith('.class'):
            assert w['entry_sha256'] == census[w['entry']]
        else:
            assert w['entry'] in RESOURCES.values()
        for m in w.get('methods', []):
            if 'instruction_offset_ranges' in m:
                assert m['instruction_offset_ranges'] == FRAGMENTS[w['entry'][len(PKG):-6]][m['name']]
    for e in selected(review):
        for p in e['implementation']:
            w = next(w for w in sources[p['evidence_file']]['witnesses'] if w['id'] == p['witness_id'])
            assert p['entry'] == w['entry']
            assert set(p['methods']) <= {m['name'] for m in w.get('methods', [])}
    validate_native_boundaries(evidence)
    return len(new_methods)


def validate_native_boundaries(evidence):
    def body(n, method):
        w = next(w for w in evidence['witnesses'] if w['entry'] == PKG + n + '.class')
        return next(m['instructions'] for m in w['methods'] if m['name'] == method)

    def calls(ins, name):
        return [i['offset'] for i in ins if name in str(i.get('operand', ''))]

    def op(ins, offset):
        return next(i['opcode'] for i in ins if i['offset'] == offset)

    charge = body(R, 'Charge')
    assert calls(charge, '.hurt(') == [159]
    assert calls(charge, '.hurt(')[0] < calls(charge, '.onGround(')[0] < calls(charge, '.push(')[0]
    assert not calls(charge, '.hitZ') and not calls(charge, '.addEffect(')
    assert not calls(body(R + '$RemnantChargeGoal', 'start'), '.hitZ')
    assert calls(body(R + '$RemnantChargeGoal', 'start'), '.setRage(')
    assert not calls(body(R + '$RemnantMonolithAttackGoal', 'stop'), '.setRage(')
    assert calls(body(R + '$2', 'canContinueToUse'), '.getCrash(')
    assert calls(body(R + '$2', 'stop'), '.setCrash(')
    assert not calls(body(R + '$2', 'tick'), 'InternalStateGoal.tick(')
    assert len(calls(body(R + '$RemnantMonolithAttackGoal', 'canUse'), '.nextFloat(')) == 3
    assert not calls(body(R + '$RemnantMonolithAttackGoal', 'canUse'), 'InternalAttackGoal.canUse(')
    assert calls(body(R + '$RemnantStompGoal', 'start'), '.getIsPower(')
    assert not calls(body(R + '$RemnantStompGoal', 'start'), '.isPower(')
    stomp = body(R, 'spawnBlocks')
    assert calls(stomp, '.hurt(') == [383] and not calls(stomp, 'Math.min(')
    assert calls(stomp, '.addFreshEntity(')[0] < calls(stomp, '.hurt(')[0]
    assert calls(stomp, '.isDamageSourceBlocked(')[0] < calls(stomp, '.setDeltaMovement(')[0]
    assert not calls(stomp, '.destroyBlock(') and not calls(stomp, '.addEffect(')
    assert not calls(body(R, 'StompDamage'), '.destroyBlock(')
    assert not calls(body(R, 'EarthQuakeSummon'), 'isClientSide')
    assert not calls(body(R, 'EarthQuakeSummon'), '.hurt(')
    assert not calls(body(R + '$RemnantMonolithAttackGoal', 'spawnSpikeLine'), '.setOwner(')
    assert not calls(body(R + '$RemnantMonolithAttackGoal', 'spawnSpikeLine'), '.destroyBlock(')
    terrain = body(R, 'ChargeBlockBreaking')
    assert calls(terrain, '.onEntityDestroyBlock(') == [145]
    assert len(calls(terrain, '.destroyBlock(')) == 2 and not calls(terrain, '.hurt(')
    storm = body(S, 'tick')
    assert calls(storm, '.discard(') == [25]
    assert calls(storm, '.damage(') == [482]
    assert not any(i['opcode'] == '0xb1' and 25 < i['offset'] < 482 for i in storm)
    assert calls(body(S, 'addAdditionalSaveData'), '.putUUID(')
    assert not calls(body(S, 'addAdditionalSaveData'), '.getOffset(')
    quake = body(E, 'onUpdateInAir')
    assert calls(quake, '.hurt(') == [193] and op(quake, 196) == '0x99'
    assert calls(quake, '.strongKnockback(') == [205]
    assert not calls(quake, '.addEffect(') and not calls(quake, '.heal(')
    assert calls(quake, '.isAlliedTo(') == [163]
    assert not any(i['opcode'] == '0xb1' for i in quake)
    life = body(E, 'tick')
    assert calls(life, '.move(')[0] < calls(life, 'ThrowableProjectile.tick(')[0]
    assert not any(i['opcode'] == '0xb1' and 18 < i['offset'] < calls(life, 'ThrowableProjectile.tick(')[0] for i in life)
    stele = body(T, 'tick')
    assert calls(stele, '.onProjectileImpact(') == [27] and calls(stele, '.onHit(') == [35]
    assert calls(stele, '.onHit(')[0] < calls(stele, '.setWarmUp(')[0] < calls(stele, '.discard(')[0]
    assert calls(stele, '.move(')[0] < calls(stele, '.setPos(')[0]
    assert not calls(body(T, 'setCaster'), '.setOwner(')
    for method in ['addAdditionalSaveData', 'readAdditionalSaveData']:
        assert not calls(body(T, method), 'Projectile.' + method + '(')
    assert calls(body(T, 'addAdditionalSaveData'), '.putUUID(')
    assert calls(body(T, 'onHit'), 'Projectile.onHit(') == [2]
    assert calls(body(T, 'onHit'), '.discard(') == [135]
    assert body(T, 'onHitBlock') == [{'offset': 0, 'opcode': '0xb1', 'operand': None}]
    death = body(R, 'die')
    assert calls(death, '.die(') == [2] and calls(death, '.setAttackState(') == [7]
    assert not any(i['opcode'] in ['0x99', '0x9a'] for i in death)
    assert calls(body(R, 'AfterDefeatBoss'), 'ModItems.DESERT_EYE')
    assert not calls(body(R, 'onDeathAIUpdate'), '.hurt(')
    assert not calls(body(R, 'onDeathAIUpdate'), '.explode(')
    registry = next(w for w in evidence['witnesses'] if w['entry'] == PKG + REGISTRY + '.class')
    factories = {i: n for i, n in [(37, E), (30, S), (27, T)]}
    for index, entry in factories.items():
        bootstrap = next(b for b in registry['registration_bootstraps'] if b['index'] == index)
        assert PKG + entry + '.<init>' in bootstrap['arguments'][1]


def validate(jar_path=None):
    review, note, ledger = [read_json(p) for p in [REVIEW, NOTE, LEDGER]]
    summary = validate_records(review, note, ledger)
    validate_preservation(review, note, ledger)
    methods = validate_evidence(review, note, jar_path)
    return dict(status='PASS', **summary, new_method_witnesses=methods,
        protected_remnant_admission_shared_status_prior_bosses='BYTE_IDENTICAL',
        prior_records_and_paths='UNCHANGED',
        pinned_jar='REPRODUCED' if jar_path is not None else 'ARCHIVED_WITNESSES_VALIDATED')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jar', type=Path, help='Optional exact pinned Cataclysm 3.27 JAR')
    print(json.dumps(validate(parser.parse_args().jar), indent=2))
