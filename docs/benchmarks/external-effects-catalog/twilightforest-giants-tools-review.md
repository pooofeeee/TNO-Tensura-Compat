# r2f8d - TWILIGHT_GIANTS_TOOLS_SEMANTIC_REVIEW_COMPLETE

Installed TF4.8.3345/raw Minecraft1.21.1/exact NeoForge21.1.244. ANT customsource is neoforge:is_physical only in scoped native mergedtags; no armor/shield/Resistance/enchantment/cooldown bypass, projectile/fire/explosion/no_knockback tags. Native armor, directional shield, Resistance/generalprotection, absorption, events/cooldown remain; hurttrue is not measuredHP. CausingLivingnonPlayer for ANT enables Playerdifficulty Peaceful0/Easymin(a/2+1,a)/Normal a/Hard1.5a. Native Player weapon attacks use minecraft:player_attack, not ANT. No runtime/L2/SHP/Stage/production claim.

Adds 4 reviewed packages / 16 delivery cases. Twilight remains PARTIAL at 92/253 drafts, zero promoted. REVIEW_REQUIRED 0.

## Native contracts

### Pipeline

Installed TF4.8.3345/raw Minecraft1.21.1/exact NeoForge21.1.244. ANT customsource is neoforge:is_physical only in scoped native mergedtags; no armor/shield/Resistance/enchantment/cooldown bypass, projectile/fire/explosion/no_knockback tags. Native armor, directional shield, Resistance/generalprotection, absorption, events/cooldown remain; hurttrue is not measuredHP. CausingLivingnonPlayer for ANT enables Playerdifficulty Peaceful0/Easymin(a/2+1,a)/Normal a/Hard1.5a. Native Player weapon attacks use minecraft:player_attack, not ANT. No runtime/L2/SHP/Stage/production claim.

### Giant body

GiantMiner and ArmoredGiant bothHP80/speed.23/baseattack2/follow40/stepheight1.2, registered2.4x7.2, nofireproof. Monster ordinary Float1/Melee4/strolllook, retaliation/visiblePlayer; no customhurt, regen, HPthreshold, ranged, defensephase, undeadbehavior, minionmaster or deathoverride. No incoming tags granting giant-specific fall/freeze/knockback/boss immunity in scoped TFcontributions. canRidefalse (ordinaryforced/event mechanics stillnative). Constructor allslotdropchance0; native equipment/HPsave/load retained, no customsavedresource. Equipment onceassigned appliesnativeattributes; no damage formula derived solely from visualsize. Vanilla Mob melee checks native attackAABB intersects victimhitbox, rootBB inflated sqrt(2.04F)-.6 inXZ, noYinflation, withvehicleXZunion ifpresent. This differs from Player interactionrange attributes; defaultMeleeGoal interval20 independent of weapons ATTACK_SPEED.

### Giant equipment

finalizeSpawn super thenpopulateDefaultEquipmentSlots andpopulateDefaultEquipmentEnchantments; Giant overrides enchantSpawnedWeapon/Armor with emptybodies, so no defaultspawn enchantedgear. Miner getsGIANT_PICKAXE mainhand; Armored callsMiner equipmentthenreplaceswithGIANT_SWORD and fullvanillaironhelmet/chest/legs/boots. Giant tier SimpleTier uses1024/speed4/attackbonus1/enchantvalue5/incorrect=#incorrect_for_stone_tool, repairsGiantCobblestone; GiantSword additionally acceptsIronwoodIngot. RegisteredPick damageargument8=>MAINHAND additive9; Sword argument10=>additive11, speedmodifier-3.5 both. Thus default equipped Mob effectiveattack2+9=11 miner and2+11=13 armored, NOT base2 or Player10/12. Armored fulliron defense2+6+5+2=15, toughness0/knockbackresistance0, ordinarydamagepipeline; Minerordinarybasearmor0. Equippedattrs/nativeenchantments/mutations canchangevalues, no hardcodedHP damage. Helper itself doesnot invoke Player itempostHurtEnemy durability; native mob hit with theseweapons is not a Player held-itemattack. Weaponrepair/acquisition/loot are not damagebonuses.

