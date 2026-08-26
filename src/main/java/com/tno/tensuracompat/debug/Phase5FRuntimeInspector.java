package com.tno.tensuracompat.debug;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.mojang.brigadier.Command;
import com.mojang.brigadier.context.CommandContext;
import com.mojang.logging.LogUtils;
import io.github.manasmods.tensura.registry.attribute.TensuraAttributes;
import io.github.manasmods.tensura.storage.TensuraStorages;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.commands.arguments.EntityArgument;
import net.minecraft.core.Holder;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.enchantment.Enchantment;
import net.minecraft.world.item.enchantment.ItemEnchantments;
import net.neoforged.fml.ModList;
import net.neoforged.fml.loading.FMLEnvironment;
import net.neoforged.neoforge.event.RegisterCommandsEvent;
import net.neoforged.neoforge.event.server.ServerStartedEvent;
import net.neoforged.neoforge.event.tick.ServerTickEvent;
import org.slf4j.Logger;

import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Comparator;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;

/**
 * Development-only, read-only runtime inspection for the Phase 5F benchmark.
 *
 * <p>Every Apotheosis and L2 Hostility access is reflective so neither mod is a
 * linkage dependency. Registration is additionally guarded by
 * {@link FMLEnvironment#production}, leaving release runtimes inert.</p>
 */
public final class Phase5FRuntimeInspector {
    private static final Logger LOGGER = LogUtils.getLogger();
    private static final Gson GSON = new GsonBuilder().disableHtmlEscaping().create();
    private static final String LOG_MARKER = "TNO_PHASE5F";
    private static final ResourceLocation ROYAL_BOW = id("royalvariations", "royal_bow");

    private static final String APOTH_AFFIX_HELPER = "dev.shadowsoffire.apotheosis.affix.AffixHelper";
    private static final String APOTH_AFFIX = "dev.shadowsoffire.apotheosis.affix.Affix";
    private static final String APOTH_AFFIX_REGISTRY = "dev.shadowsoffire.apotheosis.affix.AffixRegistry";
    private static final String APOTH_LOOT_CATEGORY = "dev.shadowsoffire.apotheosis.loot.LootCategory";
    private static final String APOTH_RARITY_REGISTRY = "dev.shadowsoffire.apotheosis.loot.RarityRegistry";
    private static final String APOTH_SOCKET_HELPER = "dev.shadowsoffire.apotheosis.socket.SocketHelper";
    private static final String L2_MISC_REGISTRY = "dev.xkmc.l2hostility.init.registrate.LHMiscs";

    private static final List<ResourceLocation> RELEVANT_ATTRIBUTES = List.of(
            id("apothic_attributes", "arrow_damage"),
            id("apothic_attributes", "arrow_velocity"),
            id("apothic_attributes", "draw_speed"),
            id("apothic_attributes", "armor_pierce"),
            id("apothic_attributes", "armor_shred"),
            id("apothic_attributes", "prot_pierce"),
            id("apothic_attributes", "prot_shred"),
            id("apothic_attributes", "crit_chance"),
            id("apothic_attributes", "crit_damage"),
            id("manascore_attribute", "critical_attack_chance"),
            id("tensura", "earth_boost"),
            id("tensura", "flame_boost"),
            id("tensura", "lightning_boost"),
            id("tensura", "space_boost"),
            id("tensura", "water_boost"),
            id("tensura", "wind_boost"),
            id("tensura", "warp_shot"),
            id("tensura", "projectile_dodge_chance")
    );

    private static final List<String> RELEVANT_MODS = List.of(
            "royalvariations",
            "apotheosis",
            "apothic_attributes",
            "apothic_enchanting",
            "apothic_equipment",
            "ancientreforging",
            "apothicnightmares",
            "apotheosis_balance",
            "l2hostility",
            "l2library",
            "l2complements"
    );
    private static boolean startupTargetLogged;
    private static int startupTargetScanCount;

    private Phase5FRuntimeInspector() {
    }

    public static void onRegisterCommands(RegisterCommandsEvent event) {
        if (FMLEnvironment.production) {
            return;
        }

        event.getDispatcher().register(Commands.literal("tno_phase5f")
                .requires(source -> source.hasPermission(2))
                .then(Commands.literal("bow").executes(Phase5FRuntimeInspector::inspectHeldBow))
                .then(Commands.literal("apo_benchmark").executes(Phase5FApotheosisBenchmark::start))
                .then(Commands.literal("target")
                        .then(Commands.argument("entity", EntityArgument.entity())
                                .executes(Phase5FRuntimeInspector::inspectTarget))));
    }

    public static void onServerStarted(ServerStartedEvent event) {
        startupTargetLogged = false;
        startupTargetScanCount = 0;
        if (FMLEnvironment.production || !ModList.get().isLoaded("apotheosis")) {
            return;
        }

        Item item = BuiltInRegistries.ITEM.get(ROYAL_BOW);
        if (item == Items.AIR) {
            LOGGER.info("{} {}", LOG_MARKER, GSON.toJson(errorReport("bow_startup", "royal_bow_not_registered")));
            return;
        }

        JsonObject report = inspectBow(new ItemStack(item), null, event.getServer(), "startup_template");
        LOGGER.info("{} {}", LOG_MARKER, GSON.toJson(report));
    }

    public static void onServerTick(ServerTickEvent.Post event) {
        if (FMLEnvironment.production || startupTargetLogged || startupTargetScanCount >= 20
                || event.getServer().getTickCount() % 100 != 0) {
            return;
        }

        startupTargetScanCount++;
        for (var level : event.getServer().getAllLevels()) {
            for (Entity entity : level.getAllEntities()) {
                if (entity instanceof LivingEntity living && !(living instanceof ServerPlayer)) {
                    JsonObject report = inspectLivingTarget(living, "startup_sample");
                    LOGGER.info("{} {}", LOG_MARKER, GSON.toJson(report));
                    startupTargetLogged = true;
                    return;
                }
            }
        }
    }

