# R2j3 — Bosses of Mass Destruction Night Lich

BOMD Night Lich combat/admission/projectile/teleport/minion semantics complete; whole mod remains PARTIAL.

Static review only. Future runtime fixtures remain unexecuted; whole Bosses of Mass Destruction review is PARTIAL.

## Scope

BOMD Night Lich only; Twilight Lich remains accepted and untouched. Twenty-seven installed native class witnesses, exact loader projectile/explosion paths, selected CerbonsAPI geometry helpers and raw vanilla Phantom/source bytecode pin the actual implementation. No runtime boss test is represented here.

## Admission

LichEntity has no hurt/isInvulnerableTo/canBeAffected override or configured EffectsImmunity. All installed shared damage handlers admit; ordinary inherited damage/effect admission and external hooks remain. There is no native boss shield, fixed damage cap, reflection requirement or projectile-type immunity in this Lich code. Lich registry does not set fireImmune. causeFallDamage=false and checkFallDamage empty suppress native falling damage. canCollideWith returns the mutable collides flag; that flag is not a damage invulnerability flag and is never consulted by BaseEntity.hurt. Native despawn helper keeps it except Peaceful. File HP300 and attack9 were pinned in R2j1; no base-attribute multiplier is proposed.

## Delivery and phase

Server constructor registers Player FindTargetGoal with visibility=true, reachability=false, reciprocal chance10, search AABB inflated by range and unseenMemoryTicks200. Attack ActionGoal requires alive/not deadOrDying and a target, updates every tick, uses initial CooldownAction80; stop raises remaining cooldown to at least80. Concrete actions require target instanceof ServerPlayer. Shared phase change adds priority actions comet rage12, volley rage11, minion rage8 in that order; crossing several milestones still schedules one bundle per monitored hit. Regular weighted choice may choose comet/volley/minion/teleport; exact attack counts are native. Native callbacks cancel when deadOrDying OR current target null; changing to another nonnull target does not by itself cancel captures of an earlier ServerPlayer.

## Projectile admission

ProjectileThrower creates the native projectile with constructor owner, computes target-current position, adds horizontal-distance*.2 vertical compensation, shoots speed1.6/divergence0 and adds it to the level. Inherited ThrowableProjectile checks native ray hit and NeoForge onProjectileImpact cancellation before hitTargetOrDeflectSelf. A native non-NONE target deflection suppresses onHit; default self-deflection forwards the CURRENT owner, not automatically the defender. BaseThrownItemProjectile.onHit further requires server side, then entityCollisionPredicate. ExemptEntities rejects by exact entity TYPE; Lich missiles/comets exempt minecraft:phantom, including unrelated wild Phantoms. Inherited canHitEntity and owner/vehicle-leftOwner rules remain. No extra LOS/team/current-target-only or Tensura eligibility is invented.

## Missile damage

Native entity id bosses_of_mass_destruction:blue_fireball is MagicMissileProjectile, despite its name. On admitted entityHit: current getOwner must be LivingEntity; request owner current ATTACK_DAMAGE with native damageSources.thrown(this,owner), direct missile/causing current owner. It ignores hurt return, then invokes its nonnull LivingEntity callback, then discards unconditionally, including missing/nonliving-owner cases. No post-attack enchantment or ignition callback exists in this body. Actual source is minecraft:thrown, not magic, fire or shield_piercing. Single Stage point: final native entity.hurt argument after the owner attribute read; never multiply both attribute and hit.

## Missile status

Volley/VolleyRage resolve configured MobEffect id from the native registry and pass a callback that wraps that effect as a holder and calls target.addEffect(instance) without effect-source entity argument. Installed snapshot Slowness duration100 amplifier2. The callback runs after hurt regardless of its boolean, but still requires a Living owner, Living victim and nonnull callback; addEffect has separate native/NeoForge admission. Absent lookup gives no callback effect, without fallback. Keep duration/amplifier/control native, NO_STAGE_VALUE. Default/loading constructor does not rebuild this Java callback; it is not a substitute positive-control constructor.

## Volleys

Ordinary volley schedules five missiles after delay46 and aims at captured ServerPlayer current bounding-box center with plane-projected launch offsets. Rage schedules four volleys at60,90,120,150:9 horizontal,9 vertical,18 cross,18 rotated-cross =54 projectile creations if uncanceled, including coincident crossing offsets; return duration180. Helpers prove lineCallback emits exactly points and circleCallback exactly points. Counts and geometry are native, not extra scaling points. A hit or status application is not guaranteed per creation.

