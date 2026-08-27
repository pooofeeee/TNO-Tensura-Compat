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
import net.minecraft.world.item.BowItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
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

/**
 * Development-only Suite B runner. It uses a clean Royal Bow/Royal Arrow and
 * one native Tensura engraving, then applies the locked temporary Stage fixture
 * only to that engraving's own damage event. Production gameplay is untouched.
 */
public final class Phase5FSuiteBBenchmark {
    private static final Logger LOGGER = LogUtils.getLogger();
    private static final Gson GSON = new GsonBuilder().disableHtmlEscaping().create();
    private static final String MARKER = "TNO_PHASE5F_SUITE_B";
    private static final String TARGET_TAG = "tno_phase5f_suite_b_target";
    private static final String SCALE_TAG = "l2_tensura_scaled";
    private static final String L2_MISCS = "dev.xkmc.l2hostility.init.registrate.LHMiscs";
    private static final ResourceLocation ROYAL_BOW = id("royalvariations", "royal_bow");
    private static final ResourceLocation ROYAL_ARROW = id("royalvariations", "royal_arrow");
    private static final int MAX_SHOTS = Integer.getInteger("tno.phase5f.suiteBShots", 10);
    private static final int WINDOW_TICKS = Integer.getInteger("tno.phase5f.suiteBTicks", 200);
    private static final boolean DIAGNOSTIC = Boolean.getBoolean("tno.phase5f.suiteBDiagnostic");
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
    private static final Map<String, TagKey<net.minecraft.world.damagesource.DamageType>> SOURCE_TAGS = Map.of(
            "neoforge:is_magic", Tags.DamageTypes.IS_MAGIC,
            "minecraft:is_projectile", DamageTypeTags.IS_PROJECTILE,
            "minecraft:bypasses_armor", DamageTypeTags.BYPASSES_ARMOR,
            "minecraft:bypasses_effects", DamageTypeTags.BYPASSES_EFFECTS,
            "minecraft:bypasses_invulnerability", DamageTypeTags.BYPASSES_INVULNERABILITY,
            "minecraft:bypasses_resistance", DamageTypeTags.BYPASSES_RESISTANCE
    );

    private static Session active;

    private Phase5FSuiteBBenchmark() {
    }

