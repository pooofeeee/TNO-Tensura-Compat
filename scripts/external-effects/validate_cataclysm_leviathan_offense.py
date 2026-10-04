"""Focused read-only R2k9b records, protected contracts and pinned-JAR checks."""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import struct
import subprocess

from catalog_common import OUT, ROOT, read_json
from collect_cataclysm_leviathan_offense import (
    EVIDENCE_FILE, FAMILY, FRAGMENTS, GOALS, L, METHODS, PKG, REG,
    RESOURCES, SPEC_FILE, collect, specification,
)

START = '4f31fffddda43e955dc7adf1c26a9cbe6647ba92'
CHECKPOINT = 'R2k9b-cataclysm-leviathan-offense-complete'
NOTE = OUT / 'cataclysm-r2k9b-leviathan-offense.json'
REVIEW = OUT / 'mod-reviews/cataclysm.json'
LEDGER = OUT / 'mod-completion-ledger.json'
KINDS = {'VANILLA_DIRECT', 'VANILLA_EQUIVALENT', 'VANILLA_LIKE_EXTENDED',
         'VANILLA_COMPOSITE', 'CUSTOM_DAMAGE', 'CUSTOM_STATUS',
         'CUSTOM_CONTROL', 'CUSTOM_RESOURCE', 'BINARY_MECHANIC'}
KEYS = {
    'alliance',
    'attack_selection',
    'beam_burst_delivery',
    'beam_contact',
    'beam_geometry',
    'beam_lifecycle',
    'beam_single_delivery',
    'beam_terrain',
    'bite_contact',
    'bite_delivery',
    'blast_portal_delivery',
    'blast_portal_lifecycle',
    'defeat_lifecycle',
    'held_beam_delivery',
    'held_victim_control',
    'hold_contact',
    'hold_control',
    'mine_delivery',
    'mine_lifecycle',
    'mine_trigger',
    'orb_contact',
    'orb_lifecycle',
    'orb_motion',
    'orb_terminal_explosion',
    'orb_volley',
    'portal_lifecycle',
    'portal_teleport',
    'rift_damage',
    'rift_delivery',
    'rift_lifecycle',
    'rift_pull',
    'rift_terminal_explosion',
    'rift_terrain',
    'roar_darkness',
    'rush_movement',
    'sequence_state',
    'stuck_portal_delivery',
    'tail_contact',
    'tentacle_contact',
    'terrain_control',
    'tongue_contact',
    'tongue_delivery',
    'tongue_lifecycle',
    'tongue_motion',
    'water_movement',
}


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
    assert {e['id'] for e in new} == {'cataclysm:leviathan_' + k for k in KEYS}
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
            assert len(owners) == 1, 'Candidate lost its native primitive'
            owner = owners[0]
            assert c['native_value'] == owner['numerical_parameters'][p]
            assert c['native_formula'] == owner['formula']
            assert c['units'] == owner['parameter_units'][p]
            assert c['native_boundary'] == owner['native_boundary']
        if e['primary_classification'] == 'BINARY_MECHANIC':
            assert not candidates
    new_paths = [p for p in paths if p['id'].startswith('cataclysm:leviathan-offense:')]
    assert len(new_paths) == len(KEYS)
    for p in new_paths:
        assert p['mod_key'] == 'cataclysm' and p['status'] == 'VERIFIED'
        assert p['primary_source'] and p['native_path'] and p['setup'] and p['implementation']
        assert p['labels'] and p['runtime_status'] == 'NOT_RUN'
        assert p['effect_ids'] and set(p['effect_ids']) <= eids
        for e in new:
            assert (p['id'] in e['delivery_paths']) == (e['id'] in p['effect_ids'])
    rows = {e['id']: e for e in new}
    payloads = note['payload_entities']
    assert {p['entry'] for p in payloads} == {PKG + FAMILY + n + '.class' for n in [
        'Abyss_Blast_Entity', 'Portal_Abyss_Blast_Entity', 'Abyss_Blast_Portal_Entity',
        'Abyss_Orb_Entity', 'Abyss_Mine_Entity', 'Dimensional_Rift_Entity',
        'Abyss_Portal_Entity', 'The_Leviathan_Tongue_Entity']} | {
        PKG + 'entity/effect/Cm_Falling_Block_Entity.class'}
    assert len(payloads) == 9
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
        unresolved_subsection_ambiguities=0, new_owned_payload_classes=8, reused_non_damage_debris_classes=1)
    assert summary == note['summary'] and summary['candidate_numeric_parameters'] == 107
    assert review['status'] == ledger['status'] == note['status'] == 'PARTIAL'
    for f in ['semantic_discovery_complete', 'special_damage_discovery_complete',
              'source_mapping_complete', 'delivery_mapping_complete']:
        assert review[f] is False
    cat = next(t for t in ledger['targets'] if t['mod_key'] == 'cataclysm')
    assert cat['state'] == 'PARTIAL' and cat['semantic_effect_count'] == len(effects)
    assert review['checkpoint'] == ledger['checkpoint'] == note['checkpoint'] == CHECKPOINT
    assert review['exact_next_task'] == note['exact_next_task'] == cat['exact_next_task']
    assert note['exact_next_task'].startswith('R2k10a: Scylla incoming admission and phase/encounter prerequisites.')
    assert note['leviathan_family_closed'] is True and not note['remaining_leviathan_work']
    assert not note['remaining_subsection_native_ambiguities'] and note['remaining_cataclysm_research']
    assert note['whole_mod_complete'] is False and note['runtime_tests'] == 0
    assert all(note[k] is False for k in ['stage_eligibility_decided', 'phase6_reopened',
        'production_changed', 'stage_changed', 'boss_testing_started', 'l2_testing_started',
        'compatibility_fixes_started', 'phase7_started'])
    validate_contracts(rows)
    return summary


