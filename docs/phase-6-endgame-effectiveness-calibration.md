# Phase 6 endgame-effectiveness calibration

This branch is calibration and architecture validation only. It does not
implement a permanent L2 solution, change Curve C, change Stage thresholds,
or change any production combat behavior.

## Checkpoint ledger

| Checkpoint | Status | Evidence | Conclusion |
|---|---|---|---|
| A — durability decomposition | Complete | `docs/benchmarks/phase6-endgame-calibration/durability.jsonl` | Generic L2 vanilla-health scaling is exact and independently observable; it is capped at 10,000 HP here. Native L2 does not scale SHP, but the required external datapack adds 3% of native SHP per L2 level. Tank is a separate trait multiplier. |
| B — Magic/Holy classification | Complete | `docs/benchmarks/phase6-endgame-calibration/classification.jsonl` | Both Tensura sources bypass armor but lack NeoForge `IS_MAGIC`; therefore installed L2 Dementor reduces both and Dispell reduces neither. Preserve source identity is the safe default. |
| C — development calibration context | Complete | `Phase6CalibrationContext` plus unit tests | Synchronous ThreadLocal scope; observes only `getExisting`; fail-closed; no serialized or L2-owned state changes; impossible to activate in production. |
| D — diagnostic ceiling | Complete | `ceiling_magic_weapon.jsonl`, `ceiling_holy_weapon.jsonl` | Neither reducer alone nor both together are sufficient. Generic-H compensation is also required for practical viability in this controlled profile. The all-100% diagnostic bound reaches about 211-242s S7 TTK at Lv600-Lv1000, proving the three-component architecture is mathematically sufficient without selecting production values. |
| E — generic-health calibration | Complete | `health_magic_weapon.jsonl`, `health_holy_weapon.jsonl` | Q is monotonic but cannot overcome untouched Dementor + Adaptive. Q=1 alone still estimates 10.7-15.0 hour S7 fights at Lv600-Lv1000. No arbitrary L2-level threshold is supported; H naturally scales. |
| F — Dementor calibration | Complete | `dementor_magic_weapon.jsonl`, `dementor_holy_weapon.jsonl` | RD 0.50-0.75 is the promising coarse interval. RD <=0.25 is too weak; RD=1 erases Dementor and is too strong architecturally. |
| G — Adaptive calibration | Complete | `adaptive_magic_weapon.jsonl`, `adaptive_holy_weapon.jsonl` | RA 0.50-0.75 is promising. Both retain a clear repeated-source penalty; RA=1 reproduces no-Adaptive and is rejected. |
| H — combined candidates | Complete | `combined_magic_weapon.jsonl`, `combined_holy_weapon.jsonl` | Three strictly increasing ramps preserve Dementor and Adaptive harm and produce clear S5 < S6 < S7 gross progression. The upper ramp reaches roughly 5.7-6.7 minute gross S7 estimates, but native Regenerate's 400-500 HP/s configured ceiling exceeds every tested TNO-only result; this is promising damage calibration, not yet a complete endgame solution. |
| I — safety matrix | Complete | `safety_magic_weapon.jsonl`, `safety_holy_weapon.jsonl`; accepted Phase 5F/6 targeted evidence | 64 cases and 640 traces preserve lower-Stage no-op behavior, source/event integrity, native L2/Tensura authority, unrelated-family isolation, and strict S5-S7 progression with zero failures, duplicates, or unexpected bypasses. |

Checkpoint A's full formula audit, 16-case table, exact modifier lists, and
per-case trait/rank lists are documented in the benchmark evidence README.

## Checkpoint D — diagnostic ceiling conclusions

The accepted D matrix has 144 cases and 1,440 per-hit reducer traces: Magic
and Holy, S5-S7, Lv300/Lv600/Lv800/Lv1000, six diagnostic policies, ten real
Royal Arrow releases per case, and `APO_profile = NONE`. All cases completed
with zero errors, unexpected bypasses, duplicate eligible events, or source
changes. Adaptive retained L2-owned state and progressed from count 1 through
10 with native factor `1.0 -> 0.001953125` where attached.

The ceiling answers are decisive but not balance decisions:

1. Full Dementor recovery alone is insufficient.
2. Full Adaptive recovery alone is insufficient.
3. Full recovery of both is insufficient; S7 still estimates 91-139 minute
   Lv600-Lv1000 fights.
4. Compensation tied to verified level-derived durability is also necessary
   for a practical target, but its correct fraction remains uncalibrated.
5. The all-100% upper bound is capable: S7 estimates 211-242 seconds across
   Lv600-Lv1000, with Lv1000 at 414.400 family DPS and 226.1 seconds.
6. The remaining limiter below that bound is the combination of dominant
   level-derived SHP resources and whichever L2 reducer remains authoritative.
7. Magic and Holy behave equivalently at the reducer boundary; observed small
   differences are runtime variance, not a semantic split.
8. Lv600 already exhibits the same wall as Lv800/Lv1000.

The H diagnostic is specifically the nominal native L2 hostility-health
multiplier, not final total resources. Target HP, Tank, native SHP, and the
external Tensura:L2Hostility SHP bridge remain unchanged and separately
identified. The 100% values are upper bounds only. No Q/RD/RA candidate or
permanent production behavior is selected here.

## Checkpoint E — Q sweep

The accepted E matrix has 120 cases and 1,200 traced hits. It varies only Q
through 0, 0.25, 0.50, 0.75, and 1.00; RD=RA=0 throughout. At S7 Lv1000,
Magic moves from 0.696 to 1.737 family DPS and Holy from 0.696 to 1.737.
Those are monotonic gains, but native Dementor's logarithm and Adaptive's
unchanged repeated-source collapse dominate them. Q=1 still estimates about
53,900 seconds family-only TTK at Lv1000.

Accordingly, level-derived durability participation is necessary in the
three-component architecture established by D, but never sufficient alone.
No target-level cutoff is justified: the verified H term already follows
actual L2 level, and Lv600 exhibits the same fundamental wall. The nominal H
input remains explicitly distinct from capped vanilla HP, Tank, native SHP,
and the separately observed Tensura:L2Hostility SHP bridge. E does not select
a permanent Q or change any production behavior.

## Checkpoint F — RD sweep

The accepted F matrix has 240 cases and 2,400 reducer traces, split equally
between the accepted legal profiles and legal otherwise-identical controls
with Dementor removed and its budget left unused. The measured formula is
exactly `nativePost + RD * (pre - nativePost)` at the native L2 boundary.

RD 0-0.25 remains too weak; RD 1.00 reproduces the no-Dementor boundary and
would delete the trait's identity. RD 0.50-0.75 is the only promising coarse
region: it retains measurable nonlinear harm while recovering enough signal
for the later combined test. Adaptive remains fully native and is why even
RD=1 alone still produces multi-hour high-level estimates. No permanent RD is
selected.

## Checkpoint G — RA sweep

The accepted G matrix has 240 cases and 2,400 traces including legal
no-Adaptive controls. L2-owned memory is untouched: the source ID remains
original, count advances 1-10, and native factor follows `0.5^(count-1)` down
to 0.001953125. Rank remains source-memory capacity rather than a reduction
percentage.

RA 0.50-0.75 is the promising region. At RA=0.75 the tenth negotiated factor
is 0.750488 versus 1.0 on hit one, so the trait retains a meaningful repeated-
source penalty. RA=0.50 retains about a 50% late-hit penalty. RA<=0.25 is too
weak for the intended combined objective, while RA=1 exactly erases Adaptive
and is rejected. No permanent RA is selected.

## Checkpoint H — combined candidates

The accepted H matrix contains 270 cases and 2,700 traced hits: 135 cases per
family across Lv600/Lv800/Lv1000, S5-S7, three small candidate ramps, and five
legal profile variants. Every case uses a fresh initialized L2 attachment so
native ticking traits are not inferred from a serialized clone. The variants
are the accepted strongest legal Orc profile; the same profile without
Dementor; without Adaptive; without both; and without Regenerate. Removed
trait budget is left unused. There are zero case errors, source changes,
duplicate eligible events, recursions, Tensura bypasses, or L2 bypasses.

The three development-only ramps are:

| Ramp | S5 `(Q,RD,RA)` | S6 `(Q,RD,RA)` | S7 `(Q,RD,RA)` |
|---|---|---|---|
| Low | `(0.25,0.50,0.50)` | `(0.375,0.625,0.625)` | `(0.50,0.75,0.75)` |
| Mid | `(0.375,0.50,0.50)` | `(0.5625,0.625,0.625)` | `(0.75,0.75,0.75)` |
| High | `(0.50,0.50,0.50)` | `(0.75,0.625,0.625)` | `(1.00,0.75,0.75)` |

All dimensions increase strictly from S5 to S7 and stay inside the promising
regions established by E-G. No permanent values are selected.

On the accepted profile, the high ramp's family DPS and gross combined-
resource TTK are:

| Family | Level | S5 DPS / TTK | S6 DPS / TTK | S7 DPS / TTK |
|---|---:|---:|---:|---:|
| Magic | 600 | 38.891 / 1,573s | 83.240 / 736s | 161.184 / 380s |
| Magic | 800 | 54.790 / 1,413s | 108.856 / 712s | 224.632 / 345s |
| Magic | 1000 | 61.558 / 1,520s | 134.449 / 697s | 262.273 / 357s |
| Holy | 600 | 40.443 / 1,513s | 96.555 / 634s | 153.459 / 399s |
| Holy | 800 | 50.237 / 1,540s | 108.856 / 712s | 211.416 / 367s |
| Holy | 1000 | 61.558 / 1,520s | 141.257 / 663s | 250.364 / 374s |

This is the intended weak-to-strong Stage shape: S5 remains a 25-minute-class
gross fight, S6 is roughly 10.6-12.3 minutes, and S7 is roughly 5.7-6.7
minutes. The low and mid S7 ramps remain slower at about 7.7-12 minutes. Magic
and Holy remain materially equivalent; small differences are repeat-run
variance.

Dementor and Adaptive still matter. At high S7, removing Dementor raises
family DPS from 153-262 to 202-348, removing Adaptive raises it to 192-313,
and removing both raises it to 253-456. Adaptive still advances count 1-10
with the original source key, and the RA=0.75 tenth-hit factor remains
0.750488 rather than 1. Tank remains rank 5 and the unscaled base physical
Royal Arrow adds only about 0.07-0.16 DPS; the candidate affects only the
eligible native family event.

Regenerate prevents H from being a final viability selection. The runtime
config is 1% of max vanilla HP per rank each second, so the legal rank-4 Lv600
profile has a 400 HP/s ceiling and the rank-5 Lv800/Lv1000 profiles have a 500
HP/s ceiling. Those values exceed even every high-ramp TNO-only gross result,
including the controls without Dementor and Adaptive. Short-window observed
healing is timing/resource-path dependent, so a finite sustained TTK with
Regenerate cannot be defended from the 200-tick damage window. The high ramp
is therefore the best safety-test candidate, but the three-component
Q/RD/RA architecture is not yet proven sufficient against Regenerate and no
production policy should be implemented from H alone.

## Checkpoint I — safety and non-interaction

Checkpoint I is complete. The new live safety matrix contains 32 Magic cases
and 32 Holy cases over the accepted legal Orc profile at Lv300, Lv600, Lv800,
and Lv1000, with production S0-S7 and ten real Royal Arrow releases per case.
The 640 hit rows each contain one calibration trace. Strict extraction reports
64/64 complete cases, zero case errors, zero duplicate sources or eligible
events, zero recursion, zero unexpected Tensura bypass, and zero unexpected L2
bypass.

S0-S4 use Q=RD=RA=0 and are exact negotiation no-ops at every tested level.
They retain the normal Curve C result, the native Dementor result, the native
Adaptive factor, one unchanged 8.0 physical-arrow input, and the original
projectile and source identities. S5-S7 use only the development high ramp:
`(0.50,0.50,0.50)`, `(0.75,0.625,0.625)`, and
`(1.00,0.75,0.75)`. Both families increase strictly S5 < S6 < S7 at all four
levels. No special Lv800 threshold exists; the verified L2 H factor naturally
follows the attached level.

Dementor and Adaptive remain authoritative. The original Adaptive source keys
are still `tensura.magic` and `tensura.holy_damage`; rank and memory capacity
are unchanged; L2 owns the memory; and every attached repeated sequence
advances count 1-10 without reset. At S7, RA=0.75 leaves the tenth factor at
0.750488 versus 1.0 on hit one. Checkpoint H's legal controls show higher
damage when either trait is removed, so both remain measurably harmful.

