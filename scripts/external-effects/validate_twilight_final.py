"""Final promotion integrity: total provenance, distinct records, native references and scope."""
from functools import lru_cache
from collections import Counter
from catalog_common import *
from complete_twilight import build,START,DRAFT,PLAN
from twilight_promotion_migration import validate_migration,NAMES


@lru_cache(None)
def evidence(name):return read_json(OUT/name)


def check_ref(ref):
    doc=evidence(ref['evidence_file'])
    witness=next(w for w in doc['witnesses'] if w['id']==ref['witness_id'])
    assert ref['entry']==witness['entry']
    assert set(ref.get('methods',[]))<={m['name'] for m in witness.get('methods',[])}


def validate_final():
    review,manifest,fixtures=build()
    assert review==read_json(OUT/'mod-reviews/twilightforest.json')
    assert manifest==read_json(OUT/'twilightforest-final-promotion-map.json')
    assert fixtures==read_json(OUT/'twilightforest-future-runtime-fixtures.json')
    assert validate_migration()==read_json(OUT/'twilightforest-validator-migration.json')
    d=evidence(DRAFT);plan=evidence(PLAN);effects={e['id']:e for e in review['effects']};paths={p['id']:p for p in review['paths']}
    counts=manifest['counts']
    assert counts==dict(original_mechanics=277,original_cases=1014,final_mechanics=219,final_deliveries=640,excluded_mechanics=49,aliased_mechanics=10,excluded_cases=275,folded_cases=99)
    assert len(effects)==len(review['effects'])==219 and len(paths)==len(review['paths'])==640
    assert set(effects).isdisjoint(plan['excluded_effects']) and set(effects).isdisjoint(plan['effect_aliases'])
    assert {r['original_effect_id'] for r in manifest['effect_dispositions']}=={e['id'] for e in d['effects']}
    assert {r['original_path_id'] for r in manifest['path_dispositions']}=={p['id'] for p in d['paths']}
    assert len(manifest['effect_dispositions'])==277 and len(manifest['path_dispositions'])==1014
    for row in manifest['effect_dispositions']:
        assert set(row['canonical_effect_ids'])<=set(effects) and row['reason']
    for row in manifest['path_dispositions']:
        if row['canonical_path_id']:
            p=paths[row['canonical_path_id']]
            assert row['original_path_id'] in p['source_case_ids'] and set(row['canonical_effect_ids'])<=set(p['effect_ids'])
        else:assert row['status']=='EXCLUDED_NONCOMBAT' and row['reason']
    assert Counter(e['primary_classification'] for e in effects.values())==review['classification_counts']
    assert not review['review_required'] and not review['unresolved_native_ambiguities'] and not review['remaining_native_ambiguities']
    assert review['named_native_effects']==['twilightforest:frosted']
    assert 'REVIEW_REQUIRED' not in review['classification_counts']
    signatures=[]
    for e in effects.values():
        assert e['inspection_status']=='VERIFIED' and e['native_status']=='STATIC_VERIFIED' and not e['pending']
        assert e['primary_classification'] in CLASSIFICATIONS and e['components'] and e['primary_test_source']
        assert e['closest_vanilla_equivalent'] and e['vanilla_similarities'] and e['vanilla_differences']
        assert set(e['delivery_paths'])=={p['id'] for p in paths.values() if e['id'] in p['effect_ids']}
        for ref in e['implementation']:check_ref(ref)
        # Shared section prose can describe two distinct payloads. Compare the
        # complete parameterized contracts, ignoring package/primitive names.
        signatures.append(json.dumps(dict(behavior=e['actual_behavior'],components=[{k:v for k,v in c.items() if k!='primitive'} for c in e['components']]),sort_keys=True))
    assert len(signatures)==len(set(signatures)),'Exact duplicate canonical mechanic contracts'
    for p in paths.values():
        assert p['status']=='VERIFIED' and p['primary_source'] and p['setup'] and p['fixture_controls']
        assert set(p['labels'])<=set(DELIVERIES) and set(p['effect_ids'])<=set(effects)
        assert [v['original_path_id'] for v in p['native_contract_variants']]==p['source_case_ids']
        assert all(v['native_contract'] for v in p['native_contract_variants'])
        for ref in p['implementation']:check_ref(ref)
    assert {f['path_id'] for f in fixtures['fixtures']}==set(paths)
    assert len(fixtures['fixtures'])==len(paths) and all(f['runtime_status']=='NOT_RUN' for f in fixtures['fixtures'])
    dup=evidence('twilightforest-final-duplicate-review.json')
    assert dup['reviewed_same_prose_candidates']==76 and len(dup['retained_groups'])==51
    for row in dup['retained_groups']:
        assert len(row['canonical_path_ids'])>1 and set(row['canonical_path_ids'])<=set(paths) and row['reason']
    # IDs are mechanic package labels, not invented registry entries. All explicit
    # registry IDs must have exact installed registration/resource witnesses.
    registered={rid for e in effects.values() for rid in e.get('registry_ids',[])}
    assert registered=={'twilightforest:frosted','twilightforest:frozen','twilightforest:ice_bomb'}
    native=evidence('native-evidence/twilightforest-r2f1-partial.json')['witnesses']
    mob=next(w for w in native if w['entry']=='twilightforest/init/TFMobEffects.class')
    assert any(i.get('operand')=='frosted' for m in mob['methods'] for i in m.get('instructions',[]))
    closure=evidence('twilightforest-r2f8y-damage-type-closure.json')
    assert closure['used']==closure['declared']==40 and not closure['unfinished_types']
    target=next(t for t in evidence('jar-inventory.json')['targets'] if t['key']=='twilightforest')
    assert sha256(target['path'])==target['sha256']
    with zipfile.ZipFile(target['path']) as jar:
        assert 'data/twilightforest/damage_type/frozen.json' in jar.namelist()
        assert 'assets/twilightforest/models/item/ice_bomb.json' in jar.namelist()
    preserved={}
    for name,key in [('effect-catalog.json','effects'),('effect-sources.json','sources'),('delivery-path-matrix.json','paths'),('vanilla-comparison.json','comparisons'),('behavior-primitives.json','primitives')]:
        old=json.loads(git('show',START+':docs/benchmarks/external-effects-catalog/'+name))[key]
        current=evidence(name)[key];oldmods={r['mod_key'] for r in old}
        assert [r for r in current if r['mod_key'] in oldmods]==old,name
        owned=[r for r in current if r['mod_key']=='twilightforest']
        if key=='effects':assert owned==review['effects']
        elif key=='paths':assert owned==review['paths']
        elif key=='sources':assert {r['path_id'] for r in owned}==set(paths)
        else:assert {r['effect_id'] for r in owned}==set(effects)
        idkey='effect_id' if key=='comparisons' else 'id'
        assert len(current)==len({r[idkey] for r in current}),name
        preserved[key]=len(old)
    assert preserved==dict(effects=116,sources=161,paths=161,comparisons=116,primitives=217)
    # Historical witnesses, drafts, sections, reports, old four reviews and all
    # production files stay untouched. Only current views/docs and exact tooling
    # migration are mutable at promotion and subsequent checkpoints.
    prefix='docs/benchmarks/external-effects-catalog/'
    mutable={prefix+n for n in ['effect-catalog.json','effect-sources.json','delivery-path-matrix.json','vanilla-comparison.json','behavior-primitives.json','mod-completion-ledger.json','mod-reviews/twilightforest.json','research-decision.json','twilightforest-owner-table.md']}
    mutable|={'docs/external-effects-catalog-research.md','scripts/external-effects/validate.py'}|{'scripts/external-effects/'+n for n in NAMES}
    for line in git('diff','--name-status',START).splitlines():
        status,path=line.split('\t',1)
        assert status=='A' or (status=='M' and path in mutable),'Protected checkpoint changed: '+line
    ledger=next(r for r in evidence('mod-completion-ledger.json')['targets'] if r['mod_key']=='twilightforest')
    assert ledger['state']=='COMPLETE' and ledger['semantic_effect_count']==219 and not ledger['remaining_native_ambiguities']
    assert all(not review[k] for k in boundary_flags()) and review['runtime_tests']==0
    return dict(schema='tno.external_effects.twilight_final_integrity.v1',baseline=BASELINE,status='PASS',checkpoint=review['checkpoint'],decision=review['decision'],counts=counts,classifications=review['classification_counts'],custom_damage_types_used=40,registered_custom_statuses=1,review_required=0,future_fixture_contracts=640,accepted_prior_counts=preserved,tooling_migration_files=5,total_mapping_complete=True,runtime_tests=0,**boundary_flags())


if __name__=='__main__':
    r=validate_final();write_json(OUT/'twilightforest-final-integrity.json',r);print(json.dumps(r,indent=2))
