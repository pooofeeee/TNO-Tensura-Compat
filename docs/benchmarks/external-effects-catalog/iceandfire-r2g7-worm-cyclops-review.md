# R2g7 — Death Worm and Cyclops combat

Death Worm/Cyclops combat and Cyclops Eye complete; other Ice & Fire creature/equipment families pending.

Static subsection complete. Runtime fixtures unexecuted; no Stage or production implementation.

## Worm melee

DeathWorm attack goal starts with target,!vehicle,ground-or-sand,cooldown; tick target+LOS+distance<3 calls doHurtTarget. That method starts Bite if needed, independently rolls explosion and returns false. aiStep at Bite tick5, current target and distance<min(4,4*ageScale) requests current ATTACK_DAMAGE via mob_attack direct=causing=Worm; no second LOS at damage frame, hurt return ignored, self Yvelocity-=.4 independent. Rider controlbit2+Player passenger tick uses protected rider ray(range3, native team filters/no world LOS) and immediately requests int ATTACK_DAMAGE through same Worm mob_attack, NOT rider source; can repeat each update while held. Mounted interaction requires wormAge>4, rider no vehicle and fishing rods in both hands; no tame/owner requirement. C2S control requires riding relationship, but Worm case has no owner check. Do not fabricate packets.

## Worm attack explosions

AI doHurtTarget random1/3,ageScale>1,mobGriefing true and Iaf ON_GRIEF_BREAK_BLOCK not vetoed constructs BlockLaunchExplosion at target, radiusageScale. Roll is outside new-animation guard and may repeat while bite already active. Rider new Bite animation random1/3 and ageScale>1 constructs explosion at forward offset1.5*scale below eye, radius.75*scale; this path has NO mobGriefing/Iaf grief predicate. Both pass Worm with null explicit DamageSource: exact Explosion defaults yield minecraft:player_explosion direct=causing=Worm (name does not imply Player). Inherited protected damage/visibility/knockback algorithm and onExplosionDetonate run, but manual construct/explode/finalize skips Level onExplosionStart. Existing BlockLaunch finalizer does not spawn its constructed FallingBlock. No extra FallingBlock damage path.

## Worm tnt

Registered DeathwormAITargetItemsGoal searches dropped nonempty TNT item on SAND below, random1/10, follows nearest; continuation live item/different team/inrange. At distanceSquared<1 consumes1, starts Bite and calls setExplosive(true, resolvedPlayer). Owner is ItemEntity.getOwner UUID resolved to Player, else null. Setter ignores boolean parameter, sets willExplode=true,countdown60,thrower. aiStep decrements to0; at0, if Iaf grief event not vetoed calls Level.explode(thrower, wormPosition, radius2.5*ageScale,false,MOB), then clears thrower. It NEVER clears willExplode or resets/decrements zero, so subsequent live aiSteps can request another explosion with null source. No unconditional self kill. First Player source gives player_explosion direct=causing=Player and excludes that Player from explosion entity query; later null source gives ownerless explosion and can hit Worm. Native death/admission can terminate repetition. Save retains WillExplode but not countdown or thrower; new instance resumes60/null. TNT Level route includes onExplosionStart, onExplosionDetonate and canEntityGrief block-mode selection; mobGriefing false does not inherently suppress entity damage. All actual damage/knockback remains native.

## Worm defense resources

Reject exact IN_WALL/FALLING_BLOCK, and current controlling passenger-caused damage while vehicle; canBeTurnedToStone=false. Empty checkFallDamage suppresses native fall path, not arbitrary FALL hurt calls. SlowPart segments use protected parent route with multiplier1. AgeScale=min(baseScale*max(1,wormAge)/5,7), native maxHP=max(6,config10*scale), attack=max(1,config3*scale), speed=min(.2,.15*scale), armor3. Tame killedEntity heals14 and returns false, wild returns true. Young age<5 after growthCounter>1000 increments age, heals15, then setDeathWormScale -> updateAttributes -> setHealth(baseMaxHP), bypassing heal event and filling HP. Reload also calls scale setter before restoring age then recalculates attributes; do not promise unchanged HP on reload. Spawn/growth baselines are not extra Stage healing; retain lifecycle fixture because direct full-HP reset can conflict.

## Cyclops melee grab

doHurtTarget random3 selects Stomp/Kick/Eat and returns true without immediate HP damage. Eat requires victim not carrying Cyclops,width<1.95,not Dragon and !CYCLOPS_UNLIFTABLES; stops old ride then startRiding(Cyclops,true), return ignored. Force still passes cycle/already-riding and NeoForge mount admission; no bypass authorized. positionRider while passenger zeros horizontal motion, positions at mouth, forces Eat animation; tick32 requests configbiteDamage(snapshot40) mob_attack direct=causing=Cyclops and stopRiding regardless of hurt. Native dismount hook may veto. aiStep Stomp tick14 rangeSquared<12, Kick tick12 rangeSquared<14 request ATTACK_DAMAGE(snapshot15); Kick knockback2 independent of hurt and ordinary knockback hook/resistance applies. No frame LOS predicate. Native melee goal custom checkAndPerformAttack has reach test and blinded distance>=6 stop, no attack-cooldown check in its override. Roar is sound/animation only, unlike Dragon roar.