### Giant attack

Both classes use inheritedGiantMiner.doHurtTarget ->EntityUtil.properlyApplyCustomDamageSource(self,victim,ANT(self),null). Direct=causingactualGiantMiner ORArmoredGiant; actualtypeprofileonlyoneclassfieldcaller inheritedbysecond. Requesteffectiveattack11/13 afterordinaryequipmentstate, thennativeenchantmenthelper with affectedentity=ATTACKER (protectedTFhelperquirk), nativevictim.hurt. Onlytrue executes helperknockback/postattackenchants, setsLastHurtMob toattacker itself; preserveidentities/quirks. No additional stomp/crushing/terrain destruction on giantmob melee. Lack ofsuccessfulhurt suppressespostcallbacks, not ordinaryAIattemptcooldown. Native mob-dealt Playerdifficulty scaling applies onsource; no customseverance/resource damage.

### Giant producers

Native registrations havebothspawneggs and GiantMiner.canSpawn requires belowblockGIANTS_SPAWNABLE_ON (#TFclouds); instancecheckSpawnRules only counts GiantMiner andsubclasses in ownBBinflate100,10,100 andrequires<5, doesnotcallsuper; clustermax1. Spawnengine/placement/finalize/events/Peaceful despawn remain. CloudCastleComponent.postProcess explicitly calls placeGiantMiner andplaceWarrior atlocal14,4,14 and17,4,17 wheninsidecurrentchunkbound; create/setposition/setPersistenceRequired/nativefinalizeMobSpawn STRUCTURE/addFreshEntity. GiantHouse andTrollCave native controlledspawnconfigs includebothweight10/group1; these are producerdefinitions, not claim naturalspawn ignores frameworkrules. Both finalizedpaths populateactualweapons/armor; a manufacturedunfinalizedentity hasbaseattack2, not a representativepositivecontrol. No nativeweaponthrow or Playeritem behavior invoked by theseproducers.

### Giant player tools

Player standardbaseattack1 +GiantPick9=10 ORGiantSword11=12; standardattackspeed4-3.5=.5, 40tick fullrecharge withnormalnativecooldown/critical/sweep/enchantment predicates. Sword has nativeSWORD_SWEEP ability and ordinarysuccessfulprimary itemdurability1; Pick nativeDigger successfulprimarydurability2. No Giant overrideofhurtEnemy/postHurtEnemy orcustomDamageSource; normalnative Player hooks retained. MAINHAND damage/speed, but BOTH tools addBLOCK_INTERACTION_RANGE +2.5 idtwilightforest:reach_modifier andENTITY_INTERACTION_RANGE +2.5 idrange_modifier inEquipmentSlotGroup.HAND, sooffhandcanextendordinaryothermainhandattack/interaction. Default survivalPlayerblockrange4.5=>7,entityrange3=>5.5; no genericMobAIreachincrease, because Mob nativeattributes lacktheseinteractioninstances andequipmentonlymodifiesexistinginstances. Two gianttools shareexactIDs: normalnativeequipmentupdate removesbyID thenaddsmodifier forchangedslots, so no+5 stacking. Removing/changingone whileotherunchanged canremove sharedmodifier untilremainingitem receivesanothernativeequipmentupdate; fixturemustobserveactualattribute/state, not assumeonebonusperhand. Slot/order effects are staticcodeconsequence, not runtimeobservation. No fixed blockbreaking radius forentityattacks andnoautoAoE fromgiantscale.

### Giant mining speed

GiantPick inheritsnative TOOL rules forpickaxetag withGIANTtierstone-equivalentincorrecttag,speed4/default1/damagePerBlock1; nominaldurability1024. getDestroySpeed multipliesparentresult64 ifexactGIANT_OBSIDIAN, thenanother64 ifblock instanceofGiantBlock. Allfourregisteredgiantblocktypes aremineable/pickaxe inTFcontribution; GiantObsidian is aGiantBlock, so normaleligiblebase4=>16384 speed (=4*4096), otherGiantBlock=>256; these are toolspeed values, NOT instantbreak/HPdamage. Nativehardness/divisors/toolcorrectness/effects stillapply. GiantObsidian hardness204800 andresistance8192000; no inferred sameasnormalobsidian ordiamond requirement justfromname. NativeTFgiantincorrectextendsstoneincorrect but giantobsidian isnotnativevanillaneedsdiamond justbecausebasepropertiescopied. Exactalltagcontents available inprotectedchainclosure. Noeffectonmobdamageamount.

### Giant volume break

GiantPick.canAttackBlock whenmainhandmatchesitem resets attachmentonly ifminingtime!=levelgameTime: miningtime=currenttick,breakingfalse,conversion0, thensuper. ExactNeoForge CommonHooks.fireBlockBreak calls item.canAttackBlock beforeBreakEvent, including recursivegameMode.destroyBlock; keepssame-tickrecursionguard intact. ToolEvents registeredBreakEvent handler needsServerPlayer/mainhandGiantPick/native doPlayerHarvestCheck true; requiresminingtime==currenttick&&!breaking. Setbreakingtrue; calculateoriginstatedrops withorigin/state/Player/toolcontext; optionallysetconversion64onlywhenfirstdropBlockItem hasconversionmapping ANDall64positions currentlysameBlockidentity (propertiesnotchecked), otherwise0 whenbranchruns. Cancelouterevent,emit2001, callPlayer.gameMode.destroyBlock(original), theneachotherposition withsameBlockidentity callnativegameMode.destroyBlock. Volume gridaligned 4x4x4 inclusive: mincoords=coord&-4,max=coord|3, includingnegativecoords. Not centeredradius4 andnotanyblockinvolume. No sneak/extrareach/LOS guard inhandler. Recursivenative destroy usesordinarygamemode/adventure/harvest/blockevents/toolbreak/drop rules andguardpreventsanotherareaexpansion; eachreturnignored. Partialdenial/failure doesnotabortothercandidates; evenoriginalfailure canleaveothermatchesattempted. Ifitembreaks midloop, remainingcalls stilloccur withcurrentequipment/nativeadmission. Resetbreakingfalseafterloop, no try/finally. Attachment is builder-only (no serialize/sync/copy): transientminingtime/breaking/conversion, no persistent HP/resource. Mobgiants never invoke this Player-only terrainhandler.

### Giant volume loot

Loot grouping is sideeffect/exclusion fromcombatpackages, but exactbudgettraced. Registrationmap: droppedCOBBLESTONE->giantcobblestone,OAK_LOG->giantlog,OAK_LEAVES->giantleaves,OBSIDIAN->giantobsidian. Globalmodifier installed viaNeoForgeglobal list/TFgiant_pick_grouping; condition THIS_ENTITY Player,currentgameTime==attachmentmining,conversion>0. doApply requiresfirstgeneratedlootBlockItem withmapping, decrementsconversion by1; ifold==64 returnsonegiantitem replacingentirelist, otherwiseemptylist. Doesnot itself rechecktool/breaking/all64success; normalconditionguardsbudget. Firstmatchingdrop emitsgiant eveniflaterbreaksdenied; successfulnativeblockcallbacks determinewhichdropcalculationsoccur. Counter initializedfromoriginfirstdrop/allstates, no rollback/all-or-nothing claim. GiantBlock placement fillsaligned64volume serverside onlywhenallpositionsreplaceable; ifvolumeincomplete onRemove, guardedrecursive destruction ofothermatchinggiantblocks destroyBlock(false), no Playerhurt/customsource andnoitemarea-eventrequirement. Not separate boss/HP/status mechanic.

### Maze tools

MAZEBREAKER_ACCELERATED tag actualidmazebreaker_accelerated_mining expandsmazestone+castleblocks. MazebreakerPick extendsPickaxe withDiamondtier, mainhanddamageadd1+tier3=4 (Playerdefault5),speed-2.8 (Player1.2),durability1561/nativepickaxeTool, getDestroySpeed=parent*16 onlytaggedblocks (nominal8*16=128 wherepickaxeefficient), nativehardness/mitigationnotbypassed. isValidRepairItemfalse plussetNoRepair; no specialentityhit/source/armorpenetration. Independent ToolEvents.damageNonMazebreakerToolsMore BreakEvent: taggedstate &&heldmainhanddamageable &&!(item instanceofMazebreakerPickItem) =>nativehurtAndBreak16, beforefinalbreakresult withnoownserver/creative/harvest/successcheck; nativeItemStack durabilityhooks/creative/Unbreaking apply. Handler registeredbeforegiantmining atsameordinarypriority; giantouterevent canrequest16 andrecursivenativeevents requestagain, not oneflat16 per64blockgesture. NativeTooldurabilitywhenactualmining isadditional. Canceledbeforethislistener normallyskip viaeventbus; latercancellation doesnotrefundearlierdurability. No arbitraryextraHPdamage toPlayer. GiantPick isnotMazebreaker andthereforeeligible. Common block/taglookup pinned; this closesgenericextra16 rule foranydamageableheldtool, not justgiants.

## Packages

| Mechanic | Primary classification |
|---|---|
| Giant and Armored Giant native ant melee | CUSTOM_DAMAGE |
| Giant weapon attack and interaction attributes | VANILLA_LIKE_EXTENDED |
| Giant Pick speed and recursive volume mining | CUSTOM_CONTROL |
| Maze-block tool speed and extra durability | CUSTOM_RESOURCE |

## Custom source callers

| Type | Amount | Source identity |
|---|---|---|
| twilightforest:ant | Effectiveattack default11 GiantMiner/13 ArmoredGiant afternativeequipment; base2 ifunequipped, nativeenchantments apply. | direct=causing actual GiantMiner orArmoredGiant |

## Scope and exclusions

- Ten fullnativeclasssurfaces; limitedevent/registry/structureproducers explicitlylisted. FullToolEvents includesothermechanics stillpending; reviewedmethods areexactlyscoped.
- Ordinary ironarmor, passivegiantsize/AI, repairingredients and equipmentdrops are nativeparameters/exclusions, notcustomdefense/statuspackages.
- Giantblockplacement/cascade andlootgrouping fullytraced toexplainterrainresourceeffects, notpromotedasseparatecombat/HPmechanics.
- GiantPick terrain isPlayer-only; no invented giantmobAoE/stomp/miningattack. ANTclosedthroughactualinheritedcallers.
- Mazeextra16 andMazebreakerspeed/exemption closedhere forreuse; no duplicatelatertoolpackage.
- FifteenothercustomDamageTypeprofiles andremainingTwilightcontentunfinished; zero promotion, noIceAndFireyet.

## Future native controls

- Native finalized/equipped miners/armoredgiants, exactsource and11/13 request/15armor; failedhurt/nativeHP/equipmentpersist.
- Playergiantweapons main/offhand/dualattributeIDs, ordinaryprimary/sweep/critical/cooldown and nativeitemsuccessdurability.
- GiantPick gridalignedsameblockvolume, negativecoords/mixedstates/events/partialbreak/toolbreak/lootbudget/transientstate.
- Giantobsidian toolspeedversushardness andgiantblockcascade; no entityHP consequence.
- Mazebreaker vsotherdamageabletool onactualtag, native16durabilitywithcancel/creative/Unbreaking andrecursiveGiantPick controls.

[Semantic packages and paths](semantic-sections/twilightforest-giants-tools.json), [integrity](twilightforest-giants-tools-integrity.json), [full validation](r2f8d-giants-tools-validation.json).

Exact next task: Continue Task C with remaining melee/control mobs and minibosses (spiders/swarm, MosquitoSwarm, Boggard/HelmetCrab, Redcap/Sapper, Kobold/Troll, golems/borers, Wraith and unfinished undead/summon paths), then remaining items/scepters/armor/charms/projectiles/hazards/resources and15 remaining custom caller profiles. Reuse protected giants/tools/chain/mounted/ranged/boss/Frosted work. Protect each subsection toward R2f8 and finalwholeTwilight promotion. IceAndFire onlyafterCOMPLETE Twilightpushed; no runtimeboss/L2/Stage/production/fixes/balancing/Phase6/7.
