package com.tno.tensuracompat.core.stage;

import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;

import java.util.Map;
import java.util.Objects;
import java.util.Optional;

/** Explicit production classifications for external compatible gear. */
public final class GearStageClasses {
    /*
     * Deliberately empty at Checkpoint 6B. Accepted evidence does not yet state
     * whether Royal Bow is TNO Common or Rare; benchmark S0-S7 coverage is not
     * itself authorization to make that production classification.
     */
    private static final Map<ResourceLocation, GearStageClass> CLASS_BY_ITEM = Map.of();

    private GearStageClasses() {
    }

    public static Optional<GearStageClass> classification(ItemStack gear) {
        Objects.requireNonNull(gear, "gear");
        return classification(BuiltInRegistries.ITEM.getKey(gear.getItem()));
    }

    public static Optional<GearStageClass> classification(ResourceLocation gearId) {
        Objects.requireNonNull(gearId, "gearId");
        return Optional.ofNullable(CLASS_BY_ITEM.get(gearId));
    }
}
