# r2f8w - TWILIGHT_CONTACT_HAZARDS_SEMANTIC_REVIEW_COMPLETE

Installed TF4.8.3345 / raw Minecraft1.21.1 / exact NeoForge21.1.244. Four contact DamageTypes now USED from actual calls: thorns, oreberry, knightmetal, fiery.35/40 closed; fire_jet/reactor/slider/ominous_fire/acid_rain unfinished. Static only, no runtime/L2/Stage/production/Phase6/7.

Adds 7 reviewed packages / 32 delivery cases. Twilight remains PARTIAL at 230/782 drafts, zero promoted. REVIEW_REQUIRED 0.

## Native contracts

### Authority

Installed TF4.8.3345 / raw Minecraft1.21.1 / exact NeoForge21.1.244. Four contact DamageTypes now USED from actual calls: thorns, oreberry, knightmetal, fiery.35/40 closed; fire_jet/reactor/slider/ominous_fire/acid_rain unfinished. Static only, no runtime/L2/Stage/production/Phase6/7.

### Source factory

All four call TFDamageTypes.getDamageSource(level,key), which delegates through entity and indirect helpers with both entities null. Native DamageSource(holder,null,null) has null explicit position; direct entity, causing entity and getSourcePosition all null. No owner, projectile, explosion or death-message exclusion changes the hit. Declarations use exhaustion.1 and when_caused_by_living_non_player scaling; null causing entity does not qualify for difficulty scaling. Fiery effects=burning is damage feedback, not an ignition instruction.

### Tags

Installed closure: thorns and oreberry = minecraft:no_knockback + neoforge:is_environment + neoforge:is_physical; fiery adds minecraft:is_fire to those three; knightmetal ONLY neoforge:is_environment. None is projectile/explosion/magic, none bypasses armor/shield/effects/Resistance/enchantments/cooldown/invulnerability. A physical classification tag is not required for armor mitigation. No vanilla thorn-enchantment retaliation is invoked by the thorns source name.

### Native pipeline

Real Entity.move on-ground stepOn and live-entity intersected-block entityInside deliver callbacks; noPhysics/early movement and world-loaded/removed gates remain. Repeated callbacks are requests, not guaranteed per-tick HP loss. LivingEntity.hurt retains invulnerability/client/dead/fire-resistance admission, incoming/shield hooks, hurt cooldown, armor/toughness, Resistance (max(1-.2*(amp+1),0)), applicable enchantment protection, absorption and damage pre/post. These four sources have no position, so native directional shield test returns false; a generic loader shield event can still change that result. Ordinary invulnerableTime>10 rejects requests<=lastHurt or admits only excess; no bypass. Actual HP depends on recipient and hooks. All four caller hurt returns are discarded; no dependent heal/status/extra hit is fabricated.

### Knockback

Thorns/Oreberry/Fiery suppress native hurt knockback by NO_KNOCKBACK. Knightmetal does not: admitted fresh hurt can call knockback(.4,0,0) because ownerless position is null. Native knockback event/resistance apply; near-zero direction is randomized by the vanilla loop, grounded Y=min(.4,currentY/2+strength). Not a proven no-motion source. Cooldown excess branch does not repeat fresh-hit feedback. No custom knockback body in the block.

### Recipient overrides

Thorns/Knightmetal can request ItemEntity damage; actual ItemEntity.hurt checks native invulnerability and stack.canBeHurtBy, then server integer item-health subtraction/destruction, not living armor/Resistance. Oreberry explicitly skips all ItemEntities; Fiery requires LivingEntity. Native ArmorStand is LivingEntity but its own hurt override rejects these four untagged-for-stand-breaking sources; Fiery lacks IGNITES_ARMOR_STANDS despite IS_FIRE. Other recipient overrides remain native. Client ItemEntity returntrue is not server item loss.

### Thorns contact

Brown and Green Thorns share ThornsBlock. entityInside requests4 against any entity except ItemEntity whose stack is in actual IMMUNE_TO_THORNS (Thorn Leaves and Thorn Rose). No age, motion, armor, crouch, water, side or living-only gate in this body. stepOn additionally invokes virtual entityInside when state block is ThornsBlock and AXIS=Y, then superclass. X/Z can still hurt through overlap. Waterlogged does not disable damage. Axis and six connector flags govern collision shape (central3..13 cube plus selected arms), not an attack ray.

