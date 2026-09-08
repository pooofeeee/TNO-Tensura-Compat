package com.tno.tensuracompat.mixin;

import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import com.tno.tensuracompat.debug.Phase6SoulNativePathResearch;
import io.github.manasmods.tensura.damage.TensuraDamageHelper;
import io.github.manasmods.tensura.storage.ep.IExistence;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Mixin(value = TensuraDamageHelper.class, remap = false)
public abstract class SoulHelperObservationMixin {
    private static final String FOUR = "directSpiritualHurt(Lnet/minecraft/world/entity/LivingEntity;Lnet/minecraft/world/entity/Entity;Lnet/minecraft/world/damagesource/DamageSource;F)Z";
    private static final String FIVE = "directSpiritualHurt(Lnet/minecraft/world/entity/LivingEntity;Lnet/minecraft/world/entity/Entity;Lnet/minecraft/world/damagesource/DamageSource;FF)Z";
    private static final String EVENT = "Lio/github/manasmods/tensura/event/TensuraEntityEvents$SpiritualHurtEvent;hurt(Lnet/minecraft/world/entity/LivingEntity;Lnet/minecraft/world/entity/Entity;FLio/github/manasmods/manascore/network/api/util/Changeable;Lio/github/manasmods/manascore/network/api/util/Changeable;Lio/github/manasmods/manascore/network/api/util/Changeable;)Ldev/architectury/event/EventResult;";
    @Inject(method = FOUR, at = @At("HEAD"))
    private static void tno$soulSource(LivingEntity target, Entity attacker, DamageSource source, float amount, CallbackInfoReturnable<Boolean> cir) {
        Phase6SoulNativePathResearch.observe("soul_source", target, source, amount, null);
    }
    @Inject(method = FOUR, at = @At("RETURN"))
    private static void tno$soulReturn(LivingEntity target, Entity attacker, DamageSource source, float amount, CallbackInfoReturnable<Boolean> cir) {
        Phase6SoulNativePathResearch.observe("soul_return", target, source, amount, cir.getReturnValue());
    }
    @Inject(method = FIVE, at = @At(value = "INVOKE", target = EVENT))
    private static void tno$soulEvent(LivingEntity target, Entity attacker, DamageSource source, float amount, float resistance, CallbackInfoReturnable<Boolean> cir) {
        Phase6SoulNativePathResearch.observe("spiritual_event", target, source, amount, null);
    }
    @WrapOperation(method = FIVE, at = @At(value = "INVOKE",
            target = "Lio/github/manasmods/tensura/storage/ep/IExistence;setSpiritualHealth(D)V"))
    private static void tno$soulResource(IExistence storage, double value, Operation<Void> original) {
        Phase6SoulNativePathResearch.resource(storage, value, false);
        original.call(storage, value);
        Phase6SoulNativePathResearch.resource(storage, value, true);
    }
}
