"""Focused R2k10b catalog, protected-contract and pinned-JAR validation."""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import struct
import subprocess

from catalog_common import OUT, ROOT, read_json
from collect_cataclysm_scylla_offense import (
    ANCHOR, AREA, BASE_SPEAR, EVIDENCE_FILE, FRAGMENTS, GOALS,
    LIGHTNING_SPEAR, METHODS, PKG, REGISTRY, RESOURCES, S, SERPENT,
    SPARK, SPEC_FILE, STORM, WATER_SPEAR, WAVE, collect, specification,
)

START = '7a216beedcd1bc00317bdcb1f385df61999cc006'
CHECKPOINT = 'R2k10b-cataclysm-scylla-offense-complete'
NOTE = OUT / 'cataclysm-r2k10b-scylla-offense.json'
REVIEW = OUT / 'mod-reviews/cataclysm.json'
LEDGER = OUT / 'mod-completion-ledger.json'
KINDS = {'VANILLA_DIRECT', 'VANILLA_EQUIVALENT', 'VANILLA_LIKE_EXTENDED',
         'VANILLA_COMPOSITE', 'CUSTOM_DAMAGE', 'CUSTOM_STATUS',
         'CUSTOM_CONTROL', 'CUSTOM_RESOURCE', 'BINARY_MECHANIC'}
KEYS = set('''alliance anchor_contact anchor_delivery anchor_grab_control
anchor_lifecycle anchor_return_motion area_contact attack_selection
body_repulsion cloud_barrage_delivery defeat_lifecycle elemental_spear_lifecycle
elemental_spear_motion flight_movement lightning_area_contact
lightning_area_lifecycle lightning_body_contact lightning_spear_block_payload
lightning_spear_contact lightning_spear_lifecycle melee_delivery sequence_state
serpent_contact serpent_delivery serpent_lifecycle spark_block_payload
spark_delivery spark_lifecycle spark_motion spear_delivery spin_contact storm_contact
storm_delivery storm_lifecycle storm_push terrain_response water_movement
water_spear_bounce water_spear_contact wave_contact wave_delivery wave_lifecycle
wave_motion weather_transition whip_spear_delivery'''.split())


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
        assert e['components'] and e['implementation'] and e['primary_test_source']
        assert e['source_actor'] and e['hurt_return_dependency'] and e['closest_vanilla_equivalent']
        assert e['delivery_paths'] and set(e['delivery_paths']) <= pids
        assert not {'stage_scaling_needed', 'stage_policy', 'stage_multiplier', 'runtime_hook',
                    'stage_eligibility', 'stage_cap', 'stage_floor'} & e.keys()
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
        if e['primary_classification'] == 'BINARY_MECHANIC':
            assert not candidates
    new_paths = [p for p in paths if p['id'].startswith('cataclysm:scylla-offense:')]
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
    assert len(payloads) == 8
    assert {p['entry'] for p in payloads} == {PKG + n + '.class' for n in [
        ANCHOR, AREA, STORM, WAVE, WATER_SPEAR, LIGHTNING_SPEAR, SPARK, SERPENT]}
    for p in payloads:
        assert p['source_mechanic_ids'] and set(p['source_mechanic_ids']) <= rows.keys()
        assert p['payload_mechanic_ids'] and set(p['payload_mechanic_ids']) <= rows.keys()
        assert p['source_actor'] and p['native_lifecycle']
        for producer in p['source_mechanic_ids']:
            assert p['entity_id'] in rows[producer]['spawned_entity_ids']
    assert note['offense_paths_closed'] == [p['id'] for p in new_paths]
    assert note['mechanic_packages'] == [dict(id=e['id'],
        primary_classification=e['primary_classification'], delivery_paths=e['delivery_paths'],
        numerical_candidates=[{k: c[k] for k in ['primitive', 'parameters', 'native_value',
            'units', 'native_boundary']} for c in e['scalable_parameter_candidates']],
        binary_gates=e['binary_parameters'], hurt_return_dependency=e['hurt_return_dependency']) for e in new]
    summary = dict(new_mechanics=len(new), delivery_paths=len(new_paths),
        classifications=dict(sorted(Counter(e['primary_classification'] for e in new).items())),
        candidate_numeric_parameters=sum(len(c['parameters']) for e in new for c in e['scalable_parameter_candidates']),
        owned_payload_entities=8, unresolved_subsection_ambiguities=0)
    assert summary == note['summary'] and summary['candidate_numeric_parameters'] == 120
    assert summary['classifications'] == dict(BINARY_MECHANIC=14, CUSTOM_CONTROL=10,
        CUSTOM_DAMAGE=9, VANILLA_COMPOSITE=7, VANILLA_LIKE_EXTENDED=5)
    assert review['status'] == ledger['status'] == note['status'] == 'PARTIAL'
    for f in ['semantic_discovery_complete', 'special_damage_discovery_complete',
              'source_mapping_complete', 'delivery_mapping_complete']:
        assert review[f] is False
    cat = next(t for t in ledger['targets'] if t['mod_key'] == 'cataclysm')
    assert cat['state'] == 'PARTIAL' and cat['semantic_effect_count'] == len(effects)
    assert review['checkpoint'] == ledger['checkpoint'] == note['checkpoint'] == CHECKPOINT
    assert review['exact_next_task'] == note['exact_next_task'] == cat['exact_next_task']
    assert note['exact_next_task'].startswith('R2k11a: Ender Golem incoming admission and combat-state/encounter prerequisites.')
    assert note['scylla_family_closed'] is True and not note['remaining_scylla_work']
    assert not note['remaining_subsection_native_ambiguities'] and note['remaining_cataclysm_research']
    assert note['whole_mod_complete'] is False and note['runtime_tests'] == 0
    assert all(note[k] is False for k in ['stage_eligibility_decided', 'phase6_reopened',
        'production_changed', 'stage_changed', 'boss_testing_started', 'l2_testing_started',
        'compatibility_fixes_started', 'phase7_started'])
    validate_contracts(rows)
    return summary


