package com.tno.tensuracompat.mixin;

import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import com.tno.tensuracompat.core.stage.NativeScalableDamage;
import io.github.manasmods.tensura.enchantment.effect.AdditionalDamageEntity;
import net.minecraft.core.Holder;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageType;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.item.enchantment.EnchantedItemInUse;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;

@Mixin(value = AdditionalDamageEntity.class, remap = false)
public abstract class AdditionalDamageEntityMixin {
    @Shadow
    public abstract Holder<DamageType> damageType();

    @WrapOperation(
            method = "postDamage",
            at = @At(
                    value = "INVOKE",
                    target = "Lnet/minecraft/world/entity/Entity;hurt(Lnet/minecraft/world/damagesource/DamageSource;F)Z"
            )
    )
    private boolean tno$scaleEligibleNativeDamage(
            Entity damaged,
            DamageSource source,
            float nativeEligibleAmount,
            Operation<Boolean> original,
            int enchantmentLevel,
            EnchantedItemInUse enchantedItem,
            Entity target,
            float multiplier
    ) {
        float scaled = NativeScalableDamage.scaleAdditionalDamage(
                damageType(), enchantedItem, nativeEligibleAmount);
        return original.call(damaged, source, scaled);
    }
}
