"""Incremental installed Lich witnesses; no gameplay or production mutation."""
from twilight_evidence import *
from vanilla_reference import MojangNames, CLIENT

def collect():
    classes={p:['*'] for p in [
        'entity/boss/Lich','entity/boss/Lich$1','entity/boss/Lich$2','entity/boss/Lich$3',
        'entity/boss/BaseTFBoss','entity/ai/goal/LichShadowsGoal','entity/ai/goal/LichMinionsGoal',
        'entity/ai/goal/LichPopMobsGoal','entity/ai/goal/LichAbsorbMinionsGoal',
        'entity/monster/LichMinion','entity/monster/LichMinion$1',
        'entity/projectile/LichBolt','entity/projectile/LichBomb','entity/projectile/TwilightWandBolt',
        'item/TwilightWandItem','init/TFAttributes','block/OminousCandleBlock','block/entity/OminousCandleBlockEntity',
        'entity/EnforcedHomePoint','entity/ai/goal/AttemptToGoHomeGoal','block/LightableBlock']}
    classes['events/EntityEvents']=['*']
    resources=read_json(WORK/'twilightforest/resources.json')
    selected=[k for k in resources if '/tags/entity_type/' in k and any(x in k for x in ['lich','redirectable','inverted_healing','multiplayer_inclusive','skeletons','zombies','bosses','undead'])]
    print('native',native('twilight-lich',classes,selected))
    raw={
      'net/minecraft/world/entity/projectile/Projectile':['deflect','onDeflection','onHit','setOwner','getOwner','canHitEntity','addAdditionalSaveData','readAdditionalSaveData'],
      'net/minecraft/world/entity/projectile/ProjectileDeflection':['<clinit>'],
      'net/minecraft/world/entity/projectile/ProjectileUtil':['getEntityHitResult','getHitResultOnMoveVector','getHitResult'],
      'net/minecraft/world/entity/LivingEntity':['randomTeleport','isInvertedHealAndHarm','canBeAffected','heal'],
      'net/minecraft/world/entity/Entity':['hurt','deflection','isAttackable','canBeHitByProjectile','teleportTo'],
      'net/minecraft/world/effect/HealOrHarmMobEffect':['applyEffectTick','applyInstantenousEffect'],
      'net/minecraft/world/effect/PoisonMobEffect':['applyEffectTick'],
      'net/minecraft/world/entity/projectile/EvokerFangs':['dealDamageTo'],
      'net/minecraft/world/entity/monster/Guardian$GuardianAttackGoal':['tick'],
      'net/minecraft/world/level/block/entity/ConduitBlockEntity':['updateDestroyTarget'],
      'net/minecraft/world/entity/ai/behavior/warden/SonicBoom':['tick','checkExtraStartConditions','start','stop'],
      'net/minecraft/world/entity/projectile/ThrownPotion':['applySplash','makeAreaOfEffectCloud','onHit'],
      'net/minecraft/world/entity/AreaEffectCloud':['tick'],
      'net/minecraft/world/entity/projectile/Arrow':['doPostHurtEffects'],
      'net/minecraft/world/entity/projectile/WitherSkull':['onHitEntity','onHit'],
      'net/minecraft/world/entity/monster/Guardian':['registerGoals'],
      'net/minecraft/world/entity/monster/Guardian$GuardianAttackSelector':['test'],
      'net/minecraft/world/entity/monster/warden/Warden':['canTargetEntity'],
      'net/minecraft/world/entity/monster/Zombie':['doHurtTarget','createAttributes','finalizeSpawn'],
      'net/minecraft/world/entity/projectile/ThrownPotion':['applySplash','makeAreaOfEffectCloud','onHit','applyWater'],
      'net/minecraft/world/damagesource/DamageSources':['magic','indirectMagic','sonicBoom'],
    }
    # Pin synthetic deflection lambda bodies, not only invokedynamic bootstrap handles.
    names=MojangNames()
    with zipfile.ZipFile(CLIENT) as z:
        names.jar=z
        for c in ['net/minecraft/world/entity/projectile/ProjectileDeflection','net/minecraft/world/entity/ai/behavior/warden/SonicBoom','net/minecraft/world/level/block/entity/ConduitBlockEntity','net/minecraft/world/entity/monster/Zombie']:
            cls=ClassFile(z.read(names.named[c]+'.class'))
            raw[c]=sorted({names.member(cls.name,m['name'],m['descriptor']) for m in cls.methods})
    loader={c+'.class':ms for c,ms in raw.items()}
    print('reference',references('twilight-lich',raw,loader))
    # Narrow raw tag closure for Lich's inherited potion inversion/eligibility.
    tag_spec=dict(classes={},resources=['data/minecraft/tags/entity_type/'+s+'.json' for s in ['undead','skeletons','inverted_healing_and_harm','ignores_poison_and_regen']])
    write_json(OUT/'vanilla-specifications/twilight-lich-tags.json',tag_spec)
    write_json(OUT/'vanilla-evidence/twilight-lich-tags.json',prepare(tag_spec))

if __name__=='__main__':collect()
