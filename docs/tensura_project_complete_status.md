# Tensura project — complete current status

## Current snapshot and source authority

Snapshot date: **2026-10-11 UTC**. Repository: **pooofeeee/TNO-Tensura-Compat**. Branch: **`external-effects-catalog-research`**.

- Latest committed research HEAD and live GitHub branch HEAD: **`79d5212faff151e98e4323c0ae5d1bceb0f60a52`** (2026-10-09, NEB R2p3). The live ref was read through GitHub during documentation preparation.
- Latest local research checkpoint: **`R2q1-mowziesmobs-sunblock-native-callback`**. Its evidence, evaluation receipts and state-map changes are uncommitted in the worktree at this snapshot.
- Alex’s Mobs closure: **`dc08cda002029695ff1acc18ce8ed44f0f8ae90f`**, COMPLETE.
- External-catalog starting baseline: **`a5e85e610349120e21d62f4a80f1b607e36607fe`**.
- Documentation publication creates a later commit. The source HEAD above remains the immutable research baseline; the commit containing this document is its publication commit.

Authority order: current completion ledger and canonical per-mod reviews; current STATE/CAMPAIGN and finite queues; mod-level closure/validation/reproduction receipts; then historical checkpoints and narrative reports within their recorded scope. Uncommitted evidence is explicitly labeled below and its hashes are preserved in the historical archive.

Some older fields retain historical values. `docs/external-effects-catalog-research.md` still opens with the Cataclysm-era “ten external reviews” summary; `catalog-integrity-audit.json` is a PASS snapshot of 12 audited mods, 2,178 records and 6,222 numeric entries. Neither is the current overall total. `effect-catalog.json` has 2,911 records and six native-Tensura references, but its `last_completed_mod` field still names BOMD. Initial role counts in immutable census files are discovery roles; final disposition totals come from closure/queue reconciliation.

## Project purpose and boundaries

TNO-Tensura-Compat integrates external equipment with native Tensura systems on Minecraft 1.21.1. The first implemented integration registers Royal Variations’ Royal Bow in Tensura’s gear-existence registry. Later production work adds native Gear EP-based Stage progression and bounded scaling for Magic, Holy, Soul, Elemental/Slotting, Energy Steal and Severance, preserving native source identities, admission rules and downstream L2 defenses.

The External Effects Catalog is a separate research track. It records distinct combat/effect/control/resource/lifecycle mechanics, materially distinct delivery paths, exact numerical inputs, original consumers, vanilla comparisons and classifications from the exact installed JARs. Registry names, keyword matches and decompiled prose are discovery aids; native bytecode and retained resource evidence establish the contracts.

Current research protections preserve production, completed reviews and canonical evidence. The catalog work makes no new Stage policy, gameplay change, Minecraft runtime, Gradle/datagen execution or whole-pack compatibility claim. Earlier Phase 5F/6 runtime experiments are historical evidence with their own explicit fixture limits.

Purpose sources: [initial gear bridge](../src/main/java/com/tno/tensuracompat/core/gear/TensuraGearRegistrar.java), [Phase 5F plan](phase-5f-l2-apotheosis-benchmark.md), [Phase 6 implementation](phase-6-production-implementation.md), and [research scope](external-effects-catalog-research.md).

## External Effects Catalog status

The catalog is **PARTIAL overall**.

| Scope | Exact current total |
| --- | ---: |
| Requested target ledger entries | 23 |
| COMPLETE target entries | 15 |
| COMPLETE external semantic reviews | 14 |
| COMPLETE Tensura reference-only entries | 1 |
| PARTIAL target entries | 2 |
| PARTIAL entries with a genuine external blocker | 1 (NEB; included in the 2) |
| UNSTARTED target entries | 6 |
| Semantic records in completed reviews | 2,867 |
| Canonical NEB local semantic records | 44 |
| Total canonical semantic records | 2,911 |
| Delivery paths in completed semantic reviews | 3,844 |
| NEB canonical delivery paths | 58 |
| Total canonical delivery paths | 3,902 |
| Numeric candidates in completed reviews | 10,424 |
| NEB canonical numeric candidates | 347 |
| Total recorded canonical numeric candidates | 10,771 |
| Preserved native-Tensura family references | 6 |
| Mowzie records promoted by R2q1 | 0 |

Record/path totals are independently summed from the 15 canonical semantic-review files; candidate totals are summed from the current ledger’s recorded per-mod candidate counts. Tensura’s reference-only null counts and unstarted/Mowzie null counts are excluded from numeric arithmetic, not converted into assertions of zero mechanics. Candidate identities are not universally the same unit as unique physical instructions: each mod’s numeric audit defines its deduplication scope.

The full track’s final cross-mod synthesis, current aggregate integrity reconciliation, final report and owner review remain unfinished. The completed per-mod classifications remain valid within their accepted scopes.

## All requested mods

### Completed targets

COMPLETE means the accepted pinned static scope is closed. Tensura has a reference-only scope; it is not a full base-mod catalog.

