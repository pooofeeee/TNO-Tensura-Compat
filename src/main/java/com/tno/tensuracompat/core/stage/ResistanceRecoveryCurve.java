package com.tno.tensuracompat.core.stage;

import java.util.Objects;

/** Locked S5-S7 recovery of loss caused by one matching Tensura Resistance layer. */
public final class ResistanceRecoveryCurve {
    private ResistanceRecoveryCurve() {
    }

    public static double penetration(Stage stage) {
        return switch (Objects.requireNonNull(stage, "stage")) {
            case S0, S1, S2, S3, S4 -> 0.0D;
            case S5 -> 0.25D;
            case S6 -> 0.50D;
            case S7 -> 1.0D;
        };
    }

    public static double recover(double preMatchingResistance, double postResistance, Stage stage) {
        validateAmount(preMatchingResistance, "preMatchingResistance");
        validateAmount(postResistance, "postResistance");
        if (postResistance > preMatchingResistance) {
            throw new IllegalArgumentException("postResistance cannot exceed preMatchingResistance");
        }
        return postResistance
                + penetration(stage) * (preMatchingResistance - postResistance);
    }

    /** Mirrors Tensura's mastered Resistance HP gate and multiplier before recovery. */
    public static double nativePostResistance(
            double preMatchingResistance,
            double targetHealth,
            double hpBypassMultiplier,
            double damageMultiplier
    ) {
        validateAmount(preMatchingResistance, "preMatchingResistance");
        validateAmount(targetHealth, "targetHealth");
        if (!Double.isFinite(hpBypassMultiplier) || !Double.isFinite(damageMultiplier)) {
            throw new IllegalArgumentException("Resistance configuration must be finite");
        }
        if (hpBypassMultiplier < 0.0D
                || preMatchingResistance <= targetHealth * hpBypassMultiplier
                || damageMultiplier <= 0.0D) {
            return 0.0D;
        }
        return preMatchingResistance * damageMultiplier;
    }

    private static void validateAmount(double amount, String name) {
        if (!Double.isFinite(amount) || amount < 0.0D) {
            throw new IllegalArgumentException(name + " must be finite and non-negative");
        }
    }
}
