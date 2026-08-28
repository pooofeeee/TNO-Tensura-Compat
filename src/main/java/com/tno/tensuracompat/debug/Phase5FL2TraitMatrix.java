package com.tno.tensuracompat.debug;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.mojang.authlib.GameProfile;
import com.mojang.logging.LogUtils;
import io.github.manasmods.tensura.registry.attribute.TensuraAttributes;
import io.github.manasmods.tensura.storage.TensuraStorages;
import net.minecraft.core.Holder;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.TagKey;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.enchantment.Enchantment;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.Vec3;
import net.neoforged.fml.ModList;
import net.neoforged.fml.loading.FMLEnvironment;
import net.neoforged.neoforge.common.Tags;
import net.neoforged.neoforge.common.util.FakePlayer;
import net.neoforged.neoforge.common.util.FakePlayerFactory;
import net.neoforged.neoforge.event.entity.living.LivingDamageEvent;
import net.neoforged.neoforge.event.entity.living.LivingIncomingDamageEvent;
import net.neoforged.neoforge.event.server.ServerStartedEvent;
import net.neoforged.neoforge.event.tick.ServerTickEvent;
import org.slf4j.Logger;

import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.lang.reflect.Proxy;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Stream;

/**
 * Development-only L2 Hostility trait coverage runner. Natural mode uses the
 * real L2 generator and legality checks. Requested levels outside an entity's
 * datapack range use the accepted Phase 5F temporary cap override and are
 * labeled accordingly. Production combat and persistent datapack state are
 * never changed.
 */
public final class Phase5FL2TraitMatrix {
    private static final Logger LOGGER = LogUtils.getLogger();
    private static final Gson GSON = new GsonBuilder().disableHtmlEscaping().create();
    private static final String MARKER = "TNO_PHASE5F_L2_TRAITS";
    private static final String TARGET_TAG = "tno_phase5f_l2_trait_target";
    private static final String SCALE_TAG = "l2_tensura_scaled";
    private static final String L2_MISCS = "dev.xkmc.l2hostility.init.registrate.LHMiscs";
    private static final String L2_TRAITS = "dev.xkmc.l2hostility.init.registrate.LHTraits";
    private static final String L2_CONFIG = "dev.xkmc.l2hostility.init.data.LHConfig";
    private static final String TRAIT_MANAGER = "dev.xkmc.l2hostility.content.logic.TraitManager";
    private static final ResourceLocation ROYAL_BOW = id("royalvariations", "royal_bow");
    private static final ResourceLocation ROYAL_ARROW = id("royalvariations", "royal_arrow");
    private static final ResourceLocation MAGIC_WEAPON = id("tensura", "magic_weapon");
    private static final List<Integer> LEVELS = List.of(50, 100, 150, 200, 300, 400, 500, 600, 800, 1000);
    private static final List<String> EXPECTED_TRAITS = List.of(
            "l2hostility:tank", "l2hostility:speedy", "l2hostility:protection",
            "l2hostility:invisible", "l2hostility:fiery", "l2hostility:regenerate",
            "l2hostility:adaptive", "l2hostility:reflect", "l2hostility:shulker",
            "l2hostility:grenade", "l2hostility:corrosion", "l2hostility:erosion",
            "l2hostility:growth", "l2hostility:split", "l2hostility:drain",
            "l2hostility:counter_strike", "l2hostility:gravity", "l2hostility:moonwalk",
            "l2hostility:arena", "l2hostility:dementor", "l2hostility:dispell",
            "l2hostility:undying", "l2hostility:teleport", "l2hostility:repelling",
            "l2hostility:pulling", "l2hostility:reprint", "l2hostility:killer_aura",
            "l2hostility:ragnarok", "l2hostility:master", "l2hostility:weakness",
            "l2hostility:slowness", "l2hostility:poison", "l2hostility:wither",
            "l2hostility:levitation", "l2hostility:blindness", "l2hostility:nausea",
            "l2hostility:soul_burner", "l2hostility:freezing", "l2hostility:cursed"
    );
    private static final List<BossSpec> BOSSES = List.of(
            boss("tensura_neb", "luminous_valentine", 130, 300),
            boss("tensura", "hinata_sakaguchi", 120, 280),
            boss("tensura", "gazel_dwargo", 110, 260),
            boss("tensura", "orc_disaster", 100, 250),
            boss("tensura", "elemental_colossus", 75, 150),
            boss("tensura_neb", "carrion", 90, 210),
            boss("tensura_neb", "rimuru_ogre_fight", 85, 250)
    );
    private static final Map<String, TagKey<net.minecraft.world.damagesource.DamageType>> SOURCE_TAGS = Map.of(
            "neoforge:is_magic", Tags.DamageTypes.IS_MAGIC,
            "minecraft:is_projectile", DamageTypeTags.IS_PROJECTILE,
            "minecraft:bypasses_armor", DamageTypeTags.BYPASSES_ARMOR,
            "minecraft:bypasses_effects", DamageTypeTags.BYPASSES_EFFECTS,
            "minecraft:bypasses_invulnerability", DamageTypeTags.BYPASSES_INVULNERABILITY,
            "minecraft:bypasses_resistance", DamageTypeTags.BYPASSES_RESISTANCE
    );

    private static Session active;

    private Phase5FL2TraitMatrix() {
    }

    public static void onServerStarted(ServerStartedEvent event) {
        if (FMLEnvironment.production || !Boolean.getBoolean("tno.phase5f.l2TraitMatrix") || active != null) return;
        try {
            for (String mod : List.of("royalvariations", "l2hostility")) {
                if (!ModList.get().isLoaded(mod)) {
                    throw new IllegalStateException("required trait-matrix runtime mod absent: " + mod);
                }
            }
            active = new Session(event.getServer());
            LOGGER.info("{} matrix started", MARKER);
        }
        catch (Throwable throwable) {
            LOGGER.error("{} startup failed", MARKER, throwable);
            event.getServer().halt(false);
        }
    }

    public static void onServerTick(ServerTickEvent.Post event) {
        Session session = active;
        if (session == null) return;
        try {
            session.tick();
            if (session.complete) {
                active = null;
                event.getServer().halt(false);
            }
        }
        catch (Throwable throwable) {
            session.fail(throwable);
        }
    }

    public static void onIncomingHighest(LivingIncomingDamageEvent event) {
        if (active != null) active.captureIncoming(event, "incoming_highest");
    }

    public static void onIncomingLowest(LivingIncomingDamageEvent event) {
        if (active != null) active.captureIncoming(event, "incoming_lowest");
    }

    public static void onDamagePre(LivingDamageEvent.Pre event) {
        if (active != null) active.captureDamage(event.getEntity(), event.getSource(), event.getNewDamage(), "damage_pre");
    }

    public static void onDamagePost(LivingDamageEvent.Post event) {
        if (active != null) active.captureDamage(event.getEntity(), event.getSource(), event.getNewDamage(), "damage_post");
    }

    private static final class Session {
        private final MinecraftServer server;
        private final ServerLevel level;
        private final String mode;
        private final BossSpec boss;
        private final List<Object> traits;
        private final List<ForcedCase> forcedCases;
        private int caseIndex;
        private int phaseTick;
        private LivingEntity target;
        private LivingEntity victim;
        private LivingEntity auraVictim;
        private Object cap;
        private FakePlayer player;
        private ForcedObservation observation;
        private String action = "idle";
        private Phase phase = Phase.START;
        private boolean complete;
        private int errors;

        private Session(MinecraftServer server) throws ReflectiveOperationException {
            this.server = server;
            this.level = server.overworld();
            this.mode = System.getProperty("tno.phase5f.l2TraitMode", "natural").toLowerCase(Locale.ROOT);
            if (!mode.equals("natural") && !mode.equals("catalog") && !mode.equals("forced")) {
                throw new IllegalArgumentException("trait matrix supports natural, forced, or catalog mode, got " + mode);
            }
            this.boss = selectBoss(System.getProperty("tno.phase5f.l2TraitBoss", BOSSES.getFirst().id.toString()));
            this.traits = readTraitRegistry();
            assertCatalog();
            this.forcedCases = buildForcedCases();
            log("matrix_start", basePayload());
            log("trait_catalog", catalogPayload());
            if (mode.equals("catalog")) finish();
        }

