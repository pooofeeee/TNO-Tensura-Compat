"""Focused, read-only R2k9a validation and optional pinned-JAR reproduction."""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import subprocess

from catalog_common import OUT, ROOT, read_json
from collect_cataclysm_leviathan_admission import (
    ALTAR, BLOCK, EVIDENCE_FILE, FRAGMENTS, L, PART, PART_BASE, PKG, REGISTRY,
    SPEC_FILE, collect, specification,
)

START = '40de2968c8d2fc0b89b73d8ca5ba8fe515f0d035'
CHECKPOINT = 'R2k9a-cataclysm-leviathan-admission-complete'
NOTE = OUT / 'cataclysm-r2k9a-leviathan-admission.json'
REVIEW = OUT / 'mod-reviews/cataclysm.json'
LEDGER = OUT / 'mod-completion-ledger.json'
BOSS_BASE = 'entity/AnimationMonster/BossMonsters/LLibrary_Boss_Monster'
KINDS = {'VANILLA_DIRECT', 'VANILLA_EQUIVALENT', 'VANILLA_LIKE_EXTENDED',
         'VANILLA_COMPOSITE', 'CUSTOM_DAMAGE', 'CUSTOM_STATUS', 'CUSTOM_CONTROL',
         'CUSTOM_RESOURCE', 'BINARY_MECHANIC'}
KEYS = {'incoming_admission', 'rush_hurt_interruption', 'multipart_admission',
        'shared_defense_bindings', 'nature_regen_binding', 'environment_admission',
        'phase_state_prerequisites', 'combat_persistence',
        'encounter_setup', 'altar_encounter'}
ORDER = ['EXCLUDE_DIRECT_ABYSS_BLAST_OR_PORTAL_ABYSS_BLAST',
         'ARM_DESTROY_BLOCKS20_IF_NONPOSITIVE', 'READ_CAUSING_RANGE_WITHOUT_USING_RESULT',
         'EYE_FLUID_CAN_SWIM_GATE_UNLESS_INVULNERABILITY_BYPASS_OR_CONFIG_OFF',
         'PHASE2_ANIMATION_GATE_UNLESS_INVULNERABILITY_BYPASS',
         'SHARED_HURT_SAME_SOURCE_AND_AMOUNT',
         'TRUE_HURT_RUSH38_TO54_REQUESTS_STUN_ANIMATION', 'RETURN_SHARED_HURT_RESULT']
