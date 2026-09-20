# R2f3 — LICH_SEMANTIC_REVIEW_COMPLETE

Installed Twilight Forest4.8.3345, Minecraft1.21.1, NeoForge21.1.244. Static native review only; no boss/runtime/L2 testing. Frosted is unchanged. Twilight remains PARTIAL.

9 reviewed package drafts / 24 delivery cases / 14 shield-source cases. Zero final Twilight promotions.

## Requested semantic closure

### 1. Shield resource/count

Integer SHIELD_STRENGTH, default6, separate from MAX_HEALTH100. Each accepted break subtracts exactly1, independent of excess amount. Clone getter returns0. Boss bar in phase1 displays shield/current max_shield_strength, not HP.

### 2. Shield initialization

Synched default6; constructor then stores int(attribute twilightforest:max_shield_strength), default6/range0..1024. clone_count defaults2 and minion_count9 (same attribute range). Constructor copies int(minion_count) to reserve. finalizeSpawn equips Fortification Scepter; it does not grant additional shields. NBT explicitly saves/restores shield/reserve/clone UUIDs/master/baby count/hit counter; missing integer keys read0. Setter has no clamp or native refill.

### 3. Shield decrement

Only the non-bypassing shield branch with tagged source and raw incoming float amount>2 decrements1. All shield-branch exits return false. A failed tag/amount check may set lastHurtByMob from a Living causing entity; successful break branch does not do that. die can clear shield to0 but is not shield break.

### 4. Hurt ordering

Order: (1) teleport invisibility>0 rejects unless BYPASSES_INVULNERABILITY; (2) exact IN_WALL with target attempts teleport; (3) clone rejects unless bypass; (4) causing entity instanceof Lich rejects unconditionally; (5) non-bypass and shield>0 performs tag/strict>2 counter logic and returns false; (6) otherwise BaseTFBoss/super.hurt; (7) only true super return can trigger randomized survival teleport, then true. BaseTFBoss has no hurt override. IN_WALL teleport can set invisibility during this call without rechecking the first gate.

### 5. Exact phases

getPhase: clone OR shield>0 =>1; else reserve<=0 AND countMyMinions()<=0 =>3; otherwise2. No HP threshold defines the three phases. countMyMinions scans AABB(x,y,z,x+1,y+1,z+1).inflate(32,16,32), master identity==this; no explicit alive filter. Nearby owned minions outside that box do not keep phase2 active.

### 6. Shield versus normal HP

Shielded non-bypass hits never enter LivingEntity.hurt. Armor, Resistance, protection, absorption, ordinary hurt cooldown, incoming/pre/post damage hooks and HP subtraction are not reached for this branch. A normal untagged sword/arrow/explosion fails; amount<=2 fails even if tagged. Lich.hurt itself does not first repeat vanilla dead/client/invulnerable checks before counter processing. Delivery APIs can have their own earlier gates.

### 7. Tag sufficiency

breaks_lich_shields is necessary inside the ordinary shield branch but is NOT sufficient. Exactly five native values: twilightforest:lich_bolt, twilightforest:twilight_scepter, minecraft:magic, minecraft:indirect_magic, minecraft:sonic_boom. Bomb and neoforge:is_magic membership alone do not qualify. BYPASSES_INVULNERABILITY skips the shield mechanism and attempts HP damage instead of decrementing.

### 8. Additional predicates

To break normally: reach Lich.hurt through a legitimate delivery; teleport counter<=0; not a clone; causing entity not any Lich; shield>0; not bypassing invulnerability; tag match; argument strictly>2. No universal Player/direct-projectile/owner/nonally test is present in Lich.hurt. Projectile, potion, fang, Conduit and Warden predicates are separately retained in source_paths. Cloaked Bolt collision is rejected even before hurt.

### 9. Legitimate sources

