# r2f8a - TWILIGHT_RANGED_MOBS_SEMANTIC_REVIEW_COMPLETE

Static installed Twilight4.8.3345 / raw Minecraft1.21.1 / exact NeoForge21.1.244. Existing four conditional compat scans reused; no runtime boss/L2 tests or production/Stage changes.

Adds 13 reviewed packages / 28 delivery cases. Twilight remains PARTIAL at 73/195 drafts, zero promoted. REVIEW_REQUIRED 0.

## Native contracts

### Shared pipeline

Protected Minecraft1.21.1/exact NeoForge21.1.244 Living/Player hurt, native effects, ranged-goal, projectile/impact/parry, explosion and BaseIceMob evidence is reused. Source identity/tags/difficulty, armor/shield, Resistance/protection, absorption/cooldown/events and effect eligibility remain native. True hurt is not actual HP loss. Native mob-owned when_caused_by_living_non_player scales Player requests Peaceful0/Easy min(a/2+1,a)/Normal a/Hard1.5a. Status addEffect(effect) calls here provide no explicit attacker; ordinary merge/immunity/cures/events apply. No runtime HP/SHP or L2/Stage claim.

### Breath goal

BreathAttackGoal is shared by FireBeetle and WinterWolf: MOVE/LOOK/JUMP, range5/duration30/chance.1. canUse selects getLastHurtByMob, NOT getTarget; requires range<=5, sensingLOS, alive Living and noncreative/nonspectator before random chance. Saves target eye-position once. start duration30/breathingtrue; continue requires duration>0, host/targetalive, current range/LOS and eligibility. tick decrements, look/face toward SAVED position (100 degree limits); after elapsed>5 calls getHeadLookTarget and attacks one selected winner. Default goal cadence, not30 guaranteed game ticks. Selection ray is30 long from hostY+.25, but candidate box is hostBB moved view*3 and inflated.5, not a swept30-block volume. Live Living/pickable/nonself/noncreative/nonspectator only; own parts removed. Nearest intersection selected before one attack, no block clip; target can be different from retaliation target. Contains-origin sets distance0 sentinel, so subsequent intersection may replace it. Continuation LOS to retaliation target is not a separate ray-winner LOS check. stop duration0/targetnull/breathfalse; state/timers unsaved.

### Fire beetle

FireBeetle HP25/speed.23/attack4, registered1.1x.5 FIREPROOF; arthropod and freeze_hurts_extra_types. Float0/Breath2/Melee3/stroll; retaliation/nearest visible Player. Native breath winner first !target.fireImmune, then scorched2 direct=causing=FireBeetle, true=>ignite10 seconds. Fire Resistance/native fire admission may reject before success; later burning is ownerless on_fire, separate. doHurtTarget while breathing instead requests scorched2, no explicit fireImmune precheck, no ignite and no normal melee helper enchantment/knockback callbacks; otherwise superclass ordinary mob_attack effectiveattack4. Normal AI breath occupies melee flags; callback branch still records the native method, not a guarantee both goals execute together. scorched fire/ignites_armor_stands, no armor/shield bypass/projectile/explosion tag; normal mitigation. Breath particles/gameevents/sounds are not projectiles or extra hits.

### Wolf baseline

HostileWolf is Monster, not tameable Wolf. HP20/speed.3/attack2; Float, native LeapAtTarget(.4), ordinary melee, wander/look; retaliation ignores HostileWolf damage for that goal, nearest Player, wolf-prey Animal, baby-on-land Turtle and AbstractSkeleton targets. Leap wrapper only toggles aggressive animation on start/stop; native leap requires no controlling passenger, target distanceSquared4..16, onGround/random reducedTickDelay5; sets motion toward target with existing momentum, no independent damage. Variant is saved appearance, not combat resource. Mist/Winter override HP30/attack6, dimensions1.4x1.9, notfireproof. All ordinary source admission/death remain; no added HP phase/regeneration/defense override. Winter replaces goal/target list with Float/Breath/Melee/stroll and retaliation/Player, so no inherited leap/prey selector in its actual registerGoals.

### Winter breath

