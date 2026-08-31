package com.tno.tensuracompat.core.stage;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

class StageResolverTest {
    @Test
    void resolvesCommonBoundariesAndCapsAtS3() {
        assertEquals(Stage.S0, StageResolver.resolve(49_999D, GearStageClass.COMMON));
        assertEquals(Stage.S1, StageResolver.resolve(50_000D, GearStageClass.COMMON));
        assertEquals(Stage.S1, StageResolver.resolve(249_999D, GearStageClass.COMMON));
        assertEquals(Stage.S2, StageResolver.resolve(250_000D, GearStageClass.COMMON));
        assertEquals(Stage.S2, StageResolver.resolve(999_999D, GearStageClass.COMMON));
        assertEquals(Stage.S3, StageResolver.resolve(1_000_000D, GearStageClass.COMMON));
        assertEquals(Stage.S3, StageResolver.resolve(Double.POSITIVE_INFINITY, GearStageClass.COMMON));
    }

    @Test
    void resolvesEveryRareBoundaryAndCapsAtS7() {
        assertBoundary(GearStageClass.RARE, 41_500L, Stage.S0, Stage.S1);
        assertBoundary(GearStageClass.RARE, 207_500L, Stage.S1, Stage.S2);
        assertBoundary(GearStageClass.RARE, 830_000L, Stage.S2, Stage.S3);
        assertBoundary(GearStageClass.RARE, 1_245_000L, Stage.S3, Stage.S4);
        assertBoundary(GearStageClass.RARE, 1_660_000L, Stage.S4, Stage.S5);
        assertBoundary(GearStageClass.RARE, 2_075_000L, Stage.S5, Stage.S6);
        assertBoundary(GearStageClass.RARE, 2_490_000L, Stage.S6, Stage.S7);
        assertEquals(Stage.S7, StageResolver.resolve(10_000_000D, GearStageClass.RARE));
    }

    @Test
    void rejectsNaNNativeEp() {
        assertThrows(IllegalArgumentException.class,
                () -> StageResolver.resolve(Double.NaN, GearStageClass.RARE));
    }

    private static void assertBoundary(
            GearStageClass stageClass,
            long threshold,
            Stage immediatelyBelow,
            Stage exactlyAt
    ) {
        assertEquals(immediatelyBelow, StageResolver.resolve(threshold - 1D, stageClass));
        assertEquals(exactlyAt, StageResolver.resolve(threshold, stageClass));
    }
}
