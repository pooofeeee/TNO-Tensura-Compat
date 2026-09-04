package com.tno.tensuracompat.mixin;

import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import com.tno.tensuracompat.core.stage.MatchingResistanceRecovery;
import com.tno.tensuracompat.core.stage.NativeScalableDamage;
import com.tno.tensuracompat.debug.Phase6CalibrationContext;
import com.tno.tensuracompat.debug.Phase5FSuiteBBenchmark;
import io.github.manasmods.tensura.enchantment.effect.AdditionalDamageEntity;
import net.minecraft.core.Holder;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageType;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
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
        float recovered = damaged instanceof LivingEntity livingTarget
                ? NativeScalableDamage.additionalDamageFamily(damageType())
                        .map(family -> MatchingResistanceRecovery.apply(
                                enchantedItem.itemStack(), family, livingTarget, source, scaled))
                        .orElse(scaled)
                : scaled;
        if (!(damaged instanceof LivingEntity livingTarget)) {
            return original.call(damaged, source, recovered);
        }
        var family = NativeScalableDamage.additionalDamageFamily(damageType());
        if (family.isEmpty()) return original.call(damaged, source, recovered);
        var scope = Phase6CalibrationContext.open(enchantedItem.itemStack(), family.get(), livingTarget,
                nativeEligibleAmount, scaled, recovered);
        try {
            boolean accepted = original.call(damaged, source, recovered);
            scope.ifPresent(value -> Phase5FSuiteBBenchmark.captureCalibrationTrace(value.snapshot()));
            return accepted;
        }
        finally {
            scope.ifPresent(Phase6CalibrationContext.Scope::close);
        }
    }
}
