"""Assemble later Twilight subsets from explicit reviewed inputs; never promotes a mod."""
from copy import deepcopy
from collections import Counter
from twilight_evidence import *
from assemble_batch import refresh


def corrected_prior(prior, corrections):
    """Apply explicit, counted errata to a new draft; historical evidence stays immutable."""
    draft=deepcopy(prior)
    for correction in corrections:
        old=correction['old_text'];new=correction['new_text'];hits=[]
        assert old and old!=new and correction['reason'] and correction['evidence_files']
        def replace(value, path):
            if isinstance(value,str):
                count=value.count(old)
                if count:hits.extend([path]*count)
                return value.replace(old,new)
            if isinstance(value,list):return [replace(v,path+'/'+str(i)) for i,v in enumerate(value)]
            if isinstance(value,dict):return {k:replace(v,path+'/'+k) for k,v in value.items()}
            return value
        for key in ['effects','paths']:draft[key]=replace(draft[key],key)
        assert hits==correction['expected_locations'],(correction['id'],hits)
    return draft


def damage_tags():
    tags={}
    for r in read_json(OUT/'vanilla-evidence/royalvariations.json')['resources']:
        if '/tags/damage_type/' in r['entry'] and 'data' in r:tags[r['entry'].split('/')[1]+':'+r['entry'].split('/tags/damage_type/')[1][:-5]]=list(r['data']['values'])
    for p,v in read_json(WORK/'twilightforest/resources.json').items():
        if '/tags/damage_type/' in p:tags.setdefault(p.split('/')[1]+':'+p.split('/tags/damage_type/')[1][:-5],[]).extend(v['data']['values'])
    def values(t,seen=()):
        if t in seen:return set()
        out=set()
        for x in tags.get(t,[]):
            x=x['id'] if isinstance(x,dict) else x
            out.update(values(x[1:],seen+(t,)) if x.startswith('#') else [x])
        return out
    return lambda rid:sorted(t for t in tags if rid in values(t))


