"""Deterministic promotion of the protected Twilight combat review, with total provenance."""
from copy import deepcopy
from collections import Counter,defaultdict
from catalog_common import *
from assemble_batch import refresh
from twilight_promotion_migration import START

CP='R2f-final-complete'
DRAFT='partial-drafts/twilightforest-r2f8af-partial.json'
PLAN='twilightforest-final-promotion-plan.json'


def unique(values):
    found=set();result=[]
    for v in values:
        key=json.dumps(v,sort_keys=True)
        if key not in found:found.add(key);result.append(deepcopy(v))
    return result


def as_list(value):return value if isinstance(value,list) else [value]


def comparison(source):
    relations=[c['primitive']+': '+c.get('vanilla_relation','Native relation is specified in the source contract.') for c in source['components']]
    return dict(closest_vanilla=source.get('closest_vanilla_equivalent','; '.join(relations)),similarities=source.get('vanilla_similarities',relations),differences=source.get('vanilla_differences',dict(classification=source['primary_classification'],component_contracts=[dict(primitive=c['primitive'],formula=c['formula'],native_relation=c.get('vanilla_relation')) for c in source['components']])))


def build():
    draft=read_json(OUT/DRAFT);plan=read_json(OUT/PLAN)
    oldeffects={e['id']:e for e in draft['effects']};oldpaths={p['id']:p for p in draft['paths']}
    emap={}
    for eid in oldeffects:
        emap[eid]=[] if eid in plan['excluded_effects'] else plan['effect_aliases'].get(eid,[eid])
    assert set(plan['effect_aliases'])<=set(oldeffects) and set(plan['excluded_effects'])<=set(oldeffects)
    assert set(plan['path_folds'])|set(plan['excluded_paths'])<=set(oldpaths)
    effects={};contributors=defaultdict(list)
    for eid,targets in emap.items():
        for target in targets:contributors[target].append(eid)
    for target,srcids in contributors.items():
        base=oldeffects.get(target,oldeffects[srcids[0]])
        e=deepcopy(base);e.update(id=target,inspection_status='VERIFIED',native_status='STATIC_VERIFIED',classification_provisional=False,pending=[],unresolved_ambiguities=[],source_draft_ids=srcids)
        e['human_summary']=e['display_name']+'; exact installed native behavior, sources and admission below. Static review only.'
        for field in ['actual_behavior','components','implementation','registry_ids','alternate_sources']:
            e[field]=[]
        e['source_parameter_variants']=[]
        e['historical_wording_note']='Temporal references to later/pending body reviews inside quoted source facts are superseded by R2f8 whole closure and the completed sections. No native ambiguity remains. The original source-specific contracts and historical evidence are not rewritten.'
        for sid in srcids:
            source=oldeffects[sid];facts=as_list(source['actual_behavior']);components=deepcopy(source['components'])
            if sid=='twilightforest:charms_curios_retention':
                facts=facts[:1]
                components=[dict(primitive='CURIO_LIFE_CONSUMPTION',formula=facts[0],numerical_parameters={},binary_parameters=['actual active equipped Life charm','native first-match cached lookup','nonempty serializable stack'],vanilla_relation='Optional native Curios source admission for the same Life rescue')]
            if sid=='twilightforest:minotaur_equipment_charge':
                indexes=[0,1,3,4] if target.endswith('minoshroom_axing') else [0,2,4]
                facts=[facts[i] for i in indexes]
                components=[dict(primitive='MINOTAUR_SOURCE_VARIANT',formula=' '.join(facts),numerical_parameters=source.get('numerical_parameters',{}),binary_parameters=source.get('binary_parameters',[]),vanilla_relation='Source-specific variant of protected native axing/charge contract')]
            # Equivalent .1 fall is a source variant of the same component.
            if sid=='twilightforest:arctic_fur_native_fall':components=[]
            e['actual_behavior']+=facts;e['components']+=components;e['implementation']+=source['implementation']
            if sid!='twilightforest:charms_curios_retention':e['registry_ids']+=source.get('registry_ids',[])
            e['alternate_sources']+=([source['primary_test_source']]+source.get('alternate_sources',[]))
            e['source_parameter_variants'].append(dict(draft_effect_id=sid,numerical_parameters=source.get('numerical_parameters',{}),binary_parameters=source.get('binary_parameters',[]),**comparison(source)))
        for field in ['actual_behavior','components','implementation','registry_ids','alternate_sources']:e[field]=unique(e[field])
        e['closest_vanilla_equivalent']=comparison(base)['closest_vanilla']
        e['vanilla_similarities']=[v['similarities'] for v in e['source_parameter_variants']]
        e['vanilla_differences']=[v['differences'] for v in e['source_parameter_variants']]
        if target=='twilightforest:native_ignition_delivery':
            e.update(display_name='Native ignition with source-specific combat admission',primary_classification='VANILLA_LIKE_EXTENDED',closest_vanilla_equivalent='Native igniteForSeconds and ordinary fire tick processing',vanilla_similarities=['Native fire timer, native on_fire source and recipient admission are retained.'],vanilla_differences=['Fiery tool incoming/Player callbacks, Fiery armor Post probability, Lamp nonplayer AOE and biome enforcement differ in source-specific gates, duration and timing; these are delivery variants of the native ignition primitive.'])
        if target=='twilightforest:cloud_native_fall_reduction':e['display_name']='Cloud and Arctic Fur native fall multiplier'
        e['human_summary']=e['display_name']+'; static native contract, not a runtime HP observation.'
        e['numerical_parameters']={v['draft_effect_id']:v['numerical_parameters'] for v in e['source_parameter_variants']}
        e['binary_parameters']=unique([gate for c in e['components'] for gate in c.get('binary_parameters',[])])
        e['parameter_note']='Exact numbers also occur in component formulas and source-specific native contracts; no balance or Stage implementation is implied.'
        e['compatibility_attribution']='GENERIC_CONDITIONAL_PRESENT; scoped direct-name scans negative, native optional integrations and generic installed hooks retained.'
        e['compatibility_evidence']=['compat-findings/twilightforest-frosted.json','compat-findings/twilightforest-global.json']
        effects[target]=e
    pathmap={};groups=defaultdict(list)
    for pid,p in oldpaths.items():
        targets=[]
        for eid in p['effect_ids']+p.get('reuses_protected_effect_ids',[]):
            if eid in plan['restricted_alias_paths'] and pid not in plan['restricted_alias_paths'][eid]:continue
            targets+=emap[eid]
        reason=plan['excluded_paths'].get(pid)
        if reason or not targets:
            reason=reason or 'All linked packages are excluded by corrected combat scope, or this is only the excluded inventory-retention half of the Curios bridge. See original archive and effect dispositions.'
            pathmap[pid]=dict(original_path_id=pid,status='EXCLUDED_NONCOMBAT',canonical_path_id=None,canonical_effect_ids=[],reason=reason)
            continue
        fold=plan['path_folds'].get(pid);canonical=fold['canonical_path'] if fold else pid
        pathmap[pid]=dict(original_path_id=pid,status='FOLDED_FIXTURE_VARIANT' if fold else 'RETAINED_NATIVE_DELIVERY',canonical_path_id=canonical,canonical_effect_ids=sorted(set(targets)),reason=fold['reason'] if fold else 'Material native producer, payload, recipient, owner, admission, callback or persistence route retained.')
        groups[canonical].append(pid)
    paths=[];fixtures=[]
    for canonical,members in groups.items():
        assert canonical in members,(canonical,members)
        members=[canonical]+[pid for pid in members if pid!=canonical]
        originals=[oldpaths[pid] for pid in members];p=deepcopy(oldpaths[canonical]);p.update(status='VERIFIED',inspection_status='VERIFIED',source_case_ids=members)
        p['primary_source']=p.get('primary_source',p.get('source'))
        p['alternate_sources']=unique([q.get('primary_source',q.get('source')) for q in originals]+p.get('alternate_sources',[]))
        p['effect_ids']=sorted({eid for pid in members for eid in pathmap[pid]['canonical_effect_ids']})
        p['implementation']=unique([r for q in originals for r in q['implementation']])
        p['labels']=unique([label for q in originals for label in q['labels']])
        p['fixture_controls']=unique([c for q in originals for c in q.get('future_controls',q.get('fixture_controls',[]))])
        p['native_contract_variants']=[dict(original_path_id=q['id'],source=q.get('primary_source',q.get('source')),native_contract=q.get('native_delivery',q.get('actual_native_contract',q['setup'])),effect_ids=pathmap[q['id']]['canonical_effect_ids']) for q in originals]
        p.pop('reuses_protected_effect_ids',None)
        fixtures.append(dict(path_id=canonical,primary_source=p['primary_source'],alternate_sources=p['alternate_sources'],setup=p['setup'],effect_ids=p['effect_ids'],controls=p['fixture_controls'],original_case_ids=members,runtime_status='NOT_RUN',runtime_uncertainties=['Actual event counts, post-mitigation HP/SHP, whole-pack ordering and Tensura/L2 interactions need separately authorized runtime fixtures.']))
        paths.append(p)
    for e in effects.values():
        e['delivery_paths']=[p['id'] for p in paths if e['id'] in p['effect_ids']]
        assert e['delivery_paths'],e['id']
        e['primary_test_source']=next(p['primary_source'] for p in paths if e['id'] in p['effect_ids'])
        e['alternate_sources']=unique([s for p in paths if e['id'] in p['effect_ids'] for s in [p['primary_source']]+p['alternate_sources']])
    manifest=dict(schema='tno.external_effects.twilight_promotion_map.v1',baseline=BASELINE,starting_sha=START,checkpoint=CP,draft_file=DRAFT,draft_sha256=sha256(OUT/DRAFT),plan_file=PLAN,plan_sha256=sha256(OUT/PLAN),effect_dispositions=[dict(original_effect_id=eid,status='EXCLUDED_NONCOMBAT' if not targets else 'ALIASED_NATIVE_CONTRACT' if targets!=[eid] else 'RETAINED',canonical_effect_ids=targets,reason=plan['excluded_effects'].get(eid,'Same native contract with source-specific parameters preserved.' if targets!=[eid] else 'Distinct combat-significant contract.')) for eid,targets in emap.items()],path_dispositions=list(pathmap.values()),counts=dict(original_mechanics=len(oldeffects),original_cases=len(oldpaths),final_mechanics=len(effects),final_deliveries=len(paths),excluded_mechanics=sum(not x for x in emap.values()),aliased_mechanics=len(plan['effect_aliases']),excluded_cases=sum(r['status']=='EXCLUDED_NONCOMBAT' for r in pathmap.values()),folded_cases=sum(r['status']=='FOLDED_FIXTURE_VARIANT' for r in pathmap.values())),dedup_policy=plan['dedup_policy'])
    fixturematrix=dict(schema='tno.external_effects.twilight_future_fixtures.v1',baseline=BASELINE,checkpoint=CP,status='FUTURE_ONLY_NOT_RUN',fixtures=fixtures,note='One row per retained native delivery contract with all folded controls; this is coverage, not a claim of globally minimal test count. Cross-mod source minimization remains R3.',runtime_tests=0,**boundary_flags())
    review=read_json(OUT/'mod-reviews/twilightforest.json')
    review.update(status='COMPLETE',checkpoint=CP,starting_sha=START,decision='TWILIGHT_FOREST_SEMANTIC_REVIEW_COMPLETE',scope='Installed Twilight4.8.3345 combat-significant static semantic review complete; ordinary utility/progression/acquisition/rendering excluded by explicit total mapping. Runtime compatibility is not certified.',semantic_discovery_complete=True,special_damage_discovery_complete=True,source_mapping_complete=True,delivery_mapping_complete=True,semantic_effect_count=len(effects),semantic_effect_count_note='Distinct accepted combat mechanic packages after explicit scope exclusions and native-contract merges.',effects=list(effects.values()),paths=paths,unresolved_native_ambiguities=[],remaining_native_ambiguities=[],ambiguity_note='Zero unresolved native semantics; future runtime observations are not native ambiguities.',review_required=[],classification_counts=dict(Counter(e['primary_classification'] for e in effects.values())),named_native_effects=['twilightforest:frosted'],promotion_manifest='twilightforest-final-promotion-map.json',future_runtime_fixture_matrix='twilightforest-future-runtime-fixtures.json',damage_type_closure='twilightforest-r2f8y-damage-type-closure.json',whole_source_closure='twilightforest-global-source-closure.json',compatibility='compat-findings/twilightforest-global.json',exact_next_task='Begin narrow combat-significant IceAndFireCE beta15 installed-native research; do not repeat Twilight, run runtime/L2/Stage tests or alter production.',runtime_tests=0,**boundary_flags())
    return review,manifest,fixturematrix


