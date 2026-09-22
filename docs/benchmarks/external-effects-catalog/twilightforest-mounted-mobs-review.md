# r2f8b - TWILIGHT_MOUNTED_MOBS_SEMANTIC_REVIEW_COMPLETE

Installed TF4.8.3345/raw Minecraft1.21.1/exact NeoForge21.1.244 authority. Reuse native Living/Player/Mob hurt/attack, events, attribute calculation, mount/save and TF EntityUtil evidence. Hurt true is not measured HP loss; ordinary armor/directional shield/Resistance/protection/absorption/cooldown/events remain unless explicitly preempted below. Ordinary mob_attack and clamped use when_caused_by_living_non_player scaling for Player recipients: Peaceful0/Easy min(a/2+1,a)/Normal a/Hard1.5a. No SHP/L2/Stage/runtime conclusions.

Adds 8 reviewed packages / 20 delivery cases. Twilight remains PARTIAL at 81/215 drafts, zero promoted. REVIEW_REQUIRED 0.

## Native contracts

### Pipeline

Installed TF4.8.3345/raw Minecraft1.21.1/exact NeoForge21.1.244 authority. Reuse native Living/Player/Mob hurt/attack, events, attribute calculation, mount/save and TF EntityUtil evidence. Hurt true is not measured HP loss; ordinary armor/directional shield/Resistance/protection/absorption/cooldown/events remain unless explicitly preempted below. Ordinary mob_attack and clamped use when_caused_by_living_non_player scaling for Player recipients: Peaceful0/Easy min(a/2+1,a)/Normal a/Hard1.5a. No SHP/L2/Stage/runtime conclusions.

### Knight pair

Lower HP20/speed.28/attack4, dimensions.7x1.1; Upper HP30/speed.28/attack8,1.1x1.3. Separate HP/armor and ordinary death; no shared HP or resurrection/phase. Constructors give armor to both and shield to Upper. Lower finalizeSpawn calls super, constructs Upper atY+1, native finalizeMobSpawn hook with NATURAL/data then startRiding(lower). No addFreshEntity inside this method: native passenger-tree insertion matters; canceled mount/finalize hooks remain effective. Lower melee delegates to first passenger if Living; otherwise superclass mob_attack4. Upper delegation receives its own source identity and attribute, not Lower4. Upper copies vehicleMob target only when its own targetnull during customServerAiStep. Both retaliation/Player nearest target mustSee=false, ordinary melee/float/stroll/look goals. Lower attachmentheight*.91; positionRider aligns Upper body/head/yaw to Lower yaw. Lower priority0 RiderSpearAttackGoal occupies MOVE/LOOK when firstpassengerUpper timer>0<60 and Lower target living/alive/noncreative/nonspectator; no custom tick or attack, default continuation repeats admission. Anonymous melee canUse gates on active timer, not a separate damage gate.

### Knight shield

Upper owns hasShield bit and shieldHits initially0. Upper hurt first rejects exact IN_WALL when any vehicle exists. Otherwise source.getEntity (causing entity, NOT direct projectile) determines dx=selfX-causerX,dz=selfZ-causerZ, angle=degrees atan2(dz,dx)-90 and difference=abs((yBodyRot-angle)%360); no shortest-angle normalization. Front means STRICT150<difference<230. Upper front withshield calls takeHitOnShield and returns false before superclass when true. Lower uses its own position/body angle and delegates its front block to firstpassengerUpper withshield, sharing exactly that resource; no Lower shield counter. Ownerless skips this gate. No check of source armor/shield/invulnerability bypass tags in this custom pre-hurt shield gate. takeHitOnShield returnsfalse while disabled (HP may proceed); otherwise causing Living with mainhand AxeItem onserver disables shield and returns true, blocking even that disabling hit, regardless amount or actual melee/projectile source. This axe branch does not increment counter or execute later recoil/retaliation. Other front hits: requestedamount>10 onserver increments shieldHits; <=10 still block without wear. On third wear, shieldflagfalse but current hurt STILL returnsfalse: breaking shield is not HP damage. Nonfront Upper withshield independently randomBoolean damages shield before later HP processing, without amount threshold or disabled check. Lower has no nonfront wear branch. Therefore bypass source/zeroamount/rejectedlater hurt can still cause custom pre-hurt state changes. Below axe branch, native knockback request strength0 on Livingvehicle elseUpper; no invented nonzero shove (exact loader knockback event may modify it). CausingLiving sets Upper lastHurtByMob. Disabled timer postincrements in customServerAiStep and resets at oldvalue>=100, i.e.101 evaluations from0; NoAI may suspend AI evaluation. Alive Upper without any vehicle loses shield in customServerAiStep even if undamaged. Counters/disabling do not heal HP.