def validate_contracts(rows):
    def row(key):
        return rows['cataclysm:scylla_' + key]

    def params(key, primitive):
        return next(c['numerical_parameters'] for c in row(key)['components'] if c['primitive'] == primitive)

    f32 = lambda x: struct.unpack('f', struct.pack('f', x))[0]
    facts = {
        'attack_selection': dict(independent_random_draws=True, backstep_state_or_bypasses_selection=True,
            whip_spear_registered_max=8.0, whip_spear_local_min=15.0, selection_gates_are_stage_scalars=False),
        'sequence_state': dict(cooldowns_have_local_side_ai_guard=False, flight_initial_cooldown=160, raw_state_is_tno_stage=False),
        'alliance': dict(alliance_inherited_globally_by_payloads=False),
        'area_contact': dict(movement_requires_hurt_true=True, shield_disable_requires_hurt_true=False,
            movement_is_native_knockback=False, wrapped_angle_branches_have_local_range_check=False),
        'spin_contact': dict(movement_requires_hurt_true=True, shield_disable_requires_hurt_true=False,
            sample_deduplication=False, zero_airborne_removes_native_rng=False),
        'storm_push': dict(storm_push_has_local_ally_filter=False, movement_is_native_knockback=False),
        'body_repulsion': dict(adds_second_repulsion=False, local_server_guard=False, local_ally_filter=False),
        'lightning_body_contact': dict(uses_native_explosion=False, hp_contribution_has_min_cap=True, contact_hurt_return_consumed=False),
        'storm_contact': dict(hp_contribution_has_min_cap=False, uses_native_lightning_bolt_entity=False),
        'storm_delivery': dict(wake_ring_divisor_is_integer=True, landing_ring_divisor_is_integer=False,
            prediction_has_local_server_guard=False),
        'storm_lifecycle': dict(saved_damage=True, saved_caster_uuid=True),
        'water_movement': dict(local_server_guard=False, local_ai_guard=False, motion_is_native_knockback=False),
        'flight_movement': dict(motion_is_native_knockback=False, fall_movement_overwrites_velocity=True),
        'wave_contact': dict(wetness_requires_hurt_true=True, movement_requires_hurt_true=False, raw_contact_owner_field=True),
        'wave_lifecycle': dict(saved_damage=False, saved_yaw=False, saved_state=False,
            returns_after_native_remove=False, contact_uses_owner_resolver=False),
        'wave_delivery': dict(wave_entity_is_projectile_subclass=False),
        'elemental_spear_motion': dict(impact_event_preserved=True, initial_speed_is_acceleration=False, entity_hit_auto_discards=False),
        'elemental_spear_lifecycle': dict(saved_private_lifetick=False, concrete_tick_calls_check_despawn=False, returns_after_expiry=False),
        'water_spear_contact': dict(wetness_requires_hurt_true=True, entity_hit_auto_discards=False),
        'water_spear_bounce': dict(reflection_preserves_full_incoming_speed=False, motion_written_before_zero_bounce_discard=True),
        'lightning_spear_contact': dict(victim_to_owner_alliance_checked=False, applies_wetness=False, entity_hit_auto_discards=False),
        'lightning_spear_block_payload': dict(storm_damage_config_field='LightningAreaDamage', creates_two_distinct_payloads=True,
            radius_on_use_consumed=False, native_bounds_are_proposed_stage_bounds=False),
        'lightning_spear_lifecycle': dict(hp_damage_save_reads='getAreaRadius', hp_damage_load_writes='setHpDamage', native_snapshot_repaired=False),
        'lightning_area_contact': dict(has_vanilla_victim_cache=False, has_circular_distance_filter=False,
            uses_native_area_effect_cloud=False, has_hp_contribution=False, radius_on_use_consumed=False, duration_on_use_consumed=False),
        'lightning_area_lifecycle': dict(saved_owner_uuid=False, saved_damage=False, native_snapshot_repaired=False),
        'cloud_barrage_delivery': dict(lightning_damage_config_field='SnakeDamage', water_damage_config_field='SpearDamage', delivery_has_local_server_guard=False),
        'spear_delivery': dict(delivery_has_local_server_guard=False),
        'spark_block_payload': dict(spark_has_custom_entity_hit_damage=False, area_requires_ground_support=False, creates_two_distinct_payloads=True),
        'spark_lifecycle': dict(area_damage_load_key='HpDamage', area_damage_saved_key='AreaDamage', native_snapshot_repaired=False, custom_entity_hit_damage=False),
        'anchor_contact': dict(movement_requires_hurt_true=True, movement_is_native_knockback=False,
            damage_causing_actor_is_controller=True, local_ally_filter=False, local_server_guard=False),
        'anchor_grab_control': dict(ride_requires_hurt_true=True, grab_latch_requires_hurt_true=False,
            ride_result_controls_packet=False, boss_is_victim_carrier=False),
        'anchor_return_motion': dict(hook_uses_normal_return_motion=False, returns_after_controller_collision_discard=False),
        'anchor_lifecycle': dict(saved_controller_uuid=True, saved_rotations=False,
            death_explicitly_discards_anchor=False, hook_adds_normal_owner_alive_guard=False),
        'serpent_contact': dict(wetness_requires_hurt_true=True, null_caster_applies_wetness=False, has_hp_contribution=False),
        'serpent_delivery': dict(serpent_is_projectile_subclass=False, delivery_has_local_server_guard=False),
        'serpent_lifecycle': dict(saved_right=False, saved_state=False, saved_life_ticks=False, translates_as_homing_projectile=False),
        'whip_spear_delivery': dict(private_whip_helper_used=False),
        'weather_transition': dict(weather_is_damage=False, weather_is_stage_scalar=False),
        'terrain_response': dict(ignore_mobgriefing_config_read=False, creates_damaging_debris=False),
        'defeat_lifecycle': dict(adds_duplicate_death_payload=False, death_has_storm_payload=True),
    }
    for key, fields in facts.items():
        for name, value in fields.items():
            assert row(key)[name] == value, (key, name)
    assert params('area_contact', 'NATIVE_DAMAGE_REQUEST') == dict(coefficient=1.0, hp_coefficient=f32(.05))
    assert params('spin_contact', 'NATIVE_DAMAGE_REQUEST')['hp_coefficient'] == f32(.07)
    assert params('spin_contact', 'FORCED_MOVEMENT')['airborne'] == 0.0
    assert params('storm_contact', 'NATIVE_DAMAGE_REQUEST') == dict(damage=10.0, hp_coefficient=f32(.04))
    assert params('water_spear_contact', 'NATIVE_DAMAGE_REQUEST') == dict(damage=14.0, fallback=5.0)
    assert params('serpent_contact', 'NATIVE_DAMAGE_REQUEST') == dict(damage=16.0)
    assert params('serpent_contact', 'WETNESS_DELIVERY') == dict(duration=150)
    assert params('wave_contact', 'WETNESS_DELIVERY') == dict(duration=200)
    assert params('lightning_area_contact', 'AREA_SELECTION') == dict(radius=2.0, height=.5, cadence=5)
    assert params('anchor_contact', 'NATIVE_DAMAGE_REQUEST') == dict(damage=16.0)
    assert params('elemental_spear_motion', 'PAYLOAD_MOTION')['acceleration'] == .1
    assert not any('bounce_speed' in c['parameters'] for c in row('water_spear_bounce')['scalable_parameter_candidates'])
    assert row('water_spear_bounce')['bounce_speed_binding']
    assert row('melee_delivery')['attack_schedule'] == row('area_contact')['native_call_variants']
    assert len(row('area_contact')['native_call_variants']) == 12
    assert len(row('attack_selection')['selection_table']) == 14
    whip = next(g for g in row('attack_selection')['selection_table'] if g['goal'] == 'WhipAndSpearGoal')
    assert whip['range'] == '>=15 and parent<8'


