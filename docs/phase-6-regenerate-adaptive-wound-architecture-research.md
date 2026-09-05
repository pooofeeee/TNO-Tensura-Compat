# Phase 6 Regenerate / Adaptive / wound architecture research

## Scope and checkpoint status

This branch is post-Phase-6, pre-Phase-7 research. It does not change production
combat behavior, Curve C, Magic/Holy production, Royal Arrow base damage, L2
traits, Regenerate, or Tensura's stored wound. It begins from
`571736da7c4de3e30038b0778a5351da6ace3b26`.

| Checkpoint | Status | Result |
|---|---|---|
| W1 — exact wound/Adaptive boundaries | Complete | Adaptive reaches stored wound only through realized HP and Tensura's HP-deficit clamp; the native callback amount remains the pre-L2 integer arrow amount. |
| W2 — candidate architectures | Complete | Candidate C, a partial Adaptive negotiation applied only to eligible Severance wound credit after Tank/Dementor, passes the architecture gate. No coefficient is selected. |
| W3 — development-only prototype | Authorized | Prototype Candidate C only, production-disabled, beginning with capability extremes rather than tuning. |
| W4 — trait identity | Not authorized | Requires W3 mechanical success. |
| W5 — sustained viability | Not authorized | Requires W4 safety success. |

The completed R1-R5 evidence remains authoritative and is not duplicated or
overwritten here. In particular, R5's force-loaded, normally ticking fixture
supersedes the obsolete pre-`DamageData` rejection interpretation from R3/R4.

## W1 authoritative artifacts

| Component | Installed artifact | Version | SHA-256 |
|---|---|---:|---|
| Tensura | `tensura-neoforge-2.0.1.1.jar` | 2.0.1.1 | `C12EC9AAA1488C662EDE52B4BD0150EC114E7BDAC32AF20C0E723612DD79D8B9` |
| L2 Hostility | `l2hostility-3.0.18.jar` | 3.0.18 | `8821952B49C5E9B1980B4D7CCECBCFA8E957204D39AC62D8D40DFF34FAAAF780` |
| embedded L2 Damage Tracker | `l2damagetracker-3.0.8+3.jar` | 3.0.8+3 | `144DD06F1189DDCCBC065512787260C563F9702B8127A4EAB74864971A7F5E89` |

The installed server configuration used by the accepted evidence has
`adaptFactor = 0.5`, `dementorDamageReductionBase = 2.0`, and `regen = 0.01`.
The companion machine-readable source audit is
`docs/benchmarks/phase6-regenerate-adaptive-wound-architecture/w1-boundaries.json`.

## W1 exact single-hit timeline

The following map is for one accepted Royal Arrow hit carrying Severance I.
Symbols identify every numeric quantity that exists at the boundary; a value is
not described as post-defense unless the installed code or accepted runtime
trace establishes that fact.

