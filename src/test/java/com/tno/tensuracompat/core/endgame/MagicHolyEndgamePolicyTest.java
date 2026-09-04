package com.tno.tensuracompat.core.endgame;

import com.tno.tensuracompat.core.stage.ScalableFamily;
import com.tno.tensuracompat.core.stage.Stage;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.EnumSource;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

class MagicHolyEndgamePolicyTest {
    @ParameterizedTest
    @EnumSource(value = Stage.class, names = {"S0", "S1", "S2", "S3", "S4"})
    void lowerStagesAreExactNoOp(Stage stage) {
        assertEquals(MagicHolyEndgamePolicy.Parameters.NONE,
                MagicHolyEndgamePolicy.parameters(stage, ScalableFamily.MAGIC_WEAPON));
        assertEquals(MagicHolyEndgamePolicy.Parameters.NONE,
                MagicHolyEndgamePolicy.parameters(stage, ScalableFamily.HOLY_WEAPON));
    }

    @Test
    void exposesLockedS5ThroughS7Values() {
        assertEquals(new MagicHolyEndgamePolicy.Parameters(0.50D, 0.50D, 0.50D),
                MagicHolyEndgamePolicy.parameters(Stage.S5, ScalableFamily.MAGIC_WEAPON));
        assertEquals(new MagicHolyEndgamePolicy.Parameters(0.75D, 0.625D, 0.625D),
                MagicHolyEndgamePolicy.parameters(Stage.S6, ScalableFamily.HOLY_WEAPON));
        assertEquals(new MagicHolyEndgamePolicy.Parameters(1.00D, 0.75D, 0.75D),
                MagicHolyEndgamePolicy.parameters(Stage.S7, ScalableFamily.MAGIC_WEAPON));
    }

    @ParameterizedTest
    @EnumSource(value = ScalableFamily.class, names = {"SOUL_EATER", "ELEMENTAL_SLOTTING", "ENERGY_STEAL", "SEVERANCE"})
    void rejectsEveryUnrelatedFamily(ScalableFamily family) {
        assertFalse(MagicHolyEndgamePolicy.supports(family));
        assertFalse(MagicHolyEndgamePolicy.permitsNativeEvent(family, false));
        assertEquals(MagicHolyEndgamePolicy.Parameters.NONE,
                MagicHolyEndgamePolicy.parameters(Stage.S7, family));
    }

    @Test
    void matchingNullificationIsAnAbsoluteAdmissionGate() {
        assertFalse(MagicHolyEndgamePolicy.permitsNativeEvent(ScalableFamily.MAGIC_WEAPON, true));
        assertFalse(MagicHolyEndgamePolicy.permitsNativeEvent(ScalableFamily.HOLY_WEAPON, true));
        assertTrue(MagicHolyEndgamePolicy.permitsNativeEvent(ScalableFamily.MAGIC_WEAPON, false));
        assertTrue(MagicHolyEndgamePolicy.permitsNativeEvent(ScalableFamily.HOLY_WEAPON, false));
    }

    @Test
    void missingOrInvalidContextInputsAreNoOp() {
        assertEquals(MagicHolyEndgamePolicy.Parameters.NONE,
                MagicHolyEndgamePolicy.parameters(null, ScalableFamily.MAGIC_WEAPON));
        assertEquals(MagicHolyEndgamePolicy.Parameters.NONE,
                MagicHolyEndgamePolicy.parameters(Stage.S7, null));
        assertFalse(MagicHolyEndgamePolicy.Parameters.NONE.active());
        assertTrue(MagicHolyEndgamePolicy.parameters(Stage.S5, ScalableFamily.HOLY_WEAPON).active());
    }

    @Test
    void genericHealthUsesExactLockedStageFractions() {
        double h = 25.0D;
        assertEquals(1.0D, MagicHolyEndgameMath.genericNormalization(
                MagicHolyEndgamePolicy.parameters(Stage.S4, ScalableFamily.MAGIC_WEAPON), h));
        assertEquals(13.0D, MagicHolyEndgameMath.genericNormalization(
                MagicHolyEndgamePolicy.parameters(Stage.S5, ScalableFamily.MAGIC_WEAPON), h));
        assertEquals(19.0D, MagicHolyEndgameMath.genericNormalization(
                MagicHolyEndgamePolicy.parameters(Stage.S6, ScalableFamily.MAGIC_WEAPON), h));
        assertEquals(25.0D, MagicHolyEndgameMath.genericNormalization(
                MagicHolyEndgamePolicy.parameters(Stage.S7, ScalableFamily.MAGIC_WEAPON), h));
    }
}
