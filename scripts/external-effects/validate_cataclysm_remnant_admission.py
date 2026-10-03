"""Focused read-only R2k7a validation and optional pinned-JAR reproduction."""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import subprocess

from catalog_common import OUT, ROOT, read_json
from collect_cataclysm_remnant_admission import (
    AM, BASE, EVIDENCE_FILE, FRAGMENTS, IA, PKG, PIECE, R, REGISTRY,
    SPEC_FILE, collect, specification,
)

START = '3f28a7f93270bdb0ccfee3c63ffb881be2f74121'
CHECKPOINT = 'R2k7a-cataclysm-remnant-admission-complete'
NOTE = OUT / 'cataclysm-r2k7a-remnant-admission.json'
REVIEW = OUT / 'mod-reviews/cataclysm.json'
LEDGER = OUT / 'mod-completion-ledger.json'
KINDS = {'VANILLA_DIRECT', 'VANILLA_EQUIVALENT', 'VANILLA_LIKE_EXTENDED',
         'VANILLA_COMPOSITE', 'CUSTOM_DAMAGE', 'CUSTOM_STATUS',
         'CUSTOM_CONTROL', 'CUSTOM_RESOURCE', 'BINARY_MECHANIC'}
KEYS = {'incoming_admission', 'shared_defense_bindings', 'nature_regen_binding',
        'activation_state', 'phase_prerequisites', 'powered_regeneration',
        'combat_persistence', 'encounter_prerequisites'}
ORDER = ['PHASE7_UNLESS_INVULNERABILITY_BYPASS', 'DIRECT_ARROW_UNLESS_STATE12',
         'SLEEP_UNLESS_INVULNERABILITY_BYPASS', 'SHARED_HURT_SAME_SOURCE_AND_AMOUNT',
         'RETURN_SHARED_HURT_RESULT']


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
    assert {e['id'] for e in new} == {'cataclysm:remnant_' + k for k in KEYS}
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
        if e['id'] not in {'cataclysm:remnant_nature_regen_binding', 'cataclysm:remnant_powered_regeneration'}:
            assert not candidates, 'Admission/setup constants are not new scalar candidates'
    new_paths = [p for p in paths if p['id'].startswith('cataclysm:remnant-admission:')]
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
    assert summary == note['summary'] and summary['candidate_numeric_parameters'] == 2
    assert review['status'] == ledger['status'] == note['status'] == 'PARTIAL'
    for field in ['semantic_discovery_complete', 'special_damage_discovery_complete',
                  'source_mapping_complete', 'delivery_mapping_complete']:
        assert review[field] is False
    cat = next(t for t in ledger['targets'] if t['mod_key'] == 'cataclysm')
    assert cat['state'] == 'PARTIAL' and cat['semantic_effect_count'] == len(effects)
    assert review['checkpoint'] == ledger['checkpoint'] == note['checkpoint'] == CHECKPOINT
    assert review['exact_next_task'] == note['exact_next_task'] == cat['exact_next_task']
    assert note['exact_next_task'].startswith('R2k7b: Ancient Remnant offense/payload family.')
    assert note['remaining_remnant_work'] and not note['remaining_subsection_native_ambiguities']
    assert note['whole_mod_complete'] is False and note['runtime_tests'] == 0
    assert all(note[k] is False for k in ['stage_eligibility_decided', 'phase6_reopened',
        'production_changed', 'stage_changed', 'boss_testing_started', 'l2_testing_started',
        'compatibility_fixes_started', 'phase7_started'])
    validate_contracts({e['id'].removeprefix('cataclysm:remnant_'): e for e in new}, note)
    return summary


