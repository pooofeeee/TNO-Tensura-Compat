"""Installed ordering/source/return guards for the mechanical-hazard subsection."""
from catalog_common import *

def validate_mechanical(d,s,old,new,methods,ins,pos,target):
    from collect_twilight_mechanical_hazards import scan_callers,FIELDS
    scan=read_json(OUT/'twilightforest-mechanical-hazards-caller-scan.json');assert scan==scan_callers(target)
    J='block/entity/FireJetBlockEntity';R='block/entity/CarminiteReactorBlockEntity';D='block/entity/ReactorDebrisBlockEntity';S='entity/SlideBlock';B='block/SliderBlock'
    expected={'FIRE_JET':{(J,'tickFlame')},'REACTOR':{(R,'tick')},'SLIDER':{(B,'entityInside'),(S,'damageKnockbackEntities')}}
    for field,rows in expected.items():
        actual={(x['entry'],x['method']) for x in scan['hits'] if 'TFDamageTypes.'+field+'L' in str(x['instruction']['operand']) and '/data/' not in x['entry'] and '/init/' not in x['entry']}
        assert actual=={('twilightforest/'+c+'.class',n) for c,n in rows},(field,actual)
    for c,n,amount in [(J,'tickFlame',2.0),(B,'entityInside',5.0),(S,'damageKnockbackEntities',5.0)]:
        i=ins(c,n);at=next(k for k,x in enumerate(i) if '.hurt(' in str(x['operand']));assert i[at-1]['operand']==amount and int(i[at+1]['opcode'],16)==0x57
    flame=ins(J,'tickFlame');assert pos(flame,'.fireImmune(')<pos(flame,'TFDamageTypes.FIRE_JET')<pos(flame,'.hurt(')<pos(flame,'.setRemainingFireTicks(')
    assert any(x['operand']==60 for x in flame) and any(x['operand']==300 for x in flame)
    assert not any(int(x['opcode'],16)==0xb1 for x in flame[:-1]),'No early return after counter reset'
    assert pos(flame,'FireJetVariant.IDLE')<pos(flame,'FireJetVariant.TIMEOUT')<pos(flame,'.getEntitiesOfClass(')
    assert not any('.igniteForSeconds(' in str(x['operand']) for x in flame)
    assert any(x['operand']==80 for x in ins(J,'tickPopping'))
    fuel=ins('block/FireJetBlock','isLava');assert pos(fuel,'BlockTagGenerator.FIRE_JET_FUEL')<pos(fuel,'FluidTagGenerator.FIRE_JET_FUEL')
    natural=ins('block/FireJetBlock','randomTick');assert pos(natural,'FireJetVariant.IDLE')<pos(natural,'.findLavaAround(')<pos(natural,'Blocks.AIR')<pos(natural,'FireJetVariant.POPPING')
    for c in [J,R]:assert not {'saveAdditional','loadAdditional'} & {m['name'] for m in methods(c)}
    active=ins('block/CarminiteReactorBlock','neighborChanged');assert pos(active,'.isClientSide(')<pos(active,'ACTIVE')<pos(active,'.isReactorReady(')<pos(active,'.setBlockAndUpdate(')
    tick=ins(R,'tick');assert pos(tick,'.isDebug(')<pos(tick,'ACTIVE')<pos(tick,'.isClientSide(')<pos(tick,'.createFakeBlock(')<pos(tick,'.destroyBlock(')<pos(tick,'.explode(')<pos(tick,'.spawnGhastNear(')
    assert sum('.createFakeBlock(' in str(x['operand']) for x in tick)==26 and sum('.spawnGhastNear(' in str(x['operand']) for x in tick)==2
    assert any(x['operand']==350 for x in tick) and any(x['operand']==4.0 for x in tick) and any('ExplosionInteraction.BLOCK' in str(x['operand']) for x in tick)
    for needle in ['.destroyBlock(','.explode(']:
        at=next(k for k,x in enumerate(tick) if needle in str(x['operand']));assert int(tick[at+1]['opcode'],16)==0x57
    spawn=ins(R,'spawnGhastNear');assert pos(spawn,'CARMINITE_GHASTLING')<pos(spawn,'.create(')<pos(spawn,'.moveTo(')<pos(spawn,'.addFreshEntity(')
    assert not any(any(z in str(x['operand']) for z in ['.makeBossMinion(','.finalizeSpawn(','.checkSpawnRules(','.setOwner(','.setHealth(']) for x in spawn)
    trans=ins(R,'transformBlock');assert pos(trans,'Blocks.AIR')<pos(trans,'CARMINITE_REACTOR_IMMUNE')<pos(trans,'.getDestroySpeed(')<pos(trans,'CARMINITE_REACTOR_ORES')<pos(trans,'Blocks.NETHERRACK')<pos(trans,'Blocks.FIRE')
    assert any(x['operand']==8 for x in trans) and not any('BreakEvent' in str(x['operand']) or '.canEntityGrief(' in str(x['operand']) for x in trans)
    collision=ins('block/ReactorDebrisBlock','getCollisionShape');assert any('Shapes.block(' in str(x['operand']) for x in collision) and not any('.shape' in str(x['operand']) for x in collision)
    debris=ins(D,'tick');assert any(x['operand']==60 for x in debris) and not any('.isClientSide(' in str(x['operand']) for x in debris)
    assert all(any(x['operand']==key for x in ins(D,'saveAdditional')) for key in ['rerolls','will_disappear','timeAlive','textures','pos','sizes'])
    for c,n in [(B,'entityInside'),(S,'damageKnockbackEntities')]:
        code=ins(c,n);assert pos(code,'.hurt(')<pos(code,'.knockback(') and any(x['operand']==2.0 for x in code)
    assert pos(ins(S,'damageKnockbackEntities'),'LivingEntity')<pos(ins(S,'damageKnockbackEntities'),'.hurt(')
    moving=ins(S,'tick');assert not any('Entity.tick(' in str(x['operand']) for x in moving)
    mul=[k for k,x in enumerate(moving) if 'Vec3.multiply(' in str(x['operand'])];assert len(mul)==2 and moving[mul[0]-1]['operand']==.98 and int(moving[mul[0]+1]['opcode'],16)==0x57
    assert moving[mul[1]-1]['operand']==.7 and '.setDeltaMovement(' in moving[mul[1]+1]['operand']
    assert pos(moving,'.move(')<pos(moving,'.removeBlock(')<pos(moving,'.getOpposite(')<pos(moving,'.isUnobstructed(')<pos(moving,'.setBlockAndUpdate(')<pos(moving,'.damageKnockbackEntities(')
    assert not any('.canBeReplaced(' in str(x['operand']) or '.canSurvive(' in str(x['operand']) for x in moving)
    assert not {'hurt','getHealth'} & {m['name'] for m in methods(S)}
    connection=ins(B,'isConnectedInRangeRecursive');assert any(int(x['opcode'],16)==0xa6 for x in connection) and pos(connection,'.anyPlayerInRange(')<pos(connection,'.isConnectedInRangeRecursive(')
    schedule=ins(B,'scheduleBlockUpdate');assert any(int(x['opcode'],16)==0x88 for x in schedule) and any(int(x['opcode'],16)==0x70 for x in schedule)
    for c in ['block/TFSmokerBlock','block/EncasedSmokerBlock','block/entity/TFSmokerBlockEntity']:
        assert not any('.hurt(' in str(x['operand']) or '.setRemainingFireTicks(' in str(x['operand']) or '.addEffect(' in str(x['operand']) for m in methods(c) for x in m['instructions'])
    profiles={p['type'].split(':')[1]:p for p in s['damage_profiles']};assert set(profiles)=={f.lower() for f in FIELDS}
    assert set(profiles['fire_jet']['tags'])=={'minecraft:is_fire','minecraft:ignites_armor_stands','minecraft:no_knockback','neoforge:is_environment','neoforge:is_physical'}
    assert set(profiles['reactor']['tags'])=={'minecraft:no_knockback','neoforge:is_environment','neoforge:is_magic'}
    assert set(profiles['slider']['tags'])=={'neoforge:is_environment','neoforge:is_physical'}
    refs=[w for p in (OUT/'reference-evidence').glob('*.json') for w in read_json(p).get('witnesses',[]) if w.get('archive_sha256') in ['8e3563a078289f0f07ee6f87f1c8651294387639c8355983ee207cb753f08b7f','d874b2aa4d511919a567ae73f13510e63e16f7318194eb2c03824cd68a59df6f']]
    raw=[c for p in (OUT/'vanilla-evidence').glob('*.json') for c in read_json(p).get('classes',[])]
    def rm(c,n):
        rows=[m for w in refs if w['entry']==c+'.class' for m in w.get('methods',[]) if m['name']==n]
        return rows or [m for w in raw if w['class_name']==c for m in w['methods'] if m['name']==n]
    def ri(c,n):return rm(c,n)[0]['instructions']
    exp=ri('net/minecraft/world/level/Explosion','explode');assert pos(exp,'.onExplosionDetonate(')<pos(exp,'.hurt(')<pos(exp,'EXPLOSION_KNOCKBACK_RESISTANCE')<pos(exp,'.getExplosionKnockback(')<pos(exp,'.setDeltaMovement(')
    calc=ri('net/minecraft/world/level/ExplosionDamageCalculator','getEntityDamageAmount');assert any(x['operand']==7.0 for x in calc) and not any(int(x['opcode'],16)==0x8e for x in calc),'Native formula has no d2i rounding'
    level=next(m['instructions'] for m in rm('net/minecraft/world/level/Level','explode') if any('.onExplosionStart(' in str(x['operand']) for x in m['instructions']));assert pos(level,'.onExplosionStart(')<pos(level,'Explosion.explode(')<pos(level,'.finalizeExplosion(')
    nearest=next(m['instructions'] for m in rm('net/minecraft/world/level/EntityGetter','getNearestPlayer') if any('NO_CREATIVE_OR_SPECTATOR' in str(x['operand']) for x in m['instructions']));assert any('NO_CREATIVE_OR_SPECTATOR' in str(x['operand']) for x in nearest) and any('NO_SPECTATORS' in str(x['operand']) for x in nearest)
    timer=ri('net/minecraft/world/entity/Entity','setRemainingFireTicks');assert len(timer)==4 and int(timer[-2]['opcode'],16)==0xb5
    res=read_json(WORK/'twilightforest/resources.json');assert res['data/twilightforest/tags/block/fire_jet_fuel.json']['data']['values']==['minecraft:lava']
    assert res['data/twilightforest/tags/block/carminite_reactor_ores.json']['data']['values']==['minecraft:nether_quartz_ore','minecraft:nether_gold_ore']
    assert old.get('semantic_corrections')==new.get('semantic_corrections') and d['damage_census']['reviewed_profiles_after']==38 and d['damage_census']['remaining_profiles']==2