| Order | Boundary and owner | Numeric quantity |
|---:|---|---|
| 1 | Royal Bow releases `royalvariations:royal_arrow` | Royal Arrow base projectile value `B`. The controlled Phase 5F/6 fixture records `B = 8.0`; it is not a TNO-scalable contribution. |
| 2 | Minecraft calls `EnchantmentHelper.modifyDamage` | Input `B` plus any other ordinary native modifiers. |
| 3 | Tensura Severance I `minecraft:damage` effect | Native eligible contribution `A = 3.0 * enchantmentLevel`, therefore `A = 3.0` at level I. |
| 4 | TNO `SeveranceStageScaling`, before velocity and rounding | Native modified base `M_native`; Curve-C eligible amount `A_stage = A * stage.curveMultiplier`; TNO-only delta `Delta = A_stage - A`; staged modified base `M_stage = M_native + Delta`. Only `A`/`Delta` are eligible. |
| 5 | Projectile velocity and native integer ceiling | `P_native = speed * M_native`; `P_stage = speed * M_stage`; one combined physical integer `D_preL2 = ceil(P_stage)`. The existing positive-delta guard may advance one integer bucket when a real positive eligible delta would otherwise collapse into the same ceiling. |
| 6 | One physical `Entity.hurt` | Exactly one original arrow source: message/source identity `minecraft:arrow`, projectile tag retained, no `IS_MAGIC` retag, no Severance-created second physical hit. |
| 7 | Tank/armor boundary | Tank rank changes native max-health, armor, and toughness attributes. It does not add an L2 damage modifier. Accepted wall traces expose `damageOriginal` and `D_beforeDementor`; Tank/armor influence is already present at the observed pre-Dementor boundary. |
| 8 | L2 Dementor `PRE_NONLINEAR`, priority 7436 | Input `D_dementorIn`; with live base `R = 2`, output is `D/R` below `R`, otherwise `log(D)/log(R)`. Physical arrow sources are eligible; magic/bypass-effect/invulnerability-bypass sources return early. |
| 9 | L2 Adaptive `POST_MULTIPLICATIVE` | Input `D_adaptiveIn = D_dementorOut`; source key is `DamageSource.getMsgId()`, hence `arrow`. On repeat count `n`, native factor is `F_native = adaptFactor^(n-1) = 0.5^(n-1)` in the accepted runtime; output is `D_adaptiveOut = D_adaptiveIn * F_native`. Rank is memory capacity, not the reduction percentage. |
| 10 | Remaining native target processing | Realized vanilla HP loss `L_hp = HP_before - HP_after`. This is the authoritative delivered HP quantity and need not be inferred from an earlier event value. |
| 11 | Tensura `MixinAbstractArrow` after-damage callback | `callbackDamage = D_preL2`, the local integer computed before the `Entity.hurt` call. It is not `D_adaptiveOut` and it is not `L_hp`. The original arrow source/weapon context is reused. |
| 12 | `SeveranceDamageEntity.postDamage` candidate | With the installed Severance-I data, `C_native = min(0.5, 0.5) * callbackDamage = 0.5 * D_preL2`. The amount is explicitly based on the original callback amount and capped by the effect's `severanceCap`. |
| 13 | HP-deficit wound clamp (`ignoreDefence=false`) | `H_free = max(0.5, maxHP - currentHP - existingWound)`; amount offered to storage is `W_offer = min(C_native, H_free)`. This is where post-L2 realized HP first controls enchantment wound magnitude. |
| 14 | Native `EffectStorage.increaseSeveranceAmount` | Severance Protection reduces `W_offer` by 10% per level. Final increment `W_store` is added to native `tensura:effect_storage`; the removal timer is refreshed to the configured 300 seconds. |
| 15 | Native ceiling enforcement | Effective heal ceiling is `maxHP - storedWound`. If HP is above a newly lowered ceiling, `setSeveranceAmount` attempts native `tensura:severance` damage for the excess. |
| 16 | Later Tensura `LivingHealEvent` | At highest priority, healing below the ceiling remains native; crossing healing is truncated; healing at the ceiling is cancelled. Wound does not constrain Spiritual Health. |
| 17 | L2 Regenerate tick | Server-side every 20 target ticks, it calls `heal(maxHP * 0.01 * rank)`: 400 HP/s at rank 4 and 500 HP/s at rank 5 on a 10,000-HP target. It goes through the same `LivingHealEvent`. |

### Boundary relationships

The callback deliberately carries two different concepts:

```text
wound potential:  C_native = 0.5 * pre-L2 integer arrow amount
storage authority: W_offer  = min(C_native, post-hit unallocated HP deficit, with 0.5 floor)
```

Adaptive changes neither `callbackDamage` nor `C_native`. It reduces
`D_adaptiveOut` and therefore usually reduces `L_hp`. The lower realized deficit
then binds `H_free`, which binds `W_offer`. Adaptive's effect on normal stored
wound is consequently indirect but causal and decisive.

Tank and Dementor occur before Adaptive's repeated-source multiplier. Tank is
attribute/vanilla-defense behavior; Dementor is a nonlinear L2 modifier;
Adaptive is a later multiplicative modifier. None of them writes Tensura wound
state. Regenerate occurs later and is constrained only by the wound ceiling
that native Tensura successfully stored.

