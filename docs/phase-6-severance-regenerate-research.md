# Phase 6 Severance / L2 Regenerate research

## Scope and status

This branch is research-only. It does not authorize or implement a permanent
Severance change, a generic anti-heal mechanic, or any change to the completed
Magic/Holy production path.

Checkpoints R1, R2, and R3 are complete. Direct inspection and controlled
installed-runtime evidence establish conclusion **A: native Severance clearly
constrains L2 Regenerate**. The interaction is a hard vanilla-HP healing ceiling
equal to `maxHP - wound`; it is not a proportional reduction in Regenerate's
nominal rate. R3 isolates the endgame physical wall and narrowly authorizes a
development-only R4 eligible-contribution prototype. No production Severance
change or permanent coefficient is authorized.

## Authoritative installed runtime

| Component | Installed artifact | Declared version | SHA-256 |
|---|---|---:|---|
| Tensura | `tensura-neoforge-2.0.1.1.jar` | 2.0.1.1 | `C12EC9AAA1488C662EDE52B4BD0150EC114E7BDAC32AF20C0E723612DD79D8B9` |
| L2 Hostility | `l2hostility-3.0.18.jar` | 3.0.18 | `8821952B49C5E9B1980B4D7CCECBCFA8E957204D39AC62D8D40DFF34FAAAF780` |
| L2 Library | `l2library-3.0.8.jar` | 3.0.8 | `26038E30873CF505BC289E28F9DCF084561B8A4929B294DD0552BA5E52505DD6` |
| L2 Complements | `l2complements-3.1.3.jar` | 3.1.3 | `94E34372F6C0EE1D36FD18EEDA5F2C6676800D32D63AA250C194472C7196B8A7` |

The live server configuration used by the development runtime has
`severanceRemoveSec = 300` and `regen = 0.01`.

## R1: exact native Severance semantics

### Damage and callback path

The installed `data/tensura/enchantment/severance.json` defines Severance I as
both:

- a `minecraft:damage` additive contribution of `+3.0`; and
- a `tensura:after_damage` victim effect whose amount is `0.5`, whose
  `severanceCap` is `0.5`, whose `multiplyOriginalDamage` is true, and whose
  `ignoreDefence` is false.

For an `AbstractArrow`, Tensura's `MixinAbstractArrow` invokes
`TensuraEnchantmentHelper.doAdditionalAfterDamage` immediately after the
arrow's normal `Entity.hurt(source, damage)` invocation. It passes the local
integer projectile `damage`, which is the combined arrow amount after
enchantment modification, projectile velocity, and the native integer ceiling.
The callback uses the weapon retained by the projectile and the original arrow
`DamageSource` context. It does not create a second hit or a second damage
source.

The injection does **not** capture or explicitly test the boolean returned by
`Entity.hurt`. Static inspection alone therefore did not prove that the
callback required a successful `hurt` result. R3 resolves the effective woven
runtime behavior: all 140 calls that returned true reached the callback, while
all 580 calls that returned false before L2 `DamageData` did not. The callback
is therefore effectively downstream of successful hurt admission in this
installed runtime, even though it does not read the boolean itself. Stored
amount remains bounded by the target's post-call HP deficit when
`ignoreDefence` is false.

The current TNO production mixin preserves the same single physical arrow
source. It changes only the already-eligible native `+3` contribution before
the same velocity/ceiling calculation; Royal Arrow base physical damage and
Apotheosis output remain outside Stage scaling.

### Wound admission and magnitude

`SeveranceDamageEntity.postDamage` attempts storage only when all of the
following hold:

1. the affected entity is a `LivingEntity`;
2. the target does not have infinite materials;
3. `SkillUtils.shouldCancelSeverance(target, null)` is false; and
4. `severanceRemoveSec` is nonzero.

With the null source used by the enchantment effect,
`shouldCancelSeverance` rejects an entity in the `tensura:no_severance` entity
type tag or a target with mastered Suppressor. Its physical-conversion check
cannot trigger because this call passes no damage source.

