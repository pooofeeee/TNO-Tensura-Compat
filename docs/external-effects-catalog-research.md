# External combat effects catalog — separate research track

**Status: PARTIAL overall; R2c1 completes Variants & Ventures native discovery.** Phase 6 is complete and closed. This track does not reopen, supersede, recalibrate or change Phase 6, its Stage behavior, accepted family integrations, or production combat. Original Phase 7 is not started by this research.

Baseline: `a5e85e610349120e21d62f4a80f1b607e36607fe`. Branch: `external-effects-catalog-research`. Recovery found a clean working tree and the live readiness remote at this baseline; no earlier external-effects track existed. No applicable `AGENTS.md` was found. The dedicated branch was created from the verified baseline without resetting or discarding work.

The owner confirmed the installed instance at `C:/Users/youra/curseforge/minecraft/Instances/new`. The source directory is its `mods/` folder. Exact requested filenames, SHA-256 hashes, archive/class counts, version metadata, damage resources and mixin configuration names are recorded in [jar-inventory.json](benchmarks/external-effects-catalog/jar-inventory.json). Other instances and newer/older versions are not substituted. An inventory check is not a completed mechanical inspection.

**R1 inventory result: 23/23 exact target filenames available; zero unavailable.** Embedded metadata is preserved rather than silently normalized: Royal Variations declares `2.0` inside the requested `2.0.4` file, Darkest Souls declares `1.2.3.1` inside the requested `v1.2.3.3` file, and Legendary Monsters declares `1.21.1` as its mod version. Nether Expansion also has a shorter internal version than its filename. These are discrepancies in the exact installed files, not version substitutions. JAR SHA-256 identity controls subsequent inspection.

Four existing-compat candidates are pinned separately: `antarchy_tensura_compat-1.0.0.jar`, `tensura_iaf-neoforge-2.0.0.1.jar`, `rarcompat-1.21-0.9.7.jar`, and `ftb-xmod-compat-neoforge-21.1.9.jar`. R2 must determine their actual relevance and modifications; a filename alone does not establish behavior. These four are additional context JARs, not extra members of the 23 requested targets.

## Scope and method

The target is distinct **mechanics and materially distinct delivery paths**, not weapon count or effect names. Discovery must cover registered MobEffects, direct vanilla effects, attributes, events, callbacks, custom damage/source tags, projectiles/explosions, entity state, timers/stacks/buildup, healing/resource mutations, action/AI suppression, items/enchantments/accessories and skills. Cosmetic code and ordinary physical damage are excluded only after their behavior is assessed. Registry/keyword scans are candidate discovery aids, not completeness proof.

Every included effect will retain exact JAR/class/method evidence, behavior and numerical parameters, vanilla similarities/differences, flags for custom state/attributes/source/stack/buildup/threshold/immunity/removal, duration/strength semantics, legitimate source(s), and distinct delivery paths. Primary classification uses exactly one of the owner's ten categories. A pending review is marked unverified with no final classification; `REVIEW_REQUIRED` is reserved for actual unresolved evidence ambiguity, not work that has not been inspected.

Base Tensura 2.0.1.1 is a reference authority. Its six completed native TNO families are recorded as `TENSURA_NATIVE_EXISTING_TNO_COVERAGE`, with immutable accepted references and no repeated research. Tensura addons are reviewed for additional mechanics, keeping their use of base native helpers explicit. Existing compatibility-layer modifications are separately attributed; native source behavior is not inferred from a compatibility patch.

Minecraft 1.21.1 comparison will use implementation, including relevant native attributes, damage tags and control flow. Local mapped NeoForge artifacts are pinned as reference aids; where patches could matter, raw vanilla must be distinguished from loader changes. Names, icons and wiki descriptions are not authority.

Only parameter availability is observed. No Stage formulas or integration choices are made. There will be no boss/L2 tests, balance changes, compatibility fixes or production Java in this track.

## Artifact structure

