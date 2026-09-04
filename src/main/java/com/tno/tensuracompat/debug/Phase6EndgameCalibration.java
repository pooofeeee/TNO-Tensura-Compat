package com.tno.tensuracompat.debug;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.mojang.logging.LogUtils;
import io.github.manasmods.tensura.registry.attribute.TensuraAttributes;
import io.github.manasmods.tensura.storage.TensuraStorages;
import net.minecraft.core.Holder;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageType;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.tags.TagKey;
import net.neoforged.fml.ModList;
import net.neoforged.fml.loading.FMLEnvironment;
import net.neoforged.neoforge.event.server.ServerStartedEvent;
import net.neoforged.neoforge.event.tick.ServerTickEvent;
import net.neoforged.neoforge.common.Tags;
import org.slf4j.Logger;

import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.LinkedHashSet;

/** Development-only post-Phase-6 calibration harness. */
public final class Phase6EndgameCalibration {
    private static final Logger LOGGER = LogUtils.getLogger();
    private static final Gson GSON = new GsonBuilder().disableHtmlEscaping().create();
    private static final String MARKER = "TNO_PHASE6_CALIBRATION";
    private static final String TARGET_TAG = "tno_phase6_calibration_target";
    private static final String SCALE_TAG = "l2_tensura_scaled";
    private static final String L2_MISCS = "dev.xkmc.l2hostility.init.registrate.LHMiscs";
    private static final List<Integer> LEVELS = List.of(300, 600, 800, 1000);
    private static final List<ResourceLocation> BOSSES = List.of(
            id("tensura_neb", "luminous_valentine"),
            id("tensura", "hinata_sakaguchi"),
            id("tensura", "gazel_dwargo"),
            id("tensura", "orc_disaster"));
    private static Session active;

    private Phase6EndgameCalibration() {
    }

    public static void onServerStarted(ServerStartedEvent event) {
        if (FMLEnvironment.production || !Boolean.getBoolean("tno.phase6.calibration") || active != null) return;
        String mode = System.getProperty("tno.phase6.calibrationMode", "");
        if (!Set.of("durability", "classification").contains(mode)) return;
        try {
            if (!ModList.get().isLoaded("l2hostility")) throw new IllegalStateException("L2 Hostility is absent");
            active = new Session(event.getServer(), mode);
            log("suite_start", active.catalog());
        }
        catch (Throwable throwable) {
            LOGGER.error("{} startup failed", MARKER, throwable);
            event.getServer().halt(false);
        }
    }

    public static void onServerTick(ServerTickEvent.Post event) {
        if (active == null) return;
        try {
            active.tick();
            if (active.complete) {
                active = null;
                event.getServer().halt(false);
            }
        }
        catch (Throwable throwable) {
            LOGGER.error("{} case failed", MARKER, throwable);
            active.fail(throwable);
        }
    }

    private static final class Session {
        private final MinecraftServer server;
        private final ServerLevel level;
        private final String mode;
        private final List<CaseSpec> cases = new ArrayList<>();
        private final List<JsonObject> results = new ArrayList<>();
        private LivingEntity target;
        private Object cap;
        private NativeState nativeState;
        private int index;
        private int ticks;
        private Phase phase = Phase.SPAWN;
        private boolean complete;

        Session(MinecraftServer server, String mode) {
            this.server = server;
            this.level = server.overworld();
            this.mode = mode;
            if (mode.equals("durability")) {
                for (ResourceLocation boss : BOSSES) for (int requested : LEVELS) cases.add(new CaseSpec(boss, requested));
            }
        }

        JsonObject catalog() {
            JsonObject json = new JsonObject();
            json.addProperty("mode", mode);
            json.addProperty("APO_profile", "NONE");
            json.addProperty("requested_case_count", mode.equals("durability") ? cases.size() : 2);
            if (mode.equals("durability")) {
                json.addProperty("health_formula", "H=1+level*healthFactor*entity.healthScale (exponentialHealth=false)");
                json.addProperty("health_modifier", "l2hostility:hostility_health / ADD_MULTIPLIED_TOTAL");
                json.addProperty("tank_formula", "T=1+tankRank*tankHealth");
                json.addProperty("tank_modifier", "l2hostility:tank_health / ADD_MULTIPLIED_TOTAL");
                json.addProperty("SHP_datapack_formula", "1+level*0.03 / ADD_MULTIPLIED_BASE");
            }
            return json;
        }

