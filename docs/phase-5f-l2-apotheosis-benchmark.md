# Phase 5F — L2 / Apotheosis / TNO Benchmark Plan

Status: runtime instrumentation, the Apotheosis-only controlled benchmark, and
Suite B Checkpoint 2 for Magic Weapon, Holy Weapon, and Soul Eater are complete.
The full L2 trait/boss matrix remains future work. No balance values are changed
by this phase.

## Goal

Validate three independent combat suites against Tensura / NEB bosses enhanced by L2 Hostility:

1. **Apotheosis only** — determine whether a legal endgame Apotheosis bow build materially affects damage under the final pack settings.
2. **TNO only** — primary suite. Verify TNO Stage progression remains meaningful against L2 defenses without bypassing L2 mechanics.
3. **Apotheosis + TNO** — verify the two systems stack without collapsing progression or creating an unintended damage explosion.

The target is not for S7 or max-Apotheosis to trivialize L2 bosses. The target is measurable progression while preserving boss and L2 defenses.

## Runtime stack to validate

- Minecraft 1.21.1
- NeoForge 21.1.x
- Tensura 2.0.1.1
- ManasCore 4.0.0.2
- Royal Variations runtime
- L2 Hostility 3.0.18
- L2 Library 3.0.8
- L2 Complements 3.1.3
- Tensura: L2Hostility datapack
- Apotheosis 8.7.0
- Apothic Attributes 2.10.1
- Apothic Enchanting 1.6.1
- Apothic Equipment 1.0.0
- Ancient Reforging 1.8.5
- Nightmare's Apothic Tensura 0.1.0
- Apothic Cataclysm 1.2.0 (present in final pack; not required for the Tensura-boss target set)

## Boss target set

Primary:

- Luminous
- Hinata
- Gazel

Secondary coverage:

- Orc Disaster
- Carrion
- Rimuru Ogre Fight
- Elemental Colossus

Each target must first be verified as actually receiving L2 level scaling / traits in the live runtime.

## L2 level matrix

Primary checkpoints:

- Lv300 — high natural Tensura:L2 region
- Lv600 — Ragnarok unlock threshold
- Lv800 — endgame stress target
- Lv1000 — large trait-budget / Arena-feasibility stress target

Optional torture check:

- Lv3000 — only if the pack keeps L2's default maxMobLevel=3000. This is not the primary balance target unless the final pack is intended to reach that level naturally.

## L2 trait coverage

All 39 enabled L2 Hostility traits must be covered by the test matrix:

Tank, Speedy, Protection, Invisible, Fiery, Regenerate, Adaptive, Reflect, Shulker, Grenade, Corrosion, Erosion, Growth, Split, Drain, Counter Strike, Gravity, Moonwalk, Arena, Dementor, Dispell, Undying, Teleport, Repelling, Pulling, Reprint, Killer Aura, Ragnarok, Master, Weakness, Slowness, Poison, Wither, Levitation, Blindness, Nausea, Soul Burner, Freezing, Cursed.

### Legal balance profile

Balance evidence must use legal L2 combinations only, honoring:

- trait min level
- trait cost and rank budget
- max trait count
- entity whitelist / blacklist
- SEMIBOSS restrictions
- trait exclusions
- entity-specific datapack overrides

### Forced diagnostic profile

A separate forced-trait diagnostic may intentionally violate natural generation rules to expose integration failures. It must never be used as balance evidence.

## Suite A — Apotheosis only

TNO scalable Engraving contribution must be disabled or held constant.

Compare:

- baseline Royal Bow
- legal maximum Apotheosis Royal Bow under the final pack configuration

Record:

- raw arrow hit damage
- critical hit state / critical multiplier
- effective armor / protection penetration contribution
- time to kill
- target max HP / SHP before test
- Regen recovery during sustained fire
- whether L2 Dementor / Dispell / Adaptive / Repelling changes the result

### Definition of “max Apotheosis” — source findings so far

Apotheosis 8.7.0 uses the Bow loot category for ranged affixes and gem bonuses. Candidate endgame damage components visible in the official 1.21 source include:

- `ranged/attribute/elven` — Arrow Damage
- `ranged/attribute/streamlined` — Arrow Velocity
- `melee/attribute/piercing` — Armor Pierce, also legal on Bow
- `weapon/attribute/shredding` — Armor Shred, also legal on Bow
- `melee/attribute/lacerating` — Crit Damage, also legal on Bow
- `melee/attribute/intricate` — Crit Chance, also legal on Bow
- `ranged/attribute/agile` — Draw Speed
- ranged basic/effect/ability affixes such as Acidic, Deathbound, Magical, Spectral where legal and useful

Known Perfect gem candidates from the official 1.21 source:

- `core/combatant` — +55% Arrow Damage (unique)
- `core/breach` — +15 Protection Pierce on Bow (unique)
- `core/lightning` — +55% Arrow Velocity
- `core/slipstream` — +60% Draw Speed (unique)
- `core/warlord` — +70% Crit Damage
- `the_nether/molten_breach` — +10 Armor Pierce on Bow (unique)

The final max build must be determined from the live installed stack, not from source assumptions alone. In particular verify:

- Royal Bow resolves to Apotheosis `BOW` loot category
- actual maximum rarity with Ancient Reforging installed
- actual number of legal affix slots
- actual socket cap in the installed configuration
- gem uniqueness / incompatibility rules
- max legal Apothic Enchanting enchantments
- whether Sigil of Supremacy is enabled and legal in the final pack
- whether any addon changes the above values

Do not use creative-only impossible affix combinations as the balance build.

## Suite B — TNO only (primary)

No Apotheosis affix, gem, socket, or enchantment damage amplification.

Test every scalable TNO family:

- Magic Weapon
- Holy Weapon
- Soul Eater
- Elemental / Slotting damage coefficient
- Energy Steal
- Severance

For each family run Native / S0 through S7 as applicable.

Record repeated-hit sequences, not only first hit, because Adaptive changes repeated damage behavior.

TNO matching Resistance penetration remains limited to Tensura matching Resistance. It must not silently bypass L2 Adaptive, Dispell, Dementor, Protection, Tank, Regen, Repelling, Arena, or other L2 defenses.

## Suite C — Apotheosis + TNO

Use the exact legal max-Apotheosis build established by Suite A and then apply the same TNO Stage matrix from Suite B.

This suite answers whether generic Apotheosis weapon progression plus TNO special integration combine sanely.

## Required instrumentation / output

Every measurement row should include at least:

- suite: APO / TNO / BOTH
- boss entity id
- L2 level
- exact L2 traits + ranks
- legal vs forced profile
- target Max HP
- target SHP / spiritual health if present
- target armor / toughness
- TNO family
- TNO Stage
- Apotheosis rarity
- applied affixes + levels
- sockets + gems + purity
- enchantments
- pre-hit HP/SHP
- post-hit HP/SHP
- observed damage
- repeated-hit index for Adaptive tests
- elapsed time for sustained-DPS / TTK tests
- notes for immunity, Nullification, projectile cancellation, regeneration, death reset, etc.

## Phase 5F runtime inspector

The development runtime now registers these permission-level-2 commands:

- `/tno_phase5f bow` inspects the held item.
- `/tno_phase5f target <entity>` inspects a targeted living entity.

Both emit one-line JSON prefixed by `TNO_PHASE5F`, using schema
`tno.phase5f.runtime_inspector.v1`, to both the command source and the log. A
startup template inspection checks `royalvariations:royal_bow`; a bounded
one-shot entity scan provides an L2/Tensura attachment smoke test when a living
non-player entity is loaded. Registration and both automatic probes are guarded
by `!FMLEnvironment.production`.

All Apotheosis and L2 calls use runtime class names plus reflection. There is no
compile-time linkage to either family. Tensura's SHP read uses the project's
existing mandatory API linkage (`TensuraStorages.getExistenceFrom` and
`TensuraAttributes.MAX_SPIRITUAL_HEALTH`).

