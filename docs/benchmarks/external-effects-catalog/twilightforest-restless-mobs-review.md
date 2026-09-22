# r2f8h - TWILIGHT_RESTLESS_MOBS_SEMANTIC_REVIEW_COMPLETE

Installed TF4.8.3345, raw Minecraft1.21.1 and exact NeoForge21.1.244. This section closes the previously partial Wraith/Minotaur body and actual RisingZombie delivery, reusing protected HAUNT/AXING/helper/charge semantics. Requests are not measured HP loss; no new source type, runtime or production change. Normal damage admission, native events, armor/shield/Resistance/protection/cooldown/absorption remain wherever not explicitly overridden below.

Adds 4 reviewed packages / 20 delivery cases. Twilight remains PARTIAL at 116/346 drafts, zero promoted. REVIEW_REQUIRED 0.

## Native contracts

### Authority

Installed TF4.8.3345, raw Minecraft1.21.1 and exact NeoForge21.1.244. This section closes the previously partial Wraith/Minotaur body and actual RisingZombie delivery, reusing protected HAUNT/AXING/helper/charge semantics. Requests are not measured HP loss; no new source type, runtime or production change. Normal damage admission, native events, armor/shield/Resistance/protection/cooldown/absorption remain wherever not explicitly overridden below.

### Wraith body

Wraith is FlyingMob/Enemy, not Monster: HP20, speed.5, attack5, dimensions.6x2.1, registered fireproof. Constructor sets noPhysics=true and NoClipMoveControl. Native FlyingMob has no fall-check payload, no climbing and its own friction/travel, not ordinary gravity navigation. TF also tags fall-damage-immune, freeze-immune and undead. No custom damage cap, incoming phase, self-heal, life timer or death attack. canRide=false, careful stepping true, despawns in Peaceful. Full hurt calls super first; only true may set current target to source.getEntity if Living, not self, not current vehicle/passenger and not source.isCreativePlayer. It uses causing entity, not direct projectile. Rejected hurt cannot trigger this custom retaliation.

### Wraith attack

Protected alternate HAUNT path: doHurtTarget first requests twilightforest:haunt using current ATTACK_DAMAGE (normally5), direct=causing=Wraith; discards that hurt return, then unconditionally calls super.doHurtTarget, a separate ordinary mob_attack request using native attribute/enchantment melee processing. Method returns the SECOND result. This is not one10-damage hit or guaranteed double HP damage: equal requests commonly meet native damage cooldown, while source admission, prior state, equipment/enchantments and incoming hooks can differ. HAUNT is magic-tagged but not armor-bypassing; ordinary mob_attack is physical. Native Player difficulty scaling, shield/armor/effect processing and callbacks apply separately. No first-hit-return gate or direct health subtraction. Protected Knight/Wraith HAUNT profile remains unchanged.

### Wraith goal

SimplifiedAttackGoal priority4 has no flags. canUse needs nonnull target and native isWithinMeleeAttackRange; inherited canContinueToUse calls canUse. requiresUpdateEveryTick=true. start/stop reset attackTick0. A tick with counter>0 only decrements; otherwise checkAndPerformAttack requires counter<=0, native melee range and hasLineOfSight, stores adjustedTickDelay20 (20 because every-tick), swings and calls doHurtTarget without using return. Thus uninterrupted attempts have20 decrement callbacks plus the next attempt callback (21), not an unconditional20-world-tick promise. Reentry resets counter and may attempt sooner. Movement through walls does not waive attack LOS. Nearest Player target acquisition uses mustSee=false but native combat/range/invisibility/team eligibility still applies.

### Wraith motion

