package com.tno.tensuracompat;

import com.mojang.logging.LogUtils;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.ModContainer;
import net.neoforged.fml.common.Mod;
import org.slf4j.Logger;

@Mod(TNOTensuraCompat.MOD_ID)
public class TNOTensuraCompat {
    public static final String MOD_ID = "tno_tensura_compat";
    public static final Logger LOGGER = LogUtils.getLogger();

    public TNOTensuraCompat(IEventBus modEventBus, ModContainer modContainer) {
        LOGGER.info("TNO Tensura Compat loaded");
    }
}
