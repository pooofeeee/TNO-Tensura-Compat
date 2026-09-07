package com.tno.tensuracompat.mixin;

import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import com.tno.tensuracompat.debug.Phase6ElementalNativePathResearch;
import io.github.manasmods.tensura.entity.projectile.TensuraFlyingProjectile;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.HitResult;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Coerce;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Observes the real native gate and overload, never supplies or changes a hit result. */
@Mixin(value = TensuraFlyingProjectile.class, remap = false)
public abstract class ElementalFlyingObservationMixin {
    @WrapOperation(method = "tickHandler", at = @At(value = "INVOKE", target =
            "Lio/github/manasmods/manascore/skill/api/EntityEvents$ProjectileHitEvent;hit(Lnet/minecraft/world/phys/HitResult;Lnet/minecraft/world/entity/projectile/Projectile;Lio/github/manasmods/manascore/network/api/util/Changeable;Lio/github/manasmods/manascore/network/api/util/Changeable;)V"))
    private void tno$observeGate(@Coerce Object event, HitResult hit, Projectile projectile,
            @Coerce Object deflection, @Coerce Object result, Operation<Void> original) {
        original.call(event, hit, projectile, deflection, result);
        Phase6ElementalNativePathResearch.gate((Projectile) projectile, hit, result, deflection);
    }

    @Inject(method = "onHitEntity(Lnet/minecraft/world/phys/EntityHitResult;Lio/github/manasmods/manascore/skill/api/EntityEvents$ProjectileHitResult;)V", at = @At("HEAD"))
    private void tno$observeCustomCollision(EntityHitResult hit, @Coerce Object result, CallbackInfo ci) {
        Phase6ElementalNativePathResearch.boundary("two_argument_hit", (Entity) (Object) this,
                hit.getEntity(), String.valueOf(result));
    }
}
