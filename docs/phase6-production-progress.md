# Phase 6 production progress

- Baseline SHA: `50d599f374d94deafa46f5cd10b09d548b369461`
- Current branch: `phase-6-production-stage-framework`
- Latest completed checkpoint: 6E — rounding-aware Severance
- Current checkpoint: 6F — Royal Bow end-to-end integration, runtime regression, and Phase 6 closure
- Latest known good commit SHA: `95783e6257d6309043ff023ce3a6f5ec3ed77200` (6D remote checkpoint)

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
- Severance is intercepted inside `AbstractArrow.onHitEntity`: Tensura's installed `+3` is first applied by native `EnchantmentHelper.modifyDamage`, then TNO adds only `+3 * Curve C bonus` before projectile velocity and the one native ceiling.
- A classified Severance arrow whose positive eligible pre-round delta lands in the same native integer bucket receives the next integer result. This is scoped to that classified weapon and enchantment; it does not alter global projectile rounding, base/APO physical damage, velocity, crit logic, source identity, L2 order, or wound order.
- The existing local integer continues through the single `minecraft:arrow` hit and Tensura's native after-damage/wound path. Rejected or zero physical hits still cannot create a wound.

## Completed tests

- Common boundary/cap, every Rare threshold, exact Curve C, no-Engraving zero-gain, and family-isolation unit tests pass.
- All six family isolation cases pass.
- A dev `runServer` reached `Done` and applied both 6B mixins without injection errors.
- Energy Steal's production mixin applied without injection errors during dev-server startup.
- Elemental Native/S0-S7 multiplier and Energy 1.00%-to-1.40% deterministic tests pass.
- Resistance recovery schedule, native HP gate, and loss-only interpolation tests pass.
- A dev `runServer` reached `Done` with the 6D `TensuraProjectileMixin` and all loaded family mixins applied without injection errors.
- Low-magnitude S0 collapse, naturally distinct ceiling, eligible-only +3 scaling, and APO/base isolation tests pass.
- A dev `runServer` reached `Done` with Royal Variations, Tensura's `MixinAbstractArrow`, and TNO's `AbstractArrowMixin` all applied without injection errors.
- `gradlew.bat clean build` passes at Checkpoints 6A-6E.

## Remaining tests

- Final targeted runtime acceptance and Phase 6 closure remain for 6F.
- Positive-control Resistance/Nullification combat values remain blocked until a production gear classification is authorized; the generic native boundary and deterministic invariants are complete.
- Magic/Holy positive-control damage values remain blocked until a production gear classification is authorized.

## Unresolved findings

- The accepted repository evidence defines Common and Rare thresholds but does not assign Royal Bow a production TNO Common/Rare class. Phase 5's S0-S7 Royal Bow fixture is benchmark coverage, not an explicit classification decision.
- The exact authorized production trigger for Royal Bow's first applicable Engraving roll is not established.

## Exact next action

Resolve the two recorded Royal Bow production ambiguities (TNO Common/Rare classification and the first-applicable-Engraving trigger) before enabling the generic framework for Royal Bow and running 6F acceptance. Do not invent either rule.
