# r2f8k - TWILIGHT_UTILITY_PROJECTILES_SEMANTIC_REVIEW_COMPLETE

Installed TF4.8.3345, raw Minecraft1.21.1 and exact NeoForge21.1.244. Native item/dispenser/impact/terrain callbacks only. HP requests, actual HP, equipment, block replacement, motion and durability stay separate. Static research, no runtime/L2/Stage/production/fix. Protected nonbreaking durability, parry, source helpers and weapon-event predicates reused.

Adds 7 reviewed packages / 26 delivery cases. Twilight remains PARTIAL at 139/426 drafts, zero promoted. REVIEW_REQUIRED 0.

## Native contracts

### Authority

Installed TF4.8.3345, raw Minecraft1.21.1 and exact NeoForge21.1.244. Native item/dispenser/impact/terrain callbacks only. HP requests, actual HP, equipment, block replacement, motion and durability stay separate. Static research, no runtime/L2/Stage/production/fix. Protected nonbreaking durability, parry, source helpers and weapon-event predicates reused.

### Queen use

Moonworm Queen registered capacity256/setNoRepair; rejects ordinary enchanting and book enchanting. use fails fully damaged even creative; else starts72000-tick BOW use. Native release computes72000-useRemaining, requires server/useTime>12 (strictly13+)/damage+1<max, then addFreshEntity(MoonwormShot) must return true. Real Living shooter constructor uses speed1.5/inaccuracy1 and native shootFromRotation adds shooter motion. Only successful add plays squish and, Player&&!instabuild, protected nonbreaking cost2. No stat/cooldown/second source, no consumption on false add. One remaining charge cannot fire, including creative; direct placement can use it.

### Queen dispenser

RegistrationEvents init schedules TFDispenserBehaviors.init; its actual first anonymous behavior creates ownerless MoonwormShot at native dispenser position. DamageableStackDispenseBehavior requires maxDamage>=damage+getDamageAmount; Moonworm threshold2, but common execute requests wear1 with entity=null, independent of addFreshEntity return. shoot direction(X,Y+.1,Z), speed1.1/inaccuracy18. Item retained; genuine dispenser has no Player creative/Crown owner. Native helper still processes durability hooks/Unbreaking. Protected Twilight Scepter behavior shares helper with threshold1/inaccuracy6; its projectile package remains protected. No direct Player launcher equivalent inferred for dispenser source attribution.

### Moonworm collision

MoonwormShot registered .25x.25, nonfireproof; TFThrowable/ITFProjectile with native ThrowableProjectile collision, gravity float.03, air drag.99/water.8. Native Projectile.canHitEntity retains canBeHitByProjectile (normally alive and pickable) and shared-vehicle-until-left-owner gates; exact244 ProjectileImpactEvent can cancel before hitTargetOrDeflectSelf. Projectile native target deflection is separate. TF protected shield-parry route accepts ITFProjectile independent of parryNonTwilightAttacks, when no shield-parry mod and blocking within configured interval; deflect changes owner to blocker, event cancellation prevents current impact. Item not an arrow; ownerless dispenser/reflected ownership remain real native paths. isPickable=true/pickRadius1 but no hurt override: ordinary direct attack uses inherited Entity hurt, not LichBolt-style manual reflection. No custom age/expiry/NBT override; native owner/motion save remains.

### Moonworm head

onHitEntity after no-op super: if Player && !hasItemInSlot(HEAD), sets HEAD=new Moonworm block item and returns. No hurt/source/HP/Resistance/armor check, team/consent/creative gate, or random draw inside this branch; native collision/event gates still apply. Existing helmet prevents branch. No overwrite of occupied slot; callback adds no armor/status modifier. Outer onHit still broadcasts particles/discards server-side after super dispatch, so successful equip consumes projectile. Administrative/creative spectator collision eligibility is inherited, not bypassed.

### Moonworm damage

Other entity impact calls hurt(twilightforest:moonworm, random.nextInt(3)==0 ?1:0), ignoring return. Direct=MoonwormShot, causing=current owner (nullable); exactly one type caller. Tags only minecraft:no_knockback and neoforge:is_physical, not IS_PROJECTILE despite projectile entity. Exhaustion0, native living-nonPlayer scaling. Ordinary armor, facing shield/source position, Resistance/general Protection, absorption, cooldown and event admission remain; no TF throw-marker or poison/freeze. NO_KNOCKBACK suppresses native hurt knockback; zero request is still an attempted native hurt and need not return false or have no native attribution/cooldown effects. Never claim one HP per impact. No attack attribute/melee enchantment helper. Loot/sound/discard below do not depend on true hurt.

### Moonworm drop

Non-head entity impact always on server evaluates MOONWORM_FAILED_TO_PLACE_DROPS with THIS_ENTITY=shot, ORIGIN=shot position and ownerless minecraft:fall solely as loot context (no fall hurt). Installed table returns1 Moonworm item. Creates temporary ItemEntity then calls its spawnAtLocation(item), which creates/adds the actual dropped item; no second explicit add of temporary entity. Bug sound/ENTITY_DIE event. Failed block placement uses same loot; no doMobLoot check in this callback. Native entity veto/failed hurt does not suppress these actions; canceled projectile impact does.

