package com.tno.tensuracompat.data;

import com.tno.tensuracompat.compat.royalvariations.RoyalVariationsGearData;
import io.github.manasmods.tensura.registry.data.TensuraCustomData;
import java.util.Set;
import java.util.concurrent.CompletableFuture;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.RegistrySetBuilder;
import net.minecraft.data.PackOutput;
import net.neoforged.neoforge.common.conditions.ItemExistsCondition;
import net.neoforged.neoforge.common.conditions.ModLoadedCondition;
import net.neoforged.neoforge.common.data.DatapackBuiltinEntriesProvider;

public final class TNORegistryProvider extends DatapackBuiltinEntriesProvider {
    private static final RegistrySetBuilder BUILDER = new RegistrySetBuilder()
            .add(TensuraCustomData.GEAR_EXISTENCE, RoyalVariationsGearData::bootstrap);

    public TNORegistryProvider(PackOutput output, CompletableFuture<HolderLookup.Provider> registries) {
        super(
                output,
                registries,
                BUILDER,
                conditions -> {
                    conditions.accept(
                            RoyalVariationsGearData.ROYAL_BOW_GEAR_KEY,
                            new ModLoadedCondition(RoyalVariationsGearData.MOD_ID)
                    );
                    conditions.accept(
                            RoyalVariationsGearData.ROYAL_BOW_GEAR_KEY,
                            new ItemExistsCondition(RoyalVariationsGearData.ROYAL_BOW_ID)
                    );
                },
                Set.of(RoyalVariationsGearData.MOD_ID)
        );
    }
}
