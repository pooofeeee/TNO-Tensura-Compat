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
}
