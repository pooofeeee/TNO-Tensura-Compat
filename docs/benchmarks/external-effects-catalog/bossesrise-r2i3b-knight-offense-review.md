# R2i3b — Bosses Rise Knight offensive payloads

Knight offensive native payloads and independent arena-mob combat; Knight complete with protected defense section, whole mod PARTIAL.

Static review only. Future runtime fixtures remain unexecuted; whole Bosses’ Rise review is PARTIAL.

## Live scope

Knight server tick executes attacks only outside animation transition. Its MeleeAttackGoal.canPerformAttack override returnsfalse, so no extra ordinary AI melee is invented for the boss. Actual producers are tick melee/SwordWave/Rift plus jumpSlash->SoulShockwave. attackCombo1 is genuinely called; older attackJumpspin1 has zero installed invocation callers, so its17.5base shockwave is excluded. SoulShockwave static convenience shoot overloads have no external native static callers; do not invent a player delivery. SwordWave also has a real KnightSwordItem.releaseUsing producer, reserved for equipment review using this payload contract.

## Melee

All native boss melee uses protected shared helper: final damageScale*ATTACK_DAMAGE then native enchantment damage, mob_attack boss/boss, hurttrue required for outward push and consumer. Real variants(full box side,forward reach,push,scale): intro timer28/light1timer10/light2timer18=(6,7,1.5,1) plus getOutOfMe(7,0,1,1); heavy23=(5,7,2.5,1) plus getOutOfMe; light-heavy8=(6,7,1.5,1),37=(5,7,2.5,1), eachplusgetOutOfMe. Combo2 timers38/79/118=(14,2.5,1.5,1),98/125=(6,2.5,1.5,1). Thrust timers46..60=(4,9,.2,.5); native block clearing requires mobGriefing and destroySpeed>0<50, no extra blast. Recovery knocked_down_to_idle timer20=(10,0,3.5,.1). One final helper multiplier, no Stage on boxes/counts/push or attack attributes.

## Combo ring

attackCombo1 computes A=158-timer. Melee A122/76/58=(6,2.5,1.5,1); A108/94/62=(14,2.5,1.5,1); A30=(8,2.5,3,1). For A<29 within livecombo, nb2=2+(18-A)*.1, loop round(18*nb2) points around forward4 at radius2*nb2, angular incrementnb2. Each point queries .5full-side Living AABB excludingboss then requests ownerless new DamageSource(IN_WALL),12. No block support/LOS/hurt-success/once-per-target set; native iframes remain. This is actual ring damage, not native suffocation detection or a Level explosion. Scale each admitted final in_wall request once; no radius/counter multiplier.

## Wave delivery

Horizontal ranged timer14 creates SwordWave ownerKnight,noGravity,baseDamage5,knockback0,silenttrue atY+.5; scale4 at patternIndex2 else2. Index4 additionally creates scale2 wave timer24 atY+1.5. Vertical timer7 creates5/7/9 waves for ordinary/index3/index5; verticaltrue,scale default1,ownerKnight,base5,speed2,spread yaw(30-1.5*count)*i degrees. shoot flattens velocityY and renormalizes to original speed; hitbox vertical scales width.25*scale,height12*scale, horizontalnormal*scale. These geometry/count variants share one HP formula, no separate geometry Stage scaling.

## Wave payload

SwordWave tick clips COLLIDER/noFluid then custom nearest entity ray against targetBB inflated(2,0,2), broadBB expandedvelocity+1; native canHitEntity retains canBeHitByProjectile and leftOwner/same-vehicle admission. Native Player-vs-Player canHarmPlayer and ProjectileImpactEvent veto preserved. Final HP=ceil(clamp(currentSpeed*baseDamage,0,INT_MAX)), native indirect_magic directwave/causingowner elsewave. Living owner records lastHurtMob beforehurt. Hurttrue non-EndermanLiving receives native Slowness60 amp1 and configured KB (native producer0); hurtfalse restorespriorfirecounter. isOnFire alwaysfalse/fireImmune true makes copied ignition branch dormant. No post-enchantment damage/callback added by this class. Wave survives entity contact (no per-target set), drag.99, discard onblock/deflection/server or timer>=200. Override deflect discards and returnstrue, no ownership change/reflection. Save retains native Projectile owner plusTimer/Vertical/WaveScale; baseDamage/knockback are not saved and reloaddefault2/0, distinct futurefixture. Yeti-owner reaction exists inpayload but no nativeYeti wave producer proven; not promoted as Yeti delivery.