All five tag identities and their native producers are resolved in source_paths. The raw Minecraft factory census has10 callers; LootCommand is a loot-context source only, Guardian default targeting excludes Lich, Poison and water requests fail, and the other producer families have explicit eligible paths. Reuse accepted Friends ice chunk, Cult fangs and Royal anvil/pearl/enderman paths conditionally. This closes Lich semantics against native Twilight/Minecraft and accepted prior sources, not arbitrary unreviewed mods or datapack additions.

### 10. Reflected projectile behavior

LichBolt is in minecraft:redirectable_projectile. Native Player.attack deflects AIM and returns before calling Bolt.hurt, provided attack hook/attackable/skipInteraction gates pass. AIM gives normalized look velocity (speed1), owner=Player. An admitted projectile hit on a redirectable bolt calls generic Projectile.onHit deflection with that projectile owner before its own onHitEntity. TF shield parry also calls AIM with blocking Living entity as owner and cancels impact. These are genuine transfer paths, distinct from Bolt.hurt fallback shoot(speed1.5,inaccuracy0.1).

### 11. Direct/causing/owner

Lich Bolt damage direct=this bolt, causing=current owner; optional excluded Lich EntityType affects death message only. Phase1 Bolt collision additionally requires owner instanceof Player; native Lich/clone-owned, ownerless and other-mob-owned bolts cannot collide with phase1 Lich. Local Bolt.canHitEntity does not call super: it excludes Bolt/Bomb/Wand targets and cloaked Lich, then allows other candidates; do not invent inherited owner-vehicle/pickability predicates. Wand does call super.canHitEntity, then excludes Bolt/Bomb. Lich.hurt rejects ANY causing Lich, including another boss or clone.

### 12. Ownership changes

Generic deflect executes callback, then setOwner(argument), then onDeflection. setOwner(null) is a no-op. Player/AIM/TF parry with nonnull owner transfer ownership. Bolt.hurt redirects using causing entity look, but only transfers if DIRECT entity is Living; indirect arrow damage alone does not transfer (the earlier generic onHit may already have done so). Later-phase Lich callback sets owner=Lich temporarily: a prior nonnull Player/Lich owner is restored by outer deflect; an initially ownerless projectile keeps the new Lich owner. Native projectile owner UUID serialization is inherited by Bolt/Bomb/Wand.

### 13. Breaking shield and HP

A shield decrement, including6->5 and1->0, returns false without super.hurt: same request causes no HP loss, no hurt cooldown and no standard successful-hit callback. Separate later requests from one compound delivery can damage HP after1->0: ownerless Wither Skull magic5 can break, then its distinct native explosion request can hit exposed Lich. Multiple fangs/Anvil sweep+AoE similarly remain distinct requests. Damage requests are not measured HP loss.

### 14. Final shield transition

At1->0 getPhase immediately becomes2 if reserve>0 or owned minion count>0; otherwise3. Default fresh Lich has reserve9, so phase2. No immediate HP damage, forced HP write or forced teleport is performed by shield break. Phase1 goal stops and despawns clones when goal scheduling observes loss of phase1; phase2 equips Zombie Scepter. Bossbar switches to HP on its next update.

### 15. Later damage admission

Phase2 and3 with zero shields both admit ordinary source identities into super.hurt; killing all minions is NOT a prerequisite for HP damage. Teleport gate and causing-Lich rejection still apply. BYPASSES_INVULNERABILITY can skip shield/clone/teleport gates but still cannot skip causing-Lich rejection; native subsequent gates remain. Native exact244 LivingEntity checks invulnerable/client/dead/fire-resistance, incoming event, shield, freezing/helmet changes, cooldown, armor/magic/absorption, pre/post hooks and death handling. True hurt need not mean positive HP loss.

### 16. Lich Bolt

