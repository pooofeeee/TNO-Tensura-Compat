package com.tno.tensuracompat.core.endgame;

/** Pure formulas used at the verified L2 damage-modifier boundaries. */
public final class MagicHolyEndgameMath {
    private MagicHolyEndgameMath() {
    }

    public static double genericNormalization(
            MagicHolyEndgamePolicy.Parameters parameters,
            double genericHealthMultiplier
    ) {
        if (parameters == null || !parameters.active()) return 1.0D;
        if (!Double.isFinite(genericHealthMultiplier) || genericHealthMultiplier < 1.0D) {
            return 1.0D;
        }
        return 1.0D + parameters.genericHealthQ() * (genericHealthMultiplier - 1.0D);
    }

    public static double negotiateDementor(
            boolean hasDementor,
            double preDementor,
            double nativePostDementor,
            double recovery
    ) {
        if (!hasDementor || !Double.isFinite(preDementor) || !Double.isFinite(nativePostDementor)
                || !validFraction(recovery) || nativePostDementor > preDementor) {
            return nativePostDementor;
        }
        return nativePostDementor + recovery * (preDementor - nativePostDementor);
    }

    public static double negotiateAdaptive(boolean hasAdaptive, double nativeFactor, double recovery) {
        if (!hasAdaptive || !Double.isFinite(nativeFactor) || nativeFactor < 0.0D || nativeFactor > 1.0D
                || !validFraction(recovery)) {
            return nativeFactor;
        }
        return nativeFactor + recovery * (1.0D - nativeFactor);
    }

    private static boolean validFraction(double value) {
        return Double.isFinite(value) && value >= 0.0D && value <= 1.0D;
    }
}
