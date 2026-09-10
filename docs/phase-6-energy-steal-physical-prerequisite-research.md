# Energy Steal physical-prerequisite research

Bounded post-Phase-6 / pre-Phase-7 causal research. **ES1, ES2, ES3a and ES3 are validated. ES3 proves the historical empty-world entity-tick suspension mechanism; ES4 and final clean build remain pending.** No production correction or bypass is authorized or implemented. Earlier ES3a uncertainty below records that checkpoint's status; ES3b supersedes it.

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
| ES3a | `b414ffafa67ff989a6e61cbe5eb618a756a9b924`, validated 35-release native Royal comparison, pushed and live-verified. |
| ES3 | Complete bounded causal reproduction below; protect the commit containing ES3b before starting ES4. |
| ES4 | Pending bounded final decision, clean build and final push. |

No final Energy classification or production correction is claimed at ES3a. Resume the historical timing/physical-return comparison described above. After Energy closes, the next separately reviewed project task is a consolidated readiness assessment of all six Phase-6 families and remaining endgame limitations. Do not start that assessment or original Phase 7 automatically.

## ES3b — historical empty-world suspension reproduced

Recovery found a clean working tree at ES3a `b414ffafa67ff989a6e61cbe5eb618a756a9b924`; fetch and live remote lookup matched it. No newer or unfinished Energy work existed. ES1, ES2 and the accepted ES3a experiments were not repeated. The owner's resume instruction specifically authorized observation of the unchanged historical fixture and one-property causal controls.

The historical fixture was traced back to `0cc6005` and compared with its current source. It creates the first native target at each level, saves a pristine pre-combat NBT template, and uses fresh clones for subsequent Stages. Within each case it reuses the target, FakePlayer and mainhand bow for ten releases. Original setup fills target pools/HP, empties attacker MP/AP, and resets invulnerability once per case. The historical creative attacker has explicitly configured capacity attributes; these existing fixture grants are observed, not introduced by this research or proposed as gameplay requirements. The new observer supplies none.

`ServerTick.Post` stabilizes positions and advances the FakePlayer's native item cooldown exactly once. Releases remain 20 server ticks apart in a 200-tick window; the final observation lasts 19 ticks. The original bow `releaseUsing` creates the real Royal Arrow. Its native eligibility is checked, marking and critical-arrow state retain the historical isolation settings, then its own `onHitEntity` is invoked and it is discarded immediately. Its age is zero. No native Energy function is invoked by the fixture. AI is enabled; position stabilization does not advance native entity ticks. Native trait memory is retained across shots and reset only at the next case's profile initialization.

An initial single S7 startup control succeeded **10/10** (`es3b-startup-control.jsonl`). It ended at server tick 212, before the relevant native boundary. This valid diagnostic is preserved separately and is not included in the decisive differential. It rules out immediate dispatch alone as a sufficient cause in this fixture.

The smallest original sequence crossing the boundary is two Lv1000 cases, S0 then S7, retaining the historical pristine-clone policy. The seven accepted Orc traits remain present in both cases. The baseline changes only case selection and adds the existing read-only boundary/resource observers. Its actual physical `hurt` return is captured by the original-once arrow wrapper.

| Capture / Stage | Attempts / incoming / applied / hurt true | Callback / apply / drain / successful drain | Target MP loss | Target AP loss | Physical HP loss / healing |
|---|---|---|---:|---:|---:|
| Original, S0 | 10 / 10 / 10 / 10 | 10 / 10 / 10 / 10 | 520,021.946634 | 110.249998 | 1.522461 / 1.522461 |
| Original, S7 | 10 / 10 / 5 / 5 | 5 / 5 / 5 / 5 | 353,340.540006 | 73.499998 | 1.383789 / 1.338867 |
| Native ticket, S0 | 10 / 10 / 10 / 10 | 10 / 10 / 10 / 10 | 522,617.885268 | 110.249998 | 1.426758 / 1.426758 |
| Native ticket, S7 | 10 / 10 / 10 / 10 | 10 / 10 / 10 / 10 | 686,048.098119 | 146.999997 | 1.426758 / 1.426758 |

**First fixture divergence:** installed NeoForge `ServerLevel.tick` runs its entity loop when the level has real players or `ForcedChunkManager.hasForcedChunks`, or while `emptyTime++ < 300`. The benchmark's FakePlayer is not in `ServerLevel.players`. Without a forced chunk the world stops advancing entities after tick 300, even though the target's chunk still reports `isPositionEntityTicking=true`. The benchmark's server-post-tick scheduler continues issuing immediate collisions and ticking the item's cooldown. The distinction is a suspended world entity loop, not necessarily an unloaded chunk.

