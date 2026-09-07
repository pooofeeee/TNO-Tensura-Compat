package com.tno.tensuracompat.debug;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.mojang.authlib.GameProfile;
import com.tno.tensuracompat.TNOTensuraCompat;
import com.tno.tensuracompat.core.stage.ProductionStageScaling;
import io.github.manasmods.tensura.enchantment.SlottingHelper;
import io.github.manasmods.tensura.entity.projectile.TensuraFlyingProjectile;
import io.github.manasmods.tensura.registry.attribute.TensuraAttributes;
import io.github.manasmods.tensura.registry.item.misc.TensuraDataComponents;
import io.github.manasmods.tensura.storage.TensuraStorages;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.component.BundleContents;
import net.minecraft.world.item.enchantment.ItemEnchantments;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import net.neoforged.fml.ModList;
import net.neoforged.fml.loading.FMLEnvironment;
import net.neoforged.neoforge.common.util.FakePlayer;
import net.neoforged.neoforge.common.util.FakePlayerFactory;
import net.neoforged.neoforge.event.entity.living.LivingDamageEvent;
import net.neoforged.neoforge.event.entity.EntityJoinLevelEvent;
import net.neoforged.neoforge.event.entity.living.LivingIncomingDamageEvent;
import net.neoforged.neoforge.event.server.ServerStartedEvent;
import net.neoforged.neoforge.event.tick.ServerTickEvent;

import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.nio.charset.StandardCharsets;
import java.util.*;

/** Opt-in, non-production research. No damage source, skill, affinity or damage injection. */
public final class Phase6ElementalNativePathResearch {
    private static final boolean ENABLED = !FMLEnvironment.production
            && Boolean.getBoolean("tno.phase6.elementalNativePath");
    private static final String PREFIX = "TNO_ELEMENTAL_NATIVE_PATH ";
    private static final String[] ELEMENTS = {"earth", "fire", "space", "water", "wind"};
    private static final String[] MODES = {"vanilla_free", "royal_legacy", "royal_rescue",
            "royal_native", "royal_native_s7", "royal_free"};
    private static final String[] TARGETS = {"neutral", "orc_disaster", "luminous_valentine"};
    private static Session active;

    private Phase6ElementalNativePathResearch() { }

    public static void onServerStarted(ServerStartedEvent event) {
        if (ENABLED) active = new Session(event.getServer());
    }

    public static void onServerTick(ServerTickEvent.Post event) {
        if (active == null) return;
        try { active.tick(); }
        catch (Throwable error) {
            JsonObject failure = new JsonObject();
            failure.addProperty("error", error.toString());
            TNOTensuraCompat.LOGGER.error("Elemental native-path research failed", error);
            log("error", failure);
            active.finish(false);
        }
    }

    /** Read-only observer endpoints; dormant unless the exact research projectile is active. */
    public static void boundary(String name, Entity projectile, Entity target, String detail) {
        if (active == null || projectile != active.projectile || target != active.target) return;
        JsonObject trace = active.trace(name);
        trace.addProperty("detail", detail);
        trace.addProperty("projectile_age", active.projectile.getAge());
        trace.addProperty("can_hit", Boolean.TRUE.equals(call(active.projectile, "canHitEntity", target)));
        active.traces.add(trace);
    }

    public static void gate(Projectile projectile, HitResult hit, Object result, Object deflection) {
        if (active == null || projectile != active.projectile || !(hit instanceof EntityHitResult entityHit)
                || entityHit.getEntity() != active.target) return;
        boundary("native_projectile_gate", projectile, active.target,
                call(result, "get") + "/" + (call(deflection, "get")
                        == net.minecraft.world.entity.projectile.ProjectileDeflection.NONE ? "NONE" : "NATIVE_DEFLECTION"));
    }

