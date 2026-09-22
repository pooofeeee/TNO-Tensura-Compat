"""Native structural utility admission/order/resource guards."""
from catalog_common import *

def validate_structural(d,s,old,new,methods,ins,pos,target):
    from collect_twilight_structural_utilities import scan_callers
    assert read_json(OUT/'twilightforest-structural-utilities-caller-scan.json')==scan_callers(target)
    R='block/RopeBlock';I='item/RopeItem';B='item/MagicBeansItem';G='block/entity/GrowingBeanstalkBlockEntity';U='block/UberousSoilBlock';C='block/SpecialMagicLogBlock';T='block/TimeLogCoreBlock';X='block/TransLogCoreBlock';S='block/SortLogCoreBlock';K='util/BlockCapabilityDirectionalCache'
    extend=ins(I,'updatePlacementContext');assert pos(extend,'.getForward(')<pos(extend,'Direction.UP')<pos(extend,'Direction.DOWN')<pos(extend,'.isInWorldBounds(')<pos(extend,'.stateHasValue(')<pos(extend,'.isHorizontal(')
    assert any(x['operand']==7 for x in extend)
    placement=ins(I,'getPlacementState');assert pos(placement,'RopeBlock.X')<pos(placement,'.setValue(')<pos(placement,'BlockItem.getPlacementState(')
    assert not any('.canPlace(' in str(x['operand']) for x in placement)
    connection=ins(R,'canConnectTo');assert pos(connection,'Direction.DOWN')<pos(connection,'LeavesBlock')<pos(connection,'.hasAxis(')<pos(connection,'SupportType.CENTER')
    collision=ins(R,'getCollisionShape');assert pos(collision,'.isAbove(')<pos(collision,'.isDescending(') and not any('RopeBlock.Y' in str(x['operand']) for x in collision)
    assert len(ins(R,'isScaffolding'))==2 and int(ins(R,'isScaffolding')[0]['opcode'],16)==4
    support=ins(R,'tick');assert sum('.checkConnection(' in str(x['operand']) for x in support)==5 and pos(support,'.destroyBlock(')<pos(support,'.setBlockAndUpdate(')<pos(support,'.dropResources(')
    beans=ins(B,'useOn');assert pos(beans,'UBEROUS_SOIL')<pos(beans,'.isAir(')<pos(beans,'.isClientSide(')<pos(beans,'.shrink(')<pos(beans,'BEANSTALK_GROWER')<pos(beans,'.setBlockAndUpdate(')<pos(beans,'.getAllAdvancements(')<pos(beans,'.contains(')<pos(beans,'.award(')
    assert not any('.isCreative(' in str(x['operand']) or '.hasInfiniteMaterials(' in str(x['operand']) for x in beans)
    grow=ins(G,'tick');assert any(x['operand']==100 for x in grow) and any(x['operand']==175 for x in grow) and pos(grow,'.isClientSide(')<pos(grow,'.tryToPlaceStalk(')<pos(grow,'.placeLeaves(')<pos(grow,'.removeBlockEntity(')
    assert not any('.setChanged(' in str(x['operand']) or '.hurt(' in str(x['operand']) or '.canEntityGrief(' in str(x['operand']) for x in grow)
    place=ins(G,'tryToPlaceStalk');assert pos(place,'.canBeReplaced(')<pos(place,'BEANSTALK_GROWER')<pos(place,'BlockTags.LEAVES')<pos(place,'FLUFFY_CLOUD')<pos(place,'.setBlockAndUpdate(')<pos(place,'.blocksSkipped')
    assert any(x['operand']==15 for x in place) and any(x['operand']==150 for x in place) and any(x['operand']==7 for x in place)
    for m in ['saveAdditional','loadAdditional']:
        assert {x['operand'] for x in ins(G,m) if isinstance(x['operand'],str)} >= {'ticker','layer','isAreaClearEnough','nextLeafY','beardifierGroundDelta','cScale','rScale','maxY','blocksSkipped'}
    soil=ins(U,'neighborChanged');assert pos(soil,'BonemealableBlock')<pos(soil,'BlockTags.CROPS')<pos(soil,'MushgloomBlock')<pos(soil,'.pushEntitiesUp(')<pos(soil,'.growMushroom(')<pos(soil,'FakePlayerFactory.getMinecraft(')<pos(soil,'TickTask')
    lambdas=[m['instructions'] for m in methods(U) if m['name'].startswith('lambda$neighborChanged')];assert len(lambdas)==2
    for code in lambdas:assert any(x['operand']==15 for x in code) and pos(code,'Items.BONE_MEAL')<pos(code,'BoneMealItem.applyBonemeal(')
    assert int(ins('block/MushgloomBlock','isValidBonemealTarget')[0]['opcode'],16)==3
    core=ins(C,'tick');assert pos(core,'ACTIVE')<pos(core,'.doesCoreFunction(')<pos(core,'.performTreeEffect(')<pos(core,'.scheduleTick(')
    time=ins(T,'performTreeEffect');assert any(x['operand']==24 for x in time) and pos(time,'.tickRate(')<pos(time,'.randomOffset(')<pos(time,'TIME_CORE_EXCLUDED')<pos(time,'.isRandomlyTicking(')<pos(time,'.randomTick(')<pos(time,'.getBlockEntity(')<pos(time,'.getTicker(')<pos(time,'BlockEntityTicker.tick(')
    assert not any('.setDayTime(' in str(x['operand']) or '.scheduleTick(' in str(x['operand']) for x in time)
    trans=ins(X,'performTreeEffect');assert any(x['operand']==256.0 for x in trans) and any(x['operand']==16 for x in trans)
    assert pos(trans,'.distSqr(')<pos(trans,'.getMinBuildHeight(')<pos(trans,'.getSections(')<pos(trans,'.getMinSection(')<pos(trans,'PalettedContainer')<pos(trans,'.setUnsaved(')<pos(trans,'.resendBiomesForChunks(')
    sorting=ins(S,'performTreeEffect');extracts=[i for i,x in enumerate(sorting) if 'IItemHandler.extractItem(' in str(x['operand'])];inserts=[i for i,x in enumerate(sorting) if 'IItemHandler.insertItem(' in str(x['operand'])]
    assert len(extracts)==2 and len(inserts)==2 and extracts[0]<extracts[1]<inserts[0]<inserts[1]
    assert int(sorting[extracts[0]-1]['opcode'],16)==4 and int(sorting[extracts[1]-1]['opcode'],16)==3
    assert int(sorting[inserts[0]-1]['opcode'],16)==4 and int(sorting[inserts[1]-1]['opcode'],16)==3 and int(sorting[inserts[1]+1]['opcode'],16)==0x57
    assert not any('ItemHandlerHelper' in str(x['operand']) for x in sorting)
    key=next(m for m in methods(K+'$BlockPosAndDirection') if m['name']=='<init>');assert key['descriptor']=='(Lnet/minecraft/core/BlockPos;Lnet/minecraft/core/Direction;)V'
    cache=ins(K,'get');assert pos(cache,'Map.get(')<pos(cache,'BlockCapabilityCache.create(')<pos(cache,'Map.put(')<pos(cache,'.getCapability(')
    assert not any('.clear(' in str(x['operand']) for m in methods(K) for x in m['instructions'])
    refs=[w for p in (OUT/'reference-evidence').glob('*.json') for w in read_json(p).get('witnesses',[]) if w.get('archive_sha256') in ['8e3563a078289f0f07ee6f87f1c8651294387639c8355983ee207cb753f08b7f','d874b2aa4d511919a567ae73f13510e63e16f7318194eb2c03824cd68a59df6f']]
    def ri(c,n):return next(m['instructions'] for w in refs if w['entry']==c+'.class' for m in w.get('methods',[]) if m['name']==n)
    mode=ri('net/minecraft/server/level/ServerPlayerGameMode','useItemOn');assert pos(mode,'.isCreative(')<pos(mode,'ItemStack.getCount(')<pos(mode,'ItemStack.useOn(')<pos(mode,'ItemStack.setCount(')
    assert sum('ITEM_USED_ON_BLOCK' in str(x['operand']) for x in mode)==2
    nativecache=ri('net/neoforged/neoforge/capabilities/BlockCapabilityCache','getCapability');assert pos(nativecache,'.level')<pos(nativecache,'.isLoaded(')<pos(nativecache,'ServerLevel.getCapability(')
    bone=ri('net/minecraft/world/item/BoneMealItem','applyBonemeal');assert pos(bone,'.fireBonemealEvent(')<pos(bone,'.isCanceled(')<pos(bone,'.isValidBonemealTarget(')<pos(bone,'.performBonemeal(')
    mushroom=ri('net/minecraft/world/level/block/MushroomBlock','growMushroom');assert pos(mushroom,'.fireBlockGrowFeature(')<pos(mushroom,'.isCanceled(')<pos(mushroom,'.removeBlock(')<pos(mushroom,'.place(')<pos(mushroom,'.setBlock(')
    climb=ri('net/minecraft/world/entity/LivingEntity','handleOnClimbable');assert pos(climb,'.resetFallDistance(')<pos(climb,'.isScaffolding(')<pos(climb,'.isSuppressingSlidingDownLadder(')
    cfg=read_json(OUT/'config-evidence/twilightforest-common.json');assert sha256(cfg['path'])==cfg['sha256']
    for k in ['timeCoreRange','transformationCoreRange','sortingCoreRange']:assert cfg['values']['Magic Trees'][k]==16
    assert old.get('semantic_corrections')==new.get('semantic_corrections') and len(new['semantic_corrections'])==2
    assert not s['damage_profiles'] and d['damage_census']['reviewed_profiles_after']==31 and d['damage_census']['remaining_profiles']==9
