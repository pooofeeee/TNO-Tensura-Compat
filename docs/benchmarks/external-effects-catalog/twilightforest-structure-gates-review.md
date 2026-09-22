# r2f8z - TWILIGHT_STRUCTURE_GATES_SEMANTIC_REVIEW_COMPLETE

DIRECT_SOURCE_SPECIFIC: optional gravestone:gravestone tag exemption is a real direct resource mapping, conditional on that registry entry existing; installed Twilight progression listeners match its native progression structures/pieces, tags, player advancement and Kobold exclusion. GENERIC_CONDITIONAL_PRESENT: exact loader RightClick/Break/MultiPlace/IncomingDamage/entity-add hooks, native mining attributes and native criterion predicates. These are real conditional hooks, not evidence that every pack mod cancels, bypasses or augments them. NONE_PROVEN: this inspected barrier/hint logic has no source-specific Tensura/L2 or Curios mapping. UNKNOWN: pack-wide cross-mod outcomes and untested runtime ordering. No runtime compatibility claim from static absence.

Adds 6 reviewed packages / 28 delivery cases. Twilight remains PARTIAL at 253/876 drafts, zero promoted. REVIEW_REQUIRED 0.

## Native contracts

### Authority

Installed TF4.8.3345 with exact Minecraft1.21.1/NeoForge21.1.244, static evidence only. Terrain shields, advancement admission and actual HP damage remain distinct. No new DamageType, direct HP subtraction, runtime fixture execution, production/Stage/L2/Phase6/7 change. All40 custom types already resolved in protected Y; whole Twilight remains PARTIAL pending portal/control blocks, other events/ASM/source/compatibility closure and final promotion.

### Area gate

Registered ProgressionEvents callbacks call isAreaProtected: server level, player not instabuild, not spectator, not FakePlayer, tfEnforcedProgression true, actual located structure start, at least one containing piece whose isPieceProtected is true, actual structure instanceof ProgressionStructure and player missing required advancement. No conquered-state test, DamageType/tag bypass, boss HP or item ownership test. Gamerule is registered defaulttrue; actual world value is not statically assumed. Native PlayerHelper first-entry-only advancement behavior is reused; installed structure lists each have one entry.

### Landmark lookup

LandmarkUtil locateNearestLandmarkStart uses the actual LANDMARK structure tag, legacy nearest-center XZ from supplied chunk coordinates, then center chunk STRUCTURE_STARTS and first matching tagged start. Default readiness check returns empty if that center chunk is not loaded; missing registry/tag/start is empty. It is not an unrestricted nearest bounding-box search. Area admission uses uninflated containing piece bounds; the attack position is victim.blockPosition. Default isPieceProtected is true unless the piece implements ProgressionPiece and returns false.

### Piece exceptions

Installed method census resolves six false overrides: StrongholdAccessChamber, StrongholdUpperAscender, StrongholdUpperLeftTurn, StrongholdUpperRightTurn, StrongholdUpperCorridor and StrongholdUpperTIntersection components. Other actual ProgressionPiece default is true. Access chamber pedestal can therefore be used before the deeper Stronghold advancement; overlapping containing protected pieces can still satisfy anyMatch. Native structure records, pieces and player advancements persist normally; this event gate stores no per-victim invulnerability flag.

### Block actions

BreakEvent server/notcanceled requires block NOT in twilightforest:progression_allow_breaking and area gate, then cancels. EntityMultiPlaceEvent server/Player/notcanceled applies the same break-tag/area tests to replaced snapshots, cancels and resyncs inventory on first protected snapshot. The listener named preventLockedAreaBlockPlacing actually receives every RightClickBlock: server/notcanceled plus area gate cancels and resyncs inventory, without requiring a BlockItem, attempted placement or banned-interaction tag. Installed break allow-tag includes skull_chest, keepsake_casket and optional gravestone:gravestone; banned-interaction tag includes lever, antibuilder, buttons and c:chests. Separate RightClickBlock banned-interaction listener sets UseBlock FALSE for tagged blocks in protected area; earlier full event cancellation is broader and normal event dispatch may skip canceled events. Do not turn the break allow-tag into an all-interaction exemption.

### Incoming damage

LivingIncomingDamageEvent listener requires server Living victim implementing Enemy, source.getEntity() instanceof Player (causing entity, not direct entity), victim not Kobold and area gate at victim block position. It cancels the event, making native LivingEntity.hurt return false before block/armor/damage processing. Real player-owned projectiles can qualify; ownerless sources, mob-caused sources, PVP/non-Enemy victims, Kobolds and exempt players do not satisfy this listener. No source rewrite, reflection, new damage, shield count or direct HP operation. Other native admission/defense/loader listeners remain, including on paths this listener does not cancel.

### Feedback

