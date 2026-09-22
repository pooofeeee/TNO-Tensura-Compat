# r2f8i - TWILIGHT_SUMMON_RESOURCES_SEMANTIC_REVIEW_COMPLETE

Installed TF4.8.3345, raw Minecraft1.21.1 and exact NeoForge21.1.244. Real owned-mob use/AI, native EXPIRED self-hurt and native crafting/enchantment callbacks only. Request, final HP, motion, effect lifetime and item charges are separate. No runtime/L2/Stage/production change. Other scepter unique payloads remain protected or explicitly pending.

Adds 9 reviewed packages / 28 delivery cases. Twilight remains PARTIAL at 125/374 drafts, zero promoted. REVIEW_REQUIRED 0.

## Native contracts

### Authority

Installed TF4.8.3345, raw Minecraft1.21.1 and exact NeoForge21.1.244. Real owned-mob use/AI, native EXPIRED self-hurt and native crafting/enchantment callbacks only. Request, final HP, motion, effect lifetime and item charges are separate. No runtime/L2/Stage/production change. Other scepter unique payloads remain protected or explicitly pending.

### Summon

ZombieWand is the actual survival producer of registered LoyalZombie; no egg/world producer in all-TF field-caller census. Capacity9. Use fails damage==max && !instabuild; exact244 default damage getters/setters clamp0..max, so no ordinary overshoot exploit inferred. Server native POV ray uses Player eye/look, current blockInteractionRange, OUTLINE/Fluid.NONE. Non-MISS creates LoyalZombie at exact hit location, requires noCollision(entity,itsBB), else PASS without cost. spawnAnim, setTame(true,false), Player ownerUUID, Strength1200/amp1, optional baby, addFreshEntity, ENTITY_PLACE and noncreative durability request1. Add return ignored: later denied add does not gate cost. No finalizeSpawn, injected gear/target, bespoke cap or cooldown. Client/MISS sided success without server summon/cost.

### Loyal body

TamableAnimal, registered category MONSTER, HP40/speed.3/armor3, dimensions.6x1.95, not fireproof. Actual supplier LoyalZombie.registerAttributes starts Mob base, NOT Zombie, adds no ATTACK_DAMAGE. TF zombies tag/native undead nesting does not import Zombie sun burning, reinforcement or conversion. No phase/regen. dropExperience empty, native loot table empty; isFood=false, offspring null. removeWhenFarAway=!isTame, so genuine scepter tame avoids normal far-away despawn. No Lich master/shared HP.

### Loyal hit

doHurtTarget requests fixed7 minecraft:mob_attack, direct=causing=LoyalZombie, NOT summoner. Only true then raw push(0,.2,0), not scaled by knockback resistance. False no push. No ATTACK_DAMAGE/Strength/Weakness read, super Mob melee, enchantment modify/post-attack helper or weapon callback. Native recipient events/admission remain; tame-owner kill credit is separate from source identity. Strength1200/1 is a lifetime marker, not +6 here. Native melee goal20 cadence, eligibility, armor/shield/Resistance/protection/cooldown/absorption and Player difficulty remain. Extra motion uses ordinary later fall, no TF throw marker.

### Loyal expiry

Before super.aiStep: server && Strength absent && tickCount%20==0 -> self.hurt(ownerless twilightforest:expired,2), return ignored. No separate lifetime counter/owner-distance gate or explicit alive check; native hurt still rejects dead/invalid state. ANY present Strength amplifier/duration suppresses branch, including genuine admitted splash/lingering potion or AreaEffectCloud. Removal/expiry enables next modulo20 request. Standard spawn/feed1200ticks/amp1 uses native loaded effect ticking, not wall-clock countdown. Effects/health/owner persist, tickCount phase separate. No HP subtraction or guaranteed death time; exactly one actual EXPIRED combat caller.

### Expired source

EXPIRED exhaustion0/default when-caused-by-living-non-player scaling; direct/causing/position null, no owner difficulty scaling. Transitive tags: bypasses_armor, bypasses_shield, bypasses_wolf_armor, bypasses_invulnerability, bypasses_resistance, always_most_significant_fall, neoforge:is_technical. Not is_fall, no_knockback, bypasses_cooldown/effects/enchantments. Native armor/shield/Resistance/invulnerable-flag bypasses apply; absorption, cooldown, events and custom enchantment logic remain native. Standard Protection requires NOT bypasses_invulnerability, so contributes0 despite no global bypasses_enchantments; Feather Falling also fails native fall/predicate. Native totem check rejects bypasses_invulnerability before consumption. ALWAYS_MOST_SIGNIFICANT_FALL is attribution, not fall HP damage. No source position/Living attacker for normal directed knockback. Default40HP/2 would need20 admitted unmitigated requests, not a measured lifetime.

### Loyal feed

interactAt requires resolved getOwner()!=null && owner.is(player), held rotten_flesh. remove Strength, add Strength1200/1, heal(1), sound, consume1 with Player creative handling, sidedSuccess. No explicit server/fullHP/renewal-needed gate and no cross-call success dependency; native remove/add/heal hooks may reject individual operations without stopping others. Stronger/longer Strength removed first if removal succeeds. Ordinary heal(), not HP write or undead instant-health potion damage. Other item/player falls through inherited interaction. No breed/tame behavior inferred.

