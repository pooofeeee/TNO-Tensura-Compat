package com.tno.tensuracompat.compat.royalvariations;

import com.tno.tensuracompat.TNOTensuraCompat;
import com.tno.tensuracompat.core.stage.GearStageClass;
import com.tno.tensuracompat.core.stage.GearStageClasses;
import io.github.manasmods.tensura.enchantment.EngravingHelper;
import io.github.manasmods.tensura.registry.item.misc.TensuraDataComponents;
import net.minecraft.core.Holder;
import net.minecraft.core.Registry;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.component.CustomData;
import net.minecraft.world.item.enchantment.Enchantment;
import net.minecraft.world.item.enchantment.EnchantmentHelper;

import java.util.ArrayList;
import java.util.List;

/** Performs Royal Bow's one authorized first-applicable Engraving roll. */
public final class RoyalBowFirstEngraving {
    static final String PROCESSED_KEY = "tno_tensura_compat.first_engraving_roll_processed";

    private RoyalBowFirstEngraving() {
    }

    public static void afterNativeGearIntegration(LivingEntity wearer, ItemStack equipped) {
        if (wearer.level().isClientSide() || !isSuccessfullyIntegratedRoyalBow(equipped)) {
            return;
        }
        RollResult result = processOnce(wearer, equipped);
        if (result.status() == RollStatus.APPLIED || result.status() == RollStatus.NO_ELIGIBLE_RESULT) {
            TNOTensuraCompat.LOGGER.info(
                    "[Phase 6F] Royal Bow first Engraving roll processed: rarity={}, result={}, engraving={}",
                    result.rarity(), result.status(), result.engravingId());
        }
    }

    public static boolean isSuccessfullyIntegratedRoyalBow(ItemStack stack) {
        if (stack.isEmpty()
                || !BuiltInRegistries.ITEM.getKey(stack.getItem())
                .equals(RoyalVariationsGearData.ROYAL_BOW_ID)
                || GearStageClasses.classification(stack).orElse(null) != GearStageClass.RARE) {
            return false;
        }
        double maxEp = stack.getOrDefault(TensuraDataComponents.MAX_EP.get(), 0.0D);
        return maxEp >= RoyalVariationsGearData.ROYAL_BOW_MAX_EP
                && stack.has(TensuraDataComponents.EP.get())
                && stack.has(TensuraDataComponents.EP_GAIN.get());
    }

    public static RollResult processOnce(LivingEntity wearer, ItemStack stack) {
        if (!isSuccessfullyIntegratedRoyalBow(stack)) {
            return RollResult.notApplicable();
        }
        if (!claim(stack)) {
            return RollResult.alreadyProcessed();
        }

        FirstRollRarity rarity = rarityForRoll(wearer.getRandom().nextInt(100));
        List<Holder<Enchantment>> eligible = eligibleEngravings(wearer, stack, rarity);
        if (eligible.isEmpty()) {
            return new RollResult(RollStatus.NO_ELIGIBLE_RESULT, rarity, null);
        }

        Holder<Enchantment> engraving = eligible.get(
                wearer.level().getRandom().nextInt(eligible.size()));
        int before = EnchantmentHelper.getItemEnchantmentLevel(engraving, stack);
        EngravingHelper.increaseEngraving(wearer, stack, engraving, rarity.enchantmentLevel());
        int after = EnchantmentHelper.getItemEnchantmentLevel(engraving, stack);

        if (wearer.getRandom().nextFloat() * 100.0F < EngravingHelper.CONFIG.curseChance) {
            EngravingHelper.applyCurseEngraving(wearer, stack, rarity.enchantmentLevel());
        }

        ResourceLocation engravingId = engraving.unwrapKey()
                .map(ResourceKey::location)
                .orElse(null);
        return new RollResult(
                after > before ? RollStatus.APPLIED : RollStatus.CANCELLED_BY_NATIVE_EVENT,
                rarity,
                engravingId
        );
    }

    public static boolean isProcessed(ItemStack stack) {
        CustomData data = stack.getOrDefault(DataComponents.CUSTOM_DATA, CustomData.EMPTY);
        return data.copyTag().getBoolean(PROCESSED_KEY);
    }

    static boolean claim(ItemStack stack) {
        if (isProcessed(stack)) {
            return false;
        }
        CustomData.update(DataComponents.CUSTOM_DATA, stack,
                tag -> tag.putBoolean(PROCESSED_KEY, true));
        return true;
    }

    static FirstRollRarity rarityForRoll(int roll) {
        if (roll < 0 || roll >= 100) {
            throw new IllegalArgumentException("roll must be in [0, 100)");
        }
        if (roll < 35) {
            return FirstRollRarity.COMMON;
        }
        if (roll < 70) {
            return FirstRollRarity.UNCOMMON;
        }
        if (roll < 90) {
            return FirstRollRarity.RARE;
        }
        return FirstRollRarity.EPIC;
    }

    private static List<Holder<Enchantment>> eligibleEngravings(
            LivingEntity wearer,
            ItemStack stack,
            FirstRollRarity rarity
    ) {
        Registry<Enchantment> registry = wearer.level().registryAccess()
                .registryOrThrow(Registries.ENCHANTMENT);
        List<Holder<Enchantment>> eligible = new ArrayList<>();
        for (String configuredId : configuredPool(rarity)) {
            ResourceLocation id = ResourceLocation.tryParse(configuredId);
            if (id == null) {
                continue;
            }
            registry.getHolder(ResourceKey.create(Registries.ENCHANTMENT, id))
                    .filter(holder -> holder.value().canEnchant(stack))
                    .ifPresent(eligible::add);
        }
        return List.copyOf(eligible);
    }

    private static List<String> configuredPool(FirstRollRarity rarity) {
        return switch (rarity) {
            case COMMON -> EngravingHelper.CONFIG.commonEngraving;
            case UNCOMMON -> EngravingHelper.CONFIG.uncommonEngraving;
            case RARE -> EngravingHelper.CONFIG.rareEngraving;
            case EPIC -> EngravingHelper.CONFIG.epicEngraving;
        };
    }

    enum FirstRollRarity {
        COMMON(1),
        UNCOMMON(1),
        RARE(2),
        EPIC(3);

        private final int enchantmentLevel;

        FirstRollRarity(int enchantmentLevel) {
            this.enchantmentLevel = enchantmentLevel;
        }

        int enchantmentLevel() {
            return enchantmentLevel;
        }
    }

    public enum RollStatus {
        NOT_APPLICABLE,
        ALREADY_PROCESSED,
        NO_ELIGIBLE_RESULT,
        CANCELLED_BY_NATIVE_EVENT,
        APPLIED
    }

    public record RollResult(
            RollStatus status,
            FirstRollRarity rarity,
            ResourceLocation engravingId
    ) {
        static RollResult notApplicable() {
            return new RollResult(RollStatus.NOT_APPLICABLE, null, null);
        }

        static RollResult alreadyProcessed() {
            return new RollResult(RollStatus.ALREADY_PROCESSED, null, null);
        }
    }
}
