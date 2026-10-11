# Task Preflight controlled A/B experiment

**Conclusion: the wrapper removed an evidence-selection decision, but this run does not establish a meaningful usage reduction.** B used 8 model-facing operations versus A's 10, yet both made two retrieval calls, and B emitted 23.4% more tool-output characters. Correctness matched. One controlled replication is reasonable; this result does not justify expansion or default adoption. No token or cost reduction is claimed.

## Task and frozen controls

The user approved the actual repository Sugar Rush offline-preview tool task: add independent frame previews and CLI `--frames-file` / `--upward-factor` support to `scripts/external-effects/examples/sugar_rush_workflow.py`, preserving existing APIs, demonstration output, source provenance, client/server branches and error behavior. This is a repository tooling change, not a Minecraft gameplay integration. Both solutions remain isolated experimental copies and were not applied to the working repository.

A and B started from **597 byte-identical files per arm**, including the actual module, specification, change request and test inputs. Base commit: `e0918e782355756f718a1adcff1f346a26230327`; branch: `feat/mod-intelligence-v1`. The existing uncommitted preflight wrapper was frozen at SHA-256 `2041ab5a639c7e2bc51bf69214451531551bd7638da43e6ada7df31794acff73`. V4 was identical throughout. Both agents were freshly dispatched with `gpt-6-astra`, `medium`, `fork_turns=none`; neither saw prior solutions, parent conversation or the other arm's output. Both ran concurrently.

A used the existing V4-first workflow, including its documented V1/V3 restoration when the requested implementation exceeds literal-only scope. A did not use Task Preflight. B started with Task Preflight; for this declared broader implementation it selects the existing **full V3 plan** rather than a literal-only V4 projection. B was allowed existing retrieval if needed. These are the actual current tool behaviors, not a redesigned V4 or an LLM router.

One shared meter controlled inspection, retrieval, edits and tests. Only the approved module could be edited. All frozen inputs, meter code, V4, wrapper and tests stayed unchanged during both runs. No parent repairs, mid-experiment optimization, source rescans or model escalation occurred. Preparation verified both initial evidence commands succeeded. Before implementation the 40-test suite failed only in the new acceptance module because the new API/CLI was absent.

## Results

| Metric | A: existing V4 workflow | B: preflight workflow |
| --- | ---: | ---: |
| Model-facing operations | 10 | 8 |
| Model-facing retrieval calls | 2 | 2 |
| Direct files inspected | 5 | 5 |
| Search operations | 1 | 0 |
| Coding-phase test commands | 2 | 1 |
| Failed test runs | 0 | 0 |
| Successful edit batches | 1 | 1 |
| Elapsed seconds | 82.601 | 77.5 |
| Tool execution seconds | 13.107 | 7.466 |
| Meter-emitted stdout characters | 100048 | 123464 |
| Frozen tests passed per independent mode | 40/40 | 40/40 |
| Implementation correction cycles | 0 | 0 |

The 40 tests comprise **25 existing workflow tests and 15 new, frozen acceptance tests**. Both implementations passed independent normal Python, `-O`, and `PYTHONOPTIMIZE=1` execution: 120 passing executions per arm, 240 total. A also ran the coding-phase suite twice (80 passing executions); B ran it once (40). No failed test run occurred. Both used a single edit batch.

Manual review and the frozen tests found no missed specified constraint or legacy regression. Both preserve X/Z and downward motion, native Slow Falling payload/flags, client sound markers, duration gates, ignored owner/amplifier/addEffect return, independent snapshots and existing APIs. Both reject finite-input movement overflow through WorkflowError and return CLI JSON errors. No-argument demonstration behavior and evidence provenance remain intact. This is not exhaustive edge-case or native runtime proof.

## What disappeared and what was added

A's V4 plan omitted client-sound behavior needed by the new preview API. A recognized this and issued V1 `get` with semantics, numbers and evidence. B's initial full plan already contained the needed behavior, so B made **no restoration decision or supplementary retrieval**. A performed one search; B performed none. Both inspected the same five direct files, and total emitted file-read content was identical (35,646 characters).

The expected one-call advantage was erased in execution: **B repeated preflight** because the first `functions.exec` call used the default outer output limit and truncated the large returned plan. Its second call increased the outer output budget. The nested shell budget alone did not prevent outer truncation. Both complete metered responses remain counted. This is a real delivery overhead, not a failed preflight or implementation correction.

A also repeated `meter test` after the first command returned an ongoing-session response, rather than resuming that session. Both completed test runs remain counted. These operational repeats differ between arms and strongly limit attribution: B's 77.500 seconds versus A's 82.601 seconds is only 5.101 seconds lower, while tool execution time differs by 5.641 seconds. The observed latency difference therefore does not demonstrate reduced model reasoning.

B adds a **4,431-byte task manifest**, file/hash checks, expected-source validation and a full plan upfront. The manifest was prepared by the evaluator from the shared task, tests and known pins. No B-agent operations were spent authoring it, but authoring is not free: its model/human cost was not captured. The logged sub-millisecond mechanical serialization time excludes authoring, harness preparation and preflight execution and must not be treated as total setup cost. Shared evaluator setup and independent scoring are excluded from coding-arm metrics for both arms.

## Context and usage

A emitted **100,048** tool-output characters; B emitted **123,464**, an observed **23.4% increase**. A's two evidence responses totaled 61,259 characters; B emitted its 43,801-character preflight twice, totaling 87,602. The wrapper could deliver the needed broader contract without an extra model decision, but this run paid for the duplicate delivery.

These are complete outputs captured by the meter, not exact model context: the first B response was truncated by the outer transport. Prompt text, command text, tool wrappers and internal reasoning are excluded. Complete context tokens, input/output/reasoning usage, billing and allowance telemetry are unavailable through the exposed tools. Thus **actual context-token growth and cost reduction cannot be determined**. No savings are inferred from byte or character counts.

Elapsed time runs from the first metered operation through finish completion, excluding agent startup and final-message rendering. Operation counts correspond to metered exec/shell calls, including the operational repeats. One concurrent observation per arm, visible tests, output-limit handling and asynchronous-session handling limit generalization.

## Continue or stop?

Continue only as a **small controlled replication**, not feature expansion or rollout. The functional mechanism worked: preflight supplied the broader evidence upfront and preserved tested quality. The measured retrieval-call reduction did not materialize, however, and total emitted output increased. A next experiment would need identical sufficient outer/inner output budgets, identical session-resume handling, and a recorded manifest-authoring cost before attributing differences to the wrapper. Those changes were not made during this experiment, and no additional run was launched.

The final preservation audit confirms that only the approved module changed in each isolated arm. Frozen tests, source evidence, wrapper and V4 hashes match their baselines. The real workspace has no tracked diff, and all preexisting uncommitted wrapper/example/documentation artifacts were preserved. No commit, push, production edit or canonical research change occurred.

Artifacts: `manifest.json` contains frozen hashes and setup details; `results.json` contains measured events and independent checks; `comparison.json` records the decision and limits; `preservation-audit.json` records immutable inputs. Each `task1/A` and `task1/B` retains the actual repository module implementation, metered events, full raw outputs, evidence report and three independent validation logs. The experiment is complete and stopped.
