"""Fortification admission/resource and Lifedrain native payloads; no runtime."""
from twilight_evidence import *
from vanilla_reference import MojangNames,CLIENT
BATCH='twilight-scepter-payloads'
FULL=['item/FortificationWandItem','components/entity/FortificationShieldAttachment','command/ShieldCommand','item/LifedrainScepterItem','item/TwilightWandItem']
NEEDLES=['TFDamageTypes.LIFEDRAIN','FortificationShieldAttachment.setShields','FortificationShieldAttachment.addShields','FortificationShieldAttachment.breakShield','TFDataAttachments.FORTIFICATION_SHIELDS','TFItems.MYSTIC_CROWN']

def scan_callers(target):
    hits=[]
    with zipfile.ZipFile(target['path']) as jar:
        for entry in jar.namelist():
            if not entry.startswith('twilightforest/') or not entry.endswith('.class'):continue
            b=jar.read(entry)
            if not any(s.encode() in b for s in ['LIFEDRAIN','FortificationShieldAttachment','FORTIFICATION_SHIELDS','MYSTIC_CROWN']):continue
            c=ClassFile(b)
            for m in c.methods:
                for i in c.instructions(m.get('code',b'')):
                    if any(s in str(i['operand']) for s in NEEDLES):hits.append(dict(entry=entry,class_sha256=byte_hash(b),method=m['name'],descriptor=m['descriptor'],instruction=i))
    return dict(jar_sha256=target['sha256'],scope='All native TF instruction callers of actual Lifedrain type, Fortification attachment/producers and Crown consumers. Other Crown material/producer effects scoped separately.',needles=NEEDLES,hits=hits)

def collect():
    target=next(t for t in read_json(OUT/'jar-inventory.json')['targets'] if t['key']=='twilightforest');res=read_json(WORK/'twilightforest/resources.json')
    selected=[p for p,v in res.items() if ('/tags/' in p and any(x in str(v) for x in ['lifedrain','bosses','mystic_crown'])) or p.endswith('/lifedrain.json') or 'lifedrain_scepter_kill_bonus' in p]
    classes={c:['*'] for c in FULL};classes.update({'events/CapabilityEvents':['setup','updateShields','absorbShieldHits'],'command/TFCommand':['register'],'util/entities/EntityUtil':['getDeathSound'],'events/ToolEvents':['addExtraAxeChargingDamage','doKnightmetalToolLogic']})
    with zipfile.ZipFile(target['path']) as jar:
        c=ClassFile(jar.read('twilightforest/init/TFDataAttachments.class'))
        classes['init/TFDataAttachments']=[m['name'] for m in c.methods if m['name']=='<clinit>' or any('FortificationShieldAttachment' in str(i['operand']) for i in c.instructions(m.get('code',b'')))]
    print('native',native(BATCH,classes,selected))
    raw={'net/minecraft/world/entity/LivingEntity':['hurt','die','heal','checkTotemDeathProtection','getDamageAfterMagicAbsorb','updateUsingItem','updatingUsingItem','startUsingItem','stopUsingItem','isPickable'], 'net/minecraft/world/entity/player/Player':['hurt','aiStep','isCreative'], 'net/minecraft/world/food/FoodData':['eat'], 'net/minecraft/server/level/ServerPlayer':['restoreFrom'], 'net/minecraft/world/entity/Entity':['saveWithoutId','load','discard'], 'net/minecraft/world/item/ItemCooldowns':['isOnCooldown','addCooldown'], 'net/minecraft/world/effect/MobEffect':['addAttributeModifiers'], 'net/minecraft/world/effect/MobEffects':['<clinit>']}
    raw['net/minecraft/world/food/FoodData'].append('add')
    raw['net/minecraft/world/food/FoodConstants']=['saturationByModifier']
    raw['net/minecraft/server/level/ServerPlayerGameMode']=['useItem']
    names=MojangNames()
    with zipfile.ZipFile(CLIENT) as jar:
        names.jar=jar
        for c,ms in raw.items():
            cls=ClassFile(jar.read(names.named[c]+'.class'));available={names.member(cls.name,m['name'],m['descriptor']) for m in cls.methods}
            raw[c]=sorted({m for m in available if m in ms or any(m.startswith('lambda$'+n+'$') for n in ms)})
    loader={c+'.class':list(ms) for c,ms in raw.items()};template=read_json(OUT/'reference-specifications/vv-loader-244.json');a=next(a for a in template['archives'] if a['path'].endswith('client.jar'))
    with zipfile.ZipFile(a['path']) as jar:
        for c in loader:
            if c not in jar.namelist():continue
            available={m['name'] for m in ClassFile(jar.read(c)).methods};wanted=raw[c[:-6]]
            loader[c]=sorted({m for m in available if m in wanted or any(m.startswith('lambda$'+n+'$') for n in wanted if not n.startswith('lambda$'))})
    hooks={};a=next(a for a in template['archives'] if a['path'].endswith('universal.jar'))
    with zipfile.ZipFile(a['path']) as jar:
        for c in ['AttachmentHolder','AttachmentType','AttachmentType$Builder','AttachmentInternals']:
            entry='net/neoforged/neoforge/attachment/'+c+'.class';hooks[entry]=sorted({m['name'] for m in ClassFile(jar.read(entry)).methods})
    hooks['net/neoforged/neoforge/common/extensions/IEntityExtension.class']=['copyAttachmentsFrom']
    hooks['net/neoforged/neoforge/event/EventHooks.class']=['onPlayerClone','onItemUseStart','onItemUseTick']
    print('references',references(BATCH,raw,loader,hooks))
    write_json(OUT/'twilightforest-scepter-payloads-caller-scan.json',scan_callers(target))

if __name__=='__main__':collect()