| Target / ledger key | Semantic records | Delivery paths / references | Numeric candidates | Canonical evidence | Completion milestone |
| --- | --- | --- | --- | --- | --- |
| Cult of Azazel (`cultofazazel`) | 51 | 64 | 222 | [cultofazazel.json](benchmarks/external-effects-catalog/mod-reviews/cultofazazel.json) | `R2c3-complete`; [94532221ac23681deef5462f7932a8a405f5979e](https://github.com/pooofeeee/TNO-Tensura-Compat/commit/94532221ac23681deef5462f7932a8a405f5979e) |
| Variants & Ventures (`variantsandventures`) | 8 | 14 | 7 | [variantsandventures.json](benchmarks/external-effects-catalog/mod-reviews/variantsandventures.json) | `R2c1`; [2d1022ddb1c6436c0dd2142ee88c764bc8aed4c1](https://github.com/pooofeeee/TNO-Tensura-Compat/commit/2d1022ddb1c6436c0dd2142ee88c764bc8aed4c1) |
| Royal Variations (`royalvariations`) | 26 | 37 | 113 | [royalvariations.json](benchmarks/external-effects-catalog/mod-reviews/royalvariations.json) | `R2d-complete`; [7dcdcc4c03516928aa516fe10a1cd0d1fc1a9a91](https://github.com/pooofeeee/TNO-Tensura-Compat/commit/7dcdcc4c03516928aa516fe10a1cd0d1fc1a9a91) |
| Friends & Foes (`friendsandfoes`) | 31 | 46 | 132 | [friendsandfoes.json](benchmarks/external-effects-catalog/mod-reviews/friendsandfoes.json) | `R2e-complete`; [148a9e435b76118162695c5979f2ebce5e77307f](https://github.com/pooofeeee/TNO-Tensura-Compat/commit/148a9e435b76118162695c5979f2ebce5e77307f) |
| Twilight Forest (`twilightforest`) | 219 | 640 | 9 | [twilightforest.json](benchmarks/external-effects-catalog/mod-reviews/twilightforest.json) | `R2f-final-complete`; [86b6e670819be918b2df9ddcd73bf81b729282fc](https://github.com/pooofeeee/TNO-Tensura-Compat/commit/86b6e670819be918b2df9ddcd73bf81b729282fc) |
| Ice and Fire CE (`iceandfire`) | 81 | 228 | 0 | [iceandfire.json](benchmarks/external-effects-catalog/mod-reviews/iceandfire.json) | `R2g10b-iceandfire-complete`; [74492a5c2ec72051e8c0d142e16542a795aa5029](https://github.com/pooofeeee/TNO-Tensura-Compat/commit/74492a5c2ec72051e8c0d142e16542a795aa5029) |
| Eternal Starlight (`eternalstarlight`) | 127 | 274 | 1 | [eternalstarlight.json](benchmarks/external-effects-catalog/mod-reviews/eternalstarlight.json) | `R2h8b-eternalstarlight-complete`; [e8f4fd9f930b7ef262ac981faef109adc8f3e458](https://github.com/pooofeeee/TNO-Tensura-Compat/commit/e8f4fd9f930b7ef262ac981faef109adc8f3e458) |
| Bosses Rise / Block Factory’s Bosses (`block_factorys_bosses`) | 82 | 232 | 0 | [block_factorys_bosses.json](benchmarks/external-effects-catalog/mod-reviews/block_factorys_bosses.json) | `R2i9b-bossesrise-complete`; [0d53681feca19379ce8047d0cdc2db7b18806516](https://github.com/pooofeeee/TNO-Tensura-Compat/commit/0d53681feca19379ce8047d0cdc2db7b18806516) |
| Bosses of Mass Destruction (`bosses_of_mass_destruction`) | 44 | 85 | 0 | [bosses_of_mass_destruction.json](benchmarks/external-effects-catalog/mod-reviews/bosses_of_mass_destruction.json) | `R2j8-bomd-complete`; [bbd92263f0534929416b2ccfad969c472a1c7607](https://github.com/pooofeeee/TNO-Tensura-Compat/commit/bbd92263f0534929416b2ccfad969c472a1c7607) |
| L_Ender’s Cataclysm (`cataclysm`) | 1,037 | 1,047 | 1,776 | [cataclysm.json](benchmarks/external-effects-catalog/mod-reviews/cataclysm.json) | `R2k34-catalog-integrity-and-cataclysm-closure`; [68f3a5b1bf56a0a43e41980e2dd2d6877d82cd69](https://github.com/pooofeeee/TNO-Tensura-Compat/commit/68f3a5b1bf56a0a43e41980e2dd2d6877d82cd69) |
| Alex’s Mobs (`alexsmobs`) | 352 | 352 | 2,124 | [alexsmobs.json](benchmarks/external-effects-catalog/mod-reviews/alexsmobs.json) | `R2oj-alexsmobs-verified-complete`; [dc08cda002029695ff1acc18ce8ed44f0f8ae90f](https://github.com/pooofeeee/TNO-Tensura-Compat/commit/dc08cda002029695ff1acc18ce8ed44f0f8ae90f) |
| ArPhEx (`arphex`) | 466 | 482 | 3,933 | [arphex.json](benchmarks/external-effects-catalog/mod-reviews/arphex.json) | `R2m7s-arphex-full-native-integrity-and-coverage-complete`; [d12f024c3fb0c635e236be40a0e5777e1fe345ce](https://github.com/pooofeeee/TNO-Tensura-Compat/commit/d12f024c3fb0c635e236be40a0e5777e1fe345ce) |
| Alex’s Caves (`alexscaves`) | 145 | 145 | 367 | [alexscaves.json](benchmarks/external-effects-catalog/mod-reviews/alexscaves.json) | `R2m11-alexscaves-exact-citadel-dependencies-closed`; [82c5f052d8324613d6de71d548437b3f648faa7f](https://github.com/pooofeeee/TNO-Tensura-Compat/commit/82c5f052d8324613d6de71d548437b3f648faa7f) |
| Tensura (`tensura`) | Not enumerated | 6 family references | Not enumerated | [effect-catalog.json](benchmarks/external-effects-catalog/effect-catalog.json) | Reference-only scope; [2d1022ddb1c6436c0dd2142ee88c764bc8aed4c1](https://github.com/pooofeeee/TNO-Tensura-Compat/commit/2d1022ddb1c6436c0dd2142ee88c764bc8aed4c1) |
| Legendary Monsters (`legendary_monsters`) | 198 | 198 | 1,740 | [legendary_monsters.json](benchmarks/external-effects-catalog/mod-reviews/legendary_monsters.json) | `legendary-monsters-complete`; [07cf32a4a9e006cf3cf2b86ff0b88efbfe2a69ca](https://github.com/pooofeeee/TNO-Tensura-Compat/commit/07cf32a4a9e006cf3cf2b86ff0b88efbfe2a69ca) |

All 14 completed semantic reviews have no remaining native ambiguities in the completion ledger. Runtime compatibility, whole-pack balance, and future Stage eligibility are separate questions.

### Partial targets

| Target | Records | Paths | Numeric candidates | Current verified scope | Remaining work |
| --- | --- | --- | --- | --- | --- |
| TenSura: Not Enough Bosses (NEB) (`tensura_neb`) | 44 | 58 | 347 | R2p3: 476/476 local methods dispositioned; committed at [79d5212faff151e98e4323c0ae5d1bceb0f60a52](https://github.com/pooofeeee/TNO-Tensura-Compat/commit/79d5212faff151e98e4323c0ae5d1bceb0f60a52) | Four external dependency obligation groups; exact original ManasCore identity/bytes required. |
| Mowzie’s Mobs (`mowziesmobs`) | Unknown / ledger null; no canonical promotion | Unknown | Unknown; 2 bounded observed numeric inputs | Local uncommitted R2q1: 1 callback boundary, 3 classes, 8 methods; 3 reused Minecraft methods | Establish/recover initial finite census once; Sunblock application, duration/amplifier, refresh, holder consumers, later full mod/dependency/resource closure. |

Mowzie’s two observed inputs are 50 and 1.0; they are not a canonical numeric-candidate total. The historical 3,124 keyword candidates are not a finite census or a semantic count.

### Blocked targets

Blocked is a condition within PARTIAL, not an additional target counted in the total.

| Target | Blocker | Evidence | Consequence |
| --- | --- | --- | --- |
| NEB | Original installed ManasCore filename, exact version, SHA-256 and matching bytes unavailable | [tensura_neb-dependency-obligations.json](benchmarks/external-effects-catalog/tensura_neb-dependency-obligations.json) | Local static closure stands; inherited dispatch/storage/projectile/AI and dependency closure remain unverified. |

Mowzie’s selected callback has no external provenance blocker. Nether Expansion and Illager Invasion were skipped for the bounded R2q1 step because matching local cached bytes were not found; their ledger status remains UNSTARTED. This is not evidence of a permanent artifact blocker.

### Unstarted targets

| Target | Pinned filename | Semantic records | Numeric candidates | Existing discovery receipt | Remaining work |
| --- | --- | --- | --- | --- | --- |
| Jaden’s Nether Expansion (`netherexp`) | `Jadens-Nether-Expansion-2.4.0-BETA.7.jar` | Unknown / null | Unknown / not recorded | [netherexp-scan.json](benchmarks/external-effects-catalog/discovery/netherexp-scan.json) | Recover exact pinned bytes and retained discovery aids, then begin finite semantic/source/delivery research. |
| Illager Invasion (`illagerinvasion`) | `IllagerInvasion-v21.1.6-1.21.1-NeoForge.jar` | Unknown / null | Unknown / not recorded | [illagerinvasion-scan.json](benchmarks/external-effects-catalog/discovery/illagerinvasion-scan.json) | Recover exact pinned bytes and retained discovery aids, then begin finite semantic/source/delivery research. |
| Lycanites Mobs (`lycanitesmobs`) | `lycanitesmobs-0.0.1.jar` | Unknown / null | Unknown / not recorded | [lycanitesmobs-scan.json](benchmarks/external-effects-catalog/discovery/lycanitesmobs-scan.json) | Recover exact pinned bytes and retained discovery aids, then begin finite semantic/source/delivery research. |
| Darkest Souls (`darkestsouls`) | `DarkestSouls-Neoforge1.21.1-v1.2.3.3.jar` | Unknown / null | Unknown / not recorded | [darkestsouls-scan.json](benchmarks/external-effects-catalog/discovery/darkestsouls-scan.json) | Recover exact pinned bytes and retained discovery aids, then begin finite semantic/source/delivery research. |
| Ten No Game No Life (`tennogamenolife`) | `tennogamenolife-1.1.4.3.jar` | Unknown / null | Unknown / not recorded | [tennogamenolife-scan.json](benchmarks/external-effects-catalog/discovery/tennogamenolife-scan.json) | Recover exact pinned bytes and retained discovery aids, then begin finite semantic/source/delivery research. |
| Antarchy (`antarchy`) | `antarchy-1.1.1+1.21.1-neoforge.jar` | Unknown / null | Unknown / not recorded | [antarchy-scan.json](benchmarks/external-effects-catalog/discovery/antarchy-scan.json) | Recover exact pinned bytes and retained discovery aids, then begin finite semantic/source/delivery research. |

All six have broad scan/source aids. UNSTARTED describes semantic review; it does not mean that the mod has no effects.

## Important mechanics established by the research

These are selected findings with exact native details. Full contracts, delivery variants and method coordinates are in each linked canonical review.

| Target | Important finding | Canonical record / evidence |
| --- | --- | --- |
| Cult of Azazel | Manipulation retargets Piglin/ZombifiedPiglin around affected players on duration-mod-20 server ticks; the client also changes view/input. Stick pull applies Manipulation 600/0 and requested velocity (horizontal factor 1.4, Y 0.4); motion has no addEffect-success gate. | `cultofazazel:manipulation` / `cultofazazel:stick_pull` |
| Variants & Ventures | Gelid assigns frozen ticks to 240. Melee and owned-snowball admission differ; the snowball requests 4 thrown-source damage and sets the timer independently of hurt success. A frozen-timer assignment is not a fixed-duration stun. Poison payload is 100 ticks / amplifier 0. | `variantsandventures:frozen_ticks_set` / `variantsandventures:poison_payload` |
| Royal Variations | Dazed modifies MOVEMENT_SPEED and ATTACK_DAMAGE by `1 - 0.6*(amplifier+1)`. The modifier identifier’s “attack_speed” text does not change its actual ATTACK_DAMAGE holder. Knightly Fortitude gives armor +7, toughness +4 and knockback resistance +1 per level. | `royalvariations:dazed` / `royalvariations:knightly_fortitude` |
| Friends & Foes | Iceologer assigns frozen ticks 400 only to canFreeze recipients. Its spell enum BLINDNESS is presentation; that freeze path does not apply Blindness. Ice Chunk’s 12 indirect-magic request and freeze assignment have separate admission. | `friendsandfoes:iceologer_freeze` / `friendsandfoes:ice_chunk` |
| Twilight Forest | Lich shield is a separate integer resource, default 6, rather than HP. Eligible tagged incoming raw amount >2 removes exactly one shield; the shield branch returns false. Frosted combines its own movement modifier and vanilla frozen-state behavior. | `twilightforest:lich_shield_resource` / `twilightforest:frosted_package` |
| Ice and Fire CE | Frozen is NEUTRAL and repeatedly damps horizontal velocity by 0.25; non-EnderDragon airborne recipients also get Y -0.2. Native fire/death/IceDragon/creative gates and the separate weapon companion effects are preserved. | `iaf:frozen` |
| Eternal Starlight | Abyss conditions modify air, not HP/SHP: underwater player tick below Y=0 clamps air using the depth formula; post-damage subtracts 30 air when air>0 without requiring positive amount. Later drowning stays under native authority. | `es:abyss_air` |
| Bosses Rise | Dodge roll starts with duration 14; invulnerability is strictly roll>7, counters 14..8. Default two charges recover sequentially only after roll reaches -5. Serialization and native server admission are separate from runtime delivery guarantees. | `br:roll_resource` |
| BOMD | Shared damage handlers run before hooks, short-circuit native hurt on rejection, and still run after hooks with original source/request and boolean result. Native shield_piercing has five actual hurt callers; requested damage is not certified actual HP loss. | `bomd:shared_admission`; `bomd-total-source-coverage.json` |
| Cataclysm | Abyssal Fear cancels LivingHealEvent, including normal heal/Regeneration paths, without amount/amplifier scaling. Direct setHealth changes such as rebirth do not pass through that veto. | `cataclysm:abyssal_fear` |
| ArPhEx | AB Flight’s admitted server-side living tick requests vanilla Slow Falling 10/4 and ignores addEffect’s return. The local effect core does not itself add flight velocity. Broader native equipment, delayed attacks, actors, control and resource paths are separately cataloged. | `arphex:ab_flight` |
| Alex’s Caves | Sugar Rush has movement coefficient 0.25 per amplifier level; server ascending Y uses 0.85 and descending Y 0.45, with conditional Slow Falling 10/0. Exact Citadel 2.7.6 distinguishes local modifiers, active configured hooks, transport and lifecycle; existing client copies are not synchronized by native update/remove. | `alexscaves:sugar_rush`; exact Citadel obligation registry |
| Alex’s Mobs | Cockroach item callback chooses maracas state instead of healing on that branch; other accepted items request heal 5, and FOODSTUFFS set Breaded. Musician propagation also drives a real travel/navigation pause. Ownership, delivery and lifecycle remain distinct. | `alexsmobs:cockroach_native_heal` / `alexsmobs:cockroach_native_musician_motion` |
| Legendary Monsters | Ambusher attack tick 8 requests its native configured area damage; incoming FALL/TRIDENT/configured direct-arrow rejection is separate. Native death creates three Spikebugs and preserves silence/server/removal gates. | `lm:ambusher` |
| NEB | Carrion constructs an owned AuraSlash with skill and attack-derived damage, native speed 1/inaccuracy 0, and distinct talon offsets. Those local producer facts do not close inherited impact/block cutting or ManasCore dispatch. | `tensura_neb:carrion_aura_slash_producer` |
| Mowzie, local R2q1 | Sunblock requests heal 1.0 only at positive interval `50 >> (amplifier & 31)`, divisible entity tickCount, and health below max. Amplifiers 0..5 give 50/25/12/6/3/1; 6..31 give zero, and 32 wraps to 50. | `native-findings/mowziesmobs-sunblock-native-callback.json` (uncommitted) |
| Tensura reference scope | Six accepted families retain existing TNO references: Magic, Holy, Soul, Elemental, Energy Steal and Severance. Base-mod discovery is not repeated. | `effect-catalog.json:existing_tno_coverage` |

Native requests, stored state, callback outcomes, source construction and actual runtime damage/healing are distinct evidence claims. These findings preserve that distinction.

## Exact finite coverage and validation receipts

| Target | Classes in finite census | Total methods | Contract methods | Explicit exclusions | Final pending | Receipt |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| ArPhEx | 3,702 | 19,159 | 10,708 | 8,451 | 0 | `arphex-r2m7s-integrity-closure.json` |
| Alex’s Caves | 1,340 | 11,764 | 4,983 | 6,781 | 0 | `alexscaves-r2m11-citadel-dependency-closure.json` |
| Legendary Monsters | 1,217 | 8,819 | 6,023 | 2,796 | 0 | `legendary_monsters-closure-audit.json` |
| Alex’s Mobs | 1,126 | 11,434 | 5,546 | 5,888 | 0 | `alexsmobs-r2oj-mod-closure.json` |
| NEB local scope | 40 | 476 | 365 | 111 | 0 | `tensura_neb-r2p3-verification.json` |
| Mowzie local callback | 3 captured classes; full census unknown | 8 captured methods; full census unknown | Not yet reconciled | Not yet reconciled | Unknown | `mowziesmobs-r2q1-sunblock-verification.json` (uncommitted) |

The five reconciled census scopes sum to **51,652 methods = 27,625 contract methods + 24,027 explicit exclusions**. This is a sum of the listed scopes, not a whole-catalog method denominator. NEB’s zero local pending does not close external dependencies.

Earlier mods used whole-source coverage and watched-call/source matrices with different units. Ice and Fire’s closure records 726 installed classes, 188 watched methods, 130 targeted callers, five custom DamageTypes and seven factory callers. Eternal Starlight records a 1,384-class / 274-method audit and 18 custom source families. Bosses Rise records 802 classes / 157 watched methods. These counts must not be represented as the later census model’s exact contract/exclusion counts.

### Latest mod-level acceptance results

- **ArPhEx:** R2m7s integrity/classification/numeric/coverage closure PASS; 36 targeted tests PASS. Metadata-only final closure reused the byte-identical newly captured native/vanilla packets from R2m7r.
- **Alex’s Caves:** 46 native evidence packets reproduce BYTE_IDENTICAL; 8,680 unique native methods / 1,144 entries. Five exact Citadel dependency groups resolved. Final clean mod run: 194 tests in 23 modules, including 13 new dependency tests; focused protocol rerun 7 and native-absence check 1 passed. Later closure re-verification passed 20 focused tests. Counts describe their respective runs, not a new aggregate suite.
- **Legendary Monsters:** 198 records / 198 paths; 2,575 numeric labels reconcile to 1,740 native candidate identities plus 835 summary dispositions, zero unresolved. 39 targeted tool tests PASS; 20 pinned reproduction files PASS. All 465 JSON and 71 NBT templates audited (58 naturally reachable, 13 additional loadable), zero unresolved resources.
- **Alex’s Mobs:** independent replay PASS across 34 batches / 18 authored renderings; 302 tests across 31 modules PASS (294 existing + 8 dependency). 646 complete DATA_JSON/metadata resources and seven dependency groups closed. Pinned reproduction retained 42 native, 18 vanilla and 11 loader packets. 2,124 candidate identities bind through 2,120 distinct physical sites; one summary alias is recorded. Immutable 1,126-class / 11,434-method census verified without rebuild.
- **NEB R2p3:** authored rendering, canonical integrity, numeric audit, exact census reconciliation and five projected views PASS. Both available pinned packets reproduce BYTE_IDENTICAL; native method/class hashes match the census. 66 distinct static tests verified in 67 executions: initial 65 PASS / 1 preexisting queue-fixture error, corrected focused rerun 1 PASS; zero outstanding failures. Mod status stays PARTIAL.
- **Mowzie R2q1, local:** native packet BYTE_IDENTICAL; all three native classes and eight methods verified; three existing Minecraft methods checked against the pinned client; numeric-site, branch, return and registry-bootstrap checks PASS. No canonical promotion or full-mod completion.

These are recorded research results. Documentation preparation did not rerun Minecraft, Gradle, datagen or the research suites.

## Latest progress and retained blockers

### Committed NEB checkpoint — R2p3

NEB 2.0.0.3 and base Tensura 2.0.1.1 were recovered with exact accepted hashes. Three detailed discovery indexes were restored BYTE_IDENTICAL. The full local native packet retains all 476 methods and 50 JSON/metadata resources: 90 witnesses, 2,832,484 bytes. Selected base evidence captures 96 complete methods from 16 relevant classes, 508,291 bytes; 163 other methods in those classes are omitted. Ten bounded base facts are preserved. Omission establishes neither absence nor inherited behavior.

Four explicit obligations remain:

1. `tensura_neb:dependency:manascore_identity` — recover original-instance filename, exact version, digest and matching artifact.
2. `tensura_neb:dependency:skill_race_config_dispatch` — exact SkillAPI/RaceAPI/config/serialization and learned/toggled/recipient dispatch.
3. `tensura_neb:dependency:storage_event_projectile_critical_contracts` — concrete storage/dirty tracking, event aggregation, impact/status/critical and attribute consumers.
4. `tensura_neb:dependency:transitive_ai_and_loader_closure` — relevant inherited AI/registration/renderer contracts under exact original SBL/Architectury/GeckoLib and installed-loader identities after source recovery.

A prior search checked 328 cached JARs and found zero providers for the required ManasCore class. Dependency minima and development runtime’s reported 4.0.0.2 are not original installed identity: no corresponding original-instance artifact hash is retained, and the development loader differs. This source search was not repeated for documentation.

### Local Mowzie checkpoint — R2q1

The selected native registration, scheduler and healing callback uses the exact cached `mowziesmobs-1.21.1-1.8.2.jar`, SHA-256 `b8e7e39fb6430326de7fbb193db56588ee8bd04d0054527924fe588f37131e4f`. Three complete classes / eight methods retain 25,410 packet bytes. Three existing raw Minecraft 1.21.1 status-scheduling methods were reused and independently verified against the pinned client.

The callback calls its inherited implementation and discards the return, then evaluates the signed Java-int interval and healing gates. Scheduler and callback return true. There is no local server guard. Registration proof covers the Sunblock bootstrap; other registrations are not closed by this bounded class capture. Runtime healing is untested.

Current findings, verification, native specification/evidence and two project-evaluation receipts are uncommitted. Six state-map/ledger files also carry the local update: `AGENTS.md`, `STATE.md`, `CAMPAIGN.md`, `large-mod-campaign.json`, `mod-completion-ledger.json` and `research-decision.json`. Canonical views, 14 completed semantic reviews and all 15 COMPLETE ledger rows remain protected. The exact Sunblock continuation is recorded, but no full Mowzie campaign was authorized by the bounded research step.

### Production readiness remains a separate decision

The accepted post-Phase-6 decision is `POST_PHASE6_READY_WITH_OWNER_DECISIONS` at `a5e85e610349120e21d62f4a80f1b607e36607fe`, with zero listed engineering blockers. `OD1_SEVERANCE_PHASE7_BASELINE` remains `PENDING_OWNER_ACCEPTANCE` in that evidence: the owner must decide whether mechanically valid but severely Regenerate-limited Severance is an acceptable original Phase 7 baseline. Candidate C is rejected/exhausted. Phase 7 is not started or authorized in the retained readiness decision.

The current catalog does not settle that design choice or establish all-boss sustained balance, multiplayer or all equipment/defense combinations.

## How Mod Intelligence was used on this project

Tooling stayed in separate pinned checkouts. It was not merged or cherry-picked into the research branch, and production was not modified to use it.

| Project use | Pinned tool commit | Observed result | Repository receipt |
| --- | --- | --- | --- |
| NEB research workflow locator / source aid isolation | `a3145162e3b22e576fe216ef25482862ad5a6d2b` | Isolated V1 checkout recorded by R2p3; retained evidence, numeric/census tools and targeted checks used for native research. The closure does not claim a successful adaptive research planner. | `tensura_neb-r2p3-verification.json:measurements` |
| Actual next NEB obligation evaluation, 2026-10-10 | `e0918e782355756f718a1adcff1f346a26230327` | verify exited 0 with source/version/hash MATCH, 1,059 response bytes. Adaptive request exited 4, 363-byte ERROR: completed-review gate refused PARTIAL NEB. No plan/edit sites/tests were prepared. | `docs/benchmarks/mod-intelligence-repository-evaluation/neb-manascore-identity.json` (uncommitted) |
| Smallest unblocked Mowzie step, 2026-10-11 | `e0918e782355756f718a1adcff1f346a26230327` | verify exited 0, exact 1.8.2 source/hash MATCH. mods exited 0 and reported PARTIAL, semantic_catalog_available=false, mechanic_count=null. Native callback research then proceeded manually using retained witnesses. | `docs/benchmarks/mod-intelligence-repository-evaluation/mowziesmobs-sunblock-next-step.json` (uncommitted) |

The NEB adaptive request targets dependency-artifact recovery. The observed result proves the completed-review refusal; it does not separately test downstream support for that task after the refusal. Mowzie’s new research has no completed canonical mechanic or supported numeric-edit request, so adaptive planning was not applied.

Task Preflight is recorded as `NOT_RUN_NOT_INTEGRATED` in the NEB evaluation receipt. The documented potential handoff is before the CLI calls `catalog.find(intent['target'], args.mod)`; required inputs include repository/catalog path and HEAD, explicit task kind/target, exact request bytes/digest, expected native version/hash and full CLI result/exit code. No integration or automatic-research result was implemented or tested on this project.

No token, allowance or preparation-time savings telemetry is available for these project uses. Response sizes and witness/method/byte measurements are the actual recorded measurements.

## Verified reuse and selective retrieval

The existing tool-first workflow retrieves relevant complete methods from structured indexes, groups exact method equivalence, reuses locked canonical contracts and binds native numeric consumers incrementally. Full raw evidence stays preserved; grouping and filtering do not grant semantic coverage.

Alex’s Mobs final receipt records 250 existing item witnesses + 4 block witnesses + 196 global witnesses + 2 client witnesses = **452 reused method witnesses**, plus four additional equal-owner/search uses. It records zero census rebuilds, zero new generic infrastructure, zero subagents and zero claimed avoided detailed-body loads for that continuation.

| Recorded Alex retrieval | Complete methods selected | Full packet methods | Raw bytes | Selected bytes |
| --- | ---: | ---: | ---: | ---: |
| R2o7 | 431 | 1,915 | 12,405,472 | 3,109,525 |
| R2o8 | 170 | 1,915 | 12,405,472 | 1,306,112 |
| R2o9 | 218 | 1,915 | 12,405,472 | 1,883,354 |
| R2oa | 368 | 1,915 | 12,405,472 | 2,079,515 |

These are captured evidence-volume measurements. They do not establish token or allowance savings. NEB retained all local method bodies and selected only the required base boundary methods; Mowzie reused three exact raw vanilla methods. See the respective closure/evaluation receipts for full measurement scope.

## Remaining work and recommended continuation

1. Preserve the local R2q1 checkpoint and its raw evidence, independent verification and evaluation receipts. Review/commit research separately from this documentation publication; retain all completed canonical reviews.
2. Under a separately authorized bounded continuation, trace Sunblock’s real application producers, requested duration/amplifier, refresh/lifecycle and incoming/global SUNBLOCK-holder consumers. Establish/recover Mowzie’s initial finite census once before canonical promotion. Its whole-mod method/semantic totals remain unknown.
3. Recover the original installed ManasCore filename, exact version, SHA-256 and matching bytes. Resume NEB’s four retained dependency groups from R2p3 without rebuilding its census or repeating completed native families. Then perform dependency-aware mod-level closure.
4. For each of the six unstarted targets, recover the exact inventory-pinned artifact and saved discovery/source aids, establish the finite queue, review native producers/consumers/control/resource/lifecycle semantics, bind/deduplicate numeric candidates and audit relevant dependencies/resources.
5. After the remaining per-mod research is closed, reconcile current aggregate views/counts, cross-mod equivalence, legitimate source/delivery coverage and final catalog integrity; resolve retained broad-discovery/nested-resource/compatibility obligations using current per-mod receipts. Historical R2a anomalies are not automatically current blockers, and omissions are not closure proof.
6. Produce the final full-track report and owner-review decision. Decide future Stage integration, runtime validation/balance, and original Phase 7 only through separate authorized tasks; preserve the locked Phase 6 contracts and the retained Severance owner decision.

The present task publishes documentation. It does not change research completion states or authorize the continuation tasks listed above.

## Production protection

Recorded R2p3 and local R2q1 protections preserve all 14 completed reviews, all 15 COMPLETE ledger rows and canonical other-mod data. At documentation preparation, `git diff dc08cda002029695ff1acc18ce8ed44f0f8ae90f -- src build.gradle gradle.properties settings.gradle` is empty. This verifies the current research continuation against its production baseline; it does not erase earlier accepted Phase 6 implementation history.

Historical large-campaign protection also names `eb37f0bfc0e7aa863632f163881566c0ae2a8701`. Alex’s closure preserves the already-existing four source deletions against that older baseline; they were present at the safe handoff. Treat that retained delta separately from new production edits. Documentation publication stages only documentation files and preserves the existing worktree research changes.

## Current checkpoint and receipt index

- [STATE.md](benchmarks/external-effects-catalog/STATE.md) — `docs/benchmarks/external-effects-catalog/STATE.md`.
- [CAMPAIGN.md](benchmarks/external-effects-catalog/CAMPAIGN.md) — `docs/benchmarks/external-effects-catalog/CAMPAIGN.md`.
- [mod-completion-ledger.json](benchmarks/external-effects-catalog/mod-completion-ledger.json) — `docs/benchmarks/external-effects-catalog/mod-completion-ledger.json`.
- [large-mod-campaign.json](benchmarks/external-effects-catalog/large-mod-campaign.json) — `docs/benchmarks/external-effects-catalog/large-mod-campaign.json`.
- [jar-inventory.json](benchmarks/external-effects-catalog/jar-inventory.json) — `docs/benchmarks/external-effects-catalog/jar-inventory.json`.
- [effect-catalog.json](benchmarks/external-effects-catalog/effect-catalog.json) — `docs/benchmarks/external-effects-catalog/effect-catalog.json`.
- [effect-sources.json](benchmarks/external-effects-catalog/effect-sources.json) — `docs/benchmarks/external-effects-catalog/effect-sources.json`.
- [delivery-path-matrix.json](benchmarks/external-effects-catalog/delivery-path-matrix.json) — `docs/benchmarks/external-effects-catalog/delivery-path-matrix.json`.
- [vanilla-comparison.json](benchmarks/external-effects-catalog/vanilla-comparison.json) — `docs/benchmarks/external-effects-catalog/vanilla-comparison.json`.
- [behavior-primitives.json](benchmarks/external-effects-catalog/behavior-primitives.json) — `docs/benchmarks/external-effects-catalog/behavior-primitives.json`.
- [research-decision.json](benchmarks/external-effects-catalog/research-decision.json) — `docs/benchmarks/external-effects-catalog/research-decision.json`.
- [catalog-integrity-repairs.json](benchmarks/external-effects-catalog/catalog-integrity-repairs.json) — `docs/benchmarks/external-effects-catalog/catalog-integrity-repairs.json`.
- [catalog-integrity-audit.json](benchmarks/external-effects-catalog/catalog-integrity-audit.json) — `docs/benchmarks/external-effects-catalog/catalog-integrity-audit.json`.
- [alexsmobs-r2oj-mod-closure.json](benchmarks/external-effects-catalog/alexsmobs-r2oj-mod-closure.json) — `docs/benchmarks/external-effects-catalog/alexsmobs-r2oj-mod-closure.json`.
- [alexsmobs-final-independent-replay.json](benchmarks/external-effects-catalog/alexsmobs-final-independent-replay.json) — `docs/benchmarks/external-effects-catalog/alexsmobs-final-independent-replay.json`.
- [alexsmobs-final-resource-audit.json](benchmarks/external-effects-catalog/alexsmobs-final-resource-audit.json) — `docs/benchmarks/external-effects-catalog/alexsmobs-final-resource-audit.json`.
- [alexsmobs-dependency-obligations.json](benchmarks/external-effects-catalog/alexsmobs-dependency-obligations.json) — `docs/benchmarks/external-effects-catalog/alexsmobs-dependency-obligations.json`.
- [tensura_neb-r2p3-verification.json](benchmarks/external-effects-catalog/tensura_neb-r2p3-verification.json) — `docs/benchmarks/external-effects-catalog/tensura_neb-r2p3-verification.json`.
- [tensura_neb-r2p3-reproduction.json](benchmarks/external-effects-catalog/tensura_neb-r2p3-reproduction.json) — `docs/benchmarks/external-effects-catalog/tensura_neb-r2p3-reproduction.json`.
- [tensura_neb-unresolved-queue.json](benchmarks/external-effects-catalog/tensura_neb-unresolved-queue.json) — `docs/benchmarks/external-effects-catalog/tensura_neb-unresolved-queue.json`.
- [tensura_neb-dependency-obligations.json](benchmarks/external-effects-catalog/tensura_neb-dependency-obligations.json) — `docs/benchmarks/external-effects-catalog/tensura_neb-dependency-obligations.json`.
- [tensura_neb-tensura-boundary-facts.json](benchmarks/external-effects-catalog/tensura_neb-tensura-boundary-facts.json) — `docs/benchmarks/external-effects-catalog/tensura_neb-tensura-boundary-facts.json`.

Local R2q1 files are currently uncommitted:

- `docs/benchmarks/external-effects-catalog/native-findings/mowziesmobs-sunblock-native-callback.json`.
- `docs/benchmarks/external-effects-catalog/native-specifications/mowziesmobs-sunblock-native-callback.json`.
- `docs/benchmarks/external-effects-catalog/native-evidence/mowziesmobs-sunblock-native-callback.json`.
- `docs/benchmarks/external-effects-catalog/mowziesmobs-r2q1-sunblock-verification.json`.
- `docs/benchmarks/mod-intelligence-repository-evaluation/neb-manascore-identity.json`.
- `docs/benchmarks/mod-intelligence-repository-evaluation/mowziesmobs-sunblock-next-step.json`.

[Historical archive](project_history_complete.md) preserves their receipt snapshots and hashes for this publication.
