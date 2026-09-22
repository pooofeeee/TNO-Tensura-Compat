# r2f8r - TWILIGHT_FOOD_FLASKS_SEMANTIC_REVIEW_COMPLETE

Installed Twilight4.8.3345 and raw Minecraft1.21.1/exact NeoForge21.1.244 authority, with incremental bytecode/resource witnesses. Static research only, runtime0. Prior protected gear/boss/source work preserved. This closes food/flask/Essence Berry consumption and Experiment115 block resource; utility/map/passive/hazard and remaining ASM/source closure still unfinished. FAILED_CHALLENGE is USED;31/40 profiles now reviewed,9 unfinished. No Stage/L2/production/Phase6/7 changes.

Adds 12 reviewed packages / 33 delivery cases. Twilight remains PARTIAL at 202/646 drafts, zero promoted. REVIEW_REQUIRED 0.

## Native contracts

### Authority

Installed Twilight4.8.3345 and raw Minecraft1.21.1/exact NeoForge21.1.244 authority, with incremental bytecode/resource witnesses. Static research only, runtime0. Prior protected gear/boss/source work preserved. This closes food/flask/Essence Berry consumption and Experiment115 block resource; utility/map/passive/hazard and remaining ASM/source closure still unfinished. FAILED_CHALLENGE is USED;31/40 profiles now reviewed,9 unfinished. No Stage/L2/production/Phase6/7 changes.

### Food admission

Native Item.use reads actual stack food properties and Player.canEat(canAlwaysEat); native canEat is abilities.invulnerable OR canAlwaysEat OR foodData.needsFood. Use duration normally32ticks, StackableEffectItem fast16ticks. Native use completion and loader item-use events remain; no instant consumption fabricated. Item.finishUsingItem delegates LivingEntity.eat when food exists. Player.eat adds FoodData and stats/criterion before superclass effects/stack consumption. Native FoodData adds nutrition clamped0..20, saturation gain nutrition*modifier*2 clamped0..newfood. Ordinary possible effects apply server-side when randomFloat<probability; vanilla addEffect admission/merge applies. Native consume preserves stack for infinite-material Player. usingConvertsTo gives bowl copy when consumed stack empty or server inventory/drop otherwise, only without infinite materials. Registration fireResistant protects item entity/stack, not consumer.

### Food values

All nutrition/saturation-modifier parameter sets: raw_venison2/.3; cooked_venison6/.6; hydra_chop18/2; raw_meef2/.2; cooked_meef7/.6; meef_stroganoff14/1.2; maze_wafer4/.6; experiment_1154/.3; berry_medley and moss_soup5/.6; shika_senbei4/1; monster_jerky4/.275; beef/pork/venison/meef_jerky6/1.18; chicken_jerky4/1.075; mutton/salmon_jerky4/1.35; rabbit_jerky4/.925; cod_jerky4/.875; tropical_fish/fugu_jerky2/.6; gelatinous_slime_drop1/.2; gelatinous_maze_slime_drop2/.3. Stackable berries1/.4. Torchberries leave Builder defaults nutrition0/modifier0. Only Torchberries and Meef Stroganoff explicitly alwaysEdible here. Medley, soup and Stroganoff stack1 and return BOWL. No raw-meat, monster-jerky or fugu-jerky poison inferred from name: registration has none.

### Hunger health

Food addition is a nutrition/saturation resource, not immediate HP healing. Native FoodData.tick naturalRegeneration gamerule: food>=20, saturation>0 and Player.isHurt ->each10ticks heal min(saturation,6)/6 and add that numerator as exhaustion; otherwise food>=18 and hurt ->each80ticks heal1/exhaustion6. Actual native heal hook, HP eligibility and subsequent food exhaustion remain. Hunger/starvation is inherited native behavior, not a new Twilight damage source. Food data persists through native Player save/death rules; no Twilight custom food attachment.

### Torchberries

