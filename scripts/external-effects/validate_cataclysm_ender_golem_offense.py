"""Focused R2k11b records, protected evidence and pinned-JAR validation."""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import subprocess

from catalog_common import OUT, ROOT, read_json
from collect_cataclysm_ender_golem_offense import (
    EVIDENCE_FILE, FRAGMENTS, G, METHODS, PKG, PURSUIT, SPEC_FILE, TERRAIN,
    collect, specification,
)

START = '22fed877e803aba06ba23f609fde258584cb5026'
CHECKPOINT = 'R2k11b-cataclysm-ender-golem-offense-complete'
NOTE = OUT / 'cataclysm-r2k11b-ender-golem-offense.json'
REVIEW = OUT / 'mod-reviews/cataclysm.json'
LEDGER = OUT / 'mod-completion-ledger.json'
KEYS = {'alliance', 'pursuit_goal', 'attack_selection', 'sequence_state',
        'attack_control', 'dormant_control', 'melee_damage', 'melee_knockback',
        'quake_damage', 'quake_launch', 'rune_delivery', 'rune_damage',
        'rune_lifecycle', 'terrain_response', 'body_repulsion', 'defeat_lifecycle'}
KINDS = {'VANILLA_DIRECT', 'VANILLA_EQUIVALENT', 'VANILLA_LIKE_EXTENDED',
         'VANILLA_COMPOSITE', 'CUSTOM_DAMAGE', 'CUSTOM_STATUS', 'CUSTOM_CONTROL',
         'CUSTOM_RESOURCE', 'BINARY_MECHANIC'}


def at_start(path):
    return subprocess.check_output(['git', 'show', START + ':' +
        Path(path).relative_to(ROOT).as_posix()], cwd=ROOT)


def selected(review):
    return [e for e in review['effects'] if e['review_checkpoint'] == CHECKPOINT]


def observations(components):
    result = []
    for c in components:
        assert c['primitive'] and c['formula'] and c['native_boundary'] and c['vanilla_relation']
        assert set(c['numerical_parameters']) == set(c['parameter_units'])
        for p, v in c['numerical_parameters'].items():
            assert isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)
            result.append(dict(primitive=c['primitive'], parameter=p, native_value=v,
                native_formula=c['formula'], units=c['parameter_units'][p], boundary=c['native_boundary']))
        formulas = c.get('parameter_formulas', {})
        assert set(formulas) == set(c.get('formula_parameter_units', {}))
        assert not set(formulas) & set(c['numerical_parameters'])
        for p, f in formulas.items():
            assert f and c['formula_parameter_units'][p]
            result.append(dict(primitive=c['primitive'], parameter=p, native_value=None,
                native_formula=f, units=c['formula_parameter_units'][p], boundary=c['native_boundary']))
    return result


