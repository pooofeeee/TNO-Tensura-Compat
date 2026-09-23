"""Remaining combat callbacks and source census; no runtime or production writes."""
from twilight_evidence import *
from selected_reference import collect as reference_collect
from vanilla_reference import CLIENT
from structure_nbt import decode
import zlib

BATCH='twilight-combat-closure'
FULL=['block/HedgeBlock','block/ArcticFurBlock','block/MazeSlimeBlock','block/SinisterSpawnerBlock',
 'block/entity/spawner/SinisterSpawnerLogic','block/entity/spawner/SinisterSpawnerBlockEntity','block/entity/spawner/SinisterSpawnerBlockEntity$1',
 'block/ChiseledCanopyShelfBlock','block/entity/bookshelf/BookshelfSpawner','block/entity/bookshelf/ChiseledCanopyShelfBlockEntity','block/entity/bookshelf/ChiseledCanopyShelfBlockEntity$1',
 'events/MiscEvents','events/EntityEvents','events/EntityEvents$ExtendedEndermanTakeBlockGoal','entity/RovingCube','entity/ai/goal/CubeMoveToRedstoneSymbolsGoal','entity/ai/goal/CubeCenterOnSymbolGoal',
 'entity/boss/PlateauBoss','block/entity/spawner/FinalBossSpawnerBlockEntity','asmhooks/MultipartHooks','asmhooks/WorldgenHooks','util/multiparts/MultipartEntityUtil','util/multiparts/MultipartEntityIteratorWrapper',
 'network/UpdateTFMultipartPacket','network/UpdateTFMultipartPacket$PartDataHolder','compat/CosmeticArmorCompat']


def census(target):
    """Pin producer references, not an absence proof inferred from a class name."""
    needles=['HEDGE','ARCTIC_FUR_BLOCK','MAZE_SLIME_BLOCK','SINISTER_SPAWNER','CHISELED_CANOPY_BOOKSHELF','BookshelfSpawner','ROVING_CUBE','PLATEAU_BOSS','CosmeticArmorCompat','getPotentialSpawns','gatherPotentialSpawns']
    hits=[];templates=[]
    with zipfile.ZipFile(target['path']) as jar:
        for entry in jar.namelist():
            b=jar.read(entry)
            if entry.endswith('.class'):
                if not any(n.encode() in b for n in needles):continue
                cl=ClassFile(b)
                for m in cl.methods:
                    ii=list(cl.instructions(m.get('code',b'')))
                    operands=[i for i in ii if any(n in str(i['operand']) for n in needles)]
                    if operands:hits.append(dict(entry=entry,sha256=byte_hash(b),method=m['name'],descriptor=m['descriptor'],references=operands))
            elif entry.endswith('.nbt'):
                raw=zlib.decompress(b,31) if b.startswith(b'\x1f\x8b') else b
                if not any(n in raw for n in [b'sinister_spawner',b'chiseled_canopy_shelf',b'lectern',b'spawner',b'twilightforest:hedge',b'twilightforest:arctic_fur_block']):continue
                d=decode(raw);pal=d.get('palette',d.get('palettes',[None])[0]);selected=[]
                if pal is None:continue
                for block in d.get('blocks',[]):
                    state=pal[block['state']];nbt=block.get('nbt',{})
                    if state['Name']=='minecraft:structure_block' or state['Name'] in ['twilightforest:hedge','twilightforest:arctic_fur_block','twilightforest:sinister_spawner','twilightforest:chiseled_canopy_bookshelf']:
                        selected.append(dict(pos=block['pos'],state=state,nbt=nbt))
                templates.append(dict(entry=entry,sha256=byte_hash(b),decoded_sha256=byte_hash(raw),selected_blocks=selected))
    return dict(scope='All outer installed classes and native NBT resources, exact producer symbols and structured marker states. Data generators/renderers retained as provenance, not promoted as runtime delivery.',jar_sha256=target['sha256'],needles=needles,caller_hits=hits,templates=templates)


