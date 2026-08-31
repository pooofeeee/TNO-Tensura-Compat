package com.tno.tensuracompat.core.stage;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.item.ItemStack;

import java.util.Optional;

/** Attack-time Stage snapshot for a native Slotting projectile that may hit later. */
public final class ElementalStageProjectileContext {
    private static final String STAGE_KEY = "tno_tensura_compat:elemental_stage";

    private ElementalStageProjectileContext() {
    }

    public static void capture(Entity projectile, ItemStack gear) {
        ProductionStageScaling.stage(gear).ifPresent(stage ->
                projectile.getPersistentData().putInt(STAGE_KEY, stage.index()));
    }

    public static Optional<Stage> stage(Entity projectile) {
        CompoundTag data = projectile.getPersistentData();
        if (!data.contains(STAGE_KEY)) {
            return Optional.empty();
        }
        int index = data.getInt(STAGE_KEY);
        Stage[] stages = Stage.values();
        return index >= 0 && index < stages.length
                ? Optional.of(stages[index])
                : Optional.empty();
    }
}
