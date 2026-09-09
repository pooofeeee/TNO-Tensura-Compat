# Soul Eater native-event-path research

**Final decision: `SOUL_NATIVE_PATH_VALID_NO_FIX`.** Research is complete. No production fix or prototype was introduced. Stop for owner review; Energy Steal physical-prerequisite research is the next separate task and has not started.

## Recovery and scope

Recovered accepted Elemental HEAD `deeb10247883b1825338349b8a6250e39d026a2e` after a clean working-tree inspection, fetch and live remote verification. No newer local/remote Soul work or interrupted runtime existed. Dedicated branch: `phase-6-soul-native-event-path-research`.

Phase 6 Stage and Magic/Holy production remain locked; Candidate C remains rejected and exhausted; Elemental is complete. No Energy Steal, original Phase 7, production correction or Severance work is included.

## S1 — installed native authority

Source audit: [s1-native-path-audit.json](benchmarks/phase6-soul-native-event-path/s1-native-path-audit.json). Reproduce with `scripts/audit-phase6-soul-native-path.ps1 -TensuraJar <installed jar> -JavaHome <Java 21>`. The audit records Tensura 2.0.1.1 artifact/class hashes, JVM descriptors, packaged definitions/tags and immutable historical evidence hash. Inspection used `javap -p -s -c` and local Vineflower 1.10.1 decompilation with inner classes supplied; bytecode is the authority.

Soul Eater is a level-one mainhand engraving supported by the native handheld item tag. Its `tensura:after_attack` component targets the victim with `tensura:spiritual_damage`, `TOTAL_ATTACK_MULTIPLY`, amount 1 and the registry holder `tensura:soul_scatter`. The message ID is separately `tensura.soul_scatter`.

Both native `MixinPlayer.attack` and `MixinAbstractArrow.onHitEntity` inject **after the first physical `Entity.hurt` invocation**, independent of its boolean return. The arrow requires a nonnull weapon stack, living owner, non-Enderman victim and no owner interaction cancellation. The helper iterates mainhand-compatible enchantments and matching conditional effects. `EnchantmentPostDamageWithTypeEffect.apply(...,float)` passes the attempted physical amount. Soul Eater has no random trigger, kill prerequisite or requirement for positive applied physical HP damage at this boundary.

`SpiritualDamageEntity.postDamage(int,EnchantedItemInUse,Entity,float)` rejects target `invulnerableTime >= 40` or nonliving targets; otherwise it constructs the native source with the enchantment holder and owner. Existing TNO code scales this legitimate amount once and runs its existing Resistance recovery before the original `directSpiritualHurt(LivingEntity,Entity,DamageSource,float)` call. No production code is changed by this audit.

The four-argument native helper rejects the `no_spiritual_damage` entity tag and toggled Spiritual Attack Nullification. Toggled Spiritual Attack Resistance rejects amounts at or below current HP/2; larger amounts enter the five-argument helper with 50% resistance. This direct branch reads the toggles itself, not the source's Resistance-bypass metadata. The five-argument helper rejects client/dead/infinite-material targets, disabled labyrinth PVP, Anti Skill, and nonpositive damage after native Spiritual Protection. It then dispatches **Tensura's `SPIRITUAL_HURT_EVENT`**, with changeable resistance, amount and source marked spiritual.

If accepted, native code subtracts SHP, clamps it to zero, marks hurt and syncs. SHP exhaustion causes native HP/absorption zero and death. The normal branch never calls `LivingEntity.hurt`, so ordinary NeoForge incoming/applied HP events are not expected. There is no Soul Eater cost, heal, resource transfer or cooldown mutation in this branch. Physical delivery can independently change HP/resources. `DamagingHandler` has separate Ogre Berserker conversion and Training Dummy feedback branches which interrupt ordinary SHP subtraction; these are native exceptions, not fallback proposals.

Native spiritual immunity and event handlers remain authoritative. Ordinary L2 HP-event mitigation cannot be inferred from the absence of an event on a separate SHP path. The installed native source carries its own bypass tags (listed in the JSON); this research does not add or alter tags. Runtime will separately inspect actual physical and spiritual processing.

The historical Royal Arrow harness invokes the genuine one-argument `AbstractArrow.onHitEntity` and then discards the projectile. Unlike the completed Elemental case, this is a real implemented callback. All 320 historical rows still truthfully report absent ordinary `soul_scatter` HP events; historical SHP movement must be evaluated independently. Historical files are unchanged.

