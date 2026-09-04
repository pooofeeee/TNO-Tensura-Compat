# Phase 6 Severance / L2 Regenerate research

## Scope and status

This branch is research-only. It does not authorize or implement a permanent
Severance change, a generic anti-heal mechanic, or any change to the completed
Magic/Holy production path.

Checkpoints R1 and R2 are complete. Direct inspection and controlled installed-
runtime evidence establish conclusion **A: native Severance clearly constrains
L2 Regenerate**. The interaction is a hard vanilla-HP healing ceiling equal to
`maxHP - wound`; it is not a proportional reduction in Regenerate's nominal
rate. The R2 decision gate therefore authorizes the research-only R3 physical-
wall decomposition, but no production Severance change is authorized.

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

The injection does **not** capture or test the boolean returned by
`Entity.hurt`. Therefore the installed callback does not, at this layer,
require a successful `hurt` result, HP loss, or SHP loss. Runtime admission can
still be prevented by the native target checks below, and the stored amount is
bounded by the target's post-call HP deficit when `ignoreDefence` is false.
That distinction is retained for R2/R3 rather than inferring admission from a
zero aggregate-damage row.

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
