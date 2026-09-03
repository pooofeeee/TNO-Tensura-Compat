# Phase 6 endgame-viability research evidence

## Status and scope

This is a development-only observation set. Phase 6 production behavior,
Curve C, matching-Resistance recovery, matching Nullification, L2 Hostility,
Royal Bow/Royal Arrow base damage, and native Tensura mechanics were not
changed.

The controlled comparator is `tensura:orc_disaster`. The accepted Phase 5F
evidence established it as the one target in the seven-boss set on which Magic
Weapon, Holy Weapon, Energy Steal, and Severance can all exercise their native
paths without a matching Tensura Resistance or Nullification. That makes a
zero result attributable to the native prerequisite or L2 instead of an
unrelated matching defense. Soul Eater and Earth Slotting are retained in the
same comparator to test whether their native events exist at all.

Every artifact uses:

- one clean `royalvariations:royal_bow` with exactly one selected native
  Tensura Engraving and real native Gear EP;
- resolved production Rare S0-S7 at EP 1,000, 41,500, 207,500, 830,000,
  1,245,000, 1,660,000, 2,075,000, and 2,490,000;
- `APO_profile = NONE`, no affixes, gems, sockets, projectile multiplication,
  Apotheosis critical, or Apotheosis amplification;
- Royal Arrow Mark disabled;
- ten releases and a 200-tick window per case;
- one pristine clone of the exact accepted legal L2 profile for all eight
  Stage cases at a level; and
- the authoritative attached L2 level read from
  `LHMiscs.MOB.type().getOrCreate(target)` and `MobTraitCap.getLevel()`.

The installed runtime contains Apotheosis modules, but none is applied to the
weapon or attack. The row assertions require the default, unmodified Apotheosis
attribute values, zero APO components, no APO critical event, no multiplied
projectile, and `APO_profile = NONE`.

## Exact legal L2 profiles

These are the accepted strongest legal Orc Disaster profiles from the Phase 5F
39-trait evidence. Native random residue is cleared, the exact legal profile is
installed, and its pristine serialized state is cloned across S0-S7.

| Level | Exact traits and ranks | Budget |
|---:|---|---:|
| 300 | Dementor 1, Drain 2, Regenerate 2, Tank 5, Wither 1 | 290 / 300 |
| 600 | Adaptive 3, Dementor 1, Drain 2, Regenerate 4, Tank 5, Wither 1 | 590 / 600 |
| 800 | Adaptive 5, Dementor 1, Drain 2, Regenerate 5, Tank 5, Wither 1 | 780 / 800 |
| 1000 | Adaptive 5, Dementor 1, Dispell 2, Drain 2, Regenerate 5, Tank 5, Wither 1 | 980 / 1000 |

The target had 46 armor and 20 toughness in every case. Its combined maximum
HP plus Spiritual Health was 37,000 at Lv300, 61,300 at Lv600, 77,500 at Lv800,
and 93,700 at Lv1000.

## Validation result

All six captures passed the strict extractor: 32 cases and 320 per-hit rows per
family, for 192 cases and 1,920 rows overall. Every capture has one complete
suite result, zero case errors, exact S0-S7 coverage at all four levels, exact
legal traits, exact native EP/production Stage agreement, zero unexpected L2
bypass, zero unexpected Tensura bypass, zero source duplication, zero event
recursion, and `APO_profile = NONE` throughout.

| Family | Native event/contribution | Effect executed | Classification | Failure reasons |
|---|---:|---:|---|---|
| Magic Weapon | 320 / 320 | 320 / 320 | 114 nonzero, 192 near-zero, 14 zero | 192 `L2_MITIGATION`, 14 `OTHER_VERIFIED_REASON` |
| Holy Weapon | 320 / 320 | 320 / 320 | 114 nonzero, 192 near-zero, 14 zero | 192 `L2_MITIGATION`, 14 `OTHER_VERIFIED_REASON` |
| Soul Eater | 0 / 320 | 0 / 320 | 320 zero | 320 `NATIVE_EVENT_ABSENT` |
| Elemental / Slotting | 0 / 320 | 0 / 320 | 320 zero | 320 `NATIVE_EVENT_ABSENT` |
| Energy Steal | 51 / 320 | 51 / 320 | 51 nonzero, 269 zero | 269 `PREREQUISITE_HIT_FAILED` |
| Severance | 320 / 320 | 58 / 320 | 4 nonzero, 54 near-zero, 262 zero | 316 `L2_MITIGATION` |

`NEAR_ZERO` is a diagnostic label for a final eligible family result at or
below 10% of its value entering L2. It is evidence metadata, not a production
threshold or a proposed balance percentage.

The 14 Magic/Holy `OTHER_VERIFIED_REASON` rows are the Lv300 S0 cases and
the first four Lv300 S1 hits. A positive final family event existed, but the
target showed no persistent HP/SHP loss during the observed hit interval. The
capture reports that exact observation and does not misattribute it to L2,
Tensura Resistance, or Nullification.

## Exact fixed-window results

The arrays below are ordered S0, S1, S2, S3, S4, S5, S6, S7. Values are from
the accepted case results; every intermediate layer and every individual hit
is retained in the corresponding JSONL artifact.

### Magic Weapon — final target HP/SHP DPS

| L2 level | S0-S7 DPS |
|---:|---|
| 300 | 0.000000, 1.992456, 3.272559, 3.334082, 3.411206, 3.464224, 3.504004, 3.563867 |
| 600 | 0.705381, 0.698140, 0.769409, 0.792424, 0.784414, 0.746498, 0.757188, 0.767738 |
| 800 | 0.684772, 0.698606, 0.711067, 0.738329, 0.735024, 0.746384, 0.825052, 0.778633 |
| 1000 | 0.699398, 0.698606, 0.712769, 0.764093, 0.735024, 0.750062, 0.762545, 0.806312 |

