# R2i8c — Bosses Rise Dragon armor and remaining combat equipment

Dragon armor actual native Post/buff callbacks; Knight Sword/Pirate Saber delivery; native shield/ordinary equipment exclusions.

Static review only. Future runtime fixtures remain unexecuted; whole Bosses’ Rise review is PARTIAL.

## Armor buffs

DragonArmorEvents.onPlayerTick is PlayerTick.Post, ServerPlayer only, gameTime%20==0. Exact equipped Dragon leggings while crouching request native Speed40 amp2 and FireResistance40 amp0. Exact full skull/chest/legs/boots requests Strength40 amp0 and Resistance40 amp0. Real addEffect/Applicable admission and Roll veto remain, including beneficial effects; native attributes and Resistance influence ordinary combat downstream. No outgoing HP request here, and no extra Stage factor on amplifier/duration/attributes. Skull NightVision60amp0/flashing helper is utility/cosmetic, excluded briefly.

## Post admission

onPlayerHurt is LivingDamageEvent.Post for ServerPlayer. Checks exact equipped boots first then chest. No event amount>0, source-is-fall, cooldown or recursive guard in handler. Patched Player.actuallyHurt invokes Post after the f1!=0 HP-change block, so reaching this native event does not require positive HP loss (e.g. full absorption); incoming cancellation/invulnerability can prevent reaching it. Do not turn a synthetic event into a delivered path. Native runtime fixtures must use genuine admitted incoming hits and record actual Post/result ordering.

## Boots explosion

Boots require fallDistance>=3 and max(knownMovement dot down, deltaMovement dot down)>=.5. Radius clamps that downward speed to[0,4.5]. Calls level.explode(player,playerPosition,radius,NONE), then immediately Explosion.explode() on the returned SAME object. Pinned Level final overload constructs explosion, checks Neo onExplosionStart, normally invokes explode then finalizeExplosion; ServerLevel returns it after packet handling. Thus normally two damage/detonate/control passes, one finalization. If Neo start cancels the first pass, Level returns the same object and mod still invokes explode explicitly once; no second start check. Every actual Explosion.explode still calls native detonate, calculator/exposure, hurt and impulse logic. This is an existing native cancellation inconsistency, not a proposed bypass. Source is player_explosion with direct/causing wearer; NONE keeps blocks and fire flag isfalse. Native hurt cooldowns/geometry may suppress repeat HP: do not assert doubled HP. Future Stage belongs once at each actual explosion per-victim hurt request, never radius or two hook layers. Existing native control impulse remains independent from hurt success. Multiple equipped victims can enter their own native Post handlers; preserve this test case without adding recursion or runtime tests now.

## Boots ignition

After explosion call(s), getNearbyPlayers(DEFAULT,wearer,full-side4 box at wearerPosition). Native EntityGetter tests player position in box; DEFAULT forCombat excludes self, unseen/dead/spectator, cannotAttack/cannotAttackType and allies. Its LOS check applies only when attacker is Mob; wearer is Player, so no block LOS test here. Each selected other player setRemainingFireTicks250 directly; not a MobEffect, not conditional on explosion hurttrue, and no FireResistance/fireImmune check at write. Direct counter writes bypass the duration helper/attribute, but later native on_fire HP still respects native admission. Reuse proven-origin native burning Stage point, never fire duration. No boss/mob ignition from this particular player-only loop.

## Chest retaliation

Chest Post branch independently passes Math.random<=.1, requires direct DamageSource entity instanceof Projectile, uses projectile.owner when nonnull else source.causing entity, requires nonnull cause and cause.distanceTo(wearer)>=3. No source-tag projectile inference, amount threshold or hurt-return test. Creates real BlazingFireBallEntity owner wearerPlayer, baseDamage1, silent, eyesY-.1, aimed at cause.position plus independent[-.5,.5) jitter, speed1.5/inaccuracy3; insertion result ignored. Reviewed native arrow direct HP, independent hit FireArea, block radius2 NONE explosion, proximity ignition and later burning are reused unchanged. The retaliating owner is defender, not original shooter. Multiple native projectile hits require independent random trials; no fabricated positive control.

## Knight sword

Native use requires item off cooldown then starts use(duration1200). Server Player release charge<5 makes0 waves; otherwise min(((charge-5)/20)*2+1,7), thresholds5/25/45/65 for1/3/5/7. Native cooldown80 only when waves>0. Each real SwordWave ownerPlayer/base5/KB0/silent/eyesY-.1/speed2/inaccuracy0; no release durability cost. No spread or deferred schedule in this item loop. Reuses exact SwordWave indirect_magic ceil(speed*base) hit and hurttrue status logic; do not multiply item attack13 into projectile or scale wave count. Native projectile overlap/iframes determine total HP. Ordinary melee attributes remain native.

## Pirate saber

