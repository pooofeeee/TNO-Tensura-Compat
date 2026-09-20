# R2f4 — NAGA_SEMANTIC_REVIEW_COMPLETE

Installed Twilight Forest4.8.3345 / Minecraft1.21.1 / NeoForge21.1.244. Static native review only. Frosted and Lich remain immutable; whole Twilight PARTIAL.

8 reviewed package drafts, 18 delivery cases; REVIEW_REQUIRED0; no custom Naga DamageType. Combined Twilight drafts: 19 packages / 55 cases; zero final promotions.

## Combat semantics

### Ordinary melee

SimplifiedAttackGoal canUse requires Living target and native melee-range intersection; checkAndPerformAttack also requires LOS and attackTick<=0. Native unmounted reach is head AABB inflated XZ by sqrt(2.04F)-0.6, not a segment-count radius. Goal flags are empty and requiresUpdateEveryTick=true, so it coexists with movement. Start/stop resets counter0; successful admission sets adjustedTickDelay(20)=20 before calling doHurtTarget and ignores its return. With uninterrupted goal execution,20 decrement calls precede the next attack call (21 tick-call spacing); re-entry can attack immediately. Outside blocking special branches and while !isDazed, super Mob.doHurtTarget requests minecraft:mob_attack using effective ATTACK_DAMAGE (registered base5) modified by native weapon enchantments. Success enables native enchantment post-attack/knockback and then Naga adds victim velocity(-sin(yaw)*2,0.4,cos(yaw)*2). False suppresses that extra push. The HP hit is ORDINARY_MELEE; only the extra delivery/control is a special package. True hurt can occur with no actual HP loss.

### Charge block

Before normal melee, target must be Living and isBlocking. Exact244 isBlocking requires active nonempty use item, SHIELD_BLOCK ability and use elapsed>=5; no facing/source-angle test is added by Naga. With movement state CHARGE, victim server velocity receives (1.5*vx,0.5,1.5*vz), Naga receives(-1.25*vx,0.5,-1.25*vz), using original Naga motion. ServerPlayer gets durability request5 on current use item, then registered play-to-client MovePlayerPacket whose handler adds(3*vx,vy+0.75,3*vz) to client motion. Do not add those server/client vectors into one guaranteed resulting velocity. Naga then requests ownerless minecraft:generic2 on itself, ignores its return, plays block sound, enters doDaze and returns false without ordinary victim melee. Thus false does not mean no self damage or no movement. Self recoil can be rejected by its existing hurt cooldown yet daze still starts. Native durability/Unbreaking/creative rules remain;5 is requested durability, not guaranteed loss.

### Stunless block

Same initial Living/isBlocking gate, but movement state STUNLESS_CHARGE. ServerPlayer: durability request10, then addCooldown(current use-item item,200), stopUsingItem and broadcast shield-break animation. These are not contingent on damage success. The item is read again after durability handling; if it broke, do not assume the cooldown necessarily names the original shield. Other Living blockers do not receive this Player-only disable branch. Requests minecraft:mob_attack4 directly (not Mob.doHurtTarget, no ATTACK_DAMAGE/weapon-damage modification and no normal post-attack callback), ignores hurt return, changes pattern to CIRCLE and returns false. Player stopped using can take the ordinary mitigated hit; nonPlayer blocker retains native facing shield admission. No special armor/Resistance bypass is created.

### Parts link

Naga constructs12 NagaSegment objects; each TFPart extends NeoForge PartEntity<Entity>, retaining a final parent reference and the parent EntityType/world. They are Entity, not LivingEntity, and have no HP/armor/effect pool. Parent getParts always returns all12; exact244 tracking inserts/removes all into the part map, and world entity queries append intersecting parts. Client recreate assigns parentId+i+1; TF part data synchronizes positions/dimensions/data. Native interaction lookup uses getEntityOrPart; ordinary reach/world-border/attack hooks still apply. TFPart.isPickable always true; inherited Entity.canBeHitByProjectile is isAlive && isPickable. NagaSegment.is(entity) accepts itself or parent, but the inspected world query uses identity and does not deduplicate by parent.