WinterWolf shares the reviewed retaliation breath goal but doBreathAttack requests minecraft:mob_attack2 direct=causing=WinterWolf, ignores hurt bool, no ignite/freeze/Frosted/Slowness/projectile. Native melee remains effectiveattack6. Freeze immune entity tag is recipient defense, not outgoing elemental damage. Winter canSpawnHere expression is (nonPeaceful && exactSnowyForestBiome) OR Monster.isDarkEnoughToSpawn; no parentheses importing the nonPeaceful predicate into the second branch and no base checkMobSpawnRules in that method. Native spawn engine and later Monster Peaceful despawn still apply. Breathing flag unsaved; visual snow is not damage evidence.

### Mist blindness

MistWolf only modifies successful superclass melee: inspect integer getMaxLocalRawBrightness at WOLF position castfloat, requires<.1 (therefore level0), Living victim, and wolf current block !isSolid. Then native Blindness amplifier0: Easy0/noadd, Hard15*20, default7*20 (Normal and Peaceful branch; Player Peaceful hurt usually rejected first). Effect application is success-dependent, may be refused/merged normally; ordinary melee damage6 native mitigation remains. No darkness effect, invisibility, magical outgoing source or damage immunity. HostileWolf leap/target behavior inherited.

### Nature bolt

SkeletonDruid main-hand Hoe creates native NatureBolt ownerDruid, speed.6/inaccuracy6, aim targetEyeY-2.7-shooterY plus horizontalDistance*.2; gravity.003. TFThrowable/ITFProjectile, .25 square. onHitEntity calls super, then Living only, owner==null OR victim!=owner && victim!=owner.vehicle, then leaf_brain2 direct=bolt/causing=currentowner. Only true hurt and difficulty!=Peaceful applies Poison amp0 Easy/Normal60 ticks, Hard140. No poison if failed hurt or owner/vehicle gate; native recipient immunity/effect events remain. Source is magic/projectile, bypasses ordinary armor/transitively shield/wolf armor, witch-resistant; normal Resistance/protection/projectile protection/absorption/cooldown. onHit superclass then server particle3/discard regardless hurt; block case separate. No explicit custom entity-hit server check, but native hurt rejects client. Inherited projectile owner serialization retained, no custom payload state lost on load.

### Nature terrain

NatureBolt onHitBlock first superclass block callback. If canEntityGrief(projectile), server BonemealableBlock valid target calls performBonemeal directly (no isBonemealSuccess probability or bonemeal item/event consumption). Else if solid && canReplaceBlock: no blockentity, solidRender, DRUID_PROJECTILE_REPLACEABLE tag and EntityUtil.canDestroyBlock then persistent BIRCH_LEAVES setBlockAndUpdate. Else branch has no explicit server guard; native delivery/world authority remains. Owner immunity on entities does not stop terrain callback. Standard onHit server discard follows. Tag content/resources pinned; no arbitrary block replacement or duplicated Frosted/ice terrain.

### Poison comparison

Raw PoisonMobEffect amp0 checks every25 duration ticks and, only currentHP>1, requests ownerless minecraft:magic1. Installed NeoForge21.1.244 replaces holder with neoforge:poison when registered (fallback minecraft:magic), still ownerless1/nativehurt/no direct subtraction. This is subsequent poison source, not leaf_brain and not projectile. Ordinary native effect application checks immunity tags/events and merges/cures; toxin does not inherit bolt owner, duration refresh does not guarantee additional immediate damage, and rejected damage still ages. Slowness in TomeBolt is native MOVEMENT_SLOWDOWN amp1 (movement modifier-.15*(amp+1)=-.30), no custom frozen buildup.

### Druid state

SkeletonDruid extends AbstractSkeleton and uses its attributes (HP20, movement.25, base attack2) and ordinary sunburn/equipment protection, skeleton tags/targeting/armor/enchantment setup. registerGoals calls super then priority4 RangedAttackGoal speed1.25/60/range5. Server reassess removes this ranged goal; Hoe mainhand adds it but does NOT remove preexisting inherited melee/bow goals (unlike calling super branch). NonHoe calls inherited reassess (BowItem accepts native mod bows under exact NeoForge); native equal-priority MOVE/LOOK arbitration decides retained goal competition. performRangedAttack Hoe=>NatureBolt, STICK=>no projectile, other item=>inherited arrow. Inherited arrow factory/customArrow and equipment/enchantments remain. Adult default goldenhoe, baby stick. setBaby syncs flag, server transient speed+.5 ADD_MULTIPLIED_BASE, dimensions half/eye.93; NBT IsBaby restores modifier, no age countdown/grow-up. SwarmSpider native summonJockey called after finalizeSpawn: existing passenger OR randInt200==0, creates babyDruid before finalizeSpawn(JOCKEY), ejects prior passenger if any, startRiding(spider), no separate addFreshEntity here (caller passenger-tree insertion matters). Full SwarmSpider review remains separate. Baby control changes native equipment/AI, not custom status.

