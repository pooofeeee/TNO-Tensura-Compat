# R2h4b — Eternal Starlight Ether, Shattered Blade and Wilt

Last three custom damage types and genuine fluid/projectile/armor/mob/crossbow deliveries; whole ES remains partial.

Static subsection complete. Runtime fixtures remain unexecuted; no Stage or production implementation.

## Ether contact

EntityMixin at BlockState.entityInside invocation marks IN_ETHER true for block fluid in #eternal_starlight:ether (still/flowing). Server Living entity tick reads old IN_ETHER_TICKS and current ARMOR. If contact flag true: factor=1-ETHER_RESISTANCE if attribute present, else0; only armor attribute PRESENT and current value<=0 requests ownerless ETHER(.3+.6*factor), ordinary iframes, hurttrue only gates particles. Null armor attribute does not admit this HP branch. Independently, (armor absent OR armor>0 OR oldTicks<140) && random.nextFloat()<=factor increments counter. Then clears contact flag. Full resistance factor0 still leaves .3 HP request when armor gate admits, and <= comparison includes exact random0 for counter; do not claim unconditional immunity. Alchemist armor supplies.3 Ether resistance per matching slot, range capped0..1; no reduction of shard flat4 via this attribute. Ether native fluid type extinguishes, cannot swim/drown, motionScale.0014. No fabricated fire/drowning/poison source.

## Ether corrosion

When no contact, positive old counter decrements1. Server if OLD<=0 removes armor.ether modifier; each living.tickCount%20==0 and OLD>0 replaces it with permanent ADD_VALUE(-OLD/100). These operations use the pre-update local, so counter changes and armor modifier are not instant/synchronous. Counter alone causes no ETHER HP request outside fluid; it is native armor corrosion, no MobEffect eligibility or effect-removal hook. Counter/contact are serialized attachments and native modifier persisted. Keep this resource and armor penalty unscaled: it governs damage admission itself, and multiplying both corrosion and ensuing HP would change eligibility. Proposed Stage only at final admitted ETHER hurt, not contact duration/state/armor threshold/resistance.

## Ether deliveries

Native ThioquartzArrow via bow/crossbow owned creation or registered ownerless dispenser: successful Living AbstractArrow post-hit callback (after Enderman early-return) adds200 IN_ETHER_TICKS capped400 if current<400, then emits five shards. Candidate aiming uses Living AABB8 filtered shouldHarm(owner), first five in returned order, remaining random; no LOS/sort. Secondary ThioquartzShard entity collision excludes exact owner then custom ETHER4 direct=shard/causer=owner (null allowed), ordinary iframes, no armor<=0 gate or shouldHarm recheck. Hurttrue &&Living gates +200 counter capped400; always discard even owner/hurtfalse contact. Shard block hit reflects only normal-axis velocity*-.5, other components unchanged; age>80 discards after super tick. ETHER tags bypass armor/enchantments/shield and no_impact/no_knockback, but not Resistance/invulnerability/cooldowns. Thus fluid armor admission and source armor bypass are separate. Stage shard final4 once; arrow primary remains final vanilla arrow hurt once, and counter/count/direction stay native.

## Amulet corrosion

Post damage handler checks active Butterfly Wings Amulet on ARMOR-slot accessory union (item Set, duplicates do not stack). Victim amulet plus Living causer adds200 counter capped600 to causer; Living causer amulet adds same to victim. Both can occur on one Post event, with no amount>0 condition or per-amulet cooldown here; source direct identity is not required. No normal effect add/canBeAffected call and no Ether-resistance test in these injections. Native fluid resistance affects subsequent contact accumulation, not existing counter or injected amounts. Future tests must distinguish projectile-caused Post, ownerless source, status immunity and actual armor modifier behavior. No extra Stage multiplier on this resource.

## Blade delivery

Player ShatteredSword native use with HAS_BLADE(defaulttrue) spawns owned ThrownShatteredBlade, weapon snapshot, speed2.5/inaccuracy1; no explicit side guard in use. Noncreative durability1 and sets hasBladefalse; creative pickup-only without spending blade. Native use/inventory can rearm from Blade item; finite blade state is a resource, not HP or Stage. LonestarSkeleton mainhand exact Shattered Sword selects its shoot goal (otherwise ordinary melee). Goal LOS sight counter and20 charge ticks then throws owned blade at current look rotation, interval20; attack radius15 controls navigation, not a separate final distance rejection. Native goal regenerates HAS_BLADE when charging and clears on throw. No blade dispenser producer proven.

## Blade payload

