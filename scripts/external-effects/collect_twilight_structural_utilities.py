"""Incremental structural utility, tree core and related native growth witnesses."""
from twilight_evidence import *
from vanilla_reference import MojangNames,CLIENT
BATCH='twilight-structural-utilities'
FULL=['item/RopeItem','item/MagicBeansItem']+['block/'+c for c in ['RopeBlock','GrowingBeanstalkBlock','SpecialMagicLogBlock','TimeLogCoreBlock','TransLogCoreBlock','SortLogCoreBlock','UberousSoilBlock','MushgloomBlock','TransformationLeavesBlock']]+['block/entity/GrowingBeanstalkBlockEntity','util/BlockCapabilityDirectionalCache','util/BlockCapabilityDirectionalCache$BlockPosAndDirection','world/components/feature/BigMushgloomFeature','world/components/feature/trees/treeplacers/TreeCorePlacer']
TOKENS=['RopeItem','RopeBlock','MAGIC_BEANS','BEANSTALK_GROWER','TIME_LOG_CORE','TRANSFORMATION_LOG_CORE','SORTING_LOG_CORE','TIME_CORE_EXCLUDED','SORTABLE_ENTITIES','BlockCapabilityDirectionalCache','UberousSoilBlock']

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
    return dict(jar_sha256=target['sha256'],scope='All TF instruction callers for Rope/Beans/remaining tree cores/native soil growth. Worldgen and compatibility tag producers retained; no runtime execution.',needles=TOKENS,hits=hits)

def collect():
    target=next(t for t in read_json(OUT/'jar-inventory.json')['targets'] if t['key']=='twilightforest');res=read_json(WORK/'twilightforest/resources.json')
    words=['twilightforest:rope','magic_beans','beanstalk','huge_stalk','time_log_core','transformation_log_core','sorting_log_core','time_core_excluded','sortable_entities','uberous_soil','mushroom/big_mushgloom']
    selected=[p for p,v in res.items() if p.startswith('data/') and any(k in p+' '+str(v.get('data','')) for k in words)]
    classes={c:['*'] for c in FULL}
    classes.update({'world/components/feature/trees/TimeTreeFeature':['generate'],'world/registration/TreeConfigurations':['<clinit>'],'util/features/FeatureLogic':['getSphericalMushroomBlockState','hasAllMushroomsProperties'],'util/WorldUtil':['getAllAround','randomOffset'],'config/TFConfig':['rebakeCommonOptions']})
    with zipfile.ZipFile(target['path']) as jar:
        for c,wanted in list(classes.items()):
            if wanted==['*']:continue
            available={m['name'] for m in ClassFile(jar.read('twilightforest/'+c+'.class')).methods};assert set(wanted)<=available,(c,set(wanted)-available)
            classes[c]=sorted(set(wanted)|{m for m in available if any(m.startswith('lambda$'+n+'$') for n in wanted)})
        for c,needles in [('init/TFItems',['RopeItem','MagicBeansItem']),('init/TFBlocks',['RopeBlock','GrowingBeanstalkBlock','TimeLogCoreBlock','TransLogCoreBlock','SortLogCoreBlock','UberousSoilBlock','MushgloomBlock']),('init/TFBlockEntities',['GrowingBeanstalkBlockEntity']),('init/TFConfiguredFeatures',['BIG_MUSHGLOOM']),('init/TFFeatures',['BigMushgloomFeature']),('init/TFFeatureModifiers',['TreeCorePlacer'])]:
            cl=ClassFile(jar.read('twilightforest/'+c+'.class'));classes[c]=[m['name'] for m in cl.methods if m['name']=='<clinit>' or any(any(n in str(i['operand']) for n in needles) for i in cl.instructions(m.get('code',b'')))]
    print('native',native(BATCH,classes,selected),flush=True)
    raw={'net/minecraft/world/entity/LivingEntity':['onClimbable','handleOnClimbable','handleRelativeFrictionAndCalculateMovement'],'net/minecraft/world/item/BlockItem':['place','canPlace','getPlacementState','placeBlock'],'net/minecraft/world/item/BoneMealItem':['applyBonemeal','growCrop'],'net/minecraft/world/level/block/Block':['pushEntitiesUp'],'net/minecraft/world/level/chunk/LevelChunkSection':['getBiomes'],'net/minecraft/core/QuartPos':['fromBlock'],'net/minecraft/world/level/block/state/BlockBehaviour$BlockStateBase':['isRandomlyTicking','randomTick','getTicker'],'net/minecraft/world/level/block/MushroomBlock':['growMushroom'],'net/minecraft/world/level/levelgen/feature/AbstractHugeMushroomFeature':['place','isValidPosition','placeTrunk'],'net/minecraft/world/item/ItemStack':['useOn'],'net/minecraft/server/level/ServerPlayerGameMode':['useItemOn'],'net/minecraft/server/ServerAdvancementManager':['getAllAdvancements','get'],'net/minecraft/world/level/LevelHeightAccessor':['getMinSection','getHeight','getMaxBuildHeight'],'net/minecraft/world/level/levelgen/feature/Feature':['setBlock']}
    names=MojangNames()
    with zipfile.ZipFile(CLIENT) as jar:
        names.jar=jar
        for c,ms in raw.items():
            cl=ClassFile(jar.read(names.named[c]+'.class'));available={names.member(cl.name,m['name'],m['descriptor']) for m in cl.methods};raw[c]=sorted({m for m in available if m in ms or any(m.startswith('lambda$'+n+'$') for n in ms)})
            assert raw[c],c
    loader={c+'.class':list(ms) for c,ms in raw.items()};template=read_json(OUT/'reference-specifications/vv-loader-244.json');a=next(a for a in template['archives'] if a['path'].endswith('client.jar'))
    with zipfile.ZipFile(a['path']) as jar:
        for c in loader:
            if c not in jar.namelist():continue
            available={m['name'] for m in ClassFile(jar.read(c)).methods};wanted=raw[c[:-6]]+(['applyBonemeal'] if c.endswith('BoneMealItem.class') else [])
            loader[c]=sorted({m for m in available if m in wanted or any(m.startswith('lambda$'+n+'$') for n in wanted if not n.startswith('lambda$'))})
    hooks={'net/neoforged/neoforge/capabilities/BlockCapabilityCache.class':['*'],'net/neoforged/neoforge/common/CommonHooks.class':['isLivingOnLadder','onPlaceItemIntoWorld'],'net/neoforged/neoforge/common/extensions/IBlockExtension.class':['isScaffolding','isLadder'],'net/neoforged/neoforge/common/extensions/IBlockStateExtension.class':['isScaffolding','isLadder'],'net/neoforged/neoforge/items/IItemHandler.class':['*'],'net/neoforged/neoforge/event/EventHooks.class':['fireBonemealEvent','fireBlockGrowFeature']}
    a=next(a for a in template['archives'] if a['path'].endswith('universal.jar'))
    with zipfile.ZipFile(a['path']) as jar:
        for c,ms in hooks.items():
            available={m['name'] for m in ClassFile(jar.read(c)).methods};hooks[c]=sorted(available if ms==['*'] else {m for m in available if m in ms or any(m.startswith('lambda$'+n+'$') for n in ms)})
            assert hooks[c],(c,ms)
    print('references',references(BATCH,raw,loader,hooks),flush=True)
    write_json(OUT/'twilightforest-structural-utilities-caller-scan.json',scan_callers(target))

if __name__=='__main__':collect()