The Bow JSON includes:

- item ID, Royal Bow identity, loaded relevant mods and versions;
- resolved loot category, category validity and affixability;
- current rarity and all live rarities, their exact rule trees, affix pools,
  enabled reforging recipes, constructible affix sets and missing rule slots;
- every current affix's registry ID, rarity, raw stored float, formatted/displayed
  level, effective clamped level, validity, exclusivity and Supremacy-floor state;
- socket count, every gem ID/purity/uniqueness/validity and applicable live bonus;
- raw main-hand modifiers and, for a player-held Bow, effective values for the
  requested Apothic Attributes plus the addon-provided Manas/Tensura attributes;
- current enchantments, supported enchantments, live registry max levels, and an
  exact largest pairwise-compatible set;
- presence of the Supremacy and add-sockets recipes.

The target JSON includes registry ID, UUID, current/max HP, armor, toughness,
Tensura current/base-max/effective-max SHP, Magicules and Aura, the datapack
scaling multipliers and marker, L2 initialization state, level, and every trait
ID/rank with its live maximum rank where accessible.

### Optional local runtime setup

The Gradle property below adds only a filtered Phase 5F set of local files to
`localRuntime`:

```powershell
.\gradlew.bat runClient '-Pphase5f_runtime_mods_dir=C:\path\to\instance\mods'
```

Nothing is added when the property is absent or is not a directory. The existing
private Royal Variations JAR remains conditional on its own `libs/` file. When
the target directory supplies Curios, that exact local Curios JAR is used for the
Royal Variations test runtime; otherwise the prior Maven local-runtime fallback
is retained. None of these file dependencies is published or declared as a
released mandatory dependency.

## Verification sources

The investigation used both upstream source and the exact installed artifacts.
The upstream references establish the intended APIs; the local JAR/data results
below take precedence for version-specific values.

