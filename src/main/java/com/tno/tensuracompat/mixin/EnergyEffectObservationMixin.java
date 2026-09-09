package com.tno.tensuracompat.mixin;

import com.tno.tensuracompat.debug.Phase6EnergyNativePathResearch;
import io.github.manasmods.tensura.enchantment.effect.EnergyStealEntity;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.item.enchantment.EnchantedItemInUse;
import net.minecraft.world.phys.Vec3;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Noncancellable observations, dormant outside an explicit development research session. */
@Mixin(value=EnergyStealEntity.class,remap=false)
public abstract class EnergyEffectObservationMixin {
    @Inject(method="apply(Lnet/minecraft/server/level/ServerLevel;ILnet/minecraft/world/item/enchantment/EnchantedItemInUse;Lnet/minecraft/world/entity/Entity;Lnet/minecraft/world/phys/Vec3;F)V",at=@At("HEAD"))
    private void tno$energyCallback(ServerLevel world,int level,EnchantedItemInUse item,Entity target,Vec3 pos,float damage,CallbackInfo ci) {
        Phase6EnergyNativePathResearch.effect("energy_callback",(EnergyStealEntity)(Object)this,level,item,target);
    }
    @Inject(method="applyEnergySteal",at=@At("HEAD"))
    private void tno$energyApply(int level,EnchantedItemInUse item,Entity target,CallbackInfo ci) {
        Phase6EnergyNativePathResearch.effect("energy_apply",(EnergyStealEntity)(Object)this,level,item,target);
    }
    @Inject(method="applyEnergySteal",at=@At("RETURN"))
    private void tno$energyApplyReturn(int level,EnchantedItemInUse item,Entity target,CallbackInfo ci) {
        Phase6EnergyNativePathResearch.effect("energy_apply_return",(EnergyStealEntity)(Object)this,level,item,target);
    }
}
