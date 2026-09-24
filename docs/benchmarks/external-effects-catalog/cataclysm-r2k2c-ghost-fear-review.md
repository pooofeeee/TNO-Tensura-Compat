# R2k2c — Cataclysm Ghost, Fear and Blessing

Four status cores plus Cursium revival and Blessed Crab food paths; full Leviathan damage/launch families remain pending.

Static review only. Future runtime fixtures remain unexecuted; whole Cataclysm review is PARTIAL.

## Scope

Four effects (Ghost Form, Ghost Sickness, Abyssal Fear, Blessing of Amethyst), native Cursium chestplate rebirth and associated food healing are reviewed. Nine installed class witnesses, three selected loader classes and the accepted native food/Regeneration dependency pin the contracts. All12 field-reference methods have a disposition. Full Abyss Mine/Orb launch and Leviathan attack schedules remain family work; their effect-side delivery is distinguished here. Together withR2k2b, five of twelve Cataclysm effect cores are reviewed.

## Rebirth

LivingDeathEvent handler first requires source NOT BYPASSES_INVULNERABILITY, then tryCursiumPlateRebirth. Recipient must be in ServerLevel, wear exact CURSIUM_CHESTPLATE in CHEST, and have neither Ghost Sickness nor Ghost Form. It setsHealth(5), requests Fire Resistance200amp0, requests Ghost Form100amp0 (ambient=false,particles=true,icon=true), then returns true so death is canceled. The native setHealth clamps to[0,maxHP]; it is a fixed revival state, not heal(5) and not a LivingHealEvent. Abyssal Fear therefore does not veto this assignment through BlockHeal. Preserve fixed5 and binary death admission, no Stage multiplier on this state reset. No item consumption/durability or separate timer is used by this helper.

## Rebirth effect failures

Neither addEffect return controls revival success. If Ghost Form admission fails, health reset and death cancellation still happen; no guaranteed protection or future Sickness follows. Its only repeat-prevention checks here are current Form/Sickness presence. Early removal of Form or failed Form/Sickness admission can therefore permit another native chestplate revival once neither is present. Do not fabricate a cooldown/resource or repair this path. Preserve death-event composition with other mods and maxHP clamp; event priority/other listeners can affect runtime.

## Ghost form

Beneficial Ghost Form adds MOVEMENT_SPEED +0.4*(amplifier+1) ADD_MULTIPLIED_TOTAL under cataclysm:ghost_speed. ServerEventHandler cancels LivingIncomingDamageEvent while recipient has Form unless source BYPASSES_INVULNERABILITY. It also cancels the Player attack event and use-item Start, and sets base use-item event duration0. No Form canAttack mixin, no direct entity NoAI/noPhysics, and no universal prohibition of already-scheduled/direct hurt producers are present in this slice. Rendering transparency is cosmetic. Binary immunity/actions and speed/duration stay native; no extra Stage.

## Ghost expiry

EffectGhostForm.shouldApply stores its argument in the registered effect object lastDuration and returns argument>0. applyEffectTick requests Ghost Sickness7200amp0 with particles=false/icon=true only when stored argument==1. Native finite MobEffectInstance.tick calls shouldApply with remaining duration, immediately calls apply, then decrements, so ordinary100tick Form attempts Sickness on its last tick before expiry. It is not an on-remove callback: early cure/explicit removal does not itself schedule Sickness. For native infinite instances the argument is recipient.tickCount, not remaining duration, so do not generalize to a universal expiry trigger. Normal native tick ordering is pinned; no concurrency effect inferred.

## Sickness

Harmful Ghost Sickness has no damage, movement modifier or resource drain in applyEffectTick (returns true); its combat role is the rebirth presence gate. The50>>amplifier callback cadence does not imply periodic damage. fillEffectCures is empty rather than calling the default extension, so native instances start with no ordinary cure entries. removeEffectsCuredBy requires the cure to exist in that set before the removal event. Thus ordinary cure-based removal is excluded by that mechanism; it is distinct from explicit removeEffect/removeAllEffects.

## Removal mismatch

ServerEventHandler.preventEffectRemoval compares effectInstance.getEffect() == ModEffect.EFFECTGHOST_SICKNESS.get(). The first is a Holder; the second is the registered EffectGhost_Sickness MobEffect value, which is not that Holder. Its identity test is false for the native effect instances, so this listener does NOT prevent explicit removal. Patched removeEffect/removeAllEffects still post normal removal events and other listeners can veto. Natural expiry is not prevented by this code. Keep empty cure-set admission and ineffective explicit-removal listener separate; no immunity repair is authorized.

## Fear

Abyssal Fear is harmful and its own tick does no damage. BlockHeal cancels LivingHealEvent whenever recipient has Fear, irrespective of heal amount/amplifier/source and without a new duration/amplifier scaling rule. Native LivingEntity.heal passes through EventHooks.onLivingHeal before adding HP, so normal healing, Regeneration and boss heal calls are subject to this veto. Direct native setHealth state changes such as Cursium rebirth do not route through heal. Do not describe Fear as blocking every possible HP increase or bypass its veto with a fallback.

