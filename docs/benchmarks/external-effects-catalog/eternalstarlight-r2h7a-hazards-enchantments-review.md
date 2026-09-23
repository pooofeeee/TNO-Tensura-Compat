# R2h7a — Eternal Starlight hazards and enchantments

Native environmental damage/control/resources, remaining enchantment semantics and indirect Rocket weather delivery.

Static subsection complete. Runtime fixtures remain unexecuted; no Stage or production implementation.

## Abyssal fire

AbyssalFireBlock.entityInside if type NOT #abyssal_fire_immune and entity.tickCount%30==0 requests ownerless native in_fire3; ignores hurt result. Independently server sets ABYSSAL_FIRE_TICKS=max(old,5) even on immune type. Server entity tick while old timer>0 decrements1, and if not immune and tick%30==0 saves victim invulnerableTime, sets0, requests ownerless native on_fire3, then restores saved time regardless return. Contact and timer are separate requests and may coincide; neither uses a new ES DamageType or direct HP write. Preserve both source identities, exact iframe handling and native fire immunity/Fire Resistance/IS_FIRE processing. Scale each final native hurt once; no Stage on timer duration/cadence.

## Abyssal admission

Installed immune tag exactly Luminofish, Luminaris, Twilight Gaze. Whole-JAR state producers only block contact and IgniteAbyssalFire enchantment effect; timer consumer ES tick and EntityFlagsPredicate mixin plus cosmetic render readers. Predicate wrapper treats ordinary isOnFire OR timer>0 as on-fire in EntityFlagsPredicate.matches; it does not universally override Entity.isOnFire or ordinary fire ticks. Water contact does not explicitly clear this custom counter in these native writers/consumer. Immune tagged entities may retain counter yet reject the custom timer damage request before native hurt. Preserve tag reload and effect-source admission, no fake fire source.

## Abyssal touch

Native Abyssal Touch enchantment max2, supported/primary whip tag MAINHAND, post_attack enchanted=attacker affected=victim with no extra JSON predicate. IgniteAbyssalFire.apply sets timer=max(old,(int)duration(level)*20); installed duration5/10 seconds ->100/200 ticks. Whip successful hit supplies genuine native enchantment post callback; do not fabricate a callback on rejected hit. No direct source from effect apply; later timer uses ownerless on_fire and loses attacker attribution by design. Leave post eligibility and timer unchanged; final native DOT hurt is only Stage point.

## Amaramber fire

Every AmaramberFireBlock contact requests ownerless native in_fire1; return ignored, and Living target separately receives native Regeneration100 amp0. No canHarm, special owner, success requirement or fire-tick increment in this override. Thus native fire rejection can coexist with accepted healing buff, and effect rejection can coexist with fire damage. Scale final native in_fire hurt once; native Regeneration healing retains its existing final heal processing, duration/amplifier unscaled.

## Contact hazards

Lunaris Cactus only when FRUIT=false requests ownerless cactus1; fruiting state does not request damage. Stellagmite Block/Slab/Stair/Wall all delegate shared step: block must be a molten value in TO_MOLTEN mapping, target Living and not stepping carefully, then ownerless hot_floor1. No enchantment/Frost Walker test in ES wrapper; later native source admission remains. Native hot-floor immunity on relevant fish is separate creature review. Each final native contact hurt is single future Stage point, not callback count or block-state probability.

## Icicle

Upward TIP landing invokes causeFallDamage(fallDistance+2,2,native stalagmite); other states delegate normal block fall. Unsupported downward formation tick spawns native FallingBlockEntity; only TIP gets setHurtsEntities(5,40). Icicle is Block/SimpleWaterloggedBlock, not Fallable, so exact native FallingBlockEntity.causeFallDamage uses falling_block direct=causing=falling entity (no player owner), not falling_stalactite. It selects alive Living excluding creative/spectator in impact box, i=ceil(fallDistance-1), skips i<0, requests min(floor(i*5),40), ignores each hurt return and method returnsfalse. No ES iframe reset or cold damage. Projectile mayInteract AND mayBreak AND speed>.6 can destroy supporting icicle via native callback; block-update falling is indirect environment delivery, not projectile damage. Scale each final actual stalagmite/falling_block hurt once after native fall calculation.

## Cushion jet

Crinoa Bale native causeFallDamage(distance,.2,fall). Yeti Fur normal fall when suppressing bounce, otherwise native fall multiplier0 and rebound negativeY by.8 Living/.6 other; no new HP damage added. Golem Steel Jet server tick with power>0 and cooldown0 gets all Entities in blockAABB expanded facing.05, adds velocity direction*sqrt(power*.21)*(oxidized?.9:1), marks motion, and for Player sets currentImpulseImpactPos plus ignore-fall-damage-from-current-impulse. Success sets cooldown5. No attack/source/hurt or knockback-resistance query; environmental movement and fall admission remain unscaled. Existing native resulting fall damage, if any, gets only final damage scaling.

## Abyss air

Player tick in THE_ABYSS biome with water at eyes and Y<0 clamps current air down to max(round((maxAir+Y*3)/30)*30-15,0). Post living damage to Player in same biome+water eyes with air>0 subtracts30 floored0, with no amount>0 test. These are independent air-resource writes, not HP/SHP damage or custom drowning DamageType. Native later drowning remains source/admission authority. Preserve Water Breathing/air refills and actual environment intersection; no Stage on depth formula or30-air penalty.

## Freeze enchant

