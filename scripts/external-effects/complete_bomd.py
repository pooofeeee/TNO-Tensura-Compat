"""Promote protected BOMD native contracts; retain every source case and future fixture."""
from copy import deepcopy
from collections import defaultdict,Counter
from catalog_common import *
from bomd_combat_common import write_json,refresh_safe
from complete_eternalstarlight import unique

KEY='bosses_of_mass_destruction'
START='0c883899d7458e7ce6cc90ccf3349d30be3725a4'
CP='R2j8-bomd-complete'
NEXT='R2k1: Cataclysm installed-native combat source foundation, then bounded combat-significant status/admission and family review. Reuse completed mod contracts; continue automatically while quota healthy. Cross-mod R3/source minimization remains pending. No runtime boss matrix, L2 testing, Stage, production, Phase6 reopening or Phase7.'
STEMS=['r2j2-shared-admission','r2j3-night-lich','r2j4-obsidilith','r2j5-gauntlet','r2j6-void-blossom','r2j7-equipment']
ALIASES={'bomd:lich_missile':'bomd:native_thrown','bomd:blossom_thrown':'bomd:native_thrown','bomd:rift_damage':'bomd:shield_piercing_hp','bomd:blossom_spikes_hp':'bomd:shield_piercing_hp','bomd:summon_melee':'bomd:native_mob_melee','bomd:gauntlet_melee':'bomd:native_mob_melee'}
PATH_ALIASES={'bomd:blossom:idle_heal':'bomd:shared:blossom_idle_heal'}
CANONICAL={
 'native_thrown':('Native owner-attribute thrown damage','VANILLA_LIKE_EXTENDED','Once at final native projectile entityHit hurt amount after current-owner attribute selection; preserve separate missile/spore/petal predicates and secondaries.'),
 'shield_piercing_hp':('Native shield-piercing ground damage','CUSTOM_DAMAGE','Once at final native hurt amount after the actual caller attribute formula. Preserve exact-key native blocking override and spore captured-amount/current-source owner split.'),
 'native_mob_melee':('Native Mob.doHurtTarget melee','VANILLA_LIKE_EXTENDED','Once at native Mob.doHurtTarget final hurt amount after native attributes/enchantments. Keep owned Gauntlet and unowned Phantom identities, laser modifier and independent motion native.'),
 'native_explosion':('Native explosions and radius-modified delivery','VANILLA_LIKE_EXTENDED','Once at originating native Explosion per-victim final hurt amount after exposure/calculator. Preserve source-null or native entity attribution, Monolith radius, fire and independent motion; no wrapper/radius duplicate multiplier.'),
}
FACT_KEYS={}
for line in '''
shared_admission=damage_order composite
effect_filter=effect_filter external_effect_admission
phase_monitor=phase_detection
damage_history=damage_memory retarget
combat_schedule=scheduler
lich_missile=projectile_admission missile_damage
lich_slow=missile_status volleys
lich_summon=minion_delivery minion_actual_state placement_geometry
summon_melee=minion_actual_state night_context
lich_teleport=teleport placement_geometry
lich_admission=admission
lich_phase=delivery_and_phase
lich_cleanup=death_cleanup
obsidilith_shield=shield_resource shield_admission pillars_and_phase
obsidilith_defense=other_defense
rift_damage=rift_delivery burst wave spike
rift_motion=client_motion burst wave
wave_fire_counter=wave
spike_slow=spike
obsidilith_anvil_movement=anvil
world_rift_schedule=world_scheduler rift_delivery
gauntlet_admission=hitbox_admission parts projectile_part_delivery melee_part_delivery
gauntlet_aggro=aggro_and_defense move_selection
gauntlet_heal=aggro_and_defense
gauntlet_melee=melee_and_laser_amount punch swirl laser_delivery
gauntlet_motion=punch swirl
gauntlet_laser_delivery=laser_delivery block_clear move_selection
gauntlet_blindness=blindness
native_fire_hp=explosions_and_fire stage_and_followup
blossom_parts=admission_and_parts defense_and_selection
blossom_thorns=retaliation proximity death_and_exclusions
blossom_spikes_hp=spike_geometry spore_block_and_area source_and_stage
blossom_thrown=spore_direct petal
blossom_poison=spore_block_and_area poison
poison_tick=poison source_and_stage
blossom_blocks=blossoms heal
pearl_zero=pearl_use_and_zero_hit
pearl_teleport=pearl_control
equipment_buffs=pearl_effects_and_shove fruit_delivery
pearl_shove=pearl_effects_and_shove
food_regen=fruit_delivery fruit_numeric
food_heal=fruit_delivery fruit_numeric
spear_teleport=spear
monolith_radius=monolith
table_flight=cache_and_flight
'''.strip().splitlines():
    name,keys=line.split('=');FACT_KEYS['bomd:'+name]=keys.split()
