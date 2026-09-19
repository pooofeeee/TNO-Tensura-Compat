"""Research integrity for reviewed subsets; never grants whole-mod completion."""
from catalog_common import *
from assemble_twilight_frosted import START


def validate_progress():
    def old(path):return json.loads(subprocess.check_output(['git','show',START+':'+path],cwd=ROOT).decode('utf-8'))
    protected=['variantsandventures','cultofazazel','royalvariations','friendsandfoes']
    for key in protected:
        p=f'docs/benchmarks/external-effects-catalog/mod-reviews/{key}.json'
        assert read_json(ROOT/p)==old(p),key
    counts={}
    for name,key in [('effect-catalog.json','effects'),('effect-sources.json','sources'),('delivery-path-matrix.json','paths'),('vanilla-comparison.json','comparisons'),('behavior-primitives.json','primitives')]:
        p='docs/benchmarks/external-effects-catalog/'+name;d=read_json(ROOT/p)
        assert d[key]==old(p)[key],name
        counts[key]=len(d[key])
    sections=[]
    for p in sorted((OUT/'semantic-sections').glob('twilightforest-*.json')):
        s=read_json(p);assert s['baseline']==BASELINE and not s['semantic_coverage_complete'] and not s['promoted_to_catalog']
        ids={e['id'] for e in s['effects']};paths={p['id'] for p in s['paths']}
        assert len(ids)==len(s['effects']) and len(paths)==len(s['paths'])
        for e in s['effects']:
            assert e['primary_classification'] in CLASSIFICATIONS and e['components'] and e['primary_test_source']
            assert set(e['delivery_paths'])=={p['id'] for p in s['paths'] if e['id'] in p['effect_ids']}
        for row in s['effects']+s['paths']+[dict(implementation=s.get('source_registration_evidence',[]))]:
            for ref in row['implementation']:
                w=next(w for w in read_json(OUT/ref['evidence_file'])['witnesses'] if w['id']==ref['witness_id'])
                assert w['entry']==ref['entry'] and set(ref['methods'])<={m['name'] for m in w['methods']}
        for pth in s['paths']:assert set(pth['effect_ids'])<=ids and set(pth['labels'])<=set(DELIVERIES)
        for ref in s.get('comparison_evidence',[]):assert sha256(OUT/ref['evidence_file'])==ref['sha256']
        for profile in s.get('damage_profiles',[]):
            for caller in profile['callers']:
                assert any(caller['entry']==r['entry'] and caller['method'] in r['methods'] for e in s['effects'] for r in e['implementation'])
        sections.append(dict(file=p.name,effects=len(ids),paths=len(paths)))
    for p in (OUT/'reference-routing').glob('twilight-*.json'):
        for r in read_json(p)['raw_fallbacks']:
            assert sha256(r['absent_from'])==r['archive_sha256']
            with zipfile.ZipFile(r['absent_from']) as z:assert r['entry'] not in z.namelist()
    compat=read_json(OUT/'compat-findings/twilightforest-frosted.json')
    assert len(compat['candidate_jars'])==4 and compat['generic_attribution']=='GENERIC_CONDITIONAL_PRESENT'
    for c in compat['candidate_jars']:
        assert not c['twilight_name_hits']
        for i in c['reused_index_inputs']:assert sha256(i['path'])==i['sha256']
    for h in compat['hooks']:
        for ref in h['implementation']:
            w=next(w for w in read_json(OUT/ref['evidence_file'])['witnesses'] if w['id']==ref['witness_id'])
            assert ref['entry']==w['entry'] and set(ref['methods'])<={m['name'] for m in w['methods']}
    ledger={r['mod_key']:r for r in read_json(OUT/'mod-completion-ledger.json')['targets']}
    assert ledger['twilightforest']['state']=='PARTIAL' and ledger['iceandfire']['state']=='UNSTARTED'
    assert all(ledger[k]['state']=='COMPLETE' for k in protected+['tensura'])
    return dict(schema='tno.external_effects.twilight_progress_integrity.v1',status='PASS',immutable_start=START,
                sections=sections,accepted_counts_unchanged=counts,promoted_twilight_records=0,iceandfire_started=False,**boundary_flags())


if __name__=='__main__':
    r=validate_progress();write_json(OUT/'twilightforest-progress-integrity.json',r);print(json.dumps(r,indent=2))
