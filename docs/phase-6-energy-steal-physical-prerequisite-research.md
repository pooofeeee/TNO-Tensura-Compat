# Energy Steal physical-prerequisite research

Bounded post-Phase-6 / pre-Phase-7 causal research. **ES1, ES2 and intermediate ES3a are validated. Historical failure diagnosis and ES4 remain unfinished.** No production correction or bypass is authorized or implemented.

Branch: `phase-6-energy-steal-physical-prerequisite-research`.
Accepted base: `38262bfa99ca4cecd3a2ba58cdb8cc6595893a4c` (Soul final, `SOUL_NATIVE_PATH_VALID_NO_FIX`). Fetch found no newer local or remote Energy work; the working tree was clean. No applicable `AGENTS.md` was found. Stage/Curve C/native EP and Magic/Holy production remain locked. Candidate C remains rejected and exhausted. Elemental and Soul are accepted, completed research; original Phase 7 remains unstarted.

Evidence: [phase6-energy-steal-physical-prerequisite](benchmarks/phase6-energy-steal-physical-prerequisite/es1-native-path-audit.json). The installed Tensura 2.0.1.1 JAR is the authority, with NeoForge 21.1.248 patched Minecraft 1.21.1 and installed L2 Hostility 3.0.18. Artifact and class hashes, descriptors, native definition/tags, and relevant disassembly are retained in ES1. Local readable decompilation used Vineflower 1.10.1; conclusions were checked against `javap -p -s -c`.

## ES1 — installed prerequisites

Native `energy_steal.json` registers one `tensura:after_damage` effect: enchanted attacker, affected victim, mainhand, level I, percentage `linear(0.01,0.01)`, cooldown 20. Its supported item tag is `tensura:handheld_enchantable`, including `ranged_enchantable` -> vanilla bow/crossbow enchantable tags. Bow/projectile delivery is native. Legal item admission must also be checked in the running registry; research does not force an incompatible enchantment.

The arrow chain is:

1. Genuine release and native collision -> `AbstractArrow.onHitEntity` -> `Entity.hurt(source, amount)`.
2. Only the true branch continues to the server-side living-victim post-attack effects call. Enderman returns earlier. In the pinned patched bytecode, `hurt` is offset 298, `ifeq 609` at 301, Enderman return at 309, and `doPostAttackEffectsWithItemSource` at 391.
3. Tensura `MixinAbstractArrow` injects **after** that post-effects invocation (ordinal 0), requires a nonnull stored weapon and living owner, then calls `TensuraEnchantmentHelper.doAdditionalAfterDamage` with the physical source and attempted amount. Unlike the separate `after_attack` hook, this after-damage injection has no additional `SkillUtils.shouldCancelInteraction` check.
4. The helper iterates the nonempty stored stack's enchantments in MAINHAND; matching slot, targeted effect/conditional context, and nonnull affected entity are required. Energy targets the victim and implements `EnchantmentPostDamageEffect`.
5. `EnergyStealEntity.apply(..., float originalDamage)` ignores `originalDamage` and calls `applyEnergySteal(level, enchantedItem, victim)`.
6. Target must be alive, living, and have `invulnerableTime < 60`. For a player owner, the weapon item's native cooldown must be inactive. Native code sets cooldown **before** calling the drain, even if the drain subsequently fails. Nonplayer living owners skip this player cooldown branch.
7. The existing TNO wrapper scales the already-existing call's percentage only for `percentage=true`, `DrainType.EP`, `GainType.NORMAL`, and calls the original exactly once.
8. Native `EnergyHelper.drainEnergy` applies its immunity/protection/event gates, performs native resource accounting, then returns. A true result controls the sound, not whether cooldown was charged.

Melee uses Tensura `MixinPlayer.attack`, after `EnchantmentHelper.doPostAttackEffects` ordinal 1 on the successful primary attack path. Both effect `apply` overloads delegate to the same `applyEnergySteal`. Melee setup/admission differs from projectile collision, but the resource operation is shared. No Energy-specific random chance, affinity, skill prerequisite, minimum owner EP, or positive `originalDamage` test exists here.

