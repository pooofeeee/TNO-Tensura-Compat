# R2f7 - ALPHA_YETI_SNOW_QUEEN_SEMANTIC_REVIEW_COMPLETE

Static installed Twilight4.8.3345 / raw Minecraft1.21.1 / exact NeoForge21.1.244 review. No runtime boss tests. All protected subsections preserved.

15 new packages / 41 delivery cases; combined 60/167 drafts, PARTIAL, zero promoted. REVIEW_REQUIRED0.

## Mechanics

### Alpha admission

AlphaYeti extends BaseTFBoss and implements RangedAttackMob/IHostileMount. Base HP200, movement.38, attack1, follow40, knockback resistance.5, root3.8x5, NOT fireproof. Freeze immune through TF bosses tag; NOT in fall_damage_immune. hurt first rejects IS_PROJECTILE when !canRampage && !isTired, before super/native incoming event, regardless projectile entity identity or bypass tag. Otherwise super.hurt; only true sets canRampage=true. True need not mean HP loss (absorption/event mitigation still possible). canRampage is a private admission/AI flag, not the synced isRampaging flag or an HP threshold. setTired(any boolean) clears canRampage: damage while tired can set it, but leaving tired clears it again. No other custom HP gate, resistance multiplier, regeneration or shield resource.

### Alpha schedule

Goals: Float0; noninterruptible Tired1; Rampage3; native RangedAttack4 and ThrowRider4; home restriction, stroll/look. Retaliation then nearest visible Player targets. Ranged canUse requires randomInt50>0, target nonnull, distanceSquared>=16 and native live-target check. Native canContinue also permits a live cached target with unfinished navigation when canUse fails. Native RangedAttackGoal requiresUpdateEveryTick=true, attack interval40 calls, LOS at shot, navigation stops within40 after five consecutive visible calls; missing LOS at timer0 delays/reinitializes timing. performRangedAttack itself only fires while !canRampage, not while !isRampaging. It constructs owner=AlphaYeti IceBomb, aims at target minY+height/3 with +.2*horizontalDistance, speed1.6/inaccuracy14-4*difficultyId. Payload/Frosted are linked to accepted packages, not re-reviewed. Vehicle aiStep looks at first passenger100/100; no extra contact damage there.

### Alpha rampage

YetiRampageGoal flags MOVE/JUMP. Timeout starts10, decremented only on canUse evaluations with target nonnull && canRampage; return currentTimeOut<=0 is outside that conditional. It accumulates eligible evaluations, not necessarily ten game ticks, and expired timeout alone can admit a later evaluation. start sets duration180, synced rampage=true. continue only duration>0, not current target/alive-target/canRampage. Each tick decrements duration first; onGround sets velocity(0,.4,0) and HIT_GROUND event; destroys ownBB.inflate(1,2,1).move(0,2,0). Remaining%10 triggers random ceiling range30/hang80; %20 target ceiling hang40; remaining<40 && %10 extra random range15/hang40. %20 also emits a protected IceBomb with ownerYeti and randomly rotated velocity, speed.4+rand*.3, inaccuracy0. A full uninterrupted180 goal calls yields18 regular random attempts,9 target attempts,4 extra random attempts and9 bombs, including remaining0. These goals inherit default alternate AI-tick cadence; do not call180 a nine-second duration. stop (also interruption) resets timeout10, rampaging=false, tired=true. TiredGoal priority1 MOVE/JUMP, noninterruptible, canUse isTired, continues timer<100, tick++timer; stop timer0/setTired(false). No healing, universal damage immunity or damage multiplier while tired. Timers/flags/collisionCounter are unsaved; reload defaults unarmed/not-rampaging/not-tired.

### Alpha slam

Server causeFallDamage while isRampaging calls hitNearbyEntities BEFORE super.causeFallDamage, regardless fall distance or multiplier. All Living in ownBB.inflate(5,0,5) except self request minecraft:mob_attack5 direct=causing=AlphaYeti. Only hurt true adds velocity(0,.4,0); no target/LOS/grounded-victim/team filter. No twilightforest:slam source. Native Living fall hook/cancel and calculated self damage happen afterwards, so canceling the later fall hook does not undo the area attempt. Native calculateFallDamage uses ceil((distance-safeFallDistance)*multiplier*fallDamageMultiplier) unless type fall-immune; Entity super also propagates fall to passengers. Alpha is not fall-immune, so native self fall may be admitted and unlock canRampage. Native returned fall bool is not the area damage result; shared cooldown/armor/shield/Resistance/protection/absorption remain.

