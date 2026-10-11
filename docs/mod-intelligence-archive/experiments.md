# Experiment and benchmark ledger

This ledger covers every available Mod Intelligence experiment directory and the
recorded design-analysis steps between them. [Artifact index](artifact-index.md)
links exact reports, manifests, complete responses, code, tests and logs. Counts
are snapshot-specific. Unless stated otherwise, coding tasks are static Python
fixtures/tools, not Minecraft runtime integrations. Bytes never imply tokens,
allowance or billing savings.

| ID | Experiment / evidence directory | Result and interpretation |
| --- | --- | --- |
| E01 | V1 Sugar Rush consumption: `mod-intelligence-validation` | 13 workflow + 22 V1 tests at the original milestone. CLI returns 65,778 bytes for get/dependencies/verify. Exposed coarse dependency selection and unresolved witness detail; justified the narrow selector. Optional local artifact checks hash bytes only. |
| E02 | Five-defect repair: `five-defect-repair-recheck`, `five-defect-repair-final-check` | Five findings / seven corruptions reproduced against `58287e6`, rejected safely after repair in normal/-O/environment modes. Original 82-test replay, later 128-test replay. 2,867 valid mechanic results across 14 completed mods unchanged. |
| E03 | V1.5 animation: `mod-intelligence-v15-validation` | Corrodent fixed-animation clock, 11 focused tests. Final search/get/selected-dependency responses 1,818 / 23,684 / 18,332 bytes. Cancelled Start does not stop local clock advance; equality expiration preserved. |
| E04 | V2.0: `mod-intelligence-v2-validation` | 82 tests per Python mode; 2,867 V1 results unchanged. Sugar Rush context 52,805 bytes and Corrodent 54,763 at this snapshot. Budget failure retains no partial success. |
| E05 | Simple manual/tool A/B: `mod-intelligence-ab-validation` | Fix mutable `slow_fall` alias in isolated Sugar Rush code. Initial 2/4 failures; both implementations pass 4/4 and end byte-identical. Tool arm inspects more artifacts and emits more context; no correctness advantage. Sequential, unblinded, same-agent pilot. |
| E06 | Complex manual/tool A/B: `mod-intelligence-complex-ab-validation` | Corrodent/Citadel event-aware two-module preview. Both pass 15/15 and three demonstration outputs match. Manual domain files 5→1, method windows 12→5, but full CLI output remains broad. Same-agent A-then-B learning prevents causal attribution. |
| E07 | Exact coding targets: `mod-intelligence-impact-prototype` | 10 new tests, 92 total per mode. Three mechanics retain all recorded root methods; three unrelated method candidates create zero edges. Fixture mappings only; no production mapper. |
| E08 | V3 plans: `mod-intelligence-v3-validation` | 18 final added tests, 110 total per mode. Three examples preserve all recorded constraint groups. Uncertain Knightly Fortitude exposes missing binding rather than inventing an edit. Preliminary focused logs predate final test counts. |
| E09 | V4 adaptive: `mod-intelligence-v4-validation` | 18 final added tests, 128 total per mode; 45 protected comparisons. Four example projections preserve targeted required fields. Three pinned profiles, not universal semantic relevance. Preliminary focused logs retained. |
| E10 | Fresh-context V3 versus V4 coding: `mod-intelligence-real-coding-benchmark` | Three tasks, six isolated agents. 58/58 per arm per mode. V3 operations 22, V4 19; V4 needs restoration for two tasks. Decision INCONCLUSIVE. Includes discarded setup attempt and failed standalone CLI authentication probe. |
| E11 | Astra Medium versus user-identified Sol Extra High: `mod-intelligence-astra-medium-evaluation` | Compare new Medium with successful prior V4 arms, not prior V3 arms. Both 58/58 per mode; calls 18 vs 19, summed seconds 189.394 vs 349.169. Cost/usage unmeasured; INCONCLUSIVE. Exact prior model identity not independently exposed. |
| E12 | Astra Medium versus Astra Extra High: `mod-intelligence-astra-effort-evaluation` | Both 58/58 per mode; calls 18 vs 21; summed seconds 189.394 vs 394.405. Medium sufficient for these tasks. Extra defensive checks outside frozen cases do not establish necessary higher effort. |
| E13 | Normal versus constrained Medium: `mod-intelligence-astra-economic-evaluation` | Both 58/58 per mode; calls 18 vs 18; seconds 189.394 vs 192.977. No demonstrated work reduction. Symmetric post-run probe finds raw OverflowError in constrained duration calculation versus WorkflowError in normal. Do not adopt as default based on this run. |
| E14 | Workflow analysis (conversation-derived, summarized below) | Scope reconciliation, not another retrieval engine, identified as repeated work. Model Router unsupported by results. Proposed explicit scope + deterministic preflight. No implementation during this analysis step. |
| E15 | Task Preflight implementation/replay: `task-preflight-experiment` | 12 focused tests + existing 128 = 140 per mode. Saved-task routing reduces calls 2/1/2 to 1/1/1. No fresh coding model run; no usage savings claimed. |
| E16 | Fresh Task Preflight A/B: `task-preflight-ab` | User-approved repository Sugar Rush API + CLI task. 40/40 per arm in all modes. Calls 10→8, retrievals 2→2, files 5→5. Output grows 23.4% because B repeats preflight after truncation. Inconclusive usage benefit; bounded replication only. |
| E17 | Archive cut-off validation: `verification/` in this archive | Fresh 140 tests pass normal/-O/PYTHONOPTIMIZE=1 on 2026-10-11. Archive hashes and immutable-source checks are separate from historical measurements. |