    private static int inspectHeldBow(CommandContext<CommandSourceStack> context) {
        try {
            ServerPlayer player = context.getSource().getPlayerOrException();
            JsonObject report = inspectBow(player.getMainHandItem(), player, context.getSource().getServer(), "held_item");
            emit(context.getSource(), report);
            return Command.SINGLE_SUCCESS;
        }
        catch (Exception exception) {
            return emitFailure(context.getSource(), "bow", exception);
        }
    }

    private static int inspectTarget(CommandContext<CommandSourceStack> context) {
        try {
            Entity entity = EntityArgument.getEntity(context, "entity");
            if (!(entity instanceof LivingEntity living)) {
                context.getSource().sendFailure(Component.literal("Target must be a LivingEntity."));
                return 0;
            }

            JsonObject report = inspectLivingTarget(living, "command");
            emit(context.getSource(), report);
            return Command.SINGLE_SUCCESS;
        }
        catch (Exception exception) {
            return emitFailure(context.getSource(), "target", exception);
        }
    }

    private static JsonObject inspectBow(ItemStack stack, ServerPlayer player, MinecraftServer server, String trigger) {
        JsonObject report = baseReport("bow", trigger);
        ResourceLocation itemId = BuiltInRegistries.ITEM.getKey(stack.getItem());
        report.addProperty("item_id", itemId.toString());
        report.addProperty("is_royal_bow", ROYAL_BOW.equals(itemId));
        report.addProperty("count", stack.getCount());
        report.add("mods", loadedMods());

        JsonObject apotheosis = new JsonObject();
        report.add("apotheosis", apotheosis);
        if (!ModList.get().isLoaded("apotheosis")) {
            apotheosis.addProperty("status", "mod_absent");
            addEnchantments(report, stack, server);
            return report;
        }

        try {
            Object category = callStatic(APOTH_LOOT_CATEGORY, "forItem", stack);
            String categoryId = String.valueOf(invoke(category, "getKey"));
            boolean categoryValid = booleanValue(invoke(category, "isValid", stack));
            boolean categoryNone = booleanValue(invoke(category, "isNone"));
            apotheosis.addProperty("status", "ok");
            apotheosis.addProperty("loot_category", categoryId);
            apotheosis.addProperty("category_accepts_stack", categoryValid);
            apotheosis.addProperty("affixable", categoryValid && !categoryNone);
            apotheosis.addProperty("is_bow_category", "apotheosis:bow".equals(categoryId));

            Object rarityHolder = callStatic(APOTH_AFFIX_HELPER, "getRarity", stack);
            Object currentRarity = holderValue(rarityHolder).orElse(null);
            apotheosis.addProperty("rarity", holderId(rarityHolder));
            if (currentRarity != null) {
                apotheosis.addProperty("rarity_sort_index", numberValue(invoke(currentRarity, "sortIndex")).intValue());
                apotheosis.add("rarity_rule_limits", inspectRuleLimits(currentRarity, category));
            }

            RarityResult rarities = inspectRarities(stack, category, server);
            apotheosis.add("available_rarities", rarities.rarityArray());
            apotheosis.addProperty("maximum_declared_rarity", rarities.maximumDeclaredId());
            apotheosis.addProperty("maximum_obtainable_rarity", rarities.maximumObtainableId());
            apotheosis.addProperty("maximum_rule_complete_rarity", rarities.maximumRuleCompleteId());
            if (rarities.maximumObtainableRarity() != null) {
                apotheosis.add("maximum_obtainable_rarity_rule_limits",
                        inspectRuleLimits(rarities.maximumObtainableRarity(), category));
                apotheosis.add("maximum_obtainable_rarity_affix_pool",
                        inspectLegalAffixPool(stack, category, rarities.maximumObtainableRarity()).json());
            }
            if (rarities.maximumRuleCompleteRarity() != null) {
                apotheosis.add("maximum_rule_complete_rarity_rule_limits",
                        inspectRuleLimits(rarities.maximumRuleCompleteRarity(), category));
            }

            apotheosis.add("affixes", inspectAffixes(stack));
            apotheosis.add("sockets", inspectSockets(stack));
            apotheosis.add("attributes", inspectAttributes(stack, player));

            JsonObject recipes = new JsonObject();
            recipes.addProperty("sigil_of_supremacy_recipe",
                    server.getRecipeManager().byKey(id("apotheosis", "supremacy")).isPresent());
            recipes.addProperty("sigil_add_sockets_recipe",
                    server.getRecipeManager().byKey(id("apotheosis", "sigil_add_sockets")).isPresent());
            apotheosis.add("recipes", recipes);
        }
        catch (Throwable throwable) {
            apotheosis.addProperty("status", "inspection_error");
            apotheosis.addProperty("error", summarize(throwable));
            LOGGER.debug("Phase 5F Apotheosis inspection failed", throwable);
        }

        addEnchantments(report, stack, server);
        return report;
    }

    private static JsonObject inspectLivingTarget(LivingEntity living, String trigger) {
        JsonObject report = baseReport("target", trigger);
        report.addProperty("entity_id", BuiltInRegistries.ENTITY_TYPE.getKey(living.getType()).toString());
        report.addProperty("uuid", living.getUUID().toString());
        report.addProperty("health", living.getHealth());
        report.addProperty("max_health", living.getMaxHealth());
        report.addProperty("armor", living.getArmorValue());
        report.addProperty("armor_toughness", living.getAttributeValue(net.minecraft.world.entity.ai.attributes.Attributes.ARMOR_TOUGHNESS));
        report.add("tensura", inspectTensuraHealth(living));
        report.add("l2_hostility", inspectL2(living));
        report.add("mods", loadedMods());
        return report;
    }

    private static JsonObject inspectTensuraHealth(LivingEntity living) {
        JsonObject tensura = new JsonObject();
        try {
            var existence = TensuraStorages.getExistenceFrom(living);
            tensura.addProperty("status", "ok");
            addTensuraResource(tensura, living, "spiritual_health", existence.getSpiritualHealth(),
                    TensuraAttributes.MAX_SPIRITUAL_HEALTH);
            addTensuraResource(tensura, living, "magicule", existence.getMagicule(), TensuraAttributes.MAX_MAGICULE);
            addTensuraResource(tensura, living, "aura", existence.getAura(), TensuraAttributes.MAX_AURA);
            tensura.addProperty("l2_scaling_marker", living.getTags().contains("l2_tensura_scaled"));
        }
        catch (Throwable throwable) {
            tensura.addProperty("status", "unavailable");
            tensura.addProperty("error", summarize(throwable));
        }
        return tensura;
    }

