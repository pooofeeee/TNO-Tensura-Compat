# R2k3a — Cataclysm Ender Guardian admission and phase

Bounded Ender Guardian incoming admission, helmet/altar phase and attack teleports; full Guardian and Cataclysm remain PARTIAL.

Static review only. Future runtime fixtures remain unexecuted; whole Cataclysm review is PARTIAL.

## Scope

Installed Cataclysm3.27: eleven class witnesses plus four selected loader classes and one vanilla calculator class close incoming Guardian damage admission, persistent helmet/mass state, native altar prerequisite, helmet explosion and two attack teleports. Full Guardian offensive AI, projectiles/runes/vortex, death/respawner and team behavior remain pending. Source aids are reading aids; saved instruction witnesses and installed hashes are authority.

## Incoming order

Ender_Guardian_Entity.hurt first rejects during GUARDIAN_MASS_DESTRUCTION unless source has BYPASSES_INVULNERABILITY. Next read DIRECT entity: while getIsHelmetless()==false reject AbstractArrow; reject ShulkerBullet and Ender_Guardian_Bullet_Entity in BOTH helmet states; halve amount for direct AbstractGolem; then call LLibrary_Boss_Monster.hurt with the same source. BYPASSES_INVULNERABILITY only exempts the first animation gate here: it does not exempt those arrow/bullet predicates or golem reduction. The local post-super branch only plays a sound on hurttrue and helmetless. An owner/causing golem behind a projectile does not satisfy direct AbstractGolem. These are class tests, not a general IS_PROJECTILE damage tag test.

## Shared binding

After the concrete prefilters, shared hurt calls virtual isInvulnerableTo (Guardian adds exact IN_WALL rejection), then applies the accepted bypass/cap/causing-distance/bucket/native-hurt pipeline. Guardian overrides DamageCap, DpsCap, RangeLimit and NatureRegen using CMCommonConfig.EnderGuardian. Pinned installed common file and static defaults give cap22, drain-rate13/20=0.65 per AI-enabled server tick, range12 with linear falloff12..18 and rejection at>=18, idle heal25 per20ticks when targetless and inherited regen timer<=0; HealCooldown remains inherited200. Bucket capacity is22, not13; full bucket still requests0.1; custom bypasses_hurt_time skips bucket only; BYPASSES_INVULNERABILITY skips shared cap/range/bucket AFTER concrete prefilters. Anonymous causing source skips shared range, not other rules. Native hurtfalse rolls back bucket. Do not scale cap/range/bucket/defense multipliers. Future Stage idle healing reuses exactly the R2k2a native heal argument point. No duplicate healing mechanic is introduced.

## Config and attributes

Native registered builder: HP333, attack16, armor20, speed0.27, follow range50, step height1.75, knockback resistance1. Constructor applies health/attack config multipliers (installed file1/1); this is initialization, not healing. CMCommonConfig.Commonbake resolves the fields from CommonConfig. Installed TOML is a pinned file snapshot, not proof of runtime-loaded effective values. The shared drain uses DpsCap/20; a dps_limit_time20 config field is not substituted into that reviewed formula. Shared EFFECTIVE_FOR_BOSSES and NeoForge effect admission continue unchanged; no concrete Guardian canBeAffected override is present in the pinned hierarchy. No Tensura/L2 compatibility is inferred from this static review.

## Helmet state

Synched initialization: IS_HELMETLESS=false, USED_MASS_DESTRUCTION=true, TELEPORT_POS empty. isHelmetless() is a separate live HP<=maxHP/2 predicate. tick first calls super.tick (including eligible shared heal), then while alive and flagfalse and HP<=half, setIsHelmetless(true) and BrokenHelmet. No NoAI guard surrounds this transition. Setter writes armor BASE15/speed BASE0.29 for true,20/0.27 for false, then synced flag. Native modifiers still apply to those bases. It is a latched transition: healing over half does not restore the helmet. Arrow admission changes when the flag changes, not merely when an earlier hit crosses half HP. This phase flag/threshold/attribute change has no independent Stage factor.

## Persistence

