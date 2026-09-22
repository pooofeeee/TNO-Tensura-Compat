# r2f8x - TWILIGHT_MECHANICAL_HAZARDS_SEMANTIC_REVIEW_COMPLETE

Installed TF4.8.3345, exact Minecraft1.21.1 and NeoForge21.1.244 evidence. Three types fire_jet/reactor/slider USED from actual calls;38/40 closed, ominous_fire/acid_rain remain. Static only; no runtime/L2/Stage/production/Phase6/7.

Adds 8 reviewed packages / 33 delivery cases. Twilight remains PARTIAL at 238/815 drafts, zero promoted. REVIEW_REQUIRED 0.

## Native contracts

### Authority

Installed TF4.8.3345, exact Minecraft1.21.1 and NeoForge21.1.244 evidence. Three types fire_jet/reactor/slider USED from actual calls;38/40 closed, ominous_fire/acid_rain remain. Static only; no runtime/L2/Stage/production/Phase6/7.

### Sources and tags

All three use TFDamageTypes.getDamageSource(level,key): direct entity=null, causing entity=null, explicit/source position=null. Even moving Slider entity is NOT a source owner/direct entity. Declarations exhaustion.1, when_caused_by_living_non_player; null cause prevents difficulty scaling. fire_jet tags: IS_FIRE, IGNITES_ARMOR_STANDS, NO_KNOCKBACK, neoforge environment/physical. reactor: NO_KNOCKBACK, environment/magic, NOT IS_EXPLOSION or IS_FIRE. slider: environment/physical, no NO_KNOCKBACK. None bypasses armor, shield, effects, Resistance, enchantments, cooldown or invulnerability. Engine explosion is independent of source tag identity.

### Native damage

LivingEntity native admission retains client/dead/invulnerability/fire-resistance gates, incoming/shield events, cooldown, armor/toughness, Resistance max(1-.2*(amp+1),0), applicable protection, absorption, damage pre/post. Null source position defeats ordinary directional shield geometry; generic loader shield event remains. Repeated <=lastHurt requests while invulnerableTime>10 may fail; excess-only admission differs from a fresh hit. TF hurt returns are discarded. Fire Jet and Reactor suppress native hurt-knockback; Slider fresh native hurt may already produce .4 ownerless random-direction knockback. Native knockback event/resistance retained. Requests, HP loss and explicit movement/fire writes are separate.

### Jet activation

