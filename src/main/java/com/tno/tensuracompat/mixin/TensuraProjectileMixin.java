package com.tno.tensuracompat.mixin;

import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import com.tno.tensuracompat.core.stage.ElementalStageProjectileContext;
import com.tno.tensuracompat.core.stage.MatchingResistanceRecovery;
import com.tno.tensuracompat.core.stage.ScalableFamily;
import io.github.manasmods.tensura.entity.TensuraProjectile;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;

/** Carries Slotting's attack-time Stage to Tensura's native projectile damage boundary. */
@Mixin(value = TensuraProjectile.class, remap = false)
public abstract class TensuraProjectileMixin {
    @WrapOperation(
            method = "dealDamage(Lnet/minecraft/world/entity/Entity;FF)Z",
            at = @At(
                    value = "INVOKE",
                    target = "Lnet/minecraft/world/entity/Entity;hurt(Lnet/minecraft/world/damagesource/DamageSource;F)Z"
            )
    )
    private boolean tno$recoverMatchingElementalResistance(
            Entity damaged,
            DamageSource source,
            float preMatchingResistance,
            Operation<Boolean> original
    ) {
        if (!(damaged instanceof LivingEntity livingTarget)) {
            return original.call(damaged, source, preMatchingResistance);
        }

        var stage = ElementalStageProjectileContext.stage((Entity) (Object) this);
        if (stage.isEmpty()) {
            return original.call(damaged, source, preMatchingResistance);
        }

        float recovered = MatchingResistanceRecovery.apply(
                stage.get(),
                ScalableFamily.ELEMENTAL_SLOTTING,
                livingTarget,
                source,
                preMatchingResistance
        );
        return original.call(damaged, source, recovered);
    }
}