At Severance I the unprotected candidate increment is:

`candidate = min(0.5, 0.5) * callbackDamage = 0.5 * callbackDamage`

Because `ignoreDefence` is false, the actual increment passed to storage is:

`min(candidate, max(0.5, maxHP - currentHP - existingWound))`

Severance Protection then reduces that increment by 10% per enchantment level.
The remaining increment is additive. Every application refreshes the removal
timer to the configured value, including an application whose computed
increment is zero.

### Stored state, lifetime, and effects

Every `LivingEntity` receives Tensura's ManasCore-backed
`tensura:effect_storage`. Its serialized fields include:

- `severance`: floating-point accumulated wound amount; and
- `severanceRemove`: integer remaining lifetime.

The storage ticks the lifetime once per server second. Positive values count
down; when the prior value is 1 the amount is cleared. Zero disables storage at
the effect entry point, while negative removal time does not count down. With
the live value 300, a refreshed wound lasts approximately 300 seconds.

The native effective health ceiling is:

`severanceMaxHealth = LivingEntity.getMaxHealth() - severanceAmount`

Writing a wound does not modify the vanilla maximum-health attribute. If
current HP is already above the new ceiling, `EffectStorage.setSeveranceAmount`
immediately attempts `tensura:severance` damage for the excess. Player natural
regeneration and several Tensura self-heal paths also consult the same ceiling.

Most importantly, Tensura's NeoForge `LivingHealEvent` listener runs at
`HIGHEST` priority. For any positive wound it:

- cancels healing when HP is exactly at the wound ceiling;
- truncates a heal that would cross the ceiling to `ceiling - currentHP`;
- when HP is already above the ceiling, attempts native Severance damage down
  to the ceiling and cancels that heal; and
- leaves a heal entirely unchanged while it remains below the ceiling.

This is a hard HP ceiling, not a proportional reduction of every heal and not a
change to the maximum-health attribute. The stored wound does not directly
modify Spiritual Health, magicules, aura, or any other resource recovery.

## R1: exact installed L2 Regenerate semantics

Installed `RegenTrait.tick(target, rank)` is server-only. Whenever the target's
own `tickCount % 20 == 0`, it calls:

`target.heal(target.getMaxHealth() * regenConfig * rank)`

With live `regen = 0.01`, nominal healing is 4% of vanilla max HP each second
at rank 4 and 5% each second at rank 5. For a 10,000-max-HP target those values
are 400 HP/s and 500 HP/s. Regenerate uses `LivingEntity.heal(float)`, so it
fires NeoForge's `LivingHealEvent` and is directly visible to Tensura's
highest-priority wound ceiling. It heals vanilla HP only; it has no SHP healing
call.

Regenerate itself does not bypass other mods. Its trait admission excludes the
Ender Dragon and requires that the L2 Complements Curse effect be applicable,
in addition to the normal `MobTrait` constraints.

## R1 conclusion and runtime questions

Native Severance is a direct semantic counter to L2 Regenerate: Regenerate can
heal normally below the wound ceiling, but cannot restore the wounded portion
of HP while the wound remains. The maximum absolute healing denied by one wound
is the stored wound amount; the mechanic does not reduce the nominal 4%/5%
per-second rate before the ceiling is reached.

R2 must now prove this exact path in the installed server and quantify:

- rank-4 and rank-5 nominal versus actual healing across multiple cycles;
- identical controls with and without a legitimately created wound;
- HP, SHP, wound amount, and remaining duration for every cycle;
- whether the native heal callback is truncated or cancelled at the ceiling;
- whether the live Royal Arrow wound matches the audited storage semantics; and
- errors, duplicate effects, or unexpected bypasses.

No production value or combat behavior is selected by R1.

## R2: direct installed-runtime interaction