## Shockwave

jumpSlash creates native AbstractArrow-derived SoulShockwave ownerKnight,baseDamage21,speed1 aimeddown; jump1 timer38offset0; jump2 additionally56offset3; jump3 additionally49offset3,70offset7. DirectEntityhit exactowner skipped; others first run native AbstractArrow.onHitEntity: arrow source directprojectile/causingowner elseprojectile, ceil(speed*enchantment-adjusted baseDamage), native crit/pierce/fire/iframe/deflection rules. Knight factory sets no fired weapon and no crit flag. Success hooks native; doPostHurtEffects decrements embedded-arrow count back, knockback fielddefault0. Then custom onHitSomething executes regardless direct hurt success or super Enderman return/discard. Blockhit also executes it. Server6full-side AABB centeredPROJECTILE.position selectsLiving except ALL UnderworldKnight: explicit new DamageSource(EXPLOSION,this,getOwner),4 with resultignored; independentSlowness100amp1 to area; directLiving target getsSlowness100amp2 even ifarrowhitfailed. Then discard. No Level.explode, exposure/block destruction/native blast impulse; source is explosion (notplayer_explosion). Arrow and independent area request each scaleonce at their own final hurt; neither is damage-derived. Native iframes may prevent combined HP despite both attempts; effects have separate Applicable admission.

## Rift

Revenge timer24 creates Rift atKnightY+5, ownerKnight and currenttarget. Native timer120 countsdown; server even timer108..22 inclusive withnonnullowner/target emits44 projectileattempts (40normal,4Big at100/80/60/40), each ownerKnight/target/speed1.2/upwardspread25. No alive/LOS requirement in emitter. Entity storesTimer only: reload loses owner/target and suppresses further emissions. Projectile homes toward transienttarget while incrementedtimer<20, retains speed, zero gravity; discards>=60, inwater/bubble or BBcontainsnoair; native ray/canHitEntity/ProjectileImpact/deflection remain. Entity hit owner-excluded requests ownerless magic2; hurttrue server post-attack enchantment callback; serverdiscard independentofhurt. Big invokesparent then, for nonownerLiving, Slowness100amp1 regardless hurtreturn. Native Projectile owner persists but homingtarget doesnot. Ownerless damage is deliberate native source identity despite projectile owner; no attributed fallback.

## Arena mobs

SoulSkeleton and SoulKnightWitherSkeleton extendMonster, not vanillaSkeleton/WitherSkeleton, and have NO ownable attribution. Registered native eggs/placement paths deliver real mobs; Knight/Rift code has no summon caller. They targetPlayer/HurtByTarget via native AI. Ordinary MeleeAttackGoal checksattackcooldown, distance²<ownwidth²+targetwidth, LOS -> inherited Mob.doHurtTarget with current attackattribute/enchantmentformula andnative mob_attack mob/mob. Separate baseTick procedures also attack currenttarget through box-only timers: Skeleton cooldown>=15 -> targetwithin2.75inflate startsanim20; at14 targetwithin3inflate andattackeralive -> native mob_attack currentATTACK_DAMAGE(default6). WitherKnight cooldown>=30 ->same start; at10 targetwithin3.5inflate ->attribute(default8). Cooldown accumulates only when currenttargetwithin8inflate; no LOS or nativeordinarymelee cooldown synchronization inprocedure. Both apply .2lookhorizontal+.1Y motion independentlyofhurtreturn. Therefore ordinary melee andprocedure are distinct real HPattempts, not a duplicate to remove. Single final hurt peractualpath; never scale attribute plusboth paths.

## Wither and defense

