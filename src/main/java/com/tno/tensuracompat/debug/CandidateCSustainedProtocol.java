package com.tno.tensuracompat.debug;

/** Pure observation arithmetic. No Minecraft object or combat mutation is available here. */
public final class CandidateCSustainedProtocol {
    public static final double STATE_TOLERANCE = 0.01D;
    // At 10,000 HP one float ULP is 0.0009765625 HP. Allow just over one ULP.
    public static final double FORMULA_TOLERANCE = 0.001D;
    public static final int MIN_TICKS = 2400;
    public static final int MAX_TICKS = 3600;

    private CandidateCSustainedProtocol() { }

    public static String state(double hp, double ceiling, double request) {
        if (hp >= ceiling - STATE_TOLERANCE) return "C";
        return hp + request <= ceiling + STATE_TOLERANCE ? "A" : "B";
    }

    public static double expected(double hp, double ceiling, double request) {
        return Math.min(request, Math.max(0.0D, ceiling - hp));
    }

    public static void requireTransaction(double hp, double shp, double wound, double maxHp,
            double request, double hpAfter, double shpAfter, double woundAfter) {
        double actual = Math.max(0.0D, hpAfter - hp);
        if (Math.abs(actual - expected(hp, maxHp - wound, request)) > FORMULA_TOLERANCE
                || Math.abs(shpAfter - shp) > FORMULA_TOLERANCE
                || Math.abs(woundAfter - wound) > FORMULA_TOLERANCE
                || hpAfter > maxHp - woundAfter + FORMULA_TOLERANCE) {
            throw new IllegalStateException("Candidate C native Regenerate transaction violated the counter contract");
        }
    }

    public static double slope(double start, double end, int ticks) {
        if (ticks <= 0) throw new IllegalArgumentException("positive interval required");
        return (start - end) * 20.0D / ticks;
    }

    public static boolean stable(double previous, double latest) {
        // A convergence tolerance, never a combat-viability cutoff: 5% or 0.01 HP/s.
        return Math.abs(previous - latest)
                <= Math.max(0.01D, 0.05D * Math.max(Math.abs(previous), Math.abs(latest)));
    }
}
