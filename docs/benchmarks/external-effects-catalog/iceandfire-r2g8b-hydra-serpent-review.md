# R2g8b — Hydra and Sea Serpent combat

Hydra/Sea Serpent combat and related ammunition/Heart/armor complete; remaining creature/gear research pending.

Static subsection complete. Runtime fixtures unexecuted; no Stage or production implementation.

## Hydra attack

Hydra.doHurtTarget returns false; aiStep owns damage. Actual target+LOS chooses random native head; idle head at distance<6 and strikeCooldown0/progress0 starts strike (cooldown3), otherwise random1/2+breathCooldown0 starts breath (cooldown15). For every nine slots, striking with progress>9 clears strike then current target distance<6 requests ATTACK_DAMAGE(base3) mob_attack direct=causing=Hydra, independently Poison100ticks amp3 and knockback.25. No fresh LOS at strike completion or severed-head exclusion. Breathing head i<headCount fires owned HydraBreath every global tick%7, server spawn, aim Gaussian*.4; active breath stops server-side if targetmissing/dead or breathTicks>60, with cooldown15. Strike/poison/knockback hurt/effect results are independent.

## Hydra breath

HydraBreath Fireball/IDragonProjectile replaces tick with baseTick and ProjectileUtil move-vector hit -> direct onHit, omitting normal ProjectileImpact/deflection path. Server advances only if ownerabsent-or-alive and chunkloaded; client advances. TickCount>30 discards but no immediate return. Not pickable,hurtfalse,no fire; ENTITY hit on server ignores ANY HydraHead, needs Hydra owner, excludes owner/allied. Requests mob_attack direct=causing=Hydra2, then Living Poison60ticks amp0 regardless of hurt. Projectile itself is neither direct nor causing source. No discard on entity/block impact and mobGriefing result unused, so repeated intersections remain possible; preserve native collision eligibility.

## Hydra head resource

HeadCount initializes3,clamped1..9. HydraHead neck/head hurt records lastHitHead then forwards unchanged source/amount to parent (multiplier1); Player multipart attack/packet path additionally sets index. Parent hurt first accumulates raw requested amount into headDamageTracker[lastHitHead] BEFORE parent admission/HP protection. If tracker>max(5,configmaxHP*.08)=20 snapshot and no valid existing severed head, resets tracker and marks severed with regrowCooldown0. lastHitHead starts0, body hits reuse last index; clamp tests >headCount, not>=. Severing is not proof of admitted HP damage. Save HeadCount/SeveredHead/all nine counters, but not regrow cooldown/onlyRegrowOne flag/last index. Do not scale counters or threshold separately from incoming damage.

## Hydra survival regrowth

After resource accounting, if currentHP<=incomingAmount+5 and headCount>1 and !BYPASSES_INVULNERABILITY, passes amount0 to super.hurt. This preserves native HP admission, not unconditional invulnerability or direct HP clamp. At one head, severed cleared; if not onFire immediately headCount2,severed1,onlyRegrowOne=true. Valid severed head increments regrow counter; at>=100 resets resource/severed, if currentlyonFire decrements headCount, else adds one head unless onlyRegrowOne; count clamp9. Fire TIMER state at regrowth matters, not merely a fire-tagged hurt source. Attack selection/slots do not universally omit severed index. Runtime must separately measure counter/sever/regrow and HP/SHP outcomes.

## Hydra regen heart

Hydra tick headCount>1,!onFire,injured,every30 attempts Regeneration30ticks amp=headCount-1-(severed!=-1?1:0). While onFire removes Regeneration (native removal admission remains); Poison effect canBeAffected false. No blanket Wither or petrification immunity is declared by Hydra. Regeneration uses protected vanilla heal1 at50>>amp (every tick when<=0), through HealEvent. HydraHeart inventoryTick Player slot0..8,HP/max<1 chooses amp3 below25%,2 below50%,1 below75%,else0; only adds900tick regeneration when absent or weaker. It never downgrades/refreshes same-or-stronger effect and removing Heart does not remove existing effect. No selected-hand requirement or consumption.

## Hydra arrow

