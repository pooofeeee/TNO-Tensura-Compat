"""Incremental passive-animal authority, native callbacks and quest resources."""
from twilight_evidence import *
from vanilla_reference import MojangNames,CLIENT
BATCH='twilight-passive-entities'
FULL=['entity/passive/'+x for x in ['Bird','FlyingBird','TinyBird','TinyBirdVariant','Raven','Penguin','Squirrel','Boar','Deer','Bighorn','DwarfRabbit','DwarfRabbitVariant','QuestRam','quest/QuestReloadListener','quest/ram/QuestingRamContext','quest/ram/QuestingRamCurrentContext']]+['entity/ai/goal/QuestRamEatWoolGoal','network/SyncQuestsPacket']
TOKENS=['QuestRam','QuestingRam','QuestReloadListener','SyncQuestsPacket','entity/passive/','SHIKA_SENBEI','FALL_DAMAGE_IMMUNE','FREEZE_IMMUNE_ENTITY_TYPES']
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
    return dict(jar_sha256=target['sha256'],scope='All TF instruction references to passive classes, Quest Ram callbacks and native immunity tags. Cosmetic/worldgen/data consumers retained for disposition; static only.',needles=TOKENS,hits=hits)
def collect():
    target=next(t for t in read_json(OUT/'jar-inventory.json')['targets'] if t['key']=='twilightforest');res=read_json(WORK/'twilightforest/resources.json')
    words=['quest_ram','questing_ram','deer','boar','penguin','tiny_bird','raven','squirrel','dwarf_rabbit','bighorn','fall_damage_immune','freeze_immune_entity_types']
    selected=[p for p,v in res.items() if p.startswith('data/') and any(k in p+' '+str(v.get('data','')) for k in words) and any(x in p for x in ['/tags/','/loot_table/','/twilight/quests/','/twilight/dwarf_rabbit_variant/','/twilight/tiny_bird_variant/','/advancement/quest','/neoforge/data_maps/'])]
    classes={c:['*'] for c in FULL}
    classes.update({'entity/EnforcedHomePoint':['*'],'entity/ai/goal/AttemptToGoHomeGoal':['*'],'world/components/structures/QuestGrove':['handleDataMarker'],'util/features/FeaturePlacers':['placeEntity'],'util/landmarks/LandmarkUtil':['markStructureConquered','locateNearestLandmarkStart'],'advancements/SimpleAdvancementTrigger':['trigger'],'advancements/SimpleAdvancementTrigger$TriggerInstance':['completeQuestRam'],'events/EntityEvents':['handleQuestSyncing','<init>']})
    with zipfile.ZipFile(target['path']) as jar:
        for c,ns in list(classes.items()):
            if ns==['*']:continue
            available={m['name'] for m in ClassFile(jar.read('twilightforest/'+c+'.class')).methods};assert set(ns)<=available,(c,set(ns)-available)
            classes[c]=sorted(set(ns)|{m for m in available if any(m.startswith('lambda$'+n+'$') for n in ns)})
        for c,needles in [('init/TFEntities',['Bighorn','Boar','Deer','DwarfRabbit','Penguin','QuestRam','Raven','Squirrel','TinyBird']),('init/TFItems',['QUEST_RAM_TROPHY']),('events/RegistrationEvents',['QuestReloadListener','SyncQuestsPacket','registerAttributes','Sheep.createAttributes']),('init/TFAdvancements',['quest_ram_completed']),('loot/TFLootTables',['questing_ram'])]:
            cl=ClassFile(jar.read('twilightforest/'+c+'.class'));classes[c]=[m['name'] for m in cl.methods if m['name']=='<clinit>' or any(any(n in str(i['operand']) for n in needles) for i in cl.instructions(m.get('code',b'')))]
    print('native',native(BATCH,classes,selected),flush=True)
    raw={'net/minecraft/world/entity/animal/Animal':['mobInteract','usePlayerItem','canMate'],'net/minecraft/world/entity/LivingEntity':['heal','setHealth','causeFallDamage','calculateFallDamage','canFreeze'],'net/minecraft/world/entity/Entity':['canFreeze','checkInsideBlocks','isIgnoringBlockTriggers'],'net/minecraft/world/item/ItemStack':['consume'],'net/minecraft/world/entity/ai/goal/PanicGoal':['<init>','canUse','shouldPanic'],'net/minecraft/advancements/critereon/SimpleCriterionTrigger':['trigger'],'net/minecraft/world/level/storage/loot/functions/SetContainerContents':['run'],'net/minecraft/world/level/storage/loot/ContainerComponentManipulator':['setContents'],'net/minecraft/world/level/storage/loot/ContainerComponentManipulators$2':['setContents','type'],'net/minecraft/world/item/component/BundleContents$Mutable':['tryInsert','getMaxAmountToAdd','toImmutable'],'net/minecraft/world/item/component/BundleContents':['getWeight'],'net/minecraft/world/level/block/BasePressurePlateBlock':['getEntityCount'],'net/minecraft/world/level/block/TripWireBlock':['checkPressed'],'net/minecraft/server/network/ServerGamePacketListenerImpl':['handleInteract'],'net/minecraft/server/network/ServerGamePacketListenerImpl$1':['performInteraction','onInteraction'],'net/minecraft/world/entity/player/Player':['interactOn'],'net/minecraft/world/entity/animal/Sheep':['createAttributes'],'net/minecraft/world/level/storage/loot/LootTable':['getRandomItems'],'net/minecraft/world/item/Item':['<init>','getDefaultMaxStackSize','canFitInsideContainerItems']}
    names=MojangNames()
    with zipfile.ZipFile(CLIENT) as jar:
        names.jar=jar
        for c,ms in raw.items():
            cl=ClassFile(jar.read(names.named[c]+'.class'));av={names.member(cl.name,m['name'],m['descriptor']) for m in cl.methods};raw[c]=sorted({m for m in av if m in ms or any(m.startswith('lambda$'+n+'$') for n in ms)})
            assert raw[c],c
    loader={c+'.class':list(ms) for c,ms in raw.items()};template=read_json(OUT/'reference-specifications/vv-loader-244.json');a=next(a for a in template['archives'] if a['path'].endswith('client.jar'))
    with zipfile.ZipFile(a['path']) as jar:
        for c in loader:
            if c not in jar.namelist():continue
            av={m['name'] for m in ClassFile(jar.read(c)).methods};wanted=raw[c[:-6]]
            loader[c]=sorted({m for m in av if m in wanted or any(m.startswith('lambda$'+n+'$') for n in wanted if not n.startswith('lambda$'))})
    hooks={'net/neoforged/neoforge/common/CommonHooks.class':['onInteractEntityAt','onLivingFall'],'net/neoforged/neoforge/event/EventHooks.class':['onLivingHeal','finalizeMobSpawn']}
    print('references',references(BATCH,raw,loader,hooks),flush=True)
    write_json(OUT/'twilightforest-passive-entities-caller-scan.json',scan_callers(target))
if __name__=='__main__':collect()
