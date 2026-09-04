# Phase 6 endgame-effectiveness calibration evidence

## Checkpoint A — target durability decomposition

Status: complete. The accepted artifact is `durability.jsonl`: one catalog,
16 `durability_result` records, one complete suite result, and zero case
errors. Every row uses `APO_profile = NONE`. The disposable targets were
captured only after the requested L2 level, native L2 trait state, trait
attribute modifiers, and the required Tensura:L2Hostility datapack modifiers
had settled. The complete exact trait/rank list and the complete health and
Spiritual Health modifier lists are retained per row.

### Installed-runtime formula audit

The installed artifact is `l2hostility-3.0.18.jar`. Its
`dev.xkmc.l2hostility.content.logic.TraitManager.scale` method does the
following:

1. because `exponentialHealth = false`, calculate `level * healthFactor`;
2. multiply that amount by the entity datapack's `healthScale`; and
3. install `l2hostility:hostility_health` on vanilla `MAX_HEALTH` using
   `ADD_MULTIPLIED_TOTAL`.

The active server setting is `healthFactor = 0.03`. The four entity scales
from the loaded Tensura:L2Hostility datapack are Luminous `0.85`, Hinata
`0.90`, Gazel `1.00`, and Orc Disaster `1.20`. Therefore the exact generic
vanilla-health multiplier is:

```text
H = 1 + level * 0.03 * entityHealthScale
```

Tank is a separate trait path. `LHTraits.TANK` constructs an
`AttributeTrait`; `AttributeTrait.initialize` multiplies every configured
factor by the actual rank. With the active values `tankHealth = 0.20`,
`tankArmor = 4`, and `tankTough = 4`, it installs
`l2hostility:tank_health` as `ADD_MULTIPLIED_TOTAL`, plus four armor and four
toughness per rank. Thus `T = 1 + 0.20 * rank`. Tank is not generic level
scaling.

L2's `hostility_health` modifier was absent from `MAX_SPIRITUAL_HEALTH` in all
16 cases. Native L2 does not directly scale SHP. The required external
Tensura:L2Hostility datapack independently installs
`tensura_l2h:l2_shp_scale` on `tensura:max_spiritual_health` as
`ADD_MULTIPLIED_BASE`, with amount `level * 0.03`. That bridge is why SHP
grows as `nativeSHP * (1 + 0.03 * level)`. It is level-derived durability,
but it must not be mistaken for `TraitManager.scale` or for Tank.

### Runtime results

The `generic` and `Tank` columns show multiplier followed by the portion that
actually survived the runtime's 10,000 vanilla-health ceiling. Unclamped
contributions are retained in the JSONL as separate fields.

