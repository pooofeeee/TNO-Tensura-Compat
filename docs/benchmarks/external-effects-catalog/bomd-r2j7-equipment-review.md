# R2j7 — Bosses of Mass Destruction equipment and block hooks

BOMD remaining equipment and generic combat-relevant block hooks complete; final coverage/promotion remains.

Static review only. Future runtime fixtures remain unexecuted; whole Bosses of Mass Destruction review is PARTIAL.

## Scope

Remaining combat-significant items and blocks reviewed, including registered food effects and generic mixin. Equipment is not a new boss family. Cosmetics/acquisition/structure repair/locator content receives short exclusions.

## Pearl use and zero hit

ChargedEnderPearlItem native use adds cooldown180, creates owner-player ChargedEnderPearlEntity serverside, sets native item and shoots speed1.5/divergence1. It does not shrink the stack. onHit calls superclass first; onHitEntity calls superclass then victim.hurt(thrown(this,getOwner),0). This is a genuine native ZERO request, direct pearl/causing current owner (possibly null), not a missing HP event to fix. Boolean is discarded; server onHit then checks !isRemoved and runs collision. No vanilla ThrownEnderpearl inheritance, no native five-point self-hurt or endermite branch. Stage must keep the zero request zero and must not invent HP damage.

## Pearl control

serverCollision teleports owner, independently applies owner buffs and nearby knockback, then visual packet/sound/discard. Player teleport requires accepting connection, same level and not sleeping; passenger dismounts to impact, otherwise teleportTo; resetFallDistance. Nonplayer nonnull owner uses teleportTo/reset without those player gates. Buff/area callbacks still execute when player teleport prerequisites fail or owner null (owner buffs alone then absent). Each projectile tick discards for dead Player owner, not every nonplayer; changeDimension clears owner when owners dimension differs from destination. Native projectile deflection/owner behavior and normal event gates remain; no new source attribution.

## Pearl effects and shove

Living current owner gets Resistance120amp1 and SlowFalling20amp0 via independent addEffect calls without source entity. Then query all Living in impact AABB inflate6, no owner/team/LOS exclusion. XZ accepts center distanceSquared<9 OR horizontal radius3 point contained in victim box inflatedY10. Y predicate is literally maxY>impactY-1 OR minY<impactY+3, not AND; for ordinary ordered boxes this does not provide the intended interval rejection. The outer6 AABB still bounds query. Native knockback.4 uses impact-minus-victim X/Z (push away), including potentially just-teleported owner; preserves vanilla knockback Resistance and NeoForge hook. Independent of zero hurt result and effect admission. Native Resistance amp1 contributes40% reduction when neither BYPASSES_EFFECTS nor BYPASSES_RESISTANCE, amp0 contributes20%; SlowFalling descending gravity is min(nativeGravity,.01). No Stage multiplier to control or mitigation percentage.

## Fruit delivery

Registered CrystalFruit properties supply always-edible food: each native server addEatEffect probability1 requests Regeneration300amp1, Heal1amp0, Resistance600amp0. Native Player.eat delegates LivingEntity.eat -> addEatEffect -> addEffect; no custom finishUsingItem or direct HP subtraction. Normal consumption/effect applicability and existing-effect merging remain. The Heal effect is added as a one-tick status; it follows HealOrHarmMobEffect.applyEffectTick, not the potion applyInstantenousEffect source form. Ordinary nutrition/saturation and acquisition excluded.

## Fruit numeric

Regeneration tick: if HP<maxHP, heal1; interval50>>amp =>25 atamp1. Heal tick: isHarm(false)==isInvertedHealAndHarm -> heal(max(4<<amp,0)) =4; otherwise native anonymous minecraft:magic hurt6. isInvertedHealAndHarm delegates entity type INVERTED_HEALING_AND_HARM, so preserve that admission and do not assume every externally transformed player is inverted. Native heal event, HP>0 guard and maxHP remain. Resistance is native mitigation, not a scalable HP payload. Future single points are originating native Regen heal1 and Heal tick heal4/hurt6; never multiply effect amp/duration or globally scale all heals/magic. Food-specific origin tracking is a future integration requirement.

## Spear

EarthdiveSpear use fails when damage>=maxDamage-1, then native use charge72000 with elapsed>=10 required. Server Player release tries WallTeleport from eye OR eye-minus1 (short circuit), on success durability1 and stat/sound. onUseTick uses preview-only Consumer that spawns particles: it does not teleport early or damage. WallTeleport finds first redstone-conductor block within3 along look, then first air+air-above along20 from it; unbreakable defaultDestroyTime<0 stops search. Actual teleportTo targetsblockcenterXZ without another shown safe-ground/LOS/hurt gate. Ordinary mainhand +8attack/-2.9speed and hurtEnemy durability use native melee, with no extra damage callback. This combat-positioning control has no Stage value.

