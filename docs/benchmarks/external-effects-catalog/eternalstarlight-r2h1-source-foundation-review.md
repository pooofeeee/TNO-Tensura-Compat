# R2h1 — Eternal Starlight source foundation

Ice & Fire remains COMPLETE at 74492a5c2ec72051e8c0d142e16542a795aa5029. This new mod is PARTIAL with no promoted packages or runtime claims.

## Authority

Installed eternalstarlight-0.8.1+1.21.1+neoforge.jar, SHA acb8fa7a69c4f7d4f1dfa3fba1dbdc96976478ea80b2f9025e43f0c4ee1ceb19, contains1384 classes. Exact bytecode/resource witnesses and existing source aids are reused. Inventory key eternalstarlight differs from actual namespace eternal_starlight. This foundation does not claim completed effect or boss semantics.

## Factory

ESDamageTypes.getDamageSource(level,key) delegates getEntityDamageSource with null; entity overload forwards attacker twice; indirect overload constructs ordinary DamageSource(holder,directArgument,causingArgument). Exact native DamageSource constructor/getters are retained in twilight-equipment-244 reference evidence. Source-only has both entities null; entity source has both identical; indirect source preserves separate supplied arguments. No special subclass, rewritten owner, fallback DamageType, target hurt or HP subtraction is performed by these factory methods. registryOrThrow then getHolderOrThrow requires a valid native registry holder.

## Damage declarations

Eighteen native ResourceKeys match eighteen installed damage_type JSON definitions. All declare exhaustion0.1 and difficulty scaling when_caused_by_living_non_player; this is native difficulty policy, not TNO Stage. Only laser and energized_flame request burning damage feedback. Feedback does not add IS_FIRE or ignition; no custom declaration gains IS_FIRE/IS_FREEZING/IS_LIGHTNING in the scoped native tag closure. Individual payload amounts and eligibility remain family review work.

## Tags

Scoped raw Minecraft1.21.1 + NeoForge21.1.244 + ES closure: ether/crystal_infection/soul_absorb bypass armor, enchantments and shield; numbness and sonar also bypass shield. Only seeds/shattered_blade/wilt have IS_PROJECTILE. Only numbness belongs to ES bypasses_crescent_pendant. No ES custom declaration gains bypasses_cooldown or bypasses_invulnerability here. Per-type no-impact/no-knockback/panic/armor-stand membership is explicit in the machine table. Other mods/datapacks and runtime load order can alter membership; no whole-pack tag claim.

## Registered statuses

Nine holders: crystal_infection, dream_catcher, sticky, flammable, brittle, numbness, teary, starfire, oblivion. Dream Catcher/Sticky/Numbness/Oblivion are BENEFICIAL; the other five HARMFUL. Registry constructors for Flammable/Brittle/Numbness/Teary are plain MobEffect, so their actual combat consumers must be reviewed in shared hooks rather than assuming absence of behavior. The five custom subclasses likewise need their actual methods and native producers reviewed; registry categories alone do not prove admission or compatibility.

## Registration

ESNeoEntrypoint constructor calls EternalStarlight.init, which loads ESMobEffects. RegistrationProvider.get delegates the service-loaded ESPlatform; installed META-INF/services selects ESNeoPlatform. Its provider creates/retains a DeferredRegister in REGISTERS, and the entrypoint registers those instances with the supplied mod event bus. Native bootstrap/datagen definitions and on-disk resources are distinguished from actual holder lookup; no fabricated registry setup is allowed.

## Event bridge

CommonEvents is declared EventBusSubscriber(modid=eternal_starlight), with SubscribeEvent on the pinned eleven combat callbacks. IncomingDamage: if not canceled, call onAllowLivingHurt and cancel on false; afterward call onModifyLivingHurtDamage/setAmount and onModifyPostAttackInvulnerabilityTicks/container setter even if this method just canceled. This describes in-method ordering, not a claim that the event bus dispatches pre-canceled events to a default subscriber. LivingDamageEvent.Pre separately calls onModifyLivingActualHurtDamage/setNewDamage; Post separately invokes onPostLivingHurt. These are different stages, not permission for multiple TNO multipliers.

## Other bridges

LivingHealEvent replaces its amount with ESCommonHandler.onLivingHeal result. LivingDeathEvent consults onAllowLivingDeath only while uncanceled, then calls onLivingDeath only if still uncanceled. LivingChangeTargetEvent sets the new target if the helper returns a different object. EntityTickEvent.Post delegates onEntityTick; CriticalHit calls its helper only when event.isCriticalHit; ShieldBlock calls its helper on getOriginalBlock, and ProjectileImpact delegates hit handling. Actual helper predicates, amount modifications, resource effects and mixin application remain the next semantic review.

## Census

All1384 installed classes parsed:29 direct damage-factory caller methods,31 damage-key-reference methods,38 status-field-reference methods. These include implementation/support/registry/client/datagen contexts; counts are not confirmed native delivery counts or completed mechanic packages. The census pins method/entry hashes and exact matched instructions so the next review starts at real producers/consumers.

## Compatibility

Explicit-name constant-pool and text-resource scans are negative in both reviewed directions: ES for Tensura/L2Hostility/L2Complements/L2Library names, and installed Tensura plus the four inventoried compat candidates for ES namespace/package names. Scope is exactly six archives, not the entire installed pack. Generic skill, damage/effect admission, event ordering, registry/tag-driven behavior and unnamed integrations remain possible and untested. No absence-of-conflict conclusion.

## Stage boundary

Source construction/registration/tag declarations have NO_STAGE_VALUE. When a reviewed payload requests a numeric hurt/heal amount, choose one amount boundary after native formula selection and retain eligibility/source identity; do not multiply factory creation, native difficulty scaling, status duration/amplifier and multiple event phases together. No payload scaling point or permanent implementation is approved by this foundation.

## Exclusions

Rendering/particles, registry-remap acquisition details, creative tabs, crafting, worldgen and ordinary utility are excluded quickly. No deep noncombat sections. Installed source aids are navigation only; existence of a class, method or census hit is not semantic completion.

[Machine evidence](eternalstarlight-r2h1-source-foundation.json); [native callers](eternalstarlight-source-census.json); [all eighteen source profiles](eternalstarlight-damage-tags.json).

Exact next task: R2h2: Eternal Starlight status/control and damage-admission semantics, starting Crystal Infection plus LivingEntityMixin and ESCommonHandler damage/effect hooks, then Starfire/Flammable/Brittle/Numbness/Dream Catcher/Sticky/Teary/Oblivion. Trace real native producers and one Stage amount boundary per scalable component; no runtime/L2/Stage/production work.
