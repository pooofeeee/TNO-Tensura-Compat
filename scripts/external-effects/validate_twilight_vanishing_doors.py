"""Bytecode guards for distinct native barrier state machines and real key use."""
from catalog_common import *
from classfile import ClassFile

def validate_vanishing_doors(d,s,old,new,methods,ins,pos,target):
    from collect_twilight_vanishing_doors import scan_callers
    assert read_json(OUT/'twilightforest-vanishing-doors-caller-scan.json')==scan_callers(target)
    V='block/VanishingBlock';R='block/ReappearingBlock';L='block/LockedVanishingBlock';C='block/CastleDoorBlock';W='world/components/structures/darktower/DarkTowerWingComponent';M='world/components/structures/darktower/DarkTowerMainComponent'
    lock=ins(V,'areBlocksLocked');assert any(x['operand']==512 for x in lock) and pos(lock,'Deque.pop(')<pos(lock,'LOCKED_VANISHING_BLOCK')<pos(lock,'Set.add(')<pos(lock,'Set.contains(')
    assert sum('Deque.offer(' in str(x['operand']) for x in lock)==2
    active=ins(V,'activate');assert pos(active,'VanishingBlock')<pos(active,'.isVanished(')<pos(active,'.setBlockAndUpdate(')<pos(active,'.scheduleTick(')
    assert not any('areBlocksLocked' in str(x['operand']) or '.LOCKED' in str(x['operand']) for x in active)
    assert any(x['operand']==5 for x in active) and any(x['operand']==2 for x in active)
    use=ins(V,'useWithoutItem');assert pos(use,'.isVanished(')<pos(use,'.areBlocksLocked(')<pos(use,'.activate(')<pos(use,'.sidedSuccess(')
    neighbor=ins(V,'neighborChanged');assert pos(neighbor,'.isClientSide(')<pos(neighbor,'.hasNeighborSignal(')<pos(neighbor,'.areBlocksLocked(')<pos(neighbor,'.activate(')
    tick=ins(V,'tick');assert any(x['operand']==80 for x in tick) and any(x['operand']==15 for x in tick) and pos(tick,'.removeBlock(')<pos(tick,'.activate(')
    assert not any('.areBlocksLocked(' in str(x['operand']) or '.canEntityDestroy(' in str(x['operand']) or 'BreakEvent' in str(x['operand']) for x in tick)
    assert any('VANISHED' in str(x['operand']) for x in ins(R,'<init>'))
    resist=ins(V,'getExplosionResistance');assert any(x['operand']==6000.0 for x in resist)
    locked=ins(L,'getExplosionResistance');assert any(x['operand']==6000000.0 for x in locked)
    key=ins(L,'useItemOn');assert pos(key,'.isEmpty(')<pos(key,'TOWER_KEY')<pos(key,'.LOCKED')<pos(key,'.isClientSide(')<pos(key,'.shrink(')<pos(key,'.setBlockAndUpdate(')<pos(key,'.sidedSuccess(')
    assert not any(any(n in str(x['operand']) for n in ['.instabuild','.hasInfiniteMaterials(','.activate(']) for x in key)
    assert [int(x['opcode'],16) for x in ins(C,'isBlockLocked')]==[0x03,0xac]
    activate=ins(C,'onActivation');assert pos(activate,'.VANISHED')<pos(activate,'.ACTIVE')<pos(activate,'InteractionResult.FAIL')<pos(activate,'.isBlockLocked(')<pos(activate,'.changeToActiveBlock(')<pos(activate,'InteractionResult.SUCCESS')
    cneigh=ins(C,'neighborChanged');assert pos(cneigh,'CastleDoorBlock')<pos(cneigh,'.hasNeighborSignal(')<pos(cneigh,'.onActivation(') and not any('.isClientSide(' in str(x['operand']) for x in cneigh)
    change=ins(C,'changeToActiveBlock');assert any(x['operand']==2 for x in change) and any(x['operand']==5 for x in change)
    ctick=ins(C,'tick');assert any(x['operand']==80 for x in ctick) and not any(x['operand']==15 for x in ctick) and pos(ctick,'.setBlockAndUpdate(')<pos(ctick,'.checkAndActivateCastleDoor(')
    chain=ins(C,'checkAndActivateCastleDoor');assert pos(chain,'CastleDoorBlock')<pos(chain,'.isBlockLocked(')<pos(chain,'.changeToActiveBlock(') and not any('TFBlocks' in str(x['operand']) for x in chain)
    for c in [V,R,L,C]:
        assert not any(any(n in str(x['operand']) for n in ['.hurt(','.setHealth(','.addEffect(','.teleportTo(','.knockback(','.igniteFor']) for m in methods(c) for x in m['instructions'])
    for c in [V,C]:assert any('Shapes.empty(' in str(x['operand']) for x in ins(c,'getCollisionShape'))
    wing=ins(W,'addAdditionalSaveData');assert any(x['operand']=='keyTower' for x in wing)
    treasure=ins(W,'decorateTreasureRoom');assert pos(treasure,'.isKeyTower(')<pos(treasure,'DARKTOWER_KEY')<pos(treasure,'DARKTOWER_CACHE')<pos(treasure,'.placeTreasureAtCurrentPosition(')
    main=ins(M,'addChildren');assert pos(main,'.placedKeys')<pos(main,'.setKeyTower(') and any(x['operand']==9 for x in main)
    with zipfile.ZipFile(target['path']) as jar:
        cl=ClassFile(jar.read('twilightforest/'+M+'.class'));assert not any(m['name']=='addAdditionalSaveData' for m in cl.methods)
    refs=[w for p in (OUT/'reference-evidence').glob('*.json') for w in read_json(p).get('witnesses',[]) if w.get('archive_sha256')=='8e3563a078289f0f07ee6f87f1c8651294387639c8355983ee207cb753f08b7f']
    native=next(m['instructions'] for w in refs if w['entry']=='net/minecraft/server/level/ServerPlayerGameMode.class' for m in w['methods'] if m['name']=='useItemOn')
    assert pos(native,'.onRightClickBlock(')<pos(native,'BlockState.useItemOn(')<pos(native,'ItemInteractionResult.consumesAction(')<pos(native,'.isCreative(')<pos(native,'ItemStack.setCount(')
    ret=pos(native,'ItemInteractionResult.result(');assert any(int(x['opcode'],16)==0xb0 for x in native if ret<x['offset']<pos(native,'.isCreative('))
    resources=read_json(WORK/'twilightforest/resources.json');keypool=resources['data/twilightforest/loot_table/darktower_key.json']['data']['pools'][-1];assert keypool['rolls']==1 and keypool['entries']==[{'type':'minecraft:item','name':'twilightforest:tower_key'}] and not keypool.get('conditions')
    assert 'twilightforest:tower_key' in resources['data/twilightforest/tags/item/kept_on_death.json']['data']['values']
    assert old.get('semantic_corrections')==new.get('semantic_corrections') and not s['damage_profiles'] and d['damage_census']['remaining_profiles']==0
