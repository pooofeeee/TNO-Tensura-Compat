# External combat effects catalog — separate research track

**Status: PARTIAL overall; R2f8f completes Redcap/Sapper, Kobold and Troll/ThrownBlock, and excludes unregistered Boggard. Twilight Forest remains PARTIAL at107 package drafts/305 delivery cases, with26/40 custom DamageTypes reviewed. Remaining mob bodies and registered producer checks are next. Variants & Ventures, Cult of Azazel, Royal Variations and Friends & Foes remain COMPLETE.** Phase 6 is complete and closed. This track does not reopen, supersede, recalibrate or change Phase 6, its Stage behavior, accepted family integrations, or production combat. Original Phase 7 is not started by this research.

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

## R2c2 protected partial Cult of Azazel continuation

R2c1 was committed, pushed and verified against the live remote at `2d1022ddb1c6436c0dd2142ee88c764bc8aed4c1`, with a clean tree, before continuing. New research stopped as usage approached the owner's approximately-80% boundary; the subsequent save-mode reading was 82%. This checkpoint preserves **20 partial observation groups and 25 additional installed-class witnesses**, plus a read-only snapshot of `netherman-common.toml`. These are not 20 finalized mechanics or a completion claim. [R2c2 partial notes](benchmarks/external-effects-catalog/partial-notes/cultofazazel-r2c2.json) contain the formulas, eligibility, callback identities, persistence details and exact remaining work. Their [bytecode witnesses](benchmarks/external-effects-catalog/native-evidence/cultofazazel-r2c2.json) retain individual instruction offsets and code hashes.

| Native source | Proven behavior now preserved | Remaining qualification |
|---|---|---|
| Azazel shield/cinematic | Incoming owner-hit counter triggers 100-countdown protection and heal(20); raw incoming amount can trigger a terminal cinematic before normal mitigation | Final classification/source cases; no runtime HP projection |
| Azazel Wind/Pull/Launch/Wheel | Four separate velocity-control paths with native mobAttack requests; Launch's explosion is audiovisual | Preserve all four deliveries and native downstream admission |
| Azazel Midas | Expanding native fire ring plus proximity counter replacing an inventory stack with raw gold | Pin exact vanilla inventory slot coverage; retain replacement separately from damage |
| Azazel prison | Builds a ring of walls, grows it when the target rises, removes tracked matching blocks on cleanup | Terrain control, not a fabricated stun; persistence limits recorded |
| Guardian/Welcomer | Rapid melee resets hurt cooldown; separate area punch; Welcomer switches range/damage values through a boolean | Goal invocation timing must be checked against the exact scheduler |
| Gilded Golem | Pulls items/players, consumes an entire item entity to heal, or requests magic damage then heals without testing damage success | Inherited Iron Golem attack/launch comparison remains |
| Laser | Moving invulnerable Mob hazard requests magic damage every two entity ticks and sets fire ticks to 60 | It is not an arrow; lifetime/reload condition preserved |
| Statue Bossunit / Statue | Random actual vanilla effects; separately, observation freezes statue navigation/horizontal movement and controls its next attack attempt | Exact vanilla effect formulas and package/source grouping remain |
| Manipulator / Believer | Mob Manipulation cast, native summons, prisoner replacement/Ghastly direct death; Believer protection/healing/sickness/death callbacks | Finish conversion timing, reverse paths, inherited summons and source alternatives |
| Crimson Honey / Void blocks | Custom bounce vectors; separate magic-plus-Darkness collision callbacks | Inherited block properties and remaining environmental classes remain |

Two interpretation corrections are explicit. Totemus does **not** clear its zone marker merely because a player leaves the radius; a type-3 Totemus clears it within its own scan. AzazelConfig's decompiled field layout also misleadingly moves `SPEC = BUILDER.build()` ahead of definitions. Installed bytecode proves definitions precede the final build and preserves the real section order. This is a reading-aid limitation, not an asserted mod bug. The configuration snapshot matches the declared defaults but does not prove a live game loaded it.