Natural FireJet default IDLE, randomTicks. Server randomTick IDLE finds fuel directly below, else up to3 random X/Z offsets -1..1 at belowY. isLava accepts actual block OR fluid FIRE_JET_FUEL tag without source-fluid amount check (installed block fuel=minecraft:lava; fluid fuel=#minecraft:lava); consumes the entire selected fuel block to AIR and changes state POPPING. Encased variant is not random-ticking: neighbor change IDLE+powered ->POPPING; TIMEOUT+unpowered ->IDLE. It needs no fuel and retains TIMEOUT while powered. This body has no explicit side guard. Native neighbor updates/state admission remain. These are alternative activators of the same typed block entity.

### Jet timing

Typed FLAME_JET ticker executes only exact natural/encased blocks. POPPING preincrements counter and at>=80 resets0 then server sets FLAME. FLAME preincrements counter; at>60 resets0 and server sets natural IDLE or encased TIMEOUT, but DOES NOT RETURN. Server pulses when counter%5==0:5,10,...60 and reset0 on callback61. Thus an uninterrupted ordinary flame cycle makes13 damage/ignition opportunities, not12; occupancy, immunity and native hurt gates still apply. Protected Time core can accelerate genuine eligible block-entity callbacks, not turn these into guaranteed wall-clock seconds. Counter is not saved/synced by a custom override; saved FLAME state reload starts its counter again.

### Jet payload

Each server pulse queries Entity.class through native non-spectator query with AABB between centers of pos+(-2,0,-2) and pos+(2,4,2): X/Z[pos-1.5,pos+2.5],Y[pos+.5,pos+4.5]. It has no LOS/owner/team/living-only filter. For !entity.fireImmune(): request fire_jet2 then setRemainingFireTicks(300), independently of hurt return. Exact assignment can shorten a longer timer; no igniteForSeconds duration-enchantment calculation. Fire Resistance can reject hurt yet still receive300 fire ticks; fireImmune skips both. Subsequent native entity fire processing/water/rain/powder-snow/extinguish and on_fire damage are separate sources. Admitted fire can invoke protected Frosted downrank before later HP mitigation; early admission rejection cannot.

### Jet subtypes

ItemEntity uses native item durability/fire-resistant stack gates rather than living armor; timer assignment is still unconditional after attempted hurt for non-fireImmune entity. ArmorStand own hurt sees IGNITES_ARMOR_STANDS: it ignites when not already burning or requests native stand health loss .15 when burning, returnsfalse, then TF writes300. This differs from Fiery Block lacking that tag. Slider entity inherits Entity.hurt (markHurt thenfalse unless invulnerable) and does not define an HP pool/hurt override; its own tick omits super.tick, so do not infer ordinary baseTick fire progression for it. No attack-destroy route is added.

### Jet sources smoke

Registered block items and natural FireJetFeature are legitimate sources. Feature requires suitable5x2x5 area;4 random offsets, empty/sky-visible cell with dirt undercenter+fourcardinals, then5x5grass platform, configured jet/smoker below,3x3lava layer,stone border unless existinglava and stone floor. Actual configured/placed biome resources bound generation. Ordinary and encased Smokers only emit client smoke every4 callbacks; encased ACTIVE redstone gates it. No hurt, ignition, status or control call; no duplicate combat package.

### Reactor activation

CarminiteReactor defaults inactive. Server neighbor update latches ACTIVE=true only if all6 adjacent blocks are exact REDSTONE_BLOCK. It does not require ongoing redstone power or recheck those six during active ticking. Registered strength10/resistance6,pistonBLOCK. Native DarkTower experiment structure places inactive reactor and piston/redstone apparatus; later real neighbor changes activate it. On removal to a different block, scans27 cells in surrounding cube and destroys exact FakeGold/FakeDiamond without drops, then parent removal.

### Reactor sequence

Typed block-entity tick requires !debugWorld and ACTIVE; increments counter on both sides. Server every5 callbacks: at5,26 specific neighboring cells become FakeGold/FakeDiamond when not reactor-immune and destroySpeed!=-1 (air may be filled). Primary p=counter-80: if10<=p<=249 draws AIR shell radius(p-10)/40; ifp<=200 draws DEBRIS shell radiusp/40. Negative Java division/radii cause no useful shell, and radius0 excludes center. Secondary s=counter-120 and tertiary t=counter-160 each draw AIR when10..129 radius(value-10)/40, then nether-transform shell when0..160 radiusvalue/40. Order is significant; this is not one sphere explosion.

### Reactor geometry

Constructor RandomSource.create chooses secondary and tertiary X/Y/Z independently +/-3; if all equal, flips all tertiary signs. drawBlob loops nonnegative byte dx/dy/dz<=radius, distance=max+int(.5*middle+.25*min), selecting distance==radius and excluding origin. (fuzz+dx)%8 selects one signed octant per candidate; (fuzz+dy)%8 reaches transformBlock. Allowed replacement is exact AIR OR (!CARMINITE_REACTOR_IMMUNE && destroySpeed!=-1). Nether-transform on non-exact-AIR selects random entry of actual REACTOR_ORES;1/8 if entry present uses its defaultstate (installed tag: Nether Quartz Ore and Nether Gold Ore), else NETHERRACK. If above empty and fuzz%3==0 writes native FIRE above. Other admitted transformations directly set requested AIR/DEBRIS with flags3. No item-drop, player BreakEvent or mobGriefing predicate inside these TF writes; native level callbacks and immunity tag/hardness still apply. Fire created here later uses ordinary native fire damage, not reactor.

### Reactor detonation

At counter>=350 server destroys reactor without drops, then calls level.explode(null,ownerless reactor DamageSource,nullCalculator,integer block X/Y/Z,radius4,fire=true,ExplosionInteraction.BLOCK), then makes3 secondary+3 tertiary Ghastling creation attempts. DestroyBlock and explode returns are ignored. Native ExplosionEvent.Start cancellation can cancel explosion processing but cannot cancel later TF spawn calls by that return. No hurt-success dependency; counter/offset fields have no custom save/load, so reload ACTIVE restarts0 and rerolls lobe offsets. Removing the BE normally terminates subsequent callbacks, not a separate stored exploded flag.

### Reactor engine

Native explicit source is preserved; null source/calculator selects default ExplosionDamageCalculator. Entity range radius*2=8, distance normalized by8; skip ignoreExplosion, out-of-range or zero direction-length. q=(1-distance/8)*sampled unobstructed AABB exposure; request float((q*q+q)/2*7*8+1), up to57 before recipient mitigation, no integer truncation in this installed version. Native COLLIDER/no-fluid exposure, ray block resistance, ExplosionStart/Detonate hooks and recipient overrides remain. Source NOT explosion-tagged: no explosion-only damage protection is implied; ordinary armor/Resistance/general Protection still apply.

### Reactor movement fire

After attempted hurt, explosion engine independently computes q*defaultKnockbackMultiplier1, multiplied for Living by(1-EXPLOSION_KNOCKBACK_RESISTANCE), direction-normalizes, passes getExplosionKnockback event and adds velocity. Hurt false/zeroHP does not gate this vector; reactor NO_KNOCKBACK only suppresses LivingEntity.hurt feedback, not this engine operation. Creative-flying/spectator player exclusions shown in hitPlayers map occur after vector application; entity query/ignoreExplosion remain earlier gates. BLOCK mode uses native block-explosion drop-decay game rule rather than mobGriefing, then native onExplosionHit/loot. fire=true later chooses toBlow cells random1/3, air and solid-render below, sets BaseFireBlock.getState. Neither creation of fire nor explosion engine changes source tags.

### Reactor summons

spawnGhastNear creates actual CARMINITE_GHASTLING, positions each coordinate lobeCenter-1.5+randomFloat*3, yawrandom*360, addFreshEntity. No finalizeSpawn, spawn-rule/obstruction check, makeBossMinion, owner or team assignment in caller. Native entity-add admission can still fail. These are default10HP/wander4 Ghastlings, not Ur-Ghast6HP/wander.005 minions. Their protected ordinary LargeFireball, targeting/pumpkin/LOS, fire/fall immunity, reflected-fireball and trap/Ur-Ghast interactions are reused unchanged; this package records alternate native production, not duplicate attacks.

### Debris

ReactorDebris changes transient terrain. Its getShape uses randomized BE outline, but getCollisionShape always full block; visual holes do not provide passage. Server onPlace randomizes outline/textures. BE tick has no side/debug guard: ifwillDisappear&&timeAlive==5 OR rerolls&&randomInt5==0 rerandomizes, then whenwillDisappear increments byte timeAlive and>=60 destroys without drops. Default fresh BE rerollsfalse,willDisappeartrue,time0. Textures,bounds,rerolls,will_disappear,timeAlive are saved/loaded and sent in native update tag/packet; absent will_disappear readsfalse. Random min/grid size1/16, recursion until volume>=.125, clamps.008.. .992. Load checks min validity twice (second check also min), not a proven max-validation guarantee. Block scheduled tick would destroy itself but no autonomous schedule is established by its own body. Fake Gold/Diamond are ordinary non-loot blocks, not resources secretly awarded or additional attacks.

### Slider schedule

Slider saves AXIS(defaultY),DELAY0..3(default0),WATERLOGGED. onPlace schedules80-(int)(gameTime-DELAY*20)%80: signed int cast before remainder; initial negative/overflow values need not yield1..80. Server tick ifisConnectedInRange creates SlideBlock at centerXZ,integerY with exact currentstate then reschedules. Range test is nearest non-spectator player strictly distance<32, including creative (booleanfalse). Or recursively follows both axis directions through reference-identical full BlockStates until any qualifies; no fixed recursion distance in this body. Different delay/water state breaks connection. Real block placement/restoration can supply this path; do not invent a maze generation source without an actual caller.

### Slider movement

Moving entity registered .98x.98, blocksBuildingtrue. For axisX direction candidates DOWN,UP,NORTH,SOUTH;axisZ DOWN,UP,WEST,EAST;axisY WEST,EAST,NORTH,SOUTH. First empty cell with nonempty opposite, else first empty; ifnone, synced defaultDOWN remains. tick does not call super.tick. slideTime increments;>20 adds direction*.04 and movesSELF. Vec3.multiply(.98,.98,.98) return is discarded, so no damping from that expression. Server tick1 requires worldstate reference==myState else discards and returns; success removes original block. At60 after movement resetsvelocity0 and reversesdirection. Warmup still queries damage each server tick. No ordinary entity push/fluid push/riding; pickable whilealive, no HP-hurt override.

### Slider restore

Without collision, iftime>100 andY<minBuildHeight+1 orY>maxBuildHeight, or time>600, drops newItemStack(block) then discards. With vertical/horizontal collision: velocity*.7 assigned, discard, then native isUnobstructed(myState,pos,emptyCollisionContext) ->setBlockAndUpdate state, else block-itemdrop. That check obtains proposed collision shape and tests entity obstruction, not a general replaceability/canSurvive predicate; the TF caller has no such additional gate. State restoration preserves axis/delay/water; itemdrop preserves only block item. Damage query still follows termination branch, except earlier tick1 mismatch returns. NBT saves Time,Direction,fullBlockState; inherited native entity storage retains standard fields. No fabricated instant return teleport.

### Slider payload

Stationary block entityInside requests ownerless slider5 against ANY Entity, then Living-only knockback2 with XZdirection=(blockcenter-target)*2. Moving SlideBlock queries overlapping entities excluding self with native non-spectator predicate; Living-only requests same5 then knockback2 with(direction=sliderPos-targetXZ)*2. Hurt return is POP and explicit knockback follows unconditionally; native event/resistance/zero-direction randomization still apply. Initial native fresh-hit .4 knockback and explicit2 are separate calls, not guaranteed summed displacement. No team/owner/water/LOS predicate or cooldown-bypass tag. Stationary subtype ItemEntity/ArmorStand remains native; moving path skips non-Living items. This is damage plus control, not direct position/HP subtraction.

### Compatibility

GENERIC_CONDITIONAL_PRESENT: exact loader damage/shield/knockback, ExplosionStart/Detonate/Knockback, entity-add and native block callbacks. Scoped DIRECT_SOURCE_SPECIFIC external combat override NONE_PROVEN; external tag consumers and other-mod interaction UNKNOWN, not pack certification. Protected Time-core acceleration and Frosted incoming-fire callbacks reused. Remaining ominous_fire/acid_rain and whole-mod event/ASM/source exclusions unfinished.

## Packages

| Mechanic | Primary classification |
|---|---|
| Fire Jet native pulsed damage | CUSTOM_DAMAGE |
| Fire Jet independent native fire-timer assignment | VANILLA_LIKE_EXTENDED |
| Carminite Reactor latched terrain sequence | CUSTOM_CONTROL |
| Reactor ownerless native explosion and movement | CUSTOM_DAMAGE |
| Reactor native default Ghastling production | CUSTOM_RESOURCE |
| Reactor Debris temporary full collision | CUSTOM_CONTROL |
| Slider native contact damage and independent knockback | CUSTOM_DAMAGE |
| Slider native block-to-entity motion and restoration | CUSTOM_CONTROL |

## Custom source callers

| Type | Amount | Source identity |
|---|---|---|
| twilightforest:fire_jet | 2 per native pulse; request is not final HP. | Both null; explicit/source position null. All three use TFDamageTypes.getDamageSource(level,key): direct entity=null, causing entity=null, explicit/source position=null. Even moving Slider entity is NOT a source owner/direct entity. Declarations exhaustion.1, when_caused_by_living_non_player; null cause prevents difficulty scaling. fire_jet tags: IS_FIRE, IGNITES_ARMOR_STANDS, NO_KNOCKBACK, neoforge environment/physical. reactor: NO_KNOCKBACK, environment/magic, NOT IS_EXPLOSION or IS_FIRE. slider: environment/physical, no NO_KNOCKBACK. None bypasses armor, shield, effects, Resistance, enchantments, cooldown or invulnerability. Engine explosion is independent of source tag identity. |
| twilightforest:reactor | float((q*q+q)/2*56+1), q=(1-distance/8)*exposure; maximum57; request is not final HP. | Both null; explicit/source position null. All three use TFDamageTypes.getDamageSource(level,key): direct entity=null, causing entity=null, explicit/source position=null. Even moving Slider entity is NOT a source owner/direct entity. Declarations exhaustion.1, when_caused_by_living_non_player; null cause prevents difficulty scaling. fire_jet tags: IS_FIRE, IGNITES_ARMOR_STANDS, NO_KNOCKBACK, neoforge environment/physical. reactor: NO_KNOCKBACK, environment/magic, NOT IS_EXPLOSION or IS_FIRE. slider: environment/physical, no NO_KNOCKBACK. None bypasses armor, shield, effects, Resistance, enchantments, cooldown or invulnerability. Engine explosion is independent of source tag identity. |
| twilightforest:slider | 5 per admitted callback; request is not final HP. | Both null; explicit/source position null. All three use TFDamageTypes.getDamageSource(level,key): direct entity=null, causing entity=null, explicit/source position=null. Even moving Slider entity is NOT a source owner/direct entity. Declarations exhaustion.1, when_caused_by_living_non_player; null cause prevents difficulty scaling. fire_jet tags: IS_FIRE, IGNITES_ARMOR_STANDS, NO_KNOCKBACK, neoforge environment/physical. reactor: NO_KNOCKBACK, environment/magic, NOT IS_EXPLOSION or IS_FIRE. slider: environment/physical, no NO_KNOCKBACK. None bypasses armor, shield, effects, Resistance, enchantments, cooldown or invulnerability. Engine explosion is independent of source tag identity. |

## Scope and exclusions

- Smoker and EncasedSmoker have cosmetic client particles only; no combat payload.
- FakeGold/FakeDiamond do not yield hidden ore resources or define attacks; Reactor debris outline is cosmetic geometry over real full collision.
- Ghastling attacks/defenses and Frosted incoming-fire behavior reused from protected review, not recounted.
- Slider placed-block activation is proven; no unproven natural maze delivery is invented.
- Remaining2 custom DamageTypes, structures/events, additional ASM/compatibility/source coverage remain unfinished; no final promotion.

## Future native controls

- Genuine natural/encased Fire Jet cycles,13pulse boundary, native fuel, reload, subtype/hurt-failure and independent300firetimer controls.
- Real Reactor latch/terrain sequence, native radius4 explosion source/exposure/defenses and hurt-independent motion/fire.
- Native canceled-explosion versus six Ghastling attempts, default-vs-minion and entity-add controls.
- Reactor Debris full collision versus outline, expiry and saved-state controls.
- Stationary/moving Slider source/knockback, same-state chain, native motion/collision/itemdrop and persistence controls.

[Semantic packages and paths](semantic-sections/twilightforest-mechanical-hazards.json), [integrity](twilightforest-mechanical-hazards-integrity.json), [full validation](r2f8x-mechanical-hazards-validation.json).

Exact next task: Review Ominous Fire native damage/conversion and Acid Rain/progression to close the last2 custom DamageTypes; then finish remaining structures/events, nested ASM, compatibility and source exclusions. Protect R2f8 and final Twilight COMPLETE before IceAndFire. Static only.
