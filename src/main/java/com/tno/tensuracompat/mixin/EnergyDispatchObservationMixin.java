package com.tno.tensuracompat.mixin;

import com.tno.tensuracompat.debug.Phase6EnergyNativePathResearch;
import io.github.manasmods.tensura.enchantment.TensuraEnchantmentHelper;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(value=TensuraEnchantmentHelper.class,remap=false)
public abstract class EnergyDispatchObservationMixin {
    @Inject(method="doAdditionalAfterDamage",at=@At("HEAD"))
    private static void tno$energyDispatch(ServerLevel level,Entity target,LivingEntity owner,DamageSource source,ItemStack weapon,float amount,CallbackInfo ci) {
        Phase6EnergyNativePathResearch.observe("after_damage_dispatch",target,source,amount,null);
    }
}
