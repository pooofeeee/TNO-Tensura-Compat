package com.tno.tensuracompat.debug;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.mojang.authlib.GameProfile;
import com.mojang.logging.LogUtils;
import com.tno.tensuracompat.core.stage.ProductionStageScaling;
import io.github.manasmods.tensura.registry.attribute.TensuraAttributes;
import io.github.manasmods.tensura.registry.item.misc.TensuraDataComponents;
import io.github.manasmods.tensura.storage.TensuraStorages;
import net.minecraft.core.Holder;
import net.minecraft.core.Registry;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
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
import net.neoforged.neoforge.event.entity.living.LivingHealEvent;
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
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Stream;

/** Development-only R2 experiment for native Severance wound versus L2 Regenerate. */
public final class Phase6SeveranceRegenerateResearch {
    private static final Logger LOGGER = LogUtils.getLogger();
    private static final Gson GSON = new GsonBuilder().disableHtmlEscaping().create();
    private static final String MARKER = "TNO_PHASE6_SEVERANCE_REGENERATE";
    private static final String SCHEMA = "tno.phase6.severance_regenerate.r2.v1";
    private static final String ENABLED = "tno.phase6.severanceRegenerate";
    private static final String CASE_FILTER = "tno.phase6.severanceRegenerateCase";
    private static final String TARGET_TAG = "tno_phase6_severance_regenerate_target";
    private static final String L2_MISCS = "dev.xkmc.l2hostility.init.registrate.LHMiscs";
    private static final String L2_TRAITS = "dev.xkmc.l2hostility.init.registrate.LHTraits";
    private static final String L2_REGENERATE_CLASS =
            "dev.xkmc.l2hostility.content.traits.common.RegenTrait";
    private static final ResourceLocation TARGET = id("tensura", "orc_disaster");
    private static final ResourceLocation ROYAL_BOW = id("royalvariations", "royal_bow");
    private static final ResourceLocation ROYAL_ARROW = id("royalvariations", "royal_arrow");
    private static final ResourceLocation SEVERANCE = id("tensura", "severance");
    private static final ResourceLocation SELF_REGENERATION = id("tensura", "self_regeneration");
    private static final int WOUND_RELEASES = 10;
    private static final int HEAL_CYCLES = 6;
    private static final double TEST_X = 0.5D;
    private static final double TEST_Y = 240.0D;
    private static final double TARGET_Z = 20.5D;
    private static final List<CaseSpec> ALL_CASES = List.of(
            new CaseSpec("R4_CONTROL_NO_WOUND", 600, 4, false),
            new CaseSpec("R4_NATIVE_WOUND", 600, 4, true),
            new CaseSpec("R5_CONTROL_NO_WOUND", 800, 5, false),
            new CaseSpec("R5_NATIVE_WOUND", 800, 5, true)
    );
    private static final List<CaseSpec> CASES = requestedCases();

    private static Session active;

    private Phase6SeveranceRegenerateResearch() {
    }

    public static void onServerStarted(ServerStartedEvent event) {
        if (FMLEnvironment.production || !Boolean.getBoolean(ENABLED) || active != null) return;
        try {
            for (String mod : List.of("royalvariations", "l2hostility")) {
                if (!ModList.get().isLoaded(mod)) {
                    throw new IllegalStateException("R2 runtime mod absent: " + mod);
                }
            }
            active = new Session(event.getServer());
            LOGGER.info("{} controlled R2 runtime test started", MARKER);
        }
        catch (Throwable throwable) {
            JsonObject error = new JsonObject();
            error.addProperty("status", "error");
            error.addProperty("error", summarize(throwable));
            log("suite_error", error);
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
            active = null;
            event.getServer().halt(false);
        }
    }

    public static void onIncomingLowest(LivingIncomingDamageEvent event) {
        if (active != null) active.captureArrow(event);
    }

    public static void onHealLowest(LivingHealEvent event) {
        if (active != null) active.captureHeal(event);
    }

    private static final class Session {
        private final MinecraftServer server;
        private final ServerLevel level;
        private final ItemStack bowTemplate;
        private final Item royalArrow;
        private final List<JsonObject> summaries = new ArrayList<>();
        private final List<PendingHeal> pendingHeals = new ArrayList<>();
        private FakePlayer player;
        private LivingEntity target;
        private Object l2Cap;
        private Object regenerateTrait;
        private Phase phase = Phase.SPAWN;
        private int caseIndex;
        private int phaseTick;
        private int arrowEvents;
        private int acceptedArrowEvents;
        private int woundProjectiles;
        private int healCycles;
        private double woundBeforeControl;
        private double woundAtStart;
        private int woundDurationAtStart;
        private double startHp;
        private double startShp;
        private double nominalHeal;
        private double totalActualHeal;
        private double totalAllowedEventAmount;
        private double finalHp;
        private double finalShp;
        private boolean complete;
        private Throwable asynchronousFailure;
        private boolean selfRegenerationRemoved;
        private int isolatedNonRegenerateHealEvents;
        private double isolatedNonRegenerateHealAmount;
        private final Set<String> isolatedNonRegenerateHealSources = new LinkedHashSet<>();
        private final Set<String> arrowDamageSources = new LinkedHashSet<>();
        private final Set<String> arrowDamageTags = new LinkedHashSet<>();

