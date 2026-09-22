# Twilight Forest — R2f8i partial, summon and scepter resources also reviewed

The installed4.8.3345 review is **PARTIAL**. Frosted remains protected at two reviewed package drafts and13 cases. Lich is now semantically complete at nine additional reviewed package drafts and24 delivery cases (14 shield-source cases): Naga adds eight reviewed packages and18 delivery cases: Minoshroom and Knight Phantom add10 packages /28 delivery cases: Hydra and Ur-Ghast add16 packages /43 cases: Alpha Yeti and Snow Queen add15 packages /41 cases: remaining ranged-mob subsection adds13 packages /28 cases: mounted knights/PinchBeetle/Yeti add8 packages /20 cases: chain/spike paths add7 packages /22 cases: giants/tools add4 packages /16 cases: spiders/swarm/borers add7 packages /24 cases: tactical mobs add8 packages /28 cases: constructs/slimes add5 packages /21 cases: Wraith/Minotaur/RisingZombie add4 packages /20 cases: summon/resources add9 packages /28 cases: current combined125 package drafts /374 delivery cases. **Zero final Twilight records are promoted.** Full mod mechanic, boss, defense, item and final source totals remain unknown. The four accepted reviews remain116 mechanics/161 paths/217 components. No runtime tests were performed.

| Mechanic | Native behavior | Vanilla comparison | Classification / source coverage |
|---|---|---|---|
| Frosted | Stable eligible server tick adds amp+1 to frozen gauge, capped140. Movement modifier -0.15*(amp+1) total multiplier, plus native ground frost penalty. Native freeze request every40ticks when fully frozen; exact-freeze incoming bonus floor(amp/2). Admitted incoming fire down-ranks amplifier. | Shares Slowness coefficient and native freeze processing; additional state and incoming hooks make the complete status custom. Native add/merge/expire/cures remain. | CUSTOM_STATUS; Ice Sword, three Ice Bow ammo cases, armor, Chill Aura, two biome settings, all six bomb source/mode cases |
| Ice Bomb package | Contact request2 or10; zone request1 or5, using custom frozen type. Frosted follows independently of hurt return. Landed zone runs six20tick callbacks in inflated AABB3/2/3. Yeti zone branch becomes ice blocks and is discarded. | Custom request/zone/control package through native damage and effect processing. Not vanilla freeze damage or direct HP subtraction. | CUSTOM_DAMAGE; player/dispenser/Alpha Yeti, each contact and zone |

| Source | Exact important distinction | Future fixture |
|---|---|---|
| Ice Sword | Player primary hurt must succeed before item callback200/2. Sweep secondary victims do not get the item callback. | Primary success/failure and secondary sweep controls |
| Ice Bow, ordinary/tipped/spectral | Once onHitEntity is entered, Frosted200/2 is independent of hurt result. Impact cancellation/deflection can prevent entry. Parent potion/glowing callback needs successful inherited hurt. Parent critical flag is not copied. Parent callback is lost after reload. | Three ammo paths; failed hurt; parry/deflection; full draw; save/load |
| Yeti armor | LivingDamageEvent.Post, originalDamage>0, n pieces: causing Living attacker receives5n+5ticks/amp n. Post can exist with zero final HP damage. | Piece counts, absorption, early cancellation, projectile owner versus ownerless |
| Chill Aura | Actual installed enchantment: per matching item chance0.15*level,200ticks/amp(level-1), then item durability request2 even if Frosted helper rejects. Targets causing attacker. | Native melee/arrow post-attack and secondary sweep controls, levels1–3 |
| Biome enforcement | Every60ticks: Snowy Forest100/0 without progress_lich, Glacier100/1 without progress_yeti; progression gamerule required, noncreative/nonspectator. Does not use helper equipment filter. | Both biomes, advancement/gamerule and freeze-immune gear controls |
| Player Ice Bomb | Owner=Player; speed1.25/inaccuracy1/pitch-5. Contact and zone differ. | Owned contact + zone, owner exclusion |
| Dispenser Ice Bomb | Proven native registration; ownerless, speed1.1/inaccuracy6. | Ownerless contact + zone |
| Alpha Yeti Ice Bomb | Native ranged goal, !canRampage; speed1.6, inaccuracy14-4*difficultyId. Living boss owner enables native difficulty scaling for Player victims. | Boss-owned contact + zone; only future testing |

Frosted's helper rejects freeze-immune entity types, freeze-immune head/chest/legs/feet wearables and creative Players. Native canFreeze also checks spectator and BODY armor, so some recipients can receive movement slowdown without building freeze. Fresh Frosted uses default milk/totem cures; honey does not cure it. Fire Resistance and other pre-incoming immunity gates prevent the fire down-rank callback. Later shield/cooldown rejection does not necessarily prevent it.

Ice Bomb's `twilightforest:frozen` is tagged magic and bypasses wolf armor, **not ordinary armor**. It lacks IS_FREEZING, projectile, fire, explosion, normal armor/shield/enchantment/Resistance/iframe bypass and no-knockback tags in the scoped native sources. Its explicit heat-sensitive multiplier occurs once. Normal mitigation applies. Save/load omits parent projectile serialization, losing owner and therefore original-thrower zone exclusion. Requests are not measured HP loss.

