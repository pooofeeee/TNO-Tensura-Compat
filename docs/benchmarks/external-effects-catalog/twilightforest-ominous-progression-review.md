# r2f8y - TWILIGHT_OMINOUS_PROGRESSION_SEMANTIC_REVIEW_COMPLETE

Installed TF4.8.3345 and exact Minecraft1.21.1/NeoForge21.1.244. Ominous Fire and Acid Rain are USED; all40 custom DamageType profiles now reviewed. This does not close whole Twilight: remaining structures/events/ASM/compatibility/source exclusions and final assembly still unfinished. Static only; runtime0; production/Stage/L2/Phase6/7 untouched.

Adds 9 reviewed packages / 33 delivery cases. Twilight remains PARTIAL at 247/848 drafts, zero promoted. REVIEW_REQUIRED 0.

## Native contracts

### Authority

Installed TF4.8.3345 and exact Minecraft1.21.1/NeoForge21.1.244. Ominous Fire and Acid Rain are USED; all40 custom DamageType profiles now reviewed. This does not close whole Twilight: remaining structures/events/ASM/compatibility/source exclusions and final assembly still unfinished. Static only; runtime0; production/Stage/L2/Phase6/7 untouched.

### Identity

Both use TFDamageTypes.getDamageSource: direct=null,causing=null,explicit/source position=null. Ominous exhaustion.1 and Acid Rain0, declarations when_caused_by_living_non_player but no causing entity so no difficulty scaling. Ominous tags BYPASSES_ARMOR,BYPASSES_SHIELD,NO_KNOCKBACK,PANIC_CAUSES,PANIC_ENVIRONMENTAL_CAUSES,WITHER_IMMUNE_TO,neoforge:is_magic; NOT IS_FIRE/IS_EXPLOSION/IS_PROJECTILE or environment/physical. Acid Rain tags BYPASSES_ARMOR,BYPASSES_SHIELD,BYPASSES_WOLF_ARMOR,NO_KNOCKBACK,WITCH_RESISTANT_TO,neoforge:is_environment/is_magic; NOT fire/projectile/explosion. Feedback effects=burning on Ominous is not ignition.

### Native admission

Both retain recipient invulnerability/client/dead, normal hurt cooldown, incoming/damage events, Resistance max(1-.2*(amp+1),0), applicable protection and absorption. Armor/shield are bypassed by actual tags, not by the source name; neither bypasses effects, Resistance, enchantments, cooldown or invulnerability. NO_KNOCKBACK suppresses ordinary fresh-hit hurt movement. Fire Resistance and fireImmune provide no type-based immunity because neither source is IS_FIRE. Native directional shield geometry is irrelevant to bypass tag, though loader shield hooks remain. Ominous lacks IGNITES_ARMOR_STANDS/CAN_BREAK_ARMOR_STAND; native stand override rejects. ItemEntity uses native item-health handling; ordinary fire-resistant item tagging is not an Ominous immunity. Wither own WITHER_IMMUNE_TO rejection and Witch WITCH_RESISTANT_TO reduction remain native; acid caller is Player-only, so do not fabricate Witch/Wolf exposure.

### Ominous contact

OminousFireBlock extends BaseFireBlock but overrides entityInside WITHOUT parent call. It skips any EntityType tagged minecraft:undead; all other Entity recipients request ownerless ominous_fire1. Hurt return discarded. No fireImmune, living-only, movement, age, crouch or explicit side predicate in body; native recipient performs admission. No native in_fire request, fire-timer increment,8second ignition or Frosted fire-downrank from this custom type. Fire-immune non-undead targets are not exempt here. Undead tag is independent of inverted heal/harm.

### Ominous block

Survival requires below face sturdyUP and current fluid empty. updateShape returns default Ominous Fire ifvalid elseAIR. canBurn always true only supplies inherited base-fire behavior; there is no FireBlock spreading/random-age tick in this class hierarchy. Registered no collision/replaceable/light15; actual loot table has no drops. Native BaseFireBlock.onPlace remains: on actual block change, Ominous block is in minecraft:fire block tag (independent of DamageType tags); Overworld/Nether empty portal shape and onTrySpawnPortal hook can replace with ordinary Nether portal, else native survival/removal. No guaranteed permanent fire or invented dimension bypass. Native player destroy/extinguish handling remains; clone pick gives Exanimate Essence.

### Essence delivery

ExanimateEssence.useOn first checks clicked real CandleBlock in17-entry vanilla CANDLE_MAP and LIT: replaces with matching Ominous Candle, preserving count1..4. Otherwise uses clickedPos.relative(face), requires canBeReplaced and OminousFire.canSurvive then writes Ominous Fire. Sound/BLOCK_PLACE and true flag follow branch; shrink1 whenflag, regardless setBlock return and without local creative exemption; sidedSuccess. Actual native ServerPlayerGameMode creative path restores original count after item use. Normal use/placement/event admission remains; no private helper or free damage delivery. Existing loot/recipe resources supply actual essence; protected Renewal use remains unchanged.

