package com.tno.tensuracompat.core.stage;

import io.github.manasmods.tensura.registry.item.misc.TensuraDataComponents;
import net.minecraft.world.item.ItemStack;

import java.util.Objects;

/** Reads the live Tensura gear component without maintaining TNO-owned progression state. */
public final class NativeGearEpSource {
    private NativeGearEpSource() {
    }

    public static double currentEp(ItemStack gear) {
        Objects.requireNonNull(gear, "gear");
        return gear.getOrDefault(TensuraDataComponents.EP.get(), 0.0D);
    }

    public static Stage resolve(ItemStack gear, GearStageClass stageClass) {
        return StageResolver.resolve(currentEp(gear), stageClass);
    }
}
