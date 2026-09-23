# r2f8ac - TWILIGHT_CONTROL_BLOCKS_SEMANTIC_REVIEW_COMPLETE

DIRECT_SOURCE_SPECIFIC: native tower/cloud/portal tags and three actual registered TF transformers; optional gravestone block tag is explicit integration. GENERIC_CONDITIONAL_PRESENT: native fall/incoming/teleport hooks, native rain-query and precipitation consumers, extensible conduit frame and block tags. NONE_PROVEN: inspected control logic has no direct Tensura/L2/Curios mapping. UNKNOWN: runtime transformer application, third-party hooks/tag changes/world gamerules and pack-wide outcomes. Static trace is not compatibility certification.

Adds 5 reviewed packages / 36 delivery cases. Twilight remains PARTIAL at 267/972 drafts, zero promoted. REVIEW_REQUIRED 0.

## Native contracts

### Authority

Installed TF 4.8.3345 and exact nested ASM, Minecraft 1.21.1 and NeoForge 21.1.244 are the static authority. Prior protected sections and all 40 USED custom DamageTypes are preserved. No runtime fixture, L2, Stage, production or Phase 6/7 change. Native terrain control, fall mitigation and native rain consumers are separate mechanics; no fabricated cloud damage source.

### Builder producer

Actual registered carminite_builder creates the typed TOWER_BUILDER block entity. DarkTowerMain.addTopBuilderPlatform and makeBuilderPlatform place default inactive Builders with native unpowered levers; makeBuilderPlatforms routes to them. Genuine placed block/redstone callbacks also supply the native path. Default state BUILDER_INACTIVE; only ACTIVE state supplies its ticker, and block entity tick work is server-side. Builder hardness 10/resistance 6, piston BLOCK; built_block hardness 50/resistance 2000, full native collision despite noOcclusion, no loot, piston BLOCK.

### Builder activation

Server neighborChanged INACTIVE+powered writes ACTIVE, sounds and schedules 4 ticks. ACTIVE+unpowered writes INACTIVE and schedules 4; TIMEOUT+unpowered writes INACTIVE without scheduling. These are separate checks on captured original variant. Server onPlace INACTIVE+powered writes ACTIVE and sounds but does NOT schedule or startBuilding. Scheduled ACTIVE+still powered calls letsBuild only if the actual block entity exists and is not makingBlocks. Scheduled INACTIVE/TIMEOUT requires a non-null cast block entity, resets counters and activates six adjacent Built Blocks for removal. Initial powered placement alone can therefore run the idle countdown rather than start construction.

### Builder tracking

startBuilding sets makingBlocks=true then resetStats. When making and trackedPlayer is null, nearest player within strict distance 16 from block center is selected using getNearestPlayer(...,false): native NO_SPECTATORS includes creative and has no explicit alive predicate. No owner, team, line-of-sight or subsequent range/alive revalidation. Direction is floor(pitch*4/360+1.5)&3: 0 UP, 2 DOWN, otherwise player horizontal getDirection. Without a player, nextFacing is null and construction can wait indefinitely without adding blockedCounter.

### Builder build

While making on server, increment ticksRunning; every 10 counts, with lastBlockCoords and direction, inspect adjacent destination. If blocksMade<=16 AND isEmptyBlock, set native inactive built_block with flags 3, sound, advance last coordinates, clear blockedCounter and increment blocksMade; write return is ignored. Starting at 0 permits 17 placement branches, not 16. A blocked destination or exhausted allowance increments blockedCounter; >0 then stops making, clears tracked player and resets stopped counter. No direct hurt, setHealth, entity displacement or player placement/break event in this body; resulting collision is native terrain behavior.

### Builder removal

When active ticker is not making, it clears trackedPlayer; ++ticksStopped==60 writes TIMEOUT and schedules 4 ticks. Builder scheduled inactive/timeout or actual block replacement activates exact adjacent built_block if not ACTIVE: writes ACTIVE and schedules 10 ticks. TranslucentBuiltBlock scheduled ACTIVE removes itself without drops then activates all six neighbors; removals/writes are not success-gated. This is a propagating terrain-removal chain, not an attack or lock search.