On positive area gate, containing-piece boxes are sent via AreaProtectionPacket to players within64 and real hint production is attempted; this happens even though the player action/damage is subsequently denied. Registered PlayerTick.Post every100 with progression enabled sends locked-structure display using broader AdvancementLockedStructure interface: protected pieces inflated4 for display, unprotected pieces unchanged. Present unlocked start or creative/spectator sends clear; absent start returnsfalse without clear. These packets/render bounds do not expand real protection or create damage. Protected Y biome enforcement at20 ticks is unchanged; portal branch still pending.

### Hint sources

Two genuine callers feed StructureHints: protected action/attack denial at attempted position, and protected Y biome enforcement optional hint_structure via registry lookup. ProgressionStructure holds lastSpawnedHintMonsterTime on the structure registry object, not player, structure start or separate dimension key; initial0 and no serialization. World time below storedtime resets0. Only strict currentTime-last>1200 attempts up to20 times, stops and sets timestamp on first didSpawnHintMonster true; failed attempts do not reset cooldown. First possible attempt from initialstate is worldtime1201, not immediate.

### Hint delivery

Each attempt uses X/Z difference of two nextInt16 (-15..15) and Y difference of two nextInt4 (-3..3) relative to supplied position. Optional configured EntityType.create returns Mob or null; moves to position, then checkSpawnObstruction and sensing.hasLineOfSight(player). Nonempty configured hint item is copied with components into MAINHAND, dropchance1; world.addFreshEntity return is discarded, then method returns true. Thus add-veto can still advance cooldown. No finalizeSpawn call, normal spawn-rule/light test, owner/tame/team assignment or explicit persistenceRequired. Native entity add hooks and native book/equipment drop admission remain. Existing Kobold combat package is reused, not a duplicate new attack.

### Hint configuration

All10 installed hint-configured structure resources specify actual twilightforest:kobold: aurora_palace requires progress_yeti; dark_tower progress_knights; final_castle progress_troll; giant_house/troll_cave progress_merge; hydra_lair progress_labyrinth; knight_stronghold progress_trophy_pedestal; labyrinth/yeti_cave progress_lich; lich_tower progress_naga. Each required list has one entry. HintConfig.checkCastMob literally uses entityType.getBaseClass().isAssignableFrom(Mob.class); exact loader EntityType.getBaseClass returns Entity.class, so this check is not independent subclass proof. Installed actual factories are Kobold. Default generated written-book content has generation3/resolvedtrue/translatable pages; item contents are not damage. ProgressionWrappedStructure delegates generation/settings to wrapped structure and retains progression interfaces, not a new attacker.

### Stronghold shield

StrongholdShieldBlock is a terrain barrier, not the Lich entity shield. Default FACING DOWN, placement nearestLookingDirection with vertical opposite. Properties hardness-1/resistance6000000/no loot/requires correct tool/piston BLOCK; canEntityDestroy false. getDestroyProgress ray traces from player eye/view with BLOCK_INTERACTION_RANGE+1, OUTLINE and FluidNONE. It compares only hit direction to FACING when vertical, otherwise FACING.opposite; no explicit hit-position equality or hit-type check. On matching side returns native player.getDigSpeed(STONE,pos)/1.5/100. Other side uses native parent hardness-1 =>0 normal mining progress. Native mining/equipment/interaction and progression events still apply; creative native destruction path is distinct from ordinary progress. No contact hurt, HP damage, reflect or owner requirement.

### Shield producers

Exact caller evidence records real structure placements, including StrongholdAccessChamber postProcess placing default Trophy Pedestal and a5x5 Stronghold Shield floor; Stronghold wall generation uses actual face states. Pedestal removal is a separate native terrain path. Force-field producers are actual Final Castle structure methods recorded in source-providers evidence; no speculative player damage from visual barrier names.

### Pedestal activation

TrophyPedestal default ACTIVEfalse/WATERLOGGEDfalse; placement detects native water and update schedules water tick. neighborChanged first updates comparator, then server+inactive+above block in TROPHY_PEDESTAL_ACTIVATION_BLOCKS. With progression enabled, any eligible nearby Player permits doPedestalEffect; all ineligible nearby players receive warning. Eligibility is progress_lich OR instabuild. Native getEntitiesOfClass default excludes spectators, within AABB(blockpos).inflate16. With gamerule disabled no nearby eligible player required. Native installed activation tag has8 ground boss trophies (Naga,Lich,Minoshroom,Hydra,Knight,Ur,Alpha,Snow); no default wall/QuestRam trophy member. Ordinary neighbor trigger and tag membership are required, not manual direct helper execution.

### Pedestal effect

doPedestalEffect first writes ACTIVEtrue, then traverses inclusive offsets-5..5 in all3 axes and destroys only exact STRONGHOLD_SHIELD without drops, then plays sound. It does not consume the trophy, damage entities, clear all force fields or emit a player BreakEvent itself. State-write/destroy returns are discarded. No automatic deactivation on trophy removal. Inactive destroyProgress returns-1 and piston BLOCK; active uses parent hardness2/resistance2000 and piston NORMAL. Comparator returns above real TrophyBlock comparatorValue, otherwise0; tag extension alone does not create a comparator value. Block state persists via native chunk data.

