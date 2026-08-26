package com.tno.tensuracompat.debug;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.mojang.brigadier.Command;
import com.mojang.brigadier.context.CommandContext;
import com.mojang.logging.LogUtils;
import com.mojang.authlib.GameProfile;
import io.github.manasmods.tensura.registry.attribute.TensuraAttributes;
import io.github.manasmods.tensura.storage.TensuraStorages;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.core.Holder;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.HumanoidArm;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.item.BowItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.component.Unbreakable;
import net.minecraft.world.item.enchantment.Enchantment;
import net.minecraft.world.phys.Vec3;
import net.minecraft.core.NonNullList;
import net.neoforged.fml.ModList;
import net.neoforged.fml.loading.FMLEnvironment;
import net.neoforged.neoforge.common.util.FakePlayer;
import net.neoforged.neoforge.common.util.FakePlayerFactory;
import net.neoforged.neoforge.event.entity.living.LivingDamageEvent;
import net.neoforged.neoforge.event.entity.living.LivingIncomingDamageEvent;
import net.neoforged.neoforge.event.server.ServerStartedEvent;
import net.neoforged.neoforge.event.tick.ServerTickEvent;
import org.slf4j.Logger;

import java.lang.reflect.Constructor;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Comparator;
import java.util.IdentityHashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;

/** Development-only, opt-in live combat harness for the Phase 5F APO profiles. */
public final class Phase5FApotheosisBenchmark {
    private static final Logger LOGGER = LogUtils.getLogger();
    private static final Gson GSON = new GsonBuilder().disableHtmlEscaping().create();
    private static final String MARKER = "TNO_PHASE5F_APO_BENCH";
    private static final ResourceLocation ROYAL_BOW = id("royalvariations", "royal_bow");
    private static final ResourceLocation CONTROL_TARGET = id("minecraft", "armor_stand");
    private static final int SAMPLE_SHOTS = Integer.getInteger("tno.phase5f.apoSampleShots", 80);
    private static final int SHOT_WINDOW_TICKS = 8;
    private static final int SUSTAINED_TICKS = Integer.getInteger("tno.phase5f.apoSustainedTicks", 400);
    private static final double TEST_X = 0.5D;
    private static final double TEST_Y = 240.0D;
    private static final double TARGET_Z = 20.5D;

    private static final String AFFIX_HELPER = "dev.shadowsoffire.apotheosis.affix.AffixHelper";
    private static final String AFFIX_INSTANCE = "dev.shadowsoffire.apotheosis.affix.AffixInstance";
    private static final String AFFIX_REGISTRY = "dev.shadowsoffire.apotheosis.affix.AffixRegistry";
    private static final String RARITY_REGISTRY = "dev.shadowsoffire.apotheosis.loot.RarityRegistry";
    private static final String SOCKET_HELPER = "dev.shadowsoffire.apotheosis.socket.SocketHelper";
    private static final String GEM_REGISTRY = "dev.shadowsoffire.apotheosis.socket.gem.GemRegistry";
    private static final String PURITY = "dev.shadowsoffire.apotheosis.socket.gem.Purity";
    private static final String L2_MISCS = "dev.xkmc.l2hostility.init.registrate.LHMiscs";

    private static final List<ResourceLocation> ENCHANTMENTS = List.of(
            id("apothic_enchanting", "endless_quiver"),
            id("apothicnightmares", "spatial_bow"),
            id("l2complements", "soul_bound"),
            id("l2complements", "transparent"),
            id("l2hostility", "vanish"),
            id("minecraft", "flame"),
            id("minecraft", "power"),
            id("minecraft", "punch"),
            id("tensura", "barrier_piercing")
    );

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

    private static final List<ResourceLocation> ANCIENT_BASICS = List.of(
            id("ancientreforging", "ranged/mob_effect/acidic"),
            id("ancientreforging", "ranged/mob_effect/deathbound"),
            id("ancientreforging", "ranged/mob_effect/ivy_laced")
    );
    private static final ResourceLocation ANCIENT_MAGICAL = id("ancientreforging", "ranged/magical");
    private static final ResourceLocation ANCIENT_SPECTRAL = id("ancientreforging", "ranged/spectral");
    private static final ResourceLocation ANCIENT_PROSPEROUS =
            id("ancientreforging", "ranged/enchantment/prosperous");
    private static final ResourceLocation ANCIENT_PIERCING =
            id("ancientreforging", "melee/attribute/piercing");
    private static final ResourceLocation ANCIENT_AGILE =
            id("ancientreforging", "ranged/attribute/agile");
    private static final ResourceLocation ANCIENT_SHREDDING =
            id("ancientreforging", "weapon/attribute/shredding");
    private static final List<ResourceLocation> GENESIS_STATS = List.of(
            id("apothicnightmares", "ranged/attribute/earth_volley"),
            id("apothicnightmares", "ranged/attribute/flame_volley"),
            id("apothicnightmares", "ranged/attribute/spatial_archery"),
            id("apothicnightmares", "ranged/attribute/water_volley"),
            id("apothicnightmares", "ranged/attribute/wind_volley")
    );
    private static final ResourceLocation GENESIS_BASIC =
            id("apothicnightmares", "ranged/mob_effect/crippling_shot");

    private static Session active;

    private Phase5FApotheosisBenchmark() {
    }

    public static int start(CommandContext<CommandSourceStack> context) {
        CommandSourceStack source = context.getSource();
        if (FMLEnvironment.production) {
            source.sendFailure(Component.literal("Phase 5F benchmark is disabled in production."));
            return 0;
        }
        if (active != null) {
            source.sendFailure(Component.literal("Phase 5F APO benchmark is already running."));
            return 0;
        }
        try {
            requireMods();
            active = new Session(source.getServer());
            source.sendSuccess(() -> Component.literal(MARKER + " started; output is written to the server log."), false);
            return Command.SINGLE_SUCCESS;
        }
        catch (Throwable throwable) {
            LOGGER.error("{} startup failed", MARKER, throwable);
            source.sendFailure(Component.literal(MARKER + " startup failed: " + summarize(throwable)));
            return 0;
        }
    }

    public static void onServerTick(ServerTickEvent.Post event) {
        Session session = active;
        if (session == null) return;
        try {
            session.tick();
            if (session.complete) {
                active = null;
                if (Boolean.getBoolean("tno.phase5f.apoBenchmark")) event.getServer().halt(false);
            }
        }
        catch (Throwable throwable) {
            LOGGER.error("{} runtime failure", MARKER, throwable);
            session.cleanup();
            active = null;
        }
    }

