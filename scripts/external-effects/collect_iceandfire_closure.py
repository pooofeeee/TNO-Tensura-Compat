from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from collect_iceandfire_foundation import IAF,COMPAT,targets,caller_census,tag_census
CLASSES=['entity/CockatriceEggEntity','entity/DeathWormEggEntity','entity/HippogryphEggEntity','item/RottenEggItem','item/DeathwormEggItem','item/HippogryphEggItem','item/armor/BlindfoldItem','entity/DragonEggEntity','entity/DragonSkullEntity','entity/MobSkullEntity','entity/ai/EntityGroundAIRideGoal','entity/ai/StymphalianBirdAIAirTargetGoal','entity/ai/VillagerAIFearUntamedGoal','entity/util/IVillagerFear','entity/util/IAnimalFear','item/SummoningCrystalItem']
NEED=['.hurt(','.heal(','.setHealth(','.addEffect(','.removeEffect(','.igniteForSeconds(','.explode(','.knockback(','.causeFallDamage(','.teleportTo(','.randomTeleport(','.setTarget(']
WATCH={'hurt','isInvulnerableTo','canBeAffected','canBeTurnedToStone','doHurtTarget','thunderHit','causeFallDamage','onHit','onHitEntity','hurtEnemy','finishUsingItem','inventoryTick','releaseUsing','mobInteract'}

def census():
    t=targets()['iceandfire'];rows=[];classes=[];covered={}
    for p in sorted((OUT/'native-evidence').glob('iceandfire*.json')):
        for w in read_json(p)['witnesses']:
            for m in w.get('methods',[]):covered.setdefault((w['entry'],m['name'],m['descriptor']),[]).append(dict(file=p.relative_to(OUT).as_posix(),witness_id=w['id']))
    with zipfile.ZipFile(t['path']) as z:
        for entry in sorted(n for n in z.namelist() if n.endswith('.class')):
            data=z.read(entry);c=ClassFile(data);classes.append(dict(entry=entry,sha256=byte_hash(data),superclass=c.super))
            for m in c.methods:
                body=list(c.instructions(m.get('code',b'')));hits=[i for i in body if any(s in str(i.get('operand','')) for s in NEED)]
                if hits or m['name'] in WATCH:
                    rows.append(dict(entry=entry,method=m['name'],descriptor=m['descriptor'],code_sha256=byte_hash(m.get('code',b'')),api_hits=hits,watched_override=m['name'] in WATCH,witnesses=covered.get((entry,m['name'],m['descriptor']),[])))
    return dict(schema='tno.external_effects.iaf_combat_closure_census.v1',jar_sha256=t['sha256'],classes=classes,methods=rows,coverage_scope='All726 classes: HP/heal/status/ignite/explosion/knockback/fall/teleport/target calls plus combat delivery/admission overrides. Witness availability is not itself semantic completion; reviewed family contracts and closure dispositions supply interpretation.')

def save():
    rows=[]
    with zipfile.ZipFile(targets()['iceandfire']['path']) as z:
        for s in CLASSES:rows.append(dict(id='iaf:closure:'+s,mod_key='iceandfire',entry=IAF+s+'.class',methods=sorted({m['name'] for m in ClassFile(z.read(IAF+s+'.class')).methods})))
        for s,methods in {'entity/DragonBaseEntity':['aiStep','updateCheckPlayer'],'world/structure/DragonCaveStructure$DragonCavePiece':['createDragon'],'world/structure/DragonRoostStructure$DragonRoostPiece':['spawnDragon']}.items():rows.append(dict(id='iaf:closure:'+s,mod_key='iceandfire',entry=IAF+s+'.class',methods=methods))
    with zipfile.ZipFile(targets()[COMPAT]['path']) as z:
        for n in sorted(z.namelist()):
            if n.startswith('data/') and '/tags/entity_type/' in n and n.endswith('.json'):rows.append(dict(id='iaf:closure:compat-tag:'+n,mod_key=COMPAT,entry=n))
    s=dict(schema='tno.external_effects.native_specification.v1',baseline=BASELINE,scope='Final combat census gaps and short exclusions, not renewed accepted research.',evidence_specifications=rows)
    write_json(OUT/'native-specifications/iceandfire-closure.json',s);write_json(OUT/'native-evidence/iceandfire-closure.json',collect(s))
    assert caller_census()==read_json(OUT/'iceandfire-source-census.json')
    assert tag_census()==read_json(OUT/'iceandfire-damage-tag-census.json')
    write_json(OUT/'iceandfire-combat-closure-census.json',census());print('Combat/source closure witnesses saved')
if __name__=='__main__':save()
