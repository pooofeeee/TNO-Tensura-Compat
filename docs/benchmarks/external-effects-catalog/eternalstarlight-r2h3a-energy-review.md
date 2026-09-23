# R2h3a — Eternal Starlight energy combat

Energy weapon/projectile/hazard and Golem smash payloads complete; full boss defenses/phases and other debris producers remain later work.

Static subsection complete. Runtime fixtures remain unexecuted; no Stage or production implementation.

## Spark payload

EnergySpark.onHitEntity and tick target-AABB contact converge on hurtTarget. Require (no assigned target OR contacted entity is assigned target) AND entity!=owner. Native code writes target invulnerableTime=0 without restoring it, then requests ENERGIZED_FLAME3 direct=Spark/causing=owner; ignores hurt return. No shouldHarm/ally check and no ignition here. Discard occurs even if contact fails those predicates. Block contact reflects the corresponding velocity axis. Server resolves/clears target UUID, clears dead target; native homing/jitter does not change damage. Lifetime is >600 spawnedTicks with Player owner, >120 otherwise. These native iframe rules are evidence, not permission for compat to bypass admission.

## Spark producers

EnergySword.postHurtEnemy follows native successful primary Player melee/item callback and, server-side with item cooldown clear, creates5..7 Sparks targeting victim then cooldown75. MechanicalCrossbow marks both arrow and firework, adds1 AbstractArrow piercing and multiplies shot velocity1.75. OnProjectileImpact server Living entity branch clears marker BEFORE checking Living owner, nonnull projectile.getWeaponItem and item cooldown; then spawns5..7 Sparks and cooldown75 without requiring native primary hurt success. Block impact does not clear this mechanical marker. Exact installed FireworkRocketEntity and Projectile declare no getWeaponItem override; inherited Entity getter returns null, so native mechanical firework fails this weapon prerequisite and spawns no Sparks. Arrow stores its fired weapon and can qualify. StarlightGolemSmashPhase tick30 with target creates5 owned Sparks in a fan, all assigned to target. SpecialItemCooldown is per owning entity and item identity (not stack identity), ticks down server-side through ESCommonHandler.onEntityTick.

## Ball lightning

GolemSteelGreatsword successful melee callback OR native swing_attack packet calls performSpecialAttack: server, cooldown clear ->3 owned BallLightning at yaw offsets-15/0/15 and speed.8; each later ball targets the preceding ball; cooldown100 shared by both triggers. Tick target link >16 blocks is removed. With a target, ESEntityUtil.raytrace returns entities along the full segment and a separate block result: BallLightning ignores block result, so intervening walls do not truncate this beam. Living recipients passing shouldHarm(owner,recipient) get ELECTRIC_SHOCK8 direct=ball/causing=owner; only hurt true ignites2 seconds. Ordinary cooldown applies to beam. Block impacts bounce. Owner distance>32 or spawnedTicks>600 calls explodeAndDiscard: manual AABB+2 Living recipients passing shouldHarm get ENERGIZED_FLAME8, no Level.explode and no ignition; Player owner resets each recipient iframe0 without restoration, other owners do not. Hurt result ignored. Distance discard has no early return, so tick may continue beam work and a simultaneous lifetime expiry may call burst again. Ownerless/null-source behavior is kept native, not replaced by invented ownership.

## Energized hazard

EnergizedFlame server tick, after tickCount20, requires resolved nonnull owner; its AABB is expanded XZ.5 and extends6 upward. Living recipients passing shouldHarm receive ENERGIZED_FLAME2 direct=hazard/causing=owner, then ignite3 seconds regardless of hurt result. No LOS or iframe override. Owner UUID persists, unresolved lookup clears it. Lifetime>60 discards without an early return. Incoming damage to hazard only discards on BYPASSES_INVULNERABILITY (binary, not HP scaling). Golem.spawnEnergizedFlame optionally creates one at target position+velocity*20, then random available empty/sturdy-ground positions without replacement. SummonFlame phase0, cooldown over, target and attackEnergy>=0 starts and subtracts20 floored0; every40 behavior ticks spawn(2,15,true). LaserBeam phase requires cooldown, target and (phase1 OR energy>=30), subtracts50 floored0; beam spawns tick60, and ticks>=60 divisible40 spawn(1,15,phase==1). Boss phase/admission remains next subsection.

## Boomerang primary

BoomerangItem.use fails when damage>=maxDamage-1; native hand use otherwise consumes durability1, spawns owned no-gravity EnergyBoomerang speed2/inaccuracy.3, removes noncreative held stack and sets ordinary use cooldown15. EnergyBoomerang.asProjectile is an ownerless factory, but whole ES dispenser-registration census/commonSetup shows no native registration for it: do not claim default dispenser delivery. Base ThrownBoomerang uses owner ATTACK_DAMAGE base value (fallback1), replaces owner modifiers with matching weapon attack-modifier IDs, prepends weapon modifiers then appends remaining owner modifiers, and applies native ADD_VALUE/BASE/TOTAL loop order. Enchantment damage adjustment precedes Precision critical chance (installed .16 per level, max5), random success multiplies damage1.5. Actual HP source is vanilla thrown direct=boomerang/causing=owner. dealtDamage is set BEFORE hurt. Only hurt true, after Enderman early return, runs enchantment Post, knockback and Living doPostHurtEffects. Enchantment Post alone receives a separate player_attack/mob_attack source for Living owner; it does not replace the HP source. Subsequent entity hits are disabled once dealtDamage. Homing uses enchantment strength clamp0..1 (installed .1+.75*(level-1)), nearest shouldHarm Living within AABB3 and forward dot>.5; no explicit LOS check. Return/invalid-owner rules govern one-flight lifetime; item recovery is utility, not another HP mechanic.