### Builder persistence

Block state and native scheduled ticks persist normally. Block entity has no custom save/load methods for makingBlocks, tracking, counters or last position. resetStats resets blocksMade, last position, ticksStopped and blockedCounter, but NOT makingBlocks, ticksRunning or trackedPlayer. Inactive block states have no ticker, so a power cycle may retain making/tracking/cadence in the live block entity; reload reconstructs those transient fields. No guaranteed fresh owner or ten-tick phase is inferred on each power cycle.

### Antibuilder producer

Actual antibuilder creates typed AntibuilderBlockEntity; ticker available on both sides, client branch only particles. Native Dark Tower unbuilder maze and makeBuilderPlatforms place the block. Server operation requires hasNearbyAlivePlayer(center,16): strict distance <16, native NO_SPECTATORS AND LIVING_ENTITY_STILL_ALIVE; creative is admitted. Antibuilder hardness 10/resistance 6, light 10, no loot, piston BLOCK. Absence of a qualifying player clears snapshot and tickCount, not the other transient counters.

### Antibuilder snapshot

After qualifying range increments tickCount, server captures 9x9x9=729 BlockState references only if snapshot null and areaLoaded radius 4; starts slowScan. Existing snapshot scans every tick when fast, otherwise tickCount%20==0. Only block TYPE identity differences are tested, so same-block properties, inventory and block entity NBT changes are not restored. revertBlock true keeps original snapshot, sets fastScan and ticksSinceChange=0. False adopts current state as new baseline. More than 20 unchanged scan results returns to slow mode. Snapshot and all counters lack custom NBT persistence; leaving/re-entering range or reloading captures a new world baseline.

### Antibuilder revert

Reject/adopt change if current is AIR and original snapshot does not block motion, current destroy speed <0, or current/original is in ANTIBUILDER_IGNORES. Otherwise each scan has nextInt(10)==0 write chance. Original non-air becomes default ANTIBUILT_BLOCK, not the original material/state/inventory; original air becomes AIR. If current is air, emit block-break level event for replacement. Then native Block.updateOrDestroy(current,replacement,level,pos,2). Returns true even if randomness declined or write had no effect, so pending eligible changes keep fast scanning. Installed ignored tag does NOT contain antibuilt_block, including common_protections expansion: replacement can remain a type mismatch with original forever; native same-state updateOrDestroy then does nothing on later write attempts.

### Antibuilder native removal

Native Block.updateOrDestroy checks replacement identity. Replacement AIR calls server destroyBlock with dropItems=(flags&32)==0; flags 2 therefore permits normal native drops. Non-air calls setBlock with flags&~32. Native drops/removal/block callbacks remain; no original inventory restoration, direct player BreakEvent, HP operation or ownership claim. ANTIBUILT_BLOCK is ordinary full-collision Block, no loot/noOcclusion, hardness .3/resistance 2000, piston BLOCK. Source ignored tag includes redstone_lamp, tnt, water, specified tower machinery, common_protections and optional gravestone:gravestone. Optional tag entry is source-specific integration evidence, not proof of loaded pack behavior.

### Cloud producers

Native block items/resources provide wispy_cloud, fluffy_cloud, rainy_cloud and snowy_cloud. Trollcave CloudComponent places wispy/fluffy through setIfAir; CloudTree and CloudCastle foundations place fluffy. GrowingBeanstalk cloud replacement is reused from the protected structural-utilities review. Wispy has collision height 14/16 despite forceSolidOff/replaceable/noOcclusion, hardness .3/resistance 0 and no randomTicks; fixed precipitation NONE. Other three have ordinary full Block collision, hardness .8/resistance 0 and randomTicks; all piston DESTROY. Client CloudEvents rendering/sounds and registered EntityEvents.addCloudJumpParticles do not change velocity, server weather, effects or HP.

### Cloud fall

