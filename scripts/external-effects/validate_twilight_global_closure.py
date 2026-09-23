"""Global source closure plus frozen semantic-section and custom-type integrity."""
from catalog_common import *
from collect_twilight_global_closure import api_census,compat_census,EXCLUDED
from twilight_damage_closure import census as damage_census


def validate_global_closure():
    target=next(t for t in read_json(OUT/'jar-inventory.json')['targets'] if t['key']=='twilightforest')
    assert sha256(target['path'])==target['sha256']
    api=read_json(OUT/'twilightforest-global-source-census.json');assert api==api_census(target)
    assert api['class_count']==1943 and api['method_hit_count']==279
    excluded=[r for r in api['records'] if r['disposition']=='EXCLUDED_NONCOMBAT'];assert len(excluded)==sum(len(v) for v in EXCLUDED.values())==19
    closure=read_json(OUT/'twilightforest-global-source-closure.json')
    assert closure['decision']=='TWILIGHT_REMAINING_CONTENT_COMPLETE' and all(closure[k] for k in ['semantic_discovery_complete','special_damage_discovery_complete','source_mapping_complete','delivery_mapping_complete','combat_asm_coverage_complete','compatibility_attribution_complete'])
    assert not closure['remaining_native_ambiguities'] and not closure['review_required'] and not closure['unfinished_combat_significant_work'] and not closure['final_promotion_complete']
    actual={p.relative_to(OUT).as_posix() for p in (OUT/'semantic-sections').glob('twilightforest-*.json')}
    assert {r['file'] for r in closure['sections']}==actual
    for r in closure['sections']:assert sha256(OUT/r['file'])==r['sha256']
    for k in ['source_census','damage_type_closure','compatibility']:
        r=closure[k];assert sha256(OUT/r['file'])==r['sha256']
    assert read_json(OUT/'compat-findings/twilightforest-global.json')==compat_census()
    assert damage_census()==read_json(OUT/'twilightforest-r2f8y-damage-type-closure.json')
    d=read_json(OUT/'partial-drafts/twilightforest-r2f8af-partial.json');assert len(d['effects'])==277 and len(d['paths'])==1014
    assert all(not closure[k] for k in boundary_flags())
    return dict(schema='tno.external_effects.twilight_global_integrity.v1',status='PASS',checkpoint='R2f8-remaining-content-complete',reviewed_drafts=277,reviewed_path_cases=1014,parsed_classes=1943,api_caller_methods=279,new_noncombat_dispositions=19,registered_transformers=31,custom_damage_types=40,review_required=0,semantic_sections=len(actual),runtime_tests=0,**boundary_flags())


if __name__=='__main__':
    r=validate_global_closure();write_json(OUT/'twilightforest-global-source-integrity.json',r);print(json.dumps(r,indent=2))
