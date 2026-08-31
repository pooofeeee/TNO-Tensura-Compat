package com.tno.tensuracompat.mixin;

import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import com.tno.tensuracompat.compat.royalvariations.RoyalBowFirstEngraving;
import io.github.manasmods.tensura.handler.GearHandler;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;

/** Runs the one-time Royal Bow roll immediately after native Gear conversion. */
@Mixin(value = GearHandler.class, remap = false)
public abstract class GearHandlerMixin {
    @WrapOperation(
            method = "lambda$init$2",
            at = @At(
                    value = "INVOKE",
                    target = "Lio/github/manasmods/tensura/handler/GearHandler;initiateGearExistence(Lnet/minecraft/world/level/Level;Lnet/minecraft/world/item/ItemStack;)V"
            )
    )
    private static void tno$processFirstEngravingAfterNativeConversion(
            Level level,
            ItemStack equipped,
            Operation<Void> original,
            LivingEntity wearer,
            ItemStack previous,
            ItemStack current,
            EquipmentSlot slot
    ) {
        original.call(level, equipped);
        RoyalBowFirstEngraving.afterNativeGearIntegration(wearer, equipped);
    }
}
