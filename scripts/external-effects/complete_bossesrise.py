"""Promote protected Bosses Rise contracts; retain source variants and additive corrections."""
from copy import deepcopy
from collections import defaultdict,Counter
from catalog_common import *
from assemble_batch import refresh
from complete_eternalstarlight import unique

def write_json(path,obj):
    # Windows can briefly refuse a second open after refresh wrote these views.
    # Retry only the observed transient open error; preserve every other failure.
    import time
    from catalog_common import write_json as write_once
    for attempt in range(5):
        try:return write_once(path,obj)
        except OSError as error:
            if error.errno!=22 or attempt==4:raise
            time.sleep(.1)

KEY='block_factorys_bosses'
START='b5a3d5806403dab92c2bc6dcf1a533a0c6c30875'
CP='R2i9b-bossesrise-complete'
NEXT='R2j1: Bosses of Mass Destruction installed-native combat source foundation, then bounded combat family review, on this same side-research branch. Continue automatically while quota is healthy under the existing user instruction. Eternal Starlight and Bosses Rise are complete; cross-mod R3 normalization/source minimization remains pending. No runtime boss matrix, L2, Stage, production, Phase6 reopening or Phase7.'
STEMS=['r2i2a-roll-admission','r2i2b-shared-combat','r2i3a-knight-defense','r2i3b-knight-offense','r2i4-infernal-dragon','r2i5a-yeti-defense','r2i5b-yeti-offense','r2i6-sandworm','r2i7a-kraken-defense','r2i7b-kraken-offense','r2i8a-gauntlets','r2i8b-tentacle-trident','r2i8c-equipment','r2i9a-closure']
FACT_KEYS={}
for line in '''
roll_resource=delivery state recharge other_gate_and_persistence
roll_movement=movement state
roll_admission=damage_admission effect_admission projectile_identity
roll_freeze_write=freeze
shared_boss_attack=attack_amount melee_geometry_and_return
shared_death=legacy_death_order state_death_order defeat_sources
knight_spawn_control=legacy_procedures
part_admission=parts
owner_targeting=ownership
raw_displacement=displacement
knight_stacks=admission_order stack_vs_hp stuck_delivery
knight_mark=mark_creation mark_hit
knight_hp_gates=hp_gates phases_and_death
knight_lifecycle=native_initialization timing_and_intro phases_and_death
knight_traits=traits_and_persistence
knight_melee=live_scope melee
knight_ring=combo_ring
sword_wave=wave_delivery wave_payload
shockwave_arrow shockwave_area=shockwave
rift_damage rift_emitter=rift
arena_mob_melee arena_mob_timed arena_mob_control=arena_mobs wither_and_defense
native_wither=wither_and_defense
knight_slow=wave_payload shockwave rift
dragon_admission=admission traits_and_stats phase_lifecycle
dragon_cinematic=cinematic_and_death
dragon_melee dragon_melee_push=melee
blazing_arrow=fireball_delivery fireball_secondaries
blazing_area_delivery=fireball_secondaries fire_area_and_explosion
blazing_explosion fire_area=fire_area_and_explosion
dragon_breath_magic=breath
dragon_fire_contact dragon_burning=burning_and_tags breath fireball_secondaries
dragon_guard_ai dragon_guard_timed dragon_guard_control=guardians
yeti_admission=admission_order projectile_reduction hit_lockout
yeti_death=raw_lethal_branch dormant_death_counter
yeti_enrage=enrage_and_ultimate state_dispatch
yeti_traits=initialization traits_persistence
yeti_melee=melee
yeti_melee_control=melee_control
yeti_ice_delivery=ice_producers burst_geometry
ice_spike_damage=spike_admission_and_payload
ice_cluster_damage ice_cluster_resource=spike_admission_and_payload cluster_resource_and_reload
yeti_barrage_aura=barrage_aura
ice_spike_projectile=projectile_delivery
ice_spike_touch=projectile_player_touch
glacial_shove=glacial_shove
yeti_passive_freeze=freeze_counter_vs_HP
sandworm_segments=multipart_admission retaliation
sandworm_defenses=defenses underground_and_persistence
sandworm_phase=phase_death state_delivery
sandworm_contact=body_geometry
sandworm_body=body_attack_schedule body_geometry
sandworm_column=column_producers column_payload
sandworm_spit sandworm_poison_delivery=spit_and_hazard
sandworm_poison_tick=poison_effect
sandworm_screech=screech
kraken_admission=incoming_order hidden_admission
kraken_knockdown=knockdown
kraken_phase=phase_initialization cinematic_control
kraken_tentacle_resources=tentacle_resources tentacle_lifetime
kraken_death=death_sequence
kraken_smash=goal_admission_timing smash_geometry
kraken_crate_impact=crate_launch crate_impact
kraken_crate_explosion=crate_impact explosion_sources explosion_payload
kraken_runaway=runaway_control
cannon_operation=cannon_delivery
cannon_defense=cannon_object_admission
cannon_impact=cannon_impact
cannon_explosion=cannon_impact explosion_sources explosion_payload
pirate_melee pirate_control=pirate_melee
pirate_crossbow=pirate_crossbow
ice_gauntlet_control=ice_native_use ice_wave ice_leap ice_shards
ice_gauntlet_landing=ice_leap
sandworm_gauntlet_control=sandworm_modes sandworm_quake sandworm_barrage
undying_whip=undying_whip
undying_summon=undying_summon
ghost_tentacle_melee=ghost_attack
ghost_tentacle_control=ghost_attack ghost_lifetime
kraken_trident_delivery=trident_real_throw trident_persistence_factory
kraken_trident_hit=trident_direct_hit
kraken_trident_area=trident_area
dragon_armor_buffs=armor_buffs ordinary_equipment
dragon_armor_trigger=post_admission boots_ignition chest_retaliation
dragon_boots_explosion=post_admission boots_explosion
pirate_saber_summon=pirate_saber
'''.strip().splitlines():
    names,keys=line.split('=')
    for n in names.split():FACT_KEYS['br:'+n]=keys.split()

