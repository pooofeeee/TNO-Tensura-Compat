# r2f8f - TWILIGHT_TACTICAL_MOBS_SEMANTIC_REVIEW_COMPLETE

Installed TF4.8.3345, raw Minecraft1.21.1 and exact NeoForge21.1.244 are the authority. Static research only. Ordinary mob melee retains native mob_attack (direct=causing mob), effective attributes/enchantments, armor/shield/Resistance/protection/absorption/cooldown/events and native Player difficulty scaling. No runtime HP/SHP/L2/Stage claim. Native hurt true need not mean measurable HP loss. Native control/resource/terrain callbacks are not fabricated damage events.

Adds 8 reviewed packages / 28 delivery cases. Twilight remains PARTIAL at 107/305 drafts, zero promoted. REVIEW_REQUIRED 0.

## Native contracts

### Authority

Installed TF4.8.3345, raw Minecraft1.21.1 and exact NeoForge21.1.244 are the authority. Static research only. Ordinary mob melee retains native mob_attack (direct=causing mob), effective attributes/enchantments, armor/shield/Resistance/protection/absorption/cooldown/events and native Player difficulty scaling. No runtime HP/SHP/L2/Stage claim. Native hurt true need not mean measurable HP loss. Native control/resource/terrain callbacks are not fabricated damage events.

### Redcap body

Redcap HP20, speed.28, base attack2; Sapper HP30 and base armor2, same speed/base attack. Native finalize populates mainhand iron pick and iron boots; Sapper replaces pick with Ironwood pick and boots with Ironwood boots. Both pickaxes add3 mainhand damage (Iron tier2 or Ironwood tier2 plus pick argument1), so unenchanted equipped mob attack5, not Player tool attack4. Boots supply2 armor/toughness0, yielding Redcap2/Sapper4 total armor. Ordinary spawn equipment enchantments can alter results. Native equipment updates apply attributes; displaying held Flint/TNT temporarily removes the pick modifier. Melee goal priority5 uses speed1 and normal cooldown, not item attack-speed cadence. Default visible Player targeting and retaliation remain. No extra hurt/death/HP phase, fire/TNT immunity, summon or status payload in either body. Saved native equipment persists separately from heldPick helper stack; loaded custom gear can later be replaced by goal stop restoring heldPick.

### Redcap shy

Priority2 RedcapShyGoal has MOVE/LOOK and speed1. isShy is lastHurtByPlayerTime<=0 (native recent-Player-hurt counter); not a permanent pacification flag. Entry requires target, shy, distance3..6 inclusive, target-looking predicate abs((targetYaw-(atan2(dz,dx)*180/pi-90))%360)<60 OR >300. No pitch or new ray trace in this helper. Per-goal lefty=Math.random()<.5 chooses rotation+1 or-1 radian. Destination is a snapshot radius5 around the target at Redcap minY. Continuation needs current target, captured target alive, navigation unfinished, shy, strict3<distance<6 and looking predicate. Tick looks at captured entity30/30; stop clears reference and stops navigation. This higher-priority control can preempt TNT lighting/melee; it does not modify incoming damage or grant immunity.

### Redcap avoid

Priority1 AvoidAnyEntityGoal targets PrimedTnt within own AABB inflated2 XZ/3 Y, alive, sensed LOS, nonallied and native no-creative/spectator filter; selects first candidate, not nearest. MOVE flag. Native DefaultRandomPos.getPosAway is unusually passed the Redcap own position, then candidate must be at least as far from TNT as current Redcap and produce a path. Start speed1; tick speed2 within squared distance49 else1. Continues only while navigation unfinished, not a refreshed fuse/LOS/radius predicate. No disarm, damage or immunity. Primed TNT from any legitimate source can trigger this avoidance.

### Redcap light

