# R2k2b — Cataclysm STUN admission and control

STUN effect-side contract and native application sites; full originating boss/projectile/charge families remain pending.

Static review only. Future runtime fixtures remain unexecuted; whole Cataclysm review is PARTIAL.

## Scope

STUN core, effect-side delivery/admission, native action hooks and all34 installed EFFECTSTUN field-reference methods are indexed. Twenty-two Cataclysm class witnesses and ten patched MC/NeoForge reference classes plus vanilla DamageSources are pinned. This closes the STUN slice only: full originating boss state machines, helper invocation parameters, Accretion launch and Wall Watcher construction/scheduling remain their family review. No boss family or whole mod is marked complete.

## Effect core

cataclysm:stun is HARMFUL. EffectStun registers MOVEMENT_SPEED ADD_VALUE -0.5 with IDcataclysm:stun_speed. Native AttributeTemplate.create multiplies by amplifier+1; e.g.amp0=-0.5,amp1=-1.0 before normal attribute bounds. Tick callback returns true without damage/motion; shouldApply tests duration>0. No forced NoAI or unconditional entity freeze. Duration/amplifier, movement modifier and binary restrictions remain native and receive no Stage scalar. Independently generated HP at its real attack producer remains a separate future scaling point.

## Action gates

LivingEntityMixin canAttack(LivingEntity) HEAD returns false when SELF has STUN, not when its proposed target has STUN. It affects callers of that admission method; it does not prevent every direct hurt call or every already-scheduled attack. ServerEventHandler cancels AttackEntityEvent, LeftClickBlock (two handlers), EntityInteract, RightClickBlock, RightClickItem, block placement by a stunned LivingEntity, and BreakEvent by a stunned Player. LivingJump sets current Y velocity to0 while retaining XZ. LivingEntityUseItemEvent.Start is canceled and the base use-item event handler sets duration0; this is not a proof that all Stop/Finish callbacks are canceled. The same Start method also computes food duration; other modifiers and event ordering remain runtime composition. No damage source is fabricated.

## Left click and target

LeftClickEmpty has an empty initial STUN branch, then !hasEffect guards native ILeftClick calls for both held stacks and sending the MAIN_HAND swing packet. MessageSwingArm.handle enqueues the indicated held ILeftClick call without its own STUN check. Therefore normal event delivery is gated but that packet handler is not an independent STUN admission guarantee; retain a future in-flight packet test. The LivingChangeTargetEvent handler in this artifact checks lava-monster/helmet/last-attacker rules, not STUN; no direct target clearing or target-change cancellation is proven for STUN. Its camera shaking is a short cosmetic exclusion.

## Skull

Both addEffect overloads inject at HEAD and call the same helper. SELF must be Player; effect.getEffect().equals(ModEffect.EFFECTSTUN); EntityUtil.isEquipped must find the exact UNBREAKABLE_SKULL in CuriosApi.getCuriosInventory(...).findFirstCurio(item); and Player ItemCooldowns must report not on cooldown. It then adds900ticks cooldown and returns false BEFORE native Applicable/merge/attribute insertion. Hand/inventory possession alone is not this Curios lookup. No source, amount, damage or alive check is added here. No server-side-only guard. Failed/redundant attempts can consume this cooldown even if later native admission would reject. It rejects the incoming attempt; it does not remove existing STUN.

## Overloads and equality

The one-argument native addEffect delegates to the two-argument overload with null source. If the outer HEAD rejects, delegation never occurs, so one attempt does not consume two cooldowns. If cooldown is already active, both HEAD hooks pass through and ordinary admission follows. Direct two-argument delivery goes through one HEAD. MobEffectInstance preserves its supplied Holder and getEffect returns it; patched Holder.Reference and DeferredHolder equals both accept the same reference ResourceKey. Thus Skull uses semantic holder equality and recognizes ordinary registered-holder STUN as well as the native DeferredHolder. Other mixins/listeners can still affect final runtime outcomes.

## Post damage removal

ServerEventHandler.onLivingDamage consumes LivingDamageEvent.Post and attempts removeEffect(STUN) when CURRENT HP <= event.getNewDamage() and STUN present. Both patched LivingEntity and Player actuallyHurt call Post AFTER native health subtraction; newDamage is the container final damage value. This is not just a lethal-hit test: e.g.preHP10,actual damage6 -> remaining4<=6, so removal is attempted while alive. Existing absorption/mitigation precedes this comparison; external healing/HP changes at callbacks can alter it. Native removeEffect veto and cleanup remain. No extra damage or HP refund is generated. For producer callbacks that add STUN only after hurt returns, this earlier Post check cannot remove that newly applied instance; it may remove a preexisting instance first.

## Effect immunity

