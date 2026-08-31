package com.tno.tensuracompat.core.stage;

import java.util.Objects;

/** Derives a Stage from the current authoritative native Tensura gear EP. */
public final class StageResolver {
    private StageResolver() {
    }

    public static Stage resolve(double currentEp, GearStageClass stageClass) {
        Objects.requireNonNull(stageClass, "stageClass");
        if (Double.isNaN(currentEp)) {
            throw new IllegalArgumentException("Native gear EP cannot be NaN");
        }

        Stage resolved = Stage.S0;
        for (GearStageClass.Threshold threshold : stageClass.thresholds()) {
            if (currentEp < threshold.minimumEp()) {
                break;
            }
            resolved = threshold.stage();
        }
        return resolved;
    }

}
