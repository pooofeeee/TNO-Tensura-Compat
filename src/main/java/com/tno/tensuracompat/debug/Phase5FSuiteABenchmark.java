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
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
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
import net.minecraft.world.item.BowItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import net.neoforged.fml.ModList;
import net.neoforged.fml.loading.FMLEnvironment;
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
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Comparator;
import java.util.IdentityHashMap;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;

/**
 * Development-only, opt-in Suite A runner for the locked Apotheosis profile.
 * Third-party APIs remain reflective so this class is inert and load-safe when
 * the optional benchmark stack is absent.
 */
public final class Phase5FSuiteABenchmark {
    private static final Logger LOGGER = LogUtils.getLogger();
    private static final Gson GSON = new GsonBuilder().disableHtmlEscaping().create();
    private static final String MARKER = "TNO_PHASE5F_SUITE_A";
    private static final String TARGET_TAG = "tno_phase5f_suite_a_target";
    private static final String SCALE_TAG = "l2_tensura_scaled";
    private static final String APO_PROFILE = "ANCIENT_SINGLE_PROSPEROUS_SPECTRAL";
    private static final String L2_MISCS = "dev.xkmc.l2hostility.init.registrate.LHMiscs";
    private static final int MAX_SHOTS = Integer.getInteger("tno.phase5f.suiteAShots", 10);
    private static final int WINDOW_TICKS = Integer.getInteger("tno.phase5f.suiteATicks", 200);
    private static final double TEST_X = 0.5D;
    private static final double TEST_Y = 240.0D;
    private static final double TARGET_Z = 20.5D;