def validate_records(review, note, ledger):
    effects, paths = review['effects'], review['paths']
    assert len(effects) == len({e['id'] for e in effects})
    assert len(paths) == len({p['id'] for p in paths})
    assert effects == sorted(effects, key=lambda e: e['id'])
    assert paths == sorted(paths, key=lambda p: p['id'])
    new = selected(review)
    assert {e['id'] for e in new} == {'cataclysm:ender_golem_' + k for k in KEYS}
    pids, eids = {p['id'] for p in paths}, {e['id'] for e in effects}
    for e in new:
        assert e['mod_key'] == 'cataclysm' and e['primary_classification'] in KINDS
        assert e['inspection_status'] == 'STATIC_REVIEWED' and not e['unresolved_ambiguities']
        for key in ['actual_behavior', 'source_actor', 'primary_test_source', 'components',
                    'implementation', 'delivery_paths', 'closest_vanilla_equivalent', 'hurt_return_dependency']:
            assert e[key], (e['id'], key)
        assert not {'stage_scaling_needed', 'stage_policy', 'stage_multiplier', 'stage_eligibility',
                    'stage_cap', 'stage_floor', 'runtime_hook'} & e.keys()
        assert set(e['delivery_paths']) <= pids
        obs = observations(e['components'])
        assert obs == e['numeric_observations']
        candidates = e['scalable_parameter_candidates']
        assert candidates == sorted(candidates, key=lambda c: (c['primitive'], c['parameters']))
        seen = set()
        for c in candidates:
            assert len(c['parameters']) == 1
            p = c['parameters'][0]
            assert (c['primitive'], p) not in seen
            seen.add((c['primitive'], p))
            owners = [o for o in obs if o['primitive'] == c['primitive'] and o['parameter'] == p]
            assert len(owners) == 1, 'Candidate lost its native primitive'
            owner = owners[0]
            for k in ['native_value', 'native_formula', 'units']:
                assert c[k] == owner[k], (e['id'], p, k)
            assert c['native_boundary'] == owner['boundary']
        if e['primary_classification'] == 'BINARY_MECHANIC' or e['id'].endswith(('dormant_control', 'pursuit_goal')):
            assert not candidates, 'State/admission/setup constants are not automatic scalar candidates'
    new_paths = [p for p in paths if p['id'].startswith('cataclysm:ender-golem-offense:')]
    assert len(new_paths) == 16
    for p in new_paths:
        assert p['mod_key'] == 'cataclysm' and p['status'] == 'VERIFIED'
        assert p['primary_source'] and p['native_path'] and p['setup'] and p['implementation']
        assert p['labels'] and p['runtime_status'] == 'NOT_RUN'
        assert p['effect_ids'] and set(p['effect_ids']) <= eids
        for e in new:
            assert (p['id'] in e['delivery_paths']) == (e['id'] in p['effect_ids'])
    assert note['mechanic_packages'] == [dict(id=e['id'], primary_classification=e['primary_classification'],
        delivery_paths=e['delivery_paths'], numerical_candidates=e['scalable_parameter_candidates'],
        binary_gates=e['binary_parameters'], hurt_return_dependency=e['hurt_return_dependency']) for e in new]
    summary = dict(new_mechanics=len(new), delivery_paths=len(new_paths),
        classifications=dict(sorted(Counter(e['primary_classification'] for e in new).items())),
        candidate_numeric_parameters=sum(len(c['parameters']) for e in new for c in e['scalable_parameter_candidates']),
        unresolved_subsection_ambiguities=0)
    assert summary == note['summary']
    assert summary['classifications'] == {'BINARY_MECHANIC': 6, 'CUSTOM_CONTROL': 4,
        'VANILLA_DIRECT': 1, 'VANILLA_LIKE_EXTENDED': 5}
    assert summary['candidate_numeric_parameters'] == 27
    cat = next(t for t in ledger['targets'] if t['mod_key'] == 'cataclysm')
    assert review['status'] == ledger['status'] == note['status'] == cat['state'] == 'PARTIAL'
    assert cat['semantic_effect_count'] == len(effects)
    assert all(review[k] is False for k in ['semantic_discovery_complete',
        'special_damage_discovery_complete', 'source_mapping_complete', 'delivery_mapping_complete'])
    assert review['checkpoint'] == ledger['checkpoint'] == note['checkpoint'] == CHECKPOINT
    assert review['exact_next_task'] == note['exact_next_task'] == cat['exact_next_task']
    assert note['exact_next_task'].startswith('R2k12a: Ignited Revenant incoming admission and combat-state/encounter prerequisites.')
    assert note['ender_golem_fully_closed'] is True and not note['remaining_ender_golem_work']
    assert not note['remaining_subsection_native_ambiguities'] and note['remaining_cataclysm_research']
    assert note['runtime_tests'] == 0
    assert all(note[k] is False for k in ['whole_mod_complete', 'stage_eligibility_decided', 'phase6_reopened',
        'production_changed', 'stage_changed', 'boss_testing_started', 'l2_testing_started',
        'compatibility_fixes_started', 'phase7_started'])
    validate_contracts({e['id'].removeprefix('cataclysm:ender_golem_'): e for e in new})
    return summary


