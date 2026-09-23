# R2g4 — Gorgon combat semantics

Static subsection COMPLETE; Ice & Fire PARTIAL. Four mechanic packages and eleven materially distinct paths; no runtime or implementation.

## Gaze entry

Gorgon.aiStep follows super, decrements positive playerStatueCooldown, and works on the current target. Gorgon/prey Blindness and deathTime gate forced Mob look control; the stare goal can also force Mob look. Mutual IafEntityUtil.isEntityLookingAt(...,0.4), !isBlindfolded(target), neither participant Blindness, no rejecting BlacklistedFromStatues, deathTime==0, SCARE animation tick>10, server side and cooldown==0 admit conversion. SCARE starts on eligible mutual gaze; no proof of 10 uninterrupted gaze ticks is implied. Cooldown is assigned40 and target cleared after conversion; it is not serialized by this class. No direct target-current-HP or creative check occurs at this final gaze block: native acquisition, LOS and subsequent player hurt still matter.

## Gaze geometry

isEntityLookingAt multiplies degree by 1+0.1*looker.distanceTo(seen); normalized view dot normalized eye-direction must exceed 1-degree/eyeDistance. It then requires looker.hasLineOfSight(seen) and seen not StoneStatue. Exact LivingEntity LOS requires same level, eye distance<=128 and COLLIDER/Fluid.NONE ray MISS. Both directions are checked. Stare goal15block squared-distance/20seen ticks control navigation/strafe, not an additional final petrification range. Gorgon.isTargetBlocked returns COLLIDER/Fluid.NONE ray !=MISS; its sole installed caller is DragonUtils.getBlockInTargetsViewGorgon, which has no installed direct caller. Do not substitute this unused positioning helper for actual gaze LOS.

## Gaze order

aiStep builds and attempts to add statue BEFORE victim disposal. addFreshEntity return is ignored. Player hurt uses causeGorgonDamage(this), float2147483648 (rounded integer-max float), discards hurt result; direct=causing=Gorgon. Thus rejected player damage can coexist with a statue. Non-player remove(KILLED) does not call hurt/die, emit this DamageSource, or directly subtract HP/SHP. Native entity removal callbacks still occur; no generic damage/death-hook guarantee is invented.

## Head entry

GorgonHead.use starts use, sets ACTIVE and returns SUCCESS; use duration72000, empty onUseTick. releaseUsing has no minimum charge-time test. A32block eye/view segment queries expanded entity bounds; no block ray or LOS check. Candidates Living, pickable, !deadOrDying, !Blindness, !IMMUNE_TO_GORGON_STONE, no rejecting BlacklistedFromStatues, and Player or DragonUtils.isAlive. That helper additionally excludes model-dead dragons/IDeadMob/StoneStatue; it is not itself the generic HP check. Unlike gaze, Head does not invoke isBlindfolded, so native blindfold equipment, BLINDED and the compat helper are not automatically Head gates.

## Head order

Nearest inflated-AABB segment selection preserves shared-root-vehicle rules. If an AABB contains the ray origin, code sets best distance0 WITHOUT selecting that entity; do not copy Siren Flute behavior. Player hurt is first, using causeGorgonDamage(pointedEntity): direct=causing=VICTIM, not wielder or item. Only hurt==true admits statue creation; true is not proof of death or HP loss. Non-player server remove(KILLED) precedes statue construction; success flag remains true. Server spawn return is ignored. A selected Living target consumes one Head for noncreative Player user even when player hurt rejects; no selected target consumes none. ACTIVE removed at end. Player hurt/item consumption has no whole-method server guard; only non-player removal and statue spawn are explicitly server gated.

## Native admission

R2g1 GORGON resource: only scoped bypasses_armor/bypasses_shield, no bypass_invulnerability/cooldown/resistance/effects/enchantments. Exact ServerPlayer hurt checks invulnerability, spawn protection and causing-Player canHarmPlayer, then Player ability invulnerability, death, difficulty scaling and Living incoming/shield/cooldown/reduction/death/totem hooks. Head self-attribution therefore enters player-PVP/team checks against the victim itself; PVP disabled rejects. Gaze has Gorgon attribution. Neither gigantic requested amount nor hurt=true certifies death, SHP loss or Nullification bypass. Non-player conversion never reaches this damage admission at all.

## Immunity