One registered custom MobEffect: `twilightforest:frosted`. Forty custom damage declarations remain pinned from R2f1; **twenty-seven custom damage caller profiles are reviewed**: frozen, lich_bolt, lich_bomb, twilight_scepter, axing, slam, haunt, thrown_axe, thrown_pickaxe, hydra_bite, hydra_fire, hydra_mortar, ghast_tear, falling_ice, yeeted, squish, chilling_breath, scorched, leaf_brain, lost_words, schooled, snowball_fight, clamped, spiked, ant, thrown_block and expired. Another13 remain unfinished. They are not classified as unused. REVIEW_REQUIRED0; unfinished review is not ambiguity. Final VANILLA_DIRECT/COMPOSITE/EXTENDED lists are not available yet. Lich, Naga, Minoshroom, Knight Phantom, Hydra, Ur-Ghast, Alpha Yeti and Snow Queen boss/defense semantics are closed; remaining Twilight combat content is pending.

Four pinned compatibility candidates have no direct Twilight name hits; generic conditional hooks remain, including Antidote duration reduction and player recipient/owner damage hooks. This is scoped static attribution, not pack-wide compatibility. No production fixes were made.

Particles, sounds, color/icon, repair/acquisition and registration infrastructure are excluded as separate combat mechanics. Other mod areas remain unreviewed. Subset fixtures are preserved; global minimum runtime runs remain R3.

Details: [reviewed section](semantic-sections/twilightforest-frosted.json), [current drafts](partial-drafts/twilightforest-r2f2-partial.json), [compat mapping](compat-findings/twilightforest-frosted.json), [progress validation](twilightforest-progress-integrity.json), [full validation](r2f2-partial-validation.json).

## R2f3 — LICH_SEMANTIC_REVIEW_COMPLETE

| Reviewed package | Native result | Classification |
|---|---|---|
| Shield resource | Default6, subtract1 only for admitted tagged request strictly>2; false return, no HP damage from the request | CUSTOM_RESOURCE |
| HP admission / projectile defense | Cloak, clone and causing-Lich gates precede shield and native HP processing; phase2 already admits HP damage | BINARY_MECHANIC |
| Lich Bolt | Custom6; phase1 Lich collision requires Player owner; native attack/projectile/parry reflection paths transfer ownership | CUSTOM_DAMAGE |
| Lich Bomb | Custom radius2 entity explosion, no block destruction/fire; not shield-breaking; direct strikes detonate | CUSTOM_DAMAGE |
| Phase summons | Real clone cap2, minion reserve9/active cap3; failed spawn attempt still spends reserve | CUSTOM_RESOURCE |
| Mob absorption | Native discard then heal2 or owned-minion current HP; no damage source | CUSTOM_RESOURCE |
| Teleport | Candidate/home search, cloak20, extinguish, combat goal/admission effects | CUSTOM_CONTROL |
| Minion enrage | Successful inherited hurt from any causing Lich grants native Speed200/2 and Strength200/1 | VANILLA_LIKE_EXTENDED |
| Twilight Scepter bolt | Native item launch; custom6 with ordinary armor processing, unlike Lich Bolt | CUSTOM_DAMAGE |

**Shield break and HP damage remain separate.** `breaks_lich_shields` has five values; the tag alone is insufficient. Cloak/clone/causing-Lich rejection, raw amount>2, shield state and source delivery predicates still apply. Final shield break returns false; a separate later request from a compound attack can hit exposed HP. Phase2 does not require all minions dead to admit HP damage.

Native reflection distinguishes direction from ownership. Player attack uses redirectable-projectile AIM before Bolt.hurt. Later-phase Lich deflection restores a prior nonnull owner; an initially ownerless projectile instead keeps the callback's new Lich owner because setOwner(null) is a no-op. Bombs never directly collide with Lich and do not carry the shield-breaking tag; a player-parried bomb can only attempt exposed HP damage through its later explosion.

All21 requested semantic conclusions, 14 shield-source cases, rejected controls, custom/vanilla source tags and hurt-return dependencies are saved in the [Lich owner review](twilightforest-lich-review.md) and [machine-readable section](semantic-sections/twilightforest-lich.json). Source coverage includes all native tag identities and Minecraft factory caller dispositions, plus exact reuse of accepted Cult, Royal and Friends producers. This is static native-source coverage, not an assertion about all unreviewed modpack/datapack producers or runtime results.

The [combined draft](partial-drafts/twilightforest-r2f3-partial.json) retains Frosted unchanged. [Lich integrity](twilightforest-lich-integrity.json), [shared progress integrity](twilightforest-progress-integrity.json), five tooling tests and [full validation](r2f3-lich-validation.json) protect this bounded checkpoint. Accepted global116 mechanics /161 paths /217 components remain unchanged; Twilight final totals and R3/R4 remain unfinished.

Historical R2f3 next task (now completed): **Naga**, then Minoshroom / Knight Phantom, Hydra / Ur-Ghast, Alpha Yeti / Snow Queen. Do not repeat Lich or Frosted. Ice and Fire remains UNSTARTED. No runtime boss/L2 tests, production, Stage, Phase6 reopening, balancing or original Phase7 work.

Historical R2f3 save boundary: usage reached75% during Lich finalization. Stop new research and protect R2f3 by validated commit/push/live-SHA equality. Naga has not started; it is the exact resume point.

## R2f4 — NAGA_SEMANTIC_REVIEW_COMPLETE

Recovered clean branch at local/fetched/live `d9dffb33a867aae9152a2ed3bc68f50b0b02f59d`; divergence0/0, no newer or conflicting work. Reused installed4.8.3345 source aids; no accepted subsection repeated.

