"""Read-only, bounded R2k3b validation; no runtime, broad census or reassembly."""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import subprocess

from catalog_common import OUT, ROOT, read_json
from collect_cataclysm_guardian_offense import (
    B, EVIDENCE_FILE, G, PKG, R, SPEC_FILE, V, collect, specification,
)

START = '22b6844b0d854b005e32dc2f1b32f4435855e54a'
CHECKPOINT = 'R2k3b-cataclysm-guardian-offense-complete'
NOTE = OUT / 'cataclysm-r2k3b-guardian-offense.json'
REVIEW = OUT / 'mod-reviews/cataclysm.json'
LEDGER = OUT / 'mod-completion-ledger.json'
KINDS = {'VANILLA_DIRECT', 'VANILLA_EQUIVALENT', 'VANILLA_LIKE_EXTENDED',
         'VANILLA_COMPOSITE', 'CUSTOM_DAMAGE', 'CUSTOM_STATUS',
         'CUSTOM_CONTROL', 'CUSTOM_RESOURCE', 'BINARY_MECHANIC'}
KEYS = {
    'guardian_attack_selection', 'guardian_punches', 'guardian_gravity_punch',
    'guardian_burst', 'guardian_uppercut', 'guardian_rage_finisher',
    'guardian_hug_impact', 'guardian_swings', 'guardian_rocket_punch',
    'guardian_mass_destruction', 'guardian_airstrike_landing',
    'guardian_bullet_family', 'guardian_void_runes', 'guardian_void_vortex',
    'guardian_mass_terrain', 'guardian_body_repulsion', 'guardian_alliance',
    'guardian_defeat_respawner',
}


def at_start(path):
    relative = Path(path).relative_to(ROOT).as_posix()
    return subprocess.check_output(['git', 'show', START + ':' + relative], cwd=ROOT)


def validate_records(review, note, ledger):
    effects, paths = review['effects'], review['paths']
    assert len(effects) == 18
    assert len({e['id'] for e in effects}) == 18
    assert {e['id'] for e in effects} == {'cataclysm:' + k for k in KEYS}
    assert len(paths) == len({p['id'] for p in paths}) == 20
    assert effects == sorted(effects, key=lambda e: e['id'])
    assert paths == sorted(paths, key=lambda p: p['id'])
    path_ids, effect_ids = {p['id'] for p in paths}, {e['id'] for e in effects}
    candidate_count = 0
    for e in effects:
        assert e['mod_key'] == 'cataclysm'
        assert e['primary_classification'] in KINDS
        assert e['inspection_status'] == 'STATIC_REVIEWED'
        assert e['review_checkpoint'] == CHECKPOINT
        assert e['implementation'] and e['components']
        assert e['primary_test_source'] and e['delivery_paths']
        assert set(e['delivery_paths']) <= path_ids
        assert not e['unresolved_ambiguities']
        candidates = e['scalable_parameter_candidates']
        assert candidates == sorted(candidates, key=lambda c: (c['primitive'], c['parameters']))
        seen = set()
        for c in candidates:
            assert len(c['parameters']) == 1
            parameter = c['parameters'][0]
            key = (c['primitive'], parameter)
            assert key not in seen
            seen.add(key)
            owners = [comp for comp in e['components'] if comp['primitive'] == c['primitive']
                      and parameter in comp['numerical_parameters']]
            assert len(owners) == 1, (e['id'], key)
            native = owners[0]
            assert c['native_value'] == native['numerical_parameters'][parameter]
            assert isinstance(c['native_value'], (int, float)) and not isinstance(c['native_value'], bool)
            assert math.isfinite(c['native_value'])
            assert c['native_formula'] == native['formula']
            assert c['units'] == native['parameter_units'][parameter] and c['units']
            candidate_count += 1
        if e['primary_classification'] == 'BINARY_MECHANIC':
            assert not candidates, e['id']
    for p in paths:
        assert p['mod_key'] == 'cataclysm' and p['status'] == 'VERIFIED'
        assert p['primary_source'] and p['native_path'] and p['setup'] and p['implementation']
        assert p['labels'] and p['runtime_status'] == 'NOT_RUN'
        assert p['effect_ids'] and set(p['effect_ids']) <= effect_ids
        for e in effects:
            assert (p['id'] in e['delivery_paths']) == (e['id'] in p['effect_ids'])
    assert review['status'] == 'PARTIAL'
    for field in ['semantic_discovery_complete', 'special_damage_discovery_complete',
                  'source_mapping_complete', 'delivery_mapping_complete']:
        assert review[field] is False
    cat = next(t for t in ledger['targets'] if t['mod_key'] == 'cataclysm')
    assert cat['state'] == 'PARTIAL' and cat['semantic_effect_count'] == 18
    assert review['checkpoint'] == note['checkpoint'] == ledger['checkpoint'] == CHECKPOINT
    assert review['exact_next_task'] == note['exact_next_task'] == cat['exact_next_task']
    assert review['protected_checkpoint'] == 'R2k3a-cataclysm-guardian-admission-complete'
    assert review['protected_notes_file'] == 'cataclysm-r2k3a-guardian-admission.json'
    assert note['whole_mod_complete'] is False and note['runtime_tests'] == 0
    assert note['stage_eligibility_decided'] is False
    assert all(note[k] is False for k in ['phase6_reopened', 'production_changed', 'stage_changed',
        'boss_testing_started', 'l2_testing_started', 'compatibility_fixes_started', 'phase7_started'])
    assert not note['remaining_subsection_native_ambiguities']
    assert note['remaining_cataclysm_research']
    assert {m['id'] for m in note['mechanic_packages']} == effect_ids
    for m, e in zip(note['mechanic_packages'], effects):
        assert m['id'] == e['id'] and m['primary_classification'] == e['primary_classification']
        assert m['delivery_paths'] == e['delivery_paths']
        assert m['numerical_candidates'] == [
            {k: c[k] for k in ['primitive', 'parameters', 'native_value', 'units']}
            for c in e['scalable_parameter_candidates']]
    summary = dict(new_mechanics=18, delivery_paths=20,
        classifications=dict(sorted(Counter(e['primary_classification'] for e in effects).items())),
        candidate_numeric_parameters=candidate_count, unresolved_subsection_ambiguities=0)
    assert note['summary'] == summary
    return summary


