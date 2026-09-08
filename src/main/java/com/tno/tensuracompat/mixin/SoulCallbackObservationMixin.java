package com.tno.tensuracompat.mixin;

import com.tno.tensuracompat.debug.Phase6SoulNativePathResearch;
import io.github.manasmods.tensura.enchantment.effect.SpiritualDamageEntity;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.item.enchantment.EnchantedItemInUse;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Observes the native callback without cancellation or argument changes. */
@Mixin(value = SpiritualDamageEntity.class, remap = false)
public abstract class SoulCallbackObservationMixin {
    @Inject(method = "postDamage", at = @At("HEAD"))
    private void tno$soulCallback(int level, EnchantedItemInUse item, Entity target, float amount, CallbackInfo ci) {
        Phase6SoulNativePathResearch.observe("soul_callback", target, null, amount, null);
    }
}
