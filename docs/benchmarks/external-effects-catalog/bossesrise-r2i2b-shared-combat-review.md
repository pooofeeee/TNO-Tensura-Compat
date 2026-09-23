# R2i2b — Bosses Rise shared combat contracts

Shared native boss attack, death callback ordering, multipart/owner and raw-motion contracts; concrete families remain pending.

Static review only. Future runtime fixtures remain unexecuted; whole Bosses’ Rise review is PARTIAL.

## Authority and scope

Both installed base classes have the same attack helper body. AbstractBossEntity is parent of UnderworldKnight/InfernalDragon/Yeti; AbstractStateBossEntity is parent of Sandworm/Kraken. The39-method whole-artifact shared-caller census pins real attack/death/motion references. Full concrete phase timing/geometry/immunities still belong to each boss family; this section completes only shared contracts, not five bosses.

## Attack amount

attackEntity(target,damageScale) selects native mobAttack(this), whose direct and causing entities are the boss. Explicit-source overload retains caller-supplied DamageSource unchanged. damageScale<=0 returns false before damage. Otherwise requested damage = damageScale * current ATTACK_DAMAGE; on ServerLevel EnchantmentHelper.modifyDamage uses getWeaponItem,target,same source,amount before target.hurt. Hurtfalse returns false; hurttrue runs native server post-attack enchantments, records lastHurtMob, returns true. No hardcoded universal damage amount, no source substitution and no owner-to-player rewrite. Single numeric Stage point is final helper hurt argument after native attribute/enchantment formula; never multiply both attribute and helper or concrete caller and helper.

## Melee geometry and return

meleeAttack uses LivingEntity query in AABB.ofSize(position+getLookOffset(reach),aabbSize,aabbSize,aabbSize), excluding self. Default offset height1.5; size is full side length, not radius. Shared helper adds no LOS, team/owner, attackable, current-target-only or native TargetingConditions predicate; callers may choose their own predicates separately. For each selected entity, attackEntity success is required before raw outward normalized horizontal push*pushForce (Y=.2) and consumer callback. Hurtfalse prevents both these followups. Caller-specific damageScale, box, timing and callbacks remain next; no geometric inflation/eligibility repair.

## Legacy death order

Exact NeoForge LivingEntity.actuallyHurt performs native armor/magic/Pre/absorption processing; when final newDamage!=0, records damage, setHealth(oldHP-newDamage), game event, then virtual onDamageTaken. Only afterward calls CommonHooks.onLivingDamagePost. AbstractBossEntity.onDamageTaken invokes maybeCancelDeath: require deadOrDying, source NOT BYPASSES_INVULNERABILITY, shouldCancelDeath true; if still dead, setHealth(.1), then BossCancelDieProcedure. Base shouldCancelDeath always sets state dead and returns whether prior state was not dead. This is native conditional death choreography, not heal/event amount replacement. Subclasses override decision (pending exact family semantics). Post listeners can observe already-restoredHP while reported damage remains unchanged; no measured-HP-loss equivalence assumed.

## State death order

AbstractStateBossEntity overrides actuallyHurt: call super.actuallyHurt completely (including native Post callback), then maybeCancelDeath(source). Same dead/non-bypass/shouldCancelDeath predicates and .1 restoration, followed by cancelDeath. Base shouldCancelDeath=false and cancelDeath empty; only real subclass overrides enable it. Thus state bosses perform this restoration AFTER Post while legacy bosses do it BEFORE Post. Neither is an unconditional boss immunity or ordinary heal. BYPASSES_INVULNERABILITY skips this shared choreography, subject to the concrete boss own hurt admission. Do not scale .1 restoration or intercepted death-state duration.

## Defeat sources

Both getSourceEntity methods try stored SourceUUID lookup in ServerLevel and require LivingEntity; on missing/invalid/nonliving use current Living target else self. AbstractStateBossEntity.simulatePlayerKill creates ordinary PLAYER_ATTACK source with that resolved entity in the single-entity constructor (direct=causing resolved entity, not necessarily a Player), requests999 against self, ignores hurt result. Actual callers are Kraken two state lambdas and Sandworm one state lambda, with exact state gating pending respective review. This is native defeat scripting, NO_STAGE_VALUE, not a proposed fallback damage implementation. Native source tags/admission and callbacks still apply.

## Legacy procedures

