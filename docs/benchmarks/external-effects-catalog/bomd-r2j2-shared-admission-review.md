# R2j2 — Bosses of Mass Destruction shared admission

Shared native hurt/effect admission, HP phase monitoring, damage memory, capped healing and scheduler semantics; concrete boss families remain PARTIAL.

Static review only. Future runtime fixtures remain unexecuted; whole Bosses of Mass Destruction review is PARTIAL.

## Native authority

Nineteen BOMD class witnesses plus installed CerbonsAPI-NeoForge-1.21-1.3.0.jar SHA5c750762b31ab79127df6f455351fe79793d8c2b41e1a0f94b335a5a1123534d, patched Minecraft1.21.1/NeoForge21.1.244 and JDK21 Arrays list evidence establish these shared contracts. Thirteen whole-artifact constructor/helper caller methods are indexed. Boss-specific hitbox/shield geometry, attacks and equipment remain pending; no unrelated library archaeology.

## Damage order

BaseEntity.hurt captures a handler reference and EntityStats wrapper. Server: all beforeDamage hooks run first; then handler.shouldDamage(this,source,amount) short-circuits super.hurt when false; afterDamage runs server-side with the original source and requested amount and the boolean result even when admission rejected or super returned false. shouldDamage itself is not server-gated. With no handler, it directly uses super.hurt. The wrapper stores the LivingEntity, not an immutable HP snapshot: getHealth/getMaxHealth read current native values. This layer does not multiply damage, rewrite sources or directly subtract HP.

## Composite

CompositeDamageHandler preserves supplied order for all beforeDamage and all afterDamage callbacks. shouldDamage stops at the first false handler. Thus a rejecting inner handler does not prevent the outer before/after notifications. Actual installed order: Lich phase detector, targetless-attacker callback, LichMoveLogic, DamageMemory; Obsidilith move logic, ShieldDamageHandler, DamageMemory; Gauntlet hitbox helper, goal handler, DamageMemory; VoidBlossom HP detector, composite hitbox handlers, DamageMemory. Concrete handler predicates belong to their boss family. No new TNO scale at the wrapper or each handler.

## Effect filter

Exactly two installed constructors create EffectsImmunity: Obsidilith and Gauntlet, passing MobEffects.WITHER.value() and POISON.value() into a MobEffect array. The filter stores Arrays.asList(values) but canBeAffected calls !list.contains(effect.getEffect()). Patched MobEffectInstance.getEffect returns Holder. Arrays$ArrayList.indexOf compares the supplied holder via equals to each stored MobEffect. Patched Holder.Reference.equals requires identity or another Holder of reference kind with the same key; the MobEffect value is neither. Therefore these ordinary registered effects are NOT excluded by this filter, including Poison and Wither. The code never unwraps the candidate holder. This is a proven native Holder/value mismatch, not an intended immunity to preserve by inference. BaseEntity uses this filter result directly, bypassing its super.canBeAffected fallback while configured. No repair is implemented or authorized.

## External effect admission

The filter mismatch is not an unconditional force-apply bypass. Patched LivingEntity.addEffect calls CommonHooks.canMobEffectBeApplied before inserting/updating an effect. That posts NeoForge MobEffectEvent.Applicable; APPLY admits, DEFAULT calls virtual canBeAffected, DO_NOT_APPLY rejects. Tensura/L2 or other listeners may still reject through this path. Native parent tag checks (immune_to_infested, immune_to_oozing, ignores_poison_and_regen) are in the superclass branch and are skipped by configured filter delegation; actual pack tags/traits are runtime fixture work. Other two bosses have no installed EffectsImmunity constructor here and inherit the fallback unless their own family changes admission.

## Phase detection

StagedDamageHandler is native HP-phase bookkeeping, unrelated to TNO Stage. beforeDamage saves HP/MAX_HP; afterDamage recomputes HP ratio and compares MathUtils.roundedStep(ratio,milestones,false) for the two values. It ignores result and calls its Runnable once when the selected milestone differs; not once per crossed threshold. Installed rounding sorts ascending and picks the first step STRICTLY GREATER than ratio, otherwise the final step. Thus equality at0.75 maps to1.0, just below0.75 maps to0.75; equivalent rules hold at0.5/0.25. The comparison is inequality, not a downward-only test, so a change upward within the before/after interval can also trigger. An unchanged rejected hit does not change phase. Quarter milestone lists are native constants. Exact phase actions remain boss review.

## Damage memory

DamageMemory.afterDamage records only result==true AND source.getEntity()!=null AND requested amount>4 (strict); it stores that original request, source object and entity.tickCount. It does not measure final HP loss, absorption, resistance or actual damage events. Its initial history item is amount0/fellOutOfWorld/age0 and is not an attack. Installed Lich/Gauntlet capacity5, Obsidilith/VoidBlossom10; CerbonsAPI adds newest and removes oldest on overflow. Do not multiply the history amount separately or invent owners for null causing entities.

