# r2f8g - TWILIGHT_CONSTRUCTS_SLIMES_SEMANTIC_REVIEW_COMPLETE

Installed TF4.8.3345, raw Minecraft1.21.1 and exact NeoForge21.1.244. Native mob_attack direct=causing actual mob for ordinary Golem/Guardian/Slime hits, with ordinary armor, directional shield, Resistance/protection/absorption/cooldown/events and Player difficulty scaling. Slime contact has its own native caller, not ordinary Mob.doHurtTarget. Adherent uses the protected NatureBolt source contract. Native hurt true is admission, not measured HP loss. No new custom DamageType, runtime HP/SHP/L2/Stage or production claim.

Adds 5 reviewed packages / 21 delivery cases. Twilight remains PARTIAL at 112/326 drafts, zero promoted. REVIEW_REQUIRED 0.

## Native contracts

### Authority

Installed TF4.8.3345, raw Minecraft1.21.1 and exact NeoForge21.1.244. Native mob_attack direct=causing actual mob for ordinary Golem/Guardian/Slime hits, with ordinary armor, directional shield, Resistance/protection/absorption/cooldown/events and Player difficulty scaling. Slime contact has its own native caller, not ordinary Mob.doHurtTarget. Adherent uses the protected NatureBolt source contract. Native hurt true is admission, not measured HP loss. No new custom DamageType, runtime HP/SHP/L2/Stage or production claim.

### Golem

CarminiteGolem extends Monster, not IronGolem: actual registered HP40/speed.25/attack9/armor2, dimensions1.4x2.9, not fireproof. TF fall_damage_immune tag prevents native fall damage; no Poison immunity/regen/repair behavior or iron-ingot interaction inferred from name. Water path malus-1, melee1, water-avoiding stroll2 with probability0, look3, retaliation and visible Player targets; no Float goal. doHurtTarget calls super ordinary native melee, only on true sets attackTimer10, broadcasts4, and victim.push(0,.4,0). The extra vertical push is unconditional within that success branch, not scaled by victim knockback resistance and not a new damage source. Ordinary superclass knockback/enchantments remain. No push on false; later fall damage, if any, stays ordinary recipient fall mechanics, without TF throw/YEETED marking. Attack timer decrements in aiStep and is client animation state, not the native20-tick melee cooldown; it is not saved. Clustermax2, sprint particles/ambient red dust cosmetic. No custom incoming hurt/death/boss phase.

### Maze size

MazeSlime extends native Slime and is registered with Monster.createMonsterAttributes, dimensions.52x.52/eye.325 before size scaling. Native Slime.setSize clamps n to1..127, sets size/dimensions, base MAX_HEALTH=n*n, speed=.2+.1*n, attack=n; ordinary max-health attribute caps at1024. TF override then addOrReplacePermanentModifier id twilightforest:double_health, amount2, ADD_MULTIPLIED_BASE, and ALWAYS setHealth(getMaxHealth()), even resetHealth=false; xpReward uses requested size+3. With ordinary unmodified attributes, effective maximum is min(3*n*n,1024), NOT2*n*n. Natural finalized sizes1/2/4 therefore HP3/12/48, attack1/2/4 and speed.3/.4/.6. This is native HP assignment at size change, not regeneration or a separate DamageSource. Same modifier ID replaces rather than stacking on repeated setSize. External attributes/effects can change final values; no balancing change introduced.

### Maze spawn save

Registered Maze placement is nonPeaceful && checkMobSpawnRules && Monster.isDarkEnoughToSpawn, not vanilla slime-chunk/moon/Y spawning. Inherited finalize chooses i=nextInt3; if i<2 and randomFloat<.5*specialDifficultyMultiplier increment; setSize(1<<i,true) then super finalization. Actual initialized size/HP must be observed, not constructor defaults or an unfinalized test entity. Native NBT stores Size=n-1 and wasOnGround plus normal Living health/attributes. Exact244 Slime.readAdditionalSaveData calls virtual setSize(storedSize+1,false) BEFORE superclass loading; TF temporarily fills health there, then native Living load restores saved Health and attributes. Thus this override alone does NOT prove free healing on ordinary reload. Persistent modifier ID survives native attribute serialization without intentional stacking. Native command with explicit NBT can skip randomization, while ordinary command without NBT finalizes; those are different initial states, not production fixes.

