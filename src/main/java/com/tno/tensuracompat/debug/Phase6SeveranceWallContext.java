package com.tno.tensuracompat.debug;

import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.AbstractArrow;
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
 * Development-only, observation-only context for the R3 Severance physical-wall
 * decomposition. Identity modifiers expose L2's native Dementor and Adaptive
 * boundaries without changing either result.
 */
public final class Phase6SeveranceWallContext {
    private static final String L2_MISCS = "dev.xkmc.l2hostility.init.registrate.LHMiscs";
    private static final String L2_CONFIG = "dev.xkmc.l2hostility.init.data.LHConfig";
    private static final String ATTACK_HANDLER = "dev.xkmc.l2damagetracker.contents.attack.AttackEventHandler";
    private static final String ATTACK_LISTENER = "dev.xkmc.l2damagetracker.contents.attack.AttackListener";
    private static final String DAMAGE_MODIFIER = "dev.xkmc.l2damagetracker.contents.attack.DamageModifier";
    private static final String DAMAGE_ORDER = "dev.xkmc.l2damagetracker.contents.attack.DamageModifier$Order";
    private static final int LISTENER_PRIORITY = 4502;
    private static final int BEFORE_DEMENTOR = 7435;
    private static final int AFTER_DEMENTOR = 7437;
    private static final int AFTER_ADAPTIVE = 7437;
    private static final ThreadLocal<Deque<Frame>> FRAMES = ThreadLocal.withInitial(ArrayDeque::new);
    private static boolean listenerRegistered;
    private static Object registeredListener;

    private Phase6SeveranceWallContext() {
    }

    public static boolean enabled() {
        return !FMLEnvironment.production
                && Boolean.getBoolean("tno.phase6.calibration")
                && System.getProperty("tno.phase6.calibrationMode", "").equals("severance_wall");
    }

    public static synchronized void registerL2Listener() {
        if (!enabled() || listenerRegistered || !ModList.get().isLoaded("l2hostility")) return;
        try {
            Class<?> listenerType = Class.forName(ATTACK_LISTENER);
            Object listener = Proxy.newProxyInstance(listenerType.getClassLoader(), new Class<?>[]{listenerType},
                    (proxy, method, args) -> {
                        if (method.getDeclaringClass() == Object.class) {
                            return objectMethod(proxy, method, args, "TNO Phase 6 Severance wall observer");
                        }
                        if (method.getName().equals("onDamage") && args != null && args.length == 1) {
                            addObservationModifiers(args[0]);
                        }
                        return method.getReturnType() == boolean.class ? false : null;
                    });
            Class<?> handler = Class.forName(ATTACK_HANDLER);
            handler.getMethod("register", int.class, listenerType)
                    .invoke(null, LISTENER_PRIORITY, listener);
            registeredListener = listener;
            listenerRegistered = true;
        }
        catch (ReflectiveOperationException exception) {
            throw new IllegalStateException("could not register development-only Severance wall observer", exception);
        }
    }

    public static Optional<Scope> open(
            AbstractArrow arrow,
            LivingEntity target,
            DamageSource source,
            double combinedPhysicalAmount
    ) {
        if (!enabled() || arrow == null || target == null || source == null
                || !target.getTags().contains("tno_phase6_severance_wall_target")
                || !source.getMsgId().equals("arrow") || !ModList.get().isLoaded("l2hostility")) {
            return Optional.empty();
        }
        try {
            Object type = invoke(staticField(L2_MISCS, "MOB"), "type");
            Object result = invoke(type, "getExisting", target);
            Object cap = result instanceof Optional<?> optional ? optional.orElse(null) : result;
            if (cap == null || !booleanValue(invoke(cap, "isInitialized"))) return Optional.empty();
            Frame frame = new Frame(arrow, target, cap, relevantTraits(cap), combinedPhysicalAmount, new Trace());
            FRAMES.get().push(frame);
            return Optional.of(new Scope(Thread.currentThread(), frame));
        }
        catch (ReflectiveOperationException exception) {
            return Optional.empty();
        }
    }

    public static void captureWoundAttempt(Entity target, float callbackDamage) {
        Frame frame = current().orElse(null);
        if (frame == null || frame.target() != target) return;
        frame.trace().woundAttemptCount++;
        frame.trace().woundCallbackDamage += callbackDamage;
    }

    private static Optional<Frame> current() {
        Deque<Frame> stack = FRAMES.get();
        return stack.isEmpty() ? Optional.empty() : Optional.of(stack.peek());
    }

