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
| D — diagnostic ceiling | Complete | `ceiling_magic_weapon.jsonl`, `ceiling_holy_weapon.jsonl` | Neither reducer alone nor both together are sufficient. Generic-H compensation is also required for practical viability in this controlled profile. The all-100% diagnostic bound reaches about 211-242s S7 TTK at Lv600-Lv1000, proving the three-component architecture is mathematically sufficient without selecting production values. |
| E — generic-health calibration | Complete | `health_magic_weapon.jsonl`, `health_holy_weapon.jsonl` | Q is monotonic but cannot overcome untouched Dementor + Adaptive. Q=1 alone still estimates 10.7-15.0 hour S7 fights at Lv600-Lv1000. No arbitrary L2-level threshold is supported; H naturally scales. |
| F — Dementor calibration | Complete | `dementor_magic_weapon.jsonl`, `dementor_holy_weapon.jsonl` | RD 0.50-0.75 is the promising coarse interval. RD <=0.25 is too weak; RD=1 erases Dementor and is too strong architecturally. |
| G — Adaptive calibration | Pending | — | — |
| H — combined candidates | Pending | — | — |
| I — safety matrix | Pending | — | — |

Checkpoint A's full formula audit, 16-case table, exact modifier lists, and
per-case trait/rank lists are documented in the benchmark evidence README.

## Checkpoint D — diagnostic ceiling conclusions

The accepted D matrix has 144 cases and 1,440 per-hit reducer traces: Magic
and Holy, S5-S7, Lv300/Lv600/Lv800/Lv1000, six diagnostic policies, ten real
Royal Arrow releases per case, and `APO_profile = NONE`. All cases completed
with zero errors, unexpected bypasses, duplicate eligible events, or source
changes. Adaptive retained L2-owned state and progressed from count 1 through
10 with native factor `1.0 -> 0.001953125` where attached.

The ceiling answers are decisive but not balance decisions:

1. Full Dementor recovery alone is insufficient.
2. Full Adaptive recovery alone is insufficient.
3. Full recovery of both is insufficient; S7 still estimates 91-139 minute
   Lv600-Lv1000 fights.
4. Compensation tied to verified level-derived durability is also necessary
   for a practical target, but its correct fraction remains uncalibrated.
5. The all-100% upper bound is capable: S7 estimates 211-242 seconds across
   Lv600-Lv1000, with Lv1000 at 414.400 family DPS and 226.1 seconds.
6. The remaining limiter below that bound is the combination of dominant
   level-derived SHP resources and whichever L2 reducer remains authoritative.
7. Magic and Holy behave equivalently at the reducer boundary; observed small
   differences are runtime variance, not a semantic split.
8. Lv600 already exhibits the same wall as Lv800/Lv1000.

The H diagnostic is specifically the nominal native L2 hostility-health
multiplier, not final total resources. Target HP, Tank, native SHP, and the
external Tensura:L2Hostility SHP bridge remain unchanged and separately
identified. The 100% values are upper bounds only. No Q/RD/RA candidate or
permanent production behavior is selected here.

## Checkpoint E — Q sweep

The accepted E matrix has 120 cases and 1,200 traced hits. It varies only Q
through 0, 0.25, 0.50, 0.75, and 1.00; RD=RA=0 throughout. At S7 Lv1000,
Magic moves from 0.696 to 1.737 family DPS and Holy from 0.696 to 1.737.
Those are monotonic gains, but native Dementor's logarithm and Adaptive's
unchanged repeated-source collapse dominate them. Q=1 still estimates about
53,900 seconds family-only TTK at Lv1000.

Accordingly, level-derived durability participation is necessary in the
three-component architecture established by D, but never sufficient alone.
No target-level cutoff is justified: the verified H term already follows
actual L2 level, and Lv600 exhibits the same fundamental wall. The nominal H
input remains explicitly distinct from capped vanilla HP, Tank, native SHP,
and the separately observed Tensura:L2Hostility SHP bridge. E does not select
a permanent Q or change any production behavior.

## Checkpoint F — RD sweep

The accepted F matrix has 240 cases and 2,400 reducer traces, split equally
between the accepted legal profiles and legal otherwise-identical controls
with Dementor removed and its budget left unused. The measured formula is
exactly `nativePost + RD * (pre - nativePost)` at the native L2 boundary.

RD 0-0.25 remains too weak; RD 1.00 reproduces the no-Dementor boundary and
would delete the trait's identity. RD 0.50-0.75 is the only promising coarse
region: it retains measurable nonlinear harm while recovering enough signal
for the later combined test. Adaptive remains fully native and is why even
RD=1 alone still produces multi-hour high-level estimates. No permanent RD is
selected.
