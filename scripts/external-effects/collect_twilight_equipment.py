"""Conventional gear, ignition/shatter, and installed nested source transformer."""
from twilight_evidence import *
from vanilla_reference import MojangNames,CLIENT
from selected_reference import collect as reference_collect
import io
BATCH='twilight-equipment'
FULL=['item/FierySwordItem','item/FieryPickItem','item/FieryArmorItem','item/GlassSwordItem','item/CustomDamageProvider','item/CustomDamageSwordItem','item/KnightmetalShieldItem','item/ArcticArmorItem','item/PhantomArmorItem','item/MysticCrownItem','util/TFToolMaterials','init/TFArmorMaterials','asmhooks/DamageSourceHooks']
TOKENS=['FIERY_SWORD','FIERY_PICKAXE','FieryArmorItem','GlassSwordItem','INFINITE_GLASS_SWORD','CustomDamageProvider','CustomDamageSwordItem','STALE_SANDWICH','KnightmetalShieldItem','ArcticArmorItem','MysticCrownItem']
NESTED='META-INF/jarjar/s.tf-asm-4.8.3345.jar'

def scan_callers(target):
    hits=[];providers=[]
    with zipfile.ZipFile(target['path']) as jar:
        for entry in jar.namelist():
            if not entry.startswith('twilightforest/') or not entry.endswith('.class'):continue
            b=jar.read(entry)
            if not any(s.encode() in b for s in TOKENS):continue
            c=ClassFile(b)
            if 'twilightforest/item/CustomDamageProvider' in c.interfaces:providers.append(entry)
            for m in c.methods:
                for i in c.instructions(m.get('code',b'')):
                    if any(s in str(i['operand']) for s in TOKENS):hits.append(dict(entry=entry,class_sha256=byte_hash(b),method=m['name'],descriptor=m['descriptor'],instruction=i))
        b=jar.read(NESTED)
        with zipfile.ZipFile(io.BytesIO(b)) as asm:
            nested=dict(outer_jar_sha256=target['sha256'],entry=NESTED,sha256=byte_hash(b),classes=[n for n in asm.namelist() if n.endswith('.class')],service=asm.read('META-INF/services/net.neoforged.neoforgespi.coremod.ICoreMod').decode())
    return dict(jar_sha256=target['sha256'],scope='All installed TF instruction callers of actual gear mechanisms and all CustomDamageProvider implementers. Nested source transformer registration binding, not whole ASM closure.',needles=TOKENS,hits=hits,custom_damage_provider_implementers=providers,nested=nested)

def collect():
    target=next(t for t in read_json(OUT/'jar-inventory.json')['targets'] if t['key']=='twilightforest');res=read_json(WORK/'twilightforest/resources.json')
    words=['fiery_','glass_sword','stale_','knightmetal_shield','arctic_','naga_chestplate','naga_leggings','ironwood_','steeleaf_','phantom_helmet','phantom_chestplate','mystic_crown']
    selected=[p for p,v in res.items() if p.startswith('data/') and any(x in p+' '+str(v) for x in words)]
    selected+=['META-INF/jarjar/metadata.json','META-INF/neoforge.mods.toml']
    classes={c:['*'] for c in FULL};classes.update({'events/ToolEvents':['setup','fieryToolSetFire'],'events/EntityEvents':['setup','entityHurts','getGearCoverage'],'init/TFCreativeTabs':['createGlassSwordAndLoreVer']})
    with zipfile.ZipFile(target['path']) as jar:
        for c,needles in [('init/TFItems',TOKENS+['TFArmorMaterials.','TFToolMaterials.IRONWOOD','TFToolMaterials.STEELEAF']),('init/TFDataComponents',['infinite_glass_sword'])]:
            cls=ClassFile(jar.read('twilightforest/'+c+'.class'));classes[c]=[m['name'] for m in cls.methods if m['name']=='<clinit>' or any(any(n in str(i['operand']) for n in needles) for i in cls.instructions(m.get('code',b'')))]
        nestedpath=WORK/'twilightforest/nested-tf-asm.jar';nestedpath.write_bytes(jar.read(NESTED))
    print('native',native(BATCH,classes,selected),flush=True)
    asmclasses=['twilightforest/asm/transformers/damagesources/DamageSourcesTransformer.class','twilightforest/asm/TFCoreMod.class','twilightforest/asm/ASMUtil.class']
    spec=dict(id=BATCH+'-asm',scope='Installed nested archive source-factory transformer, service and registration. Other registered transformers pending dedicated coverage.',archives=[dict(path=str(nestedpath),sha256=sha256(nestedpath),classes={c:['*'] for c in asmclasses},resources=['META-INF/services/net.neoforged.neoforgespi.coremod.ICoreMod'])])
    write_json(OUT/'reference-specifications'/f'{BATCH}-asm.json',spec);write_json(OUT/'reference-evidence'/f'{BATCH}-asm.json',reference_collect(spec,source_aids=True))
    raw={'net/minecraft/world/item/TieredItem':['<init>','getEnchantmentValue','isValidRepairItem'],'net/minecraft/world/item/Tiers':['<clinit>','getUses','getAttackDamageBonus'],'net/minecraft/world/item/SwordItem':['<init>','createAttributes','hurtEnemy','postHurtEnemy'],'net/minecraft/world/item/DiggerItem':['<init>','createAttributes','hurtEnemy','postHurtEnemy'],'net/minecraft/world/item/ItemStack':['hurtEnemy','postHurtEnemy','hurtAndBreak','isDamageableItem','canBeHurtBy'],'net/minecraft/world/entity/player/Player':['attack','getWeaponItem','hurtArmor','hurtCurrentlyUsedShield','disableShield','actuallyHurt'],'net/minecraft/world/entity/LivingEntity':['getWeaponItem','getArmorSlots','doHurtEquipment','getDamageAfterArmorAbsorb','igniteForTicks','canFreeze','isDamageSourceBlocked','isBlocking','blockedByShield'],'net/minecraft/world/entity/Entity':['igniteForSeconds','igniteForTicks','baseTick','canFreeze'],'net/minecraft/world/entity/Mob':['doHurtTarget','hurtArmor'],'net/minecraft/world/item/ArmorItem':['<init>','getDefaultAttributeModifiers','dispenseArmor','use','getEquipmentSlot'],'net/minecraft/world/item/ArmorItem$Type':['<clinit>','getDurability'],'net/minecraft/world/item/ShieldItem':['<init>','use','getUseDuration','getUseAnimation','isValidRepairItem'],'net/minecraft/world/item/Equipable':['swapWithEquipmentSlot'],'net/minecraft/world/level/block/PowderSnowBlock':['getCollisionShape','canEntityWalkOnPowderSnow'],'net/minecraft/world/damagesource/DamageSources':['mobAttack','playerAttack','source','onFire'],'net/minecraft/world/damagesource/DamageSource':['<init>','getDirectEntity','getEntity'],'net/minecraft/world/damagesource/CombatRules':['getDamageAfterAbsorb']}
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
    hooks={'net/neoforged/neoforge/common/CommonHooks.class':['onArmorHurt','onLivingDamagePost','onEntityIncomingDamage'],'net/neoforged/neoforge/common/extensions/IItemExtension.class':['canWalkOnPowderedSnow','canPerformAction'],'net/neoforged/neoforge/event/entity/living/LivingDamageEvent$Post.class':['<init>','getOriginalDamage']}
    print('references',references(BATCH,raw,loader,hooks),flush=True)
    write_json(OUT/'twilightforest-equipment-caller-scan.json',scan_callers(target))

if __name__=='__main__':collect()
