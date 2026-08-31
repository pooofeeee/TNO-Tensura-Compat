package com.tno.tensuracompat.core.stage;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

class ResistanceRecoveryCurveTest {
    @Test
    void lockedPenetrationScheduleIsExact() {
        assertEquals(0.0D, ResistanceRecoveryCurve.penetration(Stage.S0));
        assertEquals(0.0D, ResistanceRecoveryCurve.penetration(Stage.S4));
        assertEquals(0.25D, ResistanceRecoveryCurve.penetration(Stage.S5));
        assertEquals(0.50D, ResistanceRecoveryCurve.penetration(Stage.S6));
        assertEquals(1.0D, ResistanceRecoveryCurve.penetration(Stage.S7));
    }

    @Test
    void recoversOnlyTheMeasuredMatchingResistanceLoss() {
        assertEquals(50.0D, ResistanceRecoveryCurve.recover(100.0D, 50.0D, Stage.S4));
        assertEquals(62.5D, ResistanceRecoveryCurve.recover(100.0D, 50.0D, Stage.S5));
        assertEquals(75.0D, ResistanceRecoveryCurve.recover(100.0D, 50.0D, Stage.S6));
        assertEquals(100.0D, ResistanceRecoveryCurve.recover(100.0D, 50.0D, Stage.S7));
    }

    @Test
    void nativeHpGateLossCanBeRecoveredWithoutInventingDownstreamDamage() {
        double post = ResistanceRecoveryCurve.nativePostResistance(25.0D, 100.0D, 0.5D, 0.5D);
        assertEquals(0.0D, post);
        assertEquals(6.25D, ResistanceRecoveryCurve.recover(25.0D, post, Stage.S5));
        assertEquals(12.5D, ResistanceRecoveryCurve.recover(25.0D, post, Stage.S6));
        assertEquals(25.0D, ResistanceRecoveryCurve.recover(25.0D, post, Stage.S7));
        assertEquals(0.0D,
                ResistanceRecoveryCurve.nativePostResistance(50.0D, 100.0D, 0.5D, 0.5D));
    }

    @Test
    void invalidPostAmountCannotCreateRecovery() {
        assertThrows(IllegalArgumentException.class,
                () -> ResistanceRecoveryCurve.recover(10.0D, 11.0D, Stage.S7));
    }
}
