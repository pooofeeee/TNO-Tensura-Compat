# Phase 5F — L2 / Apotheosis / TNO Benchmark Plan

Status: runtime instrumentation and the Apotheosis-only controlled benchmark are
complete. The full L2 trait/boss matrix remains future work. No balance values
are changed by this phase.

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
Tensura current/max SHP, L2 initialization state, level, and every trait ID/rank
with its live maximum rank where accessible.

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

## Preliminary L2 Lv300 smoke proof

Luminous is present but is rejected by L2 Hostility's live attachment predicate:
it is neither `Enemy` nor included in `l2hostility:whitelist`. The other installed
NEB boss candidates checked before the fallback also did not pass that predicate.
The smoke test therefore used `minecraft:wither`, for which Tensura
`entity_existence` data exists and L2 accepts a normal attachment.

With the official winning Royal Bow equipped, the isolated smoke reported:

- L2 initialized: `true`;
- L2 level: `300`;
- forced traits: `false`;
- naturally rolled trait count: `0` in this smoke run;
- real Bow direct events: `2`;
- real Bow post-mitigation damage: `1577.6461791992188`;
- the expected winning-build attributes, including Arrow Damage `3.0224999815`,
  Armor Pierce `31`, Protection Pierce `15`, Crit Chance `1.5300000191`, and Crit
  Damage `5.8799999714`.

This proves the winning Apotheosis stack can fire through the real Tensura + L2
runtime path at L2 Lv300 without a forced illegal trait package. It is a
compatibility smoke only and is not boss-balance evidence.

## L2 runtime proof and remaining benchmark work

The target command was executed in the exact optional stack against a summoned
`minecraft:zombie`. It reported HP 20/20, armor 2, toughness 0, Tensura SHP
40/40, and an initialized L2 attachment at level 0 with an empty trait map. This
proves the registry, SHP and L2 attachment/trait paths without forcing traits or
changing balance state.

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
- The target command ran in that server and returned the live zombie/L2/Tensura
  result above. The temporary local RCON switch used to issue the command was
  restored to disabled and is not tracked.
- `runClient` with the same optional exact-stack directory completed mod loading,
  initialized OpenAL, created the GUI atlas and preloaded Patchouli content with
  no fatal/crash marker. It was manually stopped after main-menu readiness.
- Datagen was not run because this phase changes no generated registry/data
  resources.
