package com.tno.tensuracompat.core.endgame;

import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.LivingEntity;
import net.neoforged.fml.ModList;

import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Optional;

/** Reflection-only, fail-closed view of an already-existing L2 Hostility mob attachment. */
final class L2HostilityTargetAdapter {
    private static final String L2_MISCS = "dev.xkmc.l2hostility.init.registrate.LHMiscs";
    private static final String L2_CONFIG = "dev.xkmc.l2hostility.init.data.LHConfig";

    private L2HostilityTargetAdapter() {
    }

    static Optional<TargetView> existingInitialized(LivingEntity target) {
        if (target == null || target.isRemoved() || !target.isAlive()
                || !ModList.get().isLoaded("l2hostility")) {
            return Optional.empty();
        }
        try {
            Object attachmentType = invoke(staticField(L2_MISCS, "MOB"), "type");
            Object lookup = invoke(attachmentType, "getExisting", target);
            Object capability = lookup instanceof Optional<?> optional ? optional.orElse(null) : lookup;
            if (capability == null || !booleanValue(invoke(capability, "isInitialized"))) {
                return Optional.empty();
            }

            int level = ((Number) invoke(capability, "getLevel")).intValue();
            Object entityConfig = invoke(capability, "getConfigCache", target);
            if (entityConfig == null) return Optional.empty();
            double entityHealthScale = ((Number) readField(entityConfig, "healthScale")).doubleValue();
            double healthFactor = serverDouble("healthFactor");
            boolean exponentialHealth = serverBoolean("exponentialHealth");
            double healthMultiplier = L2HealthScaling.nominalMultiplier(
                    level, healthFactor, entityHealthScale, exponentialHealth);
            return Optional.of(new TargetView(capability, level, healthMultiplier, relevantTraits(capability)));
        }
        catch (ReflectiveOperationException | RuntimeException ignored) {
            return Optional.empty();
        }
    }

    private static double serverDouble(String name) throws ReflectiveOperationException {
        Object holder = readField(staticField(L2_CONFIG, "SERVER"), name);
        return ((Number) invoke(holder, "get")).doubleValue();
    }

    private static boolean serverBoolean(String name) throws ReflectiveOperationException {
        Object holder = readField(staticField(L2_CONFIG, "SERVER"), name);
        return booleanValue(invoke(holder, "get"));
    }

    private static Map<String, Integer> relevantTraits(Object capability) throws ReflectiveOperationException {
        Object value = readField(capability, "traits");
        if (!(value instanceof Map<?, ?> map)) return Map.of();
        Map<String, Integer> result = new LinkedHashMap<>();
        for (Map.Entry<?, ?> entry : map.entrySet()) {
            String id = traitId(entry.getKey());
            if ((id.equals("l2hostility:adaptive") || id.equals("l2hostility:dementor"))
                    && entry.getValue() instanceof Number rank && rank.intValue() > 0) {
                result.put(id, rank.intValue());
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

    record TargetView(Object existingCapability, int level, double genericHealthMultiplier,
                      Map<String, Integer> relevantTraits) {
        boolean hasTrait(String id) {
            return relevantTraits.getOrDefault(id, 0) > 0;
        }
    }
}