### Thorns growth

Non-instabuild player onDestroyedByPlayer returns false; server first grows along both axis directions plus3 random directions. Each grow attempt length=1+randomInt3 but loop i=1;i<length gives0..2 new Green Thorns in consecutive empty blocks, stopping at first nonempty; new axis matches direction. Native outer BreakEvent/adventure admission occurs before callback; item mining/durability callback can already run before rejected removal, and GameMode destroyBlock can return true despite removeBlock false. No ordinary block destruction/drop on failed removal. Creative delegates normal removal. Registered Brown/Green strength50/resistance2000, piston BLOCK, no loot. Geometry/regrowth is independent of HP damage; no synthetic growth attack.

### Burnt and exclusions

Protected LampOfCinders.burnBlock converts exact Brown/Green to Burnt using withPropertiesOf; lamp behavior remains unchanged. Burnt virtual entityInside server destroys itself without drops for LivingEntity OR Projectile; no hurt, item-entity removal or projectile discard. Inherited Y stepOn dispatches this harmless override. Its player removal installs legacy fluid state, without regrowth; instabreak/no loot/piston DESTROY. Thorn Rose extends native BushBlock and SpecialStemLeaves extends LeavesBlock with stem-distance override; neither has a contact-hurt callback. Dropped rose/leaves thorns immunity does not make their carrier immune. Leaves are flammable from registration; name alone is not a thorns attack.

### Thorns sources

Legitimate producers: registered block-item placement, native failed survival break growth, installed Thornlands placed/configured feature, and final-castle thorn foundation. Thorn feature uses Brown states, axis-oriented segments, air/leaves replacement, horizontal abs-offset<7, initial cloud-height limit and recursion; leaf/rose additions are separate non-hurt blocks. Installed chunk blanketing locks Thornlands, OCEAN_FLOOR_WG and integrity.7. Final-castle foundation uses Brown descending vines until Deadrock or worldY<=90 and Green branches; actual structure/chunk placement boundaries remain. No worldgen path directly hurts an entity; contact later delivers same type.

### Oreberry contact

All four Iron/Gold/Copper/Essence OreBerryBlocks request oreberry1 on entityInside except ItemEntity, then super.entityInside. TFBushBlock extends Block and has no such override; native BlockBehaviour body is empty. Thus no sweet-berry slowing, movement threshold, fox/bee exception or age>0 requirement. Age0/1 still damage when callback reached. For age>=2 and collision context !=empty, almost-full [0.001,0,0.001..15.999,15.999,15.999] box allows contact; empty context uses normal shape. Path DANGER_OTHER/isPathfindablefalse are AI hints, not immunity.

### Oreberry state

Native default AGE0/SNOW_LAYERS0. CanSurvive requires support in OREBERRY_BUSHES_SURVIVE or same mature bush below; Iron/Gold/Copper additionally raw brightness<13, growth requires<10. Essence constructor surviveInLight=true removes both light tests. RandomTick AGE<3, randomInt20==0, canGrowAt ->age+1; OreBerry is not Bonemealable and has no fruit-bush upward growth override. Changes in support/light are not immediate guaranteed deletion: base updateShape handles snow then Block, no OreBerry survival-destruction override. Registered genuine placement checks native survival. Natural UndergroundPlantFeature maxCount1 descends from origin to above minBuildHeight; empty+5/6 test, configured ripeAGE3 canSurvive and outside located structure unless allowed; set flags18. Failed empty/random branch jitters X/Z; no free helper insertion fixture.

### Bush harvest

Shared TFBushBlock useWithoutItem at AGE3: server real BLOCK loot context (state,center origin,EMPTY tool), current berry table ->ItemHandlerHelper.giveItemToPlayer, sound, AGE2, BLOCK_CHANGE. No harvest cost/HP/status; empty or modified loot still resets age. Oreberry installed harvest gives exactly1 matching Iron/Gold/Copper berry or Essence berry, each separate from already-protected food/XP item consumption. Normal block loot returns bush item and additionally ripe berry-table roll at AGE3. Real interaction/events, inventory remainder/drop and loot hooks remain.

### Fruit bushes