    public static void hurtBoundary(Entity projectile, Entity target, DamageSource source,
            float amount, Boolean result) {
        if (active == null || projectile != active.projectile || target != active.target) return;
        JsonObject trace = active.trace(result == null ? "native_hurt_call" : "native_hurt_return");
        source(trace, source, amount);
        if (result != null) trace.addProperty("result", result);
        trace.addProperty("hp", active.target.getHealth());
        trace.addProperty("shp", TensuraStorages.getExistenceFrom(active.target).getSpiritualHealth());
        trace.addProperty("target_fire_resistance", active.target.hasEffect(net.minecraft.world.effect.MobEffects.FIRE_RESISTANCE));
        trace.addProperty("target_fire_immune", active.target.fireImmune());
        trace.addProperty("target_invulnerable_time", active.target.invulnerableTime);
        trace.addProperty("source_is_fire", source.is(net.minecraft.tags.DamageTypeTags.IS_FIRE));
        JsonArray effects = new JsonArray();
        active.target.getActiveEffects().forEach(effect -> effects.add(effect.toString()));
        trace.add("target_effects", effects);
        active.traces.add(trace);
    }

    public static void onIncomingHighest(LivingIncomingDamageEvent event) { incoming(event, "incoming_highest"); }
    public static void onIncomingLowest(LivingIncomingDamageEvent event) { incoming(event, "incoming_lowest"); }
    private static void incoming(LivingIncomingDamageEvent event, String boundary) {
        if (active == null || event.getEntity() != active.target || active.projectile == null) return;
        JsonObject trace = active.trace(boundary);
        source(trace, event.getSource(), event.getAmount());
        trace.addProperty("canceled", event.isCanceled());
        active.traces.add(trace);
    }
    public static void onDamagePost(LivingDamageEvent.Post event) {
        if (active == null || event.getEntity() != active.target || active.projectile == null) return;
        JsonObject trace = active.trace("damage_post");
        source(trace, event.getSource(), event.getNewDamage());
        active.traces.add(trace);
    }

    public static void onEntityJoin(EntityJoinLevelEvent event) {
        if (active == null || !(event.getEntity() instanceof TensuraFlyingProjectile flying)
                || flying.getOwner() != active.player) return;
        active.joinedProjectile = flying;
    }

    private static void source(JsonObject json, DamageSource source, float amount) {
        json.addProperty("source", source.typeHolder().unwrapKey().orElseThrow().location().toString());
        json.addProperty("amount", amount);
        json.addProperty("direct", entityId(source.getDirectEntity()));
        json.addProperty("direct_uuid", source.getDirectEntity() == null ? "NONE" : source.getDirectEntity().getStringUUID());
        json.addProperty("owner_retained", source.getEntity() == active.player);
        json.addProperty("magic_type", String.valueOf(call(source, "tensura$getMagicType")));
        json.addProperty("resistance_bypass", ((Number) call(source, "tensura$getResistanceBypassLevel")).doubleValue());
    }

    private static final class Session {
        final MinecraftServer server;
        final ServerLevel level;
        final List<Case> cases = new ArrayList<>();
        final boolean alreadyForced;
        FakePlayer player;
        LivingEntity target;
        TensuraFlyingProjectile projectile;
        TensuraFlyingProjectile joinedProjectile;
        Object l2Cap;
        JsonArray traces = new JsonArray();
        JsonObject row;
        int index, step, releaseTick, readyWait;
        String phase = "SETUP";

        Session(MinecraftServer server) {
            this.server = server;
            level = server.overworld();
            if (!ModList.get().isLoaded("l2hostility") || !ModList.get().isLoaded("apotheosis"))
                throw new IllegalStateException("Full comparison stack required");
            for (String element : ELEMENTS) for (String target : TARGETS) for (String mode : MODES)
                cases.add(new Case(element, target, mode));
            alreadyForced = level.getForcedChunks().contains(new net.minecraft.world.level.ChunkPos(80, 80).toLong());
            level.setChunkForced(80, 80, true);
            level.getChunk(80, 80);
            server.getCommands().performPrefixedCommand(server.createCommandSourceStack().withSuppressedOutput(), "tick sprint 1000000");
            JsonObject catalog = new JsonObject();
            catalog.addProperty("requested_cases", cases.size());
            catalog.addProperty("baseline", "b50061eb9040474a7fb8bdeb780f46a30201d63f");
            catalog.addProperty("full_stack", true);
            catalog.addProperty("shooters", "fresh survival FakePlayers; no skills/affinities/resource attributes granted");
            catalog.addProperty("targets", "neutral LivingEntity adapter and normally ticking accepted Lv1000 Orc/Luminous profiles; setup-only resources and position");
            catalog.addProperty("delivery", "real ItemStack.use/releaseUsing; either historical onHit then discard, same-projectile rescue, or ordinary world ticks");
            catalog.addProperty("production_prototype", false);
            log("catalog", catalog);
        }