def validate_preservation(note):
    protected = OUT / note['protected_r2k3a']['file']
    assert note['starting_sha'] == START
    assert protected.read_bytes() == at_start(protected)
    assert hashlib.sha256(protected.read_bytes()).hexdigest() == note['protected_r2k3a']['sha256']
    prior = read_json(protected)
    assert prior['checkpoint'] == 'R2k3a-cataclysm-guardian-admission-complete'
    assert len(prior['mechanic_packages']) == 4 and len(prior['delivery_paths']) == 17
    for reference in prior['reference_files']:
        path = OUT / reference['file']
        data = path.read_bytes()
        assert data == at_start(path), reference['file']
        # R2k3a recorded Windows working-file hashes before Git normalized LF.
        # Exact equality to the protected Git blob is required independently;
        # reconstruct only CRLF to verify the historical published hash.
        historical = data.replace(b'\r\n', b'\n').replace(b'\n', b'\r\n')
        assert reference['sha256'] in {
            hashlib.sha256(data).hexdigest(), hashlib.sha256(historical).hexdigest()}
    for reference in note['reference_files']:
        path = OUT / reference['file']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == reference['sha256']
        if reference['file'] not in ['native-evidence/cataclysm-guardian-offense.json',
                                     'native-specifications/cataclysm-guardian-offense.json']:
            assert path.read_bytes() == at_start(path), reference['file']
    previous = json.loads(at_start(LEDGER))
    current = read_json(LEDGER)
    assert [t for t in current['targets'] if t['mod_key'] != 'cataclysm'] == [
        t for t in previous['targets'] if t['mod_key'] != 'cataclysm']
    assert {k: v for k, v in current.items() if k not in ['targets', 'checkpoint']} == {
        k: v for k, v in previous.items() if k not in ['targets', 'checkpoint']}


def validate_evidence(review, note, jar_path=None):
    assert read_json(SPEC_FILE) == specification()
    evidence = read_json(EVIDENCE_FILE)
    assert len(evidence['witnesses']) == 14
    if jar_path is not None:
        assert evidence == collect(jar_path)
    census = {c['entry']: c['entry_sha256'] for c in read_json(OUT / 'cataclysm-source-census.json')['classes']}
    sources = {'native-evidence/cataclysm-guardian-offense.json': evidence}
    for f in ['native-evidence/cataclysm-guardian-admission.json',
              'native-evidence/cataclysm-stun.json', 'native-evidence/cataclysm-shared.json',
              'native-evidence/cataclysm-foundation.json']:
        sources[f] = read_json(OUT / f)
    new_methods = {(w['entry'], m['name'], m['descriptor']) for w in evidence['witnesses'] for m in w.get('methods', [])}
    reused_methods = {(w['entry'], m['name'], m['descriptor']) for f, d in sources.items()
                      if f != 'native-evidence/cataclysm-guardian-offense.json'
                      for w in d['witnesses'] for m in w.get('methods', [])}
    assert not new_methods & reused_methods, 'Previously captured native evidence was duplicated'
    for w in evidence['witnesses']:
        assert w['jar_sha256'] == note['tooling']['jar_sha256']
        if w['entry'].endswith('.class'):
            assert w['entry_sha256'] == census[w['entry']]
    for record in review['effects'] + review['paths']:
        for p in record['implementation']:
            w = next(w for w in sources[p['evidence_file']]['witnesses'] if w['id'] == p['witness_id'])
            assert p['entry'] == w['entry']
            assert set(p['methods']) <= {m['name'] for m in w.get('methods', [])}
    return len(new_methods)


