"""Focused read-only R2k6b record, return-boundary and pinned-JAR validation."""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import subprocess

from catalog_common import OUT, ROOT, read_json
from collect_cataclysm_harbinger_offense import (
    D, EVIDENCE_FILE, FRAGMENTS, H, HM, HOW, L, M, SM, PKG, RESOURCES, SPEC_FILE, TIMER,
    collect, specification,
)

START = '1e428ed3649fbb6142c8abe24f930c253053da07'
CHECKPOINT = 'R2k6b-cataclysm-harbinger-offense-complete'
NOTE = OUT / 'cataclysm-r2k6b-harbinger-offense.json'
REVIEW = OUT / 'mod-reviews/cataclysm.json'
LEDGER = OUT / 'mod-completion-ledger.json'
KINDS = {'VANILLA_DIRECT', 'VANILLA_EQUIVALENT', 'VANILLA_LIKE_EXTENDED',
         'VANILLA_COMPOSITE', 'CUSTOM_DAMAGE', 'CUSTOM_STATUS',
         'CUSTOM_CONTROL', 'CUSTOM_RESOURCE', 'BINARY_MECHANIC'}
KEYS = {'attack_selection', 'head_targeting', 'flight_control', 'charge_chain',
        'charge_contact', 'launch_chain', 'missile_volley', 'ranged_dispatch',
        'missile_contact', 'missile_motion', 'homing_contact', 'homing_motion',
        'howitzer_contact', 'howitzer_burst', 'smoke_payload', 'smoke_lifecycle',
        'laser_contact', 'laser_motion', 'laser_terrain', 'death_laser_chain',
        'death_laser_payload', 'death_laser_lifecycle', 'death_laser_terrain',
        'terrain_control', 'alliance', 'status_admission', 'defeat_lifecycle'}


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
    assert {e['id'] for e in new} == {'cataclysm:harbinger_' + k for k in KEYS}
    pids, eids = {p['id'] for p in paths}, {e['id'] for e in effects}
    for e in new:
        assert e['mod_key'] == 'cataclysm' and e['primary_classification'] in KINDS
        assert e['inspection_status'] == 'STATIC_REVIEWED' and not e['unresolved_ambiguities']
        assert e['components'] and e['implementation'] and e['primary_test_source']
        assert e['source_actor'] and e['hurt_return_dependency']
        assert e['delivery_paths'] and set(e['delivery_paths']) <= pids
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
    new_paths = [p for p in paths if p['id'].startswith('cataclysm:harbinger-offense:')]
    assert len(new_paths) == 27
    for p in new_paths:
        assert p['mod_key'] == 'cataclysm' and p['status'] == 'VERIFIED'
        assert p['primary_source'] and p['native_path'] and p['setup'] and p['implementation']
        assert p['labels'] and p['runtime_status'] == 'NOT_RUN'
        assert p['effect_ids'] and set(p['effect_ids']) <= eids
        for e in new:
            assert (p['id'] in e['delivery_paths']) == (e['id'] in p['effect_ids'])
    rows = {e['id']: e for e in new}
    payloads = note['payload_entities']
    assert {p['entry'] for p in payloads} == {PKG + n + '.class' for n in [M, HM, HOW, L, D, SM,
        'entity/effect/Cm_Falling_Block_Entity']}
    assert len(payloads) == 7
    for p in payloads:
        assert p['source_mechanic_ids'] and set(p['source_mechanic_ids']) <= rows.keys()
        assert set(p['payload_mechanic_ids']) <= rows.keys()
        assert p['source_actor'] and p['native_lifecycle']
        for producer in p['source_mechanic_ids']:
            assert p['entity_id'] in rows[producer]['spawned_entity_ids']
        assert bool(p['payload_mechanic_ids']) == (p['role'] != 'NON_DAMAGE_DEBRIS_VERIFIED')
    assert note['mechanic_packages'] == [dict(id=e['id'],
        primary_classification=e['primary_classification'], delivery_paths=e['delivery_paths'],
        numerical_candidates=[{k: c[k] for k in ['primitive', 'parameters', 'native_value',
            'units', 'native_boundary']} for c in e['scalable_parameter_candidates']],
        binary_gates=e['binary_parameters'], hurt_return_dependency=e['hurt_return_dependency']) for e in new]
    summary = dict(new_mechanics=len(new), delivery_paths=len(new_paths),
        classifications=dict(sorted(Counter(e['primary_classification'] for e in new).items())),
        candidate_numeric_parameters=sum(len(c['parameters']) for e in new for c in e['scalable_parameter_candidates']),
        unresolved_subsection_ambiguities=0, new_owned_payload_classes=6, reused_non_damage_debris_classes=1)
    assert summary == note['summary'] and summary['candidate_numeric_parameters'] == 88
    assert review['status'] == ledger['status'] == note['status'] == 'PARTIAL'
    for field in ['semantic_discovery_complete', 'special_damage_discovery_complete',
                  'source_mapping_complete', 'delivery_mapping_complete']:
        assert review[field] is False
    cat = next(t for t in ledger['targets'] if t['mod_key'] == 'cataclysm')
    assert cat['state'] == 'PARTIAL' and cat['semantic_effect_count'] == len(effects)
    assert review['checkpoint'] == ledger['checkpoint'] == note['checkpoint'] == CHECKPOINT
    assert review['exact_next_task'] == note['exact_next_task'] == cat['exact_next_task']
    assert note['exact_next_task'].startswith('R2k7a: Ancient Remnant incoming admission and phase/encounter prerequisites.')
    assert note['harbinger_family_closed'] is True and not note['remaining_harbinger_work']
    assert not note['remaining_subsection_native_ambiguities'] and note['remaining_cataclysm_research']
    assert note['whole_mod_complete'] is False and note['runtime_tests'] == 0
    assert all(note[k] is False for k in ['stage_eligibility_decided', 'phase6_reopened',
        'production_changed', 'stage_changed', 'boss_testing_started', 'l2_testing_started',
        'compatibility_fixes_started', 'phase7_started'])
    validate_contracts(rows)
    return summary


