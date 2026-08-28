# Phase 5F Suite C — Apotheosis + TNO

Status: harness gate accepted; official matrix pending.

Suite C reuses the accepted Suite B boss/level, Native + S0-S7, ten-release, and 200-tick fixture while equipping the accepted `ANCIENT_SINGLE_PROSPEROUS_SPECTRAL` Apotheosis profile. It is development-only and reports `production_combat_mutated=false`.

## Legal combined item

The runtime compatibility API proves that every tested TNO family Engraving is incompatible with `tensura:barrier_piercing`. Suite C therefore preserves the complete accepted Ancient rarity, ten effective-level-1.5 affixes, five Perfect gems, effective APO attributes, and all eight compatible Suite A enchantments, then replaces only `tensura:barrier_piercing` with the active family Engraving. The harness fails on an illegal pairwise enchantment set or any other APO profile drift.

## Projectile lifecycle gate

The initial controlled-collision harness called the real projectile hit callback but left the dispatched entity alive in the final collision lane. The same entity could collide again on the next tick, yielding two physical and two Magic events from one projectile. This was a benchmark-harness defect, not a production combat defect.

The corrected harness discards only the entity whose legitimate hit callback has completed. It records every spawned entity ID/UUID and every entity ID/UUID that reaches the damage event, then rejects a second physical event from the same UUID. Genuine extra projectiles remain intact and are dispatched independently.

The accepted Magic/Luminous diagnostic gate produced:

- 4/4 cases and 40 rows, zero `case_error`;
- zero duplicate-event, same-projectile-rehit, recursion, Mark, L2-bypass, or Tensura-bypass flags;
- exactly two unique spawned projectile UUIDs per release;
- the two legal entity outcomes `royalvariations:royal_arrow` and `minecraft:spectral_arrow` from the locked Spectral affix;
- exactly one physical `minecraft:arrow` event and one `tensura:magic` event per unique projectile;
- the exact Ancient profile: ten valid level-1.5 affixes, five Perfect gems, five sockets, and the accepted effective APO attributes.

Diagnostic logs are not accepted evidence and are not tracked. Official JSONL is extracted only by `scripts/extract-phase5f-suite-c.ps1`, whose strict validation rejects malformed stages/profile identity, illegal enchantments, unknown projectile types, reused projectile UUIDs, event duplication, Mark, production mutation, or L2/Tensura bypass.

Official captures may opt into vanilla server tick sprint. This removes wall-clock sleeping only: every case still advances the locked 200 server ticks, fires ten releases at the same 20-tick spacing, and observes the same tick-based cooldown, DoT, regeneration, and L2 logic. The catalog records `server_tick_sprint_enabled` so this execution detail is never implicit.

The controlled dispatcher also records pending sibling projectiles discarded after an earlier projectile from the same genuine APO multi-projectile release defeats the target. Those siblings retain their spawn entity IDs/UUIDs but are not forced through `canHitEntity` against an already-dead target and cannot contribute damage events.

For Severance, the evidence retains both the exact pre-round/native/staged Severance contribution and the actual combined physical `minecraft:arrow` amount entering L2. The Suite C validator does not equate those values: the legal APO profile changes bow base damage, and its enchantment/critical processing may further transform the combined event after the isolated Severance contribution has been calculated.
