# r2f8l - TWILIGHT_BOWS_FAN_SEMANTIC_REVIEW_COMPLETE

Installed TF4.8.3345, raw Minecraft1.21.1, exact NeoForge21.1.244. Static native item/AI/impact/packet/attachment review. Source request, HP, pre-hit teleport, homing, effect delegation, motion and durability remain distinct. No runtime/L2/Stage/production/fix; protected Ice Bow/Frosted/parry/attachment primitives unchanged.

Adds 8 reviewed packages / 26 delivery cases. Twilight remains PARTIAL at 147/452 drafts, zero promoted. REVIEW_REQUIRED 0.

## Native contracts

### Authority

Installed TF4.8.3345, raw Minecraft1.21.1, exact NeoForge21.1.244. Static native item/AI/impact/packet/attachment review. Source request, HP, pre-hit teleport, homing, effect delegation, motion and durability remain distinct. No runtime/L2/Stage/production/fix; protected Ice Bow/Frosted/parry/attachment primitives unchanged.

### Bow common

Ender/Seeker/Triple registered BowItem subclasses, each384 durability. Native Player use72000/BOW with ammo and ArrowNock hooks; release ArrowLoose/ammo/draw, charge f=min(1,((t/20)^2+2*t/20)/3), requires f>=.1. Ordinary Ender/Seeker launch speed3*f/inaccuracy1; native shootFromRotation includes shooter motion. createProjectile constructs real ammo ArrowItem (ordinary/tipped/Spectral), sets full-draw crit on parent, then exact244 customArrow. Native draw processProjectileCount/ammo-use, creative/Infinity and intangible pickup rules remain, no fabricated ammo. Ordinary bow wear1 per nonempty drawn projectile entry after spawn attempt. Triple overrides release/shoot as below. Item cooldown not added by these classes.

### Arrow native

Native AbstractArrow impact source minecraft:arrow, direct actual arrow and causing current owner (self fallback if none). Request ceil(clamp(impactSpeed * native weapon-enchantment-modified baseDamage,0,Integer.MAX_VALUE)); crit if enabled adds random0..floor(request/2)+1 with integer cap. Armor/shield including pierce rules, Resistance/Protection/projectile protection, cooldown, absorption, PvP/source/event eligibility remain. Native fire ignition5s before hurt (restored on false), true Living post-knockback/enchantment/postHurt; Enderman true returns before normal postHurt. False rebounds, may drop/discard when sufficiently slow; true normally discards unless piercing, with native exceptions. Three requests do not imply triple HP because native admission/defenses remain; the conditional TF post-damage cooldown reset below can admit successive arrows. No custom DamageType from these bows.

### Ender marker

EnderBow.customArrow returns original ammo arrow and puts boolean true at persistent-data key twilightforest:ender. Preserves native ammo subtype, damage, crit, weapon/effect state. ToolEvents.onEnderBowHit is ordinary ProjectileImpactEvent listener: owner instanceof Player, EntityHitResult Living target !=owner, target NOT c:bosses, and persistentData.contains(key), not getBoolean value. No explicit side, hurt-success, health/damage, friendship, distance, collision-safe-destination or magic-resistance predicate inside TF callback. Native arrow PvP/collision and earlier event cancellation may prevent delivery; unknown cross-listener order is not asserted. Callback neither cancels event nor removes marker/arrow: normal impact can proceed afterward and multiple admitted impacts may swap again. Saved NeoForgeData preserves marker.

### Ender swap

Snapshots Player XYZ/yaw/pitch/vehicle; sets Player yaw=target yaw (Player pitch unchanged), player.teleportTo(targetXYZ), sets Player.invulnerableTime40, event46/sound. If target rides nonnull vehicle: player.startRiding(vehicle,true), target.stopRiding, ignores return. Sets target yaw/pitch=originalPlayer values, target.teleportTo(originalPlayerXYZ), event46 mistakenly uses player argument again; if original Player vehicle nonnull: target.startRiding(that,true), player.stopRiding, ignores return. Native ServerPlayer connection teleport / Entity.moveTo+passengers; ordinary Entity.teleportTo relocates only on ServerLevel. No randomTeleport safe-ground search or EnderPearl HP request. Native mount admission/hooks remain despite force; no guaranteed mount swap. Target invulnerableTime is not set. Player40 is ordinary hurt cooldown, not universal immunity/BYPASSES_COOLDOWN protection. Positions change before original hit processing; no guaranteed HP outcome.

