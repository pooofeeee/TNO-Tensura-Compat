package com.tno.tensuracompat.debug;

import com.tno.tensuracompat.core.stage.SeveranceStageScaling;
import net.neoforged.fml.loading.FMLEnvironment;

/**
 * Development-only R4 parameter scope. It multiplies only the already-isolated
 * staged Severance contribution before that contribution rejoins the ordinary
 * arrow base in the existing single physical source.
 */
public final class Phase6SeverancePrototypeContext {
    private static final ThreadLocal<Double> ELIGIBLE_MULTIPLIER = ThreadLocal.withInitial(() -> 1.0D);

    private Phase6SeverancePrototypeContext() {
    }

    public static boolean enabled() {
        return !FMLEnvironment.production
                && Boolean.getBoolean("tno.phase6.calibration")
                && System.getProperty("tno.phase6.calibrationMode", "")
                .equals("severance_prototype");
    }

    public static ParameterScope useEligibleMultiplier(double multiplier) {
        if (!enabled()) return ParameterScope.INACTIVE;
        requireMultiplier(multiplier);
        double previous = ELIGIBLE_MULTIPLIER.get();
        ELIGIBLE_MULTIPLIER.set(multiplier);
        return new ParameterScope(Thread.currentThread(), previous, true);
    }

    public static SeveranceStageScaling.Adjustment apply(
            SeveranceStageScaling.Adjustment production
    ) {
        if (!enabled()) return production;
        double multiplier = ELIGIBLE_MULTIPLIER.get();
        requireMultiplier(multiplier);
        double negotiatedEligible = production.stagedEligibleContribution() * multiplier;
        return new SeveranceStageScaling.Adjustment(
                production.nativeModifiedBase(),
                production.nativeModifiedBase() + negotiatedEligible
                        - production.nativeEligibleContribution(),
                production.nativeEligibleContribution(),
                negotiatedEligible
        );
    }

    private static void requireMultiplier(double multiplier) {
        if (!Double.isFinite(multiplier) || multiplier < 1.0D || multiplier > 64.0D) {
            throw new IllegalArgumentException("Severance prototype multiplier must be within [1,64]");
        }
    }

    public static final class ParameterScope implements AutoCloseable {
        private static final ParameterScope INACTIVE = new ParameterScope(null, 1.0D, false);
        private final Thread owner;
        private final double previous;
        private final boolean active;
        private boolean closed;

        private ParameterScope(Thread owner, double previous, boolean active) {
            this.owner = owner;
            this.previous = previous;
            this.active = active;
        }

        @Override
        public void close() {
            if (closed || !active) return;
            if (Thread.currentThread() != owner) {
                throw new IllegalStateException("Severance prototype scope closed on another thread");
            }
            if (previous == 1.0D) ELIGIBLE_MULTIPLIER.remove();
            else ELIGIBLE_MULTIPLIER.set(previous);
            closed = true;
        }
    }
}
