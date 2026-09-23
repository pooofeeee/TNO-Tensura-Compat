# R2g10a — Ice & Fire combat closure

Whole installed Iaf combat-significant census and final small gaps complete; dedup/promotion remains.

Static subsection complete. Runtime fixtures unexecuted; no Stage or production implementation.

## Coverage

Installed IceAndFireCE beta15 whole-JAR census parses726 classes and188 watched combat/admission methods, including130 methods with targeted HP/heal/status/fire/explosion/knockback/fall/teleport/target calls. Every such method now has pinned native instructions. This is an index into completed family semantics plus the explicit exclusions here, not an assumption that a class containing a witness is automatically reviewed. All five declared custom damage types and seven direct factory caller methods reproduce protected R2g1 evidence unchanged. Registry creature families, item combat overrides, named statuses, direct compat hooks and remaining callback gaps have been reviewed; no runtime execution implied.

## Blindfold

BlindfoldItem.inventoryTick on Player requires equipped HEAD stack identity == ticking stack, then requests Blindness50ticks amp0 each tick, normal effect admission. It is separate from Gorgon.isBlindfold native head item-tag check: rejecting Blindness does not remove a still-matching head-item predicate. Unwearing can leave admitted Blindness until duration expires. No numeric HP or extra Stage value; all accepted Gorgon and Cockatrice gaze semantics remain unchanged.

## Egg zero hit

Rotten/Cockatrice, DeathWorm(normal/giant), Hippogryph eggs have legitimate Player.use server-owned launches (speed1.5/inaccuracy1) and registered dispenser asProjectile ownerless variants. On entity impact each native override requests minecraft:thrown direct=egg, causing=owner/null, amount0; no added HP payload or scalar to Stage. Keep real zero-amount callback/hurt-return/aggro processing in later compatibility tests. Native hatching and discard run independently of that hurt return. Hatching supplies new native creature state, not direct target damage; ordinary breeding/acquisition mechanics are excluded, and existing creature packages cover any later attack. No added damage to make an egg test visible.

## Native target control

DragonBase.aiStep clears Player target in Peaceful; model-dead state ejects passengers and clears hover/flight. updateCheckPlayer wakes sitting state and sets a nearby nonowner/noncreative Player target when sleeping, radius boundingBoxSize*3; no additional HP request. Ground riding AI clears mob target every tick while rider exists, explaining AI versus controlled attack separation. ServerEvents entity-join installs ordinary AvoidEntityGoal wrapper for configured tagged villagers/animals (8/30 range), based on native IVillagerFear/IAnimalFear predicates; it is navigation, not Tensura fear status, damage or resource drain. Preserve normal native AI target/owner gates, no Stage on these values. Tracking/attack alarms and chest/pile aggression reuse the saved ServerEvents and prior family contracts.

## Custom sources

Custom registry closure: iceandfire:bonus only bypasses_cooldown; gorgon bypasses_armor and bypasses_shield; dragon_fire/dragon_ice/dragon_lightning each always_hurts_ender_dragons in scoped installed tags. Source wrappers change death messages, not broad bypass. Preserve proven ridden Lightning indirect factory returning dragon_ice. Seven native factory call sites route through three charge causeDamage methods, Gorgon.aiStep, GorgonHead.releaseUsing, DragonDestructionManager.getDamageSource and DamageBonusAbility.active. Secondary vanilla arrow/trident/mob_attack/player_attack/indirect_magic/magic/wither/cactus/explosion/lightning/fire routes remain individually documented. No new damage type or fallback source is proposed.

## Compat closure

Protected installed tensura_iaf11 mixins are fully accounted for: Gorgon abnormal/native gaze eligibility; Siren admission; Frozen ColdNullification; IceSpikes and three breath projectile callbacks; Dragon corpse eligibility; RaceUtils nonliving corpse; Chain attachment; TensuraDamageHelper classification. Helper classifies GORGON abnormal, DRAGON_ICE cold, DRAGON_FIRE fire, DRAGON_LIGHTNING lightning and all four nonphysical by exact source-holder predicates, not by visual appearance. BONUS is not in this override. Whole compatibility entity-tag declarations are pinned as data; pack merging and consumers remain native and must be observed later, not treated as measured immunity. No L2 interception or SHP manipulation implemented.

## Short exclusions

Decorative DragonSkull/MobSkull hurt converts decoration to item before parent hurt, not an offensive mechanic. Stationary DragonEgg hurt is binary item removal (Fire egg rejects IS_FIRE); hatching/Dragon cave/roost setHealth are acquisition/spawn initialization, not combat healing. SummoningCrystal/DragonHorn store or recall owned creatures; no separate HP/status attack claimed. Bird air-target/flock positions and ordinary pathfinding are navigation. Rendering, animation-only state, particles, sounds, crafting, repair, loot, books, colors, structures, containers and worldgen without combat callbacks are excluded without deep subsections. Myrmex is absent; Queen and legacy necromancy have no proven native delivery as protected in R2g8a/R2g8d.

## Decision

Static combat-significant family research is closed. Ice & Fire remains PARTIAL in accepted catalog until the explicit dedup/promotion checkpoint; all reviewed packages and native distinctions must survive that promotion. Stage remains a proposed single integration point per numeric payload, with binary/control/admission behavior kept native. No Stage, production, runtime boss, L2 or Phase6/7 work performed.

## TNO integration decisions

- **Equipped Blindfold native Blindness**: VANILLA_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional value; Native status and separate item-tag gaze admission, no HP scalar.
- **Native egg zero-amount impact**: VANILLA_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional value; Zero native HP request must remain zero, hatching is separate.
- **Native creature targeting and fear navigation**: BINARY, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional value; AI targeting/movement, no damage or Tensura fear status.

[Machine-readable packages, native paths and future fixtures](iceandfire-r2g10a-closure.json). Validation reproduces new witnesses, checks significant call order/amounts, preserves accepted records and prior evidence, runs five tooling tests and diff checks. No whole-mod completion claim.

Exact next task: R2g10b: deduplicate and promote all reviewed Ice & Fire packages/deliveries into accepted views, mark mod COMPLETE, run full validation and five tooling tests, push/live-verify. Then Eternal Starlight native source foundation while usage healthy.
