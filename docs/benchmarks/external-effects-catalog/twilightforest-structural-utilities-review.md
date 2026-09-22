# r2f8u - TWILIGHT_STRUCTURAL_UTILITIES_SEMANTIC_REVIEW_COMPLETE

Installed TF4.8.3345/raw Minecraft1.21.1/exact NeoForge21.1.244. Rope, Magic Beans/grower, Uberous Soil growth and remaining Time/Transformation/Sorting cores. Protected MiningCore/OreMagnet unchanged. No new DamageType:31/40 reviewed,9 unfinished. Static only; runtime0, no L2/Stage/production/Phase6/7.

Adds 6 reviewed packages / 28 delivery cases. Twilight remains PARTIAL at 219/729 drafts, zero promoted. REVIEW_REQUIRED 0.

## Native contracts

### Authority

Installed TF4.8.3345/raw Minecraft1.21.1/exact NeoForge21.1.244. Rope, Magic Beans/grower, Uberous Soil growth and remaining Time/Transformation/Sorting cores. Protected MiningCore/OreMagnet unchanged. No new DamageType:31/40 reviewed,9 unfinished. Static only; runtime0, no L2/Stage/production/Phase6/7.

### Use admission

Genuine ServerPlayerGameMode useItemOn retains RightClickBlock cancellation, spectator, item-before-block/block callbacks, useItem admission/cooldown. ItemStack.useOn posts ITEM_AFTER_BLOCK; server CommonHooks.onPlaceItemIntoWorld checks adventure CAN_PLACE_ON, snapshots stack/components and captures nonbucket block changes. Consuming result posts single/multiblock-place event; cancellation restores block snapshots and prior stack/components, not all earlier custom sounds/stats. Admitted path restores new stack/components and notifications. Creative GameMode separately restores original count after useOn. Item-body shrink alone does not prove final creative cost; direct helper calls are not substitute fixtures.

### Rope item

Rope is native RopeItem/BlockItem;3 Root Strand vertical recipe outputs8. Nonrope context uses normal placement. Existingrope getForward tests clickedface connectable neighbor then opposite; else first3 nearest-look directions, reversed for secondary. Y selectsDOWN; matching X/Z inspects neighboring replaceable/Rope and opposite. UP result becomesDOWN. updatePlacementContext checks candidates while horizontal counter<7, advancing only when axis already present; nonrope replaceable or missing-axis rope returns relocated context. Horizontal checks offsets0..6; vertical counter never increments. Server world-bound check remains. No7-block vertical cap or projectile/levitation.

### Rope placement

Existingrope getPlacementState missing clickedface axis returns state with axis true directly, without super.canPlace; it does not repeat native survival/unobstructed check. Initial/newstate super branch does both. Actual native placeBlock flags11 return gates success/consume1, with creative rules. Rope canBeReplaced only by own item. DefaultYtrue,X/Zfalse; placement onlyclicked axis and actual WATER waterlogging. Native outer interaction/events remain.

### Rope support

canConnectTo rejectsDOWN, otherwise LeavesBlock OR RopeBlock with matching axis OR center-face sturdiness at oppositeface. canSurvive needsANY enabled axis with immediate support (X west/east,Yup,Znorth/south); neighbor-sturdiness helper is passed originalpos here. Place/neighbor schedules1tick. checkConnection walks consecutive identical rope, checks each neighbor, no horizontal7 cap. Tick removes unsupportedaxes; ifnone survive destroyBlock(true), actual loot count equals true-axiscount before explosion decay. Otherwise update survivingstate and drop default one-axis rope once perremovedaxis. Waterlogged update scheduleswater; state persists natively.

### Rope motion

Actual minecraft:climbable tag includesrope; NeoForge default isLadder checks it. Living.onClimbable rejects spectators and calls CommonHooks.isLivingOnLadder (native config in-block/fullboundingbox). No Y-axis requirement. Admitted native movement resets fallDistance, clampsXZ +/-float.15, descent>=-float.15; horizontalcollision orjumping whileclimbable givesY.2. Rope.isScaffolding always true, so Player suppress-sliding branch (!isScaffolding) doesnot zero negativeY atrope feet. X/Z thinbar collision only contextabove&&!descending; Y hasno collision. Outline shows activebars, pathfindablefalse. No flight/invulnerability/damage.

### Beans activation

MagicBeans useOn requires clickedY<max(clickedY+100,175), exactUBEROUS_SOIL and aboveair. Server body shrink1, setBlockAndUpdate above BEANSTALK_GROWER, sound and ServerPlayer stat; mutationbool ignored. Native creative outer count restoration still applies. Wrongsoil/occupiedabove PASS. Grower noCollision/noLoot/strength-1 with typedBE ticker bothsides; client particles, server terrain. HugeStalk is ordinary solid RotatedPillar, no automatic ladder byname.

