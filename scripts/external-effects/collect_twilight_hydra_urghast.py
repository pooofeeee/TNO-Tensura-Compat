"""Incremental installed Hydra/Ur-Ghast witnesses; no game process or full decompile."""
from twilight_evidence import *
from vanilla_reference import MojangNames, CLIENT

BATCH = 'twilight-hydra-urghast'
FULL = [
    'entity/boss/Hydra', 'entity/boss/Hydra$1', 'entity/boss/HydraHeadContainer',
    'entity/boss/HydraHeadContainer$State', 'entity/boss/HydraHead', 'entity/boss/HydraNeck',
    'entity/boss/HydraPart', 'entity/boss/HydraSmallPart', 'entity/boss/HydraMortar',
    'entity/boss/UrGhast', 'entity/projectile/UrGhastFireball',
    'entity/ai/goal/UrGhastAttackGoal', 'entity/ai/goal/UrGhastFlightGoal', 'entity/ai/goal/UrGhastLookGoal',
    'entity/monster/CarminiteGhastguard', 'entity/monster/CarminiteGhastling',
    'entity/ai/goal/GhastguardAttackGoal', 'entity/ai/goal/GhastguardHomedFlightGoal',
    'entity/ai/goal/GhastguardRandomFlyGoal', 'block/GhastTrapBlock', 'block/entity/GhastTrapBlockEntity',
    'network/MovePlayerPacket', 'block/entity/spawner/HydraSpawnerBlockEntity',
    'block/entity/spawner/UrGhastSpawnerBlockEntity', 'init/TFPOITypes']


def collect():
    classes = {c:['*'] for c in FULL}
    classes.update({'client/renderer/TFWeatherRenderer':['tickRain'],
                    'util/WorldUtil':['getAllInBB'],
                    'init/TFEntities':['make','buildNoEgg','<clinit>'],
                    'events/RegistrationEvents':['registerSpawnPlacements','registerEntityAttributes']})
    target = next(t for t in read_json(OUT/'jar-inventory.json')['targets'] if t['key']=='twilightforest')
    # Resolve event registration names from the installed class, not source-aid guesses.
    with zipfile.ZipFile(target['path']) as jar:
        c=ClassFile(jar.read('twilightforest/events/RegistrationEvents.class'))
        classes['events/RegistrationEvents']=[m['name'] for m in c.methods if any(
            'Hydra.registerAttributes' in str(i['operand']) or 'CarminiteGhastling.canSpawnHere' in str(i['operand'])
            or 'CARMINITE_GHASTLING' in str(i['operand']) for i in c.instructions(m.get('code',b'')))]
    resources=read_json(WORK/'twilightforest/resources.json')
    chosen=[p for p,v in resources.items() if '/tags/entity_type/' in p and any(
        x in str(v) for x in ['twilightforest:hydra','twilightforest:ur_ghast','twilightforest:carminite_ghastling'])]
    chosen += ['data/twilightforest/tags/block/common_protections.json']
    print('native',native(BATCH,classes,chosen))
    names=MojangNames()
    fullraw=[
        'net/minecraft/world/entity/projectile/Fireball',
        'net/minecraft/world/entity/projectile/LargeFireball',
        'net/minecraft/world/entity/projectile/AbstractHurtingProjectile',
        'net/minecraft/world/entity/monster/Ghast',
        'net/minecraft/world/entity/monster/Ghast$GhastMoveControl',
        'net/minecraft/world/entity/ai/goal/Goal',
        'net/minecraft/world/entity/ai/goal/GoalSelector',
        'net/minecraft/world/level/EntityBasedExplosionDamageCalculator',
        'net/minecraft/world/entity/LightningBolt']
    raw={
        'net/minecraft/world/entity/LivingEntity':['heal','setHealth','knockback','hurt','isInvulnerableTo'],
        'net/minecraft/world/entity/Entity':['getBlockExplosionResistance','shouldBlockExplode','isInvulnerableTo','igniteForSeconds','hurt','push'],
        'net/minecraft/world/entity/Mob':['checkSpawnRules','checkSpawnObstruction','serverAiStep'],
        'net/minecraft/server/level/ServerLevel':['findLightningTargetAround'],
        'net/minecraft/world/level/block/LightningRodBlock':['onLightningStrike','tick','getSignal','getDirectSignal'],
        'net/minecraft/world/entity/EntityType':['loadEntityRecursive','create','<clinit>'],
        'net/minecraft/world/damagesource/DamageSources':['fireball','explosion','generic'],
        'net/minecraft/world/level/Explosion':['explode','finalizeExplosion','getIndirectSourceEntity','getDirectSourceEntity'],
        'net/minecraft/world/entity/projectile/Projectile':['<init>','shoot','shootFromRotation','hurt','setOwner','getOwner','canHitEntity','deflect','addAdditionalSaveData','readAdditionalSaveData'],
        'net/minecraft/world/entity/projectile/ThrowableProjectile':['<init>','tick'],
    }
    with zipfile.ZipFile(CLIENT) as jar:
        names.jar=jar
        for c in fullraw:
            cls=ClassFile(jar.read(names.named[c]+'.class'))
            raw[c]=sorted({names.member(cls.name,m['name'],m['descriptor']) for m in cls.methods})
        # Only declared methods: Projectile inherits Entity.hurt in this version.
        for c,ms in raw.items():
            cls=ClassFile(jar.read(names.named[c]+'.class'))
            available={names.member(cls.name,m['name'],m['descriptor']) for m in cls.methods}
            raw[c]=[m for m in ms if m in available]
    loader={c+'.class':list(ms) for c,ms in raw.items()}
    template=read_json(OUT/'reference-specifications/vv-loader-244.json')
    with zipfile.ZipFile(next(a['path'] for a in template['archives'] if a['path'].endswith('client.jar'))) as jar:
        for c,ms in loader.items():
            if c in jar.namelist():
                available={m['name'] for m in ClassFile(jar.read(c)).methods}
                loader[c]=[m for m in ms if m in available]
    print('references',references(BATCH,raw,loader,{'net/neoforged/neoforge/event/EventHooks.class':['onLivingHeal']}))
    # Exhaustive installed TF class scan for the four DamageType field references.
    wanted=['HYDRA_BITE','HYDRA_FIRE','HYDRA_MORTAR','GHAST_TEAR']; hits=[]
    with zipfile.ZipFile(target['path']) as jar:
        for entry in jar.namelist():
            if not entry.startswith('twilightforest/') or not entry.endswith('.class'):continue
            data=jar.read(entry)
            if not any(n.encode() in data for n in wanted):continue
            cls=ClassFile(data)
            for m in cls.methods:
                for i in cls.instructions(m.get('code',b'')):
                    if any('TFDamageTypes.'+n+'Lnet/minecraft/resources/ResourceKey;' in str(i['operand']) for n in wanted):
                        hits.append(dict(entry=entry,class_sha256=byte_hash(data),method=m['name'],descriptor=m['descriptor'],instruction=i))
    write_json(OUT/'twilightforest-hydra-urghast-caller-scan.json',dict(jar_sha256=target['sha256'],scope='All installed twilightforest/*.class instructions; producer calls distinguished from registration, data generation and defensive source tests.',fields=wanted,hits=hits))


if __name__=='__main__':collect()
