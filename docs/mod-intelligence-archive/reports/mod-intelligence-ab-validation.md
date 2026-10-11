# Controlled Mod Intelligence A/B evaluation

Committed baseline: `697ad4df7b4ed70e6409c18419bce4ac2c93b2f3` on `feat/mod-intelligence-v1`.
Date: 2026-10-09. This is a sequential, unblinded pilot by the same agent, with
prior Sugar Rush familiarity. It is not an independent causal or statistical
comparison. Shared setup opened seven repository files; these are listed in the
manifest and excluded from both arm measurements. B also benefits from A's task
experience, so fewer source lines cannot be attributed solely to retrieval.

## Frozen task and oracle

Fix the existing Sugar Rush coding fixture's mutable output alias:
`SugarRush.motion()` returns `self.slow_fall`, including its mutable flags list.
Changing that result changes the contract, earlier previews, and later previews.
Detach the returned payload while preserving directional motion, effect values,
and the existing server/duration/descending/effect-absence predicates.

The unmodified fixture failed two of four frozen tests. The tests were written
before either arm's implementation, do not invoke any Mod Intelligence command,
and are byte-identical in both arms. They cover mutation of contract/later output,
mutation of another existing output, native motion/effect values, and the gate
matrix. Other constructor fields are inert harness inputs, not asserted mod
contracts. Oracle SHA-256: `822ca442143681d25b8a49188f534ca06f077e6efbb7cff1f8ad5db5c5350317`.

Both arms started from source hash `789f73c87c9d5388054febfd27fbe552050817beeb117dd7b4793fe20bb103ec`. Both final
source hashes are `b81eb0d2767acaa3f8797689884cf740f27735f124bc0d6d9ad474e59f3f4e8a`. Each added `deepcopy` and copied
only an admitted returned effect request; inactive requests and motion math stay
unchanged. This is an isolated diagnostic-fixture bug fix, not a native mod edit.

## A — without Mod Intelligence

No Mod Intelligence command was executed. Discovery inspected three files:

- `A/sugar_rush_workflow.py`: class state, payload construction and `motion`.
- `committed/scripts/external-effects/test_mod_intelligence_workflow.py`: existing
  directional motion and Slow Falling behavioral expectations.
- Canonical `mod-reviews/alexscaves.json`: exactly `alexscaves:sugar_rush`, its
  two relevant components and callback proof reference; no catalog rewrite.

One search: `rg -n 'def motion|slow_fall' sugar_rush_workflow.py`.
Source/test excerpts totaled 112 lines, including repeat
reads. One initial range selection missed the intended class/motion start and
included unrelated response/controller lines; corrected ranges are recorded.
This was a navigation correction, not an implementation or semantic correction.

Manual evidence: Y factors `0.85`/`0.45`, server-only original-Y-sign behavior,
Slow Falling duration `10`, amplifier `0`, three false flags, and the existing
`SugarRushEffect.class`/`applyEffectTick` witness reference. The independent
existing behavioral tests supplied the duration and effect-presence gate checks.
The native packet was not reopened or rescanned; this arm used the completed
canonical review's recorded proof reference.

Reasoning still required deciding that both dictionary and nested flags need
ownership isolation, choosing `deepcopy` over a shallow copy, keeping all admission
gates, and selecting behavioral regressions. Native catalog semantics do not
specify Python object ownership. No semantic ambiguity required new research.

Implementation changed only `A/sugar_rush_workflow.py`. The common test file was
copied unchanged into A. `python3 -B -m unittest -v test_motion_isolation` passed
4/4 on the first implementation; zero code corrections.

## B — with Mod Intelligence

Before any B edit, these exact commands executed the exported committed V2.0 CLI
instead of the unrelated dirty worktree version:

```sh
/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3 -B /workspace/mod-intelligence-v1/run/mod-intelligence-ab-validation/committed/scripts/external-effects/mod_intelligence.py impact alexscaves:sugar_rush --mod alexscaves --limit 1 --expect-version 2.0.10 --expect-sha256 6fad35bf07fcb977aaa32d3fe05bf122150c6a30ed16b057385040207a3b788f --expect-dependency-version 2.7.6 --expect-dependency-sha256 9e12468c49e5a95b7adbf22b3b4d05bc55565989b89c40b985cd73bdfe63c3c2
/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3 -B /workspace/mod-intelligence-v1/run/mod-intelligence-ab-validation/committed/scripts/external-effects/mod_intelligence.py context alexscaves:sugar_rush --mod alexscaves --budget-bytes 65536 --expect-version 2.0.10 --expect-sha256 6fad35bf07fcb977aaa32d3fe05bf122150c6a30ed16b057385040207a3b788f --expect-dependency-version 2.7.6 --expect-dependency-sha256 9e12468c49e5a95b7adbf22b3b4d05bc55565989b89c40b985cd73bdfe63c3c2
```

Impact returned **100,668 UTF-8 bytes**; context returned **51,251 bytes**, each
including its newline. Total CLI return size: **151,919 bytes**. Both native
AlexCaves `2.0.10` and dependency Citadel `2.7.6` version/digest checks matched the
catalog pins. No local JAR was read; local artifact verification remains
`NOT_CHECKED`.