Native main/clone phase1 and main phase2 attacks launch owner-bound Bolt from body offset at speed0.5/inaccuracy1; gravity0.001. Server admitted Living impact requests custom lich_bolt6, ignores return and broadcasts/discards. Block collision discards. Pickable radius1; ignoreExplosion=true. Later phases return deflection before onHit for tagged projectile with owner Player/Lich/null; another Living owner is not in that deflection predicate. The projectile remains alive after deflection; lastDeflectedBy suppresses repeated callback on the same entity but still suppresses onHit.

### 17. Lich Bomb

Native AI launch shares speed0.5/inaccuracy1, gravity0.001. CanHitEntity unconditionally excludes every Lich plus Bolt/Bomb/Wand, despite an earlier conditional Lich check. Admitted hit calls super.onHit then explode. hurt ignores super result; direct entity required; non-IS_EXPLOSION request explodes, IS_EXPLOSION returns true without detonation. Not a native melee-reflect path, and not redirectable_projectile; TF shield parry can still deflect because ITFProjectile. Explosion server radius2, fire=false, Interaction.NONE, explicit lich_bomb direct=bomb/causing=current owner; then discard. isOnFire=true is not a target ignition callback. Parent block onProjectileHit can still trigger native block reactions (e.g. lighting candles).

### 18. Clones

MASTER_LICH UUID presence defines clone even if master unresolved; getter shield0 but phase1 and normal hurt immunity. Default cap2 from attribute; tracked UUIDs resolved to Lich with getMaster()==this. Phase1 canUse phase1/tickCount>20/target!=null. Main synchronizes cooldown/cloak to clones, fires itself and all resolved clones at cooldown0/range<30; type choice nextInt(3)>0 gives next Bolt2/3 else Bomb1/3, cooldown100. At60 it teleports and on success requests at most one clone. Clone spawn uses LOS candidate, copies target/home/cloak, initial cooldown60+rand(3)-rand(3). During its active uncloaked goal an orphan seeks nonclone master with capacity nearby; absent/dead/non-phase1 master discards clone. Main goal stop/death despawns clones. Clones have real projectiles but no independent normal main firing branch.

### 19. Minions/summons/healing

Phase2 goal only nonclone, acts while uncloaked with target. At attackCooldown%15==0 and server reserve>0/count<3, attempts spawn then decrements reserve even if LOS position/addFreshEntity fails. Native finalized MOB_SUMMONED LichMinion is Zombie subclass with master reference, no default equipment/loot pickup. Hard baby chance nextInt(100)<=20 while babyCount<minion_count/4 (default permits up to3 successful babies), otherwise adult. Missing/dead master seeks nearby nonclone count<3 then native kill if unresolved; master field is not custom-saved. Super-hurt success from ANY causing Lich grants Speed200/amp2 and Strength200/amp1, restores prior target via lastHurtByMob; false gives no buff. Ordinary Zombie melee uses effective ATTACK_DAMAGE, source mob_attack, inherited burning barehand successful-hit ignition; buffs are native effects. Pop goal: nonclone damaged, popCooldown0 and visible tagged Mob nearby; after20..39 held-scepter countdown and uncloaked/server, discard first visible poppable then heal2, cooldown40. Absorb goal: HP<max/2 and own nearby minions>0; after countdown/uncloaked, discard first owned minion then heal its current HP, no LOS test or hurt-success requirement. These discard/heal operations create NO DamageSource and are not player Lifedrain Scepter damage. Normal heal hook/clamp remains. Pop tag includes skeletons,zombie,enderman,spider,creeper,swarm_spider and removes #c:bosses. Inherited Zombie behavior remains: registered Zombie attributes (base HP20, attack3, armor2, speed0.23), baby speed modifier+0.5 total; native finalization randomizes reinforcement chance, knockback/follow range and possible leader HP/door modifiers, so20 is not a universal finalized minion HP. Sun exposure ignites8s unless headwear protects. Barehand burning successful melee can ignite for2*int(effectiveDifficulty) seconds at chance0.3*effectiveDifficulty. Hard, mob-spawning-enabled successful hurt can spawn ordinary Zombie reinforcements after native chance/space/player-distance checks; these are not LichMinion and do not consume/count the Lich reserve. Underwater600ticks then conversion300 (native predecrement completion) can convert to ordinary Drowned through loader conversion hooks, losing LichMinion type/count. Native ZombieGroupData allows baby jockey handling; minion spawn calls addFreshEntity, not an independent guaranteed passenger-add path. No default equipment population does not suppress the separate native calendar/headwear and attribute-finalization branches. These inherited behaviors are pinned to exact244, not treated as new Twilight status types.

