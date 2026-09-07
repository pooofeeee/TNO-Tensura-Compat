# Post-Phase-6 Elemental native-event-path research

Current status: **E1-E3 COMPLETE; STOP FOR OWNER REVIEW.** Final branch:
`phase-6-elemental-native-event-path-research`. No production native-path fix
is indicated by this study. See E3 for the terminal decision and scope limits.

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
| E2 bounded native flight and historical-dispatch comparison | Complete; 90 cases validated, including native Fire Resistance before event dispatch |
| E3 final interpretation and decision | Complete; historical fixture defect proven; no production prerequisite restoration indicated; owner review next |

No production correction or development prerequisite-restoration prototype has
been implemented. A native fix is justified only if runtime evidence identifies
a legitimate missing prerequisite in production, rather than a fixture defect.

## E2a: continuity recovery on 2026-09-08

Fetched all origin heads. The newest remote and local HEAD was
`57d733755bca4acafa995e42a498f69e7b504dbe` on
`codex/post-phase6-elemental-native-event-path-research`, a direct descendant of
the supplied Candidate-C terminal checkpoint. No newer remote work or applicable
AGENTS.md was found. Three modified tracked files and five untracked files
contained an unfinished opt-in Elemental runner, three read-only observers, and
a strict extractor. All were retained, with no reset or overwrite, on the
owner-requested `phase-6-elemental-native-event-path-research` branch.

The recovered local trials are not accepted runtime evidence. Trials 1-5 failed
during fixture setup. Trial 6 completed 90 cases but fails the current extractor
at case 6 because its L2 initialization evidence is invalid. Trial 7 failed in
L2Complements construction before the research catalog. None can establish an
accepted E2 result. The current runner adds an explicit initialized-attachment
assertion; its runtime acceptance remains pending. The recovery build and all
54 Java tests pass. `e2a-recovery.json` preserves input hashes and trial status.

The runner compares six delivery modes per element and target: an unclassified
vanilla bow's untouched flight, historical Royal dispatch/discard, the same
historically dispatched projectile allowed to fly, Royal ordinary ticks from a
positioned lane at S0/S7, and Royal untouched flight at S0. Targets are the
neutral pre-flight-style adapter and the accepted Lv1000 Orc/Luminous profiles.
Setup-only positioning/resources/profile installation are explicit. All native
collision results, owner skills, utility settings, damage sources, and matching
defenses remain authoritative. The neutral adapter makes itself pickable; boss
eligibility is never overridden. No production prerequisite-restoration
prototype exists. The exact next task is strict E2 runtime acceptance, then E3
interpretation and owner review. Candidate C remains rejected and exhausted.

## E2: runtime proof

E2a was pushed and its live remote equality verified as
`c4b2c47b33574f0cdc8d16ec41bf3b4f36a15780` before new runtime work.
The accepted capture is `benchmarks/phase6-elemental-native-event-path/e2-runtime.jsonl`:
one catalog, 90 per-release rows, and one successful suite result. The full
compatibility stack reached Done, completed the matrix, restored the original
force-load state and shut down successfully. No synthetic damage, spell grant,
affinity grant, callback-result override, or production correction was needed.

The first resumed 90-case run exposed an overly restrictive inherited extractor
assumption that every native source must reach an incoming event. It is retained
as unaccepted diagnostic evidence in `e2-diagnostic.jsonl`. Extra read-only fields
were then added at the existing native hurt boundary; the second run proves the
Fire Resistance guard described below. The accepted capture was never edited to
satisfy the extractor. Its independently validated outcomes are:

| Element | Cases | Empty historical dispatch | Native source creations | Incoming family events | Applied family events | Matching Nullification | Native Fire Resistance before event |
|---|---:|---:|---:|---:|---:|---:|---:|
| Earth | 18 | 3 | 15 | 15 | 10 | 5 | 0 |
| Fire | 18 | 3 | 15 | 11 | 6 | 5 | 4 |
| Space | 18 | 3 | 15 | 15 | 10 | 5 | 0 |
| Water | 18 | 3 | 15 | 15 | 10 | 5 | 0 |
| Wind | 18 | 3 | 15 | 15 | 10 | 5 | 0 |
| Total | 90 | 15 | 75 | 71 | 46 | 25 | 4 |