        void tick() {
            if (step == 0) {
                if (index == cases.size()) { finish(true); return; }
                setup();
            }
            if (step == 1 && (target.tickCount == 0 || level.getEntity(target.getUUID()) != target)) {
                if (++readyWait > 2000) throw new IllegalStateException("Research chunk/target did not become tickable");
                return;
            }
            if (step == 5 && !cases.get(index).target.equals("neutral")) configureL2();
            if (step == 10 && l2Cap != null) installProfile();
            if (step == 20) release();
            if (step > 20 && (cases.get(index).mode.equals("royal_legacy") || step >= 40)) {
                completeCase();
                return;
            }
            step++;
        }

        void setup() {
            Case spec = cases.get(index);
            traces = new JsonArray(); phase = "SETUP"; readyWait = 0;
            UUID uuid = UUID.nameUUIDFromBytes(("elemental-e2-" + index).getBytes(StandardCharsets.UTF_8));
            player = FakePlayerFactory.get(level, new GameProfile(uuid, "TNO_E2_" + index));
            player.getInventory().clearContent();
            player.setPos(1280.5, 200, 1280.5);
            player.getAbilities().instabuild = false;
            player.getAbilities().invulnerable = false;
            ResourceLocation targetId = id(spec.target.equals("luminous_valentine")
                    ? "tensura_neb:luminous_valentine" : "tensura:" + spec.target);
            if (!spec.target.equals("neutral") && !BuiltInRegistries.ENTITY_TYPE.containsKey(targetId))
                throw new IllegalStateException("Missing registry target " + targetId);
            target = spec.target.equals("neutral") ? new NeutralTarget(level)
                    : (LivingEntity) BuiltInRegistries.ENTITY_TYPE.get(targetId).create(level);
            if (target == null) throw new IllegalStateException("Missing target " + spec.target);
            target.setPos(1280.5, 200, 1286.5);
            target.setNoGravity(true);
            if (target instanceof Mob mob) mob.setNoAi(false);
            level.addFreshEntity(target);
            l2Cap = null;
        }

        void configureL2() {
                Object type = call(staticField("dev.xkmc.l2hostility.init.registrate.LHMiscs", "MOB"), "type");
                l2Cap = call(type, "getOrCreate", target);
                Object config = call(l2Cap, "getConfigCache", target);
                if (config == null) throw new IllegalStateException("Missing native L2 config for " + entityId(target));
                Field max = field(config.getClass(), "maxLevel");
                try {
                    int previous = max.getInt(config);
                    try { max.setInt(config, 1000); call(l2Cap, "reinit", target, 1000, false); }
                    finally { max.setInt(config, previous); }
                } catch (IllegalAccessException e) { throw new IllegalStateException(e); }
        }

        @SuppressWarnings("unchecked")
        void installProfile() {
            Case spec = cases.get(index);
            Map<String, Integer> expected = spec.target.equals("orc_disaster")
                    ? ((Map<Integer, Map<String, Integer>>) staticPrivate("ACCEPTED_ORC_ENDGAME_PROFILES")).get(1000)
                    : ((Map<String, Map<String, Integer>>) staticPrivate("ACCEPTED_ENDGAME_PROFILES")).get(entityId(target));
            Map<Object, Integer> traits = (Map<Object, Integer>) read(l2Cap, "traits");
            for (Object trait : new ArrayList<>(traits.keySet())) {
                call(trait, "initialize", target, 0); call(trait, "postInit", target, 0);
            }
            traits.clear(); ((Map<?, ?>) read(l2Cap, "data")).clear();
            ((Collection<?>) read(l2Cap, "pending")).clear();
            Object registry = call(staticField("dev.xkmc.l2hostility.init.registrate.LHTraits", "TRAITS"), "get");
            for (Object trait : (Iterable<?>) registry) {
                String name = traitId(trait);
                if (expected.containsKey(name)) {
                    traits.put(trait, expected.get(name));
                    call(trait, "initialize", target, expected.get(name));
                }
            }
            ((Collection<?>) read(l2Cap, "pending")).clear();
            if (!traitRanks().equals(toJson(expected))) throw new IllegalStateException("Profile mismatch");
        }

