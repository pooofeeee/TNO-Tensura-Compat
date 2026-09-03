# Phase 6 post-completion endgame-viability research

## Status

Research and design recommendation only. Phase 6 remains complete and
unchanged. No permanent combat solution, Curve C change, Stage threshold
change, matching-Resistance change, L2 change, native Tensura change, base
damage change, or Apotheosis dependency was implemented.

The complete protocol, exact S0-S7 arrays, and machine-readable artifacts are
in [`benchmarks/phase6-endgame-viability/README.md`](benchmarks/phase6-endgame-viability/README.md).

## 1. Exact TNO-only results at Lv300, Lv600, Lv800, and Lv1000

The controlled target was `tensura:orc_disaster`, chosen from the accepted
Phase 5F set because it admits the four native Royal Bow paths that can execute
on a single target without matching Tensura Resistance or Nullification. Each
cell below is S0 -> S7 over the same ten-release, 200-tick window and exact
legal profile. Full S0-S7 values and every per-hit layer are in the artifacts.

| Family and final metric | Lv300 | Lv600 | Lv800 | Lv1000 |
|---|---:|---:|---:|---:|
| Magic Weapon HP/SHP DPS | 0.000000 -> 3.563867 | 0.705381 -> 0.767738 | 0.684772 -> 0.778633 | 0.699398 -> 0.806312 |
| Holy Weapon HP/SHP DPS | 0.000000 -> 3.563867 | 0.714024 -> 0.767738 | 0.700857 -> 0.767738 | 0.684772 -> 0.767738 |
| Soul Eater family result | 0 -> 0 | 0 -> 0 | 0 -> 0 | 0 -> 0 |
| Elemental / Slotting family result | 0 -> 0 | 0 -> 0 | 0 -> 0 | 0 -> 0 |
| Energy Steal resource impact/s | 16509.669536 -> 2307.096348 | 3210.493578 -> 4280.658104 | 4047.362460 -> 5396.483279 | 5180.162284 -> 6906.883046 |
| Severance HP/SHP DPS | 1.684499 -> 0.192537 | 0.168450 -> 0.188114 | 0.168450 -> 0.188114 | 0.168450 -> 0.188114 |

The target's combined maximum HP plus Spiritual Health was 37,000, 61,300,
77,500, and 93,700 at the four levels. Thus the approximately 0.77-0.81 S7
Magic/Holy DPS at Lv800-Lv1000 is measurable but functionally negligible: ten
seconds removed only about 0.010% of Lv800 resources and 0.008% of Lv1000
resources. This is not a difficult-but-fightable damage path.

All 320 Magic and 320 Holy native events existed and reached their post-damage
callback. The S7 eligible amount entering L2 was normally 11.2. At Lv1000 the
legal profile changed each ten-hit family sequence to 3.485427, 1.742713,
0.871357, 0.435678, 0.217839, 0.108920, 0.054460, 0.027230, 0.013615, and
0.006807. Curve C is working; its result is overwhelmed downstream.

Soul Eater emitted no native `tensura:soul_scatter` event in any of 320 rows.
Earth Slotting created and production-scaled the native
`tensura:stone_shot`, but no `tensura:earth_elemental` damage event existed in
any of 320 rows. Multiplying either family cannot change its zero result.

Energy Steal's native operation existed in 51 of 320 rows. Every admitted
operation used the exact production-scaled 1.05%-1.40% current Magicule/Aura
argument and transferred the same amount to the attacker. The other 269 rows
failed their prerequisite physical hit. At S7 only one of ten events executed
at Lv800 and one of ten at Lv1000 in this capture.

Severance's native +3 contribution existed on all 320 physical sources, but
only 58 shots stored a wound. Its combined Lv1000 S7 physical input was about
20-21 before L2; only two of ten hits stored a wound, for a total wound delta
of 2.336914 and 0.188114 final HP/SHP DPS.

## 2. Families that are already healthy

No HP/SHP damage family is fully healthy against the intended strongest-legal
Lv800-Lv1000 profile.

- Energy Steal is healthy at its own native operation: when admitted, the
  percentage, transfer, and Stage progression are exact and its resource
  impact is meaningful. It is only conditionally usable because 80%-90% of
  high-level physical prerequisites failed in this capture.
- Magic Weapon and Holy Weapon are healthy through native event creation,
  Phase 6 potency, and Tensura admission, but not in final endgame outcome.
- Severance is healthy through native contribution construction and single
  source preservation, but not in final endgame outcome or wound reliability.
- Soul Eater and Elemental / Slotting are not healthy on this Royal Bow path;
  their required native damage events are absent.

## 3. Families genuinely suppressed by L2

Magic Weapon and Holy Weapon are the clearest true L2 wall. Across each
family, 192 rows were classified `L2_MITIGATION`; the high-level event exists,
has no matching Tensura defense, enters L2 nonzero, and then decays to a
near-zero repeated-hit result.

