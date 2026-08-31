package com.tno.tensuracompat.core.stage;

import io.github.manasmods.tensura.damage.TensuraDamageHelper;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemStack;

import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.util.List;
import java.util.Optional;

/** Applies recovery before Tensura's matching Resistance and before downstream L2 processing. */
public final class MatchingResistanceRecovery {
    private MatchingResistanceRecovery() {
    }

    public static float apply(
            ItemStack gear,
            ScalableFamily family,
            LivingEntity target,
            DamageSource source,
            float preMatchingResistance
    ) {
        Optional<Stage> stage = ProductionStageScaling.stage(gear);
        return stage.isEmpty()
                ? preMatchingResistance
                : apply(stage.get(), family, target, source, preMatchingResistance);
    }

    public static float apply(
            Stage stage,
            ScalableFamily family,
            LivingEntity target,
            DamageSource source,
            float preMatchingResistance
    ) {
        double penetration = ResistanceRecoveryCurve.penetration(stage);
        if (penetration == 0.0D || preMatchingResistance <= 0.0F) {
            return preMatchingResistance;
        }

        List<String> resistances = matchingResistances(family, source);
        if (resistances.isEmpty()
                || !hasActive(target, resistances)
                || hasActiveMatchingNullification(target, family, source)
                || resistances.stream().anyMatch(skill -> isResistanceBypass(skill, source))) {
            return preMatchingResistance;
        }

        double postResistance = ResistanceRecoveryCurve.nativePostResistance(
                preMatchingResistance,
                target.getHealth(),
                resistanceConfig("hpDamageBypassResistance"),
                resistanceConfig("resistanceDamageMultiplier")
        );
        double recovered = ResistanceRecoveryCurve.recover(
                preMatchingResistance, postResistance, stage);

        setResistanceBypassLevel(source, Math.max(1.0F, getResistanceBypassLevel(source)));
        return (float) recovered;
    }

    private static boolean hasActiveMatchingNullification(
            LivingEntity target,
            ScalableFamily family,
            DamageSource source
    ) {
        return !isNullificationDisabled(target)
                && hasActive(target, matchingNullifications(family, source));
    }

    private static boolean hasActive(LivingEntity target, List<String> skillFields) {
        return skillFields.stream().anyMatch(field -> isSkillToggled(target, field));
    }

    private static List<String> matchingResistances(
            ScalableFamily family,
            DamageSource source
    ) {
        return switch (family) {
            case MAGIC_WEAPON -> List.of("MAGIC_RESISTANCE");
            case HOLY_WEAPON -> List.of("HOLY_ATTACK_RESISTANCE");
            case SOUL_EATER -> List.of("SPIRITUAL_ATTACK_RESISTANCE");
            case ELEMENTAL_SLOTTING -> elementalResistances(source);
            case ENERGY_STEAL, SEVERANCE -> List.of();
        };
    }

    private static List<String> matchingNullifications(
            ScalableFamily family,
            DamageSource source
    ) {
        return switch (family) {
            case MAGIC_WEAPON -> List.of("MAGIC_NULLIFICATION");
            case HOLY_WEAPON -> List.of("HOLY_ATTACK_NULLIFICATION");
            case SOUL_EATER -> List.of("SPIRITUAL_ATTACK_NULLIFICATION");
            case ELEMENTAL_SLOTTING -> elementalNullifications(source);
            case ENERGY_STEAL, SEVERANCE -> List.of();
        };
    }

    private static List<String> elementalResistances(DamageSource source) {
        if (TensuraDamageHelper.isEarthDamage(source)) {
            return List.of("EARTH_ATTACK_RESISTANCE", "SPIRITUAL_ATTACK_RESISTANCE");
        }
        if (TensuraDamageHelper.isFireDamage(source)) {
            return List.of("FLAME_ATTACK_RESISTANCE", "SPIRITUAL_ATTACK_RESISTANCE");
        }
        if (TensuraDamageHelper.isSpatialDamage(source)) {
            return List.of("SPATIAL_ATTACK_RESISTANCE", "SPIRITUAL_ATTACK_RESISTANCE");
        }
        if (TensuraDamageHelper.isWaterDamage(source)) {
            return List.of("WATER_ATTACK_RESISTANCE", "SPIRITUAL_ATTACK_RESISTANCE");
        }
        if (TensuraDamageHelper.isWindDamage(source)) {
            return List.of("WIND_ATTACK_RESISTANCE", "SPIRITUAL_ATTACK_RESISTANCE");
        }
        return List.of();
    }

