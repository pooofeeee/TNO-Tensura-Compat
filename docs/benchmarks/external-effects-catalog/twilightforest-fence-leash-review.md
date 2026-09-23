# r2f8ad - TWILIGHT_FENCE_LEASH_SEMANTIC_REVIEW_COMPLETE

DIRECT_SOURCE_SPECIFIC: exact TF fence/knot/pathfinder transformers, native attachment producers, and explicit TF contributions to alexscaves:ferromagnetic_blocks / ferromagnetic_items. External AlexsCaves consumer behavior is not established here. GENERIC_CONDITIONAL_PRESENT: native entity/block interaction, placement, leash serialization, spawn cancellation and extensible tags. NONE_PROVEN: inspected fence/leash paths have no direct Tensura/L2/Curios mapping. UNKNOWN: applied runtime transformer order, other pack tag/hook changes and actual fixture outcomes. No pack-wide certification from static absence.

Adds 3 reviewed packages / 24 delivery cases. Twilight remains PARTIAL at 270/996 drafts, zero promoted. REVIEW_REQUIRED 0.

## Native contracts

### Authority

Installed TF4.8.3345, its exact nested ASM, raw Minecraft1.21.1 and installed NeoForge21.1.244 are the authority. Full outer-class attachment census finds TWO native writers; existing source aids omitted relevant references, so source-text absence was not accepted. Exact methods, resources and eight structurally decoded NBT templates are pinned. This is static research, not a runtime claim or production change.

### Fence source

Registered wrought_iron_fence uses WroughtIronFenceBlock and WroughtIronFenceItem; hardness8/resistance20, requires correct tool, noOcclusion. Native recipe uses six #c:ingots/wrought_iron for3; ordinary block loot returns itself subject to survives_explosion. TF explicitly adds it to minecraft:walls. In pinned raw-Minecraft plus TF block tags it is not in minecraft:fences or wooden_fences; other pack data changes remain unknown. Actual worldgen producers below and ordinary placed block items supply legitimate sources.

### Fence geometry

POST!=NONE adds central x/z7..9/16 post of height1. CAPPED also adds neck y16..17/16 and head y17..20/16 (maximum1.25). Each non-NONE directional side adds its fixed width2/16 height1 arm; MIDDLE/BOTTOM/TOP/FULL share that collision shape. With no post and no arms, empty union falls back to a full cube. Inherited BlockBehaviour collision uses getShape when hasCollision; noOcclusion does not disable collision. isPathfindable returns false for all computation types. There is no hurt/HP/status operation in the fence.

### Fence connections

Connects to WALLS, or non-exception solid face, or IronBarsBlock. makeFenceState checks same-fence block above/below and that layer adjacent self/connectable state: both =>MIDDLE, below only=>TOP, above only=>BOTTOM, neither=>FULL. makePost preserves existing cap only with allowCap and replaceable above, otherwise vertical-column post requirement then own connection requirement. Own post is required for isolation, asymmetric opposite connections, or north/east presence (including cross/corner); a straight opposite pair may have NONE. Upward column search accepts qualifying connections or CAPPED; downward search accepts qualifying connections, without a separate CAPPED test. Rotation/mirror remap direction properties normally.

### Fence placement

Literal getStateForPlacement reads connections at clicked position but passes pos.above() to fenceShape; subsequent neighbor updates pass actual position. This offset is recorded without repair. WATERLOGGED is true only for actual WATER fluid on placement; returns native source water and schedules water tick on shape updates. Skylight propagates only when not waterlogged. These are terrain/fluid controls, not a new damage source.

### Fence cap

WroughtIronFenceItem secondary-use branch requires clicked exact item block and block above not that same fence. If capped OR above replaceable, write POST = makePost(...,allowCap=false) for capped, otherwise CAPPED. Write result ignored. Sound and SUCCESS occur even when a nonreplaceable above-block prevented the write. This branch has no stack decrement, durability cost or internal server-only guard. Other cases delegate BlockItem.useOn; native outer interaction/permission hooks remain. Cap can change collision and native knot support, not HP.