    private static void addTensuraResource(JsonObject report, LivingEntity living, String name, double current,
            Holder<Attribute> maximumAttribute) {
        report.addProperty(name, current);
        var instance = living.getAttribute(maximumAttribute);
        if (instance == null) {
            report.add("base_max_" + name, null);
            report.add("max_" + name, null);
            report.add("max_" + name + "_multiplier", null);
            return;
        }
        double base = instance.getBaseValue();
        double maximum = instance.getValue();
        report.addProperty("base_max_" + name, base);
        report.addProperty("max_" + name, maximum);
        report.addProperty("max_" + name + "_multiplier", base == 0.0D ? 0.0D : maximum / base);
    }

    private static JsonObject inspectL2(LivingEntity living) {
        JsonObject l2 = new JsonObject();
        if (!ModList.get().isLoaded("l2hostility")) {
            l2.addProperty("status", "mod_absent");
            return l2;
        }

        try {
            Class<?> misc = Class.forName(L2_MISC_REGISTRY);
            Object mobEntry = misc.getField("MOB").get(null);
            Object attachmentType = invoke(mobEntry, "type");
            Object optionalCap = invoke(attachmentType, "getExisting", living);
            Object cap = optionalValue(optionalCap).orElse(null);
            if (cap == null) {
                l2.addProperty("status", "no_attachment");
                return l2;
            }

            l2.addProperty("status", "ok");
            l2.addProperty("initialized", booleanValue(invoke(cap, "isInitialized")));
            l2.addProperty("level", numberValue(invoke(cap, "getLevel")).intValue());

            JsonArray traits = new JsonArray();
            Object traitMapValue = readField(cap, "traits");
            if (traitMapValue instanceof Map<?, ?> traitMap) {
                traitMap.entrySet().stream()
                        .sorted(Comparator.comparing(entry -> traitId(entry.getKey())))
                        .forEach(entry -> {
                            JsonObject trait = new JsonObject();
                            trait.addProperty("id", traitId(entry.getKey()));
                            trait.addProperty("rank", numberValue(entry.getValue()).intValue());
                            try {
                                trait.addProperty("max_rank",
                                        numberValue(invoke(entry.getKey(), "getMaxLevel", living.registryAccess())).intValue());
                            }
                            catch (Throwable ignored) {
                                trait.add("max_rank", null);
                            }
                            traits.add(trait);
                        });
            }
            l2.add("traits", traits);
            l2.addProperty("trait_count", traits.size());
        }
        catch (Throwable throwable) {
            l2.addProperty("status", "inspection_error");
            l2.addProperty("error", summarize(throwable));
            LOGGER.debug("Phase 5F L2 inspection failed", throwable);
        }
        return l2;
    }

    private static JsonObject inspectAffixes(ItemStack stack) throws ReflectiveOperationException {
        JsonObject result = new JsonObject();
        Object affixMapValue = callStatic(APOTH_AFFIX_HELPER, "getAffixes", stack);
        JsonArray entries = new JsonArray();
        boolean everyAffixAtSupremacyFloor = true;

        if (affixMapValue instanceof Map<?, ?> affixMap) {
            List<Map.Entry<?, ?>> sorted = new ArrayList<>(affixMap.entrySet());
            sorted.sort(Comparator.comparing(entry -> holderId(entry.getKey())));
            for (Map.Entry<?, ?> entry : sorted) {
                Object instance = entry.getValue();
                float storedLevel = numberValue(invoke(instance, "level")).floatValue();
                float effectiveLevel = Math.clamp(storedLevel, 0.0F, 2.0F);
                JsonObject affix = new JsonObject();
                affix.addProperty("id", holderId(entry.getKey()));
                affix.addProperty("raw_stored_level", storedLevel);
                affix.addProperty("effective_level", effectiveLevel);
                affix.addProperty("displayed_level", String.valueOf(callStatic(APOTH_AFFIX, "fmt", effectiveLevel)));
                affix.addProperty("rarity", holderId(invoke(instance, "rarity")));
                affix.addProperty("valid", booleanValue(invoke(instance, "isValid")));
                affix.addProperty("supremacy_floor_reached", storedLevel >= 1.5F);
                affix.addProperty("pre_supremacy_level_available", false);

                Object affixValue = invoke(instance, "getAffix");
                Object definition = invoke(affixValue, "definition");
                Object type = invoke(definition, "type");
                affix.addProperty("type", String.valueOf(invoke(type, "getSerializedName")));
                affix.add("exclusive_with", holderCollection(invoke(definition, "exclusiveSet")));
                entries.add(affix);
                everyAffixAtSupremacyFloor &= storedLevel >= 1.5F;
            }
        }

        result.add("entries", entries);
        result.addProperty("count", entries.size());
        result.addProperty("supremacy_inferred", entries.size() > 0 && everyAffixAtSupremacyFloor);
        result.addProperty("supremacy_detection",
                "inferred when every stored affix level is at least the recipe floor of 1.5; Apotheosis stores no separate marker");
        return result;
    }