SPAWN_ORDER = ['SACRIFICE_SLOT0_AND_COUNTER_GT121',
               'CLEAR_ENCOUNTER_VOLUME_BEFORE_SERVER_CHECK', 'CREATE_BEFORE_SERVER_CHECK',
               'SERVER_LEVEL_AND_NON_NULL', 'SET_POS', 'SET_HOME', 'ADD_FRESH_ENTITY',
               'ON_SUCCESS_CLEAR_ITEM_AND_NOTIFY', 'ORIGINAL_COUNTDOWN_UPDATE_OR_RESET']


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
    assert {e['id'] for e in new} == {'cataclysm:leviathan_' + k for k in KEYS}
    pids, eids = {p['id'] for p in paths}, {e['id'] for e in effects}
    for e in new:
        assert e['mod_key'] == 'cataclysm' and e['primary_classification'] in KINDS
        assert e['inspection_status'] == 'STATIC_REVIEWED' and not e['unresolved_ambiguities']
        assert e['actual_behavior'] and e['source_actor'] and e['primary_test_source']
        assert e['components'] and e['implementation'] and e['delivery_paths']
        assert set(e['delivery_paths']) <= pids
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
        for c in candidates:
            assert len(c['parameters']) == 1
            p = c['parameters'][0]
            owners = [x for x in e['components'] if x['primitive'] == c['primitive']
                      and p in x['numerical_parameters']]
            assert len(owners) == 1
            owner = owners[0]
            assert c['native_value'] == owner['numerical_parameters'][p]
            assert c['native_formula'] == owner['formula']
            assert c['units'] == owner['parameter_units'][p]
            assert c['native_boundary'] == owner['native_boundary']
        if e['id'] != 'cataclysm:leviathan_nature_regen_binding':
            assert not candidates, 'Native admission/setup constants are not outgoing scalar candidates'
    new_paths = [p for p in paths if p['id'].startswith('cataclysm:leviathan-admission:')]
    assert len(new_paths) == 10
    for p in new_paths:
        assert p['mod_key'] == 'cataclysm' and p['status'] == 'VERIFIED'
        assert p['primary_source'] and p['native_path'] and p['setup'] and p['implementation']
        assert p['labels'] and p['runtime_status'] == 'NOT_RUN'
        assert p['effect_ids'] and set(p['effect_ids']) <= eids
        for e in new:
            assert (p['id'] in e['delivery_paths']) == (e['id'] in p['effect_ids'])
    expected_packages = [dict(id=e['id'], primary_classification=e['primary_classification'],
        delivery_paths=e['delivery_paths'], numerical_candidates=[{k: c[k] for k in
            ['primitive', 'parameters', 'native_value', 'units', 'native_boundary']}
            for c in e['scalable_parameter_candidates']], binary_gates=e['binary_parameters']) for e in new]
    assert note['mechanic_packages'] == expected_packages
    summary = dict(new_mechanics=len(new), delivery_paths=len(new_paths),
        classifications=dict(sorted(Counter(e['primary_classification'] for e in new).items())),
        candidate_numeric_parameters=sum(len(c['parameters']) for e in new for c in e['scalable_parameter_candidates']),
        shared_binding_records=1, unresolved_subsection_ambiguities=0)
    assert summary == note['summary']
    assert summary['classifications'] == {'BINARY_MECHANIC': 9, 'VANILLA_DIRECT': 1}
    assert summary['candidate_numeric_parameters'] == 1
    assert review['status'] == ledger['status'] == note['status'] == 'PARTIAL'
    assert all(review[k] is False for k in ['semantic_discovery_complete',
        'special_damage_discovery_complete', 'source_mapping_complete', 'delivery_mapping_complete'])
    cat = next(t for t in ledger['targets'] if t['mod_key'] == 'cataclysm')
    assert cat['state'] == 'PARTIAL' and cat['semantic_effect_count'] == len(effects)
    assert review['checkpoint'] == ledger['checkpoint'] == note['checkpoint'] == CHECKPOINT
    assert review['exact_next_task'] == note['exact_next_task'] == cat['exact_next_task']
    assert note['exact_next_task'].startswith('R2k9b: The Leviathan offense/payload family.')
    assert note['remaining_leviathan_work'] and not note['remaining_subsection_native_ambiguities']
    assert note['whole_mod_complete'] is False and note['runtime_tests'] == 0
    assert all(note[k] is False for k in ['stage_eligibility_decided', 'phase6_reopened',
        'production_changed', 'stage_changed', 'boss_testing_started', 'l2_testing_started',
        'compatibility_fixes_started', 'phase7_started'])
    validate_contracts({e['id'].removeprefix('cataclysm:leviathan_'): e for e in new}, note)
    return summary


