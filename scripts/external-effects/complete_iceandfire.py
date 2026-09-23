"""Promote protected combat contracts, preserving source variants without repeating native research."""
from copy import deepcopy
from collections import defaultdict,Counter
from catalog_common import *
from assemble_batch import refresh
from iceandfire_promotion_migration import START

CP='R2g10b-iceandfire-complete'
NEXT='R2h1: Eternal Starlight installed-native combat source foundation. Reuse broad source aids, pin native registries/damage/status producers and direct compat; no repeated Ice & Fire, runtime, L2, Stage or production work.'
STEMS=['r2g2a-frozen-core','r2g2b-frozen-dragons','r2g3a-siren-song','r2g3b-siren-flute-attacks','r2g4-gorgon','r2g5a-dragon-elements','r2g5b-dragon-combat','r2g6-cockatrice','r2g7-worm-cyclops','r2g8a-ghost-troll','r2g8b-hydra-serpent','r2g8c-avian-mounts','r2g8d-dread','r2g9a-weapons','r2g9b-control','r2g10a-closure']

# These are pointers to already reviewed facts, not new native assertions.
FACT_KEYS={line.split('=')[0]:line.split('=')[1].split() for line in '''
frozen=core not_damage tick_order native_admission native_removal cures compat_dispatch compat_eligibility compat_existing
frozen_weapon_companions=weapon_registry weapon_callback weapon_payload config compat_existing
ice_blood_bonus=weapon_callback config blood_bonus
siren_song=mechanic singing acquisition map_before_effect timer_and_distance map_player_bug approach removal_shared_state aggro_boundary persistence native_immunity status_independence
siren_flute=flute_acquisition flute_selection attachment_route tick_entry love_control love_removal_and_compat
siren_bite=attack_entry bite
siren_pull=attack_entry pull
gorgon_petrification=gaze_entry gaze_geometry gaze_order head_entry head_order native_admission immunity compatibility
gorgon_melee=fallback_melee native_admission
gorgon_poison=fallback_melee immunity compatibility
stone_statue_admission=statue_state statue_defense compatibility
dragon_elemental_damage=native_entries sampling breath_amounts charge_amounts charge_subtypes source_identity runtime_limits
dragon_fire_ignition=fire_lifecycle sampling source_identity
dragon_lightning_knockback=knockback source_identity
dragon_charge_explosion=optional_explosion explosion_amount explosion_finalize source_identity
dragon_placed_fire=terrain_hazards fire_lifecycle
dragon_ice_spikes=terrain_hazards
dragon_body_hits=entry body_attacks tackle rider_bite shake_prey target_admission
dragon_grab_knockback=body_attacks shake_prey
dragon_roar=roar
dragon_healing=healing resources shake_prey
dragon_native_defense=defenses death_and_compat target_admission
dragon_native_attributes=attributes resources
dragon_multipart=multipart
cockatrice_wither=gaze_admission gaze_payload scepter_acquisition scepter_maintained scepter_lifecycle compatibility
cockatrice_control=gaze_admission gaze_payload melee_control target_control
cockatrice_melee=melee_control
cockatrice_taming=taming
cockatrice_defense=defense_heal compatibility
cockatrice_heal=defense_heal
scepter_target_lock=scepter_acquisition scepter_maintained scepter_lifecycle
worm_cyclops_hits=worm_melee cyclops_melee_grab
worm_explosions=worm_attack_explosions worm_tnt
cyclops_grab=cyclops_melee_grab
cyclops_blinding=cyclops_eye
worm_defense=worm_defense_resources compatibility_and_scaling
worm_kill_heal=worm_defense_resources
worm_lifecycle=worm_defense_resources worm_tnt
cyclops_eye_aura=cyclops_target_and_aura
ghost_troll_body=ghost_body troll_body_explosion troll_weapon
ghost_sword_magic=ghost_sword_launch ghost_sword_impact ghost_sword_returns
ghost_sword_aux=ghost_sword_launch ghost_sword_impact ghost_sword_returns
ghost_defense=ghost_defense compatibility
troll_explosion=troll_body_explosion
troll_control=troll_body_explosion troll_regen_conversion troll_weapon
troll_regeneration=troll_regen_conversion
iaf_armor_callback=armor_real_hook compatibility
hydra_serpent_damage=hydra_attack hydra_breath serpent_attack serpent_breath_admission serpent_bubble_payload
hydra_poison=hydra_attack hydra_breath hydra_arrow
hydra_heads=hydra_head_resource hydra_survival_regrowth
hydra_regen=hydra_regen_heart
hydra_serpent_arrows=hydra_arrow serpent_arrow_armor arrow_delivery
hydra_arrow_heal=hydra_arrow
hydra_serpent_control=hydra_breath serpent_attack serpent_arrow_armor
serpent_defense=serpent_defense_resources
serpent_armor=serpent_arrow_armor
avian_mount_hits=bird_hits amphithere_body amphithere_rider_defense hippogryph_body macuahuitl_dagger
avian_projectiles=feather_and_bundle avian_arrows
avian_control=avian_arrows amphithere_body hippogryph_body macuahuitl_dagger
avian_ai_defense=bird_flock_control amphithere_rider_defense
mount_healing=mount_healing
hippocampus_breathing=hippocampus_support
dread_melee=body_damage
dread_motion=body_damage knight_mount
dread_summon=lich_summon commander_resource necromancy_unreachable queen_exclusion
dread_skull=lich_skull_delivery skull_homing skull_damage
dread_shield=skull_damage
dread_admission=defenses_targets direct_compat
weapon_bonus=post_hit_entry bonus
weapon_fire=post_hit_entry fire_payload
weapon_lightning=summoned_lightning tide_channeling
weapon_chain=post_hit_entry lightning_chain
weapon_active_melee=hippogryph_sweep gauntlet
weapon_control=post_hit_entry fire_payload slapper gauntlet hippogryph_sweep
dragon_arrow_damage=dragon_bow_arrow
tide_trident_damage=tide_delivery tide_hit tide_channeling
chain_control=chain_delivery chain_compat chain_tick chain_release
flute_control=flute
pixie_spell_damage=pixie_wand pixie_charge
pixie_status_resource=pixie_charge pixie_aura pixie_theft pixie_defense_heal
pixie_heal=pixie_defense_heal
food_status=foods dragon_flesh
food_hazard=dragon_flesh
lightning_armor_immunity=lightning_armor
ghost_death_summon=ghost_death_delivery
blindfold_status=blindfold
egg_zero_hit=egg_zero_hit
native_ai_admission=native_target_control
'''.strip().splitlines()}

