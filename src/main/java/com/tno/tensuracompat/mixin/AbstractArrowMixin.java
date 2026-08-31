package com.tno.tensuracompat.mixin;

import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import com.tno.tensuracompat.core.stage.SeveranceStageScaling;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.enchantment.EnchantmentHelper;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;

/** Keeps the eligible Severance delta in the one native physical arrow calculation. */
@Mixin(AbstractArrow.class)
public abstract class AbstractArrowMixin {
    @Unique
    private SeveranceStageScaling.Adjustment tno$severanceAdjustment;

    @WrapOperation(
            method = "onHitEntity",
            at = @At(
                    value = "INVOKE",
                    target = "Lnet/minecraft/world/item/enchantment/EnchantmentHelper;modifyDamage(Lnet/minecraft/server/level/ServerLevel;Lnet/minecraft/world/item/ItemStack;Lnet/minecraft/world/entity/Entity;Lnet/minecraft/world/damagesource/DamageSource;F)F"
            )
    )
    private float tno$carryEligibleSeveranceBeforeNativeCeil(
            ServerLevel level,
            ItemStack weapon,
            Entity target,
            DamageSource source,
            float nativeModifiedBaseInput,
            Operation<Float> original
    ) {
        float nativeModifiedBase = original.call(
                level, weapon, target, source, nativeModifiedBaseInput);
        tno$severanceAdjustment = SeveranceStageScaling
                .adjustment(weapon, nativeModifiedBase)
                .orElse(null);
        return tno$severanceAdjustment == null
                ? nativeModifiedBase
                : (float) tno$severanceAdjustment.stagedModifiedBase();
    }

    @WrapOperation(
            method = "onHitEntity",
            at = @At(
                    value = "INVOKE",
                    target = "Lnet/minecraft/util/Mth;ceil(D)I"
            )
    )
    private int tno$preservePositiveSeveranceDelta(
            double stagedPreRound,
            Operation<Integer> original
    ) {
        if (tno$severanceAdjustment == null) {
            return original.call(stagedPreRound);
        }
        double speed = ((AbstractArrow) (Object) this).getDeltaMovement().length();
        int rounded = SeveranceStageScaling.roundedProjectileDamage(
                speed, tno$severanceAdjustment);
        tno$severanceAdjustment = null;
        return rounded;
    }
}
