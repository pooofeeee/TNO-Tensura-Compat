# Mod Intelligence: complex task A/B validation

Repository: `pooofeeee/TNO-Tensura-Compat`; branch `feat/mod-intelligence-v1`.
Committed baseline: `697ad4df7b4ed70e6409c18419bce4ac2c93b2f3`. Date: 2026-10-10.
Only ignored experiment artifacts were created. The existing dirty planner,
production, canonical research, and branch HEAD are preserved.

## Task and why it requires project understanding

Extend the existing fixed Corrodent animation preview into a two-module,
event-aware combat diagnostic. It must handle Citadel Start cancellation and
replacement, Tick callbacks that mutate actor animation/tick, client packet
restart, native bite eligibility, independent knockback and vehicle damage.
This is an ability-preview extension, not a local bug fix or refactor.

The task crosses `CorrodentEntity.tick`, its animation getters/setters/registry,
`CorrodentAttackGoal.tick`/`checkAndDealDamage`, Citadel's
`AnimationHandler.updateAnimations`/`sendAnimationMessage`, Start replacement,
and `ClientProxy.handleAnimationPacket`. These span two native evidence packets,
the completed mechanic review, and a pinned dependency obligation.

The new behavior requires distinguishing all of these:

- Native BITE duration **15**, hit frame **8**, with exact animation object identity.
- Strict LOS/range test: native float distance is less than float width sum + 1.
- Original attack attribute **3** times bite multiplier **1.5** requests **4.5**;
  rejected hurt still requests knockback **0.2 + 0.3 * 1.5 = 0.65**, copies observed
  post-knockback velocity to a vehicle, and requests **2.25** vehicle damage.
- Damage acceptance does not gate these requests or the burrowing flag; there is
  no heal. An initial rough selection note mentioning heal was corrected from the
  canonical record before the task/API/tests were frozen.
- Cancelled Start skips send/set but still advances locally. Event replacement
  changes the server animation; a client update does not apply that replacement.
- Corrodent's native setter does not reset tick; client packet reception does.
- Tick listeners run before the exact equality end check; both animation and tick
  must be re-read afterward. Overshoot is not a terminal condition.

`animation_events.py` implements dependency protocol transitions;
`corrodent_scenario.py` consumes a pinned contract and integrates the actor's bite
requests. Each arm adds its own `contract.json`. Both use the same frozen API,
scaffold and **15 behavioral tests**, written after manual contract discovery but
before either implementation. No Mod Intelligence command appears in the tests.
Oracle SHA-256: `a0c390215284bd0feb68586b43a21b3dce8cdd92ac3a89bfd91f6425d2291a5b`.
The unimplemented scaffold produced 15 expected `NotImplementedError` test errors;
that is a feature baseline, not 15 introduced defects.

## Experiment A: manual discovery

No Mod Intelligence command was used. Seven unique repository files were
inspected, with exact selections and hashes recorded in `manifest.json`:

1. `mod-reviews/alexscaves.json`: selected Corrodent behavior, numeric components,
   implementation references, and exact dependency mapping.
2. `alexscaves-citadel-dependency-obligations.json`: animation clock obligation,
   protocol/lifecycle, original numerical contract and witness locations.
3. `jar-inventory.json`: AlexCaves 2.0.10 and exact Citadel 2.7.6 pins/versions.
4. `native-evidence/alexscaves-forlorn-actors.json`: eight native actor/goal
   method bodies or selected windows, including duration, frame, strict range,
   float arithmetic, ignored hurt return, vehicle behavior, setter and registry.
5. `native-evidence/citadel-alexscaves-dependencies.json`: four dependency method
   bodies (send, update, client restart, Start setter).
6. Existing `examples/animation_clock_preview.py`: fixed-animation baseline.
7. Existing `test_mod_intelligence_animation_workflow.py`: current cancellation,
   client, equality, overshoot and unclamped-duration expectations.

Two explicit `rg` invocations searched the mechanic ID and fixture/test symbols.
Eight structured read selections are also logged; those are evidence selections,
not included in the `rg` counter. Source/test excerpts emitted 150 lines including
repeated or extra lines. All discovery emissions totaled **93,056 UTF-8 bytes**.
Of these, **54,223** were in oversized/partly truncated combined emissions;
**38,833** were in bounded, untruncated excerpts/search output. One full obligation
selection accidentally included other actors' boundary calls and inventory
resources; it was narrowed in a recorded discovery correction. A smaller later
source/test output also exceeded its display budget slightly. Actual
model-delivered bytes for truncated outputs cannot be measured, so emitted bytes
must not be presented as token consumption or exact model context.

