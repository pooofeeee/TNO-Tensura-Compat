# Mod Intelligence V1

Read verified mod mechanics from the existing external-effects catalog during coding tasks. The CLI is read-only: it reuses `catalog_common` and the existing `EvidenceIndex` witness resolver. It never extracts a JAR, rebuilds a census, regenerates research, or writes catalog views.

Requires Python 3.11 or newer and the checked-out catalog. No package installation, Minecraft, or Gradle is needed. Run from the repository root; the script also resolves the default catalog correctly from another working directory.

```sh
python3 scripts/external-effects/mod_intelligence.py mods
python3 scripts/external-effects/mod_intelligence.py search "anaconda strangle" --mod alexsmobs --limit 3
python3 scripts/external-effects/mod_intelligence.py get alexsmobs:anaconda_native_bite_strangle --mod alexsmobs --expect-version 1.22.17
python3 scripts/external-effects/mod_intelligence.py dependencies alexsmobs
python3 scripts/external-effects/mod_intelligence.py verify alexsmobs --jar /path/to/alexsmobs-1.22.17.jar
python3 scripts/external-effects/mod_intelligence.py verify citadel --expect-version 2.7.6
```

For a small coding context, search first and retrieve an exact ID with only the needed sections:

```sh
python3 scripts/external-effects/mod_intelligence.py get alexsmobs:anaconda_native_bite_strangle --mod alexsmobs --section numbers --section evidence
```

`get` sections are `semantics`, `numbers`, `evidence`, and `dependencies`; omit `--section` to include all. Witness and numeric-binding checks always run, even when evidence is omitted from the output. `get` includes a compact dependency summary; `dependencies` returns the recorded contracts and evidence references for each obligation. Source-version flags on either command refer to the target mod. Use `verify citadel --jar ...` to check the dependency artifact itself.

All ordinary responses are one compact JSON object followed by a newline. Use `--pretty` before the command for indented JSON, or `--catalog DIRECTORY` before the command to select another existing catalog. `--help` prints normal CLI help. Errors also produce a JSON object, without partial mechanic results.

| Command | Result |
| --- | --- |
| `mods` | All inventoried targets, completion state, semantic availability, source filename, hash, and declared versions. Reference-only and unstarted scopes remain visible. |
| `search QUERY` | Case-insensitive AND search across IDs, names, recorded behavior, registry IDs, classifications, components, numeric labels/values, and implementation class/method names. Completed semantic reviews only. |
| `get ID` | Exact canonical mechanic or explicit semantic alias, full behavior and gates, original numeric values/formulas/units, candidate consumers, delivery links, facts, and selected source evidence. |
| `dependencies MOD` | Original metadata dependency ranges, plus exact installed artifacts and resolved obligations where the canonical review records them. |
| `dependencies MOD --mechanic ID [--obligation ID]` | Only recorded obligations required by this mechanic, with resolved dependency witness identities, available hashes, and validation state. |
| `verify ARTIFACT` | Catalog source identity and optional expected-version, expected-hash, or local-artifact checks for an inventoried mod or dependency. |

Search defaults to 10 summaries, accepts `--limit 1..100` and `--offset N`, and reports `total` and `has_more`. Ordering is stable by mod key and mechanic ID. Each summary is limited to 240 characters and marks truncation; full semantics come from `get`. Filters include `--mod`, `--classification`, and `--primitive`. Empty search results are a successful query with `total: 0`, not proof that a mod has no such mechanic. `bossesrise` and `bomd` are accepted aliases for the corresponding inventory mod keys.

## Selected dependency contracts

```sh
python3 scripts/external-effects/mod_intelligence.py dependencies alexscaves \
  --mechanic alexscaves:sugar_rush \
  --obligation alexscaves:citadel:sugar_rush_tick_controller \
  --expect-version 2.0.10 \
  --expect-dependency-version 2.7.6 \
  --expect-dependency-sha256 9e12468c49e5a95b7adbf22b3b4d05bc55565989b89c40b985cd73bdfe63c3c2
```

Omit `--obligation` to return all obligations explicitly mapped to the mechanic. Selection uses the mechanic's `external_dependency_contracts` and the obligations' `affected_mechanic_ids`, cross-checking their recorded file and artifact pins. It never infers a dependency from names, descriptions, or historical file citations. An unknown or unrelated obligation, absent mechanic mapping, unresolved obligation, or file-only evidence without witness identities fails with exit code `4`. Malformed or missing witness identities fail with code `2`; stale dependency versions, hashes, or witness JAR pins fail with code `3`.

