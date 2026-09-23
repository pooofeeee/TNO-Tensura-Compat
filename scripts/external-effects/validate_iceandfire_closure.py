from catalog_common import *
from native_evidence import collect
from collect_iceandfire_closure import census
from collect_iceandfire_foundation import caller_census,tag_census
from assemble_iceandfire_closure import CP,STEM,FACTS
from iceandfire_combat_common import preserve_section

def validate_closure():
    e=read_json(OUT/'native-evidence/iceandfire-closure.json');assert collect(read_json(OUT/'native-specifications/iceandfire-closure.json'))==e
    c=read_json(OUT/'iceandfire-combat-closure-census.json');assert census()==c
    assert len(c['classes'])==726 and len(c['methods'])==188 and sum(bool(m['api_hits']) for m in c['methods'])==130 and all(m['witnesses'] for m in c['methods'])
    for m in c['methods']:
        for ref in m['witnesses']:
            w=next(w for w in read_json(OUT/ref['file'])['witnesses'] if w['id']==ref['witness_id'])
            assert any(x['name']==m['method'] and x['descriptor']==m['descriptor'] and x['code_sha256']==m['code_sha256'] for x in w['methods'])
    source=read_json(OUT/'iceandfire-source-census.json');assert caller_census()==source and len(source['factory_callers'])==7
    tags=read_json(OUT/'iceandfire-damage-tag-census.json');assert tag_census()==tags and len(tags['declarations'])==5
    def body(cls,name):return next(m['instructions'] for w in e['witnesses'] if w['entry'].endswith('/'+cls+'.class') for m in w['methods'] if m['name']==name)
    for cls in ['CockatriceEggEntity','DeathWormEggEntity','HippogryphEggEntity']:
        b=body(cls,'onHit');idx=next(i for i,x in enumerate(b) if '.hurt(' in str(x.get('operand','')));assert b[idx-1]['opcode']=='0xb'
    blind=body('BlindfoldItem','inventoryTick');assert any('MobEffects.BLINDNESS' in str(i.get('operand','')) for i in blind)
    d=read_json(OUT/(STEM+'.json'));assert d['facts']==FACTS and len(d['delivery_paths'])==10 and len(d['mechanic_packages'])==3
    assert all(v in (OUT/(STEM+'-review.md')).read_text(encoding='utf-8') for v in FACTS.values())
    preserved=preserve_section(d)
    return dict(checkpoint=CP,status='PASS',native_witnesses=len(e['witnesses']),classes=726,watched_methods=188,targeted_callers=130,custom_damage_types=5,factory_callers=7,packages=3,paths=10,fixtures=7,accepted_counts_preserved=preserved,unwitnessed_census_methods=0,whole_combat_semantics_closed=True,runtime_tests=0,whole_iceandfire_complete=False,**boundary_flags())
if __name__=='__main__':
    d=validate_closure();write_json(OUT/'iceandfire-r2g10a-integrity.json',d);print(json.dumps(d,indent=2))