def validate_contracts(rows, note):
    def values(key, primitive):
        return next(c['numerical_parameters'] for c in rows[key]['components'] if c['primitive'] == primitive)

    assert note['admission_order']['concrete'] == rows['incoming_admission']['admission_order'] == ORDER
    incoming = rows['incoming_admission']
    assert all(incoming[k] is False for k in ['direct_arrow_bypass_exemption', 'post_hurt_state_write',
        'incoming_amount_rewritten', 'concrete_is_invulnerable_override'])
    assert values('incoming_admission', 'NATIVE_DAMAGE_ADMISSION') == dict(phase_state=7, arrow_exception_state=12)
    cfg = read_json(OUT / 'cataclysm-installed-common-config.json')['values']['mobs']['ancient_remnant']
    expected = {'DamageCap': ('damageCap', cfg['cap_config']['damage_cap']),
                'DpsCap': ('dpsCap', cfg['cap_config']['dps_cap']),
                'RangeLimit': ('rangeCap', cfg['cap_config']['range_cap']),
                'NatureRegen': ('natureHeal', cfg['nature_heal_config']['nature_heal'])}
    for name, (field, value) in expected.items():
        assert note['concrete_bindings'][name]['config_field'] == 'AncientRemnant.' + field
        assert note['concrete_bindings'][name]['installed_value'] == value
        assert note['concrete_bindings'][name]['shared_boundary']
    assert note['concrete_bindings']['HealCooldown']['native_value'] == 200
    defense = rows['shared_defense_bindings']
    assert defense['installed_config_values'] == dict(damage_cap=21.0, dps_cap=14.0, range_limit=14.0, heal_cooldown=200)
    assert defense['damage_cap_is_bucket_capacity'] is True and defense['dps_is_bucket_capacity'] is False
    assert defense['range_narrows_float_before_double'] is True
    assert defense['dps_limit_time_read_by_bindings'] is False
    assert defense['registered_fire_immune'] is True and defense['registered_immune_blocks'] == []
    assert values('shared_defense_bindings', 'DAMAGE_CAP') == dict(per_hit_cap=21.0)
    assert values('shared_defense_bindings', 'DPS_BUCKET') == dict(capacity=21.0, dps_cap=14.0, drain_divisor=20)
    assert values('shared_defense_bindings', 'RANGE_ADMISSION') == dict(range_limit=14.0)
    assert values('shared_defense_bindings', 'REGEN_ADMISSION_TIMER') == dict(heal_cooldown=200)
    regen = rows['nature_regen_binding']
    assert regen['record_kind'] == 'SHARED_BINDING' and regen['binding_of'] == 'cataclysm:shared_heal'
    assert values('nature_regen_binding', 'NATIVE_HEAL') == dict(amount=25.0)
    activation = rows['activation_state']
    assert activation['default_necklace'] is True
    assert activation['sleep_states'] == [1, 2] and activation['wake_goal_arguments'] == [2, 2, 0, 80, 0]
    assert all(activation[k] is False for k in ['necklace_setter_changes_attack_state', 'necklace_setter_heals',
        'awakening_goal_has_velocity_write'])
    assert values('activation_state', 'ACTIVATION_STATE') == dict(sleep_state=1, awaken_state=2, awaken_max_ticks=80)
    assert values('activation_state', 'FORCED_MOVEMENT') == dict(horizontal_write=0.0)
    phase = rows['phase_prerequisites']
    assert phase['stored_power_is_saved'] is True and phase['live_power_is_saved'] is False
    assert all(phase[k] is False for k in ['power_setter_rewrites_health', 'phase_can_use_requires_target',
        'phase_can_use_requires_necklace', 'phase_can_use_requires_random', 'power_latch_local_server_guard'])
    assert phase['phase_goal_arguments'] == [0, 7, 0, 60, 13] and phase['power_latch_tick'] == 14
    assert values('phase_prerequisites', 'PHASE_STATE') == dict(health_divisor=2.0, phase_state=7,
        phase_max_ticks=60, phase_see_tick=13, power_latch_tick=14)
    assert all(rows['powered_regeneration'][k] is False for k in ['local_server_guard', 'reads_live_hp_predicate',
        'reads_self_regen', 'reads_target', 'reads_no_ai', 'reads_necklace'])
    assert values('powered_regeneration', 'NATIVE_HEAL') == dict(amount=1.0, cadence_ticks=20)
    persistence = rows['combat_persistence']
    assert persistence['saved_concrete_keys'] == ['has_necklace', 'Rage', 'Power']
    assert persistence['missing_key_defaults'] == dict(has_necklace=False, Rage=0, Power=False)
    assert all(persistence[k] is False for k in ['crash_saved', 'attack_state_saved', 'rage_setter_clamps', 'generic_persistence_added'])
    encounter = rows['encounter_prerequisites']
    assert all(encounter[k] is False for k in ['marker_sets_home', 'marker_sets_attack_state', 'marker_necklace',
        'interaction_local_server_guard', 'interaction_heals', 'configured_health_is_heal_delivery'])
    assert encounter['marker_persistence_required'] is True
    assert encounter['interaction_order'] == ['EXACT_ITEM_AND_NO_NECKLACE', 'CONSUME_UNLESS_CREATIVE',
        'SET_CURRENT_HOME', 'SET_NECKLACE_TRUE', 'SET_ATTACK_STATE2', 'SUCCESS']
    assert encounter['attribute_builder_method'] == 'maledictus'
    assert encounter['attributes_apply_to'] == 'cataclysm:ancient_remnant'
    assert encounter['registered_dimensions'] == dict(width=4.349999904632568, height=5.0)
    assert values('encounter_prerequisites', 'NATIVE_ATTRIBUTE_SETUP') == dict(base_health=450.0,
        base_attack_damage=25.0, armor=12.0, armor_toughness=4.0, health_multiplier=1.0, attack_multiplier=1.0)
    assert values('encounter_prerequisites', 'ENCOUNTER_GATE') == dict(item_count=1, awaken_state=2, inherited_home_cooldown=400)