def validate_contracts(rows):
    def row(k):
        return rows['cataclysm:harbinger_' + k]

    assert row('attack_selection')['selection_order'] == ['DEATHLASER', 'CHARGE', 'LAUNCH', 'MISSILE']
    assert row('attack_selection')['rolls_short_circuit'] is True
    assert row('attack_selection')['local_server_guard'] is False
    assert row('head_targeting')['side_head_dispatch_indices'] == [2, 3]
    assert row('head_targeting')['side_head_storage_slots'] == [1, 2]
    assert row('head_targeting')['idle_head_counter_read_for_shot'] is False
    assert row('head_targeting')['stale_id_has_instanceof_guard'] is False
    assert row('flight_control')['movement_is_native_knockback'] is False
    assert row('flight_control')['pursuit_reads_is_act'] is False
    assert row('flight_control')['pursuit_reads_no_ai'] is False
    assert row('charge_chain')['movement_is_native_knockback'] is False
    assert row('charge_chain')['charge_window'] == [24, 36]
    assert row('charge_chain')['stop_requires_los'] is False
    assert row('charge_chain')['stop_requires_cooldown'] is False
    assert row('charge_contact')['push_requires_hurt_true'] is True
    assert row('charge_contact')['push_requires_on_ground'] is True
    assert row('charge_contact')['terrain_result_gates_damage'] is False
    assert row('charge_contact')['local_damage_server_guard'] is False
    assert row('launch_chain')['launch_ticks'] == [13, 19]
    assert row('launch_chain')['power_read_at_each_launch'] is True
    assert row('missile_volley')['normal_ticks'] == {'2': [80, 84, 88], '1': [98, 102, 106]}
    assert row('missile_volley')['fast_ticks'] == [71, 75, 79]
    assert row('missile_volley')['shots_per_goal'] == 6
    assert row('ranged_dispatch')['caller_gate_rechecked'] is False
    assert row('ranged_dispatch')['constructor_damage_bindings'] == {'laser': 5.0, 'missile': 8.0}
    for k, fallback in [('missile_contact', 5.0), ('homing_contact', 3.0)]:
        r = row(k)
        assert r['direct_has_ally_check'] is False and r['kill_heal_call_count'] == 2
        assert r['status_requires_hurt_true'] is True and r['status_requires_victim_alive'] is False
        assert r['explosion_requires_hurt_true'] is False and r['anonymous_fallback_damage'] == fallback
    assert row('howitzer_contact')['kill_heal_call_count'] == 1
    assert row('howitzer_contact')['other_difficulty_duration'] == 200
    assert row('homing_motion')['steering_speed_reassigned_to_inertia'] is True
    assert row('homing_motion')['terminal_branches_mutually_exclusive'] is False
    assert row('homing_motion')['continues_after_discard'] is True
    assert row('homing_motion')['fuse_saved_as_short'] is True
    assert row('homing_motion')['target_equals_owner'] is False
    for k in ['missile_motion', 'homing_motion', 'laser_motion']:
        assert row(k)['damage_saved'] is False
    for k in ['missile_motion', 'laser_motion']:
        assert row(k)['has_lifetime_timer'] is False
    assert row('howitzer_burst')['explosion_requires_hurt_true'] is False
    assert row('howitzer_burst')['smoke_requires_hurt_true'] is False
    assert row('howitzer_burst')['radius_on_use_consumed'] is False
    for k, radius in [('missile_contact', 1.0), ('homing_contact', 1.0),
                      ('homing_motion', 1.0), ('howitzer_burst', 2.0), ('defeat_lifecycle', 7.0)]:
        explosion = next(c for c in row(k)['components'] if c['primitive'] == 'NATIVE_EXPLOSION')
        assert explosion['numerical_parameters'] == {'radius': radius}
        assert explosion['vanilla_relation'] == 'VANILLA_DIRECT'
    assert row('smoke_payload')['has_radial_distance_check'] is False
    assert row('smoke_payload')['has_victim_reuse_cache'] is False
    assert row('smoke_payload')['has_bilateral_allied_check'] is True
    assert row('smoke_payload')['status_has_explicit_source'] is False
    assert row('smoke_payload')['status_requires_hurt_true'] is True
    for k, expected in [('owner_uuid_saved', False), ('owner_uuid_read', True),
                        ('radius_on_use_consumed', False), ('duration_on_use_consumed', False)]:
        assert row('smoke_lifecycle')[k] is expected
    assert row('laser_contact')['burn_restored_on_hurt_false'] is True
    assert row('laser_contact')['enchantment_requires_alive_after_hurt'] is False
    assert row('laser_contact')['entity_hit_discards'] is False
    assert row('laser_contact')['has_ally_check'] is False and row('laser_contact')['has_explosion'] is False
    assert row('laser_motion')['has_water_inertia_override'] is False
    assert row('death_laser_chain')['spawn_tick'] == 18 and row('death_laser_chain')['power_fire_snapshotted'] is True
    assert row('death_laser_chain')['spawn_requires_target'] is False
    r = row('death_laser_payload')
    assert r['hp_percent_factor'] == 0.01 and r['burn_requires_hurt_true'] is True
    assert all(r[k] is False for k in ['has_heal_call', 'has_enchantment_callback',
        'dispatch_requires_on', 'dispatch_checks_caster_alive'])
    damage = next(c for c in r['components'] if c['primitive'] == 'CUSTOM_DAMAGE_REQUEST')
    assert damage['numerical_parameters'] == dict(base_damage=5.0, hp_damage=0.05, percent_factor=0.01)
    assert damage['damage_type'] == 'cataclysm:deathlaser'
    assert damage['shipped_tags'] == ['minecraft:bypasses_armor', 'minecraft:bypasses_shield', 'minecraft:panic_causes']
    laser = next(c for c in row('laser_contact')['components'] if c['primitive'] == 'CUSTOM_DAMAGE_REQUEST')
    assert laser['damage_type'] == 'cataclysm:laser' and laser['shipped_tags'] == ['minecraft:is_projectile', 'minecraft:panic_causes']
    life = row('death_laser_lifecycle')
    assert life['native_nbt_empty'] is True and life['caster_uuid_saved'] is False
    assert life['discard_returns_early'] is False and life['ray_entity_clip_uses_full_endpoint'] is True
    assert life['default_dispatch_window'] == [21, 85] and life['default_possible_dispatch_ticks'] == 65
    assert row('death_laser_terrain')['emp_reset_has_grief_gate'] is False
    assert row('death_laser_terrain')['grief_actor'] == 'BEAM_ENTITY'
    assert row('death_laser_terrain')['glass_has_destroy_event_hook'] is False
    for k in ['debris_adds_damage', 'reads_ignore_mobgriefing', 'idle_has_destroy_event_hook',
              'reactive_timer_decrements_during_stun']:
        assert row('terrain_control')[k] is False
    assert row('alliance')['scoped_selector_tag'] == 'TEAM_THE_HARBINGER'
    assert row('alliance')['none_targets_tag_read'] is False
    assert row('status_admission')['excluded_native_effects'] == [
        'minecraft:slowness', 'minecraft:poison', 'minecraft:wither', 'minecraft:weakness', 'minecraft:levitation']
    assert row('defeat_lifecycle')['death_animation_duration'] == 144
    assert row('defeat_lifecycle')['death_removal_duration'] == 124
    assert row('defeat_lifecycle')['death_explosion_time'] == 123
    assert row('defeat_lifecycle')['respawner_item'] == 'cataclysm:mech_eye'
    assert row('defeat_lifecycle')['has_first_defeat_ledger'] is False