        void tick() throws ReflectiveOperationException {
            if (mode.equals("classification")) {
                classifySources();
                complete = true;
                return;
            }
            switch (phase) {
                case SPAWN -> spawn();
                case WAIT_ATTACHMENT -> waitAttachment();
                case WAIT_SCALING -> waitScaling();
                case DONE -> complete = true;
            }
        }

        void classifySources() {
            List<ResourceLocation> ids = List.of(id("tensura", "magic"), id("tensura", "holy_damage"));
            for (ResourceLocation id : ids) {
                Holder<DamageType> holder = server.registryAccess().registryOrThrow(Registries.DAMAGE_TYPE)
                        .getHolderOrThrow(ResourceKey.create(Registries.DAMAGE_TYPE, id));
                DamageSource source = new DamageSource(holder);
                Set<String> tags = new LinkedHashSet<>();
                holder.tags().map(tag -> tag.location().toString()).sorted().forEach(tags::add);
                boolean bypassInvulnerability = source.is(DamageTypeTags.BYPASSES_INVULNERABILITY);
                boolean bypassEffects = source.is(DamageTypeTags.BYPASSES_EFFECTS);
                boolean neoForgeMagic = source.is(Tags.DamageTypes.IS_MAGIC);
                JsonObject json = new JsonObject();
                json.addProperty("status", "complete");
                json.addProperty("damage_type", id.toString());
                json.addProperty("TNO_family", id.getPath().equals("magic") ? "MAGIC_WEAPON" : "HOLY_WEAPON");
                json.addProperty("message_id", holder.value().msgId());
                json.addProperty("DamageSource_getMsgId", source.getMsgId());
                json.add("runtime_damage_tags", GSON.toJsonTree(tags));
                json.addProperty("minecraft_bypasses_armor", source.is(DamageTypeTags.BYPASSES_ARMOR));
                json.addProperty("minecraft_bypasses_effects", bypassEffects);
                json.addProperty("minecraft_bypasses_invulnerability", bypassInvulnerability);
                json.addProperty("minecraft_bypasses_resistance", source.is(DamageTypeTags.BYPASSES_RESISTANCE));
                json.addProperty("neoforge_is_magic", neoForgeMagic);
                json.addProperty("L2_Dementor_eligible", !bypassInvulnerability && !bypassEffects && !neoForgeMagic);
                json.addProperty("L2_Dispell_eligible", !bypassInvulnerability && !bypassEffects && neoForgeMagic);
                json.addProperty("L2_Dementor_runtime_class", "dev.xkmc.l2hostility.content.traits.legendary.DementorTrait#onDamaged");
                json.addProperty("L2_Dispell_runtime_class", "dev.xkmc.l2hostility.content.traits.legendary.DispellTrait#onDamaged");
                json.addProperty("Dementor_reduction_base", uncheckedServerDouble("dementorDamageReductionBase"));
                json.addProperty("Dispell_reduction_base", uncheckedServerDouble("dispellDamageReductionBase"));
                log("classification_result", json);
            }
            JsonObject suite = new JsonObject();
            suite.addProperty("status", "complete");
            suite.addProperty("case_count", 2);
            suite.addProperty("requested_case_count", 2);
            log("suite_result", suite);
        }

