"""Installed map information paths, locator ASM and the cloth Elytra erratum."""
from twilight_evidence import *
from vanilla_reference import MojangNames,CLIENT
from selected_reference import collect as reference_collect
BATCH='twilight-maps-information'
FULL=['item/'+c for c in ['EmptyMagicMapItem','EmptyMazeMapItem','MagicMapItem','MazeMapItem','OreMeterItem']]+['item/mapdata/'+c for c in ['TFMagicMapData','TFMagicMapData$DecorationHolder','TFMazeMapData']]+['item/recipe/'+c for c in ['MagicMapCloningRecipe','MazeMapCloningRecipe']]+['network/'+c for c in ['MagicMapPacket','MagicMapPacket$1','MazeMapPacket','MazeMapPacket$1','WipeOreMeterPacket']]+['components/item/OreScannerComponent','components/item/OreScannerData','asmhooks/MapHooks','util/landmarks/LegacyLandmarkPlacements','util/iterators/XZQuadrantIterator','world/components/structures/placements/LandmarkGridPlacement','util/datamaps/MagicMapBiomeColor','util/datamaps/OreMapOreColor','client/renderer/map/MagicMapPlayerIconRenderer','client/renderer/map/ConqueredMapIconRenderer']
TRANSFORMERS=['CancelElytraRenderingTransformer','ResolveNearestNonRandomSpreadMapStructureTransformer']
TOKENS=['MagicMapItem','MazeMapItem','MagicMapPacket','MazeMapPacket','OreMeterItem','ORE_SCANNING','ORE_DATA','ORE_FILTER','ORE_LOADING','ORE_RANGE','resolveNearestNonRandomSpreadMapStructure','biomesForMap','cancelArmorRendering']

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
    return dict(jar_sha256=target['sha256'],scope='All installed TF instruction callers of map, OreMeter and selected hook tokens. Commands/display consumers are informational; protected goggles callback reused.',needles=TOKENS,hits=hits)

def collect():
    target=next(t for t in read_json(OUT/'jar-inventory.json')['targets'] if t['key']=='twilightforest');res=read_json(WORK/'twilightforest/resources.json')
    selected=[p for p,v in res.items() if p.startswith('data/') and any(k in p+' '+str(v.get('data','')) for k in ['magic_map','maze_map','ore_map','ore_meter','landmark_grid'])]
    classes={c:['*'] for c in FULL}
    classes.update({'util/WorldUtil':['findNearestMapLandmark','getOverworldSeed'],'util/landmarks/LandmarkUtil':['isConquered','locateNearestMatchingLandmark'],'events/EntityEvents':['setup','wipeOreMeterOnLeftClick'],'client/event/OverlayHandler':['registerOverlays','renderOreMeterStats','initTooltips'],'init/TFDataComponents':['*'],'init/TFMapDecorations':['*']})
    with zipfile.ZipFile(target['path']) as jar:
        for c,wanted in list(classes.items()):
            if wanted==['*']:continue
            available={m['name'] for m in ClassFile(jar.read('twilightforest/'+c+'.class')).methods}
            assert set(wanted)<=available,(c,set(wanted)-available)
            classes[c]=sorted(set(wanted)|{m for m in available if any(m.startswith('lambda$'+n+'$') for n in wanted)})
        for c,needles in [('init/TFRecipes',['MapCloning']),('init/TFItems',['MagicMapItem','MazeMapItem','OreMeterItem']),('events/RegistrationEvents',['MagicMapPacket','MazeMapPacket','WipeOreMeterPacket']),('client/event/ClientRegistrationEvents',['MagicMapPlayerIconRenderer','ConqueredMapIconRenderer','OreMeterItem','renderOreMeterStats'])]:
            cls=ClassFile(jar.read('twilightforest/'+c+'.class'));classes[c]=[m['name'] for m in cls.methods if m['name']=='<clinit>' or any(any(n in str(i['operand']) for n in needles) for i in cls.instructions(m.get('code',b'')))]
    print('native',native(BATCH,classes,selected),flush=True)
    raw={'net/minecraft/server/level/ServerLevel':['findNearestMapStructure'],'net/minecraft/world/level/storage/loot/functions/ExplorationMapFunction':['run'],'net/minecraft/world/entity/npc/VillagerTrades$TreasureMapForEmeralds':['getOffer'],'net/minecraft/server/commands/LocateCommand':['locateStructure'],'net/minecraft/world/item/MapItem':['*'],'net/minecraft/world/level/saveddata/maps/MapItemSavedData':['createFresh','load','save','tickCarriedBy','getUpdatePacket','addDecoration','toggleBanner'],'net/minecraft/world/level/chunk/ChunkGenerator':['findNearestMapStructure'],'net/minecraft/world/level/levelgen/structure/placement/StructurePlacement':['isStructureChunk'],'net/minecraft/core/component/DataComponentType$Builder':['build'],'net/minecraft/world/inventory/CartographyTableMenu':['*']}
    raw.update({'net/minecraft/world/inventory/CartographyTableMenu$'+str(i):['*'] for i in range(1,6)})
    names=MojangNames()
    with zipfile.ZipFile(CLIENT) as jar:
        names.jar=jar
        for c,ms in raw.items():
            cls=ClassFile(jar.read(names.named[c]+'.class'));available={names.member(cls.name,m['name'],m['descriptor']) for m in cls.methods}
            raw[c]=sorted(available if ms==['*'] else {m for m in available if m in ms or any(m.startswith('lambda$'+n+'$') for n in ms)})
            assert raw[c],(c,ms)
    loader={c+'.class':list(ms) for c,ms in raw.items()};template=read_json(OUT/'reference-specifications/vv-loader-244.json');a=next(a for a in template['archives'] if a['path'].endswith('client.jar'))
    with zipfile.ZipFile(a['path']) as jar:
        for c in loader:
            if c not in jar.namelist():continue
            available={m['name'] for m in ClassFile(jar.read(c)).methods};wanted=raw[c[:-6]]+(['getCustomMapData'] if c.endswith('/MapItem.class') else [])
            loader[c]=sorted({m for m in available if m in wanted or any(m.startswith('lambda$'+n+'$') for n in wanted if not n.startswith('lambda$'))})
    print('references',references(BATCH,raw,loader,{}),flush=True)
    nested=WORK/'twilightforest/nested-tf-asm.jar'
    with zipfile.ZipFile(nested) as jar:asmclasses={n:['*'] for n in jar.namelist() if n.endswith('.class') and n.rsplit('/',1)[-1][:-6] in TRANSFORMERS}
    assert len(asmclasses)==2
    spec=dict(id=BATCH+'-asm',scope='Registered final-return map locator plus exact Elytra shouldRender IRETURN component hook; corrects prior pretransform-only conclusion.',archives=[dict(path=str(nested),sha256=sha256(nested),classes=asmclasses,resources=[])])
    write_json(OUT/'reference-specifications'/f'{BATCH}-asm.json',spec);write_json(OUT/'reference-evidence'/f'{BATCH}-asm.json',reference_collect(spec,source_aids=True))
    write_json(OUT/'twilightforest-maps-information-caller-scan.json',scan_callers(target))

if __name__=='__main__':collect()
