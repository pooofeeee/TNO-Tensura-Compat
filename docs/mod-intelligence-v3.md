# Mod Intelligence V3 Change Plan prototype

The `plan` command converts an explicit numeric change request into a bounded implementation plan. It reuses V1 witness/value validation, V2 impact retrieval, the existing compact context projection, dependency obligations, pinned fixture mappings, and optional pinned historical validation reports. It generates no code, interprets no intent prose, runs no tests, and performs no extraction or JAR scan.

```sh
python3 -B scripts/external-effects/mod_intelligence.py plan \
  --request scripts/external-effects/examples/change_requests/sugar_rush_movement.json \
  --expect-version 2.0.10 \
  --expect-sha256 6fad35bf07fcb977aaa32d3fe05bf122150c6a30ed16b057385040207a3b788f \
  --expect-dependency-version 2.7.6 \
  --expect-dependency-sha256 9e12468c49e5a95b7adbf22b3b4d05bc55565989b89c40b985cd73bdfe63c3c2
```

## Request and bounded scope

```json
{
  "target": "alexscaves:sugar_rush",
  "change_type": "modify movement multiplier",
  "requested_behavior": "Apply the proposed upward factor on the original ascending server branch",
  "parameter": {"primitive": "FORCED_MOVEMENT", "name": "upward_y_factor"},
  "proposed_value": 0.95,
  "constraints": ["Preserve X/Z, the descending branch and Slow Falling gates"]
}
```

`target`, `change_type`, and `requested_behavior` are required. The optional schema is `tno.mod_intelligence.change_request.v1`. Numeric changes require an exact `parameter` selector with `primitive` and `name`; ambiguous selectors also need `mechanic_id` or `component_index`. A proposed value requires a selector and must be a finite number. Caller constraints and requested future behavior always require review.

Supported change types are exactly `modify numeric parameter` and `modify movement multiplier`. The prototype handles six existing scalar literal-binding formats and native vector multiplication bindings; the latter type requires a `FORCED_MOVEMENT` parameter and a recorded vector-multiply binding. It does not infer a stronger boost from prose or choose an amount. A request with only the three required fields is accepted with `SELECTION_REQUIRED` and no edit location. Unsupported change types produce `UNSUPPORTED_CHANGE` with an explicit unknown, rather than an invented plan.

Only numeric values recorded in component `numerical_parameters` are selectable. Formula-only values, unsupported binding formats, missing method descriptors/hashes, missing class hashes, and absent consumer sites cannot supply an edit location. These limits do not weaken V1: all original contract validation runs first, even for omitted output. Corrupt evidence remains an error.

`--change-spec` aliases `--request`; `--mechanic` optionally cross-checks the request target. The earlier uncommitted `change_intent.v1` draft format is normalized using its explicit parameter selector; its prose remains uninterpreted. The original draft and intent were preserved in ignored recovery artifacts, and the existing intent file remains unchanged.

## Connected plan and classifications

Successful responses use `tno.mod_intelligence.v3`, the existing static-catalog scope, and the actual-input hash manifest. Seven item lists contain `mechanics`, `source_locations`, `preserved_constraints`, `dependencies`, `required_tests`, `patterns`, and `risks_and_questions`. Every planning item has one of these classifications:

| Classification | Meaning |
| --- | --- |
| `VERIFIED` | An existing recorded contract, validated literal site, source identity, dependency obligation, or pinned repository association/report. A recorded value does not imply that its exact consumer binding is known. |
| `REQUIRES_REVIEW` | A proposed edit, preservation obligation, acceptance scenario, conditional impact, caller requirement, or future behavior needing developer decisions. |
| `UNKNOWN` | Missing binding/mapping/coverage, unsupported scope, or insufficient evidence for impact/completeness. |

`reasoning_chain` connects the request to current mechanic items, a preservation obligation, proposed implementation locations, and validation obligations through item IDs. Each proposed edit depends on the exact literal-site item and preservation obligation. Each validation obligation references those edit/preservation items. This makes the output an actionable sequence instead of a related-file list. It never declares an implementation ready without review.

For Sugar Rush, the verified site is `SugarRushEffect.class#applyEffectTick`, with its exact descriptor/code hash and literal offset **51**, currently **0.85**. The invocation at offset **55** remains distinct from the literal. The proposed **0.95** substitution requires review. All six components, original gates/contracts/facts, numeric observations, and delivery records remain present. Other consumers in this method include the downward factor and Slow Falling duration/amplifier; the plan explicitly flags them and proposes regression checks. The resolved Citadel tick-controller obligation remains required by the whole mechanic, without claiming that the dependency needs an edit.

Generic validation obligations cover the selected value, recorded gate boundaries, unchanged parameters/effects, source identity, and existing plus new regressions. Vector plans add unchanged-axis and conditional directional-branch checks. Dependency plans add protocol/gate review. These are proposed requirements, not executed tests or certified coverage. Existing test references remain `NOT_RUN`; pinned historical reports remain `NOT_RERUN`/`HISTORICAL_REPORT_ONLY`. Unverified literal-ID references stay `UNKNOWN`.

