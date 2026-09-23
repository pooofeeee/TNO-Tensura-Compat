# R2g1 — Ice & Fire native source foundation

IceAndFireCE beta15 is **PARTIAL**. This closes the bounded registry/source-factory foundation, not a combat family or the whole mod. Twilight remains COMPLETE at219/640, all40 types USED, zero REVIEW_REQUIRED. Five accepted reviews/views are preserved.

## Authority

Exact installed IceAndFireCE2.0-beta.15 / Minecraft1.21.1 / NeoForge21.1.244. Reused protected broad discovery parses726 classes; source aids are locators, pinned native method bytes control findings.

## Registries

IafStatusEffects registers exactly frozen (FrozenStatusEffect) and siren_charm (SirenCharmStatusEffect); IceAndFire.init registers that DeferredRegister through the actual NeoForge mod constructor. Five custom DamageType resources: bonus, gorgon, dragon_fire, dragon_ice, dragon_lightning. This is a registry/source census, not whole mechanic or delivery closure.

## Factories

bonusDamage and the direct custom factories construct DamageSource(holder,entity): native direct and causing are both the supplied entity. Indirect factories construct DamageSource(holder,direct,causing); registry is resolved through the causing entity level. No null-owner fallback exists in these Iaf methods. Custom subclasses only add randomized localized death messages; they do not override damage admission or subtract HP.

## Registry fallback

get(entity,key) calls level.damageSources.damageTypes.getHolder(key).orElse(getHolderOrThrow(FELL_OUT_OF_WORLD)). The native fallback lookup is eager before orElse. All five resources exist in the installed archive; runtime registry loading is not asserted. This documents existing native code and authorizes no synthetic fallback or source change.

## Lightning identity

Proven bytecode: causeIndirectDragonLightningDamage loads DRAGON_ICE_TYPE at offset5, while causeDragonLightningDamage loads DRAGON_LIGHTNING_TYPE at offset5. IafDragonDestructionManager.getDamageSource chooses indirect when getRidingPlayer()!=null; its Lightning branch therefore returns iceandfire:dragon_ice, direct=dragon and causing=controlling Player. Unridden Lightning branch returns iceandfire:dragon_lightning with direct=causing=dragon. This actual holder difference is preserved, not corrected.

## Charge identity

DragonChargeEntity.onHit chooses cause=current riding Player if nonnull else shooting Dragon, then calls the projectile subtype causeDamage. LightningDragonChargeEntity.causeDamage uses the DIRECT lightning factory, so the entity-impact source has direct=causing=that cause, not direct=projectile, even with a rider. Its separate destroyArea route delegates destroyAreaCharge/getDamageSource and can select the indirect ice holder. Complete collision, grief, team, amount, effect and hurt-return admission is pending the dragon family review; the two source routes must not be conflated.

## Other callers

Native factory callers include GorgonEntity.aiStep, GorgonHeadItem.releaseUsing and DamageBonusAbility.active in addition to three charge subclasses and the dragon manager. Gorgon entity supplies itself; Gorgon Head supplies the pointed victim to causeGorgonDamage; Bonus supplies attacker. These source arguments are pinned, while full legitimate delivery prerequisites and HP/statue consequences remain pending family review.

## Tags

Scoped raw Minecraft+NeoForge+Iaf closure: bonus only bypasses_cooldown; gorgon bypasses_armor and transitively bypasses_shield; three dragon types only always_hurts_ender_dragons. Burning/freezing in DamageType effects fields is not IS_FIRE/IS_FREEZING membership. Native tags alone do not grant armor/Resistance/Nullification/SHP bypass beyond the exact listed membership; additional installed-mod/datapack alterations need separate attribution.

## Direct compat

tensura_iaf2.0.0.1 explicitly registers eleven required mixins, its common init and IafHandler listeners. Native annotations are pinned with javap. MixinTensuraDamageHelper sets Gorgon isAbnormal, DragonIce isCold, DragonFire isFireDamage, DragonLightning isLightningDamage true, and sets isPhysicalAttack false for those four exact types. Bonus is not in those injected branches. It classifies actual holder identity, not method name: the rider manager lightning route matches the ICE branch. This is static declared code, not runtime mixin-application certification.

## Compat admission

Existing declared compat also extends ColdNullification immune-effects list with frozen; makes Gorgon blindfold predicate true for native immune tag or toggled AbnormalConditionNullification; extends Siren earplug result for toggled SpiritualAttackNullification; cancels IceSpikes step for toggled ColdResistance/Nullification or ThermalFluctuationResistance/Nullification. Other pinned listeners gate dead-model dragons for skill plunder, energy drain and spiritual hurt; statue recipients reject LivingEffectAdded. Family-specific API admission and total hook order remain unreviewed, not inferred from these declarations.

## Exclusions

DragonForge recipe processing, breath-to-forge charging, DragonEssence acquisition, models, sounds, title screens, books, recipes and ordinary utility are short dispositions unless a real combat callback is proven. Data-driven existence/attribute/skill/tag compatibility can be combat-significant and remains scheduled for attribution; no exhaustive utility archaeology.

## Coverage and next checkpoint

726 installed classes scanned;7 direct factory caller methods and6 effect-registry reference methods located. Two registered custom statuses/five custom damage declarations. Zero promoted Ice & Fire mechanics/paths, zero fully reviewed damage profiles; no runtime measurements.

[Native witnesses](native-evidence/iceandfire-foundation.json), [caller census](iceandfire-source-census.json), [damage declarations/tags](iceandfire-damage-tag-census.json), [compat annotations](annotation-evidence/iceandfire-compat-javap.json), [integrity](iceandfire-r2g1-integrity.json).

Validation recollects these54 witnesses and source/tag scans, checks exact factory key offsets/constructor dispatch/registered compat declarations, pinned earlier references, five tooling tests, accepted-view preservation and research-only scope. The complete Twilight full validation is protected at86b6e67; no runtime certification is inferred.

Exact next task: R2g2: trace FrozenStatusEffect plus all actual native producers, effect lifecycle/removal, motion order, eligibility and installed ColdNullification bridge; then Siren charm/Gorgon and remaining combat families. Reuse R2g1 factories, tag census and exact compat declarations. No runtime/L2/Stage/production work.