    private static JsonObject inspectSockets(ItemStack stack) throws ReflectiveOperationException {
        JsonObject result = new JsonObject();
        int socketCount = numberValue(callStatic(APOTH_SOCKET_HELPER, "getSockets", stack)).intValue();
        Object gemsValue = callStatic(APOTH_SOCKET_HELPER, "getGems", stack);
        JsonArray gems = new JsonArray();
        Map<String, Integer> uniqueGemCounts = new HashMap<>();

        if (gemsValue instanceof Iterable<?> iterable) {
            for (Object instance : iterable) {
                boolean valid = booleanValue(invoke(instance, "isValid"));
                JsonObject gem = new JsonObject();
                gem.addProperty("slot", numberValue(invoke(instance, "slot")).intValue());
                gem.addProperty("valid", valid);
                if (valid) {
                    Object holder = invoke(instance, "gem");
                    String gemId = holderId(holder);
                    Object gemValue = invoke(instance, "getGem");
                    boolean unique = booleanValue(invoke(gemValue, "isUnique"));
                    gem.addProperty("id", gemId);
                    gem.addProperty("purity", String.valueOf(invoke(invoke(instance, "purity"), "getSerializedName")));
                    gem.addProperty("unique", unique);
                    gem.add("bonus", inspectGemBonus(instance));
                    if (unique) {
                        uniqueGemCounts.merge(gemId, 1, Integer::sum);
                    }
                }
                else {
                    gem.add("id", null);
                }
                gems.add(gem);
            }
        }

        JsonArray uniquenessViolations = new JsonArray();
        uniqueGemCounts.forEach((gemId, count) -> {
            if (count > 1) {
                JsonObject violation = new JsonObject();
                violation.addProperty("id", gemId);
                violation.addProperty("count", count);
                uniquenessViolations.add(violation);
            }
        });

        result.addProperty("effective_socket_count", socketCount);
        result.add("gems", gems);
        result.add("unique_gem_violations", uniquenessViolations);
        result.addProperty("all_unique_constraints_satisfied", uniquenessViolations.isEmpty());
        return result;
    }

    private static JsonObject inspectGemBonus(Object gemInstance) {
        JsonObject result = new JsonObject();
        try {
            Object optionalBonus = invoke(gemInstance, "getBonus");
            Object bonus = optionalValue(optionalBonus).orElse(null);
            if (bonus == null) {
                result.addProperty("status", "none_for_category_or_purity");
                return result;
            }

            result.addProperty("status", "ok");
            result.addProperty("type", String.valueOf(invoke(bonus, "getTypeKey")));
            Object gemClass = invoke(bonus, "getGemClass");
            result.addProperty("gem_class", String.valueOf(invoke(gemClass, "key")));
            Object purity = invoke(gemInstance, "purity");

            if (bonus.getClass().getName().endsWith("AttributeBonus")) {
                result.addProperty("attribute", holderId(readField(bonus, "attribute")));
                result.addProperty("operation", String.valueOf(readField(bonus, "operation")));
                Object values = readField(bonus, "values");
                if (values instanceof Map<?, ?> valueMap && valueMap.get(purity) instanceof Number value) {
                    result.addProperty("value", value.doubleValue());
                }
            }
            else if (bonus.getClass().getName().endsWith("MultiAttrBonus")) {
                JsonArray modifiers = new JsonArray();
                Object modifierValue = readField(bonus, "modifiers");
                if (modifierValue instanceof Collection<?> collection) {
                    for (Object modifier : collection) {
                        JsonObject json = new JsonObject();
                        json.addProperty("attribute", holderId(invoke(modifier, "attr")));
                        json.addProperty("operation", String.valueOf(invoke(modifier, "op")));
                        Object values = invoke(modifier, "values");
                        if (values instanceof Map<?, ?> valueMap && valueMap.get(purity) instanceof Number value) {
                            json.addProperty("value", value.doubleValue());
                        }
                        modifiers.add(json);
                    }
                }
                result.add("modifiers", modifiers);
            }
        }
        catch (Throwable throwable) {
            result.addProperty("status", "inspection_error");
            result.addProperty("error", summarize(throwable));
        }
        return result;
    }

    private static JsonObject inspectAttributes(ItemStack stack, ServerPlayer player) {
        JsonObject result = new JsonObject();
        Map<String, JsonArray> rawModifiers = new LinkedHashMap<>();
        for (ResourceLocation id : RELEVANT_ATTRIBUTES) {
            rawModifiers.put(id.toString(), new JsonArray());
        }

        stack.forEachModifier(EquipmentSlot.MAINHAND, (attribute, modifier) -> {
            String attributeId = holderId(attribute);
            JsonArray modifiers = rawModifiers.get(attributeId);
            if (modifiers != null) {
                JsonObject json = new JsonObject();
                json.addProperty("id", modifier.id().toString());
                json.addProperty("amount", modifier.amount());
                json.addProperty("operation", modifier.operation().getSerializedName());
                modifiers.add(json);
            }
        });

        for (ResourceLocation id : RELEVANT_ATTRIBUTES) {
            JsonObject attribute = new JsonObject();
            attribute.add("raw_mainhand_modifiers", rawModifiers.get(id.toString()));
            Optional<Holder.Reference<Attribute>> holder = BuiltInRegistries.ATTRIBUTE.getHolder(id);
            attribute.addProperty("registered", holder.isPresent());
            if (player != null && holder.isPresent() && player.getAttributes().hasAttribute(holder.get())) {
                attribute.addProperty("player_base_value", player.getAttributeBaseValue(holder.get()));
                attribute.addProperty("player_effective_value", player.getAttributeValue(holder.get()));
            }
            else {
                attribute.add("player_base_value", null);
                attribute.add("player_effective_value", null);
            }
            result.add(id.toString(), attribute);
        }
        return result;
    }

