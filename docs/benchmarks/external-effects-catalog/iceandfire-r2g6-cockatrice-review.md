# R2g6 — Cockatrice and Scepter combat

Cockatrice and Scepter combat semantics complete; other Ice & Fire families remain pending.

Static subsection complete. Runtime fixtures unexecuted; no Stage or production implementation.

## Gaze admission

Server Cockatrice.aiStep requires actual target, neither actor nor target Blindness, mutual IafEntityUtil look(.6), target not Gorgon.isBlindfolded and !shouldMelee. Protected helper supplies distance-adjusted angle, same-level collider LOS<=128 and statue exclusion. shouldMelee is true at distance<4, COCKATRICE_TARGETS type, Blindness or statue blacklist refusing conversion. shouldStareAttack(distance>5) only sets display target, not a five-block payload requirement. Gorgon helper includes native blindfold/Blindness/BLINDED plus installed Tensura IMMUNE_TO_GORGON and qualified AbnormalNull immunity. Scepter does NOT call this helper. First admitted gaze tick only starts staring; later admitted ticks apply payload. A broken gaze does not alone clear stored staring; blindness/melee/no-target do. No invented warmup80 damage gate: client attack-duration is visual.

## Gaze payload

strength=other Cockatrices in directional box.expandTowards(config chickenSearchLength each axis) sharing the SAME current target and mutually looking at it, plus1 on HARD. Friend count does not require their staring flag, blindness or blindfold eligibility. Each payload tick attempts Wither10ticks amp2+min(1,strength), Slowness10ticks ampmin(4,strength), Nausea200ticks amp0; all returns ignored. If strength>=2 and target.tickCount%40==0, separately requests ownerless minecraft:wither strength-1; hurt return ignored. setLastHurtByMob(this) is independent bookkeeping, not DamageSource attribution. Native Wither effect requests ownerless wither1, ignores hurt result and returns true; tick interval40>>amplifier (10 for amp2,5 for amp3), using remaining-effect duration. Reapplication/refresh and i-frames can alter actual event cadence; never claim one hit per nominal interval without runtime evidence.

## Melee control

doHurtTarget chooses Bite or Jump animation when not staring and returns false, no parent damage. aiStep Bite tick7 distanceSquared<8 requests int ATTACK_DAMAGE (base5) mob_attack direct=causing=Cockatrice. Jump tick>10 and distanceSquared<4 repeats same request and independently adds target horizontal velocity normalized*.8 + Cockatrice motion*.2 (no Y), if horizontal distance>=1e-4. No extra LOS at these frames and no hurt-success gate for motion. EntityAIAttackMeleeNoCooldownGoal merely delegates ordinary MeleeAttackGoal.tick when target present; its name does not prove cooldown removal. No second Stage multiplier on native attributes, animation or control.

## Target control

Native nearest goal random1/20, non-PEACEFUL, parent search, different exact class; wild nonowner Player allowed, other target requires !owner and canMove. Registration filters creative/spectator, tame hostile exclusions and target/chicken tags. Wild aggro-look Player goal uses forCombat range25 plus looking/follow-range predicate; continuation requires look .4 and assigns actual target. Owner/hurt retaliation and chicken alarm are separate legitimate paths. ServerEvents Player attack or onLivingSetTarget for CHICKENS signals nearby Cockatrices (horizontal configured range, vertical10), excluding same-owner/Cockatrice attacker and creative/owned Player. aiStep captures target before peaceful/allied/sit clearing; that local may survive this invocation. Do not bypass real target acquisition in positive controls.

## Taming

Wild admitted gaze at Player increments persistent tamingLevel1 even if effects/hurt rejected; replaces numeric tamingPlayer entity ID with current Player. At level>=1000 resolves that ID, tames if Player, clears attack/taming/target IDs. TamingLevel is serialized and has no gaze-break reset in native callers; progress is not a damage amount and is not per-player UUID keyed. Taming changes future allegiance, not victim HP/SHP. Commands/home/egg breeding details excluded.

## Defense heal

Cockatrice.hurt multiplies input5 if causing entity type SCARES_COCKATRICES, then rejects the identical cached inWall source object, otherwise parent hurt. canBeTurnedToStone=false excludes gaze/Head/Scepter acquisition. Owner hand feed with HEAL_COCKATRICE and HP<max calls heal8 then consumes1 even creative; NAME_TAG/LEAD/POISONOUS_POTATO excluded from this hand branch. AI dropped tagged food requires movable/injured, chance/search/navigation and distanceSquared<1, consumes1 then heal8. Native LivingHealEvent/positive HP/max clamp remain; consumption is independent of heal acceptance. Base maxHP config and armor2 remain native.

## Scepter acquisition

