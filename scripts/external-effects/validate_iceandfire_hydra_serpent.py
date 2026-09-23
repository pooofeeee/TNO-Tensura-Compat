from catalog_common import *
from native_evidence import collect
from selected_reference import collect as reference_collect
from vanilla_reference import prepare
from collect_iceandfire_hydra_serpent import census
from assemble_iceandfire_hydra_serpent import CP,STEM,FACTS
from iceandfire_combat_common import preserve_section
def validate_hydra_serpent():
    e=read_json(OUT/'native-evidence/iceandfire-hydra-serpent.json');assert collect(read_json(OUT/'native-specifications/iceandfire-hydra-serpent.json'))==e
    r=read_json(OUT/'reference-evidence/iceandfire-hydra-serpent-244.json');assert reference_collect(read_json(OUT/'reference-specifications/iceandfire-hydra-serpent-244.json'))==r
    assert prepare(read_json(OUT/'vanilla-specifications/iceandfire-hydra-serpent.json'))==read_json(OUT/'vanilla-evidence/iceandfire-hydra-serpent.json')
    c=read_json(OUT/'iceandfire-hydra-serpent-census.json');assert census()==c
    def body(doc,cls,name):return next(m['instructions'] for w in doc['witnesses'] if w['entry'].endswith(cls+'.class') for m in w['methods'] if m['name']==name)
    def hits(b,n):return [i for i in b if n in str(i.get('operand',''))]
    hurt=body(e,'HydraEntity','hurt');assert hits(hurt,'.headDamageTracker')[0]['offset']<hits(hurt,'.hurt(')[0]['offset'] and hits(hurt,'BYPASSES_INVULNERABILITY')
    breath=body(e,'HydraBreathEntity','onHit');assert hits(breath,'.mobAttack(') and hits(breath,'.hurt(')[0]['offset']<hits(breath,'.addEffect(')[0]['offset']
    for cls in ['HydraBreathEntity','SeaSerpentBubblesEntity']:
        b=body(e,cls,'tick');assert hits(b,'.baseTick(') and hits(b,'.onHit(') and not hits(b,'.onProjectileImpact(')
    bubble=body(e,'SeaSerpentBubblesEntity','tick');alive=hits(bubble,'.isAlive(')[0];assert bubble[bubble.index(alive)+1]['opcode']=='0x9a'
    arrow=body(e,'HydraArrowEntity','doPostHurtEffects');assert hits(arrow,'.damageShield(')[0]['offset']<hits(arrow,'.addEffect(')[0]['offset']<hits(arrow,'.heal(')[0]['offset']
    factory=body(r,'item/ArrowItem','asProjectile');assert hits(factory,'projectile/Arrow.<init>') and not hits(factory,'.createArrow(')
    for cls in ['HydraArrowItem','SeaSerpentArrowItem']:
        w=next(w for w in e['witnesses'] if w['entry'].endswith(cls+'.class'));assert not any(m['name']=='asProjectile' for m in w['methods'])
    d=read_json(OUT/(STEM+'.json'));assert d['facts']==FACTS and len(d['delivery_paths'])==19 and len(d['mechanic_packages'])==9
    assert all(v in (OUT/(STEM+'-review.md')).read_text(encoding='utf-8') for v in FACTS.values())
    preserved=preserve_section(d)
    return dict(checkpoint=CP,status='PASS',native_witnesses=len(e['witnesses']),reference_witnesses=len(r['witnesses']),caller_methods=len(c['rows']),packages=9,paths=19,fixtures=len(d['unexecuted_future_fixtures']),accepted_counts_preserved=preserved,resource_order_bubble_branch_and_factory_checks='PASS',runtime_tests=0,whole_iceandfire_complete=False,**boundary_flags())
if __name__=='__main__':
    d=validate_hydra_serpent();write_json(OUT/'iceandfire-r2g8b-integrity.json',d);print(json.dumps(d,indent=2))
