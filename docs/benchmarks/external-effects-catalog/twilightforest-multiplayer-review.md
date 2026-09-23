# r2f8ae - TWILIGHT_MULTIPLAYER_SEMANTIC_REVIEW_COMPLETE

DIRECT_SOURCE_SPECIFIC: TF tagged spawn modifier, serialized attribute ID and TF participation/loot/advancement consumers. GENERIC_CONDITIONAL_PRESENT: NeoForge spawn, incoming/pre/post/death events, native mutable attributes, tag reloads and native loot predicates. NONE_PROVEN: no direct Tensura/L2/Curios mapping in these paths. UNKNOWN: other runtime listeners, applied pack tags/attribute caps and actual compatibility outcomes; no pack-wide compatibility inferred. Future Stage must preserve upstream source eligibility, native post ordering and maximum/current-HP distinction.

Adds 1 reviewed packages / 3 delivery cases. Twilight remains PARTIAL at 271/999 drafts, zero promoted. REVIEW_REQUIRED 0.

## Native contracts

### Authority scope

Resumes b00c1f7 protected partial evidence without repeating boss reviews. Installed TF4.8.3345, exact NeoForge21.1.244 and raw Minecraft1.21.1 are authority. New owner scope admits combat-significant attributes; participation-driven loot and advancement are closed as acquisition/progression dispositions, not new combat packages. Historical drafts stay immutable until final deduplication/promotion. Static only; no runtime, L2, Stage, production or Phase6/7 work.

### Health admission

Registered EntityEvents.adjustEntityHealthInMultiplayerFights receives FinalizeSpawnEvent. Requires actual recipient type in twilightforest:multiplayer_inclusive_entities AND TFConfig.multiplayerFightAdjuster.adjustsHealth. Query ServerPlayer intersecting entity bounding box inflated32/10/32, using NO_CREATIVE_OR_SPECTATOR AND ENTITY_STILL_ALIVE. No line of sight, radial distance, party, target or prior-hit requirement. Count n>1 and nonnull MAX_HEALTH attribute admit permanent twilightforest:group_health_boost ADD_VALUE = coefficient*(n-1). Difficulty coefficient from event.getDifficulty().getDifficulty(): EASY20, NORMAL40, HARD60, default0. This is a snapshot at finalization, not live scaling as players enter/leave, and the callback does not require a particular spawn reason.

### Health configuration

Exact enum NONE(false,false), MORE_LOOT(true,false), MORE_HEALTH(false,true), MORE_LOOT_AND_HEALTH(true,true); argument order loot,health. Static/default and installed protected common-config snapshot are NONE; config declares worldRestart. Health and loot callbacks are therefore disabled by that snapshot, but native participation recording/advancement are not gated by it. Source/config comments describing a universal20-hearts increment or multiplayer_multiplier function are not authority: actual amount is difficulty-dependent health points and actual loot function ID is multiplayer_addition. No configuration changed.

### Health vs hp

Callback only adds MAX_HEALTH modifier: no heal, setHealth, setBaseValue or current-HP refill. Native attribute calculation sums ADD_VALUE before base/total multipliers and sanitizeValue; it is not necessarily an unbounded final HP increase by exactly the raw modifier. Native Living constructor initializes HP before spawn callback. Native onAttributeUpdated lowers HP only if current HP exceeds new maximum; raising maximum does not fill it. EventHooks.finalizeMobSpawn posts event BEFORE mob.finalizeSpawn, and cancellation skips that finalizer. setSpawnCancelled separately marks Mob and can prevent native addition. Other listeners may cancel/change difficulty; this callback has no internal cancellation test. No blanket claim a health-boosted boss spawns at its enlarged maximum.

### Native boss routes

Existing native base BossSpawner tick requires unspawned and qualifying nearby player; server non-Peaceful invokes spawnMyBoss. It creates/moves boss, posts finalize event, initializes restriction, then uses addFreshEntity return; successful result removes spawner and marks spawned. Lich override chooses position above ground before event, then cooldown40/extinguish/home and add. Native Lich finalizer delegates parent then equipment/sound, no HP refill; Minoshroom/Minotaur parent/equipment finalizers likewise have no refill. Reuses protected boss admission/defenses. Knight Phantom has its own six-entity spawner but is excluded by the installed multiplayer tag.

### Naga order

Naga uses native base spawner but its already-reviewed finalizeSpawn is materially distinct after the event: level difficulty !=EASY, MAX_HEALTH present and difficulty_health_boost absent => add permanent difficulty modifier (HARD130, otherwise80), then setHealth(getMaxHealth). Thus on a fresh native non-Easy Naga this later branch fills the maximum including the earlier multiplayer modifier. EASY or preexisting difficulty modifier does not enter that refill. Event difficulty used for group coefficient and level difficulty used here are separate values; external changes can make them differ. No repair or new heal is introduced.