## W1 native Severance and wound precedents

### Enchantment path

Installed `data/tensura/enchantment/severance.json` contains:

- an additive native attack contribution of `+3.0` per level;
- `amount = 0.5`;
- `severanceCap = 0.5`;
- `multiplyOriginalDamage = true`; and
- `ignoreDefence = false`.

This path is the installed precedent for pre-defense/original damage and capped
wound potential: it receives the arrow's pre-L2 integer damage, multiplies that
original amount, caps the multiplier, and then normally subjects storage to the
post-hit HP-deficit constraint.

### General Severance-source path

Tensura's `DamagingHandler` also listens to its living post-damage event. When
`TensuraDamageHelper.isSeveranceDamage(source, target, false)` is true, it calls
the same native `increaseSeveranceAmount` storage method with the event damage
times Tensura's configured `severanceMultiplier`. A constant-pool/call-site
scan of the installed artifact found no third native caller of
`increaseSeveranceAmount`: the other call sites are `EffectStorage` itself and
the enchantment `SeveranceDamageEntity`.

This provides both installed design conventions: a general Severance-tagged
damage path based on the post-damage event amount, and the enchantment path
whose explicit `multiplyOriginalDamage` mode is based on the original arrow
callback amount.

### Exact `ignoreDefence` behavior

`ignoreDefence` is narrowly named but mechanically precise. In
`SeveranceDamageEntity.postDamage`, `true` skips only this expression:

```text
candidate = min(candidate,
                max(0.5, maxHP - currentHP - existingWound))
```

It does not:

- alter or bypass the physical `Entity.hurt` call;
- restore damage removed by Tank, armor, Dementor, or Adaptive;
- change Adaptive source identity, memory, count, rank, or factor;
- bypass `SkillUtils.shouldCancelSeverance` or the `no_severance`/Suppressor gate;
- bypass `amount`/`severanceCap`;
- bypass Severance Protection;
- replace native storage or lifetime; or
- modify Regenerate or healing callbacks.

After the skipped clamp, the ordinary native storage method still applies. If
the resulting wound ceiling falls below current HP, that storage method itself
attempts a separate native `tensura:severance` ceiling-enforcement damage. This
is an important consequence: `ignoreDefence` can leave the physical arrow hit
fully native, but it is not guaranteed to leave total HP loss equal to that
physical hit.

The codec requires an `ignoreDefence` value, but an exhaustive extracted-JAR
search found the identifier only in `SeveranceDamageEntity.class` and the one
installed Severance enchantment JSON. That JSON is false. No installed native
datapack effect or construction enables `true`; there is therefore a supported
code path but no active installed gameplay use from which to infer balance or
authorization.

## W1 explicit answers

1. **Exactly where does Adaptive influence stored wound?** Adaptive reduces the
   physical value in L2's `POST_MULTIPLICATIVE` layer before realized HP loss.
   The later native HP-deficit clamp observes the smaller missing-HP budget and
   limits the amount offered to wound storage.
2. **Direct or only through realized HP deficit?** Indirect only. Adaptive does
   not change Tensura's `callbackDamage`, candidate formula, or storage object.
3. **What does native Severance conceptually track?** The enchantment computes
   potential from original pre-L2 integer arrow damage, then normally grants
   only the portion supportable by the post-hit unallocated HP deficit. It is a
   hybrid of original-damage potential and post-defense storage authority, not
   purely one or the other.
4. **Other native precedents?** Yes. The enchantment itself explicitly uses
   original damage and a capped multiplier. The separate general
   Severance-source handler uses its post-damage event amount. Both use the same
   native storage; no third installed wound-increase caller was found.
5. **What does `ignoreDefence` do?** It skips only the HP-deficit clamp before
   native storage, with all gates, candidate caps, protection, storage, ceiling,
   and lifetime behavior intact.
6. **Is it used natively?** The installed runtime contains the code/codec path,
   but no installed data enables it.