def validate_contracts(rows):
    def row(key):
        return rows['cataclysm:leviathan_' + key]

    def params(key, primitive):
        return next(c['numerical_parameters'] for c in row(key)['components'] if c['primitive'] == primitive)

    f32 = lambda x: struct.unpack('f', struct.pack('f', x))[0]
    expected = {
        'attack_selection': dict(selection_is_goal_scheduled=True, directly_used_offensive_goal_classes=16,
            independent_random_draws=True, selection_counters_are_stage_scalars=False),
        'sequence_state': dict(unused_charge_helpers_promoted=False, countdown_local_server_guard=False,
            per_tick_mode_decrement_goals=['LeviathanMineAttackGoal', 'LeviathanTailWhipsAttackGoal', 'LeviathanTentacleHoldAttackGoal']),
        'rush_movement': dict(rush_requests_contact_damage=False),
        'water_movement': dict(water_motion_is_knockback=False),
        'bite_contact': dict(hp_config_field='TentacleHpDamage', shield_disable_requires_hurt_true=False, status_requires_hurt_true=True),
        'bite_delivery': dict(bite_method_reused=True),
        'tentacle_contact': dict(shield_disable_requires_hurt_true=False, movement_requires_hurt_true=True, movement_is_native_knockback=False),
        'tail_contact': dict(tail_method_reused=True, shield_disable_requires_hurt_true=False, movement_is_native_knockback=False),
        'hold_contact': dict(damage_has_hp_min_cap=False),
        'hold_control': dict(ride_result_controls_animation=False, forced_ride=True),
        'held_victim_control': dict(release_returns_before_positioning=False),
        'roar_darkness': dict(darkness_requires_hurt_true=False),
        'orb_volley': dict(sets_native_projectile_owner=True, damage_snapshot_at_launch=True, local_spawn_server_guard=True),
        'orb_motion': dict(impact_event_preserved=True, homing_uses_distance_squared=True, homing_has_distance_floor=False),
        'orb_contact': dict(fear_requires_hurt_true=True, explosion_requires_hurt_true=False, local_ally_predicate=False),
        'orb_terminal_explosion': dict(explosion_requires_hurt_true=False, applies_fear=False),
        'orb_lifecycle': dict(tracking_save_key='tracking', tracking_load_key='fired', lifetick_saved=False),
        'mine_delivery': dict(local_spawn_server_guard=False, mine_requires_ground_support=False),
        'mine_trigger': dict(fear_requires_hurt_true=False, activation_flag_gates_explosion=False, loop_breaks_after_remove=False),
        'mine_lifecycle': dict(saved_lifetime=False),
        'rift_delivery': dict(growth_checks_owner=False, native_rift_stage_is_tno_stage=False, look_query_is_nearest_to_boss=False),
        'rift_pull': dict(pull_has_local_server_guard=False, pull_uses_owner_alliance=False),
        'rift_damage': dict(damage_reads_dimensional_rift_config=False, damage_has_local_server_guard=False),
        'rift_terrain': dict(debris_deals_damage=False),
        'rift_terminal_explosion': dict(explosion_resolves_owner=False),
        'rift_lifecycle': dict(ordinal_is_clamped=False, close_flag_saved=False),
        'beam_single_delivery': dict(damage_snapshot_at_launch=True, local_spawn_server_guard=True),
        'beam_burst_delivery': dict(damage_snapshot_at_launch=True, local_spawn_server_guard=True),
        'held_beam_delivery': dict(local_spawn_server_guard=True),
        'beam_contact': dict(beam_ticks_reused=True, hp_formula_has_percent_unit_factor=True, burn_requires_hurt_true=True, beam_is_projectile=False),
        'beam_geometry': dict(entity_segment_ends_at_block_clip=False, uses_projectile_impact_event=False),
        'beam_lifecycle': dict(ordinary_damage_saved=True, portal_damage_saved=False, caster_saved=False, server_caster_uuid_restore=False),
        'beam_terrain': dict(has_native_explosion=False, has_entity_destroy_hook=False),
        'blast_portal_delivery': dict(local_spawn_server_guard=False, upper_portal_helper_used=False),
        'blast_portal_lifecycle': dict(raw_caster_guard_before_resolver=True, life_ticks_saved=False),
        'stuck_portal_delivery': dict(root_stuck_requires_water=False),
        'portal_teleport': dict(has_local_team_filter=False, changes_dimension=False, deduplicates_recipients=False),
        'portal_lifecycle': dict(entrance_saved=False, destination_loaded_before_sister=True),
        'tongue_delivery': dict(bite_transition_requires_tongue_hit=False),
        'tongue_contact': dict(hurt_evaluated_before_server_guard=True, return_flag_requires_hurt_true=False, mount_force=False, local_team_filter=False),
        'tongue_motion': dict(target_read_precedes_server_refresh=True, movement_is_knockback=False),
        'tongue_lifecycle': dict(max_duration_load_calls_set_duration=True, self_discards_at_duration_limit=False, has_entity_destroy_hook=False),
        'terrain_control': dict(incoming_response_has_destroy_hook=True, melee_response_has_destroy_hook=False, debris_deals_damage=False),
        'defeat_lifecycle': dict(concrete_respawner_spawned=False, defeat_world='OVERWORLD'),
    }
    for key, facts in expected.items():
        for name, value in facts.items():
            assert row(key)[name] == value, (key, name)
    assert params('bite_contact', 'NATIVE_DAMAGE_REQUEST') == dict(attack_coefficient=1.5, hp_coefficient=f32(.06))
    assert params('tentacle_contact', 'NATIVE_DAMAGE_REQUEST')['hp_coefficient'] == f32(.06)
    assert params('tail_contact', 'NATIVE_DAMAGE_REQUEST')['hp_coefficient'] == f32(.06)
    assert params('hold_contact', 'NATIVE_DAMAGE_REQUEST')['hp_coefficient'] == f32(.1)
    assert 'STUN_DELIVERY' in {c['primitive'] for c in row('bite_contact')['components']}
    assert 'BONE_FRACTURE_DELIVERY' in {c['primitive'] for c in row('tail_contact')['components']}
    assert 'DARKNESS_DELIVERY' in {c['primitive'] for c in row('roar_darkness')['components']}
    assert not {'STUN_DELIVERY', 'DARKNESS_DELIVERY'} & {c['primitive'] for c in row('tail_contact')['components']}
    assert params('orb_volley', 'PROJECTILE_DELIVERY')['normal_volley_count'] == 12
    assert params('orb_volley', 'PROJECTILE_DELIVERY')['phase_volley_count'] == 24
    assert params('orb_motion', 'PROJECTILE_MOTION')['inertia'] == f32(.6)
    assert params('orb_terminal_explosion', 'NATIVE_EXPLOSION')['strength'] == 1.0
    assert params('rift_damage', 'NATIVE_DAMAGE_REQUEST')['amount'] == 10.0
    assert params('rift_terminal_explosion', 'NATIVE_EXPLOSION')['strength'] == 4.0
    assert params('beam_contact', 'NATIVE_DAMAGE_REQUEST') == dict(damage=10.0, hp_damage=f32(.1), hp_unit_factor=.01)
    assert 'min(' in next(c['formula'] for c in row('beam_contact')['components'] if c['primitive'] == 'NATIVE_DAMAGE_REQUEST')
    assert params('beam_geometry', 'AREA_SELECTION') == dict(range=50.0, ordinary_query_inflation=2.0,
        ordinary_victim_pad=.5, portal_query_inflation=1.0, portal_victim_pad=f32(1.3))
    assert params('beam_single_delivery', 'BEAM_DELIVERY')['duration'] == 80
    assert params('beam_burst_delivery', 'BEAM_DELIVERY') == dict(count=3, interval=45, duration=28)
    assert params('blast_portal_lifecycle', 'BEAM_DELIVERY')['duration'] == 160
    assert params('tongue_contact', 'NATIVE_DAMAGE_REQUEST')['amount'] == 6.0
    assert params('tongue_delivery', 'TONGUE_DELIVERY')['max_duration'] == 120