### Lead event

Actual registered EntityEvents RightClickBlock callback requires held exact Items.LEAD, actual TF fence, POST!=NONE and server. It calls LeadItem.bindPlayerMobs, then cancels event and sets SUCCESS regardless of helper PASS/SUCCESS. It has no additional item cost. Thus empty nearby lead list still produces this event result. Earlier native interaction cancellation/permission remains possible; this callback does not fabricate a new leash or override target eligibility.

### Lead eligibility

Native Entity.interact first requires alive and Leashable. Already held by this player => server dropLeash(true,!hasInfiniteMaterials), game event and sided success. Otherwise held LEAD and canHaveALeashAttachedToIt (canBeLeashed AND !isLeashed) => server setLeashedTo(player,true), then shrink1 on both sides. Exact Player.interactOn rejects spectators and honors CommonHooks.onInteractEntity; consuming result refunds creative instabuild count only when same held stack and count decreased. Mob.canBeLeashed excludes Enemy, so ordinary player-new-lead interaction does not admit zombies. Genuine worldgen setLeashedTo below is a separate native producer. Native setLeashedTo also stops riding if passenger; it does not tame or transfer attack ownership.

### Lead binding

LeadItem.leashableInArea uses AABB from pos-7 to pos+7, not a radial sphere or +1 block box. bindPlayerMobs selects any Leashable whose current holder is this player. First match creates/reuses a knot in a +/-1 search box with exact stored BlockPos; new addFreshEntity return ignored. Plays knot placement sound, then setLeashedTo(knot,true) for each. Nonempty list emits BLOCK_ATTACH and SUCCESS; empty list PASS. No second canBeLeashed test and no extra lead consumption; it transfers already legitimate player-held leads.

### Knot survival

Exact registered LeashFenceKnotSurvivesTransformer targets FIRST IRETURN of native survives (raw method has one return). Hook preserves original true, otherwise accepts actual TF fence with POST!=NONE. Original native test is BlockTags.FENCES. Native BlockAttachedEntity server tick checks checkInterval++==100, hence101 calls between checks; if not removed and !survives, discard and dropItem (knot sound). A supported knot becomes invalid after post disappears, subject to this periodic check. This is not immediate universal wall support.

### Knot interaction

Native knot interact is client SUCCESS; server queries nearby leads held by player OR this knot, transferring player-held ones first. If none transferred, discard knot; creative explicitly dropLeash(true,false) for attached leads. Noncreative relies on subsequent native leash tick seeing dead holder and dropping lead item. Returns CONSUME. BlockAttached hurt rejects isInvulnerableTo, otherwise server !removed kills/marks hurt/drops and returns true independently of amount. Player skipAttackInteraction checks level.mayInteract then hurt(playerAttack,0). Nonzero move/push similarly kills. thunderHit is empty. Knot is nonliving, so these are removal/hurt-return rules, not HP damage.

### Leash motion

Entity.baseTick on server invokes Leashable.tickLeash. Restore delayed leash first; dead leasheed entity or holder drops leash(true,true). Same-level holder invokes handleLeashAtDistance: Pathfinder restrictTo(holder block,5), true. Distance>10 => drop leash and Mob disables MOVE; >6 => elastic additive velocity per axis copySign((delta/distance)^2*.4,delta/distance), then checkSlowFallDistance; <=6 => closeRange. Pathfinder closeRange follows only if shouldStayCloseToLeashHolder AND !isPanicking, enabling MOVE and navigating at speed1 toward holder with2-unit stop distance. Ordinary autonomous goals and combat remain; no full immobilization.

### Leash override