    private static void addEnchantments(JsonObject report, ItemStack stack, MinecraftServer server) {
        JsonObject result = new JsonObject();
        JsonArray applied = new JsonArray();
        ItemEnchantments enchantments = stack.getEnchantments();
        List<Holder<Enchantment>> appliedHolders = new ArrayList<>();
        boolean appliedCompatible = true;

        for (var entry : enchantments.entrySet()) {
            Holder<Enchantment> holder = entry.getKey();
            JsonObject enchantment = new JsonObject();
            enchantment.addProperty("id", holderId(holder));
            enchantment.addProperty("level", entry.getIntValue());
            enchantment.addProperty("runtime_max_level", holder.value().getMaxLevel());
            enchantment.addProperty("supported_by_item", holder.value().canEnchant(stack));
            applied.add(enchantment);
            for (Holder<Enchantment> other : appliedHolders) {
                appliedCompatible &= Enchantment.areCompatible(holder, other);
            }
            appliedHolders.add(holder);
        }

        result.add("applied", applied);
        result.addProperty("applied_count", applied.size());
        result.addProperty("applied_pairwise_compatible", appliedCompatible);

        try {
            HolderLookup.RegistryLookup<Enchantment> registry = server.registryAccess()
                    .lookup(Registries.ENCHANTMENT).orElseThrow();
            List<Holder.Reference<Enchantment>> supported = registry.listElements()
                    .filter(holder -> holder.value().canEnchant(stack))
                    .sorted(Comparator.comparing(Phase5FRuntimeInspector::holderId))
                    .toList();

            JsonArray legal = new JsonArray();
            for (Holder.Reference<Enchantment> holder : supported) {
                JsonObject enchantment = new JsonObject();
                enchantment.addProperty("id", holderId(holder));
                enchantment.addProperty("runtime_max_level", holder.value().getMaxLevel());
                legal.add(enchantment);
            }
            result.add("item_supported_enchantments", legal);

            List<Holder.Reference<Enchantment>> maximumSet = maximumCompatibleEnchantments(supported);
            JsonArray maximum = new JsonArray();
            for (Holder.Reference<Enchantment> holder : maximumSet) {
                JsonObject enchantment = new JsonObject();
                enchantment.addProperty("id", holderId(holder));
                enchantment.addProperty("runtime_max_level", holder.value().getMaxLevel());
                maximum.add(enchantment);
            }
            result.add("maximum_pairwise_compatible_set", maximum);
            result.addProperty("maximum_pairwise_compatible_count", maximum.size());
        }
        catch (Throwable throwable) {
            result.addProperty("legal_set_status", "inspection_error");
            result.addProperty("error", summarize(throwable));
        }

        report.add("enchantments", result);
    }

    private static List<Holder.Reference<Enchantment>> maximumCompatibleEnchantments(
            List<Holder.Reference<Enchantment>> supported) {
        List<Holder.Reference<Enchantment>> best = new ArrayList<>();
        findMaximumCompatibleSet(supported, 0, new ArrayList<>(), best);
        return best;
    }

    private static void findMaximumCompatibleSet(List<Holder.Reference<Enchantment>> candidates, int start,
            List<Holder.Reference<Enchantment>> current, List<Holder.Reference<Enchantment>> best) {
        if (current.size() + candidates.size() - start <= best.size()) {
            return;
        }

        for (int index = start; index < candidates.size(); index++) {
            Holder.Reference<Enchantment> candidate = candidates.get(index);
            boolean compatible = current.stream().allMatch(existing -> Enchantment.areCompatible(existing, candidate));
            if (compatible) {
                current.add(candidate);
                if (current.size() > best.size()) {
                    best.clear();
                    best.addAll(current);
                }
                findMaximumCompatibleSet(candidates, index + 1, current, best);
                current.removeLast();
            }
        }
    }

    private static RarityResult inspectRarities(ItemStack stack, Object category, MinecraftServer server)
            throws ReflectiveOperationException {
        JsonArray result = new JsonArray();
        Object rarityRegistry = staticField(APOTH_RARITY_REGISTRY, "INSTANCE");
        Object sortedValue = callStatic(APOTH_RARITY_REGISTRY, "getSortedRarities");
        String maximumDeclaredId = "none";
        int maximumDeclaredSortIndex = Integer.MIN_VALUE;
        Object maximumObtainable = null;
        String maximumObtainableId = "none";
        int maximumObtainableSortIndex = Integer.MIN_VALUE;
        Object maximumRuleComplete = null;
        String maximumRuleCompleteId = "none";
        int maximumRuleCompleteSortIndex = Integer.MIN_VALUE;

        if (sortedValue instanceof Collection<?> rarities) {
            for (Object rarity : rarities) {
                String rarityId = String.valueOf(invoke(rarityRegistry, "getKey", rarity));
                int sortIndex = numberValue(invoke(rarity, "sortIndex")).intValue();
                RuleStats stats = ruleStats(rarity, category);
                LegalAffixPool pool = inspectLegalAffixPool(stack, category, rarity);
                List<AffixCandidate> selection = findMaximumConstructibleAffixSelection(
                        pool.candidates(), stats.maximumByType());
                int requiredAffixes = stats.maximumAffixes();
                boolean maximumRulesFeasible = selection.size() == requiredAffixes;
                JsonObject recipe = inspectReforgingRecipe(rarityId, server);
                boolean obtainable = recipe.get("enabled").getAsBoolean();
                JsonObject json = new JsonObject();
                json.addProperty("id", rarityId);
                json.addProperty("sort_index", sortIndex);
                json.add("rule_limits", inspectRuleLimits(rarity, category));
                json.add("legal_affix_pool", pool.json());
                json.add("reforging_recipe", recipe);
                json.addProperty("obtainable", obtainable);
                json.addProperty("maximum_affix_rules_satisfiable", maximumRulesFeasible);
                json.addProperty("maximum_constructible_affix_count", selection.size());
                json.add("maximum_constructible_affix_set", affixCandidateArray(selection));
                json.add("missing_maximum_affix_slots_by_type",
                        missingAffixSlots(stats.maximumByType(), selection));
                result.add(json);
                if (sortIndex > maximumDeclaredSortIndex) {
                    maximumDeclaredId = rarityId;
                    maximumDeclaredSortIndex = sortIndex;
                }
                if (obtainable && sortIndex > maximumObtainableSortIndex) {
                    maximumObtainable = rarity;
                    maximumObtainableId = rarityId;
                    maximumObtainableSortIndex = sortIndex;
                }
                if (maximumRulesFeasible && sortIndex > maximumRuleCompleteSortIndex) {
                    maximumRuleComplete = rarity;
                    maximumRuleCompleteId = rarityId;
                    maximumRuleCompleteSortIndex = sortIndex;
                }
            }
        }
        return new RarityResult(result, maximumDeclaredId,
                maximumObtainable, maximumObtainableId, maximumRuleComplete, maximumRuleCompleteId);
    }

    private static JsonObject inspectReforgingRecipe(String rarityId, MinecraftServer server) {
        ResourceLocation rarity = ResourceLocation.parse(rarityId);
        Set<ResourceLocation> candidates = new LinkedHashSet<>();
        candidates.add(id(rarity.getNamespace(), "reforging/" + rarity.getPath()));
        candidates.add(id("apotheosis", "reforging/" + rarity.getPath()));

        JsonArray enabledIds = new JsonArray();
        for (ResourceLocation candidate : candidates) {
            if (server.getRecipeManager().byKey(candidate).isPresent()) {
                enabledIds.add(candidate.toString());
            }
        }
        JsonObject result = new JsonObject();
        result.addProperty("enabled", !enabledIds.isEmpty());
        result.add("ids", enabledIds);
        return result;
    }

