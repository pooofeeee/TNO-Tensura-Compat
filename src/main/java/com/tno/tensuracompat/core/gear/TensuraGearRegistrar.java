package com.tno.tensuracompat.core.gear;

import io.github.manasmods.tensura.data.existence.gear.GearExistenceData;
import io.github.manasmods.tensura.registry.data.TensuraCustomData;
import net.minecraft.data.worldgen.BootstrapContext;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;

/** Minimal shared bridge from external item IDs into Tensura's gear registry. */
public final class TensuraGearRegistrar {
    private TensuraGearRegistrar() {
    }

    public static ResourceKey<GearExistenceData> key(ResourceLocation gearId) {
        return ResourceKey.create(TensuraCustomData.GEAR_EXISTENCE, gearId);
    }

    public static void register(BootstrapContext<GearExistenceData> context, GearExistenceData data) {
        context.register(key(data.gear()), data);
    }
}