### Knight armor

Armor is independent flag/transient ADD_VALUE modifier: Lower+17, Upper+20. In each hurt, after shield-return opportunity, causingentity rear difference>300 OR<60 breaks that mob armor before superclass hurt. Boundary60/300 doesnotbreak; ownerless doesnotstrip. No amount/success/event approval prerequisite; later immunity/cooldown/cancel can reject HP after stripping. Upper nonfront random shield wear happens before reararmor. Removing flag removes only named modifier; remaining nativearmor/equipment and source bypass behavior remain. NBT saves Lower hasArmor and Upper hasArmor/hasShield and restores corresponding armor modifier; native HP persists. shieldHits, disabledflag/timer and heavySpearTimer are not saved, so remaining shield presence survives but partial wear/disability/timing reset. Bits/ironchest particles are not armor items or dropped/repaired resources.

### Knight spear

Upper doHurtTarget while timer>0 returnsfalse. Otherwise random nextInt(2)==0 sets60/broadcast4/returnsfalse; other branch swing and ordinary superclass melee. Timer decrements after super.aiStep while (client OR !NoAi) andpositive. HeavySpearAttackGoal MOVE/LOOK admits timer>0<60 with current living/alive/noncreative/nonspectator target; default continuation=canUse and default requiresUpdateEveryTick=false. Sole native strike call is its tick when timer==25. Native Mob serverAiStep ticks all goals on even(tickCount+entityId), otherwise only every-tick goals after tickCount>1; then customServerAiStep; Upper decrements timer after super.aiStep. Consequently a running Heavy goal samples alternating timer values and can miss25 entirely depending phase; target loss/admission can also prevent it. No guarantee of one strike per60timer and no invented retry. Static timing inference only, not runtime frequency. During positive timer customServerAiStep adds spear_attack_boost amount12 ADD_MULTIPLIED_BASE; removes when timer<=0 on a subsequent evaluation. Attribute calculation yields default8+8*12=104, NOT20; effective external attributes/enchantments still apply. Because goals precede modifier maintenance, modifiers can remain until maintenance after timerreaches0; do not replace native sequencing with idealized on/off. Strike center currentlook XZ*1.25, Y=rootBBminY minus.75 ifpassenger; AABB +/-1.5 eachaxis. Query allEntity except self/vehicle, no explicit Living/LOS/team/target filter. Each calls super.doHurtTarget directly (bypassing Upper timer guard), native mob_attack direct=causingUpper using currenteffectiveattribute, ignores bool. Enchantment/knockback callbacks inside superclass still need nativehurttrue. Critical sound iff querynonempty even ifnonehurt; HIT_GROUND not damage. No projectile/customDamageType/new HP subtraction.

### Pinch grab