### Maze contact

MazeSlime.isDealsDamage returns true unconditionally, removing BOTH vanilla !isTiny and isEffectiveAi predicates. Native playerTouch and push(IronGolem) call Slime.dealDamage; ordinary Entity push occurs before the IronGolem damage branch. Recipient need not be current target. dealDamage requires slime alive, native melee AABB range and LOS, requests mob_attack effective ATTACK_DAMAGE (normally size n), then only true plays hit sound and native server post-attack enchantments. It does not call EnchantmentHelper.modifyDamage or ordinary Mob melee helper, add a bespoke cooldown, extra vertical launch, poison or armor penetration. Repeated contact is limited by native collision dispatch and recipient damage cooldown. Size1 is therefore dangerous; NoAI alone does not restore the removed contact gate, though all remaining native hurt/LOS/range checks remain. No guarantee of a hit every tick or actual HP loss.

### Maze ai

Inherited native slime AI: Player target requires |targetY-slimeY|<=4 and ordinary visible targeting, plus IronGolem target. SlimeAttackGoal LOOK requires attackable current target and SlimeMoveControl; every-tick goal looks and supplies isDealsDamage as aggressive flag. Its own tired counter uses reducedTickDelay300 and continuation decrements; it does not itself damage. MoveControl turns up to90 degrees, consumes MOVE_TO, uses speedModifier*movement attribute. On ground jumpDelay postdecrements; reset random10..29 divided by3 while aggressive (integer3..9), so the postdecrement cadence is distinct from that stored number; waiting sets forward/side/speed0. Float goal in water/lava requests speed1.2 and80% jump; keep-jumping requires notPassenger, speed1. Random direction LOOK applies without target while grounded/in water/lava/Levitation. Native jump hook retained. TF landing particles and sounds are cosmetic, not splash damage.

### Maze split

Native Slime.remove: server && size>1 && isDeadOrDying -> choose2+nextInt3 children, size integer parent/2, create via actual entity type (MazeSlime). Copies name, NoAI, invulnerable and persistence-required flag, calls child.setSize(j,true), positions offsets from parent dimensions; no inherited low HP, owner or shared health pool. TF override yields fresh child HP3*j*j (native max clamp applies). Exact244 posts MobSplitEvent after preparing children; only notCanceled adds them, then parent removal proceeds regardless. No split for size1, living unload/removal, client side or missing child creation; no native finalizeSpawn call for children and no independent TF summon code. Removal reason alone is not the test: dead/dying state matters. Size4 native child sizes2 then1 can still deal contact damage. This inherited split is a delivery of the size/contact packages, not a newly invented custom summon type.

### Maze tags

TF adds MazeSlime to immune_to_oozing and frog_food. Native Living effect eligibility rejects Oozing for the former; no blanket all-effect or Poison immunity. Frog.canEat rejects any Slime whose size!=1, then checks frog_food, so only tiny MazeSlime is eligible in this path. Native ShootTongue additionally requires attack-target memory, no panic, path distance<1.75 and not croaking; on close approach it pulls the target toward Frog with velocity magnitude.75 and after catch animation calls Frog.doHurtTarget (ordinary native attack attribute10 before modifications), removes entity only if it is then dead. Not an unconditional instant kill, and no Maze child split at size1. This is a proven native consumer of the tag, documented for incoming-source coverage rather than a TF-specific outgoing attack.

### Guardian equipment