Player use starts72000tick BOW use and returns PASS. onUseTick has no whole-method server guard. Entity ray32 from eyes with bounding expansion1 and pick-radius inflated candidates; initial filter pickable, no target Blindness, no refusing statue blacklist, Player or living DragonUtils.isAlive. No block clip here, no blindfold/earplug/IMMUNE_TO_GORGON tag helper and no team predicate. Selection accumulates candidates in query order as best distance shrinks, without removing earlier farther candidates; origin-contained/shared-root branches differ from Gorgon Head. A selected dead Living aborts whole onUseTick before attackTargets. Each eligible Living is added to caster MiscData UUID list if absent, marking attachment dirty. Actual damage still needs maintained LOS below.

## Scepter maintained

attackTargets resolves stored UUID via ServerLevel or ClientLevel. Resolved Living needs one-way IafEntityUtil look(.2) and neither removed; applies Wither40ticks amp2 each tick. Every caster.tickCount%20==0 increments Item-instance specialWeaponDmg then requests ownerless minecraft:wither2 independently of effect/hurt acceptance. This does not recheck initial Blindness/blacklist/pickable/alive/team predicates or32block range; helper still supplies LOS/not-statue/128 bound. Failed maintained look/removal removes UUID; unresolved/nonliving UUID remains. Same vanilla Wither1 passive ticks remain distinct from explicit2 pulse.

## Scepter lifecycle

Reuse protected Siren MiscData serialized/synced copyOnDeath attachment authority. releaseUsing applies accumulated specialWeaponDmg as durability loss then resets it and clears caster list; specialWeaponDmg belongs to shared Item instance, not ItemStack or caster. Iterator removal/clear do not markDirty. checkScepterTarget removes resolved Living if removed or lacking positive-duration Wither; whole-JAR census shows its sole gameplay-external consumer is client living rendering, not server tick cleanup. Unresolved/nonliving entries persist. finishUsingItem adds20tick cooldown; releaseUsing itself does not. Multiple casters/stacks, reconnect/copyOnDeath and canceled use require future native tests; no fix here.

## Compatibility

No direct SHP writes. Preserve native effect admission/cures, vanilla wither damage immunity and normal hurt hooks, including installed Tensura/L2 processing; ownerless sources must remain ownerless. Effect rejection does not suppress explicit pulse or taming. Existing Gorgon helper mixin protects Cockatrice gaze only, not Scepter acquisition. Stage eligibility for damage/real healing amounts is recorded, but ownerless Stage policy is not invented. No multiplier on effect duration/amplifier, lock list, taming, durability, friend count or incoming x5 native susceptibility.

## Exclusions

Beam/animation rendering, sounds, egg acquisition/breeding, home location, ordinary follow/wander and item lore excluded. Client Scepter cleanup retained only because it changes attachment state visibility. Static review only; every listed fixture remains unexecuted.

## TNO integration decisions

- **Cockatrice and Scepter Wither damage**: NUMERIC_SCALABLE, VANILLA_ROUTED, ADMISSION_GATED. Stage: yes; Once at each native target.hurt amount: explicit Cockatrice strength-1 pulse, Scepter2 pulse, or vanilla Wither1 tick. Preserve ownerless attribution; do not also multiply status amplifier/duration.
- **Cockatrice gaze debuffs and pounce motion**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional value; Native Slowness/Nausea, gaze and horizontal displacement stay native.
- **Cockatrice bite/pounce HP damage**: NUMERIC_SCALABLE, VANILLA_ROUTED, ADMISSION_GATED. Stage: yes; Native aiStep target.hurt amount once, after native attribute selection and before damage admission.
- **Combat gaze taming/allegiance**: BINARY, CUSTOM_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional value; Taming threshold is native progress, not HP damage.
- **Cockatrice petrification immunity and incoming susceptibility**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional value; Keep incoming native x5 and cached inWall veto; generic incoming Stage layer already owns damage.
- **Cockatrice native heal8**: NUMERIC_SCALABLE, VANILLA_ROUTED, ADMISSION_GATED. Stage: yes; Once at native heal(8) request through LivingHealEvent, retaining HP clamp and consumption order.
- **Scepter native lock and shared durability budget**: CUSTOM_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional value; Preserve UUID admission/lifecycle and cost; damage already assigned separately.

[Machine-readable packages, native paths and future fixtures](iceandfire-r2g6-cockatrice.json). Validation reproduces new witnesses, checks significant call order/amounts, preserves accepted records and prior evidence, runs five tooling tests and diff checks. No whole-mod completion claim.

Exact next task: R2g7: Death Worm and Cyclops combat damage, grab/explosion/projectile/eye defenses and legitimate delivery. Then remaining creatures and equipment, whole-mod combat closure/dedup/promotion. No runtime/L2/Stage/production.
