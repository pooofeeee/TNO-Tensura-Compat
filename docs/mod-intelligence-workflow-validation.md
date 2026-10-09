# Mod Intelligence V1 coding workflow validation

Validated on 2026-10-09 from tooling commit `1e8c8ce7c1c2ff6df9d107963f46745b07e3971f`, on `feat/mod-intelligence-v1`. The concrete consumer is [sugar_rush_workflow.py](../scripts/external-effects/examples/sugar_rush_workflow.py); its [targeted tests](../scripts/external-effects/test_mod_intelligence_workflow.py) exercise the CLI process boundary.

The completed `alexscaves:sugar_rush` contract was chosen because it combines numeric motion, amplifier-dependent attributes, and a resolved Citadel tick-controller dependency. This is a static coding fixture using existing verified contracts. It does not execute Minecraft or certify runtime behavior.

## Reproduce the workflow

```sh
python3 -B scripts/external-effects/mod_intelligence.py search "sugar rush" --mod alexscaves --limit 4
python3 -B scripts/external-effects/mod_intelligence.py get alexscaves:sugar_rush --mod alexscaves --expect-version 2.0.10 --section semantics --section numbers --section evidence
python3 -B scripts/external-effects/mod_intelligence.py dependencies alexscaves --expect-version 2.0.10
python3 -B scripts/external-effects/mod_intelligence.py verify citadel --expect-version 2.7.6
python3 -B scripts/external-effects/examples/sugar_rush_workflow.py
```

The example calls `get`, `dependencies`, and `verify` as subprocesses, checks both exact version/hash pairs, and consumes their JSON responses. It never imports the catalog API or opens research documents itself. Values come from the returned components and dependency obligation; only source pins and the fixture's input scenarios are fixed in the consumer. Nine numeric-site citations retain file hashes and method descriptors/code hashes. Evidence joins include file, class, method, descriptor, and offset: the regular and long potion factory methods both use offset 20, so an offset-only join is insufficient.

| Artifact | Exact version | SHA-256 |
| --- | --- | --- |
| AlexCaves | `2.0.10` | `6fad35bf07fcb977aaa32d3fe05bf122150c6a30ed16b057385040207a3b788f` |
| Citadel | `2.7.6` | `9e12468c49e5a95b7adbf22b3b4d05bc55565989b89c40b985cd73bdfe63c3c2` |

Both available local artifacts also passed streaming byte-hash checks through the CLI. To repeat that check against your own paths:

```sh
python3 -B scripts/external-effects/examples/sugar_rush_workflow.py --mod-jar /path/to/alexscaves-2.0.10.jar --dependency-jar /path/to/citadel-1.21.1-2.7.6.jar
```

Without these options, the output explicitly retains `local_artifact: NOT_CHECKED`. The example prints its source checks, actual input fingerprints, numeric-site citations, dependency evidence locators, and measured CLI response bytes. Generated demonstration outputs from this validation are under the ignored `run/mod-intelligence-validation/` directory; they are reproducible output, not new catalog records.

## Demonstrated behavior

| Input or boundary | Fixture result |
| --- | --- |
| Amplifier 0 / 1 | Native attribute amounts `0.25` / `0.5`, using the retrieved coefficient and `amplifier + 1`. |
| Server motion `(1, 2, 3)` | `(1, 1.7, 3)`, preserving X/Z and using upward factor `0.85`. |
| Server motion `(1, -2, 3)` | `(1, -0.9, 3)` with a Slow Falling request of duration `10`, amplifier `0`, and three false flags when absent. |
| Client, expired effect, non-descending Y, or existing Slow Falling | Original client/expired motion retained; no additional Slow Falling request in these cases. |
| One valid local modifier at distance 9, regular duration 1800 | Radius `10`, multiplier `2`, supplied maximum duration `3600`, client expiry at master tick `1800`, client query `200 ms`, server query `50 ms`. |
| Native Player speed RETURN `0.1`, active client query | Client speed approximately `0.3`, flying RETURN approximately `0.15`; server RETURN remains `0.1` in this local-only scenario. Flying uses the modified `getSpeed`, not the original flying RETURN. |
| Distance exactly 10 | Strict radius rejects applicability; client query remains `50 ms` and speed/flying RETURNs remain original. |
| Client master tick 1799 / 1800 | Modifier applies / expires. Long potion duration 3600 instead supplies maximum duration 7200 and expiry at 3600. |
| Invalid owner, missing owner Sugar Rush, or absent local modifier | No local query contribution. |
| Recipient lacks Sugar Rush or speed config is disabled, with an existing valid client copy | Existing local clock query can remain `200 ms`; recipient speed/flying RETURNs remain original. Owner validity and recipient gates stay distinct. |

