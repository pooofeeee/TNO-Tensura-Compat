"""Focused read-only R2k8b records, protected contracts and pinned-JAR checks."""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import struct
import subprocess

from catalog_common import OUT, ROOT, read_json
from collect_cataclysm_maledictus_offense import (
    A, EVIDENCE_FILE, FRAGMENTS, GOALS, H, M, METHODS, PKG, REG,
    RESOURCES, SPEC_FILE, collect, specification,
)

START = 'c154e03927ac03180a8d82269c133e7bf1e44c3b'
CHECKPOINT = 'R2k8b-cataclysm-maledictus-offense-complete'
NOTE = OUT / 'cataclysm-r2k8b-maledictus-offense.json'
REVIEW = OUT / 'mod-reviews/cataclysm.json'
LEDGER = OUT / 'mod-completion-ledger.json'
KINDS = {'VANILLA_DIRECT', 'VANILLA_EQUIVALENT', 'VANILLA_LIKE_EXTENDED',
         'VANILLA_COMPOSITE', 'CUSTOM_DAMAGE', 'CUSTOM_STATUS',
         'CUSTOM_CONTROL', 'CUSTOM_RESOURCE', 'BINARY_MECHANIC'}
KEYS = {'attack_selection', 'rage_offense', 'mace_leap', 'area_contact',
    'spin_chain', 'combo_chain', 'combo_contact', 'rush_chain', 'rush_contact',
    'uppercut_chain', 'uppercut_contact', 'custom_sweep', 'flying_smash_chain',
    'flying_smash_contact', 'shockwave_sweep', 'shockwave_debris', 'soul_release',
    'grab_contact', 'grab_control', 'held_victim_control', 'held_soul_slam',
    'halberd_ground_delivery', 'halberd_ring_chain', 'halberd_windmill_chain',
    'halberd_radagon_chain', 'halberd_contact', 'halberd_lifecycle',
    'ground_bow_volley', 'flying_bow_volley', 'flying_bow_control',
    'arrow_contact', 'arrow_homing', 'arrow_lifecycle', 'terrain_control',
    'alliance', 'defeat_lifecycle'}


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
    new_paths = [p for p in paths if p['id'].startswith('cataclysm:maledictus-offense:')]
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
    assert {p['entry'] for p in payloads} == {PKG + n + '.class' for n in [
        A, H, 'entity/effect/Cm_Falling_Block_Entity']}
    assert len(payloads) == 3
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
        unresolved_subsection_ambiguities=0, new_owned_payload_classes=2, reused_non_damage_debris_classes=1)
    assert summary == note['summary'] and summary['candidate_numeric_parameters'] == 136
    assert review['status'] == ledger['status'] == note['status'] == 'PARTIAL'
    for f in ['semantic_discovery_complete', 'special_damage_discovery_complete',
              'source_mapping_complete', 'delivery_mapping_complete']:
        assert review[f] is False
    cat = next(t for t in ledger['targets'] if t['mod_key'] == 'cataclysm')
    assert cat['state'] == 'PARTIAL' and cat['semantic_effect_count'] == len(effects)
    assert review['checkpoint'] == ledger['checkpoint'] == note['checkpoint'] == CHECKPOINT
    assert review['exact_next_task'] == note['exact_next_task'] == cat['exact_next_task']
    assert note['exact_next_task'].startswith('R2k9a: The Leviathan incoming admission and phase/encounter prerequisites.')
    assert note['maledictus_family_closed'] is True and not note['remaining_maledictus_work']
    assert not note['remaining_subsection_native_ambiguities'] and note['remaining_cataclysm_research']
    assert note['whole_mod_complete'] is False and note['runtime_tests'] == 0
    assert all(note[k] is False for k in ['stage_eligibility_decided', 'phase6_reopened',
        'production_changed', 'stage_changed', 'boss_testing_started', 'l2_testing_started',
        'compatibility_fixes_started', 'phase7_started'])
    validate_contracts(rows)
    return summary


