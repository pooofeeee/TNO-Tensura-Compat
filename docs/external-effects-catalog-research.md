# External combat effects catalog — separate research track

**Status: PARTIAL overall; Twilight Forest static combat review COMPLETE at R2f-final: 219 distinct mechanics / 640 delivery paths, 40/40 custom DamageTypes USED, 0 REVIEW_REQUIRED/native ambiguities. Five accepted external mod reviews are COMPLETE.** Phase 6/production remain closed; original Phase 7 has not started.

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

## R2f8k — Moonworm Queen and Cube of Annihilation

R2f8j was pushed/live verified at `e5c8d8929aca86db5c3d0f9a7925cd662714fab1`. Seven packages/26 delivery cases bring Twilight to **139 package drafts/426 cases**. The actual MOONWORM caller advances the custom census to **29/40**,11 unfinished. REVIEW_REQUIRED0, zero Twilight promotion; four accepted mods unchanged.

Native Queen release/dispenser/direct placement have different success and durability gates. Moonworm bare-head equipment is separate from random zero/one damage and independent failure loot. Cube uses owner melee sources for fixed10, has native shield-disable delivery but no shield-block ability, and removes terrain only after event/tag/resistance/adventure admission. Its per-stack UUID, steering, return, save and null-stack boundaries are preserved. Cube has a registered native item path; no survival recipe/loot acquisition is inferred from its WIP name.

[Contracts](benchmarks/external-effects-catalog/twilightforest-utility-projectiles-review.md), [packages and paths](benchmarks/external-effects-catalog/semantic-sections/twilightforest-utility-projectiles.json), [integrity](benchmarks/external-effects-catalog/twilightforest-utility-projectiles-integrity.json), [validation](benchmarks/external-effects-catalog/r2f8k-utility-projectiles-validation.json). Ten full native class surfaces, actual instruction/data census, raw/exact244 reference chains, semantic/source/path/preservation checks and all five tooling tests protect this subsection. No runtime work or fixes.

Next: Ender/Seeker/Triple bows and Peacock Fan, then armor/charms/food, utility/passive entities, hazards/11 unfinished types and nested ASM/compatibility closure before whole-Twilight promotion. IceAndFire only after COMPLETE Twilight pushed/live verified. No boss/L2/Stage/production/Phase6/7 work.

## R2f8l — Ender/Seeker/Triple bows and Peacock Fan

R2f8k was pushed/live verified at `3cc6c3220519ccea8ae88db90a90fa0ae20633b6`. Eight packages/26 delivery cases bring Twilight to **147 package drafts/452 cases**. Custom census remains **29/40**,11 unfinished; REVIEW_REQUIRED0, zero promotion, unchanged four accepted mods.

Ender swap occurs in the native impact event before HP damage. Seeker uses priority-based steering and a real unsaved parent-arrow effect delegate; reflected HP and delegated-effect ownership can differ. Triple Bow emits three native arrows per Player draw entry and conditionally clears target cooldown in LivingDamageEvent.Post when its Player cause currently holds Triple in the remembered used hand. Early rejected hits cannot reach that reset; admitted zero-HP Post can. Triple wears before construction; an actual final-durability break reaches the native empty-weapon rejection. Native skeletons use customArrow instead of Triple's volley method. Peacock Fan separates client boost, server velocity replacement, client Player push, fall-context marker, terrain and Living-only dispenser behavior; its conditional cooldown reads the previous use item. These installed contracts are preserved without fixes.

[Contracts](benchmarks/external-effects-catalog/twilightforest-bows-fan-review.md), [packages and paths](benchmarks/external-effects-catalog/semantic-sections/twilightforest-bows-fan.json), [integrity](benchmarks/external-effects-catalog/twilightforest-bows-fan-integrity.json), [validation](benchmarks/external-effects-catalog/r2f8l-bows-fan-validation.json). Eight full native class surfaces, actual caller census, raw/exact244 inheritance, semantic/source/path/preservation checks and all five tooling tests protect this subsection. No runtime tests.

Next: remaining armor/charms/food and utility resources, utility/passive entities, hazards/11 unfinished types and nested ASM/mixin/event/compatibility closure before final Twilight promotion. IceAndFire only after COMPLETE Twilight pushed/live verified; no boss/L2/Stage/production/Phase6/7 work.

## R2f8m — Conventional equipment, Fiery/Glass and Stale source routing

Protected input R2f8l `9588519010ff6b717f8921e8d447f3342dc34aa4`. Adds **8 reviewed mechanic packages / 24 delivery cases**, bringing Twilight to **155 package drafts / 476 delivery cases**, still PARTIAL with zero promotions and REVIEW_REQUIRED0. **30/40 custom DamageTypes** now have reviewed actual callers; `stale_sandwich` is newly USED, ten remain unfinished.

Fiery Incoming ignition, successful Player melee ignition and armor Post retaliation are separate native paths. Glass custom shatter and inherited wear are independent, while the actual infinite lore variant carries both required protection components. The installed nested ASM service/transformer proves Stale Bread replaces real mobAttack/playerAttack factory results and also applies to the existing Cube owner factory path. It does not change attack amounts or target eligibility. Knightmetal Shield retains native shield/parry contracts; conventional attributes, recipe enchantments, Arctic snow/freeze and crown HEAD armor are saved with native references.

See the equipment semantic section, caller scan, nested archive/service witnesses, integrity and full-validation report. Previous accepted116/161/217 catalog bodies are unchanged. No runtime boss/L2/Stage/production/fixes/Phase6/7 work.

Next: Charms of Life/Keeping, Phantom retention and Keepsake Casket death/respawn paths; then Travellers modifiers, remaining utilities/food/passive entities/hazards, ten custom DamageTypes and full nested ASM/compatibility closure. IceAndFire only after complete Twilight is pushed and live verified.

## R2f8n — Charms, Phantom retention and Keepsake Caskets

Protected input R2f8m `7449fff57d659e0bfd004e6fd5c9f4b1c78a5eaf`. Adds **8 reviewed packages / 30 delivery cases**, bringing Twilight to **163 package drafts / 506 delivery cases**, still PARTIAL with zero promotions and REVIEW_REQUIRED0. DamageType coverage remains **30/40**, ten unfinished.

Life charms act at the native death event, with exact health writes and effect payloads distinct from the earlier Totem path. Keeping tiers, independent Phantom/TowerKey retention, persisted respawn slots, casket reservation/placement/storage and repair/access rules are recorded. The real KeepingI varargs call creates an empty list, so it does not retain the selected main slot. Native casket opening uses owner-or-operator, while breaking a nonempty owned casket requires owner-and-operator. Full-inventory return loss and pre-placement consumption remain unchanged source-proven behavior.

Selected installed Curios9.5.1 methods close Twilight's real accessory consumption/drop/clone dependency, including active versus cosmetic slots, identity overrides, persisted token behavior and same-tick cached-reference boundaries. This is not a new family review or a runtime compatibility test. CharmEffect and animation packets are visual exclusions.

See the charms semantic section, caller scan, native and selected dependency witnesses, integrity and full-validation report. Accepted116/161/217 catalog bodies remain unchanged; runtime boss/L2/Stage/production/fixes/Phase6/7 remain untouched.

Next: Travellers gear/modifiers and their actual ASM/event control paths; then remaining utility/food/passive entities/hazards, ten custom DamageTypes and whole-mod ASM/compatibility/source closure before final Twilight promotion. IceAndFire only after complete Twilight is pushed and live verified.

## R2f8o — Travellers core modifiers and equipment state

Protected input R2f8n `bf7b2fc69d8adab76096b99f49850a3d52206861`, rechecked by fetch/live equality after the latest continuation request. Adds **11 reviewed packages / 38 delivery cases**, bringing Twilight to **174 mechanic drafts / 544 delivery cases**, still PARTIAL, zero promoted, REVIEW_REQUIRED0. DamageTypes remain **30/40**, ten unfinished.

[Reviewed contracts](benchmarks/external-effects-catalog/twilightforest-travellers-core-review.md) close registry/components and activation, genuine modifier recipes/transfer/removal, base equipment attributes, last-durability wear and stored attributes, Auto-Repair, Perfect Dodge, Arrow Magnetism, All-Night, Stealth, Haste, Aquatic Agility and Efficient Eater. Nineteen declared class bodies and selected event/loader/native dependencies are pinned. The actual nested ASM transformer restricts Efficient Eater to movement statistics and jumping.