ALIAS_GROUPS={
 'shared_boss_attack':'knight_melee dragon_melee yeti_melee sandworm_body',
 'native_arrow_hp':'shockwave_arrow blazing_arrow sandworm_spit pirate_crossbow',
 'native_explosion_hp':'blazing_explosion kraken_crate_explosion cannon_explosion dragon_boots_explosion',
 'native_AI_melee':'arena_mob_melee dragon_guard_ai',
 'native_timed_melee':'arena_mob_timed dragon_guard_timed pirate_melee ghost_tentacle_melee',
}
ALIASES={'br:'+old:'br:'+new for new,olds in ALIAS_GROUPS.items() for old in olds.split()}
CANONICAL={
 'native_arrow_hp':('Native arrow HP with distinct real producers','VANILLA_LIKE_EXTENDED','Once at final native AbstractArrow hurt after speed/base/critical/enchantment calculation, retaining each native projectile/weapon owner and eligibility. Do not also scale baseDamage or source equipment attributes.'),
 'native_explosion_hp':('Native explosion HP with distinct producers and pass counts','VANILLA_COMPOSITE','Once at each actual native Explosion.explode per-victim hurt after exposure/calculator, retaining native explosion/player_explosion source and the boots repeated-pass lifecycle; never scale radius or wrapper plus final amount.'),
 'native_AI_melee':('Native AI melee with explicit timer, range and LOS admission','VANILLA_LIKE_EXTENDED','Once at inherited Mob.doHurtTarget final native mob_attack after attributes/enchantments. Keep anonymous canPerformAttack and separate timed hit admission.'),
 'native_timed_melee':('Native animation-timed summon and guardian melee','VANILLA_LIKE_EXTENDED','Once at each actual timed native mob_attack hurt using current attacker ATTACK_DAMAGE. Preserve own-source identity, per-class ranges/block gates and independent status/control; do not scale attribute too.'),
}
EXTENSION_FACTS={
 'r2i8a-gauntlets':{'ice_spike_damage':['ice_wave','ice_leap'],'ice_cluster_damage':['ice_wave','ice_leap'],'ice_spike_projectile':['ice_shards'],'ice_spike_touch':['ice_shards'],'yeti_passive_freeze':['ice_native_use','ice_leap'],'sandworm_column':['sandworm_quake'],'sandworm_spit':['sandworm_barrage','correction_and_reuse'],'sandworm_poison_delivery':['sandworm_barrage'],'sandworm_poison_tick':['sandworm_barrage']},
 'r2i8c-equipment':{'dragon_burning':['boots_ignition','chest_retaliation'],'blazing_arrow':['chest_retaliation'],'blazing_area_delivery':['chest_retaliation'],'blazing_explosion':['chest_retaliation'],'fire_area':['chest_retaliation'],'sword_wave':['knight_sword'],'knight_slow':['knight_sword'],'pirate_melee':['pirate_saber'],'pirate_crossbow':['pirate_saber'],'pirate_control':['pirate_saber']}
}

