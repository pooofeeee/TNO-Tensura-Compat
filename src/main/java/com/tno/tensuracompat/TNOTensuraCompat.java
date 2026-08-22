package com.tno.tensuracompat;

import com.mojang.logging.LogUtils;
import com.tno.tensuracompat.compat.royalvariations.RoyalVariationsRuntimeVerifier;
import com.tno.tensuracompat.data.TNODataGenerators;
import io.github.manasmods.tensura.Tensura;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.ModContainer;
import net.neoforged.fml.common.Mod;
import net.neoforged.neoforge.common.NeoForge;
import org.slf4j.Logger;

@Mod(TNOTensuraCompat.MOD_ID)
public class TNOTensuraCompat {
    public static final String MOD_ID = "tno_tensura_compat";
    public static final Logger LOGGER = LogUtils.getLogger();

    public TNOTensuraCompat(IEventBus modEventBus, ModContainer modContainer) {
        modEventBus.addListener(TNODataGenerators::gatherData);
        NeoForge.EVENT_BUS.addListener(RoyalVariationsRuntimeVerifier::onServerStarted);

        LOGGER.info("TNO Tensura Compat loaded with API linkage to {}", Tensura.class.getName());
    }
}
