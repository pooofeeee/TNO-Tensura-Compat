"""Travellers modifier admission, durability and defensive/resource hooks."""
from twilight_evidence import *
from vanilla_reference import MojangNames,CLIENT
from selected_reference import collect as reference_collect
BATCH='twilight-travellers-core'
T='item/travellers_gear/';M=T+'modifiers/';R='item/recipe/travellers/'
FULL=[T+'TravellersArmorItem','init/custom/TravellersModifiersManager','init/custom/TravellersModifiersManager$CacheInvalidationReloadListener']+[M+c for c in ['TravellersModifier','InsertableTravellersModifier','TravellersModifiable','TravellersComponentModifier','TravellersEntryModifier','BuiltinTravellersComponentModifier','TransferableTravellersModifier','TransferableComponentModifier']]+[R+c for c in ['TravellersGearModifierRecipe','TravellersGearModifierRecipe$AbstractModifierRecipeSerializer','TravellersGearModifierShapedRecipe','TravellersGearModifierShapedRecipe$Serializer','TravellersGearModifierShapelessRecipe','TravellersGearModifierShapelessRecipe$Serializer','TravellersVestGlovesMergeRecipe','TravellersVestGlovesMergeRecipe$InputPair']]
TOKENS=['IS_TRAVELLERS_GEAR','STORED_BROKEN_ATTRIBUTES','AUTO_REPAIR_PROBABILITY','PERFECT_DODGE_PROBABILITY','ARROW_MAGNETISM','ALL_NIGHT_GOGGLES','STEALTH_CROUCHING','HASTE_AMPLIFIER','AQUATIC_AGILITY','EFFICIENT_EATER','getFoodExhaustion','LAST_DAMAGE_ARMOR_TIME']

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
    return dict(jar_sha256=target['sha256'],scope='All TF instruction callers of core gear state and selected passive/defensive modifiers. Movement, belt/display and remaining visual/control hooks are explicitly pending.',needles=TOKENS,hits=hits)

