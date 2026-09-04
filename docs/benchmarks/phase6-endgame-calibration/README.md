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

## Checkpoint B — Magic/Holy classification

Status: complete. `classification.jsonl` contains two runtime registry
observations and one complete suite result, with zero case errors.

Tensura 2.0.1.1 defines both Engravings through its `tensura:after_attack`
`additional_damage` effect using `TOTAL_ATTACK_MULTIPLY`. Magic Weapon names
`tensura:magic`; Holy Weapon names `tensura:holy_damage`. The installed
`TensuraDamageTypes` registry exposes these as `MAGIC_GENERIC` and
`HOLY_DAMAGE`, respectively. Their runtime `DamageSource.getMsgId()` values
are `tensura.magic` and `tensura.holy_damage`.

Both runtime holders have exactly these effective tags:

| Damage type | Runtime tags |
|---|---|
| `tensura:magic` | `minecraft:bypasses_armor`, `minecraft:bypasses_shield`, `minecraft:no_knockback`, `minecraft:witch_resistant_to`, `tensura:bypass_protection_enchantment` |
| `tensura:holy_damage` | `minecraft:bypasses_armor`, `minecraft:bypasses_shield`, `minecraft:no_knockback`, `tensura:bypass_protection_enchantment` |

Neither source has `neoforge:is_magic`, `minecraft:bypasses_effects`,
`minecraft:bypasses_invulnerability`, or `minecraft:bypasses_resistance`.
The distinction is decisive in the installed L2 Hostility 3.0.18 bytecode:

- `DementorTrait.onDamaged` returns without reducing only for bypass-
  invulnerability, bypass-effects, or NeoForge `IS_MAGIC` sources. These two
  sources satisfy none of those exits, so Dementor installs its nonlinear
  reducer. The active base is 2; `x < 2` becomes `x/2`, otherwise it becomes
  `log(x)/log(2)`. This exactly explains `11.2 -> 3.485427`.
- `DispellTrait.onDamaged` is the complementary branch: after the same two
  bypass exits, it returns unless the source has NeoForge `IS_MAGIC`. These
  sources do not, so Dispell does not install its damage reducer. Its
  equipment-disable behavior when the mob attacks is a separate method and
  remains unaffected.
- `LHAttackListener.onDamage` obtains the target capability through
  `LHMiscs.MOB.type().getExisting(target)` and invokes each actual trait's
  `onDamaged`; L2 DamageTracker carries the original source into that path.

This is a semantic mismatch: Tensura calls the events Magic/Holy and gives
them armor-bypassing semantics, while L2's two reducers classify them solely
by the NeoForge `IS_MAGIC` tag.

Two research-only architecture choices were compared:

1. Preserve the exact source and tags, then negotiate only the demonstrated
   Dementor reduction inside the TNO eligible-contribution context. This is
   narrow, retains DamageTracker ordering, does not activate Dispell, and
   cannot affect unrelated damage.
2. Teach only a compatibility bridge that Tensura Magic/Holy are semantically
   magical to L2. This must not add a global tag or replace the DamageSource;
   it would also need to define whether the compatibility classification
   activates Dispell, making it broader and more interaction-sensitive.

No production choice is locked here. The safe default carried into the next
checkpoints is option 1: preserve original source identity/classification and
negotiate only reductions that calibration proves necessary.

## Checkpoint C — development-only calibration context

Status: complete. `Phase6CalibrationContext` is a synchronous scope around
only the existing `AdditionalDamageEntity` call for the classified Magic and
Holy families. It records the originating classified stack, authoritative
native-EP Stage, family, native eligible amount, amount after production Curve
C, amount after the accepted Tensura defense layer, target, actual existing L2
capability, relevant attached trait ranks, and temporary `Q/RD/RA` parameters.

The capability path is exactly
`LHMiscs.MOB.type().getExisting(target)`. The context does not call
`getOrCreate`; absent, uninitialized, inaccessible, or malformed attachments
fail closed by producing no scope. It also rejects unclassified gear,
non-Magic/Holy families, and missing Stages.

The scope and its parameters are thread-local and are removed in `finally`
after the one native `Entity.hurt` call. Nothing is written to the ItemStack,
Royal Arrow, target capability, target/player, or world. The L2 capability is
observed but never mutated. In particular, Adaptive memory, source keys,
counts, rank, and capacity remain entirely L2-owned.

Ordinary production cannot activate the mechanism: it requires both a
non-production environment and the explicit `tno.phase6.calibration` system
property. With the property absent, the wrapped call receives the exact same
`recovered` value as before and no context exists. Parameter construction is
bounded to finite `[0,1]` values and is covered by unit tests. The full clean
build, existing Stage/Resistance/Severance suites, and the new parameter tests
all pass.
