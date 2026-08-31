package com.tno.tensuracompat.mixin;

import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import com.tno.tensuracompat.core.stage.NativeScalableDamage;
import io.github.manasmods.tensura.damage.TensuraDamageHelper;
import io.github.manasmods.tensura.enchantment.effect.SpiritualDamageEntity;
import net.minecraft.core.Holder;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageType;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.enchantment.EnchantedItemInUse;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;

@Mixin(value = SpiritualDamageEntity.class, remap = false)
public abstract class SpiritualDamageEntityMixin {
    @Shadow
    public abstract Holder<DamageType> damageType();

    @WrapOperation(
            method = "postDamage",
            at = @At(
                    value = "INVOKE",
                    target = "Lio/github/manasmods/tensura/damage/TensuraDamageHelper;directSpiritualHurt(Lnet/minecraft/world/entity/LivingEntity;Lnet/minecraft/world/entity/Entity;Lnet/minecraft/world/damagesource/DamageSource;F)Z"
            )
    )
    private boolean tno$scaleEligibleNativeSoulDamage(
            LivingEntity damaged,
            Entity attacker,
            DamageSource source,
            float nativeEligibleAmount,
            Operation<Boolean> original,
            int enchantmentLevel,
            EnchantedItemInUse enchantedItem,
            Entity target,
            float multiplier
    ) {
        float scaled = NativeScalableDamage.scaleSpiritualDamage(
                damageType(), enchantedItem, nativeEligibleAmount);
        return original.call(damaged, attacker, source, scaled);
    }
}