Codex had to decide callback state ownership, live versus captured duration,
server/client mutation rules, frame identity, float precision, vehicle ordering,
and simulation boundaries. The completed records answered the native rules;
explicit target geometry, accepted/rejected damage observations and post-knockback
velocity remained scenario inputs. Full AI scheduling was not inferred.

A implemented both modules and its contract from manually collected evidence.
The first implementation passed **15/15**; no code/semantic correction followed
those tests. There was one discovery selection correction.

## Experiment B: impact/context first

B's scaffold and oracle were checked unchanged before these exact calls used the
exported committed V2.0 CLI, excluding the preexisting uncommitted planner:

```sh
/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3 -B /workspace/mod-intelligence-v1/run/mod-intelligence-complex-ab-validation/committed/scripts/external-effects/mod_intelligence.py impact alexscaves:corrodent_bite_native_dig_light_fear --mod alexscaves --limit 3 --expect-version 2.0.10 --expect-sha256 6fad35bf07fcb977aaa32d3fe05bf122150c6a30ed16b057385040207a3b788f --expect-dependency-version 2.7.6 --expect-dependency-sha256 9e12468c49e5a95b7adbf22b3b4d05bc55565989b89c40b985cd73bdfe63c3c2
/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3 -B /workspace/mod-intelligence-v1/run/mod-intelligence-complex-ab-validation/committed/scripts/external-effects/mod_intelligence.py context alexscaves:corrodent_bite_native_dig_light_fear --mod alexscaves --budget-bytes 65536 --expect-version 2.0.10 --expect-sha256 6fad35bf07fcb977aaa32d3fe05bf122150c6a30ed16b057385040207a3b788f --expect-dependency-version 2.7.6 --expect-dependency-sha256 9e12468c49e5a95b7adbf22b3b4d05bc55565989b89c40b985cd73bdfe63c3c2
```

`impact` returned **86,197 bytes**; `context` returned **53,209 bytes** including
newlines, totaling **139,406 bytes**. Expected AlexCaves 2.0.10 and Citadel 2.7.6
versions/JAR digests matched recorded pins. No local JAR check or scan occurred;
`local_artifact` remains `NOT_CHECKED`.

The package supplied **123 root/dependency methods**, **81 root context methods**,
**20 class/witness evidence links** across **two source packets**, and two confirmed
dependencies. The animation obligation was used; selective collision remained an
existing boundary outside this change. Three of 24 possible peers were returned,
with `has_more`; they are conditional relationships, not required edits.
The classifications remain `CONFIRMED_DEPENDENCY`,
`EVIDENCE_BACKED_RELATIONSHIP`, `POSSIBLE_IMPACT`, and `UNKNOWN`.

The retrieved components and selected dependency contract were B's primary
knowledge source. Impact supplied hashes and relationships for 11 task methods.
Pinned mappings located the existing static fixture and test class; mapped tests
were `NOT_RUN`, and literal references remained unverified coverage.

B then manually opened only three repository files: the referenced actor packet,
the mapped existing fixture and its tests. Its two generated retrieval responses
also count as inspected artifacts, for **five total**. It did not manually reopen
the canonical review, inventory, obligation file or raw Citadel packet.
One `rg` search and three structured evidence/response selections were recorded;
source/test excerpts emitted **57 lines**. All selected investigation output was
bounded and totaled **22,993 bytes**. This is a projection of saved full responses,
not a claim that the complete 139,406-byte return was inserted into model context.

Retrieval did not fully supply the concrete animation duration, strict range
comparison, native float conversions, actor setter body or one-item registry.
B inspected five selected actor method bodies/windows to resolve those gaps.
Recorded method hashes and the packet file hash agreed with retrieval. An initial
reader assumed `code_hex` existed and raised `KeyError`; it was corrected to
handle legitimate packets containing only recorded hashes/instructions. All five
extra methods lack raw bytecode hex, so **zero raw method hashes were recomputed**.
A's twelve selected methods also lack raw hex. Static recorded hashes/pins are
not fresh JAR reproduction or runtime verification.

B still required Codex to choose callback interfaces, re-read mutable state after
Tick, preserve float/identity rules, distinguish independent damage effects, and
separate admitted goal evaluation from navigation/fear/collision scheduling.
The first implementation passed the same **15/15**; zero code corrections and one
evidence-reader discovery correction.

## Comparison

