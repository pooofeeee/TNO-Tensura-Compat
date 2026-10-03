"""Focused read-only R2k5b record, return-boundary and pinned-JAR validation."""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import subprocess

from catalog_common import OUT, ROOT, read_json
from collect_cataclysm_ignis_offense import (
    A, EVIDENCE_FILE, F, FRAGMENTS, I, PKG, RESOURCES, S, SPEC_FILE, X,
    collect, specification,
)

START = 'd3f6f7b555cac77db3efb5b51abbb82c9f202425'
CHECKPOINT = 'R2k5b-cataclysm-ignis-offense-complete'
NOTE = OUT / 'cataclysm-r2k5b-ignis-offense.json'
REVIEW = OUT / 'mod-reviews/cataclysm.json'
LEDGER = OUT / 'mod-completion-ledger.json'
KINDS = {'VANILLA_DIRECT', 'VANILLA_EQUIVALENT', 'VANILLA_LIKE_EXTENDED',
         'VANILLA_COMPOSITE', 'CUSTOM_DAMAGE', 'CUSTOM_STATUS',
         'CUSTOM_CONTROL', 'CUSTOM_RESOURCE', 'BINARY_MECHANIC'}
KEYS = {'abyss_fireball_contact', 'abyss_fireball_motion', 'alliance',
        'area_melee', 'attack_selection', 'body_check', 'defeat_lifecycle',
        'fireball_contact', 'fireball_motion', 'fireball_volley',
        'flame_strike_chain', 'flame_strike_payload', 'goal_motion',
        'ground_wave', 'held_victim', 'native_explosion', 'phase_wave',
        'poke_capture', 'reinforced_contact', 'shield_break_burst',
        'terrain_control', 'ultimate_lane'}


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
    assert {e['id'] for e in new} == {'cataclysm:ignis_' + k for k in KEYS}
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
    new_paths = [p for p in paths if p['id'].startswith('cataclysm:ignis-offense:')]
    assert len(new_paths) == 22
    for p in new_paths:
        assert p['mod_key'] == 'cataclysm' and p['status'] == 'VERIFIED'
        assert p['primary_source'] and p['native_path'] and p['setup'] and p['implementation']
        assert p['labels'] and p['runtime_status'] == 'NOT_RUN'
        assert p['effect_ids'] and set(p['effect_ids']) <= eids
        for e in new:
            assert (p['id'] in e['delivery_paths']) == (e['id'] in p['effect_ids'])
    rows = {e['id']: e for e in new}
    payloads = note['payload_entities']
    assert {p['entry'] for p in payloads} == {PKG + n + '.class' for n in [F, A, S,
        'entity/effect/Cm_Falling_Block_Entity']}
    assert len(payloads) == 4
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
        unresolved_subsection_ambiguities=0, new_owned_payload_classes=3, reused_non_damage_debris_classes=1)
    assert summary == note['summary'] and summary['candidate_numeric_parameters'] == 344
    assert review['status'] == ledger['status'] == note['status'] == 'PARTIAL'
    for field in ['semantic_discovery_complete', 'special_damage_discovery_complete',
                  'source_mapping_complete', 'delivery_mapping_complete']:
        assert review[field] is False
    cat = next(t for t in ledger['targets'] if t['mod_key'] == 'cataclysm')
    assert cat['state'] == 'PARTIAL' and cat['semantic_effect_count'] == len(effects)
    assert review['checkpoint'] == ledger['checkpoint'] == note['checkpoint'] == CHECKPOINT
    assert review['exact_next_task'] == note['exact_next_task'] == cat['exact_next_task']
    assert note['exact_next_task'].startswith('R2k6a: The Harbinger incoming admission and power/phase/encounter prerequisites.')
    assert note['ignis_family_closed'] is True and not note['remaining_ignis_work']
    assert not note['remaining_subsection_native_ambiguities'] and note['remaining_cataclysm_research']
    assert note['whole_mod_complete'] is False and note['runtime_tests'] == 0
    assert all(note[k] is False for k in ['stage_eligibility_decided', 'phase6_reopened',
        'production_changed', 'stage_changed', 'boss_testing_started', 'l2_testing_started',
        'compatibility_fixes_started', 'phase7_started'])
    validate_contracts(rows)
    return summary