### Health duplicate persistence

No hasModifier/remove/replace guard precedes addPermanentModifier. Native AttributeInstance.addModifier putIfAbsent throws IllegalArgumentException for duplicate same ID; repeated admitted finalization does not safely stack or refresh it. addPermanentModifier records modifier in permanent map; save/load serializes base plus permanent modifiers, Living saves attribute data and Health separately and loads attributes before setHealth. Modifier survives ordinary save/reload; there is no native removal or recalculation when nearby players leave or the config later disables adjustment. Runtime hook/tag outcomes remain future controls.

### Exact tag

Installed tag has exactly naga, lich, minoshroom, hydra, ur_ghast, alpha_yeti, snow_queen and plateau_boss in twilightforest namespace. Knight Phantom and Lich Minion are absent. Tag membership is eligibility, not proof all tagged entities have identical attack/finalization or actual worldgen availability. Real native base/Lich/Naga spawner routes are recorded, not a fabricated summon, tag edit or forced event.

### Participant admission

Registered LivingDamageEvent.Post callback first tests recipient multiplayer tag, then getData(MULTIPLAYER_FIGHT), creating empty data even if causing entity null. Nonnull event.source.getEntity goes to maybeAddQualifiedPlayer, which admits ServerPlayer and List.contains dedup. Native Entity.equals compares entity integer ID, not UUID; a replacement player entity is not UUID-deduplicated. No game-mode, alive, distance, config, positive original/final damage or last-hit requirement in this callback. Causing player on genuine owned projectile can qualify; direct projectile alone, ownerless source, ordinary Mob or tame pet causing entity does not. No tame-owner/kill-credit traversal or source rewriting.

### Post order

Exact Living.hurt native invulnerability/client/dead/fire-resistance/incoming-veto/cooldown gates precede actuallyHurt; boss-specific admission remains upstream. Native actuallyHurt invulnerability gate then armor/magic/pre-damage/absorption processing, optional nonzero HP subtraction and damage callbacks, THEN CommonHooks.onLivingDamagePost. Post is emitted outside the nonzero-HP branch and snapshots original/new damage and source. Zero final HP loss can therefore qualify, including native fully absorbed hits, while earlier rejection does not reach Post. A shield path may reach Post and ultimately return false; hurt return is not the participation predicate. Killing-blow Post precedes ordinary death processing. No bypass of armor, Resistance, eligibility or source identity.

### Participant death persistence

MULTIPLAYER_FIGHT builder has no serializer, sync or copyOnDeath; qualifiedPlayers is an in-memory List<ServerPlayer>, exposed as unmodifiable view. It does not persist across normal entity reload. Permanent health modifier and transient participants are distinct. Native CommonHooks.onLivingDeath posts cancellable death event; TF listener requires event not canceled and hasData, without rechecking recipient tag/config. grantGroupAdvancement iterates recorded players without clearing list or rechecking range/alive/connection. A later listener cancellation can occur after this listener; no unconditional final death or award guarantee is asserted.

### Loot consumers disposition

Acquisition disposition, no separate combat package. Actual registered multiplayer_rolls provider requires loot flag, THIS_ENTITY and existing attachment, otherwise samples defaultRolls. With q participants: defaultFloat + sum of max(0,perPlayerFloat) sampled independently max(q-1,0) times. Native NumberProvider.getInt uses Math.round on the resulting total when LootPool consumes it; native pool conditions and bonus rolls still apply. multiplayer_addition conditional function requires same config/context/data and q>1, samples value.getInt ONCE, multiplies by(q-1), adds existing stack count and clamps0..stack max. Extra amount is not clamped nonnegative; ordinary signed integer arithmetic is retained. It does not recheck tag itself. Actual JSON pointer routing pins all consumer parameters, conditions and pool order.

### Loot material distinctions

Actual Minoshroom axe addition Uniform[-2,1] uses native UniformGenerator.getInt -> Mth.nextInt inclusive bounds. Negative draws can reduce or remove a stack; do not call it guaranteed extra loot. Lich/SnowQueen extra-roll Uniform[-2,1] uses getFloat then max0 per extra player, a different rule. Knight Phantom JSON uses multiplayer_rolls inside looting_rolls then binomial .17; LootingEnchantNumberProvider adds actual ATTACKING_ENTITY Living enchantment level to base, native binomial uses integer n and random trials. Knight is absent from tag, and whole installed-class census finds native participant creation only in tagged damage callback, so ordinary Knight path has no participant attachment and uses default multiplayer rolls. No synthetic attachment path is offered as native. Acquisition/resource parameters are evidence, not combat mechanics.

### Advancement disposition

