# r2f8t - TWILIGHT_MAPS_INFORMATION_SEMANTIC_REVIEW_COMPLETE

Installed TF4.8.3345, raw Minecraft1.21.1 and exact NeoForge21.1.244 bytecode. Maps and OreMeter provide information; no HP/status/damage delivery or boss progression mutation. Prior goggles callbacks are reused. Two more registered nested ASM transformers reviewed, including an explicit correction to R2f8q. Static research only, no runtime/L2/Stage/production/Phase6/7 changes. Twilight remains PARTIAL;31/40 custom types reviewed,9 ordinary unfinished types.

Adds 4 reviewed packages / 28 delivery cases. Twilight remains PARTIAL at 213/701 drafts, zero promoted. REVIEW_REQUIRED 0.

## Native contracts

### Authority

Installed TF4.8.3345, raw Minecraft1.21.1 and exact NeoForge21.1.244 bytecode. Maps and OreMeter provide information; no HP/status/damage delivery or boss progression mutation. Prior goggles callbacks are reused. Two more registered nested ASM transformers reviewed, including an explicit correction to R2f8q. Static research only, no runtime/L2/Stage/production/Phase6/7 changes. Twilight remains PARTIAL;31/40 custom types reviewed,9 ordinary unfinished types.

### Registration

TFItems registers filled_magic_map as MagicMapItem; filled_maze_map/filled_ore_map as MazeMapItem(false/true), matching empty variants, and ore_meter stack1/uncommon without durability. Native recipes use8 c:paper plus matching focus; magic focus is raven feather+torchberries+glowstone dust; ore_map is EMPTY maze_map plus diamond/gold/iron storage blocks. This does not convert an already filled Maze map or preserve its ID. Actual registered OreMeter is a legitimate future item fixture; no survival crafting recipe is inferred from its name. All matching installed resources pinned.

### Empty magic

EmptyMagicMapItem.use clientPASS; server requires dimension TYPE holder tag twilightforest:allows_magic_map_charting, installed value twilightforest:twilight_forest_type. Rejection displays message/FAIL, no consumption/map. Success consumes1 through native ItemStack.consume (infinite-materials exemption), awards stat/sound, creates filled map at floor playerXZ, scale4/trackingtrue/unlimitedfalse. Replaces exhausted held stack; otherwise inventory add copy then drop if insertion fails. No damage, status or use cooldown.

### Magic identity

MagicMapItem.createMapData allocates native free MapId but stores under magicmap_<id>. Center per axis round((coord-1024)/2048)*2048+1024, independent of supplied scale. getCustomMapData missing-data fallback SERVER ONLY uses shared spawn, scale3/trackingfalse, newID; this fallback does not recheck empty-map dimension-type tag. TFMagicMapData server storage is server.overworld().dataStorage, with dimension saved in each map; client separate static name->map cache. Native colors/banner/frame data retained on save/load; custom showOnItemFrame decorations persisted with IDs/counts, conquered string list persisted. No source attacker/recipient ownership.

### Magic update

Exact244 MapItem.getSavedData(ItemStack,Level) dispatches virtual getCustomMapData for MapItem subclasses. Native server inventoryTick performs Player.tickCarriedBy, then if unlocked and selected OR actual offhand stack identity, virtual update. Magic update additionally same dimension ResourceKey identity +Player+server. Samples128x128 output, hard-coded16 blocks/pixel and32 pixel radius (512blocks), even fallback scale3; four biome samples per pixel grid,512x512 cached biome samples atY0 spaced4blocks. Floor then Java integer division affects negative viewer offsets. Ring fuzz outside radius30, only radius<32 and odd parity in fuzzy ring. Stream neighbor preference, actual MAGIC_MAP_BIOME_COLOR datamap; absent map uses MAGENTA/brightness1. Native status/damage/attributes unaffected.

### Magic cache

Static MagicMapItem.CACHE uses only ChunkPos(startX,startZ) for complete biome sample array; dimension/world/seed are not part of cache key. Installed TF instruction scan proves only this class accesses this private field and no clear/removal call in its class. Reusing coordinate key can reuse earlier level biome holders during this JVM lifetime. This is a source-level information-cache property, not runtime-tested world contamination or pack-wide reflection exclusion.

### Magic icons

Within charted pixels, only a Legacy landmark center, a structure holder in LANDMARK tag, LandmarkStructure instance and present icon produce TF decoration. Icon rotation180; LandmarkUtil.isConquered reads actual matching TFStructureStart flag, does not mark it conquered. TFMagicMapData.addTFDecoration first native addDecoration, then uses existing decoration byte x/y and asset ID to make conquered marker ID, adds/removes string accordingly. List mutation alone does not call setDirty/setDecorationsDirty; pixel/decor updates use native dirty paths. A map icon is not proof of a live spawned boss, boss death, shield break or protection removal.

