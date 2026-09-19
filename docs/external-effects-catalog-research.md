# External combat effects catalog — separate research track

**Status: PARTIAL overall; R2e completes Friends & Foes. Variants & Ventures, Cult of Azazel and Royal Variations remain protected COMPLETE. Twilight Forest is UNSTARTED.** Phase 6 is complete and closed. This track does not reopen, supersede, recalibrate or change Phase 6, its Stage behavior, accepted family integrations, or production combat. Original Phase 7 is not started by this research.

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
