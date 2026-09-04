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

    private static MagicHolyEndgamePolicy.Parameters parameters(Stage stage) {
        return MagicHolyEndgamePolicy.parameters(stage, ScalableFamily.MAGIC_WEAPON);
    }
}