Severance is also genuinely L2-suppressed. Of 320 configured native
contributions, 316 rows were classified `L2_MITIGATION`; only 58 wounds were
stored, and only four rows exceeded the near-zero threshold.

Energy Steal does not itself enter the L2 damage pipeline. Its 269
`PREREQUISITE_HIT_FAILED` rows are an indirect L2 wall: the combined
Tank/Dementor/Adaptive physical pipeline prevents the prerequisite Royal Arrow
hit from reaching the native drain operation. TNO correctly does not invent a
drain after a rejected hit.

There was no legal Arena, Repelling, or Teleport in these profiles. The captures
therefore contain no `L2_ADMISSION_VETO` or `L2_PROJECTILE_REJECTION`, and no
unexpected L2 bypass.

## 4. Tensura and native-event failures

Soul Eater and Elemental / Slotting are native-path compatibility findings, not
L2 or Stage failures. Both have 320 `NATIVE_EVENT_ABSENT` rows. They require a
separate investigation of native Royal Bow/Royal Arrow eligibility; an endgame
effectiveness multiplier must not fabricate their missing events.

The controlled Orc target had no matching Magic, Holy, Soul, Earth, or
Spiritual Resistance/Nullification. No current zero is therefore attributed to
`TENSURA_RESISTANCE` or `TENSURA_NULLIFICATION`. The accepted Phase 6 rules
remain authoritative: matching Resistance uses its existing S5-S7 recovery,
and matching Nullification remains absolute.

Fourteen Lv300 rows in each of Magic and Holy are
`OTHER_VERIFIED_REASON`: the final family callback was positive, but the boss
showed no persistent HP/SHP loss during the observed hit interval. This is kept
as a target/runtime observation and is not relabeled as an L2 or Tensura
defense without evidence.

## 5. Exact L2 traits creating the endgame wall

- `l2hostility:dementor` rank 1 compresses both the physical source and the
  Tensura Magic/Holy damage types. At Lv1000 S7 it reduces an ordinary 11.2
  family input to about 3.485427 before the repeated-hit decay.
- `l2hostility:adaptive` rank 3 at Lv600 and rank 5 at Lv800-Lv1000 is the
  dominant sustained wall. It is source-keyed and halves successive Magic,
  Holy, and arrow-family results into the verified geometric sequence.
- `l2hostility:tank` rank 5 supplies the 46 armor / 20 toughness physical wall.
  It directly suppresses Severance's one combined physical source and the
  prerequisite that Energy Steal legitimately requires.
- `l2hostility:regenerate` ranks 2/4/5 preserve boss sustain. It was not the
  cause of the per-event zero classifications, but any solution must leave its
  recovery identity intact.
- `l2hostility:dispell` rank 2 appears only at Lv1000. It did not transform the
  installed Tensura damage types in this path and is not the measured wall.
- Drain and Wither are offensive traits and did not create the measured
  defensive collapse.

## 6. Is target-level-aware endgame effectiveness needed?

Yes, but only as a family-scoped interaction for an already-admitted native
TNO mechanic. A global S7 increase is neither necessary nor safe. Curve C
correctly turns 8.0 into 11.2, yet Adaptive/Dementor reduce the final ten-hit
sum to about 6.96 at Lv800-Lv1000. Raising Curve C globally would buff every
ordinary target and still feed the same geometric reducer.

The system cannot solve every family. It is applicable to admitted Magic/Holy
and, with stricter proportional attribution, Severance. It must not manufacture
Soul/Elemental events or an Energy Steal operation whose prerequisite failed.

## 7. Smallest safe architecture

Keep potency and endgame effectiveness separate:

1. `L2TargetLevelSource` is an optional, fail-closed adapter. The installed
   L2Core API exposes public
   `LHMiscs.MOB.type().getExisting(entity) -> Optional<MobTraitCap>` plus public
   `MobTraitCap.isInitialized()` and `MobTraitCap.getLevel()`. Production should
   use that non-creating accessor, then read the existing authoritative level.
   It stores no level, creates no TNO level component, and grants nothing if
   the mod, attachment, initialization, or read is unavailable.
2. `EndgameEffectivenessPolicy` is a pure decision over current production
   Stage, `ScalableFamily`, authoritative target L2 level, and the existing
   eligible-event context. It owns no damage and cannot create an event.
3. Extend the existing transient eligible-contribution context with that
   decision. The context remains scoped to the exact native invocation; it is
   not put on Royal Arrow, ItemStack NBT, or a persistent target capability.
4. Add a narrow L2 reduction bridge at the reducers that evidence identifies.
   It must negotiate the reduction while it happens, not restore arbitrary
   damage afterward. For Magic/Holy, the bridge may temper only the eligible
   component's Dementor/Adaptive reduction while leaving both traits active.
