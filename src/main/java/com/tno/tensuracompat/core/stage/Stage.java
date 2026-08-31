package com.tno.tensuracompat.core.stage;

/** A TNO integration stage. These names are independent of every mod's rarity names. */
public enum Stage {
    S0(0, 0.05D),
    S1(1, 0.10D),
    S2(2, 0.15D),
    S3(3, 0.20D),
    S4(4, 0.25D),
    S5(5, 0.30D),
    S6(6, 0.35D),
    S7(7, 0.40D);

    private final int index;
    private final double curveBonus;

    Stage(int index, double curveBonus) {
        this.index = index;
        this.curveBonus = curveBonus;
    }

    public int index() {
        return index;
    }

    public double curveBonus() {
        return curveBonus;
    }

    public double curveMultiplier() {
        return 1.0D + curveBonus;
    }
}
