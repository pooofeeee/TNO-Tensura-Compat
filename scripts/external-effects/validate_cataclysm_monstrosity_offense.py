"""Read-only R2k4b validation; no runtime, broad discovery or Stage decisions."""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import subprocess

from catalog_common import OUT, ROOT, read_json
from collect_cataclysm_monstrosity_offense import (
    D, EVIDENCE_FILE, F, FRAGMENTS, J, L, M, PKG, SPEC_FILE, collect, specification,
)

START = 'c7ce02866c9615a695035da147ebe1649bb57200'
CHECKPOINT = 'R2k4b-cataclysm-monstrosity-offense-complete'
NOTE = OUT / 'cataclysm-r2k4b-monstrosity-offense.json'
REVIEW = OUT / 'mod-reviews/cataclysm.json'
LEDGER = OUT / 'mod-completion-ledger.json'
KINDS = {'VANILLA_DIRECT', 'VANILLA_EQUIVALENT', 'VANILLA_LIKE_EXTENDED',
         'VANILLA_COMPOSITE', 'CUSTOM_DAMAGE', 'CUSTOM_STATUS',
         'CUSTOM_CONTROL', 'CUSTOM_RESOURCE', 'BINARY_MECHANIC'}
KEYS = {'alliance', 'attack_sequence', 'berserk_quake', 'flame_jet_payload',
        'flare_impact', 'flare_volley', 'lava_absorption', 'lava_bomb_impact',
        'lava_bomb_lifecycle', 'magma_volley', 'overpower_launch', 'radial_jets',
        'shoulder_check', 'smash', 'stomp_wave', 'terrain_control'}


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
    assert {e['id'] for e in new} == {'cataclysm:monstrosity_' + k for k in KEYS}
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
            assert len(owners) == 1, 'Candidate lost its exact native primitive'
            owner = owners[0]
            assert c['native_value'] == owner['numerical_parameters'][p]
            assert c['native_formula'] == owner['formula']
            assert c['units'] == owner['parameter_units'][p]
            assert c['native_boundary'] == owner['native_boundary']
        if e['primary_classification'] == 'BINARY_MECHANIC':
            assert not candidates
    new_paths = [p for p in paths if p['id'].startswith('cataclysm:monstrosity-offense:')]
    assert len(new_paths) == 20
    for p in new_paths:
        assert p['mod_key'] == 'cataclysm' and p['status'] == 'VERIFIED'
        assert p['primary_source'] and p['native_path'] and p['setup'] and p['implementation']
        assert p['labels'] and p['runtime_status'] == 'NOT_RUN'
        assert p['effect_ids'] and set(p['effect_ids']) <= eids
        for e in new:
            assert (p['id'] in e['delivery_paths']) == (e['id'] in p['effect_ids'])
    payloads = note['payload_entities']
    assert {p['entry'] for p in payloads} == {PKG + n + '.class' for n in [L, F, J, D]}
    assert len(payloads) == 4
    rows = {e['id']: e for e in new}
    for p in payloads:
        assert p['source_mechanic_ids'] and set(p['source_mechanic_ids']) <= rows.keys()
        assert set(p['payload_mechanic_ids']) <= rows.keys()
        assert p['source_actor'] and p['native_lifecycle']
        for source in p['source_mechanic_ids']:
            assert p['entity_id'] in rows[source]['spawned_entity_ids']
        assert bool(p['payload_mechanic_ids']) == (p['role'] != 'NON_DAMAGE_DEBRIS_VERIFIED')
    assert {m['id'] for m in note['mechanic_packages']} == set(rows)
    for m, e in zip(note['mechanic_packages'], new):
        assert m['id'] == e['id'] and m['primary_classification'] == e['primary_classification']
        assert m['delivery_paths'] == e['delivery_paths'] and m['binary_gates'] == e['binary_parameters']
        assert m['hurt_return_dependency'] == e['hurt_return_dependency']
        assert m['numerical_candidates'] == [{k: c[k] for k in ['primitive', 'parameters',
            'native_value', 'units', 'native_boundary']} for c in e['scalable_parameter_candidates']]
    summary = dict(new_mechanics=len(new), delivery_paths=len(new_paths),
        classifications=dict(sorted(Counter(e['primary_classification'] for e in new).items())),
        candidate_numeric_parameters=sum(len(c['parameters']) for e in new for c in e['scalable_parameter_candidates']),
        unresolved_subsection_ambiguities=0, payload_classes_reviewed=len(payloads))
    assert summary == note['summary'] and summary['candidate_numeric_parameters'] == 157
    assert review['status'] == ledger['status'] == note['status'] == 'PARTIAL'
    for field in ['semantic_discovery_complete', 'special_damage_discovery_complete',
                  'source_mapping_complete', 'delivery_mapping_complete']:
        assert review[field] is False
    cat = next(t for t in ledger['targets'] if t['mod_key'] == 'cataclysm')
    assert cat['state'] == 'PARTIAL' and cat['semantic_effect_count'] == len(effects)
    assert review['checkpoint'] == ledger['checkpoint'] == note['checkpoint'] == CHECKPOINT
    assert review['exact_next_task'] == note['exact_next_task'] == cat['exact_next_task']
    assert note['exact_next_task'].startswith('R2k5a: Ignis incoming admission and phase/shield prerequisites.')
    assert note['monstrosity_family_closed'] is True and not note['remaining_monstrosity_work']
    assert not note['remaining_subsection_native_ambiguities'] and note['remaining_cataclysm_research']
    assert note['whole_mod_complete'] is False and note['runtime_tests'] == 0
    assert all(note[k] is False for k in ['stage_eligibility_decided', 'phase6_reopened',
        'production_changed', 'stage_changed', 'boss_testing_started', 'l2_testing_started',
        'compatibility_fixes_started', 'phase7_started'])
    validate_contracts(rows)
    return summary