### Parts forward

NagaSegment.hurt forwards the SAME DamageSource and amount*2F/3F to parent.hurt when !isInvisible; returns parent result. It neither calls own super.hurt nor subtracts local HP. Multiplication/division occur before parent invulnerability, incoming event, armor, Resistance/protection, absorption and shared hurt cooldown. This is a fixed segment-hit reduction, not a head damage cap or projectile immunity. Two-thirds applies to bypass-tagged sources too; parent source-specific rejection remains. Source direct/causing entities are unchanged and checked against home bounds at the head.

### Parts contact

Each parent tick calls tick on every part BEFORE repositioning it. NagaSegment tick, when !isInvisible, queries its current AABB. Only entity.isPushable candidates call collideWithEntity. It first invokes recipient.push(part), independently of hurt; for a Living recipient other than ANY Naga, when parent !isDazed and !isDeadOrDying, it then requests minecraft:mob_attack2, or6 if recipient instanceof Animal. Source direct/causing=parent Naga, not the part. Result ignored; no LOS, target, team/owner test, bespoke cooldown or weapon/enchantment post-attack call. Multiple overlapping segments can attempt in one parent tick; recipient native invulnerability normally rejects equal later requests. Native collision push checks same vehicle/noPhysics/sleep and position, and does not use the damage-return gate. Nonpushable entities receive neither this push nor contact hurt. Dazed/dead parent stops contact damage, but not the preceding push.

### Parts activity

activate sets size2x2 and own invisible flagfalse; deactivate sets size0x0 and own flagtrue. However TFPart.isInvisible returns PARENT.isInvisible, and NagaSegment does not override it. Consequently local deactivation does not make the hurt/contact !isInvisible predicate false while parent visible. All12 remain returned/moved; zero-sized boxes still can intersect a containing AABB and projectile selection inflates hitboxes, so loss is not a proven absolute untargetability/contact-disable guarantee. Parent Invisibility suppresses all segment forwarding/contact regardless their local active flags. This is a resolved installed-code discrepancy, not REVIEW_REQUIRED or a fix. Native generic Entity isAlive only tests removal; dead parent alone does not mark parts removed until parent cleanup.

### Parts geometry

Every parent tick: update segment count, super.tick, then for each of12 tick/contact followed by position. Leader=head for first, previous part thereafter; normalized existing separation plus head/leader facing straightenForce=0.05+0.5/(i+1), or0 if head dead. Final adjacent offset length2; in-wall part adds vertical correction before normalization. This changes real contact geometry, not just renderer animation. Native part push(D,D,D) does not forward movement to head and next positioning can overwrite displacement. Head isPushable=false prevents ordinary collision shoving, not hurt knockback/manual pushes. Incoming LivingEntity knockback retains registered KR0.25; explicit Naga velocity writes do not read that attribute.

### Multi hits

Generic Entity queries/AoEs can include head plus multiple parts and make separate forwarded requests; LivingEntity-only AoEs exclude the parts. No Naga-wide attack-ID deduplication exists. Native piercing-arrow ignored IDs are per hit entity, so head/parts are separate candidates, bounded by piercing and collision/return handling. Forwarded requests share head invulnerableTime/lastHurt: equal/lower during>10 is rejected unless BYPASSES_COOLDOWN, larger admitted request contributes only excess over prior amount. A later head hit can therefore add the difference after a reduced segment hit; do not multiply full damage by13. A successful ordinary nonpiercing arrow discards. Parts are not Living, so native arrow potion/post-hurt/knockback callbacks that require Living target do not automatically run on parent. Native Player attack routes successful item.hurtEnemy to the part parent, but enchantment post-attack still receives the originally hit entity; a legitimate sweeping Living-only query may additionally hit head if geometry/eligibility permits.

### Defense

