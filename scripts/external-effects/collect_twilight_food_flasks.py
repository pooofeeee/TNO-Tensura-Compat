"""Installed food/flask contracts and actual native consumption/damage comparisons."""
from twilight_evidence import *
from vanilla_reference import MojangNames,CLIENT
BATCH='twilight-food-flasks'
FULL=['item/'+c for c in ['BrittleFlaskItem','BrittleFlaskItem$Tooltip','GreaterFlaskItem','StackableEffectItem','StackableEffectItem$StackableEffectInstance','HydraChopItem','Experiment115Item','EssenceBerryItem']]+['components/item/PotionFlaskComponent','components/entity/PotionFlaskTrackingAttachment','advancements/DrinkFromFlaskTrigger','advancements/DrinkFromFlaskTrigger$TriggerInstance','advancements/DrinkFromFlaskTrigger$TriggerInstance$DrinkFromFlaskTriggerInstanceFactory','block/Experiment115Block']
TOKENS=['FAILED_CHALLENGE','POTION_FLASK_CONTENTS','FLASK_DOSES','PotionFlaskComponent','StackableEffectItem','EssenceBerryItem','EXPERIMENT_115_VARIANTS']
FOODS=['torchberries','venison','hydra_chop','meef','maze_wafer','experiment_115','raspberry','blueberry','blackberry','maloberry','blightberry','duskberry','skyberry','stingberry','berry_medley','moss_soup','shika_senbei','jerky','gelatinous','essence_berry','flask','failed_challenge']

def scan_callers(target):
    hits=[]
    with zipfile.ZipFile(target['path']) as jar:
        for entry in jar.namelist():
            if not entry.startswith('twilightforest/') or not entry.endswith('.class'):continue
            b=jar.read(entry)
            if not any(s.encode() in b for s in TOKENS):continue
            c=ClassFile(b)
            for m in c.methods:
                for i in c.instructions(m.get('code',b'')):
                    if any(s in str(i['operand']) for s in TOKENS):hits.append(dict(entry=entry,class_sha256=byte_hash(b),method=m['name'],descriptor=m['descriptor'],instruction=i))
    return dict(jar_sha256=target['sha256'],scope='All TF instruction callers of flask source/resource and food components. Data/model/UI producers are not independent combat payloads.',needles=TOKENS,hits=hits)

