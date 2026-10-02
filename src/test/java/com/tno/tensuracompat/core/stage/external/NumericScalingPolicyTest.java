package com.tno.tensuracompat.core.stage.external;

import com.tno.tensuracompat.core.stage.Stage;
import com.tno.tensuracompat.core.stage.StageCurve;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.EnumSource;

import java.util.List;

import static com.tno.tensuracompat.core.stage.external.NumericScalingPolicy.Kind;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

class NumericScalingPolicyTest {
    @ParameterizedTest
    @EnumSource(Stage.class)
    void magnitudePoliciesReuseCurveCWithoutChangingNativeSigns(Stage stage) {
        double multiplier = StageCurve.multiplier(stage);
        assertEquals(20.0D * multiplier, NumericScalingPolicy.positiveMagnitude(100).scaleOriginal(20, stage));
        assertEquals(-0.25D * multiplier, NumericScalingPolicy.negativeDebuff(-1).scaleOriginal(-0.25D, stage));
        assertEquals(20.0D * multiplier, NumericScalingPolicy.durationLengthening(1, 100).scaleOriginal(20, stage));
        assertEquals(0.2D * multiplier, NumericScalingPolicy.probability(1).scaleOriginal(0.2D, stage));
        assertEquals(5.0D * multiplier, NumericScalingPolicy.radiusRange(10).scaleOriginal(5, stage));
        assertEquals(10.0D * multiplier, NumericScalingPolicy.resourceMagnitude(-50, 50).scaleOriginal(10, stage));
        assertEquals(-10.0D * multiplier, NumericScalingPolicy.resourceMagnitude(-50, 50).scaleOriginal(-10, stage));
    }

    @ParameterizedTest
    @EnumSource(Stage.class)
    void durationAndCooldownReductionUseTheInverseExistingMultiplier(Stage stage) {
        double expected = 20.0D / StageCurve.multiplier(stage);
        assertEquals(expected, NumericScalingPolicy.durationReduction(1, 100).scaleOriginal(20, stage));
        assertEquals(expected, NumericScalingPolicy.cooldownReduction(1, 100).scaleOriginal(20, stage));
    }

    @ParameterizedTest
    @EnumSource(Stage.class)
    void integerRoundingIsConservativeForBothSignsAndDirections(Stage stage) {
        double multiplier = StageCurve.multiplier(stage);
        assertEquals((int) Math.floor(3 * multiplier), NumericScalingPolicy.positiveMagnitude(100).scaleOriginalInteger(3, stage));
        assertEquals((int) Math.ceil(-3 * multiplier), NumericScalingPolicy.negativeDebuff(-100).scaleOriginalInteger(-3, stage));
        assertEquals((int) Math.floor(3 * multiplier), NumericScalingPolicy.durationLengthening(1, 100).scaleOriginalInteger(3, stage));
        assertEquals((int) Math.ceil(3 / multiplier), NumericScalingPolicy.durationReduction(1, 100).scaleOriginalInteger(3, stage));
        assertEquals((int) Math.ceil(3 / multiplier), NumericScalingPolicy.cooldownReduction(1, 100).scaleOriginalInteger(3, stage));
        assertEquals((int) Math.ceil(-3 * multiplier), NumericScalingPolicy.resourceMagnitude(-100, 100).scaleOriginalInteger(-3, stage));
    }

    @Test
    void roundingHandlesIntegralCurveBoundariesWithoutEscapingExplicitBounds() {
        assertEquals(115, NumericScalingPolicy.positiveMagnitude(200).scaleOriginalInteger(100, Stage.S2));
        assertEquals(-115, NumericScalingPolicy.negativeDebuff(-200).scaleOriginalInteger(-100, Stage.S2));
        assertEquals(115, NumericScalingPolicy.durationLengthening(1, 200).scaleOriginalInteger(100, Stage.S2));
        assertEquals(3, NumericScalingPolicy.positiveMagnitude(Math.nextDown(4.0D)).scaleOriginalInteger(3, Stage.S7));
        assertEquals(-3, NumericScalingPolicy.negativeDebuff(Math.nextUp(-4.0D)).scaleOriginalInteger(-3, Stage.S7));
        assertEquals(4, NumericScalingPolicy.cooldownReduction(Math.nextUp(3.0D), 10).scaleOriginalInteger(4, Stage.S7));
    }

