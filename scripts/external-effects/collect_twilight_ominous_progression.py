"""Ominous contact/death/re-entry and biome enforcement; no runtime execution."""
from twilight_evidence import *
from vanilla_reference import MojangNames,CLIENT
BATCH='twilight-ominous-progression'
FIELDS=['OMINOUS_FIRE','ACID_RAIN']
FULL=['block/OminousFireBlock','block/OminousCandleBlock','block/entity/OminousCandleBlockEntity','item/ExanimateEssenceItem','item/recipe/EssenceRepairRecipe','util/entities/OminousFireDamageSource','init/custom/Enforcements','init/custom/Restrictions','util/Enforcement','util/Restriction']
TOKENS=['TFDamageTypes.'+f for f in FIELDS]+['TFBlocks.OMINOUS_FIRE','TFDataMaps.OMINOUS_FIRE','ZOMBIFIED_PLAYER','OminousFireDamageSource','enforceBiomeProgression','Enforcements.','EssenceRepairRecipe','TFItems.EXANIMATE_ESSENCE']
def scan_callers(target):
    hits=[]
    with zipfile.ZipFile(target['path']) as jar:
        for entry in jar.namelist():
            if not entry.startswith('twilightforest/') or not entry.endswith('.class'):continue
            b=jar.read(entry)
            if not any(s.rsplit('.',1)[-1].encode() in b for s in TOKENS):continue
            c=ClassFile(b)
            for m in c.methods:
                for i in c.instructions(m.get('code',b'')):
                    if any(s in str(i['operand']) for s in TOKENS):hits.append(dict(entry=entry,class_sha256=byte_hash(b),method=m['name'],descriptor=m['descriptor'],instruction=i))
    return dict(jar_sha256=target['sha256'],scope='Installed TF callers for last2 DamageTypes, Ominous conversion/profile wrapper, Exanimate Essence and biome enforcement; other structure/portal closure separate.',needles=TOKENS,hits=hits)
