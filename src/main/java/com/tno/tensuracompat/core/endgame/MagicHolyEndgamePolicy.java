package com.tno.tensuracompat.core.endgame;

import com.tno.tensuracompat.core.stage.ScalableFamily;
import com.tno.tensuracompat.core.stage.Stage;

/** Immutable production policy for the Magic/Holy endgame negotiation layer. */
public final class MagicHolyEndgamePolicy {
    private MagicHolyEndgamePolicy() {
    }

    public static Parameters parameters(Stage stage, ScalableFamily family) {
        if (stage == null || !supports(family)) return Parameters.NONE;
        return switch (stage) {
            case S0, S1, S2, S3, S4 -> Parameters.NONE;
            case S5 -> new Parameters(0.50D, 0.50D, 0.50D);
            case S6 -> new Parameters(0.75D, 0.625D, 0.625D);
            case S7 -> new Parameters(1.00D, 0.75D, 0.75D);
        };
    }

    public static boolean supports(ScalableFamily family) {
        return family == ScalableFamily.MAGIC_WEAPON || family == ScalableFamily.HOLY_WEAPON;
    }

    /** Matching native Nullification is authoritative and prevents an endgame scope. */
    public static boolean permitsNativeEvent(ScalableFamily family, boolean matchingNullification) {
        return supports(family) && !matchingNullification;
    }

    public record Parameters(double genericHealthQ, double dementorRecovery, double adaptiveRecovery) {
        public static final Parameters NONE = new Parameters(0.0D, 0.0D, 0.0D);

        public Parameters {
            requireFraction("genericHealthQ", genericHealthQ);
            requireFraction("dementorRecovery", dementorRecovery);
            requireFraction("adaptiveRecovery", adaptiveRecovery);
        }

        public boolean active() {
            return genericHealthQ > 0.0D || dementorRecovery > 0.0D || adaptiveRecovery > 0.0D;
        }

        private static void requireFraction(String name, double value) {
            if (!Double.isFinite(value) || value < 0.0D || value > 1.0D) {
                throw new IllegalArgumentException(name + " must be finite and within [0,1]");
            }
        }
    }
}
