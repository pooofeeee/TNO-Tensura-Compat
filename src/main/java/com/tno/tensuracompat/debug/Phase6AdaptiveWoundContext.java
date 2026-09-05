package com.tno.tensuracompat.debug;

import io.github.manasmods.tensura.storage.TensuraStorages;
import io.github.manasmods.tensura.storage.effect.IEffect;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.neoforged.fml.loading.FMLEnvironment;

import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;

/** Development-only W3 negotiation at Tensura's native wound-clamp boundary. */
public final class Phase6AdaptiveWoundContext {
    private static final ThreadLocal<State> STATE = new ThreadLocal<>();

    private Phase6AdaptiveWoundContext() {
    }

    public static boolean enabled() {
        return !FMLEnvironment.production
                && Boolean.getBoolean("tno.phase6.calibration")
                && System.getProperty("tno.phase6.calibrationMode", "")
                .startsWith("adaptive_wound");
    }

    public static ParameterScope useRecovery(double recovery) {
        if (!enabled()) return ParameterScope.INACTIVE;
        requireFraction(recovery);
        if (STATE.get() != null) throw new IllegalStateException("nested Adaptive-wound parameter scope");
        State state = new State(recovery);
        STATE.set(state);
        return new ParameterScope(Thread.currentThread(), state, true);
    }

    public static void registerProjectile(
            AbstractArrow arrow,
            double combinedPostRound,
            double eligiblePostRound
    ) {
        State state = STATE.get();
        if (state == null || arrow == null) return;
        if (!Double.isFinite(combinedPostRound) || combinedPostRound <= 0.0D
                || !Double.isFinite(eligiblePostRound) || eligiblePostRound < 0.0D
                || eligiblePostRound > combinedPostRound) {
            throw new IllegalArgumentException("invalid Adaptive-wound projectile decomposition");
        }
        state.projections.put(arrow.getUUID(), new Projection(combinedPostRound, eligiblePostRound));
    }

    public static float negotiate(
            Entity target,
            float callbackDamage,
            float nativeCandidate,
            float nativeOffer
    ) {
        State state = STATE.get();
        if (state == null || !(target instanceof LivingEntity living)) return nativeOffer;
        Optional<Phase6SeveranceWallContext.BoundaryView> optional =
                Phase6SeveranceWallContext.currentBoundary(target);
        if (optional.isEmpty()) return nativeOffer;
        Phase6SeveranceWallContext.BoundaryView boundary = optional.get();
        Projection projection = state.projections.get(boundary.projectileUuid());
        if (projection == null || !boundary.sourceMsgId().equals("arrow")) return nativeOffer;

        double combined = boundary.combinedPhysicalAmount();
        if (combined <= 0.0D || Math.abs(combined - projection.combinedPostRound) > 0.001D
                || Math.abs(callbackDamage - combined) > 0.001D) {
            throw new IllegalStateException("Adaptive-wound physical/callback decomposition mismatch");
        }

        IEffect storage = TensuraStorages.getEffectFrom(living);
        double hpBeforeStorage = living.getHealth();
        double woundBeforeStorage = storage.getSeveranceAmount();
        double freeDeficit = Math.max(0.5D,
                living.getMaxHealth() - hpBeforeStorage - woundBeforeStorage);
        double postDementorRatio = clamp01(boundary.dementorOutput() / combined);
        double eligiblePreAdaptive = projection.eligiblePostRound * postDementorRatio;
        double nativeAdaptiveFactor = boundary.adaptiveApplied()
                ? clamp01(boundary.adaptiveFactor()) : 1.0D;
        double woundAdaptiveFactor = nativeAdaptiveFactor
                + state.recovery * (1.0D - nativeAdaptiveFactor);
        double nativeEligibleWound = 0.5D * eligiblePreAdaptive * nativeAdaptiveFactor;
        double negotiatedEligibleWound = 0.5D * eligiblePreAdaptive * woundAdaptiveFactor;
        double extra = Math.max(0.0D, negotiatedEligibleWound - nativeEligibleWound);
        double negotiatedOffer = Math.min(nativeCandidate, nativeOffer + extra);

        state.activeCallback = new ActiveCallback(
                living, boundary, projection, state.recovery, callbackDamage,
                nativeCandidate, freeDeficit, nativeOffer, postDementorRatio,
                eligiblePreAdaptive, nativeAdaptiveFactor, woundAdaptiveFactor,
                nativeEligibleWound, negotiatedEligibleWound, extra, negotiatedOffer,
                hpBeforeStorage, woundBeforeStorage);
        return (float) negotiatedOffer;
    }

