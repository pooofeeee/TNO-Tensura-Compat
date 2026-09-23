# R2g3a — Siren song control and status marker

**Song subsection complete; Ice & Fire remains PARTIAL.** Flute loveTicks and bite/pull combat are separate pending mechanics.

## Authority

Installed Iaf beta15 SirenEntity complete class bytes plus SirenCharmStatusEffect, native prey tag, config and cosmetic shader consumer; exact protected loader effect lifecycle and tensura_iaf bridge are reused. Actual callback is SirenEntity.aiStep; lambda$tickMovement$8 is only the compiler helper name, not an absent or separate tickMovement override. All726 native classes contain no SirenData class. The actual state is SirenEntity.charmingEntities.

## Mechanic

The constructor allocates a private final Object2IntOpenHashMap<LivingEntity> charmingEntities. Song control is that map and tickCharm, while iceandfire:siren_charm is a HARMFUL heart-particle MobEffect with only a constructor, no movement/damage/removal override. The status is an independent marker and shader input; its native lifecycle/Resistance admission does not own the map. Whole package classification is CUSTOM_CONTROL with a custom status marker component. No new DamageType, hurt, HP subtraction or SHP call is used by tickCharm.

## Singing

aiStep first calls superclass. Positive singCooldown decrements and calls setSinging(false). Server no-target/not-aggressive state requests setSinging(true), but setter clamps false while cooldown>0. wantsToSing=isSinging&&inWater&&!aggressive; isActuallySinging=isSinging&&!wantsToSing. The animation-pose local additionally requires !aggressive,!inWater,onGround, but those pose guards are NOT all acquisition guards. Server acquisition/tickCharm checks !GorgonEntity.isStoneMob(this) and isActuallySinging; isStoneMob is instanceof StoneStatueEntity, not a generalized petrification flag. Normally Siren and StoneStatue are different entity classes.

## Acquisition

Every tickCount%20==0 during that server singing block: get LivingEntity in own box inflated(50,12,50), using explicit SIREN_PREY predicate; filter !isWearingEarplugs and distance>=5. SIREN_PREY is (Player&&!creative&&!spectator) OR entityType tag SIREN_CHARMABLE; native tag has villager and wandering_trader only. The OR allows tagged entities independently of the Player clause; do not invent an unconditional creative/spectator exclusion for arbitrary future tag additions. No LOS/wall check, damage result, holder application, or owner/team check gates this query.

## Map before effect

Refresh removes map keys absent from current target list directly (no stopCharm/cooldown), adds missing keys with time0, then attempts addEffect(SIREN_CHARM,30ticks,amp0,source=this Siren) for every retained key; returned boolean discarded. Existing time counters are preserved by computeIfAbsent. Then setSinging(true) and tickCharm run even if effect addition was vetoed. Native finite duration/merge/cures remain, but clearing/rejecting this marker cannot remove map entries through this class. Shader enabled by marker is cosmetic and not proof of control admission.

## Timer and distance

tickCharm iterates current map. First time>maxSingTime (default/snapshot12000) calls stopCharm; equality still permits a control tick. Next checks Siren isAlive and target distance<=64; failure stops that target and sets Siren aggressive=false. There is no corresponding target alive check in this method. The box query can include diagonals beyond64, so acquisition/marker attempt can be followed by immediate stop and global cooldown. Outside the server singing block the map/timers are not ticked or cleared by this class; they can remain dormant.

## Map player bug

Exact bytecode tickCharm loads charmingEntities atoffset93 into a local before instanceof Player at100; another field load353 precedes instanceof Player356. Both test the MAP, not charmingEntity. The actual constructor allocates Object2IntOpenHashMap, so the intended creative/spectator escape in this tick body never applies and the rotation body also runs for Players. Ordinary initial Player eligibility still comes from SIREN_PREY; a mid-charm creative/spectator change is only removed by the next target refresh (unless tagged), not this mistaken tick guard. Preserve the native bug; no repair is authorized.

## Approach