def save():
    review,manifest,fixtures=build()
    write_json(OUT/'mod-reviews/twilightforest.json',review)
    write_json(OUT/'twilightforest-final-promotion-map.json',manifest)
    write_json(OUT/'twilightforest-future-runtime-fixtures.json',fixtures)
    refresh(CP)
    primitives=read_json(OUT/'behavior-primitives.json')
    primitives['primitives']=[p for p in primitives['primitives'] if p['mod_key']!='twilightforest']
    for e in review['effects']:
        for i,c in enumerate(e['components']):
            primitives['primitives'].append(dict(c,id=e['id']+':component:'+str(i),effect_id=e['id'],mod_key='twilightforest',status='VERIFIED_PER_MOD',implementation=e['implementation'],source_case_paths=e['delivery_paths']))
    primitives.update(checkpoint=CP,note='Accepted per-mod component instances. Source variants share canonical mechanic packages; component instances are not a global primitive count. Cross-mod R3 normalization remains unfinished.')
    write_json(OUT/'behavior-primitives.json',primitives)
    for name in ['effect-catalog.json','effect-sources.json','delivery-path-matrix.json','vanilla-comparison.json','behavior-primitives.json']:
        doc=read_json(OUT/name);doc.pop('unfinished_review',None);doc['last_completed_mod']='twilightforest';write_json(OUT/name,doc)
    decision=read_json(OUT/'research-decision.json');decision.update(checkpoint=CP,next_task=review['exact_next_task'],latest_twilight_subsection_decision=review['decision'],save_mode=False,save_reason='Owner authorizes continuing after protected Twilight COMPLETE into narrow IceAndFire research.')
    decision['checkpoints']['R2f8-remaining-content-complete']=START;decision['checkpoints'][CP]='Self: exact SHA supplied by commit and live verification.'
    write_json(OUT/'research-decision.json',decision)
    print(json.dumps(dict(counts=manifest['counts'],classifications=review['classification_counts']),indent=2))


if __name__=='__main__':save()
