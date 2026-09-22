# r2f8p - TWILIGHT_TRAVELLERS_MOVEMENT_SEMANTIC_REVIEW_COMPLETE

Installed Twilight4.8.3345 with exact installed nested ASM, raw Minecraft1.21.1 and installed NeoForge21.1.244. Static research, runtime0; no production/Stage/Phase6/7/L2/boss tests or changes. Eleven movement packages close the remaining TravellersGearLogic methods and eight registered movement transformers. Protected R2f8o modifier activation, recipes, broken state, attributes and Efficient Eater remain authoritative. Belt/display/zoom, Emperor cloth and unrelated ASM remain unfinished. No new DamageType, direct HP/SHP payload, synthetic event or compatibility fix.

Adds 11 reviewed packages / 40 delivery cases. Twilight remains PARTIAL at 185/584 drafts, zero promoted. REVIEW_REQUIRED 0.

## Native contracts

### Authority

Installed Twilight4.8.3345 with exact installed nested ASM, raw Minecraft1.21.1 and installed NeoForge21.1.244. Static research, runtime0; no production/Stage/Phase6/7/L2/boss tests or changes. Eleven movement packages close the remaining TravellersGearLogic methods and eight registered movement transformers. Protected R2f8o modifier activation, recipes, broken state, attributes and Efficient Eater remain authoritative. Belt/display/zoom, Emperor cloth and unrelated ASM remain unfinished. No new DamageType, direct HP/SHP payload, synthetic event or compatibility fix.

### Activation

Reuse R2f8o: actual component/marker presence, registered modifier group and current equipped stack; !spectator and not broken Travellers armor, except Auto-Repair. Movement modifiers are not ALWAYS_ACTIVE. Real slots are FEET for boots, LEGS for wings, CHEST for Swift Swim. No reviewed movement callback queries Curios. Some later stored-state consumers explicitly do not repeat current activation checks; those differences are recorded below. Item attributes have their native equipment lifecycle independently from component activation. Native external listeners/clamps remain, no pack-wide compatibility certification.

### Water

WaterWalkTransformer inserts EntityHooks.processWaterWalking before every IRETURN of LivingEntity.canStandOnFluid(FluidState). Non-WATER fluid tag or inactive WATER_WALK preserves prior result. Eligible WATER overrides prior result with WATER_TYPE fluid height<.4 strict AND !shift. If height>0, eligible and gameTime%3==1, splash helper runs; it also requires horizontal known-motion length>=.01 and last-water-walk tick+1!=current tick before visuals/timestamp. No damage/effect/resource cost. Native LiquidBlock.getCollisionShape additionally requires context.isAbove(STABLE_SHAPE,pos,true), LEVEL==0, and context.canStandOnFluid(aboveFluid,currentFluid). STABLE_SHAPE height8/16; EntityCollisionContext requires entity bottom>posY+.5-1e-5, captured living canStandOnFluid(current), and above fluid type not same as current. Thus exposed source-fluid surface/position admission remains; this is not collision on every flowing water block or a deep-water/lava immunity. Living.travel liquid branch separately requires !canStandOnFluid. Other native collision/fluid eligibility remains.

### Unrestrained

Installed UnrestrainedBlockSpeedAndJumpFactorTransformer changes Entity.getBlockSpeedFactor/getBlockJumpFactor FRETURN to1 only with active UNRESTRAINED. ResetStuckUnrestrainedTransformer inserts helper before Entity.move reads stuckSpeedMultiplier; Living entity with lengthSqr>1e-7 and active modifier gets ZERO. EntityTick.Post also sets ZERO whenever active. UnrestrainedFrictionTransformer changes default IBlockExtension.getFriction FRETURN to.6 when active; cannot assert custom overrides necessarily call that default method. SlimeBlockMomentumTransformer modifies Entity.isSteppingCarefully result in SlimeBlock.stepOn totrue when active, skipping native |y|<.1 horizontal multiplier .4+|y|*.2. SlimeBlockBounceUpTransformer invokes stopBouncing before first getDeltaMovement in bounceUp: active and y>-.08 strict sets y=max(0,y); at y<=-.08 ordinary bounce remains. These are movement inputs; they do not cancel all falls, alter DamageSources, or provide general status/damage immunity.

