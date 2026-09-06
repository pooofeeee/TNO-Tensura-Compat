# Candidate C decisive sustained viability research

## Scope and checkpoint ledger

Post-Phase-6 / pre-Phase-7. Source: `0033ecef9f81272adafbbc53fdd33adba9507f2e`.
Branch: `phase-6-candidate-c-sustained-viability-research`.
Phase 6 and Magic/Holy production are complete; original Phase 7 is unstarted.
R1-R5, W1-W4 and P1-P4 remain accepted historical evidence.

| Checkpoint | Status |
|---|---|
| V1 sustained harness | Complete: focused tests, strict extraction and full-stack smoke passed |
| V2 official 15-case matrix | Not started; requires V1 push and remote verification |
| V3 analysis | Not started; requires V2 push and remote verification |
| V4 terminal decision | Not started |

This is the last architecture-level Candidate C viability study. Its only
permitted terminal decisions are `CANDIDATE_C_REJECTED` and
`CANDIDATE_C_CALIBRATION_AUTHORIZED`. No calibration or production change is
authorized here. RW=1 failure exhausts Candidate C; the default subsequent
project task is Elemental native-event-path research, subject to owner review.

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
`adaptive_wound_sustained_smoke` (V1 only). They reuse the accepted real
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