def validate_contracts(rows):
    flags = {
        'alliance': dict(quake_filters_other_golems=True, rune_bidirectional_alliance=True,
            melee_extra_alliance_filter=False, body_extra_alliance_filter=False),
        'pursuit_goal': dict(pursuit_calls_native_hurt=False, inherited_tick_called=False, long_memory=True),
        'attack_selection': dict(rune_ground_gate_applies_to_fallback=False,
            selection_local_server_guard=False, short_circuit_rng_preserved=True),
        'sequence_state': dict(cooldown_decrements_after_selection=True, selected_cooldown_end_of_tick=249,
            cooldown_decrement_has_no_ai_guard=False, cooldown_decrement_has_server_guard=False, new_persistent_state=False),
        'attack_control': dict(uses_native_knockback=False, preserves_vertical_velocity=True, control_depends_on_hurt=False),
        'dormant_control': dict(new_awake_state_transition=False, preserves_vertical_velocity=True, control_depends_on_hurt=False),
        'melee_damage': dict(hurt_return_used=False, post_hurt_status=False, invulnerability_reset=False,
            local_server_guard=False, local_team_guard=False),
        'melee_knockback': dict(control_depends_on_hurt=False, uses_native_knockback=True),
        'quake_damage': dict(hurt_return_used=False, launch_depends_on_hurt=False, uses_native_explosion=False,
            extra_radial_filter=False, quake_server_only=True),
        'quake_launch': dict(control_depends_on_hurt=False, uses_native_knockback=False,
            reads_knockback_resistance=False, active_huge_only=True),
        'rune_delivery': dict(spawn_attempts=34, guaranteed_spawn_count=False, ring_rotation_argument='lateralX f2',
            gaussian_rotation_argument='lateralZ f3', helper_local_server_guard=False, spawn_return_used=False, creates_evoker_fangs=False),
        'rune_damage': dict(hurt_return_used=False, stored_damage_at_creation=True, payload_evidence_reused=True,
            guardian_damage_binding_unchanged=True, anonymous_magic_fallback=True),
        'rune_lifecycle': dict(new_owned_payload_class=False, native_damage_saved=True,
            native_life_ticks_saved=False, new_persistent_state=False, new_callbacks=False),
        'terrain_response': dict(terrain_depends_on_hurt=False, creates_explosion=False,
            spawns_damaging_debris=False, block_tag_is_allowlist=True, air_test_is_reference=True),
        'body_repulsion': dict(control_depends_on_hurt=False, uses_native_knockback=False,
            preserves_vertical_velocity=True, local_team_guard=False, local_server_guard=False, shared_write_not_new_golem_field=True),
        'defeat_lifecycle': dict(concrete_death_payload=False, concrete_respawner_link=False,
            global_death_callbacks_absent_claimed=False, shared_death_contract_reused=True),
    }
    for key, fields in flags.items():
        for f, v in fields.items():
            assert rows[key][f] == v, (key, f)
    def params(key, primitive):
        return next(c['numerical_parameters'] for c in rows[key]['components'] if c['primitive'] == primitive)
    assert params('melee_knockback','KNOCKBACK') == dict(strength=1.25)
    assert params('melee_damage','ATTACK_REACH') == dict(distance=4.75)
    assert params('quake_launch','FORCED_MOVEMENT') == dict(horizontal_factor=2.0,
        vertical_increment=.5, native_denominator_minimum=.001)
    assert params('quake_damage','AREA_QUERY') == dict(quake_grow=5.0, rune_grow=4.25)
    assert params('rune_damage','NATIVE_DAMAGE_REQUEST') == dict(amount=7.0)
    assert params('sequence_state','COOLDOWN_STATE') == dict(rune_cooldown=250)
    assert params('rune_lifecycle','PAYLOAD_LIFECYCLE') == dict(initial_life_ticks=34,
        pulse_tick_modulo=5, active_warmup_first=-11, active_warmup_last=-29, query_grow=.2)
    assert params('defeat_lifecycle','DEATH_LIFECYCLE')['removal_timer'] == 75
    for key, bound in [('melee_damage', dict(random_bound=4)),
                       ('quake_damage', dict(quake_random_bound=6, rune_random_bound=4))]:
        c = next(c for c in rows[key]['components'] if c['primitive']=='NATIVE_DAMAGE_REQUEST')
        assert c['numerical_parameters'] == bound
        assert list(c['parameter_formulas']) == ['requested_damage']
        formula = c['parameter_formulas']['requested_damage']
        assert 'current configured ATTACK_DAMAGE' in formula and 'nextInt(' in formula
        assert 'coefficient' not in formula and 'multiplier' not in formula
        candidate = next(c for c in rows[key]['scalable_parameter_candidates'] if c['parameters']==['requested_damage'])
        assert candidate['native_value'] is None, 'Dynamic request cannot be invented as a fixed native value'


def validate_preservation(review, note, ledger):
    assert note['starting_sha'] == START
    old = json.loads(at_start(REVIEW))
    assert len(old['effects']) == 304 and len(old['paths']) == 310
    assert [e for e in review['effects'] if e['review_checkpoint'] != CHECKPOINT] == old['effects']
    assert [p for p in review['paths'] if not p['id'].startswith('cataclysm:ender-golem-offense:')] == old['paths']
    mutable = {'effects','paths','checkpoint','scope','notes_file','exact_next_task','protected_checkpoints'}
    assert {k:v for k,v in review.items() if k not in mutable} == {k:v for k,v in old.items() if k not in mutable}
    assert review['protected_checkpoints'] == old['protected_checkpoints'] + [dict(checkpoint=old['checkpoint'],notes_file=old['notes_file'])]
    for r in note['reference_files']:
        path = OUT / r['file']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == r['sha256'], r['file']
        if r['usage'] == 'LOCKED_REUSED':
            assert path.read_bytes() == at_start(path), r['file']
    lock = note['protected_r2k11a']
    assert lock['file'] == 'cataclysm-r2k11a-ender-golem-admission.json'
    assert hashlib.sha256((OUT/lock['file']).read_bytes()).hexdigest() == lock['sha256']
    prior = json.loads(at_start(LEDGER))
    assert [t for t in ledger['targets'] if t['mod_key']!='cataclysm'] == [t for t in prior['targets'] if t['mod_key']!='cataclysm']
    assert {k:v for k,v in ledger.items() if k not in ['targets','checkpoint']} == {k:v for k,v in prior.items() if k not in ['targets','checkpoint']}


