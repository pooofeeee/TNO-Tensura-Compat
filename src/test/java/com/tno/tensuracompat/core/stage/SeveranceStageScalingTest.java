package com.tno.tensuracompat.core.stage;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class SeveranceStageScalingTest {
    @Test
    void scalesOnlyNativeThreePointContribution() {
        var s0 = SeveranceStageScaling.adjustment(103.0D, 1, Stage.S0);
        var s7 = SeveranceStageScaling.adjustment(103.0D, 1, Stage.S7);

        assertEquals(3.0D, s0.nativeEligibleContribution());
        assertEquals(3.15D, s0.stagedEligibleContribution(), 1.0E-12D);
        assertEquals(103.15D, s0.stagedModifiedBase(), 1.0E-12D);
        assertEquals(4.2D, s7.stagedEligibleContribution(), 1.0E-12D);
        assertEquals(104.2D, s7.stagedModifiedBase(), 1.0E-12D);
    }

    @Test
    void lowMagnitudeS0DeltaNoLongerCollapsesAtNativeCeil() {
        double speed = 2.9919025534090893D;
        var adjustment = SeveranceStageScaling.adjustment(5.4D, 1, Stage.S0);

        assertEquals(17, (int) Math.ceil(speed * adjustment.nativeModifiedBase()));
        assertEquals(17, (int) Math.ceil(speed * adjustment.stagedModifiedBase()));
        assertEquals(18, SeveranceStageScaling.roundedProjectileDamage(speed, adjustment));
    }

    @Test
    void naturallyDistinctNativeCeilIsNotRaisedTwice() {
        double speed = 3.0D;
        var adjustment = SeveranceStageScaling.adjustment(5.4D, 1, Stage.S7);

        assertEquals(17, (int) Math.ceil(speed * adjustment.nativeModifiedBase()));
        assertEquals(20, (int) Math.ceil(speed * adjustment.stagedModifiedBase()));
        assertEquals(20, SeveranceStageScaling.roundedProjectileDamage(speed, adjustment));
    }

    @Test
    void largeApoPhysicalRemainderIsNotMultipliedByStage() {
        var adjustment = SeveranceStageScaling.adjustment(250.0D, 1, Stage.S7);

        assertEquals(1.2D, adjustment.eligibleDelta(), 1.0E-12D);
        assertEquals(251.2D, adjustment.stagedModifiedBase(), 1.0E-12D);
    }
}
