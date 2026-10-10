# Mod Intelligence V4 adaptive prototype

V4 adds `plan --adaptive` to the existing CLI. It projects a fully validated V3 plan using three pinned literal-edit scope profiles. V1 retrieval, V2 impact, V3 planning, source checks, dependency checks, and witness validation remain active. The default `plan` command still returns unchanged V3 data.

```sh
python3 -B scripts/external-effects/mod_intelligence.py plan --adaptive \
  --request scripts/external-effects/examples/change_requests/sugar_rush_movement.json \
  --mod alexscaves --expect-version 2.0.10 \
  --expect-sha256 6fad35bf07fcb977aaa32d3fe05bf122150c6a30ed16b057385040207a3b788f \
  --expect-dependency-version 2.7.6 \
  --expect-dependency-sha256 9e12468c49e5a95b7adbf22b3b4d05bc55565989b89c40b985cd73bdfe63c3c2
```

Successful adaptive responses use `tno.mod_intelligence.v4`. Input schemas and the existing JSON error protocol are unchanged. The 65,536-byte default successful-response budget remains enforced; a smaller budget fails with exact required/requested bytes and no partial data, rather than dropping required information.

## Relevance and evidence

`information` partitions items into four buckets. Each item has a `relevance` tag; the V3 `classification` still distinguishes verified current facts from proposed actions requiring review.

| Relevance | Meaning |
| --- | --- |
| `REQUIRED` | Information needed under the selected literal-edit profile: current value/site, specified gates/components, preservation and validation obligations, dependency information, and source evidence. |
| `CONTEXT` | Recoverable broader information whose complete body is unnecessary for this declared edit scope. Default output contains V3 item/field references. |
| `EXCLUDE` | Informational detail outside the pinned edit footprint, empty records, or explicitly scoped historical/comparison metadata. It does not certify absence of runtime effects. |
| `UNKNOWN` | Unresolved scope, source correspondence, coverage, binding gaps, or effects requiring investigation. Dynamic warnings remain intact. |

Selection uses explicit component indices, contract JSON pointers, literal coordinates, and extractive quotes from existing verified records. It does not search descriptions, class names, actor names, sound names, or rendering names to guess relevance. Gate fields named `rendering` and component fields named `sounds` remain required in the regression fixture when their structure makes them required.

`mod_intelligence_scope_profiles.json` contains three tooling-owned profiles. Each pins every catalog input used by its authored V3 scope and the exact class, method, descriptor, code hash, and literal site. Profiles are authored scope rules over existing evidence, not automatic discovery of semantic independence. Stale pins/site identities fail with exit `3`. Malformed profiles, escapes, incomplete component partitions, selected/shared-consumer demotion, and explicit dependency-contract demotion fail before output. The permitted historical/comparison exclusions cannot classify behavioral gates as `EXCLUDE`.

The profiles assume **only the selected numeric literal changes**, with control flow, other inputs, and dependency code preserved. Proposed edits still require developer review. Broader changes require the full V3 plan. `scope.sufficiency` is `PINNED_SCOPE_ONLY`, not a proof of a global minimum or runtime independence; `excluded_runtime_impact` remains `NOT_PROVEN`.

## Required information in the examples

- **Local healing:** preserves the healing literal **5.0** at `onGetItem` offset **50**, the component, maraca branch, crafting remainder, food/breed-tag admission, and native max/death/return rules. The unrelated breaded-AI implementation description is outside the declared literal edit. Dependency mapping remains unknown.
- **Sugar Rush movement:** preserves the upward literal **0.85** at offset **51**, its separate consumer offset **55**, vector X/Z **1.0**, downward factor **0.45**, Slow Falling duration/amplifier/flags, server/duration/Y-sign gates, ownership/return/lifecycle constraints, source pins, and validation steps. It returns no client-sound implementation body. The existing Citadel obligation's identity, status, source check, gaps, and retrieval command remain required; its broader contract is recoverable context because dependency code is outside this profile's edit footprint. This does not prove the movement change has no indirect clock effects.
- **Sugar Rush controller request:** preserves the float **2.0** at offset **181**, its store/reads at **182/196/201**, request at **202**, both coupled duration/controller uses, component protocol data, complete root binary gates, complete Citadel contract, and dependency evidence. The explicit component dependency prevents identity-only projection.
- **Ambiguous movement boost:** preserves the request, complete parameter candidates, questions, source identities, and proposed validation steps. It asserts no edit and no `EXCLUDE` item. Broader facts are deferred as context until a parameter is selected; sufficiency is `NOT_ESTABLISHED`.

