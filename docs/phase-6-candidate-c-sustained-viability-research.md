# Candidate C decisive sustained viability research

## Scope and checkpoint ledger

Post-Phase-6 / pre-Phase-7. Source: `0033ecef9f81272adafbbc53fdd33adba9507f2e`.
Branch: `phase-6-candidate-c-sustained-viability-research`.
Phase 6 and Magic/Holy production are complete; original Phase 7 is unstarted.
R1-R5, W1-W4 and P1-P4 remain accepted historical evidence.

| Checkpoint | Status |
|---|---|
| V1 sustained harness | Complete: focused tests, strict extraction and full-stack smoke passed |
| V2 official 15-case matrix | Complete: strict evidence and clean build passed |
| V3 analysis | Complete: all 15 cells strictly recomputed; six ON/OFF comparisons passed |
| V4 terminal decision | Complete: rejected; final validation passed; stop for owner review |

This is the last architecture-level Candidate C viability study. Candidate C
is rejected and exhausted. No calibration or production change is authorized.
The default subsequent project task is Elemental native-event-path research,
subject to owner review; it has not started.

## Locked architecture and official matrix

Candidate C and its implementation are unchanged from the source commit:

```text
D = combined physical pre-L2 integer
E = eligible Severance post-round portion, excluding ordinary Royal Arrow base
K = clamp(post-Dementor / D, 0, 1)
E_preA = E*K
A_wound = A_native + RW*(1-A_native)
eligible_extra = 0.5*E_preA*(A_wound-A_native)
W_offer_C = min(nativeCandidate, W_native + max(0,eligible_extra))
```

Actual physical damage uses native Adaptive, never the wound factor. Tank,
Dementor, Adaptive source/rank/memory/count/factor, Regenerate, native Tensura
wound storage, base arrow damage and Magic/Holy production remain native.
Tensura is the sole wound writer. Native ceiling enforcement is separately
counted and must not recurse into another physical delivery or wound callback.

At S7, each of Lv600/Lv800/Lv1000 runs RW=0/.5/1 with Regenerate ON and
RW=.5/1 with only Regenerate OFF. Removed trait budget stays unused.
The accepted Orc profiles, APO=NONE, Mark disabled, three separate real Royal
Bows and the Magic -> Holy -> Severance order are retained from P3.
One real full-draw Royal Arrow is released every 20 server ticks.

Official measurements last 2400 ticks (120 seconds); only an affected case with
unstable HP or SHP late slope extends to 3600 ticks (180 seconds). The initial
120 seconds are the matched comparison horizon for any unequal extensions.
RW=0 is the exact native wound control, .5 the diagnostic midpoint, and 1 the
capability ceiling. No other RW is permitted.

## V1 harness changes and observation integrity

The new modes are `adaptive_wound_sustained` (official) and
`adaptive_wound_sustained_smoke` (V1 and final runtime validation). They reuse the accepted real
Bow/Arrow collision dispatch, production Magic/Holy, native wound callback,
and existing development-only Candidate C. Targets are fresh, normally
ticking, and the two firing-lane chunks are force-loaded.

The legacy P3 harness rewinds target age after each 20-tick healing cycle and
cancels unrelated Orc healing. Neither operation is allowed in the new mode:
the target clock advances naturally and all other native healing is retained
and counted. The new branch does not revise the accepted historical results.
Keeping unrelated healing is an explicitly disclosed fixture difference from
P3 and can affect absolute damage/healing totals.

Initial native resource fill, legal profile installation, Stage preparation,
positioning and one clock alignment occur before measurement and are
SETUP_ONLY. After the case starts there is no HP/SHP/wound reset, direct wound
write, target-clock rewind, synthetic healing, or synthetic combat damage.
The existing deterministic collision lane and fake-player aiming hold position;
they do not alter the fixed one-second release schedule or damage amount.

A new non-cancelling `LivingEntity.heal` HEAD/RETURN observer captures the real
requested argument and transaction-level before/after state. Its scope requires
the active development study, the exact target, RUN phase and the real
`RegenTrait` call stack. It changes no argument, HP, SHP, wound or event result.
The existing lowest-priority heal listener only reads the allowed/cancelled
result in this mode. The observer has no mutable L2 ownership.

The old clock-rewind observer is bypassed. Each living target tick must advance
exactly once, and its current trait ranks must equal the setup profile. Every
Regenerate transaction must have the native rank, configured request and
20-target-tick cadence. All transactions, each physical arrow's native
Dementor/Adaptive boundaries and Candidate C wound arithmetic, and each
tick's HP/SHP/wound/ceiling trajectory are persisted.