| Boss | Lv | native HP | generic H / realized HP | Tank rank / T / realized HP | final HP | native SHP + bridge SHP = final SHP | combined | armor / toughness |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `tensura_neb:luminous_valentine` | 300 | 8000 | 8.65x / 2000 | 0 / 1x / 0 | 10000 | 10000 + 90000 = 100000 | 110000 | 50 / 0 |
| `tensura_neb:luminous_valentine` | 600 | 8000 | 16.3x / 2000 | 5 / 2x / 0 | 10000 | 10000 + 180000 = 190000 | 200000 | 70 / 20 |
| `tensura_neb:luminous_valentine` | 800 | 8000 | 21.4x / 2000 | 0 / 1x / 0 | 10000 | 10000 + 240000 = 250000 | 260000 | 50 / 0 |
| `tensura_neb:luminous_valentine` | 1000 | 8000 | 26.5x / 2000 | 0 / 1x / 0 | 10000 | 10000 + 300000 = 310000 | 320000 | 50 / 0 |
| `tensura:hinata_sakaguchi` | 300 | 3000 | 9.1x / 7000 | 0 / 1x / 0 | 10000 | 3600 + 32400 = 36000 | 46000 | 50 / 0 |
| `tensura:hinata_sakaguchi` | 600 | 3000 | 17.2x / 7000 | 0 / 1x / 0 | 10000 | 3600 + 64800 = 68400 | 78400 | 50 / 0 |
| `tensura:hinata_sakaguchi` | 800 | 3000 | 22.6x / 7000 | 0 / 1x / 0 | 10000 | 3600 + 86400 = 90000 | 100000 | 50 / 0 |
| `tensura:hinata_sakaguchi` | 1000 | 3000 | 28x / 7000 | 5 / 2x / 0 | 10000 | 3600 + 108000 = 111600 | 121600 | 70 / 20 |
| `tensura:gazel_dwargo` | 300 | 3000 | 10x / 7000 | 5 / 2x / 0 | 10000 | 3600 + 32400 = 36000 | 46000 | 80 / 20 |
| `tensura:gazel_dwargo` | 600 | 3000 | 19x / 7000 | 2 / 1.4x / 0 | 10000 | 3600 + 64800 = 68400 | 78400 | 68 / 8 |
| `tensura:gazel_dwargo` | 800 | 3000 | 25x / 7000 | 3 / 1.6x / 0 | 10000 | 3600 + 86400 = 90000 | 100000 | 72 / 12 |
| `tensura:gazel_dwargo` | 1000 | 3000 | 31x / 7000 | 2 / 1.4x / 0 | 10000 | 3600 + 108000 = 111600 | 121600 | 68 / 8 |
| `tensura:orc_disaster` | 300 | 700 | 11.8x / 7560 | 3 / 1.6x / 1740 | 10000 | 2700 + 24300 = 27000 | 37000 | 38 / 12 |
| `tensura:orc_disaster` | 600 | 700 | 22.6x / 9300 | 3 / 1.6x / 0 | 10000 | 2700 + 48600 = 51300 | 61300 | 38 / 12 |
| `tensura:orc_disaster` | 800 | 700 | 29.8x / 9300 | 3 / 1.6x / 0 | 10000 | 2700 + 64800 = 67500 | 77500 | 38 / 12 |
| `tensura:orc_disaster` | 1000 | 700 | 37x / 9300 | 3 / 1.6x / 0 | 10000 | 2700 + 81000 = 83700 | 93700 | 38 / 12 |

### Answer to the checkpoint question

Only the realized `hostility_health` amount in the table is truly generic L2
vanilla-health scaling: 2,000 HP for Luminous, 7,000 for Hinata/Gazel, and
7,560 at Orc Lv300 or 9,300 at Orc Lv600+. The much larger mathematical L2
health values are clipped by the 10,000 attribute ceiling. Tank contributes
separately; in this sample only Orc Lv300 had room below the ceiling, so 1,740
Tank HP was realized. The dominant high-level growth in combined fight
resources is instead the external datapack's SHP bridge: 3% of native SHP per
L2 level. A future candidate may compensate verified level-derived durability,
but must keep these native, generic-L2, Tank, and datapack-SHP layers distinct.

No production combat or balance behavior was changed by this checkpoint.

## Checkpoint D — absolute diagnostic ceiling

Status: complete. `ceiling_magic_weapon.jsonl` and
`ceiling_holy_weapon.jsonl` each contain one catalog, 72 accepted case
results, 720 per-hit rows, 720 reducer traces, one complete suite result, and
zero case errors. This is 144 cases and 1,440 traced hits overall. Every case
uses the real Royal Bow/Royal Arrow, native Gear EP resolving production S5,
S6, or S7, `APO_profile = NONE`, ten releases, a 200-tick window, and a
pristine clone of the accepted legal Orc Disaster profile for its level.

The development listener runs immediately after L2's own listener and adds
modifiers inside `DamageData.Defence`; it does not restore damage after L2.
The generic diagnostic is `PRE_NONLINEAR` priority 7435, the Dementor blend is
`PRE_NONLINEAR` priority 7437 around native priority 7436, and the Adaptive
blend is `POST_MULTIPLICATIVE` priority 7437. The original source IDs remain
`tensura.magic` and `tensura.holy_damage`. Each hit has exactly one eligible
family event and no duplicate, recursion, unexpected L2 bypass, unexpected
Tensura bypass, second family source, or direct HP subtraction.

### Durability-layer precision