### Map packets

TFMagic/MazeData.getUpdatePacket wraps only a nonnull native ClientboundMapItemDataPacket; otherwise passes native result through. Registered playToClient handlers additionally require clientbound flow. Missing client data is created center0, current client dimension, packet scale/locked; native patch then applied. Magic clears/replaces conquered list, Maze sets ore/yCenter; native MapRenderer.update follows. These packets carry information to clients and do not mutate server boss state. Conquered renderer draws red X for matching map marker and returnsfalse so normal icon can render; Magic Player icon custom4scale returns true. Frame/banner/native rendering remains native, with actual NeoForge virtual map lookup; protected Goggles real inventory callback can deliver update/packet without holding map in hand.

### Empty maze

EmptyMazeMapItem.use creates scale0/trackingtrue/unlimitedfalse at floor playerXYZ with constructor ore flag BEFORE consuming1; unlike EmptyMagic no explicit side or dimension-charting tag guard. Native use, inventory/drop and consume semantics remain. Maze create allocates new mapID and mazemap_<id>, native128*(1<<scale) center rounding; TFMazeMapData.calculateMapCenter sets yCenter=creationY and, only ServerLevel with Legacy selected LABYRINTH, snapsXZ to nearest legacy center. Otherwise keeps native rounded center. Missing-data server fallback uses sharedspawnXYZ scale0/trackingfalse and item ore flag, no empty-map recreation requirement.

### Maze pixels

Maze update requires same dimension ResourceKey and Player; server gate comes from native TF inventoryTick. Pixel size1<<scale, view radius16pixels (8 with ceiling), native HoldingPlayer.step increment, columns step-mod16 or prior-change continuation, radius/parity fuzz. Ceiling uses deterministic pseudorandom DIRT/STONE colors, not underground block contents. Nonceiling reads original state at chunk-localXZ/yCenter and immediately adds its map color. If original is STONE OR air, probesY-3..Y+3 for STONE AND notair, assigns first such state and brightness0below/2above/1same. It does NOT search for the first nonstone; original color multiset is not replaced by searched state. Ore branch uses resulting state, datamap ORE_MAP_ORE_COLOR weight1000 else nonair c:ores PINK weight1000. Actual9 installed color keys cover8 native ore tags plus ancient_debris; dynamically mapped/tagged ores remain conditional.

### Maze y

TF Maze server inventoryTick calls tickCarriedBy first. floor(playerY-yCenter) outside[-3,3] replaces existing own-name decoration with PLAYER_OFF_MAP retaining coordinates/rotation. This vertical test changes marker only: it does not veto subsequent unlocked selected/offhand pixelupdate. yCenter and ore flag persist with native saved map fields; server storageoverworld/clientstatic cache separate from Magic. Same mapId among copies shares saved data. No target damage, mining, teleport or forced block loading is introduced by this review; real update reads native chunks as coded.

### Cloning

Native Magic/Maze custom crafting recipes require exactlyone filled matching map slot plus>=1 empty matching map slots and no other nonempty ingredients; canCraftInDimensions requires>=3x3. Output is filled.copy() with count(empty SLOTS+1), so components/mapID preserved and all copies share underlying saved data. Filled Ore and empty Ore are not accepted by MazeMapCloningRecipe. Native recipe consumption remains; no invented copy of Ore map or special quantity-per-stacked-input.

### Cartography

Exact244 archive has no replacement for native CartographyTableMenu/its five anonymous classes; raw bytecode slot0 mayPlace requires Items.FILLED_MAP, additional slot PAPER/MAP/GLASS_PANE, quickMove sameFILLED_MAP identity. Genuine UI therefore rejects TF filled item identities; no baseline cartography scale/lock/copy route is proven. TF empty onCraftedBy overrides do not override native onCraftedPostProcess (MAP_POST_PROCESSING handles scale/lock). Do not infer disabled scaling from wrong method or force TF stacks through rejected native slots. Other mods changing admission are conditional external behavior.

### Locator asm

Registered ResolveNearestNonRandomSpreadMapStructureTransformer targets exact ChunkGenerator.findNearestMapStructure(ServerLevel,HolderSet,BlockPos,int,boolean)Pair. Finds LAST ARETURN and inserts originalPair +locals1,2,3,4,5 into MapHooks.resolveNearestNonRandomSpreadMapStructure. Exact244 target has THREE ARETURN instructions: empty placement map early-null and early random-spread result bypass hook; only final return is intercepted. Hook calls WorldUtil.findNearestMapLandmark(...).orElse(original). A found TF pair replaces original without comparing distances to original vanilla result. No unconditional all-return interception or global nearest guarantee.

### Locator search