    private static List<String> elementalNullifications(DamageSource source) {
        if (TensuraDamageHelper.isEarthDamage(source)) {
            return List.of("EARTH_ATTACK_NULLIFICATION", "SPIRITUAL_ATTACK_NULLIFICATION");
        }
        if (TensuraDamageHelper.isFireDamage(source)) {
            return List.of("FLAME_ATTACK_NULLIFICATION", "SPIRITUAL_ATTACK_NULLIFICATION");
        }
        if (TensuraDamageHelper.isSpatialDamage(source)) {
            return List.of("SPATIAL_ATTACK_NULLIFICATION", "SPIRITUAL_ATTACK_NULLIFICATION");
        }
        if (TensuraDamageHelper.isWaterDamage(source)) {
            return List.of("WATER_ATTACK_NULLIFICATION", "SPIRITUAL_ATTACK_NULLIFICATION");
        }
        if (TensuraDamageHelper.isWindDamage(source)) {
            return List.of("WIND_ATTACK_NULLIFICATION", "SPIRITUAL_ATTACK_NULLIFICATION");
        }
        return List.of();
    }

    /* ManasCore's API classes are nested inside its published Jar-in-Jar module,
       so the narrow runtime calls remain reflective while all Tensura semantics
       and field names are verified against the installed 2.0.1.1 artifact. */
    private static Object skill(String fieldName) {
        try {
            Class<?> registry = Class.forName("io.github.manasmods.tensura.registry.skill.ResistanceSkills");
            Object supplier = registry.getField(fieldName).get(null);
            return supplier.getClass().getMethod("get").invoke(supplier);
        } catch (ReflectiveOperationException exception) {
            throw reflectionFailure("resolve Tensura resistance " + fieldName, exception);
        }
    }

    private static double resistanceConfig(String fieldName) {
        try {
            Class<?> resistSkill = Class.forName(
                    "io.github.manasmods.tensura.ability.skill.resist.ResistSkill");
            Object config = resistSkill.getField("CONFIG").get(null);
            return config.getClass().getField(fieldName).getDouble(config);
        } catch (ReflectiveOperationException exception) {
            throw reflectionFailure("read Tensura Resistance config " + fieldName, exception);
        }
    }

    private static boolean isNullificationDisabled(LivingEntity target) {
        try {
            Class<?> resistSkill = Class.forName(
                    "io.github.manasmods.tensura.ability.skill.resist.ResistSkill");
            for (Method method : resistSkill.getMethods()) {
                if (method.getName().equals("isNullificationDisabled")
                        && method.getParameterCount() == 1) {
                    return (boolean) method.invoke(null, target.level());
                }
            }
            throw new NoSuchMethodException("ResistSkill.isNullificationDisabled(Level)");
        } catch (ReflectiveOperationException exception) {
            throw reflectionFailure("query native Nullification rule", exception);
        }
    }

    private static boolean isSkillToggled(LivingEntity target, String fieldName) {
        Object skill = skill(fieldName);
        try {
            Class<?> skillUtils = Class.forName("io.github.manasmods.tensura.ability.SkillUtils");
            for (Method method : skillUtils.getMethods()) {
                if (method.getName().equals("isSkillToggled") && method.getParameterCount() == 2) {
                    return (boolean) method.invoke(null, target, skill);
                }
            }
            throw new NoSuchMethodException("SkillUtils.isSkillToggled(LivingEntity, ManasSkill)");
        } catch (ReflectiveOperationException exception) {
            throw reflectionFailure("query Tensura resistance " + fieldName, exception);
        }
    }

    private static boolean isResistanceBypass(String fieldName, DamageSource source) {
        Object skill = skill(fieldName);
        try {
            return (boolean) skill.getClass()
                    .getMethod("isResistanceBypass", DamageSource.class)
                    .invoke(skill, source);
        } catch (ReflectiveOperationException exception) {
            throw reflectionFailure("query native Resistance bypass", exception);
        }
    }

    private static float getResistanceBypassLevel(DamageSource source) {
        try {
            return (float) source.getClass()
                    .getMethod("tensura$getResistanceBypassLevel")
                    .invoke(source);
        } catch (ReflectiveOperationException exception) {
            throw reflectionFailure("read native Resistance bypass level", exception);
        }
    }

    private static void setResistanceBypassLevel(DamageSource source, float level) {
        try {
            source.getClass()
                    .getMethod("tensura$setResistanceBypassLevel", float.class)
                    .invoke(source, level);
        } catch (ReflectiveOperationException exception) {
            throw reflectionFailure("set native Resistance bypass level", exception);
        }
    }

    private static IllegalStateException reflectionFailure(String action, ReflectiveOperationException exception) {
        Throwable cause = exception instanceof InvocationTargetException && exception.getCause() != null
                ? exception.getCause()
                : exception;
        return new IllegalStateException("Could not " + action + " through Tensura 2.0.1.1", cause);
    }
}
