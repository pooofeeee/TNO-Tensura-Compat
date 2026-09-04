package com.tno.tensuracompat.core.endgame;

import com.tno.tensuracompat.TNOTensuraCompat;
import com.tno.tensuracompat.core.stage.ScalableFamily;
import net.minecraft.resources.ResourceLocation;
import net.neoforged.fml.ModList;

import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.lang.reflect.Proxy;

/** Optional runtime bridge into L2's verified damage-modifier pipeline. */
public final class MagicHolyEndgameL2Bridge {
    private static final String ATTACK_HANDLER = "dev.xkmc.l2damagetracker.contents.attack.AttackEventHandler";
    private static final String ATTACK_LISTENER = "dev.xkmc.l2damagetracker.contents.attack.AttackListener";
    private static final String DAMAGE_MODIFIER = "dev.xkmc.l2damagetracker.contents.attack.DamageModifier";
    private static final String DAMAGE_ORDER = "dev.xkmc.l2damagetracker.contents.attack.DamageModifier$Order";
    private static final int LISTENER_PRIORITY = 4501;
    private static final int BEFORE_DEMENTOR = 7435;
    private static final int AFTER_DEMENTOR = 7437;
    private static boolean registrationAttempted;
    private static Object registeredListener;

    private MagicHolyEndgameL2Bridge() {
    }

    /** Registers only when L2 is present; resolution failure leaves ordinary Phase 6 behavior intact. */
    public static synchronized void registerIfAvailable() {
        if (registrationAttempted || !ModList.get().isLoaded("l2hostility")) return;
        registrationAttempted = true;
        try {
            Class<?> listenerType = Class.forName(ATTACK_LISTENER);
            Object listener = Proxy.newProxyInstance(listenerType.getClassLoader(), new Class<?>[]{listenerType},
                    (proxy, method, args) -> {
                        if (method.getDeclaringClass() == Object.class) {
                            return objectMethod(proxy, method, args,
                                    "TNO Magic/Holy production L2 listener");
                        }
                        if (method.getName().equals("onDamage") && args != null && args.length == 1) {
                            tryAddProductionModifiers(args[0]);
                        }
                        return method.getReturnType() == boolean.class ? false : null;
                    });
            Class<?> handler = Class.forName(ATTACK_HANDLER);
            handler.getMethod("register", int.class, listenerType)
                    .invoke(null, LISTENER_PRIORITY, listener);
            registeredListener = listener;
        }
        catch (ReflectiveOperationException | RuntimeException | LinkageError exception) {
            registeredListener = null;
            TNOTensuraCompat.LOGGER.warn(
                    "L2 Hostility production bridge unavailable; preserving ordinary Phase 6 behavior", exception);
        }
    }

    private static void tryAddProductionModifiers(Object defence) {
        MagicHolyEndgameContext.Frame frame = MagicHolyEndgameContext.current().orElse(null);
        if (frame == null) return;
        try {
            if (invoke(defence, "getTarget") != frame.target()) return;
            Object source = invoke(defence, "getSource");
            String msgId = String.valueOf(invoke(source, "getMsgId"));
            if (!msgId.equals(expectedMsgId(frame.family()))) return;

            double normalization = MagicHolyEndgameMath.genericNormalization(
                    frame.parameters(), frame.l2Target().genericHealthMultiplier());
            double[] beforeDementor = {Double.NaN};
            invoke(defence, "addDealtModifier", modifier("PRE_NONLINEAR", BEFORE_DEMENTOR,
                    "magic_holy_generic_health", value -> {
                        beforeDementor[0] = value * normalization;
                        return beforeDementor[0];
                    }));
            if (frame.l2Target().hasTrait("l2hostility:dementor")) {
                invoke(defence, "addDealtModifier", modifier("PRE_NONLINEAR", AFTER_DEMENTOR,
                        "magic_holy_dementor_recovery", value -> MagicHolyEndgameMath.negotiateDementor(
                                true, beforeDementor[0], value, frame.parameters().dementorRecovery())));
            }
        }
        catch (ReflectiveOperationException | RuntimeException ignored) {
            // The optional bridge is deliberately fail-closed for this event.
        }
    }

    private static String expectedMsgId(ScalableFamily family) {
        return family == ScalableFamily.MAGIC_WEAPON ? "tensura.magic" : "tensura.holy_damage";
    }

    private static Object modifier(String orderName, int priority, String path,
            java.util.function.DoubleUnaryOperator operation) throws ReflectiveOperationException {
        Class<?> modifierType = Class.forName(DAMAGE_MODIFIER);
        @SuppressWarnings({"rawtypes", "unchecked"})
        Object order = Enum.valueOf((Class<? extends Enum>) Class.forName(DAMAGE_ORDER), orderName);
        ResourceLocation id = ResourceLocation.fromNamespaceAndPath(TNOTensuraCompat.MOD_ID, path);
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
}