def validate_contracts(rows):
    def row(key):
        return rows['cataclysm:monstrosity_' + key]

    # These differences affect native cancellation, ownership and lifecycle;
    # none expresses a Stage eligibility or balance decision.
    assert row('lava_absorption')['heal_calls'] == [24, 26, 28]
    assert row('lava_absorption')['heal_requires_lava_removal'] is False
    assert row('lava_absorption')['heal_call_site_server_guard'] is False
    assert row('shoulder_check')['effect_application_source'] is None
    assert row('shoulder_check')['movement_is_absolute_velocity_write'] is False
    assert row('shoulder_check')['active_ticks'] == [20, 48]
    assert row('flare_impact')['burn_requires_alive_after_hurt'] is True
    assert row('flare_impact')['child_spawn_requires_hurt'] is False
    assert row('flare_impact')['direct_has_ally_check'] is False
    assert row('flare_impact')['direct_amount'] == row('flare_impact')['child_amount'] == 7.0
    for k in ['flare_impact', 'flare_volley']:
        assert row(k)['reads_flare_bomb_damage_config'] is False
    jet = row('flame_jet_payload')
    assert jet['damage_warmup_equality'] == -8 and jet['mutual_ally_checks'] is True
    assert jet['burn_requires_alive_after_hurt'] is False
    assert jet['owned_hurt_enchantment_callback'] is False
    assert jet['saved_native_keys'] == ['Warmup', 'Owner', 'damage']
    assert jet['default_synced_damage'] == 0.0 and jet['default_life_ticks'] == 22
    impact = row('lava_bomb_impact')
    assert impact['entity_hit_source_argument'] == 'owner'
    assert impact['block_hit_source_argument'] == 'projectile'
    assert impact['has_direct_hurt_call'] is False and impact['impact_class_gate_is_aoe_team_gate'] is False
    life = row('lava_bomb_lifecycle')
    assert life['position_zero_check'] == 'REFERENCE_INEQUALITY'
    assert life['cleanup_checks_original_block_identity'] is False
    assert row('stomp_wave')['shieldbreakticks'] == 0
    assert row('stomp_wave')['explicit_monstrosity_class_exclusion'] is False
    assert row('terrain_control')['terrain_result_gates_victim_damage'] is False
    for k in ['terrain_control', 'stomp_wave']:
        assert row(k)['debris_adds_damage'] is False
    assert row('terrain_control')['debris_places_blocks'] is False
    assert row('attack_sequence')['explicit_awake_gate'] is False
    assert row('attack_sequence')['explicit_berserk_gate'] is False
    assert row('flare_volley')['explicit_berserk_gate'] is False
    for e in rows.values():
        if 'damage_path' in e:
            assert e['damage_path']['source_mod_custom_damage_type'] is False


