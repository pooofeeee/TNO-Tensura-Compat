# r2f8n - TWILIGHT_CHARMS_CASKETS_SEMANTIC_REVIEW_COMPLETE

Installed TF4.8.3345, raw MC1.21.1, exact NeoForge21.1.244 and selected installed Curios9.5.1 dependency bytes. Static research only; no runtime boss/L2, fixes, Stage/production or Phase6/7. Existing Phantom armor stats are protected; this section closes its real retention producer. Native HP writes are described as installed TF behavior, never added or simulated.

Adds 8 reviewed packages / 30 delivery cases. Twilight remains PARTIAL at 163/506 drafts, zero promoted. REVIEW_REQUIRED 0.

## Native contracts

### Authority

Installed TF4.8.3345, raw MC1.21.1, exact NeoForge21.1.244 and selected installed Curios9.5.1 dependency bytes. Static research only; no runtime boss/L2, fixes, Stage/production or Phase6/7. Existing Phantom armor stats are protected; this section closes its real retention producer. Native HP writes are described as installed TF behavior, never added or simulated.

### Death order

CharmEvents.setup registers applyCharmOfLife at HIGHEST LivingDeathEvent, applyKeepingAndCasket at HIGH, returnItemsOnRespawn at ordinary priority. Each death handler explicitly requires !event.canceled, server, Player, !FakePlayer, !isCreative and !isSpectator. Life can cancel event before Keeping; same-priority/other-mod ordering is not invented. Native Living.hurt ordinarily checks Totem before die; successful native Totem prevents death event and charm consumption. Totem rejects BYPASSES_INVULNERABILITY, searches hands and has distinct effects/cures; TF Life handler has no DamageSource/tag check, so that tag alone does not veto Life once death event is reached. Exact244 ServerPlayer.die emits ENTITY_DIE game event then onLivingDeath; cancellation skips subsequent ordinary death/drops. No universal protection from removal/discard or pathways that never post eligible event.

### Life

handleCharmOfLife tries LifeII inventory, then equipped Curio II; only if neither succeeds tries LifeI inventory then Curio I. Consumes one. LifeI setHealth8 (native clamp to max), then Regeneration100 ticks amplifier0. LifeII setHealth(getMaxHealth), then Regeneration600 amplifier3, Resistance600 amplifier0, FireResistance600 amplifier0. Direct native setHealth, not heal and not damage cancellation before HP; no DamageSource for restoration. Does not explicitly clear existing effects/fire, grant absorption, modify invulnerableTime or restore hunger/SHP. addEffect native eligibility/merging/events/return behavior remains; returns true/cancels death even if an effect is rejected. Native Regeneration periodically heals1 with 50>>amplifier cadence (50/6 ticks here), subject to max/current health and native healing hooks, not guaranteed total HP. Higher LifeII priority can prefer Curio II over inventory I. Native packet/stat after activation, no extra item cooldown or charge field.

### Consume

TFItemStackUtils.consumeInventoryItem scans armor list first, then all36 main inventory slots, then offhand, stopping on first exact item match, shrink1. No held/hotbar-only condition for consuming charm/casket, no ender chest, bags or nested-container search. saveItemToTag true writes full pre-shrink stack to PlayerPersisted.CharmStack for later animation, not item reimbursement; Life inventory uses false, Keeping true. It also reads minecraft:block_state property damage if present, numeric parse else0, otherwise TF CASKET_DAMAGE component, into CasketDamage; normal casket has0. It does not clear old CasketDamage when neither property/component exists. Creative/spectator gate is in death handler, no permission/HP/source predicate in helper.

### Keeping

Only eligible uncanceled death with keepInventory=false runs handleCharmOfKeeping followed by stockKeepsakeCasket. Tries KeepingIII against all36 items, then II against real subList0..9 hotbar. Each candidate eligibility copies selected list plus armor/offhand, ignores stacks matching that SAME charm, and returns false if all remaining entries empty; otherwise tries inventory consumption then Curio. Other items including another tier count. Successful III transfers all36 plus armor/offhand; II transfers hotbar into same0..8 and armor/offhand. Item copies moved into temporary Inventory, original slots emptied. No XP/food/health/SHP preservation here. Curios-only contents do not satisfy base-list eligibility. Native later drop/vanishing logic sees the remaining inventory, not moved stacks.

