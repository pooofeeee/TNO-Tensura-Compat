# r2f8ab - TWILIGHT_PORTALS_SEMANTIC_REVIEW_COMPLETE

DIRECT_SOURCE_SPECIFIC: native portal tags/resources, actual TF advancement/config/structure gates and registered first-spawn attachment callbacks. GENERIC_CONDITIONAL_PRESENT: native ItemToss/entity-add/lightning-strike/dimension-travel hooks, native subtype lightning callbacks, collision and criteria. Common #c:gems/diamond is a tag extension point, not proof every mod diamond is loaded. NONE_PROVEN: this inspected portal logic has no direct Tensura/L2/Curios source mapping. UNKNOWN: pack-wide hook outcomes, actualworldgamerules and runtime transport/collision; no static compatibility certification.

Adds 5 reviewed packages / 36 delivery cases. Twilight remains PARTIAL at 262/936 drafts, zero promoted. REVIEW_REQUIRED 0.

## Native contracts

### Authority

Exact TF4.8.3345, raw Minecraft1.21.1 PortalProcessor and actual NeoForge21.1.244 references. Static only; no executed portal/boss fixture, no L2/Stage/production/Phase6/7 change. Native terrain creation, transport and genuine lightning are distinct mechanics. All40 custom Twilight DamageTypes remain USED; this subset introduces a vanilla lightning source path, not a41st custom type.

### Configuration

Pinned installed common config: newPlayersSpawnInTF=false, portalForNewPlayer=false; originDimension=minecraft:overworld, allowPortalsInOtherDimensions=false, portalCreationPermission=0, disablePortalCreation=false, checkPortalPlacement=true, destructivePortalLightning=true, shouldReturnPortalBeUsable=true, portalUnlockedByAdvancement empty, maxPortalSize64. Alternative configured branches are reviewed native paths, not claimed active defaults. Actual world gamerules remain unknown. Registered playersTfPortalDefaultDelay60 and playersTfPortalCreativeDelay1 are defaults. TFConfig rebake clears cached advancement lock, but TFPortalBlock cachedOriginDimension is initialized once and not cleared by that method.

### Creation producer

Registered PlayerTick.Post ServerPlayer+ServerLevel: !disablePortalCreation, tickCount modulus(checkPortalPlacement?20:100)==0 and profile permission>=configuredpermission. Radius is configuredpermission>=3?4:32 around player AABB. Dimension must equal configuredorigin, exact standard Twilight destination, or allowOther=true. FIRST queried ItemEntity with PORTAL_ACTIVATOR stack, canFormPortal at its block position, and Objects.equals(item.getOwner(),player) is selected. Actual ItemEntity.getOwner resolves cached/UUID thrower, not pickup target stored as Owner. Native player toss with traceItem=true supplies thrower; item-toss/add hooks remain. No arbitrary nearby ownerless catalyst or pickup-ownership substitution.

### Advancement lock

Creation and portal contact each require optional valid configured advancement for noncreative/nonspectator ServerPlayer. Lazy TFConfig lookup validates resource against actual player advancement registry; invalid/missing configured entry logs and clears config string, leaving null; a missing holder at later gate also does not reject. Static playersNotified set suppresses repeated missing-advancement toast, no serialization/removal in portal class. This is separate from tfEnforcedProgression and deeper structure gates. Config snapshot has empty lock.

### Pool validation