The candidate is isolated to an explicitly flagged development scope around
an already-existing native Magic/Holy event. The gate now returns no scope for
an unflagged runtime, unrelated family, unclassified gear, absent Stage,
missing target, absent L2 mod, absent or uninitialized existing attachment, or
failed reflective read. It uses `getExisting`, never `getOrCreate`, and owns no
persistent state. The clean build remains independent of local L2/Royal
Variations runtime artifacts.

Accepted Phase 5F/6 evidence supplies the targeted non-interaction controls
without repeating completed runs. Matching Resistance remains exactly 0% at
S0-S4, 25% at S5, 50% at S6, and 100% at S7. Matching Nullification remains
absolute. Arena admission, Repelling projectile rejection, Teleport avoidance,
Reflect behavior, Tank's physical mitigation, and current Dispell routing are
unchanged. Regenerate rank/config/rate is observed but never modified. Missing
Soul/Elemental native events are not synthesized; Energy Steal retains its
physical prerequisite and native transfer accounting; Severance retains one
physical source, unchanged base-arrow contribution, and native wound gate.
APO and base Royal Arrow output stay outside Q/RD/RA, and native Gear EP remains
the only Stage authority.

All 22 safety acceptance items therefore pass. The evidence proves that the
high ramp is the best current development candidate and does not violate the
accepted boundaries, but it still does not solve Regenerate and is not a
permanent production selection.

## Final calibration analysis

Status: complete. Checkpoints A-I establish a safe answer for admitted Magic
Weapon and Holy Weapon events. They do not establish a complete solution for
all six families or authorize a production change on this branch.

### A. Proven for Magic Weapon and Holy Weapon

The evidence supports one narrow architecture: after the native event exists,
after production Curve C, and after the authoritative matching Tensura layer,
use the existing initialized L2 attachment and its actual level-derived
generic-health factor to negotiate only the eligible Magic/Holy contribution
at L2's existing generic-health, Dementor, and Adaptive modifier boundaries.
Never restore arbitrary final damage, replace or duplicate the DamageSource,
retag the source as NeoForge magic, subtract HP directly, or create an event.

The best tested development candidate is:

| Stage | Q | RD | RA |
|---|---:|---:|---:|
| S0-S4 | 0 | 0 | 0 |
| S5 | 0.50 | 0.50 | 0.50 |
| S6 | 0.75 | 0.625 | 0.625 |
| S7 | 1.00 | 0.75 | 0.75 |

Q uses only the verified nominal generic L2 hostility-health factor
`H = 1 + level * healthFactor * entityHealthScale`; it does not collapse
native HP, capped generic HP, Tank, native SHP, or the external datapack SHP
bridge into one quantity. RD blends from native Dementor output toward the
same reducer input. RA blends the native Adaptive factor toward 1 while L2
continues to own source memory and count. No arbitrary Lv800 activation
threshold is justified: the H input already follows the actual attached L2
level, and S5-S7 provide the progression boundary.

Checkpoint H demonstrates damage-side usefulness: accepted-profile high-ramp
S7 estimates are roughly 153-262 family DPS and 345-399 seconds gross TTK at
Lv600-Lv1000. Checkpoint I then proves strict S5 < S6 < S7 at every tested
Lv300/Lv600/Lv800/Lv1000 coordinate and exact Q/RD/RA no-op behavior at S0-S4.

### B. Explicit answers

1. **Is Q required?** Yes. D proves that reducer recovery without generic-H
   participation remains too weak; E proves Q alone is insufficient. It is a
   necessary component, not a global durability or damage multiplier.
2. **Is RD required?** Yes. Native Dementor logarithmically compresses both
   installed Tensura source types. Partial RD in the 0.50-0.75 range is needed;
   RD=1 is rejected because it erases Dementor.
3. **Is RA required?** Yes. Untouched Adaptive collapses repeated same-source
   hits. Partial RA in the 0.50-0.75 range is needed; RA=1 is rejected because
   it erases Adaptive.
4. **Is the HIGH ramp the best current development candidate?** Yes. It is the
   strongest tested ramp that passes the complete safety matrix while retaining
   both reducer identities. This is a recommendation for the next production-
   implementation task, not code implemented by this branch.