Priority3 RedcapLightTNTGoal MOVE/LOOK. canUse first requires canEntityGrief; if delay>0 decrement and reject, else lexicographically scan x/y/z=-8..8 around blockPosition and choose first exact TNT, not nearest/path-reachable check. No target, owner, heldTNT stock, LOS, lit-TNT exclusion or Flint durability predicate. Start equips heldFlint; continue only while stored block remains exact TNT, without rechecking grief permission. Tick looks at integer block coords; distanceSquared to lower corner<5.76 primes via Blocks.TNT.onCaughtFire(defaultState,level,pos,UP,Redcap), swings, replaces block with Air flags2, emits PRIME_FUSE and stops navigation. Otherwise navigates speed1. Stop restores heldPick and sets delay20 canUse evaluations (paused when grief gate fails). No native item use/hurtAndBreak call; Flint is not consumed. Any nearby native TNT block can be ignited, regardless planter, and Redcap/Sapper becomes the TNT owner when this priming route runs.

### Sapper plant

Only Sapper registers priority4 RedcapPlantTNTGoal. Redcap heldTNT starts1 but has no planting goal; Sapper constructor sets3. Goal has no MOVE/LOOK flags and inherits canContinueToUse=canUse; therefore it can coexist with other nonconflicting goals rather than guaranteeing exclusive combat. Entry requires target, nonempty heldTNT, distanceSquared<25, target NOT looking by the shared yaw predicate, canEntityGrief, no PrimedTnt in BBinflate8, and no exact TNT in a +/-5 cube. Start equips the same heldTNT stack; only if current blockPosition is empty, shrink1 BEFORE setBlockAndUpdate(default TNT), sound and BLOCK_PLACE. Placement return ignored; no refund if it fails. Stop restores pick. TNTLeft saves/restores stack count; no native replenishment path. Placing alone is not an explosion or hurt call; higher-priority lighting can subsequently prime it, or ordinary Player/redstone/fire/projectile/explosion mechanics can determine a different owner.

### Tnt blast

Exact244 TntBlock.onCaughtFire delegates server-only native PrimedTnt construction with supplied Living igniter. Redcap route starts fuse80 and owner Redcap/Sapper. Native fuse ticks to0, discards TNT then explodes strength4, fire=false, ExplosionInteraction.TNT. Direct entity=PrimedTnt, causing entity=its Living owner; native DamageSources selects minecraft:player_explosion whenever BOTH are nonnull, even when owner is a mob. With absent owner it selects minecraft:explosion. Both use native explosion pipeline and ALWAYS difficulty scaling on Player victims; no custom TF damage declaration. For native radius4, distance d<=8 and exposure e, request float(((q*q+q)/2)*56+1), q=(1-d/8)*e; normal shouldDamageEntity/ignoreExplosion/nonzero direction and event filters remain. No integer flooring of this1.21 formula. Native explosion armor/shield/Resistance/blast/general protection/absorption apply. Knockback follows independently of hurt return with native exposure, explosion knockback resistance and244 hook; terrain/explosion callbacks are separate. TNT interaction uses native TNT drop-decay rule, not a new canEntityGrief check at detonation, though priming/planting goal entry was grief gated. ExplosionStart/Detonate and block resistance/selection remain. Redcap owner is not excluded from its own blast.

### Tnt alternates

Sapper places ordinary default-state TNT: native Player Flint/fire-charge or a burning eligible projectile supplies that igniter/owner; redstone can prime immediately during placement with null owner. Native wasExploded creates chain TNT with previous explosion indirect Living owner and fuse randomInt(80/4)+80/8=10..29; not another Sapper charge decrement. PrimedTnt saves fuse and block state but not owner, so ordinary unload/save/load can retain fuse yet lose owner and change native source from player_explosion to explosion. restoreFrom during dimension transfer explicitly copies owner; usedPortal substitutes native portal-protecting damage calculator, no custom TF adjustment. These alternate native routes are distinguished from Redcap-owned lighting and preserve source identity rather than assigning planter credit.

### Kobold body