Native common components and constructor ordering prove Gloves/Belt have empty armor attributes despite their material values. Broken gear can retain removed Aquatic attributes in its separate saved component; native grindstone removal followed by material repair restores those entries without the modifier marker. Both are recorded source behavior without production changes. Arrow recovery discards without canceling its block-impact event; Perfect Dodge instead vetoes the native impact before damage. Piglin/snow item predicates are independent of the broken-modifier gate.

[Integrity](benchmarks/external-effects-catalog/twilightforest-travellers-core-integrity.json) and [full validation](benchmarks/external-effects-catalog/r2f8o-travellers-core-validation.json) cover native/reference reproduction, semantic guards, source/path links, all five tooling tests, previous-checkpoint/accepted-mod preservation and research-only boundaries. Runtime0; Stage/production/Phase6/7 untouched.

Next: Travellers movement/control and exact installed ASM/packets, then belt/display/zoom and Emperor cloth. Continue remaining utility/food/passive entities/hazards, ten custom DamageTypes and complete ASM/compatibility/source exclusions before R2f8 and final Twilight promotion. Protect each complete subsection and continue while actual usage permits. IceAndFire only after Twilight COMPLETE is pushed and live-verified.

## R2f8p — Travellers movement, native physics and packet state

Protected input R2f8o `3462e60868bb8877855ae2a441379c61a322a90c`, fetched and live-verified with a clean working tree. Adds **11 reviewed packages / 40 delivery cases**: Twilight now has **185 mechanic drafts / 584 delivery cases**, still PARTIAL, zero promoted, REVIEW_REQUIRED0. DamageTypes remain **30/40**, ten unfinished.

[Reviewed contracts](benchmarks/external-effects-catalog/twilightforest-travellers-movement-review.md) close Water Walk, Unrestrained, Swift Swim, High Step, High Jump, Slimy Soles, Gradual Glide, Double Jump, Sidestep, Straight Ahead and Agile Ranger. Nine complete declared logic/state/packet classes and eight installed movement transformers are pinned against raw Minecraft and exact NeoForge21.1.244 references. Genuine surface collision, fall cancellation, attribute/effect inputs, motion changes, input ordering and packet/resource state stay separate.

Water Walk still requires native exposed source-fluid collision admission. Slimy Soles cancels an eligible fall event, then consumes stored bounce without a fresh gear check; its decode constructor omits the encoded double-jump boost field. Double Jump consumes stored availability, calls native jump and adds its separate safe-fall modifier; the helper does not recheck current gear or require a successful vertical impulse. Sidestep uses a strict >40-tick cooldown and adds motion. Straight Ahead has different client direction and server presence gates. Glide physics retains current gear eligibility even though the state packet does not check sender/target UUID equality. These are static native findings; no fixes or runtime tests were made.

[Integrity](benchmarks/external-effects-catalog/twilightforest-travellers-movement-integrity.json) and [full validation](benchmarks/external-effects-catalog/r2f8p-travellers-movement-validation.json) cover evidence reproduction, semantic/source/path checks, five tooling tests and previous-checkpoint preservation. Accepted116/161/217 catalog bodies remain unchanged. Runtime0; Stage/production/Phase6/7 untouched.

Next: Travellers belt/hotbar/item-display/zoom/red-thread and Emperor cloth/render hooks, then remaining utilities/food/passive entities/hazards, ten custom DamageTypes, all remaining ASM/compatibility/source exclusions, R2f8 and final Twilight promotion. Leash pathfinder ASM is a separate unfinished structure mechanic. Continue automatically while current usage allows; IceAndFire only after Twilight COMPLETE is pushed and live-verified.

## R2f8q — Travellers storage/view and Emperor cloth

Protected input R2f8p `0ed32df8aa5e3dad148f742d25492f90fab4323a`. Adds **5 reviewed packages / 29 delivery cases**, reaching **190 mechanic drafts / 613 delivery cases**, PARTIAL, zero promoted, REVIEW_REQUIRED0. Custom DamageTypes remain **30/40**, ten unfinished. Travellers core, movement and remaining storage/view contracts are now reviewed together; other Twilight content remains unfinished.

[Reviewed contracts](benchmarks/external-effects-catalog/twilightforest-travellers-utility-review.md) close Belt/Wings hotbar storage, Item Display and genuine map callbacks, Goggles zoom/mouse state, Red Thread visibility and Emperor cloth. Four exact installed nested armor/map transformers are pinned with native/NeoForge references. Inactive belt gear can retrieve into empty hotbar slots. Map tracking's two injected inventory checks both use the original method Player argument. Zoom FOV requires active gear, while the mouse-sensitivity handler only checks the component/key and retains its native zero-sensitivity nonfinite boundary.

Cloth changes armor's contribution only inside native Invisibility visibility calculation, preserves armor/enchantment/flight behavior, and retains ordinary targeting limits. Exact humanoid/cape render targets were verified here. The original separate-Elytra conclusion is superseded by the explicit R2f8t erratum below: an additional registered transformer suppresses clothed Elytra wing rendering. Storage, view, rendering and native detection remain distinct. Item Display codec/cycle behavior, genuine insertion/removal/overflow, red-thread local toggle/death-copy limits and administrative modifier source differences are saved without executing commands or making fixes.

[Integrity](benchmarks/external-effects-catalog/twilightforest-travellers-utility-integrity.json) and [full validation](benchmarks/external-effects-catalog/r2f8q-travellers-utility-validation.json) cover source/reference reproduction, full declared class coverage, native anchors, semantic/path checks, five tooling tests, protected checkpoint and accepted116/161/217 preservation. Runtime0; no L2/Stage/production/Phase6/7 changes.

Next: remaining utility/map/food/flask and passive-entity contracts, environmental hazards and all ten unfinished custom DamageTypes, then complete the remaining installed ASM/compatibility/source exclusions. Protect R2f8, deduplicate and promote full Twilight COMPLETE, push/live verify, then begin IceAndFire only while actual usage remains healthy.

## R2f8r — Food, flasks and native consumption payloads

Protected input R2f8q `723f5d70964592ece674c7ab3d93e71e8f3fe69b`, clean and fetched/live-verified. Adds **12 reviewed packages / 33 delivery cases**, reaching **202 mechanic drafts / 646 delivery cases**, PARTIAL, zero promoted, REVIEW_REQUIRED0. **FAILED_CHALLENGE is USED**, bringing custom DamageType coverage to **31/40**, nine unfinished.

[Reviewed contracts](benchmarks/external-effects-catalog/twilightforest-food-flasks-review.md) close native food parameters/effects, custom berry duration extension, Brittle/Greater filling/doses/breakage/persistence, real instant/noninstant potion delivery, Experiment115 portion regeneration and Essence Berry native XP orbs. Fourteen complete declared classes plus actual registration/event/resource and native/NeoForge comparisons are pinned. Food resource, later regeneration, status damage and direct flask requests stay separate.

Strong Harming normally requests ownerless `failed_challenge`12; its exact predicate is `(isHarm != invertedHealAndHarm) && amplifier>0`, before the instantaneous-effect check. Consequently a legitimately inverted Player also diverts amplified non-HARM effects. No such Player eligibility is fabricated. The source has no native tag memberships or source position; ordinary mitigation applies, but native directional shield has no position to block. Hurt success does not control remaining effects or dose costs. Ordinary HarmingI uses native self-attributed indirect magic instead. Genuine component-bearing splash/lingering/tipped-arrow donors are admitted by the real flask handlers.

Berry extension requests existing duration plus ticks at amplifier0 and retains native merge/eligibility. Exact244 Poison uses `neoforge:poison` with vanilla magic fallback. Eating Experiment115's final portion removes even its regenerating block. Essence Berry creates a real6..19 XP orb whose native pickup/repair can belong to another player. These findings are static source contracts, with no runtime tests or fixes.

[Integrity](benchmarks/external-effects-catalog/twilightforest-food-flasks-integrity.json) and [full validation](benchmarks/external-effects-catalog/r2f8r-food-flasks-validation.json) cover evidence/reference reproduction, native predicate/order/return guards, class/source/path checks, five tooling tests and prior-checkpoint/accepted116/161/217 preservation. Runtime0; production/Stage/Phase6/7 untouched.

Next: remaining utility/map items (Pocket Watch, transformation/terrain tools and native map/landmark ASM), then passive entities, hazards and nine unfinished custom DamageTypes. Finish remaining ASM/compatibility/source exclusions, protect R2f8 and promote Twilight COMPLETE before IceAndFire. Continue after push/live equality while actual usage permits.