def validate_preservation(review, note, ledger):
    assert note['starting_sha'] == START
    old = json.loads(at_start(REVIEW))
    assert [e for e in review['effects'] if e['review_checkpoint'] != CHECKPOINT] == old['effects']
    assert [p for p in review['paths'] if not p['id'].startswith('cataclysm:harbinger-offense:')] == old['paths']
    mutable = {'effects', 'paths', 'checkpoint', 'scope', 'notes_file', 'exact_next_task', 'protected_checkpoints'}
    assert {k: v for k, v in review.items() if k not in mutable} == {k: v for k, v in old.items() if k not in mutable}
    assert review['protected_checkpoints'][:-1] == old['protected_checkpoints']
    assert review['protected_checkpoints'][-1]['checkpoint'] == old['checkpoint']
    for reference in note['reference_files']:
        path = OUT / reference['file']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == reference['sha256'], reference['file']
        if reference['usage'] == 'LOCKED_REUSED':
            assert path.read_bytes() == at_start(path), reference['file']
    locked = note['protected_r2k6a']
    assert locked['file'] == 'cataclysm-r2k6a-harbinger-admission.json'
    assert (OUT / locked['file']).read_bytes() == at_start(OUT / locked['file'])
    previous = json.loads(at_start(LEDGER))
    assert [t for t in ledger['targets'] if t['mod_key'] != 'cataclysm'] == [
        t for t in previous['targets'] if t['mod_key'] != 'cataclysm']
    assert {k: v for k, v in ledger.items() if k not in ['targets', 'checkpoint']} == {
        k: v for k, v in previous.items() if k not in ['targets', 'checkpoint']}


