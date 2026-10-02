# Compact external Stage integration manifest

Generate from exactly the nine completed review JSONs at `external-effects-catalog-research`:

```bash
git fetch --no-tags origin refs/heads/external-effects-catalog-research:refs/remotes/origin/external-effects-catalog-research
python3 scripts/external-stage/extract_manifest.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s scripts/external-stage -p test_extract_manifest.py -v
```

Python's standard library is sufficient. The extractor reads the allowlisted paths with `git show` at one resolved commit. It never checks out/merges the archive, discovers additional files, or reads JARs. The manifest records its source ref, commit, and nine review paths. `--ref <commit>` allows extraction from a pinned snapshot; `--output <path>` supports comparisons without replacing the committed manifest.

Each mechanic retains its source `mod_key` and `id` (renamed `mechanic_id`). Optional fields stay absent/null. The older `scalable_parameters` field is copied as `scalable_parameter_candidates`; its contents are observations, not approved eligibility or formulas. Components retain only `primitive`, `attribute`, `operation`, `formula`, and `coefficient`. Explicit `numerical_parameters.coefficient` supplies a missing coefficient; an explicit `numerical_parameters.formula` takes precedence over a prose component formula. No values are inferred from names or parsed from formula prose.

Short vanilla-difference/formula prose is retained with whitespace normalized. Longer prose becomes an extractive first sentence or word-boundary prefix, limited to 240 characters and marked `…`. Vanilla differences are normalized to a flat list in source order; structured component contracts supply only their explicit `native_relation` strings. Null remains null. Full native audit details, witnesses and reference-file lists remain in the cold reviews. These excerpts are navigation aids; exact implementation facts still require the specific source review/evidence.

Records are sorted by `(mod_key, mechanic_id)` and emitted as one compact JSON record per line. Duplicate source identities and incomplete reviews are rejected. `stage_review_bucket` follows only the fixed classification mapping in the extractor; it does not approve Stage eligibility, native gates, or balance values. No production parameter is registered by this manifest.

## Stage candidate matrix

Generate the smaller candidate matrix using only the committed integration manifest:

```bash
python3 scripts/external-stage/extract_candidate_matrix.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s scripts/external-stage -p test_extract_candidate_matrix.py -v
```

This generator does not access Git refs, research files, or JARs. It retains only mechanics with non-empty `scalable_parameter_candidates`. Structured candidates retain their exact primitive/parameter mappings and other supplied fields, with `candidate_form: STRUCTURED` and `needs_mapping_review: false`. Legacy strings become `candidate_name` entries with `candidate_form: LEGACY_UNSCOPED`, `needs_mapping_review: true`, and a sorted list of available component primitives; that list supplies context without assigning an owner. Structured-only mechanics retain components whose primitives match explicitly; mechanics containing legacy names retain all source components as review context. Optional context stays absent/null.

The deterministic summary counts structured candidate objects separately from their parameter entries, and counts each legacy name as one candidate. It lists unique structured `(primitive, parameter)` pairs. Counts by mod and review bucket count candidate-bearing mechanics. Records, components, candidate groups, parameters, and unique pairs are sorted; `--output <path>` supports byte comparisons. The matrix chooses no Stage eligibility, formulas, caps, or policies.
