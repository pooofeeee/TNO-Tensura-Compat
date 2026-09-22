# r2f8e - TWILIGHT_ARTHROPODS_SEMANTIC_REVIEW_COMPLETE

Installed Twilight4.8.3345 with raw Minecraft1.21.1 and exact NeoForge21.1.244. These melee paths use native minecraft:mob_attack, direct=causing actual attacking mob, effective ATTACK_DAMAGE plus ordinary native enchantment processing; no custom DamageSource or armor/shield/Resistance/protection/cooldown bypass. Native causingLiving difficulty scaling applies to Player victims. Native hurt true is admission, not a measured HP loss. Hunger is a vanilla MobEffect/resource operation, not another damage event; any later starvation is separate ownerless minecraft:starve, not attributed to the mosquito. Static source evidence only; no runtime, L2, SHP, Stage or production claim.

Adds 7 reviewed packages / 24 delivery cases. Twilight remains PARTIAL at 99/277 drafts, zero promoted. REVIEW_REQUIRED 0.

## Native contracts

### Pipeline

Installed Twilight4.8.3345 with raw Minecraft1.21.1 and exact NeoForge21.1.244. These melee paths use native minecraft:mob_attack, direct=causing actual attacking mob, effective ATTACK_DAMAGE plus ordinary native enchantment processing; no custom DamageSource or armor/shield/Resistance/protection/cooldown bypass. Native causingLiving difficulty scaling applies to Player victims. Native hurt true is admission, not a measured HP loss. Hunger is a vanilla MobEffect/resource operation, not another damage event; any later starvation is separate ownerless minecraft:starve, not attributed to the mosquito. Static source evidence only; no runtime, L2, SHP, Stage or production claim.

### Spider inheritance

All four TF Spider descendants retain native Float, Armadillo avoidance (range6, speeds1/1.2, only not-scared Armadillo), leap .4, retaliation and IronGolem targeting. Spider uses WallClimberNavigation and sets a climbing flag from horizontalCollision; exact cobweb makeStuckInBlock skips the ordinary slowdown. Exact Poison is rejected before superclass canBeAffected, including in the installed244 authority (Spider class has no244 replacement). No outgoing poison payload is added. Ordinary native effects, equipment, mitigation and health persistence remain. TF adds Hedge/King/Swarm/Broodling, HelmetCrab and Borer to minecraft:arthropod, affecting tag-based native Bane of Arthropods rather than granting Poison immunity to non-Spider classes. MosquitoSwarm is not in this scoped TF arthropod contribution. No new shield, boss phase or death attack in these bodies.

### Spider finalize

Spider.finalizeSpawn calls super then rolls nextInt(100)==0 for a vanilla Skeleton, directly finalizes it with the caller spawn reason and starts it riding the spider. Passenger creation has no explicit addFreshEntity here; ordinary native passenger-tree insertion is required. With null group data create SpiderEffectsGroupData; on Hard, randomFloat < .1*localDifficulty.specialMultiplier selects one infinite amplifier0 effect: nextInt(5) 0/1 Speed,2 Strength,3 Regeneration,4 Invisibility. Existing group data can share the selected effect. Ordinary native MobEffect attribute/heal/visibility behavior and save/load apply, not a custom resource or fixed unmodified melee amount. TF subclass finalize runs after this native setup; source fixtures must retain genuine finalization and passenger state.

### Hedge

HedgeSpider uses native Spider HP16/speed.3/baseattack2. Its registerGoals removes all MeleeAttackGoal instances and installs ordinary MeleeAttackGoal(priority4,speed1,longMemorytrue); replaces only priority2 NearestAttackableTargetGoal with ordinary visible Player targeting. Thus removes SpiderAttackGoal vehicle-start veto and brightness-based random continuation stop, and removes Player darkness targeting gate. Inherited IronGolem targeting still needs brightness<.5; retaliation/Armadillo avoidance/native target eligibility remain. onClimbable remains inherited. Spawn placement uses HedgeSpider.canSpawn: nonPeaceful and either current chunk landmark HEDGE_MAZE or ordinary dark-enough test; this method itself lacks SwarmSpider extra checkMobSpawnRules. Native spawn engine/placement/event checks remain; no assertion of universal aggression or unconditional spawning.

### King