        private void tick() throws ReflectiveOperationException {
            if (complete) return;
            if (mode.equals("forced")) {
                tickForced();
                return;
            }
            switch (phase) {
                case START -> startCase();
                case WAIT_ATTACHMENT -> waitAttachment();
                case WAIT_POST_INIT -> waitPostInit();
                case DONE -> {
                }
            }
        }

        private void startCase() {
            cleanup();
            if (caseIndex >= LEVELS.size()) {
                finish();
                return;
            }
            Entity created = BuiltInRegistries.ENTITY_TYPE.get(boss.id).create(level);
            if (!(created instanceof LivingEntity living)) {
                throw new IllegalStateException("could not create living target " + boss.id);
            }
            target = living;
            target.setPos(0.5D, 240.0D, 20.5D);
            target.setNoGravity(true);
            target.setSilent(true);
            target.addTag(TARGET_TAG);
            level.addFreshEntity(target);
            phaseTick = 0;
            phase = Phase.WAIT_ATTACHMENT;
        }

        private void waitAttachment() throws ReflectiveOperationException {
            if (++phaseTick < 5) return;
            Object type = invoke(staticField(L2_MISCS, "MOB"), "type");
            if (!booleanValue(invoke(type, "isProper", target))) {
                throw new IllegalStateException("L2 attachment rejected " + boss.id);
            }
            cap = invoke(type, "getOrCreate", target);
            int requested = LEVELS.get(caseIndex);
            Object config = invoke(cap, "getConfigCache", target);
            Field difficulty = findField(config.getClass(), "difficulty");
            Field maxLevel = findField(config.getClass(), "maxLevel");
            Object originalDifficulty = difficulty.get(config);
            int originalMax = maxLevel.getInt(config);
            try {
                int configuredMin = numberValue(invoke(originalDifficulty, "min")).intValue();
                if (requested < configuredMin) difficulty.set(config, difficultyWithMin(originalDifficulty, requested));
                if (requested > originalMax) maxLevel.setInt(config, requested);
                invoke(cap, "reinit", target, requested, false);
            }
            finally {
                difficulty.set(config, originalDifficulty);
                maxLevel.setInt(config, originalMax);
            }
            int attached = numberValue(invoke(cap, "getLevel")).intValue();
            if (attached != requested) {
                throw new IllegalStateException("attached level " + attached + " != requested " + requested);
            }
            invoke(cap, "syncToClient", target);
            phaseTick = 0;
            phase = Phase.WAIT_POST_INIT;
        }

        private void waitPostInit() throws ReflectiveOperationException {
            if (++phaseTick < 5) return;
            if (!target.getTags().contains(SCALE_TAG) && phaseTick < 60) return;
            log("natural_profile", profilePayload());
            caseIndex++;
            phase = Phase.START;
        }

        private JsonObject basePayload() {
            JsonObject json = new JsonObject();
            json.addProperty("evidence_class", mode.equals("forced")
                    ? "FORCED_DIAGNOSTIC_MATRIX" : "LEGAL_NATURAL_MATRIX");
            json.addProperty("mode", mode);
            json.addProperty("boss", boss.id.toString());
            json.add("requested_levels", ints(LEVELS));
            json.addProperty("expected_trait_count", EXPECTED_TRAITS.size());
            if (mode.equals("forced")) {
                json.addProperty("requested_forced_case_count", forcedCases.size());
                json.addProperty("trait_filter", System.getProperty("tno.phase5f.l2Trait", ""));
            }
            return json;
        }

        private JsonObject catalogPayload() throws ReflectiveOperationException {
            JsonObject json = basePayload();
            JsonArray entries = new JsonArray();
            for (Object trait : traits) entries.add(traitMetadata(trait));
            json.add("traits", entries);
            json.addProperty("trait_count", entries.size());
            return json;
        }

        private JsonObject profilePayload() throws ReflectiveOperationException {
            int requested = LEVELS.get(caseIndex);
            int attached = numberValue(invoke(cap, "getLevel")).intValue();
            Object config = invoke(cap, "getConfigCache", target);
            JsonArray generated = readTraits(cap);
            JsonObject json = basePayload();
            json.addProperty("requested_level", requested);
            json.addProperty("attached_level", attached);
            json.addProperty("configured_min_level", boss.minLevel);
            json.addProperty("configured_max_level", boss.maxLevel);
            json.addProperty("requested_level_naturally_obtainable", requested >= boss.minLevel && requested <= boss.maxLevel);
            json.addProperty("requested_level_mechanism", requested >= boss.minLevel && requested <= boss.maxLevel
                    ? "NATIVE_ENTITY_RANGE" : "SAFE_REQUESTED_LEVEL_OVERRIDE");
            json.addProperty("l2_initialized", booleanValue(invoke(cap, "isInitialized")));
            json.addProperty("max_HP", target.getMaxHealth());
            json.addProperty("HP", target.getHealth());
            json.addProperty("armor", target.getAttributeValue(Attributes.ARMOR));
            json.addProperty("toughness", target.getAttributeValue(Attributes.ARMOR_TOUGHNESS));
            ResourceState resources = resources(target);
            json.addProperty("spiritual_health", resources.spiritualHealth);
            json.addProperty("max_spiritual_health", resources.maxSpiritualHealth);
            json.addProperty("magicules", resources.magicules);
            json.addProperty("aura", resources.aura);
            json.add("traits", generated);
            json.add("trait_ranks", traitRanks(generated));
            json.addProperty("trait_count", generated.size());
            int globalMax = serverConfigInt("maxTraitCount");
            int entityMax = numberValue(readField(config, "maxTraitCount")).intValue();
            int effectiveMax = entityMax > 0 ? entityMax : globalMax;
            json.addProperty("global_max_trait_count", globalMax);
            json.addProperty("entity_max_trait_count", entityMax);
            json.addProperty("effective_max_trait_count", effectiveMax);
            json.addProperty("max_trait_count_reached", effectiveMax > 0 && generated.size() >= effectiveMax);
            JsonArray presets = presetTraits(config);
            json.add("preset_traits", presets);
            int nominalCost = nominalNonFreeCost(generated, presets);
            json.addProperty("trait_budget_observability", "NOT_EXPOSED_AFTER_GENERATION");
            json.addProperty("nominal_nonfree_trait_cost_upper_bound", nominalCost);
            json.addProperty("consumed_trait_budget", "NOT_RUNTIME_OBSERVABLE");
            json.addProperty("remaining_trait_budget", "NOT_RUNTIME_OBSERVABLE");
            JsonArray eligibility = new JsonArray();
            int maxModLevel = numberValue(invoke(Class.forName(TRAIT_MANAGER), "getMaxLevel")).intValue() + 1;
            for (Object trait : traits) eligibility.add(traitEligibility(trait, requested, maxModLevel, config));
            json.add("trait_eligibility", eligibility);
            json.addProperty("complete_trait_eligibility_count", eligibility.size());
            json.addProperty("tensura_l2h_scaling_marker", target.getTags().contains(SCALE_TAG));
            json.addProperty("APO_profile", "NONE");
            return json;
        }

