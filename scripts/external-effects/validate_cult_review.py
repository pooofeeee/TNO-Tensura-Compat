"""Final Cult evidence, reference, registry, path and attribution integrity checks."""
from catalog_common import *
from collections import Counter
from functools import lru_cache

@lru_cache(None)
def evidence(file):return read_json(OUT/file)

def check_reference(ref):
    obj=evidence(ref['evidence_file'])
    if 'witness_id' in ref:
        row=next(w for w in obj['witnesses'] if w['id']==ref['witness_id'])
        assert row['entry']==ref['entry']
    else:
        row=next(w for w in obj.get('classes',obj.get('witnesses',[])) if w.get('class_name')==ref['class_name'])
    assert ref['methods'] and set(ref['methods'])<={m['name'] for m in row.get('methods',[])}

def validate_cult():
    r=read_json(OUT/'mod-reviews/cultofazazel.json')
    assert r['status']=='COMPLETE' and r['decision']=='CULT_OF_AZAZEL_SEMANTIC_REVIEW_COMPLETE'
    assert r['baseline']==BASELINE and not r['unresolved_native_ambiguities']
    effects={e['id']:e for e in r['effects']}; paths={p['id']:p for p in r['paths']}
    assert len(effects)==len(r['effects'])==r['semantic_effect_count']
    assert len(paths)==len(r['paths'])==r['distinct_delivery_path_count']
    assert dict(Counter(e['primary_classification'] for e in effects.values()))==r['classification_counts']
    assert r['review_required_count']==sum(e['primary_classification']=='REVIEW_REQUIRED' for e in effects.values())==0
    compat=read_json(OUT/r['compatibility_attribution_file']);hooks={h['id']:h for h in compat['hooks']}
    assert len(hooks)==len(compat['hooks'])
    for h in hooks.values():
        assert h['condition'] and h['change'] and set(h['effect_ids'])<=set(effects)
        for ref in h['implementation']:check_reference(ref)
    for e in effects.values():
        assert e['inspection_status']=='VERIFIED' and e['pending']==[] and e['unresolved_ambiguities']==[]
        assert e['primary_classification'] in CLASSIFICATIONS
        for key in ['actual_behavior','closest_vanilla_equivalent','vanilla_similarities','vanilla_differences','components','eligibility','hurt_return_dependency','duration_and_tick_semantics','custom_state','primary_test_source','confidence']:
            assert e[key],(e['id'],key)
        for ref in e['implementation']+e['vanilla_implementation']:check_reference(ref)
        for c in e['components']:
            assert c['primitive'] and c['formula'] and c['implementation'] and c['vanilla_implementation']
            assert isinstance(c['numerical_parameters'],dict) and isinstance(c['binary_parameters'],list)
        assert set(e['delivery_paths'])=={pid for pid,p in paths.items() if e['id'] in p['effect_ids']}
        expected={h['id'] for h in hooks.values() if e['id'] in h['effect_ids']}
        assert set(e['compatibility_hook_ids'])==expected
        assert e['compatibility_attribution']==('GENERIC_CONDITIONAL_PRESENT' if expected else 'NONE_PROVEN')
    for p in paths.values():
        assert p['status']=='VERIFIED' and set(p['effect_ids'])<=set(effects)
        assert set(p['labels'])<=set(DELIVERIES) and p['setup'] and p['primary_source']
        for ref in p['implementation']:check_reference(ref)
    for group in r['source_chains']+r['exclusions']:
        for ref in group['evidence']:check_reference(ref)
    fixtures=r['minimum_future_sources']['fixtures']
    assert len(fixtures)==r['minimum_future_sources']['fixture_family_count']
    fixture_paths=[p for f in fixtures for p in f['path_ids']]
    assert len(fixture_paths)==len(set(fixture_paths)) and set(fixture_paths)==set(paths)
    inv=read_json(OUT/'jar-inventory.json');target=next(t for t in inv['targets'] if t['key']=='cultofazazel')
    from classfile import ClassFile
    with zipfile.ZipFile(target['path']) as jar:
        cov=r['coverage'];assert cov['jar_sha256']==target['sha256']
        assert {x['entry'] for x in cov['classes']}=={n for n in jar.namelist() if n.endswith('.class')}
        assert {x['entry'] for x in cov['resources']}=={n for n in jar.namelist() if n.startswith('data/') and n.endswith('.json')}
        for row in cov['classes']+cov['resources']:
            assert byte_hash(jar.read(row['entry']))==row['sha256'] and row['disposition']
        assert len(cov['classes'])==151 and len(cov['resources'])==62
        names=set(ClassFile(jar.read('com/benji/netherman/NetherExp.class')).strings())
        for e in list(effects.values())+r['exclusions']:
            for rid in e.get('registry_ids',[]):
                if rid.startswith('netherman:'):
                    name=rid.split(':')[1]
                    assert name in names or 'data/netherman/worldgen/structure/'+name+'.json' in jar.namelist(),rid
    # Reassembly must reproduce the final records; it cannot silently promote the
    # partial draft or mutate already completed Variants & Ventures evidence.
    import complete_cult as builder
    builder.finalize()
    assert builder.E==r['effects'] and builder.P==r['paths']
    old=json.loads(git('show',r['starting_sha']+':docs/benchmarks/external-effects-catalog/mod-reviews/variantsandventures.json'))
    assert old==read_json(OUT/'mod-reviews/variantsandventures.json')
    primitives=read_json(OUT/'behavior-primitives.json')['primitives']
    assert len({p['id'] for p in primitives})==len(primitives)
    assert {p['effect_id'] for p in primitives if p['mod_key']=='cultofazazel'}==set(effects)
    ledger=read_json(OUT/'mod-completion-ledger.json')
    cult=next(t for t in ledger['targets'] if t['mod_key']=='cultofazazel')
    assert cult['state']=='COMPLETE' and cult['semantic_effect_count']==len(effects)
    for k in boundary_flags():assert r[k] is False
    return dict(status='PASS',mechanics=len(effects),paths=len(paths),classifications=r['classification_counts'],
        native_review_required=0,fixture_families=len(fixtures),classes=151,resources=62,
        compatibility_counts=dict(Counter(e['compatibility_attribution'] for e in effects.values())))

if __name__=='__main__':
    result=validate_cult();write_json(OUT/'cult-final-integrity.json',result);print(json.dumps(result,indent=2))