| Artifact | R1 meaning |
|---|---|
| `jar-inventory.json` | Exact installed identities and metadata; availability established separately from mechanical discovery |
| `effect-catalog.json` | Per-mechanic catalog; empty at R1 means not discovered yet |
| `effect-sources.json` | Legitimate primary/alternate sources and code-proven equivalence groups |
| `delivery-path-matrix.json` | Distinct native delivery implementations, not merely delivery labels |
| `vanilla-comparison.json` | Actual behavior comparisons and primary classifications |
| `behavior-primitives.json` | Shared primitive grouping while preserving semantic distinctions |
| `research-decision.json` | Honest partial/final status, immutable baseline, boundaries and exact next task |

The final human table will contain mod, mechanic, registry ID, classification, actual behavior, vanilla equivalent/differences, numerical/scalable/binary parameters, delivery, primary/alternate test sources, implementation, existing compat modification, confidence and notes. The second matrix will group behavior primitives with their concrete implementations and minimum future source coverage. Neither table is complete at R1.

## Checkpoint ledger

| Checkpoint | State |
|---|---|
| R1 | Complete, pushed and live-verified: `1a362b65e075177f78792cbad12fb979203f2890` |
| R2a | Pushed and live-verified `2e9d999ca68c101ac26c9e41415a696db7c5f65b`: all external outer-JAR classes scanned, source aids prepared, first six provisional native findings pinned; not R2 completion |
| R2b | Pushed and verified `e380f8a2afce27ec768ec23ae4c6f19b3fb21483`: raw vanilla callback prerequisites and initial Cult of Azazel notes |
| R2c1 | Variants & Ventures native semantics COMPLETE; eight records, fourteen paths/predicates, five actor types; further Cult of Azazel work preserved as PARTIAL |
| R2 | In progress: semantic discovery across every available external target, including non-MobEffect mechanics and compatibility candidates |
| R3 | Pending: vanilla comparisons, classifications, code-proven deduplication and complete delivery/source mapping |
| R4 | Pending: final validation, report and owner-review decision |

## R2a partial discovery evidence

All 22 external target JARs and four compatibility candidates were scanned at class/member/instruction level: **18,601 parsed classes, zero class parse failures**. The broad filter produced 14,662 candidate classes and 85,421 candidate methods. These deliberately over-inclusive counts include harmless helpers/rendering and **are not distinct effect counts**. Base Tensura was not broadly rescanned. Six nested archives remain explicitly unverified. Nine JSON parsing failures are recorded (eight Mowzie world-generation resources and one ArPhEx dimension-type resource); none are silently omitted from the audit.

[discovery-audit.json](benchmarks/external-effects-catalog/discovery-audit.json) records identities, counts, nested archives and decompiler caveats. Source aids for all 26 scanned outer JARs were prepared with pinned Vineflower 1.10.1. Successful decompiler exit is insufficient: failed method bodies and warning markers remain listed for bytecode follow-up, including ArPhEx `DwellerLifestealProcedure`. Large reproducible indexes/source aids stay under ignored `run/external-effects-catalog/`; locator hashes, research tooling and reviewed bytecode witnesses are committed. No mod JAR or whole decompiled source tree is committed.

The research class reader passed five tests: JDK disassembler agreement on instruction offsets including dense/sparse switch, wide locals, invokedynamic, interface calls, multidimensional arrays and wide constants; modified UTF-8 constants; malformed class rejection; malformed opcode rejection; and five installed Variants & Ventures classes cross-checked against `javap`. These validate tooling, not gameplay.

The first [native findings](benchmarks/external-effects-catalog/native-findings/variantsandventures.json) are pinned to 14 installed class/resource witnesses. They remain provisional entries with no final R3 classification:

| Mod | Native finding | Proven behavior / parameters | Distinct source paths | Pending comparison |
|---|---|---|---|---|
| Variants & Ventures | Poison payload (`minecraft:poison`) | Constructs duration 100, amplifier 0 | Thicket successful unarmed melee; Verdant native Arrow payload | Arrow target duration, native Poison ticking/eligibility/merging |
| Variants & Ventures | Gelid frozen-timer assignment | Absolute `setTicksFrozen(240)`; snowball also requests 4 thrown-source damage | Eligible successful unarmed melee; owned native snowball callback without the same eligibility/hurt-return checks | Native callback chain, timer decay, freeze protection and damage admission; timer is not asserted to be a 12-second stun |
| Variants & Ventures | Thicket Poison rejection | `canBeAffected` rejects POISON | Recipient eligibility override | Whether redundant with native undead protection |
| Variants & Ventures | Freeze eligibility overrides | Murk/Verdant false-return overrides; Zombie mixin false-return shim; Gelid powder-snow entity-type flag | Multiple distinct recipient implementations | Native freeze handling, mixin hierarchy and final deduplication |
| Variants & Ventures | Murk underwater arrow inertia | Owner-specific water inertia return `0.99F` | Native Murk bow projectile in water | Actual vanilla inertia/use; may remain delivery-only rather than standalone effect |
| Variants & Ventures | Zombie conversion to Gelid | 140 exposure threshold, 300 countdown, converts below zero; exit resets exposure/cancels conversion | Native powder-snow environment | Native conversion preservation and final treatment as effect versus source prerequisite |

These six are **not** a final count of distinct mechanics or proof the mod is fully covered. `effect-catalog.json` carries their native parameters, flags, method references, prospective sources and pending questions. Source/delivery/vanilla/primitive matrices remain incomplete. `REVIEW_REQUIRED` has not been used to label ordinary unfinished work.

The separately pinned [Antarchy compatibility data](benchmarks/external-effects-catalog/compat-findings/antarchy-tensura-data.json) establishes a `PRESENT` data contribution: 29 Tensura `entity_existence` definitions and zero Java classes. Values include declared SHP, magicule/aura ranges and optional Tensura ability IDs. These declarations belong to the compatibility layer. Loader interpretation and pack resource precedence still need inspection; no runtime resource amounts or skill activation are claimed from JSON alone.

Validation of the research boundary compares every pre-existing tracked file to `a5e85e610349120e21d62f4a80f1b607e36607fe`; only new research docs/evidence/tooling are allowed. A generated Python cache accidentally included in R1 is removed from tracking in R2a and locally ignored; its local file is preserved. Production, Stage, accepted Phase 6/readiness files and runtime remain unchanged.

Exact next task after protecting R2a: continue semantic discovery from these saved indexes and findings. Finish Variants & Ventures candidate/exclusion coverage and native prerequisites; review the remaining external mods, nested archives and relevant failed decompiler methods. Resolve the nine resource parsing anomalies and existing compat attribution. Do not rerun accepted R1 or Phase 6 research. R2, R3 and R4 are unfinished, and the owner-review decision is not yet available.

## R2b protected partial results and resume point

The usage check reached 80% of the current five-hour allowance. Under the owner's save-mode instruction, new research stopped and the following valid work was preserved. **R1 is COMPLETE. R2 is PARTIAL. Final classification, deduplication, minimum runtime source matrix and R3/R4 are UNVERIFIED/uncompleted.** No final effect count or `REVIEW_REQUIRED` list is asserted.

[Raw vanilla witnesses](benchmarks/external-effects-catalog/vanilla-evidence/variants-prerequisites.json) pin seven Minecraft 1.21.1 classes, 19 selected methods and seven entity-type tag resources. Cached client/mapping SHA-1 values match the cached 1.21.1 version manifest; SHA-256 identities are also saved. Obfuscated bytecode is resolved through the exact Mojang mappings. This avoids treating NeoForge development patches as vanilla.

The [native prerequisite findings](benchmarks/external-effects-catalog/native-prerequisites/variantsandventures.json) establish:

- Verdant's added Poison enters the arrow's **custom-effects** list. The target receives the constructed 100-tick payload; the separate base-potion duration-divide-by-eight branch does not apply to this path. Native hit admission and effect merging still matter.
- Gelid's listener runs through the superclass projectile callback before Snowball's ordinary 3-damage-against-Blaze/0-otherwise request. The listener's 4-damage request and later vanilla request are separate; their amounts are not asserted to add to actual HP loss.
- Vanilla freezing uses threshold 140, reduces the timer by 2 per living tick outside eligible powder snow, and requests freeze damage every 40 entity ticks while fully frozen and eligible. A 240 assignment is not a 12-second stun. Vanilla frost movement reduction is an **ADD_VALUE** modifier of `-0.05 * percentFrozen`, subject to its supporting-block condition. That branch does not check `canFreeze`, while freeze damage does.
- Thicket's explicit Poison guard overlaps the source mod's zombie-tag contribution and vanilla undead Poison/Regeneration eligibility. Murk's extra underwater-breathing tag also overlaps the skeleton/undead graph. These are native redundancy findings, not proof against later pack tag replacement.
- Murk changes actual vanilla underwater arrow velocity retention from `0.6F` to `0.99F`, through the native inertia return value.

An important authority distinction is preserved in [instance-loader-reference.json](benchmarks/external-effects-catalog/instance-loader-reference.json): the installed instance declares **NeoForge 21.1.244**, while the repository's mapped source aid is **21.1.248**. Raw vanilla Poison requests magic-source damage; the 21.1.248 source aid shows a NeoForge-specific poison source patch. The exact installed 21.1.244 client/universal artifacts are located and hashed, but their relevant behavior is **UNVERIFIED**. Do not silently substitute the development loader or attribute its patch to the source mod.

[Cult of Azazel partial notes](benchmarks/external-effects-catalog/partial-notes/cultofazazel.json) preserve five method-level class witnesses and six initial observations: Manipulation player-target aggro, active stick pull, held-stick fleeing navigation, owned Wither Skeleton target filtering, Chance Totem death cancellation/relocation/effect bundle, and a ZoneEffect marker whose consumers still need review. These notes are not assembled into final effect counts. Exact registry IDs, other deliveries, Curios helper behavior and broader entity/event coverage are unfinished. No action described in the mod code was executed by research.

**Exact resume:** verify this branch/HEAD/live remote without resetting; read the two R2b finding files above. Finish Variants & Ventures delivery/exclusion, tag/conversion and exact-loader prerequisites from the saved evidence. Continue Cult of Azazel at `NetherExp` registration, `CuriosCompat`, ZoneEffect consumers and remaining item/entity/event damage paths. Then review the remaining external mods, six nested archives, nine JSON anomalies, relevant failed decompiler bodies and compatibility attribution. Reuse the protected R1/R2a evidence and source aids. Do not repeat accepted Phase 6 or begin boss/L2/Stage work.

To validate a resumed checkout with the installed artifacts unchanged, run the research reader tests and `scripts/external-effects/validate.py --report <new-checkpoint>-validation.json`, then `git diff --check`. Large `run/` aids are reproducible with the committed scan/decompile tooling if missing; do not regenerate accepted data merely because the next checkpoint is unfinished. Finish and protect R2 before claiming R3/R4 completion. The final owner-review decision remains pending.

## R2c1 completed native discovery: Variants & Ventures

Recovery on the continuation found a clean tree, local/live remote at R2b, no newer work and no applicable `AGENTS.md`. All 49 existing JSON evidence files were read and recovery validation passed. Protected R1/R2a/R2b findings remain available; current completion is recorded separately in [mod-reviews/variantsandventures.json](benchmarks/external-effects-catalog/mod-reviews/variantsandventures.json). [mod-completion-ledger.json](benchmarks/external-effects-catalog/mod-completion-ledger.json) explicitly tracks all 23 targets. Base Tensura is complete only for its reference-only scope; other unreviewed mods remain UNSTARTED, not effect-free.