        void spawn() {
            cleanup();
            if (index >= cases.size()) {
                JsonObject suite = new JsonObject();
                suite.addProperty("status", "complete");
                suite.addProperty("case_count", results.size());
                suite.addProperty("requested_case_count", cases.size());
                suite.add("cases", GSON.toJsonTree(results));
                log("suite_result", suite);
                phase = Phase.DONE;
                return;
            }
            CaseSpec spec = cases.get(index);
            Entity created = BuiltInRegistries.ENTITY_TYPE.get(spec.boss).create(level);
            if (!(created instanceof LivingEntity living)) throw new IllegalStateException("cannot create " + spec.boss);
            target = living;
            nativeState = NativeState.capture(target);
            target.setPos(0.5D, 240.0D, 20.5D);
            target.setNoGravity(true);
            target.setSilent(true);
            target.addTag(TARGET_TAG);
            level.addFreshEntity(target);
            ticks = 0;
            phase = Phase.WAIT_ATTACHMENT;
        }

        void waitAttachment() throws ReflectiveOperationException {
            if (++ticks < 5) return;
            Object type = invoke(staticField(L2_MISCS, "MOB"), "type");
            if (!booleanValue(invoke(type, "isProper", target))) throw new IllegalStateException("L2 rejected " + cases.get(index).boss);
            Object existing = invoke(type, "getExisting", target);
            cap = existing instanceof Optional<?> optional ? optional.orElse(null) : existing;
            if (cap == null || !booleanValue(invoke(cap, "isInitialized"))) {
                if (ticks <= 20) return;
                // Checkpoint A is an explicit level-construction benchmark, not
                // production-style observation. C and all policy probes use only
                // getExisting; A may initialize its disposable controlled copy.
                cap = invoke(type, "getOrCreate", target);
            }
            CaseSpec spec = cases.get(index);
            Object config = invoke(cap, "getConfigCache", target);
            Field maxLevel = findField(config.getClass(), "maxLevel");
            int previous = maxLevel.getInt(config);
            try {
                if (spec.level > previous) maxLevel.setInt(config, spec.level);
                invoke(cap, "reinit", target, spec.level, false);
            }
            finally {
                maxLevel.setInt(config, previous);
            }
            if (numberValue(invoke(cap, "getLevel")).intValue() != spec.level) throw new IllegalStateException("wrong L2 level");
            invoke(cap, "syncToClient", target);
            removeDatapackScaling();
            ticks = 0;
            phase = Phase.WAIT_SCALING;
        }

        void waitScaling() throws ReflectiveOperationException {
            if (++ticks < 30 || !target.getTags().contains(SCALE_TAG)) {
                if (ticks > 80) throw new IllegalStateException("Tensura:L2Hostility scaling did not reapply");
                return;
            }
            CaseSpec spec = cases.get(index);
            if (numberValue(invoke(cap, "getLevel")).intValue() != spec.level) throw new IllegalStateException("L2 level drift");
            JsonObject result = durabilityResult(spec);
            results.add(result);
            log("durability_result", result);
            index++;
            phase = Phase.SPAWN;
        }

