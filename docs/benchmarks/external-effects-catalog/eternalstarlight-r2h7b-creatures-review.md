# R2h7b — Eternal Starlight remaining creature combat

Remaining non-boss creature attacks, summons, admission/defenses and native healing only.

Static subsection complete. Runtime fixtures remain unexecuted; no Stage or production implementation.

## Gleech egg

Player native Gleech Egg use or explicitly registered dispenser spawns real projectile. Entity hit first requests native thrown(egg,owner) amount0; return ignored. Server Living victim NOT #gleech_immune creates larval Gleech, attaches before addFreshEntity, sets victim target, then requests mobAttack(victim) amount0 against Gleech, also ignored. No successful hit, shouldHarm or player owner requirement for this summon. Installed immune set Gleech/NightfallSpider/Silverfish/Spider/CaveSpider. Zero requests are native callbacks, not Stage HP. Preserve source/owner and loader admission; never replace them with damage.

## Gleech attachment

Whole-JAR attachTo caller is GleechEgg only. Server attachTo calls startRiding(victim,true), ignores return and sends ClientMount. Force bypasses canRide/canAddPassenger, but native same-vehicle, couldAcceptPassenger, cycle and NeoForge canMountEntity checks remain. rideTick invokes normal tick, zeroes motion/resets fall; after attachTicks>80 attempts stopRiding and sends ClientDismount. Native dismount event may veto: no claim guaranteed release. Larval/growth saved, attachTicks not saved. No custom life drain/heal/Poison/SHP. Attached or free Gleech uses MeleeAttackGoal and ordinary Mob.doHurtTarget; native cooldown, melee reach and LOS still gate attempts. Native Mob ATTACK_DAMAGE plus enchant modifyDamage -> mob_attack(this), hurttrue gates knockback/enchantment post/last-target. Future fixtures must measure actual mounted attack admission, not assume every riding tick damages.

## Creteor

Creteor hurt activates before super even if rejected. Target/ignition also activate. Swell below80: ignition increments; otherwise target squared distance<=25 plus sensing LOS increments, else decrements, clamp0..80. Once80 there is no distance/LOS abort; noGravity and spin, upward first40, explosion after spin>80. Server explosion radius3 normal/6 powered, native MOB interaction. TinyCreteor has same swell gate but detonates without spin, radius2/3 and NONE interaction. Native creeper igniter and lightning power are legitimate distinct paths. Native explosion direct=causing=Living Creteor/TinyCreteor, so DamageSources.explosion selects player_explosion despite mob identity. Final native per-victim damage only Stage point, after exposure/radius formula; keep source tags, shield/Resistance/admission, no Stage on radius/fuse.

## Creteor aftereffects

Detonation marks dead before Level.explode, then independently copies current status effects into ownerless native AreaEffectCloud, triggerOnDeathMobEffects(KILLED), discard; Creteor additionally creates2..4 TinyCreteors only if their canSpawn config allows, inheriting powered and target, no player owner. Tiny has no split. Cloud radius2.5, radiusOnUse-.5, wait10, half native duration (600->300), radius shrinks-r/duration; no setOwner. Hurt returns from blast do not gate cloud/split/death-effect callback. Native AEC victim eligibility, reapplication and addEffect/instant-effect handling remain authoritative. No ordinary-death auto-explosion caller found; only native detonation state path. Child ordinary melee/blast reused, no separate summon damage multiplier.

## Aethersent golem

Every server20ticks stationary Golem queries AABB75 natural AethersentMeteors -> dropAndDiscard(true), a binary interception, no HP. Separately AABB50 Living type#aethersent_golem_targets (Seeker,TinyCreteor,Phantom) requests ownerless native magic8; no LOS/sphere/shouldHarm check, return ignored. Laser particles do not create laser entity. Single final magic hurt Stage point; native magic source remains ownerless. AethersentIngot interaction native heal25 and consumes1 only if actual health changes; native heal event may veto. Heal separately at final native heal once, not item count. Config HP/armor, knockback resistance1 are native defenses.

## Astral golem

Registry material attack/defense factors: installed iron1/1, deepsilver1.2/1.2, unknown/null fallback1 and IronIngot repair. Attack only if !isGolemBlocking: ATTACK_DAMAGE*material factor then native enchant modifyDamage, mob_attack(self); hurttrue gates knockback/post/last-target/sound. Incoming amount divided by material defense before super, with no explicit bypass-tag exception. Final native outgoing hurt scales once, not material factor again. Offhand native SHIELD_BLOCK action plus distant target enables blocking: threshold squared distance>=3*(bbWidth*2*bbWidth*2+targetWidth)+2. Native using/block direction/source bypass and piercing retained, no universal shield immunity. Empty checkFallDamage gives ordinary fall-check immunity. Repair material heal25 only consumes if actual HP changes, creative exempt; one final native heal scaling point.