5. Severance needs proportional single-source attribution through
   Tank/Dementor/Adaptive. Only the production-scaled portion of native +3 may
   receive the negotiated treatment; Royal Arrow base damage remains fully
   subject to the original physical pipeline. If this cannot be proven without
   splitting or post-restoring the source, Severance must remain unresolved.
6. Energy Steal keeps its native prerequisite. Soul Eater and Elemental route
   to separate native-eligibility work. Nullification, Arena, Repelling,
   Teleport, Reflect, Regenerate, source identity, and normal L2 admission are
   never bypassed.

The required order is:

`native event -> Phase 6 potency -> Tensura defense/nullification -> eligible target-relative decision -> L2 trait reduction -> native final effect`

This is deliberately not a generic damage multiplier, armor-pierce statistic,
post-L2 floor, second `DamageSource`, or HP subtraction.

## 8. Supported thresholds and unsupported percentages

The evidence supports a conservative eligibility boundary, not a strength
percentage:

- target must have an initialized authoritative L2 attachment at level 800 or
  higher; and
- weapon must resolve production S5, S6, or S7 for the exact active scalable
  family.

Lv800 is where the accepted profile reaches Adaptive 5 and matches the stated
pack endgame target. Lv600 Adaptive 3 is strongly suppressive, but the design
explicitly permits very-high-level bosses to suppress low/mid progression and
does not require Lv600 to receive the endgame layer. S5 is the existing start
of high-Stage defense interaction; it provides a natural ramp point without
changing Curve C.

No mitigation-resistance percentage, result floor, or revised coefficient is
supported by this one-target dataset. Those values must be selected only after
candidate-policy runs across the full intended Lv800-Lv1000 boss set. The
research therefore proposes no permanent percentage.

## 9. Lower-level safety

The current research changed no production behavior. On the existing Phase 6
rules, even the Lv300 strongest legal control measured only 3.563867 S7
Magic/Holy DPS against 37,000 combined HP/SHP, while Severance measured
0.192537 DPS. Nothing in this capture is overpowered.

For a future implementation, the hard no-op contract is the safety mechanism:
no L2 attachment, uninitialized L2, L2 level below 800, Stage S0-S4,
unclassified gear, inactive family, absent native event, failed prerequisite,
or matching Nullification must produce byte-for-byte Phase 6 behavior. That
keeps normal and lower-level enemies outside the new layer instead of trying to
counterbalance a global buff.

## 10. Acceptance tests for permanent implementation

1. Verify the optional level adapter returns the exact live L2 level at
   300/600/800/1000, returns inactive without L2, and never creates duplicate
   level state.
2. Prove exact Phase 6 parity for no-L2 targets, Lv300, Lv600, S0-S4, inactive
   families, unclassified gear, and a no-Engraving control.
3. Re-run production S0-S7 at Lv800/Lv1000 for Magic and Holy. S5-S7 must be
   increasingly usable, S7 must remain below its unmitigated input, and
   Adaptive must still reduce repeated same-source hits instead of disappearing.
4. Compare otherwise identical profiles with/without Dementor, Adaptive, Tank,
   and Regenerate. Every trait must retain a measurable disadvantage and its
   native identity.
5. Keep matching Resistance on its exact existing S0-S7 recovery schedule and
   prove matching Nullification remains zero at every Stage and target level.
6. Prove Arena/Repelling/Teleport rejection remains authoritative and creates
   no fallback result.
7. Prove Soul Eater and Elemental remain zero when their native event is absent;
   no endgame layer may synthesize an event.
8. Prove Energy Steal remains absent after a failed physical prerequisite and
   emits no `DamageSource`. When admitted, target drain must still equal
   attacker gain and the native cooldown must remain active.
9. For Severance, prove one physical source, unchanged source tags, unchanged
   base-arrow contribution, proportional treatment of only native +3 Stage
   delta, and no wound after a rejected/zero hit.
10. Re-run the legal Lv800/Lv1000 intended boss matrix with ten-shot and longer
    sustained windows. Require zero unexpected L2/Tensura bypass, no duplicate
    source/event, no APO contribution, and review an explicit difficult-but-
    fightable outcome band before locking any percentage.
11. Run `gradlew.bat clean build`, dev-server startup with the full compatibility
    stack, and a clean-clone build without optional Royal Variations/L2 local
    artifacts.

## Recommendation

Approve the architecture boundary, not a balance value. A target-level-aware,
family-scoped L2 reduction negotiation is justified for admitted endgame TNO
effects. Do not change Curve C; do not add a global damage buff; do not
post-restore damage; and do not use the mechanism to hide native-event defects.
The next reviewed task should prototype candidate policies only for Magic/Holy
at S5-S7 and Lv800-Lv1000, measure them across the intended boss set, and then
decide whether the same transient attribution model can safely support
Severance.