        void release() {
            Case spec = cases.get(index);
            if (l2Cap != null) installProfile();
            target.setPos(1280.5, 200, 1286.5); target.setDeltaMovement(Vec3.ZERO);
            target.setHealth(target.getMaxHealth()); target.invulnerableTime = 0;
            var existence = TensuraStorages.getExistenceFrom(target);
            existence.setSpiritualHealth(target.getAttributeValue(TensuraAttributes.MAX_SPIRITUAL_HEALTH));
            ItemStack bow = new ItemStack(BuiltInRegistries.ITEM.get(id(spec.mode.startsWith("vanilla")
                    ? "minecraft:bow" : "royalvariations:royal_bow")));
            player.setItemInHand(InteractionHand.MAIN_HAND, bow);
            player.setItemInHand(InteractionHand.OFF_HAND,
                    new ItemStack(BuiltInRegistries.ITEM.get(id("royalvariations:royal_arrow")), 64));
            call(player, "detectEquipmentUpdates");
            // Legal isolated engraving/core loadout after normal conversion and first roll.
            bow.set(DataComponents.ENCHANTMENTS, ItemEnchantments.EMPTY);
            var engraving = server.registryAccess().registryOrThrow(Registries.ENCHANTMENT)
                    .getHolderOrThrow(ResourceKey.create(Registries.ENCHANTMENT, id("tensura:slotting")));
            if (!engraving.value().canEnchant(bow)) throw new IllegalStateException("Illegal Slotting item");
            bow.enchant(engraving, 1);
            bow.set(DataComponents.BUNDLE_CONTENTS, new BundleContents(List.of(
                    new ItemStack(BuiltInRegistries.ITEM.get(id("tensura:element_core_" + spec.element))))));
            if (!spec.mode.startsWith("vanilla")) {
                if (!bow.has(TensuraDataComponents.EP.get())) throw new IllegalStateException("Native gear conversion missing");
                bow.set(TensuraDataComponents.EP.get(), spec.mode.endsWith("s7") ? 2_490_000D : 1000D);
            }
            Vec3 delta = target.getBoundingBox().getCenter().subtract(player.getEyePosition());
            player.setYRot((float) Math.toDegrees(Math.atan2(-delta.x, delta.z)));
            player.setXRot((float) -Math.toDegrees(Math.atan2(delta.y, delta.horizontalDistance())));
            player.yHeadRot = player.getYRot();
            row = new JsonObject();
            row.addProperty("case", index); row.addProperty("element", spec.element);
            row.addProperty("target", spec.target); row.addProperty("mode", spec.mode);
            row.addProperty("target_id", entityId(target));
            row.addProperty("bow", bow.getItem().toString());
            row.addProperty("stage", ProductionStageScaling.stage(bow).map(Enum::name).orElse("NONE"));
            row.addProperty("ep", bow.getOrDefault(TensuraDataComponents.EP.get(), 0D));
            row.addProperty("slotting_capacity", SlottingHelper.getElementalSlots(level, bow));
            row.addProperty("core_count_before", SlottingHelper.getContentSize(bow));
            row.addProperty("used_hand", "MAIN_HAND");
            row.addProperty("owner_creative", player.getAbilities().instabuild);
            row.add("owner_skills", skills(player)); row.add("target_skills", skills(target));
            row.addProperty("owner_magicules", TensuraStorages.getExistenceFrom(player).getMagicule());
            row.addProperty("owner_aura", TensuraStorages.getExistenceFrom(player).getAura());
            row.addProperty("owner_attack_damage", player.getAttributeValue(net.minecraft.world.entity.ai.attributes.Attributes.ATTACK_DAMAGE));
            row.addProperty("l2_level", l2Cap == null ? 0 : ((Number) call(l2Cap, "getLevel")).intValue());
            row.addProperty("l2_initialized", l2Cap != null && Boolean.TRUE.equals(call(l2Cap, "isInitialized")));
            if (l2Cap != null && !row.get("l2_initialized").getAsBoolean())
                throw new IllegalStateException("L2 target must finish native initialization before release");
            row.addProperty("target_no_ai", target instanceof Mob mob && mob.isNoAi());
            row.addProperty("max_hp", target.getMaxHealth());
            row.add("traits", traitRanks());
            row.addProperty("pre_hp", target.getHealth()); row.addProperty("pre_shp", existence.getSpiritualHealth());
            row.addProperty("target_tick_at_release", target.tickCount);
            row.addProperty("pickable", target.isPickable());
            bow.use(level, player, InteractionHand.MAIN_HAND);
            if (!player.isUsingItem()) throw new IllegalStateException("Native Slotting use rejected");
            bow.releaseUsing(level, player, bow.getUseDuration(player) - 20);
            player.stopUsingItem();
            var spawned = level.getEntitiesOfClass(Projectile.class, player.getBoundingBox().inflate(32),
                    entity -> entity.getOwner() == player);
            row.addProperty("spawn_count", spawned.size());
            if (spawned.size() != 1 || !(spawned.getFirst() instanceof TensuraFlyingProjectile))
                throw new IllegalStateException("Unexpected Slotting release " + spawned + "; joined=" + joinedProjectile
                        + "; joined_removed=" + (joinedProjectile != null && joinedProjectile.isRemoved())
                        + "; player=" + player.position() + "; bow=" + bow + "; cores=" + SlottingHelper.getContentSize(bow));
            projectile = (TensuraFlyingProjectile) spawned.getFirst();
            row.addProperty("projectile", entityId(projectile));
            row.addProperty("projectile_uuid", projectile.getStringUUID());
            row.addProperty("owner_retained", projectile.getOwner() == player);
            row.addProperty("damage", projectile.getDamage()); row.addProperty("speed", projectile.getSpeed());
            row.addProperty("burn_ticks", projectile.getBurnTicks()); row.addProperty("knockback", projectile.getKnockForce());
            row.addProperty("no_gravity", projectile.isNoGravity()); row.addProperty("elemental_attack", projectile.isElementalAttack());
            row.addProperty("projectile_element", projectile.getElement().name());
            row.addProperty("projectile_skill", String.valueOf(call(projectile, "getSkill")));
            row.addProperty("projectile_mp_cost", projectile.getMpCost()); row.addProperty("projectile_ap_cost", projectile.getApCost());
            row.addProperty("core_count_after", SlottingHelper.getContentSize(bow));
            row.addProperty("can_hit_at_release", Boolean.TRUE.equals(call(projectile, "canHitEntity", target)));
            CompoundTag data = new CompoundTag(); projectile.saveWithoutId(data);
            row.addProperty("projectile_data_at_release", data.toString());
            if (!spec.mode.endsWith("free")) {
                Vec3 aim = target.getBoundingBox().getCenter();
                Vec3 direction = aim.subtract(projectile.position()).normalize();
                double speed = projectile.getDeltaMovement().length();
                projectile.setPos(aim.subtract(direction.scale(2))); projectile.setDeltaMovement(direction.scale(speed));
            }
            phase = "RUN"; releaseTick = server.getTickCount();
            if (spec.mode.equals("royal_legacy") || spec.mode.equals("royal_rescue")) {
                phase = "LEGACY_CALL";
                call(projectile, "onHit", new EntityHitResult(target));
                row.addProperty("legacy_trace_count", traces.size());
                row.addProperty("legacy_hp", target.getHealth());
                row.addProperty("legacy_shp", existence.getSpiritualHealth());
                row.addProperty("legacy_removed", projectile.isRemoved());
                if (spec.mode.equals("royal_legacy")) projectile.discard();
                phase = "RUN";
            }
        }