### Loyal targets

Goals Float1, Melee4(speed1,longMemory), FollowOwner5(speed1,start10,stop2), stroll7/look9. Targets OwnerHurtBy1, OwnerHurtTarget2, HurtBy3, nearest Monster4(mustSee=true). Owner-response requires tame/notOrderedSit/resolved owner, new hurt timestamp, native TargetGoal.canAttack and wantsToAttack. Custom veto: Creeper/Ghast, same-owner tame LoyalZombie, PvP-protected Player, tame horse/other tame animal. NOT global canAttack: HurtBy and nearest Monster do not invoke wantsToAttack. Eligible Creeper can be selected by nearest Monster despite owner-response veto. Ghast is FlyingMob, not Monster, so it fails that class search; native HurtBy retaliation can still target an otherwise eligible Ghast. The registry MONSTER category is not the Java Monster class (Wraith likewise is FlyingMob). Native owner/team/combat/range/LOS/restriction gates remain; TamableAnimal.canAttack rejects owner and alliance follows resolved owner. No universal friendly-fire immunity/source rewrite.

### Loyal follow

Native follow starts squared distance>=100; continues navigation unfinished, distance>2 and !unableToMoveToOwner. Vetoes orderedSit/passenger/any leash data (mayBeLeashed, even unresolved holder)/spectator owner. Higher-priority melee may preempt. Recalc adjustedTickDelay10 (default reduced5 goal callbacks) selects navigation1 or teleport when owner distanceSquared>=144. Up to10 integer offsets X/Z-3..3, at least one abs>=2, Y-1..1; WALKABLE, no leaves below (canFlyToOwnerfalse), translatedBB noCollision, then centered X/Z+.5 moveTo and nav stop. Native relocation, no HP/owner change or arbitrary compat teleport.

### Loyal baby

ZombieWand HEAD MysticCrown && randomFloat<=.1 -> setBaby(true), AFTER collision check using adult dimensions. Custom flag half dimensions .3x.975/eye.93, transient minecraft:baby +.5 ADD_MULTIPLIED_BASE speed ->.45. setBaby first removes same modifier, adds server-only; does not set AgeableMob.age. Native age tick updates its own age/flag, not Loyal custom flag: this baby does not grow via ordinary24000tick aging. Save IsBaby restored after parent read reinstates speed without stacking. HP40/armor3/fixed7/lifetime unchanged; no Crown wear or charge discount in this item.

### Charges

hurtButDontBreak: if damageable, item.damageItem(amount,entity,empty callback) first; entity null or !hasInfiniteMaterials then positive amount passes native durability-enchantment processing (nonpositive result returns). Nonzero ServerPlayer amount triggers durability criterion; setDamageValue(current+amount), exact244 clamp0..max. Never shrinks/breaks item at max. Unbreakable/item hooks/Unbreaking/creative remain native. Zombie/Fortification9, Twilight/Lifedrain99. Actual helper callers also MoonwormQueen and DamageableStackDispenseBehavior; payloads there remain pending. Charges are durability, not HP.

### Renewal routes

Renewal data: four #twilightforest:scepters, maxLevel1, HAND, native tick RechargeScepterEffect, no random requirement. Server Living.baseTick -> EnchantmentHelper.tickEffects -> equipment/item matchingSlot -> Enchantment.tick -> effect.apply -> applyRecharge. Main/offhand run each native tick, including selected mainhand; exact244 uses getAllEnchantments. Separately all four item.inventoryTick require tickCount%20==0, ServerLevel, literal ENCHANTMENTS component Renewal>0, !isSelected. Exact244 Inventory.tick uses global slot, selected==slot: offhand/unselected inventory eligible; offhand has both routes. Helper requires Player AND damage==max; partial use/mob holder no recharge. No level scaling/XP/HP operation. Shared inventory consumption order may matter; no simultaneous-refill guarantee.

### Renewal algorithm

Queries current CRAFTING recipes filtered ScepterRepairRecipe. For each same-scepter recipe copies ingredients, scans ONLY Player.inventory.items in index order. Nonempty EXANIMATE_ESSENCE -> shrink1,setDamage0,return (no creative exemption). Otherwise each still-needed Ingredient.test match removes it and records slot; complete ingredient list ends inventory scan. If recorded slot count equals ingredient count, each stack shrinks1 THEN remainder is queried/added/dropped; subtract recipe repair amount. Slots list lives outside recipe loop, not reset; no return/exhausted recheck after normal repair. Installed data has one matching recipe each, so no invented multiple-recipe producer. Essence not globally prioritized: earlier complete ingredients stop scan; essence after partial match consumes itself without recorded ingredients. Native clamp retained.

### Repair data