Naga.isInvulnerableTo ordering: nonnull causing entity outside home -> true; nonnull direct entity outside home -> true; IS_EXPLOSION -> true; else super. Home uses floored block positions relative to valid same-dimension restriction point, inclusive |dx|<=46, |dy|<=7, |dz|<=46; invalid/missing home returns true for within-home. No own-position test is added to this damage predicate. Ownerless/directless environment bypasses only the entity-position checks. Thus an inside projectile from an outside owner still fails. These early home/explosion rejections precede super and have no BYPASSES_INVULNERABILITY exemption. Registered EntityType fireImmune=true rejects IS_FIRE through native Entity invulnerability; installed fall_damage_immune tag similarly rejects IS_FALL. Normal native invulnerability event can affect that later superclass decision. Naga also overrides isInLava false, not universal immunity to all unnamed damage. No Naga projectile/magic whitelist, flat cap, daze-vulnerability multiplier, shield resource or HP-phase admission threshold exists.

### Native damage

Admitted head damage uses exact244 LivingEntity pipeline: invulnerability/client/dead/fire-resistance checks; incoming event; shield/freeze/helmet changes; invulnerableTime>10 rejection or excess; normal armor/toughness, Resistance and protection, absorption, pre/post events/death. No Naga cooldown reset or special short iframe. Naga.hurt only acts after true super return: resets ticksSinceDamaged=0, and if isDazed adds (int)original method argument to damageDuringCurrentStun. This integer accumulator is not actual HP loss; body reduction has already happened, but armor/absorption/cooldown excess have not changed this argument. Server AI forces CIRCLE when accumulator>15 and resets it then only; it is not reset by entering/leaving each daze, so subthreshold totals can carry between dazes. ForceCircle changes state/counter, and daze flag clears when CIRCLE tick executes.

### Health segments

Registered base HP120, speed0.5, attack5, follow80, KR0.25, stepheight2. Constructor stores final healthPerSegment=getMaxHealth()/10 =12 for native attributes BEFORE finalizeSpawn. Non-Easy finalization adds difficulty_health_boost +130 Hard else+80 and fills health once: native Easy120/Normal200/Hard250. Denominator remains12; it is not recomputed from finalized maxHP or later changes/load. Each tick N=clamp(int(HP/12+(HP>0?2:0)),0,12). All difficulties therefore keep12 segments until HP<120; normal/hard do not use proportional ten-percent segment losses. Alive lowHP retains2, HP0 yields0. On count change, server replaces transient segment_speed_boost ADD_VALUE with float(12/N*0.02), so effective base speed normally0.52 at12 through0.62 at2 before other modifiers. N=0 calculation is unguarded floating-point Infinity, not division exception; native ranged-attribute sanitization/clamping remains. It is not proof of an infinite-speed living attack. No direct HP-based attack-damage multiplier.

### Segment lifecycle

When N drops old->new, parts indices[new,old) receive deathCounter=(old-i)*12 and remain active-sized until their countdown reaches0. Thus lost parts can continue their actual contact during staged loss. Completion makes particles/sound, resets parent.deathTime=0 and deactivates size0. Growth calls activateBodySegments for ALL indices<new, repositioning them near head; it does not clear existing part deathCounter, so a previously scheduled countdown can later deactivate a reactivated part. No independent severed-part life/damage pool. Parent removal server-side kills all12. Naga server removal waits deathTime>=124 (BaseTFBoss), with segment countdown completion resetting that counter; corpse duration is therefore not always exactly124 after lethal HP loss. HP0 still activates native dead hurt rejection; presentation/deferred removal is not extra HP or mandatory per-segment killing.

### Regeneration

customServerAiStep increments ticksSinceDamaged; when>600 AND divisible by20 it calls native heal(1). First uninterrupted eligible call is620, then640 etc, not600. Counter resets only on true Naga.hurt; a rejected source does not postpone regen. Heal uses native alive/health/event/clamp behavior, not setHealth bypass. Segment count can grow on following tick and reduce speed modifier. Counter, stun accumulator, current count, movement state/counters and part death counters are not custom NBT-saved by Naga/parts; ordinary parent health/attributes/home remain native-saved and constructor-derived denominator remains12 on ordinary reload. There is no permanent severing state.