## Comet

Comet uses the same native owner/exemption/delivery helper but deals no separate entity-impact HP hit. Entity hit, block hit, or CometProjectile.hurt calls onImpact. onImpact first checks and sets impacted=true; then if CURRENT owner Living, invokes nonnull captured impactAction at projectile.position and discards. Missing/nonliving owner sets impacted with no callback and no discard in this branch. Default/load constructor has null callback. hurt invokes onImpact BEFORE super.hurt and returns the superclass result: explosion is not conditional on attack damage being accepted, and onImpact has no independent server guard (natural collision delivery is server-gated by the base). This is detonation, not a native reflection mechanic.

## Comet source

Both CometAction constructors capture the creating Lich in their explosion callback: level.explode(lich,x,y,z,config.comet.explosionStrength,ExplosionInteraction.MOB), default fire=false. Installed strength4. Native explosion direct source is that captured Lich and indirect source is the same Living Lich, selecting minecraft:player_explosion even though the attacker is a mob. The comet projectile and the entity that hurt it are neither direct nor causing explosion source. Owner changes alone would not rewrite the captured callback. Do not fabricate PLAYER identity from the DamageType name. A native source exclusion keeps the Lich out of the initial explosion candidate list, subject to later event-list modifications.

## Explosion payload

Native explosion selects within radius2*strength, permits ignoreExplosion and damage-calculator admission, checks nonzero directional length, posts NeoForge detonation hooks, then calls victim.hurt with calculator amount. Default amount: ((exposure*(1-distance/(2*strength)))^2 + exposure*(1-distance/(2*strength)))/2 *7*(2*strength)+1. Native exposure and geometry remain; damage hurt return is ignored and explosion displacement proceeds independently with native EXPLOSION_KNOCKBACK_RESISTANCE and EventHooks.getExplosionKnockback. Monolith ExplosionMixin may change supplied strength and is pending equipment review. Single future Stage point is this attributed native explosion per-victim final hurt amount; do not scale strength/radius, exposure, knockback or both callback and explosion engine.

## Comet delivery

Ordinary comet requires ServerPlayer at scheduling, launches once at delay60 through ThrowProjectileAction, which uses whatever nonnull current target exists at execution; cooldown80. Rage captures ServerPlayer, emits six comet creations at delays60+30*i, i0..5, from a six-point radius3 ring and aims at captured player current center; return duration240. Entity-hit, block-hit and projectile-hurt detonation are distinct runtime entry paths. Prevent duplicate damage by retaining impacted flag; never add an entity-impact fallback.

## Minion delivery

Ordinary summon queues beginSummonSingleMob after40; that copies fixed NBT, adds id minecraft:phantom, resolves through EntityType.loadEntityRecursive, attempts up to30 placements, then schedules actual SimpleMobSpawner.spawn after another40 with cancellation. Rage queues nine begin calls at40+40*i-3*i*(i+1)/2 (i0..8), then each successful rune waits40; total action duration292. Placement requires loaded chunk, no liquid in prospective spawn AABB, no collision and valid native empty spawn block. No owner/tame/team inheritance or forced target is written. SimpleMobSpawner sets position, calls native finalizeSpawn(MOB_SUMMONED), then adds entity with passengers; genuine later Phantom AI supplies melee.

## Minion actual state

Literal summon NBT is Health14,Size2,Attributes:[{Name:generic.max_health,Base:14f}]. Installed LivingEntity load reads lowercase attributes, so the legacy Attributes list does not set max health. Health14 is loaded through native setHealth; Phantom read sets size2, but subsequent SimpleMobSpawner.finalizeSpawn calls Phantom.finalizeSpawn, which resets size0. Native size update sets attack base6+size, hence6 after this reset before external modifiers. Do not record maxHP14 or effective size2 from the literal alone. Phantom sweep intersection calls native Mob.doHurtTarget: mob_attack direct=causing Phantom, current ATTACK_DAMAGE plus native server enchantment formula; successful hurt gates native knockback/postattack/lastHurt bookkeeping. No Lich-owner damage credit is introduced. Current runtime stats/HP remain future observations, not measured here.

## Placement geometry

RangedSpawnPosition uses CerbonsAPI randVec with each component in[-.5,.5), normalizes it, and clamps its ORIGINAL length to[min,max]. That length is below.867, so ordinary normalized vectors are always scaled to min, not uniformly across the advertised interval. Lich teleport thus uses nominal20 rather than20..35, minion positions nominal4 rather than4..8; preserve native near-zero normalization behavior and placement rejection. This affects test coverage, not a Stage value or a proposed fix.