    public static void finishCallback(Entity target) {
        State state = STATE.get();
        if (state == null || state.activeCallback == null
                || state.activeCallback.target != target) return;
        ActiveCallback active = state.activeCallback;
        state.activeCallback = null;
        IEffect storage = TensuraStorages.getEffectFrom(active.target);
        double hpAfterStorage = active.target.getHealth();
        double woundAfterStorage = storage.getSeveranceAmount();
        Phase5FSuiteBBenchmark.captureAdaptiveWoundTrace(new Snapshot(
                active.boundary.projectileUuid().toString(),
                active.boundary.sourceMsgId(), "minecraft:arrow",
                "tensura:effect_storage", "tensura:severance",
                active.projection.combinedPostRound,
                active.projection.eligiblePostRound,
                active.callbackDamage, active.nativeCandidate,
                active.nativeFreeDeficit, active.nativeOffer,
                active.postDementorRatio, active.eligiblePreAdaptive,
                active.nativeAdaptiveFactor, active.recovery,
                active.woundAdaptiveFactor, active.nativeEligibleWound,
                active.negotiatedEligibleWound, active.eligibleExtra,
                active.negotiatedOffer, active.hpBeforeStorage, hpAfterStorage,
                active.woundBeforeStorage, woundAfterStorage,
                Math.max(0.0D, hpAfterStorage < active.hpBeforeStorage
                        ? active.hpBeforeStorage - hpAfterStorage : 0.0D),
                active.boundary.adaptiveRank(), active.boundary.adaptiveCount(),
                active.boundary.adaptiveApplied(), active.boundary.dementorOutput(),
                active.boundary.adaptiveResult()));
    }

    private static double clamp01(double value) {
        return Math.max(0.0D, Math.min(1.0D, value));
    }

    private static void requireFraction(double value) {
        if (!Double.isFinite(value) || value < 0.0D || value > 1.0D) {
            throw new IllegalArgumentException("Adaptive wound recovery must be within [0,1]");
        }
    }

    private static final class State {
        final double recovery;
        final Map<UUID, Projection> projections = new LinkedHashMap<>();
        ActiveCallback activeCallback;

        State(double recovery) {
            this.recovery = recovery;
        }
    }

    private record Projection(double combinedPostRound, double eligiblePostRound) {
    }

    private record ActiveCallback(
            LivingEntity target,
            Phase6SeveranceWallContext.BoundaryView boundary,
            Projection projection,
            double recovery,
            double callbackDamage,
            double nativeCandidate,
            double nativeFreeDeficit,
            double nativeOffer,
            double postDementorRatio,
            double eligiblePreAdaptive,
            double nativeAdaptiveFactor,
            double woundAdaptiveFactor,
            double nativeEligibleWound,
            double negotiatedEligibleWound,
            double eligibleExtra,
            double negotiatedOffer,
            double hpBeforeStorage,
            double woundBeforeStorage
    ) {
    }

    public record Snapshot(
            String projectileUuid,
            String physicalSourceMsgId,
            String physicalSourceId,
            String woundStateIdentity,
            String nativeCeilingSourceId,
            double combinedPhysicalPreL2,
            double eligiblePhysicalPostRound,
            double nativeCallbackDamage,
            double nativeCandidate,
            double nativeHpDeficitConstraint,
            double nativePostClampOffer,
            double tankDementorSurvivalRatio,
            double eligiblePreAdaptive,
            double nativeAdaptiveFactor,
            double diagnosticRecovery,
            double diagnosticWoundAdaptiveFactor,
            double nativeEligibleWoundPotential,
            double diagnosticEligibleWoundPotential,
            double diagnosticEligibleExtra,
            double negotiatedNativeStorageOffer,
            double hpBeforeNativeStorage,
            double hpAfterNativeStorage,
            double woundBeforeNativeStorage,
            double woundAfterNativeStorage,
            double nativeCeilingEnforcementHpLoss,
            int adaptiveRank,
            int adaptiveCount,
            boolean adaptiveApplied,
            double postDementorPhysical,
            double postAdaptivePhysical
    ) {
    }

    public static final class ParameterScope implements AutoCloseable {
        private static final ParameterScope INACTIVE = new ParameterScope(null, null, false);
        private final Thread owner;
        private final State state;
        private final boolean active;
        private boolean closed;

        private ParameterScope(Thread owner, State state, boolean active) {
            this.owner = owner;
            this.state = state;
            this.active = active;
        }

        @Override
        public void close() {
            if (closed || !active) return;
            if (Thread.currentThread() != owner || STATE.get() != state) {
                throw new IllegalStateException("Adaptive-wound parameter scope mismatch");
            }
            if (state.activeCallback != null) {
                throw new IllegalStateException("unfinished Adaptive-wound native callback");
            }
            STATE.remove();
            closed = true;
        }
    }
}