    public static void onServerStarted(ServerStartedEvent event) {
        if (FMLEnvironment.production || !Boolean.getBoolean("tno.phase5f.apoBenchmark") || active != null) return;
        try {
            requireMods();
            active = new Session(event.getServer());
            LOGGER.info("{} automatic benchmark started", MARKER);
        }
        catch (Throwable throwable) {
            LOGGER.error("{} automatic startup failed", MARKER, throwable);
        }
    }

    public static void onIncomingDamage(LivingIncomingDamageEvent event) {
        Session session = active;
        if (session != null) session.captureIncoming(event);
    }

    public static void onIncomingBeforeCrit(LivingIncomingDamageEvent event) {
        Session session = active;
        if (session != null) session.captureBeforeCrit(event);
    }

    public static void onIncomingAfterCrit(LivingIncomingDamageEvent event) {
        Session session = active;
        if (session != null) session.captureAfterCrit(event);
    }

    public static void onDamagePost(LivingDamageEvent.Post event) {
        Session session = active;
        if (session != null) session.capturePost(event);
    }

    private static void requireMods() {
        for (String mod : List.of("royalvariations", "apotheosis", "apothic_attributes",
                "ancientreforging", "apothicnightmares")) {
            if (!ModList.get().isLoaded(mod)) throw new IllegalStateException("required benchmark mod absent: " + mod);
        }
    }

    private static final class Session {
        private final MinecraftServer server;
        private final ServerLevel level;
        private FakePlayer player;
        private final List<Profile> profiles;
        private final List<ProfileResult> results = new ArrayList<>();
        private LivingEntity target;
        private final Map<LivingIncomingDamageEvent, Float> beforeCrit = new IdentityHashMap<>();
        private int profileIndex;
        private int shotIndex;
        private int phaseTick;
        private Phase phase = Phase.SETUP_PROFILE;
        private Shot currentShot;
        private ProfileResult currentResult;
        private long sustainedStartTick;
        private long nextSustainedShot;
        private int sustainedShots;
        private JsonObject smokeReport;
        private Object smokeCap;
        private boolean complete;

        Session(MinecraftServer server) throws ReflectiveOperationException {
            this.server = server;
            this.level = server.overworld();
            this.player = createBenchmarkPlayer(-1);
            String filter = System.getProperty("tno.phase5f.apoProfileFilter", "");
            this.profiles = buildProfiles(server).stream()
                    .filter(profile -> filter.isBlank() || profile.name.equals(filter))
                    .toList();
            if (profiles.isEmpty()) throw new IllegalStateException("benchmark profile filter matched no profiles: " + filter);
            logCandidateCatalog();
        }

        void tick() throws ReflectiveOperationException {
            keepTestEntitiesStable();
            switch (phase) {
                case SETUP_PROFILE -> setupProfile();
                case SAMPLE_LAUNCH -> launchSample();
                case SAMPLE_WAIT -> waitForSample();
                case SUSTAINED_SETUP -> setupSustained();
                case SUSTAINED_RUN -> runSustained();
                case FINISH_PROFILE -> finishProfile();
                case L2_SMOKE -> runL2Smoke();
                case DONE -> {
                    cleanup();
                    complete = true;
                }
            }
        }

        private void setupProfile() throws ReflectiveOperationException {
            if (profileIndex >= profiles.size()) {
                logOfficialProfiles();
                phaseTick = 0;
                phase = Phase.L2_SMOKE;
                return;
            }
            Profile profile = profiles.get(profileIndex);
            player = createBenchmarkPlayer(profileIndex);
            equip(profile.stack);
            target = createControlTarget();
            resetTarget(true);
            currentResult = new ProfileResult(profile, readAttributes(player), fullDrawTicks(player));
            shotIndex = 0;
            phaseTick = 0;
            phase = Phase.SAMPLE_LAUNCH;
            log("profile_start", profileJson(profile, currentResult.attributes, currentResult.fullDrawTicks));
        }

        private void launchSample() {
            if (shotIndex >= SAMPLE_SHOTS) {
                phase = Phase.SUSTAINED_SETUP;
                return;
            }
            if (target == null || target.isRemoved()) {
                throw new IllegalStateException("control target was removed during sample collection");
            }
            resetTarget(true);
            clearArrows();
            beforeCrit.clear();
            currentShot = new Shot(shotIndex);
            fireFullDraw();
            phaseTick = 0;
            phase = Phase.SAMPLE_WAIT;
        }

        private void waitForSample() {
            if (++phaseTick < Math.max(SHOT_WINDOW_TICKS, currentResult.fullDrawTicks)) return;
            currentResult.samples.add(currentShot);
            currentShot = null;
            shotIndex++;
            phase = Phase.SAMPLE_LAUNCH;
        }

        private void setupSustained() {
            player = createBenchmarkPlayer(profileIndex + 1_000);
            equip(currentResult.profile.stack);
            resetTarget(true);
            clearArrows();
            currentResult.sustainedIncoming = 0.0D;
            currentResult.sustainedPost = 0.0D;
            currentResult.sustainedEvents = 0;
            currentResult.sustainedPreCrit = 0.0D;
            currentResult.sustainedPreCritEvents = 0;
            sustainedShots = 0;
            sustainedStartTick = server.getTickCount();
            nextSustainedShot = sustainedStartTick;
            phase = Phase.SUSTAINED_RUN;
        }

        private void runSustained() {
            long elapsed = server.getTickCount() - sustainedStartTick;
            if (elapsed >= SUSTAINED_TICKS) {
                phase = Phase.FINISH_PROFILE;
                return;
            }
            resetTarget(false);
            if (server.getTickCount() >= nextSustainedShot) {
                // Previous misses are outside the current release's damage window and must not
                // contaminate collision/ownership state for the next controlled shot.
                clearArrows();
                fireFullDraw();
                sustainedShots++;
                nextSustainedShot += currentResult.fullDrawTicks;
            }
        }

        private void finishProfile() {
            currentResult.sustainedShots = sustainedShots;
            results.add(currentResult);
            log("profile_result", currentResult.toJson());
            target.discard();
            target = null;
            currentResult = null;
            profileIndex++;
            phase = Phase.SETUP_PROFILE;
        }

