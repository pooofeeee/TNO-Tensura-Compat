package com.tno.tensuracompat.mixin;

import com.tno.tensuracompat.debug.Phase6SoulNativePathResearch;
import io.github.manasmods.tensura.storage.ep.ExistenceStorage;
import io.github.manasmods.tensura.storage.ep.IExistence;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Read-only ledger for native Soul damage and later native SHP recovery. */
@Mixin(value = ExistenceStorage.class, remap = false)
public abstract class SoulStorageObservationMixin {
    @Inject(method = "setMagicule", at = @At("HEAD"))
    private void tno$soulMagiculeBefore(double value, CallbackInfo ci) { Phase6SoulNativePathResearch.energy((IExistence)this,"target_magicule",value,false); }
    @Inject(method = "setMagicule", at = @At("RETURN"))
    private void tno$soulMagiculeAfter(double value, CallbackInfo ci) { Phase6SoulNativePathResearch.energy((IExistence)this,"target_magicule",value,true); }
    @Inject(method = "setAura", at = @At("HEAD"))
    private void tno$soulAuraBefore(double value, CallbackInfo ci) { Phase6SoulNativePathResearch.energy((IExistence)this,"target_aura",value,false); }
    @Inject(method = "setAura", at = @At("RETURN"))
    private void tno$soulAuraAfter(double value, CallbackInfo ci) { Phase6SoulNativePathResearch.energy((IExistence)this,"target_aura",value,true); }
    @Inject(method = "setSpiritualHealth", at = @At("HEAD"))
    private void tno$soulStorageBefore(double value, CallbackInfo ci) {
        Phase6SoulNativePathResearch.storage((IExistence)this, value, false);
    }
    @Inject(method = "setSpiritualHealth", at = @At("RETURN"))
    private void tno$soulStorageAfter(double value, CallbackInfo ci) {
        Phase6SoulNativePathResearch.storage((IExistence)this, value, true);
    }
}
