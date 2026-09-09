package com.tno.tensuracompat.mixin;

import com.tno.tensuracompat.debug.Phase6EnergyNativePathResearch;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemCooldowns;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(ItemCooldowns.class)
public abstract class EnergyCooldownObservationMixin {
    @Inject(method="addCooldown",at=@At("HEAD"))
    private void tno$energyCooldownBefore(Item item,int ticks,CallbackInfo ci) { Phase6EnergyNativePathResearch.cooldown((ItemCooldowns)(Object)this,"cooldown_add_before",item,ticks); }
    @Inject(method="addCooldown",at=@At("RETURN"))
    private void tno$energyCooldownAfter(Item item,int ticks,CallbackInfo ci) { Phase6EnergyNativePathResearch.cooldown((ItemCooldowns)(Object)this,"cooldown_add_after",item,ticks); }
    @Inject(method="tick",at=@At("HEAD"))
    private void tno$energyClockBefore(CallbackInfo ci) { Phase6EnergyNativePathResearch.cooldown((ItemCooldowns)(Object)this,"cooldown_tick_before",null,null); }
    @Inject(method="tick",at=@At("RETURN"))
    private void tno$energyClockAfter(CallbackInfo ci) { Phase6EnergyNativePathResearch.cooldown((ItemCooldowns)(Object)this,"cooldown_tick_after",null,null); }
}
