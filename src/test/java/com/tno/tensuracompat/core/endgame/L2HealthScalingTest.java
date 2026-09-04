package com.tno.tensuracompat.core.endgame;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

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
}