def validate_native_boundaries(evidence):
    def body(n, m):
        w = next(w for w in evidence['witnesses'] if w['entry']==PKG+n+'.class')
        return next(mo['instructions'] for mo in w['methods'] if mo['name']==m)
    def calls(ins, name):
        return [i['offset'] for i in ins if name in str(i['operand'])]
    def at(ins, off):
        return next(i for i in ins if i['offset']==off)
    tick = body(G,'tick')
    assert calls(tick,'.hurt(')==[450] and at(tick,453)['opcode']=='0x57'
    assert calls(tick,'.knockback(')==[476]
    assert not any(i['opcode'] in {'0x99','0x9a'} for i in tick if 453<i['offset']<476)
    assert calls(tick,'.EarthQuake(')==[303,503] and calls(tick,'.VoidRuneAttack(')==[564]
    assert at(tick,220)['operand']==250 and calls(tick,'void_rune_attack_cooldownI')==[137,223,568,576,581]
    assert at(tick,161)['operand'].endswith('.onGround()Z')
    assert at(tick,173)['operand'].endswith('.nextInt(I)I') and at(tick,199)['operand'].endswith('.nextInt(I)I')
    assert calls(tick,'.getRandomAttack(')==[269]
    q = body(G,'EarthQuake')
    assert calls(q,'.mobAttack(')==[46] and calls(q,'.hurt(')==[144]
    assert at(q,147)['opcode']=='0x57' and at(q,151)['operand']==1
    assert calls(q,'.launch(')==[152]
    assert calls(q,'.isAlliedTo(')==[101] and at(q,109)['opcode']=='0xc1'
    assert calls(q,'isClientSide')==[35] and not calls(q,'.explode(')
    launch = body(G,'launch')
    assert at(launch,30)['operand']==.001 and at(launch,42)['operand']==2.0
    assert at(launch,46)['operand']==.5 and not calls(launch,'.knockback(')
    assert calls(launch,'.push(')==[82]
    # Boolean selects coefficients; both branches converge on this one native push.
    assert len([i for i in launch if '.push(' in str(i['operand'])])==1
    delivery = body(G,'VoidRuneAttack')
    assert calls(delivery,'.spawnFangs(')==[165,212,290,353]
    assert [at(delivery,o)['local_index'] for o in [161,208,287,349]]==[6,6,7,8]
    assert [at(delivery,o)['operand'] for o in [95,226,304]]==[10,6,8]
    assert not calls(delivery,'isClientSide') and not calls(delivery,'.isAlive(')
    spawn = body(G,'spawnFangs')
    assert calls(spawn,'EnderGolem.VoidRuneDamage')==[164] and at(spawn,167)['opcode']=='0x90'
    assert at(spawn,168)['opcode']=='0x2a' and 'Void_Rune_Entity.<init>' in at(spawn,169)['operand']
    assert not calls(spawn,'EvokerFangs') and not calls(spawn,'isClientSide')
    terrain = body(G,'BlockBreaking')
    assert at(terrain,114)['opcode']=='0xa5' and at(terrain,125)['branch_target']==180
    assert calls(terrain,'ENDER_GOLEM_CAN_DESTROY')==[119]
    assert calls(terrain,'.canEntityDestroy(')==[137] and calls(terrain,'.onEntityDestroyBlock(')==[148]
    assert calls(terrain,'.destroyBlock(')==[162] and not calls(terrain,'.hurt(')
    pursuit = body(PURSUIT,'tick')
    assert not calls(pursuit,'.hurt(') and not calls(pursuit,'.doHurtTarget(')
    assert not calls(pursuit,'MeleeAttackGoal.tick')
    for n in [G+'$AttackGoal',G+'$AwakenGoal']:
        control = body(n,'tick')
        assert at(control,4)['operand']==at(control,15)['operand']==0.0
        assert calls(control,'.setDeltaMovement(')==[16] and not calls(control,'.hurt(')
    death = body(G,'onDeathAIUpdate')
    assert calls(death,'.onDeathAIUpdate(')==[1] and calls(death,'.setDeltaMovement(')==[14]
    assert not calls(death,'.hurt(') and not calls(death,'.addFreshEntity(')
    tag = next(w for w in evidence['witnesses'] if w['entry']==TERRAIN)
    assert json.loads(tag['raw_text'])==dict(replace=False,values=[
        'minecraft:end_stone_brick_stairs','cataclysm:chiseled_obsidian_bricks',
        'cataclysm:obsidian_brick_slab','cataclysm:polished_end_stone_stairs','cataclysm:obsidian_brick_wall'])