## R2f8s — Active utilities and legitimate native alternatives

Protected input R2f8r `a5aed2439d588673357293c434d83570377bf21f`. Adds **7 reviewed packages / 27 delivery cases**, reaching **209 mechanic drafts / 673 delivery cases**, PARTIAL, zero promoted, REVIEW_REQUIRED0. DamageTypes remain **31/40**, nine unfinished.

[Reviewed contracts](benchmarks/external-effects-catalog/twilightforest-active-utilities-review.md) close Pocket Watch effects/application veto, Transformation Powder replacement, Crumble Horn terrain alteration, Ore Magnet/Mining Core relocation and Lamp of Cinders terrain/ignition. Fourteen complete declared classes plus exact native/NeoForge comparisons are pinned. All32 transformation mappings and63 crumble entries retain their actual source data. Existing ToolEvents contracts are reused and the remaining declared methods now closed.

Pocket Watch prevents new eligible Mining Fatigue applications while held; it does not cleanse an existing effect. Powder conversion reloads saved state and directly resets destination HP to the resulting maximum, retaining native conversion events and a new UUID. Ordinary Mob hand/armor stacks can be emptied by native transfer before old-state serialization overwrites destination equipment; surviving BODY/subtype entries remain conditional. The dispenser iterates all eligible front-box entities without a remaining-stack recheck. No conversion or HP operations were executed by this research.

Handheld Horn uses remaining-time modulo and an inclusive125-position box with probability/Player BreakEvent/harvest rules. Its dispenser has distinct deterministic admission. The posted BreakEvent can also invoke the already-protected mainhand maze-tool wear rule before a Horn roll. Ore Magnet and Mining Core share actual dynamic tag caches and24-block exact-state vein traversal. Lamp uses a release durability reserve without spending durability, and its separate Player-only activation ignites nearby nonplayers through native fire ticks; thorn conversion and HP damage are not conflated.

[Integrity](benchmarks/external-effects-catalog/twilightforest-active-utilities-integrity.json) and [full validation](benchmarks/external-effects-catalog/r2f8s-active-utilities-validation.json) cover source/reference reproduction, native predicates/order/return checks, full declared coverage, all five tooling tests, prior-checkpoint preservation and unchanged accepted116/161/217 catalog bodies. Runtime0; no L2/Stage/production/Phase6/7 changes.

Next: Magic/Maze maps, Ore Meter and landmark ASM; remaining structural utilities (Rope, Magic Beans and other magic cores), passive entities, hazards and nine custom DamageTypes. Finish all remaining ASM/compatibility/source exclusions, protect R2f8 and promote full Twilight COMPLETE before IceAndFire. Continue after push/live equality while actual usage is healthy.

## R2f8t — Maps, Ore Meter and installed map/render ASM

Protected input R2f8s `e63af59ef4558422a3036d617381645c0e4ff160`, pushed/live-verified with a clean tree. Adds **4 reviewed packages / 28 delivery cases**, reaching **213 mechanic drafts / 701 delivery cases**, PARTIAL, zero promoted, REVIEW_REQUIRED0. DamageTypes remain **31/40**, nine unfinished.

[Reviewed contracts](benchmarks/external-effects-catalog/twilightforest-maps-information-review.md) close Magic/Maze/Ore map creation, lookup, fixed sampling, storage, packets, copying and genuine inventory/Goggles delivery; Ore Meter activation, scan geometry, persistence, filtering and clearing; and native landmark locator integration. Twenty-five complete declared TF classes plus relevant native/NeoForge comparison and two registered transformers are pinned. These information mechanics do not damage targets or change boss progression.

The landmark transformer intercepts only the last of three native returns. Its TF result replaces the original without comparing their distances; earlier returns bypass the hook. Native command, configured exploration-map loot and configured treasure-map trade paths retain their own admission. Maze map vertical distance changes the player marker without vetoing map updates. Native cartography slots reject TF map item identities, while custom copying shares the original saved map ID. OreMeter normal horizontal spans are15/47/79; its volume uses maximum build height rather than total height. Clearing results/filter does not cancel an ongoing scan.

**R2f8q correction:** the separate registered `CancelElytraRenderingTransformer` targets exact NeoForge `ElytraLayer.shouldRender` and inserts the cloth hook before every boolean return. Cloth does suppress native Elytra wing rendering. The prior conclusion used only the untransformed method and was incomplete. Historical Q files/evidence remain unchanged; the new accumulated draft applies a counted, source-linked erratum to the existing cloth package and two paths. Armor, enchantments, durability, cape eligibility and native flight conclusions remain unchanged.

[Integrity](benchmarks/external-effects-catalog/twilightforest-maps-information-integrity.json) and [full validation](benchmarks/external-effects-catalog/r2f8t-maps-information-validation.json) cover exact source/reference reproduction, predicate/return guards, explicit erratum locations, five tooling tests, protected-file preservation and unchanged accepted116/161/217 catalog bodies. Runtime0; no L2/Stage/production/Phase6/7 changes.

Next: structural utilities (Rope, Magic Beans and remaining magic cores/callbacks), passive entities, hazards and nine custom DamageTypes; complete remaining ASM/compatibility/source exclusions, protect R2f8 and promote Twilight COMPLETE. Begin IceAndFire only after that promotion is pushed/live-verified. Continue automatically while current enforced usage allows.

## R2f8u — Structural utilities and remaining magic cores

Protected input R2f8t `45e1866125b36a5a4bfa1d0b26190043abd3da66`, pushed/live-verified clean. Adds **6 reviewed packages / 28 delivery cases**, reaching **219 mechanic drafts / 729 delivery cases**, PARTIAL, zero promoted, REVIEW_REQUIRED0. DamageTypes remain **31/40**, nine unfinished; all nine actual caller locations are identified for the hazard review.

[Reviewed contracts](benchmarks/external-effects-catalog/twilightforest-structural-utilities-review.md) close Rope placement/support/native climb and platform behavior, Magic Beans/grower terrain, Uberous Soil growth/displacement, and Time/Transformation/Sorting cores. Sixteen full declared TF classes, actual producers, configuration/resources and raw/native NeoForge references are pinned. Protected MiningCore is reused. No production behavior changed.

Genuine item delivery retains native placement events and creative count restoration. Beans starts terrain growth at callback102, advances on even callbacks and stops a layer after15 counted obstructions. Its manual advancement guard is ineffective for an ordinary present holder, but native item-use criteria still run. Soil queues15 genuine FakePlayer bone meal calls; its separate Mushgloom route invokes native growth with BlockGrowFeature and feature admission intact. Rope uses the native climbable/scaffolding path, with distinct horizontal platform collision and scheduled axis-support removal.

Timewood samples480 positions per20-tick core callback and invokes actual random/typed block-entity callbacks; it is not a universal24x multiplier. Transformation retains the fixed distance256 gate and exact quart-height expression. Sorting uses real sided block/entity capabilities, extracts before simulating destination insertion, and ignores the final insertion remainder. Its position/side cache does not include a dimension, while the underlying loader cache retains the initial level. These source contracts are saved with future controls; no loss, world change or combat test was executed.

[Integrity](benchmarks/external-effects-catalog/twilightforest-structural-utilities-integrity.json) and [full validation](benchmarks/external-effects-catalog/r2f8u-structural-utilities-validation.json) cover evidence reproduction, native predicate/order/return checks, full declared coverage, all five tooling tests, protected-file and accepted116/161/217 preservation, and research-only boundaries. R2f8t's explicit cloth erratum remains carried forward.

Next: remaining passive entities and nine hazard types (`thorns`, `oreberry`, `knightmetal`, `fiery`, `fire_jet`, `reactor`, `slider`, `ominous_fire`, `acid_rain`), all legitimate callers and other combat-significant structures/callbacks. Complete remaining ASM/compatibility/source exclusions, protect R2f8, promote Twilight COMPLETE, push/live verify, then IceAndFire. Continue while actual usage allows. No runtime/L2/Stage/production/Phase6/7.

## R2f8v — TWILIGHT_PASSIVE_ENTITIES_SEMANTIC_REVIEW_COMPLETE