The strict extractor independently recomputes these formulas, validates exact
profile/rotation/source/callback counts and projectile UUID uniqueness, checks
native physical Adaptive and Dementor, verifies wound offers against native
storage increments, and recomputes interval slopes from the trajectories.
Identity assertions in summary metadata alone are not used as proof.

A defeated target is never restored. The case retains its observation horizon
and scheduled genuine releases; post-defeat arrows are discarded without a
living collision and explicitly have zero physical/family events. Such rows
are excluded from admitted-hit counts. A corpse's residual SHP is reported
without being described as consumed. Actual defeat and separate resource
viability are reported independently.

## Counter protocol and floating-point tolerances

For M=maxHP, W=native wound, C=M-W, H=pre-heal HP, R=request:
L=max(0,C-H) and expected actual healing=min(R,L).

State classification uses **0.01 HP**:
C when H >= C-0.01; otherwise A when H+R <= C+0.01; otherwise B.
The ordered classification is mutually exclusive and intentionally treats
sub-millihit residue as at-ceiling.

Transaction validation independently uses the unrounded legal space and
**0.001 HP** tolerance. At 10,000 HP, a float ULP is 0.0009765625 HP, while P3's
largest observed residue was 0.00048447 HP. Classification tolerance never
replaces the tighter formula check. In the boundary tolerance band the
transaction formula is authoritative; no wounded HP or SHP may be restored.
A native State-C denial is valid counterplay, not an identity failure.

Regenerate ON/OFF advantage is assessed where meaningful legal room exists.
Native rank, configuration, cadence, request and heal source must remain
unchanged. All native non-Regenerate healing remains independently present.

## Convergence and projection protocol

Report first 30 seconds, middle, final 30 seconds, whole case, and preceding
30 seconds separately. Compare the final two 30-second HP slopes and SHP
slopes. Convergence means their difference is at most the larger of 0.01 HP/s
and 5% of their maximum absolute magnitude. This is a disclosed convergence
tolerance, not a viability cutoff. Zero/zero is stable but stalled.

Project remaining-resource TTK only for positive, stable, representative late
slopes. Report HP and SHP separately. A scalar HP+SHP slope must never imply
that untouched SHP was depleted. Do not extrapolate startup bursts, corpse
plateaus or transient intervals. Use the accepted ~52-minute and ~16.64-hour
HP-only failures as practical context, without a hidden numerical success
cutoff.

## Reproduction and evidence

Run with Java 21 and the full local compatibility stack selected by
`-Pphase5f_runtime_mods_dir=<mods>`; the third-party JARs remain untracked.
Use `runServer -Pphase6_calibration=true
-Pphase6_calibration_mode=adaptive_wound_sustained
-Pphase6_calibration_family=severance`. The smoke mode substitutes
`adaptive_wound_sustained_smoke` and runs one Lv600/RW1 case for 660 ticks.

Validate/extract using
`scripts/extract-phase6-candidate-c-sustained.py <log-or-jsonl>`.
Use `--smoke` for V1 and `--output <new-path>` only when creating evidence;
existing output files are never overwritten.

Evidence directory: `docs/benchmarks/phase6-candidate-c-sustained-viability/`.


## V1 validation result

The final smoke is v1-harness-smoke-final.jsonl: 1 case, 660 natural target
ticks, 33 genuine releases, 33 native Regenerate transactions, B=22/C=11/A=0.
Requests totaled 13,200 HP; actual healing 2,824.2529296875; denied
10,375.7470703125. The target clock reached 660 without rewinds or changed
trait ranks. The 67 other native heal events were retained, not cancelled.
All physical, wound and healing transaction checks passed.

v1-harness-smoke.jsonl is the initial preflight, retained unchanged. Its
legacy catalog descriptions were corrected for the final smoke; both contain
the same observed aggregate results. Only the final capture is the V1 gate.

Focused Java tests passed (counter arithmetic, locked Magic/Holy policy,
Severance eligible isolation). Four negative extractor tests rejected missing
trajectory data, replaced physical Adaptive factors, healing through the
ceiling, and changed native requests. The full compatibility-stack server
reached Done, completed the final smoke and shut down successfully. No
Candidate C, Magic/Holy, core Stage or historical evidence file was changed.

## V2 official capture and validation

