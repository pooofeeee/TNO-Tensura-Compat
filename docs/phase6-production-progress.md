# Phase 6 production progress

- Baseline SHA: `50d599f374d94deafa46f5cd10b09d548b369461`
- Current branch: `phase-6-production-stage-framework`
- Latest completed checkpoint: 6E — rounding-aware Severance
- Current checkpoint: 6F — Royal Bow activation and targeted production acceptance
- Latest known good commit SHA: `90ae0d9b0555ae589c2ea67de352ced83d3a9f97` (resolved-blocker remote checkpoint)

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
- Royal Bow is explicitly mapped to TNO `GearStageClass.RARE`; Apotheosis and native Tensura rarity names are not consulted.
- Royal Bow native GearExistence now permits the locked S7 threshold at 2,490,000 EP while retaining the existing temporary 1,000 initial EP and 0.01 growth rate.
- A narrow wrapper around Tensura's equipment-change `initiateGearExistence` call recognizes successful Royal Bow conversion immediately after the native operation and performs the authorized first applicable Engraving roll once, without relying on listener registration order.
- The roll claims a persistent `minecraft:custom_data` marker before selection, uses the exact Common 35% / Uncommon 35% / Rare 20% / Epic 10% distribution, filters Tensura's configured pool through native `canEnchant`, and applies the result through Tensura's `EngraveEvent` path. Later equipment/login/EP/Stage/shot checks cannot repeat it.

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
- Exact 100-value first-roll distribution and Rare Stage boundary tests pass for the initial 6F activation unit.

## Remaining tests

- Dev-runtime conversion/marker/roll verification and the full targeted 6F acceptance set remain.
- Magic/Holy, matching Resistance/Nullification, strongest-legal L2, and accepted Ancient coexistence spot checks remain to be captured through the now-active Royal Bow Rare mapping.

## Unresolved findings

- None. The prior Royal Bow class and first-roll trigger decisions are now explicitly resolved; runtime acceptance is unfinished work, not a design blocker.

## Exact next action

Run dev-server verification of native Royal Bow conversion, the persistent one-time marker and native eligible roll, then execute the targeted 6F combat acceptance set without rerunning the Phase 5F matrix.