Actual food effect GLOWING duration100ticks amplifier0 probability.75. Always edible with0nutrition/0saturation; native outline effect on eater, not emitted light, target damage or custom detection immunity. Ordinary effect eligibility, duration merge, expiry and native rendering remain.

### Hydra chop

Food applies native REGENERATION100ticks amplifier0 probability1. HydraChopItem separately triggers CONSUME_HYDRA_CHOP criterion before parent consumption only ServerPlayer and foodLevel<=0; this is advancement admission, not a second heal or stronger regeneration. Native Regeneration requests heal1 on remaining-duration multiples of50>>amplifier while HP<max, through native heal hook. Full-food ordinary non-invulnerable player cannot begin this non-alwaysEdible food use. Item fire resistance is not consumer immunity.

### Stroganoff

Native food applies FIRE_RESISTANCE3600ticks/amp0 and DAMAGE_BOOST(Strength)2400ticks/amp0 independently with probability1 each. AlwaysEdible14nutrition/1.2modifier, bowl remainder. Strength is native attack-damage ADD_VALUE+3 per level, not direct HP. Fire Resistance native hurt gate checks source IS_FIRE; it is not Entity.fireImmune nor protection from arbitrary untagged source. Native effect eligibility/merge and attribute cleanup remain.

### Slime food

Gelatinous Slime Drop applies MOVEMENT_SPEED600ticks/amp0 probability1; Maze variant applies DAMAGE_RESISTANCE600ticks/amp0 probability1. Speed native movement attribute +.2 ADD_MULTIPLIED_TOTAL per level. Resistance native damage reduction is20% per level where native source bypass predicates permit, not absolute immunity. These are food effects on consumer; protected Slime/Maze Slime contact attacks remain separate.

### Berry stack

StackableEffectItem.finishUsingItem server applies each configured custom roll BEFORE super food consumption. Each independent test chance>=random.nextFloat; accepted effect requests MobEffectInstance(effect,currentDurationOr0+extraTicks,configuredAmplifier). All installed berry configured amplifiers0; this extends requested duration, never increments amplifier. Native addEffect return ignored; eligibility, stronger/hidden/infinite effect merge still determine actual result. For active infinite duration=-1 the finite request becomes extraTicks-1; no automatic infinite extension/replacement claim. No cap in TF helper; Java int addition and native instance validation/merge remain. Noarg constructor decompiler appears recursive, but pinned bytecode constructs zero-length StackableEffectInstance array then invokes varargs constructor. Raspberry/Blueberry/Blackberry/Maloberry therefore have no custom status payload.

### Berry payloads

Blightberry independent REGENERATION+160ticks p1, POISON+100ticks p.75, WITHER+100ticks p.15. Duskberry NIGHT_VISION+300ticks p1, BLINDNESS+60ticks p.75. Skyberry JUMP+160ticks p1, MOVEMENT_SLOWDOWN+60ticks p.75. Stingberry DAMAGE_BOOST+200ticks p1, DIG_SLOWDOWN+200ticks p.75. Every payload amp0. Negative rolls do not veto other effects or nutrition. Native levelI Jump adds.1 jump power and+1 safe-fall distance, Slowness movement-.15 total, Strength attack+3, MiningFatigue attackSpeed-.1 total and ordinary Player mining multiplier.3 at amp0. NightVision/Blindness affect native visibility/control rather than HP. Protected native status implementations reused; no TF custom effect registered by these items.

### Berry damage

Native Poison tick requires HP>1, requests1 every25>>amp on duration modulo; exact244 uses holder neoforge:poison, fallback minecraft:magic if holder absent, new ownerless DamageSource. Raw vanilla comparison uses magic. Native Wither requests1 every40>>amp via ownerless minecraft:wither, no HP>1 floor. Tick method returns true independently of hurt success. Regeneration native heal1 every50>>amp only belowmax. These indirect later native status HP requests remain separate from food consumption/roll success; armor/source tags, Resistance/Protection/invulnerability/absorption/loader hooks remain native. No guaranteed final HP amount, no SHP write or new TF DamageType.

