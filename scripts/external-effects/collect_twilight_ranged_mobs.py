"""R2f8a remaining ranged mobs; reuse the original census and boss/Frosted evidence."""
from twilight_evidence import *
from vanilla_reference import MojangNames,CLIENT

BATCH='twilight-ranged-mobs'
FIELDS=['SCORCHED','LEAF_BRAIN','LOST_WORDS','SCHOOLED','SNOWBALL_FIGHT']
FULL=['entity/monster/'+c for c in ['FireBeetle','SlimeBeetle','SkeletonDruid','DeathTome','DeathTome$1','DeathTome$2','HostileWolf','HostileWolf$LeapGoal','WinterWolf','MistWolf','StableIceCore','UnstableIceCore']]+['entity/ai/goal/BreathAttackGoal']+['entity/projectile/'+c for c in ['NatureBolt','TomeBolt','SlimeProjectile','IceSnowball','TFThrowable']]


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
                    if any('TFDamageTypes.'+n+'Lnet/minecraft/resources/ResourceKey;' in str(i['operand']) for n in FIELDS):hits.append(dict(entry=entry,class_sha256=byte_hash(data),method=m['name'],descriptor=m['descriptor'],instruction=i))
    return dict(jar_sha256=target['sha256'],scope='All installed TF classes, five newly touched fields only; original declarations reused.',fields=FIELDS,hits=hits)


def collect():
    target=next(t for t in read_json(OUT/'jar-inventory.json')['targets'] if t['key']=='twilightforest')
    classes={c:['*'] for c in FULL}
    classes.update({'events/MiscEvents':['setup','addTomesToLecterns'],'world/components/structures/lichtowerrevamp/LichTowerWingRoom':['putTrappableLectern'],'entity/monster/SwarmSpider':['finalizeSpawn','summonJockey'],'util/ColorUtil':['<clinit>','getColor']})
    with zipfile.ZipFile(target['path']) as jar:
        c=ClassFile(jar.read('twilightforest/util/ColorUtil.class'))
        classes['util/ColorUtil'] += [m['name'] for m in c.methods if any('STAINED_GLASS' in str(i['operand']) or 'TERRACOTTA' in str(i['operand']) for i in c.instructions(m.get('code',b'')))]
    ids=['fire_beetle','slime_beetle','skeleton_druid','death_tome','nature_bolt','tome_bolt','slime_blob','ice_snowball','winter_wolf','mist_wolf','hostile_wolf','stable_ice_core','unstable_ice_core']
    resources=read_json(WORK/'twilightforest/resources.json')
    selected=[p for p,v in resources.items() if ('/tags/entity_type/' in p and any(x in str(v) for x in ids)) or p.endswith('/druid_projectile_replaceable.json')]
    print('native',native(BATCH,classes,selected))
    raw={'net/minecraft/world/entity/monster/AbstractSkeleton':['<init>','registerGoals','reassessWeaponGoal','createAttributes','performRangedAttack','getArrow','populateDefaultEquipmentSlots','finalizeSpawn','aiStep','isSunBurnTick','doHurtTarget','setItemSlot','readAdditionalSaveData','getHardAttackInterval','getAttackInterval'],
         'net/minecraft/world/entity/EntitySelector':['<clinit>'],
         'net/minecraft/world/effect/PoisonMobEffect':['<init>','applyEffectTick','shouldApplyEffectTickThisTick'],
         'net/minecraft/world/effect/MobEffects':['<clinit>'],
         'net/minecraft/world/entity/Mob':['createMobAttributes','doHurtTarget','isSunBurnTick'],
         'net/minecraft/world/entity/monster/Monster':['createMonsterAttributes'],
         'net/minecraft/world/damagesource/DamageSources':['thrown','mobAttack','explosion','magic'],
         'net/minecraft/world/entity/ai/goal/LeapAtTargetGoal':['<init>','canUse','canContinueToUse','start']}
    names=MojangNames()
    with zipfile.ZipFile(CLIENT) as jar:
        names.jar=jar
        for c,ms in raw.items():
            cls=ClassFile(jar.read(names.named[c]+'.class'));available={names.member(cls.name,m['name'],m['descriptor']) for m in cls.methods}
            raw[c]=[m for m in ms if m in available]
            if c.endswith('EntitySelector'):
                raw[c]+=[names.member(cls.name,m['name'],m['descriptor']) for m in cls.methods if names.member(cls.name,m['name'],m['descriptor']).startswith('lambda$')]
    print('references',references(BATCH,raw,{c+'.class':ms for c,ms in raw.items()}))
    write_json(OUT/'twilightforest-ranged-mobs-caller-scan.json',scan_callers(target))


if __name__=='__main__':collect()