### Candle exclusion

Ominous Candle extends BaseEntityBlock, not OminousFireBlock/AbstractCandleBlock. No hurt, fire timer, conversion, entityInside override or ticking combat payload. CANDLES geometry/light and visual BE height fields are cosmetic/native terrain state. Empty-hand mayBuild interaction replaces with corresponding unlit ordinary candle at same count and calls extinguish; matching candle BlockItem can add until4, consumes1 via native infinite-material handling, sends actual placement criterion/stat/event. BE only stores transient visual heights, no custom persistent attack/owner. Candelabra separate OMINOUS lighting use accepts scepter or essence only from NORMAL, with no essence consumption in that branch; no Ominous Fire block or custom damage is emitted by that inspected callback. Wider Candelabra/source exclusions remain global closure.

### Death conversion

Registered EntityEvents LivingDeathEvent callback requires not canceled and exact source key OMINOUS_FIRE. A mere burning timer or class named OminousFireDamageSource is insufficient. Native totem/death prevention before die means no conversion event. For non-ServerPlayer, actual OMINOUS_FIRE entity-type data map must exist and level must beServerLevel; installed mappings Horse->ZombieHorse, Piglin->ZombifiedPiglin, Villager->ZombieVillager. Calls protected EntityUtil.convertEntity and ignores return; no event cancellation or alternate new type guessed from undead names.

### Conversion consequences

Protected generic conversion creates target, honors canLivingConvert for Living target, uses Mob.convertTo for Mob pairs (copy/clear equipment, native entity add, discardold), otherwise real addition/discard. Then overlays old NBT onto new NBT, restoresnewUUID, sets Living health to resultingmax, drops/clears equipment, preserves passenger rides and conversion callback. It is replacement/full-health initialization, not native heal or direct attack. On ordinary LivingEntity.die, death event precedes !isRemoved&&!dead: successful discard of old Mob suppresses its later normal death-loot branch. Failed/vetoed conversion leaves ordinary death to continue. Generic helper behavior reused unchanged; no duplicate Powder package.

### Player zombie

ServerPlayer death branch takes precedence over data-map membership: creates actual EntityType.ZOMBIE, attaches deceased GameProfile, custom player name, copiesposition, requests canPickUpLoottrue and babyfalse, THEN EventHooks.finalizeMobSpawn(CONVERSION,null), THEN addFreshEntity. No inventory/XP/player-health transfer, resurrection, allegiance or owner assignment. Native Zombie.finalizeSpawn can overwrite loot pickup withrandom<.55*specialDifficulty and can setbabytrue from native groupdata; thus adult/loottrue setters are NOT final guarantees. Native equipment/enchantment/door/jockey/difficulty attributes can apply; no spawn-obstruction check in TF caller, native finalization/add hooks remain. No null guard after Zombie.create in caller; no invented fallback. Player death event is not canceled and normal player death/keep-inventory processing continues. Profile attachment serializes SIMPLE_GAME_PROFILE; customname/native Zombie state save normally, no custom lifespan.

### Zombie reentry

Registered LivingIncomingDamageEvent callback: source not already OminousFireDamageSource, causingentity instanceof Zombie, zombie.hasData(ZOMBIFIED_PLAYER). Captures event.getAmount, cancels original, then recipient.hurt(new OminousFireDamageSource(original),amount), ignores nested return. Wrapper retains original typeHolder, but constructor passes original.getEntity as native DIRECT and original.getDirectEntity as native CAUSING; explicitposition=original.getSourcePosition. For genuine melee both entities are the same Zombie, so attribution is unchanged. A conditional indirect source would swap them; no native ranged-zombie source is invented. Guard prevents this callback recursively wrapping its own nested source. Normal nested native eligibility/defenses/events remain; it is not type ominous_fire unless original already was.

### Reentry effects

Original IncomingDamage cancellation makes ordinary LivingEntity.hurt returnfalse while nested hurt can independently succeed. Genuine Zombie melee therefore skips caller success-only Mob extra knockback/EnchantmentHelper.doPostAttackEffects/setLastHurtMob/playAttackSound and Zombie burning-attacker ignition; native recipient hurt feedback from nested hit can still occur. Player.hurt applies source scaling before Living incoming event, so nested virtual Player.hurt applies it again. With ordinary default mob_attack, no modifying external hooks and standard defenses pending: Hard maps inputx to2.25x across two1.5 passes; Easy applies min(x/2+1,x) twice; Normal unchanged; Peaceful returnszero before event. Not double damage requests that both admit: outer canceled, one nested processing path. Other subscribed incoming hooks may observe both dispatches according to native event order; no pack-wide count guarantee.

