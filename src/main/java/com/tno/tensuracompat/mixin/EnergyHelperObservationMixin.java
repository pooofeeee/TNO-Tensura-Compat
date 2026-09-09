package com.tno.tensuracompat.mixin;

import com.tno.tensuracompat.debug.Phase6EnergyNativePathResearch;
import io.github.manasmods.tensura.util.EnergyHelper;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Mixin(value=EnergyHelper.class,remap=false)
public abstract class EnergyHelperObservationMixin {
    @Inject(method="drainEnergy",at=@At("HEAD"))
    private static void tno$energyDrain(LivingEntity target,Entity owner,double amount,boolean percentage,EnergyHelper.DrainType drain,EnergyHelper.GainType gain,CallbackInfoReturnable<Boolean> ci) {
        Phase6EnergyNativePathResearch.drain("drain_enter",target,owner,amount,percentage,drain,gain,null);
    }
    @Inject(method="drainEnergy",at=@At("RETURN"))
    private static void tno$energyDrainReturn(LivingEntity target,Entity owner,double amount,boolean percentage,EnergyHelper.DrainType drain,EnergyHelper.GainType gain,CallbackInfoReturnable<Boolean> ci) {
        Phase6EnergyNativePathResearch.drain("drain_return",target,owner,amount,percentage,drain,gain,ci.getReturnValue());
    }
}