### Flask fill

Brittle default POTION_FLASK_CONTENTS EMPTY=(PotionContents.EMPTY,0doses,0breakage,true); Greater default EMPTY_UNBREAKABLE same but false, stack1/fireResistant. Brittle stack-aware max is1 only when inner potion base Holder is present, otherwise native default max64. Both secondary-click override directions require donor POTION_CONTENTS nonnull, existing baseholder empty OR full PotionContents.equals(donor), and doses<3-breakage. No PotionItem class/regular-drinkable-only gate: genuine splash/lingering potions and tipped arrows with actual component also qualify. No additional slot.allowModification/mayPickup check in TF handlers; real menu dispatch posts CommonHooks.onItemStackedOn first, then feature-enabled item handlers before ordinary fallback slot pickup/insert checks. Other native menu/player/event admission remains. Not permission to bypass it.

### Flask resource

If !instabuild filling shrinks donor1 and gives glass bottle via inventory.add or drop. changeAndConsumeFlask splits one flask when stackcount>1, mutates copy, inventory-add/drop; otherwise mutate original. tryAddDose replaces contents with supplied PotionContents and adds1dose, retaining breakage/breakable. Capacity lives in UI caller, not record. An existing custom-only payload without baseholder can therefore be replaced by next donor and does not trigger maxstack1; no ordinary producer of arbitrary custom data is invented. Drink use requires inner PotionContents identity !=static EMPTY and doses>0, starts native32tick DRINK; finish itself does not recheck positive doses. Non-instabuild completion removeDose subtracts1, clears contents if newdose<1, increments breakage only if breakable. Breakable breaks/shrinks1 at breakage>=3, otherwise cracks; Greater unbreakable retains breakage0 and refills max3, no break/crack. Hurt/addEffect return never gates these costs. Creative processes effects but no donor/dose cost; survival and creative actual eligibility still native.

### Flask native payload

finish requires nonempty-by-identity potion and LivingEntity instanceof Player; server iterates actual getAllEffects, base potion effects then custom list. First tests custom FAILED_CHALLENGE predicate below; otherwise instant MobEffect invokes applyInstantenousEffect(player,player,player,amplifier,1), noninstant calls player.addEffect(copy). For normal noninverted eater, HARMamp0 requests native indirectMagic direct=causing=self amount6; Healingamp0/1 native heals4/8. Inverted heal/harm reverses those native branches, subject to earlier custom branch. Ordinary native PotionItem passes same instant arguments but has no TF custom branch. PotionContents defines payload, so same filling path carries actual installed modded potion effects without assuming all recipient eligibility. Parent here is Item, not PotionItem: default flask has no FOOD; no second potion application, native PotionItem bottle replacement or its DRINK gameevent from this parent call. Native item-use framework hooks still apply.

### Failed challenge

Exact predicate: (effect.is(HARM) != entity.isInvertedHealAndHarm()) && amplifier>0, evaluated BEFORE effect.isInstantenous. Ordinary noninverted Player: amplified HARM only ->hurt(damageSources.source(TFDamageTypes.FAILED_CHALLENGE),(float)(6<<amp)); native Strong Harming amp1 requests12. Inverted Player: EVERY non-HARM amplified effect meets predicate, including noninstant strong Speed/Poison; HARM falls through normal inverted-healing branch. Code does not restrict that side to HEAL/instantaneous. A legitimate inverted Player producer is not proven by this TF method; future inverted fixture must obtain real native eligibility, never manufacture it. Java shift/int overflow semantics retained for nonordinary amplifiers. No direct setHealth/SHP operation.

### Failed source