Shared ordinary fruit BerryBushBlock has no contact damage or sticky movement. Growth adds native resource/geometry: parent age growth, then separate1/20 upward attempt if count of consecutive same bushes below<2 and brightness>=8/survival. tryGrowUpwards adds another1/3 roll and original age>=2, places default age0 into air or replaces snow preserving layers. Bonemeal target age<2 OR air/snow above; success true, ifyoung age+=1or2 clamped2, then upward attempt uses original state. Bone meal cannot directly ripen2->3 and does not apply the random-growth height<2/brightness test inside performBonemeal. Actual native bone-meal admission/cost still applies. DarkTowerBerry additionally refuses growth while snowlogged; matching DIE tag below schedules1tick and destroys with drops when area loaded. No new berry-consumption effects reviewed here.

### Snowlogging

Shared TFBush snow state changes collision/resource independently of hurt. Player SNOW use when layers<8 and native snow survival: new shape must be unobstructed for player; consume1 unless infinite, set flags19, sound, mark snowy dirt below. No explicit server guard inside body; real interaction governs execution. Age shapes:0 small,1 medium,2/3 full block; snow-layer shapes union for young bushes. At growth age2, snowlogged bush can put a single snow layer above if replaceable or zero-layer SnowLoggable. Ordinary nonsecondary break of snowlogged bush intercepts removal:6block OUTLINE/no-fluid ray; hitY<=snowheight clears snow only, else drops bush normally unless creative and replaces with native snow layers. Returnsfalse to outer removal. Secondary bypasses interception. No direct entity damage, shove or freeze call. Random melt at blocklight>11 and layers1..7 drops native snow resources then clears layers;8doesnotmelt here. Native support-loss update clears snow state. Wider SnowLoggable users/ASM consumers remain global-closure work.

### Knightmetal contact

Knightmetal entityInside unconditionally requests4 through ownerless source; no living-only, owner/team, equipment, crouch or water gate. Shape1..15 inset; native movement/contact needed. Default waterloggedfalse, placement true only water-tag fluid amount8; water schedules do not suppress hazard. Registered block-item,9 matching ingots recipe, native drop-self/decompression are genuine sources. Armor item protection is normal pipeline; no special Knightmetal armor immunity is coded.

### Fiery contact

Fiery stepOn checks !entity.fireImmune(), entity instanceof LivingEntity and FEET stack item !=exactTF FIERY_BOOTS, then requests fiery1, then super. No isSteppingCarefully/crouch test or generic Frost-Walker equipment check in this body. Native MagmaBlock separately tests !isSteppingCarefully and uses hotFloor; this is not that source. No ignite, remaining-fire write or secondary hurt. Native IS_FIRE admission makes Fire Resistance reject before incoming event. If admitted while Frosted, protected TF incoming callback downranks Frosted even if later mitigation gives0HP; early fire immunity/boots/FireResistance prevents callback. Direct/owner null also prevents causing-Living Yeti armor retaliation.

### Fiery utilities

Fiery.isFireSource returns true for every direction; actual installed FireBlock.tick checks block below with UP under doFireTick and survival, skipping rain/nonfuel extinction branches when true. It does not spontaneously create fire or replace fire DamageTypes; later real fire uses native in_fire/on_fire. Actual minecraft:strider_warm_blocks includes Fiery Block. Native Strider tick unless noAI considers current/on-block warmth or lava, but a cold Strider vehicle overrides warm state; setSuffocating(false) removes native -.34f ADD_MULTIPLIED_BASE speed penalty. Ridden speed uses attribute*(cold?.35:.55)*boost. This is native warmth control, not an HP heal or resistance buff. Fiery item fireResistant only concerns dropped item; CTM conditional skipRendering is cosmetic.

### Persistence compat

Block states AGE/SNOW/AXIS/connectors/WATER are native saved states; no custom owner, damage timer, accumulation or source rewriting. Time core may call genuine random ticks with unchanged recipient/state gates (protected R2f8u). GENERIC_CONDITIONAL_PRESENT for actual loader interaction/break/damage/shield/knockback/loot/bone-meal hooks. CTM is direct conditional visual integration, no combat override. Other external tag consumers UNKNOWN; scoped direct source-specific external combat override NONE_PROVEN, no pack certification. Five other damage types and remaining structures/events/ASM/source closure unfinished.

## Packages