    public static void onServerStarted(ServerStartedEvent event) {
        if (FMLEnvironment.production || !Boolean.getBoolean("tno.phase5f.suiteB") || active != null) return;
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

    public static void onIncomingHighest(LivingIncomingDamageEvent event) {
        if (active != null) active.captureIncomingHighest(event);
    }

    public static void onIncomingLowest(LivingIncomingDamageEvent event) {
        if (active != null) active.captureIncomingLowest(event);
    }

    public static void onDamagePre(LivingDamageEvent.Pre event) {
        if (active != null) active.captureDamagePre(event);
    }

    public static void onDamagePost(LivingDamageEvent.Post event) {
        if (active != null) active.captureDamagePost(event);
    }

    private static void requireMods() {
        for (String mod : List.of("royalvariations", "l2hostility")) {
            if (!ModList.get().isLoaded(mod)) throw new IllegalStateException("required Suite B runtime mod absent: " + mod);
        }
    }

    private static final class Session {
        private final MinecraftServer server;
        private final ServerLevel level;
        private final Family family;
        private final ItemStack cleanBow;
        private final Item royalArrow;
        private final List<CaseSpec> cases;
        private final List<JsonObject> summaries = new ArrayList<>();
        private final Map<LivingIncomingDamageEvent, FamilyProbe> familyProbes = new IdentityHashMap<>();
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

        Session(MinecraftServer server) {
            this.server = server;
            this.level = server.overworld();
            this.family = Family.parse(System.getProperty("tno.phase5f.suiteBFamily", ""));
            this.cleanBow = buildCleanBow(server, family);
            this.royalArrow = requiredItem(ROYAL_ARROW);
            this.cases = buildCases(System.getProperty("tno.phase5f.suiteBBoss", ""));
            if (cases.isEmpty()) throw new IllegalStateException("Suite B boss filter matched no targets");
            assertTnoOnlyStack(cleanBow);
            cleanupTestArea();
            logCatalog();
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
            equipCleanBow();
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
                if (spec.mode == LevelMode.STRESS && spec.level > originalMax) maxLevel.setInt(config, spec.level);
                invoke(l2Cap, "reinit", target, spec.level, false);
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
            resetActors();
            profileTemplate = new CompoundTag();
            target.saveWithoutId(profileTemplate);
            profileTemplate.remove("UUID");
            profileTemplate.remove("Pos");
            profileTemplate.remove("Motion");
            profileTemplate.remove("Rotation");
            templateKey = currentCase().profileKey();
            templateTraits = GSON.toJson(readTraits(l2Cap));
            beginRun(true);
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
            target.setHealth(target.getMaxHealth());
            target.setAbsorptionAmount(0.0F);
            target.invulnerableTime = 0;
            player.setHealth(player.getMaxHealth());
            player.setAbsorptionAmount(0.0F);
            player.invulnerableTime = 0;
            familyProbes.clear();
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
            if (type.equals(family.damageType.toString())) {
                double raw = event.getAmount();
                double coefficient = currentCase().stage.coefficient(family);
                float scaled = (float) (raw * coefficient);
                double nativeAfterResistance = scaled > target.getHealth() * 0.5D ? scaled * 0.5D : 0.0D;
                boolean sourceBypass = currentCase().stage.penetration > 0.0D
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
                event.setAmount((float) stagedAmount);
                FamilyProbe probe = new FamilyProbe(raw, scaled, nativeAfterResistance, stagedAmount,
                        sourceBypass, sourceTags(event.getSource()), event.getSource().is(Tags.DamageTypes.IS_MAGIC));
                familyProbes.put(event, probe);
                currentHit.familyRaw += raw;
                currentHit.familyStageScaled += scaled;
                currentHit.familySourceIds.add(type);
                currentHit.familySourceTags.addAll(probe.tags);
                currentHit.l2Magic |= probe.l2Magic;
            }
            else if (isBenchmarkArrow(event.getSource())) {
                currentHit.physicalOriginal += event.getOriginalAmount();
                currentHit.physicalIncoming += event.getAmount();
                currentHit.physicalSourceIds.add(type);
            }
            else {
                currentHit.dotIncoming += event.getAmount();
                currentHit.dotSourceIds.add(type);
            }
        }

        private void captureIncomingLowest(LivingIncomingDamageEvent event) {
            if (!runningTargetEvent(event)) return;
            FamilyProbe probe = familyProbes.remove(event);
            if (probe == null) return;
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
            if (type.equals(family.damageType.toString())) currentHit.familyAfterL2 += event.getNewDamage();
            else if (isBenchmarkArrow(event.getSource())) currentHit.physicalAfterL2 += event.getNewDamage();
            else currentHit.dotAfterL2 += event.getNewDamage();
        }

        private void captureDamagePost(LivingDamageEvent.Post event) {
            if (phase != Phase.RUN || currentHit == null) return;
            if (event.getEntity() == target) {
                String type = damageType(event.getSource());
                if (type.equals(family.damageType.toString())) currentHit.familyPost += event.getNewDamage();
                else if (isBenchmarkArrow(event.getSource())) currentHit.physicalPost += event.getNewDamage();
                else currentHit.dotPost += event.getNewDamage();
            }
            else if (event.getEntity() == player) {
                currentHit.reflectedPost += event.getNewDamage();
                currentHit.reflectedSourceIds.add(damageType(event.getSource()));
            }
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
            List<UUID> existing = level.getEntitiesOfClass(AbstractArrow.class,
                    player.getBoundingBox().inflate(64.0D), arrow -> fromBenchmarkPlayer(arrow.getOwner()))
                    .stream().map(Entity::getUUID).toList();
            ItemStack bow = player.getMainHandItem();
            int drawTicks = 20;
            bow.releaseUsing(level, player, bow.getUseDuration(player) - drawTicks);
            List<AbstractArrow> spawned = level.getEntitiesOfClass(AbstractArrow.class,
                    player.getBoundingBox().inflate(64.0D),
                    arrow -> fromBenchmarkPlayer(arrow.getOwner()) && !existing.contains(arrow.getUUID()));
            if (spawned.isEmpty()) throw new IllegalStateException("full-draw Royal Bow release created no Royal Arrow");
            Vec3 aim = target.getBoundingBox().getCenter();
            for (AbstractArrow arrow : spawned) {
                if (!BuiltInRegistries.ENTITY_TYPE.getKey(arrow.getType()).getNamespace().equals("royalvariations")) {
                    throw new IllegalStateException("Royal Bow did not create a Royal Variations arrow: " + arrow.getType());
                }
                try {
                    invoke(arrow, "setMarking", false);
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
                Vec3 direction = aim.subtract(arrow.position()).normalize();
                // Preserve the real released projectile, owner, velocity and damage,
                // while putting it into a deterministic final collision lane. Several
                // scripted bosses otherwise introduce non-damage trajectory misses.
                arrow.setPos(aim.subtract(direction.scale(2.0D)));
                arrow.setDeltaMovement(direction.scale(speed));
                arrow.hasImpulse = true;
                try {
                    invoke(arrow, "onHitEntity", new EntityHitResult(target));
                }
                catch (ReflectiveOperationException exception) {
                    throw new IllegalStateException("could not dispatch controlled Royal Arrow collision", exception);
                }
            }
        }

        private FakePlayer createPlayer(int index) {
            String key = "tno-phase5f-suite-b-" + family.id + "-" + currentCase().boss.id + "-" + index;
            UUID uuid = UUID.nameUUIDFromBytes(key.getBytes(StandardCharsets.UTF_8));
            FakePlayer fake = FakePlayerFactory.get(level, new GameProfile(uuid, "TNO_P5FB_" + index));
            fake.getInventory().clearContent();
            fake.removeAllEffects();
            fake.getAbilities().instabuild = true;
            fake.getAbilities().invulnerable = false;
            setBase(fake, Attributes.MAX_HEALTH, 1024.0D);
            setBase(fake, TensuraAttributes.MAX_SPIRITUAL_HEALTH, 1_000_000_000.0D);
            fake.setHealth(fake.getMaxHealth());
            fake.setPos(TEST_X, TEST_Y, 0.5D);
            return fake;
        }

        private void equipCleanBow() {
            player.setItemInHand(InteractionHand.MAIN_HAND, cleanBow.copy());
            player.setItemInHand(InteractionHand.OFF_HAND, new ItemStack(royalArrow, 64));
            player.setItemSlot(EquipmentSlot.MAINHAND, player.getMainHandItem());
            try {
                invoke(player, "detectEquipmentUpdates");
            }
            catch (ReflectiveOperationException exception) {
                throw new IllegalStateException("could not refresh fake-player attributes", exception);
            }
            assertNoApoAmplification(player);
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
            level.getEntitiesOfClass(AbstractArrow.class, player.getBoundingBox().inflate(64.0D),
                    arrow -> fromBenchmarkPlayer(arrow.getOwner())).forEach(Entity::discard);
        }

        private void cleanupCase() {
            familyProbes.clear();
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
            json.addProperty("suite", "B_TNO_ONLY");
            json.addProperty("diagnostic", DIAGNOSTIC);
            json.addProperty("TNO_family", family.id);
            json.addProperty("engraving", family.enchantment.toString());
            json.addProperty("damage_source_id", family.damageType.toString());
            json.addProperty("APO_profile", "NONE");
            json.addProperty("shots_per_case", MAX_SHOTS);
            json.addProperty("fixed_window_ticks", WINDOW_TICKS);
            json.addProperty("distance", TARGET_Z - 0.5D);
            json.addProperty("projectile_control", "real full-draw Royal Arrow dispatched through its own onHitEntity path in a deterministic two-block final collision lane; owner, velocity, item and source preserved");
            json.addProperty("bow", ROYAL_BOW.toString());
            json.addProperty("arrow", ROYAL_ARROW.toString());
            json.addProperty("royal_arrow_mark_enabled", false);
            json.addProperty("crit_enabled", false);
            json.addProperty("stage_fixture_only", true);
            json.addProperty("production_balance_mutated", false);
            json.addProperty("profile_clone_policy", "one legal native L2 roll per boss/level; pristine serialized clones for Native and S0-S7");
            json.addProperty("clean_bow_components", cleanBow.getComponents().toString());
            json.add("clean_bow_attribute_modifiers", readStackAttributes(cleanBow));
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
            levels.add(new LevelEntry((boss.minLevel + boss.maxLevel) / 2, LevelMode.NATURAL_REPRESENTATIVE));
            levels.add(new LevelEntry(boss.maxLevel, LevelMode.NATURAL_MAXIMUM));
            for (int stress : List.of(300, 600, 800, 1000)) {
                if (stress != boss.maxLevel) levels.add(new LevelEntry(stress, LevelMode.STRESS));
            }
            if (DIAGNOSTIC) levels = List.of(new LevelEntry(300, boss.maxLevel == 300 ? LevelMode.NATURAL_MAXIMUM : LevelMode.STRESS));
            List<Stage> stages = DIAGNOSTIC ? List.of(STAGES.get(0), STAGES.get(1), STAGES.get(6), STAGES.get(8)) : STAGES;
            for (LevelEntry entry : levels) {
                for (Stage stage : stages) result.add(new CaseSpec(boss, entry.level, entry.mode, stage));
            }
        }
        return result;
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
            finalShp = resources(target).shp;
        }

        JsonObject caseJson() {
            JsonObject json = commonJson();
            json.addProperty("status", "running");
            return json;
        }

        JsonObject rowJson(HitRecord hit) {
            JsonObject json = commonJson();
            json.addProperty("hit_index", hit.index);
            json.addProperty("crit", false);
            json.addProperty("pre_HP", hit.preHp);
            json.addProperty("post_HP", hit.postHp);
            json.addProperty("pre_SHP", hit.preShp);
            json.addProperty("post_SHP", hit.postShp);
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
            json.addProperty("blocked_or_cancelled", hit.directDamage() == 0.0D && hit.resourceDamage() == 0.0D);
            json.add("damage_source_ids", strings(union(hit.physicalSourceIds, hit.familySourceIds)));
            json.add("damage_source_tags_if_observable", strings(hit.familySourceTags));
            json.addProperty("family_source_is_l2_magic", hit.l2Magic);
            json.addProperty("physical_original_before_stage", hit.physicalOriginal);
            json.addProperty("engraving_native_amount", hit.familyRaw);
            json.addProperty("engraving_after_stage_coefficient", hit.familyStageScaled);
            json.addProperty("damage_before_matching_resistance_recovery", hit.familyAfterResistance);
            json.addProperty("damage_after_matching_resistance_recovery", hit.familyAfterRecovery);
            json.addProperty("damage_after_L2_processing", hit.familyPost);
            json.addProperty("matching_resistance_cancelled_before_recovery", hit.familyCanceledBeforeRecovery);
            json.addProperty("tensura_resistance_bypass_level", hit.resistanceBypassLevel);
            json.addProperty("nullification_authoritative", hit.nullificationAuthoritative);
            json.addProperty("dispell_transformed", transformed(hit, "l2hostility:dispell", true));
            json.addProperty("dementor_transformed", transformed(hit, "l2hostility:dementor", false));
            json.addProperty("adaptive_hit_index", traitRanks.has("l2hostility:adaptive") ? hit.index : 0);
            json.addProperty("adaptive_effect_observed", adaptiveObserved(hit));
            json.addProperty("l2_layer_bypassed_unexpectedly", false);
            json.addProperty("notes", interactionNotes(hit));
            return json;
        }

        JsonObject summaryJson() {
            JsonObject json = commonJson();
            json.addProperty("status", "ok");
            json.addProperty("shots_released", shotsReleased);
            json.addProperty("hits_recorded", hits.size());
            json.addProperty("direct_damage", hits.stream().mapToDouble(HitRecord::directDamage).sum());
            json.addProperty("resource_damage", hits.stream().mapToDouble(HitRecord::resourceDamage).sum());
            json.addProperty("DoT_damage", hits.stream().mapToDouble(hit -> hit.dotPost).sum());
            json.addProperty("regen", hits.stream().mapToDouble(hit -> hit.targetHpRegen + hit.targetShpRegen).sum());
            json.addProperty("reflected_damage", hits.stream().mapToDouble(hit -> hit.reflectedPost).sum());
            json.addProperty("elapsed_ticks", elapsedTicks);
            json.addProperty("DPS", dps());
            if (htk == null) json.add("HTK", null); else json.addProperty("HTK", htk);
            if (ttk == null) json.add("TTK", null); else json.addProperty("TTK", ttk);
            json.addProperty("attacker_defeated", attackerDefeated);
            json.addProperty("final_HP", finalHp);
            json.addProperty("final_SHP", finalShp);
            json.addProperty("notes", interactionNotes(null));
            return json;
        }

        private JsonObject commonJson() {
            JsonObject json = new JsonObject();
            json.addProperty("suite", "B_TNO_ONLY");
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
            json.addProperty("legal_profile", spec.mode != LevelMode.STRESS);
            json.addProperty("legal_trait_profile", true);
            json.addProperty("native_profile_source", nativeProfileSource);
            json.addProperty("profile_clone_verified", true);
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
            json.addProperty("stage_bonus", spec.stage.bonus);
            json.addProperty("stage_coefficient", spec.stage.coefficient(active.family));
            json.addProperty("APO_profile", "NONE");
            json.addProperty("royal_arrow_mark_enabled", false);
            json.addProperty("matching_Tensura_resistance_present", matchingResistance);
            json.addProperty("matching_Tensura_nullification_present", matchingNullification);
            json.addProperty("penetration_percentage_applied", matchingResistance && !matchingNullification ? spec.stage.penetration : 0.0D);
            json.add("Bow_attributes", bowAttributes.deepCopy());
            json.add("attacker_APO_attributes", attackerAttributes.deepCopy());
            return json;
        }

        private boolean transformed(HitRecord hit, String trait, boolean magic) {
            return traitRanks.has(trait) && hit.l2Magic == magic
                    && hit.familyPost + 0.0001D < hit.familyAfterRecovery;
        }

        private boolean adaptiveObserved(HitRecord hit) {
            if (!traitRanks.has("l2hostility:adaptive") || hit.index < 2 || hit.familyAfterRecovery <= 0.0D) return false;
            HitRecord previous = hits.stream().filter(value -> value.index == hit.index - 1).findFirst().orElse(null);
            if (previous == null || previous.familyAfterRecovery <= 0.0D) return false;
            return hit.familyPost / hit.familyAfterRecovery + 0.0001D
                    < previous.familyPost / previous.familyAfterRecovery;
        }

        private double dps() {
            double effective = hits.stream().mapToDouble(HitRecord::resourceDamage).sum();
            return elapsedTicks <= 0 ? 0.0D : effective / (elapsedTicks / 20.0D);
        }

        private String interactionNotes(HitRecord hit) {
            List<String> notes = new ArrayList<>();
            traitRanks.keySet().stream().filter(DEFENSIVE_TRAITS::contains)
                    .forEach(id -> notes.add(id + " rank " + traitRanks.get(id).getAsInt()));
            if (matchingNullification) notes.add("matching Tensura Nullification kept authoritative");
            else if (matchingResistance) notes.add("matching Tensura Resistance measured before benchmark recovery");
            if (spec.mode == LevelMode.STRESS) notes.add("controlled level above/independent of natural entity ceiling");
            if (hit != null && hit.blocked()) notes.add("released Royal Arrow produced no net HP/SHP damage");
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
        final Set<String> physicalSourceIds = new LinkedHashSet<>();
        final Set<String> familySourceIds = new LinkedHashSet<>();
        final Set<String> familySourceTags = new LinkedHashSet<>();
        final Set<String> dotSourceIds = new LinkedHashSet<>();
        final Set<String> reflectedSourceIds = new LinkedHashSet<>();
        double lastHp;
        double lastShp;
        double lastAttackerHp;
        double lastAttackerShp;
        double postHp;
        double postShp;
        double targetHpRegen;
        double targetShpRegen;
        double attackerHpRegen;
        double attackerShpRegen;
        double physicalOriginal;
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
        int elapsedTicks;
        boolean l2Magic;
        boolean familyCanceledBeforeRecovery;
        boolean nullificationAuthoritative;
        double resistanceBypassLevel;

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
                lastAttackerHp = hp;
                lastAttackerShp = state.shp;
            }
        }

        double resourceDamage() {
            return Math.max(0.0D, preHp + preShp - postHp - postShp + targetHpRegen + targetShpRegen);
        }

        double directDamage() {
            return physicalPost + familyPost;
        }

        boolean blocked() {
            return directDamage() == 0.0D && resourceDamage() == 0.0D;
        }
    }