    private static void addObservationModifiers(Object defence) throws ReflectiveOperationException {
        Frame frame = current().orElse(null);
        if (frame == null || invoke(defence, "getTarget") != frame.target()) return;
        Object source = invoke(defence, "getSource");
        if (invoke(source, "getDirectEntity") != frame.arrow()) return;
        String msgId = String.valueOf(invoke(source, "getMsgId"));
        if (!msgId.equals("arrow")) return;

        Trace trace = frame.trace();
        trace.sourceMsgId = msgId;
        trace.damageOriginal = numberValue(invoke(defence, "getDamageOriginal"));
        trace.dementorApplied = frame.hasTrait("l2hostility:dementor");
        trace.adaptiveApplied = frame.hasTrait("l2hostility:adaptive");
        invoke(defence, "addDealtModifier", modifier("PRE_NONLINEAR", BEFORE_DEMENTOR,
                "severance_wall_before_dementor", value -> {
                    trace.dementorInput = value;
                    return value;
                }));
        invoke(defence, "addDealtModifier", modifier("PRE_NONLINEAR", AFTER_DEMENTOR,
                "severance_wall_after_dementor", value -> {
                    trace.dementorOutput = value;
                    return value;
                }));

        if (trace.adaptiveApplied) {
            trace.adaptiveRank = frame.relevantTraits().getOrDefault("l2hostility:adaptive", 0);
            trace.adaptiveMemoryCapacity = trace.adaptiveRank;
            trace.adaptiveCount = adaptiveCount(frame, msgId);
            trace.configuredAdaptFactor = serverDouble("adaptFactor");
        }
        invoke(defence, "addDealtModifier", modifier("POST_MULTIPLICATIVE", AFTER_ADAPTIVE,
                "severance_wall_after_adaptive", value -> {
                    trace.adaptiveInput = trace.dementorOutput;
                    trace.adaptiveFactor = value;
                    trace.adaptiveResult = trace.adaptiveInput * value;
                    return value;
                }));
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

    private static Map<String, Integer> relevantTraits(Object cap) throws ReflectiveOperationException {
        Object value = readField(cap, "traits");
        if (!(value instanceof Map<?, ?> map)) return Map.of();
        Map<String, Integer> result = new LinkedHashMap<>();
        for (Map.Entry<?, ?> entry : map.entrySet()) {
            String id = traitId(entry.getKey());
            if (id.equals("l2hostility:adaptive") || id.equals("l2hostility:dementor")
                    || id.equals("l2hostility:regenerate") || id.equals("l2hostility:tank")) {
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

    private static double serverDouble(String name) throws ReflectiveOperationException {
        Object holder = readField(staticField(L2_CONFIG, "SERVER"), name);
        return ((Number) invoke(holder, "get")).doubleValue();
    }

    private static Object objectMethod(Object proxy, Method method, Object[] args, String label) {
        return switch (method.getName()) {
            case "toString" -> label;
            case "hashCode" -> System.identityHashCode(proxy);
            case "equals" -> proxy == args[0];
            default -> null;
        };
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
        for (Method method : type.getMethods()) {
            if (method.getName().equals(name) && method.getParameterCount() == args.length) {
                method.setAccessible(true);
                return method.invoke(Modifier.isStatic(method.getModifiers()) ? null : targetOrClass, args);
            }
        }
        throw new NoSuchMethodException(type.getName() + "#" + name);
    }

    private static double numberValue(Object value) {
        if (value instanceof Number number) return number.doubleValue();
        throw new IllegalArgumentException("expected number, got " + value);
    }

    private static boolean booleanValue(Object value) {
        return value instanceof Boolean bool && bool;
    }

    private record Frame(
            AbstractArrow arrow,
            LivingEntity target,
            Object existingL2Capability,
            Map<String, Integer> relevantTraits,
            double combinedPhysicalAmount,
            Trace trace
    ) {
        boolean hasTrait(String id) {
            return relevantTraits.getOrDefault(id, 0) > 0;
        }
    }

    private static final class Trace {
        String sourceMsgId = "";
        double damageOriginal;
        double dementorInput;
        double dementorOutput;
        boolean dementorApplied;
        double adaptiveInput;
        double adaptiveFactor = 1.0D;
        double adaptiveResult;
        boolean adaptiveApplied;
        int adaptiveRank;
        int adaptiveMemoryCapacity;
        int adaptiveCount;
        double configuredAdaptFactor = 1.0D;
        boolean hurtReturned;
        int woundAttemptCount;
        double woundCallbackDamage;
    }

    public static final class Scope implements AutoCloseable {
        private final Thread owner;
        private final Frame frame;
        private boolean closed;

        private Scope(Thread owner, Frame frame) {
            this.owner = owner;
            this.frame = frame;
        }

        public void recordHurtResult(boolean result) {
            frame.trace().hurtReturned = result;
        }

        public Snapshot snapshot() {
            Trace trace = frame.trace();
            return new Snapshot(
                    frame.combinedPhysicalAmount(), trace.sourceMsgId, trace.damageOriginal,
                    frame.relevantTraits().getOrDefault("l2hostility:tank", 0),
                    trace.dementorApplied, trace.dementorInput, trace.dementorOutput,
                    trace.adaptiveApplied, trace.adaptiveRank, trace.adaptiveMemoryCapacity,
                    trace.adaptiveCount, trace.configuredAdaptFactor, trace.adaptiveInput,
                    trace.adaptiveFactor, trace.adaptiveResult, trace.hurtReturned,
                    trace.woundAttemptCount, trace.woundCallbackDamage);
        }

        @Override
        public void close() {
            if (closed) return;
            if (Thread.currentThread() != owner) {
                throw new IllegalStateException("Severance wall scope closed on a different thread");
            }
            Deque<Frame> stack = FRAMES.get();
            if (stack.isEmpty() || stack.pop() != frame) {
                throw new IllegalStateException("Severance wall scope stack mismatch");
            }
            if (stack.isEmpty()) FRAMES.remove();
            closed = true;
        }
    }

    public record Snapshot(
            double combinedPhysicalAmount,
            String sourceMsgId,
            double damageOriginal,
            int tankRank,
            boolean dementorApplied,
            double dementorInput,
            double dementorOutput,
            boolean adaptiveApplied,
            int adaptiveRank,
            int adaptiveMemoryCapacity,
            int adaptiveCount,
            double configuredAdaptFactor,
            double adaptiveInput,
            double adaptiveFactor,
            double adaptiveResult,
            boolean hurtReturned,
            int woundAttemptCount,
            double woundCallbackDamage
    ) {
    }
}
