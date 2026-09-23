# R2i5a — Bosses Rise Yeti defense and phase ordering

Yeti native admission, raw predicted HP gates and frozen corpse lifecycle; outgoing payloads next.

Static review only. Future runtime fixtures remain unexecuted; whole Bosses’ Rise review is PARTIAL.

## Admission order

YetiEntity.hurt first reads enrageFlag. If6 AND server level: discard and returntrue without HP damage, source/amount/type predicate or inherited hurt. Otherwise flags0 and1 each reject unless BYPASSES_INVULNERABILITY. Next, unconditionally for every source including bypass: flags3/4 reject; exact FALL,DROWN,FALLING_ANVIL,WITHER,WITHER_SKULL reject; DATA_SPAWN_ANIMTIME must<=0; DATA_HIT_ANIMTIME must<=13; DATA_GROUNDSMASH_ANIMTIME must<=0 or>=119. Thus bypass tag bypasses ONLY first iced/emerging tests, not all Yeti defenses. Only then modify amount and evaluate raw HP transitions. Do not confuse hurttrue statue removal or scripted lethal state with a native HP damage event.

## Projectile reduction

After admission, direct entity instanceof AbstractArrow multiplies amount by.15, then source exact TRIDENT multiplies by.3. These are sequential independent tests. Installed vanilla ThrownTrident constructors invoke AbstractArrow, so a native thrown trident meets both ->.045 of incoming amount, not merely .3. This is different from Dragon causing-entity check. Non-AbstractArrow projectile sources receive no .15 modifier solely because of is_projectile tag. Preserve original source; modifiers are native defense and NOT a second Stage point.

## Hit lockout

When admitted hit finds hit counter==0 on server, Yeti sets27 and DATA_HIT_TICK=gameTime BEFORE any inherited hurt. Server tick decrements positive counter and clears marker to-1 at0; values27..14 reject incoming even if original hit later failed normal damage admission. Values13..1 allow calls without restarting counter. Counter marker read by renderer is cosmetic, not separate admission rule. No hitboolean gate protects these writes. Legacy spawn counter default0 guarded separately; do not synthesize a positive counter as ordinary delivery.

## Raw lethal branch

After native projectile reductions, getHealth()-amount<=0 selects native DEATH handling before armor, Resistance, Neo IncomingDamage/hurt or actual HP subtraction. If not already DEATH, selects death112, resolves kill-score Living first from direct, then causing, then causing OwnableEntity owner; native server death-loot/advancement callback runs once. Then setHealth(.1) and returntrue, no super.hurt. Native death state therefore can trigger despite a downstream mitigation/cancel rule that would have rejected ordinary HP damage. This is installed behavior to preserve and runtime-test, not permission to fix it. setState refuses all changes after DEATH; server tick at timer112 setsflag6, noAI, hides bar; subsequent native server hurt removes frozen corpse. It does not need another HP threshold. Native shouldCancelDeath=false, so shared legacy lethal restoration is NOT Yeti normal death mechanism. If inherited downstream amount becomes lethal despite smaller precheck, normal downstream death remains possible; fixture later, no invented event.

## Enrage and ultimate

For nonlethal predicted damage in flag2 with proposed HP ratio<=.5, applies native Slowness200 and Resistance200 for200ticks to all Living in BB.inflate32 excluding self; no LOS/team/Player restriction; then flag3 before super.hurt. Native addEffect/Applicable and Roll veto remain. On current state timer done, baseTick flag3->ENRAGED state200/flag4; tick increments groundsmash counter whiletimer<=200 and flag5 at>=180; baseTick alternative ifflag4 andstatechanged also sets5. During groundsmash1..118 local hurt rejects independently; ending tick outside ENRAGED clearscounter0. No HP restoration/clamp to50%. Else-if current ratio>.2 and proposed ratio<=.2 and usedUltimate==0 selects ICE_BARRAGE and sets1 before super.hurt. The50% branch takes priority, so one large nonlethal crossing both thresholds does not also select ultimate. Later pattern can select barrage if used>0; outgoing repeat lifecycle deferred R2i5b. All these transitions can occur even inherited hurt returnsfalse. Incoming thresholds, timers, effect amplifiers and resource flags need no Stage scaling.

