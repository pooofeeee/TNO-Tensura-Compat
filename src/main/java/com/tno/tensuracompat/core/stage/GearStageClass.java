package com.tno.tensuracompat.core.stage;

import java.util.List;

/**
 * TNO's integration class for a compatible gear item. It is unrelated to
 * Apotheosis rarity and to Tensura Unique/Legend/God/Transcendence naming.
 */
public enum GearStageClass {
    COMMON(List.of(
            new Threshold(Stage.S0, 0L),
            new Threshold(Stage.S1, 50_000L),
            new Threshold(Stage.S2, 250_000L),
            new Threshold(Stage.S3, 1_000_000L)
    )),
    RARE(List.of(
            new Threshold(Stage.S0, 0L),
            new Threshold(Stage.S1, 41_500L),
            new Threshold(Stage.S2, 207_500L),
            new Threshold(Stage.S3, 830_000L),
            new Threshold(Stage.S4, 1_245_000L),
            new Threshold(Stage.S5, 1_660_000L),
            new Threshold(Stage.S6, 2_075_000L),
            new Threshold(Stage.S7, 2_490_000L)
    ));

    /** The accepted Rare thresholds are the locked 17% discount values. */
    public static final double RARE_THRESHOLD_DISCOUNT = 0.17D;

    private final List<Threshold> thresholds;

    GearStageClass(List<Threshold> thresholds) {
        this.thresholds = thresholds;
    }

    public List<Threshold> thresholds() {
        return thresholds;
    }

    public Stage maximumStage() {
        return thresholds.getLast().stage();
    }

    public boolean supports(Stage stage) {
        return stage.index() <= maximumStage().index();
    }

    public record Threshold(Stage stage, long minimumEp) {
    }
}