Kobold HP13/speed.28/attack4, registered.8x1.1, ordinary mob melee4 and leap.3. setCanPickUpLoot(true), native powder-snow-walkable tag; no custom armor/shield or damage source. Goals: Float0, panic1, seek bread2 and run-away-with-bread2, leap3, melee4, flock5, stroll6/look7; retaliation1 and custom Player target2. Native TF kobold_pacification_breads contains minecraft:bread directly, not the broader c:foods/bread tag. Standard bread has FOOD nutrition5/saturationModifier.6 and no effect; Kobold is not a Player and gets no native food bar or automatic HP heal from bread.

### Kobold pickup

SeekBreadGoal MOVE: reject while getUseItem nonempty or panicked; nextInt(10)==0 then any tagged ItemEntity in own BBinflate8 and mainhand empty. It navigates to first result at1.2 (not nearest), start and tick; no direct pickup in this goal. Ordinary server Mob.aiStep performs actual pickup only canPickUpLoot/alive/!dead/canEntityGrief, native pickup-reach box, item not removed/nonempty/no pickup delay, wantsToPickUp -> overridden canHoldItem (mainhand empty, tagged bread, !panicked). Kobold.pickUpItem splits excess count into a new dropped ItemEntity, equips exactly1 bread, sets mainhand dropChance2, discards original item, initializes lastEatenBreadTicks1/eatingTime and clears target. It does not call native equipItemIfPossible or setPersistenceRequired here. canTakeItem only permits empty destination MAINHAND plus parent admission. No special interact/feed/tame hook, owner or allegiance change. Native dropped bread, rather than a fabricated held item, is the legitimate pacification control.

### Kobold pacification

Holding a tagged mainhand stack blocks KoboldAttackPlayerTarget.canUse only; inherited continuation and HurtByTargetGoal retaliation are not overridden. Pickup explicitly clears current target once, not a universal permanent inability to attack. RunAwayWhileHoldingBreadGoal extends native AvoidEntityGoal<Player>(radius8,speed1.5/1.5), with canUse gated by held bread; inherited continuation does not repeat that held-item gate. Flock entry is also blocked by bread. On server alive+heldbread, lastEaten counter increments and positive eatingTime decrements, even while panicked; actual canEat requires FOOD component and !panicked. Initial eatingTime Easy400..999, Normal/default200..799, Hard100..699 (base+nextInt600), with decrement possible in the same aiStep as pickup. At<=0, directly calls stack.finishUsingItem; nonempty result replaces mainhand, ordinary bread mutates held stack to empty. It does not use the LivingEntity completeUsingItem/start/finish-event sequence. Native Item->Living.eat applies any actual food effects and consumes1, without Player food resources or guaranteed HP heal. lastEaten>60 plus10% roll resets only munch sound/gameevent/particles; it is not the consumption timer. Both counters save under EatingTimeLeft/TimeSinceBreadLastEaten; PANICKED is synced but not saved. Ordinary native held-item save/load retains bread; counter expiration during panic waits to consume until not panicked.

### Kobold panic

PanicOnFlockDeathGoal MOVE, speed2 for Kobold. Entry if fleeTimer>0 OR any same-runtime-class entity within BBinflate(4,2,4) has deathTime>0, then requires DefaultRandomPos.getPos(5,4) nonnull. It does not require seeing the death, attacker identity or a successful new hit. Start sets fleeTimer40, navigates, sets Kobold PANICKED true. Continue timer>0 && navigation unfinished; tick--, stop subtracts20 and clears PANICKED. Positive residual timer can trigger another start/reset40; not a guaranteed single40 world-tick duration. Default goal cadence, not requiresUpdateEveryTick. Panic suppresses canHoldItem/canEat and higher-priority MOVE can preempt lower movement goals, but does not itself clear target, grant invulnerability, change ownership, or directly subtract HP. Timer and panic resource are not saved; particles are cosmetic.

### Kobold flock