KingSpider HP30/speed.35/attack6, registered1.6x1.6, inherits Spider goals unchanged but onClimbable always false. Native SpiderAttackGoal.canUse requires super.canUse AND !isVehicle; therefore a freshly finalized ridden King cannot start its normal melee goal. Vehicle check is not repeated in canContinueToUse, so it is a start gate, not universal damage immunity or an override of doHurtTarget. Unridden admitted melee uses native mob_attack effective6. Player/IronGolem target acquisition requires brightness<.5; active SpiderAttackGoal can stop at brightness>=.5 with nextInt(100)==0. King finalize calls super, then creates adult SkeletonDruid, directly finalizes JOCKEY, walks first-passenger chain and starts the Druid riding the last rider. It does not eject passengers: the native1% Skeleton case can form King -> Skeleton -> Druid. Each entity retains separate HP/source/AI; no shared master or health pool. Druid equipment/NatureBolt payload is reused from protected ranged section. Attachment height .85*King height is geometry only.

### Swarm

SwarmSpider HP3/speed.3/attack1, clustermax6; TowerBroodling inherits Swarm with HP7/attack4, speed.3. Both share Hedge-style ordinary melee and brightness-independent visible Player acquisition, climbing/web/Poison inheritance. Swarm.doHurtTarget first rolls nextInt(4)==0, otherwise returns false without invoking superclass damage. Native AI attempt cooldown can still reset on the failed attempt; probability is per callback, not final HP success. Tower inherits this exact gate. getReinforcementType returns their own EntityTypes, but an all-TF-class instruction scan proves zero call sites for that method: no native reinforcement producer is established by the method name or spawn cluster6. Swarm native spawn placement uses nonPeaceful && (HedgeMaze landmark OR dark) && checkMobSpawnRules; registered TowerBroodling placement instead explicitly uses Monster.checkMonsterSpawnRules. They are not equivalent static-spawn paths.

### Swarm jockey

Protected R2f8a Swarm finalize/jockey contract is reused: superclass Spider setup first, then existing first passenger OR nextInt(200)==0 causes baby SkeletonDruid creation, setBaby(true), EventHooks.finalizeMobSpawn(JOCKEY), eject prior passengers if any, and startRiding spider. This can replace the superclass Skeleton, not stack on it. TowerBroodling overrides summonJockey with an empty method, suppressing this TF baby replacement only; Spider.finalizeSpawn still runs and can create its native Skeleton. Ordinary melee replacement has no Spider vehicle-start veto for either species. This extends producer coverage without duplicating protected Druid permanent-baby or NatureBolt packages.

### Mosquito

MosquitoSwarm Monster HP12/speed.23/attack3/stepheight2.1, registered.7x1.9. Ground navigation with Float0/Melee3 speed1 longMemoryfalse/stroll6, retaliation and visible Player targeting; no flying navigation inferred from appearance. doHurtTarget first calls super; only true and LivingEntity applies vanilla Hunger amplifier0: Easy140ticks, Hard600, default300 (including code default Peaceful, whose ordinary Player hurt admission normally prevents it). addEffect has no explicit attacker and retains native eligibility, merging, removals and ticking. False hurt adds no Hunger. Non-Player Living can receive Hunger but its native tick only changes Player exhaustion. displayFireAnimation false is cosmetic, not fire immunity; registration is not fireproof. TF entity tags grant fall_damage_immune and powder_snow_walkable_mobs. canRide false and clustermax1. No poison, custom source, healing or summon.

### Hunger

Native HungerMobEffect applies every effect tick: Player.causeFoodExhaustion(.005*(amplifier+1)); Player requires !abilities.invulnerable and server. FoodData caps exhaustion at40; tick consumes4 only when exhaustion>4, then removes up to1 saturation, else1 food when difficulty is not Peaceful. Thus nominal new amp0 exhaustion is .7/1.5/3 across uninterrupted140/300/600ticks before other food operations; no fixed immediate food/HP subtraction. Ordinary natural regeneration can heal and consume exhaustion (food20 with saturation: every10ticks heal min(saturation,6)/6; food>=18: every80ticks heal1, exhaust6). With food<=0 the native counter at80ticks requests ownerless starve1 if HP>10 OR Hard OR (HP>1 AND Normal), ignores hurt return then resets counter. Native source mitigation/event admission still applies; no mosquito owner propagated and no guaranteed death or HP loss. Effects/resource counters retain ordinary native persistence.

### Crab exclusion