The result retains the exact resolved `artifact`, including `exact_installed_version` and `sha256`, and adds `requested_mechanic`, canonical `mechanic_ids`, `required_obligation_ids`, and `dependency_source_check`. Each selected obligation includes its original status, contract, affected IDs (or `null` when not recorded), resolved `witnesses`, and `validation_state`. Witnesses contain the recorded class/resource identity, class/entry hash, selected method names/descriptors/code hashes, packet file/hash, and source-pin validation. Bytecode bodies are omitted.

Missing entry or method hashes stay `null` with `hash_status: MISSING`; the selector does not derive them. An obligation with such gaps reports `WITNESSES_RESOLVED_WITH_MISSING_HASHES`, otherwise `WITNESSES_RESOLVED`. These states describe static witness resolution, not runtime behavior. File-only citations are retained separately as `references` with `validation_state: REFERENCE_ONLY`; they are not opened or promoted to verified witness evidence.

`--expect-version`, `--expect-sha256`, and `--jar` still check the target mod. The separate `--expect-dependency-version` and `--expect-dependency-sha256` options check the selected dependency and require `--mechanic`. No dependency JAR is scanned or inspected; its local artifact remains `NOT_CHECKED`. Use `verify citadel --jar PATH` for the existing optional byte-hash check. Unselected `dependencies MOD` and `get` responses retain their previous behavior.

This selector requires an inventoried dependency artifact and explicit native dependency witnesses. Older records containing only broad module-level references remain available through unselected `dependencies`, but cannot supply an inferred mechanic contract. The catalog is not rewritten to fill missing mappings, identities, or hashes.

## Provenance and source checks

Every success uses schema `tno.mod_intelligence.v1`, includes `scope: STATIC_PINNED_CATALOG`, the catalog checkpoint, and an `inputs` manifest of the files actually read with SHA-256 hashes. Search loads canonical reviews without opening evidence packets or censuses. Exact retrieval opens only the selected implementation, shared-contract, native-resource, and numeric-consumer witnesses plus cited fact documents. Evidence includes packet and class hashes, method names/descriptors/code hashes, source pins, and numeric instruction offsets when available; bytecode bodies are omitted.

Completion comes from agreement between the ledger and canonical review. An unstarted mod or a completed reference-only scope without a semantic review cannot supply mechanics. Catalog baseline mismatches, missing facts/methods, broken delivery links, conflicting selected method hashes, detached numeric candidates, or changed numeric consumer sites fail the lookup. Supported numeric bindings must agree with component values and the actual literal instructions at their recorded offsets; an invocation offset alone does not prove its arguments. These checks also run with Python optimization enabled.

Native evidence requires a nonempty mod identity and valid JAR SHA-256, checked against the inventory when that artifact is inventoried. Vanilla packets require their version, client JAR, mappings and manifest pins plus raw class identity. Selected reference packets require their witness archive pin. Unknown evidence schemas fail retrieval. Alternative witnesses expose their validated packet pins as `PACKET_PIN_ONLY`; reference-file citations remain locators and are not a fresh audit of every referenced document.

Use `--expect-version VERSION` and/or `--expect-sha256 HASH` on `get`, `dependencies`, `verify`, or a mod-scoped `search`. These compare the requested source identity to the catalog. Version strings come from embedded metadata or an inventoried dependency version, preserving discrepancies such as Royal Variations declaring `2.0` inside a filename containing `2.0.4`. A hash is the decisive byte identity; equal version strings alone do not prove equal artifacts.

With `--jar PATH`, the CLI streams a SHA-256 hash of that local artifact and rejects different bytes. It does not parse or scan the artifact. Without `--jar`, `source_check.local_artifact` explicitly remains `NOT_CHECKED`; a matching expected version/hash does not claim that a local installation was examined. No network access occurs.

Original observations and formulas stay separate from integration decisions. Legacy string candidate labels retain their original unscoped meaning; the CLI does not invent a consumer mapping. Numeric candidates do not authorize scaling. Dependency declarations do not establish behavior, and absent obligation documents yield `NOT_RECORDED`, not a compatibility certification. All evidence remains static research; runtime behavior and future gameplay integration require the relevant coding task and validation.

| Exit code | Meaning |
| --- | --- |
| `0` | Successful lookup or query, including an empty search. |
| `2` | Invalid arguments or missing, malformed, or inconsistent catalog evidence. |
| `3` | Source version/hash or dependency artifact mismatch. |
| `4` | Unknown mechanic/artifact, unresolved mechanic, or unavailable completed semantic scope. |

Malformed structures and nonfinite contract numbers, including numeric overflow during JSON decoding, return an `ERROR` object with exit code `2`. Serialization errors also follow this protocol. Historical native packets contain 18 nonfinite JVM constants (14 infinities and four NaNs); the reader preserves those only as opaque tokens in literal instruction operands. They cannot serve as numeric parameters or literal numeric evidence. The original packet bytes and hashes remain unchanged.