## Mine delivery

After server warmup decrements below-20, Abyss Mine enumerates LivingEntities intersecting its box inflated(.2,0,.2). explode(candidate) requires candidate alive. With resolved Living caster, it excludes caster/allies, calls native Level.explode(caster,...,radius1,NONE), then applies Fear200amp0 with null effect-source and discards. Without caster it explodes using mine entity and still applies Fear200amp0. The Fear request is NOT gated by explosion damage success and occurs after blast; there is no second alive check. The enclosing candidate loop has no break/removal guard, so multiple captured candidates can still call this method; retain a future multi-target fixture rather than assuming one blast. Caster UUID and warmup persist, caster resolves server-side; unresolved owner follows the actual caster-null branch. Full damage/source closure and originating summons stay in Leviathan review.

## Orb delivery

Abyss Orb entity impact invokes super then, server-side, rejects Leviathan/LeviathanPart hits only when current owner is Leviathan. With Living owner it requests native mobProjectile(orb,owner), amount getDamage(); otherwise anonymous native magic with getDamage(). Only hurttrue plus Living victim applies Fear100amp0 with native getEffectSource (owner or orb). Afterward native radius1 explosion using owner and discard occur regardless of hurt result in this admitted impact branch. Thus contact Fear, contact HP and explosion HP are independent observations; block impacts have no Fear call. Owner/alliance/launch/secondary blast source details remain projectile family review; no fabricated source.

## Blessing

Blessing of Amethyst is beneficial; every positive-duration tick independently checks and attempts native removal of Abyssal Burn, Abyssal Fear and vanilla Darkness in that order. Removal return is ignored, so vetoed effects can be retried on subsequent ticks; other statuses are untouched. It neither prevents initial application nor grants blanket immunity. Same-tick effect iteration order can determine whether a healing/DOT tick happens before cleanse; runtime must observe rather than assume priority. Shared boss whitelist omits Blessing and Fear/Form while including Sickness, subject to actual concrete/native/external admission.

## Food

Exact blessed_amethyst_crab_meat ModItems supplier lambda$static$226 installs native food effects Regeneration100amp0 and Blessing1800amp0, each chance1, and alwaysEdible. Its subclass adds only foil/tooltip; native food addEffect admission remains. Regeneration is a separate native heal1 callback at50tick cadence for amp0 when HP<max, subject to heal veto/max/alive processing; reuse the accepted vanilla Regeneration contract. Future Stage belongs once on that positive native heal amount, not food effect duration, application chance, modifier or cleanse. Blessing may remove Fear before later regeneration, but same-tick heal success is not promised.

## Compatibility

No new DamageType belongs to these four effects themselves. Parent mine/orb HP stays at each original native producer and is deferred rather than multiplied at Fear application. Keep event cancellation, cure-set eligibility, native holder/value mismatch, death cancellation, source identity, fixed revival HP and effect add/remove returns intact. Future fixtures remain NOT_RUN; no runtime, L2, Stage, production, Phase6 or Phase7 change.

- **Native Cursium chestplate revival state**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE, CUSTOM_ROUTED. Stage: Native binary control/admission, fixed revival state, effect duration/modifier or presence resource.
- **Ghost Form native immunity/actions and expiry delivery**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE, CUSTOM_ROUTED. Stage: Native binary control/admission, fixed revival state, effect duration/modifier or presence resource.
- **Ghost Sickness cure set and revival exclusion**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE, CUSTOM_ROUTED. Stage: Native binary control/admission, fixed revival state, effect duration/modifier or presence resource.
- **Abyssal Fear heal-event veto and delivery**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE, CUSTOM_ROUTED. Stage: Native binary control/admission, fixed revival state, effect duration/modifier or presence resource.
- **Blessing of Amethyst selective native cleanse**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE, CUSTOM_ROUTED. Stage: Native binary control/admission, fixed revival state, effect duration/modifier or presence resource.
- **Blessed food native Regeneration healing**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE, VANILLA_ROUTED. Stage: Once on positive native RegenerationMobEffect.applyEffectTick heal(1) amount, preserving HP/cadence/effect and heal-event admission; no additional food/status scale.

[Machine evidence, packages and native paths](cataclysm-r2k2c-ghost-fear.json).

Exact next task: R2k2d: Cataclysm remaining seven statuses: Monstrous, Blazing Brand, Abyssal Burn, Bone Fracture, Abyssal Curse, Curse of Desert and Wetness. Trace numeric/DOT/source and event modifiers plus real application sites. Reuse shared boss, STUN and Ghost/Fear contracts; full bosses/projectiles/equipment remain pending. Continue automatically while quota healthy; static only.