def assemble(input_name):
    input_path=OUT/'review-inputs'/input_name
    data=read_json(input_path);facts=data['facts'];cp=data['checkpoint'];slug=data['slug'];nxt=data['exact_next_task']
    effects=[];paths=[]
    for row in data['packages']:
        e=deepcopy(row);keys=e.pop('facts');classes=e.pop('classes');relation=e.pop('relation');nums=e.pop('parameters');gates=e.pop('gates')
        e.update(mod_key='twilightforest',inspection_status='DRAFT',subsection_status='REVIEWED',classification_provisional=False,actual_behavior=[facts[k] for k in keys],components=[dict(primitive=e['id'].split(':')[-1].upper(),formula='; '.join(facts[k] for k in keys),numerical_parameters=nums,binary_parameters=gates,vanilla_relation=relation)],implementation=native_refs(*classes),delivery_paths=[],registry_ids=e.get('registry_ids',[]),pending=['Whole Twilight closure/final promotion only; this bounded subsection is reviewed.'],unresolved_ambiguities=None)
        effects.append(e)
    for row in data['paths']:
        p=deepcopy(row);keys=p.pop('facts');classes=p.pop('classes')
        p.update(mod_key='twilightforest',status='DRAFT',subsection_status='REVIEWED',native_delivery=' '.join(facts[k] for k in keys),implementation=native_refs(*classes))
        paths.append(p)
        for e in effects:
            if e['id'] in p['effect_ids']:e['delivery_paths'].append(p['id'])
    tagsof=damage_tags();resources=read_json(WORK/'twilightforest/resources.json');profiles=[]
    for row in data['damage_profiles']:
        p=deepcopy(row);rid=p['type'];p.update(tags=tagsof(rid),declaration=resources['data/twilightforest/damage_type/'+rid.split(':')[1]+'.json']['data']);profiles.append(p)
    counts=dict(mechanic_packages=len(effects),delivery_cases=len(paths),classification_totals=dict(Counter(e['primary_classification'] for e in effects)),review_required=sum(e['primary_classification']=='REVIEW_REQUIRED' for e in effects),new_custom_types_resolved=data['new_damage_types'])
    assert counts==data['expected_counts'],(counts,data['expected_counts'])
    refs=[dict(evidence_file=p,sha256=sha256(OUT/p)) for p in data['comparison_files']]
    section=dict(schema='tno.external_effects.semantic_section.v1',baseline=BASELINE,mod_key='twilightforest',checkpoint=cp,starting_sha=data['starting_sha'],status='REVIEWED_SUBSET_NOT_MOD_COMPLETE',subsection_decision=data['decision'],semantic_coverage_complete=False,promoted_to_catalog=False,remaining_content_subsection=True,effects=effects,paths=paths,damage_profiles=profiles,semantic_closure=facts,closure_checklist={k:True for k in data['closure_checklist']},comparison_evidence=refs,review_input=dict(evidence_file=input_path.relative_to(OUT).as_posix(),sha256=sha256(input_path)),source_registration_evidence=native_refs(*data['registration_classes']),full_declared_class_coverage=data['full_classes'],limited_class_coverage=data['limited_classes'],exclusions=data['exclusions'],fixture_groups=data['fixture_groups'],compatibility_scope=data['compatibility_scope'],counts=counts,damage_census=data['damage_census'],exact_next_task=nxt,**boundary_flags())
    write_json(OUT/'semantic-sections'/('twilightforest-'+slug+'.json'),section)
    prior=corrected_prior(read_json(OUT/data['previous_draft']),data.get('semantic_corrections',[]));draft=deepcopy(prior);draft.update(checkpoint=cp,starting_sha=data['starting_sha'],effects=prior['effects']+effects,paths=prior['paths']+paths)
    if data.get('semantic_corrections'):
        draft.setdefault('semantic_corrections',[]).extend(data['semantic_corrections'])
    assert len({e['id'] for e in draft['effects']})==len(draft['effects'])
    assert len({p['id'] for p in draft['paths']})==len(draft['paths'])
    draftfile='partial-drafts/twilightforest-'+data['checkpoint_short']+'-partial.json';write_json(OUT/draftfile,draft)
    review=read_json(OUT/'mod-reviews/twilightforest.json');review.update(checkpoint=cp,scope=data['current_scope'],draft_file=draftfile,notes_file='semantic-sections/twilightforest-'+slug+'.json',draft_mechanic_count=len(draft['effects']),draft_path_count=len(draft['paths']),exact_next_task=nxt);write_json(OUT/'mod-reviews/twilightforest.json',review);refresh(cp)
    for f in ['effect-catalog.json','effect-sources.json','delivery-path-matrix.json','vanilla-comparison.json','behavior-primitives.json']:
        d=read_json(OUT/f);d.update(checkpoint=cp,unfinished_review=dict(mod_key='twilightforest',status='PARTIAL',draft_file=draftfile,promoted_records=0));write_json(OUT/f,d)
    decision=read_json(OUT/'research-decision.json');decision.update(checkpoint=cp,next_task=nxt,latest_twilight_subsection_decision=data['decision'],save_mode=False,save_reason='Protect this complete subsection; current usage healthy. Continue the authorized remaining Twilight review after push/live equality.');decision['checkpoints'][data['previous_checkpoint']]=data['starting_sha'];decision['checkpoints'][cp]='Self: exact SHA supplied after push/live verification.';write_json(OUT/'research-decision.json',decision)
    lines=['# '+data['checkpoint_short']+' - '+data['decision'],'',data['compatibility_scope'],'',f"Adds {len(effects)} reviewed packages / {len(paths)} delivery cases. Twilight remains PARTIAL at {len(draft['effects'])}/{len(draft['paths'])} drafts, zero promoted. REVIEW_REQUIRED {counts['review_required']}.",'','## Native contracts','']
    for k,v in facts.items():lines+=['### '+k.replace('_',' ').capitalize(),'',v,'']
    lines+=['## Packages','','| Mechanic | Primary classification |','|---|---|']
    for e in effects:lines+=['| '+e['display_name']+' | '+e['primary_classification']+' |']
    lines+=['','## Custom source callers','','| Type | Amount | Source identity |','|---|---|---|']
    for p in profiles:lines+=['| '+p['type']+' | '+p['amount']+' | '+p['direct_and_causing_entities']+' |']
    lines+=['','## Scope and exclusions','']+['- '+x for x in data['exclusions']]+['','## Future native controls','']+['- '+x for x in data['fixture_groups']]
    lines+=['',f"[Semantic packages and paths](semantic-sections/twilightforest-{slug}.json), [integrity](twilightforest-{slug}-integrity.json), [full validation]({data['checkpoint_short']}-{slug}-validation.json).",'','Exact next task: '+nxt,'']
    (OUT/('twilightforest-'+slug+'-review.md')).write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps(dict(counts=counts,twilight_packages=len(draft['effects']),twilight_paths=len(draft['paths'])),indent=2))


if __name__=='__main__':
    import sys
    assemble(sys.argv[1])