CASE 4 and CASE 5 multiply only the eligible special contribution by
`1 + Q * (H - 1)`, where the nominal generic L2 hostility-health multiplier
for Orc is `H = 1 + level * 0.03 * 1.2`. They do not alter target HP, SHP,
Tank, or the external datapack. This must not be misread as all durability
being native L2 generic health. Checkpoint A proved that vanilla HP is capped
at 10,000, Tank is separate, and the external Tensura:L2Hostility datapack
independently makes SHP `nativeSHP * (1 + level * 0.03)`. At Lv1000 the
diagnostic input is therefore 37x while the separately retained SHP bridge is
31x. Checkpoint E must calibrate this deliberately; D uses 100% only as an
upper-bound necessity test.

### S7 diagnostic results

Each cell is family DPS / estimated family-only TTK. TTK uses the full
recorded maximum HP + SHP and is an estimate, not a simulated kill.

| Family | Lv | C0 baseline | C1 Dementor 100% | C2 Adaptive 100% | C3 both 100% | C4 H 100% only | C5 H + both 100% |
|---|---:|---:|---:|---:|---:|---:|---:|
| Magic | 300 | 3.544 / 10,440s | 11.200 / 3,304s | 3.544 / 10,440s | 11.200 / 3,304s | 7.046 / 5,251s | 132.160 / 280s |
| Magic | 600 | 0.704 / 87,095s | 2.238 / 27,393s | 3.602 / 17,016s | 11.200 / 5,473s | 1.595 / 38,428s | 265.776 / 231s |
| Magic | 800 | 0.704 / 110,130s | 2.238 / 34,632s | 3.602 / 21,513s | 11.200 / 6,920s | 1.675 / 46,272s | 333.760 / 232s |
| Magic | 1000 | 0.696 / 134,548s | 2.238 / 41,871s | 3.485 / 26,883s | 11.760 / 7,968s | 1.767 / 53,042s | 414.400 / 226s |
| Holy | 300 | 3.485 / 10,616s | 11.200 / 3,304s | 3.485 / 10,616s | 11.200 / 3,304s | 7.105 / 5,208s | 138.768 / 267s |
| Holy | 600 | 0.726 / 84,476s | 2.249 / 27,260s | 3.544 / 17,297s | 11.200 / 5,473s | 1.595 / 38,426s | 253.120 / 242s |
| Holy | 800 | 0.696 / 111,286s | 2.378 / 32,593s | 3.485 / 22,235s | 11.200 / 6,920s | 1.675 / 46,272s | 367.136 / 211s |
| Holy | 1000 | 0.697 / 134,372s | 2.238 / 41,871s | 3.485 / 26,883s | 11.200 / 8,366s | 1.745 / 53,709s | 414.400 / 226s |

The total TNO-only Royal Bow event DPS differs from family DPS only by the
surviving unscaled physical arrow residue. At Lv1000 S7 CASE 5 it is 414.471
DPS for both families, giving a 226.1-second estimated total TTK. At the same
coordinate, baseline total DPS is about 0.77 and estimated TTK exceeds 121,000
seconds.

### Reducer and necessity findings

- Dementor recovery alone is not sufficient. At S7 Lv600-Lv1000 its
  family-only TTK remains about 7.6-11.6 hours because Adaptive still owns the
  repeated-source collapse where present.
- Adaptive recovery alone is not sufficient. Dementor still constrains the
  family to roughly 3.5 DPS and 4.7-7.5 hours at Lv600-Lv1000.
- Recovering both reducers is still not sufficient: 11.2-11.76 family DPS
  leaves 91-139 minute estimated fights.
- Generic-H compensation alone is not sufficient because both traits still
  act after it; its S7 high-level TTK remains 10.7-14.9 hours.
- Some level-derived durability compensation is therefore necessary together
  with partial trait negotiation if practical endgame viability is the goal.
  D does not yet choose how much, and it keeps the external SHP bridge distinct.
- The all-100% upper bound is mathematically capable: S7 Lv600-Lv1000 lands at
  211-242 seconds in this controlled profile. Thus the three-component
  architecture is sufficient in principle and no hidden fourth multiplier is
  justified by this checkpoint.
- Magic and Holy are materially equivalent at these boundaries. Small table
  differences are run-to-run physical/projectile and target-update variance;
  their exact Lv1000 S7 CASE 5 family result is identical.
