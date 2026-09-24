# R2j5 — Bosses of Mass Destruction Nether Gauntlet

Nether Gauntlet native part admission, awakening, attacks, control/heal and explosion/fire semantics complete; whole BOMD PARTIAL.

Static review only. Future runtime fixtures remain unexecuted; whole Bosses of Mass Destruction review is PARTIAL.

## Scope

Nether Gauntlet combat semantics complete from16 native witnesses, installed CerbonsAPI multipart/EventSeries paths and exact Minecraft/NeoForge references. This reviews actual eye admission and native attacks, not a runtime boss matrix. Existing production and Phase6 remain locked.

## Hitbox admission

GauntletHitboxes.shouldDamage captures nextDamagedPart then clears it for EVERY attempt. If MiscUtils.isModLoaded(bettercombat) OR epicfight at helper initialization, returntrue from this handler. Otherwise eye part OR BYPASSES_INVULNERABILITY passes. For null/non-eye part and no bypass, IS_EXPLOSION also passes when nonnull source.getSourcePosition yields vector(sourcePos->GauntletEye) with dot(lookAngle)<=0; perpendicular boundary is included. DamageSource.getSourcePosition uses explicit source position, otherwise direct entity current position, otherwise null; it is not necessarily the explosion center. This is a front-side source-position test, not a shield_piercing exemption or a per-victim amount cap. Remaining cases reject; nonprojectile causing Living attacker receives native knockback.5, fire-tagged sources only suppress clink sound. Earlier shared before/after hooks remain and remaining native super.hurt admission applies. The compatibility toggle does not disable every native defense.

## Parts

Open-hand native EntityBounds includes eye and fingers/thumb/pinky/root shapes. Closed fist has rootFist/rootFistYaw and NO eye. Geometry follows entity yaw/pitch/position; setOpenHandHitbox/setClosedFistHitbox sends native ChangeHitboxS2C. Thus genuine closed-fist geometry cannot supply an eye part, but invulnerability bypass/front explosion/compatibility-toggle rules still apply. GauntletClientEnergyShieldHandler only renders isEnergized particles/alpha; it is not a separate damage shield or charge resource. Preserve actual part selection rather than setting eye by a harness shortcut.

## Projectile part delivery

Required CerbonsAPI ProjectileMixin injects at Projectile.onHit HEAD. On EntityHitResult whose victim is MultipartAwareEntity, it raycasts victim.getBounds from projectile.position to position+deltaMovement and passes the returned part string to setNextDamagedPart. EntityBounds.raycast chooses the nearest intersecting named part. It does not fabricate a DamageSource or multiply amount. Genuine vanilla projectile impact/deflection/cancellation and projectile-specific superclass calls must reach this hook; a raw target.hurt call does not supply a part. Missing ray hit writesnull; consumed field does not grant persistent eye admission.

## Melee part delivery

Client MultiPlayerGameMode attack HEAD raycasts camera eye/view to ENTITY_INTERACTION_RANGE. If nonnull part, sends native MultipartEntityInteractionC2SPacket; nonspectator locally sets part, attacks and resets attack ticker, cancels original client method. Server packet requires nonclient side and sender, resolves entity id, writes native part through MultipartAwareEntity and calls ServerPlayer.attack(entity). It does not directly subtract HP or create substitute damage. The pinned packet body does not perform its own server raycast/reach check; research fixtures must use genuine native ray/packet delivery, not inject a part. Ordinary non-multipart/generic attack callbacks are separate missing-part fixtures. Runtime mixin application/packet registration still needs observation.

## Aggro and defense

GauntletGoalHandler starts isAggroed=false; its afterDamage activates goals only on hurt resulttrue, once, and writes/loads isAggroed NBT. Rejected body attempts do not wake it. Base moveHandler denies ordinary move until aggro. Player target acquisition then uses existing FindTargetGoal visibility/range controls. Native getArmorValue is24 while no target, otherwise superclass installed armor8 before modifiers; HP250,attack16. Registry fireImmune, fall callbacks disabled, isInWall=false. Poison/Wither holder mismatch remains R2j2. Unlike other bosses, targetless server tick directly calls heal(config idleHealingPerTick=.5), with no milestone cap; native heal admission/max HP still applies.

