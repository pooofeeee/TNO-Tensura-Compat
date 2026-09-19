"""Validate Friends & Foes evidence links, coverage, views and protected inputs."""
from catalog_common import *
import subprocess

def validate_friends():
    import complete_friends as b
    r=read_json(OUT/'mod-reviews/friendsandfoes.json')
    assert r==b.build_review()
    assert r['status']=='COMPLETE' and r['semantic_effect_count']==31 and r['distinct_delivery_path_count']==46
    effects={e['id']:e for e in r['effects']};paths={p['id']:p for p in r['paths']}
    assert len(effects)==31 and len(paths)==46 and r['review_required_count']==0
    assert r['named_native_effects']==['friendsandfoes:reach'] and r['registered_combat_custom_effects']==[]
    refs=[v for e in r['effects'] for v in e['implementation']]+[v for p in r['paths'] for v in p['implementation']]+[v for x in r['exclusions'] for v in x['evidence']]
    native_cache={f:{x['id']:x for x in read_json(OUT/f)['witnesses']} for f in {ref['evidence_file'] for ref in refs}}
    for ref in refs:
        w=native_cache[ref['evidence_file']][ref['witness_id']]
        assert w['entry']==ref['entry'] and set(ref['methods'])<={m['name'] for m in w.get('methods',[])}
    for e in effects.values():
        assert e['primary_classification'] in CLASSIFICATIONS and e['inspection_status']=='VERIFIED'
        assert e['delivery_paths'] and e['primary_test_source'] and e['components'] and not e['unresolved_ambiguities']
        for pid in e['delivery_paths']:assert e['id'] in paths[pid]['effect_ids']
        for f in e['reference_files']:assert (OUT/f).is_file()
    for p in paths.values():
        assert set(p['labels'])<=set(DELIVERIES)
        for eid in p['effect_ids']:assert p['id'] in effects[eid]['delivery_paths']
    covered=[p for x in r['minimum_future_sources']['fixtures'] for p in x['path_ids']]
    assert len(covered)==len(set(covered)) and set(covered)==set(paths)
    sources=r['minimum_future_sources']['sources']
    assert r['minimum_future_sources']['concrete_source_count']==len(sources)==15
    assert len({s['id'] for s in sources})==15
    assert {pid for s in sources for pid in s['path_ids']}==set(paths)
    for source in sources:
        assert source['necessity_witness_path'] in source['path_ids']
        assert source['necessity_reason']
    cov=r['coverage'];assert cov['class_count']==341 and cov['resource_count']==237
    assert {x['entry'] for x in cov['classes']+cov['resources']}=={w['entry'] for w in b.W.values()}
    # Native code guards against name-based mistaken conclusions.
    assert not {'addAdditionalSaveData','readAdditionalSaveData'} & {m['name'] for m in b.W[b.RA]['methods']}
    assert not any('/damage_type/' in w['entry'] and w['entry'].startswith('data/friendsandfoes/') for w in b.W.values())
    cfg=read_json(OUT/'friendsandfoes-config-snapshot.json');assert sha256(cfg['path'])==cfg['sha256']
    assert read_json(cfg['path'])==cfg['data'] and cfg['data']['enableWildfire'] is False
    for name,key in [('effect-catalog.json','effects'),('effect-sources.json','sources'),('delivery-path-matrix.json','paths'),('vanilla-comparison.json','comparisons'),('behavior-primitives.json','primitives')]:
        rows=read_json(OUT/name)[key];idkey='effect_id' if key=='comparisons' else 'id'
        assert len(rows)==len({x[idkey] for x in rows})
        owned=[x for x in rows if x.get('mod_key')=='friendsandfoes']
        if key=='effects':assert owned==r['effects']
        elif key=='paths':assert owned==r['paths']
        elif key=='sources':assert {x['path_id'] for x in owned}==set(paths)
        else:assert {x['effect_id'] for x in owned}==set(effects)
        old=json.loads(subprocess.check_output(['git','show',b.START+':docs/benchmarks/external-effects-catalog/'+name],cwd=ROOT).decode('utf-8'))[key]
        protected_mods={x.get('mod_key') for x in old}
        assert [x for x in rows if x.get('mod_key') in protected_mods]==old
    for name in ['variantsandventures','cultofazazel','royalvariations']:
        path='docs/benchmarks/external-effects-catalog/mod-reviews/'+name+'.json'
        assert json.loads(subprocess.check_output(['git','show',b.START+':'+path],cwd=ROOT).decode('utf-8'))==read_json(ROOT/path)
    ledger=read_json(OUT/'mod-completion-ledger.json');row=next(x for x in ledger['targets'] if x['mod_key']=='friendsandfoes')
    assert row['state']=='COMPLETE' and row['semantic_effect_count']==31 and not row['remaining_native_ambiguities']
    # Other targets may advance later; this validator protects the Friends checkpoint.
    for key in boundary_flags():assert r[key] is False
    return dict(status='PASS',mechanics=31,delivery_paths=46,fixture_families=13,concrete_source_families=15,native_classes=341,data_resources=237,registered_custom_effects=1,registered_combat_custom_effects=0,review_required=0,protected_reviews_unchanged=['variantsandventures','cultofazazel','royalvariations'],twilight_started=False,**boundary_flags())

if __name__=='__main__':
    result=validate_friends();write_json(OUT/'friendsandfoes-final-integrity.json',result);print(json.dumps(result,indent=2))