| Metric | Without Tool | With Tool |
|---|---|---|
| Files inspected | 7 repository files | 3 repository files + 2 responses = 5 |
| Searches | 2 `rg`; 8 structured selections | 1 `rg`; 3 structured selections |
| Manual evidence gathering | 5 domain files; 12 method bodies/windows | 1 domain file; 5 remaining method bodies/windows, after verified retrieval |
| Context size | 38,833 bounded bytes; 93,056 total emitted bytes including truncated output | 22,993 bounded bytes; 139,406 full CLI-return bytes |
| Corrections | 0 code; 1 discovery selection | 0 code; 1 optional-bytecode reader |
| Tests | Frozen 15/15 pass | Same frozen 15/15 pass |
| Correctness | Contract values and scenario behavior pass | Same semantic contract and matching three demonstration traces |

The implementations differ in source layout; B did not copy A's implementation.
Their numerical/source-identity contract fields are equal; provenance records
reflect their different discovery paths. Three runnable scenarios produced
byte-identical JSON: an explicit goal-before-clock bite/vehicle trace, cancelled
Start, and Start replacement. Demonstration SHA-256:
`95a3d9451a6720b0d2a24d901c67212eee70b4d8f5470e054c95318299a80355`.
The rejected-hurt example requests 4.5 victim and 2.25 vehicle damage, independent
knockback, and ends the animation correctly. These are requested effects, not
claimed damage dealt by Minecraft.

## Interpretation and limits

**Manual investigation decreased in this task.** B replaced four manually opened
domain files and seven method body/window inspections with pinned retrieval.
It had fewer searches/selections and bounded discovery excerpts, while still
performing targeted evidence reads for gaps. This is a useful result for tracing
an existing dependency contract across multiple methods.

**Whole-response context is still broad.** B returned 139,406 bytes, including
unrelated collision/dig/light/peer information. Its displayed bounded projection
was smaller even when A's oversized emissions are excluded, but the full tool
return was not smaller than A's manual discovery output. These are distinct
workflow byte measurements; neither establishes token/allowance savings.

**No correctness improvement was demonstrated.** Both first implementations
passed identical tests; discovery correction counts were equal. B automated
source/version/witness checks and supplied explicit classifications, but this
run does not show fewer implementation defects or prove Minecraft correctness.

**Missing information remains material.** Concrete omitted literals and branch
semantics still needed native evidence. Actual damage acceptance, knockback
physics, event-bus execution, network delivery, external listener behavior and
complete native AI phase ordering were not established by retrieval. The preview
assumes an admitted goal and supplied target/geometry observations; navigation,
light-flee admission, collisions and digging are deliberately outside its API.
The demonstration chooses goal-before-clock explicitly; it does not claim a full
native scheduler proof. A real production integration would need that task's
source mapping and runtime validation.

**This is not an independent causal benchmark.** One agent ran A then B and had
prior familiarity with the animation fixture. The frozen oracle was designed
from A's discoveries before coding, and both arms know its expectations. Shared
setup (four instruction/fixture files), authored scaffold/tests, compiler data
reads, test logs, demonstration JSON, commentary/history and transport wrappers
are excluded from discovery byte/file counts. B benefited from prior learning;
reduced investigation cannot be attributed entirely to the tool. Native/global
input changes and cold-start order controls were not independently randomized.
No time, cost, token, allowance or broad productivity savings are claimed.

The CLI automatically read six catalog input files per call and scanned 142
repository Python test files per call for literal-reference discovery, plus pin
mapping metadata. Those automated reads are not manually inspected files and
were not new mod research or a JAR scan. Relationship occurrence counts in the
manifest include repeated references, not unique-edge counts.

## Reproduction artifacts

- `manifest.json`: command/read/search selections, bytes, hashes, decisions,
  corrections, limits and verification results.
- `shared/test_complex_scenario.py`: frozen 15-test oracle.
- `A/` and `B/`: separate implementations, `contract.json`, module diffs and
  `final-tests.log`; `demo.py` and matching `demo.json` outputs.
- `B/impact.json`, `B/context.json`: original complete CLI JSON.
- `A/baseline-tests.log`: expected unimplemented-scaffold failures.

From either arm, run `python3 -B -m unittest -v test_complex_scenario` and
`python3 -B demo.py`. Existing workflow suites were inspected but not executed
in A because they invoke Mod Intelligence. No broad test suite, Astra audit,
new mod research, canonical rewrite, production edit, V2.1 implementation,
commit or push was performed. Stop after this evaluation.