WitherKnight procedure adds Wither100amp1 when attacker(notvictim) is NOTblocking, attacker alive and victimLiving onserver; ignores melee hurtreturn. Wither source ownerless minecraft:wither1 every40>>amp ticks (20 atamp1); native immunity/Applicable anddamage mitigation remain, scale finaltickamount once, no status duration/amplifier scaling. Both mobs fireImmune=true; Skeleton explicitlyrejectsIN_FIRE; WitherKnight additionally rejects exactWITHER/WITHER_SKULL damage (not blanket MobEffect rejection). Entity undead tags are pinned infoundation; inherited effectadmission retained. Attempt to clear Knight ascurrenttarget uses null instanceof LivingEntity, alwaysfalse; no actualowner/alliance protection inferred. Knight cinematiccleanup discards both mobtypes ininflate64 withoutowner test. Skeleton deathprocedure particles/soundsonly, noextraHP/explosion/summon.

## Source profiles

Seven native types pinned with resolved scoped tags. mob_attack/arrow are Neo physical, arrowprojectile; indirect_magic/magic/wither Neo magic and bypassarmor+shield, while indirect_magic is NOTis_projectile despite wavegeometry. in_wall is Neo physical/environment and bypassarmor+shield. explosion is IS_EXPLOSION/no_knockback, notarmor/shieldbypass. None ofthese seven bypassResistance/effects/enchantments/invulnerability/cooldown inthisclosure. All native difficulty policies are when_caused_by_living_non_player except explosion ALWAYS; ownerlessmagic/ring/wither have no causingLiving despitepolicynaming. Keep exact actualsource andnativeResistance/L2 classification, not visual soul/magic/projectile labels. Wholepacktag/eventorder untested.

## Tno and exclusions

Review completes Knight combat together with R2i3a; native modifier/stack/mark/phase packages preserved. Nine numeric package candidates below include aliases tosharedboss/nativeMobhurt for finaldedup; no implementation approved. Statusadmission/nativeowner/lifecycle are fixed control. No runtime/L2/Stage/production/Phase6/7 work. Cosmetics, sounds, loot, ordinaryacquisition/worldgen excluded quickly; realeggs are named only as honest futurecreature delivery. Do not runtime-call orphan helpers or manufacture sources.

- **Knight live native melee variants**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Reuse shared_boss_attack final native hurt amount once.
- **Knight native suffocation-typed ring damage**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Once at final in_wall12 hurt; retain native iframe and geometry.
- **Native SwordWave attributed indirect magic**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Once at final ceil(currentSpeed*baseDamage) indirect_magic hurt.
- **SoulShockwave native arrow contact**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Once at inherited AbstractArrow final arrow hurt after native speed/base/enchant/crit formula.
- **SoulShockwave independent explosion-typed area damage**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Once at each independent explicit explosion4 hurt, retaining native admission.
- **Rift native ownerless magic**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Once at final ownerless magic2 hurt.
- **Arena mobs ordinary native melee**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Once at inherited Mob.doHurtTarget final native amount after attribute/enchantments.
- **Arena mobs independent timed native melee**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Once at procedure mob_attack(current ATTACK_DAMAGE) hurt; never also multiply attribute.
- **Native Wither damage tick**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Once at native WitherMobEffect final wither1 hurt; no amplifier/duration multiplier.
- **Native Slowness application variants**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Native control/status/duration/admission/geometry or source prerequisite; no additional Stage value.
- **Native Rift emitter/homing/lifecycle**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Native control/status/duration/admission/geometry or source prerequisite; no additional Stage value.
- **Arena mob independent movement and defense**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Native control/status/duration/admission/geometry or source prerequisite; no additional Stage value.

[Machine evidence, packages and native paths](bossesrise-r2i3b-knight-offense.json).

Exact next task: R2i4: Infernal Dragon combat-significant native defense/phases, collision melee, magic/fire/breath/fire-area/projectile callbacks and guardian attacks. Reuse complete Knight/shared/roll contracts. Do not repeat Knight or begin runtime/L2/Stage/production work. Then Yeti, Sandworm, Kraken/cannon, remaining combat equipment and closure.