### First missing prerequisite: Earth

All three historical Earth controls enter `Projectile.onHit(HitResult)` and
the empty one-argument `onHitEntity(EntityHitResult)` at projectile age zero.
They produce no native hurt call or damage event and leave HP/SHP unchanged.
Each corresponding rescue uses the **same already-released projectile UUID**:
after the empty call, ordinary world ticks invoke the native swept collision
search, `canHitEntity`, `EntityEvents.PROJECTILE_HIT` (DEFAULT/NONE), and the
two-argument callback. That callback calls the empty superclass callback and
then continues into `applyHitEntity -> hitEntity -> dealDamage -> target.hurt`.

Earth sources then exist on neutral, Orc and Luminous. Neutral/Orc reach applied
damage; Luminous cancels the existing incoming event. The first missing
prerequisite in the historical absence evidence is native collision dispatch,
not a missing skill, affinity, cost, owner, Stage or fabricated damage type.
Unmodified-position/velocity vanilla-bow and Royal-bow flight controls agree.
Slotting intercepts release and produces a native projectile, not a Royal Arrow.

### Other elements and authoritative target guards

Fire, Space, Water and Wind reproduce the same empty historical overload and
successful source-creation path after native flight. All five work through
untouched Royal flight on the neutral adapter, with one native family event.
At native/S0/S7, the native damage argument is 1.00/1.05/1.40 for every element.
Speed, knockback, burn, gravity, core count/capacity, owner and source identities
match the installed values; no double scaling or unexpected source appears.
Water retains `elementalAttack=false` and null magic type while still creating
`tensura:water_elemental`. Wind retains its native two-argument override and
non-damaging wind explosion; no extra damaging wind source is observed.
Fire's ordinary later `minecraft:on_fire` attempts are recorded separately.

Four Fire/Orc cases reach native `dealDamage` and construct the correct
`tensura:fire_elemental` source, but have `IS_FIRE=true` and the real vanilla
Fire Resistance effect active. The native call returns false with unchanged
HP/SHP and no incoming event. Installed `LivingEntity.hurt` tests that exact
combination before `CommonHooks.onEntityIncomingDamage`; `e2-static.json`
reproducibly asserts the bytecode order. The remaining Fire/Orc case has no Fire
Resistance and reaches one incoming/applied family event. Thus source creation,
incoming event dispatch, and applied damage are three distinct observations.

All 25 Luminous native-flight cases have their respective Earth, Flame, Spatial,
Water or Wind Attack Nullification toggled on. Their source and incoming event
exist, the event becomes cancelled, native hurt returns false, and no family
Post event follows, including at S7. No matching-defense bypass is introduced.

### Fixture limits

The boss trait maps are the accepted initialized Lv1000 profiles at release and
after measurement. Setup replaces randomly generated L2 traits but does not
clear their already-applied temporary effects. The Fire Resistance cases and
some Gravity/Moonwalk residue are explicitly visible in the new effect traces.
Installed L2 `FieryTrait`/`SelfEffectTrait` supplies a native Fire Resistance
precedent; this capture does not trace which earlier callback originally applied
each effect. The **active effect and its native damage gate** are proven; an
innate Orc immunity or a Fiery trait in the final accepted profile is not claimed.
Effects are never removed to force a successful attack.

Native boss resource values vary with setup and are preserved in every row.
These single-release, 20-tick observations establish event-path availability,
not sustained DPS, calibrated damage balance, SHP viability, or exact equivalence
to earlier endgame durability fixtures. This is a fresh survival FakePlayer
comparison, not a new human-client multiplayer acceptance run. Other bosses,
multi-core combinations, and active PASS/HIT_NO_DAMAGE vetoes are outside this
bounded matrix; installed code retains those gates and no callback is forced.

### Validation and reproduction

