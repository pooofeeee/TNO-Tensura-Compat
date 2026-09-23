"""Validate complete promotion, total source coverage and exact historical preservation."""
from catalog_common import *
from complete_iceandfire import build,CP,STEMS,ALIASES,START
from iceandfire_promotion_migration import protected_rows,permitted_tool_change,validate_migration

VIEWS=[('effect-catalog.json','effects'),('effect-sources.json','sources'),('delivery-path-matrix.json','paths'),('vanilla-comparison.json','comparisons'),('behavior-primitives.json','primitives')]

def validate_final():
    r,m,f=build()
    assert r==read_json(OUT/'mod-reviews/iceandfire.json')
    assert m==read_json(OUT/'iceandfire-final-promotion-map.json')
    assert f==read_json(OUT/'iceandfire-future-runtime-fixtures.json')
    assert r['status']=='COMPLETE' and not r['review_required'] and not r['unresolved_native_ambiguities']
    assert m['counts']==dict(normalized_input_packages=90,native_cases=228,final_mechanics=81,final_deliveries=228,aliased_input_packages=12,excluded_combat_cases=0)
    assert {p['id'] for p in r['paths']}=={p['path_id'] for p in f['fixtures']}
    assert len({e['id'] for e in r['effects']})==81 and len({p['id'] for p in r['paths']})==228
    assert len({json.dumps((e['actual_behavior'],e['single_scaling_point'],e['stage_reason']),sort_keys=True) for e in r['effects']})==81,'Duplicate canonical combat contract'
    assert sum(e['stage_scaling_needed'] for e in r['effects'])==35
    assert sum(len(e['components']) for e in r['effects'])==88
    assert all(p['runtime_status']=='NOT_RUN' for p in f['fixtures']) and f['runtime_tests']==0
    assert all(not r[k] and not f[k] for k in boundary_flags())
    cache={};facts={}
    for e in r['effects']:
        assert e['primary_classification'] in CLASSIFICATIONS and e['primary_classification']!='REVIEW_REQUIRED'
        assert e['components'] and e['implementation'] and e['delivery_paths'] and e['primary_test_source']
        assert e['stage_scaling_needed']==bool(e['single_scaling_point'])
        assert set(e['tno_categories'])<={'NUMERIC_SCALABLE','BINARY','COMPOSITE','VANILLA_ROUTED','CUSTOM_ROUTED','ADMISSION_GATED','NO_STAGE_VALUE'}
        for ref in e['fact_references']:
            facts.setdefault(ref['file'],read_json(OUT/ref['file'])['facts'])
            assert facts[ref['file']][ref['key']] in e['actual_behavior']
        for ref in e['implementation']:
            if ref['evidence_file'] not in cache:cache[ref['evidence_file']]={w['id']:w for w in read_json(OUT/ref['evidence_file'])['witnesses']}
            w=cache[ref['evidence_file']][ref['witness_id']]
            assert ref['entry']==w['entry'] and set(ref['methods'])<={method['name'] for method in w['methods']}
    byid={e['id']:e for e in r['effects']}
    assert not byid['iaf:gorgon_petrification']['stage_scaling_needed']
    assert not byid['iaf:frozen']['stage_scaling_needed'] and not byid['iaf:siren_song']['stage_scaling_needed']
    assert len(byid['iaf:frozen']['delivery_paths'])==13 and len(byid['iaf:dragon_elemental_damage']['delivery_paths'])==21
    assert 'iaf:control:flesh_fire' in byid['iaf:native_ignition']['delivery_paths']
    assert 'iaf:control:flesh_lightning' not in byid['iaf:native_ignition']['delivery_paths']
    assert 'iaf:control:flesh_lightning' in byid['iaf:native_lightning']['delivery_paths']
    assert 'iaf:control:flesh_fire' not in byid['iaf:native_lightning']['delivery_paths']
    assert {'iaf:frozen-weapon:dragonbone_sword_ice'}<=set(byid['iaf:weapon_bonus']['delivery_paths'])
    corrected=byid['iaf:cockatrice_control']['fact_references']
    assert dict(file='iceandfire-r2g7-worm-cyclops.json',key='shared_callback_clarification') in corrected
    assert dict(file='iceandfire-r2g6-cockatrice.json',key='target_control') in corrected
    assert corrected.index(dict(file='iceandfire-r2g7-worm-cyclops.json',key='shared_callback_clarification'))>corrected.index(dict(file='iceandfire-r2g6-cockatrice.json',key='target_control'))
    for p in r['paths']:
        assert set(p['labels'])<=set(DELIVERIES) and p['effect_ids']
        assert all(p['id'] in byid[eid]['delivery_paths'] for eid in p['effect_ids'])
    preserved={};totals={}
    for name,key in VIEWS:
        old=json.loads(git('show',START+':docs/benchmarks/external-effects-catalog/'+name))[key]
        rows=read_json(OUT/name)[key];preserved[key]=len(protected_rows(rows,old));totals[key]=len(rows)
        accepted=[row for row in rows if row['mod_key']=='iceandfire']
        if key=='effects':assert accepted==r['effects']
        elif key=='paths':assert accepted==r['paths']
        elif key=='sources':
            assert {x['path_id'] for x in accepted}=={p['id'] for p in r['paths']}
            for x in accepted:
                p=next(p for p in r['paths'] if p['id']==x['path_id']);assert x['effect_ids']==p['effect_ids'] and x['implementation']==p['implementation']
        elif key=='comparisons':
            assert {x['effect_id'] for x in accepted}==set(byid)
            for x in accepted:assert x['components']==byid[x['effect_id']]['components']
        else:
            assert len(accepted)==sum(len(e['components']) for e in r['effects'])
            for e in r['effects']:
                actual=[p for p in accepted if p['effect_id']==e['id']]
                for p,c in zip(actual,e['components']):assert all(p[k]==v for k,v in c.items())
    assert preserved==dict(effects=335,sources=801,paths=801,comparisons=335,primitives=465)
    migration=validate_migration();assert migration==read_json(OUT/'iceandfire-validator-migration.json')
    mutable={'docs/external-effects-catalog-research.md','scripts/external-effects/validate.py'}|{'docs/benchmarks/external-effects-catalog/'+n for n in [n for n,_ in VIEWS]+['mod-reviews/iceandfire.json','mod-completion-ledger.json','research-decision.json']}
    for line in git('diff','--name-status',START).splitlines():
        status,path=line.split('\t',1)
        assert status=='A' or (status=='M' and (path in mutable or permitted_tool_change(path))),line
    for line in git('diff','--name-status',BASELINE).splitlines():
        status,path=line.split('\t',1)
        assert status=='A' and path.startswith(('docs/external-effects-catalog-research.md','docs/benchmarks/external-effects-catalog/','scripts/external-effects/')),line
    git('diff','--check',BASELINE)
    return dict(schema='tno.external_effects.iaf_final_integrity.v1',baseline=BASELINE,starting_sha=START,checkpoint=CP,status='PASS',counts=m['counts'],accepted_counts_preserved=preserved,current_view_counts=totals,all_original_combat_paths_retained=True,all_named_fixtures_preserved=True,exact_tooling_migration='iceandfire-validator-migration.json',remaining_native_ambiguities=0,review_required=0,whole_iceandfire_complete=True,runtime_tests=0,**boundary_flags())

if __name__=='__main__':
    d=validate_final();write_json(OUT/'iceandfire-final-integrity.json',d);print(json.dumps(d,indent=2))
