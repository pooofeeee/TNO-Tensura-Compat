"""Four contact hazards, native plant-state mechanics and genuine sources."""
from twilight_evidence import *
from vanilla_reference import MojangNames,CLIENT
BATCH='twilight-contact-hazards'
FIELDS=['THORNS','OREBERRY','KNIGHTMETAL','FIERY']
FULL=['block/'+x for x in ['ThornsBlock','BurntThornsBlock','ThornRoseBlock','SpecialStemLeavesBlock','ConnectableRotatedPillarBlock','OreBerryBlock','FieryBlock','KnightmetalBlock','TFBushBlock','BerryBushBlock','DarkTowerBerryBushBlock','SnowLoggable']]+['world/components/feature/ThornFeature','world/components/feature/UndergroundPlantFeature','world/components/feature/BerryBushFeature']
TOKENS=['TFDamageTypes.'+f for f in FIELDS]+['ThornsBlock','OreBerryBlock','FieryBlock','KnightmetalBlock','TFBushBlock','SnowLoggable','BROWN_THORNS','GREEN_THORNS','BURNT_THORNS','OREBERRY','FIERY_BLOCK','KNIGHTMETAL_BLOCK']
def scan_callers(target):
    hits=[]
    with zipfile.ZipFile(target['path']) as jar:
        for entry in jar.namelist():
            if not entry.startswith('twilightforest/') or not entry.endswith('.class'):continue
            b=jar.read(entry)
            if not any(s.rsplit('.',1)[-1].encode() in b for s in TOKENS):continue
            c=ClassFile(b)
            for m in c.methods:
                for i in c.instructions(m.get('code',b'')):
                    if any(s in str(i['operand']) for s in TOKENS):hits.append(dict(entry=entry,class_sha256=byte_hash(b),method=m['name'],descriptor=m['descriptor'],instruction=i))
    return dict(jar_sha256=target['sha256'],scope='Installed TF instruction callers for four contact sources and actual hazard/plant producers. Shared SnowLoggable callers retained for later whole-mod disposition. Static only.',needles=TOKENS,hits=hits)
def collect():
    target=next(t for t in read_json(OUT/'jar-inventory.json')['targets'] if t['key']=='twilightforest');res=read_json(WORK/'twilightforest/resources.json')
    words=['thorns','thorn_rose','thorn_leaves','oreberry','oreberries','berry_bush','berries','fiery_block','knightmetal_block','immune_to_thorns','fiery.json','knightmetal.json','strider_warm_blocks']
    selected=[p for p,v in res.items() if p.startswith('data/') and any(k in p+' '+str(v.get('data','')) for k in words)]
    classes={c:['*'] for c in FULL}
    classes.update({'world/components/structures/finalcastle/FinalCastleFoundation13ComponentThorns':['postProcess','makeThornVine','makeThornBranch'],'item/LampOfCindersItem':['burnBlock'],'events/EntityEvents':['reduceFrostedEffectIfOnFire'],'init/TFDamageTypes':['getDamageSource','getEntityDamageSource','getIndirectEntityDamageSource']})
    with zipfile.ZipFile(target['path']) as jar:
        for c,ns in list(classes.items()):
            if ns==['*']:continue
            av={m['name'] for m in ClassFile(jar.read('twilightforest/'+c+'.class')).methods};assert set(ns)<=av,(c,set(ns)-av);classes[c]=sorted(set(ns)|{m for m in av if any(m.startswith('lambda$'+n+'$') for n in ns)})
        for c,needles in [('init/TFBlocks',['ThornsBlock','OreBerryBlock','FieryBlock','KnightmetalBlock','BerryBushBlock','THORN_LEAVES']),('init/TFFeatures',['ThornFeature','UndergroundPlantFeature','BerryBushFeature']),('init/TFConfiguredFeatures',['THORNS','OREBERRIES','BUSHES']),('init/TFPlacedFeatures',['THORNS','OREBERRIES','BUSHES']),('events/RegistrationEvents',['setFlammable']),('loot/TFLootTables',['berry','berries'])]:
            cl=ClassFile(jar.read('twilightforest/'+c+'.class'));classes[c]=[m['name'] for m in cl.methods if m['name']=='<clinit>' or any(any(n in str(i['operand']) for n in needles) for i in cl.instructions(m.get('code',b'')))]
    print('native',native(BATCH,classes,selected),flush=True)
    raw={'net/minecraft/world/level/block/FireBlock':['tick'],'net/minecraft/world/entity/item/ItemEntity':['hurt'],'net/minecraft/world/entity/decoration/ArmorStand':['hurt'],'net/minecraft/world/level/block/state/BlockBehaviour':['entityInside','getCollisionShape'],'net/minecraft/world/level/block/Block':['stepOn'],'net/minecraft/server/level/ServerPlayerGameMode':['destroyBlock'],'net/minecraft/world/damagesource/DamageSource':['getSourcePosition','scalesWithDifficulty'],'net/minecraft/world/entity/Entity':['isInvulnerableTo','move','checkInsideBlocks'],'net/minecraft/world/entity/LivingEntity':['hurt','knockback','getDamageAfterArmorAbsorb','getDamageAfterMagicAbsorb','actuallyHurt','isDamageSourceBlocked'],'net/minecraft/world/level/block/MagmaBlock':['stepOn'],'net/minecraft/world/level/block/SweetBerryBushBlock':['entityInside'],'net/minecraft/world/entity/monster/Strider':['<clinit>','tick','getMoveSpeed','getRiddenSpeed','isSuffocating','setSuffocating'],'net/minecraft/world/item/BlockItem':['place'],'net/minecraft/world/item/BoneMealItem':['applyBonemeal','growCrop'],'net/minecraft/world/item/ItemStack':['canBeHurtBy']}
    names=MojangNames()
    with zipfile.ZipFile(CLIENT) as jar:
        names.jar=jar
        for c,ms in raw.items():
            cl=ClassFile(jar.read(names.named[c]+'.class'));av={names.member(cl.name,m['name'],m['descriptor']) for m in cl.methods};raw[c]=sorted({m for m in av if m in ms or any(m.startswith('lambda$'+n+'$') for n in ms)});assert raw[c],c
    loader={c+'.class':list(ms) for c,ms in raw.items()};template=read_json(OUT/'reference-specifications/vv-loader-244.json');a=next(a for a in template['archives'] if a['path'].endswith('client.jar'))
    with zipfile.ZipFile(a['path']) as jar:
        for c in loader:
            if c not in jar.namelist():continue
            av={m['name'] for m in ClassFile(jar.read(c)).methods};wanted=raw[c[:-6]]+(['removeBlock'] if c.endswith('ServerPlayerGameMode.class') else [])
            loader[c]=sorted({m for m in av if m in wanted or any(m.startswith('lambda$'+n+'$') for n in wanted if not n.startswith('lambda$'))})
    hooks={'net/neoforged/neoforge/common/CommonHooks.class':['fireBlockBreak','onLivingKnockBack','isEntityInvulnerableTo'],'net/neoforged/neoforge/common/extensions/IBlockExtension.class':['isFireSource']}
    print('references',references(BATCH,raw,loader,hooks),flush=True)
    write_json(OUT/'twilightforest-contact-hazards-caller-scan.json',scan_callers(target))
if __name__=='__main__':collect()
