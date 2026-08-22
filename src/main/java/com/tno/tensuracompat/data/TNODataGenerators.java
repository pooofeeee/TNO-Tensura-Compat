package com.tno.tensuracompat.data;

import net.neoforged.neoforge.data.event.GatherDataEvent;

public final class TNODataGenerators {
    private TNODataGenerators() {
    }

    public static void gatherData(GatherDataEvent event) {
        event.getGenerator().addProvider(
                event.includeServer(),
                new TNORegistryProvider(event.getGenerator().getPackOutput(), event.getLookupProvider())
        );
    }
}