        private JsonObject traitMetadata(Object trait) throws ReflectiveOperationException {
            ResourceLocation id = ResourceLocation.parse(traitId(trait));
            Object config = invoke(trait, "getConfig", level.registryAccess());
            JsonObject json = new JsonObject();
            json.addProperty("trait_id", id.toString());
            json.addProperty("runtime_class", trait.getClass().getName());
            json.addProperty("min_level", numberValue(invoke(config, "min_level")).intValue());
            json.addProperty("cost", numberValue(invoke(config, "cost")).intValue());
            json.addProperty("weight", numberValue(invoke(config, "weight")).intValue());
            json.addProperty("native_max_rank", numberValue(invoke(config, "max_rank")).intValue());
            json.addProperty("enabled", !booleanValue(invoke(trait, "isBanned")));
            TagKey<EntityType<?>> whitelist = TagKey.create(Registries.ENTITY_TYPE, id.withSuffix("_whitelist"));
            TagKey<EntityType<?>> blacklist = TagKey.create(Registries.ENTITY_TYPE, id.withSuffix("_blacklist"));
            json.addProperty("has_whitelist", BuiltInRegistries.ENTITY_TYPE.getTag(whitelist).map(set -> set.size() > 0).orElse(false));
            json.addProperty("has_blacklist", BuiltInRegistries.ENTITY_TYPE.getTag(blacklist).map(set -> set.size() > 0).orElse(false));
            Object exclusion = invoke(trait, "getExclusion", level.registryAccess());
            JsonObject excluded = new JsonObject();
            if (invoke(exclusion, "excluded") instanceof Map<?, ?> map) {
                map.entrySet().stream().sorted(Comparator.comparing(entry -> holderTraitId(entry.getKey())))
                        .forEach(entry -> excluded.addProperty(holderTraitId(entry.getKey()), numberValue(entry.getValue()).doubleValue()));
            }
            json.add("exclusions", excluded);
            return json;
        }

        private JsonObject traitEligibility(Object trait, int requested, int maxModLevel, Object entityConfig)
                throws ReflectiveOperationException {
            ResourceLocation id = ResourceLocation.parse(traitId(trait));
            Object config = invoke(trait, "getConfig", level.registryAccess());
            int min = numberValue(invoke(config, "min_level")).intValue();
            TagKey<EntityType<?>> whitelist = TagKey.create(Registries.ENTITY_TYPE, id.withSuffix("_whitelist"));
            TagKey<EntityType<?>> blacklist = TagKey.create(Registries.ENTITY_TYPE, id.withSuffix("_blacklist"));
            boolean hasWhitelist = BuiltInRegistries.ENTITY_TYPE.getTag(whitelist).map(set -> set.size() > 0).orElse(false);
            boolean hasBlacklist = BuiltInRegistries.ENTITY_TYPE.getTag(blacklist).map(set -> set.size() > 0).orElse(false);
            Collection<?> entityBlacklist = collectionValue(invoke(entityConfig, "blacklist"));
            JsonObject json = new JsonObject();
            json.addProperty("trait_id", id.toString());
            json.addProperty("min_level", min);
            json.addProperty("min_level_met", requested >= min);
            json.addProperty("has_whitelist", hasWhitelist);
            json.addProperty("whitelist_match", target.getType().is(whitelist));
            json.addProperty("has_blacklist", hasBlacklist);
            json.addProperty("blacklist_match", target.getType().is(blacklist));
            json.addProperty("entity_config_blacklisted", entityBlacklist.contains(trait));
            json.addProperty("entity_restriction_allows", booleanValue(invoke(trait, "allow", target, Integer.MAX_VALUE, maxModLevel)));
            json.addProperty("legal_at_requested_level", booleanValue(invoke(trait, "allow", target, requested, maxModLevel)));
            return json;
        }

        private JsonArray presetTraits(Object config) throws ReflectiveOperationException {
            JsonArray array = new JsonArray();
            for (Object base : collectionValue(invoke(config, "traits"))) {
                Object trait = invoke(base, "trait");
                JsonObject json = new JsonObject();
                json.addProperty("trait_id", traitId(trait));
                json.addProperty("minimum_rank", numberValue(invoke(base, "min")).intValue());
                json.addProperty("free_rank", numberValue(invoke(base, "free")).intValue());
                json.addProperty("caps_generation", booleanValue(invoke(base, "cap")));
                array.add(json);
            }
            return array;
        }

        private int nominalNonFreeCost(JsonArray generated, JsonArray presets) throws ReflectiveOperationException {
            Map<String, Integer> free = new LinkedHashMap<>();
            presets.forEach(value -> {
                JsonObject entry = value.getAsJsonObject();
                free.put(entry.get("trait_id").getAsString(), entry.get("free_rank").getAsInt());
            });
            Map<String, Object> byId = new LinkedHashMap<>();
            traits.forEach(trait -> byId.put(traitId(trait), trait));
            int total = 0;
            for (var value : generated) {
                JsonObject entry = value.getAsJsonObject();
                String id = entry.get("id").getAsString();
                int rank = entry.get("rank").getAsInt();
                Object trait = byId.get(id);
                Object config = invoke(trait, "getConfig", level.registryAccess());
                int cost = numberValue(invoke(config, "cost")).intValue();
                total += Math.max(0, rank - free.getOrDefault(id, 0)) * cost;
            }
            return total;
        }

        private List<ForcedCase> buildForcedCases() throws ReflectiveOperationException {
            List<ForcedCase> cases = new ArrayList<>();
            String filter = System.getProperty("tno.phase5f.l2Trait", "");
            for (Object trait : traits) {
                if (!filter.isBlank() && !traitId(trait).equals(filter)) continue;
                Object config = invoke(trait, "getConfig", level.registryAccess());
                int max = numberValue(invoke(config, "max_rank")).intValue();
                for (int rank = 1; rank <= max; rank++) cases.add(new ForcedCase(trait, traitId(trait), rank, max));
            }
            if (mode.equals("forced") && cases.isEmpty()) {
                throw new IllegalArgumentException("forced trait filter matched no live trait: " + filter);
            }
            return cases;
        }

        private void tickForced() throws ReflectiveOperationException {
            switch (phase) {
                case START -> startForcedCase();
                case FORCED_RUN -> runForcedCase();
                case DONE -> {
                }
                default -> throw new IllegalStateException("unexpected forced phase " + phase);
            }
        }

        private void startForcedCase() throws ReflectiveOperationException {
            cleanup();
            if (caseIndex >= forcedCases.size()) {
                finish();
                return;
            }
            ForcedCase spec = forcedCases.get(caseIndex);
            Entity created = BuiltInRegistries.ENTITY_TYPE.get(boss.id).create(level);
            if (!(created instanceof LivingEntity living)) throw new IllegalStateException("could not create forced target " + boss.id);
            target = living;
            target.setPos(0.5D, 240.0D, 20.5D);
            target.setNoGravity(true);
            target.setSilent(true);
            target.addTag(TARGET_TAG);

            Object type = invoke(staticField(L2_MISCS, "MOB"), "type");
            cap = invoke(type, "getOrCreate", target);
            initializeWithoutGeneratedTraits(cap, target, 1000);
            AttributeState baseline = attributes(target);
            boolean legal = booleanValue(invoke(spec.trait, "allow", target, 1000,
                    numberValue(invoke(Class.forName(TRAIT_MANAGER), "getMaxLevel")).intValue() + 1));
            Object rawTraits = readField(cap, "traits");
            if (!(rawTraits instanceof Map<?, ?> rawMap)) {
                throw new IllegalStateException("L2 forced trait map is not observable");
            }
            @SuppressWarnings("unchecked")
            Map<Object, Integer> traitMap = (Map<Object, Integer>) rawMap;
            traitMap.put(spec.trait, spec.rank);
            invoke(spec.trait, "initialize", target, spec.rank);
            invoke(spec.trait, "postInit", target, spec.rank);
            invoke(cap, "syncToClient", target);
            level.addFreshEntity(target);

            Entity auraProbe = EntityType.ARMOR_STAND.create(level);
            if (!(auraProbe instanceof LivingEntity livingAuraProbe)) {
                throw new IllegalStateException("could not create aura probe entity");
            }
            auraVictim = livingAuraProbe;
            auraVictim.setPos(0.5D, 240.0D, 23.0D);
            auraVictim.setNoGravity(true);
            auraVictim.addTag(TARGET_TAG);
            level.addFreshEntity(auraVictim);

            Entity probe = EntityType.ZOMBIE.create(level);
            if (!(probe instanceof LivingEntity livingProbe)) throw new IllegalStateException("could not create probe entity");
            victim = livingProbe;
            victim.setPos(0.5D, 240.0D, 50.0D);
            victim.setNoGravity(true);
            victim.addTag(TARGET_TAG);
            setBase(victim, Attributes.MAX_HEALTH, 1_000.0D);
            victim.setHealth(victim.getMaxHealth());
            if (victim instanceof Mob mobProbe) mobProbe.setNoAi(true);
            equipProbe(victim);
            level.addFreshEntity(victim);
            Object probeCap = invoke(type, "getOrCreate", victim);
            invoke(probeCap, "deinit");
            if (readTraits(probeCap).size() != 0) {
                throw new IllegalStateException("neutral probe retained L2 traits after deinit");
            }

            player = createForcedPlayer(caseIndex);
            observation = new ForcedObservation(spec, legal, baseline, resources(target),
                    resources(player), nearbyEntityTypes());
            observation.victimInitialEquipment = equipment(victim);
            observation.playerInitialEquipment = equipment(player);
            if (target instanceof Mob mob) mob.setTarget(player);
            phaseTick = 0;
            action = "forced_initialization";
            phase = Phase.FORCED_RUN;
        }

