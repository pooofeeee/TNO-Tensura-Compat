package com.tno.tensuracompat.mixin;

import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import com.tno.tensuracompat.debug.Phase6EnergyNativePathResearch;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.projectile.AbstractArrow;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;

/** Exactly one unchanged invocation of the existing physical call. */
@Mixin(AbstractArrow.class)
public abstract class EnergyArrowObservationMixin {
    @WrapOperation(method = "onHitEntity", at = @At(value = "INVOKE",
            target = "Lnet/minecraft/world/entity/Entity;hurt(Lnet/minecraft/world/damagesource/DamageSource;F)Z"))
    private boolean tno$energyPhysical(Entity target, DamageSource source, float amount, Operation<Boolean> original) {
        Phase6EnergyNativePathResearch.observe("physical_attempt", target, source, amount, null);
        boolean result = original.call(target, source, amount);
        Phase6EnergyNativePathResearch.observe("physical_return", target, source, amount, result);
        return result;
    }
}
