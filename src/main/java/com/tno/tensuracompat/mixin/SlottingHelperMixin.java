package com.tno.tensuracompat.mixin;

import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import com.tno.tensuracompat.core.stage.ProductionStageScaling;
import com.tno.tensuracompat.core.stage.ScalableFamily;
import io.github.manasmods.tensura.enchantment.SlottingHelper;
import io.github.manasmods.tensura.entity.projectile.TensuraFlyingProjectile;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;

@Mixin(value = SlottingHelper.class, remap = false)
public abstract class SlottingHelperMixin {
    @WrapOperation(
            method = "onRelease",
            at = @At(
                    value = "INVOKE",
                    target = "Lio/github/manasmods/tensura/entity/projectile/TensuraFlyingProjectile;setDamage(F)V"
            )
    )
    private static void tno$scaleElementalProjectileDamage(
            TensuraFlyingProjectile projectile,
            float nativeProjectileDamage,
            Operation<Void> original,
            ItemStack gear,
            LivingEntity owner,
            int elapsedUseTicks
    ) {
        float scaled = ProductionStageScaling.scaleEligible(
                gear, ScalableFamily.ELEMENTAL_SLOTTING, nativeProjectileDamage);
        original.call(projectile, scaled);
    }
}