HelmetCrab fully reviewed: Monster HP13/speed.28/attack3/armor6, registered.8x1.1/eye.45. Float0, custom AlwaysWatchTargetGoal1, ordinary LeapAtTargetGoal2(.28), Melee3 and stroll/look; retaliation and visible Player targeting. AlwaysWatch has no conflict flags, requires every tick, canUse target!=null and inherited continuation repeats canUse; lookControl.setLookAt(target,100,100), no damage/target eligibility override. Leap/control and armor6 are ordinary vanilla primitives; no shell HP, directional shield, reflect, armor break or special payload. Synced BLUE=false, finalize nextInt(10000)==0, saved blue; rendering/helmet angle only, no combat modifier. Therefore ordinary melee/armor/leap/watch and blue variant are documented exclusions rather than inflated unique effect packages. Borer/Crab do not inherit Spider Poison immunity.

### Borer body

TowerwoodBorer Monster HP15/speed.27/attack5/follow8, registered.4x.3. Ordinary melee4/Float1/ClimbOnTopPowderSnow1, visible Player acquisition and HurtByTargetGoal.setAlertOthers; shared retaliation is ordinary native AI, separate from releasing infested blocks. Movement emission EVENTS and isSteppingCarefully false; not silent/no-sensor immunity. TF adds powder_snow_walkable_mobs, arthropod and immune_to_infested; native LivingEntity rejects INFESTED MobEffect for the last tag, not Poison generally. No custom damage source or death attack, ownership link, saved reinforcement counter, boss state or spawn HP copied from another borer.

### Borer notify

TowerwoodBorer.hurt ordering: isInvulnerableTo(source) false-return first; then if (source.getEntity()!=null OR source.is(ALWAYS_TRIGGERS_SILVERFISH)) && summonBorers!=null, notifyHurt(); finally super.hurt(source,amount). Causing entity, not merely direct entity, admits the first predicate. No positive-amount or final-hurt-success requirement before scheduling; later shield/cooldown/event rejection can leave the timer armed. Raw tag contains minecraft:magic; exact244 adds #neoforge:is_poison containing neoforge:poison plus optional #forge:is_poison. This source-tag route admits ownerless magic/poison; arbitrary ownerless physical damage is not equivalent. Runtime third-party datapack contributions are outside the scoped native tag proof. notify sets20 only at0, does not refresh an active positive counter. Goal has no flags and no requiresUpdateEveryTick override:20 goal tick callbacks, not a promise of20 world ticks; ordinary Mob goal cadence applies.

### Borer release

SummonBorersGoal tick decrements counter; at<=0 scans offsets in order y=0,1,-1,...5,-5 outer, x=0,1,-1,...10,-10 middle, z similarly inner (21*11*21=4851 candidate positions). For each exact INFESTED_TOWERWOOD, canEntityGrief true calls world.destroyBlock(pos,true), ignores return, emits BLOCK_DESTROY; false replaces with ordinary TOWERWOOD flags3, no drop callback or released borer. After each matching block, nextBoolean true exits the entire scan regardless mutation success; otherwise continues. No LOS, hurt success, owner, Player or HP test in scan. Successful drop-bearing destruction can reach InfestedTowerwoodBlock.spawnAfterBreak and produce a fresh borer under its separate gates. No direct spawn call in the goal, no guaranteed count, and repeated hurt while timerpositive does not reset it.

### Borer hide

HideInTowerwoodGoal extends RandomStroll speed1/interval10, MOVE flag. canUse requires no target and finished navigation; nextInt(10)==0 && canEntityGrief then chooses one of six Directions, examines floor(x,y+.5,z)+direction for exact TOWERWOOD. A match sets doMerge true; otherwise clears it and uses normal stroll. start recomputes neighbor, requires still exact TOWERWOOD and nextInt(5)==0, then setBlock INFESTED_TOWERWOOD flags3, spawnAnim, discard self. SetBlock return is ignored; failed placement can still discard the entity. doMerge prevents continuation. Chance is conditional on native AI evaluation, chosen direction, griefing and terrain, not an unconditional1/50 world-tick rate. Block stores no entity HP/effects/UUID; a later released borer is newly created, not healing or restoring this one. No native hurt/death/source for hide-discard.

### Infested block

InfestedTowerwoodBlock extends ordinary Block, overriding spawnAfterBreak only. Calls super, then server && doBlockDrops && !EnchantmentHelper.hasTag(tool,PREVENTS_INFESTED_SPAWNS) creates fresh TowerwoodBorer at(x+.5,y,z+.5), addFreshEntity, spawnAnim. No finalizeMobSpawn, owner/master, stored HP, spawn chance, Player-only or internal mobGriefing predicate; boolean sourceIsPlayer is unused. Native prevents_infested_spawns contains Silk Touch, no additional244 contribution. Player harvest/dropResources and Borer destroyBlock(true) reach exact244 CommonHooks.handleBlockDrops: post BlockDropsEvent, only notCanceled spawns event drops then state.spawnAfterBreak(...,tool,false); its false boolean does not prevent the TF release. Replacement/setBlock and destroyBlock(false) do not reach this callback; ordinary creative destruction also skips harvest drops. Late drop-event cancellation suppresses release; tool or doBlockDrops gate suppresses it independently.

