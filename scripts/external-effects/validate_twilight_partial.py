"""Validate a partial checkpoint without mistaking draft rows for completed review."""
from catalog_common import *
from native_evidence import collect
from checkpoint_twilight_partial import START, NAME, CHECKPOINT


def validate_partial():
    def old(path):
        return json.loads(subprocess.check_output(['git','show',START+':'+path],cwd=ROOT).decode('utf-8'))
    protected = ['variantsandventures','cultofazazel','royalvariations','friendsandfoes']
    for key in protected:
        path=f'docs/benchmarks/external-effects-catalog/mod-reviews/{key}.json'
        assert read_json(ROOT/path)==old(path), key
    counts={}
    for name,key in [('effect-catalog.json','effects'),('effect-sources.json','sources'),('delivery-path-matrix.json','paths'),('vanilla-comparison.json','comparisons'),('behavior-primitives.json','primitives')]:
        path='docs/benchmarks/external-effects-catalog/'+name
        current=read_json(ROOT/path)
        assert current[key]==old(path)[key], name
        counts[key]=len(current[key])
        assert current['checkpoint']==CHECKPOINT and current['unfinished_review']['promoted_records']==0
    spec=read_json(OUT/'native-specifications'/f'{NAME}.json')
    native=read_json(OUT/'native-evidence'/f'{NAME}.json')
    assert collect(spec)==native
    assert len(native['witnesses'])==79
    review=read_json(OUT/'mod-reviews/twilightforest.json')
    assert review['status']=='PARTIAL' and review['effects']==[] and review['paths']==[]
    assert not any(review[k] for k in ['semantic_discovery_complete','special_damage_discovery_complete','source_mapping_complete','delivery_mapping_complete'])
    draft=read_json(OUT/'partial-drafts'/f'{NAME}.json')
    assert len(draft['effects'])==1 and len(draft['paths'])==7 and not draft['promoted_to_catalog']
    assert draft['effects'][0]['primary_classification']=='CUSTOM_STATUS'
    assert set(draft['effects'][0]['delivery_paths'])=={p['id'] for p in draft['paths']}
    assert all(p['effect_ids']==[draft['effects'][0]['id']] for p in draft['paths'])
    notes=read_json(OUT/'partial-notes'/f'{NAME}.json')
    assert len(notes['damage_type_declarations'])==40 and len(notes['damage_tag_contributions'])==23
    assert len({d['registry_id'] for d in notes['damage_type_declarations']})==40
    assert notes['custom_effects_found']==['twilightforest:frosted'] and notes['review_required_count']==0
    registry=next(w for w in native['witnesses'] if w['id']=='tf:init/TFMobEffects')
    assert any(i.get('operand')=='frosted' for m in registry['methods'] for i in m['instructions'])
    ledger={r['mod_key']:r for r in read_json(OUT/'mod-completion-ledger.json')['targets']}
    assert ledger['twilightforest']['state']=='PARTIAL' and ledger['iceandfire']['state']=='UNSTARTED'
    assert all(ledger[k]['state']=='COMPLETE' for k in protected+['tensura'])
    return dict(schema='tno.external_effects.partial_integrity.v1',status='PASS',checkpoint=CHECKPOINT,
                immutable_start=START,protected_reviews=protected,accepted_counts_unchanged=counts,
                native_witnesses=79,draft_mechanics=1,draft_paths=7,promoted_twilight_records=0,
                semantic_coverage_complete=False,iceandfire_started=False,**boundary_flags())


if __name__=='__main__':
    result=validate_partial()
    write_json(OUT/'twilightforest-partial-integrity.json',result)
    print(json.dumps(result,indent=2))
