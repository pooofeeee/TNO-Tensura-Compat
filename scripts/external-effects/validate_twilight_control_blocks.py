"""Exact-source guardrails for terrain construction/substitution and native cloud consumers."""
from catalog_common import *
from classfile import ClassFile
import tomllib

def validate_control_blocks(d,s,old,new,methods,ins,pos,target):
    from collect_twilight_control_blocks import scan_callers,CONFIG,ASM
    from twilight_subsection import damage_tags
    assert read_json(OUT/'twilightforest-control-blocks-caller-scan.json')==scan_callers(target)
    snap=read_json(OUT/'twilightforest-control-blocks-config-snapshot.json');assert snap['sha256']==sha256(CONFIG) and snap['data']==tomllib.loads(CONFIG.read_text(encoding='utf-8')) and snap['data']['cloudBlockPrecipitationDistance']==32
    B='block/BuilderBlock';BE='block/entity/CarminiteBuilderBlockEntity';BU='block/TranslucentBuiltBlock';AE='block/entity/AntibuilderBlockEntity';C='block/CloudBlock';H='asmhooks/BlockHooks'
    place=ins(B,'onPlace');assert pos(place,'.isClientSide(')<pos(place,'BUILDER_INACTIVE')<pos(place,'.hasNeighborSignal(')<pos(place,'.setBlockAndUpdate(') and not any('.scheduleTick(' in str(x['operand']) or '.startBuilding(' in str(x['operand']) for x in place)
    signal=ins(B,'neighborChanged');assert sum('.scheduleTick(' in str(x['operand']) for x in signal)==2 and any(x['operand']==4 for x in signal)
    ticker=ins(B,'getTicker');assert pos(ticker,'BUILDER_ACTIVE')<pos(ticker,'TOWER_BUILDER')
    build=ins(BE,'tick');assert pos(build,'.makingBlocks')<pos(build,'.findClosestValidPlayer(')<pos(build,'.findNextFacing(')<pos(build,'.ticksRunning')<pos(build,'.isEmptyBlock(')<pos(build,'.setBlock(')<pos(build,'.blockedCounter')
    at=next(i for i,x in enumerate(build) if x['operand']==16);assert int(build[at+1]['opcode'],16)==0xa3,'blocksMade >16 rejects: 17 admitted branches from zero'
    at=next(i for i,x in enumerate(build) if '.setBlock(' in str(x['operand']));assert int(build[at+1]['opcode'],16)==0x57
    assert any(x['operand']==60 for x in build) and any(x['operand']==10 for x in build)
    reset=ins(BE,'resetStats');assert not any(any('.'+n in str(x['operand']) for n in ['makingBlocks','ticksRunning','trackedPlayer']) for x in reset)
    for c in [BE,AE]:assert not {'saveAdditional','loadAdditional','addAdditionalSaveData','readAdditionalSaveData'} & {m['name'] for m in methods(c)}
    nearest=ins(BE,'findClosestValidPlayer');at=next(i for i,x in enumerate(nearest) if '.getNearestPlayer(' in str(x['operand']));assert int(nearest[at-1]['opcode'],16)==0x03 and any(x['operand']==16.0 for x in nearest)
    remove=ins(BU,'tick');assert pos(remove,'ACTIVE')<pos(remove,'.removeBlock(')<pos(remove,'Direction.values(')<pos(remove,'.activateBuiltBlocks(')
    active=ins(B,'activateBuiltBlocks');assert pos(active,'BUILT_BLOCK')<pos(active,'ACTIVE')<pos(active,'.setBlockAndUpdate(')<pos(active,'.scheduleTick(') and any(x['operand']==10 for x in active)
    antitick=ins(AE,'tick');assert pos(antitick,'.anyPlayerInRange(')<pos(antitick,'.isClientSide(')<pos(antitick,'.isAreaLoaded(')<pos(antitick,'.captureBlockData(')<pos(antitick,'.scanAndRevertChanges(')
    capture=ins(AE,'captureBlockData');assert any(x['operand']==729 for x in capture) and not any('getBlockEntity' in str(x['operand']) for x in capture)
    scan=ins(AE,'scanAndRevertChanges');assert sum('.getBlock(' in str(x['operand']) for x in scan)==2 and not any('getValue' in str(x['operand']) or 'getBlockEntity' in str(x['operand']) for x in scan)
    revert=ins(AE,'revertBlock');assert pos(revert,'.isAir(')<pos(revert,'.blocksMotion(')<pos(revert,'.getDestroySpeed(')<pos(revert,'.isUnrevertable(')<pos(revert,'.nextInt(')<pos(revert,'ANTIBUILT_BLOCK')<pos(revert,'.updateOrDestroy(')
    assert any(x['operand']==10 for x in revert) and not any('.hurt(' in str(x['operand']) or '.setHealth(' in str(x['operand']) for c in [B,BE,BU,AE] for m in methods(c) for x in m['instructions'])
    fall=ins(C,'fallOn');assert pos(fall,'.fall(')<pos(fall,'.causeFallDamage(') and any(abs(x['operand']-.1)<1e-6 for x in fall if isinstance(x['operand'],float))
    at=next(i for i,x in enumerate(fall) if '.causeFallDamage(' in str(x['operand']));assert int(fall[at+1]['opcode'],16)==0x57
    precip=ins(C,'randomTick');assert pos(precip,'.isAreaLoaded(')<pos(precip,'commonCloudBlockPrecipitationDistance')<pos(precip,'.getCurrentPrecipitation(')<pos(precip,'MOTION_BLOCKING')<pos(precip,'RULE_SNOW_ACCUMULATION_HEIGHT')<pos(precip,'.pushEntitiesUp(')<pos(precip,'.handlePrecipitation(')
    snow=ins(C,'shouldSnow');assert any(x['operand']==10 for x in snow) and pos(snow,'LightLayer.BLOCK')<pos(snow,'.isAir(')<pos(snow,'.canSurvive(')
    rain=ins(H,'isRainingAt');assert pos(rain,'commonCloudBlockPrecipitationDistance')<pos(rain,'.hasChunkAt(')<pos(rain,'.getChunkAt(')<pos(rain,'.getCurrentPrecipitation(')<pos(rain,'MOTION_BLOCKING')
    shroom=ins(H,'modifySoilDecisionForMushroomBlockSurvivability');assert pos(shroom,'.isDefault(')<pos(shroom,'TWILIGHT_PORTAL')<pos(shroom,'TriState.TRUE')
    snowy=ins(H,'keepSnowyStateForSnowloggableBlocks');assert pos(snowy,'SnowLoggable')<pos(snowy,'SNOW_LAYERS')
    for m in methods('client/event/CloudEvents'):
        assert not any(any(k in str(x['operand']) for k in ['.hurt(','.setHealth(','.setDeltaMovement(','.addEffect(','.setWeatherParameters(']) for x in m['instructions'])
    resources=read_json(WORK/'twilightforest/resources.json');ign=resources['data/twilightforest/tags/block/antibuilder_ignores.json']['data']['values'];prot=resources['data/twilightforest/tags/block/common_protections.json']['data']['values'];assert 'twilightforest:antibuilt_block' not in ign+prot and '#twilightforest:common_protections' in ign and dict(id='gravestone:gravestone',required=False) in ign
    asm=read_json(OUT/'reference-evidence/twilight-control-blocks-asm.json')['witnesses'];assert {w['entry'] for w in asm}==set(ASM)
    for w in asm:
        flat=[x for m in w['methods'] for x in m['instructions']];ops=[x['operand'] for x in flat]
        assert 'twilightforest/asmhooks/BlockHooks' in ops and any('Target.targetMethod' in str(x) for x in ops)
        if '/shroom/' in w['entry']:assert 'canSustainPlant' in ops and 'modifySoilDecisionForMushroomBlockSurvivability' in ops and 'canSurvive' in ops
        else:assert 172 in ops and any('ASMUtil.findInstructions(' in str(x) for x in ops)
    refs=[w for p in (OUT/'reference-evidence').glob('*.json') for w in read_json(p).get('witnesses',[]) if w.get('archive_sha256') in ['8e3563a078289f0f07ee6f87f1c8651294387639c8355983ee207cb753f08b7f','d874b2aa4d511919a567ae73f13510e63e16f7318194eb2c03824cd68a59df6f']]
    raw=[c for p in (OUT/'vanilla-evidence').glob('*.json') for c in read_json(p).get('classes',[])]
    def rm(c,n):return [m for w in refs if w['entry']==c+'.class' for m in w.get('methods',[]) if m['name']==n] or [m for w in raw if w['class_name']==c for m in w['methods'] if m['name']==n]
    def ri(c,n):return rm(c,n)[0]['instructions']
    E='net/minecraft/world/entity/Entity';L='net/minecraft/world/entity/LivingEntity';Q='net/minecraft/world/level/block/entity/ConduitBlockEntity'
    lf=ri(L,'causeFallDamage');assert pos(lf,'.onLivingFall(')<pos(lf,'Entity.causeFallDamage(')<pos(lf,'.calculateFallDamage(')<pos(lf,'.hurt(');at=next(i for i,x in enumerate(lf) if '.hurt(' in str(x['operand']));assert int(lf[at+1]['opcode'],16)==0x57
    calc=ri(L,'calculateFallDamage');assert pos(calc,'FALL_DAMAGE_IMMUNE')<pos(calc,'SAFE_FALL_DISTANCE')<pos(calc,'FALL_DAMAGE_MULTIPLIER')<pos(calc,'Mth.ceil') and not any('MobEffects.JUMP' in str(x['operand']) for x in calc)
    wet=ri(E,'isInRain');assert sum('.isRainingAt(' in str(x['operand']) for x in wet)==2
    sensitive=ri(L,'aiStep');assert pos(sensitive,'.isSensitiveToWater(')<pos(sensitive,'.isInWaterRainOrBubble(')<pos(sensitive,'.drown(')
    for c in ['monster/Blaze','monster/EnderMan','monster/Strider','animal/SnowGolem']:assert int(ri('net/minecraft/world/entity/'+c,'isSensitiveToWater')[0]['opcode'],16)==0x04
    hurt=ri('net/minecraft/world/entity/monster/EnderMan','hurt');assert pos(hurt,'.isInvulnerableTo(')<pos(hurt,'Monster.hurt(')<pos(hurt,'.nextInt(')<pos(hurt,'.teleport(')
    tri=ri('net/minecraft/world/item/TridentItem','releaseUsing');assert pos(tri,'.getTridentSpinAttackStrength(')<pos(tri,'.isInWaterOrRain(')<pos(tri,'.isTooDamagedToUse(')<pos(tri,'.hurtAndBreak(')<pos(tri,'.startAutoSpinAttack(')
    shape=ri(Q,'updateShape');assert pos(shape,'.isWaterAt(')<pos(shape,'.isConduitFrame(') and any(x['operand']==16 for x in shape)
    effect=ri(Q,'applyEffects');assert pos(effect,'.isInWaterOrRain(')<pos(effect,'CONDUIT_POWER')<pos(effect,'.addEffect(') and any(x['operand']==260 for x in effect)
    targetins=ri(Q,'updateDestroyTarget');assert any(x['operand']==42 for x in targetins) and pos(targetins,'.magic(')<pos(targetins,'.hurt(');at=next(i for i,x in enumerate(targetins) if '.hurt(' in str(x['operand']));assert int(targetins[at+1]['opcode'],16)==0x57
    f=ri('net/minecraft/world/level/block/FireBlock','tick');assert pos(f,'.isRaining(')<pos(f,'.isNearRain(')
    burn=ri('net/minecraft/world/level/block/FireBlock','checkBurnOut');assert pos(burn,'.onCaughtFire(')<pos(burn,'.isRainingAt(')
    p=read_json(OUT/'twilightforest-control-blocks-vanilla-sources.json')['profiles'];assert {x['type'] for x in p}=={'minecraft:'+x for x in ['fall','drown','magic','dry_out']}
    loader_tags=[w for w in read_json(OUT/'reference-evidence/twilight-portals-244.json')['witnesses'] if '/tags/damage_type/' in w['entry']]
    for x in p:
        extra=['neoforge:'+w['entry'].rsplit('/',1)[-1][:-5] for w in loader_tags if x['type'] in w['data']['values']]
        assert x['tags']==sorted(set(damage_tags()(x['type'])+extra)) and x['direct_entity'] is None and x['causing_entity'] is None and x['source_position'] is None
    assert old.get('semantic_corrections')==new.get('semantic_corrections') and not s['damage_profiles'] and d['damage_census']['reviewed_profiles_after']==40
