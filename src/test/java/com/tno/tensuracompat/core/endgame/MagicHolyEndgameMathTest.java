package com.tno.tensuracompat.core.endgame;

import com.tno.tensuracompat.core.stage.ScalableFamily;
import com.tno.tensuracompat.core.stage.Stage;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

class MagicHolyEndgameMathTest {
    @Test
    void dementorUsesExactStageRecoveryFractions() {
        double pre = 100.0D;
        double nativePost = 10.0D;
        assertEquals(10.0D, MagicHolyEndgameMath.negotiateDementor(true, pre, nativePost,
                parameters(Stage.S4).dementorRecovery()));
        assertEquals(55.0D, MagicHolyEndgameMath.negotiateDementor(true, pre, nativePost,
                parameters(Stage.S5).dementorRecovery()));
        assertEquals(66.25D, MagicHolyEndgameMath.negotiateDementor(true, pre, nativePost,
                parameters(Stage.S6).dementorRecovery()));
        assertEquals(77.5D, MagicHolyEndgameMath.negotiateDementor(true, pre, nativePost,
                parameters(Stage.S7).dementorRecovery()));
    }

    @Test
    void actualDementorRemainsHarmfulAtEveryNegotiatedStage() {
        double pre = 100.0D;
        double nativePost = 10.0D;
        for (Stage stage : new Stage[]{Stage.S5, Stage.S6, Stage.S7}) {
            double negotiated = MagicHolyEndgameMath.negotiateDementor(
                    true, pre, nativePost, parameters(stage).dementorRecovery());
            assertTrue(negotiated < pre);
            assertTrue(negotiated >= nativePost);
        }
    }

    @Test
    void absentTraitMeansCallerKeepsNativeValueAndInvalidReductionCannotCreateGain() {
        assertEquals(10.0D, MagicHolyEndgameMath.negotiateDementor(false, 100.0D, 10.0D, 0.75D));
        assertEquals(120.0D, MagicHolyEndgameMath.negotiateDementor(true, 100.0D, 120.0D, 0.75D));
        assertEquals(10.0D, MagicHolyEndgameMath.negotiateDementor(true, Double.NaN, 10.0D, 0.75D));
    }

    @Test
    void adaptiveUsesExactStageRecoveryFractions() {
        double nativeFactor = 0.10D;
        assertEquals(0.10D, MagicHolyEndgameMath.negotiateAdaptive(true, nativeFactor,
                parameters(Stage.S4).adaptiveRecovery()));
        assertEquals(0.55D, MagicHolyEndgameMath.negotiateAdaptive(true, nativeFactor,
                parameters(Stage.S5).adaptiveRecovery()));
        assertEquals(0.6625D, MagicHolyEndgameMath.negotiateAdaptive(true, nativeFactor,
                parameters(Stage.S6).adaptiveRecovery()));
        assertEquals(0.775D, MagicHolyEndgameMath.negotiateAdaptive(true, nativeFactor,
                parameters(Stage.S7).adaptiveRecovery()));
    }

    @Test
    void nativeTenHitSequenceRemainsOwnedAndMeasurablyHarmful() {
        double recovery = parameters(Stage.S7).adaptiveRecovery();
        double negotiated = 1.0D;
        for (int hit = 1; hit <= 10; hit++) {
            double nativeFactor = hit == 1 ? 1.0D : Math.pow(0.5D, hit - 1);
            negotiated = MagicHolyEndgameMath.negotiateAdaptive(true, nativeFactor, recovery);
            if (hit == 1) assertEquals(1.0D, negotiated);
        }
        assertEquals(0.75048828125D, negotiated);
        assertTrue(negotiated < 1.0D);
        assertEquals(1.0D, MagicHolyEndgameMath.negotiateAdaptive(false, 1.0D, recovery));
    }

    @Test
    void adaptiveNeverCreatesGainFromInvalidNativeFactor() {
        assertEquals(1.25D, MagicHolyEndgameMath.negotiateAdaptive(true, 1.25D, 0.75D));
        assertEquals(-0.25D, MagicHolyEndgameMath.negotiateAdaptive(true, -0.25D, 0.75D));
    }

    private static MagicHolyEndgamePolicy.Parameters parameters(Stage stage) {
        return MagicHolyEndgamePolicy.parameters(stage, ScalableFamily.MAGIC_WEAPON);
    }
}