- Lv600 already has the same fundamental wall: baseline is about 0.70-0.73
  family DPS and roughly 23-24 hours estimated TTK, while both reducer ceilings
  without H still leave about 91 minutes.

Adaptive was never reset or rewritten. In every attached-trait case its count
advanced exactly 1 through 10 and native factor exactly followed
`0.5^(count-1)`, ending at `0.001953125`. A 100% diagnostic factor never
exceeded the pre-Adaptive value; 0% matched native behavior. Equivalent bounds
were validated around Dementor's native base-2 nonlinear result. These are
diagnostic ceilings, not candidate production values.

## Checkpoint E — generic L2-health normalization sweep

Status: complete. `health_magic_weapon.jsonl` and
`health_holy_weapon.jsonl` each contain 60 accepted cases, 600 per-hit rows,
and 600 reducer traces: Q = 0, 0.25, 0.50, 0.75, 1.00 across S5-S7 and
Lv300/Lv600/Lv800/Lv1000. RD and RA remain zero, so actual Dementor and
Adaptive behavior is unchanged. Both artifacts have zero case errors,
unexpected bypasses, duplicates, recursion, or source changes.

The exact candidate tested is `eligible * (1 + Q * (H - 1))`, using only the
nominal Orc generic hostility-health `H = 1 + level * 0.03 * 1.2`. Target
health is never rewritten. Native HP, realized/capped generic HP, Tank, native
SHP, and the separate external SHP bridge retain the Checkpoint A
decomposition. In particular, Q is not derived from final combined resources.

S7 family DPS below is ordered Q = 0, 0.25, 0.50, 0.75, 1.00:

| Family | Lv300 | Lv600 | Lv800 | Lv1000 |
|---|---|---|---|---|
| Magic | 3.485, 5.373, 6.222, 6.730, 7.046 | 0.697, 1.290, 1.408, 1.516, 1.595 | 0.696, 1.303, 1.485, 1.595, 1.677 | 0.696, 1.360, 1.545, 1.686, 1.737 |
| Holy | 3.602, 5.490, 6.280, 6.730, 7.046 | 0.697, 1.231, 1.412, 1.531, 1.595 | 0.696, 1.303, 1.486, 1.597, 1.675 | 0.696, 1.360, 1.549, 1.657, 1.737 |

Q is monotonic at the reducer input but has diminishing final returns because
Dementor applies logarithmically and Adaptive still reaches a 0.001953125
factor. Q=1 alone remains unusable: S7 family-only estimated TTK is 38,428s
at Lv600, about 46,200s at Lv800, and about 53,900s at Lv1000. Thus E confirms
that generic-H participation is required by D's viable architecture but is
not sufficient and cannot substitute for trait negotiation.

No explicit target-level threshold is supported by this sweep. H naturally
scales with actual attached L2 level, Lv600 already has the same wall, and the
development context is absent on no-L2 targets. This is not a final Q choice.
The full 0.25-1.00 interval remains available for the small combined shortlist;
F and G must first establish trait-negotiation regions.

## Checkpoint F — Dementor sweep

Status: complete. `dementor_magic_weapon.jsonl` and
`dementor_holy_weapon.jsonl` each contain 120 cases, 1,200 traced hits, and
zero errors. RD = 0, 0.25, 0.50, 0.75, 1.00 was tested across S5-S7 and all
four levels on both the accepted legal profile and an otherwise-identical
legal control with Dementor removed. The removed trait's 120-point budget was
left unused; no replacement trait or impossible combination was created.
Q=RA=0 throughout.

S7 accepted-profile family DPS below is ordered RD = 0, 0.25, 0.50, 0.75,
1.00. Adaptive remains native at Lv600+ and therefore compresses every value.

| Family | Lv300 | Lv600 | Lv800 | Lv1000 |
|---|---|---|---|---|
| Magic | 3.485, 5.414, 7.652, 10.141, 11.760 | 0.696, 1.082, 1.467, 1.868, 2.238 | 0.696, 1.093, 1.467, 1.853, 2.238 | 0.696, 1.082, 1.467, 2.072, 2.242 |
| Holy | 3.602, 5.414, 7.343, 9.706, 11.200 | 0.696, 1.105, 1.467, 2.287, 2.238 | 0.762, 1.151, 1.660, 1.853, 2.308 | 0.698, 1.266, 1.467, 1.961, 2.238 |