        private void initializeWithoutGeneratedTraits(Object forcedCap, LivingEntity living, int requested)
                throws ReflectiveOperationException {
            Object config = invoke(forcedCap, "getConfigCache", living);
            Field difficulty = findField(config.getClass(), "difficulty");
            Field maxLevel = findField(config.getClass(), "maxLevel");
            Object originalDifficulty = difficulty.get(config);
            int originalMax = maxLevel.getInt(config);
            Class<?> modifierType = Class.forName(
                    "dev.xkmc.l2hostility.content.capability.chunk.RegionalDifficultyModifier");
            Object modifier = Proxy.newProxyInstance(modifierType.getClassLoader(), new Class<?>[]{modifierType},
                    (proxy, method, args) -> {
                        if (method.getDeclaringClass() == Object.class) {
                            return switch (method.getName()) {
                                case "toString" -> "TNO forced no-trait difficulty fixture";
                                case "hashCode" -> System.identityHashCode(proxy);
                                case "equals" -> proxy == args[0];
                                default -> null;
                            };
                        }
                        if (args != null && args.length == 2) {
                            Object collector = args[1];
                            setIntField(collector, "min", 0);
                            setIntField(collector, "base", requested);
                            setIntField(collector, "cap", requested);
                            setDoubleField(collector, "apply_chance", 1.0D);
                            setDoubleField(collector, "trait_chance", 0.0D);
                            setBooleanField(collector, "fullChance", false);
                        }
                        return null;
                    });
            try {
                maxLevel.setInt(config, Math.max(originalMax, requested));
                invoke(forcedCap, "deinit");
                invoke(forcedCap, "init", level, living, modifier);
            }
            finally {
                difficulty.set(config, originalDifficulty);
                maxLevel.setInt(config, originalMax);
            }
            if (numberValue(invoke(forcedCap, "getLevel")).intValue() != requested) {
                throw new IllegalStateException("forced clean level did not attach at " + requested);
            }
            if (readTraits(forcedCap).size() != 0) {
                throw new IllegalStateException("forced clean initialization generated native traits");
            }
        }

        private void runForcedCase() throws ReflectiveOperationException {
            phaseTick++;
            stabilizeForcedEntities();
            if (phaseTick == 5) {
                JsonArray attached = readTraits(cap);
                ForcedCase spec = forcedCases.get(caseIndex);
                if (attached.size() != 1 || !attached.get(0).getAsJsonObject().get("id").getAsString().equals(spec.id)
                        || attached.get(0).getAsJsonObject().get("rank").getAsInt() != spec.rank) {
                    throw new IllegalStateException("forced trait attachment mismatch: " + attached);
                }
                observation.afterInitialization = attributes(target);
                observation.targetInvisible = target.isInvisible();
                observation.targetEffectsAtStart = effects(target);
                target.setHealth(Math.max(1.0F, target.getMaxHealth() * 0.5F));
                observation.regenWoundedHealth = target.getHealth();
            }
            if (phaseTick == 25) observation.regenObservedHealth = target.getHealth();
            if (phaseTick == 30) {
                restoreTargetResources();
                action = "royal_arrow_physical_repeat_1";
                fireRoyalArrow(false, false);
            }
            if (phaseTick == 35) {
                restoreTargetResources();
                action = "royal_arrow_physical_repeat_2";
                fireRoyalArrow(false, false);
            }
            if (phaseTick == 40) {
                restoreTargetResources();
                action = "direct_player_melee_control";
                target.hurt(player.damageSources().playerAttack(player), 40.0F);
            }
            if (phaseTick == 45) {
                restoreTargetResources();
                action = "magic_weapon_native";
                fireRoyalArrow(true, false);
            }
            if (phaseTick == 50) {
                restoreTargetResources();
                action = "magic_weapon_s7_fixture";
                fireRoyalArrow(true, true);
            }
            if (phaseTick == 55 || phaseTick == 60) {
                restoreVictimResources();
                action = "boss_sourced_physical_control_" + phaseTick;
                victim.hurt(target.damageSources().mobAttack(target), 10.0F);
            }
            ForcedCase spec = forcedCases.get(caseIndex);
            if (phaseTick == 70 && (spec.id.equals("l2hostility:undying") || spec.id.equals("l2hostility:split"))) {
                action = "lethal_royal_arrow_transition";
                target.setHealth(1.0F);
                TensuraStorages.getExistenceFrom(target).setSpiritualHealth(0.0D);
                fireRoyalArrow(false, false);
                observation.lethalTransitionExercised = true;
            }
            int terminalTick = spec.id.equals("l2hostility:shulker") || spec.id.equals("l2hostility:grenade")
                    || spec.id.equals("l2hostility:master") ? 240 : 100;
            if (phaseTick >= terminalTick) finishForcedCase();
        }

        private void finishForcedCase() throws ReflectiveOperationException {
            action = "final_snapshot";
            observation.afterRun = target != null && !target.isRemoved() ? attributes(target) : AttributeState.ZERO;
            observation.targetAlive = target != null && target.isAlive();
            observation.targetFinalHealth = target != null && !target.isRemoved() ? target.getHealth() : 0.0D;
            observation.targetFinalResources = target != null && !target.isRemoved() ? resources(target) : ResourceState.ZERO;
            observation.playerFinalResources = resources(player);
            observation.playerFinalHealth = player != null ? player.getHealth() : 0.0D;
            observation.playerEffects = player != null ? effects(player) : new JsonArray();
            observation.playerEquipment = player != null ? equipment(player) : new JsonArray();
            observation.victimFinalHealth = victim != null && !victim.isRemoved() ? victim.getHealth() : 0.0D;
            observation.victimEffects = victim != null && !victim.isRemoved() ? effects(victim) : new JsonArray();
            observation.victimEquipment = victim != null && !victim.isRemoved() ? equipment(victim) : new JsonArray();
            observation.victimFireTicks = victim != null ? victim.getRemainingFireTicks() : 0;
            observation.victimMotion = victim != null ? victim.getDeltaMovement() : Vec3.ZERO;
            observation.auraVictimEffects = auraVictim != null && !auraVictim.isRemoved()
                    ? effects(auraVictim) : new JsonArray();
            observation.auraVictimMotion = auraVictim != null ? auraVictim.getDeltaMovement() : Vec3.ZERO;
            observation.targetMotion = target != null ? target.getDeltaMovement() : Vec3.ZERO;
            observation.targetFinalPosition = target != null ? target.position() : Vec3.ZERO;
            observation.finalNearbyEntities = nearbyEntityTypes();
            observation.masterProtected = cap != null && booleanValue(invoke(cap, "isMasterProtected"));
            observation.tensuraScalingMarker = target != null && target.getTags().contains(SCALE_TAG);
            log("forced_trait_result", observation.toJson(boss.id));
            cleanup();
            observation = null;
            caseIndex++;
            phaseTick = 0;
            phase = Phase.START;
        }

        private void restoreTargetResources() {
            if (target == null || target.isRemoved()) return;
            target.setHealth(target.getMaxHealth());
            var existence = TensuraStorages.getExistenceFrom(target);
            existence.setSpiritualHealth(attribute(target, TensuraAttributes.MAX_SPIRITUAL_HEALTH));
        }

        private void restorePlayerResources() {
            if (player == null) return;
            player.setHealth(player.getMaxHealth());
            var existence = TensuraStorages.getExistenceFrom(player);
            existence.setSpiritualHealth(attribute(player, TensuraAttributes.MAX_SPIRITUAL_HEALTH));
        }

