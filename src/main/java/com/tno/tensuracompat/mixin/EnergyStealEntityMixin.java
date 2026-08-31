package com.tno.tensuracompat.mixin;

import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import com.tno.tensuracompat.core.stage.ProductionStageScaling;
import com.tno.tensuracompat.core.stage.ScalableFamily;
import io.github.manasmods.tensura.enchantment.effect.EnergyStealEntity;
import io.github.manasmods.tensura.util.EnergyHelper;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.enchantment.EnchantedItemInUse;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;

@Mixin(value = EnergyStealEntity.class, remap = false)
public abstract class EnergyStealEntityMixin {
    @WrapOperation(
            method = "applyEnergySteal",
            at = @At(
                    value = "INVOKE",
                    target = "Lio/github/manasmods/tensura/util/EnergyHelper;drainEnergy(Lnet/minecraft/world/entity/LivingEntity;Lnet/minecraft/world/entity/Entity;DZLio/github/manasmods/tensura/util/EnergyHelper$DrainType;Lio/github/manasmods/tensura/util/EnergyHelper$GainType;)Z"
            )
    )
    private boolean tno$scaleEligibleDrainPercentage(
            LivingEntity drained,
            Entity source,
            double nativeAmount,
            boolean percentage,
            EnergyHelper.DrainType drainType,
            EnergyHelper.GainType gainType,
            Operation<Boolean> original,
            int enchantmentLevel,
            EnchantedItemInUse enchantedItem,
            Entity target
    ) {
        double scaledAmount = nativeAmount;
        if (percentage && drainType == EnergyHelper.DrainType.EP
                && gainType == EnergyHelper.GainType.NORMAL) {
            scaledAmount = ProductionStageScaling.scaleEligible(
                    enchantedItem.itemStack(), ScalableFamily.ENERGY_STEAL, nativeAmount);
        }
        return original.call(drained, source, scaledAmount, percentage, drainType, gainType);
    }
}