def validate_contracts(rows, note):
    def values(key, primitive):
        return next(c['numerical_parameters'] for c in rows[key]['components'] if c['primitive'] == primitive)

    def flags(key, true=(), false=()):
        assert all(rows[key][k] is True for k in true), key
        assert all(rows[key][k] is False for k in false), key

    incoming = rows['incoming_admission']
    assert note['admission_order']['concrete'] == incoming['admission_order'] == ORDER
    assert incoming['excluded_direct_classes'] == ['Abyss_Blast_Entity', 'Portal_Abyss_Blast_Entity']
    flags('incoming_admission', true=['source_object_preserved', 'timer_armed_before_shared_hurt',
        'fluid_gate_uses_eye_fluid', 'immune_out_of_water_installed', 'feedback_uses_direct_player',
        'phase_gate_uses_animation_not_saved_latch'], false=['incoming_amount_rewritten',
        'direct_exclusion_bypassable', 'timer_requires_hurt_success', 'local_range_read_result_used',
        'fluid_gate_is_water_type_equality'])
    assert values('incoming_admission', 'TERRAIN_RESPONSE_ARMING') == dict(arming_ticks=20)
    flags('rush_hurt_interruption', true=['interruption_requires_hurt_true'], false=[
        'interruption_requires_measured_hp_loss', 'interruption_is_mob_effect',
        'local_interruption_server_guard', 'adds_outgoing_damage'])
    assert values('rush_hurt_interruption', 'NATIVE_ANIMATION_STATE') == dict(
        window_first_tick=38, window_last_tick=54, stun_animation_duration=90)
    flags('multipart_admission', true=['game_event_requires_hurt_true', 'part_nbt_methods_empty'],
        false=['part_damage_multiplier_added', 'part_scale_used_in_hurt', 'part_hurt_calls_super',
        'part_hurt_checks_own_invulnerability'])
    assert rows['multipart_admission']['part_count'] == 3
    assert values('multipart_admission', 'MULTIPART_ADMISSION') == dict(part_count=3, unused_scale_default=1.0)
    cfg = read_json(OUT / 'cataclysm-installed-common-config.json')['values']['mobs']['leviathan']
    assert incoming['immune_out_of_water_installed'] == cfg['immune_out_of_water']
    bindings = {'DamageCap': ('damageCap', cfg['cap_config']['damage_cap']),
        'DpsCap': ('dpsCap', cfg['cap_config']['dps_cap']),
        'RangeLimit': ('rangeCap', cfg['cap_config']['range_cap']),
        'NatureRegen': ('natureHeal', cfg['nature_heal_config']['nature_heal']),
        'DpsMulti': ('dpsLimitTime', cfg['cap_config']['dps_limit_time'])}
    assert note['concrete_bindings'] == rows['shared_defense_bindings']['concrete_bindings']
    for name, (field, value) in bindings.items():
        assert note['concrete_bindings'][name]['config_field'] == 'Leviathan.' + field
        assert note['concrete_bindings'][name]['installed_value'] == value
        assert note['concrete_bindings'][name]['shared_boundary']
    assert note['concrete_bindings']['RangeLimit']['native_cast'] == 'double(config), no float narrowing'
    assert note['concrete_bindings']['HealCooldown']['native_value'] == 600
    assert note['concrete_bindings']['HealCooldown']['inherited'] is False
    flags('shared_defense_bindings', true=['damage_cap_is_bucket_capacity'], false=[
        'dps_is_bucket_capacity', 'range_narrows_float_before_double', 'dps_multi_read_by_shared_hurt_or_tick'])
    assert rows['shared_defense_bindings']['installed_config_values'] == dict(
        damage_cap=20.0, dps_cap=15.0, range_limit=38.0, heal_cooldown=600, dps_limit_time=20)
    assert values('shared_defense_bindings', 'DAMAGE_CAP') == dict(per_hit_cap=20.0)
    assert values('shared_defense_bindings', 'DPS_BUCKET') == dict(capacity=20.0, dps_cap=15.0, drain_divisor=20)
    assert values('shared_defense_bindings', 'RANGE_ADMISSION') == dict(range_limit=38.0)
    assert values('shared_defense_bindings', 'REGEN_ADMISSION_TIMER') == dict(heal_cooldown=600)
    regen = rows['nature_regen_binding']
    assert regen['record_kind'] == 'SHARED_BINDING' and regen['binding_of'] == 'cataclysm:shared_heal'
    packages = read_json(OUT / regen['binding_contract_file'])['mechanic_packages']
    assert any(p['id'] == regen['binding_of'] for p in packages)
    assert regen['adds_second_heal'] is False
    assert values('nature_regen_binding', 'NATIVE_HEAL') == dict(amount=25.0)
    assert rows['environment_admission']['blocked_exact_damage_type_keys'] == [
        'minecraft:in_wall', 'minecraft:falling_block']
    flags('environment_admission', true=['exact_type_filter_precedes_shared_bypass',
        'registered_fire_immune', 'air_supply_returns_native_max'], false=['fluid_push',
        'bubble_callbacks_call_parent', 'blanket_drowning_damage_immunity_claimed', 'concrete_fall_damage_override'])
    assert {c['primitive'] for c in rows['environment_admission']['components']} == {
        'NATIVE_DAMAGE_ADMISSION', 'NATIVE_FIRE_ADMISSION', 'AIR_SUPPLY_GATE', 'FLUID_RESPONSE_GATE'}
    assert rows['phase_state_prerequisites']['default_state'] == dict(
        blast_chance=0, mode_chance=0, melt_down=False, tongue_uuid=None, tongue_id=-1)
    flags('phase_state_prerequisites', true=['phase_start_has_no_ai_gate'], false=[
        'live_health_predicate_is_saved_latch', 'raw_integer_setters_clamp', 'raw_setters_heal',
        'raw_setters_change_animation', 'phase_start_local_server_guard', 'phase_start_requires_target',
        'phase_start_requires_fluid', 'latch_write_local_server_guard', 'latch_write_local_no_ai_gate',
        'healing_clears_saved_latch', 'mode_chance_is_attack_mode_enum'])
    assert values('phase_state_prerequisites', 'PHASE_STATE') == dict(
        health_divisor=2.0, phase_animation_duration=200, latch_tick=90)
    persistence = rows['combat_persistence']
    assert persistence['saved_concrete_keys'] == ['BlastChance', 'MeltDown', 'ModeChance']
    assert persistence['missing_key_defaults'] == dict(BlastChance=0, ModeChance=0, MeltDown=False)
    flags('combat_persistence', false=['saved_animation', 'saved_attack_mode', 'saved_tongue_uuid',
        'saved_tongue_id', 'saved_portal_target', 'saved_terrain_timer', 'saved_native_attack_timers',
        'generic_persistence_added'])
    setup = rows['encounter_setup']
    assert setup['attributes_apply_to'] == 'cataclysm:the_leviathan'
    assert setup['registered_dimensions'] == dict(width=4.5, height=3.0)
    assert setup['registered_eye_height'] == 1.350000023841858
    flags('encounter_setup', true=['constructor_calls_switch_navigator_false'], false=[
        'concrete_finalize_spawn_override', 'constructor_sets_home', 'constructor_sets_phase_latch',
        'configured_health_is_heal_delivery', 'explicit_armor_toughness_added'])
    assert values('encounter_setup', 'NATIVE_ATTRIBUTE_SETUP') == dict(base_health=400.0,
        base_attack_damage=15.0, armor=10.0, knockback_resistance=1.0, health_multiplier=1.0, attack_multiplier=1.0)
    altar = rows['altar_encounter']
    assert altar['spawn_order'] == SPAWN_ORDER
    assert altar['default_block_state'] == dict(facing='NORTH', waterlogged=False)
    flags('altar_encounter', true=['spawn_sets_home', 'clearance_precedes_create',
        'cleanup_requires_add_success', 'inventory_saved'], false=['spawn_calls_finalize_spawn',
        'spawn_sets_persistence_required', 'spawn_sets_phase_latch', 'spawn_requires_water',
        'clearance_has_local_server_guard', 'clearance_requires_mobgriefing', 'clearance_has_explicit_destroy_hook',
        'altar_removed_on_add_success', 'retry_counter_reset_on_failed_add', 'countdown_saved',
        'summoning_flag_saved', 'ticker_has_side_gate', 'activation_local_server_guard', 'placement_requires_sacrifice'])
    assert values('altar_encounter', 'ENCOUNTER_GATE') == dict(slot=0, max_stack_size=1,
        summon_threshold_exclusive=121, spawn_y_offset=3, spawn_xz_offset=0.5)
    assert values('altar_encounter', 'ENCOUNTER_CLEARANCE') == dict(x_extent=3, y_extent=6, z_extent=3)


