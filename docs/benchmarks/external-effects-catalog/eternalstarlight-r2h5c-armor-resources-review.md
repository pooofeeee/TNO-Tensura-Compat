# R2h5c — Eternal Starlight armor and resources

Remaining armor, material Post effects, accessory attribute routing, native healing/air resources and consumable cleanse.

Static subsection complete. Runtime fixtures remain unexecuted; no Stage or production implementation.

## Material post

Neo LivingDamageEvent.Post routes to ES onPostLivingHurt with native source and event new damage. Material branches have no amount>0 test. ANY ThermalSpringstoneArmorItem among four worn slots plus source.directEntity Living adds200 fire ticks to that direct attacker; tagged Thermal Springstone current weapon on direct Living adds200 to victim. No explicit fireImmune test in these writes; later native burning admission is separate. ANY GlaciteArmorItem similarly adds80 frozen ticks capped300 to direct Living attacker WITHOUT canFreeze; tagged Glacite weapon adds80 capped300 to victim WITH canFreeze. Pieces are OR membership, not four stacked retaliation calls. Non-Living direct projectile with Living causing owner does not meet these material branches. No additional HP source or direct health subtraction. Leave counters native and scale only existing later native fire/freeze hurt once.

## Material status

Direct-Living current weapon #MALARITE_WEAPONS requests native Poison60 amp0; #PUNGENCY_FRUIT_WEAPONS requests Poison80 amp1 and Nausea120 amp0, each independent of effect acceptance. Native addEffect eligibility/event rejection remains; no new custom poison DamageType. Tagged spear HELD melee can reach these Post branches; thrown material spear instead uses its reviewed projectile post-hit branch, so do not count both on a non-Living direct spear source. Native Starfire and Petal Scythe Post branches already accepted; no duplicate semantic research/package here.

## Deepsilver

Every worn TickableArmor item receives tick callback; Deepsilver verifies all four armor-slot stacks are DeepsilverArmorItem and attempts removeEffect for currently present entries in #deepsilver_armor_can_remove. Installed tag: Poison, Wither, Nausea, Hunger, Slowness, Infested, Blindness. This is repeated removal, not canBeAffected immunity, and no arbitrary negative-effect cleanse; custom ES/Tensura/L2 effects are not in this installed tag. Four-piece dispatch can attempt four removals in a tick if prior native removal was vetoed. Native removeEffect event and downstream effect callbacks remain. Deepsilver also adds attack speed .05 and movement .01 per matching slot, standard native attributes. No Stage value on removal or attributes.

## Armor attributes

Thermal Springstone adds ES FIRE_RESISTANCE .24 per slot; attribute clamped0..1, four ordinary pieces .96 before other modifiers. Its IS_FIRE Incoming multiplier already reviewed; burning effects do not automatically mean source IS_FIRE. AirSac adds WATER_MOVEMENT_EFFICIENCY .9 per slot, preserving native attribute limits. Alchemist adds THROWN_POTION_DISTANCE .25 and ETHER_RESISTANCE .3 per piece; Ether resistance semantics already reviewed. ProjectileMixin scales native getMovementToShoot result by living-owner potion-distance attribute (default1,range0..1024) ONLY for ThrownPotion; ownerless dispenser unaffected. This changes splash/lingering delivery trajectory, not damage or effect potency. Standard armor/toughness/knockback and ordinary Starlit Diamond armor retain native processing; Neo subclass is texture-only. None receives a separate Stage multiplier.

## Unrealium attributes

Unrealium extra component declares MOVEMENT_SPEED +.05 ADD_VALUE then +.1 ADD_MULTIPLIED_TOTAL using SAME minecraft:armor.<slot> ID and attribute. Raw ItemAttributeModifiers.Builder appends both entries; exact loader IItemStackExtension passes defaults through ItemAttributeModifierEvent; without an external rewrite, native collectEquipmentChanges iterates order and removes the ID before each addTransientModifier. Thus later +.1 total replaces earlier +.05 flat on equipped attribute instance; do not claim their sum. Each piece also contributes KNOCKBACK_RESISTANCE -.05 total, ENEMY_FOLLOW_RANGE_MULTIPLIER -.15 additive. Helmet fogvision50 excluded as rendering; chest EXPLOSION_KNOCKBACK_RESISTANCE+1, leggings GRAVITY-.02, boots MOVEMENT_EFFICIENCY+1 and STEP_HEIGHT+.5. Native clamps, same-ID replacement and external modifier-event rewrites remain runtime fixture concerns. No Stage quantity.