### Water sprint

WaterSprintTransformer targets LocalPlayer.aiStep isInWater calls and isInFluidType(BiPredicate) calls. Active UNRESTRAINED returns originalWaterResult && !canStandOnFluid(current block fluid); wrapped fluid predicate only transforms WATER_TYPE, preserving other fluid results. With actual Water Walk surface eligibility this allows the relevant native land-sprint checks; submerged/shift/inactive Water Walk still follows original water result. Not unconditional water sprint permission. PathFinderUnrestrainedByLeashTransformer is NOT this equipment mechanic: its separate LEASH_PATHFINDER_OVERRIDE structure marker is explicitly deferred to source closure.

### Swim

Builtin Swift Swim supplies current CHEST WATER_MOVEMENT_EFFICIENCY+1 ADD_VALUE, vanilla attribute default0 clamped0..1. In the actual native travel water branch, e=attribute, halved if !onGround; drag starts sprint?.9:getWaterSlowDown(.8), acceleration .02. With e>0: drag+=(.54600006-drag)*e; acceleration+=(getSpeed-.02)*e. Dolphins Grace overrides drag to.96; NeoForge SWIM_SPEED multiplies acceleration. Native fluid/controlled-instance/affected-by-fluid/!canStandOnFluid and collision checks remain. This is native attribute behavior, not a universal fixed speed multiple or Water Breathing. Broken stored-attribute lifecycle is protected R2f8o.

### Step

Builtin High Step FEET item attribute STEP_HEIGHT+.5 ADD_VALUE. PlayerTick.Pre with active STEP_UP_ABILITY removes that modifier ID while crouching and, if not crouching and absent, adds the same modifier as PERMANENT. It has no inactive else-cleanup; ordinary equipment changes separately remove old item modifier IDs and add new ones. AttributeInstance distinguishes permanent saved modifiers from transient ones. No additional step-height total is assumed across other modifiers/entities, no teleport or collision bypass. Active gate, real feet equipment, crouch and native movement/collision remain. Save/load and remove/break timing deserve separate fixture controls.

### High jump

Server EntityTick.Post Living wearer with active LEGS HIGH_JUMP and nonnull component amplifier applies native JUMP(duration2,amp1 default,hidden). Native effect eligibility/merge/expiry remains. Native Jump Boost contributes .1*(amp+1)=.2 to getJumpPower and SAFE_FALL_DISTANCE+1*(amp+1)=+2. Jump power=JUMP_STRENGTH*inputScale*getBlockJumpFactor+boost. Native jumpFromGround only changes velocity and posts LivingJumpEvent when power>1e-5; sets vertical power, adds sprint horizontal.2, marks impulse. This is a vanilla effect with equipment renewal; it is distinct from the separate Double Jump safe-fall modifier. No direct damage or unconditional jump/HP immunity.

### Slimy fall

LivingFallEvent: real Living wearer, FEET coefficient nonnull(default.5), active SLIMY_SOLES, !shift, and (TF formula>0 OR stored forceBounce). TF formula=ceil((eventDistance-SAFE_FALL_DISTANCE)*eventDamageMultiplier*FALL_DAMAGE_MULTIPLIER). Unlike native Living.calculateFallDamage, this helper does not test EntityType FALL_DAMAGE_IMMUNE tag. On admission cancel event; store bounceVelocity=-currentY*sqrt(coefficient), doubleJumpBoostVelocity=same, hasBounced=false. Native CommonHooks.onLivingFall returns null on cancellation; Living.causeFallDamage returnsfalse before parent/HP damage. Thus eligible fall HP damage is canceled via a genuine native event, not reduced by a fabricated source. Failed admission follows native fall source/tag/armor/Resistance/protection/invulnerability and hurt pipeline unchanged. No proof of immunity to non-fall damage.