7. **Under what mechanic/context?** None active in this artifact. It is a field
   of the `tensura:after_damage` `SeveranceDamageEntity` codec; the sole packaged
   Severance instance sets it to false.
8. **Can native wound differ from realized HP loss?** Yes, narrowly. Even the
   normal path has a `0.5` free-deficit floor, so a qualifying candidate may
   store up to that floor after a very small delivered hit. The dormant
   `ignoreDefence=true` path can differ much more, after which native storage
   may enforce the lower ceiling with `tensura:severance` damage. The existence
   of that capability is architectural precedent, not evidence that TNO may
   enable it or a balance value.

## W1 conclusion

The 1x-64x proportional prototype plateaued because it enlarged a candidate
that was already non-limiting. Repeated-source Adaptive geometrically reduced
realized physical HP loss; the unchanged native HP-deficit clamp then admitted
only the same tiny free deficit (frequently its 0.5 floor). Any W2 candidate
must therefore address the semantic relationship between eligible wound
potential and that native clamp. Increasing the pre-L2 eligible contribution
again cannot answer the question.

W1 makes no prototype recommendation. In particular, the unused
`ignoreDefence` field cannot simply be toggled: W2 must account for native
ceiling-enforcement damage, source integrity, the absence of a packaged true
use, and whether a narrower eligible-only semantic can still be expressed
through the native callback and storage.

## W2 candidate semantic architectures

### Shared notation and hard constraints

W2 evaluates semantics, not balance. For one accepted hit:

- `D` is the one combined physical integer passed to `Entity.hurt` and later
  supplied unchanged as Tensura's native callback amount;
- `E` is only the post-round eligible Severance portion of `D` (native +3 plus
  its existing Curve-C delta), excluding ordinary Royal Arrow base;
- `K = clamp(D_dementorOut / D, 0, 1)` is the observed combined survival ratio
  through Tank/armor and Dementor;
- `E_preA = E * K` is the eligible share at the boundary immediately before
  Adaptive;
- `A_native` is L2's own Adaptive factor for the unchanged `arrow` source key;
  and
- `W_native` is Tensura's unmodified post-clamp amount offered to native
  storage.

`E_preA` is an allocation of the observed native wall, not restored physical
damage. It intentionally remains after Tank and Dementor. A future production
design would need to prove this allocation against nonlinear boundary cases;
W2 authorizes only a development diagnostic.

All candidates are rejected if they need another physical `DamageSource`, a
spoofed source key, an Adaptive memory reset, TNO-owned wound state, direct HP
subtraction, Regenerate modification, generic heal cancellation, a fabricated
Tensura event, global defense bypass, or base-arrow scaling.

### Ranked result

| Rank | Candidate | Semantic assessment | Gate result |
|---:|---|---|---|
| 1 | C — partial Adaptive recovery for wound credit only | The narrowest candidate capable of addressing the proven limiter while preserving a nonzero Adaptive penalty. It negotiates only the eligible share after Tank/Dementor. | **Pass for development prototype** |
| 2 | B — full pre-Adaptive eligible wound credit | Source-safe and mechanically expressible, but full recovery makes Adaptive irrelevant to the eligible wound quantity. Useful only as W3's capability extreme, not as a preferred architecture. | Conditional diagnostic only |
| 3 | A — current native semantics | Maximally native and safe, but R5 falsifies practical viability because its HP-deficit clamp remains the limiting boundary. | Safe but mission-failing |
| 4 | E — full native `ignoreDefence` semantic | Has real codec/code precedent, but no packaged true use. Applied literally, it credits the whole combined callback (including ordinary base) and may invoke native ceiling-enforcement damage. | Reject as too broad |
| 5 | D — pre-Dementor/pre-Adaptive credit | Removes both decisive L2 reducers from wound potential and lacks an installed semantic boundary that justifies doing so. | Reject |

### Candidate A — current native semantics

Formula:

```text
W_offer = min(0.5 * D, max(0.5, maxHP - HP - existingWound))
```

