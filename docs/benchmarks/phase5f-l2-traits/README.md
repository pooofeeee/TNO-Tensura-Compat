# Phase 5F L2 Hostility trait matrix

This directory contains the dedicated 39-trait runtime-coverage evidence that
follows Suite B. It does not contain a Phase 6 implementation or a balance
change.

The development-only `Phase5FL2TraitMatrix` harness has three isolated modes:

- `catalog` reads the live L2 Hostility dynamic trait registry and datapack
  legality metadata.
- `natural` attaches each accepted Tensura/NEB boss at the exact requested
  levels 50, 100, 150, 200, 300, 400, 500, 600, 800, and 1000. Values outside
  an entity's configured range use the same temporary requested-level fixture
  established in Phase 5F and remain explicitly labeled.
- `forced` suppresses generated traits, attaches one exact trait/rank, and
  exercises real Royal Bow/Royal Arrow physical hits, a direct-physical control,
  Magic Weapon Native, the locked temporary S7 coefficient fixture, boss
  offence, healing, equipment, movement, spawning, and lethal-transition probes.

Forced rows are always compatibility evidence only. A naturally legal trait
is labeled `FORCED_DIAGNOSTIC`; an entity-illegal trait is labeled
`FORCED_ILLEGAL_DIAGNOSTIC`. Neither may be used as natural-spawn or balance
evidence. The harness is registered only in the non-production development
environment, and every artifact records `APO_profile = NONE` and
`production_combat_mutated = false`.

`scripts/extract-phase5f-l2-traits.ps1` is the acceptance gate. It requires the
exact 39-trait catalog, exact requested levels/ranks, clean terminal result,
zero case errors, correct evidence labels, no production mutation, and no
unexpected L2 bypass before preserving JSONL. Raw runtime logs remain ignored.

Validated evidence will be added under `natural/`, `forced/`, and `profiles/`.
The terminal one-row-per-trait classifications will be stored in
`coverage.jsonl` after cross-trait validation.
