# Phase 6 endgame-effectiveness calibration evidence

## Checkpoint A — target durability decomposition

Status: complete. The accepted artifact is `durability.jsonl`: one catalog,
16 `durability_result` records, one complete suite result, and zero case
errors. Every row uses `APO_profile = NONE`. The disposable targets were
captured only after the requested L2 level, native L2 trait state, trait
attribute modifiers, and the required Tensura:L2Hostility datapack modifiers
had settled. The complete exact trait/rank list and the complete health and
Spiritual Health modifier lists are retained per row.

### Installed-runtime formula audit

The installed artifact is `l2hostility-3.0.18.jar`. Its
`dev.xkmc.l2hostility.content.logic.TraitManager.scale` method does the
following:

1. because `exponentialHealth = false`, calculate `level * healthFactor`;
2. multiply that amount by the entity datapack's `healthScale`; and
3. install `l2hostility:hostility_health` on vanilla `MAX_HEALTH` using
   `ADD_MULTIPLIED_TOTAL`.

The active server setting is `healthFactor = 0.03`. The four entity scales
from the loaded Tensura:L2Hostility datapack are Luminous `0.85`, Hinata
`0.90`, Gazel `1.00`, and Orc Disaster `1.20`. Therefore the exact generic
vanilla-health multiplier is:

```text
H = 1 + level * 0.03 * entityHealthScale
```

Tank is a separate trait path. `LHTraits.TANK` constructs an
`AttributeTrait`; `AttributeTrait.initialize` multiplies every configured
factor by the actual rank. With the active values `tankHealth = 0.20`,
`tankArmor = 4`, and `tankTough = 4`, it installs
`l2hostility:tank_health` as `ADD_MULTIPLIED_TOTAL`, plus four armor and four
toughness per rank. Thus `T = 1 + 0.20 * rank`. Tank is not generic level
scaling.

L2's `hostility_health` modifier was absent from `MAX_SPIRITUAL_HEALTH` in all
16 cases. Native L2 does not directly scale SHP. The required external
Tensura:L2Hostility datapack independently installs
`tensura_l2h:l2_shp_scale` on `tensura:max_spiritual_health` as
`ADD_MULTIPLIED_BASE`, with amount `level * 0.03`. That bridge is why SHP
grows as `nativeSHP * (1 + 0.03 * level)`. It is level-derived durability,
but it must not be mistaken for `TraitManager.scale` or for Tank.

### Runtime results

The `generic` and `Tank` columns show multiplier followed by the portion that
actually survived the runtime's 10,000 vanilla-health ceiling. Unclamped
contributions are retained in the JSONL as separate fields.

| Boss | Lv | native HP | generic H / realized HP | Tank rank / T / realized HP | final HP | native SHP + bridge SHP = final SHP | combined | armor / toughness |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `tensura_neb:luminous_valentine` | 300 | 8000 | 8.65x / 2000 | 0 / 1x / 0 | 10000 | 10000 + 90000 = 100000 | 110000 | 50 / 0 |
| `tensura_neb:luminous_valentine` | 600 | 8000 | 16.3x / 2000 | 5 / 2x / 0 | 10000 | 10000 + 180000 = 190000 | 200000 | 70 / 20 |
| `tensura_neb:luminous_valentine` | 800 | 8000 | 21.4x / 2000 | 0 / 1x / 0 | 10000 | 10000 + 240000 = 250000 | 260000 | 50 / 0 |
| `tensura_neb:luminous_valentine` | 1000 | 8000 | 26.5x / 2000 | 0 / 1x / 0 | 10000 | 10000 + 300000 = 310000 | 320000 | 50 / 0 |
| `tensura:hinata_sakaguchi` | 300 | 3000 | 9.1x / 7000 | 0 / 1x / 0 | 10000 | 3600 + 32400 = 36000 | 46000 | 50 / 0 |
| `tensura:hinata_sakaguchi` | 600 | 3000 | 17.2x / 7000 | 0 / 1x / 0 | 10000 | 3600 + 64800 = 68400 | 78400 | 50 / 0 |
| `tensura:hinata_sakaguchi` | 800 | 3000 | 22.6x / 7000 | 0 / 1x / 0 | 10000 | 3600 + 86400 = 90000 | 100000 | 50 / 0 |
| `tensura:hinata_sakaguchi` | 1000 | 3000 | 28x / 7000 | 5 / 2x / 0 | 10000 | 3600 + 108000 = 111600 | 121600 | 70 / 20 |
| `tensura:gazel_dwargo` | 300 | 3000 | 10x / 7000 | 5 / 2x / 0 | 10000 | 3600 + 32400 = 36000 | 46000 | 80 / 20 |
| `tensura:gazel_dwargo` | 600 | 3000 | 19x / 7000 | 2 / 1.4x / 0 | 10000 | 3600 + 64800 = 68400 | 78400 | 68 / 8 |
| `tensura:gazel_dwargo` | 800 | 3000 | 25x / 7000 | 3 / 1.6x / 0 | 10000 | 3600 + 86400 = 90000 | 100000 | 72 / 12 |
| `tensura:gazel_dwargo` | 1000 | 3000 | 31x / 7000 | 2 / 1.4x / 0 | 10000 | 3600 + 108000 = 111600 | 121600 | 68 / 8 |
| `tensura:orc_disaster` | 300 | 700 | 11.8x / 7560 | 3 / 1.6x / 1740 | 10000 | 2700 + 24300 = 27000 | 37000 | 38 / 12 |
| `tensura:orc_disaster` | 600 | 700 | 22.6x / 9300 | 3 / 1.6x / 0 | 10000 | 2700 + 48600 = 51300 | 61300 | 38 / 12 |
| `tensura:orc_disaster` | 800 | 700 | 29.8x / 9300 | 3 / 1.6x / 0 | 10000 | 2700 + 64800 = 67500 | 77500 | 38 / 12 |
| `tensura:orc_disaster` | 1000 | 700 | 37x / 9300 | 3 / 1.6x / 0 | 10000 | 2700 + 81000 = 83700 | 93700 | 38 / 12 |

### Answer to the checkpoint question

Only the realized `hostility_health` amount in the table is truly generic L2
vanilla-health scaling: 2,000 HP for Luminous, 7,000 for Hinata/Gazel, and
7,560 at Orc Lv300 or 9,300 at Orc Lv600+. The much larger mathematical L2
health values are clipped by the 10,000 attribute ceiling. Tank contributes
separately; in this sample only Orc Lv300 had room below the ceiling, so 1,740
Tank HP was realized. The dominant high-level growth in combined fight
resources is instead the external datapack's SHP bridge: 3% of native SHP per
L2 level. A future candidate may compensate verified level-derived durability,
but must keep these native, generic-L2, Tank, and datapack-SHP layers distinct.

No production combat or balance behavior was changed by this checkpoint.
