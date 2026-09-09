package com.tno.tensuracompat.debug;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.mojang.authlib.GameProfile;
import com.tno.tensuracompat.TNOTensuraCompat;
import com.tno.tensuracompat.core.stage.ProductionStageScaling;
import io.github.manasmods.tensura.damage.TensuraDamageHelper;
import io.github.manasmods.tensura.registry.item.misc.TensuraDataComponents;
import io.github.manasmods.tensura.storage.TensuraStorages;
import io.github.manasmods.tensura.storage.ep.IExistence;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.enchantment.ItemEnchantments;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.Vec3;
import net.neoforged.fml.ModList;
import net.neoforged.fml.loading.FMLEnvironment;
import net.neoforged.neoforge.common.util.FakePlayer;
import net.neoforged.neoforge.common.util.FakePlayerFactory;
import net.neoforged.neoforge.event.entity.living.LivingDamageEvent;
import net.neoforged.neoforge.event.entity.living.LivingIncomingDamageEvent;
import net.neoforged.neoforge.event.server.ServerStartedEvent;
import net.neoforged.neoforge.event.tick.ServerTickEvent;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.nio.charset.StandardCharsets;
import java.util.*;

/** Opt-in research; all damage and resource changes originate in unchanged native calls. */
public final class Phase6SoulNativePathResearch {
    private static final boolean ENABLED = !FMLEnvironment.production && Boolean.getBoolean("tno.phase6.soulNativePath");
    private static Session active;
    private Phase6SoulNativePathResearch() { }
    public static void onServerStarted(ServerStartedEvent event) { if (ENABLED) active = new Session(event.getServer()); }
    public static void onServerTick(ServerTickEvent.Post event) {
        if (active == null) return;
        try { active.tick(); } catch (Throwable error) {
            JsonObject failure = new JsonObject(); failure.addProperty("error", error.toString());
            TNOTensuraCompat.LOGGER.error("Soul native-path research failed", error);
            log("error", failure); active.finish(false);
        }
    }
    public static void observe(String boundary, Entity target, DamageSource source, float amount, Boolean result) {
        if (active == null || !active.running || target != active.target) return;
        JsonObject trace = active.trace(boundary);
        trace.addProperty("amount", amount);
        if (source != null) {
            trace.addProperty("source", source.typeHolder().unwrapKey().orElseThrow().location().toString());
            trace.addProperty("source_object", System.identityHashCode(source));
            trace.addProperty("message", source.getMsgId());
            trace.addProperty("direct", entityId(source.getDirectEntity()));
            trace.addProperty("direct_uuid", source.getDirectEntity() == null ? "NONE" : source.getDirectEntity().getStringUUID());
            trace.addProperty("owner_retained", source.getEntity() == active.player);
            JsonArray tags = new JsonArray(); source.typeHolder().tags().map(tag -> tag.location().toString()).sorted().forEach(tags::add);
            trace.add("tags", tags);
            trace.addProperty("resistance_bypass", ((Number)call(source, "tensura$getResistanceBypassLevel")).doubleValue());
        }
        if (result != null) trace.addProperty("result", result);
        active.traces.add(trace);
    }
    public static void resource(IExistence storage, double requested, boolean after) {
        if (active == null || !active.running || storage != TensuraStorages.getExistenceFrom(active.target)) return;
        JsonObject trace = active.trace(after ? "shp_write_after" : "shp_write_before");
        trace.addProperty("requested_shp", requested); active.traces.add(trace);
    }
    public static void storage(IExistence storage, double requested, boolean after) {
        if(active!=null && active.running && storage==TensuraStorages.getExistenceFrom(active.player)) { ledger("owner_shp",requested,after); return; }
        if (active == null || !active.running || storage != TensuraStorages.getExistenceFrom(active.target)) return;
        JsonObject trace = active.trace(after ? "storage_after" : "storage_before");
        trace.addProperty("requested_shp", requested);
        JsonArray callers = new JsonArray();
        StackWalker.getInstance().walk(frames -> frames.map(frame -> frame.getClassName()+"."+frame.getMethodName())
                .filter(name -> name.startsWith("io.github.manasmods.") && !name.contains("tno$") && !name.endsWith(".setSpiritualHealth"))
                .limit(6).toList()).forEach(callers::add);
        trace.add("native_callers", callers); active.traces.add(trace);
    }
    public static void health(LivingEntity target, float value, boolean after) {
        if(active==null || !active.running || (target!=active.target && target!=active.player)) return;
        ledger(target==active.target ? "hp":"owner_hp",value,after);
    }
    public static void energy(IExistence storage, String resource, double value, boolean after) {
        if(active==null || !active.running) return;
        if(storage==TensuraStorages.getExistenceFrom(active.target)) ledger(resource,value,after);
        else if(storage==TensuraStorages.getExistenceFrom(active.player)) ledger(resource.replace("target_","owner_"),value,after);
    }
    private static void ledger(String resource,double value,boolean after) {
        JsonObject trace=active.trace(after ? "resource_after":"resource_before");
        trace.addProperty("resource",resource); trace.addProperty("requested",value);
        JsonArray callers=new JsonArray(); StackWalker.getInstance().walk(frames -> frames
                .map(frame -> frame.getClassName()+"."+frame.getMethodName())
                .filter(name -> !name.startsWith("com.tno.") && !name.contains("tno$") && !name.endsWith(".setHealth") && !name.endsWith(".setMagicule") && !name.endsWith(".setAura"))
                .limit(9).toList()).forEach(callers::add);
        trace.add("native_callers",callers); active.traces.add(trace);
    }
    public static void onIncomingHighest(LivingIncomingDamageEvent event) { incoming(event, "incoming_highest"); }
    public static void onIncomingLowest(LivingIncomingDamageEvent event) { incoming(event, "incoming_lowest"); }
    private static void incoming(LivingIncomingDamageEvent event, String name) {
        observe(name, event.getEntity(), event.getSource(), event.getAmount(), !event.isCanceled());
    }
    public static void onDamagePost(LivingDamageEvent.Post event) {
        observe("damage_post", event.getEntity(), event.getSource(), event.getNewDamage(), null);
    }
    private static final class Session {
        final MinecraftServer server; final ServerLevel level; final boolean alreadyForced;
        final List<Case> cases = new ArrayList<>();
        final boolean followup = Boolean.getBoolean("tno.phase6.soulFollowup");
        final double laneX = followup ? 1288.5 : 1280.5;
        final double startZ = followup ? 1282.5 : 1280.5;
        final double targetZ = followup ? 1288.5 : 1286.5;
        FakePlayer player; LivingEntity target; AbstractArrow projectile; Object l2Cap;
        JsonObject row; JsonArray traces = new JsonArray();
        int index, step, releaseTick, readyWait; boolean running;
        Session(MinecraftServer server) {
            this.server = server; level = server.overworld();
            if (!ModList.get().isLoaded("l2hostility") || !ModList.get().isLoaded("apotheosis"))
                throw new IllegalStateException("Full stack required");
            if (followup) {
                cases.add(new Case("neutral","royal_plain_s0"));
                cases.add(new Case("neutral","royal_plain_s7"));
                cases.add(new Case("hinata_sakaguchi","royal_native_s7"));
            } else if (Boolean.getBoolean("tno.phase6.soulComparison")) {
                for (String target : List.of("neutral", "orc_disaster", "gazel_dwargo", "luminous_valentine", "hinata_sakaguchi"))
                    for (String mode : List.of("royal_legacy_s0", "royal_legacy_s7", "royal_native_s0", "royal_native_s7"))
                        cases.add(new Case(target, mode));
            } else {
                cases.add(new Case("neutral", "vanilla_plain")); cases.add(new Case("neutral", "vanilla_soul"));
            }
            alreadyForced = level.getForcedChunks().contains(new net.minecraft.world.level.ChunkPos(80,80).toLong());
            level.setChunkForced(80,80,true); level.getChunk(80,80);
            server.getCommands().performPrefixedCommand(server.createCommandSourceStack().withSuppressedOutput(), "tick sprint 1000000");
            JsonObject catalog = new JsonObject(); catalog.addProperty("requested_cases", cases.size());
            catalog.addProperty("baseline", "c882e1885ed925f1dc24e47cf6c8960ad1400caa");
            catalog.addProperty("focused_followup",followup);
            catalog.addProperty("setup", "Native spawned ticking targets; native L2 initialization/profile; survival FakePlayer without skill/resource grants; no HP/SHP/cooldown setters; legal isolated enchantment/gear EP fixture");
            JsonObject mods = new JsonObject(); ModList.get().getMods().forEach(mod -> mods.addProperty(mod.getModId(), mod.getVersion().toString()));
            catalog.add("mods", mods); log("catalog", catalog);
        }
        void tick() {
            if (step == 0) { if(index == cases.size()) { finish(true); return; } setup(); }
            if(step == 1 && (target.tickCount == 0 || level.getEntity(target.getUUID()) != target)) {
                if(++readyWait > 2000) throw new IllegalStateException("Target not ticking"); return;
            }
            if(step == 5) configureL2();
            if(step == 10) installProfile();
            if(step == 20) release();
            if(step == 45) { complete(); return; }
            step++;
        }
        void setup() {
            running = false; traces = new JsonArray(); readyWait = 0;
            Case spec = cases.get(index);
            player = FakePlayerFactory.get(level, new GameProfile(UUID.nameUUIDFromBytes(("soul-"+spec).getBytes(StandardCharsets.UTF_8)), "TNO_S_"+index));
            player.getInventory().clearContent(); player.setPos(laneX,200,startZ);
            player.getAbilities().instabuild = false; player.getAbilities().invulnerable = false;
            ResourceLocation targetId = id(spec.target.equals("neutral") ? "minecraft:iron_golem"
                    : (spec.target.equals("luminous_valentine") ? "tensura_neb:" : "tensura:")+spec.target);
            if(!BuiltInRegistries.ENTITY_TYPE.containsKey(targetId)) throw new IllegalStateException("Missing target "+targetId);
            target = (LivingEntity)BuiltInRegistries.ENTITY_TYPE.get(targetId).create(level);
            if(target == null) throw new IllegalStateException("Cannot spawn target");
            target.setPos(laneX,200,targetZ); target.setNoGravity(true);
            level.addFreshEntity(target); l2Cap = null;
        }
        void configureL2() {
            Object type = call(staticField("dev.xkmc.l2hostility.init.registrate.LHMiscs", "MOB"), "type");
            l2Cap = call(type,"getOrCreate",target);
            Object config = call(l2Cap,"getConfigCache",target);
            if(config == null && cases.get(index).target.equals("neutral")) { l2Cap=null; return; }
            if(config == null) throw new IllegalStateException("Missing native L2 config");
            Field max = field(config.getClass(),"maxLevel");
            try { int previous=max.getInt(config);
                try { max.setInt(config,1000); call(l2Cap,"reinit",target,cases.get(index).target.equals("neutral") ? 0 : 1000,false); }
                finally { max.setInt(config,previous); }
            } catch(IllegalAccessException e) { throw new IllegalStateException(e); }
        }
        @SuppressWarnings("unchecked")
        void installProfile() {
            if(l2Cap == null) return;
            Case spec = cases.get(index);
            Map<String,Integer> expected = spec.target.equals("neutral") ? Map.of() : spec.target.equals("orc_disaster")
                    ? ((Map<Integer,Map<String,Integer>>)staticPrivate("ACCEPTED_ORC_ENDGAME_PROFILES")).get(1000)
                    : ((Map<String,Map<String,Integer>>)staticPrivate("ACCEPTED_ENDGAME_PROFILES")).get(entityId(target));
            if(expected == null) throw new IllegalStateException("No accepted profile for "+entityId(target));
            Map<Object,Integer> traits = (Map<Object,Integer>)read(l2Cap,"traits");
            for(Object trait : new ArrayList<>(traits.keySet())) { call(trait,"initialize",target,0); call(trait,"postInit",target,0); }
            traits.clear(); ((Map<?,?>)read(l2Cap,"data")).clear(); ((Collection<?>)read(l2Cap,"pending")).clear();
            Object registry=call(staticField("dev.xkmc.l2hostility.init.registrate.LHTraits","TRAITS"),"get");
            for(Object trait : (Iterable<?>)registry) if(expected.containsKey(traitId(trait))) {
                traits.put(trait,expected.get(traitId(trait))); call(trait,"initialize",target,expected.get(traitId(trait)));
            }
            ((Collection<?>)read(l2Cap,"pending")).clear();
            JsonObject wanted=new JsonObject(); expected.forEach(wanted::addProperty);
            if(!traits().equals(wanted)) throw new IllegalStateException("Profile mismatch");
        }
        void release() {
            Case spec=cases.get(index); installProfile();
            target.setPos(laneX,200,targetZ); target.setDeltaMovement(Vec3.ZERO);
            boolean royal=spec.mode.startsWith("royal");
            ItemStack bow=new ItemStack(BuiltInRegistries.ITEM.get(id(royal ? "royalvariations:royal_bow" : "minecraft:bow")));
            player.setItemInHand(InteractionHand.MAIN_HAND,bow);
            player.setItemInHand(InteractionHand.OFF_HAND,new ItemStack(BuiltInRegistries.ITEM.get(id(royal ? "royalvariations:royal_arrow" : "minecraft:arrow")),64));
            call(player,"detectEquipmentUpdates"); bow.set(DataComponents.ENCHANTMENTS,ItemEnchantments.EMPTY);
            var engraving=server.registryAccess().registryOrThrow(Registries.ENCHANTMENT).getHolderOrThrow(ResourceKey.create(Registries.ENCHANTMENT,id("tensura:soul_eater")));
            if(!engraving.value().canEnchant(bow)) throw new IllegalStateException("Illegal Soul Eater item");
            if(!spec.mode.contains("plain")) bow.enchant(engraving,1);
            if(royal) {
                if(!bow.has(TensuraDataComponents.EP.get())) throw new IllegalStateException("No native gear conversion");
                bow.set(TensuraDataComponents.EP.get(),spec.mode.endsWith("s7") ? 2_490_000D : 1000D);
            }
            Vec3 delta=target.getBoundingBox().getCenter().subtract(player.getEyePosition());
            player.setYRot((float)Math.toDegrees(Math.atan2(-delta.x,delta.z)));
            player.setXRot((float)-Math.toDegrees(Math.atan2(delta.y,delta.horizontalDistance()))); player.yHeadRot=player.getYRot();
            row=new JsonObject(); row.addProperty("case",index); row.addProperty("mode",spec.mode); row.addProperty("target",spec.target);
            row.addProperty("target_id",entityId(target)); row.addProperty("target_uuid",target.getStringUUID()); row.addProperty("owner_uuid",player.getStringUUID());
            row.addProperty("bow",bow.getItem().toString()); row.addProperty("legal_enchantment",true); row.addProperty("enchanted",!spec.mode.contains("plain"));
            row.addProperty("stage",ProductionStageScaling.stage(bow).map(Enum::name).orElse("NONE"));
            row.addProperty("owner_creative",player.getAbilities().instabuild); row.add("owner_skills",skills(player)); row.add("target_skills",skills(target));
            row.addProperty("l2_initialized",l2Cap!=null && Boolean.TRUE.equals(call(l2Cap,"isInitialized"))); row.addProperty("l2_level",l2Cap==null ? 0 : ((Number)call(l2Cap,"getLevel")).intValue());
            if(!spec.target.equals("neutral") && !row.get("l2_initialized").getAsBoolean()) throw new IllegalStateException("L2 not initialized");
            row.addProperty("target_no_ai",target instanceof Mob mob && mob.isNoAi()); row.add("traits",traits());
            row.addProperty("target_tick_at_release",target.tickCount); row.addProperty("native_immune",TensuraDamageHelper.hasSpiritualDamageImmunity(level,target,player));
            row.addProperty("spiritual_resistance",toggled(target,"SPIRITUAL_ATTACK_RESISTANCE")); row.addProperty("spiritual_nullification",toggled(target,"SPIRITUAL_ATTACK_NULLIFICATION"));
            row.add("pre",snapshot());
            bow.use(level,player,InteractionHand.MAIN_HAND);
            if(!player.isUsingItem()) throw new IllegalStateException("Bow use rejected");
            bow.releaseUsing(level,player,bow.getUseDuration(player)-20); player.stopUsingItem();
            var spawned=level.getEntitiesOfClass(Projectile.class,player.getBoundingBox().inflate(32),entity -> entity.getOwner()==player);
            row.addProperty("spawn_count",spawned.size());
            if(spawned.size()!=1 || !(spawned.getFirst() instanceof AbstractArrow)) throw new IllegalStateException("Unexpected release");
            projectile=(AbstractArrow)spawned.getFirst();
            row.addProperty("projectile",entityId(projectile)); row.addProperty("projectile_uuid",projectile.getStringUUID());
            row.addProperty("owner_retained",projectile.getOwner()==player); row.addProperty("weapon_retained",projectile.getWeaponItem()!=null);
            row.addProperty("weapon_soul_level",projectile.getWeaponItem()==null ? -1 : projectile.getWeaponItem().getEnchantmentLevel(engraving));
            row.addProperty("can_hit",Boolean.TRUE.equals(call(projectile,"canHitEntity",target)));
            row.addProperty("base_damage",projectile.getBaseDamage()); row.addProperty("speed",projectile.getDeltaMovement().length());
            row.addProperty("delivery",royal ? (spec.mode.contains("legacy") ? "legacy_collision" : "native_final_lane_ticks") : "native_free_ticks");
            if(royal) {
                // The same final lane as the accepted historical fixture, followed by real ticks in native mode.
                // No collision, hit-admission, damage, critical roll or cooldown is supplied by this setup.
                Vec3 aim=target.getBoundingBox().getCenter(); Vec3 direction=aim.subtract(projectile.position()).normalize();
                double speed=projectile.getDeltaMovement().length(); projectile.setPos(aim.subtract(direction.scale(2))); projectile.setDeltaMovement(direction.scale(speed));
            }
            releaseTick=server.getTickCount(); running=true;
            if(spec.mode.contains("legacy")) {
                call(projectile,"setMarking",false); projectile.setCritArrow(false);
                Vec3 aim=target.getBoundingBox().getCenter(); Vec3 direction=aim.subtract(projectile.position()).normalize();
                double speed=projectile.getDeltaMovement().length(); projectile.setPos(aim.subtract(direction.scale(2))); projectile.setDeltaMovement(direction.scale(speed));
                if(!Boolean.TRUE.equals(call(projectile,"canHitEntity",target))) throw new IllegalStateException("Legacy collision rejected");
                call(projectile,"onHitEntity",new EntityHitResult(target)); row.add("legacy_immediate",snapshot()); projectile.discard();
            }
        }
        JsonObject snapshot() {
            JsonObject value=new JsonObject(); var targetStorage=TensuraStorages.getExistenceFrom(target); var ownerStorage=TensuraStorages.getExistenceFrom(player);
            value.addProperty("hp",target.getHealth()); value.addProperty("shp",targetStorage.getSpiritualHealth());
            value.addProperty("target_magicule",targetStorage.getMagicule()); value.addProperty("target_aura",targetStorage.getAura());
            value.addProperty("owner_hp",player.getHealth()); value.addProperty("owner_shp",ownerStorage.getSpiritualHealth());
            value.addProperty("owner_magicule",ownerStorage.getMagicule()); value.addProperty("owner_aura",ownerStorage.getAura());
            value.addProperty("cooldown",target.invulnerableTime); value.addProperty("target_tick",target.tickCount);
            value.addProperty("target_position",target.position().toString());
            if(projectile!=null) { value.addProperty("projectile_position",projectile.position().toString()); value.addProperty("projectile_motion",projectile.getDeltaMovement().toString()); }
            if(cases.get(index).target.equals("gazel_dwargo")) value.addProperty("native_phase",((Number)call(target,"getPhase")).intValue());
            JsonArray effects=new JsonArray(); target.getActiveEffects().forEach(effect -> effects.add(effect.toString())); value.add("effects",effects);
            return value;
        }
        JsonObject trace(String name) {
            JsonObject trace=snapshot(); trace.addProperty("boundary",name); trace.addProperty("relative_tick",server.getTickCount()-releaseTick);
            trace.addProperty("projectile_age",projectile.tickCount); return trace;
        }
        JsonObject traits() {
            JsonObject result=new JsonObject(); if(l2Cap!=null) ((Map<?,?>)read(l2Cap,"traits")).forEach((trait,rank)->result.addProperty(traitId(trait),(Number)rank)); return result;
        }
        void complete() {
            row.add("post",snapshot()); row.add("traits_after",traits()); row.add("traces",traces);
            row.addProperty("projectile_age_end",projectile.tickCount); row.addProperty("projectile_removed",projectile.isRemoved());
            row.addProperty("observation_ticks",server.getTickCount()-releaseTick); log("row",row);
            cleanup(); index++; step=0;
        }
        void cleanup() {
            running=false; if(projectile!=null) projectile.discard(); if(target!=null) target.discard();
            if(player!=null) { player.getInventory().clearContent(); player.setPos(1280.5,-200,1280.5); }
            projectile=null; target=null; player=null; l2Cap=null;
        }
        void finish(boolean success) {
            cleanup(); if(!alreadyForced) level.setChunkForced(80,80,false);
            JsonObject result=new JsonObject(); result.addProperty("status",success ? "complete":"error"); result.addProperty("completed_cases",index);
            result.addProperty("requested_cases",cases.size()); result.addProperty("force_load_restored",true); log("suite_result",result);
            active=null; server.halt(false);
        }
    }
    private record Case(String target,String mode) { }
    private static boolean toggled(LivingEntity entity,String name) {
        Object skill=call(staticField("io.github.manasmods.tensura.registry.skill.ResistanceSkills",name),"get");
        return Boolean.TRUE.equals(call(type("io.github.manasmods.tensura.ability.SkillUtils"),"isSkillToggled",entity,skill));
    }
    private static JsonArray skills(LivingEntity entity) {
        JsonArray result=new JsonArray(); Object skills=call(type("io.github.manasmods.manascore.skill.api.SkillAPI"),"getSkillsFrom",entity);
        for(Object skill:(Collection<?>)call(skills,"getLearnedSkills")) result.add(call(skill,"toNBT").toString()); return result;
    }
    private static String entityId(Entity entity) { return entity==null ? "NONE":BuiltInRegistries.ENTITY_TYPE.getKey(entity.getType()).toString(); }
    private static ResourceLocation id(String id) { return ResourceLocation.parse(id); }
    private static String traitId(Object trait) { return String.valueOf(call(Phase5FSuiteBBenchmark.class,"traitId",trait)); }
    private static Class<?> type(String name) { try { return Class.forName(name); } catch(ReflectiveOperationException e) { throw new IllegalStateException(e); } }
    private static Object staticField(String name,String field) { try { return type(name).getField(field).get(null); } catch(ReflectiveOperationException e) { throw new IllegalStateException(e); } }
    private static Field field(Class<?> type,String name) {
        for(Class<?> current=type;current!=null;current=current.getSuperclass()) {
            try { Field field=current.getDeclaredField(name); field.setAccessible(true); return field; } catch(NoSuchFieldException ignored) { }
        } throw new IllegalStateException("Missing field "+name);
    }
    private static Object read(Object object,String name) { try { return field(object.getClass(),name).get(object); } catch(ReflectiveOperationException e) { throw new IllegalStateException(e); } }
    private static Object staticPrivate(String name) { try { return field(Phase5FSuiteBBenchmark.class,name).get(null); } catch(ReflectiveOperationException e) { throw new IllegalStateException(e); } }
    private static Object call(Object target,String name,Object... args) {
        try { Method method=Phase5FSuiteBBenchmark.class.getDeclaredMethod("invoke",Object.class,String.class,Object[].class); method.setAccessible(true); return method.invoke(null,target,name,args); }
        catch(ReflectiveOperationException e) { throw new IllegalStateException("Native read/call failed: "+name,e); }
    }
    private static void log(String kind,JsonObject value) {
        value.addProperty("schema","tno.phase6.soul_native_path.runtime.v1"); value.addProperty("kind",kind); TNOTensuraCompat.LOGGER.info("TNO_SOUL_NATIVE_PATH "+value);
    }
}
