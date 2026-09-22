"""R2f8d giant mobs, actual equipment, giant mining and maze-tool rules."""
from twilight_evidence import *
from vanilla_reference import MojangNames,CLIENT
BATCH='twilight-giants-tools'
FULL=['entity/monster/GiantMiner','entity/monster/ArmoredGiant','item/GiantPickItem','item/GiantSwordItem','item/MazebreakerPickItem','util/TFToolMaterials','block/GiantBlock','components/entity/GiantPickaxeMiningAttachment','loot/modifiers/GiantToolGroupingModifier','loot/conditions/GiantPickUsedCondition']

def scan_callers(target):
    needles=['TFDamageTypes.ANTLnet/minecraft/resources/ResourceKey;','TFDataAttachments.GIANT_PICKAXE_MINING','GiantBlock.getVolume','GIANT_MINERL','ARMORED_GIANTL']
    hits=[]
    with zipfile.ZipFile(target['path']) as jar:
        for entry in jar.namelist():
            if not entry.startswith('twilightforest/') or not entry.endswith('.class'):continue
            b=jar.read(entry)
            if not any(x.encode() in b for x in ['ANT','GIANT_PICKAXE_MINING','GiantBlock','GIANT_MINER','ARMORED_GIANT']):continue
            c=ClassFile(b)
            for m in c.methods:
                for i in c.instructions(m.get('code',b'')):
                    if any(n in str(i['operand']) for n in needles):hits.append(dict(entry=entry,class_sha256=byte_hash(b),method=m['name'],descriptor=m['descriptor'],instruction=i))
    return dict(jar_sha256=target['sha256'],scope='All installedTF class instructions; ANT, giant mining state/volume and mob registry accesses.',needles=needles,hits=hits)

