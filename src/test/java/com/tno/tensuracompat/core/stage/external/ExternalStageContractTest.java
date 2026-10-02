package com.tno.tensuracompat.core.stage.external;

import com.tno.tensuracompat.core.stage.Stage;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;

import static com.tno.tensuracompat.core.stage.external.ExternalStageContract.ParameterKey;
import static com.tno.tensuracompat.core.stage.external.ExternalStageContract.ParameterSpec;
import static com.tno.tensuracompat.core.stage.external.ExternalStageContract.ScalingContext;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

class ExternalStageContractTest {
    private static final ParameterKey KEY = new ParameterKey("example:mechanic", "damage/amount");
    private static final String BOUNDARY = "example.Native#apply()@damage-argument";
    private static final ScalingContext CONTEXT = new ScalingContext(Stage.S7, BOUNDARY);

    @Test
    void anEmptyRegistryDoesNotTransformAnyNativeValue() {
        ExternalStageContract contract = new ExternalStageContract();
        assertEquals(100.0D, contract.scaleOriginal(KEY, CONTEXT, 100));
        assertEquals(3, contract.scaleOriginalInteger(KEY, CONTEXT, 3));
    }

    @Test
    void registrationOptsInOnlyTheExactMechanicAndPrimitiveAtItsIntendedBoundary() {
        ExternalStageContract contract = registeredContract();
        ParameterKey equalKey = new ParameterKey("example:mechanic", "damage/amount");
        assertEquals(140.0D, contract.scaleOriginal(equalKey, CONTEXT, 100));
        assertEquals(4, contract.scaleOriginalInteger(equalKey, CONTEXT, 3));
        assertEquals(100.0D, contract.scaleOriginal(new ParameterKey("another:mechanic", "damage/amount"), CONTEXT, 100));
        assertEquals(100.0D, contract.scaleOriginal(new ParameterKey("example:mechanic", "duration/ticks"), CONTEXT, 100));
        assertEquals(100.0D, contract.scaleOriginal(KEY, new ScalingContext(Stage.S7, "another-boundary"), 100));
        assertEquals(3, contract.scaleOriginalInteger(KEY, new ScalingContext(Stage.S7, "another-boundary"), 3));
    }

    @Test
    void duplicateRegistrationCannotReplaceTheOriginalPolicyOrBoundary() {
        ExternalStageContract contract = registeredContract();
        ParameterSpec replacement = new ParameterSpec(
                new ParameterKey("example:mechanic", "damage/amount"),
                "another-boundary", NumericScalingPolicy.identity(0, 1_000));
        assertThrows(IllegalArgumentException.class, () -> contract.register(replacement));
        assertEquals(140.0D, contract.scaleOriginal(KEY, CONTEXT, 100));
        assertEquals(100.0D, contract.scaleOriginal(KEY, new ScalingContext(Stage.S7, "another-boundary"), 100));
    }

    @Test
    void missingContextOrIdentityDoesNotFallBackToS0() {
        ExternalStageContract contract = registeredContract();
        assertEquals(100.0D, contract.scaleOriginal(KEY, null, 100));
        assertEquals(100.0D, contract.scaleOriginal(null, CONTEXT, 100));
        assertEquals(3, contract.scaleOriginalInteger(KEY, null, 3));
        assertEquals(3, contract.scaleOriginalInteger(null, CONTEXT, 3));
        assertEquals(105.0D, contract.scaleOriginal(KEY, new ScalingContext(Stage.S0, BOUNDARY), 100));
    }

    @Test
    void callsScaleOnlyTheSuppliedOriginalValueWithoutRetainingRuntimeState() {
        ExternalStageContract contract = registeredContract();
        assertEquals(140.0D, contract.scaleOriginal(KEY, CONTEXT, 100));
        assertEquals(140.0D, contract.scaleOriginal(KEY, CONTEXT, 100));
        assertEquals(28.0D, contract.scaleOriginal(KEY, CONTEXT, 20));
        assertEquals(105.0D, contract.scaleOriginal(KEY, new ScalingContext(Stage.S0, BOUNDARY), 100));
        assertEquals(100.0D, new ExternalStageContract().scaleOriginal(KEY, CONTEXT, 100));
    }

    @Test
    void registeredInvalidAndOffValuesStillFailClosed() {
        ExternalStageContract contract = registeredContract();
        assertEquals(-1.0D, contract.scaleOriginal(KEY, CONTEXT, -1));
        assertEquals(1_001.0D, contract.scaleOriginal(KEY, CONTEXT, 1_001));
        assertEquals(Double.NaN, contract.scaleOriginal(KEY, CONTEXT, Double.NaN));
        assertEquals(Double.POSITIVE_INFINITY, contract.scaleOriginal(KEY, CONTEXT, Double.POSITIVE_INFINITY));
        assertEquals(Double.doubleToRawLongBits(-0.0D), Double.doubleToRawLongBits(contract.scaleOriginal(KEY, CONTEXT, -0.0D)));
        assertEquals(-1, contract.scaleOriginalInteger(KEY, CONTEXT, -1));
    }

    @Test
    void independentlyRegisteredParametersKeepTheirOwnSignsAndPolicies() {
        ExternalStageContract contract = registeredContract();
        ParameterKey debuff = new ParameterKey("example:mechanic", "movement/coefficient");
        String debuffBoundary = "example.Native#apply()@movement-modifier";
        contract.register(new ParameterSpec(debuff, debuffBoundary, NumericScalingPolicy.negativeDebuff(-1)));
        assertEquals(-0.35D, contract.scaleOriginal(debuff, new ScalingContext(Stage.S7, debuffBoundary), -0.25D));
        assertEquals(140.0D, contract.scaleOriginal(KEY, CONTEXT, 100));
        assertEquals(-0.25D, contract.scaleOriginal(debuff, CONTEXT, -0.25D));
    }

    @ParameterizedTest
    @ValueSource(strings = {"mechanic", "Example:mechanic", "example:Mechanic", "example:", ":mechanic", "example:mechanic:alias", "example:mechanic/../alias"})
    void rejectsNoncanonicalMechanicIdentities(String mechanicId) {
        assertThrows(IllegalArgumentException.class, () -> new ParameterKey(mechanicId, "damage/amount"));
    }

    @ParameterizedTest
    @ValueSource(strings = {"", "Damage/amount", "/damage", "damage/", "damage//amount", "damage/../amount", "damage/./amount", "damage amount", " damage/amount"})
    void rejectsNoncanonicalPrimitivePaths(String parameterPath) {
        assertThrows(IllegalArgumentException.class, () -> new ParameterKey("example:mechanic", parameterPath));
    }

    @Test
    void specificationsAndContextsRequireAnExplicitBoundaryAndStage() {
        assertThrows(IllegalArgumentException.class, () -> new ParameterSpec(KEY, " ", NumericScalingPolicy.positiveMagnitude(100)));
        assertThrows(NullPointerException.class, () -> new ParameterSpec(KEY, BOUNDARY, null));
        assertThrows(NullPointerException.class, () -> new ParameterKey(null, "damage/amount"));
        assertThrows(NullPointerException.class, () -> new ParameterKey("example:mechanic", null));
        assertThrows(NullPointerException.class, () -> new ScalingContext(null, BOUNDARY));
        assertThrows(IllegalArgumentException.class, () -> new ScalingContext(Stage.S7, ""));
    }

    private static ExternalStageContract registeredContract() {
        ExternalStageContract contract = new ExternalStageContract();
        contract.register(new ParameterSpec(KEY, BOUNDARY, NumericScalingPolicy.positiveMagnitude(1_000)));
        return contract;
    }
}
