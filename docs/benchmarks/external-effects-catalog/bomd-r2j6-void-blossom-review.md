# R2j6 — Bosses of Mass Destruction Void Blossom

Void Blossom multipart retaliation, proximity/spikes/projectiles, Poison and native healing/defenses complete; whole BOMD PARTIAL.

Static review only. Future runtime fixtures remain unexecuted; whole Bosses of Mass Destruction review is PARTIAL.

## Scope

Void Blossom native combat complete from21 installed class witnesses plus protected shared/projectile/part/RiftBurst contracts. No boss runtime matrix, L2 test, Stage implementation, production change or Phase6/7 work.

## Admission and parts

All seven VoidBlossomCompoundHitbox.shouldDamage handlers returntrue: body/flower are not an eye-only immunity gate. Native super.hurt, armor, Resistance and external events still apply. NetworkedHitboxManager writes the native incoming part marker ONLY into the currently selected hitbox; CompositeDamageHandler runs every hitbox afterDamage, each captures then clears its own marker before any retaliation. Idle/Spike spiked parts are neck and rootYaw; Petal, Spore and all SpikeWave forms use rootYaw only. Flower/flowerBottom are not spiked. Genuine CerbonsAPI projectile/client multipart ray delivery is already pinned R2j5; do not fake markers. Incoming IS_PROJECTILE suppresses part retaliation even if its part is spiked. Missing marker cannot independently trigger this retaliation.

## Retaliation

After incoming hurt returns true, a spiked part plus source not IS_PROJECTILE plus nonnull source.getEntity triggers causingEntity.hurt(thorns(VoidBlossom), current boss ATTACK_DAMAGE). Target need not be Living. Resultfalse suppresses retaliation; source direct entity is not the recipient unless it is also causing. Requested native amount is installed attack12 before modifiers, direct=causing boss, minecraft:thorns. Retaliatory hurt result is discarded. Native amount is not multiplied by incoming amount and no HP threshold/owner/team shortcut is added.

## Proximity

VoidBlossomSpikeTick independently runs in BaseEntity.serverTick: query Living in position-centered box inflated3xyz and movedY1.5, exclude exact boss, then strict target.position distanceSquared<9. It requests same thorns amount12/current attack every tick; no target/LOS/team/part or hurt-success gate, and no hit cache. Native victim cooldown/mitigation decides HP. This is not the same trigger as afterDamage retaliation. BaseEntity invokes serverTick before super.tick even while dying; this proximity callback has no alive guard, so it remains wired through native death animation until removal. Do not invent a safety cutoff.

## Defense and selection

Installed maxHP350 and active armor4; getArmorValue returns20 when targetnull. Registry fireImmune, isInWall=false, move suppresses X/Z. No custom EffectsImmunity assigned, so normal canBeAffected remains. Alive+nonnull target runs attacks after initial80 cooldown; cancel supplier is deadOrDying OR current targetnull. Target switching reuses shared damage memory10. Spike always eligible; wave at target distance<=21; spore also requires strict HP ratio<.75; blade strict ratio<.5. Milestone-change BooleanFlag forces BlossomAction at next move and resets; multiple changes can coalesce, not a shield resource or immediate damage event.

## Spike geometry

SpikeAction requires ServerPlayer (otherwise80); prepares three predicted-player filled radius2 disks after30/60/90, each using Spikes delay20. SpikeWaveAction also requires ServerPlayer, prepares filled radius7 then rings(7,14] and(14,21] after20/45/70 using delay30. Spikes tests three starting heights0/6/12, findGroundBelow with replaceable-or-moss predicate, accepts ground.above when upY+5>=startY, then queues one callback per placement. Callback queries a 1x9x1 AABB (block inflatedY4), Living except exact boss, requests shield_piercing(current boss, current attack12), ignores return. No projectile entity, explosion, native knockback packet or status. No placement/per-target dedup; shared native cooldown governs overlaps. Scheduler is boss preTickEvents and supplied cancel condition; no final open-block recheck in Spikes. Hitbox EventSeries returns to Idle without cancellation. SpikeS2C only visuals, not another damage producer.

## Spore direct

SporeAction requires ServerPlayer, after45 throws one native SporeBall from boss eye toward captured target eye with speed.75, divergence0, gravity compensation.2. Constructor exempts ALL VoidBlossom entity types from entityHit through ExemptEntities. BaseThrownItemProjectile calls native superclass onHit then gated entityHit; Spore overrides outer collision predicate totrue on both sides. Entity contact on server requires current owner Living and victim!=owner, requests minecraft:thrown(direct ball, causing current owner), amount current owner ATTACK_DAMAGE, discards boolean. It does NOT latch impacted, call onImpact, discard, poison or start burst. Native projectile collision/deflection still applies; it can continue and encounter blocks later.

## Spore block and area

Only native onHitBlock calls onImpact. First call records pitch, sets impacted=true and getDeltaMovement becomesZERO; if current owner Living capture it for doExplosion, otherwise server discards. Despite method name this is NOT Level.explode. Creates radius7 filled disk of RiftBurst columns, ground finder startingY+2, accepts upY+8>=startY and replaceable-or-moss. World scheduler outerdelay30 cancels if blocked or CAPTURED owner not alive. Inner seven callbacks at offsetsY0/2/4/6/8/10/12 are uncanceled and exclude only captured owner, not every VoidBlossom type. Same-delay independent discard event is also queued; it does not cancel queued columns. Callback amount comes from CAPTURED owner current attack, but only when projectile.getOwner()!=null it selects CURRENT owner as both direct/causing shield_piercing source and effect-source argument. Preserve this split if another native mechanism changes owner; null current owner suppresses both area HP and Poison. Do not substitute the projectile as direct source or call native explosion hooks.

