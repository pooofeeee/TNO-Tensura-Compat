"""Pinned Wrought Iron Fence, native leash controls and actual bound-zombie producers."""
from twilight_evidence import *
from selected_reference import collect as reference_collect
from vanilla_reference import prepare, CLIENT
from structure_nbt import decode
import zlib


def scan_attachment(target):
    matches=[];resource_hits=[];needles=['LEASH_PATHFINDER_OVERRIDE','leashed_pathfinder_override']
    with zipfile.ZipFile(target['path']) as jar:
        for entry in jar.namelist():
            b=jar.read(entry)
            if entry.endswith('.class'):
                if not any(n.encode() in b for n in needles):continue
                c=ClassFile(b)
                for m in c.methods:
                    ii=list(c.instructions(m.get('code',b'')))
                    if any(any(n in str(i['operand']) for n in needles) for i in ii):
                        matches.append(dict(entry=entry,sha256=byte_hash(b),method=m['name'],descriptor=m['descriptor'],instructions=ii))
            else:
                if b.startswith(b'\x1f\x8b'):b=zlib.decompress(b,31)
                if any(n.encode() in b for n in needles):resource_hits.append(entry)
    return dict(scope='All installed outer TF classes and resources (gzip decoded), exact attachment symbols. Nested registered transformer reviewed separately; no pack-wide absence claim.',jar_sha256=target['sha256'],needles=needles,matches=matches,resource_hits=resource_hits)


def templates(target):
    records=[]
    with zipfile.ZipFile(target['path']) as jar:
        for entry in jar.namelist():
            if not entry.endswith('.nbt'):continue
            b=jar.read(entry);raw=zlib.decompress(b,31) if b.startswith(b'\x1f\x8b') else b
            if 'outer_fence_' not in entry and b'zombie_trap' not in raw:continue
            d=decode(raw);pal=d.get('palette',d.get('palettes',[None])[0]);markers=[];posts=[]
            assert pal is not None and all(isinstance(x,dict) for x in pal)
            for block in d['blocks']:
                assert 0<=block['state']<len(pal)
                state=pal[block['state']];nbt=block.get('nbt',{})
                if state['Name']=='minecraft:structure_block':markers.append(dict(pos=block['pos'],state=state,metadata=nbt.get('metadata'),mode=nbt.get('mode')))
                if state['Name']=='twilightforest:wrought_iron_fence':posts.append(dict(pos=block['pos'],state=state))
            records.append(dict(entry=entry,sha256=byte_hash(b),decoded_sha256=byte_hash(raw),size=d['size'],root_keys=sorted(d),markers=markers,fence_posts=posts))
    return dict(scope='Whole native NBT resource search for zombie_trap plus outer-fence templates, structurally decoded marker/palette states. No world execution.',jar_sha256=target['sha256'],records=records)


