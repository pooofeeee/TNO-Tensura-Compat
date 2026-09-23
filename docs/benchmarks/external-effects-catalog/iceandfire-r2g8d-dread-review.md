# R2g8d — Dread combat and summons

Dread combat and native availability reviewed; remaining equipment and whole-mod closure pending.

Static subsection complete. Runtime fixtures unexecuted; no Stage or production implementation.

## Body damage

Ghoul aiStep requires actual target, distance<4 and current LOS: Slash ticks9 and19 each request float ATTACK_DAMAGE (base5) with mob_attack direct=causing=Ghoul, then knockback.25 independent of hurt success. Beast and Scuttler use the same range/LOS gate with Bite tick6, bases4 and7 respectively, then independent knockback.25. doHurtTarget only starts an animation and returns true, not proof of HP damage. Thrall and Knight inherit ordinary Mob.doHurtTarget (base attribute2 plus actual equipment/enchantments); unstaffed Lich uses the same melee route (base1). Keep native damage admission, armor, Resistance and L2 processing. Scale once at final hurt amount, never both attribute and event. Scream/spawn animations add no special damage or invulnerability.

## Lich summon

Mainhand exact LICH_STAFF selects DreadLichAIStrifeGoal; otherwise ordinary melee. Strife requires target/staff and calls performRangedAttack on every tick with sensing LOS. Its squared15 range controls movement, not a hard delivery range; attackCooldown field is assigned100 but unused in tick. Entity fireCooldown/minionCooldown provide actual100-tick cooldowns, decrement in aiStep, not saved. With minionCount<5 and minionCooldown0, summon takes precedence over skull that invocation: Thrall chance>0.5, Ghoul>0.35, Beast>0.15, otherwise Scuttler. Summon is immediate, not animation-frame gated; uses target, nearby native placement/finalizeSpawn, CommanderUUID=Lich and server addFreshEntity. It increments count and cooldown regardless of addFreshEntity success. Summon count/cooldown/placement are native binary/resource admission, not Stage quantities.

## Commander resource

CommanderUUID and Lich MinionCount persist. Base DreadMob resolves Player UUID first, otherwise loaded LivingEntity in same server dimension. Server aiStep copies a living Lich target when resolved. DreadMob.remove decrements a resolved Lich counter on any first removal reason, not only death, with no clamp. Beast and Scuttler override getCommander to return null: their stored commander never resolves, so no base target-follow or removal decrement. Initial summon setTarget still works. Lich also returns null. Thrall/Ghoul/Knight use base resolution. DreadHorse extends SkeletonHorse separately, resolves Player only and has no DreadMob decrement. Counts can remain stale or change on unloading; no automatic reconciliation is present. Test natural summon/kill/unload/reload without repairing counters.

## Lich skull delivery

When no summon occurs and fireCooldown0, Lich constructs owned DreadLichSkull(baseDamage6), shoot speed0, addFreshEntity, cooldown100. The owned skull constructor calls AbstractArrow(EntityType,Level), setOwner and setBaseDamage only. This constructor chain leaves Entity at (0,0,0); setOwner does not position it. Lich never sets projectile position. Therefore a legitimate Lich launch must first be tested for spawn location/delivery, not assumed to hit near its caster. Player LichStaff.use on server explicitly sets position to (playerX,playerY+1,playerZ), adds projectile, then shoots speed1/inaccuracy1 along noisy look. An earlier shoot(speed7) is overwritten; staff costs durability1 and cooldown4. No ammo/charge threshold. Preserve the native divergence; no relocation fix or synthetic hit is authorized.

## Skull homing

Skull tick before inherited arrow tick: if horizontal speed<.1 OR collision/inGround, and tickCount>5, remove(DISCARDED), without immediate return. Mob owner with target adds (targetPosition-skullPosition)*.015 to velocity; no local LOS/alive/range gate. Player owner first uses player.getKillCredit (not necessarily attacked target); if absent/dead, searches live Enemy in asymmetric projectile box expanded10, chooses nearest to Player, not nearest projectile, with no LOS/alliance filter at acquisition. Player live target steers each axis 10% toward sign(delta)*.5. NoGravity=true and isInWater=false; inherited collision/PVP/projectile-impact handling still applies. Stage belongs at final native arrow hurt amount, not homing speed or baseDamage.

## Skull damage

onHitEntity suppresses parent only when victim.isAlliedTo(owner); null owner is allowed. Ordinary AbstractArrow creates minecraft:arrow direct=skull, causing=owner (or projectile itself when no owner), amount ceil(clamp(speed*baseDamage)), plus native critical handling if applicable. These launchers do not provide firedFromWeapon/enchantment state. Normal hurt false prevents post-hurt shield wear; successful Living hit reaches doPostHurtEffects (native Enderman early return retained). Non-owner Player actively using a ShieldItem and baseDamage>=3 receives extra durability wear1+floor(baseDamage)=7 at default6, independent of actual HP lost. This does not bypass blocking or force hurt true, and is separate from HP scaling. No custom Dread damage type, freeze, soul scatter, direct SHP drain or direct HP subtraction.