V1 was pushed and its live remote SHA verified as
4b0bfc6d47409b7642eb88da8e723fbda7b6fbf3 before this run started.

The official v2-sustained.jsonl contains 15 complete cases, each 2400 ticks.
No case required extension. Total observation is 36,000 ticks / 1,800 simulated
seconds (30 minutes); the full-stack Gradle runtime completed in 2m 9s using
native tick sprint. There are 1,800 genuine releases (600 per family), 36,015
trajectory samples including the initial samples, and 1,080 native Regenerate
transactions. A=0, B=720, C=360. Requests totaled 504,000 HP; actual healing
122,293.2041015625 HP; denied requests 381,706.7958984375 HP. Denied request
is not presented as wholly wound-specific denial: ordinary max-HP capacity
also limits requests before a wound exists.

All runtime cases passed. The strict extractor independently verified the
entire stored capture. Post-defeat spawn records required a validator
correction: a discarded real arrow retains its type/UUID in the released
projectile arrays, but has no hit-derived projectile identity. The extractor
now requires that spawn identity plus exactly one discard and zero damage
for such rows; living-target rows still require one exact physical source.
No runtime data or historical evidence was changed to satisfy this correction.

Full clean build and all Java tests passed; the four extractor corruption
tests passed. The runtime reached Done, completed all cases, released its
force-load tickets and shut down successfully. Error records, duplicated
physical projectiles, recursion and unexpected bypasses are zero.

The reused generic benchmark serializer retains legacy gross/estimated TTK
fields in the raw capture. These are not sustained-viability projections and
are excluded from V3. Only the recorded trajectories, observed defeat times,
and explicitly justified late-window projections are authoritative for this
study. V3/V4 had not been decided at the V2 checkpoint.

## V3 sustained analysis

V2 was pushed and its live remote SHA verified as
d494aa6e321908f6d66691e40ef6b3e124533aeb before analysis began.
The immutable v3-analysis.json answers all ten required questions for every
cell, retains all interval slopes and separates physical/family/ceiling damage.
The analysis script strictly revalidates V2 before computing its results;
its --check mode reproduces the stored analysis exactly. Strict extraction,
analysis recomputation and all four extractor corruption tests passed.

### Accepted profile: Regenerate ON

All cases start with 10,000 HP. SHP starts and ends at 51,300 / 67,500 / 83,700
for Lv600 / Lv800 / Lv1000 respectively, with zero observed SHP progress
in every interval. The final living slopes pass the declared convergence rule
in all nine cells. The two living Lv600 OFF controls also pass. No living case
needed extension; the four defeated controls have no living trajectory to extend.

| Level | RW | HP end | Maximum/final wound | Late HP/s | Late SHP/s | Late HP+SHP/s | HP projection, total hours |
|---|---|---|---|---|---|---|---|
| 600 | 0 | 9980.000 | 20.000 | 0.166667 | 0 | 0.166667 | 16.666667 |
| 600 | .5 | 9969.003 | 30.997 | 0.258496 | 0 | 0.258496 | 10.745942 |
| 600 | 1 | 9958.063 | 41.938 | 0.350326 | 0 | 0.350326 | 7.929214 |
| 800 | 0 | 9980.000 | 20.000 | 0.166667 | 0 | 0.166667 | 16.666667 |
| 800 | .5 | 9968.917 | 31.083 | 0.258496 | 0 | 0.258496 | 10.745850 |
| 800 | 1 | 9958.005 | 41.995 | 0.350326 | 0 | 0.350326 | 7.929168 |
| 1000 | 0 | 9980.000 | 20.000 | 0.166667 | 0 | 0.166667 | 16.666667 |
| 1000 | .5 | 9968.974 | 31.026 | 0.258496 | 0 | 0.258496 | 10.745910 |
| 1000 | 1 | 9958.005 | 41.995 | 0.354134 | 0 | 0.354134 | 7.844251 |

Each ON cell has 40 wound refreshes and 98.2917% wound uptime across the whole
120-second horizon. Wound quantities in the table are stored native values;
small differences from HP loss are float rounding. The native ceiling still
limits vanilla HP to M-W. It does not wound SHP.

HP projections are conditional, multi-hour estimates, calculated as 120 seconds
already observed plus remaining HP divided by the final 30-second HP slope.
Remaining-only estimates are separately stored in JSON. They assume the current
cadence, defenses, native healing, wound refresh and late rate continue.
No hours-long kill was observed. All are worse than the accepted unreasonable
~52-minute context; RW=0 is consistent with the prior ~16.64-hour failure.
This interpretation introduces no new numerical viability cutoff.