### Alpha terrain

While rampaging, each customServerAiStep with horizontal OR vertical collision increments collisionCounter. At>=15 destroy ownBB and reset0; noncollision/tired does not reset accumulated counter. Both this and rampage forward-box clearing require canEntityGrief and EntityUtil.canDestroyBlock (nonair, hardness>=0 && <50, not Container BE, canEntityDestroy and uncanceled destroy hook), drops=false. WorldUtil integer-truncates coordinates and iterates inclusive. Random ceiling producer requires canEntityGrief, picks floorX/Z+rand(range)-rand(range), starts floor(Y+eyeHeight); scans1..24 blocks upward for first BlockTags.ICE with AIR immediately below. Target producer instead starts target.blockPosition, hang40 and has NO canEntityGrief gate. makeBlockFall removes source block to AIR then addFreshEntity(FallingIce(actualState,hang)), no owner/helper predicate/restore-on-add-failure. This native difference is preserved, not fixed.

### Throw grab

Shared ThrowRiderGoal is native AlphaYeti and ordinary Yeti producer (limited Yeti registerGoals/anonymous class witnesses; full Yeti review remains Task C). canUse requires empty passengers, target nonnull, target type NOT c:bosses, target YETI_THROWING cooldown<=0 and native MeleeAttackGoal. It inherits every-tick updates. start sets throwTimer10+rand30 and chase timeout80+rand40. tick decrements timeout; while carrying decrements throwTimer, otherwise native melee tick. checkAndPerformAttack requires native canPerformAttack, native attack timer<=0, empty passengers and private cooldown--==0; sets cooldown3, resets native attack timer, swings, then if target current vehicle absent or not RIDES_OBSTRUCT_SNATCHING (pinch_beetle/yeti/alpha_yeti), stopRiding and startRiding(mob,true). No doHurtTarget/hurt at grab. Force bypasses canRide/canAddPassenger but NOT native same-vehicle/cycle/couldAcceptPassenger or NeoForge mount event; result is ignored. Continuation: carrying with throwTimer>0 OR empty with timeout>0 and native continuation. Neither boss-tag nor attachment cooldown is rechecked by checkAndPerformAttack after goal start.

### Throw release

stop if a passenger exists selects first, hostileDismount, then throwVec=(lookX*2,.9,lookZ*2). For Player, attachment thrown=true/thrower=mob, stored vector, cooldown200, immediate native push and server MovePlayerPacket; for nonPlayer only push, no thrown flag or200 cooldown. No hurt at release and native add-velocity is not knockback API/KR. HostileMountEvents hostileDismount toggles static allowDismount around stopRiding, no try/finally; other mount-event vetoes still possible. Player post-tick attachment: if thrown && (onGround||swimming||inWater), clear thrown/thrower. Independently if cooldown>0 and server cooldown==199, push stored vector AGAIN/send packet/reset vectorZERO, then decrement;200->199 first tick, second repeats even if thrown cleared. Player registration is CapabilityEvents.updatePlayerCaps. Manual UpdateThrownPacket sends bool/throwerID/cooldown, not vector. Attachment builder has no serializer/copyOnDeath/sync; no persistence/reload guarantee, fields reset by new attachment.

### Throw fall

HostileMountEvents.handleMountDamage first cancels exact IN_WALL for Player riding IHostileMount. Independently, exact minecraft:fall plus living YETI_THROWING.thrown captures current LivingIncomingDamageEvent amount, cancels original, and invokes living.hurt(twilightforest:yeeted,amount). Direct=causing=attachment thrower (nullable), no projectile; result ignored, thrown flag not cleared here. Exact FALL test prevents recursion on YEETED even though YEETED has IS_FALL tag. Native fall hook/calculateFallDamage/admission may prevent the original callback, and earlier event changes affect captured amount. DamageTypes.YEETED scaling is when_caused_by_living_non_player: boss-owned replacement receives native Player difficulty scaling although original ownerless fall did not. Armor/shield bypass and IS_FALL remain; Resistance, fall protection/protection, absorption, cooldown and fall-immune recipients apply normally. NonPlayer native throw has no flag and remains ordinary fall. Landing/water/tick ordering and persisted attachment absence matter; do not claim every throw guarantees HP damage.

### Hostile mount