def fact_text(file,key):
    value=read_json(OUT/file)['facts'][key]
    if file=='bossesrise-r2i6-sandworm.json' and key=='spit_and_hazard':
        correction=read_json(OUT/'bossesrise-r2i8a-gauntlets.json')['semantic_corrections'][0]
        prefix=value.split(correction['superseded_text'])[0];assert prefix!=value
        return prefix+correction['replacement']+' Its native input/cost values are completed in R2i8a.'
    return value

def implementation(d):
    refs=[]
    own=next(r['file'] for r in d['reference_files'] if r['file'].startswith('native-evidence/'))
    watched=defaultdict(set)
    for row in read_json(OUT/'bossesrise-source-census.json')['watched_methods']:watched[row['entry']].add(row['method'])
    for w in read_json(OUT/own)['witnesses']:
        names={m['name'] for m in w.get('methods',[])}
        selected=names & watched[w['entry']]
        selected|={n for n in names if n in {'hurt','canPerformAttack','registerGoals','tick','baseTick','use','releaseUsing','finishUsingItem','onUseTick','getOwner','canUse','start','canAttack','getDefaultAttributeModifiers','createAttributesBuilder','<init>','<clinit>'}}
        if not selected:selected=names
        if selected:refs.append(dict(evidence_file=own,witness_id=w['id'],entry=w['entry'],methods=sorted(selected)))
    assert refs
    return refs