        private void logOfficialProfiles() {
            ProfileResult single = results.stream()
                    .max(Comparator.comparingDouble(ProfileResult::meanCritHit)
                            .thenComparingDouble(ProfileResult::meanHit))
                    .orElseThrow();
            ProfileResult sustained = results.stream()
                    .max(Comparator.comparingDouble(ProfileResult::sustainedDps)).orElseThrow();
            JsonObject report = new JsonObject();
            report.addProperty("MAX_APO_SINGLE_HIT", single.profile.name);
            report.addProperty("single_hit_selection_metric", "mean post-mitigation damage of critical released shots");
            report.addProperty("single_hit_mean_crit", single.meanCritHit());
            report.addProperty("single_hit_mean_all_shots", single.meanHit());
            report.addProperty("MAX_APO_SUSTAINED", sustained.profile.name);
            report.addProperty("sustained_dps", sustained.sustainedDps());
            report.addProperty("same_build_wins_both", single == sustained);
            log("official_profiles", report);
        }

        private void captureIncoming(LivingIncomingDamageEvent event) {
            if (event.getEntity() != target) return;
            if (phase == Phase.SUSTAINED_RUN) {
                currentResult.sustainedIncoming += event.getAmount();
                currentResult.sustainedEvents++;
                return;
            }
            if (!fromBenchmarkPlayer(event.getSource().getEntity())) return;
            boolean projectile = event.getSource().getDirectEntity() instanceof AbstractArrow;
            if ((phase == Phase.SAMPLE_WAIT || phase == Phase.L2_SMOKE) && projectile && currentShot != null) {
                currentShot.incoming.add((double) event.getAmount());
                currentShot.original.add((double) event.getOriginalAmount());
            }
            beforeCrit.remove(event);
        }

        private void captureBeforeCrit(LivingIncomingDamageEvent event) {
            if (event.getEntity() != target || !fromBenchmarkPlayer(event.getSource().getEntity())) return;
            if (!(event.getSource().getDirectEntity() instanceof AbstractArrow)) return;
            if (phase == Phase.SUSTAINED_RUN) {
                currentResult.sustainedPreCrit += event.getAmount();
                currentResult.sustainedPreCritEvents++;
            }
            else if ((phase == Phase.SAMPLE_WAIT || phase == Phase.L2_SMOKE) && currentShot != null) {
                currentShot.preCrit.add((double) event.getAmount());
                beforeCrit.put(event, event.getAmount());
            }
        }

        private void captureAfterCrit(LivingIncomingDamageEvent event) {
            Float before = beforeCrit.get(event);
            if (before != null && currentShot != null && event.getAmount() > before + 0.001F) {
                currentShot.criticalEvents++;
            }
        }

        private void capturePost(LivingDamageEvent.Post event) {
            if (event.getEntity() != target) return;
            if (phase == Phase.SUSTAINED_RUN) {
                currentResult.sustainedPost += event.getNewDamage();
                restoreControlTargetHealth();
                return;
            }
            if (!fromBenchmarkPlayer(event.getSource().getEntity())) return;
            boolean projectile = event.getSource().getDirectEntity() instanceof AbstractArrow;
            if ((phase == Phase.SAMPLE_WAIT || phase == Phase.L2_SMOKE) && projectile && currentShot != null) {
                currentShot.post.add((double) event.getNewDamage());
            }
            restoreControlTargetHealth();
        }

        private boolean fromBenchmarkPlayer(Entity owner) {
            return owner == player || owner != null && owner.getUUID().equals(player.getUUID());
        }

        private FakePlayer createBenchmarkPlayer(int index) {
            String key = "tno-phase5f-apo-" + index;
            UUID uuid = UUID.nameUUIDFromBytes(key.getBytes(StandardCharsets.UTF_8));
            FakePlayer fresh = FakePlayerFactory.get(level, new GameProfile(uuid, "TNO_P5F_" + index));
            fresh.getInventory().clearContent();
            fresh.getAbilities().instabuild = true;
            fresh.setPos(TEST_X, TEST_Y, 0.5D);
            fresh.setYRot(0.0F);
            fresh.setYHeadRot(0.0F);
            fresh.setXRot(0.0F);
            return fresh;
        }

        private void equip(ItemStack stack) {
            player.getInventory().clearContent();
            player.setItemInHand(InteractionHand.MAIN_HAND, stack.copy());
            player.setItemInHand(InteractionHand.OFF_HAND, new ItemStack(Items.ARROW, 64));
            player.setItemSlot(EquipmentSlot.MAINHAND, player.getMainHandItem());
            try {
                invoke(player, "detectEquipmentUpdates");
            }
            catch (ReflectiveOperationException exception) {
                throw new IllegalStateException("could not refresh fake-player equipment attributes", exception);
            }
        }

        private void fireFullDraw() {
            // Volley affixes can consume several arrows per release. Replenish the controlled
            // vanilla-arrow supply so long distributions never change ammo state or arrow type.
            player.setItemInHand(InteractionHand.OFF_HAND, new ItemStack(Items.ARROW, 64));
            List<UUID> existing = level.getEntitiesOfClass(AbstractArrow.class,
                    player.getBoundingBox().inflate(64.0D), arrow -> fromBenchmarkPlayer(arrow.getOwner()))
                    .stream().map(Entity::getUUID).toList();
            ItemStack bow = player.getMainHandItem();
            int remaining = bow.getUseDuration(player) - fullDrawTicks(player);
            bow.releaseUsing(level, player, remaining);
            List<AbstractArrow> spawned = level.getEntitiesOfClass(AbstractArrow.class,
                    player.getBoundingBox().inflate(64.0D),
                    arrow -> fromBenchmarkPlayer(arrow.getOwner()) && !existing.contains(arrow.getUUID()));
            if (spawned.isEmpty()) throw new IllegalStateException("full-draw release did not create a benchmark arrow");
            if (target == null || target.isRemoved()) {
                throw new IllegalStateException("cannot aim benchmark arrow at a missing target");
            }
            Vec3 aim = target.getBoundingBox().getCenter();
            for (AbstractArrow arrow : spawned) {
                double speed = arrow.getDeltaMovement().length();
                Vec3 direction = aim.subtract(arrow.position()).normalize();
                arrow.setDeltaMovement(direction.scale(speed));
                arrow.hasImpulse = true;
            }
        }

        private LivingEntity createControlTarget() {
            LivingEntity mob = new NeutralArmorStandTarget(level);
            mob.setPos(TEST_X, TEST_Y, TARGET_Z);
            mob.setNoGravity(true);
            mob.setSilent(true);
            setBase(mob, Attributes.MAX_HEALTH, 1024.0D);
            // Full netherite contributes 20 armor and 12 toughness, yielding 50/24 total.
            setBase(mob, Attributes.ARMOR, 30.0D);
            setBase(mob, Attributes.ARMOR_TOUGHNESS, 12.0D);
            equipProtection(mob);
            level.addFreshEntity(mob);
            setBase(mob, TensuraAttributes.MAX_SPIRITUAL_HEALTH, 1_000_000_000.0D);
            return mob;
        }