### Seeker wrap

SeekerBow.customArrow constructs new SeekerArrow(parent, projectileStack.copyWithCount1, weaponStack). TFArrow constructor casts parent owner Living and initializes new AbstractArrow from owner/real ammo/weapon, stores parent reference; does not clone all parent flags/motion/NBT. Ordinary real Player/skeleton paths supply Living owner. New body baseDamage reset1 after constructor; onHitEntity explicitly clears crit before super, so full-draw parent crit is not inherited/applied. Native weapon enchantments at impact still modify base1; no fixed1 HP. Real ammo factories pass a copy to parent constructor, so original projectile stack retains intangible marker for replacement constructor; no inferred Infinity pickup duplication. Native pickup/weapon serialization remains.

### Seeker target

Seeker tick when !inGround && velocity.lengthSquared>1 (strict): server updateTarget, both sides steering, then super.tick. Synced target numeric entity ID defaults-1. Existing target cleared only when resolved && !alive; if unresolved getTarget null allows reacquisition. Search volume is AABB union of arrow point and velocity*5 rotated yaw +pi/6 and -pi/6, then inflateY2.5 (velocity-dependent, not fixed5 sphere). Native getEntitiesOfClass excludes spectators. Priority: first Monster with getTarget()==currentOwner, no LOS/dot check; else first non-NeutralMob Monster with LOS to arrow; else any Living with LOS, not owner, excluding same-owner TamableAnimal only when owner nonnull, maximal normalized motion/eye-target dot strictly>max(previous,.5). No c:bosses/general team/PvP filter in acquisition. First Monster paths are list-order, not nearest/best angle; new invalid-angle selection can be cleared by steering afterward. Existing target not continuously rechecked for LOS/owner/alliance; normal collision/hurt eligibility remains.

### Seeker steer

For resolved target, T=(target eye - arrow position)*.8, V=current velocity, s=|V|, q=|T|, h=sqrt(s^2+q^2), cosine=V dot T/(s*q). If cosine>.5, set velocity=(V+T)*(s/h)+(0,.045f,0); otherwise server clears target. T is not normalized, no fixed speed cap/damage guarantee; zero/NaN denominator fails > comparison. Then native arrow drag/gravity/collision. Steering may run client against synced ID. Below/equal speed1 skips steering/update; marker not automatically cleared. No terrain pass-through, teleport, direct damage or guaranteed homing hit.

### Seeker effects save

TFArrow.doPostHurtEffects calls parentArrow.doPostHurtEffects(target) if parent exists, then native super. Thus admitted normal Living hit preserves genuine tipped effects (base potion duration/8 minimum1; custom effects native direct durations) or Spectral Glowing default200/amp0 through original ammo parent. Hurt false and native Enderman early return skip it; native effect applicability remains. TFArrow parent reference not serialized; Seeker target ID also not written by subclass. Reload uses registry constructor parent=null/target-1, so inherited saved pickup/weapon/baseDamage do not restore original potion/Spectral delegate. Protected native parry changes Seeker owner, but parent owner reference stays original: HP source follows new owner while delegated effect attribution uses original parent.getEffectSource. This is actual composition, not source normalization.

### Triple volley

Triple release only Player; calls ArrowLoose before checking nonempty ammo, aborts negative charge; native draw then server shoot with speed2.5*f/inaccuracy1/crit f==1. Shoot uses constant20-degree total yaw distribution across n drawn entries (0 when n1), bypassing native processProjectileSpread. For each nonempty entry, wear getDurabilityUse=1 BEFORE construction; for j=-1,0,+1 copies ammo, adds INTANGIBLE_PROJECTILE for side copies, creates real native projectile, shoots at entry yaw, adds Y velocity .15*j, addFreshEntity return ignored. Default n1 consumes ordinary one ammo/wear1 and emits3; future native count modifiers produce3*n, not an assumed supported Multishot enchantment. Center retains original intangible status; sides creative-only pickup. Independent arrows with conditional post-damage cooldown reset below; no threefold HP promise.

### Triple post reset