        JsonObject trace(String name) {
            JsonObject trace = new JsonObject();
            trace.addProperty("boundary", name); trace.addProperty("phase", phase);
            trace.addProperty("relative_tick", server.getTickCount() - releaseTick);
            trace.addProperty("uuid", projectile.getStringUUID());
            return trace;
        }

        JsonObject traitRanks() {
            JsonObject result = new JsonObject();
            if (l2Cap != null) ((Map<?, ?>) read(l2Cap, "traits")).forEach((trait, rank) ->
                    result.addProperty(traitId(trait), (Number) rank));
            return result;
        }

        void completeCase() {
            row.addProperty("post_hp", target.getHealth());
            row.addProperty("post_shp", TensuraStorages.getExistenceFrom(target).getSpiritualHealth());
            row.addProperty("projectile_age_end", projectile.getAge());
            row.addProperty("target_ticks_elapsed", target.tickCount - row.get("target_tick_at_release").getAsInt());
            row.addProperty("observation_ticks", server.getTickCount() - releaseTick);
            row.add("traits_after", traitRanks()); row.add("traces", traces);
            log("row", row);
            cleanup(); index++; step = 0;
        }

        void cleanup() {
            if (projectile != null) projectile.discard();
            if (joinedProjectile != null) joinedProjectile.discard();
            if (target != null) target.discard();
            if (player != null) { player.getInventory().clearContent(); player.setPos(1280.5, -200, 1280.5); }
            projectile = null; joinedProjectile = null; target = null; player = null; l2Cap = null;
        }