Continues protected R2f8u `33c70323b3cd409c57873d78822011cab91c046d`; local/live equality verified before proceeding. Adds four packages and 21 native delivery paths: Quest Ram collection/reward, Deer Senbei healing, bird movement/contact control and native passive immunities. All nine concrete passive classes have a disposition; ordinary wildlife/variant details are explicit exclusions.

Hand-fed Quest Ram costs one item; its native dropped-item goal discards the entire accepted item entity. Reward/home/progress predicates, current quest reload and saved color/reward state are separate. Deer healing uses native heal(4), including parent feeding callbacks; the protected player-food nutrition package is unchanged. TinyBird held-seed spooking is a positive predicate. Trigger suppression does not skip generic entityInside hazards.

[Reviewed contracts](benchmarks/external-effects-catalog/twilightforest-passive-entities-review.md), [source integrity](benchmarks/external-effects-catalog/twilightforest-passive-entities-integrity.json), [full validation](benchmarks/external-effects-catalog/r2f8v-passive-entities-validation.json). Four accepted mods retain 116 mechanics / 161 paths / 217 components. Twilight PARTIAL, zero promoted, REVIEW_REQUIRED 0, runtime 0.

Exact next task: remaining environmental hazards and all nine unfinished custom DamageTypes, then other combat-significant structures/callbacks, nested ASM, compatibility and source closure; protect R2f8 and final Twilight COMPLETE before IceAndFire.

## R2f8w - TWILIGHT_CONTACT_HAZARDS_SEMANTIC_REVIEW_COMPLETE

Continues protected R2f8v `a4979735e3ac9ca501a8e3f6a4193b3fb6258eb2`, verified local/live. Adds seven packages / 32 delivery cases: four ownerless contact sources, independent thorn regrowth/Burnt removal, bush growth/harvest/snow state and Fiery native environmental utility.

Thorns4, Oreberry1, Knightmetal4 and Fiery1 are requests through native hurt. None bypasses armor, Resistance, protection or cooldown; null source position fails the ordinary directional shield test. Knightmetal lacks NO_KNOCKBACK and can cause native randomized knockback. Fiery checks exact boots/fire immunity, does not ignite, and retains the protected admitted-fire Frosted callback. Burnt Thorns remove themselves without a hurt call; Oreberries do not inherit vanilla sweet-berry slow/motion predicates. Fiery fire support and Strider warmth remain separate from its damage.

[Reviewed contracts](benchmarks/external-effects-catalog/twilightforest-contact-hazards-review.md), [source integrity](benchmarks/external-effects-catalog/twilightforest-contact-hazards-integrity.json), [full validation](benchmarks/external-effects-catalog/r2f8w-contact-hazards-validation.json).35/40 custom types now USED; remaining: fire_jet, reactor, slider, ominous_fire, acid_rain. REVIEW_REQUIRED0, runtime0, Twilight zero promoted; accepted116/161/217 unchanged.

Exact next: FireJet/Reactor/Slider, then Ominous Fire conversion and Acid Rain/progression; other structures/callbacks, nested ASM, compatibility and exclusions before R2f8 and final Twilight COMPLETE. IceAndFire has not started.

## R2f8x — mechanical hazards protected subsection

Continues the verified R2f8w contact checkpoint `724e0e768885a4603477b96832271326d6712ffc`. Adds eight packages and 33 legitimate delivery cases: Fire Jet pulses and independent fire timer, Reactor terrain sequence/native explosion/default Ghastling production, transient Debris collision, and stationary/moving Slider damage/control/restoration. [Full contracts and source evidence](benchmarks/external-effects-catalog/twilightforest-mechanical-hazards-review.md).

Fire Jet has13 pulse opportunities across61 flame callbacks, including counter reset0; hurt rejection does not gate the300 fire-tick assignment. Reactor keeps its custom ownerless magic/environment source even inside the engine explosion, whose movement and later six Ghastling attempts do not depend on HP damage. Slider uses ownerless5 damage then independent native knockback2; the apparent.98 Vec3 damping result is discarded. No behavior is changed.

Validation for this checkpoint: exact installed evidence/reference integrity, mechanical source/ordering guards, all five tooling tests, previous accepted records and protected draft preservation, duplicate/source/delivery/classification/registry checks, research-only scope and staged diff check. Static runtime tests remain0. Twilight238/815 drafts,38/40 types, REVIEW_REQUIRED0, zero promoted; accepted four mods116/161/217 unchanged.

Exact next task: Ominous Fire damage/conversion and Acid Rain/progression to close the last two types; then remaining structures/events/nested ASM/compatibility/source exclusions, R2f8 closure and final Twilight COMPLETE promotion. Only after pushed/live-verified COMPLETE may IceAndFire start. Continue automatically while actual current usage remains healthy.

## R2f8y — Ominous Fire, biome enforcement and DamageType closure

Continues protected mechanical research `2c9c1157531d499945ec9551196e612cd3831d4a` plus its published integrity report at live-verified `3c40f7c261350d75dca3e22e018ddd2162d2d433`. Adds9 packages /33 paths: Ominous contact, mapped death conversion, player-profile Zombie creation and native incoming-source re-entry, Acid Rain, native Darkness/Hunger/ignition biome consumers, and distinct Essence crafting repair. [Full reviewed contracts](benchmarks/external-effects-catalog/twilightforest-ominous-progression-review.md).

[The machine-readable40-type closure](benchmarks/external-effects-catalog/twilightforest-r2f8y-damage-type-closure.json) maps every installed custom declaration to exactly one USED native semantic profile. No missing/duplicate profile and no declared-without-caller disposition. This closes DamageTypes, not the whole mod. Twilight247/848 drafts; REVIEW_REQUIRED0; zero promoted; accepted four mods116/161/217 unchanged; runtime0.

Ominous contact is armor/shield-bypassing magic, not IS_FIRE: no parent ignition or fire immunity is inferred. Exact-key uncanceled death drives three mapped replacements or a profile-bearing native Zombie. Zombie spawn finalization can overwrite earlier adult/loot setters. Its incoming wrapper cancels the original hit, retries native hurt, preserves DamageType, swaps direct/causing constructor arguments (same Zombie on real melee), and can repeat Player difficulty scaling while outer success-only attacker callbacks are skipped. Acid Rain actually arrives through a20tick outer player callback, with no weather/sky gate; only its sound requires truehurt.

Validation: source/return/order/cadence guards, exact native/reference integrity, allfive tooling tests,40-type census, prior accepted records/draft preservation, source/delivery/classification/duplicate/registry checks, research-only scope and diff check. Per-section integrity and full validation are saved with this checkpoint.

Exact next task: remaining structure protection/hint producers and portal/control blocks, remaining callbacks, nested ASM, compatibility/source exclusions; then R2f8 remaining-content closure and final Twilight dedup/promotion. IceAndFire remains unstarted until Twilight COMPLETE is pushed and live-verified. Continue automatically while enforced current usage remains healthy.

## R2f8z — structure admission, hints and physical barriers

Continues live-verified `1aec32ae7cb9d2ce04887268c1e8ba1759f42576`. Adds six packages and28 native delivery cases: protected player actions, player-caused hostile damage admission, real hint Kobold/book production, directional Stronghold Shield mining, Trophy Pedestal shield removal/progression and five Force Field geometries. [Full reviewed contracts and evidence](benchmarks/external-effects-catalog/twilightforest-structure-gates-review.md).

The hostile gate tests causing Player, Enemy victim, Kobold exclusion and actual loaded protected piece; it cancels native incoming damage without changing source or HP. RightClickBlock cancellation is broader than the break allow-tag. That tag includes a direct optional gravestone mapping. Hint production uses strict1200tick structure-object cooldown and ignores addFreshEntity return. Pedestal shield removal requires eligibility when enforced, while trophy criterion/stat requests can reach ineligible nearby players; the actual advancement still requires its separate Lich criterion. Force Fields use native partial collision and retain stale connection bits on failed updates. No production change.

Twilight remains PARTIAL at253 mechanic drafts/876 paths, all40 custom DamageTypes USED, REVIEW_REQUIRED0, zero promoted. Accepted four mods116/161/217 and every protected subsection remain unchanged; runtime0. Validation saved: exact native/reference evidence, source/caller/order guards, subsection integrity, allfive tooling tests, full catalog validation, preservation and diff checks.

Exact next task: native Vanishing/Reappearing/Locked blocks and Castle Doors; then remaining portal/control blocks, callbacks, nested ASM, source exclusions and compatibility closure. Finish R2f8 and final Twilight dedup/promotion before starting IceAndFire. Continue automatically while actual enforced usage remains healthy.

