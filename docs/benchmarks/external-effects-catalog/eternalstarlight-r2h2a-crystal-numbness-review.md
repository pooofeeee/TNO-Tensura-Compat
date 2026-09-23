# R2h2a — Crystal Infection, Numbness and shared admission

R2h2a Crystal Infection, Numbness and shared cap/cure/admission complete; other R2h2 statuses pending.

Static subsection complete. Runtime fixtures remain unexecuted; no Stage or production implementation.

## Crystal tick

CrystalInfectionEffect requests ownerless eternal_starlight:crystal_infection HP damage = amplifier+1 every duration%35==0. Finite effects use remaining duration; infinite effects use recipient tickCount. applyEffectTick returns true regardless of hurt result; rejection does not remove the effect. The separate armor modifier is -1.5*(amplifier+1), ADD_VALUE with one stable armor.crystal_infection ID; native effect update/removal replaces/removes it. This armor penalty affects other armor-routed hits, not the infection source that bypasses armor. No direct HP/SHP subtraction, native magic classification or generic Tensura immunity is implied.

## Crystal melee

Player.attack calls CrystalGreatswordItem.getAttackDamageBonus before critical multiplication and native hurt. Bonus = existing amplifier * (amplifier>=4 ? .25 : .15) * current input attack damage; absent infection gives zero. At amplifier4 the bonus equals the input damage. Only a successful primary target hurt followed by item.hurtEnemy true (SwordItem returns true), server side/nonempty stack, calls postHurtEnemy. After ordinary durability cost: existing amplifier defaults0; if >=4 attempt removeEffect, otherwise addEffect duration60 amplifier=min(existing+1,4). Thus first application is amplifier1, not0; subsequent native merge/expiry rules apply. Removal failure is not repaired and addEffect failure only suppresses ordinary chime. No separate burst hurt exists in this callback; the particles are cosmetic. Sweep targets do not each execute this item callback. Mob-held delivery is not claimed from the Player-only chain.

## Crystal crossbow

CrystalCrossbowItem.createProjectile delegates to native CrossbowItem (arrow or firework), writes persistent ARROW_TYPE=eternal_starlight:crystal, and for AbstractArrow adds .25 base damage; shootProjectile then multiplies resulting velocity by1.35. Native ProjectileImpact event invokes ESCommonHandler on the server before normal impact HP handling, not after a successful hurt. Block impact clears the marker but continues this invocation. Five candidate positions within random offset4 are moved upward at most40 until air, then raycast down128 with COLLIDER/Fluid.NONE. A ground hit spawns one CrystalCluster; owner copied only if projectile owner is Living. Entity impact on Living separately adds infection200 amplifier0 if absent, otherwise min(old+1,4), ignoring addEffect return and without shouldHarm/LOS checks in that status branch. Entity impact does not clear the marker. Arrows/piercing and firework impacts are distinct future fixtures. Event cancellation before ES dispatch can suppress the helper; cancellation later does not undo already spawned clusters/status.

## Crystal cluster

CrystalCluster server tick resolves saved owner UUID in the same ServerLevel; if unresolved it clears that UUID. At spawnedTicks>=20 it discards, without returning; at >5 and nonnull Living owner it still visits Living entities in its AABB inflated.5. shouldHarm(owner,target) must pass, then hurt4 via crystal_infection direct=cluster/causing=owner must return true before infection120 amplifier0 is requested. There is no LOS predicate. The final discard tick can still execute this block. Repeated visits are subject to ordinary native damage cooldown; do not multiply damage by duration or entity count. Ownerless clusters never enter this damage branch. NBT saves owner UUID and spawned_ticks; cluster hurt itself only discards/returns true for BYPASSES_INVULNERABILITY, otherwise false (binary entity removal, no numeric HP).

## Crystal stew

ESBlocks registers Desert/Withered Desert Amethysia with infection4 seconds and Red/Blue Crystalfleur with10 seconds. DesertFlowerBlock delegates to FlowerBlock, whose SuspiciousStewEffects entry converts seconds to ticks; these are native suspicious-stew effect providers, not contact hazards. SuspiciousStewItem.finishUsingItem applies component entries through ordinary addEffect: amplifier0,80 or200 ticks. Acquisition/crafting and flower placement are excluded beyond identifying this real component route; no invented potion, splash or lingering recipe.

## Shared effect admission

All reviewed status producers use ordinary addEffect, not force-add/map insertion. Exact NeoForge LivingEntity.addEffect calls CommonHooks.canMobEffectBeApplied, then Added event and native update/hidden-effect merging. canBeAffected and external applicability hooks remain authoritative; successful hurt does not guarantee status admission. removeEffect and removeAllEffects pass removal hooks; expiration can be canceled. LivingEntityMixin.eat HEAD attempts to remove each non-beneficial effect for Lunaris Cactus Gel, with each removeEffect result ignored; it does not remove beneficial Numbness. Milk/cure behavior remains the native per-effect cure set and removal event, not an unconditional bypass. These custom statuses have no newly proven direct ES-specific Tensura/L2 hook; R2h1 scoped explicit-name scan is not a certification of generic runtime compatibility.

## Numbness admission

Silver Pungency Fruit native FoodProperties requests Numbness1200 amplifier0 with probability1 (and independent Nausea120 at.8). LivingEntity.eat/addEatEffect performs the server food-effect application through addEffect. LivingDamageEvent.Pre passes current damage to onModifyLivingActualHurtDamage AFTER armor, Resistance and enchantment reductions but BEFORE absorption for both LivingEntity and Player. If Numbness is active: debt += modified*.75, immediate damage = modified*.25. Amplifier has no role. This is deferred damage, not HP healing or a direct subtraction. Debt can be written even when subsequent absorption consumes all immediate damage.