### Slimy bounce

EntityTick.Post on both sides calls stored bounce consumer without a fresh gear/active check: bounceVelocity!=0 && !hasBounced ->newY=sqrt(currentY^2+bounceVelocity^2), preserveXZ, sethasBounced=true and forceBounce=abs(newY)>.25, sound/particles. LivingJumpEvent clears bounceVelocity and forceBounce, but not doubleJumpBoostVelocity or hasBounced. Double Jump reads the retained boost AFTER native jump callback, combines sqrt(afterJumpY^2+boost^2) and zeroes boost. A legitimate stored bounce can therefore outlive modifier removal until consumed/reset by the actual state callbacks. Coefficient codec is FLOAT without an added positive range guard; legitimate packaged coefficient.5.

### Slimy save

SLIMY_SOLES_BOUNCE_INFO is serialized with SlimySolesAttachment.CODEC fields bounce_velocity,double_jump_boost_velocity,force_bounce,bounce. Actual four-argument constructor writes bounceVelocity,forceBounce,hasBounced only; it ignores the doubleJumpBoostVelocity parameter. Encoding includes boost but decode leaves that field Java-default0. This is proven bytecode state loss on native load, not an uncertain tooltip inference or a proposed fix. Other three encoded fields restore. No copyOnDeath declared; ordinary death attachment copy omits it.

### Glide

EntityTick.Post both sides, any Living entity with current LEGS active GRADUAL_GLIDE, nonnull multiplier(default.8333333), descendingY<0 and !fallFlying. Players also require IS_GRADUALLY_GLIDING=true; nonplayers do not. SetY=oldY*mult, preserveXZ, fallDistance=float(newY^2/2/getGravity()). No separate onGround/liquid/passenger/jump-key requirement inside physics helper. Native gravity/collision/fall rules remain; not a blanket no-fall-damage effect, Slow Falling MobEffect or source replacement.

### Glide input

Client RenderFrame.Pre computes flag=(TFConfig.manualTravellersWingsGradualGlideDefault==shift) &&knownMovementY<0&&!onGround, without current gear check; on change stores and sends GradualGlidePacket(bool,playerUUID). Installed client TOML and default config are true, so descending hold-shift is the ordinary input. Bidirectional handler looks up packet UUID in ctx.player.level, requires nonnull Player, sets flag; server forwards to tracking players. It does not compare senderUUID or check gear; actual physics still checks current gear, and server PlayerPre clears true flag when modifier inactive and syncs tracking+self. Client MovementInputUpdate with flag&&shift divides forward/left by.2 without its own gear check. Native input.tick precedes event and item-use .2 slowdown follows it. Packet/state admission is recorded as implemented, with no fabricated traffic or security/runtime testing.

### Double state

PlayerPre sets proposed HAS_DOUBLE_JUMP=false when inactive; else true onGround OR inLiquid OR onClimbable; otherwise leaves it alone. Only when nonnull proposal differs from stored value does it update availability, reset validator0 and remove Double Jump SAFE_FALL_DISTANCE modifier. Client jump-key press uses native key/action/no-GUI check, stores lastpress and avoids creative flight toggle when mayFly &&elapsed<=6; requires current active DOUBLE_JUMP and helper success to send empty PerformDoubleJumpPacket. Server packet calls helper on ctx.player, with failed return routed to movement validator. Helper checks stored HAS_DOUBLE_JUMP and !fallFlying,!onClimbable,!onGround,!isSwimming,!abilities.flying,!inLiquid,!passenger; it does NOT independently recheck current gear. PlayerPre usually clears stale availability on the next tick; ordering remains material.

### Double payload

