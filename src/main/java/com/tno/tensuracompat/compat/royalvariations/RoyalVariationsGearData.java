package com.tno.tensuracompat.compat.royalvariations;

import com.tno.tensuracompat.core.gear.TensuraGearRegistrar;
import io.github.manasmods.tensura.data.existence.gear.GearExistenceData;
import net.minecraft.data.worldgen.BootstrapContext;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;

public final class RoyalVariationsGearData {
    public static final String MOD_ID = "royalvariations";
    public static final ResourceLocation ROYAL_BOW_ID =
            ResourceLocation.fromNamespaceAndPath(MOD_ID, "royal_bow");
    public static final ResourceKey<GearExistenceData> ROYAL_BOW_GEAR_KEY =
            TensuraGearRegistrar.key(ROYAL_BOW_ID);

    /** Temporary technical-test minimum/initial EP; not a final balance value. */
    public static final int ROYAL_BOW_INITIAL_EP = 1_000;

    /** Temporary technical-test native Tensura EP gain coefficient; not final balance. */
    public static final double ROYAL_BOW_GROWTH_RATE = 0.01D;

    private RoyalVariationsGearData() {
    }

    public static void bootstrap(BootstrapContext<GearExistenceData> context) {
        GearExistenceData royalBow = GearExistenceData.getDefault(
                ROYAL_BOW_ID,
                ROYAL_BOW_INITIAL_EP,
                ROYAL_BOW_GROWTH_RATE
        );
        TensuraGearRegistrar.register(context, royalBow);
    }
}
