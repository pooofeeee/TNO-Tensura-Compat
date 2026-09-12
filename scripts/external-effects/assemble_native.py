"""Materialize partial native findings; never grants R3 classification or coverage."""
from catalog_common import *

def assemble():
    effects=[]
    for path in sorted((OUT/'native-findings').glob('*.json')):
        document=read_json(path)
        assert document['baseline']==BASELINE
        byid={x['id']:x for x in document['evidence_specifications']}
        for finding in document['findings']:
            effect=dict(finding,mod_key=document['mod_key'],inspection_status='PARTIAL',
                closest_vanilla_equivalent=None,vanilla_similarities=None,vanilla_differences=None,
                existing_compat_modification=document['existing_compat_modification'],
                compat_note=document['compat_note'],
                native_findings_file=path.relative_to(ROOT).as_posix(),
                implementation=[dict(entry=byid[e]['entry'],methods=byid[e].get('methods',[])) for e in finding['evidence_ids']],
                confidence='Native bytecode-backed finding; final comparison, delivery deduplication and pack-wide compat relevance unfinished.')
            effects.append(effect)
    return effects

if __name__=='__main__':
    catalog=read_json(OUT/'effect-catalog.json')
    assert catalog['status']=='PARTIAL', 'Do not overwrite a completed catalog with partial assembly'
    catalog.update(checkpoint='R2a_PARTIAL',effects=assemble(),
        note='These are provisional native findings, not a final distinct-effect count. Null comparison/classification means R3 has not been performed. R2 semantic coverage remains incomplete.')
    write_json(OUT/'effect-catalog.json',catalog)
    print(f'{len(catalog["effects"])} provisional native findings assembled')
