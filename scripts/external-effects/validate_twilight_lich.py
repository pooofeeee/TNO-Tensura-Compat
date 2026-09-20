"""Lich checkpoint integrity and immutable accepted subsection protection."""
from catalog_common import *
from assemble_twilight_lich import START
from validate_twilight_progress import validate_progress
from lich_source_audit import audit

def validate_lich():
    progress=validate_progress()
    protected=['semantic-sections/twilightforest-frosted.json','partial-drafts/twilightforest-r2f2-partial.json','partial-drafts/twilightforest-r2f1-partial.json','native-evidence/twilightforest-r2f1-partial.json','native-evidence/twilight-frosted.json','native-specifications/twilight-frosted.json','vanilla-specifications/twilight-frosted.json','vanilla-evidence/twilight-frosted.json','reference-specifications/twilight-frosted-244.json','reference-evidence/twilight-frosted-244.json','reference-routing/twilight-frosted.json','compat-findings/twilightforest-frosted.json','config-evidence/twilightforest-common.json']
    for f in protected:
        p='docs/benchmarks/external-effects-catalog/'+f
        old=json.loads(subprocess.check_output(['git','show',START+':'+p],cwd=ROOT).decode('utf-8'))
        assert read_json(ROOT/p)==old,f
    section=read_json(OUT/'semantic-sections/twilightforest-lich.json')
    assert section['subsection_decision']=='LICH_SEMANTIC_REVIEW_COMPLETE'
    assert [r['requirement'] for r in section['requested_semantic_closure']]==list(range(1,22))
    assert len(section['effects'])==9 and len(section['paths'])==24 and len(section['source_paths'])==14
    assert {p['type'] for p in section['damage_profiles']}=={'twilightforest:lich_bolt','twilightforest:lich_bomb','twilightforest:twilight_scepter'}
    assert section['counts']['review_required']==section['counts']['promoted']==0
    for r in section['reused_accepted_producers']:assert sha256(OUT/r['evidence_file'])==r['sha256']
    assert audit()==read_json(OUT/'lich-vanilla-source-audit.json')
    old=read_json(OUT/'partial-drafts/twilightforest-r2f2-partial.json');new=read_json(OUT/'partial-drafts/twilightforest-r2f3-partial.json')
    assert new['effects']==old['effects']+section['effects'] and new['paths']==old['paths']+section['paths']
    witnesses=read_json(OUT/'native-evidence/twilight-lich.json')['witnesses']
    lich=next(w for w in witnesses if w['entry']=='twilightforest/entity/boss/Lich.class')
    hurt=next(m for m in lich['methods'] if m['name']=='hurt')['instructions']
    def pos(fragment):return next(i['offset'] for i in hurt if fragment in str(i.get('operand')))
    order=[pos(s) for s in ['.getTeleportInvisibility(','.IN_WALL','.isShadowClone(','.getEntity(','.getShieldStrength(','.BREAKS_LICH_SHIELDS','.setShieldStrength(','BaseTFBoss.hurt(']]
    assert order==sorted(order)
    # No normal super call before the counter path; native branch really returns false.
    assert any(i['opcode']=='0xac' and 149<i['offset']<297 for i in hurt)
    assert any(i['opcode']=='0x95' and 118<i['offset']<149 for i in hurt), 'strict float comparison witness'
    tag=next(w for w in read_json(OUT/'native-evidence/twilightforest-r2f1-partial.json')['witnesses'] if w['entry']=='data/twilightforest/tags/damage_type/breaks_lich_shields.json')
    assert set(tag['data']['values'])=={'twilightforest:lich_bolt','twilightforest:twilight_scepter','minecraft:magic','minecraft:indirect_magic','minecraft:sonic_boom'}
    ledger=read_json(OUT/'mod-reviews/twilightforest.json')
    if ledger['status']=='PARTIAL':
        assert not ledger['effects'] and not ledger['paths']
        assert ledger['draft_mechanic_count']>=11 and ledger['draft_path_count']>=37
    return dict(schema='tno.external_effects.lich_integrity.v1',status='PASS',starting_sha=START,decision=section['subsection_decision'],requirements_closed=21,reviewed_lich_packages=9,lich_delivery_cases=24,shield_source_cases=14,twilight_reviewed_drafts=11,twilight_delivery_drafts=37,protected_frosted_files=len(protected),hurt_admission_offsets=order,raw_factory_census_reproduced=True,accepted_counts_unchanged=progress['accepted_counts_unchanged'],runtime_tests=0,promoted_twilight_records=0,**boundary_flags())

if __name__=='__main__':
    result=validate_lich();write_json(OUT/'twilightforest-lich-integrity.json',result);print(json.dumps(result,indent=2))
