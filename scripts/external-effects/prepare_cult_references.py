"""Select inherited Cult mechanics for raw vanilla and exact installed-loader comparison."""
from catalog_common import *
from vanilla_reference import prepare
from selected_reference import collect
from classfile import ClassFile

classes={
 'world/entity/ai/goal/Goal':['requiresUpdateEveryTick','adjustedTickDelay','reducedTickDelay'],
 'world/entity/ai/goal/GoalSelector':['tick','tickRunningGoals'],
 'world/entity/ai/goal/WrappedGoal':['tick','requiresUpdateEveryTick'],
 'world/entity/Mob':['serverAiStep'],
 'world/entity/player/Inventory':['<init>','getContainerSize','getItem','setItem'],
 'world/item/ArrowItem':['createArrow','asProjectile'],
 'world/item/BowItem':['releaseUsing'],
 'world/item/CrossbowItem':['createProjectile'],
 'world/item/ProjectileWeaponItem':['draw','shoot','createProjectile'],
 'world/entity/monster/WitherSkeleton':['doHurtTarget'],
 'world/entity/projectile/EvokerFangs':['tick','dealDamageTo'],
 'world/entity/animal/IronGolem':['doHurtTarget'],
 'world/item/PotionItem':['finishUsingItem'],
 'world/item/HoneyBottleItem':['finishUsingItem'],
 'world/level/block/SlimeBlock':['fallOn','updateEntityAfterFallOn','bounceUp','stepOn'],
 'world/level/block/HoneyBlock':['fallOn','entityInside','isSlidingDown','doSlideMovement'],
 'world/level/block/PointedDripstoneBlock':['fallOn','onProjectileHit','tick','spawnFallingStalactite','isStalactite','isPointedDripstoneWithDirection','isStalagmite'],
 'world/level/block/state/BlockBehaviour$Properties':['ofFullCopy','ofLegacyCopy'],
 'world/level/block/Blocks':['<clinit>'],
 'world/level/block/state/BlockBehaviour':['getCollisionShape','entityInside'],
 'world/entity/Entity':['getBlockSpeedFactor','getBlockJumpFactor','igniteForSeconds','setRemainingFireTicks','isInvulnerableTo','causeFallDamage','push'],
 'world/effect/MobEffects':['<clinit>'],
 'world/effect/MobEffect':['createModifiers','addAttributeModifiers','applyInstantenousEffect'],
 'world/effect/RegenerationMobEffect':['applyEffectTick','shouldApplyEffectTickThisTick'],
 'world/effect/WitherMobEffect':['applyEffectTick','shouldApplyEffectTickThisTick'],
 'world/effect/BadOmenMobEffect':['applyEffectTick','shouldApplyEffectTickThisTick'],
 'world/effect/HealOrHarmMobEffect':['applyEffectTick','applyInstantenousEffect'],
 'world/effect/AbsorptionMobEffect':['applyEffectTick','shouldApplyEffectTickThisTick','onEffectStarted'],
 'world/item/MilkBucketItem':['finishUsingItem'],
 'world/level/block/DispenserBlock':['getDispenseMethod'],
 'core/dispenser/DispenseItemBehavior':['bootStrap'],
 'client/renderer/FogRenderer$BlindnessFogFunction':['setupFog'],
 'client/renderer/FogRenderer$DarknessFogFunction':['setupFog'],
 'world/entity/LivingEntity':['knockback','heal','setHealth','die','removeAllEffects','getDamageAfterMagicAbsorb','getDamageAfterArmorAbsorb','updateInvisibilityStatus','getVisibilityPercent','canBeSeenAsEnemy','hasLineOfSight','calculateFallDamage'],
}
# NeoForge-only removal method is covered by an exact loader witness below, not invented in raw vanilla.
spec=dict(classes={'net/minecraft/'+k:v for k,v in classes.items()},resources=[])
write_json(OUT/'vanilla-specifications/cult-completion.json',spec)
result=prepare(spec)
write_json(OUT/'vanilla-evidence/cult-completion.json',result)
loader=read_json(OUT/'reference-specifications/vv-loader-244.json')
archives=[]
for a in loader['archives']:
 if a['path'].endswith('-client.jar'):
  with zipfile.ZipFile(a['path']) as jar:
   selected={name+'.class':wanted for name,wanted in spec['classes'].items() if name+'.class' in jar.namelist()}
   for name in selected:
    cls=ClassFile(jar.read(name));available={m['name'] for m in cls.methods}
    selected[name]=[m for m in selected[name] if m in available]
   selected={k:v for k,v in selected.items() if v}
  archives.append(dict(path=a['path'],sha256=a['sha256'],classes=selected))
reference=dict(id='cult-loader-244',scope='Cult inherited-path comparison, exact installed NeoForge21.1.244; compare raw vanilla separately.',archives=archives)
write_json(OUT/'reference-specifications/cult-loader-244.json',reference)
write_json(OUT/'reference-evidence/cult-loader-244.json',collect(reference,source_aids=True))
print(len(result['classes']),'raw classes;',sum(len(c['methods']) for c in result['classes']),'raw methods;',len(archives[0]['classes']),'patched classes')