Admitted helper calls native Player.jumpFromGround() then optional saved Slimy boost combination, resets fallDistance, consumes HAS_DOUBLE_JUMP=false, resets validator0 and adds/updates TRANSIENT SAFE_FALL_DISTANCE+2 under its own ID. Native jump returns void: even if its low jump-power branch produces no vertical impulse, TF continues reset/resource/safe-distance actions and returnstrue. Actual exact TRAVELLERS_WINGS item is checked only for wing-state/particle packet visuals, not the physics admission. Safe-distance removal is conditional on availability transition in PlayerPre, not an unconditional landing hook; do not assume all inactive/equal-false states erase it. Native High Jump effect safe-distance is a distinct additional modifier.

### Sidestep

Client MovementInputUpdate LocalPlayer onGround detects prior leftImpulse==0, matching sign with last nonzero, currentTick-lastWalkingTick<4 and newleft!=0; successful tryPerformSidestep sends server boolean left/right. Helper uses current active LEGS SIDESTEP, cooldown nonnull(default40), gameTime-lastSidestepTime>cooldown STRICT, !fallFlying,onGround,!crouching. No separate passenger/creative gate. performSidestep adds horizontal vector magnitude1.6 perpendicular to current yaw with player.push (not velocity replacement), sound and wing state; records time and cooldown-sound flag. Server packet repeats helper for ctx.player; failed helper invokes validator. Cooldown notification uses same strict>cooldown and active current modifier. lastSidestepTime defaults0, so first ordinary use requires gameTime>40; attachment is not serialized, so cooldown does not persist across reconstruction.

### Validator

Only failed double-jump/sidestep server packet helpers call validateMovement for ServerPlayer. CurrentServer must be nonnull AND dedicated; integrated server skips. Read stored count and tick delta; when diff>=45&&!fallFlying reset local count=-1; record current lastCheck. If count>=5 disconnect with native flying message; else save count+1. If old/reset count>1 also warn and absMoveTo current pose plus native position packet. No HP/source, invulnerability or cooldown resource change is implied by validator. Serialized count/tick values and helper successful resets differ from visual wing timers.

### Straight

Server Living EntityPost reads FEET multiplier(default1.4), active and !=1 determines desired presence of MOVEMENT_SPEED modifier ID. Only when desiredpresence!=actualpresence does it add/update transient(mult-1) ADD_MULTIPLIED_TOTAL orremove. No server forward-input gate; changed numeric component while modifier already present is not updated by that branch. Client MovementInputUpdate LocalPlayer selects multiplier1 if inactive/null/forwardImpulse<=0; otherwise actual value, then addOrUpdateTransient(mult-1) and divides leftImpulse bymult. This is native client/server asymmetry, not uniform unconditional x1.4 speed. Ordinary attribute stacking/clamps, equipment and current inputs remain.

### Straight fov

GetFieldOfViewModifierTransformer targets AbstractClientPlayer.getFieldOfViewModifier: before first FCONST_1 call straightAheadNullify; before every FRETURN call straightAheadRestore, only if first anchor found. Installed target contains anchors. Nullify saves current modifier amount+1 (or1), removes the ID for FOV computation; restore re-adds transient(mult-1) only for LocalPlayer. Nonlocal AbstractClientPlayer has no corresponding restore branch. The native returned FOV/event computes while modifier is removed; this is visual compensation with temporary attribute state, not a second speed buff. TF Goggles zoom is a separate unfinished feature.

### Agile

Client MovementInputUpdate LocalPlayer with current LEGS active AGILE_RANGER and nonnull multiplier(default5), usingitem and !passenger, and ((item instanceof ProjectileWeaponItem OR whitelist tag) AND !blacklist tag) multiplies left/forward by5. Installed whitelist adds MOONWORM_QUEEN; no packaged blacklist resource is present, but datapack tags remain extensible. Exact NeoForge244 LocalPlayer.aiStep posts event AFTER input.tick and BEFORE ordinary using-item .2 slowdown; default5 offsets that later factor for eligible use. No server projectile power, ammo, firing callback, source, HP or damage multiplier. Native use-item state, other event handlers and movement gates remain.

