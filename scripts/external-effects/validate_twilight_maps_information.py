"""Source predicate guards for maps and an explicit installed-ASM historical correction."""
from catalog_common import *

def validate_maps(d,s,old,new,methods,ins,pos,target):
    from collect_twilight_maps_information import scan_callers,TRANSFORMERS
    scan=read_json(OUT/'twilightforest-maps-information-caller-scan.json');assert scan==scan_callers(target)
    M='item/MagicMapItem';Z='item/MazeMapItem';O='item/OreMeterItem';S='components/item/OreScannerComponent';H='asmhooks/MapHooks'
    empty=ins('item/EmptyMagicMapItem','use');assert pos(empty,'.isClientSide(')<pos(empty,'ALLOWS_MAGIC_MAP_CHARTING')<pos(empty,'.consume(')<pos(empty,'.setupNewMap(')
    mz=ins('item/EmptyMazeMapItem','use');assert pos(mz,'.setupNewMap(')<pos(mz,'.consume(') and not any('.isClientSide' in str(x['operand']) or 'ALLOWS_MAGIC' in str(x['operand']) for x in mz)
    update=ins(M,'update');assert pos(update,'.dimension(')<pos(update,'entity/player/Player')<pos(update,'.isClientSide')<pos(update,'.computeIfAbsent(')
    assert any('.isConquered(' in str(x['operand']) for m in methods(M) if m['name'].startswith('lambda$update') for x in m['instructions'])
    assert any(x['operand']==16 for x in update) and any(x['operand']==512 for x in update)
    cache=[x for x in scan['hits'] if 'MagicMapItem.CACHE' in str(x['instruction']['operand'])];assert {(x['entry'],x['method']) for x in cache}=={('twilightforest/item/MagicMapItem.class','update'),('twilightforest/item/MagicMapItem.class','<clinit>')}
    for m in methods(M):assert not any('.clear(' in str(x['operand']) or '.remove(' in str(x['operand']) for x in m['instructions'])
    for c in [M,Z]:assert len(ins(c,'onCraftedBy'))==1 and 'onCraftedPostProcess' not in {m['name'] for m in methods(c)}
    pixel=ins(Z,'update');assert pos(pixel,'Blocks.STONE')<pos(pixel,'ORE_MAP_ORE_COLOR')<pos(pixel,'Tags$Blocks.ORES') and any(x['operand']==1000 for x in pixel)
    tick=ins(Z,'inventoryTick');assert pos(tick,'.tickCarriedBy(')<pos(tick,'.yCenter')<pos(tick,'PLAYER_OFF_MAP')<pos(tick,'.locked')<pos(tick,'.update(')
    clone=ins('item/recipe/MazeMapCloningRecipe','matches');assert any('FILLED_MAZE_MAP' in str(x['operand']) for x in clone) and not any('ORE_MAP' in str(x['operand']) for x in clone)
    for c in ['MagicMapCloningRecipe','MazeMapCloningRecipe']:
        make=next(m['instructions'] for m in methods('item/recipe/'+c) if m['name']=='assemble' and 'ItemStack;' in m['descriptor']);assert pos(make,'.copy(')<pos(make,'.setCount(') and not any('.getFreeMapId(' in str(x['operand']) for x in make)
    use=ins(O,'use');assert pos(use,'.getClass(')<pos(use,'net/minecraft/server/level/ServerPlayer')<pos(use,'.isLoading(')<pos(use,'.isSecondaryUseActive(')
    begin=ins(O,'beginScanning');assert any(x['operand']==50 for x in begin) and any(x['operand']==25 for x in begin) and not any('ORE_LOADING' in str(x['operand']) for x in begin)
    on=ins(O,'useOn');assert pos(on,'.isSecondaryUseActive(')<pos(on,'ORE_METER_TARGETABLE')<pos(on,'ORE_FILTER') and not any('.isLoading(' in str(x['operand']) for x in on)
    scan_tick=ins(S,'tickScan');assert pos(scan_tick,'.getMinBuildHeight(')<pos(scan_tick,'.getMaxBuildHeight(')<pos(scan_tick,'.abs(')<pos(scan_tick,'.ceil(')<pos(scan_tick,'.getBlockState(')
    assert not any('.getHeight(' in str(x['operand']) for x in scan_tick)
    geometry=ins(S,'scanFromCenter');assert sum(int(x['opcode'],16)==0x64 for x in geometry)>=4 and sum(x['operand']==15 for x in geometry)==2
    itick=ins(O,'inventoryTick');assert pos(itick,'.tickScan(')<pos(itick,'.isEmpty(')<pos(itick,'.isFinished(')<pos(itick,'ORE_LOADING')<pos(itick,'ORE_FILTER')<pos(itick,'OreScannerData.create(')
    wipe=[x for m in methods('network/WipeOreMeterPacket') if m['name'].startswith('lambda$handle') for x in m['instructions']];assert pos(wipe,'.player(')<pos(wipe,'.getItemInHand(')<pos(wipe,'TFItems.ORE_METER')<pos(wipe,'ORE_DATA')<pos(wipe,'ORE_FILTER')
    assert not any('ORE_SCANNING' in str(x['operand']) or 'ORE_LOADING' in str(x['operand']) or 'ORE_RANGE' in str(x['operand']) for x in wipe)
    for c in [M,Z,O,S]:assert not any('.hurt(' in str(x['operand']) or '.setHealth(' in str(x['operand']) or '.addEffect(' in str(x['operand']) for m in methods(c) for x in m['instructions'])
    hook=ins(H,'resolveNearestNonRandomSpreadMapStructure');assert pos(hook,'.findNearestMapLandmark(')<pos(hook,'.orElse(') and len(hook)<12
    lookup=ins('util/WorldUtil','findNearestMapLandmark');assert pos(lookup,'LandmarkGridPlacement')<pos(lookup,'.landmarkCenterScanner(')<pos(lookup,'.isStructureChunk(')<pos(lookup,'.getBiome(')<pos(lookup,'.checkStructurePresence(')<pos(lookup,'START_PRESENT')<pos(lookup,'.distToLowCornerSqr(')
    refs=[w for p in (OUT/'reference-evidence').glob('*.json') for w in read_json(p).get('witnesses',[]) if w.get('archive_sha256') in ['8e3563a078289f0f07ee6f87f1c8651294387639c8355983ee207cb753f08b7f','d874b2aa4d511919a567ae73f13510e63e16f7318194eb2c03824cd68a59df6f']]
    def ri(c,fn):return next(m for w in refs if w['entry']==c+'.class' for m in w.get('methods',[]) if m['name']==fn)
    generator=ri('net/minecraft/world/level/chunk/ChunkGenerator','findNearestMapStructure')['instructions'];assert len([x for x in generator if int(x['opcode'],16)==0xb0])==3
    maplookup=next(m['instructions'] for w in refs if w['entry']=='net/minecraft/world/item/MapItem.class' for m in w.get('methods',[]) if m['name']=='getSavedData' and 'ItemStack' in m['descriptor']);assert any('.getCustomMapData(' in str(x['operand']) for x in maplookup)
    elytra=ri('net/minecraft/client/renderer/entity/layers/ElytraLayer','shouldRender');assert elytra['descriptor']=='(Lnet/minecraft/world/item/ItemStack;Lnet/minecraft/world/entity/LivingEntity;)Z' and any(int(x['opcode'],16)==0x2b for x in elytra['instructions']) and any('Items.ELYTRA' in str(x['operand']) for x in elytra['instructions'])
    asm=read_json(OUT/'reference-evidence/twilight-maps-information-asm.json')['witnesses'];assert {w['entry'].rsplit('/',1)[-1][:-6] for w in asm}==set(TRANSFORMERS)
    reg=read_json(OUT/'reference-evidence/twilight-equipment-asm.json')['witnesses']
    for name in TRANSFORMERS:assert any(name+'.<init>' in str(x['operand']) for w in reg for m in w.get('methods',[]) for x in m['instructions'])
    ew=next(w for w in asm if w['entry'].endswith('/CancelElytraRenderingTransformer.class'));allins=[x for m in ew['methods'] for x in m['instructions']];assert any(x['operand']==172 for x in allins) and any(x['operand']=='shouldRender' for x in allins) and any(x['operand']=='cancelArmorRendering' for x in allins)
    lw=next(w for w in asm if w['entry'].endswith('/ResolveNearestNonRandomSpreadMapStructureTransformer.class'));allins=[x for m in lw['methods'] for x in m['instructions']];assert any(x['operand']==176 for x in allins) and any('ASMUtil.findLast(' in str(x['operand']) for x in allins)
    raw=[c for p in (OUT/'vanilla-evidence').glob('*.json') for c in read_json(p).get('classes',[])]
    carto=[m for c in raw if c['class_name'].startswith('net/minecraft/world/inventory/CartographyTableMenu$') for m in c['methods'] if m['name']=='mayPlace'];assert any(any('Items.FILLED_MAP' in str(x['operand']) for x in m['instructions']) for m in carto)
    codec=[x for c in raw if c['class_name']=='net/minecraft/core/component/DataComponentType$Builder' for m in c['methods'] for x in m['instructions']];assert any('fromCodecWithRegistries' in str(x['operand']) for x in codec)
    assert len(d['semantic_corrections'])==2 and len(new['semantic_corrections'])==2
    assert 'No installed TF cloth hook changes' in old['effects'][189]['actual_behavior'][2]
    assert 'registered CancelElytraRenderingTransformer' in new['effects'][189]['actual_behavior'][2]
    assert old['paths'][611]['future_controls'][2]=='Elytralayerstillrenders' and new['paths'][611]['future_controls'][2]=='registeredElytraHookSuppressesClothedWings'
    oldids={e['id'] for e in old['effects']}
    for e in s['effects']:assert set(e.get('reuses_protected_effect_ids',[]))<=oldids
    assert not s['damage_profiles'] and d['damage_census']['reviewed_profiles_after']==31 and d['damage_census']['remaining_profiles']==9