**Testable hypothesis:** the old observer mistook ordinary HP-event absence for native Soul-effect absence. An eligible native control and genuine Royal Arrow should show a native callback, spiritual event and SHP movement while ordinary Soul HP-event counts remain zero. Boss exclusions may occur at the direct native spiritual gates.

**S2 plan:** use a normally ticking, native-eligible living target and a survival FakePlayer with a legally enchantable native bow or sword. Use actual attack/release and collision; do not call a Soul callback. Add a no-enchantment control. Observe physical attempt/return/events, Soul callback, source, helper result, spiritual-event result and resources at each boundary without changing arguments, cancellation or state. Armor stands are excluded from the neutral control because the installed native tag explicitly rejects them.

S1 checkpoint: `5f83978c06dfdd620ce33f14f46511aa50378df0`, pushed and remote-verified before S2. All 320 historical rows also contain a lower final SHP value; absence of HP events was not evidence of absent spiritual damage.

## S2 — legitimate native positive control

The full installed stack completed two naturally ticking vanilla-bow/vanilla-arrow cases against real Iron Golems. The native enchantment API accepts Soul Eater on the bow. Fresh survival FakePlayers have no granted skills or resources. Targets retain native spawn initialization and native AI; no HP, SHP or cooldown setters are used in the runner. Iron Golems have no applicable native L2 mob config, so the neutral target retains that exclusion. Boss comparison will still require initialized native L2 profiles.

Formal evidence: `s2-runtime.jsonl`, `s2-validation.json`, `s2-extractor-tests.json`, `s2-provenance.json` in the evidence directory. The plain control applied 8 physical HP damage with zero Soul callbacks and unchanged SHP (278). The Soul Eater control applied 7 physical HP damage (112 → 105), invoked one native Soul callback/source/spiritual event, and removed 7 SHP (224 → 217). Native `ExistenceStorage.handleSpiritualHealthRegen` later restored 2 SHP, leaving 219. Both have zero ordinary Soul incoming/applied HP events. Other recorded target/owner resources remain unchanged.

The read-only observers bracket the existing physical/helper/storage calls once and inject noncancellable observations at the Soul callback and native event invocation. They do not change values, results, defenses or order. The general storage ledger records both actual native subtraction and later native recovery; the strict extractor reconciles every observed SHP state against those paired writes. Source identity, owner, exact runtime tags, physical admission, callback order, native amount, all resource accounting and projectile uniqueness are independently checked. Nine corruption tests reject missing physical/spiritual events, substituted sources/tags, duplicate delivery/write, invalid prerequisites, wrong resources and reordered callbacks.

Diagnostic 1 is preserved as a failed setup (neutral Iron Golem has no native L2 config). Diagnostic 2 is a successful exploratory trace predating the complete native recovery ledger; it is not the formal result. Natural entity attribute and arrow critical-roll variation make their numeric damage different from the formal run. No damage or target eligibility was changed to obtain success.

Validation: full-stack server completed and shut down; `gradlew.bat build -Pphase5f_runtime_mods_dir=run/elemental-runtime-mods` passed, with 54 existing Java tests and nine extractor corruption tests. Existing optional-mod startup warnings remain; no research/mixin/runtime error occurred in the formal run. S3 and S4 are pending; no production correction has been made.

## S3a — recovered comparison capture, follow-up pending

S2 checkpoint is `34457ee5eb2a9c1eba76353faf711da0e1f9bce4`. After the usage interruption, fetch/live-remote inspection found this same HEAD, no newer commits and no running server. Uncommitted S3 observers, diagnostics and a completed 20-case runtime were preserved. S1/S2 were not rerun.

The recovered `s3-runtime.jsonl` now passes independent event/resource reconciliation and 13 corruption tests. Its 20 cases compare historical direct native arrow collision with genuine ticking Royal Arrow collision in the same two-block final lane, at S0/S7, against neutral Iron Golem and accepted Lv1000 Orc, Gazel, Luminous and Hinata profiles. Neither route calls a Soul callback or manufactures a source. Natural-flight rows retain native critical rolls; historical rows reproduce the old no-critical/Mark-disabled fixture, so absolute physical amounts need not match. Stage is checked against each actual native callback amount.