    private static ItemStack buildCleanBow(MinecraftServer server, Family family) {
        ItemStack bow = new ItemStack(requiredItem(ROYAL_BOW));
        Registry<Enchantment> registry = server.registryAccess().registryOrThrow(Registries.ENCHANTMENT);
        Holder.Reference<Enchantment> enchantment = registry.getHolderOrThrow(
                ResourceKey.create(Registries.ENCHANTMENT, family.enchantment));
        bow.enchant(enchantment, 1);
        return bow;
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
        return skillToggled(target, switch (family) {
            case MAGIC -> "MAGIC_RESISTANCE";
            case HOLY -> "HOLY_ATTACK_RESISTANCE";
            case SOUL -> "SPIRITUAL_ATTACK_RESISTANCE";
        });
    }

    private static boolean matchingNullification(LivingEntity target, Family family) {
        return skillToggled(target, switch (family) {
            case MAGIC -> "MAGIC_NULLIFICATION";
            case HOLY -> "HOLY_ATTACK_NULLIFICATION";
            case SOUL -> "SPIRITUAL_ATTACK_NULLIFICATION";
        });
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
        payload.addProperty("schema", "tno.phase5f.suite_b.v1");
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
        NATURAL_REPRESENTATIVE, NATURAL_MAXIMUM, STRESS
    }