| Reviewed package | Native result | Classification |
|---|---|---|
| Head contact | Ordinary effective attack5 melee; successful inherited hurt adds explicit push | VANILLA_LIKE_EXTENDED |
| Charge block | Native blocking during CHARGE produces mutual push, generic2 self recoil and daze; false return without victim melee | CUSTOM_CONTROL |
| Stunless block | Player durability10/cooldown200/stop-use precede fixed mob_attack4; circle/false independent of hurt success | VANILLA_LIKE_EXTENDED |
| Multipart body | Twelve linked Entity parts, no independent HP; same-source two-thirds forwarding and contact2/Animal6 | VANILLA_LIKE_EXTENDED |
| Damage admission | Causing/direct home gates and explosion rejection before native fire/fall immunity and mitigation | BINARY_MECHANIC |
| HP/body resource | HP controls segment count and additive speed; delayed regeneration and cumulative daze-damage counter | CUSTOM_RESOURCE |
| Combat movement | Navigation-dependent circle/intimidate/crumble/charge/daze states, real movement inputs and HP-dependent selection | CUSTOM_CONTROL |
| Terrain pressure | Predicate-limited obstacle/support destruction and home recovery affect combat delivery | CUSTOM_CONTROL |

Eight packages /18 delivery cases. Classification totals: VANILLA_LIKE_EXTENDED3, CUSTOM_CONTROL3, CUSTOM_RESOURCE1, BINARY_MECHANIC1; all other classes0, REVIEW_REQUIRED0. Only native `minecraft:mob_attack` and ownerless `minecraft:generic` are used; no custom Naga DamageType. Four Twilight custom type profiles remain reviewed,36 remain unfinished. Naga closes no additional custom declaration.

The head retains the native damage pipeline and shared hurt cooldown. Part forwarding preserves source identity and applies two-thirds before mitigation. Overlapping parts can produce multiple attempts, not thirteen independent full HP hits. Inactive parts shrink to zero size but the inherited visibility getter reads the parent, so local deactivation is not an absolute forwarding/targetability prohibition. This installed-code discrepancy is documented without a fix.

Constructor health-per-segment remains12 before difficulty HP finalization (Easy120/Normal200/Hard250 with pinned multiplayer bonus modeNONE). Segment count stays12 until HP falls below120; living speed bonus increases from0.02 to0.12 as count falls to2. First undamaged regeneration is server-AI counter620, then every20; true hurt resets the timer. Daze interruption accumulates truncated admitted request amounts, not actual HP loss. Death has staged part cleanup, not extra part HP.

[Complete review](twilightforest-naga-review.md), [semantic section and future controls](semantic-sections/twilightforest-naga.json), [combined draft](partial-drafts/twilightforest-r2f4-partial.json), [Naga integrity](twilightforest-naga-integrity.json), [full validation](r2f4-naga-validation.json). Future native fixtures distinguish home-bound spawner encounters from unrestricted spawn eggs, head/part/overlap hits, genuine Player blocking and charge state, mitigation/return versus HP, HP thresholds/regeneration, and terrain grief/helper predicates. No runtime fixtures executed.

Save mode began at70% usage to reserve protection capacity. Minoshroom and Knight Phantom were not started. Exact next task: their semantic review using existing installed source aids, followed by Hydra / Ur-Ghast and Alpha Yeti / Snow Queen. Twilight remains PARTIAL with19/55 reviewed drafts and zero promoted records. Accepted116/161/217 totals are unchanged. No Ice and Fire, runtime boss/L2, Stage, production, fixes, balancing, Phase6 reopening or Phase7 work.


## R2f5 — MINOSHROOM_KNIGHT_PHANTOM_SEMANTIC_REVIEW_COMPLETE

Recovered clean local/fetched/live branch at `c30b8c98fbbd8aefad86088cd027d4156b22924f`, divergence0/0. No newer or conflicting work. Existing source aids and protected comparisons were reused; none of Frosted/Lich/Naga was reopened.

| Boss | Reviewed packages | Delivery cases | Classification totals |
|---|---:|---:|---|
| Minoshroom | 4 | 11 | VANILLA_LIKE_EXTENDED1, CUSTOM_DAMAGE1, CUSTOM_CONTROL2 |
| Knight Phantom | 6 | 17 | VANILLA_LIKE_EXTENDED2, CUSTOM_DAMAGE1, CUSTOM_CONTROL2, BINARY_MECHANIC1 |
| New total | 10 | 28 | VANILLA_LIKE_EXTENDED3, CUSTOM_DAMAGE2, CUSTOM_CONTROL4, BINARY_MECHANIC1 |

REVIEW_REQUIRED0. Current Twilight drafts29/83; zero promotions. Accepted global116 mechanics/161 paths/217 components remain unchanged.

Minoshroom uses `axing` through its custom melee helper, with settled unenchanted attack11 and a sprinting Minotaur-axe incoming bonus7. Native Player difficulty scaling precedes that bonus. Charge is a snapshot navigation/one-attempt path; ground slam is a separate Player-only grounded AABB request at half effective attack, bypassing armor and transitively shields, with upward push before hurt. Ordinary axe shield disabling is native behavior. No special home damage gate, HP phase or regeneration is present. Charge terrain clearing and inherited accepted-lava cleanup have different predicates.

Knight Phantom has independent HP and local nearby-Knight coordination, not a shared health/resource pool. Charging changes attack+7, armor multiplier and dimensions; inactive armor normally clamps30 versus charged11 with supplied equipment. Early guard false skips the normal shield damage/events pipeline. Actual block traversal does not imply damage immunity. Final-survivor random weapon selection is overwritten by setNumber(0), producing sword. Formation/progress persistence does not immediately restore charging flags or transient armor/attack modifiers.

