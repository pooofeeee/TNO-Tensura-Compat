# Phase 6 endgame-effectiveness calibration

This branch is calibration and architecture validation only. It does not
implement a permanent L2 solution, change Curve C, change Stage thresholds,
or change any production combat behavior.

## Checkpoint ledger

| Checkpoint | Status | Evidence | Conclusion |
|---|---|---|---|
| A — durability decomposition | Complete | `docs/benchmarks/phase6-endgame-calibration/durability.jsonl` | Generic L2 vanilla-health scaling is exact and independently observable; it is capped at 10,000 HP here. Native L2 does not scale SHP, but the required external datapack adds 3% of native SHP per L2 level. Tank is a separate trait multiplier. |
| B — Magic/Holy classification | Complete | `docs/benchmarks/phase6-endgame-calibration/classification.jsonl` | Both Tensura sources bypass armor but lack NeoForge `IS_MAGIC`; therefore installed L2 Dementor reduces both and Dispell reduces neither. Preserve source identity is the safe default. |
| C — development calibration context | Complete | `Phase6CalibrationContext` plus unit tests | Synchronous ThreadLocal scope; observes only `getExisting`; fail-closed; no serialized or L2-owned state changes; impossible to activate in production. |
| D — diagnostic ceiling | Pending | — | — |
| E — generic-health calibration | Pending conditional checkpoint | — | — |
| F — Dementor calibration | Pending | — | — |
| G — Adaptive calibration | Pending | — | — |
| H — combined candidates | Pending | — | — |
| I — safety matrix | Pending | — | — |

Checkpoint A's full formula audit, 16-case table, exact modifier lists, and
per-case trait/rank lists are documented in the benchmark evidence README.
