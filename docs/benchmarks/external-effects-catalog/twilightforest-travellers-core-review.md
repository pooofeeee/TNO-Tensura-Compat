# r2f8o - TWILIGHT_TRAVELLERS_CORE_SEMANTIC_REVIEW_COMPLETE

Installed Twilight4.8.3345, raw Minecraft1.21.1 and exact NeoForge21.1.244, plus the installed service-registered nested TF ASM archive. Static research only, runtime tests0. This section closes modifier admission/crafting/removal, base equipment and non-movement defensive/resource payloads. Movement, belt/display/zoom and other ASM hooks remain pending. No compatibility implementation, HP/SHP simulation, Stage/production/Phase6/7 changes.

Adds 11 reviewed packages / 38 delivery cases. Twilight remains PARTIAL at 174/544 drafts, zero promoted. REVIEW_REQUIRED 0.

## Native contracts

### Authority

Installed Twilight4.8.3345, raw Minecraft1.21.1 and exact NeoForge21.1.244, plus the installed service-registered nested TF ASM archive. Static research only, runtime tests0. This section closes modifier admission/crafting/removal, base equipment and non-movement defensive/resource payloads. Movement, belt/display/zoom and other ASM hooks remain pending. No compatibility implementation, HP/SHP simulation, Stage/production/Phase6/7 changes.

### Registry

