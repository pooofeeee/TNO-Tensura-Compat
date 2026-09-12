# External combat effects catalog — separate research track

**Status: PARTIAL, R1 inventory and research structure.** Phase 6 is complete and closed. This track does not reopen, supersede, recalibrate or change Phase 6, its Stage behavior, accepted family integrations, or production combat. Original Phase 7 is not started by this research.

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
| R1 | Inventory/scaffold; validate, commit, push and verify live SHA before R2 |
| R2 | Pending: broad discovery across every available external target, including non-MobEffect mechanics and compatibility candidates |
| R3 | Pending: vanilla comparisons, classifications, code-proven deduplication and complete delivery/source mapping |
| R4 | Pending: final validation, report and owner-review decision |

Exact next task after protecting R1: perform broad R2 static discovery on the exact installed JARs. Do not confuse candidate scan counts with final effect counts. Save validated partial discovery checkpoints if needed; never represent an unfinished inventory as complete effect coverage.