def validate_contracts(rows):
    def row(k):
        return rows['cataclysm:maledictus_' + k]

    def params(k, primitive):
        return next(c['numerical_parameters'] for c in row(k)['components'] if c['primitive'] == primitive)

    f32 = lambda x: struct.unpack('f', struct.pack('f', x))[0]
    assert row('attack_selection')['selection_is_goal_scheduled'] is True
    assert row('attack_selection')['directly_used_offensive_goal_classes'] == 19
    assert row('attack_selection')['cooldown_tick_has_local_server_guard'] is False
    assert row('rage_offense')['direct_rage_is_live'] is True
    assert row('rage_offense')['raw_setter_clamps_rage'] is False
    assert row('rage_offense')['gain_guard_is_global_clamp'] is False
    assert row('rage_offense')['reset_precedes_soul_damage'] is True
    assert params('rage_offense', 'NATIVE_DAMAGE_REQUEST')['rage_coefficient'] == f32(.2)
    for k in ['ground_bow_volley', 'flying_bow_volley']:
        assert params(k, 'DAMAGE_CARRIER') == dict(config_damage=5.0, rage_coefficient=f32(.05))
        assert row(k)['damage_snapshot_at_launch'] is True
        assert row(k)['sets_native_projectile_owner'] is True
        assert row(k)['local_spawn_server_guard'] is False
    assert params('halberd_ground_delivery', 'DAMAGE_CARRIER') == dict(config_damage=11.0, rage_coefficient=f32(.1))
    assert row('halberd_ground_delivery')['damage_snapshot_at_spawn'] is True
    assert row('halberd_ground_delivery')['local_spawn_server_guard'] is False
    assert row('halberd_ground_delivery')['sets_native_projectile_owner'] is False
    for k, expected in [('area_contact', False), ('combo_contact', True), ('rush_contact', True),
                        ('uppercut_contact', False), ('custom_sweep', False), ('flying_smash_contact', True)]:
        assert row(k)['local_damage_server_guard'] is expected
        assert row(k)['hp_addition_capped'] is True
    for k in ['area_contact', 'combo_contact', 'rush_contact', 'uppercut_contact']:
        assert row(k)['shield_requires_hurt_true'] is False
    for k in ['mace_leap', 'area_contact', 'spin_chain', 'combo_chain', 'rush_chain',
              'uppercut_contact', 'flying_smash_chain', 'flying_bow_control']:
        assert row(k)['movement_is_native_knockback'] is False
    assert row('area_contact')['push_requires_hurt_true'] is True
    assert row('combo_contact')['combo_requires_hurt_true'] is True
    assert row('combo_chain')['combo_branch_calls_parent_stop'] is False
    assert row('rush_contact')['has_same_class_exclusion'] is False
    assert row('rush_contact')['adds_victim_movement'] is False
    assert row('rush_chain')['continuation_validates_alternative_state'] is False
    assert row('rush_chain')['charge_state_profiles'][-1]['count'] == 3
    assert row('uppercut_chain')['goal_tick_calls_parent'] is False
    assert row('flying_bow_control')['has_extra_line_of_sight_gate'] is False
    assert row('uppercut_contact')['lift_requires_hurt_true'] is True
    assert row('flying_smash_chain')['strike_ticks'] == {'8': 56, '24': 51}
    assert row('flying_smash_chain')['landing_min_ticks'] == {'8': 65, '24': 60}
    assert row('flying_smash_contact')['contact_ticks'] == {'9': [4], '25': [4, 37]}
    for k in ['shockwave_sweep', 'soul_release', 'grab_contact', 'held_soul_slam']:
        assert row(k)['adds_rage'] is False
    assert row('shockwave_sweep')['base_damage_captured_before_samples'] is True
    assert row('shockwave_sweep')['global_victim_deduplication'] is False
    assert row('shockwave_sweep')['lift_requires_hurt_true'] is True
    assert row('shockwave_sweep')['wave_profiles'] == [dict(tick=8+2*i, distance=2+i) for i in range(5)]
    for f in ['debris_adds_damage', 'debris_destroys_terrain', 'debris_places_terrain']:
        assert row('shockwave_debris')[f] is False
    assert row('soul_release')['reset_precedes_damage'] is True
    assert row('soul_release')['hurt_return_consumed'] is False
    assert row('held_soul_slam')['hurt_return_consumed'] is False
    assert row('held_soul_slam')['requires_held_passenger'] is False
    assert row('grab_contact')['grab_flag_requires_hurt_true'] is True
    assert row('grab_contact')['grab_flag_requires_mount_success'] is False
    for f in ['mount_return_checked', 'camera_request_requires_mount_success', 'grab_transition_requires_passenger', 'success_dropspeed_read']:
        assert row('grab_control')[f] is False
    assert row('grab_control')['unused_success_dropspeed'] == 2.0
    assert not any('dropspeed' in p for c in row('grab_control')['scalable_parameter_candidates'] for p in c['parameters'])
    assert row('held_victim_control')['state33_y_equals_boss_y'] is True
    assert row('held_victim_control')['release_tick'] == 23
    for f in ['shift_suppression_has_local_server_guard', 'release_has_local_server_guard', 'adds_damage']:
        assert row('held_victim_control')[f] is False
    assert row('halberd_ring_chain')['radius_argument_is_physical_radius'] is False
    assert row('halberd_windmill_chain')['attempted_entity_count'] == 100
    assert row('halberd_radagon_chain')['has_single_sample_denominator_fallback'] is False
    for k in ['halberd_ring_chain', 'halberd_windmill_chain', 'halberd_radagon_chain']:
        assert row(k)['spawn_requires_hurt_true'] is False
    for f in ['has_bilateral_allied_check', 'caster_absence_magic_fallback', 'cadence_uses_entity_tick_count']:
        assert row('halberd_contact')[f] is True
    assert row('halberd_contact')['contact_period_ticks'] == 5
    assert row('halberd_contact')['hurt_return_consumed'] is False
    assert row('halberd_contact')['damage_uses_live_caster_rage'] is False
    assert row('halberd_lifecycle')['owner_uuid_saved'] is True
    assert row('halberd_lifecycle')['warmup_saved'] is True
    for f in ['damage_saved', 'state_saved', 'lifetime_saved', 'contact_requires_visual_state', 'damage_requires_caster_alive']:
        assert row('halberd_lifecycle')[f] is False
    assert row('halberd_lifecycle')['default_damage_after_reload'] == 0.0
    for f in ['parent_on_hit_entity_called', 'damage_uses_native_velocity_multiplier', 'burn_requires_hurt_true',
              'burn_rolled_back_on_false', 'successful_hit_discards_locally', 'false_slow_discard_requires_pickup_allowed', 'local_payload_allied_check']:
        assert row('arrow_contact')[f] is False
    assert row('arrow_contact')['enderman_true_returns_early'] is True
    assert row('arrow_homing')['native_parent_tick_retained'] is True
    for f in ['homing_precedes_native_parent_tick', 'alive_spectator_predicate_is_conjunction', 'failed_target_lookup_retries', 'homing_normalizes_final_speed']:
        assert row('arrow_homing')[f] is False
    assert row('arrow_lifecycle')['nbt_calls_parent'] is True
    assert row('arrow_lifecycle')['despawn_is_universal_flight_timer'] is False
    assert row('arrow_lifecycle')['stop_seeking_saved'] is False
    assert row('arrow_lifecycle')['owner_storage'] == 'NATIVE_PROJECTILE'
    assert row('terrain_control')['ground_has_no_ai_gate'] is True
    assert row('terrain_control')['flying_has_no_ai_gate'] is False
    assert row('terrain_control')['chandelier_pass_checks_immune_tag'] is False
    assert row('terrain_control')['terrain_result_gates_damage'] is False
    assert row('alliance')['tag_fallback_requires_both_team_null'] is True
    assert row('defeat_lifecycle')['death_state_write_checks_parent_admission'] is False
    assert row('defeat_lifecycle')['death_removal_duration'] == 60
    assert row('defeat_lifecycle')['placement_uses_current_level'] is True
    assert row('defeat_lifecycle')['home_dimension_lookup_is_placement_level'] is False
    assert row('defeat_lifecycle')['has_death_damage_payload'] is False