def collect():
    target=next(t for t in read_json(OUT/'jar-inventory.json')['targets'] if t['key']=='twilightforest')
    r=read_json(WORK/'twilightforest/resources.json');ids=['giant_miner','armored_giant','giant_pickaxe','giant_sword','mazebreaker_pickaxe']
    selected=[p for p,v in r.items() if '/tags/' in p and (any(x in str(v) for x in ids) or any(x in p for x in ['giants_spawnable_on','incorrect_for_giant_tool','repairs_giant_tools','mazebreaker_accelerated_mining']))]
    selected+=['data/twilightforest/tags/block/clouds.json','data/neoforge/loot_modifiers/global_loot_modifiers.json','data/twilightforest/loot_modifiers/giant_pick_grouping.json']
    classes={c:['*'] for c in FULL}
    classes['events/ToolEvents']=['setup','handleGiantPickaxeMining','canHarvestWithGiantPick','shouldBreakGiantBlock','damageNonMazebreakerToolsMore']
    classes['world/components/structures/trollcave/CloudCastleComponent']=['postProcess','placeGiantMiner','placeWarrior']
    classes['world/components/structures/type/GiantHouseStructure']=['buildGiantHouseConfig']
    classes['world/components/structures/type/TrollCaveStructure']=['buildTrollCaveConfig']
    with zipfile.ZipFile(target['path']) as jar:
        for short,needles in [('init/TFItems',['GiantPickItem','GiantSwordItem','MazebreakerPickItem']),('init/TFDataAttachments',['GiantPickaxeMiningAttachment']),('init/TFBlocks',['giant_obsidian']),('events/RegistrationEvents',['GiantToolGroupingModifier.CONVERSIONS']),('init/TFLoot',['GiantPickUsedCondition'])]:
            c=ClassFile(jar.read('twilightforest/'+short+'.class'))
            classes[short]=[m['name'] for m in c.methods if m['name']=='<clinit>' or any(any(n in str(i['operand']) for n in needles) for i in c.instructions(m.get('code',b'')))]
        # The giant-obsidian constructor is a lambda separate from its registry-name instruction.
        c=ClassFile(jar.read('twilightforest/init/TFBlocks.class'))
        classes['init/TFBlocks'] += [m['name'] for m in c.methods if any(i['operand']==204800.0 for i in c.instructions(m.get('code',b'')))]
    print('native',native(BATCH,classes,selected))
    raw={'net/minecraft/world/entity/player/Player':['createAttributes','getBlockInteractionRange','getEntityInteractionRange'],
         'net/minecraft/world/entity/LivingEntity':['createLivingAttributes','collectEquipmentChanges'],
         'net/minecraft/world/entity/Mob':['<clinit>','createMobAttributes','getAttackBoundingBox','isWithinMeleeAttackRange','addAdditionalSaveData','readAdditionalSaveData'],
         'net/minecraft/world/entity/ai/attributes/AttributeMap':['getInstance'],
         'net/minecraft/world/entity/ai/goal/MeleeAttackGoal':['getAttackInterval','requiresUpdateEveryTick','canPerformAttack'],
         'net/minecraft/world/item/TieredItem':['<init>','isValidRepairItem'],
         'net/minecraft/world/item/PickaxeItem':['<init>'],
         'net/minecraft/world/item/DiggerItem':['<init>','createAttributes','hurtEnemy','postHurtEnemy'],
         'net/minecraft/world/item/SwordItem':['<init>','createAttributes','hurtEnemy','postHurtEnemy'],
         'net/minecraft/world/item/ArmorMaterials':['<clinit>','register'],
         'net/minecraft/world/item/ArmorItem':['<init>','createAttributes'],
         'net/minecraft/world/item/Item':['mineBlock','canAttackBlock','getDestroySpeed'],
         'net/minecraft/server/level/ServerPlayerGameMode':['destroyBlock']}
    names=MojangNames()
    with zipfile.ZipFile(CLIENT) as jar:
        names.jar=jar
        for c,ms in raw.items():
            cls=ClassFile(jar.read(names.named[c]+'.class'));available={names.member(cls.name,m['name'],m['descriptor']) for m in cls.methods};raw[c]=[m for m in ms if m in available]
            if c.endswith('LivingEntity') or c.endswith('ArmorMaterials') or c.endswith('ArmorItem'):
                raw[c]+=[names.member(cls.name,m['name'],m['descriptor']) for m in cls.methods if (names.member(cls.name,m['name'],m['descriptor']).startswith('lambda$collectEquipmentChanges') or (c.endswith('ArmorMaterials') and names.member(cls.name,m['name'],m['descriptor']).startswith('lambda$static')) or (c.endswith('ArmorItem') and names.member(cls.name,m['name'],m['descriptor']).startswith('lambda$new')))]
    hooks={'net/neoforged/neoforge/common/SimpleTier.class':['*'],'net/neoforged/neoforge/common/CommonHooks.class':['fireBlockBreak'],'net/neoforged/neoforge/event/EventHooks.class':['doPlayerHarvestCheck']}
    # Expand wildcard because incremental reference reuse compares explicit method names.
    a=next(a for a in read_json(OUT/'reference-specifications/vv-loader-244.json')['archives'] if a['path'].endswith('universal.jar'))
    with zipfile.ZipFile(a['path']) as jar:hooks['net/neoforged/neoforge/common/SimpleTier.class']=[m['name'] for m in ClassFile(jar.read('net/neoforged/neoforge/common/SimpleTier.class')).methods]
    loader={c+'.class':list(ms) for c,ms in raw.items()}
    a=next(a for a in read_json(OUT/'reference-specifications/vv-loader-244.json')['archives'] if a['path'].endswith('client.jar'))
    with zipfile.ZipFile(a['path']) as jar:
        for c,ms in loader.items():
            if c not in jar.namelist():continue
            prefixes={m.rsplit('$',1)[0]+'$' for m in ms if m.startswith('lambda$')}
            names244={m['name'] for m in ClassFile(jar.read(c)).methods}
            loader[c]=[m for m in ms if not m.startswith('lambda$')]+sorted(m for m in names244 if any(m.startswith(p) for p in prefixes))
    print('references',references(BATCH,raw,loader,hooks))
    write_json(OUT/'twilightforest-giants-tools-caller-scan.json',scan_callers(target))

if __name__=='__main__':collect()
