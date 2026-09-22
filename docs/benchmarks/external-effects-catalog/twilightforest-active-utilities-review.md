# r2f8s - TWILIGHT_ACTIVE_UTILITIES_SEMANTIC_REVIEW_COMPLETE

Installed Twilight4.8.3345/raw Minecraft1.21.1/exact NeoForge21.1.244 static authority. Completes five active utilities and actual dispenser/mining-core alternatives, including complete ToolEvents class across protected prior subsets. No new custom DamageType;31/40 reviewed,9 unfinished. No runtime/L2/Stage/production/Phase6/7 changes. Maps, structural utilities, passive entities, hazards and remaining ASM/compatibility/source closure remain unfinished.

Adds 7 reviewed packages / 27 delivery cases. Twilight remains PARTIAL at 209/673 drafts, zero promoted. REVIEW_REQUIRED 0.

## Native contracts

### Authority

Installed Twilight4.8.3345/raw Minecraft1.21.1/exact NeoForge21.1.244 static authority. Completes five active utilities and actual dispenser/mining-core alternatives, including complete ToolEvents class across protected prior subsets. No new custom DamageType;31/40 reviewed,9 unfinished. No runtime/L2/Stage/production/Phase6/7 changes. Maps, structural utilities, passive entities, hazards and remaining ASM/compatibility/source closure remain unfinished.

### Watch inventory

PocketWatchItem registration stack1, no damage/armor attribute. inventoryTick server and LivingEntity: slot0..8 OR40 requests native MOVEMENT_SPEED5ticks/amp0 and JUMP5/0, ambientfalse/particlesfalse/iconfalse. Independently, living.isHolding(this) requests DIG_SPEED(Haste)5/0 with same flags, regardless of this callback stack slot/held boolean. Exact244 Player.Inventory.tick passes global indices: hotbar0..8, ordinary storage9..35, armor36..39, offhand40; raw vanilla compartment indices differ. Actual hotbar/offhand refreshes Speed/Jump; any genuine ticked watch plus a held watch can refresh Haste. No callback for arbitrary stored display/belt/Curio contents is invented. Other Living native inventories require a real caller; method accepting Living is not automatic Mob inventory ticking. Native status eligibility/merge remains. After removal, the last applied short effect expires normally; no custom persistent attachment or infinite status.

### Watch native

Speed native movement attribute+.2 ADD_MULTIPLIED_TOTAL at levelI, Jump native jump-power+.1 and safe-fall-distance+1, Haste native attack-speed+.1 total and ordinary mining multiplier1.2 at amp0. No direct HP, reach, invulnerability, Timewood tick acceleration or global time change. Existing stronger effects follow native merge, not amplifier stacking. Native noncombat tooltip is not another mechanism.

### Watch fatigue

ToolEvents.setup registers MobEffectEvent.Applicable. preventFatigueWithPocketWatch requires event.getApplicationResult true, exact DIG_SLOWDOWN(MiningFatigue), recipient currently isHolding PocketWatch in either hand; sets DO_NOT_APPLY. Exact244 CommonHooks.canMobEffectBeApplied posts the event before addEffect/forceAddEffect merge; Applicable.getApplicationResult is APPLY OR(DEFAULT && entity.canBeAffected(instance)). A prior denial stays denied; TF does not require status source/owner, server/player type, duration, amplifier or pocket inventory position beyond held identity. It prevents eligible new applications/refreshes, does not remove an already active MiningFatigue instance, cleanse other negative effects or bypass external later listeners. Native effect loading from NBT is a different path.

### Powder admission

Player interactLivingEntity checks target.isAlive, then actual held-hand powder and shrink=!player.isCreative. Helper rejects target instanceof OwnableEntity only when getOwner()!=null: resolved owner presence, not a generic tame/ownerUUID test. Then native entity-type holder must have TRANSFORMATION_POWDER datamap. No boss/allied/HP-threshold/LOS/attack-damage check inside helper; actual Player interaction reach/event admission remains. Air use produces only client CRIT particles in look-distance2 radius1 box, returnsSUCCESS without searching/transformation or cost. All32 installed directed mappings (16 pairs) are saved explicitly in package parameters and native resource witness; data maps may be extended by real datapacks.