At S7, the average native/TNO family value before Tensura defenses was 11.2.
There was no matching Tensura defense. The final post-L2 Magic sums across ten
hits were 34.854269 at Lv300, 6.964046 at Lv600, 7.037167 at Lv800, and
6.964046 at Lv1000. At Lv1000 the ten identical 11.2 L2 inputs became
3.485427, 1.742713, 0.871357, 0.435678, 0.217839, 0.108920, 0.054460,
0.027230, 0.013615, and 0.006807. This is the verified Dementor compression
followed by Adaptive's same-source geometric decay.

### Holy Weapon — final target HP/SHP DPS

| L2 level | S0-S7 DPS |
|---:|---|
| 300 | 0.000000, 2.040976, 3.272559, 3.334082, 3.393349, 3.449938, 3.553320, 3.563867 |
| 600 | 0.714024, 0.756636, 0.723413, 0.723213, 0.735024, 0.746384, 0.757188, 0.767738 |
| 800 | 0.700857, 0.712783, 0.773032, 0.723213, 0.735456, 0.783387, 0.757188, 0.767738 |
| 1000 | 0.684772, 0.727061, 0.771362, 0.734395, 0.735024, 0.758901, 0.778055, 0.767738 |

Holy follows the same high-level wall. Its S7 post-L2 family sums were
34.854269, 6.964046, 6.964046, and 6.964046 from Lv300 through Lv1000. The
Lv1000 per-hit sequence exactly matches the Magic sequence above.

### Soul Eater — family result

Every S0-S7 case at every level had zero native `tensura:soul_scatter` events,
zero eligible Soul amount, and zero Soul effect. All 320 rows are
`NATIVE_EVENT_ABSENT`. The small overall DPS in the artifact is residual
physical Royal Arrow damage and is not a Soul Eater result.

| L2 level | Overall residual physical DPS, S0 -> S7 | Soul result |
|---:|---:|---:|
| 300 | 0.791336 -> 0.107143 | 0 -> 0 |
| 600 | 0.071429 -> 0.089286 | 0 -> 0 |
| 800 | 0.109954 -> 0.089286 | 0 -> 0 |
| 1000 | 0.071429 -> 0.071429 | 0 -> 0 |

### Elemental / Slotting — family result

The production wrapper correctly scaled the legal Earth core's native
`tensura:stone_shot` projectile damage, but the projectile emitted no native
`tensura:earth_elemental` damage event against this target at any level or
Stage. All 320 rows are `NATIVE_EVENT_ABSENT`; every S0-S7 final family result
and overall DPS is zero.

### Energy Steal — target resource impact per second

The arrays are combined current Magicule plus Aura drain per second. The
native event is not a DamageSource and does not enter the L2 damage pipeline.
Whenever its physical prerequisite survived, the exact native 1% argument was
scaled by production Curve C to 1.05%-1.40% and target drain equaled attacker
gain.

| L2 level | S0-S7 resource impact/s |
|---:|---|
| 300 | 16509.669536, 8866.743389, 1895.114858, 1977.511156, 2059.907454, 4256.757556, 4419.366651, 2307.096348 |
| 600 | 3210.493578, 6689.751334, 3516.254871, 3669.135518, 3822.016165, 3974.896811, 4127.777458, 4280.658104 |
| 800 | 4047.362460, 4240.094005, 4432.825551, 9195.607509, 9576.348678, 5011.020188, 5203.751734, 5396.483279 |
| 1000 | 5180.162284, 5426.836679, 5673.511073, 11769.328711, 6166.859862, 6413.534257, 6660.208651, 6906.883046 |

Admitted native events per S0-S7 case were respectively `10,5,1,1,1,2,2,1`
at Lv300; `1,2,1,1,1,1,1,1` at Lv600; `1,1,1,2,2,1,1,1` at Lv800; and
`1,1,1,2,1,1,1,1` at Lv1000. Thus the per-event formula is healthy, while
Tank/Dementor/Adaptive suppression of the physical prerequisite makes the
fixed-window result sparse and non-monotonic.

### Severance — final target HP/SHP DPS

| L2 level | S0-S7 DPS |
|---:|---|
| 300 | 1.684499, 0.842249, 0.168450, 0.176250, 0.176250, 0.185137, 0.272908, 0.192537 |
| 600 | 0.168450, 0.168450, 0.168450, 0.176250, 0.176250, 0.221597, 0.228279, 0.188114 |
| 800 | 0.168450, 0.261496, 0.261496, 0.275289, 0.218633, 0.180714, 0.228279, 0.188114 |
| 1000 | 0.168450, 0.168450, 0.168450, 0.172914, 0.176250, 0.180714, 0.288281, 0.188114 |

The native Severance contribution existed for all 320 shots and stayed in the
one physical `minecraft:arrow` source. Only 58 shots stored any wound. At
Lv1000 S7 the combined physical values entering L2 were about 20-21; the ten
final physical values were 1.836502, 0, 0, 0, 0, 0.044643, 0, 0, 0, and 0.
Only two wounds were stored, for a final wound sum of 2.336914. Tank,
Dementor, and Adaptive are the verified wall.

## Evidence files

- `magic_weapon.jsonl`
- `holy_weapon.jsonl`
- `soul_eater.jsonl`
- `elemental_slotting.jsonl`
- `energy_steal.jsonl`
- `severance.jsonl`

Each file contains one catalog, 320 per-hit rows, 32 case results, and one
complete suite result. Raw runtime logs and worlds are not evidence artifacts
and are not tracked.
