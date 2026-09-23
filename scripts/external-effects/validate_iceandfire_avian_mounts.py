from catalog_common import *
from native_evidence import collect
from collect_iceandfire_avian_mounts import census
from assemble_iceandfire_avian_mounts import CP,STEM,FACTS
from iceandfire_combat_common import preserve_section
def validate_avian_mounts():
    e=read_json(OUT/'native-evidence/iceandfire-avian-mounts.json');assert collect(read_json(OUT/'native-specifications/iceandfire-avian-mounts.json'))==e
    c=read_json(OUT/'iceandfire-avian-mounts-census.json');assert census()==c
    def body(cls,name):return next(m['instructions'] for w in e['witnesses'] if w['entry'].endswith(cls+'.class') for m in w['methods'] if m['name']==name)
    def hits(b,n):return [i for i in b if n in str(i.get('operand',''))]
    amphi=body('AmphithereEntity','tick');assert len(hits(amphi,'.hurt('))==4 and len(hits(amphi,'.knockback('))==1
    assert all('AmphithereEntity.setDeltaMovement' in str(i['operand']) for i in hits(amphi,'.setDeltaMovement('))
    fallen=body('AmphithereEntity','hurt');assert hits(fallen,'IS_PROJECTILE') and hits(fallen,'.isFallenZ')[0]['offset']<hits(fallen,'.hurt(')[0]['offset']
    for cls in ['AmphithereArrowItem','StymphalianArrowItem']:
        w=next(w for w in e['witnesses'] if w['entry'].endswith(cls+'.class'));assert not any(m['name']=='asProjectile' for m in w['methods'])
    assert hits(body('HippocampusEntity','aiStep'),'MobEffects.WATER_BREATHING')
    for cls in ['HippogryphEntity','AmphithereEntity','StymphalianBirdEntity']:assert not hits(body(cls,'doHurtTarget'),'.hurt(')
    d=read_json(OUT/(STEM+'.json'));assert d['facts']==FACTS and len(d['delivery_paths'])==23 and len(d['mechanic_packages'])==6
    assert all(v in (OUT/(STEM+'-review.md')).read_text(encoding='utf-8') for v in FACTS.values())
    preserved=preserve_section(d)
    return dict(checkpoint=CP,status='PASS',native_witnesses=len(e['witnesses']),caller_methods=len(c['rows']),packages=6,paths=23,fixtures=len(d['unexecuted_future_fixtures']),accepted_counts_preserved=preserved,motion_actor_and_damage_gate_checks='PASS',runtime_tests=0,whole_iceandfire_complete=False,**boundary_flags())
if __name__=='__main__':
    d=validate_avian_mounts();write_json(OUT/'iceandfire-r2g8c-integrity.json',d);print(json.dumps(d,indent=2))