## Move selection

After aggro, ActionGoal runs alive+target, initial cooldown80. Cancel supplier for attacks is deadOrDying OR current targetnull. Regular punch weight1; laser weight.7 only HP ratio<.85 and not previous move8; swirl weight.7 only ratio<.7 and not previous10; blindness weight1 only ratio<.5 and absent from last-four move history. These are native current-ratio selection gates, not TNO Stage or forced one-shot rage transitions. Exact equality at thresholds excludes the corresponding move.

## Punch

Punch captures target-based overshoot point, attempts native block clear, pushes bossY+.7. Close fist delay7, accelerate from16 for15 updates (.6 first then.32, stop near target squared distance<9 or cancel), active impact from16 for40 updates, stop animation56, reopen64 without cancellation. Each active callback tests block collision then entity overlap then records current speed as previousSpeed; previousSpeed field persists between moves. Collision horizontal/vertical AND previousSpeed>.55 requests actor-source native explosion strength(previousSpeed*normalPunchExplosionMultiplier), installed multiplier1.5. No once-per-punch explosion flag. Entity impact queries Living entities in current native bounding box excluding boss only, calls Mob.doHurtTarget then unconditionally target.addDeltaMovement(bossVelocity*.5), even on hurtfalse. No target-only/team/LOS predicate or per-target hit cache.

## Swirl

Swirl sets isEnergized=true and bossY+.7, closes fist7, accelerates30 for15 updates (.6 then.4), active impact30 for30, reopens60 and clears energized without cancellation. Entity contact uses same native melee and independent extra velocity. First qualifying block collision while energized requests actor-source explosion configured4.5 with fire=true, then clears energized; later collisions use speed*1.5 firefalse. Native isEnergized changes explosion mode, not a separate absorption shield. Counts, velocity, hitbox timing and explosion strength remain native.

## Melee and laser amount

Punch/Swirl native Mob.doHurtTarget selects mob_attack direct=causing Gauntlet, current ATTACK_DAMAGE with server EnchantmentHelper.modifyDamage, then victim.hurt. Success gates native knockback/postattack/lastHurt bookkeeping; extra punch velocity outside helper is unconditional. Laser ALSO calls this same melee helper. Per selected laser victim it temporarily adds id bosses_of_mass_destruction:laser, ADD_MULTIPLIED_BASE=-.25 to ATTACK_DAMAGE, calls doHurtTarget, then removes modifier regardless boolean. With otherwise unmodified attack16 this contributes12 before native enchantments; it is not a separate magic/fire DamageType. Single future scaling point for all is final native Mob.doHurtTarget hurt amount after native attribute/enchantment selection; do not scale temporary modifier and helper together.

## Laser delivery

Laser captures a Living target, builds HistoricalData(Vec3.ZERO,8), then EventSeries: delay25 start target-id sync;60 updates of position recording/application; final uncancelled stop clears history/id and emits stop event. EventSeries advances through removed/canceled members and preserves final cleanup, not parallel scheduling. After seven captured positions, list size first reaches8 and oldest is still initial Vec3.ZERO, so first application aims along that direction; thereafter oldest is a lagged target center. At most54 applications in an uncanceled60-update recording stage; no claim of54 hits. Extend eye->selected position to length30, block clip COLLIDER/Fluid.NONE truncates beam to hit location; every even boss tick attempts tiny-AABB native block clearing. FindEntitiesInLine uses segment AABB and each candidate bounding-box clip, excludes boss, then selects Living; no extra team/current-target-only filter. Native helper damage/cooldown repeats determine actual HP loss.

## Block clear

Despite destroyBlocks name, installed helper destroys ONLY nonair block equal to Blocks.FIRE, with mobGriefing true and not WITHER_IMMUNE. It does not clear stone or general cover, or soul fire. Laser therefore does not tunnel through ordinary solid cover via this helper. This binary native gate is relevant to delivery; no worldgen/utility archaeology or bypass is proposed.

## Blindness