Exact registered PathFinderUnrestrainedByLeashTransformer targets EVERY IRETURN of BASE PathfinderMob.shouldStayCloseToLeashHolder; hook returns prior && !hasData(LEASH_PATHFINDER_OVERRIDE). Only close-range follow decision changes. Elastic pull, leash break, holder-range restriction, damage immunity and hostile goals are not changed. This is not blanket instrumentation of subclass overrides. Actual Unit attachment leashed_pathfinder_override is serialized, without sync/copyOnDeath declared. Registered EntityJoinLevel handler removes it from Pathfinder only if !mayBeLeashed, which means getLeashData()==null, NOT canBeLeashed or !Enemy. Saved unresolved leash data can retain it. No tick-time cleanup; breaking a leash can leave attachment until later join.

### Wing route

Registered LichTowerStructure starts LichTowerFoyer/jigsaws. Native WingBridge tryRoomAndBridge/tryGenerateRoom/tryPlaceRoom route through LichTowerUtil.rollRandomRoom: size1 ->5x5 pool, size3 ->9x9. StructureTemplateDefinitions reload/apply and weighted random choose genuine installed templates. Five-by-five zombie_trap has one DATA marker zombie_trap; nine-by-nine holding and lockup each have four DATA zombie_trap|wrought_iron_post markers, each1/2 random choice at processing. Each corresponding installed pool entry has weight100. Selection still requires native jigsaw, terrain and collision admission; no guaranteed generation frequency inferred.

### Wing marker

TwilightTemplateStructurePiece customPostProcess sets chunk bounding box and requires template.placeInWorld true before filtering STRUCTURE_BLOCK DATA markers. Native StructureTemplate.filterBlocks transforms/offsets positions, respects bounding box, rotates state and preserves NBT. Wing handleDataMarker processes optional > prefix / @ orientation / random | alternatives / : parameters, removes marker without drops and dispatches handleDataParams zombie_trap. putZombieTrap writes TF fence flag2 POST=CAPPED if above AIR, otherwise POST, marks postprocessing; failed write is not success-gated. Shuffles horizontal directions excluding outward chunk edges at x/z0 or15, chooses one or UP sentinel; only non-Y direction creates entities.

### Zombie creation

Both real producers call EntityUtil.createEntityIgnoreException(world,type), which uses type.create(world.getLevel()) and catches Exception to null. Only if knot AND Zombie nonnull: move knot to anchor x+.5,y,z+.5; zombie.setPersistenceRequired; zombie.setLeashedTo(knot,false); move zombie to adjacent x+.5,y-1,z+.5; set Unit override; world.addFreshEntity(zombie), ignoring return. They do not add the temporary knot, call finalizeSpawn, tame, disable AI, heal or damage. Zombie attacks retain their native source/eligibility; leash holder is not attack owner. Native setPos stores containing BlockPos, knot recalculation centers x/z+.5,y+.375.

### Perimeter route

LichTowerStructure.generateFromStartingPiece invokes LichYardBox.beginYard and native perimeter generation (outer_fence3..7). Perimeter constructor randomFloat>0.25 leaves no anchor; otherwise filter actual fence states and remove POST!=POST (CAPPED and NONE excluded), shuffle candidates and save first selected leash_pos. Actual outer_fence3/4/6 templates contain only NONE, whereas5/7 include eligible POST plus excluded CAPPED. postProcess invokes generateBoundZombie after parent; both stored anchor and adjacent zombie position must lie in current chunkBounds, direction is sourceJigsaw.orientation.top. It uses the same creation sequence. leash_pos is serialized; no generated-once flag is written or cleared in this method, so arbitrary rerun idempotence is not asserted.

### Generation persistence

Exact NeoForge244 WorldGenRegion.addFreshEntity rejects spawn-canceled Mob, otherwise delegates current chunk.addEntity and returns true. ProtoChunk.addEntity on nonpassenger saves Entity to a new compound then stores it, ignoring save boolean. Native Mob save writes leash data: Knot holder becomes native leash BlockPos int array; other holder becomes UUID compound. Entity save persists serialized attachment. Load restores delayed LeashData and attachment. Subsequent server leash restore for saved position calls getOrCreateKnot in actual ServerLevel and setLeashedTo(...,true). Thus normal ProtoChunk serialization legitimately creates the real knot later; missing direct TF temporary-knot add is NOT a proven defect. No claim all alternative immediate-add WorldGenLevel implementations behave identically.