Registered hostile mount callbacks cancel emitted EntityTeleportEvent for any Living riding an IHostileMount; this is not a blanket claim about every teleport API (randomTeleport has its own path). Server EntityMountEvent dismount is canceled for alive Player from alive hostile vehicle unless allowDismount or Player invulnerable ability; nonPlayer dismount is not blocked here. EntityTickEvent.Post on IHostileMount sets all passengers shift=false. Rider may interact on AlphaYeti; local attachment point(0,vehicle height,.4). Mount/suffocation/teleport controls are independent of HP damage. All other native/external event eligibility remains.

### Falling ice

FallingIce is nonLiving Entity, NOT Projectile, registered1x1/fireproof; IMPACT_PROJECTILES entity tag is not a DamageType tag. Default packed ice, hang100/time0, fall max100. Native Alpha ceiling constructor uses actual ICE state/hang40 or80; blocksBuilding=true, velocity0, no owner. tick omits super.tick, increments time, setNoGravity(time<hang), then gravity-.04 when enabled, moveSELF and drag*.98. causeFallDamage computes realDist=ceil(distance-5); if>=0 amount=min(floor(realDist*[0,.5,1,2][difficultyId]),100), queries BB.inflate(1,0,1) EntitySelector.NO_SPECTATORS, skips ANY AlphaYeti, every other Entity.hurt(ownerless falling_ice,amount). Hurt return ignored; zero request is possible. Always200 particles/sound, returnsfalse; false does NOT undo those attempts. No Frosted, ignite, secondary explosion or parry/owner transfer. isAttackable=false, isPickable=!removed, inherited Entity.hurt false. Tags physical/environment + bypasses_enchantments, not bypass_armor/fire/fall/projectile/explosion/helmet: ordinary armor/Resistance/absorption/cooldown remain; no directional shield source position. Manual difficulty coefficient is separate from Player-causer scaling (ownerless does not get latter).

### Falling ice lifecycle

After native movement/fall callback, server landing applies velocity*(.7,-.5,.7). Unless MOVING_PISTON, requires replaceable target, supported below and state.canSurvive; setBlock(flags3) success broadcasts update/discards/restores block-entity data, predicate failure discards, but setBlock failure has no explicit discard in that branch. No item drop fallback. Concrete-powder hydration branch exists but native Alpha ICE-only producer does not select it. Air state discards; airborne out-of-build-height after time>100 or lifetime>1000 discards. Native NBT saves BlockState/Time/optional BlockEntityData, not hangTime/startPos; reloaded hang becomes100 while time persists. Parent Entity saves position/motion/fallDistance/onGround. No explosion or block attack event invented; falling hurt return is independent of later placement.

### Queen admission

SnowQueen extends BaseTFBoss/IBreathAttacker, NOT BaseIceMob. Base HP200, movement/flying.23, attack7, follow40, KR.75, root.7x2.5, NOT fireproof. Freeze/fall immune through entity tags. FlyingMoveControl(10,true), noGravity=true. Body ordinary Living hurt in ALL phases: no shield-count/HP-threshold gate or phase immunity. hurt calls super, then if true && phaseBEAM adds(int)ORIGINAL argument to damageWhileBeaming; no actual-loss read, alive/hurtTime freshness check or breathing flag. Full absorption can count; rejected hurt cannot. This is request accumulation, not HP removed or mitigated event amount. isPushable=false controls collision eligibility, not all movement/damage immunity. Native separate knockback .75 resistance/events, armor/Resistance/protection/absorption/cooldown still apply.

### Queen phases

Constructor phaseSUMMON, six summons remaining, no boss-phase save methods. customServerAiStep uses three independent ifs: SUMMON && remaining==0 && countMyMinions<=0 ->DROP; DROP && successfulDrops>=maxDrops ->BEAM; BEAM && damageWhileBeaming>=25 ->SUMMON. setCurrentPhase(SUMMON) resets remaining6; DROP resets successful0/max2+rand3 (2..4); BEAM resets damage0. No timer exits BEAM without sufficient counted requests. Summon count is all IceCrystals in unit queen box inflated(32,16,32), no master/owner/alive predicate; unremoved dying/natural/another encounter crystal can count. Phase/counters/breath/goal timing unsaved; reload native HP/home persists but resets SUMMON6. Summoned crystal age/expiry is also unsaved. No healing on phase change.

### Queen shields

