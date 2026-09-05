# Phase 6 Regenerate / Adaptive / wound architecture research

## Scope and checkpoint status

This branch is post-Phase-6, pre-Phase-7 research. It does not change production
combat behavior, Curve C, Magic/Holy production, Royal Arrow base damage, L2
traits, Regenerate, or Tensura's stored wound. It begins from
`571736da7c4de3e30038b0778a5351da6ace3b26`.

| Checkpoint | Status | Result |
|---|---|---|
| W1 — exact wound/Adaptive boundaries | Complete | Adaptive reaches stored wound only through realized HP and Tensura's HP-deficit clamp; the native callback amount remains the pre-L2 integer arrow amount. |
| W2 — candidate architectures | Not started | Pending W1 checkpoint review. |
| W3 — development-only prototype | Not authorized | Requires a W2 candidate that passes all seven decision-gate invariants. |
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