### Leash persistence

Native LEASH_KNOT EntityType is noSave, .375x.5, tracking10/updateInterval INT_MAX. Relationship persists on leasheed mob, not standalone knot save. Saved BlockPos restore creates/reuses real knot (add return ignored); unresolved UUID restore waits and at tickCount>100 drops a lead and clears data. LeashData.setLeashHolder clears delayed UUID/position/id. EntityJoin may retain pending saved leash by mayBeLeashed. Runtime save/reload, canceled spawn and failed-add outcomes remain fixture controls, not observed results.

### Compatibility

DIRECT_SOURCE_SPECIFIC: exact TF fence/knot/pathfinder transformers, native attachment producers, and explicit TF contributions to alexscaves:ferromagnetic_blocks / ferromagnetic_items. External AlexsCaves consumer behavior is not established here. GENERIC_CONDITIONAL_PRESENT: native entity/block interaction, placement, leash serialization, spawn cancellation and extensible tags. NONE_PROVEN: inspected fence/leash paths have no direct Tensura/L2/Curios mapping. UNKNOWN: applied runtime transformer order, other pack tag/hook changes and actual fixture outcomes. No pack-wide certification from static absence.

### Exclusions

Fence tooltip, sounds and property visual variants are presentation; recipe/loot/tag source attribution is retained without separate damage packages. Native knot removal is not living HP damage. Leash/knot/attachment introduce no custom DamageType or HP/SHP subtraction. Only identified Lich worldgen producer/caller methods are closed here; other room spawners, traps, loot/control paths remain ordinary unfinished work for global source review.

## Packages

| Mechanic | Primary classification |
|---|---|
| Wrought Iron Fence geometry and cap control | CUSTOM_CONTROL |
| Wrought Iron Fence native lead and knot support | VANILLA_LIKE_EXTENDED |
| Native bound-zombie close-follow override | CUSTOM_CONTROL |

## Custom source callers

| Type | Amount | Source identity |
|---|---|---|

## Scope and exclusions

- Fence tooltip, sounds and property visual variants are presentation; recipe/loot/tag source attribution is retained without separate damage packages. Native knot removal is not living HP damage. Leash/knot/attachment introduce no custom DamageType or HP/SHP subtraction. Only identified Lich worldgen producer/caller methods are closed here; other room spawners, traps, loot/control paths remain ordinary unfinished work for global source review.
- Other EntityEvents, remaining nested ASM and broader worldgen/exclusion closure are unfinished ordinary review, not REVIEW_REQUIRED.
- No runtime, L2, Stage, production, Phase6/7 or balance work. All40 custom DamageTypes remain USED.

## Future native controls

- Real fence placement/neighbor/cap/water state and collision, including literal placement offset and no-write SUCCESS.
- Legitimate native player lead acquisition, fence binding, knot survival/removal, creative costs and native distance control.
- Actual registered Lich room/perimeter templates, native chunk admission, spawn cancellation and ProtoChunk save/load knot restoration.
- Exact attachment close-follow ASM, EntityJoin pending-leash cleanup, elastic/break/hostile-goal preservation and source ownership controls.

[Semantic packages and paths](semantic-sections/twilightforest-fence-leash.json), [integrity](twilightforest-fence-leash-integrity.json), [full validation](r2f8ad-fence-leash-validation.json).

Exact next task: Continue remaining EntityEvents callbacks (including multiplayer health adjustment), other native Lich worldgen trap/spawner paths and still-unreviewed nested ASM; finish compatibility attribution and global source exclusions. All40 custom types USED. Protect R2f8 remaining-content closure, then deduplicate/promote Twilight COMPLETE before IceAndFire. Static only.