Nineteen cases reach physical attempts. All nineteen reach the native Soul callback, fifteen construct Soul sources and twelve dispatch native spiritual events and subtract SHP. Ordinary Soul HP incoming/applied events remain zero. Gazel's native encounter opening sets cooldown 80 and prevents source creation. Hinata's **physical Resistance** cancels HP incoming and her separate spiritual Resistance rejects the Soul amount at HP/2. Luminous's physical Nullification cancels HP incoming but does not exclude this separate spiritual path; native healing later restores SHP.

Two extractor assumptions were corrected from evidence: recipient Magicule gain can be capped despite a native drain, and target age need only show actual native ticking rather than match an arbitrary twenty-tick minimum. Luminous also spends Magicules on her native Universal Perception/regen and may drain the shooter through her existing AI; all such writes are separately reconciled, not attributed to Soul Eater or used to begin Energy Steal research.

One old observer filter omitted the NEB addon namespace. Row 15's SHP +50 is attributed by its immediately adjacent native `LuminousValentineEntity.tick` HP heal(10) and the exact installed bytecode sequence (see `s3-native-audit.json`). The SHP write and persistent amount are directly captured; that specific caller attribution is a reconstruction from adjacent runtime evidence and installed code. Native NEB addition can exceed SHP maximum until later ticks. No normalization was introduced.

Row 19 (Hinata natural S7) has **no physical attempt**, a still-live projectile aged four ticks after 25 server ticks, and no Soul callback or resource change. It is explicitly a flight observation gap, not a Soul defense result. A focused native-flight follow-up and two Royal no-Soul controls remain unfinished. The prior diagnostics preserve shorter observer versions and actual trajectory misses unchanged. S3 is not complete until those follow-ups, final validation and remote protection; S4 has not started.

## S3 — completed causal comparison

Recovered work was first pushed and remote-verified as S3a `c882e1885ed925f1dc24e47cf6c8960ad1400caa`. Only the three unfinished cases were then run with `-Pphase6_soul_followup=true`, in a lane centered inside the forced chunk. No S1/S2 runtime or completed S3 case was repeated. The two Royal no-Soul controls (S0/S7) applied 9 and 8 physical HP damage, with no Soul callback/source/event and unchanged SHP. The Hinata S7 follow-up reached one real physical attempt, one incoming cancellation by physical Resistance, one Soul callback/source and the native spiritual HP/2 rejection. The earlier missing collision is preserved; its exact trajectory cause is not claimed proved.

Formal follow-up: `s3f-runtime.jsonl`, `s3f-validation.json`, `s3f-extractor-tests.json`. `s3-comparison.json` is reproduced by `scripts/analyze-phase6-soul-native-path.ps1`, which revalidates both captures and cross-run projectile uniqueness. Across 23 Royal releases (including the preserved missed shot), there are **22 physical attempts, 18 physical incoming events, 10 physical applied events, 20 Soul callbacks, 16 native Soul sources and 12 accepted spiritual events/SHP subtractions**. Ordinary Soul HP incoming/applied counts are zero. Each spiritual-event acceptance is established by its native SHP write and true helper return. No duplicate physical/Soul delivery or recursion occurs.

| Target | Physical attempts / incoming / applied | Soul callback / source / spiritual event | Gross SHP loss | Later SHP recovery |
| --- | --- | --- | ---: | ---: |
| Neutral (includes two plain controls) | 6 / 6 / 6 | 4 / 4 / 4 | 48.30 | 10.00 |
| Orc | 4 / 4 / 4 | 4 / 4 / 4 | 40.25 | 10.00 |
| Gazel | 4 / 0 / 0 | 4 / 0 / 0 | 0 | 0 |
| Luminous | 4 / 4 / 0 | 4 / 4 / 4 | 46.20 | 78.00 |
| Hinata (plus one preserved miss) | 4 / 4 / 0 | 4 / 4 / 0 | 0 | 0 |

HP is independently attributed to the ordinary physical event and paired native health setters. Orc's L2/ordinary HP mitigation and healing remain active. Its SHP loss does not pass through ordinary L2 HP-event mitigation. Luminous's later SHP gains come from installed regeneration/NEB tick behavior, with actual costs and capped boss-AI drains separately recorded. No Soul invocation itself costs or transfers the observed owner/target Magicules or Aura. Soul source IDs/tags remain exact native values; Stage scales the legitimate amount once (S0 1.05, S7 1.40), with no added physical multiplier or Soul effect in plain controls.