## Teleport

Chosen teleport requires ServerPlayer. First attempts100 positions around captured player position with native spawn predicate AND Lich.inLineOfSight(target). The latter checks existing Lich eye-to-target collider-block ray/Fluid.NONE and target look dot(targetEye->LichEye)>0; it does NOT test LOS from prospective candidate pos. If all fail, backup attempts100 around target heightmap MOTION_BLOCKING_NO_LEAVES position using only spawn predicate. Successful placement queues delay10 with normal cancellation; on execution collides=false and queues nested delay30 with default no-cancellation supplier, then teleports to captured pos, emits native end event and sets collides=true. It does not set invulnerable or require a successful damage event. Targetless-attacker afterDamage can schedule this but if target remains null until outer delay, normal cancellation prevents execution; once inner event queued it lacks that cancellation.

## Night context

Installed eternalNighttime=true makes Lich serverTick force current day to time16000 through LichUtils.timeToNighttime. This matters to vanilla Phantom daylight burning: Phantom.aiStep performs native sunlight test and ignition. Keep the world-time context in summon fixtures; it is not an extra damage or Stage amount. No unrelated time-system research.

## Death cleanup

Lich.die queues experience drops (excluded acquisition), then obtains every Phantom in new AABB(blockPosition).inflate(100,100,100) and invokes LivingEntity.kill before super.die. It does not check summon ownership or call hurt boolean. Patched kill requests generic_kill Float.MAX_VALUE against each Phantom, subject to native admission/hooks. This is death cleanup, NO_STAGE_VALUE, not a scalable combat nuke or proposed fallback. Ordinary wild Phantoms and any other matching Phantoms in the box are included by this code.

## Source tags

Pinned closure: thrown is_projectile + neoforge:is_physical + panic_causes; mob_attack is_physical + panic_causes; player_explosion is_explosion, no_knockback, avoids_guardian_thorns, always_hurts_ender_dragons, can_break_armor_stand, panic_causes. None has native armor/shield/Resistance/enchantment/invulnerability/cooldown bypass tags in this scope. Explosion no_knockback suppresses generic hurt knockback, not the separate native explosion vector. generic_kill has technical, armor/shield/invulnerability/Resistance/wolf-armor bypass and no_knockback; preserve exact cleanup source. Other mod/datapack changes remain untested.

## Tno and exclusions

Three numeric payload boundaries: missile native hurt, comet attributed per-victim explosion hurt, and summoned Phantom native melee hurt. Slowness, summon count/state, teleport/collision, fall veto, native phase scheduling and death cleanup stay unscaled; shared capped healing was already reviewed and is not duplicated. Native literal/state discrepancies are recorded, not repaired. Skip rendering/animations without callbacks, experience/loot, soul-star acquisition ; the combat-relevant nighttime context is recorded above.

- **Native Lich thrown missile damage**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Once at MagicMissileProjectile.entityHit final hurt argument after current living owner ATTACK_DAMAGE read.
- **Configured native missile Slowness**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Native control/eligibility/counts/phase or cleanup; no additional scalable payload.
- **Native attributed comet explosion damage**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Once at attributed native Explosion.explode per-victim final hurt amount; preserve strength/geometry/source and independent displacement.
- **Native Phantom creation and initialization**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Native control/eligibility/counts/phase or cleanup; no additional scalable payload.
- **Native summoned Phantom melee**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Once at summoned Phantom Mob.doHurtTarget final hurt argument after native attribute/enchantment formula.
- **Native Lich teleport and collision window**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Native control/eligibility/counts/phase or cleanup; no additional scalable payload.
- **Native Lich admission and fall veto**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Native control/eligibility/counts/phase or cleanup; no additional scalable payload.
- **Native Lich priority rage sequence**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Native control/eligibility/counts/phase or cleanup; no additional scalable payload.
- **Native Lich death Phantom cleanup**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Native control/eligibility/counts/phase or cleanup; no additional scalable payload.

[Machine evidence, packages and native paths](bomd-r2j3-night-lich.json).

Exact next task: R2j4: BOMD Obsidilith shield/pillar admission and break rules, native Burst/Wave/Spike/anvil delivery, hurt-return/secondary effects and exact custom shield_piercing formulas. Reuse R2j1/R2j2 source, effect-filter, phase, scheduler and capped-heal evidence. Then Nether Gauntlet, Void Blossom and combat equipment. Static only; continue automatically while quota is healthy.