Native thrown axe6/pick3 retain a projectile owner but create DamageSources with direct=null and causing=null. Consequently native entity-owner difficulty scaling and directional source-position shield blocking do not apply. Native timed parry remains possible, but no reflected throw damages any Knight. Any accepted impact discards the projectile regardless of hurt result; payload is unsaved, so reloaded pick becomes default axe6/gravity.001 with owner retained. No pickup/ammunition resource or thrown-block attack is invented.

The shared melee helper also passes the attacker, rather than victim, into EnchantmentHelper.modifyDamage and records lastHurtMob=self; exact bytecode comparisons preserve these differences. No fixes were made.

Five custom profiles newly USED: **axing, slam, haunt, thrown_axe, thrown_pickaxe**. Nine of40 profiles are now reviewed;31 remain unfinished, not unused. Alternate Minotaur/Player tool paths and limited Wraith HAUNT caller evidence are explicit; full Wraith and unrelated knightmetal-block/thrown-block reviews are pending. No other family was begun.

[Complete owner review](twilightforest-minoshroom-knight-review.md), [machine-readable packages and paths](semantic-sections/twilightforest-minoshroom-knight.json), [current combined draft](partial-drafts/twilightforest-r2f5-partial.json), [integrity](twilightforest-minoshroom-knight-integrity.json), [full validation](r2f5-minoshroom-knight-validation.json). Five future fixture groups cover native boss spawns, equipment/Player alternatives, native projectile/parry/load behavior, state/home/defense and group death controls. No runtime fixtures executed.

Research stopped at68% usage to reserve protection capacity. Hydra and Ur-Ghast have NOT STARTED. They are the exact next task after review, followed by Alpha Yeti / Snow Queen. Twilight remains PARTIAL. No Ice and Fire, runtime boss/L2 tests, Stage/production, compatibility fixes, balancing, Phase6 reopening or Phase7 work. Validate, commit, push, verify live equality and STOP.


## R2f6 — HYDRA_UR_GHAST_SEMANTIC_REVIEW_COMPLETE

Recovered clean local/fetched/live `79b3284081ee71a1a5c5ec0b18af02595535e379`, divergence0/0. No newer or conflicting work. Earlier five subsections and all accepted catalog entries remain protected.

| Boss | Packages | Delivery cases | Classification totals |
|---|---:|---:|---|
| Hydra | 8 | 22 | BINARY_MECHANIC1, CUSTOM_RESOURCE2, CUSTOM_CONTROL2, CUSTOM_DAMAGE3 |
| Ur-Ghast | 8 | 21 | CUSTOM_RESOURCE1, CUSTOM_CONTROL3, CUSTOM_DAMAGE1, VANILLA_LIKE_EXTENDED2, VANILLA_DIRECT1 |
| Added | 16 | 43 | REVIEW_REQUIRED0 |

Twilight combined **45 package drafts /126 delivery cases**, PARTIAL, zero promoted records. Accepted116 mechanics/161 paths/217 components remain unchanged. Four new USED custom profiles: **hydra_bite, hydra_fire, hydra_mortar, ghast_tear**. Census13/40 reviewed,27 unfinished, not unused.

Hydra has one360-HP pool,46 Entity parts and seven head counters (three initially active). Open-head requests forward unchanged; other parts/closed heads round(amount/8). Head counters add truncated requests even if HP damage is rejected. Strict counter>120 triggers head death/regrowth, separately from HP. Self/own-part/owner-distance/dead-head admission precedes native mitigation and shared cooldown. Regrowth and reloading have different semantics; no cauterization rule exists. Bite48 has independent blocking disruption/control; flame19 uses the actual moved-box/ray query and ignites only on true hurt. Mortar performs a native explosion then a distinct nearby18 fire request; normal Player reflection bypasses its separate hurt-reflection fuse/ground callback. Terrain/contact, inactivity heal, counters, state schedule, persistence and death are closed without fixes.

Ur-Ghast's tantrum threshold is18 actual counted HP loss, with hurtTime/alive/trap predicates; no fixed duration. Tantrum divides incoming amount by10 and periodically checks Players below for sky-visible ghast_tear3, plus independent ghastling lift. Tear damage bypasses armor/shield but retains helmet reduction, Resistance/protection/absorption/cooldown. Live custom volley fires three16-impact projectiles with a separate ownerless explosion; reflected identity is native and no boss1000-hit rule exists. Saved minecraft:fireball type recreates vanilla6/MOB-explosion behavior. Minions have no master/target inheritance; six spawn attempts per selected trap, own targeting and native fireballs, and minion load restores6HP. Nearby ghastling consumption discards then heal(2), with normal heal event/clamp. Trap charge requires three unique dying ghastlings and a redstone neighbor event; active120 ticks force normal phase/velocity and random generic7 boss or10 other Ghast requests. Control does not depend on hurt success. Rain is client-only; visualOnly lightning suppresses damage/fire but preserves native rod/copper/game-event callbacks, explicitly classified VANILLA_DIRECT.

[Complete owner review](twilightforest-hydra-urghast-review.md), [machine-readable mechanics and paths](semantic-sections/twilightforest-hydra-urghast.json), [combined draft](partial-drafts/twilightforest-r2f6-partial.json), [caller census](twilightforest-hydra-urghast-caller-scan.json), [integrity](twilightforest-hydra-urghast-integrity.json), [full validation](r2f6-hydra-urghast-validation.json). Installed JAR/method/resource witnesses, raw1.21.1 and exact NeoForge21.1.244 references are reproducible. Five tooling tests, prior-file preservation, source/delivery/classification checks and research-only boundary validation protect this checkpoint. No runtime boss/L2 tests performed.

