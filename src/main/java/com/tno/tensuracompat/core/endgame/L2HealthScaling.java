package com.tno.tensuracompat.core.endgame;

/** Pure representation of L2 Hostility's native generic-health scaling formula. */
public final class L2HealthScaling {
    private L2HealthScaling() {
    }

    public static double nominalMultiplier(
            int level,
            double healthFactor,
            double entityHealthScale,
            boolean exponentialHealth
    ) {
        if (level < 0 || !Double.isFinite(healthFactor) || healthFactor < 0.0D
                || !Double.isFinite(entityHealthScale) || entityHealthScale < 0.0D) {
            throw new IllegalArgumentException("invalid L2 generic-health inputs");
        }
        double scaledLevel = exponentialHealth
                ? Math.pow(1.0D + healthFactor, level) - 1.0D
                : level * healthFactor;
        double multiplier = 1.0D + scaledLevel * entityHealthScale;
        if (!Double.isFinite(multiplier) || multiplier < 1.0D) {
            throw new IllegalArgumentException("invalid L2 generic-health multiplier");
        }
        return multiplier;
    }
}