def validate_preservation(review, note, ledger):
    assert note['starting_sha'] == START
    old = json.loads(at_start(REVIEW))
    assert [e for e in review['effects'] if e['review_checkpoint'] != CHECKPOINT] == old['effects']
    assert [p for p in review['paths'] if not p['id'].startswith('cataclysm:leviathan-offense:')] == old['paths']
    mutable = {'effects', 'paths', 'checkpoint', 'scope', 'notes_file', 'exact_next_task', 'protected_checkpoints'}
    assert {k: v for k, v in review.items() if k not in mutable} == {k: v for k, v in old.items() if k not in mutable}
    assert review['protected_checkpoints'][:-1] == old['protected_checkpoints']
    assert review['protected_checkpoints'][-1] == dict(checkpoint=old['checkpoint'], notes_file=old['notes_file'])
    for r in note['reference_files']:
        path = OUT / r['file']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == r['sha256'], r['file']
        if r['usage'] == 'LOCKED_REUSED':
            assert path.read_bytes() == at_start(path), r['file']
    locked = note['protected_r2k9a']
    assert locked['file'] == 'cataclysm-r2k9a-leviathan-admission.json'
    assert (OUT / locked['file']).read_bytes() == at_start(OUT / locked['file'])
    previous = json.loads(at_start(LEDGER))
    assert [t for t in ledger['targets'] if t['mod_key'] != 'cataclysm'] == [
        t for t in previous['targets'] if t['mod_key'] != 'cataclysm']
    assert {k: v for k, v in ledger.items() if k not in ['targets', 'checkpoint']} == {
        k: v for k, v in previous.items() if k not in ['targets', 'checkpoint']}