### Beans advancement

Manual award requires holder!=null AND !manager.getAllAdvancements().contains(holder); native get/values use same map, so ordinary presentholder makes branchfalse. Genuine consuming GameMode.useItemOn still triggers ITEM_USED_ON_BLOCK with pre-use stackcopy. Installed beanstalk advancement requires inventorybeans AND magic_beans used on uberous_soil. Not impossible from manualguard alone. Item stat plus admitted CommonHooks stat can both fire; later placement cancellation doesnot erase earlier stat/sound.

### Beans clock

Ticker increments perreal callback; ticker1 chooses nextLeafY=baseY+10+randInt10,yOffset=randInt100,cScale/rScale=.125+randFloat*.25,maxY=max(GROWERbaseY+100,175). Server growth ticker>100 and even, first102; layerY=baseY+layer. Clear and belowmax growsone layer; otherwise replacebaseHugeStalk/removeBE. Growerbase=soilY+1, distinct from preliminary itemheight. Genuine TimeCore extra typedticker calls canadvance schedule; not globaltime.

### Beans geometry

Helix shifted origin uses sin/cos(baseY+yOffset)*cScale and radius4+sin((baseY+yOffset)*rScale)*3. Layer radius5+sin((layerY+yOffset)*rScale)*2.5, thickness2.5 taper remainingY/5 in last<5. Floor/ceil bounds around shifted origin; squared distance tohelixcenter<thickness^2 attemptsstalk, extraY+1 ifcircle<thickness andY+2 ifcircle<thickness/2. Only mainattempt result updatesclear flag. ResetblocksSkipped afterloop; mayplaceleaves then layer++. No PlayerBreakEvent,mobGriefing,entityoccupancy or damage call; worldmutationbools ignored.

### Beans blocking

Stalk replacesair,native replaceable EXCEPTgrower,leaves or exactFLUFFY_CLOUD. Otherblocks retained; notalreadyHugeStalk and checkBlocked incrementsblocksSkipped, returns<15. Perlayer count;15th stopsmainloop,nexteligiblecallback finalizesbase. AboveY150 successfulplacement clearsWISPY/FLUFFY atUP0..6. Leafcenter setHugeStalk unconditionally; onlyair/leaves receive leaves DISTANCE1..4 flags2. Firstleaf base+10..19; later+5..14 adjusted toalternateYparity. No HP/source/hurt-return request; later solid collision native.

### Beans persistence

Save/load ticker,layer,isAreaClearEnough,nextLeafY,yOffset under beardifierGroundDelta,cScale,rScale,maxY,blocksSkipped. No explicit setChanged in tick; serializable isnot guaranteed everycallback flush. Native chunkdirty/save remains. Rumbling ticker<110 presentation only. Grower listed in c:immovable and c:relocation_not_supported blockentity tags; externalconsumer behavior conditional, no universalban claimed.

### Soil conversion

Soil shape15/16; placement under solid nonbonemealable resolvesDIRT. canSustainPlant rejectsnonvertical, admitscropstag, otherwisefallback. Above-neighborY+1 Bonemealable otherthanthis convertssoil: crops->moisture7FARMLAND,mushroom->MYCELIUM,Bush->GRASS,Moss->thatMossdefault,otherwiseDIRT. Native pushEntitiesUp onshapechange computes newminusoldcollision volume and intersectingentity teleportRelativeY fromcollision result. Plain solidabove nativeFarmBlock.turnToDirt. BelowY-1 Bonemealable convertssoilDIRT andtargetsbelow; callbackdoesnot separatelycheckXZ. No damage/heal/status.

### Soil bonemeal

Ordinary qualifyingconversion queues server TickTask atcurrenttick, actualFakePlayerFactory.getMinecraft. Loop15 freshnative BoneMeal stacks, each exact244 applyBonemeal sameposition; no15-item cost toplayer. Each rereadscurrentblock, postsBonemealEvent; canceled returnsisSuccessful, otherwise actualBonemealable eligibility/successroll/performBonemeal. TF ignoresreturn, noearlybreak afterfailure/replacement. Actualplant/loaderhooks remain; externalpayload conditional.

### Soil mushgloom