Native ItemUtils.startUsingInstantly/BOW, duration14 -> finishUsingItem. Server creates one CrossbowPirate with native crossbow and one Rook with PirateSaber, positions one block at horizontal +/-90deg view, ownerUUIDPlayer, skipXP; direct construction/addFreshEntity, no finalizeMobSpawn and no explicit collision/LOS/cap/expiry check. Add results ignored. Player item-used stat and cooldown80; costs10 durability unless infinite materials. Standard use dispatch cooldown is preserved; do not manually call finish to bypass it. Summons retain own attributes/gear, own timed mob_attack or native crossbow arrow causes, not the player as source; no owner-to-projectile source rewriting. Owner UUID persists; shouldDropLoot false when owned; these two classes have no Ghost age200 expiry. Protected ownership target helpers exclude owner/shared resolved owner independently from damage immunity. Existing AI/timed/crossbow/control paths reused; no new Stage at summon.

## Ordinary equipment

Knight armor builds native default armor modifiers plus slot-specific rollCount+1. Dragon chest/legs/boots similarly add rollCount+1 and BURNING_TIME-2 ADD_VALUE; Dragon skull BlockItem explicitly installs head roll+1/BURNING_TIME-2/armor+3/toughness+2. Native IItemStackExtension uses explicit ATTRIBUTE_MODIFIERS when nonempty else item default modifiers, then Neo computeModifiedAttributes; no unconditional stacking with replacement components. DragonGuardShield is actual ShieldItem with offhand movementSpeed-.01/armor+1/toughness+2. EnhancedShield extends ShieldItem but constructor has onlydurability450; its static roll+1 createAttributes has no installed caller and is not installed in properties/override, so do NOT promote a roll bonus. All shield blocking/bypass sources remain native. Warrior/Large/Dagger ordinary damage/speed/reach modifiers and animation only; Dagger dual-hand animation is not a second damage callback. AnimatedSword swing hook empty unless override; Knight override empty. No mod-specific extra Stage for ordinary melee/equipment attributes. DragonShank native food and bone remainder, materials/repair/render/mining animations are short exclusions, not new combat mechanics.

## Compatibility scope

Only native damage requests are future numeric Stage candidates. Do not scale buffs, random chance, summon count, armor, Roll charges, ignition time, exposure or explosion radius. Native physical/magic/projectile/fire/explosion source tags and their admission are unchanged. Armor retaliation extends existing hazard identities and runtime paths. No Stage/production/runtime changes; whole-mod closure still required.

- **Native burning from Dragon/Blazing paths**: COMPOSITE, NUMERIC_SCALABLE, ADMISSION_GATED, VANILLA_ROUTED. Stage: Entity.baseTick final onFire1 hurt request with proven origin attribution, not ignition duration plus damage.
- **Blazing Fireball native arrow hit**: COMPOSITE, NUMERIC_SCALABLE, ADMISSION_GATED, VANILLA_ROUTED. Stage: Inherited AbstractArrow.onHitEntity final ceil/clamp/crit native hurt amount, not baseDamage and hit both.
- **Blazing Fireball independent impact hazard and ignition**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Native admission, phase/resource or control; no independent outgoing HP amount.
- **Blazing Fireball block-impact explosion**: COMPOSITE, NUMERIC_SCALABLE, ADMISSION_GATED, VANILLA_ROUTED. Stage: Native Explosion.explode final damageCalculator amount at entity.hurt after exposure, not radius.
- **Fire Area native contact damage**: COMPOSITE, NUMERIC_SCALABLE, ADMISSION_GATED, VANILLA_ROUTED. Stage: FireAreaEntity.tick touchingEntity.hurt(inFire,1.5) final amount.
- **Native SwordWave attributed indirect magic**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Once at final ceil(currentSpeed*baseDamage) indirect_magic hurt.
- **Native Slowness application variants**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Native control/status/duration/admission/geometry or source prerequisite; no additional Stage value.
- **Pirate native timed melee**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Pirate baseTick final mob_attack ATTACK_DAMAGE hurt only; AI melee attack is disabled.
- **Pirate native crossbow projectile**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Native AbstractArrow final hurt after crossbow speed/base/enchantment path, never pirate ATTACK_DAMAGE9.
- **Pirate blocking item cooldown and raw impulse**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Native control/admission/resources or prop durability; no additional scalable HP request here.
- **Dragon armor native buffs and equipment modifiers**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Native admission/control/resources/ordinary attributes, no additional HP scaling here.
- **Dragon armor native Post retaliation/ignition admission**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Native admission/control/resources/ordinary attributes, no additional HP scaling here.
- **Dragon boots native repeated explosion request**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Native Explosion.explode final per-victim hurt for the actual boots explosion origin, once per request; preserve native two-pass behavior and do not scale radius.
- **Pirate Saber native owned summon delivery**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: Native admission/control/resources/ordinary attributes, no additional HP scaling here.

[Machine evidence, packages and native paths](bossesrise-r2i8c-equipment.json).

Exact next task: R2i9: reconcile whole-JAR watched methods and source/entity closure, including anonymous melee-goal admission for Knight arena mobs and Dragon guardians. Apply evidence-backed additive corrections, deduplicate/promote Bosses Rise, resolve both custom DamageTypes, run full catalog validation and protect completion. No runtime work.