def validate_preservation(review, note, ledger):
    assert note['starting_sha'] == START
    old = json.loads(at_start(REVIEW))
    assert [e for e in review['effects'] if e['review_checkpoint'] != CHECKPOINT] == old['effects']
    assert [p for p in review['paths'] if not p['id'].startswith('cataclysm:leviathan-admission:')] == old['paths']
    mutable = {'effects', 'paths', 'checkpoint', 'scope', 'notes_file', 'exact_next_task', 'protected_checkpoints'}
    assert {k: v for k, v in review.items() if k not in mutable} == {k: v for k, v in old.items() if k not in mutable}
    assert review['protected_checkpoints'] == old['protected_checkpoints'] + [
        dict(checkpoint=old['checkpoint'], notes_file=old['notes_file'])]
    assert note['previous_checkpoint'] == old['checkpoint']
    previous_note = json.loads(at_start(OUT / old['notes_file']))
    assert {r['file'] for r in note['reference_files'] if r['usage'] == 'LOCKED_REUSED'} >= {
        old['notes_file'], *(r['file'] for r in previous_note['reference_files'])}
    assert note['protected_r2k8b'] == dict(file=old['notes_file'],
        sha256=hashlib.sha256(at_start(OUT / old['notes_file'])).hexdigest())
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