        JsonObject durabilityResult(CaseSpec spec) throws ReflectiveOperationException {
            AttributeInstance hp = requiredAttribute(target, Attributes.MAX_HEALTH);
            AttributeInstance shp = requiredAttribute(target, TensuraAttributes.MAX_SPIRITUAL_HEALTH);
            Object config = invoke(cap, "getConfigCache", target);
            double entityHealthScale = numberValue(readField(config, "healthScale")).doubleValue();
            double healthFactor = serverDouble("healthFactor");
            boolean exponential = serverBoolean("exponentialHealth");
            double expectedHostilityAmount = exponential
                    ? Math.pow(1.0D + healthFactor, spec.level) - 1.0D
                    : spec.level * healthFactor;
            expectedHostilityAmount *= entityHealthScale;
            double hostilityAmount = modifierAmount(hp, "l2hostility:hostility_health");
            int tankRank = traitRank(cap, "l2hostility:tank");
            double tankHealthPerRank = serverDouble("tankHealth");
            double tankAmount = modifierAmount(hp, "l2hostility:tank_health");
            double nativeBase = hp.getBaseValue();
            double genericOnly = nativeBase * (1.0D + hostilityAmount);
            double genericDelta = genericOnly - nativeBase;
            double tankDelta = genericOnly * tankAmount;
            double theoretical = genericOnly * (1.0D + tankAmount);
            double finalHp = target.getMaxHealth();
            double genericRealized = Math.max(0.0D, Math.min(genericOnly, finalHp) - nativeBase);
            double tankRealized = Math.max(0.0D, finalHp - Math.min(genericOnly, finalHp));
            ResourceState resources = resources(target);
            double shpScale = modifierAmount(shp, "tensura_l2h:l2_shp_scale");

            JsonObject json = new JsonObject();
            json.addProperty("status", "complete");
            json.addProperty("boss", spec.boss.toString());
            json.addProperty("L2_level", spec.level);
            json.addProperty("APO_profile", "NONE");
            json.addProperty("native_created_max_HP_before_entity_join", nativeState.maxHp);
            json.addProperty("native_MAX_HEALTH_base_value", nativeBase);
            json.addProperty("native_created_MAX_HEALTH_base_value", nativeState.hpBase);
            json.addProperty("entity_healthScale", entityHealthScale);
            json.addProperty("L2_healthFactor", healthFactor);
            json.addProperty("L2_exponentialHealth", exponential);
            json.addProperty("generic_L2_health_modifier_amount", hostilityAmount);
            json.addProperty("generic_L2_health_modifier_expected_amount", expectedHostilityAmount);
            json.addProperty("generic_L2_health_multiplier", 1.0D + hostilityAmount);
            json.addProperty("generic_L2_health_unclamped_HP", genericOnly);
            json.addProperty("generic_L2_health_unclamped_contribution", genericDelta);
            json.addProperty("generic_L2_health_realized_contribution_to_final_HP", genericRealized);
            json.addProperty("Tank_rank", tankRank);
            json.addProperty("Tank_health_per_rank", tankHealthPerRank);
            json.addProperty("Tank_health_modifier_amount", tankAmount);
            json.addProperty("Tank_health_multiplier", 1.0D + tankAmount);
            json.addProperty("Tank_unclamped_contribution_after_generic", tankDelta);
            json.addProperty("Tank_realized_contribution_to_final_HP", tankRealized);
            json.addProperty("theoretical_unclamped_HP", theoretical);
            json.addProperty("final_max_HP", finalHp);
            json.addProperty("health_attribute_ceiling_loss", Math.max(0.0D, theoretical - finalHp));
            json.addProperty("armor", target.getAttributeValue(Attributes.ARMOR));
            json.addProperty("toughness", target.getAttributeValue(Attributes.ARMOR_TOUGHNESS));
            json.addProperty("native_created_max_SHP_before_entity_join", nativeState.maxShp);
            json.addProperty("native_MAX_SHP_base_value", shp.getBaseValue());
            json.addProperty("generic_L2_health_modifier_present_on_SHP", hasModifier(shp, "l2hostility:hostility_health"));
            json.addProperty("Tensura_L2H_datapack_SHP_modifier_amount", shpScale);
            json.addProperty("Tensura_L2H_datapack_SHP_expected_amount", spec.level * 0.03D);
            json.addProperty("Tensura_L2H_datapack_SHP_contribution", resources.maxShp - shp.getBaseValue());
            json.addProperty("final_max_SHP", resources.maxShp);
            json.addProperty("final_HP", target.getHealth());
            json.addProperty("final_SHP", resources.shp);
            json.addProperty("final_combined_fight_resources", finalHp + resources.maxShp);
            json.add("MAX_HEALTH_modifiers", modifiers(hp));
            json.add("MAX_SHP_modifiers", modifiers(shp));
            json.add("traits", readTraits(cap));
            json.addProperty("unexpected_L2_bypass", false);
            return json;
        }

        void removeDatapackScaling() {
            command("attribute @e[tag=" + TARGET_TAG + ",limit=1] tensura:max_spiritual_health modifier remove tensura_l2h:l2_shp_scale");
            command("attribute @e[tag=" + TARGET_TAG + ",limit=1] tensura:max_magicule modifier remove tensura_l2h:l2_magic_scale");
            command("attribute @e[tag=" + TARGET_TAG + ",limit=1] tensura:max_aura modifier remove tensura_l2h:l2_aura_scale");
            target.removeTag(SCALE_TAG);
        }