### Powder pairs

Installed two-way pairs: Minotaur/ZombifiedPiglin, Deer/Cow, Boar/Pig, BighornSheep/Sheep, DwarfRabbit/Rabbit, TinyBird/Parrot, Raven/Bat, HostileWolf/Wolf, Penguin/Chicken, HedgeSpider/Spider, SwarmSpider/CaveSpider, Wraith/Vex, SkeletonDruid/Witch, CarminiteGhastguard/Ghast, TowerwoodBorer/Silverfish, MazeSlime/Slime. No installed boss/Player transformation entry. Mapping absence is not an invented blanket boss immunity. Runtime-loaded map overrides are conditional, not assumed present.

### Conversion order

EntityUtil.convertEntity requires ServerLevel, creates requested entity and rejectsnull. If destination Living, EventHooks.canLivingConvert posts cancelable Pre; rejection returnsfalse before old replacement/cost. Saves old passengers. Old Mob+new Mob branch invokes native oldMob.convertTo(newType,true): creates another destination, copies position/baby/noAI/name/persistence/invulnerability, transfers equipment via copyAndClear, adds entity, transfers current vehicle and discards old. No finalizeMobSpawn in this branch. Other branch copiesposition, if destinationMob calls finalizeMobSpawn(CONVERSION), then addFreshEntity and discards old. In that else branch the nested oldMob+newMob equipment copy condition is unreachable after the earlier branch. TF and native Mob helper ignore addFreshEntity boolean; no guarantee against external spawn cancellation. Native convertTo can returnnull and TF does not recheck it before later stages; no failure recovery invented.

### Conversion state

After replacement, inside try: remember NEW UUID; new.load(old.saveWithoutId(new.saveWithoutId(new CompoundTag()))); restore remembered NEW UUID; if Living setHealth(getMaxHealth()). Source writes into destination NBT, rather than copying only selected safe fields. Native saveWithoutId writes even removed entities; native Living read loads saved attributes/effects/absorption/health/hurt/death/brain state. AttributeMap.load uses saved values for attributes present in destination, so resulting maxHealth can reflect old persisted attributes rather than destination species default. setHealth is a direct native state reset after load, not heal(amount), damage, source or healing-event callback; no damage-resistance/shield/HP-return gate. It does not remove copied status effects. TF catches Exception only around UUID/NBT/health section, logs warning and continues later stages; not a transactional rollback.

### Conversion equipment

Crucial ordinary Mob hand/armor sequence: native convertTo transfers each nonempty stack with copyAndClear, emptying old slots; subsequent old Mob.save writes ArmorItems/HandItems lists containing empty compounds over destination NBT; new Mob.read replaces destination hand/armor slots with those emptied lists. Thus ordinary transferred hand/armor can disappear before final TF drop loop. Do not claim guaranteed equipment preservation or drops. BODY key is conditional: empty old body does not overwrite preexisting destination body key, so it can remain in seeded destination NBT. Subtype save/load overrides and actual slot layout remain native. TF then drops a SADDLE if old was saddled and new is not Saddleable, calls destination Mob.spawnAnim twice, and copyAndClear/spawnAtLocation for equipment that actually survives the reload. Saved old passengers are force-rebound to new entity; native startRiding admission still returns its own result, ignored. Living conversion Post follows, then sound and true return. Powder shrinks1 only on returnedtrue and shrinkStack flag. No loot/death attack source attributed to the Player.

### Powder dispenser

