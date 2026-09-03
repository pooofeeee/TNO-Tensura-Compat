package com.tno.tensuracompat.debug;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.mojang.authlib.GameProfile;
import com.mojang.logging.LogUtils;
import dev.architectury.event.EventResult;
import io.github.manasmods.tensura.registry.attribute.TensuraAttributes;
import io.github.manasmods.tensura.registry.item.misc.TensuraDataComponents;
import io.github.manasmods.tensura.storage.TensuraStorages;
import io.github.manasmods.tensura.util.EnergyHelper;
import com.tno.tensuracompat.core.stage.ProductionStageScaling;
import com.tno.tensuracompat.core.stage.SeveranceStageScaling;
import net.minecraft.core.Holder;
import net.minecraft.core.Registry;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.tags.TagKey;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.item.BowItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.component.BundleContents;
import net.minecraft.world.item.component.CustomData;
import net.minecraft.world.item.enchantment.Enchantment;
import net.minecraft.world.item.enchantment.EnchantmentHelper;
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
import java.util.IdentityHashMap;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Stream;

/**
 * Development-only Suite B/C runner and Phase 6 endgame observer. Suite B/C
 * retain their locked fixtures; the explicitly gated Phase 6 mode instead uses
 * real native Gear EP and observes the existing production Stage integration.
 * Production gameplay is untouched.
 */
public final class Phase5FSuiteBBenchmark {
    private static final Logger LOGGER = LogUtils.getLogger();
    private static final Gson GSON = new GsonBuilder().disableHtmlEscaping().create();
    private static final boolean SUITE_C = Boolean.getBoolean("tno.phase5f.suiteC");
    private static final boolean ENDGAME_RESEARCH = Boolean.getBoolean("tno.phase6.endgameResearch");
    private static final String MARKER = ENDGAME_RESEARCH ? "TNO_PHASE6_ENDGAME_RESEARCH"
            : SUITE_C ? "TNO_PHASE5F_SUITE_C" : "TNO_PHASE5F_SUITE_B";
    private static final String TARGET_TAG = ENDGAME_RESEARCH ? "tno_phase6_endgame_research_target"
            : SUITE_C ? "tno_phase5f_suite_c_target" : "tno_phase5f_suite_b_target";
    private static final String APO_PROFILE = "ANCIENT_SINGLE_PROSPEROUS_SPECTRAL";
    private static final String SCALE_TAG = "l2_tensura_scaled";
    private static final String L2_MISCS = "dev.xkmc.l2hostility.init.registrate.LHMiscs";
    private static final String L2_TRAITS = "dev.xkmc.l2hostility.init.registrate.LHTraits";
    private static final boolean ENDGAME = SUITE_C && Boolean.getBoolean("tno.phase5f.suiteCEndgame");
    private static final boolean STRONGEST_LEGAL_PROFILE = ENDGAME || ENDGAME_RESEARCH;
    private static final ResourceLocation ROYAL_BOW = id("royalvariations", "royal_bow");
    private static final ResourceLocation ROYAL_ARROW = id("royalvariations", "royal_arrow");
    private static final ResourceLocation EARTH_CORE = id("tensura", "element_core_earth");
    private static final double SEVERANCE_NATIVE_ATTACK_BONUS = 3.0D;
    private static final int MAX_SHOTS = Integer.getInteger(
            ENDGAME_RESEARCH ? "tno.phase6.endgameShots"
                    : SUITE_C ? "tno.phase5f.suiteCShots" : "tno.phase5f.suiteBShots", 10);
    private static final int WINDOW_TICKS = Integer.getInteger(
            ENDGAME_RESEARCH ? "tno.phase6.endgameTicks"
                    : SUITE_C ? "tno.phase5f.suiteCTicks" : "tno.phase5f.suiteBTicks", 200);
    private static final boolean DIAGNOSTIC = Boolean.getBoolean(
            SUITE_C ? "tno.phase5f.suiteCDiagnostic" : "tno.phase5f.suiteBDiagnostic");
    private static final double TEST_X = 0.5D;
    private static final double TEST_Y = 240.0D;
    private static final double TARGET_Z = 20.5D;

