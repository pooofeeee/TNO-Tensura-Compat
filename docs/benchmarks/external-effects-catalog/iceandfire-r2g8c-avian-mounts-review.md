# R2g8c — Avian and mount combat

Stymphalian/Amphithere, related weapons and combat-special Hippogryph/Hippocampus reviewed; Dread/equipment closure remains.

Static subsection complete. Runtime fixtures unexecuted; no Stage or production implementation.

## Bird hits

Stymphalian doHurtTarget starts Peck only if NO_ANIMATION,returnstrue. Server aiStep live actualtarget,Pecktick7,distSquared<1.5 requests intATTACK_DAMAGE mob_attack direct=causing=Bird. Native nearest goal uses sight,excludes sameclass/statue,victor,targets eligible Player/Villager/Golem and configAnimals. Peaceful removes Bird; creative/victor target cleared. RangeSquared>3 and<225 starts Shoot outsidePeck/Shoot; whileflying ticks7and14 with collider directpath launches FOUR owned Feather each (8peranimation),speed1.6,inaccuracy14-difficultyId*4. No extra Stage per volley count.

## Feather and bundle

StymphalianFeather owned constructor uses configfeatherAttackDamage as baseDamage; AbstractArrow handles native velocity/crit/source/impact/PVP/damage. If shooterBird AND victimBird, onHitEntity suppresses parent entirely; Player bundle feather can damage Bird then decrements arrowCount after parent independent of hurt success. Tick>100discards. FeatherBundle use cooldown15,server8ownedfeathers at yaw+45successively/horizontal pitch0,speed1.5,inaccuracy1,consume1noncreative,returnsPASS. Pickup/drop cosmetics do not add damage. Bird and Player sources share arrow direct=projectile/causer=owner, with distinct friendly gate.

## Bird flock control

Server die with Living causing entity assigns VictorUUID to deadBird and all current flock members. getVictor resolves ONLY level.getPlayerByUUID, so nonPlayer killer UUID does not resolve as active victor. Saved VictorUUID blocks targetsetter/nearest target and aiStep clears matching Player target. Leader assignment propagates target only to idle nonleader members; no damage amount modifier. Flee goal requires resolved victor and first eligible visible nonallied Player in boxinflate(10,3,10) equalvictor; native selection/order and inverted-looking continuation distanceSquared<2 retained, not guaranteed full flee duration. Flock and victor are AI control, no Stage value.

## Avian arrows

StymphalianArrow baseDamage3.5,ordinary AbstractArrow hit,noGravitytrue; when horizontal speed<.1 addsY-.01 aftersuper. AmphithereArrow base2.5,ordinary accepted-Living-hit postcallback excluding Enderman: target hasImpulse, halves horizontal velocity then adds normalized projectile horizontal direction*1.4,Y+.6. No zero-horizontal guard and no Living knockback/resistance callback; rejected hurt does not reach gust. Cosmetic explosion particles are not Explosion damage. Both ArrowItems override createArrow only; protected IafRecipes+ArrowItem.asProjectile prove registered dispenser creates vanilla Arrow, losing these special entity behaviors. Legitimate weapon factory retains native customArrow/enchantment hooks.

## Amphithere body

doHurtTarget while no Bite/Tail/Wing and no controller chooses Bite half,else Tail ifnotflying/randombit orWing; returns true when starts, no direct hurt. tick actualtarget: Bite tick7 distSquared<10 normal knockback.6 BEFORE intATTACK_DAMAGE hurt; Wing ticks6..21 distSquared<25 requests intATTACK_DAMAGE/2 everytick; Tail tick7 distSquared<10 requests intATTACK_DAMAGE. All source mob_attack direct=causing=Amphithere and no newframeLOS. Wing marks target impulse but resistance check uses ATTACKER knockbackResistance and displacement writes ATTACKER motion; Tail likewise moves ATTACKER, no target displacement beyond impulseflag. Swapped dx/dz vector preserved. No hurt-success control gate.

## Amphithere rider defense

Rider controlbit2 with actual owner/tame Player controller (not currenttarget) uses protected rider-ray2.5 and requests intattack EVERYupdate,sourceAmphithere notPlayer,noanimationframegate. Wild adult empty-hand native mount allows riding; untamed rider random1/15 NO_ANIMATION starts BiteRider; serverpositionRider tick6 whileuntame requests mob_attack1 onpassenger. RidingTime increments with Player passenger whilewild,resetswhenabsent; after>configtameTime tames that Player,clears matching target; savedcounter. hurt BEFOREparent marks isFallen for wild flying airborne IS_PROJECTILE server even if later HP rejected. Tame owner causer sharing vehicle returnsfalse. Fallen sets flightBehaviorNONE,uncontrolled flight addsY-.3 and fallen adds-.2; landing stopsflight,cooldown12000wild/50tame. EmptycheckFallDamage prevents ordinary fall route. Native onHearFlute(tame,airborne) also marksfallen; exact Flute item entry retained for equipment closure.

## Hippogryph body