        private void equipProtection(LivingEntity mob) {
            Holder.Reference<Enchantment> protection = enchantment(server, id("minecraft", "protection"));
            for (Map.Entry<EquipmentSlot, Item> entry : Map.of(
                    EquipmentSlot.HEAD, Items.NETHERITE_HELMET,
                    EquipmentSlot.CHEST, Items.NETHERITE_CHESTPLATE,
                    EquipmentSlot.LEGS, Items.NETHERITE_LEGGINGS,
                    EquipmentSlot.FEET, Items.NETHERITE_BOOTS).entrySet()) {
                ItemStack armor = new ItemStack(entry.getValue());
                armor.enchant(protection, protection.value().getMaxLevel());
                armor.set(DataComponents.UNBREAKABLE, new Unbreakable(false));
                mob.setItemSlot(entry.getKey(), armor);
            }
        }

        private void resetTarget(boolean clearEffects) {
            if (target == null || target.isRemoved()) return;
            if (target instanceof NeutralArmorStandTarget) restoreControlTargetHealth();
            else target.setHealth(target.getMaxHealth());
            target.setAbsorptionAmount(0.0F);
            target.invulnerableTime = 0;
            target.setRemainingFireTicks(0);
            if (clearEffects) {
                for (MobEffectInstance effect : List.copyOf(target.getActiveEffects())) {
                    target.removeEffect(effect.getEffect());
                }
            }
            try {
                TensuraStorages.getExistenceFrom(target).setSpiritualHealth(1_000_000_000.0D);
            }
            catch (Throwable ignored) {
            }
        }

        private void restoreControlTargetHealth() {
            if (target instanceof NeutralArmorStandTarget) target.setHealth(1_000_000.0F);
        }

        private void keepTestEntitiesStable() {
            player.setPos(TEST_X, TEST_Y, 0.5D);
            player.setYRot(0.0F);
            player.setYHeadRot(0.0F);
            if (target != null && !target.isRemoved()) {
                Vec3 aim = target.getBoundingBox().getCenter();
                double horizontal = Math.hypot(aim.x - player.getX(), aim.z - player.getZ());
                player.setXRot((float) -Math.toDegrees(Math.atan2(aim.y - player.getEyeY(), horizontal)));
            }
            else player.setXRot(0.0F);
            if (target != null && !target.isRemoved()) {
                target.setPos(TEST_X, TEST_Y, TARGET_Z);
                target.setDeltaMovement(0.0D, 0.0D, 0.0D);
            }
        }

        private void clearArrows() {
            level.getEntitiesOfClass(AbstractArrow.class, player.getBoundingBox().inflate(64.0D),
                    arrow -> fromBenchmarkPlayer(arrow.getOwner())).forEach(Entity::discard);
        }

        private void runL2Smoke() throws ReflectiveOperationException {
            if (phaseTick > 0) {
                if (smokeCap == null) {
                    if (++phaseTick < 4) return;
                    Object attachmentType = invoke(staticField(L2_MISCS, "MOB"), "type");
                    if (!booleanValue(invoke(attachmentType, "isProper", target))) {
                        smokeReport.addProperty("status", "fallback_rejected_by_l2_predicate");
                        log("l2_smoke", smokeReport);
                        phase = Phase.DONE;
                        return;
                    }
                    smokeCap = invoke(attachmentType, "getOrCreate", target);
                    // This is L2's normal reroll path at a requested base level. The false flag
                    // preserves normal trait chances instead of forcing a full-chance package.
                    invoke(smokeCap, "reinit", target, 300, false);
                    invoke(smokeCap, "setLevel", target, 300);
                    if (target instanceof Mob controlledMob) controlledMob.setNoAi(true);
                    player = createBenchmarkPlayer(10_000);
                    ProfileResult winner = results.stream()
                            .max(Comparator.comparingDouble(ProfileResult::sustainedDps)).orElseThrow();
                    equip(winner.profile.stack);
                    target.setHealth(target.getMaxHealth());
                    target.setAbsorptionAmount(0.0F);
                    target.invulnerableTime = 0;
                    target.setRemainingFireTicks(0);
                    if (target.getType() == EntityType.WITHER) {
                        invoke(target, "setInvulnerableTicks", 0);
                    }
                    currentShot = new Shot(0);
                    fireFullDraw();
                    smokeReport.addProperty("status", "ok");
                    ResourceLocation targetId = BuiltInRegistries.ENTITY_TYPE.getKey(target.getType());
                    smokeReport.addProperty("entity", targetId.toString());
                    smokeReport.addProperty("tensura_integration",
                            "Tensura entity_existence data exists for " + targetId);
                    phaseTick = 100;
                    return;
                }
                if (++phaseTick < 112) return;
                smokeReport.addProperty("l2_initialized", booleanValue(invoke(smokeCap, "isInitialized")));
                smokeReport.addProperty("l2_level", numberValue(invoke(smokeCap, "getLevel")).intValue());
                smokeReport.addProperty("forced_traits", false);
                smokeReport.addProperty("trait_count", ((Map<?, ?>) readField(smokeCap, "traits")).size());
                smokeReport.addProperty("bow_direct_events", currentShot == null ? 0 : currentShot.incoming.size());
                smokeReport.addProperty("bow_post_damage",
                        currentShot == null ? 0.0D : currentShot.total(currentShot.post));
                smokeReport.add("bow_attributes", readAttributes(player));
                log("l2_smoke", smokeReport);
                if (target != null) target.discard();
                target = null;
                currentShot = null;
                smokeReport = null;
                smokeCap = null;
                phaseTick = 0;
                phase = Phase.DONE;
                return;
            }
            ProfileResult winner = results.stream()
                    .max(Comparator.comparingDouble(ProfileResult::sustainedDps)).orElseThrow();
            JsonObject report = new JsonObject();
            report.addProperty("winning_profile", winner.profile.name);
            report.addProperty("preferred_entity", "tensura_neb:luminous_valentine");
            Object mobEntry = staticField(L2_MISCS, "MOB");
            Object attachmentType = invoke(mobEntry, "type");
            LivingEntity boss = null;
            for (ResourceLocation bossId : List.of(
                    id("tensura_neb", "luminous_valentine"),
                    id("tensura_neb", "carrion"),
                    id("tensura_neb", "rimuru_ogre_fight"),
                    id("tensura_neb", "veldora"),
                    id("minecraft", "wither"))) {
                if (!BuiltInRegistries.ENTITY_TYPE.containsKey(bossId)) continue;
                Entity entity = BuiltInRegistries.ENTITY_TYPE.get(bossId).create(level);
                if (!(entity instanceof LivingEntity candidate)) continue;
                candidate.setPos(TEST_X, TEST_Y, TARGET_Z);
                candidate.setNoGravity(true);
                candidate.setSilent(true);
                level.addFreshEntity(candidate);
                if (booleanValue(invoke(attachmentType, "isProper", candidate))) {
                    boss = candidate;
                    break;
                }
                if (bossId.equals(id("tensura_neb", "luminous_valentine"))) {
                    report.addProperty("preferred_entity_status",
                            "rejected by the live L2 attachment predicate: Luminous is neither Enemy nor in l2hostility:whitelist");
                }
                candidate.discard();
            }
            if (boss == null) {
                report.addProperty("status", "no_l2_eligible_tensura_target");
                log("l2_smoke", report);
                phase = Phase.DONE;
                return;
            }
            target = boss;
            smokeReport = report;
            smokeCap = null;
            phaseTick = 1;
        }

