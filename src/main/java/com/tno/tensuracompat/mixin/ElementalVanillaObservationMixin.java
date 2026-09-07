package com.tno.tensuracompat.mixin;

import com.tno.tensuracompat.debug.Phase6ElementalNativePathResearch;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.HitResult;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Counts the inherited vanilla route used by the historical fixture. */
@Mixin(Projectile.class)
public abstract class ElementalVanillaObservationMixin {
    @Inject(method = "onHit", at = @At("HEAD"))
    private void tno$observeOnHit(HitResult hit, CallbackInfo ci) {
        if (hit instanceof EntityHitResult entityHit)
            Phase6ElementalNativePathResearch.boundary("vanilla_on_hit", (Entity) (Object) this,
                    entityHit.getEntity(), "HitResult");
    }
    @Inject(method = "onHitEntity", at = @At("HEAD"))
    private void tno$observeSingleCollision(EntityHitResult hit, CallbackInfo ci) {
        Phase6ElementalNativePathResearch.boundary("one_argument_hit", (Entity) (Object) this,
                hit.getEntity(), "EntityHitResult");
    }
}
