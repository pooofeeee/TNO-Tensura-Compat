"""Incremental R2f7 witnesses. Reuse Frosted and existing native/loader proofs."""
from twilight_evidence import *
from vanilla_reference import MojangNames,CLIENT

BATCH='twilight-yeti-queen'
FIELDS=['FALLING_ICE','YEETED','SQUISH','CHILLING_BREATH']
FULL=['entity/boss/AlphaYeti','entity/boss/AlphaYeti$1','entity/boss/AlphaYeti$2',
      'entity/boss/SnowQueen','entity/boss/SnowQueen$Phase','entity/boss/SnowQueenIceShield',
      'entity/ai/goal/YetiRampageGoal','entity/ai/goal/YetiTiredGoal','entity/ai/goal/ThrowRiderGoal',
      'entity/ai/goal/HoverBaseGoal','entity/ai/goal/HoverSummonGoal','entity/ai/goal/HoverThenDropGoal',
      'entity/ai/goal/HoverBeamGoal','entity/projectile/FallingIce','entity/monster/IceCrystal',
      'entity/monster/BaseIceMob','components/entity/YetiThrowAttachment','events/HostileMountEvents',
      'network/UpdateThrownPacket','block/entity/spawner/AlphaYetiSpawnerBlockEntity',
      'block/entity/spawner/SnowQueenSpawnerBlockEntity']


def scan_callers(target):
    hits=[]
    with zipfile.ZipFile(target['path']) as jar:
        for entry in jar.namelist():
            if not entry.startswith('twilightforest/') or not entry.endswith('.class'):continue
            data=jar.read(entry)
            if not any(n.encode() in data for n in FIELDS):continue
            c=ClassFile(data)
            for m in c.methods:
                for i in c.instructions(m.get('code',b'')):
                    if any('TFDamageTypes.'+n+'Lnet/minecraft/resources/ResourceKey;' in str(i['operand']) for n in FIELDS):
                        hits.append(dict(entry=entry,class_sha256=byte_hash(data),method=m['name'],descriptor=m['descriptor'],instruction=i))
    return dict(jar_sha256=target['sha256'],scope='All installed TF classes, only four newly touched fields; not a repeated declaration census.',fields=FIELDS,hits=hits)


def collect():
    classes={c:['*'] for c in FULL}
    classes['events/CapabilityEvents']=['setup','updatePlayerCaps']
    classes['entity/monster/Yeti']=['registerGoals']
    classes['entity/monster/Yeti$1']=['*']
    classes['init/TFDataAttachments']=['<clinit>']
    target=next(t for t in read_json(OUT/'jar-inventory.json')['targets'] if t['key']=='twilightforest')
    with zipfile.ZipFile(target['path']) as jar:
        c=ClassFile(jar.read('twilightforest/init/TFDataAttachments.class'))
        classes['init/TFDataAttachments'] += [m['name'] for m in c.methods if any('YetiThrowAttachment' in str(i['operand']) for i in c.instructions(m.get('code',b'')))]
    resources=read_json(WORK/'twilightforest/resources.json')
    selected=[p for p,v in resources.items() if '/tags/entity_type/' in p and (p.endswith('/bosses.json') or any(
        x in str(v) for x in ['alpha_yeti','snow_queen','ice_crystal','falling_ice','rides_obstruct_snatching']))]
    print('native',native(BATCH,classes,selected))
    raw={'net/minecraft/world/entity/Entity':['causeFallDamage','checkFallDamage','move','startRiding','stopRiding','removeVehicle','removePassenger','canRide','canAddPassenger','getDimensions','refreshDimensions','push'],
         'net/minecraft/world/entity/LivingEntity':['causeFallDamage','calculateFallDamage','randomTeleport'],
         'net/minecraft/world/entity/ai/goal/RangedAttackGoal':['<init>','canUse','canContinueToUse','start','stop','tick','requiresUpdateEveryTick'],
         'net/minecraft/world/entity/ai/control/FlyingMoveControl':['<init>','tick'],
         'net/minecraft/world/entity/projectile/AbstractArrow':['onHitEntity']}
    names=MojangNames()
    with zipfile.ZipFile(CLIENT) as jar:
        names.jar=jar
        for c,ms in raw.items():
            cls=ClassFile(jar.read(names.named[c]+'.class'));available={names.member(cls.name,m['name'],m['descriptor']) for m in cls.methods}
            raw[c]=[m for m in ms if m in available]
    loader={c+'.class':list(ms) for c,ms in raw.items()}
    print('references',references(BATCH,raw,loader,{
        'net/neoforged/neoforge/attachment/AttachmentType$Builder.class':['<init>','build','serialize'],
        'net/neoforged/neoforge/common/Tags$EntityTypes.class':['<clinit>','tag'],
        'net/neoforged/neoforge/common/CommonHooks.class':['onLivingFall'],
        'net/neoforged/neoforge/event/EventHooks.class':['canMountEntity']}))
    write_json(OUT/'twilightforest-yeti-queen-caller-scan.json',scan_callers(target))


if __name__=='__main__':collect()
