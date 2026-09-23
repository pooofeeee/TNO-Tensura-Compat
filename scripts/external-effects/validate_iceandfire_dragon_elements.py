"""R2g5a native-entry, independent-payload and optional-explosion checks."""
from catalog_common import *
from native_evidence import collect
from selected_reference import collect as reference_collect
from collect_iceandfire_dragon_elements import census
from assemble_iceandfire_dragon_elements import CP,STEM,FACTS
from iceandfire_combat_common import preserve_section

def validate_dragon_elements():
    e=read_json(OUT/'native-evidence/iceandfire-dragon-elements.json');assert collect(read_json(OUT/'native-specifications/iceandfire-dragon-elements.json'))==e
    r=read_json(OUT/'reference-evidence/iceandfire-dragon-elements-244.json');assert reference_collect(read_json(OUT/'reference-specifications/iceandfire-dragon-elements-244.json'))==r
    c=read_json(OUT/'iceandfire-dragon-elements-census.json');assert census()==c
    old=read_json(OUT/'native-evidence/iceandfire-frozen-dragons.json');foundation=read_json(OUT/'native-evidence/iceandfire-foundation.json')
    def body(doc,ending,name):return next(m['instructions'] for w in doc['witnesses'] if w['entry'].endswith(ending+'.class') for m in w.get('methods',[]) if m['name']==name)
    def hits(b,n):return [i for i in b if n in str(i.get('operand',''))]
    for cls in ['FireDragonEntity','LightningDragonEntity']:
        for method in ['riderShootFire','shootFireAtMob']:
            b=body(e,'entity/'+cls,method);assert any(i.get('operand')==20 for i in b) and hits(b,'.addFreshEntity(') and hits(b,'.isActuallyBreathingFire(')
    lightning=body(e,'entity/LightningDragonEntity','performNormalBreathAttack');assert hits(lightning,'.destroyAreaBreath(') and not hits(lightning,'.stop(')
    effect=body(e,'IafDragonDestructionManager','applyDragonEffect');assert hits(effect,'.igniteForSeconds(') and hits(effect,'.knockback(') and hits(effect,'.addEffect(')
    for w in old['witnesses']:
        if w['entry'].endswith('/IafDragonDestructionManager.class'):
            payloads=[m for m in w['methods'] if hits(m['instructions'],'.hurt(')]
            assert len(payloads)==2
            for m in payloads:
                b=m['instructions'];h=hits(b,'.hurt(')[0];assert b[b.index(h)+1]['opcode']=='0x57' and h['offset']<hits(b,'.applyDragonEffect(')[0]['offset']
    final=body(e,'BlockLaunchExplosion','finalizeExplosion');assert hits(final,'FallingBlockEntity.<init>(') and not hits(final,'.addFreshEntity(') and not hits(final,'.setHurtsEntities(')
    explosion=body(e,'IafDragonDestructionManager','causeExplosion');assert hits(explosion,'Math.min(') and hits(explosion,'.explode(') and hits(explosion,'.finalizeExplosion(') and not hits(explosion,'Level.explode(')
    inherited=body(r,'level/Explosion','explode');assert hits(inherited,'.onExplosionDetonate(') and hits(inherited,'.getExplosionKnockback(')
    spikes=body(e,'IceSpikesBlock','stepOn');assert hits(spikes,'.cactus(') and hits(spikes,'.hurt(')[0]['offset']<hits(spikes,'.knockback(')[0]['offset'] and not hits(spikes,'.addEffect(')
    fire=body(foundation,'FireDragonChargeEntity','isPickable');assert fire[0]['operand']==1
    firetick=body(foundation,'FireDragonChargeEntity','tick');assert hits(firetick,'.remove(')[0]['offset']<hits(firetick,'DragonChargeEntity.tick(')[0]['offset']
    d=read_json(OUT/(STEM+'.json'));assert d['facts']==FACTS and len(d['delivery_paths'])==19 and len(d['mechanic_packages'])==6
    preserved=preserve_section(d)
    return dict(schema='tno.external_effects.iaf_dragon_elements_integrity.v1',checkpoint=CP,status='PASS',native_witnesses=len(e['witnesses']),reference_witnesses=len(r['witnesses']),caller_methods=len(c['rows']),reviewed_packages=6,delivery_paths=19,future_fixtures=len(d['unexecuted_future_fixtures']),accepted_counts_preserved=preserved,prior_evidence_unchanged=True,source_and_independent_payload_checks='PASS',whole_iceandfire_complete=False,runtime_tests=0,**boundary_flags())

if __name__=='__main__':
    d=validate_dragon_elements();write_json(OUT/'iceandfire-r2g5a-integrity.json',d);print(json.dumps(d,indent=2))