### Persistence

TFDataAttachments: HAS_DOUBLE_JUMP(false), lastJump/validator/lastCheck/horizontal input state(default0), LAST_TICK_WATER_WALKING(0), TEMPORARY_SAVED_STRAIGHT_AHEAD(1) and IS_GRADUALLY_GLIDING(false) serialize with native codecs; glide also declares native BOOL sync. None declares copyOnDeath. TravellersGearEvents explicit death copy preserves only RED_THREAD_VISION, not movement state. Native attachment death-copy filters copyOnDeath; nondeath copying uses serializer/copy rules. TRAVELLERS_WINGS and TRAVELLERS_WINGS_ANIM have no serializer, so sidestep time/soundflag and visual state do not save. Wing state packets carry ID/state/left/timers for visuals; DoubleJump15 and Sidestep11 tick locks in determineWingState do not create another movement payload. Raw item components persist independently as protected in R2f8o. No runtime save/load test or pack-wide integration claim.

## Packages

| Mechanic | Primary classification |
|---|---|
| Travellers native water-surface collision | CUSTOM_CONTROL |
| Travellers terrain movement overrides | CUSTOM_CONTROL |
| Travellers native swim-efficiency attribute | VANILLA_DIRECT |
| Travellers crouch-controlled step attribute | VANILLA_LIKE_EXTENDED |
| Travellers renewed native Jump Boost | VANILLA_LIKE_EXTENDED |
| Travellers fall veto and stored bounce | CUSTOM_CONTROL |
| Travellers descent and fall-distance control | CUSTOM_CONTROL |
| Travellers stored second-jump availability | CUSTOM_CONTROL |
| Travellers native sidestep impulse and cooldown | CUSTOM_CONTROL |
| Travellers directional speed and FOV compensation | CUSTOM_CONTROL |
| Travellers eligible item-use input recovery | CUSTOM_CONTROL |

## Custom source callers

| Type | Amount | Source identity |
|---|---|---|

## Scope and exclusions

- Nine full declared logic/state/packet classes, selected movement events/hooks, exact config, native attribute/fluid/fall/input comparison and eight registered nested transformers reviewed.
- All movement has no new custom DamageType. Eligible fall veto and stored motion are distinct from subsequent native HP damage. No direct HP/SHP write or runtime claim.
- Leash pathfinder ASM is structure state, not Travellers Unrestrained; separately unfinished. Belt/display/zoom, Emperor cloth and remaining ASM remain unfinished.
- No Curios slot lookup in movement callbacks; generic loader/event hooks present, source-specific external compatibility NONE_PROVEN for these paths, not a pack-wide guarantee.
- Protected prior mechanics and source paths retained without redoing accepted work. Twilight remains PARTIAL with zero promoted records.

## Future native controls

- Real crafted gear plus source-water/terrain/collision matrix; exact native ASM anchors, no synthetic movement events.
- Native effect/attribute stacking, crouch/equipment lifecycle and relevant save/death controls.
- Genuine falls and bounce/jump sequence separating event cancellation, motion, state decoding and HP observations.
- Actual input and server packet helpers for glide/double-jump/sidestep with current state, cooldown and dedicated/integrated controls.
- Native forward/side/back/FOV and projectile-item-use input order with unchanged projectile payload.

[Semantic packages and paths](semantic-sections/twilightforest-travellers-movement.json), [integrity](twilightforest-travellers-movement-integrity.json), [full validation](r2f8p-travellers-movement-validation.json).

Exact next task: Complete Travellers belt/hotbar/item-display/zoom/red-thread and Emperor cloth/render/equipment hooks; then remaining utilities/food/passive entities/hazards,10 custom DamageTypes, remaining installed ASM/compatibility/source exclusions, R2f8 and final Twilight promotion. Continue IceAndFire only after Twilight COMPLETE pushed/live verified. No runtime boss/L2/Stage/production/Phase6/7.