## Boarwarf

Before super hurt, causing Living aggressor alerts AstralGolems AABB30 replacing targets, even if hurt rejected; creative Player skipped. Avoid query also alerts when nearby Targeting entity targets Boarwarf or Player native credit<=-30, but only idle Golems. Native setTarget/loader change-target admission remains; no direct damage in alert. Astral incoming causing noncreative Player can change credit before hurt result; preserve existing reputation rather than Stage-scale it. Boarwarf server gameTime%40 native heal1 has no combat exclusion. Scale final native heal once. Trade/chat/storage details excluded.

## Luminofish

Successful superhurt from direct Living while swell<=0 on server sets swell20 and target direct attacker. aiStep old swell==10 and target distance<3 performs ordinary melee then Poison60 amp0 regardless melee return; no extra LOS test there. Native addEffect admission remains independent of HP. Luminofish and Luminaris isInvulnerableTo exact HOT_FLOOR OR super; no explicit bypass exception in that first predicate. Both AbyssalFire immune tag already accepted. Keep projectile direct vs causing distinction: shooter is not direct Living on normal arrow hit.

## Snail

ShadowSnail PANIC_CAUSES hit while hide0 sets hide1, resets transition and stops navigation BEFORE super. States1 after>20 ticks ->2, state2 after>400->3, state3 after>20->0. Only state2 divides incoming amount by8 unless source BYPASSES_INVULNERABILITY. Trigger can occur even when native hurt rejects. No additional Stage multiplier on native defense ratio/timers.

## Stranghoul

Direct Living attacker with current main weapon tagged #stranghoul_vulnerable_to doubles incoming amount before super; no damage-type/bypass exception. Exact installed list deepsilver sword,pickaxe,axe,sickle. Existing Hunger/Teary immunity/ranged weapons remain prior packages. EatGoal may start on eat animation or random reducedTickDelay80 when HP/max<.4 or offhand food and damaged. Can supply tagged food when offhand not food; tick32 native heal(nutrition+saturation*3), then eats. Healing is final native heal Stage point; item nutrition/cadence unscaled. No direct HP write. Food acquisition/drop details excluded.

## Spider

NightfallSpider successful super melee adds Glowing NORMAL140/HARD300, none EASY, owner=this; failed melee adds nothing. Inherited Spider rejects Poison then delegates other effects; loader/native addEffect machinery retained. Native spawn-jockey replacement of vanilla Skeleton with LonestarSkeleton preserves that already-reviewed skeleton ranged route, not new damage type. Target/passenger native admission remains.

## Thirst walker

Behavior MeleeAttackPhase20/cooldown10 performs ordinary melee at phase tick7 with horizontal reach2; actual query is TargetingConditions.DEFAULT AABB2 and actual target only. Hurttrue Living adds Hunger140*(int)effective local difficulty amp0 and raises hungerLevel by.6 intentional/.1 otherwise capped1. Intentional attempt independently stops anger/flees for100ticks even when hit false, retry movement every20. Resource decays.001 each server tick; below.3, no target and staggered1200tick interval chooses nearby Player inAABB20 and sets intentional. This resource/AI/control is native, unscaled; ordinary final mob hurt scales once.

## Seeker deer

Seeker aiStep requires alive/AI; attack geometry line5 from center at stored angle intersecting victim expanded box plus sensing LOS. At eligible movement/attack/cooldown state starts attack30/cooldown50, rechecks at attackTicks10 then ordinary Mob melee; no invented projectile. AuroraDeer charge requires target distance<=20, LOS, random1/80, HP/max>=.5 and any antler. Windup80 then captured target point navigation2; every charge goal tick including windup checks AABB+.6 for target, attacks once and ends regardless hurtreturn. While charging nearby LOGS/SNAPS_GOAT_HORN/BASE_STONE_STARLIGHT can probabilistically break antler (1/8, cooldown200), eventually preventing future charge; no block destruction or damage source from antler break. One final mob hurt Stage point, AI/geometry unchanged.

## Registry and exclusions