def validate_preservation(review, note, ledger):
    assert note['starting_sha'] == START
    old = json.loads(at_start(REVIEW))
    assert [e for e in review['effects'] if e['review_checkpoint'] != CHECKPOINT] == old['effects']
    assert [p for p in review['paths'] if not p['id'].startswith('cataclysm:maledictus-offense:')] == old['paths']
    mutable = {'effects', 'paths', 'checkpoint', 'scope', 'notes_file', 'exact_next_task', 'protected_checkpoints'}
    assert {k: v for k, v in review.items() if k not in mutable} == {k: v for k, v in old.items() if k not in mutable}
    assert review['protected_checkpoints'][:-1] == old['protected_checkpoints']
    assert review['protected_checkpoints'][-1] == dict(checkpoint=old['checkpoint'], notes_file=old['notes_file'])
    for r in note['reference_files']:
        path = OUT / r['file']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == r['sha256'], r['file']
        if r['usage'] == 'LOCKED_REUSED':
            assert path.read_bytes() == at_start(path), r['file']
    locked = note['protected_r2k8a']
    assert locked['file'] == 'cataclysm-r2k8a-maledictus-admission.json'
    assert (OUT / locked['file']).read_bytes() == at_start(OUT / locked['file'])
    previous = json.loads(at_start(LEDGER))
    assert [t for t in ledger['targets'] if t['mod_key'] != 'cataclysm'] == [
        t for t in previous['targets'] if t['mod_key'] != 'cataclysm']
    assert {k: v for k, v in ledger.items() if k not in ['targets', 'checkpoint']} == {
        k: v for k, v in previous.items() if k not in ['targets', 'checkpoint']}