No selected profile has active **spiritual** Nullification. Its unchanged native early return is source-proven, not claimed exercised at runtime. Physical Nullification is exercised by Luminous. Hinata's native direct spiritual Resistance still uses HP/2 even when the existing S7 recovery code sets source Resistance metadata to 1; this is a native target limitation, not evidence of a missing Soul callback prerequisite. SHP-zero death, Berserker conversion and Training Dummy special behavior are source-only observations.

S3 checks: both strict captures pass; 13 comparison corruption tests and eight focused follow-up corruption tests pass. Full-stack runtime completed normally. The original 320-row evidence and accepted production files remain unchanged. S4 remains pending until this checkpoint is pushed and verified.

## S4 — final decision and validation

S3 was pushed and remote-verified at `cabc3a658ff53800bcd3fcafd49eb7edafcb8435` before S4. Final machine decision: [s4-decision.json](benchmarks/phase6-soul-native-event-path/s4-decision.json).

**Root cause of the historical conclusion:** ordinary NeoForge HP-event observation was used to infer absence of an effect delivered through Tensura's separate spiritual event and SHP storage. All 320 original rows already showed SHP loss. Both historical Royal collision delivery and real native ticking reach Soul Eater when native conditions allow it. This is not the Elemental empty-collision-overload defect. No missing production prerequisite is proved, so there is no justified native-path fix and no prototype.

Exact path: native bow release creates an owned arrow retaining its enchanted weapon; native `AbstractArrow.onHitEntity` attempts ordinary physical `Entity.hurt`; Tensura's AFTER_ATTACK hook runs independently of that result; `TensuraEnchantmentHelper.doAdditionalAfterAttack` selects Soul Eater; `EnchantmentPostDamageWithTypeEffect.apply` passes TOTAL_ATTACK_MULTIPLY damage; `SpiritualDamageEntity.postDamage` checks cooldown/living target and constructs the native `tensura:soul_scatter` holder source with the owner; existing TNO Stage/Resistance integration runs once; native `directSpiritualHurt` enforces spiritual eligibility/defenses and dispatches `SPIRITUAL_HURT_EVENT`; accepted continuation writes SHP and syncs. Ordinary Soul HP incoming/applied events are absent by design in this branch.

Permanent Stage, Magic/Holy, Royal physical damage, Resistance/Nullification, L2 and Candidate-C behavior remain unchanged. Git comparison against accepted Elemental HEAD verifies all pre-existing core, compatibility, production mixin and data files unchanged; historical viability and Elemental evidence are unchanged. New runner activation requires the explicit research flag and a non-production environment; observer calls return without work outside the active research session. No observer changes damage/source/eligibility arguments or event results; wrapped calls invoke the original once.

`gradlew.bat clean build -Pphase5f_runtime_mods_dir=run/elemental-runtime-mods` passed. The 54 Java test results contain zero failures/errors/skips; Gradle reused three matching cached tasks. Before cleaning generated output, the entire prior build directory (including earlier ignored Elemental inspection work) was copied into `run/soul-preclean-build.zip`. Raw logs remain under `run/`; machine evidence and diagnostics are committed. Both formal comparison captures pass strict extraction; 21 S3/S3F corruption tests pass, in addition to the accepted nine S2 tests. Formal runtimes complete and shut down without research/mixin failures; existing optional-mod startup warnings are not claimed absent.

Checkpoint record:

| Checkpoint | Verified commit |
| --- | --- |
| S1 source audit | `5f83978c06dfdd620ce33f14f46511aa50378df0` |
| S2 native control | `34457ee5eb2a9c1eba76353faf711da0e1f9bce4` |
| S3a recovered partial protection | `c882e1885ed925f1dc24e47cf6c8960ad1400caa` |
| S3 completed comparison | `cabc3a658ff53800bcd3fcafd49eb7edafcb8435` |
| S4 final decision | The commit containing this final section and `s4-decision.json`; full live-verified SHA is reported to the owner after push. |

This is a bounded native-path result, not sustained viability, full-roster, multiplayer or damage calibration. Native target limitations remain documented above, including the preserved flight miss and reconstructed NEB recovery attribution. Original Phase 7, Energy Steal and renewed Severance/Candidate-C work remain unstarted. **Next task after owner review: Energy Steal physical-prerequisite research.**