    private static JsonObject inspectRuleLimits(Object rarity, Object category) throws ReflectiveOperationException {
        RuleStats total = ruleStats(rarity, category);
        Object rulesValue = invoke(rarity, "getRules", category);
        JsonArray rules = new JsonArray();
        if (rulesValue instanceof Collection<?> collection) {
            for (Object rule : collection) {
                RuleInspection inspection = inspectRule(rule);
                rules.add(inspection.json());
            }
        }

        JsonObject result = new JsonObject();
        result.add("rules", rules);
        result.addProperty("minimum_affixes", total.minimumAffixes());
        result.addProperty("maximum_affixes", total.maximumAffixes());
        JsonObject byType = new JsonObject();
        Set<String> types = new LinkedHashSet<>();
        types.addAll(total.minimumByType().keySet());
        types.addAll(total.maximumByType().keySet());
        for (String type : types) {
            JsonObject range = new JsonObject();
            range.addProperty("min", total.minimumByType().getOrDefault(type, 0));
            range.addProperty("max", total.maximumByType().getOrDefault(type, 0));
            byType.add(type, range);
        }
        result.add("affixes_by_type", byType);
        result.addProperty("minimum_sockets", total.minimumSockets());
        result.addProperty("maximum_sockets", total.maximumSockets());
        return result;
    }

    private static RuleStats ruleStats(Object rarity, Object category) throws ReflectiveOperationException {
        RuleStats total = RuleStats.empty();
        Object rulesValue = invoke(rarity, "getRules", category);
        if (rulesValue instanceof Collection<?> collection) {
            for (Object rule : collection) {
                total = total.plus(inspectRule(rule).stats());
            }
        }
        return total;
    }

    private static RuleInspection inspectRule(Object rule) {
        JsonObject json = new JsonObject();
        String simpleName = rule.getClass().getSimpleName();
        json.addProperty("kind", simpleName);
        try {
            if (simpleName.equals("AffixLootRule")) {
                String type = String.valueOf(invoke(invoke(rule, "type"), "getSerializedName"));
                json.addProperty("affix_type", type);
                return new RuleInspection(json, RuleStats.affix(type));
            }
            if (simpleName.equals("SocketLootRule")) {
                int minimum = numberValue(invoke(rule, "min")).intValue();
                int maximum = numberValue(invoke(rule, "max")).intValue();
                json.addProperty("min", minimum);
                json.addProperty("max", maximum);
                return new RuleInspection(json, RuleStats.sockets(minimum, maximum));
            }
            if (simpleName.equals("SelectLootRule")) {
                json.addProperty("chance", numberValue(invoke(rule, "chance")).floatValue());
                RuleInspection ifTrue = inspectRule(invoke(rule, "ifTrue"));
                RuleInspection ifFalse = inspectRule(invoke(rule, "ifFalse"));
                json.add("if_true", ifTrue.json());
                json.add("if_false", ifFalse.json());
                return new RuleInspection(json, RuleStats.choose(ifTrue.stats(), ifFalse.stats()));
            }
            if (simpleName.equals("ChancedLootRule")) {
                json.addProperty("chance", numberValue(invoke(rule, "chance")).floatValue());
                RuleInspection nested = inspectRule(invoke(rule, "rule"));
                json.add("rule", nested.json());
                return new RuleInspection(json, RuleStats.optional(nested.stats()));
            }
            if (simpleName.equals("CombinedLootRule")) {
                RuleStats combinedStats = RuleStats.empty();
                JsonArray combinedRules = new JsonArray();
                Object nestedRules = invoke(rule, "rules");
                if (nestedRules instanceof Collection<?> collection) {
                    for (Object nestedRule : collection) {
                        RuleInspection nested = inspectRule(nestedRule);
                        combinedStats = combinedStats.plus(nested.stats());
                        combinedRules.add(nested.json());
                    }
                }
                json.add("rules", combinedRules);
                return new RuleInspection(json, combinedStats);
            }
            json.addProperty("description", String.valueOf(rule));
        }
        catch (Throwable throwable) {
            json.addProperty("inspection_error", summarize(throwable));
        }
        return new RuleInspection(json, RuleStats.empty());
    }

    private static LegalAffixPool inspectLegalAffixPool(ItemStack stack, Object category, Object rarity) {
        JsonObject result = new JsonObject();
        JsonArray entries = new JsonArray();
        List<AffixCandidate> candidates = new ArrayList<>();
        int rejectedByError = 0;
        try {
            Object registry = staticField(APOTH_AFFIX_REGISTRY, "INSTANCE");
            Object values = invoke(registry, "getValues");
            if (values instanceof Collection<?> affixes) {
                List<Object> sorted = new ArrayList<>(affixes);
                sorted.sort(Comparator.comparing(affix -> affixRegistryId(registry, affix)));
                for (Object affix : sorted) {
                    try {
                        if (!booleanValue(invoke(affix, "canApplyTo", stack, category, rarity))) {
                            continue;
                        }
                        JsonObject json = new JsonObject();
                        json.addProperty("id", affixRegistryId(registry, affix));
                        Object definition = invoke(affix, "definition");
                        String type = String.valueOf(invoke(invoke(definition, "type"), "getSerializedName"));
                        json.addProperty("type", type);
                        json.add("exclusive_with", holderCollection(invoke(definition, "exclusiveSet")));
                        entries.add(json);
                        candidates.add(new AffixCandidate(affixRegistryId(registry, affix), type, affix));
                    }
                    catch (Throwable ignored) {
                        rejectedByError++;
                    }
                }
            }
        }
        catch (Throwable throwable) {
            result.addProperty("status", "inspection_error");
            result.addProperty("error", summarize(throwable));
        }
        result.add("entries", entries);
        result.addProperty("count", entries.size());
        result.addProperty("rejected_by_runtime_error", rejectedByError);
        return new LegalAffixPool(result, candidates);
    }