def validate_native_distinctions(evidence):
    def body(name, method):
        w = next(w for w in evidence['witnesses'] if w['entry'] == PKG + name + '.class')
        return next(m['instructions'] for m in w['methods'] if m['name'] == method)

    def calls(ins, text):
        return [i['offset'] for i in ins if text in str(i['operand'])]

    def item(ins, offset):
        return next(i for i in ins if i['offset'] == offset)

    hurt = body(L, 'hurt')
    assert calls(hurt, '.getDirectEntity(') == [1]
    assert [item(hurt, p)['operand'] for p in [6, 13]] == [
        PKG + 'entity/AnimationMonster/BossMonsters/The_Leviathan/Abyss_Blast_Entity',
        PKG + 'entity/AnimationMonster/BossMonsters/The_Leviathan/Portal_Abyss_Blast_Entity']
    assert item(hurt, 19)['operand'] == 0 and item(hurt, 20)['opcode'] == '0xac'
    assert calls(hurt, '.destroyBlocksTickI') == [22, 31] and item(hurt, 29)['operand'] == 20
    assert calls(hurt, '.calculateRange(') == [36] and item(hurt, 39)['opcode'] == '0x39'
    assert not any(i['opcode'] in ['0x18', '0x26', '0x27', '0x28', '0x29'] for i in hurt)
    assert calls(hurt, '.getEyeInFluidType(') == [43] and calls(hurt, '.canInFluidType(') == [46]
    assert calls(hurt, 'BYPASSES_INVULNERABILITY') == [57, 110]
    assert calls(hurt, 'Leviathan.ImmuneOutofWaterZ') == [66]
    assert item(hurt, 73)['operand'] == 'net/minecraft/world/entity/player/Player'
    assert calls(hurt, '.displayClientMessage(') == [94]
    assert calls(hurt, '.LEVIATHAN_PHASE2L') == [103]
    assert calls(hurt, 'LLibrary_Boss_Monster.hurt(') == [124]
    assert [item(hurt, p)['opcode'] for p in [122, 123, 127]] == ['0x2b', '0x24', '0x36']
    assert calls(hurt, '.LEVIATHAN_RUSHL') == [133]
    assert [item(hurt, p)['operand'] for p in [143, 152]] == [38, 54]
    assert [item(hurt, p)['opcode'] for p in [145, 154, 157, 159]] == ['0xa1', '0xa3', '0x15', '0x99']
    assert calls(hurt, '.LEVIATHAN_STUNL') == [166]
    assert calls(hurt, 'AnimationHandler.sendAnimationMessage(') == [169]
    assert [item(hurt, p)['opcode'] for p in [172, 174]] == ['0x15', '0xac']
    assert all(not calls(hurt, x) for x in ['.heal(', '.addEffect(', '.getHealth(', '.getOwner('])
    fluid = body(L, 'canInFluidType')
    assert calls(fluid, 'WATER_TYPE') == [0] and item(fluid, 8)['opcode'] == '0x57'
    assert calls(fluid, 'FluidType.canSwim(') == [14]
    assert not any(i['opcode'] in ['0xa5', '0xa6'] for i in fluid)
    invulnerable = body(L, 'isInvulnerableTo')
    assert calls(invulnerable, 'DamageTypes.IN_WALL') == [1]
    assert calls(invulnerable, 'DamageTypes.FALLING_BLOCK') == [11]
    assert calls(invulnerable, 'LLibrary_Boss_Monster.isInvulnerableTo(') == [22]
    assert not calls(invulnerable, 'BYPASSES_INVULNERABILITY')
    for method, field in [('DamageCap', 'damageCap'), ('DpsCap', 'dpsCap'), ('NatureRegen', 'natureHeal')]:
        ins = body(L, method)
        assert calls(ins, 'CMCommonConfig$Leviathan.' + field + 'D') == [0]
        assert item(ins, 3)['opcode'] == '0x90'
    assert calls(body(L, 'RangeLimit'), 'Leviathan.rangeCapD') == [0]
    assert item(body(L, 'RangeLimit'), 3)['opcode'] == '0xaf'
    assert calls(body(L, 'DpsMulti'), 'Leviathan.dpsLimitTimeI') == [0]
    assert item(body(L, 'HealCooldown'), 0)['operand'] == 600
    assert calls(body(L, 'increaseAirSupply'), '.getMaxAirSupply(') == [1]
    assert [i['opcode'] for i in body(L, 'isPushedByFluid')] == ['0x3', '0xac']
    for method in ['onInsideBubbleColumn', 'onAboveBubbleCol']:
        assert [i['opcode'] for i in body(L, method)] == ['0xb1']
    defaults = body(L, 'defineSynchedData')
    assert [item(defaults, p)['operand'] for p in [9, 21, 33, 56]] == [0, 0, 0, -1]
    for method in ['setMeltDown', 'setBlastChance', 'setModeChance']:
        ins = body(L, method)
        assert len(calls(ins, 'SynchedEntityData.set(')) == 1
        assert all(not calls(ins, t) for t in ['clamp', '.heal(', '.setAnimation('])
    assert item(body(L, 'isMeltDown'), 8)['operand'] == 2.0
    assert not calls(body(L, 'isMeltDown'), '.getMeltDown(')
    tick, ai = body(L, 'tick'), body(L, 'aiStep')
    assert calls(tick, '.isNoAi(') == [690] and calls(tick, '.setAnimation(') == [731]
    assert [calls(tick, t) for t in ['.getMeltDown(', '.isMeltDown(', '.isAlive(']] == [[707], [714], [721]]
    assert calls(ai, '.getAnimationTick(') == [2900] and item(ai, 2903)['operand'] == 90
    assert calls(ai, '.getMeltDown(') == [2909] and calls(ai, '.setMeltDown(') == [2917]
    assert item(ai, 2905)['opcode'] == '0xa0' and item(ai, 2916)['operand'] == 1
    assert all(not calls(ins, t) for ins in [tick, ai] for t in ['isClientSide', '.getTarget(', '.getEyeInFluidType('])
    assert not calls(ai, '.isNoAi(')
    assert [item(body(L, '<clinit>'), p)['operand'] for p in [52, 135]] == [90, 200]
    save, load = body(L, 'addAdditionalSaveData'), body(L, 'readAdditionalSaveData')
    assert calls(save, 'CompoundTag.putInt(') == [13, 35]
    assert calls(save, 'CompoundTag.putBoolean(') == [24]
    assert [item(save, p)['operand'] for p in [6, 17, 28]] == ['BlastChance', 'MeltDown', 'ModeChance']
    assert [calls(load, t) for t in ['.setBlastChance(', '.setModeChance(', '.setMeltDown(']] == [[13], [24], [35]]
    assert not calls(load, 'CompoundTag.contains(')
    part = body(PART, 'hurt')
    assert item(part, 4)['opcode'] == '0xc6' and calls(part, '.attackEntityFromPart(') == [17]
    assert item(part, 30)['opcode'] == '0x99' and calls(part, 'GameEvent.ENTITY_DAMAGE') == [34]
    assert all(not calls(part, t) for t in ['.scaleF', '.isInvulnerableTo(', 'Cm_Part_Entity.hurt('])
    assert [i['opcode'] for i in body(L, 'attackEntityFromPart')] == ['0x2a', '0x2c', '0x25', '0xb6', '0xac']
    for method in ['addAdditionalSaveData', 'readAdditionalSaveData']:
        assert [i['opcode'] for i in body(PART, method)] == ['0xb1']
    spawn = body(ALTAR, 'tick')
    assert calls(spawn, 'ABYSSAL_SACRIFICE') == [42] and item(spawn, 111)['operand'] == 121
    assert item(spawn, 113)['opcode'] == '0xa4'
    assert calls(spawn, '.BlockBreaking(') == [121] and calls(spawn, 'EntityType.create(') == [134]
    assert item(spawn, 143)['operand'] == 'net/minecraft/server/level/ServerLevel'
    assert item(spawn, 157)['opcode'] == '0xc6'
    assert calls(spawn, '.setPos(') == [187] and calls(spawn, '.setHomePos(') == [201]
    assert calls(spawn, '.addFreshEntity(') == [207] and item(spawn, 214)['opcode'] == '0x99'
    assert calls(spawn, 'NonNullList.set(') == [225] and calls(spawn, '.sendBlockUpdated(') == [238]
    assert all(not calls(spawn, t) for t in ['.finalizeSpawn(', '.setPersistenceRequired(', '.setMeltDown(',
        '.destroyBlock(', 'isClientSide', 'GameRules.', '.isInWater('])
    clearance = body(ALTAR, 'BlockBreaking')
    assert calls(clearance, 'Mth.floor(F)') == [8, 21, 34]
    assert calls(clearance, 'ALTAR_DESTROY_IMMUNE') == [128]
    assert item(clearance, 123)['opcode'] == '0xa5'
    assert calls(clearance, '.destroyBlock(') == [144] and item(clearance, 143)['operand'] == 0
    assert all(not calls(clearance, t) for t in ['GameRules.', 'isClientSide', 'EventHooks.', '.isAir('])
    use = body(BLOCK, 'useItemOn')
    assert calls(use, '.isShiftKeyDown(') == [23] and calls(use, '.isCreative(') == [89]
    assert calls(use, 'ItemStack.setCount(') == [62] and calls(use, 'ItemStack.shrink(') == [98]
    assert calls(use, '.popResource(') == [116] and not calls(use, 'ABYSSAL_SACRIFICE')
    assert not calls(use, 'isClientSide')
    assert calls(body(ALTAR, 'loadAdditional'), 'ContainerHelper.loadAllItems(') == [19]
    assert calls(body(ALTAR, 'saveAdditional'), 'ContainerHelper.saveAllItems(') == [13]
    assert not calls(body(ALTAR, 'loadAdditional'), '.summoningticksI')
    registry = body(REGISTRY, 'lambda$static$27')
    assert calls(registry, '.fireImmune(') == [20]
    assert [item(registry, p)['operand'] for p in [11, 14, 23, 38]] == [4.5, 3.0, 1.350000023841858, 'cataclysm:the_leviathan']
    assert calls(body(L, '<init>'), '.setConfigattribute(') == [302]


