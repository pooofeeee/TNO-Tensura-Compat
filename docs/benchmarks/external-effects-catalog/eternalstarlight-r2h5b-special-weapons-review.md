# R2h5b — Eternal Starlight special weapons and shields

Remaining special melee, two projectile weapon modifiers, native shields and concentration/motion modifiers. Armor remains separate.

Static subsection complete. Runtime fixtures remain unexecuted; no Stage or production implementation.

## Crescent delivery

Crescent Spear use -> Player release at>=10 ticks and downward5-block COLLIDER/Fluid.ANY clip non-MISS, or creative. Push look vector by trident-spin-enchantment strength+1.75, server durability1, dash markertrue, startAutoSpinAttack20 with ATTACK_DAMAGE*1.5 (attribute missing fallback8), cooldown20; onGround additionally move up1.2. No projectile is created. Native Player.attack reads spin amount and stored spin weapon while spin flagtrue, then ordinary strength/enchantment/item/critical/sweep processing; native source player_attack direct=causing=Player. Scale final per-victim native hurt once, not the stored spin amount or ordinary attack attribute as an additional multiplier.

## Crescent order

Exact loader LivingEntity.checkAutoSpinAttack first calls Player.doAutoAttackOnTouch -> attack on the first Living in swept box, sets spin ticks0, then reverses velocity. ES AFTER-setDeltaMovement injection performs AABB3 nearby-Living attacks with TargetingConditions.DEFAULT and shouldHarm, resetting attackStrengthTicker to ceil(delay) before EACH attack. The spin flag/amount/item are only cleared at native method end, so these extra attacks still use stored spin amount. ES separately calls the same helper at HEAD when horizontalCollision; despite method name checkAutoSpinAttackTail this is a HEAD injection. Helper checks stored item exact Crescent Spear, not the dash marker. Both hooks can run in one invocation, repeated attempts including original victim can meet ordinary iframe rejection; no forced victim iframe reset. Helper ends with owner invulnerableTime=max(existing,10) and markerfalse, not an atomic one-shot damage guard. Native primary and helper admission differ: helper has shouldHarm, native touch does not gain that extra predicate. These are source-proven attempts, not a claim all cause HP loss.

## Hammer

#HAMMERS adds1 to native LivingEntity.getKnockback return. PlayerMixin forces the first boolean local (enough attack strength f2>.9) true before sprint check, AFTER strength already scaled damage; it does not set actual f2 or force every critical. Other critical predicates/events still apply. Neo CriticalHitEvent handler requires event currently critical, #HAMMERS, HammerItem instance and actual getAttackStrengthScale(.5)>.9, then performs splash BEFORE primary target.hurt. Splash nearby Living in target block AABB.inflate2 with TargetingConditions.DEFAULT requests native player_attack .75*current ATTACK_DAMAGE. No explicit shouldHarm or primary-target exclusion; native targeting and hurt admission remain. Only hurttrue adds vertical .4*max(0,1-KB resistance). Parent rejection does not retroactively prevent splash; splash may change primary iframe outcome. Single Stage point per independent final splash hurt, plus ordinary primary path, with no additional scale on .75 or knockback.

## Scythe

#SCYTHES mixin temporarily forces the same enough-strength local true at Player.walkDist read for sweep eligibility; restores saved value at getItemInHand inside eligible sweep branch (if branch is not entered that restore does not execute). It does not replace actual attack strength f2, critical-blocks-sweep, sprint knockback, onGround/movement or item ability. NeoScytheItem and NeoPetalScytheItem expose DEFAULT_SWORD_ACTIONS. Exact loader fires SweepAttackEvent then primary hurt; only successful primary enters native sweep loop. Sweep excludes player, original victim, allies and marker armor stands, uses reach limit, and requests native player_attack enchanted(1+SWEEPING_DAMAGE_RATIO*f)*f2. Thus low charge can admit a weaker sweep, not automatic full-strength AoE. Scale each final native damage once; preserve reach, events and admission.

## Greatsword block

Greatsword use fails when damage>=max-1, otherwise begins BLOCK use. LivingMixin forces isBlocking true immediately when using #GREATSWORDS, bypassing ordinary minimum-use delay only. Native isDamageSourceBlocked still rejects BYPASSES_SHIELD, piercing AbstractArrow and missing/behind source position; loader shield event may modify final blocking. On positive shield durability callback PlayerMixin wears max(int(amount/5),1), stops using and applies cooldown100 before native shield body. Native body then sees stopped use; this is not a second custom HP event. disableShield HEAD is canceled only while current use stack is tagged greatsword. Keep binary admission, durability and cooldown native; no Stage value.

## Flowglaze concentration

Incoming handler requires source.directEntity Living, current weapon #FLOWGLAZE_WEAPONS, victim object identity==stored target, weapon ItemStack object identity==stored weapon and level>=4 to multiply by1.25. Player success branch calls handleFlowglazeWeaponAttack just before ItemStack.hurtEnemy; native part-parent mapping is not substituted for the mixin original argument, so original non-Living part cannot accrue here. Non-Player direct-Living path updates in Post handler. Same target+stack increments level capped4 and timestamp; changed target/stack stores new identities with level0. In plain sequential successful Player hits first sets0, fifth reaches4, earliest sixth Incoming gets bonus. Tick clears only when level>0 and elapsed>100 or weapon identity changed; level0 is not cleared by that branch. No requirement that each arbitrary direct-Living source be a melee DamageType, and no new effect/source. Preserve 1.25 and apply future Stage once at parent final HP request.

## Warhammer pendant

