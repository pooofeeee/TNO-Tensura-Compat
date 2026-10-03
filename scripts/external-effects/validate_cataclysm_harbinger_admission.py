"""Focused read-only R2k6a validation and optional pinned-JAR reproduction."""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import subprocess

from catalog_common import OUT, ROOT, read_json
from collect_cataclysm_harbinger_admission import (
    AM, AWAKEN, BASE, EVIDENCE_FILE, FRAGMENTS, H, MM, PKG, REGISTRY, POOL, TEMPLATE,
    SPEC_FILE, collect, specification,
)

START = '934ad8a97d9e9208cde27e7c87550ef57e1f560b'
CHECKPOINT = 'R2k6a-cataclysm-harbinger-admission-complete'
NOTE = OUT / 'cataclysm-r2k6a-harbinger-admission.json'
REVIEW = OUT / 'mod-reviews/cataclysm.json'
LEDGER = OUT / 'mod-completion-ledger.json'
KINDS = {'VANILLA_DIRECT', 'VANILLA_EQUIVALENT', 'VANILLA_LIKE_EXTENDED',
         'VANILLA_COMPOSITE', 'CUSTOM_DAMAGE', 'CUSTOM_STATUS',
         'CUSTOM_CONTROL', 'CUSTOM_RESOURCE', 'BINARY_MECHANIC'}
KEYS = {'incoming_admission', 'power_prerequisites', 'activation_state', 'mode_state',
        'shared_defense_bindings', 'nature_regen_binding', 'native_state_healing', 'encounter_state'}
ORDER = ['CAUSING_HARBINGER_CLASS_REJECT', 'IDLE_HEAD_COUNTERS_INCREMENT',
    'ARM_TERRAIN_TIMER', 'EMP_ANIMATION_RESPONSE', 'POWERED_DIRECT_ABSTRACT_ARROW_REJECT',
    'DEACTIVATION_PROGRESS_REJECT_UNLESS_INVULNERABILITY_BYPASS',
    'SHARED_HURT_SAME_SOURCE_AND_AMOUNT', 'RETURN_SHARED_HURT_RESULT']


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
        if e['id'] not in {'cataclysm:harbinger_nature_regen_binding', 'cataclysm:harbinger_native_state_healing'}:
            assert not candidates, 'Admission/setup constants are not new scalar candidates'
    new_paths = [p for p in paths if p['id'].startswith('cataclysm:harbinger-admission:')]
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
    assert summary == note['summary'] and summary['candidate_numeric_parameters'] == 3
    assert review['status'] == ledger['status'] == note['status'] == 'PARTIAL'
    for field in ['semantic_discovery_complete', 'special_damage_discovery_complete',
                  'source_mapping_complete', 'delivery_mapping_complete']:
        assert review[field] is False
    cat = next(t for t in ledger['targets'] if t['mod_key'] == 'cataclysm')
    assert cat['state'] == 'PARTIAL' and cat['semantic_effect_count'] == len(effects)
    assert review['checkpoint'] == ledger['checkpoint'] == note['checkpoint'] == CHECKPOINT
    assert review['exact_next_task'] == note['exact_next_task'] == cat['exact_next_task']
    assert note['exact_next_task'].startswith('R2k6b: The Harbinger offense/payload family.')
    assert note['remaining_harbinger_work'] and not note['remaining_subsection_native_ambiguities']
    assert note['whole_mod_complete'] is False and note['runtime_tests'] == 0
    assert all(note[k] is False for k in ['stage_eligibility_decided', 'phase6_reopened',
        'production_changed', 'stage_changed', 'boss_testing_started', 'l2_testing_started',
        'compatibility_fixes_started', 'phase7_started'])
    validate_contracts({e['id'].removeprefix('cataclysm:harbinger_'): e for e in new}, note)
    return summary


