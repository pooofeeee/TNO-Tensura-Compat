# R2g9a — Remaining special weapons

Remaining HP-special weapons reviewed; chain/control/Pixie and final mod closure pending.

Static subsection complete. Runtime fixtures unexecuted; no Stage or production implementation.

## Post hit entry

Five ActivePostHit tool wrappers (sword/axe/pickaxe/shovel/hoe) call ability.active only if ability.isEnable, then parent hurtEnemy. Legitimate Player.attack reaches ItemStack.hurtEnemy only after primary hurt succeeds; exact installed Player resets attack strength AFTER this callback. Ordinary Mob.doHurtTarget does not automatically invoke these item methods. Frozen R2g2a already proves that admission and its Ice payload; reuse it, do not reopen it. One primary melee Stage point at final original hurt; independent secondary native requests each scale once at their own final hurt, without multiplying a shared attribute twice.

## Bonus

Registered Silver five tools use DamageBonusAbility2 against UNDEAD. Fire Blood Sword uses bonus8 against FIRE_DRAGON (same tag as accepted Ice Blood bonus, not opposite inferred element). Lightning Blood Sword requests4 against FIRE_DRAGON then4 against ICE_DRAGON; a type in both tags receives two requests. Player must have exact getAttackStrengthScale(0)==1, then victim tag; nonPlayer helper has no strength gate, but native entry must exist. Source iceandfire:bonus has direct=causing=attacker and only scoped bypasses_cooldown tag from the installed census. Normal hurt still processes armor/resistances/etc; return is ignored. Fire/Lightning outer wrapper disabled by corresponding config suppresses all their payload including bonus. Do not fabricate damage if tags/gates reject.

## Fire payload

Enabled Fire Blood Sword ignites for captured constructor config5 seconds then normal knockback1; Dragonsteel Fire five tools ignite15 seconds then knockback1, no bonus. Config snapshot has dragonFireAbility=true; duration captured when ability instantiated, enable read live. Ignite and knockback independent of secondary bonus hurt result, but dependent on admitted primary item callback. Native ignite, fire immunity/extinguish and subsequent on_fire processing remain; scale once at native periodic fire damage if Stage applies, not duration and tick damage both. Knockback retains native resistance/event admission; no Stage on vector.

## Summoned lightning

Enabled Lightning Blood Sword first performs tagged bonuses, then SummonLightningAbility; Player attackAnim>0.2 rejects lightning only. Server creates real LightningBolt at target, adds string tags iceandfire.bolt_skip_loot and attacker UUID, adds entity; no setCause and no visualOnly. Whole Iaf bytecode finds no loot-tag consumer beyond writer/declaration; tags do not prove loot protection, allegiance or DamageSource owner. Exact vanilla/NeoForge bolt tick when life>=0 and !visualOnly visits living/alive entities in x/z+-3,y-3..+9, without attacker/team/LOS filter, checks onEntityStruckByLightning cancellation, then thunderHit. Default damage5 via cached ownerless minecraft:lightning_bolt, not iceandfire:dragon_lightning; Entity.thunderHit changes fire timer before hurt. Native flashes can revisit recipients; hitEntities is not an immunity filter for this damage loop. Native fire spawning obeys its difficulty/fireTick conditions. Scale only final thunderHit hurt amount, never both bolt damage and event. Converted mob-specific thunderHit behavior remains native.

## Lightning chain

Dragonsteel Lightning five tools use LightningMultihitAbility, not LightningBolt. Requires dragonLightningAbility, ServerLevel and initial target instanceof Mob; no Player victims in chain search. Seed damage=EnchantmentHelper.modifyDamage(stack,initialTarget,mob_attack(attacker),1), NOT attacker ATTACK_DAMAGE or initial hit amount. Initial target gets no extra chain HP request. Each queued noninitial Mob gets mob_attack direct=causing=attacker at propagated float damage; normal hurt return does not stop queue expansion. Search always centered on attacker with configured cube range10 and attacker LOS, not previous hop; no ally/pet/self/Enemy filter. Only already processed mobs excluded, queued mobs can be enqueued again. Counter cap10 includes processed+queued; each enqueue multiplies parent damage by snapshot reduction.5. Duplicates/rejected hits still consume traversal budget. Lightning packet is cosmetic. Scale once each final chain hurt, never propagate Stage-scaled amounts through queue or scale range/count.