### Keeping one

If III/II did not succeed and selected index is valid hotbar, installed bytecode calls NonNullList.of(selectedStack,new ItemStack[0]) for KeepingI. Native of uses Arrays.asList(varargs) with first argument only as default value; the passed list therefore has SIZE ZERO. This does not contain or alias the selected inventory slot. Candidate eligibility sees only armor/offhand; a selected item alone cannot trigger KeepingI. If other eligible armor/offhand exists and charm is available, I consumes one and transfers armor/offhand but NO selected/main slot. This is proven by caller and raw native implementation, not assumed intended behavior or a runtime test; no fix made.

### Reserve casket

keepWholeListAndCheckCasket copies each transferred stack. III starts skipCasketCheck=true so retains all selected caskets. Lower tiers reserve the first casket encountered across chosen items then armor then offhand for later death placement: if count>1 retain all but1 and leave original copy count1; if count1 leave original untouched, no retained copy. Further caskets transfer normally. Boolean result threads reservation across lists. Remaining unselected inventory may contain caskets too; actual consumption later scans normal armor/items/offhand order. No global guarantee that reserved casket is the exact consumed object.

### Tag retention

After charm attempts, independently scans all36 items, armor and offhand for twilightforest:kept_on_death, copying to same temporary Inventory slots and clearing originals. Installed tag exactly TowerKey, PhantomHelmet, PhantomChestplate. No charm required, no worn-only restriction and no enchantment/curse gate; still subject to eligible death and keepInventory=false outer condition. Armor stats stay protected prior package. If resulting temporary Inventory nonempty, native Inventory.save writes TFCharmInventory in PlayerPersisted. Full main/armor/offhand structure retains slot numbers; no accessory/backpack search. No explicit keep-existing TFCharmInventory merge here, so a newly saved nonempty result replaces that key.

### Persistence return

getPlayerData creates PlayerPersisted CompoundTag inside native persistent entity data. Exact244 ServerPlayer.restoreFrom copies old PlayerPersisted before PlayerClone; subsequent ordinary non-End-conquered ServerPlayer PlayerRespawnEvent runs returnStoredItems. TFInventory loadNoClear parses Slot byte&255: main0..35, armor100..103, offhand150. Empty valid destination gets saved stack; occupied destination queues saved stack for Inventory.add. Native add may merge/partially insert or fail when full; TF ignores return and neither drops nor retains leftovers, then clears/removes TFCharmInventory. Thus collision preserves existing slot but does not guarantee all saved items survive full inventory. Invalid-slot/empty parsed stacks skipped. No blind inventory clear. If CharmStack key exists, parsed stack sent in Keep animation packet/stat then key removed; this is independent of saved inventory presence and does not reimburse consumed charm. End-return respawn skips this restoration.

### Casket gate

After Keeping/tag moves, stockKeepsakeCasket checks current player Inventory.hasAnyMatching(nonempty item not KeepsakeCasket). If true, consumes one genuine casket through normal inventory helper; no casket means returns. Consumption happens BEFORE placement/validation, with no refund on later failure. If false (only caskets/empty left), loops normal Inventory slots, loads any TFCharmInventory into temp Inventory, attempts add(copy of each casket), ignores add return, empties original slot and re-saves key. This preserves casket-only remainder when space allows without placing a block; full storage can lose uninserted remainder. No Curios/bag items qualify gate or enter casket.

### Casket place