ALIASES={
 'iaf:ice_blood_bonus':['iaf:weapon_bonus'],
 'iaf:dragon_fire_ignition':['iaf:native_ignition'],
 'iaf:weapon_fire':['iaf:native_ignition'],
 'iaf:weapon_lightning':['iaf:native_lightning'],
 'iaf:food_hazard':['iaf:native_ignition','iaf:native_lightning'],
 'iaf:gorgon_poison':['iaf:native_poison'],
 'iaf:hydra_poison':['iaf:native_poison'],
 'iaf:troll_regeneration':['iaf:native_regeneration'],
 'iaf:hydra_regen':['iaf:native_regeneration'],
 'iaf:hydra_serpent_arrows':['iaf:native_arrow_damage'],
 'iaf:avian_projectiles':['iaf:native_arrow_damage'],
 'iaf:dragon_arrow_damage':['iaf:native_arrow_damage'],
}
CANONICAL={
 'iaf:native_ignition':('Native ignition and fire pulses','VANILLA_LIKE_EXTENDED','Once at native Entity.baseTick on_fire hurt amount. Source-specific ignition seconds and admission remain unchanged; never add dragon or attacker attribution.'),
 'iaf:native_lightning':('Real vanilla lightning from weapons and food','VANILLA_DIRECT','Once at native Entity.thunderHit final lightning_bolt hurt amount after native/NeoForge admission. Do not scale bolt count or duplicate this at the summoner.'),
 'iaf:native_poison':('Native Poison from Gorgon and Hydra','VANILLA_COMPOSITE','Once at native PoisonMobEffect.applyEffectTick hurt amount, preserving HP>1 and effect admission. No duration/amplifier scaling; nonlethal behavior requires runtime/policy review before implementation.'),
 'iaf:native_regeneration':('Native Regeneration from Troll and Hydra sources','VANILLA_DIRECT','Once at native RegenerationMobEffect heal(1) request through LivingHealEvent. Do not scale duration/amplifier.'),
 'iaf:native_arrow_damage':('Inherited arrow HP damage with source-specific payloads','VANILLA_LIKE_EXTENDED','Once at AbstractArrow.onHitEntity final hurt amount after native speed, base damage, crit and enchantments. Preserve separate accepted-hit poison/heal/control/shield effects; do not also scale baseDamage.'),
}

