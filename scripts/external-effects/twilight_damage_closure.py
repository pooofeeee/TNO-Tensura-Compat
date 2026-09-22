"""Link all exact installed Twilight DamageTypes to reviewed caller profiles."""
from catalog_common import *

def census():
    resources=read_json(WORK/'twilightforest/resources.json')
    prefix='data/twilightforest/damage_type/'
    declarations={'twilightforest:'+p[len(prefix):-5]:(p,v) for p,v in resources.items() if p.startswith(prefix) and p.endswith('.json')}
    found={}
    for path in sorted((OUT/'semantic-sections').glob('twilightforest-*.json')):
        section=read_json(path)
        for index,profile in enumerate(section.get('damage_profiles',[])):
            rid=profile.get('type',profile.get('damage_type',''))
            if rid not in declarations:continue
            assert rid not in found,(rid,path)
            assert profile['status']=='USED',(rid,profile['status'])
            entry,resource=declarations[rid]
            found[rid]=dict(type=rid,status='USED',declaration_entry=entry,declaration_sha256=resource['sha256'],declaration=resource['data'],semantic_section=path.relative_to(OUT).as_posix(),semantic_section_sha256=sha256(path),profile_index=index,profile_sha256=byte_hash(json.dumps(profile,sort_keys=True,ensure_ascii=False).encode('utf-8')))
    assert len(declarations)==40 and set(found)==set(declarations),(set(declarations)-set(found),set(found)-set(declarations))
    return dict(schema='tno.external_effects.twilight_damage_type_closure.v1',baseline=BASELINE,checkpoint='R2f8y-ominous-progression-complete',status='ALL_CUSTOM_TYPES_REVIEWED_NOT_WHOLE_MOD_COMPLETE',declared=40,used=40,declared_but_no_combat_caller_proven=0,unfinished_types=[],runtime_tests=0,profiles=[found[k] for k in sorted(found)],scope='Exact installed declarations each map to one protected semantic profile with caller/source/amount/tags/native admission. Native vanilla sources in other profiles excluded from this40. Whole-mod source/ASM/compatibility closure and final promotion still pending.',**boundary_flags())

if __name__=='__main__':
    write_json(OUT/'twilightforest-r2f8y-damage-type-closure.json',census())
    print('Twilight DamageType census40/40 USED; no missing or duplicate profiles')
