"""Remaining spider/swarm/crab/borer surfaces; no new damage declarations."""
from twilight_evidence import *
from vanilla_reference import MojangNames,CLIENT
BATCH='twilight-arthropods'
FULL=['entity/monster/'+c for c in ['HedgeSpider','KingSpider','SwarmSpider','TowerBroodling','MosquitoSwarm','MosquitoSwarm$1','HelmetCrab','TowerwoodBorer','TowerwoodBorer$HideInTowerwoodGoal','TowerwoodBorer$SummonBorersGoal']]+['entity/ai/goal/AlwaysWatchTargetGoal','block/InfestedTowerwoodBlock']

def scan_callers(target):
    hits=[]
    with zipfile.ZipFile(target['path']) as jar:
        for entry in jar.namelist():
            if not entry.startswith('twilightforest/') or not entry.endswith('.class'):continue
            b=jar.read(entry)
            if b'getReinforcementType' not in b:continue
            c=ClassFile(b)
            for m in c.methods:
                for i in c.instructions(m.get('code',b'')):
                    if '.getReinforcementType(' in str(i['operand']):hits.append(dict(entry=entry,class_sha256=byte_hash(b),method=m['name'],descriptor=m['descriptor'],instruction=i))
    return dict(jar_sha256=target['sha256'],scope='All installedTF class instructions; getReinforcementType call sites, not declarations.',hits=hits)

def collect():
    target=next(t for t in read_json(OUT/'jar-inventory.json')['targets'] if t['key']=='twilightforest')
    resources=read_json(WORK/'twilightforest/resources.json');ids=['hedge_spider','king_spider','swarm_spider','carminite_broodling','mosquito_swarm','helmet_crab','towerwood_borer','infested_towerwood']
    selected=[p for p,v in resources.items() if '/tags/' in p and any(x in str(v) for x in ids)]
    print('native',native(BATCH,{c:['*'] for c in FULL},selected))
    fullraw=['net/minecraft/world/entity/monster/'+c for c in ['Spider','Spider$SpiderAttackGoal','Spider$SpiderTargetGoal','Spider$SpiderEffectsGroupData']]+['net/minecraft/world/effect/HungerMobEffect']
    raw={'net/minecraft/world/food/FoodData':['tick','addExhaustion'],
         'net/minecraft/world/entity/player/Player':['causeFoodExhaustion'],
         'net/minecraft/world/level/block/Block':['dropResources','spawnAfterBreak','wasExploded','playerDestroy'],
         'net/minecraft/world/level/block/state/BlockBehaviour':['onExplosionHit','spawnAfterBreak'],
         'net/minecraft/world/entity/Entity':['ejectPassengers','removeVehicle','canRide','isPushable'],
         'net/minecraft/world/entity/ai/goal/Goal':['requiresUpdateEveryTick','canContinueToUse'],
         'net/minecraft/world/damagesource/DamageSources':['starve']}
    names=MojangNames()
    with zipfile.ZipFile(CLIENT) as jar:
        names.jar=jar
        for c in fullraw:raw[c]=[] # expanded from exact mapped owner below
        for c,ms in raw.items():
            cls=ClassFile(jar.read(names.named[c]+'.class'));available={names.member(cls.name,m['name'],m['descriptor']) for m in cls.methods}
            raw[c]=sorted(available) if c in fullraw else [m for m in ms if m in available]
    loader={c+'.class':list(ms) for c,ms in raw.items()}
    template=read_json(OUT/'reference-specifications/vv-loader-244.json')
    a=next(a for a in template['archives'] if a['path'].endswith('client.jar'))
    with zipfile.ZipFile(a['path']) as jar:
        for c,ms in loader.items():
            if c not in jar.namelist():continue
            actual={m['name'] for m in ClassFile(jar.read(c)).methods}
            if c[:-6] in fullraw:loader[c]=sorted(actual)
    print('references',references(BATCH,raw,loader,{'net/neoforged/neoforge/common/CommonHooks.class':['handleBlockDrops']}))
    rawresources=['data/minecraft/tags/damage_type/always_triggers_silverfish.json','data/minecraft/tags/enchantment/prevents_infested_spawns.json','data/minecraft/tags/entity_type/immune_to_infested.json','data/minecraft/tags/entity_type/immune_to_oozing.json']
    with zipfile.ZipFile(CLIENT) as jar:rawresources=[p for p in rawresources if p in jar.namelist()]
    spec=dict(classes={},resources=rawresources);write_json(OUT/'vanilla-specifications/twilight-arthropod-tags.json',spec);write_json(OUT/'vanilla-evidence/twilight-arthropod-tags.json',prepare(spec))
    archive=next(a for a in template['archives'] if a['path'].endswith('universal.jar'))
    with zipfile.ZipFile(archive['path']) as jar:
        tags=[p for p in jar.namelist() if p.endswith('/always_triggers_silverfish.json') or p.endswith('/prevents_infested_spawns.json') or p=='data/neoforge/tags/damage_type/is_poison.json']
    spec=dict(id='twilight-arthropod-tags-244',scope='Exactloader additions to two touched native eligibility tags.',archives=[dict(path=archive['path'],sha256=archive['sha256'],classes={},resources=tags)])
    write_json(OUT/'reference-specifications/twilight-arthropod-tags-244.json',spec);write_json(OUT/'reference-evidence/twilight-arthropod-tags-244.json',collect_reference(spec))
    write_json(OUT/'twilightforest-arthropods-caller-scan.json',scan_callers(target))

if __name__=='__main__':collect()
