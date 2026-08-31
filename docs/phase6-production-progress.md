# Phase 6 production progress

- Baseline SHA: `50d599f374d94deafa46f5cd10b09d548b369461`
- Current branch: `phase-6-production-stage-framework`
- Latest completed checkpoint: 6D — matching Resistance recovery and absolute Nullification
- Current checkpoint: 6E — rounding-aware Severance
- Latest known good commit SHA: `f4379a58cc95cb9a8fe307fc49162b4cdf2cad2a` (6C remote checkpoint)

## Completed implementation areas

- Generic TNO `Stage`, `GearStageClass`, `StageResolver`, `StageCurve`, and closed `ScalableFamily` model.
- Common S0-S3 and locked Rare S0-S7 thresholds.
- Direct authoritative read from Tensura 2.0.1.1 `TensuraDataComponents.EP`; no TNO EP counter or Stage cache.
- Curve C family isolation and zero-gain behavior when no scalable native family is active.
- Narrow production wrappers around Tensura's existing Magic/Holy additional-damage and Soul spiritual-damage calls.
- Damage source holders, native event count, and Soul event availability are preserved; the wrappers do not manufacture events.
- Explicit external-gear classification table defaults to no classification, so unclassified gear receives zero TNO combat gain.
- Slotting scales only Tensura's computed elemental projectile damage argument; speed, utility, core capacity/count/tier, and physical arrows are untouched.
- Energy Steal scales only Tensura's admitted EP percentage drain argument; it adds no operation and no `DamageSource`.
- Matching Resistance recovery uses the locked S0-S4 0%, S5 25%, S6 50%, S7 100% schedule and `post + penetration * (pre - post)`.
- Recovery is applied at the native damage boundary before Tensura Resistance and downstream L2. It uses Tensura bypass level 1 only to prevent that already-modelled matching Resistance layer from applying twice.
- Matching Nullification is checked first and remains absolute. Its presence prevents both recovery and the level-1 bypass; no alternate source or fallback damage is created.
- Slotting projectiles carry only an attack-time Stage snapshot derived from native Gear EP so delayed native projectile hits use the same 6D rule. No independent EP or persistent gear Stage counter exists.

## Completed tests

- Common boundary/cap, every Rare threshold, exact Curve C, no-Engraving zero-gain, and family-isolation unit tests pass.
- All six family isolation cases pass.
- A dev `runServer` reached `Done` and applied both 6B mixins without injection errors.
- Energy Steal's production mixin applied without injection errors during dev-server startup.
- Elemental Native/S0-S7 multiplier and Energy 1.00%-to-1.40% deterministic tests pass.
- Resistance recovery schedule, native HP gate, and loss-only interpolation tests pass.
- A dev `runServer` reached `Done` with the 6D `TensuraProjectileMixin` and all loaded family mixins applied without injection errors.
- `gradlew.bat clean build` passes at Checkpoints 6A-6D.

## Remaining tests

- Severance and final targeted runtime acceptance remain for 6E-6F.
- Positive-control Resistance/Nullification combat values remain blocked until a production gear classification is authorized; the generic native boundary and deterministic invariants are complete.
- Magic/Holy positive-control damage values remain blocked until a production gear classification is authorized.

## Unresolved findings

- The accepted repository evidence defines Common and Rare thresholds but does not assign Royal Bow a production TNO Common/Rare class. Phase 5's S0-S7 Royal Bow fixture is benchmark coverage, not an explicit classification decision.
- The exact authorized production trigger for Royal Bow's first applicable Engraving roll is not established.

## Exact next action

Trace Royal Arrow's native Severance +3 through velocity multiplication, native rounding, the one physical `minecraft:arrow` event, L2 processing, and wound storage before implementing the rounding-aware eligible delta.
