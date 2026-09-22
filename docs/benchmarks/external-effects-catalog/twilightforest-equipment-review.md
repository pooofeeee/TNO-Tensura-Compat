# r2f8m - TWILIGHT_EQUIPMENT_SEMANTIC_REVIEW_COMPLETE

Installed Twilight4.8.3345 outer and nested ASM bytes, raw Minecraft1.21.1 and exact NeoForge21.1.244. Static only. HP requests, ignition, retaliation, source replacement, shatter and equipment stats remain distinct. No runtime/L2/Stage/production/fix. Protected Frosted/Yeti/parry/Knightmetal/Minotaur/giant and scepter contracts are reused, not reopened.

Adds 8 reviewed packages / 24 delivery cases. Twilight remains PARTIAL at 155/476 drafts, zero promoted. REVIEW_REQUIRED 0.

## Native contracts

### Authority

Installed Twilight4.8.3345 outer and nested ASM bytes, raw Minecraft1.21.1 and exact NeoForge21.1.244. Static only. HP requests, ignition, retaliation, source replacement, shatter and equipment stats remain distinct. No runtime/L2/Stage/production/fix. Protected Frosted/Yeti/parry/Knightmetal/Minotaur/giant and scepter contracts are reused, not reopened.

### Fiery incoming

ToolEvents.setup registers fieryToolSetFire on LivingIncomingDamageEvent. If causing entity is Living, its CURRENT main-hand item is exactly FIERY_SWORD or FIERY_PICKAXE, and recipient !fireImmune, invokes igniteForSeconds1. No direct-melee, positive amount, hurt-success, range/LOS, boss/team or explicit side/cancel predicate inside this listener; normal listener dispatch and native earlier hurt admission still apply. Exact244 server Living hurt posts Incoming before ordinary shield/cooldown/armor/HP, so later false/blocked/cooldown-rejected hits can still ignite. Sources with Living causing owner, including arrows and real offhand Cube while holding fiery tool, qualify. Source/amount unchanged; fire-immune negative. Fire Resistance is not fireImmune: it can prevent later ON_FIRE damage while ignition remains. Source whose own early hurt admission is rejected before Incoming cannot reach listener.

### Fiery melee

FierySword/Pick hurtEnemy first call native superclass (true) then ignite15 seconds on server !target.fireImmune. Sword false/client/fireimmune else only particles; Pick particles only client admitted branch. Exact244 Player.attack invokes itemstack.hurtEnemy only after true primary hurt and ServerLevel, resolving multipart parent Living. Subsequent native postHurtEnemy wears Sword1/Pick2 if stack still nonempty and callback true. Sweep secondary targets have hurt calls/Incoming1-second ignition but no per-secondary item hurtEnemy15-second callback. Mob.doHurtTarget uses native damage/enchantment/knockback and never invokes item hurtEnemy/postHurtEnemy: ordinary fiery-equipped Mob gets Incoming1-second route, not Player15-second branch. No item callback on blocked/false primary hurt. No direct HP, custom fire DamageType or forced extra hit from either item method.

### Native burning

Entity.igniteForSeconds floors seconds*20; Living igniteForTicks applies ceil(ticks*Attributes.BURNING_TIME), then Entity only raises existing remainingFireTicks if requested larger, never adds duration or shortens longer fire. Ordinary requested1/15 seconds =>20/300 ticks before Living burning-time multiplier. Native server Entity.baseTick, while burning and !fireImmune, every remainingFireTicks%20==0 and !inLava requests1 minecraft:on_fire, ignores hurt return, decrements fire. Direct/causing null from native onFire factory; ordinary fire tags, Fire Resistance, Protection, cooldown, absorption and extinguishing remain. No guaranteed1/15 HP totals; native fireImmune rapidly removes burning. Fiery items fireResistant property protects item stack/dropped-item against fire-type sources; it grants no wearer Fire Resistance or universal immunity.

### Fiery retaliation

EntityEvents.entityHurts is registered LivingDamageEvent.Post, not Incoming or successful-return callback. Requires nonnull causing entity and event.originalDamage>0. Counts CURRENT nonempty getArmorSlots entries whose Item instanceof FieryArmorItem; ordinary four slots n0..4. fireLevel=5*n; if fireLevel>0 and wearer.random.nextInt25<fireLevel and causingEntity !fireImmune, ignite causing entity for integer fireLevel/2 seconds: n1..4 => probability20/40/60/80%, duration2/5/7/10 seconds before burning-time multiplier. No direct-Living/melee/LOS/distance/boss/team/positive-final-HP gate; projectile owners can burn, including non-Living causing entities. Current slots are read after native armor wear, so a just-broken piece no longer counts. Exact244 Post can occur at final0 after absorption or fully blocked processing; earlier Incoming/cooldown/invulnerability veto cannot reach Post. No extra armor durability cost, custom thorns HP request or elemental source; ordinary native fire ticks follow. Yeti chilling in same callback remains protected existing work.

