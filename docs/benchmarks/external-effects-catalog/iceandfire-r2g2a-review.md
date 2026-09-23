# R2g2a — Frozen core and ordinary weapon deliveries

Ice & Fire remains **PARTIAL**. This is a bounded static subsection; full dragon delivery closure is next. No permanent implementation or runtime testing.

## Authority

Installed IceAndFireCE2.0-beta.15, exact NeoForge21.1.244, installed Tensura2.0.1.1 and tensura_iaf2.0.0.1 plus the parent-hash-bound nested ManasCore skill4.0.0.2 archive. Method bytes control findings; source aids locate branches. R2g1 sources/tags are reused. No runtime or mixin-application certification.

## Core

iceandfire:frozen is NEUTRAL, not HARMFUL, and requests applyEffectTick every eligible remaining-duration tick. Amplifier is unused. Ordered core: IceDragonEntity or dead/dying returns false; otherwise on fire clears fire then returns false; otherwise creative Player returns true without motion; otherwise multiplies current delta x/z by0.25 preserving y; then non-EnderDragon airborne recipients add y=-0.2; returns true. IceDragon/dead admission occurs before extinguishing. EnderDragon only escapes the extra downward term, not horizontal damping.

## Not damage

The entire Frozen class has no hurt, HP subtraction, freezing-gauge write, attribute modifier registration, setNoAi, movement lock or custom DamageSource. This is repeated velocity modification. Ordinary entity travel/input/gravity later in the tick can change motion again; it does not prove a fixed final speed. Existing Slowness/MiningFatigue in weapon delivery are separate vanilla effects, not effects of Frozen itself.

## Tick order

LivingEntity.baseTick calls tickEffects; LivingEntity.tick calls its Entity superclass tick/baseTick route before aiStep and travel. The callback modifies the velocity present at that point. A Frozen instance can exist on an IceDragon/creative recipient until native processing; the tick branch is not a custom addEffect admission veto.

## Native admission

Frozen producers use ordinary addEffect(instance) which delegates addEffect(instance,null). Native NeoForge Applicable/canBeAffected and installed Manas HEAD interception remain in force. Each boolean is ignored by the producer. An admitted request may merge/update an existing instance or return false on no effective update. Same-amp longer duration refreshes; weaker/higher effects follow native hidden-effect update rules. onEffectStarted is called for admitted add requests even when update returns false; glass placement sound is not proof of a new stored status.

## Native removal

Exact installed MobEffectInstance.tick on applyEffectTick=false calls entity.removeEffect(holder), ignores its boolean, then ticks duration and hidden state; it does not zero the duration. removeEffect uses cancelable NeoForge removal admission. If fire-removal is vetoed, fire was still cleared and subsequent ticks can damp motion. Ordinary duration expiration is a separate server-side Expired event path, also cancelable. Frozen onRemoved is glass particles/sound only; the Iaf mixin invokes it at LivingEntity.onEffectRemoved refreshDirtyAttributes, within the native server branch.

## Cures

Frozen inherits the loader default effect cures; no Frozen-specific cure override exists. removeEffectsCuredBy is server-only, checks the instance cure set and removal event, and removes through ordinary callbacks. Native cure/expiration hooks are preserved; no guaranteed unconditional cleanse is asserted.

## Weapon registry

Exactly six Iaf item suppliers read the two Frozen weapon ability fields: dragonbone_sword_ice uses ICE_DRAGON_BLOOD_TOOL; dragonsteel_ice_sword/pickaxe/axe/shovel/hoe use DRAGONSTEEL_ICE_TOOL. The full installed class census records their actual supplier lambda methods. Registry IDs and actual wrapper constructors are pinned, not inferred from names.

## Weapon callback

Each of five ActivePostHit wrapper classes checks ability.isEnable, invokes ability.active, then calls and returns the parent hurtEnemy. Parent return is not a prerequisite once the callback has started. The legitimate ordinary server Player.attack path requires target attack admission and primary hurt=true before ItemStack.hurtEnemy on the living target/PartEntity parent. Sweeping secondary targets receive hurt/enchantment processing but no per-secondary item hurtEnemy. Ordinary Mob.doHurtTarget has no item hurtEnemy call, so merely equipping a mob is not a proven Frozen weapon delivery.

## Weapon payload

FrozenTargetAbility.active independently calls Slowness(duration,amp2), MiningFatigue(duration,amp2), then Frozen(duration,amp0), in that order; all three addEffect results are ignored and all source arguments are null through the single-argument overload. A failed earlier status does not stop later ones; Frozen rejection/removal does not undo the two vanilla statuses.

## Config

Both abilities read live tools.dragonIceAbility for enable admission, including the wrapper check. FrozenTargetAbility duration is captured in the ability constructor: default and installed JSON snapshot100 ticks for IceDragonBlood,300 for DragonsteelIce. A later duration config change is not necessarily reflected in an existing ability object. Snapshot is file evidence, not proof of runtime load timing. Outer disabled wrapper suppresses the entire blood callback, including its bonus.

## Blood bonus