Seven SnowQueenIceShield TFPart/NeoForge PartEntity, no independent HP and no damage forwarding. Constructor writes dimensions(.75,.75) directly, while inherited realSize remains1x1 until setSize/packet refresh; source preserves this distinction rather than assuming every refresh retains.75. Queen after super.tick ticks/repositions all: six ring radius1 at60*i+tickCount*5 degrees, Yqueen+.1; seventh centerY-1. Part hurt returns true only if DIRECT instanceof AbstractArrow && pierceLevel>0; otherwise break sound and false. It never decrements a resource/removes a part/hurts queen. Piercing true drives native per-entity arrow bookkeeping/continuation, not shield HP; nonpiercing false follows native failed-hit bounce behavior. Root remains independently hittable where native geometry permits; no obligation to break seven shields and no source tag bypass for the geometric parts. Multipart IDs/query/impact hooks reused. No active-phase/alive guard on server part-collision loop, so callbacks can continue during native death ticks before removal.

### Queen contact

Each server queen tick after positioning queries entities except collider in colliderBB.deflate(.2,.2,.2). For each isPushable and !=queen, collided.push(collider) occurs BEFORE any hurt. If Living && queen.doHurtTarget true, adds Y+.4 and impact sound. doHurtTarget picks twilightforest:squish in DROP, otherwise minecraft:mob_attack, direct=causing=SnowQueen. Effective base attack7 plus native equipment/enchantment helper changes; no fixed extra shield damage. Native melee goal priority6 uses same method, so DROP melee is also squish, not only a successful descent. Protected EntityUtil.properlyApplyCustomDamageSource uses attacker as affectedEntity in enchantment modifyDamage and records lastHurtMob=self; success-only native enchantment/knockback callbacks retained. Other phase contact is ordinary mob source. Initial push independent of false hurt, upward push success-dependent. Multiple parts can attempt against one shared victim cooldown; never multiply seven by7 as guaranteed HP.

### Queen hover

Goals SUMMON1 / DROP2 / BEAM3 (MOVE/LOOK), then native melee6; retaliation and nearest visible Player targets plus home goals. HoverBase chooses up to100 candidates around current target: X/Z=(rand-rand)*radius, Y=targetY+height; requires candidate volume unobstructed/noCollision AND attacker current-position LOS, not candidate LOS. If all fail still uses last candidate. SUMMON hover height6/radius6: live target + phase + sensingLOS for canUse, continuation phase/live/attackerLOS/seek<=80; seek++ each tick; at distanceSquared<=3 check remaining>0 && local crystalcount<4 then summon, choose new spot/resetseek. Motion normalized offset*(.05,.1,.05)+Y.05, look30. Native FlyingMoveControl and navigation coexist with these explicit pushes; no custom boss teleport. Queen tick adds Y-.05 before super despite noGravity. Goal default alternate AI update cadence applies; no seconds claim from counters.

### Queen drop

DROP hover height6/radius0, max seek80, hover80, drop20. canUse live target/phase, no LOS gate. canContinue rejects lost target/phase/seek>80; then if distanceSquared<=1 increments hoverTimer and returns true BEFORE dropTimer test; otherwise if dropTimer<20 true, else increments successfulDrops and returnsfalse. Thus successful means timer completion away from hover point, not floor contact/actual hit/HP damage. tick increments hoverTimer if already>0 else seek; while hoverTimer<80 normalized motion(.05,.1,.05)+Y.05/look30; afterwards dropTimer++, and if queenY>snapshot targetY-1 clears ICE in queenBB.inflate(1,.5,1). No explicit downward impulse here; queen tick Y-.05 continues. hoverTimer can increment in both continuation and tick, so not80 game ticks. stop clears hover/drop counters; lost target/seek interruption need not count a success.

### Queen breath

BEAM hover height3/radius4, seek80/hover80/beam100. Live target + phase, no LOS gate; continue seek<80 && beam<100. Reaching distanceSquared<=1 permanently latches in-position for this run; in-position increments hoverTimer else seek. At hover>=80 increment beam, breathing=true, ray attack, lower hoverY by.05 but no lower than initial targetY. Movement only when distance>.5, normalized(.05,.1,.05)+Y.045; look1 when positioned else20. stop resets timers/position latch/breath. doRayAttack source=(queenX,queenY+.25,queenZ), view20, candidates queenBB.move(view*10).inflate20; remove own shields; pickable !=queen. No block ray clip. For each candidate, contains-start attacks immediately/set hitDist0; otherwise intersected entity nearer than previous hitDist (or hitDist0) attacks immediately and updates distance. This is order-dependent multiple progressively-nearer hits, NOT nearest-only postselection and NOT guaranteed every intersected target; walls are not clipped here. doBreathAttack requests4 chilling_breath, direct=causing=queen; returned hurt bool ignored, no Frosted/slow/fire/ice structure/projectile entity. Magic tag only: no intrinsic armor bypass, freeze/fire/projectile/explosion, native directional shield/armor/Resistance/protection/absorption/cooldown remain. Repeated goal attempts are not100*4 guaranteed HP.