Java 21 `gradlew.bat build` passes with 54 tests and zero failures/errors.
The strict extractor replays all 90 rows; eight corrupted-capture tests reject
missing events, overridden gates, replaced projectile identity, double scaling,
uninitialized L2, fabricated legacy damage, Nullification bypass, and an unproven
Fire Resistance exception. Evidence includes `e2-validation.json`,
`e2-extractor-tests.json`, `e2-static.json`, and `e2-provenance.json`.

```powershell
./gradlew.bat runServer -Pphase6_elemental_native_path=true -Pphase5f_runtime_mods_dir=run/elemental-runtime-mods
./scripts/extract-phase6-elemental-native-path.ps1 -LogPath <capture-log>
./scripts/test-elemental-native-path-extractor.ps1
./scripts/audit-phase6-elemental-native-path.ps1 -TensuraJar <installed-jar> -MinecraftJar build/moddev/artifacts/neoforge-21.1.248.jar -JavaHome <jdk21> -IncludeFireGuard
```

The runtime artifact hashes are in provenance; local third-party JARs are not
committed. E1 and E2 inspect different generated Minecraft archives; both pass
the same callback assertions, and E2 additionally inspects the patched runtime
hurt method. Their archive hashes are recorded separately without rewriting E1.

## E3: terminal interpretation and decision

E2 was committed, pushed, and verified against the live remote as
`db8d2583085aa7bd9ff6580adba70f271b97633f` before E3 analysis. The independently
recomputed decision is `benchmarks/phase6-elemental-native-event-path/e3-decision.json`.
Reproduce it with `scripts/analyze-phase6-elemental-native-path.ps1 -Check
docs/benchmarks/phase6-elemental-native-event-path/e3-decision.json`.

**Proven root cause of the historical Earth absence:** benchmark collision
dispatch chose the wrong overload and immediately discarded the projectile.
Native projectile existence and Stage scaling therefore did not imply that the
native collision/damage path had run. The first missing prerequisite was ordinary
native flight/collision dispatch. All five elements reproduce that distinction.

**Safe correction:** future Elemental research fixtures should let real native
projectiles tick, observe their native collision admission, and distinguish
source construction from incoming-event dispatch and applied damage. The E2
runner already provides this path without a replacement source or forced hit.
No missing production prerequisite was demonstrated, so no production fix or
development prerequisite-restoration prototype is justified. Fire Resistance,
matching Nullification, and any native projectile veto remain authoritative.

**Historical evidence:** the 320 absent Earth rows and the 90 accepted positive-
control rows remain byte-for-byte equivalent to their protected Git blobs.
Their observations are retained. The older blanket inference that the empty
dispatch proves boss-dependent native-event unavailability is superseded for
that harness. The removed pre-flight fixture cannot be reconstructed from its
single commit, and this study does not invent its implementation. E2 establishes
a reproducible positive control independently.

**Production boundary:** the entire core directory and every pre-existing combat
mixin remain unchanged from Candidate-C terminal HEAD. The only modified
pre-existing integration files register opt-in development observations and the
run property; added observers pass through the original native call once and
return its result. They cannot start a research session in production and are
dormant without the explicit development property. No Candidate-C/RW work,
Magic/Holy policy revision, Stage revision, or historical benchmark rewrite was
performed. No new production-mode runtime test is claimed by this study.

**Exact next task:** project-owner review of these Elemental findings. If accepted
and separately authorized, the next family in the established sequence is Soul
Eater's native `tensura:soul_scatter` eligibility research. It has not started.
Permanent production, another family, and original Phase 7 do not start
automatically. Candidate C remains rejected and exhausted.

| Protected checkpoint | Remote SHA verified before proceeding |
|---|---|
| E1 installed dispatch audit, recovered | `57d733755bca4acafa995e42a498f69e7b504dbe` |
| E2a recovered local harness and pending gate | `c4b2c47b33574f0cdc8d16ec41bf3b4f36a15780` |
| E2 accepted native-flight and defense evidence | `db8d2583085aa7bd9ff6580adba70f271b97633f` |
| E3 terminal decision | The commit containing this section; final response reports its verified SHA. |
