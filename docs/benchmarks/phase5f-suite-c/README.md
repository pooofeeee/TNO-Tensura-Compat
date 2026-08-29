# Phase 5F Suite C — Apotheosis + TNO

Status: complete; official direct and strongest-legal endgame matrices accepted.

Suite C reuses the accepted Suite B boss/level, Native + S0-S7, ten-release, and 200-tick fixture while equipping the accepted `ANCIENT_SINGLE_PROSPEROUS_SPECTRAL` Apotheosis profile. It is development-only and reports `production_combat_mutated=false`.

## Legal combined item

The runtime compatibility API proves that every tested TNO family Engraving is incompatible with `tensura:barrier_piercing`. Suite C therefore preserves the complete accepted Ancient rarity, ten effective-level-1.5 affixes, five Perfect gems, effective APO attributes, and all eight compatible Suite A enchantments, then replaces only `tensura:barrier_piercing` with the active family Engraving. The harness fails on an illegal pairwise enchantment set or any other APO profile drift.

## Projectile lifecycle gate

The initial controlled-collision harness called the real projectile hit callback but left the dispatched entity alive in the final collision lane. The same entity could collide again on the next tick, yielding two physical and two Magic events from one projectile. This was a benchmark-harness defect, not a production combat defect.

The corrected harness discards only the entity whose legitimate hit callback has completed. It records every spawned entity ID/UUID and every entity ID/UUID that reaches the damage event, then rejects a second physical event from the same UUID. Genuine extra projectiles remain intact and are dispatched independently.

The accepted Magic/Luminous diagnostic gate produced:

- 4/4 cases and 40 rows, zero `case_error`;
- zero duplicate-event, same-projectile-rehit, recursion, Mark, L2-bypass, or Tensura-bypass flags;
- exactly two unique spawned projectile UUIDs per release;
- the two legal entity outcomes `royalvariations:royal_arrow` and `minecraft:spectral_arrow` from the locked Spectral affix;
- exactly one physical `minecraft:arrow` event and one `tensura:magic` event per unique projectile;
- the exact Ancient profile: ten valid level-1.5 affixes, five Perfect gems, five sockets, and the accepted effective APO attributes.

Diagnostic logs are not accepted evidence and are not tracked. Official JSONL is extracted only by `scripts/extract-phase5f-suite-c.ps1`, whose strict validation rejects malformed stages/profile identity, illegal enchantments, unknown projectile types, reused projectile UUIDs, event duplication, Mark, production mutation, or L2/Tensura bypass.

Official captures may opt into vanilla server tick sprint. This removes wall-clock sleeping only: every case still advances the locked 200 server ticks, fires ten releases at the same 20-tick spacing, and observes the same tick-based cooldown, DoT, regeneration, and L2 logic. The catalog records `server_tick_sprint_enabled` so this execution detail is never implicit.

The controlled dispatcher also records pending sibling projectiles discarded after an earlier projectile from the same genuine APO multi-projectile release defeats the target. Those siblings retain their spawn entity IDs/UUIDs but are not forced through `canHitEntity` against an already-dead target and cannot contribute damage events.

For Severance, the evidence retains both the exact pre-round/native/staged Severance contribution and the actual combined physical `minecraft:arrow` amount entering L2. The Suite C validator does not equate those values: the legal APO profile changes bow base damage, and its enchantment/critical processing may further transform the combined event after the isolated Severance contribution has been calculated.

Severance aggregation is scoped to projectiles that actually emit an admitted physical arrow event. Configured/released and admitted projectile counts remain separate, so an L2/Tensura-cancelled sibling cannot contribute phantom native or staged Severance amount.

The targeted endgame mode reuses the already-accepted strongest legal Lv1000 defensive profile for every boss. It runs Native and S7 only, records the exact trait/rank set and prior legality budget, and uses pristine serialized clones across the two Stage cases. It does not synthesize new traits or relax L2 legality.

## Final accepted evidence

The closure validator is `scripts/validate-phase5f-suite-c.ps1`. It reparses all
48 accepted artifacts, rejects missing Native/S0-S7 or strongest-profile cases,
and rechecks protocol, APO identity, exact legal L2 endgame profiles, projectile
UUID ownership, DamageSource identity, Stage scope, Energy Steal cardinality,
Severance wound constraints, bypass flags, and production-mutation flags.

| Matrix | Artifacts | Cases | Rows | Case errors |
| --- | ---: | ---: | ---: | ---: |
| Direct: six families x seven bosses | 42 | 2,214 | 21,204 | 0 |
| Strongest legal Lv1000: six families x seven bosses x Native/S7 | 6 | 84 | 840 | 0 |
| **Suite C total** | **48** | **2,298** | **22,044** | **0** |

Across the complete set there are zero unexpected source duplications, zero
same-projectile re-hits, zero recursive events, zero unexpected L2 bypasses,
zero unexpected Tensura bypasses, zero Mark events, and zero production
mutations. The accepted Spectral affix produced genuine APO multi-projectile
releases; each projectile has a distinct UUID and is admitted at most once.
Those sibling events are legal upstream multiplication, not duplicated damage.

The machine-readable aggregate is `summary.json`.

## Direct family results

