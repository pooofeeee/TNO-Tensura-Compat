package com.tno.tensuracompat.mixin;

import com.tno.tensuracompat.debug.Phase6SeveranceWallContext;
import com.tno.tensuracompat.debug.Phase6AdaptiveWoundContext;
import com.llamalad7.mixinextras.injector.ModifyExpressionValue;
import io.github.manasmods.tensura.enchantment.effect.SeveranceDamageEntity;
import net.minecraft.world.entity.Entity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Development-only observation hook; the native Severance method is not modified. */
@Mixin(value = SeveranceDamageEntity.class, remap = false)
public abstract class SeveranceDamageEntityMixin {
    @Inject(method = "postDamage", at = @At("HEAD"))
    private void tno$observeNativeWoundAttempt(int enchantmentLevel, Entity target,
            float callbackDamage, CallbackInfo callback) {
        Phase6SeveranceWallContext.captureWoundAttempt(target, callbackDamage);
    }

    @ModifyExpressionValue(
            method = "postDamage",
            at = @At(
                    value = "INVOKE",
                    target = "Ljava/lang/Math;min(FF)F",
                    ordinal = 1
            )
    )
    private float tno$negotiateEligibleWoundAtNativeClamp(
            float nativeOffer,
            int enchantmentLevel,
            Entity target,
            float callbackDamage
    ) {
        SeveranceDamageEntity self = (SeveranceDamageEntity) (Object) this;
        float nativeCandidate = Math.min(
                self.amount().calculate(enchantmentLevel), self.severanceCap()) * callbackDamage;
        return Phase6AdaptiveWoundContext.negotiate(
                target, callbackDamage, nativeCandidate, nativeOffer);
    }

    @Inject(method = "postDamage", at = @At("RETURN"))
    private void tno$finishAdaptiveWoundObservation(int enchantmentLevel, Entity target,
            float callbackDamage, CallbackInfo callback) {
        Phase6AdaptiveWoundContext.finishCallback(target);
    }
}
