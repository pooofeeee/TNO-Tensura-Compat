"""Exact source/admission/death/re-entry/cadence guards for the final two types."""
from catalog_common import *

def validate_ominous(d,s,old,new,methods,ins,pos,target):
    from collect_twilight_ominous_progression import scan_callers
    scan=read_json(OUT/'twilightforest-ominous-progression-caller-scan.json');assert scan==scan_callers(target)
    F='block/OminousFireBlock';E='events/EntityEvents';W='util/entities/OminousFireDamageSource';P='events/ProgressionEvents';N='init/custom/Enforcements';R='item/recipe/EssenceRepairRecipe'
    for key,wanted in [('OMINOUS_FIRE',{(F,'entityInside'),(E,'ominousFireConversion')}),('ACID_RAIN',{(N,'lambda$static$8')})]:
        actual={(x['entry'],x['method']) for x in scan['hits'] if 'TFDamageTypes.'+key+'L' in str(x['instruction']['operand']) and '/data/' not in x['entry'] and '/init/TFDamageTypes' not in x['entry']}
        assert actual=={('twilightforest/'+c+'.class',n) for c,n in wanted},(key,actual)
    hit=ins(F,'entityInside');assert pos(hit,'EntityTypeTags.UNDEAD')<pos(hit,'TFDamageTypes.OMINOUS_FIRE')<pos(hit,'.hurt(')
    at=next(i for i,x in enumerate(hit) if '.hurt(' in str(x['operand']));assert hit[at-1]['operand']==1.0 and int(hit[at+1]['opcode'],16)==0x57
    assert not any(any(z in str(x['operand']) for z in ['BaseFireBlock.entityInside(','.fireImmune(','.ignite','.setRemainingFireTicks(']) for x in hit)
    survive=ins(F,'canSurvive');assert pos(survive,'.isFaceSturdy(')<pos(survive,'.getFluidState(')<pos(survive,'.isEmpty(')
    use=ins('item/ExanimateEssenceItem','useOn');assert pos(use,'CandleBlock')<pos(use,'CANDLE_MAP')<pos(use,'.LIT')<pos(use,'CANDLES')<pos(use,'.getClickedFace(')<pos(use,'.canBeReplaced(')<pos(use,'.canSurvive(')<pos(use,'.shrink(')
    assert not any('.hasInfiniteMaterials(' in str(x['operand']) or '.instabuild' in str(x['operand']) for x in use)
    for c in ['block/OminousCandleBlock','block/entity/OminousCandleBlockEntity']:
        assert not any('.hurt(' in str(x['operand']) or '.ignite' in str(x['operand']) or '.setRemainingFireTicks(' in str(x['operand']) for m in methods(c) for x in m['instructions'])
    death=ins(E,'ominousFireConversion');assert pos(death,'.isCanceled(')<pos(death,'TFDamageTypes.OMINOUS_FIRE')<pos(death,'TFDataMaps.OMINOUS_FIRE')<pos(death,'ServerPlayer')<pos(death,'EntityType.ZOMBIE')<pos(death,'ZOMBIFIED_PLAYER')<pos(death,'.setBaby(')<pos(death,'.finalizeMobSpawn(')<pos(death,'.addFreshEntity(')<pos(death,'.convertEntity(')
    assert not any('.setCanceled(' in str(x['operand']) or '.setHealth(' in str(x['operand']) or '.getInventory(' in str(x['operand']) for x in death)
    wrap=ins(E,'zombifiedPlayerAttacks');assert pos(wrap,'OminousFireDamageSource')<pos(wrap,'.getEntity(')<pos(wrap,'Zombie')<pos(wrap,'ZOMBIFIED_PLAYER')<pos(wrap,'.getAmount(')<pos(wrap,'.setCanceled(')<pos(wrap,'.hurt(')
    at=next(i for i,x in enumerate(wrap) if '.hurt(' in str(x['operand']));assert int(wrap[at+1]['opcode'],16)==0x57
    ctor=ins(W,'<init>');assert pos(ctor,'.typeHolder(')<pos(ctor,'.getEntity(')<pos(ctor,'.getDirectEntity(')<pos(ctor,'.getSourcePosition(')<pos(ctor,'DamageSource.<init>(')
    assert not any('TFDamageTypes' in str(x['operand']) for x in ctor)
    msg=ins(W,'getLocalizedDeathMessage');assert pos(msg,'.getKillCredit(')<pos(msg,'ZOMBIFIED_PLAYER')<pos(msg,'.getGameProfile(')<pos(msg,'.getName(')<pos(msg,'String.equals(')
    outer=ins(P,'performProtectionAndPortalChecks');assert pos(outer,'ServerPlayer')<pos(outer,'ServerLevel')<pos(outer,'.isProgressionEnforced(')<pos(outer,'.isCreative(')<pos(outer,'.isSpectator(')<pos(outer,'.enforceBiomeProgression(')
    assert any(x['operand']==20 for x in outer)
    callers={(x['entry'],x['method']) for x in scan['hits'] if 'Enforcement.enforceBiomeProgression(' in str(x['instruction']['operand'])};assert callers=={('twilightforest/events/ProgressionEvents.class','performProtectionAndPortalChecks')}
    acid=ins(N,'lambda$static$8');assert any(x['operand']==5 for x in acid) and pos(acid,'.runsNormally(')<pos(acid,'ACID_RAIN')<pos(acid,'.multiplier(')<pos(acid,'.hurt(')<pos(acid,'.playSound(')
    at=next(i for i,x in enumerate(acid) if '.hurt(' in str(x['operand']));assert int(acid[at+1]['opcode'],16)==0x99,'Sound depends on truehurt'
    for c in [N,'util/Enforcement','util/Restriction']:
        assert not any(any(z in str(x['operand']) for z in ['.isRaining(','.canSeeSky(','.isRainingAt(']) for m in methods(c) for x in m['instructions'])
    advance=ins('util/PlayerHelper','playerHasRequiredAdvancements');assert sum('Iterator.next(' in str(x['operand']) for x in advance)==1 and sum('Iterator.hasNext(' in str(x['operand']) for x in advance)==1
    from classfile import ClassFile
    with zipfile.ZipFile(target['path']) as jar:body=next(m['code'] for m in ClassFile(jar.read('twilightforest/util/PlayerHelper.class')).methods if m['name']=='playerHasRequiredAdvancements')
    assert all(int.from_bytes(body[x['offset']+1:x['offset']+3],byteorder='big',signed=True)>0 for x in advance if 0x99<=int(x['opcode'],16)<=0xa7),'No advancement loop/back-edge'
    match=ins(R,'matches');assert pos(match,'ItemTagGenerator.SCEPTERS')<pos(match,'.isDamaged(')<pos(match,'EXANIMATE_ESSENCE')
    craft=ins(R,'assemble');assert pos(craft,'.isDamaged(')<pos(craft,'.copy(')<pos(craft,'.setDamageValue(') and not any('EXANIMATE_ESSENCE' in str(x['operand']) for x in craft)
    profiles={p['type'].split(':')[1]:p for p in s['damage_profiles']};assert set(profiles)=={'acid_rain','ominous_fire'}
    assert set(profiles['ominous_fire']['tags'])=={'minecraft:bypasses_armor','minecraft:bypasses_shield','minecraft:no_knockback','minecraft:panic_causes','minecraft:panic_environmental_causes','minecraft:wither_immune_to','neoforge:is_magic'}
    assert set(profiles['acid_rain']['tags'])=={'minecraft:bypasses_armor','minecraft:bypasses_shield','minecraft:bypasses_wolf_armor','minecraft:no_knockback','minecraft:witch_resistant_to','neoforge:is_environment','neoforge:is_magic'}
    refs=[w for p in (OUT/'reference-evidence').glob('*.json') for w in read_json(p).get('witnesses',[]) if w.get('archive_sha256') in ['8e3563a078289f0f07ee6f87f1c8651294387639c8355983ee207cb753f08b7f','d874b2aa4d511919a567ae73f13510e63e16f7318194eb2c03824cd68a59df6f']]
    raw=[c for p in (OUT/'vanilla-evidence').glob('*.json') for c in read_json(p).get('classes',[])]
    def rm(c,n):
        rows=[m for w in refs if w['entry']==c+'.class' for m in w.get('methods',[]) if m['name']==n]
        return rows or [m for w in raw if w['class_name']==c for m in w['methods'] if m['name']==n]
    def ri(c,n):return rm(c,n)[0]['instructions']
    source=next(m['instructions'] for m in rm('net/minecraft/world/damagesource/DamageSource','<init>') if 'Lnet/minecraft/world/phys/Vec3;' in m.get('descriptor','') and m['descriptor'].count('Lnet/minecraft/world/entity/Entity;')==2)
    assert pos(source,'.causingEntity')<pos(source,'.directEntity')
    # Actual native constructor local slots: direct=2,causing=3; wrapper supplies them reversed.
    causing=next(i for i,x in enumerate(source) if '.causingEntity' in str(x['operand']));direct=next(i for i,x in enumerate(source) if '.directEntity' in str(x['operand']));assert int(source[causing-1]['opcode'],16)==0x2d and int(source[direct-1]['opcode'],16)==0x2c
    player=ri('net/minecraft/world/entity/player/Player','hurt');assert pos(player,'.scaleDamage(')<pos(player,'LivingEntity.hurt(')
    living=ri('net/minecraft/world/entity/LivingEntity','hurt');assert pos(living,'.onEntityIncomingDamage(')<pos(living,'.onDamageBlock(')<pos(living,'.actuallyHurt(')
    scale=ri('net/neoforged/neoforge/common/damagesource/IScalingFunction','lambda$static$0');assert any(x['operand']==1.5 for x in scale) and any('Math.min(' in str(x['operand']) for x in scale)
    mob=ri('net/minecraft/world/entity/Mob','doHurtTarget');at=next(i for i,x in enumerate(mob) if '.hurt(' in str(x['operand']));assert any(int(x['opcode'],16)==0x99 for x in mob[at+1:at+5]) and pos(mob,'.hurt(')<pos(mob,'.doPostAttackEffects(')
    ldeath=ri('net/minecraft/world/entity/LivingEntity','die');assert pos(ldeath,'.onLivingDeath(')<pos(ldeath,'.isRemoved(')<pos(ldeath,'.dropAllDeathLoot(')
    zomb=ri('net/minecraft/world/entity/monster/Zombie','finalizeSpawn');assert pos(zomb,'.setCanPickUpLoot(')<pos(zomb,'.getSpawnAsBabyOdds(')<pos(zomb,'.setBaby(')<pos(zomb,'.populateDefaultEquipmentSlots(')
    fire=ri('net/minecraft/world/level/block/BaseFireBlock','entityInside');assert pos(fire,'.setRemainingFireTicks(')<pos(fire,'.igniteForSeconds(')<pos(fire,'.inFire(')<pos(fire,'.hurt(')
    place=ri('net/minecraft/world/level/block/BaseFireBlock','onPlace');assert pos(place,'.onTrySpawnPortal(')<pos(place,'.createPortalBlocks(')<pos(place,'.canSurvive(')
    assert any('BlockTags.FIRE' in str(x['operand']) for x in ri('net/minecraft/world/level/portal/PortalShape','isEmpty'))
    burning=ri('net/minecraft/world/entity/LivingEntity','igniteForTicks');assert pos(burning,'BURNING_TIME')<pos(burning,'Mth.ceil(')<pos(burning,'Entity.igniteForTicks(')
    res=read_json(WORK/'twilightforest/resources.json');assert res['data/minecraft/tags/block/fire.json']['data']['values']==['twilightforest:ominous_fire']
    assert len(res['data/twilightforest/data_maps/entity_type/ominous_fire.json']['data']['values'])==3
    restrictions={p.rsplit('/',1)[1][:-5]:v['data'] for p,v in res.items() if p.startswith('data/twilightforest/twilight/restrictions/')};assert len(restrictions)==9 and all(len(v['advancements'])==1 for v in restrictions.values())
    assert {k:v['multiplier'] for k,v in restrictions.items() if v['enforcement']=='twilightforest:acid_rain'}=={'highlands':.5,'thornlands':1.0,'final_plateau':1.5}
    assert old.get('semantic_corrections')==new.get('semantic_corrections') and d['damage_census']['reviewed_profiles_after']==40 and d['damage_census']['remaining_profiles']==0
    from twilight_damage_closure import census
    assert read_json(OUT/'twilightforest-r2f8y-damage-type-closure.json')==census()