### Glass

Glass tier uses1/enchantability30/attack bonus36; registered Sword adds3 =>MAINHAND attack modifier39 and speed-2.4, ordinary base1 Player fully charged noncrit plain request40 before native modifiers/mitigation (not guaranteed HP). Native Sword callbacks/sweep remain. Glass hurtEnemy sends particles then own hurtAndBreak, always returns true. Server, !Player instabuild, and private hurt true: sound/equipped-break notification, shrink1, Player broken stat. private hurt returns false when INFINITE_GLASS_SWORD component nonnull. Otherwise ServerPlayer alone calls processDurabilityChange(stack,1): <=0 prevents CUSTOM shatter; positive triggers durability criterion0 and glass-break advancement. NonPlayer callback argument would skip enchantment wear processing, but ordinary Mob attacks never invoke this callback. Custom shatter does not consult ordinary UNBREAKABLE/isDamageableItem/item damage hook itself. No target hurt call or damage bonus inside callback.

### Glass two paths

Exact244 Player true primary hurt -> Glass.hurtEnemy; if custom shatter empties stack, postHurtEnemy skipped. If custom branch is suppressed and stack survives, inherited Sword.postHurtEnemy independently calls native stack.hurtAndBreak1 with normal hooks/enchantment/instabuild/isDamageable rules. Thus a durability-saving roll in first branch does not guarantee survival of second roll; INFINITE_GLASS_SWORD alone suppresses custom shatter but not inherited native wear. Actual creative lore variant from TFCreativeTabs has BOTH INFINITE_GLASS_SWORD and minecraft:unbreakable, protecting both routes; ordinary creative instabuild also avoids wear. UNBREAKABLE alone does not veto custom shatter. Sweep secondaries do not each shatter. Ordinary glass from aurora_room loot has native enchant_with_levels20; not automatically infinite. No survival recipe is asserted. These source-proven branches are preserved without repair/fix/runtime experimentation.

### Stale asm

Outer jarjar metadata binds s.tf-asm4.8.3345 archive SHA1324a81e5cf085d62385f85e4b06e6217bf977977f92c58034af315c5d975690. Its ICoreMod service names twilightforest.asm.TFCoreMod, whose getTransformers includes DamageSourcesTransformer. Transformer targets exactly DamageSources.mobAttack(LivingEntity) and playerAttack(Player), votes YES, inserts before every ARETURN: ALOAD1 then DamageSourceHooks.getCustomDamageSource(original,attacker). Hook tests attacker.getWeaponItem().getItem() instanceof CustomDamageProvider, calls provider.getDamageSource(attacker), else returns original. Full outer interface/caller scan finds CustomDamageSwordItem as sole direct implementer and STALE_BREAD as actual registered instance. This proves installed native registration/insertion intent, not a live transformed-class/runtime experiment. Other nested transformers remain pending scope.

### Stale source

STALE_BREAD is CustomDamageSwordItem(TFDamageTypes.STALE_SANDWICH,Tiers.WOOD,stack1, Sword attributes3/-2.4 with hidden tooltip), not food. Native tier uses59; Player ordinary base1 plusmodifier3 =>fully charged noncrit plain request4. Provider calls attacker.damageSources().source(type,attacker): exact native source overload gives direct=causing=attacker, no projectile owner, position or amount rewrite. Declared twilightforest:stale_sandwich message twilightforest.stale_sandwich, exhaustion0, scaling when_caused_by_living_non_player; installed TF/raw tag graph has no membership. Ordinary armor/shield, Resistance/Protection, cooldown, absorption and native difficulty rules remain, no bypass inferred. Native Player/Mob attacks, Player sweep reusing selected source and any other real factory caller acquire this source only when weapon predicate holds at factory construction. getWeaponItem normally mainhand; Player auto-spin may return captured autoSpinAttackItemStack, so not unconditionally current mainhand. Arrow/thrown/mobAttackNoAggro/explicit source factories are not targeted. Installed TF minecraft:swords membership omits Stale Bread, so no ordinary sword-tag enchantment eligibility is inferred from its Java class; native supported-item rules remain.

