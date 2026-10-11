# Astra Medium economic workflow evaluation

**Recommendation: Do not adopt this constrained workflow as the default based on this evaluation.** It did not reduce measured operations or direct file inspections, did not improve observed timing, and introduced one arithmetic-error handling regression outside the frozen test cases. Frozen acceptance quality was unchanged. Reasoning, complete context and billed usage reductions cannot be determined from the available telemetry.

Repository: pooofeeee/TNO-Tensura-Compat; branch: feat/mod-intelligence-v1; frozen commit: `e0918e782355756f718a1adcff1f346a26230327`.

## A/B design

A is the saved normal GPT-6 Astra Medium run for each of the same three tasks. B consists of three new fresh-context agents explicitly dispatched as `gpt-6-astra`, `medium`, `fork_turns=none`, with the user's authorization. The agents were not shown earlier solutions or parent conversation. The tasks, initial solutions, source snapshot, requests, tests and acceptance criteria match the original hashes. All three V4 plans passed preflight. No model/reasoning escalation occurred.

The B prompt adds the requested workflow: use Mod Intelligence and its change plan first; reuse verified information; restore evidence only for missing required facts, contradictions or validation failure; inspect only task/plan-required files; avoid speculative improvements and unnecessary defensive additions; preserve existing patterns with the smallest correct change; run required tests and verify constraints. Necessary specification, fixture edit target and test files remain permitted. Required validation and evidence limitations may not be omitted for brevity.

A already used V4 and targeted evidence restoration, so the incremental intervention is narrower than comparing against unrestricted research. A reads task inputs before its initial plan; B begins with the plan, then reads inputs. Both may restore V3/V1 when necessary. The same meter and scoring logic apply. Only B's isolated solution files were editable; no parent repairs were made.

This uses one saved normal run and one later constrained run per task, not randomized repeated trials. Both sets of agents ran concurrently in their respective rounds. Timing and individual implementation choices can vary independently of the workflow.

## Quality

| Task | Normal | Constrained | Review |
| --- | ---: | ---: | --- |
| 1. Local healing batch | 11/11 | 11/11 | Preserved legacy healing default, admission, maraca early return, remainder/breaded handling, health bounds and independent snapshots. |
| 2. Dependency request | 23/23 | 23/23 | Preserved float32 rate coupling, duration-only refresh, retained modifier fields, query/config/recipient gates and exact Citadel pins. Additional overflow-handling regression described below. |
| 3. Motion preservation | 24/24 | 24/24 | Preserved server/client/duration branches, original downward motion and Slow Falling payload, sound marker and legacy APIs. |

Independent B validation passed **58/58 in normal Python, 58/58 with `-O`, and 58/58 with `PYTHONOPTIMIZE=1`**: 174 test executions. A's saved independent validation has the same results. The Sugar Rush tasks each include the unchanged 14-test legacy workflow suite. All coding-phase suites passed on the first run under both workflows; both had one edit batch per task, zero failed tests and zero test-driven correction cycles. No frozen acceptance or legacy regression was detected. Tests were visible to implementers and do not establish exhaustive or Minecraft runtime correctness.

Manual review found a concrete robustness loss in B task 2. The symmetric post-run probe `request_preview(3600, request_multiplier=3e38)` supplies a valid fixture duration and finite float32-representable rate, but the duration product overflows float32. A catches this arithmetic failure and raises `WorkflowError`; B lets `OverflowError: cannot convert float infinity to integer` escape. B validates the rate but omits handling around the duration product and ceil operation.

This probe was applied to both completed solutions without modifying either implementation, the frozen tests, or their acceptance scores. It is a **separately reported robustness regression**, not a retrospective change from 58/58 to a different test score. The probe harness catches exceptions only to record their types; its zero process exit does not mean B handled the error. The original specification does not separately spell out duration-product overflow behavior, so this is not counted as a missed frozen preservation requirement. One observation does not prove the prompt caused the omission, but it prevents claiming unchanged robustness.

B also uses narrower built-in container/numeric type checks in some new paths than A. Those untested type-domain differences are not promoted into additional confirmed defects. No speculative feature additions were detected. Exact source evidence, dependency identities and unresolved impact limits remain in the agents' reports.