### Movement

MovementPattern requires target and both self/target in home. Default/stop state CIRCLE counter15, clockwisefalse; stop does not itself clear DATA_DAZE/CHARGE/STUNLESS. Goal MOVE/LOOK, default requiresUpdateEveryTick=false; native Mob schedules it on full selector ticks, generally alternating ticks. State counter advances only when navigation done, using postdecrement (counter--<=0 transitions); while path active it waits or stops a stuck path. These counters are NOT fixed wall-clock attack seconds. Circle clears daze/charge (which clears stunless), uses radius12/14 alternating, radius16 when counter2 and rotation0.1 instead of1 when counter1. CandidateY=min(head.minY,targetY). Intimidate stops/looks, sets forward input.1 and counter +=15+randInt10. One calculation picks stunless with randomFloat*.75 < clamp(.75-HP/maxHP+difficultyId*.05,0,.5), giving probability threshold/.75 capped2/3. It is a choice probability, not a50% cap or hard HP phase.

### Rush daze

Intimidate transition flips clockwise; if target.minY>head.maxY selects CRUMBLE else charge. Crumble counter20+randInt20, then charge. Charge/STUNLESS counter2 sends navigation to target-relative radius5/rotationPI at speed multiplier1.5, sets DATA_CHARGE; no independent rush DamageSource/damage bonus. CIRCLE uses speed1.0. Custom move control DAZE sets strafe xxa0; CHARGE or INTIMIDATE multiplies strafe by.8; other states INCLUDING STUNLESS_CHARGE use cos(tickCount*.3)*.6; native MoveControl may further set movement. These are real movement inputs, not decorative body animation. doDaze sets state/nav-stop/counter60+randInt40 but DATA_DAZE only sets during DAZE tick; DATA_CHARGE then clears. doCircle counter +=10+randInt10, forceCircle resets10+randInt10; neither immediately clears synced flags. DAZE blocks normal head melee/body damage when bool set, but collision push/externally applied velocity remains; no MobEffect or universal immobilization is created.

### Terrain

customServerAiStep, gated by EventHooks.canEntityGrief and loaded box: x/z head BB±.75; y floor(minY+(shouldDestroyAll?1.01:.5)) to floor(maxY+1). Leaves are destroyed with no drops; other blocks only if charging OR head outside home and EntityUtil.canDestroyBlock succeeds. NagaSmashGoal canUse horizontalCollision+grief; server start uses same XZ with y min+1.01 to maxY (no+1); leaves OR charging/outside-home helper rule. Leaves short-circuit the helper hardness/container/per-block test, though the outer grief and loaded-region gates remain. Helper requires hardness>=0 and<50, nonair, no Container block entity, block.canEntityDestroy and uncanceled LivingDestroyBlockEvent. Default loader block permission for Naga allows, but custom blocks can override. Grief event defaults to mobGriefing and is externally alterable. These destroy real obstacles/support and pressure combat navigation; they are not extra direct damage.

### Crumble home

CRUMBLE tick calls crumbleBelowTarget(2) and(3). Grief+target needed, int(target.minY)>int(head.minY). For each range r, dx/dz=int(target coord)+rand(r)-rand(r), dy=targetY-rand(r)+rand(r-1); ifdy<=floor substitutes targetY. Helper permission as above, destroys with drops; no bespoke direct damage or LOS requirement. Any later fall damage is native environment, not Naga damage. Combat targeting clears when target distanceSquared>6400 or either outside home; native player target selector also checks home, retaliation remains native. Every20ticks with valid home and headY<homeY-5, teleport to integer homeXYZ and stop navigation. This is positional recovery, no teleport damage/invulnerability/refill. Path shortcut advances nodes while horizontal distance<4*headWidth (normally8), not a body-contact damage radius.

## Package classification