def validate_evidence(review, note, jar_path=None):
    assert read_json(SPEC_FILE)==specification()
    evidence=read_json(EVIDENCE_FILE)
    assert {w['entry'] for w in evidence['witnesses']}=={PKG+n+'.class' for n in METHODS}|{TERRAIN}
    assert len(evidence['witnesses'])==5
    if jar_path is not None:
        reproduced=collect(jar_path)
        assert evidence==reproduced, 'New witnesses failed pinned-JAR reproduction'
        assert EVIDENCE_FILE.read_bytes()==(json.dumps(reproduced,ensure_ascii=False,indent=2)+'\n').encode()
    census={c['entry']:c for c in read_json(OUT/'cataclysm-source-census.json')['classes']}
    new_methods={(w['entry'],m['name'],m['descriptor']):m for w in evidence['witnesses'] for m in w.get('methods',[])}
    assert len(new_methods)==27
    sources={r['file']:read_json(OUT/r['file']) for r in note['reference_files'] if r['file'].startswith('native-evidence/')}
    for file,data in sources.items():
        if file==EVIDENCE_FILE.relative_to(OUT).as_posix():
            continue
        for w in data['witnesses']:
            for old in w.get('methods',[]):
                new=new_methods.get((w['entry'],old['name'],old['descriptor']))
                if new is not None:
                    assert 'instruction_offset_ranges' in new, 'Old method recaptured'
                    assert new['code_sha256']==old['code_sha256']
                    assert not {i['offset'] for i in new['instructions']} & {i['offset'] for i in old['instructions']}, 'Old fragment recaptured'
    for w in evidence['witnesses']:
        assert w['jar_sha256']==note['tooling']['jar_sha256']
        if w['entry']==TERRAIN:
            continue
        assert w['entry_sha256']==census[w['entry']]['entry_sha256']
        assert w['superclass']==census[w['entry']]['superclass']
        name=w['entry'][len(PKG):-6]
        assert {m['name'] for m in w['methods']}==set(METHODS[name])|set(FRAGMENTS.get(name,{}))
        for m in w['methods']:
            if 'instruction_offset_ranges' in m:
                assert m['instruction_offset_ranges']==FRAGMENTS[name][m['name']]
    for e in selected(review):
        for p in e['implementation']:
            w=next(w for w in sources[p['evidence_file']]['witnesses'] if w['id']==p['witness_id'])
            assert p['entry']==w['entry']
            assert set(p['methods'])<={m['name'] for m in w.get('methods',[])}
    assert note['tooling']['new_native_witnesses']==5 and note['tooling']['new_method_witnesses']==27
    assert note['tooling']['new_owned_payload_classes']==0
    assert not note['tooling']['reused_evidence_regenerated'] and not note['tooling']['recursive_jar_scan']
    assert note['next_family_header']['entry_sha256']==census[note['next_family_header']['entry']]['entry_sha256']
    validate_native_boundaries(evidence)
    return len(new_methods)


def validate(jar_path=None):
    review,note,ledger=[read_json(p) for p in [REVIEW,NOTE,LEDGER]]
    summary=validate_records(review,note,ledger)
    validate_preservation(review,note,ledger)
    methods=validate_evidence(review,note,jar_path)
    for path in [REVIEW,NOTE,LEDGER,SPEC_FILE,EVIDENCE_FILE]:
        assert path.read_text(encoding='utf-8')==json.dumps(read_json(path),ensure_ascii=False,indent=2)+'\n'
    return dict(status='PASS',**summary,new_method_witnesses=methods,
        protected_shared_status_prior_families_r2k11a='BYTE_IDENTICAL',
        pinned_jar_reproduction='PASS' if jar_path else 'NOT_REQUESTED')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jar',type=Path,help='Reproduce only new witnesses against the exact pinned JAR')
    print(json.dumps(validate(parser.parse_args().jar),indent=2))
