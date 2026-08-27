# Phase 5F Suite A machine-readable evidence

These JSON Lines files preserve the structured `TNO_PHASE5F_SUITE_A` records
from the accepted post-fix official server captures. Each file contains its
catalog, case-start records, every per-shot row, case results, and final suite
result exactly as emitted by the runtime harness.

Locked protocol:

- APO profile: `ANCIENT_SINGLE_PROSPEROUS_SPECTRAL`
- TNO family: `NONE`
- TNO stage: `Native`
- 10 shots per case
- 200-tick fixed observation window
- natural representative and maximum levels, then stress levels 300, 600, 800,
  and 1000 where not duplicated by the natural maximum

The source logs remain ignored runtime state. The checked-in extractor validates
the boss ID, profile, protocol, initialization, complete case count, absence of
case errors, and presence of per-hit rows before writing an artifact:

```powershell
scripts/extract-phase5f-suite-a.ps1 `
  -LogPath <runtime-log> `
  -OutputPath <artifact.jsonl> `
  -ExpectedBoss <entity-id> `
  -ExpectedCases <count>
```

Accepted captures:

| Artifact | Cases | Per-shot rows | Case errors |
|---|---:|---:|---:|
| `luminous_valentine.jsonl` | 5 | 50 | 0 |
| `hinata_sakaguchi.jsonl` | 6 | 60 | 0 |
| `gazel_dwargo.jsonl` | 6 | 60 | 0 |
| `orc_disaster.jsonl` | 6 | 59 | 0 |

Orc Disaster has 59 rows because the natural-representative target was defeated
on shot 9. This is a valid terminal case, not missing evidence.