Priority2 home goal,5 fly-to-target,6 random float each flag MOVE and return false from continuation, so each supplies a destination on start. Target goal captures current target XYZ at speed.5. Random goal needs no target and within home plus squared wanted-distance<1 or>3600, picks each coordinate independently within +/-16 at speed.5. Home goal requires outside valid home and no target, picks homePos.relative(random six-direction).offset(nextInt5,nextInt5,nextInt5), requires loaded position and uses speed.85. Look goal7 flag LOOK faces velocity when no target, otherwise target if distanceSquared<4096. NoClipMoveControl only when operation MOVE_TO: postdecrement courseChangeCooldown<=0 then adds nextInt5+2 to the decremented counter and adds normalized-to-destination velocity*.1*speedModifier. No obstacle/zero-distance guard or operation reset is present; zero-distance division is an installed edge, not a fabricated corrective clamp. This changes self-motion, not a victim teleport or damage.

### Wraith home

STRUCTURE or SPAWNER finalizeSpawn stores current dimension/block position as home before super. Natural/egg/command do not acquire home from this override. EnforcedHomePoint home is valid only nonnull and same dimension; absent/wrong-dimension is treated as within. Valid radius test is block-position squared distance<400, strict boundary. HomePos uses GlobalPos codec; legacy Home list loads in TF dimension. No attack/velocity/course counter serialization is added. Home goal only without target; it does not cap pursuit at radius20 or teleport the Wraith. Saved home persists normally across reload.

### Minotaur body

Minotaur HP30/speed.25/native base attack2, dimensions.6x2.1, ordinary armor0 before external equipment, not fireproof. Goals Float0, Charge2(speed1.5,canBreak=false), native melee3(speed1), stroll/look, retaliation and nearest Player mustSee=false. No custom incoming hurt/phase/regeneration/death payload. CHARGING synced defaultfalse, getter/setter; aiStep only adds .6 animation speed while true. It is not a separate damage multiplier or saved charge resource. Native health/equipment persists; its own class has no NBT override. Finalize calls parent, then this override populates ONLY mainhand (not parent random armor), then native equipment enchantments.

### Minotaur equipment

Equipment roll uses entity.getRandom().nextInt10 (not the RandomSource argument), q=effectiveLocalDifficulty+1, result=(int)(roll/q). result0 equips gold_minotaur_axe, else vanilla golden_axe. Both registered tools have gold tier bonus0 + axe6 -> unenchanted settled native ATTACK_DAMAGE8; different attack-speed modifiers (-3.2 TF versus -3 vanilla) do not set mob goal cadence. The probability depends on local difficulty and exact integer truncation, not a fixed10 percent. Native equipment attributes/enchantments must have settled before fixture measurement. Neither weapon callback is automatically a Player hurtEnemy call for mob attacks.

### Minotaur charge

Protected ChargeAttackGoal applies with Minotaur-specific squared entry distance16..64 inclusive, ground, current-target LOS and nextInt10==0; no Minoshroom +9 range offset. Destination overshoots2.1 horizontally, targetY snapshot; windup15..44 goal callbacks, sprint true immediately; speed1.5 navigation starts when windup predecrements to0. Native sprint multiplier1.3 is separate. Continuation is windup>0 OR navigation unfinished, not renewed target/LOS/ground checks. Each tick including windup checks captured target minY distanceSquared<=4*width*width+targetWidth (normally1.44+targetWidth), sets one-attempt flag BEFORE attack. No hit-time LOS test in this charge goal, no success retry; ordinary melee goal has its own native admission. canBreak=false suppresses this goal terrain destruction entirely. Stop resets sprint/CHARGING/target/windup/attempt. Full protected charge semantics reused; no new phase or permanent state.

### Minotaur damage

Actual Minotaur AXING caller uses protected EntityUtil.properlyApplyCustomDamageSource, direct=causing=Minotaur, normal effective attack8 and helper enchantment quirks. On sprint, ToolEvents native incoming +7 applies ONLY current mainhand instanceof MinotaurAxeItem; vanilla golden axe has no bonus. Native Player difficulty scaling precedes +7: without enchantments ordinary8; TF axe sprint Normal15/Easy12/Hard19 before mitigation; plain gold sprint stays D(8). CHARGING flag alone is not predicate. Both axes retain native axe Player-shield disable100 and ordinary armor/shield processing; the extra incoming amount is independent of final hurt return. Do not duplicate protected axe/AXING implementation or relabel as Minoshroom slam.

### Rising body