### Tome bolt

DeathTome normal ranged goal speed1/100/range5; actual projectile ownerTome, speed.6/inaccuracy6, aim targetEyeY-1.1-projectileY+.2*horizontalDistance; gravity.003. TomeBolt TFThrowable/ITFProjectile .25 square. onHit special early return when ownernonnull, BlockHit same blockPos as owner and that block Lectern: skips superclass and discard; no block-owner tag magic. Otherwise superclass; Living hit randomBoolean chooses lost_words OR schooled, request3 direct=bolt/causing=currentowner. True=>SlownessII amp1 Easy40, Normal120, otherwise160 ticks; no explicit Peaceful exclusion (native Player scaling often prevents true). Both types same magic/projectile/armor+shield+wolf-bypass/witch-resistant tags and scaling, distinct identity/deathtext. Hit misses/nonLiving/false hurt still discard server after superclass. No direct projectile HP, homing, Frosted or enchantment-specific damage added. Owner/speed serialize through parent, no custom state lost.

### Tome lectern

DeathTome HP20/speed.25/flying.6/attack4, root.75x1.5, notfireproof; fall immune tag and empty checkFallDamage, cannot ride. FlyingMoveControl(10,false), flying navigation prefers support below, no door open/float but passdoors. DATA_LECTERN saved on_lectern; persistence required whiletrue. Native producers: LichTowerWingRoom.putTrappableLectern(putMimic) places lectern HAS_BOOK=false, creates persistent positioned tome, setsflagtrue/finalizes STRUCTURE/addWithPassengers. MiscEvents registered RightClickBlock DeathTome SpawnEgg on empty lectern cancels ordinary interaction, server native EntityType.spawn(pos.below,SPAWN_EGG,true,false), ifnonnull consumes egg respectingPlayerabilities and setsflagtrue. On lectern aiStep aligns facing, manually server targetSelector.tick and RETURNS withoutsuper; targetnonnull releasesflag, velocity(0,.25,0), immediate ranged shot. Missing Lectern clearsflag then ordinary AI. Lectern Player target finds nearest within3, !shift, noncreative/nonspectator and view-dot>.75 plus VISUAL/FluidNONE LOS to one ofthree tomeY samples (range<=128, samelevel). Normal off-lectern target is native nearestvisiblePlayer; retaliation also exists. Hurt true with doubled-or-normal request>0 releases/lifts and rolls hurtloot; false does not release. Offlectern descending airborneY*.6 AFTERsuper; no regeneration or boss-style damage gate.

### Tome fire

DeathTome hurt multiplies IS_FIRE input by2 BEFOREsuper/native incoming event/mitigation, including on_fire/lava/etc taggedfire; no damage source replacement and no special cold weakness. True and modifiedrequest>0 triggers lectern release and native hurtloot even if actual HP loss0; absent guard does not mean unconditional loot per attemptedhit. Fire Resistance/native invulnerability can reject. Loot is excluded as separate combat mechanic. Saved native HP plus on_lectern, no custom recovery resource.

### Slime blob

SlimeBeetle HP25/speed.23/attack4 root.9x.5 arthropod; Float0, AvoidPlayer2 range3 speeds1.25/2, native Ranged3 speed1/30/range10, wander/look, retaliation/nearestvisiblePlayer. No melee goal despite attackattribute4. Shoots SlimeProjectile ownerBeetle speed.6/inaccuracy6, eyeY-1.1-projectileY+.2*horizontalDistance. Projectile TFThrowable/ITFProjectile .25 square, gravity.006; server Living hit requests ordinary minecraft:thrown4 direct=projectile/causingowner, return ignored, no Slowness/slime status. onHit super then die server(sound/discard/particle), including block or failed damage. hurt calls super but ignores it, then die and returns true regardlessamount/source, even if superclass false; this is projectile disposal not reflection/HP. Native isPickable remainsfalse, so do not invent normal Player melee targeting. No custom save override; parent owner/motion retained. Thrown tag/armor/directional shield/Resistance/protection/projectile protection/absorption/cooldown remain.