def collect():
    target=next(t for t in read_json(OUT/'jar-inventory.json')['targets'] if t['key']=='twilightforest');res=read_json(WORK/'twilightforest/resources.json')
    selected=[p for p,v in res.items() if p.startswith('data/') and any(k in p+' '+str(v.get('data','')) for k in FOODS)]
    classes={c:['*'] for c in FULL}
    classes.update({'events/EntityEvents':['setup','resetFlaskLogic'],'init/TFDataComponents':['*'],'init/TFDataAttachments':['*'],'data/TFAdvancementGenerator':['flaskWithHarming']})
    with zipfile.ZipFile(target['path']) as jar:
        for c,wanted in list(classes.items()):
            if wanted==['*']:continue
            available={m['name'] for m in ClassFile(jar.read('twilightforest/'+c+'.class')).methods}
            classes[c]=sorted(set(wanted)|{m for m in available if any(m.startswith('lambda$'+n+'$') for n in wanted)})
        for c,needles in [('init/TFItems',['FoodProperties','StackableEffectItem','FlaskItem','HydraChopItem','Experiment115Item','EssenceBerryItem']),('init/TFBlocks',['Experiment115Block']),('init/TFAdvancements',['DrinkFromFlaskTrigger'])]:
            cls=ClassFile(jar.read('twilightforest/'+c+'.class'));classes[c]=[m['name'] for m in cls.methods if m['name']=='<clinit>' or any(any(n in str(i['operand']) for n in needles) for i in cls.instructions(m.get('code',b'')))]
    print('native',native(BATCH,classes,selected),flush=True)
    raw={'net/minecraft/world/item/Item':['use','finishUsingItem','getUseDuration'],'net/minecraft/world/item/ItemStack':['consume','consumeAndReturn','finishUsingItem'],'net/minecraft/world/item/PotionItem':['finishUsingItem'],'net/minecraft/world/item/alchemy/PotionContents':['*'],'net/minecraft/world/food/FoodProperties':['*'],'net/minecraft/world/food/FoodProperties$Builder':['*'],'net/minecraft/world/food/FoodData':['eat','add','tick'],'net/minecraft/world/entity/LivingEntity':['eat','addEatEffect','completeUsingItem','addEffect','canBeAffected','isInvertedHealAndHarm','hurt','isDamageSourceBlocked','getDamageAfterArmorAbsorb','getDamageAfterMagicAbsorb'],'net/minecraft/world/entity/player/Player':['eat','canEat','hasInfiniteMaterials','getDestroySpeed','hurt'],'net/minecraft/world/effect/HealOrHarmMobEffect':['*'],'net/minecraft/world/effect/PoisonMobEffect':['*'],'net/minecraft/world/effect/RegenerationMobEffect':['*'],'net/minecraft/world/effect/WitherMobEffect':['*'],'net/minecraft/world/effect/MobEffectInstance':['update','tick','applyEffect','tickDownDuration','isInfiniteDuration'],'net/minecraft/world/effect/MobEffects':['<clinit>'],'net/minecraft/world/entity/ExperienceOrb':['playerTouch','repairPlayerItems','tick'],'net/minecraft/world/damagesource/DamageSources':['source','indirectMagic','magic','wither'],'net/minecraft/world/damagesource/DamageSource':['<init>','getSourcePosition','getDirectEntity','getEntity'],'net/minecraft/world/inventory/AbstractContainerMenu':['doClick','tryItemClickBehaviourOverride']}
    names=MojangNames()
    with zipfile.ZipFile(CLIENT) as jar:
        names.jar=jar
        for c,ms in raw.items():
            cls=ClassFile(jar.read(names.named[c]+'.class'));available={names.member(cls.name,m['name'],m['descriptor']) for m in cls.methods}
            raw[c]=sorted(available if ms==['*'] else {m for m in available if m in ms or any(m.startswith('lambda$'+n+'$') for n in ms)})
            assert raw[c],(c,ms)
    loader={c+'.class':list(ms) for c,ms in raw.items()};template=read_json(OUT/'reference-specifications/vv-loader-244.json');a=next(a for a in template['archives'] if a['path'].endswith('client.jar'))
    with zipfile.ZipFile(a['path']) as jar:
        for c in loader:
            if c not in jar.namelist():continue
            available={m['name'] for m in ClassFile(jar.read(c)).methods};wanted=raw[c[:-6]]
            loader[c]=sorted({m for m in available if m in wanted or any(m.startswith('lambda$'+n+'$') for n in wanted if not n.startswith('lambda$'))})
    hooks={'net/neoforged/neoforge/common/CommonHooks.class':['onItemStackedOn','onLivingHeal','onLivingIncomingDamage','onLivingUseItemFinish','onLivingEntityUseItemStart','onLivingEntityUseItemTick','onLivingEntityUseItemStop'],'net/neoforged/neoforge/event/entity/player/PlayerXpEvent$PickupXp.class':['*'],'net/neoforged/neoforge/common/NeoForgeMod.class':['<clinit>']}
    a=next(a for a in template['archives'] if a['path'].endswith('universal.jar'))
    with zipfile.ZipFile(a['path']) as jar:
        for c,ms in hooks.items():
            available={m['name'] for m in ClassFile(jar.read(c)).methods};hooks[c]=sorted(available if ms==['*'] else {m for m in available if m in ms or any(m.startswith('lambda$'+n+'$') for n in ms)})
            assert hooks[c],(c,ms,available)
    print('references',references(BATCH,raw,loader,hooks),flush=True)
    write_json(OUT/'twilightforest-food-flasks-caller-scan.json',scan_callers(target))

if __name__=='__main__':collect()
