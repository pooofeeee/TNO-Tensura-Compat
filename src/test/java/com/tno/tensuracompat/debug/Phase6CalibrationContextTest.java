package com.tno.tensuracompat.debug;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertThrows;

class Phase6CalibrationContextTest {
    @Test
    void acceptsClosedCalibrationFractions() {
        assertDoesNotThrow(() -> new Phase6CalibrationContext.Parameters(0.0D, 0.5D, 1.0D));
    }

    @Test
    void rejectsOutOfRangeOrNonFiniteCalibrationFractions() {
        assertThrows(IllegalArgumentException.class,
                () -> new Phase6CalibrationContext.Parameters(-0.01D, 0.0D, 0.0D));
        assertThrows(IllegalArgumentException.class,
                () -> new Phase6CalibrationContext.Parameters(0.0D, 1.01D, 0.0D));
        assertThrows(IllegalArgumentException.class,
                () -> new Phase6CalibrationContext.Parameters(0.0D, 0.0D, Double.NaN));
    }
}
