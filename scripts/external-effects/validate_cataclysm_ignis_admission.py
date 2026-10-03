"""Focused read-only R2k5a validation and optional pinned-JAR reproduction."""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import subprocess

from catalog_common import OUT, ROOT, read_json
from collect_cataclysm_ignis_admission import (
    ALTAR, AM, BASE, EVIDENCE_FILE, FRAGMENTS, I, MM, PKG, REGISTRY,
    SPEC_FILE, collect, specification,
)

START = 'aa13dd0f69626f4e8491d2f397c90e80aebdc3ab'
CHECKPOINT = 'R2k5a-cataclysm-ignis-admission-complete'
NOTE = OUT / 'cataclysm-r2k5a-ignis-admission.json'
REVIEW = OUT / 'mod-reviews/cataclysm.json'
LEDGER = OUT / 'mod-completion-ledger.json'
KINDS = {'VANILLA_DIRECT', 'VANILLA_EQUIVALENT', 'VANILLA_LIKE_EXTENDED',
         'VANILLA_COMPOSITE', 'CUSTOM_DAMAGE', 'CUSTOM_STATUS',
         'CUSTOM_CONTROL', 'CUSTOM_RESOURCE', 'BINARY_MECHANIC'}
KEYS = {'incoming_admission', 'counter_admission', 'shield_admission', 'shield_state',
        'phase_prerequisites', 'shared_defense_bindings', 'nature_regen_binding', 'encounter_state'}
ORDER = ['READ_DIRECT_TARGET_AND_CAUSING_RANGE_SQUARED', 'REACTIVE_COUNTER_STATE_AND_WINDOW_RETURN',
    'ABYSS_DIRECT_CLASS_CAUSING_IGNIS_REJECT', 'ABYSS_PROJECTILE_TAG_SERVER_DURABILITY_INCREMENT',
    'PHASE_OR_ULTIMATE_HALF_UNLESS_INVULNERABILITY_BYPASS',
    'PHASE2_PHASE3_OR_STRIKE_REJECT_UNLESS_INVULNERABILITY_BYPASS',
    'ORDINARY_IGNIS_FIREBALL_DIRECT_REJECT', 'POSITIVE_DIRECTIONAL_SHIELD_CALLBACKS_AND_FALSE',
    'ARM_TERRAIN_TIMER_BEFORE_SHARED_HURT', 'SHARED_HURT_SAME_SOURCE', 'RETURN_NATIVE_HURT_RESULT']


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
        assert e['components'] and e['implementation'] and e['primary_test_source'] and e['source_actor']
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
            assert len(owners) == 1
            owner = owners[0]
            assert c['native_value'] == owner['numerical_parameters'][p]
            assert c['native_formula'] == owner['formula']
            assert c['units'] == owner['parameter_units'][p]
            assert c['native_boundary'] == owner['native_boundary']
        if e['id'] != 'cataclysm:ignis_nature_regen_binding':
            assert not candidates, 'Admission/setup constants are not new scalar candidates'
    new_paths = [p for p in paths if p['id'].startswith('cataclysm:ignis-admission:')]
    assert len(new_paths) == 8
    for p in new_paths:
        assert p['mod_key'] == 'cataclysm' and p['status'] == 'VERIFIED'
        assert p['primary_source'] and p['native_path'] and p['setup'] and p['implementation']
        assert p['labels'] and p['runtime_status'] == 'NOT_RUN'
        assert p['effect_ids'] and set(p['effect_ids']) <= eids
        for e in new:
            assert (p['id'] in e['delivery_paths']) == (e['id'] in p['effect_ids'])
    assert {m['id'] for m in note['mechanic_packages']} == {e['id'] for e in new}
    for m, e in zip(note['mechanic_packages'], new):
        assert m['id'] == e['id'] and m['primary_classification'] == e['primary_classification']
        assert m['delivery_paths'] == e['delivery_paths'] and m['binary_gates'] == e['binary_parameters']
        assert m['numerical_candidates'] == [{k: c[k] for k in ['primitive', 'parameters',
            'native_value', 'units', 'native_boundary']} for c in e['scalable_parameter_candidates']]
    summary = dict(new_mechanics=len(new), delivery_paths=len(new_paths),
        classifications=dict(sorted(Counter(e['primary_classification'] for e in new).items())),
        candidate_numeric_parameters=sum(len(c['parameters']) for e in new for c in e['scalable_parameter_candidates']),
        shared_binding_records=1, unresolved_subsection_ambiguities=0)
    assert summary == note['summary'] and summary['candidate_numeric_parameters'] == 1
    assert review['status'] == ledger['status'] == note['status'] == 'PARTIAL'
    for field in ['semantic_discovery_complete', 'special_damage_discovery_complete',
                  'source_mapping_complete', 'delivery_mapping_complete']:
        assert review[field] is False
    cat = next(t for t in ledger['targets'] if t['mod_key'] == 'cataclysm')
    assert cat['state'] == 'PARTIAL' and cat['semantic_effect_count'] == len(effects)
    assert review['checkpoint'] == ledger['checkpoint'] == note['checkpoint'] == CHECKPOINT
    assert review['exact_next_task'] == note['exact_next_task'] == cat['exact_next_task']
    assert note['exact_next_task'].startswith('R2k5b: Ignis offense/payload family.')
    assert note['remaining_ignis_work'] and not note['remaining_subsection_native_ambiguities']
    assert note['whole_mod_complete'] is False and note['runtime_tests'] == 0
    assert all(note[k] is False for k in ['stage_eligibility_decided', 'phase6_reopened',
        'production_changed', 'stage_changed', 'boss_testing_started', 'l2_testing_started',
        'compatibility_fixes_started', 'phase7_started'])
    validate_contracts({e['id'].removeprefix('cataclysm:ignis_'): e for e in new}, note)
    return summary