## R2f8aa — native vanishing barriers and Castle Doors

Continues live-verified `641e33dfb66bed3830cad0eed0d9c7542d7d08d7`. Adds four packages/24 paths covering Vanishing removal, Reappearing collision cycles, native Tower Key unlocking/loot and Castle Door cycles. [Complete contracts and source evidence](benchmarks/external-effects-catalog/twilightforest-vanishing-doors-review.md).

The initial Vanishing lock search is bounded by512 queue pops, including duplicate/boundary entries. Scheduled propagation does not recheck locks. Reappearing collision is absent for nominal95ticks; CastleDoor has a separate82..86tick cycle and a literalfalse lock helper. Native creative players still consume a key because successful block interaction returns before the later ItemStack creative refund branch. Inactive Unbreakable Vanishing reports6000 explosion resistance through its inherited override despite its6000000 base property. These are recorded native semantics; no implementation changes.

Twilight remains PARTIAL at257 mechanic drafts/900 paths,40/40 USED custom types, REVIEW_REQUIRED0, zero promoted. All previous drafts/errata and four accepted mods116/161/217 preserved; runtime0. Validation includes exact source/reference/caller integrity, state/cost/order guards, five tooling tests, subsection and full catalog checks, preservation and diff checks.

Exact next task: native portal creation/lightning/transport and configured first-spawn path, then remaining Builder/Antibuilder/cloud/control blocks, events/nested ASM, compatibility and source exclusions. Finish R2f8 and final Twilight dedup/promotion before IceAndFire. Continue automatically while actual enforced usage remains healthy.

## R2f8ab — native portal resource, lightning and transport

Continues live-verified `961b4c6c9fe7620c8853f64d81550938ac78481f`. Adds five packages/36 paths: actual owned-catalyst pool creation, native lightning delivery, PortalProcessor transport, destination routing/cache/terrain, and configured login/respawn entry. [Full source contracts](benchmarks/external-effects-catalog/twilightforest-portals-review.md) include the installed common-config snapshot and exact raw/loader comparisons.

Installed destructivePortalLightning=true makes a visual-only bolt but explicitly calls native thunderHit on nearby entities; false permits ordinary automatic lightning instead. Native lightning_bolt remains ownerless, uses real recipient mitigation and separate fire-timer handling. No custom DamageType is invented. Portal contact uses Minecraft PortalProcessor, whose postincrement gives61 qualifying calls at default60; overlay attachment is separate. Destination terrain can be created before travel veto. Configured first-spawn ignores changeDimension return before writing respawn/BANISHED, but this configuration is disabled in the installed snapshot. Native search/cache/collision limits are recorded without changes or runtime safety claims.

Twilight remains PARTIAL at262 mechanic drafts/936 delivery cases;40/40 custom types USED, REVIEW_REQUIRED0, zero promoted. Earlier protected drafts/errata and accepted four mods116/161/217 unchanged; runtime0. Validation saved: source/caller/ordering/config integrity, native references, five tooling tests, subsection/full catalog checks, preservation and diff checks.

Exact next task: Builder/Antibuilder and cloud/snow/control blocks, remaining event callbacks/nested ASM, compatibility attribution and source exclusions. Then protect R2f8 remaining-content closure and final Twilight dedup/promotion. IceAndFire remains unstarted until Twilight COMPLETE is pushed and live-verified. Continue automatically while actual enforced usage remains healthy.

## R2f8ac - native Builder, Antibuilder and cloud controls

Continues live-verified `8a780600bbf3b6eea309c6f65e26c6f3c3700e26`. Adds five packages/36 paths covering custom terrain construction/substitution, native fall reduction, local precipitation and exact cloud rain-query consumers. [Reviewed contracts and evidence](benchmarks/external-effects-catalog/twilightforest-control-blocks-review.md).

Builder admits 17 placement branches from its <=16 counter test; powered onPlace does not itself schedule construction. Antibuilder compares block types in a transient 729-cell snapshot and substitutes Antibuilt Blocks, without restoring original inventories. Its native AIR-removal path permits drops. Cloud fall multiplies native input by .1 before rounding and retains all fall/hurt gates. Exact cloud rain ASM affects local wetness consumers, including native water-sensitive damage and Conduit/Riptide eligibility; it does not set global weather or bypass those consumers' additional prerequisites. Snow/mushroom support and client presentation are explicitly dispositioned without extra combat packages.

Twilight remains PARTIAL at267 mechanic drafts/972 delivery cases, all40 custom DamageTypes USED, REVIEW_REQUIRED0, zero promoted. Previous protected drafts/errata and accepted four mods116/161/217 remain unchanged; runtime0. Validation includes source/reference/caller/config integrity, native ordering/return guards, all five tooling tests, subsection/full validation, preservation and diff checks.

Exact next task: Wrought Iron Fence/native leash/pathfinding control, then remaining events/nested ASM, compatibility attribution and source exclusions. Protect R2f8 whole remaining-content closure and final Twilight dedup/promotion before IceAndFire. Continue automatically while actual enforced usage remains healthy.

## R2f8ad - native fence, leash and bound-zombie controls

Continues live-verified `ca0ba916a2f81c2a3f29e4ed11e399780215e97c`. Adds three packages/24 paths covering Wrought Iron Fence collision/cap state, genuine native lead/knot support, and two real Lich Tower bound-zombie producers. [Reviewed contracts](benchmarks/external-effects-catalog/twilightforest-fence-leash-review.md) include exact installed ASM, native leash movement/eligibility and save/load admission.

The full installed-class census found two attachment writers omitted by incomplete source aids. Actual room and perimeter templates establish legitimate delivery. Native ProtoChunk saves the zombie's leash position, allowing normal loading to restore the real knot; not adding the temporary knot during structure generation is not a proven defect. The close-follow override retains native elastic pull, leash breaking, holder restriction and hostile AI. No damage source or production fix was added.

Twilight remains PARTIAL at270 mechanics/996 paths, all40 custom types USED, REVIEW_REQUIRED0, zero promoted. Accepted four mods116/161/217 and earlier protected drafts/errata preserved; runtime0. Validation includes source/producer/ordering guards, references and structured template evidence, five tooling tests plus four new NBT parser tests, subsection/full integrity, preservation and diff checks.

Exact next task: remaining EntityEvents callbacks (including multiplayer health adjustment), other Lich worldgen trap/spawner paths and nested ASM; finish compatibility and global source exclusions. Protect R2f8 remaining-content closure, then deduplicate/promote Twilight COMPLETE before IceAndFire. Continue automatically while actual enforced usage remains healthy.

## R2f8ae - multiplayer partial evidence saved at usage boundary

Continues live-verified `9784db969a2ca2dd2e9eced38a763fc60d9ff2eb`. R2f8ad remains the latest completed semantic subsection. The actual enforced weekly allowance reached80% used/20% remaining, so new research stopped and valid multiplayer read-ahead was preserved. No reset credit redeemed.

[Exact resume notes](benchmarks/external-effects-catalog/partial-notes/twilightforest-r2f8ae-multiplayer.md) and [pinned partial evidence](benchmarks/external-effects-catalog/partial-evidence/twilightforest-multiplayer/manifest.json) save installed TF/raw Minecraft/exact NeoForge witnesses and a whole outer-JAR source/resource census. This bundle is PARTIAL, adds no reviewed mechanics/paths and no REVIEW_REQUIRED entry. It must not be treated as semantic closure.

Twilight remains PARTIAL at270 reviewed mechanic drafts/996 paths,40/40 custom DamageTypes USED, no unfinished types, REVIEW_REQUIRED0, zero promoted. Four accepted mods116/161/217 preserved. IceAndFire unstarted; runtime0, no L2/Stage/production/Phase6/7 changes. Full R2f8ad validation, five tooling tests plus four NBT-reader tests, partial witness regeneration/integrity, preservation and diff checks protect the save.

Exact next task: finish multiplayer maximum-health versus current-HP behavior, native spawn/event/participant admission, permanent modifier and transient participant persistence, native reward consumers and source guards from the saved bundle. Then remaining EntityEvents, Lich worldgen trap/spawner paths, nested ASM, compatibility/global exclusions; R2f8 completion and final Twilight promotion before IceAndFire. Stop after push/live equality because of the actual usage save boundary.

## R2f8ae complete - multiplayer review and corrected scope