NBT saves is_Helmetless, used_mass_destruction and optional TeleportPos; load uses the state setters and reads optional position. Loading helmetless true restores attribute bases without calling BrokenHelmet. getBoolean on absent legacy keys supplies false, so missing used_mass_destruction differs from fresh synced defaulttrue; this is an NBT edge fixture, not a recommended artificial spawn setup. Existing shared home persistence remains unchanged.

## Altar prerequisite

Altar_Of_Void_Block.getTicker -> AltarOfVoid_Block_Entity.commonTick -> tick: !spawnedBoss, nearby alive player within6, server level and non-PEACEFUL -> spawnMyBoss. Native creation sets altar center position, finalizeSpawn(SPAWNER), setUsedMassDestruction(false), setHomePos(current dimension/altar BlockPos), then addFreshEntity. Only successful add destroys altar and marks spawnedBoss. Ordinary fresh entity construction retains used=true and lacks this altar initialization. Whole installed class scan finds four setter-caller methods: altar spawnMyBoss, mass-goal start, Guardian load and tick. External mods and NBT remain possible inputs. A legitimate future encounter fixture must distinguish actual altar spawn from ordinary fresh spawn; never silently invent the native prerequisite.

## Mass phase

Alive tick selects GUARDIAN_MASS_DESTRUCTION when AI enabled, animation NO_ANIMATION, used=false and current HP<=half. It does not require a target. It runs after the helmet-transition block and before other attack-selection branches. Registered anonymous AttackAnimationGoal2.start sets used=true. Selection alone is not the consumed flag; actual goal start is. Incoming non-bypass immunity lasts for this animation identity, not an inferred subrange. Its attack payload/timings remain R2k3b. A fresh default used=true Guardian can still lose its helmet/explode but does not enter this one-time mass phase via that branch.

## Helmet blast

BrokenHelmet server-only invokes Level.explode(Guardian,x+cos(yaw)*0.75,y+eyeHeight,z+sin(yaw)*0.75,2.0,TRIGGER). It supplies no custom source/calculator. Pinned native Explosion chooses EntityBasedExplosionDamageCalculator; that class overrides block behavior only, inheriting shouldDamageEntity=true and native exposure/distance damage. Native source is minecraft:player_explosion with DIRECT=Guardian and CAUSING=Guardian (the source factory tests non-null actors, not Player class). TRIGGER selects TRIGGER_BLOCK behavior; it does not disable entity damage. Explosion Start/Detonate hooks and native target filtering remain in the patched pipeline. Source entity itself is excluded by the entity query; immune-to-explosion targets are skipped. With radius2, D=((I*I+I)/2)*28+1, I=(1-distance/4)*seenPercent, within native candidate/range/zero-vector gates. Ordinary downstream armor/shield/Resistance/protection still apply. Hurt boolean is ignored by Explosion; knockback proceeds on its separate native branch. The tick has already latched helmetless even if explosion is canceled or every hurt is rejected. No direct HP subtraction and no second status payload is added.

## Blast scaling

Future Stage belongs once on the final per-target damage amount passed by this native helmet Explosion to hurt. Keep radius2, exposure, source identity, predicates, native hooks and knockback. Do not multiply radius or add a second hit. This is a new independently calculated explosion payload, not a fraction of prior incoming damage. Native damage JSON scaling=when_caused_by_living_non_player is vanilla difficulty behavior, distinct from a future TNO Stage factor; avoid duplicate integration when a central native explosion amount hook is later selected.

## Hug entry

Native tick priority is mass phase, air strike, vortex, then Hug and other attacks. Hug requires alive target, AI enabled, NO_ANIMATION, target onGround and teleport cooldown<=0: range4.3..16 inclusive with randomFloat*100<4, or distance<4.3 with threshold0.7. It sets cooldown280; counters decrement later that same tick. Its branch is reached only if the earlier vortex selection does not win. Vortex selection itself requires ready cooldown, AI enabled, NO_ANIMATION, distanceSq<=1024 and either distanceSq>=35 with random<2%, or random<60% with targetY>=GuardianY+3; short-circuit draw ordering remains native. No new LOS gate appears in these Hug predicates. Broader attack selection and all payloads are deferred.

## Hug prediction