def source_coverage(sections,paths):
    census=read_json(OUT/'bossesrise-source-census.json');index=defaultdict(list);semantic=defaultdict(list)
    for stem,d in sections.items():
        own=next(r['file'] for r in d['reference_files'] if r['file'].startswith('native-evidence/'));semantic[own].append('bossesrise-'+stem+'.json')
    for f in sorted((OUT/'native-evidence').glob('bossesrise-*.json')):
        for w in read_json(f)['witnesses']:
            for m in w.get('methods',[]):index[(w['entry'],m['name'],m['descriptor'])].append(dict(evidence_file='native-evidence/'+f.name,witness_id=w['id'],entry=w['entry'],methods=[m['name']]))
    def refs(row):
        impl=index[(row['entry'],row['method'],row['descriptor'])];assert impl,row
        return dict(implementation=impl,semantic_sections=unique([s for r in impl for s in semantic[r['evidence_file']]]) or ['bossesrise-r2i9a-closure.json'])
    excluded=['/client/','/configuration/ClientConfiguration','/geckolib/ServerAnimationPlayer','/util/BossHandling$ClientHandler','/entity/decoration/AnchorEntity','/entity/decoration/CageEntity','/entity/decoration/CratePileEntity','/entity/decoration/PileOfBonesEntity','/event/StructureDestructionEvents']
    watched=[dict(**row,disposition='SHORT_NONCOMBAT_EXCLUSION' if any(v in row['entry'] for v in excluded) else 'REVIEWED_COMBAT_OR_SHARED_NATIVE_HELPER',**refs(row)) for row in census['watched_methods']]
    types=[]
    for decl in read_json(OUT/'bossesrise-damage-tags.json')['declarations']:
        short=decl['id'].split(':')[1];upper=short.upper();callers=[]
        for row in census['custom_damage_key_methods']:
            if not any('.'+upper+'L' in str(h['operand']) for h in row['hits']):continue
            producer=row['method'] in ['attackEntityWithSlam','onHitEntity'];data='/data/' in row['entry']
            callers.append(dict(entry=row['entry'],method=row['method'],descriptor=row['descriptor'],kind='ACTUAL_NATIVE_HURT_PRODUCER' if producer else 'DATAGEN_NOT_DELIVERY' if data else 'ADMISSION_ONLY_NOT_DELIVERY',**({} if data else refs(row))))
        assert sum(x['kind']=='ACTUAL_NATIVE_HURT_PRODUCER' for x in callers)==1
        eid='br:cannon_impact' if short=='cannonball_hit' else 'br:kraken_smash'
        field='cannon_impact' if short=='cannonball_hit' else 'smash_geometry'
        types.append(dict(**decl,disposition='USED',callers=callers,requested_amount_formula='10 native impact' if short=='cannonball_hit' else 'ATTACK_DAMAGE * (heavy1/light.5) * clamp(geometryModifier,.5,1)',direct_entity='CannonballEntity' if short=='cannonball_hit' else 'KrakenTentacleEntity',causing_entity='native projectile owner, null when genuinely unresolved' if short=='cannonball_hit' else 'native resolved Ownable owner, normally Kraken; null when genuinely unresolved',mechanic_ids=[eid],delivery_paths=[p['id'] for p in paths if eid in p['effect_ids']],armor_behavior='BYPASSES_ARMOR',shield_behavior='BYPASSES_SHIELD',resistance_behavior='Native Resistance retained; no bypass_resistance',protection_behavior='Native enchantment/protection retained; no bypass_enchantments',hurt_return_dependencies_and_secondary_callbacks=sections['r2i7b-kraken-offense']['facts'][field],scoped_physical_magic_tags='Neither neoforge:is_physical nor neoforge:is_magic in pinned raw Minecraft/loader/mod contributions; generic pack hooks/tags unmeasured.'))
    effects=[dict(**row,disposition='REVIEWED_NATIVE_EFFECT_REFERENCE',**refs(row)) for row in census['native_effect_reference_methods']]
    return dict(schema='tno.external_effects.bossesrise_total_source_coverage.v1',baseline=BASELINE,checkpoint=CP,jar_sha256=census['jar_sha256'],parsed_classes=802,watched_methods=watched,custom_damage_types=types,custom_damage_key_method_count=6,actual_custom_hurt_producers=2,native_effect_reference_methods=effects,custom_effect_registry_candidates=[],whole_class_inventory='bossesrise-source-census.json',direct_compat='bossesrise-direct-compat-census.json',scope='All native watched methods, custom source-key and status references have explicit dispositions. Inherited and source-delivery semantics come from protected family reviews; static inventory alone is not coverage proof.',runtime_tests=0)

