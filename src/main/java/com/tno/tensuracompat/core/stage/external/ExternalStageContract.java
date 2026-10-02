package com.tno.tensuracompat.core.stage.external;

import com.tno.tensuracompat.core.stage.Stage;

import java.util.HashMap;
import java.util.Map;
import java.util.Objects;
import java.util.regex.Pattern;

/**
 * Instance-local, opt-in parameter registrations. Register during setup before use.
 * Scaling is pure: adapters must supply the original native value at exactly one
 * proven boundary. This core has no native hooks, ownership inference, or receipts.
 */
public final class ExternalStageContract {
    private static final Pattern NAMESPACE = Pattern.compile("[a-z0-9_.-]+");
    private static final Pattern PATH = Pattern.compile("[a-z0-9_.-]+(?:/[a-z0-9_.-]+)*");

    private final Map<ParameterKey, ParameterSpec> parameters = new HashMap<>();

    /** Canonical lowercase mechanic namespace:path plus a stable primitive/parameter path. */
    public record ParameterKey(String mechanicId, String parameterPath) {
        public ParameterKey {
            Objects.requireNonNull(mechanicId, "mechanicId");
            int separator = mechanicId.indexOf(':');
            if (separator < 1 || !NAMESPACE.matcher(mechanicId.substring(0, separator)).matches()) {
                throw new IllegalArgumentException("Mechanic ID must have an explicit lowercase namespace");
            }
            requirePath(mechanicId.substring(separator + 1));
            requirePath(parameterPath);
        }
    }

    /** The boundary identifies one native scalar site, not an entire method or mechanic. */
    public record ParameterSpec(ParameterKey key, String nativeBoundary, NumericScalingPolicy policy) {
        public ParameterSpec {
            Objects.requireNonNull(key, "key");
            requireBoundary(nativeBoundary);
            Objects.requireNonNull(policy, "policy");
        }
    }

    /**
     * Caller assertion only: a future native adapter must prove the exact source gear
     * and derive Stage from authoritative Tensura Gear EP before creating this context.
     * Unknown ownership must supply no context, never a fallback S0. Transport, lifetime,
     * and delayed snapshots belong to that adapter, not this immutable record.
     */
    public record ScalingContext(Stage stage, String nativeBoundary) {
        public ScalingContext {
            Objects.requireNonNull(stage, "stage");
            requireBoundary(nativeBoundary);
        }
    }

    public void register(ParameterSpec spec) {
        Objects.requireNonNull(spec, "spec");
        if (parameters.putIfAbsent(spec.key(), spec) != null) {
            throw new IllegalArgumentException("Parameter already registered: " + spec.key());
        }
    }

    /** Missing registration/context or a mismatched boundary leaves the native scalar unchanged. */
    public double scaleOriginal(ParameterKey key, ScalingContext context, double originalNativeValue) {
        ParameterSpec spec = applicableSpec(key, context);
        return spec == null ? originalNativeValue : spec.policy().scaleOriginal(originalNativeValue, context.stage());
    }

    public int scaleOriginalInteger(ParameterKey key, ScalingContext context, int originalNativeValue) {
        ParameterSpec spec = applicableSpec(key, context);
        return spec == null ? originalNativeValue : spec.policy().scaleOriginalInteger(originalNativeValue, context.stage());
    }

    private ParameterSpec applicableSpec(ParameterKey key, ScalingContext context) {
        if (key == null || context == null) {
            return null;
        }
        ParameterSpec spec = parameters.get(key);
        return spec != null && spec.nativeBoundary().equals(context.nativeBoundary()) ? spec : null;
    }

    private static void requireBoundary(String boundary) {
        Objects.requireNonNull(boundary, "nativeBoundary");
        if (boundary.isBlank()) {
            throw new IllegalArgumentException("A parameter must name its intended native scalar boundary");
        }
    }

    private static void requirePath(String path) {
        Objects.requireNonNull(path, "path");
        if (!PATH.matcher(path).matches()) {
            throw new IllegalArgumentException("Expected a canonical lowercase parameter/resource path");
        }
        for (String segment : path.split("/")) {
            if (segment.equals(".") || segment.equals("..")) {
                throw new IllegalArgumentException("Path aliases are not canonical parameter identities");
            }
        }
    }
}