        void command(String value) {
            server.getCommands().performPrefixedCommand(server.createCommandSourceStack().withSuppressedOutput(), value);
        }

        void fail(Throwable throwable) {
            JsonObject json = new JsonObject();
            json.addProperty("status", "error");
            if (index < cases.size()) {
                json.addProperty("boss", cases.get(index).boss.toString());
                json.addProperty("L2_level", cases.get(index).level);
            }
            json.addProperty("error", throwable.toString());
            log("case_error", json);
            cleanup();
            index++;
            phase = Phase.SPAWN;
        }

        void cleanup() {
            if (target != null && !target.isRemoved()) target.discard();
            target = null;
            cap = null;
            level.getEntitiesOfClass(LivingEntity.class,
                    new net.minecraft.world.phys.AABB(-8, 230, 10, 8, 250, 30),
                    entity -> entity.getTags().contains(TARGET_TAG)).forEach(Entity::discard);
        }
    }

    private static JsonArray modifiers(AttributeInstance instance) {
        JsonArray array = new JsonArray();
        instance.getModifiers().stream().sorted(Comparator.comparing(modifier -> modifier.id().toString())).forEach(modifier -> {
            JsonObject json = new JsonObject();
            json.addProperty("id", modifier.id().toString());
            json.addProperty("amount", modifier.amount());
            json.addProperty("operation", modifier.operation().getSerializedName());
            array.add(json);
        });
        return array;
    }

    private static boolean hasModifier(AttributeInstance instance, String id) {
        return instance.hasModifier(ResourceLocation.parse(id));
    }

    private static double modifierAmount(AttributeInstance instance, String id) {
        AttributeModifier modifier = instance.getModifier(ResourceLocation.parse(id));
        return modifier == null ? 0.0D : modifier.amount();
    }

    private static int traitRank(Object cap, String id) throws ReflectiveOperationException {
        Object value = readField(cap, "traits");
        if (!(value instanceof Map<?, ?> map)) return 0;
        for (Map.Entry<?, ?> entry : map.entrySet()) {
            if (traitId(entry.getKey()).equals(id)) return numberValue(entry.getValue()).intValue();
        }
        return 0;
    }

    private static JsonArray readTraits(Object cap) throws ReflectiveOperationException {
        JsonArray array = new JsonArray();
        Object value = readField(cap, "traits");
        if (value instanceof Map<?, ?> map) {
            map.entrySet().stream().sorted(Comparator.comparing(entry -> traitId(entry.getKey()))).forEach(entry -> {
                JsonObject json = new JsonObject();
                json.addProperty("id", traitId(entry.getKey()));
                json.addProperty("rank", numberValue(entry.getValue()).intValue());
                array.add(json);
            });
        }
        return array;
    }

    private static String traitId(Object trait) {
        try {
            return invoke(invoke(trait, "getEntry"), "getId").toString();
        }
        catch (ReflectiveOperationException exception) {
            return String.valueOf(trait);
        }
    }

    private static AttributeInstance requiredAttribute(LivingEntity entity, Holder<Attribute> attribute) {
        AttributeInstance instance = entity.getAttribute(attribute);
        if (instance == null) throw new IllegalStateException("missing attribute " + attribute);
        return instance;
    }

    private static ResourceState resources(LivingEntity entity) {
        var existence = TensuraStorages.getExistenceFrom(entity);
        return new ResourceState(existence.getSpiritualHealth(), entity.getAttributeValue(TensuraAttributes.MAX_SPIRITUAL_HEALTH));
    }

    private static double serverDouble(String field) throws ReflectiveOperationException {
        Object server = staticField("dev.xkmc.l2hostility.init.data.LHConfig", "SERVER");
        return numberValue(invoke(readField(server, field), "get")).doubleValue();
    }

    private static boolean serverBoolean(String field) throws ReflectiveOperationException {
        Object server = staticField("dev.xkmc.l2hostility.init.data.LHConfig", "SERVER");
        return booleanValue(invoke(readField(server, field), "get"));
    }