### Queen summons

summonMinionAt constructs IceCrystal, positions at queen and addFreshEntity BEFORE up to100 randomTeleport attempts. Valid home uses gaussian offsets3/2/3 around home integer; otherwise6/8/6 around target. Native randomTeleport requires loaded target chunk, descends to motion-blocking support above min height, teleports then tests noCollision/noLiquid; failure restores original position, success broadcasts event46/stops navigation. It does not manufacture a teleport DamageSource. On success queen ENTITY_PLACE event/break; all failures leave crystal at initial location. Then setTarget(current target), setToDieIn30Seconds and remaining-- regardless add/teleport success. No owner/master/UUID field or boss-death cleanup. Independent native targeting may change target. count<4 limits the summon goal, not number of attempted constructor calls per entire phase (six budget) or all crystals in world.

### Ice crystal

IceCrystal extends BaseIceMob/Monster: HP10, speed.23, attack5; Float0, native MeleeAttack1/stroll/look, retaliation/nearest Player. Ordinary minecraft:mob_attack with native melee/enchantment processing, no Frosted callback. age0/maxAge-1 initially; queen sets600. Server aiStep increments age aftersuper and discard when maxAge>0 && age>=maxAge; no source/heal/boss-resource decrement callback. No NBT methods for age/maxAge: reloaded summoned crystal defaults unlimited lifetime, can keep nearby SUMMON count positive. BaseIceMob scales descending airborne velocityY*.6 before super; cannot ride. Biome SNOW_GOLEM_MELTS and tickCount%20==0 requests ownerless minecraft:on_fire1, outside explicit client guard (native hurt rejects client). Freeze/fall immune but not fireproof; Fire Resistance applies. SnowQueen does NOT inherit this melting behavior. Natural and summoned crystals share melee/melting; only timed-discard producer differs.

### Queen ice clear

SnowQueen.destroyBlocksInAABB requires canEntityGrief, integer-truncated inclusive WorldUtil positions and BlockTags.ICE, then destroyBlock(false) and BLOCK_DESTROY game event. It does NOT reuse Alpha general destroy helper hardness/container/canEntityDestroy checks. Producer is DROP tick while queenY>dropY. No created damaging ICE wall/ice projectile/beam-freeze placement here. Existing rotating Entity parts are separate from terrain blocks; do not infer ice shield HP or regeneration.

### Shared defense death

Both reuse BaseTFBoss home restriction/boss-spawner admission (Alpha home30 Yeti Cave; Queen home20 Aurora Palace), no ordinary home-distance hurt gate, no boss mounting/portal/far-away despawn, Peaceful valid-loaded-home spawner restoration. Neither overrides tickDeath: native20-tick Living death/removal, ordinary inherited rewards/bossbar. Their private encounter/goal flags reset on reload, native HP/home persists. Both are nonfireproof: inherited accepted lava4 first ignite5 and, if hurt true, removes exact lava in inflated9 box, separate from grief-gated clearing. No new implementation/fix or runtime outcome. Freeze/fall/entity boss tags, source tags and DamageType scaling are distinct namespaces/mechanics.

### Shared damage pipeline

Reuse protected raw Minecraft1.21.1 and exact NeoForge21.1.244 admission: native Player applies source scaling before Living hurt (when_caused_by_living_non_player: Peaceful0, Easy min(amount/2+1,amount), Normal unchanged, Hard1.5). Living source/client/dead/fire/fall immunity and incoming event, shield/cooldown, armor, Resistance/protection, absorption, downstream events decide HP. Hurt true is not measured HP loss; hurt false cannot be used to erase preceding movement/world actions. Directional shield requires usable direct source position unless bypassed. Custom shared cooldown is not bypassed here. Preserve conditional installed compatibility hooks; no native HP/SHP runtime claim or invented DamageSource.

## Packages

