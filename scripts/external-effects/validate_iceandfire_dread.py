from catalog_common import *
from native_evidence import collect
from selected_reference import collect as reference_collect
from collect_iceandfire_dread import census
from assemble_iceandfire_dread import CP,STEM,FACTS
from iceandfire_combat_common import preserve_section

def validate_dread():
    e=read_json(OUT/'native-evidence/iceandfire-dread.json');assert collect(read_json(OUT/'native-specifications/iceandfire-dread.json'))==e
    r=read_json(OUT/'reference-evidence/iceandfire-dread-244.json');assert reference_collect(read_json(OUT/'reference-specifications/iceandfire-dread-244.json'))==r
    c=read_json(OUT/'iceandfire-dread-census.json');assert census()==c
    def methods(cls):return [m for w in e['witnesses'] if w['entry'].endswith('/'+cls+'.class') for m in w['methods']]
    def body(cls,name):return next(m['instructions'] for m in methods(cls) if m['name']==name)
    def hits(b,n):return [i for i in b if n in str(i.get('operand',''))]
    for a in c['archives']:
        assert not any('.onKillEntity(' in str(i['operand']) for row in a['legacy_and_queen_references'] for i in row['hits'])
    assert not any(m['name']=='killedEntity' for w in e['witnesses'] if '/entity/Dread' in w['entry'] for m in w.get('methods',[]))
    for cls in ['DreadBeastEntity','DreadScuttlerEntity']:
        assert [i['opcode'] for i in body(cls,'getCommander')]==['0x1','0xb0']
        b=body(cls,'aiStep');assert hits(b,'.hurt(')[0]['offset']<hits(b,'.knockback(')[0]['offset']
    constructors=[m for m in methods('DreadLichSkullEntity') if m['name']=='<init>'];assert all(not hits(m['instructions'],'.setPos(') for m in constructors)
    assert not hits(body('DreadLichEntity','performRangedAttack'),'.setPos(')
    assert hits(body('LichStaffItem','use'),'.setPos(')
    assert not hits(body('DreadLichAIStrifeGoal','tick'),'.attackCooldownI')
    assert hits(body('DreadLichSkullEntity','onHitEntity'),'.isAlliedTo(')
    assert hits(body('DreadLichSkullEntity','doPostHurtEffects'),'.damageShield(')
    assert not any('DreadQueen' in str(i.get('operand','')) for m in methods('IafEntities') for i in m['instructions'])
    death=next(m['instructions'] for w in r['witnesses'] if w['entry'].endswith('/LivingEntity.class') for m in w['methods'] if m['name']=='die');assert hits(death,'.killedEntity(') and not hits(death,'.onKillEntity(')
    d=read_json(OUT/(STEM+'.json'));assert d['facts']==FACTS and len(d['delivery_paths'])==17 and len(d['mechanic_packages'])==6
    assert all(v in (OUT/(STEM+'-review.md')).read_text(encoding='utf-8') for v in FACTS.values())
    preserved=preserve_section(d)
    return dict(checkpoint=CP,status='PASS',native_witnesses=len(e['witnesses']),reference_witnesses=len(r['witnesses']),caller_methods=sum(len(a['combat_callers']) for a in c['archives']),packages=6,paths=17,fixtures=len(d['unexecuted_future_fixtures']),accepted_counts_preserved=preserved,legacy_callback_and_constructor_admission_checks='PASS',runtime_tests=0,whole_iceandfire_complete=False,**boundary_flags())
if __name__=='__main__':
    d=validate_dread();write_json(OUT/'iceandfire-r2g8d-integrity.json',d);print(json.dumps(d,indent=2))