This preserves every native authority. It also preserves the exact R5
plateau: enlarging `D` did not enlarge late wound once repeated Adaptive made
the free HP deficit the smaller operand. A is retained as the mandatory
control but cannot solve the stated architecture problem.

### Candidate B — pre-Adaptive Severance wound credit

B leaves the physical path untouched and derives wound-only credit from
`E_preA`. It is expressible without writing storage directly by narrowly
intercepting the final HP-deficit-clamp result inside the existing native
`SeveranceDamageEntity.postDamage` callback, then allowing that same callback
to invoke `increaseSeveranceAmount`.

A safe bounded expression would be:

```text
eligible_postA_wound = 0.5 * E_preA * A_native
eligible_preA_wound  = 0.5 * E_preA
extra                = eligible_preA_wound - eligible_postA_wound
W_offer_B            = min(nativeCandidate, W_native + max(0, extra))
```

This is not a second hit, damage restoration, or source-key change. However,
it fully removes Adaptive from the recovered eligible wound portion. B is
therefore retained only as the `RW=1` diagnostic capability ceiling for C.

### Candidate C — partial Adaptive recovery for wound credit only

C keeps L2's actual physical result and Adaptive state exactly native and
defines a separate diagnostic factor only for eligible wound potential:

```text
A_wound = A_native + RW * (1 - A_native)
eligible_extra = 0.5 * E_preA * (A_wound - A_native)
W_offer_C = min(nativeCandidate, W_native + max(0, eligible_extra))
```

`RW=0` is the exact native control. `RW=1` is B's capability extreme. A
semantically viable later candidate must use `0 < RW < 1`, so repeat count
continues to make Adaptive-on wound smaller than Adaptive-off wound. W2 does
not choose such a value.

The expression preserves the normal native amount first, adds only the
eligible recovery, and never exceeds Tensura's own `0.5 * D` candidate. Tank
and Dementor stay in `E_preA`; ordinary base is absent from
`eligible_extra`; Severance Protection still applies afterward. The physical
amount, source, and L2 memory are never touched.

Like every architecture that stores more wound than the immediate free HP
deficit, C may cause `EffectStorage.setSeveranceAmount` to use Tensura's own
`tensura:severance` ceiling-enforcement damage. That source is not a second
physical arrow hit and is not created by TNO, but W3/W4 must explicitly count
it, prove no recursion, and reject the architecture if it produces duplicate
physical delivery or unsafe re-entry.

### Candidate D — pre-Dementor/pre-Adaptive credit

D would derive the eligible quantity before both nonlinear Dementor and
Adaptive. It would also have to ignore Tank/armor if placed before the complete
defensive wall. That is neither required by the W1 causal finding nor
supported by an active native Tensura use. It would erase too much legal L2
identity and is rejected without prototype.

### Candidate E — literal native ignore-defence behavior

Literal `ignoreDefence=true` is mechanically narrow inside Tensura but
semantically broad for this integration. It skips the clamp for the entire
`0.5 * D` candidate, so ordinary Royal Arrow base contributes to the bypassed
wound credit. No installed native data enables the mode, and its native
ceiling enforcement can produce additional nonphysical HP loss. The field is
useful precedent that native wound potential may be separated from immediate
deficit; it is not authorization to toggle the installed enchantment or emulate
the whole behavior.

## W2 decision gate

Candidate C passes all seven requirements for a minimal development-only
prototype, subject to fail-closed scoping and explicit runtime validation:

| Requirement | Why Candidate C passes |
|---|---|
| One physical source | It observes the existing `minecraft:arrow` call and creates no physical source. Native storage may independently use its existing nonphysical `tensura:severance` ceiling source, which must be measured. |
| Actual physical damage fully native | No L2 modifier or `Entity.hurt` amount is changed. |
| Adaptive state fully native | Source key, memory, rank, count, and factor are read-only inputs. No reset or spoof occurs. |
| Ordinary Royal Arrow base unchanged | Only `E`, the existing Severance eligible portion, contributes to the added wound credit. |
| Existing callback/storage | The final offer remains inside `SeveranceDamageEntity.postDamage`; native `increaseSeveranceAmount` performs the write. |
| Regenerate unchanged | No tick, configuration, heal amount, or `LivingHealEvent` path is modified. |
| Defensible Severance relationship | Tensura already separates original-damage candidate from realized-deficit authority and implements an explicit clamp-skipping mode. C is narrower: it partially negotiates only the existing eligible Severance contribution and remains capped by the native candidate. |