def unique(rows):
    result=[];seen=set()
    for row in rows:
        key=json.dumps(row,sort_keys=True)
        if key not in seen:seen.add(key);result.append(deepcopy(row))
    return result

def pkg(id,name,classification,categories,point,reason,paths):
    return dict(id='iaf:'+id,name=name,primary_classification=classification,tno_categories=categories.split(),stage_scaling_needed=bool(point),single_scaling_point=point,stage_reason=reason,delivery_paths=paths)

def normalized_section(stem,d):
    """Adapt early schemas using protected facts only; keep all original route IDs."""
    if 'mechanic_packages' in d:return deepcopy(d['mechanic_packages']),deepcopy(d['delivery_paths'])
    if stem=='r2g2a-frozen-core':
        paths=deepcopy(d['reviewed_weapon_paths']);ids=[p['id'] for p in paths]
        return [pkg('frozen','Frozen velocity control','CUSTOM_STATUS','CUSTOM_ROUTED ADMISSION_GATED NO_STAGE_VALUE',None,'Velocity/lifecycle control; no HP payload or Stage amount.',ids),
          pkg('frozen_weapon_companions','Frozen weapon Slowness and Mining Fatigue','VANILLA_COMPOSITE','COMPOSITE VANILLA_ROUTED ADMISSION_GATED NO_STAGE_VALUE',None,'Independent native status requests; no duration/amplifier scaling.',ids),
          pkg('ice_blood_bonus','Ice blood conditional native bonus','CUSTOM_DAMAGE','NUMERIC_SCALABLE CUSTOM_ROUTED ADMISSION_GATED','Once at DamageBonusAbility final target.hurt(bonusSource,bonus).','Native8 is a separate request, not Frozen damage.',ids[:1])],paths
    if stem=='r2g2b-frozen-dragons':
        paths=deepcopy(d['dragon_entry_routes']);ids=[p['id'] for p in paths]
        return [pkg('frozen','Frozen velocity control','CUSTOM_STATUS','CUSTOM_ROUTED ADMISSION_GATED NO_STAGE_VALUE',None,'Same protected Frozen holder, with native dragon source variants.',ids),
          pkg('dragon_elemental_damage','Dragon elemental HP requests','CUSTOM_DAMAGE','NUMERIC_SCALABLE CUSTOM_ROUTED ADMISSION_GATED','Each native target.hurt amount once in the downstream Stage amount layer; never also scale age/config, projectile and area.','Ice direct damage and area HP attempts are separate from Frozen.',ids)],paths
    if stem=='r2g3a-siren-song':
        paths=deepcopy(d['delivery_paths'])
        return [pkg('siren_song','Siren native song map and control','CUSTOM_CONTROL','COMPOSITE CUSTOM_ROUTED ADMISSION_GATED NO_STAGE_VALUE',None,'Independent map-driven control and cosmetic status marker; no HP amount.',[p['id'] for p in paths])],paths
    assert stem=='r2g3b-siren-flute-attacks'
    paths=deepcopy(d['delivery_paths']);ids=[p['id'] for p in paths]
    return [pkg('siren_flute','Siren Flute attachment pacification','CUSTOM_CONTROL','CUSTOM_ROUTED ADMISSION_GATED NO_STAGE_VALUE',None,'Binary target/navigation clearing over native timer; no HP amount.',ids[:2]),
      pkg('siren_bite','Siren animated bite','VANILLA_LIKE_EXTENDED','NUMERIC_SCALABLE VANILLA_ROUTED ADMISSION_GATED','Once at Siren.aiStep victim.hurt(mob_attack,ATTACK_DAMAGE).','Animation eligibility and ordinary hurt admission remain native.',ids[2:3]),
      pkg('siren_pull','Siren animated pull and hit','CUSTOM_CONTROL','COMPOSITE NUMERIC_SCALABLE CUSTOM_ROUTED ADMISSION_GATED','Once at Siren.aiStep pull victim.hurt(mob_attack,ATTACK_DAMAGE); movement/rotation receive no multiplier.','Independent control can occur even if hurt=false.',ids[3:])],paths