Resumes protected `b00c1f7fc41c0feb28e1c9d8f9023c8eb46bc2c3` partial evidence. [Completed multiplayer contracts](benchmarks/external-effects-catalog/twilightforest-multiplayer-review.md) add one combat maximum-health package/three native spawn paths: Twilight271 mechanics/999 paths,40/40 custom types USED, zero REVIEW_REQUIRED or promoted records.

Native ordering separates added maximum health from current HP; Naga's later finalizer may refill it. Modifier duplicate IDs throw and permanent state survives reload; participant list does not. Exact damage-post/source/death admission and real loot/advancement consumer routing are closed. Acquisition/progression behaviors are dispositions rather than new combat packages. Existing boss mechanics were reused without re-review or production changes.

The owner explicitly superseded percentage-based stopping and narrowed future scope to combat-significant compatibility mechanics. Remaining utility, maps, storage, crafting, information, progression, cosmetic and noncombat worldgen receive brief exclusions. Continue after this checkpoint through true combat event/worldgen/ASM/source gaps, R2f8 closure, final Twilight dedup/promotion, then IceAndFire only after COMPLETE is pushed/live-verified. Static only; no runtime/L2/Stage/Phase6/7 work.

Validation: native source/order/persistence guards, exact references and resource routes, five tooling tests, targeted/full catalog checks, prior-checkpoint/accepted-mod preservation and diff check.

## R2f8af — remaining combat callbacks

Resumes live-verified multiplayer checkpoint `98a9bd4d9f1083eb2de212ca269e9ae59b78f4f5`. [Remaining native combat review](benchmarks/external-effects-catalog/twilightforest-combat-closure-review.md) closes Hedge, Arctic Fur, inherited Maze Slime fall/motion, Sinister and bookshelf encounter spawning, controlled structure spawn selection, remaining event dispositions and the final ten nested ASM transforms. All31 registered transforms now have pinned coverage; no runtime application is claimed.

The bookshelf cannot consume a slot through its normal successful-spawn call chain while SPAWNER is true. Burning it uses native exceptions to cap/light checks, retains collision/Peaceful/native insertion, and destroys the block. Sinister uses native spawn-position checks that bookshelf does not. Conquered structure spawn selection returns null and leaves the incoming list unchanged. These are native source facts, not proposed production fixes.

Twilight remains PARTIAL at277 mechanic drafts/1014 paths, all40 custom DamageTypes USED, REVIEW_REQUIRED0, zero promoted; four accepted mods116/161/217 and historical evidence preserved. New callback/source/ASM guards, evidence integrity, five tooling tests, full validation and diff/preservation checks protect this checkpoint. Exact next task: final global combat-source/exclusion and compatibility census, protect R2f8 remaining-content completion, then deduplicate/promote Twilight COMPLETE before starting IceAndFireCE beta15. No runtime/L2/Stage/production/Phase6/7 work.

## R2f8 — TWILIGHT_REMAINING_CONTENT_COMPLETE

Resumes protected `99c517b6906562860c228eae3d4ed33968e4104a`. [Whole Twilight source closure](benchmarks/external-effects-catalog/twilightforest-r2f8-complete-review.md) is complete for the corrected combat scope:38 immutable semantic sections,277 mechanic drafts/1014 path cases,40/40 custom DamageTypes USED, one custom status, all31 registered transformers, no REVIEW_REQUIRED or remaining native ambiguity. Supplemental exact whole-class API scan covers279 methods across1,943 classes;19 new pinned methods have brief noncombat exclusions. The source scan supplements prior registry/inheritance/resource review.

Scoped compatibility attribution is closed; native generic hooks and optional Curios/Parry/cosmetic-armor bridges are recorded without a runtime compatibility claim. Accepted four mods116/161/217 remain unchanged. Five tooling tests, global/source/type checks, full evidence/reference validation and research-only preservation/diff checks protect this checkpoint. Twilight remains PARTIAL pending final deduplication/promotion only; IceAndFire has not started. Exact next task: deduplicate all reviewed drafts and paths, preserve meaningful source/owner/admission differences, promote Twilight COMPLETE, validate/push/live-verify, then begin narrow IceAndFireCE beta15. Continue automatically while execution supports safe checkpoints; no arbitrary percentage stop.

## R2f-final — TWILIGHT_FOREST_SEMANTIC_REVIEW_COMPLETE

Promoted the protected R2f8 whole-source closure at `393426ae12907217f25279013d437181c7b16dac`: 219 distinct combat mechanics / 640 native delivery contracts after total explicit mapping of 277 drafts / 1,014 cases. Forty-nine utility packages excluded, ten repeated packages merged, 99 cases folded into fixtures, 275 cases scope-excluded. All 40 custom DamageTypes USED; one custom status Frosted; zero native ambiguities/REVIEW_REQUIRED. Four prior accepted mods preserved at 116/161/217. The five views and mod ledger now include COMPLETE Twilight.

[Final review and classifications](benchmarks/external-effects-catalog/twilightforest-final-review.md), [total deduplication map](benchmarks/external-effects-catalog/twilightforest-final-promotion-map.json), [future runtime fixtures](benchmarks/external-effects-catalog/twilightforest-future-runtime-fixtures.json), [integrity](benchmarks/external-effects-catalog/twilightforest-final-integrity.json), [full validation](benchmarks/external-effects-catalog/r2f-final-validation.json). Historical subsections remain immutable; their earlier partial counts/next tasks are superseded by this current checkpoint.

After commit/push/live equality, begin narrow installed IceAndFireCE beta15 combat research automatically. No runtime boss/L2 tests, Stage, production, Phase 6 or Phase 7 work.

## R2g1 — Ice & Fire source foundation

Twilight COMPLETE protected at `86b6e670819be918b2df9ddcd73bf81b729282fc`. IceAndFireCE beta15 static combat review is now PARTIAL. Two custom statuses, five custom damage declarations, seven factory caller methods and six status-reference methods are pinned. The indirect lightning factory actually selects the ICE holder; direct lightning charge hits and manager area damage use different source routes. Existing Tensura-Iaf compatibility directly classifies those actual holders. Full family eligibility/effects remain unfinished; zero Ice & Fire records promoted.

[Foundation and exact next task](benchmarks/external-effects-catalog/iceandfire-r2g1-review.md). No runtime boss/L2/Stage/production/Phase 6/7 changes.

## R2g2a — Frozen core and weapons

Ice & Fire remains PARTIAL. Frozen core/lifecycle, six ordinary weapon paths and the existing ColdNullification dispatcher are reviewed. Frozen is velocity control; weapon Slowness/MiningFatigue are independent, and fire-removal is vetoable. Ice blood bonus is a distinct native secondary hurt attempt. Dragon manager payload evidence is saved; actual dragon delivery roots remain next. [Findings and exact resume](benchmarks/external-effects-catalog/iceandfire-r2g2a-review.md). All accepted Twilight records remain unchanged.

## R2g2b — Frozen native delivery complete

Frozen native source mapping is complete: six ordinary weapon paths plus seven dragon entry routes, three area contracts. Damage, Frozen, terrain grief and companion statuses remain separate. Native charge entity collision rejects TamableAnimal through a self-owner comparison; charge area requires canGrief while breath living payload does not. No behavior was changed. [Review and next task](benchmarks/external-effects-catalog/iceandfire-r2g2b-review.md). Ice & Fire remains PARTIAL; Siren charm is next.

## R2g3a — Siren song

Native song control is a Siren-owned target map, independent of its30tick HARMFUL status marker. Effect rejection/cure need not stop control. Two purported Player guards actually inspect the map; native rotation therefore also applies to Player victims. Existing SpiritualAttackNullification compatibility acts as earplugs at periodic target acquisition. [Evidence and exact resume](benchmarks/external-effects-catalog/iceandfire-r2g3a-review.md). No fixes or runtime tests; Flute and bite/pull are next.

## R2g3b — Siren Flute and attacks

Flute uses a serialized loveTicks attachment driven by native EntityTickEvent.Post. It clears Mob target/navigation after normal entity tick; it is not a MobEffect or universal damage veto. Siren bite/pull damage uses native mob_attack; pull motion does not depend on hurt succeeding and its X term uses old Z velocity. [Evidence and exact next task](benchmarks/external-effects-catalog/iceandfire-r2g3b-review.md). Gorgon is next; Ice & Fire remains PARTIAL.

## R2g4 — Gorgon