WorldUtil restricts target holder placements to actual LandmarkGridPlacement, otherwise Optional.empty. Scans Legacy landmark centers using focus chunk &-16, spacing16chunks and supplied radius as GRID radius; skipCenterfalse, iterator hasNext dX+1<=radius means radius0 scansnothing. Placement.isStructureChunk remains: native placement/frequency/exclusion checks; TF ctorfreq1/salt0/zerooffset/noexclusion plus actual center and optional resource-key gridlock==pickVarietyLandmark. Target must be in that placement set and structure biome list contain level.getBiome(centerY0). With skipKnown, START_PRESENT breaks inner target loop. It does not load/validate a generated structure start for every accepted candidate. Chooses smallest center.distToLowCornerSqr(queryX,0,queryZ) among TF candidates. Native search reads info, no spawning/HP/shield/progression modification.

### Locator seed

Legacy center coordinates derive region math and deterministic coordinate seed, sign-dependent+8/+9. Biome-specific landmark selection uses rounded16chunk cells sampled atY0; variety uses overworld worldgen seed+chunkX*25117+chunkZ*151121, hill weights6/3/1,hedge2,Naga2,Lich2, with reserved regional Naga/Lich positions. Gridlock uses variety selection; Magic map landmark pick first uses biome mapping. These are distinct code paths. Full native helper/iterator/placement bodies pinned; blockNearLandmarkCenter shifts by(4+x)/(4+z) per Java precedence rather than adding offsets after shift, and is not the map locator call used here. No new boss attack mechanic inferred from structure choice.

### Locator delivery

Actual ServerLevel.findNearestMapStructure delegates to generator with requested tag holders. Native ExplorationMapFunction requires actual Items.MAP and nonnull loot ORIGIN, then uses configured destination/radius/skipKnown; found result creates ordinary native map with zoom, tracking/unlimitedtrue, biome preview and target marker. VillagerTrades.TreasureMapForEmeralds requires ServerLevel trader and uses destination tag, radius100, skipKnowntrue; found result creates native scale2 map and ordinary offer with emerald cost plus compass, configured maxUses/xp and .2 priceMultiplier. Missing search result yields unchanged loot stack or null trade. Native LocateCommand calls generator directly for actual requested structure holder(s), requires normal command authority. Their results reach TF hook only through final-return path and actual LandmarkGridPlacement target. No installed TF exploration-map loot resource is assumed; direct native path availability is distinct from a configured TF trade/loot producer.

### Meter start

OreMeter.use requires player.getClass()==ServerPlayer.class, not instanceof (real subclasses/FakePlayer fail). isLoading means ORE_LOADING component presence; if present PASS. Otherwise nonsecondary begins server scan with range=getOrDefault1, duration50+25range and ORE_SCANNING only. No ORE_LOADING until first tick, so another valid use before tick can restart. No consumption, durability or cooldown. Secondary air-use only cycles range via positiveModulo(range+1,3) when native Fluid.ANY ray MISS; hit returnsPASS. Separate useOn secondary+actual clicked ORE_METER_TARGETABLE tag sets ORE_FILTER, no loading/server check inside method, no nullPlayer guard. Actual interaction eligibility remains.

### Meter geometry

OreScannerComponent.scanFromCenter uses chunk=(center>>4), origin((chunk-range)<<4,Y0), span=endcoord(chunk+range,15)-origin WITHOUT+1. Normalranges0/1/2 produce15/47/79 blocks per horizontal axis. tickScan uses CURRENT level minBuildHeight as originY, area=xSpan*zSpan, volume=area*CURRENT getMaxBuildHeight (not max-min). march=ceil(float(volume)/abs(duration)), starts at ticksProgressed*march, scans linearX/Z/Y until volume; copies immutable counter and adds one tick. Standard min=-64,max=320 yieldsY-64..255, excluding256..319. This exact formula is recorded, not repaired or assumed to scan full nominal chunks.

### Meter progress

Server inventoryTick any real ticked slot with ORE_SCANNING: tickScan first; if empty removeSCANNINGonly, else unfinished writesLOADINGprogress+SCANNINGnext; finished writesORE_DATA(getResults(CURRENTfilter),centerChunk,volume,CURRENTrange), removesLOADING/SCANNING. No held requirement or persisted dimension: carrying genuine scanning stack across levels can sample current level at storedXZ and combine counters; no runtime assertion. Existing ORE_DATA remains during new scan but loadingHUD takes precedence. No ore removal, damage source, status or direct resource transfer. Scanning continues only with real inventoryTick caller, not hypothetical every container.

### Meter results