**`hurt == true` is the arrow prerequisite; positive measured HP loss is not a separate Energy condition.** Patched `LivingEntity.hurt` can reject before incoming damage (invulnerability/client/dead/fire resistance), at incoming cancellation, or during its invulnerability comparison. Target overrides can reject still earlier. Zero applied HP damage alone does not prove `hurt == false`: the normal final return is based on shield-block state and remaining damage. Runtime must distinguish attempt, incoming, post event, HP write, return, and effect admission. The effect's `<60` target timer gate is separate from ordinary physical invulnerability frames.

### Native helper gates and accounting

`drainEnergy(LivingEntity, Entity, double, boolean, DrainType, GainType):boolean`:

- Nonpositive amount rejects; multipart victims resolve through `ILivingPartEntity.checkForHead`.
- `hasEnergyDrainImmunity` rejects infinite-material targets, the `NO_ENERGY_DRAIN` tag (whose actual ID is **`tensura:no_current_ep_drain`**), disabled labyrinth PvP, or a different target with Anti Skill toggled or in its active ability preset. The tag contains `non_living`, Ifrit Clone, Evil Centipede Body and Tempest Serpent Body. `non_living` includes armor stands and training dummies. Iron Golem is not excluded by this packaged tag.
- Energy Protection reduces the amount by `1 - level * 0.1`; a nonpositive result rejects. The native `ENERGY_DRAIN_EVENT` may change amount, percentage flag, drain type and gain type; an event false result rejects. Observers must never edit these values.
- EP drains **current Aura and current Magicules separately**, each `min(current, current * percentage)` in the percentage branch. It does not use maximum pools, Gear EP, HP or SHP. Each resource branch requires its corresponding target maximum attribute. Neither attribute present returns false. Zero pools alone do not return false; a valid attribute can produce a successful zero transfer.
- Order is native attacker Aura gain, target Aura subtraction, attacker Magicule gain, target Magicule subtraction. Missing/dead/nonliving attackers may receive nothing while the victim still loses resources. Native gain resolves multipart owners to their heads.
- `GainType.NORMAL` caps each gain at the minimum of its maximum attribute and positive spiritual limit **when current <= cap**. If already above cap, it permits `current + gain`. Storage setters also clamp above `2,147,483,647`. Thus requested drain, target loss and attacker gain are distinct quantities; equal transfer is not guaranteed.
- After accepted accounting, storage is marked dirty and the native attacker is marked as hurting the victim. `ExistenceStorage.getEP()` is current Aura + current Magicules. If that sum is nonpositive and the target is alive, native code creates `tensura:energy_drain`, records lethal damage, sets HP/absorption to zero and invokes death. Normal nondepleting Energy Steal creates no DamageSource and does not directly damage HP/SHP. Research must not fabricate this exceptional native death branch or generalize “no source” to all possible helper outcomes.
- Successful accounting returns true and allows native sound. Target zero pools, attacker capacity and cooldown are not equivalent rejection states.

The drain does not directly consult matching damage Resistance/Nullification or create a normal L2 damage event. Those defenses can remain decisive on the prerequisite physical call; Energy Protection, Anti Skill, entity exclusions and game rules also remain authoritative. L2 causality has not yet been isolated in this task.

### Historical reassessment and hypothesis

The unchanged historical `phase6-endgame-viability/energy_steal.jsonl` contains 320 rows: 51 native events and 269 absent operations. **All 320 contain one physical incoming observation**, including all 269 failures. The old `failureReason` function labels any absent Energy operation `PREREQUISITE_HIT_FAILED`; it did not record the actual physical return, Energy apply entry, item cooldown at that entry, or native drain return. Therefore the label alone does not prove a Tank/Dementor/Adaptive cause.