## Targeted validation

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s scripts/external-effects -p test_mod_intelligence.py -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s scripts/external-effects -p 'test_mod_intelligence*.py' -q
PYTHONDONTWRITEBYTECODE=1 python3 -O -m unittest discover -s scripts/external-effects -p 'test_mod_intelligence*.py' -q
PYTHONDONTWRITEBYTECODE=1 PYTHONOPTIMIZE=1 python3 -m unittest discover -s scripts/external-effects -p 'test_mod_intelligence*.py' -q
```

Tests exercise actual retrieval from each existing completed semantic catalog, a pinned numeric consumer, a semantic alias, native resource evidence, and dependency/version metadata. Small temporary catalogs test pagination, hashes, descriptors, numeric offsets and values, malformed input, path boundaries, unchanged inputs, and invocation from another directory. They do not rerun mod extraction or research. V1 ends at this CLI; indexing services, new research, policy generation, and runtime integration are outside its scope.

The [coding workflow validation](mod-intelligence-workflow-validation.md) demonstrates a small Sugar Rush consumer of CLI JSON, its numeric and dependency behavior, stale-source rejection, targeted tests, and the minimum follow-up justified by that workflow.

### Astra V1 repair milestone

All five reported defects were independently reproduced against `58287e6c767e7dfd906e45e5f910d0c8cfe6eec0` before repair:

| Defect | Baseline reproduction | Repair and focused regression |
| --- | --- | --- |
| Nested numeric integrity | Sugar Rush component Y factor changed from `0.45` to `0.6` still returned `OK` with binding `0.45`. | Check component/binding/literal agreement. Test component-only corruption, coordinated component/binding corruption, and an invocation offset substituted for a literal. |
| Missing native source pin | Removing the native witness JAR hash returned `OK` with `PACKET_PIN_ONLY`. | Require native identity and JAR pins; test missing, empty and malformed pins, plus valid Vanilla/reference alternatives and missing alternative pins. |
| Disabled assertions | Conflicting `code_hex` failed normally but returned `OK` under `-O`. | Explicit resolver validation replaces assertions; test hash corruption and duplicate witnesses in normal, `-O`, and environment-optimized subprocesses. |
| Malformed/nonfinite inputs | Metadata `[null]` and a NaN component raised uncaught exceptions with empty stdout. | Validate consumed structures, finite JSON numbers and guarded serialization; test null objects, wrong containers, NaN, both infinities, overflow, and serialization failure. |
| Unqualified witness ID | A wrong explicit ID was ignored when the evidence file came from row references. | Validate IDs after either resolution path; test valid and wrong IDs through the resolver and CLI. |

Nine focused regression tests cover these repairs. The current 64 CLI and workflow tests, including the existing V1 and Sugar Rush suites, pass in normal Python, `python -O`, and `PYTHONOPTIMIZE=1`. All 2,867 mechanic retrieval results across the 14 completed semantic catalogs match the audited baseline exactly. Catalog files and source evidence are unchanged; no extraction or JAR rescan was performed.

The full compatibility check exposed four valid item-attribute records rejected by the initial repair's scalar-only handling. Item modifiers and recorded `DiggerItem`/`SwordItem` argument pairs now have separate validation. The argument-pair checks use explicit parameter roles, the recorded tier and invocation, and the immediately preceding damage/speed literal sites. Two additional regressions cover all four valid records and reject contradictory components, coordinated binding changes, invocation offsets substituted for literals, and incorrect roles.

The separate existing catalog integrity suite passes 13 of 14 tests. Its published-snapshot equality test fails because `catalog-integrity-audit.json` is already stale at the audited baseline. Replaying the original baseline auditor also reports a live `PASS` with a stale published snapshot. This repair leaves that canonical record unchanged. No reported V1 defect remains unresolved; legacy observations and static-evidence limits described above remain in force.

## V2.0 impact intelligence

V2.0 adds two commands to the same entrypoint. The original V1 commands and schema remain unchanged; the new commands return `tno.mod_intelligence.v2.0`. No planner, database service, MCP server, archive scan, production edit, or catalog migration is involved.

```sh
python3 -B scripts/external-effects/mod_intelligence.py impact alexscaves:sugar_rush --mod alexscaves --limit 3
python3 -B scripts/external-effects/mod_intelligence.py context alexscaves:sugar_rush --budget-bytes 65536
python3 -B scripts/external-effects/mod_intelligence.py context alexscaves:corrodent_bite_native_dig_light_fear --mod alexscaves
```

Both commands accept the existing `--expect-version`, `--expect-sha256`, and optional streaming `--jar` check. They also accept `--expect-dependency-version` and `--expect-dependency-sha256`; these require a recorded mechanic dependency and fail if that check cannot be supplied. Without local byte checks, `local_artifact` remains `NOT_CHECKED`.

`impact` reuses exact mechanic lookup, numeric-binding validation, and the dependency selector. It returns related methods and available hashes, original numeric components and formulas, consumers, dependency contracts, source locators, tests, evidence, boundaries, and immediate possible peers. Shared methods must resolve to the same evidence file, entry, and descriptor through `EvidenceIndex`, including unqualified references. Shared dependency relationships use recorded affected IDs. Names, similar values, and packet filenames alone never prove a relationship.

Every relationship carries `relationship` with one of `CONFIRMED_DEPENDENCY`, `EVIDENCE_BACKED_RELATIONSHIP`, `POSSIBLE_IMPACT`, or `UNKNOWN`. Possible peers include their evidence-backed reason and a condition: changing one mechanic does not imply changing a shared method or dependency. Peer comparison stays within the selected completed mod and does not infer call chains or runtime reachability. `--limit 1..100` and `--offset` bound and paginate peer output; reason truncation is explicit. Required root contracts, dependencies, tests, and unknowns are retained. Peer witness links are checked; peer contracts and numeric behavior are not re-evaluated.

`context` supplies verified behavior, full component gates/flags/units, original formulas, numeric consumers, dependency contracts, fixture tests, warnings, and provenance. It uses a fixed compact projection independent of the requested budget. Source locations and numeric consumers refer to `evidence` by `evidence_link`; evidence refers to `evidence_sources` by `source_id`, and consumer `method_ids`/parameter `method_id` resolve through `methods`. These tables retain exact class entries, witness IDs, file hashes, source pins and root method descriptors/hashes while avoiding repeated identities.

All dependency witnesses are validated before projection. Dependency-only method descriptors/hashes are available through each dependency's `retrieve` arguments; the compact package retains class evidence, method names, validation states, all missing-hash records, and an explicit projection warning. File-only historical references remain `UNKNOWN`/`REFERENCE_ONLY`. Original historical inspection labels are preserved alongside current dependency validation.

The default context budget is 65,536 UTF-8 bytes for the entire successful JSON response, including its newline. `--pretty` counts indentation too. A smaller budget never removes required content: failure returns JSON `ERROR`, exit `2`, and `budget.requested_bytes`/`budget.required_bytes`, without partial `data`. For example, a 20,000-byte Sugar Rush request cannot hold the complete package; increase the budget reported by the error. Error responses themselves are not constrained by that budget.

`mod_intelligence_links.json` is a small tooling-owned JSON index for the two existing validated fixtures. It pins the mod, canonical review, selected dependency inputs, and repository file contents. Mapped Python symbols are checked without importing or executing them. Changed pins/files fail with exit `3`; malformed mappings, missing files/symbols, and path escapes fail with exit `2`. `--links PATH` selects another index confined to the current repository. No canonical research record is rewritten to add mappings.

Mapped tests and editable source locations have scope `STATIC_CODING_FIXTURE` and execution `NOT_RUN`. They describe the Sugar Rush and animation examples, not native Minecraft coverage or production edit targets. Other literal-ID test references are `UNKNOWN` with `UNVERIFIED_ID_REFERENCE`; imported/indirect references are not resolved. External class entries remain read-only locators, and absent production mappings remain explicit unknowns.

Catalog provenance remains in the response's `inputs`; selected repository mapping/file fingerprints appear in `repository_inputs`, and discovered literal references carry their own file hashes. The commands read existing JSON and repository Python metadata only. The derived source/method maps are in memory; no persistent graph is required.

The focused `test_mod_intelligence_v2.py` suite covers relationships, false name/value/overload matches, both witness-resolution paths, missing evidence/hashes, pinned and stale mappings, path boundaries, original gates/units, stable pagination, source checks, and exact UTF-8 budget boundaries in compact and pretty output. Run it with the existing `test_mod_intelligence*.py` suite in normal Python, `python -O`, and `PYTHONOPTIMIZE=1`.

V2.0 validation: all **82 tests** (64 existing plus 18 new) pass in each Python mode, and all **2,867 V1 mechanic results** across 14 completed catalogs are unchanged. With both expected artifact version/hash pairs supplied, the Sugar Rush context is **52,805 bytes**, contains 24 root methods and 32 evidence entries, and retains its tick-controller contract; the full impact report has 106 methods and five conditional peer mechanics. The complete Corrodent context is **54,763 bytes** and retains both mapped dependencies. A 20,000-byte Sugar Rush request returns exit `2` with the exact required size. These are UTF-8 response measurements, not token, time, cost, or usage savings. Example JSON and test logs are reproducible, ignored outputs under `run/mod-intelligence-v2-validation/`.