def build():
    sections={s:read_json(OUT/('bossesrise-'+s+'.json')) for s in STEMS};groups=defaultdict(list);original_paths={};pathgroups=defaultdict(set);dispositions=[];manifest_sections=[];fixture_sets=[]
    for stem,d in sections.items():
        filename='bossesrise-'+stem+'.json';impl=implementation(d)
        manifest_sections.append(dict(file=filename,sha256=sha256(OUT/filename),packages=len(d['mechanic_packages']),paths=len(d['delivery_paths'])))
        fixture_sets.append(dict(file=filename,contracts=d['unexecuted_future_fixtures'],runtime_status='NOT_RUN'))
        for p in d['delivery_paths']:
            assert p['id'] not in original_paths;p=deepcopy(p)
            # Protected Roll fixture was written before the shove family review; its payload is now closed.
            if p['id']=='br:roll:glacial_gate':p['native_path']='Yeti native GlacialShove skips invulnerable rolling ServerPlayer; actual movement-only payload reviewed in R2i5b.'
            original_paths[p['id']]=(filename,p,impl)
        for m in d['mechanic_packages']:
            mid=m['id'];target=ALIASES.get(mid,mid);keys=EXTENSION_FACTS[stem][mid.split(':')[1]] if m.get('extends_existing_package') else FACT_KEYS[mid]
            facts=[dict(file=filename,key=k,text=fact_text(filename,k)) for k in keys]
            groups[target].append(dict(section=filename,original=deepcopy(m),facts=facts,implementation=impl))
            dispositions.append(dict(section=filename,original_id=mid,canonical_ids=[target],status='EXTENDS_REVIEWED_PACKAGE' if m.get('extends_existing_package') else 'ALIASED_NATIVE_PRIMITIVE' if target!=mid else 'RETAINED_NATIVE_CONTRACT'))
            for pid in m['delivery_paths']:pathgroups[pid].add(target)
    paths=[];fixtures=[]
    for pid,(file,p,impl) in original_paths.items():
        assert pathgroups[pid] and set(p['labels'])<=set(DELIVERIES),pid
        source=p['native_path'];controls=p.get('runtime_variants',[])
        row=dict(id=pid,mod_key=KEY,status='VERIFIED',inspection_status='VERIFIED',labels=p['labels'],effect_ids=sorted(pathgroups[pid]),primary_source=source,setup='Genuine enclosing native delivery: '+source,implementation=impl,native_contract=p,semantic_section=file,fixture_controls=controls,source_case_ids=[pid],runtime_status='NOT_RUN')
        paths.append(row);fixtures.append(dict(path_id=pid,effect_ids=row['effect_ids'],primary_source=source,native_contract=p,section_fixture_set=file,controls=controls,runtime_status='NOT_RUN'))
    effects=[]
    for eid,members in groups.items():
        base=members[0]['original'];name,cl,point=CANONICAL.get(eid.split(':')[1],(base['name'],base['primary_classification'],base['single_scaling_point']))
        scale=bool(point);categories=unique([c for m in members for c in m['original']['tno_categories']]);categories=[c for c in categories if c not in {'NUMERIC_SCALABLE','NO_STAGE_VALUE'}]+['NUMERIC_SCALABLE' if scale else 'NO_STAGE_VALUE']
        facts=unique([f for m in members for f in m['facts']]);variants=[dict(section=m['section'],original_package_id=m['original']['id'],native_contract=m['original'],fact_keys=[f['key'] for f in m['facts']]) for m in members]
        closure_key='ai_admission' if eid in ['br:native_AI_melee','br:native_timed_melee'] else 'ownership' if eid=='br:owner_targeting' else None
        if closure_key:facts.append(dict(file='bossesrise-r2i9a-closure.json',key=closure_key,text=sections['r2i9a-closure']['facts'][closure_key]))
        ids=[p['id'] for p in paths if eid in p['effect_ids']];reason=base.get('stage_reason','Only native final amount once; control and admission unchanged.')
        components=[dict(primitive='NATIVE_FINAL_AMOUNT' if scale else 'NATIVE_CONTROL_ADMISSION_RESOURCE',formula=point or reason,numerical_parameters={'source_variant_contracts':[v['section']+'#'+v['original_package_id'] for v in variants]},binary_parameters=['Preserve native source, owner, immunity, return value and callback ordering.'],vanilla_relation=cl,tno_categories=categories,stage_scaling_needed=scale,single_scaling_point=point)]
        if scale and 'COMPOSITE' in categories:components.append(dict(primitive='UNSCALED_NATIVE_COMPANIONS',formula='Native counters/resources/attributes/radius/cadence/control and eligibility receive no duplicate Stage multiplier.',numerical_parameters={},binary_parameters=[],vanilla_relation='Source-specific native companion contract',stage_scaling_needed=False,single_scaling_point=None))
        behavior=[f['text'] for f in facts];refs=unique([r for m in members for r in m['implementation']])
        if closure_key:refs+= [ref for ref in implementation(sections['r2i9a-closure']) if any(n in ref['entry'] for n in (['OwnableByAllEntity'] if closure_key=='ownership' else ['SoulSkeletonEntity$1','SoulKnightWitherSkeletonEntity$1','GuardSwordEntity$1','GuardFireballEntity$1']))]
        effects.append(dict(id=eid,mod_key=KEY,display_name=name,human_summary=name+'; static native semantics, runtime untested.',inspection_status='VERIFIED',native_status='STATIC_VERIFIED',primary_classification=cl,classification_provisional=False,registry_ids=[],tno_categories=categories,stage_scaling_needed=scale,single_scaling_point=point,stage_reason=reason,actual_behavior=behavior,fact_references=[dict(file=f['file'],key=f['key'],correction_file='bossesrise-r2i8a-gauntlets.json' if f['file']=='bossesrise-r2i6-sandworm.json' and f['key']=='spit_and_hazard' else None) for f in facts],components=components,implementation=refs,delivery_paths=ids,primary_test_source=next(p['primary_source'] for p in paths if p['id']==ids[0]),alternate_sources=unique([p['primary_source'] for p in paths if eid in p['effect_ids']]),source_parameter_variants=variants,closest_vanilla_equivalent=cl+'; exact delegated native callbacks retained in contracts.',vanilla_similarities=['Native source/hurt/effect processing where actually delegated.'],vanilla_differences=behavior,compatibility_attribution='SCOPED_EXPLICIT_NAME_SCAN_AND_GENERIC_HOOKS_STATIC_ONLY',compatibility_evidence=['bossesrise-r2i1-source-foundation.json','bossesrise-r2i9a-closure.json'],pending=[],unresolved_ambiguities=[],runtime_status='NOT_RUN'))
    counts=dict(input_packages=len(dispositions),native_cases=len(paths),final_mechanics=len(effects),final_deliveries=len(paths),aliased_input_packages=sum(x['status']=='ALIASED_NATIVE_PRIMITIVE' for x in dispositions),delivery_extensions=sum(x['status']=='EXTENDS_REVIEWED_PACKAGE' for x in dispositions),excluded_combat_cases=0)
    future_review=unique([v for d in sections.values() for v in d.get('review_required',[])])
    manifest=dict(schema='tno.external_effects.bossesrise_promotion_map.v1',baseline=BASELINE,checkpoint=CP,starting_sha=START,sections=manifest_sections,mechanic_dispositions=dispositions,path_dispositions=[dict(original_id=p['id'],canonical_id=p['id'],canonical_effect_ids=p['effect_ids']) for p in paths],counts=counts,semantic_corrections=sections['r2i8a-gauntlets']['semantic_corrections'],dedup_policy='Shared boss helper, native arrows, actual native explosions, native AI melee and timed melee consolidated. Equipment extends existing hazard packages. Distinct explicit explosion-typed HP, trident, freeze direct/passive, control, resource and defense contracts remain separate. Every native delivery retained; no cross-mod R3 claim.')
    matrix=dict(schema='tno.external_effects.bossesrise_future_fixtures.v1',baseline=BASELINE,checkpoint=CP,status='FUTURE_ONLY_NOT_RUN',fixtures=fixtures,section_fixture_sets=fixture_sets,review_required=future_review,runtime_tests=0,note='Cases include shared admission/helper contracts: exercise through genuine enclosing native producers, never forced helper/synthetic event/source. Fixture count is not a runtime test count. Origin policy and current native bugs remain review-required before implementation.',**boundary_flags())
    review=dict(schema='tno.external_effects.mod_review.v1',baseline=BASELINE,mod_key=KEY,checkpoint=CP,starting_sha=START,status='COMPLETE',decision='BOSSES_RISE_COMBAT_SEMANTIC_REVIEW_COMPLETE',scope='Installed Bosses Rise2.1.2 combat-significant static semantics complete. Two native custom DamageTypes mapped; runtime compatibility/Stage implementation untested.',semantic_discovery_complete=True,special_damage_discovery_complete=True,source_mapping_complete=True,delivery_mapping_complete=True,effects=effects,paths=paths,semantic_effect_count=len(effects),unresolved_native_ambiguities=[],remaining_native_ambiguities=[],review_required=future_review,review_required_scope='Future runtime/integration decisions, not unresolved native semantics; kept explicitly visible.',classification_counts=dict(Counter(e['primary_classification'] for e in effects)),promotion_manifest='bossesrise-final-promotion-map.json',future_runtime_fixture_matrix='bossesrise-future-runtime-fixtures.json',whole_source_closure='bossesrise-total-source-coverage.json',exact_next_task=NEXT,runtime_tests=0,**boundary_flags())
    return review,manifest,matrix,source_coverage(sections,paths)