### Infested explosion

Legitimate native destructive explosion follows exact244 BlockBehaviour.onExplosionHit: nonair && interaction!=TRIGGER_BLOCK, then canDropFromExplosion && ServerLevel -> spawnAfterBreak(EMPTY,indirectSource instanceof Player) before getDrops/onBlockExploded. InfestedTowerwood ignores that Player boolean; with doBlockDrops true, empty tool cannot carry Silk Touch, so admitted explosion block processing can release a fresh borer independently of entity-damage hurt returns or explosion loot decay. Native explosion block selection/events/griefing/drop-from-explosion conditions remain. This is a separate callback path from CommonHooks.handleBlockDrops and its BlockDropsEvent gate; no assumption that cancellation of unrelated entity HP damage prevents block spawn. No guaranteed release from a non-destructive/TRIGGER_BLOCK/unselected/protected block.

## Packages

| Mechanic | Primary classification |
|---|---|
| Hedge and swarm spider native AI/defense inheritance | VANILLA_LIKE_EXTENDED |
| King Spider rider composition and melee start gate | CUSTOM_CONTROL |
| Swarm and Tower Broodling probabilistic melee admission | VANILLA_LIKE_EXTENDED |
| Mosquito melee and native Hunger resource effect | VANILLA_COMPOSITE |
| Borer pre-admission reinforcement timer and block scan | CUSTOM_CONTROL |
| Borer conditional towerwood infestation and discard | CUSTOM_CONTROL |
| Infested towerwood native drop and explosion release | CUSTOM_CONTROL |

## Custom source callers

| Type | Amount | Source identity |
|---|---|---|

## Scope and exclusions

- All12 declared native class surfaces pinned; prior Swarm finalize/jockey witnesses reused rather than overwritten. Native registration/attributes/spawn methods reused.
- HelmetCrab native armor/melee/leap/watch and blue variant are fully assessed exclusions, not a custom shield or inflated unique effect.
- No native getReinforcementType caller exists in the installed TF class instruction census; cluster cap is not a spawn-on-hit mechanic.
- Protected Druid baby/NatureBolt packages are linked, not duplicated. Native Skeleton ordinary arrow payload and native Spider random buffs remain vanilla primitives.
- No new custom DamageType is introduced by this subsection: reviewed custom census remains25/40,15 unfinished.
- All other Twilight areas remain unfinished; zero final promotion and no IceAndFire until whole-Twilight completion.

## Future native controls

- Spiders: native brightness/vehicle/Poison/web/Armadillo controls, Hard group effects and distinct King/Swarm/Tower passenger producers.
- Swarm/Tower: callback probability vs native AI cooldown/hurt admission, native spawn placement differences and no phantom reinforcement path.
- Mosquito: genuine melee followed by Hunger, difficulty/eligibility/merge/removal, Player exhaustion/food/saturation/regen and separately sourced starvation.
- Crab: ordinary armor6/melee3/leap/watch and blue cosmetic negative controls only.
- Borer: early invulnerability vs late false hurt, causer vs ownerless damage tag, goal-cadence timer, spatial scan/random stop, griefing and drop callbacks.
- Infested towerwood: Player harvest, native reinforcement destruction and destructive explosion; Silk/BlockDropsEvent/doBlockDrops/no-drop/creative/replacement controls.

[Semantic packages and paths](semantic-sections/twilightforest-arthropods.json), [integrity](twilightforest-arthropods-integrity.json), [full validation](r2f8e-arthropods-validation.json).

Exact next task: Continue Task C with remaining melee/control mobs: Boggard, Redcap/Sapper, Kobold/Troll, CarminiteGolem, Adherent/HarbingerCube, MazeSlime, SnowGuardian, RisingZombie/LoyalZombie and unfinished Wraith/Minotaur bodies; then remaining items/scepters/armor/charms/projectiles/hazards/resources and15 custom caller profiles. Reuse protected arthropods and earlier subsections. Protect each logical subsection toward R2f8 and final Twilight promotion; IceAndFire only after COMPLETE Twilight is pushed. No runtime boss/L2/Stage/production/fixes/Phase6/7.