PinchBeetle HP40/speed.23/attack4/armor2, arthropod, dimensions1.2x.5; Float0/Charge2(speed1.5,canBreakfalse)/Melee4/stroll/look, retaliation/visiblePlayer. Protected ChargeAttackGoal reused: snapshot approach,windup15+rand30,rangeSq16..64,random1/10,onGround/LOS,one attack attempt includingwindup,marks attempted beforehurt, no terrainbreak here. doHurtTarget first ifno passengers and victimvehicle absent OR not RIDES_OBSTRUCT_SNATCHING: stopRiding then startRiding(beetle,true); capture attempts occur BEFORE damage, no c:bosses/Player-only or hurt-success check. Force still retains native mount event but bypasses ordinary canRide/capacity predicates; stopRiding may be vetoed by hostilemount hook, later native checks remain. Capture failure doesnot skipdamage. Captured passengers use protected HostileMountEvents dismount prevention/interaction; this is not Yeti throw timer. aiStep aftersuper assigns dimensions=getDimensions (no explicit refreshDimensions here), carrieddefault2.2x1.6, otherwise1.2x.5. Firstpassenger mismatch removes it; look100 and Livingpassenger becomes currenttarget. InvulnerablePlayer stopRiding/cleartarget. Attachment(0,eyeHeight,.75), canRiderInteracttrue. knockback override skips super entirely while carrying; not blanket immunity to every velocity API. die asks allpassengers stopRiding before superdie; native hooks/liveness matter. No custom HPgate/regen/throw/proprietary save resource.

### Pinch damage

PinchBeetle doHurtTarget always returns EntityUtil.properlyApplyCustomDamageSource(attacker=self,target,CLAMPEDsource,null) after possiblegrab. Source direct=causingPinchBeetle, requested effectiveATTACK_DAMAGE default4 plus native enchantment calculation. CLAMPED tagged neoforge:is_physical and minecraft:no_knockback only in scoped mergedsource tags; not armor/shield/Resistance/enchantment/iframe bypass. no_knockback suppresses native hurt recoil, not a categorical prohibition on independent helper knockback/capture. Shared TF helper uses attacker as affectedEntity in modifyDamage, and on success sets lastHurtMob toattacker itself; exact previously reviewed semantics reused, no corrective rewrite. Helper native knockback and postattack callbacks only on hurttrue; capture independent. Source request survives blocked/false capture. Capture may succeed even damagefalse/zeroHP. Newcustomprofile CLAMPED USED, sole runtimeTF fieldcaller PinchBeetle.doHurtTarget.

### Pinch boat

PinchBeetle startRiding(Boat,force) kills boat BEFORE superclass/mount event or capacity checks, optionally drops3 variantplanks+2sticks under doEntityDrops, playssound,returnsfalse. NonBoat delegatesordinary. Boat.kill inherits Entity.kill: remove(KILLED)+ENTITY_DIE, no DamageSource/hurt/HP request. Legitimate producer is native Boat.tick collision pickup: server, controllingpassenger notPlayer, own passenger count<2, candidate notpassenger, candidate.width<boat.width, Living nonWaterAnimal nonPlayer, notcarryingboat, in inflated(.2,-.01,.2) pushableBy query. Pinch width1.2 fits normalboat1.375 when unladen; carried2.2 fails width. Exact loader method uses hasEnoughSpaceFor with samewidth rule; not arbitrary boat contact or a damage resistance bypass event. Boat ride-obstruction tag for grabbing a boatpassenger is a different predicate, not this producer.

### Yeti anger