SHP-only projections are non-finite at the observed zero slope. There is no
representative slope for depletion of the full combined resource pool, so no
finite combined-resource TTK is supported. Positive HP+SHP sums above reflect
HP movement alone and do not establish practical combined viability.

### Matched Regenerate OFF controls

| Level | RW | HP end | Maximum/final wound | Observed HP defeat | Conditional HP projection |
|---|---|---|---|---|---|
| 600 | .5 | 1436.258 | 402.5 / 402.5 | None within 120s | ~141.9s total |
| 600 | 1 | 1436.264 | 402.5 / 402.5 | None within 120s | ~141.9s total |
| 800 | .5 | 0 | 323 / 0 | 97.1s | Not extrapolated |
| 800 | 1 | 0 | 321 / 0 | 97.1s | Not extrapolated |
| 1000 | .5 | 0 | 241 / 0 | 73.1s | Not extrapolated |
| 1000 | 1 | 0 | 240.5 / 0 | 73.1s | Not extrapolated |

Both Lv600 OFF late HP slopes are ~65.5846 HP/s and stable. The Lv800 late
windows include death, and Lv1000 late windows are corpse plateaus. These four
terminal windows are not representative combat slopes and receive no TTK
projection or living convergence claim. All scheduled genuine releases continue
through 120 seconds; post-defeat arrows are discarded without collision.
Targets and resources are never reset. Native death clears their wound.

The OFF controls demonstrate native HP death with SHP still present. Thus SHP
depletion is not a prerequisite for killing this fixture. It remains a separate
requested viability criterion, and the accepted Regenerate-ON profile already
fails practical HP viability independently. No ON target died.

### Counter protocol and native authority

All nine ON cases preserve native rank, configuration, one-second cadence and
request: Lv600 rank 4 requests 400 HP; Lv800/Lv1000 rank 5 request 500 HP.
Each has 80 State-B and 40 State-C transactions. Actual legal healing per cell
is approximately 9,893.21 / 13,588.57 / 17,282.62 HP by level. State A does not
occur in this sustained matrix; its arithmetic is covered by the focused tests
and the accepted P4 protocol. Every observed transaction independently matches
min(requested, legal space) within 0.001 HP. Wounded HP and SHP are not healed.
The 0.01-HP classification tolerance does not relax that formula check.

All six matched ON/OFF comparisons show material defense: ON retains 8,521.80
to 9,968.97 more HP at 120 seconds. The ON fixture heals meaningful legal space
and survives while OFF loses most HP or dies. Valid State-C denial is not a
Regenerate failure. Other native healing remains present in both variants.

Adaptive keeps the arrow key, rank/memory capacity 3 at Lv600 and 5 at
Lv800/Lv1000. Native physical counts advance from 1 through 120 in every ON
case; its factor falls from 1 to 1.504632769052528e-36. OFF physical counts end
at 120 / 98 / 74 by level. The reused raw last-Severance summary reaches only
96 / 72 for the defeated controls; V3 reports the true all-physical progression.
RW=1 yields wound-credit factor 1, while physical damage still uses the tiny
native factor. This is diagnostic wound recovery only.

Tank remains rank 5 with armor 46 and toughness 20. Dementor remains rank 1,
with observed input/output ranges and native formula validation in every cell.
Their accepted relevance tests are not repeated. Independent replay of every
living Magic/Holy amount matches the locked S7 Q=1, RD=.75, RA=.75 policy within
0.001 HP. Fixture health-scaling assumptions are disclosed in the JSON.

There are 1,664 living physical source events, 136 post-defeat releases and 552
native wound callbacks. Every living arrow has exactly one physical source.
Native entityless tensura:severance ceiling enforcement has 1,238 incoming
attempts, 360 applied damage events totaling 274.314453125 HP, and no additional
physical delivery, wound reentry or recursion. All applications are in ON cases.
Tensura remains the sole wound owner and the native ceiling remains the healing
counter. Errors, duplicate physical events, recursion and unexpected bypasses
are zero. No practical combined-resource region is demonstrated at any tested RW.

## V4 final decision

V3 was pushed and its live remote SHA verified as
98231ef3218ccdd3297519e7c2ad6d8f24cac442 before the terminal decision.
The machine-readable decision and validation record is v4-decision.json.