W3 is authorized for Candidate C only. The prototype must be inactive in
production, exact-native at `RW=0`, and fail closed outside an explicitly
flagged accepted Severance research scope. W3 begins with `RW=0` and `RW=1`
only to prove mechanical no-op/capability; neither is a production proposal.

## W3 development-only capability prototype

Status: **complete; mechanical gate passed; W4 authorized**.

The prototype intercepts only the second `Math.min(float, float)` result in
the installed `SeveranceDamageEntity.postDamage` callback: the native
HP-deficit-clamped offer. It adds Candidate C's eligible-only amount, caps the
result by the native candidate, and then returns control to the same native
callback. Tensura's own `increaseSeveranceAmount` remains the only wound
writer. The physical arrow event, Tank, Dementor, Adaptive, source key,
Adaptive memory, Regenerate, and Royal Arrow base are not modified.

The scope is fail-closed: it requires a non-production environment, the
explicit `adaptive_wound_*` research mode, an active per-case scope, a Royal
Arrow projection registered from the classified S7 Severance bow, an
initialized L2 target wall, the native `arrow` source, and the native callback.
Any missing boundary returns the unmodified native offer. State is a
thread-local case scope and is removed at case cleanup; there is no persistent
combat state.

### Official capability matrix

The strict capture contains six cases and 60 real Royal Arrow releases: S7 at
Lv600, Lv800, and Lv1000, each with the accepted legal L2 profile at `RW=0`
and `RW=1`. APO is `NONE`; Apothic crit chance is fixed to zero in this
development harness so it cannot confound the physical boundary. Every case
completed with 10 hits, 10 native callbacks, 10 native wound writes, and zero
case errors.

| L2 level | RW | Physical total | Stored wound total | Candidate-C eligible extra | Native ceiling damage |
|---:|---:|---:|---:|---:|---:|
| 600 | 0 | 3.667819 | 6.754883 | 0 | 0.311523 |
| 600 | 1 | 3.674805 | 11.213660 | 4.458778 | 7.539062 |
| 800 | 0 | 3.669047 | 6.754883 | 0 | 0.041016 |
| 800 | 1 | 3.737871 | 11.361327 | 4.541991 | 0.758789 |
| 1000 | 0 | 3.667831 | 6.754883 | 0 | 3.086914 |
| 1000 | 1 | 3.733394 | 11.256564 | 4.437228 | 0 |

The small cross-case physical-total variation is native runtime variation
between fresh targets, not Candidate-C output. The decisive per-hit invariant
is exact within `0.001`: the observed physical result equals the recorded
native post-Adaptive result, and the prototype never writes the physical
amount. Each hit retains exactly one `minecraft:arrow` physical event with
`minecraft:is_projectile`, no magic tag, one wall trace, and no duplicate
projectile delivery. `D` remained the callback amount, ordinary Royal Arrow
base remained `2.4` (post-round base `8`), and only the existing S7 eligible
Severance contribution `E=12` was available to Candidate C.

At `RW=0`, all 30 hits had `A_wound=A_native`, `eligible_extra=0`, and
`W_offer_C=W_native` within `0.001`. The native Adaptive count advanced 1
through 10 and its factor remained exactly `0.5^(count-1)`. The stored wound
increment was the native offer after the observed Severance Protection
multiplier of 1.0. Thus `RW=0` is the exact no-op control at the intercepted
boundary.

At `RW=1`, physical damage still used the same native Adaptive factor while
the wound-only factor became 1.0. All three levels stored more wound than
their corresponding control: approximately 11.21-11.36 versus 6.75, with
4.44-4.54 of explicitly attributed eligible extra. This proves the required
mechanical separation without restoring physical damage or writing wound
state from TNO.