def validate_evidence(review, note, jar_path=None):
    assert read_json(SPEC_FILE) == specification()
    evidence = read_json(EVIDENCE_FILE)
    assert len(evidence['witnesses']) == 25
    assert {w['entry'] for w in evidence['witnesses']} == {
        PKG + n + '.class' for n in METHODS} | set(RESOURCES.values())
    if jar_path is not None:
        assert evidence == collect(jar_path), 'Pinned-JAR witnesses did not reproduce'
    census = {c['entry']: c['entry_sha256'] for c in read_json(OUT / 'cataclysm-source-census.json')['classes']}
    sources = {r['file']: read_json(OUT / r['file']) for r in note['reference_files']
               if r['file'].startswith('native-evidence/')}
    new_methods = {(w['entry'], m['name'], m['descriptor']): m
                   for w in evidence['witnesses'] for m in w.get('methods', [])}
    assert len(new_methods) == 144
    assert len(GOALS) == 19
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
    tag = next(e for e in selected(review) if e['id'] == 'cataclysm:maledictus_alliance')['tag_evidence']
    w = next(w for w in sources[tag['evidence_file']]['witnesses'] if w['id'] == tag['witness_id'])
    assert w['entry'] == tag['entry'] and w['data']['values'] == [
        'cataclysm:maledictus', 'cataclysm:draugr', 'cataclysm:royal_draugr', 'cataclysm:elite_draugr', 'cataclysm:aptrgangr']
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

    f32 = lambda x: struct.unpack('f', struct.pack('f', x))[0]
    assert any(i['operand'] == f32(.2) for i in body(M, 'DMG'))
    for name, hurt, shield, rage in [('AreaAttack',306,345,375),('ComboAreaAttack',316,355,390),
                                    ('Rushattack',177,216,246),('uppercut',151,190,220)]:
        ins = body(M, name)
        assert calls(ins, '.hurt(') == [hurt]
        assert calls(ins, '.disableShield(') == [shield]
        assert calls(ins, '.setRageMeter(') == [rage]
        assert hurt < shield < rage
    assert op(body(M, 'AreaAttack'), 350) == '0x99'  # hurt flag tested after independent shield check
    assert not calls(body(M, 'Rushattack'), '.push(')
    assert not calls(body(M, 'Rushattack'), '.setDeltaMovement(')
    assert calls(body(M, 'ComboAreaAttack'), '.comboZ')
    grab = body(M, 'Grab')
    assert calls(grab, '.hurt(') == [177]
    assert calls(grab, '.grabZ') == [226]
    assert calls(grab, 'ModTag.IGNIS_CANT_POKE') == [234]
    assert calls(grab, '.startRiding(') == [291] and op(grab,294) == '0x57'
    assert not calls(grab, '.setRageMeter(')
    success = body(M + '$MaledictusSuccessState', 'tick')
    assert not calls(success, '.dropspeedD')
    assert calls(body(M + '$MaledictusSuccessState', '<init>'), '.dropspeedD')
    for n in ['Maledictus_Bow','Maledictus_Flying_Bow']:
        ins = body(M+'$'+n, 'tick')
        assert any(i['operand'] == f32(.05) for i in ins)
        assert calls(ins, '.setBaseDamage(') and calls(ins, '.shoot(')
        assert not calls(ins, 'isClientSide')
    assert not calls(body(M+'$Maledictus_Flying_Bow', 'canUse'), '.hasLineOfSight(')
    spawn = body(M, 'spawnHalberd')
    assert any(i['operand'] == f32(.1) for i in spawn)
    assert not calls(spawn, '.setOwner(') and not calls(spawn, 'isClientSide')
    shock = body(M, 'ShieldSmashDamage')
    assert calls(shock, '.DMG(') == [136] and calls(shock, '.hurt(') == [527]
    assert op(shock,534) == '0x99' and calls(shock, '.setDeltaMovement(') == [572]
    assert not calls(shock, '.setRageMeter(') and not calls(shock, '.destroyBlock(')
    arrow = body(A, 'onHitEntity')
    assert not calls(arrow, 'AbstractArrow.onHitEntity(')
    assert min(calls(arrow, '.getDeltaMovement(')) > 114  # velocity read belongs to false-result bounce
    assert calls(arrow, '.modifyDamage(') == [65]
    assert calls(arrow, '.stopSeekingZ') == [88]
    assert calls(arrow, '.igniteForSeconds(') == [107] and calls(arrow, '.hurt(') == [114]
    assert op(arrow,117) == '0x99' and op(arrow,125) == '0xb1'
    assert calls(arrow, '.doPostAttackEffectsWithItemSource(') == [156]
    assert calls(arrow, '.doKnockback(') == [177] and calls(arrow, '.doPostHurtEffects(') == [183]
    assert calls(arrow, '.discard(') == [274]  # false branch only; no successful-hit discard
    assert not calls(arrow, '.isAlliedTo(') and not calls(arrow, '.clearFire(')
    assert calls(body(A,'tick'), 'AbstractArrow.tick(') == [1]
    assert calls(body(A,'onHit'), 'AbstractArrow.onHit(') == [2]
    assert not calls(body(A,'addAdditionalSaveData'), '.stopSeekingZ')
    assert any(i['operand'] == 200 for i in body(A,'tickDespawn'))
    halberd = body(H,'damage')
    assert calls(halberd,'.isAlliedTo(') == [58,66]
    assert calls(halberd,'.hurt(') == [49,82]
    assert op(halberd,52) == op(halberd,85) == '0x57'  # both hurt results ignored
    assert calls(halberd,'.tickCountI') == [25] and op(halberd,29) == '0x70'
    for name in ['addAdditionalSaveData','readAdditionalSaveData']:
        assert not calls(body(H,name), '.getDamage(') and not calls(body(H,name), '.setDamage(')
        assert not calls(body(H,name), '.lifeTicksI')
    assert calls(body(H,'tick'), '.damage(') == [323]
    assert calls(body(H,'tick'), '.discard(') == [367]
    ground = body(M,'blockdestroy')
    assert len(calls(ground,'.onEntityDestroyBlock(')) == len(calls(ground,'.destroyBlock(')) == 2
    assert len(calls(ground,'ModTag.MALEDICTUS_IMMUNE')) == 1
    assert len(calls(ground,'ModTag.FROSTED_PRISON_CHANDELIER')) == 1
    assert calls(body(M,'blockbreak'), '.isNoAi(') and not calls(body(M,'flyingdestroy'), '.isNoAi(')
    death = body(M,'die')
    assert calls(death,'.die(') == [2] and calls(death,'.setAttackState(') == [8]
    assert not any(i['opcode'] in ['0x99','0x9a'] for i in death)
    after = body(M,'AfterDefeatBoss')
    assert calls(after,'.getLevel(') == [47]
    assert calls(after,'.setBlockAndUpdate(') == [120,148]
    assert calls(after,'.level(')[-2:] == [101,128]  # current-level receivers for both branches
    registry = next(w for w in evidence['witnesses'] if w['entry'] == PKG+REG+'.class')
    for index, entry in [(82,A),(81,H)]:
        bootstrap = next(b for b in registry['registration_bootstraps'] if b['index'] == index)
        assert PKG+entry+'.<init>' in bootstrap['arguments'][1]
    assert not any('.addEffect(' in str(i['operand']) or '.heal(' in str(i['operand'])
        for w in evidence['witnesses'] for m in w.get('methods',[]) for i in m['instructions'])


def validate(jar_path=None):
    review, note, ledger = [read_json(p) for p in [REVIEW, NOTE, LEDGER]]
    summary = validate_records(review, note, ledger)
    validate_preservation(review, note, ledger)
    methods = validate_evidence(review, note, jar_path)
    for path in [REVIEW, NOTE, LEDGER, SPEC_FILE, EVIDENCE_FILE]:
        assert path.read_text(encoding='utf-8') == json.dumps(read_json(path),ensure_ascii=False,indent=2)+'\n'
    return dict(status='PASS', **summary, new_method_witnesses=methods,
        protected_maledictus_admission_shared_status_prior_bosses='BYTE_IDENTICAL',
        pinned_jar_reproduction='PASS' if jar_path else 'NOT_REQUESTED')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jar', type=Path, help='Exact pinned Cataclysm JAR; reproduce missing witnesses only')
    print(json.dumps(validate(parser.parse_args().jar), indent=2))
