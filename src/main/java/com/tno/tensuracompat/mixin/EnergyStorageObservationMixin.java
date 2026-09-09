package com.tno.tensuracompat.mixin;

import com.tno.tensuracompat.debug.Phase6EnergyNativePathResearch;
import io.github.manasmods.tensura.storage.ep.ExistenceStorage;
import io.github.manasmods.tensura.storage.ep.IExistence;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Read-only ledger for all native resource writes. */
@Mixin(value = ExistenceStorage.class, remap = false)
public abstract class EnergyStorageObservationMixin {
    @Inject(method = "setMagicule", at = @At("HEAD"))
    private void tno$energyMagiculeBefore(double value, CallbackInfo ci) { Phase6EnergyNativePathResearch.energy((IExistence)this,"target_magicule",value,false); }
    @Inject(method = "setMagicule", at = @At("RETURN"))
    private void tno$energyMagiculeAfter(double value, CallbackInfo ci) { Phase6EnergyNativePathResearch.energy((IExistence)this,"target_magicule",value,true); }
    @Inject(method = "setAura", at = @At("HEAD"))
    private void tno$energyAuraBefore(double value, CallbackInfo ci) { Phase6EnergyNativePathResearch.energy((IExistence)this,"target_aura",value,false); }
    @Inject(method = "setAura", at = @At("RETURN"))
    private void tno$energyAuraAfter(double value, CallbackInfo ci) { Phase6EnergyNativePathResearch.energy((IExistence)this,"target_aura",value,true); }
    @Inject(method = "setSpiritualHealth", at = @At("HEAD"))
    private void tno$energyStorageBefore(double value, CallbackInfo ci) {
        Phase6EnergyNativePathResearch.energy((IExistence)this, "shp", value, false);
    }
    @Inject(method = "setSpiritualHealth", at = @At("RETURN"))
    private void tno$energyStorageAfter(double value, CallbackInfo ci) {
        Phase6EnergyNativePathResearch.energy((IExistence)this, "shp", value, true);
    }
}