def validate_contracts(rows):
    def row(k):
        return rows['cataclysm:ignis_' + k]

    # Contract differences tied to original call sites, not Stage decisions.
    assert row('attack_selection')['horizontal_cooldown_reader'] is False
    assert row('attack_selection')['reinforced_choice_phase_based'] is False
    assert row('area_melee')['has_ally_check'] is False
    assert len(row('area_melee')['attack_profiles']) == 30
    assert len(row('ground_wave')['attack_profiles']) == 115
    assert row('area_melee')['heal_requires_effect_add_success'] is False
    assert row('held_victim')['heal_requires_effect_add_success'] is False
    assert row('poke_capture')['animation_requires_mount_success'] is False
    assert row('poke_capture')['damage_reads_capture_tag'] is False
    assert row('held_victim')['release_returns_early'] is False
    assert row('held_victim')['damage_tick46_after_release'] is True
    assert row('held_victim')['has_controlling_passenger'] is False
    assert row('phase_wave')['has_heal_call'] is False
    assert row('phase_wave')['damage_ticks'] == {'PHASE_2': [30, 32, 34, 36, 38], 'PHASE_3': [60, 62, 64, 66]}
    assert row('shield_break_burst')['status_requires_hurt_true'] is False
    assert row('body_check')['movement_is_native_knockback'] is False
    assert row('goal_motion')['movement_is_native_knockback'] is False
    for k in ['ground_wave', 'terrain_control', 'ultimate_lane']:
        assert row(k)['debris_adds_damage'] is False
    assert row('ground_wave')['wave_has_hitset'] is False
    assert row('ground_wave')['terrain_result_gates_damage'] is False
    assert row('terrain_control')['reads_ignore_mobgriefing'] is False
    assert row('ultimate_lane')['sample_calls_per_attack'] == 612
    assert row('fireball_volley')['soul_flag_source'] == 'BOSS_PHASE_AT_SPAWN'
    assert row('fireball_volley')['blade_helper_calls_shoot'] is False
    for k in ['fireball_contact', 'abyss_fireball_contact']:
        r = row(k)
        assert r['direct_has_ally_check'] is False
        assert r['heal_requires_alive_after_hurt'] is False
        assert r['enchantment_requires_alive_after_hurt'] is True
        assert r['explosion_requires_hurt_true'] is False
        assert r['brand_requires_explosion_hurt_true'] is False
        assert r['brand_absent_amplifier'] == 1 and r['brand_increment'] == 2
    assert row('abyss_fireball_motion')['reflection_reads'] == 'CAUSING_ENTITY'
    assert row('abyss_fireball_motion')['reflection_resets_bounces'] is False
    assert row('abyss_fireball_motion')['allows_six_bounce_increments'] is True
    assert row('abyss_fireball_motion')['block_projectile_callbacks_per_eligible_hit'] == 2
    assert row('abyss_fireball_motion')['age_limit_requires_block_collision'] is True
    assert row('flame_strike_payload')['mutual_ally_checks'] is True
    assert row('flame_strike_payload')['damage_has_local_server_guard'] is False
    assert row('flame_strike_payload')['terminal_source'] == 'RAW_CACHED_OWNER'
    assert row('flame_strike_payload')['terminal_calls_getOwner'] is False
    assert row('flame_strike_payload')['terminal_fire'] is False
    assert row('flame_strike_payload')['soul_terminal_explosion'] is False
    assert row('flame_strike_chain')['chain_soul'] is False
    assert row('flame_strike_chain')['startup_soul'] is True
    assert row('native_explosion')['damage_return_controls_motion'] is False
    assert row('native_explosion')['calculator_should_damage_controls_motion'] is False
    assert row('native_explosion')['keep_prevents_fire'] is False
    assert row('native_explosion')['has_level_explode_call'] is False
    assert row('defeat_lifecycle')['respawner_created'] is False
    assert row('defeat_lifecycle')['altar_defeat_flag_gate'] is False


def validate_preservation(review, note, ledger):
    assert note['starting_sha'] == START
    old = json.loads(at_start(REVIEW))
    assert [e for e in review['effects'] if e['review_checkpoint'] != CHECKPOINT] == old['effects']
    assert [p for p in review['paths'] if not p['id'].startswith('cataclysm:ignis-offense:')] == old['paths']
    mutable = {'effects', 'paths', 'checkpoint', 'scope', 'notes_file', 'exact_next_task', 'protected_checkpoints'}
    assert {k: v for k, v in review.items() if k not in mutable} == {k: v for k, v in old.items() if k not in mutable}
    assert review['protected_checkpoints'][:-1] == old['protected_checkpoints']
    assert review['protected_checkpoints'][-1]['checkpoint'] == old['checkpoint']
    for reference in note['reference_files']:
        path = OUT / reference['file']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == reference['sha256'], reference['file']
        if reference['usage'] == 'LOCKED_REUSED':
            assert path.read_bytes() == at_start(path), reference['file']
    locked = note['protected_r2k5a']
    assert locked['file'] == 'cataclysm-r2k5a-ignis-admission.json'
    assert (OUT / locked['file']).read_bytes() == at_start(OUT / locked['file'])
    previous = json.loads(at_start(LEDGER))
    assert [t for t in ledger['targets'] if t['mod_key'] != 'cataclysm'] == [
        t for t in previous['targets'] if t['mod_key'] != 'cataclysm']
    assert {k: v for k, v in ledger.items() if k not in ['targets', 'checkpoint']} == {
        k: v for k, v in previous.items() if k not in ['targets', 'checkpoint']}


