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
    @Inject(method = "setSpiritualHealth", at = @At("HEAD"))
    private void tno$soulStorageBefore(double value, CallbackInfo ci) {
        Phase6SoulNativePathResearch.storage((IExistence)this, value, false);
    }
    @Inject(method = "setSpiritualHealth", at = @At("RETURN"))
    private void tno$soulStorageAfter(double value, CallbackInfo ci) {
        Phase6SoulNativePathResearch.storage((IExistence)this, value, true);
    }
}