## Hippogryph sweep

HippogryphSword accepted primary item callback adds a sweep for Player: target box inflate(1,.25,1), excludes attacker/primary/allied, attacker distanceSquared<9; no new LOS or charged/grounded/sprinting requirement. Each secondary gets knockback.4 BEFORE player_attack damage 1+(1-1/(SweepingEdgeLevel+1))*attackerATTACK_DAMAGE. This may coexist with normal vanilla Sword sweep during the original attack. Secondary hurt does not recursively call item.hurtEnemy. Preserve both native paths and hurt-independent knockback; scale final request once.

## Slapper

HippocampusSlapper accepted item callback independently requests Slowness100ticks amp2 and Nausea100ticks amp2, with normal effect admission; return values ignored. No extra HP damage. Native status duration/strength and immunity remain, no extra Stage value. Ordinary sword HP damage is already a primary melee path.

## Gauntlet

DeathwormGauntlet use starts10-tick use; releasing early only clears USER_ID. finishUsingItem for Player scans LivingEntity in centered+-5 cube excluding self; cone dot(view,normalized delta)>1-.5/distance and player.hasLineOfSight required, not a spherical5-radius test. All admitted recipients get player_attack3 direct=causing=Player, then knockback.5 with target-minus-attacker horizontal arguments, pulling toward Player under native knockback formula, independent of hurt success. No team/creative filter before native hurt; no explicit server guard in finish method, so preserve actual caller sidedness. Cooldown20, no explicit item durability charge/consumption in this class. LungeTicks/USER_ID are animation state, not a damage scalar. Scale only each native hurt3.

## Dragon bow arrow

DragonBow accepts DRAGON_ARROWS tag or ordinary arrows, native ammo/creative/Infinity; charge getPowerForTime>=.1, speed3*power, full power critical; manual Power adds .5*level+.5 baseDamage and Flame ignites projectile100seconds. It calls chosen ArrowItem.createArrow with weapon stack directly (no extra generic ProjectileWeaponItem factory wrapper), preserving that constructor enchantment behavior. Infinity waives ammo for any supported projectile here. DragonArrow baseDamage10, inherited arrow source direct=arrow/causer=owner, final speed/crit/native damage; unlike other reviewed custom ammo it overrides asProjectile, so registered dispenser really creates ownerless DragonArrow. addAdditionalSaveData overwrites saved damage with10; reloaded arrow loses added baseDamage. Stage only at final arrow hurt, not baseDamage/bow power too. Weapon/dispenser/reload are distinct fixtures.

## Tide delivery

TideTrident inherits TridentItem.use admission (durability and native spin/water gate), custom release requires Player, charge>=10, actual RIPTIDE level<=0 or water/rain. Server durability1; noRiptide constructs positioned owned TideTrident using original stack, speed2.5, removes inventory stack noncreative; native Loyalty and Piercing levels captured. IafRecipes does not register a Tide dispenser behavior; inherited asProjectile would create vanilla ThrownTrident if externally invoked, but no native dispenser attack claimed. Riptide instead pushes Player and startAutoSpinAttack20 with damage8 and same stack, grounded upward movement. Native collision calls Player.attack on first Living contact, using spin damage8 and native enchantments/admission, then stops/reverses motion. This is player_attack, not thrown trident12.

## Tide hit