Machine-readable evidence is preserved in the four independently validated
`r2-*.jsonl` captures under
`docs/benchmarks/phase6-severance-regenerate-research/`. Each capture ran in a
fresh server process because repeated Orc Disaster instances in one process can
stop ticking after earlier boss cleanup. Each case contains one catalog, one
case start, six per-event healing rows, one complete case result, and one
complete suite result.

The controlled target is `tensura:orc_disaster`. It is the only accepted
seven-boss Severance benchmark target on which the real Royal Bow / real Royal
Arrow path produced native wound storage. Each case first released ten arrows
from an S0, Apotheosis-free Royal Bow carrying only Severance I; all 40 releases
produced one accepted `minecraft:arrow` event with `minecraft:is_projectile`
and no magic tag. The no-wound cases then used Tensura's native
`EffectStorage.clearSeverance`; wound cases retained the naturally produced
wound. No wound was fabricated.

Orc Disaster has unrelated native 20-HP and 2-HP healing. The development-only
fixture identifies every synchronous heal callback by its call stack, retains
only callbacks from installed `RegenTrait.tick`, and cancels/counts the Orc-
native contaminants. It also resets target age after each accepted tick-20
Regenerate callback, preserving an exact 20-server-tick Regenerate cadence.
This isolation changes neither L2 Regenerate nor production combat code.

| Case | L2 / rank | Max HP | Nominal Regenerate | Initial HP | Native wound at start | Six-cycle actual healing | Final HP | Difference from control |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| R4 control | 600 / 4 | 10,000 | 400 HP/s | 9,000 | 0 | 1,000 | 10,000 | 0 |
| R4 native wound | 600 / 4 | 10,000 | 400 HP/s | 9,000 | 50 | 950 | 9,950 | -50 |
| R5 control | 800 / 5 | 10,000 | 500 HP/s | 8,750 | 0 | 1,250 | 10,000 | 0 |
| R5 native wound | 800 / 5 | 10,000 | 500 HP/s | 8,750 | 50 | 1,200 | 9,950 | -50 |

All 24 Regenerate callbacks were stack-verified as
`RegenTrait.tick -> LivingEntity.heal`, and all occurred at target tick 20.
Below the ceiling, rank 4 continued to request/heal 400 and rank 5 continued to
request/heal 500. The crossing callback was truncated to the remaining distance
to the ceiling; later callbacks were cancelled there. Wound duration counted
down normally from 300 seconds. SHP changed by exactly zero in every case.

Aggregate R2 invariants: four complete cases, 40 accepted real-arrow events,
24 native Regenerate events, zero case errors, zero duplicate damage sources,
and zero unexpected L2 bypasses. The quantitative answer is exact for these
fixtures: a 50-HP native wound denies exactly 50 HP that Regenerate would
otherwise restore. The wound does not reduce the 4%/5% per-second rate before
the ceiling and does not heal or modify SHP.

## R2 decision gate

Native Severance meaningfully counters Regenerate whenever a meaningful wound
can be stored and kept refreshed. The current ten-arrow S0 setup demonstrated
only a 50-HP ceiling reduction, which is negligible beside 400-500 HP/s native
Regenerate, so reliability and achievable wound magnitude through the full L2
physical wall remain decisive. Continue to R3; do not infer that the current
production path has solved sustained endgame Regenerate viability.

## R3: observation-only physical-wall decomposition

The official capture is preserved as
`docs/benchmarks/phase6-severance-regenerate-research/r3-physical-wall.jsonl`
(SHA-256
`99584764DB3428FC9DF64175214E76D3CC2115FFD550B330851CDC2F64172F9B`).
The focused extractor accepted one catalog, 72 case starts, 720 rows, 72 case
results, one complete suite result, and zero error records.

The exact matrix was three levels (600, 800, 1000) by three production Stages
(S5, S6, S7) by eight profiles: accepted strongest legal; no Tank; no
Dementor; no Adaptive; no Tank+Dementor; no Tank+Adaptive; no
Dementor+Adaptive; and no Tank+Dementor+Adaptive. Each case used a fresh L2
attachment and ten real Royal Arrow releases in 200 ticks. Removed trait budget
was left unused. `APO_profile` remained `NONE`, the R3 observer used identity
modifiers only, and Q/RD/RA were all zero.