All four inherit fallOn -> entity.causeFallDamage(distance,.1,damageSources.fall()), discarding return and not calling parent fallOn. Native Entity forwards to passengers unless FALL_DAMAGE_IMMUNE, and returns false. Living first runs CommonHooks.onLivingFall; canceled hook returns false; otherwise uses hook-adjusted distance/multiplier, then superclass/passengers and calculateFallDamage. Immune type yields 0; otherwise ceil((double)((distance-(float)SAFE_FALL_DISTANCE)*multiplier)*FALL_DAMAGE_MULTIPLIER). With unmodified inputs multiplier=.1 BEFORE rounding. No additional Jump Boost subtraction in this formula. If computed >0, native sound then hurt(fall,computed) return discarded and causeFallDamage returns true even when hurt fails. Not universal 90% final HP reduction or unconditional fall immunity.

### Native damage identities

Exact machine-readable vanilla-source profiles pin declarations and installed tag membership. fall/drown/magic/dry_out factories are cached ownerless sources: direct null, causing null, position null, so when_caused_by_living_non_player does not scale them. fall bypasses armor/shield, is_fall/no_knockback and NeoForge physical; drown bypasses armor/shield/wolf armor, is_drowning/no_impact/no_knockback/wither_immune_to and environmental; magic bypasses armor/shield/wolf armor, no_knockback, magic and its native subtype tags (including Twilight breaks_lich_shields, which alone does not establish a legitimate Lich shield break). dry_out is environmental, bypasses wolf armor but NOT armor/shield. None is fire/projectile/explosion or bypasses effects/resistance/enchantments/invulnerability/cooldown. Native Resistance/protection/absorption/incoming hooks and recipient-specific admission remain. No success implies HP delta, and no SHP bypass is introduced.

### Cloud precipitation

Installed commonCloudBlockPrecipitationDistance=32 (config range 0..INT_MAX); 0 disables additional rain query and random precipitation. Fluffy null mode uses biome precipitation only if global rainLevel>0, with that intensity. Rainy always RAIN/1; snowy always SNOW/1; wispy NONE/1. Server randomTick requires areaLoaded radius 1 and distance !=0, positive intensity and RAIN/SNOW. Start highest=cloudY-1; scan y=Y-1 while y>Y-distance and current state is not MOTION_BLOCKING opaque, assigning highest=y-1. If highest>minBuildHeight, snow logic then invokes actual block.handlePrecipitation at highest for either rain or snow. This does not set global weather or manufacture fluid/rain damage.

### Cloud snow cauldron

Snow: gamerule snowAccumulationHeight>0; position highest+1 within build height, BLOCK light<10, current AIR or SNOW and default SNOW.canSurvive. Existing layers increment only below min(rule,8), call native pushEntitiesUp then setBlockAndUpdate; fresh snow writes default state. No freeze/Frosted callback. Native cauldron precipitation is an actual consumer: empty cauldron uses random<.05 rain -> WATER_CAULDRON level1, <.1 snow -> POWDER_SNOW_CAULDRON level1. Layered cauldron requires matching precipitation and level!=3, increments one with same random gate. Subsequent native burning-entity content contact clears fire, then mayInteract gates level consumption; snow content converts to water while lowering. Other actual block overrides remain dynamic, not universal farmland/fire behavior.

### Cloud rain asm

Exact installed IsRainingAtTransformer targets Level.isRainingAt(BlockPos)Z, every IRETURN, inserting original bool+local0 Level+local1 position into BlockHooks.isRainingAt. Registered TFCoreMod/service is reused. Original true remains true. Otherwise distance>0 and hasChunkAt are required; scan current query Y inclusive to <Y+distance in its loaded chunk. First CloudBlock with current precipitation RAIN returns true BEFORE its opacity check. Any earlier MOTION_BLOCKING opaque state returns false. Thus rainy clouds can supply local rain without sky/global rain/biome eligibility; fluffy still requires its biome/weather condition. Snowy and wispy do not provide RAIN, and opaque non-rain clouds may block higher clouds. No stored wetness status or owner is assigned.

### Cloud wet damage

Native Entity.isInRain tests isRainingAt at block position OR bounding-box maxY at same integer X/Z. Native isInWaterOrRain and isInWaterRainOrBubble share that result. Living.aiStep server + isSensitiveToWater + wet calls hurt(drown,1) each qualifying callback; return discarded, with native hurt cooldown/defenses still limiting accepted damage. Exact Blaze, EnderMan, Strider and SnowGolem return true; ordinary Living false. EnderMan ownerless nonprojectile hurt first calls super, then server nextInt(10)!=0 attempts native teleport regardless of super hurt result; invulnerability rejection precedes that. Native destination solidity/no-water, alive/server, teleport hook, collision and return conditions remain.