def validate_evidence(review, note, jar_path=None):
    assert read_json(SPEC_FILE) == specification()
    evidence = read_json(EVIDENCE_FILE)
    assert len(evidence['witnesses']) == 29
    assert {w['entry'] for w in evidence['witnesses']} == {
        PKG + n + '.class' for n in METHODS} | set(RESOURCES.values())
    if jar_path is not None:
        assert evidence == collect(jar_path), 'Pinned-JAR witnesses did not reproduce'
    census = {c['entry']: c['entry_sha256'] for c in read_json(OUT / 'cataclysm-source-census.json')['classes']}
    sources = {r['file']: read_json(OUT / r['file']) for r in note['reference_files']
               if r['file'].startswith('native-evidence/')}
    new_methods = {(w['entry'], m['name'], m['descriptor']): m
                   for w in evidence['witnesses'] for m in w.get('methods', [])}
    assert len(new_methods) == 267
    assert len(GOALS) == 16
    for f, data in sources.items():
        if f == EVIDENCE_FILE.relative_to(OUT).as_posix():
            continue
        for w in data['witnesses']:
            assert not (w['entry'] in RESOURCES.values()), 'Previously captured resource duplicated'
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
        for m in w.get('methods', []):
            if 'instruction_offset_ranges' in m:
                assert m['instruction_offset_ranges'] == FRAGMENTS[w['entry'][len(PKG):-6]][m['name']]
    for e in selected(review):
        for p in e['implementation']:
            w = next(w for w in sources[p['evidence_file']]['witnesses'] if w['id'] == p['witness_id'])
            assert p['entry'] == w['entry']
            assert set(p['methods']) <= {m['name'] for m in w.get('methods', [])}
    checks = evidence['scoped_private_helper_checks']
    assert checks == note['scoped_private_helper_checks']
    assert {(c['entry'], c['method']) for c in checks} == {
        (PKG + L + '.class', 'chargeDamage'),
        (PKG + L + '.class', 'chargeblockbreaking'),
        (PKG + L + '$LeviathanAbyssBlastPortalAttackGoal.class', 'spawnUpperPortal'),
        (PKG + FAMILY + 'The_Leviathan_Tongue_Entity.class', 'shouldDropItem')}
    assert all(c['access'] == 2 and not c['callers_within_owned_family'] for c in checks)
    assert note['tooling']['new_native_witnesses'] == 29
    assert note['tooling']['new_method_witnesses'] == 267
    assert not note['tooling']['reused_evidence_regenerated']
    assert not note['tooling']['recursive_jar_scan']
    root_witness = next(w for w in evidence['witnesses'] if w['entry'] == PKG + L + '.class')
    assert not {'die', 'deathtimer'} & set(root_witness['declared_method_names'])
    assert not {'hurt', 'isInvulnerableTo', 'DamageCap', 'DpsCap', 'RangeLimit',
        'NatureRegen', 'biteattack', 'TailWhips', 'canBeAffected',
        'chargeDamage', 'chargeblockbreaking'} & {
            m['name'] for m in root_witness['methods']}
    for name in ['Abyss_Blast_Entity', 'Portal_Abyss_Blast_Entity']:
        w = next(w for w in evidence['witnesses'] if w['entry'] == PKG + FAMILY + name + '.class')
        assert 'tick' not in {m['name'] for m in w['methods']}
        assert w['superclass'] == 'net/minecraft/world/entity/Entity'
    validate_native_boundaries(evidence)
    validate_reused_boundaries(sources)
    return len(new_methods)


