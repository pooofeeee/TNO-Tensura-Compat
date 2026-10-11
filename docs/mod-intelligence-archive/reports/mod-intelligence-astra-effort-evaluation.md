# Astra Medium versus Astra Extra High

**Decision: Astra Medium sufficient for these three medium-complexity tasks.** Extra High produced no improvement in frozen test outcomes, detected preservation constraints, regressions or correction cycles. Its summed task time was about 2.08 times Medium's, with 21 versus 18 metered operations. This supports Medium as the default for this measured workload, not a universal claim about harder coding tasks. Cost remains unmeasured.

Repository: pooofeeee/TNO-Tensura-Compat; branch: feat/mod-intelligence-v1; frozen commit: `e0918e782355756f718a1adcff1f346a26230327`.

## Controls and method

A uses the completed GPT-6 Astra Medium runs from `mod-intelligence-astra-medium-evaluation`. B uses three new isolated agents explicitly dispatched with `model=gpt-6-astra`, `reasoning_effort=xhigh`, and `fork_turns=none`, one per task. The user explicitly authorized these agents. No prior solutions or parent conversation were included in their task prompts, and no agent received another arm's implementation. No reasoning escalation occurred during a run. Model/effort labels are the requested execution configurations, not billing telemetry.

All initial implementations, specifications, requests, tests and acceptance criteria match the prior hash-locked benchmark. The repository state, exported source, source pins and metering code are identical. Each agent begins with the same V4 Adaptive Plan, with V3/V1 restoration allowed when the scoped projection omits facts needed by the adapter task. All three V4 requests passed preflight. Tests were available to implementers, unchanged throughout execution. Only each new arm's `solution.py` could be edited. Parent review made no repairs.

Medium runs were reused rather than repeated. This is a controlled input comparison with one observation per task/effort, not a randomized or repeated statistical timing study. New Extra High agents ran concurrently; previous Medium agents also ran concurrently. Different execution times and scheduling can affect latency.

## Quality and correctness

| Task | Medium | Extra High | Preservation review |
| --- | ---: | ---: | --- |
| 1. Local healing batch behavior | 11/11 | 11/11 | Old single-call default, food-or-tag admission, maraca early return, remainder/breaded handling, health bounds and isolated ordered snapshots preserved. |
| 2. Dependency-related request behavior | 23/23 | 23/23 | Exact Citadel pins, float32 rate/duration coupling, duration-only refresh, retained fields and strict query/config/recipient gates preserved. |
| 3. Motion change with preservation constraints | 24/24 | 24/24 | Server/client/duration branches, original downward motion, Slow Falling payload, sound marker, snapshot isolation and legacy APIs preserved. |

Independent Extra High validation passed **58/58 in normal Python, 58/58 with `-O`, and 58/58 with `PYTHONOPTIMIZE=1`**: 174 passing test executions. The completed Medium runs have the same independently verified results. Task 2 and task 3 each include the unchanged 14-test legacy Sugar Rush workflow suite. The frozen tests and acceptance criteria were not extended or weakened for either side.

Both efforts passed all coding-phase tests on the first run. Both used one implementation edit batch per task, zero test-driven correction cycles, zero implementation retries and zero failed operations. Manual review found no missed preservation constraint or legacy regression within the frozen fixture scope. Full edge-case correctness and Minecraft runtime behavior are not established by this benchmark.

Manual review also found extra defensive checks in Extra High task 1 for malformed outer item collections and numeric conversion overflow, and explicit bytearray rejection in task 3. These differences were outside the frozen test cases. They were not used to add tests, redefine acceptance, or claim a measured quality score improvement. They are a limited robustness observation, not evidence that Extra High is necessary for the specified tasks.

Task 1 restored V3 under both efforts. Task 2 used the adaptive plan without restoration under both. Task 3 restored V1 semantics under Medium and full V3 under Extra High for the client sound branch. Both recognized the adaptive scope limit and retained dependency, evidence and unresolved-impact constraints. No informational exclusion was promoted into proof of runtime independence. Agent reports preserve the distinction between proposed fixture policy and verified native behavior; no local JAR scans or Minecraft execution occurred.

## Efficiency

Each cell is **Medium / Extra High**.

| Metric | Task 1 | Task 2 | Task 3 | Sum |
| --- | ---: | ---: | ---: | ---: |
| Metered operations | 7 / 9 | 5 / 6 | 6 / 6 | 18 / 21 |
| Direct files inspected | 4 / 4 | 5 / 5 | 5 / 5 | 14 / 14 |
| CLI calls | 2 / 2 | 1 / 1 | 2 / 2 | 5 / 5 |
| Searches | 1 / 3 | 0 / 0 | 0 / 0 | 1 / 3 |
| Failed operations | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| Failed test runs | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| Elapsed seconds | 57.641 / 147.774 | 55.45 / 118.442 | 76.303 / 128.189 | 189.394 / 394.405 |
| Tool execution seconds | 1.437 / 1.482 | 3.04 / 2.941 | 3.293 / 3.611 | 7.77 / 8.034 |
| Emitted stdout characters | 34584 / 57012 | 65433 / 65433 | 60566 / 92401 | 160583 / 214846 |

Metered operations count the same protocol's exec calls and nested shell calls. File counts are direct unique inspections per task, summed across separate contexts; search results and backend catalog reads are separate. CLI calls total five for each effort; backend catalog inputs are 6, 10 and 10 per task for both. No agent reported unmetered tool calls. Parent preparation, scoring and review are excluded consistently.

Elapsed time starts at the first metered operation and ends after meter finish, including thinking/tool waits but excluding agent startup and final reply rendering. The totals are sums of individual task durations, not overall experiment wall-clock time. Extra High's 394.405 seconds versus Medium's 189.394 seconds is an observed 2.08-times duration, not a general latency guarantee.

Extra High task 1 performed a broad search whose output exceeded the meter display limit, then narrowed it with two additional searches. This is a navigation recovery, not a failed test or implementation correction; all operations remain counted. Extra High task 2 used an additional file-read operation. Medium had no limited search output. Different restoration choices also affected response volume.

Token counts, reasoning-token usage, billed cost, allowance usage and full model-context size are unavailable through the exposed telemetry. Emitted stdout characters and raw bytes are retained only as output-volume measurements. They exclude prompts, command text, wrappers, reasoning and transport effects; **no cost or usage savings are inferred from them**.

## Preservation and artifacts

The final audit confirms 656 existing Medium artifacts and 856 original Sol benchmark artifacts unchanged, 591 exported source files identical, unchanged meter code, and no tracked repository diff. The preexisting untracked `scripts/external-effects/examples/sugar_rush_change.json` was preserved. Canonical research, production, Mod Intelligence and frozen benchmark definitions were not modified. New implementations, logs and reports remain in this ignored evaluation directory; no commit or push was needed or performed.

`comparison.json` records both efforts side by side; `results.json` contains Extra High scoring; `manifest.json` records initial hashes and dispatch settings; `preservation-audit.json` records integrity checks. Each `taskN/B` contains its implementation, unchanged tests, evidence report, metered operations and independent validation logs. The preserved Medium results remain in the adjacent `mod-intelligence-astra-medium-evaluation` directory.

Stop after this benchmark. Extra High is not justified by the measured outcomes of these three tasks; harder tasks, repeated trials and cost telemetry would be needed to support a broader decision.