### Native ceiling-enforcement result

The native `tensura:severance` ceiling source was fully observed. Across the
six cases it emitted 197 entity-less incoming attempts during the 20-tick hit
observation windows. Vanilla hurt admission allowed 22 actual Pre/Post damage
applications totaling 11.737305; the remaining attempts did not pass the
native hurt admission/invulnerability path. `RW=1` accounted for 105 attempts,
11 admitted applications, and 8.297852 damage; `RW=0` accounted for 92, 11,
and 3.439453 respectively. This variability is why ceiling damage is reported
separately from stored wound and physical arrow damage.

For every attempt, incoming amount before and after the observable L2 boundary
was identical and uncancelled. The source had neither source nor direct entity,
so the installed L2 profile produced no visible transformation. Actual Pre and
Post amounts matched. No event was tagged or counted as the physical arrow;
there remained one physical arrow event per release. No extra native wound
callback, duplicate wound write, TNO wall re-entry, recursion, unexpected L2
bypass, or unexpected Tensura bypass occurred. The ceiling source is therefore
native Tensura enforcement rather than fabricated TNO damage and does not
violate the one-physical-hit architecture in this capability matrix.

### W3 decision gate

Candidate C is mechanically valid for further development-only testing. The
strict extractor validates the formula, source identity, native callback and
storage ownership, Adaptive rank/count/factor, exact `RW=0` offer parity,
`RW=1` eligible-only capability, Protection-adjusted storage, ceiling-source
flow, one-arrow integrity, and zero recursion/bypass. This result does not
select a production `RW` and does not authorize production implementation.
W4 may now test a small intermediate diagnostic value against paired trait
controls.

W3 checkpoint: `e032f1837b137171cafbba6de3711f9a1802fd5c`.

## W4 trait-identity matrix

Status: **complete capture; decision gate failed; W5 is not authorized**.

W4 used only the arithmetic midpoint `RW=0.5`, explicitly as a diagnostic
between W3's proven endpoints rather than a proposed balance value. At S7,
Lv600/Lv800/Lv1000 each ran the accepted legal profile and four exact
single-trait-removed controls: no Tank, no Dementor, no Adaptive, and no
Regenerate. Removed budget was not reassigned. The result is 15 complete
cases, 150 real Royal Arrow hits, zero errors, and a strict validated JSONL.

| Level | Profile | Physical | Final wound | Net HP movement | Regen demand / actual / denied |
|---:|---|---:|---:|---:|---:|
| 600 | accepted | 3.665912 | 8.955547 | 8.955078 | 49.541992 / 0 / 49.541992 |
| 600 | no Tank | 4.932803 | 10.766729 | 10.766602 | 67.969727 / 0 / 67.969727 |
| 600 | no Dementor | 7.133584 | 13.926117 | 13.925781 | 85.680664 / 0 / 85.680664 |
| 600 | no Adaptive | 18.365018 | 18.369141 | 18.369141 | 101.030273 / 0 / 101.030273 |
| 600 | no Regenerate | 3.659654 | 8.933073 | 8.932617 | 0 / 0 / 0 |
| 800 | accepted | 3.659314 | 8.911363 | 8.911133 | 49.400391 / 0 / 49.400391 |
| 800 | no Tank | 4.958140 | 10.825224 | 10.825195 | 68.733398 / 0 / 68.733398 |
| 800 | no Dementor | 7.205404 | 14.085970 | 14.085938 | 92.287109 / 0 / 92.287109 |
| 800 | no Adaptive | 18.365018 | 18.369141 | 18.369141 | 101.030273 / 0 / 101.030273 |
| 800 | no Regenerate | 3.664249 | 8.933883 | 8.933594 | 0 / 0 / 0 |
| 1000 | accepted | 3.673965 | 8.956120 | 8.956055 | 54.719727 / 0 / 54.719727 |
| 1000 | no Tank | 4.932132 | 10.766609 | 10.766602 | 62.574219 / 0 / 62.574219 |
| 1000 | no Dementor | 7.100120 | 13.875509 | 13.875977 | 92.117188 / 0 / 92.117188 |
| 1000 | no Adaptive | 18.620926 | 18.625000 | 18.625000 | 103.460938 / 0 / 103.460938 |
| 1000 | no Regenerate | 3.671416 | 8.987325 | 3.671875 | 0 / 0 / 0 |