The old Royal fixture invoked the real arrow `onHitEntity` and discarded afterward. This is distinct from Elemental's accepted empty callback defect. It emptied attacker pools at setup and ticked the native FakePlayer cooldown tracker once per server tick. Those fixture choices are relevant to interpreting equal transfer and timing; they are not new production requirements.

Testable hypothesis: the 269 absent operations may combine physical rejection, the post-hurt target gate, item cooldown and native helper rejection. L2's reduced HP amount alone cannot distinguish them. ES2/ES3 must observe the first divergence directly.

### ES2 design

Use a naturally spawned and ticking neutral Iron Golem and survival FakePlayer, with no resource or capacity grants. Compare legal vanilla bow/plain arrow with and without Energy I, using real release and collision. Preserve native owner, weapon, crit and damage. Record read-only physical attempt/incoming/applied/return, callback/apply/drain entry/return, percentage before/after TNO, cooldown, capacities and all HP/SHP/MP/AP writes. Model native player cooldown ticking in the fixture scheduler; never reset it in an observer. Strict extraction must reject missing or forged boundaries, duplicates, source/percentage errors, wrong resource accounting, bad ordering/cooldown and unexplained mutations.

## ES2 — legitimate native positive control

ES1 was pushed and live-verified at `7bcbcdd4c4f43712e0fbe33a13ae5001a53e2d99` before implementation. The opt-in `phase6_energy_native_path` runner uses real vanilla bow release and naturally ticking arrow collision against normally spawned Iron Golems. It preserves native crit, source, owner and stored weapon. Targets tick with AI enabled; no HP/SHP/MP/AP or capacity grants/reset, manual hit dispatch, forced cooldown success or direct Energy invocation occurs. FakePlayer's native cooldown tracker is advanced once per server tick because FakePlayers are not in the real player list. This scheduler action is separately observed.

| Control | Attempt / incoming / applied / hurt true | Callback / apply / drain / true | Physical HP loss | SHP delta |
|---|---|---|---:|---:|
| Vanilla plain | 1 / 1 / 1 / 1 | 0 / 0 / 0 / 0 | 7 | 0 |
| Vanilla Energy I | 1 / 1 / 1 / 1 | 1 / 1 / 1 / 1 | 6 | 0 |

Both retain `minecraft:arrow` and its five installed tags, with zero Resistance bypass metadata. Native crit and independent native mob initialization account for different physical inputs/maxima; this is an admission/accounting control, not a paired damage-balance claim. Vanilla bow is unclassified by TNO, so the observed percentage remains widened native float `0.009999999776482582`, with no Stage gain.

The Energy target begins with 6,156 Magicules and 57 Aura. The drain removes **61.559998624026775 MP and 0.5699999872595072 AP**. The attacker remains at its native 50/50 capacities, receiving **0 MP and 0 AP**. Four observed native writes occur in exact Aura gain/subtract, Magicule gain/subtract order. Later native regeneration adds 15 MP and restores the lost Aura; the final MP is 6,109.440001375973. The plain target's energy is unchanged. Neither SHP pool changes. No normal drain DamageSource is created.

Cooldown is zero at callback/apply, set to 20 before drain entry, still 20 at drain return, then decrements through the native clock to zero. The capture records 25 native cooldown ticks per control. All 60 HP/SHP/energy setter pairs reconcile against every trace snapshot and final state, including Apotheosis's unchanged-health bookkeeping and later Tensura resource regeneration. No phantom operation, duplicate drain, recursion, unexplained resource change or unexpected defense bypass was observed.

Artifacts: `es2-runtime.jsonl`, `es2-validation.json`, `es2-extractor-tests.json`, `es2-observer-audit.json`, `es2-provenance.json`. Strict extraction independently recomputes percentage, target subtraction, native capped gain, operation ordering and cooldown transitions. All **15** corruption tests reject, including coherently altered transfer ledgers whose snapshots still balance: the independent native formula rejects the false loss/gain. Full compatibility-stack `runServer` completed successfully; `compileJava test` passed **54 tests**, zero failures/errors/skips. Static audit confirms opt-in/read-only instrumentation, one original physical call and unchanged locked production code. Final `clean build` remains required at ES4. Optional-mod startup diagnostics are not represented as research failures.

