package com.tno.tensuracompat.debug;

import com.tno.tensuracompat.core.stage.GearStageClasses;
import com.tno.tensuracompat.core.stage.ProductionStageScaling;
import com.tno.tensuracompat.core.stage.ScalableFamily;
import com.tno.tensuracompat.core.stage.Stage;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.resources.ResourceLocation;
import net.neoforged.fml.ModList;
import net.neoforged.fml.loading.FMLEnvironment;

import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.lang.reflect.Proxy;
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
    private static final String L2_CONFIG = "dev.xkmc.l2hostility.init.data.LHConfig";
    private static final String ATTACK_HANDLER = "dev.xkmc.l2damagetracker.contents.attack.AttackEventHandler";
    private static final String ATTACK_LISTENER = "dev.xkmc.l2damagetracker.contents.attack.AttackListener";
    private static final String DAMAGE_MODIFIER = "dev.xkmc.l2damagetracker.contents.attack.DamageModifier";
    private static final String DAMAGE_ORDER = "dev.xkmc.l2damagetracker.contents.attack.DamageModifier$Order";
    private static final int LISTENER_PRIORITY = 4501;
    private static final int BEFORE_DEMENTOR = 7435;
    private static final int AFTER_DEMENTOR = 7437;
    private static final int AFTER_ADAPTIVE = 7437;
    private static final ThreadLocal<Deque<Frame>> FRAMES = ThreadLocal.withInitial(ArrayDeque::new);
    private static final ThreadLocal<Parameters> PARAMETERS = ThreadLocal.withInitial(() -> Parameters.NONE);
    private static boolean l2ListenerRegistered;

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
        if (GearStageClasses.classification(gear).isEmpty()) {
            throw new IllegalStateException("development calibration received unclassified gear "
                    + BuiltInRegistries.ITEM.getKey(gear.getItem()));
        }
        Optional<Stage> stage = ProductionStageScaling.stage(gear);
        if (stage.isEmpty()) {
            throw new IllegalStateException("development calibration gear has no production Stage");
        }
        if (target == null) {
            throw new IllegalStateException("development calibration target is absent");
        }
        if (!ModList.get().isLoaded("l2hostility")) {
            throw new IllegalStateException("development calibration requires the local L2 Hostility runtime");
        }

        try {
            Object type = invoke(staticField(L2_MISCS, "MOB"), "type");
            Object result = invoke(type, "getExisting", target);
            Object cap = result instanceof Optional<?> optional ? optional.orElse(null) : result;
            if (cap == null || !booleanValue(invoke(cap, "isInitialized"))) {
                throw new IllegalStateException("development calibration target has no initialized existing L2 attachment");
            }
            Map<String, Integer> traits = relevantTraits(cap);
            Frame frame = new Frame(gear, stage.get(), family, nativeEligibleAmount,
                    afterProductionStage, afterTensuraDefense, target, cap, traits, PARAMETERS.get(), new Trace());
            Deque<Frame> stack = FRAMES.get();
            stack.push(frame);
            return Optional.of(new Scope(Thread.currentThread(), frame));
        }
        catch (ReflectiveOperationException exception) {
            throw new IllegalStateException("could not open development-only L2 calibration context", exception);
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

    /** Registers an optional runtime listener at L2's own defensive modifier boundary. */
    public static synchronized void registerL2Listener() {
        if (!enabled() || l2ListenerRegistered) return;
        if (!ModList.get().isLoaded("l2hostility")) return;
        try {
            Class<?> listenerType = Class.forName(ATTACK_LISTENER);
            Object listener = Proxy.newProxyInstance(listenerType.getClassLoader(), new Class<?>[]{listenerType},
                    (proxy, method, args) -> {
                        if (method.getDeclaringClass() == Object.class) {
                            return objectMethod(proxy, method, args, "TNO Phase 6 calibration L2 listener");
                        }
                        if (method.getName().equals("onDamage") && args != null && args.length == 1) {
                            addDiagnosticModifiers(args[0]);
                        }
                        return method.getReturnType() == boolean.class ? false : null;
                    });
            Class<?> handler = Class.forName(ATTACK_HANDLER);
            Method register = handler.getMethod("register", int.class, listenerType);
            register.invoke(null, LISTENER_PRIORITY, listener);
            l2ListenerRegistered = true;
        }
        catch (ReflectiveOperationException exception) {
            throw new IllegalStateException("could not register development-only L2 calibration listener", exception);
        }
    }

    private static void addDiagnosticModifiers(Object defence) throws ReflectiveOperationException {
        Frame frame = current().orElse(null);
        if (frame == null || invoke(defence, "getTarget") != frame.target()) return;
        Object source = invoke(defence, "getSource");
        String msgId = String.valueOf(invoke(source, "getMsgId"));
        if (!msgId.equals(frame.family() == ScalableFamily.MAGIC_WEAPON
                ? "tensura.magic" : "tensura.holy_damage")) return;

        Trace trace = frame.trace();
        trace.sourceMsgId = msgId;
        trace.damageOriginal = numberValue(invoke(defence, "getDamageOriginal"));
        trace.genericHealthMultiplier = genericHealthMultiplier(frame);
        double normalization = 1.0D + frame.parameters().genericHealthQ()
                * (trace.genericHealthMultiplier - 1.0D);
        invoke(defence, "addDealtModifier", modifier("PRE_NONLINEAR", BEFORE_DEMENTOR,
                "calibration_generic_health", value -> {
                    trace.genericPre = value;
                    trace.genericPost = value * normalization;
                    return trace.genericPost;
                }));

        if (frame.hasTrait("l2hostility:dementor")) {
            trace.dementorApplied = true;
            invoke(defence, "addDealtModifier", modifier("PRE_NONLINEAR", AFTER_DEMENTOR,
                    "calibration_dementor_recovery", value -> {
                        trace.dementorPre = trace.genericPost;
                        trace.dementorNativePost = value;
                        trace.dementorDiagnosticPost = value + frame.parameters().dementorRD()
                                * (trace.dementorPre - value);
                        return trace.dementorDiagnosticPost;
                    }));
        }
        else {
            invoke(defence, "addDealtModifier", modifier("PRE_NONLINEAR", AFTER_DEMENTOR,
                    "calibration_dementor_observation", value -> {
                        trace.dementorPre = trace.genericPost;
                        trace.dementorNativePost = value;
                        trace.dementorDiagnosticPost = value;
                        return value;
                    }));
        }

        if (frame.hasTrait("l2hostility:adaptive")) {
            trace.adaptiveApplied = true;
            trace.adaptiveRank = frame.relevantTraits().getOrDefault("l2hostility:adaptive", 0);
            trace.adaptiveMemoryCapacity = trace.adaptiveRank;
            trace.adaptiveCount = adaptiveCount(frame, msgId);
            trace.configuredAdaptFactor = serverDouble("adaptFactor");
            invoke(defence, "addDealtModifier", modifier("POST_MULTIPLICATIVE", AFTER_ADAPTIVE,
                    "calibration_adaptive_recovery", value -> {
                        trace.adaptivePre = trace.dementorDiagnosticPost;
                        trace.adaptiveNativeFactor = value;
                        trace.adaptiveDiagnosticFactor = value + frame.parameters().adaptiveRA() * (1.0D - value);
                        trace.adaptiveNativePost = trace.adaptivePre * value;
                        trace.adaptiveDiagnosticPost = trace.adaptivePre * trace.adaptiveDiagnosticFactor;
                        return trace.adaptiveDiagnosticFactor;
                    }));
        }
        else {
            invoke(defence, "addDealtModifier", modifier("POST_MULTIPLICATIVE", AFTER_ADAPTIVE,
                    "calibration_adaptive_observation", value -> {
                        trace.adaptivePre = trace.dementorDiagnosticPost;
                        trace.adaptiveNativeFactor = value;
                        trace.adaptiveDiagnosticFactor = value;
                        trace.adaptiveNativePost = trace.adaptivePre * value;
                        trace.adaptiveDiagnosticPost = trace.adaptiveNativePost;
                        return value;
                    }));
        }
    }

    private static Object modifier(String orderName, int priority, String path,
            java.util.function.DoubleUnaryOperator operation) throws ReflectiveOperationException {
        Class<?> modifierType = Class.forName(DAMAGE_MODIFIER);
        @SuppressWarnings({"rawtypes", "unchecked"})
        Object order = Enum.valueOf((Class<? extends Enum>) Class.forName(DAMAGE_ORDER), orderName);
        ResourceLocation id = ResourceLocation.fromNamespaceAndPath("tno_tensura_compat", path);
        return Proxy.newProxyInstance(modifierType.getClassLoader(), new Class<?>[]{modifierType},
                (proxy, method, args) -> {
                    if (method.getDeclaringClass() == Object.class) {
                        return objectMethod(proxy, method, args, id.toString());
                    }
                    return switch (method.getName()) {
                        case "id" -> id;
                        case "priority" -> priority;
                        case "order" -> order;
                        case "modify" -> (float) operation.applyAsDouble(((Number) args[0]).doubleValue());
                        case "info" -> id + "=" + args[0];
                        default -> null;
                    };
                });
    }

    private static Object objectMethod(Object proxy, Method method, Object[] args, String label) {
        return switch (method.getName()) {
            case "toString" -> label;
            case "hashCode" -> System.identityHashCode(proxy);
            case "equals" -> proxy == args[0];
            default -> null;
        };
    }

    private static double genericHealthMultiplier(Frame frame) throws ReflectiveOperationException {
        int level = ((Number) invoke(frame.existingL2Capability(), "getLevel")).intValue();
        Object config = invoke(frame.existingL2Capability(), "getConfigCache", frame.target());
        double entityScale = ((Number) readField(config, "healthScale")).doubleValue();
        return 1.0D + level * serverDouble("healthFactor") * entityScale;
    }

    private static int adaptiveCount(Frame frame, String msgId) throws ReflectiveOperationException {
        Object raw = readField(frame.existingL2Capability(), "data");
        if (!(raw instanceof Map<?, ?> data)) return 0;
        for (Map.Entry<?, ?> entry : data.entrySet()) {
            if (!traitId(entry.getKey()).equals("l2hostility:adaptive")) continue;
            Object counts = readField(entry.getValue(), "adaption");
            if (counts instanceof Map<?, ?> map && map.get(msgId) instanceof Number count) {
                return count.intValue();
            }
        }
        return 0;
    }

    private static double serverDouble(String name) throws ReflectiveOperationException {
        Object holder = readField(staticField(L2_CONFIG, "SERVER"), name);
        return ((Number) invoke(holder, "get")).doubleValue();
    }

    private static double numberValue(Object value) {
        if (value instanceof Number number) return number.doubleValue();
        throw new IllegalArgumentException("expected number, got " + value);
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

    private static String traitId(Object trait) {
        try {
            Object id = invoke(invoke(trait, "getEntry"), "getId");
            if (id instanceof ResourceLocation resource) return resource.toString();
        }
        catch (ReflectiveOperationException ignored) {
        }
        return String.valueOf(trait);
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
            Parameters parameters,
            Trace trace
    ) {
        public boolean hasTrait(String id) {
            return relevantTraits.getOrDefault(id, 0) > 0;
        }
    }

    public static final class Trace {
        private String sourceMsgId = "";
        private double damageOriginal;
        private double genericHealthMultiplier = 1.0D;
        private double genericPre;
        private double genericPost;
        private boolean dementorApplied;
        private double dementorPre;
        private double dementorNativePost;
        private double dementorDiagnosticPost;
        private boolean adaptiveApplied;
        private int adaptiveRank;
        private int adaptiveMemoryCapacity;
        private int adaptiveCount;
        private double configuredAdaptFactor = 1.0D;
        private double adaptivePre;
        private double adaptiveNativeFactor = 1.0D;
        private double adaptiveDiagnosticFactor = 1.0D;
        private double adaptiveNativePost;
        private double adaptiveDiagnosticPost;

        public Snapshot snapshot() {
            return new Snapshot(sourceMsgId, damageOriginal, genericHealthMultiplier, genericPre, genericPost,
                    dementorApplied, dementorPre, dementorNativePost, dementorDiagnosticPost,
                    adaptiveApplied, adaptiveRank, adaptiveMemoryCapacity, adaptiveCount, configuredAdaptFactor,
                    adaptivePre, adaptiveNativeFactor, adaptiveDiagnosticFactor,
                    adaptiveNativePost, adaptiveDiagnosticPost);
        }
    }

    public record Snapshot(
            String sourceMsgId,
            double damageOriginal,
            double genericHealthMultiplier,
            double genericPre,
            double genericPost,
            boolean dementorApplied,
            double dementorPre,
            double dementorNativePost,
            double dementorDiagnosticPost,
            boolean adaptiveApplied,
            int adaptiveRank,
            int adaptiveMemoryCapacity,
            int adaptiveCount,
            double configuredAdaptFactor,
            double adaptivePre,
            double adaptiveNativeFactor,
            double adaptiveDiagnosticFactor,
            double adaptiveNativePost,
            double adaptiveDiagnosticPost
    ) {
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

        public Snapshot snapshot() {
            return frame.trace().snapshot();
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