        private void restoreVictimResources() {
            if (victim == null || victim.isRemoved()) return;
            victim.setHealth(victim.getMaxHealth());
            var existence = TensuraStorages.getExistenceFrom(victim);
            existence.setSpiritualHealth(attribute(victim, TensuraAttributes.MAX_SPIRITUAL_HEALTH));
        }

        private void stabilizeForcedEntities() {
            if (player != null) {
                player.getCooldowns().tick();
                if (!player.isAlive()) player.setHealth(player.getMaxHealth());
            }
            if (target instanceof Mob mob && player != null && player.isAlive()) {
                mob.setTarget(player);
                target.setOnGround(true);
            }
        }

        private FakePlayer createForcedPlayer(int index) {
            UUID uuid = UUID.nameUUIDFromBytes(("tno-phase5f-l2-traits-" + index).getBytes(StandardCharsets.UTF_8));
            FakePlayer fake = FakePlayerFactory.get(level, new GameProfile(uuid, "TNO_L2T_" + index));
            fake.getInventory().clearContent();
            fake.removeAllEffects();
            fake.getAbilities().instabuild = false;
            fake.getAbilities().invulnerable = false;
            setBase(fake, Attributes.MAX_HEALTH, 1_000_000.0D);
            setBase(fake, TensuraAttributes.MAX_SPIRITUAL_HEALTH, 1_000_000_000.0D);
            setBase(fake, TensuraAttributes.MAX_MAGICULE, 1_000_000_000.0D);
            setBase(fake, TensuraAttributes.MAX_AURA, 1_000_000_000.0D);
            fake.setHealth(fake.getMaxHealth());
            var existence = TensuraStorages.getExistenceFrom(fake);
            existence.setSpiritualHealth(1_000_000_000.0D);
            existence.setMagicule(1_000_000_000.0D);
            existence.setAura(1_000_000_000.0D);
            fake.setPos(0.5D, 240.0D, 16.0D);
            fake.setItemSlot(EquipmentSlot.HEAD, enchanted(new ItemStack(Items.DIAMOND_HELMET)));
            fake.setItemSlot(EquipmentSlot.CHEST, enchanted(new ItemStack(Items.DIAMOND_CHESTPLATE)));
            fake.setItemSlot(EquipmentSlot.LEGS, enchanted(new ItemStack(Items.DIAMOND_LEGGINGS)));
            fake.setItemSlot(EquipmentSlot.FEET, enchanted(new ItemStack(Items.DIAMOND_BOOTS)));
            return fake;
        }

        private void equipProbe(LivingEntity probe) {
            probe.setItemSlot(EquipmentSlot.MAINHAND, enchanted(new ItemStack(Items.DIAMOND_SWORD)));
            probe.setItemSlot(EquipmentSlot.OFFHAND, new ItemStack(Items.SHIELD));
            probe.setItemSlot(EquipmentSlot.HEAD, enchanted(new ItemStack(Items.DIAMOND_HELMET)));
            probe.setItemSlot(EquipmentSlot.CHEST, enchanted(new ItemStack(Items.DIAMOND_CHESTPLATE)));
            probe.setItemSlot(EquipmentSlot.LEGS, enchanted(new ItemStack(Items.DIAMOND_LEGGINGS)));
            probe.setItemSlot(EquipmentSlot.FEET, enchanted(new ItemStack(Items.DIAMOND_BOOTS)));
        }

        private ItemStack enchanted(ItemStack stack) {
            Registry<Enchantment> registry = server.registryAccess().registryOrThrow(Registries.ENCHANTMENT);
            var holder = registry.getHolderOrThrow(ResourceKey.create(Registries.ENCHANTMENT, id("minecraft", "unbreaking")));
            stack.enchant(holder, 3);
            return stack;
        }

        private void fireRoyalArrow(boolean magic, boolean s7) {
            if (target == null || target.isRemoved()) return;
            ItemStack bow = new ItemStack(requiredItem(ROYAL_BOW));
            if (magic) {
                Registry<Enchantment> registry = server.registryAccess().registryOrThrow(Registries.ENCHANTMENT);
                bow.enchant(registry.getHolderOrThrow(ResourceKey.create(Registries.ENCHANTMENT, MAGIC_WEAPON)), 1);
            }
            player.setItemInHand(InteractionHand.MAIN_HAND, bow);
            player.setItemInHand(InteractionHand.OFF_HAND, new ItemStack(requiredItem(ROYAL_ARROW), 64));
            player.setItemSlot(EquipmentSlot.MAINHAND, bow);
            try {
                invoke(player, "detectEquipmentUpdates");
            }
            catch (ReflectiveOperationException exception) {
                throw new IllegalStateException("could not refresh forced player equipment", exception);
            }
            Set<UUID> existing = new LinkedHashSet<>();
            level.getEntitiesOfClass(Projectile.class, player.getBoundingBox().inflate(64.0D),
                    projectile -> sameEntity(projectile.getOwner(), player)).forEach(projectile -> existing.add(projectile.getUUID()));
            bow.releaseUsing(level, player, bow.getUseDuration(player) - 20);
            List<Projectile> spawned = level.getEntitiesOfClass(Projectile.class, player.getBoundingBox().inflate(64.0D),
                    projectile -> sameEntity(projectile.getOwner(), player) && !existing.contains(projectile.getUUID()));
            if (spawned.isEmpty()) throw new IllegalStateException("forced Royal Bow release created no projectile");
            boolean dispatched = false;
            for (Projectile projectile : spawned) {
                if (!(projectile instanceof AbstractArrow arrow)) continue;
                if (!BuiltInRegistries.ENTITY_TYPE.getKey(arrow.getType()).equals(ROYAL_ARROW)) continue;
                try {
                    invoke(arrow, "setMarking", false);
                }
                catch (ReflectiveOperationException exception) {
                    throw new IllegalStateException("could not disable Royal Arrow Mark", exception);
                }
                arrow.setCritArrow(false);
                arrow.addTag(TARGET_TAG);
                Vec3 aim = target.getBoundingBox().getCenter();
                double speed = arrow.getDeltaMovement().length();
                Vec3 direction = aim.subtract(arrow.position()).normalize();
                arrow.setPos(aim.subtract(direction.scale(2.0D)));
                arrow.setDeltaMovement(direction.scale(speed));
                arrow.hasImpulse = true;
                observation.magicS7FixtureActive = s7;
                try {
                    invoke(arrow, "onHitEntity", new EntityHitResult(target));
                }
                catch (ReflectiveOperationException exception) {
                    throw new IllegalStateException("could not dispatch forced Royal Arrow collision", exception);
                }
                finally {
                    observation.magicS7FixtureActive = false;
                }
                dispatched = true;
            }
            if (!dispatched) throw new IllegalStateException("Royal Bow did not create royalvariations:royal_arrow");
        }

        private void captureIncoming(LivingIncomingDamageEvent event, String hook) {
            if (!mode.equals("forced") || observation == null) return;
            if (event.getEntity() != target && event.getEntity() != victim && event.getEntity() != player) return;
            String source = damageType(event.getSource());
            double before = event.getAmount();
            if (hook.equals("incoming_highest") && observation.magicS7FixtureActive
                    && event.getEntity() == target && source.equals("tensura:magic")) {
                event.setAmount((float) (event.getAmount() * 1.8D));
            }
            JsonObject json = eventPayload(event.getEntity(), event.getSource(), action, hook, before, event.getAmount());
            json.addProperty("canceled", event.isCanceled());
            json.addProperty("magic_S7_fixture_active", observation.magicS7FixtureActive);
            observation.events.add(json);
            if (hook.equals("incoming_lowest") && event.isCanceled()) {
                observation.anyIncomingCanceled = true;
                observation.canceledActions.add(action);
                if (event.getEntity() == target) {
                    observation.canceledTargetDamageKeys.add(damageKey(action, source));
                }
            }
        }