canFormPortal accepts actual PORTAL_POOL block tag (installed minecraft:water) OR this portal block with DISALLOW_RETURNtrue. Starting block requires below sturdyUP. Recursive horizontal flood fill requires exact SAME BlockState identity as initial poolBlock and below sturdyUP; edge requires PORTAL_EDGE (farmland/dirt_path/#minecraft:dirt) with above PORTAL_DECO. Portal decoration tag includes installed plants and native flower/leaf/sapling/crop tags, not an inferred flower-only rule. Pool visited map prevents repeats; entry increments size, maxconfigured64, minimum4. Sturdy checks pass current pool position rather than below position to isFaceSturdy. Initial state equality disallows mixed water states despite same block type. Portal activator tag is #c:gems/diamond, not hardcoded one item.

### Creation commit

Only when !checkPortalPlacement does tryToCreatePortal call isSafeAround on CURRENT level and catalyst entity with progressiongamerule; failure sends optionalplayer unsafe message and returnsfalse. NonPlayer catalyst is biome-safe under Restriction helper, though TF structure/worldborder gates still apply. Defaulttrue skips this precheck. On valid pool: shrink catalyst1, causeLightning, then replace each maptrue pool position with default usable portal usingflag2; ignore add/write results and returntrue. Successful helper return triggers MADE_TF_PORTAL criterion. No item-cost refund on creative or write failure in this dropped-item path, no break event or explosion terrain operation. Lightning is requested BEFORE pool writes.

### Lightning dispatch

causeLightning makes real native LightningBolt at block center X/Z, blockY; calls setVisualOnly(destructive), addFreshEntity (return ignored). When destructive=true and ServerLevel, independently queries Entity within AABB(blockpos).inflate3, default native query excludes spectators, then if !EventHooks.onEntityStruckByLightning invokes victim.thunderHit(level,bolt). No line of sight, team, owner or hurt-success gate. This manual query can include the newly added bolt and dropped catalyst; actual subtype callbacks decide effects. A canceled bolt add does not suppress these manual calls. No cause/owner is assigned to bolt.

### Lightning modes

With installed destructive=true: bolt is visualOnly, so automatic entity strikes and spawnFire are suppressed, but the explicit nearby thunderHit calls still run. With destructive=false: no manual query, bolt is NOT visualOnly and normal native lifetime ticks can strike alive entities in bolt-relative X/Z+-3,Y-3..Y+9; initialNormal/Hard spawnFire4 and laterflash spawnFire0 require native doFireTick. Every strike retains loader veto. VisualOnly still powers rods, clears copper and emits LIGHTNING_STRIKE at life2, as protected UrGhast review proved. No claim that false option eliminates damage/fire. Native LightningBolt is noSave; life/flashes/add admission remain native.

### Lightning damage

Native Entity.thunderHit first increments remainingFireTicks by1; if resultingtimer==0 requests ignite8seconds, then hurt(damageSources.lightningBolt(),bolt.getDamage()) with return discarded. Default exact NeoForge bolt damage5 (custom hooks could alter bolt state). Native minecraft:lightning_bolt cached source has direct=null,causing=null,position=null, exhaustion.1; scaling when_caused_by_living_non_player does not scale an ownerless source. Tags: minecraft:is_lightning,no_knockback,panic_causes,panic_environmental_causes; exact loader neoforge:is_environment. Not IS_FIRE,magic,physical,projectile,explosion or armor/shield bypass. Normal armor, Resistance/protection, absorption, cooldown/invulnerability and incoming hooks remain; native directional shield lacks source position. Fire Resistance is not immunity to this lightning request, though later fire remains fire. Fire timer update is independent of hurt result. ArmorStand/ItemEntity and thunderHit overrides retain native subtype behavior; conversions/powered state are not fabricated generic damage. No direct HP subtraction.

### Portal block

Portal default DISALLOW_RETURNfalse (property is_one_way). Outline13/16high. getCollisionShape override returns empty whenusable,13/16high whenoneway, even though registered noCollission; native BlockState collision dispatch/cache calls override. Registered hardness-1,light11,noLoot/noOcclusion,pistonBLOCK. Fluid state is flowingwater amount1; canPlaceLiquid/placeLiquid false. neighborChanged requires belowsturdyUP and eachhorizontal neighbor PORTAL_EDGE or exactsameBlockState; failure replaces block with WATER flag3. Continued survival does not require decoration above. One-way state can be reactivated through native catalyst pool validation; do not directly flip flags in a fixture.

### Contact processor

entityInside acts ONLY when state==defaultBlockState. After optional player advancement gate, entity.canUsePortal(false) then setAsInsidePortal and set overlay attachment inPortal=true. Native base eligibility is alive&&!passenger; Living additionally !sleeping. Vehicle may enter and native transfer handles passengers. Existing portal cooldown resets full cooldown on contact instead of opening processor. Otherwise same Portal identity updates position/insidebit or creates PortalProcessor. Server handlePortal first decrements cooldown, then processes; only qualifying insidebit && canChange increments time. Exact processor compares portalTime++>=delay, so from0 default60 means61 qualifying process calls, configuredcreative1 means2, nonplayer0 means1. Outside callback decays time by4 clamp0; expires<=0. These are processing counts, not measured elapsed runtime ticks.

### Native transition

Portal delay for Player uses abilities.invulnerable to choose gamerule, not isCreative; nonPlayer0. On readiness Entity sets native cooldown BEFORE asking destination; missing destination or travel veto can therefore still leave cooldown. Native Player cooldown10; baseEntity firstpassengerServerPlayer uses that delay, otherwise300. TF destination: if currentdimension is standardTF go cachedorigin, otherwise standardTF; missingserverlevelnull. Coordinate scale uses actual dimension ratio and destination worldborder clamp. Installed TF coordinate_scale.125 gives Overworld->TF8x and reverse1/8 before further routing. Native enabled-level/canChangeDimensions/onTravelToDimension gates remain; TF terrain creation can precede final travel veto.

### Transport state

TF constructs DimensionTransition with Vec3.ZERO and current yaw/pitch plus PLACE_PORTAL_TICKET. Native Entity.changeDimension honors travel veto, handles passenger transfer and native recreate/restore/remove/add, applies requested zero speed; actual base move uses restored entity pitch. Exact ServerPlayer override teleports/syncs current player, effects and attachments and does not apply transition.speed via setDeltaMovement in this method. Do not claim every player velocity is reset. No TF HP/SHP heal/subtraction. PortalCooldown is native saved NBT; PortalProcessor is not normal NBT but restoreFrom copies it during entity transfer. Native type-specific travel eligibility and lifecycle remain.

### Cache existing

TeleporterCache is shared Overworld SavedData twilightforest_teleporter_cache, keyed destination dimension then source entity blockX/Z column, not player/UUID. Values targetpos,lasttime; save/load full maps; add/remove markdirty, access timestamp update alone does not. No age expiry in class. Existing cache accepts any TF portal block includingoneway, rejects missingblock and removes entry; invalidcached path returnsnull for creation rather than fresh search in that method. Cachemiss searches accessible loaded chunks within initial X/Z+-200 and nativeworldborder, allY from min(worldmax-1,highestsection+15)down, closest3D candidate with shrinkingradiusceil(sqrt(distance²)); uses lowestvertical portal. On newmatch sourcepool recursive validator return ignored, maps true cells into cache and adds PORTAL ticket3. Return side chooses random horizontal boundary with fullUPcollision face and emptycollisionabove, elseportal itself, then safePosInColumn.

### Safe routing

Safety only restricts standardTF: outsideborder OR progressionenabled and player biome restriction missing advancement OR any LANDMARK structure reference in chunk. NonTF returnssafe; nonPlayer has no biome restriction. isSafeAround tests center and4cardinal offsets16. Unsafe destinations scan DiagonalSpiral arguments(radius128,spacing16,chunk-coordinate center)->LegacyNearestCenter, then XZQuadrant arguments128,16. Iterator implementations differ: Diagonal divides radius byspacing; XZ stores128 unscaled and emits offsets multiplied16 (up to2048). On a safe inner candidate, code returns biomeCenter rather than testedposInBiome. Ifnone, falls backoriginalpos. safePosInColumn returnsposition when entity-size AABB noCollision; otherwise setsY to heightmap at roundedX/Z without second collision check. No guaranteed hazard-free exit is inferred.

### Portal search

If no existing portal, createPosition reroutes then makePortal; loadSurroundingArea requests5x5chunks using floor(pos.x)>>4 and floor(pos.y)>>4 for Z (literalY). Searches X/Z+-16 with allY, weighted distance uses targetY*factor (Overworld2,else.5). Tries existingportal, idealspot, okay, fallbackinair, then heightmap at originalentityX/Z timesnativehorizontalScale. Ideal4x4x6 excludes FEATURES_CANNOT_REPLACE, requiresDIRTbase/replacableupper; okay allows solid/liquidbase; fallback allows anybase except protectedtag and still replaceableupper. Finalrandomfallback lacks those tests. Native helper search does not repeat border check per candidate. These exact branches are reviewed behavior, not fixes.

### Portal construction

makePortalAt writes12grassperimeter; inner4below becomeDIRT only if DIRT/REPLACEABLE/AIR; writes2x2portal whose DISALLOW_RETURN=locked||!shouldReturnPortalBeUsable. Removes4x4x5above withoutdrops, places12 random GENERATED_PORTAL_DECO (17installedchoices; fallbackSHORT_GRASS), ignores writes/removals. No BreakEvent/directHP/itemcost in generated-destination helper. Reverse cache links added for4newportalcolumns only if source portal found. createTransition finally uses heightmapcenter transition if other transition remainsnull. Separate native worldgen/block callbacks may run; no invented explosion/damage source.

### Configured spawn

Registered login data-fixes legacy PlayerPersisted twilightforest_banished flag then, if BANISHED attachment absent, calls newSpawn; respawn without respawnPosition calls it too. If newPlayersSpawnInTF and TFlevel exists: computes heightmap at currentplayerblock; portalForNewPlayerSpawn true calls createTransition(forcedEntrytrue), else NoReturnTeleporter. changeDimension return is ignored, THEN sets forced TFrespawn at originalnewDefaultSpawn (not final reroutedposition) and BANISHED Unit. Travel veto therefore does not gate these writes. Existing portal selection can bypass new one-way construction even with forcedEntrytrue. BANISHED attachment serialized/copyOnDeath. Installed newPlayersSpawnInTF=false, so this alternative is inactive in snapshot.

### No return spawn

NoReturnTeleporter reuses safe routing and same load helper; finds existingportal thenideal thenokay, returns safe center of spot.above; ifnone uses originalentity X/Z*horizontalScale and Y*yFactor+2 then safePosInColumn. Creates no portal and no new cache link; returns standard native transition. Configured source is actual CapabilityEvents, not arbitrary direct teleport call.

### Overlay exclusion

TF_PORTAL_COOLDOWN attachment name is not transport authority: builder has no serialize/sync/copyOnDeath. PlayerTick.Post ticks it. inPortal increments overlaytimer cap60, checks current/belowportal only when !isInWall; otherwise outside timer>0 subtracts2 (odd value canreach-1). ClientLocalPlayer insideportal closes nonpause/nonDeath GUI, closes container ifnecessary, clearsinsidebit. This is presentation/input behavior, not the native PortalProcessor timer or damage. Static playersNotified/toast and particles are likewise not HP mechanics.

### Compatibility

DIRECT_SOURCE_SPECIFIC: native portal tags/resources, actual TF advancement/config/structure gates and registered first-spawn attachment callbacks. GENERIC_CONDITIONAL_PRESENT: native ItemToss/entity-add/lightning-strike/dimension-travel hooks, native subtype lightning callbacks, collision and criteria. Common #c:gems/diamond is a tag extension point, not proof every mod diamond is loaded. NONE_PROVEN: this inspected portal logic has no direct Tensura/L2/Curios source mapping. UNKNOWN: pack-wide hook outcomes, actualworldgamerules and runtime transport/collision; no static compatibility certification.

## Packages

| Mechanic | Primary classification |
|---|---|
| Twilight Portal native pool/catalyst creation | CUSTOM_RESOURCE |
| Portal native lightning delivery modes | VANILLA_LIKE_EXTENDED |
| Twilight Portal native contact and transport | CUSTOM_CONTROL |
| Twilight Portal destination routing and terrain | CUSTOM_CONTROL |
| Configured Twilight initial/respawn transport | CUSTOM_CONTROL |

## Custom source callers

| Type | Amount | Source identity |
|---|---|---|

## Scope and exclusions

- Portal overlay attachment is separate from actual native PortalProcessor transport; no extra damage or native delay inferred.
- Protected Ur visual lightning rod/copper semantics reused; new mechanic is real portal manual/automatic lightning delivery.
- 40custom DamageTypes unchanged; vanilla lightning_bolt has native source/recipient admission.
- Configured new-player spawn is disabled in installed snapshot but real conditional source reviewed.
- Remaining Builder/Antibuilder/cloud/control/events/ASM/source closure is unfinished ordinary work, not REVIEW_REQUIRED.

## Future native controls

- Actual player-owned dropped catalyst in valid/invalid native pools with config/advancement/cost/permission controls.
- Real portal lightning true/false modes with add/strike veto, source identity, mitigation and native subtype/fire/world callbacks.
- Native PortalProcessor contact/eligibility/delay/cooldown/travel and actual entity/player lifecycle controls.
- Genuine cached/generated destinations with dimensions/border/progression/structure/collision/fallback/saved-data controls.
- Actual configured login/respawn events with portal/noportal, travel-veto, savedrespawn/BANISHED and legacy controls; snapshotdisabled acknowledged.

[Semantic packages and paths](semantic-sections/twilightforest-portals.json), [integrity](twilightforest-portals-integrity.json), [full validation](r2f8ab-portals-validation.json).

Exact next task: Continue remaining native Builder/Antibuilder and cloud/snow/control blocks, remaining event callbacks/nested ASM, compatibility attribution and global source exclusions. Then R2f8 whole remaining-content closure and final Twilight dedup/promotion. All40 types already USED; IceAndFire only after Twilight COMPLETE pushed/live-verified. Static only.