        void finish(boolean success) {
            cleanup();
            if (!alreadyForced) level.setChunkForced(80, 80, false);
            JsonObject result = new JsonObject();
            result.addProperty("status", success ? "complete" : "error"); result.addProperty("completed_cases", index);
            result.addProperty("requested_cases", cases.size()); result.addProperty("force_load_restored", true);
            log("suite_result", result);
            active = null; server.halt(false);
        }
    }

    private record Case(String element, String target, String mode) { }
    /** Same neutral entity-type adapter concept as the accepted pre-flight; no custom hurt override. */
    private static final class NeutralTarget extends LivingEntity {
        NeutralTarget(Level level) { super(EntityType.ARMOR_STAND, level); }
        @Override public Iterable<ItemStack> getArmorSlots() { return List.of(); }
        @Override public ItemStack getItemBySlot(EquipmentSlot slot) { return ItemStack.EMPTY; }
        @Override public void setItemSlot(EquipmentSlot slot, ItemStack stack) { }
        @Override public HumanoidArm getMainArm() { return HumanoidArm.RIGHT; }
        @Override public boolean isPickable() { return true; }
    }

    private static JsonArray skills(LivingEntity entity) {
        JsonArray result = new JsonArray();
        Object skills = call(type("io.github.manasmods.manascore.skill.api.SkillAPI"), "getSkillsFrom", entity);
        for (Object skill : (Collection<?>) call(skills, "getLearnedSkills")) result.add(call(skill, "toNBT").toString());
        return result;
    }
    private static JsonObject toJson(Map<String, Integer> values) {
        JsonObject result = new JsonObject(); values.forEach(result::addProperty); return result;
    }
    private static String traitId(Object trait) {
        return String.valueOf(call(Phase5FSuiteBBenchmark.class, "traitId", trait));
    }
    private static String entityId(Entity entity) { return entity == null ? "NONE" : BuiltInRegistries.ENTITY_TYPE.getKey(entity.getType()).toString(); }
    private static ResourceLocation id(String id) { return ResourceLocation.parse(id); }
    private static Class<?> type(String name) {
        try { return Class.forName(name); } catch (ReflectiveOperationException e) { throw new IllegalStateException(e); }
    }
    private static Object staticField(String name, String field) {
        try { return type(name).getField(field).get(null); } catch (ReflectiveOperationException e) { throw new IllegalStateException(e); }
    }
    private static Field field(Class<?> type, String name) {
        for (Class<?> current = type; current != null; current = current.getSuperclass()) {
            try { Field field = current.getDeclaredField(name); field.setAccessible(true); return field; }
            catch (NoSuchFieldException ignored) { }
        }
        throw new IllegalStateException("Missing field " + name);
    }
    private static Object read(Object object, String name) {
        try { return field(object.getClass(), name).get(object); } catch (ReflectiveOperationException e) { throw new IllegalStateException(e); }
    }
    private static Object staticPrivate(String name) {
        try { return field(Phase5FSuiteBBenchmark.class, name).get(null); } catch (ReflectiveOperationException e) { throw new IllegalStateException(e); }
    }
    /** Reuse the accepted, compatible-signature reflection helper without changing its harness. */
    private static Object call(Object target, String name, Object... args) {
        try {
            Method method = Phase5FSuiteBBenchmark.class.getDeclaredMethod("invoke", Object.class, String.class, Object[].class);
            method.setAccessible(true);
            return method.invoke(null, target, name, args);
        } catch (ReflectiveOperationException e) { throw new IllegalStateException("Native read/call failed: " + name, e); }
    }
    private static void log(String kind, JsonObject value) {
        value.addProperty("schema", "tno.phase6.elemental_native_path.runtime.v1"); value.addProperty("kind", kind);
        TNOTensuraCompat.LOGGER.info(PREFIX + value);
    }
}