def save():
    r,m,f,c=build()
    for name,obj in [('mod-reviews/'+KEY+'.json',r),('bossesrise-final-promotion-map.json',m),('bossesrise-future-runtime-fixtures.json',f),('bossesrise-total-source-coverage.json',c)]:write_json(OUT/name,obj)
    import assemble_batch
    original_writer=assemble_batch.write_json
    try:
        assemble_batch.write_json=write_json
        refresh(CP)
    finally:assemble_batch.write_json=original_writer
    p=read_json(OUT/'behavior-primitives.json');p['primitives']=[x for x in p['primitives'] if x['mod_key']!=KEY]
    for e in r['effects']:
        for i,component in enumerate(e['components']):p['primitives'].append(dict(component,id=e['id']+':component:'+str(i),effect_id=e['id'],mod_key=KEY,status='VERIFIED_PER_MOD',implementation=e['implementation'],source_case_paths=e['delivery_paths']))
    p.update(checkpoint=CP);write_json(OUT/'behavior-primitives.json',p)
    for name in ['effect-catalog.json','effect-sources.json','delivery-path-matrix.json','vanilla-comparison.json','behavior-primitives.json']:
        o=read_json(OUT/name);o.pop('unfinished_review',None);o['last_completed_mod']=KEY;write_json(OUT/name,o)
    o=read_json(OUT/'research-decision.json');o.update(checkpoint=CP,next_task=NEXT,latest_bossesrise_decision=r['decision'],save_mode=False,save_reason=None);o['checkpoints']['R2i9a-bossesrise-combat-closure-complete']=START;o['checkpoints'][CP]='Self: exact SHA from commit/live verification.';write_json(OUT/'research-decision.json',o)
    lines=['# Bosses Rise combat owner table — COMPLETE','',f"{len(r['effects'])} deduplicated combat packages; {len(r['paths'])} native source/control/admission paths from {m['counts']['input_packages']} protected input packages. Static review only; no runtime tests.",'','Both custom DamageTypes are USED: cannonball_hit and kraken_tentacle_smash. All157 watched methods,18 native status references and6 source-key references have dispositions. Stage points identify future final native numeric requests only; production is unchanged.','', '| Mechanic | TNO classification | Single candidate Stage point / no-value reason |','|---|---|---|']
    for e in r['effects']:lines.append('| '+e['display_name']+' | '+', '.join(e['tno_categories'])+' | '+str(e['single_scaling_point'] or e['stage_reason']).replace('|',' / ')+' |')
    lines+=['','[Complete contracts](mod-reviews/block_factorys_bosses.json), [native paths and future fixtures](bossesrise-future-runtime-fixtures.json), [source coverage](bossesrise-total-source-coverage.json), [deduplication and additive correction map](bossesrise-final-promotion-map.json).','','Compatibility priorities: Roll rejects damage/effects/frozen writes; boss phase/resources and direct-versus-causing predicates; native failed-hurt independent control/hazard callbacks; lost owner/save state; distinct active/passive freeze and native Poison eligibility; owned cannon splash uses player_explosion; boots explicitly repeat Explosion.explode and still invoke that pass after start cancellation. These are native static findings, not measured Tensura/L2 results.','','Future integration review remains required:']
    lines+=['- '+x for x in r['review_required']]
    lines+=['','Short exclusions: rendering/animation, ordinary attributes/melee, acquisition/food/repair, breakable decoration and structure/worldgen helpers without combat HP/status callbacks. Prior source-aid static-shoot wording is corrected in promoted contracts without rewriting history.','','Exact next task: '+NEXT,'']
    (OUT/'bossesrise-final-owner-table.md').write_text('\n'.join(lines),encoding='utf-8')
    main=ROOT/'docs/external-effects-catalog-research.md';s=main.read_text(encoding='utf-8');heading='## R2i9b — Bosses Rise combat catalog COMPLETE'
    if heading not in s:s+='\n'+heading+'\n\n'+f"{len(r['effects'])} deduplicated packages, {len(r['paths'])} native paths and both custom DamageTypes mapped. Static semantics complete; future integration reviews remain explicit. [Owner table and next task](benchmarks/external-effects-catalog/bossesrise-final-owner-table.md).\n"
    main.write_text(s,encoding='utf-8');print(json.dumps(m['counts'],indent=2))
if __name__=='__main__':save()