SPECIAL={('r2j2-shared-admission','bomd:capped_heal'):['idle_heal','heal_scaling'],('r2j6-void-blossom','bomd:capped_heal'):['heal'],('r2j3-night-lich','bomd:native_explosion'):['comet','comet_source','explosion_payload','comet_delivery'],('r2j4-obsidilith','bomd:native_explosion'):['anvil','death_and_explosions'],('r2j5-gauntlet','bomd:native_explosion'):['punch','swirl','explosions_and_fire','death','stage_and_followup'],('r2j7-equipment','bomd:native_explosion'):['monolith']}

def implementation(d):
    file=next(r['file'] for r in d['reference_files'] if r['file'].startswith('native-evidence/'))
    return [dict(evidence_file=file,witness_id=w['id'],entry=w['entry'],methods=sorted({m['name'] for m in w['methods']})) for w in read_json(OUT/file)['witnesses'] if w.get('methods')]

def coverage(sections,paths):
    census=read_json(OUT/'bomd-source-census.json');index=defaultdict(list);semantic=defaultdict(list)
    for stem,d in sections.items():
        semantic[next(r['file'] for r in d['reference_files'] if r['file'].startswith('native-evidence/'))].append('bomd-'+stem+'.json')
    for f in sorted((OUT/'native-evidence').glob('bomd-*.json')):
        for w in read_json(f)['witnesses']:
            for m in w.get('methods',[]):index[(w['entry'],m['name'],m['descriptor'])].append(dict(evidence_file='native-evidence/'+f.name,witness_id=w['id'],entry=w['entry'],methods=[m['name']]))
    def refs(row):
        impl=index[(row['entry'],row['method'],row['descriptor'])];assert impl,row
        return dict(implementation=impl,semantic_sections=unique([s for r in impl for s in semantic[r['evidence_file']]]) or ['bomd-r2j1-source-foundation.json'])
    watched=[dict(**r,disposition='SHORT_LOCATOR_EXCLUSION' if '/SoulStarEntity' in r['entry'] else 'REVIEWED_COMBAT_OR_NATIVE_HELPER',**refs(r)) for r in census['watched_methods']]
    callers=[dict(entry=r['entry'],method=r['method'],descriptor=r['descriptor'],kind='ACTUAL_NATIVE_HURT_PRODUCER',**refs(r)) for r in census['watched_methods'] if any('.shieldPiercing(' in str(h['operand']) for h in r['hits'])]
    assert len(callers)==5
    decl=read_json(OUT/'bomd-damage-tags.json')['declarations'];assert len(decl)==1
    dtype=dict(**decl[0],disposition='USED',callers=callers,key_readers=[dict(**r,disposition='EXACT_KEY_NATIVE_BLOCKING_OVERRIDE',**refs(r)) for r in census['custom_damage_key_methods']],factory=dict(evidence_file='native-evidence/bomd-foundation.json',entry='com/cerbon/bosses_of_mass_destruction/util/BMDUtils.class',methods=['shieldPiercing']),requested_amount_formula='Current originating boss ATTACK_DAMAGE for four ground attacks; captured Living owner ATTACK_DAMAGE at spore-column callback.',direct_entity='Native supplied boss for Obsidilith/Void Blossom ground attacks; CURRENT spore projectile owner for its column callback.',causing_entity='Same entity as direct entity; native source factory uses single entity constructor.',mechanic_ids=['bomd:shield_piercing_hp'],delivery_paths=[p['id'] for p in paths if 'bomd:shield_piercing_hp' in p['effect_ids']],armor_behavior='No bypass_armor tag; native armor retained.',shield_behavior='Native exact-key LivingEntity.isDamageSourceBlocked HEAD override false; not a bypass for boss-specific rune/eye admission.',resistance_behavior='No bypass_resistance/bypasses_effects tags; native Resistance retained.',protection_behavior='No bypass_enchantments tag; native protection retained.',hurt_return_dependencies='All five caller hurt booleans discarded. Obsidilith burst/wave client motion independent; wave raw fire timer before hurt; spike Slowness after hurt; spore Poison after hurt; Void Blossom Spikes HP only.',tag_scope='Pinned vanilla1.21.1/NeoForge21.1.244/BOMD only, no contribution tags. Other pack/runtime changes not certified.')
    return dict(schema='tno.external_effects.bomd_total_source_coverage.v1',baseline=BASELINE,checkpoint=CP,jar_sha256=census['jar_sha256'],parsed_classes=287,watched_methods=watched,custom_damage_types=[dtype],actual_custom_hurt_producers=5,native_effect_reference_methods=[dict(**r,disposition='ZERO_DURATION_FLOWER_METADATA_NOT_CONTACT_STATUS' if '/VoidLilyBlock' in r['entry'] else 'REVIEWED_NATIVE_EFFECT_REFERENCE',**refs(r)) for r in census['native_effect_reference_methods']],custom_effect_registry_candidates=[dict(**r,disposition='CONFIGURED_LICH_EFFECT_LOOKUP_NOT_REGISTRATION',**refs(r)) for r in census['custom_effect_registry_candidates']],whole_class_inventory='bomd-source-census.json',direct_compat='bomd-direct-compat-census.json',additional_closure_evidence='native-evidence/bomd-closure.json',short_exclusions=sections['r2j7-equipment']['facts']['short_exclusions'],movement_boundary='Lich/Gauntlet native VelocityGoal -> target selector/steering -> own addDeltaMovement; travel is native flight friction. No victim HP/effect source or separate Stage payload. Combat callbacks remain in protected boss contracts.',packet_boundary='SpikeS2C updates clientSpikeHandler; HealS2C invokes particle handler; ChargedEnderPearlS2C invokes client impact visuals. Separate SendDeltaMovementS2C actually writes client motion and remains an explicit Obsidilith path. No packet HP fallback.',scope='All watched methods, native status references and custom source consumers have explicit dispositions. Family reviews also cover inherited delivery/admission and actual food/block/multipart callbacks; census alone is not semantic coverage proof.',runtime_tests=0)