def validate_evidence(review, note, jar_path=None):
    assert read_json(SPEC_FILE) == specification()
    evidence = read_json(EVIDENCE_FILE)
    assert len(evidence['witnesses']) == 28
    if jar_path is not None:
        assert evidence == collect(jar_path), 'Pinned-JAR witnesses did not reproduce'
    census = {c['entry']: c['entry_sha256'] for c in read_json(OUT / 'cataclysm-source-census.json')['classes']}
    sources = {r['file']: read_json(OUT / r['file']) for r in note['reference_files']
               if r['file'].startswith('native-evidence/')}
    new_methods = {(w['entry'], m['name'], m['descriptor']): m
                   for w in evidence['witnesses'] for m in w.get('methods', [])}
    assert len(new_methods) == 162
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
    validate_native_returns(evidence, sources['native-evidence/cataclysm-remaining-status.json'])
    return len(new_methods)


def validate_native_returns(evidence, reused):
    def body(name, method, data=evidence):
        w = next(w for w in data['witnesses'] if w['entry'] == PKG + name + '.class')
        return next(m['instructions'] for m in w['methods'] if m['name'] == method)

    def calls(ins, name):
        return [i['offset'] for i in ins if name in str(i.get('operand', ''))]

    def op(ins, offset):
        return next(i['opcode'] for i in ins if i['offset'] == offset)

    poke = body(I, 'Poke')
    assert calls(poke, '.hurt(') == [245] and calls(poke, '.isAlive(') == [306]
    assert calls(poke, '.startRiding(') == [342] and op(poke, 345) == '0x57'
    area = body(I, 'AreaAttack', reused)
    assert not calls(area, '.isAlliedTo(')
    assert calls(area, '.addEffect(') == [420] and op(area, 423) == '0x57'
    assert calls(area, '.heal(') == [439] and not calls(area, '.isAlive(')
    rider = body(I, 'positionRider', reused)
    assert calls(rider, '.stopRiding(') == [35] and calls(rider, '.hurt(') == [204]
    assert calls(rider, '.addEffect(') == [290] and op(rider, 293) == '0x57'
    assert calls(rider, '.heal(') == [307]
    phase = body(I, 'Phase_Transition', reused)
    assert not calls(phase, '.heal(')
    for entity, explosion_offset, discard_offset, effect_offset in [(F, 279, 303, 400), (A, 263, 276, 373)]:
        ins = body(entity, 'onHitEntity', reused)
        assert calls(ins, '.explode(') == [explosion_offset]
        assert calls(ins, '.discard(') == [discard_offset]
        assert calls(ins, '.addEffect(') == [effect_offset]
        assert len(calls(ins, '.hurt(')) == 3  # native alternative branches, not three hits
        assert len(calls(ins, '.heal(')) == 2  # owner Ignis/non-Ignis alternatives
        assert not calls(ins, '.isAlliedTo(')
    bounce = body(A, 'onHitBlock')
    assert calls(bounce, '.onHitBlock(') == [2] and calls(bounce, '.onProjectileHit(') == [58]
    reflection = body(A, 'hurt')
    assert calls(reflection, '.setOwner(') == [93] and not calls(reflection, '.hurt(')
    blast = body(X, 'explode')
    assert calls(blast, '.hurt(') == [798] and op(blast, 801) == '0x57'
    assert calls(blast, '.setDeltaMovement(') == [927]
    assert not calls(blast, '.isAlliedTo(')
    strike = body(S, 'damage', reused)
    assert calls(strike, '.isAlliedTo(') == [153, 161]
    assert not calls(strike, '.heal(') and not calls(strike, '.igniteForSeconds(')
    life = body(S, 'tick')
    assert calls(life, '.explode(') == [418] and not calls(life, '.getOwner(')
    assert calls(life, '.damage(') == [550]


def validate(jar_path=None):
    review, note, ledger = [read_json(p) for p in [REVIEW, NOTE, LEDGER]]
    summary = validate_records(review, note, ledger)
    validate_preservation(review, note, ledger)
    methods = validate_evidence(review, note, jar_path)
    return dict(status='PASS', **summary, new_method_witnesses=methods,
        protected_ignis_admission_shared_status_guardian_monstrosity='BYTE_IDENTICAL',
        prior_records_and_paths='UNCHANGED',
        pinned_jar='REPRODUCED' if jar_path is not None else 'ARCHIVED_WITNESSES_VALIDATED')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jar', type=Path, help='Optional exact pinned Cataclysm 3.27 JAR')
    print(json.dumps(validate(parser.parse_args().jar), indent=2))