Counter includes all scanned Block identities. With assigned filter getResults returns exactly its translated-descriptionID and count (even0); without filter includes count>0 and block holder c:ores. Results use immutable map, saved scannedChunk,totalScannedBlocks, universalId=(counts.hashCode XOR chunk.toLong)*(scannedRange XOR total). ORE_SCANNING codec persists origin/spans/duration/counts/progression; default-on-parse-error is empty scanner. TF registration specifies persistent codec with no explicit network codec, but native DataComponentType.Builder.build derives fromCodecWithRegistries, so not server-only/transient. DATA/LOADING/RANGE/FILTER have explicit persistence/network codecs. Native stack/save/load/sync applies; no timer outside callback.

### Meter clear display

EntityEvents.LeftClickEmpty listener, if genuine heldmeter hasDATA ORFILTER, sends WipeOreMeterPacket and locally removesDATA/FILTER. Registered playToServer handler uses ctx.player actual hand and exactORE_METER before removing those two only. Does not cancel SCANNING, LOADING or RANGE; ongoing scan may refillDATA. HUD real heldmeter (main preferred), activeclient GUIvisible/no debug/no screen; LOADINGdots elseDATA. Nonzero universalId initializes cached table; id0 skipped unless an entry already exists. Displays snapshot counts/percentages/scannedchunk, not live world query. Cache key omits dimension/independent configuration and can collide; read-only info behavior, not proven pack issue.

### Cloth erratum

R2f8q incorrectly treated untransformed NeoForge ElytraLayer.shouldRender as final behavior. Installed TFCoreMod registers CancelElytraRenderingTransformer, targets exact shouldRender(ItemStack,LivingEntity)Z, inserts ALOAD1 plus ArmorHooks.cancelArmorRendering(originalBoolean,stack) before EVERY IRETURN (172). Exact244 method has local1ItemStack and native ELYTRA identity predicate. Component present turns true tofalse; false staysfalse. Cloth therefore hides native Elytra wing rendering, separately from humanoid armor hook, while cape may render through protected cape hook. This changes no attributes, protection, durability or native flight. Historical Q files remain immutable; new accumulated draft explicitly corrects one paragraph in four locations and one future-control label, with source references and counted locations.

### Compatibility

NeoForge virtual custom-map lookup is actual loader behavior; two registered TF ASM hooks are native TF source changes (DIRECT_SOURCE_SPECIFIC to exact native targets). Native inventory/crafting/packet/data-component methods plus real dynamic biome/block data maps and c tags are GENERIC_CONDITIONAL_PRESENT. No direct external mod combat override proven in these scoped source bodies (NONE_PROVEN), no Curios-native map inventory callback invented. Unscanned external modifications remain UNKNOWN; no pack-wide certification or runtime success claim. Other ASM/hazards/passives/source exclusions remain ordinary unfinished scope.

## Packages

| Mechanic | Primary classification |
|---|---|
| Magic Map native biome and landmark information | CUSTOM_CONTROL |
| Maze and Ore Map slice information | CUSTOM_CONTROL |
| Native landmark locator integration | CUSTOM_CONTROL |
| Ore Meter native scanned snapshot | CUSTOM_CONTROL |

## Custom source callers

| Type | Amount | Source identity |
|---|---|---|

## Scope and exclusions

- Information mechanics are separated from HP damage, shields, statuses and boss progression; no new DamageType.
- Full25 TF map/scanner/helper classes reviewed; protected Goggles and cloth mechanics reused, only proven Elytra erratum updates accumulated draft. Historical Q evidence unchanged.
- Registered map locator target has three native returns, only final transformed; legitimate configured native loot/trade/command paths are conditional, not fabricated installed TF producers.
- Other structural utilities, passive entities, hazards/nine custom types, ASM/compatibility/source closure remain unfinished. No runtime or production change.

## Future native controls

- Actual emptyMagicdimensiontype gate, Maze/Ore creationY and orevariant; held/offhand/protectedgoggles native callbacks.
- Map cache/dimension, fixedYsearch, highYmarker, ceilingcolors, savedIDcloning and cartography negativecontrols.
- Native landmark configuredquery: exactfinalreturn, biome/grid/presence/radius0, originalfallback versus TFreplacement.
- OreMeter exactplayer/start/loading/filter, geometry/minmaxY, save/dimensionmovement, clear-duringscan, realHUDsnapshot.
- Native Emperor cloth on Elytra: registered shouldRender hook suppression separately from cape/defense/flight; runtime0.

[Semantic packages and paths](semantic-sections/twilightforest-maps-information.json), [integrity](twilightforest-maps-information-integrity.json), [full validation](r2f8t-maps-information-validation.json).

Exact next task: Review structural utility items/blocks (Rope, Magic Beans, remaining magic cores and associated callbacks), passive entities, environmental hazards and nine remaining custom DamageTypes; close remaining nested ASM, compatibility and source exclusions. Then R2f8 and final Twilight COMPLETE promotion; only afterward IceAndFire. Static only; no runtime/L2/Stage/production/Phase6/7.
