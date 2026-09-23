# R2i1 — Bosses Rise source foundation

Bosses Rise native source/tag/entrypoint and admission-hook foundation; all payload/control families remain PARTIAL.

Static review only. Future runtime fixtures remain unexecuted; whole Bosses’ Rise review is PARTIAL.

## Authority

Installed block_factorys_bosses-2.1.2-neo-1.21.1.jar SHA9e230bd509e7aeb3af4c08125db0340734c0179d83483649a16e45c0ea085e8c; modid block_factorys_bosses, display name Bosses Rise, version2.1.2. All802 classes parsed; existing539 decompiled Java files are navigation aids only. Exact native bytecode/resources and annotation declarations are pinned. Eternal Starlight is COMPLETE at e8f4fd9f930b7ef262ac981faef109adc8f3e458 and stays unchanged.

## Registry

BossesRise entrypoint registers native entities/items/attributes/data attachments on supplied mod event bus, and itself on NeoForge EVENT_BUS. Two static DamageType keys correspond to two installed JSON definitions. No MobEffect subclass or custom MobEffect registry/constructor candidate exists in the entire-class census;18 methods reference vanilla MobEffects instead. This is not a no-status/no-control claim: native effects, freeze/fire counters and attachment states require family review.

## Source construction

CannonballEntity.onHitEntity: if hit entity differs from getOwner, native damageSources.source(CANNONBALL_HIT,this,getOwner) requests10 damage; successful hurt plus ServerLevel runs native post-attack enchantment callback. Independent server explosion radius2/MOB/firefalse follows regardless hurt return, then discard. KrakenTentacleEntity.attackEntityWithSlam constructs native source(KRAKEN_TENTACLE_SMASH,this,getOwner), requests ATTACK_DAMAGE * maxDamageScale * clamp(distanceModifier,.5,1), then independently pushes target. Both preserve separate direct entity and actual causing owner (including null), no fallback owner or direct HP edit. Full geometry, creation/ownership, explosion source and defenses remain family review.

## Type contracts

cannonball_hit exhaustion0; kraken_tentacle_smash exhaustion.1. Both difficulty scaling when_caused_by_living_non_player; this is native difficulty policy, not TNO Stage. Scoped Minecraft1.21.1 + NeoForge21.1.244 + native mod closure gives BOTH bypasses_armor and bypasses_shield (shield tag includes armor-bypass tag). Cannonball additionally is_projectile, panic_causes, always_kills_armor_stands; tentacle additionally no_knockback. Neither gains bypasses_effects, bypasses_resistance, bypasses_enchantments, bypasses_invulnerability, bypasses_cooldown, is_fire or is_freezing. Native mitigation beyond armor/shield remains applicable unless actual admission changes it; no whole-pack datapack order claim.

## Census

157 watched combat/admission method candidates;6 custom-key-reference methods comprise3 datagen/lang/tag support methods,2 actual hurt producers and Cannonball.hasCausedDamage recognition. That helper recognizes exact cannonball_hit OR vanilla EXPLOSION whose direct entity is CannonballEntity; it does not create damage. Census membership is not semantic completion and no boss/family is marked complete here.

## Admission hooks

Installed SubscribeEvent declarations: RollAttachment.preDamage checks Player plus isInvulnerable and cancels LivingIncomingDamageEvent; preEffect checks same gate and returns DO_NOT_APPLY for MobEffectEvent.Applicable. RollMixin targets Entity.setTicksFrozen HEAD, cancellable, canceling Player writes during same gate; ControlMixin targets Player.isImmobile HEAD and returns true while isRolling. Actual roll activation/server packet/cooldowns, expiry and effect-event dispatch are next. No source-tag exception is present in preDamage body; native event dispatch/admission still matters.

## Other hooks

DragonArmorEvents.onPlayerHurt is a LivingDamageEvent.Post hook whose actual gear predicates and secondary callbacks need equipment review. BossCancelDie2Procedure is named as if canceling death, but onEntityAttacked merely forwards IncomingDamage to execute: no setCanceled/setAmount/setHealth/hurt invocation in either pinned overload. Native source UUID bookkeeping and EnderDragon loot code are not an established death veto. Shared boss entity methods carry their own death/state logic and remain pending.

## Compatibility

Explicit-name scans: Bosses Rise for Tensura/L2 names, installed Tensura and four inventoried compat candidates for block_factorys_bosses/bossesrise; zero hits in six archives. Generic event/mixin/skill/effect/tag behavior remains possible and untested. This does not certify Tensura/L2 compatibility.

## Stage scope

Registry/source creation/tags/roll admission have NO_STAGE_VALUE. Numeric payloads must receive one final native damage/heal amount multiplier after native formula selection; never multiply source construction, attributes, difficulty policy, event phases and hurt amount together. Counts/duration/geometry, native death choreography, ownership and binary defenses stay native. No production or Stage implementation authorized.

## Exclusions

Rendering/animation/camera cosmetics, crafting/acquisition, ordinary utility/storage, information, loot/progression and worldgen without combat callbacks are short exclusions. Native server animation timing that actually schedules a hit remains combat-relevant. No deep noncombat archaeology.


[Machine evidence, packages and native paths](bossesrise-r2i1-source-foundation.json).

Exact next task: R2i2: Bosses Rise shared native admission/control, beginning RollAttachment and its real server delivery/expiry, effect/freeze cancellation and ControlMixin, then shared boss damage helpers and death/state admission. Preserve source identity; no runtime/L2/Stage/production work.
