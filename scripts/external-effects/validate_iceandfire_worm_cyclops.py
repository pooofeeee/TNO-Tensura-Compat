from catalog_common import *
from native_evidence import collect
from selected_reference import collect as reference_collect
from vanilla_reference import prepare
from collect_iceandfire_worm_cyclops import census
from assemble_iceandfire_worm_cyclops import CP,STEM,FACTS
from iceandfire_combat_common import preserve_section
def validate_worm_cyclops():
    e=read_json(OUT/'native-evidence/iceandfire-worm-cyclops.json');assert collect(read_json(OUT/'native-specifications/iceandfire-worm-cyclops.json'))==e
    r=read_json(OUT/'reference-evidence/iceandfire-worm-cyclops-244.json');assert reference_collect(read_json(OUT/'reference-specifications/iceandfire-worm-cyclops-244.json'))==r
    assert prepare(read_json(OUT/'vanilla-specifications/iceandfire-worm-cyclops.json'))==read_json(OUT/'vanilla-evidence/iceandfire-worm-cyclops.json')
    c=read_json(OUT/'iceandfire-worm-cyclops-census.json');assert census()==c
    def body(cls,name):return next(m['instructions'] for w in e['witnesses'] if w['entry'].endswith(cls+'.class') for m in w['methods'] if m['name']==name)
    def hits(b,n):return [i for i in b if n in str(i.get('operand',''))]
    ai=body('DeathWormEntity','aiStep');assert hits(ai,'.explode(') and hits(ai,'.throwerL')
    assert not any(i['opcode']=='0xb5' and 'willExplodeZ' in str(i['operand']) for i in ai)
    rider=body('DeathWormEntity','tick');assert hits(rider,'.explode(') and not hits(rider,'ON_GRIEF_BREAK_BLOCK')
    normal=body('DeathWormEntity','doHurtTarget');assert hits(normal,'ON_GRIEF_BREAK_BLOCK') and not hits(normal,'.hurt(')
    eye=body('CyclopsEyeEntity','hurt');assert hits(eye,'DamageTypes.ARROW') and hits(eye,'.onHitEye(') and not hits(eye,'IS_PROJECTILE')
    hit=body('CyclopsEntity','onHitEye');assert hits(hit,'.setBlinded(')[0]['offset']<hits(hit,'.hurt(')[0]['offset']
    hurt=hits(hit,'.hurt(')[0];assert hit[hit.index(hurt)+1]['opcode']=='0x57'
    assert hits(body('DeathWormEntity','updateAttributes'),'.setHealth(')
    d=read_json(OUT/(STEM+'.json'));assert d['facts']==FACTS and len(d['delivery_paths'])==15 and len(d['mechanic_packages'])==8
    assert all(v in (OUT/(STEM+'-review.md')).read_text(encoding='utf-8') for v in FACTS.values())
    preserved=preserve_section(d)
    return dict(checkpoint=CP,status='PASS',native_witnesses=len(e['witnesses']),reference_witnesses=len(r['witnesses']),caller_methods=len(c['rows']),packages=8,paths=15,fixtures=len(d['unexecuted_future_fixtures']),accepted_counts_preserved=preserved,source_return_and_flag_checks='PASS',runtime_tests=0,whole_iceandfire_complete=False,**boundary_flags())
if __name__=='__main__':
    d=validate_worm_cyclops();write_json(OUT/'iceandfire-r2g7-integrity.json',d);print(json.dumps(d,indent=2))
