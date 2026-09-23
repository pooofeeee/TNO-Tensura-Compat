"""Source guards for remaining combat admissions, not runtime compatibility claims."""
from catalog_common import *


def validate_combat_closure(d,s,old,new,methods,ins,pos,target):
    from collect_twilight_combat_closure import census,ASM
    assert read_json(OUT/'twilightforest-combat-closure-producer-census.json')==census(target)
    H='block/HedgeBlock';S='block/entity/spawner/SinisterSpawnerLogic';B='block/entity/bookshelf/BookshelfSpawner';BE='block/entity/bookshelf/ChiseledCanopyShelfBlockEntity';E='events/EntityEvents'
    for n in ['entityInside','stepOn','attack','playerDestroy','tick']:
        ii=ins(H,n);assert pos(ii,'.cactus(')<pos(ii,'.hurt(')
        assert any(x['operand']==3.0 for x in ii)
        for j,x in enumerate(ii):
            if '.hurt(' in str(x['operand']):assert int(ii[j+1]['opcode'],16)==0x57
    for n in ['entityInside','stepOn']:assert pos(ins(H,n),'.shouldDamage(')<pos(ins(H,n),'.hurt(')
    for n in ['attack','playerDestroy','tick']:assert not any('.shouldDamage(' in str(x['operand']) for x in ins(H,n))
    assert pos(ins(H,'tick'),'.swinging')<pos(ins(H,'tick'),'.rayTrace(')<pos(ins(H,'tick'),'.hurt(')<pos(ins(H,'tick'),'.scheduleTick(')
    assert any('Spider' in str(x['operand']) for x in ins(H,'shouldDamage')) and any('.getVehicle(' in str(x['operand']) for x in ins(H,'shouldDamage'))
    assert any(x['operand']==0.10000000149011612 for x in ins('block/ArcticFurBlock','fallOn'))
    assert not {'fallOn','stepOn','updateEntityAfterFallOn'} & {m['name'] for m in methods('block/MazeSlimeBlock')}
    ii=ins(S,'serverTick');assert pos(ii,'.scanSpawnPositions(')<pos(ii,'.noCollision(')<pos(ii,'.loadEntityRecursive(')<pos(ii,'.getEntities(')<pos(ii,'.checkSpawnPositionSpawner(')<pos(ii,'.finalizeMobSpawnSpawner(')<pos(ii,'.tryAddFreshEntityWithPassengers(')<pos(ii,'.clear(')
    assert any('.countNextToSpawn' in str(x['operand']) for x in ii)
    scan=ins(S,'scanSpawnPositions');assert pos(scan,'CORONATION_CARPET')<pos(scan,'.nextBoolean(')<pos(scan,'.contains(')<pos(scan,'.add(')
    for n in ['load','save']:
        assert not any(any(k in str(x['operand']) for k in ['spawnBuffer','countNextToSpawn','checkPos']) for x in ins(S,n))
    spawn=ins(B,'attemptSpawnTome')
    assert pos(spawn,'.canBeReplaced(')<pos(spawn,'.noCollision(')<pos(spawn,'Difficulty.PEACEFUL')<pos(spawn,'.loadEntityRecursive(')<pos(spawn,'.getEntities(')<pos(spawn,'.finalizeMobSpawnSpawner(')<pos(spawn,'.tryAddFreshEntityWithPassengers(')<pos(spawn,'.setItem(')
    assert not any(any(k in str(x['operand']) for k in ['.checkSpawnPositionSpawner(','.checkSpawnObstruction(','.checkSpawnRules(','.spawnRange']) for x in spawn)
    recurse=next(j for j,x in enumerate(spawn) if '.attemptSpawnTome(' in str(x['operand']));assert int(spawn[recurse+1]['opcode'],16)==0x57
    assert pos(ins(BE,'removeItem'),'SPAWNER')<pos(ins(BE,'removeItem'),'ItemStack.EMPTY')<pos(ins(BE,'removeItem'),'ChiseledBookShelfBlockEntity.removeItem(')
    actual=ins(BE,'setEntityId');assert pos(actual,'.setEntityId(')<pos(actual,'SPAWNER')<pos(actual,'.setChanged(')
    fire=ins('block/ChiseledCanopyShelfBlock','onCaughtFire');assert pos(fire,'SPAWNER')<pos(fire,'ServerLevel')<pos(fire,'.attemptSpawnTome(')<pos(fire,'.destroyBlock(')
    tick=ins(B,'serverTick');assert pos(tick,'.isNearPlayer(')<pos(tick,'.shuffle(')<pos(tick,'.attemptSpawnTome(')<pos(tick,'SPAWNER')
    lambdas=[i for m in methods(B) if m['name'].startswith('lambda$attemptSpawnTome') for i in m['instructions']];assert any('.setRemainingFireTicks(' in str(x['operand']) for x in lambdas) and any('.setTarget(' in str(x['operand']) for x in lambdas)
    gather=ins(E,'gatherPotentialSpawns');assert pos(gather,'MobCategory.MONSTER')<pos(gather,'.isConquered(')<pos(gather,'.canSpawnMob(')<pos(gather,'.getSpawnListIndexAt(')<pos(gather,'.getSpawnableMonsterList(')
    callback=ins(E,'structureSpecialSpawns');assert not any('.setCanceled(' in str(x['operand']) for x in callback)
    assert any(int(x['opcode'],16)==0xc6 for x in callback) # null result skips replacement
    enderman=ins('events/EntityEvents$ExtendedEndermanTakeBlockGoal','canUse');assert pos(enderman,'.canUse(')<pos(enderman,'.dimensionTypeRegistration(')<pos(enderman,'TWILIGHT_DIM_TYPE')
    assert {int(i['opcode'],16) for i in ins('block/entity/spawner/FinalBossSpawnerBlockEntity','spawnMyBoss')}=={0x03,0xac}
    assert not any(any(x in str(i['operand']) for x in ['MeleeAttackGoal','RangedAttackGoal']) for i in ins('entity/RovingCube','registerGoals'))
    refs=[w for p in (OUT/'reference-evidence').glob('*.json') for w in read_json(p).get('witnesses',[])]
    raw=[c for p in (OUT/'vanilla-evidence').glob('*.json') for c in read_json(p).get('classes',[])]
    def ri(c,n):
        exact=[m for w in refs if w.get('archive_sha256') in ['8e3563a078289f0f07ee6f87f1c8651294387639c8355983ee207cb753f08b7f','d874b2aa4d511919a567ae73f13510e63e16f7318194eb2c03824cd68a59df6f'] and w['entry']==c+'.class' for m in w.get('methods',[]) if m['name']==n]
        return (exact or [m for w in raw if w['class_name']==c for m in w['methods'] if m['name']==n])[0]['instructions']
    setitem=ri('net/minecraft/world/level/block/entity/ChiseledBookShelfBlockEntity','setItem');assert pos(setitem,'.isEmpty(')<pos(setitem,'.removeItem(')
    assert next(int(x['opcode'],16) for x in setitem if '.removeItem(' in str(x['operand']))==0xb6
    finalize=ri('net/neoforged/neoforge/event/EventHooks','finalizeMobSpawnSpawner');assert pos(finalize,'.getOwner(')<pos(finalize,'.post(')<pos(finalize,'.isCanceled(')<pos(finalize,'.finalizeSpawn(')
    potential=ri('net/neoforged/neoforge/event/EventHooks','getPotentialSpawns');assert pos(potential,'.post(')<pos(potential,'.isCanceled(')<pos(potential,'NO_SPAWNS')
    core=next(w for w in refs if w['entry']=='twilightforest/asm/TFCoreMod.class')
    registered={str(i['operand']).split('.<init>')[0]+'.class' for m in core['methods'] for i in m['instructions'] if 'asm/transformers/' in str(i['operand']) and '.<init>' in str(i['operand'])}
    covered={w['entry'] for w in refs if w.get('archive_sha256')=='1324a81e5cf085d62385f85e4b06e6217bf977977f92c58034af315c5d975690'}
    assert len(registered)==31 and registered<=covered and set(ASM)<=registered,(len(registered),registered-covered)
    packet=ins('events/RegistrationEvents','setupPackets');j=next(i for i,x in enumerate(packet) if 'UpdateTFMultipartPacket.TYPE' in str(x['operand']));assert any('.playToClient(' in str(x['operand']) for x in packet[j:j+5])
    assert pos(ins('entity/TFPart','writeData'),'.packDirty(')>=0 and pos(ins('entity/TFPart','readData'),'.assignValues(')<pos(ins('entity/TFPart','readData'),'.refreshDimensions(')
    assert old.get('semantic_corrections')==new.get('semantic_corrections') and not s['damage_profiles'] and d['damage_census']['reviewed_profiles_after']==40