    @Test
    void preservesZeroOffValuesIncludingSignedZeroForEveryKind() {
        for (NumericScalingPolicy policy : policies()) {
            assertSameBits(0.0D, policy.scaleOriginal(0.0D, Stage.S7));
            assertSameBits(-0.0D, policy.scaleOriginal(-0.0D, Stage.S7));
            assertEquals(0, policy.scaleOriginalInteger(0, Stage.S7));
        }
    }

    @Test
    void invalidScalarsAndMissingStageRemainUnchanged() {
        for (NumericScalingPolicy policy : policies()) {
            for (double invalid : new double[]{Double.NaN, Double.POSITIVE_INFINITY, Double.NEGATIVE_INFINITY}) {
                assertSameBits(invalid, policy.scaleOriginal(invalid, Stage.S7));
            }
            assertSameBits(10.0D, policy.scaleOriginal(10.0D, null));
            assertEquals(10, policy.scaleOriginalInteger(10, null));
        }
    }

    @Test
    void rejectsOppositeSignsOutOfDomainInputsAndDurationSentinelsWithoutRepairingThem() {
        assertEquals(-1.0D, NumericScalingPolicy.positiveMagnitude(100).scaleOriginal(-1, Stage.S7));
        assertEquals(101.0D, NumericScalingPolicy.positiveMagnitude(100).scaleOriginal(101, Stage.S7));
        assertEquals(0.1D, NumericScalingPolicy.negativeDebuff(-1).scaleOriginal(0.1D, Stage.S7));
        assertEquals(-1.1D, NumericScalingPolicy.negativeDebuff(-1).scaleOriginal(-1.1D, Stage.S7));
        assertEquals(-1.0D, NumericScalingPolicy.durationLengthening(1, 100).scaleOriginal(-1, Stage.S7));
        assertEquals(0.5D, NumericScalingPolicy.durationLengthening(1, 100).scaleOriginal(0.5D, Stage.S7));
        assertEquals(-1, NumericScalingPolicy.durationReduction(1, 100).scaleOriginalInteger(-1, Stage.S7));
        assertEquals(-1, NumericScalingPolicy.cooldownReduction(1, 100).scaleOriginalInteger(-1, Stage.S7));
        assertEquals(101, NumericScalingPolicy.cooldownReduction(1, 100).scaleOriginalInteger(101, Stage.S7));
        assertEquals(-0.1D, NumericScalingPolicy.probability(1).scaleOriginal(-0.1D, Stage.S7));
        assertEquals(1.1D, NumericScalingPolicy.probability(1).scaleOriginal(1.1D, Stage.S7));
        assertEquals(-1.0D, NumericScalingPolicy.radiusRange(10).scaleOriginal(-1, Stage.S7));
        assertEquals(11.0D, NumericScalingPolicy.radiusRange(10).scaleOriginal(11, Stage.S7));
        assertEquals(-51.0D, NumericScalingPolicy.resourceMagnitude(-50, 50).scaleOriginal(-51, Stage.S7));
        assertEquals(51.0D, NumericScalingPolicy.resourceMagnitude(-50, 50).scaleOriginal(51, Stage.S7));
        assertEquals(1.0D, NumericScalingPolicy.probability(0.8D).scaleOriginal(1, Stage.S7));
    }

    @Test
    void appliesExplicitCapsFloorsAndNativeProbabilityEndpoints() {
        assertEquals(110.0D, NumericScalingPolicy.positiveMagnitude(110).scaleOriginal(100, Stage.S7));
        assertEquals(-1.0D, NumericScalingPolicy.negativeDebuff(-1).scaleOriginal(-0.9D, Stage.S7));
        assertEquals(55.0D, NumericScalingPolicy.durationLengthening(1, 55).scaleOriginal(50, Stage.S7));
        assertEquals(8.0D, NumericScalingPolicy.durationReduction(8, 100).scaleOriginal(10, Stage.S7));
        assertEquals(8, NumericScalingPolicy.cooldownReduction(8, 100).scaleOriginalInteger(10, Stage.S7));
        assertEquals(1.0D, NumericScalingPolicy.probability(1).scaleOriginal(0.9D, Stage.S7));
        assertEquals(1.0D, NumericScalingPolicy.probability(1).scaleOriginal(1, Stage.S7));
        assertEquals(0.7D, NumericScalingPolicy.probability(0.7D).scaleOriginal(0.6D, Stage.S7));
        assertEquals(10.0D, NumericScalingPolicy.radiusRange(10).scaleOriginal(9, Stage.S7));
        assertEquals(-10.0D, NumericScalingPolicy.resourceMagnitude(-10, 10).scaleOriginal(-9, Stage.S7));
        assertEquals(10.0D, NumericScalingPolicy.resourceMagnitude(-10, 10).scaleOriginal(9, Stage.S7));
    }