Registered TransformationDispenseBehavior selects every LivingEntity intersecting the one-block AABB immediately in front of dispenser with NO_SPECTATORS predicate, server only. Calls same transformEntityIfPossible(target,stack,true) for every returned entity. No explicit isAlive recheck here, no break after one success and no remaining stack count/empty check in the loop: one activation can transform multiple eligible recipients and calls shrink1 per success even after original stack count reacheszero. Native helper still rejects ownership/missingmap/conversionPre; dispenser itself does not directly damage. Its instance fired flag becomestrue on any success and is never reset in execute/playSound, affecting later sound only. Default item-ejection fallback is not called; unchanged stack returned on no success.

### Horn activation

Crumble Horn durability1024, native use starts72000tick TOOT_HORN. onUseTick requires remaining count>10 && count%5==0 && ServerLevel; count is REMAINING use time, not elapsed warmup. Exact244 native item-use tick hook may alter remaining count before callback. Therefore an eligible72000 first callback can act immediately and last10remainingticks are excluded. canContinueUsing tests same Item identity, reequip onlyslot/item change. Center=floor(eye+look*3), construct AABB.encapsulatingFullBlocks(center-2,center+1). WorldUtil.getAllInBB casts integer bounds and betweenClosed includes upper bound; resulting integer positions center-2..center+2 in each axis (125 positions), not only4cubed. No TF ray/LOS filter. Each successful crumble awards block stat toServerPlayer and hurtAndBreak1 on used hand, then break loop when damage>=max. Native wear/creative/enchantments remain; no direct Living HP request.

### Horn payload

Per nonair block require CRUMBLE_HORN datamap, exact installed63 mappings captured. Player user first posts BreakEvent and canceled returnsfalse, before random. AIR-result branch chance randomFloat<chance: Player additionally block.canHarvestBlock then removeBlock(false), block.playerDestroy with ItemStack.EMPTY and post-removal getBlockEntity, event2001/stat; nonplayer Living additionally EventHooks.canEntityGrief then destroyBlock(true). NonAIR branch chance succeeds ->setBlock(result.withPropertiesOf(old),3),event2001/stat; no nonplayer grief check there. Returntrue does not test boolean success of remove/set/destroy calls. Ordinary native terrain/loot/support consequences remain, not fabricated damage. Installed AIR mappings are .05; nonAIR .2 including crack/downgrade stone/copper/Twilight masonry. Full source table retained, not inferred by names.

### Horn secondary

The real Player BreakEvent can also reach protected ToolEvents.damageNonMazebreakerToolsMore: MAZEBREAKER_ACCELERATED state plus current MAINHAND damageable non-Mazebreaker item requests native wear16 before final break success. This may affect a held Horn or a different mainhand item while Horn is used offhand, and occurs before this Horn probability test. Earlier cancellation can suppress ordinary event dispatch; later rejection does not refund prior wear. Reuses protected maze_tool_durability, not another mechanic. Other protected native BreakEvent listeners keep their own conditions.

### Horn dispenser

Registered CrumbleDispenseBehavior acts only front block, requires stack.maxDamage != stack.damage+1 and a datamap entry. It ignores chanceToCrumble: AIR->destroyBlock(true), otherwise setBlock preserving matching properties/event2001. No TF Player BreakEvent, harvest or grief gate in this class. Requests native durability1 with ServerLevel/nullplayer, firedtrue; playSound resets firedfalse after successful sound. It does not use handheld box/countdown or guaranteeworld mutation success. Keep this legitimate alternate separate from handheld probability and admission.

### Magnet activation

Ore Magnet durability64, use starts72000tick BOW. release server && elapsed>10. Tries yaw/pitch offsets in order(0,0),(10,0),(10,10),(0,10),(-10,10),(-10,0),(-10,-10),(0,-10),(10,-10), stopping as soon as moved>0. Each ray uses eye to offset-look*32 convertedto BlockPos and integer VoxelBresenhamIterator, not collision raycast. If moved>0 native hurtAndBreak(moved) usedhand andsound. No cooldown, attack/hurt/source or XP call. isEnchantablefalse; book method compares Enchantments.UNBREAKING ResourceKey to each entry from book.getEnchantments().entrySet via Objects.equals, not entry key. Nonempty ordinary ENCHANTMENTS entries therefore reject even Unbreaking; empty ordinary list passes native superclass true. Native getEnchantments reads ENCHANTMENTS, not STORED_ENCHANTMENTS, so this is not a proven blanket ban on normal enchanted books. Other native anvil/enchantment admission remains.

