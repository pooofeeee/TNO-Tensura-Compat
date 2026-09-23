"""Pin the remaining native Frozen dragon entry paths, not a full dragon review."""
from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from selected_reference import collect as reference_collect
from vanilla_reference import prepare
from collect_iceandfire_foundation import IAF,targets

BATCH='iceandfire-frozen-dragons'
SELECTED={
'entity/DragonBaseEntity':['tick','updateRider','updateBurnTarget','breathAttack','performNormalBreathAttack','performChargeAttack','tryScorchTarget','rayTraceRider','canPositionBeSeen','isActuallyBreathingFire','isBreathingFire','setBreathingFire','getDragonStage','isBaby','useFlyingPathFinder','isAlliedTo','isPart','setTarget','isStriking','strike','setStateField','setControlState','getControlState'],
'entity/IceDragonEntity':['aiStep','shootIceAtMob','createCharge','riderShootFire','breathFireAtPos'],
'entity/DragonChargeEntity':['<init>','tick','onHit','canHitMob','hurt','isPickable'],
'entity/util/dragon/IafDragonFlightManager':['update','onSetAttackTarget'],
'entity/util/dragon/IafDragonLogic':['updateDragonServer','updateDragonCommon'],
'entity/util/dragon/DragonUtils':['canGrief','onSameTeam'],
'event/IafEvents':['*'],
'event/ClientEvents':['onLivingUpdate'],
'event/ServerEvents':['isRidingOrBeingRiddenBy'],
'network/ServerNetworkHelper':['registerReceivers'],
'item/block/DragonForgeInputBlock':['getTicker'],
'item/block/entity/DragonForgeInputBlockEntity':['tick','lureDragons','isAssembled','canSeeInput','getDragonType','getConnectedTileEntity'],
}

def save():
    t=targets()['iceandfire'];rows=[]
    with zipfile.ZipFile(t['path']) as z:
        for short,wanted in SELECTED.items():
            c=ClassFile(z.read(IAF+short+'.class'))
            if wanted==['*']:wanted=sorted({m['name'] for m in c.methods})
            else:wanted=list(wanted)
            if short=='network/ServerNetworkHelper':
                wanted += [m['name'] for m in c.methods if 'Lcom/iafenvoy/iceandfire/network/payload/DragonControlC2SPayload;' in m['descriptor']]
            rows.append(dict(id=BATCH+':'+short,mod_key='iceandfire',entry=IAF+short+'.class',methods=sorted(set(wanted))))
    s=dict(schema='tno.external_effects.native_specification.v1',baseline=BASELINE,scope='Frozen-specific dragon entry, collision, ownership, team/grief and forge collateral routes; unrelated dragon powers pending.',evidence_specifications=rows)
    write_json(OUT/'native-specifications'/f'{BATCH}.json',s);write_json(OUT/'native-evidence'/f'{BATCH}.json',collect(s))
    a=dict(read_json(OUT/'reference-specifications/vv-loader-244.json')['archives'][0]);a.pop('semantic_review',None)
    a['classes']={'net/minecraft/world/entity/TamableAnimal.class':['isOwnedBy','isAlliedTo'],'net/minecraft/world/entity/OwnableEntity.class':['getOwner'],'net/minecraft/world/entity/projectile/Fireball.class':['<init>'],'net/minecraft/world/entity/projectile/AbstractHurtingProjectile.class':['<init>'],'net/minecraft/world/entity/projectile/Projectile.class':['canHitEntity','setOwner','getOwner','tick'],'net/minecraft/world/entity/projectile/ProjectileUtil.class':['getHitResultOnMoveVector','getHitResult'],'net/minecraft/world/entity/LivingEntity.class':['hasLineOfSight']}
    a['classes']['net/minecraft/world/entity/projectile/ProjectileUtil.class'].append('getEntityHitResult')
    a['classes']['net/minecraft/world/level/EntityGetter.class']=['getEntitiesOfClass']
    a['classes']['net/minecraft/world/entity/Entity.class']=['canBeHitByProjectile','isPassengerOfSameVehicle']
    with zipfile.ZipFile(a['path']) as z:missing={k:v for k,v in a['classes'].items() if k not in z.namelist()}
    a['classes']={k:v for k,v in a['classes'].items() if k not in missing}
    raw=dict(classes={k[:-6]:v for k,v in missing.items()},resources=[])
    write_json(OUT/'vanilla-specifications'/f'{BATCH}.json',raw);write_json(OUT/'vanilla-evidence'/f'{BATCH}.json',prepare(raw))
    write_json(OUT/'reference-routing'/f'{BATCH}.json',dict(archive=a['path'],sha256=a['sha256'],absent_entries=list(missing),authority='Exact raw Minecraft1.21.1 for classes absent from installed patched archive.'))
    ref=dict(id=BATCH+'-244',scope='Exact installed charge constructor owner assignment and collision/team/LOS prerequisites; existing frozen lifecycle refs reused.',archives=[a])
    write_json(OUT/'reference-specifications'/f'{BATCH}-244.json',ref);write_json(OUT/'reference-evidence'/f'{BATCH}-244.json',reference_collect(ref,source_aids=True))
    print('Frozen dragon native witnesses:',len(rows))

if __name__=='__main__':save()
