# r2f8v - TWILIGHT_PASSIVE_ENTITIES_SEMANTIC_REVIEW_COMPLETE

Installed Twilight Forest 4.8.3345, raw Minecraft 1.21.1 and exact NeoForge 21.1.244. Eighteen full passive/quest classes and selected genuine producers/callers reviewed. No custom DamageType added:31/40 reviewed,9 unfinished. Static research only; no runtime/L2/Stage/production/Phase6/7.

Adds 4 reviewed packages / 21 delivery cases. Twilight remains PARTIAL at 223/750 drafts, zero promoted. REVIEW_REQUIRED 0.

## Native contracts

### Authority

Installed Twilight Forest 4.8.3345, raw Minecraft 1.21.1 and exact NeoForge 21.1.244. Eighteen full passive/quest classes and selected genuine producers/callers reviewed. No custom DamageType added:31/40 reviewed,9 unfinished. Static research only; no runtime/L2/Stage/production/Phase6/7.

### Quest config

Component QuestingRamCurrentContext starts with FALLBACK: all16 exact vanilla wool colors and entities/questing_ram_rewards. Installed twilight/quests/questing_ram.json agrees. Codec requires all16 DyeColor bits and nonempty Ingredients. Reload listener matches path questing_ram regardless namespace, applies each matching entry in map iteration order (last wins); absent file resets fallback, parse error throws. No fixed namespace priority or merged quest assumed. Context is shared/current rather than saved per ram. OnDatapackSync sends current context to one joining player or all; registered playToClient packet only updates client context, not server color flags.

### Quest accept

Quest Ram has synced integer ColorFlags initially0 and Rewarded false. tryAccept iterates current Ingredients; first matching nonnull not-yet-present color sets bit1<<color.id, emits50 particles/ambient and returns true. It does not consume itself or heal. isItemTempting returns immediately for first matching Ingredient, even if already collected; overlapping configured Ingredients can therefore differ from tryAccept. Genuine defaults have no overlap. countColorsSet counts all32 integer bits but legitimate16-color feeding only sets16; no injected flags used as a fixture.

### Quest hand

Native interactAt on server invokes tryAccept then ItemStack.consume(1,player), returning SUCCESS. Native consume preserves infinite-material players. Client or failure delegates Animal/Entity interactAt; no custom mobInteract bypass. Real server interaction retains packet range/world-border/feature admission, CommonHooks.onInteractEntityAt cancellation and native advancement/swing. No normal feeding/breeding: isFood false, offspring null.

### Quest dropped

QuestRamEatWoolGoal MOVE/LOOK priority2 selects nearest ItemEntity in ram AABB inflated16: onGround OR inWater, alive, nonempty, line of sight and isItemTempting. Continuation requires ram alive, navigation not stuck/not done, live target and still tempting. Start stops old path, looks at target and requests navigation speed1. Server tick checks target/nonempty eligibility through isItemTempting; distance squared<6.25 and successful tryAccept ->DISCARD ENTIRE ItemEntity then EAT game event. It does not shrink1, honor item thrower/pickup delay, or call mobGriefing in these bodies. Start predicates and native AI scheduling remain; no claim an arbitrary helper call is legitimate feeding.

### Quest reward

customServerAiStep pre-decrements divider initially0, resets70+randomInt50 on expiry; if bitCount>15 and !Rewarded, rewardQuest then sets Rewarded true. Complete but waiting emits5 particles/ambient per AI step. Reward uses current context table and real LootParams with THIS_ENTITY, PIGLIN_BARTER param set; getRandomItems then spawnAtLocation(stack,1). Bundled default gives one Crumble Horn and one Bundle. Bundle set_contents requests Quest Ram Trophy plus one each Coal/Iron/Copper/Lapis/Gold/Diamond/Emerald block. Native bundle manipulator clears prior contents and uses actual tryInsert capacity/item rules; unmodified 64-stack defaults fit all8. No reward HP/status. Loot hooks/loaded tables may change output; no synthetic inventory grant.

### Quest progress

After loot, every ServerPlayer in ram AABB inflated16 gets QUEST_RAM_COMPLETED trigger; no contributor/line-of-sight filter here, normal criterion player predicates still apply. LandmarkUtil marks QUEST_GROVE only for nonnull home in current dimension, nearest matching TFStructureStart; it also triggers STRUCTURE_CLEARED around home AABB inflated32. No home does not prevent loot/reward flag, but cannot mark a grove. Native death loot quest_ram has no pools, so killing is not an alternative quest reward.

### Quest spawn save