### Magnet lookup

ToolEvents TagsUpdated refresh clears item/tree maps. For c-namespace tags whose path contains ores_in_ground/, derives suffix via substring15, finds matching c:ore_bearing_ground/suffix; iterates each ground thenore, puts last encountered ground as replacement unless ore.defaultState is respective ORE_MAGNET_IGNORE or MINING_CORE_EXCLUDED. Iteration order can select among multiple grounds; no hardcoded per-ore guarantee. If allowed and absent, AncientDebris->Netherrack fallback. Installed exclusion tags include minecraft:coal_ores; safe replacement tag aggregates native dirt/gravel/sand/nylium/base stone/end stone/ore replaceable and TF root-ground tags. Real loaded tag/data changes are generic conditional integration, not direct proof every external ore works.

### Magnet move

Ray scans inclusively and chooses first safe-replace-tag block as base, then first later nonAIR ore in selected map with no block entity. It does not stop at solid obstacles. findVein recursively visits six-axis neighbors, exact BlockState identity and cap24. Only initial selected ore explicitly checked for block entity; neighbors follow exactstate/cap. For each HashSet vein position, destination=source+(base-found); admit destination safe-replace ORcanBeReplaced ORair. Set source to mapped replacement.defaultState (STONE fallback), set destination to first selected ore BlockState, bothflags2, increment count regardless of setBlock returns. No TF break/place/harvest/grief/LOS event checks here; generic world hooks remain. HashSet order/overlapping targets and later native block updates retain their real behavior, not guaranteed atomic vein move or drops. No custom state persistence; actual changed blocks persist, maps rebuild on tag update.

### Mining core

MineLogCore uses same helper with sourceIsMineCoretrue and tree map, no held item/durability. SpecialMagicLog defaultACTIVEfalse, onPlace schedules20ticks; native no-item interaction togglesACTIVE if doesCoreFunction, scheduleswhenenabled; disabledconfig forcesinactive. Server scheduled tick only if ACTIVE&&enabled performs effect and reschedules20ticks; otherwise no reschedule. Mine core chooses random offset peraxis nextInt(2*range+1)-range; exact installed common miningCoreRange16, disabled when configuredrange<=0. Thus random endpoints eachaxis[-16,16], not 32block Player look ray. Core-specific extra is particles/sound to nearbyplayers(distanceSq<4096), noentitydamage. Light15 whenACTIVE, nativeblocks/persistedACTIVE. Other Time/Transformation/Sorting cores remain separate unfinished structure utilities.

### Lamp terrain

Lamp of Cinders durability1024/fireResistant, table/book enchantingfalse. useOn attempts burnBlock at clicked position immediately with no durability/side gate in TF: only exact BROWN_THORNS or GREEN_THORNS ->BURNT_THORNS.withPropertiesOf(old), true despite unchecked setBlockAndUpdate result, criterion/sound/particles. Airuse begins72000tick BOW; release requires elapsed>12 AND damage+1<getMaxDamage, then doBurnEffect. No hurtAndBreak/shrink/addCooldown anywhere in complete Lamp class: release checks a durability reserve but does not spend it. Server burn loop center=floor(eye+look*2), offsets-4..4 eachaxis729positions. Native thorn hazard details remain later; this utility converts blocks rather than source injection.

### Lamp ignite