FlockToSameKindGoal has no flags. Bread-holding Kobold fails entry; else nextInt40==0 scans same runtime class in BBinflate(16,4,16), rejects list size>5. Computes average X/Y/Z over returned entities (no special alive/owner/LOS filter here); requires center distanceSquared>=25. Captures center, continuation needs25<=distanceSquared<=256; it does not refresh center or recheck bread, target, panic or count. Start moveTimer0; every10 goal tick callbacks navigation.moveTo(center,speed1). Stop clears center only. No MOVE flag means it may coexist with and issue navigation during other goals; priority alone is not a blanket suppression proof. No summons, shared HP or attack buff. Caller census confines these panic/flock constructors to Kobold in installed TF.

### Boggard

Boggard is an unregistered native class, not an established installed delivery source: full TFEntities registration surface and all-TF-class internal/dotted class-reference census find only its own class and no native producer. Its following declared behavior is assessed solely for exclusion, not promoted or exposed as a future native fixture. Boggard body: HP14/speed.28/attack3 and normal mob_attack; Float0, ChargeAttackGoal2(speed1.5,canBreak=false), normal melee3, stroll/look, retaliation and Player target with mustSee=false. Shared ChargeAttackGoal is reused from R2f5: requires captured target distanceSquared16..64, onGround, sensing LOS and nextInt10==0; snapshots targetY and overshoots horizontal position2.1. Start windup15..44 goal callbacks, sets sprinting; movement sprint multiplier1.3 and navigation1.5 are distinct. Boggard does not implement ITFCharger or use MinotaurAxe, so no synced charging flag or axe+7 payload. Even during windup, first squared-distance check <=4*attackerWidth^2+targetWidth sets hasAttacked before ordinary doHurtTarget; false hurt still spends the one attempt. Continuation windup>0 OR unfinished navigation does not refresh target/LOS/range; stop resets target/windup/attempt/sprint. No terrain break because canBreak=false, extra charge DamageType, launch, boss geometry or unique death behavior. The shared charge primitive is already reachable through protected Minoshroom/Minotaur paths; this unused class does not add a legitimate source.

### Troll body

Troll HP30/speed.25/attack7, registered1.4x2.4, ordinary mob_attack7 when melee goal active. Float1, RestrictSun2/FleeSun3, combat4, stroll/look; retaliation ignores Troll class for that goal, visible Player acquisition. Sun avoidance is native navigation behavior, not petrification, forced burning or a custom daylight defense. ROCK_FLAG syncs false initially; rockCooldown starts300..399 and block state initially null. setHasRock server adds/removes transient follow-range+8 by fixed ID (default16->24), then swaps goal: rock=true RangedAttackGoal(speed1,min20,max60,range15), false MeleeAttackGoal(speed1.2,longMemoryfalse). Does not add armor, HP, attack damage or knockback immunity. Ordinary ranged goal distance/LOS/timer controls remain, callbacks not fixed60 ticks regardless distance.

### Troll pickup

Server Troll.tick after super: only !hasRock && target!=null; positive cooldown decrements, else makes one random sample floor(x-2+rand*4),floor(y+rand*3),floor(z-2+rand*4). Outline/no-fluid ray from (blockX+.5,sampledY+.5,blockZ+.5) to sampled center must report the sampled blockPos, and sampled state must be BASE_STONE_OVERWORLD. Native raw tag: stone/granite/diorite/andesite/deepslate/tuff. If accepted, stores state then level.removeBlock(pos,false), ignores result, emits BLOCK_DESTROY. There is no canEntityGrief, EntityUtil.canDestroyBlock, hardness, inventory or drop-return gate in this TF method; ordinary world set/remove behavior still applies. If field rock!=null, setHasRock(true), create owned ThrownBlock with that state, startRiding Troll and addFreshEntity. Failed initial sample retries while cooldown0; cooldown only counts down while target present and no held rock. Rock carrying creates a real projectile entity, not just a render flag.

### Troll throw