## Unrealium admission

Native IN_WALL helmet and CRAMMING chest source veto already accepted in R2h2a. Additional server VanillaGameEvent cancellation checks source Living wearing exact piece: helmet EAT/ITEM_INTERACT_START/FINISH; chest ENTITY_DAMAGE; legs HIT_GROUND/SPLASH; boots STEP/HIT_GROUND. Cancelling propagation can suppress vibration-driven detection; this is distinct from cosmetic sound suppression and does not make entity untargetable. ES visibility attribute multiplies native LivingVisibilityEvent modifier; default1, range0..1024, four-.15=0.4 before other modifiers, not absolute target immunity. Preserve binary events/visibility; no Stage value.

## Amaramber

ES entity tick requires exact Amaramber Mask and Chestplate plus EMPTY legs and feet, then ensures permanent ARMOR+7 with fixed amaramber_bonus ID; otherwise removes that ID. This is native armor mitigation, not direct damage cancellation or max-HP change. No Stage scaling of armor; preserve source bypass_armor and later native defensive processing. Natural Amaramber inventory durability mending is short excluded maintenance.

## Accessory delivery

Actual ES accessory component on equipment is delivered by ItemStackMixin RETURN in BOTH forEachModifier overloads (slot and slotGroup). It iterates stored accessory stacks, reads ACCESSORY attributeModifiers and invokes only matching slot entries; does not multiply by accessory stack count. Native apply slots/IDs govern stacking. Normal combination UI checks target tag, available slot count and no duplicate item; direct runtime data may differ and must not be presumed valid. Active armor accessory queries use a SET across worn slots for proc membership; numeric attribute entries still follow native per-slot rules. Equipment passive armor, weapon-held and direct-source proc routes are distinct future fixtures.

## Accessory attributes

Six native Accessory builders: Battleaxe Pendant and Warhammer Pendant each +.15 total attack speed MAINHAND; Butterfly Wings Amulet +.5 Ether resistance CHEST; Fungus Amulet +.5 HEAL_MULTIPLIER CHEST; Pearl Necklace +3 OXYGEN_BONUS and +4 total submerged-mining-speed CHEST (mining excluded); Crescent Pendant +.15 total attack damage CHEST. Preserve these modifiers and apply Stage once at final native HP/heal path, not another multiplier on attributes. Existing Warhammer movement proc, Butterfly armor erosion and Crescent incoming cap are reused, not duplicated. Battleaxe stripping/durability and Crescent periodic repair are excluded maintenance/utility.

## Heal fungus

All living entities receive HEAL_MULTIPLIER default1 range0..1024; ES LivingHealEvent handler returns current amount*attribute, then native heal accepts positive result on alive target and clamps via native health setter. Fungus chest accessory gives ordinary factor1.5 before other modifiers, not a separate healing event, HP transfer or immunity bypass. Parent native heal is the only future Stage point if that parent heal is in scope; never scale both modifier and resulting heal. Fungus also changes absent food properties for tagged #c:mushrooms while any active worn Fungus Amulet: Item.use/getUseDuration/finishUsingItem obtain food nutrition6/saturationModifier1.2. Existing food properties take precedence. Native food admission/consumption/replenishment remains; no instant custom heal.

## Air resources

AirSac Mask hook only when Neo LivingBreatheEvent cannot breathe and consumeAirAmount>0. If swimming, random half returns-1 -> reduce consumption by1 floored0; otherwise horizontal stored MOVEMENT length<.01 returns+1 -> setCanBreathe(true), refill1. Other case no change. Movement uses reviewed accumulator and can remain stale without new move callback; no permanent universal water immunity. Pearl Necklace gives native oxygen bonus and Player tick outside WATER eyes refills max air immediately. Native drowning admission/source remain; air counts, cadence and oxygen modifier are not Stage quantities. Abyss depth/attack air loss is separately reserved for hazards.

## Food cleanse

LivingEntityMixin eat HEAD: exact Lunaris Cactus Gel iterates active effects and removes each effect whose isBeneficial is false (includes neutral as well as harmful), with normal removeEffect return/veto and cleanup; exact Pungency Stew removes Hunger. No fabricated milk event, damage or HP write. Gel can attempt removal of custom Numbness and leave its already-reviewed deferred release behavior; removal is not debt deletion. This is materially distinct from Deepsilver tag-only repeated cleanse and should be runtime-tested against Tensura/L2 effect removal listeners.