## Early pilots: useful observations, weak causal controls

The simple alias-repair pilot used baseline `697ad4d`, frozen oracle hash
`822ca442143681d25b8a49188f534ca06f077e6efbb7cff1f8ad5db5c5350317`, and equal
initial code. Without Tool inspected 3 repository files, made 1 search and emitted
8,724 rendered investigation bytes. With Tool inspected 2 repository files plus
2 response artifacts, made 1 search, emitted 20,578 rendered bytes and returned
151,919 full CLI bytes. Both passed 4/4; only A had one navigation correction.
The local bug did not require a large evidence package. Prior Sugar Rush
familiarity and sequential execution were explicitly disclosed.

The complex Corrodent pilot adds Start replacement/cancellation, Tick mutation,
client restart, strict native float range checks, independent hurt/knockback and
vehicle requests. A rough discovery note incorrectly mentioned healing; it was
corrected from canonical behavior **before** task/API/tests were frozen. The
15-test oracle hash is
`a0c390215284bd0feb68586b43a21b3dce8cdd92ac3a89bfd91f6425d2291a5b`.
A inspected 7 repository files, B 3 files plus 2 responses. B's bounded selected
output was 22,993 bytes versus A's 38,833 untruncated bounded bytes, but B's full
CLI return was 139,406 bytes. Neither is actual model-context telemetry. A had
one discovery-selection correction; B had one reader correction for legitimate
packets without `code_hex`. Neither recomputed nonexistent raw method hashes.
Both first implementations passed; B benefited from A's discoveries.

## V3/V4 projection measurements

V3's three published example plan sizes are 13,913 bytes (cockroach healing),
40,582 (Sugar Rush movement) and 14,696 (uncertain armor). These commands/snapshots
are not interchangeable with the later V4 comparison's transport and request
settings. The V4 comparison measured:

| Example | V3 bytes | V4 bytes | Reduction |
| --- | ---: | ---: | ---: |
| Cockroach healing | 12,470 | 12,210 | 2.09% |
| Sugar Rush movement | 39,140 | 20,431 | 47.80% |
| Sugar Rush dependency | 38,824 | 32,301 | 16.80% |
| Ambiguous Sugar Rush | 36,240 | 11,499 | 68.27% |

These are successful-response bytes, not model usage. Backend input counts
remain 6/10/10/10 because V4 retains full upstream validation. Ambiguity produces
a selection aid, not a sufficient implementation plan.

## Fresh-context coding benchmark and the discarded attempt

E10 tasks were ordered local-healing previews (11 tests), dependency request /
refresh behavior (23), and motion-frame preservation (24). Both workflows passed
58/58 in normal and both optimized modes, 348 independent executions across six
arms. No implementation retries or missed frozen constraint were detected.
V3/V4 files inspected sum to 16/15; operations 22/19; summed elapsed time
436.182/349.169 seconds. Both healing arms attempted an absent optional test file.
Full command lists and agent reports are preserved.