Native isBlindfolded: nonnull target with HEAD blindfold item OR Blindness OR BLINDED entity tag. Installed BLINDED lists deathworm,dragon_skull,mob_skull. IMMUNE_TO_GORGON_STONE declares optional #c:bosses/#neoforge:bosses plus warden; final merged tags are runtime data, not this static list. Native gaze itself does not read IMMUNE tag, but installed tensura_iaf HEAD cancellable isBlindfolded injection returns true for that tag or SkillUtils.isSkillToggled(ABNORMAL_CONDITION_NULLIFICATION). Protected helper requires instance toggled and mastery>=0; it does not perform ResistSkill.canInteractSkill here. Head checks IMMUNE tag directly but does not call this helper. Cockatrice,DeathWorm,DragonEgg,DragonSkull,Ghost,MobSkull,StoneStatue return false from canBeTurnedToStone; Cyclops returns !isBlinded. No assumption that every boss is immune without tag membership.

## Compatibility

Existing required compat mixins classify exact GORGON as abnormal and not physical. Ordinary player hurt still traverses actual Tensura/NeoForge/L2 pipelines; final interactions require runtime tests. Non-player remove can avoid damage-based defenses because that is the installed native route; research does not add or authorize a bypass. IafHandler rejects nonnull MobEffect additions to StoneStatue via Manas LivingEffectAdded. That is not a veto of statue creation/removal. Native Head versus gaze differences must survive future integration.

## Fallback melee

setTarget invokes parent then chooses server melee/stare goals using own/target Blindness, rejecting blacklist OR isBlindfolded(target), provided deathTime==0 for melee. doHurtTarget has narrower poison predicate: own Blindness OR CURRENT target Blindness OR rejecting CURRENT target blacklist, and deathTime==0. Mere blindfold/tag/compat immunity switches AI but does not alone grant poison. If predicate passes, animation HIT starts and actual Living entityIn gets Poison100ticks amplifier2 before parent Monster/Mob.doHurtTarget; addEffect result ignored, poison not gated by melee hurt. Parent uses current ATTACK_DAMAGE(base3), native mob_attack, enchantment modification then hurt; accepted-hit knockback/postattack retains native result gate. Poison ticks use installed NeoForge poison holder (native magic fallback), source without entity,1requested HP when HP>1, interval25>>2=6; independent normal effect admission/removal/cures and damage hooks remain.

## Statue state

buildStatueEntity creates a separate stone_statue LivingEntity; non-Player saveWithoutId snapshot attempted (exception caught), Player trapped NBT empty; stores registry type,width,height,age scale. It does not preserve a live prisoner or implement timed release. Defaults pig,emptyNBT,.5width/.5height,scale1,cracks0. Saves CrackAmount int but reloads getByte; saves/reloads dimensions,scale,type,tag. No native resurrection path in reviewed statue consumers. Item restore creates another statue, not trapped creature; resets cracks0. ServerEvents player attack repairs statue to maxHP before tool logic, increments cracks for MAINHAND PICKAXES and removes at>9, interrupting attack; other player attack interrupts default. Silk-touch storage/replacement is a short persistence disposition, not a new combat family.

## Statue defense

StoneStatue.hurt first checks source IS_PROJECTILE && amount>0; if so it optionally awards server XP from newly constructed trapped type, removes KILLED and returns true BEFORE parent hurt. No owner/causer requirement, HP subtraction, hurt-hook or invulnerability check in this branch. Non-projectile/zero amount delegates LivingEntity.hurt. isInvulnerable() returns true, but exact Entity.isInvulnerableTo reads its FIELD rather than calling that override; do not claim universal statue damage immunity. baseTick/push are empty, kill removes, and canBeTurnedToStone=false. Ordinary non-projectile damage/loaded Invulnerable field and external overrides require separate runtime observation.

## Excluded

Rendering/statue pose/sounds, Head acquisition/crafting/lore and ordinary storage cosmetics excluded. Statue NBT/item restoration retained only to distinguish persistence from resurrection and admission state. Gorgon prolonged cosmetic death, utility data/components and unconnected positioning helpers receive no separate deep review. Troll sunlight uses the shared statue constructor but its trigger belongs to the later Troll family.

## TNO decisions

Binary petrification, huge execution proxy, statue deletion/cracks and immunity gates receive no numeric Stage multiplier. Ordinary melee and Poison use their existing native damage routes exactly once; Poison remains an independently admitted effect. Exact per-package integration points and future fixtures are in [the machine-readable review](iceandfire-r2g4-gorgon.json). No scaling is implemented or production behavior changed.

## Validation

Reproduce installed native/reference witnesses and whole-JAR predicate/caller census; assert conversion ordering and hurt-return dependencies, source argument distinction and actual invulnerability field dispatch; preserve prior accepted records/evidence; five tooling tests and diff checks. This is bounded subsection validation, not a new whole-catalog completion claim.

Exact next task: R2g5: Dragons combat review: shared native attack/admission, fire/lightning breath and charge payloads, melee specials, age attributes and defenses. Reuse R2g1 factories and R2g2b Frozen/charge routing unchanged; no runtime/L2/Stage/production work.