def collect():
    target=next(t for t in read_json(OUT/'jar-inventory.json')['targets'] if t['key']=='twilightforest');res=read_json(WORK/'twilightforest/resources.json')
    selected=[p for p,v in res.items() if p.startswith('data/') and ('travellers' in p+' '+str(v))]
    classes={c:['*'] for c in FULL}
    classes.update({'events/TravellersGearEvents':['setup','magnetizeArrows','performPerfectDodge','performStealth','updateOtherModifiers','activateAndDeactivateTravellersModifiers','stopDamagingTravellersGear','setLastDamageArmorTime','cancelCombiningTravellersGear','removeModifiersFromTravellersGear','extractItemsFromSwapHotbarModifier','returnModifierItems','getUniqueTravellersGear','cancelPhantomSpawns','fireCraftingModifierTrigger'],T+'TravellersGearLogic':['travellersStealth','travellersGearAutoRepair','getAutoRepairChance','travellersVestHaste'],T+'TravellersGogglesItem':['<init>','isEnderMask'],'client/event/TravellersClientEvents':['setup','handleStealth'],'asmhooks/PlayerHooks':['getFoodExhaustion'],'util/TFMathUtil':['probabilityOfAtLeastOneSuccess'],'init/TFAttributeModifiers':['<clinit>']})
    with zipfile.ZipFile(target['path']) as jar:
        for c,wanted in list(classes.items()):
            if wanted==['*']:continue
            allnames={m['name'] for m in ClassFile(jar.read('twilightforest/'+c+'.class')).methods}
            classes[c]=sorted(set(wanted)|{m for m in allnames if any(m.startswith('lambda$'+n+'$') for n in wanted)})
        for c,needles in [('init/TFItems',['Travellers']),('init/TFRecipes',['Travellers']),('init/TFDataComponents',TOKENS+['travellers','repair_probability','dodge_probability','haste_amplifier','efficient_eater','aquatic_agility']),('init/TFDataAttachments',['LAST_DAMAGE_ARMOR_TIME','last_damage_armor']),('events/RegistrationEvents',['TravellersModifiersManager','TravellersModifier.CODEC']),('init/custom/TravellersModifierTypes',['Travellers']),('TFRegistries',['travellers_modifiers']),('TFRegistries$Keys',['travellers_modifiers']),('compat/common/DefaultModifiedTravellersGearGetter',['Travellers'])]:
            cls=ClassFile(jar.read('twilightforest/'+c+'.class'));classes[c]=[m['name'] for m in cls.methods if m['name']=='<clinit>' or any(any(n in str(i['operand']) for n in needles) for i in cls.instructions(m.get('code',b'')))]
    classes['init/TFDataComponents']=['*'];classes['init/TFDataAttachments']=['*']
    print('native',native(BATCH,classes,selected),flush=True)
    raw={'net/minecraft/world/effect/MobEffects':['<clinit>'], 'net/minecraft/world/effect/MobEffect':['addAttributeModifier','addAttributeModifiers','removeAttributeModifiers'], 'net/minecraft/world/effect/MobEffect$AttributeTemplate':['create'], 'net/minecraft/core/component/DataComponents':['<clinit>'], 'net/minecraft/world/item/Item$Properties':['<init>','component','buildAndValidateComponents','attributes'], 'net/minecraft/server/level/ServerPlayer':['checkMovementStatistics'], 'net/minecraft/world/entity/LivingEntity':['getVisibilityPercent','decreaseAirSupply','getCurrentSwingDuration','doHurtEquipment','addEffect','updateInvisibilityStatus'], 'net/minecraft/world/entity/player/Player':['checkMovementStatistics','causeFoodExhaustion','jumpFromGround','getDestroySpeed'], 'net/minecraft/world/food/FoodData':['addExhaustion','tick'], 'net/minecraft/world/entity/monster/EnderMan':['isLookingAtMe'], 'net/minecraft/world/entity/monster/piglin/PiglinAi':['isWearingGold'], 'net/minecraft/world/level/levelgen/PhantomSpawner':['tick'], 'net/minecraft/world/entity/projectile/AbstractArrow':['tick','getPickupItemStackOrigin'], 'net/minecraft/world/entity/projectile/ThrowableProjectile':['tick'], 'net/minecraft/world/entity/projectile/Projectile':['hitTargetOrDeflectSelf','onHit'], 'net/minecraft/world/item/ItemStack':['getAttributeModifiers','forEachModifier','setDamageValue','isDamageableItem'], 'net/minecraft/world/inventory/GrindstoneMenu':['createResult','removeNonCurses','computeResult'], 'net/minecraft/world/inventory/GrindstoneMenu$4':['onTake'], 'net/minecraft/world/inventory/AnvilMenu':['createResult'], 'net/minecraft/world/effect/MobEffectUtil':['hasDigSpeed','getDigSpeedAmplification'], 'net/minecraft/world/item/Item':['getDefaultAttributeModifiers','getDefaultInstance']}
    names=MojangNames()
    with zipfile.ZipFile(CLIENT) as jar:
        names.jar=jar
        for c,ms in raw.items():
            cls=ClassFile(jar.read(names.named[c]+'.class'));available={names.member(cls.name,m['name'],m['descriptor']) for m in cls.methods};raw[c]=sorted({m for m in available if m in ms or any(m.startswith('lambda$'+n+'$') for n in ms)})
    loader={c+'.class':list(ms) for c,ms in raw.items()};template=read_json(OUT/'reference-specifications/vv-loader-244.json');a=next(a for a in template['archives'] if a['path'].endswith('client.jar'))
    with zipfile.ZipFile(a['path']) as jar:
        for c in loader:
            if c not in jar.namelist():continue
            available={m['name'] for m in ClassFile(jar.read(c)).methods};wanted=raw[c[:-6]]
            loader[c]=sorted({m for m in available if m in wanted or any(m.startswith('lambda$'+n+'$') for n in wanted if not n.startswith('lambda$'))})
    hooks={'net/neoforged/neoforge/event/entity/living/ArmorHurtEvent.class':['*'],'net/neoforged/neoforge/event/ItemAttributeModifierEvent.class':['*'],'net/neoforged/neoforge/event/entity/ProjectileImpactEvent.class':['*'],'net/neoforged/neoforge/event/entity/player/PlayerSpawnPhantomsEvent.class':['*'],'net/neoforged/neoforge/common/CommonHooks.class':['onArmorHurt','shouldSuppressEnderManAnger','computeModifiedAttributes','onGrindstoneChange','onGrindstoneTake','onAnvilChange'],'net/neoforged/neoforge/event/EventHooks.class':['onProjectileImpact','firePlayerSpawnPhantoms'],'net/neoforged/neoforge/common/extensions/IItemStackExtension.class':['getAttributeModifiers','isRepairable'],'net/neoforged/neoforge/common/extensions/IItemExtension.class':['getDefaultAttributeModifiers','isEnderMask','makesPiglinsNeutral','isRepairable'],'net/neoforged/neoforge/items/ItemHandlerHelper.class':['giveItemToPlayer']}
    a=next(a for a in template['archives'] if a['path'].endswith('universal.jar'))
    with zipfile.ZipFile(a['path']) as jar:
        for c,ms in hooks.items():
            available={m['name'] for m in ClassFile(jar.read(c)).methods}
            hooks[c]=sorted(available if ms==['*'] else {m for m in available if m in ms or any(m.startswith('lambda$'+n+'$') for n in ms)})
    print('references',references(BATCH,raw,loader,hooks),flush=True)
    nestedpath=WORK/'twilightforest/nested-tf-asm.jar'
    with zipfile.ZipFile(nestedpath) as jar:asmclasses={n:['*'] for n in jar.namelist() if n.endswith('.class') and 'ReduceMovementFoodExhaustion' in n}
    assert asmclasses
    spec=dict(id=BATCH+'-asm',scope='Installed service-registered movement-exhaustion transformer; TFCoreMod service/registration protected in equipment witnesses.',archives=[dict(path=str(nestedpath),sha256=sha256(nestedpath),classes=asmclasses,resources=[])])
    write_json(OUT/'reference-specifications'/f'{BATCH}-asm.json',spec);write_json(OUT/'reference-evidence'/f'{BATCH}-asm.json',reference_collect(spec,source_aids=True))
    write_json(OUT/'twilightforest-travellers-core-caller-scan.json',scan_callers(target))

if __name__=='__main__':collect()