def validate_preservation(review, note, ledger):
    assert note['starting_sha'] == START
    old = json.loads(at_start(REVIEW))
    assert [e for e in review['effects'] if e['review_checkpoint'] != CHECKPOINT] == old['effects']
    assert [p for p in review['paths'] if not p['id'].startswith('cataclysm:monstrosity-offense:')] == old['paths']
    mutable = {'effects', 'paths', 'checkpoint', 'scope', 'notes_file', 'exact_next_task', 'protected_checkpoints'}
    assert {k: v for k, v in review.items() if k not in mutable} == {k: v for k, v in old.items() if k not in mutable}
    assert review['protected_checkpoints'][:-1] == old['protected_checkpoints']
    assert review['protected_checkpoints'][-1]['checkpoint'] == old['checkpoint']
    for reference in note['reference_files']:
        path = OUT / reference['file']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == reference['sha256'], reference['file']
        if reference['usage'] == 'LOCKED_REUSED':
            assert path.read_bytes() == at_start(path), reference['file']
    locked = note['protected_r2k4a']
    assert locked['file'] == 'cataclysm-r2k4a-monstrosity-admission.json'
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

    def opcode(ins, offset):
        return next(i['opcode'] for i in ins if i['offset'] == offset)

    quake = body(M, 'EarthQuake')
    assert calls(quake, '.hurt(') == [155]
    assert calls(quake, '.disableShield(') == [188]
    assert calls(quake, '.launch(') == [205] and calls(quake, '.igniteForSeconds(') == [219]
    shoulder = body(M, 'aiStep', reused)
    assert calls(shoulder, '.hurt(') == [840] and calls(shoulder, '.push(') == [969]
    assert calls(shoulder, '.addEffect(') == [986]
    flare = body(F, 'onHitEntity')
    assert calls(flare, '.hurt(') == [112, 159]
    assert opcode(flare, 119) == opcode(flare, 127) == '0x99'
    assert calls(flare, '.isAlive(') == [124]
    assert calls(flare, '.igniteForSeconds(') == [134] and calls(flare, '.doPostAttackEffects(') == [142]
    assert opcode(flare, 162) == '0x57', 'Anonymous hurt return is discarded'
    onhit = body(F, 'onHit')
    assert calls(onhit, 'ThrowableProjectile.onHit(') == [2]
    assert calls(onhit, '.XStrikeRune(') == [53] and calls(onhit, '.PlusStrikeRune(') == [65]
    assert calls(onhit, '.discard(') == [69] and not calls(onhit, '.hurt(')
    jet = body(J, 'damage')
    assert calls(jet, '.isAlliedTo(') == [49, 57]
    assert calls(jet, '.hurt(') == [40, 77] and opcode(jet, 80) == '0x99'
    assert opcode(jet, 43) == '0x57' and calls(jet, '.igniteForSeconds(') == [87]
    assert calls(jet, '.isAlive(') == [6] and not calls(jet, '.doPostAttackEffects(')
    entity_hit, block_hit = body(L, 'onHitEntity'), body(L, 'onHitBlock')
    assert calls(entity_hit, '.getOwner(') == [6] and not calls(block_hit, '.getOwner(')
    assert calls(entity_hit, '.explode(') == [89] and calls(block_hit, '.explode(') == [54]
    assert not calls(entity_hit, '.hurt(') and not calls(block_hit, '.hurt(')
    assert opcode(body(M, 'CircleFlameJet'), 77) == '0x6c', 'Native vertex division is integer division'
    for m in ['<init>', 'tick']:
        ins = body(D, m)
        assert not calls(ins, '.hurt(') and not calls(ins, '.setBlock(')


def validate(jar_path=None):
    review, note, ledger = [read_json(p) for p in [REVIEW, NOTE, LEDGER]]
    summary = validate_records(review, note, ledger)
    validate_preservation(review, note, ledger)
    methods = validate_evidence(review, note, jar_path)
    return dict(status='PASS', **summary, new_method_witnesses=methods,
        protected_admission_guardian_shared_status='BYTE_IDENTICAL',
        prior_records_and_paths='UNCHANGED',
        pinned_jar='REPRODUCED' if jar_path is not None else 'ARCHIVED_WITNESSES_VALIDATED')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jar', type=Path, help='Optional exact pinned Cataclysm 3.27 JAR')
    print(json.dumps(validate(parser.parse_args().jar), indent=2))