Independently of server-only terrainloop, doBurnEffect if user instanceof Player iterates native getEntitiesOfClass(LivingEntity,new AABB(center.below2).inflate4), default NO_SPECTATORS. Excludes every Player and ignites each other Living for5seconds. No TF LOS, distance sphere, team/owner, alive, fireImmune or successful thorn-change predicate. Branch occurs outside explicit server-only guard, though actual authoritative fire ticks are server native. Nonplayer genuine use can burnterrain but has no ignition branch. Native igniteForSeconds floors5*20=100ticks; Living multiplies by BURNING_TIME thenceil and Entity onlyraises currentremainingticks, not additive stacking. Fire immunity/native water/powdersnow extinguish and FireResistance/damage eligibility remain. Native later ON_FIRE ownerless damage1 on20tick modulo, separate from initial ignition, ordinary source tags/mitigation and hurtreturn; no initial HP hit, enchantment postattack, direct/cause attacker or custom Lamp DamageType.

### Compatibility

PocketWatch effect-applicability hook and native utility logic belong to TF. NeoForge conversion Pre/Post, item-use/interaction, effect applicability, BreakEvent/harvest/grief, entity spawning/serialization and ordinary fire mitigation are GENERIC_CONDITIONAL_PRESENT. Dynamic c ore tags/data maps are shared integration points. Recipe-view compat discovery is presentation, not additional damage delivery. No direct external source-specific combat override is proven in these bodies (NONE_PROVEN scoped here), and no pack-wide compatibility certification. No Curios-specific watch consumer in source scan; actual vanilla inventory and either-hand tests retained. Ominous-fire conversion is a proven separate caller, its death/source predicate and payload remain unfinished hazard scope.

## Packages

| Mechanic | Primary classification |
|---|---|
| Pocket Watch native inventory effects | VANILLA_COMPOSITE |
| Pocket Watch Mining Fatigue application veto | BINARY_MECHANIC |
| Transformation Powder native entity replacement | CUSTOM_CONTROL |
| Crumble Horn native terrain transformation | CUSTOM_CONTROL |
| Ore Magnet and mining-core block relocation | CUSTOM_CONTROL |
| Lamp of Cinders thorn conversion | CUSTOM_CONTROL |
| Lamp of Cinders native nonplayer ignition | VANILLA_LIKE_EXTENDED |

## Custom source callers

| Type | Amount | Source identity |
|---|---|---|

## Scope and exclusions

- Complete five utility item classes, two dispenser behaviors, native data-map records, ore ray/core classes and ToolEvents are reviewed; old ToolEvents mechanics reused without redo.
- Actual32 powder mappings and63 crumble entries pinned. No arbitrary target conversion, synthetic native source or fallback damage introduced.
- Recipe-view integrations are informational; ordinary native hooks and dynamic tags/maps remain conditional, not blanket pack compatibility.
- OminousFire conversion caller and thorn hazard admission remain unfinished separate hazards; reviewing shared helper does not close those sources.
- Other maps/structural utilities/passive entities/hazards/nine custom types/ASM/source closure remain unfinished; no production, Stage, L2 or runtime work.

## Future native controls

- Actual global-slot PocketWatch effects plus new-vs-existing MiningFatigue application.
- Player/dispenser powder real mapping/ownership/conversion events, UUID/NBT/health/equipment/vehicle/passenger lifecycle.
- Handheld vsdispenser Horn remainingtime/box/probability/harvest/grief/wear contrasts.
- Actual OreMagnet tag caches, nine rays and24state-identical vein cap, enabled MiningCore alternate.
- Clicked/charged Lamp thorn transformation separately from native nonplayer ignition and later fire damage.

[Semantic packages and paths](semantic-sections/twilightforest-active-utilities.json), [integrity](twilightforest-active-utilities-integrity.json), [full validation](r2f8s-active-utilities-validation.json).

Exact next task: Review native Magic/Maze maps, Ore Meter and landmark ASM; remaining structural utility items/blocks (Rope, Magic Beans, magic cores and relevant callbacks), passive entities, hazards and nine custom DamageTypes. Complete remaining ASM/compatibility/source exclusions, R2f8 and final Twilight COMPLETE promotion before IceAndFire. No runtime/L2/Stage/production/Phase6/7.
