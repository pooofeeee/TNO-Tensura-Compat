# R2j4 — Bosses of Mass Destruction Obsidilith

Obsidilith rune shield, attack/source/admission/control and native explosion semantics complete; whole BOMD PARTIAL.

Static review only. Future runtime fixtures remain unexecuted; whole Bosses of Mass Destruction review is PARTIAL.

## Scope

Obsidilith native shield/rune and combat delivery review complete. Nineteen native class witnesses and nine selected installed reference witnesses cover the actual boss, block, packet and world scheduler callbacks. Shared effect-filter mismatch, strict HP milestones, capped idle heal, source factory and vanilla explosion contract remain accepted; no reimplementation or runtime tests.

## Shield resource

Synced isShielded initially false. Native resource is activePillars, an append-only-until-cleanup list of BlockPos, not hit count or HP. RuneBlock.onPlace schedules its native block tick after10; that tick links itself to EVERY Obsidilith in AABB(pos).inflate(15,40,15), by addActivePillar with no owner test or deduplication. Each boss serverTick removes positions whose block is no longer OBSIDILITH_RUNE OR whose BlockPos is not strictly closerThan boss.blockPosition,64, then sets shield to list nonempty. Removing all valid linked rune blocks or moving them/boss out of this distance clears shield at that update. Breaking supporting obsidian alone does not break the link if rune remains. Multiple nearby bosses and duplicate link entries are legitimate native cases.

## Shield admission

Shared beforeDamage runs before ShieldDamageHandler.shouldDamage. If shield true and source NOT BYPASSES_INVULNERABILITY: when source NOT IS_PROJECTILE and causing entity Living, invoke that attacker knockback(.5, bossX-attackerX,bossZ-attackerZ); play native shield sound; return false so super.hurt never runs. Native knockback uses its own NeoForge event and KNOCKBACK_RESISTANCE. Any amount is rejected here; ordinary hits neither decrement resource nor damage HP. A BYPASSES_INVULNERABILITY source passes this handler but leaves all runes/shield unchanged and still faces remaining native admission. Exact shield_piercing only disables normal LivingEntity shield blocking: it has no invulnerability-bypass tag and therefore does not pierce this boss rune gate. Keep rune removal, passing admission and HP damage separate.

## Pillars and phase

Shared native quarter-milestone change sets shouldDoPillarDefense; next move selection consumes that flag and uses PillarAction. PillarAction server path attempts four horizontal random radius13 locations, runs native ground scans, schedules construction after40 canceling if boss not alive, and returns100; client path returns80. Each successful build writes two obsidian blocks with rune above, triggering the delayed native linking path. No additional per-hit shield counter exists. Rune native block properties strength50/resistance1200 and requiresCorrectToolForDrops use ordinary native block breaking/explosion rules; no special damage type or attack-tag removal callback. Exact production block-removal eligibility must stay native. The position list persists as activePillars int triples, reload appends them and the next server tick validates blocks/range; initial synced flag is not separately loaded.

## Other defense

Registry sets Obsidilith fireImmune; its isOnFire override also returnsfalse, and causeFallDamage returnsfalse. It overrides move to preserve only Y motion and push(Entity) is empty; these are concrete movement routes, not blanket immunity to every effect or displacement API. getArmorValue returns24 while target null, else superclass (installed armor attribute14 before modifiers). Native idle heal is target-null/alive and milestone-capped per R2j2. Config HP300/attack16 are reference file values. Poison/Wither filter mismatch and external MobEffect admission remain R2j2; no immunity repaired.

## World scheduler

These attacks use CapabilityUtils -> installed NeoForgeCapabilityHelper -> LevelEventScheduler.get(level), not the boss preTick queue. Installed @SubscribeEvent LevelTickEvent.Post updates that scheduler. Server storage is per-level SavedData with lazily allocated EventScheduler, but save returns the supplied tag unchanged and queued events are not serialized. Boss death does not itself destroy the world queue; each callback supplier controls cancellation. General Event.shouldDoEvent reads condition only; shouldRemoveEvent reads cancellation. Shared scheduler executes eligible callback before checking removal, so condition and cancellation true in the same update can still run the callback. No runtime dispatch is claimed from annotations alone.

## Rift delivery

RiftBurst default placement begins14 blocks above requested point, finds sturdy upward FULL support down to min build height, chooses ground.above, requires upY+28>=aboveY and replaceability using DirectionalPlaceContext. On placement schedule indicator wait riftTime, cancel while original block no longer replaceable OR actor dead. Once that event executes, it queues inner TimedEvent(delay0,duration7,cancel=false). For seven updates it queries LivingEntity in one-block AABB at pos+(0,2*k,0), k0..6, excludes only exact actor and calls onImpact for each. No LOS/team/owner/canAttack/target-only filter or per-target deduplication is added. Adjacent tiles, height intersections and later waves can attempt repeated hits; native hurt cooldown/admission determines HP progress. Once inner queue begins, actor death or loss of target/open block does not cancel it.

## Burst

BurstAction uses filled block disk radius7 around actor current position, RiftBurst delay30, cooldown80. Every delivered callback reads actor current ATTACK_DAMAGE (installed16) then, if victim ServerPlayer, sends raw client velocity packet preserving server-observed X/Z and replacing Y with1.3 BEFORE hurt. It then requests shield_piercing with direct=causing Obsidilith and ignores hurt return. Packet is not LivingEntity.knockback and this method does not directly set server victim motion. Hurt rejection cannot retroactively prevent the prior packet.

## Wave