## Monolith

ExplosionMixin modifies float at ServerLevel.explode HEAD through MonolithBlock.getExplosionPower. Query cached monolith positions across origin chunk plus/minus4X/Z; first block whose absolute block-coordinate deltas are EACH strictly<64 returns power*1.3. Nonstacking even with multiple halves/monoliths; exact64 excluded, no radial-distance/owner/source/team/LOS filter. This is native radius/strength modification for ANY explosion through that overload, changing native geometry and resultant per-victim amount; it does not invoke hurt itself. Keep this existing1.3 radius behavior native; candidate Stage still applies ONCE at final native Explosion per-victim amount, never add a second Stage on radius. Actual mixin application remains a runtime fixture, not static-certified.

## Cache and flight

ChunkCacheBlockEntity firsttick inserts position, setRemoved removes; ChunkBlockCache stores unique sets and returns empty list when missing. ServerLevel saved-data wrapper stores no contents, lazily rebuilding cache from block ticks. Query does not revalidate blockstate itself. Table of Elevation is flight permission, NOT MobEffects.LEVITATION: server PlayerTick.Post scans nearby5x5chunks, requires player position inside block AABB inflated installed radius3 horizontally; Y uses level.getMinBuildHeight to level.getHeight literally. It inserts player in static flight set even if mayfly alreadytrue; grants mayfly when false. On leaving, if tracked and neither creative nor spectator, clears mayfly AND flying and sends abilities packet, then untracks. It does not preserve another mod flight grant. Existing tracked player whose permission is externally cleared is not regranted by this branch until membership cycles. No ownership/team/cost/HP scaling; future Tensura/L2 fixture must observe native permission conflict without changing it.

## Short exclusions

BrimstoneNectar repairs structures after30, acquisition only. SoulStar entity moves as structure locator and can initiate Lich summon through altar path; native Lich combat already mapped, no locator damage. VoidLily sends direction particles; FlowerBlock constructor declares Glowing with0seconds ->0ticks suspicious-stew metadata, not block-contact Glowing. No BOMD data tags reference void_lily; do not invent a combat status delivery. MobWard generic NaturalSpawner return hook vetoes accepted natural spawn near cached ward; it does not cancel addFreshEntity/minion combat delivery or damage. IceBlockMixin removes resulting water in Lich structure; test/health-overlay/eye-use mixins are log/UI/locator utility. Material items, all sounds/particles, recipes/worldgen/summon acquisition get no separate scalable package. No custom armor or additional registered special weapon beyond inspected spear is evidenced by BMDItems.

## Coverage limits

All eight native MobEffects-reference methods now resolved: VoidLily zero metadata; two effect-immunity lists; configured/independent boss effects; food/pearl buffs; spore Poison. Four registry references only resolve configured Lich vanilla status, not custom registrations. shield_piercing has five native caller methods, one exact-key blocking reader and no tags in pinned closure. Final source coverage will link every watched method to native evidence, including ordinary flight helper travel and SoulStar utility hits; no runtime success or packwide compatibility inference.

- **Native zero-amount pearl contact**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Native zero-hit/control/mitigation/admission/delivery only; no additional numeric Stage payload.
- **Native pearl teleport and owner admission**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Native zero-hit/control/mitigation/admission/delivery only; no additional numeric Stage payload.
- **Native Resistance and Slow Falling**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Native zero-hit/control/mitigation/admission/delivery only; no additional numeric Stage payload.
- **Native pearl independent knockback**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Native zero-hit/control/mitigation/admission/delivery only; no additional numeric Stage payload.
- **Native originating food Regeneration healing**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Once at originating native Regeneration heal argument; preserve effect cadence/amp and normal heal admission.
- **Native originating food Heal effect**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Once at native Heal effect selected heal or hurt argument after inversion predicate; never also scale effect amplifier/duration.
- **Native charged spear wall traversal**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Native zero-hit/control/mitigation/admission/delivery only; no additional numeric Stage payload.
- **Native nonstacking explosion radius amplification**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Native zero-hit/control/mitigation/admission/delivery only; no additional numeric Stage payload.
- **Native explosions with Monolith delivery modifier**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Once at originating native Explosion.explode per-victim final hurt amount; preserve native monolith radius and source.
- **Native flight permission grant and revocation**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Native zero-hit/control/mitigation/admission/delivery only; no additional numeric Stage payload.

[Machine evidence, packages and native paths](bomd-r2j7-equipment.json).

Exact next task: R2j8: final BOMD coverage, deduplication/promotion and complete owner table with honest runtime fixtures; then Cataclysm installed-native source foundation if quota healthy. Static only; no owner-review stop inserted.
