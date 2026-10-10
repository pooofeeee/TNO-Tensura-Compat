# Mod Intelligence impact prototype

The existing V2.0 `impact` command retrieves the verified mechanic contract and its recorded links. This prototype also accepts an exact coding target through the existing pinned repository mappings. It reuses the V1 evidence resolver, source checks, dependency selector, and V2.0 impact representation. It adds no catalog research, JAR scans, persistent graph, package dependency, or production mapping.

```sh
python3 scripts/external-effects/mod_intelligence.py impact alexscaves:sugar_rush --mod alexscaves --limit 3 --expect-version 2.0.10
python3 scripts/external-effects/mod_intelligence.py impact alexscaves:corrodent_bite_native_dig_light_fear --mod alexscaves --limit 3
python3 scripts/external-effects/mod_intelligence.py impact royalvariations:knightly_fortitude --mod royalvariations --limit 3
python3 scripts/external-effects/mod_intelligence.py impact --target 'scripts/external-effects/examples/sugar_rush_workflow.py#SugarRush' --mod alexscaves --limit 3 --expect-version 2.0.10
```

Supply either a mechanic ID or `--target FILE#SYMBOL`. A target resolves only through an exact file/symbol association in `mod_intelligence_links.json`, or the existing repository-confined `--links` override. File names, mechanic names, and similar symbols do not establish an association. Ambiguous targets require an explicit mechanic ID. The selected mapping, source file, symbol, canonical review, catalog inputs, and artifact pins undergo the existing validation before a successful response. Mapping changes during resolution also fail. Errors use the existing JSON protocol: malformed inputs exit `2`, stale pins exit `3`, and unmapped or ambiguous targets exit `4`.

The response adds `coding_target` only when `--target` is used. It records the selected file/symbol, mapping/file hashes, scope, and verification relationship. The currently mapped targets are static Python coding fixtures; their `execution` remains `NOT_RUN`. They do not identify native Minecraft production edit locations. Mechanic-ID result data is unchanged in the three example comparisons.

## Evidence and uncertainty

`CONFIRMED_DEPENDENCY` and `EVIDENCE_BACKED_RELATIONSHIP` describe verified recorded relationships. `POSSIBLE_IMPACT` marks conditional neighbors sharing an exact recorded method identity or explicit dependency obligation. `UNKNOWN` records absent mappings, unverified test references, incomplete numeric binding coverage, runtime behavior, and transitive or cross-mod impact. These categories describe the evidence available, rather than predicting the effect of an arbitrary patch.

Methods retain their class entry, descriptor, evidence reference, available hashes, and roles. The root contract retains numeric components and their gates, units, consumers, delivery paths, dependency contracts, source locators, and test references. Tests named in a response are references, not assertions that they ran. Missing hashes and dependency mappings remain explicit gaps.

Peer selection uses file/class/method/descriptor identity or recorded obligation IDs. Matching names, values, descriptions, or overload names alone cannot create an edge. Registry initializers and shared dependency obligations can produce broad candidate sets. For example, Sugar Rush and Bubbled share a recorded registry `<clinit>`, while Corrodent and Caniac share the actor-animation-clock obligation; both remain `POSSIBLE_IMPACT`.

## Three completed mechanic examples

Measurements use compact JSON responses with `--limit 3`, including the trailing newline. The ignored validation snapshot starts at `697ad4df7b4ed70e6409c18419bce4ac2c93b2f3` and contains only this prototype's code and tests. Original mechanic-ID data was compared directly against that commit with identical test-discovery inputs.

| Mechanic | Recorded obligations | Root methods retained | Evidence links | Numeric components | Delivery paths | Conditional peers, returned / total | Response bytes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `alexscaves:sugar_rush` | 1: tick controller | 24 / 24 | 32 | 6 | 1 | 3 / 5 | 103,716 |
| `alexscaves:corrodent_bite_native_dig_light_fear` | 2: animation clock, selective collision | 81 / 81 | 20 | 5 | 1 | 3 / 24 | 86,268 |
| `royalvariations:knightly_fortitude` | 0 recorded; mapping `UNKNOWN` | 41 / 41 | 4 | 3 | 3 | 3 / 13 | 30,312 |

Including dependency methods, the reports contain 106, 123, and 41 methods respectively. They reference 5, 4, and 1 tests. These reference counts can change as repository tests change. The Sugar Rush coding-target response is 104,222 bytes and contains the same contract plus target provenance.

All cataloged root method identities were retained: zero missing and zero extra root methods in these comparisons. Numeric components, source-evidence identities, and delivery records match V1 retrieval. The two mapped mechanics retain exactly their recorded obligations. Knightly Fortitude's absent mechanic-level dependency mapping is a known missing relationship, not evidence of no dependencies. Completeness beyond recorded root contracts and selected immediate links is `UNKNOWN`.

A controlled negative probe supplied three unrelated candidates: the same method name in another class, the same class/method in another evidence packet, and another overload. It produced **0 edges out of 3 negative candidates**. This is a focused false-positive check, not an estimate of a global false-positive rate. Known registry and dependency neighbors are also checked by the regression suite.

## Validation and implementation size

`test_mod_intelligence_impact_prototype.py` adds ten tests covering exact target resolution and provenance, malformed/escaping/unmapped targets, stale pins, mapping drift, ambiguity, JSON CLI errors, native source-version checks, three dependency patterns, preservation of V1 contract data, and conditional neighbor/test labels. Existing V1 integrity, V2.0 impact/context, Sugar Rush, and animation workflow tests remain included.

```sh
python3 -B -m unittest discover -s scripts/external-effects -p 'test_mod_intelligence*.py'
python3 -B -O -m unittest discover -s scripts/external-effects -p 'test_mod_intelligence*.py'
PYTHONOPTIMIZE=1 python3 -B -m unittest discover -s scripts/external-effects -p 'test_mod_intelligence*.py'
```

All **92 tests pass in each mode** in the isolated snapshot. Existing source evidence and canonical records are unchanged. Reproduction JSON, measurements, and test logs are ignored artifacts under `run/mod-intelligence-impact-prototype/`.

The runtime delta is 54 net lines. Target resolution occupies 31 source lines and the reused impact method now occupies 174. The addition has no new dependency or framework. Required contract data remains untruncated; `--limit` bounds peers and reasons, so it does not impose a total output budget. The existing `context` command provides a smaller fixed projection and fails explicitly when its requested byte budget cannot hold the required data.

The main limitation is output size for broad root contracts and registry neighbors. The next justified improvement would be an exact method/component focus within a verified mechanic, retaining its required gates, source pins, and uncertainty labels. That would need separate validation and is not implemented here. Patch interpretation, runtime prediction, transitive dependency expansion, and new production mappings remain outside this prototype.