Every release retained one `royalvariations:royal_arrow`, one physical
`minecraft:arrow` source, and `minecraft:is_projectile`; none acquired the
magic tag. All 720 rows preserved the native Severance `+3`, separate Royal
Arrow base contribution, current production Stage delta, original source,
unique projectile UUID, and exact profile ranks. There were zero second
sources, duplicate events, recursion events, unexpected L2 bypasses, unexpected
Tensura bypasses, or case errors. Tank is not described as an L2 damage
modifier: its observed profile change is armor/toughness 46/20 to 26/0, before
the Dementor observation boundary.

### Hurt admission and callback split

Only 140 of 720 releases (19.4444%) entered L2 `DamageData` and returned
`Entity.hurt=true`. Every one of those 140 invoked the native Severance callback
exactly once and stored a positive wound. The other 580 releases (80.5556%)
produced their one uncancelled `LivingIncomingDamageEvent`, but returned false
before L2 `DamageData`; none ran Dementor or Adaptive, invoked the native wound
callback, changed HP/SHP, or stored wound. This is an observed pre-`DamageData`
hurt-admission gate in the real Orc Disaster path. R3 does not identify it as
Tank, Dementor, or Adaptive, and does not bypass or alter it.

The captured field named `final_physical_after_L2_pipeline` is the
`LivingDamageEvent.Pre` observation used by the existing harness. When Adaptive
applies its later post-multiplicative factor, the authoritative Adaptive result
is `Adaptive_native_result` and the realized result is `final_HP_delta`; the
document does not misrepresent the earlier event value as the post-Adaptive HP
loss.

### Profile results

All nine first releases for every profile were admitted, so the last column is
the cleaner magnitude comparison. Ten-release totals also include the separate,
non-monotonic hurt-admission gate and must not be read as pure trait effects.

| Profile | Admitted/stored | Admission rate | Wound total | Wound/release | Wound/admitted | Mean first-release wound |
|---|---:|---:|---:|---:|---:|---:|
| Accepted | 25/90 | 27.7778% | 26.842773 | 0.298253 | 1.073711 | 1.942600 |
| No Tank | 18/90 | 20.0000% | 27.323242 | 0.303592 | 1.517958 | 2.449219 |
| No Dementor | 13/90 | 14.4444% | 41.395508 | 0.459950 | 3.184270 | 4.377279 |
| No Adaptive | 17/90 | 18.8889% | 22.302734 | 0.247808 | 1.311926 | 1.820421 |
| No Tank + Dementor | 14/90 | 15.5556% | 55.234375 | 0.613715 | 3.945312 | 5.547743 |
| No Tank + Adaptive | 17/90 | 18.8889% | 31.306641 | 0.347852 | 1.841567 | 2.667535 |
| No Dementor + Adaptive | 17/90 | 18.8889% | 39.928711 | 0.443652 | 2.348748 | 3.531576 |
| No Tank + Dementor + Adaptive | 19/90 | 21.1111% | 64.915039 | 0.721278 | 3.416581 | 5.493815 |

### Causal answers

1. **Tank:** in the clean first-release no-Dementor/no-Adaptive pair, retaining
   Tank left 61.0714%-67.6692% of the physical amount entering the Dementor
   boundary (mean 64.3045%). Its measured mean reduction was 35.6955%. This is
   armor/toughness behavior, not an L2 `DamageModifier` callback.
2. **Dementor:** across 77 admitted rows carrying Dementor, output/input averaged
   0.489553 (range 0.314901-0.530615), a mean 51.0447% reduction after the
   armor/Tank boundary. The nonlinearity makes low inputs vary; it is not a
   constant resistance percentage.