| Package | Primary classification |
|---|---|
| Naga ordinary melee with added push | VANILLA_LIKE_EXTENDED |
| Naga charge block recoil/daze | CUSTOM_CONTROL |
| Naga stunless charge shield disruption | VANILLA_LIKE_EXTENDED |
| Naga linked body routing/contact | VANILLA_LIKE_EXTENDED |
| Naga source/home damage admission | BINARY_MECHANIC |
| Naga HP/body/speed and regeneration | CUSTOM_RESOURCE |
| Naga combat movement state machine | CUSTOM_CONTROL |
| Naga combat terrain destruction/recovery | CUSTOM_CONTROL |

## Source/delivery cases

| Case | Source |
|---|---|
| head_melee | Ordinary head melee |
| charge_player_block | Native Player block during CHARGE |
| charge_other_block | Other Living blocking during CHARGE |
| stunless_player_block | Native Player block during STUNLESS_CHARGE |
| stunless_other_block | Other Living blocker during stunless charge |
| body_nonanimal | Native segment contact with non-Animal Living |
| body_animal | Native segment contact with Animal |
| head_incoming | Native incoming hit to head |
| part_incoming | Native incoming hit to body part |
| multipart_overlap | One native delivery intersecting multiple parts |
| segment_loss_growth | Native HP loss and subsequent regeneration |
| regen_daze_counter | Native accepted/rejected hurt and idle regeneration |
| movement_cycle | Native movement state/HP choice |
| adjacent_terrain | Head adjacent terrain clearing |
| collision_smash | Horizontal collision NagaSmashGoal |
| high_target_crumble | High target CRUMBLE |
| home_recovery | Native boss-spawner home and recovery |
| death_cleanup | Native lethal HP and staged part cleanup |

Each saved case includes native predicates, parameters and future controls in [machine-readable section](semantic-sections/twilightforest-naga.json). No runtime fixtures were executed. Native mob_attack requests are ordinary armor/Resistance/protection/absorption/cooldown damage; generic2 recoil is ownerless, armor-bypassing and no-knockback. Explicit push callbacks remain separate.

## Exclusions and evidence

- Ordinary Mob.doHurtTarget HP damage alone is ORDINARY_MELEE, not a new CUSTOM_DAMAGE package. Included package is its extra success-dependent push.
- Hiss/rattle/block sounds, crit/angry/poof particles, red overlay, bossbar10notches, tail renderer rotations and124tick presentation trail are not extra damage/status. Real segment positioning and death-counter resets are retained.
- Ambient RandomStroll radius30/Y7 and purely visual interpolation are not separate effects. Combat circle/charge/strafe changes are real movement inputs and retained.
- Loot chest/advancement/worldgen/progression acquisition is excluded. Terrain destruction is included only as obstacle/support pressure and home recovery; no invented damage source.
- Installed Twilight contributes alexscaves:resists_acid entity tag for Naga. This declaration alone is not proven immunity; external Alexs Caves consumer attribution belongs to its later mod review, which was not started.

Native Twilight + Minecraft + exact NeoForge21.1.244, reusing four pinned candidate scans from Frosted. No direct Naga-specific patch proven there. Generic damage/status hooks remain conditional on real dispatched events, source owner/recipient and head-versus-part callback differences; no pack-wide guarantee or fixes. Installed multiplayerFightAdjuster=NONE snapshot is reused, so native multiplayer HP bonus is disabled in that pinned configuration.

[Native evidence](native-evidence/twilight-naga.json), [raw comparison](vanilla-evidence/twilight-naga.json), [exact loader](reference-evidence/twilight-naga-244.json), [integrity validation](twilightforest-naga-integrity.json), [full checkpoint validation](r2f4-naga-validation.json).

Exact next task: Begin Minoshroom + Knight Phantom semantic review from existing installed Twilight source aids. Naga, Lich and Frosted are complete subsections; do not repeat them. Then Hydra + Ur-Ghast, followed by Alpha Yeti + Snow Queen. No Ice and Fire, runtime boss/L2 tests, Stage/production, balancing or Phase6/Phase7 work.
