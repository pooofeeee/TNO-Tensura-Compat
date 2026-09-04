package com.tno.tensuracompat.debug;

import com.tno.tensuracompat.core.stage.GearStageClasses;
import com.tno.tensuracompat.core.stage.ProductionStageScaling;
import com.tno.tensuracompat.core.stage.ScalableFamily;
import com.tno.tensuracompat.core.stage.Stage;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemStack;
import net.neoforged.fml.ModList;
import net.neoforged.fml.loading.FMLEnvironment;

import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.util.ArrayDeque;
import java.util.Deque;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Optional;

/**
 * Synchronous, development-only context for post-Phase-6 calibration.
 * Nothing is serialized or attached to gameplay objects; L2 owns all of its
 * trait state, including Adaptive memory.
 */
public final class Phase6CalibrationContext {
    private static final String L2_MISCS = "dev.xkmc.l2hostility.init.registrate.LHMiscs";
    private static final ThreadLocal<Deque<Frame>> FRAMES = ThreadLocal.withInitial(ArrayDeque::new);
    private static final ThreadLocal<Parameters> PARAMETERS = ThreadLocal.withInitial(() -> Parameters.NONE);

    private Phase6CalibrationContext() {
    }

    public static Optional<Scope> open(
            ItemStack gear,
            ScalableFamily family,
            LivingEntity target,
            double nativeEligibleAmount,
            double afterProductionStage,
            double afterTensuraDefense
    ) {
        if (!enabled() || family != ScalableFamily.MAGIC_WEAPON && family != ScalableFamily.HOLY_WEAPON) {
            return Optional.empty();
        }
        if (GearStageClasses.classification(gear).isEmpty()) return Optional.empty();
        Optional<Stage> stage = ProductionStageScaling.stage(gear);
        if (stage.isEmpty() || target == null || !ModList.get().isLoaded("l2hostility")) return Optional.empty();

        try {
            Object type = invoke(staticField(L2_MISCS, "MOB"), "type");
            Object result = invoke(type, "getExisting", target);
            Object cap = result instanceof Optional<?> optional ? optional.orElse(null) : result;
            if (cap == null || !booleanValue(invoke(cap, "isInitialized"))) return Optional.empty();
            Map<String, Integer> traits = relevantTraits(cap);
            Frame frame = new Frame(gear, stage.get(), family, nativeEligibleAmount,
                    afterProductionStage, afterTensuraDefense, target, cap, traits, PARAMETERS.get());
            Deque<Frame> stack = FRAMES.get();
            stack.push(frame);
            return Optional.of(new Scope(Thread.currentThread(), frame));
        }
        catch (ReflectiveOperationException exception) {
            return Optional.empty();
        }
    }

    public static Optional<Frame> current() {
        Deque<Frame> stack = FRAMES.get();
        return stack.isEmpty() ? Optional.empty() : Optional.of(stack.peek());
    }

    public static ParameterScope useParameters(Parameters parameters) {
        if (!enabled()) return ParameterScope.INACTIVE;
        Parameters previous = PARAMETERS.get();
        PARAMETERS.set(parameters);
        return new ParameterScope(Thread.currentThread(), previous, true);
    }

    public static boolean enabled() {
        return !FMLEnvironment.production && Boolean.getBoolean("tno.phase6.calibration");
    }

    private static Map<String, Integer> relevantTraits(Object cap) throws ReflectiveOperationException {
        Object value = readField(cap, "traits");
        if (!(value instanceof Map<?, ?> map)) return Map.of();
        Map<String, Integer> result = new LinkedHashMap<>();
        for (Map.Entry<?, ?> entry : map.entrySet()) {
            String id = traitId(entry.getKey());
            if (id.equals("l2hostility:adaptive") || id.equals("l2hostility:dementor")
                    || id.equals("l2hostility:dispell") || id.equals("l2hostility:regenerate")
                    || id.equals("l2hostility:tank")) {
                result.put(id, ((Number) entry.getValue()).intValue());
            }
        }
        return Map.copyOf(result);
    }