The first export omitted `docs/mod-intelligence-workflow-validation.md`, a pinned
input required by plans. Its **58 metered operations** were discarded as
setup-contaminated; one arm was interrupted. The missing document was restored
from the same commit, every initial plan preflighted, and all six tasks restarted
in fresh contexts. `discarded-attempt1/` remains inside the archived workspace.
It is not relabeled as successful, nor counted as a V4 implementation defect.
The standalone Codex CLI authentication probe failed; its diagnostic logs contain
no usable usage telemetry. Successful agents inherited a configuration later
identified by the user as Sol Extra High; runtime identifiers were not exposed.

## Model and prompt-workflow comparisons

The following are sums across the same three tasks, not whole-experiment wall
clock time. Each successful implementation passed the visible frozen tests on
its first test run. Saved Medium runs were reused in E12/E13; only comparison
arms were new. Single observations and scheduling prevent stable speed claims.

| Workflow | Operations | Direct files | Seconds | Frozen tests per mode |
| --- | ---: | ---: | ---: | ---: |
| Sol Extra High, user-identified V4 baseline | 19 | 15 | 349.169 | 58/58 |
| Astra Medium, normal | 18 | 14 | 189.394 | 58/58 |
| Astra Extra High | 21 | 14 | 394.405 | 58/58 |
| Astra Medium, constrained | 18 | 14 | 192.977 | 58/58 |

Extra High's additional searches included a broad search that hit the display
limit and was narrowed. The constrained workflow replaced a search with a failed
optional-file read. Its task 2 omitted duration-product overflow handling:
`request_preview(3600, request_multiplier=3e38)` raised raw OverflowError, while
normal Medium raised WorkflowError. That post-run symmetric probe did not modify
the frozen tests or retrospectively change 58/58 scores. It is a separately
recorded robustness regression, with no proof the prompt alone caused it.

## Preflight analysis, replay and actual A/B

E14 found that `choose_profile` matches mechanic and parameter, while broader
API/behavior requirements lived in separate task specifications. Two normal
Medium tasks needed extra evidence after their literal-only plan. A deterministic
manifest could carry declared scope, approved files, test commands, source pins
and questions; a new LLM router would add a decision without demonstrated benefit.
Expected removal of two round trips was a hypothesis, not a measured token saving.

E15 implemented that wrapper without modifying V4. The three saved broader tasks
receive full V3 in one call each; complete response sizes 14,425 / 42,105 / 42,076
bytes. Questions and unknown scope are not silently declared resolved. This was
routing replay against saved files, not evidence of better coding performance.

E16 then used **two new Astra Medium contexts** on the actual repository Sugar
Rush preview module. The shared task added `preview_frames`, `--frames-file`,
`--upward-factor`, JSON error handling and explicit overflow validation. Each arm
started with 597 byte-identical files and the same 25 existing + 15 new tests.
The initial 40-test run failed only because the new API/CLI was absent.

| Metric | A: existing V4 workflow | B: Task Preflight |
| --- | ---: | ---: |
| Model-facing operations | 10 | 8 |
| Retrieval calls | 2 | 2 |
| Direct files inspected | 5 | 5 |
| Coding-phase test commands | 2 | 1 |
| Elapsed seconds | 82.601 | 77.500 |
| Tool execution seconds | 13.107 | 7.466 |
| Meter-emitted characters | 100,048 | 123,464 |
| Independent tests per Python mode | 40/40 | 40/40 |

A restored client behavior via V1 and repeated its test after an ongoing-session
response. B needed no restoration, but repeated preflight after the default
outer tool-output budget truncated its first response. Both repeats count.
The 5.101-second elapsed difference is smaller than the 5.641-second tool-time
difference, so it does not demonstrate less model reasoning. B adds a prebuilt
4,431-byte manifest whose authoring cost was not measured. Actual delivered
context tokens remain unknown because of truncation. No tool, wrapper, tests or
acceptance criteria were optimized during this run. Neither experimental solution
was applied to the real module.
