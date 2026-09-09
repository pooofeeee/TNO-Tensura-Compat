package com.tno.tensuracompat.mixin;
import com.tno.tensuracompat.debug.Phase6EnergyNativePathResearch;
import net.minecraft.world.entity.LivingEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Observes native damage/healing, including legal L2 Regenerate. */
@Mixin(LivingEntity.class)
public abstract class EnergyHealthObservationMixin {
    @Inject(method="setHealth", at=@At("HEAD"))
    private void tno$energyHealthBefore(float value, CallbackInfo ci) { Phase6EnergyNativePathResearch.health((LivingEntity)(Object)this,value,false); }
    @Inject(method="setHealth", at=@At("RETURN"))
    private void tno$energyHealthAfter(float value, CallbackInfo ci) { Phase6EnergyNativePathResearch.health((LivingEntity)(Object)this,value,true); }
}