        private void cleanup() {
            clearArrows();
            if (target != null) target.discard();
            player.setItemInHand(InteractionHand.MAIN_HAND, ItemStack.EMPTY);
        }

        private void logCandidateCatalog() throws ReflectiveOperationException {
            JsonObject report = new JsonObject();
            report.addProperty("sample_shots_per_profile", SAMPLE_SHOTS);
            report.addProperty("sustained_ticks", SUSTAINED_TICKS);
            report.addProperty("target", CONTROL_TARGET.toString());
            report.addProperty("distance", TARGET_Z - 0.5D);
            report.addProperty("target_armor", 50.0D);
            report.addProperty("target_toughness", 24.0D);
            report.addProperty("target_equipment", "neutral LivingEntity adapter using minecraft:armor_stand type; full_netherite");
            report.addProperty("target_protection", "minecraft:protection IV on four pieces");
            report.addProperty("arrow", "minecraft:arrow");
            report.addProperty("draw", "full (attribute-adjusted use ticks recorded per profile)");
            report.addProperty("tno_scalable_data", "absent/default; no TNO engraving applied");
            JsonArray profileArray = new JsonArray();
            for (Profile profile : profiles) profileArray.add(profileJson(profile, readStackAttributes(profile.stack), -1));
            report.add("profiles", profileArray);
            log("catalog", report);
        }
    }

        private static List<Profile> buildProfiles(MinecraftServer server) throws ReflectiveOperationException {
        List<ProfileSpec> specs = List.of(
                genesis("GENESIS_SINGLE_CRITICAL_FOCUS", false,
                        List.of("core/combatant", "core/breach", "core/lightning", "core/warlord",
                                "core/samurai", "overworld/verdant_ruin")),
                genesis("GENESIS_SINGLE_WARP_FLETCHING", true,
                        List.of("core/combatant", "core/breach", "core/lightning", "core/warlord",
                                "core/samurai", "overworld/verdant_ruin")),
                genesis("GENESIS_SUSTAINED_CRITICAL_FOCUS", false,
                        List.of("core/combatant", "core/breach", "core/lightning", "core/slipstream",
                                "core/samurai", "overworld/verdant_ruin")),
                genesis("GENESIS_SUSTAINED_WARP_FLETCHING", true,
                        List.of("core/combatant", "core/breach", "core/lightning", "core/slipstream",
                                "core/samurai", "overworld/verdant_ruin")),
                ancient("ANCIENT_SINGLE_MAGICAL_SPECTRAL", ANCIENT_PIERCING,
                        List.of("core/combatant", "core/breach", "core/lightning", "core/warlord", "core/warlord"),
                        List.of(ANCIENT_MAGICAL, ANCIENT_SPECTRAL)),
                ancient("ANCIENT_SINGLE_PROSPEROUS_SPECTRAL", ANCIENT_PIERCING,
                        List.of("core/combatant", "core/breach", "core/lightning", "core/warlord", "core/warlord"),
                        List.of(ANCIENT_PROSPEROUS, ANCIENT_SPECTRAL)),
                ancient("ANCIENT_SINGLE_PROSPEROUS_SPECTRAL_VERDANT", ANCIENT_PIERCING,
                        List.of("core/combatant", "core/breach", "core/lightning", "core/warlord",
                                "overworld/verdant_ruin"),
                        List.of(ANCIENT_PROSPEROUS, ANCIENT_SPECTRAL)),
                ancient("ANCIENT_SINGLE_PROSPEROUS_SPECTRAL_MOLTEN", ANCIENT_PIERCING,
                        List.of("core/combatant", "core/breach", "core/lightning", "core/warlord",
                                "the_nether/molten_breach"),
                        List.of(ANCIENT_PROSPEROUS, ANCIENT_SPECTRAL)),
                ancient("ANCIENT_SINGLE_PROSPEROUS_SPECTRAL_SHREDDING", ANCIENT_SHREDDING,
                        List.of("core/combatant", "core/breach", "core/lightning", "core/warlord", "core/warlord"),
                        List.of(ANCIENT_PROSPEROUS, ANCIENT_SPECTRAL)),
                ancient("ANCIENT_SUSTAINED_PROSPEROUS_SPECTRAL_WARLORD", ANCIENT_AGILE,
                        List.of("core/combatant", "core/breach", "core/lightning", "core/slipstream", "core/warlord"),
                        List.of(ANCIENT_PROSPEROUS, ANCIENT_SPECTRAL)),
                ancient("ANCIENT_SUSTAINED_PROSPEROUS_SPECTRAL_TYRANNICAL", ANCIENT_AGILE,
                        List.of("core/combatant", "core/breach", "core/lightning", "core/slipstream", "core/tyrannical"),
                        List.of(ANCIENT_PROSPEROUS, ANCIENT_SPECTRAL)),
                ancient("ANCIENT_SUSTAINED_MAGICAL_SPECTRAL_WARLORD", ANCIENT_AGILE,
                        List.of("core/combatant", "core/breach", "core/lightning", "core/slipstream", "core/warlord"),
                        List.of(ANCIENT_MAGICAL, ANCIENT_SPECTRAL)),
                ancient("ANCIENT_SUSTAINED_PIERCING_WARLORD", ANCIENT_PIERCING,
                        List.of("core/combatant", "core/breach", "core/lightning", "core/slipstream", "core/warlord"),
                        List.of(ANCIENT_PROSPEROUS, ANCIENT_SPECTRAL)),
                ancient("ANCIENT_SUSTAINED_SHREDDING_WARLORD", ANCIENT_SHREDDING,
                        List.of("core/combatant", "core/breach", "core/lightning", "core/slipstream", "core/warlord"),
                        List.of(ANCIENT_PROSPEROUS, ANCIENT_SPECTRAL))
        );
        List<Profile> profiles = new ArrayList<>();
        for (ProfileSpec spec : specs) profiles.add(construct(server, spec));
        return profiles;
    }

