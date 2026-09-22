"""Wraith movement, Minotaur body/equipment and native RisingZombie conversion."""
from twilight_evidence import *
from vanilla_reference import MojangNames,CLIENT
BATCH='twilight-restless-mobs'
FULL=['entity/monster/'+c for c in ['Wraith','Wraith$FlyTowardsTargetGoal','Wraith$LookAroundGoal','Wraith$MoveTowardsHomeGoal','Wraith$RandomFloatAroundGoal','Minotaur','RisingZombie']]+['entity/ai/control/NoClipMoveControl','entity/ai/goal/SimplifiedAttackGoal']
FIELDS=['WRAITH','MINOTAUR','RISING_ZOMBIE']

def scan_callers(target):
    hits=[]
    with zipfile.ZipFile(target['path']) as jar:
        for entry in jar.namelist():
            if not entry.startswith('twilightforest/') or not entry.endswith('.class'):continue
            b=jar.read(entry)
            if not any(f.encode() in b for f in FIELDS):continue
            c=ClassFile(b)
            for m in c.methods:
                for i in c.instructions(m.get('code',b'')):
                    if any('TFEntities.'+f+'L' in str(i['operand']) for f in FIELDS):hits.append(dict(entry=entry,class_sha256=byte_hash(b),method=m['name'],descriptor=m['descriptor'],instruction=i))
    return dict(jar_sha256=target['sha256'],scope='All TF class instructions referencing these three actual entity registrations; actual producers distinguished from client/data/registry references.',fields=FIELDS,hits=hits)

def collect():
    target=next(t for t in read_json(OUT/'jar-inventory.json')['targets'] if t['key']=='twilightforest')
    resources=read_json(WORK/'twilightforest/resources.json')
    selected=[p for p,v in resources.items() if '/tags/' in p and any(n in str(v) for n in ['wraith','minotaur','rising_zombie'])]
    classes={c:['*'] for c in FULL};classes['entity/EnforcedHomePoint']=['*']
    scan=scan_callers(target)
    for h in scan['hits']:
        if '/world/' in h['entry']:classes.setdefault(h['entry'][len('twilightforest/'):-6],[]).append(h['method'])
    classes.setdefault('world/components/structures/HollowHillComponent',[]).extend(['getMobID','placeFloorFeature','setFeatures','postProcess'])
    print('native',native(BATCH,classes,selected))
    raw={'net/minecraft/world/entity/monster/Zombie':['createAttributes','<init>','registerGoals','addBehaviourGoals','aiStep','doHurtTarget','finalizeSpawn'],
         'net/minecraft/world/entity/FlyingMob':['causeFallDamage','checkFallDamage','travel','onClimbable'],
         'net/minecraft/world/entity/Mob':['convertTo','isWithinMeleeAttackRange'],
         'net/minecraft/world/entity/LivingEntity':['isInvulnerableTo','hurt','aiStep'],
         'net/minecraft/world/entity/Entity':['isInvulnerableTo'],
         'net/minecraft/world/entity/ai/goal/Goal':['canContinueToUse','adjustedTickDelay'],
         'net/minecraft/world/level/EntityGetter':['getNearestPlayer'],
         'net/minecraft/world/entity/ai/targeting/TargetingConditions':['test'],
         'net/minecraft/world/item/Items':['<clinit>']}
    names=MojangNames()
    with zipfile.ZipFile(CLIENT) as jar:
        names.jar=jar
        for c,ms in raw.items():
            cls=ClassFile(jar.read(names.named[c]+'.class'));available={names.member(cls.name,m['name'],m['descriptor']) for m in cls.methods}
            raw[c]=[m for m in ms if m in available]
    loader={c+'.class':list(ms) for c,ms in raw.items()}
    print('references',references(BATCH,raw,loader))
    write_json(OUT/'twilightforest-restless-mobs-caller-scan.json',scan)

if __name__=='__main__':collect()
