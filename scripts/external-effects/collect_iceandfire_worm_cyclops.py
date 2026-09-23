from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from selected_reference import collect as reference_collect
from vanilla_reference import prepare
from collect_iceandfire_foundation import IAF,targets
CLASSES=['entity/DeathWormEntity','entity/ai/DeathWormAIAttackGoal','entity/ai/DeathWormAITargetGoal','entity/ai/DeathwormAITargetItemsGoal','entity/SlowPartEntity','entity/CyclopsEntity','entity/CyclopsEyeEntity','entity/ai/CyclopsAIAttackMeleeGoal','entity/ai/CyclopsAITargetSheepPlayersGoal','item/CyclopsEyeItem']

def census():
    t=targets()['iceandfire'];rows=[]
    with zipfile.ZipFile(t['path']) as z:
        for entry in sorted(n for n in z.namelist() if n.endswith('.class')):
            c=ClassFile(z.read(entry))
            for m in c.methods:
                hits=[i for i in c.instructions(m.get('code',b'')) if '.setExplosive(' in str(i.get('operand','')) or (any(s in entry.lower() for s in ['deathworm','cyclops']) and any(s in str(i.get('operand','')) for s in ['.hurt(','.heal(','.setHealth(','.addEffect(','.explode(','.startRiding(','willExplodeZ','ticksTillExplosionI']))]
                if hits:rows.append(dict(entry=entry,method=m['name'],descriptor=m['descriptor'],hits=hits))
    return dict(jar_sha256=t['sha256'],rows=rows,scope='Whole-JAR TNT setter and Death Worm/Cyclops combat/resource caller census.')

def save():
    with zipfile.ZipFile(targets()['iceandfire']['path']) as z:rows=[dict(id='iaf:worm-cyclops:'+s,mod_key='iceandfire',entry=IAF+s+'.class',methods=sorted({m['name'] for m in ClassFile(z.read(IAF+s+'.class')).methods})) for s in CLASSES]
    s=dict(schema='tno.external_effects.native_specification.v1',baseline=BASELINE,scope='Death Worm and Cyclops combat only.',evidence_specifications=rows)
    write_json(OUT/'native-specifications/iceandfire-worm-cyclops.json',s);write_json(OUT/'native-evidence/iceandfire-worm-cyclops.json',collect(s));write_json(OUT/'iceandfire-worm-cyclops-census.json',census())
    a=dict(read_json(OUT/'reference-specifications/vv-loader-244.json')['archives'][0]);a.pop('semantic_review',None);a['classes']={'net/minecraft/world/level/Level.class':['explode'],'net/minecraft/server/level/ServerLevel.class':['explode'],'net/minecraft/world/level/Explosion.class':['getDefaultDamageSource','getIndirectSourceEntityInternal']}
    r=dict(id='iceandfire-worm-cyclops-244',scope='Level versus manually constructed explosion start/detonate admission; inherited explosion algorithm already protected.',archives=[a])
    write_json(OUT/'reference-specifications/iceandfire-worm-cyclops-244.json',r);write_json(OUT/'reference-evidence/iceandfire-worm-cyclops-244.json',reference_collect(r,source_aids=True))
    raw=dict(classes={'net/minecraft/world/damagesource/DamageSources':['explosion']},resources=[])
    write_json(OUT/'vanilla-specifications/iceandfire-worm-cyclops.json',raw);write_json(OUT/'vanilla-evidence/iceandfire-worm-cyclops.json',prepare(raw))
    print('Death Worm/Cyclops witnesses saved')
if __name__=='__main__':save()
