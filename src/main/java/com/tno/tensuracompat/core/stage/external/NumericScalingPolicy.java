package com.tno.tensuracompat.core.stage.external;

import com.tno.tensuracompat.core.stage.Stage;
import com.tno.tensuracompat.core.stage.StageCurve;

import java.util.Objects;

/**
 * An opt-in scalar policy in the native parameter's units (probabilities use [0, 1]).
 * Bounds describe both the accepted input domain and the permitted output range.
 * This policy never repairs invalid native values or implements a native mechanic.
 */
public record NumericScalingPolicy(Kind kind, double minimum, double maximum) {
    public enum Kind {
        POSITIVE_MAGNITUDE,
        NEGATIVE_DEBUFF,
        DURATION_LENGTHENING,
        DURATION_REDUCTION,
        COOLDOWN_REDUCTION,
        PROBABILITY,
        RADIUS_RANGE,
        RESOURCE_MAGNITUDE,
        IDENTITY
    }

    public NumericScalingPolicy {
        Objects.requireNonNull(kind, "kind");
        if (!Double.isFinite(minimum) || !Double.isFinite(maximum) || minimum > maximum) {
            throw new IllegalArgumentException("Policy bounds must be finite and ordered");
        }

        switch (kind) {
            case NEGATIVE_DEBUFF -> {
                if (maximum > 0.0D) {
                    throw new IllegalArgumentException("Debuff bounds must be nonpositive");
                }
            }
            case RESOURCE_MAGNITUDE, IDENTITY -> {
                // Native resource APIs may encode a drain as a negative delta.
            }
            default -> {
                if (minimum < 0.0D) {
                    throw new IllegalArgumentException("This parameter requires nonnegative bounds");
                }
            }
        }
        if (kind == Kind.PROBABILITY && maximum > 1.0D) {
            throw new IllegalArgumentException("Probability bounds must be within [0, 1]");
        }
        if ((kind == Kind.DURATION_LENGTHENING || kind == Kind.DURATION_REDUCTION
                || kind == Kind.COOLDOWN_REDUCTION) && minimum <= 0.0D) {
            throw new IllegalArgumentException("Active durations and cooldowns require a positive minimum");
        }
    }

    public static NumericScalingPolicy positiveMagnitude(double maximum) {
        return new NumericScalingPolicy(Kind.POSITIVE_MAGNITUDE, 0.0D, maximum);
    }

    public static NumericScalingPolicy negativeDebuff(double minimum) {
        return new NumericScalingPolicy(Kind.NEGATIVE_DEBUFF, minimum, 0.0D);
    }

    public static NumericScalingPolicy durationLengthening(double minimum, double maximum) {
        return new NumericScalingPolicy(Kind.DURATION_LENGTHENING, minimum, maximum);
    }

    public static NumericScalingPolicy durationReduction(double minimum, double maximum) {
        return new NumericScalingPolicy(Kind.DURATION_REDUCTION, minimum, maximum);
    }

    public static NumericScalingPolicy cooldownReduction(double minimum, double maximum) {
        return new NumericScalingPolicy(Kind.COOLDOWN_REDUCTION, minimum, maximum);
    }

    public static NumericScalingPolicy probability(double maximum) {
        return new NumericScalingPolicy(Kind.PROBABILITY, 0.0D, maximum);
    }

    public static NumericScalingPolicy radiusRange(double maximum) {
        return new NumericScalingPolicy(Kind.RADIUS_RANGE, 0.0D, maximum);
    }

    /** Increases magnitude without changing the native credit/debit sign. */
    public static NumericScalingPolicy resourceMagnitude(double minimum, double maximum) {
        return new NumericScalingPolicy(Kind.RESOURCE_MAGNITUDE, minimum, maximum);
    }

    public static NumericScalingPolicy identity(double minimum, double maximum) {
        return new NumericScalingPolicy(Kind.IDENTITY, minimum, maximum);
    }

    /** Requires an original native scalar and an already-proven Stage; not an idempotent operation. */
    public double scaleOriginal(double originalNativeValue, Stage stage) {
        if (kind == Kind.IDENTITY || stage == null || originalNativeValue == 0.0D
                || !Double.isFinite(originalNativeValue)
                || originalNativeValue < minimum || originalNativeValue > maximum) {
            return originalNativeValue;
        }

        double multiplier = StageCurve.multiplier(stage);
        double scaled = reducesDuration()
                ? originalNativeValue / multiplier
                : originalNativeValue * multiplier;
        if (!Double.isFinite(scaled)) {
            return originalNativeValue;
        }
        return Math.max(minimum, Math.min(maximum, scaled));
    }

    /**
     * Rounds toward the original integer: floor increases, ceil reductions (including
     * stronger negative debuffs). An unrepresentable result leaves the native value intact.
     */
    public int scaleOriginalInteger(int originalNativeValue, Stage stage) {
        double scaled = scaleOriginal(originalNativeValue, stage);
        // Correct a one-ulp arithmetic error at an integral boundary without crossing a bound.
        double nearestInteger = Math.rint(scaled);
        if (Math.abs(scaled - nearestInteger) <= Math.ulp(scaled)
                && nearestInteger >= minimum && nearestInteger <= maximum) {
            scaled = nearestInteger;
        }
        double rounded = scaled > originalNativeValue ? Math.floor(scaled) : Math.ceil(scaled);
        if (rounded < Integer.MIN_VALUE || rounded > Integer.MAX_VALUE) {
            return originalNativeValue;
        }
        return (int) rounded;
    }

    private boolean reducesDuration() {
        return kind == Kind.DURATION_REDUCTION || kind == Kind.COOLDOWN_REDUCTION;
    }
}
