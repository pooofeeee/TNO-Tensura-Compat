package com.tno.tensuracompat.mixin;

import com.tno.tensuracompat.debug.Phase6SeveranceWallContext;
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
}