Retrieved classifications were `CONFIRMED_DEPENDENCY`,
`EVIDENCE_BACKED_RELATIONSHIP`, `POSSIBLE_IMPACT`, and `UNKNOWN`. The impact has
106 root/dependency methods, 32
evidence links, the confirmed Citadel tick-controller obligation, and one of five
conditional peers with explicit `has_more`. The compact context retains
24 root methods and 32
evidence records across 6 evidence sources.
Both retrievals list ten catalog input files; those automatic reads are distinct
from files manually inspected. Each call also reads 142 repository Python
test files for literal-ID discovery, plus mapping metadata; those automatic
reads are excluded from manual file counts. Relationship occurrence counts in the manifest
include repeated references and must not be treated as counts of unique edges.

The primary behavioral source was the retrieved motion/Slow Falling components
and typed consumers. `applyEffectTick` is method `m2`, with recorded descriptor
`(Lnet/minecraft/world/entity/LivingEntity;I)Z` and SHA-256
`603a87fa9473558f28a559c516332c3d18241323446465f0a2b72e50bd94ca4c`.
Motion consumers are at offsets `55` and `86`; effect construction is at `135`.
The response retains actual literal offsets/arguments, class/file/JAR pins and
units. These are existing static evidence, not newly inspected native code.

After retrieval, B inspected two repository files: its copied fixture and the
mapped existing workflow tests. One additional `rg` search located `motion` and
`slow_fall`. Those source/test reads totaled 42 lines and
2,596 rendered bytes including search output. B
opened no additional canonical review or native packet. Its two generated
retrieval responses also count as inspected artifacts.

The tool supplied a pinned fixture source/test mapping; mapped tests are
`NOT_RUN` and literal-ID references are `UNKNOWN`, not verified coverage.
Python alias detection, object ownership, deep-versus-shallow copying, regression
design, and deciding that native/controller peers are irrelevant to a Python-only
copy fix still required Codex reasoning. No production edit mapping, runtime
Minecraft verification or transitive call analysis was available or needed.

Implementation changed only `B/sugar_rush_workflow.py`. The common test file was
copied unchanged into B. The exact same four-test command passed 4/4 on the first
implementation; zero code or navigation corrections. No A code was copied to B;
the same agent implemented the same straightforward fix from the untouched copy.

## Measured comparison

| Metric | Without Tool | With Tool |
|---|---|---|
| Files inspected | 3 repository files | 2 repository files + 2 responses = 4 artifacts |
| Searches | 1 | 1 after retrieval |
| Evidence gathering | Manual two-component canonical lookup + proof reference | 32 validated evidence links + one dependency; no extra catalog lookup |
| Context size | 8,724 rendered investigation bytes | 20,578 rendered bytes; 151,919 full CLI return bytes |
| Corrections | 0 code; 1 navigation | 0 code; 0 navigation |
| Tests | Same 4/4 pass | Same 4/4 pass |
| Final correctness | Mutation isolated; behavior/gates preserved | Identical source and tested behavior |

Rendered investigation bytes measure the exact emitted source/search/selected
JSON excerpts, including repeated reads. Shared setup, authored tests, test logs,
commentary, prompt history and tool transport wrappers are excluded in both arms.
B's displayed excerpts are projections of larger saved responses, so full CLI
return bytes are reported separately rather than silently equated with model
context. Source line counts exclude JSON projections and search matches.
No token, allowance, cost, runtime-coverage or elapsed-time savings are claimed.

## Explicit conclusions

1. **Investigation work:** B eliminated one manual canonical lookup, but searches
   stayed equal and total inspected artifacts increased. This pilot does not
   demonstrate a net reduction in investigation work. Its stronger provenance is
   a concrete benefit; the native contract lookup was already narrow in A.
2. **Unnecessary context:** No reduction was observed. Even after displaying only
   selected projections, B rendered more than twice A's investigation bytes.
   Most of the tick-controller, speed, potion and peer information was irrelevant
   to this Python payload-isolation fix. `--limit 1` bounded peers, not the required
   whole-mechanic/root/dependency package.
3. **Correctness:** No observed improvement. Both first implementations were
   byte-identical and passed the same frozen behavioral tests. B offers stronger
   automated pin/literal checks, but this experiment does not show fewer bugs.
4. **Missing information:** Python aliasing/ownership and the copying strategy;
   which new test catches this fixture bug; runtime integration and coverage;
   transitive impact and production targets. Codex still had to reason about the
   relevant source and run tests. These missing runtime facts were not needed for
   the scoped fixture change.
5. **V2.1:** This pilot does **not justify implementing V2.1**. A planner is not
   established as the remedy for the observed context overhead or ownership bug.
   A broader claim needs independent cold-start repetitions on mod-mechanics
   coding tasks. This result is limited to one familiar, local Python fixture bug.

## Artifacts and scope

- `manifest.json`: measured reads, lines, search commands, retrieval commands,
  hashes, decisions, corrections and outcomes.
- `A/implementation.diff`, `B/implementation.diff`: isolated identical fixes.
- `shared/test_motion_isolation.py`: frozen four-test oracle.
- `A/baseline-tests.log`: original bug reproduction (two failures).
- `A/final-tests.log`, `B/final-tests.log`: final four-test passes.
- `B/impact.json`, `B/context.json`: exact unmodified CLI responses.

All outputs are in ignored `run/mod-intelligence-ab-validation/`. No tracked
implementation, production, canonical catalog, branch ref, or existing planner
work was changed. No JAR scan, new mod research, catalog rewrite, V2.1 work,
Astra audit, broad test suite, commit, or push was performed. Stop at this A/B
validation milestone.