### Death message

Wrapper getLocalizedDeathMessage checks living.getKillCredit instanceof Zombie carrying profile. If victim isPlayer and its profileNAME equals stored profileNAME, selects self message; otherwise includes profile name. Not UUID ownership/hostility logic. Fallback delegates ordinary source death message. Genuine Zombie attack keeps mob_attack damage tags/mitigation and does not by itself trigger Ominous death conversion.

### Enforcement delivery

Actual registered PlayerTick.Post callback requires ServerPlayer/ServerLevel; every20player ticks, tfEnforcedProgression gameruletrue, !creative&&!spectator invokes Enforcement.enforceBiomeProgression. No TF dimension, rain, sky visibility, shelter, height, biome-weather or line-of-sight gate in this chain. Level biome at player.blockPosition -> same-ID Restriction registry lookup; missing biomekey/registry/restriction ->none. Requires player lacks required advancement. Calls registered enforcement consumer then optional StructureHints.tryHintForStructure regardless whether consumer applied payload that tick. Hint-monster mechanics and structure protection are separate subsequent closure work. Gamerule defaulttrue; actual world value remains runtime state, not inferred installedtrue.

### Advancement gate

Restriction stores rawfloat multiplier, optionalhint/toast and nonempty advancement list. PlayerHelper.playerHasRequiredAdvancements consumes ONLY FIRST iterable entry: emptylisttrue; server first advancement mustexist and isDone, missing=false; client first progressanalog. It does not AND all entries. Installed nine restriction lists each have one so no default contradiction, but reload/custom multi-entry behavior must be preserved. This exact helper was already pinned during Frosted review; no reopening of Frosted mechanics.

### Acid payload

Acid Rain consumer checks player.tickCount%5==0 and tickRateManager.runsNormally, then hurt(ownerlessacid_rain,restriction.multiplier); only ifhurtreturnsTRUE plays burn sound atplayer. Actual every20 outer caller means opportunities every20 ticks, not5; no native weather requirement. Installed Highlands .5 requires progress_merge, Thornlands1 requires progress_troll, FinalPlateau1.5 requires progress_troll. No secondary potion, fire timer, armor corrosion, equipment damage or native poison. Normal cooldown/absorption/Resistance/protection can change HP and return; a sound is not guaranteed positive HP loss.

### Other consumers

Same real outer biome path: Darkness every60ticks+normaltickrate adds vanillaDARKNESS duration200, amplifier(int)multiplier(default0), ambientfalse,particlestrue; native darkness blend22/no damaging server effect. Hunger every60 adds vanillaHUNGER duration100 withamp=currentamp+(int)multiplier else(int)multiplier(default1), native add/merge/cure; stacks while current persists. Native Hunger server effect adds .005*(amp+1) exhaustion per callback through native player food processing, not direct HP. Fire every60+normaltickrate invokes igniteForSeconds((float)(int)multiplier), default8 forFireSwamp, requiring progress_labyrinth. Native floor(seconds*20), then Living ceil(ticks*BURNING_TIME attribute), then Entity monotonic timer extension retained; subsequent on_fire source separate. Frost every60 adds protected Frosted100 amp0 SnowyForest or1 Glacier; reuse accepted package/path, no repeat review. Darkness sitesDarkForest progress_lich andDarkForestCenter progress_knights; Swamp Hunger progress_lich.

### Essence repair

Distinct genuine CRAFTING EssenceRepairRecipe requires one nonempty damaged SCEPTERS-tag stack plus one nonempty exact ExanimateEssence stack and no other occupiedslots; two essence slots or two scepters reject, stackcounts are not slotcounts. Output copies original scepter including components/count and setsDamage0. assemble alone does not revalidate essence, but actual recipe lookup/matches is admission. Dimensions area>=2. Native ResultSlot consumes one per occupiedslot and ordinary recipe remainders; no creative exemption invented. No enchantment restriction or requirement for fully exhausted charges. This fully repairs custom scepter charge resource without casting; distinct from protected nine-point manual recipes and automatic Renewal.

### Compatibility

GENERIC_CONDITIONAL_PRESENT for loader hurt/incoming/death/conversion/finalize/add/placement/effect/recipe hooks. Source-specific TF wrapper and TF advancement/restriction consumers are native TF mechanics. Recipe-viewer Ominous displays describe mappings, not actual conversion callers. Other external combat overrides scoped NONE_PROVEN; additional mod interactions UNKNOWN, no pack-wide compatibility certification. Protected Frosted, Powder conversion and scepter Renewal preserved. Remaining structures,portal/hints,events,ASM and source exclusions still ordinary unfinished review.

