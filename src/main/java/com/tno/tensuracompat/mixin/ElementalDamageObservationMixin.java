package com.tno.tensuracompat.mixin;

import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import com.tno.tensuracompat.debug.Phase6ElementalNativePathResearch;
import io.github.manasmods.tensura.entity.TensuraProjectile;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Brackets the existing call once; no new call or altered argument. */
@Mixin(value = TensuraProjectile.class, remap = false)
public abstract class ElementalDamageObservationMixin {
    @Inject(method = "dealDamage(Lnet/minecraft/world/entity/Entity;FF)Z", at = @At("HEAD"))
    private void tno$observeDamage(Entity target, float damage, float cost, CallbackInfoReturnable<Boolean> cir) {
        Phase6ElementalNativePathResearch.boundary("deal_damage", (Entity) (Object) this, target, damage + "/" + cost);
    }
    @WrapOperation(method = "dealDamage(Lnet/minecraft/world/entity/Entity;FF)Z", at = @At(value = "INVOKE",
            target = "Lnet/minecraft/world/entity/Entity;hurt(Lnet/minecraft/world/damagesource/DamageSource;F)Z"))
    private boolean tno$observeHurt(Entity target, DamageSource source, float amount, Operation<Boolean> original) {
        Phase6ElementalNativePathResearch.hurtBoundary((Entity) (Object) this, target, source, amount, null);
        boolean result = original.call(target, source, amount);
        Phase6ElementalNativePathResearch.hurtBoundary((Entity) (Object) this, target, source, amount, result);
        return result;
    }
}