Exact next task: **Alpha Yeti + Snow Queen semantic review**, reusing existing source aids and protected Ice Bomb evidence. Do not repeat accepted sections. No Stage/production, balancing, compatibility fixes, Phase6 reopening or Phase7. Updated user authorization on2026-09-22 replaces the earlier percentage stop rule: commit/push/live-verify R2f6, then continue while current usage is healthy. Ice and Fire stays blocked until full Twilight completion and promotion are protected.


## R2f7 — ALPHA_YETI_SNOW_QUEEN_SEMANTIC_REVIEW_COMPLETE

R2f6 was committed, pushed and live-verified at `99c3e9e55663347f9ea23042f041d9ad512da7ec` before this subsection began. Existing Frosted, Lich, Naga, Minoshroom, Knight Phantom, Hydra and Ur-Ghast evidence remains protected. No research was restarted.

| Owner | Packages | Delivery cases | Classification totals |
|---|---:|---:|---|
| Alpha Yeti | 7 | 22 | BINARY_MECHANIC1, CUSTOM_RESOURCE1, CUSTOM_CONTROL2, CUSTOM_DAMAGE2, VANILLA_LIKE_EXTENDED1 |
| Snow Queen | 8 | 19 | BINARY_MECHANIC1, CUSTOM_RESOURCE1, CUSTOM_CONTROL3, CUSTOM_DAMAGE2, VANILLA_LIKE_EXTENDED1 |
| Added | 15 | 41 | REVIEW_REQUIRED0 |

Twilight combined **60 package drafts /167 delivery cases**, PARTIAL, zero promoted records. Accepted116 mechanics/161 paths/217 components are unchanged. Four new USED custom types: **falling_ice, yeeted, squish, chilling_breath**. Census17/40 reviewed;23 unfinished, not unused.

Alpha Yeti initially rejects projectile-tagged sources before native damage processing until a true accepted hit unlocks rampage or while tired. Rampage/tired counters measure goal calls/evaluations, not guaranteed game ticks or HP thresholds. Its fall callback requests ordinary mob_attack5 in an area before native self-fall processing; successful hurt alone adds upward motion. Ceiling conversion creates ownerless falling ice; target-ceiling and random-ceiling grief predicates differ. Falling damage is min(floor(ceil(distance-5)*difficulty coefficient),100), excludes all Alpha Yetis, bypasses enchantments but retains armor/Resistance/absorption/cooldown. Placement and hurt returns are separate.

Native grabs/releases have no immediate damage. Player throws attach transient state and send impulses; a later admitted exact fall callback cancels that source and re-enters native hurt with yeeted using the captured incoming amount and thrower attribution. Native difficulty, fall protections and other hooks remain. NonPlayer throws do not receive that attachment. Hostile mount/dismount/teleport-event/suffocation controls and reload/landing/water ordering are explicit. Ordinary and rampage IceBomb producers link the two protected Frosted packages without duplicating their semantics.

Snow Queen has one ordinary200-HP body in every phase and seven geometric shield parts without HP. Parts do not forward damage or break; piercing AbstractArrow returns true only for native projectile bookkeeping. Collision push precedes hurt; accepted hits add Y+.4. DROP contact and melee use squish with effective attack7; other phases use mob_attack. Beam phase counts integer original requests only on true body hurt, independently of actual HP loss;25 resets to SUMMON. Drop-count completion does not require a hit. The chilling_breath4 ray has no block clip and can attack multiple progressively-nearer candidates in query order; it is neither a projectile nor Frosted. Summoned IceCrystals have no master and all nearby crystals count; failed teleports still spend a summon, saved/reloaded summoned crystals lose their600-tick expiry. Native melee, biome melting, terrain clearing, phase persistence and death callbacks are resolved.

[Owner review](twilightforest-yeti-queen-review.md), [mechanics and paths](semantic-sections/twilightforest-yeti-queen.json), [combined draft](partial-drafts/twilightforest-r2f7-partial.json), [caller scan](twilightforest-yeti-queen-caller-scan.json), [integrity](twilightforest-yeti-queen-integrity.json), [full validation](r2f7-yeti-queen-validation.json). Installed native methods/resources and raw1.21.1/exact NeoForge21.1.244 comparisons are reproducible;21 complete declared native classes plus producer/event/registration witnesses. Two protected Frosted packages are linked, zero duplicated.

Exact next task: **Task C remaining Twilight combat content**, using existing source aids. Close the remaining23 custom type callers, mobs/minibosses, weapons/scepters/staves, armor/charms, projectiles/hazards/resources/control, source/delivery/compatibility attribution and exclusions. Protect each complete subsection toward R2f8, then perform final deduplication/promotion only after all semantics close. Current usage healthy; continue after push/live verification. No runtime boss/L2, Stage/production, balancing/fixes, Phase6 reopening or Phase7. Ice and Fire remains blocked until full Twilight completion is protected.


## R2f8a — TWILIGHT_RANGED_MOBS_SEMANTIC_REVIEW_COMPLETE

R2f7 was pushed and live-verified at `cb929fb7833eb27ddc3c16126f281cc62247421a`; clean tree before continuation. This bounded Task C subsection adds **13 reviewed mechanic packages /28 delivery cases**: CUSTOM_CONTROL4, CUSTOM_DAMAGE4, VANILLA_LIKE_EXTENDED5. Combined Twilight **73/195 drafts**, PARTIAL, zero promotions. REVIEW_REQUIRED0. Accepted global116/161/217 counts remain unchanged.