### 20. Combat teleport

teleportToNoChecks changes position, sets cloak20, clears fire/jumping. aiStep decrements cloak; isInvisible and canBeSeenAsEnemy reflect it (clone also invisible first10ticks). Combat goals pause actions while cloak>0, but global cooldown decrements follow their own conditions. findVecInLOSOf tries100 candidates target+Gaussian16XZ/Y+2; native randomTeleport requires loaded chunk, ground, no collision/liquid and stops navigation on success; restores original position after probe. Candidate must see target, remain in home range and be >=5 away; first85 attempts also require candidateY>=targetY. Home checks use current Lich Y for low-floor tests, candidate position for radius30. Target teleport helper randomly chooses an alive Player in range without its own creative/spectator filter, else uses passed target; successful move relocates clones. Triggers: phase1 cooldown60, later successful hurt (randomInt(3 or6)<=old hit counter, then increment; survival check; reset0 before attempted teleport), phase2 unable-to-shoot, phase3 failed navigation, IN_WALL with target, home escape. Home fallback can place stone support. No teleport damage callback. No EnderEntity event is explicitly posted by these Lich methods; native randomTeleport/teleportTo witnesses retained.

### 21. Types/tags/amounts/returns

Custom lich_bolt6 and lich_bomb radius2 use armor/Wolf-armor bypass, projectile, witch-resistant and NeoForge magic tags; Bomb additionally explosion, Bolt additionally shield-break. twilight_scepter6 uses projectile/magic/shield-break but NOT normal armor bypass. None of these three has shield/Resistance/enchantment/invulnerability/cooldown bypass or no_knockback in scoped tags. Damage scaling WHEN_CAUSED_BY_LIVING_NON_PLAYER affects Player recipients (Peaceful0, Easy min(x/2+1,x), Normal x, Hard1.5x); it does not rescale a Lich target before shield threshold. Explosion damage = float((q*q+q)/2*7*4+1), q=(1-distance/4)*exposure, NO integer floor; outer radius and nonzero direction gates remain. Knockback is separate from hurt return and uses exposure and native explosion resistance/event adjustment. TF Detonate removes ItemEntity and LichBomb from affected entities; Bolt ignores explosions. Lich-owned explosion cannot damage any Lich, but displacement can still occur. See source_paths for native magic/sonic thresholds and secondary callback gates.

## Source admission table

All eligible rows also require the Lich gates above. Requests are not measured HP loss. This table covers native Twilight/Minecraft plus accepted earlier mod producers; future unreviewed mods and dynamic datapacks can add producers.