def validate_preservation(review, note, ledger):
    assert note['starting_sha'] == START
    old = json.loads(at_start(REVIEW))
    assert [e for e in review['effects'] if e['review_checkpoint'] != CHECKPOINT] == old['effects']
    assert [p for p in review['paths'] if not p['id'].startswith('cataclysm:remnant-admission:')] == old['paths']
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
    assert len(evidence['witnesses']) == note['tooling']['new_native_witnesses'] == 9
    assert [w['entry'] for w in evidence['witnesses']] == [s['entry'] for s in specification()['evidence_specifications']]
    if jar_path is not None:
        assert evidence == collect(jar_path), 'Pinned-JAR witnesses did not reproduce'
    census = {c['entry']: c['entry_sha256'] for c in read_json(OUT / 'cataclysm-source-census.json')['classes']}
    sources = {r['file']: read_json(OUT / r['file']) for r in note['reference_files']
               if r['file'].startswith('native-evidence/')}
    methods = {(w['entry'], m['name'], m['descriptor']): m
               for w in evidence['witnesses'] for m in w.get('methods', [])}
    assert len(methods) == note['tooling']['new_method_witnesses'] == 38
    for file, data in sources.items():
        if file == EVIDENCE_FILE.relative_to(OUT).as_posix():
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
        assert w['jar_sha256'] == note['tooling']['jar_sha256'] and w['entry_sha256'] == census[w['entry']]
        if w['entry'] in [PKG + n + '.class' for n in [R, BASE, IA, AM]]:
            assert 'isInvulnerableTo' not in w['declared_method_names']
        if w['entry'] in [PKG + n + '.class' for n in [BASE, IA, AM]]:
            assert not w['methods'], 'Locked parent bodies must be reused'
        for m in w.get('methods', []):
            if 'instruction_offset_ranges' in m:
                assert m['instruction_offset_ranges'] == FRAGMENTS[w['entry'][len(PKG):-6]][m['name']]
    for e in selected(review):
        for p in e['implementation']:
            w = next(w for w in sources[p['evidence_file']]['witnesses'] if w['id'] == p['witness_id'])
            assert p['entry'] == w['entry']
            assert set(p['methods']) <= {m['name'] for m in w.get('methods', [])}
    registry = next(w for w in sources['native-evidence/cataclysm-guardian-admission.json']['witnesses']
                    if w['entry'] == PKG + REGISTRY + '.class')
    attributes = next(m['instructions'] for m in registry['methods'] if m['name'] == 'initializeAttributes')
    assert any(i['offset'] == 533 and 'ModEntities.ANCIENT_REMNANT' in str(i['operand']) for i in attributes)
    assert any(i['offset'] == 542 and 'Ancient_Remnant_Entity.maledictus(' in str(i['operand']) for i in attributes)
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

    hurt = body(R, 'hurt')
    assert calls(hurt, '.getDirectEntity(') == [22] and not calls(hurt, '.getEntity(')
    assert item(hurt, 4)['operand'] == 7 and item(hurt, 30)['operand'] == 12
    assert item(hurt, 36)['opcode'] == '0xc1' and item(hurt, 36)['operand'] == 'net/minecraft/world/entity/projectile/AbstractArrow'
    assert calls(hurt, 'BYPASSES_INVULNERABILITY') == [10, 52] and calls(hurt, '.isSleep(') == [45]
    assert calls(hurt, 'IABoss_monster.hurt(') == [66] and item(hurt, 69)['opcode'] == '0xac'
    assert [item(hurt, i)['opcode'] for i in [63, 64, 65]] == ['0x2a', '0x2b', '0x24']
    assert not calls(hurt, '.setAttackState(') and not calls(hurt, '.setNecklace(') and not calls(hurt, '.heal(')
    power = body(R, 'isPower')
    assert calls(power, '.getHealth(') == [1] and calls(power, '.getMaxHealth(') == [5]
    assert item(power, 8)['operand'] == 2.0 and item(power, 11)['opcode'] == '0x9d'
    assert not calls(power, '.getIsPower(')
    for name, field in [('DamageCap', 'damageCap'), ('DpsCap', 'dpsCap'),
                        ('RangeLimit', 'rangeCap'), ('NatureRegen', 'natureHeal')]:
        assert calls(body(R, name), 'CMCommonConfig$AncientRemnant.' + field) == [0]
    assert [i['opcode'] for i in body(R, 'RangeLimit')] == ['0xb2', '0x90', '0x8d', '0xaf']
    defaults = body(R, 'defineSynchedData')
    assert [item(defaults, i)['operand'] for i in [9, 21, 33, 45]] == [0, 1, 0, 0]
    necklace = body(R, 'setNecklace')
    assert len(calls(necklace, '.setVisible(')) == 2
    assert not calls(necklace, '.setAttackState(') and not calls(necklace, '.heal(')
    for setter in ['setIsPower', 'setCrash', 'setRage']:
        ins = body(R, setter)
        assert len(calls(ins, 'SynchedEntityData.set(')) == 1
        assert not calls(ins, '.setHealth(') and not calls(ins, '.clamp(')
    saved, loaded = body(R, 'addAdditionalSaveData'), body(R, 'readAdditionalSaveData')
    for ins in [saved, loaded]:
        assert [i['operand'] for i in ins if i['opcode'] in ['0x12', '0x13'] and isinstance(i['operand'], str)] == ['has_necklace', 'Rage', 'Power']
        assert not calls(ins, '.getCrash(') and not calls(ins, '.setCrash(') and not calls(ins, '.setAttackState(')
    assert not calls(loaded, '.contains(')
    assert calls(loaded, '.setNecklace(') == [13] and calls(loaded, '.setRage(') == [42] and calls(loaded, '.setIsPower(') == [53]
    sleep = body(R, 'isSleep')
    assert item(sleep, 4)['operand'] == 1 and item(sleep, 12)['operand'] == 2
    assert calls(sleep, '.getNecklace(') == [17]
    tick = body(R, 'tick')
    assert calls(tick, 'IABoss_monster.tick(') == [1] and calls(tick, '.getIsPower(') == [237]
    assert item(tick, 247)['operand'] == 20 and item(tick, 254)['operand'] == 1.0
    assert calls(tick, '.heal(') == [255]
    for absent in ['isClientSide', '.isNoAi(', '.isSleep(', '.getTarget(', '.isPower(', 'self_regen']:
        assert not calls(tick, absent)
    phase = body(R, 'aiStep')
    assert item(phase, 498)['operand'] == 7 and item(phase, 507)['operand'] == 14
    assert item(phase, 561)['operand'] == 1 and calls(phase, '.setIsPower(') == [562]
    assert not calls(phase, 'isClientSide')
    for excluded in ['.AreaAttack(', '.TailAreaAttack(', '.Charge(', '.EarthQuakeSummon(', 'Sandstorm_Entity']:
        assert not calls(phase, excluded), 'Offense is outside this batch'
    goal = body(R+'$RemnantPhaseChangeGoal', 'canUse')
    assert len(calls(goal, '.getIsPower(')) == len(calls(goal, '.getAttackState(')) == len(calls(goal, '.isPower(')) == 1
    for absent in ['.getTarget(', '.getNecklace(', '.nextFloat(', '.nextInt(']:
        assert not calls(goal, absent)
    interaction = body(R, 'mobInteract')
    assert calls(interaction, 'ModItems.NECKLACE_OF_THE_DESERT') == [14]
    assert calls(interaction, '.shrink(') == [39] and item(interaction, 38)['operand'] == 1
    assert calls(interaction, '.setHomePos(') == [57] and calls(interaction, '.setNecklace(') == [62]
    assert calls(interaction, '.setAttackState(') == [67] and item(interaction, 66)['operand'] == 2
    assert not calls(interaction, 'isClientSide') and not calls(interaction, '.heal(')
    marker = body(PIECE, 'handleDataMarker')
    assert item(marker, 150)['operand'] == 'remnant'
    assert calls(marker, '.setNecklace(') == [587] and item(marker, 586)['operand'] == 0
    assert calls(marker, '.setPersistenceRequired(') == [592]
    assert calls(marker, '.finalizeSpawn(') == [624] and calls(marker, 'MobSpawnType.STRUCTURE') == [617]
    assert calls(marker, '.addFreshEntityWithPassengers(') == [631]
    assert not calls(marker, '.setHomePos(') and not calls(marker, '.setAttackState(')
    finalize = body(R, 'finalizeSpawn')
    assert calls(finalize, 'IABoss_monster.finalizeSpawn(') and not calls(finalize, '.setHomePos(')
    registered = body(REGISTRY, 'lambda$static$78')
    assert calls(registered, '.fireImmune(') == [20] and not calls(registered, '.immuneTo(')
    assert item(registered, 11)['operand'] == 4.349999904632568 and item(registered, 14)['operand'] == 5.0
    registry = next(w for w in evidence['witnesses'] if w['entry'] == PKG + REGISTRY + '.class')
    assert [b['index'] for b in registry['registration_bootstraps']] == [35, 192]
    assert any(PKG + R + '.<init>' in str(b['arguments']) for b in registry['registration_bootstraps'])


def validate(jar_path=None):
    review, note, ledger = [read_json(p) for p in [REVIEW, NOTE, LEDGER]]
    summary = validate_records(review, note, ledger)
    validate_preservation(review, note, ledger)
    methods = validate_evidence(review, note, jar_path)
    return dict(status='PASS', **summary, new_method_witnesses=methods,
        protected_shared_status_guardian_monstrosity_ignis_harbinger='BYTE_IDENTICAL',
        prior_records_and_paths='UNCHANGED',
        pinned_jar='REPRODUCED' if jar_path is not None else 'ARCHIVED_WITNESSES_VALIDATED')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jar', type=Path, help='Optional exact pinned Cataclysm 3.27 JAR')
    print(json.dumps(validate(parser.parse_args().jar), indent=2))
