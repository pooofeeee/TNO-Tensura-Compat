# Twilight Forest — R2f3 partial, Frosted and Lich reviewed

The installed4.8.3345 review is **PARTIAL**. Frosted remains protected at two reviewed package drafts and13 cases. Lich is now semantically complete at nine additional reviewed package drafts and24 delivery cases (14 shield-source cases): combined11 package drafts /37 delivery cases. **Zero final Twilight records are promoted.** Full mod mechanic, boss, defense, item and final source totals remain unknown. The four accepted reviews remain116 mechanics/161 paths/217 components. No runtime tests were performed.

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

One registered custom MobEffect: `twilightforest:frosted`. Forty custom damage declarations remain pinned from R2f1; **frozen, lich_bolt, lich_bomb and twilight_scepter have reviewed caller profiles**, while36 caller dispositions remain unfinished. They are not classified as unused. REVIEW_REQUIRED0; unfinished review is not ambiguity. Final VANILLA_DIRECT/COMPOSITE/EXTENDED lists are not available yet. Lich boss/defense semantics are closed; the remaining boss reviews are pending.

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

Exact next task: **Naga**, then Minoshroom / Knight Phantom, Hydra / Ur-Ghast, Alpha Yeti / Snow Queen. Do not repeat Lich or Frosted. Ice and Fire remains UNSTARTED. No runtime boss/L2 tests, production, Stage, Phase6 reopening, balancing or original Phase7 work.

Save boundary: usage reached75% during Lich finalization. Stop new research and protect R2f3 by validated commit/push/live-SHA equality. Naga has not started; it is the exact resume point.