HydraArrowItem.createArrow returns native HydraArrow baseDamage5; normal AbstractArrow velocity/crit/enchantment damage and arrow source direct=arrow/causer=owner remain. Native doPostHurtEffects runs only accepted hit on Living excluding Enderman early-return. Then Player active ShieldItem receives durability1+floor(baseDamage) if base>=3, independent of whether it blocked; addPoison300ticks amp0 and heal Living owner by baseDamage (not actual HP loss). These requests are independent of poison admission; native HealEvent/max clamp preserved. A fully blocked/rejected initial hurt cannot reach this callback. No fallback healing/poison on rejection.

## Serpent attack

SeaSerpent doHurtTarget starts Bite if not already, returns true only when starting. aiStep Bite+currenttarget+body/segment asymmetric expanded-box contact OR distanceSquared<50 delegates hurtMob; at animationtick6 requests int ATTACK_DAMAGE mob_attack direct=causing=Serpent and randomizes attackDecision independent of hurt. No frame LOS. Splash triggers transition jumpingOutOfWater true->false, normally water two blocks above; queries living DragonUtilsalive non-Serpent in box.inflate(2*scale,scale,2*scale). Requests same int damage, destroys victim Boat server-side, then halves horizontal velocity and adds vector TOWARD serpent normalized*.3*scale and upward*.3*scale. No LOS/team/hurt-success or zero-horizontal-distance guard. This direct motion is not normal knockback resistance. Serpent riding a Boat separately removes its rootBoat and dismounts.

## Serpent breath admission

Server ranged mode attackDecision=false requires target water, LOS and distance>=30*scale; otherwise switches to melee. Melee switches ranged when distanceSquared>200*scale, a different unit/threshold. shoot requires serpent water, first enables breathing, then while breathing emits owner-bound bubble everytick%10 from head, Gaussian*.0075 aim. Roar disables breath but only sound/animation. Bubble tick condition on SERVER is (owner==null OR !owner.isAlive) AND chunkloaded: live legitimate Serpent owner does NOT enter baseTick/movement/collision branch. Client does enter. This is a proven static divergence, not proof of successful breath HP damage. Do not repair or synthesize hits; later native delivery should measure server bubble position and owner lifecycle.

## Serpent bubble payload

Bubble not pickable,hurtfalse,IDragonProjectile,canHitEntity excludes all MultipartPart and other Bubble. Direct onHit server ENTITY requires SeaSerpent owner, !self,!allied; ignores SlowPart again, requests mob_attack direct=causing=Serpent6, no effect/explosion/discard. mobGriefing read unused. Ownerless moving bubble cannot damage; dead retained Serpent owner can enter server collision and still satisfies instanceof owner gate. Tick>400discard/no early return; tick>20 outside water/rain discards; client autoTarget discards after20 if wrong/missing owner or owner targetnull. No server homing steering in autoTarget. Keep active-owner stalled and dead-owner potential paths distinct.

## Serpent defense resources

Native scale influences dimensions,9 SlowPart multipliers1,HP=max(10,baseHealth20*scale*ancient1.5),attack=max(4,config4*scale*ancient1.5),speedmin(.25,.15*scale*ancient),armor3. updateAttributes includes heal30*scale; called by setConfigurableAttributes on reload, not a natural regeneration tick. Keep native initialization/reload baseline, no Stage on absolute attributes or size. isInvulnerableTo uses cached object identity for fall/drown/inWall/lava, exact IN_FIRE, plus source==damageSources.fallingBlock(source.causer). Exact fallingBlock allocates a NEW source, so that equality is not effective ordinary falling-block protection. Empty checkFallDamage handles natural falls; no broad IS_FIRE/customdragonfire immunity follows. Reload scale/ancient/attribute recalculation and healing require future native observation.

## Serpent arrow armor

SeaSerpentArrow baseDamage3 uses ordinary AbstractArrow hurt/source; isInWater returnsfalse so its movement/water-slowdown behavior differs, with cosmetic bubbles only. SeaSerpentArmor inventoryTick requires Player exact stack at its equipment slot; counts pieces-1. Every equipped piece attempts WaterBreathing50amp0 always and Strength50amp0..3 only while water/rain. Effects linger native duration after leaving/removing; no explicit removal. No additional Stage on Strength amplifier; downstream native attack attribute already includes it.