        private void captureDamage(LivingEntity entity, net.minecraft.world.damagesource.DamageSource source,
                float amount, String hook) {
            if (!mode.equals("forced") || observation == null) return;
            if (entity != target && entity != victim && entity != player) return;
            observation.events.add(eventPayload(entity, source, action, hook, amount, amount));
            if (hook.equals("damage_post") && entity == target && amount > 0.0F) {
                observation.anyTargetDamagePost = true;
                observation.targetDamagePostActions.add(action);
                observation.targetDamagePostKeys.add(damageKey(action, damageType(source)));
            }
        }

        private String damageKey(String eventAction, String source) {
            return eventAction + "|" + source;
        }

        private JsonObject eventPayload(LivingEntity entity, net.minecraft.world.damagesource.DamageSource source,
                String eventAction, String hook, double before, double after) {
            JsonObject json = new JsonObject();
            json.addProperty("action", eventAction);
            json.addProperty("hook", hook);
            json.addProperty("entity_role", entity == target ? "boss" : entity == victim ? "probe_entity" : "royal_bow_user");
            json.addProperty("damage_source_id", damageType(source));
            json.add("damage_source_tags", strings(sourceTags(source)));
            json.addProperty("source_is_projectile", source.is(DamageTypeTags.IS_PROJECTILE));
            json.addProperty("source_is_l2_magic", source.is(Tags.DamageTypes.IS_MAGIC));
            json.addProperty("amount_before_hook", before);
            json.addProperty("amount_after_hook", after);
            return json;
        }

        private AttributeState attributes(LivingEntity living) {
            return new AttributeState(living.getMaxHealth(), living.getAttributeValue(Attributes.ARMOR),
                    living.getAttributeValue(Attributes.ARMOR_TOUGHNESS),
                    living.getAttributeValue(Attributes.MOVEMENT_SPEED));
        }

        private JsonArray effects(LivingEntity living) {
            JsonArray array = new JsonArray();
            living.getActiveEffects().stream()
                    .sorted(Comparator.comparing(effect -> BuiltInRegistries.MOB_EFFECT.getKey(effect.getEffect().value()).toString()))
                    .forEach(effect -> {
                        JsonObject json = new JsonObject();
                        json.addProperty("id", BuiltInRegistries.MOB_EFFECT.getKey(effect.getEffect().value()).toString());
                        json.addProperty("amplifier", effect.getAmplifier());
                        json.addProperty("duration", effect.getDuration());
                        array.add(json);
                    });
            return array;
        }

        private JsonArray equipment(LivingEntity living) {
            JsonArray array = new JsonArray();
            for (EquipmentSlot slot : EquipmentSlot.values()) {
                ItemStack stack = living.getItemBySlot(slot);
                JsonObject json = new JsonObject();
                json.addProperty("slot", slot.getName());
                json.addProperty("item", BuiltInRegistries.ITEM.getKey(stack.getItem()).toString());
                json.addProperty("damage", stack.getDamageValue());
                JsonArray components = new JsonArray();
                stack.getComponents().keySet().stream()
                        .map(type -> BuiltInRegistries.DATA_COMPONENT_TYPE.getKey(type).toString())
                        .sorted().forEach(components::add);
                json.add("component_types", components);
                json.addProperty("sealed_or_disabled_component_present",
                        stack.getComponents().toString().contains("l2hostility"));
                array.add(json);
            }
            return array;
        }

        private JsonObject nearbyEntityTypes() {
            Map<String, Integer> counts = new LinkedHashMap<>();
            level.getEntities((Entity) null, new AABB(-32, 220, -32, 32, 270, 48), entity -> true)
                    .forEach(entity -> counts.merge(BuiltInRegistries.ENTITY_TYPE.getKey(entity.getType()).toString(), 1, Integer::sum));
            JsonObject json = new JsonObject();
            counts.forEach(json::addProperty);
            return json;
        }

        private void finish() {
            cleanup();
            JsonObject json = basePayload();
            json.addProperty("status", errors == 0 ? "complete" : "complete_with_errors");
            json.addProperty("profile_count", caseIndex);
            json.addProperty("requested_profile_count", mode.equals("natural") ? LEVELS.size()
                    : mode.equals("forced") ? forcedCases.size() : 0);
            json.addProperty("case_error_count", errors);
            log("matrix_result", json);
            phase = Phase.DONE;
            complete = true;
        }

        private void fail(Throwable throwable) {
            errors++;
            JsonObject json = basePayload();
            if (mode.equals("forced") && caseIndex < forcedCases.size()) {
                ForcedCase spec = forcedCases.get(caseIndex);
                json.addProperty("trait_id", spec.id);
                json.addProperty("rank", spec.rank);
            }
            else {
                json.addProperty("requested_level", caseIndex < LEVELS.size() ? LEVELS.get(caseIndex) : -1);
            }
            json.addProperty("error_type", throwable.getClass().getName());
            json.addProperty("error_message", String.valueOf(throwable.getMessage()));
            log("case_error", json);
            LOGGER.error("{} case failure", MARKER, throwable);
            caseIndex++;
            phase = Phase.START;
        }

        private void cleanup() {
            if (target != null && !target.isRemoved()) target.discard();
            if (victim != null && !victim.isRemoved()) victim.discard();
            if (auraVictim != null && !auraVictim.isRemoved()) auraVictim.discard();
            target = null;
            victim = null;
            auraVictim = null;
            cap = null;
            player = null;
            level.getEntities((Entity) null, new AABB(-64, 200, -64, 64, 300, 64),
                    entity -> entity.getTags().contains(TARGET_TAG)).forEach(Entity::discard);
        }

        private List<Object> readTraitRegistry() throws ReflectiveOperationException {
            Object registry = invoke(staticField(L2_TRAITS, "TRAITS"), "get");
            List<Object> values = new ArrayList<>();
            if (registry instanceof Iterable<?> iterable) iterable.forEach(values::add);
            else if (invoke(registry, "stream") instanceof Stream<?> stream) stream.forEach(values::add);
            values.sort(Comparator.comparing(Phase5FL2TraitMatrix::traitId));
            return values;
        }

        private void assertCatalog() {
            List<String> actual = traits.stream().map(Phase5FL2TraitMatrix::traitId).sorted().toList();
            List<String> expected = EXPECTED_TRAITS.stream().sorted().toList();
            if (!actual.equals(expected)) {
                throw new IllegalStateException("live trait catalog differs from required 39: " + actual);
            }
        }
    }

    private static JsonArray readTraits(Object cap) throws ReflectiveOperationException {
        JsonArray traits = new JsonArray();
        if (readField(cap, "traits") instanceof Map<?, ?> map) {
            map.entrySet().stream().sorted(Comparator.comparing(entry -> traitId(entry.getKey())))
                    .forEach(entry -> {
                        JsonObject trait = new JsonObject();
                        trait.addProperty("id", traitId(entry.getKey()));
                        trait.addProperty("rank", numberValue(entry.getValue()).intValue());
                        traits.add(trait);
                    });
        }
        return traits;
    }

    private static JsonObject traitRanks(JsonArray traits) {
        JsonObject ranks = new JsonObject();
        traits.forEach(value -> {
            JsonObject trait = value.getAsJsonObject();
            ranks.addProperty(trait.get("id").getAsString(), trait.get("rank").getAsInt());
        });
        return ranks;
    }

    private static ResourceState resources(LivingEntity entity) {
        try {
            var existence = TensuraStorages.getExistenceFrom(entity);
            return new ResourceState(existence.getSpiritualHealth(), attribute(entity, TensuraAttributes.MAX_SPIRITUAL_HEALTH),
                    existence.getMagicule(), existence.getAura());
        }
        catch (Throwable ignored) {
            return new ResourceState(0.0D, 0.0D, 0.0D, 0.0D);
        }
    }

    private static double attribute(LivingEntity entity, Holder<Attribute> attribute) {
        return entity.getAttributes().hasAttribute(attribute) ? entity.getAttributeValue(attribute) : 0.0D;
    }

    private static void setBase(LivingEntity entity, Holder<Attribute> attribute, double value) {
        var instance = entity.getAttribute(attribute);
        if (instance != null) instance.setBaseValue(value);
    }

    private static Item requiredItem(ResourceLocation id) {
        Item item = BuiltInRegistries.ITEM.get(id);
        if (item == null || BuiltInRegistries.ITEM.getKey(item).equals(id("minecraft", "air"))) {
            throw new IllegalStateException("required forced-matrix item absent: " + id);
        }
        return item;
    }

