# R2k2a — Cataclysm shared boss admission

Shared Cataclysm native boss hurt/effect admission, damage bucket, self-heal, home/life and death contracts; concrete overrides remain pending.

Static review only. Future runtime fixtures remain unexecuted; whole Cataclysm review is PARTIAL.

## Authority and scope

Six installed Cataclysm class witnesses and patched Minecraft1.21.1/NeoForge21.1.244 pin the shared contracts below. The inheritance index records thirteen classes, including two bases and eleven concrete subclasses. Concrete hurt/cap/phase/immunity overrides remain family work; these contracts apply only when that actual call chain reaches the shared implementation. No boss runtime tests or generic compatibility guarantee.

## Hurt order

Both LLibrary_Boss_Monster.hurt and IABoss_monster.hurt first call virtual isInvulnerableTo(source), rejecting when true. Next, BYPASSES_INVULNERABILITY directly returns super.hurt(source,original amount), skipping the shared cap/range/bucket and self-regen timer bookkeeping. Otherwise clamp amount to min(DamageCap(),incoming), apply causing-entity distance admission/falloff, save the prior bucket, update the bucket unless cataclysm:bypasses_hurt_time, then call super.hurt with the SAME source and selected amount. Successful hurt resets self_regen only for cataclysm:block_self_regen; failed hurt rolls back the bucket. Standard native cooldown, armor, shield, Resistance and event processing remain downstream. A true hurt return is not proof of final HP loss.

## Range

Animation_Monsters.calculateRange reads source.getEntity(), the causing entity, and its CURRENT distanceSquared from the boss. Null causing entity returns -1 and skips this distance gate; direct projectile distance, launch position, source position and LOS are not tested here. Let L=RangeLimit(): distance>=1.5L rejects, distance>L multiplies amount by (1.5L-distance)/(0.5L) and rejects a nonpositive result. Exact L admits without attenuation; exact1.5L rejects. Anonymous environmental damage and projectiles with/without causing owners are distinct native fixtures. Do not invent an owner to change this admission.

## Bucket

Bucket capacity is DamageCap(), NOT DpsCap(). After per-hit cap/falloff, projected=bucket+amount. If projected exceeds capacity: positive remaining room becomes the selected amount and bucket becomes capacity; with no room the code STILL attempts 0.1F damage, leaving bucket unchanged. Otherwise it adds the requested amount to the bucket. It tracks pre-mitigation requests, not measured HP loss. On failed super.hurt it restores the saved bucket. Each server tick with AI enabled drains positive bucket by DpsCap()/20 and clamps negative to0. NoAI prevents decay. cataclysm:bypasses_hurt_time skips only this bucket logic, retaining per-hit cap/range and ordinary native hurt cooldown unless another native tag bypasses that cooldown. No extra Stage multiplier belongs on caps, bucket capacity/drain, distance or the0.1 fallback: preserve this target admission after scaling a real outgoing payload at its producer.

## Defaults and tags

Base DamageCap and DpsCap are Float.MAX_VALUE, RangeLimit Double.MAX_VALUE, NatureRegen0 and HealCooldown200; concrete overrides remain pending and must not be replaced with these defaults. Pinned MC/NeoForge/Cataclysm tag closure: bypasses_hurt_time={abyssal_burn,maledictio_sagitta,shredder,generic_kill,out_of_world,wither,neoforge:poison}; block_self_regen={generic_kill,mob_attack,out_of_world,player_attack}, with unqualified names in their natural Cataclysm or Minecraft namespace as enumerated in evidence. Ordinary arrow/thrown/explosion sources do not reset this shared timer under these shipped tags. Even tag membership does not reset on the early BYPASSES_INVULNERABILITY return. Other pack/datapack tag contributions remain unmeasured.

## Native regen

super.tick runs first. Positive self_regen decrements on both sides, even NoAI. On the server with AI enabled, self_regen<=0 AND NatureRegen()>0 AND target==null AND tickCount%20==0 call heal(NatureRegen()). No extra alive check here; native LivingEntity.heal and NeoForge healing hooks remain authoritative. Future Stage point: ONCE on the positive NatureRegen() amount entering this shared heal call; preserve cadence, target/no-AI/timer gates and native heal admission/max-HP clamp. Never also multiply config or global healing callbacks. Attack-triggered timer reset requires actual hurt=true plus the shipped tag; effect applications do not reset it by this layer.

## Effect whitelist

