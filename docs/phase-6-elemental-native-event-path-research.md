# Post-Phase-6 Elemental native-event-path research

## Recovery and scope

Source: `b50061eb9040474a7fb8bdeb780f46a30201d63f`, verified against live
`origin/phase-6-candidate-c-sustained-viability-research` on 2026-09-07.
All remote heads were inspected and fetched; no newer Elemental research existed.
The working tree was clean. Research branch:
`codex/post-phase6-elemental-native-event-path-research`.

Phase 6 Stage and Magic/Holy production remain complete and locked. Candidate C
is rejected and exhausted, including RW=1; no Severance/Regenerate work is
reopened. Original Phase 7, Soul and Energy research are outside this task.

## E1: installed path and first static divergence

The installed Tensura artifact is Modrinth `Br0kXPwc:uw05A7u2` (2.0.1.1).
Inspection uses its class bytecode and local Vineflower 1.10.1 decompilation;
third-party source and JARs are not committed. The reproducible bytecode audit
and artifact hashes are in `benchmarks/phase6-elemental-native-event-path/e1-static.json`.

The existing 320/320 absent-event study used only Earth, not all five elements.
Its real Slotting release was valid, but
`Phase5FSuiteBBenchmark.Session.dispatchSlottingProjectile` called
`onHit(HitResult)` with an `EntityHitResult`, captured state, then discarded
the projectile before any ordinary flight tick.

The installed native flight path is different:

1. `ItemStack.releaseUsing` invokes native `SlottingHelper.onRelease`.
2. A matching single-core combination creates a native Tensura projectile,
   retains its owner, computes weapon-derived damage, sets native utility
   data, and adds it to the world. The intercepted release creates no Royal Arrow.
3. `TensuraFlyingProjectile.tickHandler` searches its swept collision box with
   `canHitEntity`, invokes ManasCore `EntityEvents.PROJECTILE_HIT`, and, unless
   its result is PASS, calls **the two-argument**
   `onHitEntity(EntityHitResult, ProjectileHitResult)`.
4. That callback checks eligibility and calls `applyHitEntity`, then
   `hitEntity`. PASS skips everything; HIT_NO_DAMAGE preserves its native
   no-damage semantics. Positive native damage reaches `dealDamage`.
5. `TensuraProjectile.dealDamage(Entity,float,float)` creates the native source
   and invokes the target's native hurt path. Tensura defenses and L2 remain
   downstream and authoritative.

By contrast, vanilla `Projectile.onHit(HitResult)` invokes **the one-argument**
`onHitEntity(EntityHitResult)`. Its base implementation is an empty return.
Neither Tensura base class nor these five projectile subclasses overrides
that one-argument method. This is an overload mismatch in the historical
benchmark dispatch, before native target admission and damage creation.
It is not yet a runtime conclusion at E1; E2 must reproduce it and compare
normal ticking of genuinely released projectiles without injecting callbacks.

## Element-specific native implementation

| Element | Single-core projectile | Native source | Distinct installed behavior |
|---|---|---|---|
| Earth | stone_shot | earth_elemental | Speed 3; knockback 1.5; elemental flag true; water/lava survival |
| Fire | fire_bolt | fire_elemental | Speed 2; burn 100 ticks; FLAME element; elemental flag true |
| Space | space_cut_projectile | space_elemental | Speed 1.75; size 1.5; elemental flag true; water/lava survival |
| Water | water_ball | water_elemental | Speed 1.25; knockback 1; burn -1; constructor leaves elemental flag false; block hit extinguishes nearby entities |
| Wind | wind_sphere | wind_elemental | Speed 1; knockback 3; no gravity; two-argument callback adds native wind explosion before superclass callback |

All IDs in the table use the `tensura` namespace. Each combination has damage
coefficient 1.0, multiplied by native weapon damage. Water's different
elemental flag and Wind's callback override must be retained, not normalized.

Slotting has native item/content/draw/sneaking/exclusion prerequisites. The
damage creation path permits a null projectile skill and zero skill costs;
it does not require granting the shooter a spell or elemental affinity.
Owner context and target skills can still affect weapon damage, collision,
defenses and later damage processing. E2 will record actual context instead
of assuming these paths are interchangeable.

## Historical positive control

The accepted pre-flight contains 90 real Earth events on a neutral adapter.
Its temporary Java fixture was removed before the single committed checkpoint;
the exact invocation implementation is not in that commit. The report describes
an accepted native projectile-hit entry point. Its valid recorded events are
retained; no equivalence with the later committed `onHit` harness is assumed.
E2 supplies a reproducible comparison using normal native ticking.

## Checkpoint ledger

| Checkpoint | Status |
|---|---|
| E1 recovery and installed bytecode audit | Complete; static assertions pass; runtime hypothesis pending |
| E2 bounded native flight and historical-dispatch comparison | Pending |
| E3 final interpretation and decision | Pending |

No production correction or development prerequisite-restoration prototype has
been implemented. A native fix is justified only if runtime evidence identifies
a legitimate missing prerequisite in production, rather than a fixture defect.
