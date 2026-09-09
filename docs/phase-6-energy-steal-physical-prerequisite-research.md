# Energy Steal physical-prerequisite research

Bounded post-Phase-6 / pre-Phase-7 causal research. **ES1 source audit complete; runtime decision pending.** No production correction or bypass is authorized or implemented.

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

## Checkpoint ledger and resume point

| Checkpoint | State |
|---|---|
| ES1 | Source/bytecode and historical audit passes; commit containing this section is pushed and live-verified before ES2. |
| ES2 | Pending legitimate native positive control and strict corruption-tested runtime evidence. |
| ES3 | Pending Royal causal comparison and only evidence-implicated L2 decomposition. |
| ES4 | Pending bounded final decision, clean build and final push. |

No runtime result, production fix decision or final Energy classification is claimed at ES1. Exact next action: implement and run the ES2 read-only native positive control after remotely protecting ES1. After Energy closes, the next separately reviewed project task is a consolidated readiness assessment of all six Phase-6 families and remaining endgame limitations. Do not start that assessment or original Phase 7 automatically.