Both bases require effect.getEffect().getDelegate().is(cataclysm:effective_for_bosses) AND super.canBeAffected(effect). This is a real Holder tag check. The shipped replace=false whitelist has31 values:27 vanilla plus monstrous,abyssal_burn,blazing_brand,ghost_sickness. Poison,STUN,Levitation,SlowFalling and the other eight Cataclysm effects are not included by this resource. Patched addEffect posts NeoForge Applicable: DEFAULT calls the virtual filter, APPLY can admit without that filter, DO_NOT_APPLY rejects. Cataclysm mixin HEAD admission and concrete boss overrides may add gates; these are not resolved by whitelist membership. Preserve native external effect admission, including Tensura/L2 listeners. No scalable value exists in the whitelist.

## Home control

HOME_COOLDOWN is captured at instance construction as CMCommonConfig.ETC.ReturnHome*20 (installed common-file value20 seconds ->400 ticks, not proof of runtime-loaded config). finalizeSpawn initializes homeTicks; the shared base does not establish the actual home position. On server AI ticks, positive homeTicks decrements, any non-null target resets it, and <=0 invokes ReturnToHome when HOME_COOLDOWN>0. With saved home and ServerLevel: cross-dimension home with an existing server level uses native changeDimension and resets timer; otherwise a position not closer than16 to the block center uses moveTo(x+.5,y,z+.5) and resets timer. If destination level lookup fails it can fall through to that same-coordinate move in the current dimension. No additional LOS/collision/ground gate or direct heal is present in this helper. Portal prohibition does not cancel the explicit native dimension call shown. Native hooks downstream remain intact. Home GlobalPos persists; legacy Home doubles load in OVERWORLD. homeTicks,self_regen and bucket are not serialized here; loading begins with their zero defaults unless concrete code changes them. Test restored home/target state separately from fresh finalizeSpawn.

## Life retry

IABoss alone defines synced LIFE default0 and persists LifeRemain. PlayerCounter counts alive, noncreative, nonspectator Players in box.inflate64 with strict distanceSquared<4096, then sets LIFE. awardKillScore for a killed ServerPlayer decrements LIFE when >0, otherwise calls Retry BEFORE super.awardKillScore. Transition1->0 does not itself call Retry; the next credited ServerPlayer kill while0 does. Base Retry is empty. Actual callers and concrete Retry behavior remain boss-family review. This is native retry bookkeeping, not HP/SHP and not a Stage-scalable payload.

## Death and collision

Animation_Monsters.die first allows CommonHooks.onLivingDeath cancellation, then processes only not removed/not already dead. It resolves native kill credit, awards score, marks dead and records combat; server death side effects (including AfterDefeatBoss) additionally require causing entity null OR causingEntity.killedEntity(server,this) true. Server death broadcast follows regardless of that callback result. onDeathUpdate calls onDeathAIUpdate before incrementing deathTime and server removal at the chosen duration. IA defaults20; LLibrary uses death animation duration-20 or20, with concrete combat death callbacks deferred. Ordinary IA collision pushes contain no damage/effect, use horizontal native motion and canBePushedByEntity; IABoss returns true. Both bases prohibit riding/portals and ordinary far/peaceful despawn. These lifecycle/ordinary collision facts add no Stage value; special attack knockback remains at its concrete producer.

## Configuration and boundaries

setConfigattribute applies native transient ADD_VALUE modifiers baseHP*hpConfig-baseHP and baseAttack*damageConfig-baseAttack, then initializes health to max. This is construction/configuration, not an independent heal delivery; concrete constructor use remains pending. Keep native configured attack damage as the input to any future one-time payload scaling. Rendering/animation-only/loot/progression utility is excluded; actual death combat callbacks remain in scope. Research changes no production, source identities, HP/SHP, Stage or eligibility.

- **Shared boss cap, causing-distance and request bucket**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Native target admission, bookkeeping or lifecycle; no separate payload for Stage.
- **Successful tagged-hit native regen cooldown**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Native target admission, bookkeeping or lifecycle; no separate payload for Stage.
- **Targetless native boss regeneration**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Once on positive NatureRegen() heal argument in the shared tick call; retain native cadence, gates and heal hooks.
- **Shared boss whitelist and native effect admission**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Native target admission, bookkeeping or lifecycle; no separate payload for Stage.
- **Native boss home timer and teleport**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Native target admission, bookkeeping or lifecycle; no separate payload for Stage.
- **Native IA player-count and retry resource**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Native target admission, bookkeeping or lifecycle; no separate payload for Stage.
- **Native boss death admission and delayed removal**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Native target admission, bookkeeping or lifecycle; no separate payload for Stage.

[Machine evidence, packages and native paths](cataclysm-r2k2a-shared-admission.json).

Exact next task: R2k2b: Cataclysm status/control and global event admission. Begin STUN and both LivingEntityMixin addEffect overloads, Unbreakable Skull cooldown, attack/use/jump/target hooks; then the other eleven registered effects and real native producers. Concrete boss overrides/attacks and equipment remain pending. Continue automatically while quota is healthy; static only.
