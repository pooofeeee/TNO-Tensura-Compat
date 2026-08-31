package com.tno.tensuracompat.core.stage;

import net.minecraft.world.item.ItemStack;

import java.util.Optional;

/** Applies Curve C only when an explicitly classified gear item owns the native effect. */
public final class ProductionStageScaling {
    private ProductionStageScaling() {
    }

    public static float scaleEligible(ItemStack gear, ScalableFamily family, float nativeEligibleAmount) {
        Optional<GearStageClass> stageClass = GearStageClasses.classification(gear);
        if (stageClass.isEmpty()) {
            return nativeEligibleAmount;
        }

        Stage stage = NativeGearEpSource.resolve(gear, stageClass.get());
        return (float) StageCurve.scaleForActiveFamily(
                nativeEligibleAmount,
                stage,
                Optional.of(family),
                family
        );
    }
}
