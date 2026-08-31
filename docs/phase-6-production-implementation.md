# Phase 6 production Stage implementation

## Status

Checkpoints 6A through 6F are implemented and accepted on `phase-6-production-stage-framework`. Royal Bow is explicitly TNO Rare, its first applicable Engraving roll runs once immediately after successful native Tensura Gear conversion, and the targeted production runtime acceptance is complete. Phase 6 is complete.

## Architecture and native EP

The production framework is intentionally small:

- `Stage` defines S0-S7 and the locked Curve C coefficients.
- `GearStageClass` defines the Common and Rare EP schedules and caps.
- `StageResolver` derives Stage directly from current native Tensura Gear EP.
- `NativeGearEpSource` reads Tensura 2.0.1.1 `TensuraDataComponents.EP` from the weapon.
- `GearStageClasses` is the explicit external-item classification table. Royal Bow maps directly to TNO Rare; no Apotheosis or native Tensura rarity controls this mapping.
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
- Deterministic Elemental, Energy Steal, matching Resistance schedule, native HP gate, and recovery interpolation tests pass. The matching-Nullification-first branch is implemented, its mixin loads, and its S4-S7 runtime acceptance is complete.
- Severance tests cover eligible-only +3 scaling, a low-magnitude S0 collapse, naturally distinct ceiling behavior, and large Apotheosis/base isolation.
- Development server startup reached `Done` with the relevant production mixins, Royal Variations, and Tensura's arrow mixin applied without injection errors.
- `gradlew.bat clean build` passed for the final Phase 6 tree.
- Phase 5 benchmark listeners remain behind the existing `!FMLEnvironment.production` registration guard; no Phase 6 benchmark listener or temporary runtime instrumentation was added.
- No raw runtime log, world, temporary config, generated capture, or third-party local JAR is tracked by the Phase 6 commits.

The accepted Phase 5F and Phase 6 Elemental pre-flight evidence was not modified.

## Royal Bow end-to-end and first Engraving behavior

The production chain is Royal Bow -> native Tensura Gear -> native Gear EP -> TNO Rare Stage -> native eligible Engraving -> eligible scaled component -> Tensura defenses -> L2. Royal Arrow has no separate EP or Stage.

TNO narrowly wraps the `initiateGearExistence` call inside Tensura's native equipment-change listener. It invokes the native operation first, then requires the Royal Bow ID, its explicit Rare mapping, initialized native EP/EP-gain components, and native maximum EP at least equal to the S7 threshold. This guarantees conversion-before-roll ordering without depending on listener registration order. The GearExistence record now uses max EP 2,490,000 so every authorized Rare Stage is naturally reachable; its existing temporary 1,000 initial EP and 0.01 growth rate are unchanged.

On the first successful conversion, TNO atomically claims a persistent item marker before selecting the first roll. The distribution is Common 35%, Uncommon 35%, Rare 20%, and Epic 10%. Only Tensura's configured pool for the selected rarity is considered, each candidate must pass native `canEnchant`, and a chosen candidate is applied through `EngravingHelper.increaseEngraving` so the native `EngraveEvent` remains authoritative. An empty legal pool or a native event cancellation is a valid no-Engraving outcome. The native curse chance/path is preserved. The marker is copied and serialized with the ItemStack, so equipment changes, login, load, Stage/EP changes, shots, and reintegration checks cannot perform the first roll again. Later Engraving behavior remains native/previously established.

## Checkpoint 6F targeted production acceptance

The accepted set used 29 targeted cases and 89 per-hit rows. It used real native Royal Bow EP components and the production mixins; no Phase 5 Stage fixture mutation was active. The temporary observer was removed after capture and no raw runtime log or generated acceptance capture is tracked.

- Fresh equipment conversion produced `royalvariations:royal_bow` with native EP 1,000, max EP 2,490,000, growth 0.01, and resolved Rare S0. The observed first roll selected Common and legally applied `tensura:swift`; this is an observed stochastic result, not a guaranteed starting Engraving. The persistent marker was present, and repeating the equipment update left the enchantment set unchanged.
- A no-scalable-Engraving S0/S7 control emitted zero scalable-family events and zero eligible TNO amount. Its physical arrow input remained 8.0 at both stages.
- Magic Weapon resolved real EP through all Rare stages. A stable native amount of 8.0 became 8.4, 8.8, 9.2, 9.6, 10.0, 10.4, 10.8, and 11.2 at S0-S7. The physical arrow input remained 8.0 throughout.
- Holy Weapon reproduced the positive control at S0/S7: native 8.0 became 8.4/11.2 while physical input remained 8.0.
- Soul Eater emitted no native `tensura:soul_scatter` event in the targeted Royal Arrow control. Native and staged Soul amounts both remained zero; the production framework did not fabricate an event.
- Earth Slotting scaled its native projectile damage from 1.0 to 1.05 at S0 and 1.40 at S7, retained the native `tensura:stone_shot` owner/entity path, and did not create or scale a physical Royal Arrow.
- Energy Steal emitted exactly three admitted native drain events per case. Its native 1.00% argument became 1.05% at S0 and 1.40% at S7, with no added damage source.
- Low-magnitude Severance reproduced the rounding case. At S0, native/staged pre-round values were about 16.245/16.696 and both ordinary ceilings were 17; the production guard preserved the positive eligible delta as combined physical input 18. At S7 the staged pre-round value was about 19.750 and the one combined physical input was 20. No second Severance source appeared.
- A Lv300 Luminous matching-Magic-Resistance control stayed canceled at S4 with bypass level 0. S5 admitted 25% of the 10.4 pre-resistance staged amount (2.6), S6 admitted 50% of 10.8 (5.4), and S7 admitted 100% of 11.2; S5-S7 used native bypass level 1 only for the already-modelled matching Resistance layer.
- A Lv300 Luminous Earth Nullification control remained absolute at S4-S7. The production Slotting values were 1.25, 1.30, 1.35, and 1.40, but every eligible damage path remained zero and the Resistance bypass level stayed 0.
- The accepted `ANCIENT_SINGLE_PROSPEROUS_SPECTRAL` Royal Bow was checked at S7 against the accepted strongest-legal Lv1000 Luminous profile: Adaptive 5, Dementor 1, Dispell 3, Killer Aura 1, Reflect 2, Regenerate 5, Soul Burner 2, and Tank 5. Runtime inspection revalidated Ancient rarity, the locked affixes, five Perfect gems, Supremacy levels, and the compatible enchantment package. Five releases produced ten real APO projectiles, ten physical events, and ten Magic events. Downstream L2 reduced the events without any TNO restoration or bypass.
- Across the accepted set: unexpected duplicate events 0, unexpected L2 bypasses 0, unexpected Tensura bypasses 0, base/APO physical Stage violations 0, Mark Stage violations 0, and detected double scaling 0.

The runtime run also exposed and resolved one compatibility defect: reflective invocation on Architectury's non-public registry-supplier implementation failed at S5-S7. Production now reads the same Tensura registry entry through its public `Supplier` interface. The rerun completed S5-S7 and the matching-Resistance control without errors.

## Remaining observations

- High Magic/Holy combined results, absent Royal Arrow Soul events, boss-dependent Elemental availability, Orc-only Energy Steal/Severance observations, and strongest-legal L2 suppression remain accepted non-bug research observations.
- No authorized balance constants, native Tensura mechanics, L2 mechanics, Apotheosis mechanics, Royal Bow/Arrow base damage, Mark behavior, or accepted research evidence were changed.
- Phase 6 is `COMPLETE`. Phase 7 has not started.
