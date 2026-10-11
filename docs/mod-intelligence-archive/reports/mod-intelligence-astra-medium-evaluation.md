# Astra Medium versus Sol Extra High with Mod Intelligence V4

**Recommendation: Inconclusive.** Astra matched the frozen benchmark's tested quality and completed the three tasks faster in this sample. Actual token usage, billing and complete model-context telemetry are unavailable, so the result does not establish a better quality/cost tradeoff or justify a general recommendation for complex work.

Repository: pooofeeee/TNO-Tensura-Compat. Branch: feat/mod-intelligence-v1. Frozen commit: `e0918e782355756f718a1adcff1f346a26230327`.

## Controlled comparison

This compares the completed Astra Medium runs against the **successful V4 B arms** from the previous Sol benchmark. Comparing against the previous V3 A arms would confound model capability with workflow. Both groups begin with V4 Adaptive Plans and may restore V3/V1 evidence when required.

The saved Astra manifest requests `gpt-6-astra` with `medium` reasoning in fresh contexts, with no prior solutions in prompts. Completed agent reports record no reasoning escalation. The previous benchmark inherited its model/effort; its exact runtime identifiers were not exposed. “Sol Extra High” is the user's identification, not independently attested usage metadata. The available tool catalog exposes no applicable model-usage telemetry endpoint.

The source snapshot, initial solutions, requests, task specifications, tests and acceptance criteria were hash-locked to the prior experiment. Independent final scoring verified all frozen inputs except the permitted solution edits unchanged. The metering code is unchanged; the copied scorer only restricts its arm loop to B. No solutions were repaired during scoring. Original benchmark artifacts were not modified.

## Quality

| Task | Astra Medium | Sol Extra High | Review |
| --- | ---: | ---: | --- |
| Ordered local-healing previews | 11/11 | 11/11 | Preserved old healing default, admission/maraca/remainder/breaded behavior, health bounds and independent snapshots. Both restored V3. |
| Sugar Rush dependency requests | 23/23 | 23/23 | Preserved float32 coupling, refresh-only duration, retained modifier fields, query gates, exact Citadel pins and existing APIs. V4 sufficed for both. |
| Sugar Rush motion frames | 24/24 | 24/24 | Preserved server/client and duration branches, downward motion, Slow Falling payload, sound marker and existing APIs. Astra restored V1 semantics; Sol restored V3. |

Independent Astra reruns passed **58/58 in each of normal Python, `python -O`, and `PYTHONOPTIMIZE=1`**, totaling 174 test executions. These use the identical frozen acceptance and legacy suites; Sol's saved independent results also pass all 174 executions. Both Sugar Rush tasks include the 14 unchanged legacy workflow tests. Frozen tests are visible to implementers.

All three Astra coding-phase suites passed on the first run, as did Sol's. Both had zero failed test runs, zero test-driven implementation correction cycles, and one edit batch per task. Manual inspection against the unchanged specifications found no additional missed constraint or legacy regression within the fixture scope. This is not exhaustive edge-case or Minecraft runtime proof. Agent reports retain exact evidence pins, unresolved impact limits and the distinction between proposed policy values and verified native behavior. Local JARs were not rescanned.

Astra's reported pre-test design adjustments included boolean admission normalization and deep-copy ownership. The Sugar Rush implementations repointed the historical fixture CLI path to the new byte-identical frozen source export. These are recorded in agent reports, not hidden retries. Sol's task 1 had one failed optional-file read and a navigation recovery; Astra had no failed operation.

## Efficiency

Values are Astra / Sol. Elapsed time uses the same definition: first metered operation start through finish completion, including thinking and tool waits but excluding startup and final response rendering.

| Measure | Task 1 | Task 2 | Task 3 | Sum |
| --- | ---: | ---: | ---: | ---: |
| Metered tool operations | 7 / 8 | 5 / 5 | 6 / 6 | 18 / 19 |
| Direct files inspected | 4 / 5 | 5 / 5 | 5 / 5 | 14 / 15 |
| CLI calls | 2 / 2 | 1 / 1 | 2 / 2 | 5 / 5 |
| Elapsed seconds | 57.641 / 107.992 | 55.450 / 113.825 | 76.303 / 127.352 | 189.394 / 349.169 |
| Tool execution seconds | 1.437 / 1.415 | 3.040 / 2.856 | 3.293 / 3.468 | 7.770 / 7.739 |
| Failed operations | 0 / 1 | 0 / 0 | 0 / 0 | 0 / 1 |
| Failed tests / implementation retries | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| Emitted stdout characters | 34,584 / 43,499 | 65,433 / 65,421 | 60,566 / 92,387 | 160,583 / 201,307 |

Astra used one search; Sol used none. Unique backend catalog inputs per task were identical (6, 10, 10). Direct file counts exclude backend catalog reads and search results; they are sums across isolated task contexts. Every coding-arm meter operation corresponds to one exec tool call and nested shell call under the shared protocol. Parent preparation, review and scoring operations are excluded for both groups. Agents reported no unmetered calls.

The summed task elapsed time was **45.76% lower** for Astra. These sums are not total experiment wall-clock time. There was one observation per task/model, with concurrent scheduling and stochastic choices; the difference is observational, not a stable speed guarantee. The original Sol experiment's discarded setup-contaminated attempt remains preserved and excluded from this successful-run comparison, as documented in its report.

Complete model-context size, input/output/reasoning token counts, billed cost and allowance usage are **unavailable**. Meter stdout is only a partial output-volume measurement, excluding prompts, command text, wrappers, reasoning and possible transport truncation. No usage or cost savings are inferred from characters or bytes. Different restoration choices also account for output-size differences.

## Preservation and conclusion

The preservation audit checked **856 prior artifacts** unchanged, **591 exported source files** identical to the prior export, and **3,256 committed source/catalog files** identical to the requested commit. There is no tracked diff. The preexisting untracked `scripts/external-effects/examples/sugar_rush_change.json` was left untouched. No Mod Intelligence, canonical research, production or frozen benchmark definition was changed; only new ignored evaluation outputs were written.

Astra is promising for latency on these three static fixture tasks with equal observed quality. The requested broader quality/cost decision remains **Inconclusive** because usage/cost is unmeasured, baseline runtime identity is not independently exposed, and the sample is small. No effort escalation or additional benchmark cycle was performed. Stop after this evaluation.

Artifacts: `comparison.json` contains the side-by-side machine-readable metrics; `results.json` contains Astra per-task scoring; `preservation-audit.json` records integrity checks; each `taskN/B` retains its solution, evidence report, original events and three independent validation logs. The earlier Sol report and results remain unchanged in the adjacent `mod-intelligence-real-coding-benchmark` directory.
