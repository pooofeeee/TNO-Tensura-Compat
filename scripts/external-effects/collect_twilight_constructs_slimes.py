"""Remaining constructs, native slime inheritance and guardian equipment."""
from twilight_evidence import *
from vanilla_reference import MojangNames,CLIENT
BATCH='twilight-constructs-slimes'
FULL=['entity/monster/'+c for c in ['CarminiteGolem','MazeSlime','SnowGuardian','SnowGuardian$1','Adherent','HarbingerCube']]
FIELDS=['CARMINITE_GOLEM','MAZE_SLIME','SNOW_GUARDIAN','ADHERENT','HARBINGER_CUBE']

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
    return dict(jar_sha256=target['sha256'],scope='All TF class instructions referencing these five actual entity registrations; distinguish world producers, registration, client and data uses.',fields=FIELDS,hits=hits)

def collect():
    target=next(t for t in read_json(OUT/'jar-inventory.json')['targets'] if t['key']=='twilightforest')
    resources=read_json(WORK/'twilightforest/resources.json');ids=['carminite_golem','maze_slime','snow_guardian','adherent','harbinger_cube','ironwood','steeleaf','knightmetal','arctic']
    selected=[p for p,v in resources.items() if '/tags/' in p and any(n in str(v) for n in ids)]
    classes={c:['*'] for c in FULL}
    scan=scan_callers(target)
    for h in scan['hits']:
        if '/world/' in h['entry']:classes.setdefault(h['entry'][len('twilightforest/'):-6],[]).append(h['method'])
    with zipfile.ZipFile(target['path']) as jar:
        c=ClassFile(jar.read('twilightforest/init/TFItems.class'))
        classes['init/TFItems']=[m['name'] for m in c.methods if m['name']=='<clinit>' or any(any(n in str(i['operand']) for n in ['TFArmorMaterials.IRONWOOD','TFArmorMaterials.STEELEAF','TFArmorMaterials.KNIGHTMETAL','TFArmorMaterials.ARCTIC','TFToolMaterials.IRONWOOD','TFToolMaterials.STEELEAF','TFToolMaterials.KNIGHTMETAL']) for i in c.instructions(m.get('code',b'')))]
    print('native',native(BATCH,classes,selected))
    names=MojangNames()
    fullraw=[c for c in names.named if c=='net/minecraft/world/entity/monster/Slime' or c.startswith('net/minecraft/world/entity/monster/Slime$')]
    raw={c:[] for c in fullraw}
    fullraw+=['net/minecraft/world/entity/animal/frog/ShootTongue']
    raw['net/minecraft/world/entity/animal/frog/ShootTongue']=[]
    raw.update({'net/minecraft/world/entity/LivingEntity':['readAdditionalSaveData','setHealth'], 'net/minecraft/server/commands/SummonCommand':['createEntity'], 'net/minecraft/world/entity/ai/goal/RangedAttackGoal':['<init>','tick','requiresUpdateEveryTick'], 'net/minecraft/world/entity/Entity':['push'], 'net/minecraft/world/entity/animal/frog/Frog':['canEat','createAttributes'], 'net/minecraft/world/entity/animal/frog/FrogAi':['isEdibleEntity']})
    with zipfile.ZipFile(CLIENT) as jar:
        names.jar=jar
        for c,ms in raw.items():
            cls=ClassFile(jar.read(names.named[c]+'.class'));available={names.member(cls.name,m['name'],m['descriptor']) for m in cls.methods}
            raw[c]=sorted(available) if c in fullraw else [m for m in ms if m in available]
    loader={c+'.class':list(ms) for c,ms in raw.items()};template=read_json(OUT/'reference-specifications/vv-loader-244.json')
    a=next(a for a in template['archives'] if a['path'].endswith('client.jar'))
    with zipfile.ZipFile(a['path']) as jar:
        for c in loader:
            if c[:-6] in fullraw and c in jar.namelist():loader[c]=sorted({m['name'] for m in ClassFile(jar.read(c)).methods})
    print('references',references(BATCH,raw,loader,{'net/neoforged/neoforge/event/EventHooks.class':['onMobSplit']}))
    write_json(OUT/'twilightforest-constructs-slimes-caller-scan.json',scan)

if __name__=='__main__':collect()
