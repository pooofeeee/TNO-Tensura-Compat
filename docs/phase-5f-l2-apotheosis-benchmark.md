# Phase 5F — L2 / Apotheosis / TNO Benchmark Plan

Status: planning + runtime instrumentation only. No balance values are changed by this phase until measurements justify a change.

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

## Immediate next step

Before writing any balance logic, build a runtime inspector / benchmark helper that can print:

1. Royal Bow Apotheosis loot category and affixability.
2. Current rarity, affixes and effective affix levels.
3. Socket count and installed gems / purities.
4. Relevant Apothic Attributes values (Arrow Damage, Arrow Velocity, Draw Speed, Armor Pierce/Shred, Protection Pierce/Shred, Crit Chance/Damage).
5. Target L2 level and exact traits / ranks.
6. Hit result before and after the target takes damage where the event API allows observation.

Keep all helper code development-only and production-inert.
