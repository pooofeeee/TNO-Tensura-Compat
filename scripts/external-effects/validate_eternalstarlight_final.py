"""Final static promotion/source integrity, preserving every previous accepted record."""
from catalog_common import *
from complete_eternalstarlight import build,CP,START,STEMS,ALIASES

VIEWS=[('effect-catalog.json','effects'),('effect-sources.json','sources'),('delivery-path-matrix.json','paths'),('vanilla-comparison.json','comparisons'),('behavior-primitives.json','primitives')]

def validate_final():
    r,m,f,c=build()
    for name,obj in [('mod-reviews/eternalstarlight.json',r),('eternalstarlight-final-promotion-map.json',m),('eternalstarlight-future-runtime-fixtures.json',f),('eternalstarlight-total-source-coverage.json',c)]:assert read_json(OUT/name)==obj,name
    assert r['status']=='COMPLETE' and r['decision']=='ETERNAL_STARLIGHT_COMBAT_SEMANTIC_REVIEW_COMPLETE'
    assert not r['unresolved_native_ambiguities'] and not r['review_required']
    assert m['counts']==dict(input_packages=157,native_cases=274,final_mechanics=127,final_deliveries=274,aliased_input_packages=39,delivery_extensions=2,excluded_combat_cases=0)
    ids={e['id'] for e in r['effects']};pids={p['id'] for p in r['paths']};assert len(ids)==127 and len(pids)==274
    assert {x['path_id'] for x in f['fixtures']}==pids
    assert all(x['runtime_status']=='NOT_RUN' for x in f['fixtures']) and f['runtime_tests']==0
    for s in m['sections']:assert sha256(OUT/s['file'])==s['sha256']
    for s in m['native_effect_reference_files']:assert sha256(OUT/s['file'])==s['sha256']
    assert len(c['custom_damage_types'])==18 and c['factory_caller_count']==29 and len(c['watched_methods'])==274
    cache={}
    def checkref(ref):
        fn=ref['evidence_file']
        if fn not in cache:cache[fn]={w['id']:w for w in read_json(OUT/fn)['witnesses']}
        w=cache[fn][ref['witness_id']];assert ref['entry']==w['entry'] and set(ref['methods'])<={x['name'] for x in w['methods']}
    for row in c['watched_methods']:
        assert row['semantic_sections'] and row['implementation']
        for ref in row['implementation']:checkref(ref)
    actual=set()
    for typ in c['custom_damage_types']:
        assert typ['disposition']=='USED' and typ['requested_amount_formula'] and typ['direct_entity'] and typ['causing_entity']
        assert typ['hurt_return_dependencies_and_secondary_callbacks'] and typ['delivery_paths'] and set(typ['delivery_paths'])<=pids
        assert set(typ['mechanic_ids'])<=ids
        producers=[x for x in typ['callers'] if x['kind']=='ACTUAL_NATIVE_DAMAGE_FACTORY_CALLER'];assert producers
        actual|={(x['entry'],x['method'],x['descriptor']) for x in producers}
    assert len(actual)==29
    byid={e['id']:e for e in r['effects']}
    for e in r['effects']:
        assert e['inspection_status']=='VERIFIED' and e['primary_classification'] in CLASSIFICATIONS
        assert e['components'] and e['implementation'] and e['primary_test_source'] and e['delivery_paths']
        assert e['stage_scaling_needed']==bool(e['single_scaling_point'])
        for ref in e['fact_references']:assert read_json(OUT/ref['file'])['facts'][ref['key']] in e['actual_behavior']
        for ref in e['implementation']:checkref(ref)
    for p in r['paths']:
        assert set(p['labels'])<=set(DELIVERIES) and p['effect_ids'] and set(p['effect_ids'])<=ids
        assert all(p['id'] in byid[e]['delivery_paths'] for e in p['effect_ids'])
    assert not byid['es:numbness_debt']['stage_scaling_needed'] and not byid['es:starfire_status']['stage_scaling_needed']
    assert 'es:weapons:moon_sword' in byid['es:lunar_thorns']['delivery_paths'] and 'es:weapons:tentacle' in byid['es:whip_damage']['delivery_paths']
    assert 'es:lunar:tangled_melee' in byid['es:native_poison_tick']['delivery_paths'] and 'es:lunar:skull_normal_melee' not in byid['es:native_poison_tick']['delivery_paths']
    assert 'es:ebw:wilt_aura' in byid['es:native_wither_tick']['delivery_paths']
    # Preserve exact installed Poison source identity, rather than raw vanilla magic.
    poison=next(w for w in read_json(OUT/'reference-evidence/vv-loader-244.json')['witnesses'] if w['entry'].endswith('/PoisonMobEffect.class'))
    text=str(poison);assert 'POISON_DAMAGE' in text and 'MAGIC' in text and '.hurt(' in text
    preserved={};totals={}
    for name,key in VIEWS:
        old=json.loads(git('show',START+':docs/benchmarks/external-effects-catalog/'+name))[key];now=read_json(OUT/name)[key]
        assert [x for x in now if x['mod_key'] in {o['mod_key'] for o in old}]==old
        preserved[key]=len(old);totals[key]=len(now);es=[x for x in now if x['mod_key']=='eternalstarlight']
        if key=='effects':assert es==r['effects']
        elif key=='paths':assert es==r['paths']
        elif key=='sources':
            assert {x['path_id'] for x in es}==pids
            for x,p in zip(es,r['paths']):assert x['effect_ids']==p['effect_ids'] and x['implementation']==p['implementation']
        elif key=='comparisons':assert {x['effect_id'] for x in es}==ids
        else:
            assert len(es)==sum(len(e['components']) for e in r['effects'])
            for e in r['effects']:
                for x,part in zip([v for v in es if v['effect_id']==e['id']],e['components']):assert all(x[k]==v for k,v in part.items())
    assert preserved==dict(effects=416,sources=1029,paths=1029,comparisons=416,primitives=553)
    ledger=read_json(OUT/'mod-completion-ledger.json');assert next(x for x in ledger['targets'] if x['mod_key']=='eternalstarlight')['state']=='COMPLETE'
    mutable={'docs/external-effects-catalog-research.md','scripts/external-effects/validate.py'}|{'docs/benchmarks/external-effects-catalog/'+n for n in [n for n,_ in VIEWS]+['mod-reviews/eternalstarlight.json','mod-completion-ledger.json','research-decision.json']}
    for line in git('diff','--name-status',START).splitlines():
        status,path=line.split('\t',1);assert status=='A' or (status=='M' and path in mutable),line
    for line in git('diff','--name-status',BASELINE).splitlines():
        status,path=line.split('\t',1);assert status=='A' and path.startswith(('docs/external-effects-catalog-research.md','docs/benchmarks/external-effects-catalog/','scripts/external-effects/')),line
    assert all(not r[k] and not f[k] for k in boundary_flags())
    git('diff','--check',BASELINE)
    return dict(schema='tno.external_effects.es_final_integrity.v1',baseline=BASELINE,checkpoint=CP,starting_sha=START,status='PASS',counts=m['counts'],custom_damage_types=18,actual_factory_callers=29,watched_methods=274,accepted_counts_preserved=preserved,current_view_counts=totals,remaining_native_ambiguities=0,review_required=0,whole_eternalstarlight_complete=True,runtime_tests=0,**boundary_flags())

if __name__=='__main__':
    d=validate_final();write_json(OUT/'eternalstarlight-final-integrity.json',d);print(json.dumps(d,indent=2))