QuestGrove quest_ram marker within chunk bounds calls FeaturePlacers.placeEntity: create, persistenceRequired, moveTo, actual finalizeMobSpawn STRUCTURE event, set home GlobalPos, add entity/passengers, clear marker to AIR. Native spawn eggs are alternate producer without this home assignment. Saved ColorFlags, Rewarded and HomePos (legacy Home migration); divider is transient, resets after load. Home radius13, native AttemptToGoHomeGoal speed1.25 seeks random point toward home if outside valid-dimension radius; no teleport or hard barrier. Quest Ram70HP/.23 speed, PanicGoal1.38, cannot ride; no custom hurt immunity, regeneration, attacks or armor from wool. Culling AABB inflate3 is render-only.

### Deer heal

Deer mobInteract first calls Animal.mobInteract. Actual DEER_TEMPT_ITEMS includes wheat tag, apple and Shika Senbei. Adult age0 and canFallInLove or baby feeding calls virtual Deer.usePlayerItem: if exact Shika Senbei, server native heal(4), sound, then superclass consume1. Thus accepted breeding/growth can heal too. If superclass result exactly PASS, held Senbei and HP<max, fallback usePlayerItem heals/consumes even when breeding unavailable. No full-health-only fallback, but eligible breeding still consumes/heals at full health. Native heal first posts LivingHealEvent, rejects nonpositive result or HP<=0, then clamps new HP to max. Consumption does not depend on healing success; infinite materials retained. Player nutrition of same food is already R2f8r and is not duplicated.

### Bird descent

Bird.aiStep after Animal calls scales vertical velocity by.6 only when not onGround and Y<0; Penguin, Raven and TinyBird inherit. Flap fields/sounds are cosmetic. FlyingBird.tick after super multiplies Y by.6 whenever not landed, including upward motion; descending flying birds can encounter both factors in native tick sequence. No effect instance or direct HP write. Flight flags initially landed, age0, isBaby false; no custom save of landed/target/flight timer, so these reset on load. Variants separately persist.

### Bird flight

FlyingBird server AI: landed resets flightTime0. Takeoff on isSpooked OR inWater OR fluid below OR (randomInt200==0 AND below not landable). Raven spooked iff lastHurtByMob nonnull. TinyBird also spooked by nearest noncreative/nonspectator native query player within4 HOLDING tempt item (positive predicate, not negated); normal seeds tag. Flight increments timer; invalid nonair/minHeight target clears. Water/fluid below resets timer and Y=.1f. Retarget when null/random1in30/within2: X/Z current+randInt7-randInt7; Y+randInt6-(flightTime<100?2:4). Steering adds (signum(delta)*(.5,.7,.5)-velocity)*.1f with center offsets(.5,.1,.5); yaw follows motion, zza=.5. Random1in10 + landable below sets landed and Y0. Landable means nonair and leaves OR sturdy UP. No attack/teleport/owner control.

### Bird contacts

FlyingBird isPushable false, doPush and pushEntities empty, canRide false, isIgnoringBlockTriggers true. These govern its native push/riding and pressure/tripwire trigger predicates, not all hazards. Exact Entity.checkInsideBlocks still visits intersected live-entity blocks and invokes entityInside without this flag. Native BasePressurePlateBlock filters spectators and ignoring-trigger entities; TripWire checks flag. Incoming damage/projectiles and unrelated force movement retain native admission; no general invulnerability claimed.

### Passive immunity

Bundled minecraft:fall_damage_immune explicitly contains Squirrel, Penguin, Raven and TinyBird. Native LivingEntity.calculateFallDamage returns0 for this tag (after native causeFallDamage LivingFall hook); not universal source immunity. Penguin also in minecraft:freeze_immune_entity_types: Entity.canFreeze false, with LivingEntity wearable/spectator gates. This blocks native freezing eligibility, not all custom ice/cold hits or Frosted movement. No passive custom hurt override or new DamageType. Other passive types here are not added to either of these TF contributions; dynamic external tags remain conditional.

### Ordinary wildlife

All nine concrete passive classes dispositioned. Boar extends Animal, not Pig:10HP/.25 speed, standard breeding/tempt/panic, no inherited pig saddle/lightning conversion implied. Deer10/.2 and Senbei heal above. DwarfRabbit extends Animal, not Rabbit:3/.3/step1, ordinary breeding/avoidance, variant texture+biomes only, no killer-bunny behavior;95% parent variant when valid dwarf mate, otherwise random common. Squirrel6/.3/step1, tempt/avoid/panic but isFood false/offspring null. Penguin10/.2, native breeding plus Bird descent/immunities. Raven10/.2/step1 and TinyBird4/.2/step1 use flight above, no breeding. Bighorn extends Sheep and uses native Sheep8HP/.23 attributes, shear/eat/regrow/breed; TF overrides color/loot/sound/path preference, not a ram attack. Initial color brown with1/2 else uniform16; same-class breeding and native offspring color. Quest Ram separate above. None registers a melee/ranged attack goal in these bodies.