| Mechanic | Primary classification |
|---|---|
| Thorns ownerless contact damage | CUSTOM_DAMAGE |
| Thorns regrowth and Burnt removal | CUSTOM_CONTROL |
| Oreberry ownerless contact damage | CUSTOM_DAMAGE |
| Knightmetal ownerless contact damage | CUSTOM_DAMAGE |
| Fiery Block native contact damage | CUSTOM_DAMAGE |
| Native berry bush growth, harvest and snow state | VANILLA_LIKE_EXTENDED |
| Fiery Block native fire support and Strider warmth | VANILLA_COMPOSITE |

## Custom source callers

| Type | Amount | Source identity |
|---|---|---|
| twilightforest:thorns | 4 per admitted native callback; not final HP or guaranteed DPS. | Both null; explicit/source position null; no owner/projectile. All four call TFDamageTypes.getDamageSource(level,key), which delegates through entity and indirect helpers with both entities null. Native DamageSource(holder,null,null) has null explicit position; direct entity, causing entity and getSourcePosition all null. No owner, projectile, explosion or death-message exclusion changes the hit. Declarations use exhaustion.1 and when_caused_by_living_non_player scaling; null causing entity does not qualify for difficulty scaling. Fiery effects=burning is damage feedback, not an ignition instruction. |
| twilightforest:oreberry | 1 per admitted native callback; not final HP or guaranteed DPS. | Both null; explicit/source position null; no owner/projectile. All four call TFDamageTypes.getDamageSource(level,key), which delegates through entity and indirect helpers with both entities null. Native DamageSource(holder,null,null) has null explicit position; direct entity, causing entity and getSourcePosition all null. No owner, projectile, explosion or death-message exclusion changes the hit. Declarations use exhaustion.1 and when_caused_by_living_non_player scaling; null causing entity does not qualify for difficulty scaling. Fiery effects=burning is damage feedback, not an ignition instruction. |
| twilightforest:knightmetal | 4 per admitted native callback; not final HP or guaranteed DPS. | Both null; explicit/source position null; no owner/projectile. All four call TFDamageTypes.getDamageSource(level,key), which delegates through entity and indirect helpers with both entities null. Native DamageSource(holder,null,null) has null explicit position; direct entity, causing entity and getSourcePosition all null. No owner, projectile, explosion or death-message exclusion changes the hit. Declarations use exhaustion.1 and when_caused_by_living_non_player scaling; null causing entity does not qualify for difficulty scaling. Fiery effects=burning is damage feedback, not an ignition instruction. |
| twilightforest:fiery | 1 per admitted native callback; not final HP or guaranteed DPS. | Both null; explicit/source position null; no owner/projectile. All four call TFDamageTypes.getDamageSource(level,key), which delegates through entity and indirect helpers with both entities null. Native DamageSource(holder,null,null) has null explicit position; direct entity, causing entity and getSourcePosition all null. No owner, projectile, explosion or death-message exclusion changes the hit. Declarations use exhaustion.1 and when_caused_by_living_non_player scaling; null causing entity does not qualify for difficulty scaling. Fiery effects=burning is damage feedback, not an ignition instruction. |

## Scope and exclusions

- ThornRose and SpecialStemLeaves do not define contact damage; normal leaves/rose shapes/decay/flammability are source dispositions.
- Ordinary fruit bushes have no sweet-berry slowing/damage. Protected berry food/XP and Cinder Lamp packages reused without duplicate.
- Worldgen/recipes/loot are legitimate producers; decorative geometry does not create an additional attack.
- Remaining5 custom types, structures/events, additional SnowLoggable consumers and nested ASM/compatibility/source closure unfinished.

## Future native controls

- Four real block contact sources with source identity, age/axis/water, exact item exceptions and mitigation/subtype controls.
- Thorn survival break/regrowth, event veto/mining cost, native lamp conversion and Burnt living/projectile removal.
- Oreberry/fruit growth, actual harvest/loot, native bonemeal and snow geometry/persistence.
- Native Fiery fire support and Strider warmth, separate from fiery HP damage.

[Semantic packages and paths](semantic-sections/twilightforest-contact-hazards.json), [integrity](twilightforest-contact-hazards-integrity.json), [full validation](r2f8w-contact-hazards-validation.json).

Exact next task: Review FireJet, Carminite Reactor and Slider block/entity hazards, then Ominous Fire conversion and Acid Rain/progression with exact source/return dependencies; finish other structures/events, nested ASM and compatibility/source exclusions. Protect R2f8 and final Twilight COMPLETE before IceAndFire. Static only.
