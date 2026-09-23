# R2g3b — Siren Flute and animation attacks

**Flute and bite/pull subsection complete; Ice & Fire remains PARTIAL.** Song and Frozen are reused unchanged. No runtime tests or production changes.

## Scope

Siren song remains separately complete atR2g3a. This subsection closes the native Siren Flute love attachment and Siren bite/pull animation combat. It does not turn Siren song into the Flute effect or mark the entire Ice & Fire mod complete. All findings are static installed-JAR contracts, with no runtime measurements.

## Flute acquisition

Registered siren_flute uses SirenFluteItem, durability200. Native use gets the used-hand stack, calls startUsingItem and unconditionally adds900tick item cooldown, then casts a32block eye/view segment through entity bounds in an expanded search box. It does not clip world blocks or require LOS. Candidate must be nonnull/pickable, not a LivingEntity with Blindness, not a BlacklistedFromStatues returning false, and either Player or LivingEntity passing DragonUtils.isAlive. That helper rejects dead-model dragons, IDeadMob.isMobDead and StoneStatue; it is not a generic current-HP test. Pickability and normal use admission still apply. The unusual blindness/statue guards are preserved.

## Flute selection

Candidates intersect inflated-by-pick-radius AABBs; nearest segment distance wins, with origin-contained and shared-root-vehicle branches preserved. Shared-root candidate is selected only when current best distance is0. On a selected LivingEntity, MiscData.get(target).setLoveTicks(200) overwrites the timer and marks dirty; used stack hurtAndBreak2 specifies EquipmentSlot.MAINHAND even for offhand use; cooldown900 set again. Sound plays and result is PASS even after mutation. The method has no explicit server-only guard. Native ordinary item use/cooldown checks remain; no cast-success or damage-result gate is invented.

## Attachment route

MiscData.get -> transformed ComponentManager.getMiscData -> NeoForge ComponentManagerImpl -> entity.getData(MISC_DATA). Actual IceAndFireNeoForge constructor registers IafAttachments.REGISTRY. MISC_DATA builder uses MiscData factory, CODEC serialization, PACKET_CODEC sync and copyOnDeath. CODEC stores loveTicks/lungeTicks/targetedByScepters and reconstructs the timer; only love semantics are reviewed here. NeedUpdateData.markDirty sets a boolean; isDirty consumes/reset it. setLoveTicks and zero-crossing mark dirty; ordinary decrement does not mark every tick.

## Tick entry

Native IafAttachments has EventBusSubscriber/SubscribeEvent on EntityTickEvent.Post; on LivingEntity it calls tickAndSync for MISC_DATA among the four attachments. tickAndSync resolves attachment, calls its interface tick (MiscData bridge delegates LivingEntity overload), then syncs only when isDirty returns true. Exact installed ServerLevel and ClientLevel tickNonPassenger call entity.tick then fireEntityTickPost only when Pre was not canceled. Their tickPassenger paths call rideTick without fireEntityTickPost. Thus this is an eligible-Post-event timer, not a guarantee of200 elapsed ticks for all mounted/unloaded/canceled-tick states; both client/server callback declarations exist. No generic LivingTick callback is substituted.

## Love control

If loveTicks>0, MiscData.tick decrements first. On becoming0 it marks dirty, requests Mob navigation.recomputePath, then returns before pacification. Otherwise a Mob has lastHurtByPlayer=null, lastHurtByMob=null, setTarget(null), aggressive=false and navigation.stop requested, then heart particles. Starting200 yields199 nonzero pacification passes before the zero-crossing pass if no refresh/interruption. Player/other non-Mob recipients get counter/particles but no Mob target/navigation changes. No setNoAi, speed/velocity lock, HP/SHP change, MobEffect, DamageSource or guaranteed prohibition of every attack is implemented. Because this is Post, an AI attack earlier in the tick is not retroactively prevented. Native target-change hooks remain in force.

## Love removal and compat

