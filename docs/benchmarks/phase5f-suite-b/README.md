# Phase 5F Suite B machine-readable evidence

Checkpoint 2 measures TNO-only `Magic Weapon`, `Holy Weapon`, and `Soul Eater`
on the seven accepted Tensura/L2 bosses. It does not contain Elemental, Energy
Steal, Severance, forced-trait coverage, or APO+TNO evidence.

Locked protocol:

- clean `royalvariations:royal_bow` with exactly one native Tensura engraving
- real `royalvariations:royal_arrow`, with Royal Arrow Mark disabled only for
  this opt-in isolation harness
- `APO_profile = NONE`; no affix, gem, socket, rarity, or APO combat bonus
- Native plus S0-S7 for every boss/level profile
- natural representative, natural maximum, and stress 300/600/800/1000 levels,
  skipping only an exact natural-maximum duplicate
- ten releases and a 200-tick observation window per case
- each real full-draw projectile keeps its owner, velocity, item and damage and
  is dispatched through the Royal Arrow's own `onHitEntity` path in a
  deterministic two-block final collision lane; this removes scripted-boss
  trajectory misses without fabricating a damage source or amount
- one legal native L2 roll per boss/level, cloned before damage so all nine
  Stage cases have identical traits and fresh Adaptive memory

The Stage fixture does not implement the production Stage system. Magic/Holy
use the locked temporary coefficient `1 + 2 * Curve-C bonus`; Soul uses
`1 + Curve-C bonus`. Matching Tensura Resistance recovery is 0% through S4,
25% at S5, 50% at S6, and 100% at S7. For S5-S7 only, the harness computes the
locked `post + penetration * (pre - post)` amount from Tensura's runtime 50%
HP gate/50% resistance rule, then uses Tensura's own resistance-bypass level 1
to prevent the same layer from being applied twice. This happens before L2
defensive processing. The bypass is never set when matching Nullification is
present, so Nullification remains absolute.

Official artifacts are stored under one family directory per boss. The source
runtime logs remain ignored. Preserve a capture only after validation:

```powershell
scripts/extract-phase5f-suite-b.ps1 `
  -LogPath <runtime-log> `
  -OutputPath <family>/<boss>.jsonl `
  -ExpectedFamily <MAGIC_WEAPON|HOLY_WEAPON|SOUL_EATER> `
  -ExpectedBoss <entity-id> `
  -ExpectedCases <45-or-54>
```

`45` applies to Luminous because its natural maximum is exactly level 300;
every other boss has `54` cases. Diagnostic output is explicitly rejected.

## Checkpoint status

| Family | Boss | Levels | Cases | Per-hit rows | Errors | Status |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| Magic Weapon | `tensura_neb:luminous_valentine` | 215, 300, 600, 800, 1000 | 45 | 450 | 0 | Accepted |

Luminous has matching Magic Resistance and no Magic Nullification in every
captured profile. Native through S4 remained fully blocked. The locked recovery
fixture produced measurable progression at S5-S7 (roughly 3.2-3.36, 6.8-7.14,
and 14.4-15.12 DPS respectively). Its actual `tensura:magic` source was not in
`neoforge:is_magic`, so naturally rolled L2 Dispell did not transform these
events. These are capture facts, not balance conclusions; family-wide
classification is deferred until all seven Magic Weapon bosses are complete.