AboveMushgloom server specialbranch convertssoil/pushesentities, callsnative growMushroom thenreturns, no15-task. Mushgloom.isValidBonemealTarget false rejectsordinary bone meal; legitimate TFsoil directgrow avoids thattest andnormal40percent successroll. Exact244 growMushroom retainsBlockGrowFeature cancellation/replacement, configuredfeaturepresence, removesoriginal andrestoresif feature.placefalse. DefaultTF BIG_MUSHGLOOM stem2..3,cap1or2,foliageradius1; nativeAbstractHugeMushroom soil/buildheight/air-leafclearance, nonsolidrender stem/cap writes. FeatureLogic onlycapfaceproperties. No explosion/status.

### Soil spread

Soil Bonemealable eligibility: horizontalneighbor sameY/above/below isDIRTtag orFARMLAND, notsoil, withnonsolidabove. performBonemeal Collections.shuffle directions (notpassedworldRNG), skipsvertical, checks same/above/below, spreadsfirstone. isBonemealSuccess true. spreadTo setssoil thenmanualabove callback ifnonair, allowing immediateplantconversion/task. Realbone meal caller governs event/cost. Growth/resource/collision state separate fromHP.

### Core activation

SpecialMagicLog ACTIVEfalse,strength2,WOODsound, light15 onlyactive. onPlace schedules20. Server tick requiresACTIVE&&doesCoreFunction, then sound/effect/reschedule20; inactive/disabled noreschedule. useWithoutItem disabledsetsfalse/message, otherwise toggles,activation schedules20. Pinnedcommon Time/Transformation/Sorting ranges16, disabledifrange<=0. Stateblockstate persistence, nofuel/playerowner. ProtectedMiningCore sharesbase; not reopened.

### Core sources

TimeTreeFeature afternative treeadmission tests origin.above state (notcoreposition) isLOGS orreplaceable, sets coreat(-1,+2,0),Yaxis/defaultACTIVEfalse,schedules20. Transformation/Sorting configs TreeCorePlacer firstlog+Y3/Y2, providerdefaultinactive. Decorator logs.get0/setprovidedstate, noactivation. Installed coreloot dropsmatchingregularlog. Genuinegrowntree use andcreative registereditem are distinct; no intactcoredrop or autoactivation assumed. TransformationLeaves animateTick particlesonly, no biomechange.

### Time core

ActiveTime makes24*tickRate=480 independentsampledpositions per20tick scheduledcallback. WorldUtil uniformeachaxis[-range,+range],default16; repeatspossible, not24ticksperblock. TIME_CORE_EXCLUDED skipsentireposition, installedonlyminecraft:nether_portal. Originalstate isRandomlyTicking ->realrandomTick once. Then lookupcurrentBE but obtainticker fromORIGINALstate withactualBEtype; nonnullticker tickonce. Bothcanoccur; randomtickmaychangestate beforeBElookup. Native dispatch/type/body retained. No scheduledblockqueue/entity/globaltime advancement, syntheticdamage orsourcechange. workedflag onlyparticles. Actualgrower/hazardBE canadvance ifeligible; their ownpayloadgates remain.

### Transformation core

ActiveTrans resolvesENCHANTED_FOREST, upto16 horizontalrandomsamples inconfiguredrange(Y0offset). RejectsdistSqr>256 regardlessrange andalreadytargetbiome atsampleY. Firsteligible: nativechunk,quartXZ, foreachsection sy0,4,8,12; y=clamp(QuartPos.fromBlock(chunk.getMinSection()+sy),minQuart,minQuart+QuartPos.fromBlock(level.getHeight())-1), usesy&3. Actualexpression useschunkminSECTION and repeatspersection, notsectionworldY. Ifnontarget andPalettedContainer,setquartbiome. Unclampedfourvalues coverfourlocalY; nonstandardclamp canrepeat. Markunsaved/resendbiomes/particles/break evenifnomutationultimatelyoccurred. Noexpiry/cost/directHP/effect/forceunlock. Biomedependent hazards retain actualrules; MagicMap staticcache notcleared.

### Sort selection

ActiveSort inclusiveblockcube configuredradius16,skipcorepos,requireBE. Chebyshev<=2 collectsall6non-null BLOCK ItemHandlers intoinputlist; outercellsoutputs. Alive SORTABLE_ENTITIES innewAABB(core).inflate2 likewiseinputlists via6ENTITY_AUTOMATION directions. Installedtag chest_minecart,hopper_minecart,llama,trader_llama,donkey,mule; actualnonnullprovider required. Ifanyinput, entityoutputs alive/tagged withinFIXEDinflate16 (notconfig),excludingentities alreadyinput. No explicitowner/tame/team test; Playernotininstalledtag. Nativeprovideraccess rules remain; no Curios bypass.

### Sort order

