"""Pin only missing exact native comparison methods for Frosted and its delivery."""
from twilight_evidence import *

raw={
 'net/minecraft/world/entity/Entity':['tick','baseTick','move','setIsInPowderSnow','canFreeze','getTicksRequiredToFreeze','getPercentFrozen','isFullyFrozen'],
 'net/minecraft/world/entity/LivingEntity':['baseTick','tick','aiStep','tickEffects','canFreeze','addEffect','removeEffect','removeEffectNoUpdate','onEffectAdded','onEffectUpdated','onEffectRemoved','tryAddFrost','removeFrost','travel'],
 'net/minecraft/world/entity/player/Player':['attack','hurt','isInvulnerableTo'],
 'net/minecraft/world/item/ItemStack':['hurtEnemy','postHurtEnemy'],
 'net/minecraft/world/item/SwordItem':['hurtEnemy','postHurtEnemy'],
 'net/minecraft/world/entity/projectile/Arrow':['doPostHurtEffects'],
 'net/minecraft/world/entity/projectile/SpectralArrow':['doPostHurtEffects'],
 'net/minecraft/world/entity/projectile/ThrowableProjectile':['tick'],
 'net/minecraft/world/entity/projectile/Projectile':['onHit','hitTargetOrDeflectSelf','canHitEntity'],
 'net/minecraft/core/dispenser/ProjectileDispenseBehavior':['<init>','execute'],
 'net/minecraft/world/item/ProjectileItem':['shoot','createDispenseConfig'],
 'net/minecraft/world/item/ProjectileItem$DispenseConfig':['<clinit>'],
 'net/minecraft/world/item/ProjectileItem$DispenseConfig$Builder':['<init>','build'],
 'net/minecraft/world/level/block/DispenserBlock':['registerProjectileBehavior'],
 'net/minecraft/world/entity/projectile/AbstractArrow':['<init>','defineSynchedData','tick'],
 'net/minecraft/world/item/enchantment/EnchantmentHelper':['doPostAttackEffects','doPostAttackEffectsWithItemSource','runIterationOnEquipment','runIterationOnItem','lambda$doPostAttackEffectsWithItemSource$11','lambda$doPostAttackEffectsWithItemSource$10'],
 'net/minecraft/world/item/enchantment/Enchantment':['doPostAttack'],
 'net/minecraft/world/item/enchantment/effects/AllOf$EntityEffects':['apply'],
 'net/minecraft/world/item/enchantment/effects/DamageItem':['apply'],
 'net/minecraft/world/entity/animal/Wolf':['actuallyHurt','canArmorAbsorb'],
 'net/minecraft/world/effect/MobEffectInstance':['<init>','setDetailsFrom'],
 'net/minecraft/world/damagesource/DamageSource':['scalesWithDifficulty'],
}
loader={c+'.class':ms for c,ms in raw.items()}
loader['net/minecraft/world/entity/LivingEntity.class']+=['getArmorSlots']
loader['net/minecraft/world/damagesource/DamageScaling.class']=['<init>','<clinit>','getScalingFunction']
hooks={
 'net/neoforged/neoforge/common/CommonHooks.class':['onEntityIncomingDamage','onLivingDamagePre','onLivingDamagePost','onDamageBlock'],
 'net/neoforged/neoforge/event/entity/living/LivingDamageEvent$Post.class':['<init>','getOriginalDamage','getNewDamage'],
 'net/neoforged/neoforge/common/damagesource/DamageContainer.class':['<init>','getOriginalDamage','getNewDamage','setNewDamage'],
 'net/neoforged/neoforge/common/damagesource/IScalingFunction.class':['<clinit>','lambda$static$0'],
 'net/neoforged/neoforge/common/damagesource/IScalingFunction$1.class':['<clinit>'],
}
if __name__=='__main__':print(references('twilight-frosted',raw,loader,hooks))
