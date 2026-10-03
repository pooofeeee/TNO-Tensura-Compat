"""Focused, read-only R2k4a admission/setup and protected-checkpoint validation."""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import subprocess
import zipfile

from catalog_common import OUT, ROOT, read_json
from classfile import ClassFile
from collect_cataclysm_monstrosity_admission import (
    EVIDENCE_FILE, FRAGMENTS, M, P, PKG, REGISTRY, S, SPEC_FILE, collect, specification,
)

START = 'ede50693160cf2b0a37da8d82b17f042e625baf6'
CHECKPOINT = 'R2k4a-cataclysm-monstrosity-admission-complete'
NOTE = OUT / 'cataclysm-r2k4a-monstrosity-admission.json'
REVIEW = OUT / 'mod-reviews/cataclysm.json'
LEDGER = OUT / 'mod-completion-ledger.json'
KINDS = {'VANILLA_DIRECT', 'VANILLA_EQUIVALENT', 'VANILLA_LIKE_EXTENDED',
         'VANILLA_COMPOSITE', 'CUSTOM_DAMAGE', 'CUSTOM_STATUS',
         'CUSTOM_CONTROL', 'CUSTOM_RESOURCE', 'BINARY_MECHANIC'}
KEYS = {'monstrosity_incoming_admission', 'monstrosity_head_admission',
        'monstrosity_shared_defense_bindings', 'monstrosity_awakening',
        'monstrosity_berserk_phase', 'monstrosity_encounter_state', 'monstrosity_nature_regen_binding'}
ORDER = dict(
    body=['BODY_STATE4_UNLESS_INVULNERABILITY_BYPASS', 'DIRECT_GOLEM_HALF', 'SHARED_HURT',
          'AWAKEN_IF_RETURN_TRUE_ALIVE_AND_UNAWAKENED'],
    head=['PART_NATIVE_INVULNERABILITY', 'HEAD_X1_5_FLOAT_MAX_CLAMP', 'SHARED_HURT'],
    shared=['VIRTUAL_NATIVE_INVULNERABILITY', 'INVULNERABILITY_BYPASS_EARLY_NATIVE_RETURN',
            'PER_HIT_DAMAGE_CAP', 'CAUSING_ENTITY_RANGE', 'SAVE_BUCKET', 'BUCKET_UNLESS_HURT_TIME_BYPASS',
            'NATIVE_HURT', 'REGEN_TIMER_IF_TRUE_AND_TAGGED', 'BUCKET_ROLLBACK_IF_FALSE'])


def at_start(path):
    return subprocess.check_output(['git', 'show', START + ':' + Path(path).relative_to(ROOT).as_posix()], cwd=ROOT)


def selected(review):
    return [e for e in review['effects'] if e['review_checkpoint'] == CHECKPOINT]


def values(effects, key, primitive):
    e = next(e for e in effects if e['id'] == 'cataclysm:' + key)
    return {p: v for c in e['components'] if c['primitive'] == primitive
            for p, v in c['numerical_parameters'].items()}