BossCancelDieProcedure only acts when state dead/fake_dead: Dragon death timer88, Yeti60; no generic Knight timer branch. BossCancelDie2 IncomingDamage helper never cancels damage/death: on apparent lethal amount and BF_BOSS tag it attempts source UUID writes; its if/else-if uses instanceof-other-type defaults0, so the first non-Sandworm condition is true with no write and skips later Dragon/Yeti/Knight branches. Preserve actual control flow, not intended name. EnderDragon/KNIGHT_SWORD branch spawns loot and is excluded. AbstractBossOnEntityTickUpdateProcedure.onDying contains native PLAYER_ATTACK999 at countdown1 but has ZERO installed invocation callers; do not promote it as a delivered attack. onSpawn DOES have native UnderworldKnight procedure caller; while spawn timer>0 it sets bossHP=MAX_HEALTH/zero motion, at initialservertick repositions Players in32full-side AABB, and during timer>10 constrains their motion/facing. Exact Knight activation is next; scripted initialization/control has no Stage multiplier.

## Parts

AbstractEntityPart.hurt forwards unchanged source and amount to parent.hurt(thisPart,source,amount), with no extra hurt invocation, damage formula or source rewriting. Parent chooses part-specific defense (Sandworm/Tentacle pending). Fire ticks/clearFire route to parent; part.is recognizes self or parent, attackable/pickable delegated. Part itself is not independently saved. Scale admitted parent damage only once, never part forwarding plus parent. Native direct entity in source remains actual attacker/projectile, not automatically part or parent.

## Ownership

OwnableByAllEntity.getOwner uses UUID; nullUUID returnsnull; server resolves any LivingEntity byUUID, client resolves Player only. No fallback boss/shooter is invented. OwnerHurtBy/OwnerHurtTarget require owner, changed native timestamp and TargetingConditions.DEFAULT admission before setting Mob target. All three owner-aware goals exclude exact resolved owner and OwnableEntity whose resolved owner is same object (including null==null for ownerless candidates in DoNotAttackOwnerGoal), then native TargetGoal.canAttack. This controls target selection only, not blanket allied damage immunity or source credit; actual mob/projectile callbacks determine source.

## Displacement

SpatialUtil.pushEntity computes additive raw force. With speedLimit>=0, project newMotion=(current+force) onto normalized force; if projection>limit replace force with normalized newMotion*limit, then target.push(force). This is NOT a strict final velocity cap. Native Entity.push(Vec3/doubles) adds delta and marks impulse, without LivingEntity.knockback resistance/event path. For ServerPlayer also sends PlayerPushMessage(force), whose CLIENTBOUND handler applies client push; no second server damage/Stage event. Generic roll has no blanket push veto; only concrete payloads such as already-indexed GlacialShove add one.

## Tno decision

One numeric shared attack package with one final native hurt boundary; native control/death/part/source/resource bookkeeping stays unscaled. No direct HP/SHP edits are introduced by research. Future runtime must distinguish canceled hurt vs post callbacks, source attribution with unresolved owners, two death timing models, bypass tags, parts forwarding, native push vs knockback and cloned/summoned eligibility. No runtime, Stage, production, Phase6/7 changes.

## Exclusions

Boss bars, music, sounds, render pose, loot/advancements and registry acquisition are short exclusions. State persistence retained only as native prerequisite; no exhaustive state-controller or cosmetic archaeology. Uncalled onDying helper is explicitly excluded from live delivery claims.

- **Shared native boss damage**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Once at final target.hurt amount after damageScale * ATTACK_DAMAGE and EnchantmentHelper.modifyDamage.
- **Native boss lethal-hit choreography**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Native control/source/part/death choreography; no additional scalable amount.
- **Knight native spawn HP/control prerequisite**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Native control/source/part/death choreography; no additional scalable amount.
- **Native multipart damage forwarding**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Native control/source/part/death choreography; no additional scalable amount.
- **Native owner-aware summon targeting**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Native control/source/part/death choreography; no additional scalable amount.
- **Native raw additive combat displacement**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Native control/source/part/death choreography; no additional scalable amount.

[Machine evidence, packages and native paths](bossesrise-r2i2b-shared-combat.json).

Exact next task: R2i3: Underworld Knight concrete hurt admission, immunity stacks/phases, real melee/SwordWave/Rift/KnightMark/SoulShockwave producers and summoned skeletons. Reuse completed roll and shared helper contracts; review live callers, skip unused helper/cosmetic/acquisition branches. Then Infernal Dragon, Yeti, Sandworm, Kraken/cannon and combat equipment. Static only.