def validate_evidence(review, note, jar_path=None):
    assert read_json(SPEC_FILE) == specification()
    evidence = read_json(EVIDENCE_FILE)
    assert len(evidence['witnesses']) == note['tooling']['new_native_witnesses'] == 7
    assert [w['entry'] for w in evidence['witnesses']] == [s['entry'] for s in specification()['evidence_specifications']]
    if jar_path is not None:
        assert evidence == collect(jar_path), 'Pinned-JAR witnesses did not reproduce'
    census = {c['entry']: c['entry_sha256'] for c in read_json(OUT / 'cataclysm-source-census.json')['classes']}
    inventory = next(t for t in read_json(OUT / 'jar-inventory.json')['targets'] if t['key'] == 'cataclysm')
    assert note['tooling']['jar_sha256'] == inventory['sha256']
    assert note['tooling']['jar_size_bytes'] == inventory['size_bytes']
    assert note['tooling']['reused_evidence_regenerated'] is False and note['tooling']['recursive_jar_scan'] is False
    sources = {r['file']: read_json(OUT / r['file']) for r in note['reference_files']
               if r['file'].startswith('native-evidence/')}
    methods = [(w['entry'], m['name'], m['descriptor']) for w in evidence['witnesses'] for m in w.get('methods', [])]
    assert len(methods) == len(set(methods)) == note['tooling']['new_method_witnesses'] == 61
    old_methods = {}
    for ref in note['reference_files']:
        if ref['usage'] != 'LOCKED_REUSED' or ref['file'] not in sources:
            continue
        for w in sources[ref['file']]['witnesses']:
            for m in w.get('methods', []):
                old_methods.setdefault((w['entry'], m['name'], m['descriptor']), []).append(m)
    for w in evidence['witnesses']:
        assert w['jar_sha256'] == inventory['sha256']
        if w['entry'].endswith('.class'):
            assert w['entry_sha256'] == census[w['entry']]
        for m in w.get('methods', []):
            if 'instruction_offset_ranges' in m:
                assert m['instruction_offset_ranges'] == FRAGMENTS[w['entry'][len(PKG):-6]][m['name']]
            for old in old_methods.get((w['entry'], m['name'], m['descriptor']), []):
                assert {'instruction_offset_ranges', 'instruction_offset_range'} & old.keys()
                assert 'instruction_offset_ranges' in m
                assert not ({i['offset'] for i in old['instructions']} & {i['offset'] for i in m['instructions']}), w['entry']
    concrete = next(w for w in evidence['witnesses'] if w['entry'] == PKG + L + '.class')
    assert concrete['superclass'] == PKG + BOSS_BASE
    assert not {'finalizeSpawn', 'causeFallDamage', 'mobInteract'} & set(concrete['declared_method_names'])
    for e in selected(review):
        for p in e['implementation']:
            w = next(w for w in sources[p['evidence_file']]['witnesses'] if w['id'] == p['witness_id'])
            assert p['entry'] == w['entry'] and set(p['methods']) <= {m['name'] for m in w.get('methods', [])}
    tag = next(w for w in evidence['witnesses'] if w['entry'].endswith('/altar_destroy_immune.json'))
    assert 'cataclysm:altar_of_abyss' in tag['data']['values']
    registration = next(w for w in evidence['witnesses'] if w['entry'] == PKG + REGISTRY + '.class')
    assert [b['index'] for b in registration['registration_bootstraps']] == [86, 141]
    assert any(PKG + L + '.<init>' in str(b['arguments']) for b in registration['registration_bootstraps'])
    ticker = next(w for w in evidence['witnesses'] if w['entry'] == PKG + BLOCK + '.class')
    assert any(PKG + ALTAR + '.commonTick' in str(b['arguments']) for b in ticker['registration_bootstraps'])
    shared = next(w for w in sources['native-evidence/cataclysm-shared.json']['witnesses']
                  if w['entry'] == PKG + BOSS_BASE + '.class')
    assert not any('DpsMulti' in str(i['operand']) for m in shared['methods'] if m['name'] in ['hurt', 'tick']
                   for i in m['instructions'])
    validate_native_distinctions(evidence)
    return len(methods)


def validate(jar_path=None):
    review, note, ledger = [read_json(p) for p in [REVIEW, NOTE, LEDGER]]
    summary = validate_records(review, note, ledger)
    validate_preservation(review, note, ledger)
    methods = validate_evidence(review, note, jar_path)
    return dict(status='PASS', **summary, new_method_witnesses=methods,
        protected_shared_status_and_prior_bosses='BYTE_IDENTICAL', prior_records_and_paths='UNCHANGED',
        pinned_jar='REPRODUCED' if jar_path is not None else 'ARCHIVED_WITNESSES_VALIDATED')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jar', type=Path, help='Optional exact pinned Cataclysm 3.27 JAR')
    print(json.dumps(validate(parser.parse_args().jar), indent=2))