### Pedestal reward

After the server inactive+trophy branch, rewardNearbyPlayers executes regardless of whether player eligibility allowed shield removal. All nearby native-query ServerPlayers receive PLACED_TROPHY_ON_PEDESTAL trigger and TROPHY_PEDESTALS_ACTIVATED stat request. With failed activation, repeated neighbor changes can repeat stat/criterion requests. SimpleAdvancementTrigger invokes native listener processing with true custom test; native listener/player predicates still apply. Actual progress_trophy_pedestal resource requires BOTH trophy_pedestal criterion (placed_on_trophy_pedestal) AND kill_lich tick criterion checking progress_lich. An ineligible player can bank the trophy criterion/stat but does NOT thereby complete the advancement or unlock deeper Stronghold. No separate owner/player who placed trophy test.

### Force field

All5 force-field colors use hardness-1/resistance3600000.8/light2/noLoot/noOcclusion/pistonBLOCK, with canEntityDestroyfalse. They do NOT set noCollision: native collision follows getShape, consisting of central cube7/16..9/16, enabled direction arms and qualifying corner planes. No entityInside/hurt/HP/projectile reflect/owner admission. This is physical terrain collision; entity behavior outside its shape is native. Different colors are distinct blocks for direct same-block connection, while any ForceFieldBlock can participate in the corner helper.

### Force connections

Default6 direction bits false and WATERLOGGEDfalse. canConnectTo accepts same exact field block; otherwise counts better connections (adjacent sameblock at placement/nullstate; existing true bits on update) and refuses solid-face connection when count>=3; else requires not native isExceptionForConnection and neighbor face sturdy. Placement forces opposite clicked face true and clicked face true unless secondary use; other directions use canConnectTo(null). Corner helper requires both adjacent direction bits plus sturdy opposite neighbor face or another ForceField whose corresponding bit is true. updateShape schedules water if already waterlogged and sets a direction true if now connectable, but returns unchanged state on failure; it never clears a stale connection bit. Placement does not read fluid, despite waterlogging interface; later native waterlogging and native state save remain. Rotation/mirror permute bits normally.

### Compatibility

DIRECT_SOURCE_SPECIFIC: optional gravestone:gravestone tag exemption is a real direct resource mapping, conditional on that registry entry existing; installed Twilight progression listeners match its native progression structures/pieces, tags, player advancement and Kobold exclusion. GENERIC_CONDITIONAL_PRESENT: exact loader RightClick/Break/MultiPlace/IncomingDamage/entity-add hooks, native mining attributes and native criterion predicates. These are real conditional hooks, not evidence that every pack mod cancels, bypasses or augments them. NONE_PROVEN: this inspected barrier/hint logic has no source-specific Tensura/L2 or Curios mapping. UNKNOWN: pack-wide cross-mod outcomes and untested runtime ordering. No runtime compatibility claim from static absence.

## Packages

| Mechanic | Primary classification |
|---|---|
| Progression structure player action gate | BINARY_MECHANIC |
| Progression structure hostile damage gate | BINARY_MECHANIC |
| Progression native hint Kobold production | CUSTOM_RESOURCE |
| Stronghold Shield directional mining gate | BINARY_MECHANIC |
| Trophy Pedestal shield removal and progression credit | CUSTOM_CONTROL |
| Force Field conditional terrain geometry | CUSTOM_CONTROL |

## Custom source callers

| Type | Amount | Source identity |
|---|---|---|

## Scope and exclusions

- Lich entity shields and actual HP damage are protected separately; Stronghold Shield and Force Field here are terrain.
- Biome consumers/first-entry advancement behavior and Kobold attacks reused unchanged; no duplicate mechanic.
- Display packets, hint-book prose and comparator values are not damage or larger protection bounds.
- Portal creation/transport, vanishing blocks/Castle Doors and remaining callback/ASM/compatibility closure remain ordinary unfinished work, not REVIEW_REQUIRED.

## Future native controls

- Native mining/right-click/multi-place and actual player-caused Enemy damage versus exemptions/pieces/Kobold/sourceowner controls.
- Real hint attempts through both callers, strict/shared cooldown, obstruction/LOS, add veto and native copied book drop.
- Stronghold Shield directional mining with real tools/attributes/events and pedestal removal as distinct terrain mechanism.
- Pedestal eligible/ineligible/creative/gamerule controls, criterion credit versus full advancement and persistent active terrain state.
- Five Force Field colors with genuine placement/update/water/corner/collision controls.

[Semantic packages and paths](semantic-sections/twilightforest-structure-gates.json), [integrity](twilightforest-structure-gates-integrity.json), [full validation](r2f8z-structure-gates-validation.json).

Exact next task: Continue native vanishing/reappearing/locked blocks and Castle Doors, then portal/control blocks and remaining events/nested ASM/compatibility/source exclusions. All40 DamageTypes closed; whole Twilight PARTIAL until complete source closure and final dedup/promotion. IceAndFire only after live-verified Twilight COMPLETE. Static only.
