"""Contact damage identity, ordering and independent block-state guards."""
from catalog_common import *
def validate_contacts(d,s,old,new,methods,ins,pos,target):
    from collect_twilight_contact_hazards import scan_callers,FIELDS
    scan=read_json(OUT/'twilightforest-contact-hazards-caller-scan.json');assert scan==scan_callers(target)
    expected={'THORNS':('ThornsBlock','entityInside',4.0),'OREBERRY':('OreBerryBlock','entityInside',1.0),'KNIGHTMETAL':('KnightmetalBlock','entityInside',4.0),'FIERY':('FieryBlock','stepOn',1.0)}
    for field,(c,n,amount) in expected.items():
        rows={(x['entry'],x['method']) for x in scan['hits'] if 'TFDamageTypes.'+field+'L' in str(x['instruction']['operand']) and '/init/' not in x['entry'] and '/data/' not in x['entry']}
        assert rows=={('twilightforest/block/'+c+'.class',n)},(field,rows)
        code=ins('block/'+c,n);assert pos(code,'TFDamageTypes.'+field)<pos(code,'.getDamageSource(')<pos(code,'.hurt(')
        at=next(i for i,x in enumerate(code) if '.hurt(' in str(x['operand']));assert int(code[at+1]['opcode'],16)==0x57 and code[at-1]['operand']==amount,(field,code[at-1])
        assert not any('.ignite' in str(x['operand']) or '.setRemainingFireTicks(' in str(x['operand']) for x in code)
    T='block/ThornsBlock';B='block/BurntThornsBlock';O='block/OreBerryBlock';K='block/KnightmetalBlock';F='block/FieryBlock';P='block/TFBushBlock';N='block/SnowLoggable'
    thorn=ins(T,'entityInside');assert pos(thorn,'ItemEntity')<pos(thorn,'IMMUNE_TO_THORNS')<pos(thorn,'TFDamageTypes.THORNS')
    step=ins(T,'stepOn');assert pos(step,'Axis.Y')<pos(step,'.entityInside(')
    grow=ins(T,'growThorns');assert any(x['operand']==3 for x in grow) and pos(grow,'.isEmptyBlock(')<pos(grow,'GREEN_THORNS')<pos(grow,'.setBlock(')
    burst=ins(T,'doThornBurst');assert sum('.growThorns(' in str(x['operand']) for x in burst)==9
    broke=ins(T,'onDestroyedByPlayer');assert pos(broke,'.instabuild')<pos(broke,'.isClientSide(')<pos(broke,'.doThornBurst(')<pos(broke,'ConnectableRotatedPillarBlock.onDestroyedByPlayer(')
    burnt=ins(B,'entityInside');assert pos(burnt,'.isClientSide(')<pos(burnt,'LivingEntity')<pos(burnt,'Projectile')<pos(burnt,'.destroyBlock(') and not any('.hurt(' in str(x['operand']) for x in burnt)
    ore=ins(O,'entityInside');assert pos(ore,'ItemEntity')<pos(ore,'OREBERRY')<pos(ore,'TFBushBlock.entityInside(') and not any('AGE' in str(x['operand']) or '.makeStuckInBlock(' in str(x['operand']) for x in ore)
    assert 'entityInside' not in {m['name'] for m in methods(P)}
    assert any(x['operand']==13 for x in ins(O,'canSurvive')) and any(x['operand']==10 for x in ins(O,'canGrowAt'))
    fiery=ins(F,'stepOn');assert pos(fiery,'.fireImmune(')<pos(fiery,'LivingEntity')<pos(fiery,'EquipmentSlot.FEET')<pos(fiery,'FIERY_BOOTS')<pos(fiery,'TFDamageTypes.FIERY')
    assert not any('.isSteppingCarefully(' in str(x['operand']) or 'FROST_WALKER' in str(x['operand']) for x in fiery)
    assert int(ins(F,'isFireSource')[0]['opcode'],16)==4
    harvest=ins(P,'useWithoutItem');assert pos(harvest,'AGE')<pos(harvest,'ServerLevel')<pos(harvest,'.dropFromBlockInteractLootTable(')<pos(harvest,'.setBlock(')<pos(harvest,'BLOCK_CHANGE')
    assert not any('.hurt(' in str(x['operand']) or '.makeStuckInBlock(' in str(x['operand']) for c in [P,'block/BerryBushBlock','block/DarkTowerBerryBushBlock',N,'block/ThornRoseBlock','block/SpecialStemLeavesBlock'] for m in methods(c) for x in m['instructions'])
    meal=ins('block/BerryBushBlock','performBonemeal');assert pos(meal,'.grow(')<pos(meal,'.tryGrowUpwards(') and not any('.canGrowAt(' in str(x['operand']) for x in meal)
    snow=ins(P,'useItemOn');assert pos(snow,'Items.SNOW')<pos(snow,'.canSurvive(')<pos(snow,'.isColliding(')<pos(snow,'.hasInfiniteMaterials(')<pos(snow,'.shrink(')<pos(snow,'.setBlock(')
    profiles={x['type'].split(':')[1]:x for x in s['damage_profiles']};assert set(profiles)=={x.lower() for x in FIELDS}
    assert profiles['knightmetal']['tags']==['neoforge:is_environment']
    for n in ['thorns','oreberry']:assert set(profiles[n]['tags'])=={'minecraft:no_knockback','neoforge:is_environment','neoforge:is_physical'}
    assert set(profiles['fiery']['tags'])=={'minecraft:no_knockback','minecraft:is_fire','neoforge:is_environment','neoforge:is_physical'}
    refs=[w for p in (OUT/'reference-evidence').glob('*.json') for w in read_json(p).get('witnesses',[]) if w.get('archive_sha256') in ['8e3563a078289f0f07ee6f87f1c8651294387639c8355983ee207cb753f08b7f','d874b2aa4d511919a567ae73f13510e63e16f7318194eb2c03824cd68a59df6f']]
    raw=[c for p in (OUT/'vanilla-evidence').glob('*.json') for c in read_json(p).get('classes',[])]
    def ri(c,n):
        selected=[m['instructions'] for w in refs if w['entry']==c+'.class' for m in w.get('methods',[]) if m['name']==n]
        return selected[0] if selected else next(m['instructions'] for w in raw if w['class_name']==c for m in w['methods'] if m['name']==n)
    source=ri('net/minecraft/world/damagesource/DamageSource','getSourcePosition');assert pos(source,'.damageSourcePosition')<pos(source,'.directEntity')
    knock=ri('net/minecraft/world/entity/LivingEntity','knockback');assert pos(knock,'.onLivingKnockBack(')<pos(knock,'KNOCKBACK_RESISTANCE')<pos(knock,'Math.random(')<pos(knock,'.setDeltaMovement(')
    fire=ri('net/minecraft/world/level/block/FireBlock','tick');assert pos(fire,'RULE_DOFIRETICK')<pos(fire,'.isFireSource(')<pos(fire,'.isRaining(')
    block=ri('net/minecraft/world/level/block/state/BlockBehaviour','entityInside');assert [int(x['opcode'],16) for x in block]==[0xb1]
    remove=ri('net/minecraft/server/level/ServerPlayerGameMode','removeBlock');assert pos(remove,'.onDestroyedByPlayer(')<pos(remove,'.destroy(')
    strider=ri('net/minecraft/world/entity/monster/Strider','tick');assert pos(strider,'.isNoAi(')<pos(strider,'STRIDER_WARM_BLOCKS')<pos(strider,'.getVehicle(')<pos(strider,'.setSuffocating(')
    res=read_json(WORK/'twilightforest/resources.json');assert res['data/twilightforest/tags/item/immune_to_thorns.json']['data']['values']==['twilightforest:thorn_leaves','twilightforest:thorn_rose']
    assert 'twilightforest:fiery_block' in res['data/minecraft/tags/block/strider_warm_blocks.json']['data']['values']
    assert old.get('semantic_corrections')==new.get('semantic_corrections')
    assert d['damage_census']['reviewed_profiles_after']==35 and d['damage_census']['remaining_profiles']==5