One-argument native DamageSources.source(key) ->DamageSource(holder) has direct=null, causing=null and explicit sourcePosition=null. FAILED_CHALLENGE declaration exhaustion0, message twilightforest.failedChallenge, scaling when_caused_by_living_non_player. Installed TF+raw native tag closure has no membership: no armor/effect/Resistance/Enchantment/invulnerability/cooldown bypass, no IS_FIRE/IS_PROJECTILE/IS_EXPLOSION or magic/physical/environment tag identity. Potion origin is delivery context only. Ordinary native armor/toughness, Protection, Resistance, absorption, player invulnerability and cooldown remain. Null causing entity does not satisfy living-non-player difficulty scaling. Despite no BYPASSES_SHIELD tag, native directional shield cannot block this null-position source (getSourcePosition null); generic loader block hooks remain conditional. hurt return ignored: following effects/tracking/stat/dose/breakage continue even if request rejected/mitigated. Only advancement trigger below checks player alive, not effect loop/resource code.

### Flask tracking

Server noncreative nonspectator Player with basepotion Holder records FLASK_DOSES attachment after effects. Same Holder increments doses; different resets count1 and start gameTime, then stores Holder. Alive player triggers DrinkFromFlask with floor(float(gameTime-start)/20) seconds and exact native dose/time/HolderMatcher criterion. EntityEvents resetFlaskLogic on an earned advancement containing DrinkFromFlask trigger resets count0/Holdernull, retaining time field. Attachment defaults null/0/0 and serializes those values, no copyOnDeath; no combat buff or separate HP. TFAdvancementGenerator.flaskWithHarming creates a four-dose unbreakable Brittle icon; this data-generation display is not a survival capacity/default recipe. Persistent/network PotionFlaskComponent codec stores potion/doses/breakage/breakable without independent numeric bounds.

### Experiment item

Experiment115Item food4/.3 and ordinary food completion, plus ServerPlayer slice statistic. useOn same Experiment115 block returnsPASS to its block handler; on another block with Player&&!secondary tries native placement, falling back to native food use when placement did not consume action and FOOD exists. Secondary use returnsPASS. Genuine default placed block has BITES_TAKEN7 (one portion), REGENERATEfalse. Component EXPERIMENT_115_VARIANTS selects presentation/advancement icons, no combat effect producer in caller scan.

### Experiment block

Block native no-item use requires Player.canEat(false), immediately adds FoodData4/.3 without item-use32tick delay, awards stats/criterion and increases bites by1 or removes block when oldbites7. This is food resource, not direct heal. Nonsecondary item use with Experiment115 requires bites>0, decreasesbites1 and consumes item1; full0 returnsFAIL. Redstone on full0 nonregenerating block consumes1 and sets REGENERATEtrue. Secondary item use only on nonregenerating block removes one portion and gives native item unlesscreative; last portion removesblock. Native ItemStack.consume respects infinite materials; eating block still removesportion for invulnerable Player. Server randomTick if regenerate&&bites!=0 decreasesbites1, no additional TF chance gate; no ticks after removed. Thus eating finalportion destroys even regenerating block, not inexhaustible instant healing. Belowblock must isSolid; loss of lower support makes AIR; noLootTable and native randomTicks registered. Comparator=8-bites+(regen?7:0), redstone=regen?15-2*bites:0, no direct damage/effect pulse.

### Essence

EssenceBerryItem is not FOOD. Either-hand use consumes1 via native consume, server creates actual ExperienceOrb atplayer(x,y+1,z) value6+random.nextInt14=6..19, addFreshEntity; returns sidedSuccess. Infinite-material stack preserved; orb still created by actual use. No direct grantExperiencePoints/heal or personal ownership restriction. Native orb motion/merging/pickup/despawn/ordinary entity admission remain. Exact244 orb playerTouch ServerPlayer with takeXpDelay0 posts cancelable PickupXp; if allowed setsdelay2, then repairPlayerItems before positive residual XP. Native random eligible damaged REPAIR_WITH_XP item and actual getXpRepairRatio/enchantment durability conversion determine repair, recursive leftover accounting; not a fixed TF repair/heal. Another player can pick up actual orb. Oreberry bush harvest/hazard reviewed later, not inferred closed by item consumption.