Installed repair amount9: Twilight #c:ender_pearls, Lifedrain fermented_spider_eye, Fortification golden_apple, Zombie potion plus rotten_flesh. Zombie potion ingredient ORs normal/long/strong Strength potion_contents for minecraft:potion. Renewal fully restores9-capacity, only9 of99 for others; essence restoresall. Compound/DataComponentIngredient strict defaultsfalse: actual item plus WHOLE potion_contents equality, unrelated stack components allowed, changed custom effects/color inside contents rejected; splash/lingering wrong item. Native Potion has no ordinary crafting remainder declaration; no promised glass bottle. Generic after-shrink remainder lookup can lose remainder on emptied stack, preserved without fix.

### Crafting

ScepterRepairRecipe extends CustomRecipe (special/empty display result). Single-ingredient match: exactly one damaged same scepter; every other occupied slot actual Ingredient.test, n>0 and damage+9-9*n>0 -> n<=ceil(damage/9), per occupied slot not stack count. Zombie multi-ingredient branch finds one damaged scepter, repairItems.size==ingredientCount-1, then input.stackedContents.canCraft(this,null). CraftingInput accounts each nonempty slot once; StackedContents indexes registry ITEM ID; RecipePicker uses Ingredient.getStackingIds. Exact244 Ingredient samples custom ingredient items but reduces them to ITEM IDs, without Ingredient.test/component checks. Thus manual Zombie repair statically accepts any minecraft:potion contents +rotten_flesh+damaged scepter, unlike Renewal Strength requirement. Water/other potion is real manual native path; splash/lingering still wrong IDs. No repair patch or runtime result claimed.

### Crafting output

assemble creates target scepter, copies original components, subtracts9*n single or9 multi, native clamp. Enchants/name preserved. Native crafting consumes one per used slot and uses normal recipe remainder callback; inventory recharge separate. Literal canCraftInDimensions is repairItems.size+1 > width*height, inverted-looking but preserved. RecipeManager.getRecipeFor uses matches, not that dimension method, so it does not veto ordinary manual matching; no recipe-book UI outcome claimed. Full serializer pins item/ingredient/int amount; external recipe/data-pack changes outside fixed native defaults.

### Persistence scope

Native Health/effects/owner UUID/Sitting persist; IsBaby custom and native Age separate. No bespoke saved Strength countdown/attack resource. Unresolved owner prevents owner feed/follow, not loaded expiry. Empty loot/XP, visuals and acquisition excluded. Other scepter payloads, Crown material/other bonuses, Essence fire/candle and Moonworm/dispenser payloads remain unfinished separately. No runtime or production claims.

## Packages

| Mechanic | Primary classification |
|---|---|
| Zombie Scepter native owned summon | CUSTOM_CONTROL |
| Loyal Zombie fixed attack and successful push | VANILLA_COMPOSITE |
| Loyal Zombie absent-Strength expiration | CUSTOM_DAMAGE |
| Owner flesh feed and effect/heal refresh | VANILLA_COMPOSITE |
| Loyal Zombie owner response and follow | VANILLA_COMPOSITE |
| Crown-produced persistent Loyal baby | VANILLA_LIKE_EXTENDED |
| Persistent scepter durability charges | CUSTOM_RESOURCE |
| Renewal hand/inventory reagent recharge | CUSTOM_RESOURCE |
| Special native manual repair matching | CUSTOM_RESOURCE |

## Custom source callers

| Type | Amount | Source identity |
|---|---|---|
| twilightforest:expired | 2 per server tickCount%20==0 while Strength absent; hurt return ignored. | Both null; no source position or summoner attribution. |

## Scope and exclusions

- Five full native classes plus actual tag/data/registration and raw/exact244 caller chains.
- Other scepters only shared resource callbacks here; Fortification/Lifedrain payloads next. Protected Twilight bolt unchanged.
- Crown armor/other bonuses, Essence fire/candle and Moonworm/dispenser payloads remain separate.
- Recipe quirks and source predicates preserved, no runtime/Stage/L2/production/fixes.
- EXPIRED USED:27/40 reviewed,13 unfinished. Twilight PARTIAL, zero promotion; IceAndFire unstarted.

## Future native controls

- Real Zombie Scepter ray/collision/owner/Strength/resource and creative/add-return controls.
- Fixed7 melee/true push with effect/equipment/recipient controls.
- Natural Strength expiry versus native refresh; EXPIRED tags, Protection/totem/absorption/events and persistence.
- Owner feed independent returns, different target routes and native follow/teleport.
- Crown baby/adult collision/independent age flag/save without damage or HP change.
- Native charge consumption and main/offhand/inventory Renewal, ingredient/essence ordering, partial/mob negatives.
- Manual ITEM-ID repair versus Renewal potion component tests, copied components and native remainders.

[Semantic packages and paths](semantic-sections/twilightforest-summon-resources.json), [integrity](twilightforest-summon-resources-integrity.json), [full validation](r2f8i-summon-resources-validation.json).

Exact next task: Continue Task C with Fortification Scepter shield attachment/event admission/timer/producers and Lifedrain target/damage/control/execute/heal/food, reusing protected recharge. Then remaining utility/passive entities, weapons/armor/charms/projectiles/hazards/resources and13 unfinished custom DamageTypes. Protect each subsection toward R2f8 and final Twilight dedup/promotion. IceAndFire only after Twilight COMPLETE is protected; no runtime boss/L2/Stage/production/fixes/Phase6/7.
