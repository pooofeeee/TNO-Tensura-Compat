package com.tno.tensuracompat.compat.royalvariations;

import org.junit.jupiter.api.Test;

import java.util.EnumMap;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

class RoyalBowFirstEngravingTest {
    @Test
    void firstRollDistributionIsExactlyThirtyFiveThirtyFiveTwentyTen() {
        var counts = new EnumMap<RoyalBowFirstEngraving.FirstRollRarity, Integer>(
                RoyalBowFirstEngraving.FirstRollRarity.class);
        for (int roll = 0; roll < 100; roll++) {
            counts.merge(RoyalBowFirstEngraving.rarityForRoll(roll), 1, Integer::sum);
        }

        assertEquals(35, counts.get(RoyalBowFirstEngraving.FirstRollRarity.COMMON));
        assertEquals(35, counts.get(RoyalBowFirstEngraving.FirstRollRarity.UNCOMMON));
        assertEquals(20, counts.get(RoyalBowFirstEngraving.FirstRollRarity.RARE));
        assertEquals(10, counts.get(RoyalBowFirstEngraving.FirstRollRarity.EPIC));
    }

    @Test
    void rejectsOutOfRangeRolls() {
        assertThrows(IllegalArgumentException.class,
                () -> RoyalBowFirstEngraving.rarityForRoll(-1));
        assertThrows(IllegalArgumentException.class,
                () -> RoyalBowFirstEngraving.rarityForRoll(100));
    }
}
