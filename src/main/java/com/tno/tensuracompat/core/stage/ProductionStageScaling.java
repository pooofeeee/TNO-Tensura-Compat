package com.tno.tensuracompat.core.stage;

import net.minecraft.world.item.ItemStack;

import java.util.Optional;

/** Applies Curve C only when an explicitly classified gear item owns the native effect. */
public final class ProductionStageScaling {
    private ProductionStageScaling() {
    }

    public static float scaleEligible(ItemStack gear, ScalableFamily family, float nativeEligibleAmount) {
        return (float) scaleEligible(gear, family, (double) nativeEligibleAmount);
    }

    public static double scaleEligible(ItemStack gear, ScalableFamily family, double nativeEligibleAmount) {
        Optional<Stage> stage = stage(gear);
        if (stage.isEmpty()) {
            return nativeEligibleAmount;
        }

        return StageCurve.scaleForActiveFamily(
                nativeEligibleAmount,
                stage.get(),
                Optional.of(family),
                family
        );
    }

    /** Resolves attack-time Stage directly from authoritative native Gear EP. */
    public static Optional<Stage> stage(ItemStack gear) {
        return GearStageClasses.classification(gear)
                .map(stageClass -> NativeGearEpSource.resolve(gear, stageClass));
    }
}