    private static ProfileSpec genesis(String name, boolean warp, List<String> gems) {
        List<ResourceLocation> affixes = new ArrayList<>(GENESIS_STATS);
        affixes.add(id("apothicnightmares", warp
                ? "ranged/attribute/warp_fletching" : "ranged/attribute/critical_focus"));
        affixes.add(GENESIS_BASIC);
        return new ProfileSpec(name, id("apothicnightmares", "genesis_grade"), affixes,
                gemIds(gems), 6, "5 stat + 1 ability + 1 basic (two declared basic slots unsatisfiable)");
    }

    private static ProfileSpec ancient(String name, ResourceLocation fifthStat, List<String> gems,
            List<ResourceLocation> abilities) {
        List<ResourceLocation> affixes = new ArrayList<>(List.of(
                id("ancientreforging", "ranged/attribute/elven"),
                id("ancientreforging", "ranged/attribute/streamlined"),
                id("ancientreforging", "melee/attribute/lacerating"),
                id("ancientreforging", "melee/attribute/intricate"),
                fifthStat));
        affixes.addAll(ANCIENT_BASICS);
        affixes.addAll(abilities);
        return new ProfileSpec(name, id("ancientreforging", "ancient"), affixes,
                gemIds(gems), 5, "5 stat + 3 basic + 2 ability; all declared slots satisfied");
    }

    private static List<ResourceLocation> gemIds(List<String> paths) {
        return paths.stream().map(path -> id("apotheosis", path)).toList();
    }

    private static Profile construct(MinecraftServer server, ProfileSpec spec) throws ReflectiveOperationException {
        Item item = BuiltInRegistries.ITEM.get(ROYAL_BOW);
        if (item == Items.AIR) throw new IllegalStateException("Royal Bow is not registered");
        ItemStack stack = new ItemStack(item);
        Object rarityRegistry = staticField(RARITY_REGISTRY, "INSTANCE");
        Object rarityHolder = invoke(rarityRegistry, "holder", spec.rarity);
        Object rarity = invoke(rarityHolder, "get");
        callStatic(AFFIX_HELPER, "setRarity", stack, rarity);
        // Both compared rarity recipes have a legitimate low-chance Unbreakable outcome.
        // Select it for the legal maximum stack so an 80-shot distribution never changes
        // item condition partway through the controlled sample.
        stack.set(DataComponents.UNBREAKABLE, new Unbreakable(false));

        Object category = callStatic("dev.shadowsoffire.apotheosis.loot.LootCategory", "forItem", stack);
        Object affixRegistry = staticField(AFFIX_REGISTRY, "INSTANCE");
        Class<?> instanceClass = Class.forName(AFFIX_INSTANCE);
        for (ResourceLocation id : spec.affixes) {
            Object holder = invoke(affixRegistry, "holder", id);
            Object affix = invoke(holder, "get");
            if (!booleanValue(invoke(affix, "canApplyTo", stack, category, rarity))) {
                throw new IllegalStateException(id + " cannot apply to " + spec.rarity);
            }
            Object instance = construct(instanceClass, holder, 1.0F, rarityHolder, stack);
            callStatic(AFFIX_HELPER, "applyAffix", stack, instance);
        }
        callStatic(AFFIX_HELPER, "applySupremacy", stack);
        validateAffixes(stack, spec);

        callStatic(SOCKET_HELPER, "setSockets", stack, spec.sockets);
        Object perfect = staticField(PURITY, "PERFECT");
        Object gemRegistry = staticField(GEM_REGISTRY, "INSTANCE");
        for (ResourceLocation gemId : spec.gems) {
            Object holder = invoke(gemRegistry, "holder", gemId);
            Object gem = invoke(holder, "get");
            ItemStack gemStack = (ItemStack) invoke(gem, "toStack", perfect);
            if (!booleanValue(callStatic(SOCKET_HELPER, "canSocketGemInItem", stack, gemStack))) {
                throw new IllegalStateException(gemId + " cannot be legally socketed in " + spec.name);
            }
            stack = (ItemStack) callStatic(SOCKET_HELPER, "socketGemInItem", stack, gemStack);
        }
        if (numberValue(callStatic(SOCKET_HELPER, "getSockets", stack)).intValue() != spec.sockets) {
            throw new IllegalStateException("socket count changed during construction");
        }

        List<String> enchantments = new ArrayList<>();
        List<Holder<Enchantment>> applied = new ArrayList<>();
        for (ResourceLocation enchantId : ENCHANTMENTS) {
            Holder.Reference<Enchantment> holder = enchantment(server, enchantId);
            if (!holder.value().canEnchant(stack)) throw new IllegalStateException(enchantId + " does not support Royal Bow");
            if (applied.stream().anyMatch(other -> !Enchantment.areCompatible(other, holder))) {
                throw new IllegalStateException(enchantId + " is not compatible with preceding maximum set");
            }
            stack.enchant(holder, holder.value().getMaxLevel());
            applied.add(holder);
            enchantments.add(enchantId + " " + holder.value().getMaxLevel());
        }
        return new Profile(spec.name, spec.rarity, List.copyOf(spec.affixes), List.copyOf(spec.gems),
                spec.sockets, List.copyOf(enchantments), spec.layout, stack);
    }

    private static void validateAffixes(ItemStack stack, ProfileSpec spec) throws ReflectiveOperationException {
        Object value = callStatic(AFFIX_HELPER, "getAffixes", stack);
        if (!(value instanceof Map<?, ?> affixes) || affixes.size() != spec.affixes.size()) {
            throw new IllegalStateException("affix count mismatch for " + spec.name);
        }
        for (Object instance : affixes.values()) {
            float level = numberValue(invoke(instance, "level")).floatValue();
            if (Math.abs(level - 1.5F) > 0.0001F || !booleanValue(invoke(instance, "isValid"))) {
                throw new IllegalStateException("Supremacy/validity failure for " + spec.name + ": " + instance);
            }
        }
    }