def validate_records(review, note, ledger):
    effects, paths = review['effects'], review['paths']
    assert len(effects) == len({e['id'] for e in effects})
    assert len(paths) == len({p['id'] for p in paths})
    assert effects == sorted(effects, key=lambda e: e['id'])
    assert paths == sorted(paths, key=lambda p: p['id'])
    new = selected(review)
    assert len(new) == 7 and {e['id'] for e in new} == {'cataclysm:' + k for k in KEYS}
    pids, eids = {p['id'] for p in paths}, {e['id'] for e in effects}
    for e in new:
        assert e['mod_key'] == 'cataclysm' and e['primary_classification'] in KINDS
        assert e['inspection_status'] == 'STATIC_REVIEWED' and not e['unresolved_ambiguities']
        assert e['components'] and e['implementation'] and e['primary_test_source']
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
        seen = set()
        for c in e['scalable_parameter_candidates']:
            assert len(c['parameters']) == 1
            p = c['parameters'][0]
            assert (c['primitive'], p) not in seen
            seen.add((c['primitive'], p))
            owner = [x for x in e['components'] if x['primitive'] == c['primitive'] and p in x['numerical_parameters']]
            assert len(owner) == 1
            assert c['native_value'] == owner[0]['numerical_parameters'][p]
            assert c['native_formula'] == owner[0]['formula']
            assert c['units'] == owner[0]['parameter_units'][p]
            assert c['native_boundary'] == owner[0]['native_boundary']
        if e['primary_classification'] == 'BINARY_MECHANIC':
            assert not e['scalable_parameter_candidates'], 'Admission constants must not become candidates'
    new_paths = [p for p in paths if p['id'].startswith('cataclysm:monstrosity-admission:')]
    assert len(new_paths) == 7
    for p in new_paths:
        assert p['mod_key'] == 'cataclysm' and p['status'] == 'VERIFIED'
        assert p['primary_source'] and p['native_path'] and p['setup'] and p['implementation']
        assert p['labels'] and p['runtime_status'] == 'NOT_RUN'
        assert p['effect_ids'] and set(p['effect_ids']) <= eids
        for e in new:
            assert (p['id'] in e['delivery_paths']) == (e['id'] in p['effect_ids'])
    assert note['admission_order'] == ORDER
    cfg = read_json(OUT / 'cataclysm-installed-common-config.json')['values']['mobs']['netherite_monstrosity']
    expected = {'DamageCap': ('damageCap', cfg['cap_config']['damage_cap']),
                'DpsCap': ('dpsCap', cfg['cap_config']['dps_cap']),
                'RangeLimit': ('rangeCap', cfg['cap_config']['range_cap']),
                'NatureRegen': ('natureHeal', cfg['nature_heal_config']['nature_heal'])}
    for name, (field, value) in expected.items():
        b = note['concrete_bindings'][name]
        assert b['config_field'] == 'NetheriteMonstrosity.' + field and b['installed_value'] == value
        assert b['shared_boundary']
    assert note['concrete_bindings']['HealCooldown']['native_value'] == 200
    assert values(new, 'monstrosity_incoming_admission', 'INCOMING_DAMAGE_MULTIPLIER') == {'direct_golem_multiplier': 0.5}
    assert values(new, 'monstrosity_head_admission', 'INCOMING_DAMAGE_MULTIPLIER') == {'head_multiplier': 1.5}
    assert values(new, 'monstrosity_shared_defense_bindings', 'DAMAGE_CAP') == {'per_hit_cap': 25.0}
    assert values(new, 'monstrosity_shared_defense_bindings', 'DPS_BUCKET') == {
        'capacity': 25.0, 'dps_cap': 20.0, 'drain_divisor': 20, 'full_bucket_request': 0.10000000149011612}
    assert values(new, 'monstrosity_shared_defense_bindings', 'RANGE_ADMISSION') == {'range_limit': 18.0}
    rows = {e['id'].split(':')[1]: e for e in new}
    assert rows['monstrosity_head_admission']['routing'] == dict(part_entry='hurtParts',
        alternative_entry='attackEntityFromPart -> body hurt', part_skips_body_gate=True,
        part_skips_direct_golem_half=True, part_skips_body_awakening=True, part_skips_shared_admission=False)
    assert rows['monstrosity_awakening']['state_binding'] == dict(idle_goal_priority=0,
        awakening_goal_priority=1, start_state=2, active_state=2, end_state=0, final_tick_inclusive=40,
        sleep_states=[1, 2], awake_setter_sets_attack_state=False, awake_setter_sets_home=False,
        true_setter_recounts_native_life=True)
    assert rows['monstrosity_berserk_phase']['state_binding'] == dict(goal_priority=0, start_state=0,
        active_state=4, end_state=0, final_tick_inclusive=54, continuation_rechecks_active_state=False,
        flag_latched=True, setter_changes_health_or_attributes=False)
    persistence = rows['monstrosity_encounter_state']['persistence']
    assert persistence['saved_keys'] == ['is_Berserk', 'is_Awaken', 'Magazine']
    assert persistence['not_saved_here'] == ['attackState', 'attackTicks', 'homeTicks', 'self_regen', 'bucket']
    assert persistence['native_template_flags'] == {'is_Awaken': 0, 'is_Berserk': 0, 'Magazine': 0, 'Invulnerable': 0}
    assert not persistence['template_contains_home'] and not persistence['template_contains_attack_state']
    assert persistence['awake_spawn_types'] == ['COMMAND', 'SPAWN_EGG', 'MobSpawnType.isSpawner(type)', 'DISPENSER']
    assert persistence['concrete_death_state'] == 5 and persistence['native_deathtimer'] == 60
    regen = rows['monstrosity_nature_regen_binding']
    assert regen['record_kind'] == 'SHARED_BINDING' and regen['binding_of'] == 'cataclysm:shared_heal'
    assert values(new, 'monstrosity_nature_regen_binding', 'NATIVE_HEAL') == {'amount': 25.0}
    assert regen['scalable_parameter_candidates'][0]['primitive'] == 'NATIVE_HEAL'
    assert review['status'] == 'PARTIAL' and ledger['status'] == 'PARTIAL'
    for field in ['semantic_discovery_complete', 'special_damage_discovery_complete',
                  'source_mapping_complete', 'delivery_mapping_complete']:
        assert review[field] is False
    cat = next(t for t in ledger['targets'] if t['mod_key'] == 'cataclysm')
    assert cat['state'] == 'PARTIAL' and cat['semantic_effect_count'] == len(effects)
    assert review['checkpoint'] == ledger['checkpoint'] == note['checkpoint'] == CHECKPOINT
    assert review['exact_next_task'] == note['exact_next_task'] == cat['exact_next_task']
    assert note['exact_next_task'].startswith('R2k4b: Netherite Monstrosity offense/payload family.')
    assert note['whole_mod_complete'] is False and note['runtime_tests'] == 0
    assert note['stage_eligibility_decided'] is False and note['remaining_monstrosity_work']
    assert all(note[k] is False for k in ['phase6_reopened', 'production_changed', 'stage_changed',
        'boss_testing_started', 'l2_testing_started', 'compatibility_fixes_started', 'phase7_started'])
    assert not note['remaining_subsection_native_ambiguities']
    assert {m['id'] for m in note['mechanic_packages']} == {e['id'] for e in new}
    for m, e in zip(note['mechanic_packages'], new):
        assert m['id'] == e['id'] and m['primary_classification'] == e['primary_classification']
        assert m['delivery_paths'] == e['delivery_paths'] and m['binary_gates'] == e['binary_parameters']
        assert m['numerical_candidates'] == [{k: c[k] for k in ['primitive', 'parameters', 'native_value',
            'units', 'native_boundary']} for c in e['scalable_parameter_candidates']]
    summary = dict(new_mechanics=7, delivery_paths=7,
        classifications=dict(sorted(Counter(e['primary_classification'] for e in new).items())),
        candidate_numeric_parameters=sum(len(c['parameters']) for e in new for c in e['scalable_parameter_candidates']),
        shared_binding_records=1, unresolved_subsection_ambiguities=0)
    assert summary == note['summary'] and summary['candidate_numeric_parameters'] == 1
    return summary