Registered HugmeGoal has sensing30/teleport20. start stores targetX/Z. At animation tick14 with target present it predicts floor(currentX+(currentX-startX)/20*30), sameZ, and saves TeleportPos with current targetY. At tick20, target still present and saved pos present -> private teleport(savedX,CURRENT targetY,savedZ). Returned boolean is ignored: a failed/canceled teleport does not cancel the animation. Goal matching uses SimpleAnimationGoal animation reference identity; AnimationGoal requires updates every tick.

## Hug teleport

Private teleport first searches downward from original candidate until blocksMotion/min height; no solid block ->false. Otherwise EventHooks.onEnderTeleport constructs AND posts EntityTeleportEvent.EnderEntity to NeoForge.EVENT_BUS. Cancellation ->false; modified targetXYZ ->ProperTeleport. Helper requires hasChunkAt, searches down for solid below, tentatively teleportTo, then noCollision AND !containsAnyLiquid. Failure restores prior XYZ and returns false; success optionally broadcasts46, stops navigation and returns true. Outer helper emits TELEPORT game event at old position/sound only on success. No damage request or Stage value. Keep event-mutated destination and cancellation distinct from collision/liquid rejection.

## Air teleport

AIR_STRIKE1 normal selection requires alive target, AI enabled, NO_ANIMATION, distanceSq256..1024 inclusive, target onGround, helmetless flagtrue, randomFloat*100<20 and smash cooldown<=0; assigns cooldown600 before later same-tick decrement. Registered TeleportStrikeGoal zeroes XZ velocity before tick40, retaining Y. With target present at tick40 it calls direct teleportTo(targetX,targetY+(helmetless?8:4),targetZ). It does NOT call private teleport, Ender teleport hook, ground search, collision or liquid check at that site. Normal native selector requires helmetless, hence8 is the ordinary path; the helper also contains a4 branch if reached under another native state. At tick>48 and self onGround it sends AIR_STRIKE2 independent of target still being present. No claim that all downstream teleport listeners are bypassed; only the missing helper/event/placement gates at this native site is proven. Landing attack payload remains pending.

## Scope exclusions

Music, boss-bar presentation, sounds, particles and acquisition details receive no separate mechanic packages. Altar initialization is retained because it changes combat admission/phase behavior. Native shove, full ally rules, offensive specials, death/respawner and effect-triggered attack selection are explicitly unfinished. All future runtime fixtures listed here are NOT_RUN; no correction or production integration is implemented.

- **Guardian concrete incoming damage admission**: COMPOSITE, ADMISSION_GATED, CUSTOM_ROUTED, NO_STAGE_VALUE. Stage: Native eligibility, defense/phase state and teleport gates retain fixed semantics.
- **Guardian latched helmet and altar-initialized mass phase**: COMPOSITE, ADMISSION_GATED, CUSTOM_ROUTED, NO_STAGE_VALUE. Stage: Native eligibility, defense/phase state and teleport gates retain fixed semantics.
- **Guardian native helmet-loss explosion**: COMPOSITE, ADMISSION_GATED, VANILLA_ROUTED, NUMERIC_SCALABLE. Stage: Once at final per-target native Explosion hurt amount for this helmet burst; retain source/geometry/mitigation. No radius or parent-hit multiplication.
- **Guardian predicted Hug and direct air-strike teleports**: COMPOSITE, ADMISSION_GATED, CUSTOM_ROUTED, NO_STAGE_VALUE. Stage: Native eligibility, defense/phase state and teleport gates retain fixed semantics.

[Machine evidence, packages and native paths](cataclysm-r2k3a-guardian-admission.json).

Exact next task: R2k3b: Ender Guardian offense/remaining family. Start aiStep -> AreaAttack and MassDestruction, attack-selection STUN/Levitation reader, Bulletpattern -> Ender_Guardian_Bullet_Entity, spawnFangs -> Void_Rune_Entity, spawnVortex -> Void_Vortex_Entity; close native payloads/source actors, return-dependent status/control, team predicates, death/respawner and remaining combat callbacks. Reuse protected R2k3a admission/helmet/teleports and R2k2 shared/status contracts. No runtime, L2, Stage or production work.