doHurtTarget starts randomBite/Scratch and returnsfalse when new, true if already either; aiStep tick6,targetdistSquared<8 requests intATTACK_DAMAGE(base5),source mob_attackHippogryph. Scratch independently adds(-.5/sqrt(.5),1,-.5/sqrt(.5)),halveshorizontal,thenonGroundaddsY.3; fixed world-direction motion, not away-from-attacker knockback. Rider controlbit2 actualtameowner Player,protected ray3,choosesanimationifneeded,requests intattack at animationticks10..12; own natural target may also receive tick6path. hurt rejects controller-caused whilevehicle; emptycheckFallDamage suppresses natural fall. Keep owner/passenger target/command/mount admission, no synthetic rider.

## Mount healing

Hippogryph/Hippocampus server aiStep random1/900,deathTime0 heal1. Hippogryph owner interaction FOOD+MEAT+injured heal5,noncreativeconsume; droppedTAME_HIPPOGRYPH AI movable/chance1/20/liveitem/native reach consumes1,feedings++,heal4 even before taming. Afterfeedings>3 and (>7 orrandom1/3),wild and itemownerPlayer =>tame,clearTarget,sit; independenthealreturn. Amphithere handHEAL_AMPITHERE+injured heal5,noncreativeconsume (BREEDtag branch has priority); droppedtaggeditem movable/chance1/20/distanceSquared<1 consumes1 thenheal5,no injured/owner gate. Hippocampus hand HEAL_HIPPOCAMPUS serverheal5 evenfullHP,consume1noncreative; validbreed branchprecedes. All real heal calls use LivingHealEvent/positiveHP/maxclamp; feeding/taming costs do not depend on accepted heal.

## Hippocampus support

No custom attack damage callback found. Everytick%20 actualcontrollingpassenger gets WaterBreathing30ticks amp0,ambient/hiddenparticles; not conditioned on water. Controller firstpassenger Mob directly,or firstPlayer if saddled. Native Player mount interaction still requires owner/saddle/adult/notpassenger. Buff effect admission/cures remain and lingers after dismount; no Stage on duration or immunity. Ordinary ride/swim/storage excluded.

## Macuahuitl dagger

AmphithereMacuahuitl.hurtEnemy after legitimate item hit sets targetimpulse and motion=(halfX+attackerlookX*.6,.8,halfZ+lookZ*.6), thenparent; normal Player.attack item callback gated by accepted original damage, no new HP request. Native mob attacks do not universally call this item callback; use native Player item route,not hypothetical proc. StymphalianDagger override simply delegates SwordItem,ordinary damage/speed only. No special bleed/armor bypass inferred from tooltip. Standard melee Stage once at native attack amount.

## Integration

Native mob_attack/arrow,owner requirements,normal damage/effect/heal admission and installed Tensura/L2 processing preserved. Numeric attacks once at final hurt amount; no second projectile baseDamage/attribute/volley multiplier. Real heal once at healrequest. Direct motion,fallen state,victor,taming and WaterBreathing remain native. No SHP subtraction/custom damage sources. Flute,eggs and unrelated Dread/equipment remain explicitly next work.

## Exclusions

Flight navigation/path details, colors/armor visuals, flute acquisition, pet commands/home/storage, breeding/egg acquisition and feather drops excluded. Their combat-specific callbacks above are retained. No lore-based special effects or runtime completion claims.

## TNO integration decisions

- **Avian and mount native HP attacks**: NUMERIC_SCALABLE, VANILLA_ROUTED, ADMISSION_GATED. Stage: yes; Once at native hurt amount in Bird/Hippogryph aiStep or Amphithere tick/positionRider, rider tick, ordinary Player sword attack.
- **Feather/avian-arrow HP damage**: NUMERIC_SCALABLE, VANILLA_ROUTED, ADMISSION_GATED. Stage: yes; Once at inherited AbstractArrow final hurt amount after native velocity/crit/enchantment formula.
- **Native gust/scratch/attack motion**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional value; Keep actual actor/target motion and native hurt-gated arrow/item versus independent creature control.
- **Victor, taming, rider protection and forced landing**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional value; Native allegiance/control/immunity state, not numeric Stage amount.
- **Mount native healing**: NUMERIC_SCALABLE, VANILLA_ROUTED, ADMISSION_GATED. Stage: yes; Once at native heal(1/4/5) request through LivingHealEvent, retain native food/random/HP gates.
- **Hippocampus rider WaterBreathing**: VANILLA_ROUTED, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional value; Native breathing status, no damage/Stage numeric value.

[Machine-readable packages, native paths and future fixtures](iceandfire-r2g8c-avian-mounts.json). Validation reproduces new witnesses, checks significant call order/amounts, preserves accepted records and prior evidence, runs five tooling tests and diff checks. No whole-mod completion claim.

Exact next task: R2g8d: Dread creature/summon/skull combat. Then remaining equipment (including Dragon Flute delivery), chain/status/resource callbacks and whole-JAR custom DamageType/combat closure; dedup/promote Ice & Fire and continue next target if usage healthy.