5. **Does it preserve Dementor?** Yes. In H's otherwise-identical controls,
   removing Dementor raises high-S7 family DPS from the accepted 153-262 range
   to 202-348. The accepted profile therefore remains measurably worse.
6. **Does it preserve Adaptive?** Yes. Removing Adaptive raises high-S7 family
   DPS to 192-313. In I, the original source key, rank, memory capacity, and
   L2-owned count remain unchanged; count advances 1-10 and the S7 tenth-hit
   factor is 0.750488 rather than 1.
7. **Is it safe for lower Stages, non-L2 paths, and unrelated families?** Yes,
   within the tested architecture. Four hundred S0-S4 traces are exact
   negotiation no-ops. Missing/uninitialized L2, an unclassified or unstaged
   item, an inactive family, and an absent eligible event fail closed. Soul,
   Elemental, Energy, and Severance are rejected before the L2 negotiation.
8. **Is Magic/Holy production implementation now justified?** Yes, as the next
   narrow damage-side task: Magic/Holy only, initialized existing L2 attachment,
   active native eligible event, S5-S7 only, and the high-ramp parameters above.
   It is not evidence that Regenerate is solved or that a full sustained kill
   is guaranteed.
9. **What prevents calling the six-family system solved?** Native Regenerate
   can nominally heal 400-500 HP/s, exceeding every tested TNO-only Magic/Holy
   result. Soul lacks its native `tensura:soul_scatter` event. Elemental's
   native projectile can exist while its matching elemental damage event does
   not. Energy Steal is healthy only after a physical prerequisite that often
   fails. Severance preserves its native +3 and one source but rarely survives
   the physical wall to store wound.
10. **What is the next exact order?** Implement the validated Magic/Holy
    architecture first; then investigate Severance against Regenerate; then
    investigate the Elemental native-event path; then Soul's native-event path;
    then Energy Steal's physical prerequisite; only after those blockers are
    resolved should the original Phase 7 resume.

### C. Unresolved work and exact next investigations

The first follow-up after Magic/Holy production implementation should be a
separate **Severance ↔ Regenerate** investigation. Do not begin by inventing a
generic TNO anti-heal mechanic. Determine the installed native Severance wound
semantics; whether wound reduces, prevents, or materially constrains L2
Regenerate; whether Tank, Dementor, or Adaptive prevents wound admission; and
whether proportional treatment of only the native eligible Severance +3 can
make wound reliable while retaining one physical DamageSource. Royal Arrow
base damage must remain native, and Tank/Dementor/Adaptive must remain relevant.
Only that evidence can decide whether Tensura's existing anti-sustain semantic
already supplies the correct answer.

Elemental requires a different native-path investigation across Earth, Fire,
Space, Water, and Wind. The accepted Earth case proves
`tensura:stone_shot` can exist and receive Stage propagation while the required
`tensura:earth_elemental` event is absent. Determine the exact owner, state,
skill, target, or hit-path prerequisite for each matching elemental
DamageSource; whether another native damage path is selected; and whether the
result is boss-dependent. Compatibility may satisfy a legitimate missing
prerequisite, but it must not synthesize an elemental event merely because TNO
expects one.

Soul then needs its own native `soul_scatter` eligibility investigation.
Energy Steal follows: its drain math and equal target-loss/attacker-gain
accounting are healthy when admitted, so research must remain focused on the
physical prerequisite rather than inventing a drain. These tasks are distinct
from Q/RD/RA and must not be hidden inside the Magic/Holy implementation.

### Final recommendation

Approve the high-ramp Q/RD/RA architecture for a separately reviewed,
production-quality Magic/Holy implementation. Preserve the exact existing
matching-Resistance schedule, absolute Nullification, original source IDs and
tags, L2 admission and trait state, Curve C, base Royal Arrow damage, APO
output, and native Gear EP. Keep it inactive at S0-S4 and fail closed whenever
the already-existing L2/native-event context is unavailable.

Do not claim complete endgame viability until Regenerate and the other four
family-specific blockers have their own evidence. This branch ends with the
calibration recommendation only; it contains no permanent Q/RD/RA production
implementation and does not start Phase 7.