## Arrow delivery

Weapon ProjectileWeaponItem.createProjectile invokes ammo ArrowItem.createArrow then native customArrow hooks; Bow/Crossbow and legitimate mob weapons retaining that factory reach Hydra/Serpent custom entities. IafRecipes registers their dispenser projectile behavior, but neither item overrides asProjectile. Exact installed ArrowItem.asProjectile constructs vanilla Arrow with ammo copy and null weapon, pickupALLOWED; DISPENSER therefore does NOT construct the custom Hydra/Serpent entity or its post-hit payload. Record dispenser as native vanilla delivery, not fabricate an ownerless custom arrow positive control.

## Integration

Numeric mob/arrow damage Stage once at final native hurt amount; poison/regen Stage once at vanilla damage/heal tick, not again on status duration/amplifier. Hydra arrow owner heal at its native heal(baseDamage) request independently, not scaled baseDamage twice. Binary head budget/regrowth/lowHP/fire gates and source identity remain native. No direct SHP writes, new DamageTypes or production changes. Existing Tensura registry skills are metadata; runtime Resistance/Nullification/L2 interactions remain fixtures, not bypasses.

## Exclusions

Particles, head/neck visuals, roar sounds, scale color/loot, recipes/acquisition, ordinary swim pathfinding and plant breaking excluded. Healing reload, boat destruction and dispenser construction retained because they change combat/lifecycle. Runtime tests remain unexecuted.

## TNO integration decisions

- **Hydra/Sea Serpent body and breath HP damage**: NUMERIC_SCALABLE, VANILLA_ROUTED, ADMISSION_GATED. Stage: yes; Once at native target.hurt amount in Hydra aiStep/Breath.onHit and Serpent hurtMob/doSplashDamage/Bubble.onHit, after native attribute selection.
- **Hydra native Poison payloads**: NUMERIC_SCALABLE, VANILLA_ROUTED, ADMISSION_GATED. Stage: yes; Once at native PoisonMobEffect hurt(1) tick; preserve HP>1 and source/effect admission, no duration/amplifier multiplier.
- **Hydra head resource/regrowth/low-HP protection**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional value; Keep native head budget and HP damage separate; no counter/threshold/zero-amount bypass or secondary Stage.
- **Hydra/Heart native regeneration**: NUMERIC_SCALABLE, VANILLA_ROUTED, ADMISSION_GATED. Stage: yes; Once at vanilla RegenerationMobEffect heal(1) through LivingHealEvent.
- **Hydra/Sea Serpent ammunition damage**: NUMERIC_SCALABLE, VANILLA_ROUTED, ADMISSION_GATED. Stage: yes; Once at AbstractArrow.onHitEntity final hurt amount after native velocity/crit/enchantments.
- **Hydra Arrow owner heal**: NUMERIC_SCALABLE, VANILLA_ROUTED, ADMISSION_GATED. Stage: yes; Once at doPostHurtEffects owner.heal(baseDamage) request, through native HealEvent.
- **Hydra shield wear/knockback and Serpent splash/boat removal**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional value; Native control/resource cost independent of HP where code says so.
- **Serpent native source defenses, parts and lifecycle heal**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional value; Keep native identity predicates and age/scale initialization; no repeated Stage at part or maxHP refresh.
- **Sea Serpent armor WaterBreathing/Strength**: VANILLA_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional value; Native buffs modify underlying behavior; ordinary attack damage scaled downstream once.

[Machine-readable packages, native paths and future fixtures](iceandfire-r2g8b-hydra-serpent.json). Validation reproduces new witnesses, checks significant call order/amounts, preserves accepted records and prior evidence, runs five tooling tests and diff checks. No whole-mod completion claim.

Exact next task: R2g8c: Stymphalian/Amphithere and combat-special Hippogryph/Hippocampus. Then remaining Dread creatures and equipment/status/source closure, dedup and Ice & Fire promotion. Static only.
