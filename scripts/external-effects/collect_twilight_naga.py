"""Selected Naga/part authority, reusing protected Twilight/vanilla witnesses."""
from twilight_evidence import *
from vanilla_reference import MojangNames, CLIENT

def collect():
    classes={p:['*'] for p in ['entity/boss/Naga','entity/boss/Naga$1','entity/boss/Naga$2','entity/boss/Naga$3','entity/boss/NagaSegment','entity/TFPart','entity/ai/goal/SimplifiedAttackGoal','entity/ai/goal/NagaMovementPattern','entity/ai/goal/NagaMovementPattern$MovementState','entity/ai/goal/NagaSmashGoal','entity/ai/control/NagaMoveControl','network/MovePlayerPacket','network/UpdateTFMultipartPacket','network/UpdateTFMultipartPacket$PartDataHolder','util/multiparts/MultipartEntityUtil','asmhooks/MultipartHooks','block/entity/spawner/NagaSpawnerBlockEntity','block/entity/spawner/BossSpawnerBlockEntity']}
    classes['util/entities/EntityUtil']=['canDestroyBlock']
    classes['init/TFEntities']=['make','build','buildNoEgg','makeCastedBuilder','makeBuilder']
    classes['events/RegistrationEvents']=['setupPackets','addEntityAttributes']
    resource_index=read_json(WORK/'twilightforest/resources.json')
    selected=[k for k,v in resource_index.items() if '/tags/entity_type/' in k and ('twilightforest:naga' in str(v) or k.endswith('/bosses.json'))]
    print('native',native('twilight-naga',classes,selected))
    raw={
      'net/minecraft/world/entity/Entity':['push','isInvisible','setInvisible','isInvulnerableTo','isPushable','canBeHitByProjectile','isAttackable','isAlive','is','getBoundingBox','refreshDimensions'],
      'net/minecraft/world/entity/LivingEntity':['push','knockback','getDamageAfterArmorAbsorb','getDamageAfterMagicAbsorb','actuallyHurt','hurt','isDamageSourceBlocked','isBlocking','heal','isInvulnerableTo'],
      'net/minecraft/world/entity/Mob':['doHurtTarget','isWithinMeleeAttackRange','getAttackBoundingBox','serverAiStep'],
      'net/minecraft/world/entity/ai/goal/Goal':['adjustedTickDelay','requiresUpdateEveryTick','canContinueToUse'],
      'net/minecraft/world/entity/ai/goal/GoalSelector':['tick','tickRunningGoals'],
      'net/minecraft/world/entity/ai/control/MoveControl':['tick'],
      'net/minecraft/world/entity/projectile/AbstractArrow':['onHitEntity','findHitEntity','canHitEntity','tick'],
      'net/minecraft/world/entity/player/Player':['attack','isInvulnerableTo'],
      'net/minecraft/world/level/Level':['getEntities'],
      'net/minecraft/server/level/ServerLevel':['getEntity'],
      'net/minecraft/server/level/ServerLevel$EntityCallbacks':['onTrackingStart','onTrackingEnd'],
      'net/minecraft/network/protocol/game/ServerboundInteractPacket':['getTarget','createAttackPacket'],
      'net/minecraft/server/network/ServerGamePacketListenerImpl':['handleInteract'],
      'net/minecraft/world/phys/AABB':['intersects','inflate','clip'],
      'net/minecraft/world/damagesource/DamageSources':['mobAttack','generic'],
      'net/minecraft/world/entity/ai/attributes/RangedAttribute':['sanitizeValue'],
    }
    names=MojangNames()
    with zipfile.ZipFile(CLIENT) as jar:
        names.jar=jar
        for c,prefix in [('net/minecraft/world/level/Level','lambda$getEntities$')]:
            cls=ClassFile(jar.read(names.named[c]+'.class'))
            raw[c]+=sorted({names.member(cls.name,m['name'],m['descriptor']) for m in cls.methods if names.member(cls.name,m['name'],m['descriptor']).startswith(prefix)})
    loader={c+'.class':list(ms) for c,ms in raw.items()}
    loader['net/minecraft/server/level/ServerLevel.class']+=['getPartEntities','getEntityOrPart']
    template=read_json(OUT/'reference-specifications/vv-loader-244.json')
    archive=next(a for a in template['archives'] if a['path'].endswith('universal.jar'))
    with zipfile.ZipFile(archive['path']) as jar:
        hook={c:sorted({m['name'] for m in ClassFile(jar.read(c)).methods}) for c in ['net/neoforged/neoforge/entity/PartEntity.class']}
    hook['net/neoforged/neoforge/event/EventHooks.class']=['canEntityGrief','onEntityDestroyBlock']
    hook['net/neoforged/neoforge/common/extensions/IBlockExtension.class']=['canEntityDestroy']
    # Installed anonymous attack packet handler, plus mapped Level lambdas whose numbering differs.
    client=next(a for a in template['archives'] if a['path'].endswith('client.jar'))
    with zipfile.ZipFile(client['path']) as jar:
        c='net/minecraft/server/network/ServerGamePacketListenerImpl$1.class'
        loader[c]=sorted({m['name'] for m in ClassFile(jar.read(c)).methods})
        c='net/minecraft/world/level/Level.class'
        exact={m['name'] for m in ClassFile(jar.read(c)).methods}
        loader[c]=[m for m in loader[c] if not m.startswith('lambda$')]+sorted(m for m in exact if m.startswith('lambda$getEntities$'))
    print('references',references('twilight-naga',raw,loader,hook))
    data_spec=dict(classes={},resources=['data/minecraft/damage_type/mob_attack.json','data/minecraft/damage_type/generic.json'])
    write_json(OUT/'vanilla-specifications/twilight-naga-data.json',data_spec)
    write_json(OUT/'vanilla-evidence/twilight-naga-data.json',prepare(data_spec))

if __name__=='__main__':collect()