## Initialization

Default flag0 iced, usedUltimate0, hit counter inherited0, hit marker-1. finalizeSpawn applies config HP250,armor5,attack18 defaults (base attributes250/2/18) and fills HP; non-STRUCTURE spawn setsflag2 and barvisible. STRUCTURE keeps frozen/default initialization unless native saved state differs. YetiEvents @EventBusSubscriber onBreakBlock for server player breaking exact Blocks.ICE finds first Yeti flag0 within blockAABB.inflate10, selects INTRO193/flag1, cancels break and replaces that ice withair. Intro removes surrounding native ice/barriers at scheduled frames and setsflag2 at frame190 (frame=timer-2, hence timer192); combat acquisition details omitted. Event registration annotation is static evidence, not runtime certification. No mutation of player world or boss run here.

## Traits persistence

checkFallDamage is empty; getDeltaMovement returnsZERO whileflag0. Native canCollideWith ignores its own owner-matched IceSpikeEntity only. Yeti clears positive ticksFrozen both baseTick and server tick; it does not override canFreeze/fireImmune and its entity registration is not fireImmune. This is repeated freeze-counter clearing, not proof that every FREEZE source is rejected. Native Living freeze eligibility still applies; no new immunity invented. Knockback resistance1. Saves usedUltimate,is_enraged,GroundsmashAnimtime plus inherited state/timer/HP; read of extra fields guarded by BossPhase. Hit timestamp not saved and only render-relevant. Genuine saved/native spawn cases are future fixtures; do not fabricate tags to activate legacy routes.

## Dormant death counter

baseTick contains separate positive DATA_DIE_ANIMTIME decrement, clears attack/hit/groundsmash and requests self PLAYER_ATTACK999 atcount1. However default is0; only native positive writer BossCancelDieProcedure is reached via shared onDamageTaken only when shouldCancelDeath, which Yeti returnsfalse. Native Yeti DEATH state uses its own112timer and does not set legacy counter. Therefore this legacy999 route is not promoted as normal delivered Yeti defeat; retain as conditional saved-counter code only, no synthetic test setup. Scope-specific census pins actual writers/callers, not a guessed behavior from method names.

## State dispatch

Tick state switch runs only when not intercepted by navigation.getPath nonnull AND !path.canReach AND current target nonnull AND state!=LEAP_SMASH. That branch requests LEAP_SMASH and stops navigation instead. Therefore exact intro/enrage/death tick callbacks also require switch entry; a retained unreachable path can skip a scheduled frame. DEATH setState rejects replacement but does not remove this outer dispatch predicate. Preserve this as a native future navigation/transition fixture; do not assume timer alone guarantees corpse transition.

## Scope

This section closes only defense, native phase/death and combat initialization. Outgoing melee/barrage/ice callbacks are present in the tick witness but remain R2i5b semantic work. Rendering, sounds, loot contents, advancements and detailed ice-shell coordinates are excluded after identifying combat callbacks. No runtime/L2/Stage/production changes; whole Bosses Rise remains PARTIAL.

- **Yeti native admission and projectile reductions**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Incoming native modifiers, admission/state/resources or scripted HP reset; no independent outgoing HP payload.
- **Yeti raw lethal death/corpse lifecycle**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Incoming native modifiers, admission/state/resources or scripted HP reset; no independent outgoing HP payload.
- **Yeti predicted HP enrage and ultimate resources**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Incoming native modifiers, admission/state/resources or scripted HP reset; no independent outgoing HP payload.
- **Yeti combat initialization, traits and persistence**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Incoming native modifiers, admission/state/resources or scripted HP reset; no independent outgoing HP payload.

[Machine evidence, packages and native paths](bossesrise-r2i5a-yeti-defense.json).

Exact next task: R2i5b: Yeti native outgoing melee/barrage, Ice Spike/cluster/projectile, Glacial Shove and Frozen Skeleton combat payloads. Defense/phase ordering is complete; reuse R2i5a, roll and shared evidence. Then Sandworm, Kraken/cannon, equipment and whole-mod closure.