## ES3a — protected Royal comparison, historical cause still open

ES2 was pushed/live-verified at `86e0b6c24e619c6e3d6216590016478af7ed28ec` before this work. A subsequent owner resume instruction arrived during ES3; fetch and local/remote inspection again found that ES2 checkpoint and preserved the local ES3 work. ES1/ES2 experiments were not repeated.

The corrected matrix uses real Royal Bow release and the released arrow's native ticks/collision. Initial final-lane positioning preserves speed, damage, owner, stored weapon and natural critical behavior. The three Orc cases preserve the same target, attacker, weapon, resources, item cooldown and native trait data across ten releases at a 20-server-tick cadence. Target native ticks advance by exactly 20 per observation window. No traits are removed. The accepted Lv1000 Orc profile remains Adaptive 5, Dementor 1, Dispell 2, Drain 2, Regenerate 5, Tank 5, Wither 1. Natural current resource pools differ across separately spawned cases; absolute drain totals are accounting observations, not matched balance comparisons.

| Case | Releases | Attempt / incoming / applied / hurt true | Callback / apply / drain / true | Target MP loss | Target AP loss |
|---|---:|---|---|---:|---:|
| Neutral Royal plain S0 | 1 | 1 / 1 / 1 / 1 | 0 / 0 / 0 / 0 | 0 | 0 |
| Neutral Energy S0 | 1 | 1 / 1 / 1 / 1 | 1 / 1 / 1 / 1 | 60.101999 | 0.556500 |
| Neutral Energy S7 | 1 | 1 / 1 / 1 / 1 | 1 / 1 / 1 / 1 | 87.695998 | 0.812000 |
| Lv1000 Orc Royal plain S0 | 10 | 10 / 10 / 10 / 10 | 0 / 0 / 0 / 0 | 0 | 0 |
| Lv1000 Orc Energy S0 | 10 | 10 / 10 / 10 / 10 | 10 / 10 / 10 / 10 | 76,802.463535 | 16.170000 |
| Lv1000 Orc Energy S7 | 10 | 10 / 10 / 10 / 10 | 10 / 10 / 10 / 10 | 97,391.905687 | 22.399999 |
| Lv1000 Gazel Energy S7 | 1 | 1 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | 0 | 0 |
| Lv1000 Luminous Energy S7 | 1 | 1 / 1 / 0 / 0 | 0 / 0 / 0 / 0 | 0 | 0 |

Totals: **35 attempts, 34 incoming events, 33 applied events/true hurt returns, 22 Energy callbacks, 22 apply calls, 22 drain entries, 22 successful returns.** Thirty-five unique reported projectiles each have one physical attempt. All sources remain native `minecraft:arrow` with unchanged installed tags and zero Resistance bypass metadata. No Energy operation or cooldown is created on plain controls or rejected physical hits.

All admitted native percentages are independently checked as widened float 0.01 times the existing S0 1.05 or S7 1.40 coefficient, exactly once: `0.010499999765306712` and `0.013999999687075614`. Every attacker remains at native 50/50 capacities and receives zero MP/AP despite native target subtraction. Native cooldown is zero at every admitted apply, becomes 20 before drain, and reaches zero through normal tracker ticks before the next collision. All 700 native cooldown ticks and every resource write reconcile; the extractor also rejects resets between repeated releases.

Physical HP losses are 8/12/8 on neutral plain/S0/S7, and total 2.1123046875 / 2.478515625 / 2.37109375 on the three Orc cases. Native Orc `healAndEat` and L2 Regenerate restore the losses. There is no SHP change. The last S0 and S7 Orc applied amounts are both `0.0020164489`, yet hurt returns true and native Energy drains. This disproves the inference that a very small physical amount necessarily prevents this native operation in the tested live setup. It does not isolate each trait's individual effect or establish the exact historic failure cause.