    private static List<AffixCandidate> findMaximumConstructibleAffixSelection(List<AffixCandidate> candidates,
            Map<String, Integer> requirements) {
        List<String> slots = new ArrayList<>();
        requirements.entrySet().stream()
                .sorted(Comparator.comparingInt(entry -> countCandidates(candidates, entry.getKey())))
                .forEach(entry -> {
                    for (int count = 0; count < entry.getValue(); count++) {
                        slots.add(entry.getKey());
                    }
                });
        List<AffixCandidate> best = new ArrayList<>();
        selectMaximumAffixes(candidates, slots, 0, new ArrayList<>(), best);
        return best;
    }

    private static int countCandidates(List<AffixCandidate> candidates, String type) {
        return (int) candidates.stream().filter(candidate -> candidate.type().equals(type)).count();
    }

    private static void selectMaximumAffixes(List<AffixCandidate> candidates, List<String> slots, int slot,
            List<AffixCandidate> selected, List<AffixCandidate> best) {
        if (slot >= slots.size()) {
            if (selected.size() > best.size()) {
                best.clear();
                best.addAll(selected);
            }
            return;
        }
        if (selected.size() + slots.size() - slot <= best.size()) {
            return;
        }

        String requiredType = slots.get(slot);
        for (AffixCandidate candidate : candidates) {
            if (!candidate.type().equals(requiredType) || selected.contains(candidate)
                    || !selected.stream().allMatch(existing -> affixesCompatible(existing.value(), candidate.value()))) {
                continue;
            }
            selected.add(candidate);
            selectMaximumAffixes(candidates, slots, slot + 1, selected, best);
            selected.removeLast();
        }
        selectMaximumAffixes(candidates, slots, slot + 1, selected, best);
    }

    private static JsonObject missingAffixSlots(Map<String, Integer> requirements,
            List<AffixCandidate> selection) {
        JsonObject result = new JsonObject();
        requirements.forEach((type, required) -> {
            long selected = selection.stream().filter(candidate -> candidate.type().equals(type)).count();
            int missing = required - (int) selected;
            if (missing > 0) {
                result.addProperty(type, missing);
            }
        });
        return result;
    }

    private static boolean affixesCompatible(Object first, Object second) {
        try {
            return booleanValue(invoke(first, "isCompatibleWith", second))
                    && booleanValue(invoke(second, "isCompatibleWith", first));
        }
        catch (ReflectiveOperationException exception) {
            return false;
        }
    }

    private static JsonArray affixCandidateArray(List<AffixCandidate> candidates) {
        JsonArray result = new JsonArray();
        if (candidates != null) {
            for (AffixCandidate candidate : candidates) {
                JsonObject json = new JsonObject();
                json.addProperty("id", candidate.id());
                json.addProperty("type", candidate.type());
                result.add(json);
            }
        }
        return result;
    }

    private static String affixRegistryId(Object registry, Object affix) {
        try {
            return String.valueOf(invoke(registry, "getKey", affix));
        }
        catch (ReflectiveOperationException exception) {
            return String.valueOf(affix);
        }
    }

    private static JsonArray loadedMods() {
        JsonArray mods = new JsonArray();
        for (String modId : RELEVANT_MODS) {
            JsonObject mod = new JsonObject();
            mod.addProperty("id", modId);
            Optional<? extends net.neoforged.fml.ModContainer> container = ModList.get().getModContainerById(modId);
            mod.addProperty("loaded", container.isPresent());
            container.ifPresent(value -> mod.addProperty("version", value.getModInfo().getVersion().toString()));
            mods.add(mod);
        }
        return mods;
    }

    private static JsonObject baseReport(String kind, String trigger) {
        JsonObject report = new JsonObject();
        report.addProperty("schema", "tno.phase5f.runtime_inspector.v1");
        report.addProperty("kind", kind);
        report.addProperty("trigger", trigger);
        report.addProperty("production", FMLEnvironment.production);
        return report;
    }

    private static JsonObject errorReport(String kind, String message) {
        JsonObject report = baseReport(kind, "automatic");
        report.addProperty("status", "error");
        report.addProperty("error", message);
        return report;
    }

    private static void emit(CommandSourceStack source, JsonObject report) {
        String json = GSON.toJson(report);
        LOGGER.info("{} {}", LOG_MARKER, json);
        source.sendSuccess(() -> Component.literal(LOG_MARKER + " " + json), false);
    }

    private static int emitFailure(CommandSourceStack source, String kind, Throwable throwable) {
        JsonObject report = errorReport(kind, summarize(throwable));
        String json = GSON.toJson(report);
        LOGGER.error("{} {}", LOG_MARKER, json, throwable);
        source.sendFailure(Component.literal(LOG_MARKER + " " + json));
        return 0;
    }

    private static JsonArray holderCollection(Object value) {
        JsonArray result = new JsonArray();
        if (value instanceof Collection<?> collection) {
            collection.stream().map(Phase5FRuntimeInspector::holderId).sorted().forEach(result::add);
        }
        return result;
    }

    private static Optional<Object> holderValue(Object holder) {
        try {
            return optionalValue(invoke(holder, "getOptional"));
        }
        catch (Throwable ignored) {
            try {
                return Optional.ofNullable(invoke(holder, "get"));
            }
            catch (Throwable ignoredAgain) {
                return Optional.empty();
            }
        }
    }

    private static Optional<Object> optionalValue(Object value) {
        if (value instanceof Optional<?> optional) {
            return optional.map(element -> element);
        }
        return Optional.ofNullable(value);
    }

    private static String holderId(Object holder) {
        if (holder instanceof Holder<?> minecraftHolder) {
            return minecraftHolder.unwrapKey()
                    .map(key -> key.location().toString())
                    .orElseGet(() -> "direct:" + minecraftHolder.value());
        }
        try {
            return String.valueOf(invoke(holder, "getId"));
        }
        catch (Throwable ignored) {
            return String.valueOf(holder);
        }
    }

    private static String traitId(Object trait) {
        try {
            return String.valueOf(invoke(trait, "getRegistryName"));
        }
        catch (Throwable ignored) {
            return String.valueOf(trait);
        }
    }