def fact_refs(stem,d,m):
    if stem=='r2g2b-frozen-dragons':keys=[k for k in d['facts'] if k not in {'closure','boundaries'}]
    else:keys=FACT_KEYS[m['id'].split(':',1)[1]]
    refs=[dict(file='iceandfire-'+stem+'.json',key=k,text=d['facts'][k]) for k in keys]
    if stem=='r2g6-cockatrice' and 'target_control' in keys:
        corrected=read_json(OUT/'iceandfire-r2g7-worm-cyclops.json')['facts']['shared_callback_clarification']
        refs.append(dict(file='iceandfire-r2g7-worm-cyclops.json',key='shared_callback_clarification',text=corrected))
    return refs

def implementation(d):
    # Index combat methods rather than copying every constructor, renderer and
    # utility method from the shared witnesses into every accepted row. Full
    # helper/parent/compat evidence remains in the immutable section references.
    refs=[]
    watched=defaultdict(set)
    for m in read_json(OUT/'iceandfire-combat-closure-census.json')['methods']:watched[m['entry']].add(m['method'])
    for ref in d['reference_files']:
        f=ref['file']
        if not f.startswith('native-evidence/') or f.endswith('iceandfire-foundation.json'):continue
        for w in read_json(OUT/f)['witnesses']:
            methods=sorted({m['name'] for m in w.get('methods',[])} & watched[w['entry']])
            if methods:
                refs.append(dict(evidence_file=f,witness_id=w['id'],entry=w['entry'],methods=methods))
    assert refs
    return unique(refs)