def validate_contracts(rows, note):
    def values(key, primitive):
        return next(c['numerical_parameters'] for c in rows[key]['components'] if c['primitive'] == primitive)

    assert note['admission_order']['concrete'] == rows['incoming_admission']['admission_order'] == ORDER
    incoming = rows['incoming_admission']
    assert incoming['invulnerability_bypass_skips_all_prefilters'] is False
    assert incoming['terrain_timer_requires_hurt_true'] is False and incoming['shared_return_forwarded'] is True
    assert incoming['source_actor_distinctions']['source_rewritten'] is False
    assert values('incoming_admission', 'INCOMING_DAMAGE_MULTIPLIER') == {'phase_multiplier': 0.5}
    assert rows['counter_admission']['counter_range_reader'] == 'CAUSING_DISTANCE_SQUARED'
    assert rows['counter_admission']['null_causing_range'] == -1
    assert rows['counter_admission']['requires_hurt_success'] is False
    shield = rows['shield_admission']
    assert shield['shield_bypass_tag'] == 'BYPASSES_SHIELD' and shield['native_shield_damage_noop'] is True
    assert all(shield[k] is False for k in ['recoil_requires_shared_hurt', 'checks_arrow_piercing',
        'reads_show_shield', 'reads_shield_break_flag', 'shield_callback_changes_custom_durability'])
    state = rows['shield_state']
    assert state['shield_window_default'] == state['shield_windows']['OTHER_ANIMATION'] == 'RETAIN_PREVIOUS_IS_SHIELD'
    assert all(state[k] is False for k in ['break_setter_clears_admission_flag',
        'durability_increment_requires_hurt_true', 'durability_setter_clamps', 'break_false_restores_shield'])
    phase = rows['phase_prerequisites']
    assert phase['selection_order'] == ['SHIELD_BREAK', 'PHASE_2', 'PHASE_3']
    assert all(phase[k] is False for k in ['requires_target', 'requires_line_of_sight', 'local_server_guard',
        'phase_setter_changes_health', 'phase_setter_changes_attributes', 'phase_setter_changes_shield'])
    assert phase['native_state_bindings'] == dict(default_phase=0, phase2_committed_value=1,
        phase3_committed_value=2, phase2_goal_priority=1, phase3_goal_priority=1, break_goal_priority=1)
    cfg = read_json(OUT / 'cataclysm-installed-common-config.json')['values']['mobs']['ignis']
    expected = {'DamageCap': ('damageCap', cfg['cap_config']['damage_cap']),
                'DpsCap': ('dpsCap', cfg['cap_config']['dps_cap']),
                'RangeLimit': ('rangeCap', cfg['cap_config']['range_cap']),
                'NatureRegen': ('natureHeal', cfg['nature_heal_config']['nature_heal'])}
    for name, (field, value) in expected.items():
        assert note['concrete_bindings'][name]['config_field'] == 'Ignis.' + field
        assert note['concrete_bindings'][name]['installed_value'] == value
        assert note['concrete_bindings'][name]['shared_boundary']
    assert note['concrete_bindings']['HealCooldown']['native_value'] == 200
    assert rows['shared_defense_bindings']['has_concrete_invulnerability_override'] is False
    assert rows['shared_defense_bindings']['registered_fire_immune'] is True
    assert values('shared_defense_bindings', 'DAMAGE_CAP') == {'per_hit_cap': 20.0}
    assert values('shared_defense_bindings', 'DPS_BUCKET') == {
        'capacity': 20.0, 'dps_cap': 14.0, 'drain_divisor': 20, 'full_bucket_request': 0.10000000149011612}
    assert values('shared_defense_bindings', 'RANGE_ADMISSION') == {'range_limit': 15.0}
    regen = rows['nature_regen_binding']
    assert regen['record_kind'] == 'SHARED_BINDING' and regen['binding_of'] == 'cataclysm:shared_heal'
    assert regen['scalable_parameter_candidates'][0]['primitive'] == 'NATIVE_HEAL'
    assert values('nature_regen_binding', 'NATIVE_HEAL') == {'amount': 25.0}
    encounter = rows['encounter_state']
    persist = encounter['persistence']
    assert persist['saved_keys'] == persist['load_order'] == ['BossPhase', 'Is_Shield_Break', 'Shield_Durability']
    assert persist['raw_saved_durability_overwrites_break_setter'] is True
    assert {'IS_SHIELD', 'blockingProgress', 'animation', 'animationTick', 'bucket', 'homeTicks'} <= set(persist['not_saved_here'])
    assert encounter['synced_defaults'] == dict(BossPhase=0, ShieldDurability=0, IsBlocking=False,
        IsShield=False, IsShieldBreak=False, IsSword=False, ShowShield=True)
    gates = encounter['encounter']
    assert gates['item'] == 'cataclysm:burning_ashes'
    assert all(gates[k] is False for k in ['altar_calls_finalize_spawn', 'requires_player',
        'requires_nonpeaceful', 'requires_no_existing_boss', 'reads_defeat_flag', 'saves_summoning_timer'])
    assert gates['item_consumption_requires_add_success'] is True and gates['failed_add_retries'] is True


