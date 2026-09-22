# r2f8q - TWILIGHT_TRAVELLERS_UTILITY_SEMANTIC_REVIEW_COMPLETE

Installed Twilight4.8.3345, its registered nested ASM, raw Minecraft1.21.1 and exact NeoForge21.1.244. Static research only, runtime0; no production/Stage/Phase6/7/L2/boss tests or fixes. Completes Travellers storage/view/cloth and declared Travellers item/event/logic/modifier contracts using protected R2f8o/p activation/recipes/physics. Other utilities, food, passive entities, hazards, ten DamageTypes and remaining ASM/compatibility remain unfinished. No new DamageType or direct HP/SHP payload in these five packages.

Adds 5 reviewed packages / 29 delivery cases. Twilight remains PARTIAL at 190/613 drafts, zero promoted. REVIEW_REQUIRED 0.

## Native contracts

### Authority

Installed Twilight4.8.3345, its registered nested ASM, raw Minecraft1.21.1 and exact NeoForge21.1.244. Static research only, runtime0; no production/Stage/Phase6/7/L2/boss tests or fixes. Completes Travellers storage/view/cloth and declared Travellers item/event/logic/modifier contracts using protected R2f8o/p activation/recipes/physics. Other utilities, food, passive entities, hazards, ten DamageTypes and remaining ASM/compatibility remain unfinished. No new DamageType or direct HP/SHP payload in these five packages.

### Belt

Native Belt properties supply SWAP_HOTBAR_ABILITY, CONTAINER built from nine EMPTY slots, and HAS_BELT; native ItemContainerContents.fromItems trims trailing empty slots and returns EMPTY when all empty, so logical belt capacity9 differs from current serialized getSlots. Genuine Wings+Belt shapeless modifier recipe transfers CONTAINER via protected TransferableComponentModifier and adds SWAP_HOTBAR_MODIFIER marker; copied Wings state persists. Real swap reads player.inventory.getArmor(LEGS.index), requires either swap modifier/ability PRESENT plus CONTAINER, then processes hotbar0..8. Missing stored indices use EMPTY. For each slot, current inventoryStack must canFitInsideContainerItems && !TRAVELLERS_BELT_BLACKLISTED && (active swap OR inventoryStack.isEmpty). Eligible slot stores that current stack and replaces inventory slot with stored stack; ineligible slot keeps stored stack. Rebuild CONTAINER from resulting nine slots; getStackInSlot returns a copy and fromItems copies stacks. Other inventory/offhand slots and selected index are not explicitly swapped. No HP, attack reset, cooldown, item-use action or source creation in helper.

### Belt inactive

hasSwapHotbar tests registry/marker presence, independently from isModifierActive. Broken or spectator-inactive gear can retrieve stored items into EMPTY hotbar slots (subject to empty-stack canFit/tag checks) while nonempty hotbar inputs cannot be deposited/swapped. Stored belt item itself is not rechecked against blacklist/canFit on retrieval; those predicates are on the hotbar input. Client hotbar key consumeClick uses presence+CONTAINER, sends empty SwapHotbarPacket; server handler uses ctx.player and current native helper, then ServerPlayer.broadcastToPlayer(self). No UUID target argument or client inventory prediction. Helper has no rate limit/cooldown. Changed sound uses ItemStack.equals, not isSameItemSameComponents; no gameplay gain inferred from that sound. Actual belt class stack overload canFitInsideContainerItems returns !has(CONTAINER), while noarg returnsfalse; native stack extension calls the stack-aware item hook. Gear with stored container is therefore excluded from native nested-container insertion where that hook is respected. No packaged belt blacklist file exists; tag remains extensible.

### Display storage

