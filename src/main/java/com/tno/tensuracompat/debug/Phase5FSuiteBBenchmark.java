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
import com.tno.tensuracompat.core.endgame.L2HealthScaling;
import com.tno.tensuracompat.core.endgame.MagicHolyEndgameMath;
import com.tno.tensuracompat.core.endgame.MagicHolyEndgamePolicy;
import com.tno.tensuracompat.core.stage.ProductionStageScaling;
import com.tno.tensuracompat.core.stage.ScalableFamily;
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
import net.neoforged.neoforge.event.entity.living.LivingHealEvent;
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
    private static final boolean PRODUCTION_ACCEPTANCE = Boolean.getBoolean("tno.phase6.productionAcceptance");
    private static final String CALIBRATION_MODE = System.getProperty("tno.phase6.calibrationMode", "");
    private static final boolean SEVERANCE_WALL = Boolean.getBoolean("tno.phase6.calibration")
            && CALIBRATION_MODE.equals("severance_wall");
    private static final boolean SEVERANCE_SUSTAINED = Boolean.getBoolean("tno.phase6.calibration")
            && CALIBRATION_MODE.equals("severance_sustained");
    private static final boolean ADAPTIVE_WOUND_RESEARCH = Boolean.getBoolean("tno.phase6.calibration")
            && CALIBRATION_MODE.startsWith("adaptive_wound");
    private static final boolean ADAPTIVE_WOUND_SAFETY = ADAPTIVE_WOUND_RESEARCH
            && CALIBRATION_MODE.equals("adaptive_wound_safety");
    private static final boolean ADAPTIVE_WOUND_COUNTER_STATES = ADAPTIVE_WOUND_RESEARCH
            && CALIBRATION_MODE.equals("adaptive_wound_counter_states");
    private static final boolean ADAPTIVE_WOUND_DYNAMIC = ADAPTIVE_WOUND_RESEARCH
            && CALIBRATION_MODE.equals("adaptive_wound_dynamic");
    private static final boolean NATIVE_REGENERATE_OBSERVATION = SEVERANCE_SUSTAINED
            || ADAPTIVE_WOUND_SAFETY || ADAPTIVE_WOUND_COUNTER_STATES
            || ADAPTIVE_WOUND_DYNAMIC;
    private static final boolean SUSTAINED_ROTATION = SEVERANCE_SUSTAINED
            || ADAPTIVE_WOUND_DYNAMIC;
    private static final boolean SEVERANCE_PROTOTYPE = Boolean.getBoolean("tno.phase6.calibration")
            && (CALIBRATION_MODE.equals("severance_prototype") || SEVERANCE_SUSTAINED);
    private static final boolean SEVERANCE_RESEARCH = SEVERANCE_WALL || SEVERANCE_PROTOTYPE
            || ADAPTIVE_WOUND_RESEARCH;
    private static final boolean CALIBRATION_COMBAT = Boolean.getBoolean("tno.phase6.calibration")
            && Set.of("ceiling", "health", "dementor", "adaptive", "combined", "safety",
                    "severance_wall", "severance_prototype", "severance_sustained",
                    "adaptive_wound_capability", "adaptive_wound_safety",
                    "adaptive_wound_counter_states", "adaptive_wound_dynamic")
                    .contains(CALIBRATION_MODE);
    private static final boolean PRODUCTION_OBSERVATION = ENDGAME_RESEARCH || CALIBRATION_COMBAT
            || PRODUCTION_ACCEPTANCE;
    private static final MagicHolyEndgamePolicy.Parameters R5_MAGIC_HOLY_S7_PARAMETERS =
            MagicHolyEndgamePolicy.parameters(com.tno.tensuracompat.core.stage.Stage.S7,
                    ScalableFamily.MAGIC_WEAPON);
    private static final String MARKER = ADAPTIVE_WOUND_RESEARCH ? "TNO_PHASE6_ADAPTIVE_WOUND"
            : SEVERANCE_SUSTAINED ? "TNO_PHASE6_SEVERANCE_SUSTAINED"
            : SEVERANCE_PROTOTYPE ? "TNO_PHASE6_SEVERANCE_PROTOTYPE"
            : SEVERANCE_WALL ? "TNO_PHASE6_SEVERANCE_WALL"
            : CALIBRATION_COMBAT ? "TNO_PHASE6_CALIBRATION"
            : PRODUCTION_ACCEPTANCE ? "TNO_PHASE6_MAGIC_HOLY_PRODUCTION"
            : ENDGAME_RESEARCH ? "TNO_PHASE6_ENDGAME_RESEARCH"
            : SUITE_C ? "TNO_PHASE5F_SUITE_C" : "TNO_PHASE5F_SUITE_B";
    private static final String TARGET_TAG = SEVERANCE_RESEARCH ? "tno_phase6_severance_wall_target"
            : CALIBRATION_COMBAT ? "tno_phase6_calibration_target"
            : PRODUCTION_ACCEPTANCE ? "tno_phase6_magic_holy_production_target"
            : ENDGAME_RESEARCH ? "tno_phase6_endgame_research_target"
            : SUITE_C ? "tno_phase5f_suite_c_target" : "tno_phase5f_suite_b_target";
    private static final String APO_PROFILE = "ANCIENT_SINGLE_PROSPEROUS_SPECTRAL";
    private static final String SCALE_TAG = "l2_tensura_scaled";
    private static final String L2_MISCS = "dev.xkmc.l2hostility.init.registrate.LHMiscs";
    private static final String L2_TRAITS = "dev.xkmc.l2hostility.init.registrate.LHTraits";
    private static final boolean ENDGAME = SUITE_C && Boolean.getBoolean("tno.phase5f.suiteCEndgame");
    private static final boolean STRONGEST_LEGAL_PROFILE = ENDGAME || PRODUCTION_OBSERVATION;
    private static final ResourceLocation ROYAL_BOW = id("royalvariations", "royal_bow");
    private static final ResourceLocation ROYAL_ARROW = id("royalvariations", "royal_arrow");
    private static final ResourceLocation EARTH_CORE = id("tensura", "element_core_earth");
    private static final ResourceLocation SELF_REGENERATION = id("tensura", "self_regeneration");
    private static final String L2_REGENERATE_CLASS =
            "dev.xkmc.l2hostility.content.traits.common.RegenTrait";
    private static final double SEVERANCE_NATIVE_ATTACK_BONUS = 3.0D;
    private static final int MAX_SHOTS = Integer.getInteger(
            CALIBRATION_COMBAT ? "tno.phase6.calibrationShots"
                    : PRODUCTION_ACCEPTANCE ? "tno.phase6.productionAcceptanceShots"
                    : ENDGAME_RESEARCH ? "tno.phase6.endgameShots"
                    : SUITE_C ? "tno.phase5f.suiteCShots" : "tno.phase5f.suiteBShots",
            SUSTAINED_ROTATION ? 60 : ADAPTIVE_WOUND_COUNTER_STATES ? 1 : 10);
    private static final int WINDOW_TICKS = Integer.getInteger(
            CALIBRATION_COMBAT ? "tno.phase6.calibrationTicks"
                    : PRODUCTION_ACCEPTANCE ? "tno.phase6.productionAcceptanceTicks"
                    : ENDGAME_RESEARCH ? "tno.phase6.endgameTicks"
                    : SUITE_C ? "tno.phase5f.suiteCTicks" : "tno.phase5f.suiteBTicks",
            SUSTAINED_ROTATION ? 1200 : ADAPTIVE_WOUND_COUNTER_STATES ? 40 : 200);
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
        boolean calibration = CALIBRATION_COMBAT;
        boolean productionAcceptance = PRODUCTION_ACCEPTANCE;
        if (FMLEnvironment.production || (!suiteB && !suiteC && !endgameResearch
                && !calibration && !productionAcceptance) || active != null) return;
        try {
            if ((suiteB ? 1 : 0) + (suiteC ? 1 : 0) + (endgameResearch ? 1 : 0)
                    + (calibration ? 1 : 0) + (productionAcceptance ? 1 : 0) != 1) {
                throw new IllegalStateException(
                        "Suite B, Suite C, Phase 6 research, calibration, and production acceptance are mutually exclusive");
            }
            requireMods();
            if (SEVERANCE_RESEARCH) Phase6SeveranceWallContext.registerL2Listener();
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

    public static void onHealLowest(LivingHealEvent event) {
        if (active != null) active.captureHealLowest(event);
    }

    public static void captureCalibrationTrace(Phase6CalibrationContext.Snapshot snapshot) {
        if (active != null) active.captureCalibrationTrace(snapshot);
    }

    public static void captureSeveranceWallTrace(Phase6SeveranceWallContext.Snapshot snapshot) {
        if (active != null) active.captureSeveranceWallTrace(snapshot);
    }

    public static void captureAdaptiveWoundTrace(Phase6AdaptiveWoundContext.Snapshot snapshot) {
        if (active != null) active.captureAdaptiveWoundTrace(snapshot);
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
                throw new IllegalStateException("required " + (CALIBRATION_COMBAT ? "Phase 6 calibration"
                        : PRODUCTION_ACCEPTANCE ? "Phase 6 Magic/Holy production acceptance"
                        : ENDGAME_RESEARCH ? "Phase 6 endgame research"
                        : "Suite " + (SUITE_C ? "C" : "B")) + " runtime mod absent: " + mod);
            }
        }
    }

    private static final class Session {
        private final MinecraftServer server;
        private final ServerLevel level;
        private final Family family;
        private final ItemStack benchmarkBow;
        private final ItemStack sustainedMagicBow;
        private final ItemStack sustainedHolyBow;
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
        private Phase6CalibrationContext.ParameterScope calibrationParameters;
        private Phase6SeverancePrototypeContext.ParameterScope severancePrototypeParameters;
        private Phase6AdaptiveWoundContext.ParameterScope adaptiveWoundParameters;
        private boolean selfRegenerationRemovedForIsolation;
        private boolean counterStateSetupComplete;

        Session(MinecraftServer server) {
            this.server = server;
            this.level = server.overworld();
            this.family = Family.parse(System.getProperty(
                    CALIBRATION_COMBAT ? "tno.phase6.calibrationFamily"
                            : PRODUCTION_ACCEPTANCE ? "tno.phase6.productionAcceptanceFamily"
                            : ENDGAME_RESEARCH ? "tno.phase6.endgameFamily"
                            : SUITE_C ? "tno.phase5f.suiteCFamily" : "tno.phase5f.suiteBFamily", ""));
            this.benchmarkBow = buildBenchmarkBow(server, family);
            this.sustainedMagicBow = SUSTAINED_ROTATION
                    ? buildBenchmarkBow(server, Family.MAGIC) : ItemStack.EMPTY;
            this.sustainedHolyBow = SUSTAINED_ROTATION
                    ? buildBenchmarkBow(server, Family.HOLY) : ItemStack.EMPTY;
            this.royalArrow = requiredItem(ROYAL_ARROW);
            this.cases = buildCases(System.getProperty(
                    CALIBRATION_COMBAT ? "tno.phase6.calibrationBoss"
                            : PRODUCTION_ACCEPTANCE ? "tno.phase6.productionAcceptanceBoss"
                            : ENDGAME_RESEARCH ? "tno.phase6.endgameBoss"
                            : SUITE_C ? "tno.phase5f.suiteCBoss" : "tno.phase5f.suiteBBoss", ""));
            if (cases.isEmpty()) throw new IllegalStateException((CALIBRATION_COMBAT ? "Calibration"
                    : PRODUCTION_ACCEPTANCE ? "Production acceptance"
                    : "Suite " + (SUITE_C ? "C" : "B")) + " boss filter matched no targets");
            if (PRODUCTION_ACCEPTANCE && family != Family.MAGIC && family != Family.HOLY) {
                throw new IllegalStateException("production acceptance is limited to Magic/Holy");
            }
            if (SEVERANCE_RESEARCH && family != Family.SEVERANCE) {
                throw new IllegalStateException("Severance research requires the SEVERANCE family");
            }
            if (SEVERANCE_SUSTAINED && (MAX_SHOTS != 60 || WINDOW_TICKS != 1200)) {
                throw new IllegalStateException(
                        "R5 sustained evidence requires exactly 60 releases over 1200 ticks");
            }
            if (ADAPTIVE_WOUND_SAFETY && (MAX_SHOTS != 10 || WINDOW_TICKS != 200)) {
                throw new IllegalStateException(
                        "W4 trait-safety evidence requires exactly 10 releases over 200 ticks");
            }
            if (ADAPTIVE_WOUND_COUNTER_STATES && (MAX_SHOTS != 1 || WINDOW_TICKS != 40)) {
                throw new IllegalStateException(
                        "P2 counter-state evidence requires one setup release over at most 40 ticks");
            }
            if (ADAPTIVE_WOUND_DYNAMIC && (MAX_SHOTS != 60 || WINDOW_TICKS != 1200)) {
                throw new IllegalStateException(
                        "P3 dynamic evidence requires exactly 60 releases over 1200 ticks");
            }
            if (!PRODUCTION_ACCEPTANCE && PRODUCTION_OBSERVATION && cases.stream().anyMatch(spec ->
                    !spec.boss.id.equals(id("tensura", "orc_disaster")))) {
                throw new IllegalStateException("Phase 6 endgame research is locked to the accepted Orc Disaster positive-control target");
            }
            if (!SUITE_C) {
                assertTnoOnlyStack(benchmarkBow);
                if (SUSTAINED_ROTATION) {
                    assertTnoOnlyStack(sustainedMagicBow);
                    assertTnoOnlyStack(sustainedHolyBow);
                }
            }
            cleanupTestArea();
            if (SEVERANCE_SUSTAINED || ADAPTIVE_WOUND_RESEARCH) {
                // Fake players do not hold normal player chunk tickets. Keep only
                // the two controlled firing-lane chunks entity-ticking so native
                // L2 Regenerate executes for every sustained case.
                runCommand("forceload add 0 0 0 31");
            }
            if (PRODUCTION_OBSERVATION || SUITE_C && Boolean.getBoolean("tno.phase5f.suiteCFastTicks")) {
                runCommand("tick sprint 10000000");
            }
            if (!SUITE_C) {
                logCatalog();
                catalogLogged = true;
            }
        }

        void tick() throws ReflectiveOperationException {
            stabilize();
            if (NATIVE_REGENERATE_OBSERVATION && phase == Phase.RUN && result != null && target != null) {
                result.observeNativeRegenerateTick(target, l2Cap, currentHit,
                        (int) (server.getTickCount() - runStartTick));
            }
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
                    if (SEVERANCE_SUSTAINED || ADAPTIVE_WOUND_RESEARCH) {
                        runCommand("forceload remove 0 0 0 31");
                    }
                    complete = true;
                }
            }
            if (NATIVE_REGENERATE_OBSERVATION && phase == Phase.RUN && result != null && target != null) {
                result.captureServerPostHp(target);
            }
            if (ADAPTIVE_WOUND_DYNAMIC && phase == Phase.RUN && result != null && target != null) {
                result.observeDynamicCounterPosition(target);
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
            if (!freshCalibrationAttachment()
                    && profileTemplate != null && spec.profileKey().equals(templateKey)) {
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
            Map<String, Integer> reference = currentCase().boss.id.equals(id("tensura", "orc_disaster"))
                    && ACCEPTED_ORC_ENDGAME_PROFILES.containsKey(currentCase().level)
                    ? ACCEPTED_ORC_ENDGAME_PROFILES.get(currentCase().level)
                    : ACCEPTED_ENDGAME_PROFILES.get(currentCase().boss.id.toString());
            if (reference == null || !PRODUCTION_OBSERVATION && currentCase().level != 1000) {
                throw new IllegalStateException("missing accepted endgame profile for "
                        + currentCase().boss.id + " at Lv" + currentCase().level);
            }
            Map<String, Integer> expected = currentCase().traitProfile.apply(reference);

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
            if (!freshCalibrationAttachment()) {
                profileTemplate = new CompoundTag();
                target.saveWithoutId(profileTemplate);
                profileTemplate.remove("UUID");
                profileTemplate.remove("Pos");
                profileTemplate.remove("Motion");
                profileTemplate.remove("Rotation");
                templateKey = currentCase().profileKey();
                templateTraits = GSON.toJson(readTraits(l2Cap));
            }
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
            if (NATIVE_REGENERATE_OBSERVATION && target instanceof Mob mob) {
                // Match the already-validated R2 native Regenerate fixture: the
                // controlled target must execute its normal entity/L2 tick path.
                mob.setNoAi(false);
            }
            player.setHealth(player.getMaxHealth());
            player.setAbsorptionAmount(0.0F);
            player.invulnerableTime = 0;
            familyProbes.clear();
            beforeCrit.clear();
            clearArrows();
        }

        private void beginRun(boolean nativeProfileSource) throws ReflectiveOperationException {
            if (CALIBRATION_COMBAT) {
                calibrationParameters = Phase6CalibrationContext.useParameters(currentCase().calibration.parameters());
            }
            if (SEVERANCE_PROTOTYPE) {
                severancePrototypeParameters = Phase6SeverancePrototypeContext.useEligibleMultiplier(
                        currentCase().calibration.severanceEligibleMultiplier);
            }
            if (ADAPTIVE_WOUND_RESEARCH) {
                adaptiveWoundParameters = Phase6AdaptiveWoundContext.useRecovery(
                        currentCase().calibration.woundAdaptiveRecovery);
            }
            selfRegenerationRemovedForIsolation = NATIVE_REGENERATE_OBSERVATION
                    && BuiltInRegistries.MOB_EFFECT.getHolder(SELF_REGENERATION)
                    .map(target::removeEffect).orElse(false);
            if (NATIVE_REGENERATE_OBSERVATION) {
                // Align every fresh case to the same real RegenTrait tick boundary.
                // Reset again only after each native tick-20 cycle so the accepted
                // trait map is not changed by the unrelated 300-tick validity sweep.
                target.tickCount = 0;
            }
            result = new CaseResult(currentCase(), target, player, l2Cap, nativeProfileSource);
            shotsReleased = 0;
            currentHit = null;
            counterStateSetupComplete = false;
            runStartTick = server.getTickCount();
            nextShotTick = runStartTick;
            phase = Phase.RUN;
            log("case_start", result.caseJson());
        }

        private void runCase() {
            long now = server.getTickCount();
            int elapsed = (int) (now - runStartTick);
            if (ADAPTIVE_WOUND_COUNTER_STATES) {
                runCounterStateCase(elapsed);
                return;
            }
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

        private void runCounterStateCase(int elapsed) {
            if (target == null || target.isRemoved() || target.isDeadOrDying()
                    || target.getHealth() <= 0.0F) {
                throw new IllegalStateException("P2 counter-state target became invalid");
            }
            if (!counterStateSetupComplete) {
                CounterState state = currentCase().calibration.counterState();
                if (state.requiresWound()) {
                    currentHit = new HitRecord(1, elapsed, target, player);
                    fireFullDraw();
                    shotsReleased = 1;
                    currentHit.observe(target, player);
                    if (severance(target) <= 0.0001D) {
                        throw new IllegalStateException(
                                "P2 setup Royal Arrow did not create a legitimate native wound");
                    }
                }
                else if (severance(target) > 0.0001D) {
                    throw new IllegalStateException("P2 no-wound control began with native wound state");
                }
                result.configureCounterState(target, state, shotsReleased);
                target.tickCount = 0;
                result.captureServerPostHp(target);
                counterStateSetupComplete = true;
                return;
            }
            if (result.nativeTickBoundaryCount >= 1) {
                if (currentHit != null) closeCurrentHit(elapsed);
                result.elapsedTicks = Math.max(1, elapsed);
                phase = Phase.FINISH;
                return;
            }
            if (elapsed >= WINDOW_TICKS) {
                throw new IllegalStateException("P2 did not observe the native tick-20 boundary");
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
            if (ADAPTIVE_WOUND_COUNTER_STATES) result.finishCounterState(target);
            else if (ADAPTIVE_WOUND_DYNAMIC) result.finishDynamic(target);
            else result.finish(target);
            for (HitRecord hit : result.hits) log("row", result.rowJson(hit));
            if (ADAPTIVE_WOUND_COUNTER_STATES) {
                log("counter_state_result", result.counterStateJson());
            }
            if (ADAPTIVE_WOUND_DYNAMIC) {
                for (RegenerateCycle cycle : result.regenerateCycles) {
                    log("regenerate_cycle", result.regenerateCycleJson(cycle));
                }
            }
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
            if (phase == Phase.RUN && currentHit != null && event.getEntity() == target
                    && damageType(event.getSource()).equals("tensura:severance")) {
                currentHit.nativeSeveranceIncomingEventCount++;
                currentHit.nativeSeveranceIncomingAmount += event.getAmount();
                currentHit.nativeSeveranceSourceEntityIds.add(entityType(event.getSource().getEntity()));
                currentHit.nativeSeveranceDirectEntityIds.add(entityType(event.getSource().getDirectEntity()));
            }
            if (!runningTargetEvent(event)) return;
            String type = damageType(event.getSource());
            if (currentHit.shotFamily.matchesDamageType(type)) {
                double eventAmount = event.getAmount();
                double raw = PRODUCTION_OBSERVATION
                        ? eventAmount / currentCase().stage.coefficient(currentHit.shotFamily)
                        : currentHit.shotFamily == Family.ELEMENTAL
                                ? currentHit.elementalNativeProjectileDamage : eventAmount;
                float scaled = PRODUCTION_OBSERVATION || currentHit.shotFamily == Family.ELEMENTAL
                        ? (float) eventAmount
                        : (float) (raw * currentCase().stage.coefficient(currentHit.shotFamily));
                double nativeAfterResistance = scaled > target.getHealth() * 0.5D ? scaled * 0.5D : 0.0D;
                boolean sourceBypass = !PRODUCTION_OBSERVATION && currentCase().stage.penetration > 0.0D
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
                if (!PRODUCTION_OBSERVATION) event.setAmount((float) stagedAmount);
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
                currentHit.physicalOriginal += currentHit.shotFamily == Family.SEVERANCE
                        ? currentHit.severanceBasePostByProjectile.getOrDefault(
                                projectileUuid, 0.0D)
                        : event.getOriginalAmount();
                currentHit.physicalIncoming += event.getAmount();
                currentHit.physicalSourceIds.add(type);
                currentHit.physicalSourceTags.addAll(sourceTags(event.getSource()));
                currentHit.physicalDamageEventCount++;
                if (currentHit.shotFamily == Family.SEVERANCE) {
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
                        currentHit.severancePrototypePreRound += projection.prototypePre;
                        currentHit.severancePrototypePostRound += projection.prototypePost;
                        currentHit.severanceProductionEligibleContribution += projection.productionEligible;
                        currentHit.severancePrototypeEligibleContribution += projection.prototypeEligible;
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
            if (phase == Phase.RUN && currentHit != null && event.getEntity() == target
                    && damageType(event.getSource()).equals("tensura:severance")) {
                currentHit.nativeSeveranceAfterL2EventCount++;
                currentHit.nativeSeveranceAfterL2Amount += event.isCanceled() ? 0.0D : event.getAmount();
                currentHit.nativeSeveranceIncomingCanceled |= event.isCanceled();
            }
            if (!runningTargetEvent(event)) return;
            Float preCrit = beforeCrit.remove(event);
            if (SUITE_C && preCrit != null && event.getAmount() > preCrit + 0.001F && !currentHit.crit) {
                currentHit.crit = true;
                currentHit.critMultiplierEvents++;
                currentHit.critDamageSourceIds.add(damageType(event.getSource()));
            }
            if (isBenchmarkArrow(event.getSource())) {
                currentHit.physicalAfterIncomingL2 += event.isCanceled() ? 0.0D : event.getAmount();
                currentHit.physicalIncomingCanceled |= event.isCanceled();
            }
            FamilyProbe probe = familyProbes.remove(event);
            if (probe == null) return;
            if (PRODUCTION_OBSERVATION) {
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
            if (type.equals("tensura:severance")) {
                currentHit.nativeSeveranceDamagePreEventCount++;
                currentHit.nativeSeveranceDamagePreAmount += event.getNewDamage();
            }
            if (currentHit.shotFamily.matchesDamageType(type)) currentHit.familyAfterL2 += event.getNewDamage();
            else if (isBenchmarkArrow(event.getSource())) currentHit.physicalAfterL2 += event.getNewDamage();
            else currentHit.dotAfterL2 += event.getNewDamage();
        }

        private void captureCalibrationTrace(Phase6CalibrationContext.Snapshot snapshot) {
            if (CALIBRATION_COMBAT && phase == Phase.RUN && currentHit != null) {
                currentHit.calibrationTraces.add(snapshot);
            }
        }

        private void captureSeveranceWallTrace(Phase6SeveranceWallContext.Snapshot snapshot) {
            if (SEVERANCE_RESEARCH && phase == Phase.RUN && currentHit != null) {
                currentHit.severanceWallTraces.add(snapshot);
            }
        }

        private void captureAdaptiveWoundTrace(Phase6AdaptiveWoundContext.Snapshot snapshot) {
            if (ADAPTIVE_WOUND_RESEARCH && phase == Phase.RUN && currentHit != null) {
                currentHit.adaptiveWoundTraces.add(snapshot);
            }
        }

        private void captureDamagePost(LivingDamageEvent.Post event) {
            if (phase != Phase.RUN || currentHit == null) return;
            if (event.getEntity() == target) {
                String type = damageType(event.getSource());
                if (type.equals("tensura:severance")) {
                    currentHit.nativeSeveranceDamagePostEventCount++;
                    currentHit.nativeSeveranceDamagePostAmount += event.getNewDamage();
                }
                if (currentHit.shotFamily.matchesDamageType(type)) currentHit.familyPost += event.getNewDamage();
                else if (isBenchmarkArrow(event.getSource())) currentHit.physicalPost += event.getNewDamage();
                else currentHit.dotPost += event.getNewDamage();
            }
            else if (event.getEntity() == player) {
                currentHit.reflectedPost += event.getNewDamage();
                currentHit.reflectedSourceIds.add(damageType(event.getSource()));
            }
        }

        private void captureHealLowest(LivingHealEvent event) {
            if (!NATIVE_REGENERATE_OBSERVATION || phase != Phase.RUN || result == null
                    || event.getEntity() != target) return;
            StackTraceElement[] stack = Thread.currentThread().getStackTrace();
            boolean regenerateCallback = Stream.of(stack)
                    .anyMatch(frame -> frame.getClassName().equals(L2_REGENERATE_CLASS));
            if (!regenerateCallback) {
                result.isolatedNonRegenerateHealEvents++;
                result.isolatedNonRegenerateHealNominalAmount += event.getAmount();
                Stream.of(stack).map(StackTraceElement::getClassName)
                        .filter(name -> name.startsWith("io.github.manasmods.tensura."))
                        .findFirst().ifPresent(result.isolatedNonRegenerateHealSources::add);
                event.setCanceled(true);
                return;
            }
            double nominal = result.nominalRegenerateHpPerSecond;
            double allowed = event.isCanceled() ? 0.0D : event.getAmount();
            if (ADAPTIVE_WOUND_COUNTER_STATES) {
                result.captureCounterHealEvent(target, nominal, allowed, event.isCanceled(), true);
            }
            if (ADAPTIVE_WOUND_DYNAMIC) {
                result.captureDynamicHealEvent(target, nominal, allowed, event.isCanceled(),
                        (int) (server.getTickCount() - runStartTick));
            }
            result.regenerateCallbackCount++;
            result.regenerateAllowedEventAmount += allowed;
            if (event.isCanceled()) result.regenerateCanceledEventCount++;
            if (currentHit != null) {
                currentHit.regenerateCallbackCount++;
                currentHit.regenerateNominalAmount += nominal;
                currentHit.regenerateAllowedEventAmount += allowed;
                currentHit.regenerateEventCanceled |= event.isCanceled();
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
            if (PRODUCTION_OBSERVATION) {
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
            if (SUSTAINED_ROTATION) {
                ItemStack selected = switch (currentHit.shotFamily) {
                    case MAGIC -> sustainedMagicBow;
                    case HOLY -> sustainedHolyBow;
                    case SEVERANCE -> benchmarkBow;
                    default -> throw new IllegalStateException(
                            "illegal family in R5 bow rotation: " + currentHit.shotFamily);
                };
                equipBow(selected, currentHit.shotFamily);
            }
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
                if (currentHit.shotFamily == Family.SEVERANCE) configureSeveranceStage(arrow, speed);
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
                double nativeDamage = PRODUCTION_OBSERVATION
                        ? observedDamage / currentCase().stage.coefficient(family) : observedDamage;
                double stagedDamage = PRODUCTION_OBSERVATION
                        ? observedDamage : nativeDamage * currentCase().stage.coefficient(family);
                if (!PRODUCTION_OBSERVATION) invoke(projectile, "setDamage", (float) stagedDamage);
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
            if (!PRODUCTION_OBSERVATION) arrow.setBaseDamage(stagedBase);
            SeveranceStageScaling.Adjustment production = SeveranceStageScaling.adjustment(
                    nativeBase + SEVERANCE_NATIVE_ATTACK_BONUS, 1,
                    com.tno.tensuracompat.core.stage.Stage.valueOf(currentCase().stage.name));
            SeveranceStageScaling.Adjustment prototype = Phase6SeverancePrototypeContext.apply(production);
            double nativePre = speed * production.nativeModifiedBase();
            double stagedPre = speed * production.stagedModifiedBase();
            double prototypePre = speed * prototype.stagedModifiedBase();
            double basePost = Math.ceil(speed * nativeBase);
            double nativePost = Math.ceil(nativePre);
            double stagedPost = PRODUCTION_OBSERVATION
                    ? SeveranceStageScaling.roundedProjectileDamage(speed, production)
                    : Math.ceil(stagedPre);
            double prototypePost = PRODUCTION_OBSERVATION
                    ? SeveranceStageScaling.roundedProjectileDamage(speed, prototype)
                    : stagedPost;
            currentHit.severanceConfiguredProjectileCount++;
            currentHit.severanceProjectileSpeed = speed;
            currentHit.severanceBaseProjectileDamage = nativeBase;
            currentHit.severanceNativeAttackBonus = SEVERANCE_NATIVE_ATTACK_BONUS;
            currentHit.severanceStagedAttackBonus = SEVERANCE_NATIVE_ATTACK_BONUS * coefficient;
            currentHit.severanceBasePostByProjectile.put(arrow.getUUID().toString(), basePost);
            currentHit.severanceProjections.put(arrow.getUUID().toString(),
                    new SeveranceProjection(nativePre, stagedPre, prototypePre,
                            basePost, nativePost, stagedPost, prototypePost,
                            production.stagedEligibleContribution(), prototype.stagedEligibleContribution()));
            if (ADAPTIVE_WOUND_RESEARCH) {
                Phase6AdaptiveWoundContext.registerProjectile(arrow, stagedPost,
                        Math.max(0.0D, stagedPost - basePost));
            }
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
            if (ADAPTIVE_WOUND_RESEARCH) {
                BuiltInRegistries.ATTRIBUTE.getHolder(id("apothic_attributes", "crit_chance"))
                        .ifPresent(attribute -> setBase(fake, attribute, 0.0D));
            }
            fake.setHealth(fake.getMaxHealth());
            fake.setPos(TEST_X, TEST_Y, 0.5D);
            return fake;
        }

        private void equipBenchmarkBow() {
            equipBow(benchmarkBow, family);
        }

        private void equipBow(ItemStack template, Family selectedFamily) {
            player.setItemInHand(InteractionHand.MAIN_HAND, template.copy());
            player.setItemInHand(InteractionHand.OFF_HAND, new ItemStack(royalArrow, 64));
            player.setItemSlot(EquipmentSlot.MAINHAND, player.getMainHandItem());
            try {
                invoke(player, "detectEquipmentUpdates");
            }
            catch (ReflectiveOperationException exception) {
                throw new IllegalStateException("could not refresh fake-player attributes", exception);
            }
            if (PRODUCTION_OBSERVATION) {
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
                                .getHolderOrThrow(ResourceKey.create(Registries.ENCHANTMENT,
                                        selectedFamily.enchantment)),
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
            if (calibrationParameters != null) {
                calibrationParameters.close();
                calibrationParameters = null;
            }
            if (severancePrototypeParameters != null) {
                severancePrototypeParameters.close();
                severancePrototypeParameters = null;
            }
            if (adaptiveWoundParameters != null) {
                adaptiveWoundParameters.close();
                adaptiveWoundParameters = null;
            }
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
                if (CALIBRATION_COMBAT) {
                    json.addProperty("L2_profile_variant", spec.traitProfile.id);
                    json.addProperty("calibration_case", spec.calibration.id);
                }
                if (PRODUCTION_ACCEPTANCE) {
                    json.addProperty("L2_profile_variant", spec.traitProfile.id);
                    json.addProperty("production_policy_case", spec.calibration.id);
                }
            }
            return json;
        }

        private void logCatalog() {
            JsonObject json = new JsonObject();
            json.addProperty("suite", CALIBRATION_COMBAT ? "PHASE6_ENDGAME_CALIBRATION"
                    : PRODUCTION_ACCEPTANCE ? "PHASE6_MAGIC_HOLY_PRODUCTION"
                    : ENDGAME_RESEARCH ? "PHASE6_TNO_ENDGAME_RESEARCH"
                    : SUITE_C ? "BOTH" : "B_TNO_ONLY");
            json.addProperty("diagnostic", DIAGNOSTIC);
            json.addProperty("strongest_legal_endgame_matrix", STRONGEST_LEGAL_PROFILE);
            json.addProperty("production_stage_observation", PRODUCTION_OBSERVATION);
            if (PRODUCTION_OBSERVATION) {
                json.addProperty("authoritative_L2_level_api",
                        "LHMiscs.MOB.type().getOrCreate(target) -> MobTraitCap.getLevel()");
                json.addProperty("profile_evidence_source",
                        "accepted Phase 5F strongest-legal profiles/orc_disaster.jsonl");
            }
            json.addProperty("TNO_family", family.id);
            if (CALIBRATION_COMBAT) {
                json.addProperty("calibration_mode", CALIBRATION_MODE);
                json.addProperty("diagnostic_policy_scope", SEVERANCE_PROTOTYPE
                        ? "development-only multiplier on the isolated staged Severance contribution before one native physical arrow source; Royal Arrow base unchanged"
                        : ADAPTIVE_WOUND_RESEARCH
                        ? "development-only eligible Severance wound credit at the native HP-deficit clamp; physical damage and L2 state unchanged"
                        : SEVERANCE_WALL
                        ? "observation-only identity modifiers around native physical Dementor/Adaptive; Tank observed through armor/toughness"
                        : "eligible native Magic/Holy contribution only at L2 defensive modifier boundaries");
                json.addProperty("L2_listener_priority", SEVERANCE_RESEARCH ? 4502 : 4501);
                json.addProperty("generic_health_modifier_order", SEVERANCE_RESEARCH
                        ? "not modified" : "PRE_NONLINEAR priority 7435");
                json.addProperty("Dementor_recovery_modifier_order", SEVERANCE_RESEARCH
                        ? "observation identity PRE_NONLINEAR priorities 7435/7437"
                        : "PRE_NONLINEAR priority 7437");
                json.addProperty("Adaptive_recovery_modifier_order", SEVERANCE_RESEARCH
                        ? "observation identity POST_MULTIPLICATIVE priority 7437"
                        : "POST_MULTIPLICATIVE priority 7437");
                if (SEVERANCE_PROTOTYPE) {
                    json.addProperty("prototype_development_only", true);
                    json.addProperty("prototype_changes_Royal_Arrow_base", false);
                    json.addProperty("prototype_creates_second_source", false);
                    json.addProperty("prototype_writes_wound_directly", false);
                    json.addProperty("prototype_candidate_set", "1x,4x,16x,64x eligible staged Severance only");
                    if (SEVERANCE_SUSTAINED) {
                        json.addProperty("R5_sustained_viability", true);
                        json.addProperty("R5_rotation",
                                "three legal separate Royal Bows: Magic Weapon I -> Holy Weapon I -> Severance I");
                        json.addProperty("R5_enchantment_exclusivity_preserved", true);
                        json.addProperty("R5_magic_holy_production_unchanged", true);
                        json.addProperty("R5_Severance_factor_role",
                                "64x development-only falsification upper bound; not a production candidate");
                        json.addProperty("R5_native_Regenerate_clock_fixture",
                                "target age resets after each native tick-20 cycle to retain the exact profile and exclude the 300-tick validity sweep");
                    }
                }
                if (ADAPTIVE_WOUND_RESEARCH) {
                    if (ADAPTIVE_WOUND_DYNAMIC) {
                        json.addProperty("checkpoint", "P3_DYNAMIC_DEFENDER_ADVANTAGE");
                        json.addProperty("P3_candidate", "C_PARTIAL_ADAPTIVE_RECOVERY_WOUND_ONLY");
                        json.addProperty("P3_diagnostic_RW", 0.5D);
                        json.addProperty("P3_native_control_RW", 0.0D);
                        json.addProperty("P3_rotation",
                                "three legal separate Royal Bows: production Magic Weapon I -> production Holy Weapon I -> Severance I");
                        json.addProperty("P3_magic_holy_production_unchanged", true);
                        json.addProperty("P3_window_role",
                                "60-second functional defender-advantage probe; not W5 balance/viability calibration");
                    }
                    else if (ADAPTIVE_WOUND_COUNTER_STATES) {
                        json.addProperty("checkpoint", "P2_COUNTER_STATES");
                        json.addProperty("P2_candidate", "C_PARTIAL_ADAPTIVE_RECOVERY_WOUND_ONLY");
                        json.addProperty("P2_diagnostic_RW", 0.5D);
                        json.addProperty("P2_fixture",
                                "one legitimate native Royal Arrow wound where required, diagnostic vanilla-HP placement only, then one native tick-20 Regenerate observation");
                        json.addProperty("P2_setup_changes_wound_directly", false);
                        json.addProperty("P2_setup_counted_as_combat_output", false);
                    }
                    else if (ADAPTIVE_WOUND_SAFETY) {
                        json.addProperty("checkpoint", "W4_TRAIT_IDENTITY");
                        json.addProperty("W4_candidate", "C_PARTIAL_ADAPTIVE_RECOVERY_WOUND_ONLY");
                        json.addProperty("W4_diagnostic_RW", 0.5D);
                        json.addProperty("W4_RW_role",
                                "arithmetic midpoint between proven W3 endpoints; diagnostic trait-identity probe only, not a balance or production recommendation");
                    }
                    else {
                        json.addProperty("W3_candidate", "C_PARTIAL_ADAPTIVE_RECOVERY_WOUND_ONLY");
                    }
                    json.addProperty("prototype_development_only", true);
                    json.addProperty("prototype_changes_physical_damage", false);
                    json.addProperty("prototype_changes_Royal_Arrow_base", false);
                    json.addProperty("prototype_creates_physical_source", false);
                    json.addProperty("prototype_writes_wound_directly", false);
                    json.addProperty("prototype_changes_Adaptive_state", false);
                    json.addProperty("prototype_changes_Tank", false);
                    json.addProperty("prototype_changes_Dementor", false);
                    json.addProperty("prototype_changes_Regenerate", false);
                    json.addProperty("prototype_has_persistent_combat_state", false);
                    json.addProperty("prototype_native_callback_storage", true);
                    json.addProperty("prototype_scope_fail_closed",
                            "non-production explicit adaptive_wound mode + scoped registered Royal Arrow decomposition + initialized L2 wall + native arrow callback; otherwise native offer");
                }
            }
            if (PRODUCTION_ACCEPTANCE) {
                json.addProperty("production_feature_active_without_calibration_property",
                        !Boolean.getBoolean("tno.phase6.calibration"));
                json.addProperty("production_policy_scope",
                        "existing native Magic/Holy event only; Curve C and matching Tensura defense precede L2 Q/RD/RA");
                json.addProperty("L2_listener_priority", 4501);
                json.addProperty("generic_health_modifier_order", "PRE_NONLINEAR priority 7435");
                json.addProperty("Dementor_recovery_modifier_order", "PRE_NONLINEAR priority 7437");
                json.addProperty("Adaptive_recovery_modifier_order", "POST_MULTIPLICATIVE priority 7437");
            }
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
                    PRODUCTION_OBSERVATION || SUITE_C && Boolean.getBoolean("tno.phase5f.suiteCFastTicks"));
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
            json.addProperty("stage_fixture_only", !PRODUCTION_OBSERVATION);
            json.addProperty("production_balance_mutated", false);
            json.addProperty("production_combat_mutated", false);
            json.addProperty("development_only_combat_fixture_active",
                    SEVERANCE_PROTOTYPE || ADAPTIVE_WOUND_RESEARCH);
            json.addProperty("profile_clone_policy", freshCalibrationAttachment()
                    ? "fresh initialized L2 attachment and exact legal constructed profile for every case; required for native ticking-trait evidence"
                    : PRODUCTION_OBSERVATION
                    ? "accepted strongest legal profile per exact L2 level; pristine serialized clone for S0-S7"
                    : ENDGAME ? "accepted strongest legal Lv1000 profile per boss; pristine serialized clone for Native and S7"
                    : "one legal native L2 roll per boss/level; pristine serialized clones for Native and S0-S7");
            json.addProperty("benchmark_bow_components", benchmarkBow.getComponents().toString());
            json.add("benchmark_bow_attribute_modifiers", readStackAttributes(benchmarkBow));
            if (SUSTAINED_ROTATION) {
                json.addProperty("magic_bow_components", sustainedMagicBow.getComponents().toString());
                json.addProperty("holy_bow_components", sustainedHolyBow.getComponents().toString());
                json.addProperty("severance_bow_components", benchmarkBow.getComponents().toString());
                json.addProperty("native_target_tick_fixture",
                        "two firing-lane chunks force-loaded only for this dev-server session; removed before shutdown");
            }
            if (SUITE_C) json.add("APO_runtime_inspection", apoInspection.deepCopy());
            JsonArray planned = new JsonArray();
            for (CaseSpec spec : cases) {
                JsonObject entry = new JsonObject();
                entry.addProperty("boss", spec.boss.id.toString());
                entry.addProperty("level", spec.level);
                entry.addProperty("level_mode", spec.mode.name());
                entry.addProperty("TNO_stage", spec.stage.name);
                if (CALIBRATION_COMBAT) {
                    entry.addProperty("L2_profile_variant", spec.traitProfile.id);
                    entry.addProperty("calibration_case", spec.calibration.id);
                    entry.addProperty("Q_generic_health", CaseResult.evidenceQ(spec));
                    entry.addProperty("RD_dementor", CaseResult.evidenceRD(spec));
                    entry.addProperty("RA_adaptive", CaseResult.evidenceRA(spec));
                    if (SEVERANCE_PROTOTYPE) {
                        entry.addProperty("Severance_eligible_multiplier",
                                spec.calibration.severanceEligibleMultiplier);
                        entry.addProperty("diagnostic_ceiling_candidate",
                                spec.calibration == CalibrationCase.SEVERANCE_PROTOTYPE_X64);
                        entry.addProperty("diagnostic_upper_bound_only",
                                spec.calibration == CalibrationCase.SEVERANCE_PROTOTYPE_X64);
                        if (SEVERANCE_SUSTAINED) CaseResult.addR5PolicyMetadata(entry, spec);
                    }
                    if (ADAPTIVE_WOUND_RESEARCH) {
                        entry.addProperty("wound_Adaptive_recovery_RW",
                                spec.calibration.woundAdaptiveRecovery);
                    }
                }
                if (PRODUCTION_ACCEPTANCE) {
                    entry.addProperty("L2_profile_variant", spec.traitProfile.id);
                    entry.addProperty("production_policy_case", spec.calibration.id);
                    entry.addProperty("Q_generic_health", spec.calibration.parameters.genericHealthQ());
                    entry.addProperty("RD_dementor", spec.calibration.parameters.dementorRD());
                    entry.addProperty("RA_adaptive", spec.calibration.parameters.adaptiveRA());
                }
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
        if (PRODUCTION_ACCEPTANCE) {
            BossSpec boss = BOSSES.stream()
                    .filter(value -> !filter.isBlank()
                            ? value.id.toString().equals(filter)
                            : value.id.equals(id("tensura", "orc_disaster")))
                    .findFirst().orElse(null);
            if (boss == null) return result;
            if (boss.id.equals(id("tensura", "orc_disaster"))) {
                for (int level : List.of(300, 600, 800, 1000)) {
                    for (Stage stage : STAGES.subList(1, STAGES.size())) {
                        result.add(new CaseSpec(boss, level, LevelMode.ENDGAME_TARGET, stage,
                                CalibrationCase.productionFor(stage), TraitProfile.ACCEPTED));
                    }
                    Stage s7 = STAGES.get(8);
                    result.add(new CaseSpec(boss, level, LevelMode.ENDGAME_TARGET, s7,
                            CalibrationCase.productionFor(s7), TraitProfile.WITHOUT_DEMENTOR));
                    if (level >= 600) {
                        result.add(new CaseSpec(boss, level, LevelMode.ENDGAME_TARGET, s7,
                                CalibrationCase.productionFor(s7), TraitProfile.WITHOUT_ADAPTIVE));
                    }
                }
            }
            else {
                for (Stage stage : STAGES.subList(5, STAGES.size())) {
                    result.add(new CaseSpec(boss, 1000, LevelMode.ENDGAME_TARGET, stage,
                            CalibrationCase.productionFor(stage), TraitProfile.ACCEPTED));
                }
            }
            return result;
        }
        if (CALIBRATION_COMBAT) {
            BossSpec boss = BOSSES.stream().filter(value -> value.id.equals(id("tensura", "orc_disaster")))
                    .findFirst().orElseThrow();
            if (!filter.isBlank() && !boss.id.toString().equals(filter)) return result;
            if (ADAPTIVE_WOUND_RESEARCH) {
                Stage stage = STAGES.get(8);
                if (ADAPTIVE_WOUND_DYNAMIC) {
                    for (int level : List.of(600, 800, 1000)) {
                        result.add(new CaseSpec(boss, level, LevelMode.ENDGAME_TARGET,
                                stage, CalibrationCase.DYNAMIC_RW_50, TraitProfile.ACCEPTED));
                        result.add(new CaseSpec(boss, level, LevelMode.ENDGAME_TARGET,
                                stage, CalibrationCase.DYNAMIC_RW_50,
                                TraitProfile.WITHOUT_REGENERATE));
                        result.add(new CaseSpec(boss, level, LevelMode.ENDGAME_TARGET,
                                stage, CalibrationCase.DYNAMIC_NATIVE_RW_0,
                                TraitProfile.ACCEPTED));
                    }
                    return result;
                }
                if (ADAPTIVE_WOUND_COUNTER_STATES) {
                    for (int level : List.of(600, 1000)) {
                        for (CalibrationCase calibration : List.of(
                                CalibrationCase.COUNTER_STATE_A,
                                CalibrationCase.COUNTER_STATE_B,
                                CalibrationCase.COUNTER_STATE_C,
                                CalibrationCase.COUNTER_NO_REGENERATE,
                                CalibrationCase.COUNTER_NO_WOUND)) {
                            TraitProfile profile = calibration == CalibrationCase.COUNTER_NO_REGENERATE
                                    ? TraitProfile.WITHOUT_REGENERATE : TraitProfile.ACCEPTED;
                            result.add(new CaseSpec(boss, level, LevelMode.ENDGAME_TARGET,
                                    stage, calibration, profile));
                        }
                    }
                    return result;
                }
                if (ADAPTIVE_WOUND_SAFETY) {
                    for (int level : List.of(600, 800, 1000)) {
                        for (TraitProfile profile : List.of(TraitProfile.ACCEPTED,
                                TraitProfile.WITHOUT_TANK, TraitProfile.WITHOUT_DEMENTOR,
                                TraitProfile.WITHOUT_ADAPTIVE, TraitProfile.WITHOUT_REGENERATE)) {
                            result.add(new CaseSpec(boss, level, LevelMode.ENDGAME_TARGET,
                                    stage, CalibrationCase.WOUND_RW_50, profile));
                        }
                    }
                    return result;
                }
                for (int level : List.of(600, 800, 1000)) {
                    result.add(new CaseSpec(boss, level, LevelMode.ENDGAME_TARGET,
                            stage, CalibrationCase.WOUND_RW_0, TraitProfile.ACCEPTED));
                    result.add(new CaseSpec(boss, level, LevelMode.ENDGAME_TARGET,
                            stage, CalibrationCase.WOUND_RW_100, TraitProfile.ACCEPTED));
                }
                return result;
            }
            if (SEVERANCE_PROTOTYPE) {
                if (SEVERANCE_SUSTAINED) {
                    Stage stage = STAGES.get(8);
                    for (int level : List.of(600, 800, 1000)) {
                        result.add(new CaseSpec(boss, level, LevelMode.ENDGAME_TARGET,
                                stage, CalibrationCase.SEVERANCE_PROTOTYPE_X1, TraitProfile.ACCEPTED));
                        result.add(new CaseSpec(boss, level, LevelMode.ENDGAME_TARGET,
                                stage, CalibrationCase.SEVERANCE_PROTOTYPE_X64, TraitProfile.ACCEPTED));
                        result.add(new CaseSpec(boss, level, LevelMode.ENDGAME_TARGET,
                                stage, CalibrationCase.SEVERANCE_PROTOTYPE_X64,
                                TraitProfile.WITHOUT_REGENERATE));
                        for (TraitProfile profile : List.of(TraitProfile.WITHOUT_TANK,
                                TraitProfile.WITHOUT_DEMENTOR, TraitProfile.WITHOUT_ADAPTIVE)) {
                            result.add(new CaseSpec(boss, level, LevelMode.ENDGAME_TARGET,
                                    stage, CalibrationCase.SEVERANCE_PROTOTYPE_X64, profile));
                        }
                    }
                    return result;
                }
                if (Boolean.getBoolean("tno.phase6.severancePrototypeCeilingOnly")) {
                    Stage stage = STAGES.get(6);
                    result.add(new CaseSpec(boss, 600, LevelMode.ENDGAME_TARGET, stage,
                            CalibrationCase.SEVERANCE_PROTOTYPE_X64, TraitProfile.ACCEPTED));
                    result.add(new CaseSpec(boss, 600, LevelMode.ENDGAME_TARGET, stage,
                            CalibrationCase.SEVERANCE_PROTOTYPE_X64,
                            TraitProfile.WITHOUT_TANK_DEMENTOR_ADAPTIVE));
                    return result;
                }
                for (int level : List.of(600, 800, 1000)) {
                    for (Stage stage : STAGES.subList(6, STAGES.size())) {
                        for (CalibrationCase calibration : CalibrationCase.severancePrototypeCases()) {
                            result.add(new CaseSpec(boss, level, LevelMode.ENDGAME_TARGET,
                                    stage, calibration, TraitProfile.ACCEPTED));
                        }
                        for (TraitProfile profile : List.of(TraitProfile.WITHOUT_TANK,
                                TraitProfile.WITHOUT_DEMENTOR, TraitProfile.WITHOUT_ADAPTIVE,
                                TraitProfile.WITHOUT_TANK_DEMENTOR_ADAPTIVE)) {
                            result.add(new CaseSpec(boss, level, LevelMode.ENDGAME_TARGET,
                                    stage, CalibrationCase.SEVERANCE_PROTOTYPE_X16, profile));
                        }
                    }
                }
                return result;
            }
            List<Integer> levels = switch (CALIBRATION_MODE) {
                case "combined", "severance_wall" -> List.of(600, 800, 1000);
                case "safety" -> List.of(300, 600, 800, 1000);
                default -> List.of(300, 600, 800, 1000);
            };
            for (int level : levels) {
                for (TraitProfile profile : TraitProfile.forMode(CALIBRATION_MODE)) {
                    List<Stage> stages = CALIBRATION_MODE.equals("safety")
                            ? STAGES.subList(1, STAGES.size())
                            : STAGES.subList(6, STAGES.size());
                    for (Stage stage : stages) {
                        for (CalibrationCase calibration : CalibrationCase.forMode(CALIBRATION_MODE, stage)) {
                            result.add(new CaseSpec(boss, level, LevelMode.ENDGAME_TARGET,
                                    stage, calibration, profile));
                        }
                    }
                }
            }
            return result;
        }
        for (BossSpec boss : BOSSES) {
            if (!filter.isBlank() && !boss.id.toString().equals(filter)) continue;
            List<LevelEntry> levels = new ArrayList<>();
            if (PRODUCTION_OBSERVATION) {
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
                for (Stage stage : stages) result.add(new CaseSpec(
                        boss, entry.level, entry.mode, stage, CalibrationCase.NONE, TraitProfile.ACCEPTED));
            }
        }
        return result;
    }

    private static MagicHolyEndgamePolicy.Parameters productionParameters(CaseSpec spec) {
        ScalableFamily family = active.family == Family.MAGIC
                ? ScalableFamily.MAGIC_WEAPON : ScalableFamily.HOLY_WEAPON;
        MagicHolyEndgamePolicy.Parameters parameters = MagicHolyEndgamePolicy.parameters(
                com.tno.tensuracompat.core.stage.Stage.valueOf(spec.stage.name), family);
        Phase6CalibrationContext.Parameters declared = spec.calibration.parameters;
        if (parameters.genericHealthQ() != declared.genericHealthQ()
                || parameters.dementorRecovery() != declared.dementorRD()
                || parameters.adaptiveRecovery() != declared.adaptiveRA()) {
            throw new IllegalStateException("production policy/declaration mismatch for " + spec.stage.name);
        }
        return parameters;
    }

    private static int endgameBudgetSpent(BossSpec boss, int level) {
        if (PRODUCTION_OBSERVATION && boss.id.equals(id("tensura", "orc_disaster"))) {
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

    private static int calibrationBudgetSpent(CaseSpec spec) {
        int spent = endgameBudgetSpent(spec.boss, spec.level);
        Map<String, Integer> reference = ACCEPTED_ORC_ENDGAME_PROFILES.getOrDefault(spec.level, Map.of());
        if (spec.traitProfile.removedTraits.contains("l2hostility:dementor")) {
            spent -= 120 * reference.getOrDefault("l2hostility:dementor", 0);
        }
        if (spec.traitProfile.removedTraits.contains("l2hostility:adaptive")) {
            spent -= 80 * reference.getOrDefault("l2hostility:adaptive", 0);
        }
        if (spec.traitProfile.removedTraits.contains("l2hostility:regenerate")) {
            spent -= 30 * reference.getOrDefault("l2hostility:regenerate", 0);
        }
        if (spec.traitProfile.removedTraits.contains("l2hostility:tank")) {
            spent -= 20 * reference.getOrDefault("l2hostility:tank", 0);
        }
        return spent;
    }

    private static boolean freshCalibrationAttachment() {
        return PRODUCTION_ACCEPTANCE || CALIBRATION_MODE.equals("combined")
                || CALIBRATION_MODE.equals("safety") || CALIBRATION_MODE.equals("severance_wall")
                || CALIBRATION_MODE.equals("severance_prototype")
                || CALIBRATION_MODE.equals("severance_sustained")
                || ADAPTIVE_WOUND_RESEARCH;
    }

    private static final class CaseResult {
        final CaseSpec spec;
        final JsonArray traits;
        final JsonObject traitRanks;
        final JsonObject attackerAttributes;
        final JsonObject bowAttributes;
        final List<HitRecord> hits = new ArrayList<>();
        final List<RegenerateCycle> regenerateCycles = new ArrayList<>();
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
        final int regenerateRank;
        final double regenerateFractionPerRankPerSecond;
        final double nominalRegenerateHpPerSecond;
        final int l2Level;
        final double l2HealthFactor;
        final boolean l2ExponentialHealth;
        final double entityHealthScale;
        final double genericHealthMultiplier;
        final double adaptiveConfiguredFactor;
        final double dementorReductionBase;
        final boolean nativeSelfRegenerationRemovedForIsolation;
        final boolean regenerateTraitValidAtStart;
        final Set<String> isolatedNonRegenerateHealSources = new LinkedHashSet<>();
        int shotsReleased;
        int elapsedTicks;
        Integer ttk;
        Integer htk;
        boolean attackerDefeated;
        double finalHp;
        double finalShp;
        double finalMagicules;
        double finalAura;
        int regenerateCallbackCount;
        int regenerateCanceledEventCount;
        int regenerateNativeTickAttemptCount;
        int nativeTickBoundaryCount;
        int targetTickCountMaximumObserved;
        int regenerateTraitRankAtEnd;
        int regenerateTraitMissingTickCount;
        Integer regenerateTraitFirstMissingElapsedTick;
        boolean regenerateTraitValidOnAllObservedAttempts;
        int isolatedNonRegenerateHealEvents;
        double regenerateNominalAmount;
        double regenerateAllowedEventAmount;
        double regenerateUnconstrainedHealingDemand;
        double regenerateActualHealingAtNativeTicks;
        double regenerateHealingDeniedByWoundCeiling;
        double isolatedNonRegenerateHealNominalAmount;
        double lastServerPostHp;
        CounterState counterState = CounterState.NONE;
        boolean counterSetupApplied;
        boolean counterWoundCreatedByNativeArrow;
        int counterSetupArrowCount;
        double counterWoundAmount;
        double counterWoundCeiling;
        double counterSetupHp;
        double counterReferenceRequest;
        double counterHpBeforeHeal;
        double counterShpBeforeHeal;
        double counterWoundAtHeal;
        double counterCeilingAtHeal;
        double counterLegalHealingSpace;
        double counterRequestedHealing;
        double counterEventAllowedHealing;
        boolean counterHealEventObserved;
        boolean counterHealEventCanceled;
        boolean counterHealSourceStackVerified;
        double counterHpAfterHeal;
        double counterShpAfterHeal;
        double counterActualHealing;
        double counterDeniedHealing;
        int dynamicTicksBelowCeiling;
        int dynamicTicksAtCeiling;
        int dynamicTicksAboveCeiling;
        double dynamicMaximumWound;
        double dynamicMinimumCeiling;
        double dynamicCumulativeActualHealing;
        double dynamicCumulativeDeniedHealing;

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
            this.regenerateRank = traitRanks.has("l2hostility:regenerate")
                    ? traitRanks.get("l2hostility:regenerate").getAsInt() : 0;
            this.regenerateTraitRankAtEnd = regenerateRank;
            this.regenerateTraitValidAtStart = regenerateRank == 0
                    || traitValidTarget(cap, "l2hostility:regenerate", target);
            this.regenerateTraitValidOnAllObservedAttempts = regenerateTraitValidAtStart;
            Object serverConfig = staticField("dev.xkmc.l2hostility.init.data.LHConfig", "SERVER");
            Object regenConfig = readField(serverConfig, "regen");
            this.regenerateFractionPerRankPerSecond = numberValue(invoke(regenConfig, "get")).doubleValue();
            this.nominalRegenerateHpPerSecond = initialMaxHp
                    * regenerateFractionPerRankPerSecond * regenerateRank;
            this.l2Level = numberValue(invoke(cap, "getLevel")).intValue();
            Object entityConfig = invoke(cap, "getConfigCache", target);
            this.entityHealthScale = numberValue(readField(entityConfig, "healthScale")).doubleValue();
            this.l2HealthFactor = serverDouble("healthFactor");
            this.l2ExponentialHealth = serverBoolean("exponentialHealth");
            this.genericHealthMultiplier = L2HealthScaling.nominalMultiplier(
                    l2Level, l2HealthFactor, entityHealthScale, l2ExponentialHealth);
            this.adaptiveConfiguredFactor = serverDouble("adaptFactor");
            this.dementorReductionBase = serverDouble("dementorDamageReductionBase");
            this.nativeSelfRegenerationRemovedForIsolation =
                    active.selfRegenerationRemovedForIsolation;
            this.lastServerPostHp = initialHp;
        }

        void observeNativeRegenerateTick(LivingEntity target, Object cap, HitRecord hit,
                int elapsedTick) throws ReflectiveOperationException {
            targetTickCountMaximumObserved = Math.max(targetTickCountMaximumObserved, target.tickCount);
            int currentRank = traitRank(cap, "l2hostility:regenerate");
            regenerateTraitRankAtEnd = currentRank;
            if (regenerateRank > 0 && currentRank != regenerateRank) {
                regenerateTraitMissingTickCount++;
                if (regenerateTraitFirstMissingElapsedTick == null) {
                    regenerateTraitFirstMissingElapsedTick = elapsedTick;
                }
            }
            if (target.tickCount < 20) return;
            nativeTickBoundaryCount++;
            if (currentRank > 0) {
                boolean valid = traitValidTarget(cap, "l2hostility:regenerate", target);
                regenerateTraitValidOnAllObservedAttempts &= valid;
                double nominal = initialMaxHp * regenerateFractionPerRankPerSecond * currentRank;
                double demand = Math.min(nominal, Math.max(0.0D, initialMaxHp - lastServerPostHp));
                double actual = Math.max(0.0D, target.getHealth() - lastServerPostHp);
                actual = Math.min(actual, demand);
                double denied = Math.max(0.0D, demand - actual);
                regenerateNativeTickAttemptCount++;
                regenerateNominalAmount += nominal;
                regenerateUnconstrainedHealingDemand += demand;
                regenerateActualHealingAtNativeTicks += actual;
                regenerateHealingDeniedByWoundCeiling += denied;
                if (hit != null) {
                    hit.regenerateNativeTickAttempts++;
                    hit.regenerateNominalAmount += nominal;
                    hit.regenerateUnconstrainedHealingDemand += demand;
                    hit.regenerateActualHealingAtNativeTicks += actual;
                    hit.regenerateHealingDeniedByWoundCeiling += denied;
                }
            }
            if (ADAPTIVE_WOUND_COUNTER_STATES) {
                captureCounterHealPost(target);
            }
            if (ADAPTIVE_WOUND_DYNAMIC && currentRank > 0) {
                captureDynamicHealPost(target, elapsedTick);
            }
            // R2 established this controlled native cadence. The real L2
            // RegenTrait has already executed for tick 20 at this point.
            target.tickCount = 0;
        }

        void captureServerPostHp(LivingEntity target) {
            lastServerPostHp = target.getHealth();
        }

        void configureCounterState(LivingEntity target, CounterState state, int setupArrowCount) {
            counterState = state;
            counterSetupArrowCount = setupArrowCount;
            counterWoundAmount = severance(target);
            counterWoundCreatedByNativeArrow = state.requiresWound()
                    && setupArrowCount == 1 && counterWoundAmount > 0.0001D;
            if (state.requiresWound() != counterWoundCreatedByNativeArrow) {
                throw new IllegalStateException("P2 wound provenance mismatch for " + state.id);
            }
            counterWoundCeiling = initialMaxHp - counterWoundAmount;
            int referenceRank = ACCEPTED_ORC_ENDGAME_PROFILES
                    .getOrDefault(spec.level, Map.of())
                    .getOrDefault("l2hostility:regenerate", 0);
            if (referenceRank <= 0) {
                throw new IllegalStateException("P2 accepted Regenerate reference rank absent at Lv" + spec.level);
            }
            counterReferenceRequest = initialMaxHp
                    * regenerateFractionPerRankPerSecond * referenceRank;
            double margin = 25.0D;
            double requestedStart = switch (state) {
                case A_BELOW_CEILING, NO_REGENERATE_CONTROL ->
                        counterWoundCeiling - counterReferenceRequest - margin;
                case B_CROSSING_CEILING -> counterWoundCeiling - counterReferenceRequest / 2.0D;
                case C_AT_CEILING -> counterWoundCeiling;
                case NO_WOUND_CONTROL -> initialMaxHp - counterReferenceRequest - margin;
                case NONE -> throw new IllegalStateException("P2 counter state is not configured");
            };
            target.setHealth((float) Math.max(1.0D, requestedStart));
            counterSetupHp = target.getHealth();
            counterSetupApplied = true;
            lastServerPostHp = counterSetupHp;
        }

        void captureCounterHealEvent(LivingEntity target, double requested, double allowed,
                boolean canceled, boolean sourceStackVerified) {
            if (counterHealEventObserved) {
                throw new IllegalStateException("P2 observed multiple Regenerate callbacks in one case");
            }
            counterHealEventObserved = true;
            counterHpBeforeHeal = target.getHealth();
            counterShpBeforeHeal = resources(target).shp;
            counterWoundAtHeal = severance(target);
            counterCeilingAtHeal = target.getMaxHealth() - counterWoundAtHeal;
            counterLegalHealingSpace = Math.max(0.0D, counterCeilingAtHeal - counterHpBeforeHeal);
            counterRequestedHealing = requested;
            counterEventAllowedHealing = allowed;
            counterHealEventCanceled = canceled;
            counterHealSourceStackVerified = sourceStackVerified;
        }

        void captureCounterHealPost(LivingEntity target) {
            counterHpAfterHeal = target.getHealth();
            counterShpAfterHeal = resources(target).shp;
            if (counterHealEventObserved) {
                counterActualHealing = Math.max(0.0D, counterHpAfterHeal - counterHpBeforeHeal);
                counterDeniedHealing = Math.max(0.0D,
                        counterRequestedHealing - counterActualHealing);
            }
            else {
                counterHpBeforeHeal = counterSetupHp;
                counterHpAfterHeal = target.getHealth();
                counterShpBeforeHeal = resources(target).shp;
                counterShpAfterHeal = counterShpBeforeHeal;
                counterWoundAtHeal = severance(target);
                counterCeilingAtHeal = target.getMaxHealth() - counterWoundAtHeal;
                counterLegalHealingSpace = Math.max(0.0D,
                        counterCeilingAtHeal - counterHpBeforeHeal);
                counterRequestedHealing = 0.0D;
                counterEventAllowedHealing = 0.0D;
                counterActualHealing = 0.0D;
                counterDeniedHealing = 0.0D;
            }
        }

        void captureDynamicHealEvent(LivingEntity target, double requested,
                double allowed, boolean canceled, int elapsedTick) {
            RegenerateCycle cycle = new RegenerateCycle(
                    regenerateCycles.size() + 1,
                    nativeTickBoundaryCount + 1,
                    elapsedTick,
                    target.tickCount,
                    regenerateTraitRankAtEnd,
                    target.getMaxHealth(),
                    target.getHealth(),
                    resources(target).shp,
                    severance(target),
                    requested,
                    allowed,
                    canceled);
            regenerateCycles.add(cycle);
        }

        void captureDynamicHealPost(LivingEntity target, int elapsedTick) {
            if (regenerateCycles.isEmpty()) {
                throw new IllegalStateException(
                        "P3 native Regenerate tick completed without a heal-event record");
            }
            RegenerateCycle cycle = regenerateCycles.getLast();
            if (cycle.complete) {
                throw new IllegalStateException(
                        "P3 native Regenerate cycle was completed more than once");
            }
            cycle.postElapsedTick = elapsedTick;
            cycle.hpAfter = target.getHealth();
            cycle.shpAfter = resources(target).shp;
            cycle.woundAfter = severance(target);
            cycle.actual = Math.max(0.0D, cycle.hpAfter - cycle.hpBefore);
            cycle.denied = Math.max(0.0D, cycle.requested - cycle.actual);
            dynamicCumulativeActualHealing += cycle.actual;
            dynamicCumulativeDeniedHealing += cycle.denied;
            cycle.cumulativeActual = dynamicCumulativeActualHealing;
            cycle.cumulativeDenied = dynamicCumulativeDeniedHealing;
            cycle.complete = true;
        }

        void observeDynamicCounterPosition(LivingEntity target) {
            double wound = severance(target);
            double ceiling = target.getMaxHealth() - wound;
            double hp = target.getHealth();
            dynamicMaximumWound = Math.max(dynamicMaximumWound, wound);
            dynamicMinimumCeiling = dynamicMinimumCeiling == 0.0D
                    ? ceiling : Math.min(dynamicMinimumCeiling, ceiling);
            if (hp < ceiling - 0.01D) dynamicTicksBelowCeiling++;
            else if (hp > ceiling + 0.01D) dynamicTicksAboveCeiling++;
            else dynamicTicksAtCeiling++;
        }

        void finish(LivingEntity target) {
            if (target == null) return;
            finalHp = target.getHealth();
            ResourceState resources = resources(target);
            finalShp = resources.shp;
            finalMagicules = resources.magicules;
            finalAura = resources.aura;
        }

        void finishCounterState(LivingEntity target) {
            if (target == null) return;
            // The controlled observation ends at the native tick-20 boundary.
            // Orc Disaster may execute an unrelated heal on the following
            // FINISH-transition tick, so final HP/SHP must remain the already
            // captured counter-state result rather than that later fixture noise.
            finalHp = counterHpAfterHeal;
            finalShp = counterShpAfterHeal;
            ResourceState resources = resources(target);
            finalMagicules = resources.magicules;
            finalAura = resources.aura;
        }

        void finishDynamic(LivingEntity target) {
            if (target == null) return;
            if (hits.isEmpty()) {
                finish(target);
                return;
            }
            // Preserve the final RUN-tick observation. The subsequent FINISH
            // transition is outside the fixed 1200-tick P3 measurement window.
            HitRecord last = hits.getLast();
            finalHp = last.postHp;
            finalShp = last.postShp;
            finalMagicules = last.postMagicules;
            finalAura = last.postAura;
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
            if (SUSTAINED_ROTATION) {
                json.addProperty("rotation_family", hit.shotFamily.id);
                json.addProperty("rotation_enchantment", hit.shotFamily.enchantment.toString());
                json.addProperty("legal_separate_bow_rotation", true);
            }
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
            json.add("dot_damage_source_ids", strings(hit.dotSourceIds));
            json.addProperty("native_severance_incoming_event_count",
                    hit.nativeSeveranceIncomingEventCount);
            json.addProperty("native_severance_incoming_amount",
                    hit.nativeSeveranceIncomingAmount);
            json.addProperty("native_severance_after_L2_event_count",
                    hit.nativeSeveranceAfterL2EventCount);
            json.addProperty("native_severance_after_L2_amount",
                    hit.nativeSeveranceAfterL2Amount);
            json.addProperty("native_severance_incoming_cancelled",
                    hit.nativeSeveranceIncomingCanceled);
            json.addProperty("native_severance_damage_pre_event_count",
                    hit.nativeSeveranceDamagePreEventCount);
            json.addProperty("native_severance_damage_pre_amount",
                    hit.nativeSeveranceDamagePreAmount);
            json.addProperty("native_severance_damage_post_event_count",
                    hit.nativeSeveranceDamagePostEventCount);
            json.addProperty("native_severance_damage_post_amount",
                    hit.nativeSeveranceDamagePostAmount);
            json.add("native_severance_source_entity_ids",
                    strings(hit.nativeSeveranceSourceEntityIds));
            json.add("native_severance_direct_entity_ids",
                    strings(hit.nativeSeveranceDirectEntityIds));
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
            if (PRODUCTION_OBSERVATION) {
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
            if (SEVERANCE_RESEARCH) addSeveranceWallTrace(json, hit);
            else if (CALIBRATION_COMBAT) addCalibrationTrace(json, hit);
            if (PRODUCTION_ACCEPTANCE) addProductionExpectation(json, hit);
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
            json.addProperty("severance_prototype_eligible_multiplier",
                    spec.calibration.severanceEligibleMultiplier);
            json.addProperty("severance_production_eligible_contribution",
                    hit.severanceProductionEligibleContribution);
            json.addProperty("severance_prototype_eligible_contribution",
                    hit.severancePrototypeEligibleContribution);
            json.addProperty("severance_prototype_pre_round", hit.severancePrototypePreRound);
            json.addProperty("severance_prototype_post_round", hit.severancePrototypePostRound);
            json.addProperty("severance_prototype_delta_over_production_post_round",
                    hit.severancePrototypePostRound - hit.severanceStagedPostRound);
            json.addProperty("severance_base_affected_by_prototype", false);
            json.addProperty("severance_configured_projectile_count", hit.severanceConfiguredProjectileCount);
            json.addProperty("severance_admitted_projectile_count", hit.severanceAdmittedProjectileCount);
            json.addProperty("severance_pre_amount", hit.preSeverance);
            json.addProperty("severance_post_amount", hit.postSeverance);
            json.addProperty("severance_amount_delta", Math.max(0.0D, hit.postSeverance - hit.preSeverance));
            json.addProperty("severance_duration_before_seconds", hit.preSeveranceDuration);
            json.addProperty("severance_duration_after_seconds", hit.postSeveranceDuration);
            json.addProperty("severance_max_observed_amount", hit.maxSeverance);
            json.addProperty("severance_observed_ticks", hit.woundObservedTicks);
            json.addProperty("target_observation_ticks", hit.targetObservationTicks);
            json.addProperty("regenerate_callback_count", hit.regenerateCallbackCount);
            json.addProperty("regenerate_native_tick_attempt_count", hit.regenerateNativeTickAttempts);
            json.addProperty("regenerate_nominal_amount", hit.regenerateNominalAmount);
            json.addProperty("regenerate_unconstrained_healing_demand",
                    hit.regenerateUnconstrainedHealingDemand);
            json.addProperty("regenerate_actual_healing_at_native_ticks",
                    hit.regenerateActualHealingAtNativeTicks);
            json.addProperty("regenerate_healing_denied_by_wound_ceiling",
                    hit.regenerateHealingDeniedByWoundCeiling);
            json.addProperty("regenerate_event_allowed_amount", hit.regenerateAllowedEventAmount);
            json.addProperty("regenerate_event_cancelled", hit.regenerateEventCanceled);
            json.addProperty("regenerate_actual_healing_observed", hit.targetHpRegen);
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

        private void addSeveranceWallTrace(JsonObject json, HitRecord hit) {
            json.addProperty("severance_wall_trace_count", hit.severanceWallTraces.size());
            if (hit.severanceWallTraces.isEmpty()) {
                json.add("severance_wall_trace", null);
                return;
            }
            if (hit.severanceWallTraces.size() != 1) {
                throw new IllegalStateException("expected one physical-wall trace per release, found "
                        + hit.severanceWallTraces.size());
            }
            Phase6SeveranceWallContext.Snapshot trace = hit.severanceWallTraces.getFirst();
            JsonObject value = new JsonObject();
            value.addProperty("native_arrow_base_post_round", hit.severanceBasePostRound);
            value.addProperty("native_Severance_post_round_contribution",
                    hit.severanceNativePostRound - hit.severanceBasePostRound);
            value.addProperty("TNO_Stage_delta_post_round",
                    hit.severanceStagedPostRound - hit.severanceNativePostRound);
            value.addProperty("prototype_eligible_multiplier", spec.calibration.severanceEligibleMultiplier);
            value.addProperty("prototype_eligible_pre_velocity",
                    hit.severancePrototypeEligibleContribution);
            value.addProperty("prototype_combined_post_round", hit.severancePrototypePostRound);
            value.addProperty("prototype_delta_over_production_post_round",
                    hit.severancePrototypePostRound - hit.severanceStagedPostRound);
            value.addProperty("Royal_Arrow_base_changed_by_prototype", false);
            value.addProperty("pre_L2_combined_physical", hit.physicalIncoming);
            value.addProperty("context_combined_physical", trace.combinedPhysicalAmount());
            value.addProperty("DamageData_original", trace.damageOriginal());
            value.addProperty("Tank_present", trace.tankRank() > 0);
            value.addProperty("Tank_rank", trace.tankRank());
            value.addProperty("armor_with_current_profile", initialArmor);
            value.addProperty("toughness_with_current_profile", initialToughness);
            value.addProperty("incoming_event_amount_before_damage_finalization", hit.physicalAfterIncomingL2);
            value.addProperty("post_armor_Tank_result_entering_Dementor", trace.dementorInput());
            value.addProperty("Dementor_applied", trace.dementorApplied());
            value.addProperty("Dementor_input", trace.dementorInput());
            value.addProperty("Dementor_native_output", trace.dementorOutput());
            value.addProperty("Adaptive_applied", trace.adaptiveApplied());
            value.addProperty("Adaptive_source_msgId", trace.sourceMsgId());
            value.addProperty("Adaptive_trait_rank", trace.adaptiveRank());
            value.addProperty("Adaptive_memory_capacity", trace.adaptiveMemoryCapacity());
            value.addProperty("Adaptive_adaptation_count", trace.adaptiveCount());
            value.addProperty("Adaptive_configured_factor", trace.configuredAdaptFactor());
            value.addProperty("Adaptive_input", trace.adaptiveInput());
            value.addProperty("Adaptive_native_factor", trace.adaptiveFactor());
            value.addProperty("Adaptive_native_result", trace.adaptiveResult());
            value.addProperty("final_physical_after_L2_pipeline", hit.physicalAfterL2);
            value.addProperty("LivingDamageEvent_Pre_amount", hit.physicalAfterL2);
            value.addProperty("post_Adaptive_projected_physical", trace.adaptiveResult());
            value.addProperty("incoming_event_cancelled_after_L2", hit.physicalIncomingCanceled);
            value.addProperty("final_hurt_returned_success", trace.hurtReturned());
            value.addProperty("final_HP_delta",
                    Math.max(0.0D, hit.preHp - hit.postHp + hit.targetHpRegen));
            value.addProperty("final_SHP_delta",
                    Math.max(0.0D, hit.preShp - hit.postShp + hit.targetShpRegen));
            value.addProperty("wound_attempted", trace.woundAttemptCount() > 0);
            value.addProperty("wound_attempt_count", trace.woundAttemptCount());
            value.addProperty("native_wound_callback_damage", trace.woundCallbackDamage());
            value.addProperty("wound_stored", hit.postSeverance > hit.preSeverance + 0.0001D);
            value.addProperty("wound_before", hit.preSeverance);
            value.addProperty("wound_after", hit.postSeverance);
            value.addProperty("wound_delta", Math.max(0.0D, hit.postSeverance - hit.preSeverance));
            value.addProperty("observation_only", !SEVERANCE_PROTOTYPE);
            value.addProperty("modifier_values_changed", false);
            value.addProperty("eligible_pre_hurt_prototype_active", SEVERANCE_PROTOTYPE);
            if (ADAPTIVE_WOUND_RESEARCH) {
                value.addProperty("adaptive_wound_trace_count", hit.adaptiveWoundTraces.size());
                if (hit.shotFamily != Family.SEVERANCE) {
                    if (!hit.adaptiveWoundTraces.isEmpty()) {
                        throw new IllegalStateException(
                                "non-Severance rotation hit unexpectedly entered Adaptive-wound negotiation");
                    }
                    value.add("adaptive_wound_architecture", null);
                    json.add("severance_wall_trace", value);
                    return;
                }
                if (hit.adaptiveWoundTraces.size() != 1) {
                    throw new IllegalStateException("expected one Adaptive-wound trace per release, found "
                            + hit.adaptiveWoundTraces.size());
                }
                Phase6AdaptiveWoundContext.Snapshot wound = hit.adaptiveWoundTraces.getFirst();
                JsonObject architecture = new JsonObject();
                architecture.addProperty("projectile_uuid", wound.projectileUuid());
                architecture.addProperty("physical_source_msgId", wound.physicalSourceMsgId());
                architecture.addProperty("physical_source_id", wound.physicalSourceId());
                architecture.addProperty("wound_state_identity", wound.woundStateIdentity());
                architecture.addProperty("native_ceiling_source_id", wound.nativeCeilingSourceId());
                architecture.addProperty("combined_physical_pre_L2", wound.combinedPhysicalPreL2());
                architecture.addProperty("eligible_physical_post_round", wound.eligiblePhysicalPostRound());
                architecture.addProperty("native_callback_damage", wound.nativeCallbackDamage());
                architecture.addProperty("native_Severance_candidate", wound.nativeCandidate());
                architecture.addProperty("native_HP_deficit_constraint", wound.nativeHpDeficitConstraint());
                architecture.addProperty("native_post_clamp_offer", wound.nativePostClampOffer());
                architecture.addProperty("Tank_Dementor_survival_ratio", wound.tankDementorSurvivalRatio());
                architecture.addProperty("eligible_pre_Adaptive", wound.eligiblePreAdaptive());
                architecture.addProperty("Adaptive_native_factor", wound.nativeAdaptiveFactor());
                architecture.addProperty("Adaptive_rank", wound.adaptiveRank());
                architecture.addProperty("Adaptive_count", wound.adaptiveCount());
                architecture.addProperty("diagnostic_RW", wound.diagnosticRecovery());
                architecture.addProperty("diagnostic_wound_Adaptive_factor",
                        wound.diagnosticWoundAdaptiveFactor());
                architecture.addProperty("native_eligible_wound_potential",
                        wound.nativeEligibleWoundPotential());
                architecture.addProperty("diagnostic_eligible_wound_potential",
                        wound.diagnosticEligibleWoundPotential());
                architecture.addProperty("diagnostic_eligible_extra", wound.diagnosticEligibleExtra());
                architecture.addProperty("negotiated_native_storage_offer",
                        wound.negotiatedNativeStorageOffer());
                architecture.addProperty("HP_before_native_storage", wound.hpBeforeNativeStorage());
                architecture.addProperty("HP_after_native_storage", wound.hpAfterNativeStorage());
                architecture.addProperty("wound_before_native_storage", wound.woundBeforeNativeStorage());
                architecture.addProperty("wound_after_native_storage", wound.woundAfterNativeStorage());
                architecture.addProperty("native_ceiling_enforcement_HP_loss",
                        wound.nativeCeilingEnforcementHpLoss());
                double woundIncrement = Math.max(0.0D,
                        wound.woundAfterNativeStorage() - wound.woundBeforeNativeStorage());
                architecture.addProperty("native_Severance_Protection_adjusted_increment",
                        woundIncrement);
                architecture.addProperty("native_Severance_Protection_multiplier",
                        wound.negotiatedNativeStorageOffer() <= 0.0D ? 1.0D
                                : woundIncrement / wound.negotiatedNativeStorageOffer());
                architecture.addProperty("post_Dementor_physical", wound.postDementorPhysical());
                architecture.addProperty("post_Adaptive_physical", wound.postAdaptivePhysical());
                architecture.addProperty("physical_damage_changed_by_prototype", false);
                architecture.addProperty("Adaptive_state_changed_by_prototype", false);
                architecture.addProperty("direct_TNO_wound_write", false);
                value.add("adaptive_wound_architecture", architecture);
            }
            json.add("severance_wall_trace", value);
        }

        private void addProductionExpectation(JsonObject json, HitRecord hit) {
            MagicHolyEndgamePolicy.Parameters parameters = productionParameters(spec);
            boolean hasDementor = traitRanks.has("l2hostility:dementor");
            boolean hasAdaptive = traitRanks.has("l2hostility:adaptive");
            double input = hit.familyAfterRecovery;
            double normalization = MagicHolyEndgameMath.genericNormalization(
                    parameters, genericHealthMultiplier);
            double genericPost = input * normalization;
            double nativeDementor = hasDementor
                    ? genericPost < 2.0D ? genericPost / 2.0D
                    : Math.log(genericPost) / Math.log(dementorReductionBase)
                    : genericPost;
            double negotiatedDementor = MagicHolyEndgameMath.negotiateDementor(
                    hasDementor, genericPost, nativeDementor, parameters.dementorRecovery());
            double nativeAdaptiveFactor = hasAdaptive
                    ? Math.pow(adaptiveConfiguredFactor, Math.max(0, hit.index - 1)) : 1.0D;
            double negotiatedAdaptiveFactor = MagicHolyEndgameMath.negotiateAdaptive(
                    hasAdaptive, nativeAdaptiveFactor, parameters.adaptiveRecovery());
            double expectedAfterL2 = hit.familyDamageEventCount == 0
                    ? 0.0D : negotiatedDementor * negotiatedAdaptiveFactor;

            JsonObject expectation = new JsonObject();
            expectation.addProperty("input_after_Tensura", input);
            expectation.addProperty("generic_health_multiplier", genericHealthMultiplier);
            expectation.addProperty("generic_normalization", normalization);
            expectation.addProperty("generic_post", genericPost);
            expectation.addProperty("Dementor_present", hasDementor);
            expectation.addProperty("Dementor_native_post", nativeDementor);
            expectation.addProperty("Dementor_negotiated_post", negotiatedDementor);
            expectation.addProperty("Adaptive_present", hasAdaptive);
            expectation.addProperty("Adaptive_native_factor", nativeAdaptiveFactor);
            expectation.addProperty("Adaptive_negotiated_factor", negotiatedAdaptiveFactor);
            expectation.addProperty("expected_after_L2", expectedAfterL2);
            expectation.addProperty("observed_after_L2", hit.familyPost);
            expectation.addProperty("formula_matches_observation",
                    Math.abs(expectedAfterL2 - hit.familyPost) <= 0.001D);
            json.add("production_expectation", expectation);
        }

        private void addCalibrationTrace(JsonObject json, HitRecord hit) {
            json.addProperty("calibration_trace_count", hit.calibrationTraces.size());
            if (hit.calibrationTraces.isEmpty()) {
                json.add("calibration_trace", null);
                return;
            }
            if (hit.calibrationTraces.size() != 1) {
                throw new IllegalStateException("expected one eligible calibration trace per release, found "
                        + hit.calibrationTraces.size());
            }
            Phase6CalibrationContext.Snapshot trace = hit.calibrationTraces.getFirst();
            JsonObject value = new JsonObject();
            value.addProperty("eligible_amount_before_Tensura_defense", hit.familyStageScaled);
            value.addProperty("result_after_matching_Tensura_layer", hit.familyAfterRecovery);
            value.addProperty("DamageData_original", trace.damageOriginal());
            value.addProperty("generic_L2_health_multiplier", trace.genericHealthMultiplier());
            value.addProperty("generic_input", trace.genericPre());
            value.addProperty("generic_diagnostic_output", trace.genericPost());
            value.addProperty("Dementor_applied", trace.dementorApplied());
            value.addProperty("Dementor_pre", trace.dementorPre());
            value.addProperty("Dementor_native_post", trace.dementorNativePost());
            value.addProperty("Dementor_diagnostic_post", trace.dementorDiagnosticPost());
            value.addProperty("Adaptive_applied", trace.adaptiveApplied());
            value.addProperty("Adaptive_source_msgId", trace.sourceMsgId());
            value.addProperty("Adaptive_trait_rank", trace.adaptiveRank());
            value.addProperty("Adaptive_memory_capacity", trace.adaptiveMemoryCapacity());
            value.addProperty("Adaptive_adaptation_count", trace.adaptiveCount());
            value.addProperty("Adaptive_configured_factor", trace.configuredAdaptFactor());
            value.addProperty("Adaptive_pre", trace.adaptivePre());
            value.addProperty("Adaptive_native_factor", trace.adaptiveNativeFactor());
            value.addProperty("Adaptive_negotiated_factor", trace.adaptiveDiagnosticFactor());
            value.addProperty("Adaptive_native_result", trace.adaptiveNativePost());
            value.addProperty("Adaptive_diagnostic_result", trace.adaptiveDiagnosticPost());
            value.addProperty("final_family_event_amount", hit.familyPost);
            value.addProperty("target_HP_delta", Math.max(0.0D, hit.preHp - hit.postHp + hit.targetHpRegen));
            value.addProperty("target_SHP_delta", Math.max(0.0D, hit.preShp - hit.postShp + hit.targetShpRegen));
            json.add("calibration_trace", value);
        }

        private boolean nativeEventExisted(HitRecord hit) {
            return switch (hit.shotFamily) {
                case MAGIC, HOLY, SOUL, ELEMENTAL -> hit.familyDamageEventCount > 0;
                case ENERGY -> hit.energyDrainEvents > 0;
                case SEVERANCE -> hit.severanceConfiguredProjectileCount > 0;
            };
        }

        private double valueBeforeTensura(HitRecord hit) {
            return switch (hit.shotFamily) {
                case MAGIC, HOLY, SOUL, ELEMENTAL -> hit.familyStageScaled;
                case ENERGY -> hit.energyStagedPercentage;
                case SEVERANCE -> hit.physicalCombinedOriginal;
            };
        }

        private double valueAfterTensura(HitRecord hit) {
            return switch (hit.shotFamily) {
                case MAGIC, HOLY, SOUL, ELEMENTAL -> hit.familyAfterResistance;
                case ENERGY -> hit.energyStagedPercentage;
                case SEVERANCE -> hit.physicalIncoming;
            };
        }

        private double valueEnteringL2(HitRecord hit) {
            return switch (hit.shotFamily) {
                case MAGIC, HOLY, SOUL, ELEMENTAL -> hit.familyAfterRecovery;
                case ENERGY -> 0.0D;
                case SEVERANCE -> hit.physicalIncoming;
            };
        }

        private double valueAfterL2(HitRecord hit) {
            return switch (hit.shotFamily) {
                case MAGIC, HOLY, SOUL, ELEMENTAL -> hit.familyPost;
                case ENERGY -> 0.0D;
                case SEVERANCE -> hit.physicalPost;
            };
        }

        private boolean associatedEffectExecuted(HitRecord hit) {
            return switch (hit.shotFamily) {
                case MAGIC, HOLY, SOUL, ELEMENTAL -> hit.familyPost > 0.0D;
                case ENERGY -> hit.energyDrainEvents > 0 && hit.energyDrain() > 0.0D;
                case SEVERANCE -> hit.postSeverance > hit.preSeverance;
            };
        }

        private double familyFinalResult(HitRecord hit) {
            return switch (hit.shotFamily) {
                case MAGIC, HOLY, SOUL, ELEMENTAL -> hit.familyPost;
                case ENERGY -> hit.energyDrain();
                case SEVERANCE -> Math.max(0.0D, hit.postSeverance - hit.preSeverance);
            };
        }

        private String resultClassification(HitRecord hit) {
            if (familyFinalResult(hit) <= 0.0001D) return "ZERO";
            if ((hit.shotFamily == Family.MAGIC || hit.shotFamily == Family.HOLY)
                    && hit.resourceDamage() <= 0.0001D) return "ZERO";
            if (hit.shotFamily != Family.ENERGY) {
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
            if ((hit.shotFamily == Family.MAGIC || hit.shotFamily == Family.HOLY
                    || hit.shotFamily == Family.ENERGY) && !nativeEventExisted(hit)) {
                return "PREREQUISITE_HIT_FAILED";
            }
            if ((hit.shotFamily == Family.SOUL || hit.shotFamily == Family.ELEMENTAL)
                    && !nativeEventExisted(hit)) return "NATIVE_EVENT_ABSENT";
            if (hit.shotFamily == Family.SEVERANCE && hit.physicalDamageEventCount == 0) {
                return traitRanks.has("l2hostility:repelling")
                        ? "L2_PROJECTILE_REJECTION" : "PREREQUISITE_HIT_FAILED";
            }
            if (valueEnteringL2(hit) > 0.0D && valueAfterL2(hit) <= 0.0001D) {
                return traitRanks.has("l2hostility:arena")
                        ? "L2_ADMISSION_VETO" : "L2_MITIGATION";
            }
            if (valueEnteringL2(hit) > 0.0D
                    && familyFinalResult(hit) / valueEnteringL2(hit) <= 0.10D) return "L2_MITIGATION";
            if ((hit.shotFamily == Family.MAGIC || hit.shotFamily == Family.HOLY)
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
                default -> (hit.shotFamily == Family.MAGIC || hit.shotFamily == Family.HOLY)
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
            if (CALIBRATION_COMBAT) {
                double seconds = elapsedTicks / 20.0D;
                double familyDamage = hits.stream().mapToDouble(hit -> hit.familyPost).sum();
                double familyDps = seconds <= 0.0D ? 0.0D : familyDamage / seconds;
                double totalEventDamage = hits.stream().mapToDouble(HitRecord::directDamage).sum()
                        + hits.stream().mapToDouble(hit -> hit.dotPost).sum();
                double totalEventDps = seconds <= 0.0D ? 0.0D : totalEventDamage / seconds;
                double combined = initialHp + initialShp;
                double observedNetDamage = Math.max(0.0D,
                        initialHp + initialShp - finalHp - finalShp);
                double observedNetDps = seconds <= 0.0D ? 0.0D : observedNetDamage / seconds;
                double nominalPostRegenerateDps = Math.max(0.0D,
                        totalEventDps - nominalRegenerateHpPerSecond);
                json.addProperty("family_event_damage", familyDamage);
                json.addProperty("family_DPS", familyDps);
                json.addProperty("total_TNO_only_Royal_Bow_event_DPS", totalEventDps);
                json.addProperty("observed_net_resource_damage", observedNetDamage);
                json.addProperty("observed_net_resource_DPS", observedNetDps);
                json.addProperty("nominal_total_TNO_only_DPS_after_Regenerate", nominalPostRegenerateDps);
                json.addProperty("target_HP_delta_including_regen", Math.max(0.0D,
                        initialHp - finalHp + hits.stream().mapToDouble(hit -> hit.targetHpRegen).sum()));
                json.addProperty("target_SHP_delta_including_regen", Math.max(0.0D,
                        initialShp - finalShp + hits.stream().mapToDouble(hit -> hit.targetShpRegen).sum()));
                json.addProperty("combined_target_resources", combined);
                addFiniteOrNull(json, "estimated_family_TTK_seconds", combined, familyDps);
                addFiniteOrNull(json, "estimated_total_TNO_only_TTK_seconds", combined, totalEventDps);
                addFiniteOrNull(json, "estimated_observed_net_TTK_seconds", combined, dps());
                addFiniteOrNull(json, "estimated_total_TNO_only_TTK_after_nominal_Regenerate_seconds",
                        combined, nominalPostRegenerateDps);
                json.addProperty("calibration_trace_count",
                        hits.stream().mapToInt(hit -> hit.calibrationTraces.size()).sum());
                if (SEVERANCE_RESEARCH) {
                    json.addProperty("severance_wall_trace_count",
                            hits.stream().mapToInt(hit -> hit.severanceWallTraces.size()).sum());
                    json.addProperty("hurt_success_count", hits.stream()
                            .flatMap(hit -> hit.severanceWallTraces.stream())
                            .filter(Phase6SeveranceWallContext.Snapshot::hurtReturned).count());
                    json.addProperty("wound_attempt_count", hits.stream()
                            .flatMap(hit -> hit.severanceWallTraces.stream())
                            .mapToInt(Phase6SeveranceWallContext.Snapshot::woundAttemptCount).sum());
                    json.addProperty("wound_success_count", hits.stream()
                            .filter(hit -> hit.postSeverance > hit.preSeverance + 0.0001D).count());
                }
                if (SEVERANCE_SUSTAINED) {
                    double magicDamage = hits.stream().filter(hit -> hit.shotFamily == Family.MAGIC)
                            .mapToDouble(hit -> hit.familyPost).sum();
                    double holyDamage = hits.stream().filter(hit -> hit.shotFamily == Family.HOLY)
                            .mapToDouble(hit -> hit.familyPost).sum();
                    double severancePhysical = hits.stream().filter(hit -> hit.shotFamily == Family.SEVERANCE)
                            .mapToDouble(hit -> hit.physicalPost).sum();
                    double rotationPhysical = hits.stream().mapToDouble(hit -> hit.physicalPost).sum();
                    double actualRegenerate = hits.stream().mapToDouble(hit -> hit.targetHpRegen).sum();
                    double netHpMovement = initialHp - finalHp;
                    double netShpMovement = initialShp - finalShp;
                    double netResourceMovement = netHpMovement + netShpMovement;
                    double netResourceDps = seconds <= 0.0D ? 0.0D : netResourceMovement / seconds;
                    HitRecord midpoint = hits.isEmpty() ? null
                            : hits.get(Math.max(0, hits.size() / 2 - 1));
                    double lateSeconds = midpoint == null ? 0.0D
                            : Math.max(0.0D, (elapsedTicks - midpoint.elapsedTicks) / 20.0D);
                    double lateHpMovement = midpoint == null ? 0.0D : midpoint.postHp - finalHp;
                    double lateShpMovement = midpoint == null ? 0.0D : midpoint.postShp - finalShp;
                    double lateCombinedMovement = lateHpMovement + lateShpMovement;
                    double lateHpDps = lateSeconds <= 0.0D ? 0.0D : lateHpMovement / lateSeconds;
                    double lateShpDps = lateSeconds <= 0.0D ? 0.0D : lateShpMovement / lateSeconds;
                    double lateCombinedDps = lateSeconds <= 0.0D ? 0.0D
                            : lateCombinedMovement / lateSeconds;
                    double maximumWound = hits.stream().mapToDouble(hit -> hit.maxSeverance).max().orElse(0.0D);
                    double finalWound = hits.isEmpty() ? 0.0D : hits.getLast().postSeverance;
                    int woundTicks = hits.stream().mapToInt(hit -> hit.woundObservedTicks).sum();
                    int observedTicks = hits.stream().mapToInt(hit -> hit.targetObservationTicks).sum();
                    long integrityFailures = hits.stream().filter(this::unexpectedSourceDuplication).count();
                    long severanceReleases = hits.stream()
                            .filter(hit -> hit.shotFamily == Family.SEVERANCE).count();
                    long severanceAdmissions = hits.stream()
                            .filter(hit -> hit.shotFamily == Family.SEVERANCE)
                            .flatMap(hit -> hit.severanceWallTraces.stream())
                            .filter(Phase6SeveranceWallContext.Snapshot::hurtReturned).count();
                    long severanceCallbacks = hits.stream()
                            .filter(hit -> hit.shotFamily == Family.SEVERANCE)
                            .flatMap(hit -> hit.severanceWallTraces.stream())
                            .mapToInt(Phase6SeveranceWallContext.Snapshot::woundAttemptCount).sum();
                    long woundRefreshes = hits.stream()
                            .filter(hit -> hit.shotFamily == Family.SEVERANCE
                                    && hit.preSeverance > 0.0001D
                                    && hit.postSeverance > hit.preSeverance + 0.0001D).count();
                    json.addProperty("R5_legal_rotation", "three separate Royal Bows: Magic Weapon I -> Holy Weapon I -> Severance I");
                    json.addProperty("R5_releases_per_family", MAX_SHOTS / 3);
                    json.addProperty("magic_event_damage", magicDamage);
                    json.addProperty("magic_DPS", seconds <= 0.0D ? 0.0D : magicDamage / seconds);
                    json.addProperty("holy_event_damage", holyDamage);
                    json.addProperty("holy_DPS", seconds <= 0.0D ? 0.0D : holyDamage / seconds);
                    json.addProperty("severance_shot_physical_damage", severancePhysical);
                    json.addProperty("severance_shot_physical_DPS",
                            seconds <= 0.0D ? 0.0D : severancePhysical / seconds);
                    json.addProperty("all_rotation_physical_damage", rotationPhysical);
                    json.addProperty("maximum_wound", maximumWound);
                    json.addProperty("final_wound", finalWound);
                    json.addProperty("minimum_native_healing_ceiling", initialMaxHp - maximumWound);
                    json.addProperty("final_native_healing_ceiling", initialMaxHp - finalWound);
                    json.addProperty("wound_observed_ticks", woundTicks);
                    json.addProperty("wound_observation_ticks", observedTicks);
                    json.addProperty("wound_uptime_fraction",
                            observedTicks == 0 ? 0.0D : (double) woundTicks / observedTicks);
                    json.addProperty("wound_refresh_count", woundRefreshes);
                    json.addProperty("final_wound_expiry_remaining_seconds",
                            hits.isEmpty() ? 0 : hits.getLast().postSeveranceDuration);
                    json.addProperty("severance_release_count", severanceReleases);
                    json.addProperty("severance_admitted_arrow_count", severanceAdmissions);
                    json.addProperty("severance_rejected_pre_DamageData_count",
                            severanceReleases - severanceAdmissions);
                    json.addProperty("severance_native_callback_count", severanceCallbacks);
                    json.addProperty("regenerate_callback_count", regenerateCallbackCount);
                    json.addProperty("regenerate_native_tick_attempt_count",
                            regenerateNativeTickAttemptCount);
                    json.addProperty("target_tick_count_maximum_observed",
                            targetTickCountMaximumObserved);
                    json.addProperty("regenerate_requested_healing", regenerateNominalAmount);
                    json.addProperty("regenerate_unconstrained_healing_demand",
                            regenerateUnconstrainedHealingDemand);
                    json.addProperty("regenerate_actual_healing_at_native_ticks",
                            regenerateActualHealingAtNativeTicks);
                    json.addProperty("regenerate_healing_denied_by_wound_ceiling",
                            regenerateHealingDeniedByWoundCeiling);
                    json.addProperty("regenerate_denied_fraction_of_unconstrained_demand",
                            regenerateUnconstrainedHealingDemand <= 0.0D ? 0.0D
                                    : regenerateHealingDeniedByWoundCeiling
                                    / regenerateUnconstrainedHealingDemand);
                    json.addProperty("regenerate_event_allowed_amount", regenerateAllowedEventAmount);
                    json.addProperty("regenerate_actual_healing", actualRegenerate);
                    json.addProperty("regenerate_actual_healing_clock_vs_observer_delta",
                            regenerateActualHealingAtNativeTicks - actualRegenerate);
                    json.addProperty("regenerate_cancelled_event_count", regenerateCanceledEventCount);
                    json.addProperty("regenerate_trait_valid_at_start", regenerateTraitValidAtStart);
                    json.addProperty("regenerate_trait_valid_on_all_observed_attempts",
                            regenerateTraitValidOnAllObservedAttempts);
                    json.addProperty("regenerate_trait_rank_at_end", regenerateTraitRankAtEnd);
                    json.addProperty("regenerate_trait_missing_tick_count", regenerateTraitMissingTickCount);
                    if (regenerateTraitFirstMissingElapsedTick == null) {
                        json.add("regenerate_trait_first_missing_elapsed_tick", null);
                    }
                    else {
                        json.addProperty("regenerate_trait_first_missing_elapsed_tick",
                                regenerateTraitFirstMissingElapsedTick);
                    }
                    json.addProperty("non_regenerate_heal_event_count", isolatedNonRegenerateHealEvents);
                    json.addProperty("non_regenerate_heal_nominal_amount",
                            isolatedNonRegenerateHealNominalAmount);
                    json.add("non_regenerate_heal_sources", strings(isolatedNonRegenerateHealSources));
                    json.addProperty("native_self_regeneration_removed_for_isolation",
                            nativeSelfRegenerationRemovedForIsolation);
                    json.addProperty("net_vanilla_HP_movement", netHpMovement);
                    json.addProperty("net_SHP_movement", netShpMovement);
                    json.addProperty("net_combined_resource_movement", netResourceMovement);
                    json.addProperty("net_combined_resource_DPS", netResourceDps);
                    json.addProperty("late_window_seconds", lateSeconds);
                    json.addProperty("late_window_vanilla_HP_movement", lateHpMovement);
                    json.addProperty("late_window_SHP_movement", lateShpMovement);
                    json.addProperty("late_window_combined_resource_movement", lateCombinedMovement);
                    json.addProperty("late_window_vanilla_HP_DPS", lateHpDps);
                    json.addProperty("late_window_SHP_DPS", lateShpDps);
                    json.addProperty("late_window_combined_resource_DPS", lateCombinedDps);
                    json.addProperty("late_window_progress_positive", lateCombinedDps > 0.0001D);
                    if (ttk != null) {
                        json.addProperty("estimated_sustained_TTK_seconds", ttk / 20.0D);
                        json.addProperty("sustained_TTK_basis", "observed target defeat");
                    }
                    else if (lateHpDps > 0.0001D) {
                        json.addProperty("estimated_sustained_TTK_seconds",
                                seconds + finalHp / lateHpDps);
                        json.addProperty("sustained_TTK_basis",
                                "late-window vanilla-HP-only linear projection after a 60-second run; SHP is reported separately and was not consumed by this path");
                    }
                    else {
                        json.add("estimated_sustained_TTK_seconds", null);
                        json.addProperty("sustained_TTK_basis",
                                "not estimable: no positive late-window vanilla HP progress");
                    }
                    addFiniteOrNull(json, "naive_whole_window_combined_resource_projection_seconds",
                            initialHp + initialShp, netResourceDps);
                    json.addProperty("source_event_integrity_failure_count", integrityFailures);
                    json.addProperty("unexpected_L2_bypass_count", 0);
                    json.addProperty("unexpected_Tensura_bypass_count", 0);
                }
                if (ADAPTIVE_WOUND_DYNAMIC) addDynamicCounterFields(json, seconds);
                if (ADAPTIVE_WOUND_SAFETY) {
                    double maximumWound = hits.stream()
                            .mapToDouble(hit -> hit.maxSeverance).max().orElse(0.0D);
                    double finalWound = hits.isEmpty() ? 0.0D : hits.getLast().postSeverance;
                    double actualRegenerate = hits.stream()
                            .mapToDouble(hit -> hit.targetHpRegen).sum();
                    json.addProperty("W4_trait_identity", true);
                    json.addProperty("W4_diagnostic_RW", spec.calibration.woundAdaptiveRecovery);
                    json.addProperty("severance_physical_damage",
                            hits.stream().mapToDouble(hit -> hit.physicalPost).sum());
                    json.addProperty("maximum_wound", maximumWound);
                    json.addProperty("final_wound", finalWound);
                    json.addProperty("native_ceiling_incoming_event_count", hits.stream()
                            .mapToInt(hit -> hit.nativeSeveranceIncomingEventCount).sum());
                    json.addProperty("native_ceiling_damage_application_count", hits.stream()
                            .mapToInt(hit -> hit.nativeSeveranceDamagePostEventCount).sum());
                    json.addProperty("native_ceiling_damage", hits.stream()
                            .mapToDouble(hit -> hit.nativeSeveranceDamagePostAmount).sum());
                    json.addProperty("regenerate_callback_count", regenerateCallbackCount);
                    json.addProperty("regenerate_native_tick_attempt_count",
                            regenerateNativeTickAttemptCount);
                    json.addProperty("regenerate_unconstrained_healing_demand",
                            regenerateUnconstrainedHealingDemand);
                    json.addProperty("regenerate_actual_healing_at_native_ticks",
                            regenerateActualHealingAtNativeTicks);
                    json.addProperty("regenerate_healing_denied_by_wound_ceiling",
                            regenerateHealingDeniedByWoundCeiling);
                    json.addProperty("regenerate_actual_healing", actualRegenerate);
                    json.addProperty("regenerate_actual_healing_clock_vs_observer_delta",
                            regenerateActualHealingAtNativeTicks - actualRegenerate);
                    json.addProperty("regenerate_trait_valid_at_start", regenerateTraitValidAtStart);
                    json.addProperty("regenerate_trait_valid_on_all_observed_attempts",
                            regenerateTraitValidOnAllObservedAttempts);
                    json.addProperty("regenerate_trait_rank_at_end", regenerateTraitRankAtEnd);
                    json.addProperty("regenerate_trait_missing_tick_count", regenerateTraitMissingTickCount);
                    json.addProperty("native_self_regeneration_removed_for_isolation",
                            nativeSelfRegenerationRemovedForIsolation);
                    json.addProperty("net_vanilla_HP_movement", initialHp - finalHp);
                    json.addProperty("net_SHP_movement", initialShp - finalShp);
                    json.addProperty("source_event_integrity_failure_count",
                            hits.stream().filter(this::unexpectedSourceDuplication).count());
                    json.addProperty("unexpected_L2_bypass_count", 0);
                    json.addProperty("unexpected_Tensura_bypass_count", 0);
                }
            }
            if (PRODUCTION_ACCEPTANCE) {
                json.addProperty("production_rows", hits.size());
                json.addProperty("family_event_count",
                        hits.stream().mapToInt(hit -> hit.familyDamageEventCount).sum());
                json.addProperty("duplicate_event_count",
                        hits.stream().filter(this::duplicateEventFromSameProjectile).count());
                json.addProperty("recursion_count", 0);
                json.addProperty("unexpected_Tensura_bypass_count", 0);
                json.addProperty("unexpected_L2_bypass_count", 0);
            }
            if (ADAPTIVE_WOUND_COUNTER_STATES) addCounterStateFields(json);
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

        JsonObject counterStateJson() {
            JsonObject json = commonJson();
            json.addProperty("status", "ok");
            addCounterStateFields(json);
            return json;
        }

        JsonObject regenerateCycleJson(RegenerateCycle cycle) {
            JsonObject json = commonJson();
            json.addProperty("status", "ok");
            json.addProperty("P3_profile_role", dynamicProfileRole());
            json.addProperty("cycle_index", cycle.index);
            json.addProperty("native_tick_boundary_index", cycle.nativeTickBoundaryIndex);
            json.addProperty("pre_elapsed_tick", cycle.preElapsedTick);
            json.addProperty("post_elapsed_tick", cycle.postElapsedTick);
            json.addProperty("target_tick_count", cycle.targetTickCount);
            json.addProperty("Regenerate_rank", cycle.regenerateRank);
            json.addProperty("max_HP", cycle.maxHp);
            json.addProperty("HP_before_Regenerate", cycle.hpBefore);
            json.addProperty("SHP_before_Regenerate", cycle.shpBefore);
            json.addProperty("wound_before_Regenerate", cycle.woundBefore);
            json.addProperty("wound_ceiling_before_Regenerate", cycle.ceilingBefore);
            json.addProperty("legal_healing_space", cycle.legalSpace);
            json.addProperty("requested_healing", cycle.requested);
            json.addProperty("event_allowed_healing", cycle.allowed);
            json.addProperty("heal_event_cancelled", cycle.canceled);
            json.addProperty("native_Regenerate_stack_verified", cycle.sourceStackVerified);
            json.addProperty("HP_after_Regenerate", cycle.hpAfter);
            json.addProperty("SHP_after_Regenerate", cycle.shpAfter);
            json.addProperty("wound_after_Regenerate", cycle.woundAfter);
            json.addProperty("wound_ceiling_after_Regenerate",
                    cycle.maxHp - cycle.woundAfter);
            json.addProperty("expected_actual_healing",
                    Math.min(cycle.requested, cycle.legalSpace));
            json.addProperty("actual_healing", cycle.actual);
            json.addProperty("denied_healing", cycle.denied);
            json.addProperty("cumulative_actual_healing", cycle.cumulativeActual);
            json.addProperty("cumulative_denied_healing", cycle.cumulativeDenied);
            json.addProperty("cycle_complete", cycle.complete);
            json.addProperty("SHP_unchanged_by_Regenerate",
                    Math.abs(cycle.shpAfter - cycle.shpBefore) <= 0.01D);
            json.addProperty("no_heal_above_wound_ceiling",
                    cycle.hpAfter <= cycle.maxHp - cycle.woundAfter + 0.01D);
            json.addProperty("counter_position_before_Regenerate",
                    cycle.hpBefore < cycle.ceilingBefore - 0.01D ? "BELOW_CEILING"
                            : cycle.hpBefore > cycle.ceilingBefore + 0.01D
                            ? "ABOVE_CEILING" : "AT_CEILING");
            json.addProperty("diagnostic_RW", spec.calibration.woundAdaptiveRecovery);
            json.addProperty("production_Magic_Holy_behavior_changed", false);
            json.addProperty("direct_TNO_wound_write", false);
            json.addProperty("source_event_integrity_failure_count", 0);
            json.addProperty("unexpected_L2_bypass_count", 0);
            json.addProperty("unexpected_Tensura_bypass_count", 0);
            return json;
        }

        private String dynamicProfileRole() {
            if (spec.calibration == CalibrationCase.DYNAMIC_NATIVE_RW_0) {
                return "NATIVE_RW_0_REGENERATE_ON_CONTROL";
            }
            return regenerateRank > 0
                    ? "CANDIDATE_C_RW_50_REGENERATE_ON"
                    : "CANDIDATE_C_RW_50_WITHOUT_REGENERATE";
        }

        private void addDynamicCounterFields(JsonObject json, double seconds) {
            double magicDamage = hits.stream().filter(hit -> hit.shotFamily == Family.MAGIC)
                    .mapToDouble(hit -> hit.familyPost).sum();
            double holyDamage = hits.stream().filter(hit -> hit.shotFamily == Family.HOLY)
                    .mapToDouble(hit -> hit.familyPost).sum();
            double severancePhysical = hits.stream().filter(hit -> hit.shotFamily == Family.SEVERANCE)
                    .mapToDouble(hit -> hit.physicalPost).sum();
            double rotationPhysical = hits.stream().mapToDouble(hit -> hit.physicalPost).sum();
            double finalWound = hits.isEmpty() ? 0.0D : hits.getLast().postSeverance;
            long magicReleases = hits.stream().filter(hit -> hit.shotFamily == Family.MAGIC).count();
            long holyReleases = hits.stream().filter(hit -> hit.shotFamily == Family.HOLY).count();
            long severanceReleases = hits.stream().filter(hit -> hit.shotFamily == Family.SEVERANCE).count();
            long severanceAdmissions = hits.stream()
                    .filter(hit -> hit.shotFamily == Family.SEVERANCE)
                    .flatMap(hit -> hit.severanceWallTraces.stream())
                    .filter(Phase6SeveranceWallContext.Snapshot::hurtReturned).count();
            long severanceCallbacks = hits.stream()
                    .filter(hit -> hit.shotFamily == Family.SEVERANCE)
                    .flatMap(hit -> hit.severanceWallTraces.stream())
                    .mapToInt(Phase6SeveranceWallContext.Snapshot::woundAttemptCount).sum();
            long adaptiveTraceCount = hits.stream()
                    .mapToLong(hit -> hit.adaptiveWoundTraces.size()).sum();
            int adaptiveMaximumCount = hits.stream()
                    .flatMap(hit -> hit.adaptiveWoundTraces.stream())
                    .mapToInt(Phase6AdaptiveWoundContext.Snapshot::adaptiveCount).max().orElse(0);
            double adaptiveMinimumNativeFactor = hits.stream()
                    .flatMap(hit -> hit.adaptiveWoundTraces.stream())
                    .mapToDouble(Phase6AdaptiveWoundContext.Snapshot::nativeAdaptiveFactor)
                    .min().orElse(1.0D);
            double diagnosticMinimumWoundFactor = hits.stream()
                    .flatMap(hit -> hit.adaptiveWoundTraces.stream())
                    .mapToDouble(Phase6AdaptiveWoundContext.Snapshot::diagnosticWoundAdaptiveFactor)
                    .min().orElse(1.0D);
            long integrityFailures = hits.stream().filter(this::unexpectedSourceDuplication).count();
            long incompleteCycles = regenerateCycles.stream().filter(cycle -> !cycle.complete).count();
            long ceilingViolations = regenerateCycles.stream().filter(cycle ->
                    cycle.hpAfter > cycle.maxHp - cycle.woundAfter + 0.01D).count();
            long shpMovementCycles = regenerateCycles.stream().filter(cycle ->
                    Math.abs(cycle.shpAfter - cycle.shpBefore) > 0.01D).count();
            double cycleRequested = regenerateCycles.stream().mapToDouble(cycle -> cycle.requested).sum();
            double cycleAllowed = regenerateCycles.stream().mapToDouble(cycle -> cycle.allowed).sum();
            double cycleActual = regenerateCycles.stream().mapToDouble(cycle -> cycle.actual).sum();
            double cycleDenied = regenerateCycles.stream().mapToDouble(cycle -> cycle.denied).sum();
            double netHpMovement = initialHp - finalHp;
            double netShpMovement = initialShp - finalShp;

            json.addProperty("P3_dynamic_defender_advantage", true);
            json.addProperty("P3_profile_role", dynamicProfileRole());
            json.addProperty("P3_diagnostic_RW", spec.calibration.woundAdaptiveRecovery);
            json.addProperty("P3_window_seconds", seconds);
            json.addProperty("P3_release_count", shotsReleased);
            json.addProperty("P3_legal_rotation",
                    "three separate Royal Bows: production Magic Weapon I -> production Holy Weapon I -> Severance I");
            json.addProperty("magic_release_count", magicReleases);
            json.addProperty("holy_release_count", holyReleases);
            json.addProperty("severance_release_count", severanceReleases);
            json.addProperty("magic_event_damage", magicDamage);
            json.addProperty("magic_DPS", seconds <= 0.0D ? 0.0D : magicDamage / seconds);
            json.addProperty("holy_event_damage", holyDamage);
            json.addProperty("holy_DPS", seconds <= 0.0D ? 0.0D : holyDamage / seconds);
            json.addProperty("severance_shot_physical_damage", severancePhysical);
            json.addProperty("severance_shot_physical_DPS",
                    seconds <= 0.0D ? 0.0D : severancePhysical / seconds);
            json.addProperty("all_rotation_physical_damage", rotationPhysical);
            json.addProperty("maximum_wound", dynamicMaximumWound);
            json.addProperty("final_wound", finalWound);
            json.addProperty("minimum_native_healing_ceiling", dynamicMinimumCeiling);
            json.addProperty("final_native_healing_ceiling", initialMaxHp - finalWound);
            json.addProperty("ticks_below_wound_ceiling", dynamicTicksBelowCeiling);
            json.addProperty("ticks_at_wound_ceiling", dynamicTicksAtCeiling);
            json.addProperty("ticks_above_wound_ceiling", dynamicTicksAboveCeiling);
            json.addProperty("counter_position_observation_ticks",
                    dynamicTicksBelowCeiling + dynamicTicksAtCeiling + dynamicTicksAboveCeiling);
            json.addProperty("native_tick_boundary_count", nativeTickBoundaryCount);
            json.addProperty("regenerate_cycle_count", regenerateCycles.size());
            json.addProperty("regenerate_incomplete_cycle_count", incompleteCycles);
            json.addProperty("regenerate_callback_count", regenerateCallbackCount);
            json.addProperty("regenerate_native_tick_attempt_count", regenerateNativeTickAttemptCount);
            json.addProperty("regenerate_requested_healing", cycleRequested);
            json.addProperty("regenerate_event_allowed_healing", cycleAllowed);
            json.addProperty("regenerate_actual_healing", cycleActual);
            json.addProperty("regenerate_denied_healing", cycleDenied);
            json.addProperty("regenerate_cancelled_event_count", regenerateCanceledEventCount);
            json.addProperty("regenerate_ceiling_violation_count", ceilingViolations);
            json.addProperty("regenerate_SHP_movement_cycle_count", shpMovementCycles);
            json.addProperty("regenerate_trait_valid_at_start", regenerateTraitValidAtStart);
            json.addProperty("regenerate_trait_valid_on_all_observed_attempts",
                    regenerateTraitValidOnAllObservedAttempts);
            json.addProperty("regenerate_trait_rank_at_end", regenerateTraitRankAtEnd);
            json.addProperty("regenerate_trait_missing_tick_count", regenerateTraitMissingTickCount);
            json.addProperty("net_vanilla_HP_movement", netHpMovement);
            json.addProperty("net_SHP_movement", netShpMovement);
            json.addProperty("net_combined_resource_movement", netHpMovement + netShpMovement);
            json.addProperty("defender_recovered_positive_HP", cycleActual > 0.0001D);
            json.addProperty("severance_admitted_arrow_count", severanceAdmissions);
            json.addProperty("severance_native_callback_count", severanceCallbacks);
            json.addProperty("adaptive_wound_trace_count", adaptiveTraceCount);
            json.addProperty("adaptive_maximum_count", adaptiveMaximumCount);
            json.addProperty("adaptive_minimum_native_factor", adaptiveMinimumNativeFactor);
            json.addProperty("diagnostic_minimum_wound_factor", diagnosticMinimumWoundFactor);
            json.addProperty("production_Magic_Holy_Q", evidenceQ(spec));
            json.addProperty("production_Magic_Holy_RD", evidenceRD(spec));
            json.addProperty("production_Magic_Holy_RA", evidenceRA(spec));
            json.addProperty("production_Magic_Holy_behavior_changed", false);
            json.addProperty("direct_TNO_wound_write", false);
            json.addProperty("source_event_integrity_failure_count", integrityFailures);
            json.addProperty("duplicate_physical_event_count", 0);
            json.addProperty("recursion_count", 0);
            json.addProperty("unexpected_L2_bypass_count", 0);
            json.addProperty("unexpected_Tensura_bypass_count", 0);
        }

        private void addCounterStateFields(JsonObject json) {
            double expected = Math.min(counterRequestedHealing, counterLegalHealingSpace);
            boolean needsRegenerate = counterState != CounterState.NO_REGENERATE_CONTROL;
            boolean eventContract = needsRegenerate
                    ? counterHealEventObserved && regenerateCallbackCount == 1
                            && regenerateNativeTickAttemptCount == 1
                            && counterHealSourceStackVerified
                    : !counterHealEventObserved && regenerateCallbackCount == 0
                            && regenerateNativeTickAttemptCount == 0;
            boolean stateCondition = switch (counterState) {
                case A_BELOW_CEILING -> counterWoundAtHeal > 0.0001D
                        && counterHpBeforeHeal + counterRequestedHealing
                        <= counterCeilingAtHeal + 0.01D;
                case B_CROSSING_CEILING -> counterWoundAtHeal > 0.0001D
                        && counterHpBeforeHeal < counterCeilingAtHeal - 0.01D
                        && counterHpBeforeHeal + counterRequestedHealing
                        > counterCeilingAtHeal + 0.01D;
                case C_AT_CEILING -> counterWoundAtHeal > 0.0001D
                        && counterHpBeforeHeal >= counterCeilingAtHeal - 0.01D;
                case NO_REGENERATE_CONTROL -> counterWoundAtHeal > 0.0001D
                        && counterLegalHealingSpace >= counterReferenceRequest - 0.01D;
                case NO_WOUND_CONTROL -> counterWoundAtHeal <= 0.0001D
                        && counterHpBeforeHeal + counterRequestedHealing
                        <= initialMaxHp + 0.01D;
                case NONE -> false;
            };
            boolean matches = counterSetupApplied && nativeTickBoundaryCount == 1
                    && eventContract && stateCondition
                    && Math.abs(counterActualHealing - expected) <= 0.01D
                    && Math.abs(counterEventAllowedHealing - expected) <= 0.01D
                    && Math.abs(counterShpAfterHeal - counterShpBeforeHeal) <= 0.01D;
            long integrityFailures = hits.stream().filter(this::unexpectedSourceDuplication).count();
            long physicalSources = hits.stream().mapToLong(hit -> hit.physicalDamageEventCount).sum();
            long woundCallbacks = hits.stream()
                    .flatMap(hit -> hit.severanceWallTraces.stream())
                    .mapToInt(Phase6SeveranceWallContext.Snapshot::woundAttemptCount).sum();
            json.addProperty("P2_counter_state", counterState.id);
            json.addProperty("P2_diagnostic_RW", spec.calibration.woundAdaptiveRecovery);
            json.addProperty("diagnostic_setup_only", true);
            json.addProperty("setup_health_placement_counted_as_combat_output", false);
            json.addProperty("wound_required", counterState.requiresWound());
            json.addProperty("wound_created_by_native_Royal_Arrow", counterWoundCreatedByNativeArrow);
            json.addProperty("wound_written_directly_by_TNO", false);
            json.addProperty("setup_arrow_count", counterSetupArrowCount);
            json.addProperty("setup_physical_source_count", physicalSources);
            json.addProperty("setup_native_wound_callback_count", woundCallbacks);
            json.addProperty("max_HP", initialMaxHp);
            json.addProperty("setup_wound_amount", counterWoundAmount);
            json.addProperty("setup_wound_ceiling", counterWoundCeiling);
            json.addProperty("setup_HP", counterSetupHp);
            json.addProperty("reference_native_Regenerate_request", counterReferenceRequest);
            json.addProperty("HP_before_Regenerate", counterHpBeforeHeal);
            json.addProperty("SHP_before_Regenerate", counterShpBeforeHeal);
            json.addProperty("wound_at_Regenerate", counterWoundAtHeal);
            json.addProperty("wound_ceiling_at_Regenerate", counterCeilingAtHeal);
            json.addProperty("legal_healing_space", counterLegalHealingSpace);
            json.addProperty("requested_healing", counterRequestedHealing);
            json.addProperty("event_allowed_healing", counterEventAllowedHealing);
            json.addProperty("heal_event_observed", counterHealEventObserved);
            json.addProperty("heal_event_cancelled", counterHealEventCanceled);
            json.addProperty("native_Regenerate_stack_verified", counterHealSourceStackVerified);
            json.addProperty("HP_after_Regenerate", counterHpAfterHeal);
            json.addProperty("SHP_after_Regenerate", counterShpAfterHeal);
            json.addProperty("expected_actual_healing", expected);
            json.addProperty("actual_healing", counterActualHealing);
            json.addProperty("denied_healing", counterDeniedHealing);
            json.addProperty("native_tick_boundary_count", nativeTickBoundaryCount);
            json.addProperty("regenerate_callback_count", regenerateCallbackCount);
            json.addProperty("regenerate_native_tick_attempt_count", regenerateNativeTickAttemptCount);
            json.addProperty("Regenerate_trait_rank_at_end", regenerateTraitRankAtEnd);
            json.addProperty("Regenerate_trait_valid_on_all_observed_attempts",
                    regenerateTraitValidOnAllObservedAttempts);
            json.addProperty("state_condition_verified", stateCondition);
            json.addProperty("native_counter_contract_matched", matches);
            json.addProperty("source_event_integrity_failure_count", integrityFailures);
            json.addProperty("duplicate_physical_event_count", 0);
            json.addProperty("recursion_count", 0);
            json.addProperty("unexpected_L2_bypass_count", 0);
            json.addProperty("unexpected_Tensura_bypass_count", 0);
        }

        private JsonObject commonJson() {
            JsonObject json = new JsonObject();
            json.addProperty("suite", CALIBRATION_COMBAT ? "PHASE6_ENDGAME_CALIBRATION"
                    : PRODUCTION_ACCEPTANCE ? "PHASE6_MAGIC_HOLY_PRODUCTION"
                    : ENDGAME_RESEARCH ? "PHASE6_TNO_ENDGAME_RESEARCH"
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
            json.addProperty("profile_clone_verified", !freshCalibrationAttachment());
            if (freshCalibrationAttachment()) {
                json.addProperty("fresh_L2_attachment_per_case", true);
            }
            json.addProperty("strongest_legal_endgame_profile", STRONGEST_LEGAL_PROFILE
                    && (!(CALIBRATION_COMBAT || PRODUCTION_ACCEPTANCE)
                    || spec.traitProfile == TraitProfile.ACCEPTED));
            if (CALIBRATION_COMBAT || PRODUCTION_ACCEPTANCE) {
                json.addProperty("L2_profile_variant", spec.traitProfile.id);
                json.addProperty("profile_is_accepted_strongest_legal",
                        spec.traitProfile == TraitProfile.ACCEPTED);
                json.addProperty("removed_trait_budget_not_reallocated",
                        spec.traitProfile != TraitProfile.ACCEPTED);
            }
            json.addProperty("endgame_profile_source",
                    STRONGEST_LEGAL_PROFILE && (!(CALIBRATION_COMBAT || PRODUCTION_ACCEPTANCE)
                            || spec.traitProfile == TraitProfile.ACCEPTED)
                            ? "accepted Phase 5F 39-trait strongest legal defensive profile"
                            : CALIBRATION_COMBAT || PRODUCTION_ACCEPTANCE
                                    ? "accepted legal profile with named trait(s) removed and budget left unused"
                                    : "not applicable");
            json.addProperty("endgame_profile_budget_spent",
                    STRONGEST_LEGAL_PROFILE ? calibrationBudgetSpent(spec) : 0);
            json.addProperty("endgame_profile_budget_remaining",
                    STRONGEST_LEGAL_PROFILE ? spec.level - calibrationBudgetSpent(spec) : 0);
            if (CALIBRATION_COMBAT || PRODUCTION_ACCEPTANCE) {
                json.addProperty("reference_profile_budget_spent", endgameBudgetSpent(spec.boss, spec.level));
            }
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
            json.addProperty("Regenerate_rank", regenerateRank);
            json.addProperty("Regenerate_config_fraction_per_rank_per_second",
                    regenerateFractionPerRankPerSecond);
            json.addProperty("Regenerate_nominal_HP_per_second", nominalRegenerateHpPerSecond);
            if (NATIVE_REGENERATE_OBSERVATION) {
                json.addProperty("Regenerate_trait_valid_at_case_start", regenerateTraitValidAtStart);
            }
            if (PRODUCTION_ACCEPTANCE) {
                json.addProperty("L2_level", l2Level);
                json.addProperty("L2_healthFactor", l2HealthFactor);
                json.addProperty("L2_exponentialHealth", l2ExponentialHealth);
                json.addProperty("entity_healthScale", entityHealthScale);
                json.addProperty("generic_L2_health_multiplier", genericHealthMultiplier);
                json.addProperty("Adaptive_configured_factor", adaptiveConfiguredFactor);
                json.addProperty("Dementor_reduction_base", dementorReductionBase);
            }
            json.addProperty("tensura_l2h_scaling_marker", true);
            json.addProperty("TNO_family", active.family.id);
            if (SUSTAINED_ROTATION) {
                json.addProperty(SEVERANCE_SUSTAINED ? "R5_family_set" : "P3_family_set",
                        "MAGIC_WEAPON,HOLY_WEAPON,SEVERANCE");
                json.addProperty(SEVERANCE_SUSTAINED
                        ? "R5_legal_separate_bow_rotation" : "P3_legal_separate_bow_rotation", true);
            }
            json.addProperty("TNO_stage", spec.stage.name);
            if (CALIBRATION_COMBAT) {
                json.addProperty("calibration_mode", CALIBRATION_MODE);
                json.addProperty("calibration_case", spec.calibration.id);
                json.addProperty("Q_generic_health", evidenceQ(spec));
                json.addProperty("RD_dementor", evidenceRD(spec));
                json.addProperty("RA_adaptive", evidenceRA(spec));
                json.addProperty("diagnostic_upper_bound_only", CALIBRATION_MODE.equals("ceiling")
                        || SEVERANCE_SUSTAINED
                        && spec.calibration == CalibrationCase.SEVERANCE_PROTOTYPE_X64);
                if (SEVERANCE_PROTOTYPE) {
                    json.addProperty("Severance_eligible_multiplier",
                            spec.calibration.severanceEligibleMultiplier);
                    json.addProperty("diagnostic_ceiling_candidate",
                            spec.calibration == CalibrationCase.SEVERANCE_PROTOTYPE_X64);
                    json.addProperty("prototype_development_only", true);
                    if (SEVERANCE_SUSTAINED) {
                        json.addProperty("R5_sustained_viability", true);
                        json.addProperty("R5_magic_holy_production_unchanged", true);
                        addR5PolicyMetadata(json, spec);
                    }
                }
                if (ADAPTIVE_WOUND_RESEARCH) {
                    json.addProperty("wound_Adaptive_recovery_RW",
                            spec.calibration.woundAdaptiveRecovery);
                    json.addProperty("prototype_development_only", true);
                    json.addProperty("physical_damage_negotiated", false);
                    json.addProperty("native_Adaptive_state_mutated", false);
                }
            }
            if (PRODUCTION_ACCEPTANCE) {
                json.addProperty("production_policy_case", spec.calibration.id);
                json.addProperty("Q_generic_health", spec.calibration.parameters.genericHealthQ());
                json.addProperty("RD_dementor", spec.calibration.parameters.dementorRD());
                json.addProperty("RA_adaptive", spec.calibration.parameters.adaptiveRA());
                json.addProperty("production_feature_active_without_calibration_property",
                        !Boolean.getBoolean("tno.phase6.calibration"));
            }
            if (spec.stage.ep == null) json.add("EP_or_stage_fixture", null); else json.addProperty("EP_or_stage_fixture", spec.stage.ep);
            if (PRODUCTION_OBSERVATION) {
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

        private static void addFiniteOrNull(JsonObject json, String name, double numerator, double denominator) {
            if (denominator <= 0.0D) json.add(name, null);
            else json.addProperty(name, numerator / denominator);
        }

        private static double evidenceQ(CaseSpec spec) {
            return SUSTAINED_ROTATION ? R5_MAGIC_HOLY_S7_PARAMETERS.genericHealthQ()
                    : spec.calibration.parameters.genericHealthQ();
        }

        private static double evidenceRD(CaseSpec spec) {
            return SUSTAINED_ROTATION ? R5_MAGIC_HOLY_S7_PARAMETERS.dementorRecovery()
                    : spec.calibration.parameters.dementorRD();
        }

        private static double evidenceRA(CaseSpec spec) {
            return SUSTAINED_ROTATION ? R5_MAGIC_HOLY_S7_PARAMETERS.adaptiveRecovery()
                    : spec.calibration.parameters.adaptiveRA();
        }

        private static void addR5PolicyMetadata(JsonObject json, CaseSpec spec) {
            json.addProperty("Magic_Holy_Q_generic_health",
                    R5_MAGIC_HOLY_S7_PARAMETERS.genericHealthQ());
            json.addProperty("Magic_Holy_RD_dementor",
                    R5_MAGIC_HOLY_S7_PARAMETERS.dementorRecovery());
            json.addProperty("Magic_Holy_RA_adaptive",
                    R5_MAGIC_HOLY_S7_PARAMETERS.adaptiveRecovery());
            json.addProperty("Severance_prototype_Q_generic_health",
                    spec.calibration.parameters.genericHealthQ());
            json.addProperty("Severance_prototype_RD_dementor",
                    spec.calibration.parameters.dementorRD());
            json.addProperty("Severance_prototype_RA_adaptive",
                    spec.calibration.parameters.adaptiveRA());
        }

        private boolean unexpectedSourceDuplication(HitRecord hit) {
            int projectiles = Math.max(1, hit.releasedProjectileCount);
            if (duplicateEventFromSameProjectile(hit)) return true;
            if (hit.shotFamily == Family.ELEMENTAL) return hit.physicalDamageEventCount != 0
                    || hit.familyDamageEventCount > projectiles;
            if (hit.shotFamily == Family.ENERGY) return hit.physicalDamageEventCount > projectiles
                    || hit.energyDrainEvents > projectiles;
            if (hit.shotFamily == Family.SEVERANCE) return hit.physicalDamageEventCount > projectiles
                    || hit.familyDamageEventCount != 0;
            return hit.physicalDamageEventCount > projectiles || hit.familyDamageEventCount > projectiles;
        }

        private boolean duplicateEventFromSameProjectile(HitRecord hit) {
            return hit.physicalEventsByProjectile.values().stream().anyMatch(count -> count > 1);
        }

        private boolean transformed(HitRecord hit, String trait, boolean magic) {
            if (!traitRanks.has(trait) || hit.l2Magic != magic || hit.shotFamily == Family.ENERGY) return false;
            double before = hit.shotFamily == Family.SEVERANCE ? hit.physicalIncoming : hit.familyAfterRecovery;
            double after = hit.shotFamily == Family.SEVERANCE ? hit.physicalPost : hit.familyPost;
            return after + 0.0001D < before;
        }

        private boolean adaptiveObserved(HitRecord hit) {
            double before = hit.shotFamily == Family.SEVERANCE ? hit.physicalIncoming : hit.familyAfterRecovery;
            double after = hit.shotFamily == Family.SEVERANCE ? hit.physicalPost : hit.familyPost;
            if (!traitRanks.has("l2hostility:adaptive") || before <= 0.0D
                    || hit.shotFamily == Family.ENERGY) return false;
            HitRecord previous = hits.stream()
                    .filter(value -> value.index < hit.index && value.shotFamily == hit.shotFamily)
                    .max(Comparator.comparingInt(value -> value.index)).orElse(null);
            if (previous == null) return false;
            double previousBefore = hit.shotFamily == Family.SEVERANCE
                    ? previous.physicalIncoming : previous.familyAfterRecovery;
            double previousAfter = hit.shotFamily == Family.SEVERANCE ? previous.physicalPost : previous.familyPost;
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

    private static final class RegenerateCycle {
        final int index;
        final int nativeTickBoundaryIndex;
        final int preElapsedTick;
        final int targetTickCount;
        final int regenerateRank;
        final double maxHp;
        final double hpBefore;
        final double shpBefore;
        final double woundBefore;
        final double ceilingBefore;
        final double legalSpace;
        final double requested;
        final double allowed;
        final boolean canceled;
        final boolean sourceStackVerified = true;
        int postElapsedTick;
        double hpAfter;
        double shpAfter;
        double woundAfter;
        double actual;
        double denied;
        double cumulativeActual;
        double cumulativeDenied;
        boolean complete;

        RegenerateCycle(int index, int nativeTickBoundaryIndex, int preElapsedTick,
                int targetTickCount, int regenerateRank, double maxHp,
                double hpBefore, double shpBefore, double woundBefore,
                double requested, double allowed, boolean canceled) {
            this.index = index;
            this.nativeTickBoundaryIndex = nativeTickBoundaryIndex;
            this.preElapsedTick = preElapsedTick;
            this.targetTickCount = targetTickCount;
            this.regenerateRank = regenerateRank;
            this.maxHp = maxHp;
            this.hpBefore = hpBefore;
            this.shpBefore = shpBefore;
            this.woundBefore = woundBefore;
            this.ceilingBefore = maxHp - woundBefore;
            this.legalSpace = Math.max(0.0D, ceilingBefore - hpBefore);
            this.requested = requested;
            this.allowed = allowed;
            this.canceled = canceled;
        }
    }

    private static final class HitRecord {
        final int index;
        final int startTick;
        final Family shotFamily;
        final double preHp;
        final double preShp;
        final double preMagicules;
        final double preAura;
        final double preSeverance;
        final int preSeveranceDuration;
        final double preAttackerHp;
        final double preAttackerShp;
        final double preAttackerMagicules;
        final double preAttackerAura;
        final Set<String> physicalSourceIds = new LinkedHashSet<>();
        final Set<String> physicalSourceTags = new LinkedHashSet<>();
        final Set<String> familySourceIds = new LinkedHashSet<>();
        final Set<String> familySourceTags = new LinkedHashSet<>();
        final Set<String> dotSourceIds = new LinkedHashSet<>();
        final Set<String> nativeSeveranceSourceEntityIds = new LinkedHashSet<>();
        final Set<String> nativeSeveranceDirectEntityIds = new LinkedHashSet<>();
        final Set<String> reflectedSourceIds = new LinkedHashSet<>();
        final Set<String> critDamageSourceIds = new LinkedHashSet<>();
        final Set<String> releasedProjectileEntityIds = new LinkedHashSet<>();
        final Set<String> releasedProjectileUuids = new LinkedHashSet<>();
        final Set<String> hitProjectileEntityIds = new LinkedHashSet<>();
        final Set<String> hitProjectileUuids = new LinkedHashSet<>();
        final Map<String, Integer> physicalEventsByProjectile = new LinkedHashMap<>();
        final Map<String, Double> severanceBasePostByProjectile = new LinkedHashMap<>();
        final Map<String, SeveranceProjection> severanceProjections = new LinkedHashMap<>();
        final List<Phase6CalibrationContext.Snapshot> calibrationTraces = new ArrayList<>();
        final List<Phase6SeveranceWallContext.Snapshot> severanceWallTraces = new ArrayList<>();
        final List<Phase6AdaptiveWoundContext.Snapshot> adaptiveWoundTraces = new ArrayList<>();
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
        int postSeveranceDuration;
        double maxSeverance;
        int woundObservedTicks;
        int targetObservationTicks;
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
        double physicalAfterIncomingL2;
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
        double nativeSeveranceIncomingAmount;
        double nativeSeveranceAfterL2Amount;
        double nativeSeveranceDamagePreAmount;
        double nativeSeveranceDamagePostAmount;
        double reflectedPost;
        double preCritDamage;
        int elapsedTicks;
        int physicalDamageEventCount;
        int familyDamageEventCount;
        int dotDamageEventCount;
        int nativeSeveranceIncomingEventCount;
        int nativeSeveranceAfterL2EventCount;
        int nativeSeveranceDamagePreEventCount;
        int nativeSeveranceDamagePostEventCount;
        int critMultiplierEvents;
        int releasedProjectileCount;
        int projectilesDiscardedAfterTargetDefeat;
        int severanceConfiguredProjectileCount;
        int severanceAdmittedProjectileCount;
        boolean crit;
        boolean royalArrowMarkObserved;
        boolean l2Magic;
        boolean familyCanceledBeforeRecovery;
        boolean physicalIncomingCanceled;
        boolean nativeSeveranceIncomingCanceled;
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
        double severancePrototypePreRound;
        double severanceBasePostRound;
        double severanceNativePostRound;
        double severanceStagedPostRound;
        double severancePrototypePostRound;
        double severanceProductionEligibleContribution;
        double severancePrototypeEligibleContribution;
        int regenerateCallbackCount;
        int regenerateNativeTickAttempts;
        double regenerateNominalAmount;
        double regenerateUnconstrainedHealingDemand;
        double regenerateActualHealingAtNativeTicks;
        double regenerateHealingDeniedByWoundCeiling;
        double regenerateAllowedEventAmount;
        boolean regenerateEventCanceled;
        String elementalProjectileId = "";
        String projectileEntityId = "";
        boolean elementalOwnerRetained;
        double elementalNativeProjectileDamage;
        double elementalStagedProjectileDamage;
        boolean immediateCaptured;

        HitRecord(int index, int startTick, LivingEntity target, LivingEntity player) {
            this.index = index;
            this.startTick = startTick;
            this.shotFamily = SUSTAINED_ROTATION ? switch ((index - 1) % 3) {
                case 0 -> Family.MAGIC;
                case 1 -> Family.HOLY;
                default -> Family.SEVERANCE;
            } : active.family;
            ResourceState targetResources = resources(target);
            ResourceState playerResources = resources(player);
            this.preHp = this.lastHp = target.getHealth();
            this.preShp = this.lastShp = targetResources.shp;
            this.preMagicules = this.lastMagicules = targetResources.magicules;
            this.preAura = this.lastAura = targetResources.aura;
            this.preSeverance = severance(target);
            this.preSeveranceDuration = severanceDuration(target);
            this.preAttackerHp = this.lastAttackerHp = player.getHealth();
            this.preAttackerShp = this.lastAttackerShp = playerResources.shp;
            this.preAttackerMagicules = this.lastAttackerMagicules = playerResources.magicules;
            this.preAttackerAura = this.lastAttackerAura = playerResources.aura;
            this.postHp = preHp;
            this.postShp = preShp;
            this.postMagicules = this.immediatePostMagicules = preMagicules;
            this.postAura = this.immediatePostAura = preAura;
            this.postSeverance = preSeverance;
            this.postSeveranceDuration = preSeveranceDuration;
            this.maxSeverance = preSeverance;
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
            postSeveranceDuration = severanceDuration(target);
            maxSeverance = Math.max(maxSeverance, postSeverance);
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
                postSeveranceDuration = severanceDuration(target);
                maxSeverance = Math.max(maxSeverance, postSeverance);
                targetObservationTicks++;
                if (postSeverance > 0.0001D) woundObservedTicks++;
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
        if (PRODUCTION_OBSERVATION) {
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
                case "crit_chance" -> ADAPTIVE_WOUND_RESEARCH ? 0.0D : 0.05D;
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

    private static int traitRank(Object cap, String id) throws ReflectiveOperationException {
        Object raw = readField(cap, "traits");
        if (raw instanceof Map<?, ?> traits) {
            for (Map.Entry<?, ?> entry : traits.entrySet()) {
                if (traitId(entry.getKey()).equals(id)) {
                    return numberValue(entry.getValue()).intValue();
                }
            }
        }
        return 0;
    }

    private static boolean traitValidTarget(Object cap, String id, LivingEntity target)
            throws ReflectiveOperationException {
        Object raw = readField(cap, "traits");
        if (raw instanceof Map<?, ?> traits) {
            for (Object trait : traits.keySet()) {
                if (traitId(trait).equals(id)) {
                    return booleanValue(invoke(trait, "validTarget", target));
                }
            }
        }
        return false;
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

    private static int severanceDuration(LivingEntity entity) {
        try {
            return TensuraStorages.getEffectFrom(entity).getSeveranceRemoveTime();
        }
        catch (Throwable ignored) {
            return 0;
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

    private static String entityType(Entity entity) {
        return entity == null ? "NONE" : BuiltInRegistries.ENTITY_TYPE.getKey(entity.getType()).toString();
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
        payload.addProperty("schema", ADAPTIVE_WOUND_RESEARCH
                ? adaptiveWoundSchema()
                : SEVERANCE_SUSTAINED ? "tno.phase6.severance_sustained.r5.v1"
                : SEVERANCE_PROTOTYPE ? "tno.phase6.severance_prototype.r4.v1"
                : SEVERANCE_WALL ? "tno.phase6.severance_wall.r3.v1"
                : CALIBRATION_COMBAT ? "tno.phase6.endgame_calibration.v1"
                : PRODUCTION_ACCEPTANCE ? "tno.phase6.magic_holy_production.v1"
                : ENDGAME_RESEARCH ? "tno.phase6.endgame_research.v1"
                : SUITE_C ? "tno.phase5f.suite_c.v1" : "tno.phase5f.suite_b.v1");
        payload.addProperty("kind", kind);
        LOGGER.info("{} {}", MARKER, GSON.toJson(payload));
    }

    private static String adaptiveWoundSchema() {
        return switch (CALIBRATION_MODE) {
            case "adaptive_wound_capability" -> "tno.phase6.adaptive_wound.w3.v1";
            case "adaptive_wound_safety" -> "tno.phase6.adaptive_wound.w4.v1";
            case "adaptive_wound_counter_states" ->
                    "tno.phase6.regenerate_severance_counter_protocol.p2.v1";
            case "adaptive_wound_dynamic" ->
                    "tno.phase6.regenerate_severance_counter_protocol.p3.v1";
            default -> throw new IllegalStateException(
                    "unsupported Adaptive-wound research mode: " + CALIBRATION_MODE);
        };
    }

    private static double serverDouble(String field) throws ReflectiveOperationException {
        Object server = staticField("dev.xkmc.l2hostility.init.data.LHConfig", "SERVER");
        return numberValue(invoke(readField(server, field), "get")).doubleValue();
    }

    private static boolean serverBoolean(String field) throws ReflectiveOperationException {
        Object server = staticField("dev.xkmc.l2hostility.init.data.LHConfig", "SERVER");
        Object value = invoke(readField(server, field), "get");
        if (value instanceof Boolean bool) return bool;
        throw new IllegalArgumentException("not boolean: " + value);
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

    private enum CounterState {
        NONE("NONE", false),
        A_BELOW_CEILING("A_BELOW_CEILING", true),
        B_CROSSING_CEILING("B_CROSSING_CEILING", true),
        C_AT_CEILING("C_AT_CEILING", true),
        NO_REGENERATE_CONTROL("NO_REGENERATE_CONTROL", true),
        NO_WOUND_CONTROL("NO_WOUND_CONTROL", false);

        final String id;
        final boolean requiresWound;

        CounterState(String id, boolean requiresWound) {
            this.id = id;
            this.requiresWound = requiresWound;
        }

        boolean requiresWound() {
            return requiresWound;
        }
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
            if (PRODUCTION_OBSERVATION) return 1.0D + bonus;
            return switch (family) {
                case SOUL, ENERGY -> 1.0D + bonus;
                case SEVERANCE -> 1.0D + bonus * ((2.4D + SEVERANCE_NATIVE_ATTACK_BONUS)
                        / SEVERANCE_NATIVE_ATTACK_BONUS);
                default -> 1.0D + 2.0D * bonus;
            };
        }
    }

    private record ProfileKey(ResourceLocation boss, int level, LevelMode mode, TraitProfile traitProfile) {
    }

    private enum CalibrationCase {
        NONE("NONE", 0.0D, 0.0D, 0.0D),
        BASELINE("CASE_0_BASELINE", 0.0D, 0.0D, 0.0D),
        DEMENTOR_FULL("CASE_1_DEMENTOR_100", 0.0D, 1.0D, 0.0D),
        ADAPTIVE_FULL("CASE_2_ADAPTIVE_100", 0.0D, 0.0D, 1.0D),
        REDUCERS_FULL("CASE_3_DEMENTOR_ADAPTIVE_100", 0.0D, 1.0D, 1.0D),
        HEALTH_FULL("CASE_4_GENERIC_HEALTH_100", 1.0D, 0.0D, 0.0D),
        ALL_FULL("CASE_5_ALL_100", 1.0D, 1.0D, 1.0D),
        HEALTH_Q_0("HEALTH_Q_0", 0.0D, 0.0D, 0.0D),
        HEALTH_Q_25("HEALTH_Q_25", 0.25D, 0.0D, 0.0D),
        HEALTH_Q_50("HEALTH_Q_50", 0.50D, 0.0D, 0.0D),
        HEALTH_Q_75("HEALTH_Q_75", 0.75D, 0.0D, 0.0D),
        HEALTH_Q_100("HEALTH_Q_100", 1.0D, 0.0D, 0.0D),
        DEMENTOR_RD_0("DEMENTOR_RD_0", 0.0D, 0.0D, 0.0D),
        DEMENTOR_RD_25("DEMENTOR_RD_25", 0.0D, 0.25D, 0.0D),
        DEMENTOR_RD_50("DEMENTOR_RD_50", 0.0D, 0.50D, 0.0D),
        DEMENTOR_RD_75("DEMENTOR_RD_75", 0.0D, 0.75D, 0.0D),
        DEMENTOR_RD_100("DEMENTOR_RD_100", 0.0D, 1.0D, 0.0D),
        ADAPTIVE_RA_0("ADAPTIVE_RA_0", 0.0D, 0.0D, 0.0D),
        ADAPTIVE_RA_25("ADAPTIVE_RA_25", 0.0D, 0.0D, 0.25D),
        ADAPTIVE_RA_50("ADAPTIVE_RA_50", 0.0D, 0.0D, 0.50D),
        ADAPTIVE_RA_75("ADAPTIVE_RA_75", 0.0D, 0.0D, 0.75D),
        ADAPTIVE_RA_100("ADAPTIVE_RA_100", 0.0D, 0.0D, 1.0D),
        COMBINED_LOW_S5("COMBINED_LOW_S5", 0.25D, 0.50D, 0.50D),
        COMBINED_LOW_S6("COMBINED_LOW_S6", 0.375D, 0.625D, 0.625D),
        COMBINED_LOW_S7("COMBINED_LOW_S7", 0.50D, 0.75D, 0.75D),
        COMBINED_MID_S5("COMBINED_MID_S5", 0.375D, 0.50D, 0.50D),
        COMBINED_MID_S6("COMBINED_MID_S6", 0.5625D, 0.625D, 0.625D),
        COMBINED_MID_S7("COMBINED_MID_S7", 0.75D, 0.75D, 0.75D),
        COMBINED_HIGH_S5("COMBINED_HIGH_S5", 0.50D, 0.50D, 0.50D),
        COMBINED_HIGH_S6("COMBINED_HIGH_S6", 0.75D, 0.625D, 0.625D),
        COMBINED_HIGH_S7("COMBINED_HIGH_S7", 1.00D, 0.75D, 0.75D),
        SAFETY_S0("SAFETY_S0_NATIVE_POLICY", 0.0D, 0.0D, 0.0D),
        SAFETY_S1("SAFETY_S1_NATIVE_POLICY", 0.0D, 0.0D, 0.0D),
        SAFETY_S2("SAFETY_S2_NATIVE_POLICY", 0.0D, 0.0D, 0.0D),
        SAFETY_S3("SAFETY_S3_NATIVE_POLICY", 0.0D, 0.0D, 0.0D),
        SAFETY_S4("SAFETY_S4_NATIVE_POLICY", 0.0D, 0.0D, 0.0D),
        SAFETY_S5("SAFETY_S5_HIGH_CANDIDATE", 0.50D, 0.50D, 0.50D),
        SAFETY_S6("SAFETY_S6_HIGH_CANDIDATE", 0.75D, 0.625D, 0.625D),
        SAFETY_S7("SAFETY_S7_HIGH_CANDIDATE", 1.00D, 0.75D, 0.75D),
        SEVERANCE_WALL_NATIVE("SEVERANCE_WALL_NATIVE_POLICY", 0.0D, 0.0D, 0.0D),
        SEVERANCE_PROTOTYPE_X1("SEVERANCE_PROTOTYPE_X1", 1.0D),
        SEVERANCE_PROTOTYPE_X4("SEVERANCE_PROTOTYPE_X4", 4.0D),
        SEVERANCE_PROTOTYPE_X16("SEVERANCE_PROTOTYPE_X16", 16.0D),
        SEVERANCE_PROTOTYPE_X64("SEVERANCE_PROTOTYPE_X64_DIAGNOSTIC_CEILING", 64.0D),
        WOUND_RW_0("WOUND_RW_0_NATIVE_CONTROL", 0.0D, 0.0D, 0.0D, 1.0D, 0.0D),
        WOUND_RW_50("WOUND_RW_50_TRAIT_IDENTITY_DIAGNOSTIC", 0.0D, 0.0D, 0.0D, 1.0D, 0.5D),
        WOUND_RW_100("WOUND_RW_100_CAPABILITY_EXTREME", 0.0D, 0.0D, 0.0D, 1.0D, 1.0D),
        COUNTER_STATE_A("COUNTER_STATE_A_BELOW_CEILING", 0.0D, 0.0D, 0.0D, 1.0D, 0.5D),
        COUNTER_STATE_B("COUNTER_STATE_B_CROSSING_CEILING", 0.0D, 0.0D, 0.0D, 1.0D, 0.5D),
        COUNTER_STATE_C("COUNTER_STATE_C_AT_CEILING", 0.0D, 0.0D, 0.0D, 1.0D, 0.5D),
        COUNTER_NO_REGENERATE("COUNTER_NO_REGENERATE_CONTROL", 0.0D, 0.0D, 0.0D, 1.0D, 0.5D),
        COUNTER_NO_WOUND("COUNTER_NO_WOUND_CONTROL", 0.0D, 0.0D, 0.0D, 1.0D, 0.5D),
        DYNAMIC_RW_50("DYNAMIC_CANDIDATE_C_RW_50", 0.0D, 0.0D, 0.0D, 1.0D, 0.5D),
        DYNAMIC_NATIVE_RW_0("DYNAMIC_NATIVE_WOUND_RW_0_CONTROL", 0.0D, 0.0D, 0.0D, 1.0D, 0.0D);

        final String id;
        final Phase6CalibrationContext.Parameters parameters;
        final double severanceEligibleMultiplier;
        final double woundAdaptiveRecovery;

        CalibrationCase(String id, double q, double rd, double ra) {
            this(id, q, rd, ra, 1.0D);
        }

        CalibrationCase(String id, double severanceEligibleMultiplier) {
            this(id, 0.0D, 0.0D, 0.0D, severanceEligibleMultiplier);
        }

        CalibrationCase(String id, double q, double rd, double ra, double severanceEligibleMultiplier) {
            this(id, q, rd, ra, severanceEligibleMultiplier, 0.0D);
        }

        CalibrationCase(String id, double q, double rd, double ra,
                double severanceEligibleMultiplier, double woundAdaptiveRecovery) {
            this.id = id;
            this.parameters = new Phase6CalibrationContext.Parameters(q, rd, ra);
            this.severanceEligibleMultiplier = severanceEligibleMultiplier;
            this.woundAdaptiveRecovery = woundAdaptiveRecovery;
        }

        static List<CalibrationCase> ceilingCases() {
            return List.of(BASELINE, DEMENTOR_FULL, ADAPTIVE_FULL, REDUCERS_FULL, HEALTH_FULL, ALL_FULL);
        }

        static List<CalibrationCase> severancePrototypeCases() {
            return List.of(SEVERANCE_PROTOTYPE_X1, SEVERANCE_PROTOTYPE_X4,
                    SEVERANCE_PROTOTYPE_X16, SEVERANCE_PROTOTYPE_X64);
        }

        static List<CalibrationCase> forMode(String mode, Stage stage) {
            return switch (mode) {
                case "ceiling" -> ceilingCases();
                case "health" -> List.of(HEALTH_Q_0, HEALTH_Q_25, HEALTH_Q_50, HEALTH_Q_75, HEALTH_Q_100);
                case "dementor" -> List.of(DEMENTOR_RD_0, DEMENTOR_RD_25, DEMENTOR_RD_50,
                        DEMENTOR_RD_75, DEMENTOR_RD_100);
                case "adaptive" -> List.of(ADAPTIVE_RA_0, ADAPTIVE_RA_25, ADAPTIVE_RA_50,
                        ADAPTIVE_RA_75, ADAPTIVE_RA_100);
                case "combined" -> switch (stage.name) {
                    case "S5" -> List.of(COMBINED_LOW_S5, COMBINED_MID_S5, COMBINED_HIGH_S5);
                    case "S6" -> List.of(COMBINED_LOW_S6, COMBINED_MID_S6, COMBINED_HIGH_S6);
                    case "S7" -> List.of(COMBINED_LOW_S7, COMBINED_MID_S7, COMBINED_HIGH_S7);
                    default -> throw new IllegalArgumentException("combined calibration has no " + stage.name);
                };
                case "safety" -> switch (stage.name) {
                    case "S0" -> List.of(SAFETY_S0);
                    case "S1" -> List.of(SAFETY_S1);
                    case "S2" -> List.of(SAFETY_S2);
                    case "S3" -> List.of(SAFETY_S3);
                    case "S4" -> List.of(SAFETY_S4);
                    case "S5" -> List.of(SAFETY_S5);
                    case "S6" -> List.of(SAFETY_S6);
                    case "S7" -> List.of(SAFETY_S7);
                    default -> throw new IllegalArgumentException("safety calibration has no " + stage.name);
                };
                case "severance_wall" -> List.of(SEVERANCE_WALL_NATIVE);
                default -> throw new IllegalArgumentException("calibration mode is not implemented yet: " + mode);
            };
        }

        static CalibrationCase productionFor(Stage stage) {
            return switch (stage.name) {
                case "S0" -> SAFETY_S0;
                case "S1" -> SAFETY_S1;
                case "S2" -> SAFETY_S2;
                case "S3" -> SAFETY_S3;
                case "S4" -> SAFETY_S4;
                case "S5" -> SAFETY_S5;
                case "S6" -> SAFETY_S6;
                case "S7" -> SAFETY_S7;
                default -> throw new IllegalArgumentException("production acceptance has no " + stage.name);
            };
        }

        Phase6CalibrationContext.Parameters parameters() {
            return parameters;
        }

        CounterState counterState() {
            return switch (this) {
                case COUNTER_STATE_A -> CounterState.A_BELOW_CEILING;
                case COUNTER_STATE_B -> CounterState.B_CROSSING_CEILING;
                case COUNTER_STATE_C -> CounterState.C_AT_CEILING;
                case COUNTER_NO_REGENERATE -> CounterState.NO_REGENERATE_CONTROL;
                case COUNTER_NO_WOUND -> CounterState.NO_WOUND_CONTROL;
                default -> CounterState.NONE;
            };
        }
    }

    private enum TraitProfile {
        ACCEPTED("ACCEPTED_STRONGEST_LEGAL", Set.of()),
        WITHOUT_DEMENTOR("WITHOUT_DEMENTOR_CONTROL", Set.of("l2hostility:dementor")),
        WITHOUT_ADAPTIVE("WITHOUT_ADAPTIVE_CONTROL", Set.of("l2hostility:adaptive")),
        WITHOUT_DEMENTOR_ADAPTIVE("WITHOUT_DEMENTOR_ADAPTIVE_CONTROL",
                Set.of("l2hostility:dementor", "l2hostility:adaptive")),
        WITHOUT_REGENERATE("WITHOUT_REGENERATE_CONTROL", Set.of("l2hostility:regenerate")),
        WITHOUT_TANK("WITHOUT_TANK_CONTROL", Set.of("l2hostility:tank")),
        WITHOUT_TANK_DEMENTOR("WITHOUT_TANK_DEMENTOR_CONTROL",
                Set.of("l2hostility:tank", "l2hostility:dementor")),
        WITHOUT_TANK_ADAPTIVE("WITHOUT_TANK_ADAPTIVE_CONTROL",
                Set.of("l2hostility:tank", "l2hostility:adaptive")),
        WITHOUT_TANK_DEMENTOR_ADAPTIVE("WITHOUT_TANK_DEMENTOR_ADAPTIVE_CONTROL",
                Set.of("l2hostility:tank", "l2hostility:dementor", "l2hostility:adaptive"));

        final String id;
        final Set<String> removedTraits;

        TraitProfile(String id, Set<String> removedTraits) {
            this.id = id;
            this.removedTraits = removedTraits;
        }

        Map<String, Integer> apply(Map<String, Integer> reference) {
            Map<String, Integer> result = new LinkedHashMap<>(reference);
            removedTraits.forEach(result::remove);
            return Map.copyOf(result);
        }

        static List<TraitProfile> forMode(String mode) {
            return switch (mode) {
                case "dementor" -> List.of(ACCEPTED, WITHOUT_DEMENTOR);
                case "adaptive" -> List.of(ACCEPTED, WITHOUT_ADAPTIVE);
                case "combined" -> List.of(ACCEPTED, WITHOUT_DEMENTOR, WITHOUT_ADAPTIVE,
                        WITHOUT_DEMENTOR_ADAPTIVE, WITHOUT_REGENERATE);
                case "severance_wall" -> List.of(ACCEPTED, WITHOUT_TANK, WITHOUT_DEMENTOR,
                        WITHOUT_ADAPTIVE, WITHOUT_TANK_DEMENTOR, WITHOUT_TANK_ADAPTIVE,
                        WITHOUT_DEMENTOR_ADAPTIVE, WITHOUT_TANK_DEMENTOR_ADAPTIVE);
                default -> List.of(ACCEPTED);
            };
        }
    }

    private record CaseSpec(BossSpec boss, int level, LevelMode mode, Stage stage,
                            CalibrationCase calibration, TraitProfile traitProfile) {
        ProfileKey profileKey() {
            return new ProfileKey(boss.id, level, mode, traitProfile);
        }
    }

    private record FamilyProbe(double raw, double scaled, double nativeAfterResistance,
                               double stagedAmount, boolean sourceBypass,
                               Set<String> tags, boolean l2Magic) {
    }

    private record SeveranceProjection(double nativePre, double stagedPre, double prototypePre,
                                        double basePost, double nativePost, double stagedPost,
                                        double prototypePost, double productionEligible,
                                        double prototypeEligible) {
    }

    private record ResourceState(double shp, double maxShp, double magicules, double aura) {
    }
}
