# Astra V1 five-defect repair validation

Audited baseline: `58287e6c767e7dfd906e45e5f910d0c8cfe6eec0`.
Revalidated committed implementation: `69a048abb7896ff42ea7354df91123109e3b71c5`.
Validation date: 2026-10-09.

The five repairs were already present when this repair request was resumed:
`fdaa24ac8ee3816f1ce609c8a5faf761833b856d` implements the integrity repairs,
and `a3145162e3b22e576fe216ef25482862ad5a6d2b` preserves the supported item-attribute
binding variants. This checkpoint records a fresh independent replay and
verification of those repairs. It adds no runtime feature or catalog change.
Later committed tooling and uncommitted planner work were preserved; the planner
changes were excluded from the committed-code validation and this checkpoint.

## Independent reproductions

The baseline CLI and shared resolver files were checked byte-for-byte against
the audited commit. Each replay constructs a fresh `Catalog`, mutates only its
in-memory input, and invokes the public CLI entrypoint with captured JSON output.
The original catalog files and evidence remain unchanged.

| Finding | Baseline reproduction | Repaired behavior |
| --- | --- | --- |
| 1. Nested numeric integrity | Change Sugar Rush `FORCED_MOVEMENT.downward_y_factor` from `0.45` to `0.6`, retaining its `0.45` native vector binding. `get --section numbers` returns `OK`. | Supported bindings require component, binding and actual literal-site agreement. Invocation operands cannot prove numeric arguments. The corruption returns JSON `ERROR`, exit `2`. |
| 2. Native source identity | Remove or empty the Sugar Rush native witness's `jar_sha256`. Evidence retrieval returns `OK`. | Native evidence requires a nonempty mod identity and valid JAR digest; known inventory pins must agree. Vanilla packets use their client JAR, mappings, manifest and class pins; selected references use archive pins. Both native corruptions return JSON `ERROR`, exit `2`. |
| 3. Assertions disabled | Replace `applyEffectTick.code_hex` with `00` while retaining its recorded code hash. Normal Python returns exit `2`, but both optimization modes return `OK`. | Resolver identity, uniqueness, method selection and code-hash checks use explicit runtime validation. All modes return JSON `ERROR`, exit `2`. |
| 4. Malformed/nonfinite input | Inventory metadata `[null]` raises uncaught `AttributeError`; a NaN component raises uncaught `ValueError` with empty stdout. | Consumed object/container shapes, finite contract numbers and serialization are validated. Both reproductions return JSON `ERROR`, exit `2`, with no partial data. |
| 5. Explicit witness ID | Remove the proof's explicit evidence file, resolve it through row references, and set `witness_id` to `WRONG`. Retrieval returns `OK`. | Explicit IDs are checked after both qualified and unqualified resolution. The corruption returns JSON `ERROR`, exit `2`. |

All seven corruption variants above were replayed against both revisions in
normal Python, `python -O`, and `PYTHONOPTIMIZE=1`. Every repaired replay returned
exit `2` and JSON status `ERROR`; none raised an uncaught exception. All five
reported findings were reproduced.

## Focused regressions in the repair commits

The repair commits added these nine tests to
[`test_mod_intelligence.py`](../scripts/external-effects/test_mod_intelligence.py):

- `test_nested_numeric_binding_requires_component_and_literal_agreement`
- `test_sugar_rush_vector_corruption_checks_the_argument_literals`
- `test_native_source_identity_is_required_and_vanilla_uses_its_own_pins`
- `test_runtime_hash_and_witness_validation_survives_optimization`
- `test_malformed_structures_and_nonfinite_numbers_follow_json_error_protocol`
- `test_explicit_witness_ids_are_checked_on_both_resolution_paths`
- `test_native_infinite_bytecode_constants_are_opaque_and_not_numeric_contracts`
- `test_native_item_attribute_variants_preserve_valid_retrieval`
- `test_item_attribute_arguments_require_component_roles_and_literal_sites`

These cover coordinated component/binding corruption, invocation sites supplied
as literals, missing binding values/consumers, missing/empty/malformed native and
alternative pins, duplicate witnesses, both witness-ID paths, malformed objects,
NaN/infinities/overflow, and guarded serialization. Item modifier and
`DiggerItem`/`SwordItem` argument-pair checks retain their distinct recorded roles
and literal sites. Legitimate historical nonfinite JVM constants remain opaque
instruction tokens and cannot be used as numeric contract evidence.

## Verification results

The committed implementation was exported separately from the dirty worktree.
All CLI and workflow tests ran against that export:

| Suite | Tests |
| --- | ---: |
| Existing V1 retrieval and integrity regressions | 39 |
| Sugar Rush coding workflow | 14 |
| Existing animation workflow | 11 |
| Existing V2.0 retrieval commands | 18 |
| Total | 82 |

All **82 tests passed** in each of normal Python, `python -O`, and
`PYTHONOPTIMIZE=1`. Commands:

```sh
python3 -B -m unittest discover -s scripts/external-effects -p 'test_mod_intelligence*.py' -q
python3 -B -O -m unittest discover -s scripts/external-effects -p 'test_mod_intelligence*.py' -q
PYTHONOPTIMIZE=1 python3 -B -m unittest discover -s scripts/external-effects -p 'test_mod_intelligence*.py' -q
```

A full read-only retrieval sweep produced **2,867 successful mechanic results
across 14 completed mods**, with **zero changed result hashes** against the
audited baseline. Canonical catalog files and production source have no changes
between the audited baseline and the revalidated implementation. No JAR scan,
research reconstruction, production edit, or new feature was performed.

The existing shared catalog-integrity suite passed **13 of 14 tests**. Its only
failure is a preexisting stale published snapshot comparison, documented in the
[V1 repair milestone](mod-intelligence-v1.md#astra-v1-repair-milestone).
A fresh run of the original baseline auditor returned live status `PASS` and
confirmed that its result also differs from the published snapshot. That
canonical snapshot is outside this repair scope and remains unchanged.
The five reported defects have no unresolved reproduction or regression failure;
the CLI's documented static-evidence and legacy-observation limits still apply.