performRangedAttack requires hasRock, creates a NEW ThrownBlock(level,Troll,rock), aims target X/Z and minY+height/3 with+.2*horizontalDistance elevation, speed1.6/inaccuracy4-difficultyId. Native constructor spawns at owner eyeY-.1 and sets projectile owner Troll. Adds it, setHasRock(false), discards FIRST passenger only if its type is TF THROWN_BLOCK, resets cooldown300..399, clears rock=null. Throw does not directly hurt and does not release/reuse the carried entity. Passenger attachment height1.25*Troll height and rotation tracking are cosmetic geometry, but carried projectile is ticked by native Entity.rideTick (zero velocity then projectile tick, unless244 pre-tick event cancels), and has no isPassenger guard in impact callback. Thus native carried contact is a separate eligible delivery if the ordinary collision engine actually admits contact; no guaranteed hit count or fabricated launch. Missing/discarded passenger does not itself clear Troll ROCK_FLAG; flags/state drive the later throw.

### Thrown hit

ThrownBlock extends TFThrowable/ITFProjectile, registered1x1 and fireproof, state defaults Stone unless constructor receives nonnull state. Ordinary ThrowableProjectile physics/gravity.03 and impact hook/deflection/collision eligibility apply. onHitEntity calls super; only server Living victim that is NOT any Troll requests twilightforest:thrown_block6. Source factory overload has NO entity or position: direct=null, causing=null, sourcePosition=null, despite projectile.owner=Troll or reflected blocker. Hurt result is discarded; broadcast3 and projectile discard happen after request even when false. Troll/nonLiving contacts do not enter this branch or discard there. No block-state-specific damage, enchantment/postattack callback, fire, status or area payload. Tags are exactly minecraft:damages_helmet, minecraft:is_projectile, neoforge:is_physical in scoped native merge. Helmet-equipped target receives native helmet durability processing and .75 damage factor (6->4.5 at that stage), then native cooldown/armor/etc; no armor/protection/Resistance bypass. It has no bypasses_shield tag, but ordinary directional shield check cannot block a null sourcePosition;244 shield event may still override. when_caused_by_living_non_player scaling is inactive because causing entity is null, so no automatic Troll difficulty multiplier or ownership/kill-credit substitution. Static attribution quirk is preserved, not repaired.

### Thrown block reflection

onHitBlock calls superclass native block projectile callback first, then server broadcast3, gameEvent BLOCK_DESTROY with projectile owner, discard; no placing/mining/dropping the carried state or hurt-success dependency. Native TF timed shield-parry path applies via ITFProjectile under pinned config (external parry mod absent, blocker within40ticks; parryNonTwilightAttacks=false still permits TF marker). AIM_DEFLECT changes projectile owner and cancels that impact; subsequent ThrownBlock entity hit STILL uses the ownerless source overload and Troll recipient veto. Reflection is not an exception that grants owner credit or makes Troll vulnerable. Ordinary native projectile owner/leftOwner collision mechanics and possible future block interactions use the new owner. ThrownBlock NBT stores BlockState and calls super to preserve native projectile owner; no custom lifetime timer. Aether/other data tags alone are not asserted as active consumers.

### Troll persistence death

Troll saves HasRock, RockCooldown and RockState only if nonnull; read always invokes NbtUtils.readBlockState on getCompound(RockState). Native missing Name produces AIR.defaultBlockState, which is nonnull. Therefore ordinary save/load of no-rock Troll can leave rock=Air with hasRock=false; at cooldown0 and target present, a failed stone sample still reaches rock!=null and creates a carried Air-state projectile. Valid later sample can overwrite it; ThrownBlock damage6 does not depend on state. Read restores follow-range/task from HasRock; native passenger save/load is separate, not reconstructed by this method. Death calls super.tickDeath then every deathTime%5==0 scans inclusive+/-12 cube (15625 positions), replaces exact UNRIPE_TROLLBER with ripe on independent nextBoolean and abs(x+y+z)%5==deathTime/5. Ordinary20-tick death visits offsets1..4; residue0 is not visited, no single guaranteed full ripening. No own server/grief/hurt-success gate, HP heal, explosion or summoned attack in these helpers; terrain/food availability is documented as an exclusion from unique combat packages. WorldUtil range proof reused. No extra Troll death boss phase.