def validate_preservation(review, note, ledger):
    assert note['starting_sha'] == START
    old = json.loads(at_start(REVIEW))
    assert [e for e in review['effects'] if e['review_checkpoint'] != CHECKPOINT] == old['effects']
    assert [p for p in review['paths'] if not p['id'].startswith('cataclysm:ignis-admission:')] == old['paths']
    mutable = {'effects', 'paths', 'checkpoint', 'scope', 'notes_file', 'exact_next_task', 'protected_checkpoints'}
    assert {k: v for k, v in review.items() if k not in mutable} == {k: v for k, v in old.items() if k not in mutable}
    assert review['protected_checkpoints'][:-1] == old['protected_checkpoints']
    assert review['protected_checkpoints'][-1] == dict(checkpoint=old['checkpoint'], notes_file=old['notes_file'])
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


def validate_evidence(review, note, jar_path=None):
    assert read_json(SPEC_FILE) == specification()
    evidence = read_json(EVIDENCE_FILE)
    assert len(evidence['witnesses']) == 8
    if jar_path is not None:
        assert evidence == collect(jar_path), 'Pinned-JAR witnesses did not reproduce'
    census = {c['entry']: c['entry_sha256'] for c in read_json(OUT / 'cataclysm-source-census.json')['classes']}
    sources = {r['file']: read_json(OUT / r['file']) for r in note['reference_files']
               if r['file'].startswith('native-evidence/')}
    methods = {(w['entry'], m['name'], m['descriptor']): m
               for w in evidence['witnesses'] for m in w.get('methods', [])}
    for f, data in sources.items():
        if f == EVIDENCE_FILE.relative_to(OUT).as_posix():
            continue
        for w in data['witnesses']:
            for old in w.get('methods', []):
                new = methods.get((w['entry'], old['name'], old['descriptor']))
                if new is not None:
                    assert 'instruction_offset_ranges' in new, 'Previously captured method duplicated'
                    assert new['code_sha256'] == old['code_sha256']
                    assert not {i['offset'] for i in new['instructions']} & {
                        i['offset'] for i in old['instructions']}, 'Previously captured fragment duplicated'
    for w in evidence['witnesses']:
        assert w['jar_sha256'] == note['tooling']['jar_sha256']
        assert w['entry_sha256'] == census[w['entry']]
        if w['entry'] in [PKG + n + '.class' for n in [I, BASE, MM, AM]]:
            assert not {'isInvulnerableTo', 'hurtCurrentlyUsedShield', 'blockUsingShield'} & set(w['declared_method_names'])
        for m in w['methods']:
            if 'instruction_offset_ranges' in m:
                assert m['instruction_offset_ranges'] == FRAGMENTS[w['entry'][len(PKG):-6]][m['name']]
    for e in selected(review):
        for p in e['implementation']:
            w = next(w for w in sources[p['evidence_file']]['witnesses'] if w['id'] == p['witness_id'])
            assert p['entry'] == w['entry']
            assert set(p['methods']) <= {m['name'] for m in w.get('methods', [])}
    validate_native_distinctions(evidence)
    return len(methods)