def validate_contracts(rows, note):
    def values(key, primitive):
        return next(c['numerical_parameters'] for c in rows[key]['components'] if c['primitive'] == primitive)

    assert note['admission_order']['concrete'] == rows['incoming_admission']['admission_order'] == ORDER
    incoming = rows['incoming_admission']
    assert all(incoming[k] is False for k in ['invulnerability_bypass_skips_all_prefilters',
        'prewrites_require_hurt_true', 'emp_requires_hurt_true', 'local_server_guard', 'request_multiplier_added'])
    assert incoming['shared_return_forwarded'] is True
    assert incoming['source_actor_distinctions'] == dict(first_rejection='getEntity()',
        powered_arrow='getDirectEntity()', shared_range='current getEntity() causing actor', source_rewritten=False)
    assert values('incoming_admission', 'INCOMING_STATE_PREWRITE') == {'head_counter_increment': 3, 'terrain_timer_ticks': 20}
    assert values('incoming_admission', 'EMP_ANIMATION_ADMISSION') == {'stun_animation_ticks': 105}
    power = rows['power_prerequisites']
    assert power['derived_not_latched'] is True and power['power_saved'] is False and power['power_setter_present'] is False
    assert values('power_prerequisites', 'POWER_PREREQUISITE') == {'health_divisor': 2.0}
    activation = rows['activation_state']
    assert all(activation[k] is False for k in ['setter_writes_progress', 'setter_writes_health',
        'setter_writes_home', 'progress_local_server_guard'])
    assert activation['awaken_goal_priority'] == 0
    assert values('activation_state', 'ACTIVATION_STATE') == {'inactive_progress': 40.0, 'activation_step': 1.0}
    assert values('activation_state', 'FORCED_MOVEMENT') == {'horizontal_write': 0.0}
    mode = rows['mode_state']
    assert mode['setters_clamp'] is False and mode['payload_semantics_deferred'] is True
    assert mode['mode_cycle_requires_target'] is False and mode['mode_cycle_requires_powered'] is False
    assert values('mode_state', 'MODE_STATE') == dict(toggle_threshold_ticks=300, reset_random_bound=50,
        transition_progress_max=30.0, transition_step=1.0)
    cfg = read_json(OUT / 'cataclysm-installed-common-config.json')['values']['mobs']['harbinger']
    expected = {'DamageCap': ('damageCap', cfg['cap_config']['damage_cap']),
                'DpsCap': ('dpsCap', cfg['cap_config']['dps_cap']),
                'RangeLimit': ('rangeCap', cfg['cap_config']['range_cap']),
                'NatureRegen': ('natureHeal', cfg['nature_heal_config']['nature_heal'])}
    for name, (field, value) in expected.items():
        assert note['concrete_bindings'][name]['config_field'] == 'Harbinger.' + field
        assert note['concrete_bindings'][name]['installed_value'] == value
        assert note['concrete_bindings'][name]['shared_boundary']
    assert note['concrete_bindings']['HealCooldown']['native_value'] == 200
    defense = rows['shared_defense_bindings']
    assert defense['has_concrete_invulnerability_override'] is False
    assert defense['registered_fire_immune'] is True
    assert defense['registered_immune_blocks'] == ['minecraft:wither_rose']
    assert values('shared_defense_bindings', 'DAMAGE_CAP') == {'per_hit_cap': 22.0}
    assert values('shared_defense_bindings', 'DPS_BUCKET') == {
        'capacity': 22.0, 'dps_cap': 14.0, 'drain_divisor': 20, 'full_bucket_request': 0.10000000149011612}
    assert values('shared_defense_bindings', 'RANGE_ADMISSION') == {'range_limit': 35.0}
    regen = rows['nature_regen_binding']
    assert regen['record_kind'] == 'SHARED_BINDING' and regen['binding_of'] == 'cataclysm:shared_heal'
    assert regen['reads_activation'] is False
    assert regen['scalable_parameter_candidates'][0]['primitive'] == 'NATIVE_HEAL'
    assert values('nature_regen_binding', 'NATIVE_HEAL') == {'amount': 25.0}
    stateheal = rows['native_state_healing']
    assert stateheal['health_multiplier_installed'] == cfg['combat_config']['health_multiplier'] == 1.0
    assert all(stateheal[k] is False for k in ['requires_targetless', 'reads_shared_regen_timer', 'requires_hurt_success'])
    assert [c['numerical_parameters'] for c in stateheal['components']] == [
        {'active_amount': cfg['harbinger_auto_heal']}, {'dormant_base_amount': 50.0}]
    encounter = rows['encounter_state']
    persist = encounter['persistence']
    assert persist == note['facts']['persistence']
    assert persist['saved_keys'] == ['Is_Act'] and persist['load_order'] == ['SUPER', 'Is_Act']
    assert persist['missing_is_act_loads'] is False and persist['progress_reconstructed_by_ai_step'] is True
    assert {'LASER_MODE', 'ISCHARGE', 'OVERLOAD', 'deactivateProgress', 'damageBucket', 'homeTicks'} <= set(persist['not_saved_here'])
    assert encounter['synced_defaults'] == dict(IS_ACT=True, LASER_MODE=False, ISCHARGE=False,
        OVERLOAD=0, FIRST_HEAD_TARGET=0, SECOND_HEAD_TARGET=0, THIRD_HEAD_TARGET=0)
    gates = encounter['encounter']
    assert gates == note['facts']['encounter']
    assert gates['item'] == 'minecraft:nether_star' and gates['requires_inactive'] is True
    assert all(gates[k] is False for k in ['requires_hurt_success', 'local_server_guard', 'local_alive_guard',
        'local_no_ai_guard', 'local_difficulty_guard', 'consumption_requires_heal_success',
        'directly_clears_progress', 'template_home_present', 'concrete_finalize_spawn_override'])
    assert gates['creative_exempt'] is True and gates['consumption_before_activation'] is True
    assert gates['default_constructed_is_act'] is True and gates['template_is_act'] == 0
    assert gates['template_health'] == 390.0 and gates['template_entry'] == TEMPLATE
    assert gates['activation_order'] == ['SHRINK_ONE_UNLESS_CREATIVE', 'SET_IS_ACT_TRUE',
        'SET_HOME_CURRENT_DIMENSION_AND_BLOCKPOS', 'HEAL_MAX_HEALTH', 'RETURN_SUCCESS']


