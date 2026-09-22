"""LoyalZombie/ZombieWand, expiry caller and shared real scepter recharge resources."""
from twilight_evidence import *
from vanilla_reference import MojangNames,CLIENT
BATCH='twilight-summon-resources'
FULL=['entity/monster/LoyalZombie','item/ZombieWandItem','enchantment/RechargeScepterEffect','item/recipe/ScepterRepairRecipe','item/recipe/ScepterRepairRecipe$Serializer']
NEEDLES=['TFEntities.LOYAL_ZOMBIE','TFDamageTypes.EXPIRED','RechargeScepterEffect.applyRecharge','TFItemStackUtils.hurtButDontBreak']

def scan_callers(target):
    hits=[]
    with zipfile.ZipFile(target['path']) as jar:
        for entry in jar.namelist():
            if not entry.startswith('twilightforest/') or not entry.endswith('.class'):continue
            b=jar.read(entry)
            if not any(s.encode() in b for s in ['LOYAL_ZOMBIE','EXPIRED','RechargeScepterEffect','hurtButDontBreak']):continue
            c=ClassFile(b)
            for m in c.methods:
                for i in c.instructions(m.get('code',b'')):
                    if any(s in str(i['operand']) for s in NEEDLES):hits.append(dict(entry=entry,class_sha256=byte_hash(b),method=m['name'],descriptor=m['descriptor'],instruction=i))
    return dict(jar_sha256=target['sha256'],scope='All TF instructions for actual LoyalZombie registration/EXPIRED caller/shared recharge and nonbreaking durability. Other item payloads remain separate review.',needles=NEEDLES,hits=hits)

def collect():
    target=next(t for t in read_json(OUT/'jar-inventory.json')['targets'] if t['key']=='twilightforest');res=read_json(WORK/'twilightforest/resources.json')
    selected=[p for p,v in res.items() if ('/tags/' in p and any(x in str(v) for x in ['expired','loyal_zombie','scepter','ender_pearl'])) or p.endswith('/expired.json') or p.endswith('/renewal.json') or p=='data/twilightforest/loot_table/entities/loyal_zombie.json' or ('/recipe/' in p and v['data'].get('type')=='twilightforest:scepter_repair')]
    classes={c:['*'] for c in FULL};classes.update({'util/TFItemStackUtils':['hurtButDontBreak'],'init/TFEnchantments':['bootstrap'],'item/TwilightWandItem':['inventoryTick'],'item/FortificationWandItem':['inventoryTick'],'item/LifedrainScepterItem':['inventoryTick']})
    with zipfile.ZipFile(target['path']) as jar:
        c=ClassFile(jar.read('twilightforest/init/TFItems.class'))
        classes['init/TFItems']=[m['name'] for m in c.methods if m['name']=='<clinit>' or any(any(k in str(i['operand']) for k in ['ZombieWandItem.<init>','TwilightWandItem.<init>','FortificationWandItem.<init>','LifedrainScepterItem.<init>']) for i in c.instructions(m.get('code',b'')))]
    print('native',native(BATCH,classes,selected))
    names=MojangNames()
    fullraw=['net/minecraft/world/entity/TamableAnimal','net/minecraft/world/entity/AgeableMob']+['net/minecraft/world/entity/ai/goal/'+c for c in ['FollowOwnerGoal','target/OwnerHurtByTargetGoal','target/OwnerHurtTargetGoal','target/HurtByTargetGoal','target/TargetGoal','target/NearestAttackableTargetGoal']]
    fullraw+=['net/minecraft/world/entity/player/StackedContents','net/minecraft/world/entity/player/StackedContents$RecipePicker','net/minecraft/world/item/crafting/CraftingInput','net/minecraft/world/item/crafting/CustomRecipe']
    raw={c:[] for c in fullraw}
    raw.update({'net/minecraft/world/entity/Leashable':['mayBeLeashed'], 'net/minecraft/world/item/crafting/Ingredient':['getItems','getStackingIds','test'], 'net/minecraft/core/component/DataComponentPredicate':['test'], 'net/minecraft/world/item/Item':['getPlayerPOVHitResult'], 'net/minecraft/world/item/ItemStack':['setDamageValue','getDamageValue','getMaxDamage','isDamageableItem','inventoryTick','getItem','consume','shrink'], 'net/minecraft/world/entity/player/Inventory':['tick'], 'net/minecraft/world/entity/LivingEntity':['baseTick','tick','checkTotemDeathProtection','heal','addEffect','removeEffect','canBeAffected','hurt'], 'net/minecraft/world/item/enchantment/EnchantmentHelper':['tickEffects','runIterationOnEquipment','runIterationOnItem'], 'net/minecraft/world/item/enchantment/Enchantment':['tick','getSlotItems','matchingSlot'], 'net/minecraft/world/item/crafting/RecipeManager':['getRecipeFor','getAllRecipesFor'], 'net/minecraft/recipebook/ServerPlaceRecipe':['recipeClicked'], 'net/minecraft/world/item/crafting/Recipe':['getRemainingItems']})
    with zipfile.ZipFile(CLIENT) as jar:
        names.jar=jar
        for c,ms in raw.items():
            cls=ClassFile(jar.read(names.named[c]+'.class'));available={names.member(cls.name,m['name'],m['descriptor']) for m in cls.methods}
            raw[c]=sorted(available) if c in fullraw else sorted({m for m in available if m in ms or any(m.startswith('lambda$'+n+'$') for n in ms)})
    loader={c+'.class':list(ms) for c,ms in raw.items()};template=read_json(OUT/'reference-specifications/vv-loader-244.json');a=next(a for a in template['archives'] if a['path'].endswith('client.jar'))
    with zipfile.ZipFile(a['path']) as jar:
        for c,ms in loader.items():
            if c not in jar.namelist():continue
            available={m['name'] for m in ClassFile(jar.read(c)).methods}
            wanted=raw[c[:-6]]
            loader[c]=sorted(available) if c[:-6] in fullraw else sorted({m for m in available if m in wanted or any(m.startswith('lambda$'+n+'$') for n in wanted if not n.startswith('lambda$'))})
    hooks={'net/neoforged/neoforge/common/extensions/IItemExtension.class':['getDamage','setDamage','getMaxDamage','damageItem','hasCraftingRemainingItem','getCraftingRemainingItem'],'net/neoforged/neoforge/common/extensions/IItemStackExtension.class':['hasCraftingRemainingItem','getCraftingRemainingItem']}
    a=next(a for a in template['archives'] if a['path'].endswith('universal.jar'))
    with zipfile.ZipFile(a['path']) as jar:
        for c in ['net/neoforged/neoforge/common/crafting/DataComponentIngredient.class','net/neoforged/neoforge/common/crafting/CompoundIngredient.class']:hooks[c]=sorted({m['name'] for m in ClassFile(jar.read(c)).methods})
    print('references',references(BATCH,raw,loader,hooks))
    write_json(OUT/'twilightforest-summon-resources-caller-scan.json',scan_callers(target))
    rs=dict(classes={},resources=['data/minecraft/enchantment/protection.json','data/minecraft/enchantment/feather_falling.json'])
    write_json(OUT/'vanilla-specifications/twilight-summon-protection.json',rs)
    write_json(OUT/'vanilla-evidence/twilight-summon-protection.json',prepare(rs))

if __name__=='__main__':collect()
