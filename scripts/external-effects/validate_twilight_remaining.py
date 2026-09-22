"""Later Twilight subset integrity; preserves R2f7 and every published subset input."""
from collections import Counter
from catalog_common import *
from classfile import ClassFile
from validate_twilight_yeti_queen import validate_yeti_queen

START='cb929fb7833eb27ddc3c16126f281cc62247421a'


def validate_remaining():
    previous=validate_yeti_queen();prefix='docs/benchmarks/external-effects-catalog/'
    mutable={prefix+x for x in ['behavior-primitives.json','delivery-path-matrix.json','effect-catalog.json','effect-sources.json','mod-completion-ledger.json','mod-reviews/twilightforest.json','research-decision.json','vanilla-comparison.json','twilightforest-owner-table.md']}
    mutable.add('scripts/external-effects/validate.py')
    protected=[p for p in git('ls-tree','-r','--name-only',START,'--',prefix,'scripts/external-effects/').splitlines() if p not in mutable]
    for p in protected:
        old=subprocess.check_output(['git','show',START+':'+p],cwd=ROOT)
        assert (ROOT/p).read_bytes().replace(b'\r\n',b'\n')==old.replace(b'\r\n',b'\n'),p
    witnesses={}
    for p in (OUT/'native-evidence').glob('*.json'):
        for w in read_json(p).get('witnesses',[]):
            if w.get('mod_key')=='twilightforest' and w['entry'].endswith('.class'):witnesses.setdefault(w['entry'],[]).extend(w['methods'])
    def methods(c):return witnesses['twilightforest/'+c+'.class']
    def ins(c,m):return next(x['instructions'] for x in methods(c) if x['name']==m)
    def pos(i,t):return next(x['offset'] for x in i if t in str(x['operand']))
    target=next(t for t in read_json(OUT/'jar-inventory.json')['targets'] if t['key']=='twilightforest')
    assert sha256(target['path'])==target['sha256']
    results=[]
    for sp in sorted((OUT/'semantic-sections').glob('twilightforest-*.json')):
        s=read_json(sp)
        if not s.get('remaining_content_subsection'):continue
        r=s['review_input'];assert sha256(OUT/r['evidence_file'])==r['sha256'];d=read_json(OUT/r['evidence_file'])
        assert s['counts']==d['expected_counts'] and s['semantic_closure']==d['facts']
        assert s['subsection_decision']==d['decision'] and all(s['closure_checklist'].values())
        assert set(s['closure_checklist'])==set(d['closure_checklist'])
        assert Counter(e['primary_classification'] for e in s['effects'])==s['counts']['classification_totals']
        assert len(s['effects'])==s['counts']['mechanic_packages'] and len(s['paths'])==s['counts']['delivery_cases']
        for e,row in zip(s['effects'],d['packages']):
            assert e['id']==row['id'] and e['actual_behavior']==[d['facts'][k] for k in row['facts']]
            assert e['alternate_sources'] and e['primary_test_source'] and e['components']
            assert e['components'][0]['numerical_parameters']==row['parameters'] and e['components'][0]['binary_parameters']==row['gates']
        for p,row in zip(s['paths'],d['paths']):
            assert p['id']==row['id'] and p['native_delivery']==' '.join(d['facts'][k] for k in row['facts'])
            assert p['setup'] and p['future_controls'] and set(p['labels'])<=set(DELIVERIES)
        old=read_json(OUT/d['previous_draft']);new=read_json(OUT/('partial-drafts/twilightforest-'+d['checkpoint_short']+'-partial.json'))
        assert new['effects']==old['effects']+s['effects'] and new['paths']==old['paths']+s['paths']
        assert len({e['id'] for e in new['effects']})==len(new['effects']) and len({p['id'] for p in new['paths']})==len(new['paths'])
        with zipfile.ZipFile(target['path']) as jar:
            for c in d['full_classes']:
                actual={(m['name'],m['descriptor']) for m in ClassFile(jar.read('twilightforest/'+c+'.class')).methods}
                assert actual=={(m['name'],m['descriptor']) for m in methods(c)},c
        if d['slug']=='ranged-mobs':
            from collect_twilight_ranged_mobs import scan_callers,FIELDS
            scan=read_json(OUT/'twilightforest-ranged-mobs-caller-scan.json');assert scan==scan_callers(target)
            runtime=[x for x in scan['hits'] if '/data/' not in x['entry'] and '/init/' not in x['entry']]
            assert Counter(x['entry'] for x in runtime)==Counter({'twilightforest/entity/monster/FireBeetle.class':2,'twilightforest/entity/projectile/NatureBolt.class':1,'twilightforest/entity/projectile/TomeBolt.class':2,'twilightforest/entity/projectile/IceSnowball.class':1})
            profiles={p['type']:p for p in s['damage_profiles']};assert set(profiles)=={'twilightforest:'+f.lower() for f in FIELDS}
            assert all(p['status']=='USED' for p in profiles.values())
            for name in ['leaf_brain','lost_words','schooled']:
                assert {'minecraft:bypasses_armor','minecraft:bypasses_shield','minecraft:is_projectile','neoforge:is_magic'}<=set(profiles['twilightforest:'+name]['tags'])
            assert 'minecraft:bypasses_armor' not in profiles['twilightforest:snowball_fight']['tags']
            assert 'minecraft:is_freezing' not in profiles['twilightforest:snowball_fight']['tags']
            M='entity/monster/';P='entity/projectile/';G='entity/ai/goal/BreathAttackGoal'
            use=ins(G,'canUse');assert any('.getLastHurtByMob(' in str(x['operand']) for x in use) and not any('.getTarget(' in str(x['operand']) for x in use)
            select=ins(G,'getHeadLookTarget');assert not any('ClipContext' in str(x['operand']) for x in select)
            winter=ins(M+'WinterWolf','doBreathAttack');assert any('.mobAttack(' in str(x['operand']) for x in winter) and not any('TFDamageTypes' in str(x['operand']) for x in winter)
            fire=ins(M+'FireBeetle','doBreathAttack');assert pos(fire,'.fireImmune(')<pos(fire,'.hurt(')<pos(fire,'.igniteForSeconds(')
            assert not any('.igniteForSeconds(' in str(x['operand']) for x in ins(M+'FireBeetle','doHurtTarget'))
            for c in ['NatureBolt','TomeBolt']:
                hit=ins(P+c,'onHitEntity');assert pos(hit,'.hurt(')<pos(hit,'.addEffect(')
            for c in ['SlimeProjectile','IceSnowball']:
                hit=ins(P+c,'onHitEntity');i=next(n for n,x in enumerate(hit) if '.hurt(' in str(x['operand']));assert int(hit[i+1]['opcode'],16)==0x57
                hurt=ins(P+c,'hurt');assert pos(hurt,'TFThrowable.hurt(')<pos(hurt,'.die(')
                assert not any('.addEffect(' in str(x['operand']) for x in hit)
            for c in ['NatureBolt','TomeBolt','SlimeProjectile','IceSnowball']:assert not {'addAdditionalSaveData','readAdditionalSaveData'} & {m['name'] for m in methods(P+c)}
            death=ins(M+'UnstableIceCore','tickDeath');assert pos(death,'.explode(')<pos(death,'.transformBlocks(')<pos(death,'BaseIceMob.tickDeath(')
            assert not any('.setHealth(' in str(x['operand']) for x in death)
            mist=ins(M+'MistWolf','doHurtTarget');assert pos(mist,'HostileWolf.doHurtTarget(')<pos(mist,'.getMaxLocalRawBrightness(')<pos(mist,'.addEffect(')
            assert d['damage_census']['reviewed_profiles_after']==22 and d['damage_census']['remaining_profiles']==18
        if d['slug']=='mounted-mobs':
            from collect_twilight_mounted_mobs import scan_callers
            scan=read_json(OUT/'twilightforest-mounted-mobs-caller-scan.json');assert scan==scan_callers(target)
            runtime=[x for x in scan['hits'] if '/data/' not in x['entry'] and '/init/' not in x['entry']]
            assert Counter((x['entry'].split('/')[-1],x['method']) for x in runtime)==Counter({('Yeti.class','hurt'):1,('Yeti.class','readAdditionalSaveData'):1,('PinchBeetle.class','doHurtTarget'):1,('HeavySpearAttackGoal.class','tick'):1})
            p=s['damage_profiles'][0];assert p['type']=='twilightforest:clamped' and p['status']=='USED'
            assert set(p['tags'])=={'minecraft:no_knockback','neoforge:is_physical'}
            M='entity/monster/';G='entity/ai/goal/'
            upper=ins(M+'UpperGoblinKnight','hurt');assert pos(upper,'.getEntity(')<pos(upper,'.takeHitOnShield(')<pos(upper,'Monster.hurt(')
            assert not any('.getDirectEntity(' in str(x['operand']) for x in upper)
            for c in ['UpperGoblinKnight','LowerGoblinKnight']:
                h=ins(M+c,'hurt');assert pos(h,'.breakArmor(')<pos(h,'Monster.hurt(')
            shield=ins(M+'UpperGoblinKnight','takeHitOnShield');assert pos(shield,'AxeItem')<pos(shield,'.damageShield(')<pos(shield,'.knockback(')
            cl=ins(M+'UpperGoblinKnight','<clinit>');assert any('ADD_MULTIPLIED_BASE' in str(x['operand']) for x in cl)
            assert any(x['operand']==12.0 for x in cl)
            heavy=ins(G+'HeavySpearAttackGoal','tick');assert any(x['operand']==25 for x in heavy)
            assert 'requiresUpdateEveryTick' not in {m['name'] for m in methods(G+'HeavySpearAttackGoal')}
            area=ins(M+'UpperGoblinKnight','landHeavySpearAttack');assert any('Monster.doHurtTarget(' in str(x['operand']) for x in area)
            pinch=ins(M+'PinchBeetle','doHurtTarget');assert pos(pinch,'.startRiding(')<pos(pinch,'TFDamageTypes.CLAMPED')<pos(pinch,'.properlyApplyCustomDamageSource(')
            boat=ins(M+'PinchBeetle','startRiding');assert any('Boat.kill(' in str(x['operand']) for x in boat) and not any('.hurt(' in str(x['operand']) for x in boat)
            yh=ins(M+'Yeti','hurt');assert pos(yh,'.setAngry(')<pos(yh,'Monster.hurt(')
            assert s['effects'][-1]['reuses_protected_effect_ids']==['twilightforest:alpha_yeti_throw','twilightforest:alpha_yeti_thrown_fall']
            assert d['damage_census']['reviewed_profiles_after']==23 and d['damage_census']['remaining_profiles']==17
        if d['slug']=='chain':
            from collect_twilight_chain import scan_callers,scan_vanilla_callers
            scan=read_json(OUT/'twilightforest-chain-caller-scan.json');assert scan==scan_callers(target)
            vanilla=read_json(OUT/'twilightforest-chain-vanilla-caller-scan.json');assert vanilla==scan_vanilla_callers()
            assert {(x['class_name'],x['method']) for x in vanilla['hits']}=={('net/minecraft/server/level/ServerPlayerGameMode','handleBlockBreakAction'),('net/minecraft/world/entity/projectile/AbstractArrow','hitBlockEnchantmentEffects'),('net/minecraft/world/entity/projectile/ThrownTrident','hitBlockEnchantmentEffects')}
            refs=read_json(OUT/'reference-evidence/twilight-chain-244.json')['witnesses']
            mode=next(w for w in refs if w['entry'].endswith('/ServerPlayerGameMode.class'))
            mining=next(m['instructions'] for m in mode['methods'] if m['name']=='handleBlockBreakAction')
            assert pos(mining,'onLeftClickBlock(')<pos(mining,'.isCreative(')<pos(mining,'EnchantmentHelper.onHitBlock(')<pos(mining,'.getUseBlock(')
            assert pos(mining,'.getMainHandItem(')<pos(mining,'EnchantmentHelper.onHitBlock(')
            runtime=[x for x in scan['hits'] if 'TFDamageTypes.SPIKED' in str(x['instruction']['operand']) and '/data/' not in x['entry'] and '/init/' not in x['entry']]
            assert {(x['entry'],x['method']) for x in runtime}=={('twilightforest/entity/monster/BlockChainGoblin.class','doHurtTarget'),('twilightforest/entity/projectile/ChainBlock.class','onHitEntity')}
            p=s['damage_profiles'][0];assert p['type']=='twilightforest:spiked' and p['status']=='USED' and p['tags']==['neoforge:is_physical']
            M='entity/monster/BlockChainGoblin';P='entity/projectile/ChainBlock';I='item/ChainBlockItem';E='enchantment/SmashBlocksEffect'
            melee=ins(M,'doHurtTarget');assert pos(melee,'TFDamageTypes.SPIKED')<pos(melee,'.blockL')<pos(melee,'.getIndirectEntityDamageSource(')
            collision=ins(M,'applyBlockCollision');assert pos(collision,'.push(L')<pos(collision,'Monster.doHurtTarget(')<pos(collision,'.push(DDD)')
            assert not any('TFDamageTypes' in str(x['operand']) for x in collision)
            hit=ins(P,'onHitEntity');assert pos(hit,'.hurtAndBreak(')<pos(hit,'.disableShield(')<pos(hit,'.hurt(')<pos(hit,'.setIsReturning(')
            assert not any('.doPostAttackEffects(' in str(x['operand']) for x in hit)
            assert not any(int(x['opcode'],16)==0xb4 and '.hitEntity' in str(x['operand']) for x in hit)
            block=ins(P,'onHitBlock');assert pos(block,'.bounce(')<pos(block,'EnchantmentHelper.onHitBlock(')
            smash=ins(E,'apply');assert pos(smash,'BreakEvent')<pos(smash,'.destroyBlock(')<pos(smash,'.getBlockEntity(')<pos(smash,'.playerDestroy(')<pos(smash,'.setBlocksSmashed(')
            assert not any('.vulnerableBlocks(' in str(x['operand']) for x in smash)
            setters=[x for x in scan['hits'] if '.setBlocksSmashed' in str(x['instruction']['operand'])]
            assert len(setters)==1 and setters[0]['entry']=='twilightforest/enchantment/SmashBlocksEffect.class'
            assert 'canPerformAction' not in {m['name'] for m in methods(I)}
            assert any('ItemStack.parseOptional(' in str(x['operand']) for x in ins(P,'readAdditionalSaveData'))
            for name in ['readAdditionalSaveData','addAdditionalSaveData']:
                assert not any('.HAND' in str(x['operand']) or '.getHand(' in str(x['operand']) or '.setHand(' in str(x['operand']) for x in ins(P,name))
            assert d['damage_census']['reviewed_profiles_after']==24 and d['damage_census']['remaining_profiles']==16
        if d['slug']=='giants-tools':
            from collect_twilight_giants_tools import scan_callers
            scan=read_json(OUT/'twilightforest-giants-tools-caller-scan.json');assert scan==scan_callers(target)
            runtime=[x for x in scan['hits'] if 'TFDamageTypes.ANTL' in str(x['instruction']['operand']) and '/data/' not in x['entry'] and '/init/' not in x['entry']]
            assert len(runtime)==1 and runtime[0]['entry']=='twilightforest/entity/monster/GiantMiner.class' and runtime[0]['method']=='doHurtTarget'
            p=s['damage_profiles'][0];assert p['type']=='twilightforest:ant' and p['status']=='USED' and p['tags']==['neoforge:is_physical']
            M='entity/monster/';I='item/';EV='events/ToolEvents'
            assert 'doHurtTarget' not in {m['name'] for m in methods(M+'ArmoredGiant')}
            assert not {'hurt','tickDeath','customServerAiStep'} & {m['name'] for m in methods(M+'GiantMiner')}
            for method in ['enchantSpawnedWeapon','enchantSpawnedArmor']:assert len(ins(M+'GiantMiner',method))==1
            for c in ['GiantPickItem','GiantSwordItem']:
                attrs=ins(I+c,'createGiantAttributes');assert any(x['operand']==2.5 for x in attrs) and any('EquipmentSlotGroup.HAND' in str(x['operand']) for x in attrs)
            speed=ins(I+'GiantPickItem','getDestroySpeed');assert sum(x['operand']==64.0 for x in speed)==2
            area=ins(EV,'handleGiantPickaxeMining');assert pos(area,'.setCanceled(')<pos(area,'ServerPlayerGameMode.destroyBlock(')
            assert sum('ServerPlayerGameMode.destroyBlock(' in str(x['operand']) for x in area)==2
            assert not any('.hurt(' in str(x['operand']) for x in area)
            extra=ins(EV,'damageNonMazebreakerToolsMore');assert any(x['operand']==16 for x in extra) and any('MazebreakerPickItem' in str(x['operand']) for x in extra)
            maze=ins(I+'MazebreakerPickItem','getDestroySpeed');assert any(x['operand']==16.0 for x in maze)
            assert d['damage_census']['reviewed_profiles_after']==25 and d['damage_census']['remaining_profiles']==15
        if d['slug']=='arthropods':
            from collect_twilight_arthropods import scan_callers
            scan=read_json(OUT/'twilightforest-arthropods-caller-scan.json');assert scan==scan_callers(target) and scan['hits']==[]
            M='entity/monster/';B='block/InfestedTowerwoodBlock'
            assert not s['damage_profiles'] and s['counts']['new_custom_types_resolved']==0
            king=ins(M+'KingSpider','finalizeSpawn');assert pos(king,'Spider.finalizeSpawn(')<pos(king,'SkeletonDruid.finalizeSpawn(')<pos(king,'.getPassengers(')<pos(king,'.startRiding(')
            assert not any('.ejectPassengers(' in str(x['operand']) for x in king)
            assert 'registerGoals' not in {m['name'] for m in methods(M+'KingSpider')}
            assert len(ins(M+'TowerBroodling','summonJockey'))==1
            swarm=ins(M+'SwarmSpider','doHurtTarget');assert pos(swarm,'.nextInt(')<pos(swarm,'Spider.doHurtTarget(')
            mosquito=ins(M+'MosquitoSwarm','doHurtTarget');assert pos(mosquito,'Monster.doHurtTarget(')<pos(mosquito,'.addEffect(')
            borer=ins(M+'TowerwoodBorer','hurt');assert pos(borer,'.isInvulnerableTo(')<pos(borer,'.getEntity(')<pos(borer,'.notifyHurt(')<pos(borer,'Monster.hurt(')
            assert not any('.getDirectEntity(' in str(x['operand']) for x in borer)
            goal=M+'TowerwoodBorer$SummonBorersGoal';assert 'requiresUpdateEveryTick' not in {m['name'] for m in methods(goal)}
            release=ins(goal,'tick');assert pos(release,'.destroyBlock(')<pos(release,'.setBlock(')<pos(release,'.nextBoolean(')
            assert not any('.addFreshEntity(' in str(x['operand']) for x in release)
            hide=ins(M+'TowerwoodBorer$HideInTowerwoodGoal','start');assert pos(hide,'.setBlock(')<pos(hide,'.discard(')
            block=ins(B,'spawnAfterBreak');assert pos(block,'RULE_DOBLOCKDROPS')<pos(block,'EnchantmentHelper.hasTag(')<pos(block,'.create(')<pos(block,'.addFreshEntity(')
            assert not any('.finalize' in str(x['operand']) for x in block)
            assert {m['name'] for m in methods(B)}=={'<init>','spawnAfterBreak'}
            tags={w['entry']:w['data'] for w in read_json(OUT/'reference-evidence/twilight-arthropod-tags-244.json')['witnesses']}
            assert '#neoforge:is_poison' in tags['data/minecraft/tags/damage_type/always_triggers_silverfish.json']['values']
            assert 'neoforge:poison' in tags['data/neoforge/tags/damage_type/is_poison.json']['values']
            assert d['damage_census']['reviewed_profiles_after']==25 and d['damage_census']['remaining_profiles']==15
        if d['slug']=='tactical-mobs':
            from collect_twilight_tactical_mobs import scan_callers
            scan=read_json(OUT/'twilightforest-tactical-mobs-caller-scan.json');assert scan==scan_callers(target)
            assert [r['entry'] for r in scan['boggard_class_references']]==['twilightforest/entity/monster/Boggard.class']
            assert not any('boggard' in p['id'] for p in s['paths'])
            runtime=[h for h in scan['hits'] if 'TFDamageTypes.THROWN_BLOCKL' in str(h['instruction']['operand']) and '/init/' not in h['entry'] and '/data/' not in h['entry']]
            assert len(runtime)==1 and runtime[0]['entry']=='twilightforest/entity/projectile/ThrownBlock.class'
            p=s['damage_profiles'][0];assert p['type']=='twilightforest:thrown_block' and p['tags']==['minecraft:damages_helmet','minecraft:is_projectile','neoforge:is_physical']
            M='entity/monster/';G='entity/ai/goal/';P='entity/projectile/ThrownBlock'
            light=ins(G+'RedcapLightTNTGoal','tick');assert pos(light,'.onCaughtFire(')<pos(light,'.setBlock(')
            assert not any('.hurtAndBreak(' in str(x['operand']) for x in light)
            plant=ins(G+'RedcapPlantTNTGoal','start');assert pos(plant,'.isEmptyBlock(')<pos(plant,'.shrink(')<pos(plant,'.setBlockAndUpdate(')
            assert not any('.setFlags(' in str(x['operand']) for x in ins(G+'RedcapPlantTNTGoal','<init>'))
            assert not any('.setFlags(' in str(x['operand']) for x in ins(G+'FlockToSameKindGoal','<init>'))
            pickup=ins(M+'Kobold','pickUpItem');assert pos(pickup,'.canHoldItem(')<pos(pickup,'.setItemSlot(')<pos(pickup,'.setTarget(')
            assert not any('.heal(' in str(x['operand']) or '.setHealth(' in str(x['operand']) for x in ins(M+'Kobold','aiStep'))
            assert 'canContinueToUse' not in {m['name'] for m in methods(M+'Kobold$KoboldAttackPlayerTarget')}
            troll=ins(M+'Troll','tick');assert pos(troll,'BASE_STONE_OVERWORLD')<pos(troll,'.removeBlock(')<pos(troll,'.setHasRock(')<pos(troll,'ThrownBlock.<init>')
            assert not any('canEntityGrief' in str(x['operand']) for x in troll)
            hit=ins(P,'onHitEntity');assert pos(hit,'monster/Troll')<pos(hit,'TFDamageTypes.getDamageSource(')<pos(hit,'.hurt(')<pos(hit,'.discard(')
            ci=next(n for n,x in enumerate(hit) if 'TFDamageTypes.getDamageSource(' in str(x['operand']));assert str(hit[ci]['operand']).endswith('(Lnet/minecraft/world/level/Level;Lnet/minecraft/resources/ResourceKey;[Lnet/minecraft/world/entity/EntityType;)Lnet/minecraft/world/damagesource/DamageSource;')
            assert int(hit[ci-2]['opcode'],16)==0x03 and hit[ci-1]['operand']=='net/minecraft/world/entity/EntityType'
            i=next(n for n,x in enumerate(hit) if '.hurt(' in str(x['operand']));assert int(hit[i+1]['opcode'],16)==0x57
            read=ins(M+'Troll','readAdditionalSaveData');assert pos(read,'.setHasRock(')<pos(read,'NbtUtils.readBlockState(')
            assert not any('.contains(' in str(x['operand']) for x in read)
            assert d['damage_census']['reviewed_profiles_after']==26 and d['damage_census']['remaining_profiles']==14
        if d['slug']=='constructs-slimes':
            from collect_twilight_constructs_slimes import scan_callers
            scan=read_json(OUT/'twilightforest-constructs-slimes-caller-scan.json');assert scan==scan_callers(target)
            world={(h['entry'].split('/')[-1],h['method']) for h in scan['hits'] if '/world/' in h['entry']}
            assert world=={('DarkTowerStructure.class','buildDarkTowerConfig'),('LabyrinthStructure.class','buildLabyrinthConfig'),('AuroraPalaceStructure.class','buildAuroraPalaceConfig'),('DarkTowerWingComponent.class','decorateSpawner')}
            assert not any(any(f in str(h['instruction']['operand']) for f in ['TFEntities.ADHERENT','TFEntities.HARBINGER_CUBE']) for h in scan['hits'] if '/world/' in h['entry'])
            M='entity/monster/'
            golem=ins(M+'CarminiteGolem','doHurtTarget');assert pos(golem,'Monster.doHurtTarget(')<pos(golem,'.push(')
            size=ins(M+'MazeSlime','setSize');assert pos(size,'Slime.setSize(')<pos(size,'.addOrReplacePermanentModifier(')<pos(size,'.setHealth(')
            cl=ins(M+'MazeSlime','<clinit>');assert any('ADD_MULTIPLIED_BASE' in str(x['operand']) for x in cl)
            contact=ins(M+'MazeSlime','isDealsDamage');assert [int(x['opcode'],16) for x in contact]==[0x04,0xac]
            equip=ins(M+'SnowGuardian','populateDefaultEquipmentSlots');assert sum('.setItemSlot(' in str(x['operand']) for x in equip)==3
            assert not any('EquipmentSlot.'+slot in str(x['operand']) for slot in ['FEET','LEGS'] for x in equip)
            refs=read_json(OUT/'reference-evidence/twilight-constructs-slimes-244.json')['witnesses']
            slime=next(w for w in refs if w['entry']=='net/minecraft/world/entity/monster/Slime.class')
            read=next(m['instructions'] for m in slime['methods'] if m['name']=='readAdditionalSaveData');assert pos(read,'.setSize(')<pos(read,'.readAdditionalSaveData(')
            remove=next(m['instructions'] for m in slime['methods'] if m['name']=='remove');assert pos(remove,'.onMobSplit(')<pos(remove,'.forEach(')<pos(remove,'.remove(')
            bolt=ins(M+'Adherent','performRangedAttack');assert any('NatureBolt.<init>' in str(x['operand']) for x in bolt)
            goals=ins(M+'HarbingerCube','registerGoals');assert not any(any(g in str(x['operand']) for g in ['MeleeAttackGoal','RangedAttackGoal']) for x in goals)
            assert 'doHurtTarget' not in {m['name'] for m in methods(M+'HarbingerCube')}
            assert not s['damage_profiles'] and d['damage_census']['reviewed_profiles_after']==26 and d['damage_census']['remaining_profiles']==14
        if d['slug']=='restless-mobs':
            from collect_twilight_restless_mobs import scan_callers
            scan=read_json(OUT/'twilightforest-restless-mobs-caller-scan.json');assert scan==scan_callers(target)
            world={h['entry'].split('/')[-1] for h in scan['hits'] if '/world/' in h['entry']}
            assert world=={'GraveyardFeature.class','HollowHillComponent.class','HollowHillStructure.class','LabyrinthStructure.class','LichTowerStructure.class','MazeRoomSpawnerChestsComponent.class'}
            M='entity/monster/';G='entity/ai/goal/'
            hit=ins(M+'Wraith','doHurtTarget');assert pos(hit,'TFDamageTypes.HAUNT')<pos(hit,'.hurt(')<pos(hit,'FlyingMob.doHurtTarget(')
            i=next(n for n,x in enumerate(hit) if '.hurt(' in str(x['operand']));assert int(hit[i+1]['opcode'],16)==0x57
            h=ins(M+'Wraith','hurt');assert pos(h,'FlyingMob.hurt(')<pos(h,'.getEntity(')<pos(h,'.setTarget(')
            attack=ins(G+'SimplifiedAttackGoal','checkAndPerformAttack');assert pos(attack,'.hasLineOfSight(')<pos(attack,'.adjustedTickDelay(')<pos(attack,'.doHurtTarget(')
            assert not any('.setFlags(' in str(x['operand']) for x in ins(G+'SimplifiedAttackGoal','<init>'))
            assert 'canContinueToUse' not in {m['name'] for m in methods(G+'SimplifiedAttackGoal')}
            assert not {'addAdditionalSaveData','readAdditionalSaveData'} & {m['name'] for m in methods(M+'Minotaur')}
            assert sum('.setItemSlot(' in str(x['operand']) for x in ins(M+'Minotaur','populateDefaultEquipmentSlots'))==2
            rise=ins(M+'RisingZombie','aiStep');assert pos(rise,'Monster.aiStep(')<pos(rise,'.getNearestPlayer(')<pos(rise,'.convertTo(')<pos(rise,'.setHealth(')
            veto=ins(M+'RisingZombie','isInvulnerableTo');assert any('DamageTypes.IN_WALL' in str(x['operand']) for x in veto) and not any('.isInvulnerableTo(' in str(x['operand']) for x in veto)
            assert not {'addAdditionalSaveData','readAdditionalSaveData','doHurtTarget','registerGoals'} & {m['name'] for m in methods(M+'RisingZombie')}
            refs=read_json(OUT/'reference-evidence/vv-loader-244.json')['witnesses'];mob=next(w for w in refs if w['entry']=='net/minecraft/world/entity/Mob.class')
            conv=next(m['instructions'] for m in mob['methods'] if m['name']=='convertTo');assert pos(conv,'.create(')<pos(conv,'.copyAndClear(')<pos(conv,'.addFreshEntity(')<pos(conv,'.discard(')
            assert not any('.finalizeSpawn(' in str(x['operand']) or '.addEffect(' in str(x['operand']) for x in conv)
            ids={e['id'] for e in new['effects']}
            assert all(i in ids for e in s['effects'] for i in e.get('reuses_protected_effect_ids',[]))
            assert not s['damage_profiles'] and d['damage_census']['reviewed_profiles_after']==26 and d['damage_census']['remaining_profiles']==14
        if d['slug']=='summon-resources':
            from collect_twilight_summon_resources import scan_callers
            scan=read_json(OUT/'twilightforest-summon-resources-caller-scan.json');assert scan==scan_callers(target)
            runtime=[h for h in scan['hits'] if 'TFDamageTypes.EXPIRED' in str(h['instruction']['operand']) and '/data/' not in h['entry'] and '/init/' not in h['entry']]
            assert len(runtime)==1 and runtime[0]['entry']=='twilightforest/entity/monster/LoyalZombie.class' and runtime[0]['method']=='aiStep'
            assert not any('/world/' in h['entry'] and 'TFEntities.LOYAL_ZOMBIE' in str(h['instruction']['operand']) for h in scan['hits'])
            M='entity/monster/LoyalZombie';W='item/ZombieWandItem';R='enchantment/RechargeScepterEffect';C='item/recipe/ScepterRepairRecipe'
            hit=ins(M,'doHurtTarget');assert pos(hit,'.mobAttack(')<pos(hit,'.hurt(')<pos(hit,'.push(')
            assert not any('getAttribute' in str(x['operand']) or 'EnchantmentHelper' in str(x['operand']) for x in hit)
            expire=ins(M,'aiStep');assert pos(expire,'.getEffect(')<pos(expire,'TFDamageTypes.EXPIRED')<pos(expire,'.hurt(')<pos(expire,'TamableAnimal.aiStep(')
            i=next(n for n,x in enumerate(expire) if '.hurt(' in str(x['operand']));assert int(expire[i+1]['opcode'],16)==0x57
            feed=ins(M,'interactAt');assert pos(feed,'.removeEffect(')<pos(feed,'.addEffect(')<pos(feed,'.heal(')<pos(feed,'.consume(')
            assert not any('.setAge(' in str(x['operand']) for x in ins(M,'setBaby'))
            use=ins(W,'use');assert pos(use,'.noCollision(')<pos(use,'.setOwnerUUID(')<pos(use,'.setBaby(')<pos(use,'.addFreshEntity(')<pos(use,'hurtButDontBreak(')
            assert not any('finalizeSpawn' in str(x['operand']) for x in use)
            charge=ins('util/TFItemStackUtils','hurtButDontBreak');assert pos(charge,'.damageItem(')<pos(charge,'.processDurabilityChange(')<pos(charge,'.setDamageValue(')
            assert not any('.shrink(' in str(x['operand']) for x in charge)
            recharge=ins(R,'applyRecharge');assert pos(recharge,'.getAllRecipesFor(')<pos(recharge,'TFItems.EXANIMATE_ESSENCE')<pos(recharge,'Ingredient.test(')
            match=ins(C,'matches');assert any('.stackedContents(' in str(x['operand']) for x in match) and any('StackedContents.canCraft(' in str(x['operand']) for x in match)
            refs=read_json(OUT/'reference-evidence/twilight-summon-resources-244.json')['witnesses']
            ingredient=next(w for w in refs if w['entry']=='net/minecraft/world/item/crafting/Ingredient.class');stackids=next(m['instructions'] for m in ingredient['methods'] if m['name']=='getStackingIds');assert any('StackedContents.getStackingIndex(' in str(x['operand']) for x in stackids) and not any('.test(' in str(x['operand']) for x in stackids)
            raw=read_json(OUT/'vanilla-evidence/twilight-summon-resources.json')['classes'];stacked=next(w for w in raw if w['class_name']=='net/minecraft/world/entity/player/StackedContents');idx=next(m['instructions'] for m in stacked['methods'] if m['name']=='getStackingIndex');assert any('.getItem(' in str(x['operand']) for x in idx) and not any('component' in str(x['operand']).lower() for x in idx)
            profile=s['damage_profiles'][0];assert profile['type']=='twilightforest:expired' and set(profile['tags'])=={'minecraft:always_most_significant_fall','minecraft:bypasses_armor','minecraft:bypasses_invulnerability','minecraft:bypasses_resistance','minecraft:bypasses_shield','minecraft:bypasses_wolf_armor','neoforge:is_technical'}
            protection=read_json(OUT/'vanilla-evidence/twilight-summon-protection.json')['resources'][0]['data'];assert protection['effects']['minecraft:damage_protection'][0]['requirements']['predicate']['tags']==[{'expected':False,'id':'minecraft:bypasses_invulnerability'}]
            assert d['damage_census']['reviewed_profiles_after']==27 and d['damage_census']['remaining_profiles']==13
        if d['slug']=='scepter-payloads':
            from collect_twilight_scepter_payloads import scan_callers
            scan=read_json(OUT/'twilightforest-scepter-payloads-caller-scan.json');assert scan==scan_callers(target)
            runtime={(h['entry'],h['method']) for h in scan['hits'] if 'TFDamageTypes.LIFEDRAIN' in str(h['instruction']['operand']) and '/data/' not in h['entry'] and '/init/' not in h['entry']}
            assert runtime=={('twilightforest/item/LifedrainScepterItem.class','onUseTick')}
            producers={(h['entry'],h['method']) for h in scan['hits'] if any(x in str(h['instruction']['operand']) for x in ['FortificationShieldAttachment.setShields','FortificationShieldAttachment.addShields'])}
            assert producers=={('twilightforest/item/FortificationWandItem.class','use'),('twilightforest/command/ShieldCommand.class','add'),('twilightforest/command/ShieldCommand.class','set')}
            A='components/entity/FortificationShieldAttachment';D='item/LifedrainScepterItem';E='events/CapabilityEvents'
            use=ins('item/FortificationWandItem','use');assert pos(use,'.setShields(')<pos(use,'hurtButDontBreak(')<pos(use,'.addCooldown(')
            incoming=ins(E,'absorbShieldHits');assert pos(incoming,'BYPASSES_ARMOR')<pos(incoming,'.shieldsLeft(')<pos(incoming,'.breakShield(')<pos(incoming,'.setCanceled(')
            assert not any('BYPASSES_SHIELD' in str(x['operand']) or '.getAmount(' in str(x['operand']) for x in incoming)
            tick=ins(A,'tick');assert pos(tick,'.temporaryShieldsLeft(')<pos(tick,'.breakShield(')<pos(tick,'.checkLichCrownBonus(')
            ray=ins(D,'getPlayerLookTarget');assert pos(ray,'.getEntities(')<pos(ray,'.isPickable(')<pos(ray,'.clip(')
            assert not any('ClipContext' in str(x['operand']) or '.hasLineOfSight(' in str(x['operand']) for x in ray)
            drain=ins(D,'onUseTick');assert pos(drain,'.hurt(')<pos(drain,'EntityTypes.BOSSES')<pos(drain,'.die(')<pos(drain,'.discard(')<pos(drain,'.addEffect(')<pos(drain,'.heal(')<pos(drain,'hurtButDontBreak(')<pos(drain,'.setDeltaMovement(')
            assert not any('.setHealth(' in str(x['operand']) for x in drain)
            discard=next(n for n,x in enumerate(drain) if '.die(' in str(x['operand']));assert '.discard(' in str(drain[discard+2]['operand'])
            assert sum('.hurt(' in str(x['operand']) for x in drain)==2
            profile=s['damage_profiles'][0];assert profile['type']=='twilightforest:lifedrain' and set(profile['tags'])=={'minecraft:bypasses_armor','minecraft:bypasses_shield','minecraft:bypasses_wolf_armor','minecraft:is_projectile','neoforge:is_magic'}
            ids={e['id'] for e in new['effects']};assert all(i in ids for e in s['effects'] for i in e.get('reuses_protected_effect_ids',[]))
            refs=read_json(OUT/'reference-evidence/twilight-scepter-payloads-244.json')['witnesses'];living=next(w for w in refs if w['entry']=='net/minecraft/world/entity/LivingEntity.class')
            update=next(m['instructions'] for m in living['methods'] if m['name']=='updateUsingItem');assert pos(update,'.onItemUseTick(')<pos(update,'.onUseTick(')
            assert d['damage_census']['reviewed_profiles_after']==28 and d['damage_census']['remaining_profiles']==12
        if d['slug']=='utility-projectiles':
            from collect_twilight_utility_projectiles import scan_callers
            scan=read_json(OUT/'twilightforest-utility-projectiles-caller-scan.json');assert scan==scan_callers(target)
            runtime={(h['entry'],h['method']) for h in scan['hits'] if 'TFDamageTypes.MOONWORM' in str(h['instruction']['operand']) and '/data/' not in h['entry'] and '/init/' not in h['entry']}
            assert runtime=={('twilightforest/entity/projectile/MoonwormShot.class','onHitEntity')}
            assert [r['entry'] for r in scan['cube_data_mentions']]==['data/twilightforest/tags/item/wip.json']
            Q='item/MoonwormQueenItem';M='entity/projectile/MoonwormShot';C='entity/projectile/CubeOfAnnihilation';I='item/CubeOfAnnihilationItem';D='dispenser/DamageableStackDispenseBehavior'
            release=ins(Q,'releaseUsing');assert pos(release,'.addFreshEntity(')<pos(release,'hurtButDontBreak(')
            disp=ins(D,'execute');assert pos(disp,'.getDamageAmount(')<pos(disp,'.addFreshEntity(')<pos(disp,'hurtButDontBreak(')
            i=next(n for n,x in enumerate(disp) if '.addFreshEntity(' in str(x['operand']));assert int(disp[i+1]['opcode'],16)==0x57
            head=ins(M,'onHitEntity');assert pos(head,'.hasItemInSlot(')<pos(head,'.setItemSlot(')<pos(head,'TFDamageTypes.MOONWORM')<pos(head,'.hurt(')<pos(head,'.getLootTable(')
            i=next(n for n,x in enumerate(head) if '.hurt(' in str(x['operand']));assert int(head[i+1]['opcode'],16)==0x57
            assert pos(ins(M,'onHit'),'TFThrowable.onHit(')<pos(ins(M,'onHit'),'.discard(')
            repair=ins('item/recipe/MoonwormQueenRepairRecipe','assemble');assert pos(repair,'.getDefaultInstance(')<pos(repair,'.setDamageValue(') and not any('.copy(' in str(x['operand']) for x in repair)
            source=ins(C,'getDamageSource');assert pos(source,'.getOwner(')<pos(source,'.playerAttack(')<pos(source,'.mobAttack(')<pos(source,'.thrown(')
            hit=ins(C,'onHitEntity');assert pos(hit,'.hurt(')<pos(hit,'.tickCountI');assert not any('.discard(' in str(x['operand']) for x in hit)
            terrain=ins(C,'affectBlocksInAABB');assert pos(terrain,'BlockEvent$BreakEvent.<init>')<pos(terrain,'.isCanceled(')<pos(terrain,'.canAnnihilate(')<pos(terrain,'.removeBlock(')
            assert not any('.destroyBlock(' in str(x['operand']) or 'canEntityGrief' in str(x['operand']) for x in terrain)
            tick=ins(C,'tick');assert pos(tick,'ThrowableProjectile.tick(')<pos(tick,'.getOwner(')<pos(tick,'.isReturning(')<pos(tick,'.affectBlocksInAABB(')
            i=next(n for n,x in enumerate(tick) if 'Vec3.multiply(' in str(x['operand']));assert int(tick[i+1]['opcode'],16)==0x57
            assert 'canPerformAction' not in {m['name'] for m in methods(I)} and [int(x['opcode'],16) for x in ins(I,'canDisableShield')]==[0x04,0xac]
            assert not any('hasHitObstacle' in str(x['operand']) for x in ins(C,'addAdditionalSaveData'))
            assert set(s['damage_profiles'][0]['tags'])=={'minecraft:no_knockback','neoforge:is_physical'}
            ids={e['id'] for e in new['effects']};assert all(i in ids for e in s['effects'] for i in e.get('reuses_protected_effect_ids',[]))
            assert d['damage_census']['reviewed_profiles_after']==29 and d['damage_census']['remaining_profiles']==11
        if d['slug']=='bows-fan':
            from collect_twilight_bows_fan import scan_callers
            scan=read_json(OUT/'twilightforest-bows-fan-caller-scan.json');assert scan==scan_callers(target)
            E='item/EnderBowItem';S='item/SeekerBowItem';A='entity/projectile/SeekerArrow';P='entity/projectile/TFArrow';T='item/TripleBowItem';F='item/PeacockFanItem';D='dispenser/FeatherFanDispenseBehavior'
            marker=ins(E,'customArrow');assert pos(marker,'.getPersistentData(')<pos(marker,'.putBoolean(')
            swap=ins('events/ToolEvents','onEnderBowHit');assert pos(swap,'EntityTypes.BOSSES')<pos(swap,'.contains(')<pos(swap,'.teleportTo(')<pos(swap,'.invulnerableTimeI')
            assert not any('.hurt(' in str(x['operand']) or '.setCanceled(' in str(x['operand']) or '.getBoolean(' in str(x['operand']) for x in swap)
            wrapper=ins(S,'customArrow');assert pos(wrapper,'.copyWithCount(')<pos(wrapper,'SeekerArrow.<init>')
            hit=ins(A,'onHitEntity');assert pos(hit,'.setCritArrow(')<pos(hit,'TFArrow.onHitEntity(')
            assert not {'addAdditionalSaveData','readAdditionalSaveData'} & {m['name'] for m in methods(A)+methods(P)}
            delegate=ins(P,'doPostHurtEffects');assert pos(delegate,'parentArrow')<pos(delegate,'AbstractArrow.doPostHurtEffects(')
            volley=ins(T,'shoot');assert pos(volley,'.hurtAndBreak(')<pos(volley,'.copy(')<pos(volley,'INTANGIBLE_PROJECTILE')<pos(volley,'.createProjectile(')<pos(volley,'.setDeltaMovement(')<pos(volley,'.addFreshEntity(')
            assert not any('processProjectileSpread' in str(x['operand']) for x in volley)
            post=ins('events/EntityEvents','entityHurts');assert pos(post,'.getMsgId(')<pos(post,'.getUsedItemHand(')<pos(post,'TFItems.TRIPLE_BOW')<pos(post,'.invulnerableTimeI')
            refs=read_json(OUT/'reference-evidence/vv-loader-244.json')['witnesses'];living=next(w for w in refs if w['entry']=='net/minecraft/world/entity/LivingEntity.class')
            act=next(m['instructions'] for m in living['methods'] if m['name']=='actuallyHurt');assert pos(act,'.setHealth(')<pos(act,'.onLivingDamagePost(')
            use=ins(F,'use');assert pos(use,'.doFan(')<pos(use,'.hurtAndBreak(')<pos(use,'.startUsingItem(')
            push=ins(F,'fanEntitiesInAABB');assert pos(push,'.getUseItem(')<pos(push,'.setDeltaMovement(')<pos(push,'.isShiftKeyDown(')<pos(push,'.addCooldown(')
            assert not any('.hurt(' in str(x['operand']) or '.deflect(' in str(x['operand']) for x in push)
            assert not any('SHIELD_BLOCK' in str(x['operand']) for m in methods(F) for x in m['instructions'])
            fall=ins('events/CapabilityEvents','updatePlayerCaps');assert pos(fall,'.setIgnoreFallDamageFromCurrentImpulse(')<pos(fall,'.currentImpulseImpactPosL')<pos(fall,'.onGround(')<pos(fall,'.setData(')
            disp=ins(D,'execute');assert pos(disp,'.getEntitiesOfClass(')<pos(disp,'.size(')<pos(disp,'.setDeltaMovement(')<pos(disp,'.hurtAndBreak(')
            assert not any('MovePlayerPacket' in str(x['operand']) or 'fanBlocksInAABB' in str(x['operand']) for x in disp)
            refs=read_json(OUT/'reference-evidence/twilight-ranged-mobs-244.json')['witnesses'];sk=next(w for w in refs if w['entry']=='net/minecraft/world/entity/monster/AbstractSkeleton.class')
            ranged=next(m['instructions'] for m in sk['methods'] if m['name']=='performRangedAttack');assert pos(ranged,'.getArrow(')<pos(ranged,'.customArrow(')<pos(ranged,'.shoot(')<pos(ranged,'.addFreshEntity(')
            assert not any('.releaseUsing(' in str(x['operand']) for x in ranged)
            assert not s['damage_profiles'] and d['damage_census']['reviewed_profiles_after']==29 and d['damage_census']['remaining_profiles']==11
        result=dict(schema='tno.external_effects.remaining_subsection_integrity.v1',status='PASS',checkpoint=d['checkpoint'],decision=d['decision'],starting_sha=d['starting_sha'],counts=s['counts'],protected_prior_files=len(protected),full_declared_class_coverage=len(d['full_classes']),twilight_reviewed_drafts=len(new['effects']),twilight_delivery_drafts=len(new['paths']),damage_profiles_reviewed=d['damage_census']['reviewed_profiles_after'],damage_profiles_remaining=d['damage_census']['remaining_profiles'],accepted_counts_unchanged=previous['accepted_counts_unchanged'],runtime_tests=0,promoted_twilight_records=0,**boundary_flags())
        results.append((d['slug'],result))
    assert results
    return results


if __name__=='__main__':
    for slug,result in validate_remaining():
        path=OUT/('twilightforest-'+slug+'-integrity.json')
        if path.exists():assert read_json(path)==result,'Protected integrity changed: '+slug
        else:write_json(path,result)
        print(json.dumps(result,indent=2))