### Stale alternates

Protected CubeOfAnnihilation.getDamageSource calls owner.damageSources.playerAttack or mobAttack, so genuine Player Cube use from OFFHAND while main-hand Stale Bread is the current weapon supplies fixed10 native Cube request with stale_sandwich source; callback follows actual live owner/weapon at impact. No Bread melee callback/wear is invoked by Cube, no fabricated source or changed Cube behavior. Null-owner Cube thrown fallback is outside transformer. Native Mob carrying Bread uses mobAttack with own attribute+enchantment amount, not fixed4; native arrows owned by Bread holder keep arrow source. Genuine acquisition includes installed twilightforest:drying recipe bread->stale_bread filter_time6000. Native crafting/drying admission remains; no inference from food name.

### Shield

KnightmetalShieldItem extends native ShieldItem, registered durability1024. canPerformAction accepts DEFAULT_SHIELD_ACTIONS or superclass; native SHIELD_BLOCK use/72000/BLOCK semantics and facing/source/pierce/warmup/event admission, native shield disable/knockback/defense remain. Native ShieldItem constructor also registers ArmorItem dispenser-equip behavior, native OFFHAND equip with wearer/canEquip checks; this does not automatically start blocking or grant Mob shield AI. No intrinsic retaliation/spiked HP call in complete class or installed caller scan. Native Player shield wear only if shieldDamage>=3, amount1+floor(shieldDamage), native hooks/creative/enchantments; can occur on fully blocked false hurt. Repair accepts c:ingots/knightmetal OR (!minecraft:planks AND superclass repair), thus ordinary wooden planks excluded. Protected general Twilight parry can act for this shield with same config/time/projectile eligibility; no separate Knightmetal reflect mechanic or custom DamageType.

### Stats

Conventional armor uses native ArmorItem slot ADD_VALUE ARMOR plus toughness per piece; all listed materials have knockbackResistance0. Order helmet/chest/legs/boots: Naga only chest7/legs6, toughness.5 each, durability multiplier21; Ironwood2/7/5/2,tough0,mult20; Fiery4/9/7/4,tough1.5,mult25; Steeleaf3/8/6/3,tough0,mult10; Knightmetal3/8/6/3,tough1,mult20; Phantom only helmet3/chest8,tough2.5,mult30; Arctic2/7/5/2,tough2,mult10. Native slot durability factors11/16/15/13. These are attributes, not flat percentages or custom armor-penetration rules. Native Player armor wear positive damage floor(max(1,damage/4)), exact244 ArmorHurtEvent and ArmorItem/canBeHurtBy check; source bypass tags and item fire resistance remain. Armor constructors register real dispenser-equip route with native wearer/slot/permission checks. Yeti stats/proc already protected; Travellers modifier behavior and Phantom kept-on-death callback are separate pending sections, not invented armor-body overrides.

### Tool stats

Ironwood native Sword/Shovel/Pick/Axe/Hoe with tier uses512,bonus2,enchant25; MAINHAND attack modifiers5/3.5/3/8/0, attack-speed modifiers-2.4/-3/-2.8/-3.1/-1. Steeleaf tier uses131,bonus3,enchant9; modifiers6/4.5/4/9/0, speeds-2.4/-3/-2.8/-3/-.5. Fiery tier uses1024,bonus4,enchant10; Sword modifier7/-2.4, Pick5/-2.8. Glass39/-2.4 uses1; Stale3/-2.4 uses59. Add recipient-independent base attributes and native Player charge/crit/enchant/sweep or Mob attack pipeline; never treat attribute as final HP. Tool attacks use real native source, armor/Resistance/cooldown, and Player Sword1/Digger2 post-hit wear; native Mob attacks do not consume those item callbacks. Protected Knightmetal/Minotaur/giant/Ice mechanics are not duplicated.

### Recipe components

Actual native recipe output components differ from plain creative/default item stacks. Ironwood craft: Sword KnockbackI, Axe FortuneI, Pick/Hoe EfficiencyI, Shovel UnbreakingI, helmet AquaAffinityI, chest/legs ProtectionI, boots FeatherFallingI. Steeleaf craft: Sword LootingII, Axe/Shovel EfficiencyII, Pick/Hoe FortuneII, helmet ProjectileProtectionII, chest BlastProtectionII, legs FireProtectionII, boots FeatherFallingII. Naga craft chest FireProtectionIII/legs ProtectionIII. Pinned installed recipes preserve these exact native enchantments; default item registration does not grant them globally. Other captured recipes/loot may supply ordinary native enchantments; no custom statuses inferred. Full ingredient/output paths remain in native data witnesses. Native enchantment compatibility, merging and grindstone rules remain.