Native class/offset locations are read-only evidence locators. The two mapped editable examples are static Python fixtures. Production source correspondence remains `UNKNOWN`; a developer must locate the equivalent expression before modifying code. Shared-method candidates are conditional review items. Dependency membership alone is not promoted into parameter-specific impact. Coupled parameters and repeated local reads require explicit review.

## Three examples and measurements

The requests are in `scripts/external-effects/examples/change_requests/`. Run each with `plan --request FILE`; use the appropriate source identity checks.

| Example | Result | V2 impact bytes | V2 context bytes | Plan bytes |
| --- | --- | ---: | ---: | ---: |
| `cockroach_heal.json` | One verified native healing literal: **5.0**, `onGetItem`. Proposed **6.0** requires review. Mechanic dependency mapping remains unknown. | 59,352 | 11,874 | 13,913 |
| `sugar_rush_movement.json` | One verified upward Y literal, two shared-consumer warnings, one resolved Citadel obligation. | 110,139 | 53,519 | 40,582 |
| `knightly_fortitude_uncertain.json` | Recorded armor coefficient **7**; no supported exact consumer binding, no asserted edit location, unknown dependency mapping. | 116,205 | 24,991 | 14,696 |

Sizes are compact UTF-8 CLI responses including the newline. Impact uses `--limit 100`, matching the engine's bounded candidate scan; context is a comparison projection, not a second retrieval inside the engine. Expected native versions are `1.22.17`, `2.0.10`, and `2.0` respectively. Sugar Rush also checks Citadel `2.7.6` and its exact digest. Local JAR artifacts remain `NOT_CHECKED`.

The plan omits **3 / 105 / 41** method-detail records respectively and **0 / 8 / 2** unselected numeric-consumer details. The three impact reports contain **82 / 5 / 13** broad peer candidates; none matches these selected literal methods, so no peer is asserted as affected. Omitted details are not proof of no impact. Peer comparisons stay within the same completed mod, with explicit uncertainty if the candidate/reason scan is incomplete.

Exact comparisons found **zero missing recorded constraint groups**: all root components, contract/gate/fact records, numeric observations, delivery records, and selected dependency contracts match the V2 context. This measures preservation of recorded inputs, not completeness of real-world constraints. The uncertain armor request exposes a missing literal binding, and two examples expose absent mechanic-level dependency mappings. No missing fact was filled by new research.

The focused false-positive probe returns **0 edges from 3 unrelated candidates**: another class, another packet, and another overload. Its exact-method positive control remains `REQUIRES_REVIEW`. This is not a global false-positive rate.

The machine-readable measurements, implementation fingerprints, source checks, and test results are recorded in `mod-intelligence-v3-measurements.json`. Full reproduction JSON and logs are ignored artifacts under `run/mod-intelligence-v3-validation/`.

## Validation, complexity, and limitations

Eighteen new tests cover connected plan IDs/classifications, constraint/dependency retention, ambiguous intent, unsupported changes, conditional peers, both evidence-resolution paths, missing bindings/hashes, literal corruption, coupled parameters, malformed/stale/escaping reports, malformed/nonfinite requests, source checks, exact UTF-8 budgets, and the three completed examples.

```sh
python3 -B -m unittest discover -s scripts/external-effects -p 'test_mod_intelligence*.py' -q
python3 -B -O -m unittest discover -s scripts/external-effects -p 'test_mod_intelligence*.py' -q
PYTHONOPTIMIZE=1 python3 -B -m unittest discover -s scripts/external-effects -p 'test_mod_intelligence*.py' -q
```

All **110 tests pass in each mode**, including V1 integrity, V2 impact/context, Sugar Rush, animation, and prototype suites. V1 retrieval and V2 context data for all three examples are identical to committed `10fffef4fa85cbfbcd71921f1eda8aee1103b0f5` under identical current repository inputs. Canonical research, native evidence, and production remain unchanged.

The new engine has **292 physical lines and four module-level functions**. CLI integration adds **43 lines and removes seven**, largely schema/command wiring and extracting the existing pure context projection. No package dependency, model call, framework, code generator, or test runner is added.

The default successful-response budget is **65,536 bytes**. A smaller `--budget-bytes` never discards required constraints: it returns JSON `ERROR`, exit `2`, with exact requested/required bytes and no partial data. Stale source/report pins exit `3`; unknown selectors/targets exit `4`. Malformed requests/evidence exit `2` through the existing JSON protocol.

This architecture can reduce repeated literal lookup and preservation/test bookkeeping for supported numeric changes. Significant Codex reasoning or usage savings have **not been measured**. The simple plan is larger than V2 context because it adds obligations and classifications. Behavior interpretation, value selection, non-independent formulas, cross-method effects, real source mapping, test completeness, and runtime validation still require developer reasoning. This milestone stops at the bounded prototype.