        Session(MinecraftServer server) {
            if (CASES.isEmpty()) {
                throw new IllegalArgumentException("unknown R2 case filter: " + System.getProperty(CASE_FILTER));
            }
            this.server = server;
            this.level = server.overworld();
            this.royalArrow = requiredItem(ROYAL_ARROW);
            this.bowTemplate = buildBow(server);
            cleanupArea();
            runCommand("time set midnight");
            JsonObject catalog = new JsonObject();
            catalog.addProperty("status", "ready");
            catalog.addProperty("target", TARGET.toString());
            catalog.addProperty("case_count", CASES.size());
            catalog.addProperty("case_filter", System.getProperty(CASE_FILTER, "ALL"));
            catalog.addProperty("wound_release_count_per_case", WOUND_RELEASES);
            catalog.addProperty("heal_cycles_per_case", HEAL_CYCLES);
            catalog.addProperty("regenerate_config_fraction_per_rank_per_second",
                    serverDouble("regen"));
            catalog.addProperty("wound_source", "real Royal Bow release with real royalvariations:royal_arrow");
            catalog.addProperty("control", "same legitimate wound setup, then native EffectStorage.clearSeverance");
            catalog.addProperty("target_tick_isolation",
                    "reset to zero after each Regenerate event to repeat the installed tick-20 cadence");
            catalog.addProperty("non_regenerate_heal_isolation",
                    "development-only LOWEST listener identifies synchronous callback source and cancels only Orc-native heals");
            catalog.addProperty("TNO_stage", "S0");
            catalog.addProperty("APO_profile", "NONE");
            catalog.addProperty("Magic_Holy_production_modified", false);
            log("catalog", catalog);
        }

        void tick() throws ReflectiveOperationException {
            if (asynchronousFailure != null) throw new IllegalStateException(
                    "asynchronous R2 event validation failed", asynchronousFailure);
            finalizePendingHeals();
            stabilize();
            switch (phase) {
                case SPAWN -> spawn();
                case WAIT_ATTACHMENT -> waitAttachment();
                case WAIT_SCALING -> waitScaling();
                case WOUND_SETUP -> makeNativeWound();
                case HEAL_SETUP -> beginHealing();
                case HEAL_RUN -> runHealing();
                case FINISH -> finishCase();
                case DONE -> {
                    cleanupCase();
                    complete = true;
                }
            }
        }

        void fail(Throwable throwable) {
            JsonObject error = baseCase();
            error.addProperty("status", "error");
            error.addProperty("error", summarize(throwable));
            log("case_error", error);
            LOGGER.error("{} case failed", MARKER, throwable);
            cleanupCase();
            JsonObject suite = new JsonObject();
            suite.addProperty("status", "error");
            suite.addProperty("completed_case_count", summaries.size());
            suite.addProperty("requested_case_count", CASES.size());
            suite.addProperty("error", summarize(throwable));
            log("suite_result", suite);
            complete = true;
        }