def build():
    sections={s:read_json(OUT/('iceandfire-'+s+'.json')) for s in STEMS}
    groups=defaultdict(list);origpaths={};pathgroups=defaultdict(set);dispositions=[];sectionmanifest=[];fixture_sets=[]
    for stem,d in sections.items():
        mechanics,paths=normalized_section(stem,d);impl=implementation(d)
        filename='iceandfire-'+stem+'.json'
        sectionmanifest.append(dict(file=filename,sha256=sha256(OUT/filename),original_package_field='mechanic_packages' if 'mechanic_packages' in d else 'normalized early schema',normalized_mechanics=len(mechanics),native_paths=len(paths)))
        for key in ['future_runtime_fixtures','future_fixtures','unexecuted_future_fixtures','payload_contracts']:
            if key in d:fixture_sets.append(dict(file=filename,key=key,contracts=deepcopy(d[key]),runtime_status='NOT_RUN'))
        for p in paths:
            assert p['id'] not in origpaths,p['id']
            origpaths[p['id']]=(stem,p,impl)
        for m in mechanics:
            targets=ALIASES.get(m['id'],[m['id']]);facts=fact_refs(stem,d,m)
            dispositions.append(dict(section=filename,original_id=m['id'],canonical_ids=targets,status='ALIASED_SOURCE_VARIANT' if targets!=[m['id']] else 'RETAINED_NATIVE_CONTRACT',reason='Same native primitive; source-specific amounts, eligibility and callbacks remain separate paths.' if targets!=[m['id']] else 'Distinct combat contract, including source-specific control/defense/resource behavior.'))
            for target in targets:
                member=deepcopy(m)
                if m['id']=='iaf:food_hazard':member['delivery_paths']=[p for p in m['delivery_paths'] if p.endswith('flesh_fire' if target=='iaf:native_ignition' else 'flesh_lightning')]
                groups[target].append(dict(section=filename,original=member,facts=facts,implementation=impl))
                for pid in member['delivery_paths']:pathgroups[pid].add(target)
    paths=[];fixtures=[]
    for pid,(stem,p,impl) in origpaths.items():
        assert pathgroups[pid],('Unmapped native path',pid)
        source=p.get('item_id',p.get('source',p.get('native_path',p.get('chain',p.get('native_result',pid)))))
        native_contract=deepcopy(p)
        controls=p.get('runtime_variants',p.get('required_variants',[]))
        row=dict(id=pid,mod_key='iceandfire',status='VERIFIED',inspection_status='VERIFIED',labels=p['labels'],effect_ids=sorted(pathgroups[pid]),primary_source=source,setup='Genuine native delivery only. '+str(p.get('admission',p.get('eligibility',p.get('native_path',p.get('chain',p.get('native_result',source)))))),implementation=impl,native_contract=native_contract,semantic_section='iceandfire-'+stem+'.json',fixture_controls=controls,source_case_ids=[pid],runtime_status='NOT_RUN')
        paths.append(row)
        fixtures.append(dict(path_id=pid,effect_ids=row['effect_ids'],primary_source=source,native_contract=native_contract,section_fixture_set=row['semantic_section'],controls=controls,runtime_status='NOT_RUN'))
    effects=[]
    for eid,members in groups.items():
        base=members[0]['original'];name=base['name'];classification=base['primary_classification'];point=base['single_scaling_point']
        if eid in CANONICAL:name,classification,point=CANONICAL[eid]
        categories=unique([x for member in members for x in member['original']['tno_categories']])
        facts=unique([f for member in members for f in member['facts']])
        variants=[dict(section=member['section'],original_package_id=member['original']['id'],native_contract=member['original'],fact_keys=[f['key'] for f in member['facts']]) for member in members]
        deliveries=[p['id'] for p in paths if eid in p['effect_ids']]
        registry=['iceandfire:frozen'] if eid=='iaf:frozen' else ['iceandfire:siren_charm'] if eid=='iaf:siren_song' else []
        scale=bool(point)
        behavior=[f['text'] for f in facts]
        stage_reason=base.get('stage_reason',base.get('combat_behavior','Native combat admission/control has no separate Stage value.'))
        components=[dict(primitive='NATIVE_AMOUNT' if scale else 'NATIVE_CONTROL_ADMISSION_RESOURCE',formula=point if scale else stage_reason,numerical_parameters={'source_variant_contracts':[v['section']+'#'+v['original_package_id'] for v in variants]},binary_parameters=['Preserve native eligibility, source identity, hook admission and hurt-return ordering from fact references.'],vanilla_relation=classification,tno_categories=categories,stage_scaling_needed=scale,single_scaling_point=point)]
        if scale and ('COMPOSITE' in categories or classification in {'CUSTOM_CONTROL','VANILLA_COMPOSITE'}):
            components.append(dict(primitive='UNSCALED_NATIVE_COMPANIONS',formula='Status durations/amplifiers, motion, counts, acquisition, resource/cooldown and binary admission retain native values; only the named amount boundary is a Stage candidate.',numerical_parameters={},binary_parameters=[],vanilla_relation='Native companions described in source contracts',stage_scaling_needed=False,single_scaling_point=None))
        effects.append(dict(id=eid,mod_key='iceandfire',display_name=name,human_summary=name+'; static installed-native contract, runtime untested.',inspection_status='VERIFIED',native_status='STATIC_VERIFIED',primary_classification=classification,classification_provisional=False,registry_ids=registry,tno_categories=categories,stage_scaling_needed=scale,single_scaling_point=point,stage_reason=stage_reason,actual_behavior=behavior,fact_references=[dict(file=f['file'],key=f['key']) for f in facts],components=components,implementation=unique([r for member in members for r in member['implementation']]),delivery_paths=deliveries,primary_test_source=next(p['primary_source'] for p in paths if p['id']==deliveries[0]),alternate_sources=unique([p['primary_source'] for p in paths if eid in p['effect_ids']]),source_parameter_variants=variants,closest_vanilla_equivalent=classification+'; exact native amount/control and eligibility in source contracts.',vanilla_similarities=['Inherited native HP/effect/heal admission applies only where the source contract actually delegates.'],vanilla_differences=behavior,compatibility_attribution='DIRECT_INSTALLED_COMPAT_AND_GENERIC_HOOKS_REVIEWED_STATIC_ONLY',compatibility_evidence=['iceandfire-r2g1-source-foundation.json','iceandfire-r2g10a-closure.json'],pending=[],unresolved_ambiguities=[],runtime_status='NOT_RUN'))
    counts=dict(normalized_input_packages=len(dispositions),native_cases=len(origpaths),final_mechanics=len(effects),final_deliveries=len(paths),aliased_input_packages=sum(r['status']=='ALIASED_SOURCE_VARIANT' for r in dispositions),excluded_combat_cases=0)
    manifest=dict(schema='tno.external_effects.iaf_promotion_map.v1',baseline=BASELINE,checkpoint=CP,starting_sha=START,sections=sectionmanifest,mechanic_dispositions=dispositions,path_dispositions=[dict(original_id=p['id'],canonical_id=p['id'],canonical_effect_ids=p['effect_ids'],status='RETAINED_NATIVE_DELIVERY') for p in paths],counts=counts,dedup_policy='Consolidate repeated native Poison, Regeneration, ignition, real lightning, inherited arrow amount and weapon bonus contracts; preserve every source-specific path. Cross-mod primitive normalization and source minimization remain R3.',normalization_note='Early Frozen/Siren schemas normalized from protected facts. Ice dragon HP is joined to existing elemental HP package; companion Slowness/MiningFatigue explicitly retained. R2g7 START_TRACKING_TAIL correction supersedes the R2g6 target-event label; archived evidence unchanged.')
    fixturematrix=dict(schema='tno.external_effects.iaf_future_fixtures.v1',baseline=BASELINE,checkpoint=CP,status='FUTURE_ONLY_NOT_RUN',fixtures=fixtures,section_fixture_sets=fixture_sets,note='One row per native delivery/control/defense contract, plus every protected named fixture and the three Frozen payload variants. This is coverage, not a globally minimized test count. No synthetic event or forced unsupported enchantment is a legitimate positive control.',runtime_tests=0,**boundary_flags())
    review=dict(schema='tno.external_effects.mod_review.v1',baseline=BASELINE,mod_key='iceandfire',checkpoint=CP,starting_sha=START,status='COMPLETE',decision='ICE_AND_FIRE_COMBAT_SEMANTIC_REVIEW_COMPLETE',scope='Installed IceAndFireCE beta15 combat-significant static review complete. Cosmetic, acquisition, utility and storage excluded briefly. Whole-pack runtime compatibility and Stage implementation are not claimed.',semantic_discovery_complete=True,special_damage_discovery_complete=True,source_mapping_complete=True,delivery_mapping_complete=True,semantic_effect_count=len(effects),effects=effects,paths=paths,unresolved_native_ambiguities=[],remaining_native_ambiguities=[],review_required=[],classification_counts=dict(Counter(e['primary_classification'] for e in effects)),named_native_effects=['iceandfire:frozen','iceandfire:siren_charm'],promotion_manifest='iceandfire-final-promotion-map.json',future_runtime_fixture_matrix='iceandfire-future-runtime-fixtures.json',whole_source_closure='iceandfire-r2g10a-closure.json',exact_next_task=NEXT,runtime_tests=0,**boundary_flags())
    review['historical_wording_note']='Protected source facts retain their original subsection chronology. References to later Dragon explosion or Siren attack review are closed by R2g5a and R2g3b respectively. R2g6 target_control names the onLivingSetTarget method; the accompanying R2g7 correction proves its actual START_TRACKING_TAIL registration, not a target-change event. Runtime fixtures remain unexecuted.'
    return review,manifest,fixturematrix

