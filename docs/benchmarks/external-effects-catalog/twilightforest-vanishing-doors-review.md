# r2f8aa - TWILIGHT_VANISHING_DOORS_SEMANTIC_REVIEW_COMPLETE

DIRECT_SOURCE_SPECIFIC: native key/type/state and actual Twilight structure producers; kept_on_death tag reuses protected native item-retention hook. MuseumCurator key listing is direct presentation metadata only. GENERIC_CONDITIONAL_PRESENT: exact loader RightClickBlock/UseBlock/UseItem and native criteria, block updates/collision/scheduling; protected progression gate can cancel actual interaction. NONE_PROVEN: no source-specific Tensura/L2/Curios combat mapping in these state-machine bodies. UNKNOWN: pack-wide callback alterations and actual runtime scheduling; static review does not certify compatibility.

Adds 4 reviewed packages / 24 delivery cases. Twilight remains PARTIAL at 257/900 drafts, zero promoted. REVIEW_REQUIRED 0.

## Native contracts

### Authority

Exact installed Twilight4.8.3345 plus native1.21.1/NeoForge21.1.244. Four complete barrier classes, actual structure/key producers and native interaction ordering. Static only; no runtime, HP/source invention, production/Stage/L2/Phase6/7 change. Whole Twilight remains PARTIAL pending portal/control blocks, remaining events/ASM/compatibility/source closure and final assembly.

### Vanishing initial

VanishingBlock default ACTIVEfalse, no VANISHED property. ReappearingBlock adds VANISHEDfalse; LockedVanishing adds LOCKEDtrue. Genuine useWithoutItem on visible/inactive block: bounded lock search true plays locked sound, false activates; returns sidedSuccess in both branches. Already active/vanished returnsPASS. Server neighborChanged starts visible/inactive powered block only when bounded lock search false. Native RightClickBlock and default-interaction admission remain, including protected Z structure gate. This is block interaction, not a damage-source hit.

### Lock search

areBlocksLocked uses FIFO queue starting at position and a checked set, with at most512 queue POP iterations. On every popped position, exact LOCKED_VANISHING_BLOCK with LOCKEDtrue returns true. Then mark checked; only VanishingBlock instances expand six neighbors not already checked. Enqueued positions need not be vanishing blocks; duplicate queued positions are possible because membership is tested against checked, not queued. Thus512 is not a count of512 unique connected blocks or an unlimited component proof. No block-owner/player-key/advancement predicate inside search.

### Activation

Private activate reads actual state, accepts any VanishingBlock subclass visible/inactive, writes ACTIVEtrue, schedules that actual block at2+nextInt5 (2..6 ticks). It does NOT test areBlocksLocked or LOCKED. Visible active server tick: if VANISHED property exists, set ACTIVEfalse/VANISHEDtrue and schedule80; otherwise removeBlock(pos,false) with no drops. Then activate each of six neighbors. Propagation does not repeat initial network-lock check and can activate a LOCKEDtrue block reached after the initial bounded search or after changed state; this is the installed chain, not an authorized bypass implementation. State/write/remove returns ignored. No BreakEvent or canEntityDestroy test in this callback itself.

### Reappearance

Reappearing block at vanished/inactive scheduled tick after80: sound, ACTIVEtrue, schedule15. At next vanished/active tick: VANISHEDfalse/ACTIVEfalse, reappear sound. Nominal vanished interval95ticks after original disappearance, apart from native scheduling/chunk delays. Vanished shape is central6/16..10/16 outline but collision empty; visible state uses parent collision. Native active/vanished block states and scheduled ticks persist through normal chunk save; no custom BE/owner/timer NBT. Reappearing visible/inactive can start again. Reappearance does not explicitly hurt, relocate or push overlapping entities; subsequent native collision/inside-block handling remains separate.

### Vanishing defenses

Ordinary Vanishing/Reappearing registered hardness10/resistance35, pistonBLOCK; Reappearing forceSolidOn/light4/requires correct tool, ordinary Vanishing light4 onlyACTIVE. UnbreakableVanishing reuses class/properties with hardness-1/resistance6000000/no loot. Vanishing getExplosionResistance returns6000 whenever !ACTIVE, otherwise parent value. Consequently inactive UnbreakableVanishing also reports6000 through this override, while active parent6000000 applies. Vanishing canEntityDestroy when !ACTIVE returns !areBlocksLocked; active delegates parent. These native entity-destruction/explosion predicates do not prevent the class own removal callback. No entity HP shield, fire/effect or projectile reflection.

### Locked defenses

Locked variant registered hardness-1/resistance2000/pistonBLOCK. LOCKEDtrue explosion resistance6000000 regardlessACTIVE and canEntityDestroyfalse; unlocked delegates Vanishing, giving inactive6000 and active parent2000. Unlock does not alter registered mining hardness-1, so it is not a ordinary-mining unlock. Actual chain removal still follows inherited tick. LOCKED state is native saved block state, no specific key identity or owner stored.

### Key interaction

LockedVanishingBlock.useItemOn requires stack nonempty, exact TOWER_KEY and LOCKEDtrue. Server body shrinks1 first, writes LOCKEDfalse, plays sound; ignores write success and returns sidedSuccess. No local instabuild/infinite-material exemption. Exact native ServerPlayerGameMode invokes blockstate.useItemOn before ItemStack.useOn; consumed block result returns immediately through ITEM_USED_ON_BLOCK criterion. Its creative ItemStack.useOn count restoration is later and does NOT refund this successful block callback. Thus native creative unlock also consumes one key. Wrong/empty key or already unlocked goes parent/default interaction path. Unlock does not call activate itself; normal subsequent interactions/neighbor redstone updates can start the chain. Existing protected structure RightClickBlock veto can prevent entry.