The baseline S7 target reaches age **86** at server tick **300**. That shot returns true, sets target invulnerability to **20**, and drains normally. The next five releases at server ticks **320, 340, 360, 380 and 400** find the same age 86, invulnerability 20, `hurtTime=10`, `hurtDuration=10`, and `lastHurt=8`. Incoming is accepted with amount 8. Native `LivingEntity.hurt` then tests `invulnerableTime > 10 && amount <= lastHurt`, returns **false**, and stops before `actuallyHurt` and arrow `after_damage`. This directly proves five instances of `HISTORICAL_PHYSICAL_HURT_FALSE_INVULNERABILITY`. All later Energy boundaries and HP/resource writes are absent on those shots.

**Single-property control:** after preserving that failure trace, the same two-case fixture receives one legitimate native forced-chunk ticket at target chunk `(0,1)`. This keeps the native world loop active and is restored to its previous state at completion. No timer is reset, no entity tick is directly called, and no hit/cooldown/resource/trait rule is bypassed. Empty time remains zero; the S7 target reaches age 106 at server tick 320 and invulnerability has decayed to zero. Both cases succeed 10/10. This is a development fixture control, not a proposed production patch.

Item cooldown is zero at every apply and at all five rejected attempts. Successful calls add 20 before draining; normal FakePlayer clock ticks expire it. The two captures each contain **398** observed tracker ticks, with no reset or phantom cooldown. The separate Energy target timer threshold `<60` does not cause these failures: the arrow never reaches Energy apply. Native Adaptive stores message key `arrow`; its admitted count stops at **5** on the five rejected shots. In the ticket control it reaches **10**. Installed Adaptive applies `pow(0.5, count-1)` only on its admitted `onDamaged` path. No L2 trait caused the first observed rejection; no trait removal is warranted. Accepted ES3a already proves that extremely small physical damage with the full profile can still admit Energy.

Both Stages retain their native percentages exactly once: S0 `0.010499999765306712`, S7 `0.013999999687075614`. In this historical setup attacker headroom permits gains equal to the table's target losses; this differs legitimately from ES2/ES3a's capped attackers. Every setter pair reconciles against the native formulas and all snapshots. HP healing comes from observed native Orc healing, L2 Regenerate or native Self Regeneration; no SHP movement occurs. The original S7 baseline ends 0.044921875 HP below full because its healing loop is suspended. Native initial MP and physical critical rolls vary between runs, so totals are accounting observations, not a paired balance claim.

### Reassessment of the old 269 absences

The old 320 rows remain byte-for-byte untouched: 51 native operations, 269 absent, and 320 incoming observations. All 269 absent rows have zero recorded physical applied amount and no observed MP regeneration. Regeneration first stops at Lv300/S1 hit 5 (zero-based row 14), and is absent in all **306** rows from there onward. Every case's first shot succeeds, consistent with the original per-case invulnerability reset. Six later-than-first successes outside the initial two cases are consistent with the native `amount > lastHurt` exception, which admits only the difference during invulnerability; the old trace cannot prove which incoming event increased the amount.

The source and differential establish the exact suspension/invulnerability mechanism and structurally explain the historical fixture's missing operations. **Zero of the old 269 rows have sufficient direct timer/return data for individual causal attribution.** All 269 remain individually unassigned; they must not be relabeled as 269 directly observed invulnerability failures. No remaining evidence justifies an L2 bypass or a production Energy fix. The corrected live Royal behavior remains the accepted ES3a result; it is separate from this historical fixture diagnosis.

### ES3 validation and checkpoint boundary

`es3b-runtime.jsonl` and `es3b-ticket-runtime.jsonl` retain the complete new observations. Their strict reports pass all **40** decisive rows: **40 attempts, 40 incoming, 35 applied/true hurt returns, 35 callbacks/apply/drain/successes, five directly proven rejections**. Source identity remains native `minecraft:arrow`, five installed tags, original owner/projectile, and zero Resistance bypass. No duplicate drains, recursion, case errors, unexplained resource movement or unexpected bypasses occur. The native ticket is restored.

`es3b-historical-timing-audit.json` retains original/current fixture methods and installed world/hurt/Adaptive/healing bytecode. `es3-historical-reassessment.json` distinguishes new causal proof from old observational signatures. **28 corruption tests** reject manipulated returns, timers, world/target clocks, callback/drain counts, cooldowns, resource accounting, source identity, ordering and Adaptive memory. Both full-stack server runs completed successfully; the Java suite passed **54/54**, zero failures/errors/skips. Observer and locked-production audits pass. Original Phase 6, Magic/Holy, Candidate C, Elemental and Soul evidence remains unchanged.

ES3 is complete and must be committed, pushed and live-SHA-verified before ES4. Exact next task: make the bounded terminal Energy decision, rerun the required evidence/test checks, perform the final clean build, protect ES4 remotely, then stop for owner review. Do not begin the six-family readiness assessment or original Phase 7.