RisingZombie is Monster with registered Zombie.createAttributes, not a Zombie subclass. Defaults HP20, speed.23, attack3, armor2, followRange35; entity dimensions.6x1.95/eye1.74 before rising height scaling. It declares no attack/target goals, no outgoing hurt caller, no zombie sun-burning or reinforcement override. Zombie-tag membership does not import Zombie class methods. RISING_TICKS synced0, not serialized by this class; default dimensions scale vertical height by ticks/130, refresh on data change; isInvisible exactly ticks==0. isImmobile always true disables normal input but is not a universal position lock; knockback/doPush/pushEntities empty, isPushablefalse, no fluid affect/push, cannot ride or use portal even force. Other external motion/position code is not universally intercepted.

### Rising gaze

aiStep calls super first. If ticks>0 and notDeadOrDying, server increments by1; every resulting multiple10 below130 only sound, client branch only particles. Otherwise on tickCount%10==0 selects getNearestPlayer(this,FOLLOW_RANGE/2), normally radius17.5 with strict squared distance<radiusSquared, nearest NO_SPECTATORS; creative is not excluded, and this overload does not require alive. Only that nearest player is considered; no scan for a farther player if the nearest fails gaze. Trigger uses normalized Player view dot normalized vector from Player eye to zombie X/Z and one of three Y offsets (eyeY,Y+.5*scale,mean eyeY/Y), requiring dot>.5 (strict60-degree cone; distance-normalization disabled). Custom LOS clips FROM zombie X/eyeY/Z TO Player X/zombie-selected-yOffs/Z using VISUAL blocks, Fluid.NONE, same level, distance<=128, result MISS. The endpoint is not Player eyeY. Trigger branch has no explicit server/alive/NoAI check; actual server progression is authoritative. Gaze sets1; once active, subsequent progression needs no continuing player/gaze/LOS.

### Rising conversion

After branch handling, server ticks>=130 calls native convertTo(EntityType.ZOMBIE,true), then newZombie.setHealth(old.getHealth()) and matching Y rotation. Normal trigger tick stores1 and129 subsequent live server aiStep increments reach130; not130 additional ticks after trigger. No HP heal is inferred: current damage transfers through native setHealth clamping to new maximum. Exact244 Mob.convertTo creates native Zombie, copies position/baby/NoAI/name+visibility/persistence/invulnerable and, because transferInventory=true, pickup flag, nonempty equipment via copyAndClear and drop chances; adds fresh entity, moves mount if any, discards old and returns new. It does not call Zombie.finalizeSpawn or copy old active effects/target/custom attributes; no owner/master/shared HP pool. No explicit conversion-event predicate is present in this actual method. Native addFreshEntity return is ignored; removed old or failed create can return null, and TF does not null-check before setHealth. No fix or claimed runtime failure. RISING_TICKS not saved means ordinary preconversion reload restarts at0/invisible; the converted Zombie saves as minecraft:zombie.

### Rising admission

RisingZombie.isInvulnerableTo returns ONLY source.is(minecraft:in_wall); no superclass call. This explicitly rejects in_wall regardless of normal superclass bypass logic and omits superclass Entity removed/Invulnerable-NBT/fire/fall-type checks, NeoForge CommonHooks.isEntityInvulnerableTo and Living enchantment-immunity check at that gate. Do not claim total invulnerability while underground/rising, and do not claim the native Invulnerable flag or damage-immunity enchantment is honored through this overridden gate. Subsequent Living.hurt server/dead/FireResistance/incoming-event/shield/cooldown/armor/effect/protection/absorption processing remains; there is no direct health subtraction. No special TF source or incoming cap; movement vetoes do not imply HP immunity. Converted Zombie restores ordinary native superclass admission.

### Zombie delivery

