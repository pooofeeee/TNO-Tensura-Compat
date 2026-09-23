"""Reproduce body-combat evidence and test the significant native branch distinctions."""
from catalog_common import *
from native_evidence import collect
from selected_reference import collect as reference_collect
from vanilla_reference import prepare
from collect_iceandfire_dragon_combat import census
from assemble_iceandfire_dragon_combat import CP,STEM,FACTS
from iceandfire_combat_common import preserve_section

def validate_dragon_combat():
    e=read_json(OUT/'native-evidence/iceandfire-dragon-combat.json');assert collect(read_json(OUT/'native-specifications/iceandfire-dragon-combat.json'))==e
    r=read_json(OUT/'reference-evidence/iceandfire-dragon-combat-244.json');assert reference_collect(read_json(OUT/'reference-specifications/iceandfire-dragon-combat-244.json'))==r
    assert prepare(read_json(OUT/'vanilla-specifications/iceandfire-dragon-combat.json'))==read_json(OUT/'vanilla-evidence/iceandfire-dragon-combat.json')
    routing=read_json(OUT/'reference-routing/iceandfire-dragon-combat.json');assert sha256(routing['archive'])==routing['sha256']
    with zipfile.ZipFile(routing['archive']) as z:assert all(p not in z.namelist() for p in routing['absent_entries'])
    c=read_json(OUT/'iceandfire-dragon-combat-census.json');assert census()==c
    def body(doc,ending,name):return next(m['instructions'] for w in doc['witnesses'] if w['entry'].endswith(ending+'.class') for m in w.get('methods',[]) if m['name']==name)
    def hits(b,n):return [i for i in b if n in str(i.get('operand',''))]
    attack=body(e,'IafDragonLogic','attackTarget');assert len(hits(attack,'.hurt('))==2 and hits(attack,'.mobAttack(') and hits(attack,'.indirectMagic(')
    animations=body(e,'IafDragonLogic','updateDragonAttack');requests=hits(animations,'.attackTarget(');assert len(requests)==3
    for i in requests:assert animations[animations.index(i)+1]['opcode']=='0x57'
    assert len(hits(animations,'.knockback('))==2
    for cls in ['FireDragonEntity','IceDragonEntity','LightningDragonEntity']:
        b=body(e,cls,'doHurtTarget');assert hits(b,'.startRiding(') and not hits(b,'.hurt(') and not hits(b,'.doHurtTarget(')
        assert b[-2]['operand']==0
    prey=body(e,'DragonBaseEntity','updatePreyInMouth');assert hits(prey,'.hurt(')[0]['offset']<hits(prey,'.heal(')[0]['offset']<hits(prey,'.stopRiding(')[0]['offset']
    hurt=hits(prey,'.hurt(')[0];assert prey[prey.index(hurt)+1]['opcode']=='0x36'
    roar=body(e,'DragonBaseEntity','roar');assert len(hits(roar,'.addEffect('))==4 and len(hits(roar,'IafItems.EARPLUGS'))==1 and not hits(roar,'.hasLineOfSight(')
    assert len(hits(roar,'.expandTowards('))==2
    food=body(e,'DragonAITargetItemsGoal','tick');assert hits(food,'.setHealth(') and not hits(food,'.heal(')
    heal=body(r,'entity/LivingEntity','heal');sethealth=body(r,'entity/LivingEntity','setHealth');assert hits(heal,'.onLivingHeal(') and not hits(sethealth,'.onLivingHeal(')
    lightning=body(e,'LightningDragonEntity','isInvulnerableTo');assert hits(lightning,'.getMsgId(') and hits(lightning,'.heal(') and any(i.get('operand')==15.0 for i in lightning)
    part=body(e,'MultipartPartEntity','hurt');assert hits(part,'.damageMultiplierF') and not hits(part,'.isInvulnerableTo(')
    d=read_json(OUT/(STEM+'.json'));assert d['facts']==FACTS and len(d['delivery_paths'])==20 and len(d['mechanic_packages'])==7
    text=(OUT/(STEM+'-review.md')).read_text(encoding='utf-8');assert all(value in text for value in FACTS.values())
    preserved=preserve_section(d)
    return dict(schema='tno.external_effects.iaf_dragon_combat_integrity.v1',checkpoint=CP,status='PASS',native_witnesses=len(e['witnesses']),reference_witnesses=len(r['witnesses']),primitive_caller_methods=len(c['rows']),reviewed_packages=7,delivery_paths=20,future_fixtures=len(d['unexecuted_future_fixtures']),accepted_counts_preserved=preserved,prior_evidence_unchanged=True,source_hurt_heal_and_roar_branch_checks='PASS',whole_iceandfire_complete=False,runtime_tests=0,**boundary_flags())

if __name__=='__main__':
    d=validate_dragon_combat();write_json(OUT/'iceandfire-r2g5b-integrity.json',d);print(json.dumps(d,indent=2))