Required plan IDs remain connected through `reasoning_chain`. Preservation dependencies are rewritten to the scoped required records; implementation and validation nodes still reference their required source/preservation nodes. Existing mapped tests are associations with execution `NOT_RUN`, not proof that they cover a future change. Unknown literal-ID references are compact unresolved references.

Ten fixed V3 diagnostic topics are summarized once in an `UNVERIFIED_BOUNDARIES` item with their original restoration IDs. Runtime, transitive/cross-mod, numeric-binding, test-coverage, production-mapping, peer, and projection limits remain explicit. Task-specific errors/gaps and warnings carrying additional fields are never bundled away. Repeated requested-behavior/constraint text is replaced with pointers to the unchanged request.

## Measurements and regression results

Compact UTF-8 CLI sizes include the newline. Both arms use identical requests, mod filters, expected native version/hash, and, for Sugar Rush, expected Citadel version/hash. Context/exclusion bodies are omitted from V4; scope rules and restoration references remain.

| Example | V3 bytes | V4 bytes | Reduction | Required probes | Lost required information | False exclusions in targeted checks |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Cockroach healing | 12,470 | 12,210 | 2.09% | 7 | 0 | 0 |
| Sugar Rush movement | 39,140 | 20,431 | 47.80% | 17 | 0 | 0 |
| Sugar Rush dependency | 38,824 | 32,301 | 16.80% | 13 | 0 | 0 |
| Ambiguous Sugar Rush | 36,240 | 11,499 | 68.27% | 8 | 0 | 0 |

Independent required-field oracles check **45 protected comparisons**, including literal/binding records, component values/flags, gate values, native source checks, repository/request pins, dependency identities/contracts, coupled uses, and ambiguity handling. Separate negative tests reject unsafe exclusion/demotion rules before output. Zero losses/exclusions are limited to these cases and tests; they are not global recall or false-exclusion rates. Deferred context is not counted as proven irrelevant.

Eighteen new tests exercise scope integrity, source corruption, names carrying required semantics, references, warning preservation, JSON errors, budgets, and the four example oracles. All **128 Mod Intelligence tests pass** in normal Python, `python -O`, and `PYTHONOPTIMIZE=1`, including the existing V1/V2/V3 and coding-workflow suites:

```sh
python3 -B -m unittest discover -s scripts/external-effects -p 'test_mod_intelligence*.py' -q
python3 -B -O -m unittest discover -s scripts/external-effects -p 'test_mod_intelligence*.py' -q
PYTHONOPTIMIZE=1 python3 -B -m unittest discover -s scripts/external-effects -p 'test_mod_intelligence*.py' -q
```

The four default V3 plans are byte-structure identical to committed `804c6a30d1b9b0eb054b2e8ee13c626553b7796c` under the same current repository inputs. Native evidence, canonical research, production, and the earlier untracked intent remain unchanged.

`mod-intelligence-v4-measurements.json` records sizes, protected probes, implementation fingerprints, test modes, and limits. Full V3/V4 JSON, the measurement runner, and logs are ignored artifacts under `run/mod-intelligence-v4-validation/`.

## Restoration and limits

Run the same request through `plan` **without** `--adaptive` to restore the full V3 body. Item IDs and JSON pointers in `CONTEXT`, `EXCLUDE`, and `UNKNOWN` references locate their original data. Quoted exclusions reference the source behavior field and the pinned profile's exact quote. `restore.v3_plan_fingerprint` covers the internal V3 plan before CLI-added `source_check` and `intent_input`; omit those two transport fields when checking a restored CLI data object's fingerprint. Required evidence tables retain class/source identities; full dependency mode retains all dependency evidence links.

The engine adds **237 lines**, three finite profiles, and a small CLI wrapper. It makes no model calls, adds no package dependency, and generates no code. Backend catalog reads remain **6 / 10 / 10 / 10 files**, identical to V3 in these runs: full upstream validation is intentionally retained. The reduction is in returned information, not backend extraction or research work.

The small healing plan is only slightly smaller; metadata overhead limits its gain. Unprofiled concrete changes retain full V3 constraints conservatively and may grow. Ambiguous responses are smaller selection aids, not sufficient implementation plans. Profile authoring/maintenance, indirect effects, real source mapping, and complete test coverage remain manual concerns. No Codex usage savings have been measured or claimed. This milestone stops at the bounded V4 prototype.