def validate_preservation(review, note, ledger):
    assert note['starting_sha'] == START
    old = json.loads(at_start(REVIEW))
    assert [e for e in review['effects'] if e['review_checkpoint'] != CHECKPOINT] == old['effects']
    assert [p for p in review['paths'] if not p['id'].startswith('cataclysm:monstrosity-admission:')] == old['paths']
    mutable = {'effects', 'paths', 'checkpoint', 'scope', 'notes_file', 'exact_next_task', 'protected_checkpoints'}
    assert {k: v for k, v in review.items() if k not in mutable} == {k: v for k, v in old.items() if k not in mutable}
    protected = note['protected_guardian']
    assert [p['file'] for p in protected] == ['cataclysm-r2k3a-guardian-admission.json', 'cataclysm-r2k3b-guardian-offense.json']
    for reference in note['reference_files']:
        path = OUT / reference['file']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == reference['sha256'], reference['file']
        if reference['usage'] == 'LOCKED_REUSED':
            assert path.read_bytes() == at_start(path), reference['file']
    for p in protected:
        assert (OUT / p['file']).read_bytes() == at_start(OUT / p['file'])
    previous = json.loads(at_start(LEDGER))
    assert [t for t in ledger['targets'] if t['mod_key'] != 'cataclysm'] == [
        t for t in previous['targets'] if t['mod_key'] != 'cataclysm']
    assert {k: v for k, v in ledger.items() if k not in ['targets', 'checkpoint']} == {
        k: v for k, v in previous.items() if k not in ['targets', 'checkpoint']}


