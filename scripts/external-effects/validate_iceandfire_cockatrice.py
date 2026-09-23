from catalog_common import *
from native_evidence import collect
from vanilla_reference import prepare
from collect_iceandfire_cockatrice import census
from assemble_iceandfire_cockatrice import CP,STEM,FACTS
from iceandfire_combat_common import preserve_section

def validate_cockatrice():
    e=read_json(OUT/'native-evidence/iceandfire-cockatrice.json');assert collect(read_json(OUT/'native-specifications/iceandfire-cockatrice.json'))==e
    assert prepare(read_json(OUT/'vanilla-specifications/iceandfire-cockatrice.json'))==read_json(OUT/'vanilla-evidence/iceandfire-cockatrice.json')
    r=read_json(OUT/'reference-routing/iceandfire-cockatrice.json');assert sha256(r['archive'])==r['sha256']
    with zipfile.ZipFile(r['archive']) as z:assert all(p not in z.namelist() for p in r['absent_entries'])
    c=read_json(OUT/'iceandfire-cockatrice-census.json');assert census()==c
    def body(cls,name):return next(m['instructions'] for w in e['witnesses'] if w['entry'].endswith(cls+'.class') for m in w['methods'] if m['name']==name)
    def hits(b,n):return [i for i in b if n in str(i.get('operand',''))]
    gaze=body('CockatriceEntity','aiStep');assert len(hits(gaze,'.hurt('))==3 and len(hits(gaze,'.addEffect('))==3
    assert hits(gaze,'.isBlindfolded(') and hits(gaze,'.setTamingLevel(')
    melee=body('CockatriceEntity','doHurtTarget');assert not hits(melee,'.hurt(') and melee[-2]['operand']==0
    scepter=body('CockatriceScepterItem','attackTargets');assert len(hits(scepter,'.hurt('))==1 and hits(scepter,'.wither(') and not hits(scepter,'.isBlindfolded(')
    h=hits(scepter,'.hurt(')[0];assert scepter[scepter.index(h)+1]['opcode']=='0x57'
    assert not hits(body('CockatriceScepterItem','releaseUsing'),'.markDirty(')
    checks=[r for r in c['rows'] if any('.checkScepterTarget(' in str(i['operand']) for i in r['hits'])];assert len(checks)==1 and checks[0]['entry'].endswith('event/ClientEvents.class')
    d=read_json(OUT/(STEM+'.json'));assert d['facts']==FACTS and len(d['delivery_paths'])==12 and len(d['mechanic_packages'])==7
    assert all(v in (OUT/(STEM+'-review.md')).read_text(encoding='utf-8') for v in FACTS.values())
    preserved=preserve_section(d)
    return dict(checkpoint=CP,status='PASS',native_witnesses=len(e['witnesses']),caller_methods=len(c['rows']),packages=7,paths=12,fixtures=len(d['unexecuted_future_fixtures']),accepted_counts_preserved=preserved,source_and_return_checks='PASS',runtime_tests=0,whole_iceandfire_complete=False,**boundary_flags())

if __name__=='__main__':
    d=validate_cockatrice();write_json(OUT/'iceandfire-r2g6-integrity.json',d);print(json.dumps(d,indent=2))