def validate_preservation(review, note, ledger):
    assert note['starting_sha'] == START
    old = json.loads(at_start(REVIEW))
    assert len(old['effects']) == 251 and len(old['paths']) == 257
    assert [e for e in review['effects'] if e['review_checkpoint'] != CHECKPOINT] == old['effects']
    assert [p for p in review['paths'] if not p['id'].startswith('cataclysm:scylla-offense:')] == old['paths']
    mutable = {'effects', 'paths', 'checkpoint', 'scope', 'notes_file', 'exact_next_task', 'protected_checkpoints'}
    assert {k: v for k, v in review.items() if k not in mutable} == {k: v for k, v in old.items() if k not in mutable}
    assert review['protected_checkpoints'][:-1] == old['protected_checkpoints']
    assert review['protected_checkpoints'][-1] == dict(checkpoint=old['checkpoint'], notes_file=old['notes_file'])
    for r in note['reference_files']:
        path = OUT / r['file']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == r['sha256'], r['file']
        if r['usage'] == 'LOCKED_REUSED':
            assert path.read_bytes() == at_start(path), r['file']
    locked = note['protected_r2k10a']
    assert locked['file'] == 'cataclysm-r2k10a-scylla-admission.json'
    assert (OUT / locked['file']).read_bytes() == at_start(OUT / locked['file'])
    assert hashlib.sha256((OUT / locked['file']).read_bytes()).hexdigest() == locked['sha256']
    previous = json.loads(at_start(LEDGER))
    assert [t for t in ledger['targets'] if t['mod_key'] != 'cataclysm'] == [
        t for t in previous['targets'] if t['mod_key'] != 'cataclysm']
    assert {k: v for k, v in ledger.items() if k not in ['targets', 'checkpoint']} == {
        k: v for k, v in previous.items() if k not in ['targets', 'checkpoint']}


