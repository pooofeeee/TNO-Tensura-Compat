# Eternal Starlight combat owner table — COMPLETE

127 reviewed combat packages and 274 native source/control/defense contracts promoted from 157 protected input packages. Static evidence only; runtime tests remain unexecuted.

All18 custom DamageTypes have actual native caller mappings. Nine effects and native immunity, ownership, direct/causing identity, return-value gates, loader processing, resource and control prerequisites are retained. Eight registered spell stubs have no damage payload. Numbness debt and derived Starfire damage must not receive a second Stage multiplier.

| Mechanic | TNO classification | Single candidate Stage boundary / no-value reason |
|---|---|---|
| Crystal Infection periodic HP | CUSTOM_ROUTED, ADMISSION_GATED, NUMERIC_SCALABLE | Once at CrystalInfectionEffect native hurt(amplifier+1). |
| Crystal Infection armor and native stack state | COMPOSITE, VANILLA_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE | Keep native armor/amplifier/duration and ordinary effect admission. |
| Owned Crystal Cluster impact | CUSTOM_ROUTED, ADMISSION_GATED, NUMERIC_SCALABLE | Once at CrystalCluster native hurt4. |
| Crystal weapon native primary damage | VANILLA_ROUTED, ADMISSION_GATED, NUMERIC_SCALABLE | Once at each final native melee/sweep/arrow/firework hurt request after native weapon calculations. |
| Numbness deferred damage | COMPOSITE, CUSTOM_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE | Parent damage is scaled once before deferral; debt/payout inherits it and must not scale again. |
| Crescent Pendant native damage cap | COMPOSITE, CUSTOM_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE | Fraction of current maxHP; preserve source bypass and Numbness order. |
| Unrealium exact source veto | BINARY, ADMISSION_GATED, NO_STAGE_VALUE | Exact item/type cancellation. |
| Native consumable effect removal | BINARY, VANILLA_ROUTED, ADMISSION_GATED, COMPOSITE, NO_STAGE_VALUE | Ordinary cancellable effect removal; no HP value. |
| Starfire status and spread admission | COMPOSITE, CUSTOM_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE | Derived Post amount inherits parent Stage; no second multiplier. Native status and source identity stay intact. |
| Native arrow/firework HP with preserved weapon/ammo variants | VANILLA_ROUTED, ADMISSION_GATED, COMPOSITE, NUMERIC_SCALABLE | Once at final native AbstractArrow.onHitEntity or FireworkRocketEntity per-victim hurt after speed/base/crit/enchantment calculation. No separate projectile/base/velocity multiplier. |
| Flammable vulnerability | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Amplifier+2 stays a native original-hit modifier; no extra Stage at status multiplier. |
| Brittle vulnerability and frozen state | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Native chance/amplifier/frozenTicks; downstream damage has its own single request boundary. |
| Candlash/Coldsnap native Whip HP | VANILLA_ROUTED, ADMISSION_GATED, NUMERIC_SCALABLE | Once at Whip.tick final player_attack hurt, after native charge/enchantments; conditional ordinary melee reuses native Player hurt boundary. |
| Permafrost Spit and Cloud HP | CUSTOM_ROUTED, ADMISSION_GATED, NUMERIC_SCALABLE | Once per independent native FREEZE hurt: Spit1.25*ATTACK_SPEED or fallback15, Cloud4. |
| Native timed fire and freeze HP | VANILLA_ROUTED, ADMISSION_GATED, COMPOSITE, BINARY, NUMERIC_SCALABLE | Once at final native Entity.baseTick on_fire or LivingEntity freeze hurt; keep independent native counter/immunity/water/cadence and ownerless source. |
| Teary persistent target-control budget | COMPOSITE, CUSTOM_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE | Preserve serialized counter and distinct immunity predicates. |
| Native explosion HP with source-specific triggers | VANILLA_ROUTED, ADMISSION_GATED, COMPOSITE, NUMERIC_SCALABLE | Once at final native Explosion per-victim hurt after radius/exposure. Preserve source holder/owner, block interaction, independent status and spawn callbacks. |
| Native Poison periodic HP, separate from custom ES poison | COMPOSITE, VANILLA_ROUTED, ADMISSION_GATED, NUMERIC_SCALABLE | Once at installed PoisonMobEffect final hurt1, preserving HP>1 entry predicate and native neoforge:poison holder (magic fallback only when holder absent). Keep duration/amplifier/cadence fixed. Future Stage implementation must resolve scaled nonlethal behavior explicitly. |
| Dream Catcher native armor | COMPOSITE, VANILLA_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE | Retain native armor modifier and effect rules. |
| Sticky climb and speed | COMPOSITE, CUSTOM_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE | Movement/collision eligibility, no independent HP. |
| Oblivion passage/visibility/gravity/Blindness | COMPOSITE, CUSTOM_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE | Selective collision and native attributes; no scalar HP. |
| Native final healing, regeneration and repair | VANILLA_ROUTED, ADMISSION_GATED, COMPOSITE, NUMERIC_SCALABLE | Once at each final LivingEntity.heal request, including native Regeneration heal1, preserving heal event/HP clamp. Chain local damage basis remains unchanged; never also scale native heal multiplier or shared damage local. |
| Energy Sparks | CUSTOM_ROUTED, ADMISSION_GATED, NUMERIC_SCALABLE | Once at EnergySpark.hurtTarget final ENERGIZED_FLAME3 request. |
| Ball Lightning linked beam and expiry burst | CUSTOM_ROUTED, ADMISSION_GATED, NUMERIC_SCALABLE | Once at each independent native ELECTRIC_SHOCK8 beam or ENERGIZED_FLAME8 burst hurt request. |
| Energized Flame ground hazard | CUSTOM_ROUTED, ADMISSION_GATED, NUMERIC_SCALABLE | Once at EnergizedFlame.tick native ENERGIZED_FLAME2 request. |
| Energy Boomerang primary and electrical secondary | COMPOSITE, VANILLA_ROUTED, CUSTOM_ROUTED, ADMISSION_GATED, NUMERIC_SCALABLE | Once per independent final primary thrown hurt after attributes/enchant/crit OR secondary ELECTRIC_SHOCK8 request. |
| Golem terrain shockwave HP | CUSTOM_ROUTED, ADMISSION_GATED, NUMERIC_SCALABLE | Once at ownerless GROUND_SMASH4 native hurt. |
| ES damaging falling debris | VANILLA_ROUTED, ADMISSION_GATED, NUMERIC_SCALABLE | Once at ESFallingBlock.tick final falling_block3 request. |
| Golem Energy Block protection and charge interruption | BINARY, COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Preserve admission/state/native counters and ratios. |
| Native creature mob-attack HP | COMPOSITE, VANILLA_ROUTED, ADMISSION_GATED, NUMERIC_SCALABLE | Once at final native mob_attack hurt after native attribute/enchantment/formula. Source-specific literal hits and successful-hit callbacks retain their contracts. |
| Frozen Tube owner-selected direct HP | CUSTOM_ROUTED, ADMISSION_GATED, NUMERIC_SCALABLE | Once at FrozenTube.onHitEntity final FREEZE request after owner-type formula. |
| Frozen Tube splash and Golem counterplay | COMPOSITE, BINARY, ADMISSION_GATED, NO_STAGE_VALUE | Native freeze state, energy/cooldown drain and hazard discard, independent of direct HP. |
| Golem and Orb LASER beam | CUSTOM_ROUTED, ADMISSION_GATED, NUMERIC_SCALABLE | Once at RayAttack.doHurtTarget final LASER request after GolemLaserBeam amount calculation. |
| Lunar Monstrosity phase/cap/stun defenses | COMPOSITE, ADMISSION_GATED, BINARY, NO_STAGE_VALUE | Keep native source identity, independent return gates and nonnumeric controls; no duplicate Stage. |
| Lunar frontal bite | COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE | Once at doBiteDamage final BITE20 request. |
| Lunar dig/teleport/soul transition control | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Keep native source identity, independent return gates and nonnumeric controls; no duplicate Stage. |
| Lunar toxic breath | COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE | Once at final native breath POISON3 hurt. |
| Lunar boss/bow/Wand ground thorns | COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE | Once at LunarThorn.tick POISON mode0=4/other=3 hurt. |
| Lunar Spore manual burst | COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE | Once at each native POISON5 burst request. |
| Petal Scythe cloud HP/status and Post Poison | COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE | Once at independent cloud POISON5; native Poison DOT separately at its final periodic request. |
| Wand teleport and Tangled Husk decoy | COMPOSITE, ADMISSION_GATED, BINARY, NO_STAGE_VALUE | Keep native source identity, independent return gates and nonnumeric controls; no duplicate Stage. |
| Tangled Husk owner-direct burst | COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE | Once at native POISON10 request; independent spores use their own package. |
| Chain of Souls native drain | COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE | Once at final SOUL_ABSORB hurt argument after enchantments; do not mutate shared local basis. |
| Chain latch, pull, grapple and native redirection | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Preserve native local amounts, state and return gates; do not double-scale. |
| Dagger Hunger and food/weapon-state cycle | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Preserve native local amounts, state and return gates; do not double-scale. |
| Dagger of Hunger starvation punishment | COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE | Once at final ownerless DAGGER_OF_HUNGER3 hurt request. |
| Dual-wield sword native Player damage | COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE | Once at final native Player.attack hurt after native attribute/charge/enchantments. |
| Gatekeeper active-phase and source admission | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Native state, source identity and binary admission remain unchanged. |
| Gatekeeper sparring defeat/rescue/reset | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Native state, source identity and binary admission remain unchanged. |
| Gatekeeper direct fireball hit | COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE | Once at final native fireball8 hurt. |
| Gatekeeper combat and reset teleport | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Native state, source identity and binary admission remain unchanged. |
| Solar Creeper fall immunity and intro control | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Native state, source identity and binary admission remain unchanged. |
| Crystallized Moth sonar | COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE | Once at final SONAR hurt after attack attribute and vulnerability factor. |
| Moth sonar immunity and fall processing | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Keep targeting, cooldowns, sources and native state unscaled. |
| Sonar Bomb native mob-projectile AoE | COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE | Once at per-victim mobProjectile hurt, after vulnerability amount20/5 choice. |
| Aethersent Meteor manual area damage | COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE | Once at final METEOR hurt after size/owner/config formula. |
| Meteor armor chance and shared owner cooldown | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Keep targeting, cooldowns, sources and native state unscaled. |
| Meteor projectile damage rejection | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Keep targeting, cooldowns, sources and native state unscaled. |
| Seeds Launcher pellet damage and ignition gate | COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE | Once at final SEEDS hurt after enchantments plus speed, then ammo multiplier. |
| Ether fluid armor-gated damage | COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE | Once at admitted final ownerless ETHER(.3+.6*factor) hurt. |
| Ether counter and armor corrosion | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Keep native resource/status values and thresholds; scale only the independently requested HP amount. |
| Thioquartz shard Ether damage | COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE | Once at final shard ETHER4 hurt. |
| Shattered Blade native custom hit and return | COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE | Once at final SHATTERED_BLADE hurt after current owner attribute and enchantments. |
| Wilted arrow native Slow/Wither aura | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Keep native resource/status values and thresholds; scale only the independently requested HP amount. |
| Wilted Petal damage | COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE | Once at final custom WILT8 hurt. |
| Ashen Snowball native hit | COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE | Once at native thrown5/1.5 hurt, after Blaze predicate. |
| Ashen Snowball hit Blindness and independent Slow aura | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Native status/control and item resource remain unscaled. |
| Frozen Bomb independent freezing and Slowness | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Native status/control and item resource remain unscaled. |
| Malarite and Pungency native thrown spear damage | COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE | Once at final native thrown hurt after ordered attribute reconstruction, material factor and enchantments. |
| Ordinary greatsword/hammer/scythe and BloodBow HP | COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE | Once at native final melee or ammo hurt; no new BloodBow drain. |
| Crescent Spear native spin touch and collision AoE | COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE | Once at each Player.attack final hurt, after spin/charge/enchantment; do not scale stored spin again. |
| Hammer critical-event splash | COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE | Once per independent .75*ATTACK_DAMAGE native player_attack hurt. |
| Scythe native sweep admission and HP | COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE | Once per final native sweep hurt; native charge/ratio unchanged. |
| Greatsword immediate blocking and recovery | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Retain native modifier/control; existing parent damage path receives at most one Stage multiplier. |
| Flowglaze concentration modifier | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Retain native modifier/control; existing parent damage path receives at most one Stage multiplier. |
| Warhammer motion damage modifier | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Retain native modifier/control; existing parent damage path receives at most one Stage multiplier. |
| Flowglaze Shield collision reflection | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Retain native modifier/control; existing parent damage path receives at most one Stage multiplier. |
| Glacite Shield original-block freezing | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Retain native modifier/control; existing parent damage path receives at most one Stage multiplier. |
| Thermal material fire counters | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Preserve native control/resource/attribute values; any underlying HP/DOT/heal request has only its parent final native scaling point. |
| Glacite material frozen counters | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Preserve native control/resource/attribute values; any underlying HP/DOT/heal request has only its parent final native scaling point. |
| Malarite/Pungency held-weapon Poison and Nausea | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Preserve native control/resource/attribute values; any underlying HP/DOT/heal request has only its parent final native scaling point. |
| Deepsilver full-set tagged cleanse | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Preserve native control/resource/attribute values; any underlying HP/DOT/heal request has only its parent final native scaling point. |
| Native armor combat attribute modifiers | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Preserve native control/resource/attribute values; any underlying HP/DOT/heal request has only its parent final native scaling point. |
| Alchemist living-owner potion trajectory | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Preserve native control/resource/attribute values; any underlying HP/DOT/heal request has only its parent final native scaling point. |
| Unrealium movement/knockback/gravity attributes | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Preserve native control/resource/attribute values; any underlying HP/DOT/heal request has only its parent final native scaling point. |
| Unrealium native vibration suppression and visibility | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Preserve native control/resource/attribute values; any underlying HP/DOT/heal request has only its parent final native scaling point. |
| Amaramber exposed lower slots armor bonus | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Preserve native control/resource/attribute values; any underlying HP/DOT/heal request has only its parent final native scaling point. |
| Native ES accessory slot modifiers | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Preserve native control/resource/attribute values; any underlying HP/DOT/heal request has only its parent final native scaling point. |
| ES native healing multiplier and Fungus food admission | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Preserve native control/resource/attribute values; any underlying HP/DOT/heal request has only its parent final native scaling point. |
| AirSac Mask and Pearl air resource | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Preserve native control/resource/attribute values; any underlying HP/DOT/heal request has only its parent final native scaling point. |
| Native combat-significant consumable effects | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Preserve native control/resource/attribute values; any underlying HP/DOT/heal request has only its parent final native scaling point. |
| Boulders Shield native Resistance and movement | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Native effect/attribute/fuel values stay fixed; original HP request keeps its single final damage scaling point. |
| Native spell and crest crystal resource | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Native effect/attribute/fuel values stay fixed; original HP request keeps its single final damage scaling point. |
| On-hit mana shard and pickup fuel restoration | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Native effect/attribute/fuel values stay fixed; original HP request keeps its single final damage scaling point. |
| Abyssal Fire contact and timed native HP | COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE | Once per final native in_fire3/on_fire3 hurt; preserve timer iframe handling. |
| Amaramber Fire contact HP | COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE | Once at native in_fire1 hurt. |
| Native block-contact HP | COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE | Once at final native cactus/hot_floor/campfire hurt; preserve per-block contact/stepping/lit admission and native source. |
| Icicle native pointed and falling HP | COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE | Once at final native stalagmite/falling_block hurt after fall formula. |
| Crinoa Bale and Yeti Fur fall admission | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Keep native control/resource/attributes and triggers; later native HP/heal retains its own final single scaling point. |
| Golem Steel Jet motion and fall admission | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Keep native control/resource/attributes and triggers; later native HP/heal retains its own final single scaling point. |
| Abyss depth and post-hit air resource | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Keep native control/resource/attributes and triggers; later native HP/heal retains its own final single scaling point. |
| Glacial Sowing frozen counter | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Keep native control/resource/attributes and triggers; later native HP/heal retains its own final single scaling point. |
| Fearless native knockback and owner movement | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Keep native control/resource/attributes and triggers; later native HP/heal retains its own final single scaling point. |
| Poisoning armor native attacker Poison | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Keep native control/resource/attributes and triggers; later native HP/heal retains its own final single scaling point. |
| Native enchantment modifiers on reviewed attack families | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Keep native control/resource/attributes and triggers; later native HP/heal retains its own final single scaling point. |
| Aetherstrike Rocket indirect meteor weather trigger | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Keep native control/resource/attributes and triggers; later native HP/heal retains its own final single scaling point. |
| Gleech native attachment/summon | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Fixed native defense/control/resources and modifiers remain unscaled; any resulting already-reviewed HP request keeps its own final scaling. |
| Independent native status cloud/death-effect callback | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Fixed native defense/control/resources and modifiers remain unscaled; any resulting already-reviewed HP request keeps its own final scaling. |
| Creteor native Tiny summon | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Fixed native defense/control/resources and modifiers remain unscaled; any resulting already-reviewed HP request keeps its own final scaling. |
| Aethersent Golem ownerless native magic | COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE | Once at final native magic8 hurt. |
| Aethersent Golem natural meteor interception | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Fixed native defense/control/resources and modifiers remain unscaled; any resulting already-reviewed HP request keeps its own final scaling. |
| Astral material defense and ordinary shield admission | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Fixed native defense/control/resources and modifiers remain unscaled; any resulting already-reviewed HP request keeps its own final scaling. |
| Boarwarf native guard targeting | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Fixed native defense/control/resources and modifiers remain unscaled; any resulting already-reviewed HP request keeps its own final scaling. |
| Luminofish delayed independent Poison | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Fixed native defense/control/resources and modifiers remain unscaled; any resulting already-reviewed HP request keeps its own final scaling. |
| Fish exact native hot-floor immunity | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Fixed native defense/control/resources and modifiers remain unscaled; any resulting already-reviewed HP request keeps its own final scaling. |
| ShadowSnail panic/hide mitigation | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Fixed native defense/control/resources and modifiers remain unscaled; any resulting already-reviewed HP request keeps its own final scaling. |
| Stranghoul deepsilver direct-weapon vulnerability | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Fixed native defense/control/resources and modifiers remain unscaled; any resulting already-reviewed HP request keeps its own final scaling. |
| NightfallSpider native Glowing | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Fixed native defense/control/resources and modifiers remain unscaled; any resulting already-reviewed HP request keeps its own final scaling. |
| NightfallSpider inherited Poison immunity | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Fixed native defense/control/resources and modifiers remain unscaled; any resulting already-reviewed HP request keeps its own final scaling. |
| ThirstWalker native Hunger and intentional flee resource | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Fixed native defense/control/resources and modifiers remain unscaled; any resulting already-reviewed HP request keeps its own final scaling. |
| Native fire/fall traits and sunlight ignition | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Fixed native defense/control/resources and modifiers remain unscaled; any resulting already-reviewed HP request keeps its own final scaling. |
| Native Gel bounce and bubble movement | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Native control/eligibility/physics remains fixed; reused damage paths retain their already-reviewed final amount point. |
| AirSac Boots native gravity override | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Native control/eligibility/physics remains fixed; reused damage paths retain their already-reviewed final amount point. |
| Native weapon knockback and projectile-water companions | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Native control/eligibility/physics remains fixed; reused damage paths retain their already-reviewed final amount point. |
| Stranghoul native hirer and prey targeting | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Native control/eligibility/physics remains fixed; reused damage paths retain their already-reviewed final amount point. |
| Native Quiver and ignition source prerequisites | COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE | Native control/eligibility/physics remains fixed; reused damage paths retain their already-reviewed final amount point. |
| Native Wither periodic HP | COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE | Once at native WitherMobEffect final ownerless wither1 hurt; keep40>>amplifier cadence and effect admission unchanged. |

[Complete accepted contracts](mod-reviews/eternalstarlight.json), [every native path and fixture](eternalstarlight-future-runtime-fixtures.json), [total source coverage](eternalstarlight-total-source-coverage.json), [deduplication map](eternalstarlight-final-promotion-map.json).

Runtime priorities: native source tags versus visual elements; parent/derived amount handling; body/arrow/firework/ownerless routes; rejected HP versus independent status/control/spawns; target/mount/effect/guard admission; actual final healing and shared local damage bases. Resistance/Nullification/L2 behavior is unmeasured. Native Poison HP>1 admission and future scaled nonlethal policy need explicit runtime/implementation review; no status duration/amplifier or radius/count scaling is proposed.

Short exclusions: rendering/cosmetics, crafting/acquisition/progression, storage/information, ordinary self utility, passive creatures with no attack callback, worldgen without combat effect. No runtime, L2, production, Stage, Phase6 or Phase7 work.

Exact next task: R2i1: Bosses Rise installed-native combat foundation (block_factorys_bosses-2.1.2-neo-1.21.1.jar), then bounded combat family review. Reuse source aids, preserve accepted ES/Twilight/Ice & Fire; no runtime, L2, Stage, production or Phase6/7 work.