## Packages

| Mechanic | Primary classification |
|---|---|
| Redcap shyness and TNT avoidance | CUSTOM_CONTROL |
| Redcap TNT ignition and Sapper finite planting | CUSTOM_CONTROL |
| Redcap and Sapper native TNT blast delivery | VANILLA_COMPOSITE |
| Kobold dropped-bread pickup and temporary pacification | CUSTOM_CONTROL |
| Kobold local death-triggered panic | CUSTOM_CONTROL |
| Kobold small-flock center navigation | CUSTOM_CONTROL |
| Troll rock acquisition, combat task and saved state | CUSTOM_RESOURCE |
| Troll block projectile ownerless damage | CUSTOM_DAMAGE |

## Custom source callers

| Type | Amount | Source identity |
|---|---|---|
| twilightforest:thrown_block | 6 request; native damages_helmet factor.75 at helmet stage, ordinary mitigation/events/cooldown afterward. | direct=null, causing=null, position=null; projectile owner is not passed to the source factory, including reflected path. |

## Scope and exclusions

- Full19 native class surfaces, including shared ChargeAttackGoal reused unchanged. TFArmorMaterials bytes captured for dependency proof; only Ironwood material is newly interpreted here, remaining armor review stays pending.
- Ordinary equipped melee/armor and vanilla TNT are native primitives; TF control and materially distinct source paths are explicit. No fabricated planter/reflector ownership for damage.
- Troll death ripening and Kobold munch particles are reviewed non-damage behavior, not independent combat packages. No phantom Troll petrification or Kobold healing.
- Boggard is unregistered with no external installed class reference or native producer; its declared charge behavior is excluded, not counted as a legitimate path.
- THROWN_BLOCK is USED through its actual ownerless caller;26/40 custom profiles reviewed,14 still unfinished.
- Whole Twilight still PARTIAL/zero promoted; no runtime, L2, Stage, production, balancing or Phase6/7 changes.

## Future native controls

- Redcap/Sapper native equipment, shyness/yaw/path and nearby TNT avoidance; held-tool state and late goal interruptions.
- Sapper finite placement vs ordinary Redcap ignition; grief entry/continuation, failed placement, actual igniter and source owner, native TNT chain/save/dimension paths.
- Native dropped bread and Mob pickup gates; Kobold target acquisition versus retaliation, difficulty timers/consumption, panic/residual timer and concurrent flock navigation.
- Boggard exclusion: do not instantiate an unregistered class as a native positive control; protected registered Minoshroom/Minotaur charge paths remain valid.
- Troll sampled stone/removal/cooldown/follow-range/task state, carried versus newly thrown projectile, state reload and Air-state fallback consequence.
- ThrownBlock exact6 ownerless source, helmet effect, native shield-position failure versus separate timed parry, Troll/nonLiving/block/false-hurt outcomes.

[Semantic packages and paths](semantic-sections/twilightforest-tactical-mobs.json), [integrity](twilightforest-tactical-mobs-integrity.json), [full validation](r2f8f-tactical-mobs-validation.json).

Exact next task: Continue Task C with CarminiteGolem, Adherent/HarbingerCube, MazeSlime, SnowGuardian, RisingZombie/LoyalZombie and remaining Wraith/Minotaur body coverage; then remaining items/scepters/armor/charms/projectiles/hazards/resources and14 custom caller profiles. Reuse all protected tactical/arthropod/earlier work. Protect each subsection toward R2f8 and whole-Twilight promotion; IceAndFire only after Twilight COMPLETE is pushed. No runtime boss/L2/Stage/production/fixes/Phase6/7.