| Required answer | Decision |
|---|---|
| 1. RW=0 viable? | No, at all three accepted-profile levels. |
| 2. RW=.5 viable? | No, at all three accepted-profile levels. |
| 3. RW=1 viable? | No, including the maximum diagnostic wound-credit capability. |
| 4. HP viability? | Positive late progress but impractical multi-hour projections with Regenerate ON. |
| 5. SHP viability? | Effectively stalled: zero observed progress in all 15 cells. |
| 6. Combined viability? | No practical full-resource region. Positive scalar sums reflect HP alone. |
| 7. Stable late slopes? | All nine ON and both living Lv600 OFF cases pass. Four defeated OFF cases have no representative terminal combat window. |
| 8. Projected TTKs? | ON HP: RW0 16.667h; RW.5 10.746h; RW1 7.844-7.929h. Conditional late-rate projections only. SHP non-finite; no finite combined-resource projection supported. OFF controls are minutes-scale as detailed in V3. |
| 9. Regenerate protocol preserved? | Yes: native rank/configuration/cadence/request, correct observed B/C transactions, wounded-HP protection and material ON/OFF defense. A has zero runtime occurrences here; its arithmetic remains tested. |
| 10. Adaptive physical authority preserved? | Yes: native arrow source, rank, memory, count and physical factor. Only eligible wound credit uses the diagnostic recovery. |
| 11. Tank preserved? | Yes, native rank 5, armor 46 and toughness 20. |
| 12. Dementor preserved? | Yes, native rank 1 and verified input/output formula. |
| 13. One physical source preserved? | Yes, exactly one per living hit; post-defeat releases cause no collision or damage. |
| 14. Native wound ownership preserved? | Yes, Tensura writes/stores wound and enforces M-W; enforcement is nonrecursive. |
| 15. Candidate C exhausted or calibration-worthy? | Exhausted. RW=1 fails practical HP and combined-resource viability while SHP remains unchanged. |
| 16. Exact authorized calibration interval? | None. Calibration is not authorized. |
| 17. Exact next task? | ELEMENTAL NATIVE-EVENT-PATH RESEARCH, pending project-owner review. Not started. |

The rejection follows the explicit RW=1 exhaustion rule. Native HP kills in
OFF controls do not imply SHP depletion, and no SHP-depletion prerequisite for
fixture death is asserted. Even judged independently on HP, the accepted ON
profile remains far beyond the already rejected ~52-minute practical context.
Mechanical and protocol correctness therefore do not rescue viability.

Candidate C remains development-only. No permanent RW is selected. There is
no further Candidate C architecture recommendation, no new Severance candidate,
and no RW above 1. Calibration, production implementation, Elemental, Soul,
Energy and original Phase 7 are unstarted. The task ends for owner review.

### Final validation and checkpoint protection

Strict revalidation of the immutable V2 evidence passed and is saved as
v4-official-revalidation.json. V3 analysis reproduced exactly; all four
extractor corruption tests passed. The three focused Java classes were rerun:
21 tests passed. A final clean build passed with 54 total Java tests and zero
failures/errors; eligible build/test results were reused from Gradle's cache.

The final full compatibility-stack server run passed in 23 wall-clock seconds.
It used the existing 660-tick smoke: 33 genuine releases, 33 native Regenerate
transactions, A=0/B=22/C=11, and zero integrity errors. Startup reached Done,
the suite completed, both force-load tickets were released, and shutdown saved
all dimensions successfully. v4-runtime-smoke.jsonl and
v4-runtime-validation.json preserve this separate check. Their raw V1 smoke
checkpoint label identifies the harness mode; they do not replace or augment
the official 15-case V2 viability matrix.

Final source comparison confirms the five locked files and the entire core
directory unchanged from the required source. All previously committed V1-V3
machine evidence matches its committed contents. Runtime dependency hashes
still match V1. v4-decision.json records those proofs and the test results.
Historical branches and prior research evidence have not been rewritten.

| Protected checkpoint | SHA verified against live remote before proceeding |
|---|---|
| V1 | 4b0bfc6d47409b7642eb88da8e723fbda7b6fbf3 |
| V2 | d494aa6e321908f6d66691e40ef6b3e124533aeb |
| V3 | 98231ef3218ccdd3297519e7c2ad6d8f24cac442 |
| V4 | The commit containing this final decision; its full SHA and live remote equality are reported in the final response. |

CANDIDATE_C_REJECTED
