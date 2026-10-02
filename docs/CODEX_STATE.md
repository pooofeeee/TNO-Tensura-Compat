# TNO Tensura Compat — live Codex state

## Purpose

TNO integrates selected external-mod gear and combat mechanics into Tensura progression without replacing the native mechanic.

The core rule is:

`external gear/mechanic -> native owner/mod behavior -> Tensura Gear EP -> TNO Stage -> scale only the eligible native parameter -> native defenses/lifecycle continue`

TNO should extend existing mechanics, not manufacture substitutes.

## Current production baseline

Branch: `codex/production-continuation`

Baseline commit: `a5e85e610349120e21d62f4a80f1b607e36607fe`

This baseline already contains the accepted Phase 6 production system and post-Phase-6 readiness work.

Do not treat `main` as the current implementation baseline.

## Existing Stage system

Stages are S0-S7.

Curve C multipliers:
- S0 1.05
- S1 1.10
- S2 1.15
- S3 1.20
- S4 1.25
- S5 1.30
- S6 1.35
- S7 1.40

Stage is derived from current native Tensura Gear EP. TNO does not own a second EP/Stage progression store.

Current explicit gear mapping:
- `royalvariations:royal_bow` -> TNO Rare

Rare EP thresholds:
- S0: 0
- S1: 41,500
- S2: 207,500
- S3: 830,000
- S4: 1,245,000
- S5: 1,660,000
- S6: 2,075,000
- S7: 2,490,000

## Accepted native Stage integrations

These six families are production baseline and should not be reopened casually:

1. Magic Weapon
2. Holy Weapon
3. Soul Eater
4. Elemental / Slotting
5. Energy Steal
6. Severance

Their implementation principle is already established: scale the eligible native contribution exactly once and preserve the original Tensura source/event/defense path.

Matching Tensura Resistance recovery and Nullification behavior from Phase 6 also remain baseline behavior.

Apotheosis progression remains separate from TNO Stage. TNO must not multiply generic weapon/base/APO damage just because Stage increases.

## Royal Bow integration

Royal Bow is the first implemented external gear integration.

It becomes Tensura Gear, uses native Tensura EP, resolves through the TNO Rare Stage schedule, and performs one authorized first applicable Tensura Engraving roll after successful native gear integration.

That existing behavior is not the remaining goal of the mod; it is the first working example of the wider system.

## Remaining major goal

Generalize Stage so selected combat-significant mechanics from other mods can participate in Stage progression.

The external-effects research branch exists to identify:
- actual mechanic behavior,
- native source/delivery path,
- numerical parameters,
- binary/native gates,
- possible scalable parameter candidates.

Research intentionally did NOT choose production Stage formulas for those candidates.

The next architecture should therefore be a generic External Stage Framework that can map:

`mechanic ID -> primitive/parameter -> scaling policy -> one native hook/boundary`

while keeping native ownership and semantics intact.

## External scaling invariants

Default rules:

- Scale parameters, not whole mechanics.
- Apply Stage once.
- Do not duplicate the native effect, event, projectile, explosion, damage source, or resource operation.
- Preserve native eligibility, immunity, effect merging, cancellation, cure/removal, ownership, source attribution, and return-value semantics.
- Do not Stage-scale binary decisions by default.
- Delayed mechanics may carry an activation-time Stage snapshot when ownership would otherwise be lost.
- Different parameter types may require different policies; do not blindly multiply every number by Curve C.
- Any cap, sign handling, duration rule, probability bound, cooldown direction, or radius bound must be explicit in the implementation contract before rollout.

## Cold research archive

Branch: `external-effects-catalog-research`

Latest protected checkpoint currently known:
`22b6844b0d854b005e32dc2f1b32f4435855e54a`

This branch contains large static research/evidence trees. It is NOT normal startup context.

Several mod reviews are already complete, including Royal Variations, Cult of Azazel, Variants & Ventures, Friends & Foes, Twilight Forest, Ice & Fire, Eternal Starlight, Bosses Rise, and Bosses of Mass Destruction. Cataclysm is partial. Other targets remain unstarted.

Reuse this archive only when the current implementation task needs a specific fact.

The compact `docs/external-stage/integration-manifest.json` now exists, generated only from the nine completed static reviews. It is the preferred first source for future external Stage tasks; the large research branch remains cold evidence for exact follow-up only.

`docs/external-stage/stage-candidate-matrix.json`, generated only from that manifest, is now the preferred source for deciding future external Stage integrations; legacy unscoped names still require mapping review.

Exact component numerical-parameter key recovery now resolves 156 legacy matrix candidates; 33 mechanics still need mapping review. This recovery chooses no Stage eligibility or policy.

Future unresolved mapping review should use `docs/external-stage/mapping-review-packets.json` first and open exact cold evidence only when the packet is genuinely insufficient.

`docs/external-stage/resolved-stage-candidates.json` is now the canonical first input for Stage eligibility/policy work; old research remains cold evidence only.

## Example external candidates already identified

Royal Variations contains verified Stage-candidate parameters such as:
- Dazed: movement-speed and attack-damage coefficients
- Marked: movement, attack damage, attack speed, armor, and recruit/glow-related numeric parameters
- Time Bomb: timer/fuse, fixed explosion damage/radius, and Dazed follow-up duration
- other Royal mechanics also expose candidate parameters

These are candidates only. No generic production formula has been approved yet.

## Generic External Stage Contract core

The reusable contract/policy core exists under `core/stage/external/`. No external mechanic is integrated yet.

## Next implementation milestone

Design and implement the Generic External Stage Integration Contract.

Do NOT begin by integrating every researched mod.

Recommended first pilot after the contract is approved:
1. Royal Variations Dazed
2. Royal Variations Marked
3. Royal Variations Time Bomb

The pilot should prove that the framework can handle:
- a negative debuff coefficient,
- a multi-attribute mechanic,
- a composite/delayed mechanic,

without double scaling or changing native ownership/lifecycle.

## Efficient Codex workflow

For each task:
1. Read this file and only the source files relevant to the task.
2. Search the cold research archive only for exact missing facts.
3. Change the smallest useful surface.
4. Run targeted tests.
5. Record the new stable decision here only if it changes project-wide state.
6. Use full clean build at a meaningful checkpoint, not continuously.

The goal is to finish the mod with minimal repeated research and minimal context usage.