### Moonworm blocks

onHitBlock first calls native block.onProjectileHit, then adjacent hit-face position: replaceable && not #minecraft:fire && Critter.canSurvive(face) && not lava -> setBlockAndUpdate(default Moonworm facing hit direction), result ignored, projectile-land event/sound; otherwise failure loot/squish. Support requires center support on opposite neighbor OR LeavesBlock. Projectile placement has no Player mayUseItemAt, adventure requirement, mobGriefing or BreakEvent in its TF body. It uses default waterlogged=false even when replacing water; direct Queen placement separately derives block state from context. Outer onHit after super performs server event3/discard regardless placement/damage return. No persistent damaging projectile after impact.

### Queen place

Native useOn requires Player, damage<max, mayUseItemAt(adjusted target,face,stack), default Moonworm unobstructed. Calls tryPlace; returns SUCCESS even if tryPlace fails after these outer tests, but no wear on failure. tryPlace requires context.canPlace, nonnull placement state, canSurvive/unobstructed then setBlock(flags11) true. Applies BLOCK_STATE components/custom block entity tag, setPlacedBy/ServerPlayer criterion, sounds; server non-instabuild protected cost1. No shrink/break. Native block state chooses clicked face then viable looking alternatives and initial waterlogging. Moonworm registered light14/noCollision/instant break; block entity tick is only client rotation. Critter contact may squish bug block for Projectile not DONT_KILL_BUGS or FallingBlockEntity; MoonwormShot explicitly excluded. Squish replaces with water/air, installed Moonworm squish loot1 lime dye/stat/particles, not entity HP damage. No effect merely from wearing this block in this code.

### Queen repair

Special native MoonwormQueenRepairRecipe installed. matches exactly one damaged Queen plus >=1 occupied Torchberry slots, no other nonempty items; no over-repair quantity cap. assemble creates DEFAULT Queen, sets damage oldDamage-64*berrySlotCount (native clamp0..max), so custom name/enchantment/components are not copied. Native crafting consumes one per used slot; stack counts do not multiply repair. Dimension>=2. Ordinary full Queen/duplicate/foreign item fails. This custom recipe works despite setNoRepair and does not use scepter Renewal. Resource primitive protected nonbreaking helper reused.

### Cube producer

Cube item registered stack1/fire-resistant, no durability/cost/cooldown. Data census finds only WIP tag among installed data JSON literal cube_of_annihilation mentions, no recipe/loot producer; actual native Player.use is a valid registered-item administrative/creative fixture, without claiming survival acquisition. All-TF instruction census has only CubeOfAnnihilationItem.use as explicit runtime thrown constructor. THROWN_PROJECTILE persistent/synced UUID per stack: existing token -> PASS; otherwise server creates Cube(owner Player, same stack reference), add result ignored, stores UUID; starts72000 BLOCK use. Server inventory tick removes token if current ServerLevel UUID lookup is not loaded Cube; not a global cap/ownership check. Denied add/unloaded/other-dimension projectile may clear token. Cube entity registered1x1/fireproof, no portal use.

### Cube flight

Cube extends ordinary ThrowableProjectile, NOT ITFProjectile; gravity0. Constructor shoot speed1.5/inaccuracy1; each server tick after native super collision/movement: unresolved owner -> remove(KILLED),return. Otherwise destination owner eye, or owner eye+look*16 while !hasHitObstacle and owner Player isUsingItem (ANY item, not necessarily original Cube). NonPlayer owner/obstacle/notUsing -> returning. Returning distance<2 removes, but no return afterward: velocity/block loop still executes on object that tick. Velocity set toward destination; speed> .5 normalized to.5. <=.5 calls Vec3.multiply(.5) but ignores immutable result, so no extra halving. End-of-tick terrain scan always. Native first launch movement can be1.5 before steering cap. No teleport or HP annihilation.

### Cube damage

onHitEntity only Living -> native hurt10; true only adds60 to Cube.tickCount, false no increment. No hit discard, per-target list or explicit lifetime/maximum-tick check anywhere in full Cube body; +60 does not prove shortened lifetime. getDamageSource casts owner to Living: Player -> minecraft:player_attack direct=causing owner; other Living -> minecraft:mob_attack direct=causing owner; null -> minecraft:thrown direct=Cube/causing null. Null fallback may execute during super collision before later owner-null removal, not a normal stable ownerless deployment. NonLiving owner would fail cast; no legitimate producer here. Ordinary native armor/shield/Resistance/Protection/absorption/cooldown/events and applicable Player difficulty remain. Primary owner sources NOT projectile tagged, so projectile protection/source-position logic follows actual type/owner, not Cube geometry. No attack attributes/Strength/Sharpness helper automatically added to fixed10. Source ownership can still activate protected mainhand Knightmetal/Minotaur predicates under their actual conditions.

### Cube shield