BlindnessAction closes fist10, reopens43 without cancellation. At delay30 with normal cancel supplier, collects native nearby Players using TargetingConditions.forCombat.range64 and AABB inflated64/32/64. Native conditions retain canBeSeen, attacker canAttack/type/alliance, visibility-adjusted range, and mob LOS. If list nonempty send cosmetic indicator packet, then after50 more with normal cancel supplier addEffect(Blindness140,amp0) to CAPTURED players; it does not requery LOS/distance/team at application. Native addEffect admission remains, no hurt or HP prerequisite. Packet itself only calls client particle handler; it does not apply an independent status.

## Explosions and fire

Punch and energized collision explosions have direct=causing Gauntlet and native minecraft:player_explosion; preserve earlier engine admission/exposure/independent native vector. Energized fire=true can place native fire at eligible affected air blocks above solid-render support with native one-in-three choice. BaseFireBlock.getState selects ordinary or soul fire from below-block state. Native in_fire contact amount comes from that block instance (ordinary1,soul2), plus ignition and later on_fire ticks1 through native Entity.baseTick; source identities remain anonymous fire, not Gauntlet damage sources. Fire immunity/Resistance, native timers and normal damage hooks still govern actual HP. Do not assume every fiery explosion places a block or burns a victim, and do not scale strength/radius/timers.

## Death

Native custom deathServerTick increments deathTime; exactly50 creates Level.explode(null,currentPos,4,MOB), then optional debris/loot and experience (excluded), then remove(KILLED). Unlike punch explosions, direct and causing entities are null, so source is minecraft:explosion, not player_explosion. Config spawnAncientDebrisOnDeath controls loot, not this explosion. Native explosion eligibility/mitigation still applies. Preserve anonymous identity: infer no killer/boss owner or fallback entity.

## Stage and followup

Scalable numeric families here are native melee (including laser), native explosion HP, native environmental fire HP, and uncapped native targetless heal. Apply once at their terminal native amount boundaries; preserve eligibility/state/counts/source identity. For anonymous Gauntlet death explosion, resulting fire and already-reviewed unowned summoned Phantoms, generic source type alone cannot identify BOMD origin. Any future scaling must establish narrow native origin context without changing owner/source; provenance remains an explicit future integration review item, not unresolved static behavior. All eye/part, aggro, phase selection, client rendering, timers, blindness and raw velocity remain unscaled. No Stage code, production fix, runtime boss/L2 test or Phase6/7 work.

- **Native Gauntlet eye/source-direction admission**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Native admission/phase/count/control/scheduling, no independent scalable HP payload.
- **Native Gauntlet awakening and movement admission**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Native admission/phase/count/control/scheduling, no independent scalable HP payload.
- **Native uncapped targetless healing**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Once at GauntletEntity native heal argument; preserve target-null and native healing admission/max HP.
- **Native Gauntlet contact and laser melee**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Once at Gauntlet Mob.doHurtTarget final victim.hurt amount after native attribute/enchantment formula; laser modifier stays native.
- **Native extra punch victim motion**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Native admission/phase/count/control/scheduling, no independent scalable HP payload.
- **Native attributed or anonymous Gauntlet explosions**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Once at attributed native Explosion.explode per-victim final hurt amount; preserve strength/geometry/source and independent displacement.
- **Native lagged laser geometry and phase sequence**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Native admission/phase/count/control/scheduling, no independent scalable HP payload.
- **Native delayed Blindness**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Native admission/phase/count/control/scheduling, no independent scalable HP payload.
- **Native environmental fire damage**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Once on the native fire contact/timer terminal hurt amount with separately proven origin context; preserve anonymous source, fire eligibility and timers.

[Machine evidence, packages and native paths](bomd-r2j5-gauntlet.json).

Exact next task: R2j6: BOMD Void Blossom native multipart admission/retaliation, spikes/waves/spore ball/leaf blade, spawned healing blossoms and native boss death effects. Reuse shared/RiftBurst/part-delivery contracts. Then bounded combat equipment and whole-mod coverage/deduplication/promotion. Static only; continue automatically while quota is healthy.
