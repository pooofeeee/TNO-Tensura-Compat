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

## V1.5 coding validation: fixed animation-clock diagnostic

Baseline: `26f377018b1f418446b16396825c22a7472da59d`. The selected coding task is an executable animation-clock diagnostic for the existing Corrodent mechanic, implemented in `scripts/external-effects/examples/animation_clock_preview.py`. It previews one unchanged active animation: Start cancellation, server send intent, counter advance, Tick intent, and expiration. It uses the existing CLI subprocess helper and source-pin expectations from the Sugar Rush example. It never imports the catalog API or reads mechanic research files itself.

The implementation uses `alexscaves:corrodent_bite_native_dig_light_fear` and its exact `alexscaves:citadel:actor_animation_clock` obligation. The retrieved dependency supplies the numeric increment `1`, equality-based expiration, cancellation behavior, server-only animation send, and explicit absence of a damage callback. The native Corrodent tick witness and the Citadel `AnimationHandler.updateAnimations` / `sendAnimationMessage` descriptors and hashes provide the relevant source identities. Both exact artifact pins are checked by the CLI; common input fingerprints are checked for drift between responses.

### Commands and measurements

The final coding workflow executes these three CLI requests. `$MOD_SHA` is `6fad35bf07fcb977aaa32d3fe05bf122150c6a30ed16b057385040207a3b788f`; `$DEP_SHA` is `9e12468c49e5a95b7adbf22b3b4d05bc55565989b89c40b985cd73bdfe63c3c2`.

```sh
MOD_SHA=6fad35bf07fcb977aaa32d3fe05bf122150c6a30ed16b057385040207a3b788f
DEP_SHA=9e12468c49e5a95b7adbf22b3b4d05bc55565989b89c40b985cd73bdfe63c3c2
python3 -B scripts/external-effects/mod_intelligence.py search "corrodent animation" --mod alexscaves --limit 2 --expect-version 2.0.10 --expect-sha256 "$MOD_SHA"
python3 -B scripts/external-effects/mod_intelligence.py get alexscaves:corrodent_bite_native_dig_light_fear --mod alexscaves --section semantics --section evidence --expect-version 2.0.10 --expect-sha256 "$MOD_SHA"
python3 -B scripts/external-effects/mod_intelligence.py dependencies alexscaves --mechanic alexscaves:corrodent_bite_native_dig_light_fear --obligation alexscaves:citadel:actor_animation_clock --expect-version 2.0.10 --expect-sha256 "$MOD_SHA" --expect-dependency-version 2.7.6 --expect-dependency-sha256 "$DEP_SHA"
python3 -B scripts/external-effects/examples/animation_clock_preview.py --duration 3 --updates 4 --start-cancelled
```

Measured UTF-8 response sizes, including newlines, were **1,818 bytes** for search, **23,684** for get, and **18,332** for selected dependencies: **43,834 bytes** total, with six distinct input fingerprints. The executable records its exact command arguments, response byte counts, source provenance, and trace. A captured run is in the ignored `run/mod-intelligence-v15-validation/cancelled-start.json`. These byte counts are not usage telemetry; no token, time, cost, or usage savings are claimed.

Exploratory CLI requests were `search "corrodent collision" --mod alexscaves --limit 2` (one match), `search "path gate" --mod alexscaves --limit 2` (23 matches; two returned), an initial Corrodent `get` with `semantics`, `numbers`, and `evidence` plus `--expect-version 2.0.10`, and the exact animation obligation request with both expected versions. All used the CLI. The broad navigation query was discarded. The final search was narrowed to Corrodent animation, and the unused actor `numbers` section was removed.

### Implementation and tests

For the explicitly supplied scenario duration `3`, a cancelled Start produces frames `1`, `2`, then a terminal Tick `3` followed by reset to inactive tick `0`. The next update stays inactive. Cancellation omits send intent while preserving clock advance. Client updates also advance without server send intent. A frame above duration stays unchanged; expiration uses equality rather than `>=`. Duration is not clamped: zero can reset immediately, while a negative supplied duration does not become zero.

Eleven focused tests cover these rules, the retrieved increment wiring, exact source-version/hash rejection, required witness identity/hash gaps, unresolved obligations, changed end rules, input drift, and execution from an unrelated directory. A synthetic increment change is only an adapter wiring probe, not another verified contract. Results:

- All **62 Mod Intelligence tests pass** in normal Python, including the existing V1, selector, Sugar Rush, and 11 new diagnostic tests.
- All **11 new diagnostic tests pass** with `python -O` and separately with `PYTHONOPTIMIZE=1`; the latter also optimizes the spawned CLI processes.
- No mechanic or catalog correction was required, and no test failure required a behavior correction. The coding corrections were narrowing the search/sections and requiring a supplied duration instead of inventing a native value.

### Sufficiency, missing information, and next improvement

The three final responses were sufficient to implement and verify the scoped diagnostic. **No manual mechanic/source investigation was required.** Only repository instruction/state files and existing tooling/example code were opened directly; no original mechanic review or native witness packet was manually reopened. No JAR was scanned, catalog rebuilt, completed research edited, or production code changed.

Corrodent's native animation duration is absent from the returned structured numbers. `--duration 3` is therefore a scenario input, not a native Corrodent claim. The adapter translates the dependency's prose/control rules by hand. It does not simulate Start animation replacement, Tick listener mutations, actor-specific setters, networking, damage, or a Minecraft runtime. It rejects missing hashes for its required handler methods rather than deriving them. The supplied unchanged-animation scope makes those omissions explicit and keeps the code small.

V1.5 enabled this coding workflow through search, section projection, exact dependency selection, source pins, and witness identities without manual source-file lookup. This is evidence of sufficiency for this bounded task, not a measured general productivity gain. The smallest useful next improvement is optional **method-scoped evidence projection**: this adapter needed the native tick caller and two handler methods, while the responses also carried unrelated actor methods and other obligation witnesses. Such a projection can reuse existing identities and validation; it should not invent missing duration facts or introduce a new analyzer. This validation stops here.
