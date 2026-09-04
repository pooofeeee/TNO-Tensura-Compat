package com.tno.tensuracompat.core.endgame;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

class L2HealthScalingTest {
    @Test
    void reproducesNativeLinearFormula() {
        assertEquals(25.0D, L2HealthScaling.nominalMultiplier(800, 0.03D, 1.0D, false));
        assertEquals(13.0D, L2HealthScaling.nominalMultiplier(800, 0.03D, 0.5D, false));
    }

    @Test
    void reproducesNativeExponentialFormula() {
        assertEquals(1.0D + (Math.pow(1.03D, 20) - 1.0D) * 0.75D,
                L2HealthScaling.nominalMultiplier(20, 0.03D, 0.75D, true));
    }

    @Test
    void invalidLiveInputsFailClosedBeforeProducingGain() {
        assertThrows(IllegalArgumentException.class,
                () -> L2HealthScaling.nominalMultiplier(-1, 0.03D, 1.0D, false));
        assertThrows(IllegalArgumentException.class,
                () -> L2HealthScaling.nominalMultiplier(800, Double.NaN, 1.0D, false));
        assertThrows(IllegalArgumentException.class,
                () -> L2HealthScaling.nominalMultiplier(800, 0.03D, -1.0D, false));
    }

    @Test
    void configuredLevelResponseIsMonotonicWithoutAnActivationCliff() {
        double h300 = L2HealthScaling.nominalMultiplier(300, 0.03D, 1.0D, false);
        double h600 = L2HealthScaling.nominalMultiplier(600, 0.03D, 1.0D, false);
        double h800 = L2HealthScaling.nominalMultiplier(800, 0.03D, 1.0D, false);
        double h1000 = L2HealthScaling.nominalMultiplier(1000, 0.03D, 1.0D, false);
        assertEquals(10.0D, h300);
        assertEquals(19.0D, h600);
        assertEquals(25.0D, h800);
        assertEquals(31.0D, h1000);
        assertTrue(h300 < h600 && h600 < h800 && h800 < h1000);
    }

    @Test
    void missingL2ContextIsRepresentedByExactNativeParity() {
        assertEquals(1.0D, MagicHolyEndgameMath.genericNormalization(null, 31.0D));
        assertEquals(1.0D, MagicHolyEndgameMath.genericNormalization(
                MagicHolyEndgamePolicy.Parameters.NONE, 31.0D));
    }
}
