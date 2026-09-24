# R2k1 — Cataclysm source foundation

Installed Cataclysm native registry/source/tag/hook foundation. Whole mod PARTIAL; no combat family promoted.

Static review only. Future runtime fixtures remain unexecuted; whole Cataclysm review is PARTIAL.

## Authority

Installed L_Enders Cataclysm1.21.1-3.27.jar SHAfa4e8abd15aa86333d6a5fe20b05c4fe423ac865da7319be7808d321bcb3930c;1310 parsed classes. Existing source aids reused only as navigation; registry/resource/class bytecode and annotations pinned. BOMD complete checkpoint bbd92263f0534929416b2ccfad969c472a1c7607 preserved.

## Registries

Native ModEffect registry declares12 effects: monstrous, blazing_brand, stun, abyssal_burn, bone_fracture, abyssal_fear, abyssal_curse, blessing_of_amethyst, curse_of_desert, ghost_form, ghost_sickness, wetness. Cataclysm constructor registers EFFECTS and ATTRIBUTES on mod bus. Attribute keys additional_critical_damage, nature_heal, eat_speed, charge_time are also native; no claim that each is an independently scalable effect.

## Damage definitions

CMDamageTypes declares20 native ResourceKeys. Fifteen have bundled data/cataclysm/damage_type JSON. star_lance, draconic_wound, draconic_slash, draconic_wound_eruption and dagger have no bundled JSON; this does not prove no code caller or absence from a loaded external datapack. Their actual use/disposition remains family review. Do not create substitutes. Registry getHolderOrThrow is retained.

## Sources

Named source factories call native DamageSource(holder,direct,causing) for projectile/caster forms or single-entity constructor for same direct/causing actor. Generic getDamageSource delegates null actor; getEntityDamageSource supplies actor twice. getIndirectEntityDamageSource with empty toIgnore retains supplied direct/causing. With nonempty toIgnore it instead constructs EntityExcludedDamageSource(holder,array), whose constructor invokes super(holder): both entity fields are absent. Its only override is getLocalizedDeathMessage, suppressing credited killer name for listed killer entity TYPES. It is not victim immunity, a no-friendly-fire predicate or a damage callback. Preserve this identity branch before tracing actual caller eligibility.

## Tags

Pinned raw Minecraft1.21.1/NeoForge21.1.244/Cataclysm tag closure saved per15 definitions. Custom bypasses_hurt_time is distinct from vanilla bypasses_cooldown. Flame strike bypasses armor, shield and enchantments; maledictio_anima bypasses shield/enchantments; abyssal_burn bypasses armor/shield and custom hurt-time. No conclusion of damage success against native boss gates/Tensura/L2 follows from those tags. Other pack contributions and runtime load order remain unmeasured.

## Hooks

Installed ServerEventHandler subscribes to player tick, attack/use/interact/target, healing, knockback, incoming damage, post damage, shield blocking, death, crit, effect removal and fall events. LivingEntityMixin HEAD hooks canAttack and both addEffect overloads; FoodDataMixin wraps native Player.heal in FoodData.tick using nature_heal; ItemMixin handles explosion immunity of dropped tagged ITEM entities. IABoss_monster and LLibrary_Boss_Monster consume native custom hurt-time/self-regen/effect tags. Annotation declarations and bytecode are pinned; ordered semantics, source gates, costs and exact Stage point require R2k2/family review.

## Config

Native Cataclysm constructor registers cataclysm-common.toml with COMMON_SPEC, and ConfigHolder load/reload dispatch bakes only matching spec into CMCommonConfig. Installed common file pinned including parsed TOML; cataclysm.toml and .bak are not substituted. Snapshot proves file contents, not live baked runtime values. Per-boss cap/regen/projectile parameters are read when reviewing relevant family.

## Census

Whole-artifact candidate index contains538 watched methods,26 custom-key-reading methods (including factories),32 factory-calling methods,95 vanilla/custom status-reference methods and6 shared boss-tag-reading methods. These are candidate METHOD counts, not completed mechanics, paths, events or runtime hits.15class+66resource witnesses pin foundation; individual boss and gear callbacks remain pending.

## Compatibility

Explicit-name scan across Cataclysm, Tensura and four inventoried compatibility candidates returnszero matches. Cataclysm scan also searches L2 namespace strings. This does not scan/resolve every installed generic L2/Tensura event, trait, tag, attribute or pack override; no compatibility certification. Preserve native direct/causing identity and let native eligibility/Resistance/hooks operate.

## Scope

Foundation only, whole Cataclysm PARTIAL; no promoted mechanics/paths, no inferred custom-versus-vanilla classification campaign. Prior669effects/1620paths/882primitives unchanged. No runtime boss/L2 test, Stage or production implementation, Phase6 reopening or Phase7. Follow bounded combat semantics; skip rendering/acquisition/ordinary utility quickly.


[Machine evidence, packages and native paths](cataclysm-r2k1-source-foundation.json).

Exact next task: R2k2a: Cataclysm shared native boss damage admission/caps/hurt-time, self-heal and effective_for_bosses effect tag; then R2k2b status/control and actual event/mixin interactions for all12 effects, with real producer paths. Resolve20 code keys against15 shipped DamageType definitions during relevant families; never invent missing types. Continue automatically while quota healthy; static only.