def validate_evidence(review, note, jar_path=None):
    assert read_json(SPEC_FILE) == specification()
    evidence = read_json(EVIDENCE_FILE)
    assert len(evidence['witnesses']) == 10
    if jar_path is not None:
        assert evidence == collect(jar_path), 'Pinned-JAR evidence did not reproduce'
        # Declaration-only checks reuse the proven hierarchy, without capturing
        # another copy of shared methods or inspecting any offense bodies.
        with zipfile.ZipFile(jar_path) as jar:
            for name in note['hierarchy'][:-1]:
                c = ClassFile(jar.read(PKG + name + '.class'))
                assert 'isInvulnerableTo' not in {m['name'] for m in c.methods}
    census = {c['entry']: c['entry_sha256'] for c in read_json(OUT / 'cataclysm-source-census.json')['classes']}
    sources = {r['file']: read_json(OUT / r['file']) for r in note['reference_files']
               if r['file'].startswith('native-evidence/')}
    methods = {(w['entry'], m['name'], m['descriptor']) for w in evidence['witnesses'] for m in w.get('methods', [])}
    reused = {(w['entry'], m['name'], m['descriptor']) for f, d in sources.items() if f != EVIDENCE_FILE.relative_to(OUT).as_posix()
              for w in d['witnesses'] for m in w.get('methods', [])}
    assert not methods & reused, 'Previously captured native evidence was duplicated'
    for w in evidence['witnesses']:
        assert w['jar_sha256'] == note['tooling']['jar_sha256']
        if w['entry'].endswith('.class'):
            assert w['entry_sha256'] == census[w['entry']]
        for m in w.get('methods', []):
            if 'instruction_offset_range' in m:
                assert m['instruction_offset_range'] == FRAGMENTS[w['entry'][len(PKG):-6]][m['name']]
    for e in selected(review):
        for p in e['implementation']:
            w = next(w for w in sources[p['evidence_file']]['witnesses'] if w['id'] == p['witness_id'])
            assert p['entry'] == w['entry']
            assert set(p['methods']) <= {m['name'] for m in w.get('methods', [])}
    return evidence, len(methods)