Gaze spawns the statue before player hurt; Head uses victim-attributed hurt and requires true before player statue creation. Non-player branches remove directly. Petrification is binary and receives no Stage multiplier; fallback melee/Poison retain native numeric routes. [Combat semantics, immunity, exact integration points and future fixtures](benchmarks/external-effects-catalog/iceandfire-r2g4-review.md). Dragons next; Ice & Fire PARTIAL.

## R2g5a — Dragon elemental combat paths

Native Fire/Lightning direct damage, independent status/control, optional charge explosion and actual fire/spikes are separated. Scaling points target each native damage amount exactly once; no Stage implementation. [Evidence, decisions and resume point](benchmarks/external-effects-catalog/iceandfire-r2g5a-dragon-elements-review.md).

## R2g5b — Dragon body combat and defenses

Shared Dragon body attacks, rider source changes, independent control, roar variants, healing versus direct HP writes, defenses and multipart routing are reviewed with single scaling points. [Evidence, decisions and resume point](benchmarks/external-effects-catalog/iceandfire-r2g5b-dragon-combat-review.md).

## R2g6 — Cockatrice and Scepter combat

Cockatrice and Scepter ownerless Wither paths, admission differences, native control/taming, healing and attachment lifecycle reviewed without duplicating protected gaze/attachment research. [Evidence, decisions and resume point](benchmarks/external-effects-catalog/iceandfire-r2g6-cockatrice-review.md).

## R2g7 — Death Worm and Cyclops combat

Native body attacks, Worm repeated TNT explosions/source changes, Cyclops eye blinding before HP admission, grab hooks and held Eye Weakness reviewed. [Evidence, decisions and resume point](benchmarks/external-effects-catalog/iceandfire-r2g7-worm-cyclops-review.md).

## R2g8a — Ghost, Troll and Myrmex disposition

Ghost phasing/body and magic sword routes, Troll control/regeneration/sun conversion, installed armor absorption hook mismatch and Myrmex absence reviewed. [Evidence, decisions and resume point](benchmarks/external-effects-catalog/iceandfire-r2g8a-ghost-troll-review.md).

## R2g8b — Hydra and Sea Serpent combat

Head severing separated from admitted HP, fire-state survival/regrowth, native Poison/regen, stalled live-owner Serpent bubbles and weapon-versus-dispenser ammo reviewed. [Evidence, decisions and resume point](benchmarks/external-effects-catalog/iceandfire-r2g8b-hydra-serpent-review.md).

## R2g8c — Avian and mount combat

Avian volleys and source gates, real gust actor/target, rider damage/defenses, native mount healing and WaterBreathing reviewed; utility excluded. [Evidence, decisions and resume point](benchmarks/external-effects-catalog/iceandfire-r2g8c-avian-mounts-review.md).

## R2g8d — Dread combat and summons

Dread melee, summons, skull sources and defenses reviewed. Native Lich skull origin, unresolved Beast/Scuttler commanders, unreachable legacy necromancy and unregistered Queen are retained as availability limits. [Evidence, decisions and resume point](benchmarks/external-effects-catalog/iceandfire-r2g8d-dread-review.md).

## R2g9a — Remaining special weapons

Post-hit bonus, fire and lightning paths, Dragonsteel chain, gauntlet/sweep, Dragonbone delivery and Tide Trident reviewed with single Stage points and distinct admission fixtures. [Evidence, decisions and resume point](benchmarks/external-effects-catalog/iceandfire-r2g9a-weapons-review.md).

## R2g9b — Control, Pixie and combat support

Chain and Tensura attachment admission, flute ownership, Pixie source/status/resource effects, combat foods and real lightning armor veto reviewed. Remaining work is whole-JAR closure and promotion. [Evidence, decisions and resume point](benchmarks/external-effects-catalog/iceandfire-r2g9b-control-review.md).

## R2g10a — Ice & Fire combat closure

All726 installed classes cross-checked:188 watched methods,130 targeted callers,5 custom DamageTypes and7 factory callers have native witnesses and reviewed family/exclusion coverage. Promotion remains next. [Evidence, decisions and resume point](benchmarks/external-effects-catalog/iceandfire-r2g10a-closure-review.md).

## R2g10b — Ice & Fire combat catalog COMPLETE

81 reviewed combat packages and 228 native source/control/defense contracts promoted after explicit deduplication; no runtime compatibility certification. [Owner table, Stage points and next task](benchmarks/external-effects-catalog/iceandfire-final-owner-table.md).

## R2h1 — Eternal Starlight source foundation

Installed 0.8.1 source foundation: 18 custom DamageTypes, 9 MobEffects, 29 factory callers and the actual NeoForge combat bridge pinned. Family semantics remain unfinished; Ice & Fire COMPLETE preserved. [Evidence and next task](benchmarks/external-effects-catalog/eternalstarlight-r2h1-source-foundation-review.md).

## R2h2a — Crystal Infection, Numbness and shared admission

Crystal delivery and hurt-return distinctions, finite/infinite tick behavior, armor penalty, native Numbness debt/payout and Crescent/Unrealium admission reviewed; derived damage requires one Stage application on the parent. [Evidence, decisions and resume point](benchmarks/external-effects-catalog/eternalstarlight-r2h2a-crystal-numbness-review.md).

## R2h2b — Remaining Eternal Starlight status and control

Remaining seven statuses, derived Starfire, persistent Teary budget/immunity divergence, selective Oblivion collision, Whip and Permafrost paths, and native Tear Bomb clouds reviewed. No repeated Stage on derived hits. [Evidence, decisions and resume point](benchmarks/external-effects-catalog/eternalstarlight-r2h2b-status-control-review.md).

## R2h3a — Eternal Starlight energy combat

Energy sources, native iframe differences, mechanical firework null-weapon gate, boomerang callback identity, ownerless ground smash and damaging debris reviewed. [Evidence, decisions and resume point](benchmarks/external-effects-catalog/eternalstarlight-r2h3a-energy-review.md).

## R2h3b — Eternal Starlight Golem, Permafrost and laser paths

Protection/charge admission, pre-hurt interruption counters, Frozen Tube splash vs owner-gated HP, and block-clipped boss/Orb lasers reviewed. [Evidence, decisions and resume point](benchmarks/external-effects-catalog/eternalstarlight-r2h3b-golems-review.md).

## R2h3c — Eternal Starlight Lunar and toxic combat

Lunar admission/stun, distinct POISON damage/status routes, independent Wand departure hazards, decoy ownership and native skull blast attribution reviewed. [Evidence, decisions and resume point](benchmarks/external-effects-catalog/eternalstarlight-r2h3c-lunar-review.md).

## R2h3d — Eternal Starlight soul and hunger resources

Soul drain/heal basis and native collision, exact no-pull tag, old-state dagger penalty and owner-dependent Voracious rewards reviewed. [Evidence, decisions and resume point](benchmarks/external-effects-catalog/eternalstarlight-r2h3d-soul-hunger-review.md).

## R2h3e — Eternal Starlight Gatekeeper and Solar Creeper

Ordered Gatekeeper damage admission, pre-hurt healing interruption, native melee/arrow/fireball+explosion routes, sparring resets and teleport fallbacks reviewed; Solar Creeper has no native attack caller proven. [Evidence, decisions and resume point](benchmarks/external-effects-catalog/eternalstarlight-r2h3e-gatekeeper-review.md).

## R2h4a — Eternal Starlight sonar, meteor and seeds

Sonar source distinction, owner-identity manual meteor AoE/shared cooldown and speed/ammo/enchantment seed formula protected with native predicates and future fixtures. [Evidence, decisions and resume point](benchmarks/external-effects-catalog/eternalstarlight-r2h4a-sonar-meteor-seeds-review.md).

## R2h4b — Eternal Starlight Ether, Shattered Blade and Wilt

Ether contact vs corrosion vs shard separation, Shattered Blade owner-attribute and return gates, Wilt aura vs petal/Wither and firework exclusion reviewed. [Evidence, decisions and resume point](benchmarks/external-effects-catalog/eternalstarlight-r2h4b-ether-blade-wilt-review.md).

## R2h5a — Eternal Starlight native ammunition

Native ammo distinction and conditional effects, real Frozen Bomb explosion vs Aethersent cosmetic blast, water trajectory and ordered spear damage reviewed. [Evidence, decisions and resume point](benchmarks/external-effects-catalog/eternalstarlight-r2h5a-native-ammo-review.md).

## R2h5b — Eternal Starlight special weapons and shields

