"""Bytecode ordering, native caller, source and passive-resource guards."""
from catalog_common import *
def validate_passives(d,s,old,new,methods,ins,pos,target):
    from collect_twilight_passive_entities import scan_callers
    assert read_json(OUT/'twilightforest-passive-entities-caller-scan.json')==scan_callers(target)
    P='entity/passive/';Q=P+'QuestRam';G='entity/ai/goal/QuestRamEatWoolGoal';F=P+'FlyingBird';D=P+'Deer'
    hand=ins(Q,'interactAt');assert pos(hand,'.isClientSide(')<pos(hand,'.tryAccept(')<pos(hand,'.consume(')<pos(hand,'InteractionResult.SUCCESS')
    accept=ins(Q,'tryAccept');assert pos(accept,'Ingredient.test(')<pos(accept,'.isColorPresent(')<pos(accept,'.setColorPresent(')<pos(accept,'.animateAddColor(')
    assert not any('.shrink(' in str(x['operand']) or '.heal(' in str(x['operand']) for x in accept)
    goal=ins(G,'tick');assert pos(goal,'.isClientSide(')<pos(goal,'.isItemTempting(')<pos(goal,'.distanceToSqr(')<pos(goal,'.tryAccept(')<pos(goal,'ItemEntity.discard(')<pos(goal,'GameEvent.EAT')
    assert any(x['operand']==6.25 for x in goal) and not any('.shrink(' in str(x['operand']) or '.consume(' in str(x['operand']) or '.canEntityGrief(' in str(x['operand']) for m in methods(G) for x in m['instructions'])
    selection=[x for m in methods(G) if m['name'].startswith('lambda$canUse') for x in m['instructions']]
    assert pos(selection,'.onGround(')<pos(selection,'.isInWater(')<pos(selection,'.isAlive(')<pos(selection,'.isEmpty(')<pos(selection,'.hasLineOfSight(')<pos(selection,'.isItemTempting(')
    reward=ins(Q,'customServerAiStep');assert any(x['operand']==70 for x in reward) and any(x['operand']==50 for x in reward) and pos(reward,'.countColorsSet(')<pos(reward,'.getRewarded(')<pos(reward,'.rewardQuest(')<pos(reward,'.setRewarded(')
    payout=ins(Q,'rewardQuest');assert pos(payout,'PIGLIN_BARTER')<pos(payout,'.lootTable(')<pos(payout,'.getRandomItems(')<pos(payout,'.getEntitiesOfClass(')<pos(payout,'.trigger(')<pos(payout,'.markStructureConquered(')
    saved=ins(Q,'addAdditionalSaveData');assert any(x['operand']=='ColorFlags' for x in saved) and any(x['operand']=='Rewarded' for x in saved) and not any('randomTickDivider' in str(x['operand']) for x in saved)
    codec=ins(P+'quest/ram/QuestingRamContext','validate');assert any(x['operand']==16 for x in codec) and pos(codec,'DyeColor.getId(')<pos(codec,'Integer.bitCount(')<pos(codec,'DataResult.success(')
    reload=ins(P+'quest/QuestReloadListener','apply');assert pos(reload,'.getPath(')<pos(reload,'questing_ram')<pos(reload,'.parse(')<pos(reload,'.getOrThrow(')<pos(reload,'.setContext(')
    deer=ins(D,'mobInteract');assert pos(deer,'Animal.mobInteract(')<pos(deer,'InteractionResult.PASS')<pos(deer,'SHIKA_SENBEI')<pos(deer,'.getHealth(')<pos(deer,'.usePlayerItem(')
    heal=ins(D,'usePlayerItem');assert any(x['operand']==4.0 for x in heal) and pos(heal,'SHIKA_SENBEI')<pos(heal,'.isClientSide(')<pos(heal,'.heal(')<pos(heal,'Animal.usePlayerItem(')
    assert not any('.setHealth(' in str(x['operand']) for x in heal)
    spook=ins(P+'TinyBird','isSpooked');at=next(i for i,x in enumerate(spook) if 'Player.isHolding(' in str(x['operand']));assert int(spook[at+1]['opcode'],16)==0x99 and int(spook[at+2]['opcode'],16)==4,'held seed is positive spook predicate'
    for name in ['doPush','pushEntities']:assert [int(x['opcode'],16) for x in ins(F,name)]==[0xb1]
    assert int(ins(F,'isPushable')[0]['opcode'],16)==3 and int(ins(F,'isIgnoringBlockTriggers')[0]['opcode'],16)==4
    assert not {'addAdditionalSaveData','readAdditionalSaveData','hurt'} & {m['name'] for m in methods(F)}
    assert not any('.hurt(' in str(x['operand']) or '.setHealth(' in str(x['operand']) for c in [P+'Bird',F,P+'TinyBird',P+'Raven'] for m in methods(c) for x in m['instructions'])
    for name in ['Boar','Deer','DwarfRabbit','Squirrel','Penguin','Raven','TinyBird','Bighorn','QuestRam']:
        assert not {'hurt','doHurtTarget'} & {m['name'] for m in methods(P+name)},name
    refs=[w for p in (OUT/'reference-evidence').glob('*.json') for w in read_json(p).get('witnesses',[]) if w.get('archive_sha256') in ['8e3563a078289f0f07ee6f87f1c8651294387639c8355983ee207cb753f08b7f','d874b2aa4d511919a567ae73f13510e63e16f7318194eb2c03824cd68a59df6f']]
    raw=[c for p in (OUT/'vanilla-evidence').glob('*.json') for c in read_json(p).get('classes',[])]
    def ri(c,n):
        selected=[m['instructions'] for w in refs if w['entry']==c+'.class' for m in w.get('methods',[]) if m['name']==n]
        return selected[0] if selected else next(m['instructions'] for w in raw if w['class_name']==c for m in w['methods'] if m['name']==n)
    healnative=ri('net/minecraft/world/entity/LivingEntity','heal');assert pos(healnative,'.onLivingHeal(')<pos(healnative,'.getHealth(')<pos(healnative,'.setHealth(')
    inside=ri('net/minecraft/world/entity/Entity','checkInsideBlocks');assert pos(inside,'.isAlive(')<pos(inside,'.entityInside(') and not any('.isIgnoringBlockTriggers(' in str(x['operand']) for x in inside)
    fall=ri('net/minecraft/world/entity/LivingEntity','calculateFallDamage');assert pos(fall,'FALL_DAMAGE_IMMUNE')<pos(fall,'SAFE_FALL_DISTANCE')
    bundle=ri('net/minecraft/world/level/storage/loot/ContainerComponentManipulators$2','setContents');assert pos(bundle,'.clearItems(')<pos(bundle,'Stream.forEach(')<pos(bundle,'.toImmutable(')
    res=read_json(WORK/'twilightforest/resources.json');quest=res['data/twilightforest/twilight/quests/questing_ram.json']['data'];assert len(quest['items'])==16 and quest['reward']=='twilightforest:entities/questing_ram_rewards'
    fallset=set(res['data/minecraft/tags/entity_type/fall_damage_immune.json']['data']['values']);assert {'twilightforest:'+x for x in ['squirrel','penguin','raven','tiny_bird']}<=fallset
    assert 'twilightforest:penguin' in res['data/minecraft/tags/entity_type/freeze_immune_entity_types.json']['data']['values']
    assert old.get('semantic_corrections')==new.get('semantic_corrections') and len(new['semantic_corrections'])==2
    assert not s['damage_profiles'] and d['damage_census']['reviewed_profiles_after']==31 and d['damage_census']['remaining_profiles']==9
