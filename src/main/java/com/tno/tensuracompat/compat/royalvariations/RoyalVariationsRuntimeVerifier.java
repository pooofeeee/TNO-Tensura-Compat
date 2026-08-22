package com.tno.tensuracompat.compat.royalvariations;

import com.tno.tensuracompat.TNOTensuraCompat;
import io.github.manasmods.tensura.data.existence.gear.GearExistenceData;
import io.github.manasmods.tensura.registry.data.TensuraCustomData;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.neoforged.fml.ModList;
import net.neoforged.fml.loading.FMLEnvironment;
import net.neoforged.neoforge.event.server.ServerStartedEvent;

/** One-shot development verification against the live datapack registry. */
public final class RoyalVariationsRuntimeVerifier {
    private RoyalVariationsRuntimeVerifier() {
    }

    public static void onServerStarted(ServerStartedEvent event) {
        if (FMLEnvironment.production) {
            return;
        }

        Registry<GearExistenceData> registry = event.getServer()
                .registryAccess()
                .registryOrThrow(TensuraCustomData.GEAR_EXISTENCE);
        GearExistenceData data = registry.get(RoyalVariationsGearData.ROYAL_BOW_ID);
        boolean royalVariationsLoaded = ModList.get().isLoaded(RoyalVariationsGearData.MOD_ID);
        boolean royalBowPresent = BuiltInRegistries.ITEM.containsKey(RoyalVariationsGearData.ROYAL_BOW_ID);

        if (!royalVariationsLoaded) {
            if (data == null) {
                TNOTensuraCompat.LOGGER.info(
                        "[Phase 2 optionality] Royal Variations is absent and {} was correctly skipped by registry conditions",
                        RoyalVariationsGearData.ROYAL_BOW_ID
                );
            } else {
                TNOTensuraCompat.LOGGER.error(
                        "[Phase 2 optionality] {} was registered even though Royal Variations is absent",
                        RoyalVariationsGearData.ROYAL_BOW_ID
                );
            }
            return;
        }

        if (!royalBowPresent) {
            TNOTensuraCompat.LOGGER.error(
                    "[Phase 2 verification] Royal Variations loaded but item registry entry {} is missing",
                    RoyalVariationsGearData.ROYAL_BOW_ID
            );
            return;
        }

        if (data == null) {
            TNOTensuraCompat.LOGGER.error(
                    "[Phase 2 verification] {} is missing from Tensura registry {}",
                    RoyalVariationsGearData.ROYAL_BOW_ID,
                    TensuraCustomData.GEAR_EXISTENCE.location()
            );
            return;
        }

        TNOTensuraCompat.LOGGER.info(
                "[Phase 2 verification] itemPresent=true; Tensura recognized {} as GearExistenceData: minEP={}, maxEP={}, epGain={}, evolution={}",
                data.gear(),
                data.minEP(),
                data.maxEP(),
                data.epGain(),
                data.evolution()
        );
    }
}
