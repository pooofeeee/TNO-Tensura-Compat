# Phase 6 Regenerate / Severance counter-protocol research

## Scope and checkpoint status

This is post-Phase-6, pre-Phase-7 research. It begins from the completed
Candidate-C architecture checkpoint
`d0f619ccddb21e7a7f35f9d2d70bfba5d5d4de50` and does not change production
combat, Candidate C, `RW`, Regenerate, Severance storage, the heal event, the
Magic/Holy production policy, or any other scalable family.

| Checkpoint | Status | Result |
|---|---|---|
| P1 — formal counter-state model | Complete | Native Regenerate is intact when it obeys the Severance ceiling. W4 observed only the at-ceiling state, so positive healing in every window is not a valid identity rule. |
| P2 — controlled A/B/C runtime proof | Complete | Rank-4/rank-5 requests obeyed exact native A/B/C behavior with Candidate C present. |
| P3 — dynamic defender advantage | Authorized | P2 passed; must now compare matched Regenerate ON/OFF cycles below the ceiling. |
| P4 — protocol decision | Not authorized | Requires P3. |

The machine-readable protocol definition is
`docs/benchmarks/phase6-regenerate-severance-counter-protocol/p1-protocol.json`.
The prior W1-W4 and R1-R5 artifacts remain unchanged and authoritative.

## Evidence read before P1

The following accepted material was read in full before defining the model:

- `docs/phase-6-regenerate-adaptive-wound-architecture-research.md`;
- `docs/phase-6-severance-regenerate-research.md`;
- `docs/phase-6-endgame-magic-holy-production.md`;
- W3's 6 cases and 60 per-hit rows;
- W4's 15 cases and 150 per-hit rows;
- all four R2 rank-4/rank-5 wound/control captures; and
- R5's 18 sustained cases and 1,080 per-release rows.

R5's force-loaded, normally ticking result supersedes the obsolete R3/R4
non-ticking admission interpretation. It is not treated as an L2 mechanic.

The installed/runtime facts used here remain:

- Tensura `2.0.1.1` owns wound storage and the highest-priority
  `LivingHealEvent` ceiling;
- L2 Hostility `3.0.18` owns Regenerate, which calls
  `LivingEntity.heal(maxHP * 0.01 * rank)` every 20 target ticks;
- the accepted 10,000-HP fixture therefore requests 400 HP at rank 4 and
  500 HP at rank 5;
- Regenerate restores vanilla HP only, not SHP; and
- Candidate C changes only eligible Severance wound credit. It does not change
  Regenerate, its request, its clock, or the delivered physical arrow damage.

## P1 formal counter-state model

Let:

```text
M = maximum vanilla HP
W = native stored Severance wound
C = M - W                         (native healing ceiling)
H = HP immediately before heal
R = requested Regenerate healing
L = max(0, C - H)                 (legal room below the ceiling)
```

For an ordinary positive Regenerate request, native wound semantics are:

```text
actualHeal = min(R, L) when H < C
actualHeal = 0         when H >= C
deniedByWound = R - actualHeal, excluding ordinary max-HP capacity
```

This produces three mutually exclusive states.

### State A — below ceiling

Condition: `H + R <= C`.

Expected native result:

```text
actualHeal = R
deniedByWound = 0
```

Regenerate is completely effective because the request fits inside legal
unwounded HP space.

### State B — crossing ceiling

Condition: `H < C` and `H + R > C`.

Expected native result:

```text
actualHeal = C - H = L
deniedByWound = R - L
```

Regenerate remains effective over the legal space and native Severance denies
only the part that would restore wounded HP.

### State C — at or above ceiling

Condition: `H >= C`.

Expected native result:

```text
actualHeal = 0
deniedByWound = R
```

This is successful native Severance counterplay, not evidence that Regenerate
failed to tick or requested zero healing.

## P1 answers

