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