Native converted Zombie is a new ordinary entity with default attack3/armor2/HP20 maximum before transferred equipment and health; ctor registers native ZombieAttackGoal and vanilla targets. No random baby/jockey/equipment/local-difficulty reinforcement/leader roll from finalizeSpawn is invoked by convertTo. Native ordinary Mob melee and Zombie.doHurtTarget then apply: only successful super hurt, empty mainhand, attacker on fire and randomFloat<.3*effectiveLocalDifficulty can ignite victim for2*int(effectiveLocalDifficulty) seconds. This inherited vanilla follow-on is not a TF source and does not exist in the RisingZombie precursor. Other vanilla zombie systems remain native; no new TF-controlled summon owner or fabricated attack.

### Producers

Actual TF registry field census: Wraith has native egg, large HollowHill controlled spawn weight2/group1..2 and level3 spawner selection nextInt11==10; floor feature spawner branch floatChance<.025 routes getMobID(level3) to that choice. Graveyard feature Full grave with nextBoolean creates Wraith at selected placement, calls EventHooks.finalizeMobSpawn(...STRUCTURE), then addFreshEntity; native home assigned in finalization. Minotaur has egg, Labyrinth weight20/group2..3 and MazeRoomSpawnerChests postProcess native spawner at local4,2,4. RisingZombie has no egg; LichTower yard config weight2/group1..2 (separate from interior ordinary zombie10), plus Graveyard DATA marker spawner: remove marker, nextInt4==0 and successful setBlock SPAWNER, nonnull SpawnerBlockEntity then setEntityId RisingZombie. Registered Monster placement/engine caps/spawner eligibility still apply; concrete config entries are not guaranteed spawn counts. No runtime creation executed. Template chest/TNT/cosmetics are terrain infrastructure/native TNT reuse, not an undocumented monster attack.

## Packages

| Mechanic | Primary classification |
|---|---|
| Wraith native flight, home and attack scheduling | CUSTOM_CONTROL |
| Minotaur actual equipment and charge delivery | VANILLA_COMPOSITE |
| Rising Zombie gaze and native conversion | CUSTOM_CONTROL |
| Rising Zombie exact source immunity gate | BINARY_MECHANIC |

## Custom source callers

| Type | Amount | Source identity |
|---|---|---|

## Scope and exclusions

- Nine full declared native class bodies complete; protected charge/helper/HAUNT/AXING packages reused, not redone. Shared EnforcedHomePoint and actual world producers pinned.
- Wraith sounds/turning visuals and Minotaur charge animation are not damage packages. Rising particles/sounds are cosmetic and never damage the ground.
- Rising precursor is Monster despite Zombie attributes/tag: no ordinary zombie outgoing attack, sunlight burn or reinforcement before actual conversion. Native converted zombie behavior is an alternate vanilla source, not a new TF DamageType.
- No custom DamageType advanced:26/40 reviewed,14 unfinished. LoyalZombie and scepter resources remain next, not silently claimed complete.
- No runtime tests, Stage/L2/production edits, balancing or compatibility fixes. No IceAndFire before final Twilight completion.

## Future native controls

- Wraith two actual requests and individual native admission, result/callback controls and LOS/cadence.
- Wraith obstacle-free movement/home, creative-source retaliation, producer and reload differences.
- Minotaur two native gold weapons, local-difficulty rolls, AXING/helper/sprint/difficulty/shield controls and terrain-disabled charge.
- RisingZombie actual nearest-player/gaze geometry, strict radius/cone, progression and save state.
- Damaged native conversion with equipment/flags versus uncopied effects/attributes, then actual vanilla Zombie source.
- Exact Rising in_wall gate versus ordinary native damage, motion veto and restored postconversion superclass admission.

[Semantic packages and paths](semantic-sections/twilightforest-restless-mobs.json), [integrity](twilightforest-restless-mobs-integrity.json), [full validation](r2f8h-restless-mobs-validation.json).

Exact next task: Continue Task C with LoyalZombie/ZombieWand ownership, targeting, feed/Strength/expiry and shared scepter durability/recharge native paths; then remaining utility/passive entities, items/armor/charms/projectiles/hazards/resources and14 unfinished custom DamageTypes. Preserve all prior sections. Protect each subsection, finish R2f8, then whole-Twilight dedup/promotion. IceAndFire only after Twilight COMPLETE is pushed; no runtime boss/L2/Stage/production/Phase6/7.