    private static final List<ResourceLocation> OBSERVED_ATTRIBUTES = List.of(
            id("apothic_attributes", "arrow_damage"),
            id("apothic_attributes", "arrow_velocity"),
            id("apothic_attributes", "armor_pierce"),
            id("apothic_attributes", "armor_shred"),
            id("apothic_attributes", "prot_pierce"),
            id("apothic_attributes", "prot_shred"),
            id("apothic_attributes", "crit_chance"),
            id("apothic_attributes", "crit_damage"),
            id("apothic_attributes", "draw_speed"),
            id("manascore_attribute", "critical_attack_chance"),
            id("tensura", "warp_shot")
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

    private static final Set<String> DEFENSIVE_TRAITS = Set.of(
            "l2hostility:adaptive", "l2hostility:arena", "l2hostility:dementor",
            "l2hostility:dispell", "l2hostility:protection", "l2hostility:regenerate",
            "l2hostility:reflect", "l2hostility:repelling", "l2hostility:tank",
            "l2hostility:undying"
    );

    private static Session active;

    private Phase5FSuiteABenchmark() {
    }

    public static void onServerStarted(ServerStartedEvent event) {
        if (FMLEnvironment.production || !Boolean.getBoolean("tno.phase5f.suiteA") || active != null) return;
        try {
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

    public static void onIncomingBeforeCrit(LivingIncomingDamageEvent event) {
        Session session = active;
        if (session != null) session.captureBeforeCrit(event);
    }

    public static void onIncomingAfterCrit(LivingIncomingDamageEvent event) {
        Session session = active;
        if (session != null) session.captureAfterCrit(event);
    }

    public static void onIncomingDamage(LivingIncomingDamageEvent event) {
        Session session = active;
        if (session != null) session.captureIncoming(event);
    }

    public static void onDamagePost(LivingDamageEvent.Post event) {
        Session session = active;
        if (session != null) session.capturePost(event);
    }

    private static void requireMods() {
        for (String mod : List.of("royalvariations", "apotheosis", "apothic_attributes",
                "ancientreforging", "apothicnightmares", "l2hostility")) {
            if (!ModList.get().isLoaded(mod)) throw new IllegalStateException("required Suite A mod absent: " + mod);
        }
    }

    private static final class Session {
        private final MinecraftServer server;
        private final ServerLevel level;
        private final ItemStack officialBow;
        private final List<CaseSpec> cases;
        private final List<JsonObject> summaries = new ArrayList<>();
        private final Map<LivingIncomingDamageEvent, Float> beforeCrit = new IdentityHashMap<>();
        private FakePlayer player;
        private LivingEntity target;
        private Object l2Cap;
        private CaseResult result;
        private HitRecord currentHit;
        private Phase phase = Phase.SPAWN;
        private int caseIndex;
        private int phaseTick;
        private int shotsReleased;
        private int drawTicks;
        private long runStartTick;
        private long nextShotTick;
        private boolean complete;

        Session(MinecraftServer server) throws ReflectiveOperationException {
            this.server = server;
            this.level = server.overworld();
            this.officialBow = Phase5FApotheosisBenchmark.buildOfficialWinner(server);
            this.cases = buildCases(System.getProperty("tno.phase5f.suiteABoss", ""));
            if (cases.isEmpty()) throw new IllegalStateException("Suite A boss filter matched no targets");
            cleanupTestArea();
            logCatalog();
        }

        void tick() throws ReflectiveOperationException {
            stabilize();
            if (phase == Phase.RUN) observeCurrentHit();
            switch (phase) {
                case SPAWN -> spawnCase();
                case WAIT_ATTACHMENT -> waitForAttachment();
                case CONFIGURE_LEVEL -> configureLevel();
                case WAIT_SCALING -> waitForScaling();
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
            CaseSpec spec = cases.get(caseIndex);
            player = createPlayer(caseIndex);
            equipOfficialBow();
            Entity created = BuiltInRegistries.ENTITY_TYPE.get(spec.boss.id).create(level);
            if (!(created instanceof LivingEntity living)) {
                throw new IllegalStateException("could not create living target " + spec.boss.id);
            }
            target = living;
            target.setPos(TEST_X, TEST_Y, TARGET_Z);
            target.setNoGravity(true);
            target.setSilent(true);
            target.addTag(TARGET_TAG);
            level.addFreshEntity(target);
            phaseTick = 0;
            phase = Phase.WAIT_ATTACHMENT;
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
                if (spec.mode == LevelMode.STRESS && spec.level > originalMax) {
                    maxLevel.setInt(config, spec.level);
                }
                // Native L2 reroll with normal suppression, costs, exclusions and rank caps.
                invoke(l2Cap, "reinit", target, spec.level, false);
            }
            finally {
                maxLevel.setInt(config, originalMax);
            }
            int actual = numberValue(invoke(l2Cap, "getLevel")).intValue();
            if (actual != spec.level) {
                throw new IllegalStateException("stored level " + actual + " != requested " + spec.level);
            }
            if (!booleanValue(invoke(l2Cap, "isInitialized"))) {
                throw new IllegalStateException("native L2 reinit did not initialize the attachment");
            }
            invoke(l2Cap, "syncToClient", target);
            removeDatapackScaling();
            phaseTick = 0;
            phase = Phase.WAIT_SCALING;
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
            if (numberValue(invoke(l2Cap, "getLevel")).intValue() != currentCase().level) {
                throw new IllegalStateException("stored L2 level changed after datapack scaling");
            }

            fillResources(target);
            fillResources(player);
            target.setHealth(target.getMaxHealth());
            target.setAbsorptionAmount(0.0F);
            target.invulnerableTime = 0;
            player.setHealth(player.getMaxHealth());
            player.setAbsorptionAmount(0.0F);
            player.invulnerableTime = 0;
            beforeCrit.clear();
            clearArrows();

            drawTicks = fullDrawTicks(player);
            result = new CaseResult(currentCase(), target, player, l2Cap, readAttributes(player), drawTicks);
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
            if (currentHit != null && now >= nextShotTick && shotsReleased < MAX_SHOTS) {
                closeCurrentHit(elapsed);
            }

            boolean targetDead = target == null || target.isRemoved() || target.isDeadOrDying() || target.getHealth() <= 0.0F;
            boolean playerDead = player == null || player.isRemoved() || player.isDeadOrDying() || player.getHealth() <= 0.0F;
            if (targetDead || playerDead || elapsed >= WINDOW_TICKS) {
                if (currentHit != null) closeCurrentHit(elapsed);
                if (targetDead && result.ttk == null) {
                    result.ttk = elapsed;
                    result.htk = shotsReleased;
                }
                if (playerDead) result.attackerDefeated = true;
                result.elapsedTicks = Math.max(1, elapsed);
                phase = Phase.FINISH;
                return;
            }

            if (now >= nextShotTick && shotsReleased < MAX_SHOTS) {
                clearArrows();
                currentHit = new HitRecord(shotsReleased + 1, elapsed, target, player);
                fireFullDraw();
                shotsReleased++;
                nextShotTick = now + drawTicks;
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
            result.finish(target, player);
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

        private void captureBeforeCrit(LivingIncomingDamageEvent event) {
            if (phase != Phase.RUN || currentHit == null || event.getEntity() != target || !isBenchmarkArrow(event)) return;
            currentHit.preCritDamage += event.getAmount();
            beforeCrit.put(event, event.getAmount());
        }

        private void captureAfterCrit(LivingIncomingDamageEvent event) {
            Float before = beforeCrit.get(event);
            if (before != null && currentHit != null && event.getAmount() > before + 0.001F) {
                currentHit.crit = true;
                currentHit.critMultiplierEvents++;
            }
        }

        private void captureIncoming(LivingIncomingDamageEvent event) {
            if (phase != Phase.RUN || currentHit == null) return;
            if (event.getEntity() == target) {
                String type = damageType(event);
                if (isBenchmarkArrow(event)) {
                    Float before = beforeCrit.get(event);
                    if (before != null && event.getAmount() > before + 0.001F) {
                        currentHit.crit = true;
                        currentHit.critMultiplierEvents++;
                    }
                    currentHit.directIncoming += event.getAmount();
                    currentHit.directOriginal += event.getOriginalAmount();
                    currentHit.directDamageTypes.add(type);
                }
                else {
                    currentHit.dotIncoming += event.getAmount();
                    currentHit.dotDamageTypes.add(type);
                }
            }
            else if (event.getEntity() == player) {
                currentHit.reflectedIncoming += event.getAmount();
                currentHit.reflectedDamageTypes.add(damageType(event));
            }
            beforeCrit.remove(event);
        }

        private void capturePost(LivingDamageEvent.Post event) {
            if (phase != Phase.RUN || currentHit == null) return;
            if (event.getEntity() == target) {
                if (isBenchmarkArrow(event)) currentHit.directPost += event.getNewDamage();
                else currentHit.dotPost += event.getNewDamage();
            }
            else if (event.getEntity() == player) {
                currentHit.reflectedPost += event.getNewDamage();
            }
        }

        private boolean isBenchmarkArrow(LivingIncomingDamageEvent event) {
            return event.getSource().getDirectEntity() instanceof AbstractArrow arrow
                    && fromBenchmarkPlayer(arrow.getOwner());
        }

        private boolean isBenchmarkArrow(LivingDamageEvent.Post event) {
            return event.getSource().getDirectEntity() instanceof AbstractArrow arrow
                    && fromBenchmarkPlayer(arrow.getOwner());
        }

        private boolean fromBenchmarkPlayer(Entity owner) {
            return player != null && (owner == player
                    || owner != null && owner.getUUID().equals(player.getUUID()));
        }

        private void fireFullDraw() {
            player.setItemInHand(InteractionHand.OFF_HAND, new ItemStack(Items.ARROW, 64));
            List<UUID> existing = level.getEntitiesOfClass(AbstractArrow.class,
                    player.getBoundingBox().inflate(64.0D), arrow -> fromBenchmarkPlayer(arrow.getOwner()))
                    .stream().map(Entity::getUUID).toList();
            ItemStack bow = player.getMainHandItem();
            int remaining = bow.getUseDuration(player) - drawTicks;
            bow.releaseUsing(level, player, remaining);
            List<AbstractArrow> spawned = level.getEntitiesOfClass(AbstractArrow.class,
                    player.getBoundingBox().inflate(64.0D),
                    arrow -> fromBenchmarkPlayer(arrow.getOwner()) && !existing.contains(arrow.getUUID()));
            if (spawned.isEmpty()) throw new IllegalStateException("full-draw release created no arrow");
            Vec3 aim = target.getBoundingBox().getCenter();
            for (AbstractArrow arrow : spawned) {
                double speed = arrow.getDeltaMovement().length();
                arrow.setDeltaMovement(aim.subtract(arrow.position()).normalize().scale(speed));
                arrow.hasImpulse = true;
            }
        }

        private FakePlayer createPlayer(int index) {
            String key = "tno-phase5f-suite-a-" + currentCase().boss.id + "-" + index;
            UUID uuid = UUID.nameUUIDFromBytes(key.getBytes(StandardCharsets.UTF_8));
            FakePlayer fake = FakePlayerFactory.get(level, new GameProfile(uuid, "TNO_P5FA_" + index));
            fake.getInventory().clearContent();
            fake.getAbilities().instabuild = true;
            fake.getAbilities().invulnerable = false;
            setBase(fake, Attributes.MAX_HEALTH, 1024.0D);
            setBase(fake, TensuraAttributes.MAX_SPIRITUAL_HEALTH, 1_000_000_000.0D);
            fake.setHealth(fake.getMaxHealth());
            fake.setPos(TEST_X, TEST_Y, 0.5D);
            return fake;
        }

        private void equipOfficialBow() {
            player.setItemInHand(InteractionHand.MAIN_HAND, officialBow.copy());
            player.setItemInHand(InteractionHand.OFF_HAND, new ItemStack(Items.ARROW, 64));
            player.setItemSlot(EquipmentSlot.MAINHAND, player.getMainHandItem());
            try {
                invoke(player, "detectEquipmentUpdates");
            }
            catch (ReflectiveOperationException exception) {
                throw new IllegalStateException("could not refresh fake-player attributes", exception);
            }
        }

        private void stabilize() {
            if (player != null) {
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
                if (target instanceof Mob mob) {
                    mob.setTarget(null);
                    mob.getNavigation().stop();
                    mob.setAggressive(false);
                }
            }
        }

        private void observeCurrentHit() {
            if (currentHit != null) currentHit.observe(target, player);
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
            level.getEntitiesOfClass(AbstractArrow.class, player.getBoundingBox().inflate(64.0D),
                    arrow -> fromBenchmarkPlayer(arrow.getOwner())).forEach(Entity::discard);
        }

        private void cleanupCase() {
            beforeCrit.clear();
            currentHit = null;
            clearArrows();
            if (target != null) target.discard();
            if (player != null) {
                player.setItemInHand(InteractionHand.MAIN_HAND, ItemStack.EMPTY);
                player.setItemInHand(InteractionHand.OFF_HAND, ItemStack.EMPTY);
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
            }
            return json;
        }

        private void logCatalog() {
            JsonObject json = new JsonObject();
            json.addProperty("suite", "A_APOTHEOSIS_ONLY");
            json.addProperty("APO_profile", APO_PROFILE);
            json.addProperty("TNO_family", "NONE");
            json.addProperty("TNO_stage", "Native");
            json.addProperty("shots_per_case", MAX_SHOTS);
            json.addProperty("fixed_window_ticks", WINDOW_TICKS);
            json.addProperty("distance", TARGET_Z - 0.5D);
            json.addProperty("arrow", "minecraft:arrow");
            json.addProperty("draw", "full");
            json.addProperty("natural_representative_policy", "floor((configured_min + configured_max) / 2)");
            json.addProperty("stress_method", "temporarily lift only the in-memory entity config ceiling during native L2 reinit; restore immediately");
            json.addProperty("datapack_mutated", false);
            json.addProperty("balance_mutated", false);
            JsonArray planned = new JsonArray();
            for (CaseSpec spec : cases) {
                JsonObject entry = new JsonObject();
                entry.addProperty("boss", spec.boss.id.toString());
                entry.addProperty("level", spec.level);
                entry.addProperty("level_mode", spec.mode.name());
                entry.addProperty("legal_level_profile", spec.mode != LevelMode.STRESS);
                planned.add(entry);
            }
            json.add("cases", planned);
            json.add("bow_attributes", readStackAttributes(officialBow));
            log("catalog", json);
        }
    }

    private static List<CaseSpec> buildCases(String filter) {
        List<CaseSpec> result = new ArrayList<>();
        for (BossSpec boss : BOSSES) {
            if (!filter.isBlank() && !boss.id.toString().equals(filter)) continue;
            int representative = (boss.minLevel + boss.maxLevel) / 2;
            result.add(new CaseSpec(boss, representative, LevelMode.NATURAL_REPRESENTATIVE));
            if (representative != boss.maxLevel) {
                result.add(new CaseSpec(boss, boss.maxLevel, LevelMode.NATURAL_MAXIMUM));
            }
            for (int stress : List.of(300, 600, 800, 1000)) {
                // Luminous's natural maximum is already the exact Lv300 checkpoint.
                if (stress == boss.maxLevel) continue;
                result.add(new CaseSpec(boss, stress, LevelMode.STRESS));
            }
        }
        return result;
    }

    private static final class CaseResult {
        final CaseSpec spec;
        final JsonArray traits;
        final JsonObject traitRanks;
        final JsonObject bowAttributes;
        final List<HitRecord> hits = new ArrayList<>();
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
        final boolean scalingMarker;
        final int drawTicks;
        int shotsReleased;
        int elapsedTicks;
        Integer ttk;
        Integer htk;
        boolean attackerDefeated;
        double finalHp;
        double finalShp;
        double finalMagicules;
        double finalAura;
        double finalMaxHp;
        double finalArmor;
        double finalToughness;

        CaseResult(CaseSpec spec, LivingEntity target, LivingEntity player, Object cap,
                JsonObject bowAttributes, int drawTicks) throws ReflectiveOperationException {
            this.spec = spec;
            this.bowAttributes = bowAttributes;
            this.drawTicks = drawTicks;
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
            this.scalingMarker = target.getTags().contains(SCALE_TAG);

            this.traits = new JsonArray();
            this.traitRanks = new JsonObject();
            Object value = readField(cap, "traits");
            if (value instanceof Map<?, ?> map) {
                map.entrySet().stream().sorted(Comparator.comparing(entry -> traitId(entry.getKey())))
                        .forEach(entry -> {
                            String id = traitId(entry.getKey());
                            int rank = numberValue(entry.getValue()).intValue();
                            JsonObject trait = new JsonObject();
                            trait.addProperty("id", id);
                            trait.addProperty("rank", rank);
                            traits.add(trait);
                            traitRanks.addProperty(id, rank);
                        });
            }
        }

        void finish(LivingEntity target, LivingEntity player) {
            if (target != null) {
                ResourceState state = resources(target);
                finalHp = target.getHealth();
                finalMaxHp = target.getMaxHealth();
                finalShp = state.shp;
                finalMagicules = state.magicules;
                finalAura = state.aura;
                finalArmor = target.getArmorValue();
                finalToughness = target.getAttributeValue(Attributes.ARMOR_TOUGHNESS);
            }
        }

        JsonObject caseJson() {
            JsonObject json = commonJson();
            json.addProperty("status", "running");
            return json;
        }

        JsonObject rowJson(HitRecord hit) {
            JsonObject json = commonJson();
            json.addProperty("hit_index", hit.index);
            json.addProperty("crit", hit.crit);
            json.addProperty("pre_HP", hit.preHp);
            json.addProperty("post_HP", hit.postHp);
            json.addProperty("pre_SHP", hit.preShp);
            json.addProperty("post_SHP", hit.postShp);
            json.addProperty("direct_damage", hit.directPost);
            json.addProperty("critical_damage", hit.crit ? hit.directPost : 0.0D);
            json.addProperty("pre_crit_damage", hit.preCritDamage);
            json.addProperty("incoming_after_crit_damage", hit.directIncoming);
            json.addProperty("DoT_damage", hit.dotPost);
            json.addProperty("regen", hit.targetHpRegen + hit.targetShpRegen);
            json.addProperty("HP_regen", hit.targetHpRegen);
            json.addProperty("SHP_regen", hit.targetShpRegen);
            json.addProperty("reflected_damage", hit.reflectedPost);
            json.addProperty("elapsed_ticks", hit.elapsedTicks);
            if (htk == null) json.add("HTK", null);
            else json.addProperty("HTK", htk);
            if (ttk == null) json.add("TTK", null);
            else json.addProperty("TTK", ttk);
            json.addProperty("DPS", dps());
            json.addProperty("blocked", hit.directIncoming == 0.0D && hit.directPost == 0.0D);
            json.addProperty("transformed", hit.transformed());
            json.add("direct_damage_types", strings(hit.directDamageTypes));
            json.add("DoT_damage_types", strings(hit.dotDamageTypes));
            json.add("reflected_damage_types", strings(hit.reflectedDamageTypes));
            json.addProperty("notes", interactionNotes(hit));
            return json;
        }

        JsonObject summaryJson() {
            JsonObject json = commonJson();
            json.addProperty("status", "ok");
            json.addProperty("shots_released", shotsReleased);
            json.addProperty("hits_recorded", hits.size());
            json.addProperty("critical_hits", hits.stream().filter(hit -> hit.crit).count());
            json.addProperty("blocked_hits", hits.stream()
                    .filter(hit -> hit.directIncoming == 0.0D && hit.directPost == 0.0D).count());
            json.addProperty("direct_damage", sumDirect());
            json.addProperty("DoT_damage", sumDot());
            json.addProperty("regen", hits.stream().mapToDouble(hit -> hit.targetHpRegen + hit.targetShpRegen).sum());
            json.addProperty("reflected_damage", hits.stream().mapToDouble(hit -> hit.reflectedPost).sum());
            json.addProperty("elapsed_ticks", elapsedTicks);
            json.addProperty("DPS", dps());
            if (htk == null) json.add("HTK", null);
            else json.addProperty("HTK", htk);
            if (ttk == null) json.add("TTK", null);
            else json.addProperty("TTK", ttk);
            json.addProperty("attacker_defeated", attackerDefeated);
            json.addProperty("final_HP", finalHp);
            json.addProperty("final_Max_HP", finalMaxHp);
            json.addProperty("final_SHP", finalShp);
            json.addProperty("final_Magicules", finalMagicules);
            json.addProperty("final_Aura", finalAura);
            json.addProperty("final_armor", finalArmor);
            json.addProperty("final_toughness", finalToughness);
            json.addProperty("notes", interactionNotes(null));
            return json;
        }

        private JsonObject commonJson() {
            JsonObject json = new JsonObject();
            json.addProperty("suite", "A_APOTHEOSIS_ONLY");
            json.addProperty("boss", spec.boss.id.toString());
            json.addProperty("boss_priority", spec.boss.primary ? "PRIMARY" : "SECONDARY");
            json.addProperty("level", spec.level);
            json.addProperty("level_mode", spec.mode.name());
            json.addProperty("l2_initialized", true);
            json.addProperty("configured_min_level", spec.boss.minLevel);
            json.addProperty("configured_max_level", spec.boss.maxLevel);
            json.add("traits", traits.deepCopy());
            json.add("trait_ranks", traitRanks.deepCopy());
            json.addProperty("legal_profile", spec.mode != LevelMode.STRESS);
            json.addProperty("apo_profile_legal", true);
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
            json.addProperty("tensura_l2h_scaling_marker", scalingMarker);
            json.addProperty("TNO_family", "NONE");
            json.addProperty("TNO_stage", "Native");
            json.addProperty("APO_profile", APO_PROFILE);
            json.add("Bow_attributes", bowAttributes.deepCopy());
            json.addProperty("full_draw_ticks", drawTicks);
            return json;
        }

        private double sumDirect() {
            return hits.stream().mapToDouble(hit -> hit.directPost).sum();
        }

        private double sumDot() {
            return hits.stream().mapToDouble(hit -> hit.dotPost).sum();
        }

        private double dps() {
            return elapsedTicks <= 0 ? 0.0D : (sumDirect() + sumDot()) / (elapsedTicks / 20.0D);
        }

        private String interactionNotes(HitRecord hit) {
            List<String> notes = new ArrayList<>();
            traitRanks.keySet().stream().filter(DEFENSIVE_TRAITS::contains)
                    .forEach(id -> notes.add(id + " rank " + traitRanks.get(id).getAsInt()));
            if (hit != null && hit.directIncoming == 0.0D && hit.directPost == 0.0D) notes.add("released arrow produced no direct damage event");
            if (hit != null && hit.transformed()) notes.add("non-vanilla-arrow direct damage type observed");
            if (spec.mode == LevelMode.STRESS) notes.add("controlled stored level above/independent of natural entity ceiling");
            return String.join("; ", notes);
        }
    }

    private static final class HitRecord {
        final int index;
        final int startTick;
        final double preHp;
        final double preShp;
        final double preAttackerHp;
        final double preAttackerShp;
        final Set<String> directDamageTypes = new LinkedHashSet<>();
        final Set<String> dotDamageTypes = new LinkedHashSet<>();
        final Set<String> reflectedDamageTypes = new LinkedHashSet<>();
        double lastHp;
        double lastShp;
        double lastAttackerHp;
        double lastAttackerShp;
        double postHp;
        double postShp;
        double postAttackerHp;
        double postAttackerShp;
        double targetHpRegen;
        double targetShpRegen;
        double attackerHpRegen;
        double attackerShpRegen;
        double directOriginal;
        double preCritDamage;
        double directIncoming;
        double directPost;
        double dotIncoming;
        double dotPost;
        double reflectedIncoming;
        double reflectedPost;
        int critMultiplierEvents;
        int elapsedTicks;
        boolean crit;

        HitRecord(int index, int startTick, LivingEntity target, LivingEntity player) {
            this.index = index;
            this.startTick = startTick;
            ResourceState targetResources = resources(target);
            ResourceState playerResources = resources(player);
            this.preHp = this.lastHp = target.getHealth();
            this.preShp = this.lastShp = targetResources.shp;
            this.preAttackerHp = this.lastAttackerHp = player.getHealth();
            this.preAttackerShp = this.lastAttackerShp = playerResources.shp;
            this.postHp = preHp;
            this.postShp = preShp;
            this.postAttackerHp = preAttackerHp;
            this.postAttackerShp = preAttackerShp;
        }

        void observe(LivingEntity target, LivingEntity player) {
            if (target != null) {
                ResourceState state = resources(target);
                double hp = target.getHealth();
                if (hp > lastHp) targetHpRegen += hp - lastHp;
                if (state.shp > lastShp) targetShpRegen += state.shp - lastShp;
                lastHp = postHp = hp;
                lastShp = postShp = state.shp;
            }
            if (player != null) {
                ResourceState state = resources(player);
                double hp = player.getHealth();
                if (hp > lastAttackerHp) attackerHpRegen += hp - lastAttackerHp;
                if (state.shp > lastAttackerShp) attackerShpRegen += state.shp - lastAttackerShp;
                lastAttackerHp = postAttackerHp = hp;
                lastAttackerShp = postAttackerShp = state.shp;
            }
        }

        boolean transformed() {
            return directDamageTypes.stream().anyMatch(id -> !id.equals("minecraft:arrow"));
        }
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

    private static JsonObject readAttributes(LivingEntity entity) {
        JsonObject result = new JsonObject();
        for (ResourceLocation id : OBSERVED_ATTRIBUTES) {
            Optional<Holder.Reference<Attribute>> holder = BuiltInRegistries.ATTRIBUTE.getHolder(id);
            if (holder.isPresent() && entity.getAttributes().hasAttribute(holder.get())) {
                result.addProperty(id.toString(), entity.getAttributeValue(holder.get()));
            }
            else result.add(id.toString(), null);
        }
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

    private static int fullDrawTicks(LivingEntity player) {
        double drawSpeed = attribute(player, id("apothic_attributes", "draw_speed"), 1.0D);
        int progress = 0;
        int ticks = 0;
        while (progress < BowItem.MAX_DRAW_DURATION && ticks < 200) {
            ticks++;
            int advanced = 1;
            double extra = drawSpeed - 1.0D;
            if (extra < 0.0D) {
                if (ticks % Math.max(1, (int) Math.floor(1.0D / Math.min(1.0D, -extra))) == 0) advanced = 0;
            }
            else {
                while (extra > 1.0D) {
                    advanced++;
                    extra--;
                }
                if (extra > 0.5D) {
                    if (ticks % 2 == 0) advanced++;
                    extra -= 0.5D;
                }
                if (extra > 0.0D) {
                    int divisor = Math.max(1, (int) Math.floor(1.0D / Math.min(1.0D, extra)));
                    if (ticks % divisor == 0) advanced++;
                }
            }
            progress += advanced;
        }
        return Math.max(1, ticks);
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

    private static String damageType(LivingIncomingDamageEvent event) {
        return holderId(event.getSource().typeHolder());
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

    private static void log(String kind, JsonObject payload) {
        payload.addProperty("schema", "tno.phase5f.suite_a.v1");
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
        Field field = findField(target.getClass(), name);
        return field.get(target);
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
        SPAWN, WAIT_ATTACHMENT, CONFIGURE_LEVEL, WAIT_SCALING, RUN, FINISH, DONE
    }

    private enum LevelMode {
        NATURAL_REPRESENTATIVE, NATURAL_MAXIMUM, STRESS
    }

    private record BossSpec(ResourceLocation id, int minLevel, int maxLevel, boolean primary) {
    }

    private record CaseSpec(BossSpec boss, int level, LevelMode mode) {
    }

    private record ResourceState(double shp, double maxShp, double magicules, double aura) {
    }
}