Registered EntityEvents.entityHurts(LivingDamageEvent.Post) independently checks source.getMsgId().equals(arrow), causing entity instanceof Player, and Player current getItemInHand(getUsedItemHand()) is TRIPLE_BOW; then target.invulnerableTime=0. This is outside the originalDamage>0 Fiery/Yeti block: no positive final/original HP, direct-arrow class, fired-from weapon, charge, or hurt-return predicate. Native exact244 hurt sets invulnerableTime before actuallyHurt; actuallyHurt/Player override emit Post after armor/magic/absorption even final0. Thus an admitted Post can clear cooldown even on fully absorbed/fully blocked zero-HP processing that later returns false. Earlier native invulnerability/fire/PvP/incoming cancellation/cooldown rejection never reaches this callback; it cannot rescue first rejected hit. If Player still holds Triple in remembered used hand, successive admitted ordinary arrows can deal damage without ordinary cooldown; swapping away disables reset. Ordinary/Seeker/Ice/Ender arrows or reflected arrows with Player cause also qualify when current item predicate holds; Skeleton-owned Triple arrow does not. No triple-damage multiplier, bypass tag or damage-type replacement; special target overrides and other listeners remain. Other protected producers unchanged.

### Triple break

Unlike ordinary ProjectileWeaponItem.shoot, Triple damages weapon before createProjectile and has no weapon.isEmpty break guard afterward. Exact244 ItemStack.hurtAndBreak shrinks on break; native AbstractArrow constructor rejects nonnull empty firedFromWeapon with IllegalArgumentException. If actual wear breaks final bow before first construction, this native exception path is reached (no runtime crash experiment performed). Creative/Unbreaking/item hooks can prevent actual wear. Ammo draw already happened; no rollback code. Preserve as source-proven behavior, no fix or fabricated successful volley at zero remaining durability.

### Skeleton paths

Exact244 AbstractSkeleton reassessWeaponGoal and RangedBowAttackGoal accept BowItem subclasses, native Monster.getProjectile chooses held supported ammo or ordinary Arrow fallback through hook. performRangedAttack creates mob ammo arrow/getMobArrow, then ProjectileWeaponItem.customArrow, shoots speed1.6/inaccuracy14-4*difficultyId, adds entity. It does NOT call item.releaseUsing or Triple.shoot and has no bow wear/ammo split here. Ender gets real marker but owner Skeleton fails swap Player predicate until a legitimate parry changes owner to Player. Seeker wraps native mob parent/resetbase1 and can delegate ammo effects. Triple native skeleton path is SINGLE ordinary ammo arrow because inherited customArrow unchanged. canFireProjectileWeapon still literal Items.BOW in separate method; these actual AI paths do not use it as admission. Protected parry needs nonTF-projectile config for ordinary Ender/Triple arrows, while Seeker implements ITFProjectile. No bow dispenser firing behavior registered.

### Fan use

PeacockFan capacity1024, ordinary breakable durability. use computes boostFlag=!onGround && !isSwimming && !FEATHER_FAN. Client: if fallFlying, V -> .5V+1.1look+(0,1.25,0); then if boostFlag overrides Y=1.5 and scales current XZ by1.05f. Returns SUCCESS. Server always doFan first, then hurtAndBreak(fanned+1,player,hand); if boostFlag sets FEATHER_FAN true, else particles. Sound, startUsingItem(hand), returns PASS. No HP/source call, no exhaustion/full-charge guard or success check after durability break. Client/server branches are separate, not a measured final motion result. Use duration20/BLOCK; inherited canPerformAction=false means no SHIELD_BLOCK ability.

### Fan push

Server fan box centered Player eye+look*3 with radius2 on all axes. Native Entity.class query excludes spectators but does not explicitly exclude caster, allies, bosses, terrain-occluded entities or invulnerable entities. Every pushable OR ItemEntity OR Projectile: setDeltaMovement(look*2), count+1; no damage/Resistance/knockback-resistance check. Independently other ServerPlayer&&!shift: send MovePlayerPacket(look*2), add cooldown40 to item captured from player.getUseItem().getItem BEFORE this use startsUsingItem, count+2. Packet is registered playToClient and handler push adds vector to current client motion. Do not merge server replacement/client addition into guaranteed velocity4. Crouching vetoes only packet/extra count, not first push branch. Caster can be included when its box intersects (e.g. downward view). Affected projectiles keep their owner, damage type and native subsequent collision; no deflect call. Cooldown target is previous use item, possibly AIR, not necessarily Fan; no universal40-tick Fan cooldown claim.

### Fan fall