Gazel is the native pre-incoming control: its phase-0 `hurt` changes phase to 1, sets target invulnerability to 80 and returns false before normal incoming processing. Luminous is the incoming-cancellation control: native Physical Attack Nullification remains toggled; incoming is cancelled and hurt returns false. Neither reaches `after_damage`. Their native rules remain authoritative. No other boss or Lv800 experiment was needed for these two specific gates.

### Diagnostic preserved, not accepted comparison evidence

`es3-diagnostic1.jsonl` is the untouched first diagnostic. A new repeat scheduler called `release()` at the end of a row and then again at step 20 on the next tick. Later rows consequently contained two distinct real projectile attempts, one inconsistent with the reported row UUID. This was a **research fixture error**, not a production duplication or native Energy defect. The corrected scheduler resumes at step 21 after its already-issued release. Strict extraction rejects the original diagnostic. Only `es3a-runtime.jsonl` is the corrected, accepted intermediate capture. No evidence was overwritten or selectively repaired.

### Validation and remaining uncertainty

`es3a-validation.json` passes all 35 rows; `es3a-extractor-tests.json` rejects **19** corruptions, including coherent false resource transfers, duplicate/forged events, wrong Stage, wrong source, cooldown errors, changed L2 profile and actor resets. The installed native audit records the Gazel return and Orc native healing bytecode. `es3a-observer-audit.json` confirms opt-in read-only observation and unchanged locked production. Full-stack runtime succeeded; Java tests passed **54/54**, zero failures/errors/skips. Corrected official evidence contains zero case errors, duplicate drains, recursion, unexpected bypasses or unaccounted resource mutations. The invalid diagnostic is accounted for separately.

The **historical 269/320 absent operations remain causally unresolved**: this live Royal matrix produced 10/10 Energy success at both S0 and S7 on the accepted Orc profile. The old capture has no target tick/timer, physical return or callback/cooldown observations. Its manual physical dispatch and lack of an unconditional entity-ticking guarantee are relevant differences to investigate, but a frozen-target/invulnerability explanation is only a hypothesis. It is not established by ES3a and must not be promoted to a root cause. No L2-linked admission failure has yet been reproduced, so trait-removal decomposition is not justified yet.

**Save-mode boundary:** preserve and push this validated intermediate checkpoint before further experiments. ES3 is not complete and there is no ES4 decision. Exact resume action: inspect the old fixture's native entity-tick/invulnerability progression and physical-return boundary, design the smallest permissible genuine-delivery comparison that distinguishes that timing difference from native/L2 rejection, and continue only with evidence-implicated controls. A bounded longer native repeated-hit control can separately test whether actual HP float rounding reaches zero while Energy remains admitted. Do not rerun ES1/ES2 or the accepted 35-release matrix without a specific evidence problem. Final clean build and terminal decision remain pending.

## Checkpoint ledger and resume point

| Checkpoint | State |
|---|---|
| ES1 | `7bcbcdd4c4f43712e0fbe33a13ae5001a53e2d99`, pushed and live-verified. |
| ES2 | `86e0b6c24e619c6e3d6216590016478af7ed28ec`, pushed and live-verified. |
| ES3a | Validated 35-release native Royal comparison; commit containing this section and its evidence is remotely protected before continuing. |
| ES3 | Historical 269 failures not causally reproduced; only evidence-implicated L2 decomposition is permitted. |
| ES4 | Pending bounded final decision, clean build and final push. |

No final Energy classification or production correction is claimed at ES3a. Resume the historical timing/physical-return comparison described above. After Energy closes, the next separately reviewed project task is a consolidated readiness assessment of all six Phase-6 families and remaining endgame limitations. Do not start that assessment or original Phase 7 automatically.