The current ledger is **2 COMPLETE** (Variants & Ventures and Base Tensura's reference-only scope), **1 PARTIAL** (Cult of Azazel), and **20 UNSTARTED** for semantic review. All 23 have their protected inventory/broad-scan disposition; UNSTARTED is not an absence-of-effects result. The eight completed per-mod catalog records and fourteen delivery cases remain the Variants & Ventures results. R2 remains PARTIAL; R3/R4, cross-mod primitives, final deduplication/source minimization and owner-review decision remain unfinished. Existing compatibility attribution remains separate and incomplete.

**Exact resume:** verify this branch and latest local/live remote SHA without resetting. Read `partial-notes/cultofazazel-r2c2.json` together with its prior-note links. Finish Cult's remaining prisoner/Ghastly/NPC/environment coverage, inherited ArrowItem/Goal/Inventory/WitherSkeleton/EvokerFangs/IronGolem/Honey/Dripstone behavior and vanilla effect/death comparisons. Then finalize registry IDs, package decomposition, classifications and legitimate source/delivery matrices. Protect Cult completion before moving to Royal Variations. Do not restart Variants & Ventures or the broad scan. No Minecraft, boss, L2, compatibility, Stage or Phase 7 work was started.

## R2c3-partial — usage-boundary preservation, not Cult completion

Recovery verified clean local/live remote R2c2 `dd7afafe21b09954e182b4634603ebbc8bd9096c`, with no newer work. This continuation preserves 136 additional selected witnesses (74 Cult/compatibility classes and 62 Cult data resources), 34 raw Minecraft 1.21.1 classes/86 methods and 18 installed NeoForge 21.1.244 patched classes. No broad scan was regenerated. The evidence filenames containing `cult-completion` name their intended use; they do not declare the semantic review complete.

[Detailed continuation notes](benchmarks/external-effects-catalog/partial-notes/cultofazazel-r2c3-partial.md) preserve inspected inheritance, scheduler, environmental, prisoner, potion, immunity, source and conditional compatibility observations. [The separate draft](benchmarks/external-effects-catalog/partial-drafts/cultofazazel-r2c3-partial.json) contains **29 provisional records and 33 paths**, ending after Gilded Golem. It is not promoted into the accepted catalog, and its classifications/comparisons/attribution still need final audit. Its counts are not final semantic counts.

The usage check reached **81%**, triggering the owner's save mode. **Cult remains PARTIAL; Royal Variations and subsequent mods remain UNSTARTED.** The minimum desired Cult COMPLETE result was not reached. Eight completed Variants & Ventures records, fourteen accepted delivery cases and all protected earlier witnesses remain unchanged. Phase 6 remains closed; no runtime, Stage, boss, L2 or production work occurred.

**Exact resume:** use the detailed notes and draft, resolve the flagged block-property/collision and remaining exact vanilla comparisons, then continue final assembly after Gilded Golem. Complete all mechanic/source/exclusion and compatibility mappings before promoting Cult to COMPLETE. Protect that completed checkpoint before Royal Variations. R2 remains unfinished; R3/R4 and the final owner-review decision remain unavailable. Validation at this checkpoint covers research tooling, hashes, references and allowed file scope; it is not gameplay or semantic approval.

Validation: all five research-reader tests passed; selected native/raw/installed-loader witness regeneration and draft reference checks passed in [r2c3-partial-validation.json](benchmarks/external-effects-catalog/r2c3-partial-validation.json). JSON parsing and comparison to protected HEAD confirmed that accepted effect and delivery arrays did not change. The research-only boundary and `git diff --check` passed. The remote was rechecked before commit and still matched protected R2c2. Commit/push/live-SHA verification completes this checkpoint; its exact hash is reported to the owner rather than embedded self-referentially.

## R2c3-complete — CULT_OF_AZAZEL_SEMANTIC_REVIEW_COMPLETE

Starting checkpoint: `a65d652571578156c93a78986ef4a28ae895113d`. Recovery found a clean tree and exact live-remote match with no newer work. The protected partial draft and all earlier evidence remain unchanged. This continuation completed the focused gaps and promoted the audited [Cult review](benchmarks/external-effects-catalog/mod-reviews/cultofazazel.json) into the accepted catalog and completion ledger.

**Cult is COMPLETE for installed native semantic/source/delivery review: 51 mechanic/package records, 64 distinct delivery or predicate cases, zero unresolved native REVIEW_REQUIRED items.** All 151 installed Cult classes and 62 data JSON resources have explicit dispositions. Evidence uses installed `cultofazazelneo-1.1.3.1.jar`, raw Minecraft 1.21.1 and exact installed NeoForge 21.1.244; no substitution of the development loader or gameplay testing. [Owner table and future source cover](benchmarks/external-effects-catalog/cult-owner-table.md) provide the readable index; the JSON contains exact behavior, component formulas, parameters, eligibility, state, source identities, comparisons and references.

| Primary classification | Count |
|---|---:|
| VANILLA_DIRECT | 10 |
| VANILLA_EQUIVALENT | 0 |
| VANILLA_COMPOSITE | 1 |
| VANILLA_LIKE_EXTENDED | 8 |
| CUSTOM_STATUS | 1 |
| CUSTOM_DAMAGE | 2 |
| CUSTOM_CONTROL | 17 |
| CUSTOM_RESOURCE | 4 |
| BINARY_MECHANIC | 8 |
| REVIEW_REQUIRED | 0 |

The final focused audit established:

- Crimson Web, Entrance and Traphive copy **Nether Wart Block**, retaining collision. They do not inherit vanilla cobweb slowing. Their native stage/open shapes change actual collision. Exact IDs include `netherman:eye_block`, `netherman:void_midcorner` and `netherman:voidnether_midcorner`; class-name guesses are not registry identities.
- Native Invisibility retains armor-coverage visibility calculation and the installed visibility hook. Milk/Honey/totem use distinct installed cure sets; Cult `removeAllEffects` attempts all effects but still permits individual removal-event vetoes.
- Statue observation uses plain server fields, not synchronized MobEffect state or `frozenTicks`. Guardian's third greeting roar, rather than every greeting phase, toggles eligible Grand Doors. The door modifies actual Player aim. Altar-created Azazel has a separate 40-tick protected spawn state, making its admission path distinct from egg creation.
- Wither and Bossunit statuses use their real vanilla holders; summoned Wither Skeletons and Evoker Fangs retain native attack/source identities. Doctor produces a parameterized actual potion and does not own the selected holder's semantics. Ghastly's direct HP/death branch, Midas inventory replacement, prisoner capture/release and custom motion/control remain explicitly distinguished from normal damage.
- Empty ZoneEffects, cosmetic phases, ordinary summons/arrows, trades/food, empty Nether Void variants and rendering/support behavior have explicit exclusions or source-context records. Crimson Honey Bottle has no native Honey/Poison cure. No custom Cult DamageType registry, attribute registry, attachment or Mixin was found.

[Compatibility attribution](benchmarks/external-effects-catalog/compat-findings/cultofazazel.json) maps 30 records to specific **GENERIC_CONDITIONAL_PRESENT** hooks and 21 to **NONE_PROVEN within the reviewed hook scope**. It does not mark everything PRESENT or assert universal pack isolation. No direct Cult-named external patch was found in the four pinned candidates; Cult's own optional Curios totem integration is separately identified. Withered Bracelet, Antidote Vessel, Obsidian Skull, Cross Necklace, Power/Vampiric Gloves, Umbrella, Kitty Slippers, Chorus Totem, Thorn/Shock Pendants and Cowboy Hat have explicit recipient/source/equipment gates. Full-pack runtime composition/resource precedence remains UNKNOWN outside this Cult-specific review.

The future matrix provides **25 fixture families covering all 64 cases**, with native descendants and shared participants retained. It is a local source/setup cover, not a proved mathematical minimum number of actors, items, spawn eggs or runs. Cross-mod source minimization remains R3 and was not started. No runtime source was exercised.

Validation: all five reader tests passed; final artifact checks verify per-record methods, raw/loader references, registry IDs, bidirectional effect/path links, duplicate IDs, compatibility mappings, fixture coverage, all class/resource hashes, reproducible assembly and unchanged accepted Variants & Ventures review. [Cult integrity results](benchmarks/external-effects-catalog/cult-final-integrity.json) and [full validation report](benchmarks/external-effects-catalog/r2c3-complete-validation.json) record the checks. The full report also verifies every pinned target/compatibility artifact and the immutable pre-track production boundary. Accepted catalog now contains 59 records and 78 delivery cases across Cult and Variants; those are current per-mod totals, not a finished global R2/R3 catalog.

Usage reached **82% during final validation**, so no new mod research began. Protect this COMPLETE checkpoint by commit/push/live-SHA equality and stop. **Exact next task: Royal Variations 2.0.4 semantic review**, after recovering the verified checkpoint. Royal Variations remains UNSTARTED. R2 remains PARTIAL: three target scopes are COMPLETE (Cult, Variants, reference-only Tensura), twenty UNSTARTED. Phase 6, production and Stage remain unchanged; no boss/L2 tests, compatibility fixes, or original Phase 7 work occurred.
## R2d — Royal Variations semantic review complete

Recovered a clean `external-effects-catalog-research` at
`94532221ac23681deef5462f7932a8a405f5979e`; fetch and live GitHub comparison found
no newer work. Cult and Variants reviews remain byte-for-byte equivalent to their
protected inputs. Phase 6 stays COMPLETE/CLOSED; production and Stage unchanged.

Installed authority: `royal-variations-[NeoForge]_1.21.1_2.0.4.jar`, SHA-256
`fa60862af8b7416fbb707c39e384d5c832a8f014b2e82c869e73a38658501f24`.
The completed [Royal review](benchmarks/external-effects-catalog/mod-reviews/royalvariations.json)
contains **26 semantic packages and 37 legitimate delivery cases**, with
**zero unresolved native REVIEW_REQUIRED items**. The
[owner table](benchmarks/external-effects-catalog/royal-owner-table.md) separates
the actual behavior, vanilla comparison, composite components and future sources.
All 172 native classes and 58 data resources have coverage dispositions; selected
method bytes, raw Minecraft 1.21.1 and exact installed NeoForge 21.1.244 are pinned.
This is static evidence, not observed damage, HP/SHP or gameplay testing.

Ten registered effects: Knightly Fortitude, Royal Blessing, Dazed, Undead Rush,
Chosen Victim, Marked, Trapped, Time Bomb, Pressing Gaze and Heaviness of the End.
Dazed modifies MOVEMENT_SPEED and ATTACK_DAMAGE by `-0.6*(amplifier+1)` with
ADD_MULTIPLIED_TOTAL. Its misleading attack_speed modifier identifier does not
change the actual ATTACK_DAMAGE holder. Vanilla Weakness is flat subtraction;
Dazed is not equivalent. Mark modifies movement/damage/attack speed by
`-0.1*(amplifier+1)` and armor by `-0.25*(amplifier+1)`, adds glowing, and has a
conditional nonplayer-owner hostile recruitment path. It is not direct damage
amplification. Both retain native attribute clamping and effect lifecycle rules.

Important delivery distinctions:

- Royal Arrow post-hurt/Mark requires native arrow hit success. Royal Bow enables
  Mark only on Royal Arrow; other bows use the unmarked createArrow path. The
  Royal Skeleton has its own marking constructor. `asProjectile` exists, but Royal
  registers no dispenser behavior, so it is excluded as a native delivery source.
- Bomb and Royal Creeper Dazed shells do not depend on successful explosion damage
  or positive block exposure. They retain explosion eligibility checks. Time Bomb
  separately requests fixed ownerless `minecraft:explosion` damage9 in radius6;
  its carrier is excluded. Its in-memory task is not restored after restart merely
  because a saved TIME_BOMB effect remains.
- Anvil, Royal Pearl and Royal Enderman arrival use `minecraft:indirect_magic`
  (8/7/4 respectively); Heaviness requires true hurt return. Source identity,
  armor bypass, normal Resistance/shield/cooldown processing and callbacks are
  documented separately from requested amounts. Royal defines no custom DamageType.
- Trapped combines native attributes with position pinning and jump/push/knockback
  vetoes. The net requires a nonboss-tag target with maxHP<=100 and effect eligibility.
- Skeleton Knighting checks `c:tools/bow`, while Royal writes `c:tools/bows`.
  Vanilla Bow is the proven minimum upgrade source; plural resource membership
  alone does not satisfy the singular queried tag.

Classification counts: VANILLA_DIRECT3, VANILLA_EQUIVALENT1, VANILLA_COMPOSITE4,
VANILLA_LIKE_EXTENDED11, CUSTOM_STATUS3, CUSTOM_CONTROL2, CUSTOM_RESOURCE1,
BINARY_MECHANIC1; CUSTOM_DAMAGE0 as a primary package label. Time Bomb's custom
damage primitive remains explicitly decomposed inside its CUSTOM_STATUS package.
Global verified catalog now contains 85 records and 115 delivery cases. R2 remains
PARTIAL overall; R3/R4 are not started by this checkpoint.

[Compatibility attribution](benchmarks/external-effects-catalog/compat-findings/royalvariations.json)
matches the pinned external hooks to actual recipient, owner, effect-category and
callback predicates. No Royal-specific modification was found in the four audited
external candidates. Generic conditional hooks are distinguished from Royal's own
Curios integration and the repository's locked production context. Full-pack dynamic
composition remains outside this native review, not a fabricated native ambiguity.

Validation artifacts: `royal-final-integrity.json`, `parser-validation.json` and
`validation-r2d-complete.json` under the catalog directory. The first two cover
26/37 package/path reassembly, references, classifications, duplicate IDs, source
cover, ledger, unchanged accepted reviews and all five parser/javap tooling tests.
The full validation also rechecks installed evidence and the immutable-baseline
scope boundary. No Minecraft process, boss/L2 tests, balancing or fixes were used.

Checkpoint meaning: **ROYAL_VARIATIONS_SEMANTIC_REVIEW_COMPLETE**. Exact commit SHA
is recorded by final local/live remote equality verification (a commit cannot store
its own SHA). Usage reached78% before final validation; save mode protects this
completed checkpoint and stops. **Friends & Foes remains UNSTARTED** and is the exact
next semantic review; do not repeat Royal, Cult or Variants or reopen Phase 6.


## R2e — Friends & Foes semantic review COMPLETE

Recovered `external-effects-catalog-research` from clean local HEAD and fetched live GitHub HEAD `7dcdcc4c03516928aa516fe10a1cd0d1fc1a9a91`; divergence 0/0, no newer work. No accepted checkpoints were reset or rescanned. Installed JAR `friendsandfoes-neoforge-4.0.23+mc1.21.1.jar`, SHA-256 `9fce7512691302b4512b30bf33fd1d4fc5b4c91abe7cbbe8cbce9e38afd6bd14`, is the native authority. Raw Minecraft 1.21.1 bytecode and exact installed NeoForge 21.1.244 overrides are pinned separately; mapped source was only a reading aid.

Decision: **FRIENDS_AND_FOES_SEMANTIC_REVIEW_COMPLETE**. There are **31 combat mechanic packages / 46 materially distinct paths / 13 local fixture families / 0 REVIEW_REQUIRED**. Global catalog now holds **116 mechanics / 161 paths**. All 341 native classes and 237 data/mixin resources have explicit dispositions. The global catalog remains PARTIAL: R3 source minimization and R4 final closure are unfinished.

- [Owner-readable mechanic table](benchmarks/external-effects-catalog/friendsandfoes-owner-table.md)
- [Completed review, formulas, sources, exclusions and native damage profiles](benchmarks/external-effects-catalog/mod-reviews/friendsandfoes.json)
- [Installed configuration snapshot](benchmarks/external-effects-catalog/friendsandfoes-config-snapshot.json)
- [Review integrity validation](benchmarks/external-effects-catalog/friendsandfoes-final-integrity.json)
- [Full checkpoint validation](benchmarks/external-effects-catalog/r2e-complete-validation.json)

Classification counts: VANILLA_DIRECT 1, VANILLA_EQUIVALENT 1, VANILLA_COMPOSITE 3, VANILLA_LIKE_EXTENDED 17, CUSTOM_CONTROL 5, CUSTOM_RESOURCE 3, BINARY_MECHANIC 1; CUSTOM_STATUS/CUSTOM_DAMAGE/REVIEW_REQUIRED 0. The one registered custom MobEffect, `friendsandfoes:reach`, modifies **block** interaction range and is explicitly excluded from combat. No custom DamageType is registered.

Distinct findings include native frozen-gauge assignments (not fixed-duration stun), the ice chunk's native magic source, real Illusioner decoy entities, pre-hit low-health custom totems, Wildfire's shield resource, Mauler's enchantment reserve/attribute coupling, Copper Golem statue state, Rascal's three-callback disappearance, and Glare's native healing/reveal producers. Compound packages retain their individual primitives. Special damage remains native magic, mob, arrow, fireball, thrown, freeze, lightning or fire damage; values are requests, not measured HP loss.

The pinned installed configuration has **enableWildfire=false**. Its native implementation is reviewed, but it is not an available positive runtime source in this configuration; no setting was changed. Glare direct hand-heal is dormant because its caller's negative food test contradicts the installed glow-berry tag; dropped-berry healing and passive regeneration are retained separately. Tuff-only temptation can leave the original scared TemptGoal with a null Player reference before the return-value mixin runs. This static failure case is recorded without claiming a successful lure or repairing it. Copper/Tuff owner-instance lightning rejection is not natural-lightning immunity: the vanilla lightning source is ownerless. Rascal counters are synced but not custom-saved. These are resolved native-code observations, not uninspected REVIEW_REQUIRED placeholders.

Validation: native JAR/specification and reference reproducibility; effect/path IDs, classifications, source/fixture cover, registry/tag/config checks, complete ledger, shared matrices and immutable accepted review/view rows; five parser/tooling tests; baseline scope and whitespace checks. Results are saved in the linked validation artifacts. No Minecraft process, boss/L2 test, compatibility fix, Stage change, balance/Curve C work or production edit was performed. Phase 6 remains COMPLETE/CLOSED; original Phase 7 remains unstarted.

Checkpoint discipline: save and validate this completed review, commit with meaning `FRIENDS_AND_FOES_SEMANTIC_REVIEW_COMPLETE`, push this branch and verify local HEAD equals live remote HEAD. Exact self SHA is reported after push rather than embedded recursively in its own commit.

Save boundary: finalization began at 76% five-hour usage; no new family research was started. **Twilight Forest remains UNSTARTED. Exact next task: its installed-JAR semantic review**, continuing the same side catalog track from this protected checkpoint. Do not repeat the four completed mod reviews or Tensura research. Stop after remote verification for owner review.


### R2e recovery and protection — 2026-09-19

The prior run completed local semantics and validation but was interrupted before commit/push. Recovery preserved all local Friends & Foes files. Branch/local HEAD and newly fetched/live GitHub HEAD still matched `7dcdcc4c03516928aa516fe10a1cd0d1fc1a9a91` (0/0 divergence); no conflicting or newer work existed. The completed research was reused rather than restarted.

The future source plan now explicitly names **15 necessary native producer families**, organized into the existing 13 fixture groups, covering all 31 mechanics and 46 paths. Each producer has a mapped path and a reason it cannot be substituted by the other listed producers. Recipient/control permutations and derived summons do not inflate independent source counts. The list and scope of its minimality claim are in `minimum_future_sources` and the owner table. This is not a claim about a minimum number of gameplay runs. A complete runtime cover remains unavailable with the pinned `enableWildfire=false`; no configuration or gameplay was changed.

Fresh review integrity and all five tooling tests passed. Full evidence/reference, shared-catalog, ledger, immutable-input, scope and whitespace validation is refreshed before committing. The three accepted prior mod reviews and their shared catalog rows remain identical to the protected starting SHA. Only side-research documentation, evidence and scripts are changed.


R2e COMPLETE was committed, pushed and verified at `148a9e435b76118162695c5979f2ebce5e77307f`. A follow-up tooling correction scopes immutable shared-row comparisons to the already protected mod keys and removes the permanent assertion that the next target must remain UNSTARTED. This preserves accepted rows while allowing later catalog additions. It changes no Friends & Foes classification, evidence, source/path count or production behavior. Twilight Forest is still UNSTARTED at this checkpoint.

## R2f1 — Twilight Forest semantic review PARTIAL

Recovered clean branch `external-effects-catalog-research` at local/fetched/live GitHub `3f3587aed34fea3670fdcbe26c2bb1d60094023c`, divergence0/0. No newer/conflicting work existed. Accepted reviews and the existing broad scan were reused. Installed Twilight Forest4.8.3345 is the native authority; selected class/method bytes and resources are pinned in `native-evidence/twilightforest-r2f1-partial.json`.

**TWILIGHT_FOREST_SEMANTIC_REVIEW_PARTIAL**: one draft Frosted package, seven provisional paths,79 witnesses (16 classes,40 damage declarations,23 damage-tag contributions). Zero Twilight records are finalized/promoted; the final mechanic/path/boss/item counts and minimum complete fixture cover remain unknown. The global accepted116 mechanics/161 paths/217 components are unchanged. The ledger now honestly records Twilight PARTIAL.

Frosted is not just Slowness: it sets the powder-snow flag each effect tick, conditionally increments the frozen gauge, adjusts incoming exact vanilla freeze damage, and down-ranks on incoming fire. Ice Arrow's local status callback does not check arrow hurt return. Helper, armor, bomb and progression producer contracts are saved without claiming complete delivery admission. The optional entity list in EntityExcludedDamageSource changes localized death attribution, not damage eligibility. Damage declarations are not counted as reviewed combat paths.

- [Owner table and limitations](benchmarks/external-effects-catalog/twilightforest-owner-table.md)
- [Draft package and paths](benchmarks/external-effects-catalog/partial-drafts/twilightforest-r2f1-partial.json)
- [Pinned declaration values, inspected areas and exact resume](benchmarks/external-effects-catalog/partial-notes/twilightforest-r2f1-partial.json)
- [Partial review entry](benchmarks/external-effects-catalog/mod-reviews/twilightforest.json)
- [Partial integrity checks](benchmarks/external-effects-catalog/twilightforest-partial-integrity.json)
- [Full checkpoint validation](benchmarks/external-effects-catalog/r2f1-partial-validation.json)

Save mode began at77% five-hour usage to preserve validation/push capacity before the approximate80% research boundary. This is a capacity stop, not an invented native ambiguity. REVIEW_REQUIRED remains0; unresolved-ambiguity census is null because review is unfinished. Relevant external compatibility predicates are still uninspected. All boss reviews, most items and the rest of semantic discovery remain open.

Exact next task: finish the existing Frosted draft against raw Minecraft1.21.1 and installed NeoForge21.1.244 tick order, lifecycle, mitigation, producer registration and data prerequisites; then continue the ordered unfinished Twilight coverage in partial notes. Do not redo accepted work. Ice and Fire remains UNSTARTED until Twilight COMPLETE is protected. No runtime, boss/L2 tests, production/Stage edits, fixes, balancing or original Phase7 work. Validate, commit, push, verify local/live SHA equality and STOP; the final response supplies the protected self SHA.

## R2f2 — Frosted comparison and producer contracts reviewed; Twilight PARTIAL

Recovered clean local/fetched/live branch at `9e6775b7ea75fbfdc7e6e9f9fc0e5858d966e187`, divergence0/0. Reused R2f1 and prior exact vanilla/loader witnesses; no broad scan or completed-mod review was repeated. Supplemental references pin only missing methods, distinguish raw Minecraft1.21.1 from installed NeoForge21.1.244, and record classes absent from the patched client archive that therefore use raw vanilla authority.

The [reviewed Frosted section](benchmarks/external-effects-catalog/semantic-sections/twilightforest-frosted.json) closes the original seven producer contracts, retaining **two package drafts / thirteen source-path cases / zero final promoted records**. Frosted is CUSTOM_STATUS; the complete Ice Bomb damage/zone/Yeti-replacement package is CUSTOM_DAMAGE. Classification applies to packages; component formulas remain explicit. The global accepted116 mechanics/161 paths/217 components and four completed reviews are unchanged.

Normal eligible Frosted buildup is amp+1 per server tick, not amp minus ordinary decay: effect ticking sets powder-snow state after Entity.baseTick resets it, and native aiStep later adds1. Full freezing requests ownerless vanilla freeze every40ticks; the exact-type incoming hook adds integer amp/2 before native mitigation. Native fire immunity/Fire Resistance rejects before down-rank, while later shield/cooldown rejection can follow it. Native effect merge, expiration, milk/totem cures, hidden state and equipment/spectator differences are resolved.

Configured Chill Aura is proven by installed JSON and native enchantment dispatch; it is not merely a codec. Ice Sword requires successful primary player hurt; Ice Arrow's own Frosted callback does not. Parent tipped/spectral callbacks require inherited hurt success and are lost on reload. Ice Bomb has player, dispenser and Alpha Yeti producers; contact/zone admission and explicit heat-sensitive multiplier differ from native freeze. Its custom frozen source remains normally armor-mitigated but bypasses Wolf body-armor absorption. Bomb save/load omits parent ownership serialization. No source identities, eligibility or production behavior were changed.

The [owner table](benchmarks/external-effects-catalog/twilightforest-owner-table.md), [current drafts](benchmarks/external-effects-catalog/partial-drafts/twilightforest-r2f2-partial.json), [scoped compat attribution](benchmarks/external-effects-catalog/compat-findings/twilightforest-frosted.json) and supplemental evidence preserve formulas and future fixture controls. REVIEW_REQUIRED0; remaining review is pending, not a fabricated ambiguity. Forty declarations remain preserved; frozen is reviewed USED, while39 caller dispositions remain unfinished, not classified as unused.

Validate `twilightforest-progress-integrity.json`, all five tooling tests, full `r2f2-partial-validation.json`, immutable scope and whitespace before commit/push/live-SHA verification. This subsection checkpoint does not mark Twilight COMPLETE. Next: systematic Naga/Lich boss review, with special attention to Lich shield admission, followed by the remaining boss/mob/item/damage caller sections. Ice and Fire stays UNSTARTED. No runtime, boss/L2, fixes, balancing, Stage, production or Phase7 changes.

R2f2 protection verified: `9de2fa52b435b49296e7e59472864e3a1e49e52b`, local/live GitHub equality and clean working tree. All five tooling tests and full evidence/reference validation passed. At76% usage, save mode stopped new research. Only the existing Lich source aid method locations were located; no boss semantic closure is claimed. The exact next task is Lich.hurt/getPhase/shield-state/source admission, then the complete Lich review and Naga/remaining bosses. A final metadata checkpoint records this stop boundary; no Ice and Fire work began.


## R2f3 — LICH_SEMANTIC_REVIEW_COMPLETE

Recovered clean local branch `external-effects-catalog-research` at `007aa5fd7610ba656bbd3b5f887a6bf1ac713b5a`; fetched origin and verified the same live remote SHA, divergence0/0, no newer/conflicting work. No reset/clean or accepted checkpoint repetition. The protected Frosted/Ice equipment section remains identical.

The [complete Lich subsection](benchmarks/external-effects-catalog/twilightforest-lich-review.md) closes all21 requested questions with installed Twilight4.8.3345 class/resource witnesses, raw Minecraft1.21.1 and exact installed NeoForge21.1.244 comparisons. Nine reviewed package drafts,24 delivery cases and14 shield-source cases are saved; combined Twilight draft11 packages/37 cases. Twilight remains PARTIAL and promotes zero final records. Accepted116 mechanics/161 paths/217 components are unchanged.

Default shield count is **6**. Qualified non-bypass shield hits require the native tag, raw amount strictly>2 and passage through cloak/clone/causing-Lich guards and delivery-specific admission. They remove exactly one shield and return false without HP processing, including the final shield. Phase2 already permits ordinary HP damage once shields reach0. The later native HP pipeline preserves source identity, armor/Resistance/protection/absorption, cooldowns and loader events. Shield counters never reach those later incoming/post hooks.

Native Player attack, projectile impact and timed TF parry can genuinely transfer Bolt ownership; simply redirecting velocity is insufficient. Lich's later defensive deflection restores a previous nonnull owner after the callback, but ownerless projectiles retain the callback's new Lich owner because setOwner(null) does nothing. Bombs lack the break tag and never collide directly with Lich. Native healing splash/cloud, fangs, Conduit, sonic boom and conditional ownerless-skull delivery retain their actual prerequisites. Healing-tipped arrows fail their initial shielded arrow hit; Guardian targeting excludes Lich; tag membership alone is not a positive control. The skull's later explosion is a distinct request that can attempt HP after its magic hit breaks the final shield.

Clone/master lifecycle, minion reserve/spawn failure, inherited Zombie behavior, Lich-hit minion buffs, discard-based mob/minion absorption, combat teleports and20tick cloak, all three custom damage profiles and return-dependent callbacks are preserved in [machine-readable evidence](benchmarks/external-effects-catalog/semantic-sections/twilightforest-lich.json). Four custom type caller profiles are now reviewed including the accepted frozen profile;36 declarations remain unfinished, not unused. No new MobEffect is invented; REVIEW_REQUIRED0 for this closed subsection.

Validation: [Lich integrity](benchmarks/external-effects-catalog/twilightforest-lich-integrity.json), [shared progress integrity](benchmarks/external-effects-catalog/twilightforest-progress-integrity.json), reproducible raw factory-call census, all native/raw/exact-loader evidence, immutable Frosted and accepted rows, five tooling tests, baseline scope and whitespace. [Full report](benchmarks/external-effects-catalog/r2f3-lich-validation.json). Exact checkpoint SHA is reported only after commit/push/live verification.

Exact next task: Naga from existing source aids, then Minoshroom / Knight Phantom, Hydra / Ur-Ghast, Alpha Yeti / Snow Queen. Do not redo Lich or Frosted. Ice and Fire is UNSTARTED; no runtime boss/L2 tests, compatibility fixes, Stage/production edits, Phase6 reopening, balancing or Phase7 work. Continue only after this bounded checkpoint is protected and sufficient usage remains.

Save boundary: usage reached75% during Lich finalization. Stop new research and protect R2f3 by validated commit/push/live-SHA equality. Naga has not started; it is the exact resume point.


## R2f4 — NAGA_SEMANTIC_REVIEW_COMPLETE

Recovered clean `external-effects-catalog-research` at local/fetched/live GitHub `d9dffb33a867aae9152a2ed3bc68f50b0b02f59d`, divergence0/0. No newer/conflicting work or resets. Frosted/Lich and completed external reviews were preserved; existing Twilight source aids were reused.

The [Naga review](benchmarks/external-effects-catalog/twilightforest-naga-review.md) closes attacks, defense, body routing, HP behavior, sources, exclusions, DamageTypes and classification. It saves **8 reviewed packages /18 delivery cases**, classification totals VANILLA_LIKE_EXTENDED3, CUSTOM_CONTROL3, BINARY_MECHANIC1, CUSTOM_RESOURCE1, REVIEW_REQUIRED0. Combined Twilight drafts are **19 packages /55 cases**, zero final promotions. Whole Twilight remains PARTIAL; accepted116 mechanics/161 paths/217 components remain unchanged.

Ordinary melee uses effective native attack5 and success-dependent added push. Blocking CHARGE produces mutual movement, ownerless generic2 self recoil and daze with false return; STUNLESS_CHARGE applies Player shield disruption and fixed mob_attack4 independently of hurt success. Segment contact requests mob_attack2 or Animal6. These are native sources, not CUSTOM_DAMAGE; only minecraft:mob_attack and minecraft:generic are used.

Twelve Entity parts share the head, forward the same source at two-thirds and have no independent HP. Multiple intersections share parent cooldown; no thirteenfold full-damage assumption is valid. Local inactive flags do not change inherited parent visibility: zero-sized parts remain returned, and local deactivation is not a proven universal untargetability/forwarding stop. No fix was made. Owner/direct home gates and explosion rejection precede native fire/fall immunity and ordinary mitigation. HP/segments/speed, constructor denominator12 versus final difficulty HP, first regeneration620, cumulative request-based daze interruption, staged death and combat terrain predicates are saved explicitly.

[Machine-readable section](benchmarks/external-effects-catalog/semantic-sections/twilightforest-naga.json), [owner table](benchmarks/external-effects-catalog/twilightforest-owner-table.md), [combined drafts](benchmarks/external-effects-catalog/partial-drafts/twilightforest-r2f4-partial.json) preserve each path's legitimate source, numeric/binary conditions and future fixture controls. Native, raw Minecraft1.21.1 and exact installed NeoForge21.1.244 witnesses are pinned separately. Four custom Twilight damage caller profiles remain reviewed;36 are still unfinished, not unused.

Checkpoint validation comprises [Naga integrity](benchmarks/external-effects-catalog/twilightforest-naga-integrity.json), protected25 Frosted/Lich files, prior Lich/progress checks, all five tooling tests, reproducible native/raw/exact-loader evidence, immutable accepted rows/baseline scope and whitespace. [Full report](benchmarks/external-effects-catalog/r2f4-naga-validation.json) records the completed result. No runtime boss or L2 testing occurred.

Research stopped at70% five-hour usage to reserve validation/commit/push capacity. Protect R2f4 with live remote SHA equality; exact self SHA is supplied after verification. **Minoshroom and Knight Phantom have not started** and are the exact next task, using existing source aids. Then Hydra / Ur-Ghast, then Alpha Yeti / Snow Queen. Do not redo Naga/Lich/Frosted or start Ice and Fire. No production/Stage edits, fixes, balancing, Phase6 reopening or Phase7 work. STOP after protecting this checkpoint.


## R2f5 — MINOSHROOM_KNIGHT_PHANTOM_SEMANTIC_REVIEW_COMPLETE

Recovered clean `external-effects-catalog-research` at local/fetched/live GitHub `c30b8c98fbbd8aefad86088cd027d4156b22924f`, divergence0/0. No newer/conflicting work; no reset or repeated accepted subsection. Installed Twilight4.8.3345, raw Minecraft1.21.1 and exact NeoForge21.1.244 remain the authorities.

Both bosses are semantically complete: **Minoshroom4 packages/11 cases; Knight Phantom6 packages/17 cases**. The ten new packages classify as VANILLA_LIKE_EXTENDED3, CUSTOM_DAMAGE2, CUSTOM_CONTROL4, BINARY_MECHANIC1; REVIEW_REQUIRED0. Combined Twilight drafts are **29 packages/83 cases**, zero promoted records. Whole-mod PARTIAL and accepted116/161/217 counts remain unchanged.

Minoshroom axing, sprint incoming+7, charge delivery/terrain and armor/shield-bypassing ground slam are resolved. Lift precedes hurt; ordinary axe shield disabling is inherited. Knight individual attacks, local coordination, attribute/dimension states, guard, movement, native throws and persistence/death behavior are resolved. The group has independent HP; final-survivor weapon randomness is overwritten to sword by renumbering. Throws keep projectile ownership but create ownerless DamageSources; parry, hurt-return-independent discard and unsaved pick payload are explicit. The shared melee helper uses attacker-as-affected-Entity for enchantment damage and lastHurtMob=self. Shared native lava cleanup adds two distinct environmental delivery cases. No fixes or fabricated damage were introduced.

New USED custom profiles: axing, slam, haunt, thrown_axe, thrown_pickaxe. Nine of40 profiles are reviewed;31 remain unfinished rather than unused. No thrown-block source or shield-spike source is inferred from a name. Alternate native Player/Minotaur tool paths and limited Wraith HAUNT caller witness are preserved without claiming full Wraith completion.

[Detailed owner review](benchmarks/external-effects-catalog/twilightforest-minoshroom-knight-review.md), [semantic packages, sources, predicates and five future fixture groups](benchmarks/external-effects-catalog/semantic-sections/twilightforest-minoshroom-knight.json), [combined draft](benchmarks/external-effects-catalog/partial-drafts/twilightforest-r2f5-partial.json). [Checkpoint integrity](benchmarks/external-effects-catalog/twilightforest-minoshroom-knight-integrity.json) verifies39 unchanged prior files, complete declared-method coverage for nine core classes, caller identities, transitive tags and key ordering/persistence differences. Five tooling tests, all native/raw/exact-loader witnesses, baseline scope and whitespace are included in [full validation](benchmarks/external-effects-catalog/r2f5-minoshroom-knight-validation.json).

Research stopped at68% five-hour usage to reserve validation/commit/push capacity. Protect R2f5 and verify local/live SHA equality; exact self SHA is supplied after push. **Hydra and Ur-Ghast have not started** and are the exact next task using existing source aids; then Alpha Yeti / Snow Queen. No Ice and Fire, runtime boss/L2 tests, Stage/production, fixes, balancing, Phase6 reopening or Phase7 work. STOP after checkpoint protection.


## R2f6 — HYDRA_UR_GHAST_SEMANTIC_REVIEW_COMPLETE

Recovered clean branch at local/fetched/live `79b3284081ee71a1a5c5ec0b18af02595535e379`, divergence0/0. No newer work, resets or repeated completed sections. Continued only the two authorized bosses from installed Twilight4.8.3345 source aids, with raw Minecraft1.21.1 and exact NeoForge21.1.244 comparisons.

**Hydra8 packages/22 cases; Ur-Ghast8 packages/21 cases.** Sixteen new packages: CUSTOM_DAMAGE4, CUSTOM_CONTROL5, CUSTOM_RESOURCE3, BINARY_MECHANIC1, VANILLA_LIKE_EXTENDED2, VANILLA_DIRECT1, REVIEW_REQUIRED0. Twilight now **45 drafts/126 delivery cases, zero promotions**, still PARTIAL. Accepted116/161/217 catalog totals remain unchanged. Four custom DamageTypes are newly proven USED: hydra_bite, hydra_fire, hydra_mortar and ghast_tear. Thirteen of40 reviewed,27 unfinished; no unused classification inferred.

Hydra part admission, shared HP/cooldown versus head counters, all head transitions, regrowth, attack scheduling, bite/flame/mortar, reflection/save behavior, control/terrain, healing and death are closed. Ur-Ghast normal/tantrum damage admission and actual-loss counters, genuine projectile impact/explosion identities and reload, minion spawning/independent targeting, trap charge/control/damage, native healing, weather/tears, flight and death are closed. The detailed review preserves installed discrepancies, including counter gain on rejected HP damage, fixed closed-head reduction, mortar callback-specific reflection, live custom fireball reloading as vanilla, minion reload health restoration and visualOnly lightning's retained rod/copper callbacks. No fixes or runtime outcomes are claimed.

[Owner review](benchmarks/external-effects-catalog/twilightforest-hydra-urghast-review.md), [semantic section](benchmarks/external-effects-catalog/semantic-sections/twilightforest-hydra-urghast.json), [owner table](benchmarks/external-effects-catalog/twilightforest-owner-table.md), [combined draft](benchmarks/external-effects-catalog/partial-drafts/twilightforest-r2f6-partial.json). [Integrity](benchmarks/external-effects-catalog/twilightforest-hydra-urghast-integrity.json) protects previous research, checks complete declared-method coverage for25 native classes, reproduces the exhaustive four-type caller scan and verifies critical ordering/source/persistence distinctions. [Full validation](benchmarks/external-effects-catalog/r2f6-hydra-urghast-validation.json) covers pinned native/raw/exact-loader evidence, links/classifications, all five tooling tests and research-only baseline boundaries; whitespace is checked before protection.

Both requested bosses are complete; further research waits until this checkpoint is validated and protected. Final self SHA is supplied after commit/push/live remote equality. Exact next task: **Alpha Yeti + Snow Queen semantic review**, reusing existing aids and Ice Bomb evidence. They are unstarted here. The updated user request on2026-09-22 authorizes continuation through R2f7, remaining Twilight content and final promotion while current usage stays healthy, protecting each complete subsection first. The earlier68–80% five-hour stop boundary is superseded. Current weekly usage0%, secondary window unavailable. No runtime boss/L2, Stage/production, balancing, compatibility fixes, Phase6 reopening or Phase7. Ice and Fire can start only after whole Twilight completion/promotion is pushed and verified.


## R2f7 — Alpha Yeti and Snow Queen complete; remaining Twilight content next

R2f6 was pushed/live-verified at `99c3e9e55663347f9ea23042f041d9ad512da7ec`. The continued installed4.8.3345 review adds15 packages/41 delivery cases, preserving every prior subsection and linking existing IceBomb/Frosted packages. Twilight remains PARTIAL with60 draft packages/167 cases and zero promotions. Accepted global116 mechanics/161 paths/217 components remain unchanged.17/40 custom DamageType profiles are now reviewed;23 remain unfinished; REVIEW_REQUIRED0.

Alpha Yeti projectile admission, rampage/tired resources, native slam, mounted throw/fall replacement, ownerless falling ice, terrain and persistence/death are closed. Snow Queen phases, original-request beam counter, geometric multipart shields, contact/melee, hover/drop/ray control, crystal summoning/expiry/melting, terrain and native defenses/death are closed. Shield return values, HP damage, movement and phase counters are kept separate. No runtime result is claimed.

See [complete owner review](benchmarks/external-effects-catalog/twilightforest-yeti-queen-review.md), [semantic evidence](benchmarks/external-effects-catalog/semantic-sections/twilightforest-yeti-queen.json), [integrity](benchmarks/external-effects-catalog/twilightforest-yeti-queen-integrity.json), and [full validation](benchmarks/external-effects-catalog/r2f7-yeti-queen-validation.json). All five tooling tests, installed evidence/reference reproduction, protected-file/catalog/source/delivery checks and research-only boundaries protect this checkpoint.

After commit/push/live equality, continue Task C remaining Twilight combat content while current usage is healthy, protecting logical subsections toward R2f8. Final whole-mod deduplication and catalog promotion come only after semantic closure. IceAndFireCE remains unstarted until full Twilight completion is safely pushed. No runtime boss/L2, Stage/production, balancing/fixes, Phase6 reopening or original Phase7.


## R2f8a — Remaining ranged mobs complete

Continued from pushed/live-verified R2f7 `cb929fb7833eb27ddc3c16126f281cc62247421a`.13 packages/28 cases added; Twilight PARTIAL73/195 with zero promotion.22/40 custom source profiles reviewed;18 unfinished. REVIEW_REQUIRED0; accepted global116 mechanics/161 paths/217 components unchanged.

[The ranged-mob review](benchmarks/external-effects-catalog/twilightforest-ranged-mobs-review.md) closes FireBeetle/WinterWolf breath, HostileWolf/MistWolf behavior, SkeletonDruid/NatureBolt, DeathTome/TomeBolt/lectern, SlimeBeetle/SlimeBlob and stable/unstable ice-core behaviors. Installed implementation distinguishes retaliation target from current target, elemental visuals from real source identity, projectile hit return from secondary status, and delayed explosion from independent terrain conversion.18 complete declared classes and the limited native producers are pinned; existing BaseIceMob/Frosted/boss references remain immutable.

[Integrity](benchmarks/external-effects-catalog/twilightforest-ranged-mobs-integrity.json) and [full validation](benchmarks/external-effects-catalog/r2f8a-ranged-mobs-validation.json) cover all five tooling tests, evidence/reference reproduction, earlier-checkpoint preservation, source/path classification and research-only boundaries. No runtime tests executed.

Next after push/live equality: remaining melee/control mobs/minibosses, then items/armor/charms/scepters/projectiles and hazards/resources, remaining18 source profiles and all mappings/exclusions toward R2f8. Final whole-Twilight promotion follows closure. Continue while current usage healthy. IceAndFireCE remains unstarted; no Stage/production, boss/L2 tests, balancing/fixes, Phase6 reopening or original Phase7.

## R2f8b — Mounted mobs complete

R2f8a was pushed and live-verified at `3b16469cdf2e6b7023ccd8e9da4692a6b683c2ce`. This bounded subsection adds8 reviewed packages /20 cases, bringing Twilight to81/215 drafts and23/40 custom caller profiles. Zero final promotion; REVIEW_REQUIRED0.

[Mounted-mob review](benchmarks/external-effects-catalog/twilightforest-mounted-mobs-review.md) covers goblin pair coupling, shield/armor/HP separation, heavy spear modifier and AI cadence, Pinch Beetle capture versus clamped damage versus boat removal, and ordinary Yeti persistent anger with existing throw/fall reuse. All nine native class surfaces are pinned. [Integrity](benchmarks/external-effects-catalog/twilightforest-mounted-mobs-integrity.json) and [full validation](benchmarks/external-effects-catalog/r2f8b-mounted-mobs-validation.json) preserve prior work and research-only boundaries; five tooling tests required, no runtime tests.

After commit/push/live equality continue BlockChainGoblin/SpikeBlock, GiantMiner/ArmoredGiant and remaining melee content; then items/hazards/resources/remaining17 profiles. Protect each subsection toward R2f8, then final dedup/promotion. Ice and Fire stays blocked until COMPLETE Twilight is protected. Current usage remains healthy; no artificial old five-hour cutoff.

## R2f8c — Chain/spike paths complete

R2f8b was pushed and live-verified at `e391928b3448e67dd4d2d551f5bf58f20e62037c`. This subsection adds7 packages /22 cases: Twilight88/237 drafts,24/40 custom profiles, REVIEW_REQUIRED0, zero promoted.

[Chain review](benchmarks/external-effects-catalog/twilightforest-chain-review.md) separates both SPIKED callers from goblin part mob_attack, shield disruption from HP, launch/return/UUID/durability from damage, and Destruction terrain from its damage modifier. It records independent projectile and native mining-start Player budgets, repeated owner-budget return costs, reload stack identity, exact-loader blocking ability versus animation, and source tags without proposing fixes. [Integrity](benchmarks/external-effects-catalog/twilightforest-chain-integrity.json) / [full validation](benchmarks/external-effects-catalog/r2f8c-chain-validation.json). Eleven class surfaces and recursive mining/tier/immune tags are pinned; five tooling tests required, no runtime tests.

After push/live verification continue giants with native equipment damage and remaining melee mobs, then unreviewed items/hazards/resources and16 unfinished custom profiles. Preserve all protected work. Ice and Fire may begin only after final COMPLETE Twilight promotion is pushed.

## R2f8d — Giants and giant/maze tools complete

R2f8c was pushed and live-verified at `a50efa4b761a3506e248c85165328f140e2259b5`. Four additional packages /16 delivery cases bring Twilight to92/253 drafts,25/40 custom caller profiles, REVIEW_REQUIRED0 and zero promoted.

[Giants/tools review](benchmarks/external-effects-catalog/twilightforest-giants-tools-review.md) proves equipped ANT11/13, Player weapon10/12, ordinary armor15 and separate interaction ranges; it closes GiantPick speed/volume/native break admission/loot state and maze-tool speed/extra durability. Ten class surfaces and limited event/registration/structure producers are pinned. [Integrity](benchmarks/external-effects-catalog/twilightforest-giants-tools-integrity.json) / [full validation](benchmarks/external-effects-catalog/r2f8d-giants-tools-validation.json), with five tooling tests and previous-checkpoint preservation. No runtime or production work.

After push/live equality continue remaining melee/control mobs: spiders/swarm and MosquitoSwarm first, then unfinished humanoids/undead/summons and items/hazards/resources. Fifteen custom profiles remain unfinished. Protect every subsection; full Twilight promotion precedes Ice and Fire.

## R2f8e — spiders, mosquito, crab and borers

R2f8d was committed/pushed/live verified at `f87c0a08b85f49b88c4262d4852066bea8199fe9`. The next bounded subsection adds7 packages/24 cases, taking Twilight to99 reviewed package drafts/277 delivery cases, zero promoted. The custom caller census stays25/40 (15 unfinished), REVIEW_REQUIRED0.

The review separates native Spider goal/rider inheritance, Swarm/Tower melee probability, Mosquito Hunger/food/starvation, Borer pre-hurt scheduling, terrain infestation/discard and three legitimate infested-block release routes. HelmetCrab ordinary combat and its cosmetic variant are assessed exclusions. No fictitious swarm reinforcement path is created: the installed-TF instruction census finds no getReinforcementType caller.

[Full reviewed contracts and source paths](benchmarks/external-effects-catalog/twilightforest-arthropods-review.md). Validation includes evidence/reference reproduction, class/method and semantic guards, five tooling tests, accepted-mod/prior-checkpoint preservation and research-only scope. No runtime boss/L2/Stage/production or Phase6/7 work. Continue remaining melee/control mobs and undead/summon bodies, then remaining items/hazards/callers toward whole-Twilight completion.

## R2f8f — tactical mobs and native TNT/rock paths

R2f8e was committed/pushed/live verified at `ce8cafbf6c2fb8108f8db7cba46eb4a3cc9a12ff`. This subsection adds8 packages/28 cases, taking Twilight to107 package drafts/305 delivery cases. The actual ownerless `thrown_block` caller advances the custom census to26/40;14 remain unfinished. REVIEW_REQUIRED0, zero final Twilight promotion.

[Reviewed contracts](benchmarks/external-effects-catalog/twilightforest-tactical-mobs-review.md) distinguish Redcap TNT planning from ordinary native blast/ownership, Kobold bread targeting from retaliation and panic/flock control, and Troll carried/thrown projectiles from their ownerless damage source. Boggard has no registered native producer and contributes no legitimate delivery. Native reload quirks and ignored hurt returns are preserved, not repaired.

Evidence/reference reproduction, all19 class surfaces, semantic/caller guards, five tooling tests, prior-checkpoint/four accepted-mod preservation and research-only scope checks protect this checkpoint. Continue remaining mobs and producer status, then unfinished items/scepters/armor/charms/hazards/resources/custom callers before final Twilight promotion. IceAndFire only after Twilight COMPLETE is safely pushed; no runtime boss/L2/Stage/production/Phase6/7 work.

## R2f8g — constructs, slime inheritance and guardian equipment

R2f8f was committed/pushed/live verified at `ac50a160beb2abdf1524aa1ebee824a46a354891`. This subsection adds5 packages/21 cases, taking Twilight to112 package drafts/326 delivery cases. Custom census remains26/40,14 unfinished, REVIEW_REQUIRED0; zero Twilight promotions and unchanged four accepted mods.

[Reviewed contracts](benchmarks/external-effects-catalog/twilightforest-constructs-slimes-review.md) close CarminiteGolem successful-hit launch, native MazeSlime size/contact/split/load ordering, SnowGuardian's actual three-slot loadouts and inherited behavior, and registered Adherent delivery. HarbingerCube has no native attack goal/callback and is excluded rather than assigned a fabricated attack. All6 class surfaces, actual producer/equipment references and native raw/exact-loader inheritance are pinned.

[Integrity](benchmarks/external-effects-catalog/twilightforest-constructs-slimes-integrity.json) and [full validation](benchmarks/external-effects-catalog/r2f8g-constructs-slimes-validation.json) cover evidence/reference reproduction, semantic/source/path checks, all five tooling tests, accepted-mod/prior-checkpoint preservation and research-only boundaries. No runtime tests.

Continue Wraith/Minotaur remaining bodies and RisingZombie/LoyalZombie/ZombieWand producers/resources, then remaining utility/entities/items/hazards/callers toward R2f8 and final Twilight promotion. Current usage remains healthy; IceAndFire only after protected whole-Twilight completion. No L2/Stage/production/Phase6/7 work.

## R2f8h — remaining Wraith/Minotaur bodies and Rising Zombie

R2f8g was committed/pushed/live verified at `8795e3ad0def055395914c77ab7da9ae4d95060a`. Four additional packages/twenty delivery cases bring Twilight to116 reviewed package drafts/346 cases. Custom caller census26/40,14 unfinished, REVIEW_REQUIRED0, zero promotion; the four accepted mod totals remain unchanged.

[Reviewed contracts](benchmarks/external-effects-catalog/twilightforest-restless-mobs-review.md) close Wraith flight/home/cadence and native retaliation, Minotaur actual equipment/charge differences, and RisingZombie gaze/conversion/admission. Existing HAUNT/AXING/helper/sprint/charge semantics are linked, not duplicated. Nine native class bodies and actual world producers are pinned. [Integrity](benchmarks/external-effects-catalog/twilightforest-restless-mobs-integrity.json) and [full validation](benchmarks/external-effects-catalog/r2f8h-restless-mobs-validation.json) cover all five tooling tests, evidence/reference reproduction, protected source/path links and prior-checkpoint/scope preservation.

Continue LoyalZombie/ZombieWand ownership, targeting, feed/Strength/expiry and shared recharge resources; then remaining utility/entities/items/hazards/custom sources before final Twilight promotion. No runtime boss/L2/Stage/production/Phase6/7 work. IceAndFire stays unstarted until COMPLETE Twilight is pushed and verified.

## R2f8i — Loyal Zombie and native scepter resources

R2f8h was pushed/live verified at `696eb25903f23324bbedb90116fd7a41a395dd20`. Nine packages/28 cases add up to125 Twilight draft packages/374 cases. EXPIRED is USED through its actual LoyalZombie caller:27/40 custom types reviewed,13 unfinished. REVIEW_REQUIRED0; zero promotions and unchanged four accepted mods.

[Reviewed contracts](benchmarks/external-effects-catalog/twilightforest-summon-resources-review.md) cover real summon ownership, fixed melee, Strength expiry/feed, targeting/follow, Crown baby state, nonbreaking durability, Renewal and manual repair. Manual potion item-ID matching differs from Renewal component testing; the native behavior is documented without fixes. Other scepter unique effects remain explicitly pending.

[Integrity](benchmarks/external-effects-catalog/twilightforest-summon-resources-integrity.json) and [full validation](benchmarks/external-effects-catalog/r2f8i-summon-resources-validation.json) protect all five tooling tests, native/raw/exact-loader evidence, caller/tag/recipe/source/path checks and prior accepted work/research-only boundaries. No runtime work.

Continue Fortification/Lifedrain unique payloads, then remaining Twilight entities/items/hazards/custom sources toward R2f8 and final promotion. IceAndFire only after COMPLETE Twilight is pushed/verified; no L2/Stage/production/Phase6/7 work.

## R2f8j — Fortification and Lifedrain native payloads

R2f8i was pushed/live verified at `5f56f39696e7c17c4eccd8314f3953ef14578aeb`. Seven reviewed packages/26 delivery cases bring Twilight to **132 package drafts/400 cases**. LIFEDRAIN is USED through its real caller: **28/40** custom profiles reviewed,12 unfinished. REVIEW_REQUIRED0; zero Twilight promotions and unchanged four accepted mods.

The review separates Fortification count/timer/persistence from its binary incoming-event cancellation, and Lifedrain selection/source damage from low-health execution, admitted restoration, independent motion and Crown charge saving. The nonPlayer native die/discard branch is documented separately from the Player second hurt request; no compatibility implementation or balancing change is made. Protected Lich shields, Twilight bolt and shared scepter resources remain unchanged.

[Contracts](benchmarks/external-effects-catalog/twilightforest-scepter-payloads-review.md), [packages and paths](benchmarks/external-effects-catalog/semantic-sections/twilightforest-scepter-payloads.json), [integrity](benchmarks/external-effects-catalog/twilightforest-scepter-payloads-integrity.json), [validation](benchmarks/external-effects-catalog/r2f8j-scepter-payloads-validation.json). Five full native class surfaces, all-TF actual caller scan, raw Minecraft/exact244 comparison and semantic/source/path/prior-checkpoint checks protect this subsection with all five tooling tests.

Next: remaining player projectile/utility weapons (Moonworm Queen, Cube of Annihilation, Ender/Seeker/Triple bows, Peacock Fan), then armor/charms/food, utility/passive entities, hazards/custom sources and exact nested ASM/compatibility closure before final Twilight promotion. No runtime boss/L2/Stage/production/Phase6/7; IceAndFire only after Twilight COMPLETE is pushed and verified.
