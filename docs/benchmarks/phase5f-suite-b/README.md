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
| Magic Weapon | `tensura:hinata_sakaguchi` | 200, 280, 300, 600, 800, 1000 | 54 | 540 | 0 | Accepted |
| Magic Weapon | `tensura:gazel_dwargo` | 185, 260, 300, 600, 800, 1000 | 54 | 540 | 0 | Accepted |
| Magic Weapon | `tensura:orc_disaster` | 175, 250, 300, 600, 800, 1000 | 54 | 540 | 0 | Accepted |
| Magic Weapon | `tensura:elemental_colossus` | 112, 150, 300, 600, 800, 1000 | 54 | 540 | 0 | Accepted |

Luminous has matching Magic Resistance and no Magic Nullification in every
captured profile. Native through S4 remained fully blocked. The locked recovery
fixture produced measurable progression at S5-S7 (roughly 3.2-3.36, 6.8-7.14,
and 14.4-15.12 DPS respectively). Its actual `tensura:magic` source was not in
`neoforge:is_magic`, so naturally rolled L2 Dispell did not transform these
events. These are capture facts, not balance conclusions; family-wide
classification is deferred until all seven Magic Weapon bosses are complete.

Hinata likewise had matching Magic Resistance without Magic Nullification in
all six profiles. Native-S4 were fully blocked; S5-S7 measured roughly
3.2-3.36, 6.8-7.14, and 14.4-15.84 DPS. Actual post-L2 damage matched the
recorded engraving damage for all 540 rows, no L2 layer was unexpectedly
bypassed, and the naturally generated profiles in this accepted rerun did not
include Adaptive. Dispell was present, but the source again was not tagged
`neoforge:is_magic` and was not transformed by Dispell.

Gazel is `EFFECTIVELY DEAD` for this family in all six profiles and all nine
stages: every row measured zero DPS. The legitimate Royal Arrow releases
completed, but Gazel admitted no projectile/family damage event, leaving
`engraving_native_amount = 0` and no damage-source IDs. Although Magic
Resistance was present and Magic Nullification was not, even S7 had no
matching-resistance damage to recover. No L2 layer was bypassed.

Orc Disaster had neither matching Magic Resistance nor Nullification. Five of
six profiles showed measurable, generally monotonic Native/S0-S7 progression
(about 8-15 DPS at the upper stages), provisionally `MEANINGFUL/BALANCED` at
this technical-test scale. The Lv600 legal roll included Adaptive and reduced
successive same-family hits by one half (for example S7: 14.4, 7.2, 3.6, 1.8,
...). That profile's aggregate progression was non-monotonic and is classified
`MARGINAL`/ambiguous rather than tuned around. The corrected post-L2 probe
marked the Adaptive transforms, and no L2 layer was bypassed.

Elemental Colossus had neither matching Magic Resistance nor Nullification.
Five profiles progressed from about 8 Native DPS to 14.4 S7 DPS and are
provisionally `MEANINGFUL/BALANCED`. Its Lv800 legal roll included Dementor;
because the actual Magic Weapon source is not L2-magic-tagged, Dementor reduced
each S7 event from 14.4 to about 3.85. That compressed profile is `MARGINAL`,
and its recorded Dementor transforms demonstrate that Stage did not bypass L2.