Native spin/critical/sweep ordering, concentration identity, shield reflection ownership and real additional thorn/whip paths reviewed. [Evidence, decisions and resume point](benchmarks/external-effects-catalog/eternalstarlight-r2h5b-special-weapons-review.md).

## R2h5c — Eternal Starlight armor and resources

Glacite retaliation admission, repeated Deepsilver removal, Unrealium same-ID replacement/vibrations and native resource routes reviewed. [Evidence, decisions and resume point](benchmarks/external-effects-catalog/eternalstarlight-r2h5c-armor-resources-review.md).

## R2h6 — Eternal Starlight crests and spell closure

All spell callbacks dispositioned; one passive native Resistance crest and genuine mana damage/refill paths reviewed. [Evidence, decisions and resume point](benchmarks/external-effects-catalog/eternalstarlight-r2h6-crests-spells-review.md).

## R2h7a — Eternal Starlight hazards and enchantments

Separate native fire requests, true falling-block source, enchantment eligibility and weather-only Rocket trigger reviewed. [Evidence, decisions and resume point](benchmarks/external-effects-catalog/eternalstarlight-r2h7a-hazards-enchantments-review.md).

## R2h7b — Eternal Starlight remaining creature combat

Native riding admission, independent explosions/clouds/summons, ownerless Golem damage, creature defenses/heals and actual melee deliveries reviewed. [Evidence, decisions and resume point](benchmarks/external-effects-catalog/eternalstarlight-r2h7b-creatures-review.md).

## R2h8a — Eternal Starlight combat closure

Whole1384-class/274-method audit closes Dusk/Furnace/inherited hazards and remaining native source/physics prerequisites;18 custom source families retained. [Evidence, decisions and resume point](benchmarks/external-effects-catalog/eternalstarlight-r2h8a-closure-review.md).

## R2h8b — Eternal Starlight combat catalog COMPLETE

127 deduplicated packages and 274 native paths, all18 DamageTypes mapped; no runtime compatibility certification. [Owner table and exact next task](benchmarks/external-effects-catalog/eternalstarlight-final-owner-table.md).

## R2i1 — Bosses Rise source foundation

Two native DamageTypes,802 classes,157 combat/admission candidates and actual roll/freeze/event hooks pinned; accepted Eternal Starlight records preserved. [Evidence and resume point](benchmarks/external-effects-catalog/bossesrise-r2i1-source-foundation-review.md).

## R2i2a — Bosses Rise native roll admission

Real server delivery,14..8 invulnerability window, native HP/effect/freeze gates, sequential charge resource and ineffective ordinary projectile-impact callback resolved. [Evidence and resume point](benchmarks/external-effects-catalog/bossesrise-r2i2a-roll-admission-review.md).

## R2i2b — Bosses Rise shared combat contracts

One shared scalable attack boundary; native before/after-Post death restoration, unchanged multipart forwarding and raw push distinguished. Uncalled death helper excluded. [Evidence and resume point](benchmarks/external-effects-catalog/bossesrise-r2i2b-shared-combat-review.md).

## R2i3a — Bosses Rise Knight defense and native mark

Stack break separated from HP, real mark producers/forwarding, ordered phase gates and native arena/reload distinctions resolved; no extra Stage amount. [Evidence and resume point](benchmarks/external-effects-catalog/bossesrise-r2i3a-knight-defense-review.md).

## R2i3b — Bosses Rise Knight offensive payloads

Actual source/return differences across melee/ring/wave/arrow+area/Rift and independent arena mob paths resolved; unused helpers excluded. [Evidence and resume point](benchmarks/external-effects-catalog/bossesrise-r2i3b-knight-offense-review.md).

## R2i4 — Bosses Rise Infernal Dragon and guardians

Dragon phase and causing-entity admission, native arrow/fire/explosion/breath paths and independent guardian control resolved; HP and ignition/phase/control remain separate. [Evidence and resume point](benchmarks/external-effects-catalog/bossesrise-r2i4-infernal-dragon-review.md).

## R2i5a — Bosses Rise Yeti defense and phase ordering

Yeti raw lethal branch bypasses inherited hurt, trident reductions stack, and phase/counter writes precede damage results; legacy selfhurt counter is dormant in normal native lifecycle. [Evidence and resume point](benchmarks/external-effects-catalog/bossesrise-r2i5a-yeti-defense-review.md).

## R2i5b — Bosses Rise Yeti ice attacks and control

Yeti native melee/ice HP separated from iframe/freeze/control; swept magic versus real playerTouch freeze, terrain spawn admission, resource/reload predicates and roll-aware shove resolved. [Evidence and resume point](benchmarks/external-effects-catalog/bossesrise-r2i5b-yeti-offense-review.md).

## R2i6 — Bosses Rise Sandworm combat semantics

Sandworm segment resource measures real HP loss; direct-source equality can retaliate without an attacker. Body controls and poison hazards are independent of hurt success, while columns push allies before rejecting HP damage. [Evidence and resume point](benchmarks/external-effects-catalog/bossesrise-r2i6-sandworm-review.md).

## R2i7a — Bosses Rise Kraken defense and phase resources

Kraken hidden state sets real invulnerability; cannon5 takes priority over projectile.25. Knockdown tracks actual HP loss, and tentacle removal callbacks are not limited to death. [Evidence and resume point](benchmarks/external-effects-catalog/bossesrise-r2i7a-kraken-defense-review.md).

## R2i7b — Bosses Rise Kraken attacks, cannon and pirates

Native Living-owned cannon/crate explosions are player_explosion; only cannon custom impact receives the usual Kraken5 weakness. Tentacle goals use adjusted goal ticks, and pirate AI melee hits are disabled in favor of timed callbacks. [Evidence and resume point](benchmarks/external-effects-catalog/bossesrise-r2i7b-kraken-offense-review.md).

## R2i8a — Bosses Rise Ice and Sandworm Gauntlet delivery

Gauntlets extend nine existing native hazard packages; inherited shield use, active landing, shard ownership and real Sandworm constructor delivery are pinned. Prior static-helper wording corrected additively. [Evidence and resume point](benchmarks/external-effects-catalog/bossesrise-r2i8a-gauntlets-review.md).

## R2i8b — Bosses Rise Undying Tentacle and Kraken Trident

Undying whip controls motion without HP; owned Ghost uses its own mob_attack. Kraken Trident adds a separate native5 area request and pull after inherited hits, including failed direct HP results. [Evidence and resume point](benchmarks/external-effects-catalog/bossesrise-r2i8b-tentacle-trident-review.md).

## R2i8c — Bosses Rise Dragon armor and remaining combat equipment

Dragon boots normally run the same explosion twice and still invoke the explicit pass after start cancellation. Retaliatory fireballs, player SwordWaves and saber-owned pirates reuse reviewed native payloads. [Evidence and resume point](benchmarks/external-effects-catalog/bossesrise-r2i8c-equipment-review.md).

## R2i9a — Bosses Rise combat source closure

All157 watched methods across802 classes have native witnesses. Arena/guardian AI melee admission is confirmed; remaining unmatched methods add no damage source. [Evidence and resume point](benchmarks/external-effects-catalog/bossesrise-r2i9a-closure-review.md).

## R2i9b — Bosses Rise combat catalog COMPLETE

82 deduplicated packages, 232 native paths and both custom DamageTypes mapped. Static semantics complete; future integration reviews remain explicit. [Owner table and next task](benchmarks/external-effects-catalog/bossesrise-final-owner-table.md).

## R2j1 — Bosses of Mass Destruction source foundation

One custom DamageType, five native source callers,287 classes and37 combat/admission candidates pinned; existing625 mechanics and1535 native paths preserved. [Evidence and resume point](benchmarks/external-effects-catalog/bomd-r2j1-source-foundation-review.md).

## R2j2 — Bosses of Mass Destruction shared admission

Confirmed native Holder/value filter mismatch without repairing it; preserved rejected-hit callbacks, requested-damage memory, strict HP milestones and cap-safe single healing point. [Evidence and resume point](benchmarks/external-effects-catalog/bomd-r2j2-shared-admission-review.md).

## R2j3 — Bosses of Mass Destruction Night Lich

Native missile status independent of hurt success, captured-Lich comet explosion source, genuine Phantom initialization and teleport placement/cancellation proven; no mechanics repaired. [Evidence and resume point](benchmarks/external-effects-catalog/bomd-r2j3-night-lich-review.md).
