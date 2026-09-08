# Soul Eater native-event-path research

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

S1 is static evidence only. S2 runtime, S3 causal matrix and S4 decision are pending. No production fix is justified yet.