| Source | Native type / amount | Exact prerequisites |
|---|---|---|
| Player.attack native Bolt redirect | twilightforest:lich_bolt / 6 | Attack hook accepts; target attackable/interaction accepted; redirectable tag; native AIM transfer; Bolt then collides with uncloaked real phase1 Lich. No minimum player melee damage needed before redirect. |
| Player-owned projectile hits native Bolt | twilightforest:lich_bolt / 6 | Admitted collision and generic Projectile.onHit before its subclass hit callback transfer nonnull owner. Bolt needs Player owner for phase1 Lich. Example ordinary player arrow; original projectile eligibility/impact cancellation applies. |
| Twilight native timed shield parry | twilightforest:lich_bolt / 6 | Server; external parry mod absent; ITFProjectile or configured non-Twilight; entity hit Living; isBlocking and use elapsed<=shieldParryTicks (installed40). AIM transfers owner and impact canceled. Living nonPlayer blocker can parry but reflected Bolt still cannot collide with phase1 Lich. |
| Player Twilight Scepter | twilightforest:twilight_scepter / 6 | Native use accepts not fully-used-up item or creative; server launches. Wand inherited canHitEntity and onHit/deflection gates; uncloaked real shielded Lich admits6. No mandatory reflection. |
| Native splash Healing I/II | minecraft:indirect_magic / int(intensity*(6<<amp)+0.5)>2 | Lich is skeletons -> undead -> inverted_healing_and_harm, so HEALING damages and HARMING heals. Potion server splash AABB4/2/4, squared distance<16, isAffectedByPotions; direct target intensity1 else1-distance/4. Native amp0/1 full-hit amounts6/12; distant rounded<=2 fails. No arrow hurt prerequisite. |
| Native lingering Healing I/II cloud | minecraft:indirect_magic / int(0.5*(6<<amp)+0.5) =3/6 | Potion spawns radius3, wait10, radiusOnUse-.5 cloud; native cloud duration/reapplication/radius and potion-affectability gates, every5ticks, in horizontal radius. Half-intensity Healing still strictly>2. No HP success needed for cloud victim cooldown/radius update. |
| Native Evoker Fangs; accepted Cult Azazel fangs | minecraft:indirect_magic; owner absent minecraft:magic / 6 | Native warmup=-8 and inflated(.2,0,.2) hitbox; alive/noninvulnerable recipient, not owner, nonallied when owner present. Lich can be an incidental eligible recipient of naturally summoned fangs. Shield false prevents owned-fang enchantment post-attack callback. |
| Fully framed native Conduit | minecraft:magic / 4 | Native active water/frame checks;42 effect blocks for attack;40tick server update. Acquire Enemy in water/rain in AABB8; retained target must alive/within8. Lich qualifies as Enemy, but geometry/wet eligibility must genuinely hold. No artificial owner or target assignment. |
| Native Warden sonic boom | minecraft:sonic_boom / 10 | Native angry ATTACK_TARGET, cooldown absent, horizontal15/vertical20 range, sound delay34/duration60; Warden canTargetEntity requires same world, Living/noncreative/nonspectator, nonallied, not armorstand/Warden, noninvulnerable/alive/in border. Lich qualifies; cloak still rejects at hurt. Shield false prevents sonic success-dependent additional push. |
| Native Wither Skull with unresolved/non-Living owner | minecraft:magic / 5 | Server impact and owner not Living. Native persisted/unresolved owner branch is real, but ordinary Living Wither owner uses wither_skull8 and is NOT shield-breaking. Magic shield hit false suppresses Wither status; separate radius1 explosion still follows and can attempt HP after last shield. |
| Accepted Friends & Foes Iceologer Ice Chunk | minecraft:indirect_magic; owner absent minecraft:magic / 12 | Reuse accepted package and collision eligibility: alive/noninvulnerable, not owner or owner ally. Eligible incidental Lich collision breaks1; canFreeze gauge400 is independent of false shield hurt. No Friends research repeated. |
| Accepted Royal spectral anvil | minecraft:indirect_magic / 8 | Reuse accepted native creation/hover/fall/sweep+AoE. Player owner non-own-pet branch admits nonallied Lich; nonPlayer branch needs Player target or Gaze. Shield false suppresses Heaviness; a later separate sweep/AoE request after final shield may hit HP. |
| Accepted player Royal Pearl arrival | minecraft:indirect_magic / 7 | Reuse accepted successful permitted native teleport, Enemy nonally in projectile AABB4. Lich Enemy eligible; shield false suppresses Heaviness. Native pearl thrown0 contact neither breaks shield nor gates burst. |
| Accepted Royal Enderman teleport splash | minecraft:indirect_magic / 4 | Reuse accepted successful teleport and AABB4 nonallied Player OR Gaze recipient. A Lich must genuinely have Gaze; without it this path excludes Lich. Shield false suppresses Heaviness. |