## Retarget

TargetSwitcher consumes this history: causing attacker must be LivingEntity, sensed LOS, strict distanceSquared<FOLLOW_RANGE squared, entity.canAttack true, and ageWhenDamaged+600>=current tick. Group by causing entity, sum recorded requested amounts, choose maximum; if selected target differs and random.nextInt(2)==0, set target. No damage is created and no unconditional player rewrite occurs. Whole-JAR calls from Lich/Obsidilith/Gauntlet/VoidBlossom move logic are indexed; their scheduling remains family review. DamagedAttackerNotSeen separately invokes its callback when current target null and causing entity Living, regardless hurt result, with no LOS test despite its name. Installed Lich callback further requires ServerPlayer before teleport action; teleport eligibility is next.

## Idle heal

CappedHeal server tick requires getTarget()==null; LichUtils.cappedHeal also requires isAlive. Native request = clamp(nextStrictMilestone(HP/MAX_HP)*MAX_HP - HP -1,0,healingStrength), invoked only if positive through entity.heal. Lich/Obsidilith/VoidBlossom install it in their server tick pipeline; file values are0.2/0.5/0.5. At exact threshold, strict rounding selects the next threshold, whereas just below it heal stops one HP before that threshold. This is heal/event processing, not setHealth. Shared helper also has a VoidBlossomBlock caller, whose distinct native delivery is deferred to that family. Gauntlet has no CappedHeal constructor despite its config idle-heal field; do not claim delivery solely from config.

## Heal scaling

Future numeric scaling belongs ONCE on healingStrength at the shared clamp upper-bound input, leaving target-null/alive predicates, milestone selection and one-HP gap native. This produces min(native positive gap,scaled healingStrength). Multiplying the already capped result could cross the native cap; do not do that. Never also multiply config, heal callback and global healing event. Native LivingEntity.heal keeps NeoForge healing hooks and native alive checks; healing callbacks can change the eventual result. No implementation is made.

## Scheduler

BaseEntity updates preTickEvents before its client/server tick hooks and super.tick, then postTickEvents afterward. CerbonsAPI EventScheduler moves its pending HashSet into its queue, clears pending, calls shouldDoEvent only on tickSize divisibility, then doEvent, removes events by shouldRemoveEvent, increments scheduler ticks. TimedEvent.tickSize=1; shouldDoEvent tests age++>=delay and !cancel, shouldRemoveEvent tests cancel OR age>=delay+duration; default duration1. With delay d>=0 and no cancellation, callback first runs on the (d+1)th update after admission to the queue. Events added during a callback wait for the next scheduler update. Pending HashSet does not promise sibling ordering. Cancellation does not require HP damage success unless the actual supplier says so. Preserve native duration/counts; actual world-scheduler delivery and concrete suppliers remain family review.

## Compatibility and scope

Native damage identity and admission remain intact. Incoming rejection, hurt boolean, HP loss, secondary effects, retargeting and scheduled actions are distinct observations. Shared review introduces no runtime tests, compatibility fix, Stage or production edit. Rendering, animation-only/camera, loot/acquisition and general utility are excluded; server actions scheduled by animations remain combat-relevant.

- **Native before/admit/after handler contract**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Native binary admission, source-aware bookkeeping, phase state or scheduler; no independent scalable payload.
- **Native Holder/value effect filter and external admission**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Native binary admission, source-aware bookkeeping, phase state or scheduler; no independent scalable payload.
- **Native strict HP milestone monitor**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Native binary admission, source-aware bookkeeping, phase state or scheduler; no independent scalable payload.
- **Native damage memory and causing-attacker retarget**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Native binary admission, source-aware bookkeeping, phase state or scheduler; no independent scalable payload.
- **Native milestone-capped boss healing**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Once on healingStrength at LichUtils.cappedHeal clamp upper-bound input; preserve native milestone gap and heal callback.
- **Native delayed combat callback scheduling**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Native binary admission, source-aware bookkeeping, phase state or scheduler; no independent scalable payload.

[Machine evidence, packages and native paths](bomd-r2j2-shared-admission.json).

Exact next task: R2j3: BOMD Night Lich native hurt/teleport admission, missiles/comets, volley/rage/minion delivery and real source/secondary callbacks. Reuse R2j1 factory/config and R2j2 scheduler, phase, capped-heal and damage-history contracts. Then Obsidilith, Nether Gauntlet, Void Blossom and combat equipment. Continue automatically while quota is healthy; static only.