## Packages

| Mechanic | Primary classification |
|---|---|
| Ominous Fire native non-fire contact damage | CUSTOM_DAMAGE |
| Ominous death native mapped entity replacement | CUSTOM_CONTROL |
| Ominous player death profile-bearing Zombie | CUSTOM_RESOURCE |
| Zombified-player incoming source wrapper and native re-entry | CUSTOM_DAMAGE |
| Acid Rain native biome damage | CUSTOM_DAMAGE |
| Locked Dark Forest native Darkness | VANILLA_DIRECT |
| Locked Swamp native Hunger stacking | VANILLA_LIKE_EXTENDED |
| Locked Fire Swamp native ignition | VANILLA_DIRECT |
| Exanimate Essence native full scepter crafting repair | CUSTOM_RESOURCE |

## Custom source callers

| Type | Amount | Source identity |
|---|---|---|
| twilightforest:ominous_fire | 1 per overlap callback; request not finalHP. | Both use TFDamageTypes.getDamageSource: direct=null,causing=null,explicit/source position=null. Ominous exhaustion.1 and Acid Rain0, declarations when_caused_by_living_non_player but no causing entity so no difficulty scaling. Ominous tags BYPASSES_ARMOR,BYPASSES_SHIELD,NO_KNOCKBACK,PANIC_CAUSES,PANIC_ENVIRONMENTAL_CAUSES,WITHER_IMMUNE_TO,neoforge:is_magic; NOT IS_FIRE/IS_EXPLOSION/IS_PROJECTILE or environment/physical. Acid Rain tags BYPASSES_ARMOR,BYPASSES_SHIELD,BYPASSES_WOLF_ARMOR,NO_KNOCKBACK,WITCH_RESISTANT_TO,neoforge:is_environment/is_magic; NOT fire/projectile/explosion. Feedback effects=burning on Ominous is not ignition. |
| twilightforest:acid_rain | restriction.multiplier: .5/1/1.5 installed; request not finalHP. | Both use TFDamageTypes.getDamageSource: direct=null,causing=null,explicit/source position=null. Ominous exhaustion.1 and Acid Rain0, declarations when_caused_by_living_non_player but no causing entity so no difficulty scaling. Ominous tags BYPASSES_ARMOR,BYPASSES_SHIELD,NO_KNOCKBACK,PANIC_CAUSES,PANIC_ENVIRONMENTAL_CAUSES,WITHER_IMMUNE_TO,neoforge:is_magic; NOT IS_FIRE/IS_EXPLOSION/IS_PROJECTILE or environment/physical. Acid Rain tags BYPASSES_ARMOR,BYPASSES_SHIELD,BYPASSES_WOLF_ARMOR,NO_KNOCKBACK,WITCH_RESISTANT_TO,neoforge:is_environment/is_magic; NOT fire/projectile/explosion. Feedback effects=burning on Ominous is not ignition. |

## Scope and exclusions

- Ominous Candle visual names do not emit the Ominous Fire damage source; Candelabra OMINOUS lighting callback is also not a damage/conversion producer.
- Protected Frosted biome payload and Powder generic conversion reused; no duplicate Frosted or Powder mechanic.
- Essence automatic Renewal was already protected; only distinct Essence CRAFTING recipe is new.
- Source-wrapper death message is not a new DamageType or proof of Ominous conversion on mob_attack deaths.
- All40 custom types reviewed, but remaining portal/hints/structure defenses, events, ASM and global compatibility/source closure prevent Twilight COMPLETE until finished.

## Future native controls

- Genuine Essence/block overlap with source/type/undead/native defenses, no-fire side effects and base-fire portal controls.
- Actual lethal Ominous mapped Mob conversion versus veto/totem/nonlethal and removed-old death-loot behavior.
- Real player death/profile Zombie finalization/persistence and subsequent native melee re-entry, difficulty, defenses and outer success-only callbacks.
- Actual PlayerTick biome enforcement with gamerule/advancement/tickrate/20tick cadence and allnine installed restrictions; no synthetic weather source.
- Distinct native Essence crafting full repair versus existing Renewal/manual recharge.

[Semantic packages and paths](semantic-sections/twilightforest-ominous-progression.json), [integrity](twilightforest-ominous-progression-integrity.json), [full validation](r2f8y-ominous-progression-validation.json).

Exact next task: All40 custom DamageTypes are reviewed. Continue remaining Twilight structure defenses/hint producers and portal/control blocks, then remaining events/nested ASM/compatibility/source exclusions. Protect R2f8 complete and final Twilight dedup/promotion; IceAndFire only after live-verified Twilight COMPLETE. Static only.
