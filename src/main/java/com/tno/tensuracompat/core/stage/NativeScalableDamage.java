package com.tno.tensuracompat.core.stage;

import io.github.manasmods.tensura.damage.TensuraDamageTypes;
import net.minecraft.core.Holder;
import net.minecraft.world.damagesource.DamageType;
import net.minecraft.world.item.enchantment.EnchantedItemInUse;

import java.util.Optional;

/** Classification and scaling for native Tensura special-damage events. */
public final class NativeScalableDamage {
    private NativeScalableDamage() {
    }

    public static float scaleAdditionalDamage(
            Holder<DamageType> damageType,
            EnchantedItemInUse enchantedItem,
            float nativeEligibleAmount
    ) {
        return additionalDamageFamily(damageType)
                .map(family -> ProductionStageScaling.scaleEligible(
                        enchantedItem.itemStack(), family, nativeEligibleAmount))
                .orElse(nativeEligibleAmount);
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

    public static Optional<ScalableFamily> additionalDamageFamily(Holder<DamageType> damageType) {
        if (damageType.is(TensuraDamageTypes.MAGIC_GENERIC)) {
            return Optional.of(ScalableFamily.MAGIC_WEAPON);
        }
        if (damageType.is(TensuraDamageTypes.HOLY_DAMAGE)) {
            return Optional.of(ScalableFamily.HOLY_WEAPON);
        }
        return Optional.empty();
    }

    public static Optional<ScalableFamily> spiritualDamageFamily(Holder<DamageType> damageType) {
        return damageType.is(TensuraDamageTypes.SOUL_SCATTER)
                ? Optional.of(ScalableFamily.SOUL_EATER)
                : Optional.empty();
    }
}
