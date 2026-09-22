"""Exact gate, ownership, native hint, pedestal and barrier ordering checks."""
from catalog_common import *
from classfile import ClassFile

def validate_structure_gates(d,s,old,new,methods,ins,pos,target):
    from collect_twilight_structure_gates import scan_callers
    scan=read_json(OUT/'twilightforest-structure-gates-caller-scan.json');assert scan==scan_callers(target)
    P='events/ProgressionEvents';U='world/components/structures/util/';S=U+'ProgressionStructure';H=U+'StructureHints';B='block/StrongholdShieldBlock';T='block/TrophyPedestalBlock';F='block/ForceFieldBlock'
    gate=ins(P,'isAreaProtected');assert pos(gate,'.instabuild')<pos(gate,'.isSpectator(')<pos(gate,'.isProgressionEnforced(')<pos(gate,'FakePlayer')<pos(gate,'.locateNearestLandmarkStart(')<pos(gate,'ProgressionStructure')<pos(gate,'.doesPlayerHaveRequiredAdvancements(')<pos(gate,'.sendAreaProtectionPacket(')<pos(gate,'.trySpawnHintMonster(')
    assert not any('Conquer' in str(x['operand']) for x in gate)
    hit=ins(P,'preventLockedAreaEntityDamage');assert pos(hit,'ServerLevel')<pos(hit,'Enemy')<pos(hit,'DamageSource.getEntity(')<pos(hit,'Kobold')<pos(hit,'.isAreaProtected(')<pos(hit,'.setCanceled(')
    assert not any(any(n in str(x['operand']) for n in ['.getDirectEntity(','.hurt(','.setHealth(','DamageTypeTags']) for x in hit)
    click=ins(P,'preventLockedAreaBlockPlacing');assert pos(click,'.isCanceled(')<pos(click,'.isAreaProtected(')<pos(click,'.setCanceled(')<pos(click,'.sendAllDataToRemote(')
    assert not any('BlockItem' in str(x['operand']) or 'Tag' in str(x['operand']) for x in click)
    breaking=ins(P,'preventLockedAreaBlockBreaking');assert pos(breaking,'.isBlockProtectedFromBreaking(')<pos(breaking,'.isAreaProtected(')<pos(breaking,'.setCanceled(')
    multi=ins(P,'preventLockedAreaMultiblocks');assert pos(multi,'.getReplacedBlockSnapshots(')<pos(multi,'.isBlockProtectedFromBreaking(')<pos(multi,'.setCanceled(')<pos(multi,'.sendAllDataToRemote(')
    assert any('TriState.FALSE' in str(x['operand']) for x in ins(P,'preventLockedAreaBlockInteracting'))
    with zipfile.ZipFile(target['path']) as jar:
        false_overrides=[]
        for entry in jar.namelist():
            if not entry.startswith('twilightforest/') or not entry.endswith('.class'):continue
            b=jar.read(entry)
            if b'isComponentProtected' not in b:continue
            for m in ClassFile(b).methods:
                if m['name']=='isComponentProtected' and m.get('code')==b'\x03\xac':false_overrides.append(entry.rsplit('/',1)[1][:-6])
        assert set(false_overrides)=={'StrongholdAccessChamberComponent','StrongholdUpperAscenderComponent','StrongholdUpperLeftTurnComponent','StrongholdUpperRightTurnComponent','StrongholdUpperCorridorComponent','StrongholdUpperTIntersectionComponent'}
    cooldown=ins(S,'trySpawnHintMonster');assert any(x['operand']==1200 for x in cooldown) and any(x['operand']==20 for x in cooldown)
    writes=[x['offset'] for x in cooldown if int(x['opcode'],16)==0xb5 and 'lastSpawnedHintMonsterTime' in str(x['operand'])];assert len(writes)==2 and writes[0]<pos(cooldown,'.didSpawnHintMonster(')<writes[1]
    hint=ins(H,'didSpawnHintMonster');assert pos(hint,'.createHintMonster(')<pos(hint,'.moveTo(')<pos(hint,'.checkSpawnObstruction(')<pos(hint,'.hasLineOfSight(')<pos(hint,'.createHintBook(')<pos(hint,'.setItemSlot(')<pos(hint,'.setDropChance(')<pos(hint,'.addFreshEntity(')
    at=next(i for i,x in enumerate(hint) if '.addFreshEntity(' in str(x['operand']));assert int(hint[at+1]['opcode'],16)==0x57 and int(hint[at+2]['opcode'],16)==0x04
    assert sum(x['operand']==16 for x in hint)==4 and sum(int(x['opcode'],16)==0x07 for x in hint)==2
    assert not any(any(n in str(x['operand']) for n in ['finalizeSpawn','finalizeMobSpawn','setOwner','setPersistenceRequired','checkSpawnRules']) for x in hint)
    shield=ins(B,'getDestroyProgress');assert pos(shield,'.rayTrace(')<pos(shield,'.getDirection(')<pos(shield,'.getDigSpeed(')<pos(shield,'Block.getDestroyProgress(')
    assert any('BLOCK_INTERACTION_RANGE' in str(x['operand']) for m in methods('util/entities/EntityUtil') if m['name']=='rayTrace' for x in m['instructions'])
    assert any(x['operand']==1.5 for x in shield) and any(x['operand']==100.0 for x in shield)
    assert not any('.getBlockPos(' in str(x['operand']) or '.getType(' in str(x['operand']) for x in shield)
    neighbor=ins(T,'neighborChanged');assert pos(neighbor,'.updateNeighbourForOutputSignal(')<pos(neighbor,'.isClientSide(')<pos(neighbor,'.isTrophyOnTop(')<pos(neighbor,'.isProgressionEnforced(')<pos(neighbor,'.areNearbyPlayersEligible(')<pos(neighbor,'.doPedestalEffect(')<pos(neighbor,'.warnIneligiblePlayers(')<pos(neighbor,'.rewardNearbyPlayers(')
    effect=ins(T,'doPedestalEffect');assert pos(effect,'.setBlockAndUpdate(')<pos(effect,'.removeNearbyShields(')<pos(effect,'.playSound(')
    remove=ins(T,'removeNearbyShields');assert any(x['operand']==-5 for x in remove) and pos(remove,'STRONGHOLD_SHIELD')<pos(remove,'.destroyBlock(')
    assert not any('BreakEvent' in str(x['operand']) for x in remove)
    reward=ins(T,'rewardNearbyPlayers');assert pos(reward,'ServerPlayer')<pos(reward,'PLACED_TROPHY_ON_PEDESTAL')<pos(reward,'.trigger(')<pos(reward,'.awardStat(')
    assert not any('Eligible' in str(x['operand']) for x in reward)
    for c in [B,T,F]:
        assert not any('.hurt(' in str(x['operand']) or '.setHealth(' in str(x['operand']) for m in methods(c) for x in m['instructions'])
    for c in [B,F]:assert [int(x['opcode'],16) for x in ins(c,'canEntityDestroy')]==[0x03,0xac]
    place=ins(F,'getStateForPlacement');assert any('.isSecondaryUseActive(' in str(x['operand']) for x in place) and not any('.getFluidState(' in str(x['operand']) for x in place)
    update=ins(F,'updateShape');assert pos(update,'.scheduleTick(')<pos(update,'.canConnectTo(')<pos(update,'.setValue(')
    assert [int(x['opcode'],16) for x in update[-2:]]==[0x2b,0xb0],'Failure returns original state'
    assert any('.isFaceSturdy(' in str(x['operand']) for x in ins(F,'fullFaceOrSimilarForceField'))
    refs=[w for p in (OUT/'reference-evidence').glob('*.json') for w in read_json(p).get('witnesses',[]) if w.get('archive_sha256') in ['8e3563a078289f0f07ee6f87f1c8651294387639c8355983ee207cb753f08b7f','d874b2aa4d511919a567ae73f13510e63e16f7318194eb2c03824cd68a59df6f']]
    raw=[c for p in (OUT/'vanilla-evidence').glob('*.json') for c in read_json(p).get('classes',[])]
    def rm(c,n):return [m for w in refs if w['entry']==c+'.class' for m in w.get('methods',[]) if m['name']==n] or [m for w in raw if w['class_name']==c for m in w['methods'] if m['name']==n]
    living=rm('net/minecraft/world/entity/LivingEntity','hurt')[0]['instructions'];assert pos(living,'.onEntityIncomingDamage(')<pos(living,'.onDamageBlock(')<pos(living,'.actuallyHurt(')
    base=rm('net/minecraft/world/entity/EntityType','getBaseClass')[0]['instructions'];assert any('net/minecraft/world/entity/Entity'==x['operand'] for x in base)
    collision=rm('net/minecraft/world/level/block/state/BlockBehaviour','getCollisionShape')[0]['instructions'];assert pos(collision,'.hasCollision')<pos(collision,'.getShape(')
    assert any(any('EntitySelector.NO_SPECTATORS' in str(x['operand']) for x in m['instructions']) for m in rm('net/minecraft/world/level/EntityGetter','getEntitiesOfClass'))
    res=read_json(WORK/'twilightforest/resources.json')
    adv=res['data/twilightforest/advancement/progress_trophy_pedestal.json']['data'];assert adv['requirements']==[['trophy_pedestal'],['kill_lich']] and adv['criteria']['trophy_pedestal']['trigger']=='twilightforest:placed_on_trophy_pedestal'
    assert adv['criteria']['kill_lich']['conditions']['player'][0]['predicate']['type_specific']['advancements']=={'twilightforest:progress_lich':True}
    cfg={p.rsplit('/',1)[1][:-5]:v['data'] for p,v in res.items() if p.startswith('data/twilightforest/worldgen/structure/') and isinstance(v['data'],dict) and 'hint_creature' in v['data']}
    assert len(cfg)==10 and all(v['hint_creature']['hint_mob']=='twilightforest:kobold' for v in cfg.values())
    assert len(res['data/twilightforest/tags/block/trophy_pedestal_activation_blocks.json']['data']['values'])==8
    allowed=res['data/twilightforest/tags/block/progression_allow_breaking.json']['data']['values'];assert {'id':'gravestone:gravestone','required':False} in allowed
    assert old.get('semantic_corrections')==new.get('semantic_corrections') and d['damage_census']['reviewed_profiles_after']==40 and not s['damage_profiles']