Ordinary Yeti HP20/speed.38/attack0/follow4,1.4x2.4, freezeimmune. Float0/ThrowRider1/strolllook/retaliation/visiblePlayer; no ordinary melee goal separate from shared ThrowRider. hurt beforeSuper: causingentitynonnull and !source.isCreativePlayer =>setAngrytrue, even if laterhurtfalse; exact creativePlayer owner predicate, not just source directentity. Anger flag adds FOLLOW_RANGE +8 ADD_VALUE=>12, no damage/speed/heal buff. NBT Angry restores modifier; installed callercensus only hurt(true) and readAdditionalSaveData(savedvalue), no native timed reset. Ownerless/creative sources do not addanger but do not clear existinganger. Ordinary damage admission remains. Native ThrowRiderGoal, hostilemount hooks, playerlaunch state and later exactFALL->YEETED are already fully reviewed in R2f7; reuse alpha_yeti_throw and alpha_yeti_thrown_fall, no duplicate packages or new DamageTypecount. Yeti anonymous wrapper only adds grab/throw sounds; mountposition(0,height,.4), look100,canRiderInteracttrue. Sharedthrow excludes boss-tagged victims and obstructingrides; no immediateHP atlaunch, unlike Pinchclamp. Yeti has no boss bomb/rampage/projectileimmunity mechanic. Natural spawn:nonPeaceful, SnowyForest bypasses lighttest but requires basecheckMobSpawnRules; otherbiomes custom skylight/random32 and blockbrightness/random8 checks plusbasecheck. No required progression/HPphase.

## Packages

| Mechanic | Primary classification |
|---|---|
| Mounted goblin knight coupling | CUSTOM_CONTROL |
| Goblin knight shared shield resource | CUSTOM_RESOURCE |
| Directional goblin armor stripping | VANILLA_LIKE_EXTENDED |
| Timed heavy spear area attack | VANILLA_LIKE_EXTENDED |
| Pinch Beetle capture and carrying | CUSTOM_CONTROL |
| Pinch Beetle clamped damage | CUSTOM_DAMAGE |
| Pinch Beetle boat destruction on pickup | BINARY_MECHANIC |
| Ordinary Yeti hurt-triggered persistent anger | CUSTOM_CONTROL |

## Custom source callers

| Type | Amount | Source identity |
|---|---|---|
| twilightforest:clamped | Effective attackattribute default4 with shared native enchantment helper. | direct=causing=PinchBeetle |

## Scope and exclusions

- All nine declared class surfaces fully pinned, including three anonymous wrappers; shared charge/throw/mount/helper and registrations reused.
- No duplicated Alpha Yeti launch/fall or shared charge mechanic; ordinary Yeti paths explicitly link protected package identities.
- Goblin heavy attribute104 is source-derived effective default, not observed HP or runtime guarantee. Exact timer/AI cadence limitation is documented without fixing it.
- Boat removal is a native custom entity-control mechanism, not a DamageType or HP attack.
- Particles, sounds, dimensions, ordinary goals/attributes and loot are covered where relevant, not inflated into separate status packages.
- Remaining17 custom caller profiles and other Twilight content unfinished; zero promotion.

## Future native controls

- Both mounted knight HP pools; all angle boundaries/causer positions/axe owner choices/amount thresholds; finalshieldbreak vsHP; armorstrip beforelate rejection.
- Native heavywindup from Upper and delegatedLower; both AIparities/targetloss/NoAI/vehicledeath/effectiveattribute/enchantments/AABB exclusions/reload.
- Native Pinch capture and clamped independently: charge/melee/obstructingride/mountevent/failedhurt, carrierknockback/death/invulnerablePlayer.
- Native Boat pickup positive and negative predicates, boatkill/noDamageSource, dropgamerule.
- Ordinary Yeti anger/save/owner controls and existing sharednative throw/fall controls; no boss mechanic inference.

[Semantic packages and paths](semantic-sections/twilightforest-mounted-mobs.json), [integrity](twilightforest-mounted-mobs-integrity.json), [full validation](r2f8b-mounted-mobs-validation.json).

Exact next task: Continue Task C with BlockChainGoblin/SpikeBlock, GiantMiner/ArmoredGiant and remaining melee mobs/minibosses; then remaining items/scepters/armor/charms/projectiles/hazards/resources and17 unfinished custom profiles. Reuse protected mounted/ranged/boss/Frosted work. Protect every logical subsection toward R2f8, then final whole-Twilight dedup/promotion. No runtime boss/L2, Stage/production, fixes/balancing, Phase6/7. IceAndFire only after COMPLETE Twilight is pushed.