Uses player block position. Y<dimension.minY+2 ->minY+2; else Y>dimension.logicalHeight ->logicalHeight-1 (absolute comparison, not minY+logicalHeight). Starts one below then increments until canBeReplaced; no explicit upper-bound/search-length/LOS/permission/BreakEvent guard or collision safety check in TF loop. Reads fluid at destination via BlockLoggingEnum.getFromFluid and uses its native enum state. Casket damage from persisted CasketDamage else0; state BREAKAGE0..2. Facing from Direction.from2DDataValue(random.nextInt3). Random float<=.15: damage>=2 replaces with SkullChest using shared state, else increments casket damage. Native BlockState rejects out-of-range component value; no clamp in this path. setBlockAndUpdate false or unexpected missing/wrong BE logs and returns with casket already consumed, no inventory movement/refund at those failures. No fabricated placement/guaranteed success.

### Casket storage

On successful SkullChestBlockEntity destination (including Keepsake subclass), owner=Player ResolvableProfile iff config casketUUIDLocking, else null; pinned installed common config false. Stores custom name then45-slot inventory: reversed live armor4, four empty placeholders, offhand1, main inventory9..35 then hotbar0..8. Copies list references into NonNullList.of(EMPTY,45-array), clearing actual armor/offhand/items only after adding those references; resulting contents survive clear. Native fixed-size list clear fills EMPTY. Removes CasketDamage after successful transfer. Casket is world storage; no HP/SHP/DamageSource or health rescue, no XP capture. Native block entity saves contents/optional owner via codecs and native loot-table handling. No respawn auto-return of casket contents.

### Casket access

SkullChestBlockEntity45-slot GENERIC_9x5 menu. owner null uses ordinary container checks; owner nonnull allows owner OR permission>=3 to canOpen/stillValid, then native lock/distance checks. Source-proven different BreakEvent predicate: nonempty owned SkullChest cancels when (!permission3 OR !sameOwner), so only a permission3 owner passes that specific protection; ordinary owner and nonowner operator each fail. Empty/unowned chests bypass that TF cancel predicate. Native BreakEvent/protection rules remain. Both block types return explosion resistance Float.MAX_VALUE and canEntityDestroy=false, not absolute immunity to arbitrary world removal. On block replacement, native drops contents; ordinary server noncreative playerWillDestroy with doBlockDrops spawns separate block item modified by damage, while contents drop separately, not inside carried block item. Owner locking is not an HP defense.

### Casket repair

Keepsake BREAKAGE integer0..2. useItemOn only if multi-logged block AIR or fluid nonEMPTY; holding KeepingIII and damage>0 ->stack.consume1 native creative rules, setBlockAndUpdate damage-1 (return ignored), repair sound/sided result. No owner authorization or explicit server-only guard inside this repair branch; menu opening has separate native owner checks. Other admitted uses open menu on server; solid logged stone/obsidian/basalt returns default interaction. Drop/clone item carries CASKET_DAMAGE if>0; setPlacedBy directly sets component value default0, no extra clamp. No repair via Life/I/II, no HP healing. Multi-logging/native fluid behavior and ordinary container operations remain, not new custom damage.

### Curios native

Twilight common setup checks ModList curios then registers keepCurios listener and real item capability for five charms; installed data/curios/tags/item/charm.json lists all five. Actual native equipped-slot availability/eligibility remains. findAndConsumeCurio uses CuriosApi.getCuriosInventory->installed mixin capability lookup->handler.findFirstCurio(item), then if Optional present saves full pre-shrink stack into CharmStack and shrink1. Current installed Curios9.5.1 search uses real equipped stacks, not cosmetic, includes only active slots unless active-state list lacks entry, in handler slot order. It uses per-item same-gameTime cached SlotResult; TF does not re-test empty/count/item after Optional. Thus a same-tick cached emptied reference reaching save can throw native Cannot encode empty ItemStack; no runtime reproduction/fix or guaranteed repeated rescue claimed. Actual valid nonempty first-match consumption is legitimate positive path. Handler visibility is not an activation prerequisite.

### Curios keep