SnowGuardian extends protected BaseIceMob; actual registered HP10/speed.23/base attack3, dimensions.6x1.8, cluster2. Native finalize calls super then one random type nextInt4 and equips ONLY MAINHAND, CHEST, HEAD, then ordinary spawn enchantments. makeItemForSlot has FEET/LEGS branches but this producer never calls them; do not claim a full set. Type0 Ironwood sword+head/chest: mainhand+5 -> mob attack8, armor2+7=9/toughness0. Type1 Steeleaf sword+6 -> attack9, armor3+8=11/toughness0. Type2 Knightmetal sword+6 -> attack9, armor11/toughness1+1=2. Type3 Arctic head/chest but KNIGHTMETAL sword -> attack9, armor2+7=9/toughness2+2=4. Values are unenchanted settled native equipment defaults, not fixed final HP damage. No Fiery/Ice sword or automatic Frosted attack. Parent Mob.doHurtTarget uses ordinary source/enchantments; it does not become a Player item hurtEnemy callback merely because a sword is equipped.

### Guardian knight

Native Knightmetal sword incoming-event contract is reused from R2f5: server target, direct Living attacker with nonempty mainhand KnightmetalSwordItem, target armorValue>0. If armor cover>0 adds int(2*cover), else+2 for armor attribute without worn pieces; quarter cover adds0, half1, full2. Applies to actual SnowGuardian types2/3 with ordinary mob_attack, after Player difficulty scaling and before mitigation; does not turn it into HAUNT, bypass armor or guarantee hurt success. Types0/1 fail that weapon predicate. Native spawn enchantments/attribute updates and current equipment can alter results; no duplicate Knightmetal bonus implementation or production change.

### Guardian body

SnowGuardian normal Float/Melee/stroll/look, retaliation/visible Player targeting. Reuses BaseIceMob downward airborne velocity*.6 before super.aiStep, no flying navigation or perpetual hovering. In actual SNOW_GOLEM_MELTS biome every tickCount%20==0 parent requests ownerless minecraft:on_fire1; no own success dependency or bespoke server guard, normal fire resistance/immunity/event pipeline applies. TF tags grant fall damage immunity, freezing immunity and powder-snow walking, not fire immunity. No ordinary attack applies Frosted, no IceCrystal summon lifetime timer, no projectile, HP phase or death burst. Extra client snow particles are cosmetic. Normal HP/equipment save/load and armor processing remain; protected BaseIce behavior is linked rather than re-researched as a new effect.

### Adherent

Adherent IS registered (unlike excluded Boggard), HP20/speed.25/base attack2, dimensions.8x2.2, not fireproof, no egg colors and no world-generation producer reference found by scoped TF field-caller census. Registered spawn placement uses Monster.checkMonsterSpawnRules; placement eligibility does not prove ambient biome spawning. A native registered-entity command is an administrative delivery path, explicitly not a survival acquisition claim. Goals Float1, RestrictSun2, FleeSun3, RangedAttackGoal4(speed1,interval60,range10), stroll/look, retaliation/visible Player. Native ranged goal requires every-tick updates and its ordinary target/range/LOS/navigation/cooldown rules. performRangedAttack creates protected NatureBolt owned by Adherent, aims targetY+eyeHeight-1.1, horizontal aim elevation+.2*distance, speed.6, inaccuracy10-4*difficultyId (Peaceful10/Easy6/Normal2/Hard-2; no TF clamp). extraDamage argument ignored. Native shooting math uses the signed value; no fabricated Hard accuracy clamp. Protected leaf_brain2, poison-on-success, terrain/parry/source-ownership semantics all remain. Synced CHARGE_FLAG starts false; setter/getter exist but no charging goal or bespoke charge attack is registered; no reason to invent charge damage or a timed phase. No mount, new hurt/death override or native equipment attack.

### Harbinger exclusion

HarbingerCube IS registered with HP40/speed.23/base attack2, dimensions1.9x2.4 and fireproof=true; ordinary Monster placement, no spawn egg colors and no world producer reference in scoped TF field-caller scan. Its declared goals are Float/stroll/look and retaliation/visible Player target selection only: no melee/ranged/charge/attack callback, collision payload, resource, boss phase or death override. Having an attack attribute/target does not prove active damage delivery. A native registered summon can exhibit its ordinary passive navigation/target/fireproof state, but no custom combat mechanic or invented ominous/annihilation ability is cataloged. Other mods dynamically adding behavior are outside this native proof.

