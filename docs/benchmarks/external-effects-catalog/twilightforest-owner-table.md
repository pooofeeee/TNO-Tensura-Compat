# Twilight Forest — R2f2 partial, Frosted section reviewed

The installed4.8.3345 review is **PARTIAL**. Frosted and its seven original producer contracts are now resolved, with two reviewed package drafts and13 source/path cases. **Zero final Twilight records are promoted.** Full mod mechanic, boss, defense, item and final source totals remain unknown. The four accepted reviews remain116 mechanics/161 paths/217 components. No runtime tests were performed.

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

One registered custom MobEffect: `twilightforest:frosted`. Forty custom damage declarations remain pinned from R2f1; **frozen now has a reviewed caller profile**, while39 caller dispositions remain unfinished. They are not classified as unused. REVIEW_REQUIRED0; unfinished review is not ambiguity. Final VANILLA_DIRECT/COMPOSITE/EXTENDED lists are not available yet. No boss or boss-defense review is closed.

Four pinned compatibility candidates have no direct Twilight name hits; generic conditional hooks remain, including Antidote duration reduction and player recipient/owner damage hooks. This is scoped static attribution, not pack-wide compatibility. No production fixes were made.

Particles, sounds, color/icon, repair/acquisition and registration infrastructure are excluded as separate combat mechanics. Other mod areas remain unreviewed. Subset fixtures are preserved; global minimum runtime runs remain R3.

Details: [reviewed section](semantic-sections/twilightforest-frosted.json), [current drafts](partial-drafts/twilightforest-r2f2-partial.json), [compat mapping](compat-findings/twilightforest-frosted.json), [progress validation](twilightforest-progress-integrity.json), [full validation](r2f2-partial-validation.json).

Next: Naga and Lich systematic boss review, especially actual Lich shield-source admission. All remaining bosses, mobs, items, damage callers and final promotion remain pending. Ice and Fire is UNSTARTED. Phase6/production/Stage remain unchanged. R2f1 evidence remains preserved rather than redone.

Protected Frosted checkpoint: `9de2fa52b435b49296e7e59472864e3a1e49e52b` (local/live equality and clean tree verified). Save mode began at76% usage after validation/push. No boss semantic section was started. Exact next action: trace Lich.hurt/getPhase/shield state and legitimate source paths, then complete Lich and continue Naga/remaining bosses. Stop for owner review; do not repeat Frosted.
