# Mod Intelligence real coding benchmark

**Decision: INCONCLUSIVE.** In this three-task sample, V4 completed equally
correct fixture implementations with 19 metered operations versus 22 for the
V1/V2/V3 baseline. This is an observed workflow improvement, not evidence of
model-usage savings or a reliable general speedup. Two adaptive tasks required
full V3 restoration. Baseline agents also chose extra evidence checks, so fewer
commands cannot be attributed entirely to V4.

Repository: `pooofeeee/TNO-Tensura-Compat`; branch: `feat/mod-intelligence-v1`.
Frozen commit: `e0918e782355756f718a1adcff1f346a26230327`.
Evaluation date: 2026-10-10. No Mod Intelligence feature, production, canonical
research, source-evidence, or tracked repository file was changed.

## Method and controls

Six fresh agent contexts executed three independent A/B pairs with no parent
conversation or prior solutions. Every agent inherited the same model and
reasoning configuration; no override was supplied. The execution interface does
not expose the exact underlying model identifier, effort value or token usage.
The standalone Codex CLI was probed but could not authenticate. Usage, token
cost, allowance and reasoning-token savings are therefore **unavailable**, not
estimated from output sizes.

Each pair received identical task specifications, initial implementation, request,
acceptance tests and success criteria. A began with the normal V3 plan and could
use V1/V2/V3 retrieval. B began with V4 and could restore V3/V1 when necessary.
The native numeric proposals were identical; the adapter requirements were
separately explicit in the identical task specifications. Frozen source exports
match 591 committed files byte-for-byte. The shared canonical catalog is pinned
to Git tree `0099393b169557b405dccfa2459e43cd6a539387` and was accessed read-only.

All file inspection, searches, CLI calls, edits and tests used the same meter.
Its path whitelist permits only the agent's own arm and the shared frozen
source. Only `solution.py` can be edited. There was no solution sharing or parent
repair of either arm. Final hashes confirm unchanged tests, requests, protocols
and initial specifications. Agents reported no unmetered tool calls.

Dispatch order was B/A, A/B, B/A across the three tasks; all six ran concurrently.
Elapsed time runs from the first metered operation to completion of the finish
operation and includes model thinking and tool waits, but excludes initial agent
startup and final-message rendering. Concurrent scheduling, one observation per
arm and stochastic model choices limit timing interpretation.

The first experiment export omitted the committed workflow-validation document
referenced by Sugar Rush plans. Its 58 metered operations were discarded as
setup-contaminated measurements; one arm was interrupted. The missing file was
restored from the same commit, all six initial plan commands were preflighted
successfully, and all six tasks were restarted in **new fresh contexts**. These
experimental costs are recorded in `discarded-attempt1/`; they are not concealed
as zero-cost retries or included as a V4 defect. Preparation and independent
scoring are common evaluation overhead, excluded from coding-arm comparisons.

## Tasks and results

These are executable Python coding fixtures over verified mechanics, not a
Minecraft production integration benchmark. They require real implementations,
validation and preservation of existing behavior, rather than plan-only answers
or literal replacements.

| Task | Baseline result | Adaptive result | Quality difference |
| --- | --- | --- | --- |
| 1: local healing | Added ordered dropped-item previews, policy validation and independent snapshots; preserved the original single-call heal default. 11/11 tests. | Implemented the same behavior; restored full V3 because batching exceeds the literal-only profile. 11/11 tests. | None detected in frozen tests or manual review. |
| 2: dependency request | Added float32-coupled controller requests, refresh-only duration updates and queries using retained rate/radius. Restored selected Citadel method records through V1. 23/23 tests. | Implemented the same behavior from V4's complete dependency contract; retained the limitation that individual method records were not independently inspected. 23/23 tests. | None detected; both use the same backend witness validation and test matrix. Manual inspection breadth differs. |
| 3: motion preservation | Added independent server/client frame traces preserving X/Z, downward motion, Slow Falling payload, gates and existing APIs. Restored V1 numeric/evidence details. 24/24 tests. | Implemented the same behavior; restored full V3 for client sound and wider unchanged contracts. 24/24 tests. | None detected; standalone V4 projection was insufficient for the broader task. |

The healing fixture preserves food-or-breed-tag admission, maraca early return,
crafting remainder, FOODSTUFFS breaded handling and dead/max-health behavior.
It adds no owner, poison-immunity, item-stack or AI-scheduler claim. The dependency
fixture preserves float32-before-ceil duration calculation, both uses of the
same request float, refresh-only max-duration updates, retained age/rate/radius/
dimension, strict radius and expiry, owner validity, config/recipient speed gates,
unchanged server GLOBAL query and flying-from-getSpeed. It does not sync existing
client copies or implement transport/list selection. Motion traces preserve
positive-duration/server/client branches, ignored amplifier/owner/addEffect
return, original Slow Falling duration/amplifier/flags and snapshot isolation.

## Recorded workload