def build():
    sections={s:read_json(OUT/('bomd-'+s+'.json')) for s in STEMS};groups=defaultdict(list);original={};pathgroups=defaultdict(set);dispositions=[];manifest_sections=[];fixture_sets=[]
    for stem,d in sections.items():
        file='bomd-'+stem+'.json';impl=implementation(d)
        manifest_sections.append(dict(file=file,sha256=sha256(OUT/file),packages=len(d['mechanic_packages']),paths=len(d['delivery_paths'])))
        fixture_sets.append(dict(file=file,contracts=d['unexecuted_future_fixtures'],runtime_status='NOT_RUN'))
        for p in d['delivery_paths']:assert p['id'] not in original;original[p['id']]=(file,deepcopy(p),impl)
        for m in d['mechanic_packages']:
            mid=m['id'];target=ALIASES.get(mid,mid);keys=SPECIAL.get((stem,mid),FACT_KEYS.get(mid));assert keys,(stem,mid)
            facts=[dict(file=file,key=k,text=d['facts'][k]) for k in keys]
            groups[target].append(dict(section=file,original=deepcopy(m),facts=facts,implementation=impl))
            dispositions.append(dict(section=file,original_id=mid,canonical_ids=[target],status='ALIASED_NATIVE_PRIMITIVE' if target!=mid else 'EXTENDS_REVIEWED_PACKAGE' if len(groups[target])>1 else 'RETAINED_NATIVE_CONTRACT'))
            for pid in m['delivery_paths']:pathgroups[PATH_ALIASES.get(pid,pid)].add(target)
    buckets=defaultdict(list)
    for pid,row in original.items():buckets[PATH_ALIASES.get(pid,pid)].append((pid,*row))
    paths=[];fixtures=[]
    for pid,variants in buckets.items():
        _,file,p,impl=variants[0];labels=unique([{'STATUS':'OTHER','BLOCK_CONTACT':'ENVIRONMENT'}.get(x,x) for _,_,v,_ in variants for x in v['labels']]);assert set(labels)<=set(DELIVERIES)
        controls=unique([c for _,_,v,_ in variants for c in v.get('runtime_variants',[])]);source=p['native_path'];ids=[v[0] for v in variants]
        row=dict(id=pid,mod_key=KEY,status='VERIFIED',inspection_status='VERIFIED',labels=labels,effect_ids=sorted(pathgroups[pid]),primary_source=source,setup='Genuine native delivery: '+source,implementation=unique([r for _,_,_,refs in variants for r in refs]),native_contracts=[v[2] for v in variants],semantic_sections=unique([v[1] for v in variants]),fixture_controls=controls,source_case_ids=ids,runtime_status='NOT_RUN')
        paths.append(row);fixtures.append(dict(path_id=pid,effect_ids=row['effect_ids'],native_contracts=row['native_contracts'],source_case_ids=ids,section_fixture_sets=row['semantic_sections'],controls=controls,runtime_status='NOT_RUN'))
    effects=[]
    for eid,members in groups.items():
        base=members[0]['original'];name,cl,point=CANONICAL.get(eid.split(':')[1],(base['name'],base['primary_classification'],base['single_scaling_point']));scale=bool(point)
        cats=unique([c for m in members for c in m['original']['tno_categories']]);cats=[c for c in cats if c not in ['NUMERIC_SCALABLE','NO_STAGE_VALUE']]+['NUMERIC_SCALABLE' if scale else 'NO_STAGE_VALUE']
        facts=unique([f for m in members for f in m['facts']]);variants=[dict(section=m['section'],original_package_id=m['original']['id'],native_contract=m['original'],fact_keys=[f['key'] for f in m['facts']]) for m in members]
        pids=[p['id'] for p in paths if eid in p['effect_ids']];reason='Only final native amount once; leave admission/control native.' if scale else base['stage_reason'];behavior=[f['text'] for f in facts]
        components=[dict(primitive='NATIVE_FINAL_AMOUNT' if scale else 'NATIVE_CONTROL_ADMISSION_RESOURCE',formula=point or reason,numerical_parameters={'source_variants':[v['section']+'#'+v['original_package_id'] for v in variants]},binary_parameters=['Preserve native owner/source, eligibility, mitigation, hurt-return dependency and callback ordering.'],vanilla_relation=cl,tno_categories=cats,stage_scaling_needed=scale,single_scaling_point=point)]
        if scale:components.append(dict(primitive='UNSCALED_NATIVE_COMPANIONS',formula='Native radius/phase/count/cadence/modifier/status/control/source remain unchanged; no second Stage multiplier.',numerical_parameters={},binary_parameters=[],vanilla_relation='Source-specific native companion contract',stage_scaling_needed=False,single_scaling_point=None))
        effects.append(dict(id=eid,mod_key=KEY,display_name=name,human_summary=name+'; static native semantics, runtime untested.',inspection_status='VERIFIED',native_status='STATIC_VERIFIED',primary_classification=cl,classification_provisional=False,registry_ids=[],tno_categories=cats,stage_scaling_needed=scale,single_scaling_point=point,stage_reason=reason,actual_behavior=behavior,fact_references=[dict(file=f['file'],key=f['key']) for f in facts],components=components,implementation=unique([r for m in members for r in m['implementation']]),delivery_paths=pids,primary_test_source=next(p['primary_source'] for p in paths if p['id']==pids[0]),alternate_sources=unique([p['primary_source'] for p in paths if eid in p['effect_ids']]),source_parameter_variants=variants,closest_vanilla_equivalent=cl+'; exact native callbacks retained.',vanilla_similarities=['Native damage/effect/heal/source pipeline where delegated.'],vanilla_differences=behavior,compatibility_attribution='SCOPED_EXPLICIT_NAME_SCAN_AND_GENERIC_HOOKS_STATIC_ONLY',compatibility_evidence=['bomd-r2j1-source-foundation.json','bomd-total-source-coverage.json'],pending=[],unresolved_ambiguities=[],runtime_status='NOT_RUN'))
    counts=dict(input_packages=len(dispositions),native_cases=len(original),final_mechanics=len(effects),final_deliveries=len(paths),aliased_input_packages=sum(x['status']=='ALIASED_NATIVE_PRIMITIVE' for x in dispositions),delivery_extensions=sum(x['status']=='EXTENDS_REVIEWED_PACKAGE' for x in dispositions),aliased_duplicate_paths=len(original)-len(paths),excluded_combat_cases=0)
    reviews=unique([v for d in sections.values() for v in d['review_required']])
    manifest=dict(schema='tno.external_effects.bomd_promotion_map.v1',baseline=BASELINE,checkpoint=CP,starting_sha=START,sections=manifest_sections,mechanic_dispositions=dispositions,path_dispositions=[dict(original_id=pid,canonical_id=PATH_ALIASES.get(pid,pid)) for pid in original],counts=counts,dedup_policy='Merge repeated native explosion/capped-heal packages, owner-attribute thrown, custom shield-piercing HP and native Mob melee. Keep every distinct source case; exact shared/Blossom idle-heal duplicate aliases one path. Normalize provisional STATUS/BLOCK_CONTACT labels to schema OTHER/ENVIRONMENT without changing mechanics. Cross-mod R3 remains pending.')
    matrix=dict(schema='tno.external_effects.bomd_future_fixtures.v1',baseline=BASELINE,checkpoint=CP,status='FUTURE_ONLY_NOT_RUN',fixtures=fixtures,section_fixture_sets=fixture_sets,review_required=reviews,runtime_tests=0,note='Use genuine native enclosing producer and engine admission, never synthetic part/source/event/helper attacks. Counts are static coverage, not runtime tests.',**boundary_flags())
    review=dict(schema='tno.external_effects.mod_review.v1',baseline=BASELINE,mod_key=KEY,checkpoint=CP,starting_sha=START,status='COMPLETE',decision='BOMD_COMBAT_SEMANTIC_REVIEW_COMPLETE',scope='Installed BOMD1.3.3 combat-significant static review complete; native shield_piercing USED with five actual callers. Runtime compatibility and Stage untested.',semantic_discovery_complete=True,special_damage_discovery_complete=True,source_mapping_complete=True,delivery_mapping_complete=True,effects=effects,paths=paths,semantic_effect_count=len(effects),unresolved_native_ambiguities=[],remaining_native_ambiguities=[],review_required=reviews,review_required_scope='Future runtime/integration decisions, not unresolved native semantics.',classification_counts=dict(Counter(e['primary_classification'] for e in effects)),promotion_manifest='bomd-final-promotion-map.json',future_runtime_fixture_matrix='bomd-future-runtime-fixtures.json',whole_source_closure='bomd-total-source-coverage.json',exact_next_task=NEXT,runtime_tests=0,**boundary_flags())
    return review,manifest,matrix,coverage(sections,paths)