Progression disposition, no new combat package. HurtBossTrigger constructs boss entity context, native SimpleCriterionTrigger checks existing listeners, hurt-entity predicate and optional player predicate, then awards qualifying criterion. Six native hurt_boss resources: progress_naga, progress_lich, progress_hydra, progress_ur_ghast, progress_yeti, progress_glacier. was_in_fight is an alternative within their existing kill/item group; additional previous-progression requirement groups remain. Minoshroom/Knight have no such hurt_boss resource in installed census. Triggering does not unconditionally grant full advancement, bypass progression or damage an entity.

### Compatibility

DIRECT_SOURCE_SPECIFIC: TF tagged spawn modifier, serialized attribute ID and TF participation/loot/advancement consumers. GENERIC_CONDITIONAL_PRESENT: NeoForge spawn, incoming/pre/post/death events, native mutable attributes, tag reloads and native loot predicates. NONE_PROVEN: no direct Tensura/L2/Curios mapping in these paths. UNKNOWN: other runtime listeners, applied pack tags/attribute caps and actual compatibility outcomes; no pack-wide compatibility inferred. Future Stage must preserve upstream source eligibility, native post ordering and maximum/current-HP distinction.

## Packages

| Mechanic | Primary classification |
|---|---|
| Multiplayer native spawn maximum-health adjustment | VANILLA_LIKE_EXTENDED |

## Custom source callers

| Type | Amount | Source identity |
|---|---|---|

## Scope and exclusions

- Acquisition disposition, no separate combat package. Actual registered multiplayer_rolls provider requires loot flag, THIS_ENTITY and existing attachment, otherwise samples defaultRolls. With q participants: defaultFloat + sum of max(0,perPlayerFloat) sampled independently max(q-1,0) times. Native NumberProvider.getInt uses Math.round on the resulting total when LootPool consumes it; native pool conditions and bonus rolls still apply. multiplayer_addition conditional function requires same config/context/data and q>1, samples value.getInt ONCE, multiplies by(q-1), adds existing stack count and clamps0..stack max. Extra amount is not clamped nonnegative; ordinary signed integer arithmetic is retained. It does not recheck tag itself. Actual JSON pointer routing pins all consumer parameters, conditions and pool order.
- Actual Minoshroom axe addition Uniform[-2,1] uses native UniformGenerator.getInt -> Mth.nextInt inclusive bounds. Negative draws can reduce or remove a stack; do not call it guaranteed extra loot. Lich/SnowQueen extra-roll Uniform[-2,1] uses getFloat then max0 per extra player, a different rule. Knight Phantom JSON uses multiplayer_rolls inside looting_rolls then binomial .17; LootingEnchantNumberProvider adds actual ATTACKING_ENTITY Living enchantment level to base, native binomial uses integer n and random trials. Knight is absent from tag, and whole installed-class census finds native participant creation only in tagged damage callback, so ordinary Knight path has no participant attachment and uses default multiplayer rolls. No synthetic attachment path is offered as native. Acquisition/resource parameters are evidence, not combat mechanics.
- Progression disposition, no new combat package. HurtBossTrigger constructs boss entity context, native SimpleCriterionTrigger checks existing listeners, hurt-entity predicate and optional player predicate, then awards qualifying criterion. Six native hurt_boss resources: progress_naga, progress_lich, progress_hydra, progress_ur_ghast, progress_yeti, progress_glacier. was_in_fight is an alternative within their existing kill/item group; additional previous-progression requirement groups remain. Minoshroom/Knight have no such hurt_boss resource in installed census. Triggering does not unconditionally grant full advancement, bypass progression or damage an entity.
- Participant list is native combat attribution for acquisition/progression, not an independently consumed combat resource; source/admission/persistence recorded, no extra package.
- Remaining ordinary utility/storage/maps/crafting/progression/worldgen without combat callback/rendering receives concise disposition under new owner scope. Historical protected sections are not redone.

## Future native controls

- Native eligible player-count/config/difficulty/tag health admission, before/after finalization HP and attribute comparison, duplicate ID and save/reload.
- Actual causing-player vs direct-projectile/ownerless/pet source, upstream damage rejection vs absorbed zero-HP Post and killing-blow ordering; no forced events.
- Native participant identity/reload, death cancellation/criterion predicates, exact real loot-provider resources and config modes, only if later runtime approval is given.

[Semantic packages and paths](semantic-sections/twilightforest-multiplayer.json), [integrity](twilightforest-multiplayer-integrity.json), [full validation](r2f8ae-multiplayer-validation.json).

Exact next task: Finish only remaining combat-significant EntityEvents, Lich/worldgen traps or spawners, nested ASM and compatibility/source closure. Briefly disposition utility/acquisition/progression/rendering without deep new subsections. Protect R2f8 remaining-content closure, then deduplicate/promote Twilight COMPLETE before IceAndFireCE beta15. Continue while execution/quota can safely protect work; no arbitrary percentage stop.