    private static Holder.Reference<Enchantment> enchantment(MinecraftServer server, ResourceLocation id) {
        HolderLookup.RegistryLookup<Enchantment> registry = server.registryAccess()
                .lookup(Registries.ENCHANTMENT).orElseThrow();
        return registry.get(ResourceKey.create(Registries.ENCHANTMENT, id)).orElseThrow();
    }

    private static void setBase(LivingEntity entity, Holder<Attribute> attribute, double value) {
        AttributeInstance instance = entity.getAttribute(attribute);
        if (instance != null) instance.setBaseValue(value);
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
            int simulatedTick = ticks;
            if (extra < 0.0D) {
                if (simulatedTick % Math.max(1, (int) Math.floor(1.0D / Math.min(1.0D, -extra))) == 0) advanced = 0;
            }
            else {
                while (extra > 1.0D) {
                    advanced++;
                    extra--;
                }
                if (extra > 0.5D) {
                    if (simulatedTick % 2 == 0) advanced++;
                    extra -= 0.5D;
                }
                if (extra > 0.0D) {
                    int divisor = Math.max(1, (int) Math.floor(1.0D / Math.min(1.0D, extra)));
                    if (simulatedTick % divisor == 0) advanced++;
                }
            }
            progress += advanced;
        }
        return Math.max(1, ticks);
    }

    private static double attribute(LivingEntity entity, ResourceLocation id, double fallback) {
        Optional<Holder.Reference<Attribute>> holder = BuiltInRegistries.ATTRIBUTE.getHolder(id);
        return holder.isPresent() && entity.getAttributes().hasAttribute(holder.get())
                ? entity.getAttributeValue(holder.get()) : fallback;
    }

    private static JsonObject profileJson(Profile profile, JsonObject attributes, int drawTicks) {
        JsonObject json = new JsonObject();
        json.addProperty("name", profile.name);
        json.addProperty("item", ROYAL_BOW.toString());
        json.addProperty("rarity", profile.rarity.toString());
        json.addProperty("layout", profile.layout);
        json.addProperty("supremacy", true);
        json.addProperty("affix_level", 1.5F);
        json.addProperty("sockets", profile.sockets);
        json.add("affixes", strings(profile.affixes));
        json.add("perfect_gems", strings(profile.gems));
        json.add("enchantments", strings(profile.enchantments));
        json.add("attributes", attributes);
        if (drawTicks > 0) json.addProperty("full_draw_ticks", drawTicks);
        return json;
    }

    private static JsonArray strings(Collection<?> values) {
        JsonArray array = new JsonArray();
        values.forEach(value -> array.add(String.valueOf(value)));
        return array;
    }

    private static void log(String kind, JsonObject payload) {
        payload.addProperty("schema", "tno.phase5f.apo_benchmark.v1");
        payload.addProperty("kind", kind);
        LOGGER.info("{} {}", MARKER, GSON.toJson(payload));
    }

    private static Object staticField(String className, String name) throws ReflectiveOperationException {
        return Class.forName(className).getField(name).get(null);
    }

    private static Object callStatic(String className, String name, Object... args) throws ReflectiveOperationException {
        return invoke(Class.forName(className), name, args);
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

    private static Object construct(Class<?> type, Object... args) throws ReflectiveOperationException {
        for (Constructor<?> constructor : type.getConstructors()) {
            if (compatible(constructor.getParameterTypes(), args)) return constructor.newInstance(args);
        }
        throw new NoSuchMethodException(type.getName() + " constructor/" + args.length);
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
        for (Class<?> current = target.getClass(); current != null; current = current.getSuperclass()) {
            try {
                Field field = current.getDeclaredField(name);
                field.setAccessible(true);
                return field.get(target);
            }
            catch (NoSuchFieldException ignored) {
            }
        }
        throw new NoSuchFieldException(target.getClass().getName() + "#" + name);
    }

    private static Optional<Object> optionalValue(Object value) {
        if (value instanceof Optional<?> optional) return optional.map(element -> element);
        return Optional.ofNullable(value);
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
        try {
            return String.valueOf(invoke(holder, "getId"));
        }
        catch (Throwable ignored) {
            return String.valueOf(holder);
        }
    }

    private static String summarize(Throwable throwable) {
        Throwable root = throwable;
        while (root.getCause() != null && root.getCause() != root) root = root.getCause();
        return root.getClass().getSimpleName() + (root.getMessage() == null ? "" : ": " + root.getMessage());
    }

    private static ResourceLocation id(String namespace, String path) {
        return ResourceLocation.fromNamespaceAndPath(namespace, path);
    }

    private enum Phase {
        SETUP_PROFILE, SAMPLE_LAUNCH, SAMPLE_WAIT, SUSTAINED_SETUP, SUSTAINED_RUN,
        FINISH_PROFILE, L2_SMOKE, DONE
    }

    private record ProfileSpec(String name, ResourceLocation rarity, List<ResourceLocation> affixes,
            List<ResourceLocation> gems, int sockets, String layout) {
    }

    private record Profile(String name, ResourceLocation rarity, List<ResourceLocation> affixes,
            List<ResourceLocation> gems, int sockets, List<String> enchantments, String layout, ItemStack stack) {
    }

    /**
     * Vanilla ArmorStand bypasses LivingEntity's damage pipeline and breaks after direct hits.
     * This server-only adapter retains the Armor Stand entity type/dimensions while exercising
     * normal armor, toughness, enchantment, incoming-damage, and post-damage processing.
     */
    private static final class NeutralArmorStandTarget extends LivingEntity {
        private final NonNullList<ItemStack> handItems = NonNullList.withSize(2, ItemStack.EMPTY);
        private final NonNullList<ItemStack> armorItems = NonNullList.withSize(4, ItemStack.EMPTY);

        NeutralArmorStandTarget(ServerLevel level) {
            super(EntityType.ARMOR_STAND, level);
        }

        @Override
        public void setHealth(float health) {
            try {
                Field dataHealth = LivingEntity.class.getDeclaredField("DATA_HEALTH_ID");
                dataHealth.setAccessible(true);
                // Never let a comparison shot transition this reusable diagnostic entity into
                // LivingEntity's death state; the Post event still reports real mitigated damage.
                invoke(getEntityData(), "set", dataHealth.get(null), Math.max(1.0F, health));
            }
            catch (ReflectiveOperationException exception) {
                throw new IllegalStateException("could not set neutral target test health", exception);
            }
        }

        @Override
        public Iterable<ItemStack> getArmorSlots() {
            return armorItems;
        }

        @Override
        public ItemStack getItemBySlot(EquipmentSlot slot) {
            return switch (slot) {
                case MAINHAND -> handItems.get(0);
                case OFFHAND -> handItems.get(1);
                case FEET -> armorItems.get(0);
                case LEGS -> armorItems.get(1);
                case CHEST -> armorItems.get(2);
                case HEAD -> armorItems.get(3);
                default -> ItemStack.EMPTY;
            };
        }

        @Override
        public void setItemSlot(EquipmentSlot slot, ItemStack stack) {
            switch (slot) {
                case MAINHAND -> handItems.set(0, stack);
                case OFFHAND -> handItems.set(1, stack);
                case FEET -> armorItems.set(0, stack);
                case LEGS -> armorItems.set(1, stack);
                case CHEST -> armorItems.set(2, stack);
                case HEAD -> armorItems.set(3, stack);
                default -> {
                }
            }
        }

        @Override
        public HumanoidArm getMainArm() {
            return HumanoidArm.RIGHT;
        }
    }

    private static final class Shot {
        final int index;
        final List<Double> original = new ArrayList<>();
        final List<Double> preCrit = new ArrayList<>();
        final List<Double> incoming = new ArrayList<>();
        final List<Double> post = new ArrayList<>();
        int criticalEvents;

        Shot(int index) {
            this.index = index;
        }

        double total(List<Double> values) {
            return values.stream().mapToDouble(Double::doubleValue).sum();
        }

        double effectiveDamage() {
            double postDamage = total(post);
            return postDamage > 0.0D ? postDamage : total(incoming);
        }
    }

    private static final class ProfileResult {
        final Profile profile;
        final JsonObject attributes;
        final int fullDrawTicks;
        final List<Shot> samples = new ArrayList<>();
        double sustainedIncoming;
        double sustainedPost;
        double sustainedPreCrit;
        int sustainedPreCritEvents;
        int sustainedEvents;
        int sustainedShots;

        ProfileResult(Profile profile, JsonObject attributes, int fullDrawTicks) {
            this.profile = profile;
            this.attributes = attributes;
            this.fullDrawTicks = fullDrawTicks;
        }

        double sustainedDps() {
            double damage = sustainedPost > 0.0D ? sustainedPost : sustainedIncoming;
            return damage / (SUSTAINED_TICKS / 20.0D);
        }

        double meanHit() {
            return samples.stream().filter(shot -> !shot.incoming.isEmpty())
                    .mapToDouble(Shot::effectiveDamage).average().orElse(0.0D);
        }

        double meanCritHit() {
            return samples.stream().filter(shot -> shot.criticalEvents > 0)
                    .mapToDouble(Shot::effectiveDamage).average().orElse(0.0D);
        }

        JsonObject toJson() {
            JsonObject json = profileJson(profile, attributes, fullDrawTicks);
            List<Double> nonCrit = new ArrayList<>();
            List<Double> crit = new ArrayList<>();
            List<Double> preCrit = new ArrayList<>();
            JsonArray hitShotIndices = new JsonArray();
            JsonArray sampleRecords = new JsonArray();
            int shotsWithHit = 0;
            int shotsWithCrit = 0;
            int directEvents = 0;
            for (Shot shot : samples) {
                if (!shot.incoming.isEmpty()) {
                    shotsWithHit++;
                    hitShotIndices.add(shot.index);
                    JsonObject sample = new JsonObject();
                    sample.addProperty("shot", shot.index);
                    sample.addProperty("crit", shot.criticalEvents > 0);
                    sample.addProperty("damage", shot.effectiveDamage());
                    sampleRecords.add(sample);
                }
                directEvents += shot.incoming.size();
                if (shot.criticalEvents > 0) shotsWithCrit++;
                if (!shot.preCrit.isEmpty()) preCrit.add(shot.total(shot.preCrit));
                if (!shot.incoming.isEmpty()) {
                    if (shot.criticalEvents > 0) crit.add(shot.effectiveDamage());
                    else nonCrit.add(shot.effectiveDamage());
                }
            }
            json.addProperty("sample_shots", samples.size());
            json.addProperty("shots_with_direct_hit", shotsWithHit);
            json.add("hit_shot_indices", hitShotIndices);
            json.add("hit_samples", sampleRecords);
            json.addProperty("observed_hit_rate", samples.isEmpty() ? 0.0D : shotsWithHit / (double) samples.size());
            json.addProperty("direct_damage_events", directEvents);
            json.addProperty("shots_with_apothic_crit", shotsWithCrit);
            json.addProperty("observed_crit_rate", shotsWithHit == 0 ? 0.0D : shotsWithCrit / (double) shotsWithHit);
            addDistribution(json, "noncrit_hit", nonCrit);
            addDistribution(json, "crit_hit", crit);
            addDistribution(json, "pre_apothic_crit_hit", preCrit);
            json.addProperty("sustained_interval_ticks", SUSTAINED_TICKS);
            json.addProperty("sustained_interval_seconds", SUSTAINED_TICKS / 20.0D);
            json.addProperty("sustained_shots_released", sustainedShots);
            json.addProperty("sustained_damage_events", sustainedEvents);
            json.addProperty("sustained_pre_apothic_crit_events", sustainedPreCritEvents);
            json.addProperty("sustained_pre_apothic_crit_damage", sustainedPreCrit);
            json.addProperty("sustained_incoming_damage", sustainedIncoming);
            json.addProperty("sustained_post_mitigation_damage", sustainedPost);
            json.addProperty("sustained_dps", sustainedDps());
            return json;
        }

        private static void addDistribution(JsonObject json, String name, List<Double> values) {
            JsonObject dist = new JsonObject();
            if (values.isEmpty()) {
                dist.addProperty("count", 0);
            }
            else {
                List<Double> sorted = values.stream().sorted().toList();
                dist.addProperty("count", sorted.size());
                dist.addProperty("min", sorted.getFirst());
                dist.addProperty("median", sorted.get(sorted.size() / 2));
                dist.addProperty("mean", sorted.stream().mapToDouble(Double::doubleValue).average().orElse(0.0D));
                dist.addProperty("max", sorted.getLast());
            }
            json.add(name, dist);
        }
    }
}
