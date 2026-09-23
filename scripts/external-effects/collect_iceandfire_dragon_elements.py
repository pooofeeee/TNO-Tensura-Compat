"""Fire/lightning delivery deltas and elemental secondary combat paths."""
from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from selected_reference import collect as reference_collect
from collect_iceandfire_foundation import IAF,targets

METHODS={
 'entity/FireDragonEntity':['aiStep','breathFireAtPos','riderShootFire','shootFireAtMob','createCharge'],
 'entity/LightningDragonEntity':['aiStep','breathFireAtPos','riderShootFire','shootFireAtMob','performNormalBreathAttack','createCharge'],
 'entity/util/dragon/IafDragonDestructionManager':['causeExplosion','attackBlock','applyDragonEffect'],
 'entity/util/BlockLaunchExplosion':['*'],
 'item/block/IceSpikesBlock':['stepOn','canSurvive','isValidGround','updateShape'],
}

def census():
    t=targets()['iceandfire'];rows=[];classes=0
    with zipfile.ZipFile(t['path']) as z:
        for entry in sorted(n for n in z.namelist() if n.endswith('.class')):
            c=ClassFile(z.read(entry));classes+=1
            for m in c.methods:
                hits=[i for i in c.instructions(m.get('code',b'')) if any(x in str(i.get('operand','')) for x in ['BlockLaunchExplosion.<init>','IafDragonDestructionManager.destroyAreaBreath(','IafDragonDestructionManager.destroyAreaCharge(','DRAGON_ICE_SPIKES','ON_DRAGON_FIRE_BLOCK','ON_DRAGON_DAMAGE_BLOCK'])]
                if hits:rows.append(dict(entry=entry,method=m['name'],descriptor=m['descriptor'],hits=hits))
    return dict(schema='tno.external_effects.iaf_dragon_elements_census.v1',jar_sha256=t['sha256'],parsed_classes=classes,rows=rows,scope='Dragon elemental routes only; shared explosion construction in other families does not mark those reviewed.')

def save():
    rows=[]
    with zipfile.ZipFile(targets()['iceandfire']['path']) as z:
        for short,wanted in METHODS.items():
            c=ClassFile(z.read(IAF+short+'.class'));methods=sorted({m['name'] for m in c.methods}) if wanted==['*'] else wanted
            rows.append(dict(id='iaf:dragon-elements:'+short,mod_key='iceandfire',entry=IAF+short+'.class',methods=methods))
    s=dict(schema='tno.external_effects.native_specification.v1',baseline=BASELINE,scope='R2g5a: new Fire/Lightning entry methods, explosion and ice-spike combat. Frozen/common source/collision witnesses reused unchanged.',evidence_specifications=rows)
    write_json(OUT/'native-specifications/iceandfire-dragon-elements.json',s);write_json(OUT/'native-evidence/iceandfire-dragon-elements.json',collect(s));write_json(OUT/'iceandfire-dragon-elements-census.json',census())
    a=dict(read_json(OUT/'reference-specifications/vv-loader-244.json')['archives'][0]);a.pop('semantic_review',None)
    a['classes']={'net/minecraft/world/level/Explosion.class':['<init>','explode','makeDamageCalculator','getSeenPercent'], 'net/minecraft/world/level/ExplosionDamageCalculator.class':['getEntityDamageAmount','shouldDamageEntity','getKnockbackMultiplier'], 'net/minecraft/world/entity/Entity.class':['igniteForSeconds','igniteForTicks','baseTick'], 'net/minecraft/world/entity/LivingEntity.class':['knockback'], 'net/minecraft/world/level/block/BaseFireBlock.class':['entityInside']}
    ref=dict(id='iceandfire-dragon-elements-244',scope='Exact damage/knockback/ignition/fire-contact routes, not generic explosion utility review.',archives=[a])
    write_json(OUT/'reference-specifications/iceandfire-dragon-elements-244.json',ref);write_json(OUT/'reference-evidence/iceandfire-dragon-elements-244.json',reference_collect(ref,source_aids=True))
    print('Dragon elemental witnesses saved')

if __name__=='__main__':save()