## Efficiency

Each cell is **normal / constrained**.

| Metric | Task 1 | Task 2 | Task 3 | Sum |
| --- | ---: | ---: | ---: | ---: |
| Metered operations | 7 / 7 | 5 / 5 | 6 / 6 | 18 / 18 |
| Direct files inspected | 4 / 4 | 5 / 5 | 5 / 5 | 14 / 14 |
| CLI calls | 2 / 2 | 1 / 1 | 2 / 2 | 5 / 5 |
| Searches | 1 / 0 | 0 / 0 | 0 / 0 | 1 / 0 |
| Failed operations | 0 / 1 | 0 / 0 | 0 / 0 | 0 / 1 |
| Elapsed seconds | 57.641 / 59.08 | 55.45 / 63.05 | 76.303 / 70.847 | 189.394 / 192.977 |
| Tool execution seconds | 1.437 / 1.492 | 3.04 / 2.941 | 3.293 / 3.663 | 7.77 / 8.096 |
| Emitted stdout characters | 34584 / 33547 | 65433 / 65445 | 60566 / 92415 | 160583 / 191407 |

The workflow used **18 operations and 14 direct files under both conditions**. Five CLI calls and backend catalog inputs (6, 10, 10 per task) were also unchanged. Summed elapsed time was **189.394 seconds normal versus 192.977 seconds constrained**, about 1.9% higher; this small difference is not evidence of a systematic slowdown or speedup. Elapsed time covers first metered operation through finish completion, excluding agent startup and final-message rendering. These are sums of task durations, not total experiment wall-clock time.

A performed one search. B performed none, but task 1 attempted to read an absent optional `test_legacy.py`, producing one failed operation and navigation correction. All operations remain counted. No agent reported unmetered tool calls. Parent setup, independent scoring and review are excluded consistently.

Both workflows restored V3 for task 1 because the required batch/preservation contract exceeds the selected-literal profile. Neither restored evidence for task 2. Task 3's omitted client-sound branch required restoration: A selected V1 semantics; B selected the larger V3 plan. This is a justified evidence reopening under the constrained rules, not rediscovery. It also explains much of B's larger emitted output. All B runs began with the plan and read only their task inputs plus justified catalog retrievals; the failed optional test read was unnecessary navigation.

Meter stdout totals were **160,583 characters normal versus 191,407 constrained**. These are partial output-volume measurements, not complete model context. They exclude initial prompts, command text, wrappers, internal reasoning and transport effects. No applicable usage telemetry is exposed: tokens, reasoning-token usage, billed cost, allowance usage and full context size are unavailable. **No usage savings or costs are inferred from bytes or characters.** Unnecessary internal reasoning cannot be measured from elapsed time alone.

## Default-workflow decision

The benchmark does **not demonstrate a reduction in unnecessary work**: direct activity stayed the same, an avoidable failed read remained, and emitted output increased because of a broader restoration choice. Frozen quality stayed equal, while manual review exposed weaker arithmetic-error handling. The guardrails may be useful as guidance, but this result does not justify replacing the normal Astra workflow with the constrained rules as a default. In particular, arithmetic boundary validation should not be discarded merely to minimize defensive code. No workflow or product changes were made as part of this recommendation.

## Preservation and artifacts

Final checks found all 656 normal Medium artifacts, 660 Extra High evaluation artifacts and 856 original benchmark artifacts unchanged. All 591 exported source files and the meter match the normal setup. Initial inputs and final frozen files match the locked hashes. HEAD remains the requested commit, with no tracked diff. The preexisting untracked `scripts/external-effects/examples/sugar_rush_change.json` was preserved. Mod Intelligence, production, canonical research and frozen benchmark definitions were not modified; no new features, mod research, JAR rescans, commits or pushes occurred.

`comparison.json` records both arms and the decision; `results.json` records B scoring; `manual-overflow-review.json` records the symmetric review probe; `preservation-audit.json` records integrity checks; `manifest.json` records controls and workflow deltas. Each `taskN/B` retains its implementation, unchanged tests, raw events, evidence report and three independent validation logs. All new artifacts are local ignored evaluation outputs. Stop after this evaluation.