def collect():
    target=next(t for t in read_json(OUT/'jar-inventory.json')['targets'] if t['key']=='twilightforest')
    res=read_json(WORK/'twilightforest/resources.json');scan=scan_attachment(target);decoded=templates(target)
    selected=[p for p,v in res.items() if p.startswith('data/') and any(k in p+' '+str(v.get('data','')) for k in ['wrought_iron_fence','zombie_trap','lich_tower/9x9/holding','lich_tower/9x9/lockup'])]
    P='world/components/structures/lichtowerrevamp/'
    classes={c:['*'] for c in FULL}
    classes.update({'asmhooks/BlockHooks':['leashFenceKnotSurvives'],'asmhooks/EntityHooks':['overrideStayCloseToHolder'],
      'events/EntityEvents':['setup','attachLeadToWroughtFence','handleLeashPathingOverrides'],
      'init/TFDataAttachments':['<clinit>'],'init/TFBlocks':['<clinit>'],'init/TFItems':['<clinit>'],
      'init/TFStructureTypes':['<clinit>'],'init/TFStructures':['<clinit>','bootstrap'],
      P+'LichTowerWingRoom':['<init>','postProcess','handleDataMarker','handleDataParams','putZombieTrap','getRandomDirectionInsideChunk'],
      P+'LichPerimeterFence':['<init>','addAdditionalSaveData','generateFence','startPerimeterFence','generatePerimeter','generateSidedPerimeter','generateUntilNearDest','nextFence','postProcess','generateBoundZombie'],
      P+'LichYardBox':['beginYard','generateFence'],P+'LichTowerUtil':['<clinit>','rollRandomRoom'],
      P+'LichTowerWingBridge':['tryRoomAndBridge','tryGenerateRoom','tryPlaceRoom'],
      'world/components/structures/type/LichTowerStructure':['<clinit>','getFirstPiece','generateFromStartingPiece','type','buildLichTowerConfig'],
      'world/components/structures/util/StructureTemplateDefinitions':['apply','registerListener','getRandomEntry','getRandomTemplate','forLocation'],
      'world/components/structures/TwilightTemplateStructurePiece':['postProcess','customPostProcess'],
      'world/components/structures/TwilightJigsawPiece':['postProcess','addJigsaws'],
      'util/entities/EntityUtil':['createEntityIgnoreException']})
    with zipfile.ZipFile(target['path']) as jar:
        for c,ms in list(classes.items()):
            if ms==['*']:continue
            available={m['name'] for m in ClassFile(jar.read('twilightforest/'+c+'.class')).methods}
            assert set(ms)<=available,(c,set(ms)-available)
            classes[c]=sorted(set(ms)|{m for m in available if any(m.startswith('lambda$'+n+'$') for n in ms)})
    print('native',native(BATCH,classes,selected),flush=True)
    nested=WORK/'twilightforest/nested-tf-asm.jar'
    with zipfile.ZipFile(target['path']) as jar:assert nested.read_bytes()==jar.read('META-INF/jarjar/s.tf-asm-4.8.3345.jar')
    spec=dict(id=BATCH+'-asm',scope='Exact registered native leash-knot survival and base Pathfinder close-follow transformers.',archives=[dict(path=str(nested),sha256=sha256(nested),classes={c:['*'] for c in ASM},resources=[])])
    write_json(OUT/('reference-specifications/'+BATCH+'-asm.json'),spec)
    write_json(OUT/('reference-evidence/'+BATCH+'-asm.json'),reference_collect(spec,True))
    loader={c+'.class':list(ms) for c,ms in RAW.items()}
    template=read_json(OUT/'reference-specifications/vv-loader-244.json');a=next(a for a in template['archives'] if a['path'].endswith('client.jar'))
    with zipfile.ZipFile(a['path']) as jar:
        for c in loader:
            if c not in jar.namelist():continue
            available={m['name'] for m in ClassFile(jar.read(c)).methods}
            loader[c]=sorted(m for m in available if m in RAW[c[:-6]] or any(m.startswith('lambda$'+n+'$') for n in RAW[c[:-6]] if not n.startswith('lambda$')))
    print('references',references(BATCH,RAW,loader,{'net/neoforged/neoforge/common/CommonHooks.class':['onInteractEntity']}),flush=True)
    vp=OUT/('vanilla-specifications/'+BATCH+'.json');vs=read_json(vp)
    with zipfile.ZipFile(CLIENT) as jar:
        vs['resources']=[p for p in jar.namelist() if p.startswith('data/minecraft/tags/block/') and any(p.endswith('/'+n+'.json') for n in ['fences','wooden_fences','walls'])]
    write_json(vp,vs);write_json(OUT/('vanilla-evidence/'+BATCH+'.json'),prepare(vs))
    write_json(OUT/'twilightforest-fence-leash-attachment-census.json',scan)
    write_json(OUT/'twilightforest-fence-leash-structure-templates.json',decoded)