## Food effects

ESFoods native consumable effect definitions preserve duration/amplifier/chance and native canBeAffected: Cactus Fruit Glowing600 and Poison200 each.8; Abyssal Fruit Glowing600 .3 and WaterBreathing400 .15; Velvetumoss WaterBreathing400 .2; Pungency Fruit/Stew and Silver Pungency Nausea120 .8; Shadow Snail Meat Nausea600 .3; Doomeden Carrion Hunger600 .8 and Rotten Ham Hunger600 .3. All amp0. Existing Bouldershroom Sticky2400 .8, Forgotten Millet Oblivion300 certain and Silver Pungency Numbness1200 certain reuse reviewed status packages. Food effects do not call HP directly; ordinary nutrition/recipes and containers are brief exclusions. Any later native Poison/DOT/healing follows its single existing final native scaling point, never duration/chance amplification.

## Scope

Remaining armor/resources section is static only. No runtime claims, L2 pass, direct SHP/HP mutation or Stage/production implementation. No classification-only research. Generic attributes and resources are retained natively; combat quantities are identified at already-existing final HP/heal processing. Rendering, tooltip, crafting, textures, repair, food-only nutrition and mining are excluded without separate archaeology.

## TNO integration decisions

- **Thermal material fire counters**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional multiplier; Preserve native control/resource/attribute values; any underlying HP/DOT/heal request has only its parent final native scaling point.
- **Glacite material frozen counters**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional multiplier; Preserve native control/resource/attribute values; any underlying HP/DOT/heal request has only its parent final native scaling point.
- **Malarite/Pungency held-weapon Poison and Nausea**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional multiplier; Preserve native control/resource/attribute values; any underlying HP/DOT/heal request has only its parent final native scaling point.
- **Deepsilver full-set tagged cleanse**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional multiplier; Preserve native control/resource/attribute values; any underlying HP/DOT/heal request has only its parent final native scaling point.
- **Native armor combat attribute modifiers**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional multiplier; Preserve native control/resource/attribute values; any underlying HP/DOT/heal request has only its parent final native scaling point.
- **Alchemist living-owner potion trajectory**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional multiplier; Preserve native control/resource/attribute values; any underlying HP/DOT/heal request has only its parent final native scaling point.
- **Unrealium movement/knockback/gravity attributes**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional multiplier; Preserve native control/resource/attribute values; any underlying HP/DOT/heal request has only its parent final native scaling point.
- **Unrealium native vibration suppression and visibility**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional multiplier; Preserve native control/resource/attribute values; any underlying HP/DOT/heal request has only its parent final native scaling point.
- **Amaramber exposed lower slots armor bonus**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional multiplier; Preserve native control/resource/attribute values; any underlying HP/DOT/heal request has only its parent final native scaling point.
- **Native ES accessory slot modifiers**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional multiplier; Preserve native control/resource/attribute values; any underlying HP/DOT/heal request has only its parent final native scaling point.
- **ES native healing multiplier and Fungus food admission**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional multiplier; Preserve native control/resource/attribute values; any underlying HP/DOT/heal request has only its parent final native scaling point.
- **AirSac Mask and Pearl air resource**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional multiplier; Preserve native control/resource/attribute values; any underlying HP/DOT/heal request has only its parent final native scaling point.
- **Gel nonbeneficial and Stew Hunger cleanse**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional multiplier; Preserve native control/resource/attribute values; any underlying HP/DOT/heal request has only its parent final native scaling point.
- **Native combat-significant consumable effects**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional multiplier; Preserve native control/resource/attribute values; any underlying HP/DOT/heal request has only its parent final native scaling point.

[Machine-readable packages, delivery paths and future fixtures](eternalstarlight-r2h5c-armor-resources.json). Exact archive/method witnesses and targeted semantic assertions are reproducible. No whole-mod completion claim.

Exact next task: R2h6: spells/crests and mana resource delivery, then remaining non-boss creatures/hazards and whole ES caller closure/promotion/full validation. Bosses Rise follows automatically while usage remains healthy. Do not repeat prior reviewed families.