### Ice snowball

StableIceCore extends protected BaseIceMob: defaultHP20/speed.23/attack3, .8x1.8; freeze/fallimmune, snowwalkable, notfireproof; inherited descendingY*.6/no riding/warm-biome ownerless on_fire1 per20 ticks. Float0/Ranged1 speed1.25/20/range10, roam/look, retaliation/nearestvisiblePlayer. Shoots IceSnowball ownercore at own eye, targetEyeY-1.4-snowballY+.2*horizontalDistance, speed1.6/inaccuracy6; gravity.006. Projectile TFThrowable/ITFProjectile .25 square. Server Living hit snowball_fight2 direct=projectile/causingowner, ignoresbool; no vanilla Snowball Blaze3 branch, no Frosted or freezing gauge. Source magic/projectile, NO armor/shield/wolfarmor bypass and NO IS_FREEZING even though DamageEffects.FREEZING selects hurt audiovisual. onHit super then server discard/particle; hurt ignores super result then die/true. Not normally pickable; inherited serialization retainsowner/motion. IceCrystal/BaseIceMob evidence reused rather than duplicated.

### Unstable death

UnstableIceCore is separate BaseIceMob melee producer (Float0/Melee1 speed1/roam/look, retaliation/Player); defaultHP20/speed.23/attack3, same dimensions/freeze/fallimmunity/descent/warm-biome on_fire as Stable. It is NOT Stable subclass and never calls IceSnowball. tickDeath increments; only deathTime==60 server captures canEntityGrief then Level.explode(this,position,radius1,interactionMOB), nofire, and independently ifcapturedtrue transformBlocks. Afterwards deathTime=19, super.tickDeath removesat20, then assigns60. Native explosion events/LOS/exposure/armor/Resistance/blast protection/cooldown/knockback remain; source direct=causing=Livingcore, factorytype minecraft:player_explosion despite owner notPlayer, scalingALWAYS. Separate transform still executes after an explosion canceled internally because caller ignores explode return. No directHP/subtraction/heal/ice status. Native DeathTime serialization preserves delayeddeathtiming; core declares no custom save methods.

### Unstable terrain

At delayed death with captured canEntityGrief true, loops dx/dy/dz=-4..4 inclusive729 candidates; each has independent radius4+(randFloat-randFloat)*2, strictEuclideandistance<radius. transformBlock requires block explosionResistance<8 and state destroySpeed>=0. First: nonair/fullblock collision shape && (!solid || LEAVES || exactICE || TF AURORA_BLOCK) =>nearest dye STAINED_GLASS. Else nonair/redstoneConductor=>nearest-dyeTERRACOTTA. Nearest dye minimizes sum absoluteRGBdiff between block MAP color and dye TEXTURE color; first minimum wins. ColorUtil native maps to correspondingblocks. No BE/container/EntityUtil destroyhook predicate, no drop, setBlockAndUpdate; leaves/glass transform separate from actualexplosion destruction. No success/hurt/exposure dependency. Exact scope/predicates preserved, no fix.

### Projectile common

All four new payloads inherit ITFProjectile via TFThrowable. Native timed shield parry on server ProjectileImpactEvent: !external parry mod loaded, Living blocking within configured40 ticks, marker qualifies despite parryNonTwilightAttacks=false; AIM_DEFLECT transfers owner to blocker and cancels impact. It does not require successful normal shield hurt or front-direction check in this callback. Later source uses current owner, changes native difficulty/owner filters; no fabricated reflection source. Native impact hook/deflection may prevent onHit; ignored hurt result is downstream only. TFThrowable itself has no lifetime/discard override; no automatic custom timeout invented. These four are not in TF native REDIRECTABLE_PROJECTILE contribution; Aether deflectable tag exists for Nature/Slime/Ice, absent Tome, but consumer not asserted without installed Aether authority. Data tags are not implementation. Inherited normal projectile save/owner collision/leftOwner behavior reused; no payload class has custom NBT override.

