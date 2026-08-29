# Phase 6 pre-flight: Elemental / Slotting positive control

## Decision

**POSITIVE_CONTROL_PASS**

The installed Tensura 2.0.1.1 native Slotting path produced a real Earth projectile and a real Earth Elemental damage event on a neutral target. Native and every S0-S7 fixture matched the locked pre-flight Curve C rule:

`staged eligible Elemental contribution = native eligible Elemental contribution * (1 + Stage coefficient)`

No production combat fix is indicated by this diagnostic. The accepted Phase 5F zero-event results remain unchanged and are classified as target/event availability in those boss paths. Permanent Phase 6 Elemental integration is cleared to proceed in a later task.

Machine-readable evidence: `benchmarks/phase6-preflight-elemental-positive-control.jsonl` (101 records: one catalog, 90 per-release rows, nine Stage summaries, and one complete suite result).

## Live native path

- Bow: `royalvariations:royal_bow`
- Engraving: `tensura:slotting`, level I
- Slotting capacity: 1
- Inserted contents: exactly one `tensura:element_core_earth`
- Release: legal 20-tick main-hand use through `ItemStack.releaseUsing`, intercepted by the installed Tensura `SlottingHelper.onRelease` mixin
- Projectile: `tensura:stone_shot`
- Projectile owner retained: yes
- Native projectile damage coefficient: 1.0
- Damage source: `tensura:earth_elemental`
- Direct entity: `tensura:stone_shot`
- Native pre-defense and final event damage: 1.0
- Royal Arrow produced by the intercepted release: no
- Base physical damage event produced or Stage-scaled: no

The controlled collision used Tensura's accepted projectile-hit entry point. The fixture did not construct a damage source and did not call `hurt` directly.

## Positive-control target

The target was a server-only neutral `LivingEntity` adapter using the `minecraft:armor_stand` entity type and dimensions. It had zero armor and toughness, stable high HP and Spiritual Health, no Apotheosis runtime, no L2Hostility runtime or attachment, and no Earth/Spiritual Resistance or Nullification. It was not one of the seven Phase 5F bosses and did not modify any accepted Phase 5F target.

## Curve C observations

Each row below represents 10 validated releases. The displayed damage is the actual NeoForge `LivingDamageEvent.Post` value; all 10 observations per Stage were identical within the validator tolerance.

| Stage | Coefficient | Expected multiplier | Pre-defense damage | Final event damage |
|---|---:|---:|---:|---:|
| Native | 0% | 1.00 | 1.00 | 1.00 |
| S0 | 5% | 1.05 | 1.05 | 1.05 |
| S1 | 10% | 1.10 | 1.10 | 1.10 |
| S2 | 15% | 1.15 | 1.15 | 1.15 |
| S3 | 20% | 1.20 | 1.20 | 1.20 |
| S4 | 25% | 1.25 | 1.25 | 1.25 |
| S5 | 30% | 1.30 | 1.30 | 1.30 |
| S6 | 35% | 1.35 | 1.35 | 1.35 |
| S7 | 40% | 1.40 | 1.40 | 1.40 |

The raw float values are retained in the JSONL (for example, S7 is `1.399999976158142`). HP-before/after is also retained; its displayed delta has normal float quantization at the deliberately high target HP. The incoming and post-damage event values are the authoritative damage measurements.

All 90 rows confirmed:

- one core, one projectile, and one Earth Elemental event per release;
- unchanged Slotting capacity and core count;
- no cancellation;
- no Earth or Spiritual Resistance/Nullification;
- no L2 attachment or L2 bypass;
- no Apotheosis contribution;
- no Royal Arrow, Mark, or base physical damage contribution.

## Installed core-path sanity check

Artifact inspection found five legal single-core combinations in the installed Tensura version. All use `SlottingHelper.onRelease`, a native projectile coefficient of 1.0, a `TensuraFlyingProjectile`, and the common `TensuraProjectile.dealDamage` path. Their projectile utility details differ and are not Stage-scaled.

| Core | Projectile | Damage source |
|---|---|---|
| `tensura:element_core_earth` | `tensura:stone_shot` | `tensura:earth_elemental` |
| `tensura:element_core_fire` | `tensura:fire_bolt` | `tensura:fire_elemental` |
| `tensura:element_core_space` | `tensura:space_cut_projectile` | `tensura:space_elemental` |
| `tensura:element_core_water` | `tensura:water_ball` | `tensura:water_elemental` |
| `tensura:element_core_wind` | `tensura:wind_sphere` | `tensura:wind_elemental` |

This establishes that the eligible projectile damage coefficient is on a common native path. It does not treat the elements' speed, knockback, burn, gravity, or other utility properties as interchangeable.

## Scope and cleanup

This was a temporary runtime fixture only. It changed no production Stage behavior, Curve C values, Resistance/Nullification behavior, L2 behavior, Slotting capacity, Royal Bow/Royal Arrow base damage, projectile velocity, or accepted Phase 5F evidence. The temporary Java listeners and run property were removed after evidence extraction; only this report, the validated JSONL, and its extractor/validator remain.