TF keepCurios on real DropRulesEvent: server Player plus contains CharmStack AND contains TFCharmInventory AND list nonempty. No charm-tier/type/just-consumed validation. Iterates handler.getSlots and adds identity predicates stack==handler.getEquippedCurios().getStackInSlot(i) ->ALWAYS_KEEP. Native getEquippedCurios combines ordinary stacks only; cosmetics are not the matched equipped objects. Actual Curios playerDrops HIGHEST LivingDropsEvent posts DropRules, scans ordinary and cosmetic slots, last matching override wins, ALWAYS_KEEP leaves stack instead of remove/drop/vanishing processing; default/other rule and server keepCurios config remain. Other listeners may add later overrides, no total modpack order claim. Native PlayerClone copies old retained Curios tag into new handler. Twilight does not copy Curios items into its own TFCharmInventory or casket.

### Curios tokens

Inventory Life uses saveItemToTag=false, while Curio Life unconditionally saves CharmStack through shared findAndConsumeCurio. Life cancellation does not clear that token or create TFCharmInventory. It can remain until later respawn; later nonempty tagged-gear/keeping storage can satisfy TF keepCurios even if token came from Life, because no type/freshness check. Conversely Keeping consumed but empty TFCharmInventory does not trigger accessory keep. Death/respawn packets/stat follow actual persisted keys, so Keep animation/stat may use saved Life stack. These are exact shared-state predicates, not assumed intended consumption semantics.

### Visual exclusion

SpawnCharmPacket is registered clientbound; packet/anonymous handler only item activation or client CharmEffect plus particles/sound. CharmEffect follows owner eye/orbit, expires tickCount>200 or owner dead/invisible, has empty save/sync bodies and no HP/hurt/source/retention call. It is visual, not a summon, shield, resurrection source or extra gameplay mechanic. Rendering config does not change resource/HP behavior.

## Packages

| Mechanic | Primary classification |
|---|---|
| Charms of Life native death veto and restoration | BINARY_MECHANIC |
| Keeping tiers native inventory transfer | CUSTOM_RESOURCE |
| Phantom armor and Tower Key native retention | CUSTOM_RESOURCE |
| Charm inventory persistence and respawn restoration | CUSTOM_RESOURCE |
| Keepsake Casket native death placement and storage | CUSTOM_RESOURCE |
| Casket access, break and native world protection | BINARY_MECHANIC |
| Casket damage component and KeepingIII repair | CUSTOM_RESOURCE |
| Twilight Charms native Curios consumption and retention bridge | CUSTOM_RESOURCE |

## Custom source callers

| Type | Amount | Source identity |
|---|---|---|

## Scope and exclusions

- Nine listed complete native bodies plus actual helper/bridge/registration methods are covered; no custom DamageType added.
- Selected Curios code proves Twilight dependency contract only; this does not start another catalog family or a runtime compatibility matrix.
- TierI empty varargs, full-inventory return loss, pre-placement casket consumption, mismatched break/open predicates and persistent Curio token/cache boundaries remain source-proven behavior without fixes.
- CharmEffect/packet visuals excluded as combat payloads; caskets preserve inventory, not HP/SHP/XP.
- Travellers, remaining utilities/food/passive entities/hazards10 custom types and complete ASM/compatibility/source closure remain pending; Twilight PARTIAL, zero promoted, REVIEW_REQUIRED0.

## Future native controls

- Genuine LifeI/II inventory and active Curio lethal hits with native Totem/event/tag eligibility controls.
- Actual Keeping tier slot matrix including empty-list I, charm-only contents, casket reserve and unconditional tagged gear.
- Real respawn/persistence with occupied/full slots and independent token/End-return controls.
- Native death casket placement/failure/layout/damage/ownership/repair and item/block lifecycle.
- Actual Curios consumption, drop override, clone, cosmetics/inactive/cache and shared-token boundaries.

[Semantic packages and paths](semantic-sections/twilightforest-charms.json), [integrity](twilightforest-charms-integrity.json), [full validation](r2f8n-charms-validation.json).

Exact next task: Continue Task C with Travellers gear/components/modifiers and their installed ASM/event control paths; then remaining utility/food, passive entities, environmental hazards and10 unfinished custom DamageTypes, complete nested ASM/compatibility/source exclusions before R2f8 and final Twilight promotion. IceAndFire only after COMPLETE Twilight pushed/live verified. No runtime boss/L2/Stage/production/fixes/Phase6/7.
