package com.tno.tensuracompat.core.stage;

import io.github.manasmods.tensura.damage.TensuraDamageTypes;
import net.minecraft.core.Holder;
import net.minecraft.world.damagesource.DamageType;
import net.minecraft.world.item.enchantment.EnchantedItemInUse;

/** Classification and scaling for native Tensura special-damage events. */
public final class NativeScalableDamage {
    private NativeScalableDamage() {
    }

    public static float scaleAdditionalDamage(
            Holder<DamageType> damageType,
            EnchantedItemInUse enchantedItem,
            float nativeEligibleAmount
    ) {
        if (damageType.is(TensuraDamageTypes.MAGIC_GENERIC)) {
            return ProductionStageScaling.scaleEligible(
                    enchantedItem.itemStack(), ScalableFamily.MAGIC_WEAPON, nativeEligibleAmount);
        }
        if (damageType.is(TensuraDamageTypes.HOLY_DAMAGE)) {
            return ProductionStageScaling.scaleEligible(
                    enchantedItem.itemStack(), ScalableFamily.HOLY_WEAPON, nativeEligibleAmount);
        }
        return nativeEligibleAmount;
    }

    public static float scaleSpiritualDamage(
            Holder<DamageType> damageType,
            EnchantedItemInUse enchantedItem,
            float nativeEligibleAmount
    ) {
        if (!damageType.is(TensuraDamageTypes.SOUL_SCATTER)) {
            return nativeEligibleAmount;
        }
        return ProductionStageScaling.scaleEligible(
                enchantedItem.itemStack(), ScalableFamily.SOUL_EATER, nativeEligibleAmount);
    }
}
