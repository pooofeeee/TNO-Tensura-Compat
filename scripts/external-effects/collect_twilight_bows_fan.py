"""Bow customization and fan control, pinned against installed native callbacks."""
from twilight_evidence import *
from vanilla_reference import MojangNames,CLIENT
BATCH='twilight-bows-fan'
FULL=['item/EnderBowItem','item/SeekerBowItem','item/TripleBowItem','entity/projectile/SeekerArrow','entity/projectile/TFArrow','item/PeacockFanItem','dispenser/FeatherFanDispenseBehavior','network/MovePlayerPacket']
NEEDLES=['SeekerArrow.<init>','TFItems.ENDER_BOW','TFItems.SEEKER_BOW','TFItems.TRIPLE_BOW','TFItems.PEACOCK_FEATHER_FAN','TFDataAttachments.FEATHER_FAN','twilightforest:ender','FeatherFanDispenseBehavior.<init>']

def scan_callers(target):
    hits=[]
    with zipfile.ZipFile(target['path']) as jar:
        for entry in jar.namelist():
            if not entry.startswith('twilightforest/') or not entry.endswith('.class'):continue
            b=jar.read(entry)
            if not any(s.encode() in b for s in ['SeekerArrow','ENDER_BOW','SEEKER_BOW','TRIPLE_BOW','PEACOCK_FEATHER_FAN','FEATHER_FAN','twilightforest:ender','FeatherFanDispenseBehavior']):continue
            c=ClassFile(b)
            for m in c.methods:
                for i in c.instructions(m.get('code',b'')):
                    if any(s in str(i['operand']) for s in NEEDLES):hits.append(dict(entry=entry,class_sha256=byte_hash(b),method=m['name'],descriptor=m['descriptor'],instruction=i))
    return dict(jar_sha256=target['sha256'],scope='All installed-TF instruction callers of actual bow item/Seeker constructor/Ender marker and fan resource/dispenser producer.',needles=NEEDLES,hits=hits)

def collect():
    target=next(t for t in read_json(OUT/'jar-inventory.json')['targets'] if t['key']=='twilightforest');res=read_json(WORK/'twilightforest/resources.json')
    selected=[p for p,v in res.items() if p.startswith('data/') and any(x in p+' '+str(v) for x in ['ender_bow','seeker_bow','triple_bow','peacock_feather_fan'])]
    classes={c:['*'] for c in FULL};classes.update({'events/ToolEvents':['setup','onEnderBowHit'],'events/CapabilityEvents':['setup','updatePlayerCaps'],'dispenser/TFDispenserBehaviors':['init'],'util/WorldUtil':['getAllInBB']})
    with zipfile.ZipFile(target['path']) as jar:
        for c,needles in [('init/TFItems',['EnderBowItem','SeekerBowItem','TripleBowItem','PeacockFanItem']),('init/TFDataAttachments',['ByteBufCodecs.BOOL','Boolean.FALSE']),('events/RegistrationEvents',['MovePlayerPacket']),('block/LightableBlock',['extinguish'])]:
            cls=ClassFile(jar.read('twilightforest/'+c+'.class'));classes[c]=[m['name'] for m in cls.methods if m['name']=='<clinit>' or any(any(n in str(i['operand']) for n in needles) for i in cls.instructions(m.get('code',b''))) or (c=='block/LightableBlock' and m['name']=='extinguish')]
    classes['block/LightableBlock']=sorted(set(classes['block/LightableBlock']+['setLit']))
    print('native',native(BATCH,classes,selected))
    raw={'net/minecraft/world/item/BowItem':['releaseUsing','use','getPowerForTime','shootProjectile','getUseDuration','getAllSupportedProjectiles'], 'net/minecraft/world/item/ProjectileWeaponItem':['createProjectile','shoot','draw','useAmmo','getDurabilityUse','getHeldProjectile'], 'net/minecraft/world/entity/projectile/AbstractArrow':['<init>','tick','onHitEntity','doPostHurtEffects','doKnockback','addAdditionalSaveData','readAdditionalSaveData','getWeaponItem'], 'net/minecraft/world/entity/projectile/Arrow':['doPostHurtEffects','getPotionContents','<init>'], 'net/minecraft/world/entity/projectile/SpectralArrow':['doPostHurtEffects','<init>'], 'net/minecraft/world/entity/projectile/ProjectileUtil':['getMobArrow','getWeaponHoldingHand'], 'net/minecraft/world/entity/monster/AbstractSkeleton':['reassessWeaponGoal','performRangedAttack','getArrow','canFireProjectileWeapon','setItemSlot'], 'net/minecraft/world/entity/monster/Monster':['getProjectile'], 'net/minecraft/world/entity/ai/goal/RangedBowAttackGoal':['canUse','canContinueToUse','isHoldingBow','tick'], 'net/minecraft/world/entity/player/Player':['tick','getProjectile','causeFallDamage','setIgnoreFallDamageFromCurrentImpulse','tryResetCurrentImpulseContext','resetCurrentImpulseContext','addAdditionalSaveData','readAdditionalSaveData'], 'net/minecraft/world/entity/Entity':['teleportTo','teleportPassengers','startRiding','stopRiding','push','setDeltaMovement'], 'net/minecraft/server/level/ServerPlayer':['teleportTo','startRiding','stopRiding'], 'net/minecraft/world/level/EntityGetter':['getEntitiesOfClass'], 'net/minecraft/world/item/ItemStack':['hurtAndBreak','getItem'], 'net/minecraft/world/entity/LivingEntity':['startUsingItem','getUseItem','isBlocking'], 'net/minecraft/world/level/block/AbstractCandleBlock':['extinguish']}
    raw['net/minecraft/world/item/ArrowItem']=['createArrow','isInfinite']
    raw['net/minecraft/world/item/SpectralArrowItem']=['createArrow']
    raw['net/minecraft/world/entity/projectile/AbstractArrow']+=['setOwner','tryPickup','getPickupItem']
    raw['net/minecraft/world/entity/projectile/Projectile']=['getEffectSource']
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
            if c.endswith('/ProjectileWeaponItem.class'):wanted=wanted+['customArrow','getAllSupportedProjectiles','getSupportedHeldProjectiles']
            loader[c]=sorted({m for m in available if m in wanted or any(m.startswith('lambda$'+n+'$') for n in wanted if not n.startswith('lambda$'))})
    hooks={'net/neoforged/neoforge/event/EventHooks.class':['onArrowLoose','onArrowNock','onProjectileImpact'],'net/neoforged/neoforge/common/extensions/IItemExtension.class':['canPerformAction']}
    print('references',references(BATCH,raw,loader,hooks));write_json(OUT/'twilightforest-bows-fan-caller-scan.json',scan_callers(target))

if __name__=='__main__':collect()