ThrownShatteredBlade override does not call AbstractArrow.onHitEntity. Amount=current owner ATTACK_DAMAGE if Living attribute present else5, then native weapon enchant modifyDamage; no speed/base/arrow-crit term. Custom SHATTERED_BLADE direct=blade, causing=owner or blade itself when owner null. Sets dealtDamage=true BEFORE hurt, so hurtfalse still disables further findHitEntity and starts native return. Hurttrue Enderman returns before follow-up; other success invokes enchantment post effects with rewritten player_attack or mob_attack for Living owner (original custom source otherwise), then knockback/arrow post effects for Living victim. HP source stays custom; callback rewrite is not a second HP hit. Ordinary iframes, IS_PROJECTILE, no armor/shield/Resistance/protection bypass. Every normal completion dampens/reverses velocity; grounded>4 also sets dealt. Return uses owner alive/non-spectator, player loyalty-style motion/noPhysics; non-Player owner server discards when return phase begins. dealtDamage and superclass owner/weapon state persist. Stage once at final custom hurt after current owner attribute/enchantments; do not also scale attribute or substitute captured weapon modifiers.

## Wilt primary and aura

WiltedCrossbow marks every native created projectile wilted, adds1.5 base only for AbstractArrow and multiplies launched velocity1.5 for all ammo. Handler server AbstractArrow AND !inGround only: each tick selects Living AABB5 shouldHarm(owner); independently requests Slowness80 amp0 and Wither160 amp0 (300 if ARROW is in water), ignoring effect acceptance. Every arrow.tickCount%4==0 spawns three owner-Living petals or ownerless petals; first affected entries aimed, remaining random, speed.8/inaccuracy.2. No hit/LOS gate. Native firework ammo receives marker/speed but fails AbstractArrow gate, so no aura/petals. Embedded arrows stop aura; freed/relaunched marked arrows can resume. Primary arrow/firework keeps native damage, collision, source and mitigation; Stage once at final primary request, not base+speed+request together.

## Wilt petal

WiltedPetal entity impact excludes exact owner, requests custom WILT8 direct=petal/causing=owner, ignores hurt return then discards. No added Wither/Slow or shouldHarm recheck on petal collision, unlike aura selection; preserve allied collateral eligibility and ordinary iframes. Normal-axis wall bounce*-.5 and age>80 match shard. WILT is IS_PROJECTILE with no armor/shield/Resistance/protection bypass; it is NOT minecraft:wither. Native Wither effect separately requests ownerless minecraft:wither1 every40 ticks at amp0 (native effect/update admission); ordinary effect rejection prevents that DOT but not petal HP. Stage petal final8 once; vanilla Wither DOT retains its existing final native hurt processing, while aura effect duration/amp, counts and range stay native.

## Scope

ETHER, SHATTERED_BLADE and WILT are USED with real callers. Alongside preceding protected families all18 custom types now have reviewed combat consumers; whole ES catalog remains PARTIAL until remaining vanilla-routed equipment/spells/creatures and closure/promotion are complete. Runtime fixtures and Tensura/L2 admission remain unexecuted. Armor stat resources, fluid mobility, projectile recovery, binary gates and native duration/cadence do not acquire a second Stage multiplier. Rendering, repairs/acquisition and fluid item transformations are excluded.

## TNO integration decisions

- **Ether fluid armor-gated damage**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Once at admitted final ownerless ETHER(.3+.6*factor) hurt.
- **Ether counter and armor corrosion**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional multiplier; Keep native resource/status values and thresholds; scale only the independently requested HP amount.
- **Thioquartz native arrow primary**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Once at native AbstractArrow final hurt; secondary counter and shards separate.
- **Thioquartz shard Ether damage**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Once at final shard ETHER4 hurt.
- **Shattered Blade native custom hit and return**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Once at final SHATTERED_BLADE hurt after current owner attribute and enchantments.
- **Wilted Crossbow native primary**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Once at final native selected-ammo hurt; never multiply both projectile base/speed and damage.
- **Wilted arrow native Slow/Wither aura**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional multiplier; Keep native resource/status values and thresholds; scale only the independently requested HP amount.
- **Wilted Petal damage**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Once at final custom WILT8 hurt.

[Machine-readable packages, delivery paths and future fixtures](eternalstarlight-r2h4b-ether-blade-wilt.json). Exact archive/method witnesses and targeted semantic assertions are reproducible. No whole-mod completion claim.

Exact next task: R2h5: remaining ES combat equipment, spells/crests/resources/attributes and non-boss creature defenses/attacks; build whole-mod combat callback closure and all18 DamageType disposition map, deduplicate/promote/full validation, then Bosses Rise. Do not repeat protected type/family semantics.
