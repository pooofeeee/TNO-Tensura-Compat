"""Native vanishing/reappearing/locked blocks and Castle Door state machines."""
from twilight_evidence import *
from vanilla_reference import MojangNames,CLIENT
BATCH='twilight-vanishing-doors'
FULL=['block/VanishingBlock','block/ReappearingBlock','block/LockedVanishingBlock','block/CastleDoorBlock']
TOKENS=['VanishingBlock','ReappearingBlock','CastleDoorBlock','VANISHING_BLOCK','REAPPEARING_BLOCK','CASTLE_DOOR','TOWER_KEY','DARKTOWER_KEY','setKeyTower','isKeyTower','placeKeys','decorateTreasureRoom']
def scan_callers(target):
    hits=[]
    with zipfile.ZipFile(target['path']) as jar:
        for entry in jar.namelist():
            if not entry.startswith('twilightforest/') or not entry.endswith('.class'):continue
            b=jar.read(entry)
            if not any(s.encode() in b for s in TOKENS):continue
            c=ClassFile(b)
            for m in c.methods:
                for i in c.instructions(m.get('code',b'')):
                    if any(s in str(i['operand']) for s in TOKENS):hits.append(dict(entry=entry,class_sha256=byte_hash(b),method=m['name'],descriptor=m['descriptor'],instruction=i))
    return dict(jar_sha256=target['sha256'],scope='Native state machine/source closure for vanishing barriers, Tower Key and Castle Doors, using existing installed owner index.',needles=TOKENS,hits=hits)
def collect():
    target=next(t for t in read_json(OUT/'jar-inventory.json')['targets'] if t['key']=='twilightforest');res=read_json(WORK/'twilightforest/resources.json');scan=scan_callers(target)
    selected=[p for p,v in res.items() if p.startswith('data/') and any(k in p+' '+str(v.get('data','')) for k in ['vanishing_block','reappearing_block','castle_door','tower_key','darktower_key'])]
    classes={c:['*'] for c in FULL};providers={}
    for x in scan['hits']:
        if x['entry'].startswith('twilightforest/world/') and x['entry'][15:-6] not in FULL:
            providers.setdefault(x['entry'][15:-6],set()).add(x['method'])
    for c,ms in providers.items():classes[c]=sorted(ms)
    classes['world/components/structures/darktower/DarkTowerWingComponent']=sorted(set(classes.get('world/components/structures/darktower/DarkTowerWingComponent',[]))|{'<init>','addAdditionalSaveData','setKeyTower','isKeyTower'})
    classes['world/components/structures/darktower/DarkTowerMainComponent']=sorted(set(classes.get('world/components/structures/darktower/DarkTowerMainComponent',[]))|{'<init>'})
    with zipfile.ZipFile(target['path']) as jar:
        for c,ns in list(classes.items()):
            if ns==['*']:continue
            av={m['name'] for m in ClassFile(jar.read('twilightforest/'+c+'.class')).methods};assert set(ns)<=av,(c,set(ns)-av);classes[c]=sorted(set(ns)|{m for m in av if any(m.startswith('lambda$'+n+'$') for n in ns)})
        for c,needles in [('init/TFBlocks',['VanishingBlock','ReappearingBlock','CastleDoorBlock']),('init/TFItems',['tower_key']),('loot/TFLootTables',['darktower_key'])]:
            cl=ClassFile(jar.read('twilightforest/'+c+'.class'));classes[c]=sorted({m['name'] for m in cl.methods if m['name']=='<clinit>' or any(any(n in str(i['operand']) for n in needles) for i in cl.instructions(m.get('code',b'')))})
    print('native',native(BATCH,classes,selected),flush=True)
    raw={'net/minecraft/server/level/ServerPlayerGameMode':['useItemOn','destroyBlock'],'net/minecraft/world/level/Level':['setBlock','removeBlock'],'net/minecraft/world/level/block/state/BlockBehaviour':['getExplosionResistance','getCollisionShape','getDestroyProgress'],'net/minecraft/world/entity/Entity':['move','checkInsideBlocks']}
    names=MojangNames()
    with zipfile.ZipFile(CLIENT) as jar:
        names.jar=jar
        for c,ms in list(raw.items()):
            cl=ClassFile(jar.read(names.named[c]+'.class'));av={names.member(cl.name,m['name'],m['descriptor']) for m in cl.methods};raw[c]=sorted({m for m in av if m in ms or any(m.startswith('lambda$'+n+'$') for n in ms)});assert raw[c],c
    loader={c+'.class':list(ms) for c,ms in raw.items()};template=read_json(OUT/'reference-specifications/vv-loader-244.json');a=next(a for a in template['archives'] if a['path'].endswith('client.jar'))
    with zipfile.ZipFile(a['path']) as jar:
        for c in loader:
            if c not in jar.namelist():continue
            av={m['name'] for m in ClassFile(jar.read(c)).methods};wanted=raw[c[:-6]];loader[c]=sorted({m for m in av if m in wanted or any(m.startswith('lambda$'+n+'$') for n in wanted if not n.startswith('lambda$'))})
    hooks={'net/neoforged/neoforge/common/CommonHooks.class':['onRightClickBlock'],'net/neoforged/neoforge/common/extensions/IBlockExtension.class':['canEntityDestroy','getExplosionResistance']}
    print('references',references(BATCH,raw,loader,hooks),flush=True)
    write_json(OUT/'twilightforest-vanishing-doors-caller-scan.json',scan)
    write_json(OUT/'twilightforest-vanishing-doors-source-providers.json',dict(jar_sha256=target['sha256'],classes={c:sorted(ms) for c,ms in providers.items()}))
if __name__=='__main__':collect()
