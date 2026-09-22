"""Native active utility, conversion, terrain and alternate dispenser/tree paths."""
from twilight_evidence import *
from vanilla_reference import MojangNames,CLIENT
BATCH='twilight-active-utilities'
FULL=['item/'+c for c in ['PocketWatchItem','TransformPowderItem','CrumbleHornItem','OreMagnetItem','LampOfCindersItem']]+['dispenser/TransformationDispenseBehavior','dispenser/CrumbleDispenseBehavior','util/datamaps/EntityTransformation','util/datamaps/CrumbledBlock','util/iterators/VoxelBresenhamIterator','block/MineLogCoreBlock','block/SpecialMagicLogBlock','events/ToolEvents','init/TFDataMaps']
TOKENS=['POCKET_WATCH','TRANSFORMATION_POWDER','CRUMBLE_HORN','MAGNET_ORE_TO_BLOCK_REPLACEMENTS','TREE_ORE_TO_BLOCK_REPLACEMENTS','OreMagnetItem.doMagnet','EntityUtil.convertEntity','TransformPowderItem.transformEntityIfPossible','LampOfCindersItem']

def scan_callers(target):
    hits=[]
    with zipfile.ZipFile(target['path']) as jar:
        for entry in jar.namelist():
            if not entry.startswith('twilightforest/') or not entry.endswith('.class'):continue
            b=jar.read(entry)
            if not any(s.split('.')[-1].encode() in b for s in TOKENS):continue
            c=ClassFile(b)
            for m in c.methods:
                for i in c.instructions(m.get('code',b'')):
                    if any(s in str(i['operand']) for s in TOKENS):hits.append(dict(entry=entry,class_sha256=byte_hash(b),method=m['name'],descriptor=m['descriptor'],instruction=i))
    return dict(jar_sha256=target['sha256'],scope='All TF instruction callers of five utility paths. Ominous-fire alternate conversion caller is retained as unfinished hazard provenance, not closed by this subsection.',needles=TOKENS,hits=hits)

def collect():
    target=next(t for t in read_json(OUT/'jar-inventory.json')['targets'] if t['key']=='twilightforest');res=read_json(WORK/'twilightforest/resources.json')
    words=['pocket_watch','transformation_powder','crumble_horn','ore_magnet','mining_tree_excluded','ore_bearing_ground','ores_in_ground','lamp_of_cinders','mining_log_core']
    selected=[p for p,v in res.items() if p.startswith('data/') and any(k in p+' '+str(v.get('data','')) for k in words)]
    classes={c:['*'] for c in FULL};classes.update({'util/entities/EntityUtil':['convertEntity'],'util/WorldUtil':['getAllInBB','randomOffset'],'dispenser/TFDispenserBehaviors':['init'],'config/TFConfig':['rebakeCommonOptions'],'events/RegistrationEvents':['createDataMaps']})
    with zipfile.ZipFile(target['path']) as jar:
        for c,wanted in list(classes.items()):
            if wanted==['*']:continue
            available={m['name'] for m in ClassFile(jar.read('twilightforest/'+c+'.class')).methods}
            classes[c]=sorted(set(wanted)|{m for m in available if any(m.startswith('lambda$'+n+'$') for n in wanted)})
        for c,needles in [('init/TFItems',['PocketWatchItem','TransformPowderItem','CrumbleHornItem','OreMagnetItem','LampOfCindersItem']),('init/TFBlocks',['MineLogCoreBlock'])]:
            cls=ClassFile(jar.read('twilightforest/'+c+'.class'));classes[c]=[m['name'] for m in cls.methods if m['name']=='<clinit>' or any(any(n in str(i['operand']) for n in needles) for i in cls.instructions(m.get('code',b'')))]
    print('native',native(BATCH,classes,selected),flush=True)
    raw={'net/minecraft/world/entity/Mob':['convertTo','addAdditionalSaveData','readAdditionalSaveData'],'net/minecraft/world/entity/LivingEntity':['addAdditionalSaveData','readAdditionalSaveData','setHealth','getMaxHealth','addEffect','canBeAffected','isHolding','updatingUsingItem','updateUsingItem','igniteForTicks'],'net/minecraft/world/entity/Entity':['saveWithoutId','load','igniteForSeconds','igniteForTicks','baseTick','startRiding'],'net/minecraft/world/entity/player/Inventory':['tick'],'net/minecraft/world/entity/player/Player':['interactOn'],'net/minecraft/world/item/ItemStack':['interactLivingEntity','inventoryTick','getEnchantments','hurtAndBreak','shrink','copyAndClear'],'net/minecraft/world/phys/AABB':['encapsulatingFullBlocks'],'net/minecraft/core/BlockPos':['betweenClosed'],'net/minecraft/world/level/EntityGetter':['getEntitiesOfClass'],'net/minecraft/world/level/block/Block':['playerDestroy'],'net/minecraft/world/entity/ai/attributes/AttributeMap':['load'],'net/minecraft/world/entity/ai/attributes/AttributeInstance':['load']}
    names=MojangNames()
    with zipfile.ZipFile(CLIENT) as jar:
        names.jar=jar
        for c,ms in raw.items():
            cls=ClassFile(jar.read(names.named[c]+'.class'));available={names.member(cls.name,m['name'],m['descriptor']) for m in cls.methods}
            raw[c]=sorted({m for m in available if m in ms or any(m.startswith('lambda$'+n+'$') for n in ms)})
            assert raw[c],(c,ms)
    loader={c+'.class':list(ms) for c,ms in raw.items()};template=read_json(OUT/'reference-specifications/vv-loader-244.json');a=next(a for a in template['archives'] if a['path'].endswith('client.jar'))
    with zipfile.ZipFile(a['path']) as jar:
        for c in loader:
            if c not in jar.namelist():continue
            available={m['name'] for m in ClassFile(jar.read(c)).methods};wanted=raw[c[:-6]]
            loader[c]=sorted({m for m in available if m in wanted or any(m.startswith('lambda$'+n+'$') for n in wanted if not n.startswith('lambda$'))})
    hooks={'net/neoforged/neoforge/event/EventHooks.class':['canLivingConvert','onLivingConvert','finalizeMobSpawn','canEntityGrief'],'net/neoforged/neoforge/common/CommonHooks.class':['canMobEffectBeApplied'],'net/neoforged/neoforge/event/entity/living/MobEffectEvent$Applicable.class':['*'],'net/neoforged/neoforge/common/extensions/IItemExtension.class':['isBookEnchantable'],'net/neoforged/neoforge/event/level/BlockEvent$BreakEvent.class':['*']}
    a=next(a for a in template['archives'] if a['path'].endswith('universal.jar'))
    with zipfile.ZipFile(a['path']) as jar:
        for c,ms in hooks.items():
            available={m['name'] for m in ClassFile(jar.read(c)).methods};hooks[c]=sorted(available if ms==['*'] else {m for m in available if m in ms or any(m.startswith('lambda$'+n+'$') for n in ms)})
            assert hooks[c],(c,ms,available)
    print('references',references(BATCH,raw,loader,hooks),flush=True)
    write_json(OUT/'twilightforest-active-utilities-caller-scan.json',scan_callers(target))

if __name__=='__main__':collect()