### Producers

CarminiteGolem, MazeSlime and SnowGuardian have native spawn eggs and registered attributes/placement. DarkTower controlled spawn config: Golem weight10/group1..2; DarkTowerWing.decorateSpawner size>9 randomly selects Golem or Broodling, smaller wings select Broodling only, then native rotated spawner placement. Labyrinth controlled config: MazeSlime weight10/group2..4; actual engine cap/placement/finalization still apply. AuroraPalace controlled config: Guardian weight10/group1..2. Adherent/Harbinger registrations have no egg and no proved world producer; ordinary registered SummonCommand.createEntity loads registered entity NBT, checks world bounds/UUID and adds native passenger tree, optionally native COMMAND finalizes when randomizeProperties true. Native summon is a future administrative positive control, not a code-injected entity or fabricated damage source. No runtime commands were executed.

## Packages

| Mechanic | Primary classification |
|---|---|
| Carminite Golem admitted melee and vertical push | VANILLA_COMPOSITE |
| Maze Slime size and threefold native health | VANILLA_LIKE_EXTENDED |
| Maze Slime tiny and NoAI contact admission | VANILLA_LIKE_EXTENDED |
| Snow Guardian actual equipment and inherited ice behavior | VANILLA_COMPOSITE |
| Registered Adherent native NatureBolt producer | VANILLA_COMPOSITE |

## Custom source callers

| Type | Amount | Source identity |
|---|---|---|

## Scope and exclusions

- Six full native class surfaces plus actual world producers and equipment registrations. Raw/exact244 native Slime and relevant inherited AI, split and load ordering pinned.
- Harbinger is registered but has no attack goal/callback; ordinary navigation/target/fireproof behavior is an assessed exclusion, not invented damage. Unlike Boggard, it has a legitimate administrative summon path, but no unique effect package.
- Adherent has registered native ranged behavior, no proved survival world producer or egg. Command source explicitly labeled administrative; no runtime commands run.
- Protected BaseIce, NatureBolt and Knightmetal packages are reused. Final deduplication must preserve their distinct Guardian/Adherent source parameters without duplicating the shared effect.
- Particles/sounds and ordinary equipment drop/repair are not new damage/status packages. Maze split inherits native control and feeds existing size/contact packages.
- No new custom declaration resolved:26/40 reviewed,14 unfinished. Twilight PARTIAL, zero promoted, no IceAndFire yet.

## Future native controls

- Golem native melee9 and successful-only vertical push; ordinary armor2/fall immunity and false-hurt controls.
- Maze native size1/2/4 health3/12/48, attribute identity/clamps, damage persistence across ordinary reload and native split event/child state.
- Maze Player/IronGolem contact, size1/NoAI behavior, LOS/range/cooldown, Oozing immunity and genuine native Frog consumer.
- Guardian all four actual three-slot loadouts, native enchantments/armor and protected Knightmetal/BaseIce behavior.
- Registered Adherent native command producer and NatureBolt parameters, parry/ownership/poison controls; registered Harbinger no-attack exclusion.

[Semantic packages and paths](semantic-sections/twilightforest-constructs-slimes.json), [integrity](twilightforest-constructs-slimes-integrity.json), [full validation](r2f8g-constructs-slimes-validation.json).

Exact next task: Continue Task C with Wraith and Minotaur remaining body coverage, RisingZombie and its graveyard producers, LoyalZombie/ZombieWand and native recharge/feed/expiry; then remaining utility/passive entity exclusions, items/scepters/armor/charms/projectiles/hazards/resources and14 custom caller profiles. Reuse all protected boss/Frosted/ranged/mounted/chain/giant/arthropod/tactical/construct-slime work. Protect each subsection toward R2f8 and final Twilight promotion. IceAndFire only after Twilight COMPLETE is pushed; no runtime boss/L2/Stage/production/fixes/Phase6/7.