The exact per-hit formula was validated at L2's reducer boundary:
`candidate = nativePost + RD * (pre - nativePost)`. RD=0 is bit-for-bit the
native reducer output within float tolerance, no candidate exceeds the
pre-Dementor input, and RD=1 reaches the same reducer boundary as the legal
no-Dementor control. Source ID, Adaptive count/factor, event count, and all
admission paths remain unchanged.

Classification for later combined testing:

- RD 0 and 0.25: too weak. Even RD 0.25 leaves S7 Lv600-Lv1000 at roughly
  1.1 family DPS and multi-hour TTK.
- RD 0.50-0.75: promising coarse interval. RD 0.50 retains a large Dementor
  disadvantage; RD 0.75 retains a measurable gap while giving substantially
  more pre-Adaptive signal.
- RD 1.00: too strong as a policy candidate because it makes Dementor
  equivalent to the no-Dementor control, even though untouched Adaptive still
  makes the isolated fight nonviable.

Dementor therefore needs partial negotiation, but it is not sufficient alone.
No fine-grained sweep or permanent RD value is selected.

## Checkpoint G — Adaptive sweep

Status: complete. `adaptive_magic_weapon.jsonl` and
`adaptive_holy_weapon.jsonl` each contain 120 cases, 1,200 traced hits, and
zero errors. RA = 0, 0.25, 0.50, 0.75, 1.00 was tested across S5-S7 and all
four levels on the accepted legal profile and the same legal profile with
Adaptive removed and its paid budget left unused. Q=RD=0 throughout.

The installed trait's actual semantics were preserved. The source key remains
`DamageSource.getMsgId()` (`tensura.magic` or `tensura.holy_damage`); L2 owns
the memory list, adaption map, count, rank, and configured 0.5 factor. Rank is
memory capacity (3 at Lv600 and 5 at Lv800/Lv1000), not reduction percent.
With only one source ID, every accepted-profile case advances the count exactly
1 through 10 and native factor exactly
`1, .5, .25, .125, .0625, .03125, .015625, .0078125, .00390625,
.001953125`.

S7 accepted-profile family DPS below is ordered RA = 0, 0.25, 0.50, 0.75,
1.00:

| Family | Lv600 | Lv800 | Lv1000 |
|---|---|---|---|
| Magic | 0.698, 1.394, 2.091, 2.788, 3.485 | 0.696, 1.441, 2.091, 2.788, 3.544 | 0.696, 1.394, 2.091, 2.788, 3.544 |
| Holy | 0.698, 1.441, 2.091, 2.788, 3.544 | 0.696, 1.394, 2.091, 2.788, 3.544 | 0.701, 1.394, 2.122, 2.788, 3.544 |

At RA=0.75 the negotiated factors are
`1, .875, .8125, .78125, .765625, .7578125, .75390625, .751953125,
.750976563, .750488281`. Thus hit ten remains about 25% below hit one; Adaptive
is visibly and meaningfully harmful. At RA=0.50 the late-hit penalty remains
about 50%. RA=1 makes every factor 1 and reproduces the no-Adaptive boundary,
so it is rejected as too strong.

RA 0-0.25 is too weak for the later combined objective, RA 0.50-0.75 is the
promising coarse interval, and RA 1.00 is too strong architecturally. Even the
isolated RA ceiling remains nonviable because native Dementor stays active.
No Adaptive state was reset or rewritten and no permanent RA is selected.

## Checkpoint B — Magic/Holy classification

Status: complete. `classification.jsonl` contains two runtime registry
observations and one complete suite result, with zero case errors.

Tensura 2.0.1.1 defines both Engravings through its `tensura:after_attack`
`additional_damage` effect using `TOTAL_ATTACK_MULTIPLY`. Magic Weapon names
`tensura:magic`; Holy Weapon names `tensura:holy_damage`. The installed
`TensuraDamageTypes` registry exposes these as `MAGIC_GENERIC` and
`HOLY_DAMAGE`, respectively. Their runtime `DamageSource.getMsgId()` values
are `tensura.magic` and `tensura.holy_damage`.