ITEM_DISPLAY is a persistent/network component containing six logical positions: MAP,MAP,MAP,COMPASS,CLOCK,MOON_DIAL. Valid MAP means instanceof MapItem; others exact COMPASS/CLOCK/TF MOON_DIAL. Native mutable copy deep-copies stacks into six slots. Genuine Goggles secondary-click handlers require count1 and ITEM_DISPLAY component; on-slot variant also requires slot.allowModification(player). They do not require active/worn/not-broken gear for storage editing. Input must canFitInsideContainerItems; find first matching EMPTY slot, otherwise first matching slot; matching occupied item+components rejects. Split exactly1 into chosen slot. If empty target, set source remainder; if occupied, replace source with displaced item and giveOrDrop input remainder. No transaction rollback if SlotAccess.set returnsfalse; native slot/cursor admission remains. Removal takes first nonempty item accepted by destination slot.mayPlace (or any for cursor); destination uses safeInsert. Sounds are cosmetic. Grindstone return/removal and overflow are protected R2f8o, not another package.

### Display state

Chosen map starts0. Inserting into an empty map slot resets selection only when no other map exists. cycleChosenMapSlot scans forward from chosen+1 for next nonempty MAP position, then sets -1; next cycle from -1 starts0, so the sequence includes a disabled gap rather than immediate wrap. Removing selected map cycles before clearing it. CycleMapSlotPacket acts only ServerPlayer, actual HEAD component with active ITEM_DISPLAY, and contents !isEmpty; if selection changed writes new component, marks inventory changed and plays selected/empty sound. isEmpty means items-list length0, not all entries EMPTY; default six-slot EMPTY returnsfalse, but payload code checks actual stack emptiness. Persistent codec stores only nonempty indexed slots plus chosen_map_slot; fromSlots rebuilds maxIndex+1, or returns shared six-slot EMPTY with chosen0 when no saved slots, so an all-empty chosen-1 resets0 on load. Network codec copies whole items list+index. Native recipes produce valid layouts; codecs do not independently enforce all six-slot/index invariants.

### Display map

TravellersGogglesItem.inventoryTick runs map payload only slotId==36+HEAD.index (39 for native Player Inventory), server side and active current HEAD ITEM_DISPLAY. Nonnull contents, chosen index!=-1, nonempty chosen MapItem: invoke its real virtual inventoryTick(map,level,entity,slot,true), then if ServerPlayer send that MapItem.getUpdatePacket when nonnull. Native MapItem resolves actual saved data, calls tickCarriedBy, updates terrain only when !locked and selected/offhand; the passed true satisfies selected path but does not bypass saved-data/locked/map rules. Other stored items do not get a general inventoryTick loop, consumption, effect application or combat proc. Magic/Maze map subclass bodies remain later map-utility scope; invoking real polymorphic tick is not evidence that their entire mechanics are closed.

### Display map asm

Installed UpdateMapsInGogglesTransformer targets MapItemSavedData.tickCarriedBy(Player,ItemStack), after EVERY Inventory.contains(Predicate) call. Hook preservestrue; otherwise original method Player argument current HEAD must have active ITEM_DISPLAY, contents, chosen>=0, nonempty chosen map and ItemStack.isSameItemSameComponents(argumentMap,chosenMap). No upper-index bounds check is added by hook. Transformer loads locals2(mapStack) and1(original method player) at BOTH native contains sites. The second native site is a carriedBy entry player inventory check, but false fallback still checks ORIGINAL method player goggles, not that entry player. Thus an eligible original caller can keep other preexisting, not-removed tracked players through that membership branch; native same-dimension/trackingPosition/framed rules still control decoration. This is a source-proven identity boundary, not a fabricated map or runtime verification.

### Display hud

HUD renderer requires Player, no debug overlay, !hideGui, active HEAD modifier and component. It checks each stored type validity, displays only chosen map plus compass/clock/moon. Map reads actual saved map data/id and renders it; does not reveal arbitrary entities or write HP. Compass shows tracked lodestone coordinates/Manhattan distance only with present target in same dimension, otherwise player coordinates. Clock uses natural dimension and fixedTime-or-dayTime with +6000 modulo24000 converted to display time; nonnatural unknown. MoonDial uses native moon phase/natural dimension, nonnatural unknown (April1 text alternate). These are informational utilities, no time/phase change or status buff. Config changes overlay placement/scale/format only. Standalone MoonDial tooltip has same read-only phase behavior.

### Zoom