    private static String traitId(Object trait) throws ReflectiveOperationException {
        return invoke(invoke(trait, "getEntry"), "getId").toString();
    }

    private static Object staticField(String className, String name) throws ReflectiveOperationException {
        return Class.forName(className).getField(name).get(null);
    }

    private static Object readField(Object value, String name) throws ReflectiveOperationException {
        for (Class<?> current = value.getClass(); current != null; current = current.getSuperclass()) {
            try {
                Field field = current.getDeclaredField(name);
                field.setAccessible(true);
                return field.get(value);
            }
            catch (NoSuchFieldException ignored) {
            }
        }
        throw new NoSuchFieldException(value.getClass().getName() + "#" + name);
    }

    private static Object invoke(Object targetOrClass, String name, Object... args) throws ReflectiveOperationException {
        Class<?> type = targetOrClass instanceof Class<?> clazz ? clazz : targetOrClass.getClass();
        Method found = null;
        for (Method method : type.getMethods()) {
            if (method.getName().equals(name) && method.getParameterCount() == args.length) {
                found = method;
                break;
            }
        }
        if (found == null) throw new NoSuchMethodException(type.getName() + "#" + name);
        found.setAccessible(true);
        return found.invoke(Modifier.isStatic(found.getModifiers()) ? null : targetOrClass, args);
    }

    private static boolean booleanValue(Object value) {
        return value instanceof Boolean bool && bool;
    }

    public record Frame(
            ItemStack originatingGear,
            Stage stage,
            ScalableFamily family,
            double nativeEligibleAmount,
            double afterProductionStage,
            double afterTensuraDefense,
            LivingEntity target,
            Object existingL2Capability,
            Map<String, Integer> relevantTraits,
            Parameters parameters
    ) {
        public boolean hasTrait(String id) {
            return relevantTraits.getOrDefault(id, 0) > 0;
        }
    }

    public record Parameters(double genericHealthQ, double dementorRD, double adaptiveRA) {
        public static final Parameters NONE = new Parameters(0.0D, 0.0D, 0.0D);

        public Parameters {
            requireFraction("genericHealthQ", genericHealthQ);
            requireFraction("dementorRD", dementorRD);
            requireFraction("adaptiveRA", adaptiveRA);
        }

        private static void requireFraction(String name, double value) {
            if (!Double.isFinite(value) || value < 0.0D || value > 1.0D) {
                throw new IllegalArgumentException(name + " must be finite and within [0,1]");
            }
        }
    }

    public static final class Scope implements AutoCloseable {
        private final Thread owner;
        private final Frame frame;
        private boolean closed;

        private Scope(Thread owner, Frame frame) {
            this.owner = owner;
            this.frame = frame;
        }

        @Override
        public void close() {
            if (closed) return;
            if (Thread.currentThread() != owner) throw new IllegalStateException("calibration scope closed on another thread");
            Deque<Frame> stack = FRAMES.get();
            if (stack.isEmpty() || stack.pop() != frame) throw new IllegalStateException("calibration scope order violation");
            if (stack.isEmpty()) FRAMES.remove();
            closed = true;
        }
    }

    public static final class ParameterScope implements AutoCloseable {
        private static final ParameterScope INACTIVE = new ParameterScope(null, null, false);
        private final Thread owner;
        private final Parameters previous;
        private final boolean active;
        private boolean closed;

        private ParameterScope(Thread owner, Parameters previous, boolean active) {
            this.owner = owner;
            this.previous = previous;
            this.active = active;
        }

        @Override
        public void close() {
            if (closed || !active) return;
            if (Thread.currentThread() != owner) throw new IllegalStateException("parameter scope closed on another thread");
            if (previous == Parameters.NONE) PARAMETERS.remove();
            else PARAMETERS.set(previous);
            closed = true;
        }
    }
}