def save():
    review,manifest,fixtures=build()
    write_json(OUT/'mod-reviews/iceandfire.json',review);write_json(OUT/'iceandfire-final-promotion-map.json',manifest);write_json(OUT/'iceandfire-future-runtime-fixtures.json',fixtures)
    refresh(CP)
    d=read_json(OUT/'behavior-primitives.json');d['primitives']=[p for p in d['primitives'] if p['mod_key']!='iceandfire']
    for e in review['effects']:
        for i,c in enumerate(e['components']):d['primitives'].append(dict(c,id=e['id']+':component:'+str(i),effect_id=e['id'],mod_key='iceandfire',status='VERIFIED_PER_MOD',implementation=e['implementation'],source_case_paths=e['delivery_paths']))
    d.update(checkpoint=CP,note='Per-mod component instances; R3 cross-mod primitive normalization and fixture minimization remain pending.');write_json(OUT/'behavior-primitives.json',d)
    for name in ['effect-catalog.json','effect-sources.json','delivery-path-matrix.json','vanilla-comparison.json','behavior-primitives.json']:
        d=read_json(OUT/name);d.pop('unfinished_review',None);d['last_completed_mod']='iceandfire';write_json(OUT/name,d)
    d=read_json(OUT/'research-decision.json');d.update(checkpoint=CP,next_task=NEXT,latest_iceandfire_subsection_decision=review['decision'],save_mode=False,save_reason=None);d['checkpoints']['R2g10a-combat-closure-complete']=START;d['checkpoints'][CP]='Self: exact SHA from commit/live verification.';write_json(OUT/'research-decision.json',d)
    lines=['# Ice & Fire combat owner table — COMPLETE','',f"R2g10b promotes {len(review['effects'])} combat packages and {len(review['paths'])} native delivery/control/defense contracts. Installed-native static evidence only; all runtime fixtures remain unexecuted.",'','Gorgon conversion, ordinary HP damage, Poison, and statue destruction remain separate mechanics. Frozen/Siren accepted work is reused. Shared native ignition, Poison, Regeneration, lightning and arrow HP contracts are consolidated while retaining each native source path.','', '| Combat package | TNO category | Single Stage amount boundary / no-value reason |','|---|---|---|']
    for e in review['effects']:
        lines.append('| '+e['display_name']+' | '+', '.join(e['tno_categories'])+' | '+(e['single_scaling_point'] or e['stage_reason']).replace('|',' / ')+' |')
    lines+=['','## Runtime priorities','', '- Gorgon gaze versus Head; Player versus nonplayer; accepted/rejected lethal hurt and statue ordering; blindfold/LOS/native compat admission.', '- ColdNullification versus Frozen companion effects; Siren map control versus marker immunity; attachment Post tick versus passenger ticks.', '- Dragon source holder/direct/causing identity, especially ridden Lightning manager using ICE; independent direct/area/status/explosion attempts and native Tamable collision guard.', '- Sea Serpent live-owner bubble gate and Dread Lich skull origin must be observed through genuine native AI; absence is not permission to inject a payload.', '- Installed Uranus armor amount callback targets Player absorption. Lightning Dragonsteel cancellation uses a separate functioning Architectury incoming-damage hook.', '- Ordinary versus custom weapon/arrow factories, real bolt versus cosmetic chain, accepted-hit payload gates, native resource persistence and whole-pack event cancellation.','', '[Every native path and preserved fixture](iceandfire-future-runtime-fixtures.json); [total promotion mapping](iceandfire-final-promotion-map.json); [accepted mechanic contracts](mod-reviews/iceandfire.json).','', 'Short exclusions: ordinary crafting/acquisition, worldgen setup, utility/storage/transport without combat callbacks, cosmetics/rendering/animation-only branches. Dormant Dread necromancy and unregistered Queen are explicitly excluded as active native deliveries; Myrmex implementation is absent in this installed artifact.','', 'Validation: deterministic promotion, bytecode/reference witnesses, all five accepted views, exact preservation of prior accepted mods and historical research, five tooling tests, Git scope/diff checks. No runtime, L2, Stage, production, Phase6 or Phase7 changes.','', 'Exact next task: '+NEXT,'']
    (OUT/'iceandfire-final-owner-table.md').write_text('\n'.join(lines),encoding='utf-8')
    main=ROOT/'docs/external-effects-catalog-research.md';s=main.read_text(encoding='utf-8');heading='## R2g10b — Ice & Fire combat catalog COMPLETE'
    if heading not in s:s+='\n'+heading+'\n\n'+str(len(review['effects']))+' reviewed combat packages and '+str(len(review['paths']))+' native source/control/defense contracts promoted after explicit deduplication; no runtime compatibility certification. [Owner table, Stage points and next task](benchmarks/external-effects-catalog/iceandfire-final-owner-table.md).\n'
    main.write_text(s,encoding='utf-8')
    print(json.dumps(manifest['counts'],indent=2))

if __name__=='__main__':save()