EntityType.fireImmune native builders: Seeker,TheGatekeeper,StarlightGolem,Freeze,Permafrost,SolarCreeper,TearBomb. Preserve native tag-based fire handling, not blanket resistance to every visually hot custom type. Remaining entity tags pinned for whole-mod disposition. Freeze projectile and alliance/fall behavior already covered; TwilightGaze only ordinary retaliation melee, not gaze damage. ZombifiedRatlin aiStep sunlight ignites8seconds using native sun-burn check, inherits passive Ratlin goals; no fabricated hostile attack. GrimstoneGolem is AbstractGolem with panic/display goals, NOT IronGolem melee. Yeti Brain contains panic/idle/temptation/rolling, no attack activity. Ent,Ratlin,Rookfish,ShimmerLacewing ordinary passive/utility only; Lacewing empty fall check is native fall protection. StarfireBird trust removal on successful player-caused hurt is ordinary trust/avoid AI, no additional damage. Config maxHealth/armor/attack attributes retained; base numeric attacks scale at final native hurt, never both attributes and hit.

## Scope

Static only. Mount, damage, healing, status/Resistance, target-change, source identity and generic Tensura/L2 interactions remain future runtime fixtures. No source fallback, direct HP/SHP edit, production/Stage changes or native eligibility bypass.

## TNO integration decisions

- **Gleech native attachment/summon**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional multiplier; Fixed native defense/control/resources and modifiers remain unscaled; any resulting already-reviewed HP request keeps its own final scaling.
- **Native configured creature melee**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Once at final native mob_attack after attributes/enchantments.
- **Creteor/Tiny native explosions**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Once per final native explosion hurt after radius/exposure.
- **Independent native status cloud/death-effect callback**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional multiplier; Fixed native defense/control/resources and modifiers remain unscaled; any resulting already-reviewed HP request keeps its own final scaling.
- **Creteor native Tiny summon**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional multiplier; Fixed native defense/control/resources and modifiers remain unscaled; any resulting already-reviewed HP request keeps its own final scaling.
- **Aethersent Golem ownerless native magic**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Once at final native magic8 hurt.
- **Aethersent Golem natural meteor interception**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional multiplier; Fixed native defense/control/resources and modifiers remain unscaled; any resulting already-reviewed HP request keeps its own final scaling.
- **Native Golem repair/Boarwarf regeneration/Stranghoul food healing**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Once at each final native heal; preserve event veto and actual-HP-change consumption.
- **Astral material defense and ordinary shield admission**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional multiplier; Fixed native defense/control/resources and modifiers remain unscaled; any resulting already-reviewed HP request keeps its own final scaling.
- **Boarwarf native guard targeting**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional multiplier; Fixed native defense/control/resources and modifiers remain unscaled; any resulting already-reviewed HP request keeps its own final scaling.
- **Luminofish delayed independent Poison**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional multiplier; Fixed native defense/control/resources and modifiers remain unscaled; any resulting already-reviewed HP request keeps its own final scaling.
- **Fish exact native hot-floor immunity**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional multiplier; Fixed native defense/control/resources and modifiers remain unscaled; any resulting already-reviewed HP request keeps its own final scaling.
- **ShadowSnail panic/hide mitigation**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional multiplier; Fixed native defense/control/resources and modifiers remain unscaled; any resulting already-reviewed HP request keeps its own final scaling.
- **Stranghoul deepsilver direct-weapon vulnerability**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional multiplier; Fixed native defense/control/resources and modifiers remain unscaled; any resulting already-reviewed HP request keeps its own final scaling.
- **NightfallSpider native Glowing**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional multiplier; Fixed native defense/control/resources and modifiers remain unscaled; any resulting already-reviewed HP request keeps its own final scaling.
- **NightfallSpider inherited Poison immunity**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional multiplier; Fixed native defense/control/resources and modifiers remain unscaled; any resulting already-reviewed HP request keeps its own final scaling.
- **ThirstWalker native Hunger and intentional flee resource**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional multiplier; Fixed native defense/control/resources and modifiers remain unscaled; any resulting already-reviewed HP request keeps its own final scaling.
- **Native fire/fall traits and sunlight ignition**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional multiplier; Fixed native defense/control/resources and modifiers remain unscaled; any resulting already-reviewed HP request keeps its own final scaling.

[Machine-readable packages, delivery paths and future fixtures](eternalstarlight-r2h7b-creatures.json). Exact archive/method witnesses and targeted semantic assertions are reproducible. No whole-mod completion claim.

Exact next task: R2h8: finish whole-JAR combat caller/disposition coverage (all18 DamageTypes, remaining handlers/mixins/items/entity defenses), deduplicate/promote ES and full validation. Then Bosses Rise static research automatically while usage remains healthy.