    private static boolean sameEntity(Entity first, Entity second) {
        return first == second || first != null && second != null && first.getUUID().equals(second.getUUID());
    }

    private static ResourceLocation id(String namespace, String path) {
        return ResourceLocation.fromNamespaceAndPath(namespace, path);
    }

    private static String damageType(net.minecraft.world.damagesource.DamageSource source) {
        return source.typeHolder().unwrapKey().map(key -> key.location().toString()).orElse("unregistered");
    }

    private static Set<String> sourceTags(net.minecraft.world.damagesource.DamageSource source) {
        Set<String> tags = new LinkedHashSet<>();
        SOURCE_TAGS.forEach((name, tag) -> {
            if (source.is(tag)) tags.add(name);
        });
        return tags;
    }

    private static JsonArray strings(Collection<?> values) {
        JsonArray array = new JsonArray();
        values.forEach(value -> array.add(String.valueOf(value)));
        return array;
    }

    private static int serverConfigInt(String field) throws ReflectiveOperationException {
        Object server = staticField(L2_CONFIG, "SERVER");
        return numberValue(invoke(readField(server, field), "get")).intValue();
    }

    private static void setIntField(Object target, String field, int value) throws ReflectiveOperationException {
        findField(target.getClass(), field).setInt(target, value);
    }

    private static void setDoubleField(Object target, String field, double value) throws ReflectiveOperationException {
        findField(target.getClass(), field).setDouble(target, value);
    }

    private static void setBooleanField(Object target, String field, boolean value) throws ReflectiveOperationException {
        findField(target.getClass(), field).setBoolean(target, value);
    }

    private static Object difficultyWithMin(Object original, int min) throws ReflectiveOperationException {
        var constructor = original.getClass().getDeclaredConstructor(
                int.class, int.class, double.class, double.class, double.class, double.class, double.class);
        constructor.setAccessible(true);
        return constructor.newInstance(min,
                numberValue(invoke(original, "base")).intValue(),
                numberValue(invoke(original, "variation")).doubleValue(),
                numberValue(invoke(original, "scale")).doubleValue(),
                numberValue(invoke(original, "apply_chance")).doubleValue(),
                numberValue(invoke(original, "trait_chance")).doubleValue(),
                numberValue(invoke(original, "suppression")).doubleValue());
    }

    private static String holderTraitId(Object holder) {
        try {
            return traitId(invoke(holder, "value"));
        }
        catch (ReflectiveOperationException exception) {
            return String.valueOf(holder);
        }
    }

    private static String traitId(Object trait) {
        try {
            Object entry = invoke(trait, "getEntry");
            Object value = invoke(entry, "getId");
            if (value instanceof ResourceLocation id) return id.toString();
        }
        catch (Throwable ignored) {
        }
        try {
            Object value = invoke(trait, "getRegistryName");
            if (value instanceof ResourceLocation id) return id.toString();
        }
        catch (Throwable ignored) {
        }
        return String.valueOf(trait);
    }

    private static BossSpec selectBoss(String value) {
        return BOSSES.stream().filter(boss -> boss.id.toString().equals(value)).findFirst()
                .orElseThrow(() -> new IllegalArgumentException("unknown Phase 5F trait-matrix boss " + value));
    }

    private static BossSpec boss(String namespace, String path, int min, int max) {
        return new BossSpec(ResourceLocation.fromNamespaceAndPath(namespace, path), min, max);
    }

    private static JsonArray ints(Collection<Integer> values) {
        JsonArray array = new JsonArray();
        values.forEach(array::add);
        return array;
    }

    private static void log(String kind, JsonObject payload) {
        payload.addProperty("schema", "tno.phase5f.l2_trait_matrix.v1");
        payload.addProperty("kind", kind);
        LOGGER.info("{} {}", MARKER, GSON.toJson(payload));
    }

    private static Object staticField(String className, String name) throws ReflectiveOperationException {
        return Class.forName(className).getField(name).get(null);
    }

    private static Object invoke(Object targetOrClass, String name, Object... args) throws ReflectiveOperationException {
        Class<?> type = targetOrClass instanceof Class<?> clazz ? clazz : targetOrClass.getClass();
        Method method = findMethod(type, name, args);
        method.setAccessible(true);
        return method.invoke(Modifier.isStatic(method.getModifiers()) ? null : targetOrClass, args);
    }

    private static Method findMethod(Class<?> type, String name, Object... args) throws NoSuchMethodException {
        for (Class<?> cursor = type; cursor != null; cursor = cursor.getSuperclass()) {
            for (Method method : cursor.getDeclaredMethods()) {
                if (!method.getName().equals(name) || method.getParameterCount() != args.length) continue;
                Class<?>[] params = method.getParameterTypes();
                boolean matches = true;
                for (int i = 0; i < params.length; i++) {
                    if (args[i] != null && !wrap(params[i]).isAssignableFrom(args[i].getClass())) {
                        matches = false;
                        break;
                    }
                }
                if (matches) return method;
            }
        }
        throw new NoSuchMethodException(type.getName() + "." + name);
    }

    private static Object readField(Object target, String name) throws ReflectiveOperationException {
        Field field = findField(target.getClass(), name);
        return field.get(target);
    }

    private static Field findField(Class<?> type, String name) throws NoSuchFieldException {
        for (Class<?> cursor = type; cursor != null; cursor = cursor.getSuperclass()) {
            try {
                Field field = cursor.getDeclaredField(name);
                field.setAccessible(true);
                return field;
            }
            catch (NoSuchFieldException ignored) {
            }
        }
        throw new NoSuchFieldException(type.getName() + "." + name);
    }

    private static Class<?> wrap(Class<?> type) {
        if (!type.isPrimitive()) return type;
        if (type == int.class) return Integer.class;
        if (type == long.class) return Long.class;
        if (type == double.class) return Double.class;
        if (type == float.class) return Float.class;
        if (type == boolean.class) return Boolean.class;
        if (type == byte.class) return Byte.class;
        if (type == short.class) return Short.class;
        if (type == char.class) return Character.class;
        return type;
    }

    private static Number numberValue(Object value) {
        if (value instanceof Number number) return number;
        throw new IllegalArgumentException("expected number, got " + value);
    }

    private static boolean booleanValue(Object value) {
        if (value instanceof Boolean bool) return bool;
        throw new IllegalArgumentException("expected boolean, got " + value);
    }

    private static Collection<?> collectionValue(Object value) {
        if (value instanceof Collection<?> collection) return collection;
        throw new IllegalArgumentException("expected collection, got " + value);
    }

    private static String effectCategory(String trait) {
        if (Set.of("tank", "protection", "adaptive", "dementor", "dispell", "reflect", "arena", "undying", "teleport", "repelling")
                .contains(path(trait))) return "DEFENCE_OR_DAMAGE_ADMISSION";
        if (Set.of("regenerate").contains(path(trait))) return "HEALING";
        if (Set.of("speedy", "gravity", "moonwalk", "pulling", "counter_strike").contains(path(trait))) return "MOVEMENT_OR_CONTROL";
        if (Set.of("corrosion", "erosion", "reprint", "ragnarok").contains(path(trait))) return "EQUIPMENT";
        if (Set.of("shulker", "grenade", "master", "split", "growth").contains(path(trait))) return "SPAWNING_MINIONS_OR_ENTITY_STATE";
        if (Set.of("fiery", "drain", "killer_aura", "weakness", "slowness", "poison", "wither", "levitation",
                "blindness", "nausea", "soul_burner", "freezing", "cursed").contains(path(trait))) return "OFFENCE_OR_STATUS";
        return "OTHER";
    }

    private static String path(String id) {
        int index = id.indexOf(':');
        return index < 0 ? id : id.substring(index + 1);
    }

    private static JsonObject vector(Vec3 value) {
        JsonObject json = new JsonObject();
        json.addProperty("x", value.x);
        json.addProperty("y", value.y);
        json.addProperty("z", value.z);
        return json;
    }

