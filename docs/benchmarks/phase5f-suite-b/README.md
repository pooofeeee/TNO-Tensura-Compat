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
| Magic Weapon | `tensura_neb:carrion` | 150, 210, 300, 600, 800, 1000 | 54 | 540 | 0 | Accepted |
| Magic Weapon | `tensura_neb:rimuru_ogre_fight` | 167, 250, 300, 600, 800, 1000 | 54 | 540 | 0 | Accepted |
| Holy Weapon | `tensura_neb:luminous_valentine` | 215, 300, 600, 800, 1000 | 45 | 450 | 0 | Accepted |
| Holy Weapon | `tensura:hinata_sakaguchi` | 200, 280, 300, 600, 800, 1000 | 54 | 540 | 0 | Accepted |
| Holy Weapon | `tensura:gazel_dwargo` | 185, 260, 300, 600, 800, 1000 | 54 | 540 | 0 | Accepted |
| Holy Weapon | `tensura:orc_disaster` | 175, 250, 300, 600, 800, 1000 | 54 | 540 | 0 | Accepted |

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

Carrion had matching Magic Resistance and no Magic Nullification. Native-S4
were `EFFECTIVELY DEAD`; S5-S7 recovered measurable progression at roughly
3.2-3.36, 6.8-7.14, and 14.4-15.12 DPS in five profiles. The Lv300 legal roll
included Adaptive and compressed those stages to about 0.64, 1.36, and 2.90
DPS, respectively, making that profile `MARGINAL`. The repeated-hit rows record
the Adaptive reductions, with no unexpected L2 bypass.

Rimuru Ogre Fight naturally rolled Adaptive at every level. It compressed the
family to roughly 1.28 Native DPS and 2.30 S7 DPS, so the progression is
`MARGINAL` despite being measurable. Lv1000 also rolled Dementor and reduced
the range further to about 0.48-0.62 DPS. Lv167 Regenerate was observed, but
the applied-event cap kept capped/background healing out of DPS. No matching
Magic Resistance/Nullification or unexpected L2 bypass was present.

## Magic Weapon family summary

Magic Weapon is complete: seven bosses, 369 cases, 3,690 per-hit rows, and zero
case errors. Across the 41 boss/level profiles, average DPS rose from 2.09
(Native) to 9.90 (S7). Twenty-three profiles remained at zero through S4; six
profiles remained zero even at S7 (all Gazel profiles). No captured boss had
matching Magic Nullification, and no unexpected L2 bypass was recorded.

The actual `tensura:magic` source was never in `neoforge:is_magic`. Consequently
Dispell transformed zero rows even when naturally present. Dementor correctly
treated this source as non-magic and transformed 180 rows across Elemental
Colossus Lv800 and Rimuru Lv1000. Adaptive reductions were recorded on 590 rows
across Orc Disaster, Carrion, and Rimuru profiles. These live transforms remain
authoritative after Stage scaling and matching-Resistance recovery.

Evidence classifications:

- Luminous and Hinata: Native-S4 `EFFECTIVELY DEAD`; S5 `MARGINAL`; S6-S7
  `MEANINGFUL/BALANCED` as relative progression, though still small against
  their full boss resources.
- Gazel: `EFFECTIVELY DEAD` at every stage and level.
- Orc Disaster: generally `MEANINGFUL/BALANCED`; Lv600 Adaptive profile
  `MARGINAL`/ambiguous.
- Elemental Colossus: generally `MEANINGFUL/BALANCED`; Lv800 Dementor profile
  `MARGINAL`.
- Carrion: Native-S4 `EFFECTIVELY DEAD`; S5 `MARGINAL`; S6-S7 generally
  `MEANINGFUL/BALANCED`, except the Lv300 Adaptive profile (`MARGINAL`).
- Rimuru Ogre Fight: `MARGINAL` across the family because Adaptive was present
  in every captured profile; Lv1000 was further compressed by Dementor.

No Magic Weapon profile reached `TOO STRONG` or `OP`. This is benchmark
classification only; no balance value was changed.

## Holy Weapon captures

Luminous had matching Holy Resistance and no Holy Nullification. Native-S4
were `EFFECTIVELY DEAD`; S5-S7 recovered roughly 3.2-3.36, 7.14-7.48, and
14.4-15.12 DPS in four profiles. Its Lv1000 legal roll included Adaptive and
compressed those stages to about 0.64, 1.36, and 2.88 DPS (`MARGINAL`). The
actual `tensura:holy_damage` source was not in `neoforge:is_magic`, and no L2
layer was unexpectedly bypassed.

Hinata likewise had matching Holy Resistance without Holy Nullification.
Native-S4 were `EFFECTIVELY DEAD`; S5 was `MARGINAL`, while S6-S7 produced
consistent relative progression at about 6.8-7.48 and 14.4-15.12 DPS. No
Adaptive or Dementor profile was generated, and no L2 layer was bypassed.

Gazel is `EFFECTIVELY DEAD` for Holy Weapon at every stage and level. All 540
rows were zero. Matching Holy Resistance was present without Nullification,
but Gazel admitted no Holy engraving event, so even S7 had no damage to
recover. No L2 layer was bypassed.

Orc Disaster had neither matching Holy Resistance nor Nullification. Four
profiles showed broadly `MEANINGFUL/BALANCED` progression (roughly 8-16.7
DPS). Lv300 Dementor compressed the family to about 3.1-4.0 DPS, while Lv800
Adaptive compressed it to about 1.8-3.4 DPS; both are `MARGINAL` profiles.
The transforms were captured after Stage scaling, with no unexpected bypass.