### Key source

TOWER_KEY is ordinary fireResistant/uncommon Item, no custom item damage behavior. Native darktower_key chest loot has a separate unconditional one-roll pool containing one tower_key, in addition to other loot. DarkTowerMain.addChildren, when !placedKeys and generation depth<2, chooses up to4 distinct size9 same-generation-depth wing candidates without replacement, marks keyTowertrue, warns/stops if exhausted, and sets transient placedKeys even if fewer; that field is not serialized by the class. DarkTowerWing serializes keyTower; its native treasure-room method selects DARKTOWER_KEY when true and otherwise DARKTOWER_CACHE. This is a genuine loot producer, not a manually injected key. Existing protected kept_on_death tag handling also includes tower_key; reuse that mechanic without duplication. MuseumCurator artifact resource lists key but does not confer combat behavior.

### Castle initial

All4 CastleDoor colors default ACTIVEfalse/VANISHEDfalse, where property name is vanish (different from VanishingBlock vanished). isBlockLocked is literalfalse in installed code. No native key, advancement or completed-boss requirement in this helper. useWithoutItem calls onActivation: vanished/active returnsFAIL; otherwise changeToActiveBlock and SUCCESS. Dead locked branch would PASS but is unreachable with this helper. neighborChanged calls activation when changed neighbor block is NOT CastleDoorBlock and current redstone powered; no explicit side guard in that body. Native outer interaction/progression gate still applies independently.

### Castle cycle

changeToActiveBlock sets ACTIVEtrue for CastleDoor state and schedules actual block2+nextInt5. Visible/active tick writes VANISHEDtrue/ACTIVEfalse, schedules80, sounds/particles, then checks allsix neighbors. Any CastleDoor subclass/color visible/inactive and helper-unlocked is activated; no same-color restriction. Vanished/inactive tick invokes same2..6tick activation helper; vanished/active tick restores bothfalse. Nominal vanished interval82..86ticks after disappearance, not the ReappearingBlock95. Initial disappearance also waits2..6. Each state-write return ignored. CastleDoor schedule callbacks do not remove the block or consume resources.

### Castle geometry

CastleDoor vanished collision empty and outline.375..625cube; visible parent collision. Occlusion shape is parent only when visible AND active, otherwiseempty, which does not imply empty collision. Registered hardness100/resistance100, requires correct tool, forceSolidOn, pistonBLOCK. Skip-render behavior connects allCastleDoor colors with equal vanished state. Sounds/ANNIHILATE particles are visual, not damage. Native saved states/scheduled ticks persist, no custom owner or HP. No explicit entity damage, effects, ignition, knockback, teleport, hurt-return dependence or entity displacement in these four classes.

### Source paths

Caller evidence ties Vanishing/Reappearing/Locked terrain to actual Dark Tower generation and CastleDoor colors to actual Final Castle generation; registered blocks also admit ordinary native placement where an item exists. UNBREAKABLE_VANISHING_BLOCK is BLOCKS.register with no associated item-registration wrapper; do not invent a normal survival placement item. Actual repeated chain callbacks are delivery paths distinct from manual/redstone entry. Resource/tag/loot data are pinned to installed JAR, not assumed from tooltip.

### Compatibility

DIRECT_SOURCE_SPECIFIC: native key/type/state and actual Twilight structure producers; kept_on_death tag reuses protected native item-retention hook. MuseumCurator key listing is direct presentation metadata only. GENERIC_CONDITIONAL_PRESENT: exact loader RightClickBlock/UseBlock/UseItem and native criteria, block updates/collision/scheduling; protected progression gate can cancel actual interaction. NONE_PROVEN: no source-specific Tensura/L2/Curios combat mapping in these state-machine bodies. UNKNOWN: pack-wide callback alterations and actual runtime scheduling; static review does not certify compatibility.

## Packages

| Mechanic | Primary classification |
|---|---|
| Native Vanishing Block removal chain | CUSTOM_CONTROL |
| Native Reappearing Block collision cycle | CUSTOM_CONTROL |
| Tower Key native locked-barrier gate | BINARY_MECHANIC |
| Castle Door native collision cycle | CUSTOM_CONTROL |

## Custom source callers

| Type | Amount | Source identity |
|---|---|---|

## Scope and exclusions

- Terrain disappearance is not HP damage, armor bypass or source identity. No new DamageType.
- Castle Door is not a subclass of Vanishing Block; no inferred shared lock or95tick timing.
- Tower Key kept-on-death retention and protected progression event gate reused; no duplicate mechanic.
- Particles/sounds/MuseumCurator listings are presentation only. Remaining portal/control/events/ASM work is unfinished, not REVIEW_REQUIRED.

## Future native controls

- Real manual/redstone/chain Vanishing entries with bounded lock search, subclass and resistance controls.
- Reappearing95tick cycle with native scheduled ticks/collision/reload controls.
- Native key loot and actual block callback including creative cost, wrong key, event veto and state persistence.
- Four CastleDoor colors through genuine manual/redstone/chain with82..86tick vanished interval and native collision/save controls.

[Semantic packages and paths](semantic-sections/twilightforest-vanishing-doors.json), [integrity](twilightforest-vanishing-doors-integrity.json), [full validation](r2f8aa-vanishing-doors-validation.json).

Exact next task: Continue remaining native portal creation/transport and control blocks (Builder/Antibuilder/cloud/snow as applicable), then remaining events/nested ASM/compatibility/source exclusions. All40 custom types closed. Finish R2f8 and final Twilight promotion before IceAndFire. Static only.