    private enum Phase {
        START, WAIT_ATTACHMENT, WAIT_POST_INIT, FORCED_RUN, DONE
    }

    private record BossSpec(ResourceLocation id, int minLevel, int maxLevel) {
    }

    private record ResourceState(double spiritualHealth, double maxSpiritualHealth, double magicules, double aura) {
        private static final ResourceState ZERO = new ResourceState(0.0D, 0.0D, 0.0D, 0.0D);

        JsonObject toJson() {
            JsonObject json = new JsonObject();
            json.addProperty("spiritual_health", spiritualHealth);
            json.addProperty("max_spiritual_health", maxSpiritualHealth);
            json.addProperty("magicules", magicules);
            json.addProperty("aura", aura);
            return json;
        }
    }

    private record ForcedCase(Object trait, String id, int rank, int nativeMaxRank) {
    }

    private record AttributeState(double maxHealth, double armor, double toughness, double movementSpeed) {
        private static final AttributeState ZERO = new AttributeState(0.0D, 0.0D, 0.0D, 0.0D);

        JsonObject toJson() {
            JsonObject json = new JsonObject();
            json.addProperty("max_HP", maxHealth);
            json.addProperty("armor", armor);
            json.addProperty("toughness", toughness);
            json.addProperty("movement_speed", movementSpeed);
            return json;
        }
    }

    private static final class ForcedObservation {
        final ForcedCase spec;
        final boolean naturallyLegal;
        final AttributeState beforeInitialization;
        final ResourceState targetInitialResources;
        final ResourceState playerInitialResources;
        final JsonObject initialNearbyEntities;
        final JsonArray events = new JsonArray();
        final Set<String> canceledActions = new LinkedHashSet<>();
        final Set<String> targetDamagePostActions = new LinkedHashSet<>();
        final Set<String> canceledTargetDamageKeys = new LinkedHashSet<>();
        final Set<String> targetDamagePostKeys = new LinkedHashSet<>();
        AttributeState afterInitialization = AttributeState.ZERO;
        AttributeState afterRun = AttributeState.ZERO;
        ResourceState targetFinalResources = ResourceState.ZERO;
        ResourceState playerFinalResources = ResourceState.ZERO;
        JsonArray targetEffectsAtStart = new JsonArray();
        JsonArray victimEffects = new JsonArray();
        JsonArray victimInitialEquipment = new JsonArray();
        JsonArray playerInitialEquipment = new JsonArray();
        JsonArray playerEffects = new JsonArray();
        JsonArray playerEquipment = new JsonArray();
        JsonArray victimEquipment = new JsonArray();
        JsonArray auraVictimEffects = new JsonArray();
        JsonObject finalNearbyEntities = new JsonObject();
        Vec3 victimMotion = Vec3.ZERO;
        Vec3 auraVictimMotion = Vec3.ZERO;
        Vec3 targetMotion = Vec3.ZERO;
        Vec3 targetFinalPosition = Vec3.ZERO;
        double regenWoundedHealth;
        double regenObservedHealth;
        double targetFinalHealth;
        double victimFinalHealth;
        double playerFinalHealth;
        int victimFireTicks;
        boolean targetInvisible;
        boolean targetAlive;
        boolean lethalTransitionExercised;
        boolean magicS7FixtureActive;
        boolean anyIncomingCanceled;
        boolean anyTargetDamagePost;
        boolean masterProtected;
        boolean tensuraScalingMarker;

        ForcedObservation(ForcedCase spec, boolean naturallyLegal, AttributeState beforeInitialization,
                ResourceState targetInitialResources, ResourceState playerInitialResources,
                JsonObject initialNearbyEntities) {
            this.spec = spec;
            this.naturallyLegal = naturallyLegal;
            this.beforeInitialization = beforeInitialization;
            this.targetInitialResources = targetInitialResources;
            this.playerInitialResources = playerInitialResources;
            this.initialNearbyEntities = initialNearbyEntities;
        }

        JsonObject toJson(ResourceLocation boss) {
            JsonObject json = new JsonObject();
            json.addProperty("evidence_class", naturallyLegal ? "FORCED_DIAGNOSTIC" : "FORCED_ILLEGAL_DIAGNOSTIC");
            json.addProperty("compatibility_evidence_only", true);
            json.addProperty("balance_evidence_allowed", false);
            json.addProperty("trait_id", spec.id);
            json.addProperty("effect_category", effectCategory(spec.id));
            json.addProperty("tested_boss", boss.toString());
            json.addProperty("requested_level", 1000);
            json.addProperty("attached_level", 1000);
            json.addProperty("rank", spec.rank);
            json.addProperty("native_max_rank", spec.nativeMaxRank);
            json.addProperty("legal_for_tested_entity", naturallyLegal);
            json.addProperty("forced_attachment_used", true);
            json.addProperty("real_royal_bow", ROYAL_BOW.toString());
            json.addProperty("real_royal_arrow", ROYAL_ARROW.toString());
            json.addProperty("royal_arrow_mark_enabled", false);
            json.addProperty("APO_profile", "NONE");
            json.addProperty("TNO_probes", "physical Royal Arrow repeats, direct player-to-boss physical control, boss-sourced physical controls, Magic Weapon Native, temporary S7 coefficient fixture");
            json.addProperty("production_combat_mutated", false);
            json.add("attributes_before_forced_trait", beforeInitialization.toJson());
            json.add("attributes_after_forced_trait", afterInitialization.toJson());
            json.add("attributes_after_runtime_probe", afterRun.toJson());
            json.add("target_initial_resources", targetInitialResources.toJson());
            json.add("target_final_resources", targetFinalResources.toJson());
            json.add("player_initial_resources", playerInitialResources.toJson());
            json.add("player_final_resources", playerFinalResources.toJson());
            json.addProperty("royal_bow_user_final_HP", playerFinalHealth);
            json.add("royal_bow_user_effects", playerEffects);
            json.add("royal_bow_user_equipment_before", playerInitialEquipment);
            json.add("royal_bow_user_equipment_after", playerEquipment);
            json.addProperty("regen_wounded_HP", regenWoundedHealth);
            json.addProperty("regen_observed_HP_at_25_ticks", regenObservedHealth);
            json.addProperty("target_final_HP", targetFinalHealth);
            json.addProperty("target_alive_after_probe", targetAlive);
            json.addProperty("lethal_transition_exercised", lethalTransitionExercised);
            json.addProperty("target_invisible_after_initialization", targetInvisible);
            json.add("target_effects_after_initialization", targetEffectsAtStart);
            json.addProperty("probe_entity", "minecraft:zombie");
            json.addProperty("probe_entity_final_HP", victimFinalHealth);
            json.add("probe_entity_effects", victimEffects);
            json.add("probe_entity_equipment_before", victimInitialEquipment);
            json.add("probe_entity_equipment", victimEquipment);
            json.addProperty("probe_entity_fire_ticks", victimFireTicks);
            json.add("probe_entity_motion", vector(victimMotion));
            json.addProperty("aura_probe_entity", "minecraft:armor_stand");
            json.add("aura_probe_effects", auraVictimEffects);
            json.add("aura_probe_motion", vector(auraVictimMotion));
            json.add("boss_motion", vector(targetMotion));
            json.add("boss_final_position", vector(targetFinalPosition));
            json.add("nearby_entity_types_before_probe", initialNearbyEntities);
            json.add("nearby_entity_types_after_probe", finalNearbyEntities);
            json.addProperty("master_protection_active", masterProtected);
            json.addProperty("tensura_l2h_scaling_marker", tensuraScalingMarker);
            json.add("damage_event_trace", events);
            json.add("canceled_actions", strings(canceledActions));
            json.add("target_damage_post_actions", strings(targetDamagePostActions));
            Set<String> bypass = new LinkedHashSet<>(canceledTargetDamageKeys);
            bypass.retainAll(targetDamagePostKeys);
            json.add("unexpected_L2_bypass_damage_keys", strings(bypass));
            json.addProperty("unexpected_L2_bypass", !bypass.isEmpty());
            json.addProperty("runtime_probe_completed", true);
            json.addProperty("terminal_classification", "PENDING_CROSS_TRAIT_VALIDATION");
            return json;
        }
    }
}