## Rejected or conditional controls

- **Unreflected main/clone Lich Bolt:** Phase1 collision requires Player owner; any causing Lich rejected by hurt in all phases.
- **NonPlayer-reflected/ownerless Bolt:** Direction change alone fails Player-owner phase1 collision gate.
- **Lich Bomb / generic magic-tagged custom damage:** Not in breaks_lich_shields; blanket NeoForge magic tag is insufficient.
- **Ordinary Healing-tipped arrow into shield:** Arrow source untagged; hurt false prevents Arrow.doPostHurtEffects, so instant Healing callback cannot break the shield. Later-phase admitted arrow is different.
- **Harming potion on Lich:** Lich skeletons/undead inversion makes Harming heal; healing bypasses the shield damage branch. No shield decrement.
- **Guardian/Elder Guardian beam:** Damage1+2Hard+2Elder could exceed2, but native target selector is Player/Squid/Axolotl only, no Lich target. No fabricated setTarget positive control.
- **Poison:** Raw magic1 too small; installed NeoForge21.1.244 uses neoforge:poison (not shield tag). Lich ignores Poison via undead tags under ordinary addEffect.
- **Splash water:** Only water-sensitive entities receive indirect_magic1; Lich not water-sensitive and1<=2 regardless.
- **Ordinary Living-owner Wither Skull:** wither_skull8 source untagged; only the actual non-Living/unresolved-owner magic5 branch qualifies.
- **LootCommand.dropKillLoot:** Factory call builds a loot context, never calls hurt; not combat delivery.
- **amount exactly2 / cloak / clone / causing Lich:** Explicit counterexamples to tag-only admission.
- **TwilightWandBolt.hurt fallback:** Method can redirect/transfer with direct Living source, but Wand is not redirectable/pickable in native tags, so do not claim ordinary Player crosshair melee producer. Native item use is the proven positive path.

## Package review

| Package | Classification |
|---|---|
| Lich shield resource | CUSTOM_RESOURCE |
| Lich HP admission and projectile defense | BINARY_MECHANIC |
| Lich Bolt and reflection | CUSTOM_DAMAGE |
| Lich Bomb explosion | CUSTOM_DAMAGE |
| Lich phase resources and summons | CUSTOM_RESOURCE |
| Lich mob consumption and healing | CUSTOM_RESOURCE |
| Lich combat teleport | CUSTOM_CONTROL |
| Lich Minion retaliation buffs | VANILLA_LIKE_EXTENDED |
| Twilight Scepter bolt | CUSTOM_DAMAGE |

## Evidence and boundary

[Machine-readable section](semantic-sections/twilightforest-lich.json), [native witnesses](native-evidence/twilight-lich.json), [exact loader references](reference-evidence/twilight-lich-244.json), [raw references](vanilla-evidence/twilight-lich.json), [source census](lich-vanilla-source-audit.json), [integrity validation](twilightforest-lich-integrity.json), [full validation](r2f3-lich-validation.json).

Reuse four pinned candidate scans: no direct Twilight-specific name hits. Generic owner/recipient hooks only apply where their native dispatcher is reached. Lich shield early false never enters Living incoming/pre/post damage pipeline, so no power/umbrella/vampiric/etc rewrite is assumed for that counter. Exposed HP processing, Player victims of bolts/bombs, and minion effect application keep native generic hooks. No pack-wide guarantee.

Exact next task: Naga semantic review from existing installed Twilight source aids; then Minoshroom / Knight Phantom, Hydra / Ur-Ghast, Alpha Yeti / Snow Queen. Lich and Frosted are reviewed: do not restart them. No Ice and Fire, runtime boss/L2 tests, Stage/production or Phase6 work.
