# Phase 6 production Stage implementation

## Status

Checkpoints 6A through 6E are implemented, tested, committed, and pushed on `phase-6-production-stage-framework`. Checkpoint 6F is design-blocked. The repository does not establish Royal Bow's TNO Common/Rare classification or the production trigger for its first applicable Engraving roll. The Phase 6 stop condition prohibits inventing either rule, so Royal Bow remains deliberately absent from the external-gear classification table and the end-to-end runtime acceptance has not been represented as complete.

## Architecture and native EP

The production framework is intentionally small:

- `Stage` defines S0-S7 and the locked Curve C coefficients.
- `GearStageClass` defines the Common and Rare EP schedules and caps.
- `StageResolver` derives Stage directly from current native Tensura Gear EP.
- `NativeGearEpSource` reads Tensura 2.0.1.1 `TensuraDataComponents.EP` from the weapon.
- `GearStageClasses` is the explicit external-item classification table. It currently contains no Royal Bow mapping because that classification is unresolved.
- `ProductionStageScaling` joins classification, native EP, Stage, and the active native scalable family.
- `ScalableFamily` is closed to the six authorized families.

There is no TNO EP counter, Stage component, Stage cache, Stage XP, Stage UI, or arrow-owned progression. Native Gear EP remains authoritative on every resolution.

## Stage schedules

Common is capped at S3:

| Stage | Minimum EP |
|---|---:|
| S0 | 0 |
| S1 | 50,000 |
| S2 | 250,000 |
| S3 | 1,000,000 |

Rare supports S0-S7 using the locked 17% threshold discount:

| Stage | Minimum EP |
|---|---:|
| S0 | 0 |
| S1 | 41,500 |
| S2 | 207,500 |
| S3 | 830,000 |
| S4 | 1,245,000 |
| S5 | 1,660,000 |
| S6 | 2,075,000 |
| S7 | 2,490,000 |

Curve C scales only an eligible special Engraving contribution: S0-S7 are respectively 1.05, 1.10, 1.15, 1.20, 1.25, 1.30, 1.35, and 1.40. Unclassified gear or gear without an active scalable native family receives zero TNO combat gain.

## Six native family integrations

### Magic Weapon

The native Tensura additional-damage invocation is wrapped once and only its eligible amount is scaled. The existing `tensura:magic` source holder and its installed tags remain unchanged. No second source or event is emitted, and L2 Dementor behavior remains downstream and authoritative.

### Holy Weapon

The same narrow additional-damage boundary scales only the eligible native Holy amount. The source remains `tensura:holy_damage`; base damage and Apotheosis contributions are outside the operation.

### Soul Eater

The native Tensura spiritual-damage invocation is wrapped when it legitimately occurs. The framework never manufactures `tensura:soul_scatter`; therefore Royal Arrow continues to have no scalable Soul amount in the runtime path documented by Phase 5F.

### Elemental / Slotting

Slotting snapshots the firing weapon's derived Stage onto the native Tensura projectile context and scales only the native projectile damage argument. It does not store independent EP or Stage progression. The installed legal paths are:

- Earth: `tensura:element_core_earth` -> `tensura:stone_shot` -> `tensura:earth_elemental`
- Fire: `tensura:element_core_fire` -> `tensura:fire_bolt` -> `tensura:fire_elemental`
- Space: `tensura:element_core_space` -> `tensura:space_cut_projectile` -> `tensura:space_elemental`
- Water: `tensura:element_core_water` -> `tensura:water_ball` -> `tensura:water_elemental`
- Wind: `tensura:element_core_wind` -> `tensura:wind_sphere` -> `tensura:wind_elemental`

Projectile speed, utility, burn, gravity, knockback, core tier/count, Slotting capacity, and the physical arrow remain unscaled. Deterministic tests reproduce the accepted Native 1.00 through S7 1.40 coefficient series.

### Energy Steal

The native post-hit resource operation is admitted first; TNO then scales only its native 1% percentage argument through Curve C. TNO adds no operation and no `DamageSource`, so a rejected prerequisite cannot produce a phantom drain.

### Severance

The implementation preserves the one combined physical `minecraft:arrow` event. Tensura's installed Severance +3 is first included by native `EnchantmentHelper.modifyDamage`; TNO adds only the Curve C delta on that +3 before native projectile-speed multiplication and the single integer ceiling. Royal Arrow base damage, Apotheosis physical damage, critical output, Arrow Damage, and Arrow Velocity are not multiplied by Stage.