### Cloud wet preservation

Alive Living.baseTick wetness calls extinguishFire; native Entity.move and AbstractArrow.tick retain their own wet fire cleanup. Mob.isSunBurnTick treats wetness as a rejection alongside its daylight/brightness/sky/random gates. Axolotl !noAI baseTick handles air: wet resets maxAir 6000; dry alive decreases, at -20 resets0 and requests dry_out2. Dolphin !noAI wet resets moisture2400; dry decrements, <=0 requests dry_out1 and ground dry branch can flop. These are prevention of native dryness/fire consequences, not healing or cloud-emitted dry_out. Native Wolf wet/shake visuals are not a new combat effect.

### Cloud riptide

Native TridentItem use rejects too-damaged stack or positive spin strength while !isInWaterOrRain. Release requires Player, charge>=10, wet if strength>0 and usable durability; retains native server cost1. Positive native enchantment spin strength pushes normalized view vector*strength, startAutoSpinAttack(20,8,stack), and if grounded moves up1.1999999. Cloud changes the wet prerequisite only; native enchantments, attack/equipment callbacks and movement/collision remain. Zero-strength thrown-trident branch is not a cloud-created attack or alternate damage source.

### Cloud conduit

Native Conduit server gameTime%40: active requires every block in centered3x3x3 isWaterAt plus >=16 valid frame blocks (exact loader isConduitFrame). Rain does not satisfy that actual water requirement. Active effect radius integer frameCount/7*16, expanded query plus strict native block-position distance; qualifying Player wet -> CONDUIT_POWER260/amp0 ambient/visible through native addEffect. Attack needs >=42 frames. Fresh selection chooses random Enemy+wet within AABB(blockpos).inflate8; existing target instead checks alive and strict block-distance8, without rechecking wet/Enemy. Saved UUID reacquisition uses unique matching UUID in that box. If non-null, native sound then hurt(magic,4), return ignored. Cloud can admit fresh wet targets/players but does not own the source, replace native mitigation, bypass structure or guarantee continued rain eligibility.

### Cloud weather limits

FarmBlock.randomTick uses isRainingAt(above) independently of global rain: permits moisture7, not damage. FireBlock main rain extinguish/spread branches still require global isRaining (and doFireTick etc); local query cannot alone enable all of them. Actual neighbor checkBurnOut after flammability/onCaughtFire uses !isRainingAt directly when choosing fire placement versus removal, so local cloud rain can affect that branch without global rain. Natural lightning in ServerLevel.tickChunk first requires global rain AND thunder AND nextInt(100000)==0; the cloud hook changes only later isRainingAt. No cloud-only thunder/Channeling claim. Native fishing rain timing is noncombat (25% extra decrement, independent sky penalty); Leaves animation rain drips are presentation.

### Snow support exclusion

Exact KeepGrassSnowyForSnowloggableBlocksTransformer targets every IRETURN of static SnowyDirtBlock.isSnowySetting, passes original bool and local0 state. Hook preserves true or accepts SnowLoggable with SNOW_LAYERS>0. Native placement/up-neighbor consumer sets SNOWY appearance property; no damage, resistance or extra snow layers in this hook. Existing SnowLoggable plant snow behavior remains the protected contact-hazards review, not duplicated here.

### Mushroom support exclusion

Exact ModifySoilDecisionForMushroomBlockSurvivabilityTransformer inserts after each BlockState.canSustainPlant invocation in native MushroomBlock.canSurvive, passing result+level local2+position local3. Hook preserves non-DEFAULT TriState; DEFAULT becomes TRUE if any of 8 adjacent X/Z positions at Y-1 is actual TF portal (either state). It excludes center. Exact loader still admits MUSHROOM_GROW_BLOCK directly, otherwise non-default decision controls survival, else native brightness<13 and soil test. Thus portal vicinity can satisfy survival despite ordinary light/soil failure, but no healing/damage/portal transport is performed. Explicit support exclusion, not an unresolved combat mechanic.