### Traits that retained identity

- **Tank passed.** At every level the accepted profile delivered less physical
  damage and stored less wound than the otherwise-identical no-Tank control.
- **Dementor passed.** Accepted final wound was 8.91-8.96, versus 13.88-14.09
  without Dementor. Candidate C therefore did not move credit ahead of
  Dementor.
- **Adaptive passed.** Accepted final wound was 8.91-8.96, versus 18.37-18.63
  without Adaptive. With Adaptive removed, `A_native=A_wound=1` and the
  diagnostic extra was exactly zero. With Adaptive present, native count still
  advanced 1-10 and wound credit remained smaller. Candidate C did not erase
  Adaptive at `RW=0.5`.

### Regenerate gate failure

Regenerate did not retain the required defensive disadvantage in this matrix.
The 12 Regenerate-bearing cases produced exactly 120 native tick attempts and
120 callbacks, retained the correct rank throughout, and requested 928.545898
HP. Native Severance denied all 928.545898; actual healing was exactly zero.
The no-Regenerate cases produced zero attempts and zero healing.

Consequently, Regenerate-on was not consistently harder for the attacker than
Regenerate-off. Accepted net HP movement was slightly *greater* at Lv600,
slightly smaller at Lv800, and materially greater at Lv1000. The independently
timed native ceiling source and vanilla hurt admission make short-window net HP
non-monotonic, but they do not change the decisive fact: Regenerate delivered
no observed healing benefit in any `RW=0.5` case. The W4 rule requires a
material defensive disadvantage, not merely the continued presence of a trait
and callback, so the gate fails.

### W4 safety result

All 150 hits retained exactly one physical `minecraft:arrow` source and one
native wound callback/store, with unchanged projectile tags, Royal Arrow base,
Tank/Dementor/Adaptive physical output, and no magic classification. There
were zero duplicate physical events, recursion, unexpected L2 bypasses, or
unexpected Tensura bypasses. Native ceiling enforcement remained an
entity-less `tensura:severance` path; 97 actual applications totaled 64.339844
damage and never re-entered the TNO wall or created a second wound callback.
SHP movement was zero in every case.

The prototype is scoped only to a registered staged Severance Royal Arrow and
the existing native callback. It cannot act on Magic, Holy, Soul, Elemental,
Energy, APO, matching Resistance, or generic damage. A Nullification or
Arena/Repelling/Teleport veto that prevents the physical hit also prevents the
native after-damage callback, so the negotiation fails closed; W4 did not
fabricate forced veto profiles or repeat the already accepted trait matrix.

## Current architecture decision

- Candidate C is **mechanically valid** by W3.
- Native ceiling enforcement is **structurally safe** in W3/W4: native-owned,
  separately measured, entity-less, nonphysical, and nonrecursive.
- Tank, Dementor, and Adaptive remain **meaningful** at diagnostic `RW=0.5`.
- Regenerate is **not meaningfully defensive** in the isolated W4 path because
  its entire healing demand is denied.
- HP viability is not evaluated by this short trait matrix; net HP behavior is
  non-monotonic under native ceiling timing.
- SHP viability remains absent: no tested Severance wound path moved SHP.
- Production architecture authorization: **NO**.
- W5 sustained viability authorization: **NO**, because its W4 prerequisite
  failed.
- A new calibration task is not yet justified. The exact next task is an
  architecture/protocol decision on how Regenerate is expected to remain a
  defender advantage while preserving native Severance's purpose as a healing
  counter. That decision must precede any new `RW` calibration or W5 run.

No production behavior, Curve C value, Stage threshold, L2 mechanic, native
Tensura mechanic, Royal Bow/Arrow base value, or other family was changed.