Shared boss whitelist fromR2k2a omits STUN, subject to native Applicable and concrete overrides. Seven other canBeAffected methods (Cindaria,Clawdian,Coralssus,Aptrgangr,Kobolediator,Prowler,Wadjet) compare getEffect()!=ModEffect.EFFECTSTUN by REFERENCE IDENTITY before super. Native new MobEffectInstance(ModEffect.EFFECTSTUN,...) retains the same DeferredHolder and is rejected by this check; an equal-key but different Holder object can pass this particular identity check. Do not convert this to unconditional type immunity or silently repair it. These same methods compare Abyssal Curse to .get() value; that separate effect belongs toR2k2c. Native effect admission, external Applicable overrides and Tensura/L2 interactions remain future fixtures.

## Damage dependent applications

Server Guardian.AreaAttack, Ignis.BodyCheckAttack, Leviathan.biteattack, Ancient_Remnant.AreaAttack/TailAreaAttack apply STUN only after their native mobAttack hurt returns true AND supplied duration>0, amplifier0 and one-argument addEffect (null effect-source). Native DamageSource direct=causing=the mob. Ignis body formula attackAttribute*damage + victimMaxHP*hpdamage; Guardian/Remnant use base+min(base,victimMaxHP*hpdamage); Leviathan bite uses1.5*attack + min(1.5*attack,victimMaxHP*TentacleHpDamage). The helper native candidate/arc/alliance/same-class gates are pinned, not replaced; exact animation selection and caller-provided durations remain each boss review. STUN admission can fail even after HP succeeds. Shield-disable/airborne/launch ordering must stay native, not be inferred from status success.

## Independent roars

Ignis.aiStep has two server STUN60amp0 applications independent of hurt: BREAK_THE_SHIELD tick55 and SHIELD_BREAK_STRIKE tick17. It queries native nearby LivingEntities with12 extents/radius, whose helper additionally excludes self, tests distance<=radius+candidateWidth/2 and candidateY<=selfY+height; no LOS check. It excludes allied targets and Players with abilities.invulnerable. Animation entry prerequisites remain Ignis-family work. These are separate fixtures from damage-gated body check.

## Parry

Hippocamtus.hurt applies STUN50amp0 to a DIRECT Living attacker during native parry: source not BYPASSES_SHIELD, AI enabled, attackState4, non-null source position, source-to-self normalized horizontal vector dot view<0, attackTicks7..17 inclusive. It sets block_stage1, server addEffect, and returns false for incoming hurt, including when direct entity is not Living (then no STUN). This status explicitly occurs on rejected HP damage, with no invented projectile-owner promotion. Later parry phases belong to creature review.

## Accretion

Accretion.onHitEntity server: with Living owner, target!=owner and !owner.isAlliedTo(target) -> native mobProjectile(this,owner) with getDamage(); successful hurt triggers alive-target enchant post effects and discard, then Living victim STUN40amp1. Without a Living owner, it instead requests native inWall5 (anonymous source) and successful hurt can still apply STUN40amp1. Effect source is native getEffectSource(): current owner if non-null, otherwise projectile itself; it need not equal the anonymous damage causing entity. Native mobProjectile uses minecraft:mob_projectile with direct projectile/causing owner; do not relabel it thrown. Native contact/launch and full projectile lifetime are deferred, not fabricated.

## Wall watcher

Wall_Watcher server tick requires a non-null stored Living source and watch list, otherwise discards. A watched victim horizontalCollision and !victim.isAlliedTo(source) sets invulnerableTime0 BEFORE requesting native mobProjectile(watcher,source), amount=damagePerEffectiveCharge*effectiveChargeTime+1. Only hurttrue applies STUN50amp0 (null effect-source); collision removes that watched entry regardless of hurt success/alliance. Noncolliding entries keep native forced motion, not a STUN application. Timer and native constructor remain charge-family review; reload clears source, so this is not a persisted owner repair. No change to iframe behavior is made.

## Boundaries

All durations, modifiers, chances, native holder identity/equality, source fields, hurt booleans and Curios cooldown remain native. STUN restriction/removal and Skull rejection packages have no separate Stage value. No direct HP/SHP write, runtime boss/L2 test, fallback source, production or Phase6/7 change. Full numerical attack packages are deferred to prevent duplicate Stage on the status and parent hit.

- **Native STUN movement/action control and delivery**: COMPOSITE, CUSTOM_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Preserve native status/control duration, attribute modifier and admission. Parent native HP is a separate future one-time payload boundary.
- **Unbreakable Skull incoming-STUN rejection**: COMPOSITE, CUSTOM_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Preserve native status/control duration, attribute modifier and admission. Parent native HP is a separate future one-time payload boundary.
- **Native post-damage STUN removal attempt**: COMPOSITE, CUSTOM_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Preserve native status/control duration, attribute modifier and admission. Parent native HP is a separate future one-time payload boundary.

[Machine evidence, packages and native paths](cataclysm-r2k2b-stun.json).

Exact next task: R2k2c: Cataclysm remaining eleven effects and associated global hooks, starting Ghost Form/Ghost Sickness and Abyssal Fear; then numeric DOT/status and native producers. Reuse R2k2a shared admission and R2k2b STUN contracts. Full concrete boss animation/parameter schedules, attacks and equipment remain family work. Static only; continue while quota healthy.