def collect():
    target=next(t for t in read_json(OUT/'jar-inventory.json')['targets'] if t['key']=='twilightforest');res=read_json(WORK/'twilightforest/resources.json')
    words=['ominous','acid_rain','exanimate','/restrictions/','essence_repair','scepters.json']
    selected=[p for p,v in res.items() if p.startswith('data/') and any(k in p+' '+str(v.get('data','')) for k in words)]
    classes={c:['*'] for c in FULL}
    classes.update({'events/EntityEvents':['setup','ominousFireConversion','zombifiedPlayerAttacks','reduceFrostedEffectIfOnFire'],'events/ProgressionEvents':['setup','performProtectionAndPortalChecks'],'util/PlayerHelper':['playerHasRequiredAdvancements','doesPlayerHaveRequiredAdvancement','doesPlayerHaveRequiredAdvancements'],'util/landmarks/LandmarkUtil':['isProgressionEnforced'],'util/entities/EntityUtil':['convertEntity'],'block/CandelabraBlock':['useItemOn'],'world/components/structures/util/StructureHints':['tryHintForStructure'],'init/TFDamageTypes':['getDamageSource','getEntityDamageSource','getIndirectEntityDamageSource']})
    with zipfile.ZipFile(target['path']) as jar:
        for c,ns in list(classes.items()):
            if ns==['*']:continue
            av={m['name'] for m in ClassFile(jar.read('twilightforest/'+c+'.class')).methods};assert set(ns)<=av,(c,set(ns)-av);classes[c]=sorted(set(ns)|{m for m in av if any(m.startswith('lambda$'+n+'$') for n in ns)})
        for c,needles in [('init/TFBlocks',['OminousFireBlock','OminousCandleBlock']),('init/TFItems',['ExanimateEssenceItem']),('init/TFBlockEntities',['OMINOUS_CANDLE']),('init/TFRecipes',['EssenceRepairRecipe']),('init/TFDataAttachments',['ZOMBIFIED_PLAYER','SIMPLE_GAME_PROFILE','createOfflineProfile']),('init/TFDataMaps',['OMINOUS_FIRE']),('init/TFGameRules',['ENFORCED_PROGRESSION_RULE','tfEnforcedProgression']),('events/RegistrationEvents',['TFDataMaps.OMINOUS_FIRE'])]:
            cl=ClassFile(jar.read('twilightforest/'+c+'.class'));classes[c]=sorted({m['name'] for m in cl.methods if m['name']=='<clinit>' or any(any(n in str(i['operand']) for n in needles) for i in cl.instructions(m.get('code',b'')))})
    print('native',native(BATCH,classes,selected),flush=True)
    raw={'net/minecraft/world/level/block/BaseFireBlock':['*'],'net/minecraft/world/entity/LivingEntity':['hurt','die','getKillCredit','igniteForSeconds','igniteForTicks','getDamageAfterArmorAbsorb','getDamageAfterMagicAbsorb','actuallyHurt','isDamageSourceBlocked'],'net/minecraft/world/entity/Entity':['isInvulnerableTo','igniteForSeconds','igniteForTicks','baseTick','setRemainingFireTicks'],'net/minecraft/world/entity/player/Player':['hurt','causeFoodExhaustion'],'net/minecraft/server/level/ServerPlayer':['die'],'net/minecraft/world/entity/monster/Zombie':['finalizeSpawn','doHurtTarget','getSpawnAsBabyOdds','createAttributes','handleAttributes','populateDefaultEquipmentSlots'],'net/minecraft/world/entity/monster/Witch':['getDamageAfterMagicAbsorb'],'net/minecraft/world/entity/boss/wither/WitherBoss':['hurt'],'net/minecraft/world/level/portal/PortalShape':['isEmpty','findEmptyPortalShape','findPortalShape'],'net/minecraft/world/damagesource/DamageScaling':['<init>','<clinit>'],'net/minecraft/world/damagesource/DamageSources':['mobAttack'],'net/minecraft/world/damagesource/DamageSource':['<init>','getEntity','getDirectEntity','getSourcePosition','scalesWithDifficulty','getLocalizedDeathMessage'],'net/minecraft/world/entity/Mob':['convertTo','doHurtTarget'],'net/minecraft/world/effect/HungerMobEffect':['applyEffectTick','shouldApplyEffectTickThisTick'],'net/minecraft/world/effect/MobEffects':['<clinit>'],'net/minecraft/world/effect/MobEffect':['applyEffectTick','setBlendDuration'],'net/minecraft/server/level/ServerPlayerGameMode':['useItemOn'],'net/minecraft/world/item/crafting/CustomRecipe':['*'],'net/minecraft/world/item/crafting/Recipe':['getRemainingItems'],'net/minecraft/world/inventory/ResultSlot':['onTake'],'net/minecraft/world/entity/decoration/ArmorStand':['hurt'],'net/minecraft/world/entity/item/ItemEntity':['hurt']}
    names=MojangNames()
    with zipfile.ZipFile(CLIENT) as jar:
        names.jar=jar
        for c,ms in list(raw.items()):
            cl=ClassFile(jar.read(names.named[c]+'.class'));av={names.member(cl.name,m['name'],m['descriptor']) for m in cl.methods};raw[c]=sorted(av if ms==['*'] else {m for m in av if m in ms or any(m.startswith('lambda$'+n+'$') for n in ms)});assert raw[c],c
    loader={c+'.class':list(ms) for c,ms in raw.items()};template=read_json(OUT/'reference-specifications/vv-loader-244.json');a=next(a for a in template['archives'] if a['path'].endswith('client.jar'))
    with zipfile.ZipFile(a['path']) as jar:
        for c in loader:
            if c not in jar.namelist():continue
            av={m['name'] for m in ClassFile(jar.read(c)).methods};wanted=raw[c[:-6]]+(['getScalingFunction'] if c.endswith('/DamageScaling.class') else [])
            loader[c]=sorted({m for m in av if m in wanted or any(m.startswith('lambda$'+n+'$') for n in wanted if not n.startswith('lambda$'))})
    hooks={'net/neoforged/neoforge/common/damagesource/IScalingFunction.class':['<clinit>','lambda$static$0'],'net/neoforged/neoforge/common/damagesource/IScalingFunction$1.class':['<clinit>'],'net/neoforged/neoforge/event/EventHooks.class':['canLivingConvert','onLivingConvert','finalizeMobSpawn','onTrySpawnPortal'],'net/neoforged/neoforge/common/CommonHooks.class':['onLivingDeath','onEntityIncomingDamage'],'net/neoforged/neoforge/event/entity/living/LivingIncomingDamageEvent.class':['getAmount','setAmount'],'net/neoforged/neoforge/event/entity/living/LivingDeathEvent.class':['<init>','getSource']}
    print('references',references(BATCH,raw,loader,hooks),flush=True)
    write_json(OUT/'twilightforest-ominous-progression-caller-scan.json',scan_callers(target))
if __name__=='__main__':collect()