def validate_native_distinctions(evidence):
    def witness(name):
        return next(w for w in evidence['witnesses'] if w['entry'] == PKG + name + '.class')
    def body(name, method):
        return next(m['instructions'] for m in witness(name)['methods'] if m['name'] == method)
    def hits(ins, operand):
        return [i for i in ins if operand in str(i.get('operand', ''))]
    def at(ins, operand):
        return hits(ins, operand)[0]['offset']
    hurt = body(M, 'hurt')
    assert [at(hurt, x) for x in ['.getAttackState(', 'BYPASSES_INVULNERABILITY', '.getDirectEntity(',
        'AbstractGolem', 'IABoss_monster.hurt(', '.getIsAwaken(', '.isAlive(', '.setIsAwaken(']] == [1, 9, 21, 26, 41, 52, 59, 67]
    assert not hits(hurt, '.getEntity(')
    part, head = body(P, 'hurt'), body(M, 'hurtParts')
    assert at(part, '.isInvulnerableTo(') < at(part, '.hurtParts(')
    assert not hits(part, '.attackEntityFromPart(')
    assert at(head, 'Math.min(') < at(head, 'IABoss_monster.hurt(')
    assert not hits(head, '.getAttackState(') and not hits(head, '.getDirectEntity(') and not hits(head, '.setIsAwaken(')
    assert hits(body(M, 'attackEntityFromPart'), '.hurt(')
    for name, field in [('DamageCap', '.damageCap'), ('DpsCap', '.dpsCap'), ('RangeLimit', '.rangeCap'), ('NatureRegen', '.natureHeal')]:
        assert hits(body(M, name), 'CMCommonConfig$NetheriteMonstrosity' + field)
    assert 'isInvulnerableTo' not in witness(M)['declared_method_names']
    assert 'isInvulnerableTo' not in witness('entity/partentity/Cm_Part_Entity')['declared_method_names']
    assert hits(body(REGISTRY, 'lambda$static$2'), '.fireImmune(')
    assert 'netherite_monstrosity' in [i['operand'] for i in body(REGISTRY, '<clinit>')]
    boot = witness(REGISTRY)['registration_bootstraps']
    assert PKG + M + '.<init>(Lnet/minecraft/world/entity/EntityType;Lnet/minecraft/world/level/Level;)V' in boot[0]['arguments']
    assert PKG + REGISTRY + '.lambda$static$2()Lnet/minecraft/world/entity/EntityType;' in boot[1]['arguments']
    setter = body(M, 'setIsAwaken')
    assert hits(setter, '.PlayerCounter(') and not hits(setter, '.setAttackState(') and not hits(setter, '.setHomePos(')
    awake_start = body(M + '$3', 'start')
    assert at(awake_start, '.setHomePos(') < at(awake_start, '.setIsAwaken(')
    assert hits(body(S, 'canContinueToUse'), '.getAttackState(')
    phase = M + '$MonstrosityPhaseChangeGoal'
    assert at(body(phase, 'start'), '.setIsBerserk(') < at(body(phase, 'start'), '.setAttackState(')
    assert not hits(body(phase, 'canContinueToUse'), '.getAttackState(')
    assert not hits(body(M, 'setIsBerserk'), '.setHealth(') and not hits(body(M, 'setIsBerserk'), '.getAttribute(')
    assert [i['operand'] for i in body(M, 'isBerserk') if isinstance(i['operand'], float)] == [0.4000000059604645]
    spawn = body(M, 'finalizeSpawn')
    for name in ['MobSpawnType.COMMAND', 'MobSpawnType.SPAWN_EGG', 'MobSpawnType.isSpawner(', 'MobSpawnType.DISPENSER']:
        assert hits(spawn, name)
    assert not hits(spawn, '.setHomePos(') and not hits(spawn, '.setAttackState(')
    die = body(M, 'die')
    assert at(die, 'IABoss_monster.die(') < at(die, '.setAttackState(')
    assert [i['operand'] for i in die if isinstance(i['operand'], int)] == [5]
    assert [i['operand'] for i in body(M, 'deathtimer') if isinstance(i['operand'], int)] == [60]
    defeat = body(M, 'AfterDefeatBoss')
    for name in ['.respawner', '.getHomePos(', '.getLevel(', '.setBlock(', '.NETHERITE_MONSTROSITY', '.MONSTROUS_EYE']:
        assert hits(defeat, name)
    template = next(w['data'] for w in evidence['witnesses'] if w['id'].endswith(':encounter-template'))
    assert len(template['entities']) == 1
    entity = template['entities'][0]
    assert {k: entity[k] for k in ['Health', 'is_Awaken', 'is_Berserk', 'Magazine', 'Invulnerable']} == {
        'Health': 600.0, 'is_Awaken': 0, 'is_Berserk': 0, 'Magazine': 0, 'Invulnerable': 0}
    assert not any(k in entity for k in ['Home', 'HomePos', 'HomePoint', 'AttackState', 'NoAI'])
    pool = next(w['data'] for w in evidence['witnesses'] if w['id'].endswith(':encounter-pool'))
    assert pool['elements'][0]['element']['location'] == 'cataclysm:monstrosity'


def validate(jar_path=None):
    review, note, ledger = read_json(REVIEW), read_json(NOTE), read_json(LEDGER)
    summary = validate_records(review, note, ledger)
    validate_preservation(review, note, ledger)
    evidence, methods = validate_evidence(review, note, jar_path)
    validate_native_distinctions(evidence)
    return dict(status='PASS', **summary, new_native_witnesses=10, new_native_methods=methods,
                jar_reproduced=jar_path is not None, protected_guardian='BYTE_IDENTICAL',
                protected_shared_status='BYTE_IDENTICAL', whole_mod_complete=False, runtime_tests=0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jar', type=Path, help='Reproduce only new scoped witnesses against the pinned JAR')
    print(json.dumps(validate(parser.parse_args().jar), indent=2))
