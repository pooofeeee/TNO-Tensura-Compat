# Elemental native-event-path evidence

Final interpretation: [research report](../../phase-6-elemental-native-event-path-research.md).

| Artifact | Authority |
|---|---|
| `e1-static.json` | Original installed overload/combination audit; runtime pending at E1. |
| `e2a-recovery.json` | Recovery of the newer branch and eight local files; rejected trial hashes and passing build. |
| `e2-diagnostic.jsonl` | First resumed 90-case capture; **not acceptance evidence**, because Fire Resistance was not yet observed. Never repaired or combined with the accepted capture. |
| `e2-runtime.jsonl` | Accepted 90-case runtime capture, including read-only native fire-guard observations. |
| `e2-validation.json` | Strictly verified identities, stages, overloads, native gates and event outcomes. |
| `e2-extractor-tests.json` | Eight corruption tests that must reject invalid evidence. |
| `e2-static.json` | Repeated installed audit plus the exact pre-event vanilla Fire Resistance guard. Its runtime-status field belongs to the static-only tool; runtime authority is `e2-validation.json`. |
| `e2-provenance.json` | Runtime dependency/capture hashes, 54 Java tests, and diagnostic limitations. |
| `e3-decision.json` | Recomputed five-element results, protected Git-blob checks, production boundary, and exact next task. |

The accepted matrix contains five elements, three targets and six delivery modes.
Every row is a single real release. Native source creation, incoming event and
applied damage are counted separately. Boss trait ranks are the accepted Lv1000
profiles, but temporary effects from setup are retained and observed. In
particular, four Fire/Orc cases have active vanilla Fire Resistance; they do not
establish innate Orc immunity or balanced endgame performance. No event is
manufactured and no defense is suppressed.

Validate from the repository root with PowerShell 7:

```powershell
./scripts/extract-phase6-elemental-native-path.ps1 -LogPath docs/benchmarks/phase6-elemental-native-event-path/e2-runtime.jsonl
./scripts/test-elemental-native-path-extractor.ps1
./scripts/analyze-phase6-elemental-native-path.ps1 -Check docs/benchmarks/phase6-elemental-native-event-path/e3-decision.json
```

Historical Phase 5F, pre-flight, Stage, Magic/Holy and Candidate-C evidence is
unchanged. No third-party JAR, world or raw server log is committed.
