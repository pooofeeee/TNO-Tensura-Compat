# Phase 6 Magic/Holy endgame production implementation

## Status

The calibrated Magic/Holy endgame-effectiveness architecture is implemented as permanent production behavior on `phase-6-endgame-magic-holy-production`. It is limited to the existing native Magic Weapon and Holy Weapon events at S5-S7. It does not change Curve C, Stage thresholds, native Gear EP, matching Tensura defenses, Royal Bow/Arrow base damage, Apotheosis behavior, or any other scalable family.

## 1. Production architecture

The production layer has six narrow responsibilities:

- `MagicHolyEndgamePolicy` owns the immutable Stage-to-Q/RD/RA table and family admission rule.
- `L2HealthScaling` reproduces L2's live linear or exponential generic-health formula without consulting realized HP, SHP, Tank, or Regenerate.
- `L2HostilityTargetAdapter` obtains an initialized existing L2 attachment through reflection and reads only the current level, live health configuration, entity health scale, and relevant trait presence.
- `MagicHolyEndgameContext` holds one transient synchronous native-event scope. It stores no ItemStack, arrow, entity attachment, player, world, or serialized state.
- `MagicHolyEndgameL2Bridge` registers an optional reflected listener into L2's damage-modifier pipeline.
- `AdditionalDamageEntityMixin` opens the production scope only around the already-admitted native Magic/Holy call, after existing Phase 6 processing.

No production path depends on `tno.phase6.calibration`, a benchmark runner, debug parameter injection, or calibration trace objects.

## 2. Locked production policy

| Stage | Q (generic H) | RD (Dementor) | RA (Adaptive) |
|---|---:|---:|---:|
| S0 | 0.00 | 0.000 | 0.000 |
| S1 | 0.00 | 0.000 | 0.000 |
| S2 | 0.00 | 0.000 | 0.000 |
| S3 | 0.00 | 0.000 | 0.000 |
| S4 | 0.00 | 0.000 | 0.000 |
| S5 | 0.50 | 0.500 | 0.500 |
| S6 | 0.75 | 0.625 | 0.625 |
| S7 | 1.00 | 0.750 | 0.750 |

Stage is the only activation gate. There is no L2 level threshold and no Lv800 cliff.

## 3. Generic-health formula and configuration

For L2's live non-exponential configuration, the nominal generic-health multiplier is:

`H = 1 + level * healthFactor * entityHealthScale`

If L2 enables exponential health, the implementation uses its native formula:

`H = 1 + ((1 + healthFactor)^level - 1) * entityHealthScale`

The production normalization is `N = 1 + Q * (H - 1)`. The adapter reads `healthFactor`, `exponentialHealth`, current L2 level, and the entity's `healthScale` from the installed runtime. It does not hardcode `0.03` and does not derive H from final max HP, current HP, SHP, Tank, Regenerate, or other durability state.

## 4. Exact processing placement

The order is:

1. existing native Magic/Holy event;
2. Phase 6 Curve C;
3. matching Tensura Resistance recovery or authoritative Nullification;
4. transient production context;
5. generic-H normalization at L2 `PRE_NONLINEAR`, priority 7435;
6. native Dementor, followed by RD at `PRE_NONLINEAR`, priority 7437;
7. native Adaptive, followed by RA at `POST_MULTIPLICATIVE`, priority 7437;
8. the remainder of the native L2 pipeline and normal final damage.

The reflected attack listener is registered at priority 4501. The feature never creates an event, restores final post-L2 damage, or emits a second source.

## 5. Fail-closed contract

The feature produces no gain when L2 is absent, the attachment does not already exist, the attachment is uninitialized, a required live read fails, gear is unclassified, Stage is unresolved or S0-S4, the family is not Magic/Holy, the native event is absent, the target is invalid, matching Nullification is active, or the exact source identity does not match. Attachment access uses `getExisting`, never `getOrCreate`; attacking cannot create L2 state.

Matching Nullification is checked before opening a production context. Its admission rule is explicitly tested for both families. The selected runtime targets did not naturally carry matching Magic/Holy Nullification, so the P5 evidence does not misrepresent a fabricated Nullification case as runtime evidence.

## 6. Optional L2 behavior

