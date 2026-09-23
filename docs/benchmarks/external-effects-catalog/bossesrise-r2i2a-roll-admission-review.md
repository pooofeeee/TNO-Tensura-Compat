# R2i2a — Bosses Rise native roll admission

Dodge Roll combat-significant resource/control/admission only; no whole-mod completion claim.

Static review only. Future runtime fixtures remain unexecuted; whole Bosses’ Rise review is PARTIAL.

## Delivery

Native client rising-edge Dodge Roll key (default keycode90) sends DodgeRollMessage(type0,left,forward) and calls local pressAction for prediction. Registered payload handler processes only SERVERBOUND, queues work with context.player (no arbitrary target player), then pressAction. Actual server pressAction requires nonempty current chunk, type0, config CAN_USE_ROLL true, not swimming, an available charge with cooldown<=0, and successful startRoll. startRoll independently requires roll<=-5 and onGround. No native spectator/creative/gear/boss-presence predicate is added here. Native registered networking and event annotations are pinned; actual runtime delivery/sync is untested.

## State

Constructor starts roll0, duration14, no charge entries. PlayerTickEvent.Post calls tick; every tick charge capacity is max(0, configured DEFAULT_ROLL_COUNT + integer ROLL_COUNT attribute). Default capacity2, native syncable attribute default0 range0..9. Newly added slots start0; removed slots are removeLast after prior sorting. Successful start resets rollDuration14 and roll14, then caller sets used cooldown1 and sorts. isRolling is roll>0; isInvulnerable is strictly roll>7, i.e. counter values14..8 only. Counter decrements one per Post until-5, including5tick recovery after roll0. These are method counter windows, not a promise of wall-clock invulnerability independent of event order.

## Recharge

Only when roll already<=-5 does tick subtract1/ROLL_COOLDOWN from the first positive cooldown and stop; charge recovery is sequential, paused through active roll/recovery. Default configured40; negative config sets firstpositive0, zero uses native float division (no added clamp). ROLL_COOLDOWN_MORE default20 exists but has zero GETSTATIC consumers anywhere in installed artifact, so do not invent per-extra-charge delay. Charges/duration/cooldown are native resources with no Stage value. Equipment ROLL_COUNT producers are indexed for later equipment review; no uncalled attribute helper is promoted as a working delivery.

## Damage admission

RollAttachment.preDamage default SubscribeEvent: Player and isInvulnerable -> setCanceled(true), with no DamageType/tag/attacker/amount exception. Exact installed NeoForge CommonHooks posts LivingIncomingDamageEvent and returns isCanceled; LivingEntity.hurt returns false on cancellation before shield handling, armor/Resistance/final damage and ordinary HP effects. Earlier isInvulnerableTo/client/dead/fireResistance rejects still happen before this hook. Retain event ordering and other listeners; no blanket runtime claim against custom direct HP/SHP edits or nonstandard callbacks.

## Effect admission

preEffect applies to Player and same roll>7 window, sets Applicable.Result.DO_NOT_APPLY without filtering harmful/beneficial/source/duration. Installed addEffect and forceAddEffect call CommonHooks.canMobEffectBeApplied; event getApplicationResult returns true for APPLY, native canBeAffected only for DEFAULT, false for DO_NOT_APPLY. This rejects application/refresh through those paths, not removal or cleansing existing effects and not arbitrary instant-effect functions/healing. Later event listeners can change final result; Tensura/L2 ordering remains future runtime work.

## Freeze

RollMixin injects Entity.setTicksFrozen HEAD cancellable, cancels every Player write while roll>7, including attempts to lower/clear the counter. It does not reset preexisting frozen ticks and does not declare isFreezing/canFreeze immunity. A freeze-derived HP attempt reaching LivingIncomingDamage still meets the separate native damage cancellation. Preserve this write gate exactly; no synthetic Frozen status or duration scaling.

## Projectile identity

Native ProjectileImpactEvent constructor accepts Projectile and calls EntityEvent(projectile); inherited getEntity returns that projectile. EventHooks.onProjectileImpact constructs precisely this event. RollAttachment.preImpact tests event.getEntity instanceof Player, not EntityHitResult target. Player cannot also be Projectile, so this branch cannot cancel ordinary native projectile impacts. Do not promote it as projectile deflection/impact immunity. Damage/effect cancellation may still reject later callbacks, while independent explosions, motion, summons, discard or hurt-ignored callbacks can proceed; each payload family must retain its native return dependencies.

## Movement

startRoll forces CROUCHING; move normalizes existing horizontal velocity plus desired input and sets horizontal magnitude MOVEMENT_SPEED *6*(10/rollDuration), retaining vertical velocity and marking impulse. Direction selected from dominant input with forward fallback, orientation aligned with head. During rolling, tick clears shift and repeats movement while grounded. ControlMixin returns true from Player.isImmobile while roll>0; no blanket attack/use-item veto is inferred. On transition positive->0, horizontal speed becomes MOVEMENT_SPEED, retainsY, and clears forced pose only if still CROUCHING. Native terrain/collision and aerial behavior remain; no additional Stage multiplier.

## Other gate and persistence

Only other installed direct RollAttachment.isInvulnerable consumer is Yeti GlacialShove: ServerPlayer in its native zone is skipped while roll>7. That is a separate explicit displacement/status gate, not evidence ordinary knockback is canceled everywhere; full Yeti producer/geometry is pending. Attachment serialization retains direction,duration,roll,count and each cooldown; registry uses AttachmentType.serializable. Do not synthesize/clear saved state. Death-copy/synchronization behavior is not assumed from serialization alone.

## Integration

Four native nonnumeric packages: roll charge resource, movement/control, damage/effect admission and freeze-write gate. No new damage source or HP/SHP amount exists, so no Stage scaling point. Preserve native Player predicate, source identity, effect admission and exact counter window. Future runtime variants include damage rejected but projectile secondary callback still executes, benign effect rejected, existing effect retained, decrementing freeze write rejected, charge recovery and genuine server input. Runtime tests remain NOT_RUN.

## Exclusions

Roll GUI/camera/animations/sounds are cosmetic and excluded except animation duration is passed from the same native14tick state. No deep UI/network infrastructure or unrelated equipment/boss payload review in this section.

- **Dodge Roll native charges and recovery**: CUSTOM_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Fixed native resource/control/admission; no numeric HP/SHP payload to scale.
- **Dodge Roll native movement and control**: CUSTOM_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Fixed native resource/control/admission; no numeric HP/SHP payload to scale.
- **Dodge Roll damage/effect and explicit GlacialShove admission**: CUSTOM_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Fixed native resource/control/admission; no numeric HP/SHP payload to scale.
- **Dodge Roll native freeze-write veto**: CUSTOM_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Fixed native resource/control/admission; no numeric HP/SHP payload to scale.

[Machine evidence, packages and native paths](bossesrise-r2i2a-roll-admission.json).

Exact next task: R2i2b: Bosses Rise shared boss attack helper and damage/death/state admission (AbstractBossEntity, AbstractStateBossEntity, entity parts and ownership). Then distinct Underworld Knight, Infernal Dragon, Yeti, Sandworm, Kraken/cannon and equipment payload families. Roll is complete; do not repeat it. Static only.