Fire Beetle and Winter Wolf share a retaliation-only breath goal using lastHurtByMob, current range/LOS and saved aim position; one selected Living winner comes from a moved local box and30-block ray. Fire Beetle requests scorched2 and ignites10 seconds only on true breath hurt. Winter Wolf requests ordinary mob_attack2, without Frosted or freezing. Mist Wolf adds native Blindness only after successful melee with raw brightness0 at the wolf and a nonsolid current block; Easy omits it, Normal140/Hard300 ticks.

NatureBolt2 and TomeBolt3 custom types bypass armor/shield and apply native Poison or Slowness only after true hurt. Native installed Poison uses ownerless neoforge:poison1 (raw Minecraft uses magic), independently of the bolt source. Druid Hoe/Stick/Bow goal admission and permanent baby state are documented, including native SwarmSpider jockey production. Death Tome lectern gaze/retaliation/hurt release, immediate shot, saved lectern state and fire-input multiplier2 are closed. SlimeBlob is ordinary thrown4 without slow; Stable Ice Core snowball uses custom magic/projectile2 while retaining armor and applying no Frosted. All four projectiles inherit ITFProjectile and native timed parry/owner serialization.

Unstable Ice Core uses ordinary melee and delayed death60 native radius1 explosion. Its separate grief-gated block transmutation can still run after the explosion itself is canceled; shape/material/resistance/color rules are explicit. Neither ice-core subtype's appearance implies freezing attacks. Protected BaseIceMob/Frosted/boss evidence is reused.

New USED profiles: **scorched, leaf_brain, lost_words, schooled, snowball_fight**. Census22/40 reviewed;18 unfinished, not unused.18 complete declared native classes plus limited registration/producer/color witnesses are pinned. Full SwarmSpider, SnowGuardian equipment and remaining mobs/items/hazards stay pending, not falsely marked complete.

[Detailed review](twilightforest-ranged-mobs-review.md), [semantic packages and sources](semantic-sections/twilightforest-ranged-mobs.json), [explicit review inputs](review-inputs/twilightforest-ranged-mobs.json), [caller audit](twilightforest-ranged-mobs-caller-scan.json), [integrity](twilightforest-ranged-mobs-integrity.json), [full validation](r2f8a-ranged-mobs-validation.json).

Exact next task: **remaining melee/control mobs and minibosses**, followed by items/armor/charms/scepters/projectiles and hazards/resources. Close remaining18 custom types and source/delivery/compatibility/exclusion coverage toward R2f8, then deduplicate/promote Twilight only after all content closes. No runtime boss/L2, Stage/production, fixes/balancing, Phase6 or Phase7. Ice and Fire remains blocked until final Twilight protection. Current usage healthy; continue after commit/push/live equality.

## R2f8b — Mounted mobs complete

[Detailed review](twilightforest-mounted-mobs-review.md) and [machine-readable packages/paths](semantic-sections/twilightforest-mounted-mobs.json) close both goblin knights, their mounted attack delegation, shared directional shield, independent armor stripping and timer-sensitive heavy spear; Pinch Beetle capture/clamped/boat destruction; and ordinary Yeti anger with protected throw/fall reuse. Nine native class surfaces are fully pinned, with raw Minecraft and exact NeoForge references.

Shield wear/axe disabling/final shield break precede ordinary hurt; the breaking hit does not damage HP. The heavy modifier is +12 ADD_MULTIPLIED_BASE (default104 attack), and the goal can miss timer25 because it does not request every-tick updates. Pinch capture precedes damage; clamped is physical/no_knockback, while boat pickup destroys the boat through kill without DamageSource. Yeti anger changes follow range4 to12 before hurt approval and persists. These are static conclusions, not runtime observations.

Current totals81 package drafts /215 delivery cases;23/40 custom caller profiles,17 unfinished; REVIEW_REQUIRED0, zero promoted. [Integrity](twilightforest-mounted-mobs-integrity.json) / [full validation](r2f8b-mounted-mobs-validation.json). Next: BlockChainGoblin/SpikeBlock, giants and remaining melee mobs, followed by remaining items/hazards/resources toward R2f8 and final whole-Twilight promotion.

## R2f8c — Chain and spike paths complete

[Detailed chain review](twilightforest-chain-review.md) / [semantic records](semantic-sections/twilightforest-chain.json) close all native SPIKED callers: Goblin melee uses directGoblin/causingSpikeBlock, while player-thrown ChainBlock uses directprojectile/causingowner. Goblin part collision instead uses ordinary mob_attack. SPIKED is physical but not projectile-tagged.

The item has separate launch/UUID/return, damage, pre-hurt shield disruption and Destruction terrain/budget semantics. Destruction decreases entity damage by1.5 perlevel; shield disruption precedes damage approval. Projectile smash count and owner return-cost count differ, with no native transfer. A separate legitimate mining-start callback on the Player can populate the owner budget while the mainhand chain remains in flight; it persists across throws and can repeatedly charge return durability. Save/load reconstructs a separate projectile item stack and omits hand/return velocity state. Eleven native class surfaces plus registration and recursive tool-tag evidence are pinned. No changes or runtime tests.

Totals88 drafts /237 cases;24/40 custom profiles,16 unfinished; REVIEW_REQUIRED0, zero promoted. [Integrity](twilightforest-chain-integrity.json) / [full validation](r2f8c-chain-validation.json). Exact next: giants and remaining melee content, then the other unreviewed item/hazard/resource paths toward R2f8 and final Twilight promotion.