Each metered operation corresponds to one top-level `functions.exec` tool call,
one nested `exec_command`, and one meter shell command. CLI/test child processes
are listed separately. File counts are unique direct file inspections; CLI
catalog inputs are backend reads, not additional direct inspection counts.

| Measure | Task 1 A | Task 1 B | Task 2 A | Task 2 B | Task 3 A | Task 3 B |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Direct files inspected | 6 | 5 | 5 | 5 | 5 | 5 |
| Searches | 0 | 0 | 0 | 0 | 0 | 0 |
| Top-level tool calls / meter commands | 10 | 8 | 6 | 5 | 6 | 6 |
| Nested exec-command calls | 10 | 8 | 6 | 5 | 6 | 6 |
| CLI commands | 3 | 2 | 2 | 1 | 2 | 2 |
| CLI/test subprocess commands | 4 | 3 | 3 | 2 | 3 | 3 |
| Unique CLI catalog inputs | 6 | 6 | 10 | 10 | 10 | 10 |
| Coding-phase test commands | 1 | 1 | 1 | 1 | 1 | 1 |
| Failed test runs / implementation retry cycles | 0 | 0 | 0 | 0 | 0 | 0 |
| Successful edit batches | 1 | 1 | 1 | 1 | 1 | 1 |
| Failed file reads / navigation corrections | 1 | 1 | 0 | 0 | 0 | 0 |
| Elapsed seconds | 178.481 | 107.992 | 126.106 | 113.825 | 131.595 | 127.352 |
| Tool-execution seconds | 1.002 | 1.415 | 2.971 | 2.856 | 3.249 | 3.468 |

Observed differences: healing used two fewer operations, one fewer inspected
file and 70.489 fewer seconds; dependency used one fewer operation and 12.281
fewer seconds; motion used the same operation/file counts and 4.243 fewer
seconds. Both healing arms attempted to read an absent optional legacy-test
file, then recovered; those operations remain counted. All implementations
passed on their first test run. Agent-reported design corrections and complete
command/error histories remain in the per-arm reports and event logs.

Across tasks, top-level operations were **22 → 19** and CLI calls **7 → 5**.
Backend input counts were unchanged. Meter stdout character/byte counts are
available in `results.json` only as emitted-output measurements; they exclude
prompts, command text, wrappers, reasoning and any transport truncation. They
are not billed usage, tokens, complete model-visible context, or usage savings.

## Independent quality and information checks

The parent reran every frozen suite independently in normal Python, `python -O`
and `PYTHONOPTIMIZE=1`: **58/58 tests per workflow per mode**, 348 passing test
executions in total. This includes 14 unchanged legacy Sugar Rush assertions in
each dependency and motion arm. Only the import target was identically rebound
to the arm's implementation before freezing. No test was weakened or changed.
Manual review found no additional missed task constraint or legacy regression
within these fixtures. Passing tests do not establish complete coverage or
Minecraft runtime correctness.

The 18 existing V4 integrity tests also passed against the corrected committed
snapshot. A separate response audit found **no lost or upgraded UNKNOWN IDs
among 42 original unknown records**, including compact warning references. All
three V4 restoration fingerprints match the corresponding baseline internal V3
plans exactly. The required native sites, exact source pins, selected values and
dependency validation remain enforced upstream.

There is an important scope limit: Task 3 needs client-sound behavior that the
initial V4 literal-only profile lists as an informational `EXCLUDE`. That detail
is needed for the broader trace adapter. The B agent recognized the mismatch and
restored V3 **before editing**. Task 1 similarly restored broader behavior. No
required information remained missing at completion, and no runtime independence
or false runtime-exclusion claim was made. This does **not** establish that V4's
initial relevance buckets are sufficient for arbitrary coding tasks or have zero
task-level omission rates. V4 alone did not meet the information requirements of
those two broader tasks; restoration was part of the evaluated workflow.

## Interpretation and artifacts

The sample supports a modest observed reduction in navigation operations with
equivalent tested fixture behavior. It does not establish general adoption:
only two mechanics families are represented, all edit coordinates match authored
profiles, tests/specifications were available to implementers, and there is one
concurrent observation per task. Optional baseline verification choices and the
mandatory V3 fallbacks further limit attribution. Actual model usage is missing.
The final decision is therefore **INCONCLUSIVE**.

`manifest.json` records controls and initial hashes; `results.json` records each
arm's commands, workload, test results and limits; `safety-audit.json` records
UNKNOWN/restoration comparisons; `source-verification.json` and
`plan-preflight.json` record snapshot checks. Each `taskN/A` and `taskN/B` contains
the finished implementation, unchanged tests, metered JSONL events, raw command
outputs, evidence report and three independent test logs. `prepare.py`, `meter.py`
and `score.py` reproduce the fixture preparation, metering and scoring mechanics.
All artifacts remain local and ignored under this directory. Stop after this
evaluation; no V5, framework, architecture or mod research work was performed.