## Numbness release

LivingEntityMixin injects AFTER updateGlowingStatus inside tickEffects. Exact21.1.244 host executes this only inside effectsDirty && !clientSide, not every entity tick. If Numbness absent and stored debt !=0: request ownerless eternal_starlight:numbness damage equal to the entire debt; then clear debt to0 regardless of hurt result. Ordinary expiration/removal marks effectsDirty, but canceled removal/expiry or a still-active hidden effect can prevent payout. An externally loaded nonzero debt with no dirty effect state has no unconditional per-tick drain. Native NUMBNESS_DAMAGE default0 is Codec.FLOAT serialized, not synced and not configured copyOnDeath. Direct archive field-access census finds only registration, Pre accumulation and this release; no ES retry or guaranteed eventual HP loss. Rejection can consume the debt without HP loss. Payout again passes ordinary armor/Resistance/enchantment/absorption and invulnerability, but its tag bypasses shields and Crescent Pendant; it is not an exact conservation of HP.

## Shared defenses

Crescent Pendant must occur in ACCESSORIES components of HEAD/CHEST/LEGS/FEET equipment (set union; duplicates do not stack), not merely inventory or weapon. In Pre, unless source has eternal_starlight:bypasses_crescent_pendant, amount>maxHP*.75 is capped to maxHP*.75 BEFORE Numbness split. Finally BYPASSES_INVULNERABILITY returns max(original Pre amount,modified), AFTER debt is stored: bypass can retain full immediate damage plus future debt. Preserve this native ordering, not an inferred immunity override. IncomingDamage veto: exact Unrealium Helmet plus minecraft:in_wall, or exact Unrealium Chestplate plus minecraft:cramming. These are exact type keys, no global suffocation/crushing tag immunity. Shared source/weapon multipliers in onModifyLivingHurtDamage remain later family review.

## Damage identity and mitigation

R2h1 tag closure (rawMC+NeoForge21.1.244+installedES) gives crystal_infection BYPASSES_ARMOR/BYPASSES_ENCHANTMENTS/BYPASSES_SHIELD, whereas numbness only BYPASSES_SHIELD plus BYPASSES_CRESCENT_PENDANT among those. Neither bypasses effects, Resistance, invulnerability or cooldown; neither is IS_MAGIC/IS_PROJECTILE/IS_FIRE/IS_FREEZING from these archives. Both DamageType exhaustion=.1, native scaling=when_caused_by_living_non_player. Infection DOT and Numbness have null direct/null causing; cluster preserves cluster/owner, so Player difficulty scaling may differ. Armor bypass does not imply Resistance bypass: the loader handles Resistance before enchantment bypass. Native death, totem, event cancellation and skill/L2 processing remain untouched and must be observed later.

## Single stage boundary

Independent numeric requests: scale infection DOT once at its native hurt amount; cluster once at native hurt4; ordinary Greatsword and Crossbow once at the final native primary/sweep/arrow/firework hurt amount after native weapon calculations. Do not additionally scale attack attributes, bonus fractions, base-damage increment, projectile velocity, stack amplifier, tick duration or cluster count. Numbness inherits the already-scaled parent damage; never multiply the debt or payout again. The native payout can apply mitigation a second time; do not compensate by bypassing defenses. Stage lineage handling is an explicit future implementation/test requirement, not a change made here. Fixed armor modifiers, cap percentage, deferral ratio and binary admission keep native values.

## Scope

Static semantic subsection only. Registry/decompiler aids checked against installed bytecode, exact loader and raw fallback routing. Other status/shared-handler branches and the remaining16 DamageType dispositions are unfinished; no full ES completion claim. Cosmetic chimes/particles, flower placement and ordinary acquisition omitted. All runtime fixtures remain unexecuted.

## TNO integration decisions

- **Crystal Infection periodic HP**: NUMERIC_SCALABLE, CUSTOM_ROUTED, ADMISSION_GATED. Stage: Once at CrystalInfectionEffect native hurt(amplifier+1).
- **Crystal Infection armor and native stack state**: COMPOSITE, VANILLA_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional multiplier; Keep native armor/amplifier/duration and ordinary effect admission.
- **Owned Crystal Cluster impact**: NUMERIC_SCALABLE, CUSTOM_ROUTED, ADMISSION_GATED. Stage: Once at CrystalCluster native hurt4.
- **Crystal weapon native primary damage**: NUMERIC_SCALABLE, VANILLA_ROUTED, ADMISSION_GATED. Stage: Once at each final native melee/sweep/arrow/firework hurt request after native weapon calculations.
- **Numbness deferred damage**: COMPOSITE, CUSTOM_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional multiplier; Parent damage is scaled once before deferral; debt/payout inherits it and must not scale again.
- **Crescent Pendant native damage cap**: COMPOSITE, CUSTOM_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional multiplier; Fraction of current maxHP; preserve source bypass and Numbness order.
- **Unrealium exact source veto**: BINARY, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional multiplier; Exact item/type cancellation.
- **Cactus Gel harmful-status removal**: BINARY, VANILLA_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional multiplier; Ordinary cancellable effect removal; no HP value.

[Machine-readable packages, delivery paths and future fixtures](eternalstarlight-r2h2a-crystal-numbness.json). Exact archive/method witnesses and targeted semantic assertions are reproducible. No whole-mod completion claim.

Exact next task: R2h2b: finish Eternal Starlight Starfire, Flammable/Brittle, Dream Catcher, Sticky, Teary and Oblivion status/control paths; reuse R2h2a effect/debt admission. Then remaining native combat families and all 18 DamageType caller dispositions; no runtime/Stage/production work.