The averages below are arithmetic means of the fixed-window case results. They
describe these legal rolls, not a proposed balance target. Energy Steal's
resource-impact values are reported separately because its native operation
does not emit a DamageSource.

| Family | Cases | Rows | Native -> S7 | Zero cases | Runtime conclusion |
| --- | ---: | ---: | ---: | ---: | --- |
| Magic Weapon | 369 | 3,200 | 480.189045 -> 1,160.273532 DPS | 156 | Native `tensura:magic` events coexist with APO projectiles/crit; Stage applies once to the eligible native amount. |
| Holy Weapon | 369 | 3,245 | 521.705901 -> 1,084.743127 DPS | 120 | Native `tensura:holy_damage` events coexist with APO projectiles/crit; Stage applies once. |
| Soul Eater | 369 | 3,690 | 27.092741 -> 9.175172 DPS | 315 | Zero native `tensura:soul_scatter` events; positive Orc results are APO physical residue, not Soul progression. |
| Elemental / Slotting | 369 | 3,690 | 0 -> 0 DPS | 369 | No eligible Earth event survived this combined runtime path. APO does not manufacture one. |
| Energy Steal | 369 | 3,690 | 792.429557 -> 1,338.533942 resource/s | 315 | Only Orc emitted native drains; every event remained 1% x Stage and at most one drain per release. |
| Severance | 369 | 3,689 | 42.442595 -> 19.432426 DPS | 315 | Only Orc retained positive physical results; 137 rows stored wound through the single combined arrow source. |

The strongest-legal Lv1000 matrix adds 14 cases and 140 rows per family. Its
Native -> S7 averages were Magic `0.981079 -> 1.882113` DPS, Holy
`1.261482 -> 1.889448` DPS, Soul `0.189259 -> 0.194263` DPS, Elemental
`0 -> 0`, Energy `708.251984 -> 1,969.223817` resource/s, and Severance
`0.202226 -> 0.170570` DPS. These extremely defensive profiles are a stress
boundary, not the ordinary direct-matrix average.

## Suite A vs Suite B vs Suite C

Suite A isolated the accepted Apotheosis profile: 41 cases, 409 rows, zero
errors, 50.642624 average DPS, and 37 zero cases. It had no TNO family or Stage.
Suite B isolated the six native TNO families: 2,214 cases and 22,140 rows.
Suite C combines the same systems legally, replacing only the enchantment that
conflicts with the active family Engraving.

- Magic and Holy demonstrate normal independent coexistence. APO legitimately
  changes the real upstream projectile count, physical magnitude, and critical
  result. Native Tensura then emits one eligible family event per admitted
  projectile, and Stage scales that native amount exactly once. All 5,319
  positive Magic/Holy formula rows satisfy `staged = native x coefficient`.
- Soul Eater remains non-functional as a Royal Arrow Soul source in both B and
  C. APO increases residual physical damage on Orc but creates zero Soul events;
  it therefore does not accidentally scale or synthesize a TNO contribution.
- Elemental / Slotting remains event-availability limited. Its zero combined
  result is a native-runtime compatibility/balance observation, not evidence
  that APO swallowed a Stage event.
- Energy Steal remains a native post-hit resource operation. All 136 direct plus
  endgame event rows obey the one-percent formula, no row has more than one drain
  event, and no drain emits a DamageSource. There is no duplicated Energy Steal.
- Severance remains one combined physical `minecraft:arrow` event. Stage changes
  only the eligible native `+3` contribution; APO/base physical damage is never
  Stage-scaled, and no second DamageSource exists.

There is no accidental double scaling, event recursion, DamageSource
reclassification, matching-Resistance bypass, matching-Nullification bypass,
or L2 bypass. Physical remains `minecraft:arrow`; Magic remains
`tensura:magic`; Holy remains `tensura:holy_damage`; and Energy Steal remains a
non-DamageSource operation. In particular, `tensura:magic` retains its observed
`minecraft:bypasses_armor` but not `neoforge:is_magic` semantics, so Dementor
can transform it while Dispell does not.

These are integration conclusions. The large Magic/Holy combined averages,
weak or absent Soul/Elemental paths, Orc-only Energy/Severance availability,
and strongest-profile suppression are balance/runtime observations. None is a
production integration bug, so no production combat patch was made.

## Final Severance research conclusion

Suite B proved the rounding defect directly: eight surviving Orc S0 hits had a
higher staged pre-round contribution but the same native ceiled value. Suite C's
max-APO velocity/magnitude made every admitted S0-S7 contribution distinguishable
from Native: 1,920 of 1,920 staged direct rows changed the rounded contribution.
That is improved observability, not a cure. The low-magnitude Suite B result
proves that the problem is intrinsic to where the eligible Severance contribution
is rounded.

Phase 6 must resolve that rounding position explicitly. It must not invent a
second Severance DamageSource or a new curve merely to make weak L2 results look
stronger. The permanent path must retain one physical/projectile
`minecraft:arrow` event, scale only the eligible native `+3` contribution, keep
base/APO physical outside Stage scaling, preserve projectile velocity and native
L2 ordering, and forbid zeroed/cancelled physical events from storing wound.
The remaining design decision is a rounding-aware representation of the staged
eligible contribution so a positive Stage delta is not silently lost at lower
magnitudes.