def validate_native_boundaries(evidence):
    def body(name, method):
        entry = PKG + (name if '/' in name else FAMILY + name) + '.class'
        witness = next(w for w in evidence['witnesses'] if w['entry'] == entry)
        return next(m['instructions'] for m in witness['methods'] if m['name'] == method)

    def calls(instructions, name):
        return [i['offset'] for i in instructions if name in str(i.get('operand', ''))]

    def opcode(instructions, offset):
        return next(i['opcode'] for i in instructions if i['offset'] == offset)

    hold = body(L, 'TentacleHoldattack')
    assert calls(hold, '.hurt(') == [252]
    assert calls(hold, '.disableShield(') == [291]
    assert calls(hold, '.startRiding(') == [339] and opcode(hold,342) == '0x57'
    assert calls(hold, '.sendAnimationMessage(') == [350]
    assert not calls(hold, 'Math.min(')
    tentacle = body(L, 'Tentacleattack')
    assert calls(tentacle, '.hurt(') == [289] and calls(tentacle, '.disableShield(') == [323]
    assert calls(tentacle, '.push(') == [397] and calls(tentacle, 'Math.min(')
    assert not calls(tentacle, '.knockback(')
    for name in ['tick', 'aiStep']:
        ins = body(L, name)
        assert not calls(ins, '.chargeDamage(') and not calls(ins, '.chargeblockbreaking(')
    rush = body(L+'$LeviathanRushAttackGoal', 'tick')
    assert calls(rush, '.setDeltaMovement(') and not calls(rush, '.hurt(')
    assert not calls(rush, '.chargeDamage(')
    for name in ['LeviathanTailWhipsAttackGoal', 'LeviathanTentacleHoldAttackGoal', 'LeviathanMineAttackGoal']:
        assert calls(body(L+'$'+name,'tick'), '.setModeChance(')
    orb = body('Abyss_Orb_Entity', 'onHitEntity')
    assert calls(orb, '.hurt(') == [80,100]
    assert calls(orb, '.addEffect(') == [138] and calls(orb, '.explode(') == [164]
    assert not calls(orb, '.isAlliedTo(')
    assert calls(body('Abyss_Orb_Entity','tick'), '.onProjectileImpact(')
    assert any(i['operand'] == 'tracking' for i in body('Abyss_Orb_Entity','addAdditionalSaveData'))
    assert any(i['operand'] == 'fired' for i in body('Abyss_Orb_Entity','readAdditionalSaveData'))
    mine = body('Abyss_Mine_Entity','explode')
    assert calls(mine,'.explode(') == [60,117] and calls(mine,'.addEffect(') == [79,136]
    assert calls(mine,'.remove(') == [87,144] and not calls(mine,'.hurt(')
    rift = body('Dimensional_Rift_Entity','damage')
    assert calls(rift,'.hurt(') == [55,84]
    assert opcode(rift,58) == opcode(rift,87) == '0x57'
    assert not calls(rift,'CMConfig') and not calls(rift,'isClientSide')
    assert len([i for i in rift if i['operand'] == 10.0]) == 2
    portal = body('Abyss_Blast_Portal_Entity','tick')
    assert calls(portal,'.casterL') == [154] and opcode(portal,157) == '0xc6'
    assert calls(portal,'.getCaster(') == [178]
    tongue = body('The_Leviathan_Tongue_Entity','hurtEntity')
    assert calls(tongue,'.hurt(') == [11] and calls(tongue,'isClientSide') == [21]
    assert calls(tongue,'.startRiding(') == [29] and opcode(tongue,32) == '0x57'
    assert not calls(tongue,'.isAlliedTo(')
    load = body('The_Leviathan_Tongue_Entity','readAdditionalSaveData')
    assert calls(load,'.setDuration(') == [29,40] and not calls(load,'.setMaxDuration(')
    assert not calls(body('The_Leviathan_Tongue_Entity','tick'),'.discard(')
    assert calls(body('The_Leviathan_Tongue_Entity','tick'), '.getTarget(')[0] == 10
    assert not calls(body('Abyss_Portal_Entity','addAdditionalSaveData'),'.getEntrance(')
    for beam in ['Abyss_Blast_Entity', 'Portal_Abyss_Blast_Entity']:
        save = body(beam,'addAdditionalSaveData')
        assert not calls(save,'.getCasterID(')
        assert bool(calls(save,'.getDamage(')) == (beam == 'Abyss_Blast_Entity')
    assert calls(body(L,'blockbreak'),'.onEntityDestroyBlock(') == [145]
    for name, method in [(L,'blockbreak2'), ('Dimensional_Rift_Entity','berserkBlockBreaking'),
                         ('The_Leviathan_Tongue_Entity','blockbreak')]:
        assert not calls(body(name,method),'.onEntityDestroyBlock(')
    after = body(L,'AfterDefeatBoss')
    assert calls(after,'.setLeviathanDefeatedOnce(') == [30]
    assert calls(after,'Level.OVERWORLD') and not calls(after,'.addFreshEntity(')
    registry = next(w for w in evidence['witnesses'] if w['entry'] == PKG+REG+'.class')
    for index, entry in [(39,'Dimensional_Rift_Entity'), (42,'Abyss_Blast_Portal_Entity'),
        (43,'Abyss_Portal_Entity'), (49,'The_Leviathan_Tongue_Entity'), (53,'Abyss_Orb_Entity'),
        (59,'Portal_Abyss_Blast_Entity'), (61,'Abyss_Blast_Entity'), (102,'Abyss_Mine_Entity')]:
        bootstrap = next(b for b in registry['registration_bootstraps'] if b['index'] == index)
        assert PKG+FAMILY+entry+'.<init>' in bootstrap['arguments'][1]