## R2f8d — Giants and maze tools complete

[Detailed review](twilightforest-giants-tools-review.md) / [semantic records](semantic-sections/twilightforest-giants-tools.json) close GiantMiner and ArmoredGiant ANT melee with native equipped requests11/13 and ordinary ironarmor15. Player-held weapons use player_attack with default10/12 and shared +2.5 interaction-range modifiers; those modifiers do not increase native mob melee geometry. GiantPick terrain uses an aligned64-position same-block volume with native per-block admission, transient recursion state, and separately traced loot grouping. Mazebreaker tagged speed×16 and the generic extra16 durability rule are closed for reuse. No runtime tests or changes.

Four new packages /16 paths; current92/253 drafts,25/40 custom profiles,15 unfinished, REVIEW_REQUIRED0, zero promoted. [Integrity](twilightforest-giants-tools-integrity.json) / [full validation](r2f8d-giants-tools-validation.json). Next: remaining melee/control mobs, starting spiders/swarm and MosquitoSwarm, then other unfinished mobs/items/hazards/resources toward R2f8 and final promotion.

## R2f8e — arthropods and infested towerwood

Protected predecessor: `f87c0a08b85f49b88c4262d4852066bea8199fe9` (R2f8d, live verified). This subsection adds **7 reviewed packages /24 delivery cases**, bringing Twilight to **99/277 drafts**, zero promoted. Custom DamageType census remains **25/40**,15 unfinished; REVIEW_REQUIRED0.

Full declared bodies for HedgeSpider, KingSpider, SwarmSpider, TowerBroodling, MosquitoSwarm, HelmetCrab, TowerwoodBorer and its goals, AlwaysWatchTargetGoal and InfestedTowerwoodBlock are pinned. Native Spider inheritance proves the King vehicle-start veto and distinct rider compositions. Mosquito Hunger is native food exhaustion; later starvation retains a separate ownerless source. Borer reinforcement is scheduled before final incoming hurt admission and requires a legitimate infested-block callback to release a fresh mob. Grief-denied replacement releases none. Crab native armor/melee/leap and blue rendering are exclusions.

See [semantic review](twilightforest-arthropods-review.md), [machine-readable section](semantic-sections/twilightforest-arthropods.json) and [validation](r2f8e-arthropods-validation.json). Exact244 loader hooks/tags, full raw Spider/Hunger authority, zero native getReinforcementType callers and earlier protected evidence support the conclusions. No runtime or production changes.

Next: remaining melee/control mobs and unfinished undead/summon bodies, then remaining items/hazards/custom callers and whole-Twilight promotion. IceAndFire remains unstarted until Twilight COMPLETE is pushed.

## R2f8f — Redcap/Sapper, Kobold and Troll

Protected predecessor: `ce8cafbf6c2fb8108f8db7cba46eb4a3cc9a12ff` (R2f8e, live verified). Adds **8 reviewed packages /28 delivery cases**, bringing Twilight to **107/305 drafts**, zero promoted. `thrown_block` is USED through its actual caller: custom census **26/40**,14 unfinished; REVIEW_REQUIRED0.

Redcap and Sapper have native equipped melee5, ordinary armor2/4, shyness/TNT avoidance, TNT lighting and Sapper-only three-charge planting. Their blast uses ordinary native TNT; actual igniter, chain and reload state control source ownership. Kobold bread pickup/consumption, acquisition versus retaliation, panic and flock navigation are separate contracts. Troll uses a real carried projectile and a new thrown projectile, follow-range/task state and a saved-state Air fallback. Its projectile requests6 with **no direct entity, causing entity or source position**, retaining helmet processing and native mitigation; timed parry changes projectile ownership but does not repair that source identity.

Boggard is an assessed exclusion: full registration and all-class reference evidence find no registered entity/native producer, so no mechanic or delivery is promoted from its unused class. Troll death ripening and Kobold munch visuals are also documented exclusions.

[Semantic review](twilightforest-tactical-mobs-review.md), [packages and paths](semantic-sections/twilightforest-tactical-mobs.json), [integrity](twilightforest-tactical-mobs-integrity.json), [validation](r2f8f-tactical-mobs-validation.json). Full19 class surfaces, exact244/raw references, actual caller census, five tooling tests and preservation checks protect this subsection.

Next: CarminiteGolem, Adherent/HarbingerCube registration/body status, MazeSlime, SnowGuardian, RisingZombie/LoyalZombie and remaining Wraith/Minotaur bodies; then items/hazards/callers and final Twilight promotion. No runtime, L2, Stage, production, Phase6/7 work. IceAndFire remains unstarted.

## R2f8g — constructs, Maze Slime and Snow Guardian

Protected predecessor: `ac50a160beb2abdf1524aa1ebee824a46a354891` (R2f8f, live verified). Adds **5 reviewed packages /21 delivery cases**, bringing Twilight to **112/326 drafts**, zero promoted. Custom census stays **26/40**,14 unfinished; REVIEW_REQUIRED0.

CarminiteGolem ordinary melee9 only adds its vertical push on successful hurt. MazeSlime uses native size/contact/splitting with triple base health, harmful tiny/NoAI contact and exact244 cancellable splitting; saved health loads after the temporary size refill, so ordinary reload healing is not claimed. SnowGuardian spawns only three equipment slots with four loadouts, ordinary melee and protected Knightmetal/BaseIce reuse. Adherent has registered native ranged behavior and a legitimate administrative summon path, but no proved survival producer; HarbingerCube is registered without an attack goal/callback and is an assessed exclusion.