L2 Hostility remains optional. Production classes contain no compile-time L2 types; class, listener, attachment, trait, and config access is reflected only after `ModList` reports `l2hostility` loaded. Registration or event-level reflection failure is caught and preserves ordinary Phase 6 behavior.

An L2-absent development-server check reached `Done` with `l2hostility` explicitly reported `mod_absent`. No released-mod dependency on L2, Royal Variations, Curios, or the local benchmark stack was added.

## 7. Source identity guarantees

Only these native identities are eligible:

- Magic Weapon: holder `tensura:magic`, message ID `tensura.magic`.
- Holy Weapon: holder `tensura:holy_damage`, message ID `tensura.holy_damage`.

The original holder, message ID, and tags are preserved. Neither source is globally retagged as NeoForge magic, so Dispell classification does not change. The physical Royal Arrow remains `minecraft:arrow` and is outside Q/RD/RA.

## 8. Dementor semantics

If and only if the actual existing target has Dementor, the bridge observes the value entering native Dementor (`x`) and its native output (`y`), then applies:

`y' = y + RD * (x - y)`

Native Dementor still executes. RD never predicts trait presence, suppresses the callback, exceeds the pre-Dementor value, or restores loss from later L2 mechanics. All eight paired S7 runtime controls showed the accepted Dementor profile below the same legal profile with Dementor removed.

## 9. Adaptive semantics

Native Adaptive owns its source key, rank, capacity, count, memory, and factor `A`. The production modifier applies only:

`A' = A + RA * (1 - A)`

TNO stores no adaptation state and performs no reset. Focused repeated-hit tests preserve the native count-1-through-10 sequence; under the accepted factor sequence, S7's tenth negotiated factor is `0.75048828125`, still below 1. All six paired S7 runtime controls where Adaptive exists showed the accepted profile below the same legal profile with Adaptive removed.

## 10. Non-interaction guarantees

Soul Eater, Elemental/Slotting, Energy Steal, and Severance are rejected before an endgame context or additional matching-defense read. Their established Phase 6 behavior and blockers are unchanged. Q/RD/RA do not scale base Royal Bow damage, Royal Arrow damage, physical arrow damage, APO affixes/gems/crit/projectiles, generic enchantments, attributes, Mark, projectile count, piercing, Slotting capacity, core tier/count, Tank, Regenerate, or Dispell.

The P5 runtime evidence used `APO_profile = NONE` to isolate native behavior. APO non-interaction is guaranteed by the exact native-family source scope and remains consistent with the earlier accepted APO isolation evidence; P5 does not claim a new APO benchmark.

## 11. Production runtime results

The machine-readable evidence is in [`benchmarks/phase6-endgame-magic-holy-production/`](benchmarks/phase6-endgame-magic-holy-production/README.md). It contains 86 completed cases, 860 per-hit formula-observation rows, 860 physical events, and 860 native family events:

- Magic/Orc: 39 cases and 390 hits.
- Holy/Orc: 39 cases and 390 hits.
- Magic/Luminous: 4 cases and 40 hits.
- Holy/Luminous: 4 cases and 40 hits.

All 860 final family amounts matched independently recomputed H/Q/RD/RA results. There were zero case errors, duplicate events, recursions, unexpected Tensura bypasses, and unexpected L2 bypasses. All source identities were exact; Mark remained disabled; no calibration property was active.

The 42 S0-S4 cases (420 hits) used exact zero Q/RD/RA negotiation. The eight Orc family/level trajectories were strictly S5 < S6 < S7 at Lv300, Lv600, Lv800, and Lv1000. Both Lv1000 Luminous trajectories were also strictly increasing. Matching Magic/Holy Resistance on Luminous remained present for every hit, with exact penetration of 0% at S4, 25% at S5, 50% at S6, and 100% at S7.

## 12. Unresolved blockers

This damage-side implementation does not claim full endgame viability against native Regenerate. It does not address Severance/Regenerate interaction, absent Royal Arrow Soul events, boss-dependent Elemental event availability, or Energy Steal prerequisites. Those are separate reviewed tasks; their current production behavior remains unchanged.

## 13. Phase boundary

The original Phase 7 has not started. No Phase 7 feature, balance change, research run, or compatibility workaround is included here.