Both runtime holders have exactly these effective tags:

| Damage type | Runtime tags |
|---|---|
| `tensura:magic` | `minecraft:bypasses_armor`, `minecraft:bypasses_shield`, `minecraft:no_knockback`, `minecraft:witch_resistant_to`, `tensura:bypass_protection_enchantment` |
| `tensura:holy_damage` | `minecraft:bypasses_armor`, `minecraft:bypasses_shield`, `minecraft:no_knockback`, `tensura:bypass_protection_enchantment` |

Neither source has `neoforge:is_magic`, `minecraft:bypasses_effects`,
`minecraft:bypasses_invulnerability`, or `minecraft:bypasses_resistance`.
The distinction is decisive in the installed L2 Hostility 3.0.18 bytecode:

- `DementorTrait.onDamaged` returns without reducing only for bypass-
  invulnerability, bypass-effects, or NeoForge `IS_MAGIC` sources. These two
  sources satisfy none of those exits, so Dementor installs its nonlinear
  reducer. The active base is 2; `x < 2` becomes `x/2`, otherwise it becomes
  `log(x)/log(2)`. This exactly explains `11.2 -> 3.485427`.
- `DispellTrait.onDamaged` is the complementary branch: after the same two
  bypass exits, it returns unless the source has NeoForge `IS_MAGIC`. These
  sources do not, so Dispell does not install its damage reducer. Its
  equipment-disable behavior when the mob attacks is a separate method and
  remains unaffected.
- `LHAttackListener.onDamage` obtains the target capability through
  `LHMiscs.MOB.type().getExisting(target)` and invokes each actual trait's
  `onDamaged`; L2 DamageTracker carries the original source into that path.

This is a semantic mismatch: Tensura calls the events Magic/Holy and gives
them armor-bypassing semantics, while L2's two reducers classify them solely
by the NeoForge `IS_MAGIC` tag.

Two research-only architecture choices were compared:

1. Preserve the exact source and tags, then negotiate only the demonstrated
   Dementor reduction inside the TNO eligible-contribution context. This is
   narrow, retains DamageTracker ordering, does not activate Dispell, and
   cannot affect unrelated damage.
2. Teach only a compatibility bridge that Tensura Magic/Holy are semantically
   magical to L2. This must not add a global tag or replace the DamageSource;
   it would also need to define whether the compatibility classification
   activates Dispell, making it broader and more interaction-sensitive.

No production choice is locked here. The safe default carried into the next
checkpoints is option 1: preserve original source identity/classification and
negotiate only reductions that calibration proves necessary.

## Checkpoint C — development-only calibration context

Status: complete. `Phase6CalibrationContext` is a synchronous scope around
only the existing `AdditionalDamageEntity` call for the classified Magic and
Holy families. It records the originating classified stack, authoritative
native-EP Stage, family, native eligible amount, amount after production Curve
C, amount after the accepted Tensura defense layer, target, actual existing L2
capability, relevant attached trait ranks, and temporary `Q/RD/RA` parameters.

The capability path is exactly
`LHMiscs.MOB.type().getExisting(target)`. The context does not call
`getOrCreate`; absent, uninitialized, inaccessible, or malformed attachments
fail closed by producing no scope. It also rejects unclassified gear,
non-Magic/Holy families, and missing Stages.

The scope and its parameters are thread-local and are removed in `finally`
after the one native `Entity.hurt` call. Nothing is written to the ItemStack,
Royal Arrow, target capability, target/player, or world. The L2 capability is
observed but never mutated. In particular, Adaptive memory, source keys,
counts, rank, and capacity remain entirely L2-owned.

Ordinary production cannot activate the mechanism: it requires both a
non-production environment and the explicit `tno.phase6.calibration` system
property. With the property absent, the wrapped call receives the exact same
`recovered` value as before and no context exists. Parameter construction is
bounded to finite `[0,1]` values and is covered by unit tests. The full clean
build, existing Stage/Resistance/Severance suites, and the new parameter tests
all pass.

