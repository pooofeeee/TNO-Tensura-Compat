# R2i9a — Bosses Rise combat source closure

Final whole-artifact combat source closure, explicit AI admission and short noncombat exclusions.

Static review only. Future runtime fixtures remain unexecuted; whole Bosses’ Rise review is PARTIAL.

## Coverage

All802 installed classes inventoried;157 watched methods now have pinned method witnesses, including16 previously unwitnessed helper/exclusion methods. All6 custom damage-key reference methods and18 native MobEffect reference methods map to reviewed sections or explicit datagen/support dispositions. Two declared custom DamageTypes both have actual native hurt producers; no custom MobEffect registry implementation. Source census is an index, not a claim that every class is a separate mechanic. Native registries, entity/projectile inheritance, equipment, owner helpers, status/counter, event/mixin and boss families have been reviewed. Static completion does not certify runtime compatibility.

## Ai admission

Explicit anonymous classes SoulSkeletonEntity$1, SoulKnightWitherSkeletonEntity$1 and all three Dragon guardian $1 each require isTimeToAttack AND distanceSquared < mob.width*mob.width+target.width AND sensing.hasLineOfSight; they do NOT return constantfalse. Therefore protected Knight arena/Dragon guardian ordinary Mob.doHurtTarget routes remain valid alongside their separately timed callbacks. This differs from constantfalse PirateRook/PirateCaptain/GhostTentacle canPerformAttack. No accepted AI path removed or invented. Native timed callbacks, range and hurt-return ordering remain as protected; genuine runtime fixtures must distinguish AI hits from animation hits.

## Ownership

OwnableByAllEntity resolves UUID to loaded LivingEntity on server, playerByUUID on client. Owner-hurt-by and owner-hurt-target goals require a new native timestamp then normal TargetingConditions/TargetGoal admission. These and DoNotAttackOwnerGoal exclude the resolved owner and OwnableEntity with the SAME resolved owner object; not a new blanket team/HP immunity. Null-owner equality can exclude other unresolved Ownable entities. Actual melee sources remain summon itself; native arrows retain shooter. Crossbow/Rook/Ghost production remains genuine native item/boss delivery, never forced target assignment.

## Movement helpers

UnderworldKnight.move(double) pushes only itself from look angle and is already part of reviewed attack motion, no additional target HP request. SandwormMoveControl stops motion/settles collision down.025 when not dive-moving; while diving dampens velocity*.4 and follows native movementSpeed*modifier clamped to distance*.9 beyond distanceSquared.25. This is steering for already-reviewed collision attacks, not an extra damage/scaling point. Server animation PoseStack.push is matrix bookkeeping, not entity knockback.

## Short exclusions

FrozenSkeleton is breakable decoration with hit counter/8tick lockout and debug-stick pose; no frozen effect, attack or HP payload. PileOfBones consumes its own five-hit resource before many native hurt rejections, then disperses bone-remains FallingBlocks without setHurtsEntities; no summoned attacker or combat status. Anchor/Cage/CratePile implement decorative break/durability/drop behavior, not outgoing damage. CratePile refuses noncreative break while native Kraken spawner within48 or Kraken in inflated48 box, and ignores explosions/fire; its existence was already proven unnecessary for tentacle crate attack. StructureDestructionEvents changes protected tower blocks/break/place and explosion affected BLOCKS only, never affected entities or damage amount. These acquisition/world structures do not add a Stage combat package.

## Noncombat hooks

Bars/Black/Camera/KnightFirstPerson/BossHandling render cancellations affect overlays/hands/boss bars only. Client configuration push is config-builder nesting. Wither/EndDragonFight/Warden server mixins only register/update boss-bar tracking, not native boss HP or attacks. Other render/animation/acquisition/loot/storage/information/worldgen helpers have no additional combat callback. Native ordinary swords/shields/food exclusions are R2i8c; do not infer attacks from item or entity names.

## Correction and stage

Apply the protected R2i8a additive correction during promotion: Sandworm Gauntlet constructs PoisonSpitPrEntity then invokes inherited instance shoot; it does not invoke a static helper. Boss spit and native arrow/PoisonArea semantics unchanged. Keep native source holders, direct/causing entities, null ownership, admission and hurt-return companions. Future Stage scales each final native HP request exactly once, not counters/attributes/control/radius/spawn count, terminal death requests or already-derived damage. Native poison/fire/freeze origin attribution and mitigation tests remain future integration questions, not evidence of a safe implemented fix.


[Machine evidence, packages and native paths](bossesrise-r2i9a-closure.json).

Exact next task: R2i9b: deterministic Bosses Rise deduplication/promotion to five views and COMPLETE ledger; apply R2i8a static-helper correction, retain all source/owner/admission/native fixture variants and resolve both custom DamageTypes. Run full catalog validation/five tooling tests, commit/push/live-verify. Authorized next-mod sequence ends at Bosses Rise; no runtime, Stage, production, Phase6/7 work.