### Arctic

ArcticArmorItem.canWalkOnPowderedSnow returns stack exactly ARCTIC_BOOTS. Exact244 PowderSnowBlock tests Living FEET stack hook (or walkable entity tag), surface collision additionally requires above/not descending, with native falling-body/fall-distance branches. No blanket phasing/water walk/no-fall property. Armor dye renderer is visual. Separately installed minecraft:freeze_immune_wearables includes each Fiery/Arctic piece: native Living.canFreeze returns false if any armor slot HEAD/CHEST/LEGS/FEET/BODY is tagged, preventing native freeze accumulation/DOT path; not a veto on arbitrary DamageSource FREEZE or existing Frosted effect. Existing Yeti and Travellers vest/boots entries in that same tag are recorded as shared data, their prior/pending mechanics remain distinct.

### Crown

MysticCrownItem extends Item implements Equipable HEAD, native swapWithEquipmentSlot use; registration stack1 with HEAD ARMOR+2 using minecraft:armor.head ADD_VALUE, no max-damage/durability, no toughness. Native equip/curse/slot predicates remain. It is not ArmorItem and is not ordinary damageable armor; exact244 ArmorHurt hook defaults non-ArmorItem wear0. No fire/knockback/status immunity. Protected Lich scepter helpers test actual crown and apply their separately reviewed bonuses; no duplicate new scepter payload here. Native armor material body attributes are not used for crown.

## Packages

| Mechanic | Primary classification |
|---|---|
| Fiery tools incoming and Player melee ignition | VANILLA_DIRECT |
| Fiery armor probabilistic native ignition retaliation | VANILLA_LIKE_EXTENDED |
| Glass Sword native attack and two break paths | CUSTOM_RESOURCE |
| Stale Bread native factory source replacement | CUSTOM_DAMAGE |
| Knightmetal native shield and repair | VANILLA_DIRECT |
| Conventional Twilight tool and armor attributes | VANILLA_DIRECT |
| Arctic snow collision and Fiery/Arctic freeze eligibility | VANILLA_DIRECT |
| Mystic Crown native HEAD armor | VANILLA_DIRECT |

## Custom source callers

| Type | Amount | Source identity |
|---|---|---|
| twilightforest:stale_sandwich | Native Player/Mob chosen attack amount; plain fully charged noncrit unmodified Player4. Actual Cube factory alternate10. Transformer does not set amount. | Both attacker passed to source factory; Cube uses Living owner as both, not Cube projectile. |

## Scope and exclusions

- Complete listed item/material/hook bodies plus real event/registration and native inherited paths reviewed; no new runtime test.
- Phantom base armor is included, while death-retention producer closes with Charms/Keeping next; Travellers modifier system is pending.
- Stale source transformer is bound to actual nested archive and service. Other ASM transforms are not marked complete.
- Existing Frosted/Yeti/Knightmetal bonus/Minotaur/giant/scepter/parry packages reused without redoing their accepted semantics.
- All other hazards/custom sources and full-mod compatibility/source attribution remain pending. Twilight PARTIAL, zero promoted;30/40 types reviewed,10 unfinished, REVIEW_REQUIRED0.

## Future native controls

- Fiery Player/Mob/sweep/projectile Incoming timing and native burn mitigation.
- Fiery armor real Post/zero-HP/owner/current-slot retaliation.
- Glass true-primary callback, independent wear, actual infinite variant and native Mob/sweep contrasts.
- Stale native Player/Mob and Cube factory routes with direct/cause/type/tag/amount controls.
- Native Knightmetal block/repair/shared parry; conventional crafted/default stats, powder/freeze eligibility and crown equip.

[Semantic packages and paths](semantic-sections/twilightforest-equipment.json), [integrity](twilightforest-equipment-integrity.json), [full validation](r2f8m-equipment-validation.json).

Exact next task: Continue Task C with Charms of Life/Keeping, Phantom retention and Keepsake Casket death/respawn paths; then Travellers gear/components and remaining utility/food, passive entities/hazards10 unfinished custom types, nested ASM and whole-mod compatibility/source closure. Protect each subsection toward R2f8 and final dedup/promotion. IceAndFire only after COMPLETE Twilight pushed/live verified. No runtime boss/L2/Stage/production/fixes/Phase6/7.