## Checkpoint H — combined candidate matrix

Status: complete. `combined_magic_weapon.jsonl` and
`combined_holy_weapon.jsonl` each contain 135 cases, 1,350 per-hit rows, and
1,350 reducer traces. The matrix covers Lv600/Lv800/Lv1000, S5-S7, three
strictly increasing candidate ramps, and five actual legal profile variants.
Every case uses a fresh initialized L2 attachment; this avoids treating a
serialized clone as proof for native ticking traits. Removed traits are legal
controls whose budget is left unused.

The candidate inputs are:

| Ramp | S5 Q/RD/RA | S6 Q/RD/RA | S7 Q/RD/RA |
|---|---|---|---|
| Low | 0.25 / 0.50 / 0.50 | 0.375 / 0.625 / 0.625 | 0.50 / 0.75 / 0.75 |
| Mid | 0.375 / 0.50 / 0.50 | 0.5625 / 0.625 / 0.625 | 0.75 / 0.75 / 0.75 |
| High | 0.50 / 0.50 / 0.50 | 0.75 / 0.625 / 0.625 | 1.00 / 0.75 / 0.75 |

The high ramp is the only credible safety-test candidate. On the accepted
profile its Magic S7 family DPS is 161.184, 224.632, and 262.273 at levels
600, 800, and 1000; Holy is 153.459, 211.416, and 250.364. Corresponding gross
combined-resource TTK is 380/345/357 seconds for Magic and 399/367/374 seconds
for Holy. S5 remains roughly a 25-minute gross fight and S6 roughly an
11-minute fight, so the desired Stage progression is present without changing
Curve C or any production value.

The trait comparisons remain material. Across the high-S7 cases, an otherwise
identical no-Dementor control reaches 202-348 family DPS, no-Adaptive reaches
192-313, and no-Dementor/no-Adaptive reaches 253-456. The accepted profile is
therefore still disadvantaged by both traits. Adaptive count remains 1-10 and
its original `tensura.magic` or `tensura.holy_damage` source key is unchanged;
the RA=0.75 tenth-hit factor is 0.750488. Tank stays at rank 5 and continues to
apply to the unscaled physical arrow path.

Regenerate is a blocking qualification, not a value to hide in gross TTK. The
installed config and bytecode give `maxHealth * 0.01 * rank` healing every
second: 400 HP/s at the legal Lv600 rank 4 and 500 HP/s at Lv800/Lv1000 rank
5. This ceiling exceeds all tested TNO-only candidates, even with Dementor and
Adaptive removed. The 200-tick captures observed only timing/resource-path-
dependent partial healing, so they do not support a finite sustained TTK under
continuous Regenerate. H therefore preserves the high ramp only for targeted
safety validation; it does not select production Q/RD/RA values or establish a
complete endgame solution.

Strict extraction verifies the exact 135 coordinates per family, ten releases
and one reducer trace per release, legal profile flags, removed-budget policy,
Regenerate rank/config/rate, H/Dementor/Adaptive formulas, original source IDs,
natural Adaptive 1-10 progression, and zero case errors, bypasses, duplicates,
or recursion.

## Checkpoint I — safety and non-interaction matrix

Status: complete. `safety_magic_weapon.jsonl` and
`safety_holy_weapon.jsonl` each contain 32 cases, 320 per-hit rows, 320
calibration traces, and zero case errors. The matrix uses the accepted legal
Orc Disaster profile at Lv300, Lv600, Lv800, and Lv1000; production S0-S7;
ten real Royal Arrow releases per coordinate; `APO_profile = NONE`; and a
fresh initialized L2 attachment per case. S0-S4 use exactly Q=RD=RA=0. The
development-only high candidate is used only at S5-S7:

| Stage | Q | RD | RA |
|---|---:|---:|---:|
| S0-S4 | 0 | 0 | 0 |
| S5 | 0.50 | 0.50 | 0.50 |
| S6 | 0.75 | 0.625 | 0.625 |
| S7 | 1.00 | 0.75 | 0.75 |

The independently extracted family DPS is:

