# R2h6 — Eternal Starlight crests and spell closure

Installed spell closure, passive Boulders Shield and native combat mana resource. Reuse accepted laser, exclude empty stubs/locator.

Static subsection complete. Runtime fixtures remain unexecuted; no Stage or production implementation.

## Spell disposition

All10 registered spells and all11 installed crest JSONs pinned. Laser Beam is actual combat and reuses accepted GolemLaserBeam source/admission/Stage point. Guidance of Stars is a Starlight-dimension structure locator with particles/sound only: short utility exclusion. Eight others (Burst Spark, Flaming Aftershock, Flaming Arc, Flaming Ring, Merged Fireball, Surrounding Fireballs, Frozen Fog, Icy Spikes) have true extra-condition predicates and EMPTY preparation/spell/start/stop callbacks. Their registered names and crest JSONs do not establish damage, projectile, burn/freeze or crowd control; exclude as native effect stubs, not unresolved damage types. Common cast resource/cooldown processing still runs.

## Native delivery

OrbOfProphecy server use requires standing Player/SpellCaster, no current cast, bound current-crest component with spell, spell.canCast(checkCrystal=true). That checks cooldown<=0, extra conditions, and creative or ANY matching crystal tag in inventory. start uses owned crest level; normal tick removes a bound current crest absent from owned IDs. Spell source canContinue only same Item identity in recorded hand, not same stack, use animation, crest identity or sustained crystal presence. Actual Laser Orb delivery already reviewed. SimpleSpellItem contains an alternative start(checkCrystal=false)/item-durability path but whole-JAR constructor census finds NO instantiated native SimpleSpellItem route; do not invent a legitimate laser item delivery from this unused class.

## Mana cost

Orb start damages first matching crystal by1 except infinite materials; common spell tick every15 ticks calls damageCrystal for Player with no separate creative condition, although native item hurtAndBreak may itself reject durability loss. Search matches ANY listed mana type, not one crystal per type; all six type tags include universal mana_crystal. Once casting, canContinue does not recheck crystals; insufficient crystals makes later damageCrystal search do nothing rather than stop the native spell. Cooldown applied on stop; tickSpells increments state, calls stop on continuation failure then may still call tick once if within total duration. Preserve this accepted ordering; no resource affordability or source fallback invented.

## Crest passive

ES Player tick invokes ESCrestUtil.tickCrests. For every SELECTED crest, creative or first inventory crystal matching crest.type activates it; every60 player ticks damages that first crystal by crest level, then still applies effects on that tick even if crystal breaks. Active effect duration20, amplifier=entry.level+(crest.level-1)*levelAddition, refreshed every tick through native addEffect; removal when disabled is normal short-duration expiry, not explicit removeEffect. Attribute modifier amount=amount+(level-1)*amountAddition, permanent same-ID modifier added only if absent. Old active instances not in new list have modifiers removed after new additions; changing level can leave a one-tick gap before replacement, not guaranteed immediate in-place update. Fuel absent removes attribute via old-active cleanup; effect admission remains native.

## Boulders shield

Only installed passive crest is Boulders Shield: terra fuel, declared max_level2, native Resistance amp0 at level1 /amp1 at level2 and movement ADD_VALUE -.007 /-.012 respectively. Native Resistance formula reduces eligible damage20%/40%, subject to BYPASSES_EFFECTS and BYPASSES_RESISTANCE plus native effect eligibility/loader hooks; no custom shield resource, no barrier damage source. Modifier limits/levels and event interception stay native. Keep Resistance and speed fixed; Stage only once at original incoming damage source, never on buff potency or duration.

## Selection admission

UpdateCrestsPacket server handler checks each selected crest ID is among owned crest IDs, then stores supplied list; it does NOT compare submitted levels to owned levels, deduplicate entries or enforce a count in that handler. Crest.Instance.of caps normal constructed level at declared max, while Instance codec uses INT. Catalog describes normal registered level1/2 values, not a server-wide proof that all runtime data is capped. Do not bypass/fix these native selection rules; runtime fixtures must record actual selected levels/duplicates and data-pack overrides instead of assuming UI guarantees.

## Mana refill

LivingDamageEvent.Post: source.directEntity Player, random nextInt15==0 and at least one #MANA_CRYSTALS stack anywhere in inventory -> spawn one ordinary Mana Crystal Shard ItemEntity at victim. No positive event amount or final HP-loss test in this branch; indirect projectile owner alone does not qualify. ItemEntityMixin.playerTouch HEAD server, pickupDelay0 and targetUUID null/matching and exact shard: cancel ordinary pickup, take/discard whole shard entity, then repair FIRST damaged tagged crystal by shard stack count floored0 and return. Shard is consumed even if no damaged crystal exists; no player HP/heal/SHP/magicule transfer. This is a combat fuel replenishment route, not ordinary inventory loot storage; keep quantities unscaled.

## Scope

Crest entity pickup/acquisition/progression/rendering and its non-Living collectible health are brief exclusions. Spell particles and locator search receive no deep utility review. No runtime tests or production implementation. Native mana item resources/cast cadence, effect duration/amplifier and attribute modifiers have no new Stage quantity; future tests use legitimate Orb/passive/shard paths without fabricating effect-stub output.

## TNO integration decisions

- **Boulders Shield native Resistance and movement**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional multiplier; Native effect/attribute/fuel values stay fixed; original HP request keeps its single final damage scaling point.
- **Native spell and crest crystal resource**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional multiplier; Native effect/attribute/fuel values stay fixed; original HP request keeps its single final damage scaling point.
- **On-hit mana shard and pickup fuel restoration**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional multiplier; Native effect/attribute/fuel values stay fixed; original HP request keeps its single final damage scaling point.

[Machine-readable packages, delivery paths and future fixtures](eternalstarlight-r2h6-crests-spells.json). Exact archive/method witnesses and targeted semantic assertions are reproducible. No whole-mod completion claim.

Exact next task: R2h7: remaining non-boss creatures and hazards including Abyssal Fire/enchantments, Gleech Egg attachment, Aetherstrike Rocket weather, native melee/defenses. Then whole ES actual-caller closure, deduplicate/promote, full validation and automatic Bosses Rise continuation while healthy.