The blood ability calls DamageBonusAbility(8,FIRE_DRAGON,null) before its inner enable check/Frozen application. For a Player attacker it requires getAttackStrengthScale(0)==1 exactly, then the recipient type tag. The native tag contains iceandfire:fire_dragon. Primary Player.attack checks strength at0.5 for normal attack scaling but calls weapon effects before resetAttackStrengthTicker, so the separate exact1 gate at0 is reachable. Low charge can suppress only this bonus while the admitted weapon statuses still run. The bonus source is iceandfire:bonus with direct=causing=attacker and scoped bypasses_cooldown membership; native hurt return is ignored and does not gate statuses. Eight is requested damage, not guaranteed HP loss. Parent weapon durability/postHurt processing remains native.

## Compat dispatch

ManasCore nested skill MixinLivingEntity declares cancellable HEAD injection into two-argument addEffect. It passes a Changeable instance and source into LIVING_EFFECT_ADDED; false cancels with return false, otherwise replaces the local argument. SkillRegistry.init registers the callback looping learned skill instances, invoking only those passing canInteractSkill; any false onEffectAdded returns interruptFalse. The pinned instance method dispatches virtually to the actual skill. The ColdNullification list extension is the protected tensura_iaf RETURN mixin, adding the Iaf Frozen holder to native Chill/Frost.

## Compat eligibility

ColdNullification inherits ResistSkill.canInteractSkill, overriding the generic TensuraSkill gate: ExistenceStorage sleep mode (positive harvestGiftTick OR harvestTick OR sleepModeTime) rejects; Rest or InfiniteImprisonment rejects; canActivateInArea(instance,entity,-1,false,false) then applies. That call skips worldRestriction checks but can reject a server Player joined to a boss fight banning this ability and toggle it off through restrictUsage. Do not substitute the generic spectator/mastery predicate: the ResistSkill override does not call it. ResistSkill.onEffectAdded admits when not toggled or DISABLE_NULLIFICATION=true; otherwise rejects matching holder in nonempty immune list. The separate canBeToggled method requires mastery>=0 and nullification enabled. Source identity is passed through the callback but unused by this list comparison.

## Compat existing

onToggleOn obtains the same immune list and calls TensuraMobEffect.removePredicateEffect. It copies current active effects, matches holders, then ordinary removeEffect; default AP/MP costs are0 and EnergyHelper short-circuits as not out of energy. Removal can be vetoed. The ColdNullification bridge does not add Slowness or MiningFatigue to its list and does not roll them back. Other native skills/hooks can still affect them. Existing statue-recipient veto remains the R2g1 IafHandler declaration, not an implementation change.

## Dragon read ahead

Saved manager branch proof, NOT completed launch/collision delivery: ICE applyDragonEffect adds only Frozen, no Slowness/MiningFatigue. Breath requests50*stage duration and stage*attackDamageIce damage; charge area requests400 duration and max(1,stage-1)*2 damage. Both target lambdas call hurt then applyDragonEffect regardless of hurt boolean, with source identity from R2g1. Breath uses !DragonUtils.onSameTeam, !self and LOS; charge uses !dragon.isAlliedTo,!self and LOS. Event/grief/radius and actual entry routes remain the exact next subsection. A hit-only charge source must not be called a direct Frozen producer.

## Scope

Core status, ordinary six-weapon producer semantics and the declared ColdNullification dispatcher are closed here. Multipart redirection, full dragon launch/area/grief paths and other mob families are not silently certified. Iaf remains PARTIAL, zero promoted records and zero fully reviewed custom DamageType profiles. R2g1/accepted Twilight and earlier completed mods are unchanged. No HP/SHP/runtime measurements or L2/Stage claims.

## Saved scope and validation

Two non-promoted mechanic drafts, six ordinary weapon delivery records, eighteen unexecuted future fixtures. [Machine-readable findings](iceandfire-r2g2a-frozen-core.json), [native witnesses](native-evidence/iceandfire-frozen.json), [caller census](iceandfire-frozen-callers.json), [Tensura/Manas reference](reference-evidence/iceandfire-frozen-tensura.json), [installed config snapshot](iceandfire-frozen-config-snapshot.json).

Target validation recollects all new witnesses, binds the extracted Manas archive to the installed parent bytes, checks exact callback ordering and source/status contracts, checks all five accepted views unchanged, preserves protected R2g1 evidence, runs the five tooling tests and diff checks. The prior complete central Twilight validation remains protected at86b6e67; no new whole-catalog full-validation claim.

Exact next task: R2g2b: finish Frozen dragon delivery roots from DragonBaseEntity.performNormalBreathAttack/breathAttack/performChargeAttack, IceDragonEntity.aiStep/shootIceAtMob/createCharge, flight-manager scorch/hover and rider paths, DragonChargeEntity.tick/onHit/canHitMob, IceDragonChargeEntity.destroyArea and DragonUtils team/grief predicates. Reuse the saved manager status/damage witnesses. Then close Frozen family, proceed Siren charm/Gorgon and other combat families. No runtime/L2/Stage/production work.
