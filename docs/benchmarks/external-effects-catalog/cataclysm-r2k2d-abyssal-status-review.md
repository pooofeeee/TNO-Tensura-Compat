# R2k2d — Cataclysm Abyssal DOT and teleport

Abyssal Burn/Curse status DOT/control and application/filter slices; complete beam/tentacle families pending.

Static review only. Future runtime fixtures remain unexecuted; whole Cataclysm review is PARTIAL.

## Scope

Fifteen installed class witnesses, three selected loader classes and existing pinned source factory/tags establish Abyssal Burn/Curse DOT, Burn teleport and their effect-side native producers. Thirteen status-reference methods and exactly two ABYSSAL_BURN DamageType field-reading caller methods are indexed. This closes two more effect cores (seven of twelve total), not Leviathan beams or Tidal launch/chain family completion.

## Dot source

EffectAbyssal_Burn.applyEffectTick and EffectAbyssal_Curse.applyEffectTick both request hurt(damageSources().source(CMDamageTypes.ABYSSAL_BURN),1.0F). Native source(ResourceKey) constructs an anonymous DamageSource: direct=null,causing=null, no effect applier rewrite. Both use40>>amplifier cadence (positive interval -> duration modulo interval==0, otherwise every tick); normal amp0..4 yield40,20,10,5,2ticks. Java int shift semantics still apply at unusually high amplifier values; do not extrapolate an unbounded halving rule. Burn stores hurt boolean for secondary teleport; Curse ignores it and returns true. Neither directly subtracts HP/SHP.

## Source tags

cataclysm:abyssal_burn is USED by the two status methods, native JSON exhaustion0.1,scaling=never. Pinned shipped closure: cataclysm:bypasses_hurt_time, minecraft:bypasses_armor, bypasses_shield, no_knockback, panic_causes. No IS_FIRE, BYPASSES_COOLDOWN, BYPASSES_EFFECTS, BYPASSES_RESISTANCE or BYPASSES_ENCHANTMENTS in this closure. Thus this is not ordinary fire damage despite the name; native Resistance/protection and event admission remain downstream. Shared boss custom hurt-time tag skips only its bucket, with cap/range retained; anonymous source skips causing-distance gate, while ordinary hurt cooldown can still reject repeated1-point requests. Other pack tag/trait changes are future runtime work.

## Single stage point

Future Stage belongs ONCE at each of these two native status hurt amount boundaries, replacing the positive1.0 payload while retaining native key, null actors, cadence, effect admission, hurt-return branch and downstream mitigation. Burn/Curse share one deduplicated DOT mechanic package but two callback paths. These are independent new constant requests, not fractions of already-scaled parent beam/tentacle damage. Do not additionally scale duration/amplifier, stack limit, probability, teleport radius or parent damage again. How to carry legitimate originating Stage context into an anonymous delayed DOT remains an explicit future integration decision; never solve it by assigning a false damage owner.

## Teleport gate

Only Burn: after native hurttrue, sample random.nextFloat() < 0.75 - CURRENT_HP/MAX_HP, then require server side. Current HP is after hurt/callbacks; at>=75% ordinary positive maxHP the threshold is nonpositive, below75% it increases with missing HP. No extra alive/teleport-immunity/entity-type predicate is added in this method. Hurtfalse never enters random teleport. A successful hit can trigger an attempt even without equal measured HP loss; keep boolean/HP/position separate.

## Teleport attempts

Up to8attempts choose X/Z=current+(randomDouble-.5)*8 and Y=currentY+randomInt(8)-4, clamped to server minBuildHeight..minBuildHeight+logicalHeight-1. Each attempt dismounts passengers before testing success, emits native TELEPORT game event, constructs EntityTeleportEvent.ChorusFruit and reads its target coordinates, then calls local randomTeleportInwater. This method does not post that ChorusFruit event to the NeoForge bus or check its cancellation; the pinned event constructors just store entity/coordinates. The game event is not the cancellable NeoForge event. Do not claim that native ChorusFruit listeners can veto this unposted object; ordinary downstream teleport/mixin interactions remain runtime concerns. No fix is implemented.

## Teleport destination