1. **Is Regenerate intact when it follows A/B/C?** Yes. Its native functional
   contract is to request its configured heal through `LivingEntity.heal`.
   Tensura's native wound listener then admits only the portion below `C`.
   Exact A/B/C behavior proves both mechanics are executing their own native
   responsibilities.
2. **Does Candidate C alter Regenerate?** No. W3/W4 preserve the configured
   request, 20-tick cadence, rank, synchronous heal event, native call source,
   and `regen=0.01`. Candidate C intercepts only the wound offer inside the
   existing native Severance callback.
3. **Is W4's zero healing explained by State C?** Yes for the recorded matrix.
   All 120 Regenerate-bearing W4 rows produced one callback, all 120 were
   cancelled, and total allowed/actual healing was zero. After each hit, HP was
   at the corresponding `M-W` ceiling within at most `0.00048828125` HP. The
   complete 928.545898 request was therefore denied by State C semantics.
4. **Would healing in State C weaken/bypass Severance?** Yes. Positive healing
   at `H >= C` must either raise/ignore `C`, bypass or alter the Tensura heal
   listener, reduce/clear wound, or special-case Regenerate. Every option
   changes native Severance or Regenerate semantics and is outside this task.
5. **Is positive healing in every window a valid identity rule?** No. It is
   logically incompatible with an active native hard counter whenever the
   target spends the window at its wound ceiling.
6. **What does defender advantage mean here?** Regenerate must retain its
   native rank, cadence, and request, must consume every available legal HP
   space up to `C`, and must improve the defender's trajectory versus an
   otherwise-identical no-Regenerate control while meaningful legal room is
   repeatedly created. It need not, and under native rules cannot, restore the
   wounded portion itself.

## Protocol options

### Protocol H — hard-counter semantics

H is consistent with the installed mechanics. Regenerate retains identity if
its request/rank/cadence are unchanged, it heals fully in State A, truncates in
State B, is denied in State C, and returns to normal when the wound is absent
or expires. Severance remains a genuine hard counter while maintained.

P1 assessment: **semantically valid; runtime confirmation with Candidate C is
required in P2**.

### Protocol S — soft-counter semantics

S requires positive healing even in State C. That cannot occur through the
installed A/B/C contract. It necessarily changes the wound ceiling, the
highest-priority heal-event result, Regenerate, or native wound state.

P1 assessment: **not preservation of native mechanics and not authorized**.
No soft-counter prototype will be implemented here.

### Protocol D — dynamic defender-advantage semantics

D accepts complete denial in State C but requires Regenerate ON to use legal
room below `C` and outperform the matched OFF control during real repeated
damage/heal cycles. It tests gameplay identity without demanding restoration
of wounded HP.

P1 assessment: **the correct functional comparison to test after P2**. It is
compatible with H: H defines the ceiling contract, while D tests whether the
defender still benefits inside that contract.

## P1 decision and gates

W4 established a valid structural result—Candidate C left Regenerate's trait,
rank, tick attempts, and callbacks intact—but its old universal positive-heal
gate was conceptually overbroad. W4 exercised State C only. Its zero actual
healing is affirmative evidence of native Severance enforcement, not by itself
an architecture failure.

This does **not** yet approve Candidate C, `RW=0.5`, production implementation,
or W5. P2 must independently prove exact States A/B/C with a legitimate native
wound and Candidate C present. P3 is authorized only if P2 passes, and must
then test a matched dynamic Regenerate ON/OFF defender advantage.

The provisional replacement gate, subject to P2/P3 evidence, is:

1. native trait, rank, cadence, request, and heal-event source are unchanged;
2. State A heals the complete legal request;
3. State B heals exactly the remaining legal space;
4. State C may be completely denied by native Severance;
5. Regenerate ON is measurably better than OFF when meaningful legal space
   exists during otherwise-identical combat; and
6. Regenerate never heals through the wounded portion.

No production or runtime code changed in P1.