### Compatibility

DIRECT_SOURCE_SPECIFIC: native tower/cloud/portal tags and three actual registered TF transformers; optional gravestone block tag is explicit integration. GENERIC_CONDITIONAL_PRESENT: native fall/incoming/teleport hooks, native rain-query and precipitation consumers, extensible conduit frame and block tags. NONE_PROVEN: inspected control logic has no direct Tensura/L2/Curios mapping. UNKNOWN: runtime transformer application, third-party hooks/tag changes/world gamerules and pack-wide outcomes. Static trace is not compatibility certification.

## Packages

| Mechanic | Primary classification |
|---|---|
| Carminite Builder construction/removal control | CUSTOM_CONTROL |
| Antibuilder snapshot and terrain substitution | CUSTOM_CONTROL |
| Cloud native fall request reduction | VANILLA_LIKE_EXTENDED |
| Cloud snow and native precipitation callbacks | CUSTOM_CONTROL |
| Cloud local rain eligibility and native consumers | VANILLA_LIKE_EXTENDED |

## Custom source callers

| Type | Amount | Source identity |
|---|---|---|

## Scope and exclusions

- Exact KeepGrassSnowyForSnowloggableBlocksTransformer targets every IRETURN of static SnowyDirtBlock.isSnowySetting, passes original bool and local0 state. Hook preserves true or accepts SnowLoggable with SNOW_LAYERS>0. Native placement/up-neighbor consumer sets SNOWY appearance property; no damage, resistance or extra snow layers in this hook. Existing SnowLoggable plant snow behavior remains the protected contact-hazards review, not duplicated here.
- Exact ModifySoilDecisionForMushroomBlockSurvivabilityTransformer inserts after each BlockState.canSustainPlant invocation in native MushroomBlock.canSurvive, passing result+level local2+position local3. Hook preserves non-DEFAULT TriState; DEFAULT becomes TRUE if any of 8 adjacent X/Z positions at Y-1 is actual TF portal (either state). It excludes center. Exact loader still admits MUSHROOM_GROW_BLOCK directly, otherwise non-default decision controls survival, else native brightness<13 and soil test. Thus portal vicinity can satisfy survival despite ordinary light/soil failure, but no healing/damage/portal transport is performed. Explicit support exclusion, not an unresolved combat mechanic.
- Client CloudEvents, cloud movement/jump/landing particles, Wolf wet/shake and Leaves rain drips are presentation; no new combat package.
- Farmland hydration and fishing rain timing are traced native consumers, not new damage. Conduit and Riptide retain ordinary native prerequisites.
- All 40 Twilight custom DamageTypes remain USED; listed vanilla factories are separate downstream sources, with dry_out prevented through hydration.
- Wrought Iron Fence/leash/pathfinder, remaining callbacks/ASM and global source closure are unfinished ordinary work, not REVIEW_REQUIRED.

## Future native controls

- Actual Dark Tower/placed Builder redstone cycle, player/pitch, 17-branch limit, blocked/idle removal, power cycle and reload controls.
- Actual Antibuilder snapshot/range, block-type versus inventory/state, ignored tags, probabilistic substitute, native drops and reload controls.
- Native falls on all four clouds with attributes, fall-event veto, passengers, source/mitigation and hurt-false controls.
- Native cloud precipitation with loaded/opaque column, config, biome/weather, snow light/support/rule and real cauldron callbacks.
- Exact cloud rain transformer with native sensitive/fire/hydration/Riptide/Conduit/weather consumers; no runtime outcome asserted.

[Semantic packages and paths](semantic-sections/twilightforest-control-blocks.json), [integrity](twilightforest-control-blocks-integrity.json), [full validation](r2f8ac-control-blocks-validation.json).

Exact next task: Continue Wrought Iron Fence/native leash and pathfinding control, then remaining event callbacks/nested ASM, compatibility attribution and global source exclusions. All 40 custom types already USED. Protect R2f8 whole remaining-content closure and final Twilight dedup/promotion before IceAndFire; static only.