### Cosmetic exclusions

TinyBird/DwarfRabbit variant codecs carry texture and optional biome set; selection and NBT/sync do not grant status/attributes. Ordinary wildlife sounds, look/wander/tempt/avoid goals, leash offsets, color loot and texture renderers are source dispositions, not additional combat packages. Death loot is resource mapping; transformation pairs already protected R2f8s and are reused. Creature attributes are documented prerequisites, not nine duplicate attacks.

### Compatibility

GENERIC_CONDITIONAL_PRESENT: actual NeoForge interact-at, heal, fall, spawn, loot and resource-reload paths, with their native cancellations/modifications retained. No scoped direct external source-specific override proven (NONE_PROVEN); arbitrary external consumers/datapack changes UNKNOWN, not pack certification. Existing TF transformation and traveller hooks preserved. Remaining hazards/nine types, other structures/callbacks, nested ASM and global source/compatibility closure remain unfinished.

## Packages

| Mechanic | Primary classification |
|---|---|
| Quest Ram native quest resource and reward | CUSTOM_RESOURCE |
| Deer feeding native healing | VANILLA_LIKE_EXTENDED |
| Passive bird descent, flight and contact control | CUSTOM_CONTROL |
| Passive native fall and freezing eligibility | VANILLA_DIRECT |

## Custom source callers

| Type | Amount | Source identity |
|---|---|---|

## Scope and exclusions

- All nine concrete passive classes dispositioned. Boar extends Animal, not Pig:10HP/.25 speed, standard breeding/tempt/panic, no inherited pig saddle/lightning conversion implied. Deer10/.2 and Senbei heal above. DwarfRabbit extends Animal, not Rabbit:3/.3/step1, ordinary breeding/avoidance, variant texture+biomes only, no killer-bunny behavior;95% parent variant when valid dwarf mate, otherwise random common. Squirrel6/.3/step1, tempt/avoid/panic but isFood false/offspring null. Penguin10/.2, native breeding plus Bird descent/immunities. Raven10/.2/step1 and TinyBird4/.2/step1 use flight above, no breeding. Bighorn extends Sheep and uses native Sheep8HP/.23 attributes, shear/eat/regrow/breed; TF overrides color/loot/sound/path preference, not a ram attack. Initial color brown with1/2 else uniform16; same-class breeding and native offspring color. Quest Ram separate above. None registers a melee/ranged attack goal in these bodies.
- TinyBird/DwarfRabbit variant codecs carry texture and optional biome set; selection and NBT/sync do not grant status/attributes. Ordinary wildlife sounds, look/wander/tempt/avoid goals, leash offsets, color loot and texture renderers are source dispositions, not additional combat packages. Death loot is resource mapping; transformation pairs already protected R2f8s and are reused. Creature attributes are documented prerequisites, not nine duplicate attacks.
- No duplicate nutrition package, transformation package, home-navigation boss mechanic or ordinary physical attack. Passive type tags are actual defenses, not all-source immunity.
- Hazards/nine custom types, other structures/events, nested ASM and global compatibility/source coverage unfinished.

## Future native controls

- Quest native grove/egg,16 colors, hand/drop whole-stack differences, duplicate/config/reload and genuine loot/advancement/home.
- Deer adult/baby/PASS feeding with native heal and consumption hooks.
- Raven/TinyBird/Penguin descent/flight/trigger/hazard contrasts and persisted variants.
- Native fall and powder-snow tag controls versus custom damage/effects; ordinary wildlife exclusions.

[Semantic packages and paths](semantic-sections/twilightforest-passive-entities.json), [integrity](twilightforest-passive-entities-integrity.json), [full validation](r2f8v-passive-entities-validation.json).

Exact next task: Review remaining environmental hazards and nine custom DamageTypes (thorns, oreberry, knightmetal, fiery, fire_jet, reactor, slider, ominous_fire, acid_rain), their actual callers and other combat-significant structures/callbacks; finish nested ASM, compatibility and source exclusions. Protect R2f8, then final Twilight COMPLETE promotion, then IceAndFire. Static only.