    private static final List<ResourceLocation> APO_ATTRIBUTES = List.of(
            id("apothic_attributes", "arrow_damage"), id("apothic_attributes", "arrow_velocity"),
            id("apothic_attributes", "armor_pierce"), id("apothic_attributes", "armor_shred"),
            id("apothic_attributes", "prot_pierce"), id("apothic_attributes", "prot_shred"),
            id("apothic_attributes", "crit_chance"), id("apothic_attributes", "crit_damage"),
            id("apothic_attributes", "draw_speed")
    );
    private static final Set<String> OFFICIAL_AFFIXES = Set.of(
            "ancientreforging:ranged/attribute/elven",
            "ancientreforging:ranged/attribute/streamlined",
            "ancientreforging:melee/attribute/lacerating",
            "ancientreforging:melee/attribute/intricate",
            "ancientreforging:melee/attribute/piercing",
            "ancientreforging:ranged/mob_effect/acidic",
            "ancientreforging:ranged/mob_effect/deathbound",
            "ancientreforging:ranged/mob_effect/ivy_laced",
            "ancientreforging:ranged/enchantment/prosperous",
            "ancientreforging:ranged/spectral"
    );
    private static final Map<String, Integer> OFFICIAL_GEMS = Map.of(
            "apotheosis:core/combatant", 1,
            "apotheosis:core/breach", 1,
            "apotheosis:core/lightning", 1,
            "apotheosis:core/warlord", 2
    );
    private static final Map<String, Double> OFFICIAL_APO_ATTRIBUTES = Map.of(
            "apothic_attributes:arrow_damage", 3.0224999815D,
            "apothic_attributes:arrow_velocity", 2.9449999630D,
            "apothic_attributes:armor_pierce", 31.0D,
            "apothic_attributes:prot_pierce", 15.0D,
            "apothic_attributes:crit_chance", 1.5300000191D,
            "apothic_attributes:crit_damage", 5.8799999714D,
            "apothic_attributes:draw_speed", 1.0D
    );
    private static final List<BossSpec> BOSSES = List.of(
            boss("tensura_neb", "luminous_valentine", 130, 300, true),
            boss("tensura", "hinata_sakaguchi", 120, 280, true),
            boss("tensura", "gazel_dwargo", 110, 260, true),
            boss("tensura", "orc_disaster", 100, 250, false),
            boss("tensura", "elemental_colossus", 75, 150, false),
            boss("tensura_neb", "carrion", 90, 210, false),
            boss("tensura_neb", "rimuru_ogre_fight", 85, 250, false)
    );
    private static final List<Stage> STAGES = List.of(
            new Stage("Native", null, 0.00D, 0.00D),
            new Stage("S0", 1_000L, 0.05D, 0.00D),
            new Stage("S1", 41_500L, 0.10D, 0.00D),
            new Stage("S2", 207_500L, 0.15D, 0.00D),
            new Stage("S3", 830_000L, 0.20D, 0.00D),
            new Stage("S4", 1_245_000L, 0.25D, 0.00D),
            new Stage("S5", 1_660_000L, 0.30D, 0.25D),
            new Stage("S6", 2_075_000L, 0.35D, 0.50D),
            new Stage("S7", 2_490_000L, 0.40D, 1.00D)
    );
    private static final Set<String> DEFENSIVE_TRAITS = Set.of(
            "l2hostility:adaptive", "l2hostility:arena", "l2hostility:dementor",
            "l2hostility:dispell", "l2hostility:protection", "l2hostility:regenerate",
            "l2hostility:reflect", "l2hostility:repelling", "l2hostility:tank",
            "l2hostility:undying", "l2hostility:ragnarok"
    );
    private static final Map<String, Map<String, Integer>> ACCEPTED_ENDGAME_PROFILES = Map.of(
            "tensura_neb:luminous_valentine", Map.of(
                    "l2hostility:adaptive", 5, "l2hostility:dementor", 1,
                    "l2hostility:dispell", 3, "l2hostility:killer_aura", 1,
                    "l2hostility:reflect", 2, "l2hostility:regenerate", 5,
                    "l2hostility:soul_burner", 2, "l2hostility:tank", 5),
            "tensura:hinata_sakaguchi", Map.of(
                    "l2hostility:adaptive", 5, "l2hostility:dementor", 1,
                    "l2hostility:dispell", 2, "l2hostility:reflect", 2,
                    "l2hostility:regenerate", 5, "l2hostility:tank", 5),
            "tensura:gazel_dwargo", Map.of(
                    "l2hostility:adaptive", 5, "l2hostility:dementor", 1,
                    "l2hostility:dispell", 2, "l2hostility:reflect", 1,
                    "l2hostility:regenerate", 5, "l2hostility:tank", 5),
            "tensura:orc_disaster", Map.of(
                    "l2hostility:adaptive", 5, "l2hostility:dementor", 1,
                    "l2hostility:dispell", 2, "l2hostility:drain", 2,
                    "l2hostility:regenerate", 5, "l2hostility:tank", 5,
                    "l2hostility:wither", 1),
            "tensura:elemental_colossus", Map.of(
                    "l2hostility:adaptive", 5, "l2hostility:dementor", 1,
                    "l2hostility:dispell", 2, "l2hostility:regenerate", 5,
                    "l2hostility:speedy", 2, "l2hostility:tank", 5),
            "tensura_neb:carrion", Map.of(
                    "l2hostility:adaptive", 5, "l2hostility:dementor", 1,
                    "l2hostility:dispell", 2, "l2hostility:reflect", 1,
                    "l2hostility:regenerate", 5, "l2hostility:speedy", 1,
                    "l2hostility:tank", 5),
            "tensura_neb:rimuru_ogre_fight", Map.of(
                    "l2hostility:adaptive", 5, "l2hostility:dementor", 1,
                    "l2hostility:dispell", 2, "l2hostility:drain", 2,
                    "l2hostility:regenerate", 5, "l2hostility:tank", 5)
    );
    private static final Map<Integer, Map<String, Integer>> ACCEPTED_ORC_ENDGAME_PROFILES = Map.of(
            300, Map.of(
                    "l2hostility:dementor", 1, "l2hostility:drain", 2,
                    "l2hostility:regenerate", 2, "l2hostility:tank", 5,
                    "l2hostility:wither", 1),
            600, Map.of(
                    "l2hostility:adaptive", 3, "l2hostility:dementor", 1,
                    "l2hostility:drain", 2, "l2hostility:regenerate", 4,
                    "l2hostility:tank", 5, "l2hostility:wither", 1),
            800, Map.of(
                    "l2hostility:adaptive", 5, "l2hostility:dementor", 1,
                    "l2hostility:drain", 2, "l2hostility:regenerate", 5,
                    "l2hostility:tank", 5, "l2hostility:wither", 1),
            1000, Map.of(
                    "l2hostility:adaptive", 5, "l2hostility:dementor", 1,
                    "l2hostility:dispell", 2, "l2hostility:drain", 2,
                    "l2hostility:regenerate", 5, "l2hostility:tank", 5,
                    "l2hostility:wither", 1)
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
    private static boolean energyEventRegistered;

    private Phase5FSuiteBBenchmark() {
    }

    public static void onServerStarted(ServerStartedEvent event) {
        boolean suiteB = Boolean.getBoolean("tno.phase5f.suiteB");
        boolean suiteC = Boolean.getBoolean("tno.phase5f.suiteC");
        boolean endgameResearch = Boolean.getBoolean("tno.phase6.endgameResearch");
        if (FMLEnvironment.production || (!suiteB && !suiteC && !endgameResearch) || active != null) return;
        try {
            if ((suiteB ? 1 : 0) + (suiteC ? 1 : 0) + (endgameResearch ? 1 : 0) != 1) {
                throw new IllegalStateException("Suite B, Suite C, and Phase 6 endgame research are mutually exclusive");
            }
            requireMods();
            active = new Session(event.getServer());
            LOGGER.info("{} automatic benchmark started", MARKER);
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
            LOGGER.error("{} case failure", MARKER, throwable);
            session.failCurrent(throwable);
        }
    }

    public static void onIncomingHighest(LivingIncomingDamageEvent event) {
        if (active != null) active.captureIncomingHighest(event);
    }

    public static void onIncomingLowest(LivingIncomingDamageEvent event) {
        if (active != null) active.captureIncomingLowest(event);
    }

    public static void onIncomingAfterCrit(LivingIncomingDamageEvent event) {
        if (active != null) active.captureIncomingAfterCrit(event);
    }

    public static void onDamagePre(LivingDamageEvent.Pre event) {
        if (active != null) active.captureDamagePre(event);
    }

    public static void onDamagePost(LivingDamageEvent.Post event) {
        if (active != null) active.captureDamagePost(event);
    }

    public static void registerTensuraEvents() {
        if (energyEventRegistered) return;
        try {
            Class<?> listenerType = Class.forName("io.github.manasmods.tensura.event.TensuraEntityEvents$EnergyDrainEvent");
            Object listener = Proxy.newProxyInstance(listenerType.getClassLoader(), new Class<?>[]{listenerType},
                    (proxy, method, args) -> {
                        if (method.getDeclaringClass() == Object.class) {
                            return switch (method.getName()) {
                                case "toString" -> "TNO Phase 5F Energy Drain probe";
                                case "hashCode" -> System.identityHashCode(proxy);
                                case "equals" -> proxy == args[0];
                                default -> null;
                            };
                        }
                        Session session = active;
                        if (session != null && method.getName().equals("drain")) {
                            session.captureEnergyDrain((LivingEntity) args[0], (Entity) args[1],
                                    args[2], args[3], args[4], args[5]);
                        }
                        return EventResult.pass();
                    });
            Object event = staticField("io.github.manasmods.tensura.event.TensuraEntityEvents", "ENERGY_DRAIN_EVENT");
            invoke(event, "register", listener);
            energyEventRegistered = true;
        }
        catch (ReflectiveOperationException exception) {
            throw new IllegalStateException("could not register Phase 5F native Energy Drain probe", exception);
        }
    }

    private static void requireMods() {
        List<String> required = SUITE_C
                ? List.of("royalvariations", "l2hostility", "apotheosis", "apothic_attributes",
                        "ancientreforging", "apothicnightmares")
                : List.of("royalvariations", "l2hostility");
        for (String mod : required) {
            if (!ModList.get().isLoaded(mod)) {
                throw new IllegalStateException("required " + (ENDGAME_RESEARCH ? "Phase 6 endgame research"
                        : "Suite " + (SUITE_C ? "C" : "B")) + " runtime mod absent: " + mod);
            }
        }
    }

    private static final class Session {
        private final MinecraftServer server;
        private final ServerLevel level;
        private final Family family;
        private final ItemStack benchmarkBow;
        private final Item royalArrow;
        private final List<CaseSpec> cases;
        private final List<JsonObject> summaries = new ArrayList<>();
        private final Map<LivingIncomingDamageEvent, FamilyProbe> familyProbes = new IdentityHashMap<>();
        private final Map<LivingIncomingDamageEvent, Float> beforeCrit = new IdentityHashMap<>();
        private FakePlayer player;
        private LivingEntity target;
        private Object l2Cap;
        private CaseResult result;
        private HitRecord currentHit;
        private CompoundTag profileTemplate;
        private ProfileKey templateKey;
        private String templateTraits;
        private Phase phase = Phase.SPAWN;
        private int caseIndex;
        private int phaseTick;
        private int shotsReleased;
        private long runStartTick;
        private long nextShotTick;
        private boolean complete;
        private boolean catalogLogged;
        private JsonObject apoInspection;

        Session(MinecraftServer server) {
            this.server = server;
            this.level = server.overworld();
            this.family = Family.parse(System.getProperty(
                    ENDGAME_RESEARCH ? "tno.phase6.endgameFamily"
                            : SUITE_C ? "tno.phase5f.suiteCFamily" : "tno.phase5f.suiteBFamily", ""));
            this.benchmarkBow = buildBenchmarkBow(server, family);
            this.royalArrow = requiredItem(ROYAL_ARROW);
            this.cases = buildCases(System.getProperty(
                    ENDGAME_RESEARCH ? "tno.phase6.endgameBoss"
                            : SUITE_C ? "tno.phase5f.suiteCBoss" : "tno.phase5f.suiteBBoss", ""));
            if (cases.isEmpty()) throw new IllegalStateException("Suite " + (SUITE_C ? "C" : "B") + " boss filter matched no targets");
            if (ENDGAME_RESEARCH && cases.stream().anyMatch(spec ->
                    !spec.boss.id.equals(id("tensura", "orc_disaster")))) {
                throw new IllegalStateException("Phase 6 endgame research is locked to the accepted Orc Disaster positive-control target");
            }
            if (!SUITE_C) assertTnoOnlyStack(benchmarkBow);
            cleanupTestArea();
            if (ENDGAME_RESEARCH || SUITE_C && Boolean.getBoolean("tno.phase5f.suiteCFastTicks")) {
                runCommand("tick sprint 10000000");
            }
            if (!SUITE_C) {
                logCatalog();
                catalogLogged = true;
            }
        }

        void tick() throws ReflectiveOperationException {
            stabilize();
            if (phase == Phase.RUN && currentHit != null) currentHit.observe(target, player);
            switch (phase) {
                case SPAWN -> spawnCase();
                case WAIT_ATTACHMENT -> waitForAttachment();
                case CONFIGURE_LEVEL -> configureLevel();
                case WAIT_SCALING -> waitForScaling();
                case WAIT_CLONE -> waitForClone();
                case RUN -> runCase();
                case FINISH -> finishCase();
                case DONE -> {
                    cleanupCase();
                    complete = true;
                }
            }
        }

        void failCurrent(Throwable throwable) {
            JsonObject error = baseCaseJson();
            error.addProperty("status", "error");
            error.addProperty("error", summarize(throwable));
            log("case_error", error);
            cleanupCase();
            caseIndex++;
            phaseTick = 0;
            phase = Phase.SPAWN;
        }

        private void spawnCase() {
            if (caseIndex >= cases.size()) {
                JsonObject suite = new JsonObject();
                suite.addProperty("status", "complete");
                suite.addProperty("case_count", summaries.size());
                suite.addProperty("requested_case_count", cases.size());
                JsonArray values = new JsonArray();
                summaries.forEach(values::add);
                suite.add("case_summaries", values);
                log("suite_result", suite);
                phase = Phase.DONE;
                return;
            }

            cleanupCase();
            CaseSpec spec = currentCase();
            player = createPlayer(caseIndex);
            equipBenchmarkBow();
            if (!catalogLogged) {
                logCatalog();
                catalogLogged = true;
            }
            target = createTarget(spec.boss);
            if (profileTemplate != null && spec.profileKey().equals(templateKey)) {
                CompoundTag copy = profileTemplate.copy();
                target.load(copy);
                target.setPos(TEST_X, TEST_Y, TARGET_Z);
                target.addTag(TARGET_TAG);
                level.addFreshEntity(target);
                phase = Phase.WAIT_CLONE;
            }
            else {
                profileTemplate = null;
                templateKey = null;
                templateTraits = null;
                target.setPos(TEST_X, TEST_Y, TARGET_Z);
                target.setNoGravity(true);
                target.setSilent(true);
                target.addTag(TARGET_TAG);
                level.addFreshEntity(target);
                phase = Phase.WAIT_ATTACHMENT;
            }
            phaseTick = 0;
        }

        private LivingEntity createTarget(BossSpec boss) {
            Entity created = BuiltInRegistries.ENTITY_TYPE.get(boss.id).create(level);
            if (created instanceof LivingEntity living) return living;
            throw new IllegalStateException("could not create living target " + boss.id);
        }

        private void waitForAttachment() throws ReflectiveOperationException {
            if (++phaseTick < 5) return;
            Object type = invoke(staticField(L2_MISCS, "MOB"), "type");
            if (!booleanValue(invoke(type, "isProper", target))) {
                throw new IllegalStateException("L2 attachment predicate rejected " + currentCase().boss.id);
            }
            l2Cap = invoke(type, "getOrCreate", target);
            phase = Phase.CONFIGURE_LEVEL;
        }

        private void configureLevel() throws ReflectiveOperationException {
            CaseSpec spec = currentCase();
            Object config = invoke(l2Cap, "getConfigCache", target);
            Field maxLevel = findField(config.getClass(), "maxLevel");
            int originalMax = maxLevel.getInt(config);
            try {
                if ((spec.mode == LevelMode.STRESS || spec.mode == LevelMode.ENDGAME_TARGET)
                        && spec.level > originalMax) maxLevel.setInt(config, spec.level);
                invoke(l2Cap, "reinit", target, spec.level, false);
                if (STRONGEST_LEGAL_PROFILE) installAcceptedEndgameProfile();
            }
            finally {
                maxLevel.setInt(config, originalMax);
            }
            assertAttachment();
            invoke(l2Cap, "syncToClient", target);
            removeDatapackScaling();
            phaseTick = 0;
            phase = Phase.WAIT_SCALING;
        }

        private void installAcceptedEndgameProfile() throws ReflectiveOperationException {
            Map<String, Integer> expected = ENDGAME_RESEARCH
                    ? ACCEPTED_ORC_ENDGAME_PROFILES.get(currentCase().level)
                    : ACCEPTED_ENDGAME_PROFILES.get(currentCase().boss.id.toString());
            if (expected == null || !ENDGAME_RESEARCH && currentCase().level != 1000) {
                throw new IllegalStateException("missing accepted endgame profile for "
                        + currentCase().boss.id + " at Lv" + currentCase().level);
            }

            Object rawTraits = readField(l2Cap, "traits");
            if (!(rawTraits instanceof Map<?, ?> rawMap)) {
                throw new IllegalStateException("L2 endgame trait map is not observable");
            }
            @SuppressWarnings("unchecked")
            Map<Object, Integer> traitMap = (Map<Object, Integer>) rawMap;
            for (Map.Entry<Object, Integer> entry : new ArrayList<>(traitMap.entrySet())) {
                invoke(entry.getKey(), "initialize", target, 0);
                invoke(entry.getKey(), "postInit", target, 0);
            }
            traitMap.clear();
            Object data = readField(l2Cap, "data");
            if (!(data instanceof Map<?, ?> traitData)) {
                throw new IllegalStateException("L2 endgame trait state data is not observable");
            }
            traitData.clear();
            clearPendingTraitChanges();

            Map<String, Object> byId = new LinkedHashMap<>();
            Object registry = invoke(staticField(L2_TRAITS, "TRAITS"), "get");
            if (registry instanceof Iterable<?> iterable) {
                iterable.forEach(trait -> byId.put(traitId(trait), trait));
            }
            else if (invoke(registry, "stream") instanceof Stream<?> stream) {
                stream.forEach(trait -> byId.put(traitId(trait), trait));
            }
            for (Map.Entry<String, Integer> entry : expected.entrySet()) {
                Object trait = byId.get(entry.getKey());
                if (trait == null) throw new IllegalStateException("accepted endgame trait absent: " + entry.getKey());
                traitMap.put(trait, entry.getValue());
                invoke(trait, "initialize", target, entry.getValue());
            }
            clearPendingTraitChanges();
            JsonObject expectedRanks = new JsonObject();
            expected.entrySet().stream().sorted(Map.Entry.comparingByKey())
                    .forEach(entry -> expectedRanks.addProperty(entry.getKey(), entry.getValue()));
            JsonObject actualRanks = traitRanks(readTraits(l2Cap));
            if (!actualRanks.equals(expectedRanks)) {
                throw new IllegalStateException("accepted endgame profile mismatch: expected="
                        + expectedRanks + " actual=" + actualRanks);
            }
        }

        private void clearPendingTraitChanges() throws ReflectiveOperationException {
            Object pending = readField(l2Cap, "pending");
            if (!(pending instanceof Collection<?> pendingChanges)) {
                throw new IllegalStateException("L2 pending endgame trait changes are not observable");
            }
            pendingChanges.clear();
        }

        private void removeDatapackScaling() {
            runCommand("attribute @e[tag=" + TARGET_TAG + ",limit=1] tensura:max_spiritual_health modifier remove tensura_l2h:l2_shp_scale");
            runCommand("attribute @e[tag=" + TARGET_TAG + ",limit=1] tensura:max_magicule modifier remove tensura_l2h:l2_magic_scale");
            runCommand("attribute @e[tag=" + TARGET_TAG + ",limit=1] tensura:max_aura modifier remove tensura_l2h:l2_aura_scale");
            target.removeTag(SCALE_TAG);
        }

        private void waitForScaling() throws ReflectiveOperationException {
            if (++phaseTick < 5 || !target.getTags().contains(SCALE_TAG)) {
                if (phaseTick > 60) throw new IllegalStateException("datapack scaling marker was not reapplied");
                return;
            }
            assertAttachment();
            if (STRONGEST_LEGAL_PROFILE) {
                // Reapply after the delayed datapack/L2 initialization window.
                // Native reinit may still have pending generated-trait changes
                // during those ticks; accepted evidence requires the exact legal
                // constructed profile, not a mixture with that discarded roll.
                installAcceptedEndgameProfile();
                invoke(l2Cap, "syncToClient", target);
            }
            resetActors();
            profileTemplate = new CompoundTag();
            target.saveWithoutId(profileTemplate);
            profileTemplate.remove("UUID");
            profileTemplate.remove("Pos");
            profileTemplate.remove("Motion");
            profileTemplate.remove("Rotation");
            templateKey = currentCase().profileKey();
            templateTraits = GSON.toJson(readTraits(l2Cap));
            beginRun(!STRONGEST_LEGAL_PROFILE);
        }

        private void waitForClone() throws ReflectiveOperationException {
            if (++phaseTick < 5) return;
            Object type = invoke(staticField(L2_MISCS, "MOB"), "type");
            l2Cap = invoke(type, "getOrCreate", target);
            assertAttachment();
            if (!target.getTags().contains(SCALE_TAG)) throw new IllegalStateException("profile clone lost datapack scaling marker");
            String actualTraits = GSON.toJson(readTraits(l2Cap));
            if (!actualTraits.equals(templateTraits)) throw new IllegalStateException("profile clone changed generated traits");
            resetActors();
            beginRun(false);
        }

        private void assertAttachment() throws ReflectiveOperationException {
            int actual = numberValue(invoke(l2Cap, "getLevel")).intValue();
            if (actual != currentCase().level) throw new IllegalStateException("stored L2 level " + actual + " != requested " + currentCase().level);
            if (!booleanValue(invoke(l2Cap, "isInitialized"))) throw new IllegalStateException("native L2 attachment is not initialized");
        }

        private void resetActors() {
            fillResources(target);
            fillResources(player);
            if (family == Family.ENERGY) {
                var existence = TensuraStorages.getExistenceFrom(player);
                existence.setMagicule(0.0D);
                existence.setAura(0.0D);
            }
            target.setHealth(target.getMaxHealth());
            target.setAbsorptionAmount(0.0F);
            target.invulnerableTime = 0;
            player.setHealth(player.getMaxHealth());
            player.setAbsorptionAmount(0.0F);
            player.invulnerableTime = 0;
            familyProbes.clear();
            beforeCrit.clear();
            clearArrows();
        }

        private void beginRun(boolean nativeProfileSource) throws ReflectiveOperationException {
            result = new CaseResult(currentCase(), target, player, l2Cap, nativeProfileSource);
            shotsReleased = 0;
            currentHit = null;
            runStartTick = server.getTickCount();
            nextShotTick = runStartTick;
            phase = Phase.RUN;
            log("case_start", result.caseJson());
        }

        private void runCase() {
            long now = server.getTickCount();
            int elapsed = (int) (now - runStartTick);
            if (currentHit != null && now >= nextShotTick && shotsReleased < MAX_SHOTS) closeCurrentHit(elapsed);

            boolean targetDead = target == null || target.isRemoved() || target.isDeadOrDying() || target.getHealth() <= 0.0F;
            boolean playerDead = player == null || player.isRemoved() || player.isDeadOrDying() || player.getHealth() <= 0.0F;
            if (targetDead || playerDead || elapsed >= WINDOW_TICKS) {
                if (currentHit != null) closeCurrentHit(elapsed);
                if (targetDead && result.ttk == null) {
                    result.ttk = elapsed;
                    result.htk = shotsReleased;
                }
                result.attackerDefeated = playerDead;
                result.elapsedTicks = Math.max(1, elapsed);
                phase = Phase.FINISH;
                return;
            }

            if (now >= nextShotTick && shotsReleased < MAX_SHOTS) {
                clearArrows();
                currentHit = new HitRecord(shotsReleased + 1, elapsed, target, player);
                fireFullDraw();
                shotsReleased++;
                nextShotTick = now + 20L;
            }
        }

        private void closeCurrentHit(int elapsed) {
            if (currentHit == null) return;
            currentHit.observe(target, player);
            currentHit.elapsedTicks = elapsed;
            result.hits.add(currentHit);
            currentHit = null;
        }

        private void finishCase() {
            result.shotsReleased = shotsReleased;
            result.finish(target);
            for (HitRecord hit : result.hits) log("row", result.rowJson(hit));
            JsonObject summary = result.summaryJson();
            summaries.add(summary.deepCopy());
            log("case_result", summary);
            cleanupCase();
            result = null;
            caseIndex++;
            phaseTick = 0;
            phase = Phase.SPAWN;
        }

        private void captureIncomingHighest(LivingIncomingDamageEvent event) {
            if (!runningTargetEvent(event)) return;
            String type = damageType(event.getSource());
            if (family.matchesDamageType(type)) {
                double eventAmount = event.getAmount();
                double raw = ENDGAME_RESEARCH
                        ? eventAmount / currentCase().stage.coefficient(family)
                        : family == Family.ELEMENTAL
                                ? currentHit.elementalNativeProjectileDamage : eventAmount;
                float scaled = ENDGAME_RESEARCH || family == Family.ELEMENTAL
                        ? (float) eventAmount
                        : (float) (raw * currentCase().stage.coefficient(family));
                double nativeAfterResistance = scaled > target.getHealth() * 0.5D ? scaled * 0.5D : 0.0D;
                boolean sourceBypass = !ENDGAME_RESEARCH && currentCase().stage.penetration > 0.0D
                        && result.matchingResistance && !result.matchingNullification;
                double stagedAmount = scaled;
                if (sourceBypass) {
                    stagedAmount = nativeAfterResistance + currentCase().stage.penetration
                            * (scaled - nativeAfterResistance);
                    try {
                        invoke(event.getSource(), "tensura$setResistanceBypassLevel", 1.0F);
                    }
                    catch (ReflectiveOperationException exception) {
                        throw new IllegalStateException("could not apply matching Tensura Resistance bypass level 1", exception);
                    }
                }
                if (!ENDGAME_RESEARCH) event.setAmount((float) stagedAmount);
                FamilyProbe probe = new FamilyProbe(raw, scaled, nativeAfterResistance, stagedAmount,
                        sourceBypass, sourceTags(event.getSource()), event.getSource().is(Tags.DamageTypes.IS_MAGIC));
                familyProbes.put(event, probe);
                currentHit.familyRaw += raw;
                currentHit.familyStageScaled += scaled;
                currentHit.familySourceIds.add(type);
                currentHit.familySourceTags.addAll(probe.tags);
                currentHit.l2Magic |= probe.l2Magic;
                currentHit.familyDamageEventCount++;
            }
            else if (isBenchmarkArrow(event.getSource())) {
                if (SUITE_C && !type.equals("minecraft:arrow")) {
                    throw new IllegalStateException("Suite C physical projectile source changed to " + type);
                }
                Entity direct = event.getSource().getDirectEntity();
                String projectileUuid = null;
                if (direct != null) {
                    projectileUuid = direct.getUUID().toString();
                    currentHit.hitProjectileUuids.add(projectileUuid);
                    currentHit.hitProjectileEntityIds.add(
                            BuiltInRegistries.ENTITY_TYPE.getKey(direct.getType()).toString());
                    currentHit.physicalEventsByProjectile.merge(projectileUuid, 1, Integer::sum);
                }
                currentHit.physicalCombinedOriginal += event.getOriginalAmount();
                currentHit.physicalOriginal += family == Family.SEVERANCE
                        ? currentHit.severanceBasePostByProjectile.getOrDefault(
                                projectileUuid, 0.0D)
                        : event.getOriginalAmount();
                currentHit.physicalIncoming += event.getAmount();
                currentHit.physicalSourceIds.add(type);
                currentHit.physicalSourceTags.addAll(sourceTags(event.getSource()));
                currentHit.physicalDamageEventCount++;
                if (family == Family.SEVERANCE) {
                    double basePost = currentHit.severanceBasePostByProjectile.getOrDefault(
                            projectileUuid, 0.0D);
                    SeveranceProjection projection = currentHit.severanceProjections.get(projectileUuid);
                    if (projection != null && currentHit.severanceAdmittedProjectileUuids.add(projectileUuid)) {
                        currentHit.severanceAdmittedProjectileCount++;
                        currentHit.severanceNativePreRound += projection.nativePre;
                        currentHit.severanceStagedPreRound += projection.stagedPre;
                        currentHit.severanceBasePostRound += projection.basePost;
                        currentHit.severanceNativePostRound += projection.nativePost;
                        currentHit.severanceStagedPostRound += projection.stagedPost;
                        currentHit.familyRaw += projection.nativePost - projection.basePost;
                        currentHit.familyStageScaled += projection.stagedPost - projection.basePost;
                    }
                    currentHit.familyAfterResistance += Math.max(0.0D,
                            event.getAmount() - basePost);
                    currentHit.familyAfterRecovery = currentHit.familyAfterResistance;
                    currentHit.l2Magic |= event.getSource().is(Tags.DamageTypes.IS_MAGIC);
                }
            }
            else {
                currentHit.dotIncoming += event.getAmount();
                currentHit.dotSourceIds.add(type);
                currentHit.dotDamageEventCount++;
            }
            if (SUITE_C) {
                currentHit.preCritDamage += event.getAmount();
                beforeCrit.put(event, event.getAmount());
            }
        }

        private void captureIncomingAfterCrit(LivingIncomingDamageEvent event) {
            if (!SUITE_C || phase != Phase.RUN || currentHit == null || event.getEntity() != target) return;
            Float before = beforeCrit.get(event);
            if (before != null && event.getAmount() > before + 0.001F && !currentHit.crit) {
                currentHit.crit = true;
                currentHit.critMultiplierEvents++;
                currentHit.critDamageSourceIds.add(damageType(event.getSource()));
            }
        }

        private void captureIncomingLowest(LivingIncomingDamageEvent event) {
            if (!runningTargetEvent(event)) return;
            Float preCrit = beforeCrit.remove(event);
            if (SUITE_C && preCrit != null && event.getAmount() > preCrit + 0.001F && !currentHit.crit) {
                currentHit.crit = true;
                currentHit.critMultiplierEvents++;
                currentHit.critDamageSourceIds.add(damageType(event.getSource()));
            }
            FamilyProbe probe = familyProbes.remove(event);
            if (probe == null) return;
            if (ENDGAME_RESEARCH) {
                double afterTensura = event.isCanceled() ? 0.0D : event.getAmount();
                currentHit.familyAfterResistance += afterTensura;
                currentHit.familyAfterRecovery += afterTensura;
                currentHit.familyCanceledBeforeRecovery |= event.isCanceled();
                currentHit.nullificationAuthoritative |= event.isCanceled() && result.matchingNullification;
                return;
            }
            double afterResistance = probe.sourceBypass ? probe.nativeAfterResistance
                    : event.isCanceled() ? 0.0D : event.getAmount();
            double afterRecovery = afterResistance;
            boolean wasCanceled = event.isCanceled();
            double penetration = currentCase().stage.penetration;
            if (probe.sourceBypass) {
                afterRecovery = event.isCanceled() ? 0.0D : event.getAmount();
            }
            else if (penetration > 0.0D && result.matchingResistance && !result.matchingNullification
                    && probe.scaled > afterResistance + 0.0001D) {
                afterRecovery = afterResistance + penetration * (probe.scaled - afterResistance);
                event.setAmount((float) afterRecovery);
                if (wasCanceled && afterRecovery > 0.0D) event.setCanceled(false);
            }
            currentHit.familyAfterResistance += afterResistance;
            currentHit.familyAfterRecovery += afterRecovery;
            currentHit.familyCanceledBeforeRecovery |= wasCanceled;
            currentHit.nullificationAuthoritative |= wasCanceled && result.matchingNullification;
            currentHit.resistanceBypassLevel = Math.max(currentHit.resistanceBypassLevel,
                    probe.sourceBypass ? 1.0D : 0.0D);
        }

        private void captureDamagePre(LivingDamageEvent.Pre event) {
            if (phase != Phase.RUN || currentHit == null || event.getEntity() != target) return;
            String type = damageType(event.getSource());
            if (family.matchesDamageType(type)) currentHit.familyAfterL2 += event.getNewDamage();
            else if (isBenchmarkArrow(event.getSource())) currentHit.physicalAfterL2 += event.getNewDamage();
            else currentHit.dotAfterL2 += event.getNewDamage();
        }

        private void captureDamagePost(LivingDamageEvent.Post event) {
            if (phase != Phase.RUN || currentHit == null) return;
            if (event.getEntity() == target) {
                String type = damageType(event.getSource());
                if (family.matchesDamageType(type)) currentHit.familyPost += event.getNewDamage();
                else if (isBenchmarkArrow(event.getSource())) currentHit.physicalPost += event.getNewDamage();
                else currentHit.dotPost += event.getNewDamage();
            }
            else if (event.getEntity() == player) {
                currentHit.reflectedPost += event.getNewDamage();
                currentHit.reflectedSourceIds.add(damageType(event.getSource()));
            }
        }

        private void captureEnergyDrain(LivingEntity drained, Entity source,
                Object drainType, Object gainType, Object amount, Object percentage) throws ReflectiveOperationException {
            if (phase != Phase.RUN || currentHit == null || family != Family.ENERGY
                    || drained != target || !fromBenchmarkPlayer(source)
                    || invoke(drainType, "get") != EnergyHelper.DrainType.EP
                    || invoke(gainType, "get") != EnergyHelper.GainType.NORMAL
                    || !Boolean.TRUE.equals(invoke(percentage, "get"))) return;
            double nativePercentage = numberValue(invoke(amount, "get")).doubleValue();
            double stagedPercentage = nativePercentage * currentCase().stage.coefficient(family);
            if (ENDGAME_RESEARCH) {
                stagedPercentage = nativePercentage;
                nativePercentage /= currentCase().stage.coefficient(family);
            }
            else invoke(amount, "set", stagedPercentage);
            currentHit.energyDrainEvents++;
            currentHit.energyNativePercentage += nativePercentage;
            currentHit.energyStagedPercentage += stagedPercentage;
        }

        private boolean runningTargetEvent(LivingIncomingDamageEvent event) {
            return phase == Phase.RUN && currentHit != null && event.getEntity() == target
                    && fromBenchmarkPlayer(event.getSource().getEntity());
        }

        private boolean isBenchmarkArrow(net.minecraft.world.damagesource.DamageSource source) {
            return source.getDirectEntity() instanceof AbstractArrow arrow && fromBenchmarkPlayer(arrow.getOwner());
        }

        private boolean fromBenchmarkPlayer(Entity owner) {
            return player != null && (owner == player || owner != null && owner.getUUID().equals(player.getUUID()));
        }

        private void fireFullDraw() {
            player.setItemInHand(InteractionHand.OFF_HAND, new ItemStack(royalArrow, 64));
            List<UUID> existing = level.getEntitiesOfClass(Projectile.class,
                    player.getBoundingBox().inflate(64.0D), projectile -> fromBenchmarkPlayer(projectile.getOwner()))
                    .stream().map(Entity::getUUID).toList();
            ItemStack bow = player.getMainHandItem();
            int drawTicks = 20;
            bow.releaseUsing(level, player, bow.getUseDuration(player) - drawTicks);
            List<Projectile> spawned = level.getEntitiesOfClass(Projectile.class,
                    player.getBoundingBox().inflate(64.0D),
                    projectile -> fromBenchmarkPlayer(projectile.getOwner()) && !existing.contains(projectile.getUUID()));
            if (spawned.isEmpty()) throw new IllegalStateException("full-draw Royal Bow release created no projectile");
            currentHit.releasedProjectileCount = spawned.size();
            Vec3 aim = target.getBoundingBox().getCenter();
            for (Projectile projectile : spawned) {
                currentHit.releasedProjectileEntityIds.add(
                        BuiltInRegistries.ENTITY_TYPE.getKey(projectile.getType()).toString());
                currentHit.releasedProjectileUuids.add(projectile.getUUID().toString());
                if (family == Family.ELEMENTAL) {
                    dispatchSlottingProjectile(projectile, aim);
                    continue;
                }
                if (!(projectile instanceof AbstractArrow arrow)) {
                    throw new IllegalStateException("Royal Bow created non-arrow projectile for " + family.id + ": "
                            + BuiltInRegistries.ENTITY_TYPE.getKey(projectile.getType()));
                }
                ResourceLocation projectileId = BuiltInRegistries.ENTITY_TYPE.getKey(arrow.getType());
                if (!SUITE_C && !projectileId.getNamespace().equals("royalvariations")) {
                    throw new IllegalStateException("Royal Bow did not create a Royal Variations arrow: " + arrow.getType());
                }
                if (SUITE_C && !projectileId.equals(id("minecraft", "spectral_arrow"))
                        && !projectileId.getNamespace().equals("royalvariations")) {
                    throw new IllegalStateException("locked Spectral APO profile created unexpected projectile " + projectileId);
                }
                currentHit.projectileEntityId = projectileId.toString();
                if (!target.isAlive()) {
                    // A genuine multi-projectile APO release is dispatched in
                    // spawn order. If an earlier sibling defeats the target,
                    // the remaining projectile has no legal living collision
                    // target. Preserve its spawn evidence and discard it rather
                    // than misclassifying canHitEntity(false) as a case error.
                    currentHit.projectilesDiscardedAfterTargetDefeat++;
                    arrow.discard();
                    continue;
                }
                try {
                    if (projectileId.getNamespace().equals("royalvariations")) {
                        invoke(arrow, "setMarking", false);
                        currentHit.royalArrowMarkObserved |= booleanValue(readField(arrow, "marking"));
                        if (currentHit.royalArrowMarkObserved) {
                            throw new IllegalStateException("Royal Arrow Mark remained active in Suite C isolation");
                        }
                    }
                    if (!booleanValue(invoke(arrow, "canHitEntity", target))) {
                        throw new IllegalStateException("Royal Arrow rejected target collision; player_to_target_allied="
                                + player.isAlliedTo(target) + ", target_to_player_allied=" + target.isAlliedTo(player)
                                + ", target_pickable=" + target.isPickable());
                    }
                }
                catch (ReflectiveOperationException exception) {
                    throw new IllegalStateException("could not disable Royal Arrow Mark for TNO-only isolation", exception);
                }
                arrow.setCritArrow(false);
                double speed = arrow.getDeltaMovement().length();
                if (family == Family.SEVERANCE) configureSeveranceStage(arrow, speed);
                Vec3 direction = aim.subtract(arrow.position()).normalize();
                // Preserve the real released projectile, owner, velocity and damage,
                // while putting it into a deterministic final collision lane. Several
                // scripted bosses otherwise introduce non-damage trajectory misses.
                arrow.setPos(aim.subtract(direction.scale(2.0D)));
                arrow.setDeltaMovement(direction.scale(speed));
                arrow.hasImpulse = true;
                try {
                    invoke(arrow, "onHitEntity", new EntityHitResult(target));
                    currentHit.captureImmediate(target, player);
                    arrow.discard();
                }
                catch (ReflectiveOperationException exception) {
                    throw new IllegalStateException("could not dispatch controlled Royal Arrow collision", exception);
                }
            }
            if (currentHit.releasedProjectileUuids.size() != currentHit.releasedProjectileCount) {
                throw new IllegalStateException("spawned projectile UUIDs were not unique within one release");
            }
        }

        private void dispatchSlottingProjectile(Projectile projectile, Vec3 aim) {
            ResourceLocation type = BuiltInRegistries.ENTITY_TYPE.getKey(projectile.getType());
            if (!type.equals(id("tensura", "stone_shot"))) {
                throw new IllegalStateException("one-Earth-core Slotting release created unexpected projectile " + type);
            }
            if (!fromBenchmarkPlayer(projectile.getOwner())) {
                throw new IllegalStateException("native Slotting projectile did not retain the benchmark player owner");
            }
            try {
                double observedDamage = numberValue(invoke(projectile, "getDamage")).doubleValue();
                double nativeDamage = ENDGAME_RESEARCH
                        ? observedDamage / currentCase().stage.coefficient(family) : observedDamage;
                double stagedDamage = ENDGAME_RESEARCH
                        ? observedDamage : nativeDamage * currentCase().stage.coefficient(family);
                if (!ENDGAME_RESEARCH) invoke(projectile, "setDamage", (float) stagedDamage);
                currentHit.elementalProjectileId = type.toString();
                currentHit.projectileEntityId = type.toString();
                currentHit.elementalOwnerRetained = true;
                currentHit.elementalNativeProjectileDamage = nativeDamage;
                currentHit.elementalStagedProjectileDamage = stagedDamage;
                double speed = projectile.getDeltaMovement().length();
                Vec3 direction = aim.subtract(projectile.position()).normalize();
                projectile.setPos(aim.subtract(direction.scale(2.0D)));
                projectile.setDeltaMovement(direction.scale(speed));
                projectile.hasImpulse = true;
                invoke(projectile, "onHit", new EntityHitResult(target));
                currentHit.captureImmediate(target, player);
                projectile.discard();
            }
            catch (ReflectiveOperationException exception) {
                throw new IllegalStateException("could not dispatch controlled native Slotting projectile", exception);
            }
        }

        private void configureSeveranceStage(AbstractArrow arrow, double speed) {
            double nativeBase = arrow.getBaseDamage();
            double coefficient = currentCase().stage.coefficient(family);
            double stagedBase = nativeBase + SEVERANCE_NATIVE_ATTACK_BONUS * (coefficient - 1.0D);
            if (!ENDGAME_RESEARCH) arrow.setBaseDamage(stagedBase);
            double nativePre = speed * (nativeBase + SEVERANCE_NATIVE_ATTACK_BONUS);
            double stagedPre = speed * (nativeBase + SEVERANCE_NATIVE_ATTACK_BONUS * coefficient);
            double basePost = Math.ceil(speed * nativeBase);
            double nativePost = Math.ceil(nativePre);
            double stagedPost = ENDGAME_RESEARCH
                    ? SeveranceStageScaling.roundedProjectileDamage(speed,
                            SeveranceStageScaling.adjustment(nativeBase + SEVERANCE_NATIVE_ATTACK_BONUS,
                                    1, com.tno.tensuracompat.core.stage.Stage.valueOf(currentCase().stage.name)))
                    : Math.ceil(stagedPre);
            currentHit.severanceConfiguredProjectileCount++;
            currentHit.severanceProjectileSpeed = speed;
            currentHit.severanceBaseProjectileDamage = nativeBase;
            currentHit.severanceNativeAttackBonus = SEVERANCE_NATIVE_ATTACK_BONUS;
            currentHit.severanceStagedAttackBonus = SEVERANCE_NATIVE_ATTACK_BONUS * coefficient;
            currentHit.severanceBasePostByProjectile.put(arrow.getUUID().toString(), basePost);
            currentHit.severanceProjections.put(arrow.getUUID().toString(),
                    new SeveranceProjection(nativePre, stagedPre, basePost, nativePost, stagedPost));
        }

        private FakePlayer createPlayer(int index) {
            String key = "tno-phase5f-suite-" + (SUITE_C ? "c" : "b") + "-"
                    + family.id + "-" + currentCase().boss.id + "-" + index;
            UUID uuid = UUID.nameUUIDFromBytes(key.getBytes(StandardCharsets.UTF_8));
            FakePlayer fake = FakePlayerFactory.get(level,
                    new GameProfile(uuid, (SUITE_C ? "TNO_P5FC_" : "TNO_P5FB_") + index));
            fake.getInventory().clearContent();
            fake.removeAllEffects();
            fake.getAbilities().instabuild = true;
            fake.getAbilities().invulnerable = false;
            setBase(fake, Attributes.MAX_HEALTH, 1024.0D);
            setBase(fake, TensuraAttributes.MAX_SPIRITUAL_HEALTH, 1_000_000_000.0D);
            setBase(fake, TensuraAttributes.MAX_MAGICULE, 1_000_000_000.0D);
            setBase(fake, TensuraAttributes.MAX_AURA, 1_000_000_000.0D);
            fake.setHealth(fake.getMaxHealth());
            fake.setPos(TEST_X, TEST_Y, 0.5D);
            return fake;
        }

        private void equipBenchmarkBow() {
            player.setItemInHand(InteractionHand.MAIN_HAND, benchmarkBow.copy());
            player.setItemInHand(InteractionHand.OFF_HAND, new ItemStack(royalArrow, 64));
            player.setItemSlot(EquipmentSlot.MAINHAND, player.getMainHandItem());
            try {
                invoke(player, "detectEquipmentUpdates");
            }
            catch (ReflectiveOperationException exception) {
                throw new IllegalStateException("could not refresh fake-player attributes", exception);
            }
            if (ENDGAME_RESEARCH) {
                ItemStack equipped = player.getMainHandItem();
                if (!equipped.has(TensuraDataComponents.EP.get())
                        || !equipped.has(TensuraDataComponents.MAX_EP.get())
                        || !equipped.has(TensuraDataComponents.EP_GAIN.get())) {
                    throw new IllegalStateException("Royal Bow did not complete native Tensura gear integration");
                }
                equipped.set(TensuraDataComponents.EP.get(), currentCase().stage.ep.doubleValue());
                String resolved = ProductionStageScaling.stage(equipped)
                        .map(Enum::name).orElse("NONE");
                if (!resolved.equals(currentCase().stage.name)) {
                    throw new IllegalStateException("native EP resolved " + resolved
                            + " instead of " + currentCase().stage.name);
                }
                int selectedLevel = EnchantmentHelper.getItemEnchantmentLevel(
                        server.registryAccess().registryOrThrow(Registries.ENCHANTMENT)
                                .getHolderOrThrow(ResourceKey.create(Registries.ENCHANTMENT, family.enchantment)),
                        equipped);
                if (equipped.getEnchantments().size() != 1 || selectedLevel != 1) {
                    throw new IllegalStateException("TNO-only research bow did not retain exactly one selected Engraving");
                }
            }
            if (SUITE_C) {
                apoInspection = Phase5FRuntimeInspector.inspectBow(
                        player.getMainHandItem(), player, server, "suite_c_locked_profile");
                assertOfficialApoProfile(apoInspection, family);
            }
            else assertNoApoAmplification(player);
        }

        private void stabilize() {
            if (player != null) {
                // FakePlayerFactory instances are not advanced by the normal player
                // list. Tick the native cooldown tracker once per server tick so the
                // Energy Steal I 20-tick cooldown behaves like a real player.
                player.getCooldowns().tick();
                player.setPos(TEST_X, TEST_Y, 0.5D);
                player.setDeltaMovement(Vec3.ZERO);
                player.setYRot(0.0F);
                player.setYHeadRot(0.0F);
                if (target != null && !target.isRemoved()) {
                    Vec3 aim = target.getBoundingBox().getCenter();
                    double horizontal = Math.hypot(aim.x - player.getX(), aim.z - player.getZ());
                    player.setXRot((float) -Math.toDegrees(Math.atan2(aim.y - player.getEyeY(), horizontal)));
                }
            }
            if (target != null && !target.isRemoved()) {
                target.setPos(TEST_X, TEST_Y, TARGET_Z);
                target.setDeltaMovement(Vec3.ZERO);
                target.setNoGravity(true);
                if (target instanceof Mob mob) {
                    mob.setTarget(null);
                    mob.getNavigation().stop();
                    mob.setAggressive(false);
                }
            }
        }

        private void fillResources(LivingEntity living) {
            var existence = TensuraStorages.getExistenceFrom(living);
            existence.setSpiritualHealth(attribute(living, TensuraAttributes.MAX_SPIRITUAL_HEALTH));
            existence.setMagicule(attribute(living, TensuraAttributes.MAX_MAGICULE));
            existence.setAura(attribute(living, TensuraAttributes.MAX_AURA));
        }

        private void runCommand(String command) {
            server.getCommands().performPrefixedCommand(server.createCommandSourceStack(), command);
        }

        private void clearArrows() {
            if (player == null) return;
            level.getEntitiesOfClass(Projectile.class, player.getBoundingBox().inflate(64.0D),
                    projectile -> fromBenchmarkPlayer(projectile.getOwner())).forEach(Entity::discard);
        }

        private void cleanupCase() {
            familyProbes.clear();
            beforeCrit.clear();
            currentHit = null;
            clearArrows();
            if (target != null) target.discard();
            if (player != null) {
                player.setItemInHand(InteractionHand.MAIN_HAND, ItemStack.EMPTY);
                player.setItemInHand(InteractionHand.OFF_HAND, ItemStack.EMPTY);
                player.removeAllEffects();
                // FakePlayerFactory retains instances for the server lifetime. Move the
                // completed attacker out of every later projectile/collision search.
                player.setPos(TEST_X, TEST_Y - 1_000.0D, -1_000.0D - caseIndex);
            }
            target = null;
            player = null;
            l2Cap = null;
            cleanupTestArea();
        }

        private void cleanupTestArea() {
            AABB area = new AABB(TEST_X - 64.0D, TEST_Y - 32.0D, -63.5D,
                    TEST_X + 64.0D, TEST_Y + 32.0D, TARGET_Z + 64.0D);
            level.getEntities((Entity) null, area, entity -> !(entity instanceof Player)).forEach(Entity::discard);
        }

        private CaseSpec currentCase() {
            return cases.get(caseIndex);
        }

        private JsonObject baseCaseJson() {
            JsonObject json = new JsonObject();
            if (caseIndex < cases.size()) {
                CaseSpec spec = currentCase();
                json.addProperty("boss", spec.boss.id.toString());
                json.addProperty("level", spec.level);
                json.addProperty("level_mode", spec.mode.name());
                json.addProperty("TNO_stage", spec.stage.name);
            }
            return json;
        }

        private void logCatalog() {
            JsonObject json = new JsonObject();
            json.addProperty("suite", ENDGAME_RESEARCH ? "PHASE6_TNO_ENDGAME_RESEARCH"
                    : SUITE_C ? "BOTH" : "B_TNO_ONLY");
            json.addProperty("diagnostic", DIAGNOSTIC);
            json.addProperty("strongest_legal_endgame_matrix", STRONGEST_LEGAL_PROFILE);
            json.addProperty("production_stage_observation", ENDGAME_RESEARCH);
            if (ENDGAME_RESEARCH) {
                json.addProperty("authoritative_L2_level_api",
                        "LHMiscs.MOB.type().getOrCreate(target) -> MobTraitCap.getLevel()");
                json.addProperty("profile_evidence_source",
                        "accepted Phase 5F strongest-legal profiles/orc_disaster.jsonl");
            }
            json.addProperty("TNO_family", family.id);
            json.addProperty("engraving", family.enchantment.toString());
            if (family.damageType == null) json.add("damage_source_id", null);
            else json.addProperty("damage_source_id", family.damageType.toString());
            json.addProperty("native_mechanic", switch (family) {
                case ELEMENTAL -> "Slotting I with one legal Earth core; native release interception creates tensura:stone_shot at coefficient 1.0 instead of a Royal Arrow";
                case ENERGY -> "Energy Steal I; 1% current Aura and current Magicules; native 20-tick bow cooldown";
                case SEVERANCE -> "Severance I; +3 enchanted attack contribution before projectile velocity/ceil plus native wound storage";
                default -> "native Tensura damage event";
            });
            if (family == Family.ELEMENTAL) {
                json.addProperty("slotting_element", "EARTH");
                json.addProperty("slotting_core", EARTH_CORE.toString());
                json.addProperty("slotting_capacity", 1);
                json.addProperty("slotting_contents", benchmarkBow.get(DataComponents.BUNDLE_CONTENTS).toString());
                json.addProperty("representative_equivalence_proof", "installed combination_1..5 each contain exactly one Earth/Fire/Space/Water/Wind core, use projectile damage coefficient 1.0, and route through TensuraFlyingProjectile elemental damage; their speeds/knockback/burn/projectile entities remain materially distinct utility and are not Stage-scaled; Earth retained for targeted Hinata Earth Nullification and Luminous Spiritual Nullification coverage");
                json.addProperty("elemental_stage_scope", "damage coefficient only; Slotting capacity/content count/projectile pierce unchanged");
                json.addProperty("royal_arrow_compatibility", "native Slotting release hook consumes the core-loaded Royal Bow release and spawns tensura:stone_shot; no Royal Arrow exists in this legal path");
            }
            if (family == Family.ENERGY) json.addProperty("energy_operation_emits_damage_source", false);
            if (family == Family.SEVERANCE) {
                json.addProperty("severance_distinct_damage_source", false);
                json.addProperty("severance_native_attack_bonus", SEVERANCE_NATIVE_ATTACK_BONUS);
                json.addProperty("severance_stage_formula", "A'=A*(1+t*(P+A)/A), P=2.4, A=3.0; injected as pre-round projectile base delta while native +3 enchantment remains active");
            }
            json.addProperty("APO_profile", SUITE_C ? APO_PROFILE : "NONE");
            if (SUITE_C) {
                json.addProperty("suite_a_apotheosis_profile_preserved", true);
                json.addProperty("suite_a_full_enchantment_package_preserved", false);
                json.addProperty("suite_a_enchantment_removed", "tensura:barrier_piercing");
                json.addProperty("suite_c_enchantment_added", family.enchantment.toString());
                json.addProperty("enchantment_substitution_reason",
                        "the family Engraving is runtime-incompatible with tensura:barrier_piercing; all accepted APO rarity/affix/gem attributes and the other eight Suite A enchantments remain exact");
            }
            json.addProperty("shots_per_case", MAX_SHOTS);
            json.addProperty("fixed_window_ticks", WINDOW_TICKS);
            json.addProperty("server_tick_sprint_enabled",
                    ENDGAME_RESEARCH || SUITE_C && Boolean.getBoolean("tno.phase5f.suiteCFastTicks"));
            json.addProperty("distance", TARGET_Z - 0.5D);
            json.addProperty("projectile_control", family == Family.ELEMENTAL
                    ? "real native one-Earth-core Slotting projectile dispatched through its own onHit path in a deterministic two-block final collision lane; owner, velocity, entity and source preserved"
                    : "real full-draw Royal Arrow dispatched through its own onHitEntity path in a deterministic two-block final collision lane; owner, velocity, item and source preserved");
            json.addProperty("bow", ROYAL_BOW.toString());
            json.addProperty("arrow", family == Family.ELEMENTAL ? "not created by native Slotting release" : ROYAL_ARROW.toString());
            json.addProperty("projectile_entity", family == Family.ELEMENTAL ? "tensura:stone_shot"
                    : SUITE_C ? "royalvariations:royal_arrow or its probabilistic minecraft:spectral_arrow conversion from the locked Spectral affix"
                    : "royalvariations namespace Royal Arrow entity");
            json.addProperty("royal_arrow_mark_enabled", false);
            json.addProperty("crit_enabled", SUITE_C);
            json.addProperty("stage_fixture_only", !ENDGAME_RESEARCH);
            json.addProperty("production_balance_mutated", false);
            json.addProperty("production_combat_mutated", false);
            json.addProperty("profile_clone_policy", ENDGAME_RESEARCH
                    ? "accepted strongest legal profile per exact L2 level; pristine serialized clone for S0-S7"
                    : ENDGAME ? "accepted strongest legal Lv1000 profile per boss; pristine serialized clone for Native and S7"
                    : "one legal native L2 roll per boss/level; pristine serialized clones for Native and S0-S7");
            json.addProperty("benchmark_bow_components", benchmarkBow.getComponents().toString());
            json.add("benchmark_bow_attribute_modifiers", readStackAttributes(benchmarkBow));
            if (SUITE_C) json.add("APO_runtime_inspection", apoInspection.deepCopy());
            JsonArray planned = new JsonArray();
            for (CaseSpec spec : cases) {
                JsonObject entry = new JsonObject();
                entry.addProperty("boss", spec.boss.id.toString());
                entry.addProperty("level", spec.level);
                entry.addProperty("level_mode", spec.mode.name());
                entry.addProperty("TNO_stage", spec.stage.name);
                if (spec.stage.ep == null) entry.add("EP_or_stage_fixture", null);
                else entry.addProperty("EP_or_stage_fixture", spec.stage.ep);
                planned.add(entry);
            }
            json.add("cases", planned);
            log("catalog", json);
        }
    }

    private static List<CaseSpec> buildCases(String filter) {
        List<CaseSpec> result = new ArrayList<>();
        for (BossSpec boss : BOSSES) {
            if (!filter.isBlank() && !boss.id.toString().equals(filter)) continue;
            List<LevelEntry> levels = new ArrayList<>();
            if (ENDGAME_RESEARCH) {
                for (int level : List.of(300, 600, 800, 1000)) {
                    levels.add(new LevelEntry(level, LevelMode.ENDGAME_TARGET));
                }
            }
            else if (ENDGAME) {
                levels.add(new LevelEntry(1000, LevelMode.STRESS));
            }
            else {
                levels.add(new LevelEntry((boss.minLevel + boss.maxLevel) / 2, LevelMode.NATURAL_REPRESENTATIVE));
                levels.add(new LevelEntry(boss.maxLevel, LevelMode.NATURAL_MAXIMUM));
                for (int stress : List.of(300, 600, 800, 1000)) {
                    if (stress != boss.maxLevel) levels.add(new LevelEntry(stress, LevelMode.STRESS));
                }
            }
            if (DIAGNOSTIC) levels = List.of(new LevelEntry(300, boss.maxLevel == 300 ? LevelMode.NATURAL_MAXIMUM : LevelMode.STRESS));
            List<Stage> stages = ENDGAME_RESEARCH ? STAGES.subList(1, STAGES.size())
                    : ENDGAME ? List.of(STAGES.get(0), STAGES.get(8))
                    : DIAGNOSTIC ? List.of(STAGES.get(0), STAGES.get(1), STAGES.get(6), STAGES.get(8)) : STAGES;
            for (LevelEntry entry : levels) {
                for (Stage stage : stages) result.add(new CaseSpec(boss, entry.level, entry.mode, stage));
            }
        }
        return result;
    }

    private static int endgameBudgetSpent(BossSpec boss, int level) {
        if (ENDGAME_RESEARCH) {
            return switch (level) {
                case 300 -> 290;
                case 600 -> 590;
                case 800 -> 780;
                case 1000 -> 980;
                default -> throw new IllegalArgumentException("no accepted Orc budget for Lv" + level);
            };
        }
        return switch (boss.id.toString()) {
            case "tensura_neb:luminous_valentine", "tensura_neb:carrion" -> 1000;
            case "tensura:orc_disaster" -> 980;
            case "tensura_neb:rimuru_ogre_fight" -> 940;
            default -> 950;
        };
    }

    private static final class CaseResult {
        final CaseSpec spec;
        final JsonArray traits;
        final JsonObject traitRanks;
        final JsonObject attackerAttributes;
        final JsonObject bowAttributes;
        final List<HitRecord> hits = new ArrayList<>();
        final boolean nativeProfileSource;
        final boolean matchingResistance;
        final boolean matchingNullification;
        final JsonObject matchingDefenseDetails;
        final double initialMaxHp;
        final double initialHp;
        final double initialMaxShp;
        final double initialShp;
        final double initialMagicules;
        final double initialAura;
        final double initialArmor;
        final double initialToughness;
        final double shpMultiplier;
        final double magiculeMultiplier;
        final double auraMultiplier;
        int shotsReleased;
        int elapsedTicks;
        Integer ttk;
        Integer htk;
        boolean attackerDefeated;
        double finalHp;
        double finalShp;
        double finalMagicules;
        double finalAura;

        CaseResult(CaseSpec spec, LivingEntity target, LivingEntity player, Object cap,
                boolean nativeProfileSource) throws ReflectiveOperationException {
            this.spec = spec;
            this.nativeProfileSource = nativeProfileSource;
            this.traits = readTraits(cap);
            this.traitRanks = traitRanks(traits);
            this.attackerAttributes = readAttributes(player, APO_ATTRIBUTES);
            this.bowAttributes = readStackAttributes(player.getMainHandItem());
            this.matchingResistance = matchingResistance(target, active.family);
            this.matchingNullification = matchingNullification(target, active.family);
            this.matchingDefenseDetails = matchingDefenseDetails(target, active.family);
            this.initialMaxHp = target.getMaxHealth();
            this.initialHp = target.getHealth();
            ResourceState resources = resources(target);
            this.initialMaxShp = resources.maxShp;
            this.initialShp = resources.shp;
            this.initialMagicules = resources.magicules;
            this.initialAura = resources.aura;
            this.initialArmor = target.getArmorValue();
            this.initialToughness = target.getAttributeValue(Attributes.ARMOR_TOUGHNESS);
            this.shpMultiplier = multiplier(target, TensuraAttributes.MAX_SPIRITUAL_HEALTH);
            this.magiculeMultiplier = multiplier(target, TensuraAttributes.MAX_MAGICULE);
            this.auraMultiplier = multiplier(target, TensuraAttributes.MAX_AURA);
        }

        void finish(LivingEntity target) {
            if (target == null) return;
            finalHp = target.getHealth();
            ResourceState resources = resources(target);
            finalShp = resources.shp;
            finalMagicules = resources.magicules;
            finalAura = resources.aura;
        }

        JsonObject caseJson() {
            JsonObject json = commonJson();
            json.addProperty("status", "running");
            return json;
        }

        JsonObject rowJson(HitRecord hit) {
            JsonObject json = commonJson();
            if (SUITE_C) {
                // The exact profile is retained on the catalog, case_start, and
                // case_result records. Avoid repeating the large affix/gem/
                // enchantment arrays on every per-hit row in the accepted JSONL.
                json.remove("APO_affixes");
                json.remove("APO_gems");
                json.remove("APO_enchantments");
                json.addProperty("APO_profile_metadata_record", "catalog/case_start/case_result");
            }
            json.addProperty("hit_index", hit.index);
            json.addProperty("crit", hit.crit);
            json.addProperty("crit_multiplier_event_count", hit.critMultiplierEvents);
            json.addProperty("pre_crit_damage", hit.preCritDamage);
            json.add("crit_damage_source_ids", strings(hit.critDamageSourceIds));
            json.addProperty("pre_HP", hit.preHp);
            json.addProperty("post_HP", hit.postHp);
            json.addProperty("pre_SHP", hit.preShp);
            json.addProperty("post_SHP", hit.postShp);
            json.addProperty("pre_Magicules", hit.preMagicules);
            json.addProperty("immediate_post_Magicules", hit.immediatePostMagicules);
            json.addProperty("post_Magicules", hit.postMagicules);
            json.addProperty("pre_Aura", hit.preAura);
            json.addProperty("immediate_post_Aura", hit.immediatePostAura);
            json.addProperty("post_Aura", hit.postAura);
            json.addProperty("magicule_current_pool_drain", hit.immediateMagiculeDrain());
            json.addProperty("aura_current_pool_drain", hit.immediateAuraDrain());
            json.addProperty("energy_current_pool_drain", hit.energyDrain());
            json.addProperty("magicule_recovery_observed", hit.targetMagiculeRegen);
            json.addProperty("aura_recovery_observed", hit.targetAuraRegen);
            json.addProperty("attacker_magicule_gain", Math.max(0.0D,
                    hit.immediatePostAttackerMagicules - hit.preAttackerMagicules));
            json.addProperty("attacker_aura_gain", Math.max(0.0D,
                    hit.immediatePostAttackerAura - hit.preAttackerAura));
            json.addProperty("energy_drain_event_count", hit.energyDrainEvents);
            json.addProperty("energy_native_percentage", hit.energyNativePercentage);
            json.addProperty("energy_after_stage_percentage", hit.energyStagedPercentage);
            json.addProperty("energy_operation_emitted_damage_source", false);
            json.addProperty("direct_damage", hit.directDamage());
            json.addProperty("physical_damage", hit.physicalPost);
            json.addProperty("engraving_damage", hit.familyPost);
            json.addProperty("resource_damage", hit.resourceDamage());
            json.addProperty("DoT_damage", hit.dotPost);
            json.addProperty("regen", hit.targetHpRegen + hit.targetShpRegen);
            json.addProperty("reflected_damage", hit.reflectedPost);
            json.addProperty("elapsed_ticks", hit.elapsedTicks);
            if (htk == null) json.add("HTK", null); else json.addProperty("HTK", htk);
            if (ttk == null) json.add("TTK", null); else json.addProperty("TTK", ttk);
            json.addProperty("DPS", dps());
            json.addProperty("resource_impact_per_second", resourceImpactPerSecond());
            json.addProperty("blocked_or_cancelled", hit.blocked());
            json.addProperty("projectile_cancelled", hit.physicalDamageEventCount == 0
                    && active.family != Family.ELEMENTAL);
            json.addProperty("physical_damage_event_count", hit.physicalDamageEventCount);
            json.addProperty("engraving_damage_event_count", hit.familyDamageEventCount);
            json.addProperty("dot_damage_event_count", hit.dotDamageEventCount);
            json.add("damage_source_ids", strings(union(hit.physicalSourceIds, hit.familySourceIds)));
            json.add("damage_source_tags_if_observable", strings(union(hit.physicalSourceTags, hit.familySourceTags)));
            json.addProperty("family_source_is_l2_magic", hit.l2Magic);
            json.addProperty("element", active.family == Family.ELEMENTAL ? "EARTH" : "NONE");
            json.addProperty("slotting_projectile_id", hit.elementalProjectileId);
            json.addProperty("slotting_owner_retained", hit.elementalOwnerRetained);
            json.addProperty("slotting_native_projectile_damage", hit.elementalNativeProjectileDamage);
            json.addProperty("slotting_after_stage_projectile_damage", hit.elementalStagedProjectileDamage);
            json.addProperty("slotting_stage_scoped_to_native_projectile_damage",
                    active.family != Family.ELEMENTAL || (hit.physicalOriginal == 0.0D
                            && Math.abs(hit.elementalStagedProjectileDamage
                            - hit.elementalNativeProjectileDamage * spec.stage.coefficient(active.family)) < 0.0001D));
            json.addProperty("projectile_entity_id", hit.hitProjectileEntityIds.size() == 1
                    ? hit.hitProjectileEntityIds.iterator().next()
                    : hit.hitProjectileEntityIds.isEmpty() ? "NONE" : "MULTIPLE");
            json.addProperty("requested_ammo_item", active.family == Family.ELEMENTAL
                    ? ROYAL_ARROW + " consumed by native Slotting release" : ROYAL_ARROW.toString());
            json.addProperty("released_projectile_count", hit.releasedProjectileCount);
            json.add("released_projectile_entity_ids", strings(hit.releasedProjectileEntityIds));
            json.add("released_projectile_uuids", strings(hit.releasedProjectileUuids));
            json.add("hit_projectile_entity_ids", strings(hit.hitProjectileEntityIds));
            json.add("hit_projectile_uuids", strings(hit.hitProjectileUuids));
            json.addProperty("projectiles_discarded_after_target_defeat",
                    hit.projectilesDiscardedAfterTargetDefeat);
            json.addProperty("genuine_apo_multi_projectile_release", hit.releasedProjectileCount > 1
                    && hit.releasedProjectileUuids.size() == hit.releasedProjectileCount);
            json.addProperty("duplicate_event_from_same_projectile", duplicateEventFromSameProjectile(hit));
            json.addProperty("royal_arrow_mark_observed", hit.royalArrowMarkObserved);
            json.addProperty("royal_arrow_created", hit.releasedProjectileEntityIds.stream()
                    .anyMatch(id -> id.startsWith("royalvariations:")));
            json.addProperty("royal_arrow_ammunition_used", active.family != Family.ELEMENTAL);
            json.addProperty("spectral_affix_projectile_conversion",
                    SUITE_C && hit.releasedProjectileEntityIds.contains("minecraft:spectral_arrow"));
            json.addProperty("physical_original_before_stage", hit.physicalOriginal);
            json.addProperty("engraving_native_amount", hit.familyRaw);
            json.addProperty("engraving_after_stage_coefficient", hit.familyStageScaled);
            json.addProperty("damage_before_matching_resistance_recovery", hit.familyAfterResistance);
            json.addProperty("damage_after_matching_resistance_recovery", hit.familyAfterRecovery);
            json.addProperty("damage_after_L2_processing", hit.familyPost);
            if (ENDGAME_RESEARCH) {
                json.addProperty("native_event_existed", nativeEventExisted(hit));
                json.addProperty("value_before_Tensura_defenses", valueBeforeTensura(hit));
                json.addProperty("value_after_Tensura_defenses", valueAfterTensura(hit));
                json.addProperty("value_entering_L2", valueEnteringL2(hit));
                json.addProperty("value_after_L2", valueAfterL2(hit));
                json.addProperty("L2_damage_pipeline_applicable", active.family != Family.ENERGY);
                json.addProperty("associated_effect_executed", associatedEffectExecuted(hit));
                json.addProperty("family_effect_final_event_amount", familyFinalResult(hit));
                json.addProperty("family_final_result", familyFinalResult(hit));
                json.addProperty("final_observed_HP_SHP_resource_damage", hit.resourceDamage());
                json.addProperty("result_classification", resultClassification(hit));
                json.addProperty("failure_reason", failureReason(hit));
                json.addProperty("failure_reason_detail", failureReasonDetail(hit));
                json.addProperty("prerequisite_failure_reason", prerequisiteFailureReason(hit));
            }
            json.addProperty("matching_resistance_cancelled_before_recovery", hit.familyCanceledBeforeRecovery);
            json.addProperty("tensura_resistance_bypass_level", hit.resistanceBypassLevel);
            json.addProperty("nullification_authoritative", hit.nullificationAuthoritative);
            json.addProperty("physical_combined_original_before_L2", hit.physicalCombinedOriginal);
            json.addProperty("severance_projectile_speed", hit.severanceProjectileSpeed);
            json.addProperty("severance_base_projectile_damage", hit.severanceBaseProjectileDamage);
            json.addProperty("severance_native_attack_bonus", hit.severanceNativeAttackBonus);
            json.addProperty("severance_after_stage_attack_bonus", hit.severanceStagedAttackBonus);
            json.addProperty("severance_native_pre_round", hit.severanceNativePreRound);
            json.addProperty("severance_after_stage_pre_round", hit.severanceStagedPreRound);
            json.addProperty("severance_base_only_post_round", hit.severanceBasePostRound);
            json.addProperty("severance_native_post_round", hit.severanceNativePostRound);
            json.addProperty("severance_after_stage_post_round", hit.severanceStagedPostRound);
            json.addProperty("severance_configured_projectile_count", hit.severanceConfiguredProjectileCount);
            json.addProperty("severance_admitted_projectile_count", hit.severanceAdmittedProjectileCount);
            json.addProperty("severance_pre_amount", hit.preSeverance);
            json.addProperty("severance_post_amount", hit.postSeverance);
            json.addProperty("severance_amount_delta", Math.max(0.0D, hit.postSeverance - hit.preSeverance));
            json.addProperty("severance_distinct_damage_source", false);
            json.addProperty("combined_physical_after_L2", hit.physicalAfterL2);
            json.addProperty("combined_physical_post_damage", hit.physicalPost);
            json.addProperty("dispell_transformed", transformed(hit, "l2hostility:dispell", true));
            json.addProperty("dementor_transformed", transformed(hit, "l2hostility:dementor", false));
            json.addProperty("adaptive_hit_index", traitRanks.has("l2hostility:adaptive") ? hit.index : 0);
            json.addProperty("adaptive_effect_observed", adaptiveObserved(hit));
            json.addProperty("l2_layer_bypassed_unexpectedly", false);
            json.addProperty("tensura_layer_bypassed_unexpectedly", false);
            json.addProperty("unexpected_source_duplication", unexpectedSourceDuplication(hit));
            json.addProperty("event_recursion_observed", false);
            json.addProperty("physical_damage_source_id", hit.physicalSourceIds.size() == 1
                    ? hit.physicalSourceIds.iterator().next() : "MULTIPLE_OR_NONE");
            json.addProperty("family_damage_source_id", hit.familySourceIds.size() == 1
                    ? hit.familySourceIds.iterator().next() : "MULTIPLE_OR_NONE");
            json.addProperty("notes", interactionNotes(hit));
            return json;
        }

        private boolean nativeEventExisted(HitRecord hit) {
            return switch (active.family) {
                case MAGIC, HOLY, SOUL, ELEMENTAL -> hit.familyDamageEventCount > 0;
                case ENERGY -> hit.energyDrainEvents > 0;
                case SEVERANCE -> hit.severanceConfiguredProjectileCount > 0;
            };
        }

        private double valueBeforeTensura(HitRecord hit) {
            return switch (active.family) {
                case MAGIC, HOLY, SOUL, ELEMENTAL -> hit.familyStageScaled;
                case ENERGY -> hit.energyStagedPercentage;
                case SEVERANCE -> hit.physicalCombinedOriginal;
            };
        }

        private double valueAfterTensura(HitRecord hit) {
            return switch (active.family) {
                case MAGIC, HOLY, SOUL, ELEMENTAL -> hit.familyAfterResistance;
                case ENERGY -> hit.energyStagedPercentage;
                case SEVERANCE -> hit.physicalIncoming;
            };
        }

        private double valueEnteringL2(HitRecord hit) {
            return switch (active.family) {
                case MAGIC, HOLY, SOUL, ELEMENTAL -> hit.familyAfterRecovery;
                case ENERGY -> 0.0D;
                case SEVERANCE -> hit.physicalIncoming;
            };
        }

        private double valueAfterL2(HitRecord hit) {
            return switch (active.family) {
                case MAGIC, HOLY, SOUL, ELEMENTAL -> hit.familyPost;
                case ENERGY -> 0.0D;
                case SEVERANCE -> hit.physicalPost;
            };
        }

        private boolean associatedEffectExecuted(HitRecord hit) {
            return switch (active.family) {
                case MAGIC, HOLY, SOUL, ELEMENTAL -> hit.familyPost > 0.0D;
                case ENERGY -> hit.energyDrainEvents > 0 && hit.energyDrain() > 0.0D;
                case SEVERANCE -> hit.postSeverance > hit.preSeverance;
            };
        }

        private double familyFinalResult(HitRecord hit) {
            return switch (active.family) {
                case MAGIC, HOLY, SOUL, ELEMENTAL -> hit.familyPost;
                case ENERGY -> hit.energyDrain();
                case SEVERANCE -> Math.max(0.0D, hit.postSeverance - hit.preSeverance);
            };
        }

        private String resultClassification(HitRecord hit) {
            if (familyFinalResult(hit) <= 0.0001D) return "ZERO";
            if ((active.family == Family.MAGIC || active.family == Family.HOLY)
                    && hit.resourceDamage() <= 0.0001D) return "ZERO";
            if (active.family != Family.ENERGY) {
                double entering = valueEnteringL2(hit);
                if (entering > 0.0D && familyFinalResult(hit) / entering <= 0.10D) return "NEAR_ZERO";
            }
            return "NONZERO";
        }

        private String failureReason(HitRecord hit) {
            if (resultClassification(hit).equals("NONZERO")) return "NONE";
            if (matchingNullification && nativeEventExisted(hit)) return "TENSURA_NULLIFICATION";
            if (matchingResistance && nativeEventExisted(hit) && valueAfterTensura(hit) <= 0.0001D) {
                return "TENSURA_RESISTANCE";
            }
            if ((active.family == Family.MAGIC || active.family == Family.HOLY
                    || active.family == Family.ENERGY) && !nativeEventExisted(hit)) {
                return "PREREQUISITE_HIT_FAILED";
            }
            if ((active.family == Family.SOUL || active.family == Family.ELEMENTAL)
                    && !nativeEventExisted(hit)) return "NATIVE_EVENT_ABSENT";
            if (active.family == Family.SEVERANCE && hit.physicalDamageEventCount == 0) {
                return traitRanks.has("l2hostility:repelling")
                        ? "L2_PROJECTILE_REJECTION" : "PREREQUISITE_HIT_FAILED";
            }
            if (valueEnteringL2(hit) > 0.0D && valueAfterL2(hit) <= 0.0001D) {
                return traitRanks.has("l2hostility:arena")
                        ? "L2_ADMISSION_VETO" : "L2_MITIGATION";
            }
            if (valueEnteringL2(hit) > 0.0D
                    && familyFinalResult(hit) / valueEnteringL2(hit) <= 0.10D) return "L2_MITIGATION";
            if ((active.family == Family.MAGIC || active.family == Family.HOLY)
                    && familyFinalResult(hit) > 0.0001D && hit.resourceDamage() <= 0.0001D) {
                return "OTHER_VERIFIED_REASON";
            }
            return "OTHER_VERIFIED_REASON";
        }

        private String failureReasonDetail(HitRecord hit) {
            return switch (failureReason(hit)) {
                case "NONE" -> "NONE";
                case "TENSURA_RESISTANCE" -> "Matching native Tensura Resistance cancelled the eligible family amount.";
                case "TENSURA_NULLIFICATION" -> "Matching native Tensura Nullification remained authoritative.";
                case "L2_MITIGATION" -> "The legal L2 profile reduced the admitted family result to at most 10% of its L2-entry amount.";
                case "L2_ADMISSION_VETO" -> "The legal L2 Arena admission rule rejected the hit before the family effect could execute.";
                case "L2_PROJECTILE_REJECTION" -> "The legal L2 Repelling rule rejected the projectile prerequisite.";
                case "PREREQUISITE_HIT_FAILED" -> "The native family operation did not execute because its prerequisite physical hit did not survive.";
                case "NATIVE_EVENT_ABSENT" -> "The Royal Bow path emitted no native event eligible for this family.";
                default -> (active.family == Family.MAGIC || active.family == Family.HOLY)
                        && familyFinalResult(hit) > 0.0001D && hit.resourceDamage() <= 0.0001D
                        ? "A positive post-L2 family event amount produced no persistent HP/SHP resource loss during the observed hit interval."
                        : "The observed zero or near-zero result was not attributable to another verified failure category.";
            };
        }

        private String prerequisiteFailureReason(HitRecord hit) {
            if (!failureReason(hit).equals("PREREQUISITE_HIT_FAILED")) return "NONE";
            if (traitRanks.has("l2hostility:repelling") && hit.physicalDamageEventCount == 0) {
                return "L2_PROJECTILE_REJECTION";
            }
            if (traitRanks.has("l2hostility:arena") && hit.physicalDamageEventCount == 0) {
                return "L2_ADMISSION_VETO";
            }
            if (hit.physicalIncoming > 0.0D && hit.physicalAfterL2 <= 0.0001D) {
                return "L2_MITIGATION";
            }
            return hit.physicalDamageEventCount == 0 ? "OTHER_VERIFIED_REASON" : "NATIVE_EVENT_ABSENT";
        }

        JsonObject summaryJson() {
            JsonObject json = commonJson();
            json.addProperty("status", "ok");
            json.addProperty("shots_released", shotsReleased);
            json.addProperty("hits_recorded", hits.size());
            json.addProperty("direct_damage", hits.stream().mapToDouble(HitRecord::directDamage).sum());
            json.addProperty("resource_damage", hits.stream().mapToDouble(HitRecord::resourceDamage).sum());
            json.addProperty("energy_current_pool_drain", hits.stream().mapToDouble(HitRecord::energyDrain).sum());
            json.addProperty("DoT_damage", hits.stream().mapToDouble(hit -> hit.dotPost).sum());
            json.addProperty("regen", hits.stream().mapToDouble(hit -> hit.targetHpRegen + hit.targetShpRegen).sum());
            json.addProperty("reflected_damage", hits.stream().mapToDouble(hit -> hit.reflectedPost).sum());
            json.addProperty("elapsed_ticks", elapsedTicks);
            json.addProperty("DPS", dps());
            json.addProperty("resource_impact_per_second", resourceImpactPerSecond());
            if (htk == null) json.add("HTK", null); else json.addProperty("HTK", htk);
            if (ttk == null) json.add("TTK", null); else json.addProperty("TTK", ttk);
            json.addProperty("attacker_defeated", attackerDefeated);
            json.addProperty("final_HP", finalHp);
            json.addProperty("final_SHP", finalShp);
            json.addProperty("final_Magicules", finalMagicules);
            json.addProperty("final_Aura", finalAura);
            json.addProperty("notes", interactionNotes(null));
            return json;
        }

        private JsonObject commonJson() {
            JsonObject json = new JsonObject();
            json.addProperty("suite", ENDGAME_RESEARCH ? "PHASE6_TNO_ENDGAME_RESEARCH"
                    : SUITE_C ? "BOTH" : "B_TNO_ONLY");
            json.addProperty("diagnostic", DIAGNOSTIC);
            json.addProperty("boss", spec.boss.id.toString());
            json.addProperty("boss_priority", spec.boss.primary ? "PRIMARY" : "SECONDARY");
            json.addProperty("level", spec.level);
            json.addProperty("level_mode", spec.mode.name());
            json.addProperty("configured_min_level", spec.boss.minLevel);
            json.addProperty("configured_max_level", spec.boss.maxLevel);
            json.addProperty("l2_initialized", true);
            json.add("traits", traits.deepCopy());
            json.add("trait_ranks", traitRanks.deepCopy());
            json.addProperty("legal_profile", STRONGEST_LEGAL_PROFILE || spec.mode != LevelMode.STRESS);
            json.addProperty("legal_trait_profile", true);
            json.addProperty("native_profile_source", nativeProfileSource);
            json.addProperty("profile_clone_verified", true);
            json.addProperty("strongest_legal_endgame_profile", STRONGEST_LEGAL_PROFILE);
            json.addProperty("endgame_profile_source",
                    STRONGEST_LEGAL_PROFILE ? "accepted Phase 5F 39-trait strongest legal defensive profile" : "not applicable");
            json.addProperty("endgame_profile_budget_spent",
                    STRONGEST_LEGAL_PROFILE ? endgameBudgetSpent(spec.boss, spec.level) : 0);
            json.addProperty("endgame_profile_budget_remaining",
                    STRONGEST_LEGAL_PROFILE ? spec.level - endgameBudgetSpent(spec.boss, spec.level) : 0);
            json.addProperty("HP", initialMaxHp);
            json.addProperty("initial_HP", initialHp);
            json.addProperty("SHP", initialShp);
            json.addProperty("max_SHP", initialMaxShp);
            json.addProperty("Magicules", initialMagicules);
            json.addProperty("Aura", initialAura);
            json.addProperty("armor", initialArmor);
            json.addProperty("toughness", initialToughness);
            json.addProperty("SHP_multiplier", shpMultiplier);
            json.addProperty("Magicules_multiplier", magiculeMultiplier);
            json.addProperty("Aura_multiplier", auraMultiplier);
            json.addProperty("tensura_l2h_scaling_marker", true);
            json.addProperty("TNO_family", active.family.id);
            json.addProperty("TNO_stage", spec.stage.name);
            if (spec.stage.ep == null) json.add("EP_or_stage_fixture", null); else json.addProperty("EP_or_stage_fixture", spec.stage.ep);
            if (ENDGAME_RESEARCH) {
                json.addProperty("native_gear_EP", active.player.getMainHandItem()
                        .getOrDefault(TensuraDataComponents.EP.get(), 0.0D));
                json.addProperty("resolved_production_stage", ProductionStageScaling
                        .stage(active.player.getMainHandItem()).map(Enum::name).orElse("NONE"));
                json.addProperty("production_stage_observation", true);
            }
            json.addProperty("stage_bonus", spec.stage.bonus);
            json.addProperty("stage_coefficient", spec.stage.coefficient(active.family));
            json.addProperty("APO_profile", SUITE_C ? APO_PROFILE : "NONE");
            json.addProperty("royal_arrow_mark_enabled", false);
            json.addProperty("matching_Tensura_resistance_present", matchingResistance);
            json.addProperty("matching_Tensura_nullification_present", matchingNullification);
            json.add("matching_Tensura_defense_details", matchingDefenseDetails.deepCopy());
            json.addProperty("penetration_percentage_applied", matchingResistance && !matchingNullification ? spec.stage.penetration : 0.0D);
            json.add("Bow_attributes", bowAttributes.deepCopy());
            json.add("attacker_APO_attributes", attackerAttributes.deepCopy());
            if (SUITE_C) {
                JsonObject apotheosis = active.apoInspection.getAsJsonObject("apotheosis");
                json.addProperty("suite_a_apotheosis_profile_preserved", true);
                json.addProperty("suite_a_full_enchantment_package_preserved", false);
                json.addProperty("suite_a_enchantment_removed", "tensura:barrier_piercing");
                json.addProperty("suite_c_enchantment_added", active.family.enchantment.toString());
                json.addProperty("APO_rarity", apotheosis.get("rarity").getAsString());
                json.add("APO_affixes", apotheosis.getAsJsonObject("affixes").getAsJsonArray("entries").deepCopy());
                json.addProperty("APO_sockets",
                        apotheosis.getAsJsonObject("sockets").get("effective_socket_count").getAsInt());
                json.add("APO_gems", apotheosis.getAsJsonObject("sockets").getAsJsonArray("gems").deepCopy());
                json.add("APO_enchantments",
                        active.apoInspection.getAsJsonObject("enchantments").getAsJsonArray("applied").deepCopy());
            }
            return json;
        }

        private boolean unexpectedSourceDuplication(HitRecord hit) {
            int projectiles = Math.max(1, hit.releasedProjectileCount);
            if (duplicateEventFromSameProjectile(hit)) return true;
            if (active.family == Family.ELEMENTAL) return hit.physicalDamageEventCount != 0
                    || hit.familyDamageEventCount > projectiles;
            if (active.family == Family.ENERGY) return hit.physicalDamageEventCount > projectiles
                    || hit.energyDrainEvents > projectiles;
            if (active.family == Family.SEVERANCE) return hit.physicalDamageEventCount > projectiles
                    || hit.familyDamageEventCount != 0;
            return hit.physicalDamageEventCount > projectiles || hit.familyDamageEventCount > projectiles;
        }

        private boolean duplicateEventFromSameProjectile(HitRecord hit) {
            return hit.physicalEventsByProjectile.values().stream().anyMatch(count -> count > 1);
        }

        private boolean transformed(HitRecord hit, String trait, boolean magic) {
            if (!traitRanks.has(trait) || hit.l2Magic != magic || active.family == Family.ENERGY) return false;
            double before = active.family == Family.SEVERANCE ? hit.physicalIncoming : hit.familyAfterRecovery;
            double after = active.family == Family.SEVERANCE ? hit.physicalPost : hit.familyPost;
            return after + 0.0001D < before;
        }

        private boolean adaptiveObserved(HitRecord hit) {
            double before = active.family == Family.SEVERANCE ? hit.physicalIncoming : hit.familyAfterRecovery;
            double after = active.family == Family.SEVERANCE ? hit.physicalPost : hit.familyPost;
            if (!traitRanks.has("l2hostility:adaptive") || hit.index < 2 || before <= 0.0D
                    || active.family == Family.ENERGY) return false;
            HitRecord previous = hits.stream().filter(value -> value.index == hit.index - 1).findFirst().orElse(null);
            if (previous == null) return false;
            double previousBefore = active.family == Family.SEVERANCE
                    ? previous.physicalIncoming : previous.familyAfterRecovery;
            double previousAfter = active.family == Family.SEVERANCE ? previous.physicalPost : previous.familyPost;
            if (previousBefore <= 0.0D) return false;
            return after / before + 0.0001D < previousAfter / previousBefore;
        }

        private double dps() {
            double effective = hits.stream().mapToDouble(HitRecord::resourceDamage).sum();
            return elapsedTicks <= 0 ? 0.0D : effective / (elapsedTicks / 20.0D);
        }

        private double resourceImpactPerSecond() {
            double effective = active.family == Family.ENERGY
                    ? hits.stream().mapToDouble(HitRecord::energyDrain).sum()
                    : hits.stream().mapToDouble(HitRecord::resourceDamage).sum();
            return elapsedTicks <= 0 ? 0.0D : effective / (elapsedTicks / 20.0D);
        }

        private String interactionNotes(HitRecord hit) {
            List<String> notes = new ArrayList<>();
            traitRanks.keySet().stream().filter(DEFENSIVE_TRAITS::contains)
                    .forEach(id -> notes.add(id + " rank " + traitRanks.get(id).getAsInt()));
            if (matchingNullification) notes.add("matching Tensura Nullification kept authoritative");
            else if (matchingResistance) notes.add("matching Tensura Resistance measured before benchmark recovery");
            if (spec.mode == LevelMode.STRESS) notes.add("controlled level above/independent of natural entity ceiling");
            if (spec.mode == LevelMode.ENDGAME_TARGET) {
                notes.add("intended pack endgame level with accepted strongest legal L2 profile");
            }
            if (hit != null && hit.blocked()) notes.add(active.family == Family.ELEMENTAL
                    ? "released native Slotting projectile produced no net HP/SHP damage"
                    : "released Royal Arrow produced no net HP/SHP damage");
            return String.join("; ", notes);
        }
    }

    private static final class HitRecord {
        final int index;
        final int startTick;
        final double preHp;
        final double preShp;
        final double preMagicules;
        final double preAura;
        final double preSeverance;
        final double preAttackerHp;
        final double preAttackerShp;
        final double preAttackerMagicules;
        final double preAttackerAura;
        final Set<String> physicalSourceIds = new LinkedHashSet<>();
        final Set<String> physicalSourceTags = new LinkedHashSet<>();
        final Set<String> familySourceIds = new LinkedHashSet<>();
        final Set<String> familySourceTags = new LinkedHashSet<>();
        final Set<String> dotSourceIds = new LinkedHashSet<>();
        final Set<String> reflectedSourceIds = new LinkedHashSet<>();
        final Set<String> critDamageSourceIds = new LinkedHashSet<>();
        final Set<String> releasedProjectileEntityIds = new LinkedHashSet<>();
        final Set<String> releasedProjectileUuids = new LinkedHashSet<>();
        final Set<String> hitProjectileEntityIds = new LinkedHashSet<>();
        final Set<String> hitProjectileUuids = new LinkedHashSet<>();
        final Map<String, Integer> physicalEventsByProjectile = new LinkedHashMap<>();
        final Map<String, Double> severanceBasePostByProjectile = new LinkedHashMap<>();
        final Map<String, SeveranceProjection> severanceProjections = new LinkedHashMap<>();
        final Set<String> severanceAdmittedProjectileUuids = new LinkedHashSet<>();
        double lastHp;
        double lastShp;
        double lastMagicules;
        double lastAura;
        double lastAttackerHp;
        double lastAttackerShp;
        double lastAttackerMagicules;
        double lastAttackerAura;
        double postHp;
        double postShp;
        double postMagicules;
        double postAura;
        double postSeverance;
        double immediatePostMagicules;
        double immediatePostAura;
        double immediatePostAttackerMagicules;
        double immediatePostAttackerAura;
        double targetHpRegen;
        double targetShpRegen;
        double targetMagiculeRegen;
        double targetAuraRegen;
        double attackerHpRegen;
        double attackerShpRegen;
        double attackerMagiculeRegen;
        double attackerAuraRegen;
        double physicalOriginal;
        double physicalCombinedOriginal;
        double physicalIncoming;
        double physicalAfterL2;
        double physicalPost;
        double familyRaw;
        double familyStageScaled;
        double familyAfterResistance;
        double familyAfterRecovery;
        double familyAfterL2;
        double familyPost;
        double dotIncoming;
        double dotAfterL2;
        double dotPost;
        double reflectedPost;
        double preCritDamage;
        int elapsedTicks;
        int physicalDamageEventCount;
        int familyDamageEventCount;
        int dotDamageEventCount;
        int critMultiplierEvents;
        int releasedProjectileCount;
        int projectilesDiscardedAfterTargetDefeat;
        int severanceConfiguredProjectileCount;
        int severanceAdmittedProjectileCount;
        boolean crit;
        boolean royalArrowMarkObserved;
        boolean l2Magic;
        boolean familyCanceledBeforeRecovery;
        boolean nullificationAuthoritative;
        double resistanceBypassLevel;
        int energyDrainEvents;
        double energyNativePercentage;
        double energyStagedPercentage;
        double severanceProjectileSpeed;
        double severanceBaseProjectileDamage;
        double severanceNativeAttackBonus;
        double severanceStagedAttackBonus;
        double severanceNativePreRound;
        double severanceStagedPreRound;
        double severanceBasePostRound;
        double severanceNativePostRound;
        double severanceStagedPostRound;
        String elementalProjectileId = "";
        String projectileEntityId = "";
        boolean elementalOwnerRetained;
        double elementalNativeProjectileDamage;
        double elementalStagedProjectileDamage;
        boolean immediateCaptured;

        HitRecord(int index, int startTick, LivingEntity target, LivingEntity player) {
            this.index = index;
            this.startTick = startTick;
            ResourceState targetResources = resources(target);
            ResourceState playerResources = resources(player);
            this.preHp = this.lastHp = target.getHealth();
            this.preShp = this.lastShp = targetResources.shp;
            this.preMagicules = this.lastMagicules = targetResources.magicules;
            this.preAura = this.lastAura = targetResources.aura;
            this.preSeverance = severance(target);
            this.preAttackerHp = this.lastAttackerHp = player.getHealth();
            this.preAttackerShp = this.lastAttackerShp = playerResources.shp;
            this.preAttackerMagicules = this.lastAttackerMagicules = playerResources.magicules;
            this.preAttackerAura = this.lastAttackerAura = playerResources.aura;
            this.postHp = preHp;
            this.postShp = preShp;
            this.postMagicules = this.immediatePostMagicules = preMagicules;
            this.postAura = this.immediatePostAura = preAura;
            this.postSeverance = preSeverance;
            this.immediatePostAttackerMagicules = preAttackerMagicules;
            this.immediatePostAttackerAura = preAttackerAura;
        }

        void captureImmediate(LivingEntity target, LivingEntity player) {
            ResourceState targetState = resources(target);
            ResourceState playerState = resources(player);
            immediatePostMagicules = targetState.magicules;
            immediatePostAura = targetState.aura;
            immediatePostAttackerMagicules = playerState.magicules;
            immediatePostAttackerAura = playerState.aura;
            postSeverance = severance(target);
            immediateCaptured = true;
        }

        void observe(LivingEntity target, LivingEntity player) {
            if (target != null) {
                ResourceState state = resources(target);
                double hp = target.getHealth();
                if (hp > lastHp) targetHpRegen += hp - lastHp;
                if (state.shp > lastShp) targetShpRegen += state.shp - lastShp;
                if (state.magicules > lastMagicules) targetMagiculeRegen += state.magicules - lastMagicules;
                if (state.aura > lastAura) targetAuraRegen += state.aura - lastAura;
                lastHp = postHp = hp;
                lastShp = postShp = state.shp;
                lastMagicules = postMagicules = state.magicules;
                lastAura = postAura = state.aura;
                postSeverance = severance(target);
            }
            if (player != null) {
                ResourceState state = resources(player);
                double hp = player.getHealth();
                if (hp > lastAttackerHp) attackerHpRegen += hp - lastAttackerHp;
                if (state.shp > lastAttackerShp) attackerShpRegen += state.shp - lastAttackerShp;
                if (state.magicules > lastAttackerMagicules) attackerMagiculeRegen += state.magicules - lastAttackerMagicules;
                if (state.aura > lastAttackerAura) attackerAuraRegen += state.aura - lastAttackerAura;
                lastAttackerHp = hp;
                lastAttackerShp = state.shp;
                lastAttackerMagicules = state.magicules;
                lastAttackerAura = state.aura;
            }
        }

        double immediateMagiculeDrain() {
            return Math.max(0.0D, preMagicules - immediatePostMagicules);
        }

        double immediateAuraDrain() {
            return Math.max(0.0D, preAura - immediatePostAura);
        }

        double energyDrain() {
            return immediateMagiculeDrain() + immediateAuraDrain();
        }

        double resourceDamage() {
            double observed = Math.max(0.0D,
                    preHp + preShp - postHp - postShp + targetHpRegen + targetShpRegen);
            double appliedEvents = Math.max(0.0D, directDamage() + dotPost);
            return Math.min(observed, appliedEvents);
        }

        double directDamage() {
            return physicalPost + familyPost;
        }

        boolean blocked() {
            return directDamage() == 0.0D && resourceDamage() == 0.0D && energyDrain() == 0.0D;
        }
    }

    private static ItemStack buildBenchmarkBow(MinecraftServer server, Family family) {
        ItemStack bow;
        try {
            bow = SUITE_C ? Phase5FApotheosisBenchmark.buildOfficialWinner(server)
                    : new ItemStack(requiredItem(ROYAL_BOW));
        }
        catch (ReflectiveOperationException exception) {
            throw new IllegalStateException("could not construct locked Suite C APO profile", exception);
        }
        Registry<Enchantment> registry = server.registryAccess().registryOrThrow(Registries.ENCHANTMENT);
        Holder.Reference<Enchantment> enchantment = registry.getHolderOrThrow(
                ResourceKey.create(Registries.ENCHANTMENT, family.enchantment));
        if (SUITE_C) {
            EnchantmentHelper.updateEnchantments(bow, mutable -> mutable.removeIf(
                    holder -> holderId(holder).equals("tensura:barrier_piercing")));
        }
        if (!enchantment.value().canEnchant(bow)) {
            throw new IllegalStateException(family.enchantment + " does not support the locked Royal Bow");
        }
        for (var entry : bow.getEnchantments().entrySet()) {
            if (!Enchantment.areCompatible(entry.getKey(), enchantment)) {
                throw new IllegalStateException(family.enchantment
                        + " is incompatible with accepted Suite A enchantment " + holderId(entry.getKey()));
            }
        }
        bow.enchant(enchantment, 1);
        if (family == Family.ELEMENTAL) {
            bow.set(DataComponents.BUNDLE_CONTENTS,
                    new BundleContents(List.of(new ItemStack(requiredItem(EARTH_CORE)))));
        }
        if (ENDGAME_RESEARCH) {
            // This deterministic benchmark supplies its one selected family itself.
            // Mark the production one-time roll as already handled so equipping the
            // disposable stack cannot add a second random Engraving.
            CustomData.update(DataComponents.CUSTOM_DATA, bow,
                    tag -> tag.putBoolean("tno_tensura_compat.first_engraving_roll_processed", true));
        }
        return bow;
    }

    private static void assertOfficialApoProfile(JsonObject inspection, Family family) {
        if (!ROYAL_BOW.toString().equals(inspection.get("item_id").getAsString())) {
            throw new IllegalStateException("Suite C item changed from Royal Bow");
        }
        JsonObject apotheosis = inspection.getAsJsonObject("apotheosis");
        if (!"ok".equals(apotheosis.get("status").getAsString())
                || !"ancientreforging:ancient".equals(apotheosis.get("rarity").getAsString())) {
            throw new IllegalStateException("Suite C APO rarity inspection mismatch: " + apotheosis);
        }

        JsonArray affixes = apotheosis.getAsJsonObject("affixes").getAsJsonArray("entries");
        Set<String> actualAffixes = new LinkedHashSet<>();
        for (var value : affixes) {
            JsonObject affix = value.getAsJsonObject();
            actualAffixes.add(affix.get("id").getAsString());
            if (!affix.get("valid").getAsBoolean()
                    || Math.abs(affix.get("effective_level").getAsDouble() - 1.5D) > 0.0001D) {
                throw new IllegalStateException("Suite C affix is invalid or not at Supremacy 1.5: " + affix);
            }
        }
        if (!actualAffixes.equals(OFFICIAL_AFFIXES)) {
            throw new IllegalStateException("Suite C affix set mismatch: " + actualAffixes);
        }

        JsonObject sockets = apotheosis.getAsJsonObject("sockets");
        if (sockets.get("effective_socket_count").getAsInt() != 5
                || !sockets.get("all_unique_constraints_satisfied").getAsBoolean()) {
            throw new IllegalStateException("Suite C socket validation failed: " + sockets);
        }
        Map<String, Integer> actualGems = new LinkedHashMap<>();
        for (var value : sockets.getAsJsonArray("gems")) {
            JsonObject gem = value.getAsJsonObject();
            if (!gem.get("valid").getAsBoolean() || !"perfect".equals(gem.get("purity").getAsString())) {
                throw new IllegalStateException("Suite C gem is invalid or not Perfect: " + gem);
            }
            actualGems.merge(gem.get("id").getAsString(), 1, Integer::sum);
        }
        if (!actualGems.equals(OFFICIAL_GEMS)) {
            throw new IllegalStateException("Suite C gem multiset mismatch: " + actualGems);
        }

        JsonObject enchantments = inspection.getAsJsonObject("enchantments");
        if (!enchantments.get("applied_pairwise_compatible").getAsBoolean()) {
            throw new IllegalStateException("Suite C enchantment package is not pairwise compatible");
        }
        Set<String> applied = new LinkedHashSet<>();
        for (var value : enchantments.getAsJsonArray("applied")) {
            JsonObject enchantment = value.getAsJsonObject();
            applied.add(enchantment.get("id").getAsString());
            if (!enchantment.get("supported_by_item").getAsBoolean()
                    || enchantment.get("level").getAsInt() != enchantment.get("runtime_max_level").getAsInt()
                    && !enchantment.get("id").getAsString().equals(family.enchantment.toString())) {
                throw new IllegalStateException("Suite C enchantment validation failed: " + enchantment);
            }
        }
        Set<String> expectedEnchantments = new LinkedHashSet<>(List.of(
                "apothic_enchanting:endless_quiver", "apothicnightmares:spatial_bow",
                "l2complements:soul_bound", "l2complements:transparent", "l2hostility:vanish",
                "minecraft:flame", "minecraft:power", "minecraft:punch"));
        expectedEnchantments.add(family.enchantment.toString());
        if (!applied.equals(expectedEnchantments)) {
            throw new IllegalStateException("Suite C enchantment set mismatch: " + applied);
        }

        JsonObject attributes = apotheosis.getAsJsonObject("attributes");
        for (var expected : OFFICIAL_APO_ATTRIBUTES.entrySet()) {
            double actual = attributes.getAsJsonObject(expected.getKey()).get("player_effective_value").getAsDouble();
            if (Math.abs(actual - expected.getValue()) > 0.0001D) {
                throw new IllegalStateException("Suite C APO attribute mismatch: " + expected.getKey()
                        + "=" + actual + " expected " + expected.getValue());
            }
        }
    }

    private static Item requiredItem(ResourceLocation id) {
        Item item = BuiltInRegistries.ITEM.get(id);
        if (item == null || BuiltInRegistries.ITEM.getKey(item).equals(id("minecraft", "air"))) {
            throw new IllegalStateException("required item absent: " + id);
        }
        return item;
    }

    private static void assertTnoOnlyStack(ItemStack bow) {
        String components = bow.getComponents().toString().toLowerCase(Locale.ROOT);
        for (String forbidden : List.of("apotheosis:", "apothic_equipment:", "apothicnightmares:", "ancientreforging:")) {
            if (components.contains(forbidden)) throw new IllegalStateException("clean TNO-only bow contains APO component: " + forbidden);
        }
    }

    private static void assertNoApoAmplification(LivingEntity player) {
        if (!ModList.get().isLoaded("apothic_attributes")) return;
        for (ResourceLocation id : APO_ATTRIBUTES) {
            double value = attribute(player, id, 0.0D);
            String path = id.getPath();
            double expected = switch (path) {
                case "arrow_damage", "arrow_velocity", "draw_speed" -> 1.0D;
                case "crit_chance" -> 0.05D;
                case "crit_damage" -> 1.5D;
                default -> 0.0D;
            };
            if (Math.abs(value - expected) > 0.0001D) {
                throw new IllegalStateException("unexpected APO amplification on clean player: " + id + "=" + value + " expected " + expected);
            }
        }
    }

    private static boolean matchingResistance(LivingEntity target, Family family) {
        return switch (family) {
            case MAGIC -> skillToggled(target, "MAGIC_RESISTANCE");
            case HOLY -> skillToggled(target, "HOLY_ATTACK_RESISTANCE");
            case SOUL -> skillToggled(target, "SPIRITUAL_ATTACK_RESISTANCE");
            case ELEMENTAL -> skillToggled(target, "EARTH_ATTACK_RESISTANCE")
                    || skillToggled(target, "SPIRITUAL_ATTACK_RESISTANCE");
            case ENERGY, SEVERANCE -> false;
        };
    }

    private static boolean matchingNullification(LivingEntity target, Family family) {
        return switch (family) {
            case MAGIC -> skillToggled(target, "MAGIC_NULLIFICATION");
            case HOLY -> skillToggled(target, "HOLY_ATTACK_NULLIFICATION");
            case SOUL -> skillToggled(target, "SPIRITUAL_ATTACK_NULLIFICATION");
            case ELEMENTAL -> skillToggled(target, "EARTH_ATTACK_NULLIFICATION")
                    || skillToggled(target, "SPIRITUAL_ATTACK_NULLIFICATION");
            case ENERGY, SEVERANCE -> false;
        };
    }

    private static JsonObject matchingDefenseDetails(LivingEntity target, Family family) {
        JsonObject json = new JsonObject();
        switch (family) {
            case ELEMENTAL -> {
                json.addProperty("EARTH_ATTACK_RESISTANCE", skillToggled(target, "EARTH_ATTACK_RESISTANCE"));
                json.addProperty("EARTH_ATTACK_NULLIFICATION", skillToggled(target, "EARTH_ATTACK_NULLIFICATION"));
                json.addProperty("SPIRITUAL_ATTACK_RESISTANCE", skillToggled(target, "SPIRITUAL_ATTACK_RESISTANCE"));
                json.addProperty("SPIRITUAL_ATTACK_NULLIFICATION", skillToggled(target, "SPIRITUAL_ATTACK_NULLIFICATION"));
            }
            case ENERGY -> json.addProperty("native_operation_uses_damage_resistance", false);
            case SEVERANCE -> {
                json.addProperty("native_wound_uses_matching_resistance", false);
                json.addProperty("native_wound_cancellation", "NO_SEVERANCE entity tag, physical-converted source, or mastered Suppressor");
            }
            default -> {
                json.addProperty("matching_resistance_present", matchingResistance(target, family));
                json.addProperty("matching_nullification_present", matchingNullification(target, family));
            }
        }
        return json;
    }

    private static boolean skillToggled(LivingEntity target, String field) {
        try {
            Object supplier = staticField("io.github.manasmods.tensura.registry.skill.ResistanceSkills", field);
            Object skill = invoke(supplier, "get");
            return booleanValue(invoke(Class.forName("io.github.manasmods.tensura.ability.SkillUtils"),
                    "isSkillToggled", target, skill));
        }
        catch (ReflectiveOperationException exception) {
            throw new IllegalStateException("could not inspect Tensura skill " + field, exception);
        }
    }

    private static JsonArray readTraits(Object cap) throws ReflectiveOperationException {
        JsonArray traits = new JsonArray();
        Object value = readField(cap, "traits");
        if (value instanceof Map<?, ?> map) {
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
            return new ResourceState(existence.getSpiritualHealth(),
                    attribute(entity, TensuraAttributes.MAX_SPIRITUAL_HEALTH),
                    existence.getMagicule(), existence.getAura());
        }
        catch (Throwable ignored) {
            return new ResourceState(0.0D, 0.0D, 0.0D, 0.0D);
        }
    }

    private static double severance(LivingEntity entity) {
        try {
            return TensuraStorages.getEffectFrom(entity).getSeveranceAmount();
        }
        catch (Throwable ignored) {
            return 0.0D;
        }
    }

    private static JsonObject readAttributes(LivingEntity entity, Collection<ResourceLocation> ids) {
        JsonObject result = new JsonObject();
        for (ResourceLocation id : ids) result.addProperty(id.toString(), attribute(entity, id, 0.0D));
        return result;
    }

    private static JsonObject readStackAttributes(ItemStack stack) {
        JsonObject result = new JsonObject();
        Map<String, Double> values = new LinkedHashMap<>();
        stack.forEachModifier(EquipmentSlot.MAINHAND, (attribute, modifier) ->
                values.merge(holderId(attribute), modifier.amount(), Double::sum));
        values.forEach(result::addProperty);
        return result;
    }

    private static double attribute(LivingEntity entity, Holder<Attribute> attribute) {
        return entity.getAttributes().hasAttribute(attribute) ? entity.getAttributeValue(attribute) : 0.0D;
    }

    private static double attribute(LivingEntity entity, ResourceLocation id, double fallback) {
        Optional<Holder.Reference<Attribute>> holder = BuiltInRegistries.ATTRIBUTE.getHolder(id);
        return holder.isPresent() && entity.getAttributes().hasAttribute(holder.get())
                ? entity.getAttributeValue(holder.get()) : fallback;
    }

    private static double multiplier(LivingEntity entity, Holder<Attribute> attribute) {
        AttributeInstance instance = entity.getAttribute(attribute);
        if (instance == null || instance.getBaseValue() == 0.0D) return 0.0D;
        return instance.getValue() / instance.getBaseValue();
    }

    private static void setBase(LivingEntity entity, Holder<Attribute> attribute, double value) {
        AttributeInstance instance = entity.getAttribute(attribute);
        if (instance != null) instance.setBaseValue(value);
    }

    private static String damageType(net.minecraft.world.damagesource.DamageSource source) {
        return holderId(source.typeHolder());
    }

    private static Set<String> sourceTags(net.minecraft.world.damagesource.DamageSource source) {
        Set<String> tags = new LinkedHashSet<>();
        SOURCE_TAGS.forEach((name, tag) -> {
            if (source.is(tag)) tags.add(name);
        });
        return tags;
    }

    private static String traitId(Object trait) {
        try {
            Object entry = invoke(trait, "getEntry");
            Object id = invoke(entry, "getId");
            if (id instanceof ResourceLocation resource) return resource.toString();
        }
        catch (Throwable ignored) {
        }
        return String.valueOf(trait);
    }

    private static JsonArray strings(Collection<?> values) {
        JsonArray array = new JsonArray();
        values.forEach(value -> array.add(String.valueOf(value)));
        return array;
    }

    private static <T> Set<T> union(Set<T> first, Set<T> second) {
        Set<T> result = new LinkedHashSet<>(first);
        result.addAll(second);
        return result;
    }

    private static void log(String kind, JsonObject payload) {
        payload.addProperty("schema", ENDGAME_RESEARCH ? "tno.phase6.endgame_research.v1"
                : SUITE_C ? "tno.phase5f.suite_c.v1" : "tno.phase5f.suite_b.v1");
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

    private static Method findMethod(Class<?> type, String name, Object[] args) throws NoSuchMethodException {
        for (Method method : type.getMethods()) {
            if (method.getName().equals(name) && compatible(method.getParameterTypes(), args)) return method;
        }
        for (Class<?> current = type; current != null; current = current.getSuperclass()) {
            for (Method method : current.getDeclaredMethods()) {
                if (method.getName().equals(name) && compatible(method.getParameterTypes(), args)) return method;
            }
        }
        throw new NoSuchMethodException(type.getName() + "#" + name + "/" + args.length);
    }

    private static boolean compatible(Class<?>[] parameters, Object[] args) {
        if (parameters.length != args.length) return false;
        for (int i = 0; i < parameters.length; i++) {
            if (args[i] == null) {
                if (parameters[i].isPrimitive()) return false;
            }
            else if (!wrap(parameters[i]).isAssignableFrom(args[i].getClass())) return false;
        }
        return true;
    }

    private static Class<?> wrap(Class<?> type) {
        if (!type.isPrimitive()) return type;
        if (type == boolean.class) return Boolean.class;
        if (type == byte.class) return Byte.class;
        if (type == short.class) return Short.class;
        if (type == int.class) return Integer.class;
        if (type == long.class) return Long.class;
        if (type == float.class) return Float.class;
        if (type == double.class) return Double.class;
        if (type == char.class) return Character.class;
        return type;
    }

    private static Object readField(Object target, String name) throws ReflectiveOperationException {
        return findField(target.getClass(), name).get(target);
    }

    private static Field findField(Class<?> type, String name) throws NoSuchFieldException {
        for (Class<?> current = type; current != null; current = current.getSuperclass()) {
            try {
                Field field = current.getDeclaredField(name);
                field.setAccessible(true);
                return field;
            }
            catch (NoSuchFieldException ignored) {
            }
        }
        throw new NoSuchFieldException(type.getName() + "#" + name);
    }

    private static Number numberValue(Object value) {
        if (value instanceof Number number) return number;
        throw new IllegalArgumentException("expected number, got " + value);
    }

    private static boolean booleanValue(Object value) {
        return value instanceof Boolean bool && bool;
    }

    private static String holderId(Object holder) {
        if (holder instanceof Holder<?> vanilla) {
            return vanilla.unwrapKey().map(key -> key.location().toString()).orElse(String.valueOf(vanilla.value()));
        }
        return String.valueOf(holder);
    }

    private static String summarize(Throwable throwable) {
        Throwable root = throwable;
        while (root.getCause() != null && root.getCause() != root) root = root.getCause();
        return root.getClass().getSimpleName() + (root.getMessage() == null ? "" : ": " + root.getMessage());
    }

    private static ResourceLocation id(String namespace, String path) {
        return ResourceLocation.fromNamespaceAndPath(namespace, path);
    }

    private static BossSpec boss(String namespace, String path, int min, int max, boolean primary) {
        return new BossSpec(id(namespace, path), min, max, primary);
    }

    private enum Phase {
        SPAWN, WAIT_ATTACHMENT, CONFIGURE_LEVEL, WAIT_SCALING, WAIT_CLONE, RUN, FINISH, DONE
    }

    private enum LevelMode {
        NATURAL_REPRESENTATIVE, NATURAL_MAXIMUM, STRESS, ENDGAME_TARGET
    }

    private enum Family {
        MAGIC("MAGIC_WEAPON", id("tensura", "magic_weapon"), id("tensura", "magic")),
        HOLY("HOLY_WEAPON", id("tensura", "holy_weapon"), id("tensura", "holy_damage")),
        SOUL("SOUL_EATER", id("tensura", "soul_eater"), id("tensura", "soul_scatter")),
        ELEMENTAL("ELEMENTAL_SLOTTING", id("tensura", "slotting"), id("tensura", "earth_elemental")),
        ENERGY("ENERGY_STEAL", id("tensura", "energy_steal"), null),
        SEVERANCE("SEVERANCE", id("tensura", "severance"), null);

        final String id;
        final ResourceLocation enchantment;
        final ResourceLocation damageType;

        Family(String id, ResourceLocation enchantment, ResourceLocation damageType) {
            this.id = id;
            this.enchantment = enchantment;
            this.damageType = damageType;
        }

        boolean matchesDamageType(String value) {
            return damageType != null && damageType.toString().equals(value);
        }

        static Family parse(String value) {
            for (Family family : values()) {
                if (family.name().equalsIgnoreCase(value) || family.id.equalsIgnoreCase(value)) return family;
            }
            throw new IllegalArgumentException("phase5f_suite_b_family must be magic, holy, soul, elemental, energy, or severance");
        }
    }

    private record BossSpec(ResourceLocation id, int minLevel, int maxLevel, boolean primary) {
    }

    private record LevelEntry(int level, LevelMode mode) {
    }

    private record Stage(String name, Long ep, double bonus, double penetration) {
        double coefficient(Family family) {
            if (name.equals("Native")) return 1.0D;
            if (ENDGAME_RESEARCH) return 1.0D + bonus;
            return switch (family) {
                case SOUL, ENERGY -> 1.0D + bonus;
                case SEVERANCE -> 1.0D + bonus * ((2.4D + SEVERANCE_NATIVE_ATTACK_BONUS)
                        / SEVERANCE_NATIVE_ATTACK_BONUS);
                default -> 1.0D + 2.0D * bonus;
            };
        }
    }

    private record ProfileKey(ResourceLocation boss, int level, LevelMode mode) {
    }

    private record CaseSpec(BossSpec boss, int level, LevelMode mode, Stage stage) {
        ProfileKey profileKey() {
            return new ProfileKey(boss.id, level, mode);
        }
    }

    private record FamilyProbe(double raw, double scaled, double nativeAfterResistance,
                               double stagedAmount, boolean sourceBypass,
                               Set<String> tags, boolean l2Magic) {
    }

    private record SeveranceProjection(double nativePre, double stagedPre, double basePost,
                                        double nativePost, double stagedPost) {
    }

    private record ResourceState(double shp, double maxShp, double magicules, double aura) {
    }
}