Local helper requires hasChunkAt candidate, searches down until a blocksMotion block below while above minimum height, calls living.teleportTo(candidateX,adjustedY,candidateZ), then tests level.noCollision. It has NO liquid rejection check, unlike an inference from ordinary dry teleport. Failure restores the starting position and returns false; already performed dismount/game event are not rolled back. Success optionally broadcasts46, stops PathfinderMob navigation, returns true; caller plays sound and stops retrying. No Stage factor belongs to this binary control path, attempt count or displacement.

## Burn application

Both Abyss_Blast_Entity.tick and Portal_Abyss_Blast_Entity.tick process beam hits after tickCount>20 on the server. For each ray-selected Living target with non-null caster, target!=caster and !caster.isAlliedTo(target), request native deathlaser via causeDeathLaserDamage(beam,caster), amount=D+min(D,targetMaxHP*HpDamage*.01). Only hurttrue obtains old Burn amp, directly removeEffectNoUpdate when present, sets new amplifier=clamp(oldAmp+1,0,3) or0 if absent, and requests Burn160 with null effect-source. The original source has direct beam/causing caster; the subsequent DOT has neither. Beam ray/phase/spawn details remain full-family review. Discard/visual-off timing is not assumed to short-circuit the current tick body.

## Curse application

Tidal_Tentacle.tick requires Living creator and non-null current target; server progress>=5 and even tickCount enter hit logic, refetch a Living creator, require current!=creator and native mobProjectile(tentacle,creator) hurt(getBaseDamage()) true. Then it casts current to LivingEntity, removes old Curse with removeEffectNoUpdate, increments/clamps amp0..4 (absent->0), and requests Curse60 with null effect-source. The hit block does not independently require !isRetracting; native target selection normally supplies Living candidates, and full chain/launcher eligibility remains its family review. The effect-side gate must not be broadened to arbitrary synthetic targets or a fabricated caster.

## Stack removal

removeEffectNoUpdate directly removes the activeEffects map entry. It skips normal removal event/cleanup and its result is not a gate on the following addEffect. The replacement addEffect still uses ordinary admission. If replacement is vetoed, the old Burn/Curse is already removed. These two effects have no attribute modifiers, but native event/removal observations still differ from normal update/refresh. Preserve this behavior and record it; do not make the catalog a repair. Blessed Amethyst tick removes Burn through normal removeEffect, but does not cleanse Curse.

## Immunity checks

Leviathan.canBeAffected compares getEffect()!=EFFECTABYSSAL_BURN.get() before shared super; eight concrete creatures (the seven STUN-filter classes plus Hippocamtus) similarly compare Curse Holder to EFFECTABYSSAL_CURSE.get() MobEffect value. These identity comparisons do not match native Holder objects, so the specific exclusions are ineffective. Remaining super/native Applicable admission still applies: shared boss whitelist includes Burn but omits Curse. Do not infer that all effects are always accepted or silently replace native checks with intended immunity. Native STUN same-DeferredHolder identity checks fromR2k2b are a different case.

## Boundaries

All status damage actors/types, parent source distinctions, admission, resistance, cooldowns, hurt-return dependencies, raw replacement and native teleport constraints stay intact. No fake damage source, direct HP/SHP edit, Stage implementation, runtime/L2 test, production edit or Phase6/7 change. Future fixtures cover native delivery and external hook/tag composition.

- **Native Abyssal Burn/Curse anonymous DOT**: COMPOSITE, CUSTOM_ROUTED, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Once on positive1.0 amount at each original EffectAbyssal_Burn/EffectAbyssal_Curse.applyEffectTick hurt call; same native anonymous source, no cadence/parent duplication.
- **Hurt-dependent native Abyssal Burn teleport**: COMPOSITE, CUSTOM_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Native control, status stacking and admission remain fixed.
- **Native Abyssal status replacement and eligibility**: COMPOSITE, CUSTOM_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Native control, status stacking and admission remain fixed.

[Machine evidence, packages and native paths](cataclysm-r2k2d-abyssal-status.json).

Exact next task: R2k2e: remaining five Cataclysm status cores and application slices: Monstrous, Blazing Brand, Bone Fracture, Curse of Desert, Wetness. Trace numeric heal/magic DOT, modifiers, native stacking/removal and combat input. Reuse completed status/shared contracts; full originating boss/projectile/equipment families remain pending. Static only; continue while quota healthy.