WaveAction schedules start after20, captures target object, at execution takes normalized direction actor->target times4, and makes five line centers from actor+direction to that start+direction*7.5. Each center gets a delay8*i action placing a filled radius4 block disk; each rift then waits20. Outer stages cancel only when actor dead, not target changed or null later. Callback sends ServerPlayer client Y=.8 preserving X/Z, then setRemainingFireTicks(5), then shield_piercing ATTACK_DAMAGE. Both secondaries precede hurt and ignore its result. This is FIVE TICKS, not five seconds: baseTick tests positive fire counter divisible by20 before decrement. A fresh isolated value5 alone produces no native on_fire tick before expiry; it can shorten an existing longer fire counter. Do not invent a fire damage event or scale this raw timer write.

## Spike

SpikeAction requires current ServerPlayer, otherwise returns80 without attack. Normal path returns100 and queues three preparations at30,60,90. Each uses native recorded player positions to predict position, places filled radius2 disk and RiftBurst delay20, canceling outer work only if actor dead. Predictor = currentPos - .5*sum(horizontal(previousPos-currentPos)); Neo server player Post tick clears history when lastPosition.distanceSquared(current)>5, then adds current; attachment history capacity10. Callback requests shield_piercing ATTACK_DAMAGE, ignores hurt boolean, then independently addEffect(Slowness120,amplifier2), without effect-source entity. Status eligibility is native/NeoForge and separate from damage acceptance.

## Client motion

BMDPackets registers SendDeltaMovementS2CPacket. Its handler rejects Side.SERVER, obtains local player and queues client.setDeltaMovement(packetVec). Burst/Wave invoke Dispatcher.sendToClient only for ServerPlayer. This establishes intended native packet delivery, not measured authoritative server displacement or bypass of external anticheat/corrections. Preserve packet behavior and test client/server motion separately; no new server push/knockback fallback.

## Anvil

AnvilAction server path captures current target object and after20, if actor alive, reads target.position, remembers original boss pos and moveTo target+Y24. After another delay1, if alive, enqueue Event whose condition is onGround OR Y<0, removal is dead OR condition. If condition true it explodes at boss current position with actor source, configured strength4, MOB, then queues return to saved originalPos after20 canceled if boss dead. No falling-block/anvil DamageSource is produced. Because Event executes before removal and its condition ignores alive, an already-enqueued landing event can detonate if both landing condition and death are true in the same update. No extra immediate HP attack is hidden in relocation.

## Death and explosions

If spawnPillarOnDeath=true (installed), Obsidilith.die invokes onDeath before super.die. Server onDeath creates native actor-centered explosion strength2/MOB/firefalse, then schedules obsidian pillar construction and loot/experience (brief exclusion after the combat explosion). Both anvil and death explosions use direct=causing Obsidilith and thus minecraft:player_explosion, independent of hurt success. Reuse R2j3 native exposure/mitigation/independent explosion vector; Monolith may alter strength in its pending equipment hook. Config false prevents this native death branch. Source actor is excluded from initial explosion candidate list, external event changes remain possible.

## Scaling

Burst/Wave/Spike damage each has one terminal native victim.hurt amount boundary after its ATTACK_DAMAGE read, preserving exact shield_piercing factory and owner. Treat these as one payload family with three native delivery sites, not three multipliers on a single hit. The source key bypasses normal shield blocking by native mixin only; no armor/Resistance/enchantment/cooldown/invulnerability bypass is added. Anvil/death explosions extend already-reviewed native_explosion payload: scale once at attributed native per-victim final hurt, never strength/radius or callback plus engine. Binary rune shield, phase, armor/state rules, client motion, timer5, Slowness120/2, tile counts and scheduling have NO_STAGE_VALUE. No new production change.

## Fixtures and exclusions

Later native fixtures must separate shield rejection and .5 retaliation, rune removal and HP admission, repeated rift requests and successful HP hits, raw client movement and server state, Slowness admission and hurt boolean, and native explosion callbacks and displacement. Rendering/particles/sounds without combat callbacks, resurrection acquisition/structure repair, loot and worldgen are short exclusions; no deep utility catalog. Whole BOMD remains PARTIAL.

- **Native rune resource and shield admission**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Native admission/state/movement/status/count/timing; no additional scalable HP payload.
- **Native target-dependent armor and fire/fall/motion routes**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Native admission/state/movement/status/count/timing; no additional scalable HP payload.
- **Native Obsidilith rift damage**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Once at the delivered action final victim.hurt amount after native ATTACK_DAMAGE; preserve shield_piercing and native repeated-hit admission.
- **Native rift player client velocity**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Native admission/state/movement/status/count/timing; no additional scalable HP payload.
- **Native five-tick fire counter write**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Native admission/state/movement/status/count/timing; no additional scalable HP payload.
- **Native independent spike Slowness**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Native admission/state/movement/status/count/timing; no additional scalable HP payload.
- **Native attributed Obsidilith explosions**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Once at attributed native Explosion.explode per-victim final hurt amount; preserve strength/geometry/source and independent displacement.
- **Native anvil relocation/landing/return**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Native admission/state/movement/status/count/timing; no additional scalable HP payload.
- **Native world rift repeat/cancellation contract**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Native admission/state/movement/status/count/timing; no additional scalable HP payload.

[Machine evidence, packages and native paths](bomd-r2j4-obsidilith.json).

Exact next task: R2j5: BOMD Nether Gauntlet compound hitbox/eye admission, goal/rage state, punches/lasers/blindness and actual native damage/explosion sources, including native secondary callbacks. Then Void Blossom, combat equipment and whole-artifact closure/promotion. Reuse completed shared/native scheduler/source contracts; static only; continue automatically while quota is healthy.
