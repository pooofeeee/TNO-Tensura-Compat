package com.tno.tensuracompat.mixin;

import com.tno.tensuracompat.debug.Phase5FSuiteBBenchmark;
import net.minecraft.world.entity.LivingEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Read-only HEAD/RETURN observation; never cancels or changes a heal argument. */
@Mixin(LivingEntity.class)
public abstract class SustainedHealObservationMixin {
    @Inject(method = "heal", at = @At("HEAD"))
    private void tno$beforeSustainedHeal(float amount, CallbackInfo ci) {
        Phase5FSuiteBBenchmark.sustainedHealBoundary((LivingEntity) (Object) this, amount, true);
    }
    @Inject(method = "heal", at = @At("RETURN"))
    private void tno$afterSustainedHeal(float amount, CallbackInfo ci) {
        Phase5FSuiteBBenchmark.sustainedHealBoundary((LivingEntity) (Object) this, amount, false);
    }
}