def validate_reused_boundaries(sources):
    """Assert concrete caller distinctions using locked bodies, without recapture."""
    def body(file, name, method):
        witness = next(w for w in sources['native-evidence/' + file]['witnesses']
            if w['entry'] == PKG + name + '.class')
        return next(m['instructions'] for m in witness['methods'] if m['name'] == method)

    bite = body('cataclysm-stun.json', L, 'biteattack')
    assert any('Leviathan.TentacleHpDamage' in str(i['operand']) for i in bite)
    assert not any('Leviathan.BiteHpDamage' in str(i['operand']) for i in bite)
    for name, offset in [('Abyss_Blast_Entity', 581), ('Portal_Abyss_Blast_Entity', 554)]:
        ins = body('cataclysm-abyssal.json', FAMILY + name, 'tick')
        assert next(i['operand'] for i in ins if i['offset'] == offset) == .01
        assert any('Math.min(' in str(i['operand']) for i in ins)
        assert any('.removeEffectNoUpdate(' in str(i['operand']) for i in ins)
        assert not any('Level.explode(' in str(i['operand']) for i in ins)
    tail = body('cataclysm-remaining-status.json', L, 'TailWhips')
    assert any('.launch(' in str(i['operand']) for i in tail)
    assert any('ModEffect.EFFECTBONE_FRACTURE' in str(i['operand']) for i in tail)


def validate(jar_path=None):
    review, note, ledger = [read_json(p) for p in [REVIEW, NOTE, LEDGER]]
    summary = validate_records(review, note, ledger)
    validate_preservation(review, note, ledger)
    methods = validate_evidence(review, note, jar_path)
    for path in [REVIEW, NOTE, LEDGER, SPEC_FILE, EVIDENCE_FILE]:
        assert path.read_text(encoding='utf-8') == json.dumps(read_json(path),ensure_ascii=False,indent=2)+'\n'
    return dict(status='PASS', **summary, new_method_witnesses=methods,
        protected_leviathan_admission_shared_status_prior_bosses='BYTE_IDENTICAL',
        pinned_jar_reproduction='PASS' if jar_path else 'NOT_REQUESTED')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jar', type=Path, help='Exact pinned Cataclysm JAR; reproduce missing witnesses only')
    print(json.dumps(validate(parser.parse_args().jar), indent=2))
