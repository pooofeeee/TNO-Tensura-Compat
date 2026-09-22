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
        if d['slug']=='equipment':
            from collect_twilight_equipment import scan_callers
            scan=read_json(OUT/'twilightforest-equipment-caller-scan.json');assert scan==scan_callers(target)
            assert scan['custom_damage_provider_implementers']==['twilightforest/item/CustomDamageSwordItem.class']
            assert scan['nested']['service']=='twilightforest.asm.TFCoreMod' and scan['nested']['sha256']=='1324a81e5cf085d62385f85e4b06e6217bf977977f92c58034af315c5d975690'
            use=ins('events/ToolEvents','fieryToolSetFire');assert pos(use,'.getEntity(')<pos(use,'.getMainHandItem(')<pos(use,'.fireImmune(')<pos(use,'.igniteForSeconds(')
            assert not any('.getDirectEntity(' in str(x['operand']) or '.getAmount(' in str(x['operand']) for x in use)
            for c,parent in [('item/FierySwordItem','SwordItem'),('item/FieryPickItem','PickaxeItem')]:
                hit=ins(c,'hurtEnemy');assert pos(hit,parent+'.hurtEnemy(')<pos(hit,'.igniteForSeconds(') and any(x['operand']==15.0 for x in hit)
                assert not any('.hurt(' in str(x['operand']) for x in hit)
            post=ins('events/EntityEvents','entityHurts');assert pos(post,'.getOriginalDamage(')<pos(post,'.nextInt(')<pos(post,'.fireImmune(')<pos(post,'.igniteForSeconds(')
            assert any(int(x['opcode'],16)==0x6c for x in post),'Fiery duration uses integer division'
            glass=ins('item/GlassSwordItem','hurt');assert pos(glass,'INFINITE_GLASS_SWORD')<pos(glass,'.processDurabilityChange(')<pos(glass,'ITEM_DURABILITY_CHANGED')
            assert not any('UNBREAKABLE' in str(x['operand']) or '.isDamageableItem(' in str(x['operand']) for x in glass)
            shatter=ins('item/GlassSwordItem','hurtAndBreak');assert pos(shatter,'instabuild')<pos(shatter,'.hurt(')<pos(shatter,'.shrink(')
            lore=ins('init/TFCreativeTabs','createGlassSwordAndLoreVer');assert pos(lore,'UNBREAKABLE')<pos(lore,'INFINITE_GLASS_SWORD')
            provider=ins('item/CustomDamageSwordItem','getDamageSource');assert any('.source(' in str(x['operand']) for x in provider) and not any('.hurt(' in str(x['operand']) for x in provider)
            hook=ins('asmhooks/DamageSourceHooks','getCustomDamageSource');assert pos(hook,'.getWeaponItem(')<pos(hook,'CustomDamageProvider')<pos(hook,'.getDamageSource(')
            asm=read_json(OUT/'reference-evidence/twilight-equipment-asm.json')['witnesses'];tr=next(w for w in asm if w.get('class_name','').endswith('/DamageSourcesTransformer'))
            assert tr['archive_sha256']==scan['nested']['sha256']
            targets=next(m['instructions'] for m in tr['methods'] if m['name']=='targets');assert {x['operand'] for x in targets if x['operand'] in ['mobAttack','playerAttack','mobAttackNoAggro']}=={'mobAttack','playerAttack'}
            body=[x for m in tr['methods'] for x in m['instructions']];assert any(x['operand']==176 for x in body) and any(x['operand']=='getCustomDamageSource' for x in body)
            reg=next(w for w in asm if w.get('class_name','').endswith('/TFCoreMod'));assert any('DamageSourcesTransformer.<init>' in str(x['operand']) for m in reg['methods'] for x in m['instructions'])
            shield=methods('item/KnightmetalShieldItem');assert not any('.hurt(' in str(x['operand']) for m in shield for x in m['instructions'])
            assert any('ARCTIC_BOOTS' in str(x['operand']) for x in ins('item/ArcticArmorItem','canWalkOnPowderedSnow'))
            assert set(s['damage_profiles'][0]['tags'])==set() and s['damage_profiles'][0]['type']=='twilightforest:stale_sandwich'
            assert d['damage_census']['reviewed_profiles_after']==30 and d['damage_census']['remaining_profiles']==10
        if d['slug']=='charms':
            from collect_twilight_charms import scan_callers
            scan=read_json(OUT/'twilightforest-charms-caller-scan.json');assert scan==scan_callers(target)
            E='events/CharmEvents';U='util/TFItemStackUtils';C='compat/curios/CuriosCompat'
            setup=ins(E,'setup');assert pos(setup,'HIGHEST')<pos(setup,'.HIGHL')
            life=ins(E,'handleCharmOfLife');assert pos(life,'CHARM_OF_LIFE_2')<pos(life,'CHARM_OF_LIFE_1')<pos(life,'.setHealth(')<pos(life,'.addEffect(')
            assert not any('.heal(' in str(x['operand']) or '.hurt(' in str(x['operand']) or '.invulnerableTime' in str(x['operand']) for x in life)
            keep=ins(E,'handleCharmOfKeeping');i=next(n for n,x in enumerate(keep) if 'NonNullList.of(' in str(x['operand']))
            assert int(keep[i-1]['opcode'],16)==0xbd and int(keep[i-2]['opcode'],16)==0x03,'TierI actual empty varargs array'
            assert pos(keep,'CHARM_OF_KEEPING_3')<pos(keep,'CHARM_OF_KEEPING_2')<pos(keep,'CHARM_OF_KEEPING_1')<pos(keep,'KEPT_ON_DEATH')
            raw=read_json(OUT/'vanilla-evidence/twilight-charms.json')['classes'];lst=next(w for w in raw if w['class_name']=='net/minecraft/core/NonNullList')
            of=next(m['instructions'] for m in lst['methods'] if m['name']=='of');assert pos(of,'Arrays.asList(')<pos(of,'NonNullList.<init>(')
            stock=ins(E,'stockKeepsakeCasket');assert pos(stock,'.hasAnyMatching(')<pos(stock,'.consumeInventoryItem(')<pos(stock,'.canBeReplaced(')<pos(stock,'.setBlockAndUpdate(')<pos(stock,'.setItems(')
            assert not any('BreakEvent' in str(x['operand']) or '.mayUseItemAt(' in str(x['operand']) for x in stock)
            restore=ins(U,'loadNoClear');assert any('.add(' in str(x['operand']) for x in restore) and any(int(x['opcode'],16)==0xba for x in restore)
            assert not any('.drop(' in str(x['operand']) for x in restore)
            ret=ins(E,'returnStoredItems');assert pos(ret,'.loadNoClear(')<pos(ret,'.clear(')<pos(ret,'.remove(')
            curio=ins(C,'findAndConsumeCurio');assert pos(curio,'.getCuriosInventory(')<pos(curio,'.isPresent(')<pos(curio,'.save(')<pos(curio,'.shrink(')
            assert not any('.isEmpty(' in str(x['operand']) for x in curio)
            drop=ins(C,'keepCurios');assert pos(drop,'CharmStack')<pos(drop,'TFCharmInventory')<pos(drop,'.isEmpty(')<pos(drop,'.getCuriosInventory(')
            repair=ins('block/KeepsakeCasketBlock','useItemOn');assert pos(repair,'CHARM_OF_KEEPING_3')<pos(repair,'.consume(')<pos(repair,'.setBlockAndUpdate(')
            assert not any('.hurt(' in str(x['operand']) or '.setHealth(' in str(x['operand']) for m in methods('entity/CharmEffect') for x in m['instructions'])
            refs=read_json(OUT/'reference-evidence/twilight-charms-curios.json')['witnesses'];cap=next(w for w in refs if w.get('class_name','').endswith('/CurioInventoryCapability'))
            search=[x for m in cap['methods'] if m['name']=='findFirstCurio' for x in m['instructions']];assert any('Cache.getIfPresent(' in str(x['operand']) for x in search) and any('.getActiveStates(' in str(x['operand']) for x in search)
            assert cap['archive_sha256']==scan['dependency']['sha256']
            assert not s['damage_profiles'] and d['damage_census']['reviewed_profiles_after']==30 and d['damage_census']['remaining_profiles']==10
        if d['slug']=='travellers-core':
            from collect_twilight_travellers_core import scan_callers,T,M,R
            scan=read_json(OUT/'twilightforest-travellers-core-caller-scan.json');assert scan==scan_callers(target)
            E='events/TravellersGearEvents';L=T+'TravellersGearLogic';D='init/custom/TravellersModifiersManager';A=T+'TravellersArmorItem'
            active=ins(M+'TravellersModifier','isActive');assert pos(active,'.hasModifier(')<pos(active,'.isTravellersArmorAndBroken(')<pos(active,'.ALWAYS_ACTIVE')
            assert not any('IS_TRAVELLERS_GEAR' in str(x['operand']) for x in active)
            init=next(m['instructions'] for m in methods(A) if m['name']=='<init>' and m['descriptor'].endswith(';I)V'))
            firstassign=next(x['offset'] for x in init if int(x['opcode'],16)==0xb5 and '.attributeModifiers' in str(x['operand']))
            assert firstassign<pos(init,'.getDefaultAttributeModifiers('),'nonnull component assigned before virtual default lookup'
            for fn in ['glovesProperties']:
                assert not any('.attributes(' in str(x['operand']) or '.durability(' in str(x['operand']) for x in ins(A,fn))
            for fn in ['makesPiglinsNeutral','canWalkOnPowderedSnow']:
                assert not any('isModifierActive' in str(x['operand']) or 'isTravellersArmorAndBroken' in str(x['operand']) for x in ins(A,fn))
            assert [int(x['opcode'],16) for x in ins(A,'supportsEnchantment')]==[0x03,0xac]
            match=ins(R+'TravellersGearModifierRecipe','matches');assert pos(match,'.getModifiableArmor(')<pos(match,'.countInsertableModifiers(')<pos(match,'.hasTravellersModifier(')<pos(match,'.getModifierDataComponentProviders(')
            apply=ins(R+'TravellersGearModifierRecipe','applyModifier');assert pos(apply,'.transferModifier(')<pos(apply,'.addModifier(')
            attrs=ins(E,'activateAndDeactivateTravellersModifiers');assert pos(attrs,'.getCurrentServer(')<pos(attrs,'STORED_BROKEN_ATTRIBUTES')<pos(attrs,'.clearModifiers(')<pos(attrs,'.remove(')<pos(attrs,'.build(')
            remove=ins(M+'TravellersEntryModifier','removeModifier');assert pos(remove,'.getAttributeModifiers(')<pos(remove,'.set(')<pos(remove,'.remove(')
            assert not any('STORED_BROKEN_ATTRIBUTES' in str(x['operand']) for x in remove),'removal leaves separate saved attributes'
            track=ins(E,'setLastDamageArmorTime');assert any('LAST_DAMAGE_ARMOR_TIME' in str(x['operand']) for x in track)
            assert not any('getNewDamage' in str(x['operand']) for x in ins(E,'performPerfectDodge'))
            repair=ins(L,'travellersGearAutoRepair');assert pos(repair,'LAST_DAMAGE_ARMOR_TIME')<pos(repair,'.getGameTime(')<pos(repair,'.getArmorSlots(')
            assert any(x['operand']==200 for x in repair)
            rbody=[x for m in methods(L) if m['name'].startswith('lambda$travellersGearAutoRepair') for x in m['instructions']]
            assert pos(rbody,'AUTO_REPAIR_PROBABILITY')<pos(rbody,'.isModifierActive(')<pos(rbody,'.getAutoRepairChance(')<pos(rbody,'.nextFloat(')<pos(rbody,'.setDamageValue(')
            assert not any('.heal(' in str(x['operand']) or '.hurt(' in str(x['operand']) for x in repair+rbody)
            dodge=ins(E,'performPerfectDodge');assert pos(dodge,'EntityHitResult')<pos(dodge,'LivingEntity')<pos(dodge,'PERFECT_DODGE_PROBABILITY')<pos(dodge,'.isClientSide(')<pos(dodge,'.setCanceled(')<pos(dodge,'.nextFloat(')
            assert len([x for x in dodge if '.setCanceled(' in str(x['operand'])])==2
            assert not any('.getOwner(' in str(x['operand']) or 'DamageTypes' in str(x['operand']) or '.hurt(' in str(x['operand']) or '.discard(' in str(x['operand']) for x in dodge)
            magnet=ins(E,'magnetizeArrows');assert pos(magnet,'.getOwner(')<pos(magnet,'.tickCountI')<pos(magnet,'ARROW_MAGNETISM')<pos(magnet,'.discard(')<pos(magnet,'.getPickupItemStackOrigin(')
            assert pos(magnet,'.getPickupItemStackOrigin(')<max(x['offset'] for x in magnet if '.discard(' in str(x['operand'])),'separate nonplayer early discard and player post-recovery discard'
            assert any(x['operand']==200 for x in magnet) and not any('.setCanceled(' in str(x['operand']) for x in magnet)
            assert any('.DENYL' in str(x['operand']) for x in ins(E,'cancelPhantomSpawns'))
            stealth=ins(L,'travellersStealth');assert pos(stealth,'.isModifierActive(')<pos(stealth,'.isCrouching(')<pos(stealth,'INVISIBILITY')<pos(stealth,'.setInvisible(')
            assert not any('.removeEffect(' in str(x['operand']) for x in stealth)
            haste=ins(L,'travellersVestHaste');assert pos(haste,'HASTE_AMPLIFIER')<pos(haste,'.isModifierActive(')<pos(haste,'DIG_SPEED')<pos(haste,'.addEffect(')
            eater=ins('asmhooks/PlayerHooks','getFoodExhaustion');assert pos(eater,'EquipmentSlot.CHEST')<pos(eater,'EFFICIENT_EATER')<pos(eater,'.isModifierActive(')
            assert any(int(x['opcode'],16)==0x6e for x in eater),'native float division, not food addition'
            raw=[c for p in (OUT/'vanilla-evidence').glob('*.json') for c in read_json(p).get('classes',[])]
            common=next(m['instructions'] for c in raw if c['class_name']=='net/minecraft/core/component/DataComponents' for m in c['methods'] if m['name']=='<clinit>')
            end=next(i for i,x in enumerate(common) if 'COMMON_ITEM_COMPONENTS' in str(x['operand']));tail=common[end-24:end+1]
            assert pos(tail,'.ATTRIBUTE_MODIFIERS')<pos(tail,'ItemAttributeModifiers.EMPTY')<pos(tail,'.COMMON_ITEM_COMPONENTS')
            refs=[w for p in (OUT/'reference-evidence').glob('*.json') for w in read_json(p).get('witnesses',[]) if w.get('archive_sha256') in ['8e3563a078289f0f07ee6f87f1c8651294387639c8355983ee207cb753f08b7f','d874b2aa4d511919a567ae73f13510e63e16f7318194eb2c03824cd68a59df6f']]
            def ri(c,fn):return next(m['instructions'] for w in refs if w['entry']==c+'.class' for m in w.get('methods',[]) if m['name']==fn)
            grind=ri('net/minecraft/world/inventory/GrindstoneMenu','createResult');assert pos(grind,'.onGrindstoneChange(')<pos(grind,'.computeResult(')
            anvil=ri('net/minecraft/world/inventory/AnvilMenu','createResult');assert any('.isValidRepairItem(' in str(x['operand']) for x in anvil) and not any('.isRepairable(' in str(x['operand']) for x in anvil)
            arrow=ri('net/minecraft/world/entity/projectile/AbstractArrow','tick');assert pos(arrow,'.onProjectileImpact(')<pos(arrow,'.hitTargetOrDeflectSelf(')
            between=[x for x in arrow if pos(arrow,'.onProjectileImpact(')<x['offset']<pos(arrow,'.hitTargetOrDeflectSelf(')]
            assert not any('.isRemoved(' in str(x['operand']) for x in between)
            phantom=ri('net/minecraft/world/level/levelgen/PhantomSpawner','tick');assert pos(phantom,'.firePlayerSpawnPhantoms(')<pos(phantom,'.shouldSpawnPhantoms(')<pos(phantom,'TIME_SINCE_REST')
            asm=read_json(OUT/'reference-evidence/twilight-travellers-core-asm.json')['witnesses'];tr=next(w for w in asm if w.get('class_name','').endswith('ReduceMovementFoodExhaustionTransformer'))
            tg=next(m['instructions'] for m in tr['methods'] if m['name']=='targets')
            assert {x['operand'] for x in tg if x['operand'] in ['checkMovementStatistics','jumpFromGround','causeFoodExhaustion','attack']}=={'checkMovementStatistics','jumpFromGround'}
            assert any(x['operand']=='getFoodExhaustion' for m in tr['methods'] for x in m['instructions'])
            reg=read_json(OUT/'reference-evidence/twilight-equipment-asm.json')['witnesses'];assert any('ReduceMovementFoodExhaustionTransformer.<init>' in str(x['operand']) for w in reg for m in w.get('methods',[]) for x in m['instructions'])
            assert not s['damage_profiles'] and d['damage_census']['reviewed_profiles_after']==30 and d['damage_census']['remaining_profiles']==10
        if d['slug']=='travellers-movement':
            from collect_twilight_travellers_movement import scan_callers,T,TRANSFORMERS
            scan=read_json(OUT/'twilightforest-travellers-movement-caller-scan.json');assert scan==scan_callers(target)
            E='events/TravellersGearEvents';L=T+'TravellersGearLogic';C='client/event/TravellersClientEvents';H='asmhooks/EntityHooks';B='asmhooks/BlockHooks';P='asmhooks/PlayerHooks';S='components/entity/SlimySolesAttachment'
            water=ins(H,'processWaterWalking');assert pos(water,'FluidTags.WATER')<pos(water,'.isModifierActive(')<pos(water,'.isBelowMaxWaterWalkingSubmergedHeight(')<pos(water,'.isShiftKeyDown(')
            assert any(x['operand']==.4 for x in ins(L,'isBelowMaxWaterWalkingSubmergedHeight'))
            stuck=ins(H,'resetStuckUnrestrained');assert pos(stuck,'LivingEntity')<pos(stuck,'.lengthSqr(')<pos(stuck,'.isModifierActive(')<pos(stuck,'Vec3.ZERO')
            assert any(x['operand']==-.08 for x in ins(B,'stopBouncing'))
            fall=ins(E,'reduceSlimySolesFallDamage');assert pos(fall,'.isShiftKeyDown(')<pos(fall,'.isModifierActive(')<pos(fall,'.calculateFallDamage(')<pos(fall,'.setCanceled(')<pos(fall,'.sqrt(')
            assert not any('FALL_DAMAGE_IMMUNE' in str(x['operand']) or '.hurt(' in str(x['operand']) for x in ins(E,'calculateFallDamage')+fall)
            cancel=ins(E,'cancelSlimySolesJump');assert any('.bounceVelocityD' in str(x['operand']) for x in cancel) and not any('.doubleJumpBoostVelocityD' in str(x['operand']) for x in cancel)
            bounce=ins(L,'travellersBootsSlimySolesBounce');assert not any('.isModifierActive(' in str(x['operand']) for x in bounce)
            ctor=next(m['instructions'] for m in methods(S) if m['name']=='<init>' and m['descriptor']=='(DDZZ)V')
            fields=[x['operand'] for x in ctor if int(x['opcode'],16)==0xb5]
            assert len(fields)==3 and not any('doubleJumpBoostVelocity' in str(x) for x in fields),'native decode constructor drops encoded boost'
            assert any('double_jump_boost_velocity' in str(x['operand']) for m in methods(S) for x in m['instructions'])
            double=ins(L,'performDoubleJump');assert pos(double,'HAS_DOUBLE_JUMP')<pos(double,'.jumpFromGround(')<pos(double,'.doubleJumpBoostVelocityD')<pos(double,'.resetFallDistance(')<pos(double,'TRAVELLERS_DOUBLE_JUMP_SAFE_FALL_DISTANCE')
            assert not any('.isModifierActive(' in str(x['operand']) for x in double)
            pre=ins(E,'tickMovementModifiers');assert pos(pre,'.isModifierActive(')<pos(pre,'.onGround(')<pos(pre,'HAS_DOUBLE_JUMP')<pos(pre,'.removeModifier(')
            glide=ins(L,'travellersWingsGradualGlide');assert pos(glide,'.isModifierActive(')<pos(glide,'.isFallFlying(')<pos(glide,'IS_GRADUALLY_GLIDING')<pos(glide,'.setDeltaMovement(')<pos(glide,'.getGravity(')
            assert not any('.onGround(' in str(x['operand']) or '.isPassenger(' in str(x['operand']) for x in glide)
            gp=[x for m in methods('network/GradualGlidePacket') if m['name'].startswith('lambda$handle') for x in m['instructions']]
            assert pos(gp,'.getPlayerByUUID(')<pos(gp,'.setData(')<pos(gp,'.sendToPlayersTrackingEntity(')
            assert not any('.equals(' in str(x['operand']) or '.isModifierActive(' in str(x['operand']) for x in gp)
            side=ins(L,'tryPerformSidestep');assert pos(side,'SIDESTEP_COOLDOWN')<pos(side,'.isModifierActive(')<pos(side,'.onGround(')<pos(side,'.isCrouching(')<pos(side,'.performSidestep(')
            assert not any('.isPassenger(' in str(x['operand']) for x in side)
            dash=ins(L,'performSidestep');assert any(x['operand']==1.6 for x in dash) and any('.push(' in str(x['operand']) for x in dash) and not any('.setDeltaMovement(' in str(x['operand']) for x in dash)
            validate=ins(L,'validateMovement');assert pos(validate,'.isDedicatedServer(')<pos(validate,'.tickCountI')<pos(validate,'.disconnect(')
            assert any(x['operand']==45 for x in validate)
            server=ins(L,'travellersBootsStraightAhead');assert pos(server,'.isModifierActive(')<pos(server,'.hasModifier(')<pos(server,'.addOrUpdateTransientModifier(')
            assert not any('forwardImpulse' in str(x['operand']) for x in server)
            client=ins(C,'handleStraightAhead');assert pos(client,'.forwardImpulseF')<pos(client,'.addOrUpdateTransientModifier(')<pos(client,'.leftImpulseF')
            agile=ins(C,'handleAgileRanger');assert pos(agile,'ProjectileWeaponItem')<pos(agile,'TRAVELLERS_AGILE_RANGER_BLACKLISTED')<pos(agile,'.isUsingItem(')<pos(agile,'.isPassenger(')<pos(agile,'.leftImpulseF')
            assert not any('.hurt(' in str(x['operand']) or '.setHealth(' in str(x['operand']) for c in [L,H,B,P,C] for m in methods(c) for x in m['instructions'])
            refs=[w for p in (OUT/'reference-evidence').glob('*.json') for w in read_json(p).get('witnesses',[]) if w.get('archive_sha256') in ['8e3563a078289f0f07ee6f87f1c8651294387639c8355983ee207cb753f08b7f','d874b2aa4d511919a567ae73f13510e63e16f7318194eb2c03824cd68a59df6f']]
            def ri(c,fn):return next(m['instructions'] for w in refs if w['entry']==c+'.class' for m in w.get('methods',[]) if m['name']==fn)
            ai=ri('net/minecraft/client/player/LocalPlayer','aiStep');event=pos(ai,'.onMovementInputUpdate(')
            slowed=[x for x in ai if x['offset']>event and 'leftImpulse' in str(x['operand'])];assert slowed
            assert any('LocalPlayer.isInFluidType(Ljava/util/function/BiPredicate;)' in str(x['operand']) for x in ai)
            fluid=ri('net/minecraft/world/level/block/LiquidBlock','getCollisionShape');assert pos(fluid,'.isAbove(')<pos(fluid,'.LEVEL')<pos(fluid,'.canStandOnFluid(')
            actualfall=ri('net/minecraft/world/entity/LivingEntity','causeFallDamage');assert pos(actualfall,'.onLivingFall(')<pos(actualfall,'.calculateFallDamage(')<pos(actualfall,'.hurt(')
            fov=ri('net/minecraft/client/player/AbstractClientPlayer','getFieldOfViewModifier');assert any(int(x['opcode'],16)==0x0c for x in fov) and any(int(x['opcode'],16)==0xae for x in fov)
            asm=read_json(OUT/'reference-evidence/twilight-travellers-movement-asm.json')['witnesses'];assert {w['entry'].rsplit('/',1)[-1][:-6] for w in asm}==set(TRANSFORMERS)
            reg=read_json(OUT/'reference-evidence/twilight-equipment-asm.json')['witnesses']
            for name in TRANSFORMERS:assert any(name+'.<init>' in str(x['operand']) for w in reg for m in w.get('methods',[]) for x in m['instructions'])
            cfg=read_json(OUT/'config-evidence/twilightforest-client.json');assert sha256(cfg['path'])==cfg['sha256'] and cfg['values']['travellersWingsGradualGlide'] is True
            assert not s['damage_profiles'] and d['damage_census']['reviewed_profiles_after']==30 and d['damage_census']['remaining_profiles']==10
        if d['slug']=='travellers-utility':
            from collect_twilight_travellers_utility import scan_callers,T,TRANSFORMERS
            scan=read_json(OUT/'twilightforest-travellers-utility-caller-scan.json');assert scan==scan_callers(target)
            A=T+'TravellersArmorBeltItem';G=T+'TravellersGogglesItem';S='components/item/ItemDisplayContents';M=S+'$Mutable';C='client/event/TravellersClientEvents';H='asmhooks/ArmorHooks'
            swap=ins(A,'travellersTrySwapHotbar');assert pos(swap,'.getArmor(')<pos(swap,'.hasSwapHotbar(')<pos(swap,'.isSwapHotbarActive(')<pos(swap,'.canFitInsideContainerItems(')<pos(swap,'TRAVELLERS_BELT_BLACKLISTED')<pos(swap,'.setItem(')<pos(swap,'ItemContainerContents.fromItems(')
            assert any(x['operand']==9 for x in swap) and not any('.addCooldown(' in str(x['operand']) or '.getOffhandItem(' in str(x['operand']) for x in swap)
            has=ins(A,'hasSwapHotbar');assert any('.hasTravellersModifier(' in str(x['operand']) for x in has) and not any('.isModifierActive(' in str(x['operand']) for x in has)
            insert=next(m['instructions'] for m in methods(M) if m['name']=='trySwap' and 'BiConsumer' in m['descriptor']);assert pos(insert,'.canFitInsideContainerItems(')<pos(insert,'.findInsertSlot(')<pos(insert,'.findSwapSlot(')<pos(insert,'.isSameItemSameComponents(')<pos(insert,'.split(')<pos(insert,'.set(')
            cycle=ins(M,'cycleChosenMapSlot');assert not any('.tryResetChosenMapSlot(' in str(x['operand']) for x in cycle) and any(int(x['opcode'],16)==0x02 for x in cycle)
            isempty=ins(S,'isEmpty');assert any('NonNullList.isEmpty(' in str(x['operand']) for x in isempty) and not any('ItemStack.isEmpty(' in str(x['operand']) for x in isempty)
            decode=ins(S,'fromSlots');assert pos(decode,'.isEmpty(')<pos(decode,'ItemDisplayContents.EMPTY')<pos(decode,'.getAsInt(')
            tick=ins(G,'inventoryTick');assert pos(tick,'EquipmentSlot.HEAD')<pos(tick,'.isClientSide(')<pos(tick,'.isModifierActive(')<pos(tick,'.inventoryTick(')<pos(tick,'.getUpdatePacket(')
            assert any(x['operand']==36 for x in tick) and not any('.hurt(' in str(x['operand']) or '.addEffect(' in str(x['operand']) for x in tick)
            maphelper=ins('asmhooks/MapHooks','updateMapsInGoggles');assert pos(maphelper,'EquipmentSlot.HEAD')<pos(maphelper,'.isModifierActive(')<pos(maphelper,'.findActiveMapSlot(')<pos(maphelper,'.isSameItemSameComponents(')
            zoom=ins(C,'updateZoomState');assert pos(zoom,'.isZoomKeyHeld(')<pos(zoom,'.isModifierActive(')<pos(zoom,'.setNewFovModifier(')<max(x['offset'] for x in zoom if 'IS_USING_GOGGLES_ZOOM_MODIFIER' in str(x['operand']))
            mouse=ins(C,'slowZoomSensitivity');assert pos(mouse,'.getCinematicCameraEnabled(')<pos(mouse,'ZOOM_ABILITY_MODIFIER')<pos(mouse,'.isZoomKeyHeld(')<pos(mouse,'.getMouseSensitivity(')<pos(mouse,'.setMouseSensitivity(')
            assert not any('.isModifierActive(' in str(x['operand']) or '.clamp(' in str(x['operand']) for x in mouse)
            packet=[x for m in methods('network/GogglesZoomPacket') if m['name'].startswith('lambda$handle') for x in m['instructions']]
            assert pos(packet,'.getPlayerByUUID(')<pos(packet,'.isModifierActive(')<pos(packet,'.sendToPlayersTrackingEntity(') and not any('.equals(' in str(x['operand']) for x in packet)
            recipe=ins('item/recipe/EmperorsClothRecipe','matches');assert pos(recipe,'EMPERORS_CLOTH_APPLICABLE')<pos(recipe,'.hasCraftingRemainingItem(')<pos(recipe,'TFDataComponents.EMPERORS_CLOTH')
            smith=ins('item/recipe/NoTemplateSmithingRecipe','matches');assert pos(smith,'.isEmpty(')<pos(smith,'Ingredient.test(')<pos(smith,'ItemStack.has(')
            wash=ins('events/MiscEvents','washOffCloth');assert pos(wash,'.isCanceled(')<pos(wash,'WATER_CAULDRON')<pos(wash,'.lowerFillLevel(')<pos(wash,'.remove(')<pos(wash,'.setCanceled(')
            assert not any('.isClientSide(' in str(x['operand']) or '.giveItemToPlayer(' in str(x['operand']) for x in wash)
            fraction=ins('util/ArmorUtil','getShroudedArmorPercentage');assert pos(fraction,'.getArmorSlots(')<pos(fraction,'.isEmpty(')<pos(fraction,'EMPERORS_CLOTH') and any(int(x['opcode'],16)==0x6e for x in fraction)
            assert any(int(x['opcode'],16)==0x66 for x in ins(H,'modifyArmorVisibility')) and not any('.addEffect(' in str(x['operand']) or '.getAttribute(' in str(x['operand']) for m in methods(H) for x in m['instructions'])
            assert any(x['operand']==519 for x in ins('client/renderer/block/RedThreadRenderer','<clinit>'))
            toggle=ins(C,'toggleBooleanDataAttachment');assert any('.setData(' in str(x['operand']) for x in toggle) and not any('.send(' in str(x['operand']) for x in toggle)
            refs=[w for p in (OUT/'reference-evidence').glob('*.json') for w in read_json(p).get('witnesses',[]) if w.get('archive_sha256') in ['8e3563a078289f0f07ee6f87f1c8651294387639c8355983ee207cb753f08b7f','d874b2aa4d511919a567ae73f13510e63e16f7318194eb2c03824cd68a59df6f']]
            def rm(c,fn):return [m for w in refs if w['entry']==c+'.class' for m in w.get('methods',[]) if m['name']==fn]
            vis=rm('net/minecraft/world/entity/LivingEntity','getVisibilityPercent')[0];vi=vis['instructions'];vcode=bytes.fromhex(vis['code_hex']);anchor=next(x for x in vi if int(x['opcode'],16)==0x38 and vcode[x['offset']+1]==4)
            assert pos(vi,'.isInvisible(')<pos(vi,'.getArmorCoverPercentage(')<anchor['offset']<pos(vi,'.getEntityVisibilityMultiplier(')
            armor=next(m for m in rm('net/minecraft/client/renderer/entity/layers/HumanoidArmorLayer','renderArmorPiece') if m['descriptor'].endswith('FFFFFF)V'));acode=bytes.fromhex(armor['code_hex']);ai=armor['instructions'];anchor=next(x for x in ai if int(x['opcode'],16)==0xc1)
            assert any(int(x['opcode'],16)==0x3a and acode[x['offset']+1]==13 for x in ai if x['offset']<anchor['offset']),'exact installed local13 item stack'
            elytra=rm('net/minecraft/client/renderer/entity/layers/ElytraLayer','shouldRender')[0]['instructions'];assert any('Items.ELYTRA' in str(x['operand']) for x in elytra) and not any('EMPERORS_CLOTH' in str(x['operand']) for x in elytra)
            setter=rm('net/neoforged/neoforge/client/event/CalculatePlayerTurnEvent','setMouseSensitivity')[0]['instructions'];assert len(setter)==4 and int(setter[-2]['opcode'],16)==0xb5
            raw=[c for p in (OUT/'vanilla-evidence').glob('*.json') for c in read_json(p).get('classes',[])]
            carried=next(m['instructions'] for c in raw if c['class_name']=='net/minecraft/world/level/saveddata/maps/MapItemSavedData' for m in c['methods'] if m['name']=='tickCarriedBy');assert len([x for x in carried if 'Inventory.contains(Ljava/util/function/Predicate;)' in str(x['operand'])])==2
            asm=read_json(OUT/'reference-evidence/twilight-travellers-utility-asm.json')['witnesses'];assert {w['entry'].rsplit('/',1)[-1][:-6] for w in asm}==set(TRANSFORMERS)
            reg=read_json(OUT/'reference-evidence/twilight-equipment-asm.json')['witnesses']
            for name in TRANSFORMERS:assert any(name+'.<init>' in str(x['operand']) for w in reg for m in w.get('methods',[]) for x in m['instructions'])
            assert not s['damage_profiles'] and d['damage_census']['reviewed_profiles_after']==30 and d['damage_census']['remaining_profiles']==10
        if d['slug']=='food-flasks':
            from collect_twilight_food_flasks import scan_callers
            scan=read_json(OUT/'twilightforest-food-flasks-caller-scan.json');assert scan==scan_callers(target)
            callers={(x['entry'],x['method']) for x in scan['hits'] if 'TFDamageTypes.FAILED_CHALLENGE' in str(x['instruction']['operand']) and '/data/' not in x['entry'] and '/init/' not in x['entry']}
            assert callers=={('twilightforest/item/BrittleFlaskItem.class','finishUsingItem')}
            F='item/BrittleFlaskItem';C='components/item/PotionFlaskComponent';B='item/StackableEffectItem';E='block/Experiment115Block'
            drink=ins(F,'finishUsingItem');assert pos(drink,'PotionContents.EMPTY')<pos(drink,'entity/player/Player')<pos(drink,'.isClientSide(')<pos(drink,'.getAllEffects(')<pos(drink,'MobEffects.HARM')<pos(drink,'.isInvertedHealAndHarm(')<pos(drink,'FAILED_CHALLENGE')<pos(drink,'.hurt(')<pos(drink,'.isInstantenous(')<pos(drink,'.applyInstantenousEffect(')<pos(drink,'.addEffect(')<pos(drink,'.awardStat(')<pos(drink,'.changeAndConsumeFlask(')
            at=next(i for i,x in enumerate(drink) if '.hurt(' in str(x['operand']));assert int(drink[at+1]['opcode'],16)==0x57,'hurt result discarded'
            assert any('.source(Lnet/minecraft/resources/ResourceKey;)' in str(x['operand']) for x in drink)
            assert any(int(x['opcode'],16)==0x78 for x in drink) and any(x['operand']==6 for x in drink)
            assert not any('MobEffects.HEAL' in str(x['operand']) or '.setHealth(' in str(x['operand']) or '.doses(' in str(x['operand']) for x in drink)
            for name in ['overrideOtherStackedOnMe','overrideStackedOnOther']:
                fill=ins(F,name);assert pos(fill,'POTION_CONTENTS')<pos(fill,'ClickAction.SECONDARY')<pos(fill,'.equals(')<pos(fill,'.doses(')<pos(fill,'.breakage(')<pos(fill,'.shrink(')<pos(fill,'GLASS_BOTTLE')<pos(fill,'.changeAndConsumeFlask(')
                assert not any('PotionItem' in str(x['operand']) or '.allowModification(' in str(x['operand']) or '.mayPickup(' in str(x['operand']) for x in fill)
            use=ins(F,'use');assert pos(use,'PotionContents.EMPTY')<pos(use,'.doses(')<pos(use,'.startUsingInstantly(')
            remove=ins(C,'removeDose');assert pos(remove,'.doses(')<pos(remove,'PotionContents.EMPTY')<pos(remove,'.breakable(')<pos(remove,'.breakage(')
            ct=next(m['instructions'] for m in methods(B) if m['name']=='<init>' and m['descriptor']=='()V');assert ct[1]['operand']==0 and int(ct[2]['opcode'],16)==0xbd and '[Ltwilightforest/item/StackableEffectItem$StackableEffectInstance;' in ct[3]['operand']
            finish=ins(B,'finishUsingItem');assert pos(finish,'.isClientSide(')<pos(finish,'.applyEffects(')<pos(finish,'Item.finishUsingItem(')
            stack=ins(B,'applyOrStackEffect');assert pos(stack,'.getEffect(')<pos(stack,'.getDuration(')<pos(stack,'.extraDurationTicks(')<pos(stack,'.amplifier(')<pos(stack,'.addEffect(') and any(int(x['opcode'],16)==0x60 for x in stack)
            assert not any('.hurt(' in str(x['operand']) for m in methods(B) for x in m['instructions'])
            consume=ins(E,'useWithoutItem');assert pos(consume,'.canEat(')<pos(consume,'.getFoodData(')<pos(consume,'.eat(')<pos(consume,'.removeBlock(') and not any('REGENERATE' in str(x['operand']) for x in consume)
            random=ins(E,'randomTick');assert pos(random,'REGENERATE')<pos(random,'BITES_TAKEN')<pos(random,'.setBlockAndUpdate(') and not any('.next' in str(x['operand']) for x in random)
            essence=ins('item/EssenceBerryItem','use');assert pos(essence,'.consume(')<pos(essence,'.isClientSide')<pos(essence,'entity/ExperienceOrb')<pos(essence,'.nextInt(')<pos(essence,'.addFreshEntity(')
            assert any(x['operand']==14 for x in essence) and any(x['operand']==6 for x in essence) and not any('.giveExperiencePoints(' in str(x['operand']) or '.heal(' in str(x['operand']) for x in essence)
            refs=[w for p in (OUT/'reference-evidence').glob('*.json') for w in read_json(p).get('witnesses',[]) if w.get('archive_sha256') in ['8e3563a078289f0f07ee6f87f1c8651294387639c8355983ee207cb753f08b7f','d874b2aa4d511919a567ae73f13510e63e16f7318194eb2c03824cd68a59df6f']]
            def ri(c,fn):return next(m['instructions'] for w in refs if w['entry']==c+'.class' for m in w.get('methods',[]) if m['name']==fn)
            poison=ri('net/minecraft/world/effect/PoisonMobEffect','applyEffectTick');assert pos(poison,'.getHealth(')<pos(poison,'POISON_DAMAGE')<pos(poison,'DamageTypes.MAGIC')<pos(poison,'.hurt(')
            menu=ri('net/minecraft/world/inventory/AbstractContainerMenu','tryItemClickBehaviourOverride');assert pos(menu,'.onItemStackedOn(')<pos(menu,'.overrideStackedOnOther(')<pos(menu,'.overrideOtherStackedOnMe(')
            orb=ri('net/minecraft/world/entity/ExperienceOrb','playerTouch');assert pos(orb,'PickupXp')<pos(orb,'.repairPlayerItems(')<pos(orb,'.giveExperiencePoints(')
            p=s['damage_profiles'][0];assert p['type']=='twilightforest:failed_challenge' and p['status']=='USED' and p['tags']==[]
            assert d['damage_census']['reviewed_profiles_after']==31 and d['damage_census']['remaining_profiles']==9
        if d['slug']=='active-utilities':
            from collect_twilight_active_utilities import scan_callers
            scan=read_json(OUT/'twilightforest-active-utilities-caller-scan.json');assert scan==scan_callers(target)
            W='item/PocketWatchItem';P='item/TransformPowderItem';U='util/entities/EntityUtil';H='item/CrumbleHornItem';M='item/OreMagnetItem';L='item/LampOfCindersItem';E='events/ToolEvents'
            watch=ins(W,'inventoryTick');assert pos(watch,'.isClientSide')<pos(watch,'MOVEMENT_SPEED')<pos(watch,'MobEffects.JUMP')<pos(watch,'.isHolding(')<pos(watch,'DIG_SPEED')
            assert any(x['operand']==40 for x in watch) and not any('.hurt(' in str(x['operand']) or '.setHealth(' in str(x['operand']) for x in watch)
            veto=ins(E,'preventFatigueWithPocketWatch');assert pos(veto,'.getApplicationResult(')<pos(veto,'DIG_SLOWDOWN')<pos(veto,'POCKET_WATCH')<pos(veto,'.isHolding(')<pos(veto,'DO_NOT_APPLY')
            assert not any('.removeEffect(' in str(x['operand']) for x in veto)
            interact=ins(P,'interactLivingEntity');assert pos(interact,'.isAlive(')<pos(interact,'.isCreative(')<pos(interact,'.transformEntityIfPossible(')
            powder=ins(P,'transformEntityIfPossible');assert pos(powder,'OwnableEntity')<pos(powder,'.getOwner(')<pos(powder,'TRANSFORMATION_POWDER')<pos(powder,'.convertEntity(')<pos(powder,'.shrink(')
            assert not any('.isTame(' in str(x['operand']) or '.getHealth(' in str(x['operand']) for x in powder)
            convert=ins(U,'convertEntity');assert pos(convert,'ServerLevel')<pos(convert,'.create(')<pos(convert,'.canLivingConvert(')<pos(convert,'.getPassengers(')<pos(convert,'.convertTo(')<pos(convert,'.load(')<pos(convert,'.setUUID(')<pos(convert,'.getMaxHealth(')<pos(convert,'.setHealth(')<pos(convert,'.startRiding(')<pos(convert,'.onLivingConvert(')
            assert not any('.hurt(' in str(x['operand']) or '.heal(' in str(x['operand']) for x in convert)
            disp=ins('dispenser/TransformationDispenseBehavior','execute');assert pos(disp,'NO_SPECTATORS')<pos(disp,'.getEntitiesOfClass(')<pos(disp,'.transformEntityIfPossible(')
            assert not any('.isEmpty(' in str(x['operand']) or '.getCount(' in str(x['operand']) or '.isAlive(' in str(x['operand']) for x in disp)
            assert not any(int(x['opcode'],16)==0xb5 for x in ins('dispenser/TransformationDispenseBehavior','playSound'))
            horn=ins(H,'onUseTick');assert any(x['operand']==10 for x in horn) and any(int(x['opcode'],16)==0x70 for x in horn) and pos(horn,'ServerLevel')<pos(horn,'.doCrumble(')
            crumble=ins(H,'crumbleBlock');assert pos(crumble,'CRUMBLE_HORN')<pos(crumble,'BreakEvent')<pos(crumble,'.isCanceled(')<pos(crumble,'Blocks.AIR')<pos(crumble,'.nextFloat(')<pos(crumble,'.canHarvestBlock(')<pos(crumble,'.removeBlock(')<pos(crumble,'.getBlockEntity(')<pos(crumble,'.playerDestroy(')<pos(crumble,'.canEntityGrief(')
            hc=ins('dispenser/CrumbleDispenseBehavior','execute');assert pos(hc,'.getMaxDamage(')<pos(hc,'CRUMBLE_HORN')<pos(hc,'.destroyBlock(')<pos(hc,'.hurtAndBreak(')
            assert not any('.nextFloat(' in str(x['operand']) or 'BreakEvent' in str(x['operand']) or '.chanceToCrumble(' in str(x['operand']) for x in hc)
            release=ins(M,'releaseUsing');assert len([x for x in release if '.doMagnet(' in str(x['operand'])])==9 and pos(release,'.isClientSide(')<pos(release,'.doMagnet(')<pos(release,'.hurtAndBreak(')
            vein=ins(M,'findVein');assert any(x['operand']==24 for x in vein) and any(int(x['opcode'],16)==0xa6 for x in vein),'BlockState identity inequality rejection'
            move=next(m['instructions'] for m in methods(M) if m['name']=='doMagnet' and 'BlockPos' in m['descriptor']);assert pos(move,'.isReplaceable(')<pos(move,'.isOre(')<pos(move,'.getBlockEntity(')<pos(move,'.findVein(')<pos(move,'.setBlock(')
            assert not any('BreakEvent' in str(x['operand']) or '.canEntityGrief(' in str(x['operand']) for x in move)
            book=[x for m in methods(M) if m['name'].startswith('lambda$isBookEnchantable') for x in m['instructions']];assert pos(book,'Enchantments.UNBREAKING')<pos(book,'Objects.equals(') and not any('.getKey(' in str(x['operand']) for x in book)
            lamp=ins(L,'releaseUsing');assert any(x['operand']==12 for x in lamp) and pos(lamp,'.getDamageValue(')<pos(lamp,'.getMaxDamage(')<pos(lamp,'.doBurnEffect(')
            burn=ins(L,'doBurnEffect');player_branch=next(x['offset'] for x in burn if int(x['opcode'],16)==0xc1 and x['operand']=='net/minecraft/world/entity/player/Player')
            assert pos(burn,'.isClientSide(')<pos(burn,'.burnBlock(')<player_branch<pos(burn,'.getEntitiesOfClass(')<pos(burn,'.igniteForSeconds(')
            assert any(x['operand']==5.0 for x in burn) and not any('.hurtAndBreak(' in str(x['operand']) or '.shrink(' in str(x['operand']) or '.hurt(' in str(x['operand']) for m in methods(L) for x in m['instructions'])
            maps=read_json(WORK/'twilightforest/resources.json');assert len(maps['data/twilightforest/data_maps/entity_type/transformation_powder.json']['data']['values'])==32 and len(maps['data/twilightforest/data_maps/block/crumble_horn.json']['data']['values'])==63
            cfg=read_json(OUT/'config-evidence/twilightforest-common.json');assert sha256(cfg['path'])==cfg['sha256'] and cfg['values']['Magic Trees']['miningCoreRange']==16
            refs=[w for p in (OUT/'reference-evidence').glob('*.json') for w in read_json(p).get('witnesses',[]) if w.get('archive_sha256') in ['8e3563a078289f0f07ee6f87f1c8651294387639c8355983ee207cb753f08b7f','d874b2aa4d511919a567ae73f13510e63e16f7318194eb2c03824cd68a59df6f']]
            def ri(c,fn):return next(m['instructions'] for w in refs if w['entry']==c+'.class' for m in w.get('methods',[]) if m['name']==fn)
            mob=ri('net/minecraft/world/entity/Mob','convertTo');assert pos(mob,'.copyAndClear(')<pos(mob,'.addFreshEntity(')<pos(mob,'.discard(')
            saving=ri('net/minecraft/world/entity/Mob','addAdditionalSaveData');loading=ri('net/minecraft/world/entity/Mob','readAdditionalSaveData')
            assert any(x['operand']=='ArmorItems' for x in saving) and any(x['operand']=='HandItems' for x in saving) and pos(loading,'ArmorItems')<pos(loading,'ItemStack.parseOptional(')
            assert not s['damage_profiles'] and d['damage_census']['reviewed_profiles_after']==31 and d['damage_census']['remaining_profiles']==9
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
