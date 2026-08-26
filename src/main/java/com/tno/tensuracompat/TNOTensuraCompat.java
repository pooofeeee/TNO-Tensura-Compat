package com.tno.tensuracompat;

import com.mojang.logging.LogUtils;
import com.tno.tensuracompat.compat.royalvariations.RoyalVariationsRuntimeVerifier;
import com.tno.tensuracompat.data.TNODataGenerators;
import com.tno.tensuracompat.debug.Phase5FRuntimeInspector;
import com.tno.tensuracompat.debug.Phase5FApotheosisBenchmark;
import io.github.manasmods.tensura.Tensura;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.bus.api.EventPriority;
import net.neoforged.fml.ModContainer;
import net.neoforged.fml.common.Mod;
import net.neoforged.fml.loading.FMLEnvironment;
import net.neoforged.neoforge.common.NeoForge;
import org.slf4j.Logger;

@Mod(TNOTensuraCompat.MOD_ID)
public class TNOTensuraCompat {
    public static final String MOD_ID = "tno_tensura_compat";
    public static final Logger LOGGER = LogUtils.getLogger();

    public TNOTensuraCompat(IEventBus modEventBus, ModContainer modContainer) {
        modEventBus.addListener(TNODataGenerators::gatherData);
        NeoForge.EVENT_BUS.addListener(RoyalVariationsRuntimeVerifier::onServerStarted);

        if (!FMLEnvironment.production) {
            NeoForge.EVENT_BUS.addListener(Phase5FRuntimeInspector::onRegisterCommands);
            NeoForge.EVENT_BUS.addListener(Phase5FRuntimeInspector::onServerStarted);
            NeoForge.EVENT_BUS.addListener(Phase5FRuntimeInspector::onServerTick);
            NeoForge.EVENT_BUS.addListener(Phase5FApotheosisBenchmark::onServerTick);
            NeoForge.EVENT_BUS.addListener(Phase5FApotheosisBenchmark::onServerStarted);
            NeoForge.EVENT_BUS.addListener(EventPriority.HIGHEST,
                    Phase5FApotheosisBenchmark::onIncomingBeforeCrit);
            NeoForge.EVENT_BUS.addListener(EventPriority.NORMAL,
                    Phase5FApotheosisBenchmark::onIncomingAfterCrit);
            NeoForge.EVENT_BUS.addListener(EventPriority.LOWEST,
                    Phase5FApotheosisBenchmark::onIncomingDamage);
            NeoForge.EVENT_BUS.addListener(EventPriority.LOWEST,
                    Phase5FApotheosisBenchmark::onDamagePost);
        }

        LOGGER.info("TNO Tensura Compat loaded with API linkage to {}", Tensura.class.getName());
    }
}