3. **Adaptive:** a fully admitted accepted Lv600/S5 sequence recorded source
   key `arrow`, counts 1 through 10, and factors 1, 1/2, 1/4, 1/8, 1/16, 1/32,
   1/64, 1/128, 1/256, and 1/512. It is the dominant repeated-same-source
   magnitude suppressor once a hit has been admitted.
4. **Magnitude versus reliability:** magnitude collapses through the
   multiplicative sequence Tank then Dementor then repeated Adaptive. Reliability
   is dominated by the separate pre-`DamageData` gate: 580/720 releases never
   reached any of those L2 modifiers or the Severance callback.
5. **One trait or combination:** no single trait explains both effects. Tank and
   Dementor reduce the first admitted hit, Adaptive compounds repeated admitted
   hits, and the independent native admission gate controls most misses.
6. **Removing Tank alone:** it did not materially improve aggregate reliability
   or wound/release (0.303592 versus accepted 0.298253), although the mean first
   admitted wound rose from 1.942600 to 2.449219. The clean control demonstrates
   Tank's real 35.6955% mean magnitude reduction.
7. **Removing Dementor alone:** mean first admitted wound rose to 4.377279 and
   wound per admitted hit to 3.184270. Its aggregate admission rate fell because
   the separate gate varied between fresh cases, so the aggregate rate is not a
   causal Dementor result.
8. **Removing Adaptive alone:** it prevents the 1/2-per-count repeated-source
   decay, but this capture's aggregate wound/release was 0.247808 because only
   17/90 releases passed the separate gate. Its first hit is expected to be
   close to accepted because Adaptive count 1 uses factor 1.
9. **Removing pairs:** first-release means were 5.547743 without Tank+Dementor,
   2.667535 without Tank+Adaptive, and 3.531576 without Dementor+Adaptive. Their
   aggregate wound/release values were 0.613715, 0.347852, and 0.443652,
   respectively; again, admission-count differences prevent treating those
   aggregate totals as perfectly paired trait coefficients.
10. **No-three diagnostic ceiling:** all nine first releases were admitted and
    stored 5.277344-5.555664 wound from 19-20 pre-L2 physical input. The maximum
    wound observed anywhere in R3 was 7.376953. This is meaningful relative to
    accepted first-hit values but remains tiny against 10,000 HP and 400-500
    HP/s Regenerate.
11. **Very small final damage:** yes. In the clean accepted Lv600/S5 sequence,
    Adaptive reached factor 0.001953125 on release ten; every release still
    invoked the callback and stored wound. Releases three through ten stored the
    native 0.5 minimum. A tiny admitted result does not itself suppress the
    callback.
12. **What constrains wound:** for admitted hits, the native
    `0.5 * callbackDamage` candidate was 9.5-10.5 and was never limiting.
    Observed wound averaged 2.208922 (range 0.5-7.376953), with 42 rows at the
    0.5 floor and no SHP delta. The controlling magnitude is the actual vanilla
    HP deficit created by the L2-reduced admitted physical result, subject to
    the native 0.5 floor. The separate pre-`DamageData` hurt-admission gate is
    the controlling reliability limit because it prevents the callback
    altogether.

## R3 decision gate

R3 narrowly authorizes R4 as development-only research:

- meaningful native wound exists when the measured wall is relieved;
- the existing `SeveranceStageScaling` decomposition isolates Royal Arrow base
  physical damage from the eligible native Severance contribution before their
  one shared physical source; and
- a prototype can negotiate only that eligible contribution before the same
  `Entity.hurt` call, leaving one `minecraft:arrow` source and all native L2 and
  Tensura processing downstream.

This authorization has a hard limit. A modifier placed only at an L2
`DamageData` boundary cannot affect the 580 releases rejected before that
boundary. R4 must neither restore post-L2 damage nor fabricate a wound, split
the source, buff ordinary Royal Arrow base damage, or bypass Tank globally. It
must establish a diagnostic ceiling first and fail closed if eligible-only
pre-hurt negotiation cannot improve real admission while retaining Tank,
Dementor, Adaptive, and native wound storage. No permanent production value is
selected by R3.
