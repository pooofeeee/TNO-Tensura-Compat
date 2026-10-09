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
| `verify ARTIFACT` | Catalog source identity and optional expected-version, expected-hash, or local-artifact checks for an inventoried mod or dependency. |

Search defaults to 10 summaries, accepts `--limit 1..100` and `--offset N`, and reports `total` and `has_more`. Ordering is stable by mod key and mechanic ID. Each summary is limited to 240 characters and marks truncation; full semantics come from `get`. Filters include `--mod`, `--classification`, and `--primitive`. Empty search results are a successful query with `total: 0`, not proof that a mod has no such mechanic. `bossesrise` and `bomd` are accepted aliases for the corresponding inventory mod keys.

## Provenance and source checks

Every success uses schema `tno.mod_intelligence.v1`, includes `scope: STATIC_PINNED_CATALOG`, the catalog checkpoint, and an `inputs` manifest of the files actually read with SHA-256 hashes. Search loads canonical reviews without opening evidence packets or censuses. Exact retrieval opens only the selected implementation, shared-contract, native-resource, and numeric-consumer witnesses plus cited fact documents. Evidence includes packet and class hashes, method names/descriptors/code hashes, source pins, and numeric instruction offsets when available; bytecode bodies are omitted.

Completion comes from agreement between the ledger and canonical review. An unstarted mod or a completed reference-only scope without a semantic review cannot supply mechanics. Catalog baseline mismatches, missing facts/methods, broken delivery links, conflicting selected method hashes, detached numeric candidates, or changed numeric consumer sites fail the lookup. Native witness JAR hashes are checked against the inventory when that artifact is inventoried. Other witnesses expose their packet pins as `PACKET_PIN_ONLY`; reference-file citations remain locators and are not a fresh audit of every referenced document.

Use `--expect-version VERSION` and/or `--expect-sha256 HASH` on `get`, `dependencies`, `verify`, or a mod-scoped `search`. These compare the requested source identity to the catalog. Version strings come from embedded metadata or an inventoried dependency version, preserving discrepancies such as Royal Variations declaring `2.0` inside a filename containing `2.0.4`. A hash is the decisive byte identity; equal version strings alone do not prove equal artifacts.

With `--jar PATH`, the CLI streams a SHA-256 hash of that local artifact and rejects different bytes. It does not parse or scan the artifact. Without `--jar`, `source_check.local_artifact` explicitly remains `NOT_CHECKED`; a matching expected version/hash does not claim that a local installation was examined. No network access occurs.

Original observations and formulas stay separate from integration decisions. Legacy string candidate labels retain their original unscoped meaning; the CLI does not invent a consumer mapping. Numeric candidates do not authorize scaling. Dependency declarations do not establish behavior, and absent obligation documents yield `NOT_RECORDED`, not a compatibility certification. All evidence remains static research; runtime behavior and future gameplay integration require the relevant coding task and validation.

| Exit code | Meaning |
| --- | --- |
| `0` | Successful lookup or query, including an empty search. |
| `2` | Invalid arguments or missing, malformed, or inconsistent catalog evidence. |
| `3` | Source version/hash or dependency artifact mismatch. |
| `4` | Unknown mechanic/artifact, unresolved mechanic, or unavailable completed semantic scope. |

## Targeted validation

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s scripts/external-effects -p test_mod_intelligence.py -v
```

Tests exercise actual retrieval from each existing completed semantic catalog, a pinned numeric consumer, a semantic alias, native resource evidence, and dependency/version metadata. Small temporary catalogs test pagination, hashes, descriptors, numeric offsets and values, malformed input, path boundaries, unchanged inputs, and invocation from another directory. They do not rerun mod extraction or research. V1 ends at this CLI; indexing services, new research, policy generation, and runtime integration are outside its scope.
