from catalog_common import *
from complete_bomd import build,KEY,CP,START
from native_evidence import collect
VIEWS=[('effect-catalog.json','effects'),('effect-sources.json','sources'),('delivery-path-matrix.json','paths'),('vanilla-comparison.json','comparisons'),('behavior-primitives.json','primitives')]

def validate_final():
    r,m,f,c=build()
    for name,obj in [('mod-reviews/'+KEY+'.json',r),('bomd-final-promotion-map.json',m),('bomd-future-runtime-fixtures.json',f),('bomd-total-source-coverage.json',c)]:assert read_json(OUT/name)==obj,name
    assert r['status']=='COMPLETE' and r['decision']=='BOMD_COMBAT_SEMANTIC_REVIEW_COMPLETE' and not r['unresolved_native_ambiguities'] and len(r['review_required'])==8
    assert m['counts']==dict(input_packages=51,native_cases=86,final_mechanics=44,final_deliveries=85,aliased_input_packages=6,delivery_extensions=4,aliased_duplicate_paths=1,excluded_combat_cases=0)
    ids={e['id'] for e in r['effects']};pids={p['id'] for p in r['paths']};assert len(ids)==44 and len(pids)==85
    assert {p['path_id'] for p in f['fixtures']}==pids and all(p['runtime_status']=='NOT_RUN' for p in f['fixtures'])
    assert {p['original_id'] for p in m['path_dispositions']}=={pid for p in r['paths'] for pid in p['source_case_ids']}
    cache={}
    def refcheck(ref):
        file=ref['evidence_file']
        if file not in cache:cache[file]={w['id']:w for w in read_json(OUT/file)['witnesses']}
        w=cache[file][ref['witness_id']];assert w['entry']==ref['entry'] and set(ref['methods'])<={m['name'] for m in w['methods']}
    for e in r['effects']:
        assert e['inspection_status']=='VERIFIED' and e['primary_classification'] in CLASSIFICATIONS and e['components'] and e['implementation'] and e['delivery_paths']
        assert bool(e['single_scaling_point'])==e['stage_scaling_needed']
        for ref in e['implementation']:refcheck(ref)
        for ref in e['fact_references']:assert read_json(OUT/ref['file'])['facts'][ref['key']] in e['actual_behavior']
    byid={e['id']:e for e in r['effects']}
    for p in r['paths']:
        assert set(p['labels'])<=set(DELIVERIES) and p['effect_ids'] and set(p['effect_ids'])<=ids
        assert all(p['id'] in byid[e]['delivery_paths'] for e in p['effect_ids'])
    assert len(c['watched_methods'])==37 and len(c['native_effect_reference_methods'])==8 and len(c['custom_effect_registry_candidates'])==4
    for row in c['watched_methods']+c['native_effect_reference_methods']+c['custom_effect_registry_candidates']:
        assert row['disposition'] and row['semantic_sections'] and row['implementation']
        for ref in row['implementation']:refcheck(ref)
    assert len(c['custom_damage_types'])==1 and c['actual_custom_hurt_producers']==5
    d=c['custom_damage_types'][0];assert d['disposition']=='USED' and len(d['callers'])==5 and len(d['key_readers'])==1 and not d['tags']
    assert set(d['mechanic_ids'])<=ids and set(d['delivery_paths'])<=pids and len(d['delivery_paths'])==6
    assert 'bomd:equipment:monolith' in byid['bomd:native_explosion']['delivery_paths']
    assert 'bomd:blossom:spore_direct' in byid['bomd:native_thrown']['delivery_paths']
    assert 'bomd:shared:blossom_idle_heal' in byid['bomd:capped_heal']['delivery_paths'] and 'bomd:blossom:idle_heal' not in pids
    assert not byid['bomd:pearl_zero']['stage_scaling_needed']
    assert collect(read_json(OUT/'native-specifications/bomd-closure.json'))==read_json(OUT/'native-evidence/bomd-closure.json')
    preserved={};totals={}
    for name,key in VIEWS:
        old=json.loads(git('show',START+':docs/benchmarks/external-effects-catalog/'+name))[key];now=read_json(OUT/name)[key]
        assert [x for x in now if x['mod_key'] in {v['mod_key'] for v in old}]==old
        preserved[key]=len(old);totals[key]=len(now);added=[x for x in now if x['mod_key']==KEY]
        if key=='effects':assert added==r['effects']
        elif key=='paths':assert added==r['paths']
        elif key=='sources':
            assert {x['path_id'] for x in added}==pids
            for x,p in zip(added,r['paths']):assert x['effect_ids']==p['effect_ids'] and x['implementation']==p['implementation']
        elif key=='comparisons':assert {x['effect_id'] for x in added}==ids
        else:
            assert len(added)==sum(len(e['components']) for e in r['effects'])
            for e in r['effects']:
                for x,part in zip([v for v in added if v['effect_id']==e['id']],e['components']):assert all(x[k]==v for k,v in part.items())
    assert preserved==dict(effects=625,sources=1535,paths=1535,comparisons=625,primitives=827)
    assert next(t for t in read_json(OUT/'mod-completion-ledger.json')['targets'] if t['mod_key']==KEY)['state']=='COMPLETE'
    mutable={'docs/external-effects-catalog-research.md','scripts/external-effects/validate.py'}|{'docs/benchmarks/external-effects-catalog/'+n for n in [n for n,_ in VIEWS]+['mod-reviews/'+KEY+'.json','mod-completion-ledger.json','research-decision.json']}
    for line in git('diff','--name-status',START).splitlines():
        status,path=line.split('\t',1);assert status=='A' or (status=='M' and path in mutable),line
    for line in git('diff','--name-status',BASELINE).splitlines():
        status,path=line.split('\t',1);assert status=='A' and path.startswith(('docs/external-effects-catalog-research.md','docs/benchmarks/external-effects-catalog/','scripts/external-effects/')),line
    assert all(not r[k] and not f[k] for k in boundary_flags()) and r['runtime_tests']==0 and f['runtime_tests']==0
    git('diff','--check',BASELINE)
    return dict(schema='tno.external_effects.bomd_final_integrity.v1',baseline=BASELINE,checkpoint=CP,starting_sha=START,status='PASS',counts=m['counts'],custom_damage_types=1,actual_custom_hurt_producers=5,watched_methods=37,native_effect_references=8,accepted_counts_preserved=preserved,current_view_counts=totals,remaining_native_ambiguities=0,future_integration_review_items=8,whole_bomd_complete=True,runtime_tests=0,**boundary_flags())

if __name__=='__main__':
    d=validate_final();write_json(OUT/'bomd-final-integrity.json',d);print(json.dumps(d,indent=2))