TravellersModifier.CODEC dispatches through TFRegistries.TRAVELLERS_MODIFIER_TYPE; RegistrationEvents registers the synced datapack TRAVELLERS_MODIFIERS registry and cache invalidation reload listener. Manager caches found and missing keys; reload clears both. Native packaged data/twilightforest/twilight/travellers_modifiers/*.json, not tooltip prose, supplies defaults. Component modifiers test presence of their one component; entry modifiers test marker presence; transferable modifiers require marker plus payload component; builtin modifiers test component presence. Presence is not a checked equality to the packaged default value. Registry lookup absence returns false. No recipe slot-count or item-type check inside low-level addModifier; actual recipes enforce their own admission.

### Activation

TravellersModifier.isActive requires hasModifier, !spectator, and either !isTravellersArmorAndBroken(stack) or modifier key in ALWAYS_ACTIVE. The sole ALWAYS_ACTIVE key is AUTO_REPAIR. Broken means IS_TRAVELLERS_GEAR marker AND isDamageableItem AND damage>=maxDamage-1. Native isDamageableItem requires MAX_DAMAGE and DAMAGE and no UNBREAKABLE. Explicit-stack overload uses that supplied stack; no independent equipment-group validation or required gear marker for component activation. Normal callers below retrieve real HEAD/CHEST/LEGS/FEET stacks. Entity-only overload resolves exactly one armor slot from registry group; zero or multiple matching armor slots returns EMPTY, so ARMOR-wide Auto-Repair uses its explicit per-stack loop. Neither selected payloads nor activation manager query Curios inventory. No claim that another installed mod cannot redirect general equipment APIs.

### Crafting

Actual shaped/shapeless modifier recipes select the first TravellersModifiable input with getModifierSlots()>0; require countInsertableModifiers<slots, target modifier absent, and <=1 transferable data-provider ingredient; shaped pattern or exact shapeless ingredient count/matching must also pass. Assembly copies armor then tries transfer first and add second, returning EMPTY if neither works. Count includes registered Insertable and !isAbility present modifiers; builtin abilities do not consume a slot. Component addition writes its packaged value; nonbuiltin entry addition writes actual attribute entries plus marker; builtin entry addition writes marker only. Transfer searches Ingredient item arrays having any matching payload; sole provider uses its first stack payload, not a merge; >1 fails, absent provider falls back to default addition. Genuine recipes use actual input singleton ingredients. Gear/component state, damage, name and other copied components persist in outputs; no added DamageSource.

### Removal

AnvilUpdate cancels when BOTH input stacks have IS_TRAVELLERS_GEAR, including different gear items. Grindstone OnPlace with a live server: two marked gear inputs cancel; one marked gear with no insertable nonability modifier cancels; otherwise copy input and remove every present registered insertable nonability modifier, then use copied result. Component removal deletes component, nonbuiltin entry removal deletes matching attribute entries+marker, transfer removal deletes marker+payload; builtin abilities remain. OnTake returns contained swap-hotbar or item-display contents only from a unique matching marked input via ItemHandlerHelper.giveItemToPlayer, whose server overflow becomes a real ItemEntity with40-tick pickup delay. This is removal/resource behavior, not damage. Belt/display use payloads are reviewed next. Vest+Gloves merge accepts exactly one of each, vest without HAS_GLOVES, copies only vest and adds HAS_GLOVES; no new modifier slot or glove enchant/component merge. ItemCrafted advancement trigger is bookkeeping, not an additional buff.

### Equipment

Four durable pieces Goggles/Vest/Wings/Boots have3 insertable slots each, durability multiplier12 ->132/192/180/156, and actual armor attribute2/4/3/2 with toughness0/knockback resistance0. Material enchantability0. Gloves(CHEST) and Belt(LEGS) are nondurable, slots0, stack limit1. Their plain properties inherit native COMMON_ITEM_COMPONENTS.ATTRIBUTE_MODIFIERS=EMPTY; TF constructor stores that nonnull empty value BEFORE virtual getDefaultAttributeModifiers(), which then returns that same empty value. Thus native Gloves/Belt do NOT acquire the material chest4/legs3 armor merely by extending ArmorItem. The four main pieces explicitly seed their own armor entries; no doubled material armor. ItemAttributeModifiers/loader equipment pipeline applies actual entries. Base Vest also carries Swift Swim water-movement +1 and Boots step-height +.5; their full movement controls are deferred. Wings carries native high-jump component1; Goggles zoom .3, also deferred.

### Equipment predicates

TravellersArmorItem.makesPiglinsNeutral returns true for exact Goggles item OR HAS_WINGS component, without broken/spectator/modifier-active check. Native PiglinAi.isWearingGold checks equipped armor/body stacks through the item hook; this affects that gold-clothing admission, not every aggression/retaliation rule. canWalkOnPowderedSnow is exact TravellersBoots item, again no broken check; native powder-snow collision eligibility remains. These callbacks are independent of disabled active modifiers. isEnchantable/isPrimaryItemFor/supportsEnchantment are false, isBookEnchantable true, isRepairable false. Native anvil still tests inherited ArmorItem.isValidRepairItem(TANNED_LEATHER) for material repair, independently of isRepairable; ordinary damage/cost/level/output checks remain. Two-gear anvil combination is separately canceled. Enchantment-book true alone does not overcome supportsEnchantment false for ordinary survival; native creative compatibility override remains. No HP/SHP or custom damage from equipping.

### Durability

Uncanceled ArmorHurtEvent: each marked gear stack whose damage+newArmorWear>=maxDamage gets new wear=maxDamage-currentDamage-1; else if sum>=maxDamage-1 and wearer ServerPlayer, play item-break sound. Native ArmorHurtEvent.setNewDamage does not clamp; TF has no extra max(0) for anomalous states. Native CommonHooks applies integer newDamage through stack.hurtAndBreak after uncanceled event, preserving enchant/durability/creative eligibility. This caps ordinary armor wear at last durability, not arbitrary stack destruction or all durability callers, and does not cancel/reduce incoming HP damage. Later registered setLastDamageArmorTime records current gameTime if ANY EquipmentSlot event newDamage>0, including other armor; zero wear does not refresh. No hurt-return/positive-HP requirement in this tracking handler. It records event wear, not a later guaranteed consumed durability amount.

### Broken attributes

ItemAttributeModifierEvent handling runs only with nonnull ServerLifecycleHooks.currentServer and marked damageable gear. At damage>=max-1, if raw ATTRIBUTE_MODIFIERS component exists, union its entries with any STORED_BROKEN_ATTRIBUTES in LinkedHashSet, persist that union, and clear event modifiers. It does not erase raw component or stop unrelated enchantment attribute pass. At repaired damage<max-1, stored entries replace corresponding event entries, stored component is removed and event.build written back to raw ATTRIBUTE_MODIFIERS. ItemStack.getAttributeModifiers computes through CommonHooks on each retrieval; subsequent equipment refresh uses returned entries. Client-only tooltip environment lacking currentServer need not match server attribute suppression. Stored component is persistent/network-synchronized; no timer/HP/shield resource, no universal suppression of later other-mod listeners or separately installed transient modifiers.

### Broken removal

Stored-broken attributes are a separate component that TravellersEntryModifier.removeModifier never edits. With a genuine broken Aquatic piece whose STORED_BROKEN_ATTRIBUTES already contains its oxygen/mining entries, grindstone removal copies the piece, clears the Aquatic marker/current entries but preserves that stored component. Native grindstone custom output is returned before ordinary vanilla computeResult. Subsequent legitimate Tanned Leather anvil repair can make damage<max-1; the next attribute event restores ALL saved entries without checking whether their marker/modifier was removed. Thus Aquatic attributes can return with no Aquatic marker. Removing all modifiers also removes Auto-Repair, so this sequence does not assume it remains available. This is a proven native component lifecycle, no patch or runtime exploit test; absence of marker does not prove absence of previously stored attributes.

### Repair

EntityTick.Post calls Auto-Repair only server-side for LivingEntity. Require gameTime-LAST_DAMAGE_ARMOR_TIME>200 strict; attachment defaults0 and serializes LONG. Iterate real armor slots; each requires probability component and explicit-stack active AUTO_REPAIR, which remains active when broken but not spectator. Independent per-piece roll: if adjustedProbability>random.nextFloat(), setDamageValue(max(oldDamage-1,0)). No XP/item consumption, heal(), HP write or DamageSource. No explicit isDamaged/isDamageable gate in loop. Base p=.001. If !canSeeSky use p; otherwise TF dimension TYPE ->1-(1-p)^1.5; other dimension daytime ->1-(1-p)^3; other nighttime ->p. Uses dimension type, sky visibility and day rather than brightness/weather. One repair point can leave max-1 broken state and restore attributes on subsequent native query. Not guaranteed periodic repair; component codec positive float has no upper probability clamp.

### Dodge

ProjectileImpactEvent must carry EntityHitResult whose recipient is LivingEntity. Read its current CHEST stack, active PERFECT_DODGE and nonnull probability; installed default.3. Client cancels immediately; server returns if probability<=random.nextFloat(), otherwise cancels and emits sound/particles. No owner/causing/direct-entity test, no DamageType/tag, damage amount, held shield, invulnerableTime, sight, boss or distance gate. It cancels that native impact event, not LivingHurt, and neither reflects/reassigns/discards projectile nor changes HP. Exact244 AbstractArrow/ThrowableProjectile call EventHooks before native impact callbacks; cancellation suppresses that impact, with remaining projectile motion/lifetime governed by its own caller. Cannot protect from arbitrary hurts or projectile implementations that do not post this event. Failed server roll uses unchanged native source, armor/shield/Resistance/protection/cooldown/eligibility.

### Magnet

ProjectileImpactEvent requires owner LivingEntity, BLOCK hit and projectile.tickCount<200, then active owner ARROW_MAGNETISM, AbstractArrow and !client. Player owner: if !hasInfiniteMaterials && pickup==ALLOWED, give getPickupItemStackOrigin() to player and mark inventory changed. Native method returns stored pickup stack (not newly generated generic arrow). Discard if ALLOWED, or CREATIVE_ONLY && player.isCreative; DISALLOWED stays, CREATIVE_ONLY survival stays. Creative ALLOWED discards without granting extra item. Nonplayer living owner discards eligible arrow without inventory return regardless pickup mode. Reads CURRENT owner chest at impact; shooting vest snapshot is not stored. No distance/line-of-sight/projectile DamageType/damage-success test. Full inventory uses native helper remainder drop. It does NOT cancel event; exact244 Arrow.tick has no removal recheck between EventHooks return and hitTargetOrDeflectSelf, so a discard here does not itself suppress already-selected block impact callbacks. No target HP damage or owner reassignment.

### Allnight

Active HEAD ALL_NIGHT_GOGGLES sets PlayerSpawnPhantomsEvent.Result.DENY. Native PhantomSpawner asks per non-spectator player and shouldSpawnPhantoms returns false for DENY, retaining existing global spawner/game-rule timing. Does not reset TIME_SINCE_REST, remove existing phantoms, deny all other players, block eggs/summons or grant damage immunity. TravellersGogglesItem.isEnderMask delegates same active modifier; native EnderMan.isLookingAtMe calls CommonHooks.shouldSuppressEnderManAnger before dot-product/sight test. Thus suppresses gaze admission while eligible, not already-established anger/retaliation. No night-vision effect, HP/source write, resource consumption or cooldown in these callbacks. Broken/missing modifier/spectator disable active admission; base Goggles Piglin predicate is independent.

### Stealth

Server PlayerTick.Post calls travellersStealth: active CHEST STEALTH and crouching applies native INVISIBILITY(duration2,amplifier0,ambient=false,particles=false,icon=false) each tick. Client RenderFrame.Pre for rendered Players uses same active/crouch predicate and setInvisible(true), not another server effect. If active but not crouching and current Invisibility exists with duration<2, setInvisible(false); longer effects not explicitly cleared, no removeEffect call. Removing/breaking gear stops renewal; native short effect expires through ordinary ticking. Native addEffect eligibility/merge/hooks remain. Ordinary invisibility visibility multiplier includes armor coverage and native visibility events; no guaranteed target reset, stealth immunity, HP reduction or new source. Armor-shrouding ASM is a separate pending mechanic.

### Haste

Server EntityTick.Post for LivingEntity reads active CHEST HASTE and nonnull amplifier, then addEffect(DIG_SPEED,duration2,amp,ambient=false,particles=false,icon=false). Packaged amp1 (HasteII), refreshed while eligible; no extra active cost. Native effect merge/applicability/expiry remain. Native Haste adds ATTACK_SPEED .1*(amp+1) ADD_MULTIPLIED_TOTAL (about+.2 here), mining factor1+.2*(amp+1) (1.4 here), and swing duration6-(1+amp) (4 ticks here), subject to ordinary attribute/effect selection and other modifiers. No direct attack-damage bonus, hurt callback, DamageSource or HP/SHP write. Removing gear stops refresh without deleting an independent stronger/longer Haste effect.

### Aquatic

Native Aquatic Agility insertion adds HEAD OXYGEN_BONUS+3 ADD_VALUE and PLAYER.SUBMERGED_MINING_SPEED+4 ADD_MULTIPLIED_TOTAL plus marker. These are actual item attributes, not a water-breathing MobEffect or oxygen refill. Native decreaseAirSupply: with oxygen value d>0 retain current air when random.nextDouble()>=1/(d+1), else decrement1; +3 alone yields decrement probability.25, not infinite breath/drowning immunity. Native Player.getDestroySpeed multiplies by submerged-mining attribute in water (default.2 becomes1 before other changes); above-water mining has no corresponding multiplier from this attribute. Native equipment, broken-attribute suppression, removal and ordinary attribute clamps remain; no custom DamageSource or HP write.

### Eater

Installed nested ReduceMovementFoodExhaustionTransformer is registered by protected TFCoreMod service. Targets EXACTLY ServerPlayer.checkMovementStatistics(DDD)V and Player.jumpFromGround()V; inserts PlayerHooks.getFoodExhaustion before each matching Player/ServerPlayer.causeFoodExhaustion(float) call. Hook reads current CHEST active EFFICIENT_EATER with nonnull divisor and returns f*(1/divisor), default divisor2. Thus swim/underwater/water movement .01 per block ->.005; sprint .1 per block ->.05; native walk/crouch0 remains0; sprint-jump.2->.1 and ordinary jump.05->.025. Native rounded-centimeter movement, passenger/no-motion branches remain. No change to damage/attack/mining/regeneration exhaustion callers outside those target methods; no food gain/heal/refund. Native causeFoodExhaustion server-only and !abilities.invulnerable still applies; FoodData accumulation/conversion remains. Codec.FLOAT and hook impose no additional positive/nonzero divisor guard; installed value2 is the legitimate default.

### Persistence sources

Gear modifier/attribute/stored-broken components have native persistent/network codecs; ordinary ItemStack save/load/copy carries them. LAST_DAMAGE_ARMOR_TIME is serialized; no custom death-copy routine for it is added by this subsection. Native crafted base items do not automatically carry the sample auto-repair/dodge/stealth combinations used by DefaultModifiedTravellersGearGetter; actual modifier recipes must be performed. No innate Curio passive tick/slot scan is present in the reviewed Travellers callbacks: real equipment slots and vanilla/loader events are the proven delivery. Source-specific compatibility beyond those generic hooks is NONE_PROVEN here; this is not pack-wide compatibility certification. All eleven mechanics have no new custom DamageType; no fallback or synthetic damage was introduced.

## Packages

| Mechanic | Primary classification |
|---|---|
| Travellers modifier registry, crafting and removal | CUSTOM_RESOURCE |
| Travellers native loadout and equipment predicates | VANILLA_COMPOSITE |
| Travellers last-durability and stored-attribute state | CUSTOM_RESOURCE |
| Travellers native Auto-Repair probability | CUSTOM_RESOURCE |
| Travellers Perfect Dodge impact veto | BINARY_MECHANIC |
| Travellers missed-arrow native recovery | CUSTOM_RESOURCE |
| Travellers All-Night native admission | BINARY_MECHANIC |
| Travellers crouch invisibility | VANILLA_LIKE_EXTENDED |
| Travellers passive native Haste | VANILLA_LIKE_EXTENDED |
| Travellers oxygen and submerged mining attributes | VANILLA_COMPOSITE |
| Travellers movement and jump exhaustion reduction | CUSTOM_RESOURCE |

## Custom source callers

| Type | Amount | Source identity |
|---|---|---|

## Scope and exclusions

- Nineteen complete declared framework/base-item/recipe classes, selected non-movement handlers, actual item/component/registry producers and installed exhaustion ASM are pinned.
- Move/control/packet contracts, belt/display/zoom and other ASM/Emperor cloth are explicitly unfinished, not REVIEW_REQUIRED or silently covered by framework evidence.
- Tooltips/advancement/cosmetic visuals do not add damage; material defense is not assumed for empty-attribute Gloves/Belt.
- No new custom DamageType or direct HP/SHP payload. Remaining10 declarations belong to later source review. Whole Twilight PARTIAL, zero promoted; no runtime or compatibility fix.

## Future native controls

- Actual modifier crafting, slot cap, component transfer, grindstone and vest/gloves merge; native saves/reload.
- Real equipment, broken threshold, armor event wear and repair, current versus stored attributes, sky probability and positive-wear timer.
- Native projectile impact dodge/recovery with owner/pickup/age/gear/client-server/overflow and failed-admission controls.
- Native per-player phantom/gaze/gold/snow eligibility, crouch Invisibility, Haste and Aquatic attributes.
- Real transformed movement/jump exhaustion versus unmodified attack/damage/regen callers; no synthetic events.

[Semantic packages and paths](semantic-sections/twilightforest-travellers-core.json), [integrity](twilightforest-travellers-core-integrity.json), [full validation](r2f8o-travellers-core-validation.json).

Exact next task: Complete Travellers movement/control and installed ASM paths (water-walk, unrestrained, slimy soles, high-step/swim/jump, gradual glide, double-jump, sidestep, straight-ahead/agile ranger and packets); then belt/display/zoom and Emperor cloth, remaining utilities/food/passive entities/hazards,10 custom DamageTypes, full ASM/compatibility/source exclusions, R2f8 and final Twilight promotion. IceAndFire only after COMPLETE pushed/live verified; no runtime boss/L2/Stage/production/Phase6/7.