## Cyclops eye

Eye is a parent-routing part, not separate HP. Its hurt checks exact DamageTypes.ARROW, not IS_PROJECTILE and not owner/direct entity class. For Cyclops parent+ARROW calls onHitEye then returns true unconditionally. If not already blinded, onHitEye sets saved Blind=true, followRange6,speed.35,Roar then parent.hurt(originalSource,amount*3), ignoring result. Thus blindness/petrification exclusion can change even if HP hurt rejected. Already blinded ARROW to eye returns true and does NOT forward HP. Other types forward unchanged to parent and return parent hurt; no local part multiplier. isBlinking(tick%50>40) is visual and NOT hurt admission. Blind aiStep clears target beyond squared6, distinct from AI distance6. canBeTurnedToStone=!blinded. Save reload restores boolean but does not call onHitEye/followRange6; setter only data flag. Generic client player multipart path remains separate from server projectile eye route; no synthetic arrow source.

## Cyclops target and aura

Native target filters live nonstatue/nonwater/not Cyclops/not sheep; most ordinary Animals excluded except Wolf/PolarBear/Dragon; creative/spectator Player excluded. Separate nearest Player/retaliation and sheep attack alarm also exist. CyclopsAITargetSheepPlayersGoal predicate alwaysfalse: name is not proof of sheep-disguise functionality. CyclopsEyeItem while exact stack in main/offhand scans Mob in +/-15 cube, no LOS, !self,!allied and target==holder OR lastHurtByMob==holder OR Enemy. Attempts Weakness10ticks amp1. Marks a tick consumed if any eligible Mob even if effect rejected; after counter>120 hurts stack1 using current used-hand slot and resets0. Counter DataComponent persists perstack; unequipped inventory tick can still process an already>120counter. No custom DamageType or direct HP here; no Stage value on weakness/cost.

## Compatibility and scaling

Native mob_attack, arrow and explosion identities plus normal armor/effect/hurt/knockback/heal admission are retained. No direct SHP write or per-family Tensura override identified in protected compatibility foundation. Numeric attack/explosion damage is scalable once at final target.hurt amount; never scale radius, native body size, part multiplier or Cyclops x3 again. Knockback/grab/blinding and Weakness remain native binary/control. Native heal14 has one heal-event amount boundary; growth/full-HP initialization is a lifecycle baseline, not scalable absolute HP. TNT repeated requests and changing source require future runtime event-count tests, not a static fix.

## Shared callback clarification

R2g6 onLivingSetTarget name is misleading: IceAndFire registers it on EntityEvents.START_TRACKING_TAIL, so chicken alarm has a Player-starts-tracking delivery as well as Player ATTACK_ENTITY. Retain this explicit delivery distinction in final promotion; do not reinterpret it as a vanilla mob target-change event.

## Exclusions

Sand navigation, loot/egg acquisition, growth progression except HP reset, structure generation, sounds, render/blink, home storage and sheep-follow utility excluded. World block breaking has no added falling-entity damage; explosion HP/cover admission retained. No runtime tests or fixes.

## TNO integration decisions

- **Death Worm/Cyclops native body HP damage**: NUMERIC_SCALABLE, VANILLA_ROUTED, ADMISSION_GATED. Stage: yes; Once at each native target.hurt amount (worm aiStep/tick, Cyclops aiStep/positionRider), after native attribute/config selection.
- **Death Worm attack and TNT explosions**: NUMERIC_SCALABLE, VANILLA_ROUTED, ADMISSION_GATED. Stage: yes; Once at inherited Explosion target.hurt final damage amount after native radius/visibility formula; never multiply radius or source creation.
- **Cyclops grab/kick displacement**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional value; Native mount/position/knockback/dismount and independent HP result.
- **Cyclops arrow-eye blinding and native vulnerability**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional value; Keep binary blindness/native x3; ordinary parent damage receives Stage once after native x3, no extra part scaling.
- **Death Worm immunity and multipart routing**: BINARY, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional value; Keep native source/controller/statue exclusions and multiplier1 parent routing.
- **Tame Death Worm kill heal14**: NUMERIC_SCALABLE, VANILLA_ROUTED, ADMISSION_GATED. Stage: yes; Once at killedEntity heal(14) amount through native LivingHealEvent.
- **Death Worm age/size HP reset**: CUSTOM_ROUTED, NO_STAGE_VALUE. Stage: no additional value; Native growth/reload baselines; never multiply absolute maxHP reset.
- **Held Cyclops Eye Weakness aura**: VANILLA_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional value; Vanilla Weakness modifies native attacks; no extra multiplier on amplifier/duration/counter.

[Machine-readable packages, native paths and future fixtures](iceandfire-r2g7-worm-cyclops.json). Validation reproduces new witnesses, checks significant call order/amounts, preserves accepted records and prior evidence, runs five tooling tests and diff checks. No whole-mod completion claim.

Exact next task: R2g8: remaining creature combat, prioritize Ghost/Troll/Myrmex, then Hydra/Sea Serpent/Stymphalian/Amphithere and combat-special mounts; equipment and whole-mod closure/promotion follow. Static only.