| Mod | Named effect/mechanic | Actual behavior | Vanilla? / closest mechanic | Composite? | Custom behavior | Delivery | Minimum actor required later |
|---|---|---|---|---|---|---|---|
| Variants & Ventures | Poison payload | Poison I, 100 ticks before native merging | VANILLA_DIRECT; actual Poison | No | External melee/arrow producers | Thicket melee; Verdant native Arrow | Both Thicket and Verdant |
| Variants & Ventures | Gelid freeze | Set frozen ticks to 240; native frost slowdown and conditional freeze DOT; snowball additionally requests 4 thrown damage | VANILLA_DIRECT; native frozenTicks and damage factories | Components recorded | Melee admission differs from snowball callback | Melee and native thrown snowball | Gelid, exercising both paths |
| Variants & Ventures | Poison/Regeneration rejection | Native undead tag rejection plus redundant explicit Thicket Poison guard | BINARY_MECHANIC; native effect eligibility | Two rejected holders | New tagged entity types; explicit guard | Recipient predicate | Thicket plus a tag-only variant |
| Variants & Ventures | Freeze rejection | Zombie mixin and separate Murk/Verdant predicates; Gelid tag | BINARY_MECHANIC; native canFreeze | Predicate variants | Global Zombie eligibility modification | Environment/recipient predicates | Zombie, Murk, Verdant, Gelid |
| Variants & Ventures | Murk arrow inertia | Water velocity retention 0.99 rather than 0.6 | VANILLA_LIKE_EXTENDED; arrow drag | No | Owner-specific coefficient | Native bow projectile through water | Murk |
| Variants & Ventures | Zombie → Gelid | Timed powder-snow conversion using native entity replacement | VANILLA_LIKE_EXTENDED; Skeleton → Stray pattern | Timer and replacement | Different recipient/output; no custom timer persistence or Skeleton conversion events | Environment | Ordinary Zombie |
| Variants & Ventures | Powder-snow walking | Gelid tag enables native surface collision; type flag marks powder snow not dangerous | VANILLA_DIRECT; powder-snow predicates | Two native predicates | New tagged/type-flagged recipient | Environment | Gelid |
| Variants & Ventures | Underwater breathing | Vanilla undead tag graph prevents ordinary drowning-air consumption | VANILLA_DIRECT; underwater breathing | No | Adds variant entity types; explicit Murk tag redundant | Environment | Murk representative; other variants recorded |

Fourteen code-distinct delivery/predicate cases require five actor types across their setups: Zombie, Gelid, Thicket, Verdant and Murk. This is not five total test cases or a claim that five spawn-egg items must be tested. Cross-mod source minimization remains R3. No gameplay was run.

The exact installed NeoForge **21.1.244** witnesses resolve R2b's loader uncertainty: Poison selects the NeoForge poison holder with magic fallback, effect admission passes through `MobEffectEvent.Applicable` (DEFAULT consults native eligibility; APPLY/DENY can override it), and projectile impact cancellation remains before downstream delivery. Vanilla tag identity, default merging/expiration, actual arrow post-hurt admission, freezing, conversion and water predicates are pinned independently. Pack-wide modifications from other mods remain explicitly UNKNOWN pending R2h; this does not turn a native-source completion into a claim about runtime interactions.

Conversion preserves equipment and several entity properties but creates a fresh target rather than copying HP/effects/arbitrary state. It does **not** call spawn initialization, so conversion alone does not grant the default offhand snowball; retained main-hand gear can also prevent unarmed freeze delivery. The source mod's conversion omits the installed Skeleton conversion events and does not persist its custom timers. The R2b shorthand “powder-snow block immunity” is now clarified: the entity-type `immuneTo` registration affects the native block-danger predicate, and is not a general damage immunity.

Cult of Azazel remains PARTIAL. [R2c1 notes](benchmarks/external-effects-catalog/partial-notes/cultofazazel-r2c1.json) protect registry identities, the newly traced client Manipulation controls, actual Curios totem lookup, Crimson Arrow ricochet, mask death/fire/repair behavior and zone-marker consumers. **Exact next target:** finish Azazel entity/goal attacks and remaining entity/environment paths, configuration parameters and source mapping, then protect the completed Cult review before moving to Royal Variations. No protected Variants & Ventures research needs restarting.