Incoming handler source.directEntity Living and getAccessories(current weapon) containing Warhammer Pendant multiplies amount by min(1+MOVEMENT.length*1.5,2); it is not based on causing entity alone or final HP loss. EntityMixin.move captures second local movement vector at second setPos invocation, replaces stored movement on a different tick and accumulates same-tick callbacks. Whole-JAR state census shows the only MOVEMENT/LAST_MOVEMENT_UPDATE writes in that mixin; no automatic reset for a later tick without that callback. A stale stored vector can therefore remain available. Native source and multiplicative modifier stay intact; parent final HP Stage only, no independent pendant multiplier.

## Bows

FlowglazeBow native Bow factory marks created projectile. Server entity tick applies only airborne AbstractArrow: while saved extra float<3, baseDamage+=.1 and extra+=.1f each tick. Preserve float comparison rather than asserting an exact3 clamp; embedded ticks pause accrual. Damage still uses native final arrow speed/base/crit/enchantment and admission. UnrealiumCrossbow native factory on AbstractArrow adds .6+oldPierce*.1 to base then sets pierce127; shoot callback multiplies all projectile velocity by1.5. Server arrow tick with exact Unrealium weapon enforces pierce127 including inGround. Firework route receives velocity only, no arrow base/pierce. Scale final native arrow/firework per-victim hurt once, not base, velocity or pierce separately. BloodBow release delegates super with no native lifesteal/self-damage callback; ordinary bow route only.

## Flowglaze shield

Entity.deflection RETURN override: Living blocking exact Flowglaze Shield, horizontal normalized projectile-to-defender vector dot yaw-only defender view<0 -> AIM_DEFLECT. This precedes ordinary projectile onHit only for projectile classes that call native hitTargetOrDeflectSelf. That native method calls deflect(mode,defender,existingOwner,false); server deflect changes trajectory and calls setOwner(existingOwner), so collision reflection RETAINS original owner, unlike player-attack redirect. It records lastDeflectedBy to avoid repeated same-defender deflect; non-NONE still bypasses onHit. Preserve custom projectile deflect overrides/return and classes that bypass this helper as runtime distinctions. No separate damage or reflection Stage value; later legitimate projectile hurt is scaled once with its actual source.

## Glacite shield

Neo LivingShieldBlockEvent handler checks getOriginalBlock(), not final getBlocked()/blocked damage; then exact active Glacite Shield, source.directEntity Living and canFreeze -> frozen ticks+100 capped300. Loader event runs after earlier hurt admission when requested amount>0 and computes original block from normal source direction/bypass/pierce rules. Another listener can alter final blocking; the ES callback itself does not require final HP success or positive final blocked amount. Source-causing Living with non-Living direct projectile does not qualify. Native freeze control has no independent Stage quantity; retain frozen eligibility and later native freeze damage processing.

## Additional deliveries

MoonringGreatsword native successful postHurtEnemy server and per-owner special cooldown absent: four rings centered on victim, increment=min(width*.75,3), each radius=(i+1)*increment/count=max(round7radius,5), createThorn height40/delayi*7, cooldown125. This is another actual producer of reviewed mode0 LunarThorn POISON4; reuse es:lunar_thorns, no duplicate damage package. TentacleSpikeItem supplies TentacleSpike to existing Whip flow; lifespan10, range=interactionRange+7, no new hit override; reuse es:whip_damage with existing native ray, charge, source and hurt-return gates. These additional paths are explicitly linked for final dedup/promotion.

## Scope

Fixed native crit/sweep/attack/armor modifiers, movement, control, pierce, cadence and item resources are not separately Stage-scaled. Ordinary melee/ammunition final HP requests retain native immunity, Resistance/enchantment/armor, loader events, source identity and future L2 processing. Rendering, crafting/repair, tool mining/tilling and particles are short exclusions. This section makes no runtime or integration-implementation claim; armor/material procs remain next.

## TNO integration decisions

- **Ordinary greatsword/hammer/scythe and BloodBow HP**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Once at native final melee or ammo hurt; no new BloodBow drain.
- **Crescent Spear native spin touch and collision AoE**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Once at each Player.attack final hurt, after spin/charge/enchantment; do not scale stored spin again.
- **Hammer critical-event splash**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Once per independent .75*ATTACK_DAMAGE native player_attack hurt.
- **Scythe native sweep admission and HP**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Once per final native sweep hurt; native charge/ratio unchanged.
- **Greatsword immediate blocking and recovery**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional multiplier; Retain native modifier/control; existing parent damage path receives at most one Stage multiplier.
- **Flowglaze concentration modifier**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional multiplier; Retain native modifier/control; existing parent damage path receives at most one Stage multiplier.
- **Warhammer motion damage modifier**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional multiplier; Retain native modifier/control; existing parent damage path receives at most one Stage multiplier.
- **Flowglaze airborne arrow base accrual**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Once at native final arrow hurt after velocity/base/critical calculation.
- **Unrealium projectile speed and arrow piercing**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Once at native final arrow/firework hurt; no additional base/speed multiplier.
- **Flowglaze Shield collision reflection**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional multiplier; Retain native modifier/control; existing parent damage path receives at most one Stage multiplier.
- **Glacite Shield original-block freezing**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional multiplier; Retain native modifier/control; existing parent damage path receives at most one Stage multiplier.

[Machine-readable packages, delivery paths and future fixtures](eternalstarlight-r2h5b-special-weapons.json). Exact archive/method witnesses and targeted semantic assertions are reproducible. No whole-mod completion claim.

Exact next task: R2h5c: remaining armor, material Post procs, accessories/attributes and resource modifiers; then spells/crests and remaining non-boss creatures/hazards, whole ES caller closure/promotion/full validation, then Bosses Rise automatically. Do not repeat completed sections.