## Boomerang secondary

ThrownEnergyBoomerang successful primary Living callback always ignites primary2 seconds. If owner/weapon missing or special item cooldown clear, server visits Living in victim AABB+2 passing shouldHarm and excluding primary; writes iframe0 without restoration then requests ELECTRIC_SHOCK8 direct=boomerang/causing=owner. Only secondary hurt true ignites2 seconds. Afterwards, owner+weapon sets item cooldown40 even when no recipient or all hits rejected. Primary and secondary are independent native numeric attacks. Native fire ticks reuse R2h2b native_elemental_ticks; do not multiply burn duration or invent electric/fire tags.

## Smash and debris

GolemSmash can start with cooldown over OR phase1/onGround/cooldown(3)<150, requires target and (phase1 OR attackEnergy>=0), then consumes16 floored0. Tick30 captures shockwave direction and creates Sparks. From tick40 radius=int((behaviorTicks-30)/3); unvisited nonair terrain must lie in radial shell, pitch difference<75 and yaw<30, with air above or below. Exposed-above or random1/6 flagged positions spawn ESFallingBlock duration100 and request ownerless GROUND_SMASH4 on nearby Living except the Golem, without ally/LOS checks or hurt-result dependency. This source has null direct/causing entity, so Golem-causer Incoming attackDamageScale does not apply. Lava visited positions instead have random1/25 event-vetoable magma replacement. ESFallingBlock is an ES Entity, not vanilla FallingBlockEntity: default damage=true, each tick Living in its AABB gets vanilla falling_block3 sourced by the debris (direct=causing=debris); no ally/owner/hurt-success gate in that method. Gravity/velocity/lifetime and damage flag persist; hurt only binary bypass-invulnerability discard. Debris is a separate HP delivery, not merely visual. Other debris producers remain assigned to later families.

## Admission scaling

R2h1 exact tag closure: energized_flame/electric_shock have no IS_FIRE/IS_LIGHTNING/IS_PROJECTILE, armor/shield/enchantment/Resistance bypass or cooldown bypass tags; energized_flame JSON effects=burning is feedback, not elemental admission. Ground_smash likewise has no armor/shield/enchantment bypass. Source cause still drives native difficulty/config and generic mod hooks. Each independent native hurt amount (3/8/2/4/3 or computed weapon amount) gets at most one future Stage multiplier at final request after native calculations. Keep primary, independent secondary, native burn ticks, and binary projectile/hazard removal distinct. Native iframe writes, enchantment-only rewritten source, allies, target assignment, item cooldown and hurt return must remain intact; Tensura/L2 runtime outcomes are untested.

## Exclusions

Exclude particle geometry, trails, sounds, item acquisition and normal pickup/storage. Keep boomerang homing/one-hit return only because it changes delivery coverage. Do not research extra cosmetic or classification detail.

## TNO integration decisions

- **Energy Sparks**: NUMERIC_SCALABLE, CUSTOM_ROUTED, ADMISSION_GATED. Stage: Once at EnergySpark.hurtTarget final ENERGIZED_FLAME3 request.
- **Mechanical Crossbow primary HP**: NUMERIC_SCALABLE, VANILLA_ROUTED, ADMISSION_GATED. Stage: Once at native arrow/firework final hurt; do not separately scale velocity/piercing.
- **Ball Lightning linked beam and expiry burst**: NUMERIC_SCALABLE, CUSTOM_ROUTED, ADMISSION_GATED. Stage: Once at each independent native ELECTRIC_SHOCK8 beam or ENERGIZED_FLAME8 burst hurt request.
- **Energized Flame ground hazard**: NUMERIC_SCALABLE, CUSTOM_ROUTED, ADMISSION_GATED. Stage: Once at EnergizedFlame.tick native ENERGIZED_FLAME2 request.
- **Energy Boomerang primary and electrical secondary**: NUMERIC_SCALABLE, COMPOSITE, VANILLA_ROUTED, CUSTOM_ROUTED, ADMISSION_GATED. Stage: Once per independent final primary thrown hurt after attributes/enchant/crit OR secondary ELECTRIC_SHOCK8 request.
- **Golem terrain shockwave HP**: NUMERIC_SCALABLE, CUSTOM_ROUTED, ADMISSION_GATED. Stage: Once at ownerless GROUND_SMASH4 native hurt.
- **ES damaging falling debris**: NUMERIC_SCALABLE, VANILLA_ROUTED, ADMISSION_GATED. Stage: Once at ESFallingBlock.tick final falling_block3 request.

[Machine-readable packages, delivery paths and future fixtures](eternalstarlight-r2h3a-energy.json). Exact archive/method witnesses and targeted semantic assertions are reproducible. No whole-mod completion claim.

Exact next task: R2h3b: close Eternal Starlight Golem/Lunar/Gatekeeper attack and defense families, rays and remaining custom damage callers; then remaining equipment/resources and whole-mod closure. Reuse R2h2a/b statuses and R2h3a energy payloads. No runtime/Stage/production changes.