Distance<5 on a tickCharm iteration sets cooldown=timeBetweenSongs (default/snapshot2000), requests singing=false, sets target to that victim, sets aggressive=true, triggers nearby Sirens, then stopCharm. Refresh excludes <5 targets before tickCharm, so a target already inside5 on a refresh tick can be removed without this aggression handoff. At distance>=5: counter increments, horizontalCollision sets jumping=true; each velocity component moves10% toward +/-0.5 based on sign of Siren-target delta (Y sign uses SirenY-targetY+1). Writes delta, sets hurtMarked=true, stops riding if passenger, rotates pitch/yaw toward Siren-minus-target-minus(0,1,0) with each wrapped change clamped+-30 degrees. No damage result is tested.

## Removal shared state

stopCharm only removes map entry and sets global Siren singCooldown; it does not remove the MobEffect, setSinging, clear motion, stop jumping, or clear target. Next aiStep consumes cooldown and clamps singing. Direct refresh removals do not call it. Losing singing suspends map processing; last marker can expire independently. Multiple Sirens own separate maps and can write one recipient velocity; multiple victims share a Siren cooldown/target/aggression state. No stable cross-map/target priority or single-controller arbitration is implemented here.

## Aggro boundary

triggerOtherSirens scans own AABB inflated12 and for other Siren entities sets target/aggressive and singing=false. Siren.hurt calls it when source.getEntity is living BEFORE super.hurt, so propagation is not gated by accepted damage. Arrival handoff itself does no HP damage. Bite/pull animation damage in the earlier aiStep body remains a separate next subsection; ordinary later aggression is not damage caused by the SIREN_CHARM MobEffect.

## Persistence

Siren save writes each map target UUID and CharmTime under CharmingEntities. Read clears the map and restores only UUIDs resolving to a currently loaded LivingEntity in the ServerLevel; it does not store unresolved UUIDs for later. Singing/aggression and other entity fields restore separately. singCooldown is not saved in these methods. CHARMED/Passive is a distinct saved synced boolean and is not the target map or SIREN_CHARM membership.

## Native immunity

Native isWearingEarplugs checks nonempty HEAD stack exactly IafItems.EARPLUGS. tensura_iaf RETURN injection preserves an already true result; otherwise makes it true for SkillUtils.isSkillToggled(entity,SPIRITUAL_ATTACK_NULLIFICATION). Protected exact SkillUtils resolves an instance and requires isToggled&&mastery>=0. This bridge uses neither ResistSkill.canInteractSkill nor the ColdNullification holder-list dispatcher: it has no nullification-gamerule/sleep/Rest/area predicate of its own. Other native systems can change toggle state, but do not silently import those predicates into this helper. Earplug/toggle changes affect next20tick acquisition refresh; tickCharm has no per-tick earplug recheck.

## Status independence

Because marker addEffect result is ignored, generic effect immunity/cure alone need not prevent song movement. Conversely earplugs can prevent map acquisition even if a previously applied marker remains for its native duration. Existing native status admission, source=this, expiration/removal events and external hooks remain untouched. No status fallback, synthetic source, direct HP/SHP change, runtime L2 result or production fix is proposed.

## Exclusions and next

SirenShaderRenderHelper is cosmetic and excluded as a separate mechanic. Hair/pose/sounds/rendering/spawn appearance are short exclusions. Source read-ahead shows SirenFlute writes MiscData.loveTicks200 rather than SIREN_CHARM; it requires its own component dispatch/persistence review next. Siren bite/pull likewise remain separate. Ice & Fire remains PARTIAL, no promoted records; Frozen complete checkpoints preserved.

## Evidence and validation

[Findings, paths and future fixtures](iceandfire-r2g3a-siren-song.json), [native witnesses](native-evidence/iceandfire-siren.json), [whole-JAR caller census](iceandfire-siren-callers.json). Scoped validation reproduces witnesses/census, proves map-versus-Player bytecode and ignored effect return, preserves accepted records/prior evidence, and runs five tooling tests plus diff checks. No runtime tests or new whole-catalog full-validation claim.

Exact next task: R2g3b: finish distinct Siren Flute loveTicks control (SirenFluteItem.use -> MiscData.setLoveTicks/tick -> ComponentManager/native attachment and tick registration; actual consumers/removal/persistence) and Siren bite/pull attack admission/amount/hurt-return dependency. Do not conflate either with song/SIREN_CHARM. Reuse completed R2g3a song and R2g2 Frozen. Then Gorgon and remaining Ice & Fire combat families; no runtime/L2/Stage/production work.