Serialized/synced FEATHER_FAN bool defaultfalse, no copyOnDeath (native attachment persistence/copy already reviewed). PlayerTick.Post while true, without side guard: setIgnoreFallDamageFromCurrentImpulse(true) resets native grace40; currentImpulseImpactPos=current Player position; then clears TFflag if ground OR swimming OR inWater. Does not directly clear native impulse context that callback. Native Player fall processing if ignore+position: snapshot storedY, try reset when grace0, if storedY<currentY no fall; else ordinary fall distance min(actualFall,storedY-currentY), native fall hooks/attributes/HP. Native tick decrements grace; saved Player impulse fields/TF attachment persist via their codecs. This limits the applicable fall calculation; not generic invulnerability, direct HP edit or guaranteed immunity under every timing/hook. Native air boost is client motion plus server marker, no second midair boost while syncedflag remains true; Elytra client branch separately checks isFallFlying.

### Fan terrain

Server WorldUtil inclusive truncated-int box: each FlowerBlock independently nextInt3==0 and uncanceled native BreakEvent -> destroyBlock(pos,true), ignored return, cost+1. Native drops requested, no additional adventure/mayUse/mobGriefing predicate in this body. Else lit AbstractCandleBlock -> native extinguish; else LightableBlock LIGHTING NORMAL or DIM -> extinguish/setLit NONE. OMINOUS excluded by Fan predicate. Extinguish adds no per-block wear; ordinary base1 still applies. No fire removal or damage inferred from name; later specific hazardous candle mechanics remain pending.

### Fan dispenser

Native registered FeatherFanDispenseBehavior queries LivingEntity only in unit AABB of block in front inflated3, explicit NO_SPECTATORS. Admission thingsToPush.size < remaining durability (strict; includes nonpushable candidates). For each pushable Living sets velocity to unit dispenser-facing vector and ordinary hurtAndBreak1 with null entity. ItemEntity alternative inside loop is unreachable because list is Living; no items/projectiles or Player move packet, no aerial flag or terrain fanning. Empty list can satisfy gate and plays success with no wear. Equal count/remaining fails even if hooks could save wear. No base1 cost; fired sound state resets after play, cloud animation separate.

## Packages

| Mechanic | Primary classification |
|---|---|
| Ender impact position and vehicle swap | CUSTOM_CONTROL |
| Seeker selection and velocity steering | CUSTOM_CONTROL |
| Seeker native arrow damage and parent effects | VANILLA_LIKE_EXTENDED |
| Triple Bow native arrow fan and pre-spawn wear | VANILLA_LIKE_EXTENDED |
| Peacock Fan native entity and Player packet motion | CUSTOM_CONTROL |
| Peacock Fan aerial impulse and fall context | CUSTOM_CONTROL |
| Peacock Fan flower removal and candle extinguish | VANILLA_COMPOSITE |
| Dispenser Fan Living motion and wear gate | CUSTOM_CONTROL |

## Custom source callers

| Type | Amount | Source identity |
|---|---|---|

## Scope and exclusions

- Eight full native class surfaces plus event/attachment/packet registrations and raw/exact244 inherited Player/skeleton paths.
- Protected Frosted/Ice Bow and general parry contracts reused; no extra custom DamageType resolved here.
- Source-proven Triple break ordering, Seeker unsaved delegate and Fan cooldown target preserved without fixes or runtime experiments.
- Other gear/hazards/utility/passive bodies and nested ASM/whole-mod compatibility closure remain unfinished.
- Twilight PARTIAL/zero promotion;29/40 custom types reviewed,11 unfinished, REVIEW_REQUIRED0.

## Future native controls

- Genuine Ender Player/Skeleton/parried impact with boss/PvP/mount/save and false-hurt controls.
- Seeker priority/steering, real plain/tipped/Spectral parent effects, native source/mitigation/parry/reload.
- Triple real Player volley/ammo/pickup/durability, conditional used-hand Post cooldown reset/zero-HP versus early rejection and single Skeleton control.
- Fan Player raw motion/packet/caster/projectile ownership and client aerial/native fall context.
- Fan terrain event/candle predicates and separate Living-only dispenser count/wear path.

[Semantic packages and paths](semantic-sections/twilightforest-bows-fan.json), [integrity](twilightforest-bows-fan-integrity.json), [full validation](r2f8l-bows-fan-validation.json).

Exact next task: Continue Task C with remaining armor/charms/food and player utility resources, then utility/passive entities, environmental hazards and11 unfinished custom DamageTypes; close installed nested ASM/mixins/events and compatibility attribution. Protect each complete subsection toward R2f8 and final Twilight dedup/promotion. IceAndFire only after COMPLETE Twilight pushed/live verified. No runtime boss/L2/Stage/production/fixes/Phase6/7.
