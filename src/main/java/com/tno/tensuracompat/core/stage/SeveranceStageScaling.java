package com.tno.tensuracompat.core.stage;

import io.github.manasmods.tensura.enchantment.TensuraEnchantments;
import net.minecraft.core.component.DataComponents;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.enchantment.ItemEnchantments;

import java.util.Optional;

/** Isolates Severance's native +3 contribution from every other physical component. */
public final class SeveranceStageScaling {
    public static final double NATIVE_BONUS_PER_LEVEL = 3.0D;
    private static final double MAX_ARROW_DAMAGE = 2.147483647E9D;

    private SeveranceStageScaling() {
    }

    public static Optional<Adjustment> adjustment(ItemStack weapon, double nativeModifiedBase) {
        int severanceLevel = severanceLevel(weapon);
        if (severanceLevel <= 0) {
            return Optional.empty();
        }
        return ProductionStageScaling.stage(weapon)
                .map(stage -> adjustment(nativeModifiedBase, severanceLevel, stage));
    }

    public static Adjustment adjustment(
            double nativeModifiedBase,
            int severanceLevel,
            Stage stage
    ) {
        if (!Double.isFinite(nativeModifiedBase)) {
            throw new IllegalArgumentException("nativeModifiedBase must be finite");
        }
        if (severanceLevel <= 0) {
            throw new IllegalArgumentException("severanceLevel must be positive");
        }
        double nativeEligible = NATIVE_BONUS_PER_LEVEL * severanceLevel;
        double stagedEligible = StageCurve.scaleEligible(nativeEligible, stage);
        return new Adjustment(
                nativeModifiedBase,
                nativeModifiedBase + stagedEligible - nativeEligible,
                nativeEligible,
                stagedEligible
        );
    }

    public static int roundedProjectileDamage(
            double speed,
            Adjustment adjustment
    ) {
        if (!Double.isFinite(speed) || speed < 0.0D) {
            throw new IllegalArgumentException("speed must be finite and non-negative");
        }
        double nativePreRound = clamp(speed * adjustment.nativeModifiedBase());
        double stagedPreRound = clamp(speed * adjustment.stagedModifiedBase());
        int nativeRounded = ceil(nativePreRound);
        int stagedRounded = ceil(stagedPreRound);

        if (stagedPreRound > nativePreRound
                && stagedRounded <= nativeRounded
                && nativeRounded < Integer.MAX_VALUE) {
            // The installed native path exposes only one integer physical hit.
            // Preserve the smallest observable result when a real positive
            // pre-round eligible delta falls into that same integer bucket.
            return nativeRounded + 1;
        }
        return stagedRounded;
    }

    private static int severanceLevel(ItemStack weapon) {
        ItemEnchantments enchantments = weapon.getOrDefault(
                DataComponents.ENCHANTMENTS, ItemEnchantments.EMPTY);
        for (var entry : enchantments.entrySet()) {
            if (entry.getKey().is(TensuraEnchantments.SEVERANCE)) {
                return entry.getIntValue();
            }
        }
        return 0;
    }

    private static double clamp(double value) {
        return Math.max(0.0D, Math.min(MAX_ARROW_DAMAGE, value));
    }

    private static int ceil(double value) {
        return (int) Math.min(Math.ceil(value), Integer.MAX_VALUE);
    }

    public record Adjustment(
            double nativeModifiedBase,
            double stagedModifiedBase,
            double nativeEligibleContribution,
            double stagedEligibleContribution
    ) {
        public double eligibleDelta() {
            return stagedEligibleContribution - nativeEligibleContribution;
        }
    }
}