Builtin Goggles component zoom=.3. Client ComputeFovModifierEvent: keyDown AND !player.isScoping, current HEAD active ZOOM_ABILITY and nonnull value ->multiply event current newFov by.3. On state change store IS_USING_GOGGLES_ZOOM_MODIFIER, sound and send GogglesZoomPacket(bool,UUID). Server bidirectional handler resolves UUID in sender level, requires target player exists and target current active ZOOM_ABILITY before changing state/sound/relay; no senderUUID equality check. Client handler sets flag directly. FOV eligibility is recomputed from actual local input/equipment, not solely received flag. No server accuracy/reach/projectile change. Flag serializes/syncs defaultfalse, no copyOnDeath; item armor texture uses flag for lowered-goggles visual even without another active check. Failed server change (including inactive target) does not forcibly clear stored flag in this packet handler.

### Zoom mouse

CalculatePlayerTurnEvent adjustment requires !cinematicCamera, local Player, HEAD zoom component nonnull and zoom key held&&!isScoping. It DOES NOT check isModifierActive, spectator or broken state. SetSensitivity=(.5-1/(6*s))*s/(zoom+.05) with actual float addition for zoom+.05. No guard/clamp in TF or native event setter for s0/zero denominator/nonfinite values. With s0 Java floating division/multiply yields NaN; retain exact unsimplified formula. Native MouseHandler then computes (newSensitivity*.6F+.2F)^3 and ordinary turn scaling. Therefore broken gear can still change mouse sensitivity while FOV zoom is denied. This is native input behavior, no aim-assist/attack multiplier or patch.

### Red thread

Native RedThreadRenderer selects glow when Player holding RED_THREAD item in either hand OR (TRAVELLERS_GOGGLES_RED_THREAD_VISION state && active HEAD modifier). Glow uses depth-test ALWAYS(519) and fullbright15728880 for actual block faces; ordinary view uses cutout/light. Existing native block-entity distance/frustum/loading rules remain: this is marked-thread visibility, not global entity/ore revelation or a server target change. Client key toggle only with active modifier flips local attachment; no custom packet in that handler. Attachment defaulttrue serialized, and the sole explicit Travellers death-copy entry is RED_THREAD_VISION when old holder has data. No native sync declaration for that attachment; do not infer a client-toggle packet persistence guarantee. RedThread block itself is ordinary multiface placement/replacement and block entity, with no combat damage/status tick.

### Cloth acquire

EmperorsClothRecipe requires exactly one cloth ingredient slot and one other nonempty tag-applicable item, no crafting remainder and no existing cloth component; width*height>=2. Assembly copies item and sets persistent/network UNIT EMPERORS_CLOTH. Packaged applicable tag #c:armors plus ELYTRA. Packaged no_template_smithing alternative requires empty template, tag base, cloth addition and none of added component types already present; copies base and applies component. Native recipe/menu consumption remains. These source routes preserve original item attributes/enchantments/durability, not a replacement armor item. Existing cloth removal uses uncanceled RightClickBlock on WATER_CAULDRON level>0, lowers fill1, removes marker, awards CLEAN_ARMOR and cancels SUCCESS; no explicit server-only/creative-refund branch, no cloth item returned.

### Cloth visibility

ArmorVisibilityRenderingTransformer targets LivingEntity.getVisibilityPercent(Entity) before FIRST FSTORE local4, after native getArmorCoverPercentage in INVISIBLE branch. Exact installed target/slot is pinned. ArmorHooks subtracts ArmorUtil shrouded fraction: count nonempty armor slots with component / count ALL iterated armor slots (including empty); native coverage is nonempty/all. Result is unshrouded nonempty/all. Native clamp minimum.1 then multiplier .7*coverage, with earlier discrete factor.8, native matching skull factor.5 and CommonHooks.getEntityVisibilityMultiplier afterward. Four normal player armor slots all shrouded ->invisible visibility .07 (or .056 discrete) before other factors/hooks. If not invisible, this injected branch is not reached: cloth itself does not grant Invisibility. No active/broken/spectator check in cloth count. Native TargetingConditions only applies visibility when testInvisible and range>0; effective range=max(range*visibility,2), then native line-of-sight/attack/allied/selector rules. No universal aggro reset, guaranteed untargetability or damage immunity.

### Cloth render