There is no Siren earplug, SpiritualAttackNullification helper or MobEffect immunity/removal callback in Flute/MiscData love application. Native expiry is the counter reaching0; refresh replaces with200; serialized attachment/copy-on-death declarations preserve the intended data lifecycle rather than converting it to a potion. This finding does not bypass or change any external hook. The whole-JAR consumer census contains no separate damage-cancel or target-acquisition veto based on loveTicks; it must not be advertised as guaranteed pacifism. Other mods/runtime mixin outcomes remain untested.

## Attack entry

Siren registerGoals supplies native MeleeAttackGoal and aggressive Player/AbstractVillager target goals, plus retaliation; protected exact loader melee goal checks attack cooldown, melee reach and sensed LOS then calls doHurtTarget. Siren override chooses pull or bite by nextInt(2), starts that20tick animation if different and returns true unconditionally. It does not call Mob.doHurtTarget, so that return is animation admission rather than proof of damage/enchantment/weapon callback. Song contact/retaliation can provide the target through R2g3a; native AI must execute the real attack route.

## Bite

Earlier Siren.aiStep animation branch at tick5, nonnull current target, squared distance<7 requests hurt(mobAttack(this),current ATTACK_DAMAGE). Base attribute6; actual attribute can differ. Return is discarded. The code does not repeat melee-goal LOS/reach/creative/earplug gates at that animation frame. Standard source has direct=causing=Siren and native mob_attack admission; requested6 base is not guaranteed HP damage. The branch has no explicit side guard; server native hurt ultimately controls server HP. No SIREN_CHARM application is made by this attack.

## Pull

Pull tick5, target nonnull, squared distance<16 requests the same native mob_attack/current attribute and ignores hurt return, then changes target velocity/rotation even if hurt=false. Per-axis added motion=(sign(Siren-target axis)*0.5 - selected old velocity)*0.100000000372529*5; Y sign uses SirenY-targetY+1. Native X term subtracts OLD Z velocity, not X; Z subtracts Z and Y subtracts Y. Pitch/yaw turn toward the Siren with wrapped+-30 changes. This is separate from song attraction and does not explicitly set hurtMarked in this pull branch. Client observation/sync under rejected hurt is a future runtime question, not silently assumed. No direct HP subtraction or new source.

## Classification

Three non-promoted packages: Flute CUSTOM_CONTROL (attachment timer and repeated Mob target/navigation clearing); Siren bite VANILLA_LIKE_EXTENDED (native mob_attack with custom animation/timing); Siren pull CUSTOM_CONTROL (native damage attempt plus independent asymmetric motion and rotation). Song CUSTOM_CONTROL/status-marker package is reused, not duplicated. Resource costs/cooldown belong to Flute delivery, not extra duplicated utility effects.

## Exclusions

Ordinary renderer/heart appearance, descriptions, flute acquisition/crafting and Siren cosmetic pose/hair are short exclusions. Other MiscData lunge/scepter fields and other Iaf attachments are not marked reviewed by their shared registration. Gorgon/stone-statue eligibility is recorded only as an existing called predicate here; full Gorgon delivery/defense is next.

## Evidence and validation

[Machine-readable packages/paths](iceandfire-r2g3b-siren-flute-attacks.json), [native witnesses](native-evidence/iceandfire-siren-flute.json), [consumer census](iceandfire-flute-callers.json), [exact loader tick routes](reference-evidence/iceandfire-siren-flute-244.json). Scoped validation reproduces new native/reference evidence, checks actual Post entry and passenger distinction, effect/source separation and independent pull hurt return, preserves accepted views/prior evidence, runs five tooling tests and diff checks. No new whole-catalog full-validation claim.

Exact next task: R2g4: Gorgon native semantic review, starting GorgonEntity.aiStep/isBlindfolded/isTargetBlocked, IafEntityUtil.isEntityLookingAt, GorgonHeadItem.releaseUsing, StoneStatueEntity and statue creation/death/persistence, actual GORGON source identities/native hurt admission and direct compat predicates. Reuse R2g1 pinned factories/tags/compat and completed Frozen/Siren. Ice & Fire remains PARTIAL; no runtime boss/L2/Stage/production/Phase6/7 work.
