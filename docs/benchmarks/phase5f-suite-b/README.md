# Phase 5F Suite B machine-readable evidence

Checkpoint 2 measures TNO-only `Magic Weapon`, `Holy Weapon`, and `Soul Eater`
on the seven accepted Tensura/L2 bosses. Checkpoint 3 is adding Elemental /
Slotting, Energy Steal, and Severance in that order. It does not contain
forced-trait coverage or APO+TNO evidence.

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
  -ExpectedFamily <MAGIC_WEAPON|HOLY_WEAPON|SOUL_EATER|ELEMENTAL_SLOTTING|ENERGY_STEAL> `
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
| Holy Weapon | `tensura:elemental_colossus` | 112, 150, 300, 600, 800, 1000 | 54 | 540 | 0 | Accepted |
| Holy Weapon | `tensura_neb:carrion` | 150, 210, 300, 600, 800, 1000 | 54 | 540 | 0 | Accepted |
| Holy Weapon | `tensura_neb:rimuru_ogre_fight` | 167, 250, 300, 600, 800, 1000 | 54 | 540 | 0 | Accepted |
| Soul Eater | `tensura_neb:luminous_valentine` | 215, 300, 600, 800, 1000 | 45 | 450 | 0 | Accepted |
| Soul Eater | `tensura:hinata_sakaguchi` | 200, 280, 300, 600, 800, 1000 | 54 | 540 | 0 | Accepted |
| Soul Eater | `tensura:gazel_dwargo` | 185, 260, 300, 600, 800, 1000 | 54 | 540 | 0 | Accepted |
| Soul Eater | `tensura:orc_disaster` | 175, 250, 300, 600, 800, 1000 | 54 | 540 | 0 | Accepted |
| Soul Eater | `tensura:elemental_colossus` | 112, 150, 300, 600, 800, 1000 | 54 | 540 | 0 | Accepted |
| Soul Eater | `tensura_neb:carrion` | 150, 210, 300, 600, 800, 1000 | 54 | 540 | 0 | Accepted |
| Soul Eater | `tensura_neb:rimuru_ogre_fight` | 167, 250, 300, 600, 800, 1000 | 54 | 540 | 0 | Accepted |

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

Elemental Colossus had neither matching Holy Resistance nor Nullification.
Four profiles showed provisionally `MEANINGFUL/BALANCED` progression from
roughly 8 Native DPS to 14-15 S7 DPS. Lv600 and Lv800 naturally rolled
Adaptive and compressed the range to roughly 1.6-2.88 DPS (`MARGINAL`). No L2
layer was bypassed.

Carrion had neither matching Holy Resistance nor Nullification. All six
profiles showed broadly `MEANINGFUL/BALANCED` progression from roughly 8
Native DPS to 14.4-15.12 S7 DPS. No Adaptive/Dementor profile or unexpected
L2 bypass was observed.

Rimuru Ogre Fight naturally rolled Adaptive at every level, compressing Holy
Weapon to roughly 1.28 Native DPS and 2.30 S7 DPS. It is `MARGINAL` across the
boss. No matching Holy Resistance/Nullification or unexpected L2 bypass was
observed.

## Holy Weapon family summary

Holy Weapon is complete: seven bosses, 369 cases, 3,690 per-hit rows, and zero
case errors. Average DPS across the 41 boss/level profiles increased from 2.99
(Native) to 9.46 (S7). Seventeen profiles remained zero through S4; six Gazel
profiles remained zero at S7. Luminous, Hinata, and Gazel had matching Holy
Resistance; no captured profile had Holy Nullification.

The actual `tensura:holy_damage` source was never in `neoforge:is_magic`, so
Dispell transformed zero rows. Adaptive transformed 756 rows across Luminous,
Orc Disaster, Elemental Colossus, and Rimuru profiles. Dementor transformed 90
Orc Disaster Lv300 rows. No L2 layer was unexpectedly bypassed.

Evidence classifications:

- Luminous and Hinata: Native-S4 `EFFECTIVELY DEAD`; S5 `MARGINAL`; S6-S7
  generally `MEANINGFUL/BALANCED`, except Luminous Lv1000 Adaptive
  (`MARGINAL`).
- Gazel: `EFFECTIVELY DEAD` at every stage and level.
- Orc Disaster: generally `MEANINGFUL/BALANCED`; Lv300 Dementor and Lv800
  Adaptive profiles `MARGINAL`.
- Elemental Colossus: generally `MEANINGFUL/BALANCED`; Lv600/Lv800 Adaptive
  profiles `MARGINAL`.
- Carrion: `MEANINGFUL/BALANCED` across all captured profiles.
- Rimuru Ogre Fight: `MARGINAL` across the boss because every profile rolled
  Adaptive.

No Holy Weapon profile reached `TOO STRONG` or `OP`; no balance value changed.

## Soul Eater captures

Luminous is `EFFECTIVELY DEAD` for Soul Eater at every level and stage. All
450 rows were zero. Neither matching Soul Resistance nor Nullification was
present; the native engraving produced no `tensura:soul_scatter` event on the
Royal Arrow hits, leaving no eligible amount for Stage scaling. No L2 layer was
bypassed.

Hinata is likewise `EFFECTIVELY DEAD` for Soul Eater: all 540 rows were zero.
Matching Soul Resistance was present without Nullification, but no native Soul
event was generated, leaving no damage for S7 recovery. No L2 layer was
bypassed.

Gazel is likewise `EFFECTIVELY DEAD` for Soul Eater: all 540 rows were zero.
Matching Soul Resistance was present without Nullification, but no native Soul
event was generated, leaving no damage for S7 recovery. No L2 layer was
bypassed.

Orc Disaster produced only residual physical Royal Arrow damage, ranging from
0.143 to 1.667 DPS across the 54 cases. `engraving_native_amount` remained zero
in all 540 rows, so Stage had no native Soul amount to scale. Neither matching
Soul Resistance nor Soul Nullification was present, and no L2 layer was
bypassed.

Elemental Colossus is `EFFECTIVELY DEAD` for Soul Eater: all 540 rows were
zero. Neither matching Soul Resistance nor Soul Nullification was present, but
no native Soul event was generated, leaving no amount for Stage scaling. No L2
layer was bypassed.

Carrion is likewise `EFFECTIVELY DEAD` for Soul Eater: all 540 rows were zero.
Neither matching Soul Resistance nor Soul Nullification was present, but no
native Soul event was generated, leaving no amount for Stage scaling. No L2
layer was bypassed.

Rimuru Ogre Fight is likewise `EFFECTIVELY DEAD` for Soul Eater: all 540 rows
were zero. Neither matching Soul Resistance nor Soul Nullification was present,
but no native Soul event was generated, leaving no amount for Stage scaling.
No L2 layer was bypassed.

## Soul Eater family summary

Soul Eater is complete: seven bosses, 369 accepted cases, 3,690 per-hit rows,
and zero case errors. It is effectively non-functional on Royal Arrow in this
runtime path. Across the 41 boss/level profiles, average DPS fell from 0.064
(Native) to 0.030 (S7); 35 profiles were zero through S4 and remained zero at
S7. No row contained a nonzero `engraving_native_amount`.

Luminous, Hinata, Gazel, Elemental Colossus, Carrion, and Rimuru Ogre Fight
produced no native `tensura:soul_scatter` event and therefore no eligible Soul
amount for Stage scaling. Orc Disaster produced only residual physical Royal
Arrow damage (0.143-1.667 DPS), while its `engraving_native_amount` also
remained zero. The matching Soul Resistance present in all Hinata and Gazel
profiles consequently had no Soul amount for Stage scaling or S5-S7
matching-Resistance recovery to amplify or recover.

This is a benchmark/runtime compatibility finding, not permission to alter
production Soul Eater behavior. Checkpoint 2 does not attempt to fix Soul Eater
or change any balance, Tensura, L2, datapack, Royal Bow, or Royal Arrow value.

## Checkpoint 2 cross-family summary

| Family | Boss artifacts | Cases | Per-hit rows | Average DPS Native -> S7 | Zero through S4 / at S7 | Classification |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Magic Weapon | 7 | 369 | 3,690 | 2.09 -> 9.90 | 23 / 6 | Mixed progression; no `TOO STRONG` or `OP` result |
| Holy Weapon | 7 | 369 | 3,690 | 2.99 -> 9.46 | 17 / 6 | Mixed progression; no `TOO STRONG` or `OP` result |
| Soul Eater | 7 | 369 | 3,690 | 0.064 -> 0.030 | 35 / 35 | `EFFECTIVELY DEAD` / non-functional on Royal Arrow |

Magic Weapon had matching Magic Resistance in 23 profiles and no matching
Magic Nullification. Matching Resistance suppressed Native-S4 in those
profiles and exposed the configured S5-S7 recovery when an eligible native
Magic amount existed. Adaptive transformed 590 rows, Dementor transformed 180,
and Dispell transformed zero because `tensura:magic` was not in
`neoforge:is_magic`. Gazel was fully `EFFECTIVELY DEAD`; no profile was `TOO
STRONG` or `OP`.

Holy Weapon had matching Holy Resistance in 17 profiles and no matching Holy
Nullification. Matching Resistance likewise suppressed Native-S4 and exposed
S5-S7 recovery where an eligible native Holy amount existed. Adaptive
transformed 756 rows, Dementor transformed 90, and Dispell transformed zero
because `tensura:holy_damage` was not in `neoforge:is_magic`. Gazel was fully
`EFFECTIVELY DEAD`; no profile was `TOO STRONG` or `OP`.

Soul Eater generated no native Soul amount on any tested boss. Its six fully
zero bosses and Orc Disaster's residual physical-only damage leave no
meaningful Stage progression to classify beyond `EFFECTIVELY DEAD` /
non-functional for this Royal Arrow runtime path.

In total, Checkpoint 2 contains 21 accepted artifacts, 1,107 cases, and 11,070
per-hit rows. It has zero unresolved case errors, APO profile `NONE` throughout,
and no unexpected L2 bypass.

## Checkpoint 3 — Elemental / Slotting (complete)

| Boss | Levels | Cases | Per-hit rows | Errors | Native -> S7 average DPS | Status |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `tensura_neb:luminous_valentine` | 215, 300, 600, 800, 1000 | 45 | 450 | 0 | 0.00 -> 0.00 | Accepted; `EFFECTIVELY DEAD` under absolute Earth Nullification |
| `tensura:hinata_sakaguchi` | 200, 280, 300, 600, 800, 1000 | 54 | 540 | 0 | 0.00 -> 0.00 | Accepted; `EFFECTIVELY DEAD` under absolute Earth Nullification |
| `tensura:gazel_dwargo` | 185, 260, 300, 600, 800, 1000 | 54 | 540 | 0 | 0.00 -> 0.00 | Accepted; `EFFECTIVELY DEAD` under matching Earth/Spiritual Resistance |
| `tensura:orc_disaster` | 175, 250, 300, 600, 800, 1000 | 54 | 540 | 0 | 0.167 -> 0.00 | Accepted; only Lv175 Native/S0 nonzero, all S7 profiles `EFFECTIVELY DEAD` |
| `tensura:elemental_colossus` | 112, 150, 300, 600, 800, 1000 | 54 | 540 | 0 | 0.035 -> 0.00 | Accepted; only Lv112 Native/S0 nonzero, all S7 profiles `EFFECTIVELY DEAD` |
| `tensura_neb:carrion` | 150, 210, 300, 600, 800, 1000 | 54 | 540 | 0 | 0.00 -> 0.00 | Accepted; `EFFECTIVELY DEAD` under matching Earth Resistance |
| `tensura_neb:rimuru_ogre_fight` | 167, 250, 300, 600, 800, 1000 | 54 | 540 | 0 | 0.00 -> 0.00 | Accepted; no native Earth event, all profiles `EFFECTIVELY DEAD` |

The legal one-Earth-core Slotting path consumes the core-equipped Royal Bow
release and creates `tensura:stone_shot`; it does not create a Royal Arrow.
The installed projectile reports native damage `1.0`, retains the benchmark
player owner, and emits `tensura:earth_elemental` with
`minecraft:bypasses_armor` but without `neoforge:is_magic`. The temporary Stage
fixture changes only that projectile damage coefficient. Slot capacity, core
count, projectile utility, and any Royal Bow/Royal Arrow base amount remain
unchanged.

Luminous produced 14 observable Earth events across the 450 rows. Every one was
canceled by native Earth Nullification before L2, remained marked
nullification-authoritative, and received zero matching-Resistance penetration.
All five profiles therefore stayed at zero DPS from Native through S7. Dispell
was naturally present in all five profiles and Adaptive in two, but neither had
an eligible post-nullification event to transform; the actual source also was
not L2-magic. No row recorded unexpected L2 bypass.

Hinata likewise produced 14 observable Earth events across 540 rows. Native
Earth Nullification and Spiritual Resistance were present in all six profiles;
Earth Nullification canceled all 14 events before L2 and kept configured Stage
penetration at zero. Every profile remained zero DPS from Native through S7.
Dispell was naturally present in all six profiles but correctly did not
transform the non-magic source, and no Adaptive or Dementor profile rolled.
Ownership/scope invariants passed on all rows and there was no unexpected L2
bypass.

Gazel remained zero DPS in all six profiles and all nine stages. Matching Earth
and Spiritual Resistance were present without Nullification. Twelve observable
Earth events occurred (nine Native and three S0) and all were canceled by the
native resistance layer. No eligible Earth event was emitted in S5-S7, so the
configured recovery had no event amount to restore even at full S7 recovery.
One profile each naturally rolled Adaptive and Dementor, but both had no
nonzero post-resistance event to transform. No unexpected L2 bypass occurred.

Orc Disaster had no matching Tensura resistance or nullification, providing the
positive event control. Its Lv175 representative produced 1.0 Native DPS and
about 0.495 S0 DPS from 14 real Earth events (10 Native, four S0). The remaining
52 of 54 cases were zero: no eligible Earth event was emitted in the other
level/stage cases, and every S7 profile was zero. Average DPS consequently fell
from about 0.167 Native to 0.00 S7. One profile naturally rolled Dispell, which
correctly did not transform the actual non-magic source; no Adaptive or
Dementor profile rolled. No unexpected L2 bypass occurred. This is a native
runtime compatibility finding, not a Stage or Slotting behavior change.

Elemental Colossus likewise had no matching Tensura defense. Fourteen real
Earth events occurred only in the Lv112 Native/S0 cases (10 Native, four S0);
the other 52 cases and every S7 profile were zero. Average DPS fell from about
0.035 Native to 0.00 S7. Two profiles each naturally rolled Adaptive and
Dementor, but no nonzero repeated post-L2 sequence remained for either to
transform. Ownership/scope invariants passed and no unexpected L2 bypass
occurred.

Carrion was zero in all 54 cases. Matching Earth Resistance canceled the 14
observable Native/S0 Earth events, and no eligible event appeared in later
stages for configured recovery. Two profiles rolled Adaptive, one Dispell, and
one Dementor; none had a nonzero post-resistance sequence to transform. No
unexpected L2 bypass occurred.

Rimuru Ogre Fight was zero in all 54 cases and emitted no native Earth event.
It had neither matching Earth Resistance nor Earth Nullification, so there was
no native Earth amount for Stage or L2 to process. Adaptive rolled in all six
profiles and Dementor in two, but neither had an event sequence to transform.
The artifact retained `APO_profile = NONE`, passed ownership/scope invariants,
and recorded no unexpected L2 bypass.

### Elemental / Slotting family conclusion

The seven accepted artifacts contain 369 cases and 3,690 per-hit rows, with
zero case errors, APO profile `NONE` throughout, and no unexpected L2 bypass.
Across the 41 boss/level profiles, average DPS fell from `0.029512` at Native
to `0.00` at S7. Of the 369 cases, 365 were zero; 39 profiles were zero through
S4, and all 41 profiles were zero at S7. No result reached `TOO STRONG` or
`OP`.

Luminous and Hinata demonstrate that matching Earth Nullification remains
absolute. Gazel and Carrion had matching Earth Resistance, but no eligible
Earth event existed in S5-S7 for configured recovery to amplify. Orc Disaster
Lv175 and Elemental Colossus Lv112 supplied the only nonzero positive controls,
and only in Native/S0. Their native Earth-event availability disappeared in
later independently reset Stage cases despite having no matching Tensura
Resistance or Nullification. Rimuru emitted no native Earth event at any stage.
This loss of event availability is preserved as an observed native runtime
behavior; it is not altered to manufacture monotonic Stage progression.

Thirteen profiles rolled Adaptive, 13 rolled Dispell, and six rolled Dementor.
No row recorded an observed transformation: the non-magic Earth source made
Dispell inapplicable, while upstream cancellation or absent repeated event
sequences left Adaptive and Dementor nothing measurable to transform. The
family is therefore `EFFECTIVELY DEAD` as a Stage progression path in this
installed runtime, apart from the two isolated low-level Native/S0 positive
controls. This finding is not permission to change Slotting, Stage values,
matching-Resistance recovery, or production combat behavior.

## Checkpoint 3 — Energy Steal (in progress)

| Boss | Levels | Cases | Per-hit rows | Errors | Native -> S7 resource impact/s | Status |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `tensura_neb:luminous_valentine` | 215, 300, 600, 800, 1000 | 45 | 450 | 0 | 0.00 -> 0.00 | Accepted; no native Energy Drain event, all profiles `EFFECTIVELY DEAD` |
| `tensura:hinata_sakaguchi` | 200, 280, 300, 600, 800, 1000 | 54 | 540 | 0 | 0.00 -> 0.00 | Accepted; no native Energy Drain event, all profiles `EFFECTIVELY DEAD` |
| `tensura:gazel_dwargo` | 185, 260, 300, 600, 800, 1000 | 54 | 540 | 0 | 0.00 -> 0.00 | Accepted; no native Energy Drain event, all profiles `EFFECTIVELY DEAD` |
| `tensura:orc_disaster` | 175, 250, 300, 600, 800, 1000 | 54 | 540 | 0 | 4257.302 -> 6047.549 | Accepted positive control; every case emitted Energy Drain, Lv175 aggregate non-monotonic |
| `tensura:elemental_colossus` | 112, 150, 300, 600, 800, 1000 | 54 | 540 | 0 | 0.00 -> 0.00 | Accepted; no native Energy Drain event, all profiles `EFFECTIVELY DEAD` |
| `tensura_neb:carrion` | 150, 210, 300, 600, 800, 1000 | 54 | 540 | 0 | 0.00 -> 0.00 | Accepted; no native Energy Drain event, all profiles `EFFECTIVELY DEAD` |
| `tensura_neb:rimuru_ogre_fight` | 167, 250, 300, 600, 800, 1000 | 54 | 540 | 0 | 0.00 -> 0.00 | Accepted; no native Energy Drain event, all profiles `EFFECTIVELY DEAD` |

Energy Steal I is measured through its native event operation: one percent of
the target's current Aura and current Magicules, with a native 20-tick bow
cooldown and no DamageSource. The Stage fixture changes only that eligible
current-pool percentage. It does not alter the Royal Arrow's base damage,
cooldown, resource maxima, native Tensura/L2 mechanics, or production behavior.

Luminous produced no Energy Drain event in any of 450 rows. All Royal Arrow
damage was canceled before Tensura's post-damage Energy Steal hook could run,
so every case had zero resource impact from Native through S7. Dispell was
naturally present in all five profiles, but there was no Energy event or damage
source for it to transform. APO profile remained `NONE`, and no unexpected L2
bypass occurred.

Hinata likewise produced no Energy Drain event in 540 rows. Every Royal Arrow
was canceled before the native post-damage hook, leaving all 54 cases at zero
resource impact from Native through S7. Dispell was naturally present in all
six profiles but had no Energy event or DamageSource to transform. APO profile
remained `NONE`, and no unexpected L2 bypass occurred.

Gazel also produced no Energy Drain event in 540 rows. Upstream Royal Arrow
cancellation prevented the native post-damage hook in every case, so resource
impact remained zero from Native through S7. One profile naturally rolled
Dementor, but there was no Energy operation or DamageSource to transform. APO
profile remained `NONE`, and no unexpected L2 bypass occurred.

Rimuru Ogre Fight also emitted no Energy Drain event in 540 rows. Every Royal
Arrow was canceled before the native post-damage hook, so all 54 cases remained
at zero resource impact from Native through S7. Adaptive rolled in all six
profiles but had no eligible physical-hit sequence to adapt before the Energy
operation. APO profile remained `NONE`, and no unexpected L2 bypass occurred.

Carrion likewise emitted no Energy Drain event in 540 rows. Every Royal Arrow
was canceled before the native post-damage hook, leaving all 54 cases at zero
resource impact from Native through S7. No Adaptive, Dispell, or Dementor
profile rolled; APO profile remained `NONE`, and no unexpected L2 bypass
occurred.

Orc Disaster supplied the positive control: every one of its 54 cases emitted
at least one Energy Drain event, for 81 event rows in total. Every event used
the native one-percent current-pool amount, the exact Stage coefficient, equal
target drain/attacker gain, and no DamageSource. Average resource impact rose
from about 4,257.302/s Native to 6,047.549/s at S7. The Lv175 aggregate moved
the opposite direction (10 eligible Native events versus one at S7), showing
that post-damage event availability—not the per-event Stage formula—can make a
fixed-window profile non-monotonic. One profile each rolled Dispell and
Dementor; neither transforms a non-DamageSource energy operation. No unexpected
L2 bypass occurred.

Elemental Colossus emitted no Energy Drain event in 540 rows. Every Royal Arrow
was canceled before the native post-damage hook, so all 54 cases remained at
zero resource impact from Native through S7. One profile naturally rolled
Adaptive, but no eligible hit sequence reached the Energy operation. APO
profile remained `NONE`, and no unexpected L2 bypass occurred.