| Family | L2 level | S5 | S6 | S7 |
|---|---:|---:|---:|---:|
| Magic | 300 | 36.308 | 63.907 | 100.882 |
| Magic | 600 | 38.891 | 86.890 | 153.459 |
| Magic | 800 | 52.269 | 108.856 | 201.920 |
| Magic | 1000 | 64.062 | 146.525 | 250.364 |
| Holy | 300 | 36.308 | 63.907 | 100.882 |
| Holy | 600 | 40.827 | 83.240 | 175.499 |
| Holy | 800 | 50.237 | 113.995 | 214.451 |
| Holy | 1000 | 61.558 | 140.397 | 250.364 |

Every level has strict S5 < S6 < S7 progression; there is no special Lv800
activation edge. The actual L2-derived H term changes continuously with the
attached level. The S0-S4 trace assertions prove that generic normalization,
Dementor negotiation, and Adaptive negotiation each return their native input
exactly. Those 400 lower-Stage hit traces retain ordinary production Curve C
and native L2 behavior; the endgame negotiation itself is a no-op.

The strict extractor also proves all 640 rows retain one native eligible
event, one real `royalvariations:royal_arrow`, the original
`tensura.magic`/`tensura.holy_damage` Adaptive key, one unchanged 8.0 base
physical input, and no Mark, APO projectile conversion, duplicate source,
duplicate eligible event, recursion, unexpected Tensura bypass, or unexpected
L2 bypass. Adaptive remains L2-owned and advances 1-10 on every attached
profile at Lv600+. At S7 its negotiated factor still falls from 1.0 to
0.750488, so repeated-source harm remains visible. Checkpoint H's legal
otherwise-identical controls remain the comparative proof that removing
Dementor or Adaptive produces more damage than the accepted high-ramp profile.

The rest of the safety verdict deliberately reuses accepted evidence rather
than rerunning completed matrices:

- The context is development-only and fail-closed. It requires the explicit
  calibration flag, classified staged gear, Magic or Holy as the active
  family, a target, a loaded L2 runtime, and an initialized attachment returned
  by `getExisting`. Any absent gate or reflection failure produces no scope.
  An ordinary unflagged runtime exits at the first gate before optional L2
  inspection, and unrelated families exit before attachment inspection.
  Nothing is serialized or attached to the bow, arrow, target, player, or
  world.
- The accepted Phase 6 production checks remain authoritative for matching
  Resistance: S0-S4 0%, S5 25%, S6 50%, S7 100%. Matching Nullification is
  absolute at every Stage. The candidate is installed only after the existing
  Tensura layer and cannot create a fallback, second source, or post-
  nullification restoration.
- The accepted 39-trait evidence remains the targeted authority for Arena,
  Repelling, Teleport, Reflect, Tank, Dispell, and Regenerate. Arena admission,
  forced-illegal projectile rejection/avoidance, reflection behavior, Tank's
  ordinary physical reduction, and installed Dispell classification are
  unchanged. The safety cases retain the exact legal Regenerate ranks and the
  configured `maxHealth * 0.01 * rank` nominal rates; Q/RD/RA never edits or
  compensates healing.
- The accepted Suite B/production evidence remains unchanged for the other
  four families. Missing Soul and matching Elemental native events stay
  missing; Energy Steal still requires an admitted physical hit and preserves
  equal target drain/attacker gain when it runs; Severance remains one physical
  source with the native +3 Stage path and no wound after a rejected/zero hit.
  `Phase6CalibrationContext` rejects all four families before inspecting L2.
- The accepted Suite C and targeted Phase 6 APO checks remain unchanged. APO
  projectiles stay independent, APO/base physical/crit/gem/affix output is not
  Q/RD/RA-scaled, Royal Arrow owns no EP or Stage, and native Tensura Gear EP
  remains the sole Stage authority.

All 22 Checkpoint-I acceptance statements pass. Counts are 64/64 live safety
cases and 640/640 live hit traces, plus the already accepted targeted
Phase 5F/6 evidence cited above; failures, duplicate sources/events,
unexpected Tensura bypasses, and unexpected L2 bypasses are all zero. This is
a development safety result, not a permanent production selection. In
particular, it does not solve or weaken Regenerate.
