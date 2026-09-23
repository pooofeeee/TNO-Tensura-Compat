"""Native multiplayer health/admission/order and actual consumer guardrails."""
from catalog_common import *


def validate_multiplayer(d,s,old,new,methods,ins,pos,target):
    from validate_twilight_multiplayer_read_ahead import census,FOLDER
    assert read_json(OUT/'twilightforest-multiplayer-caller-scan.json')==census()
    manifest=read_json(FOLDER/'manifest.json')
    for row in manifest['files']:assert sha256(FOLDER/row['file'])==row['sha256']
    E='events/EntityEvents';A='components/entity/MultiplayerInclusivityAttachment';S='block/entity/spawner/BossSpawnerBlockEntity'
    health=ins(E,'adjustEntityHealthInMultiplayerFights')
    assert pos(health,'MULTIPLAYER_INCLUSIVE_ENTITIES')<pos(health,'.adjustsHealth(')<pos(health,'.getEntitiesOfClass(')<pos(health,'.size(')<pos(health,'Attributes.MAX_HEALTH')<pos(health,'group_health_boost')<pos(health,'.addPermanentModifier(')
    assert sum(x['operand']==32.0 for x in health)==2 and any(x['operand']==10.0 for x in health)
    assert not any(any(k in str(x['operand']) for k in ['.setHealth(','.heal(','.hasModifier(','.removeModifier(','.getSpawnType(']) for x in health)
    amounts=ins(E,'getHealthBasedOnDifficulty');assert {x['operand'] for x in amounts if isinstance(x['operand'],float)}=={20.0,40.0,60.0,0.0}
    pred=[i for m in methods(E) if m['name'].startswith('lambda$adjustEntityHealthInMultiplayerFights') for i in m['instructions']];assert pos(pred,'NO_CREATIVE_OR_SPECTATOR')<pos(pred,'ENTITY_STILL_ALIVE')<pos(pred,'.and(')
    collect=ins(E,'addQualifiedGroupPlayerIfNeeded');assert pos(collect,'MULTIPLAYER_INCLUSIVE_ENTITIES')<pos(collect,'.getData(')<pos(collect,'DamageSource.getEntity(')<pos(collect,'.maybeAddQualifiedPlayer(')
    assert not any(any(k in str(x['operand']) for k in ['.getNewDamage(','.getOriginalDamage(','.getDirectEntity(','.getOwner(','.adjustsLootRolls(']) for x in collect)
    participant=ins(A,'maybeAddQualifiedPlayer');assert pos(participant,'net/minecraft/server/level/ServerPlayer')<pos(participant,'.contains(')<pos(participant,'.add(')
    death=ins(E,'grantGroupAdvancementIfNeeded');assert pos(death,'.isCanceled(')<pos(death,'.hasData(')<pos(death,'.grantGroupAdvancement(')
    assert not any('MULTIPLAYER_INCLUSIVE_ENTITIES' in str(x['operand']) or 'TFConfig' in str(x['operand']) for x in death)
    assert not any(any(k in str(x['operand']) for k in ['.clear(','.isAlive(','.distanceTo(']) for x in ins(A,'grantGroupAdvancement'))
    reg=ins('init/TFDataAttachments','<clinit>');start=next(i for i,x in enumerate(reg) if x['operand']=='multiplayer_fight');end=next(i for i in range(start,len(reg)) if 'MULTIPLAYER_FIGHT' in str(reg[i]['operand']));assert not any('.serialize(' in str(x['operand']) or '.copyOnDeath(' in str(x['operand']) for x in reg[start:end])
    for c in [S,'block/entity/spawner/LichSpawnerBlockEntity']:
        spawn=ins(c,'spawnMyBoss');assert pos(spawn,'.moveTo(')<pos(spawn,'.finalizeMobSpawn(')<pos(spawn,'.addFreshEntity(')
    naga=ins('entity/boss/Naga','finalizeSpawn');assert pos(naga,'Difficulty.EASY')<pos(naga,'difficulty_health_boost')<pos(naga,'.hasModifier(')<pos(naga,'.addPermanentModifier(')<pos(naga,'.getMaxHealth(')<pos(naga,'.setHealth(')
    for c in ['entity/boss/Lich','entity/boss/Minoshroom','entity/monster/Minotaur']:assert not any('.setHealth(' in str(x['operand']) or '.heal(' in str(x['operand']) for x in ins(c,'finalizeSpawn'))
    resources=read_json(WORK/'twilightforest/resources.json');tag=resources['data/twilightforest/tags/entity_type/multiplayer_inclusive_entities.json']['data']['values']
    assert set(tag)=={'twilightforest:'+n for n in ['naga','lich','minoshroom','hydra','ur_ghast','alpha_yeti','snow_queen','plateau_boss']}
    rolls=ins('loot/MultiplayerBasedNumberProvider','getFloat');assert pos(rolls,'.adjustsLootRolls(')<pos(rolls,'.hasParam(')<pos(rolls,'.hasData(')<pos(rolls,'.getQualifiedPlayers(')<pos(rolls,'.defaultRolls')<pos(rolls,'.rollsPerPlayer')<pos(rolls,'Math.max(')
    addition=ins('loot/MultiplayerBasedAdditionLootFunction','run');assert pos(addition,'.size(')<pos(addition,'.getInt(')<pos(addition,'.getCount(')<pos(addition,'.getMaxStackSize(')<pos(addition,'Mth.clamp(')<pos(addition,'.setCount(')
    assert sum('.getInt(' in str(x['operand']) for x in addition)==1 and any(int(x['opcode'],16)==0x68 for x in addition)
    refs=[w for p in (OUT/'reference-evidence').glob('*.json') for w in read_json(p).get('witnesses',[]) if w.get('archive_sha256') in ['8e3563a078289f0f07ee6f87f1c8651294387639c8355983ee207cb753f08b7f','d874b2aa4d511919a567ae73f13510e63e16f7318194eb2c03824cd68a59df6f']]
    refs+=read_json(FOLDER/'multiplayer-loader-preview.json')['witnesses']
    raw=[c for p in (OUT/'vanilla-evidence').glob('*.json') for c in read_json(p).get('classes',[])]+read_json(FOLDER/'multiplayer-native-preview.json')['classes']
    def rm(c,n):return [m for w in refs if w['entry']==c+'.class' for m in w.get('methods',[]) if m['name']==n] or [m for w in raw if w['class_name']==c for m in w['methods'] if m['name']==n]
    def ri(c,n):return rm(c,n)[0]['instructions']
    L='net/minecraft/world/entity/LivingEntity';AI='net/minecraft/world/entity/ai/attributes/AttributeInstance'
    finalize=ri('net/neoforged/neoforge/event/EventHooks','finalizeMobSpawn');assert pos(finalize,'.post(')<pos(finalize,'.isCanceled(')<pos(finalize,'.finalizeSpawn(')
    modifier=ri(AI,'addModifier');assert pos(modifier,'.putIfAbsent(')<pos(modifier,'IllegalArgumentException')
    assert pos(ri(AI,'addPermanentModifier'),'.addModifier(')<pos(ri(AI,'addPermanentModifier'),'.permanentModifiers')
    assert any('.permanentModifiers' in str(x['operand']) for x in ri(AI,'save')) and any('.permanentModifiers' in str(x['operand']) for x in ri(AI,'load'))
    hp=ri(L,'onAttributeUpdated');assert pos(hp,'MAX_HEALTH')<pos(hp,'.getMaxHealth(')<pos(hp,'.getHealth(')<pos(hp,'.setHealth(')
    actual=ri(L,'actuallyHurt');assert pos(actual,'.isInvulnerableTo(')<pos(actual,'.getDamageAfterArmorAbsorb(')<pos(actual,'.getDamageAfterMagicAbsorb(')<pos(actual,'.onLivingDamagePre(')<pos(actual,'.setHealth(')<pos(actual,'.onLivingDamagePost(')
    # Jump around the optional HP-change body lands at Post, proving zero-HP participation is possible.
    am=rm(L,'actuallyHurt')[0];code=bytes.fromhex(am['code_hex']);post=pos(actual,'.onLivingDamagePost(')
    branches=[x for x in actual if int(x['opcode'],16)==0x99 and x['offset']<pos(actual,'.setHealth(')]
    assert any(pos(actual,'.onDamageTaken(')<x['offset']+int.from_bytes(code[x['offset']+1:x['offset']+3],'big',signed=True)<post for x in branches)
    assert pos(ri(L,'die'),'.onLivingDeath(')<pos(ri(L,'die'),'.dead')
    eq=ri('net/minecraft/world/entity/Entity','equals');assert sum('.idI' in str(x['operand']) for x in eq)==2 and not any('UUID' in str(x['operand']) for x in eq)
    uniform=ri('net/minecraft/world/level/storage/loot/providers/number/UniformGenerator','getInt');assert any('Mth.nextInt(' in str(x['operand']) for x in uniform)
    floor=ri('net/minecraft/world/level/storage/loot/providers/number/NumberProvider','getInt');assert pos(floor,'.getFloat(')<pos(floor,'Math.round(')
    assert old.get('semantic_corrections')==new.get('semantic_corrections') and not s['damage_profiles'] and s['counts']['mechanic_packages']==1 and len(s['paths'])==3
    assert d['damage_census']['reviewed_profiles_after']==40