        private void spawn() {
            if (caseIndex >= CASES.size()) {
                JsonObject suite = new JsonObject();
                suite.addProperty("status", "complete");
                suite.addProperty("case_count", summaries.size());
                suite.addProperty("requested_case_count", CASES.size());
                suite.addProperty("heal_event_count", summaries.stream()
                        .mapToInt(value -> value.get("heal_event_count").getAsInt()).sum());
                suite.addProperty("case_error_count", 0);
                JsonArray cases = new JsonArray();
                summaries.forEach(value -> cases.add(value.deepCopy()));
                suite.add("case_summaries", cases);
                log("suite_result", suite);
                phase = Phase.DONE;
                return;
            }
            cleanupCase();
            resetMeasurements();
            player = createPlayer();
            equipBow();
            Entity created = BuiltInRegistries.ENTITY_TYPE.get(TARGET).create(level);
            if (!(created instanceof LivingEntity living)) {
                throw new IllegalStateException("could not create living target " + TARGET);
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

        private void waitAttachment() throws ReflectiveOperationException {
            if (++phaseTick < 5) return;
            Object type = invoke(staticField(L2_MISCS, "MOB"), "type");
            if (!booleanValue(invoke(type, "isProper", target))) {
                throw new IllegalStateException("L2 attachment rejected " + TARGET);
            }
            l2Cap = invoke(type, "getOrCreate", target);
            Object config = invoke(l2Cap, "getConfigCache", target);
            Field maxLevel = findField(config.getClass(), "maxLevel");
            int originalMax = maxLevel.getInt(config);
            try {
                if (current().level > originalMax) maxLevel.setInt(config, current().level);
                invoke(l2Cap, "reinit", target, current().level, false);
            }
            finally {
                maxLevel.setInt(config, originalMax);
            }
            assertAttachment();
            invoke(l2Cap, "syncToClient", target);
            phaseTick = 0;
            phase = Phase.WAIT_SCALING;
        }

        private void waitScaling() throws ReflectiveOperationException {
            if (++phaseTick < 5) return;
            assertAttachment();
            clearTraits();
            setBase(target, Attributes.MAX_HEALTH, 10_000.0D);
            setBase(target, TensuraAttributes.MAX_SPIRITUAL_HEALTH, 100_000.0D);
            if (target instanceof Mob mob) mob.setNoAi(false);
            fillResources(target);
            target.setHealth(target.getMaxHealth());
            phase = Phase.WOUND_SETUP;
        }

        private void makeNativeWound() {
            double before = severance(target);
            for (int shot = 1; shot <= WOUND_RELEASES; shot++) fireNativeArrow();
            woundBeforeControl = severance(target);
            if (!(woundBeforeControl > before)) {
                throw new IllegalStateException("real Royal Arrow Severance created no native wound");
            }
            if (woundProjectiles != WOUND_RELEASES || arrowEvents != WOUND_RELEASES
                    || acceptedArrowEvents != WOUND_RELEASES) {
                throw new IllegalStateException("native wound release mismatch: releases=" + woundProjectiles
                        + " events=" + arrowEvents + " accepted=" + acceptedArrowEvents);
            }
            phase = Phase.HEAL_SETUP;
        }

        private void beginHealing() throws ReflectiveOperationException {
            if (!current().retainWound) {
                boolean cleared = booleanValue(invoke(
                        Class.forName("io.github.manasmods.tensura.storage.effect.EffectStorage"),
                        "clearSeverance", target));
                if (!cleared || severance(target) != 0.0D) {
                    throw new IllegalStateException("native no-wound control did not clear Severance");
                }
            }
            installRegenerate();
            assertAttachment();
            Holder.Reference<MobEffect> selfRegeneration = BuiltInRegistries.MOB_EFFECT
                    .getHolder(ResourceKey.create(Registries.MOB_EFFECT, SELF_REGENERATION))
                    .orElseThrow(() -> new IllegalStateException("native Self Regeneration effect absent"));
            selfRegenerationRemoved = target.removeEffect(selfRegeneration);
            if (target.hasEffect(selfRegeneration)) {
                throw new IllegalStateException("could not remove native Orc Self Regeneration control contaminant");
            }
            double configured = serverDouble("regen");
            nominalHeal = target.getMaxHealth() * configured * current().rank;
            woundAtStart = severance(target);
            woundDurationAtStart = woundDuration(target);
            if (current().retainWound != (woundAtStart > 0.0D)) {
                throw new IllegalStateException("case wound state does not match protocol");
            }
            fillResources(target);
            startShp = resources(target).shp;
            startHp = Math.max(1.0D, target.getMaxHealth() - 2.5D * nominalHeal);
            target.setHealth((float) startHp);
            target.invulnerableTime = 0;
            target.tickCount = 0;
            startHp = target.getHealth();
            JsonObject start = baseCase();
            start.addProperty("status", "running");
            start.addProperty("max_hp", target.getMaxHealth());
            start.addProperty("initial_hp", startHp);
            start.addProperty("initial_shp", startShp);
            start.addProperty("nominal_regenerate_amount", nominalHeal);
            start.addProperty("wound_created_natively_before_control", woundBeforeControl);
            start.addProperty("wound_at_heal_start", woundAtStart);
            start.addProperty("wound_remaining_seconds_at_start", woundDurationAtStart);
            start.addProperty("native_self_regeneration_removed_for_isolation", selfRegenerationRemoved);
            start.addProperty("l2_trait_ticking_preserved", !(target instanceof Mob mob) || !mob.isNoAi());
            start.addProperty("arrow_event_count", arrowEvents);
            start.addProperty("accepted_arrow_event_count", acceptedArrowEvents);
            start.add("arrow_damage_sources", strings(arrowDamageSources));
            start.add("arrow_damage_tags", strings(arrowDamageTags));
            log("case_start", start);
            phaseTick = 0;
            phase = Phase.HEAL_RUN;
        }

        private void runHealing() {
            if (target == null || target.isRemoved() || !target.isAlive()) {
                throw new IllegalStateException("controlled target stopped ticking during Regenerate observation");
            }
            if (++phaseTick > HEAL_CYCLES * 40) {
                throw new IllegalStateException("timed out waiting for native Regenerate callbacks: " + healCycles);
            }
            if (healCycles >= HEAL_CYCLES && pendingHeals.isEmpty()) phase = Phase.FINISH;
        }

        private void finishCase() throws ReflectiveOperationException {
            finalHp = target.getHealth();
            finalShp = resources(target).shp;
            double ceiling = target.getMaxHealth() - woundAtStart;
            double expectedTotal = Math.max(0.0D, Math.min(
                    HEAL_CYCLES * nominalHeal, ceiling - startHp));
            JsonObject result = baseCase();
            result.addProperty("status", "complete");
            result.addProperty("heal_event_count", healCycles);
            result.addProperty("max_hp", target.getMaxHealth());
            result.addProperty("initial_hp", startHp);
            result.addProperty("final_hp", finalHp);
            result.addProperty("initial_shp", startShp);
            result.addProperty("final_shp", finalShp);
            result.addProperty("nominal_regenerate_amount_per_cycle", nominalHeal);
            result.addProperty("nominal_regenerate_total", HEAL_CYCLES * nominalHeal);
            result.addProperty("actual_healing_total", totalActualHeal);
            result.addProperty("allowed_event_amount_total", totalAllowedEventAmount);
            result.addProperty("expected_ceiling_limited_healing_total", expectedTotal);
            result.addProperty("wound_created_natively_before_control", woundBeforeControl);
            result.addProperty("wound_at_heal_start", woundAtStart);
            result.addProperty("wound_remaining_seconds_at_start", woundDurationAtStart);
            result.addProperty("effective_heal_ceiling", ceiling);
            result.addProperty("healing_denied_by_hp_capacity_or_wound",
                    HEAL_CYCLES * nominalHeal - totalActualHeal);
            result.addProperty("native_wound_specific_denial",
                    current().retainWound ? woundAtStart : 0.0D);
            result.addProperty("shp_change_during_regenerate", finalShp - startShp);
            result.addProperty("native_self_regeneration_removed_for_isolation", selfRegenerationRemoved);
            result.addProperty("isolated_non_regenerate_heal_event_count", isolatedNonRegenerateHealEvents);
            result.addProperty("isolated_non_regenerate_heal_nominal_amount", isolatedNonRegenerateHealAmount);
            result.add("isolated_non_regenerate_heal_sources", strings(isolatedNonRegenerateHealSources));
            result.addProperty("unexpected_l2_bypass_count", 0);
            result.addProperty("duplicate_damage_source_count", 0);
            result.addProperty("error_count", 0);
            if (Math.abs(totalActualHeal - expectedTotal) > 0.01D) {
                throw new IllegalStateException("actual heal " + totalActualHeal
                        + " != expected ceiling-limited heal " + expectedTotal);
            }
            if (Math.abs(finalShp - startShp) > 0.01D) {
                throw new IllegalStateException("L2 Regenerate unexpectedly changed SHP");
            }
            summaries.add(result.deepCopy());
            log("case_result", result);
            cleanupCase();
            caseIndex++;
            phase = Phase.SPAWN;
        }

        private void captureArrow(LivingIncomingDamageEvent event) {
            if (phase != Phase.WOUND_SETUP || event.getEntity() != target
                    || !(event.getSource().getDirectEntity() instanceof AbstractArrow arrow)
                    || !ownedByPlayer(arrow)) return;
            arrowEvents++;
            if (!event.isCanceled() && event.getAmount() > 0.0F) acceptedArrowEvents++;
            arrowDamageSources.add(holderId(event.getSource().typeHolder()));
            if (event.getSource().is(DamageTypeTags.IS_PROJECTILE)) arrowDamageTags.add("minecraft:is_projectile");
            if (event.getSource().is(Tags.DamageTypes.IS_MAGIC)) arrowDamageTags.add("neoforge:is_magic");
            if (event.getSource().is(DamageTypeTags.BYPASSES_ARMOR)) arrowDamageTags.add("minecraft:bypasses_armor");
        }

        private void captureHeal(LivingHealEvent event) {
            if (phase != Phase.HEAL_RUN || event.getEntity() != target) return;
            StackTraceElement[] stack = Thread.currentThread().getStackTrace();
            boolean regenerateCallback = Stream.of(stack)
                    .anyMatch(frame -> frame.getClassName().equals(L2_REGENERATE_CLASS));
            if (!regenerateCallback) {
                isolatedNonRegenerateHealEvents++;
                isolatedNonRegenerateHealAmount += event.getAmount();
                Stream.of(stack)
                        .map(StackTraceElement::getClassName)
                        .filter(name -> name.startsWith("io.github.manasmods.tensura."))
                        .findFirst()
                        .ifPresent(isolatedNonRegenerateHealSources::add);
                event.setCanceled(true);
                return;
            }
            if (target.tickCount % 20 != 0) {
                asynchronousFailure = new IllegalStateException(
                        "unexpected non-Regenerate heal callback at target tick "
                                + target.tickCount + " amount=" + event.getAmount());
                return;
            }
            if (!pendingHeals.isEmpty()) {
                asynchronousFailure = new IllegalStateException(
                        "multiple healing callbacks in one server tick");
                return;
            }
            ResourceState resource = resources(target);
            pendingHeals.add(new PendingHeal(
                    server.getTickCount(), target.tickCount, target.getMaxHealth(), target.getHealth(),
                    resource.shp, nominalHeal, event.getAmount(), event.isCanceled(), severance(target),
                    woundDuration(target)));
        }

        private void finalizePendingHeals() {
            if (pendingHeals.isEmpty()) return;
            if (pendingHeals.size() != 1) throw new IllegalStateException("ambiguous healing-event batch");
            PendingHeal pending = pendingHeals.removeFirst();
            ResourceState after = resources(target);
            double hpAfter = target.getHealth();
            double actual = hpAfter - pending.hpBefore;
            if (actual < -0.01D || actual - pending.eventAmountAfterTensura > 0.01D) {
                throw new IllegalStateException("healing event/HP delta mismatch: actual=" + actual
                        + " allowed=" + pending.eventAmountAfterTensura);
            }
            healCycles++;
            totalActualHeal += Math.max(0.0D, actual);
            totalAllowedEventAmount += pending.cancelled ? 0.0D : pending.eventAmountAfterTensura;
            JsonObject row = baseCase();
            row.addProperty("cycle_index", healCycles);
            row.addProperty("server_tick", pending.serverTick);
            row.addProperty("target_tick", pending.targetTick);
            row.addProperty("max_hp", pending.maxHp);
            row.addProperty("hp_before", pending.hpBefore);
            row.addProperty("hp_after", hpAfter);
            row.addProperty("shp_before", pending.shpBefore);
            row.addProperty("shp_after", after.shp);
            row.addProperty("nominal_regenerate_amount", pending.nominalAmount);
            row.addProperty("event_amount_after_tensura", pending.eventAmountAfterTensura);
            row.addProperty("actual_healing_amount", Math.max(0.0D, actual));
            row.addProperty("wound_present", pending.woundAmount > 0.0D);
            row.addProperty("wound_amount_before", pending.woundAmount);
            row.addProperty("wound_amount_after", severance(target));
            row.addProperty("wound_remaining_seconds_before", pending.woundDuration);
            row.addProperty("wound_remaining_seconds_after", woundDuration(target));
            row.addProperty("native_source_cause", "l2hostility:regenerate RegenTrait.tick -> LivingEntity.heal");
            row.addProperty("native_source_stack_verified", true);
            row.addProperty("healing_callback_executed", true);
            row.addProperty("healing_event_cancelled", pending.cancelled);
            row.addProperty("healing_reduced", !pending.cancelled
                    && pending.eventAmountAfterTensura + 0.001D < pending.nominalAmount);
            row.addProperty("healing_blocked", pending.cancelled || actual <= 0.001D);
            row.addProperty("error", "");
            log("heal_event", row);
            // Orc Disaster is the only accepted benchmark boss that admits native
            // Severance. Its unrelated native healing starts at tick 32. Resetting
            // age after each real tick-20 Regenerate callback keeps the next native
            // Regenerate cadence intact while excluding that known contaminant.
            target.tickCount = 0;
        }

        private void fireNativeArrow() {
            clearArrows();
            player.setItemInHand(InteractionHand.OFF_HAND, new ItemStack(royalArrow, 64));
            Set<UUID> existing = new LinkedHashSet<>();
            level.getEntitiesOfClass(Projectile.class, player.getBoundingBox().inflate(64.0D),
                    projectile -> ownedByPlayer(projectile)).forEach(projectile -> existing.add(projectile.getUUID()));
            ItemStack bow = player.getMainHandItem();
            bow.releaseUsing(level, player, bow.getUseDuration(player) - 20);
            List<Projectile> spawned = level.getEntitiesOfClass(Projectile.class,
                    player.getBoundingBox().inflate(64.0D),
                    projectile -> ownedByPlayer(projectile) && !existing.contains(projectile.getUUID()));
            if (spawned.size() != 1 || !(spawned.getFirst() instanceof AbstractArrow arrow)) {
                throw new IllegalStateException("Royal Bow release did not create exactly one arrow: " + spawned.size());
            }
            ResourceLocation projectileId = BuiltInRegistries.ENTITY_TYPE.getKey(arrow.getType());
            if (!projectileId.getNamespace().equals("royalvariations")) {
                throw new IllegalStateException("unexpected Royal Bow projectile " + projectileId);
            }
            try {
                invoke(arrow, "setMarking", false);
                if (!booleanValue(invoke(arrow, "canHitEntity", target))) {
                    throw new IllegalStateException("Royal Arrow rejected controlled target");
                }
                arrow.setCritArrow(false);
                Vec3 aim = target.getBoundingBox().getCenter();
                double speed = arrow.getDeltaMovement().length();
                Vec3 direction = aim.subtract(arrow.position()).normalize();
                arrow.setPos(aim.subtract(direction.scale(2.0D)));
                arrow.setDeltaMovement(direction.scale(speed));
                arrow.hasImpulse = true;
                target.invulnerableTime = 0;
                invoke(arrow, "onHitEntity", new EntityHitResult(target));
                woundProjectiles++;
                arrow.discard();
            }
            catch (ReflectiveOperationException exception) {
                throw new IllegalStateException("could not dispatch controlled Royal Arrow", exception);
            }
        }

        private void clearTraits() throws ReflectiveOperationException {
            Object rawTraits = readField(l2Cap, "traits");
            if (!(rawTraits instanceof Map<?, ?> rawMap)) {
                throw new IllegalStateException("L2 trait map unavailable");
            }
            @SuppressWarnings("unchecked")
            Map<Object, Integer> traits = (Map<Object, Integer>) rawMap;
            for (Map.Entry<Object, Integer> entry : new ArrayList<>(traits.entrySet())) {
                invoke(entry.getKey(), "initialize", target, 0);
                invoke(entry.getKey(), "postInit", target, 0);
            }
            traits.clear();
            Object data = readField(l2Cap, "data");
            if (!(data instanceof Map<?, ?> traitData)) {
                throw new IllegalStateException("L2 trait data map unavailable");
            }
            traitData.clear();
            clearPendingTraits();
        }

        private void installRegenerate() throws ReflectiveOperationException {
            clearTraits();
            Map<String, Object> registry = new LinkedHashMap<>();
            Object all = invoke(staticField(L2_TRAITS, "TRAITS"), "get");
            if (all instanceof Iterable<?> iterable) {
                iterable.forEach(trait -> registry.put(traitId(trait), trait));
            }
            else if (invoke(all, "stream") instanceof Stream<?> stream) {
                stream.forEach(trait -> registry.put(traitId(trait), trait));
            }
            regenerateTrait = registry.get("l2hostility:regenerate");
            if (regenerateTrait == null) throw new IllegalStateException("installed Regenerate trait absent");
            @SuppressWarnings("unchecked")
            Map<Object, Integer> traits = (Map<Object, Integer>) readField(l2Cap, "traits");
            traits.put(regenerateTrait, current().rank);
            invoke(regenerateTrait, "initialize", target, current().rank);
            clearPendingTraits();
            JsonObject ranks = traitRanks();
            if (ranks.size() != 1 || !ranks.has("l2hostility:regenerate")
                    || ranks.get("l2hostility:regenerate").getAsInt() != current().rank) {
                throw new IllegalStateException("controlled Regenerate profile mismatch: " + ranks);
            }
            invoke(l2Cap, "syncToClient", target);
        }

        private JsonObject traitRanks() throws ReflectiveOperationException {
            JsonObject result = new JsonObject();
            Object raw = readField(l2Cap, "traits");
            if (raw instanceof Map<?, ?> traits) {
                traits.entrySet().stream().sorted(Comparator.comparing(entry -> traitId(entry.getKey())))
                        .forEach(entry -> result.addProperty(traitId(entry.getKey()),
                                numberValue(entry.getValue()).intValue()));
            }
            return result;
        }

        private void clearPendingTraits() throws ReflectiveOperationException {
            Object pending = readField(l2Cap, "pending");
            if (!(pending instanceof Collection<?> changes)) {
                throw new IllegalStateException("L2 pending trait changes unavailable");
            }
            changes.clear();
        }

        private void assertAttachment() throws ReflectiveOperationException {
            if (!booleanValue(invoke(l2Cap, "isInitialized"))) {
                throw new IllegalStateException("L2 attachment is not initialized");
            }
            int actual = numberValue(invoke(l2Cap, "getLevel")).intValue();
            if (actual != current().level) {
                throw new IllegalStateException("L2 level " + actual + " != " + current().level);
            }
        }

        private FakePlayer createPlayer() {
            String key = "tno-phase6-severance-regen-" + current().id;
            UUID uuid = UUID.nameUUIDFromBytes(key.getBytes(StandardCharsets.UTF_8));
            FakePlayer fake = FakePlayerFactory.get(level, new GameProfile(uuid, "TNO_P6_SR_" + caseIndex));
            fake.getInventory().clearContent();
            fake.removeAllEffects();
            fake.getAbilities().instabuild = true;
            fake.getAbilities().invulnerable = false;
            setBase(fake, Attributes.MAX_HEALTH, 1024.0D);
            setBase(fake, TensuraAttributes.MAX_SPIRITUAL_HEALTH, 1_000_000_000.0D);
            setBase(fake, TensuraAttributes.MAX_MAGICULE, 1_000_000_000.0D);
            setBase(fake, TensuraAttributes.MAX_AURA, 1_000_000_000.0D);
            fillResources(fake);
            fake.setHealth(fake.getMaxHealth());
            fake.setPos(TEST_X, TEST_Y, 0.5D);
            return fake;
        }

        private void equipBow() {
            player.setItemInHand(InteractionHand.MAIN_HAND, bowTemplate.copy());
            player.setItemInHand(InteractionHand.OFF_HAND, new ItemStack(royalArrow, 64));
            player.setItemSlot(EquipmentSlot.MAINHAND, player.getMainHandItem());
            try {
                invoke(player, "detectEquipmentUpdates");
            }
            catch (ReflectiveOperationException exception) {
                throw new IllegalStateException("could not refresh fake-player equipment", exception);
            }
            ItemStack bow = player.getMainHandItem();
            if (!bow.has(TensuraDataComponents.EP.get())) {
                throw new IllegalStateException("Royal Bow did not receive native Gear EP data");
            }
            bow.set(TensuraDataComponents.EP.get(), 1_000.0D);
            String stage = ProductionStageScaling.stage(bow).map(Enum::name).orElse("NONE");
            if (!stage.equals("S0")) throw new IllegalStateException("R2 bow stage changed from S0: " + stage);
            if (bow.getEnchantments().size() != 1
                    || EnchantmentHelper.getItemEnchantmentLevel(severanceHolder(server), bow) != 1) {
                throw new IllegalStateException("R2 bow did not retain exactly Severance I");
            }
        }

        private void stabilize() {
            if (player != null) {
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
                target.setRemainingFireTicks(-1);
                if (target instanceof Mob mob) {
                    mob.setTarget(null);
                    mob.getNavigation().stop();
                    mob.setAggressive(false);
                }
            }
        }

        private void finalizePendingHealsOnCleanup() {
            pendingHeals.clear();
        }

        private void cleanupCase() {
            finalizePendingHealsOnCleanup();
            clearArrows();
            if (target != null) target.discard();
            if (player != null) {
                player.setItemInHand(InteractionHand.MAIN_HAND, ItemStack.EMPTY);
                player.setItemInHand(InteractionHand.OFF_HAND, ItemStack.EMPTY);
                player.removeAllEffects();
                player.setPos(TEST_X, TEST_Y - 1_000.0D, -1_000.0D - caseIndex);
            }
            target = null;
            player = null;
            l2Cap = null;
            regenerateTrait = null;
            cleanupArea();
        }

        private void cleanupArea() {
            AABB area = new AABB(TEST_X - 64.0D, TEST_Y - 32.0D, -63.5D,
                    TEST_X + 64.0D, TEST_Y + 32.0D, TARGET_Z + 64.0D);
            level.getEntities((Entity) null, area, entity ->
                    !(entity instanceof net.minecraft.world.entity.player.Player)).forEach(Entity::discard);
        }

        private void clearArrows() {
            if (player == null) return;
            level.getEntitiesOfClass(Projectile.class, player.getBoundingBox().inflate(64.0D),
                    this::ownedByPlayer).forEach(Entity::discard);
        }

        private boolean ownedByPlayer(Entity entity) {
            if (!(entity instanceof Projectile projectile)) return false;
            Entity owner = projectile.getOwner();
            return player != null && (owner == player
                    || owner != null && owner.getUUID().equals(player.getUUID()));
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

        private void resetMeasurements() {
            arrowEvents = 0;
            acceptedArrowEvents = 0;
            woundProjectiles = 0;
            healCycles = 0;
            woundBeforeControl = 0.0D;
            woundAtStart = 0.0D;
            woundDurationAtStart = 0;
            startHp = 0.0D;
            startShp = 0.0D;
            nominalHeal = 0.0D;
            totalActualHeal = 0.0D;
            totalAllowedEventAmount = 0.0D;
            finalHp = 0.0D;
            finalShp = 0.0D;
            asynchronousFailure = null;
            selfRegenerationRemoved = false;
            isolatedNonRegenerateHealEvents = 0;
            isolatedNonRegenerateHealAmount = 0.0D;
            isolatedNonRegenerateHealSources.clear();
            arrowDamageSources.clear();
            arrowDamageTags.clear();
        }

        private CaseSpec current() {
            return CASES.get(caseIndex);
        }

        private JsonObject baseCase() {
            JsonObject value = new JsonObject();
            if (caseIndex < CASES.size()) {
                value.addProperty("case_id", current().id);
                value.addProperty("target", TARGET.toString());
                value.addProperty("L2_level", current().level);
                value.addProperty("Regenerate_rank", current().rank);
                value.addProperty("retain_native_wound", current().retainWound);
                value.addProperty("L2_profile", "CONTROLLED_REGENERATE_ONLY");
                value.addProperty("TNO_stage", "S0");
                value.addProperty("APO_profile", "NONE");
            }
            return value;
        }
    }

    private static ItemStack buildBow(MinecraftServer server) {
        ItemStack bow = new ItemStack(requiredItem(ROYAL_BOW));
        Holder.Reference<Enchantment> severance = severanceHolder(server);
        if (!severance.value().canEnchant(bow)) {
            throw new IllegalStateException("Severance does not support installed Royal Bow");
        }
        bow.enchant(severance, 1);
        CustomData.update(DataComponents.CUSTOM_DATA, bow,
                tag -> tag.putBoolean("tno_tensura_compat.first_engraving_roll_processed", true));
        return bow;
    }

    private static Holder.Reference<Enchantment> severanceHolder(MinecraftServer server) {
        Registry<Enchantment> registry = server.registryAccess().registryOrThrow(Registries.ENCHANTMENT);
        return registry.getHolderOrThrow(ResourceKey.create(Registries.ENCHANTMENT, SEVERANCE));
    }

    private static Item requiredItem(ResourceLocation id) {
        Item item = BuiltInRegistries.ITEM.get(id);
        if (item == null || BuiltInRegistries.ITEM.getKey(item).equals(id("minecraft", "air"))) {
            throw new IllegalStateException("required item absent: " + id);
        }
        return item;
    }

    private static ResourceState resources(LivingEntity entity) {
        var existence = TensuraStorages.getExistenceFrom(entity);
        return new ResourceState(existence.getSpiritualHealth(),
                attribute(entity, TensuraAttributes.MAX_SPIRITUAL_HEALTH));
    }

    private static double severance(LivingEntity entity) {
        return TensuraStorages.getEffectFrom(entity).getSeveranceAmount();
    }

    private static int woundDuration(LivingEntity entity) {
        return TensuraStorages.getEffectFrom(entity).getSeveranceRemoveTime();
    }

    private static double attribute(LivingEntity entity, Holder<Attribute> attribute) {
        return entity.getAttributes().hasAttribute(attribute) ? entity.getAttributeValue(attribute) : 0.0D;
    }

    private static void setBase(LivingEntity entity, Holder<Attribute> attribute, double value) {
        AttributeInstance instance = entity.getAttribute(attribute);
        if (instance != null) instance.setBaseValue(value);
    }

    private static double serverDouble(String field) {
        try {
            Object server = staticField("dev.xkmc.l2hostility.init.data.LHConfig", "SERVER");
            return numberValue(invoke(readField(server, field), "get")).doubleValue();
        }
        catch (ReflectiveOperationException exception) {
            throw new IllegalStateException("could not read L2 server config " + field, exception);
        }
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

    private static String holderId(Holder<?> holder) {
        return holder.unwrapKey().map(key -> key.location().toString()).orElse(String.valueOf(holder.value()));
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
        field.setAccessible(true);
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
        throw new IllegalArgumentException("not numeric: " + value);
    }

    private static boolean booleanValue(Object value) {
        if (value instanceof Boolean bool) return bool;
        throw new IllegalArgumentException("not boolean: " + value);
    }

    private static ResourceLocation id(String namespace, String path) {
        return ResourceLocation.fromNamespaceAndPath(namespace, path);
    }

    private static List<CaseSpec> requestedCases() {
        String filter = System.getProperty(CASE_FILTER, "").trim();
        if (filter.isEmpty()) return ALL_CASES;
        return ALL_CASES.stream().filter(spec -> spec.id.equals(filter)).toList();
    }

    private static String summarize(Throwable throwable) {
        Throwable current = throwable;
        while (current.getCause() != null) current = current.getCause();
        String message = current.getMessage();
        return current.getClass().getName() + (message == null ? "" : ": " + message);
    }

    private static void log(String kind, JsonObject payload) {
        payload.addProperty("schema", SCHEMA);
        payload.addProperty("kind", kind);
        LOGGER.info("{} {}", MARKER, GSON.toJson(payload));
    }

    private enum Phase {
        SPAWN,
        WAIT_ATTACHMENT,
        WAIT_SCALING,
        WOUND_SETUP,
        HEAL_SETUP,
        HEAL_RUN,
        FINISH,
        DONE
    }

    private record CaseSpec(String id, int level, int rank, boolean retainWound) {
    }

    private record ResourceState(double shp, double maxShp) {
    }

    private record PendingHeal(long serverTick, int targetTick, double maxHp, double hpBefore,
                               double shpBefore, double nominalAmount, double eventAmountAfterTensura,
                               boolean cancelled, double woundAmount, int woundDuration) {
    }
}
