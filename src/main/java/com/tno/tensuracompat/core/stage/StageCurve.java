package com.tno.tensuracompat.core.stage;

import java.util.Objects;
import java.util.Optional;

/** Curve C operations limited to one active eligible native family. */
public final class StageCurve {
    private StageCurve() {
    }

    public static double multiplier(Stage stage) {
        return Objects.requireNonNull(stage, "stage").curveMultiplier();
    }

    public static double scaleEligible(double nativeEligibleAmount, Stage stage) {
        return nativeEligibleAmount * multiplier(stage);
    }

    public static double scaleForActiveFamily(
            double nativeEligibleAmount,
            Stage stage,
            Optional<ScalableFamily> activeFamily,
            ScalableFamily observedFamily
    ) {
        Objects.requireNonNull(activeFamily, "activeFamily");
        Objects.requireNonNull(observedFamily, "observedFamily");
        if (activeFamily.isEmpty() || activeFamily.get() != observedFamily) {
            return nativeEligibleAmount;
        }
        return scaleEligible(nativeEligibleAmount, stage);
    }

    public static double combatGain(
            double nativeEligibleAmount,
            Stage stage,
            Optional<ScalableFamily> activeFamily,
            ScalableFamily observedFamily
    ) {
        return scaleForActiveFamily(nativeEligibleAmount, stage, activeFamily, observedFamily)
                - nativeEligibleAmount;
    }
}