P1 checkpoint: `f38382e68cfb92b41c130a0af831149e1c4cb584`.

## P2 controlled A/B/C runtime proof

Status: **complete; native counter contract passed; P3 authorized**.

The development-only `adaptive_wound_counter_states` fixture used Candidate C
at the already-tested diagnostic `RW=0.5`; this was not tuning. It tested S7
Orc Disaster at Lv600/rank 4 and Lv1000/rank 5. Every wound-bearing case first
released exactly one real `royalvariations:royal_arrow` from the classified
Severance Royal Bow. The ordinary native callback and native Tensura storage
created the wound. TNO never wrote wound state.

After native wound creation, the fixture used one direct vanilla-HP placement
solely to establish A, B, or C. That operation is recorded as
`DIAGNOSTIC_SETUP_ONLY` and excluded from combat output. The target's native
clock was aligned once, then exactly one real tick-20 Regenerate attempt was
observed. The no-wound control fired no arrow; the no-Regenerate control kept a
legitimate wound but removed only Regenerate with its budget unassigned.

| Level / rank | State | Wound | HP before | Ceiling | Legal space | Requested | Actual | Denied |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 600 / 4 | A — below | 1.836914 | 9,573.163086 | 9,998.163086 | 425 | 400 | 400 | 0 |
| 600 / 4 | B — crossing | 1.836914 | 9,798.163086 | 9,998.163086 | 200 | 400 | 200 | 200 |
| 600 / 4 | C — at ceiling | 1.964844 | 9,998.035156 | 9,998.035156 | 0 | 400 | 0 | 400 |
| 600 / 0 | no Regenerate | 1.836914 | 9,573.163086 | 9,998.163086 | 425 | 0 | 0 | 0 |
| 600 / 4 | no wound | 0 | 9,575 | 10,000 | 425 | 400 | 400 | 0 |
| 1000 / 5 | A — below | 1.836914 | 9,473.163086 | 9,998.163086 | 525 | 500 | 500 | 0 |
| 1000 / 5 | B — crossing | 1.836914 | 9,748.163086 | 9,998.163086 | 250 | 500 | 250 | 250 |
| 1000 / 5 | C — at ceiling | 1.836914 | 9,998.163086 | 9,998.163086 | 0 | 500 | 0 | 500 |
| 1000 / 0 | no Regenerate | 1.964844 | 9,473.035156 | 9,998.035156 | 525 | 0 | 0 | 0 |
| 1000 / 5 | no wound | 0 | 9,475 | 10,000 | 525 | 500 | 500 | 0 |

The aggregate is 10 complete cases, eight legitimate setup-arrow rows, eight
native Regenerate callbacks/attempts, 3,600 requested HP, 2,250 actual HP, and
1,350 denied HP. State A supplied 900 actual HP, State B supplied 450, the
no-wound controls supplied 900, and State C denied 900. No-Regenerate supplied
zero requests and zero healing. SHP moved by zero in every case.

All eight setup arrows retained one physical `minecraft:arrow` source with the
projectile tag, one native wound callback/store, unchanged Royal Arrow base,
and the Candidate-C native callback boundary. There were zero errors,
duplicate physical events, recursions, unexpected L2 bypasses, or unexpected
Tensura bypasses.

### P2 interpretation

Candidate C did not change Regenerate's configured request, rank, 20-tick
cadence, call stack, or heal event. Native Tensura admitted the full request in
State A, truncated it to precisely `C-H` in State B, and cancelled it in State
C. Removing wound restored the full native request; removing Regenerate
removed the request entirely.

Therefore W4's zero-healing observation does not prove that Candidate C erased
Regenerate. It proves those W4 targets remained at State C. Protocol H's
counter contract is now runtime-verified, and Protocol D's dynamic paired
Regenerate ON/OFF test is authorized for P3. W5, production implementation,
and `RW` calibration remain unauthorized.