## Packages

| Mechanic | Primary classification |
|---|---|
| Retaliation breath targeting and timing | CUSTOM_CONTROL |
| Fire Beetle scorching and ignition | CUSTOM_DAMAGE |
| Winter Wolf physical breath | VANILLA_LIKE_EXTENDED |
| Nature Bolt damage, poison and terrain | CUSTOM_DAMAGE |
| Druid equipment goals and permanent baby state | CUSTOM_CONTROL |
| Tome Bolt alternating source and Slowness | CUSTOM_DAMAGE |
| Lectern ambush and release control | CUSTOM_CONTROL |
| Death Tome fire vulnerability | VANILLA_LIKE_EXTENDED |
| Slime Beetle throwable damage and disposal | VANILLA_LIKE_EXTENDED |
| Stable Ice Core snowball package | CUSTOM_DAMAGE |
| Unstable Ice Core delayed explosion | VANILLA_LIKE_EXTENDED |
| Unstable Ice Core terrain transmutation | CUSTOM_CONTROL |
| Mist Wolf darkness-gated Blindness | VANILLA_LIKE_EXTENDED |

## Custom source callers

| Type | Amount | Source identity |
|---|---|---|
| twilightforest:scorched | 2; breath true ignites10 seconds, breathing melee doesnot | direct=causing=FireBeetle |
| twilightforest:leaf_brain | 2; true then Poison60/140 exceptPeaceful | direct=NatureBolt, causing=currentowner nullable |
| twilightforest:lost_words | 3 randomBoolean branch, true then SlownessII40/120/160 | direct=TomeBolt, causing=currentowner nullable |
| twilightforest:schooled | 3 complementary randomBoolean branch, same effect | direct=TomeBolt, causing=currentowner nullable |
| twilightforest:snowball_fight | 2 serverLiving, hurtreturnignored | direct=IceSnowball, causing=currentowner nullable |

## Scope and exclusions

- All18 declared native classes fully pinned/read, plus limited producer/registration/color witnesses; names are not evidence.
- HostileWolf ordinary melee/leap/variant, ordinary mob attributes/sounds/particles/loot are assessed but not each new package.
- BaseIceMob descent/melting/defense reused from protected IceCrystal review; no duplicate Frosted or IceBomb package.
- Full SwarmSpider behavior and SnowGuardian equipment are left to remaining mobs/items; only proven babyDruid producer included here.
- Custom source census advances only five actual callers; remaining18 are unfinished, not unused.
- No inference that all cold-looking attacks freeze, all slime-looking attacks slow, or all magic-tagged attacks bypassarmor.
- No runtime tests, balancing, fixes, production or Stage changes.

## Future native controls

- Legitimate retaliation-first FireBeetle/WinterWolf goal, snapshot/winner/LOS controls, native fire vs ordinarymob source.
- Adult/baby/equipped Druid with native hoe/Stick/Bow, NatureBolt Living/vehicle/terrain/parry/reload and subsequent installedpoison.
- Tome natural/structure/spawn-egg lectern producers, gaze/crouch/hurtwake, fireweakness, two sources/Slowness and parry/reload.
- SlimeBeetle/Core native shots, exact hurt/discard/owner handling, no inventedslow/Frosted.
- UnstableCore death60/nativeblast vs independenttransform, source/tags/exposure/grief/events/persistence.
- MistWolf brightness0/nonsolid/Easy/normal/Hard and native successful-melee controls.

[Semantic packages and paths](semantic-sections/twilightforest-ranged-mobs.json), [integrity](twilightforest-ranged-mobs-integrity.json), [full validation](r2f8a-ranged-mobs-validation.json).

Exact next task: Continue Task C: remaining melee/control mobs and minibosses, then weapons/scepters/staves/armor/charms/projectiles, hazards/resources, remaining18 custom DamageType profiles, compatibility/source/delivery/exclusion closure. Reuse protected ranged mobs, all bosses and Frosted. Protect each logical subsection toward R2f8; final Twilight promotion only after full closure. No runtime boss/L2, Stage/production, fixes/balancing, Phase6 or Phase7; Ice and Fire blocked until final Twilight checkpoint.