    @Test
    void identityNeverTransformsBinaryOrOtherNativeValues() {
        NumericScalingPolicy policy = NumericScalingPolicy.identity(0, 1);
        for (double value : new double[]{0, 1, -1, 5, Double.NaN, Double.POSITIVE_INFINITY}) {
            assertSameBits(value, policy.scaleOriginal(value, Stage.S7));
        }
        assertEquals(1, policy.scaleOriginalInteger(1, Stage.S7));
    }

    @Test
    void arithmeticOverflowAndUnrepresentableIntegerResultsFailClosed() {
        assertEquals(Double.MAX_VALUE, NumericScalingPolicy.positiveMagnitude(Double.MAX_VALUE).scaleOriginal(Double.MAX_VALUE, Stage.S7));
        assertEquals(-Double.MAX_VALUE, NumericScalingPolicy.negativeDebuff(-Double.MAX_VALUE).scaleOriginal(-Double.MAX_VALUE, Stage.S7));
        assertEquals(Integer.MAX_VALUE, NumericScalingPolicy.positiveMagnitude(Double.MAX_VALUE).scaleOriginalInteger(Integer.MAX_VALUE, Stage.S7));
        assertEquals(Integer.MIN_VALUE, NumericScalingPolicy.negativeDebuff(-Double.MAX_VALUE).scaleOriginalInteger(Integer.MIN_VALUE, Stage.S7));
        assertEquals(3, NumericScalingPolicy.positiveMagnitude(3.5D).scaleOriginalInteger(3, Stage.S7));
        assertEquals(3, NumericScalingPolicy.cooldownReduction(2.5D, 10).scaleOriginalInteger(3, Stage.S7));
    }

    @Test
    void rejectsNonfiniteInvertedAndSignIncompatibleConfigurations() {
        for (double invalid : new double[]{Double.NaN, Double.POSITIVE_INFINITY, Double.NEGATIVE_INFINITY}) {
            assertThrows(IllegalArgumentException.class, () -> NumericScalingPolicy.positiveMagnitude(invalid));
            assertThrows(IllegalArgumentException.class, () -> NumericScalingPolicy.resourceMagnitude(invalid, 10));
        }
        assertThrows(IllegalArgumentException.class, () -> NumericScalingPolicy.resourceMagnitude(10, -10));
        assertThrows(IllegalArgumentException.class, () -> NumericScalingPolicy.positiveMagnitude(-1));
        assertThrows(IllegalArgumentException.class, () -> new NumericScalingPolicy(Kind.POSITIVE_MAGNITUDE, -1, 10));
        assertThrows(IllegalArgumentException.class, () -> new NumericScalingPolicy(Kind.NEGATIVE_DEBUFF, -1, 0.1D));
        assertThrows(IllegalArgumentException.class, () -> NumericScalingPolicy.probability(1.1D));
        assertThrows(IllegalArgumentException.class, () -> NumericScalingPolicy.durationLengthening(0, 100));
        assertThrows(IllegalArgumentException.class, () -> NumericScalingPolicy.durationReduction(0, 100));
        assertThrows(IllegalArgumentException.class, () -> NumericScalingPolicy.cooldownReduction(0, 100));
        assertThrows(NullPointerException.class, () -> new NumericScalingPolicy(null, 0, 1));
    }

    private static List<NumericScalingPolicy> policies() {
        return List.of(
                NumericScalingPolicy.positiveMagnitude(100),
                NumericScalingPolicy.negativeDebuff(-1),
                NumericScalingPolicy.durationLengthening(1, 100),
                NumericScalingPolicy.durationReduction(1, 100),
                NumericScalingPolicy.cooldownReduction(1, 100),
                NumericScalingPolicy.probability(1),
                NumericScalingPolicy.radiusRange(10),
                NumericScalingPolicy.resourceMagnitude(-50, 50),
                NumericScalingPolicy.identity(0, 1)
        );
    }

    private static void assertSameBits(double expected, double actual) {
        assertEquals(Double.doubleToRawLongBits(expected), Double.doubleToRawLongBits(actual));
    }
}