- The official [Apotheosis 1.21 changelog](https://github.com/Shadows-of-Fire/Apotheosis/blob/1.21/changelog.md)
  documents namespaced loot categories, the 1.21 loot-rule system, generic
  projectile affix/gem handling, and runtime affix validation.
- Official `AffixHelper` source documents [Sigil of Supremacy applying a 1.5
  floor](https://github.com/Shadows-of-Fire/Apotheosis/blob/26.1/src/main/java/dev/shadowsoffire/apotheosis/affix/AffixHelper.java).
  The exact 8.7.0 bytecode was checked and has the same `builder.upgrade(affix,
  1.5F)` behavior and a maximum affix level of 2.0.
- Official Apothic Attributes source shows that [Arrow Damage scales arrow base
  damage and Arrow Velocity scales its movement](https://github.com/Shadows-of-Fire/Apothic-Attributes/blob/26.1/src/main/java/dev/shadowsoffire/apothic_attributes/impl/AttributeEvents.java).
  The exact 2.10.1 artifact was used for runtime values.
- Ancient rarity/affix data came from the exact 1.8.5 JAR and was cross-checked
  against the official [Ancient Reforging repository](https://github.com/ianm1647/ancientreforging).
- The reflective L2 route was checked against the exact 3.0.18 bytecode and the
  official [L2 entity capability initialization](https://github.com/Minecraft-LightLand/L2Hostility/blob/main/src/main/java/dev/xkmc/l2hostility/events/CapabilityEvents.java).

## Exact artifact/runtime facts

The equivalent local runtime loaded the exact target versions for Royal
Variations, Apotheosis, Apothic Attributes, Apothic Enchanting, Apothic
Equipment, Ancient Reforging, Nightmare's Apothic Tensura, Apotheosis Balance,
L2 Hostility, L2 Library and L2 Complements.

Royal Variations' artifact is
`royal-variations-[NeoForge]_1.21.1_2.0.4.jar`. Its internal NeoForge mod
metadata reports version `2.0`; the filename/distribution version is `2.0.4`.

Live Royal Bow result:

| Field | Verified result |
|---|---|
| Item | `royalvariations:royal_bow` |
| Loot category | `apotheosis:bow` |
| Category accepts stack | `true` |
| Affixable | `true` |
| Registered rarities | 8 |
| Registered affixes | 227 total; the inspector filters them per Bow/rarity |
| Registered gems | 21 |
| Supremacy recipe | enabled |
| Add-sockets recipe | enabled; recipe itself is capped at 2 sockets |

### Rarity and capacity result

There are two different maxima, and treating them as one would create an
impossible test item:

| Rarity | Sort | Declared affix rules | Constructible live maximum | Missing declared slots | Max sockets | Enabled reforging recipe |
|---|---:|---|---:|---|---:|---|
| `ancientreforging:ancient` | 800 | 5 stat + 3 basic + 2 ability | 10 | none | 5 | `ancientreforging:reforging/ancient` |
| `apothicnightmares:god_grade` | 800 | 4 stat + 2 basic + 1 ability | 6 | 1 basic | 5 | `apotheosis:reforging/god_grade` |
| `apothicnightmares:genesis_grade` | 900 | 5 stat + 3 basic + 1 ability | 7 | 2 basic | 6 | `apotheosis:reforging/genesis_grade` |

Therefore:

- With Apotheosis 8.7.0 + Ancient Reforging 1.8.5 alone, **Ancient** is the
  highest rarity and supports its full ten-affix declaration.
- In the complete installed addon stack, **Genesis Grade** is the highest
  obtainable rarity. Its live Bow pool has six stat affixes, two ability affixes,
  and only one basic-effect affix. Apotheosis's exact 8.7.0 `AffixLootRule`
  logs and skips a rule when no candidate remains, so the enabled recipe produces
  at most 5 stat + 1 basic + 1 ability = **7 affixes**, not an invented nine.
- **Ancient** remains the highest *rule-complete* rarity and the highest generic
  Apotheosis affix-count build: ten compatible affixes and up to five sockets.
- The full-stack maximum-capacity item is an obtainable Genesis Royal Bow with
  seven affixes and a six-socket roll. A Genesis Bow with nine distinct legal
  affixes is impossible in this exact stack.

Ancient's exact rule allows 3-4 sockets on the common branch and exactly 5 on its
rare branch. Genesis allows 3-5 normally and 5-6 on its rare branch. The
`sigil_add_sockets` recipe's `max_sockets: 2` is not the rarity socket ceiling.

### Affixes and actual damage

The exact Ancient Bow pool has 21 entries and can satisfy all ten slots. The
five generic damage-stat candidates are:

- `ancientreforging:ranged/attribute/elven` — Arrow Damage, up to +80%;
- `ancientreforging:melee/attribute/lacerating` — Crit Damage, up to +80%;
- `ancientreforging:melee/attribute/intricate` — Crit Chance, up to +115%;
- `ancientreforging:melee/attribute/piercing` — Armor Pierce, up to +24;
- `ancientreforging:weapon/attribute/shredding` — Armor Shred, up to +70%.

`ancientreforging:ranged/attribute/agile` is still a valid Ancient Draw Speed
alternative (up to +150% total), and `streamlined` supplies up to +70% Arrow
Velocity. Those can beat a penetration or crit slot for sustained DPS or a
low-armor target, so the five-stat damage selection must be recorded per target.

Nightmare's addon overwrites the base `apotheosis:ranged/attribute/agile` data to
use `tensura:projectile_dodge_chance`; it is not a Draw Speed affix in the merged
runtime. It also supplies the Genesis/God Bow pools. A Genesis maximum consists
of five of six elemental boost stats, one of `critical_focus` or
`warp_fletching`, and `crippling_shot`. Which elemental five and which ability
maximize damage depends on the Bow's active damage type and the target's Tensura
resistances; sort index alone cannot answer that combat question.

This is why the benchmark should retain both legal candidates:

1. Genesis 7-affix/6-socket maximum-capacity final-stack item.
2. Ancient 10-affix/5-socket rule-complete generic Apotheosis item.

The higher observed boss damage of those two, with the exact affix/gem JSON
captured, is the Suite A comparator. Declaring either universally stronger before
that measurement would be a balance guess.

### Gems

Exact Perfect values for the originally nominated gems were verified from the
8.7.0 JAR:

- `apotheosis:core/combatant`: +55% Arrow Damage, unique;
- `apotheosis:core/breach`: +15 Protection Pierce, unique;
- `apotheosis:core/lightning`: +55% Arrow Velocity, non-unique;
- `apotheosis:core/slipstream`: +60% Draw Speed, unique;
- `apotheosis:core/warlord`: +70% Crit Damage, non-unique;
- `apotheosis:the_nether/molten_breach`: +10 Armor Pierce, unique.

All six can legally coexist once each in a six-socket Genesis Bow. `unique` bans
a duplicate of that same gem; it does not ban other unique gem IDs. They are not
automatically the damage optimum. The live Bow-compatible pool also contains,
among others:

- `apotheosis:core/samurai`: +50% Crit Chance, unique;
- `apotheosis:overworld/verdant_ruin`: +40% Armor Shred with a wearer-armor
  downside, unique;
- `apotheosis:overworld/royalty`: +40% Protection Shred with -65% Draw Speed,
  unique;
- `apotheosis:core/tyrannical`: Perfect Bleeding II behavior, unique.

For maximum single-hit physical damage, start by comparing Combatant, Lightning,
Warlord, Samurai, Breach and Molten Breach against penetration/shred alternatives.
For sustained DPS, Slipstream becomes a candidate. Breach, Molten Breach,
Verdant Ruin and Royalty are target-defense-dependent. The inspector records the
actual installed bonuses, so the benchmark—not an NBT assumption—selects the
winning legal six.

### Enchantments and Supremacy

The live Royal Bow supports 20 enchantments. The exact largest pairwise-compatible
set contains 9:

- `apothic_enchanting:endless_quiver` I
- `apothicnightmares:spatial_bow` I
- `l2complements:soul_bound` I
- `l2complements:transparent` I
- `l2hostility:vanish` I
- `minecraft:flame` I
- `minecraft:power` V
- `minecraft:punch` II
- `tensura:barrier_piercing` II

This is a maximum-count sample, not a claim that every utility enchantment
increases damage. Infinity is excluded by compatibility. The APO-only suite must
also exclude or hold constant TNO engraving enchantments as specified above.

The target instance contains a legacy `config/apotheosis/enchantments.cfg` with
higher values such as Power IX, Punch V, Barrier Piercing VI and Slotting VII.
Copying that exact file into the isolated runtime did not change the live registry
values: Apothic Enchanting 1.6.1 no longer exposes the old per-enchantment config
manager. The live values above, not the stale file comments/defaults, are the
verified ceiling for this installed stack.

The Supremacy recipe is enabled. Exact 8.7.0 behavior upgrades every current
affix to at least raw/effective level 1.5; the hard affix maximum is 2.0. It stores
no separate Supremacy component, so the inspector reports per-affix levels and
infers Supremacy only when every affix reaches that floor. The pre-Supremacy value
cannot be recovered from an already upgraded stack.

### Addon impact

- Ancient Reforging adds Ancient rarity, its complete ten-affix Bow pool and the
  five-socket branch.
- Nightmare's Apothic Tensura adds God/Genesis, their incomplete Bow pools,
  six-socket Genesis branch, Tensura/Manas attributes, and overwrites base Agile.
- Apothic Equipment only replaces ordinary equipment crafting recipes; its
  vanilla Bow recipe starts with one socket. It does not modify Royal Bow or the
  rarity socket ceilings.
- Apotheosis Balance is active, but the final instance has
  `apotheosisMultiplier = 1.0`, `affixRollChance = 1.0`, and no rarity drops, so
  it makes no numeric/capacity change in this configuration. Raw runtime
  modifiers remain in the output to catch later config changes.
- Apothic Cataclysm 1.2.0 was artifact-inspected. It contains no rarity, affix or
  gem data for Royal Bow; it only tags Cataclysm boss entities and therefore was
  not required in the equivalent Tensura-target runtime.

## Official Apotheosis-only profiles

The automated harness constructs every stack through the live Apotheosis
registries. It validates every affix against the Bow category at normal maximum
level before applying the enabled Sigil of Supremacy path, which raises the
effective affix level to `1.5`. Perfect gems are inserted with `SocketHelper`,
and every enchantment is checked against the live item and the other selected
enchantments. Both rarity recipes expose a legitimate low-chance Unbreakable
component branch (3% for Genesis and 5% for Ancient); the maximum test stacks
select that legal outcome so item condition remains constant across long runs.

Both builds use the same nine-enchantment maximum listed above. TNO scalable
data is absent/default and no TNO Engraving is applied.

### Genesis maximum

`GENESIS_SINGLE_WARP_FLETCHING` is the strongest tested legal Genesis path:

- rarity: `apothicnightmares:genesis_grade`;
- seven constructible affixes at effective level `1.5`:
  `earth_volley`, `flame_volley`, `spatial_archery`, `water_volley`,
  `wind_volley`, `warp_fletching`, and `crippling_shot`, all in the
  `apothicnightmares:ranged/...` namespace shown by the runtime output;
- six sockets with Perfect `apotheosis:core/combatant`, `core/breach`,
  `core/lightning`, `core/warlord`, `core/samurai`, and
  `overworld/verdant_ruin`;
- measured attributes: Arrow Damage `1.55`, Arrow Velocity `1.55`, Armor Pierce
  `0`, Armor Shred `0.40`, Protection Pierce `15`, Protection Shred `0`, Crit
  Chance `0.55`, Crit Damage `2.55`, Draw Speed `1.0`, and Warp Shot `1.15`.

The two missing Genesis basic-effect slots remain unsatisfiable; no fabricated
affix or component was added to fill them.

### Ancient maximum

`ANCIENT_SINGLE_PROSPEROUS_SPECTRAL` is the winning legal Ancient path:

- rarity: `ancientreforging:ancient`;
- ten affixes at effective level `1.5`:
  `ancientreforging:ranged/attribute/elven`,
  `ancientreforging:ranged/attribute/streamlined`,
  `ancientreforging:melee/attribute/lacerating`,
  `ancientreforging:melee/attribute/intricate`,
  `ancientreforging:melee/attribute/piercing`,
  `ancientreforging:ranged/mob_effect/acidic`,
  `ancientreforging:ranged/mob_effect/deathbound`,
  `ancientreforging:ranged/mob_effect/ivy_laced`,
  `ancientreforging:ranged/enchantment/prosperous`, and
  `ancientreforging:ranged/spectral`;
- five sockets with Perfect `apotheosis:core/combatant`, `core/breach`,
  `core/lightning`, `core/warlord`, and a second `core/warlord`. Warlord is not
  unique, and the live socket API accepted both copies;
- measured attributes: Arrow Damage `3.0224999815`, Arrow Velocity
  `2.9449999630`, Armor Pierce `31`, Armor Shred `0`, Protection Pierce `15`,
  Protection Shred `0`, Crit Chance `1.5300000191`, Crit Damage `5.8799999714`,
  Draw Speed `1.0`, and Warp Shot `0` on the controlled target.

The maximum-hit runner-up used the same Ancient build except
`ancientreforging:weapon/attribute/shredding` replaced `piercing`. Its measured
Armor Pierce was `0` and Armor Shred was `0.7999999523`.

### Gem optimization result

The live Perfect-gem comparison produced these Bow-relevant conclusions:

| Gem | Bow effect | Unique | Primary contribution / result |
|---|---|---:|---|
| `core/combatant` | +55% Arrow Damage | yes | raw hit and DPS; selected |
| `core/breach` | +15 Protection Pierce | yes | effective armored/protected damage; selected |
| `core/lightning` | +55% Arrow Velocity | no | raw projectile hit scaling; selected |
| `core/slipstream` | +60% Draw Speed | yes | more releases per interval, but its tested profiles lost the 20-second DPS screen |
| `core/warlord` | +70% Crit Damage | no | raw critical hit and DPS; two copies are legal on Ancient and selected |
| `the_nether/molten_breach` | +10 Armor Pierce | yes | defense-dependent; lost to the selected Warlord configuration |
| `core/samurai` | +50% Crit Chance | yes | crit frequency; selected on Genesis, unnecessary on Ancient because Ancient already exceeded 100% |
| `overworld/verdant_ruin` | +40% Armor Shred, wearer-armor downside | yes | effective armored damage; selected on Genesis but lost its Ancient variant |
| `overworld/royalty` | +40% Protection Shred, -65% Draw Speed | yes | defense-dependent; dominated here by Breach without the draw penalty |
| `core/tyrannical` | Bleeding II | yes | sustained DoT candidate; its tested profile lost to the Warlord path |

Uniqueness is per gem ID, not a blanket incompatibility between different unique
gems. All selected combinations were accepted by the live `SocketHelper` path.

## Controlled benchmark result

The comparator was the same neutral `LivingEntity` adapter using the Armor Stand
entity type/dimensions at 20 blocks, with 50 armor, 24 toughness, full unbreakable
Netherite, Protection IV on all four pieces, no L2 traits, and no Tensura mob
skills/resistances. Every release used a vanilla arrow and the live
attribute-adjusted full-draw time. Damage is post-mitigation NeoForge event data.

### Seven-profile maximum-hit screen

The preliminary screen used 20 releases per profile on a fresh server. Only
averaged critical hit damage—not a single random maximum—was used to promote
finalists.

| Profile | Hit shots | Crit rate among hits | Mean crit | Maximum crit |
|---|---:|---:|---:|---:|
| `GENESIS_SINGLE_CRITICAL_FOCUS` | 15 | 46.67% | 176.946 | 191.977 |
| `GENESIS_SINGLE_WARP_FLETCHING` | 15 | 53.33% | 179.857 | 194.464 |
| `ANCIENT_SINGLE_MAGICAL_SPECTRAL` | 14 | 100% | 988.993 | 1232.356 |
| `ANCIENT_SINGLE_PROSPEROUS_SPECTRAL` | 15 | 100% | 1022.030 | 1411.413 |
| `ANCIENT_SINGLE_PROSPEROUS_SPECTRAL_VERDANT` | 15 | 100% | 767.212 | 1011.346 |
| `ANCIENT_SINGLE_PROSPEROUS_SPECTRAL_MOLTEN` | 15 | 100% | 713.805 | 901.514 |
| `ANCIENT_SINGLE_PROSPEROUS_SPECTRAL_SHREDDING` | 15 | 100% | 1071.582 | 1388.299 |

This promoted Genesis Warp Fletching, Ancient Prosperous/Spectral/Piercing, and
Ancient Prosperous/Spectral/Shredding to the official distribution. The larger
sample was necessary because the two Ancient results were close.

### Official 80-hit distributions

The installed stack has a repeatable server-session limitation: one process
stops delivering direct benchmark events after 15 controlled releases while the
player remains alive at 20 HP, the unbreakable Bow remains present at damage 0,
and the target remains alive at reset health. Recreating the player and target
does not clear it. Official distributions therefore use the first 15 validated
releases from each of six fresh server processes. Raw per-hit records are emitted
by the harness; the first 80 valid hit shots in deterministic batch/shot order
form each distribution. This is an addon/runtime harness limitation, not a TNO
balance behavior.

| Profile | Source releases / hits | Crit hits | Non-crit post-mitigation damage | Crit post-mitigation damage |
|---|---:|---:|---|---|
| Genesis Warp Fletching | 90 / 90 | 50/80 (62.5%) | n=30, min 123.825, median 132.600, mean 131.658, max 141.375 | n=50, min 164.629, median 179.546, mean 181.585, max 209.381 |
| Ancient Prosperous/Spectral/Piercing | 90 / 90 | 80/80 (100%) | none observed; legal Crit Chance is 1.53 | n=80, min 556.140, median 1094.433, mean 1067.453, max 1411.413 |
| Ancient Prosperous/Spectral/Shredding | 90 / 88 | 80/80 (100%) | none observed; legal Crit Chance is 1.53 | n=80, min 536.964, median 1079.867, mean 1051.351, max 1422.970 |

The Shredding build won the short screen but lost the official distribution.
The winner is selected by mean post-mitigation critical damage, not its random
maximum.

### Isolated 20-second sustained-DPS screen

Each row ran in a fresh server process. The fixed window includes legitimate DoT
and therefore records many more damage events than released arrows for
Prosperous/Spectral profiles.

| Profile | Releases | Damage events | DPS |
|---|---:|---:|---:|
| `GENESIS_SINGLE_CRITICAL_FOCUS` | 20 | 17 | 118.301 |
| `GENESIS_SINGLE_WARP_FLETCHING` | 20 | 17 | 127.486 |
| `GENESIS_SUSTAINED_CRITICAL_FOCUS` | 31 | 25 | 132.480 |
| `GENESIS_SUSTAINED_WARP_FLETCHING` | 31 | 25 | 133.267 |
| `ANCIENT_SINGLE_MAGICAL_SPECTRAL` | 20 | 457 | 2183.485 |
| `ANCIENT_SINGLE_PROSPEROUS_SPECTRAL` | 20 | 469 | **2252.172** |
| `ANCIENT_SINGLE_PROSPEROUS_SPECTRAL_VERDANT` | 20 | 463 | 1594.544 |
| `ANCIENT_SINGLE_PROSPEROUS_SPECTRAL_MOLTEN` | 20 | 463 | 1497.388 |
| `ANCIENT_SINGLE_PROSPEROUS_SPECTRAL_SHREDDING` | 20 | 463 | 2184.651 |
| `ANCIENT_SUSTAINED_PROSPEROUS_SPECTRAL_WARLORD` | 67 | 488 | 875.201 |
| `ANCIENT_SUSTAINED_PROSPEROUS_SPECTRAL_TYRANNICAL` | 67 | 488 | 654.184 |
| `ANCIENT_SUSTAINED_MAGICAL_SPECTRAL_WARLORD` | 67 | 475 | 846.313 |
| `ANCIENT_SUSTAINED_PIERCING_WARLORD` | 31 | 476 | 1351.452 |
| `ANCIENT_SUSTAINED_SHREDDING_WARLORD` | 31 | 483 | 1300.391 |

Official APO profiles:

1. `MAX_APO_SINGLE_HIT = ANCIENT_SINGLE_PROSPEROUS_SPECTRAL` — mean critical
   hit `1067.4534` on the controlled target.
2. `MAX_APO_SUSTAINED = ANCIENT_SINGLE_PROSPEROUS_SPECTRAL` — fixed-window
   sustained result `2252.1718 DPS`.

The same Ancient build wins both categories. Ancient wins over Genesis for both;
Genesis Grade's extra socket does not compensate for its incomplete affix pool
in this installed stack and controlled target.

## Tensura:L2Hostility datapack eligibility smoke

The earlier Luminous rejection was recorded before the required datapack was
installed and is superseded by this section. The local world now contains
`run/world/datapacks/Tensura-L2Hostility.zip`; it is runtime-only and is not
tracked. The live `datapack list enabled` response was:

```text
There are 3 data pack(s) enabled: [vanilla (built-in)], [mod_data], [file/Tensura-L2Hostility.zip (world)]
```

The live selectors confirmed every requested entity is in
`#l2hostility:whitelist` and the seven bosses are declared in the pack's
`#l2hostility:semiboss` tag. The pack defines these entity level ranges:

| Entity | Configured level range | Health scale | Attack scale |
|---|---:|---:|---:|
| `tensura:hinata_sakaguchi` | 120-280 | 0.90 | 1.10 |
| `tensura:gazel_dwargo` | 110-260 | 1.00 | 1.00 |
| `tensura:orc_disaster` | 100-250 | 1.20 | 1.00 |
| `tensura:elemental_colossus` | 75-150 | 1.30 | 0.80 |
| `tensura_neb:luminous_valentine` | 130-300 | 0.85 | 1.20 |
| `tensura_neb:carrion` | 90-210 | 1.10 | 0.95 |
| `tensura_neb:rimuru_ogre_fight` | 85-250 | 0.95 | 0.90 |

The initial diagnostic used `NoAI` before L2 initialization and correctly
produced no useful level. Exact L2 3.0.18 bytecode showed why: this runtime has
`allowNoAI = false`, and `MobTraitCap.init` suppresses NoAI mobs. The valid smoke
therefore used an explicitly ticking/force-loaded chunk and did not set NoAI
before attachment. No whitelist or compatibility patch was needed.

### Natural/default observations

All values below are current values after the datapack filled each Tensura
resource to its scaled effective maximum. Trait rolls are the exact accepted
official-pass rolls, not required fixed packages.

| Entity | L2 | Generated traits/ranks | Max HP | SHP | Magicules | Aura | SHP / Magic-Aura multiplier |
|---|---:|---|---:|---:|---:|---:|---:|
| `tensura:hinata_sakaguchi` | 124 | Freezing 1; Reflect 2 | 10000 | 16992 | 1866083.88 | 1740000 | 4.72x / 3.48x |
| `tensura:gazel_dwargo` | 122 | Cursed 1; Fiery 1; Reflect 1; Tank 5 | 10000 | 16776 | 1031656 | 2532978.64 | 4.66x / 3.44x |
| `tensura:orc_disaster` | 109 | Blindness 1; Cursed 1; Drain 1; Regenerate 2; Slowness 1; Tank 5; Wither 1 | 6893.6 | 11529 | 771426.66 | 159 | 4.27x / 3.18x |
| `tensura:elemental_colossus` | 84 | Freezing 1; Speedy 2; Tank 3 | 4104.96 | 15840 | 891070.52 | 134 | 3.52x / 2.68x |
| `tensura_neb:luminous_valentine` | 132 | Reflect 1; Slowness 4; Soul Burner 2 | 10000 | 49600 | 14741588.68 | 3729758.76 | 4.96x / 3.64x |
| `tensura_neb:carrion` | 99 | Poison 2; Regenerate 2; Speedy 1; Tank 2 | 10000 | 11910 | 342166.58 | 1514960.48 | 3.97x / 2.98x |
| `tensura_neb:rimuru_ogre_fight` | 85 | Fiery 1; Regenerate 3 | 6845 | 10650 | 295101.9 | 134244 | 3.55x / 2.70x |

Every attachment reported `initialized: true`; every level is inside its exact
entity range; and every target carried the datapack's `l2_tensura_scaled` marker.

### Requested Lv300 observations

The smoke used L2's own `level set 300` followed by
`rerollTraitNoSuppression`. This keeps the entity config ceilings and normal
trait rules. The datapack's existing one-shot modifiers were then removed from
only the disposable test entity, its marker was cleared, and its own tick
function reapplied the formulas at the stored level. No trait was manually
inserted.

| Entity | Exact level after request | Generated traits/ranks | Max HP | SHP | Magicules | Aura | SHP / Magic-Aura multiplier |
|---|---:|---|---:|---:|---:|---:|---:|
| `tensura:hinata_sakaguchi` | 280 (capped) | Dispell 2; Reflect 3; Speedy 1 | 10000 | 33840 | 3539124.6 | 3300000 | 9.40x / 6.60x |
| `tensura:gazel_dwargo` | 260 (capped) | Adaptive 2; Fiery 1; Poison 3; Reflect 1; Tank 2 | 10000 | 31680 | 1859380 | 4565252.2 | 8.80x / 6.20x |
| `tensura:orc_disaster` | 250 (capped) | Cursed 3; Drain 2; Regenerate 2; Speedy 2; Tank 4; Wither 1 | 10000 | 22950 | 1455522 | 300 | 8.50x / 6.00x |
| `tensura:elemental_colossus` | 150 (capped) | Blindness 2; Speedy 3; Tank 3; Wither 1 | 6576 | 24750 | 1329956 | 200 | 5.50x / 4.00x |
| `tensura_neb:luminous_valentine` | 300 | Dispell 3; Killer Aura 1; Reflect 2; Soul Burner 2; Speedy 1; Weakness 1; Wither 1 | 10000 | 100000 | 28349209 | 7172613 | 10.00x / 7.00x |
| `tensura_neb:carrion` | 210 (capped) | Cursed 1; Erosion 1; Regenerate 2; Speedy 2; Tank 2 | 10000 | 21900 | 597069.2 | 2643555.2 | 7.30x / 5.20x |
| `tensura_neb:rimuru_ogre_fight` | 250 (capped) | Adaptive 2; Blindness 2; Drain 2; Freezing 2; Regenerate 1; Slowness 4; Wither 2 | 10000 | 25500 | 655782 | 298320 | 8.50x / 6.00x |

The scaling is visibly and numerically applied to all seven targets. At stored
level `L`, the observed SHP multiplier is exactly `1 + 0.03L`, while the
Magicule and Aura multipliers are exactly `1 + 0.02L`, matching the installed
datapack functions. Luminous now legitimately receives L2 Lv300 and is the
preferred target for the next benchmark step. This is still a compatibility
smoke; no damage/balance conclusion or 39-trait matrix is included.

The official Apotheosis winner remains unchanged:
`ANCIENT_SINGLE_PROSPEROUS_SPECTRAL`.

## Suite A APO-only boss benchmark

Suite A locks the official `ANCIENT_SINGLE_PROSPEROUS_SPECTRAL` bow, leaves the
TNO scalable Engraving family absent (`TNO_family = NONE`, `TNO_stage = Native`),
and uses ten released arrows with a 200-tick observation window per case. Stress
levels use only the benchmark's temporary in-memory ceiling lift for native L2
reinitialization; they remain explicitly non-legal profiles and do not modify
the datapack or production balance.

The accepted post-fix captures below all report initialized L2 attachments, the
correct APO/TNO profile, complete observation windows, structured per-hit rows,
and zero case errors. The tracked raw JSONL evidence is documented in
[`docs/benchmarks/phase5f-suite-a/README.md`](benchmarks/phase5f-suite-a/README.md).

| Boss / level | Mode | Shots / crits / blocked | Direct | DoT | Regen | DPS | Result |
|---|---|---:|---:|---:|---:|---:|---|
| Luminous 215 | Natural representative | 10 / 0 / 10 | 0 | 0 | 0 | 0 | Native defenses cancelled every arrow |
| Luminous 300 | Natural maximum | 10 / 0 / 10 | 0 | 0 | 0 | 0 | Native defenses cancelled every arrow |
| Luminous 600/800/1000 | Stress | 10 / 0 / 10 each | 0 | 0 | 0 | 0 | Fully blocked at every stress level |
| Hinata 200 | Natural representative | 10 / 0 / 10 | 0 | 0 | 0 | 0 | Native defenses cancelled every arrow |
| Hinata 280 | Natural maximum | 10 / 0 / 10 | 0 | 0 | 0 | 0 | Native defenses cancelled every arrow |
| Hinata 300/600/800/1000 | Stress | 10 / 0 / 10 each | 0 | 0 | 0 | 0 | Fully blocked at every stress level |
| Gazel 185 | Natural representative | 10 / 0 / 10 | 0 | 0 | 0 | 0 | Native defenses cancelled every arrow |
| Gazel 260 | Natural maximum | 10 / 0 / 10 | 0 | 0 | 0 | 0 | Native defenses cancelled every arrow |
| Gazel 300/600/800/1000 | Stress | 10 / 0 / 10 each | 0 | 0 | 0 | 0 | Fully blocked at every stress level |
| Orc Disaster 175 | Natural representative | 9 / 8 / 1 | 10560.2271 | 20.4000 | 1348.6401 | 1306.2503 | Defeated in 9 hits / 162 ticks |
| Orc Disaster 250 | Natural maximum | 10 / 5 / 5 | 7681.8533 | 12.0000 | 1158 | 769.3853 | Survived at 3464.1462 HP |
| Orc Disaster 300/600/800/1000 | Stress | 10 / 0 / 10 each | 0 | 0 | 0 | 0 | Fully blocked at every stress level |
| Elemental Colossus 112 | Natural representative | 10 / 0 / 10 | 0 | 5.6000 | 5.1987 | 0.5600 | Direct arrows blocked; small `minecraft:wither` DoT persisted |
| Elemental Colossus 150 | Natural maximum | 10 / 0 / 10 | 0 | 1.5200 | 1.2407 | 0.1520 | Direct arrows blocked; small `minecraft:wither` DoT persisted |
| Elemental Colossus 300/600/800/1000 | Stress | 10 / 0 / 10 each | 0 | 0 | 0 | 0 | Fully blocked at every stress level |
| Carrion 150 | Natural representative | 10 / 0 / 10 | 0 | 0 | 0 | 0 | Native defenses cancelled every arrow |
| Carrion 210 | Natural maximum | 10 / 0 / 10 | 0 | 0 | 0 | 0 | Native defenses cancelled every arrow |
| Carrion 300/600/800/1000 | Stress | 10 / 0 / 10 each | 0 | 0 | 0 | 0 | Fully blocked at every stress level |
| Rimuru Ogre Fight 167 | Natural representative | 10 / 0 / 10 | 0 | 0 | 0 | 0 | Native defenses cancelled every arrow |
| Rimuru Ogre Fight 250 | Natural maximum | 10 / 0 / 10 | 0 | 0 | 0 | 0 | Native defenses cancelled every arrow |
| Rimuru Ogre Fight 300/600/800/1000 | Stress | 10 / 0 / 10 each | 0 | 0 | 0 | 0 | Fully blocked at every stress level |

Tank's armor/toughness increase is visible in the captured snapshots. Reflect
appears on multiple fully blocked profiles but produced no reflected damage.
Regenerate is directly measurable on Orc Disaster when damage lands; at its
natural representative it restored 1348.6401 HP during the fixed window, and at
the natural maximum it restored 1158 HP. Adaptive, Dispell, Dementor, Reprint,
and Ragnarok rolls are preserved with exact ranks in the JSONL case records;
their presence is not presented as isolated causation where native defense had
already reduced every hit to zero.

Elemental Colossus likewise cancelled all direct arrow events. Its two natural
cases recorded only post-release `minecraft:wither` ticks: 5.6000 damage against
5.1987 regeneration at level 112, and 1.5200 against 1.2407 at level 150. The
stress cases produced neither direct nor DoT damage. This is classified as
heavy suppression rather than meaningful APO direct damage.

Carrion fully blocked all 60 released arrows across its two natural and four
stress cases. Its generated defensive rolls included Tank in every case,
Regenerate in every case, Reflect 3 at stress level 600, and Dispell 1 at stress
level 800. Because no damage landed, regeneration and reflected damage both
remained zero; Ragnarok 2 at level 1000 did not change that outcome.

Rimuru Ogre Fight fully blocked all 60 released arrows. Adaptive 2 appeared in
every case; Dispell 3 and Reflect 1 co-occurred at level 600, while Dementor 1,
Tank 5, and Ragnarok 1 co-occurred at level 1000. None of those profiles
recorded direct, DoT, regeneration, or reflected damage during the fixed window.

### Suite A completion summary

All seven isolated official captures passed: 41 cases, 409 machine-readable
per-shot rows, and zero `case_error` records. The single short case is Orc
Disaster's valid nine-hit defeat at natural representative level 175.

| Level group | Cases | APO-only outcome |
|---|---:|---|
| Natural representative | 7 | Five bosses fully blocked; Elemental allowed only 0.5600 DPS of post-release Wither damage; Orc allowed 1306.2503 DPS and was defeated |
| Natural maximum | 7 | Five bosses fully blocked; Elemental allowed only 0.1520 DPS of post-release Wither damage; Orc allowed 769.3853 DPS and survived |
| Stress 300 | 6 | All six above-ceiling stress profiles produced 0 DPS; Luminous's legal natural maximum is already level 300 and also produced 0 DPS |
| Stress 600 | 7 | Every boss produced 0 DPS |
| Stress 800 | 7 | Every boss produced 0 DPS |
| Stress 1000 | 7 | Every boss produced 0 DPS |

Classification for this exact runtime stack and accepted random trait rolls:

- Fully block APO physical damage at every tested level: Luminous, Hinata,
  Gazel, Carrion, and Rimuru Ogre Fight.
- Heavily suppress APO damage: Elemental Colossus, which blocked every direct
  event and admitted only tiny natural-level Wither ticks; Orc Disaster at all
  four stress levels.
- Allow meaningful APO damage: Orc Disaster at its natural representative and
  natural maximum levels only.
- Regeneration materially affected the two damaging Orc cases (1348.6401 and
  1158 HP restored). Elemental's small natural-level Wither totals were almost
  entirely offset by ordinary observed healing. Regenerate rolls on fully
  blocked profiles had no damage to restore.

Notable defensive-trait coverage across the 41 accepted cases:

| Trait | Cases / ranks observed | Runtime observation |
|---|---|---|
| Tank | 29; ranks 1-5 | Armor/toughness changes were recorded; it coexisted with both Orc's damaging natural cases and many fully blocked cases, so it is not isolated as the universal cancellation source |
| Adaptive | 11; ranks 1-3 | Every Adaptive case produced 0 DPS, including all six Rimuru cases |
| Reflect | 19; ranks 1-3 | No reflected damage was recorded because the corresponding direct events were cancelled |
| Regenerate | 24; ranks 1-5 | Measurable only where damage landed; zero on untouched full-health targets |
| Dispell | 14; ranks 1-3 | All Dispell profiles produced 0 DPS, including every Hinata and Luminous case |
| Dementor | 5; rank 1 | All five cases produced 0 DPS |
| Ragnarok | 5; ranks 1-2 | All five cases produced 0 DPS |
| Protection | 0 | Not naturally generated in this accepted Suite A sample |
| Repelling | 0 | Not naturally generated in this accepted Suite A sample |
| Arena | 0 | Not naturally generated in this accepted Suite A sample |

No missing trait was forced: Suite A preserves natural/legal L2 generation as
the balance evidence. Exact boss, level, trait IDs/ranks, resources, attributes,
per-hit values, damage types, and final state remain in the tracked JSONL files.

## Suite B Checkpoint 2 completion

Checkpoint 2 is closed from 21 accepted machine-readable boss artifacts: seven
each for Magic Weapon, Holy Weapon, and Soul Eater. The locked Suite B protocol
produced 1,107 cases and 11,070 per-hit rows with zero unresolved `case_error`
records, APO profile `NONE` throughout, and no unexpected L2 bypass.

| Family | Bosses | Cases | Rows | Average DPS Native -> S7 | Zero through S4 / at S7 | Result |
|---|---:|---:|---:|---:|---:|---|
| Magic Weapon | 7 | 369 | 3,690 | 2.09 -> 9.90 | 23 / 6 | Mixed progression; no `TOO STRONG` or `OP` profile |
| Holy Weapon | 7 | 369 | 3,690 | 2.99 -> 9.46 | 17 / 6 | Mixed progression; no `TOO STRONG` or `OP` profile |
| Soul Eater | 7 | 369 | 3,690 | 0.064 -> 0.030 | 35 / 35 | `EFFECTIVELY DEAD` / non-functional on Royal Arrow |

Magic Weapon encountered matching Magic Resistance in 23 boss/level profiles
and no Magic Nullification. Eligible native Magic amounts exposed the configured
S5-S7 matching-Resistance recovery after Native-S4 suppression. Adaptive,
Dementor, and Dispell transformed 590, 180, and zero rows respectively. Dispell
did not transform `tensura:magic` because the source was not in
`neoforge:is_magic`. Gazel remained fully `EFFECTIVELY DEAD`; no Magic Weapon
result reached `TOO STRONG` or `OP`.

Holy Weapon encountered matching Holy Resistance in 17 profiles and no Holy
Nullification. Eligible native Holy amounts likewise exposed S5-S7 recovery.
Adaptive, Dementor, and Dispell transformed 756, 90, and zero rows respectively.
Dispell did not transform `tensura:holy_damage` because the source was not in
`neoforge:is_magic`. Gazel remained fully `EFFECTIVELY DEAD`; no Holy Weapon
result reached `TOO STRONG` or `OP`.

Soul Eater is effectively non-functional on Royal Arrow in this runtime path.
Luminous, Hinata, Gazel, Elemental Colossus, Carrion, and Rimuru Ogre Fight
produced no native `tensura:soul_scatter` event and therefore no eligible Soul
amount for Stage scaling. Orc Disaster produced only residual physical Royal
Arrow damage, and `engraving_native_amount` remained zero there as well.
Consequently Stage scaling and S5-S7 matching-Resistance recovery had no Soul
amount to amplify or recover.

The Soul Eater result is a benchmark/runtime compatibility finding, not
permission to alter its production behavior. Checkpoint 2 makes no change to
Stage thresholds, Curve C, matching-Resistance recovery, native Tensura or L2
mechanics, datapack behavior, or Royal Bow/Royal Arrow base damage. Soul Eater
is not fixed or rebalanced here.

The detailed artifact inventory and per-boss findings are in
`docs/benchmarks/phase5f-suite-b/README.md`.

## Checkpoint 3 — Elemental / Slotting (complete)

The Elemental family uses the installed native Slotting behavior rather than a
fabricated Royal Arrow event. One legal Earth core on the Royal Bow causes
Tensura to create `tensura:stone_shot`; the projectile retains its owner and
emits `tensura:earth_elemental`. Runtime tags contain
`minecraft:bypasses_armor` and do not contain `neoforge:is_magic`. The temporary
Stage fixture scales only the native projectile damage coefficient (`1.0`), not
slot capacity/count, projectile utility, Royal Bow base damage, or Royal Arrow
base damage. No Royal Arrow exists on this native release path.

The first accepted artifact is Luminous: 45 cases, 450 per-hit rows, zero case
errors, APO profile `NONE`, and no unexpected L2 bypass. Native Earth
Nullification canceled every one of the 14 observable Earth events and remained
absolute through S7, so average DPS was `0.00 -> 0.00` and all five profiles are
`EFFECTIVELY DEAD` for this representative Elemental path. Naturally present
Dispell and Adaptive did not override the upstream native nullification, and
Dispell also correctly saw the actual source as non-magic.

Hinata is also accepted: 54 cases, 540 per-hit rows, zero case errors, and no
unexpected L2 bypass. All six profiles had Earth Nullification plus Spiritual
Resistance. Earth Nullification canceled all 14 observable Earth events and
kept Stage penetration at zero, yielding average DPS `0.00 -> 0.00` and six
more `EFFECTIVELY DEAD` profiles. Dispell was naturally present throughout but
did not transform the actual non-magic source.

Gazel is accepted with 54 cases, 540 per-hit rows, zero case errors, and no
unexpected L2 bypass. Its six profiles had matching Earth and Spiritual
Resistance but no Nullification. All 12 observable Earth events were canceled
by that native resistance layer, and no eligible Earth event was emitted in
S5-S7 for configured recovery to restore. Average DPS therefore remained
`0.00 -> 0.00`; naturally rolled Adaptive and Dementor profiles had no nonzero
post-resistance amount to transform.

Orc Disaster is accepted with 54 cases, 540 per-hit rows, zero case errors, and
no unexpected L2 bypass. With no matching Tensura defense, it supplied the
positive control: Lv175 Native reached 1.0 DPS and S0 about 0.495 DPS through 14
real Earth events. No eligible Earth event was emitted in the other 52 cases;
every S7 profile was zero and average DPS fell `0.167 -> 0.00`. A naturally
present Dispell profile correctly did not transform the actual non-magic
source. This runtime result does not alter native Slotting or the Stage fixture.

Elemental Colossus is accepted with 54 cases, 540 per-hit rows, zero case
errors, and no unexpected L2 bypass. Fourteen real Earth events appeared only
in Lv112 Native/S0; the other 52 cases and every S7 profile were zero, so
average DPS fell `0.035 -> 0.00`. Two profiles each naturally rolled Adaptive
and Dementor, but no nonzero repeated post-L2 sequence remained to transform.

Carrion is accepted with 54 cases, 540 per-hit rows, zero case errors, and no
unexpected L2 bypass. Matching Earth Resistance canceled all 14 observable
Native/S0 Earth events, no eligible event appeared later for recovery, and all
54 cases remained zero. Natural Adaptive, Dispell, and Dementor profiles had no
nonzero post-resistance sequence to transform.

Rimuru Ogre Fight is accepted with 54 cases, 540 per-hit rows, zero case
errors, APO profile `NONE`, and no unexpected L2 bypass. It emitted no native
Earth event and stayed at `0.00 -> 0.00` average DPS despite having neither
matching Earth Resistance nor Earth Nullification. Adaptive was present in all
six profiles and Dementor in two, but there was no native event sequence for
either trait or Stage to transform.

The completed Elemental / Slotting family contains seven accepted artifacts,
369 cases, and 3,690 per-hit rows, with zero case errors, APO profile `NONE`
throughout, and no unexpected L2 bypass. Across 41 boss/level profiles, average
DPS was `0.029512 Native -> 0.00 S7`; 365 of 369 cases were zero, 39 profiles
were zero through S4, and every S7 profile was zero. No result reached `TOO
STRONG` or `OP`.

Matching Earth Nullification remained absolute on Luminous and Hinata. Gazel
and Carrion had matching Earth Resistance, but no eligible S5-S7 event existed
for configured recovery. The only nonzero controls were Orc Disaster Lv175
and Elemental Colossus Lv112 in Native/S0. On both bosses the native Earth event
disappeared in later independently reset Stage cases despite no matching
Tensura Resistance or Nullification; Rimuru never emitted the event. Across 13
Adaptive, 13 Dispell, and six Dementor profiles, zero rows recorded a transform:
the Earth source was not magic, or upstream cancellation/event absence left no
sequence to transform. Elemental / Slotting is therefore `EFFECTIVELY DEAD` as
a Stage progression path in this runtime apart from those isolated low-level
positive controls. The result is evidence only and does not change native
Slotting, Stage coefficients, matching-Resistance recovery, or production
combat behavior.

## Checkpoint 3 — Energy Steal (complete)

Energy Steal I uses the installed native post-damage operation: one percent of
the target's current Aura and current Magicules, a native 20-tick bow cooldown,
and no DamageSource. The temporary Stage fixture scales only the eligible
current-pool percentage; it does not change Royal Arrow base damage, the native
cooldown, target resource maxima, or production behavior.

Luminous is accepted with 45 cases, 450 per-hit rows, zero case errors, APO
profile `NONE`, and no unexpected L2 bypass. Every Royal Arrow was canceled
before the native post-damage hook, so no Energy Drain event was emitted and
resource impact remained `0.00 Native -> 0.00 S7`. All five profiles naturally
contained Dispell, but no Energy event or DamageSource existed to transform.

Gazel is accepted with 54 cases, 540 per-hit rows, zero case errors, APO
profile `NONE`, and no unexpected L2 bypass. Every Royal Arrow was canceled
before the native post-damage hook, so no Energy Drain event was emitted and
resource impact remained `0.00 Native -> 0.00 S7`. One profile naturally
contained Dementor, but no Energy operation or DamageSource existed to
transform.

Orc Disaster is accepted with 54 cases, 540 per-hit rows, zero case errors,
APO profile `NONE`, and no unexpected L2 bypass. All 54 cases emitted at least
one Energy Drain event (81 event rows total), and each passed exact native
one-percent/current-pool, Stage-coefficient, target-drain/attacker-gain, and
non-DamageSource invariants. Average resource impact rose from 4,257.302/s
Native to 6,047.549/s at S7. Lv175 was non-monotonic because eligible events
fell from 10 Native to one at S7; the per-event formula remained exact. One
Dispell and one Dementor profile did not transform the non-DamageSource energy
operation.

Elemental Colossus is accepted with 54 cases, 540 per-hit rows, zero case
errors, APO profile `NONE`, and no unexpected L2 bypass. Every Royal Arrow was
canceled before the native post-damage hook, so no Energy Drain event was
emitted and resource impact remained `0.00 Native -> 0.00 S7`. One profile
naturally contained Adaptive, but no eligible hit sequence reached the Energy
operation.

Carrion is accepted with 54 cases, 540 per-hit rows, zero case errors, APO
profile `NONE`, and no unexpected L2 bypass. Every Royal Arrow was canceled
before the native post-damage hook, so no Energy Drain event was emitted and
resource impact remained `0.00 Native -> 0.00 S7`. No Adaptive, Dispell, or
Dementor profile rolled.

Rimuru Ogre Fight is accepted with 54 cases, 540 per-hit rows, zero case
errors, APO profile `NONE`, and no unexpected L2 bypass. Every Royal Arrow was
canceled before the native post-damage hook, so no Energy Drain event was
emitted and resource impact remained `0.00 Native -> 0.00 S7`. Adaptive rolled
in all six profiles but had no eligible physical-hit sequence to adapt before
the Energy operation.

The completed Energy Steal family contains seven accepted artifacts, 369
cases, and 3,690 per-hit rows, with zero case errors, APO profile `NONE`
throughout, and no unexpected L2 bypass. All 81 Energy Drain events occurred on
Orc Disaster; all 54 Orc cases were nonzero, while the other 315 cases were
zero before the native post-damage hook. Across 41 profiles, average resource
impact was `623.019818/s Native -> 885.007144/s S7`; Orc alone measured
`4,257.302087/s -> 6,047.548818/s`.

Every emitted event retained the native one-percent current-Magicules/current-
Aura operation, the exact Stage coefficient up to 1.4 percent at S7, equal
target drain and attacker gain, and no DamageSource. Aggregate case progression
was sometimes non-monotonic because the number of surviving physical hits that
reached the post-damage hook varied; the per-event formula did not. Seven
Adaptive, 12 Dispell, and two Dementor profiles did not directly transform the
non-DamageSource operation. Energy Steal is measurable on Orc and `EFFECTIVELY
DEAD` on the other six bosses in this runtime path. No production behavior or
balance value was changed.

## Checkpoint 3 — Severance (in progress)

Severance I is measured through the installed Royal Arrow path as one combined
physical `minecraft:arrow` source, not a second DamageSource. Its native `+3`
attack contribution is applied before projectile velocity and vanilla ceiling;
the temporary Stage fixture scales only that eligible contribution with the
locked pre-round formula. It does not change base bow/arrow damage, velocity,
native wound cancellation, L2, or production behavior.

Luminous is accepted with 45 cases, 450 per-hit rows, zero case errors, APO
profile `NONE`, and no unexpected L2 bypass. All 450 combined physical pre-L2
events retained exact source, velocity, native `+3`, Stage, and rounding
invariants. Post-L2 physical damage was zero on every row, so average DPS
remained `0.00 Native -> 0.00 S7` and no Severance wound was stored. Dispell
was present in all five profiles and Adaptive in one, but no accepted physical
sequence remained to transform.

Hinata is accepted with 54 cases, 540 per-hit rows, zero case errors, APO
profile `NONE`, and no unexpected L2 bypass. All 540 combined physical pre-L2
events retained the exact source/velocity/native-`+3`/Stage/rounding path, but
post-L2 physical damage and Severance wound storage were zero throughout.
Average DPS remained `0.00 Native -> 0.00 S7`. Dispell was present in all six
profiles and Adaptive in one, with no accepted sequence to transform.

Gazel is accepted with 54 cases, 540 rows, zero errors, and no unexpected L2
bypass. Exact Severance configuration math remained present throughout; 486
rows reached the incoming arrow probe, but all post-L2 damage and wound storage
were zero, leaving `0.00 Native -> 0.00 S7` DPS.

Orc Disaster is accepted with 54 cases, 540 rows, zero errors, APO profile
`NONE`, and no unexpected L2 bypass. All 540 rows retained the combined
physical/projectile source and exact velocity/native-`+3`/Stage/ceiling math;
93 hits survived L2 and stored native Severance wound. Average DPS was
`0.957775 Native -> 0.539537 S7`, driven by 17 surviving Native hits versus
nine at S7 rather than a reversal of the per-hit Stage formula. All six legal
profiles contained Tank and Regenerate; Regenerate produced no separately
recorded healing row, Dispell did not transform the Lv800 source, and Adaptive
was observed on 12 Lv1000 rows. No Dementor rolled. Eight surviving S0 hits
still collapsed to the native ceiled amount despite their higher pre-round
Stage value. The validator was corrected for Tensura's native `0.5` minimum
wound clamp on an admitted sub-`0.5` physical hit, while zero post-L2 damage
continues to require zero wound storage.

Hinata is accepted with 54 cases, 540 per-hit rows, zero case errors, APO
profile `NONE`, and no unexpected L2 bypass. Every Royal Arrow was canceled
before the native post-damage hook, so no Energy Drain event was emitted and
resource impact remained `0.00 Native -> 0.00 S7`. All six profiles naturally
contained Dispell, but no Energy event or DamageSource existed to transform.

## Remaining L2 benchmark work

The final instance config retains `maxMobLevel = 3000`, `maxTraitCount = 9`, and
all requested trait toggles including Arena and Ragnarok enabled. The full
39-trait and multi-boss matrix remains later work. No forced trait profile, Stage
curve, penetration value, EP threshold or production combat behavior was added
or changed here.

## Verification completed

- `.\gradlew.bat clean build` passed with the local Royal Variations artifact
  present. This repository currently has no test sources, so Gradle reported
  `test NO-SOURCE`.
- The same clean build passed while that private JAR was temporarily renamed out
  of Gradle's expected path, then the JAR was restored. This proves clean-clone
  configuration and compilation do not require Royal Variations, Apotheosis or
  L2 artifacts.
- `runServer` with `-Pphase5f_runtime_mods_dir=<target mods>` reached `Done`,
  emitted the structured Royal Bow report, confirmed all relevant versions and
  recipes, and produced the rarity/affix/socket results above.
- A fresh `runServer` loaded `file/Tensura-L2Hostility.zip` and returned the live
  attachment, natural-roll, requested-level and Tensura-resource results for all
  seven requested bosses above. The temporary local RCON switch used to issue
  commands was restored to disabled and is not tracked.
- Seven isolated Suite A `runServer` captures completed with the locked APO-only
  profile: 41 accepted cases, 409 per-shot records, and zero case errors. The
  ignored runtime logs were reduced to validated tracked JSONL evidence before
  each subsequent server run.
- `runClient` with the same optional exact-stack directory completed mod loading,
  initialized OpenAL, created the GUI atlas and preloaded Patchouli content with
  no fatal/crash marker. It was manually stopped after main-menu readiness.
- Datagen was not run because this phase changes no generated registry/data
  resources.