TideTrident.onHitEntity requests minecraft:trident direct=projectile, causing=owner or projectile if ownerless, base12 modified by native item enchantments for Living victim on ServerLevel. entitiesHit increments BEFORE hurt; at>=2+getPierceLevel sets dealtDamage. Rejected hurt therefore consumes budget. Accepted Enderman returns early; other accepted Living targets get post-attack enchantments with item source and post-hurt callback. Custom override does not call superclass hit, does not add victim to arrow piercingIgnoreEntityIds, does not perform vanilla trident velocity reversal/knockback. Inherited ThrownTrident.findHitEntity stops only once dealtDamage; default level0 can revisit same target on subsequent tick, positive legitimate Piercing can repeat same target within parent arrow loop until count limit. Count is attempts, not distinct victims. entitiesHit itself is not saved; inherited dealtDamage is. Check naturally available enchantments first, never force unsupported Piercing.

## Tide channeling

After trident hurt branch, server+thundering+CHANNELING>0+sky visible at recipient spawns real vanilla LightningBolt and setsCause only for ServerPlayer owner. It runs even when hurt false; successful Enderman early return skips it. Cause is advancement attribution, not owner added to cached lightning DamageSource. No chain/summoned-blood loot tags added. Native projectile impact/PVP/deflection may prevent onHitEntity before this branch. Keep trident HP and ownerless lightning HP as separate native events, each with a single final hurt scaling point.

## Compat and exclusions

Retain source IDs/tags and all native damage/effect/fire/projectile/strike hooks for Tensura/L2. No direct SHP edits, synthetic element events or fallback sources. Ordinary stats, crafting, repair, tooltip/lightning rendering and acquisition excluded; accepted Frozen, Siren, Ghost sword and armor work reused. Weapon source identity and gates above define future runtime coverage; no runtime claim.

## TNO integration decisions

- **Tagged post-hit bonus HP**: NUMERIC_SCALABLE, CUSTOM_ROUTED, ADMISSION_GATED. Stage: yes; Once at DamageBonusAbility final target.hurt(bonusSource,bonus).
- **Weapon ignition and native burning**: COMPOSITE, VANILLA_ROUTED, ADMISSION_GATED. Stage: yes; Once at native periodic on_fire hurt, if admitted; not ignition duration.
- **Real summoned/channeling lightning**: NUMERIC_SCALABLE, VANILLA_ROUTED, ADMISSION_GATED. Stage: yes; Once at native Entity.thunderHit hurt amount.
- **Dragonsteel visual-lightning mob_attack chain**: NUMERIC_SCALABLE, VANILLA_ROUTED, ADMISSION_GATED. Stage: yes; Once per final LightningMultihitAbility hurt; keep unscaled native queue amounts.
- **Additional sweep and gauntlet HP**: NUMERIC_SCALABLE, VANILLA_ROUTED, ADMISSION_GATED. Stage: yes; Once at custom sweep/gauntlet native player_attack hurt.
- **Slapper statuses and weapon knockback**: COMPOSITE, VANILLA_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional value; Native status/knockback quantities unchanged.
- **Dragonbone bow and arrow HP**: NUMERIC_SCALABLE, VANILLA_ROUTED, ADMISSION_GATED. Stage: yes; Once at inherited AbstractArrow final hurt after speed/crit/native modifiers.
- **Tide thrown and spin HP**: NUMERIC_SCALABLE, VANILLA_ROUTED, ADMISSION_GATED. Stage: yes; Once at TideTrident.onHitEntity final hurt for throw, or Player.attack final hurt for Riptide.

[Machine-readable packages, native paths and future fixtures](iceandfire-r2g9a-weapons.json). Validation reproduces new witnesses, checks significant call order/amounts, preserves accepted records and prior evidence, runs five tooling tests and diff checks. No whole-mod completion claim.

Exact next task: R2g9b: Chain, Dragon Flute, Pixie and remaining combat status/food callbacks. Then whole-JAR combat/source closure, dedup/promote Ice & Fire and next target if usage healthy.