def save():
    r,m,f,c=build()
    for name,obj in [('mod-reviews/'+KEY+'.json',r),('bomd-final-promotion-map.json',m),('bomd-future-runtime-fixtures.json',f),('bomd-total-source-coverage.json',c)]:write_json(OUT/name,obj)
    refresh_safe(CP)
    p=read_json(OUT/'behavior-primitives.json');p['primitives']=[v for v in p['primitives'] if v['mod_key']!=KEY]
    for e in r['effects']:
        for i,v in enumerate(e['components']):p['primitives'].append(dict(v,id=e['id']+':component:'+str(i),effect_id=e['id'],mod_key=KEY,status='VERIFIED_PER_MOD',implementation=e['implementation'],source_case_paths=e['delivery_paths']))
    p.update(checkpoint=CP);write_json(OUT/'behavior-primitives.json',p)
    for name in ['effect-catalog.json','effect-sources.json','delivery-path-matrix.json','vanilla-comparison.json','behavior-primitives.json']:
        o=read_json(OUT/name);o.pop('unfinished_review',None);o['last_completed_mod']=KEY;write_json(OUT/name,o)
    o=read_json(OUT/'research-decision.json');o.update(checkpoint=CP,next_task=NEXT,latest_bomd_decision=r['decision'],save_mode=False,save_reason=None);o['checkpoints']['R2j7-bomd-equipment-complete']=START;o['checkpoints'][CP]='Self: exact SHA from commit/live verification.';write_json(OUT/'research-decision.json',o)
    lines=['# Bosses of Mass Destruction combat owner table — COMPLETE','',f"{len(r['effects'])} deduplicated mechanics; {len(r['paths'])} native paths from {m['counts']['input_packages']} protected packages and {m['counts']['native_cases']} source cases. Static only; runtime tests0.",'','One custom DamageType: shield_piercing USED, five actual callers. All37 watched methods, eight native effect-reference methods and four configured-effect lookups have dispositions. Existing accepted records are unchanged.','', '| Mechanic | TNO classification | Single future Stage point / no-value reason |','|---|---|---|']
    for e in r['effects']:lines.append('| '+e['display_name']+' | '+', '.join(e['tno_categories'])+' | '+str(e['single_scaling_point'] or e['stage_reason']).replace('|',' / ')+' |')
    lines+=['','[Complete contracts](mod-reviews/bosses_of_mass_destruction.json), [runtime fixtures](bomd-future-runtime-fixtures.json), [source coverage](bomd-total-source-coverage.json), [promotion map](bomd-final-promotion-map.json).','','Compatibility priorities: native Holder/value effect-filter mismatch; genuine Gauntlet part admission; rune shield distinct from ordinary shield blocking; hurt-independent secondary callbacks; captured/current owner differences; native anonymous Poison/fire/explosion attribution; capped-heal input scaling; Monolith radius and external flight permission conflict. No source rewrites or native bug repairs.','','Future integration decisions:']
    lines+=['- '+v['reason'] for v in r['review_required']]
    lines+=['','Exclusions: '+c['short_exclusions'],'','Closure: '+c['movement_boundary']+' '+c['packet_boundary'],'','Exact next task: '+NEXT,'']
    (OUT/'bomd-final-owner-table.md').write_text('\n'.join(lines),encoding='utf-8')
    main=ROOT/'docs/external-effects-catalog-research.md';s=main.read_text(encoding='utf-8');h='## R2j8 — Bosses of Mass Destruction combat catalog COMPLETE'
    if h not in s:s+='\n'+h+'\n\n'+f"{len(r['effects'])} deduplicated mechanics, {len(r['paths'])} native paths; sole custom DamageType USED at five callers. Static semantics complete, future runtime/integration decisions explicit. [Owner table and next task](benchmarks/external-effects-catalog/bomd-final-owner-table.md).\n"
    main.write_text(s,encoding='utf-8');print(json.dumps(m['counts'],indent=2))

if __name__=='__main__':save()