def validate_preservation(review, note, ledger):
    assert note['starting_sha'] == START
    old = json.loads(at_start(REVIEW))
    assert [e for e in review['effects'] if e['review_checkpoint'] != CHECKPOINT] == old['effects']
    assert [p for p in review['paths'] if not p['id'].startswith('cataclysm:harbinger-admission:')] == old['paths']
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
        if w['entry'].endswith('.class'):
            assert w['entry_sha256'] == census[w['entry']]
        if w['entry'] in [PKG + n + '.class' for n in [H, BASE, MM, AM]]:
            assert not {'isInvulnerableTo', 'hurtCurrentlyUsedShield', 'blockUsingShield'} & set(w['declared_method_names'])
        for m in w.get('methods', []):
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
    def body(name, method):
        w = next(w for w in evidence['witnesses'] if w['entry'] == PKG + name + '.class')
        return next(m['instructions'] for m in w['methods'] if m['name'] == method)

    def calls(ins, name):
        return [i['offset'] for i in ins if name in str(i.get('operand', ''))]

    def item(ins, offset):
        return next(i for i in ins if i['offset'] == offset)

    hurt = body(H, 'hurt')
    assert calls(hurt, '.getEntity(') == [1] and calls(hurt, '.getDirectEntity(') == [105]
    assert item(hurt, 6)['opcode'] == '0xc1' and item(hurt, 6)['operand'] == PKG + H
    assert item(hurt, 13)['opcode'] == item(hurt, 119)['opcode'] == item(hurt, 140)['opcode'] == '0xac'
    assert item(hurt, 35)['operand'] == 3 and item(hurt, 52)['operand'] == 20
    assert calls(hurt, 'CMDamageTypes.EMP') == [78]
    assert calls(hurt, '.sendAnimationMessage(') == [94]
    assert calls(hurt, '.isPowered(') == [98]
    assert item(hurt, 112)['operand'] == 'net/minecraft/world/entity/projectile/AbstractArrow'
    assert calls(hurt, 'BYPASSES_INVULNERABILITY') == [130]
    assert calls(hurt, 'LLibrary_Boss_Monster.hurt(') == [144] and item(hurt, 147)['opcode'] == '0xac'
    assert not calls(hurt, '.setIsAct(') and not calls(hurt, '.heal(')
    power = body(H, 'isPowered')
    assert calls(power, '.getHealth(') == [1] and calls(power, '.getMaxHealth(') == [5]
    assert item(power, 8)['operand'] == 2.0 and item(power, 10)['opcode'] == '0x96'
    for name, field in [('DamageCap', 'damageCap'), ('DpsCap', 'dpsCap'),
                        ('RangeLimit', 'rangeCap'), ('NatureRegen', 'natureHeal')]:
        assert calls(body(H, name), 'CMCommonConfig$Harbinger.' + field) == [0]
    saved, loaded = body(H, 'addAdditionalSaveData'), body(H, 'readAdditionalSaveData')
    assert calls(saved, '.putBoolean(') == [13] and calls(loaded, '.setIsAct(') == [13]
    assert not calls(loaded, '.setIsLaserMode(') and not calls(loaded, '.setOverload(')
    setter = body(H, 'setIsAct')
    assert not calls(setter, 'deactivateProgress') and not calls(setter, '.setHealth(') and not calls(setter, '.setHomePos(')
    ai = body(H, 'aiStep')
    assert item(ai, 118)['operand'] == 40.0 and item(ai, 145)['operand'] == 1.0
    assert not calls(ai, 'isClientSide')
    server = body(H, 'customServerAiStep')
    assert calls(server, '.getIsAct(') == [1]
    assert calls(server, '.setIsLaserMode(') == [420]
    assert calls(server, '.heal(') == [498, 523]
    assert calls(server, '.performRangedAttack(') == []
    assert not calls(server, 'self_regen') and not calls(server, '.isPowered(')
    interaction = body(H, 'mobInteract')
    assert calls(interaction, 'Items.NETHER_STAR') == [14]
    assert calls(interaction, '.shrink(') == [36]
    assert calls(interaction, '.setIsAct(') == [41]
    assert calls(interaction, '.setHomePos(') == [59] and calls(interaction, '.heal(') == [67]
    assert not calls(interaction, 'deactivateProgress') and not calls(interaction, 'isClientSide')
    assert not calls(interaction, '.isAlive(') and not calls(interaction, '.isNoAi(')
    pool = next(w['json'] for w in evidence['witnesses'] if w['entry'] == POOL)
    assert pool['elements'][0]['element']['location'] == 'cataclysm:the_harbinger'
    template = next(w for w in evidence['witnesses'] if w['entry'] == TEMPLATE)
    assert len(template['entities']) == 1
    entity = template['entities'][0]
    assert entity['id'] == 'cataclysm:the_harbinger' and entity['Is_Act'] == 0 and entity['Health'] == 390.0
    assert not {'Home', 'HomePos', 'HomePoint', 'HomeDimension'} & set(entity)
    registered = body(REGISTRY, 'lambda$static$24')
    assert calls(registered, '.fireImmune(') == [20] and calls(registered, '.immuneTo(') == [33]
    assert calls(registered, 'Blocks.WITHER_ROSE') == [29]
    harbinger = next(w for w in evidence['witnesses'] if w['entry'] == PKG + H + '.class')
    assert not {'tick', 'finalizeSpawn', 'isInvulnerableTo', 'setPowered', 'setBossPhase'} & set(harbinger['declared_method_names'])
    registry = next(w for w in evidence['witnesses'] if w['entry'] == PKG + REGISTRY + '.class')
    assert [b['index'] for b in registry['registration_bootstraps']] == [89, 138]
    assert any(PKG + H + '.<init>' in str(b['arguments']) for b in registry['registration_bootstraps'])


def validate(jar_path=None):
    review, note, ledger = [read_json(p) for p in [REVIEW, NOTE, LEDGER]]
    summary = validate_records(review, note, ledger)
    validate_preservation(review, note, ledger)
    methods = validate_evidence(review, note, jar_path)
    return dict(status='PASS', **summary, new_method_witnesses=methods,
        protected_shared_status_guardian_monstrosity_ignis='BYTE_IDENTICAL', prior_records_and_paths='UNCHANGED',
        pinned_jar='REPRODUCED' if jar_path is not None else 'ARCHIVED_WITNESSES_VALIDATED')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jar', type=Path, help='Optional exact pinned Cataclysm 3.27 JAR')
    print(json.dumps(validate(parser.parse_args().jar), indent=2))