    private enum Family {
        MAGIC("MAGIC_WEAPON", id("tensura", "magic_weapon"), id("tensura", "magic")),
        HOLY("HOLY_WEAPON", id("tensura", "holy_weapon"), id("tensura", "holy_damage")),
        SOUL("SOUL_EATER", id("tensura", "soul_eater"), id("tensura", "soul_scatter"));

        final String id;
        final ResourceLocation enchantment;
        final ResourceLocation damageType;

        Family(String id, ResourceLocation enchantment, ResourceLocation damageType) {
            this.id = id;
            this.enchantment = enchantment;
            this.damageType = damageType;
        }

        static Family parse(String value) {
            for (Family family : values()) {
                if (family.name().equalsIgnoreCase(value) || family.id.equalsIgnoreCase(value)) return family;
            }
            throw new IllegalArgumentException("phase5f_suite_b_family must be magic, holy, or soul");
        }
    }

    private record BossSpec(ResourceLocation id, int minLevel, int maxLevel, boolean primary) {
    }

    private record LevelEntry(int level, LevelMode mode) {
    }

    private record Stage(String name, Long ep, double bonus, double penetration) {
        double coefficient(Family family) {
            if (name.equals("Native")) return 1.0D;
            return 1.0D + bonus * (family == Family.SOUL ? 1.0D : 2.0D);
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

    private record ResourceState(double shp, double maxShp, double magicules, double aura) {
    }
}