When a real positive eligible pre-round delta would fall into the same native integer bucket, the classified Severance hit advances to the next integer result. This narrow guard fixes the confirmed low-magnitude collapse without changing global projectile rounding or adding post-defense damage. The resulting local value proceeds through the original source, native hurt/L2 order, and Tensura's native after-damage/wound order. A rejected or zero physical hit still cannot store a wound.

## Matching Resistance, Nullification, and L2

Matching Tensura Resistance recovery is independent of Curve C. Its schedule is S0-S4 0%, S5 25%, S6 50%, and S7 100%, using only `post + penetration * (preMatchingResistance - post)`. The hook is at the native Tensura boundary before that matching Resistance and before downstream L2. It never restores loss from any unrelated or downstream defense.

Matching Tensura Nullification is checked first and remains absolute at every Stage. It prevents recovery and no alternate source, fallback amount, or partial bypass is created.

L2 remains downstream and authoritative. TNO does not restore or bypass Adaptive, Dementor, Dispell, Tank, Regen, Arena, Repelling, Teleport, Reflect, or other legal L2 behavior.

## Apotheosis and non-scaled behavior

Apotheosis continues to own generic weapon progression. TNO does not scale raw/base physical damage, Royal Bow or Royal Arrow base damage, Mark, Apotheosis rarity/affixes/gems/crit/projectile multiplication, generic enchantment damage, attributes, piercing, Slotting capacity, core count/tier, or unrelated utility. Real independent Apotheosis projectiles are not collapsed or duplicated.

## Verification completed

- Boundary tests cover immediately below and exactly at every Common/Rare threshold, both caps, and the locked 17% Rare schedule.
- Curve C, all six family-isolation cases, and the no-scalable-Engraving zero-gain invariant pass.
- Deterministic Elemental, Energy Steal, matching Resistance schedule, native HP gate, and recovery interpolation tests pass. The matching-Nullification-first branch is implemented and its mixin loads; its required positive runtime acceptance remains part of blocked 6F.
- Severance tests cover eligible-only +3 scaling, a low-magnitude S0 collapse, naturally distinct ceiling behavior, and large Apotheosis/base isolation.
- Development server startup reached `Done` with the relevant production mixins, Royal Variations, and Tensura's arrow mixin applied without injection errors.
- `gradlew.bat clean build` passed after Checkpoint 6E.
- Phase 5 benchmark listeners remain behind the existing `!FMLEnvironment.production` registration guard; no Phase 6 benchmark listener or temporary runtime instrumentation was added.
- No raw runtime log, world, temporary config, generated capture, or third-party local JAR is tracked by the Phase 6 commits.

The accepted Phase 5F and Phase 6 Elemental pre-flight evidence was not modified.

## Royal Bow end-to-end and first Engraving behavior

The intended chain is Royal Bow -> native Tensura Gear -> native Gear EP -> TNO Stage -> native eligible Engraving -> eligible scaled component -> Tensura defenses -> L2. The generic production pieces through this chain are implemented. The item-specific activation is not.

Two inputs are still required:

1. Royal Bow's explicit TNO Stage class: Common or Rare.
2. The exact production event that performs the first applicable Engraving roll.

The authorized first-roll rarity distribution for the relevant Rare path is preserved as a requirement: Common 35%, Uncommon 35%, Rare 20%, Epic 10%, first applicable roll only, and no guaranteed starting Engraving. No trigger or roll implementation was added because the trigger is not established. Later-roll behavior remains native/previously established.

Until both decisions are supplied, Royal Bow end-to-end activation, positive-control runtime values, strongest-legal L2 validation, and the Ancient Apotheosis coexistence spot check are blocked. This is not a production failure and is not permission to infer a classification or progression event from benchmark fixtures.

## Remaining observations

- High Magic/Holy combined results, absent Royal Arrow Soul events, boss-dependent Elemental availability, Orc-only Energy Steal/Severance observations, and strongest-legal L2 suppression remain accepted non-bug research observations.
- No authorized balance constants, native Tensura mechanics, L2 mechanics, Apotheosis mechanics, Royal Bow/Arrow base damage, Mark behavior, or accepted research evidence were changed.
- Phase 6 status remains `BLOCKED` at 6F, not `COMPLETE`.
