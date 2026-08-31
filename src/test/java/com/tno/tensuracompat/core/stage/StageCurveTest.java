package com.tno.tensuracompat.core.stage;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.EnumSource;

import java.util.Optional;

import static org.junit.jupiter.api.Assertions.assertEquals;

class StageCurveTest {
    @Test
    void exposesExactCurveCMultipliers() {
        assertEquals(1.05D, StageCurve.multiplier(Stage.S0));
        assertEquals(1.10D, StageCurve.multiplier(Stage.S1));
        assertEquals(1.15D, StageCurve.multiplier(Stage.S2));
        assertEquals(1.20D, StageCurve.multiplier(Stage.S3));
        assertEquals(1.25D, StageCurve.multiplier(Stage.S4));
        assertEquals(1.30D, StageCurve.multiplier(Stage.S5));
        assertEquals(1.35D, StageCurve.multiplier(Stage.S6));
        assertEquals(1.40D, StageCurve.multiplier(Stage.S7));
    }

    @Test
    void noScalableEngravingProducesZeroTnoCombatGainAtS7() {
        assertEquals(0.0D, StageCurve.combatGain(
                100.0D,
                Stage.S7,
                Optional.empty(),
                ScalableFamily.MAGIC_WEAPON
        ));
    }

    @Test
    void onlyActiveFamilyScales() {
        assertEquals(140.0D, StageCurve.scaleForActiveFamily(
                100.0D,
                Stage.S7,
                Optional.of(ScalableFamily.MAGIC_WEAPON),
                ScalableFamily.MAGIC_WEAPON
        ));
        assertEquals(100.0D, StageCurve.scaleForActiveFamily(
                100.0D,
                Stage.S7,
                Optional.of(ScalableFamily.MAGIC_WEAPON),
                ScalableFamily.HOLY_WEAPON
        ));
    }

    @ParameterizedTest
    @EnumSource(ScalableFamily.class)
    void everyFamilyScalesOnlyItsOwnEligibleContribution(ScalableFamily family) {
        assertEquals(140.0D, StageCurve.scaleForActiveFamily(
                100.0D, Stage.S7, Optional.of(family), family));

        ScalableFamily different = family == ScalableFamily.MAGIC_WEAPON
                ? ScalableFamily.HOLY_WEAPON
                : ScalableFamily.MAGIC_WEAPON;
        assertEquals(100.0D, StageCurve.scaleForActiveFamily(
                100.0D, Stage.S7, Optional.of(family), different));
    }
}