def validate_evidence(review, note, jar_path=None):
    assert read_json(SPEC_FILE) == specification()
    evidence = read_json(EVIDENCE_FILE)
    assert len(evidence['witnesses']) == 27
    assert {w['entry'] for w in evidence['witnesses']} == {
        PKG + n + '.class' for n in METHODS} | set(RESOURCES.values())
    if jar_path is not None:
        reproduced = collect(jar_path)
        assert evidence == reproduced, 'Pinned-JAR witnesses did not reproduce'
        assert EVIDENCE_FILE.read_bytes() == (
            json.dumps(reproduced, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    census = {c['entry']: c['entry_sha256'] for c in read_json(OUT / 'cataclysm-source-census.json')['classes']}
    sources = {r['file']: read_json(OUT / r['file']) for r in note['reference_files']
               if r['file'].startswith('native-evidence/')}
    new_methods = {(w['entry'], m['name'], m['descriptor']): m
                   for w in evidence['witnesses'] for m in w.get('methods', [])}
    assert len(new_methods) == 279 and len(GOALS) == 15
    for f, data in sources.items():
        if f == EVIDENCE_FILE.relative_to(OUT).as_posix():
            continue
        for w in data['witnesses']:
            assert w['entry'] not in RESOURCES.values(), 'Previously captured resource duplicated'
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
            name = w['entry'][len(PKG):-6]
            assert {m['name'] for m in w['methods']} == set(METHODS[name]) | set(FRAGMENTS.get(name, {}))
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
    assert {c['method'] for c in checks} == {'Whip', 'LightningAttack', 'StrikeWindmillLightning', 'WhipLightningAttack'}
    for c in checks:
        assert c['access'] == 2 and c['entry'] == PKG + S + '.class'
        if c['method'] == 'StrikeWindmillLightning':
            assert c['callers_within_owned_family'] == [PKG + S + '.class:LightningAttack(DDIF)V']
        else:
            assert not c['callers_within_owned_family']
    assert note['tooling']['new_native_witnesses'] == 27
    assert note['tooling']['new_method_witnesses'] == 279
    assert not note['tooling']['reused_evidence_regenerated'] and not note['tooling']['recursive_jar_scan']
    root = next(w for w in evidence['witnesses'] if w['entry'] == PKG + S + '.class')
    assert not {'hurt', 'isInvulnerableTo', 'DamageCap', 'DpsCap', 'RangeLimit', 'NatureRegen',
        'canBeAffected', 'readAdditionalSaveData', 'addAdditionalSaveData', 'Whip',
        'LightningAttack', 'StrikeWindmillLightning', 'WhipLightningAttack'} & {m['name'] for m in root['methods']}
    for name, method in [(WAVE, 'attackEntities'), (WATER_SPEAR, 'onHitEntity'), (SERPENT, 'damage')]:
        w = next(w for w in evidence['witnesses'] if w['entry'] == PKG + name + '.class')
        assert method not in {m['name'] for m in w['methods']}
    validate_native_boundaries(evidence)
    return len(new_methods)


def validate_native_boundaries(evidence):
    """Native gate/source/impact/NBT assertions, independent of catalog prose."""
    def witness(name):
        return next(w for w in evidence['witnesses'] if w['entry'] == PKG + name + '.class')

    def body(name, method):
        return next(m['instructions'] for m in witness(name)['methods'] if m['name'] == method)

    def calls(ins, name):
        return [i['offset'] for i in ins if name in str(i.get('operand', ''))]

    def op(ins, offset):
        return next(i['opcode'] for i in ins if i['offset'] == offset)

    def literals(ins):
        return {i['operand'] for i in ins if isinstance(i.get('operand'), str)}

    area = body(S, 'AreaAttack')
    assert calls(area, '.hurt(') == [316] and calls(area, '.disableShield(') == [355]
    assert calls(area, '.push(') == [434] and calls(area, 'Math.min(')
    assert not calls(area, '.knockback(')
    spin = body(S, 'SpinDamage')
    assert calls(spin, '.hurt(') == [264] and calls(spin, '.disableShield(') == [303]
    assert calls(spin, '.setDeltaMovement(') and not calls(spin, '.knockback(')
    push = body(S, 'Stormknockback')
    assert calls(push, '.push(') == [127]
    assert not calls(push, '.hurt(') and not calls(push, '.isAlliedTo(')
    ai = body(S, 'aiStep')
    assert len(calls(ai, '.hurt(')) == 3 and not calls(ai, '.explode(')
    assert len(calls(ai, '.setWeatherParameters(')) == 3
    anchor = body(ANCHOR, 'onHitEntity')
    assert calls(anchor, 'causeStormBringerDamage') == [20]
    assert calls(anchor, '.hurt(') == [33] and calls(anchor, '.startRiding(') == [138]
    assert op(anchor, 141) == '0x57', 'Native ride result must remain unused'
    assert not calls(anchor, '.isAlliedTo(') and calls(anchor, 'isClientSide') == [130]
    hit = body(ANCHOR, 'onHit')
    assert calls(hit, '.setGrab(') == [53] and not calls(hit, '.hurt(')
    spear_tick = body(BASE_SPEAR, 'tick')
    assert calls(spear_tick, '.onProjectileImpact(') == [81]
    assert calls(spear_tick, '.hitTargetOrDeflectSelf(')
    assert calls(body(BASE_SPEAR, 'onHit'), 'ProjectileDeflection.AIM_DEFLECT')
    assert calls(body(WATER_SPEAR, 'onHitBlock'), '.discard(') == [222]
    assert calls(body(WATER_SPEAR, 'onHitBlock'), '.assignDirectionalMovement(')
    assert calls(body(WATER_SPEAR, 'onHitBlock'), '.assignDirectionalMovement(')[0] < 222
    spear_save = body(LIGHTNING_SPEAR, 'addAdditionalSaveData')
    assert calls(spear_save, '.getAreaRadius(') == [32, 43] and not calls(spear_save, '.getHpDamage(')
    assert calls(body(LIGHTNING_SPEAR, 'readAdditionalSaveData'), '.setHpDamage(') == [47]
    spark_load = body(SPARK, 'readAdditionalSaveData')
    assert 'AreaDamage' not in literals(spark_load)
    assert sum(i['operand'] == 'HpDamage' for i in spark_load) == 2
    assert calls(spark_load, '.setAreaDamage(') == [32]
    assert not calls(body(SPARK, 'onHitEntity'), '.hurt(')
    assert not calls(body(SPARK, 'tick'), '.hurt(')
    assert len(calls(body(LIGHTNING_SPEAR, 'onHitBlock'), '.addFreshEntity(')) == 2
    assert calls(body(SPARK, 'onHitBlock'), '.spawnArea(') and calls(body(SPARK, 'onHitBlock'), '.addFreshEntity(')
    for name in [AREA, STORM, WAVE, SERPENT]:
        assert witness(name)['superclass'] == 'net/minecraft/world/entity/Entity'
    area_save = body(AREA, 'addAdditionalSaveData')
    assert 'Owner' not in literals(area_save) and not calls(area_save, '.getDamage(')
    assert 'Owner' in literals(body(AREA, 'readAdditionalSaveData'))
    assert not calls(body(AREA, 'damage'), '.addEffect(')
    assert not calls(body(STORM, 'damage'), 'Math.min(')
    assert calls(body(STORM, 'damage'), 'causeLightningDamage')
    assert not calls(body(WAVE, 'tick'), '.getOwner(')
    assert {'Owner', 'Lifespan', 'Maxticks'} == {s for s in literals(body(WAVE, 'addAdditionalSaveData'))
        if '.' not in s and '/' not in s}
    serpent_save = literals(body(SERPENT, 'addAdditionalSaveData'))
    assert not {'Right', 'State', 'LifeTicks'} & serpent_save
    terrain = body(S, 'blockbreak')
    assert calls(terrain, '.canEntityGrief(') and calls(terrain, '.onEntityDestroyBlock(') == [190]
    assert not calls(terrain, 'IgnoreMobGriefing')
    after = body(S, 'AfterDefeatBoss')
    assert calls(after, 'BOSS_RESPAWNER') and calls(after, '.setEntityId(') == [132] and calls(after, 'ModEntities.SCYLLA')
    registry = witness(REGISTRY)
    assert len(registry['registration_bootstraps']) == 16
    assert {b['arguments'][1].split('.<init>')[0] for b in registry['registration_bootstraps']
            if '.<init>' in b['arguments'][1]} == {
        PKG + n for n in [ANCHOR, STORM, AREA, WAVE, WATER_SPEAR, LIGHTNING_SPEAR, SPARK, SERPENT]}


def validate(jar_path=None):
    review, note, ledger = [read_json(p) for p in [REVIEW, NOTE, LEDGER]]
    summary = validate_records(review, note, ledger)
    validate_preservation(review, note, ledger)
    methods = validate_evidence(review, note, jar_path)
    for path in [REVIEW, NOTE, LEDGER, SPEC_FILE, EVIDENCE_FILE]:
        assert path.read_text(encoding='utf-8') == json.dumps(read_json(path), ensure_ascii=False, indent=2) + '\n'
    return dict(status='PASS', **summary, new_method_witnesses=methods,
        protected_scylla_admission_shared_status_prior_bosses='BYTE_IDENTICAL',
        pinned_jar_reproduction='PASS' if jar_path else 'NOT_REQUESTED')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jar', type=Path, help='Reproduce only the new witnesses against the exact pinned JAR')
    print(json.dumps(validate(parser.parse_args().jar), indent=2))