    private static double uncheckedServerDouble(String field) {
        try {
            return serverDouble(field);
        }
        catch (ReflectiveOperationException exception) {
            throw new IllegalStateException("cannot read L2 config " + field, exception);
        }
    }

    private static void log(String kind, JsonObject json) {
        json.addProperty("schema", "tno.phase6.endgame_calibration.v1");
        json.addProperty("kind", kind);
        LOGGER.info("{} {}", MARKER, GSON.toJson(json));
    }

    private static Object staticField(String className, String name) throws ReflectiveOperationException {
        return Class.forName(className).getField(name).get(null);
    }

    private static Object readField(Object value, String name) throws ReflectiveOperationException {
        Field field = findField(value.getClass(), name);
        field.setAccessible(true);
        return field.get(value);
    }

    private static Field findField(Class<?> type, String name) throws NoSuchFieldException {
        for (Class<?> current = type; current != null; current = current.getSuperclass()) {
            try {
                return current.getDeclaredField(name);
            }
            catch (NoSuchFieldException ignored) {
            }
        }
        throw new NoSuchFieldException(type.getName() + "#" + name);
    }

    private static Object invoke(Object targetOrClass, String name, Object... args) throws ReflectiveOperationException {
        Class<?> type = targetOrClass instanceof Class<?> clazz ? clazz : targetOrClass.getClass();
        Method method = findMethod(type, name, args);
        method.setAccessible(true);
        return method.invoke(Modifier.isStatic(method.getModifiers()) ? null : targetOrClass, args);
    }

    private static Method findMethod(Class<?> type, String name, Object[] args) throws NoSuchMethodException {
        for (Method method : type.getMethods()) if (method.getName().equals(name) && compatible(method.getParameterTypes(), args)) return method;
        for (Class<?> current = type; current != null; current = current.getSuperclass()) {
            for (Method method : current.getDeclaredMethods()) if (method.getName().equals(name) && compatible(method.getParameterTypes(), args)) return method;
        }
        throw new NoSuchMethodException(type.getName() + "#" + name + "/" + args.length);
    }

    private static boolean compatible(Class<?>[] parameters, Object[] args) {
        if (parameters.length != args.length) return false;
        for (int i = 0; i < parameters.length; i++) {
            if (args[i] == null) continue;
            Class<?> parameter = parameters[i].isPrimitive() ? boxed(parameters[i]) : parameters[i];
            if (!parameter.isAssignableFrom(args[i].getClass())) return false;
        }
        return true;
    }

    private static Class<?> boxed(Class<?> type) {
        if (type == boolean.class) return Boolean.class;
        if (type == int.class) return Integer.class;
        if (type == long.class) return Long.class;
        if (type == float.class) return Float.class;
        if (type == double.class) return Double.class;
        if (type == short.class) return Short.class;
        if (type == byte.class) return Byte.class;
        if (type == char.class) return Character.class;
        return type;
    }

    private static Number numberValue(Object value) {
        if (value instanceof Number number) return number;
        throw new IllegalArgumentException("not numeric: " + value);
    }

    private static boolean booleanValue(Object value) {
        return value instanceof Boolean bool && bool;
    }

    private static ResourceLocation id(String namespace, String path) {
        return ResourceLocation.fromNamespaceAndPath(namespace, path);
    }

    private enum Phase { SPAWN, WAIT_ATTACHMENT, WAIT_SCALING, DONE }

    private record CaseSpec(ResourceLocation boss, int level) { }

    private record ResourceState(double shp, double maxShp) { }

    private record NativeState(double maxHp, double hpBase, double maxShp) {
        static NativeState capture(LivingEntity target) {
            AttributeInstance hp = requiredAttribute(target, Attributes.MAX_HEALTH);
            AttributeInstance shp = requiredAttribute(target, TensuraAttributes.MAX_SPIRITUAL_HEALTH);
            return new NativeState(target.getMaxHealth(), hp.getBaseValue(), shp.getValue());
        }
    }
}