The dependency contract is `alexscaves:citadel:sugar_rush_tick_controller`. Its recorded numeric behavior explains the doubled local contribution to the client query and the server's GLOBAL-only query. The native dependency record also states that the relevant server clock/entity gate mixins are not configured in this artifact. The fixture therefore preserves the server query at 50 ms rather than inferring active server slowdown from a request or class name.

The model covers one already-admitted Player Added/ServerLevel/config event and one client modifier copy, without global modifiers. It projects recorded positive potion durations, client master-tick expiry, original native RETURN values, and motion callbacks. It does not simulate list update/removal synchronization, native stacking/admission, dimension serialization, networking, rendering, or inactive server hooks. The complete CLI semantics remain the authority for those behaviors.

## Tests and protection

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s scripts/external-effects -p test_mod_intelligence_workflow.py -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s scripts/external-effects -p test_mod_intelligence.py -v
```

Results: **13 workflow tests and 22 V1 tests passed**. The workflow checks the numeric outcomes and gates above, invocation from another directory, exact numeric-site joins, inconsistent input fingerprints between CLI calls, unresolved dependency responses, and stale mod/dependency versions or hashes. Different local artifact bytes fail with CLI exit code `3` before the fixture can evaluate. A synthetic in-memory wiring probe changes a supplied motion factor and verifies that the consumer uses it; that probe is not another native verification claim.

No native archive was parsed and no mod was rescanned. Optional local checks only streamed SHA-256 hashes. No canonical research record, production source, extraction tool, or V1 CLI implementation changed. Only the isolated example, its tests, and documentation were added. No expensive unrelated suite, Minecraft, Gradle, new mod investigation, or research recreation was run.

## Missing capabilities encountered

1. **Dependency evidence is not resolved by V1's dependency command.** The returned completed obligation has Citadel class/method locators, but the command's `inputs` manifest does not include `native-evidence/citadel-alexscaves-dependencies.json`, and its witness method hashes are absent. This consumer uses the locked obligation document and its fingerprint, plus the exact dependency artifact pin. It does not claim to have revalidated those dependency witnesses. A regression test makes that limit explicit.
2. **Dependency selection is coarse.** The coding fixture needs one obligation, while `dependencies alexscaves` returns all five; selection happens in the consumer. The no-local-artifact run returned 40,735 bytes for `get`, 24,235 for `dependencies`, and 808 for `verify` (65,778 bytes total). These are measured UTF-8 response sizes including newlines, not token, time, or usage savings.
3. **Historical inspection status can be mistaken for current readiness.** Sugar Rush still returns `VERIFIED_NATIVE_ALEXSCAVES_BOUNDARIES_EXTERNAL_CITADEL_CONSUMER_PENDING` as its original `inspection_status`, while its canonical checkpoint is the completed Citadel closure and the dependency obligation is `RESOLVED_PINNED`. The consumer requires the current dependency completion and exact pins. The CLI preserves the historical label; it does not supply a separate reconciled readiness field. Canonical records were left untouched.
4. **Formula and gate translation remains task-specific.** Numeric values and identities are structured, while controller formulas and configured-hook limits include prose. The fixture manually implements the bounded operations and verifies them with boundary cases. This validation does not justify a universal formula evaluator or an analyzer.

The minimum justified next step is a narrow, optional obligation selector on `dependencies` that returns that obligation's resolved existing witness identities and hashes, using the current evidence resolver. Add targeted missing/stale dependency-witness tests. Leave formula translation in small coding adapters until another concrete workflow shows a need for broader structure. No new mod scan, research rewrite, framework, or MCP server is needed for that step. This validation stops here; the enhancement is not implemented by this task.

The later [dependency selector milestone](mod-intelligence-v1.md#selected-dependency-contracts), based on `fdaa24ac8ee3816f1ce609c8a5faf761833b856d`, implements that recommendation. `dependencies alexscaves --mechanic alexscaves:sugar_rush --obligation alexscaves:citadel:sugar_rush_tick_controller` resolves the 18 existing Citadel witnesses and 82 selected method identities/hashes. The original consumer continues to exercise the unselected interface; an additional workflow test checks the new selected response, exact artifact pins, unchanged contract, and resolved witness inputs. Missing hashes remain explicit, and historical file-only references remain separate. No research record or production code changed.