BATCH='twilight-fence-leash'
FULL=['block/WroughtIronFenceBlock','block/WroughtIronFenceBlock$FenceSide','block/WroughtIronFenceBlock$PostState','block/WroughtIronFenceBlock$1','item/WroughtIronFenceItem']
ASM=['twilightforest/asm/transformers/entity/PathFinderUnrestrainedByLeashTransformer.class','twilightforest/asm/transformers/lead/LeashFenceKnotSurvivesTransformer.class']
RAW={'net/minecraft/world/entity/Leashable': ['canBeLeashed',
                                          'canHaveALeashAttachedToIt',
                                          'closeRangeLeashBehaviour',
                                          'dropLeash',
                                          'elasticRangeLeashBehaviour',
                                          'getLeashData',
                                          'getLeashHolder',
                                          'handleLeashAtDistance',
                                          'isLeashed',
                                          'lambda$writeLeashData$0',
                                          'leashTooFarBehaviour',
                                          'legacyElasticRangeLeashBehaviour',
                                          'mayBeLeashed',
                                          'readLeashData',
                                          'restoreLeashFromSave',
                                          'setDelayedLeashHolderId',
                                          'setLeashData',
                                          'setLeashedTo',
                                          'tickLeash',
                                          'writeLeashData'],
 'net/minecraft/world/entity/Leashable$LeashData': ['<init>', 'setLeashHolder'],
 'net/minecraft/world/entity/PathfinderMob': ['<init>',
                                              'checkSpawnRules',
                                              'closeRangeLeashBehaviour',
                                              'followLeashSpeed',
                                              'getWalkTargetValue',
                                              'handleLeashAtDistance',
                                              'isPanicking',
                                              'isPathFinding',
                                              'shouldStayCloseToLeashHolder'],
 'net/minecraft/world/entity/decoration/LeashFenceKnotEntity': ['<init>',
                                                                'addAdditionalSaveData',
                                                                'defineSynchedData',
                                                                'dropItem',
                                                                'getAddEntityPacket',
                                                                'getOrCreateKnot',
                                                                'getPickResult',
                                                                'getRopeHoldPosition',
                                                                'interact',
                                                                'lambda$interact$0',
                                                                'playPlacementSound',
                                                                'readAdditionalSaveData',
                                                                'recalculateBoundingBox',
                                                                'shouldRenderAtSqrDistance',
                                                                'survives'],
 'net/minecraft/world/item/LeadItem': ['<init>',
                                       'bindPlayerMobs',
                                       'lambda$bindPlayerMobs$0',
                                       'lambda$leashableInArea$1',
                                       'leashableInArea',
                                       'useOn'],
 'net/minecraft/world/entity/Mob': ['addAdditionalSaveData',
                                    'canBeLeashed',
                                    'checkAndHandleImportantInteractions',
                                    'dropLeash',
                                    'getLeashData',
                                    'interact',
                                    'lambda$checkAndHandleImportantInteractions$1',
                                    'leashTooFarBehaviour',
                                    'mobInteract',
                                    'readAdditionalSaveData',
                                    'setLeashData'],
 'net/minecraft/world/entity/decoration/BlockAttachedEntity': ['<clinit>',
                                                               '<init>',
                                                               'addAdditionalSaveData',
                                                               'dropItem',
                                                               'getPos',
                                                               'hurt',
                                                               'isPickable',
                                                               'move',
                                                               'push',
                                                               'readAdditionalSaveData',
                                                               'recalculateBoundingBox',
                                                               'refreshDimensions',
                                                               'repositionEntityAfterLoad',
                                                               'setPos',
                                                               'skipAttackInteraction',
                                                               'survives',
                                                               'thunderHit',
                                                               'tick'],
 'net/minecraft/world/entity/Entity': ['baseTick', 'interact', 'load', 'save', 'saveWithoutId'],
 'net/minecraft/world/entity/EntityType': ['<clinit>'],
 'net/minecraft/world/entity/player/Player': ['interactOn'],
 'net/minecraft/server/level/WorldGenRegion': ['addFreshEntity'],
 'net/minecraft/world/level/chunk/ProtoChunk': ['addEntity'],
 'net/minecraft/world/level/chunk/LevelChunk': ['addEntity'],
 'net/minecraft/world/level/levelgen/structure/templatesystem/StructureTemplate': ['filterBlocks'],
 'net/minecraft/world/level/block/state/BlockBehaviour': ['getCollisionShape']}

if __name__=='__main__':collect()
