# Task preflight experiment

`scripts/external-effects/task_preflight.py` validates caller-supplied task scope
before selecting an existing Mod Intelligence planner. It makes no model calls,
changes no V4 code, edits no files, executes no test commands and rescans no JARs.

```sh
python3 -B scripts/external-effects/task_preflight.py \
  --manifest scripts/external-effects/examples/task_manifests/sugar_rush_literal.json
```

The sibling `sugar_rush_request.json` demonstrates a broader implementation task;
`sugar_rush_questions.json` demonstrates an unresolved task (exit 4). These are
static Python fixture examples, not instructions to edit production or proof of
test coverage for a future implementation.

## Manifest format

The manifest is strict JSON with schema `tno.task_manifest.v1`. Unknown fields,
duplicate keys, nonfinite numbers and manifests exceeding 65,536 bytes fail.
All fields below are required. Paths are relative to `--root` (the repository by
default); absolute paths, traversal and symlinks escaping that root fail.

| Field | Meaning |
| --- | --- |
| `task_type` | `local_behavior`, `dependency_related`, or `preservation_behavior`; descriptive, not an inferred complexity or model choice. |
| `scope` | `{ "kind": "literal_only" or "broader_implementation", "description": "…" }`. The description carries broader implementation requirements; routing uses the explicit kind, never prose inference. |
| `change_request` | `{ "file": "…", "sha256": "…" }` pointing to an existing V3/V4 change request. |
| `approved_edit_targets` | Nonempty array of `{ "file": "…", "sha256": "…" }` baseline files the caller approves for editing. |
| `required_tests` | Nonempty array of `{ "file": "…", "sha256": "…", "command": ["python3", "…"] }`. Commands are argument arrays to run from the root; preflight reports them but does not execute or certify them. |
| `sources` | Required `native` and optional `dependency`, each `{ "mod": "…", "version": "…", "sha256": "…" }`. A recorded plan dependency requires an expected dependency identity before the task is usable. |
| `unresolved_questions` | Array of blocking questions; use `[]` when none are known. Existing planner UNKNOWNs remain separate and preserved. |

Arrays have at most 32 entries and text fields at most 4,096 characters. Digests
are lowercase SHA-256. Required test files cannot also be edit targets. Existing
files are required: creating new target files is outside this experiment.

Populate expectations from an approved baseline/installation record. Rehashing a
changed file without review defeats the baseline check. Catalog identity matching
does not check installed JAR bytes. Caller-declared approval and scope do not
prove native-to-repository correspondence; fixture mappings remain fixture-only.

## Deterministic routes

1. Validate all files, baseline hashes, source expectations and the existing
   structured change request.
2. `literal_only` with no blocking questions invokes V4 once. Only an applicable
   pinned profile with planner readiness `REVIEW_REQUIRED` produces
   `SUPPORTED_LITERAL_EDIT`.
3. Broader work, or a task with explicit blocking questions, invokes full V3
   directly. Broader work with usable planner readiness produces
   `BROADER_IMPLEMENTATION`; it never first requests a literal-only projection.
4. Blocking questions, missing dependency expectations, unresolved parameter/site
   selection, or no applicable adaptive profile produce
   `REQUIRES_ADDITIONAL_EVIDENCE`. There is no guessed edit or model escalation.

Each successful retrieval returns `task`, `checks`, `route` and the **complete**
selected `evidence_plan`. The task brief is compact; evidence is not summarized
away. All existing evidence validation, source/dependency checks, preservation
requirements and UNKNOWNs remain active. No shell commands are run from manifest
text. Test status is always `NOT_RUN`; `OK` means preflight checks passed, not
implementation approval or verified future correctness.

Output schema is `tno.task_preflight.v1`, one JSON object on stdout. Exit 0 means
`OK`; exit 4 with `NEEDS_EVIDENCE` retains the task and plan for resolution.
Invalid/unavailable input uses `ERROR`, exit 2; stale pins use exit 3. Upstream
catalog errors retain their nonzero codes. The default output budget is 131,072
UTF-8 bytes; `--budget-bytes` can raise it. Insufficient budgets return an error
with required/requested sizes, never a truncated plan. Runtime checks remain
active under optimized Python.

## What this experiment removes

The earlier Medium benchmark required follow-up evidence retrieval for two of
three tasks because the coding specifications exceeded the numeric requests'
literal-only scope. Declaring that broader scope upfront selects full V3 in the
first wrapper invocation. The model no longer has to discover that mismatch,
select a restoration command and reconcile two responses. Missing files and stale
pins are detected before coding. The wrapper does not automate implementation
reasoning, invent acceptance requirements, or remove arithmetic-boundary checks.

Full V3 may be larger than V4 plus a narrowly targeted supplement. Eliminating a
model round trip therefore does not establish token or cost savings. The wrapper
supports the existing bounded numeric request types, one native identity and at
most one expected dependency identity. It does not infer whether a caller's
`literal_only` declaration is truthful or that all required tests are listed.

## Validation and usage measurement

```sh
python3 -B -m unittest discover -s scripts/external-effects -p 'test_task_preflight.py' -q
python3 -B -m unittest discover -s scripts/external-effects -p 'test_mod_intelligence*.py' -q
```

Repeat both commands with `-O` and with `PYTHONOPTIMIZE=1`. The wrapper regressions
compare returned V3/V4 plans with direct planner output and reject malformed
manifests, stale file/source pins, missing files, path escapes, missing dependency
expectations, upstream witness corruption and insufficient output budgets.

For a future Astra A/B run, freeze the same tasks, code, tests and acceptance
criteria; compare direct V4/restoration with one manifest-based preflight. Include
manifest preparation in total workflow cost. Record model-facing retrieval
decisions, calls, files, retries and elapsed time separately from backend calls.
Keep the overflow boundary found in the workflow audit in the quality evaluation
for both arms. Use actual input/output/reasoning-token and cost telemetry when
available; otherwise report usage impact as unmeasured, never infer it from bytes.
No new model benchmark is part of this implementation milestone.

## Experiment results

The existing 128 Mod Intelligence tests plus 12 new preflight tests passed in
normal Python, `-O`, and `PYTHONOPTIMIZE=1` (140 per mode). The focused preflight
suite was repeated in all three modes after the final provenance-envelope change.

A read-only routing replay used the three saved Medium task specifications,
requests, tests and completed fixture files as pinned inputs; it did not run new
coding agents or edit those artifacts. All three specifications describe broader
implementation work, so each received full V3 in one preflight call. Earlier
model-facing retrieval counts were 2 / 1 / 2; the replay used 1 / 1 / 1. Thus the
wrapper removes two follow-up retrieval decisions in this setup (5 calls to 3),
without demonstrating a model-usage reduction. Complete response sizes were
14,425 / 42,105 / 42,076 bytes; these are not token or cost measurements.

The ignored `run/task-preflight-experiment/routing-results.json` records that
replay alongside its manifests and complete outputs. Required questions,
validation coverage and future implementation correctness remain review work.
