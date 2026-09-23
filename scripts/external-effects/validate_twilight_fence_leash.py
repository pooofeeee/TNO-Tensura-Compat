"""Native-source ordering, producer and save/load guardrails for fence/leash review."""
from catalog_common import *


def validate_fence_leash(d,s,old,new,methods,ins,pos,target):
    from collect_twilight_fence_leash import scan_attachment,templates,ASM
    census=read_json(OUT/'twilightforest-fence-leash-attachment-census.json')
    assert census==scan_attachment(target) and not census['resource_hits']
    P='world/components/structures/lichtowerrevamp/';W=P+'LichTowerWingRoom';Q=P+'LichPerimeterFence'
    writers={(r['entry'],r['method']) for r in census['matches'] if any('.setData(' in str(i['operand']) for i in r['instructions'])}
    assert writers=={('twilightforest/'+W+'.class','putZombieTrap'),('twilightforest/'+Q+'.class','generateBoundZombie')}
    decoded=read_json(OUT/'twilightforest-fence-leash-structure-templates.json');assert decoded==templates(target)
    assert len(decoded['records'])==8
    traps=[r for r in decoded['records'] if any('zombie_trap' in (m['metadata'] or '') for m in r['markers'])]
    assert len(traps)==3
    actual=[m for r in traps for m in r['markers'] if 'zombie_trap' in (m['metadata'] or '')]
    assert len(actual)==9 and all(m['mode']=='DATA' for m in actual)
    assert sum(m['metadata']=='zombie_trap' for m in actual)==1 and sum(m['metadata']=='zombie_trap|wrought_iron_post' for m in actual)==8
    for n in range(3,8):
        r=next(r for r in decoded['records'] if r['entry'].endswith('outer_fence_'+str(n)+'.nbt'))
        posts={p['state']['Properties']['post'] for p in r['fence_posts']}
        assert ('post' in posts)==(n in (5,7))
    F='block/WroughtIronFenceBlock';I='item/WroughtIronFenceItem';E='events/EntityEvents';H='asmhooks/EntityHooks';B='asmhooks/BlockHooks'
    for c in [F,I]:assert not any(any(t in str(i['operand']) for t in ['.hurt(','.setHealth(','.addEffect(']) for m in methods(c) for i in m['instructions'])
    path=ins(F,'isPathfindable');assert len(path)==2 and int(path[0]['opcode'],16)==0x03
    shape=ins(F,'getShape');assert pos(shape,'PostState.NONE')<pos(shape,'PostState.CAPPED')<pos(shape,'.isEmpty(')<pos(shape,'Shapes.block(')
    place=ins(F,'getStateForPlacement');at=next(i for i,x in enumerate(place) if '.fenceShape(' in str(x['operand']));assert any('.above(' in str(x['operand']) for x in place[at-7:at])
    use=ins(I,'useOn');assert pos(use,'.isSecondaryUseActive(')<pos(use,'.canBeReplaced(')<pos(use,'.setBlockAndUpdate(')<pos(use,'.playSound(')<pos(use,'InteractionResult.SUCCESS')
    at=next(i for i,x in enumerate(use) if '.setBlockAndUpdate(' in str(x['operand']));assert int(use[at+1]['opcode'],16)==0x57
    assert not any('.shrink(' in str(x['operand']) or '.hurtAndBreak(' in str(x['operand']) for x in use)
    lead=ins(E,'attachLeadToWroughtFence');assert pos(lead,'Items.LEAD')<pos(lead,'WROUGHT_IRON_FENCE')<pos(lead,'PostState.NONE')<pos(lead,'.isClientSide(')<pos(lead,'.bindPlayerMobs(')<pos(lead,'.setCanceled(')<pos(lead,'InteractionResult.SUCCESS')
    at=next(i for i,x in enumerate(lead) if '.bindPlayerMobs(' in str(x['operand']));assert int(lead[at+1]['opcode'],16)==0x57
    cleanup=ins(E,'handleLeashPathingOverrides');assert pos(cleanup,'.hasData(')<pos(cleanup,'.mayBeLeashed(')<pos(cleanup,'.removeData(') and not any('.canBeLeashed(' in str(x['operand']) for x in cleanup)
    hook=ins(H,'overrideStayCloseToHolder');assert int(hook[0]['opcode'],16)==0x1a and pos(hook,'LEASH_PATHFINDER_OVERRIDE')<pos(hook,'.hasData(')
    support=ins(B,'leashFenceKnotSurvives');assert int(support[0]['opcode'],16)==0x1a and pos(support,'WROUGHT_IRON_FENCE')<pos(support,'PostState.NONE')
    for c,n in [(W,'putZombieTrap'),(Q,'generateBoundZombie')]:
        ii=ins(c,n);assert pos(ii,'EntityType.LEASH_KNOT')<pos(ii,'EntityType.ZOMBIE')<pos(ii,'.setPersistenceRequired(')<pos(ii,'.setLeashedTo(')<pos(ii,'LEASH_PATHFINDER_OVERRIDE')<pos(ii,'.setData(')<pos(ii,'.addFreshEntity(')
        assert sum('.createEntityIgnoreException(' in str(x['operand']) for x in ii)==2 and sum('.addFreshEntity(' in str(x['operand']) for x in ii)==1
        at=next(i for i,x in enumerate(ii) if '.addFreshEntity(' in str(x['operand']));assert int(ii[at+1]['opcode'],16)==0x57
        at=next(i for i,x in enumerate(ii) if '.setLeashedTo(' in str(x['operand']));assert int(ii[at-1]['opcode'],16)==0x03
        assert not any(any(t in str(x['operand']) for t in ['.hurt(','.setHealth(','.finalizeSpawn(','.setNoAi(']) for x in ii)
    bound=ins(Q,'generateBoundZombie');assert sum('.isInside(' in str(x['operand']) for x in bound)==2 and not any(int(x['opcode'],16)==0xb5 for x in bound)
    ctor=next(m['instructions'] for m in methods(Q) if m['name']=='<init>' and 'RandomSource' in m['descriptor']);assert any(x['operand']==0.25 for x in ctor) and pos(ctor,'.nextFloat(')<pos(ctor,'.filterBlocks(')<pos(ctor,'.removeIf(')<pos(ctor,'.shuffle(')
    mark=ins('world/components/structures/TwilightTemplateStructurePiece','customPostProcess');assert pos(mark,'.placeInWorld(')<pos(mark,'.filterBlocks(')<pos(mark,'StructureMode.DATA')<pos(mark,'.handleDataMarker(')
    asm=read_json(OUT/'reference-evidence/twilight-fence-leash-asm.json')['witnesses'];assert {w['entry'] for w in asm}==set(ASM)
    for w in asm:
        ops=[i['operand'] for m in w['methods'] for i in m['instructions']]
        assert 172 in ops and any('ASMUtil.findInstructions(' in str(x) for x in ops)
        if '/lead/' in w['entry']:assert any('.findFirst(' in str(x) for x in ops) and 'leashFenceKnotSurvives' in ops
        else:assert any('.forEach(' in str(x) for x in ops) and 'overrideStayCloseToHolder' in ops and 'shouldStayCloseToLeashHolder' in ops
    registration=read_json(OUT/'reference-evidence/twilight-equipment-asm.json')['witnesses']
    for c in ASM:assert any(c.rsplit('/',1)[-1][:-6]+'.<init>' in str(i['operand']) for w in registration for m in w.get('methods',[]) for i in m['instructions'])
    refs=[w for p in (OUT/'reference-evidence').glob('*.json') for w in read_json(p).get('witnesses',[]) if w.get('archive_sha256') in ['8e3563a078289f0f07ee6f87f1c8651294387639c8355983ee207cb753f08b7f','d874b2aa4d511919a567ae73f13510e63e16f7318194eb2c03824cd68a59df6f']]
    raw=[c for p in (OUT/'vanilla-evidence').glob('*.json') for c in read_json(p).get('classes',[])]
    def rm(c,n):return [m for w in refs if w['entry']==c+'.class' for m in w.get('methods',[]) if m['name']==n] or [m for w in raw if w['class_name']==c for m in w['methods'] if m['name']==n]
    def ri(c,n):return rm(c,n)[0]['instructions']
    N='net/minecraft/world/entity/';L=N+'Leashable';M=N+'Mob';K=N+'decoration/LeashFenceKnotEntity';D=N+'decoration/BlockAttachedEntity'
    may=ri(L,'mayBeLeashed');assert any('.getLeashData(' in str(x['operand']) for x in may) and not any('.canBeLeashed(' in str(x['operand']) for x in may)
    enemy=ri(M,'canBeLeashed');assert any(x['operand']=='net/minecraft/world/entity/monster/Enemy' for x in enemy)
    leash=ri(L,'tickLeash');assert pos(leash,'.restoreLeashFromSave(')<pos(leash,'.isAlive(')<pos(leash,'.handleLeashAtDistance(')<pos(leash,'.leashTooFarBehaviour(')<pos(leash,'.elasticRangeLeashBehaviour(')<pos(leash,'.closeRangeLeashBehaviour(')
    assert any(x['operand']==10.0 for x in leash) and any(x['operand']==6.0 for x in leash)
    elastic=ri(L,'legacyElasticRangeLeashBehaviour');assert sum(x['operand']==0.4 for x in elastic)==3 and any('.setDeltaMovement(' in str(x['operand']) for x in elastic)
    following=ri(N+'PathfinderMob','closeRangeLeashBehaviour');assert pos(following,'.shouldStayCloseToLeashHolder(')<pos(following,'.isPanicking(')<pos(following,'.enableControlFlag(')<pos(following,'.moveTo(')
    survives=ri(K,'survives');assert sum(int(x['opcode'],16)==0xac for x in survives)==1 and any('BlockTags.FENCES' in str(x['operand']) for x in survives)
    tick=ri(D,'tick');assert any(x['operand']==100 for x in tick) and pos(tick,'.survives(')<pos(tick,'.discard(')<pos(tick,'.dropItem(')
    assert len(ri(D,'thunderHit'))==1
    spawn=ri('net/minecraft/server/level/WorldGenRegion','addFreshEntity');assert pos(spawn,'.isSpawnCancelled(')<pos(spawn,'.getChunk(')<pos(spawn,'.addEntity(')
    proto=next(m['instructions'] for m in rm('net/minecraft/world/level/chunk/ProtoChunk','addEntity') if any('.isPassenger(' in str(x['operand']) for x in m['instructions']));assert pos(proto,'.isPassenger(')<pos(proto,'.save(')<pos(proto,'.addEntity(')
    save=ri(N+'Entity','saveWithoutId');assert any('.serializeAttachments(' in str(x['operand']) for x in save)
    load=ri(N+'Entity','load');assert any('.deserializeAttachments(' in str(x['operand']) for x in load)
    assert any('.writeLeashData(' in str(x['operand']) for x in ri(M,'addAdditionalSaveData')) and any('.readLeashData(' in str(x['operand']) for x in ri(M,'readAdditionalSaveData'))
    restore=ri(L,'restoreLeashFromSave');anchor=pos(restore,'.getOrCreateKnot(');assert any(x['offset']>anchor and '.setLeashedTo(' in str(x['operand']) for x in restore) and any(x['operand']==100 for x in restore)
    resources=read_json(WORK/'twilightforest/resources.json');rid='twilightforest:wrought_iron_fence'
    assert rid in resources['data/minecraft/tags/block/walls.json']['data']['values']
    for entry in ['data/alexscaves/tags/block/ferromagnetic_blocks.json','data/alexscaves/tags/item/ferromagnetic_items.json']:assert rid in resources[entry]['data']['values']
    tags={r['entry']:r['data'] for r in read_json(OUT/'vanilla-evidence/twilight-fence-leash.json')['resources']}
    for entry in ['data/minecraft/tags/block/fences.json','data/minecraft/tags/block/wooden_fences.json']:
        assert rid not in tags[entry]['values']+resources.get(entry,{}).get('data',{}).get('values',[])
    assert old.get('semantic_corrections')==new.get('semantic_corrections') and not s['damage_profiles'] and d['damage_census']['reviewed_profiles_after']==40
