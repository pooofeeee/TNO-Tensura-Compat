# Validation record, limitations and possible next work

## Test evolution

These counts describe different milestone snapshots; they must not be summed as
unique tests or treated as a consistent benchmark workload.

| Milestone | Recorded validation |
| --- | --- |
| Initial V1 + Sugar Rush | 22 retrieval tests and 13 workflow tests |
| V1.5 / repaired V1 foundation | 64 tests before V2 additions; selected dependencies and 11 animation tests included |
| V2.0 / first repair replay | 82 per mode; 2,867 V1 retrievals unchanged across 14 completed mods |
| Exact coding-target prototype | 92 per mode |
| V3 Change Plans | 110 per mode |
| V4 and fresh five-defect replay | 128 per mode |
| Task Preflight | 12 new tests, 140 combined per mode |
| Archive verification on 2026-10-11 | 140 per mode, freshly rerun; logs linked below |

The current 128 Mod Intelligence tests comprise 39 V1, 14 Sugar Rush, 11 animation,
18 V2, 10 target-prototype, 18 V3 and 18 V4 tests. The 12 preflight tests add
manifest/route/file/source integrity, direct-plan equality, JSON failures,
nonexecution of test commands, upstream corruption checks and real-catalog
examples. Existing V4 internals and catalog evidence were unchanged by preflight.

Fresh archive logs: [normal](verification/normal.log),
[`-O`](verification/optimized.log),
[`PYTHONOPTIMIZE=1`](verification/environment.log). Commands assemble the same
`test_mod_intelligence*.py` and `test_task_preflight.py` discovery suites. These
runs validate the published current implementation, not historical implementations.
Historical tests and logs remain in each package, including intermediate focused
counts that differ from final milestone docs.

Separate benchmark oracles: alias repair 4 tests; complex Corrodent 15; three-task
coding benchmarks 11/23/24; real repository preflight A/B 40 (25 existing + 15 new).
All final arms passed their specified oracles, but those tests were visible to
implementers and do not establish complete correctness.

## Known limitations and unresolved findings

- **Usage telemetry:** no actual input/output/reasoning tokens, billed cost or
  allowance measurements. Complete model context is unavailable; some outputs
  were truncated by transport. Reported bytes/characters and elapsed times cannot
  substitute for usage or reasoning measurements.
- **Statistical validity:** early pilots were sequential and unblinded; later
  experiments use one fresh run per task/arm. Some comparisons reuse historical
  baseline runs. Scheduling, operational retries and model sampling vary.
- **Model identity:** Astra model/effort overrides were requested explicitly.
  The older Sol configuration was inherited and identified by the user; its exact
  runtime model identifier was not independently exposed.
- **Source mapping:** available edit/test mappings are static fixtures. Native
  class offsets do not identify production source locations. No production
  integration or Minecraft runtime validation was performed.
- **Profile coverage:** only three pinned literal profiles; broader task scope
  and missing dependencies/test coverage remain manual. EXCLUDE is informational,
  not runtime independence or an absence-of-effects certificate.
- **Integrity snapshot:** the historical shared catalog-integrity suite had
  13/14 passing tests. Its published-snapshot equality check failed because the
  committed snapshot was already stale at the original baseline; the live auditor
  passed. Canonical records were not rewritten to make the test pass. This suite
  was not freshly rerun during archiving; current 140/140 results are a different,
  explicitly named suite.
- **Constrained workflow regression:** the task-2 arithmetic overflow difference
  was confirmed outside frozen acceptance tests. It remains in the archived
  experimental solution; no repair was invented or applied during the evaluation.
- **Experimental solutions are not shipped fixes:** the mutable-output alias fix,
  complex Corrodent extension and later preview APIs were isolated coding tasks.
  Their passing results do not mean those changes were applied to the baseline
  repository module. Publishing an archive does not merge experimental code.
- **Preflight scope:** manifests are trusted caller declarations of scope and
  approved files. They do not prove task completeness or test coverage. Source
  checks compare catalog pins, not installed JAR bytes. New files and multiple
  expected dependency identities are outside the small experiment.
- **Unavailable historical sources:** the original external Astra audit attachment
  and full chat transcripts are not available as files. The user-supplied issue
  list, repair docs and independent reproductions preserve the confirmed facts.
  No transcript, audit text or missing telemetry has been fabricated.

## Potential next improvements, ordered by evidence

| Candidate | Why consider it | What would justify implementation/adoption |
| --- | --- | --- |
| Controlled preflight replication with matched output/session handling | Last A/B duplicated a truncated preflight and repeated an asynchronous test; those costs confound results | Same task/tests/model, adequate identical outer+inner output budgets, resume sessions consistently, count all setup and retries |
| Actual usage and manifest-preparation measurement | Current conclusion cannot answer token/cost economics | Capture available usage telemetry and authoring effort; if unavailable explicitly retain an inconclusive cost conclusion |
| Reusable approved task manifests for recurring work | Scope and test/target/pin information otherwise get restated | Demonstrate repeat use with unchanged/stale-pin checks and reduced model-facing decisions; count maintenance cost |
| More targeted evidence delivery for declared broader scope | Full V3 may be larger than V4 plus a narrow supplement | Measured context need and complete preservation/UNKNOWN checks; no heuristic removal based on names |
| Explicit arithmetic-boundary acceptance checks | Constrained prompting dropped a useful overflow boundary | Apply equal criteria to both arms before freezing; do not retroactively rescore historical tests |
| Real production source/test mappings for an authorized integration | Current mappings stop at fixtures | A separately specified production task, exact source correspondence and runtime verification; do not infer mappings from names |
| Additional adaptive profiles | Could help a demonstrated recurring edit class | Real task demand, explicit scope and pinned oracles; avoid speculative coverage expansion |

**Not justified now:** an LLM router, automatic model router, new Mod Intelligence
version, persistent graph service, MCP server, universal formula evaluator,
automatic gameplay patching or further mod research. Extra High had no frozen
quality advantage in the measured tasks; that does not establish it is never
useful. Router overhead and escalation criteria need their own evidence.

The current recommendation is to preserve the validated implementation, treat
preflight as experimental, and run at most the explicitly authorized next
measurement. This archive task ends with commit/push, not new feature work.