Cube item canDisableShield always true. Exact244 Living.canDisableShield delegates current MAINHAND item; Player shield block against non-IS_PROJECTILE source/direct Living calls native block response and can disable for100 ticks even if HP hurt false. A genuine launched Cube held MAINHAND therefore supplies a shield-disable path because source direct=owner; offhand Cube with other mainhand follows that other item instead. Ordinary Player melee holding Cube also invokes native source/weapon logic. BLOCK animation alone does NOT make Cube bearer block: exact244 Living.isBlocking requires SHIELD_BLOCK ability, inherited IItemExtension.canPerformAction=false, and Cube has no override. No fictitious defensive shield resource/damage absorption.

### Cube terrain

onHitBlock if hit position nonempty calls affectBlocksInAABB(BB inflated float.2); also every server tick ends with same scan. WorldUtil.getAllInBB casts each bound to int (truncate toward zero, not floor) then inclusive BlockPos range. Each nonair block: only ServerPlayer owner; native BreakEvent must not canceled, then (#annihilation_inclusions OR explosionResistance<8 AND destroySpeed>=0) AND (not block-placing-restricted gameMode OR original stack.canBreakBlockInAdventureMode). Included tags can admit normally hard/unbreakable blocks; exact tag pinned, including deadrock/castle/force fields/thorns/nether portal. Allowed -> removeBlock(false), ignored return, sound/particles/BLOCK_DESTROY, no loot/hardness wear/XP. Veto or cancellation sets persistent-in-memory obstacle flag; continues rest of current box, and terrain remains active during return. NonServerPlayer owner skips blocks without setting obstacle. No extra mobGriefing/PlayerGameMode destroy/harvest path. No numeric damage from block removal.

### Cube reflection save

Exact244 inherited impact event/target deflection still precede Cube custom onHit. Cube custom onHit dispatches only entity/block and does not call Projectile.onHit, so its own dispatch lacks that generic redirectable-projectile target handling/PROJECTILE_LAND event. TF shield parry needs parryNonTwilightAttacks=true for this non-ITFProjectile (or separate external mod behavior, not claimed here); native accepted parry changes owner to blocker, while stored original stack reference/token is not relinked. Steering/damage/terrain then follow new owner. Native owner/motion and CubeOfAnnihilationStack save; hasHitObstacle/tickCount not explicitly saved by Cube, obstacle resets false on construction. remove stops resolved Living owner only if current use item is Cube, even another Cube stack. Bare registry/admin entity constructor leaves stack null; missing saved stack can fail save/restricted terrain path, so no claim of a fully configured summon equivalent. Real item producer supplies stack.

## Packages

| Mechanic | Primary classification |
|---|---|
| Moonworm zero-or-one native impact | CUSTOM_DAMAGE |
| Moonworm bare-head forced equipment | BINARY_MECHANIC |
| Moonworm placement and native bug lifecycle | VANILLA_LIKE_EXTENDED |
| Moonworm charge and Torchberry repair | CUSTOM_RESOURCE |
| Cube tracking, steering and return | CUSTOM_CONTROL |
| Cube fixed native melee-source hit and shield disable | VANILLA_LIKE_EXTENDED |
| Cube admitted terrain removal | BINARY_MECHANIC |

## Custom source callers

| Type | Amount | Source identity |
|---|---|---|
| twilightforest:moonworm | nextInt(3)==0 requests1, otherwise0; no hurt for bare-headed Player branch. | Direct MoonwormShot; causing current nullable owner (shooter or native parry blocker). |

## Scope and exclusions

- Ten complete native class surfaces and genuine item/dispenser/data callers. Moonworm block client animation and Critter jar/decorative handling have no additional HP/status payload.
- Cube registered WIP item has native behavior but no installed data recipe/loot acquisition proven; do not invent survival producer.
- Protected Twilight bolt/parry/charge and mainhand bonus packages remain unchanged; optional recipe-viewer/accessory/other gear attribution scoped to whole-mod closure.
- No fixes to ignored return/vector, default repair components, null stack or source identity; static research only.
- MOONWORM USED:29/40 types reviewed,11 unfinished; Twilight PARTIAL/zero promoted/REVIEW_REQUIRED0.

## Future native controls

- Real Queen charged/direct/dispenser use with distinct cost/add-return/creative controls.
- Bare-head equip versus random zero/one source, native defenses, impact/parry and independent loot.
- Projectile versus direct block placement, native support/fluid/bug collision and Torchberry repair.
- Registered Cube item UUID/outbound/return/source/shield and terrain event/tag/adventure controls.
- Native reflected owner/reload/nullable-source distinctions without fabricated summon configuration.

[Semantic packages and paths](semantic-sections/twilightforest-utility-projectiles.json), [integrity](twilightforest-utility-projectiles-integrity.json), [full validation](r2f8k-utility-projectiles-validation.json).

Exact next task: Continue Task C with Ender/Seeker/Triple bows and Peacock Fan native control/source paths, then remaining armor/charms/food, utility/passive entities, hazards and11 unfinished custom DamageTypes; close exact nested ASM/compatibility coverage. Protect each subsection toward R2f8 and final whole-Twilight dedup/promotion. IceAndFire only after COMPLETE Twilight pushed/live verified. No runtime boss/L2/Stage/production/fixes/Phase6/7.