    private static Object staticField(String className, String name) throws ReflectiveOperationException {
        return Class.forName(className).getField(name).get(null);
    }

    private static Object callStatic(String className, String name, Object... arguments)
            throws ReflectiveOperationException {
        return invoke(Class.forName(className), name, arguments);
    }

    private static Object invoke(Object targetOrClass, String name, Object... arguments)
            throws ReflectiveOperationException {
        Class<?> type = targetOrClass instanceof Class<?> clazz ? clazz : targetOrClass.getClass();
        Method method = findMethod(type, name, arguments);
        method.setAccessible(true);
        Object target = Modifier.isStatic(method.getModifiers()) ? null : targetOrClass;
        return method.invoke(target, arguments);
    }

    private static Method findMethod(Class<?> type, String name, Object[] arguments) throws NoSuchMethodException {
        for (Method method : type.getMethods()) {
            if (method.getName().equals(name) && compatible(method.getParameterTypes(), arguments)) {
                return method;
            }
        }
        for (Class<?> current = type; current != null; current = current.getSuperclass()) {
            for (Method method : current.getDeclaredMethods()) {
                if (method.getName().equals(name) && compatible(method.getParameterTypes(), arguments)) {
                    return method;
                }
            }
        }
        throw new NoSuchMethodException(type.getName() + "#" + name + "/" + arguments.length);
    }

    private static boolean compatible(Class<?>[] parameterTypes, Object[] arguments) {
        if (parameterTypes.length != arguments.length) {
            return false;
        }
        for (int index = 0; index < parameterTypes.length; index++) {
            if (arguments[index] == null) {
                if (parameterTypes[index].isPrimitive()) {
                    return false;
                }
                continue;
            }
            Class<?> parameter = wrap(parameterTypes[index]);
            if (!parameter.isAssignableFrom(arguments[index].getClass())) {
                return false;
            }
        }
        return true;
    }

    private static Class<?> wrap(Class<?> type) {
        if (!type.isPrimitive()) {
            return type;
        }
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
                // Continue through the inheritance chain.
            }
        }
        throw new NoSuchFieldException(target.getClass().getName() + "#" + name);
    }

    private static Number numberValue(Object value) {
        if (value instanceof Number number) {
            return number;
        }
        throw new IllegalArgumentException("Expected a number, got " + value);
    }

    private static boolean booleanValue(Object value) {
        return value instanceof Boolean bool && bool;
    }

    private static String summarize(Throwable throwable) {
        Throwable cause = throwable;
        while (cause.getCause() != null && cause.getCause() != cause) {
            cause = cause.getCause();
        }
        String message = cause.getMessage();
        return cause.getClass().getSimpleName() + (message == null ? "" : ": " + message);
    }

    private static ResourceLocation id(String namespace, String path) {
        return ResourceLocation.fromNamespaceAndPath(namespace, path);
    }

    private record RarityResult(JsonArray rarityArray, String maximumDeclaredId,
            Object maximumObtainableRarity, String maximumObtainableId,
            Object maximumRuleCompleteRarity, String maximumRuleCompleteId) {
    }

    private record LegalAffixPool(JsonObject json, List<AffixCandidate> candidates) {
    }

    private record AffixCandidate(String id, String type, Object value) {
    }

    private record RuleInspection(JsonObject json, RuleStats stats) {
    }

    private record RuleStats(Map<String, Integer> minimumByType, Map<String, Integer> maximumByType,
            int minimumSockets, int maximumSockets) {
        static RuleStats empty() {
            return new RuleStats(Map.of(), Map.of(), 0, 0);
        }

        static RuleStats affix(String type) {
            return new RuleStats(Map.of(type, 1), Map.of(type, 1), 0, 0);
        }

        static RuleStats sockets(int minimum, int maximum) {
            return new RuleStats(Map.of(), Map.of(), minimum, maximum);
        }

        static RuleStats choose(RuleStats first, RuleStats second) {
            Set<String> keys = new LinkedHashSet<>();
            keys.addAll(first.minimumByType.keySet());
            keys.addAll(second.minimumByType.keySet());
            keys.addAll(first.maximumByType.keySet());
            keys.addAll(second.maximumByType.keySet());
            Map<String, Integer> minimum = new LinkedHashMap<>();
            Map<String, Integer> maximum = new LinkedHashMap<>();
            for (String key : keys) {
                minimum.put(key, Math.min(first.minimumByType.getOrDefault(key, 0),
                        second.minimumByType.getOrDefault(key, 0)));
                maximum.put(key, Math.max(first.maximumByType.getOrDefault(key, 0),
                        second.maximumByType.getOrDefault(key, 0)));
            }
            return new RuleStats(minimum, maximum,
                    Math.min(first.minimumSockets, second.minimumSockets),
                    Math.max(first.maximumSockets, second.maximumSockets));
        }

        static RuleStats optional(RuleStats value) {
            return new RuleStats(Map.of(), value.maximumByType, 0, value.maximumSockets);
        }

        RuleStats plus(RuleStats other) {
            Set<String> keys = new LinkedHashSet<>();
            keys.addAll(minimumByType.keySet());
            keys.addAll(maximumByType.keySet());
            keys.addAll(other.minimumByType.keySet());
            keys.addAll(other.maximumByType.keySet());
            Map<String, Integer> minimum = new LinkedHashMap<>();
            Map<String, Integer> maximum = new LinkedHashMap<>();
            for (String key : keys) {
                minimum.put(key, minimumByType.getOrDefault(key, 0) + other.minimumByType.getOrDefault(key, 0));
                maximum.put(key, maximumByType.getOrDefault(key, 0) + other.maximumByType.getOrDefault(key, 0));
            }
            return new RuleStats(minimum, maximum,
                    minimumSockets + other.minimumSockets,
                    maximumSockets + other.maximumSockets);
        }

        int minimumAffixes() {
            return minimumByType.values().stream().mapToInt(Integer::intValue).sum();
        }

        int maximumAffixes() {
            return maximumByType.values().stream().mapToInt(Integer::intValue).sum();
        }
    }
}