def collect():
    target=next(t for t in read_json(OUT/'jar-inventory.json')['targets'] if t['key']=='twilightforest')
    classes={c:['*'] for c in FULL}
    classes.update({'util/entities/EntityUtil':['rayTrace'],'init/TFBlocks':['<clinit>'],'init/TFBlockEntities':['<clinit>'],'init/TFEntities':['<clinit>'],
      'asmhooks/ItemHooks':['modifyWrittenBookName'],'asmhooks/BlockHooks':['resolveFoliageColor'],
      'entity/TFPart':['writeData','readData'],'events/RegistrationEvents':['setupPackets'],
      'world/components/structures/lichtowerrevamp/LichTowerWingRoom':['handleDataMarker','handleDataParams','putSpawner','putSinisterSpawner','configureBaseSpawner','pickRandomMob','defaultRandomMob','randomMobFromParams','putTrappableBookshelf','putTrappableLectern'],
      'world/components/structures/type/HollowHillStructure':['canSpawnMob'],
      'world/components/structures/util/ControlledSpawns':['*'],'world/components/structures/util/ControlledSpawns$ControlledSpawningConfig':['*'],
      'world/components/structures/start/TFStructureStart':['*'],'world/components/structures/util/CustomStructureData':['*'],'world/components/structures/util/ConfigurableSpawns':['*'],'TwilightForestMod':['<init>','loadCuriosCompat']})
    with zipfile.ZipFile(target['path']) as jar:
        for c,ms in list(classes.items()):
            av={m['name'] for m in ClassFile(jar.read('twilightforest/'+c+'.class')).methods}
            if ms==['*']:continue
            assert set(ms)<=av,(c,set(ms)-av,av)
            classes[c]=sorted(set(ms)|{m for m in av if any(m.startswith('lambda$'+('static' if n=='<clinit>' else n)+'$') for n in ms)})
    res=read_json(WORK/'twilightforest/resources.json')
    selected=[p for p,v in res.items() if p.startswith('data/') and any(n in p+' '+str(v.get('data','')) for n in ['sinister_spawner','chiseled_canopy_bookshelf','arctic_fur_block','maze_slime_block','twilightforest:hedge'])]
    print('native',native(BATCH,classes,selected),flush=True)
    spec=dict(id=BATCH+'-asm',scope='Final ten registered nested transformers, including multipart data synchronization and explicit noncombat dispositions.',archives=[dict(path=str(WORK/'twilightforest/nested-tf-asm.jar'),sha256='1324a81e5cf085d62385f85e4b06e6217bf977977f92c58034af315c5d975690',classes=ASM,resources=[])])
    with zipfile.ZipFile(target['path']) as jar:assert Path(spec['archives'][0]['path']).read_bytes()==jar.read('META-INF/jarjar/s.tf-asm-4.8.3345.jar')
    write_json(OUT/'reference-specifications'/f'{BATCH}-asm.json',spec);write_json(OUT/'reference-evidence'/f'{BATCH}-asm.json',reference_collect(spec,True))
    raw=RAW
    loader={c+'.class':ms for c,ms in raw.items()}
    a=next(a for a in read_json(OUT/'reference-specifications/vv-loader-244.json')['archives'] if a['path'].endswith('client.jar'))
    with zipfile.ZipFile(a['path']) as jar:
        for c,ms in list(loader.items()):
            if c in jar.namelist():
                av={m['name'] for m in ClassFile(jar.read(c)).methods}
                loader[c]=sorted(av if c.endswith('EndermanTakeBlockGoal.class') else set(ms)&av|{m for m in av if any(m.startswith('lambda$'+n+'$') for n in ms)})
    hooks={'net/neoforged/neoforge/event/EventHooks.class':['getPotentialSpawns','checkSpawnPositionSpawner','finalizeMobSpawnSpawner','canEntityGrief']}
    print('references',references(BATCH,raw,loader,hooks),flush=True)
    write_json(OUT/'twilightforest-combat-closure-producer-census.json',census(target))


RAW={'net/minecraft/world/level/BaseSpawner': ['<init>',
                                           'delay',
                                           'isNearPlayer',
                                           'lambda$delay$1',
                                           'lambda$load$2',
                                           'lambda$load$3',
                                           'lambda$save$4',
                                           'lambda$serverTick$0',
                                           'load',
                                           'save',
                                           'serverTick'],
 'net/minecraft/world/level/block/entity/trialspawner/PlayerDetector': ['<clinit>',
                                                                        'detect',
                                                                        'inLineOfSight',
                                                                        'lambda$static$0',
                                                                        'lambda$static$1',
                                                                        'lambda$static$2',
                                                                        'lambda$static$3',
                                                                        'lambda$static$4',
                                                                        'lambda$static$5',
                                                                        'lambda$static$6',
                                                                        'lambda$static$7'],
 'net/minecraft/world/level/SpawnData$CustomSpawnRules': ['isValidPosition'],
 'net/minecraft/world/entity/monster/EnderMan$EndermanTakeBlockGoal': ['<init>',
                                                                       'canUse',
                                                                       'tick'],
 'net/minecraft/world/level/block/CactusBlock': ['entityInside'],
 'net/minecraft/world/level/block/SlimeBlock': ['bounceUp',
                                                'fallOn',
                                                'stepOn',
                                                'updateEntityAfterFallOn'],
 'net/minecraft/world/level/NaturalSpawner': ['getRandomSpawnMobAt'],
 'net/minecraft/world/item/SpawnEggItem': ['useOn'],
 'net/minecraft/world/level/block/entity/ChiseledBookShelfBlockEntity': ['setItem',
                                                                         'updateState'],
 'net/minecraft/world/level/block/entity/trialspawner/PlayerDetector$EntitySelector$1': ['getPlayers']}
ASM={'twilightforest/asm/transformers/chunk/ChunkStatusTaskTransformer.class': ['*'],
 'twilightforest/asm/transformers/conquered/StructureStartLoadStaticTransformer.class': ['*'],
 'twilightforest/asm/transformers/multipart/SendDirtyEntityDataTransformer.class': ['*'],
 'twilightforest/asm/transformers/multipart/ResolveEntitiesForRendereringTransformer.class': ['*'],
 'twilightforest/asm/transformers/multipart/ResolveEntityRendererTransformer.class': ['*'],
 'twilightforest/asm/transformers/beardifier/BeardifierClassTransformer.class': ['*'],
 'twilightforest/asm/transformers/beardifier/InitializeCustomBeardifierFieldsDuringCreateNoiseChunkTransformer.class': ['*'],
 'twilightforest/asm/transformers/beardifier/BeardifierComputeTransformer.class': ['*'],
 'twilightforest/asm/transformers/book/ModifyWrittenBookNameTransformer.class': ['*'],
 'twilightforest/asm/transformers/foliage/FoliageColorResolverTransformer.class': ['*']}

if __name__=='__main__':collect()