def validate_evidence(review, note, jar_path=None):
    assert read_json(SPEC_FILE) == specification()
    evidence = read_json(EVIDENCE_FILE)
    assert len(evidence['witnesses']) == 18
    if jar_path is not None:
        assert evidence == collect(jar_path), 'Pinned-JAR witnesses did not reproduce'
    census = {c['entry']: c['entry_sha256'] for c in read_json(OUT / 'cataclysm-source-census.json')['classes']}
    sources = {r['file']: read_json(OUT / r['file']) for r in note['reference_files']
               if r['file'].startswith('native-evidence/')}
    new_methods = {(w['entry'], m['name'], m['descriptor']): m
                   for w in evidence['witnesses'] for m in w.get('methods', [])}
    assert len(new_methods) == 191
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
    validate_native_returns(evidence)
    return len(new_methods)


def validate_native_returns(evidence):
    def body(n, method):
        w = next(w for w in evidence['witnesses'] if w['entry'] == PKG + n + '.class')
        return next(m['instructions'] for m in w['methods'] if m['name'] == method)

    def calls(ins, name):
        return [i['offset'] for i in ins if name in str(i.get('operand', ''))]

    def op(ins, offset):
        return next(i['opcode'] for i in ins if i['offset'] == offset)

    def constants(ins):
        return [i['operand'] for i in ins if i['opcode'] in ['0x12', '0x13', '0x14']]

    for n in [M, HM]:
        hit = body(n, 'onHitEntity')
        assert len(calls(hit, '.heal(')) == 3  # first5 + mutually exclusive second calls
        assert len(calls(hit, '.hurt(')) == 2  # owned vs anonymous alternatives
        assert not calls(hit, '.isAlliedTo(')
        assert len(calls(hit, '.addEffect(')) == 1
        assert op(hit, calls(hit, '.addEffect(')[0] + 3) == '0x57'
    how = body(HOW, 'onHitEntity')
    assert len(calls(how, '.heal(')) == 2  # mutually exclusive one-call branches
    assert not calls(how, '.isAlliedTo(')
    for n, method in [(M, 'onHit'), (HM, 'onHitEntity'), (HM, 'onHitBlock'), (HOW, 'onHit')]:
        burst = body(n, method)
        assert len(calls(burst, '.explode(')) == 1
        assert calls(burst, 'ExplosionInteraction.NONE')
    homing = body(HM, 'tick')
    assert len(calls(homing, '.explode(')) == 2 and len(calls(homing, '.discard(')) == 3
    assert calls(homing, '.assignDirectionalMovement(')
    smoke = body(SM, 'damage')
    assert len(calls(smoke, '.isAlliedTo(')) == 2 and not calls(smoke, '.heal(')
    assert not calls(smoke, '.getRadiusOnUse(') and not calls(body(SM, 'tick'), 'radiusOnUse')
    assert not calls(body(SM, 'tick'), 'durationOnUse')
    assert calls(body(SM, 'readAdditionalSaveData'), '.hasUUID(')
    assert not calls(body(SM, 'addAdditionalSaveData'), '.putUUID(')
    laser = body(L, 'onHitEntity')
    assert calls(laser, '.igniteForSeconds(')[0] < calls(laser, '.hurt(')[0] < calls(laser, '.setRemainingFireTicks(')[0]
    assert not calls(laser, '.isAlive(') and not calls(laser, '.isAlliedTo(')
    assert not calls(laser, '.heal(')
    for n in [M, HM, L]:
        save = body(n, 'addAdditionalSaveData')
        assert not calls(save, '.getDamage(')
        assert calls(save, 'acceleration_power')
    life = body(D, 'tick')
    assert calls(life, '.hurt(') == [887] and calls(life, '.igniteForSeconds(') == [908]
    assert 0.01 in constants(life)
    assert calls(life, '.discard(') == [214, 268]
    assert not any(i['opcode'] == '0xb1' and 214 < i['offset'] < 887 for i in life)
    for method in ['addAdditionalSaveData', 'readAdditionalSaveData']:
        assert body(D, method) == [{'offset': 0, 'opcode': '0xb1', 'operand': None}]
    ray = body(D, 'raytraceEntities')
    assert calls(ray, '.clip(') and not calls(ray, '.isAlive(') and not calls(ray, 'noPhysics')
    assert calls(body(TIMER, 'increaseTimer'), 'duration') and calls(body(TIMER, 'decreaseTimer'), 'timer')
    charge = body(H, 'blockbreak')
    assert calls(charge, '.hurt(') and calls(charge, '.onGround(') and calls(charge, '.push(')
    assert not calls(body(H, 'destoryblock2'), '.onEntityDestroyBlock(')
    assert calls(body(H, 'destroyBlock'), '.onEntityDestroyBlock(')
    assert not calls(body(H, 'destoryblock2'), 'ignoreMobGriefing')
    assert not calls(body(D, 'tick'), '.onEntityDestroyBlock(')
    assert not calls(body(D, 'tick'), '.heal(')
    assert calls(body(H, 'AfterDefeatBoss'), 'ModItems.MECH_EYE')
    assert calls(body(H, 'onDeathAIUpdate'), '.explode(')
    for n in [H+'$ChargeGoal', H+'$LaunchGoal', H+'$MissileLaunchGoal', H+'$MissileLaunchGoal2']:
        assert calls(body(n, 'start'), '.setOverload(')
    assert calls(body(H+'$DeathLaserGoal', 'start'), '.setOverload(')
    assert calls(body(H, 'aiStep'), '.setAnimation(') == [577, 686, 757, 836]


def validate(jar_path=None):
    review, note, ledger = [read_json(p) for p in [REVIEW, NOTE, LEDGER]]
    summary = validate_records(review, note, ledger)
    validate_preservation(review, note, ledger)
    methods = validate_evidence(review, note, jar_path)
    return dict(status='PASS', **summary, new_method_witnesses=methods,
        protected_harbinger_admission_shared_status_guardian_monstrosity_ignis='BYTE_IDENTICAL',
        prior_records_and_paths='UNCHANGED',
        pinned_jar='REPRODUCED' if jar_path is not None else 'ARCHIVED_WITNESSES_VALIDATED')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jar', type=Path, help='Optional exact pinned Cataclysm 3.27 JAR')
    print(json.dumps(validate(parser.parse_args().jar), indent=2))