InputMap keyList<IItemHandler>,OutputMap keyhandler: equalkeys overwritepositions; sidedduplicates withininputlistremain. Foreachinputgroup/slot simulateextract1; ifnonempty sumoutputstacks withsameITEM regardlesscomponents. Onlycount>0, cannotseedemptydestination. Map<count,handler> retainsone pertie withunspecifiedHashMap iteration; descendingcounts. Targetslot requiresisItemValid, remembersfirstempty butpreferslater sameitem+samecomponents belowmaxstacksize ANDslotlimit. NoLOS/distance/resource cost beyondselection.

### Sort transfer

Chosenoutputslot: ACTUALinput.extractItem(slot,1,false) BEFORE output.insertItem(slot,newStack,true). Nonemptyactualextract andEMPTYsimremainder ->actualinsertfalse; actualremainder IGNORED, transferredtrue andbreakslot/handlerloops forinputgroup. AtmostoneREPORTEDsuccess pergrouppercallback, notoneallgroups. Simrejection afterextract hasNOreinsertion; cantryanotheroutput andextractagain. No rollback ifactualinsertdiffers. Sourcecontracts, notruntimeobservedloss or guaranteedatomic transfer; handlers determineactualresults.

### Sort cache

RegisteredSort Blockobject ownsonefinal directionalcache. Keyrecord ONLYBlockPos+Direction, nolevel/dimension/capability. Firstmiss createsNeoForge cache withfinallevel,pos,context; laterhit nolevelcheck. Exact244 getCapability returnscachedvalue orqueriesSTOREDlevel ifloaded; invalidationclearsvalidity, neverrebindslevel. Samecoord/side inanotherlevel canreusefirstlevelcache after currentlevelBE admission. Notserialized,noclear/partition inTFclass. No runtimeoutcome/pack-wideclaim orfix; providerinvalidation native.

### Compatibility

Native NeoForge use/snapshot/placement, ladder/scaffolding, Bonemeal/BlockGrowFeature andcapabilities are GENERIC_CONDITIONAL_PRESENT. Actual bundled interop tags (immovable/relocation,treeattachments,compostactivators/randomiumexclusions) are declarations, externalconsumer behavior UNKNOWN untilproved. No directexternal source-specific combat override proven in scopedbodies (NONE_PROVEN), no packcertification. Dynamicplant/BE/capability bodies retaineligibility/sourceidentity. Passives/hazards/ninetypes/otherstructures/ASM/sourceclosure unfinished.

## Packages

| Mechanic | Primary classification |
|---|---|
| Rope native placement, support and movement | VANILLA_LIKE_EXTENDED |
| Magic Beans native growing terrain | CUSTOM_CONTROL |
| Uberous Soil native growth and shape transition | VANILLA_LIKE_EXTENDED |
| Timewood core native callback acceleration | CUSTOM_CONTROL |
| Transformation core native biome replacement | CUSTOM_CONTROL |
| Sortingwood core native inventory transfer | CUSTOM_RESOURCE |

## Custom source callers

| Type | Amount | Source identity |
|---|---|---|

## Scope and exclusions

- Six distinct utilities; protected MiningCore/OreMagnet reused, no duplicate.
- Sixteen full TF classes plus limited registrations/callers. TransformationLeaves particles only; generic tree/recipe/loot infrastructure not additional combat packages.
- TimeCore delegates real handlers, not universal24x or newsource. Interop tags are declarations, external consumers conditional.
- Remaining passives/hazards/ninecustomtypes, other structures/callbacks and ASM/compatibility/source closure unfinished.

## Future native controls

- Real Rope placement/axes/extension/support/drop/climb/platform/water with native interaction.
- Beans proper soil/air/creative/events/advancement; tick102, blocking15, leaves/clouds, persistence, realTimewood callbacks.
- Soil displacement/15 FakePlayer bone meal calls/specialMushgloom growth with nativegates/onecellspread.
- Grown/placed inactivecores, config/toggle/schedule, Time random/BE callbacks and actual Transformation quartbiomes.
- Sorting real block/entity handlers, ties/slots, extraction-before-simulation/remainder and cross-level cache boundary.

[Semantic packages and paths](semantic-sections/twilightforest-structural-utilities.json), [integrity](twilightforest-structural-utilities-integrity.json), [full validation](r2f8u-structural-utilities-validation.json).

Exact next task: Review remaining passive entities and environmental hazards (thorns, oreberry, knightmetal, fiery, fire_jet, reactor, slider, ominous_fire, acid_rain), all actual callers and other combat-significant structures/callbacks; finish nested ASM, compatibility and source exclusions. Protect R2f8 then Twilight COMPLETE promotion before IceAndFire. Static only; no runtime/L2/Stage/production/Phase6/7.