## Necromancy unreachable

DreadMob.onKillEntity(LivingEntity):void is a legacy standalone method. Whole installed Iaf726-class and compat24-class instruction census finds zero calls to it; necromancyEntity is called only from it. Exact installed LivingEntity.die invokes killer.killedEntity(ServerLevel,LivingEntity):boolean, not onKillEntity; Dread classes do not override that callback. Thus native death-to-minion conversion is not a proven reachable delivery in this version. Do not promote it as an active path or manually invoke it in tests. Dormant helper would exclude Dragon, map arthropod->Scuttler, Zombie/IHumanoid->Ghoul, undead/skeleton/Player->Thrall, horse->Horse, otherAnimal->Beast, increment commander count and assign DreadMob commander. This is sufficient to explain the gap; no conversion implementation authorized.

## Defenses targets

Dread alliance treats any IDreadMob as allied, plus inherited teams. NonDread target goal preserves parent targeting, excludes IDreadMob and DragonUtils.isAlive false; hostile predicate excludes creative/peaceful Player and model-dead Dragon. Scuttler explicitly rejects Poison then calls normal canBeAffected. Installed entity tags list all seven Dread creatures as freeze_immune_entity_types (powder-snow mechanic, not Iaf Frozen); all except Scuttler are undead, Scuttler arthropod. Native healing/harming/Regeneration/Poison tag behavior and enchantment eligibility therefore matter; do not equate undead with blanket magic immunity. Registry fireImmune is false for Dread types. No custom broad hurt immunity exists in reviewed classes.

## Knight mount

DreadKnight has native horse-mount goal: when not passenger, samples unoccupied AbstractHorse within inflate(16,7,16) every4 game ticks, chooses first, approaches and at squared distance<4 sets horse tamed then startRiding(non-force). Native mount hook may reject; tamed flag is already written. No owner check, no special mounted damage packet/source or extra horse attack. Retain a mounted normal-melee fixture; ordinary horse movement/storage excluded.

## Queen exclusion

DreadQueenEntity class exists with ordinary melee attributes/equipment and boss bar, but IafEntities contains no Queen entity registration or attribute registration. Whole Iaf/compat census finds no external constructor/launch invocation; other references are instanceof rider checks and rendering. No legitimate native Queen boss delivery established. DreadQueenStaffItem is a plain Item with no active combat callback; Queen/Dread swords are standard equipment, handled by ordinary melee. Do not force-spawn an unregistered class or invent staff summons.

## Direct compat

Pinned tensura_iaf data declares cold_resistance and native spiritual-health/magicule baselines for each Dread creature; all are cold_source and no_charisma entity-tag members. Lich additionally belongs to full_gravity_control, no_fear, no_mind_control and no_possession. These are data declarations, not measured runtime immunity or a new damage source; preserve Tensura consumers and pack/tag composition for later tests. No Dread-specific compat mixin restores legacy kill conversion, skull positioning or Queen registration. Entity-existence and gear progression values are not multiplied by this research.

## Exclusions

Dread blocks, portal/spawner acquisition/worldgen, loot, texture variants, scream visuals and staff repair are excluded briefly. Registered creature combat and all reachable native skull/summon paths above remain in future runtime coverage. No runtime, Stage, L2 or production work performed.

## TNO integration decisions

- **Dread native melee HP damage**: NUMERIC_SCALABLE, VANILLA_ROUTED, ADMISSION_GATED. Stage: yes; Once at final native hurt amount in animated aiStep or inherited Mob.doHurtTarget.
- **Dread animated attack knockback**: VANILLA_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional value; Fixed native knockback independent of hurt result; retain resistance hook.
- **Lich summon and commander resource**: COMPOSITE, CUSTOM_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional value; Preserve count/cooldown and actual commander resolution, no Stage multiplier.
- **Dread skull HP damage and homing**: NUMERIC_SCALABLE, VANILLA_ROUTED, ADMISSION_GATED. Stage: yes; Once at inherited AbstractArrow final hurt amount after speed/base/crit calculation.
- **Dread skull extra shield wear**: VANILLA_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional value; Durability resource uses baseDamage, not HP amount; keep native7 default.
- **Dread tags, allegiance, immunity and mounting**: BINARY, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional value; Preserve native and Tensura admission. No Stage on tags, owner, mount or immunity.

[Machine-readable packages, native paths and future fixtures](iceandfire-r2g8d-dread.json). Validation reproduces new witnesses, checks significant call order/amounts, preserves accepted records and prior evidence, runs five tooling tests and diff checks. No whole-mod completion claim.

Exact next task: R2g9: remaining special equipment, chain/status/resource and Pixie callbacks; then whole-JAR combat/source closure, dedup/promote Ice & Fire, and continue next target if usage healthy.