### Compatibility

Native TF source paths use actual inventory/menu/food/effect/XP hooks and no Curios-specific consumer. Generic conditional loader hooks for item stacking/use, effect applicability/merge, heal/damage/block and XP pickup/repair are present. Direct external source-specific compatibility NONE_PROVEN in reviewed food/flask implementation; this is scoped static attribution, not pack-wide compatibility certification. Existing accepted source/effect hooks remain untouched. All fixtures listed are future genuine native deliveries; no runtime test, source injection, direct HP/SHP write or fixes performed.

## Packages

| Mechanic | Primary classification |
|---|---|
| Twilight native food nutrition and saturation | VANILLA_DIRECT |
| Torchberry native Glowing | VANILLA_DIRECT |
| Hydra Chop native Regeneration | VANILLA_DIRECT |
| Meef Stroganoff native Fire Resistance and Strength | VANILLA_COMPOSITE |
| Gelatinous Slime Drop native Speed | VANILLA_DIRECT |
| Gelatinous Maze Slime Drop native Resistance | VANILLA_DIRECT |
| Twilight probabilistic berry duration extension | VANILLA_LIKE_EXTENDED |
| Brittle/Greater flask dose and breakage resource | CUSTOM_RESOURCE |
| Flask native potion effect delivery | VANILLA_COMPOSITE |
| Flask failed-challenge ownerless damage | CUSTOM_DAMAGE |
| Experiment115 portion storage and regeneration | CUSTOM_RESOURCE |
| Essence Berry native experience orb | VANILLA_DIRECT |

## Custom source callers

| Type | Amount | Source identity |
|---|---|---|
| twilightforest:failed_challenge | (float)(6 << amplifier), ordinary Strong Harming amp1 requests12; never asserted final HP. | Both null, explicit sourcePosition null: native one-argument source(key). No owner/projectile. |

## Scope and exclusions

- All food/flask/Experiment115/Essence Berry item contracts listed are reviewed, including actual native superclass/effect/damage/XP comparisons. Full registration food parameter sets pinned; recipes/loot witnesses retain source acquisition.
- No invented food poisoning from names; ore berries iron/gold/copper are plain material items. Stale Bread is protected custom sword source, not food.
- Brittle four-dose advancement icon and custom-only/inverted predicate boundaries are not invented survival fixture producers. Native data/menu/eligibility retained.
- Tooltip/model/variant/criterion outputs do not add combat payloads; bush hazards/harvest and other utility/passive/ASM closure remain later scope.
- No runtime boss/L2/Stage/production tests or changes. Twilight remains PARTIAL with31/40 custom source profiles;9 ordinary unfinished sources are not REVIEW_REQUIRED.

## Future native controls

- All native food nutrition/saturation/full-food/remainder controls and actual native regeneration/effects.
- Genuine four special berries, independent rolls, existing status merge and true native later damage/heal sources.
- Both real flask click directions, component donors, split/overflow, doses/breakage/creative and save/load.
- Native HarmingI/II and Healing flask positive controls with exact direct/cause/source tags, shield null-position, rejected hurt and separate resource costs.
- Actual Experiment115 placement/food/block portion/refill/redstone/randomtick/support lifecycle.
- Genuine Essence Berry orb creation and ordinary pickup/XP repair, no direct XP/HP simulation.

[Semantic packages and paths](semantic-sections/twilightforest-food-flasks.json), [integrity](twilightforest-food-flasks-integrity.json), [full validation](r2f8r-food-flasks-validation.json).

Exact next task: Review remaining utility/map items (Pocket Watch, transformation and terrain tools, native map/landmark ASM), then passive entities, environmental hazards and nine unfinished custom DamageTypes. Close remaining installed ASM/compatibility/source exclusions, protect R2f8 and promote full Twilight COMPLETE before IceAndFire. No runtime/L2/Stage/production/Phase6/7.