## Poison

Area callback calls hurt(shield_piercing) then addEffect(Poison140,amp0,currentOwner) regardless hurtboolean. Native addEffect/effect immunity/NeoForge applicability still applies. Installed patched PoisonMobEffect requires HP>1 and requests1 at interval25>>amplifier (amp0 every25), using anonymous neoforge:poison with fallback minecraft:magic only if poison holder absent. Application source does not become tick DamageSource owner. neoforge:poison bypasses armor/shield, has no_knockback, is_magic/is_poison; does not bypass Resistance/invulnerability by these pinned tags. Stage duration/amplifier remain unchanged. Any future numeric tick scaling must preserve native nonlethality and prove origin attribution; an unconstrained multiplied1 could violate HP>1 guard intent. This remains an explicit future integration constraint, not a static source ambiguity.

## Petal

BladeAction requires ServerPlayer; three callbacks after28/52/75 each aim11 native PetalBlade projectiles across a target-center line of halfwidth7 with random-sign20-degree rotation. Maximum33 creations if uncanceled, not33 hits. Speed.9, noGravitytrue, owner boss, exempts boss entity TYPE. Native entity hit with current owner Living requests minecraft:thrown(direct blade, causing currentowner), currentowner attack12; then supplied callback runs on Living victim regardless hurtboolean (this boss supplies EMPTY callback); discard always follows, including missing/nonliving owner. Block callback calls superclass then discards. No native hurt override that provides player reflection; retain engine deflection/ownership semantics without inventing one. Predicate/callback fields and spore impacted are not explicitly serialized by these classes; later native save/load fixture must compare reconstructed default constructor state with launched state.

## Blossoms

Forced BlossomAction on ServerLevel returns120; schedules eight shuffled cardinal/diagonal radius15 positions relative to captured boss position, one after40+8i with native cancel supplier. It directly places moss base and healing blossom above, without a shown replacement/LOS/mobGriefing check. Strict HP<.25 protects6 positions with vine walls; else strict<.5 protects3; otherwise0. Each protected ring uses neighboringx/z in[-1,1] exceptcenter and y0..2. Vines are IronBarsBlock collision, no damage; native scheduled tick destroys them. Breaking blossom schedules neighboring vine removal delays(2-y)*20+random0..19. These are delivery/obstruction mechanics, not HP payloads, and must not receive Stage scaling.

## Heal

VoidBlossomBlock.onPlace schedules blocktick1; each tick schedules next64 and queries ALL VoidBlossom in AABB(block).inflate(40,20,40), without owner link. For each captured boss, world scheduler delay16 invokes LichUtils.cappedHeal with strength10, alive guard and next-strict-quarter maxHP gap minus1. No targetnull condition and no callback-time block/range recheck. Removing the block after queueing does not cancel that heal. This extends shared bomd:capped_heal: one future point is strength10 BEFORE clamp, never multiply final capped amount. Separate targetless idle strength.5 uses the same capped helper. Native heal hooks/maxHP still apply. HealS2C is visual only.

## Death and exclusions

Native death composite first increments deathTime in LightBlockRemover, removes at70, and schedules experience when deathTime1; there is no death explosion or new HP damage callback. Existing proximity tick and already-queued uncanceled world callbacks remain distinct. Light/particles/sounds/experience and rendering rotations are short exclusions; vines retained solely as combat obstruction and healing-block removal path.

## Source and stage

Pinned source tags distinguish thorns (magic-tagged, armor/shield not bypassed here), thrown (projectile/physical), untagged shield_piercing with exact-key blocking mixin, and anonymous neoforge:poison. None certifies packwide Tensura/L2 outcomes. Single future amount boundaries: native thorns hurt requests, native Spikes/area shield_piercing requests, native thrown requests after owner attribute selection, origin-bound Poison terminal tick with native nonlethality retained, and capped-heal strength before clamp. Never scale attack attribute and terminal amount together; leave source identity, counts, geometry, phase threshold, effect duration/amplifier and eligibility unchanged.

- **Native Void Blossom multipart retaliation predicates**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Native admission/control/delivery/state only, no independent scalable numeric payload.
- **Native Void Blossom retaliation and proximity thorns**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Once at native thorns victim.hurt amount after boss attack-attribute selection; preserve distinct delivery gates.
- **Native shield-piercing ground damage**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Once at native Spikes or spore-column hurt amount after captured-owner attribute selection; source remains its native supplied current entity.
- **Native spore/petal thrown damage**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Once at native projectile entityHit hurt amount after current-owner attribute selection.
- **Native Poison application**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Native admission/control/delivery/state only, no independent scalable numeric payload.
- **Native anonymous Poison tick**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Once at origin-proven native Poison hurt amount, preserving native nonlethality; do not scale duration/amplifier or application plus tick.
- **Native healing-block and vine placement/control**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Native admission/control/delivery/state only, no independent scalable numeric payload.
- **Native milestone-capped boss healing**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Once at native cappedHeal healingStrength before clamp; preserve next-quarter maxHP minus1 gap.

[Machine evidence, packages and native paths](bomd-r2j6-void-blossom.json).

Exact next task: R2j7: BOMD remaining combat equipment/block hooks and whole-artifact source coverage, then deduplicate/promote/finalize BOMD with runtime fixtures and source dispositions. Continue the next target automatically while quota remains healthy; static only.