Glacial Sowing max2 MAINHAND Seeds Launcher, native post_attack enchanted attacker/affected victim requires direct_attacker entitytype shot_seeds. Native ShotSeeds only calls its enchantment post path on hurttrue; owned item/source branch and saved-weapon limitations were reviewed earlier. Freeze.apply adds duration(level)*20 then int cast to current frozen ticks, capped600; installed4/8 seconds adds80/160. There is NO canFreeze test in this effect. Control and subsequent native freeze admission are separate; no new custom FREEZE source or independent Stage on frozen ticks.

## Other enchants

Fearless native mainhand sharp-weapon enchantment max2 adds knockback .5/1 and post_attack affected victim invokes PushTowardsEntity: if item.owner nonnull, random speed[.1,.1] at level1 /[.1,.3] at2 floored0, owner moves toward victim and is motion-marked. It does not push victim or inspect owner knockback resistance. Poisoning armor enchantment max4, enchanted victim/affected attacker, uses native ApplyMobEffect Poison: duration random[2.5,2.5+.5*(level-1)] seconds converted round(*20), amplifier round(random[0,level]) floored0. Affected attacker resolves DamageSource.getEntity (causing owner), not direct projectile; absent causing entity yields no application. Thus indirect native projectile can poison its Living shooter if its legitimate enchantment post callback runs. Native addEffect immunity remains; chance/duration/amplifier/control not Stage quantities. Preserve callback-specific hurt-return behavior; do not assume all custom attacks call vanilla post.

## Enchant disposition

All13 installed enchantment JSONs pinned. Already accepted paths: Fertile Seeds count +2*level; Overheat native projectile-spawn ignite, Seeds hurttrue fire delivery; Precision boomerang crit +.16*level, Homing strength .1+.75*(level-1), Gathering pickup radius utility; Soul Snatcher Chain damage +.5*level after direct chain predicate; Tracing native Glowing on genuine Chain post; Tearing native Teary on direct Pungency spear. Swift Lash mainhand whip attack-speed +.2*level is ordinary native attribute. These modify existing requests or fixed native control/cadence, not new HP sources. No second Stage multiplier on their bonus or projectile count. Acquisition/exclusivity/crafting details excluded except genuine item/source eligibility.

## Rocket weather

AetherstrikeRocketItem native useOn server spawns owned rocket at clicked face offset and shrinks stack1; explicitly registered ownerless dispenser uses angle-shot constructor. Rocket custom tick native hitTargetOrDeflectSelf, entity/block impact or lifetime expiry calls explode. This method only gameEvent EXPLODE, sound/particles, possible WEATHER activation and discard: NO Level.explode or entity hurt. In server Starlight dimension, random<.6 and canSeeSky sets natural METEOR_SHOWER for native sampled duration; only successful weather activation with Player owner sets item cooldown2400. Does not require current weather empty. Later natural meteors use already-reviewed ownerless METEOR path, not rocket owner attribution. Block hit first calls impacted block.entityInside on rocket before trigger, then normal onHitBlock. Keep native weather/dimension/sky/probability/deflection and ownership, no Stage on rocket or weather trigger.

## Scope

Static hazard/enchantment completion only; runtime fixtures remain pending. Do not equate fire visuals/ice names/EXPLODE game event with invented HP damage. Fixed counters, movement, resource, effect eligibility and cadence stay native. Source mitigation/Resistance/loader/L2 later processing must remain; no runtime, production or Stage changes.

## TNO integration decisions

- **Abyssal Fire contact and timed native HP**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Once per final native in_fire3/on_fire3 hurt; preserve timer iframe handling.
- **Amaramber Fire contact HP**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Once at native in_fire1 hurt.
- **Amaramber Fire independent native Regeneration**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional multiplier; Keep native control/resource/attributes and triggers; later native HP/heal retains its own final single scaling point.
- **Cactus and molten Stellagmite contact HP**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Once at final native cactus/hot_floor hurt.
- **Icicle native pointed and falling HP**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Once at final native stalagmite/falling_block hurt after fall formula.
- **Crinoa Bale and Yeti Fur fall admission**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional multiplier; Keep native control/resource/attributes and triggers; later native HP/heal retains its own final single scaling point.
- **Golem Steel Jet motion and fall admission**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional multiplier; Keep native control/resource/attributes and triggers; later native HP/heal retains its own final single scaling point.
- **Abyss depth and post-hit air resource**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional multiplier; Keep native control/resource/attributes and triggers; later native HP/heal retains its own final single scaling point.
- **Glacial Sowing frozen counter**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional multiplier; Keep native control/resource/attributes and triggers; later native HP/heal retains its own final single scaling point.
- **Fearless native knockback and owner movement**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional multiplier; Keep native control/resource/attributes and triggers; later native HP/heal retains its own final single scaling point.
- **Poisoning armor native attacker Poison**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional multiplier; Keep native control/resource/attributes and triggers; later native HP/heal retains its own final single scaling point.
- **Native enchantment modifiers on reviewed attack families**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional multiplier; Keep native control/resource/attributes and triggers; later native HP/heal retains its own final single scaling point.
- **Aetherstrike Rocket indirect meteor weather trigger**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional multiplier; Keep native control/resource/attributes and triggers; later native HP/heal retains its own final single scaling point.

[Machine-readable packages, delivery paths and future fixtures](eternalstarlight-r2h7a-hazards-enchantments.json). Exact archive/method witnesses and targeted semantic assertions are reproducible. No whole-mod completion claim.

Exact next task: R2h7b: remaining non-boss creature combat, especially Gleech attachment/Egg, Creteor/TinyCreteor native blasts, Aethersent/Astral Golems, animal/Stranghoul/Boarwarf defenses/heals and ordinary melee. Then whole ES actual-caller coverage, dedup/promotion/full validation; continue Bosses Rise automatically while healthy.