| Mechanic | Owner | Classification |
|---|---|---|
| Projectile admission and native defenses | alpha_yeti | BINARY_MECHANIC |
| Rampage, tired resource and native bomb scheduling | alpha_yeti | CUSTOM_RESOURCE |
| Hostile grab, dismount and launch control | alpha_yeti | CUSTOM_CONTROL |
| Thrown-player native fall replacement | alpha_yeti | CUSTOM_DAMAGE |
| Rampage landing slam | alpha_yeti | VANILLA_LIKE_EXTENDED |
| Falling ice damage and block lifecycle | alpha_yeti | CUSTOM_DAMAGE |
| Rampage terrain and ceiling conversion | alpha_yeti | CUSTOM_CONTROL |
| Summon/drop/beam phase counters and admission | snow_queen | CUSTOM_RESOURCE |
| Multipart ice-shield interception | snow_queen | BINARY_MECHANIC |
| Shield collision and phase-dependent melee | snow_queen | CUSTOM_DAMAGE |
| Hover and counted drop control | snow_queen | CUSTOM_CONTROL |
| Order-dependent chilling-breath ray | snow_queen | CUSTOM_DAMAGE |
| Independent Ice Crystal summon producer | snow_queen | CUSTOM_CONTROL |
| Ice Crystal melee, descent, melt and expiry | snow_queen | VANILLA_LIKE_EXTENDED |
| Drop-phase terrain ice removal | snow_queen | CUSTOM_CONTROL |

## Source census

| Type | Request | Source identity |
|---|---|---|
| twilightforest:falling_ice | min(floor(ceil(distance-5)*difficulty[0,.5,1,2]),100) when ceil>=0 | direct=null, causing=null |
| twilightforest:yeeted | captured exact FALL incoming-event amount before replacement native Player scaling/mitigation | direct=causing=attachment thrower (nullable) |
| twilightforest:squish | effective melee attack (base7) through native helper; DROP only | direct=causing=SnowQueen |
| twilightforest:chilling_breath | 4 per selected ray candidate; no guaranteed HP loss | direct=causing=SnowQueen |

All four USED.17/40 reviewed,23 unfinished, not unused. See [semantic packages/paths](semantic-sections/twilightforest-yeti-queen.json), [caller scan](twilightforest-yeti-queen-caller-scan.json), [native evidence](native-evidence/twilight-yeti-queen.json), [integrity](twilightforest-yeti-queen-integrity.json), [full validation](r2f7-yeti-queen-validation.json).

## Protected reuse / exclusions

- Protected IceBomb/Frosted package IDs linked; no duplicate status/producer payload research.
- No Snow Queen projectile class or Frosted breath invented: beam is direct ray hurt; shield is geometric Entity part, not a resource.
- Particles, sounds, trophies/loot, progression/home rewards and bossbar appearance are not separate damage packages.
- Ordinary Yeti producer limited to shared throw goal; its full body/target semantics remain Task C. IceCrystal complete here and must be reused there.
- No runtime HP/SHP tests, boss/L2 matrix, Stage/production, balancing or fixes.

## Future native controls

- Native Alpha projectile lock/unlock, absorbed hits, rampage/tired calls, ordinary/rampage protected IceBomb producers.
- Native Alpha slam/own fall, random vs target ceiling predicates, actual falling ice distances/difficulty/placement/reload.
- Native Alpha/Yeti grab, real Player/nonPlayer launch, hostile mount events, attachment landing/water/reload and source attribution.
- Native Snow Queen body/part piercing, contact, ordinary melee and all phases/counters/save-load; damage request versus HP.
- Native summon placement/failure/local foreign crystals, actual IceCrystal melee/melt/expiry/reload.
- Native hover/drop completion independent of hurt, ray order/wall/inside-origin/cooldown, grief controls and death callbacks.

Installed Twilight4.8.3345 + raw Minecraft1.21.1 + exact NeoForge21.1.244. Prior four compatibility scans retained; source/owner/event controls conditional. No runtime integration or HP/SHP claim.

Exact next task: Task C: remaining Twilight combat content, using existing installed source aids and protected subsections. Resolve remaining23 custom DamageType callers plus remaining mobs/minibosses, weapons/scepters/staves, armor/charms, projectiles/hazards/resources/control, source/delivery/compatibility mapping and exclusions. Preserve each complete subsection before continuing toward R2f8; final Twilight promotion follows full semantic closure. No runtime boss/L2, Stage/production, balancing/fixes, Phase6 reopening or Phase7. Ice and Fire may start only after full Twilight completion and promotion are pushed/live verified.
