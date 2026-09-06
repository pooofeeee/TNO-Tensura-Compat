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
| P2 — controlled A/B/C runtime proof | Not started | Must prove Candidate C leaves native below/crossing/at-ceiling behavior exact. |
| P3 — dynamic defender advantage | Not authorized | Requires P2. |
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
