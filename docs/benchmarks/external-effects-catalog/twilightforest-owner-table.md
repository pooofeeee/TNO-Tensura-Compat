# Twilight Forest — R2f4 partial, Frosted, Lich and Naga reviewed

The installed4.8.3345 review is **PARTIAL**. Frosted remains protected at two reviewed package drafts and13 cases. Lich is now semantically complete at nine additional reviewed package drafts and24 delivery cases (14 shield-source cases): Naga adds eight reviewed packages and18 delivery cases: combined19 package drafts /55 delivery cases. **Zero final Twilight records are promoted.** Full mod mechanic, boss, defense, item and final source totals remain unknown. The four accepted reviews remain116 mechanics/161 paths/217 components. No runtime tests were performed.

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

One registered custom MobEffect: `twilightforest:frosted`. Forty custom damage declarations remain pinned from R2f1; **frozen, lich_bolt, lich_bomb and twilight_scepter have reviewed caller profiles**, while36 caller dispositions remain unfinished. They are not classified as unused. REVIEW_REQUIRED0; unfinished review is not ambiguity. Final VANILLA_DIRECT/COMPOSITE/EXTENDED lists are not available yet. Lich and Naga boss/defense semantics are closed; the remaining boss reviews are pending.

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