def validate_native_distinctions(review):
    sources = ['native-evidence/cataclysm-guardian-offense.json', 'native-evidence/cataclysm-guardian-admission.json', 'native-evidence/cataclysm-stun.json']
    witnesses = [w for f in sources for w in read_json(OUT / f)['witnesses']]
    def body(name, method):
        return next(m['instructions'] for w in witnesses if w['entry'] == PKG + name + '.class'
                    for m in w.get('methods', []) if m['name'] == method)
    def hits(ins, operand):
        return [i for i in ins if operand in str(i.get('operand', ''))]
    def at(ins, operand):
        return hits(ins, operand)[0]['offset']
    area = body(G, 'AreaAttack')
    assert [at(area, x) for x in ['.hurt(', 'disableShield(', '.setDeltaMovement(', '.addEffect(', '.launch(']] == [299, 338, 363, 390, 402]
    assert not hits(area, '.isAlliedTo(')
    mass = body(G, 'MassDestruction')
    hurt_index = next(i for i, x in enumerate(mass) if '.hurt(' in str(x.get('operand', '')))
    assert mass[hurt_index + 1]['opcode'] == '0x57'
    assert at(mass, '.isAlliedTo(') < at(mass, '.hurt(') < at(mass, '.launch(')
    tick = body(G, 'tick')
    assert len(hits(tick, 'MobEffects.LEVITATION')) == len(hits(tick, 'ModEffect.EFFECTSTUN')) == 1
    assert all(i['offset'] >= 954 for i in hits(tick, '.uppercut_cooldown') if i['opcode'] == '0xb4')
    bullet = body(B, 'onHitEntity')
    assert at(bullet, '.hurt(') < at(bullet, 'doPostAttackEffects') < at(bullet, 'MobEffects.LEVITATION') < at(bullet, '.addEffect(')
    assert not hits(body(B, 'tick'), 'AbstractHurtingProjectile.tick(')
    rune = body(R, 'damage')
    assert len(hits(rune, '.isAlliedTo(')) == 2
    assert hits(rune, '.magic(') and hits(rune, '.indirectMagic(')
    assert not hits(rune, 'doPostAttackEffects')
    vortex = body(V, 'tick')
    assert hits(vortex, '.ownerL') and not hits(vortex, '.getOwner(')
    assert at(vortex, '.setDeltaMovement(') < at(vortex, 'ExplosionInteraction.NONE') < at(vortex, 'Level.explode(')
    spawn = body('blockentities/Boss_Respawn_Spawner_Block_Entity', 'spawnMyBoss')
    assert hits(spawn, '.finalizeSpawn(') and hits(spawn, '.setHomePos(')
    assert not hits(spawn, '.setUsedMassDestruction(')
    rows = {e['id'].split(':')[1]: e for e in review['effects']}
    def values(key, primitive):
        return {p: v for c in rows[key]['components'] if c['primitive'] == primitive
                for p, v in c['numerical_parameters'].items()}
    assert values('guardian_uppercut', 'STUN') == {'duration_ticks': 60}
    assert values('guardian_bullet_family', 'LEVITATION') == {'duration_ticks': 100}
    assert values('guardian_void_runes', 'NATIVE_DAMAGE_REQUEST') == {'amount': 9.0}
    assert values('guardian_void_vortex', 'FORCED_MOVEMENT') == {'downward_y': -2.0, 'pull_factor': 0.075}
    assert values('guardian_void_vortex', 'NATIVE_EXPLOSION') == {'power': 2.0}
    assert values('guardian_body_repulsion', 'FORCED_MOVEMENT') == {'horizontal_coefficient': -0.1}
    assert not any('active_window_ticks' in c['parameters'] for c in rows['guardian_void_runes']['scalable_parameter_candidates'])


def validate(jar_path=None):
    review, note, ledger = read_json(REVIEW), read_json(NOTE), read_json(LEDGER)
    summary = validate_records(review, note, ledger)
    validate_preservation(note)
    methods = validate_evidence(review, note, jar_path)
    validate_native_distinctions(review)
    return dict(status='PASS', **summary, new_native_witnesses=14,
                new_native_methods=methods, jar_reproduced=jar_path is not None,
                protected_r2k3a='BYTE_IDENTICAL', whole_mod_complete=False, runtime_tests=0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jar', type=Path, help='Optionally reproduce only new scoped witnesses')
    args = parser.parse_args()
    print(json.dumps(validate(args.jar), indent=2))
