package com.tno.tensuracompat.core.stage;

import com.tno.tensuracompat.compat.royalvariations.RoyalVariationsGearData;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;

import java.util.Map;
import java.util.Objects;
import java.util.Optional;

/** Explicit production classifications for external compatible gear. */
public final class GearStageClasses {
    private static final Map<ResourceLocation, GearStageClass> CLASS_BY_ITEM = Map.of(
            RoyalVariationsGearData.ROYAL_BOW_ID, GearStageClass.RARE
    );

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