CancelArmorRenderingTransformer targets exact NeoForge extended HumanoidArmorLayer.renderArmorPiece(...FFFFFF) after first INSTANCEOF, loading local13 ItemStack. Hook turns true ArmorItem predicate false when component present, skipping native humanoid armor/trim/glint draw. First-person TF gloves independently skip their overlay when cloth present. FixCapeUnrenderingTransformer targets CapeLayer.render after first ItemStack.is(Item) ELYTRA check, using local12 stack; component makes checkfalse so ordinary cape may render if other native visibility/skin/model gates pass. No installed TF cloth hook changes ElytraLayer.shouldRender: exact native method still accepts ELYTRA, so cloth on Elytra does NOT prove wing model hidden by the humanoid hook. Render hooks do not remove item attributes/enchantments, native armor/protection, durability or flight; no damage event/source mutation.

### Persistence sources

Storage/cloth/zoom components carry native item persistent/network codecs; normal copies, recipe transfer and death inventory rules remain. Native display remainder helper uses inventory.add then targeted no-pickup-delay dropped remainder if needed; no item duplication is assumed from cosmetic fake pickup branch. All paths use real armor inventory/callbacks, not Curios scans; general external equipment hooks remain conditional. Installed admin /twilightforest travellers_gear add/remove uses permission2, real non-Fake Player main-hand TravellersModifiable, disallows ability modification; add additionally enforces slot cap, absent modifier and matching equipment group. Remove calls native modifier removal without grindstone item-return helper, so stored payload removal differs. Record admin provenance separately; ordinary future fixtures should use genuine crafting/equipment. No command executed. Recipe-view adapters/tooltips/models are discovery/presentation, not independent combat payloads. Source-specific external compatibility NONE_PROVEN here; generic native/loader hooks are present, no pack-wide absence certification.

## Packages

| Mechanic | Primary classification |
|---|---|
| Travellers nine-slot hotbar storage exchange | CUSTOM_RESOURCE |
| Travellers stored display and actual map ticking | CUSTOM_RESOURCE |
| Travellers zoom and mouse input state | CUSTOM_CONTROL |
| Travellers marked-thread visibility | BINARY_MECHANIC |
| Emperor cloth native armor visibility | CUSTOM_CONTROL |

## Custom source callers

| Type | Amount | Source identity |
|---|---|---|

## Scope and exclusions

- All listed Travellers storage/view classes, both complete Travellers event classes, relevant command source, display renderers and four nested armor/map transformers are pinned. Other preexisting core/movement semantics reused.
- HUD/tooltip/MoonDial/wing/goggle texture outputs are informational/cosmetic; no new effects or DamageTypes inferred from names. RedThread affects actual marked-block depth rendering only.
- Cloth does not apply Invisibility, erase attributes or force Elytra wings invisible. Native targeting and generic visibility hooks remain.
- Map goggles call actual subclass methods; complete Magic/Maze map utilities and landmark-map ASM remain unfinished. Remaining other items/food/passive entities/hazards and ten custom sources are still unfinished.
- Administrative add/remove and recipe-view adapters are separate source provenance, not fabricated survival fixtures. No commands or runtime tests performed.

## Future native controls

- Genuine Belt/transfer recipe and all nine hotbar inputs, native save/overflow/nesting and broken-state retrieval.
- Native display insertion/replacement/removal/cycle plus real selected map tick and both carrier membership call sites.
- Local input/equipment FOV/mouse and legitimate packet state with nonfinite/broken/spyglass/cinematic controls.
- Real red thread held/equipped visibility, native render limits and actual attachment lifetime.
- Native cloth crafting/smithing/wash; genuine Invisibility vsvisible target admission, real armor and Elytra/cape render controls without defense changes.

[Semantic packages and paths](semantic-sections/twilightforest-travellers-utility.json), [integrity](twilightforest-travellers-utility-integrity.json), [full validation](r2f8q-travellers-utility-validation.json).

Exact next task: Review remaining utility/map/food/flask and passive-entity contracts, then environmental hazards and ten unfinished custom DamageTypes; complete remaining installed ASM/compatibility/source exclusions, protect R2f8 and promote full Twilight COMPLETE. IceAndFire begins only after COMPLETE pushed/live verified. No runtime boss/L2/Stage/production/Phase6/7.