def validate_native_distinctions(evidence):
    reused_stun = read_json(OUT / 'native-evidence/cataclysm-stun.json')

    def body(name, method, data=evidence):
        w = next(w for w in data['witnesses'] if w['entry'] == PKG + name + '.class')
        return next(m['instructions'] for m in w['methods'] if m['name'] == method)

    def calls(ins, name):
        return [i['offset'] for i in ins if name in str(i.get('operand', ''))]

    def item(ins, offset):
        return next(i for i in ins if i['offset'] == offset)

    hurt = body(I, 'hurt')
    assert calls(hurt, '.getDirectEntity(')[0] == 1 and calls(hurt, '.calculateRange(') == [13]
    assert calls(hurt, '.setAnimation(') == [138]
    assert calls(hurt, '.sendAnimationMessage(') == [176, 253]
    assert calls(hurt, '.setShieldDurability(') == [367]
    assert item(hurt, 448)['operand'] == 0.5
    assert calls(hurt, '.canBlockDamageSource(') == [516]
    assert calls(hurt, '.hurtCurrentlyUsedShield(') == [524] and calls(hurt, '.blockUsingShield(') == [549]
    assert calls(hurt, 'LLibrary_Boss_Monster.hurt(') == [603]
    assert item(hurt, 589)['operand'] == 20
    block = body(I, 'canBlockDamageSource')
    assert calls(block, 'BYPASSES_SHIELD') and not calls(block, 'BYPASSES_INVULNERABILITY')
    assert calls(block, '.getIsShield(') == [41] and calls(block, '.getSourcePosition(') == [48]
    assert calls(block, '.normalize(') == [74] and calls(block, '.dot(') == [103]
    assert not calls(block, '.getShowShield(') and not calls(block, '.getIsShieldBreak(')
    loaded = body(I, 'readAdditionalSaveData')
    assert calls(loaded, '.setBossPhase(') == [13]
    assert calls(loaded, '.setIsShieldBreak(') == [24] and calls(loaded, '.setShieldDurability(') == [35]
    assert not calls(body(I, 'setIsShieldBreak'), '.setIsShield(')
    assert not calls(body(I, 'setBossPhase'), '.setHealth(')
    tick, ai = body(I, 'tick', reused_stun), body(I, 'aiStep', reused_stun)
    assert calls(tick, '.setAnimation(')[:3] == [1569, 1622, 1675]
    assert calls(ai, '.setBossPhase(') == [1681, 1755] and calls(ai, '.setIsShieldBreak(') == [1207]
    assert not any(m['name'] in ['tick', 'aiStep'] for w in evidence['witnesses']
                   if w['entry'] == PKG + I + '.class' for m in w['methods'])
    altar = body(ALTAR, 'tick')
    assert calls(altar, '.setHomePos(') == [201] and calls(altar, '.addFreshEntity(') == [207]
    assert item(altar, 214)['opcode'] == '0x99', 'Native add result gates consumption'
    assert not calls(altar, '.finalizeSpawn(') and not calls(altar, '.getDifficulty(')
    assert item(altar, 102)['operand'] == 121
    native = read_json(OUT / 'reference-evidence/twilight-minoshroom-knight-244.json')
    living = next(w for w in native['witnesses'] if w['entry'] == 'net/minecraft/world/entity/LivingEntity.class')
    noop = next(m for m in living['methods'] if m['name'] == 'hurtCurrentlyUsedShield')
    assert noop['code_hex'] == 'b1'


def validate(jar_path=None):
    review, note, ledger = [read_json(p) for p in [REVIEW, NOTE, LEDGER]]
    summary = validate_records(review, note, ledger)
    validate_preservation(review, note, ledger)
    methods = validate_evidence(review, note, jar_path)
    return dict(status='PASS', **summary, new_method_witnesses=methods,
        protected_shared_status_guardian_monstrosity='BYTE_IDENTICAL', prior_records_and_paths='UNCHANGED',
        pinned_jar='REPRODUCED' if jar_path is not None else 'ARCHIVED_WITNESSES_VALIDATED')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jar', type=Path, help='Optional exact pinned Cataclysm 3.27 JAR')
    print(json.dumps(validate(parser.parse_args().jar), indent=2))
