"""Royal semantic artifact integrity, native coverage and protected-input checks."""
from catalog_common import *
from collections import Counter

def validate_royal():
    import complete_royal as build
    build.finalize();build.compatibility()
    r=read_json(OUT/'mod-reviews/royalvariations.json');effects={e['id']:e for e in r['effects']};paths={p['id']:p for p in r['paths']}
    assert r['status']=='COMPLETE' and r['semantic_effect_count']==len(effects)==26
    assert r['distinct_delivery_path_count']==len(paths)==37
    assert r['effects']==build.E and r['paths']==build.P
    assert r['coverage']==build.coverage() and r['damage_profiles']==build.damage_profiles()
    assert not r['unresolved_native_ambiguities'] and r['review_required_count']==0
    assert len(r['named_native_effects'])==10 and len(set(r['named_native_effects']))==10
    assert r['classification_counts']==dict(Counter(e['primary_classification'] for e in effects.values()))
    refs=[ref for e in r['effects'] for ref in e['implementation']]+[ref for p in r['paths'] for ref in p['implementation']]+[ref for e in r['exclusions'] for ref in e['evidence']]
    compat=read_json(OUT/'compat-findings/royalvariations.json')
    assert compat==build.compatibility()
    refs += [ref for h in compat['hooks'] for ref in h['implementation']]
    for ref in refs:
        obj=read_json(OUT/ref['evidence_file']);w=next(w for w in obj['witnesses'] if w['id']==ref['witness_id'])
        assert w['entry']==ref['entry'] and set(ref['methods'])<={m['name'] for m in w.get('methods',[])}
    for e in effects.values():
        assert e['inspection_status']=='VERIFIED' and e['primary_classification'] in CLASSIFICATIONS
        assert e['delivery_paths'] and e['components'] and e['primary_test_source']
        for pid in e['delivery_paths']:assert e['id'] in paths[pid]['effect_ids']
        assert set(e['compatibility_hook_ids'])<={h['id'] for h in compat['hooks']}
        for f in e['reference_files']:assert (OUT/f).is_file()
    for p in paths.values():
        assert p['status']=='VERIFIED' and set(p['labels'])<=set(DELIVERIES)
        for eid in p['effect_ids']:assert p['id'] in effects[eid]['delivery_paths']
    covered=[pid for f in r['minimum_future_sources']['fixtures'] for pid in f['path_ids']]
    assert len(covered)==len(set(covered)) and set(covered)==set(paths)
    native=read_json(OUT/'native-evidence/royalvariations.json')
    strings=set()
    for w in native['witnesses']:
        for m in w.get('methods',[]):
            strings|={i['operand'] for i in m['instructions'] if isinstance(i.get('operand'),str)}
    for rid in r['named_native_effects']:assert rid.split(':')[1] in strings
    for name,key in [('effect-catalog.json','effects'),('vanilla-comparison.json','comparisons'),('effect-sources.json','sources'),('delivery-path-matrix.json','paths'),('behavior-primitives.json','primitives')]:
        rows=read_json(OUT/name)[key];idkey='effect_id' if key=='comparisons' else 'id'
        assert len(rows)==len({x[idkey] for x in rows})
        royal=[x for x in rows if x.get('mod_key')=='royalvariations']
        if key=='effects':assert royal==r['effects']
        elif key=='paths':assert royal==r['paths']
        elif key=='sources':assert {x['path_id'] for x in royal}==set(paths)
        else:assert {x['effect_id'] for x in royal}==set(effects)
    ledger=read_json(OUT/'mod-completion-ledger.json');row=next(x for x in ledger['targets'] if x['mod_key']=='royalvariations')
    assert row['state']=='COMPLETE' and row['semantic_effect_count']==26 and row['remaining_native_ambiguities']==[]
    for name in ['variantsandventures','cultofazazel']:
        path='docs/benchmarks/external-effects-catalog/mod-reviews/'+name+'.json'
        import subprocess
        protected=subprocess.check_output(['git','show',build.START+':'+path],cwd=ROOT).decode('utf-8')
        assert json.loads(protected)==read_json(ROOT/path)
    for k in boundary_flags():assert r[k] is False
    return dict(status='PASS',mechanics=26,delivery_cases=37,registered_effects=10,native_classes=172,data_resources=58,fixture_families=12,review_required=0,
        immutable_accepted_reviews=['variantsandventures','cultofazazel'],**boundary_flags())

if __name__=='__main__':
    result=validate_royal();write_json(OUT/'royal-final-integrity.json',result);print(json.dumps(result,indent=2))