[Semantic review](twilightforest-constructs-slimes-review.md), [packages and paths](semantic-sections/twilightforest-constructs-slimes.json), [integrity](twilightforest-constructs-slimes-integrity.json), [validation](r2f8g-constructs-slimes-validation.json). Six full native bodies, actual world/equipment callers, raw/exact244 Slime inheritance, source/path checks, five tooling tests and prior-checkpoint preservation protect this subsection.

Next: Wraith/Minotaur remaining bodies, RisingZombie graveyard conversion, LoyalZombie/ZombieWand resource/feed/expiry and native producers; then utility/passive exclusions and remaining items/hazards/custom callers. No runtime or production changes. IceAndFire remains unstarted until Twilight COMPLETE is protected.

## R2f8h — Wraith, Minotaur and Rising Zombie

Protected predecessor: `8795e3ad0def055395914c77ab7da9ae4d95060a` (R2f8g, live verified). Adds **4 reviewed packages /20 delivery cases**, bringing Twilight to **116/346 drafts**, zero promoted. Custom census stays **26/40**,14 unfinished; REVIEW_REQUIRED0.

Wraith's obstacle-free flight/home and every-tick melee scheduler are closed; its protected HAUNT request precedes a separate ordinary melee request and does not imply10 HP damage. Minotaur's native gold-axe roll, charge geometry and terrain veto reuse the protected AXING/sprint package. RisingZombie has a nearest-player gaze trigger, unsaved rising counter, native conversion preserving current health, and an exact in_wall immunity override that skips superclass immunity checks; movement and HP admission are separate.

[Semantic review](twilightforest-restless-mobs-review.md), [packages and paths](semantic-sections/twilightforest-restless-mobs.json), [integrity](twilightforest-restless-mobs-integrity.json), [validation](r2f8h-restless-mobs-validation.json). Nine full native class bodies, producer census, raw/exact244 inheritance and all five tooling tests are validated with previous-checkpoint/accepted-mod preservation.

Next: LoyalZombie/ZombieWand ownership, targeting, feeding, Strength lifetime/expiry and shared scepter durability/recharge, then remaining utility/passive mobs, items/hazards/resources and14 unfinished source profiles. Twilight remains PARTIAL. No runtime/production changes; IceAndFire only after protected final Twilight completion.

## R2f8i — Loyal Zombie and shared scepter resources

Protected predecessor: `696eb25903f23324bbedb90116fd7a41a395dd20` (R2f8h, live verified). Adds **9 reviewed packages /28 delivery cases**, bringing Twilight to **125/374 drafts**, zero promoted. Actual `expired` caller makes the custom census **27/40**,13 unfinished; REVIEW_REQUIRED0.

Native Zombie Scepter summon/ownership, fixed7 attack, true-only push, Strength-gated expiry, independent owner feed operations, scoped target vetoes, native follow teleport and persistent Crown baby are closed. Shared persistent durability charges and Renewal hand/inventory callbacks remain separate from manual crafting. Actual manual Zombie repair matches potion item IDs while Renewal checks Strength potion components; the installed difference is preserved. EXPIRED bypasses ordinary armor/Resistance and standard Protection/totem predicates but still uses native hurt/event processing.

[Semantic review](twilightforest-summon-resources-review.md), [packages and paths](semantic-sections/twilightforest-summon-resources.json), [integrity](twilightforest-summon-resources-integrity.json), [validation](r2f8i-summon-resources-validation.json). Five full native class surfaces, actual source/resource caller census, recipe/tag data and exact native comparison chains are pinned. Five tooling tests and evidence/source/path/prior-checkpoint/accepted-mod/scope validation protect this subsection.

Next: Fortification shield attachment/event/timer/producers and Lifedrain target/damage/control/execute/heal/food, reusing these resources; then remaining utility entities/items/hazards and13 unfinished types before final Twilight promotion. No runtime/production changes; IceAndFire remains unstarted.

## R2f8j — Fortification and Lifedrain native payloads

R2f8i was pushed/live verified at `5f56f39696e7c17c4eccd8314f3953ef14578aeb`. Seven reviewed packages/26 delivery cases bring Twilight to **132 package drafts/400 cases**. LIFEDRAIN is USED through its real caller: **28/40** custom profiles reviewed,12 unfinished. REVIEW_REQUIRED0; zero Twilight promotions and unchanged four accepted mods.

The review separates Fortification count/timer/persistence from its binary incoming-event cancellation, and Lifedrain selection/source damage from low-health execution, admitted restoration, independent motion and Crown charge saving. The nonPlayer native die/discard branch is documented separately from the Player second hurt request; no compatibility implementation or balancing change is made. Protected Lich shields, Twilight bolt and shared scepter resources remain unchanged.

[Contracts](twilightforest-scepter-payloads-review.md), [packages and paths](semantic-sections/twilightforest-scepter-payloads.json), [integrity](twilightforest-scepter-payloads-integrity.json), [validation](r2f8j-scepter-payloads-validation.json). Five full native class surfaces, all-TF actual caller scan, raw Minecraft/exact244 comparison and semantic/source/path/prior-checkpoint checks protect this subsection with all five tooling tests.

Next: remaining player projectile/utility weapons (Moonworm Queen, Cube of Annihilation, Ender/Seeker/Triple bows, Peacock Fan), then armor/charms/food, utility/passive entities, hazards/custom sources and exact nested ASM/compatibility closure before final Twilight promotion. No runtime boss/L2/Stage/production/Phase6/7; IceAndFire only after Twilight COMPLETE is pushed and verified.
